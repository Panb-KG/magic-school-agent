# 修复 npm run dev 错误

## 🔍 问题分析

出现 "Missing script: dev" 错误，可能的原因：

1. 不在正确的项目目录
2. package.json 文件有问题
3. Node.js 版本不兼容

---

## ✅ 解决方案

### 方案 1: 检查当前目录

首先确认你在正确的目录：

```bash
# 查看当前目录
pwd

# 应该显示类似：/path/to/magic-school-frontend

# 如果不在正确目录，进入项目目录
cd magic-school-frontend

# 确认 package.json 存在
ls -la package.json
```

### 方案 2: 直接运行 Vite

如果 `npm run dev` 仍然失败，可以直接运行 Vite：

```bash
npx vite
```

或者：

```bash
npx vite --port 5173
```

### 方案 3: 使用 Node 直接运行

```bash
node node_modules/.bin/vite
```

### 方案 4: 重新安装依赖

如果以上都不行，重新安装依赖：

```bash
# 删除 node_modules 和 package-lock.json
rm -rf node_modules package-lock.json

# 重新安装
npm install

# 然后运行
npm run dev
```

---

## 🚀 推荐操作步骤

### 步骤 1: 确认目录

```bash
pwd
```

确保你在 `magic-school-frontend` 目录下。

### 步骤 2: 配置环境变量

```bash
cat > .env.development << 'EOF'
VITE_BACKEND_URL=http://101.126.128.57:5000
VITE_API_BASE_URL=http://101.126.128.57:3000/api/v1
VITE_WS_URL=ws://101.126.128.57:8765
EOF
```

### 步骤 3: 使用 npx 启动（最可靠）

```bash
npx vite
```

或者指定端口：

```bash
npx vite --port 5173
```

---

## 📝 其他启动方式

### 方式 1: 使用 npm start（如果配置了）

```bash
npm start
```

### 方式 2: 使用 npm run（查看所有脚本）

```bash
npm run
```

这将列出所有可用的脚本。

### 方式 3: 手动创建脚本

如果 package.json 中的脚本有问题，可以手动修复：

```bash
# 编辑 package.json
nano package.json  # 或使用其他编辑器
```

确保 `scripts` 部分包含：
```json
"scripts": {
  "dev": "vite",
  "build": "tsc && vite build",
  "preview": "vite preview"
}
```

---

## 🐛 调试步骤

### 1. 检查 Node.js 版本

```bash
node -v
npm -v
```

推荐使用 Node.js 16+ 版本。

### 2. 检查 package.json

```bash
cat package.json
```

确认 `scripts` 部分存在且正确。

### 3. 查看 npm 错误日志

```bash
cat /Users/panbo/.npm/_logs/2026-02-03T14_59_53_310Z-debug-0.log
```

---

## 💡 快速修复

**最简单的解决方案：**

```bash
# 进入项目目录（如果不在）
cd magic-school-frontend

# 使用 npx 直接运行 Vite
npx vite
```

然后在浏览器访问：http://localhost:5173/

---

## 🎯 如果还是不行

### 完整重置步骤：

```bash
# 1. 进入项目目录
cd magic-school-frontend

# 2. 备份当前的 package.json
cp package.json package.json.backup

# 3. 删除依赖
rm -rf node_modules package-lock.json

# 4. 创建正确的 package.json
cat > package.json << 'EOF'
{
  "name": "magic-school-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.0",
    "echarts": "^5.4.0",
    "echarts-for-react": "^3.0.0",
    "socket.io-client": "^4.6.0",
    "antd": "^5.12.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.6",
    "typescript": "^5.3.3",
    "vite": "^5.0.8"
  }
}
EOF

# 5. 重新安装依赖
npm install

# 6. 启动开发服务器
npx vite
```

---

## 📚 相关信息

### 查看所有可用的 npm 脚本

```bash
npm run
```

### 手动运行 Vite

```bash
# 使用 npx（推荐）
npx vite

# 或直接调用
./node_modules/.bin/vite

# 或使用 node
node node_modules/vite/bin/vite.js
```

---

## 🔐 登录账号（成功启动后）

- **学生**: `student` / `password123`
- **家长**: `parent` / `password123`

---

## 💡 提示

- 使用 `npx vite` 是最可靠的方法
- 不需要修改 package.json
- 适用于各种 npm 版本

---

**现在试试运行 `npx vite` 吧！** 🚀
