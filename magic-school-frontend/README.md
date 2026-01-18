# 魔法课桌学习助手智能体 - 前端

一个基于 React + TypeScript 的魔法学校主题学习管理系统前端应用。

## ✨ 特性

- 🎨 **魔法学校风格** - 采用哈利波特风格的紫色和金色主题
- 📱 **响应式设计** - 完美适配手机和平板
- 🚀 **现代化技术栈** - React 18 + TypeScript + Vite
- 📊 **数据可视化** - 集成 ECharts 展示积分趋势
- 🔌 **实时通信** - 支持 WebSocket 实时更新
- 🎯 **TypeScript** - 完整的类型安全保障

## 🚀 快速开始

### 环境要求

- Node.js >= 18.0.0
- npm >= 9.0.0

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

应用将在 `http://localhost:5173` 启动。

### 生产构建

```bash
npm run build
```

构建产物将在 `dist` 目录中。

### 预览生产构建

```bash
npm run preview
```

## 📁 项目结构

```
magic-school-frontend/
├── src/
│   ├── api/                 # API 接口层
│   │   ├── dashboard.ts     # 仪表盘 API
│   │   ├── schedule.ts      # 课程表 API
│   │   ├── points.ts        # 积分 API
│   │   └── achievements.ts  # 成就 API
│   ├── components/          # 公共组件
│   │   ├── ProfileCard/     # 学生档案卡片
│   │   ├── Schedule/        # 课程表组件
│   │   ├── PointsChart/     # 积分图表
│   │   ├── AchievementWall/ # 成就墙
│   │   └── HomeworkList/    # 作业列表
│   ├── pages/               # 页面
│   │   ├── Dashboard/       # 仪表盘页面
│   │   ├── SchedulePage/    # 课程表页面
│   │   ├── AchievementsPage/# 成就页面
│   │   └── HomeworkPage/    # 作业页面
│   ├── hooks/               # 自定义 Hooks
│   │   ├── useWebSocket.ts  # WebSocket Hook
│   │   └── useAPI.ts       # API Hook
│   ├── utils/               # 工具函数
│   │   └── request.ts       # HTTP 请求封装
│   ├── types/               # TypeScript 类型定义
│   │   └── index.ts
│   ├── App.tsx              # 根组件
│   ├── main.tsx             # 入口文件
│   └── index.css            # 全局样式
├── public/                  # 静态资源
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## 🔧 配置

### 环境变量

创建 `.env.local` 文件配置环境变量：

```bash
VITE_API_BASE_URL=http://localhost:3000/api/v1
VITE_WS_URL=ws://localhost:8765
```

生产环境使用 `.env.production`：

```bash
VITE_API_BASE_URL=http://your-server-ip:3000/api/v1
VITE_WS_URL=ws://your-server-ip:8765
```

## 📱 页面说明

### 仪表盘 (`/dashboard/:studentName`)

- 学生档案信息
- 积分趋势图表
- 课程表概览
- 成就墙预览

### 课程表 (`/schedule/:studentName`)

- 完整的一周课程表
- 课程详情展示
- 必修/选修课程分类

### 成就墙 (`/achievements/:studentName`)

- 所有成就展示
- 成就等级统计
- 精选/最新成就筛选

### 作业中心 (`/homework/:studentName`)

- 作业进度统计
- 按学科分类
- 待办/已完成/逾期状态

## 🎨 样式定制

项目使用 Tailwind CSS，主题颜色在 `tailwind.config.js` 中配置：

```javascript
theme: {
  extend: {
    colors: {
      magic: {
        primary: '#7C3AED',    // 紫色
        primaryDark: '#5B21B6', // 深紫色
        secondary: '#F59E0B',  // 金色
        accent: '#10B981',     // 绿色
      }
    }
  }
}
```

## 🔌 API 集成

所有 API 调用封装在 `src/api/` 目录中，使用 axios 进行请求：

```typescript
import { getDashboard } from '@/api';

const { data, loading, error } = useAPI(getDashboard, true, studentName);
```

## 📡 WebSocket 实时通信

使用 `useWebSocket` Hook 连接 WebSocket：

```typescript
import { useWebSocket } from '@/hooks/useWebSocket';

const { isConnected, subscribe, send } = useWebSocket({
  channels: [`student:${studentName}`],
  onMessage: (message) => {
    console.log('收到消息:', message);
  }
});
```

## 🚢 部署

### 构建

```bash
npm run build
```

### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/magic-school-frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理
    location /api {
        proxy_pass http://localhost:3000/api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket 反向代理
    location /ws {
        proxy_pass http://localhost:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
```

### Docker 部署

```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🧪 测试

运行开发服务器后，访问：

- 仪表盘: `http://localhost:5173/dashboard/小明`
- 课程表: `http://localhost:5173/schedule/小明`
- 成就墙: `http://localhost:5173/achievements/小明`
- 作业中心: `http://localhost:5173/homework/小明`

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
