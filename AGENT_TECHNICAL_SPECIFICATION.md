# 🪄 魔法课桌学习助手智能体 - 技术实现详解

> 本文档详细描述了智能体的功能、API调用方案、用户认证、数据隔离和记忆长期化的具体实现方式

---

## 📋 目录

- [1. 智能体概述](#1-智能体概述)
- [2. 功能模块详解](#2-功能模块详解)
- [3. API调用方案](#3-api调用方案)
- [4. 用户认证实现](#4-用户认证实现)
- [5. 数据隔离实现](#5-数据隔离实现)
- [6. 记忆长期化实现](#6-记忆长期化实现)
- [7. 技术架构](#7-技术架构)
- [8. 安全机制](#8-安全机制)

---

## 1. 智能体概述

### 1.1 产品定位

魔法课桌学习助手智能体是一款基于LangGraph和多Agent架构的智能学习管理系统，专为小学生（6-12岁）和家长设计，以魔法学校为主题，将学习过程游戏化、趣味化。

### 1.2 核心特性

| 特性 | 说明 |
|------|------|
| **智能对话** | 基于LangGraph的多Agent架构，支持复杂的多轮对话 |
| **多用户支持** | 学生和家长双角色，完善的权限管理 |
| **长期记忆** | 记忆用户偏好、对话摘要、知识掌握度 |
| **数据隔离** | 完全的多租户数据隔离，确保数据安全 |
| **时间感知** | 自动获取和处理时间信息，明确时间参照 |
| **30+工具** | 课程管理、作业管理、成就系统、运动记录等 |

### 1.3 技术栈

```
后端架构:
├── Python 3.11
├── FastAPI (Web框架)
├── LangGraph (多Agent框架)
├── LangChain (LLM框架)
├── PostgreSQL (数据库)
├── SQLAlchemy (ORM)
└── WebSocket (实时通信)

AI能力:
├── 豆包大模型 (doubao-seed-1-6-251015)
├── 向量存储 (语义检索)
├── 长期记忆 (用户画像、对话摘要)
└── 工具调用 (30+功能工具)
```

---

## 2. 功能模块详解

### 2.1 智能对话中心 🧙‍♂️

#### 功能描述

智能对话中心是智能体的核心功能，基于LangGraph多Agent架构实现复杂的对话能力。

#### 核心能力

1. **自然语言理解**
   - 意图识别：理解用户想要做什么
   - 实体抽取：提取关键信息（人名、时间、科目等）
   - 上下文理解：理解对话历史和上下文

2. **工具调用**
   - 自动调用合适的工具完成任务
   - 支持串行和并行工具调用
   - 工具结果处理和反馈

3. **多轮对话**
   - 保持对话上下文
   - 支持澄清和追问
   - 自然流畅的对话体验

4. **启发式引导**
   - 引导思考而非直接给答案
   - 激发学习兴趣
   - 培养解决问题的能力

#### 可用工具（部分）

```
用户管理:
├── create_student_profile - 创建学生档案
├── get_student_profile - 获取学生信息
└── update_student_profile - 更新学生信息

课程管理:
├── create_course - 创建课程
├── get_course_schedule - 获取课程表
├── update_course - 更新课程信息
└── delete_course - 删除课程

作业管理:
├── create_homework - 创建作业
├── get_homeworks - 获取作业列表
├── update_homework_status - 更新作业状态
└── delete_homework - 删除作业

成就系统:
├── create_achievement - 创建成就
├── get_achievements - 获取成就列表
├── add_points - 增加积分
└── upgrade_magic_level - 升级魔法等级

运动记录:
├── record_exercise - 记录运动
├── get_exercise_history - 获取运动历史
└── get_exercise_stats - 获取运动统计

文件管理:
├── upload_file - 上传文件
├── get_file_url - 获取文件URL
└── list_student_files - 列出学生文件

记忆管理:
├── save_conversation_memory - 保存对话记忆
├── retrieve_relevant_memories - 检索相关记忆
├── update_user_profile - 更新用户画像
└── update_knowledge_mastery - 更新知识掌握度

会话管理:
├── create_conversation - 创建对话会话
├── get_conversations - 获取会话列表
├── search_conversations - 搜索对话会话
└── generate_conversation_title - 生成会话标题
```

#### 使用示例

```python
# 用户发送消息
user_message = "帮我查看今天的课程表"

# 智能体处理流程：
# 1. 意图识别 → "查询课程表"
# 2. 调用工具 → get_course_schedule()
# 3. 处理结果 → 格式化课程表
# 4. 生成回复 → "今天你有以下课程：..."

# 返回结果
response = {
    "message": "今天你有以下课程：\n08:00-09:30 语文课\n10:00-11:30 数学课\n14:00-15:30 英语课",
    "tool_calls": [
        {
            "tool": "get_course_schedule",
            "result": [...]
        }
    ]
}
```

---

### 2.2 历史对话管理 💬

#### 功能描述

提供完整的对话历史管理功能，支持对话会话的创建、查看、搜索和管理。

#### 核心功能

1. **对话会话管理**
   - 创建新的对话会话
   - 查看对话会话列表（按时间倒序）
   - 查看会话详情和完整历史
   - 更新会话标题
   - 删除对话会话

2. **智能标题生成**
   - 自动生成对话摘要标题
   - 基于对话内容提取关键信息
   - 支持批量生成标题

3. **对话搜索**
   - 按关键词搜索对话
   - 按时间范围筛选
   - 按对话类型筛选

#### 数据结构

```python
class Conversation(Base):
    """对话会话表"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    title = Column(String, default="新对话")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # 关联对话消息
    messages = relationship("ConversationMessage", back_populates="conversation")

class ConversationMessage(Base):
    """对话消息表"""
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String)  # user, assistant, system
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联对话会话
    conversation = relationship("Conversation", back_populates="messages")
```

#### API接口

```python
# 创建对话会话
POST /api/v1/conversations
{
    "user_id": "user123",
    "title": "关于数学的讨论"
}

# 获取对话列表
GET /api/v1/conversations?user_id=user123

# 搜索对话
GET /api/v1/conversations/search?user_id=user123&keyword=数学

# 生成会话标题
POST /api/v1/conversations/{id}/generate-title
```

---

### 2.3 课程日历 📅

#### 功能描述

管理学生的课程表，支持课程的时间管理和提醒功能。

#### 核心功能

1. **课程管理**
   - 创建、更新、删除课程
   - 查看课程表（周视图/月视图）
   - 课程时间提醒

2. **时间感知**
   - 自动标注时间参照
   - 支持相对时间表达（"明天"、"下周"）
   - 智能时间解析

#### 使用示例

```python
# 创建课程
{
    "course_name": "数学课",
    "course_type": "school",
    "weekday": "Monday",
    "start_time": "09:00",
    "end_time": "10:30",
    "teacher": "邓布利多老师",
    "room": "魔药教室"
}

# 查询课程表
{
    "weekday": "Monday",
    "courses": [
        {
            "course_name": "数学课",
            "time": "09:00-10:30",
            "teacher": "邓布利多老师",
            "room": "魔药教室"
        }
    ]
}
```

---

### 2.4 作业中心 📝

#### 功能描述

管理学生的作业，包括作业的创建、追踪和完成状态。

#### 核心功能

1. **作业管理**
   - 创建、更新、删除作业
   - 查看作业列表
   - 更新作业状态（待办/进行中/已完成）

2. **作业追踪**
   - 作业截止日期提醒
   - 作业完成统计
   - 作业优先级管理

#### 使用示例

```python
# 创建作业
{
    "title": "数学练习题",
    "subject": "数学",
    "description": "完成练习册第10页",
    "due_date": "2025-01-20",
    "priority": "high",
    "status": "pending"
}

# 查看作业列表
{
    "homeworks": [
        {
            "id": 1,
            "title": "数学练习题",
            "subject": "数学",
            "due_date": "2025-01-20",
            "priority": "high",
            "status": "pending",
            "days_left": 2
        }
    ]
}
```

---

### 2.5 成就系统 🏆

#### 功能描述

游戏化的成就系统，激励学生完成学习任务。

#### 核心功能

1. **成就管理**
   - 创建成就
   - 查看成就列表
   - 成就分类（学习、运动、阅读等）

2. **积分系统**
   - 积分增加和扣除
   - 魔法等级升级
   - 等级进度追踪

#### 成就类型

```
学习成就:
├── study_effort - 学习努力
├── homework_master - 作业达人
├── perfect_attendance - 全勤小达人
└── knowledge_expert - 知识小专家

运动成就:
├── sports_enthusiast - 运动爱好者
├── daily_exercise - 每日运动
└── marathon_runner - 马拉松跑者

阅读成就:
├── book_lover - 读书爱好者
├── reading_master - 阅读达人
└── story_teller - 故事大王

其他成就:
├── helpful_assistant - 助人为乐
├── creative_thinker - 创意思维
└── persistent_learner - 坚持学习
```

---

## 3. API调用方案

### 3.1 API架构

智能体采用RESTful API设计，支持同步和WebSocket两种通信方式。

```
API架构:
├── RESTful API (HTTP)
│   ├── 用户认证: /api/v1/auth/*
│   ├── 学生管理: /api/v1/students/*
│   ├── 课程管理: /api/v1/courses/*
│   ├── 作业管理: /api/v1/homeworks/*
│   ├── 成就管理: /api/v1/achievements/*
│   ├── 运动管理: /api/v1/exercises/*
│   ├── 文件管理: /api/v1/files/*
│   ├── 对话管理: /api/v1/conversations/*
│   └── 记忆管理: /api/v1/memory/*
│
└── WebSocket (实时通信)
    ├── /ws/chat - 实时对话
    ├── /ws/dashboard - 实时更新
    └── /ws/notifications - 实时通知
```

### 3.2 认证方式

所有受保护的API都需要JWT Token认证。

```python
# 请求头
Authorization: Bearer <access_token>

# 请求示例
GET /api/v1/students/123
Headers:
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3.3 完整API调用流程

```python
# 1. 用户注册
POST /api/v1/auth/register
{
    "username": "xiaoming",
    "password": "password123",
    "role": "student",
    "student_name": "小明",
    "grade": "三年级"
}

# 响应
{
    "success": true,
    "user_id": "usr_abc123",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

# 2. 用户登录
POST /api/v1/auth/login
{
    "username": "xiaoming",
    "password": "password123"
}

# 响应
{
    "success": true,
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

# 3. 使用Token访问受保护的API
GET /api/v1/students/dashboard
Headers:
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# 4. WebSocket连接（带Token）
ws://your-domain.com/ws/chat?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3.4 核心API接口

#### 3.4.1 用户认证API

```python
# 用户注册
POST /api/v1/auth/register
Request:
{
    "username": "xiaoming",
    "password": "password123",
    "role": "student",  # student | parent
    "student_name": "小明",  # 仅student需要
    "grade": "三年级"  # 仅student需要
}

# 用户登录
POST /api/v1/auth/login
Request:
{
    "username": "xiaoming",
    "password": "password123"
}

# 刷新Token
POST /api/v1/auth/refresh
Request:
{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

# 登出
POST /api/v1/auth/logout
Headers:
    Authorization: Bearer <access_token>
```

#### 3.4.2 智能对话API

```python
# 发送对话消息
POST /api/v1/chat
Headers:
    Authorization: Bearer <access_token>
Request:
{
    "message": "帮我查看今天的课程表",
    "session_id": "sess_123"
}

# 流式响应
Response:
{
    "type": "message",
    "content": "今天你有以下课程：...",
    "tool_calls": [...],
    "metadata": {...}
}

# WebSocket实时对话
ws://your-domain.com/ws/chat?token=<access_token>
Message:
{
    "type": "message",
    "content": "你好",
    "session_id": "sess_123"
}
```

#### 3.4.3 学生管理API

```python
# 获取学生仪表盘
GET /api/v1/students/dashboard/{student_name}
Headers:
    Authorization: Bearer <access_token>

# 创建学生档案
POST /api/v1/students
Request:
{
    "name": "小明",
    "grade": "三年级",
    "class_name": "三年级二班",
    "school": "霍格沃茨小学",
    "nickname": "小明"
}

# 更新学生档案
PUT /api/v1/students/{student_id}
Request:
{
    "nickname": "小魔法师",
    "avatar_url": "https://..."
}

# 增加积分
POST /api/v1/students/{student_id}/points
Request:
{
    "points": 50,
    "reason": "完成作业"
}

# 升级魔法等级
POST /api/v1/students/{student_id}/upgrade-level
```

#### 3.4.4 课程管理API

```python
# 获取课程表
GET /api/v1/courses/schedule/{student_name}
Headers:
    Authorization: Bearer <access_token>

# 创建课程
POST /api/v1/courses
Request:
{
    "student_id": 1,
    "course_name": "数学课",
    "course_type": "school",
    "weekday": "Monday",
    "start_time": "09:00",
    "end_time": "10:30",
    "teacher": "邓布利多老师",
    "room": "魔药教室"
}

# 更新课程
PUT /api/v1/courses/{course_id}

# 删除课程
DELETE /api/v1/courses/{course_id}
```

#### 3.4.5 作业管理API

```python
# 获取作业列表
GET /api/v1/homeworks?student_id=1
Headers:
    Authorization: Bearer <access_token>

# 创建作业
POST /api/v1/homeworks
Request:
{
    "student_id": 1,
    "title": "数学练习题",
    "subject": "数学",
    "description": "完成练习册第10页",
    "due_date": "2025-01-20",
    "priority": "high"
}

# 更新作业状态
PUT /api/v1/homeworks/{homework_id}/status
Request:
{
    "status": "completed"
}

# 删除作业
DELETE /api/v1/homeworks/{homework_id}
```

#### 3.4.6 成就管理API

```python
# 获取成就列表
GET /api/v1/achievements?student_id=1
Headers:
    Authorization: Bearer <access_token>

# 创建成就
POST /api/v1/achievements
Request:
{
    "student_id": 1,
    "achievement_type": "study_effort",
    "title": "学习努力",
    "description": "完成首次学习任务",
    "points": 10
}
```

#### 3.4.7 对话管理API

```python
# 创建对话会话
POST /api/v1/conversations
Request:
{
    "user_id": "usr_abc123",
    "title": "关于数学的讨论"
}

# 获取对话列表
GET /api/v1/conversations?user_id=usr_abc123

# 搜索对话
GET /api/v1/conversations/search?user_id=usr_abc123&keyword=数学

# 生成会话标题
POST /api/v1/conversations/{id}/generate-title

# 批量生成标题
POST /api/v1/conversations/batch-generate-titles
```

---

## 4. 用户认证实现

### 4.1 认证架构

采用JWT（JSON Web Token）认证机制，实现无状态的用户认证。

```
认证流程:
1. 用户注册 → 生成用户记录
2. 用户登录 → 验证密码 → 生成JWT Token
3. 每次请求 → 携带Token → 验证Token → 返回数据
```

### 4.2 数据库设计

```python
class User(Base):
    """用户表"""
    __tablename__ = "users"

    # 主键
    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True, nullable=False, index=True)

    # 基本信息
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # student | parent

    # 学生信息（仅student角色）
    student_name = Column(String, nullable=True)
    grade = Column(String, nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    # 状态
    is_active = Column(Boolean, default=True)

class ParentStudentMapping(Base):
    """家长-学生关联表"""
    __tablename__ = "parent_student_mapping"

    id = Column(Integer, primary_key=True)
    parent_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    student_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    relationship = Column(String)  # father | mother | guardian

    # 唯一约束：一个家长不能重复关联同一个学生
    __table_args__ = (
        UniqueConstraint('parent_id', 'student_id', name='uk_parent_student'),
    )

class UserSession(Base):
    """用户会话表"""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True)
    session_id = Column(String, unique=True, nullable=False)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    thread_id = Column(String, nullable=False)  # LangGraph线程ID

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow)

    # 状态
    is_active = Column(Boolean, default=True)
```

### 4.3 密码安全

```python
import bcrypt

class UserManager:
    """用户管理器"""

    @staticmethod
    def hash_password(password: str) -> str:
        """加密密码"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    @staticmethod
    def generate_jwt_token(user_id: str, role: str) -> str:
        """生成JWT Token"""
        import jwt
        from datetime import datetime, timedelta

        payload = {
            "user_id": user_id,
            "role": role,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=24)
        }

        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        return token

    @staticmethod
    def verify_jwt_token(token: str) -> dict:
        """验证JWT Token"""
        import jwt
        from datetime import datetime

        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

            # 检查是否过期
            if datetime.utcnow().timestamp() > payload["exp"]:
                return None

            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
```

### 4.4 认证中间件

```python
from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """获取当前用户"""
    token = credentials.credentials

    # 验证Token
    payload = UserManager.verify_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # 查询用户
    user = get_user_by_id(payload["user_id"])
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return {
        "user_id": user.user_id,
        "username": user.username,
        "role": user.role
    }

async def require_student(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """要求学生角色"""
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Student access only")
    return current_user

async def require_parent(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """要求家长角色"""
    if current_user["role"] != "parent":
        raise HTTPException(status_code=403, detail="Parent access only")
    return current_user
```

### 4.5 使用示例

```python
# API路由示例
from fastapi import APIRouter, Depends

router = APIRouter()

@router.post("/register")
async def register(data: dict):
    """用户注册"""
    # 1. 验证用户名是否已存在
    if get_user_by_username(data["username"]):
        raise HTTPException(status_code=400, detail="Username already exists")

    # 2. 加密密码
    password_hash = UserManager.hash_password(data["password"])

    # 3. 创建用户
    user = create_user(
        username=data["username"],
        password_hash=password_hash,
        role=data["role"],
        student_name=data.get("student_name"),
        grade=data.get("grade")
    )

    # 4. 生成Token
    access_token = UserManager.generate_jwt_token(user.user_id, user.role)

    return {
        "success": True,
        "user_id": user.user_id,
        "access_token": access_token
    }

@router.get("/dashboard")
async def get_dashboard(
    current_user: dict = Depends(require_student)
):
    """获取学生仪表盘（仅学生可访问）"""
    # current_user 包含用户信息
    student_id = current_user["user_id"]

    # 查询学生数据
    dashboard_data = get_student_dashboard(student_id)

    return dashboard_data

@router.get("/students/{student_id}")
async def get_student_info(
    student_id: str,
    current_user: dict = Depends(get_current_user)
):
    """获取学生信息（家长可访问关联的学生）"""
    # 如果是学生，只能访问自己的信息
    if current_user["role"] == "student":
        if student_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")

    # 如果是家长，只能访问关联的学生
    if current_user["role"] == "parent":
        if not is_parent_linked_to_student(current_user["user_id"], student_id):
            raise HTTPException(status_code=403, detail="Not linked to this student")

    # 查询学生信息
    student = get_student_by_id(student_id)

    return student
```

---

## 5. 数据隔离实现

### 5.1 隔离架构

采用**多租户数据隔离**架构，确保每个用户的数据完全隔离。

```
隔离层次:
1. 用户级别隔离
   └── 每个用户只能访问自己的数据

2. 角色级别隔离
   └── 学生和家长有不同的数据访问权限

3. 家长-学生关联隔离
   └── 家长只能访问关联的学生数据
```

### 5.2 数据库设计

所有业务表都包含 `student_id` 字段，实现数据隔离。

```python
class Student(Base):
    """学生表"""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"))  # 关联用户

    # 学生信息
    name = Column(String, nullable=False)
    grade = Column(String)
    class_name = Column(String)
    school = Column(String)

    # 魔法元素
    magic_level = Column(Integer, default=1)
    total_points = Column(Integer, default=0)

class Homework(Base):
    """作业表"""
    __tablename__ = "homeworks"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)  # 隔离字段

    # 作业信息
    title = Column(String, nullable=False)
    subject = Column(String)
    description = Column(Text)
    due_date = Column(DateTime)
    priority = Column(String)
    status = Column(String)

class Course(Base):
    """课程表"""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)  # 隔离字段

    # 课程信息
    course_name = Column(String, nullable=False)
    course_type = Column(String)
    weekday = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    teacher = Column(String)
    room = Column(String)

class Achievement(Base):
    """成就表"""
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)  # 隔离字段

    # 成就信息
    achievement_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    points = Column(Integer)
    earned_at = Column(DateTime, default=datetime.utcnow)
```

### 5.3 工具隔离

所有工具都接收 `runtime` 参数，包含用户信息。

```python
from langchain.tools import tool, ToolRuntime
from coze_coding_utils.runtime_ctx.context import new_context

@tool
def create_homework(
    title: str,
    subject: str,
    due_date: str,
    runtime: ToolRuntime = None
) -> str:
    """创建作业（工具隔离）"""
    # 获取用户信息
    ctx = runtime.context if runtime else new_context(method="create_homework")
    user_id = ctx.get("configurable", {}).get("user_id")
    user_role = ctx.get("configurable", {}).get("user_role")

    # 验证用户角色
    if user_role == "parent":
        # 家长需要指定学生ID
        student_id = ctx.get("configurable", {}).get("student_id")
        if not student_id:
            return "请先选择要操作的学生"
    else:
        # 学生使用自己的ID
        student_id = user_id

    # 验证数据隔离
    if user_role == "parent":
        # 检查家长是否关联了该学生
        if not is_parent_linked_to_student(user_id, student_id):
            return "您没有权限访问该学生的数据"

    # 创建作业
    db = get_session()
    homework = HomeworkManager().create_homework(db, HomeworkCreate(
        student_id=student_id,
        title=title,
        subject=subject,
        due_date=due_date,
        priority="medium"
    ))

    return f"作业已创建：{homework.title}"

@tool
def get_homeworks(runtime: ToolRuntime = None) -> str:
    """获取作业列表（工具隔离）"""
    # 获取用户信息
    ctx = runtime.context if runtime else new_context(method="get_homeworks")
    user_id = ctx.get("configurable", {}).get("user_id")
    user_role = ctx.get("configurable", {}).get("user_role")

    # 获取学生ID
    if user_role == "parent":
        # 家长需要指定学生ID
        student_id = ctx.get("configurable", {}).get("student_id")
        if not student_id:
            return "请先选择要查看的学生"
    else:
        # 学生使用自己的ID
        student_id = user_id

    # 查询作业（自动隔离）
    db = get_session()
    homeworks = HomeworkManager().get_student_homeworks(db, student_id)

    # 格式化结果
    result = f"找到 {len(homeworks)} 个作业：\n"
    for hw in homeworks:
        result += f"- {hw.title} ({hw.subject}) - {hw.status}\n"

    return result
```

### 5.4 Agent配置

Agent在构建时传入用户上下文，实现会话隔离。

```python
def build_agent(ctx=None):
    """构建Agent（会话隔离）"""
    # 获取配置
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    # 创建LLM
    llm = ChatOpenAI(
        model=cfg['config'].get("model"),
        api_key=api_key,
        base_url=base_url,
        temperature=cfg['config'].get('temperature', 0.7),
        default_headers=default_headers(ctx) if ctx else {}
    )

    # 创建工具（包含隔离逻辑）
    tools = [
        create_homework,
        get_homeworks,
        create_course,
        get_courses,
        # ... 其他工具
    ]

    # 创建Agent
    agent = create_agent(
        model=llm,
        system_prompt=cfg.get("sp"),
        tools=tools,
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )

    return agent

# 使用Agent
@app.post("/api/v1/chat")
async def chat(
    message: str,
    current_user: dict = Depends(get_current_user)
):
    """对话接口"""
    # 获取或创建会话
    thread_id = session_manager.get_or_create_session(current_user["user_id"])

    # 配置用户上下文
    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": current_user["user_id"],
            "user_role": current_user["role"]
        }
    }

    # 调用Agent
    agent = build_agent(ctx=new_context(method="chat", configurable=config))
    result = await agent.ainvoke({"messages": [HumanMessage(content=message)]}, config=config)

    return result
```

### 5.5 测试验证

```python
# 数据隔离测试
def test_data_isolation():
    """测试数据隔离"""
    # 创建两个学生
    student1 = create_student("张小明")
    student2 = create_student("李小红")

    # 为student1创建作业
    homework1 = create_homework(
        student_id=student1.id,
        title="张小明的数学作业"
    )

    # 为student2创建作业
    homework2 = create_homework(
        student_id=student2.id,
        title="李小红的英语作业"
    )

    # student1只能看到自己的作业
    homeworks_1 = get_student_homeworks(student1.id)
    assert len(homeworks_1) == 1
    assert homeworks_1[0].title == "张小明的数学作业"

    # student2只能看到自己的作业
    homeworks_2 = get_student_homeworks(student2.id)
    assert len(homeworks_2) == 1
    assert homeworks_2[0].title == "李小红的英语作业"

    print("✅ 数据隔离测试通过")
```

---

## 6. 记忆长期化实现

### 6.1 记忆架构

采用**分层记忆系统**，实现智能的长期记忆管理。

```
记忆层次:
1. 对话记忆（短期）
   └── 存储对话摘要和关键信息
   └── 保留最近N轮对话

2. 用户画像（中期）
   └── 存储用户偏好和特征
   └── 持久化存储

3. 知识掌握度（长期）
   └── 存储知识点掌握情况
   └── 支持知识图谱

4. 行为偏好（长期）
   └── 存储用户行为模式
   └── 个性化推荐
```

### 6.2 数据库设计

```python
class UserProfile(Base):
    """用户画像表"""
    __tablename__ = "user_profile"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)

    # 基本画像
    name = Column(String)
    grade = Column(String)
    school = Column(String)

    # 学习偏好
    favorite_subjects = Column(JSON)  # 喜欢的科目
    learning_style = Column(String)  # 学习风格
    difficulty_preference = Column(String)  # 难度偏好

    # 兴趣爱好
    hobbies = Column(JSON)  # 爱好
    interests = Column(JSON)  # 兴趣

    # 更新时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ConversationSummary(Base):
    """对话摘要表"""
    __tablename__ = "conversation_summary"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    thread_id = Column(String, nullable=False)  # 对话线程ID

    # 摘要内容
    summary = Column(Text, nullable=False)  # 对话摘要
    topics = Column(JSON)  # 讨论的主题
    key_points = Column(JSON)  # 关键点

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)

class KnowledgeMastery(Base):
    """知识掌握度表"""
    __tablename__ = "knowledge_mastery"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)

    # 知识点
    subject = Column(String, nullable=False)  # 科目
    topic = Column(String, nullable=False)  # 主题
    knowledge_point = Column(String, nullable=False)  # 知识点

    # 掌握度
    mastery_level = Column(Integer, default=0)  # 0-100
    confidence_level = Column(Integer, default=0)  # 信心度

    # 学习记录
    last_practiced = Column(DateTime)  # 最后练习时间
    practice_count = Column(Integer, default=0)  # 练习次数
    correct_count = Column(Integer, default=0)  # 正确次数

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BehaviorPreferences(Base):
    """行为偏好表"""
    __tablename__ = "behavior_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)

    # 行为模式
    preferred_response_style = Column(String)  # 喜欢的回复风格
    interaction_frequency = Column(String)  # 交互频率偏好
    time_preference = Column(JSON)  # 时间偏好

    # 反馈数据
    feedback_history = Column(JSON)  # 反馈历史

    # 时间戳
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 6.3 记忆工具实现

```python
@tool
def save_conversation_memory(
    conversation: str,
    runtime: ToolRuntime = None
) -> str:
    """保存对话记忆"""
    # 获取用户信息
    ctx = runtime.context if runtime else new_context(method="save_conversation_memory")
    user_id = ctx.get("configurable", {}).get("user_id")
    thread_id = ctx.get("configurable", {}).get("thread_id")

    # 生成摘要
    summary = generate_conversation_summary(conversation)

    # 提取主题
    topics = extract_topics(conversation)

    # 提取关键点
    key_points = extract_key_points(conversation)

    # 保存到数据库
    db = get_session()
    conv_summary = ConversationSummary(
        user_id=user_id,
        thread_id=thread_id,
        summary=summary,
        topics=topics,
        key_points=key_points
    )
    db.add(conv_summary)
    db.commit()

    return "对话记忆已保存"

@tool
def retrieve_relevant_memories(
    query: str,
    runtime: ToolRuntime = None
) -> str:
    """检索相关记忆"""
    # 获取用户信息
    ctx = runtime.context if runtime else new_context(method="retrieve_relevant_memories")
    user_id = ctx.get("configurable", {}).get("user_id")

    # 查询相关对话摘要
    db = get_session()
    summaries = db.query(ConversationSummary).filter(
        ConversationSummary.user_id == user_id
    ).order_by(ConversationSummary.created_at.desc()).limit(10).all()

    # 语义匹配
    relevant_memories = []
    for summary in summaries:
        similarity = calculate_similarity(query, summary.summary)
        if similarity > 0.7:
            relevant_memories.append({
                "summary": summary.summary,
                "topics": summary.topics,
                "created_at": summary.created_at.isoformat()
            })

    # 格式化结果
    if relevant_memories:
        result = "找到相关记忆：\n"
        for memory in relevant_memories:
            result += f"- {memory['summary']}\n"
    else:
        result = "没有找到相关记忆"

    return result

@tool
def update_user_profile(
    key: str,
    value: str,
    runtime: ToolRuntime = None
) -> str:
    """更新用户画像"""
    # 获取用户信息
    ctx = runtime.context if runtime else new_context(method="update_user_profile")
    user_id = ctx.get("configurable", {}).get("user_id")

    # 查询用户画像
    db = get_session()
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()

    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)

    # 更新字段
    if hasattr(profile, key):
        setattr(profile, key, value)
    else:
        # 处理JSON字段
        if key == "favorite_subjects":
            profile.favorite_subjects = profile.favorite_subjects or []
            profile.favorite_subjects.append(value)
        elif key == "hobbies":
            profile.hobbies = profile.hobbies or []
            profile.hobbies.append(value)

    db.commit()

    return f"用户画像已更新：{key} = {value}"

@tool
def update_knowledge_mastery(
    subject: str,
    topic: str,
    knowledge_point: str,
    mastery_level: int,
    runtime: ToolRuntime = None
) -> str:
    """更新知识掌握度"""
    # 获取用户信息
    ctx = runtime.context if runtime else new_context(method="update_knowledge_mastery")
    user_id = ctx.get("configurable", {}).get("user_id")

    # 查询知识掌握度
    db = get_session()
    mastery = db.query(KnowledgeMastery).filter(
        KnowledgeMastery.user_id == user_id,
        KnowledgeMastery.subject == subject,
        KnowledgeMastery.topic == topic,
        KnowledgeMastery.knowledge_point == knowledge_point
    ).first()

    if not mastery:
        mastery = KnowledgeMastery(
            user_id=user_id,
            subject=subject,
            topic=topic,
            knowledge_point=knowledge_point
        )
        db.add(mastery)

    # 更新掌握度
    mastery.mastery_level = mastery_level
    mastery.last_practiced = datetime.utcnow()
    mastery.practice_count += 1

    db.commit()

    return f"知识掌握度已更新：{subject} - {topic} - {knowledge_point} = {mastery_level}%"
```

### 6.4 记忆检索流程

```python
def retrieve_memories_for_context(
    user_id: str,
    query: str,
    max_memories: int = 5
) -> List[str]:
    """检索记忆用于构建上下文"""
    # 1. 查询用户画像
    profile = get_user_profile(user_id)

    # 2. 查询对话摘要
    summaries = get_conversation_summaries(user_id, limit=10)

    # 3. 查询知识掌握度
    mastery = get_knowledge_mastery(user_id)

    # 4. 语义匹配
    relevant_memories = []

    # 匹配对话摘要
    for summary in summaries:
        similarity = calculate_similarity(query, summary.summary)
        if similarity > 0.7:
            relevant_memories.append(f"历史对话：{summary.summary}")

    # 匹配用户画像
    if profile and profile.favorite_subjects:
        for subject in profile.favorite_subjects:
            if subject in query:
                relevant_memories.append(f"用户偏好：喜欢{subject}")

    # 匹配知识掌握度
    for m in mastery:
        if m.topic in query or m.knowledge_point in query:
            relevant_memories.append(
                f"知识掌握度：{m.subject} - {m.topic} - {m.knowledge_point} = {m.mastery_level}%"
            )

    # 5. 限制数量
    relevant_memories = relevant_memories[:max_memories]

    return relevant_memories

# 在Agent中使用
async def chat_with_memory(message: str, user_id: str):
    """带记忆的对话"""
    # 1. 检索相关记忆
    memories = retrieve_memories_for_context(user_id, message)

    # 2. 构建系统提示
    system_prompt = f"""你是一个魔法学习助手。

用户的相关记忆：
{chr(10).join(memories)}

请根据用户的记忆，提供个性化的回答。
"""

    # 3. 调用LLM
    response = await llm.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=message)
    ])

    # 4. 保存对话记忆
    save_conversation_memory(message, response.content, user_id)

    return response
```

### 6.5 记忆优化策略

```python
# 记忆清理策略
def cleanup_old_memories(user_id: str, days: int = 90):
    """清理旧记忆"""
    db = get_session()

    # 删除90天前的对话摘要
    db.query(ConversationSummary).filter(
        ConversationSummary.user_id == user_id,
        ConversationSummary.created_at < datetime.utcnow() - timedelta(days=days)
    ).delete()

    db.commit()

# 记忆合并策略
def merge_similar_memories(user_id: str):
    """合并相似记忆"""
    db = get_session()

    # 查询所有对话摘要
    summaries = db.query(ConversationSummary).filter(
        ConversationSummary.user_id == user_id
    ).all()

    # 计算相似度矩阵
    similarity_matrix = calculate_similarity_matrix([s.summary for s in summaries])

    # 合并相似的记忆
    merged = []
    for i in range(len(summaries)):
        for j in range(i + 1, len(summaries)):
            if similarity_matrix[i][j] > 0.9:  # 非常相似
                merged.append((summaries[i], summaries[j]))

    # 执行合并
    for s1, s2 in merged:
        merged_summary = merge_summaries(s1, s2)
        s1.summary = merged_summary
        db.delete(s2)

    db.commit()
```

---

## 7. 技术架构

### 7.1 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         前端应用                              │
│  (React + TypeScript + Ant Design + Tailwind CSS)            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ HTTP/WebSocket
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                       FastAPI 后端                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              路由层 (API Routes)                     │    │
│  │  - /api/v1/auth/* (认证)                            │    │
│  │  - /api/v1/students/* (学生管理)                    │    │
│  │  - /api/v1/courses/* (课程管理)                     │    │
│  │  - /api/v1/homeworks/* (作业管理)                   │    │
│  │  - /api/v1/chat/* (对话接口)                        │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              业务层 (Business Logic)                 │    │
│  │  - UserManager (用户管理)                           │    │
│  │  - StudentManager (学生管理)                        │    │
│  │  - HomeworkManager (作业管理)                       │    │
│  │  - CourseManager (课程管理)                         │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Agent层 (LangGraph Agent)               │    │
│  │  - Multi-Agent架构                                  │    │
│  │  - 工具调用 (30+ tools)                             │    │
│  │  - 长期记忆管理                                      │    │
│  │  - 数据隔离                                         │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              数据层 (Data Access)                    │    │
│  │  - SQLAlchemy ORM                                    │    │
│  │  - PostgreSQL数据库                                  │    │
│  │  - 会话管理 (Session Manager)                        │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ SQL
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    PostgreSQL 数据库                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  auth       │  │  public     │  │  memory     │         │
│  │  schema     │  │  schema     │  │  schema     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Agent架构

```
LangGraph Multi-Agent架构:

┌─────────────────────────────────────────────────────────┐
│                     Root Agent                           │
│  - 协调子Agent                                           │
│  - 分配任务                                              │
│  - 整合结果                                              │
└──────────┬──────────┬──────────┬──────────┬──────────────┘
           │          │          │          │
    ┌──────▼──────┐ ┌▼──────┐ ┌▼──────┐ ┌▼────────┐
    │  Student    │ │  Chat  │ │ Admin │ │ Parent  │
    │  Agent      │ │  Agent │ │ Agent │ │  Agent  │
    └──────┬──────┘ └───────┘ └───────┘ └─────────┘
           │
    ┌──────▼──────┐ ┌──────┐ ┌──────┐ ┌──────┐
    │  Tools      │ │ Tools│ │Tools │ │Tools │
    │  (30+)      │ │      │ │      │ │      │
    └─────────────┘ └──────┘ └──────┘ └──────┘
```

### 7.3 数据流图

```
用户请求流程:

用户 → 前端 → API → 认证中间件 → Agent → 工具调用 → 数据库
                            ↓
                    用户上下文注入
                            ↓
                        会话隔离
                            ↓
                        数据隔离
                            ↓
                        记忆检索
```

---

## 8. 安全机制

### 8.1 认证安全

- ✅ 密码加密（bcrypt）
- ✅ JWT Token认证
- ✅ Token过期机制（24小时）
- ✅ Refresh Token机制
- ✅ 防暴力破解（失败次数限制）

### 8.2 数据安全

- ✅ SQL注入防护（ORM参数化查询）
- ✅ XSS防护（输入验证和输出编码）
- ✅ CSRF防护（Token验证）
- ✅ 数据隔离（多租户架构）
- ✅ 敏感数据加密

### 8.3 API安全

- ✅ HTTPS加密传输
- ✅ 速率限制
- ✅ 请求大小限制
- ✅ IP白名单（可选）
- ✅ API Key管理

---

## 9. 总结

本智能体实现了以下核心特性：

### 9.1 功能完整性
- ✅ 智能对话系统（基于LangGraph）
- ✅ 多用户架构（学生/家长）
- ✅ 30+功能工具
- ✅ 长期记忆系统
- ✅ 数据完全隔离

### 9.2 技术先进性
- ✅ 多Agent架构
- ✅ 向量检索
- ✅ 语义理解
- ✅ 上下文保持
- ✅ 流式响应

### 9.3 安全可靠性
- ✅ JWT认证
- ✅ 数据隔离
- ✅ 权限管理
- ✅ 加密存储
- ✅ 审计日志

### 9.4 可扩展性
- ✅ 模块化设计
- ✅ 工具可扩展
- ✅ 数据库可扩展
- ✅ API版本管理
- ✅ 微服务架构支持

---

**本文档提供了智能体的完整技术实现说明，可以作为开发和维护的参考。**
