"""
魔法课桌 - Coze API Python SDK

一个简单易用的 Coze API Python 客户端封装
"""

import requests
import json
from typing import Optional, List, Dict, Any, Callable, AsyncGenerator, Generator
import asyncio
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CozeMessage:
    """Coze 消息对象"""
    role: str  # 'user' | 'assistant'
    content: str
    content_type: str = "text"
    file_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "role": self.role,
            "content": self.content,
            "content_type": self.content_type
        }
        if self.file_id:
            result["file_id"] = self.file_id
        return result


class CozeClient:
    """Coze API 客户端"""

    def __init__(
        self,
        api_key: str,
        bot_id: str,
        base_url: str = "https://api.coze.com/open_api/v2"
    ):
        """
        初始化 Coze 客户端

        Args:
            api_key: Coze API Key
            bot_id: Bot ID
            base_url: API 基础 URL
        """
        self.api_key = api_key
        self.bot_id = bot_id
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })

    def chat(
        self,
        message: str,
        user_id: str,
        auto_save_history: bool = True,
        additional_variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        非流式对话

        Args:
            message: 用户消息
            user_id: 用户唯一标识
            auto_save_history: 是否自动保存历史
            additional_variables: 额外变量

        Returns:
            响应数据
        """
        url = f"{self.base_url}/chat"
        data = {
            "bot_id": self.bot_id,
            "user_id": user_id,
            "additional_messages": [{
                "role": "user",
                "content": message,
                "content_type": "text"
            }],
            "stream": False,
            "auto_save_history": auto_save_history
        }

        if additional_variables:
            data["additional_variables"] = additional_variables

        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            result = response.json()

            if result.get("code") != 0:
                raise Exception(f"API Error: {result.get('message')}")

            return result
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    def chat_stream(
        self,
        message: str,
        user_id: str,
        auto_save_history: bool = True,
        on_chunk: Optional[Callable[[str], None]] = None,
        on_complete: Optional[Callable[[str], None]] = None
    ) -> Generator[str, None, None]:
        """
        流式对话（生成器）

        Args:
            message: 用户消息
            user_id: 用户唯一标识
            auto_save_history: 是否自动保存历史
            on_chunk: 接收到内容块时的回调
            on_complete: 对话完成时的回调

        Yields:
            内容块
        """
        url = f"{self.base_url}/stream_run"
        data = {
            "bot_id": self.bot_id,
            "user_id": user_id,
            "additional_messages": [{
                "role": "user",
                "content": message,
                "content_type": "text"
            }],
            "stream": True,
            "auto_save_history": auto_save_history
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }

        full_content = ""
        buffer = ""

        try:
            with requests.post(url, json=data, headers=headers, stream=True) as response:
                response.raise_for_status()

                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        buffer += line_str + '\n'

                        # 处理完整的事件行
                        lines = buffer.split('\n')
                        buffer = lines.pop()  # 保留最后一个不完整的行

                        for l in lines:
                            if l.startswith('data: '):
                                try:
                                    chunk_data = json.loads(l[6:])
                                    content = chunk_data.get('content', '')

                                    if content:
                                        full_content += content
                                        if on_chunk:
                                            on_chunk(content)
                                        yield content
                                except json.JSONDecodeError:
                                    continue

            if on_complete:
                on_complete(full_content)

        except requests.RequestException as e:
            logger.error(f"Stream request failed: {e}")
            raise

    async def chat_stream_async(
        self,
        message: str,
        user_id: str,
        auto_save_history: bool = True,
        on_chunk: Optional[Callable[[str], None]] = None,
        on_complete: Optional[Callable[[str], None]] = None
    ) -> AsyncGenerator[str, None]:
        """
        流式对话（异步生成器）

        Args:
            message: 用户消息
            user_id: 用户唯一标识
            auto_save_history: 是否自动保存历史
            on_chunk: 接收到内容块时的回调
            on_complete: 对话完成时的回调

        Yields:
            内容块
        """
        url = f"{self.base_url}/stream_run"
        data = {
            "bot_id": self.bot_id,
            "user_id": user_id,
            "additional_messages": [{
                "role": "user",
                "content": message,
                "content_type": "text"
            }],
            "stream": True,
            "auto_save_history": auto_save_history
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }

        full_content = ""
        buffer = ""

        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    response.raise_for_status()

                    async for line in response.content:
                        line_str = line.decode('utf-8')
                        buffer += line_str

                        # 处理完整的事件行
                        if '\n' in buffer:
                            lines = buffer.split('\n')
                            buffer = lines.pop()  # 保留最后一个不完整的行

                            for l in lines:
                                if l.startswith('data: '):
                                    try:
                                        chunk_data = json.loads(l[6:])
                                        content = chunk_data.get('content', '')

                                        if content:
                                            full_content += content
                                            if on_chunk:
                                                on_chunk(content)
                                            yield content
                                    except json.JSONDecodeError:
                                        continue

            if on_complete:
                on_complete(full_content)

        except Exception as e:
            logger.error(f"Async stream request failed: {e}")
            raise

    def upload_file(self, file_path: str, purpose: str = "message_output") -> Dict[str, Any]:
        """
        上传文件

        Args:
            file_path: 文件路径
            purpose: 用途

        Returns:
            文件信息
        """
        url = f"{self.base_url}/files/upload"

        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'purpose': purpose}

            response = self.session.post(url, files=files, data=data)
            response.raise_for_status()
            result = response.json()

            if result.get("code") != 0:
                raise Exception(f"Upload failed: {result.get('message')}")

            return result

    def get_bot_info(self) -> Dict[str, Any]:
        """
        获取 Bot 信息

        Returns:
            Bot 信息
        """
        url = f"{self.base_url}/bot/info"
        response = self.session.get(url)
        response.raise_for_status()
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"Get bot info failed: {result.get('message')}")

        return result

    def get_conversation_history(
        self,
        conversation_id: str,
        chat_id: str
    ) -> Dict[str, Any]:
        """
        获取对话历史

        Args:
            conversation_id: 对话 ID
            chat_id: 聊天 ID

        Returns:
            对话历史
        """
        url = f"{self.base_url}/chat/retrieve"
        params = {
            "conversation_id": conversation_id,
            "chat_id": chat_id
        }

        response = self.session.get(url, params=params)
        response.raise_for_status()
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"Get history failed: {result.get('message')}")

        return result


class MagicDeskAssistant:
    """魔法课桌助手封装类"""

    def __init__(self, api_key: str, bot_id: str):
        """
        初始化助手

        Args:
            api_key: Coze API Key
            bot_id: Bot ID
        """
        self.client = CozeClient(api_key, bot_id)

    def ask(
        self,
        question: str,
        user_id: str,
        stream: bool = False
    ) -> str:
        """
        提问

        Args:
            question: 问题
            user_id: 用户 ID
            stream: 是否流式返回

        Returns:
            回答
        """
        if stream:
            # 流式响应
            full_answer = ""
            for chunk in self.client.chat_stream(question, user_id):
                print(chunk, end="", flush=True)
                full_answer += chunk
            print()
            return full_answer
        else:
            # 非流式响应
            result = self.client.chat(question, user_id)
            return result["data"]["content"]

    async def ask_async(
        self,
        question: str,
        user_id: str,
        stream: bool = False
    ) -> str:
        """
        异步提问

        Args:
            question: 问题
            user_id: 用户 ID
            stream: 是否流式返回

        Returns:
            回答
        """
        if stream:
            # 异步流式响应
            full_answer = ""
            async for chunk in self.client.chat_stream_async(question, user_id):
                print(chunk, end="", flush=True)
                full_answer += chunk
            print()
            return full_answer
        else:
            # 异步非流式响应
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.client.chat, question, user_id)
            return result["data"]["content"]

    def upload_homework(self, file_path: str, user_id: str) -> str:
        """
        上传作业

        Args:
            file_path: 文件路径
            user_id: 用户 ID

        Returns:
            文件 ID
        """
        result = self.client.upload_file(file_path)
        file_id = result["data"]["id"]
        logger.info(f"文件上传成功: {file_id}")
        return file_id


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 配置
    API_KEY = "your_coze_api_key_here"
    BOT_ID = "your_bot_id_here"
    USER_ID = "session_123"

    # 创建客户端
    assistant = MagicDeskAssistant(API_KEY, BOT_ID)

    # 示例 1: 非流式对话
    print("=" * 50)
    print("示例 1: 非流式对话")
    print("=" * 50)
    answer = assistant.ask("你好", USER_ID, stream=False)
    print(f"回答: {answer}\n")

    # 示例 2: 流式对话
    print("=" * 50)
    print("示例 2: 流式对话")
    print("=" * 50)
    answer = assistant.ask("介绍一下魔法课桌", USER_ID, stream=True)
    print(f"\n完整回答: {answer}\n")

    # 示例 3: 异步流式对话
    print("=" * 50)
    print("示例 3: 异步流式对话")
    print("=" * 50)

    async def async_example():
        answer = await assistant.ask_async("今天有哪些课程？", USER_ID, stream=True)
        print(f"\n完整回答: {answer}\n")

    asyncio.run(async_example())

    # 示例 4: 上传文件
    # print("=" * 50)
    # print("示例 4: 上传文件")
    # print("=" * 50)
    # file_id = assistant.upload_homework("homework.jpg", USER_ID)
    # print(f"文件 ID: {file_id}")

    # 示例 5: 获取 Bot 信息
    print("=" * 50)
    print("示例 5: 获取 Bot 信息")
    print("=" * 50)
    bot_info = assistant.client.get_bot_info()
    print(f"Bot 名称: {bot_info['data']['bot_name']}")
    print(f"Bot 描述: {bot_info['data']['bot_description']}\n")
