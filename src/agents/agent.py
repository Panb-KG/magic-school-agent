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

def build_agent(ctx=None):
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, LLM_CONFIG)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")
    
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
    
    tools = [
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
    ]
    
    return create_agent(
        model=llm,
        system_prompt=cfg.get("sp"),
        tools=tools,
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )
