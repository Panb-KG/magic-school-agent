"""
对话会话管理器
负责管理用户与智能体的对话会话历史
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime

from storage.database.shared.model import Conversation, Message


# Pydantic Models
class ConversationCreate(BaseModel):
    user_id: str = Field(..., description="用户ID")
    student_id: Optional[int] = Field(None, description="关联的学生ID")
    title: str = Field(..., description="对话标题")


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None


class MessageCreate(BaseModel):
    conversation_id: int = Field(..., description="对话ID")
    role: str = Field(..., description="角色：user/assistant")
    content: str = Field(..., description="消息内容")


class ConversationManager:
    """对话会话管理器"""

    def create_conversation(self, db: Session, conv_in: ConversationCreate) -> Conversation:
        """创建新对话会话"""
        conversation_data = conv_in.model_dump()
        conversation = Conversation(**conversation_data)
        conversation.message_count = 0
        db.add(conversation)
        try:
            db.commit()
            db.refresh(conversation)
            return conversation
        except Exception:
            db.rollback()
            raise

    def get_conversation_by_id(self, db: Session, conversation_id: int) -> Optional[Conversation]:
        """根据ID获取对话会话"""
        return db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def get_conversations(
        self,
        db: Session,
        user_id: str,
        student_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Conversation]:
        """获取用户的对话列表（按时间倒序）"""
        query = db.query(Conversation).filter(Conversation.user_id == user_id)

        if student_id:
            query = query.filter(Conversation.student_id == student_id)

        return query.order_by(Conversation.created_at.desc()).offset(skip).limit(limit).all()

    def get_conversation_with_messages(self, db: Session, conversation_id: int) -> Optional[Conversation]:
        """获取对话会话及其所有消息"""
        return db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def update_conversation(self, db: Session, conversation_id: int, conv_in: ConversationUpdate) -> Optional[Conversation]:
        """更新对话会话"""
        db_conv = self.get_conversation_by_id(db, conversation_id)
        if not db_conv:
            return None
        update_data = conv_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_conv, field):
                setattr(db_conv, field, value)
        db.add(db_conv)
        try:
            db.commit()
            db.refresh(db_conv)
            return db_conv
        except Exception:
            db.rollback()
            raise

    def delete_conversation(self, db: Session, conversation_id: int) -> bool:
        """删除对话会话及其所有消息"""
        db_conv = self.get_conversation_by_id(db, conversation_id)
        if not db_conv:
            return False

        try:
            db.delete(db_conv)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False

    def add_message(self, db: Session, message_in: MessageCreate) -> Message:
        """添加消息到对话"""
        message_data = message_in.model_dump()
        message = Message(**message_data)

        db.add(message)

        # 更新对话的消息计数和更新时间
        conv = self.get_conversation_by_id(db, message_in.conversation_id)
        if conv:
            conv.message_count += 1
            conv.updated_at = datetime.now()
            db.add(conv)

        try:
            db.commit()
            db.refresh(message)
            return message
        except Exception:
            db.rollback()
            raise

    def get_messages(self, db: Session, conversation_id: int) -> List[Message]:
        """获取对话的所有消息（按时间正序）"""
        return db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).all()

    def get_recent_conversations(
        self,
        db: Session,
        user_id: str,
        days: int = 7
    ) -> List[Conversation]:
        """获取最近N天的对话"""
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days)

        return db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.created_at >= cutoff_date
        ).order_by(Conversation.created_at.desc()).all()

    def search_conversations(
        self,
        db: Session,
        user_id: str,
        keyword: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Conversation]:
        """搜索对话（按标题或消息内容）"""
        # 按标题搜索
        from sqlalchemy import or_

        return db.query(Conversation).filter(
            Conversation.user_id == user_id,
            or_(
                Conversation.title.contains(keyword),
                Conversation.summary.contains(keyword)
            )
        ).order_by(Conversation.created_at.desc()).offset(skip).limit(limit).all()

    def get_conversation_count(self, db: Session, user_id: str) -> int:
        """获取用户的对话总数"""
        return db.query(Conversation).filter(Conversation.user_id == user_id).count()

    def update_title(self, db: Session, conversation_id: int, title: str) -> Optional[Conversation]:
        """更新对话标题"""
        return self.update_conversation(db, conversation_id, ConversationUpdate(title=title))
