# 前端部署指南

本文档提供魔法课桌前端应用的详细部署说明。

## 📋 部署前准备

### 1. 环境检查

确保你的服务器满足以下要求：

- Node.js >= 18.0.0
- npm >= 9.0.0
- Nginx >= 1.18.0（推荐）
- 至少 1GB 可用内存
- 至少 2GB 可用磁盘空间

### 2. 后端服务检查

确保后端服务已正确部署并运行：

- API 服务：`http://your-server-ip:3000/api/v1`
- WebSocket 服务：`ws://your-server-ip:8765`

## 🚀 部署步骤

### 步骤 1: 克隆或上传代码

```bash
# 方式 1: 如果代码在 Git 仓库中
git clone <repository-url> magic-school-frontend
cd magic-school-frontend

# 方式 2: 上传代码包
# 将代码上传到服务器后解压
```

### 步骤 2: 安装依赖

```bash
npm install
```

### 步骤 3: 配置环境变量

编辑 `.env.production` 文件：

```bash
VITE_API_BASE_URL=http://your-server-ip:3000/api/v1
VITE_WS_URL=ws://your-server-ip:8765
```

**重要**：
- 将 `your-server-ip` 替换为实际的服务器 IP 地址
- 如果使用域名，可以替换为域名

### 步骤 4: 构建生产版本

```bash
npm run build
```

构建完成后，`dist` 目录将包含所有生产文件：

```
dist/
├── index.html
├── assets/
│   ├── index-[hash].js
│   └── index-[hash].css
└── ...
```

### 步骤 5: 配置 Nginx

创建 Nginx 配置文件 `/etc/nginx/sites-available/magic-school-frontend`：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名

    # 前端静态文件
    location / {
        root /path/to/magic-school-frontend/dist;
        try_files $uri $uri/ /index.html;
        index index.html;

        # 缓存静态资源
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # API 反向代理
    location /api {
        proxy_pass http://localhost:3000/api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;

        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket 反向代理
    location /ws {
        proxy_pass http://localhost:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # WebSocket 特定配置
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript
               application/x-javascript application/xml+rss
               application/javascript application/json;

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

启用配置：

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/magic-school-frontend /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 步骤 6: 配置 HTTPS（可选但推荐）

使用 Let's Encrypt 免费证书：

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取并配置证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

Certbot 会自动修改 Nginx 配置，添加 HTTPS 支持。

### 步骤 7: 配置防火墙

确保防火墙允许必要端口：

```bash
# 使用 ufw（Ubuntu/Debian）
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# 使用 firewall-cmd（CentOS/RHEL）
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 🐳 Docker 部署（可选）

### Dockerfile

创建 `Dockerfile`：

```dockerfile
# 构建阶段
FROM node:18-alpine as builder
WORKDIR /app

# 复制 package 文件
COPY package*.json ./
RUN npm install

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx 配置文件

创建 `nginx.conf`：

```nginx
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://host.docker.internal:3000/api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }

    location /ws {
        proxy_pass http://host.docker.internal:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
}
```

### 构建和运行

```bash
# 构建镜像
docker build -t magic-school-frontend .

# 运行容器
docker run -d \
  -p 80:80 \
  --name magic-school-frontend \
  magic-school-frontend

# 查看日志
docker logs -f magic-school-frontend
```

### Docker Compose

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  frontend:
    build: .
    ports:
      - "80:80"
    restart: unless-stopped
    networks:
      - magic-network
    environment:
      - VITE_API_BASE_URL=http://backend:3000/api/v1
      - VITE_WS_URL=ws://backend:8765

networks:
  magic-network:
    external: true
```

运行：

```bash
docker-compose up -d
```

## 🔧 监控和维护

### 日志查看

```bash
# Nginx 访问日志
sudo tail -f /var/log/nginx/access.log

# Nginx 错误日志
sudo tail -f /var/log/nginx/error.log
```

### 性能监控

使用 Nginx 状态模块监控：

在 Nginx 配置中添加：

```nginx
location /nginx_status {
    stub_status on;
    access_log off;
    allow 127.0.0.1;
    deny all;
}
```

访问 `http://your-server-ip/nginx_status` 查看状态。

## 🔒 安全建议

1. **使用 HTTPS**：始终在生产环境中使用 HTTPS
2. **定期更新**：保持 Nginx 和 Node.js 版本更新
3. **限制访问**：使用防火墙限制不必要的服务访问
4. **日志分析**：定期检查日志，发现异常访问
5. **备份**：定期备份重要数据和配置

## 📊 性能优化

1. **启用 Gzip 压缩**：已在配置中启用
2. **静态资源缓存**：已在配置中启用
3. **CDN 加速**：考虑使用 CDN 分发静态资源
4. **图片优化**：使用 WebP 格式图片
5. **代码分割**：Vite 默认支持代码分割

## 🐛 故障排除

### 常见问题

1. **502 Bad Gateway**：
   - 检查后端服务是否运行
   - 检查 Nginx 配置中的代理地址是否正确

2. **WebSocket 连接失败**：
   - 检查 WebSocket 服务是否运行
   - 检查防火墙是否允许 WebSocket 端口
   - 检查 Nginx 的 WebSocket 代理配置

3. **页面刷新 404**：
   - 确保 Nginx 配置中有 `try_files $uri $uri/ /index.html;`
   - 确保 `root` 路径指向正确的 `dist` 目录

4. **API 跨域问题**：
   - 检查后端是否配置了 CORS
   - 使用 Nginx 代理解决跨域问题

## 📞 支持

如有问题，请查阅项目文档或提交 Issue。
