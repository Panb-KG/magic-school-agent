# ⚡ 魔法课桌智能体 - 部署快速开始（5分钟上线）

## 🎯 两种部署方式

| 方式 | 时间 | 成本 | 适用场景 |
|------|------|------|----------|
| **扣子平台** | 5分钟 | 免费/低成本 | 快速测试、演示 |
| **阿里云ECS** | 30分钟 | ¥190/月 | 正式生产 |

---

## 🚀 方式一：扣子平台部署（推荐新手）

### 前置准备

```bash
# 1. 确认代码状态
cd /workspace/projects
git status

# 2. 运行测试验证
python scripts/test_full_functionality.py

# 预期输出：✅ 通过率: 100.00%
```

---

### 步骤1：准备环境变量（2分钟）

创建 `.env.production` 文件：

```bash
cat > .env.production << 'EOF'
# ⚠️ 必须修改为你的真实API Key
DASHSCOPE_API_KEY=sk-your-real-api-key-here
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# ⚠️ 必须修改为强随机字符串（至少32位）
JWT_SECRET=change-this-to-a-very-long-random-string-at-least-32-chars

DEBUG=False
LOG_LEVEL=INFO
EOF
```

**获取API Key**：
1. 访问阿里云百炼控制台：https://bailian.console.aliyun.com/
2. 创建API-KEY
3. 复制API Key到上面的配置

---

### 步骤2：推送到GitHub（2分钟）

```bash
# 如果还没有GitHub仓库
# 1. 访问 https://github.com/new
# 2. 创建仓库：magic-school-agent

# 添加远程仓库（替换你的用户名）
git remote add origin https://github.com/your-username/magic-school-agent.git

# 推送代码
git add .
git commit -m "chore: 准备部署"
git push -u origin main
```

---

### 步骤3：扣子平台部署（3分钟）

#### 3.1 登录扣子平台
访问：https://www.coze.cn/ 或 https://coze.com/

#### 3.2 创建扣子编程项目
1. 点击"创建" → "扣子编程"
2. 项目名称：魔法课桌学习助手
3. 连接GitHub仓库：选择 `magic-school-agent`

#### 3.3 配置构建
- **运行语言**：Python 3.11
- **运行命令**：
  ```bash
  pip install -r requirements.txt
  bash scripts/http_run.sh -p 5000
  ```

#### 3.4 配置环境变量
在部署界面添加：

```bash
DASHSCOPE_API_KEY=sk-your-real-api-key-here
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
JWT_SECRET=change-this-to-a-very-long-random-string-at-least-32-chars
DEBUG=False
LOG_LEVEL=INFO
```

#### 3.5 开始部署
点击"开始部署"，等待3-5分钟。

---

### 步骤4：验证部署（1分钟）

```bash
# 替换为实际的域名
curl https://your-domain.coze.site/health

# 预期输出：
# {"status":"ok","message":"Service is running"}
```

浏览器访问：
```
https://your-domain.coze.site/docs
```

---

## 🏗️ 方式二：阿里云ECS部署（推荐生产）

### 前置准备

- 阿里云账号
- ECS服务器（2核4G）
- PostgreSQL数据库（RDS或自建）

---

### 步骤1：购买ECS（5分钟）

1. 访问阿里云ECS控制台
2. 创建实例：
   - 规格：2核4G
   - 系统：Ubuntu 22.04
   - 带宽：3 Mbps
3. 记录服务器IP和密码

---

### 步骤2：连接服务器（1分钟）

```bash
ssh root@your-server-ip
# 输入密码
```

---

### 步骤3：安装依赖（5分钟）

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装依赖
sudo apt install python3.11 python3.11-venv python3-pip nginx postgresql-client git -y
```

---

### 步骤4：克隆项目（2分钟）

```bash
cd /opt
git clone https://github.com/your-username/magic-school-agent.git
cd magic-school-agent

# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

---

### 步骤5：配置环境（5分钟）

```bash
# 创建环境变量文件
cat > .env.production << 'EOF'
DASHSCOPE_API_KEY=sk-your-real-api-key-here
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
JWT_SECRET=change-this-to-a-very-long-random-string-at-least-32-chars
PGDATABASE_URL=postgresql://user:password@localhost:5432/magic_school
DEBUG=False
LOG_LEVEL=INFO
EOF

# 初始化数据库
python scripts/init_database.py
```

