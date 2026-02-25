# 🔍 魔法课桌后端API部署说明

> **重要说明**：本文档澄清项目的实际部署架构和API调用方式

---

## 📊 当前部署架构

### 📍 Coze 平台模式（当前）

```
┌─────────────┐
│   前端应用   │
└──────┬──────┘
       │ Coze API
       ↓
┌──────────────────┐
│  Coze 平台       │
│  (托管服务)      │
└──────┬───────────┘
       │ LangGraph
       ↓
┌──────────────────┐
│  魔法课桌 Agent  │
│  (您的代码)      │
└──────────────────┘
```

**关键信息**：
- ✅ 代码运行在 Coze 平台的沙箱环境中
- ✅ 无需自己部署服务器
- ✅ 使用 Coze 提供的 API 接口
- ⚠️ 有限制：无法使用自定义域名、无法完全控制认证方式

### 📍 独立服务模式（生产推荐）

```
┌─────────────┐
│   前端应用   │
└──────┬──────┘
       │ FastAPI
       ↓
┌──────────────────┐
│  FastAPI 服务    │
│  (您的服务器)    │
└──────┬───────────┘
       │ LangGraph
       ↓
┌──────────────────┐
│  魔法课桌 Agent  │
└──────────────────┘
```

**关键信息**：
- ✅ 需要部署到自己的服务器
- ✅ 可以使用自定义域名
- ✅ 完全控制认证方式（JWT）
- ✅ 完整的 REST API + WebSocket 支持

---

## 🔄 两种模式的对比

| 项目 | Coze 平台模式 | 独立服务模式 |
|------|--------------|--------------|
| **部署方式** | Coze 平台托管 | 自己部署服务器 |
| **API 地址** | Coze 提供的 API | 自定义域名 |
| **认证方式** | Coze Bearer Token | JWT Token |
| **WebSocket** | ❌ 不支持 | ✅ 支持 |
| **流式响应** | ✅ 支持（Coze API） | ✅ 支持（SSE） |
| **用户认证** | ⚠️ 依赖 Coze | ✅ 完整的 JWT 认证 |
| **数据隔离** | ⚠️ 有限制 | ✅ 完全控制 |
| **成本** | 免费或按量付费 | 需要购买服务器 |
| **推荐场景** | 开发/测试 | 生产环境 |

---

## 📡 API 调用方式对比

### Coze 平台模式

#### 聊天接口

```bash
# Coze API 地址
POST https://api.coze.com/open_api/v2/stream_run

# 请求头
Headers: {
  "Authorization": "Bearer YOUR_COZE_API_KEY",
  "Content-Type": "application/json",
  "Accept": "text/event-stream"
}

# 请求体
Body: {
  "bot_id": "YOUR_BOT_ID",
  "user_id": "session_123456",
  "additional_messages": [
    {
      "role": "user",
      "content": "你好",
      "content_type": "text"
    }
  ],
  "stream": true
}

# 响应（SSE流式响应）
data: {"event": "conversation.message.delta", "data": {"content": "你好呀！小巫师！"}}
```

#### 获取 Bot 信息

```bash
GET https://api.coze.com/open_api/v2/bot/info
Headers: {
  "Authorization": "Bearer YOUR_COZE_API_KEY"
}
```

---

### 独立服务模式

#### 1. 用户注册

```bash
# API 地址（假设部署在 https://api.magic-desk.com）
POST https://api.magic-desk.com/api/auth/register

# 请求头
Headers: {
  "Content-Type": "application/json"
}

# 请求体
Body: {
  "username": "xiaoming",
  "password": "password123",
  "role": "student",
  "student_name": "小明",
  "grade": "三年级"
}

# 响应
{
  "success": true,
  "message": "注册成功",
  "user": {
    "user_id": "usr_123456",
    "username": "xiaoming",
    "role": "student"
  }
}
```

#### 2. 用户登录

```bash
POST https://api.magic-desk.com/api/auth/login

# 请求体
Body: {
  "username": "xiaoming",
  "password": "password123"
}

# 响应
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 86400,
  "user": {
    "user_id": "usr_123456",
    "username": "xiaoming",
    "role": "student"
  }
}
```

#### 3. 聊天接口（普通）

```bash
POST https://api.magic-desk.com/api/v1/chat

# 请求头
Headers: {
  "Authorization": "Bearer YOUR_JWT_ACCESS_TOKEN",
  "Content-Type": "application/json"
}

# 请求体
Body: {
  "message": "你好",
  "session_id": "sess_123456"
}

# 响应
{
  "success": true,
  "response": "你好呀！小巫师！今天需要什么魔法帮助呢？✨",
  "message_id": "msg_789",
  "timestamp": "2025-02-24T12:00:00Z"
}
```

#### 4. 聊天接口（流式）

```bash
POST https://api.magic-desk.com/api/v1/chat/stream

# 请求头
Headers: {
  "Authorization": "Bearer YOUR_JWT_ACCESS_TOKEN",
  "Content-Type": "application/json",
  "Accept": "text/event-stream"
}

# 请求体
Body: {
  "message": "你好",
  "session_id": "sess_123456"
}

# 响应（SSE流式响应）
event: message
data: {"type": "text", "content": "你好"}

event: message
data: {"type": "text", "content": "呀！"}

event: message
data: {"type": "text", "content": "小巫师！"}
```

