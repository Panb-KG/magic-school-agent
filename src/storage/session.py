"""
会话管理器
负责管理用户的会话和 thread_id 隔离
"""

import logging
from typing import Optional, Dict
from sqlalchemy import text
from datetime import datetime, timedelta
from storage.database.db import get_engine
from auth.auth_utils import generate_session_id, generate_thread_id, verify_token

logger = logging.getLogger(__name__)


class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        self.engine = get_engine()
    
    def get_or_create_session(self, user_id: str) -> str:
        """
        获取或创建用户会话
        
        Args:
            user_id: 用户 ID
        
        Returns:
            thread_id: LangGraph 使用的 thread_id
        """
        # 1. 查找活跃会话（24小时内有活动）
        active_session = self._get_active_session(user_id)
        if active_session:
            # 更新活跃时间
            self._update_session_activity(active_session['session_id'])
            logger.debug(f"使用现有会话: {active_session['thread_id']} for user {user_id}")
            return active_session['thread_id']
        
        # 2. 创建新会话
        return self._create_session(user_id)
    
    def get_session_by_token(self, token: str) -> Optional[Dict]:
        """
        根据令牌获取会话信息
        
        Args:
            token: JWT 访问令牌
        
        Returns:
            会话信息字典
        """
        from auth.auth_utils import verify_token
        payload = verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get('user_id')
        if not user_id:
            return None
        
        thread_id = self.get_or_create_session(user_id)
        
        return {
            "user_id": user_id,
            "role": payload.get('role'),
            "thread_id": thread_id,
            "exp": payload.get('exp'),
            "iat": payload.get('iat')
        }
    
    def _get_active_session(self, user_id: str) -> Optional[Dict]:
        """获取活跃会话"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT session_id, thread_id, last_active_at
                    FROM auth.user_sessions
                    WHERE user_id = :user_id
                    AND is_active = TRUE
                    AND last_active_at > NOW() - INTERVAL '24 hours'
                    ORDER BY last_active_at DESC
                    LIMIT 1
                """), {"user_id": user_id})
                row = result.fetchone()
                if row:
                    return {
                        "session_id": row[0],
                        "thread_id": row[1],
                        "last_active_at": row[2]
                    }
        except Exception as e:
            logger.error(f"获取活跃会话失败: {e}")
        return None
    
    def _create_session(self, user_id: str) -> str:
        """创建新会话"""
        session_id = generate_session_id()
        thread_id = generate_thread_id(user_id)
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO auth.user_sessions (session_id, user_id, thread_id)
                    VALUES (:session_id, :user_id, :thread_id)
                """), {
                    "session_id": session_id,
                    "user_id": user_id,
                    "thread_id": thread_id
                })
                conn.commit()
            
            logger.info(f"创建新会话: {thread_id} for user {user_id}")
            return thread_id
        except Exception as e:
            logger.error(f"创建会话失败: {e}")
            raise
    
    def _update_session_activity(self, session_id: str):
        """更新会话活跃时间"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("""
                    UPDATE auth.user_sessions
                    SET last_active_at = NOW()
                    WHERE session_id = :session_id
                """), {"session_id": session_id})
                conn.commit()
        except Exception as e:
            logger.error(f"更新会话活跃时间失败: {e}")
    
    def end_session(self, user_id: str, thread_id: str) -> bool:
        """
        结束会话
        
        Args:
            user_id: 用户 ID
            thread_id: 线程 ID
        
        Returns:
            是否成功
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("""
                    UPDATE auth.user_sessions
                    SET is_active = FALSE
                    WHERE user_id = :user_id AND thread_id = :thread_id
                """), {"user_id": user_id, "thread_id": thread_id})
                conn.commit()
            
            logger.info(f"结束会话: {thread_id} for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"结束会话失败: {e}")
            return False
    
    def cleanup_expired_sessions(self, days: int = 7) -> int:
        """
        清理过期会话
        
        Args:
            days: 保留天数
        
        Returns:
            清理的会话数量
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    DELETE FROM auth.user_sessions
                    WHERE last_active_at < NOW() - INTERVAL ':days days'
                    RETURNING session_id
                """), {"days": days})
                conn.commit()
                count = len(result.fetchall())
                logger.info(f"清理了 {count} 个过期会话")
                return count
        except Exception as e:
            logger.error(f"清理过期会话失败: {e}")
            return 0
    
    def get_user_sessions(self, user_id: str) -> list:
        """
        获取用户的所有会话
        
        Args:
            user_id: 用户 ID
        
        Returns:
            会话列表
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT session_id, thread_id, created_at, last_active_at, is_active
                    FROM auth.user_sessions
                    WHERE user_id = :user_id
                    ORDER BY last_active_at DESC
                    LIMIT 10
                """), {"user_id": user_id})
                rows = result.fetchall()
                return [
                    {
                        "session_id": row[0],
                        "thread_id": row[1],
                        "created_at": row[2].isoformat() if row[2] else None,
                        "last_active_at": row[3].isoformat() if row[3] else None,
                        "is_active": row[4]
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"获取用户会话列表失败: {e}")
            return []


# 全局实例
session_manager = SessionManager()
