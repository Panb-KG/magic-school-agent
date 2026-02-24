# 🚀 魔法课桌智能体 - 生产环境部署完整指南

## 📋 部署概览

本指南提供两种部署方案供选择：

| 部署方案 | 难度 | 成本 | 适用场景 | 推荐度 |
|---------|------|------|----------|--------|
| **方案一：扣子平台部署** | ⭐ 简单 | 免费/低成本 | 快速上线、测试 | ⭐⭐⭐⭐⭐ |
| **方案二：阿里云ECS部署** | ⭐⭐⭐ 中等 | ¥190/月 | 生产环境、完全控制 | ⭐⭐⭐⭐ |

---

## 🎯 推荐部署流程

### 首次部署：选择扣子平台（5分钟上线）
- ✅ 无需服务器
- ✅ 自动HTTPS
- ✅ 免费域名
- ✅ 一键部署

### 正式上线：选择阿里云ECS
- ✅ 完全控制
- ✅ 自定义域名
- ✅ 高性能
- ✅ 可扩展

---

## 方案一：扣子平台部署（推荐）

### 前置条件

- ✅ 扣子平台账号（免费注册）
- ✅ 阿里云百炼API密钥
- ✅ 当前项目代码（已完成回滚和修复）

---

### 步骤 1：准备项目

#### 1.1 确认代码状态

```bash
cd /workspace/projects

# 检查Git状态



# 确认当前分支
git branch

# 确认最新提交
git log -1
```

#### 1.2 运行测试验证

```bash
# 运行完整功能测试
python scripts/test_full_functionality.py

# 预期输出：
# ✅ 通过率: 100.00%
```

#### 1.3 检查配置文件

```bash
# 检查Agent配置
cat config/agent_llm_config.json

# 确认关键配置：
# - model: "doubao-seed-1-6-251015"
# - tools: 工具列表
# - sp: 系统提示词
```

---

### 步骤 2：准备环境变量

创建 `.env.production` 文件：

```bash
cd /workspace/projects
cat > .env.production << 'EOF'
# JWT密钥（必须修改为强随机字符串）
JWT_SECRET=your-super-secret-jwt-key-change-in-production-min-32-chars

# 阿里云百炼API配置（⚠️ 注意命名）
DASHSCOPE_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 数据库配置（扣子平台自动提供）
# PGDATABASE_URL=自动配置

# 调试模式
DEBUG=False

# 日志级别
LOG_LEVEL=INFO

# 会话配置
SESSION_TIMEOUT=86400

# 文件存储（可选）
# STORAGE_BUCKET=magic-school-assets
# STORAGE_REGION=oss-cn-hangzhou

# 聊天配置
MAX_HISTORY_MESSAGES=40
DEFAULT_TEMPERATURE=0.7
EOF
```

**⚠️ 重要提醒**：
- ✅ 使用 `DASHSCOPE_API_KEY`（标准命名）
- ✅ 使用 `OPENAI_BASE_URL`（标准命名）
- ❌ 不要使用 `COZE_WORKLOAD_IDENTITY_API_KEY`
- ❌ 不要使用 `COZE_INTEGRATION_MODEL_BASE_URL`

---

### 步骤 3：推送到GitHub

#### 3.1 创建GitHub仓库（如果还没有）

1. 访问 https://github.com/new
2. 创建新仓库：`magic-school-agent`
3. 选择公开或私有
4. 不要初始化README（已有）

#### 3.2 推送代码

```bash
cd /workspace/projects

# 添加远程仓库
git remote add origin https://github.com/your-username/magic-school-agent.git

# 或者如果已存在
git remote set-url origin https://github.com/your-username/magic-school-agent.git

# 推送代码
git add .
git commit -m "chore: 准备生产环境部署"
git push -u origin main
```

---

### 步骤 4：扣子平台部署

#### 4.1 登录扣子平台

访问：https://www.coze.cn/ 或 https://coze.com/

#### 4.2 创建扣子编程项目

