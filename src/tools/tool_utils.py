"""
工具辅助函数
提供统一的用户身份获取和数据隔离功能
"""

import logging
from typing import Optional
from langchain.tools import ToolRuntime
from sqlalchemy import text
from storage.database.db import get_engine

logger = logging.getLogger(__name__)


def get_current_user_id(runtime: ToolRuntime) -> Optional[str]:
    """
    获取当前用户 ID

    Args:
        runtime: 工具运行时上下文

    Returns:
        用户 ID，如果未找到返回 None
    """
    ctx = runtime.context if runtime else None
    configurable = ctx.get("configurable") if ctx and hasattr(ctx, 'get') else None
    return configurable.get("user_id") if configurable and hasattr(configurable, 'get') else None


def get_current_user_role(runtime: ToolRuntime) -> Optional[str]:
    """
    获取当前用户角色

    Args:
        runtime: 工具运行时上下文

    Returns:
        用户角色 ('student' 或 'parent')，如果未找到返回 None
    """
    ctx = runtime.context if runtime else None
    configurable = ctx.get("configurable") if ctx and hasattr(ctx, 'get') else None
    return configurable.get("user_role") if configurable and hasattr(configurable, 'get') else None


def get_target_student_id(runtime: ToolRuntime, student_name: Optional[str] = None) -> Optional[str]:
    """
    获取目标学生 ID
    - 对于学生角色，返回自己的 ID
    - 对于家长角色，如果提供了 student_name，查找关联的学生 ID
    
    Args:
        runtime: 工具运行时上下文
        student_name: 学生姓名（可选，家长角色用于指定学生）
    
    Returns:
        学生 ID，如果未找到返回 None
    """
    user_id = get_current_user_id(runtime)
    user_role = get_current_user_role(runtime)
    
    if not user_id:
        return None
    
    # 学生角色只能操作自己
    if user_role == 'student':
        return user_id
    
    # 家长角色需要指定学生
    if user_role == 'parent':
        if not student_name:
            return None
        
        try:
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT u.user_id
                    FROM auth.users u
                    JOIN auth.parent_student_mapping ps ON u.user_id = ps.student_id
                    WHERE ps.parent_id = :parent_id 
                    AND u.role = 'student'
                    AND u.student_name = :student_name
                    LIMIT 1
                """), {
                    "parent_id": user_id,
                    "student_name": student_name
                })
                
                row = result.fetchone()
                return row[0] if row else None
        except Exception as e:
            logger.error(f"查找学生 ID 失败: {e}")
            return None
    
    return None


def check_user_isolated(student_id: Optional[str], runtime: ToolRuntime) -> bool:
    """
    检查是否可以进行数据隔离操作
    
    Args:
        student_id: 要操作的学生 ID
        runtime: 工具运行时上下文
    
    Returns:
        是否可以操作
    """
    user_id = get_current_user_id(runtime)
    user_role = get_current_user_role(runtime)
    
    if not user_id or not user_role:
        return False
    
    # 学生只能操作自己的数据
    if user_role == 'student':
        return user_id == student_id
    
    # 家长可以操作关联学生的数据
    if user_role == 'parent' and student_id:
        from auth.permissions import check_student_access
        return check_student_access(user_id, user_role, student_id)
    
    return False


def get_student_by_name(student_name: str, runtime: ToolRuntime) -> Optional[dict]:
    """
    根据学生姓名获取学生信息（带用户隔离）
    
    Args:
        student_name: 学生姓名
        runtime: 工具运行时上下文
    
    Returns:
        学生信息字典，如果未找到返回 None
    """
    user_id = get_current_user_id(runtime)
    user_role = get_current_user_role(runtime)
    
    if not user_id:
        return None
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            if user_role == 'student':
                # 学生只能查询自己
                result = conn.execute(text("""
                    SELECT student_id, student_name, grade, total_points, magic_level
                    FROM students
                    WHERE student_id = :user_id AND student_name = :student_name
                    LIMIT 1
                """), {
                    "user_id": user_id,
                    "student_name": student_name
                })
            else:  # parent
                # 家长只能查询关联的学生
                result = conn.execute(text("""
                    SELECT s.student_id, s.student_name, s.grade, s.total_points, s.magic_level
                    FROM students s
                    JOIN auth.parent_student_mapping ps ON s.student_id = ps.student_id
                    WHERE ps.parent_id = :parent_id 
                    AND s.student_name = :student_name
                    LIMIT 1
                """), {
                    "parent_id": user_id,
                    "student_name": student_name
                })
            
            row = result.fetchone()
            if row:
                return {
                    "student_id": row[0],
                    "student_name": row[1],
                    "grade": row[2],
                    "total_points": row[3],
                    "magic_level": row[4]
                }
            return None
    except Exception as e:
        logger.error(f"查询学生信息失败: {e}")
        return None


def format_tool_error(error_message: str) -> str:
    """
    格式化工具错误信息
    
    Args:
        error_message: 原始错误信息
    
    Returns:
        格式化后的错误信息
    """
    return f"⚠️ {error_message}"


def format_tool_success(success_message: str) -> str:
    """
    格式化工具成功信息
    
    Args:
        success_message: 原始成功信息
    
    Returns:
        格式化后的成功信息
    """
    return f"✅ {success_message}"
