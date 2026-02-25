"""
流式响应 API
提供Server-Sent Events (SSE) 流式对话功能
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatStreamRequest(BaseModel):
    """流式对话请求"""
    message: str
    session_id: str


async def get_current_user_from_token(authorization: str):
    """从Token获取用户信息"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="无效的认证格式")

    token = authorization[7:]  # 移除 "Bearer " 前缀

    from auth.auth_utils import verify_token
    payload = verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="无效或过期的令牌")

    return {
        "user_id": payload.get("user_id"),
        "role": payload.get("role"),
        "exp": payload.get("exp")
    }


@router.post("/api/v1/chat/stream")
async def chat_stream(
    request: ChatStreamRequest,
    authorization: str = None
):
    """
    流式对话接口（Server-Sent Events）

    请求头:
    - Authorization: Bearer <access_token>

    请求体:
    {
        "message": "用户消息",
        "session_id": "会话ID"
    }

    响应格式（SSE）:
    data: {"type": "start", "message": "正在思考..."}
    data: {"type": "chunk", "content": "流式内容"}
    data: {"type": "end", "message": "完成"}
    data: {"type": "error", "message": "错误信息"}
    """
    # 1. 验证Token
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少认证令牌")

    try:
        current_user = await get_current_user_from_token(authorization)
        logger.info(f"用户验证成功: {current_user['user_id']} ({current_user['role']})")
    except Exception as e:
        logger.error(f"Token验证失败: {e}")
        raise HTTPException(status_code=401, detail=str(e))

    # 2. 准备Agent配置
    user_id = current_user["user_id"]
    user_role = current_user["role"]
    session_id = request.session_id

    config = {
        "configurable": {
            "thread_id": session_id,
            "user_id": user_id,
            "user_role": user_role
        }
    }

    logger.info(f"流式对话配置: {config}")

    # 3. 生成流式响应
    async def generate() -> AsyncGenerator[str, None]:
        """生成SSE流式响应"""
        try:
            # 发送开始信号
            yield f"data: {json.dumps({'type': 'start', 'message': '正在思考...'}, ensure_ascii=False)}\n\n"

            # 调用Agent
            from agents.agent import build_agent
            from langchain_core.messages import HumanMessage
            from coze_coding_utils.runtime_ctx.context import new_context

            ctx = new_context(method="chat_stream", configurable=config)
            agent = build_agent(ctx)

            full_content = ""

            async for chunk in agent.astream(
                {"messages": [HumanMessage(content=request.message)]},
                config=config,
                stream_mode="messages"
            ):
                if chunk.content:
                    full_content += chunk.content
                    # 发送流式内容
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk.content}, ensure_ascii=False)}\n\n"

            logger.info(f"Agent响应完成，内容长度: {len(full_content)}")

            # 发送完成信号
            yield f"data: {json.dumps({'type': 'end', 'message': '完成'}, ensure_ascii=False)}\n\n"

        except Exception as e:
            logger.error(f"流式对话失败: {e}", exc_info=True)
            # 发送错误信号
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用Nginx缓冲
        }
    )


@router.post("/api/v1/chat")
async def chat(
    request: ChatStreamRequest,
    authorization: str = None
):
    """
    普通对话接口（非流式）

    请求头:
    - Authorization: Bearer <access_token>

    请求体:
    {
        "message": "用户消息",
        "session_id": "会话ID"
    }

    响应:
    {
        "type": "message",
        "content": "完整的响应内容"
    }
    """
    # 1. 验证Token
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少认证令牌")

    try:
        current_user = await get_current_user_from_token(authorization)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    # 2. 准备Agent配置
    user_id = current_user["user_id"]
    user_role = current_user["role"]
    session_id = request.session_id

    config = {
        "configurable": {
            "thread_id": session_id,
            "user_id": user_id,
            "user_role": user_role
        }
    }

    # 3. 调用Agent
    try:
        from agents.agent import build_agent
        from langchain_core.messages import HumanMessage
        from coze_coding_utils.runtime_ctx.context import new_context

        ctx = new_context(method="chat", configurable=config)
        agent = build_agent(ctx)

        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=request.message)]},
            config=config
        )

        # 提取响应内容
        content = ""
        if hasattr(result, "messages"):
            for msg in result.messages:
                if hasattr(msg, "content") and msg.content:
                    content += str(msg.content)

        return {
            "type": "message",
            "content": content,
            "session_id": session_id
        }

    except Exception as e:
        logger.error(f"对话失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
