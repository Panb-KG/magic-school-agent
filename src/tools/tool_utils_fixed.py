"""
工具辅助函数
提供权限检查、用户上下文获取等通用功能
整合了增强的权限检查系统
"""

from typing import Optional, Tuple
from langchain.tools import ToolRuntime
from storage.database.db import get_session
from storage.database.student_manager import StudentManager

# 导入增强的权限检查系统
from auth.permissions_enhanced import (
    get_user_context,
    check_student_access,
    require_student_access,
    require_any_permission,
    require_all_permissions,
    require_role,
    log_access,
    get_student_name_by_id,
    safe_execute,
    PermissionDeniedError
)

# 导出所有常用函数
__all__ = [
    'get_user_context',
    'check_student_access',
    'require_student_access',
    'require_any_permission',
    'require_all_permissions',
    'require_role',
    'log_access',
    'get_student_name_by_id',
    'safe_execute',
    'PermissionDeniedError'
]


# 保留向后兼容的函数别名
def require_student_access_runtime(runtime: ToolRuntime, student_id: int) -> str:
    """
    要求学生访问权限，如果无权则返回错误信息（向后兼容）
    
    Args:
        runtime: 工具运行时上下文
        student_id: 学生ID
    
    Returns:
        如果无权访问，返回错误信息；否则返回 None
    """
    if not check_student_access(runtime, student_id):
        return "错误：无权访问该学生的数据"
    return None
