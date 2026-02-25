# 🪄 魔法课桌 - Coze API 调用指南

> **部署模式**：Coze 平台托管
> **目标用户**：前端开发者和第三方应用集成者
> **更新时间**：2025-02-24

---

## 📋 目录

- [快速开始](#快速开始)
- [获取 API 凭证](#获取-api-凭证)
- [API 接口说明](#api-接口说明)
- [认证方式](#认证方式)
- [调用示例](#调用示例)
- [错误处理](#错误处理)
- [最佳实践](#最佳实践)
- [FAQ](#faq)

---

## 🚀 快速开始

### 5 分钟快速接入

```bash
# 1. 获取 Coze API Key 和 Bot ID（见下文）

# 2. 调用流式对话接口
curl -X POST "https://api.coze.com/open_api/v2/stream_run" \
  -H "Authorization: Bearer YOUR_COZE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "bot_id": "YOUR_BOT_ID",
    "user_id": "session_123",
    "additional_messages": [
      {
        "role": "user",
        "content": "你好",
        "content_type": "text"
      }
    ],
    "stream": true
  }'
```

就这么简单！🎉

---

## 🔑 获取 API 凭证

### 步骤 1：登录 Coze 平台

访问：https://www.coze.cn/

### 步骤 2：创建或进入 Bot

1. 点击"创建 Bot"
2. 填写 Bot 信息：
   - **Bot 名称**：魔法课桌学习助手
   - **Bot 描述**：面向小学生的学习管理智能体
   - **图标**：使用 `assets/魔法书AI核.jpg`

### 步骤 3：获取 Bot ID

1. 进入 Bot 设置
2. 在 Bot 信息中找到 **Bot ID**
3. 复制保存（格式：`7381xxxx`）

### 步骤 4：获取 API Key

1. 在 Coze 平台点击"个人设置" → "API Key"
2. 点击"新建 API Key"
3. 复制 API Key（格式：`pat_xxxxxxxxxxxxxxxx`）

⚠️ **安全提示**：API Key 相当于密码，请妥善保管，不要泄露！

### 步骤 5：配置您的 Agent

在 Coze 平台的 Bot 中：

1. 上传您的 Agent 代码（已完成的魔法课桌 Agent）
2. 配置环境变量（如果需要）：
   - `DASHSCOPE_API_KEY` - 阿里云百炼 API Key
   - `JWT_SECRET` - JWT 密钥（如果使用认证）
3. 测试 Agent 功能
4. 发布 Bot

---

## 📡 API 接口说明

### 1. 流式对话接口

**接口地址**：
```
POST https://api.coze.com/open_api/v2/stream_run
```

**请求头**：
```json
{
  "Authorization": "Bearer YOUR_COZE_API_KEY",
  "Content-Type": "application/json",
  "Accept": "text/event-stream"
}
```

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `bot_id` | string | ✅ | Bot ID |
| `user_id` | string | ✅ | 用户唯一标识（建议使用 session_id） |
| `additional_messages` | array | ✅ | 对话消息列表 |
| `stream` | boolean | ❌ | 是否流式返回（默认 true） |
| `auto_save_history` | boolean | ❌ | 是否自动保存历史（默认 true） |
| `additional_variables` | object | ❌ | 额外变量 |

**消息格式**：
```json
{
  "role": "user|assistant",
  "content": "消息内容",
  "content_type": "text|image_url",
  "file_id": "文件ID（可选）"
}
```

**响应格式**（SSE 流式）：
```
event: conversation.message.delta
data: {"content":"你","index":0}

event: conversation.message.delta
data: {"content":"好","index":0}

event: conversation.message.completed
data: {"role":"assistant","content":"你好！小巫师！✨"}

event: done
data: {}
```

---

### 2. 非流式对话接口

**接口地址**：
```
POST https://api.coze.com/open_api/v2/chat
```

**请求参数**：同流式接口，但 `stream` 默认为 `false`

**响应格式**：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "conversation_id": "conv_xxx",
    "id": "msg_xxx",
    "content": "你好！小巫师！✨",
    "role": "assistant",
    "type": "answer"
  }
}
```

---

### 3. 获取 Bot 信息

**接口地址**：
```
GET https://api.coze.com/open_api/v2/bot/info
```

**请求头**：
```json
{
  "Authorization": "Bearer YOUR_COZE_API_KEY"
}
```

**响应格式**：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "bot_id": "7381xxxx",
    "bot_name": "魔法课桌学习助手",
    "bot_description": "面向小学生的学习管理智能体",
    "bot_icon": "https://...",
    "create_time": 1234567890,
    "update_time": 1234567890
  }
}
```

---

### 4. 获取对话历史

**接口地址**：
```
GET https://api.coze.com/open_api/v2/chat/retrieve
```

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `conversation_id` | string | ✅ | 对话ID |
| `chat_id` | string | ✅ | 聊天ID |

**响应格式**：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "chat_xxx",
    "conversation_id": "conv_xxx",
    "messages": [
      {
        "role": "user",
        "content": "你好",
        "content_type": "text"
      },
      {
        "role": "assistant",
        "content": "你好！小巫师！✨",
        "content_type": "text"
      }
    ]
  }
}
```

---

### 5. 上传文件

**接口地址**：
```
POST https://api.coze.com/open_api/v2/files/upload
```

**请求头**：
```json
{
  "Authorization": "Bearer YOUR_COZE_API_KEY"
}
```

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | file | ✅ | 文件对象 |
| `purpose` | string | ❌ | 用途（message_output） |

**响应格式**：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "file_xxx",
    "file_name": "homework.jpg",
    "file_size": 123456,
    "upload_time": 1234567890
  }
}
```

---

## 🔐 认证方式

### Bearer Token 认证

所有 API 请求都需要在请求头中携带 `Authorization` 字段：

```
Authorization: Bearer YOUR_COZE_API_KEY
```

**示例**：
```bash
curl -X GET "https://api.coze.com/open_api/v2/bot/info" \
  -H "Authorization: Bearer pat_xxxxxxxxxxxxxxxx"
```

---

## 💻 调用示例

### JavaScript / Node.js

#### 1. 流式对话

```javascript
const fetch = require('node-fetch');

const API_KEY = 'pat_xxxxxxxxxxxxxxxx';
const BOT_ID = '7381xxxx';

async function chatStream(message, userId) {
  const response = await fetch('https://api.coze.com/open_api/v2/stream_run', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream'
    },
    body: JSON.stringify({
      bot_id: BOT_ID,
      user_id: userId,
      additional_messages: [{
        role: 'user',
        content: message,
        content_type: 'text'
      }],
      stream: true
    })
  });

  // 处理流式响应
  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('event: conversation.message.delta')) {
        // 提取数据
        const nextLine = lines[lines.indexOf(line) + 1];
        if (nextLine && nextLine.startsWith('data: ')) {
          const data = JSON.parse(nextLine.slice(6));
          console.log(data.content);
        }
      }
    }
  }
}

// 使用示例
chatStream('你好', 'session_123');
```

#### 2. 非流式对话

```javascript
async function chat(message, userId) {
  const response = await fetch('https://api.coze.com/open_api/v2/chat', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      bot_id: BOT_ID,
      user_id: userId,
      additional_messages: [{
        role: 'user',
        content: message,
        content_type: 'text'
      }],
      stream: false
    })
  });

  const result = await response.json();
  console.log(result.data.content);
  return result;
}
```

#### 3. React 前端集成

```jsx
import React, { useState, useEffect } from 'react';

function ChatBot() {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [sessionId, setSessionId] = useState(() => {
    // 生成随机 session ID
    return 'session_' + Math.random().toString(36).substr(2, 9);
  });

  const sendMessage = async () => {
    if (!message.trim()) return;

    try {
      const response = await fetch('https://api.coze.com/open_api/v2/stream_run', {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer YOUR_COZE_API_KEY',
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream'
        },
        body: JSON.stringify({
          bot_id: 'YOUR_BOT_ID',
          user_id: sessionId,
          additional_messages: [{
            role: 'user',
            content: message,
            content_type: 'text'
          }],
          stream: true
        })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('event: conversation.message.delta')) {
            const nextLine = lines[lines.indexOf(line) + 1];
            if (nextLine && nextLine.startsWith('data: ')) {
              const data = JSON.parse(nextLine.slice(6));
              fullResponse += data.content;
              setResponse(fullResponse);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div>
      <h1>魔法课桌学习助手</h1>
      <div>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="输入你的问题..."
        />
        <button onClick={sendMessage}>发送</button>
      </div>
      <div>
        <h3>回复：</h3>
        <p>{response}</p>
      </div>
    </div>
  );
}

export default ChatBot;
```

---

### Python

```python
import requests
import json

API_KEY = 'pat_xxxxxxxxxxxxxxxx'
BOT_ID = '7381xxxx'

def chat_stream(message, user_id):
    """流式对话"""
    url = 'https://api.coze.com/open_api/v2/stream_run'
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream'
    }
    data = {
        'bot_id': BOT_ID,
        'user_id': user_id,
        'additional_messages': [{
            'role': 'user',
            'content': message,
            'content_type': 'text'
        }],
        'stream': True
    }

    response = requests.post(url, headers=headers, json=data, stream=True)

    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                try:
                    data = json.loads(line_str[6:])
                    print(data.get('content', ''), end='', flush=True)
                except:
                    pass

def chat(message, user_id):
    """非流式对话"""
    url = 'https://api.coze.com/open_api/v2/chat'
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'bot_id': BOT_ID,
        'user_id': user_id,
        'additional_messages': [{
            'role': 'user',
            'content': message,
            'content_type': 'text'
        }],
        'stream': False
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    return result['data']['content']

# 使用示例
if __name__ == '__main__':
    print('流式对话：')
    chat_stream('你好', 'session_123')
    print('\n')

    print('非流式对话：')
    response = chat('你好', 'session_123')
    print(response)
```

---

### cURL

```bash
# 流式对话
curl -X POST "https://api.coze.com/open_api/v2/stream_run" \
  -H "Authorization: Bearer pat_xxxxxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "bot_id": "7381xxxx",
    "user_id": "session_123",
    "additional_messages": [
      {
        "role": "user",
        "content": "你好",
        "content_type": "text"
      }
    ],
    "stream": true
  }'

# 非流式对话
curl -X POST "https://api.coze.com/open_api/v2/chat" \
  -H "Authorization: Bearer pat_xxxxxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "bot_id": "7381xxxx",
    "user_id": "session_123",
    "additional_messages": [
      {
        "role": "user",
        "content": "你好",
        "content_type": "text"
      }
    ],
    "stream": false
  }'

# 获取 Bot 信息
curl -X GET "https://api.coze.com/open_api/v2/bot/info" \
  -H "Authorization: Bearer pat_xxxxxxxxxxxxxxxx"
```

---

## ⚠️ 错误处理

### 常见错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|---------|
| `0` | 成功 | - |
| `4001` | API Key 无效 | 检查 API Key 是否正确 |
| `4002` | Bot ID 无效 | 检查 Bot ID 是否正确 |
| `4003` | 参数错误 | 检查请求参数格式 |
| `4004` | 频率限制 | 降低请求频率 |
| `4005` | Bot 未发布 | 先在 Coze 平台发布 Bot |
| `5000` | 服务器错误 | 稍后重试 |
| `5001` | 超时 | 增加超时时间 |

### 错误响应格式

```json
{
  "code": 4001,
  "message": "Invalid API Key",
  "data": null
}
```

### 错误处理示例（JavaScript）

```javascript
async function chatWithErrorHandling(message, userId) {
  try {
    const response = await fetch('https://api.coze.com/open_api/v2/chat', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        bot_id: BOT_ID,
        user_id: userId,
        additional_messages: [{
          role: 'user',
          content: message,
          content_type: 'text'
        }]
      })
    });

    const result = await response.json();

    if (result.code !== 0) {
      // 处理错误
      switch (result.code) {
        case 4001:
          console.error('API Key 无效，请检查配置');
          break;
        case 4002:
          console.error('Bot ID 无效，请检查配置');
          break;
        case 4004:
          console.error('请求频率过高，请稍后重试');
          break;
        default:
          console.error('未知错误:', result.message);
      }
      return null;
    }

    return result.data.content;
  } catch (error) {
    console.error('网络错误:', error);
    return null;
  }
}
```

---

## 💡 最佳实践

### 1. Session ID 管理

```javascript
// 为每个用户生成唯一的 Session ID
function generateSessionId() {
  return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// 将 Session ID 存储在 localStorage 中
function getSessionId() {
  let sessionId = localStorage.getItem('coze_session_id');
  if (!sessionId) {
    sessionId = generateSessionId();
    localStorage.setItem('coze_session_id', sessionId);
  }
  return sessionId;
}
```

### 2. 防止重复请求

```javascript
let isProcessing = false;

async function sendMessage(message) {
  if (isProcessing) {
    console.warn('正在处理中，请稍候...');
    return;
  }

  isProcessing = true;
  try {
    // 发送请求...
  } finally {
    isProcessing = false;
  }
}
```

### 3. 超时处理

```javascript
function chatWithTimeout(message, userId, timeout = 30000) {
  return Promise.race([
    chat(message, userId),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('请求超时')), timeout)
    )
  ]);
}
```

### 4. 重试机制

```javascript
async function chatWithRetry(message, userId, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await chat(message, userId);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      console.log(`重试 ${i + 1}/${maxRetries}...`);
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
}
```

### 5. 流式响应优化

```javascript
function optimizeStreamResponse(reader, onUpdate) {
  const decoder = new TextDecoder();
  let buffer = '';

  return new Promise((resolve) => {
    async function read() {
      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          resolve();
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop(); // 保留最后一个不完整的行

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              onUpdate(data);
            } catch (e) {
              // 忽略解析错误
            }
          }
        }
      }
    }
    read();
  });
}
```

### 6. API Key 安全

```javascript
// ❌ 错误：在前端代码中暴露 API Key
const API_KEY = 'pat_xxxxxxxxxxxxxxxx';

// ✅ 正确：从环境变量或后端获取
const API_KEY = process.env.REACT_APP_COZE_API_KEY;

// ✅ 更好：通过后端代理，不直接暴露 API Key
async function chatViaBackend(message) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  return response.json();
}
```

---

## 📚 FAQ

### Q1: 如何获取 Bot ID？

**A**：
1. 登录 Coze 平台
2. 进入您的 Bot
3. 在 Bot 设置页面可以找到 Bot ID

### Q2: API Key 如何管理？

**A**：
- 前端应用：建议通过后端代理，不直接暴露 API Key
- 后端应用：将 API Key 存储在环境变量中
- 生产环境：定期轮换 API Key

### Q3: 如何限制访问频率？

**A**：
- Coze 平台有内置的频率限制
- 在您的应用中实现请求限流
- 使用缓存减少重复请求

### Q4: 如何处理多用户？

**A**：
- 使用不同的 `user_id` 区分用户
- 建议格式：`user_{用户唯一标识}`
- 示例：`user_123456`, `user_xiaoming`

### Q5: 流式响应和非流式响应有什么区别？

**A**：
| 特性 | 流式 | 非流式 |
|------|------|--------|
| 响应速度 | 逐字符显示 | 一次性返回 |
| 用户体验 | 更流畅 | 稍有延迟 |
| 适用场景 | 对话界面 | 后台任务 |

### Q6: 如何上传文件？

**A**：
```javascript
// 1. 先上传文件
const fileInput = document.getElementById('file-input');
const file = fileInput.files[0];

const formData = new FormData();
formData.append('file', file);

const uploadResponse = await fetch('https://api.coze.com/open_api/v2/files/upload', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${API_KEY}`
  },
  body: formData
});

const uploadResult = await uploadResponse.json();
const fileId = uploadResult.data.id;

// 2. 在对话中引用文件
const chatResponse = await fetch('https://api.coze.com/open_api/v2/chat', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    bot_id: BOT_ID,
    user_id: sessionId,
    additional_messages: [{
      role: 'user',
      content: '请帮我分析这个作业',
      content_type: 'text',
      file_id: fileId
    }]
  })
});
```

### Q7: 如何保存对话历史？

**A**：
- Coze 平台会自动保存对话历史（如果 `auto_save_history=true`）
- 可以通过 API 获取历史对话
- 建议在前端也保存一份，便于快速加载

### Q8: 费用如何计算？

**A**：
- 具体费用请参考 Coze 平台的定价页面
- 通常按 Token 使用量计费
- 流式响应和非流式响应费用相同

---

## 📞 技术支持

- **Coze 官方文档**: https://www.coze.cn/docs/
- **Coze API 文档**: https://www.coze.cn/docs/developer_guides/chat
- **Coze 社区**: https://www.coze.cn/community
- **项目文档**: `/workspace/projects/docs/`

---

## 📖 相关文档

- [Agent 技术实现详解](AGENT_TECHNICAL_SPECIFICATION.md)
- [后端开发计划](BACKEND_DEVELOPMENT_PLAN.md)
- [部署指南](DEPLOYMENT_GUIDE_COMPLETE.md)
- [API 完整文档](API_DOCUMENTATION.md)

---

**最后更新**: 2025-02-24
**版本**: 1.0.0
**维护者**: Coze Coding
