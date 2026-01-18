"""
长期记忆工具
用于提取、存储和检索用户对话记忆
"""

import logging
from typing import List, Dict, Optional
from langchain.tools import tool, ToolRuntime
from langchain_openai import ChatOpenAI
from sqlalchemy import text
from storage.database.db import get_engine
import json
import os

logger = logging.getLogger(__name__)


def _get_llm():
    """获取 LLM 实例"""
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")
    
    return ChatOpenAI(
        model="doubao-seed-1-6-251015",
        api_key=api_key,
        base_url=base_url,
        temperature=0.3,
        max_tokens=1000
    )


@tool
def save_conversation_memory(
    conversation: str,
    runtime: ToolRuntime
) -> str:
    """
    保存对话摘要到长期记忆
    
    Args:
        conversation: 对话内容（最近的几轮对话）
        runtime: 工具运行时上下文
    
    Returns:
        保存结果
    """
    ctx = runtime.context
    user_id = ctx.get("configurable", {}).get("user_id")
    thread_id = ctx.get("configurable", {}).get("thread_id")
    
    if not user_id:
        return "错误：未识别用户身份，无法保存记忆"
    
    try:
        # 使用 LLM 提取关键信息
        llm = _get_llm()
        
        analysis_prompt = f"""
        分析以下对话，提取关键信息并生成摘要：
        
        对话内容：
        {conversation}
        
        请以 JSON 格式返回以下信息：
        {{
            "topic": "对话主题（简短描述）",
            "summary": "对话摘要（100字以内）",
            "key_points": ["关键点1", "关键点2", "关键点3"],
            "emotion": "情绪状态（happy/sad/confused/excited/neutral）",
            "importance": 重要性评分（1-10，10表示最重要）
        }}
        """
        
        response = llm.invoke(analysis_prompt)
        
        # 解析 LLM 返回的 JSON
        try:
            # 尝试提取 JSON
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(content)
        except json.JSONDecodeError:
            # 如果解析失败，使用默认值
            analysis = {
                "topic": "一般对话",
                "summary": conversation[:100],
                "key_points": [],
                "emotion": "neutral",
                "importance": 3
            }
        
        # 保存到数据库
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO memory.conversation_summary 
                (user_id, thread_id, topic, summary_text, key_points, emotion, importance_score)
                VALUES (:user_id, :thread_id, :topic, :summary, :key_points, :emotion, :importance)
            """), {
                "user_id": user_id,
                "thread_id": thread_id,
                "topic": analysis.get("topic", "")[:200],
                "summary": analysis.get("summary", ""),
                "key_points": json.dumps(analysis.get("key_points", []), ensure_ascii=False),
                "emotion": analysis.get("emotion", "neutral"),
                "importance": analysis.get("importance", 3)
            })
            conn.commit()
        
        logger.info(f"保存对话记忆: user={user_id}, topic={analysis.get('topic')}")
        return f"对话记忆已保存：{analysis.get('topic')}"
    
    except Exception as e:
        logger.error(f"保存对话记忆失败: {e}")
        return f"保存记忆失败: {str(e)}"


@tool
def retrieve_relevant_memories(
    query: str,
    runtime: ToolRuntime
) -> str:
    """
    检索相关的长期记忆
    
    Args:
        query: 查询文本
        runtime: 工具运行时上下文
    
    Returns:
        相关记忆内容
    """
    ctx = runtime.context
    user_id = ctx.get("configurable", {}).get("user_id")
    
    if not user_id:
        return "错误：未识别用户身份"
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # 查询最近的相关对话摘要（按重要性和时间排序）
            result = conn.execute(text("""
                SELECT 
                    topic,
                    summary_text,
                    key_points,
                    emotion,
                    conversation_date,
                    importance_score
                FROM memory.conversation_summary
                WHERE user_id = :user_id
                ORDER BY 
                    importance_score DESC,
                    conversation_date DESC
                LIMIT 5
            """), {"user_id": user_id})
            
            rows = result.fetchall()
            
            if not rows:
                return "暂无相关记忆"
            
            # 格式化记忆内容
            memories = []
            for row in rows:
                memory = {
                    "topic": row[0],
                    "summary": row[1],
                    "key_points": json.loads(row[2]) if row[2] else [],
                    "emotion": row[3],
                    "date": row[4].isoformat() if row[4] else None,
                    "importance": row[5]
                }
                memories.append(memory)
            
            # 返回格式化的记忆文本
            memory_text = "## 相关记忆\n\n"
            for i, mem in enumerate(memories, 1):
                memory_text += f"{i}. **{mem['topic']}** (重要性: {mem['importance']}/10)\n"
                memory_text += f"   摘要: {mem['summary']}\n"
                if mem['key_points']:
                    memory_text += f"   关键点: {', '.join(mem['key_points'][:3])}\n"
                memory_text += f"   时间: {mem['date'][:10] if mem['date'] else '未知'}\n\n"
            
            return memory_text
    
    except Exception as e:
        logger.error(f"检索记忆失败: {e}")
        return f"检索记忆失败: {str(e)}"


@tool
def update_user_profile(
    preferences: Optional[str] = None,
    learning_goals: Optional[str] = None,
    learning_style: Optional[str] = None,
    favorite_subjects: Optional[str] = None,
    weak_subjects: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    更新用户画像
    
    Args:
        preferences: 偏好设置（JSON 字符串）
        learning_goals: 学习目标
        learning_style: 学习风格
        favorite_subjects: 喜欢的科目（逗号分隔）
        weak_subjects: 薄弱科目（逗号分隔）
        runtime: 工具运行时上下文
    
    Returns:
        更新结果
    """
    ctx = runtime.context
    user_id = ctx.get("configurable", {}).get("user_id")
    
    if not user_id:
        return "错误：未识别用户身份"
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # 检查是否已存在用户画像
            result = conn.execute(text("""
                SELECT profile_id FROM memory.user_profile WHERE user_id = :user_id
            """), {"user_id": user_id})
            exists = result.fetchone() is not None
            
            if exists:
                # 更新
                update_fields = []
                params = {"user_id": user_id}
                
                if preferences is not None:
                    update_fields.append("preferences = :preferences")
                    params["preferences"] = preferences
                
                if learning_goals is not None:
                    update_fields.append("learning_goals = :learning_goals")
                    params["learning_goals"] = learning_goals
                
                if learning_style is not None:
                    update_fields.append("learning_style = :learning_style")
                    params["learning_style"] = learning_style
                
                if favorite_subjects is not None:
                    update_fields.append("favorite_subjects = :favorite_subjects")
                    params["favorite_subjects"] = [s.strip() for s in favorite_subjects.split(',')]
                
                if weak_subjects is not None:
                    update_fields.append("weak_subjects = :weak_subjects")
                    params["weak_subjects"] = [s.strip() for s in weak_subjects.split(',')]
                
                if update_fields:
                    update_fields.append("updated_at = NOW()")
                    sql = f"""
                        UPDATE memory.user_profile
                        SET {', '.join(update_fields)}
                        WHERE user_id = :user_id
                    """
                    conn.execute(text(sql), params)
                    conn.commit()
                    return "用户画像已更新"
                else:
                    return "没有需要更新的字段"
            else:
                # 创建
                conn.execute(text("""
                    INSERT INTO memory.user_profile 
                    (user_id, preferences, learning_goals, learning_style, favorite_subjects, weak_subjects)
                    VALUES (:user_id, :preferences, :learning_goals, :learning_style, :favorite_subjects, :weak_subjects)
                """), {
                    "user_id": user_id,
                    "preferences": preferences or "{}",
                    "learning_goals": learning_goals,
                    "learning_style": learning_style,
                    "favorite_subjects": [s.strip() for s in favorite_subjects.split(',')] if favorite_subjects else [],
                    "weak_subjects": [s.strip() for s in weak_subjects.split(',')] if weak_subjects else []
                })
                conn.commit()
                return "用户画像已创建"
    
    except Exception as e:
        logger.error(f"更新用户画像失败: {e}")
        return f"更新用户画像失败: {str(e)}"


