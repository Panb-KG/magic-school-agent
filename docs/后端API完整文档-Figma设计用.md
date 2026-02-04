# 魔法课桌智能体 - 后端API完整文档
## 用于Figma前端设计

**版本**: v1.0
**更新日期**: 2026-02-04
**文档用途**: 辅助前端设计和开发

---

## 📋 目录

1. [系统架构](#系统架构)
2. [服务端口说明](#服务端口说明)
3. [API接口总览](#api接口总览)
4. [认证系统](#认证系统)
5. [智能体对话](#智能体对话)
6. [学生数据接口](#学生数据接口)
7. [家长功能接口](#家长功能接口)
8. [数据结构定义](#数据结构定义)
9. [前端调用示例](#前端调用示例)
10. [Figma设计要点](#figma设计要点)

---

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────┐
│                   前端应用（待开发）                    │
│                 React/Vue/小程序                       │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ↓                         ↓
┌──────────────┐         ┌──────────────┐
│  API后端     │         │  Agent服务   │
│  端口 3000   │◄────────►│  端口 5000   │
└──────┬───────┘         └──────┬───────┘
       │                        │
       ↓                        ↓
┌──────────────┐         ┌──────────────┐
│  PostgreSQL  │         │   大模型API   │
│  数据库      │         │  (豆包)      │
└──────────────┘         └──────────────┘
```

### 核心组件

| 组件 | 端口 | 说明 | 状态 |
|------|------|------|------|
| **API后端** | 3000 | 用户认证、数据管理、业务逻辑 | ✅ 已实现 |
| **Agent服务** | 5000 | 智能体对话、工具调用、LLM集成 | ✅ 已实现 |
| **前端服务** | 5173 | 用户界面（待开发） | ⏳ 待开发 |
| **WebSocket** | 8765 | 实时通信、流式响应 | ✅ 已实现 |

---

## 服务端口说明

### 基础URL配置

```javascript
// 开发环境
const API_BASE_URL = 'http://localhost:3000/api/v1';
const AGENT_BASE_URL = 'http://localhost:5000';
const WS_URL = 'ws://localhost:8765';

// 生产环境
const API_BASE_URL = 'https://your-domain.com/api/v1';
const AGENT_BASE_URL = 'https://your-domain.com/agent';
const WS_URL = 'wss://your-domain.com/ws';
```

---

## API接口总览

### 接口分类

#### 1. 认证系统（4个接口）
- POST `/api/v1/auth/login` - 用户登录
- POST `/api/v1/auth/register` - 用户注册
- GET `/api/v1/auth/me` - 获取当前用户信息
- GET `/api/v1/health` - 健康检查

#### 2. 学生功能（6个接口）
- GET `/api/v1/dashboard/{student_name}` - 学生仪表盘
- GET `/api/v1/schedule/{student_name}` - 课程表
- GET `/api/v1/achievements/{student_name}` - 成就墙
- GET `/api/v1/homework/{student_name}` - 作业列表
- GET `/api/v1/profile/{student_name}` - 学生档案
- GET `/api/v1/points/{student_name}` - 积分信息

#### 3. 家长功能（2个接口）
- GET `/api/v1/parent/students` - 管理的学生列表
- GET `/api/v1/parent/conversations/{student_id}` - 对话历史

#### 4. 记忆系统（1个接口）
- GET `/api/v1/memory/{user_id}` - 长期记忆数据

#### 5. Agent对话（2个接口）
- POST `/run` - 非流式对话
- POST `/stream_run` - 流式对话（SSE）
- POST `/cancel/{run_id}` - 取消对话

---

## 认证系统

### 1. 用户登录

**接口**: `POST /api/v1/auth/login`

**描述**: 用户名密码登录，返回JWT Token

**请求示例**:
```json
{
  "username": "student",
  "password": "password123"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": 1,
      "username": "student",
      "role": "student",
      "student_name": "测试小魔法师",
      "nickname": "小哈利",
      "grade": "五年级",
      "class_name": "魔法班",
      "school": "霍格沃茨小学",
      "created_at": "2026-01-01T00:00:00Z"
    }
  }
}
```

**错误响应**:
```json
{
  "detail": "用户名或密码错误"
}
```

---

### 2. 用户注册

**接口**: `POST /api/v1/auth/register`

**描述**: 新用户注册

**请求示例（学生）**:
```json
{
  "username": "xiaoming",
  "password": "password123",
  "email": "xiaoming@example.com",
  "role": "student",
  "student_name": "小明",
  "nickname": "小明魔法师",
  "grade": "三年级",
  "class_name": "三年级二班",
  "school": "霍格沃茨小学"
}
```

**请求示例（家长）**:
```json
{
  "username": "parent1",
  "password": "password123",
  "email": "parent@example.com",
  "role": "parent",
  "real_name": "王爸爸"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": 3,
      "username": "xiaoming",
      "role": "student",
      "student_name": "小明",
      "nickname": "小明魔法师",
      "grade": "三年级",
      "class_name": "三年级二班",
      "school": "霍格沃茨小学"
    }
  }
}
```

---

### 3. 获取当前用户信息

**接口**: `GET /api/v1/auth/me`

**描述**: 获取当前登录用户的详细信息（需要Token）

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例（学生）**:
```json
{
  "id": 1,
  "username": "student",
  "role": "student",
  "student_name": "测试小魔法师",
  "nickname": "小哈利",
  "grade": "五年级",
  "class_name": "魔法班",
  "school": "霍格沃茨小学",
  "magic_level": 2,
  "total_points": 150,
  "avatar_url": "",
  "created_at": "2026-01-01T00:00:00Z"
}
```

**响应示例（家长）**:
```json
{
  "id": 2,
  "username": "parent",
  "role": "parent",
  "real_name": "测试家长",
  "linked_students": [1],
  "avatar_url": "",
  "created_at": "2026-01-01T00:00:00Z"
}
```

---

## 智能体对话

### 核心对话方式

魔法课桌智能体支持两种对话方式：

#### 方式1：非流式对话（简单场景）

**接口**: `POST /run`

**描述**: 发送消息，等待完整响应后一次性返回

**请求示例**:
```json
{
  "query": "你好",
  "session_id": "session_123456",
  "user_id": 1,
  "user_role": "student"
}
```

**响应示例**:
```json
{
  "messages": [
    {
      "type": "ai",
      "content": "你好呀，小巫师！今天是2026年2月4日星期三，需要什么魔法帮助呢？✨",
      "id": "msg_001",
      "tool_calls": null
    }
  ],
  "run_id": "run_abc123",
  "session_id": "session_123456"
}
```

---

#### 方式2：流式对话（推荐）

**接口**: `POST /stream_run`

**描述**: 实时流式返回响应，打字机效果

**请求示例**:
```json
{
  "query": "帮我查一下今天的课程",
  "session_id": "session_123456",
  "user_id": 1,
  "user_role": "student"
}
```

**响应格式**:
- **Content-Type**: `text/event-stream`
- **格式**: SSE (Server-Sent Events)

**响应示例**:
```
event: message
data: {"type":"ai","content":"你好呀，小巫师！"}

event: message
data: {"type":"ai","content":"让我看看你今天的课程安排..."}

event: message
data: {"type":"tool","name":"get_weekly_schedule","content":"查询成功"}
```

**取消对话**:
```
POST /cancel/{run_id}
```

---

### Agent功能能力

智能体具备以下核心能力（通过工具调用实现）：

#### 📅 时间管理
- 查询当前日期、时间、星期
- 计算本周、本月日期范围
- 时间提醒和倒计时

#### 👨‍🎓 学生管理
- 创建学生档案
- 查看学生信息
- 魔法等级系统
- 积分管理

#### 📚 课程管理
- 添加课程（学校/课外）
- 查看周课程表
- 更新/删除课程
- 课程提醒

#### 📝 作业管理
- 创建作业任务
- 设置截止日期和优先级
- 查看待完成作业
- 提交作业（需要验证）
- 作业完成奖励

#### 🏆 成就系统
- 颁发成就勋章
- 展示成就墙
- 成就等级统计
- 特色成就展示

#### 🏃 运动记录
- 记录运动数据
- 运动统计分析
- 健康建议

#### 📖 朗读练习
- 提供练习材料
- 语音识别
- 朗读评估
- 评分和反馈

#### 📁 文件管理
- 上传作业附件
- 上传课件资料
- 下载文件
- 文件分类管理

---

### Agent工具列表

| 工具名 | 功能 | 前端需要 | 说明 |
|--------|------|----------|------|
| `get_current_time` | 获取当前时间 | 无 | 自动调用 |
| `create_student` | 创建学生档案 | 无 | 对话时自动 |
| `get_student_info` | 查询学生信息 | 无 | 自动调用 |
| `add_student_points` | 增加积分 | 无 | 自动调用 |
| `add_course` | 添加课程 | 无 | 对话时自动 |
| `get_weekly_schedule` | 查询课程表 | 无 | 自动调用 |
| `add_homework` | 添加作业 | 无 | 对话时自动 |
| `get_homework_list` | 查询作业列表 | 无 | 自动调用 |
| `verify_and_submit_homework` | 验证并提交作业 | ✅ 上传证明 | 需要**文件上传界面** |
| `add_achievement` | 颁发成就 | 无 | 自动调用 |
| `get_achievement_wall` | 查看成就墙 | 无 | 自动调用 |
| `upload_homework_attachment` | 上传作业附件 | ✅ 文件上传 | 需要**文件上传界面** |
| `assess_reading` | 朗读评估 | ✅ 音频上传 | 需要**录音界面** |
| `practice_reading` | 朗读练习 | ✅ 文本展示 | 需要**文本展示界面** |

---

## 学生数据接口

### 1. 学生仪表盘

**接口**: `GET /api/v1/dashboard/{student_name}`

**描述**: 获取学生综合仪表盘数据

**响应示例**:
```json
{
  "student": {
    "name": "测试小魔法师",
    "nickname": "小哈利",
    "grade": "五年级",
    "magic_level": 2,
    "total_points": 150,
    "avatar_url": ""
  },
  "today_stats": {
    "completed_homework": 2,
    "homework_pending": 1,
    "exercise_minutes": 30,
    "points_earned": 25
  },
  "upcoming": {
    "next_homework": {
      "title": "数学练习题",
      "deadline": "2026-02-05"
    },
    "next_course": {
      "name": "英语课",
      "time": "明天 09:00"
    }
  },
  "recent_achievements": [
    {
      "title": "作业小能手",
      "level": "bronze",
      "earned_at": "2026-02-03"
    }
  ]
}
```

**Figma设计要点**:
- 显示学生头像、昵称、等级
- 今日统计卡片（作业完成、运动时长、积分）
- 待办提醒（下一个作业、课程）
- 最近获得成就

---

### 2. 课程表

**接口**: `GET /api/v1/schedule/{student_name}`

**描述**: 获取学生周课程表

**响应示例**:
```json
{
  "student_name": "测试小魔法师",
  "week_date_range": "2026-02-03 至 2026-02-09",
  "schedule": {
    "monday": [
      {
        "time": "08:00-09:00",
        "subject": "语文",
        "teacher": "李老师",
        "location": "教室101",
        "type": "school"
      },
      {
        "time": "09:10-10:00",
        "subject": "数学",
        "teacher": "王老师",
        "location": "教室101",
        "type": "school"
      }
    ],
    "tuesday": [...],
    "wednesday": [...],
    "thursday": [...],
    "friday": [...]
  }
}
```

**Figma设计要点**:
- 周视图日历
- 不同颜色区分科目
- 显示课程时间、地点、老师
- 区分学校课程和课外课程

---

### 3. 成就墙

**接口**: `GET /api/v1/achievements/{student_name}`

**描述**: 获取学生成就墙数据

**响应示例**:
```json
{
  "student_name": "测试小魔法师",
  "total_achievements": 5,
  "achievement_points": 25,
  "achievements_by_level": {
    "bronze": 3,
    "silver": 2,
    "gold": 0,
    "platinum": 0,
    "diamond": 0
  },
  "achievements": [
    {
      "id": 1,
      "title": "作业小能手",
      "description": "完成10次作业",
      "level": "bronze",
      "points": 5,
      "icon_url": "",
      "is_featured": true,
      "earned_at": "2026-02-03T10:00:00Z"
    },
    {
      "id": 2,
      "title": "坚持不懈",
      "description": "连续学习7天",
      "level": "silver",
      "points": 10,
      "icon_url": "",
      "is_featured": true,
      "earned_at": "2026-02-02T15:30:00Z"
    }
  ]
}
```

**Figma设计要点**:
- 成就卡片展示
- 不同等级不同颜色/图标
- 特色成就突出显示
- 获得时间展示
- 总成就统计

---

### 4. 作业列表

**接口**: `GET /api/v1/homework/{student_name}`

**查询参数**:
- `status`: `all` | `pending` | `completed`

**响应示例**:
```json
{
  "student_name": "测试小魔法师",
  "homework_list": [
    {
      "id": 1,
      "title": "数学练习题",
      "subject": "数学",
      "description": "完成第15页练习题",
      "deadline": "2026-02-05",
      "priority": "high",
      "status": "pending",
      "created_at": "2026-02-03"
    },
    {
      "id": 2,
      "title": "语文作文",
      "subject": "语文",
      "description": "写一篇关于"春天"的作文",
      "deadline": "2026-02-06",
      "priority": "medium",
      "status": "pending",
      "created_at": "2026-02-04"
    }
  ]
}
```

**Figma设计要点**:
- 作业卡片列表
- 优先级标记（高/中/低）
- 截止日期倒计时
- 状态标签（待完成/已完成）
- 作业详情弹窗

---

### 5. 学生档案

**接口**: `GET /api/v1/profile/{student_name}`

**响应示例**:
```json
{
  "id": 1,
  "name": "测试小魔法师",
  "nickname": "小哈利",
  "grade": "五年级",
  "class_name": "魔法班",
  "school": "霍格沃茨小学",
  "avatar_url": "",
  "magic_level": 2,
  "total_points": 150,
  "level_progress": 50,
  "next_level_points": 200,
  "achievements_by_level": {
    "bronze": 3,
    "silver": 2,
    "gold": 0
  },
  "featured_count": 2,
  "total_achievement_points": 25
}
```

**Figma设计要点**:
- 学生头像展示
- 基本信息卡片
- 魔法等级进度条
- 成就分布图
- 积分统计

---

### 6. 积分信息

**接口**: `GET /api/v1/points/{student_name}`

**响应示例**:
```json
{
  "student_name": "测试小魔法师",
  "total_points": 150,
  "magic_level": 2,
  "level_progress": 50,
  "next_level_points": 200,
  "points_breakdown": {
    "homework": 75,
    "exercise": 45,
    "reading": 30
  },
  "recent_points": [
    {
      "points": 15,
      "reason": "完成数学作业",
      "earned_at": "2026-02-03T10:00:00Z"
    }
  ]
}
```

**Figma设计要点**:
- 总积分展示
- 等级进度条
- 积分来源饼图
- 最近积分记录

---

## 家长功能接口

### 1. 管理的学生列表

**接口**: `GET /api/v1/parent/students`

**描述**: 获取家长绑定的所有学生

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "parent_id": 2,
  "students": [
    {
      "id": 1,
      "name": "测试小魔法师",
      "nickname": "小哈利",
      "grade": "五年级",
      "class_name": "魔法班",
      "magic_level": 2,
      "total_points": 150,
      "avatar_url": "",
      "last_active": "2026-02-04T08:00:00Z"
    }
  ]
}
```

**Figma设计要点**:
- 学生卡片列表
- 显示基本信息和等级
- 最后活跃时间
- 点击查看详情

---

### 2. 对话历史

**接口**: `GET /api/v1/parent/conversations/{student_id}`

**描述**: 获取学生的对话历史记录

**查询参数**:
- `limit`: 返回条数（默认20）
- `offset`: 偏移量

**响应示例**:
```json
{
  "student_id": 1,
  "conversations": [
    {
      "session_id": "session_001",
      "query": "帮我查一下今天的课程",
      "response": "你今天有3节课...",
      "timestamp": "2026-02-04T09:30:00Z",
      "tools_used": ["get_weekly_schedule"]
    },
    {
      "session_id": "session_002",
      "query": "我已经完成作业了",
      "response": "太棒了！...",
      "timestamp": "2026-02-04T10:15:00Z",
      "tools_used": ["get_homework_list", "verify_and_submit_homework"]
    }
  ]
}
```

**Figma设计要点**:
- 对话记录列表
- 时间轴展示
- 显示使用的工具
- 点击查看详情

---

## 记忆系统

### 长期记忆数据

**接口**: `GET /api/v1/memory/{user_id}`

**描述**: 获取用户的长期记忆数据

**响应示例**:
```json
{
  "user_id": 1,
  "memories": [
    {
      "type": "student_profile",
      "data": {
        "name": "测试小魔法师",
        "preferences": ["数学", "科学"],
        "learning_style": "visual"
      }
    },
    {
      "type": "conversation_history",
      "data": {
        "recent_topics": ["作业", "课程", "运动"],
        "frequent_questions": ["今天的作业是什么"]
      }
    }
  ]
}
```

---

## 数据结构定义

### User（用户）

```typescript
interface User {
  id: number;
  username: string;
  role: 'student' | 'parent';
  student_name?: string;      // 学生专用
  real_name?: string;         // 家长专用
  nickname?: string;
  grade?: string;
  class_name?: string;
  school?: string;
  magic_level?: number;       // 学生专用
  total_points?: number;      // 学生专用
  avatar_url?: string;
  created_at: string;
}
```

---

### Homework（作业）

```typescript
interface Homework {
  id: number;
  title: string;
  subject: string;
  description: string;
  deadline: string;
  priority: 'high' | 'medium' | 'low';
  status: 'pending' | 'completed';
  attachment_url?: string;
  created_at: string;
}
```

---

### Course（课程）

```typescript
interface Course {
  id: number;
  subject: string;
  time: string;              // "08:00-09:00"
  teacher: string;
  location: string;
  type: 'school' | 'extracurricular';
  day: string;               // "monday", "tuesday", etc.
}
```

---

### Achievement（成就）

```typescript
interface Achievement {
  id: number;
  title: string;
  description: string;
  level: 'bronze' | 'silver' | 'gold' | 'platinum' | 'diamond';
  points: number;
  icon_url: string;
  is_featured: boolean;
  earned_at?: string;
}
```

---

### AgentMessage（Agent消息）

```typescript
interface AgentMessage {
  type: 'ai' | 'tool' | 'human';
  content: string;
  id?: string;
  tool_calls?: ToolCall[];
  tool_name?: string;
}

interface ToolCall {
  name: string;
  args: Record<string, any>;
  id: string;
}
```

---

## 前端调用示例

### 1. 用户登录

```javascript
// 登录
async function login(username, password) {
  const response = await fetch('http://localhost:3000/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ username, password })
  });

  const data = await response.json();

  if (data.success) {
    // 保存Token
    localStorage.setItem('token', data.data.access_token);
    localStorage.setItem('user', JSON.stringify(data.data.user));

    return data.data.user;
  } else {
    throw new Error(data.detail);
  }
}
```

---

### 2. 发送消息到Agent（流式）

```javascript
async function sendMessageStream(query, onMessage, onComplete) {
  const token = localStorage.getItem('token');
  const user = JSON.parse(localStorage.getItem('user'));

  const response = await fetch('http://localhost:5000/stream_run', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      query,
      session_id: generateSessionId(),
      user_id: user.id,
      user_role: user.role
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let fullResponse = '';

  while (true) {
    const { done, value } = await reader.read();

    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));
        if (data.content) {
          fullResponse += data.content;
          onMessage(data.content);
        }
      }
    }
  }

  onComplete(fullResponse);
}
```

---

### 3. 上传作业证明

```javascript
async function uploadHomeworkProof(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('http://localhost:3000/api/v1/upload', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: formData
  });

  const data = await response.json();
  return data.url;
}

// 然后告诉Agent文件已上传
await agentService.sendMessage(
  '我已上传作业照片，请验证',
  { proof_url: uploadedUrl }
);
```

---

### 4. 录音上传（朗读练习）

```javascript
async function uploadReadingAudio(file) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('type', 'reading_audio');

  const response = await fetch('http://localhost:3000/api/v1/upload', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: formData
  });

  const data = await response.json();
  return data.url;
}
```

---

## Figma设计要点

### 1. 页面结构

#### 主要页面

| 页面 | 路径 | 权限 | 主要功能 |
|------|------|------|---------|
| **登录页** | `/login` | 公开 | 用户登录/注册 |
| **仪表盘** | `/dashboard` | 学生 | 概览、待办、统计 |
| **课程表** | `/schedule` | 学生 | 周课程表 |
| **作业** | `/homework` | 学生 | 作业列表、提交 |
| **成就** | `/achievements` | 学生 | 成就墙 |
| **智能对话** | `/chat` | 所有 | Agent对话界面 |
| **家长中心** | `/parent` | 家长 | 学生管理、查看 |

---

### 2. 组件设计

#### 2.1 智能对话组件

**核心功能**:
- 消息列表（滚动）
- 输入框
- 发送按钮
- 文件上传按钮
- 录音按钮
- 停止生成按钮

**交互流程**:
```
用户输入 → 发送请求 → 显示"正在输入..." → 流式接收消息 → 实时更新UI → 完成
```

**状态处理**:
- 发送中：禁用输入框
- 接收中：显示"正在思考..."或打字动画
- 错误：显示错误提示
- 工具调用：显示工具图标

---

#### 2.2 文件上传组件

**支持格式**:
- 图片：jpg, png, gif
- 文档：pdf, doc, docx
- 音频：mp3, wav（朗读练习）

**上传流程**:
```
选择文件 → 预览（如果是图片） → 显示进度 → 上传完成 → 返回URL
```

**UI元素**:
- 上传区域（拖拽或点击）
- 文件预览
- 进度条
- 删除按钮

---

#### 2.3 录音组件（朗读练习）

**功能**:
- 开始/停止录音
- 实时波形显示
- 录音时长显示
- 试听回放
- 重新录制

**UI设计**:
- 麦克风按钮
- 波形动画
- 计时器
- 回放/重录按钮

---

#### 2.4 学生卡片

**展示信息**:
- 头像
- 姓名/昵称
- 等级徽章
- 总积分
- 最近活跃

**交互**:
- 点击查看详情
- 长按切换绑定的学生

---

#### 2.5 成就卡片

**设计元素**:
- 成就图标/徽章
- 成就名称
- 描述
- 等级颜色
- 获得时间

**等级颜色**:
- Bronze: #CD7F32
- Silver: #C0C0C0
- Gold: #FFD700
- Platinum: #E5E4E2
- Diamond: #B9F2FF

---

#### 2.6 课程表组件

**布局**:
- 周视图（横轴：星期，纵轴：时间）
- 课程卡片（时间、科目、老师、地点）
- 当前时间高亮

**交互**:
- 点击课程查看详情
- 长按编辑/删除

---

### 3. 通用UI组件

#### 3.1 魔法元素

**图标**:
- ⚡ 魔法闪电
- 🎓 魔法帽
- 🪄 魔法杖
- 📜 魔法卷轴
- ✨ 魔法星星

**动画效果**:
- 消息发送：魔法粒子效果
- 成就解锁：闪光动画
- 积分增加：数字滚动
- 等级升级：爆炸效果

---

#### 3.2 颜色主题

**主色系**:
```css
--primary-color: #667eea;    /* 紫色 */
--secondary-color: #764ba2;  /* 深紫 */
--accent-color: #f093fb;     /* 粉紫 */
--success-color: #10b981;    /* 绿色 */
--warning-color: #f59e0b;    /* 橙色 */
--danger-color: #ef4444;     /* 红色 */
```

**等级颜色**:
```css
--level-bronze: #CD7F32;
--level-silver: #C0C0C0;
--level-gold: #FFD700;
--level-platinum: #E5E4E2;
--level-diamond: #B9F2FF;
```

---

### 4. 响应式设计

#### 断点

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

#### Mobile优化

- 课程表：改为列表视图
- 对话：全屏模式
- 成就墙：卡片滚动
- 侧边栏：底部导航

---

### 5. 无障碍设计

- 键盘导航支持
- 屏幕阅读器支持
- 高对比度模式
- 字体大小可调

---

### 6. 加载状态

**场景**:
- 页面加载：骨架屏
- 数据加载：Spinner
- 消息发送：发送动画
- 文件上传：进度条

---

### 7. 错误处理

**错误类型**:
- 网络错误：重试按钮
- 认证错误：跳转登录
- 服务器错误：错误提示
- 超时错误：重试选项

---

## 设计建议

### 1. 对话界面

**推荐布局**:
```
┌─────────────────────────────┐
│  魔法课桌  🪄            ⚙️  │  ← 顶部栏
├─────────────────────────────┤
│                             │
│  AI: 你好呀，小巫师！✨    │
│                             │
│  User: 今天有什么作业？     │
│                             │
│  AI: 让我看看... 📚        │
│  [工具调用动画]             │
│                             │
│  AI: 你今天有3门作业...    │
│                             │
├─────────────────────────────┤
│ [📎] [🎤] [输入框...] [发送] │  ← 输入区
└─────────────────────────────┘
```

---

### 2. 仪表盘

**推荐布局**:
```
┌────────────────────────────────┐
│  👤 小哈利  Lv.2  ⚡150分    │
├────────────────────────────────┤
│  📊 今日统计                  │
│  [作业 2] [运动 30min] [积分25]│
├────────────────────────────────┤
│  ⏰ 下一个任务                │
│  数学作业  明天截止           │
├────────────────────────────────┤
│  🏆 最近成就                  │
│  [作业小能手] [坚持不懈]      │
└────────────────────────────────┘
```

---

### 3. 课程表

**推荐布局**:
```
┌───────┬───────┬───────┬───────┐
│ 星期  │ 时间  │ 科目  │ 老师  │
├───────┼───────┼───────┼───────┤
│ 周一  │ 8:00  │ 语文  │ 李老师 │
│ 周一  │ 9:00  │ 数学  │ 王老师 │
├───────┼───────┼───────┼───────┤
│ 周二  │ 8:00  │ 英语  │ 张老师 │
│ ...   │ ...   │ ...   │ ...   │
└───────┴───────┴───────┴───────┘
```

---

## 前端开发检查清单

### 技术栈建议

- **框架**: React 18+ / Vue 3+
- **路由**: React Router / Vue Router
- **状态管理**: Redux / Vuex / Pinia
- **UI库**: Ant Design / Element Plus
- **HTTP**: Axios
- **WebSocket**: 原生 / Socket.io
- **录音**: MediaRecorder API

---

### 核心功能实现

- [ ] 用户登录/注册
- [ ] JWT Token管理
- [ ] 流式对话（SSE）
- [ ] 文件上传
- [ ] 录音功能
- [ ] 实时消息更新
- [ ] 错误处理
- [ ] 加载状态
- [ ] 响应式布局

---

### 页面实现

- [ ] 登录页
- [ ] 仪表盘
- [ ] 课程表
- [ ] 作业列表
- [ ] 成就墙
- [ ] 智能对话
- [ ] 家长中心

---

### 组件实现

- [ ] 对话框组件
- [ ] 消息气泡
- [ ] 文件上传
- [ ] 录音组件
- [ ] 学生卡片
- [ ] 成就卡片
- [ ] 课程表组件

---

## 测试账号

### 测试环境

- **基础URL**: `http://localhost:3000` (API), `http://localhost:5000` (Agent)
- **学生账号**: `student` / `password123`
- **家长账号**: `parent` / `password123`

---

## 常见问题

### Q1: 如何实现流式对话？
**A**: 使用Server-Sent Events (SSE)，前端使用`fetch`的`ReadableStream`。

### Q2: 文件上传如何处理？
**A**: 前端先上传文件到API后端，获取URL，然后告诉Agent文件已准备好。

### Q3: 如何实现录音功能？
**A**: 使用浏览器原生的`MediaRecorder` API，录制后上传音频文件。

### Q4: 如何处理Token过期？
**A**: 捕获401错误，清除Token，跳转到登录页。

### Q5: Agent响应超时怎么办？
**A**: 设置合理的超时时间（如30秒），超时后提示用户重试。

---

## 技术支持

- **API文档**: `http://localhost:5000/docs`
- **后端源码**: `/workspace/projects/src/`
- **前端参考**: `/workspace/projects/magic-school-frontend/`

---

**文档版本**: v1.0
**最后更新**: 2026-02-04
**维护者**: Coze Coding Team
