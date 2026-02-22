from langchain.tools import tool, ToolRuntime
from tools.tool_utils_fixed import (
    get_user_context,
    check_student_access,
    require_student_access,
    get_student_name_by_id
)
from storage.database.db import get_session
from storage.database.course_manager import CourseManager, CourseCreate, CourseUpdate


@tool
@require_student_access()
def add_course(
    student_id: int,
    course_name: str,
    course_type: str,
    weekday: str,
    start_time: str,
    end_time: str,
    location: str,
    teacher: str,
    classroom: str,
    runtime: ToolRuntime
) -> str:
    """添加课程到课程表
    
    Args:
        student_id: 学生ID
        course_name: 课程名称
        course_type: 课程类型（school/extra）
        weekday: 星期几（Monday/Tuesday/Wednesday/Thursday/Friday/Saturday/Sunday）
        start_time: 开始时间（HH:MM）
        end_time: 结束时间（HH:MM）
        location: 上课地点
        teacher: 老师姓名
        classroom: 教室
    
    Returns:
        操作结果
    """
    # 权限检查（由装饰器自动完成）
    
    db = get_session()
    try:
        from storage.database.student_manager import StudentManager
        student_mgr = StudentManager()
        student = student_mgr.get_student_by_id(db, student_id)
        
        if not student:
            return f"未找到ID为{student_id}的学生"
        
        course_mgr = CourseManager()
        course = course_mgr.create_course(db, CourseCreate(
            student_id=student.id,
            course_name=course_name,
            course_type=course_type,
            weekday=weekday,
            start_time=start_time,
            end_time=end_time,
            location=location,
            teacher=teacher,
            classroom=classroom
        ))
        
        student_name = student.name or "学生"
        return f"成功为{student_name}添加课程：{course_name}（{weekday} {start_time}-{end_time}）"
    except Exception as e:
        return f"添加课程失败：{str(e)}"
    finally:
        db.close()


@tool
@require_student_access()
def get_weekly_schedule(
    student_id: int,
    runtime: ToolRuntime
) -> str:
    """获取学生的周课程表
    
    Args:
        student_id: 学生ID
    
    Returns:
        周课程表
    """
    # 权限检查（由装饰器自动完成）
    
    db = get_session()
    try:
        from storage.database.student_manager import StudentManager
        student_mgr = StudentManager()
        student = student_mgr.get_student_by_id(db, student_id)
        
        if not student:
            return f"未找到ID为{student_id}的学生"
        
        course_mgr = CourseManager()
        schedule = course_mgr.get_weekly_schedule(db, student.id)
        
        student_name = student.name or "学生"
        result = f"{student_name}的周课程表：\n\n"
        for day, courses in schedule.items():
            if courses:
                result += f"【{day}】\n"
                for c in courses:
                    c_type = "学校课程" if c['course_type'] == 'school' else "课外课程"
                    result += f"  {c['start_time']}-{c['end_time']} {c['course_name']}（{c_type}）\n"
                    result += f"    地点：{c['location'] or '未指定'}，老师：{c['teacher'] or '未指定'}\n"
                result += "\n"
        
        return result if any(schedule.values()) else f"{student_name}还没有安排任何课程"
    except Exception as e:
        return f"获取课程表失败：{str(e)}"
    finally:
        db.close()


@tool
def update_course(
    course_id: int,
    course_name: str,
    weekday: str,
    start_time: str,
    end_time: str,
    runtime: ToolRuntime
) -> str:
    """更新课程信息
    
    Args:
        course_id: 课程ID
        course_name: 新课程名称
        weekday: 新星期
        start_time: 新开始时间
        end_time: 新结束时间
    
    Returns:
        操作结果
    """
    # 需要先获取课程以进行权限检查
    db = get_session()
    try:
        from storage.database.course_manager import CourseManager
        course_mgr = CourseManager()
        
        # 获取课程
        course = course_mgr.get_course_by_id(db, course_id)
        if not course:
            return f"未找到ID为{course_id}的课程"
        
        # 权限检查
        if not check_student_access(runtime, course.student_id):
            return "错误：无权修改该课程"
        
        # 更新课程
        course = course_mgr.update_course(db, course_id, CourseUpdate(
            course_name=course_name,
            weekday=weekday,
            start_time=start_time,
            end_time=end_time
        ))
        
        if course:
            return f"成功更新课程：{course_name}（{weekday} {start_time}-{end_time}）"
        else:
            return f"未找到ID为{course_id}的课程"
    except Exception as e:
        return f"更新课程失败：{str(e)}"
    finally:
        db.close()


@tool
def delete_course(
    course_id: int,
    runtime: ToolRuntime
) -> str:
    """删除课程
    
    Args:
        course_id: 课程ID
    
    Returns:
        操作结果
    """
    # 需要先获取课程以进行权限检查
    db = get_session()
    try:
        from storage.database.course_manager import CourseManager
        course_mgr = CourseManager()
        
        # 获取课程
        course = course_mgr.get_course_by_id(db, course_id)
        if not course:
            return f"未找到ID为{course_id}的课程"
        
        # 权限检查
        if not check_student_access(runtime, course.student_id):
            return "错误：无权删除该课程"
        
        # 删除课程
        deleted_count = course_mgr.delete_courses(db, id=course_id)
        
        if deleted_count > 0:
            return f"成功删除课程（ID: {course_id}）"
        else:
            return f"未找到ID为{course_id}的课程"
    except Exception as e:
        return f"删除课程失败：{str(e)}"
    finally:
        db.close()
