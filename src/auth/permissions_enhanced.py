"""
完善的权限检查系统
提供装饰器、中间件和工具函数
"""

import functools
import logging
from typing import Callable, Optional, Any, Union
from langchain.tools import ToolRuntime
from storage.database.db import get_session
from storage.database.student_manager import StudentManager
from auth.permissions import permissions_manager

logger = logging.getLogger(__name__)


class PermissionDeniedError(Exception):
    """权限拒绝异常"""
    pass


def get_user_context(runtime: ToolRuntime) -> tuple:
    """
    从运行时上下文中获取用户信息
    
    Args:
        runtime: 工具运行时上下文
    
    Returns:
        (user_id, user_role, session_id, thread_id)
    """
    if not runtime:
        logger.warning("Runtime 为空")
        return None, None, None, None
    
    ctx = runtime.context if hasattr(runtime, 'context') else None
    if not ctx:
        logger.warning("Runtime 没有 context 属性")
        return None, None, None, None
    
    configurable = ctx.get("configurable") if hasattr(ctx, 'get') else {}
    if not configurable:
        logger.warning("Configurable 为空")
        return None, None, None, None
    
    user_id = configurable.get("user_id")
    user_role = configurable.get("user_role", 'student')
    session_id = configurable.get("session_id")
    thread_id = configurable.get("thread_id")
    
    return user_id, user_role, session_id, thread_id


def check_student_access(runtime: ToolRuntime, student_id: int) -> bool:
    """
    检查用户是否有权访问该学生的数据
    
    Args:
        runtime: 工具运行时上下文
        student_id: 学生ID
    
    Returns:
        是否有权访问
    """
    user_id, user_role, _, _ = get_user_context(runtime)
    
    if not user_id or not user_role:
        logger.warning(f"无法获取用户信息: user_id={user_id}, user_role={user_role}")
        return False
    
    # 特殊情况：如果 student_id 为 None 或无效，拒绝访问
    if not student_id or student_id <= 0:
        logger.warning(f"无效的 student_id: {student_id}")
        return False
    
    try:
        # 学生只能访问自己的数据
        if user_role == 'student':
            db = get_session()
            try:
                student_mgr = StudentManager()
                student = student_mgr.get_student_by_id(db, student_id)
                if not student:
                    logger.warning(f"学生不存在: student_id={student_id}")
                    return False
                
                # 检查 student.user_id 是否匹配当前用户
                has_access = student.user_id == user_id
                if not has_access:
                    logger.warning(f"学生无权访问: user_id={user_id}, student.user_id={student.user_id}")
                return has_access
            finally:
                db.close()
        
        # 家长可以访问关联学生的数据
        elif user_role == 'parent':
            has_access = permissions_manager.can_access_student(user_id, str(student_id))
            if not has_access:
                logger.warning(f"家长无权访问: parent_id={user_id}, student_id={student_id}")
            return has_access
        
        # 其他角色拒绝访问
        else:
            logger.warning(f"未知角色: user_role={user_role}")
            return False
    
    except Exception as e:
        logger.error(f"权限检查失败: {e}")
        # 如果权限检查失败，为了安全起见，拒绝访问
        return False