---

### 步骤6：配置Nginx（5分钟）

```bash
# 创建配置
sudo nano /etc/nginx/sites-available/magic-school

# 添加以下内容：
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# 启用配置
sudo ln -s /etc/nginx/sites-available/magic-school /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

### 步骤7：配置SSL（5分钟）

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 申请证书
sudo certbot --nginx -d your-domain.com
```

---

### 步骤8：启动服务（2分钟）

```bash
# 创建系统服务
sudo nano /etc/systemd/system/magic-school.service

# 添加内容：
[Unit]
Description=Magic School Agent Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/magic-school-agent
Environment="PATH=/opt/magic-school-agent/venv/bin"
ExecStart=/opt/magic-school-agent/venv/bin/python /opt/magic-school-agent/src/main.py -m http -p 5000
Restart=always

[Install]
WantedBy=multi-user.target

# 启动服务
sudo systemctl daemon-reload
sudo systemctl start magic-school
sudo systemctl enable magic-school
```

---

### 步骤9：验证部署（1分钟）

```bash
# 健康检查
curl http://your-domain.com/health

# 查看日志
sudo journalctl -u magic-school -f
```

---

## ✅ 部署后测试

### 1. 健康检查
```bash
curl https://your-domain.com/health
```

### 2. API文档
浏览器访问：
```
https://your-domain.com/docs
```

### 3. 测试对话
```bash
curl -X POST https://your-domain.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好",
    "session_id": "test",
    "user_id": "test"
  }'
```

### 4. 测试注册
```bash
curl -X POST https://your-domain.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_student",
    "password": "password123",
    "role": "student",
    "student_name": "测试学生",
    "grade": "3年级"
  }'
```

---

## 🆘 常见问题

### Q1: 扣子部署失败
**A**: 检查以下几点：
- API Key是否正确
- 环境变量名称是否使用 `DASHSCOPE_` 而不是 `COZE_`
- 代码是否成功推送到GitHub

### Q2: ECS服务无法启动
**A**: 查看日志：
```bash
sudo journalctl -u magic-school -n 50
```

### Q3: AI不工作
**A**: 检查API Key配置：
```bash
# 检查环境变量
cat .env.production | grep DASHSCOPE
```

### Q4: 无法访问域名
**A**: 检查：
- DNS是否生效
- 安全组端口是否开放
- Nginx是否正常运行

---

## 💡 最佳实践

### 1. 环境变量
- ✅ 使用强随机字符串作为JWT_SECRET
- ✅ 不要在代码中硬编码密钥
- ✅ 生产环境关闭DEBUG模式

### 2. 数据库
- ✅ 定期备份数据库
- ✅ 使用连接池
- ✅ 添加索引优化查询

### 3. 监控
- ✅ 配置日志监控
- ✅ 设置告警通知
- ✅ 定期检查系统资源

### 4. 安全
- ✅ 启用HTTPS
- ✅ 配置防火墙
- ✅ 禁用root远程登录
- ✅ 定期更新系统

---

## 📊 成本对比

| 项目 | 扣子平台 | 阿里云ECS |
|------|----------|-----------|
| 平台费用 | 免费 | ¥120/月 |
| 数据库 | 免费 | ¥50/月 |
| 域名 | 免费 | ¥10/年 |
| SSL证书 | 免费 | 免费 |
| 大模型 | 按需 | 按需 |
| **合计** | **¥10-50/月** | **¥190/月** |

---

## 🎯 推荐部署路径

### 开发/测试阶段
```
扣子平台部署 → 快速验证 → 迭代优化
```

### 正式上线
```
阿里云ECS部署 → 性能优化 → 监控运维
```

---

## 📚 详细文档

- [完整部署指南](DEPLOYMENT_GUIDE_COMPLETE.md) - 详细步骤和配置
- [扣子平台部署指南](docs/扣子平台部署指南.md) - 扣子平台详解
- [扣子平台快速参考卡](docs/扣子平台部署快速参考卡.md) - 快速参考
- [API文档](API_DOCUMENTATION.md) - 完整API文档

---

## 📞 获取帮助

- **文档**: `/workspace/projects/docs/`
- **日志**: `/workspace/projects/logs/`
- **配置**: `/workspace/projects/config/`

---

**🎉 开始部署吧！选择适合你的方式，5-30分钟内即可上线！**
