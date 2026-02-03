# 魔法课桌智能体 - 后端部署报告

## 📅 部署时间
$(date '+%Y-%m-%d %H:%M:%S')

## ✅ 部署状态：成功

---

## 📊 服务状态

### 1. 智能体 API 服务器

- **状态**: ✅ 运行中
- **进程 ID**: 74
- **端口**: 5000
- **监听地址**: 0.0.0.0
- **健康检查**: ✅ 通过 (HTTP 200)
- **启动命令**: `python src/main.py -m http -p 5000`
- **访问地址**:
  - API: http://localhost:5000
  - 文档: http://localhost:5000/docs
  - 日志: /app/work/logs/bypass/app.log

### 2. Mock API 服务器

- **状态**: ✅ 运行中
- **进程 ID**: 115
- **端口**: 3000
- **监听地址**: 0.0.0.0
- **健康检查**: ✅ 通过 (HTTP 200)
- **启动命令**: `python3 scripts/mock_api_server.py`
- **访问地址**:
  - API: http://localhost:3000
  - 文档: http://localhost:3000/docs
  - 日志: logs/mock_api.log

---

## 🔌 API 接口

### 智能体 API (端口 5000)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /run | 非流式对话 |
| POST | /stream_run | 流式对话 |
| POST | /cancel/{run_id} | 取消对话 |
| GET | /docs | API 文档 |

### Mock API (端口 3000)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/auth/login | 用户登录 |
| POST | /api/v1/auth/register | 用户注册 |
| GET | /api/v1/auth/me | 获取用户信息 |
| GET | /api/v1/dashboard | 仪表盘数据 |
| GET | /api/v1/schedule | 课程表 |
| GET | /api/v1/achievements | 成就墙 |
| GET | /api/v1/homework | 作业列表 |
| GET | /docs | API 文档 |

---

## 🔐 测试账号

### 学生账号
- **用户名**: student
- **密码**: password123
- **角色**: student
- **功能**: 
  - 查看课程表
  - 查看作业
  - 与智能体对话
  - 查看成就

### 家长账号
- **用户名**: parent
- **密码**: password123
- **角色**: parent
- **功能**:
  - 查看孩子学习情况
  - 管理孩子账号
  - 奖励积分
  - 审核作业

---

## 🧪 功能测试

### ✅ 智能体 API 测试
- [x] 服务启动成功
- [x] 端口监听正常
- [x] API 文档可访问
- [x] 健康检查通过

### ✅ Mock API 测试
- [x] 服务启动成功
- [x] 端口监听正常
- [x] API 文档可访问
- [x] 登录功能正常

---

## 📋 管理命令

### 查看服务状态
```bash
ps aux | grep python
netstat -tlnp | grep -E "(5000|3000)"
```

### 查看日志
```bash
# 智能体 API 日志
tail -f /app/work/logs/bypass/app.log

# Mock API 日志
tail -f logs/mock_api.log
```

### 停止服务
```bash
# 停止智能体 API
kill 74

# 停止 Mock API
kill 115

# 停止所有服务
pkill -f "python.*main.py"
pkill -f "python.*mock_api"
```

### 重启服务
```bash
# 重启智能体 API
pkill -f "python.*main.py"
sleep 2
bash scripts/http_run.sh -p 5000

# 重启 Mock API
pkill -f "python.*mock_api"
sleep 2
python3 scripts/mock_api_server.py &
```

---

## 🌐 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 智能体 API | http://localhost:5000 | 核心智能体服务 |
| API 文档 | http://localhost:5000/docs | Swagger 文档 |
| Mock API | http://localhost:3000 | 开发调试接口 |
| Mock 文档 | http://localhost:3000/docs | Swagger 文档 |
| 前端界面 | http://localhost:5173 | React 前端应用 |

---

## 📊 性能监控

### 资源使用情况
```bash
# 查看进程资源使用
ps aux | grep python

# 查看端口连接
netstat -an | grep -E "(5000|3000)" | wc -l

# 查看系统负载
uptime
```

---

## 🔧 配置文件

| 配置文件 | 路径 | 说明 |
|---------|------|------|
| 智能体配置 | config/agent_llm_config.json | LLM 模型配置 |
| 环境变量 | .env | 系统环境变量 |

---

## 📝 注意事项

1. **防火墙设置**: 确保端口 5000 和 3000 已开放
2. **数据库**: 如需使用真实数据库，请配置 PostgreSQL
3. **对象存储**: 如需存储文件，请配置 S3 兼容存储
4. **日志管理**: 定期清理日志文件避免磁盘占满
5. **性能优化**: 生产环境建议使用 gunicorn + uvicorn

---

## 🚀 生产环境建议

### 使用 Gunicorn 启动
```bash
pip install gunicorn

gunicorn src.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:5000 \
  --timeout 120 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
```

### 使用 Systemd 管理
```bash
# 创建 systemd 服务文件
sudo vim /etc/systemd/system/magic-school.service

# 启用服务
sudo systemctl enable magic-school
sudo systemctl start magic-school
sudo systemctl status magic-school
```

---

## 🎯 下一步

1. ✅ 后端服务已部署完成
2. 📱 访问前端: http://localhost:5173
3. 🔐 登录账号: student / password123
4. 💬 测试智能体对话功能
5. 📚 查看 API 文档: http://localhost:5000/docs

---

## 📞 技术支持

- API 文档: http://localhost:5000/docs
- Mock 文档: http://localhost:3000/docs
- 部署日志: logs/deployment_report.md
- 系统日志: /app/work/logs/bypass/app.log

---

**部署完成时间**: $(date '+%Y-%m-%d %H:%M:%S')
**部署状态**: ✅ 成功
