from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime

from storage.database.shared.model import Achievement


# Pydantic Models
class AchievementCreate(BaseModel):
    student_id: int = Field(..., description="学生ID")
    achievement_type: str = Field(..., description="成就类型")
    title: str = Field(..., description="成就标题")
    description: Optional[str] = Field(None, description="成就描述")
    icon_url: Optional[str] = Field(None, description="图标URL")
    points: int = 0
    level: str = "bronze"
    is_featured: bool = False


class AchievementUpdate(BaseModel):
    achievement_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None
    points: Optional[int] = None
    level: Optional[str] = None
    is_featured: Optional[bool] = None


class AchievementManager:
    """成就管理器"""

    def create_achievement(self, db: Session, achievement_in: AchievementCreate) -> Achievement:
        """创建成就"""
        achievement_data = achievement_in.model_dump()
        achievement = Achievement(**achievement_data)
        db.add(achievement)
        try:
            db.commit()
            db.refresh(achievement)
            return achievement
        except Exception:
            db.rollback()
            raise

    def get_achievements(self, db: Session, skip: int = 0, limit: int = 100, **filters) -> List[Achievement]:
        """获取成就列表"""
        query = db.query(Achievement)
        for attr, value in filters.items():
            if hasattr(Achievement, attr):
                query = query.filter(getattr(Achievement, attr) == value)
        return query.order_by(Achievement.achieved_date.desc()).offset(skip).limit(limit).all()

    def get_achievement_by_id(self, db: Session, achievement_id: int) -> Optional[Achievement]:
        """根据ID获取成就"""
        return db.query(Achievement).filter(Achievement.id == achievement_id).first()

    def get_student_achievements(self, db: Session, student_id: int, featured_only: bool = False) -> List[Achievement]:
        """获取学生的成就列表"""
        query = db.query(Achievement).filter(Achievement.student_id == student_id)
        if featured_only:
            query = query.filter(Achievement.is_featured == True)
        return query.order_by(Achievement.achieved_date.desc()).all()

    def get_achievement_wall(self, db: Session, student_id: int) -> dict:
        """获取成就墙数据"""
        achievements = self.get_student_achievements(db, student_id, featured_only=True)
        summary = {
            "featured_count": len(achievements),
            "total_points": sum(a.points or 0 for a in achievements),
            "achievements_by_level": {
                "bronze": 0, "silver": 0, "gold": 0, "platinum": 0, "diamond": 0
            },
            "recent_achievements": []
        }

        for achievement in achievements:
            level = achievement.level or "bronze"
            summary["achievements_by_level"][level] += 1
            summary["recent_achievements"].append({
                "id": achievement.id,
                "title": achievement.title,
                "description": achievement.description,
                "icon_url": achievement.icon_url,
                "points": achievement.points,
                "level": achievement.level,
                "achieved_date": achievement.achieved_date.isoformat() if achievement.achieved_date else None
            })

        return summary

    def update_achievement(self, db: Session, achievement_id: int, achievement_in: AchievementUpdate) -> Optional[Achievement]:
        """更新成就"""
        db_achievement = self.get_achievement_by_id(db, achievement_id)
        if not db_achievement:
            return None
        update_data = achievement_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_achievement, field):
                setattr(db_achievement, field, value)
        db.add(db_achievement)
        try:
            db.commit()
            db.refresh(db_achievement)
            return db_achievement
        except Exception:
            db.rollback()
            raise

    def delete_achievements(self, db: Session, **filters) -> int:
        """删除成就"""
        if not filters:
            return 0
        query = db.query(Achievement)
        for attr, value in filters.items():
            if hasattr(Achievement, attr):
                query = query.filter(getattr(Achievement, attr) == value)
        deleted_count = query.delete(synchronize_session=False)
        db.commit()
        return deleted_count
