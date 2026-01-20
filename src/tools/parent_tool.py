"""
家长专用工具
包含：查看学生对话、修改作业、奖励积分、管理学生等功能
"""

import logging
from typing import Optional
from langchain.tools import tool, ToolRuntime
from sqlalchemy import text
from storage.database.db import get_engine
from auth.permissions import check_student_access
import json

logger = logging.getLogger(__name__)


def _check_parent_access(runtime: ToolRuntime, student_id: str) -> bool:
    """检查家长是否有权访问该学生"""
    ctx = runtime.context if runtime else None
    configurable = ctx.get("configurable") if ctx and hasattr(ctx, 'get') else None
    user_id = configurable.get("user_id") if configurable and hasattr(configurable, 'get') else None
    user_role = configurable.get("user_role") if configurable and hasattr(configurable, 'get') else None

    if not user_id or not user_role:
        return False

    if user_role != 'parent':
        return False

    return check_student_access(user_id, user_role, student_id)


@tool
def parent_view_student_list(runtime: ToolRuntime) -> str:
    """
    家长查看关联的学生列表（仅家长可用）
    
    Args:
        runtime: 工具运行时上下文
    
    Returns:
        学生列表信息
    """
    ctx = runtime.context if runtime else None
    configurable = ctx.get("configurable") if ctx and hasattr(ctx, 'get') else None
    user_id = configurable.get("user_id") if configurable and hasattr(configurable, 'get') else None
    user_role = configurable.get("user_role") if configurable and hasattr(configurable, 'get') else None

    if user_role != 'parent':
        return "错误：此功能仅家长可用"
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    u.user_id,
                    u.username,
                    u.student_name,
                    u.grade,
                    ps.relationship,
                    ps.created_at AS linked_at
                FROM auth.parent_student_mapping ps
                JOIN auth.users u ON ps.student_id = u.user_id
                WHERE ps.parent_id = :parent_id
                ORDER BY ps.created_at DESC
            """), {"parent_id": user_id})
            
            rows = result.fetchall()
            
            if not rows:
                return "暂无关联的学生"
            
            students_text = "## 关联的学生\n\n"
            for i, row in enumerate(rows, 1):
                students_text += f"{i}. **{row[2]}** ({row[3]})\n"
                students_text += f"   - 用户名: {row[1]}\n"
                students_text += f"   - 关系: {row[4]}\n"
                students_text += f"   - 关联时间: {row[5].strftime('%Y-%m-%d') if row[5] else '未知'}\n\n"
            
            return students_text
    
    except Exception as e:
        logger.error(f"获取学生列表失败: {e}")
        return f"获取学生列表失败: {str(e)}"


@tool
def parent_view_student_conversations(
    student_id: str,
    limit: int = 10,
    runtime: ToolRuntime = None
) -> str:
    """
    家长查看学生的对话历史（仅家长可用）
    
    Args:
        student_id: 学生用户 ID
        limit: 返回的对话数量
        runtime: 工具运行时上下文
    
    Returns:
        对话历史信息
    """
    if not _check_parent_access(runtime, student_id):
        return "错误：无权查看该学生的对话历史"
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # 获取学生的 thread_id
            result = conn.execute(text("""
                SELECT thread_id FROM auth.user_sessions
                WHERE user_id = :user_id
                ORDER BY last_active_at DESC
                LIMIT 1
            """), {"user_id": student_id})
            
            thread_row = result.fetchone()
            if not thread_row:
                return "该学生暂无对话记录"
            
            thread_id = thread_row[0]
            
            # 查询对话摘要
            result = conn.execute(text("""
                SELECT 
                    topic,
                    summary_text,
                    key_points,
                    emotion,
                    conversation_date,
                    importance_score
                FROM memory.conversation_summary
                WHERE user_id = :user_id
                ORDER BY conversation_date DESC
                LIMIT :limit
            """), {"user_id": student_id, "limit": limit})
            
            rows = result.fetchall()
            
            if not rows:
                return "暂无对话记录"
            
            conversations_text = f"## 学生对话历史 (最近{len(rows)}条)\n\n"
            for i, row in enumerate(rows, 1):
                conversations_text += f"{i}. **{row[0]}** ({row[4].strftime('%Y-%m-%d %H:%M') if row[4] else '未知'})\n"
                conversations_text += f"   摘要: {row[1]}\n"
                if row[2]:
                    key_points = json.loads(row[2]) if isinstance(row[2], str) else row[2]
                    if key_points:
                        conversations_text += f"   关键点: {', '.join(key_points[:3])}\n"
                conversations_text += f"   情绪: {row[3]}\n"
                conversations_text += f"   重要性: {row[5]}/10\n\n"
            
            return conversations_text
    
    except Exception as e:
        logger.error(f"查看对话历史失败: {e}")
        return f"查看对话历史失败: {str(e)}"


@tool
def parent_modify_homework(
    student_id: str,
    homework_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    家长修改学生的作业（仅家长可用）
    
    Args:
        student_id: 学生用户 ID
        homework_id: 作业 ID
        title: 新标题（可选）
        description: 新描述（可选）
        due_date: 新截止日期（可选）
        runtime: 工具运行时上下文
    
    Returns:
        修改结果
    """
    if not _check_parent_access(runtime, student_id):
        return "错误：无权修改该学生的作业"
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # 构建更新语句
            update_fields = []
            params = {
                "student_id": student_id,
                "homework_id": homework_id
            }
            
            if title is not None:
                update_fields.append("title = :title")
                params["title"] = title
            
            if description is not None:
                update_fields.append("description = :description")
                params["description"] = description
            
            if due_date is not None:
                update_fields.append("due_date = :due_date")
                params["due_date"] = due_date
            
            if not update_fields:
                return "没有需要修改的内容"
            
            update_fields.append("updated_at = NOW()")
            
            sql = f"""
                UPDATE homework
                SET {', '.join(update_fields)}
                WHERE homework_id = :homework_id AND student_id = :student_id
                RETURNING title
            """
            
            result = conn.execute(text(sql), params)
            conn.commit()
            
            row = result.fetchone()
            if row:
                return f"作业修改成功：{row[0]}"
            else:
                return "未找到指定的作业"
    
    except Exception as e:
        logger.error(f"修改作业失败: {e}")
        return f"修改作业失败: {str(e)}"