1. 点击"创建" → "扣子编程"
2. 填写项目信息：
   - **项目名称**: 魔法课桌学习助手
   - **项目描述**: 面向小学生和家长的魔法风格学习管理智能体
   - **项目图标**: 上传 `assets/魔法书AI核.jpg`

3. 点击"创建"

#### 4.3 配置代码仓库

1. 选择"连接GitHub仓库"
2. 授权GitHub访问
3. 选择仓库：`magic-school-agent`
4. 选择分支：`main`

#### 4.4 配置构建选项

**运行环境**：
- 运行语言：Python 3.11
- 运行命令：
  ```bash
  pip install -r requirements.txt
  bash scripts/http_run.sh -p 5000
  ```

**端口配置**：
- 应用内部端口：`5000`
- 外部访问端口：`80`（自动配置）

#### 4.5 配置环境变量

在部署界面的"环境变量"中添加：

```bash
# JWT密钥（必须修改）
JWT_SECRET=your-super-secret-jwt-key-change-in-production-min-32-chars

# 阿里云百炼API密钥
DASHSCOPE_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 其他配置
DEBUG=False
LOG_LEVEL=INFO
```

#### 4.6 开始部署

1. 点击"开始部署"
2. 等待3-5分钟
3. 部署成功后会获得访问URL

---

### 步骤 5：验证部署

#### 5.1 健康检查

```bash
# 替换为实际的域名
curl https://your-domain.coze.site/health

# 预期输出：
# {"status":"ok","message":"Service is running"}
```

#### 5.2 查看API文档

浏览器打开：
```
https://your-domain.coze.site/docs
```

#### 5.3 测试对话

```bash
curl -X POST https://your-domain.coze.site/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好",
    "session_id": "test",
    "user_id": "test"
  }'
```

#### 5.4 测试注册和登录

```bash
# 测试注册
curl -X POST https://your-domain.coze.site/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_student",
    "password": "password123",
    "role": "student",
    "student_name": "测试学生",
    "grade": "3年级"
  }'

# 测试登录
curl -X POST https://your-domain.coze.site/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_student",
    "password": "password123"
  }'
```

---

### 步骤 6：配置自定义域名（可选）

#### 6.1 在扣子平台配置

1. 进入项目设置
2. 选择"域名管理"
3. 添加自定义域名

#### 6.2 配置DNS

在域名DNS管理中添加CNAME记录：

| 记录类型 | 主机记录 | 记录值 |
|---------|---------|--------|
| CNAME | @ | your-domain.coze.site |

#### 6.3 等待DNS生效

通常需要10-30分钟。

---

## 方案二：阿里云ECS部署

### 前置条件

- ✅ 阿里云账号
- ✅ ECS服务器（推荐2核4G）
- ✅ PostgreSQL数据库（可选RDS）
- ✅ 域名（可选）

---

### 步骤 1：购买ECS服务器

#### 1.1 选择配置

**推荐配置**：
- 实例规格：2核 vCPU
- 内存：4 GiB
- 操作系统：Ubuntu 22.04 LTS
- 带宽：3 Mbps

#### 1.2 购买

1. 访问阿里云ECS控制台
2. 选择"创建实例"
3. 选择配置
4. 设置密码（记住！）
5. 购买

---

### 步骤 2：配置安全组

#### 2.1 添加入站规则

| 协议类型 | 端口范围 | 授权对象 | 描述 |
|---------|---------|---------|------|
| 自定义TCP | 22/22 | 您的IP | SSH |
| 自定义TCP | 80/80 | 0.0.0.0/0 | HTTP |
| 自定义TCP | 443/443 | 0.0.0.0/0 | HTTPS |
| 自定义TCP | 5000/5000 | 0.0.0.0/0 | Agent服务 |

#### 2.2 保存配置

---

### 步骤 3：连接服务器

```bash
# SSH连接
ssh root@your-server-ip

# 输入密码
```

---

### 步骤 4：安装依赖

