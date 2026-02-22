import base64
import re
from difflib import SequenceMatcher
from typing import Dict, Tuple
from langchain.tools import tool, ToolRuntime
from coze_coding_dev_sdk import ASRClient
from coze_coding_utils.runtime_ctx.context import new_context
from storage.database.db import get_session
from storage.database.student_manager import StudentManager
from storage.database.achievement_manager import AchievementManager, AchievementCreate
from tools.tool_utils_fixed import (
    get_user_context,
    check_student_access,
    require_student_access,
    get_student_name_by_id
)
from datetime import datetime


def calculate_similarity(text1: str, text2: str) -> float:
    """计算两个文本的相似度（0-1之间）"""
    # 标准化文本：去除标点符号、转小写
    normalize = lambda x: re.sub(r'[^\w\s]', '', x.lower().strip())
    norm1, norm2 = normalize(text1), normalize(text2)
    
    if not norm1 or not norm2:
        return 0.0
    
    return SequenceMatcher(None, norm1, norm2).ratio()


def analyze_errors(original: str, recognized: str) -> Dict:
    """分析朗读错误"""
    norm_original = re.sub(r'[^\w\s]', '', original.lower())
    norm_recognized = re.sub(r'[^\w\s]', '', recognized.lower())
    
    original_words = norm_original.split()
    recognized_words = norm_recognized.split()
    
    # 使用动态规划对齐单词
    dp = [[0] * (len(recognized_words) + 1) for _ in range(len(original_words) + 1)]
    for i in range(len(original_words) + 1):
        for j in range(len(recognized_words) + 1):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i
            elif original_words[i-1] == recognized_words[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    
    # 回溯找出不同的单词
    i, j = len(original_words), len(recognized_words)
    mispronounced = []
    missing = []
    extra = []
    
    while i > 0 or j > 0:
        if i > 0 and j > 0 and original_words[i-1] == recognized_words[j-1]:
            i, j = i-1, j-1
        elif i > 0 and (j == 0 or dp[i-1][j] < dp[i][j-1]):
            missing.insert(0, original_words[i-1])
            i -= 1
        elif j > 0 and (i == 0 or dp[i][j-1] <= dp[i-1][j]):
            extra.insert(0, recognized_words[j-1])
            j -= 1
        else:
            mispronounced.append({
                "original": original_words[i-1],
                "recognized": recognized_words[j-1]
            })
            i, j = i-1, j-1
    
    return {
        "mispronounced": mispronounced,
        "missing": missing,
        "extra": extra
    }


@tool
@require_student_access()
def assess_reading(
    student_id: int,
    original_text: str,
    audio_url: str = None,
    audio_base64: str = None,
    language: str = "chinese",
    runtime: ToolRuntime = None
) -> str:
    """朗读评估工具
    
    评估学生的朗读表现，包括：
    - 语音识别（将语音转为文本）
    - 文本相似度计算
    - 错误分析（发音错误、遗漏、多余单词）
    - 综合评分（0-100分）
    - 详细反馈
    
    Args:
        student_id: 学生ID
        original_text: 原文文本（要朗读的内容）
        audio_url: 音频文件URL（可选）
        audio_base64: 音频文件Base64编码（可选，与audio_url二选一）
        language: 语言（chinese/english）
    
    Returns:
        评估结果，包括分数、错误分析、反馈建议
    """
    # 获取学生姓名
    student_name = get_student_name_by_id(student_id) or f"student_{student_id}"
    
    # 1. 语音识别
    ctx = new_context(method="voice_assessment.recognize")
    asr_client = ASRClient(ctx=ctx)
    
    try:
        if audio_base64:
            recognized_text, data = asr_client.recognize(
                uid=student_name,
                base64_data=audio_base64
            )
        elif audio_url:
            recognized_text, data = asr_client.recognize(
                uid=student_name,
                url=audio_url
            )
        else:
            return "❌ 请提供音频文件（URL或Base64格式）"
    except Exception as e:
        return f"❌ 语音识别失败：{str(e)}"
    
    if not recognized_text or recognized_text.strip() == "":
        return "❌ 未能识别到语音内容，请确保音频清晰"
    
    # 2. 计算相似度和评分
    similarity = calculate_similarity(original_text, recognized_text)
    score = round(similarity * 100, 1)
    
    # 3. 分析错误
    errors = analyze_errors(original_text, recognized_text)
    
    # 4. 生成反馈
    feedback_parts = []
    
    # 评分等级
    if score >= 90:
        grade = "🏆 优秀"
        comment = "太棒了！你的朗读非常标准，发音清晰准确！"
    elif score >= 80:
        grade = "🥈 良好"
        comment = "很棒！你的朗读表现很好，再接再厉！"
    elif score >= 70:
        grade = "🥉 及格"
        comment = "不错！你的朗读基本正确，继续加油！"
    elif score >= 60:
        grade = "⚠️ 需要努力"
        comment = "还需多加练习，注意发音准确性。"
    else:
        grade = "❌ 需要加强"
        comment = "建议多听多练，注意每个单词的发音。"
    
    feedback_parts.append(f"## 📖 朗读评估结果\n")
    feedback_parts.append(f"**学生**: {student_name}\n")
    feedback_parts.append(f"**评分**: {score}分 / 100分 {grade}\n")
    feedback_parts.append(f"**评价**: {comment}\n\n")
    
    # 原文对比
    feedback_parts.append("### 📝 文本对比\n")
    feedback_parts.append(f"**原文**: {original_text}\n")
    feedback_parts.append(f"**识别**: {recognized_text}\n\n")
    
    # 错误分析
    if errors["mispronounced"] or errors["missing"] or errors["extra"]:
        feedback_parts.append("### ⚠️ 发现的问题\n")
        
        if errors["mispronounced"]:
            feedback_parts.append("**发音错误**:\n")
            for err in errors["mispronounced"][:5]:  # 最多显示5个
                feedback_parts.append(f"- \"{err['original']}\" 读成了 \"{err['recognized']}\"\n")
            if len(errors["mispronounced"]) > 5:
                feedback_parts.append(f"  ... 还有 {len(errors['mispronounced'])-5} 处\n")
            feedback_parts.append("\n")
        
        if errors["missing"]:
            feedback_parts.append("**遗漏单词**:\n")
            for word in errors["missing"][:5]:
                feedback_parts.append(f"- \"{word}\"\n")
            if len(errors["missing"]) > 5:
                feedback_parts.append(f"  ... 还有 {len(errors['missing'])-5} 个\n")
            feedback_parts.append("\n")
        
        if errors["extra"]:
            feedback_parts.append("**多余内容**:\n")
            for word in errors["extra"][:5]:
                feedback_parts.append(f"- \"{word}\"\n")
            if len(errors["extra"]) > 5:
                feedback_parts.append(f"  ... 还有 {len(errors['extra'])-5} 个\n")
            feedback_parts.append("\n")
    else:
        feedback_parts.append("### ✨ 完美表现\n")
        feedback_parts.append("没有发现错误！你的朗读非常标准！\n\n")
    
    # 改进建议
    feedback_parts.append("### 💡 改进建议\n")
    
    if score >= 90:
        feedback_parts.append("- 你已经掌握了很好的朗读技巧，可以尝试更有挑战性的文章\n")
        feedback_parts.append("- 可以练习朗读诗歌、演讲稿等，提升表现力\n")
    elif score >= 70:
        feedback_parts.append("- 注意单词的发音准确性，多听标准音频模仿\n")
        feedback_parts.append("- 慢一点也没关系，先确保每个词都发音正确\n")
    else:
        feedback_parts.append("- 建议先听标准发音，逐句跟读练习\n")
        feedback_parts.append("- 注意元音和辅音的区别，多练习基础词汇\n")
        feedback_parts.append("- 可以每天花10分钟练习朗读，坚持会有进步\n")
    
    # 5. 给予积分奖励（根据评分）
    db = get_session()
    try:
        student_mgr = StudentManager()
        student = student_mgr.get_student_by_name(db, student_name)
        
        if student:
            points = int(score / 10)  # 评分转换为积分（最高10分）
            if points > 0:
                student_mgr.add_points(db, student.id, points)
                feedback_parts.append(f"\n### 🎁 奖励\n")
                feedback_parts.append(f"✨ 获得魔法积分：{points}分！\n")
                
                # 检查是否可以颁发成就
                if score >= 90:
                    achievement_mgr = AchievementManager()
                    existing_achievements = achievement_mgr.get_achievements(db, student_id=student.id, title="朗读达人")
                    if not existing_achievements:
                        achievement_mgr.create_achievement(db, AchievementCreate(
                            student_id=student.id,
                            achievement_type="reading_goal",
                            title="朗读达人",
                            description="朗读评分达到90分以上",
                            points=20,
                            level="gold",
                            is_featured=True
                        ))
                        feedback_parts.append(f"🏆 解锁成就：「朗读达人」！\n")
                
                # 检查是否升级
                current_points = getattr(student, 'total_points', 0) + points
                new_magic_level = (current_points // 100) + 1
                current_magic_level = getattr(student, 'magic_level', 1)
                if new_magic_level > current_magic_level:
                    student_mgr.upgrade_magic_level(db, student.id)
                    feedback_parts.append(f"🌟 恭喜升级到{new_magic_level}级魔法师！\n")
    except Exception as e:
        feedback_parts.append(f"\n（记录积分时出错：{str(e)}）\n")
    finally:
        db.close()
    
    feedback_parts.append("\n---\n")
    feedback_parts.append("💪 继续练习，你会越来越棒的！")
    
    return "".join(feedback_parts)


@tool
@require_student_access()
def practice_reading(
    student_id: int,
    text: str,
    runtime: ToolRuntime = None
) -> str:
    """朗读练习工具
    
    生成朗读练习题，支持中英文练习材料
    
    Args:
        student_id: 学生ID
        text: 练习文本（可选，不提供则使用默认材料）
    
    Returns:
        练习材料和建议
    """
    # 获取学生姓名
    student_name = get_student_name_by_id(student_id) or f"student_{student_id}"
    
    # 如果用户提供了文本，直接使用
    if text and text.strip():
        practice_text = text.strip()
    else:
        # 提供默认练习材料
        practice_text = """春眠不觉晓，处处闻啼鸟。
夜来风雨声，花落知多少。"""
    
    feedback = f"## 📖 朗读练习\n\n"
    feedback += f"**小巫师 {student_name}**，请大声朗读以下内容：\n\n"
    feedback += f"---\n\n"
    feedback += f"### 练习文本\n\n"
    feedback += f"**{practice_text}**\n\n"
    feedback += f"---\n\n"
    feedback += f"### 练习建议\n\n"
    feedback += f"1. 📱 录音后，告诉我「我要提交朗读」，我会帮你评估\n"
    feedback += f"2. 🎧 朗读前先听一遍标准发音（如果有录音）\n"
    feedback += f"3. ⏸️ 不用着急，放慢速度，确保每个词都发音清晰\n"
    feedback += f"4. 🔁 如果不满意，可以多录几次\n"
    feedback += f"5. 🎯 完成后，我会给你评分和改进建议！\n\n"
    feedback += f"准备好了吗？开始录音吧！🎤✨"
    
    return feedback
