from langchain.tools import tool, ToolRuntime
from tools.tool_utils_fixed import (
    get_user_context,
    check_student_access,
    require_student_access,
    get_student_name_by_id
)
from tools.logging_config import get_tool_logger, handle_tool_error, DatabaseError, ValidationError
from storage.database.db import get_session
from storage.database.student_manager import StudentManager, StudentCreate, StudentUpdate


logger = get_tool_logger(__name__)


@tool
@handle_tool_error
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
    
    Raises:
        ValidationError: 如果必填字段为空
        DatabaseError: 如果数据库操作失败
    """
    # 参数验证
    if not name or not name.strip():
        raise ValidationError("学生姓名不能为空")
    if not grade or not grade.strip():
        raise ValidationError("年级不能为空")
    if not class_name or not class_name.strip():
        raise ValidationError("班级不能为空")
    
    logger.info(f"创建学生: 姓名={name}, 年级={grade}, 班级={class_name}")
    
    db = get_session()
    try:
        mgr = StudentManager()
        student = mgr.create_student(db, StudentCreate(
            name=name.strip(),
            grade=grade.strip(),
            class_name=class_name.strip(),
            school=school.strip() if school else "",
            parent_contact=parent_contact.strip() if parent_contact else "",
            nickname=nickname.strip() if nickname else ""
        ))
        logger.info(f"成功创建学生: ID={student.id}, 姓名={student.name}")
        return f"成功创建学生：{student.name}（ID: {student.id}）"
    except Exception as e:
        logger.error(f"创建学生失败: {str(e)}", exc_info=True)
        raise DatabaseError(f"创建学生失败: {str(e)}", e)
    finally:
        db.close()


@tool
@handle_tool_error
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
    
    Raises:
        ValidationError: 如果 student_id 无效
        DatabaseError: 如果数据库操作失败
        ResourceNotFoundError: 如果学生不存在
    """
    # 参数验证
    if not isinstance(student_id, int) or student_id <= 0:
        raise ValidationError("学生ID必须是正整数")
    
    logger.info(f"获取学生信息: student_id={student_id}")
    
    db = get_session()
    try:
        mgr = StudentManager()
        student = mgr.get_student_by_id(db, student_id)
        if not student:
            logger.warning(f"学生不存在: student_id={student_id}")
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
        logger.info(f"成功获取学生信息: student_id={student_id}")
        return info
    except Exception as e:
        logger.error(f"获取学生信息失败: {str(e)}", exc_info=True)
        raise DatabaseError(f"获取学生信息失败: {str(e)}", e)
    finally:
        db.close()


@tool
@handle_tool_error
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
    
    Raises:
        ValidationError: 如果参数无效
        DatabaseError: 如果数据库操作失败
    """
    # 参数验证
    if not isinstance(student_id, int) or student_id <= 0:
        raise ValidationError("学生ID必须是正整数")
    if not isinstance(points, int):
        raise ValidationError("积分数必须是整数")
    if not reason or not reason.strip():
        raise ValidationError("原因说明不能为空")
    
    logger.info(f"给学生增加积分: student_id={student_id}, points={points}, reason={reason}")
    
    db = get_session()
    try:
        mgr = StudentManager()
        student = mgr.get_student_by_id(db, student_id)
        if not student:
            logger.warning(f"学生不存在: student_id={student_id}")
            return f"未找到ID为{student_id}的学生"
        
        student = mgr.add_points(db, student.id, points)
        logger.info(f"成功增加积分: student_id={student_id}, total_points={student.total_points}")
        return f"成功给学生{student.name}增加{points}积分，当前总积分：{student.total_points}（原因：{reason}）"
    except Exception as e:
        logger.error(f"增加积分失败: {str(e)}", exc_info=True)
        raise DatabaseError(f"增加积分失败: {str(e)}", e)
    finally:
        db.close()


@tool
@handle_tool_error
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
    
    Raises:
        ValidationError: 如果 student_id 无效
        DatabaseError: 如果数据库操作失败
    """
    # 参数验证
    if not isinstance(student_id, int) or student_id <= 0:
        raise ValidationError("学生ID必须是正整数")
    
    logger.info(f"升级魔法等级: student_id={student_id}")
    
    db = get_session()
    try:
        mgr = StudentManager()
        student = mgr.get_student_by_id(db, student_id)
        if student is None:
            logger.warning(f"学生不存在: student_id={student_id}")
            return f"未找到ID为{student_id}的学生"

        # 获取魔法等级
        old_level_value = getattr(student, 'magic_level', None)
        if old_level_value is None:
            old_level_value = 1

        student = mgr.upgrade_magic_level(db, student.id)
        if student is None:
            logger.error(f"升级失败: student_id={student_id}")
            raise DatabaseError("升级魔法等级失败")

        # 获取新等级
        new_level_value = getattr(student, 'magic_level', None)
        if new_level_value is None:
            new_level_value = 1

        if old_level_value == new_level_value:
            logger.info(f"学生已是最高等级: student_id={student_id}, level={old_level_value}")
            return f"学生{getattr(student, 'name', '该学生')}已经是最高等级（10级）了！"
        else:
            logger.info(f"成功升级魔法等级: student_id={student_id}, old={old_level_value}, new={new_level_value}")
            return f"恭喜！学生{getattr(student, 'name', '该学生')}的魔法等级从{old_level_value}级升级到{new_level_value}级！"
    except DatabaseError:
        raise
    except Exception as e:
        logger.error(f"升级魔法等级失败: {str(e)}", exc_info=True)
        raise DatabaseError(f"升级魔法等级失败: {str(e)}", e)
    finally:
        db.close()
