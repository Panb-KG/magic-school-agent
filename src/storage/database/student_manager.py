from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime

from storage.database.shared.model import Student


# Pydantic Models
class StudentCreate(BaseModel):
    user_id: Optional[str] = Field(None, description="关联的用户ID")
    name: str = Field(..., description="学生姓名")
    grade: Optional[str] = Field(None, description="年级")
    class_name: Optional[str] = Field(None, description="班级")
    school: Optional[str] = Field(None, description="学校")
    parent_contact: Optional[str] = Field(None, description="家长联系方式")
    nickname: Optional[str] = Field(None, description="昵称")


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    grade: Optional[str] = None
    class_name: Optional[str] = None
    school: Optional[str] = None
    parent_contact: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None
    magic_level: Optional[int] = None
    total_points: Optional[int] = None


class StudentManager:
    """学生信息管理器"""

    def create_student(self, db: Session, student_in: StudentCreate) -> Student:
        """创建学生"""
        student_data = student_in.model_dump()
        student = Student(**student_data)
        db.add(student)
        try:
            db.commit()
            db.refresh(student)
            return student
        except Exception:
            db.rollback()
            raise

    def get_students(self, db: Session, skip: int = 0, limit: int = 100, **filters) -> List[Student]:
        """获取学生列表"""
        query = db.query(Student)
        for attr, value in filters.items():
            if hasattr(Student, attr):
                query = query.filter(getattr(Student, attr) == value)
        return query.offset(skip).limit(limit).all()

    def get_student_by_id(self, db: Session, student_id: int) -> Optional[Student]:
        """根据ID获取学生"""
        return db.query(Student).filter(Student.id == student_id).first()

    def get_student_by_name(self, db: Session, name: str) -> Optional[Student]:
        """根据姓名获取学生"""
        return db.query(Student).filter(Student.name == name).first()

    def get_student_by_user_id(self, db: Session, user_id: str) -> Optional[Student]:
        """根据用户ID获取学生"""
        return db.query(Student).filter(Student.user_id == user_id).first()

    def update_student(self, db: Session, student_id: int, student_in: StudentUpdate) -> Optional[Student]:
        """更新学生信息"""
        db_student = self.get_student_by_id(db, student_id)
        if not db_student:
            return None
        update_data = student_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_student, field):
                setattr(db_student, field, value)
        db.add(db_student)
        try:
            db.commit()
            db.refresh(db_student)
            return db_student
        except Exception:
            db.rollback()
            raise

    def add_points(self, db: Session, student_id: int, points: int) -> Optional[Student]:
        """为学生增加积分"""
        db_student = self.get_student_by_id(db, student_id)
        if not db_student:
            return None
        db_student.total_points += points
        db.add(db_student)
        try:
            db.commit()
            db.refresh(db_student)
            return db_student
        except Exception:
            db.rollback()
            raise

    def upgrade_magic_level(self, db: Session, student_id: int) -> Optional[Student]:
        """升级魔法等级"""
        db_student = self.get_student_by_id(db, student_id)
        if not db_student:
            return None
        if db_student.magic_level < 10:
            db_student.magic_level += 1
        db.add(db_student)
        try:
            db.commit()
            db.refresh(db_student)
            return db_student
        except Exception:
            db.rollback()
            raise

    def delete_students(self, db: Session, **filters) -> int:
        """删除学生"""
        if not filters:
            return 0
        query = db.query(Student)
        for attr, value in filters.items():
            if hasattr(Student, attr):
                query = query.filter(getattr(Student, attr) == value)
        deleted_count = query.delete(synchronize_session=False)
        db.commit()
        return deleted_count
