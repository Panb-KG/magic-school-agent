from langchain.tools import tool, ToolRuntime
from tools.tool_utils_fixed import (
    get_user_context,
    check_student_access,
    require_student_access,
    get_student_name_by_id
)
from storage.database.db import get_session
from storage.database.exercise_manager import ExerciseManager, ExerciseCreate, ExerciseUpdate
from datetime import datetime


@tool
@require_student_access()
def add_exercise(
    student_id: int,
    exercise_type: str,
    duration: int,
    distance: float,
    calories: int,
    notes: str,
    runtime: ToolRuntime
) -> str:
    """添加运动记录
    
    Args:
        student_id: 学生ID
        exercise_type: 运动类型（run/swim/basketball/football/skip_rope/yoga/other）
        duration: 时长（分钟）
        distance: 距离（公里）
        calories: 消耗卡路里
        notes: 备注
    
    Returns:
        操作结果
    """
    db = get_session()
    try:
        from storage.database.student_manager import StudentManager
        student_mgr = StudentManager()
        student = student_mgr.get_student_by_id(db, student_id)
        
        if not student:
            return f"未找到ID为{student_id}的学生"
        
        # 计算积分：每分钟运动给1分
        points = duration // 10
        
        exercise_mgr = ExerciseManager()
        exercise = exercise_mgr.create_exercise(db, ExerciseCreate(
            student_id=student.id,
            exercise_type=exercise_type,
            duration=duration,
            distance=distance,
            calories=calories,
            notes=notes,
            points=points
        ))
        
        # 同时给学生增加积分
        student = student_mgr.add_points(db, student.id, points)
        
        student_name = get_student_name_by_id(student_id) or "学生"
        return f"成功为{student_name}记录运动：{exercise_type}，时长{duration}分钟，获得{points}积分！当前总积分：{student.total_points}"
    except Exception as e:
        return f"添加运动记录失败：{str(e)}"
    finally:
        db.close()


@tool
@require_student_access()
def get_exercise_list(
    student_id: int,
    exercise_type: str = "",
    runtime: ToolRuntime = None
) -> str:
    """获取学生的运动记录列表
    
    Args:
        student_id: 学生ID
        exercise_type: 运动类型筛选（可选）
    
    Returns:
        运动记录列表
    """
    db = get_session()
    try:
        from storage.database.student_manager import StudentManager
        student_mgr = StudentManager()
        student = student_mgr.get_student_by_id(db, student_id)
        
        if not student:
            return f"未找到ID为{student_id}的学生"
        
        exercise_mgr = ExerciseManager()
        exercises = exercise_mgr.get_student_exercises(db, student.id, exercise_type=exercise_type if exercise_type else None)
        
        student_name = get_student_name_by_id(student_id) or "学生"
        
        if not exercises:
            return f"{student_name}还没有{exercise_type if exercise_type else ''}运动记录"
        
        result = f"{student_name}的运动记录：\n\n"
        for ex in exercises:
            if ex.date is not None:
                date_str = ex.date.strftime("%Y-%m-%d %H:%M")
            else:
                date_str = "未记录"
            result += f"🏃 {ex.exercise_type}\n"
            result += f"   时间：{date_str}\n"
            result += f"   时长：{ex.duration or 0}分钟\n"
            if ex.distance is not None:
                result += f"   距离：{ex.distance}公里\n"
            if ex.calories is not None:
                result += f"   消耗卡路里：{ex.calories}\n"
            result += f"   获得积分：{ex.points or 0}\n"
            if ex.notes is not None:
                result += f"   备注：{ex.notes}\n"
            result += "\n"
        
        return result
    except Exception as e:
        return f"获取运动记录失败：{str(e)}"
    finally:
        db.close()


@tool
@require_student_access()
def get_weekly_exercise_stats(
    student_id: int,
    runtime: ToolRuntime = None
) -> str:
    """获取本周运动统计
    
    Args:
        student_id: 学生ID
    
    Returns:
        周运动统计数据
    """
    db = get_session()
    try:
        from storage.database.student_manager import StudentManager
        student_mgr = StudentManager()
        student = student_mgr.get_student_by_id(db, student_id)
        
        if not student:
            return f"未找到ID为{student_id}的学生"
        
        exercise_mgr = ExerciseManager()
        stats = exercise_mgr.get_weekly_exercises(db, student.id)
        
        student_name = get_student_name_by_id(student_id) or "学生"
        
        result = f"{student_name}的运动统计：\n\n"
        result += f"总运动次数：{stats['total_count']}\n"
        result += f"总时长：{stats['total_duration']}分钟\n"
        result += f"总消耗卡路里：{stats['total_calories']}\n"
        result += f"总获得积分：{stats['total_points']}\n\n"
        
        if stats['exercise_types']:
            result += "按运动类型统计：\n"
            for ex_type, data in stats['exercise_types'].items():
                result += f"  {ex_type}：{data['count']}次，{data['duration']}分钟\n"
        
        return result
    except Exception as e:
        return f"获取运动统计失败：{str(e)}"
    finally:
        db.close()
