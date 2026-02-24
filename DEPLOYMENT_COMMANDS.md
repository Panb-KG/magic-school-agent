# ⚡ 部署命令速查表

## 🚀 快速部署命令

### 扣子平台部署

```bash
# 1. 准备环境变量
cd /workspace/projects
cat > .env.production << 'EOF'
DASHSCOPE_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
JWT_SECRET=your-super-secret-jwt-key-at-least-32-chars
DEBUG=False
LOG_LEVEL=INFO
EOF

# 2. 推送到GitHub
git add .
git commit -m "chore: 准备部署"
git push -u origin main

# 3. 在扣子平台执行：
#    - 登录 https://www.coze.cn/
#    - 创建扣子编程项目
#    - 连接GitHub仓库
#    - 配置环境变量
#    - 点击"开始部署"
```

---

## 🏗️ 阿里云ECS部署命令

### 1. 系统准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装依赖
sudo apt install python3.11 python3.11-venv python3-pip nginx postgresql-client git -y
```

### 2. 项目部署

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

### 3. 数据库配置

```bash
# 初始化数据库
python scripts/init_database.py

# 测试数据库连接
python -c "
from storage.database.db import get_engine
engine = get_engine()
with engine.connect() as conn:
    result = conn.execute('SELECT 1')
    print('Database connection OK')
"
```

### 4. 环境变量配置

```bash
# 创建环境变量文件
cat > .env.production << 'EOF'
DASHSCOPE_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
JWT_SECRET=your-super-secret-jwt-key-at-least-32-chars
PGDATABASE_URL=postgresql://user:password@localhost:5432/magic_school
DEBUG=False
LOG_LEVEL=INFO
EOF
```

### 5. Nginx配置

```bash
# 创建配置文件
sudo nano /etc/nginx/sites-available/magic-school

# 添加配置内容（见下文）

# 启用配置
sudo ln -s /etc/nginx/sites-available/magic-school /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

**Nginx配置内容**：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### 6. SSL证书配置

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 申请SSL证书
sudo certbot --nginx -d your-domain.com

# 测试自动续期
sudo certbot renew --dry-run
```

### 7. 系统服务配置

```bash
# 创建服务文件
sudo nano /etc/systemd/system/magic-school.service
```

**服务文件内容**：

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

```bash
# 启动服务
sudo systemctl daemon-reload
sudo systemctl start magic-school
sudo systemctl enable magic-school

# 查看服务状态
sudo systemctl status magic-school
```

---

## 🔍 验证命令

### 健康检查

```bash
# 本地检查
curl http://localhost:5000/health

# 公网检查
curl http://your-domain.com/health
curl https://your-domain.com/health
```

### 查看日志

```bash
# 查看服务日志
sudo journalctl -u magic-school -f

# 查看应用日志
tail -f /opt/magic-school-agent/logs/agent_service.log

# 查看错误日志
tail -f /opt/magic-school-agent/app/work/logs/bypass/app.log

# 查看Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 测试API

```bash
# 测试对话
curl -X POST https://your-domain.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好",
    "session_id": "test",
    "user_id": "test"
  }'

# 测试注册
curl -X POST https://your-domain.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_student",
    "password": "password123",
    "role": "student",
    "student_name": "测试学生",
    "grade": "3年级"
  }'

# 测试登录
curl -X POST https://your-domain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_student",
    "password": "password123"
  }'
```

---

## 🛠️ 维护命令

### 服务管理

```bash
# 启动服务
sudo systemctl start magic-school

# 停止服务
sudo systemctl stop magic-school

# 重启服务
sudo systemctl restart magic-school

# 查看服务状态
sudo systemctl status magic-school

# 查看服务日志
sudo journalctl -u magic-school -f

# 重新加载配置
sudo systemctl daemon-reload
```

### Nginx管理

```bash
# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx

# 重新加载配置
sudo systemctl reload nginx

# 查看状态
sudo systemctl status nginx

# 查看日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 数据库管理

```bash
# 备份数据库
pg_dump $PGDATABASE_URL > backup_$(date +%Y%m%d).sql

# 恢复数据库
psql $PGDATABASE_URL < backup_20240101.sql

# 连接数据库
psql $PGDATABASE_URL

# 查看表
\dt

# 查看表结构
\d students
```

### 更新部署

```bash
# 进入项目目录
cd /opt/magic-school-agent

# 拉取最新代码
git pull origin main

# 激活虚拟环境
source venv/bin/activate

# 更新依赖
pip install -r requirements.txt --upgrade

