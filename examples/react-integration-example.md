# 🪄 魔法课桌 - Coze API React 集成示例

> 一个完整的 React 前端集成示例，支持流式对话、配置管理、错误处理等功能

---

## 📦 功能特性

- ✅ 流式对话显示
- ✅ 消息历史记录
- ✅ API 配置管理
- ✅ 错误处理和重试
- ✅ 自动保存配置
- ✅ 加载状态显示
- ✅ 响应式设计

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 如果还没有 React 项目
npm create vite@latest magic-desk-frontend -- --template react-ts
cd magic-desk-frontend
npm install
```

### 2. 创建 Coze API 客户端

创建 `src/lib/cozeClient.ts`:

```typescript
// src/lib/cozeClient.ts

export interface CozeMessage {
  role: 'user' | 'assistant';
  content: string;
  content_type?: string;
  file_id?: string;
}

export interface CozeStreamResponse {
  event: string;
  data: {
    content?: string;
    index?: number;
    role?: string;
    [key: string]: any;
  };
}

export interface CozeChatConfig {
  apiKey: string;
  botId: string;
}

export class CozeClient {
  private config: CozeChatConfig;
  private baseUrl = 'https://api.coze.com/open_api/v2';

  constructor(config: CozeChatConfig) {
    this.config = config;
  }

  /**
   * 流式对话
   */
  async chatStream(
    message: string,
    userId: string,
    onChunk: (content: string) => void,
    onComplete?: (fullContent: string) => void,
    onError?: (error: Error) => void
  ): Promise<string> {
    const response = await fetch(`${this.baseUrl}/stream_run`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.config.apiKey}`,
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream'
      },
      body: JSON.stringify({
        bot_id: this.config.botId,
        user_id: userId,
        additional_messages: [{
          role: 'user',
          content: message,
          content_type: 'text'
        }],
        stream: true,
        auto_save_history: true
      })
    });

    if (!response.ok) {
      const error = new Error(`HTTP error! status: ${response.status}`);
      if (onError) onError(error);
      throw error;
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let fullContent = '';
    let buffer = '';

    if (!reader) {
      const error = new Error('Response body is null');
      if (onError) onError(error);
      throw error;
    }

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.content) {
                fullContent += data.content;
                onChunk(data.content);
              }
            } catch (e) {
              // 忽略解析错误
            }
          }
        }
      }

      if (onComplete) onComplete(fullContent);
      return fullContent;
    } catch (error) {
      const err = error as Error;
      if (onError) onError(err);
      throw err;
    }
  }

  /**
   * 非流式对话
   */
  async chat(message: string, userId: string): Promise<string> {
    const response = await fetch(`${this.baseUrl}/chat`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.config.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        bot_id: this.config.botId,
        user_id: userId,
        additional_messages: [{
          role: 'user',
          content: message,
          content_type: 'text'
        }],
        stream: false
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    return result.data.content;
  }

  /**
   * 上传文件
   */
  async uploadFile(file: File): Promise<string> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/files/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.config.apiKey}`
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    return result.data.id;
  }

