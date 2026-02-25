"""
WebSocket API
提供实时对话功能
"""

from fastapi import WebSocket, WebSocketDisconnect, Query, APIRouter
from typing import Dict, Optional
import json
import logging
from coze_coding_utils.runtime_ctx.context import new_context, Context

logger = logging.getLogger(__name__)

router = APIRouter()

# WebSocket连接管理器
class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        """建立连接"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket连接建立: {session_id}")

    def disconnect(self, session_id: str):
        """断开连接"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket连接断开: {session_id}")

    async def send_message(self, session_id: str, message: dict):
        """发送消息"""
        websocket = self.active_connections.get(session_id)
        if websocket:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"发送消息失败: {e}")
                self.disconnect(session_id)

manager = ConnectionManager()


@router.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket,
    token: str = Query(...),
    session_id: str = Query(...)
):
    """
    WebSocket实时对话接口

    连接参数:
    - token: JWT访问令牌
    - session_id: 会话ID（用于保持对话上下文）

    消息格式:
    {
        "type": "message",
        "content": "用户消息"
    }

    响应格式:
    {
        "type": "start",  // 开始响应
        "type": "chunk",  // 流式内容
        "type": "end",    // 结束响应
        "type": "error"   // 错误
    }
    """
    # 1. 验证Token
    try:
        from auth.auth_utils import verify_token
        payload = verify_token(token)

        if not payload:
            await websocket.close(code=4001, reason="Invalid token")
            return

        user_id = payload.get("user_id")
        user_role = payload.get("role")

        logger.info(f"WebSocket用户验证成功: {user_id} ({user_role})")

    except Exception as e:
        logger.error(f"Token验证失败: {e}")
        await websocket.close(code=4001, reason="Invalid token")
        return

    # 2. 建立连接
    await manager.connect(websocket, session_id)

    # 3. 准备Agent配置
    try:
        from agents.agent import build_agent
        from langchain_core.messages import HumanMessage

        config = {
            "configurable": {
                "thread_id": session_id,
                "user_id": user_id,
                "user_role": user_role
            }
        }

        logger.info(f"Agent配置: {config}")

        # 4. 消息处理循环
        while True:
            try:
                # 接收消息
                data = await websocket.receive_json()

                message_type = data.get("type")
                message = data.get("message")

                if not message or message_type != "message":
                    continue

                logger.info(f"收到消息: {message[:50]}...")

                # 5. 发送开始信号
                await manager.send_message(session_id, {
                    "type": "start",
                    "message": "正在思考..."
                })

                # 6. 调用Agent（流式）
                ctx = new_context(method="chat", configurable=config)
                agent = build_agent(ctx)

                full_content = ""

                async for chunk in agent.astream(
                    {"messages": [HumanMessage(content=message)]},
                    config=config,
                    stream_mode="messages"
                ):
                    if chunk.content:
                        full_content += chunk.content
                        # 7. 发送流式响应
                        await manager.send_message(session_id, {
                            "type": "chunk",
                            "content": chunk.content
                        })

                logger.info(f"Agent响应完成，内容长度: {len(full_content)}")

                # 8. 发送完成信号
                await manager.send_message(session_id, {
                    "type": "end",
                    "message": "完成"
                })

            except WebSocketDisconnect:
                logger.info(f"WebSocket客户端断开: {session_id}")
                manager.disconnect(session_id)
                break

            except Exception as e:
                logger.error(f"消息处理失败: {e}", exc_info=True)
                await manager.send_message(session_id, {
                    "type": "error",
                    "message": str(e)
                })

    except Exception as e:
        logger.error(f"WebSocket连接错误: {e}", exc_info=True)
        await manager.send_message(session_id, {
            "type": "error",
            "message": f"连接错误: {str(e)}"
        })
        manager.disconnect(session_id)


# 心跳检测端点（可选）
@router.get("/ws/health")
async def websocket_health():
    """WebSocket服务健康检查"""
    return {
        "status": "ok",
        "active_connections": len(manager.active_connections),
        "service": "WebSocket Chat"
    }