@tool
def parent_reward_points(
    student_id: str,
    points: int,
    reason: str,
    runtime: ToolRuntime = None
) -> str:
    """
    家长给学生奖励积分（仅家长可用）
    
    Args:
        student_id: 学生用户 ID
        points: 积分数量
        reason: 奖励原因
        runtime: 工具运行时上下文
    
    Returns:
        奖励结果
    """
    if not _check_parent_access(runtime, student_id):
        return "错误：无权给该学生奖励积分"
    
    if points <= 0:
        return "积分必须大于0"
    
    if not reason:
        return "请提供奖励原因"
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # 添加积分记录
            conn.execute(text("""
                INSERT INTO point_records (student_id, points, reason, source)
                VALUES (:student_id, :points, :reason, 'parent_reward')
            """), {
                "student_id": student_id,
                "points": points,
                "reason": reason
            })
            
            # 更新学生总积分
            result = conn.execute(text("""
                UPDATE students
                SET total_points = total_points + :points
                WHERE student_id = :student_id
                RETURNING total_points
            """), {
                "student_id": student_id,
                "points": points
            })
            
            conn.commit()
            
            new_points = result.fetchone()[0] if result.fetchone() else None
            
            logger.info(f"家长奖励积分: parent -> {student_id}, +{points}, reason: {reason}")
            return f"成功奖励 {points} 积分！原因：{reason}。当前总积分：{new_points}"
    
    except Exception as e:
        logger.error(f"奖励积分失败: {e}")
        return f"奖励积分失败: {str(e)}"