@tool
def get_user_profile(runtime: ToolRuntime) -> str:
    """
    获取用户画像
    
    Args:
        runtime: 工具运行时上下文
    
    Returns:
        用户画像信息
    """
    ctx = runtime.context
    user_id = ctx.get("configurable", {}).get("user_id")
    
    if not user_id:
        return "错误：未识别用户身份"
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT preferences, learning_goals, learning_style, favorite_subjects, weak_subjects
                FROM memory.user_profile
                WHERE user_id = :user_id
            """), {"user_id": user_id})
            row = result.fetchone()
            
            if not row:
                return "暂无用户画像信息"
            
            profile_text = "## 用户画像\n\n"
            
            if row[1]:  # learning_goals
                profile_text += f"**学习目标**: {row[1]}\n\n"
            
            if row[2]:  # learning_style
                profile_text += f"**学习风格**: {row[2]}\n\n"
            
            if row[3]:  # favorite_subjects
                profile_text += f"**喜欢的科目**: {', '.join(row[3])}\n\n"
            
            if row[4]:  # weak_subjects
                profile_text += f"**薄弱科目**: {', '.join(row[4])}\n\n"
            
            return profile_text
    
    except Exception as e:
        logger.error(f"获取用户画像失败: {e}")
        return f"获取用户画像失败: {str(e)}"


@tool
def update_knowledge_mastery(
    subject: str,
    topic: str,
    mastery_level: int,
    correct_rate: Optional[float] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    更新知识掌握度
    
    Args:
        subject: 科目
        topic: 知识点
        mastery_level: 掌握度 (0-100)
        correct_rate: 正确率 (0-1)
        runtime: 工具运行时上下文
    
    Returns:
        更新结果
    """
    ctx = runtime.context
    user_id = ctx.get("configurable", {}).get("user_id")
    
    if not user_id:
        return "错误：未识别用户身份"
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # 检查是否已存在
            result = conn.execute(text("""
                SELECT mastery_id FROM memory.knowledge_mastery
                WHERE user_id = :user_id AND subject = :subject AND topic = :topic
            """), {"user_id": user_id, "subject": subject, "topic": topic})
            exists = result.fetchone() is not None
            
            if exists:
                # 更新
                conn.execute(text("""
                    UPDATE memory.knowledge_mastery
                    SET mastery_level = :mastery_level,
                        correct_rate = COALESCE(:correct_rate, correct_rate),
                        practice_count = practice_count + 1,
                        last_reviewed_at = NOW(),
                        updated_at = NOW()
                    WHERE user_id = :user_id AND subject = :subject AND topic = :topic
                """), {
                    "user_id": user_id,
                    "subject": subject,
                    "topic": topic,
                    "mastery_level": mastery_level,
                    "correct_rate": correct_rate
                })
                conn.commit()
                return f"知识掌握度已更新: {subject} - {topic} ({mastery_level}%)"
            else:
                # 创建
                conn.execute(text("""
                    INSERT INTO memory.knowledge_mastery
                    (user_id, subject, topic, mastery_level, correct_rate, practice_count, last_reviewed_at)
                    VALUES (:user_id, :subject, :topic, :mastery_level, :correct_rate, 1, NOW())
                """), {
                    "user_id": user_id,
                    "subject": subject,
                    "topic": topic,
                    "mastery_level": mastery_level,
                    "correct_rate": correct_rate
                })
                conn.commit()
                return f"知识掌握度已创建: {subject} - {topic} ({mastery_level}%)"
    
    except Exception as e:
        logger.error(f"更新知识掌握度失败: {e}")
        return f"更新知识掌握度失败: {str(e)}"


