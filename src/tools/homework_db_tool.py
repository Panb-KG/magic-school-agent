"""
作业管理工具（修复版）
支持 student_id 和权限检查
"""

from langchain.tools import tool, ToolRuntime
from storage.database.db import get_session
from storage.database.homework_manager import HomeworkManager, HomeworkCreate, HomeworkUpdate
from storage.database.student_manager import StudentManager
from datetime import datetime


def _get_user_context(runtime: ToolRuntime) -> tuple:
    """
    从运行时上下文中获取用户信息
    
    Returns:
        (user_id, user_role) 或 (None, None) 如果无法获取
    """
    if not runtime:
        return None, None
    
    ctx = runtime.context if hasattr(runtime, 'context') else None
    if not ctx:
        return None, None
    
    configurable = ctx.get("configurable") if hasattr(ctx, 'get') else {}
    if not configurable:
        return None, None
    
    user_id = configurable.get("user_id")
    user_role = configurable.get("user_role")
    
    return user_id, user_role


def _check_student_access(runtime: ToolRuntime, student_id: int) -> bool:
    """
    检查用户是否有权访问该学生的数据
    
    Args:
        runtime: 工具运行时上下文
        student_id: 学生ID
    
    Returns:
        是否有权访问
    """
    user_id, user_role = _get_user_context(runtime)
    
    if not user_id or not user_role:
        return False
    
    try:
        from auth.permissions import permissions_manager
        
        # 学生只能访问自己的数据
        if user_role == 'student':
            # 需要通过 user_id 查找对应的 student_id
            db = get_session()
            try:
                student_mgr = StudentManager()
                student = student_mgr.get_student_by_id(db, student_id)
                if not student:
                    return False
                # 检查 student.user_id 是否匹配当前用户
                return student.user_id == user_id
            finally:
                db.close()
        
        # 家长可以访问关联学生的数据
        elif user_role == 'parent':
            return permissions_manager.can_access_student(user_id, str(student_id))
        
        return False
    except Exception as e:
        # 如果权限检查失败，为了安全起见，拒绝访问
        return False


@tool
def add_homework(
    student_id: int,
    title: str,
    subject: str,
    description: str,
    due_date: str,
    priority: str,
    runtime: ToolRuntime
) -> str:
    """添加作业任务
    
    Args:
        student_id: 学生ID
        title: 作业标题
        subject: 科目
        description: 作业描述
        due_date: 截止日期（YYYY-MM-DD格式）
        priority: 优先级（low/medium/high）
        runtime: 工具运行时上下文
    
    Returns:
        操作结果
    """
    # 权限检查
    if not _check_student_access(runtime, student_id):
        return "错误：无权访问该学生的数据"
    
    db = get_session()
    try:
        student_mgr = StudentManager()
        student = student_mgr.get_student_by_id(db, student_id)
        
        if not student:
            return f"未找到ID为{student_id}的学生"
        
        due_dt = datetime.strptime(due_date, "%Y-%m-%d") if due_date else None
        
        homework_mgr = HomeworkManager()
        homework = homework_mgr.create_homework(db, HomeworkCreate(
            student_id=student.id,
            title=title,
            subject=subject,
            description=description,
            due_date=due_dt,
            priority=priority
        ))
        
        student_name = student.name or "学生"
        return f"成功为{student_name}添加作业：{title}（截止：{due_date}，优先级：{priority}）"
    except Exception as e:
        return f"添加作业失败：{str(e)}"
    finally:
        db.close()


