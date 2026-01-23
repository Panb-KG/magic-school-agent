# 前端调用智能体API示例代码

## 📋 概述

本文档提供完整的前端代码示例，展示如何连接和调用后端智能体API。

---

## 1. 创建聊天服务模块

**文件**: `src/services/chatService.ts`

```typescript
import request from '@/utils/request';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

export interface ChatRequest {
  query: string;
  session_id?: string;
  user_id?: string;
  user_role?: string;
}

export interface ChatResponse {
  message: string;
  session_id: string;
  tools_used?: string[];
  time_cost_ms?: number;
}

/**
 * 发送消息到智能体（非流式）
 */
export const sendMessageToAgent = async (
  query: string,
  sessionId: string,
  userId?: string,
  userRole?: string
): Promise<ChatResponse> => {
  try {
    // 注意：这里使用的是真实后端地址，不是 Mock API
    // 在生产环境中，应该通过环境变量配置
    const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000';
    
    const token = localStorage.getItem('token');
    
    const response = await fetch(`${backendUrl}/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        query,
        session_id: sessionId,
        user_id: userId,
        user_role: userRole
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    // 处理响应数据
    return {
      message: data.output || data.message || '抱歉，我无法回答这个问题。',
      session_id: data.session_id || sessionId,
      tools_used: data.tools_used,
      time_cost_ms: data.time_cost_ms
    };
  } catch (error) {
    console.error('发送消息失败:', error);
    throw error;
  }
};

/**
 * 发送消息到智能体（流式）
 */
