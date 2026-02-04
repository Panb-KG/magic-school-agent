# 扣子IDE vs 阿里云ECS - 部署位置说明

## 🔍 当前状态澄清

### 您现在在哪里？

您正在**扣子编程IDE的云端环境**中，这是一个**临时沙箱**，用于开发和测试。

```
扣子IDE环境（当前）
├── /workspace/projects/  ← 项目代码在这里
│   ├── src/              ← 智能体代码
│   ├── config/           ← 配置文件
│   ├── magic-school-frontend/ ← 前端代码
│   └── ...
│
└── 沙箱环境  ← 服务运行在这里（扣子提供）
    ├── IP: 9.128.44.145（扣子内网）
    ├── 端口: 5000, 5173, 3000, 8765
    └── 特点: 临时环境，重启可能丢失数据
```

### 这是什么环境？

| 特性 | 扣子IDE环境 |
|------|-----------|
| **性质** | 云端开发沙箱 |
| **用途** | 代码开发和测试 |
| **持久性** | ❌ 临时，可能丢失 |
| **公网访问** | ⚠️ 受限 |
| **适合** | 开发、调试、测试 |
| **不适合** | 生产部署 |

---

## 🏠 您需要部署到哪里？

### 您需要在**您自己的阿里云ECS服务器**上部署！

```
您的阿里云ECS服务器（目标）
├── /workspace/projects/  ← 需要将代码上传到这里
│   ├── src/
│   ├── config/
│   ├── magic-school-frontend/
│   └── ...
│
└── 您的服务器
    ├── IP: 您服务器的公网IP
    ├── 端口: 5000, 5173, 3000, 8765
    └── 特点: 永久存储，稳定运行
```

### 这是您的生产环境

| 特性 | 阿里云ECS服务器 |
|------|---------------|
| **性质** | 您的云服务器 |
| **用途** | 生产环境，长期运行 |
| **持久性** | ✅ 永久存储 |
| **公网访问** | ✅ 完全可控 |
| **适合** | 生产部署、正式上线 |
| **配置** | 需要配置安全组、SSL等 |

---

## 📦 真正的部署步骤

### 第一步：从扣子IDE导出代码

在扣子IDE终端执行：

```bash
# 1. 创建代码压缩包
cd /workspace
tar -czf magic-school-project.tar.gz projects/

# 2. 下载到本地
# 扣子IDE会提供下载链接，点击下载
```

---

### 第二步：上传到阿里云ECS服务器

在您的电脑上执行：

```bash
# 方式1: 使用SCP上传
scp magic-school-project.tar.gz root@your-ecs-ip:/root/

# 方式2: 使用SFTP工具（如FileZilla）
# 上传文件到 /root/ 目录
```

---

### 第三步：在ECS服务器上部署

登录您的阿里云ECS服务器：

```bash
# SSH登录
ssh root@your-ecs-ip

# 解压代码
cd /root
tar -xzf magic-school-project.tar.gz

# 移动到项目目录
mv projects /workspace/

# 进入项目目录
cd /workspace/projects
```

---

### 第四步：安装依赖

```bash
# 1. 安装Python依赖
pip3 install -r requirements.txt

# 2. 安装Node.js依赖（如果没有）
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt-get install -y nodejs

# 3. 安装前端依赖
cd magic-school-frontend
npm install
cd ..
```

---

### 第五步：配置环境

```bash
# 1. 创建前端环境变量
cd /workspace/projects/magic-school-frontend
cat > .env << 'EOF'
VITE_BACKEND_URL=http://your-ecs-ip:5000
VITE_API_BASE_URL=http://your-ecs-ip:3000/api/v1
VITE_WS_URL=ws://your-ecs-ip:8765
EOF

# 2. 将 your-ecs-ip 替换为您的实际IP
```

---

### 第六步：启动服务

```bash
# 1. 启动API后端（端口3000）
cd /workspace/projects
nohup python3 scripts/mock_api_server.py > logs/api.log 2>&1 &
echo $! > logs/api.pid

# 2. 启动Agent服务（端口5000）
mkdir -p logs
nohup python3 src/main.py -m http -p 5000 > logs/agent.log 2>&1 &
echo $! > logs/agent.pid

# 3. 启动前端服务（端口5173）
cd magic-school-frontend
nohup npm run dev > ../logs/frontend.log 2>&1 &
echo $! > ../logs/frontend.pid
```

---

### 第七步：验证部署

```bash
# 1. 检查服务是否启动
ps aux | grep -E "mock_api|main.py|vite"

# 2. 检查端口监听
netstat -tlnp | grep -E "3000|5000|5173"

# 3. 测试服务
curl http://localhost:5000/health
curl http://localhost:5173
```

---

### 第八步：配置安全组

在阿里云ECS控制台：

1. 进入「安全组」
2. 添加入方向规则：

| 端口 | 说明 |
|------|------|
| 80 | HTTP |
| 443 | HTTPS |
| 3000 | API后端 |
| 5000 | Agent服务 |
| 5173 | 前端服务 |
| 8765 | WebSocket |

授权对象：`0.0.0.0/0`

---

### 第九步：访问您的网站

在浏览器访问：

```
http://your-ecs-ip:5173
```

使用测试账号登录：
- 学生: `student` / `password123`
- 家长: `parent` / `password123`

---

## 🎯 关键区别总结

| 项目 | 扣子IDE环境 | 阿里云ECS服务器 |
|------|-----------|---------------|
| **性质** | 临时沙箱 | 生产服务器 |
| **代码位置** | /workspace/projects | 需要上传 |
| **访问方式** | 临时端口 | 公网IP |
| **持久性** | ❌ 可能丢失 | ✅ 永久存储 |
| **适合场景** | 开发测试 | 生产部署 |
| **需要配置** | 无 | 安全组、SSL等 |

---

## 📝 完整部署清单

- [ ] 从扣子IDE导出代码
- [ ] 上传到阿里云ECS
- [ ] 解压代码到正确位置
- [ ] 安装Python依赖
- [ ] 安装Node.js依赖
- [ ] 配置环境变量
- [ ] 启动所有服务
- [ ] 配置安全组
- [ ] 验证服务运行
- [ ] 测试访问
- [ ] 配置域名（可选）
- [ ] 配置SSL（可选）

---

## 💡 简单说明

### 当前情况：
- 代码在**扣子IDE**（临时环境）
- 服务在**扣子沙箱**运行
- 适合**开发和测试**
- **不适合**生产使用

### 您需要做的：
- 将代码**导出**并上传到**您的ECS服务器**
- 在ECS上**安装依赖**
- 在ECS上**启动服务**
- 在ECS上**配置安全组**
- **然后**就可以通过公网访问了！

---

## 🆘 常见问题

### Q: 扣子IDE和我的ECS有什么关系？
A: 没有关系！扣子IDE只是开发环境，您的ECS是生产服务器，需要手动部署。

### Q: 代码在扣子IDE里，怎么到我的ECS？
A: 需要先从扣子IDE下载代码，然后上传到您的ECS服务器。

### Q: 我现在能访问服务吗？
A: 可以在扣子IDE内网访问，但无法从外部访问。需要部署到您的ECS后才能公网访问。

---

**总结：您的代码现在在扣子IDE的临时环境中，需要部署到您自己的阿里云ECS服务器才能正式上线！**