@tool
def get_homework_list(
    student_id: int,
    status: str,
    runtime: ToolRuntime
) -> str:
    """获取学生的作业列表
    
    Args:
        student_id: 学生ID
        status: 状态筛选（pending/completed/overdue/all）
        runtime: 工具运行时上下文
    
    Returns:
        作业列表
    """
    # 权限检查
    if not _check_student_access(runtime, student_id):
        return "错误：无权访问该学生的数据"
    
    db = get_session()
    try:
        student_mgr = StudentManager()
        student = student_mgr.get_student_by_id(db, student_id)
        
        if not student:
            return f"未找到ID为{student_id}的学生"
        
        homework_mgr = HomeworkManager()
        
        if status == "pending":
            homeworks = homework_mgr.get_pending_homeworks(db, student.id)
        elif status == "completed":
            homeworks = homework_mgr.get_student_homeworks(db, student.id, status="completed")
        elif status == "overdue":
            homeworks = homework_mgr.get_overdue_homeworks(db, student.id)
        else:
            homeworks = homework_mgr.get_student_homeworks(db, student.id)
        
        student_name = student.name or "学生"
        
        if not homeworks:
            return f"{student_name}目前没有{status if status != 'all' else ''}作业"
        
        result = f"{student_name}的作业列表：\n\n"
        for hw in homeworks:
            # 获取状态值
            hw_status_value = getattr(hw, 'status', None)
            if hw_status_value is None:
                hw_status_value = "pending"

            # 设置状态文本
            if hw_status_value == "pending":
                status_text = "待完成"
            else:
                status_text = "已完成"

            # 检查是否逾期
            is_overdue = False
            try:
                if hw_status_value == "pending":
                    due_date = getattr(hw, 'due_date', None)
                    if due_date is not None:
                        is_overdue = due_date < datetime.now()
            except:
                pass
            if is_overdue:
                status_text = "已逾期"

            # 设置截止日期字符串
            try:
                due_date = getattr(hw, 'due_date', None)
                if due_date is not None:
                    due_str = due_date.strftime("%Y-%m-%d")
                else:
                    due_str = "未设置"
            except:
                due_str = "未设置"

            result += f"📝 {hw.title}\n"
            result += f"   科目：{getattr(hw, 'subject', None) or '未指定'}\n"
            result += f"   状态：{status_text}\n"
            result += f"   截止日期：{due_str}\n"
            result += f"   优先级：{getattr(hw, 'priority', None) or 'medium'}\n"
            desc = getattr(hw, 'description', None)
            if desc is not None:
                result += f"   描述：{desc}\n"
            result += "\n"
        
        return result
    except Exception as e:
        return f"获取作业列表失败：{str(e)}"
    finally:
        db.close()


@tool
def submit_homework(
    homework_id: int,
    submission_url: str,
    runtime: ToolRuntime
) -> str:
    """提交作业
    
    Args:
        homework_id: 作业ID
        submission_url: 提交文件的URL
        runtime: 工具运行时上下文
    
    Returns:
        操作结果
    """
    db = get_session()
    try:
        homework_mgr = HomeworkManager()
        
        # 先获取作业以进行权限检查
        homework = homework_mgr.get_homework_by_id(db, homework_id)
        if not homework:
            return f"未找到ID为{homework_id}的作业"
        
        # 权限检查
        if not _check_student_access(runtime, homework.student_id):
            return "错误：无权提交该作业"
        
        # 提交作业
        homework = homework_mgr.submit_homework(db, homework_id, submission_url)
        
        if homework:
            return f"成功提交作业：{homework.title}（ID: {homework_id}）"
        else:
            return f"提交作业失败"
    except Exception as e:
        return f"提交作业失败：{str(e)}"
    finally:
        db.close()


@tool
def update_homework_status(
    homework_id: int,
    status: str,
    runtime: ToolRuntime
) -> str:
    """更新作业状态
    
    Args:
        homework_id: 作业ID
        status: 新状态（pending/in_progress/completed）
        runtime: 工具运行时上下文
    
    Returns:
        操作结果
    """
    db = get_session()
    try:
        homework_mgr = HomeworkManager()
        
        # 先获取作业以进行权限检查
        homework = homework_mgr.get_homework_by_id(db, homework_id)
        if not homework:
            return f"未找到ID为{homework_id}的作业"
        
        # 权限检查
        if not _check_student_access(runtime, homework.student_id):
            return "错误：无权修改该作业"
        
        # 更新作业状态
        homework = homework_mgr.update_homework(db, homework_id, HomeworkUpdate(status=status))
        
        if homework:
            return f"成功更新作业状态为：{status}"
        else:
            return f"更新作业状态失败"
    except Exception as e:
        return f"更新作业状态失败：{str(e)}"
    finally:
        db.close()


