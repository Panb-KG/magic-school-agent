"""
WebSocket服务器 - 用于实时推送数据更新

使用方法：
1. 启动WebSocket服务器：python src/websocket_server.py
2. 前端连接：ws://your-server:port/ws/{student_name}
3. 订阅频道：client.send({"type": "subscribe", "channels": ["dashboard", "achievements"]})
"""

import asyncio
import json
import logging
from typing import Set, Dict, Any
from datetime import datetime
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("⚠️  websockets库未安装，WebSocket功能不可用")
    print("   安装命令：pip install websockets")


# 配置
WS_HOST = os.getenv("WS_HOST", "0.0.0.0")
WS_PORT = int(os.getenv("WS_PORT", "8765"))
LOG_LEVEL = logging.INFO

# 配置日志
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WebSocketServer:
    """WebSocket服务器"""
    
    def __init__(self):
        # 存储所有连接的客户端 {student_name: Set[websocket]}
        self.clients: Dict[str, Set[Any]] = {}
        # 存储客户端订阅的频道 {websocket: Set[channel]}
        self.subscriptions: Dict[Any, Set[str]] = {}
    
    async def register(self, websocket, student_name: str):
        """注册新客户端"""
        if student_name not in self.clients:
            self.clients[student_name] = set()
        self.clients[student_name].add(websocket)
        self.subscriptions[websocket] = set()
        logger.info(f"客户端注册成功: {student_name}")
        
        # 发送欢迎消息
        await self.send_to_client(websocket, {
            "type": "welcome",
            "message": f"欢迎 {student_name}！连接已建立",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    async def unregister(self, websocket, student_name: str):
        """注销客户端"""
        if student_name in self.clients:
            self.clients[student_name].discard(websocket)
            if not self.clients[student_name]:
                del self.clients[student_name]
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]
        logger.info(f"客户端断开连接: {student_name}")
    
    async def send_to_client(self, websocket, message: Dict[str, Any]):
        """发送消息给客户端"""
        try:
            await websocket.send(json.dumps(message, ensure_ascii=False))
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
    
    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any], student_name: str = None):
        """向订阅了特定频道的客户端广播消息
        
        Args:
            channel: 频道名称（dashboard/achievements/homework/points）
            message: 消息内容
            student_name: 学生姓名（如果指定，只发送给该学生）
        """
        message["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if student_name:
            # 只发送给特定学生
            if student_name in self.clients:
                for client in self.clients[student_name]:
                    if channel in self.subscriptions.get(client, set()):
                        await self.send_to_client(client, {
                            "type": "update",
                            "channel": channel,
                            "data": message
                        })
        else:
            # 发送给所有订阅了该频道的客户端
            for student, clients in self.clients.items():
                for client in clients:
                    if channel in self.subscriptions.get(client, set()):
                        await self.send_to_client(client, {
                            "type": "update",
                            "channel": channel,
                            "data": message,
                            "student_name": student
                        })
    
    async def handle_message(self, websocket, student_name: str, message: str):
        """处理客户端消息"""
        try:
            data = json.loads(message)
            msg_type = data.get("type")
            
            if msg_type == "subscribe":
                # 订阅频道
                channels = data.get("channels", [])
                if websocket in self.subscriptions:
                    self.subscriptions[websocket].update(channels)
                logger.info(f"{student_name} 订阅频道: {channels}")
                
                # 发送订阅确认
                await self.send_to_client(websocket, {
                    "type": "subscribed",
                    "channels": channels,
                    "message": f"已订阅频道: {', '.join(channels)}"
                })
            
            elif msg_type == "unsubscribe":
                # 取消订阅
                channels = data.get("channels", [])
                if websocket in self.subscriptions:
                    for channel in channels:
                        self.subscriptions[websocket].discard(channel)
                logger.info(f"{student_name} 取消订阅: {channels}")
                
                await self.send_to_client(websocket, {
                    "type": "unsubscribed",
                    "channels": channels,
                    "message": f"已取消订阅: {', '.join(channels)}"
                })
            
            elif msg_type == "ping":
                # 心跳检测
                await self.send_to_client(websocket, {
                    "type": "pong",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            
            else:
                logger.warning(f"未知消息类型: {msg_type}")
        
        except json.JSONDecodeError:
            logger.error("JSON解析失败")
            await self.send_to_client(websocket, {
                "type": "error",
                "message": "消息格式错误"
            })
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            await self.send_to_client(websocket, {
                "type": "error",
                "message": str(e)
            })
    
    async def handle_client(self, websocket, path):
        """处理客户端连接"""
        # 从路径获取学生姓名
        # 路径格式: /ws/{student_name}
        try:
            student_name = path.strip("/").split("/")[-1]
            if not student_name:
                await websocket.close(1008, "缺少学生姓名")
                return
        except:
            await websocket.close(1008, "路径格式错误")
            return
        
        logger.info(f"新客户端连接: {student_name}")
        
        await self.register(websocket, student_name)
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, student_name, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"客户端主动断开: {student_name}")
        except Exception as e:
            logger.error(f"客户端连接异常: {e}")
        finally:
            await self.unregister(websocket, student_name)
    
    async def start(self):
        """启动WebSocket服务器"""
        logger.info(f"🚀 WebSocket服务器启动中...")
        logger.info(f"📍 监听地址: {WS_HOST}:{WS_PORT}")
        logger.info(f"🔗 连接地址: ws://{WS_HOST}:{WS_PORT}/ws/{{student_name}}")
        
        if not WEBSOCKETS_AVAILABLE:
            logger.error("❌ websockets库未安装，无法启动服务器")
            logger.info("   安装命令: pip install websockets")
            return
        
        server = await websockets.serve(
            self.handle_client,
            WS_HOST,
            WS_PORT,
            ping_interval=30,
            ping_timeout=20
        )
        
        logger.info("✅ WebSocket服务器启动成功！")
        
        await server.wait_closed()


# 全局WebSocket服务器实例
ws_server = None


def get_ws_server() -> WebSocketServer:
    """获取WebSocket服务器实例"""
    global ws_server
    if ws_server is None:
        ws_server = WebSocketServer()
    return ws_server


# 便捷函数：推送更新到特定频道
async def push_update(channel: str, data: Dict[str, Any], student_name: str = None):
    """推送更新到指定频道
    
    Args:
        channel: 频道名称（dashboard/achievements/homework/points）
        data: 数据内容
        student_name: 学生姓名（可选）
    """
    server = get_ws_server()
    await server.broadcast_to_channel(channel, data, student_name)


# 便捷函数：推送仪表盘更新
async def push_dashboard_update(student_name: str, changes: list):
    """推送仪表盘数据更新
    
    Args:
        student_name: 学生姓名
        changes: 变更的字段列表（如 ["profile", "stats"]）
    """
    await push_update("dashboard", {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "changes": changes
    }, student_name)


# 便捷函数：推送成就解锁
async def push_achievement_unlocked(student_name: str, achievement: dict):
    """推送新成就解锁通知
    
    Args:
        student_name: 学生姓名
        achievement: 成就数据
    """
    await push_update("achievements", {
        "event": "achievement_unlocked",
        "achievement": achievement
    }, student_name)


# 便捷函数：推送积分更新
async def push_points_update(student_name: str, points: int, total: int):
    """推送积分更新
    
    Args:
        student_name: 学生姓名
        points: 新增积分
        total: 总积分
    """
    await push_update("points", {
        "event": "points_added",
        "points": points,
        "total": total
    }, student_name)


# 便捷函数：推送作业状态变更
async def push_homework_update(student_name: str, homework_id: int, status: str):
    """推送作业状态更新
    
    Args:
        student_name: 学生姓名
        homework_id: 作业ID
        status: 新状态
    """
    await push_update("homework", {
        "event": "status_changed",
        "homework_id": homework_id,
        "status": status
    }, student_name)


async def main():
    """主函数"""
    server = get_ws_server()
    await server.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("WebSocket服务器已停止")
