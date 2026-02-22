from langchain.tools import tool, ToolRuntime
from tools.tool_utils_fixed import (
    get_user_context,
    check_student_access,
    require_student_access,
    get_student_name_by_id
)
from storage.database.db import get_session
from storage.database.student_manager import StudentManager, StudentCreate, StudentUpdate


@tool
def create_student(
    name: str,
    grade: str,
    class_name: str,
    school: str,
    parent_contact: str,
    nickname: str,
    runtime: ToolRuntime
) -> str:
    """创建学生信息
    
    Args:
        name: 学生姓名
        grade: 年级
        class_name: 班级
        school: 学校
        parent_contact: 家长联系方式
        nickname: 昵称
    
    Returns:
        创建的学生信息
    """
    db = get_session()
    try:
        mgr = StudentManager()
        student = mgr.create_student(db, StudentCreate(
            name=name,
            grade=grade,
            class_name=class_name,
            school=school,
            parent_contact=parent_contact,
            nickname=nickname
        ))
        return f"成功创建学生：{student.name}（ID: {student.id}）"
    except Exception as e:
        return f"创建学生失败：{str(e)}"
    finally:
        db.close()


@tool
@require_student_access()
def get_student_info(
    student_id: int,
    runtime: ToolRuntime = None
) -> str:
    """获取学生信息
    
    Args:
        student_id: 学生ID
    
    Returns:
        学生详细信息
    """
    db = get_session()
    try:
        mgr = StudentManager()
        student = mgr.get_student_by_id(db, student_id)
        if not student:
            return f"未找到ID为{student_id}的学生"
        
        info = f"""
学生信息：
姓名：{student.name}
昵称：{student.nickname}
年级：{student.grade}
班级：{student.class_name}
学校：{student.school}
家长联系方式：{student.parent_contact}
魔法等级：{student.magic_level}
总积分：{student.total_points}
"""
        return info
    except Exception as e:
        return f"获取学生信息失败：{str(e)}"
    finally:
        db.close()


@tool
@require_student_access()
def add_student_points(
    student_id: int,
    points: int,
    reason: str,
    runtime: ToolRuntime = None
) -> str:
    """给学生增加积分
    
    Args:
        student_id: 学生ID
        points: 增加的积分数
        reason: 原因说明
    
    Returns:
        操作结果
    """
    db = get_session()
    try:
        mgr = StudentManager()
        student = mgr.get_student_by_id(db, student_id)
        if not student:
            return f"未找到ID为{student_id}的学生"
        
        student = mgr.add_points(db, student.id, points)
        return f"成功给学生{student.name}增加{points}积分，当前总积分：{student.total_points}（原因：{reason}）"
    except Exception as e:
        return f"增加积分失败：{str(e)}"
    finally:
        db.close()


@tool
@require_student_access()
def upgrade_magic_level(
    student_id: int,
    runtime: ToolRuntime = None
) -> str:
    """升级学生的魔法等级
    
    Args:
        student_id: 学生ID
    
    Returns:
        操作结果
    """
    db = get_session()
    try:
        mgr = StudentManager()
        student = mgr.get_student_by_id(db, student_id)
        if student is None:
            return f"未找到ID为{student_id}的学生"

        # 获取魔法等级
        old_level_value = getattr(student, 'magic_level', None)
        if old_level_value is None:
            old_level_value = 1

        student = mgr.upgrade_magic_level(db, student.id)
        if student is None:
            return "升级失败"

        # 获取新等级
        new_level_value = getattr(student, 'magic_level', None)
        if new_level_value is None:
            new_level_value = 1

        if old_level_value == new_level_value:
            return f"学生{getattr(student, 'name', '该学生')}已经是最高等级（10级）了！"
        else:
            return f"恭喜！学生{getattr(student, 'name', '该学生')}的魔法等级从{old_level_value}级升级到{new_level_value}级！"
    except Exception as e:
        return f"升级魔法等级失败：{str(e)}"
    finally:
        db.close()