@tool
def delete_homework(
    homework_id: int,
    runtime: ToolRuntime
) -> str:
    """删除作业
    
    Args:
        homework_id: 作业ID
        runtime: 工具运行时上下文
    
    Returns:
        操作结果
    """
    db = get_session()
    try:
        homework_mgr = HomeworkManager()
        
        # 先获取作业以进行权限检查
        homework = homework_mgr.get_homework_by_id(db, homework_id)
        if not homework:
            return f"未找到ID为{homework_id}的作业"
        
        # 权限检查
        if not _check_student_access(runtime, homework.student_id):
            return "错误：无权删除该作业"
        
        # 删除作业
        deleted_count = homework_mgr.delete_homeworks(db, id=homework_id)
        
        if deleted_count > 0:
            return f"成功删除作业（ID: {homework_id}）"
        else:
            return f"删除作业失败"
    except Exception as e:
        return f"删除作业失败：{str(e)}"
    finally:
        db.close()


@tool
def verify_and_submit_homework(
    student_id: int,
    homework_title: str,
    file_content: bytes = None,
    proof_description: str = "",
    runtime: ToolRuntime = None
) -> str:
    """验证并提交作业
    
    Args:
        student_id: 学生ID
        homework_title: 作业标题
        file_content: 作业文件内容（可选）
        proof_description: 作业描述证明（可选）
        runtime: 工具运行时上下文
    
    Returns:
        操作结果
    """
    # 权限检查
    if not _check_student_access(runtime, student_id):
        return "错误：无权访问该学生的数据"
    
    db = get_session()
    try:
        student_mgr = StudentManager()
        homework_mgr = HomeworkManager()
        
        student = student_mgr.get_student_by_id(db, student_id)
        if not student:
            return f"未找到ID为{student_id}的学生"
        
        # 查找待提交的作业
        pending_homeworks = homework_mgr.get_pending_homeworks(db, student_id)
        target_homework = None

        from storage.database.shared.model import Homework
        for hw in pending_homeworks:
            # 使用 getattr 确保获取实际值而不是 ColumnExpression
            title_value = getattr(hw, 'title', '')
            if title_value == homework_title:
                target_homework = hw
                break
        
        if not target_homework:
            return f"未找到标题为'{homework_title}'的待提交作业"
        
        student_name = student.name or "学生"
        
        # 检查是否有证明
        if not file_content and not proof_description:
            return f"请上传作业照片或描述作业内容，我来验证{student_name}的作业"
        
        # 上传文件（如果有）
        submission_url = None
        if file_content:
            from tools.file_storage_tool import upload_homework_submission
            submission_url = upload_homework_submission(
                file_content=file_content,
                file_name=f"{homework_title}_submission.jpg",
                student_id=student_id,
                runtime=runtime
            )
        
        # 提交作业
        homework = homework_mgr.submit_homework(db, target_homework.id, submission_url)
        
        # 更新积分
        if homework:
            points = 15  # 默认积分
            student_mgr.add_points(db, student_id, points)
            
            return f"🎉 太棒了！{student_name}已经完成了作业\"{homework_title}\"！\n\n✨ 获得{points}个魔法积分！\n\n{student_name}的努力就像施展了完美的魔法咒语！继续保持！"
        else:
            return "提交作业失败"
    except Exception as e:
        return f"验证并提交作业失败：{str(e)}"
    finally:
        db.close()
