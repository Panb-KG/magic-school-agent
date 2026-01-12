# 前端Web应用部署指南

## 📋 目录

- [技术栈推荐](#技术栈推荐)
- [项目初始化](#项目初始化)
- [目录结构](#目录结构)
- [开发环境搭建](#开发环境搭建)
- [API集成](#api集成)
- [WebSocket集成](#websocket集成)
- [部署到服务器](#部署到服务器)
- [常用组件示例](#常用组件示例)

---

## 技术栈推荐

### 方案A：React + TypeScript（推荐）

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.0",
    "echarts": "^5.4.0",
    "echarts-for-react": "^3.0.0",
    "socket.io-client": "^4.6.0",
    "tailwindcss": "^3.3.0",
    "antd": "^5.12.0"
  }
}
```

**优点**：
- 生态成熟，组件库丰富
- TypeScript类型安全
- Ant Design UI组件库美观易用

### 方案B：Vue 3 + TypeScript

```json
{
  "dependencies": {
    "vue": "^3.3.0",
    "vue-router": "^4.2.0",
    "axios": "^1.6.0",
    "echarts": "^5.4.0",
    "vue-echarts": "^6.6.0",
    "socket.io-client": "^4.6.0",
    "element-plus": "^2.4.0"
  }
}
```

**优点**：
- 学习曲线较平缓
- Vue 3 Composition API强大
- Element Plus组件库完善

---

## 项目初始化

### React项目初始化

```bash
# 使用Vite创建React项目
npm create vite@latest magic-school-frontend -- --template react-ts

# 进入项目目录
cd magic-school-frontend

# 安装依赖
npm install

# 安装额外依赖
npm install react-router-dom axios echarts echarts-for-react socket.io-client
npm install -D tailwindcss postcss autoprefixer
npm install antd

# 初始化Tailwind CSS
npx tailwindcss init -p
```

### Vue项目初始化

```bash
# 使用Vite创建Vue项目
npm create vite@latest magic-school-frontend -- --template vue-ts

# 进入项目目录
cd magic-school-frontend

# 安装依赖
npm install

# 安装额外依赖
npm install vue-router@4 axios echarts vue-echarts socket.io-client
npm install element-plus
```

---

## 目录结构

```
magic-school-frontend/
├── src/
│   ├── api/                 # API接口层
│   │   ├── index.ts         # API配置
│   │   ├── dashboard.ts     # 仪表盘API
│   │   ├── schedule.ts      # 课程表API
│   │   ├── points.ts        # 积分API
│   │   └── achievements.ts  # 成就API
│   ├── components/          # 公共组件
│   │   ├── ProfileCard/     # 学生档案卡片
│   │   ├── Schedule/        # 课程表组件
│   │   ├── PointsChart/     # 积分图表
│   │   ├── AchievementWall/ # 成就墙
│   │   └── HomeworkList/    # 作业列表
│   ├── pages/               # 页面
│   │   ├── Dashboard/       # 仪表盘页面
│   │   ├── Schedule/        # 课程表页面
│   │   ├── Achievements/    # 成就页面
│   │   └── Homework/        # 作业页面
│   ├── hooks/               # 自定义Hooks
│   │   ├── useWebSocket.ts  # WebSocket Hook
│   │   └── useAPI.ts       # API Hook
│   ├── utils/               # 工具函数
│   │   └── request.ts       # HTTP请求封装
│   ├── types/               # TypeScript类型定义
│   │   └── index.ts
│   ├── App.tsx              # 根组件
│   └── main.tsx             # 入口文件
├── public/                  # 静态资源
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

---

## 开发环境搭建

### 1. 配置Tailwind CSS

**tailwind.config.js**
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        magic: {
          primary: '#7C3AED',    // 紫色
          secondary: '#F59E0B',  // 金色
          accent: '#10B981',     // 绿色
        }
      }
    },
  },
  plugins: [],
}
```

**src/index.css**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* 魔法学校主题样式 */
body {
  font-family: 'Inter', system-ui, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.magic-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}
```

### 2. 配置API基础URL

**src/utils/request.ts**
```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api/v1';

const request = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 可以在这里添加token等认证信息
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export default request;
```

### 3. 配置环境变量

**.env.development**
```env
VITE_API_BASE_URL=http://localhost:3000/api/v1
VITE_WS_BASE_URL=ws://localhost:8765/ws
```

**.env.production**
```env
VITE_API_BASE_URL=https://your-domain.com/api/v1
VITE_WS_BASE_URL=wss://your-domain.com/ws
```

---

## API集成

### 示例1：获取学生仪表盘数据

**src/api/dashboard.ts**
```typescript
import request from '@/utils/request';

export interface DashboardData {
  profile: {
    id: number;
    name: string;
    grade: string;
    magic_level: number;
    total_points: number;
    level_progress: number;
  };
  stats: {
    completed_homeworks: number;
    pending_homeworks: number;
    total_achievements: number;
  };
  recent_achievements: any[];
  todos: any[];
}

export const getDashboard = async (studentName: string): Promise<DashboardData> => {
  const response = await request.get(`/dashboard/${studentName}`);
  return response;
};
```

**src/pages/Dashboard/index.tsx**
```typescript
import React, { useEffect, useState } from 'react';
import { getDashboard } from '@/api/dashboard';

const DashboardPage = () => {
  const [studentName] = useState('小明');
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await getDashboard(studentName);
        setData(result);
      } catch (error) {
        console.error('获取仪表盘数据失败:', error);
      }
    };

    fetchData();
  }, [studentName]);

  if (!data) return <div>加载中...</div>;

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-white mb-6">
        🧙‍♂️ {data.profile.name}的魔法档案
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* 学生档案卡片 */}
        <ProfileCard profile={data.profile} />

        {/* 统计卡片 */}
        <StatsCard stats={data.stats} />

        {/* 待办事项 */}
        <TodoList todos={data.todos} />
      </div>

      {/* 最近成就 */}
      <RecentAchievements achievements={data.recent_achievements} />
    </div>
  );
};

export default DashboardPage;
```

### 示例2：积分图表组件

**src/components/PointsChart/index.tsx**
```typescript
import React from 'react';
import ReactECharts from 'echarts-for-react';
import * as echarts from 'echarts';
import { getPointsTrend } from '@/api/points';

interface PointsChartProps {
  studentName: string;
}

const PointsChart: React.FC<PointsChartProps> = ({ studentName }) => {
  const [option, setOption] = React.useState<any>({});

  useEffect(() => {
    const fetchChartData = async () => {
      try {
        const data = await getPointsTrend(studentName, 30);

        setOption({
          title: {
            text: '积分增长趋势',
            left: 'center'
          },
          tooltip: {
            trigger: 'axis'
          },
          xAxis: {
            type: 'category',
            data: data.date_list
          },
          yAxis: {
            type: 'value'
          },
          series: [{
            data: data.cumulative_points,
            type: 'line',
            smooth: true,
            lineStyle: {
              color: '#7C3AED',
              width: 3
            },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(124, 58, 237, 0.5)' },
                { offset: 1, color: 'rgba(124, 58, 237, 0.1)' }
              ])
            }
          }]
        });
      } catch (error) {
        console.error('获取图表数据失败:', error);
      }
    };

    fetchChartData();
  }, [studentName]);

  return (
    <div className="magic-card p-6">
      <ReactECharts option={option} style={{ height: '400px' }} />
    </div>
  );
};

export default PointsChart;
```

---

## WebSocket集成

### WebSocket Hook

**src/hooks/useWebSocket.ts**
```typescript
import { useEffect, useRef, useState } from 'react';

interface WebSocketMessage {
  type: string;
  channel?: string;
  data?: any;
  message?: string;
}

export const useWebSocket = (studentName: string) => {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const wsUrl = `${import.meta.env.VITE_WS_BASE_URL}/${studentName}`;
    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      console.log('WebSocket连接成功');
      setIsConnected(true);

      // 订阅频道
      wsRef.current?.send(JSON.stringify({
        type: 'subscribe',
        channels: ['dashboard', 'achievements', 'homework', 'points']
      }));
    };

    wsRef.current.onmessage = (event) => {
      const message: WebSocketMessage = JSON.parse(event.data);
      console.log('收到WebSocket消息:', message);
      setMessages(prev => [...prev, message]);

      // 处理不同类型的消息
      switch (message.type) {
        case 'update':
          handleUpdate(message);
          break;
        case 'welcome':
          console.log(message.message);
          break;
        default:
          console.log('未知消息类型:', message.type);
      }
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket错误:', error);
    };

    wsRef.current.onclose = () => {
      console.log('WebSocket连接关闭');
      setIsConnected(false);
    };

    return () => {
      wsRef.current?.close();
    };
  }, [studentName]);

  const handleUpdate = (message: WebSocketMessage) => {
    const channel = message.channel;
    const data = message.data;

    switch (channel) {
      case 'dashboard':
        // 仪表盘更新，刷新数据
        console.log('仪表盘更新:', data);
        break;
      case 'achievements':
        // 新成就解锁，显示通知
        if (data.event === 'achievement_unlocked') {
          showNotification('🎉 成就解锁！', data.achievement.title);
        }
        break;
      case 'points':
        // 积分更新，显示通知
        if (data.event === 'points_added') {
          showNotification('✨ 获得积分', `+${data.points}分`);
        }
        break;
      case 'homework':
        // 作业状态更新
        console.log('作业状态更新:', data);
        break;
    }
  };

  const showNotification = (title: string, message: string) => {
    // 使用Ant Design的notification
    // notification.success({ title, message });
    console.log(`🔔 ${title}: ${message}`);
  };

  return { isConnected, messages };
};
```

### 使用WebSocket Hook

**src/pages/Dashboard/index.tsx**
```typescript
import { useWebSocket } from '@/hooks/useWebSocket';

const DashboardPage = () => {
  const [studentName] = useState('小明');
  const { isConnected } = useWebSocket(studentName);

  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        <h1>仪表盘</h1>
        <span className={`text-sm ${isConnected ? 'text-green-500' : 'text-red-500'}`}>
          {isConnected ? '🟢 已连接' : '🔴 未连接'}
        </span>
      </div>

      {/* 页面内容 */}
    </div>
  );
};
```

---

## 部署到服务器

### 1. 构建前端项目

```bash
# 安装依赖
npm install

# 构建生产版本
npm run build
```

### 2. 部署到Nginx

**nginx.conf**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/magic-school-frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # API代理到后端
    location /api/ {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket代理
    location /ws/ {
        proxy_pass http://localhost:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
```

### 3. 上传文件到服务器

```bash
# 本地打包
npm run build

# 上传到服务器
scp -r dist/* user@your-server:/var/www/magic-school-frontend/

# 重启Nginx
sudo systemctl restart nginx
```

### 4. 使用Docker部署（可选）

**Dockerfile**
```dockerfile
# 构建阶段
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 运行阶段
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**docker-compose.yml**
```yaml
version: '3.8'

services:
  frontend:
    build: .
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - magic-school

  backend:
    # 后端服务配置
    image: magic-school-backend:latest
    ports:
      - "3000:3000"
      - "8765:8765"
    networks:
      - magic-school

networks:
  magic-school:
    driver: bridge
```

---

## 常用组件示例

### 1. 学生档案卡片

```typescript
const ProfileCard: React.FC<{ profile: any }> = ({ profile }) => {
  return (
    <div className="magic-card p-6">
      <div className="flex items-center gap-4 mb-4">
        {profile.avatar_url ? (
          <img src={profile.avatar_url} alt="头像" className="w-20 h-20 rounded-full" />
        ) : (
          <div className="w-20 h-20 rounded-full bg-magic-primary flex items-center justify-center text-white text-3xl">
            🧙‍♂️
          </div>
        )}
        <div>
          <h2 className="text-2xl font-bold">{profile.nickname}</h2>
          <p className="text-gray-600">{profile.grade} · {profile.class_name}</p>
        </div>
      </div>

      <div className="space-y-3">
        <div>
          <div className="flex justify-between mb-1">
            <span>魔法等级: {profile.magic_level}级</span>
            <span>{profile.level_percentage}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className="bg-magic-primary h-2.5 rounded-full"
              style={{ width: `${profile.level_percentage}%` }}
            ></div>
          </div>
        </div>
        <div className="flex justify-between">
          <span>总积分</span>
          <span className="text-magic-secondary font-bold">{profile.total_points}</span>
        </div>
      </div>
    </div>
  );
};
```

### 2. 课程表组件

```typescript
const ScheduleCard: React.FC<{ schedule: any }> = ({ schedule }) => {
  return (
    <div className="magic-card p-6">
      <h2 className="text-xl font-bold mb-4">📅 本周课程表</h2>
      <div className="grid grid-cols-7 gap-2">
        {schedule.weekdays.map((day: string) => (
          <div key={day} className="text-center">
            <div className="font-bold mb-2">{day}</div>
            <div className="space-y-1">
              {schedule.courses[day].map((course: any) => (
                <div
                  key={course.id}
                  className={`p-2 rounded text-xs ${
                    course.type === 'school'
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-green-100 text-green-800'
                  }`}
                >
                  <div>{course.name}</div>
                  <div className="text-gray-600">{course.time}</div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

---

## 总结

本文档提供了完整的Web前端部署指南，包括：

✅ 技术栈推荐（React/Vue）
✅ 项目初始化和目录结构
✅ API集成示例
✅ WebSocket实时通信
✅ 部署到服务器的方法
✅ 常用组件示例

按照本指南，你可以快速搭建一个与后端API完美对接的Web前端应用！✨