@tool
def get_knowledge_mastery(subject: Optional[str] = None, runtime: ToolRuntime = None) -> str:
    """
    获取知识掌握度
    
    Args:
        subject: 科目（可选，不提供则返回所有科目）
        runtime: 工具运行时上下文
    
    Returns:
        知识掌握度信息
    """
    ctx = runtime.context
    user_id = ctx.get("configurable", {}).get("user_id")
    
    if not user_id:
        return "错误：未识别用户身份"
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            if subject:
                result = conn.execute(text("""
                    SELECT subject, topic, mastery_level, correct_rate, practice_count, last_reviewed_at
                    FROM memory.knowledge_mastery
                    WHERE user_id = :user_id AND subject = :subject
                    ORDER BY mastery_level DESC
                """), {"user_id": user_id, "subject": subject})
            else:
                result = conn.execute(text("""
                    SELECT subject, topic, mastery_level, correct_rate, practice_count, last_reviewed_at
                    FROM memory.knowledge_mastery
                    WHERE user_id = :user_id
                    ORDER BY subject, mastery_level DESC
                """), {"user_id": user_id})
            
            rows = result.fetchall()
            
            if not rows:
                return "暂无知识掌握度记录"
            
            # 按科目分组
            subjects = {}
            for row in rows:
                subj = row[0]
                if subj not in subjects:
                    subjects[subj] = []
                subjects[subj].append({
                    "topic": row[1],
                    "mastery": row[2],
                    "correct_rate": float(row[3]) if row[3] else 0,
                    "practice_count": row[4],
                    "last_reviewed": row[5].isoformat() if row[5] else None
                })
            
            # 格式化输出
            mastery_text = "## 知识掌握度\n\n"
            for subj, topics in subjects.items():
                mastery_text += f"### {subj}\n\n"
                for t in topics:
                    mastery_text += f"- **{t['topic']}**: {t['mastery']}% "
                    mastery_text += f"(练习{t['practice_count']}次, "
                    mastery_text += f"正确率{t['correct_rate']:.1%})\n"
                mastery_text += "\n"
            
            return mastery_text
    
    except Exception as e:
        logger.error(f"获取知识掌握度失败: {e}")
        return f"获取知识掌握度失败: {str(e)}"
