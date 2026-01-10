from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime

from storage.database.shared.model import Exercise


# Pydantic Models
class ExerciseCreate(BaseModel):
    student_id: int = Field(..., description="学生ID")
    exercise_type: str = Field(..., description="运动类型")
    duration: Optional[int] = Field(None, description="时长（分钟）")
    distance: Optional[float] = Field(None, description="距离（公里）")
    calories: Optional[int] = Field(None, description="消耗卡路里")
    date: datetime = Field(default_factory=datetime.now, description="运动日期")
    notes: Optional[str] = Field(None, description="备注")
    points: int = 0


class ExerciseUpdate(BaseModel):
    exercise_type: Optional[str] = None
    duration: Optional[int] = None
    distance: Optional[float] = None
    calories: Optional[int] = None
    date: Optional[datetime] = None
    notes: Optional[str] = None
    points: Optional[int] = None


class ExerciseManager:
    """运动记录管理器"""

    def create_exercise(self, db: Session, exercise_in: ExerciseCreate) -> Exercise:
        """创建运动记录"""
        exercise_data = exercise_in.model_dump()
        exercise = Exercise(**exercise_data)
        db.add(exercise)
        try:
            db.commit()
            db.refresh(exercise)
            return exercise
        except Exception:
            db.rollback()
            raise

    def get_exercises(self, db: Session, skip: int = 0, limit: int = 100, **filters) -> List[Exercise]:
        """获取运动记录列表"""
        query = db.query(Exercise)
        for attr, value in filters.items():
            if hasattr(Exercise, attr):
                query = query.filter(getattr(Exercise, attr) == value)
        return query.order_by(Exercise.date.desc()).offset(skip).limit(limit).all()

    def get_exercise_by_id(self, db: Session, exercise_id: int) -> Optional[Exercise]:
        """根据ID获取运动记录"""
        return db.query(Exercise).filter(Exercise.id == exercise_id).first()

    def get_student_exercises(self, db: Session, student_id: int, exercise_type: Optional[str] = None) -> List[Exercise]:
        """获取学生的运动记录"""
        query = db.query(Exercise).filter(Exercise.student_id == student_id)
        if exercise_type:
            query = query.filter(Exercise.exercise_type == exercise_type)
        return query.order_by(Exercise.date.desc()).all()

    def get_weekly_exercises(self, db: Session, student_id: int) -> dict:
        """获取本周运动统计"""
        exercises = self.get_student_exercises(db, student_id)
        stats = {
            "total_duration": 0,
            "total_calories": 0,
            "total_points": 0,
            "exercise_types": {},
            "total_count": len(exercises)
        }
        for exercise in exercises:
            stats["total_duration"] += exercise.duration or 0
            stats["total_calories"] += exercise.calories or 0
            stats["total_points"] += exercise.points or 0

            if exercise.exercise_type:
                if exercise.exercise_type not in stats["exercise_types"]:
                    stats["exercise_types"][exercise.exercise_type] = {"count": 0, "duration": 0}
                stats["exercise_types"][exercise.exercise_type]["count"] += 1
                stats["exercise_types"][exercise.exercise_type]["duration"] += exercise.duration or 0

        return stats

    def update_exercise(self, db: Session, exercise_id: int, exercise_in: ExerciseUpdate) -> Optional[Exercise]:
        """更新运动记录"""
        db_exercise = self.get_exercise_by_id(db, exercise_id)
        if not db_exercise:
            return None
        update_data = exercise_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_exercise, field):
                setattr(db_exercise, field, value)
        db.add(db_exercise)
        try:
            db.commit()
            db.refresh(db_exercise)
            return db_exercise
        except Exception:
            db.rollback()
            raise

    def delete_exercises(self, db: Session, **filters) -> int:
        """删除运动记录"""
        if not filters:
            return 0
        query = db.query(Exercise)
        for attr, value in filters.items():
            if hasattr(Exercise, attr):
                query = query.filter(getattr(Exercise, attr) == value)
        deleted_count = query.delete(synchronize_session=False)
        db.commit()
        return deleted_count
