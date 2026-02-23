"""
历史对话管理工具
支持创建对话、添加消息、查询历史对话、生成对话标题等功能
"""

from langchain.tools import tool, ToolRuntime
from storage.database.db import get_session
from storage.database.conversation_manager import ConversationManager, ConversationCreate, MessageCreate, Message
from typing import Optional
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


@tool
def create_conversation(
    title: str,
    student_id: Optional[int] = None,
    runtime: ToolRuntime = None
) -> str:
    """创建新的对话会话

    Args:
        title: 对话标题（可以由AI生成，也可以由用户指定）
        student_id: 关联的学生ID（可选）
        runtime: 工具运行时上下文

    Returns:
        创建结果，包含对话ID和标题
    """
    user_id, _ = _get_user_context(runtime)

    if not user_id:
        return "错误：无法获取用户信息"

    db = get_session()
    try:
        conv_mgr = ConversationManager()

        # 如果没有提供标题，使用默认标题
        if not title or title.strip() == "":
            title = f"对话 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        conversation = conv_mgr.create_conversation(db, ConversationCreate(
            user_id=user_id,
            student_id=student_id,
            title=title
        ))

        return f"✅ 对话创建成功！\n\n对话ID：{conversation.id}\n标题：{conversation.title}\n创建时间：{conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    except Exception as e:
        return f"创建对话失败：{str(e)}"
    finally:
        db.close()


@tool
def add_message(
    conversation_id: int,
    role: str,
    content: str,
    runtime: ToolRuntime = None
) -> str:
    """添加消息到对话

    Args:
        conversation_id: 对话ID
        role: 角色（user/assistant）
        content: 消息内容
        runtime: 工具运行时上下文

    Returns:
        添加结果
    """
    user_id, _ = _get_user_context(runtime)

    if not user_id:
        return "错误：无法获取用户信息"

    db = get_session()
    try:
        conv_mgr = ConversationManager()

        # 验证对话是否存在且属于该用户
        conversation = conv_mgr.get_conversation_by_id(db, conversation_id)
        if not conversation:
            return f"错误：未找到ID为{conversation_id}的对话"

        if conversation.user_id != user_id:
            return "错误：无权访问该对话"

        # 验证角色
        if role not in ["user", "assistant"]:
            return "错误：角色必须是'user'或'assistant'"

        # 添加消息
        message = conv_mgr.add_message(db, MessageCreate(
            conversation_id=conversation_id,
            role=role,
            content=content
        ))

        return f"✅ 消息添加成功！\n\n消息ID：{message.id}\n角色：{role}\n内容：{content[:50]}{'...' if len(content) > 50 else ''}"
    except Exception as e:
        return f"添加消息失败：{str(e)}"
    finally:
        db.close()


@tool
def get_conversation_list(
    student_id: Optional[int] = None,
    limit: int = 20,
    runtime: ToolRuntime = None
) -> str:
    """获取历史对话列表（按时间倒序）

    Args:
        student_id: 关联的学生ID（可选，用于筛选特定学生的对话）
        limit: 返回数量限制（默认20条）
        runtime: 工具运行时上下文

    Returns:
        对话列表
    """
    user_id, _ = _get_user_context(runtime)

    if not user_id:
        return "错误：无法获取用户信息"

    db = get_session()
    try:
        conv_mgr = ConversationManager()
        conversations = conv_mgr.get_conversations(
            db,
            user_id=user_id,
            student_id=student_id,
            skip=0,
            limit=limit
        )

        if not conversations:
            return "📝 还没有历史对话，开始一段新的对话吧！"

        result = f"📚 历史对话列表（共{len(conversations)}条）\n\n"

        for i, conv in enumerate(conversations, 1):
            time_str = conv.created_at.strftime('%m-%d %H:%M')
            message_count = conv.message_count
            student_id_value = getattr(conv, 'student_id', None)
            student_info = f" | 学生ID: {student_id_value}" if student_id_value else ""

            result += f"{i}. {conv.title}\n"
            result += f"   📅 {time_str} | 💬 {message_count}条消息{student_info}\n"
            result += f"   🆔 对话ID: {conv.id}\n\n"

        return result
    except Exception as e:
        return f"获取对话列表失败：{str(e)}"
    finally:
        db.close()


