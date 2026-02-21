import os
import json
from typing import Annotated
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
from coze_coding_utils.runtime_ctx.context import default_headers
from storage.memory.memory_saver import get_memory_saver

LLM_CONFIG = "config/agent_llm_config.json"

# 默认保留最近 20 轮对话 (40 条消息)
MAX_MESSAGES = 40

def _windowed_messages(old, new):
    """滑动窗口: 只保留最近 MAX_MESSAGES 条消息"""
    return add_messages(old, new)[-MAX_MESSAGES:] # type: ignore

class AgentState(MessagesState):
    messages: Annotated[list[AnyMessage], _windowed_messages]

def _get_role_specific_system_prompt(user_role: str, base_prompt: str) -> str:
    """
    根据用户角色获取特定的系统提示词
    
    Args:
        user_role: 用户角色 ('student' 或 'parent')
        base_prompt: 基础系统提示词
    
    Returns:
        增强后的系统提示词
    """
    if user_role == 'parent':
        return f"""{base_prompt}

# 🏠 家长模式特别说明

你现在正在与**家长用户**对话。家长具有以下能力：
- ✅ 可以查看孩子的学习情况和对话历史
- ✅ 可以修改孩子的作业和课程安排
- ✅ 可以给孩子奖励魔法积分
- ✅ 可以审核孩子的作业完成情况
- ✅ 可以管理孩子的成就

# 家长对话原则

1. **客观报告**：以专业、客观的方式报告孩子的学习情况
2. **保护隐私**：不要泄露过于敏感的个人信息
3. **建设性建议**：为家长提供可操作的教育建议
4. **积极引导**：鼓励家长与孩子建立良好的学习氛围
5. **尊重边界**：家长只能管理关联的学生数据

请以专业、友好的方式为家长提供支持。
"""
    else:  # student
        return base_prompt

def build_agent(ctx=None):
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, LLM_CONFIG)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    
    # 从配置文件读取 API 配置，如果不存在则使用环境变量
    api_config = cfg.get('api_config', {})
    api_key = api_config.get('api_key') or os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = api_config.get('base_url') or os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")
    
    # 从上下文中获取用户信息
    user_id = None
    user_role = 'student'  # 默认角色
    
    if ctx and hasattr(ctx, 'get'):
        user_id = ctx.get("configurable", {}).get("user_id")
        user_role = ctx.get("configurable", {}).get("user_role", 'student')
    
    llm = ChatOpenAI(
        model=cfg['config'].get("model"),
        api_key=api_key,
        base_url=base_url,
        temperature=cfg['config'].get('temperature', 0.7),
        streaming=True,
        timeout=cfg['config'].get('timeout', 600),
        extra_body={
            "thinking": {
                "type": cfg['config'].get('thinking', 'disabled')
            }
        },
        default_headers=default_headers(ctx) if ctx else {}
    )
    
    # 导入所有工具
    from tools.student_db_tool import create_student, get_student_info, add_student_points, upgrade_magic_level
    from tools.course_db_tool import add_course, get_weekly_schedule, update_course, delete_course
    from tools.homework_db_tool import (
        add_homework,
        get_homework_list,
        submit_homework,
        update_homework_status,
        delete_homework,
        verify_and_submit_homework
    )
    from tools.courseware_db_tool import add_courseware, get_courseware_list, delete_courseware
    from tools.exercise_db_tool import add_exercise, get_exercise_list, get_weekly_exercise_stats
    from tools.achievement_db_tool import add_achievement, get_achievement_wall, get_all_achievements
    from tools.file_storage_tool import (
        upload_homework_attachment, upload_homework_submission,
        upload_courseware, upload_achievement_icon,
        download_file, generate_file_url, delete_file, list_student_files
    )
    from tools.voice_assessment_tool import assess_reading, practice_reading
    from tools.dashboard_tool import get_student_dashboard, get_student_profile_summary
    from tools.visualization_tool import (
        get_visual_schedule,
        get_points_trend,
        get_achievement_wall_data,
        get_homework_progress
    )
    from tools.memory_tool import (
        save_conversation_memory,
        retrieve_relevant_memories,
        update_user_profile,
        get_user_profile,
        update_knowledge_mastery,
        get_knowledge_mastery
    )
    from tools.parent_tool import (
        parent_view_student_list,
        parent_view_student_conversations,
        parent_modify_homework,
        parent_reward_points,
        parent_approve_homework,
        parent_view_student_dashboard,
        parent_link_student
    )
    from tools.time_tool import (
        get_current_time,
        get_week_date_range,
        get_date_after,
        get_today_info
    )

    # 基础工具列表
    tools = [
        # 时间工具（放在最前面，确保优先调用）
        get_current_time,
        get_week_date_range,
        get_date_after,
        get_today_info,

        # 学生管理工具
        create_student,
        get_student_info,
        add_student_points,
        upgrade_magic_level,
        
        # 课程管理工具
        add_course,
        get_weekly_schedule,
        update_course,
        delete_course,
        
        # 作业管理工具
        add_homework,
        get_homework_list,
        submit_homework,
        update_homework_status,
        delete_homework,
        verify_and_submit_homework,
        
        # 课件管理工具
        add_courseware,
        get_courseware_list,
        delete_courseware,
        
        # 运动记录工具
        add_exercise,
        get_exercise_list,
        get_weekly_exercise_stats,
        
        # 成就管理工具
        add_achievement,
        get_achievement_wall,
        get_all_achievements,
        
        # 文件存储工具
        upload_homework_attachment,
        upload_homework_submission,
        upload_courseware,
        upload_achievement_icon,
        download_file,
        generate_file_url,
        delete_file,
        list_student_files,
        
        # 语音评估工具
        assess_reading,
        practice_reading,
        
        # 仪表盘和可视化工具
        get_student_dashboard,
        get_student_profile_summary,
        get_visual_schedule,
        get_points_trend,
        get_achievement_wall_data,
        get_homework_progress,
        
        # 长期记忆工具（所有角色都可用）
        save_conversation_memory,
        retrieve_relevant_memories,
        update_user_profile,
        get_user_profile,
        update_knowledge_mastery,
        get_knowledge_mastery,
    ]
    
    # 根据角色添加专用工具
    if user_role == 'parent':
        tools.extend([
            # 家长专用工具
            parent_view_student_list,
            parent_view_student_conversations,
            parent_modify_homework,
            parent_reward_points,
            parent_approve_homework,
            parent_view_student_dashboard,
            parent_link_student,
        ])
    
    # 根据角色调整系统提示词
    final_system_prompt = _get_role_specific_system_prompt(user_role, cfg.get("sp"))
    
    return create_agent(
        model=llm,
        system_prompt=final_system_prompt,
        tools=tools,
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )
