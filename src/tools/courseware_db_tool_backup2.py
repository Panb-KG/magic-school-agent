from langchain.tools import tool, ToolRuntime
from storage.database.db import get_session
from storage.database.courseware_manager import CoursewareManager, CoursewareCreate, CoursewareUpdate


@tool
def add_courseware(
    student_name: str,
    title: str,
    subject: str,
    file_type: str,
    file_url: str,
    category: str,
    description: str,
    runtime: ToolRuntime
) -> str:
    """添加课件
    
    Args:
        student_name: 学生姓名
        title: 课件标题
        subject: 科目
        file_type: 文件类型（pdf/doc/ppt/image/video/other）
        file_url: 文件URL
        category: 分类标签
        description: 课件描述
    
    Returns:
        操作结果
    """
    db = get_session()
    try:
        from storage.database.student_manager import StudentManager
        student_mgr = StudentManager()
        student = student_mgr.get_student_by_name(db, student_name)
        
        if not student:
            return f"未找到姓名为{student_name}的学生"
        
        courseware_mgr = CoursewareManager()
        courseware = courseware_mgr.create_courseware(db, CoursewareCreate(
            student_id=student.id,
            title=title,
            subject=subject,
            file_type=file_type,
            file_url=file_url,
            category=category,
            description=description
        ))
        return f"成功添加课件：{title}（类型：{file_type}）"
    except Exception as e:
        return f"添加课件失败：{str(e)}"
    finally:
        db.close()


@tool
def get_courseware_list(student_name: str, subject: str, runtime: ToolRuntime) -> str:
    """获取学生的课件列表
    
    Args:
        student_name: 学生姓名
        subject: 科目筛选（可选）
    
    Returns:
        课件列表
    """
    db = get_session()
    try:
        from storage.database.student_manager import StudentManager
        student_mgr = StudentManager()
        student = student_mgr.get_student_by_name(db, student_name)
        
        if not student:
            return f"未找到姓名为{student_name}的学生"
        
        courseware_mgr = CoursewareManager()
        coursewares = courseware_mgr.get_student_coursewares(db, student.id, subject=subject if subject else None)
        
        if not coursewares:
            return f"{student_name}还没有{subject if subject else ''}课件"
        
        result = f"{student_name}的课件列表：\n\n"
        for cw in coursewares:
            result += f"📚 {cw.title}\n"
            result += f"   科目：{cw.subject or '未指定'}\n"
            result += f"   类型：{cw.file_type}\n"
            result += f"   分类：{cw.category or '未指定'}\n"
            result += f"   下载次数：{cw.download_count}\n"
            if cw.description is not None:
                result += f"   描述：{cw.description}\n"
            result += "\n"
        
        return result
    except Exception as e:
        return f"获取课件列表失败：{str(e)}"
    finally:
        db.close()


@tool
def delete_courseware(courseware_id: int, runtime: ToolRuntime) -> str:
    """删除课件
    
    Args:
        courseware_id: 课件ID
    
    Returns:
        操作结果
    """
    db = get_session()
    try:
        courseware_mgr = CoursewareManager()
        deleted_count = courseware_mgr.delete_coursewares(db, id=courseware_id)
        
        if deleted_count > 0:
            return f"成功删除课件（ID: {courseware_id}）"
        else:
            return f"未找到ID为{courseware_id}的课件"
    except Exception as e:
        return f"删除课件失败：{str(e)}"
    finally:
        db.close()
