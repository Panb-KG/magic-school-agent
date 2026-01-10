from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime

from storage.database.shared.model import Course


# Pydantic Models
class CourseCreate(BaseModel):
    student_id: int = Field(..., description="学生ID")
    course_name: str = Field(..., description="课程名称")
    course_type: str = Field(..., description="课程类型：school/extra")
    weekday: Optional[str] = Field(None, description="星期几")
    start_time: Optional[str] = Field(None, description="开始时间 HH:MM")
    end_time: Optional[str] = Field(None, description="结束时间 HH:MM")
    location: Optional[str] = Field(None, description="上课地点")
    teacher: Optional[str] = Field(None, description="老师")
    classroom: Optional[str] = Field(None, description="教室")
    is_recurring: bool = True
    notes: Optional[str] = Field(None, description="备注")


class CourseUpdate(BaseModel):
    course_name: Optional[str] = None
    course_type: Optional[str] = None
    weekday: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None
    teacher: Optional[str] = None
    classroom: Optional[str] = None
    is_recurring: Optional[bool] = None
    notes: Optional[str] = None


class CourseManager:
    """课程管理器"""

    def create_course(self, db: Session, course_in: CourseCreate) -> Course:
        """创建课程"""
        course_data = course_in.model_dump()
        course = Course(**course_data)
        db.add(course)
        try:
            db.commit()
            db.refresh(course)
            return course
        except Exception:
            db.rollback()
            raise

    def get_courses(self, db: Session, skip: int = 0, limit: int = 100, **filters) -> List[Course]:
        """获取课程列表"""
        query = db.query(Course)
        for attr, value in filters.items():
            if hasattr(Course, attr):
                query = query.filter(getattr(Course, attr) == value)
        return query.offset(skip).limit(limit).all()

    def get_course_by_id(self, db: Session, course_id: int) -> Optional[Course]:
        """根据ID获取课程"""
        return db.query(Course).filter(Course.id == course_id).first()

    def get_student_courses(self, db: Session, student_id: int, course_type: Optional[str] = None) -> List[Course]:
        """获取学生的所有课程"""
        query = db.query(Course).filter(Course.student_id == student_id)
        if course_type:
            query = query.filter(Course.course_type == course_type)
        return query.order_by(Course.weekday, Course.start_time).all()

    def get_weekly_schedule(self, db: Session, student_id: int) -> dict:
        """获取周课程表"""
        courses = self.get_student_courses(db, student_id)
        schedule = {
            "Monday": [], "Tuesday": [], "Wednesday": [],
            "Thursday": [], "Friday": [], "Saturday": [], "Sunday": []
        }
        for course in courses:
            if course.weekday:
                schedule[course.weekday].append({
                    "id": course.id,
                    "course_name": course.course_name,
                    "course_type": course.course_type,
                    "start_time": course.start_time,
                    "end_time": course.end_time,
                    "location": course.location,
                    "teacher": course.teacher,
                    "classroom": course.classroom,
                    "notes": course.notes
                })
        return schedule

    def update_course(self, db: Session, course_id: int, course_in: CourseUpdate) -> Optional[Course]:
        """更新课程"""
        db_course = self.get_course_by_id(db, course_id)
        if not db_course:
            return None
        update_data = course_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_course, field):
                setattr(db_course, field, value)
        db.add(db_course)
        try:
            db.commit()
            db.refresh(db_course)
            return db_course
        except Exception:
            db.rollback()
            raise

    def delete_courses(self, db: Session, **filters) -> int:
        """删除课程"""
        if not filters:
            return 0
        query = db.query(Course)
        for attr, value in filters.items():
            if hasattr(Course, attr):
                query = query.filter(getattr(Course, attr) == value)
        deleted_count = query.delete(synchronize_session=False)
        db.commit()
        return deleted_count