#### 5. WebSocket 实时对话

```javascript
// WebSocket 连接
const ws = new WebSocket(
  'wss://api.magic-desk.com/ws/chat?token=YOUR_JWT_ACCESS_TOKEN&sessionId=sess_123456'
);

// 监听消息
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('收到消息:', data);
};

// 发送消息
ws.send(JSON.stringify({
  type: "message",
  content: "你好"
}));
```

#### 6. 刷新 Token

```bash
POST https://api.magic-desk.com/api/auth/refresh

# 请求头
Headers: {
  "Content-Type": "application/json"
}

# 请求体
Body: {
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

# 响应
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400
}
```

---

## 🔑 认证方式对比

### Coze 平台模式

**认证流程**：
1. 在 Coze 平台创建 Bot
2. 获取 Bot ID 和 API Key
3. 使用 API Key 进行身份认证

**特点**：
- ✅ 简单，无需自己实现认证
- ⚠️ 所有用户使用同一个 API Key
- ⚠️ 无法区分不同用户
- ⚠️ 难以实现细粒度权限控制

### 独立服务模式

**认证流程**：
1. 用户注册 → 账户存储在 PostgreSQL
2. 用户登录 → 返回 JWT Access Token 和 Refresh Token
3. 每次请求携带 Access Token
4. Token 过期后使用 Refresh Token 刷新

**特点**：
- ✅ 每个用户独立的 Token
- ✅ 完整的用户管理功能
- ✅ 支持角色权限（学生/家长）
- ✅ Token 自动刷新机制
- ✅ 安全的密码加密（bcrypt）

---

## 🚀 如何切换到独立服务模式？

### 步骤 1：修复代码（合并 multiuser 路由）

需要将 `src/api/multiuser_api.py` 改为使用 `APIRouter` 而不是独立的 FastAPI 应用。

### 步骤 2：部署到服务器

#### 部署选项

**选项 A：阿里云 ECS**

```bash
# 1. 购买阿里云 ECS 服务器
# 2. 安装依赖
ssh root@your-server-ip
yum install python3.11 postgresql -y

# 3. 上传代码
scp -r magic-school-agent root@your-server-ip:/opt/

# 4. 安装 Python 依赖
cd /opt/magic-school-agent
pip3 install -r requirements.txt

# 5. 配置环境变量
cp docs/生产环境变量配置模板.txt .env
vi .env

# 6. 初始化数据库
python3 scripts/init_database.py

# 7. 启动服务
python3 src/main.py -m http -p 5000
```

**选项 B：Docker 部署**

```bash
# 1. 创建 Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/main.py", "-m", "http", "-p", "5000"]

# 2. 构建镜像
docker build -t magic-desk-api .

# 3. 运行容器
docker run -d -p 5000:5000 \
  --env-file .env \
  magic-desk-api
```

**选项 C：使用云托管服务**

- 阿里云云应用平台
- 腾讯云云开发
- 华为云函数计算

### 步骤 3：配置域名和 SSL

```bash
# 使用 Nginx 反向代理
server {
    listen 443 ssl http2;
    server_name api.magic-desk.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws/chat {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 📝 测试账号（独立服务模式）

### 预置测试账号

运行 `scripts/init_database.py` 会自动创建：

| 用户名 | 密码 | 角色 | 用途 |
|--------|------|------|------|
| `student` | `password123` | student | 测试学生功能 |
| `parent` | `password123` | parent | 测试家长功能 |

### 测试流程

```bash
# 1. 登录获取 Token
curl -X POST https://api.magic-desk.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"password123"}'

# 2. 使用 Token 调用聊天接口
curl -X POST https://api.magic-desk.com/api/v1/chat/stream \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"你好","session_id":"test_123"}'
```

---

## ❓ 常见问题

### Q1: 我现在应该使用哪种模式？

**A**：
- **开发/测试阶段**：使用 Coze 平台模式（简单快捷）
- **生产环境**：使用独立服务模式（完整功能）

### Q2: 代码中的 JWT 认证能用吗？

**A**：
- 当前代码中已实现 JWT 认证
- 但 multiuser 路由需要修复才能集成到主服务
- 需要先合并路由，再部署为独立服务

### Q3: 前端需要修改吗？

**A**：
- **Coze 模式**：前端使用 Coze API
- **独立模式**：前端使用自定义 API 地址和 JWT 认证
- 需要配置 API 基础 URL 和认证方式

### Q4: 如何获取 Coze API Key？

**A**：
1. 登录 Coze 平台
2. 创建 Bot 或进入已有 Bot
3. 在 Bot 设置中找到 API Key
4. 使用 API Key 调用 Coze API

### Q5: 什么时候切换到独立服务？

**A**：
当您需要以下功能时：
- ✅ 自定义域名
- ✅ WebSocket 实时通信
- ✅ 完整的用户认证系统
- ✅ 数据完全隔离
- ✅ 自定义认证方式

---

## 📞 技术支持

- **Coze 平台文档**: https://www.coze.cn/docs/
- **项目文档**: `/workspace/projects/docs/`
- **API 文档**: `API_DOCUMENTATION.md`
- **部署指南**: `DEPLOYMENT_GUIDE_COMPLETE.md`

---

**最后更新**: 2025-02-24
**版本**: 1.0.0