#### 4.1 更新系统

```bash
sudo apt update
sudo apt upgrade -y
```

#### 4.2 安装Python和工具

```bash
# 安装Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# 安装Nginx
sudo apt install nginx -y

# 安装PostgreSQL客户端
sudo apt install postgresql-client -y

# 安装Git
sudo apt install git -y
```

---

### 步骤 5：克隆项目

```bash
# 克隆项目
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

### 步骤 6：配置环境变量

```bash
# 创建环境变量文件
cat > /opt/magic-school-agent/.env.production << 'EOF'
# JWT密钥（必须修改）
JWT_SECRET=your-super-secret-jwt-key-change-in-production

# 阿里云百炼API配置
DASHSCOPE_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 数据库配置（如果有RDS）
PGDATABASE_URL=postgresql://user:password@your-rds-endpoint:5432/magic_school

# 其他配置
DEBUG=False
LOG_LEVEL=INFO
EOF
```

---

### 步骤 7：配置数据库

#### 7.1 创建RDS实例（推荐）

1. 访问阿里云RDS控制台
2. 创建PostgreSQL实例
3. 创建数据库：`magic_school`
4. 获取连接信息

#### 7.2 初始化数据库

```bash
cd /opt/magic-school-agent
source venv/bin/activate

# 运行初始化脚本
python scripts/init_database.py
```

---

### 步骤 8：配置Nginx

#### 8.1 创建配置文件

```bash
sudo nano /etc/nginx/sites-available/magic-school
```

#### 8.2 添加配置内容

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为您的域名

    # API和Agent服务
    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket支持
    location /ws {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

#### 8.3 启用配置

```bash
sudo ln -s /etc/nginx/sites-available/magic-school /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

### 步骤 9：配置SSL证书

#### 9.1 安装Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

#### 9.2 申请证书

```bash
sudo certbot --nginx -d your-domain.com
```

#### 9.3 配置自动续期

```bash
sudo certbot renew --dry-run
```

---

### 步骤 10：配置系统服务

#### 10.1 创建服务文件

```bash
sudo nano /etc/systemd/system/magic-school.service
```

#### 10.2 添加服务配置

```ini
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
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 10.3 启动服务

```bash
sudo systemctl daemon-reload
sudo systemctl start magic-school
sudo systemctl enable magic-school
sudo systemctl status magic-school
```

---

### 步骤 11：验证部署

#### 11.1 健康检查

```bash
curl http://localhost:5000/health

# 或公网
curl http://your-domain.com/health
```

#### 11.2 查看日志

```bash
sudo journalctl -u magic-school -f
```

#### 11.3 访问应用

浏览器打开：
```
https://your-domain.com
```

---

## 🛡️ 安全配置

### 1. 防火墙配置

```bash
# 启用防火墙
sudo ufw enable

# 允许必要端口
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# 拒绝其他端口
sudo ufw default deny incoming
```

### 2. SSH安全

```bash
# 禁用root登录
sudo nano /etc/ssh/sshd_config

# 修改：
PermitRootLogin no

# 重启SSH
sudo systemctl restart ssh
```

### 3. 定期更新

```bash
# 设置自动更新
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 📊 监控和日志

### 1. 日志查看

```bash
# 查看服务日志
sudo journalctl -u magic-school -f

# 查看应用日志
tail -f /opt/magic-school-agent/logs/agent_service.log

# 查看错误日志
tail -f /opt/magic-school-agent/app/work/logs/bypass/app.log
```

### 2. 性能监控

```bash
# 查看系统资源
htop

# 查看磁盘使用
df -h

# 查看内存使用
free -h
```

### 3. 配置告警

推荐使用：
- 阿里云云监控
- Grafana + Prometheus
- Sentry（错误监控）

---

## 💾 备份策略

### 1. 数据库备份