@tool
def parent_approve_homework(
    student_id: str,
    homework_id: int,
    approved: bool,
    comment: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    家长审核学生作业（仅家长可用）
    
    Args:
        student_id: 学生用户 ID
        homework_id: 作业 ID
        approved: 是否批准
        comment: 评论（可选）
        runtime: 工具运行时上下文
    
    Returns:
        审核结果
    """
    ctx = runtime.context if runtime else None
    configurable = ctx.get("configurable") if ctx and hasattr(ctx, 'get') else None
    parent_id = configurable.get("user_id") if configurable and hasattr(configurable, 'get') else None
    
    if not _check_parent_access(runtime, student_id):
        return "错误：无权审核该学生的作业"
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # 更新作业审核状态
            conn.execute(text("""
                UPDATE homework
                SET 
                    parent_approved = :approved,
                    parent_comment = :comment,
                    parent_approved_at = NOW(),
                    approved_by = :parent_id
                WHERE homework_id = :homework_id AND student_id = :student_id
                RETURNING title
            """), {
                "approved": approved,
                "comment": comment,
                "parent_id": parent_id,
                "homework_id": homework_id,
                "student_id": student_id
            })
            
            row = conn.execute(text("SELECT title FROM homework WHERE homework_id = :homework_id"), 
                             {"homework_id": homework_id}).fetchone()
            
            conn.commit()
            
            if row:
                status = "批准" if approved else "未批准"
                message = f"作业【{row[0]}】已{status}"
                if comment:
                    message += f"，家长评论：{comment}"
                return message
            else:
                return "未找到指定的作业"
    
    except Exception as e:
        logger.error(f"审核作业失败: {e}")
        return f"审核作业失败: {str(e)}"


@tool
def parent_view_student_dashboard(
    student_id: str,
    runtime: ToolRuntime = None
) -> str:
    """
    家长查看学生的学习仪表盘（仅家长可用）
    
    Args:
        student_id: 学生用户 ID
        runtime: 工具运行时上下文
    
    Returns:
        学习仪表盘信息
    """
    if not _check_parent_access(runtime, student_id):
        return "错误：无权查看该学生的学习仪表盘"
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # 获取学生基本信息
            result = conn.execute(text("""
                SELECT student_name, grade, total_points, magic_level
                FROM students
                WHERE student_id = :student_id
            """), {"student_id": student_id})
            
            student = result.fetchone()
            if not student:
                return "未找到该学生"
            
            # 获取最近作业完成情况
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) FILTER (WHERE status = 'completed') as completed,
                    COUNT(*) FILTER (WHERE status = 'pending') as pending
                FROM homework
                WHERE student_id = :student_id
            """), {"student_id": student_id})
            
            homework_stats = result.fetchone()
            
            # 获取最近成就
            result = conn.execute(text("""
                SELECT achievement_name, earned_at
                FROM student_achievements sa
                JOIN achievements a ON sa.achievement_id = a.achievement_id
                WHERE sa.student_id = :student_id
                ORDER BY sa.earned_at DESC
                LIMIT 5
            """), {"student_id": student_id})
            
            achievements = result.fetchall()
            
            # 构建仪表盘文本
            dashboard_text = f"""## {student[0]} 的学习仪表盘

### 基本信息
- **年级**: {student[1]}
- **魔法等级**: {student[3]}
- **总积分**: {student[2]}

### 作业情况
- 已完成: {homework_stats[0] if homework_stats else 0}
- 待完成: {homework_stats[1] if homework_stats else 1}

### 最近成就
"""
            if achievements:
                for ach in achievements:
                    dashboard_text += f"- {ach[0]} ({ach[1].strftime('%Y-%m-%d') if ach[1] else '未知'})\n"
            else:
                dashboard_text += "暂无成就记录\n"
            
            return dashboard_text
    
    except Exception as e:
        logger.error(f"查看学习仪表盘失败: {e}")
        return f"查看学习仪表盘失败: {str(e)}"


@tool
def parent_link_student(
    student_username: str,
    relationship: str,
    runtime: ToolRuntime = None
) -> str:
    """
    家长关联学生账号（仅家长可用）
    
    Args:
        student_username: 学生用户名
        relationship: 关系 ('father', 'mother', 'guardian', 'other')
        runtime: 工具运行时上下文
    
    Returns:
        关联结果
    """
    ctx = runtime.context if runtime else None
    configurable = ctx.get("configurable") if ctx and hasattr(ctx, 'get') else None
    parent_id = configurable.get("user_id") if configurable and hasattr(configurable, 'get') else None
    user_role = configurable.get("user_role") if configurable and hasattr(configurable, 'get') else None

    if user_role != 'parent':
        return "错误：此功能仅家长可用"
    
    if relationship not in ['father', 'mother', 'guardian', 'other']:
        return "错误：无效的关系类型"
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # 查找学生用户
            result = conn.execute(text("""
                SELECT user_id, username, student_name, role
                FROM auth.users
                WHERE username = :username AND role = 'student'
            """), {"username": student_username})
            
            student = result.fetchone()
            if not student:
                return f"未找到学生账号: {student_username}"
            
            student_id = student[0]
            
            # 检查是否已关联
            result = conn.execute(text("""
                SELECT COUNT(*) FROM auth.parent_student_mapping
                WHERE parent_id = :parent_id AND student_id = :student_id
            """), {"parent_id": parent_id, "student_id": student_id})
            
            if result.scalar() > 0:
                return f"已经关联过学生: {student[2]}"
            
            # 创建关联
            conn.execute(text("""
                INSERT INTO auth.parent_student_mapping (parent_id, student_id, relationship)
                VALUES (:parent_id, :student_id, :relationship)
            """), {
                "parent_id": parent_id,
                "student_id": student_id,
                "relationship": relationship
            })
            
            conn.commit()
            
            logger.info(f"家长关联学生: {parent_id} -> {student_id} ({relationship})")
            return f"成功关联学生：{student[2]}（{student[1]}），关系：{relationship}"
    
    except Exception as e:
        logger.error(f"关联学生失败: {e}")
        return f"关联学生失败: {str(e)}"