def require_student_access(
    student_id_param: str = 'student_id',
    error_message: str = "错误：无权访问该学生的数据"
):
    """
    要求学生访问权限的装饰器
    
    Args:
        student_id_param: 包含学生ID的参数名
        error_message: 权限拒绝时的错误信息
    
    Example:
        @require_student_access()
        def get_homework_list(student_id: int, ...):
            ...
    
        @require_student_access(student_id_param='id')
        def get_student(id: int, ...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取 runtime 参数
            runtime = kwargs.get('runtime')
            if not runtime:
                return "错误：缺少运行时上下文"
            
            # 获取 student_id
            student_id = kwargs.get(student_id_param)
            if not student_id:
                return f"错误：缺少参数 {student_id_param}"
            
            # 检查权限
            if not check_student_access(runtime, student_id):
                user_id, user_role, _, _ = get_user_context(runtime)
                logger.warning(f"权限拒绝: user_id={user_id}, user_role={user_role}, student_id={student_id}")
                return error_message
            
            # 执行原函数
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_any_permission(*permission_ids: str):
    """
    要求拥有任意一个权限的装饰器
    
    Args:
        *permission_ids: 权限ID列表
    
    Example:
        @require_any_permission('view_student_data', 'view_own_data')
        def get_student_info(student_id: int, ...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            runtime = kwargs.get('runtime')
            if not runtime:
                return "错误：缺少运行时上下文"
            
            user_id, user_role, _, _ = get_user_context(runtime)
            if not user_id or not user_role:
                return "错误：未识别用户身份"
            
            # 检查是否有任意一个权限
            has_permission = False
            for perm_id in permission_ids:
                if permissions_manager.has_permission(user_role, perm_id):
                    has_permission = True
                    break
            
            if not has_permission:
                logger.warning(f"权限不足: user_id={user_id}, user_role={user_role}, required_permissions={permission_ids}")
                return f"错误：权限不足，需要以下权限之一：{', '.join(permission_ids)}"
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_all_permissions(*permission_ids: str):
    """
    要求拥有所有权限的装饰器
    
    Args:
        *permission_ids: 权限ID列表
    
    Example:
        @require_all_permissions('view_student_data', 'edit_homework')
        def modify_homework(student_id: int, homework_id: int, ...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            runtime = kwargs.get('runtime')
            if not runtime:
                return "错误：缺少运行时上下文"
            
            user_id, user_role, _, _ = get_user_context(runtime)
            if not user_id or not user_role:
                return "错误：未识别用户身份"
            
            # 检查是否拥有所有权限
            has_all_permissions = permissions_manager.has_permissions(user_role, *permission_ids)
            
            if not has_all_permissions:
                logger.warning(f"权限不足: user_id={user_id}, user_role={user_role}, required_permissions={permission_ids}")
                return f"错误：权限不足，需要以下所有权限：{', '.join(permission_ids)}"
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_role(*allowed_roles: str):
    """
    要求特定角色的装饰器
    
    Args:
        *allowed_roles: 允许的角色列表
    
    Example:
        @require_role('parent')
        def parent_view_dashboard(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            runtime = kwargs.get('runtime')
            if not runtime:
                return "错误：缺少运行时上下文"
            
            user_id, user_role, _, _ = get_user_context(runtime)
            if not user_id or not user_role:
                return "错误：未识别用户身份"
            
            if user_role not in allowed_roles:
                logger.warning(f"角色不允许: user_id={user_id}, user_role={user_role}, allowed_roles={allowed_roles}")
                return f"错误：此功能仅限以下角色使用：{', '.join(allowed_roles)}"
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def log_access(func: Callable) -> Callable:
    """
    记录访问日志的装饰器
    
    Args:
        func: 要装饰的函数
    
    Example:
        @log_access
        def get_homework_list(student_id: int, ...):
            ...
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        runtime = kwargs.get('runtime')
        if runtime:
            user_id, user_role, session_id, thread_id = get_user_context(runtime)
            logger.info(
                f"工具调用: func={func.__name__}, "
                f"user_id={user_id}, user_role={user_role}, "
                f"session_id={session_id}, thread_id={thread_id}, "
                f"args={args}, kwargs={kwargs}"
            )
        
        return func(*args, **kwargs)
    
    return wrapper


def get_student_name_by_id(student_id: int) -> Optional[str]:
    """
    根据学生ID获取学生姓名
    
    Args:
        student_id: 学生ID
    
    Returns:
        学生姓名，如果不存在则返回 None
    """
    try:
        db = get_session()
        try:
            student_mgr = StudentManager()
            student = student_mgr.get_student_by_id(db, student_id)
            return student.name if student else None
        finally:
            db.close()
    except Exception as e:
        logger.error(f"获取学生姓名失败: student_id={student_id}, error={e}")
        return None


def safe_execute(func: Callable, *args, **kwargs) -> str:
    """
    安全执行函数，捕获异常
    
    Args:
        func: 要执行的函数
        *args: 位置参数
        **kwargs: 关键字参数
    
    Returns:
        执行结果或错误信息
    """
    try:
        result = func(*args, **kwargs)
        return result
    except PermissionDeniedError as e:
        logger.error(f"权限拒绝: {e}")
        return f"错误：{e}"
    except Exception as e:
        logger.error(f"执行失败: func={func.__name__}, error={e}")
        return f"执行失败：{str(e)}"