export const streamMessageToAgent = async (
  query: string,
  sessionId: string,
  userId?: string,
  userRole?: string,
  onChunk?: (chunk: string) => void,
  onComplete?: (fullResponse: string) => void,
  onError?: (error: Error) => void
): Promise<string> => {
  try {
    const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000';
    const token = localStorage.getItem('token');
    
    const response = await fetch(`${backendUrl}/stream_run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        query,
        session_id: sessionId,
        user_id: userId,
        user_role: userRole
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('Response body is not readable');
    }

    const decoder = new TextDecoder();
    let fullResponse = '';

    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        onComplete?.(fullResponse);
        break;
      }

      // 解码数据
      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split('\n').filter(line => line.trim());
      
      for (const line of lines) {
        // SSE 格式: event: message\ndata: {...}\n\n
        if (line.startsWith('data: ')) {
          try {
            const jsonStr = line.replace('data: ', '');
            const data = JSON.parse(jsonStr);
            
            // 提取消息内容
            if (data.content) {
              const content = data.content;
              fullResponse += content;
              onChunk?.(content);
            }
          } catch (e) {
            console.warn('解析 SSE 数据失败:', e, line);
          }
        }
      }
    }

    return fullResponse;
  } catch (error) {
    console.error('流式发送消息失败:', error);
    onError?.(error as Error);
    throw error;
  }
};

/**
 * 生成会话 ID
 */
export const generateSessionId = (): string => {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};
```

---

## 2. 创建聊天组件

**文件**: `src/components/Chat/index.tsx`

```typescript
import React, { useState, useRef, useEffect } from 'react';
import { Card, Input, Button, message, Spin } from 'antd';
import { SendOutlined, RobotOutlined, UserOutlined } from '@ant-design/icons';
import { 
  sendMessageToAgent, 
  streamMessageToAgent, 
  generateSessionId,
  type ChatMessage 
} from '@/services/chatService';
import { authStorage } from '@/contexts/AuthContext';
import './Chat.css';

const { TextArea } = Input;

interface ChatProps {
  className?: string;
  defaultSessionId?: string;
}

const Chat: React.FC<ChatProps> = ({ className, defaultSessionId }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState<string>(defaultSessionId || generateSessionId());
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 发送消息
  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) {
      return;
    }

    const userMessage: ChatMessage = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toISOString()
    };

    // 添加用户消息
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // 获取用户信息
      const user = authStorage.getUser();
      
      // 创建助手消息占位符
      const assistantMessage: ChatMessage = {
        id: `msg_${Date.now() + 1}`,
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);

      // 使用流式响应
      await streamMessageToAgent(
        userMessage.content,
        sessionId,
        user?.id,
        user?.role,
        // onChunk: 收到新内容时更新
        (chunk: string) => {
          setMessages(prev => 
            prev.map(msg => 
              msg.id === assistantMessage.id 
                ? { ...msg, content: msg.content + chunk }
                : msg
            )
          );
        },
        // onComplete: 完成时的回调
        (fullResponse: string) => {
          message.success('回复完成');
        },
        // onError: 错误处理
        (error: Error) => {
          setMessages(prev => 
            prev.map(msg => 
              msg.id === assistantMessage.id 
                ? { ...msg, content: '抱歉，发生了错误，请稍后重试。' }
                : msg
            )
          );
          message.error(`错误: ${error.message}`);
        }
      );

    } catch (error) {
      console.error('发送消息失败:', error);
      message.error('发送消息失败，请稍后重试');
    } finally {
      setIsLoading(false);
    }
  };

  // 按回车发送
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Card 
      title={
        <div className="chat-header">
          <RobotOutlined />
          <span>魔法课桌助手</span>
        </div>
      }
      className={`chat-container ${className}`}
    >
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-welcome">
            <RobotOutlined style={{ fontSize: 48, color: '#1890ff' }} />
            <p>你好！我是魔法课桌助手，有什么可以帮助你的吗？</p>
          </div>
        )}
        
        {messages.map((msg) => (
          <div 
            key={msg.id} 
            className={`chat-message ${msg.role === 'user' ? 'user' : 'assistant'}`}
          >
            <div className="chat-avatar">
              {msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
            </div>
            <div className="chat-content">
              <div className="chat-text">
                {msg.content}
                {isLoading && msg.role === 'assistant' && !msg.content && (
                  <Spin size="small" />
                )}
              </div>
              <div className="chat-time">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <TextArea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="输入你的问题..."
          autoSize={{ minRows: 1, maxRows: 4 }}
          disabled={isLoading}
        />
        <Button 
          type="primary" 
          icon={<SendOutlined />}
          onClick={handleSendMessage}
          disabled={isLoading || !inputValue.trim()}
          loading={isLoading}
        >
          发送
        </Button>
      </div>
    </Card>
  );
};

export default Chat;
```

---

## 3. 创建样式文件

**文件**: `src/components/Chat/Chat.css`

```css
.chat-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 500;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background-color: #f5f5f5;
  border-radius: 8px;
  margin-bottom: 16px;
}

.chat-welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
  text-align: center;
}

.chat-message {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  animation: fadeIn 0.3s ease;
}

.chat-message.user {
  flex-direction: row-reverse;
}

.chat-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.chat-message.user .chat-avatar {
  background-color: #1890ff;
  color: white;
}

.chat-message.assistant .chat-avatar {
  background-color: #52c41a;
  color: white;
}

.chat-content {
  max-width: 70%;
}

.chat-message.user .chat-content {
  align-items: flex-end;
}

.chat-text {
  background: white;
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  line-height: 1.6;
  word-wrap: break-word;
}

.chat-message.user .chat-text {
  background: #1890ff;
  color: white;
}

.chat-time {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  text-align: right;
}

.chat-input {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.chat-input .ant-input {
  flex: 1;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 移动端适配 */
@media (max-width: 768px) {
  .chat-content {
    max-width: 85%;
  }

  .chat-text {
    padding: 10px 12px;
    font-size: 14px;
  }
}
```

---

## 4. 在页面中使用

**示例**: 在仪表盘页面中使用聊天组件

```typescript
// src/pages/Dashboard/Dashboard.tsx
import React from 'react';
import { Layout, Row, Col } from 'antd';
import Chat from '@/components/Chat';

const Dashboard: React.FC = () => {
  return (
    <Layout style={{ padding: '24px', minHeight: '100vh' }}>
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          {/* 其他仪表盘内容 */}
        </Col>
        
        <Col xs={24} lg={12}>
          <Chat 
            defaultSessionId="dashboard_session"
            style={{ height: '600px' }}
          />
        </Col>
      </Row>
    </Layout>
  );
};

export default Dashboard;
```

---

## 5. 环境变量配置

**文件**: `.env.development`

```env
# Mock API 地址（用于前端开发）
VITE_API_BASE_URL=http://localhost:3000/api/v1

# 真实后端地址（用于智能体对话）
VITE_BACKEND_URL=http://localhost:5000

# WebSocket 地址
VITE_WS_URL=ws://localhost:8765
```

**文件**: `.env.production`

```env
# 生产环境配置
VITE_API_BASE_URL=https://your-domain.com/api
VITE_BACKEND_URL=https://your-domain.com/backend
VITE_WS_URL=wss://your-domain.com/ws
```

---

## 6. 完整的聊天页面示例

**文件**: `src/pages/ChatPage/ChatPage.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import { Layout, Typography } from 'antd';
import { authStorage } from '@/contexts/AuthContext';
import Chat from '@/components/Chat';
import './ChatPage.css';

const { Header, Content } = Layout;
const { Title } = Typography;

const ChatPage: React.FC = () => {
  const [sessionId, setSessionId] = useState<string>('');

  useEffect(() => {
    // 生成或恢复会话 ID
    const savedSessionId = sessionStorage.getItem('chat_session_id');
    if (savedSessionId) {
      setSessionId(savedSessionId);
    } else {
      const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      setSessionId(newSessionId);
      sessionStorage.setItem('chat_session_id', newSessionId);
    }
  }, []);

  const user = authStorage.getUser();

  return (
    <Layout className="chat-page">
      <Header className="chat-header">
        <div className="header-content">
          <Title level={3}>魔法课桌助手</Title>
          <span className="user-info">
            {user?.role === 'student' ? '学生模式' : '家长模式'}
          </span>
        </div>
      </Header>
      
      <Content className="chat-content">
        <Chat 
          defaultSessionId={sessionId}
          style={{ height: '100%' }}
        />
      </Content>
    </Layout>
  );
};

export default ChatPage;
```

---

## 7. 使用说明

### 开发环境（使用 Mock 数据）

当前前端连接的是 Mock API 服务器，智能体对话功能需要：

1. **启动后端服务**:
```bash
# 启动智能体 API
bash /workspace/projects/scripts/http_run.sh -p 5000

# 启动 WebSocket 服务
python3 /workspace/projects/src/websocket_server.py
```

2. **配置环境变量**:
```bash
# 在 .env.development 中设置
VITE_BACKEND_URL=http://localhost:5000
```

3. **重启前端开发服务器**:
```bash
npm run dev
```

### 生产环境

1. 修改 `.env.production` 文件，配置真实的后端地址
2. 构建前端应用:
```bash
npm run build
```
3. 部署到服务器

---

## 8. 功能特性

- ✅ 支持流式响应（实时显示回复）
- ✅ 会话管理（保持对话上下文）
- ✅ 用户身份识别（学生/家长模式）
- ✅ 自动滚动到底部
- ✅ 加载状态显示
- ✅ 错误处理和提示
- ✅ 响应式设计（适配移动端）
- ✅ 回车发送消息
- ✅ Markdown 渲染（可选扩展）

---

## 9. 后续优化建议

1. **添加 Markdown 支持**:
```bash
npm install react-markdown
```

2. **添加代码高亮**:
```bash
npm install react-syntax-highlighter
```

3. **添加语音输入**:
```bash
npm install speech-recognition-polyfill
```

4. **添加消息持久化**（保存到后端数据库）
5. **添加文件上传功能**
6. **添加历史记录搜索**

---

## 10. 调试技巧

### 查看网络请求

打开浏览器开发者工具 -> Network 标签，查看：
- 请求 URL
- 请求头（特别是 Authorization）
- 响应内容
- 响应时间

### 查看控制台日志

```typescript
// 在 chatService.ts 中添加调试日志
console.log('发送消息:', { query, sessionId, userId, userRole });
console.log('收到响应:', response);
```

### 使用 Mock 数据测试

在后端服务未启动时，可以先使用 Mock 数据测试前端 UI：

```typescript
// 临时 Mock 数据
const mockResponse = {
  message: '这是模拟的回复。',
  session_id: sessionId
};

setMessages(prev => [...prev, {
  id: `msg_${Date.now()}`,
  role: 'assistant',
  content: mockResponse.message,
  timestamp: new Date().toISOString()
}]);
```

---

## 📚 相关文档

- [前端连接后端API指南](./前端连接后端API指南.md)
- [前端调试指南](./前端调试指南.md)
- [API 接口文档](http://localhost:5000/docs)
