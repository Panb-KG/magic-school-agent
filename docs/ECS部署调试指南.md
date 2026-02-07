# 🪄 魔法课桌智能体 - 阿里云 ECS 部署与调试指南

## 📋 部署概览

本文档指导您在阿里云 ECS 服务器上部署和调试魔法课桌学习助手智能体后端服务。

---

## ✅ 部署状态

**部署时间**: 2025-02-07
**服务器**: 阿里云 ECS (101.126.128.57)
**服务状态**: ✅ 正常运行
**服务端口**: 5000
**PID**: 341

---

## 🚀 部署步骤

### 1. 检查服务器环境

#### 检查 Python 版本

```bash
python3 --version
# 输出: Python 3.12.3
```

#### 检查 Pip 版本

```bash
pip3 --version
# 输出: pip 24.0
```

#### 检查环境变量

```bash
env | grep COZE_
```

确认以下环境变量已设置：
- `COZE_WORKLOAD_IDENTITY_API_KEY`
- `COZE_INTEGRATION_MODEL_BASE_URL`
- `COZE_WORKSPACE_PATH`
- `COZE_PROJECT_ID`
- `COZE_PROJECT_SPACE_ID`

---

### 2. 安装 Python 依赖

```bash
cd /workspace/projects
pip install -r requirements.txt
```

关键依赖已安装：
- ✅ langchain 1.0.3
- ✅ langchain-openai 1.0.1
- ✅ fastapi 0.121.2
- ✅ uvicorn 0.38.0

---

### 3. 配置模型配置

配置文件位置：`/workspace/projects/config/agent_llm_config.json`

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
    "sp": "系统提示词...",
    "tools": ["工具列表"]
}
```

---

### 4. 启动 Agent 服务

#### 使用管理脚本启动（推荐）

```bash
cd /workspace/projects
./scripts/manage_agent.sh start
```

#### 手动启动

```bash
cd /workspace/projects
python3 src/main.py -m http -p 5000
```

---

### 5. 验证服务启动

#### 检查服务状态

```bash
./scripts/manage_agent.sh status
```

输出示例：
```
==========================================
魔法课桌智能体 - 服务管理
==========================================

📊 服务状态检查...

✅ 服务正在运行
PID: 341
端口: 5000

✅ 端口 5000 正在监听

健康检查:
✅ 服务健康
响应: {"status":"ok","message":"Service is running"}

==========================================
```

#### 健康检查

```bash
curl http://localhost:5000/health
```

输出：
```json
{"status":"ok","message":"Service is running"}
```

#### 查看 API 文档

访问：http://localhost:5000/docs

---

## 🧪 服务测试

### 测试 1: 健康检查

```bash
curl http://localhost:5000/health
```

### 测试 2: 对话接口

```bash
curl -X POST http://localhost:5000/run \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好",
    "session_id": "test_session_001",
    "user_id": "test_user"
  }'
```

预期响应：
```json
{
  "messages": [
    {
      "content": "你好呀，小巫师！...",
      "type": "ai"
    }
  ],
  "run_id": "..."
}
```

### 测试 3: 时间查询

```bash
curl -X POST http://localhost:5000/run \
  -H "Content-Type: application/json" \
  -d '{
    "message": "现在几点了？",
    "session_id": "test_session_002",
    "user_id": "test_user"
  }'
```

### 测试 4: 创建学生

```bash
curl -X POST http://localhost:5000/run \
  -H "Content-Type: application/json" \
  -d '{
    "message": "创建学生档案：姓名：张小明，年级：三年级，班级：二班，学校：魔法小学，家长联系方式：13800138000，昵称：小明",
    "session_id": "test_session_003",
    "user_id": "test_user"
  }'
