"""
工具辅助函数
提供权限检查、用户上下文获取等通用功能
"""

from typing import Optional, Tuple
from langchain.tools import ToolRuntime
from storage.database.db import get_session
from storage.database.student_manager import StudentManager


def get_user_context(runtime: ToolRuntime) -> Tuple[Optional[str], Optional[str]]:
    """
    从运行时上下文中获取用户信息
    
    Args:
        runtime: 工具运行时上下文
    
    Returns:
        (user_id, user_role) 或 (None, None) 如果无法获取
    """
    if not runtime:
        return None, None
    
    ctx = runtime.context if hasattr(runtime, 'context') else None
    if not ctx:
        return None, None
    
    configurable = ctx.get("configurable") if hasattr(ctx, 'get') else {}
    if not configurable:
        return None, None
    
    user_id = configurable.get("user_id")
    user_role = configurable.get("user_role")
    
    return user_id, user_role


def check_student_access(runtime: ToolRuntime, student_id: int) -> bool:
    """
    检查用户是否有权访问该学生的数据
    
    Args:
        runtime: 工具运行时上下文
        student_id: 学生ID
    
    Returns:
        是否有权访问
    """
    user_id, user_role = get_user_context(runtime)
    
    if not user_id or not user_role:
        return False
    
    try:
        from auth.permissions import permissions_manager
        
        # 学生只能访问自己的数据
        if user_role == 'student':
            # 需要通过 user_id 查找对应的 student_id
            db = get_session()
            try:
                student_mgr = StudentManager()
                student = student_mgr.get_student_by_id(db, student_id)
                if not student:
                    return False
                # 检查 student.user_id 是否匹配当前用户
                return student.user_id == user_id
            finally:
                db.close()
        
        # 家长可以访问关联学生的数据
        elif user_role == 'parent':
            return permissions_manager.can_access_student(user_id, str(student_id))
        
        return False
    except Exception as e:
        # 如果权限检查失败，为了安全起见，拒绝访问
        return False


def require_student_access(runtime: ToolRuntime, student_id: int) -> str:
    """
    要求学生访问权限，如果无权则返回错误信息
    
    Args:
        runtime: 工具运行时上下文
        student_id: 学生ID
    
    Returns:
        如果无权访问，返回错误信息；否则返回 None
    """
    if not check_student_access(runtime, student_id):
        return "错误：无权访问该学生的数据"
    return None


def get_student_name_by_id(student_id: int) -> Optional[str]:
    """
    根据学生ID获取学生姓名
    
    Args:
        student_id: 学生ID
    
    Returns:
        学生姓名，如果不存在则返回 None
    """
    db = get_session()
    try:
        student_mgr = StudentManager()
        student = student_mgr.get_student_by_id(db, student_id)
        return student.name if student else None
    except Exception:
        return None
    finally:
        db.close()
