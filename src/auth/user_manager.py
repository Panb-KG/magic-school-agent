"""
用户管理模块
包含：用户注册、登录、查询等功能
"""

import logging
from typing import Optional, List, Dict
from sqlalchemy import text
from storage.database.db import get_engine
from auth.auth_utils import (
    hash_password, verify_password,
    generate_access_token, generate_refresh_token,
    verify_token, generate_user_id
)

logger = logging.getLogger(__name__)


class UserManager:
    """用户管理器"""
    
    def __init__(self):
        self.engine = get_engine()
    
    def register_user(
        self,
        username: str,
        password: str,
        role: str,
        student_name: Optional[str] = None,
        grade: Optional[str] = None
    ) -> Dict:
        """
        注册新用户
        
        Args:
            username: 用户名
            password: 密码
            role: 角色 ('student' 或 'parent')
            student_name: 学生姓名（学生角色必需）
            grade: 年级（学生角色可选）
        
        Returns:
            包含用户信息和令牌的字典
        """
        # 验证角色
        if role not in ['student', 'parent']:
            return {"success": False, "error": "无效的角色"}
        
        # 验证学生角色必需字段
        if role == 'student' and not student_name:
            return {"success": False, "error": "学生角色需要提供学生姓名"}
        
        # 检查用户名是否已存在
        if self._user_exists(username):
            return {"success": False, "error": "用户名已存在"}
        
        # 生成用户 ID
        user_id = generate_user_id()
        
        # 哈希密码
        password_hash = hash_password(password)
        
        # 插入用户记录
        try:
            with self.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO auth.users (user_id, username, password_hash, role, student_name, grade)
                    VALUES (:user_id, :username, :password_hash, :role, :student_name, :grade)
                """), {
                    "user_id": user_id,
                    "username": username,
                    "password_hash": password_hash,
                    "role": role,
                    "student_name": student_name,
                    "grade": grade
                })
                conn.commit()
            
            # 生成令牌
            access_token = generate_access_token(user_id, role)
            refresh_token = generate_refresh_token(user_id)
            
            logger.info(f"用户注册成功: {username} ({role})")
            
            return {
                "success": True,
                "user_id": user_id,
                "username": username,
                "role": role,
                "student_name": student_name,
                "grade": grade,
                "access_token": access_token,
                "refresh_token": refresh_token
            }
        except Exception as e:
            logger.error(f"用户注册失败: {e}")
            return {"success": False, "error": str(e)}
    
    def login_user(self, username: str, password: str) -> Dict:
        """
        用户登录
        
        Args:
            username: 用户名
            password: 密码
        
        Returns:
            包含用户信息和令牌的字典
        """
        # 查询用户
        user = self._get_user_by_username(username)
        if not user:
            return {"success": False, "error": "用户名或密码错误"}
        
        # 验证密码
        if not verify_password(password, user['password_hash']):
            return {"success": False, "error": "用户名或密码错误"}
        
        # 生成令牌
        access_token = generate_access_token(user['user_id'], user['role'])
        refresh_token = generate_refresh_token(user['user_id'])
        
        logger.info(f"用户登录成功: {username} ({user['role']})")
        
        return {
            "success": True,
            "user_id": user['user_id'],
            "username": user['username'],
            "role": user['role'],
            "student_name": user.get('student_name'),
            "grade": user.get('grade'),
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """获取用户信息"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT user_id, username, role, student_name, grade, created_at
                    FROM auth.users
                    WHERE user_id = :user_id
                """), {"user_id": user_id})
                row = result.fetchone()
                if row:
                    return {
                        "user_id": row[0],
                        "username": row[1],
                        "role": row[2],
                        "student_name": row[3],
                        "grade": row[4],
                        "created_at": row[5].isoformat() if row[5] else None
                    }
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
        return None
    
    def _user_exists(self, username: str) -> bool:
        """检查用户名是否已存在"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM auth.users WHERE username = :username
                """), {"username": username})
                return result.scalar() > 0
        except Exception as e:
            logger.error(f"检查用户名失败: {e}")
            return False
    
    def _get_user_by_username(self, username: str) -> Optional[Dict]:
        """根据用户名获取用户"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT user_id, username, password_hash, role, student_name, grade
                    FROM auth.users
                    WHERE username = :username
                """), {"username": username})
                row = result.fetchone()
                if row:
                    return {
                        "user_id": row[0],
                        "username": row[1],
                        "password_hash": row[2],
                        "role": row[3],
                        "student_name": row[4],
                        "grade": row[5]
                    }
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
        return None
    
    def link_parent_student(
        self,
        parent_id: str,
        student_id: str,
        relationship: str
    ) -> Dict:
        """
        关联家长和学生
        
        Args:
            parent_id: 家长用户 ID
            student_id: 学生用户 ID
            relationship: 关系 ('father', 'mother', 'guardian', 'other')
        
        Returns:
            操作结果
        """
        if relationship not in ['father', 'mother', 'guardian', 'other']:
            return {"success": False, "error": "无效的关系类型"}
        
        try:
            with self.engine.connect() as conn:
                # 检查是否已关联
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM auth.parent_student_mapping
                    WHERE parent_id = :parent_id AND student_id = :student_id
                """), {"parent_id": parent_id, "student_id": student_id})
                if result.scalar() > 0:
                    return {"success": False, "error": "已经关联过了"}
                
                # 创建关联
                conn.execute(text("""
                    INSERT INTO auth.parent_student_mapping (parent_id, student_id, relationship)
                    VALUES (:parent_id, :student_id, :relationship)
                """), {"parent_id": parent_id, "student_id": student_id, "relationship": relationship})
                conn.commit()
            
            logger.info(f"家长学生关联成功: {parent_id} -> {student_id} ({relationship})")
            return {"success": True}
        except Exception as e:
            logger.error(f"关联失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_parent_students(self, parent_id: str) -> List[Dict]:
        """获取家长关联的学生列表"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT 
                        ps.student_id,
                        u.username,
                        u.student_name,
                        u.grade,
                        ps.relationship,
                        ps.created_at
                    FROM auth.parent_student_mapping ps
                    JOIN auth.users u ON ps.student_id = u.user_id
                    WHERE ps.parent_id = :parent_id
                    ORDER BY ps.created_at DESC
                """), {"parent_id": parent_id})
                rows = result.fetchall()
                return [
                    {
                        "student_id": row[0],
                        "username": row[1],
                        "student_name": row[2],
                        "grade": row[3],
                        "relationship": row[4],
                        "linked_at": row[5].isoformat() if row[5] else None
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"获取家长学生列表失败: {e}")
            return []
    
    def get_student_parents(self, student_id: str) -> List[Dict]:
        """获取学生关联的家长列表"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT 
                        ps.parent_id,
                        u.username,
                        ps.relationship,
                        ps.created_at
                    FROM auth.parent_student_mapping ps
                    JOIN auth.users u ON ps.parent_id = u.user_id
                    WHERE ps.student_id = :student_id
                    ORDER BY ps.created_at DESC
                """), {"student_id": student_id})
                rows = result.fetchall()
                return [
                    {
                        "parent_id": row[0],
                        "username": row[1],
                        "relationship": row[2],
                        "linked_at": row[3].isoformat() if row[3] else None
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"获取学生家长列表失败: {e}")
            return []


# 全局实例
user_manager = UserManager()