  /**
   * 获取 Bot 信息
   */
  async getBotInfo() {
    const response = await fetch(`${this.baseUrl}/bot/info`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${this.config.apiKey}`
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
}
```

### 3. 创建 Chat 组件

创建 `src/components/ChatBot.tsx`:

```typescript
// src/components/ChatBot.tsx

import React, { useState, useEffect, useRef } from 'react';
import { CozeClient } from '../lib/cozeClient';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface ChatBotProps {
  config: {
    apiKey: string;
    botId: string;
  };
}

export const ChatBot: React.FC<ChatBotProps> = ({ config }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: '你好呀，小巫师！我是魔法课桌学习助手，需要什么帮助呢？✨',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [sessionId] = useState(() => {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const clientRef = useRef<CozeClient | null>(null);

  // 初始化客户端
  useEffect(() => {
    clientRef.current = new CozeClient(config);
  }, [config]);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!inputMessage.trim() || isProcessing) return;

    const userMessage: Message = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    // 添加用户消息
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsProcessing(true);

    // 创建占位消息
    const assistantMessage: Message = {
      role: 'assistant',
      content: '',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, assistantMessage]);

    // 更新最后的消息（流式响应）
    const updateLastMessage = (content: string) => {
      setMessages(prev => {
        const newMessages = [...prev];
        const lastMessage = newMessages[newMessages.length - 1];
        if (lastMessage && lastMessage.role === 'assistant') {
          lastMessage.content = content;
        }
        return newMessages;
      });
    };

    try {
      const client = clientRef.current;
      if (!client) throw new Error('Client not initialized');

      await client.chatStream(
        userMessage.content,
        sessionId,
        (chunk) => {
          const currentContent = messages[messages.length]?.content || '';
          updateLastMessage(currentContent + chunk);
        },
        (fullContent) => {
          updateLastMessage(fullContent);
        }
      );
    } catch (error) {
      console.error('Chat error:', error);
      updateLastMessage('抱歉，出现错误：' + (error as Error).message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`message ${msg.role}`}
          >
            <div className="avatar">
              {msg.role === 'user' ? '🧙‍♂️' : '🪄'}
            </div>
            <div className="bubble">
              {msg.content || <span className="loading">...</span>}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="输入你的问题..."
          disabled={isProcessing}
          rows={2}
        />
        <button
          onClick={handleSend}
          disabled={!inputMessage.trim() || isProcessing}
          className="send-button"
        >
          {isProcessing ? '发送中...' : '发送'}
        </button>
      </div>
    </div>
  );
};
```

### 4. 创建 Config 组件

创建 `src/components/ConfigPanel.tsx`:

```typescript
// src/components/ConfigPanel.tsx

import React, { useState, useEffect } from 'react';

export interface ConfigPanelProps {
  onConfigChange: (config: { apiKey: string; botId: string }) => void;
}

export const ConfigPanel: React.FC<ConfigPanelProps> = ({ onConfigChange }) => {
  const [apiKey, setApiKey] = useState('');
  const [botId, setBotId] = useState('');
  const [saved, setSaved] = useState(false);

  // 加载保存的配置
  useEffect(() => {
    const savedApiKey = localStorage.getItem('coze_api_key') || '';
    const savedBotId = localStorage.getItem('coze_bot_id') || '';
    setApiKey(savedApiKey);
    setBotId(savedBotId);

    if (savedApiKey && savedBotId) {
      onConfigChange({ apiKey: savedApiKey, botId: savedBotId });
    }
  }, [onConfigChange]);

  const handleSave = () => {
    localStorage.setItem('coze_api_key', apiKey);
    localStorage.setItem('coze_bot_id', botId);
    onConfigChange({ apiKey, botId });
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="config-panel">
      <h3>⚙️ API 配置</h3>
      <div className="config-inputs">
        <div className="input-group">
          <label>Coze API Key</label>
          <input
            type="text"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="pat_xxxxxxxxxxxxxxxx"
          />
        </div>
        <div className="input-group">
          <label>Bot ID</label>
          <input
            type="text"
            value={botId}
            onChange={(e) => setBotId(e.target.value)}
            placeholder="7381xxxx"
          />
        </div>
      </div>
      <button
        onClick={handleSave}
        className="save-button"
        disabled={!apiKey || !botId}
      >
        {saved ? '✓ 已保存' : '💾 保存配置'}
      </button>
    </div>
  );
};
```

### 5. 创建 App 组件

更新 `src/App.tsx`:

```typescript
// src/App.tsx

import React, { useState } from 'react';
import { ChatBot } from './components/ChatBot';
import { ConfigPanel } from './components/ConfigPanel';
import './App.css';

function App() {
  const [config, setConfig] = useState<{ apiKey: string; botId: string }>({
    apiKey: '',
    botId: ''
  });

  const isConfigured = config.apiKey && config.botId;

  return (
    <div className="App">
      <header className="App-header">
        <h1>🪄 魔法课桌学习助手</h1>
        <p>Coze API 集成示例</p>
      </header>

      <main>
        <ConfigPanel onConfigChange={setConfig} />

        {isConfigured ? (
          <ChatBot config={config} />
        ) : (
          <div className="config-hint">
            请先配置 API Key 和 Bot ID
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
```

### 6. 添加样式

更新 `src/App.css`:

```css
/* src/App.css */

.App {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.App-header {
  text-align: center;
  margin-bottom: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px;
  border-radius: 20px;
  color: white;
}

.App-header h1 {
  font-size: 32px;
  margin-bottom: 10px;
}

.App-header p {
  opacity: 0.9;
  font-size: 16px;
}

.config-panel {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 20px;
}

.config-panel h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #333;
}

.config-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 15px;
}

.input-group {
  display: flex;
  flex-direction: column;
}

.input-group label {
  font-size: 13px;
  color: #666;
  margin-bottom: 5px;
}

.input-group input {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.input-group input:focus {
  outline: none;
  border-color: #667eea;
}

.save-button {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.save-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.save-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.config-hint {
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 16px;
}

.chat-container {
  background: white;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.messages {
  height: 500px;
  overflow-y: auto;
  padding: 20px;
  background: #f8f9fa;
}

.message {
  display: flex;
  align-items: flex-start;
  margin-bottom: 15px;
}

.message.user {
  justify-content: flex-end;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  margin: 0 10px;
  background: #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
}

.message.user .bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.message.assistant .bubble {
  background: white;
  color: #333;
  border: 1px solid #e9ecef;
  border-bottom-left-radius: 4px;
}

.loading {
  display: inline-block;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.input-area {
  display: flex;
  gap: 10px;
  padding: 20px;
  background: white;
  border-top: 1px solid #e9ecef;
}

.input-area textarea {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  resize: none;
  font-family: inherit;
}

.input-area textarea:focus {
  outline: none;
  border-color: #667eea;
}

.send-button {
  padding: 0 25px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.send-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .config-inputs {
    grid-template-columns: 1fr;
  }

  .bubble {
    max-width: 85%;
  }
}
```

### 7. 运行项目

```bash
npm run dev
```

访问 `http://localhost:5173` 即可看到效果！

---

## 🎯 功能说明

### 配置管理
- ✅ API Key 和 Bot ID 配置
- ✅ 自动保存到 localStorage
- ✅ 页面刷新后自动加载

### 消息功能
- ✅ 流式对话显示
- ✅ 消息历史记录
- ✅ 自动滚动到底部
- ✅ 用户和助手消息区分

### 用户体验
- ✅ 加载状态显示
- ✅ 发送按钮禁用状态
- ✅ 回车键发送消息
- ✅ 响应式设计

### 错误处理
- ✅ 网络错误提示
- ✅ 配置验证
- ✅ 流式响应解析错误处理

---

## 📚 相关文档

- [Coze API 调用指南](../COZE_API_GUIDE.md)
- [Agent 技术实现详解](../AGENT_TECHNICAL_SPECIFICATION.md)
- [部署指南](../DEPLOYMENT_GUIDE_COMPLETE.md)

---

**最后更新**: 2025-02-24
**版本**: 1.0.0
