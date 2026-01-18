"""
权限检查系统
包含：权限验证装饰器、权限检查工具
"""

import logging
from typing import Callable, Optional, List
from functools import wraps
from sqlalchemy import text
from storage.database.db import get_engine

logger = logging.getLogger(__name__)


class PermissionDeniedError(Exception):
    """权限拒绝异常"""
    pass


class PermissionsManager:
    """权限管理器"""
    
    def __init__(self):
        self.engine = get_engine()
        self._permissions_cache = {}
    
    def has_permission(self, role: str, permission_id: str) -> bool:
        """
        检查角色是否拥有指定权限
        
        Args:
            role: 角色 ('student' 或 'parent')
            permission_id: 权限 ID
        
        Returns:
            是否拥有权限
        """
        # 检查缓存
        cache_key = f"{role}:{permission_id}"
        if cache_key in self._permissions_cache:
            return self._permissions_cache[cache_key]
        
        # 查询数据库
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM auth.role_permissions
                    WHERE role = :role AND permission_id = :permission_id
                """), {"role": role, "permission_id": permission_id})
                has_perm = result.scalar() > 0
                self._permissions_cache[cache_key] = has_perm
                return has_perm
        except Exception as e:
            logger.error(f"检查权限失败: {e}")
            return False
    
    def has_permissions(self, role: str, *permission_ids: str) -> bool:
        """
        检查角色是否拥有所有指定权限
        
        Args:
            role: 角色
            *permission_ids: 多个权限 ID
        
        Returns:
            是否拥有所有权限
        """
        return all(self.has_permission(role, perm_id) for perm_id in permission_ids)
    
    def has_any_permission(self, role: str, *permission_ids: str) -> bool:
        """
        检查角色是否拥有任意一个指定权限
        
        Args:
            role: 角色
            *permission_ids: 多个权限 ID
        
        Returns:
            是否拥有任意一个权限
        """
        return any(self.has_permission(role, perm_id) for perm_id in permission_ids)
    
    def can_access_student(self, parent_id: str, student_id: str) -> bool:
        """
        检查家长是否有权访问该学生
        
        Args:
            parent_id: 家长用户 ID
            student_id: 学生用户 ID
        
        Returns:
            是否有权访问
        """
        if parent_id == student_id:
            # 学生只能访问自己
            return True
        
        # 检查家长-学生关联
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM auth.parent_student_mapping
                    WHERE parent_id = :parent_id AND student_id = :student_id
                """), {"parent_id": parent_id, "student_id": student_id})
                return result.scalar() > 0
        except Exception as e:
            logger.error(f"检查家长学生关联失败: {e}")
            return False
    
    def get_user_permissions(self, role: str) -> List[str]:
        """
        获取角色的所有权限
        
        Args:
            role: 角色
        
        Returns:
            权限 ID 列表
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT permission_id FROM auth.role_permissions
                    WHERE role = :role
                """), {"role": role})
                return [row[0] for row in result.fetchall()]
        except Exception as e:
            logger.error(f"获取用户权限失败: {e}")
            return []
    
    def clear_cache(self):
        """清空权限缓存"""
        self._permissions_cache.clear()


# 全局实例
permissions_manager = PermissionsManager()


def require_permissions(*required_permissions: str):
    """
    权限检查装饰器（用于 API 端点）
    
    Args:
        *required_permissions: 需要的权限 ID
    
    Example:
        @require_permissions('view_student_data', 'edit_homework')
        async def update_homework(request):
            ...
    """
    def decorator(f: Callable):
        @wraps(f)
        async def async_wrapper(*args, **kwargs):
            # 从请求上下文中获取用户信息
            # 这里假设有一个全局的 request 对象或通过参数传递
            user_id = getattr(args[0], 'user_id', None) if args else None
            user_role = getattr(args[0], 'user_role', None) if args else None
            
            if not user_id or not user_role:
                raise PermissionDeniedError("未识别用户身份")
            
            # 检查权限
            if not permissions_manager.has_permissions(user_role, *required_permissions):
                raise PermissionDeniedError(
                    f"权限不足，需要权限: {', '.join(required_permissions)}"
                )
            
            return await f(*args, **kwargs)
        
        @wraps(f)
        def sync_wrapper(*args, **kwargs):
            # 同步函数版本
            user_id = getattr(args[0], 'user_id', None) if args else None
            user_role = getattr(args[0], 'user_role', None) if args else None
            
            if not user_id or not user_role:
                raise PermissionDeniedError("未识别用户身份")
            
            if not permissions_manager.has_permissions(user_role, *required_permissions):
                raise PermissionDeniedError(
                    f"权限不足，需要权限: {', '.join(required_permissions)}"
                )
            
            return f(*args, **kwargs)
        
        # 根据函数类型返回相应的包装器
        import asyncio
        if asyncio.iscoroutinefunction(f):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def check_user_permission(user_id: str, user_role: str, permission_id: str) -> bool:
    """
    检查用户权限的工具函数
    
    Args:
        user_id: 用户 ID
        user_role: 用户角色
        permission_id: 权限 ID
    
    Returns:
        是否有权限
    """
    return permissions_manager.has_permission(user_role, permission_id)


def check_student_access(user_id: str, user_role: str, student_id: str) -> bool:
    """
    检查用户是否有权访问学生数据
    
    Args:
        user_id: 当前用户 ID
        user_role: 当前用户角色
        student_id: 目标学生 ID
    
    Returns:
        是否有权访问
    """
    if user_role == 'student':
        # 学生只能访问自己
        return user_id == student_id
    elif user_role == 'parent':
        # 家长可以访问关联的学生
        return permissions_manager.can_access_student(user_id, student_id)
    else:
        return False


__all__ = [
    'PermissionsManager',
    'permissions_manager',
    'PermissionDeniedError',
    'require_permissions',
    'check_user_permission',
    'check_student_access'
]