@tool
def get_conversation_detail(
    conversation_id: int,
    runtime: ToolRuntime = None
) -> str:
    """获取对话详情（包含所有消息）

    Args:
        conversation_id: 对话ID
        runtime: 工具运行时上下文

    Returns:
        对话详情，包含标题、创建时间和所有消息
    """
    user_id, _ = _get_user_context(runtime)

    if not user_id:
        return "错误：无法获取用户信息"

    db = get_session()
    try:
        conv_mgr = ConversationManager()
        conversation = conv_mgr.get_conversation_by_id(db, conversation_id)

        if not conversation:
            return f"错误：未找到ID为{conversation_id}的对话"

        if conversation.user_id != user_id:
            return "错误：无权访问该对话"

        # 获取所有消息
        messages = conv_mgr.get_messages(db, conversation_id)

        result = f"📖 对话详情\n\n"
        result += f"📌 标题：{conversation.title}\n"
        result += f"📅 创建时间：{conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        result += f"💬 消息数量：{conversation.message_count}\n\n"
        result += f"─────────────────────────────\n\n"

        for msg in messages:
            role_value = getattr(msg, 'role', '')
            role_icon = "👤" if role_value == "user" else "🤖"
            role_name = "用户" if role_value == "user" else "助手"
            time_str = msg.created_at.strftime('%H:%M:%S')

            result += f"{role_icon} {role_name} [{time_str}]\n"
            result += f"{msg.content}\n\n"

        return result
    except Exception as e:
        return f"获取对话详情失败：{str(e)}"
    finally:
        db.close()


@tool
def search_conversations(
    keyword: str,
    limit: int = 20,
    runtime: ToolRuntime = None
) -> str:
    """搜索历史对话（按标题或摘要）

    Args:
        keyword: 搜索关键词
        limit: 返回数量限制（默认20条）
        runtime: 工具运行时上下文

    Returns:
        搜索结果
    """
    user_id, _ = _get_user_context(runtime)

    if not user_id:
        return "错误：无法获取用户信息"

    if not keyword or keyword.strip() == "":
        return "请输入搜索关键词"

    db = get_session()
    try:
        conv_mgr = ConversationManager()
        conversations = conv_mgr.search_conversations(
            db,
            user_id=user_id,
            keyword=keyword,
            skip=0,
            limit=limit
        )

        if not conversations:
            return f"🔍 未找到包含「{keyword}」的对话"

        result = f"🔍 搜索结果：「{keyword}」（共{len(conversations)}条）\n\n"

        for i, conv in enumerate(conversations, 1):
            time_str = conv.created_at.strftime('%m-%d %H:%M')
            message_count = conv.message_count

            result += f"{i}. {conv.title}\n"
            result += f"   📅 {time_str} | 💬 {message_count}条消息\n"
            result += f"   🆔 对话ID: {conv.id}\n\n"

        return result
    except Exception as e:
        return f"搜索对话失败：{str(e)}"
    finally:
        db.close()


@tool
def delete_conversation(
    conversation_id: int,
    runtime: ToolRuntime = None
) -> str:
    """删除对话会话及其所有消息

    Args:
        conversation_id: 对话ID
        runtime: 工具运行时上下文

    Returns:
        删除结果
    """
    user_id, _ = _get_user_context(runtime)

    if not user_id:
        return "错误：无法获取用户信息"

    db = get_session()
    try:
        conv_mgr = ConversationManager()

        # 验证对话是否存在且属于该用户
        conversation = conv_mgr.get_conversation_by_id(db, conversation_id)
        if not conversation:
            return f"错误：未找到ID为{conversation_id}的对话"

        if conversation.user_id != user_id:
            return "错误：无权删除该对话"

        success = conv_mgr.delete_conversation(db, conversation_id)

        if success:
            return f"✅ 对话已成功删除！\n\n对话ID：{conversation_id}"
        else:
            return "删除对话失败"
    except Exception as e:
        return f"删除对话失败：{str(e)}"
    finally:
        db.close()


@tool
def update_conversation_title(
    conversation_id: int,
    new_title: str,
    runtime: ToolRuntime = None
) -> str:
    """更新对话标题

    Args:
        conversation_id: 对话ID
        new_title: 新标题
        runtime: 工具运行时上下文

    Returns:
        更新结果
    """
    user_id, _ = _get_user_context(runtime)

    if not user_id:
        return "错误：无法获取用户信息"

    if not new_title or new_title.strip() == "":
        return "错误：标题不能为空"

    db = get_session()
    try:
        conv_mgr = ConversationManager()

        # 验证对话是否存在且属于该用户
        conversation = conv_mgr.get_conversation_by_id(db, conversation_id)
        if not conversation:
            return f"错误：未找到ID为{conversation_id}的对话"

        if conversation.user_id != user_id:
            return "错误：无权修改该对话"

        updated_conv = conv_mgr.update_title(db, conversation_id, new_title)

        if updated_conv:
            return f"✅ 对话标题已更新！\n\n新标题：{new_title}\n对话ID：{conversation_id}"
        else:
            return "更新对话标题失败"
    except Exception as e:
        return f"更新对话标题失败：{str(e)}"
    finally:
        db.close()
