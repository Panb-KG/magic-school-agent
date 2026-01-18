# 多用户架构功能说明

## 🎉 新功能概述

本次更新为魔法课桌学习助手智能体添加了以下重要功能：

### 1. 📚 长期记忆系统
- ✅ 对话摘要自动保存
- ✅ 用户画像管理
- ✅ 知识掌握度跟踪
- ✅ 智能记忆检索

### 2. 👥 多用户架构
- ✅ 用户注册和登录（学生/家长）
- ✅ JWT 令牌认证
- ✅ 会话隔离（每个用户独立的对话上下文）
- ✅ 数据完全隔离

### 3. 👨‍👩‍👧‍👦 家长功能
- ✅ 家长-学生关联管理
- ✅ 查看学生对话历史
- ✅ 修改学生作业
- ✅ 奖励魔法积分
- ✅ 审核作业完成情况
- ✅ 查看学生学习仪表盘

---

## 🚀 快速开始

### 1. 初始化数据库

```bash
# 执行数据库初始化脚本
python scripts/init_database.py
```

这将创建以下表结构：

**auth schema**（用户认证）:
- `auth.users` - 用户表
- `auth.parent_student_mapping` - 家长-学生关联表
- `auth.permissions` - 权限定义表
- `auth.role_permissions` - 角色权限关联表
- `auth.user_sessions` - 用户会话表

**memory schema**（长期记忆）:
- `memory.user_profile` - 用户画像
- `memory.conversation_summary` - 对话摘要
- `memory.knowledge_mastery` - 知识掌握度
- `memory.behavior_preferences` - 行为偏好
- `memory.important_conversations` - 重要对话

### 2. 运行测试

```bash
# 运行功能测试
python tests/test_multiuser.py
```

测试将验证以下功能：
- 用户注册（学生和家长）
- 用户登录和令牌验证
- 家长-学生关联
- 会话管理
- 长期记忆存储
- 权限系统
- 数据隔离

---

## 📖 使用指南

### 用户注册

**注册学生账号：**
```python
from auth.user_manager import user_manager

result = user_manager.register_user(
    username="xiaoming",
    password="password123",
    role="student",
    student_name="小明",
    grade="三年级"
)

if result["success"]:
    print(f"注册成功！用户 ID: {result['user_id']}")
    print(f"访问令牌: {result['access_token']}")
```

**注册家长账号：**
```python
result = user_manager.register_user(
    username="xiaoming_mom",
    password="password123",
    role="parent"
)
```

### 用户登录

```python
result = user_manager.login_user("xiaoming", "password123")

if result["success"]:
    access_token = result["access_token"]
    # 使用 access_token 调用 API
```

### 关联家长和学生

```python
# 家长关联学生
result = user_manager.link_parent_student(
    parent_id="parent_user_id",
    student_id="student_user_id",
    relationship="mother"
)
```

### 会话管理

```python
from storage.session import session_manager

# 获取或创建用户会话
thread_id = session_manager.get_or_create_session(user_id)

# 使用 thread_id 进行 Agent 对话
config = {
    "configurable": {
        "thread_id": thread_id,
        "user_id": user_id,
        "user_role": "student"
    }
}
```

### 长期记忆功能

**保存对话记忆：**
```python
from tools.memory_tool import save_conversation_memory

result = save_conversation_memory.invoke({
    "conversation": "最近对话内容...",
    "runtime": runtime_context
})
```

**检索相关记忆：**
```python
from tools.memory_tool import retrieve_relevant_memories

result = retrieve_relevant_memories.invoke({
    "query": "分数的概念",
    "runtime": runtime_context
})
```

### 家长功能

**查看学生列表：**
```python
from tools.parent_tool import parent_view_student_list

result = parent_view_student_list.invoke({
    "runtime": runtime_context
})
```

**查看学生对话历史：**
```python
from tools.parent_tool import parent_view_student_conversations

result = parent_view_student_conversations.invoke({
    "student_id": "student_user_id",
    "limit": 10,
    "runtime": runtime_context
})
```

**奖励积分：**
```python
from tools.parent_tool import parent_reward_points

result = parent_reward_points.invoke({
    "student_id": "student_user_id",
    "points": 10,
    "reason": "作业完成得很好",
    "runtime": runtime_context
})
```

