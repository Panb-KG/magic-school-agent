# 🪄 魔法课桌学习助手智能体

<div align="center">
  <img src="assets/魔法书AI核.jpg" alt="魔法课桌AI助手Logo" width="200" height="200" />
  <p>基于LangGraph和多Agent架构的智能学习管理系统，专为小学生和家长设计</p>
</div>

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0-purple.svg)](https://github.com/langchain-ai/langgraph)

---

## 📖 关于Logo

本项目使用"魔法书AI核心"作为官方Logo和对话头像。

**设计理念**:
- **魔法书**: 象征知识、智慧、传承
- **发光水晶球**: 象征AI的洞察力和预测能力
- **AI标识**: 明确智能体身份
- **魔法符号**: 暗示AI的多元能力

了解更多：[Logo说明文档](docs/Logo说明.md)

---

## ✨ 特性

### 🎯 核心功能

- **智能对话系统**: 基于LangGraph的多Agent架构
- **多用户支持**: 学生和家长双角色
- **长期记忆**: 记忆用户偏好和历史
- **时间感知**: 自动获取和处理时间信息
- **30+工具**: 课程管理、作业管理、成就系统等

### 🎨 魔法元素

- 游戏化学习体验
- 魔法等级和积分系统
- 成就墙展示
- 友好的魔法主题对话

### 📚 功能模块

- 📅 课程表管理
- 📝 作业管理
- 🏆 成就系统
- 🏃 运动记录
- 📖 朗读练习和评估
- 👨‍👩‍👧‍👦 家长管理
- 💾 文件管理
- 💬 对话会话管理

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 18+
- PostgreSQL 13+
- Redis 6+ (可选)

### 安装

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/magic-school-agent.git
cd magic-school-agent

# 2. 安装Python依赖
pip install -r requirements.txt

# 3. 安装前端依赖
cd magic-school-frontend
npm install
cd ..

# 4. 配置环境变量
# 创建 .env 文件（参考 docs/生产环境变量配置模板.txt）
# 必须配置: JWT_SECRET, DASHSCOPE_API_KEY, OPENAI_BASE_URL

# 5. 初始化数据库
python scripts/init_database.py
```

### 启动服务

```bash
# 方式1: 使用一键启动脚本（推荐）
./scripts/start_all_services.sh

# 方式2: 手动启动

# 1. 启动API后端（端口8000）
uvicorn src.main:app --reload --port 8000

# 2. 启动前端服务（端口5173）
cd magic-school-frontend
npm run dev
```

### 访问应用

- **前端**: http://localhost:5173
- **API文档**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws/chat

### 🚀 生产部署

如果您想部署到生产环境，推荐使用 **扣子平台部署**：

- [扣子平台部署指南](docs/扣子编程项目部署实际操作指南.md) - 详细步骤
- [快速参考卡](docs/扣子平台部署快速参考卡.md) - 5分钟完成部署

或参考 [部署指南](DEPLOYMENT_GUIDE.md) 进行手动部署。

### 测试账号

- **学生**: `student` / `password123`
- **家长**: `parent` / `password123`

## 📁 项目结构

```
magic-school-agent/
├── src/                    # 智能体核心代码
│   ├── agents/           # Agent定义
│   ├── tools/            # 工具实现
│   ├── api/              # API接口
│   └── main.py           # FastAPI入口
├── config/               # 配置文件
├── scripts/              # 脚本工具
├── docs/                 # 文档
├── assets/               # 资源文件
├── magic-school-frontend/ # 前端代码
├── requirements.txt      # Python依赖
└── README.md
```

## 🔧 配置

### 环境变量

创建 `.env` 文件：

```env
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/magic_school

# 大模型配置
LLM_API_KEY=your_api_key
LLM_MODEL=doubao-seed-1-6-251015

# JWT配置
SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256

# 服务端口
API_PORT=3000
AGENT_PORT=5000
FRONTEND_PORT=5173
```

### Agent配置

编辑 `config/agent_llm_config.json`：

```json
{
  "config": {
    "model": "doubao-seed-1-6-251015",
    "temperature": 0.8,
    "top_p": 0.9,
    "max_completion_tokens": 4000
  },
  "sp": "系统提示词...",
  "tools": ["工具列表"]
}
```

## 📖 文档

### 用户文档
- [README](README.md) - 项目概述
- [快速开始](QUICK_START.md) - 5分钟快速入门
- [项目概览](OVERVIEW.txt) - 项目快速参考

### 部署文档
- [扣子平台部署指南](docs/扣子编程项目部署实际操作指南.md) - Coze平台部署详解 ⭐
- [扣子平台部署快速参考卡](docs/扣子平台部署快速参考卡.md) - 部署快速参考 ⭐
- [环境变量配置模板](docs/生产环境变量配置模板.txt) - 生产环境配置模板
- [部署指南](DEPLOYMENT_GUIDE.md) - 通用部署指南

### API文档
- [API完整文档](API_DOCUMENTATION.md) - REST API接口文档
- [后端API文档](docs/后端API完整文档-Figma设计用.md) - 后端API详解
- [前端调用指南](docs/前端调用魔法课桌智能体指南.md) - 前端集成指南

### 开发文档
- [开发指南](DEVELOPMENT_GUIDE.md) - 开发者指南
- [项目结构](PROJECT_STRUCTURE.md) - 项目结构说明
- [架构设计](ARCHITECTURE.md) - 系统架构
- [魔法课桌部署方案](docs/魔法课桌智能体部署方案分析.md) - 部署方案分析

### 发布文档
- [发布清单](RELEASE_CHECKLIST.md) - 发布前检查清单
- [发布说明](RELEASE_NOTES.md) - 版本发布说明
- [交付清单](PROJECT_DELIVERY_CHECKLIST.md) - 项目交付清单
- [状态报告](PROJECT_STATUS_REPORT.md) - 项目状态报告
- [开发历程](PROJECT_JOURNEY.md) - 项目开发历程

## 🛠️ 技术栈

### 后端

- **框架**: FastAPI, LangGraph
- **大模型**: 豆包 (Doubao Seed)
- **数据库**: PostgreSQL
- **缓存**: Redis (可选)
- **认证**: JWT

### 前端

- **框架**: React 18, Vite
- **UI库**: Ant Design
- **状态管理**: Redux Toolkit
- **HTTP**: Axios
- **路由**: React Router

## 🧪 测试

```bash
# 运行后端测试
pytest tests/

# 运行前端测试
cd magic-school-frontend
npm test

# 测试Agent服务
bash scripts/test_agent.sh

# 测试所有服务
bash scripts/test_services.sh
```

## 📦 部署

### 方式1: 扣子平台部署（推荐）⭐

最简单快捷的部署方式，一键部署到Coze平台。

**步骤**：
1. 查看 [扣子平台部署指南](docs/扣子编程项目部署实际操作指南.md)
2. 使用 [快速参考卡](docs/扣子平台部署快速参考卡.md) 快速配置
3. 配置环境变量（见 [环境变量模板](docs/生产环境变量配置模板.txt)）
4. 点击部署，3-5分钟即可完成

**优势**：
- ✅ 无需服务器
- ✅ 自动域名
- ✅ 一键部署
- ✅ 自动扩展

### 方式2: Docker部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d
```

### 方式3: 手动部署

详见 [部署指南](DEPLOYMENT_GUIDE.md)

**环境要求**：
- Python 3.8+
- Node.js 18+
- PostgreSQL 13+
- Redis 6+ (可选)

## 🤝 贡献

欢迎贡献代码！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 👥 团队

- 开发: Magic School Team

## 🙏 致谢

- [LangGraph](https://github.com/langchain-ai/langgraph)
- [FastAPI](https://fastapi.tiangolo.com/)
- [豆包大模型](https://www.volcengine.com/product/ark)

## 📞 联系

- 项目地址: https://github.com/your-username/magic-school-agent
- 问题反馈: https://github.com/your-username/magic-school-agent/issues

---

**让学习充满魔法！** ✨🪄
