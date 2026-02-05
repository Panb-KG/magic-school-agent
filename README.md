# 🪄 魔法课桌学习助手智能体

> 基于LangGraph和多Agent架构的智能学习管理系统，专为小学生和家长设计

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0-purple.svg)](https://github.com/langchain-ai/langgraph)

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

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要的配置

# 5. 初始化数据库
cd ..
python scripts/init_db.py
```

### 启动服务

```bash
# 1. 启动API后端（端口3000）
python scripts/mock_api_server.py

# 2. 启动Agent服务（端口5000）
python src/main.py -m http -p 5000

# 3. 启动前端服务（端口5173）
cd magic-school-frontend
npm run dev
```

### 访问应用

- 前端: http://localhost:5173
- API文档: http://localhost:3000/docs
- Agent文档: http://localhost:5000/docs

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

- [API文档](docs/后端API完整文档-Figma设计用.md)
- [部署指南](docs/快速部署指南.md)
- [开发指南](docs/魔法课桌智能体部署方案分析.md)
- [前端调用指南](docs/前端调用魔法课桌智能体指南.md)

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

### Docker部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d
```

### 手动部署

详见 [快速部署指南](docs/快速部署指南.md)

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
