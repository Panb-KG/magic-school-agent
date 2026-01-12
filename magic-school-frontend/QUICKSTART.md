# 快速启动指南

## 🚀 本地开发启动

### 1. 安装依赖

```bash
cd magic-school-frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

服务器将在 `http://localhost:5173` 启动。

### 3. 访问应用

- 仪表盘: http://localhost:5173/dashboard/小明
- 课程表: http://localhost:5173/schedule/小明
- 成就墙: http://localhost:5173/achievements/小明
- 作业中心: http://localhost:5173/homework/小明

## ⚠️ 注意事项

### 依赖后端服务

前端应用需要以下后端服务运行：

1. **API 服务**（端口 3000）
   - 提供学生数据、课程表、积分、成就等数据接口
   - 确保 `http://localhost:3000/api/v1` 可访问

2. **WebSocket 服务**（端口 8765）
   - 提供实时数据更新
   - 确保 `ws://localhost:8765` 可访问

### 配置后端地址

编辑 `.env` 文件：

```bash
VITE_API_BASE_URL=http://localhost:3000/api/v1
VITE_WS_URL=ws://localhost:8765
```

如果后端在其他服务器，修改为对应地址：

```bash
VITE_API_BASE_URL=http://your-backend-server:3000/api/v1
VITE_WS_URL=ws://your-backend-server:8765
```

## 🧪 测试数据

如果后端服务未就绪，前端会显示错误提示。确保后端服务正常运行后刷新页面。

## 📱 测试响应式设计

前端应用支持响应式设计，可在不同设备上测试：

- **桌面**：浏览器窗口宽度 >= 1024px
- **平板**：浏览器窗口宽度 768px - 1023px
- **手机**：浏览器窗口宽度 < 768px

使用浏览器开发者工具（F12）切换设备模拟：

```
Chrome: Ctrl+Shift+M (或 Cmd+Shift+M)
Firefox: Ctrl+Shift+M (或 Cmd+Shift+M)
Safari: 开发菜单 -> 进入响应式设计模式
```

## 🔧 调试技巧

### 1. 查看网络请求

打开浏览器开发者工具 -> Network 标签页，查看 API 请求：

- 应该看到对 `/api/v1/dashboard/小明` 等接口的请求
- 检查请求状态码和响应内容

### 2. 查看 WebSocket 连接

打开浏览器开发者工具 -> WS (WebSocket) 标签页：

- 应该看到 WebSocket 连接到 `ws://localhost:8765`
- 可以查看实时消息

### 3. 查看控制台日志

打开浏览器开发者工具 -> Console 标签页：

- 查看任何错误信息
- 查看应用日志输出

### 4. Vue/React DevTools

安装浏览器扩展以更好地调试：

- [React Developer Tools](https://chrome.google.com/webstore/detail/react-developer-tools/)
- [Redux DevTools](https://chrome.google.com/webstore/detail/redux-devtools/)（如果使用状态管理）

## 🐛 常见问题

### 1. 安装依赖失败

```bash
# 清除缓存
npm cache clean --force

# 删除 node_modules
rm -rf node_modules package-lock.json

# 重新安装
npm install
```

### 2. 端口被占用

修改 `vite.config.ts` 中的端口配置：

```typescript
server: {
  port: 5174, // 改为其他端口
  // ...
}
```

### 3. API 请求失败

- 检查后端服务是否运行
- 检查 API 地址配置是否正确
- 检查防火墙设置
- 查看浏览器控制台的网络请求错误信息

### 4. WebSocket 连接失败

- 检查 WebSocket 服务是否运行
- 检查 WebSocket 地址配置是否正确
- 检查 Nginx 配置（如果使用代理）

## 📚 更多信息

- [完整 README](README.md)
- [部署指南](DEPLOYMENT.md)
- [API 文档](../API_DOCUMENTATION.md)

## 🤝 需要帮助？

如有问题，请查看：
1. 项目 README 文档
2. 部署指南
3. 浏览器控制台错误信息
4. 后端服务日志
