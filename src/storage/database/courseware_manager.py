from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from storage.database.shared.model import Courseware


# Pydantic Models
class CoursewareCreate(BaseModel):
    student_id: int = Field(..., description="学生ID")
    title: str = Field(..., description="课件标题")
    subject: Optional[str] = Field(None, description="科目")
    file_type: str = Field(..., description="文件类型")
    file_url: str = Field(..., description="文件URL")
    file_size: Optional[int] = Field(None, description="文件大小")
    category: Optional[str] = Field(None, description="分类标签")
    description: Optional[str] = Field(None, description="课件描述")


class CoursewareUpdate(BaseModel):
    title: Optional[str] = None
    subject: Optional[str] = None
    file_type: Optional[str] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    category: Optional[str] = None
    description: Optional[str] = None


class CoursewareManager:
    """课件管理器"""

    def create_courseware(self, db: Session, courseware_in: CoursewareCreate) -> Courseware:
        """创建课件"""
        courseware_data = courseware_in.model_dump()
        courseware = Courseware(**courseware_data)
        db.add(courseware)
        try:
            db.commit()
            db.refresh(courseware)
            return courseware
        except Exception:
            db.rollback()
            raise

    def get_coursewares(self, db: Session, skip: int = 0, limit: int = 100, **filters) -> List[Courseware]:
        """获取课件列表"""
        query = db.query(Courseware)
        for attr, value in filters.items():
            if hasattr(Courseware, attr):
                query = query.filter(getattr(Courseware, attr) == value)
        return query.order_by(Courseware.created_at.desc()).offset(skip).limit(limit).all()

    def get_courseware_by_id(self, db: Session, courseware_id: int) -> Optional[Courseware]:
        """根据ID获取课件"""
        return db.query(Courseware).filter(Courseware.id == courseware_id).first()

    def get_student_coursewares(self, db: Session, student_id: int, subject: Optional[str] = None) -> List[Courseware]:
        """获取学生的课件列表"""
        query = db.query(Courseware).filter(Courseware.student_id == student_id)
        if subject:
            query = query.filter(Courseware.subject == subject)
        return query.order_by(Courseware.created_at.desc()).all()

    def update_courseware(self, db: Session, courseware_id: int, courseware_in: CoursewareUpdate) -> Optional[Courseware]:
        """更新课件"""
        db_courseware = self.get_courseware_by_id(db, courseware_id)
        if not db_courseware:
            return None
        update_data = courseware_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_courseware, field):
                setattr(db_courseware, field, value)
        db.add(db_courseware)
        try:
            db.commit()
            db.refresh(db_courseware)
            return db_courseware
        except Exception:
            db.rollback()
            raise

    def increment_download_count(self, db: Session, courseware_id: int) -> Optional[Courseware]:
        """增加下载次数"""
        db_courseware = self.get_courseware_by_id(db, courseware_id)
        if not db_courseware:
            return None
        db_courseware.download_count += 1
        db.add(db_courseware)
        try:
            db.commit()
            db.refresh(db_courseware)
            return db_courseware
        except Exception:
            db.rollback()
            raise

    def delete_coursewares(self, db: Session, **filters) -> int:
        """删除课件"""
        if not filters:
            return 0
        query = db.query(Courseware)
        for attr, value in filters.items():
            if hasattr(Courseware, attr):
                query = query.filter(getattr(Courseware, attr) == value)
        deleted_count = query.delete(synchronize_session=False)
        db.commit()
        return deleted_count