```bash
# 创建备份脚本
cat > /opt/magic-school-agent/scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/magic-school"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# 备份数据库
pg_dump $PGDATABASE_URL > $BACKUP_DIR/db_$DATE.sql

# 压缩
gzip $BACKUP_DIR/db_$DATE.sql

# 清理7天前的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/magic-school-agent/scripts/backup.sh

# 配置定时任务
crontab -e

# 添加每天凌晨2点备份
0 2 * * * /opt/magic-school-agent/scripts/backup.sh >> /var/log/backup.log 2>&1
```

### 2. 配置文件备份

```bash
# 备份配置文件
tar -czf /backup/config_$(date +%Y%m%d).tar.gz /opt/magic-school-agent/config /opt/magic-school-agent/.env.production
```

---

## 🚀 性能优化

### 1. 启用Gzip压缩

在Nginx配置中添加：

```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
```

### 2. 配置缓存

```nginx
# 静态资源缓存
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 3. 数据库优化

- 添加适当的索引
- 配置连接池
- 定期清理日志

---

## 🆘 故障排除

### 常见问题

#### 问题1：服务无法启动

```bash
# 查看服务状态
sudo systemctl status magic-school

# 查看日志
sudo journalctl -u magic-school -n 50

# 检查端口占用
netstat -tlnp | grep 5000
```

#### 问题2：数据库连接失败

```bash
# 检查数据库连接
psql $PGDATABASE_URL

# 检查环境变量
cat /opt/magic-school-agent/.env.production
```

#### 问题3：AI不工作

```bash
# 检查API Key
echo $DASHSCOPE_API_KEY

# 测试API连接
curl -X POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seed-1-6-251015",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

---

## 📝 上线检查清单

### 扣子平台部署

- [ ] 代码已推送到GitHub
- [ ] 环境变量已配置
- [ ] API Key已配置
- [ ] JWT密钥已修改
- [ ] 部署成功
- [ ] 健康检查通过
- [ ] API文档可访问
- [ ] 测试账号可登录

### 阿里云ECS部署

- [ ] ECS服务器已购买
- [ ] 安全组已配置
- [ ] 依赖已安装
- [ ] 项目已克隆
- [ ] 数据库已配置
- [ ] 环境变量已配置
- [ ] Nginx已配置
- [ ] SSL证书已配置
- [ ] 系统服务已启动
- [ ] 健康检查通过
- [ ] 域名已配置
- [ ] 监控已配置
- [ ] 备份已配置
- [ ] 防火墙已配置

---

## 💰 成本对比

### 扣子平台部署

| 项目 | 成本 |
|------|------|
| 平台费用 | 免费 |
| 域名 | 免费 |
| SSL证书 | 免费 |
| 大模型调用 | 按需 |
| **合计** | **约 ¥10-50/月** |

### 阿里云ECS部署

| 项目 | 月成本 |
|------|--------|
| ECS服务器（2核4G） | ¥120 |
| RDS数据库 | ¥50 |
| 对象存储（OSS） | ¥10 |
| 域名 | ¥10/年 |
| SSL证书 | ¥0 |
| 大模型调用 | 按需 |
| **合计** | **约 ¥190/月** |

---

## 🎯 推荐方案

### 首次部署
✅ **使用扣子平台**
- 快速上线（5分钟）
- 无需服务器
- 成本低
- 适合测试和演示

### 正式上线
✅ **使用阿里云ECS**
- 完全控制
- 高性能
- 可扩展
- 适合生产环境

---

## 📚 相关文档

- [扣子平台部署快速参考卡](docs/扣子平台部署快速参考卡.md)
- [快速部署指南](docs/快速部署指南.md)
- [后端API文档](API_DOCUMENTATION.md)
- [环境变量配置模板](docs/生产环境变量配置模板.txt)

---

## 📞 技术支持

- **项目文档**: `/workspace/projects/docs/`
- **测试脚本**: `/workspace/projects/scripts/`
- **日志目录**: `/workspace/projects/logs/`

---

**🎉 部署完成后，您的魔法课桌智能体就可以为用户提供服务了！**
