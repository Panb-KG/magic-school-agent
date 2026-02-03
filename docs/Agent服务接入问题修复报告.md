# Agent 服务接入问题修复报告

## 🔍 问题诊断

### 问题描述
用户在本地终端IDE调试前端时，无法连接到后端的Agent服务。

### 根本原因
端口5000上的Agent服务（`src/main.py`）**未配置CORS中间件**，导致浏览器无法从前端跨域调用Agent API。

---

## ✅ 修复内容

### 1. 添加CORS支持

**文件**: `src/main.py`

**修改详情**:

#### (1) 导入CORSMiddleware
```python
from fastapi.middleware.cors import CORSMiddleware
```

#### (2) 配置CORS中间件
在 `app = FastAPI()` 之后添加：
```python
# ============ CORS 配置 ============
# 允许前端跨域访问 agent 服务
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # 如果需要支持生产环境，添加生产域名
        # "https://your-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. 重启Agent服务

```bash
# 停止旧服务
kill <进程PID>

# 启动新服务（带CORS支持）
cd /workspace/projects
mkdir -p logs
nohup python src/main.py -m http -p 5000 > logs/agent_service.log 2>&1 &
```

### 3. 验证CORS配置

```bash
# 测试CORS预检请求
curl -s -X OPTIONS http://localhost:5000/run \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization" \
  -I
```

**预期响应**:
```
HTTP/1.1 200 OK
access-control-allow-origin: http://localhost:5173
access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
access-control-allow-credentials: true
access-control-allow-headers: Content-Type,Authorization
```

---

## 🧪 测试验证

### 方式 1: 使用测试页面（推荐）

访问测试页面：
```
http://101.126.128.57:5173/agent-test.html
```

这个页面会自动测试：
1. ✅ Agent服务健康检查
2. ✅ CORS配置验证
3. ✅ Agent对话功能
4. ✅ API后端连接

### 方式 2: 本地IDE测试

如果用户在本地运行前端，需要修改前端配置连接到远程服务器。

**方案A**: 使用环境变量
```bash
# 在本地终端设置
cd magic-school-frontend
echo "VITE_BACKEND_URL=http://101.126.128.57:5000" > .env
echo "VITE_API_BASE_URL=http://101.126.128.57:3000/api/v1" >> .env
echo "VITE_WS_URL=ws://101.126.128.57:8765" >> .env
```

**方案B**: 使用Vite代理（推荐）
在 `vite.config.ts` 中配置：
```typescript
export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/agent': {
        target: 'http://101.126.128.57:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/agent/, '')
      },
      '/api': {
        target: 'http://101.126.128.57:3000',
        changeOrigin: true
      }
    }
  }
})
```

然后修改 `chatService.ts`：
```typescript
// 使用代理地址
const BACKEND_URL = '/agent';  // 替换原来的 http://localhost:5000
```

### 方式 3: 直接在服务器前端测试

访问服务器上的前端：
```
http://101.126.128.57:5173/login
```

使用测试账号登录后，在智能对话页面测试Agent功能。

---

## 🔌 服务状态

### 当前运行的服务

| 服务 | 端口 | 状态 | 说明 |
|------|------|------|------|
| Agent服务 | 5000 | ✅ 运行中 | 已配置CORS |
| API后端 | 3000 | ✅ 运行中 | Mock API |
| 前端服务 | 5173 | ✅ 运行中 | 开发服务器 |
| WebSocket | 8765 | ✅ 运行中 | 实时通信 |

### 服务管理命令

```bash
# 查看Agent服务日志
tail -f /workspace/projects/logs/agent_service.log

# 查看所有服务进程
ps aux | grep -E "vite|uvicorn|python.*main.py"

# 重启Agent服务
kill $(ps aux | grep "main.py" | grep -v grep | awk '{print $2}')
cd /workspace/projects
nohup python src/main.py -m http -p 5000 > logs/agent_service.log 2>&1 &
```

---

## 🌐 网络配置

### 本地开发环境

如果用户在本地IDE调试前端，可以有以下选择：

#### 选项1: 本地前端 + 远程后端（需要CORS）
- ✅ 已配置CORS，支持跨域访问
- 前端配置: `VITE_BACKEND_URL=http://101.126.128.57:5000`

#### 选项2: 服务器前端 + 远程后端
- 访问: `http://101.126.128.57:5173`
- 所有服务在同一网络，无跨域问题

#### 选项3: SSH端口转发（安全）
```bash
# 在本地终端运行
ssh -L 5000:localhost:5000 -L 3000:localhost:3000 root@101.126.128.57

# 然后本地前端配置使用localhost
VITE_BACKEND_URL=http://localhost:5000
VITE_API_BASE_URL=http://localhost:3000/api/v1
```

---

## 🎯 快速验证步骤

1. **访问测试页面**:
   ```
   http://101.126.128.57:5173/agent-test.html
   ```

2. **点击「一键完整测试」按钮**

3. **检查测试结果**:
   - ✅ 所有测试通过 → 可以正常使用
   - ❌ 部分失败 → 查看具体错误信息

4. **如果本地IDE调试**:
   - 方案A: 修改本地环境变量连接到远程服务器
   - 方案B: 配置Vite代理
   - 方案C: 使用SSH端口转发

---

## 📝 测试账号

### 学生账号
- **用户名**: `student`
- **密码**: `password123`

### 家长账号
- **用户名**: `parent`
- **密码**: `password123`

---

## 🐛 常见问题

### Q1: 本地IDE调试前端，仍然无法连接Agent

**可能原因**:
1. 环境变量未正确配置
2. 防火墙阻止了端口5000访问

**解决方案**:
1. 检查 `.env` 文件配置
2. 尝试使用SSH端口转发（见上文）
3. 使用服务器前端测试（http://101.126.128.57:5173）

### Q2: 测试页面显示CORS错误

**解决方案**:
1. 确认Agent服务已重启
2. 检查Agent服务日志: `tail -f logs/agent_service.log`
3. 重启Agent服务

### Q3: Agent对话功能报错

**检查项**:
1. Agent服务是否正常运行: `curl http://localhost:5000/health`
2. 查看Agent日志: `tail -f /app/work/logs/bypass/app.log`
3. 检查是否超时（默认15分钟）

---

## 📚 相关文档

- **Agent服务文档**: `http://101.126.128.57:5000/docs`
- **API后端文档**: `http://101.126.128.57:3000/docs`
- **前端服务启动**: `magic-school-frontend/前端服务启动成功.md`

---

## ✨ 修复总结

✅ **问题**: Agent服务未配置CORS，导致浏览器无法跨域访问
✅ **修复**: 添加CORSMiddleware配置
✅ **验证**: CORS测试通过，支持跨域请求
✅ **测试**: 提供完整的测试工具页面

---

**🎉 Agent服务现在可以从互联网调用了！**

使用测试页面验证: http://101.126.128.57:5173/agent-test.html
