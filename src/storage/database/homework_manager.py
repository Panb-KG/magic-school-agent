from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime

from storage.database.shared.model import Homework


# Pydantic Models
class HomeworkCreate(BaseModel):
    student_id: int = Field(..., description="学生ID")
    title: str = Field(..., description="作业标题")
    subject: Optional[str] = Field(None, description="科目")
    description: Optional[str] = Field(None, description="作业描述")
    due_date: Optional[datetime] = Field(None, description="截止日期")
    priority: str = "medium"
    attachment_url: Optional[str] = Field(None, description="附件URL")
    category: Optional[str] = Field(None, description="分类标签")


class HomeworkUpdate(BaseModel):
    title: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    attachment_url: Optional[str] = None
    submission_url: Optional[str] = None
    points: Optional[int] = None
    feedback: Optional[str] = None
    category: Optional[str] = None
    reminder_sent: Optional[bool] = None


class HomeworkManager:
    """作业管理器"""

    def create_homework(self, db: Session, homework_in: HomeworkCreate) -> Homework:
        """创建作业"""
        homework_data = homework_in.model_dump()
        homework = Homework(**homework_data)
        db.add(homework)
        try:
            db.commit()
            db.refresh(homework)
            return homework
        except Exception:
            db.rollback()
            raise

    def get_homeworks(self, db: Session, skip: int = 0, limit: int = 100, **filters) -> List[Homework]:
        """获取作业列表"""
        query = db.query(Homework)
        for attr, value in filters.items():
            if hasattr(Homework, attr):
                query = query.filter(getattr(Homework, attr) == value)
        return query.order_by(Homework.due_date).offset(skip).limit(limit).all()

    def get_homework_by_id(self, db: Session, homework_id: int) -> Optional[Homework]:
        """根据ID获取作业"""
        return db.query(Homework).filter(Homework.id == homework_id).first()

    def get_student_homeworks(self, db: Session, student_id: int, status: Optional[str] = None) -> List[Homework]:
        """获取学生的作业列表"""
        query = db.query(Homework).filter(Homework.student_id == student_id)
        if status:
            query = query.filter(Homework.status == status)
        return query.order_by(Homework.due_date).all()

    def get_pending_homeworks(self, db: Session, student_id: int) -> List[Homework]:
        """获取待完成作业"""
        return self.get_student_homeworks(db, student_id, status="pending")

    def get_overdue_homeworks(self, db: Session, student_id: int) -> List[Homework]:
        """获取逾期作业"""
        return db.query(Homework).filter(
            Homework.student_id == student_id,
            Homework.status == "pending",
            Homework.due_date < datetime.now()
        ).all()

    def update_homework(self, db: Session, homework_id: int, homework_in: HomeworkUpdate) -> Optional[Homework]:
        """更新作业"""
        db_homework = self.get_homework_by_id(db, homework_id)
        if not db_homework:
            return None
        update_data = homework_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_homework, field):
                setattr(db_homework, field, value)
        db.add(db_homework)
        try:
            db.commit()
            db.refresh(db_homework)
            return db_homework
        except Exception:
            db.rollback()
            raise

    def submit_homework(self, db: Session, homework_id: int, submission_url: str) -> Optional[Homework]:
        """提交作业"""
        return self.update_homework(db, homework_id, HomeworkUpdate(
            status="completed",
            submission_url=submission_url
        ))

    def mark_reminder_sent(self, db: Session, homework_id: int) -> Optional[Homework]:
        """标记已提醒"""
        return self.update_homework(db, homework_id, HomeworkUpdate(reminder_sent=True))

    def delete_homeworks(self, db: Session, **filters) -> int:
        """删除作业"""
        if not filters:
            return 0
        query = db.query(Homework)
        for attr, value in filters.items():
            if hasattr(Homework, attr):
                query = query.filter(getattr(Homework, attr) == value)
        deleted_count = query.delete(synchronize_session=False)
        db.commit()
        return deleted_count
