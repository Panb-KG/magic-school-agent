# 前端连接后端智能体API指南

## 📋 目录

1. [架构概述](#架构概述)
2. [连接方式](#连接方式)
3. [环境配置](#环境配置)
4. [API调用示例](#api调用示例)
5. [WebSocket连接](#websocket连接)
6. [完整流程](#完整流程)
7. [常见问题](#常见问题)

---

## 🏗️ 架构概述

### 系统架构

```
┌─────────────────┐
│   前端 (React)  │
│  Port: 5173     │
└────────┬────────┘
         │
         ├─ HTTP API (axios)
         │  └─ http://localhost:3000/api/v1/*
         │
         └─ WebSocket (socket.io-client)
            └─ ws://localhost:8765
                    │
┌───────────────────┼──────────────────┐
│                  │                  │
┌─────────────┐   │  ┌────────────┐   │  ┌──────────────┐
│ Mock API    │   │  │ 多用户 API │   │  │ 智能体 API   │
│ Server      │   │  │ Server     │   │  │ Server       │
│ Port: 3000  │   │  │ Port: 待定 │   │  │ Port: 待定   │
└─────────────┘   │  └────────────┘   │  └──────────────┘
                  │  (认证/家长)       │  (Agent对话)
                  │                     │
                  │                     │
                  │              ┌──────┴────────┐
                  │              │  LangGraph    │
                  │              │  Agent        │
                  │              └───────────────┘
```

### 组件说明

1. **前端** (React + Vite)
   - 端口: 5173
   - HTTP 请求: Axios
   - 实时通信: Socket.IO Client

2. **Mock API 服务器**
   - 端口: 3000
   - 作用: 提供模拟数据用于前端开发调试

3. **多用户 API 服务器**
   - 作用: 用户认证、家长管理、数据查询
   - 文件: `src/api/multiuser_api.py`

4. **智能体 API 服务器**
   - 作用: 流式对话、智能回复
   - 端口: 5000 (由 `src/main.py` 提供)
   - 路由: `/run`, `/stream_run`

---

## 🔗 连接方式

### 1. HTTP API 连接

#### 请求配置

**位置**: `magic-school-frontend/src/utils/request.ts`

```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api/v1';

const request = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器：自动添加 JWT token
request.interceptors.request.use(
  (config) => {
    const token = authStorage.getToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器：处理 401 错误
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      // 清除认证信息并跳转登录
      authStorage.removeToken();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

#### 环境变量

**文件**: `magic-school-frontend/.env` 或 `magic-school-frontend/.env.development`

```env
# Mock API 地址（用于前端开发）
VITE_API_BASE_URL=http://localhost:3000/api/v1

# 真实后端 API 地址（生产环境）
VITE_API_BASE_URL=http://your-backend-server:5000/api

# WebSocket 地址
VITE_WS_URL=ws://localhost:8765
```

#### Vite 代理配置

**文件**: `magic-school-frontend/vite.config.ts`

```typescript
export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:3000',  // Mock API
        changeOrigin: true
      },
      '/ws': {
        target: 'ws://localhost:8765',  // WebSocket
        ws: true,
        changeOrigin: true
      }
    }
  }
});
```

### 2. WebSocket 连接

#### WebSocket Hook

**位置**: `magic-school-frontend/src/hooks/useWebSocket.ts`

```typescript
import { io, Socket } from 'socket.io-client';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8765';

export const useWebSocket = (options: UseWebSocketOptions = {}) => {
  const { autoConnect = true, onMessage, onError } = options;
  
  const connect = () => {
    const socket = io(WS_URL, {
      transports: ['websocket'],
      autoConnect: false,
    });

    socket.on('connect', () => {
      console.log('WebSocket connected');
    });

    socket.on('message', (data) => {
      onMessage?.(data);
    });

    socket.connect();
  };

  return { connect, send, disconnect };
};
```

---

## 🛠️ 环境配置

### 开发环境（使用 Mock API）

1. **启动 Mock API 服务器**
```bash
cd /workspace/projects
python3 scripts/mock_api_server.py
```

2. **启动前端开发服务器**
```bash
cd /workspace/projects/magic-school-frontend
npm run dev
```

3. **访问应用**
```
http://localhost:5173
```

### 生产环境（连接真实后端）

1. **启动多用户 API 服务器**
```bash
cd /workspace/projects
python3 src/api/multiuser_api.py
```

2. **启动智能体 API 服务器**
```bash
cd /workspace/projects
bash /workspace/projects/scripts/http_run.sh -p 5000
```

3. **启动 WebSocket 服务器**
```bash
cd /workspace/projects
python3 src/websocket_server.py
```

4. **配置前端环境变量**
```bash
# .env.production
VITE_API_BASE_URL=http://localhost:5000/api
VITE_WS_URL=ws://localhost:8765
```

5. **启动前端**
```bash
npm run build
npm run preview
```

---

## 📡 API 调用示例

### 1. 认证 API

#### 登录

```typescript
import request from '@/utils/request';

interface LoginRequest {
  username: string;
  password: string;
}

interface LoginResponse {
  success: boolean;
  data: {
    access_token: string;
    token_type: string;
    expires_in: number;
    user: any;
  };
}

export const login = async (data: LoginRequest): Promise<LoginResponse> => {
  return request.post('/auth/login', data);
};

// 使用示例
const result = await login({
  username: 'student',
  password: 'password123'
});

// 存储 token
authStorage.setToken(result.data.access_token);
authStorage.setUser(result.data.user);
```

#### 注册

```typescript
interface RegisterRequest {
  username: string;
  password: string;
  role: 'student' | 'parent';
  student_name?: string;
  grade?: string;
}

export const register = async (data: RegisterRequest) => {
  return request.post('/auth/register', data);
};
```

### 2. 智能体对话 API

#### 流式对话（SSE）

```typescript
export const chatWithAgent = async (message: string, sessionId: string) => {
  const token = authStorage.getToken();
  
  const response = await fetch('http://localhost:5000/stream_run', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      query: message,
      session_id: sessionId
    })
  });

  // 处理 SSE 流式响应
  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n').filter(line => line.startsWith('data: '));
    
    for (const line of lines) {
      const data = JSON.parse(line.replace('data: ', ''));
      console.log('收到消息:', data);
      
      // 更新 UI
      updateChatMessage(data);
    }
  }
};
```

#### 非流式对话

```typescript
export const chatWithAgentSync = async (message: string, sessionId: string) => {
  const token = authStorage.getToken();
  
  return request.post('http://localhost:5000/run', {
    query: message,
    session_id: sessionId
  }, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
};
```

### 3. 数据 API 示例

#### 获取仪表盘数据

```typescript
import { getDashboardData } from '@/api/dashboard';

const dashboardData = await getDashboardData();
console.log('仪表盘数据:', dashboardData);
```

#### 获取课程表

```typescript
import { getWeeklySchedule } from '@/api/schedule';

const schedule = await getWeeklySchedule();
console.log('课程表:', schedule);
```

---

## 🌐 WebSocket 连接

### 前端使用

```typescript
import { useWebSocket } from '@/hooks/useWebSocket';

function ChatComponent() {
  const { isConnected, send } = useWebSocket({
    autoConnect: true,
    channels: ['chat', 'dashboard'],
    onMessage: (data) => {
      console.log('收到实时消息:', data);
      
      switch (data.type) {
        case 'chat':
          updateChatMessage(data);
          break;
        case 'dashboard_update':
          updateDashboard(data);
          break;
      }
    },
    onError: (error) => {
      console.error('WebSocket 错误:', error);
    }
  });

  const sendMessage = (message: string) => {
    send('message', {
      type: 'chat',
      content: message,
      timestamp: new Date().toISOString()
    });
  };

  return (
    <div>
      <p>连接状态: {isConnected ? '已连接' : '未连接'}</p>
      {/* 聊天界面 */}
    </div>
  );
}
```

---

## 🔄 完整流程

### 用户登录流程

```
1. 用户输入用户名和密码
   ↓
2. 前端调用 POST /api/v1/auth/login
   ↓
3. Mock API 验证用户名密码
   ↓
4. 返回 JWT Token 和用户信息
   ↓
5. 前端存储 Token 到 localStorage
   ↓
6. 后续请求自动携带 Authorization: Bearer {token}
   ↓
7. 跳转到主页
```

### 智能体对话流程

```
1. 用户发送消息
   ↓
2. 前端调用 POST /stream_run
   ↓
3. 后端验证 Token
   ↓
4. 传入 LangGraph Agent
   ↓
5. Agent 使用工具处理请求
   ↓
6. 通过 SSE 流式返回响应
   ↓
7. 前端实时更新 UI
```

### 实时数据更新流程

```
1. 后端数据发生变化（如作业更新）
   ↓
2. 后端通过 WebSocket 推送消息
   ↓
3. 前端接收消息
   ↓
4. 更新 UI 界面
```

---

## ❓ 常见问题

### 1. CORS 跨域错误

**问题**: 前端调用 API 时出现 CORS 错误

**解决方案**:

在 `multiuser_api.py` 中配置 CORS:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
);
```

### 2. Token 过期

**问题**: 请求返回 401 错误

**解决方案**:

前端已在 `request.ts` 中自动处理 401 错误，会自动跳转到登录页。

### 3. WebSocket 连接失败

**问题**: WebSocket 无法连接

**解决方案**:

1. 检查 WebSocket 服务器是否启动
2. 检查端口配置（默认 8765）
3. 检查防火墙设置
4. 查看浏览器控制台错误信息

### 4. 流式响应中断

**问题**: SSE 流式响应中途停止

**解决方案**:

1. 检查网络连接
2. 检查服务器日志是否有错误
3. 增加超时时间
4. 实现断线重连机制

---

## 📚 相关文件

### 前端文件

- `magic-school-frontend/src/utils/request.ts` - HTTP 请求配置
- `magic-school-frontend/src/hooks/useWebSocket.ts` - WebSocket Hook
- `magic-school-frontend/vite.config.ts` - Vite 配置和代理设置
- `magic-school-frontend/src/contexts/AuthContext.tsx` - 认证上下文

### 后端文件

- `src/main.py` - 智能体 API 服务器（/run, /stream_run）
- `src/api/multiuser_api.py` - 多用户 API 服务器
- `src/websocket_server.py` - WebSocket 服务器
- `scripts/mock_api_server.py` - Mock API 服务器（开发调试）

---

## 🔗 快速链接

- [前端调试指南](./前端调试指南.md)
- [前端界面访问指南](./前端界面访问指南.md)
- [后端 API 文档](http://localhost:3000/docs) (Mock API)
- [智能体 API 文档](http://localhost:5000/docs) (生产环境)
