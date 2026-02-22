from langchain.tools import tool, ToolRuntime
from tools.tool_utils_fixed import (
    get_user_context,
    check_student_access,
    require_student_access,
    get_student_name_by_id
)
from storage.database.db import get_session
from storage.database.achievement_manager import AchievementManager, AchievementCreate, AchievementUpdate


@tool
@require_student_access()
def add_achievement(
    student_id: int,
    achievement_type: str,
    title: str,
    description: str,
    points: int,
    level: str,
    is_featured: bool,
    runtime: ToolRuntime
) -> str:
    """添加成就记录
    
    Args:
        student_id: 学生ID
        achievement_type: 成就类型（homework_exercise/course_complete/reading_goal/study_effort/health_sport/creativity/persistence/other）
        title: 成就标题
        description: 成就描述
        points: 获得积分
        level: 等级（bronze/silver/gold/platinum/diamond）
        is_featured: 是否展示在成就墙
    
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
        
        achievement_mgr = AchievementManager()
        achievement = achievement_mgr.create_achievement(db, AchievementCreate(
            student_id=student.id,
            achievement_type=achievement_type,
            title=title,
            description=description,
            points=points,
            level=level,
            is_featured=is_featured
        ))
        
        # 同时给学生增加积分
        student = student_mgr.add_points(db, student.id, points)
        
        student_name = get_student_name_by_id(student_id) or "学生"
        return f"🎉 恭喜！{student_name}获得新成就：{title}（{level}级），获得{points}积分！当前总积分：{student.total_points}"
    except Exception as e:
        return f"添加成就失败：{str(e)}"
    finally:
        db.close()


@tool
@require_student_access()
def get_achievement_wall(
    student_id: int,
    runtime: ToolRuntime = None
) -> str:
    """获取学生的成就墙
    
    Args:
        student_id: 学生ID
    
    Returns:
        成就墙数据
    """
    db = get_session()
    try:
        from storage.database.student_manager import StudentManager
        student_mgr = StudentManager()
        student = student_mgr.get_student_by_id(db, student_id)
        
        if not student:
            return f"未找到ID为{student_id}的学生"
        
        achievement_mgr = AchievementManager()
        wall = achievement_mgr.get_achievement_wall(db, student.id)
        
        student_name = get_student_name_by_id(student_id) or "学生"
        
        result = f"🏆 {student_name}的成就墙 🏆\n\n"
        result += f"展示成就数：{wall['featured_count']}\n"
        result += f"成就总积分：{wall['total_points']}\n\n"
        
        result += "成就等级分布：\n"
        level_names = {
            "bronze": "青铜", "silver": "白银", "gold": "黄金",
            "platinum": "铂金", "diamond": "钻石"
        }
        for level, count in wall['achievements_by_level'].items():
            if count > 0:
                result += f"  {level_names[level]}：{count}个\n"
        
        if wall['recent_achievements']:
            result += "\n最近获得的成就：\n"
            for ach in wall['recent_achievements'][:10]:
                result += f"  🌟 {ach['title']}（{level_names.get(ach['level'], ach['level'])}级，{ach['points']}分）\n"
                if ach['description']:
                    result += f"     {ach['description']}\n"
        
        return result
    except Exception as e:
        return f"获取成就墙失败：{str(e)}"
    finally:
        db.close()


@tool
@require_student_access()
def get_all_achievements(
    student_id: int,
    runtime: ToolRuntime = None
) -> str:
    """获取学生的所有成就
    
    Args:
        student_id: 学生ID
    
    Returns:
        所有成就列表
    """
    db = get_session()
    try:
        from storage.database.student_manager import StudentManager
        student_mgr = StudentManager()
        student = student_mgr.get_student_by_id(db, student_id)
        
        if not student:
            return f"未找到ID为{student_id}的学生"
        
        achievement_mgr = AchievementManager()
        achievements = achievement_mgr.get_student_achievements(db, student.id)
        
        student_name = get_student_name_by_id(student_id) or "学生"
        
        if not achievements:
            return f"{student_name}还没有获得任何成就"
        
        result = f"{student_name}的所有成就：\n\n"
        for ach in achievements:
            if ach.achieved_date is not None:
                date_str = ach.achieved_date.strftime("%Y-%m-%d")
            else:
                date_str = "未记录"
            result += f"🌟 {ach.title}\n"
            result += f"   类型：{ach.achievement_type or '未指定'}\n"
            result += f"   等级：{ach.level or '未指定'}\n"
            result += f"   积分：{ach.points or 0}\n"
            result += f"   获得日期：{date_str}\n"
            if ach.description is not None:
                result += f"   描述：{ach.description}\n"
            result += "\n"
        
        return result
    except Exception as e:
        return f"获取成就列表失败：{str(e)}"
    finally:
        db.close()
