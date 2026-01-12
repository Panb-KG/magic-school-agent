from langchain.tools import tool, ToolRuntime
from storage.database.db import get_session
from storage.database.homework_manager import HomeworkManager, HomeworkCreate, HomeworkUpdate
from datetime import datetime


@tool
def add_homework(
    student_name: str,
    title: str,
    subject: str,
    description: str,
    due_date: str,
    priority: str,
    runtime: ToolRuntime
) -> str:
    """添加作业任务
    
    Args:
        student_name: 学生姓名
        title: 作业标题
        subject: 科目
        description: 作业描述
        due_date: 截止日期（YYYY-MM-DD格式）
        priority: 优先级（low/medium/high）
    
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
        return f"成功添加作业：{title}（截止：{due_date}，优先级：{priority}）"
    except Exception as e:
        return f"添加作业失败：{str(e)}"
    finally:
        db.close()


@tool
def get_homework_list(student_name: str, status: str, runtime: ToolRuntime) -> str:
    """获取学生的作业列表
    
    Args:
        student_name: 学生姓名
        status: 状态筛选（pending/completed/overdue/all）
    
    Returns:
        作业列表
    """
    db = get_session()
    try:
        from storage.database.student_manager import StudentManager
        student_mgr = StudentManager()
        student = student_mgr.get_student_by_name(db, student_name)
        
        if not student:
            return f"未找到姓名为{student_name}的学生"
        
        homework_mgr = HomeworkManager()
        
        if status == "pending":
            homeworks = homework_mgr.get_pending_homeworks(db, student.id)
        elif status == "completed":
            homeworks = homework_mgr.get_student_homeworks(db, student.id, status="completed")
        elif status == "overdue":
            homeworks = homework_mgr.get_overdue_homeworks(db, student.id)
        else:
            homeworks = homework_mgr.get_student_homeworks(db, student.id)
        
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
def submit_homework(homework_id: int, submission_url: str, runtime: ToolRuntime) -> str:
    """提交作业
    
    Args:
        homework_id: 作业ID
        submission_url: 提交文件的URL
    
    Returns:
        操作结果
    """
    db = get_session()
    try:
        homework_mgr = HomeworkManager()
        homework = homework_mgr.submit_homework(db, homework_id, submission_url)
        
        if homework:
            return f"成功提交作业：{homework.title}（ID: {homework_id}）"
        else:
            return f"未找到ID为{homework_id}的作业"
    except Exception as e:
        return f"提交作业失败：{str(e)}"
    finally:
        db.close()


@tool
def update_homework_status(homework_id: int, status: str, runtime: ToolRuntime) -> str:
    """更新作业状态
    
    Args:
        homework_id: 作业ID
        status: 新状态（pending/in_progress/completed）
    
    Returns:
        操作结果
    """
    db = get_session()
    try:
        homework_mgr = HomeworkManager()
        homework = homework_mgr.update_homework(db, homework_id, HomeworkUpdate(status=status))
        
        if homework:
            return f"成功更新作业状态为：{status}"
        else:
            return f"未找到ID为{homework_id}的作业"
    except Exception as e:
        return f"更新作业状态失败：{str(e)}"
    finally:
        db.close()


@tool
def verify_and_submit_homework(
    student_name: str,
    homework_title: str,
    file_content: bytes = None,
    proof_description: str = "",
    runtime: ToolRuntime = None
) -> str:
    """验证并提交作业（带作业证明）
    
    当小巫师说"我已经完成作业"时使用此工具。会要求上传作业证明（照片或描述），
    然后更新作业状态为已完成。
    
    Args:
        student_name: 学生姓名
        homework_title: 作业标题（部分匹配即可）
        file_content: 作业证明文件内容（bytes，可选）
        proof_description: 作业证明描述（如果没有文件，用文字描述作业内容）
    
    Returns:
        操作结果
    """
    db = get_session()
    try:
        from storage.database.student_manager import StudentManager
        student_mgr = StudentManager()
        student = student_mgr.get_student_by_name(db, student_name)
        
        if not student:
            return f"未找到姓名为{student_name}的小巫师"
        
        homework_mgr = HomeworkManager()
        homeworks = homework_mgr.get_pending_homeworks(db, student.id)
        
        # 根据标题匹配作业
        target_homework = None
        for hw in homeworks:
            if homework_title.lower() in hw.title.lower() or hw.title.lower() in homework_title.lower():
                target_homework = hw
                break
        
        if not target_homework:
            return f"未找到标题包含\"{homework_title}\"的待完成作业。请检查作业标题是否正确。"
        
        # 处理作业证明
        submission_url = None
        if file_content:
            # 上传作业证明文件
            from tools.file_storage_tool import upload_homework_submission
            file_key = upload_homework_submission(
                file_content=file_content,
                file_name=f"{target_homework.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                student_id=student.id,
                runtime=runtime
            )
            # 生成可访问的URL
            from tools.file_storage_tool import generate_file_url
            submission_url = generate_file_url(file_key=file_key, runtime=runtime)
        elif proof_description:
            # 如果没有文件，用描述作为证明
            submission_url = f"proof_text:{proof_description}"
        else:
            # 两者都没有，要求提供证明
            return f"请上传作业证明（照片）或描述作业完成情况，我才能确认你完成了作业\"{target_homework.title}\"哦！✨"
        
        # 提交作业
        homework = homework_mgr.submit_homework(db, target_homework.id, submission_url)
        
        if homework:
            # 给予积分奖励（作业完成后奖励10-20积分）
            points = 15
            student_mgr = StudentManager()
            student_mgr.add_points(db, student.id, points)

            # 检查是否可以升级魔法等级
            current_points = getattr(student, 'total_points', 0) + points
            new_magic_level = (current_points // 100) + 1
            current_magic_level = getattr(student, 'magic_level', 1)
            if new_magic_level > current_magic_level:
                student_mgr.upgrade_magic_level(db, student.id)
                return f"🎉 太棒了！你已经完成了作业\"{target_homework.title}\"！\n\n✨ 获得{points}个魔法积分！\n🏆 恭喜升级到{new_magic_level}级魔法师！\n\n你的努力就像施展了完美的魔法咒语！继续保持！"
            else:
                return f"🎉 太棒了！你已经完成了作业\"{target_homework.title}\"！\n\n✨ 获得{points}个魔法积分！\n\n你的努力就像施展了完美的魔法咒语！继续保持！"
        else:
            return f"提交作业失败，请再试一次"
    except Exception as e:
        return f"验证作业失败：{str(e)}"
    finally:
        db.close()


@tool
def delete_homework(homework_id: int, runtime: ToolRuntime) -> str:
    """删除作业
    
    Args:
        homework_id: 作业ID
    
    Returns:
        操作结果
    """
    db = get_session()
    try:
        homework_mgr = HomeworkManager()
        deleted_count = homework_mgr.delete_homeworks(db, id=homework_id)
        
        if deleted_count > 0:
            return f"成功删除作业（ID: {homework_id}）"
        else:
            return f"未找到ID为{homework_id}的作业"
    except Exception as e:
        return f"删除作业失败：{str(e)}"
    finally:
        db.close()