# 重启服务
sudo systemctl restart magic-school
```

---

## 🔒 安全命令

### 防火墙配置

```bash
# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status

# 允许端口
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# 删除规则
sudo ufw delete allow 5000/tcp

# 重载防火墙
sudo ufw reload
```

### SSH安全

```bash
# 编辑SSH配置
sudo nano /etc/ssh/sshd_config

# 禁用root登录
PermitRootLogin no

# 仅允许密钥认证
PasswordAuthentication no

# 重启SSH服务
sudo systemctl restart ssh
```

---

## 📊 监控命令

### 系统资源

```bash
# 查看CPU和内存
htop

# 查看磁盘使用
df -h

# 查看内存使用
free -h

# 查看进程
ps aux | grep python

# 查看端口占用
netstat -tlnp | grep 5000
```

### 日志监控

```bash
# 实时查看日志
tail -f /opt/magic-school-agent/logs/agent_service.log

# 查看错误日志
grep -i error /opt/magic-school-agent/logs/agent_service.log

# 查看最近的日志
tail -n 100 /opt/magic-school-agent/logs/agent_service.log
```

---

## 💾 备份命令

### 数据库备份

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

# 手动执行备份
/opt/magic-school-agent/scripts/backup.sh
```

### 定时备份

```bash
# 编辑crontab
crontab -e

# 添加定时任务（每天凌晨2点备份）
0 2 * * * /opt/magic-school-agent/scripts/backup.sh >> /var/log/backup.log 2>&1

# 查看定时任务
crontab -l
```

---

## 🆘 故障排查命令

### 服务问题

```bash
# 查看服务状态
sudo systemctl status magic-school

# 查看详细日志
sudo journalctl -u magic-school -n 100

# 重启服务
sudo systemctl restart magic-school

# 查看端口占用
sudo netstat -tlnp | grep 5000
```

### 数据库问题

```bash
# 测试数据库连接
python -c "
from storage.database.db import get_engine
engine = get_engine()
with engine.connect() as conn:
    result = conn.execute('SELECT 1')
    print('Database connection OK')
"

# 查看数据库进程
ps aux | grep postgres

# 重启数据库（如果自建）
sudo systemctl restart postgresql
```

### 网络问题

```bash
# 测试本地端口
curl http://localhost:5000/health

# 测试公网访问
curl http://your-domain.com/health

# 检查防火墙
sudo ufw status

# 检查Nginx
sudo nginx -t
sudo systemctl status nginx
```

### Python问题

```bash
# 检查Python版本
python --version

# 检查依赖
pip list | grep langchain

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

---

## 📝 常用文件路径

```bash
# 项目目录
/opt/magic-school-agent

# 配置文件
/opt/magic-school-agent/config/
/opt/magic-school-agent/.env.production

# 日志目录
/opt/magic-school-agent/logs/
/opt/magic-school-agent/app/work/logs/bypass/

# Nginx配置
/etc/nginx/sites-available/magic-school
/etc/nginx/sites-enabled/magic-school

# 系统服务
/etc/systemd/system/magic-school.service

# 备份目录
/backup/magic-school/
```

---

## 🎯 快速测试命令集

```bash
# 一键健康检查
curl -f http://localhost:5000/health && echo "✅ Service OK" || echo "❌ Service Failed"

# 一键服务状态
sudo systemctl status magic-school | head -n 10

# 一键资源检查
echo "=== CPU ===" && top -bn1 | head -n 10
echo "=== Memory ===" && free -h
echo "=== Disk ===" && df -h

# 一键日志检查
echo "=== Recent Logs ===" && tail -n 20 /opt/magic-school-agent/logs/agent_service.log

# 一键端口检查
netstat -tlnp | grep -E "5000|80|443"
```

---

**💡 提示**：将常用命令保存到脚本中，方便快速执行。

```bash
# 创建快捷命令脚本
cat > ~/magic-school-commands.sh << 'EOF'
#!/bin/bash
# 魔法课桌快捷命令

case "$1" in
  status)
    sudo systemctl status magic-school
    ;;
  logs)
    sudo journalctl -u magic-school -f
    ;;
  restart)
    sudo systemctl restart magic-school
    ;;
  health)
    curl http://localhost:5000/health
    ;;
  backup)
    /opt/magic-school-agent/scripts/backup.sh
    ;;
  *)
    echo "Usage: $0 {status|logs|restart|health|backup}"
    ;;
esac
EOF

chmod +x ~/magic-school-commands.sh

# 使用
~/magic-school-commands.sh status
~/magic-school-commands.sh logs
```
