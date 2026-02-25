"""
用户认证工具
包含：密码哈希、JWT 令牌生成和验证
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Optional
import uuid
import logging

logger = logging.getLogger(__name__)

# JWT 配置
JWT_SECRET_KEY = "magic_school_secret_key_change_in_production_2024"
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7天


def hash_password(password: str) -> str:
    """对密码进行哈希处理"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否正确"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def generate_access_token(user_id: str, role: str, extra_claims: Optional[Dict] = None) -> str:
    """生成访问令牌"""
    claims = {
        "user_id": user_id,
        "role": role,
        "type": "access",
        "exp": datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.utcnow(),
    }
    if extra_claims:
        claims.update(extra_claims)
    
    token = jwt.encode(claims, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def generate_refresh_token(user_id: str) -> str:
    """生成刷新令牌"""
    claims = {
        "user_id": user_id,
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        "iat": datetime.utcnow(),
    }
    
    token = jwt.encode(claims, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def verify_token(token: str) -> Optional[Dict]:
    """验证令牌并返回声明"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("令牌已过期")
        return None
    except jwt.InvalidTokenError:
        logger.warning("无效的令牌")
        return None


def generate_user_id() -> str:
    """生成用户 ID"""
    return f"usr_{uuid.uuid4().hex[:16]}"


def generate_session_id() -> str:
    """生成会话 ID"""
    return f"ses_{uuid.uuid4().hex[:16]}"


def generate_thread_id(user_id: str) -> str:
    """生成线程 ID"""
    timestamp = int(datetime.utcnow().timestamp())
    return f"thread_{user_id}_{timestamp}"


def refresh_access_token(refresh_token: str) -> Optional[Dict]:
    """
    使用刷新令牌获取新的访问令牌
    
    Args:
        refresh_token: 刷新令牌
    
    Returns:
        包含新令牌的字典，或None（如果刷新失败）
    """
    try:
        # 验证刷新令牌
        payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # 验证令牌类型
        if payload.get("type") != "refresh":
            logger.warning("令牌类型错误")
            return None
        
        user_id = payload.get("user_id")
        if not user_id:
            logger.warning("令牌中缺少用户ID")
            return None
        
        # 生成新的访问令牌（需要用户角色，从令牌中获取或从数据库查询）
        # 这里简化处理，假设刷新令牌中包含角色信息，或者重新从数据库查询
        # 为了简化，这里假设role在payload中
        role = payload.get("role", "student")
        
        new_access_token = generate_access_token(user_id, role)
        new_refresh_token = generate_refresh_token(user_id)
        
        logger.info(f"令牌刷新成功: {user_id}")
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "Bearer",
            "expires_in": JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60  # 秒
        }
    except jwt.ExpiredSignatureError:
        logger.warning("刷新令牌已过期")
        return None
    except jwt.InvalidTokenError:
        logger.warning("无效的刷新令牌")
        return None


class TokenPayload:
    """令牌载荷类"""
    def __init__(self, user_id: str, role: str, exp: datetime, iat: datetime):
        self.user_id = user_id
        self.role = role
        self.exp = exp
        self.iat = iat
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TokenPayload':
        """从字典创建"""
        return cls(
            user_id=data.get("user_id"),
            role=data.get("role"),
            exp=datetime.fromtimestamp(data.get("exp", 0)),
            iat=datetime.fromtimestamp(data.get("iat", 0))
        )
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        return datetime.utcnow() > self.exp
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "role": self.role,
            "exp": self.exp.timestamp(),
            "iat": self.iat.timestamp()
        }
