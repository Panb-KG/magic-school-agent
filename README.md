# 🪄 魔法课桌学习助手智能体 - 后端API服务

<div align="center">
  <img src="assets/魔法书AI核.jpg" alt="魔法课桌AI助手Logo" width="200" height="200" />
  <p>基于LangGraph和多Agent架构的智能学习管理系统后端服务，专为小学生和家长设计</p>
</div>

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0-purple.svg)](https://github.com/langchain-ai/langgraph)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

---

## 📖 关于

魔法课桌学习助手智能体是一款**后端API服务**，提供完整的学习管理功能，包括：

- ✅ **智能对话系统**：基于LangGraph的多Agent架构
- ✅ **多用户支持**：学生和家长双角色，完善的权限管理
- ✅ **长期记忆**：记忆用户偏好、对话摘要、知识掌握度
- ✅ **数据隔离**：完全的多租户数据隔离，确保数据安全
- ✅ **时间感知**：自动获取和处理时间信息
- ✅ **30+工具**：课程管理、作业管理、成就系统等
- ✅ **实时通信**：WebSocket支持，流式响应
- ✅ **完整API**：RESTful API + WebSocket

---

## ✨ 核心特性

### 🎯 功能模块

- **智能对话中心** 🧙‍♂️
  - 自然语言理解
  - 工具调用机制
  - 多轮对话能力
  - 启发式引导

- **用户认证系统** 🔐
  - JWT Token认证
  - Token自动刷新
  - bcrypt密码加密
  - 学生/家长双角色

- **数据管理** 📊
  - 课程表管理
  - 作业管理
  - 成就系统
  - 学生档案

- **会话管理** 💬
  - 对话历史管理
  - 会话标题生成
  - 会话搜索功能
  - 批量操作

- **记忆系统** 🧠
  - 对话摘要
  - 用户画像
  - 知识掌握度
  - 行为偏好

### 🚀 技术特性

- **实时通信**：WebSocket支持流式对话
- **流式响应**：Server-Sent Events (SSE)
- **数据隔离**：多租户架构
- **权限管理**：基于角色的访问控制
- **安全认证**：JWT + bcrypt加密

---

## 🚀 快速开始

### 📌 部署方式选择

本项目支持**两种部署方式**，请根据您的需求选择：

#### 方式 A：Coze 平台模式（推荐开发/测试）⚡

- ✅ **无需部署**：代码运行在 Coze 平台沙箱中
- ✅ **立即可用**：获取 API Key 后直接调用
- ✅ **简单快捷**：无需配置服务器和数据库
- ⚠️ **限制**：无法使用自定义域名，无 WebSocket 支持

**适用场景**：
- 快速开发和测试
- 演示和原型
- 不需要复杂部署的场景

👉 [查看 Coze API 集成指南](COZE_API_GUIDE.md)

**快速测试**：
```bash
# 打开演示页面
open examples/coze-api-demo.html

# 或使用 Python SDK
python examples/coze_client.py
```

---

#### 方式 B：独立服务模式（推荐生产环境）🚀

- ✅ **完整功能**：REST API + WebSocket
- ✅ **自定义域名**：使用自己的域名
- ✅ **完全控制**：自主管理认证、数据库等
- ✅ **数据隔离**：多租户数据完全隔离
- ⏳ **需要部署**：需要配置服务器

**适用场景**：
- 生产环境
- 需要自定义域名
- 需要完整功能控制

👉 [查看独立部署指南](DEPLOYMENT_GUIDE_COMPLETE.md)

**快速部署**：
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp docs/生产环境变量配置模板.txt .env
vi .env

# 3. 初始化数据库
python scripts/init_database.py

# 4. 启动服务
python src/main.py -m http -p 5000
```

---

### 环境要求

- Python 3.8+
- PostgreSQL 13+
- Redis 6+ (可选)

### 安装

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/magic-school-agent.git
cd magic-school-agent

# 2. 安装Python依赖
pip install -r requirements.txt

# 3. 配置环境变量
# 创建 .env 文件（参考 docs/生产环境变量配置模板.txt）
# 必须配置: JWT_SECRET, DASHSCOPE_API_KEY, OPENAI_BASE_URL

# 4. 初始化数据库
python scripts/init_database.py
```

### 启动服务

```bash
# 方式1: 使用HTTP模式（推荐）
python src/main.py -m http -p 5000

# 方式2: 使用Agent模式
python src/main.py -m agent

# 服务将在 http://localhost:5000 启动
```

### 访问应用

- **API文档**: http://localhost:5000/docs
- **WebSocket**: ws://localhost:5000/ws/chat
- **健康检查**: http://localhost:5000/health

---

## 📁 项目结构

```
magic-school-agent/
├── src/                    # 智能体核心代码
│   ├── agents/           # Agent定义
│   │   └── agent.py      # 主Agent实现
│   ├── tools/            # 工具实现
│   │   ├── conversation_tool.py  # 对话工具
│   │   ├── course_tool.py       # 课程工具
│   │   ├── homework_tool.py      # 作业工具
│   │   └── ...                    # 其他工具
│   ├── api/              # API接口
│   │   ├── multiuser_api.py      # 多用户API
│   │   ├── websocket_api.py      # WebSocket API
│   │   └── chat_api.py           # 对话API
│   ├── auth/             # 认证模块
│   │   ├── auth_utils.py         # 认证工具
│   │   ├── user_manager.py       # 用户管理
│   │   └── permissions.py        # 权限管理
│   ├── storage/          # 数据存储
│   │   ├── database/             # 数据库管理
│   │   ├── memory/               # 长期记忆
│   │   └── session.py            # 会话管理
│   └── main.py           # FastAPI入口
├── config/               # 配置文件
│   ├── agent_llm_config.json  # Agent配置
│   └── logo.config.js         # Logo配置
├── scripts/              # 脚本工具
│   ├── init_database.py        # 数据库初始化
│   ├── test_full_functionality.py  # 功能测试
│   └── manage_agent.sh         # Agent管理脚本
├── tests/                # 测试代码
│   ├── test_agent_completeness.py  # Agent测试
│   ├── test_multiuser.py          # 多用户测试
│   └── test_base.py               # 测试基类
├── docs/                 # 文档
├── assets/               # 资源文件
├── requirements.txt      # Python依赖
└── README.md            # 本文件
```

---

## 📖 文档

### 技术文档
- **[技术实现详解](AGENT_TECHNICAL_SPECIFICATION.md)** ⭐ - 功能、API、认证、数据隔离、记忆实现详解
- [多用户架构功能说明](docs/MULTIUSER_GUIDE.md) - 多用户、长期记忆系统说明
- [功能说明文档](docs/功能说明文档.md) - 完整功能模块说明
- [权限检查完善总结](docs/权限检查完善总结.md) - 权限管理详解

### API文档
- [API完整文档](API_DOCUMENTATION.md) - REST API接口文档
- [后端API文档](docs/后端API完整文档-Figma设计用.md) - 后端API详解

### 部署文档
- [后端开发计划](BACKEND_DEVELOPMENT_PLAN.md) - 后端开发计划和进度
- [完整部署指南](DEPLOYMENT_GUIDE_COMPLETE.md) - 详细部署步骤
- [快速部署开始](DEPLOYMENT_QUICK_START.md) - 5分钟快速部署
- [部署命令速查表](DEPLOYMENT_COMMANDS.md) - 常用命令集合
- [部署检查清单](DEPLOYMENT_CHECKLIST.md) - 部署前检查项
- [扣子平台部署指南](docs/扣子平台部署指南.md) - Coze平台部署
- [扣子平台部署快速参考卡](docs/扣子平台部署快速参考卡.md) - 部署快速参考
- [环境变量配置模板](docs/生产环境变量配置模板.txt) - 生产环境配置模板

### 测试文档
- [完整功能测试报告](session_fix_report_20250224.md) - Session管理修复报告
- [回滚验证报告](test_report_rollback_20250224.md) - 回滚后功能验证
- [功能完备性评估报告](docs/功能完备性评估报告.md) - 功能完整性评估
- [Agent软件完备性检查报告](docs/Agent软件完备性检查报告.md) - Agent完备性检查

---

## 🔧 配置

### 环境变量

创建 `.env` 文件：

```env
# 数据库配置
PGDATABASE_URL=postgresql://user:password@localhost:5432/magic_school

# 大模型配置
DASHSCOPE_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# JWT配置
JWT_SECRET=your-super-secret-jwt-key-change-in-production-min-32-chars

# 服务配置
API_PORT=5000
DEBUG=False
LOG_LEVEL=INFO
```

### Agent配置

编辑 `config/agent_llm_config.json`：

```json
{
  "config": {
    "model": "doubao-seed-1-6-251015",
    "temperature": 0.8,
    "top_p": 0.9,
    "max_completion_tokens": 4000,
    "timeout": 600,
    "thinking": "disabled"
  },
  "sp": "你是一个魔法学习助手...",
  "tools": [
    "create_student_profile",
    "get_student_profile",
    "create_course",
    "get_course_schedule",
    "create_homework",
    "get_homeworks",
    "create_achievement",
    "get_achievements",
    "save_conversation_memory",
    "retrieve_relevant_memories"
  ]
}
```

---

## 📡 API接口

### 认证接口

```bash
# 用户注册
POST /api/auth/register
{
  "username": "xiaoming",
  "password": "password123",
  "role": "student",
  "student_name": "小明",
  "grade": "三年级"
}

# 用户登录
POST /api/auth/login
{
  "username": "xiaoming",
  "password": "password123"
}

# 刷新Token
POST /api/auth/refresh
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

# 登出
POST /api/auth/logout
Headers: Authorization: Bearer <access_token>
```

### 对话接口

```bash
# 普通对话
POST /api/v1/chat
Headers: Authorization: Bearer <access_token>
{
  "message": "你好",
  "session_id": "sess_123"
}

# 流式对话（SSE）
POST /api/v1/chat/stream
Headers: Authorization: Bearer <access_token>
{
  "message": "你好",
  "session_id": "sess_123"
}

# WebSocket实时对话
ws://localhost:5000/ws/chat?token=<access_token>&sessionId=<session_id>
```

### 数据管理接口

```bash
# 获取学生仪表盘
GET /api/v1/students/dashboard/{student_name}
Headers: Authorization: Bearer <access_token>

# 获取课程表
GET /api/v1/courses/schedule/{student_name}
Headers: Authorization: Bearer <access_token>

# 获取作业列表
GET /api/v1/homeworks?student_id=1
Headers: Authorization: Bearer <access_token>

# 获取成就列表
GET /api/v1/achievements?student_id=1
Headers: Authorization: Bearer <access_token>

# 搜索对话会话
GET /api/v1/conversations/search?keyword=数学&user_id=usr_123
Headers: Authorization: Bearer <access_token>
```

---

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_agent_completeness.py
pytest tests/test_multiuser.py

# 运行完整功能测试
python scripts/test_full_functionality.py
```

### 测试账号

- **学生**: `student` / `password123`
- **家长**: `parent` / `password123`

---

## 🔒 安全机制

### 认证安全
- ✅ 密码加密（bcrypt）
- ✅ JWT Token认证
- ✅ Token过期机制（24小时）
- ✅ Refresh Token机制（7天）
- ✅ 防暴力破解（失败次数限制）

### 数据安全
- ✅ SQL注入防护（ORM参数化查询）
- ✅ XSS防护（输入验证和输出编码）
- ✅ CSRF防护（Token验证）
- ✅ 数据隔离（多租户架构）
- ✅ 敏感数据加密

### API安全
- ✅ HTTPS加密传输
- ✅ 速率限制
- ✅ 请求大小限制
- ✅ IP白名单（可选）
- ✅ API Key管理

---

## 📊 架构说明

### 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI 后端服务                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              API路由层 (API Routes)                 │    │
│  │  - /api/v1/auth/* (认证)                            │    │
│  │  - /api/v1/students/* (学生管理)                    │    │
│  │  - /api/v1/courses/* (课程管理)                     │    │
│  │  - /api/v1/homeworks/* (作业管理)                   │    │
│  │  - /api/v1/chat/* (对话接口)                        │    │
│  │  - /ws/chat (WebSocket)                             │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              业务层 (Business Logic)                 │    │
│  │  - UserManager (用户管理)                           │    │
│  │  - StudentManager (学生管理)                        │    │
│  │  - HomeworkManager (作业管理)                       │    │
│  │  - CourseManager (课程管理)                         │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Agent层 (LangGraph Agent)               │    │
│  │  - Multi-Agent架构                                  │    │
│  │  - 工具调用 (30+ tools)                             │    │
│  │  - 长期记忆管理                                      │    │
│  │  - 数据隔离                                         │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              数据层 (Data Access)                    │    │
│  │  - SQLAlchemy ORM                                    │    │
│  │  - PostgreSQL数据库                                  │    │
│  │  - 会话管理 (Session Manager)                        │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ SQL
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    PostgreSQL 数据库                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  auth       │  │  public     │  │  memory     │         │
│  │  schema     │  │  schema     │  │  schema     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 部署

### 快速部署（扣子平台）

```bash
# 1. 准备环境变量
cat > .env.production << 'EOF'
DASHSCOPE_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
JWT_SECRET=your-super-secret-jwt-key
DEBUG=False
LOG_LEVEL=INFO
EOF

# 2. 推送到GitHub
git add .
git commit -m "准备部署"
git push origin main

# 3. 在扣子平台创建项目并部署
# 参考: docs/扣子平台部署指南.md
```

### 生产部署（阿里云ECS）

```bash
# 参考: DEPLOYMENT_GUIDE_COMPLETE.md
# 1. 购买ECS服务器
# 2. 配置安全组
# 3. 安装依赖
# 4. 配置Nginx
# 5. 配置SSL证书
# 6. 启动服务
```

---

## 📚 快速集成

### Coze API 集成（推荐快速开始）

如果您想快速开始使用，推荐使用 **Coze 平台模式**：

#### 📖 完整文档
- [Coze API 调用指南](COZE_API_GUIDE.md) - 详细的 API 使用说明
- [API 部署架构说明](API_DEPLOYMENT_GUIDE.md) - 部署方式对比

#### 💻 代码示例
- [HTML 演示页面](examples/coze-api-demo.html) - 纯 HTML/JS 演示
- [React 集成示例](examples/react-integration-example.md) - React 完整集成
- [Python SDK](examples/coze_client.py) - Python 客户端封装

#### 🚀 5 分钟快速测试

```javascript
// JavaScript 示例
const response = await fetch('https://api.coze.com/open_api/v2/stream_run', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_COZE_API_KEY',
    'Content-Type': 'application/json',
    'Accept': 'text/event-stream'
  },
  body: JSON.stringify({
    bot_id: 'YOUR_BOT_ID',
    user_id: 'session_123',
    additional_messages: [{
      role: 'user',
      content: '你好',
      content_type: 'text'
    }],
    stream: true
  })
});
```

```python
# Python 示例
from coze_client import MagicDeskAssistant

assistant = MagicDeskAssistant(
    api_key="your_api_key",
    bot_id="your_bot_id"
)

answer = assistant.ask("你好", "session_123", stream=True)
print(answer)
```

---

## 📞 技术支持

- **文档**: `/workspace/projects/docs/`
- **测试脚本**: `/workspace/projects/scripts/`
- **日志目录**: `/workspace/projects/logs/`

---

## 📄 许可证

MIT License

---

**本项目专注于后端API服务开发，不包含前端代码。**