```

---

## 🛠️ 服务管理

### 启动服务

```bash
./scripts/manage_agent.sh start
```

### 停止服务

```bash
./scripts/manage_agent.sh stop
```

### 重启服务

```bash
./scripts/manage_agent.sh restart
```

### 查看状态

```bash
./scripts/manage_agent.sh status
```

### 查看日志

```bash
# 查看最近 50 行日志
./scripts/manage_agent.sh logs

# 实时监控日志
./scripts/manage_agent.sh monitor
```

---

## 📊 监控与日志

### 日志文件位置

| 日志类型 | 位置 | 说明 |
|---------|------|------|
| 服务日志 | `/var/log/magic-school-agent.log` | Agent 服务日志 |
| 应用日志 | `/app/work/logs/bypass/app.log` | LangGraph 日志 |
| 临时日志 | `/tmp/agent.log` | 临时调试日志 |

### 查看实时日志

```bash
tail -f /var/log/magic-school-agent.log
```

### 搜索错误日志

```bash
grep -i "error" /var/log/magic-school-agent.log
```

### 搜索工具调用

```bash
grep "tool_calls" /var/log/magic-school-agent.log
```

---

## 🔧 故障排查

### 问题 1: 端口被占用

**症状**: `Address already in use`

**解决方案**:

```bash
# 查找占用端口的进程
lsof -i :5000

# 终止进程
kill -9 <PID>

# 重启服务
./scripts/manage_agent.sh restart
```

### 问题 2: 服务不响应

**症状**: curl 请求超时

**解决方案**:

```bash
# 检查服务状态
./scripts/manage_agent.sh status

# 查看日志
./scripts/manage_agent.sh logs

# 重启服务
./scripts/manage_agent.sh restart
```

### 问题 3: 依赖缺失

**症状**: `ModuleNotFoundError`

**解决方案**:

```bash
# 重新安装依赖
cd /workspace/projects
pip install -r requirements.txt
```

### 问题 4: 环境变量缺失

**症状**: 服务启动失败或功能异常

**解决方案**:

```bash
# 检查环境变量
env | grep COZE_

# 如需设置，编辑 ~/.bashrc
nano ~/.bashrc

# 添加以下行（替换为实际值）
export COZE_WORKLOAD_IDENTITY_API_KEY="your_api_key"
export COZE_INTEGRATION_MODEL_BASE_URL="your_base_url"

# 重新加载配置
source ~/.bashrc
```

---

## 🌐 访问配置

### 公网访问

服务器 IP: `101.126.128.57`
服务端口: `5000`

**注意**: 需要在阿里云安全组中开放 5000 端口

配置步骤：
1. 登录阿里云 ECS 控制台
2. 找到实例安全组
3. 添加入站规则：
   - 端口范围：`5000/5000`
   - 授权对象：`0.0.0.0/0`（或特定 IP）

### 内网访问

```bash
curl http://101.126.128.57:5000/health
```

### API 基础地址

```
http://101.126.128.57:5000
```

### API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/run` | POST | 对话接口 |
| `/stream_run` | POST | 流式对话 |
| `/cancel/{run_id}` | POST | 取消执行 |
| `/docs` | GET | API 文档 |

---

## 📝 进阶配置

### 自定义端口

```bash
# 修改启动命令中的端口
python3 src/main.py -m http -p <YOUR_PORT>
```

### 启用 HTTPS

使用 Nginx 反向代理：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 性能优化

增加 Worker 数量：

```bash
python3 src/main.py -m http -p 5000 --workers 4
```

---

## 📚 相关文档

- [项目 README](../README.md)
- [快速部署指南](快速部署指南.md)
- [后端 API 文档](后端API完整文档-Figma设计用.md)
- [GitHub 推送指南](GITHUB推送指南.md)

---

## 🆘 技术支持

如遇问题，请：

1. 查看日志：`./scripts/manage_agent.sh logs`
2. 检查服务状态：`./scripts/manage_agent.sh status`
3. 查看本文档的故障排查部分

---

**部署完成时间**: 2025-02-07
**服务状态**: ✅ 正常运行
**维护者**: Magic School Team
