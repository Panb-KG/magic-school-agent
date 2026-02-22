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
from storage.database.course_manager import CourseManager
from storage.database.homework_manager import HomeworkManager
from storage.database.exercise_manager import ExerciseManager
from storage.database.achievement_manager import AchievementManager
from datetime import datetime, timedelta, date


def _safe_datetime(dt: Optional[datetime]) -> Optional[datetime]:
    """安全地获取 datetime 对象，避免类型检查器错误"""
    if dt is None:
        return None
    if isinstance(dt, datetime):
        return dt
    return None


def _safe_str(value: Any) -> str:
    """安全地转换为字符串"""
    return str(value) if value is not None else ""


@tool
@require_student_access()
def get_visual_schedule(student_id: int, runtime: ToolRuntime) -> str:
    """获取可视化课程表数据（用于前端展示）
    
    返回格式化的JSON数据，包含：
    - 按星期分组的课程列表
    - 时间段统计
    - 课程类型分布
    
    Args:
        student_id: 学生ID
    
    Returns:
        JSON格式的课程表数据
    """
    db = get_session()
    try:
        student_mgr = StudentManager()
        student = student_mgr.get_student_by_id(db, student_id)
        
        if not student:
            return f'{{"error": "未找到学生 ID {student_id}"}}'
        
        course_mgr = CourseManager()
        courses = course_mgr.get_courses(db, student.id)
        
        # 按星期分组
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        weekday_map = {
            "Monday": "周一", "Tuesday": "周二", "Wednesday": "周三",
            "Thursday": "周四", "Friday": "周五", "Saturday": "周六", "Sunday": "周日"
        }
        
        courses_by_day = {day: [] for day in weekdays}
        
        for course in courses:
            weekday = weekday_map.get(course.weekday, "")
            if weekday and weekday in courses_by_day:
                courses_by_day[weekday].append({
                    "id": course.id,
                    "name": course.course_name,
                    "type": course.course_type,  # school/extra
                    "time": f"{course.start_time or '--'}-{course.end_time or '--'}",
                    "location": course.location or "",
                    "teacher": course.teacher or "",
                    "classroom": course.classroom or "",
                    "notes": course.notes or ""
                })
        
        # 按时间排序
        for day in courses_by_day:
            courses_by_day[day].sort(key=lambda x: x["time"])
        
        # 统计数据
        school_courses = [c for c in courses if _safe_str(c.course_type) == "school"]
        extra_courses = [c for c in courses if _safe_str(c.course_type) == "extra"]
        
        # 统计每周总课时
        total_hours = sum([
            len(courses_by_day[day]) for day in weekdays
        ])
        
        import json
        schedule_data = {
            "student_id": student_id,
            "student_name": get_student_name_by_id(student_id) or "学生",
            "weekdays": weekdays,
            "courses": courses_by_day,
            "statistics": {
                "total_courses": len(courses),
                "school_courses": len(school_courses),
                "extra_courses": len(extra_courses),
                "course_count_by_day": {
                    day: len(courses_by_day[day]) for day in weekdays
                }
            },
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return json.dumps(schedule_data, ensure_ascii=False, indent=2)
    except Exception as e:
        import json
        return json.dumps({"error": f"获取课程表数据失败：{str(e)}"}, ensure_ascii=False)
    finally:
        db.close()


@tool
@require_student_access()
def get_points_trend(student_id: int, runtime: ToolRuntime, days: int = 30) -> str:
    """获取积分趋势数据（用于前端图表展示）

    返回格式化的JSON数据，包含：
    - 日期列表
    - 每日积分
    - 积分来源分布（作业/运动/朗读等）
    - 积分增长曲线

    Args:
        student_id: 学生ID
        days: 查询天数（默认30天）

    Returns:
        JSON格式的积分趋势数据
    """
    db = get_session()
    try:
        student_mgr = StudentManager()
        student = student_mgr.get_student_by_id(db, student_id)
        
        if not student:
            return f'{{"error": "未找到学生 ID {student_id}"}}'
        
        achievement_mgr = AchievementManager()
        achievements = achievement_mgr.get_student_achievements(db, student.id)
        
        # 生成日期列表
        end_date = date.today()
        date_list = []
        current_date = end_date - timedelta(days=days-1)
        
        while current_date <= end_date:
            date_list.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)
        
        # 按日期统计积分
        points_by_date = {d: 0 for d in date_list}
        points_breakdown = {
            "homework": 0,
            "exercise": 0,
            "reading": 0,
            "course_complete": 0,
            "other": 0
        }
        
        for ach in achievements:
            ach_date = _safe_datetime(ach.achieved_date)
            if ach_date:
                date_str = ach_date.date().strftime("%Y-%m-%d")
                
                if date_str in points_by_date:
                    points = ach.points or 0
                    points_by_date[date_str] += points
                    
                    # 分类统计
                    ach_type = _safe_str(ach.achievement_type)
                    if "homework" in ach_type:
                        points_breakdown["homework"] += points
                    elif "exercise" in ach_type:
                        points_breakdown["exercise"] += points
                    elif "reading" in ach_type:
                        points_breakdown["reading"] += points
                    elif "course" in ach_type:
                        points_breakdown["course_complete"] += points
                    else:
                        points_breakdown["other"] += points
        
        # 生成每日积分列表
        daily_points = [points_by_date[d] for d in date_list]
        
        # 计算累计积分
        cumulative_points = []
        total = 0
        for points in daily_points:
            total += points
            cumulative_points.append(total)
        
        import json
        trend_data = {
            "student_id": student_id,
            "student_name": get_student_name_by_id(student_id) or "学生",
            "date_list": date_list,
            "daily_points": daily_points,
            "cumulative_points": cumulative_points,
            "breakdown": points_breakdown,
            "summary": {
                "total_points": sum(daily_points),
                "average_daily": round(sum(daily_points) / days, 1) if days > 0 else 0,
                "max_daily": max(daily_points) if daily_points else 0,
                "days_with_points": sum(1 for p in daily_points if p > 0)
            },
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return json.dumps(trend_data, ensure_ascii=False, indent=2)
    except Exception as e:
        import json
        return json.dumps({"error": f"获取积分趋势失败：{str(e)}"}, ensure_ascii=False)
    finally:
        db.close()


@tool
@require_student_access()
def get_achievement_wall_data(student_id: int, runtime: ToolRuntime) -> str:
    """获取成就墙可视化数据（用于前端展示）
    
    返回格式化的JSON数据，包含：
    - 成就列表（按时间倒序）
    - 成就分类统计
    - 成就等级分布
    - 精选成就（用于展示墙）
    
    Args:
        student_id: 学生ID
    
    Returns:
        JSON格式的成就墙数据
    """
    db = get_session()
    try:
        student_mgr = StudentManager()
        student = student_mgr.get_student_by_id(db, student_id)
        
        if not student:
            return f'{{"error": "未找到学生 ID {student_id}"}}'
        
        achievement_mgr = AchievementManager()
        achievements = achievement_mgr.get_student_achievements(db, student.id)
        
        # 精选成就
        featured_achievements = [ach for ach in achievements if getattr(ach, 'is_featured', False)]
        
        # 按类型分类
        achievements_by_type = {}
        for ach in achievements:
            atype = _safe_str(ach.achievement_type) or "other"
            if atype not in achievements_by_type:
                achievements_by_type[atype] = []
            achievements_by_type[atype].append({
                "id": ach.id,
                "title": ach.title,
                "description": ach.description,
                "points": ach.points or 0,
                "level": _safe_str(ach.level or "bronze"),
                "icon_url": ach.icon_url or "",
                "achieved_date": _safe_datetime(ach.achieved_date).strftime("%Y-%m-%d") if _safe_datetime(ach.achieved_date) else ""
            })
        
        # 按等级分类
        achievements_by_level = {
            "bronze": [],
            "silver": [],
            "gold": [],
            "platinum": [],
            "diamond": []
        }
        for ach in achievements:
            level = _safe_str(ach.level) or "bronze"
            if level in achievements_by_level:
                achievements_by_level[level].append({
                    "id": ach.id,
                    "title": ach.title,
                    "description": ach.description,
                    "points": ach.points or 0,
                    "level": level,
                    "icon_url": ach.icon_url or "",
                    "achieved_date": _safe_datetime(ach.achieved_date).strftime("%Y-%m-%d") if _safe_datetime(ach.achieved_date) else ""
                })
        
        # 成就列表（最近10个）
        recent_achievements = []
        for ach in achievements[:10]:
            recent_achievements.append({
                "id": ach.id,
                "title": ach.title,
                "description": ach.description,
                "type": _safe_str(ach.achievement_type),
                "points": ach.points or 0,
                "level": _safe_str(ach.level) or "bronze",
                "icon_url": ach.icon_url or "",
                "achieved_date": _safe_datetime(ach.achieved_date).strftime("%Y-%m-%d") if _safe_datetime(ach.achieved_date) else ""
            })
        
        import json
        wall_data = {
            "student_id": student_id,
            "student_name": get_student_name_by_id(student_id) or "学生",
            "featured": featured_achievements,
            "by_type": achievements_by_type,
            "by_level": achievements_by_level,
            "recent": recent_achievements,
            "summary": {
                "total_count": len(achievements),
                "featured_count": len(featured_achievements),
                "total_points": sum(ach.points or 0 for ach in achievements),
                "type_distribution": {
                    atype: len(items) for atype, items in achievements_by_type.items()
                },
                "level_distribution": {
                    level: len(items) for level, items in achievements_by_level.items()
                }
            },
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return json.dumps(wall_data, ensure_ascii=False, indent=2)
    except Exception as e:
        import json
        return json.dumps({"error": f"获取成就墙数据失败：{str(e)}"}, ensure_ascii=False)
    finally:
        db.close()


@tool
@require_student_access()
def get_homework_progress(student_id: int, runtime: ToolRuntime) -> str:
    """获取作业进度数据（用于前端可视化）
    
    返回格式化的JSON数据，包含：
    - 待完成作业列表
    - 已完成作业列表
    - 逾期作业
    - 完成进度统计
    - 本周作业进度
    
    Args:
        student_id: 学生ID
    
    Returns:
        JSON格式的作业进度数据
    """
    db = get_session()
    try:
        student_mgr = StudentManager()
        student = student_mgr.get_student_by_id(db, student_id)
        
        if not student:
            return f'{{"error": "未找到学生 ID {student_id}"}}'
        
        homework_mgr = HomeworkManager()
        all_homeworks = homework_mgr.get_student_homeworks(db, student.id)
        pending_homeworks = homework_mgr.get_pending_homeworks(db, student.id)
        completed_homeworks = homework_mgr.get_student_homeworks(db, student.id, status="completed")
        overdue_homeworks = homework_mgr.get_overdue_homeworks(db, student.id)
        
        # 本周作业
        week_ago = datetime.now() - timedelta(days=7)
        week_homeworks = [
            hw for hw in all_homeworks
            if _safe_datetime(hw.created_at) and _safe_datetime(hw.created_at) >= week_ago
        ]
        week_completed = [hw for hw in week_homeworks if _safe_str(hw.status) == "completed"]
        
        # 待完成作业详情
        pending_list = []
        for hw in pending_homeworks:
            hw_due_date = _safe_datetime(hw.due_date)
            days_left = (hw_due_date - datetime.now()).days if hw_due_date else None
            is_urgent = days_left is not None and days_left <= 2
            pending_list.append({
                "id": hw.id,
                "title": hw.title,
                "subject": _safe_str(hw.subject) or "未指定",
                "due_date": hw_due_date.strftime("%Y-%m-%d") if hw_due_date else "",
                "days_left": days_left,
                "is_urgent": is_urgent,
                "priority": _safe_str(hw.priority) or "medium",
                "description": hw.description or ""
            })
        
        pending_list.sort(key=lambda x: x["days_left"] or 999)
        
        # 已完成作业详情（最近10个）
        completed_list = []
        for hw in completed_homeworks[-10:]:
            hw_updated_at = _safe_datetime(hw.updated_at)
            completed_list.append({
                "id": hw.id,
                "title": hw.title,
                "subject": _safe_str(hw.subject) or "未指定",
                "completed_date": hw_updated_at.strftime("%Y-%m-%d") if hw_updated_at else "",
                "points": hw.points or 0,
                "feedback": hw.feedback or ""
            })
        completed_list.reverse()
        
        import json
        progress_data = {
            "student_id": student_id,
            "student_name": get_student_name_by_id(student_id) or "学生",
            "statistics": {
                "total": len(all_homeworks),
                "completed": len(completed_homeworks),
                "pending": len(pending_homeworks),
                "overdue": len(overdue_homeworks),
                "completion_rate": round(len(completed_homeworks) / len(all_homeworks) * 100, 1) if all_homeworks else 0
            },
            "week_statistics": {
                "total": len(week_homeworks),
                "completed": len(week_completed),
                "completion_rate": round(len(week_completed) / len(week_homeworks) * 100, 1) if week_homeworks else 0
            },
            "pending": pending_list,
            "completed": completed_list,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return json.dumps(progress_data, ensure_ascii=False, indent=2)
    except Exception as e:
        import json
        return json.dumps({"error": f"获取作业进度失败：{str(e)}"}, ensure_ascii=False)
    finally:
        db.close()
