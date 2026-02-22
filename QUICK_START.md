# 魔法课桌学习助手智能体 - 快速启动指南

## 🚀 5分钟快速开始

### 前置条件
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- 阿里云百炼API Key

---

## 步骤1: 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装前端依赖
cd magic-school-frontend
npm install
cd ..
```

---

## 步骤2: 配置环境变量

创建 `.env` 文件并填写以下配置：

```bash
# 数据库配置
DATABASE_URL=postgresql://username:password@localhost:5432/magic_school

# JWT密钥（请修改为随机字符串）
JWT_SECRET=your-secret-key-here

# 阿里云百炼配置（使用标准命名）
DASHSCOPE_API_KEY=your-aliyun-api-key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 其他配置
DEBUG=True
LOG_LEVEL=INFO
```

---

## 步骤3: 初始化数据库

```bash
python scripts/init_database.py
```

该脚本会：
1. 创建数据库表
2. 创建初始管理员用户
3. 运行数据库迁移

**默认管理员账户**:
- 用户名: admin
- 密码: admin123
- ⚠️ 请在生产环境中立即修改密码！

---

## 步骤4: 启动服务

### 方式A: 使用启动脚本（推荐）

```bash
./scripts/start_all_services.sh
```

### 方式B: 手动启动

**终端1 - 启动后端服务**:
```bash
# 使用项目启动脚本（默认端口5000）
python src/main.py -m http -p 5000

# 或者使用uvicorn（默认端口8000）
uvicorn src.main:app --reload --port 8000
```

**终端2 - 启动前端服务**:
```bash
cd magic-school-frontend
npm run dev
```

**注意**：
- 本地开发可以使用任意端口（如8000、5000等）
- 部署到Coze平台时，应用内部端口为5000，外部访问端口为80（自动处理）

---

## 步骤5: 访问应用

### 本地开发环境
- **前端地址**: http://localhost:5173
- **API文档**: http://localhost:5000/docs（如果使用5000端口）
- **API文档**: http://localhost:8000/docs（如果使用8000端口）
- **WebSocket测试**: ws://localhost:5000/ws/chat（如果使用5000端口）

### Coze部署环境
- **前端地址**: https://your-domain.coze.site
- **API文档**: https://your-domain.coze.site/docs
- **WebSocket测试**: wss://your-domain.coze.site/ws/chat

**注意**：Coze部署后无需指定端口，系统会自动处理。

---

## 🧪 测试功能

### 1. 测试用户认证

```bash
# 使用curl测试注册
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student1",
    "email": "student1@example.com",
    "password": "password123",
    "role": "student"
  }'

# 使用curl测试登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student1",
    "password": "password123"
  }'
```

### 2. 测试智能对话

```bash
# 使用WebSocket测试对话
wscat -c ws://localhost:8000/ws/chat
# 发送消息: {"message": "你好，我是魔法学校的学生"}
```

### 3. 运行单元测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_auth.py

# 查看测试覆盖率
pytest --cov=src --cov-report=html
```

---

## 📱 使用功能

### 学生端
1. 访问 http://localhost:5173
2. 注册/登录学生账户
3. 在聊天界面与AI助手对话
4. 查看学习进度和记忆记录

### 家长端
1. 注册家长账户
2. 关联学生账户
3. 查看学生的学习报告
4. 管理学生权限

### 教师端
1. 注册教师账户
2. 创建课程和作业
3. 批改学生作业
4. 生成学习报告

---

## 🔧 常见问题

### Q1: 数据库连接失败
**解决方案**:
1. 检查PostgreSQL是否运行: `sudo systemctl status postgresql`
2. 检查DATABASE_URL配置是否正确
3. 确保数据库已创建: `createdb magic_school`

### Q2: 前端无法连接后端
**解决方案**:
1. 检查后端是否运行: `curl http://localhost:8000/docs`
2. 检查CORS配置
3. 查看浏览器控制台错误信息

### Q3: API调用失败
**解决方案**:
1. 检查阿里云API Key是否正确
2. 检查网络连接
3. 查看后端日志: `tail -f logs/app.log`

### Q4: 测试失败
**解决方案**:
1. 确保所有依赖已安装: `pip install -r requirements.txt`
2. 数据库已初始化: `python scripts/init_database.py`
3. 清理测试缓存: `rm -rf .pytest_cache __pycache__`

---

## 📚 深入学习

### 查看完整文档
- [README.md](README.md) - 项目概述
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API文档
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - 部署指南
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - 开发指南

### 项目结构
```
src/
├── agents/       # AI智能体核心
├── api/          # REST API
├── auth/         # 认证授权
├── chat/         # 聊天模块
├── memory/       # 长期记忆
├── storage/      # 数据存储
└── main.py       # 应用入口
```

---

## 🎯 下一步

1. **自定义配置**: 编辑 `config/agent_llm_config.json` 调整AI模型参数
2. **添加功能**: 查看 `DEVELOPMENT_GUIDE.md` 了解如何添加新功能
3. **部署生产**: 查看 `DEPLOYMENT_GUIDE.md` 了解生产环境部署
4. **贡献代码**: Fork项目并提交Pull Request

---

## 💡 提示

- 开发模式启动使用 `--reload` 参数会自动重载代码
- 前端开发服务器默认端口 5173，如被占用可修改 `vite.config.ts`
- 生产部署前请修改所有默认密码和密钥
- 建议使用虚拟环境隔离Python依赖

---

## 🆘 获取帮助

如果遇到问题：
1. 查看日志文件: `logs/app.log`
2. 运行验证脚本: `./scripts/verify_release.sh`
3. 查看文档: `docs/` 目录下的相关文档
4. 运行测试: `pytest -v`

---

**祝您使用愉快！** 🎉