---

## 🔌 API 使用

### 启动 API 服务

```bash
# 启动 FastAPI 服务
python -m src.api.multiuser_api
```

服务将在 `http://localhost:8000` 启动。

### API 端点

#### 认证相关

**注册用户：**
```bash
POST /api/auth/register
Content-Type: application/json

{
  "username": "xiaoming",
  "password": "password123",
  "role": "student",
  "student_name": "小明",
  "grade": "三年级"
}
```

**用户登录：**
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "xiaoming",
  "password": "password123"
}
```

#### 家长功能

**获取关联的学生列表：**
```bash
GET /api/parent/students
Authorization: Bearer <access_token>
```

**奖励积分：**
```bash
POST /api/parent/reward-points
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "student_id": "student_user_id",
  "points": 10,
  "reason": "作业完成得很好"
}
```

**修改作业：**
```bash
PUT /api/parent/homework/{homework_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "student_id": "student_user_id",
  "homework_id": 1,
  "title": "新的作业标题",
  "description": "新的作业描述"
}
```

---

## 🔒 权限系统

### 角色类型

| 角色 | 描述 |
|------|------|
| `student` | 学生角色，只能访问自己的数据 |
| `parent` | 家长角色，可以管理关联的学生数据 |

### 权限列表

| 权限 ID | 描述 | 学生 | 家长 |
|---------|------|------|------|
| `view_own_data` | 查看自己的数据 | ✅ | ✅ |
| `view_student_data` | 查看关联学生的数据 | ❌ | ✅ |
| `edit_own_homework` | 提交自己的作业 | ✅ | ❌ |
| `edit_student_homework` | 修改学生的作业 | ❌ | ✅ |
| `edit_course` | 编辑课程信息 | ❌ | ✅ |
| `view_chat_history` | 查看对话历史 | ❌ | ✅ |
| `add_points` | 添加魔法积分 | ❌ | ✅ |
| `approve_homework` | 批准作业 | ❌ | ✅ |

---

## 🗂️ 数据库表结构

### 用户相关表

**auth.users**
```sql
CREATE TABLE auth.users (
    user_id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student',
    student_name VARCHAR(50),
    grade VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**auth.parent_student_mapping**
```sql
CREATE TABLE auth.parent_student_mapping (
    mapping_id SERIAL PRIMARY KEY,
    parent_id VARCHAR(50) NOT NULL,
    student_id VARCHAR(50) NOT NULL,
    relationship VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 记忆相关表

**memory.user_profile**
```sql
CREATE TABLE memory.user_profile (
    profile_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    preferences JSONB DEFAULT '{}',
    learning_goals TEXT,
    learning_style VARCHAR(50),
    favorite_subjects TEXT[],
    weak_subjects TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);
```

**memory.conversation_summary**
```sql
CREATE TABLE memory.conversation_summary (
    summary_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    thread_id VARCHAR(50) NOT NULL,
    topic VARCHAR(200),
    summary_text TEXT NOT NULL,
    key_points JSONB DEFAULT '[]',
    emotion VARCHAR(50),
    importance_score INTEGER DEFAULT 0,
    conversation_date TIMESTAMP DEFAULT NOW()
);
```

---

## 🧪 测试

运行完整的测试套件：

```bash
python tests/test_multiuser.py
```

测试涵盖：
- ✅ 用户注册（学生和家长）
- ✅ 用户登录和令牌验证
- ✅ 家长-学生关联
- ✅ 会话管理（thread_id 隔离）
- ✅ 长期记忆存储
- ✅ 权限系统
- ✅ 数据隔离

---

## 📝 注意事项

1. **安全性**
   - 生产环境中请修改 `JWT_SECRET_KEY`
   - 使用 HTTPS 传输令牌
   - 定期轮换密钥

2. **性能优化**
   - 定期清理过期的对话摘要
   - 对记忆表添加适当的索引
   - 使用连接池管理数据库连接

3. **数据备份**
   - 定期备份 `auth` 和 `memory` schema
   - 保留用户数据的完整性

---

## 🤝 贡献

如有问题或建议，欢迎反馈！

---

## 📄 许可证

本软件为魔法课桌学习助手智能体的一部分。
