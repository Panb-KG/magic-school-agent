from typing import Dict, Any, List, Optional
from langchain.tools import tool, ToolRuntime
from tools.tool_utils_fixed import (
    get_user_context,
    check_student_access,
    require_student_access,
    get_student_name_by_id
)
from storage.database.db import get_session
from storage.database.student_manager import StudentManager
from storage.database.homework_manager import HomeworkManager
from storage.database.exercise_manager import ExerciseManager
from storage.database.achievement_manager import AchievementManager
from storage.database.shared.model import Homework
from datetime import datetime, timedelta


def _safe_datetime(dt: Optional[datetime]) -> Optional[datetime]:
    """安全地获取 datetime 对象，避免类型检查器错误"""
    if dt is None:
        return None
    # 确保 dt 是一个 datetime 对象
    if isinstance(dt, datetime):
        return dt
    return None


def _safe_str(value: Any) -> str:
    """安全地转换为字符串"""
    return str(value) if value is not None else ""


@tool
@require_student_access()
def get_student_dashboard(student_id: int, runtime: ToolRuntime) -> str:
    """获取学生仪表盘数据（用于Web前端展示）
    
    返回格式化的JSON数据，包含：
    - 学生档案信息
    - 统计数据（积分、等级、完成数等）
    - 最近成就
    - 待办事项（即将到期作业）
    - 快速操作建议
    
    Args:
        student_id: 学生ID
    
    Returns:
        JSON格式的仪表盘数据
    """
    db = get_session()
    try:
        student_mgr = StudentManager()
        student = student_mgr.get_student_by_id(db, student_id)
        
        if not student:
            return f'{{"error": "未找到学生 ID {student_id}"}}'
        
        # 1. 学生档案
        profile = {
            "id": student.id,
            "name": student.name,
            "grade": student.grade or "未设置",
            "class_name": student.class_name or "未设置",
            "school": student.school or "未设置",
            "nickname": student.nickname or student.name,
            "avatar_url": student.avatar_url or "",
            "magic_level": getattr(student, 'magic_level', 1),
            "total_points": getattr(student, 'total_points', 0),
            "level_progress": getattr(student, 'total_points', 0) % 100,
            "next_level_points": (getattr(student, 'total_points', 0) // 100 + 1) * 100
        }
        
        # 2. 统计数据
        # 作业统计
        homework_mgr = HomeworkManager()
        all_homeworks: List[Homework] = homework_mgr.get_student_homeworks(db, student.id)
        completed_homeworks = [hw for hw in all_homeworks if str(hw.status) == "completed"]
        pending_homeworks = homework_mgr.get_pending_homeworks(db, student.id)
        
        # 运动统计
        exercise_mgr = ExerciseManager()
        exercises = exercise_mgr.get_student_exercises(db, student.id)
        total_exercise_duration: int = sum(ex.duration or 0 for ex in exercises)
        
        # 成就统计
        achievement_mgr = AchievementManager()
        achievements = achievement_mgr.get_student_achievements(db, student.id)
        featured_achievements = achievement_mgr.get_student_achievements(db, student.id, featured_only=True)
        
        stats = {
            "total_points": getattr(student, 'total_points', 0),
            "magic_level": getattr(student, 'magic_level', 1),
            "completed_homeworks": len(completed_homeworks),
            "pending_homeworks": len(pending_homeworks),
            "total_exercises": len(exercises),
            "total_exercise_minutes": total_exercise_duration,
            "total_achievements": len(achievements),
            "featured_achievements": len(featured_achievements),
            "homework_completion_rate": round(len(completed_homeworks) / len(all_homeworks) * 100, 1) if all_homeworks else 0
        }
        
        # 3. 最近成就（最近5个）
        recent_achievements = []
        for ach in achievements[:5]:
            ach_date = _safe_datetime(ach.achieved_date)
            date_str = ach_date.strftime("%Y-%m-%d") if ach_date else ""
            recent_achievements.append({
                "id": ach.id,
                "title": ach.title,
                "description": ach.description,
                "type": _safe_str(ach.achievement_type),
                "points": ach.points or 0,
                "level": _safe_str(ach.level or "bronze"),
                "icon_url": ach.icon_url or "",
                "achieved_date": date_str
            })
        
        # 4. 待办事项
        # 即将到期的作业（7天内）
        upcoming_deadline = datetime.now() + timedelta(days=7)
        urgent_homeworks = [
            hw for hw in pending_homeworks
            if _safe_datetime(hw.due_date) and _safe_datetime(hw.due_date) <= upcoming_deadline
        ]
        urgent_homeworks.sort(key=lambda x: _safe_datetime(x.due_date) or datetime.min)
        
        todos = []
        for hw in urgent_homeworks[:5]:
            hw_due_date = _safe_datetime(hw.due_date)
            days_left = (hw_due_date - datetime.now()).days if hw_due_date else None
            urgency = "high" if days_left and days_left <= 1 else "medium"
            todos.append({
                "id": hw.id,
                "title": hw.title,
                "subject": _safe_str(hw.subject) or "未指定",
                "due_date": hw_due_date.strftime("%Y-%m-%d") if hw_due_date else "",
                "days_left": days_left,
                "urgency": urgency,
                "type": "homework"
            })
        
        # 5. 快速操作建议
        suggestions = []
        if len(pending_homeworks) > 0:
            suggestions.append({
                "action": "check_homeworks",
                "message": f"你有 {len(pending_homeworks)} 个待完成作业",
                "priority": "high"
            })
        if len(urgent_homeworks) > 0:
            suggestions.append({
                "action": "urgent_homeworks",
                "message": f"{len(urgent_homeworks)} 个作业即将到期",
                "priority": "high"
            })
        if total_exercise_duration < 60:  # 本周运动少于1小时
            suggestions.append({
                "action": "exercise",
                "message": "本周运动量较少，建议多运动哦！",
                "priority": "medium"
            })
        
        # 6. 本周积分统计
        week_ago = datetime.now() - timedelta(days=7)
        week_points = 0
        week_points_detail = {
            "homework": 0,
            "exercise": 0,
            "reading": 0,
            "other": 0
        }
        
        for ach in achievements:
            ach_date = _safe_datetime(ach.achieved_date)
            if ach_date and ach_date >= week_ago:
                points = ach.points or 0
                week_points += points
                ach_type = _safe_str(ach.achievement_type)
                if "homework" in ach_type:
                    week_points_detail["homework"] += points
                elif "exercise" in ach_type:
                    week_points_detail["exercise"] += points
                elif "reading" in ach_type:
                    week_points_detail["reading"] += points
                else:
                    week_points_detail["other"] += points
        
        week_stats = {
            "total_points": week_points,
            "breakdown": week_points_detail
        }
        
        # 组装完整数据
        import json
        dashboard_data = {
            "profile": profile,
            "stats": stats,
            "recent_achievements": recent_achievements,
            "todos": todos,
            "suggestions": suggestions,
            "week_stats": week_stats,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return json.dumps(dashboard_data, ensure_ascii=False, indent=2)
    except Exception as e:
        import json
        return json.dumps({"error": f"获取仪表盘数据失败：{str(e)}"}, ensure_ascii=False)
    finally:
        db.close()


@tool
@require_student_access()
def get_student_profile_summary(student_id: int, runtime: ToolRuntime) -> str:
    """获取学生档案摘要（用于展示卡片）
    
    Args:
        student_id: 学生ID
    
    Returns:
        JSON格式的学生档案摘要
    """
    db = get_session()
    try:
        student_mgr = StudentManager()
        student = student_mgr.get_student_by_id(db, student_id)
        
        if not student:
            return f'{{"error": "未找到学生 ID {student_id}"}}'
        
        # 获取成就统计
        achievement_mgr = AchievementManager()
        achievement_wall = achievement_mgr.get_achievement_wall(db, student.id)
        
        import json
        profile_data = {
            "id": student.id,
            "name": student.name,
            "nickname": student.nickname or student.name,
            "grade": student.grade or "未设置",
            "class_name": student.class_name or "未设置",
            "school": student.school or "未设置",
            "avatar_url": student.avatar_url or "",
            "magic_level": getattr(student, 'magic_level', 1),
            "total_points": getattr(student, 'total_points', 0),
            "level_progress": getattr(student, 'total_points', 0) % 100,
            "level_percentage": round(getattr(student, 'total_points', 0) % 100, 1),
            "achievements_by_level": achievement_wall.get("achievements_by_level", {}),
            "featured_count": achievement_wall.get("featured_count", 0),
            "total_achievement_points": achievement_wall.get("total_points", 0)
        }
        
        return json.dumps(profile_data, ensure_ascii=False, indent=2)
    except Exception as e:
        import json
        return json.dumps({"error": f"获取学生档案失败：{str(e)}"}, ensure_ascii=False)
    finally:
        db.close()
