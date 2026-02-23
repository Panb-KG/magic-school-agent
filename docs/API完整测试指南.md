# 魔法课桌学习助手智能体 - API 完整测试指南

## 📋 文档信息

- **文档版本**: 1.0.0
- **创建日期**: 2025年1月
- **智能体名称**: 魔法课桌学习助手智能体
- **测试类型**: API 集成测试
- **测试工具**: curl / Postman / Apifox

---

## 🎯 测试目标

本文档提供完整的API测试指南，覆盖智能体的所有功能模块，确保新部署的版本功能正常。

---

## 📌 测试准备

### 1. API 基础信息

**Base URL**: `https://your-domain.com/api`

**认证方式**: JWT Bearer Token

**Content-Type**: `application/json`

### 2. 获取认证 Token

#### 方式一：通过登录接口

```bash
curl -X POST "https://your-domain.com/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

**预期响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "user123",
  "user_role": "student"
}
```

#### 方式二：通过扣子平台

如果你使用扣子平台，使用扣子提供的 API Token：

1. 登录扣子平台
2. 进入个人中心 → API 管理
3. 复制 API Token

### 3. 设置环境变量（推荐）

```bash
# 设置 Base URL
export API_BASE_URL="https://your-domain.com/api"

# 设置认证 Token
export API_TOKEN="your_jwt_token_here"

# 设置学生 ID（如果有）
export STUDENT_ID=1

# 设置对话 ID（如果有）
export CONVERSATION_ID=100
```

### 4. 通用请求函数（Postman/脚本）

**Bash 函数示例**:

```bash
# 通用 API 请求函数
api_request() {
  local method=$1
  local endpoint=$2
  local data=$3

  curl -X "${method}" "${API_BASE_URL}${endpoint}" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${API_TOKEN}" \
    -d "${data}" \
    -w "\n--- HTTP Status: %{http_code}\n" \
    -s
}

# GET 请求
api_get() {
  api_request "GET" "$1" ""
}

# POST 请求
api_post() {
  api_request "POST" "$1" "$2"
}

# PUT 请求
api_put() {
  api_request "PUT" "$1" "$2"
}

# DELETE 请求
api_delete() {
  api_request "DELETE" "$1" ""
}
```

---

## 🧪 功能模块测试

---

## 模块一：基础对话功能

### 1.1 发送对话消息

**测试目的**: 验证智能体能够正常响应对话

**API 端点**: `POST /chat`

**curl 命令**:
```bash
curl -X POST "${API_BASE_URL}/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -d '{
    "message": "你好，请自我介绍一下",
    "user_id": "user123"
  }'
```

**预期响应**:
```json
{
  "conversation_id": 1,
  "message_id": 1,
  "response": "✨ 你好呀！我是你的魔法课桌学习助手...",
  "timestamp": "2025-01-20T10:00:00Z"
}
```

**验证点**:
- [ ] 状态码 200
- [ ] response 不为空
- [ ] 内容符合预期
- [ ] 包含对话ID

---

### 1.2 流式对话（WebSocket）

**测试目的**: 验证 WebSocket 流式响应

**WebSocket 端点**: `wss://your-domain.com/ws/chat`

**测试代码（JavaScript）**:
```javascript
const ws = new WebSocket('wss://your-domain.com/ws/chat?token=' + YOUR_TOKEN);

ws.onopen = () => {
  console.log('✅ WebSocket 连接已建立');

  // 发送消息
  ws.send(JSON.stringify({
    type: 'message',
    message: '你好，请自我介绍一下',
    user_id: 'user123'
  }));
};

ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log('📨 收到消息:', response);

  if (response.type === 'agent_reply') {
    console.log('🤖 助手回复:', response.content);
  }
};

ws.onerror = (error) => {
  console.error('❌ WebSocket 错误:', error);
};

ws.onclose = () => {
  console.log('🔌 WebSocket 连接已关闭');
};
```

---

## 模块二：时间魔法功能

### 2.1 获取当前时间

**API 端点**: `POST /tools/get_current_time`

**curl 命令**:
```bash
curl -X POST "${API_BASE_URL}/tools/get_current_time" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -d '{}'
```

**预期响应**:
```json
{
  "current_time": "2025-01-20 10:30:00",
  "date": "2025-01-20",
  "time": "10:30:00",
  "weekday": "星期一",
  "year": 2025,
  "month": 1,
  "day": 20
}
```

---

### 2.2 获取本周日期范围

**API 端点**: `POST /tools/get_week_date_range`

**curl 命令**:
```bash
curl -X POST "${API_BASE_URL}/tools/get_week_date_range" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -d '{}'
```

**预期响应**:
```json
{
  "start_date": "2025-01-20",
  "end_date": "2025-01-26",
  "start_weekday": "星期一",
  "end_weekday": "星期日",
  "year": 2025,
  "week_number": 4
}
```

---

## 模块三：学生管理功能

### 3.1 创建学生

**API 端点**: `POST /students`

**curl 命令**:
```bash
curl -X POST "${API_BASE_URL}/students" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -d '{
    "name": "测试学生小明",
    "grade": "三年级",
    "class_name": "三（1）班",
    "school": "魔法小学",
    "parent_contact": "13800000000",
    "nickname": "小明"
  }'
```

**预期响应**:
```json
{
  "id": 100,
  "name": "测试学生小明",
  "grade": "三年级",
  "class_name": "三（1）班",
  "school": "魔法小学",
  "nickname": "小明",
  "magic_level": 1,
  "total_points": 0,
  "created_at": "2025-01-20T10:30:00Z"
}
```

**验证点**:
- [ ] 状态码 201
- [ ] 返回学生ID
- [ ] 魔法等级默认为1
- [ ] 积分默认为0

---

### 3.2 获取学生列表

**API 端点**: `GET /students`

**curl 命令**:
```bash
curl -X GET "${API_BASE_URL}/students" \
  -H "Authorization: Bearer ${API_TOKEN}"
```

**预期响应**:
```json
{
  "total": 5,
  "students": [
    {
      "id": 1,
      "name": "小明",
      "grade": "三年级",
      "magic_level": 2,
      "total_points": 150
    },
    {
      "id": 100,
      "name": "测试学生小明",
      "grade": "三年级",
      "magic_level": 1,
      "total_points": 0
    }
  ]
}
```

---

### 3.3 获取学生详情

**API 端点**: `GET /students/{student_id}`

**curl 命令**:
```bash
curl -X GET "${API_BASE_URL}/students/100" \
  -H "Authorization: Bearer ${API_TOKEN}"
```

**预期响应**:
```json
{
  "id": 100,
  "name": "测试学生小明",
  "grade": "三年级",
  "class_name": "三（1）班",
  "school": "魔法小学",
  "nickname": "小明",
  "magic_level": 1,
  "total_points": 0,
  "is_active": true,
  "created_at": "2025-01-20T10:30:00Z",
  "updated_at": null
}
```

---

### 3.4 增加学生积分

**API 端点**: `POST /students/{student_id}/add-points`

**curl 命令**:
```bash
curl -X POST "${API_BASE_URL}/students/100/add-points" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -d '{
    "points": 20,
    "reason": "完成作业奖励"
  }'
```

**预期响应**:
```json
{
  "success": true,
  "message": "成功增加20个积分",
  "new_total_points": 20
}
```

---

### 3.5 提升魔法等级

**API 端点**: `POST /students/{student_id}/upgrade-level`

**curl 命令**:
```bash
curl -X POST "${API_BASE_URL}/students/100/upgrade-level" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -d '{
    "new_level": 2
  }'
```

**预期响应**:
```json
{
  "success": true,
  "message": "成功提升到2级魔法等级",
  "old_level": 1,
  "new_level": 2
}
```

---

## 模块四：课程管理功能

### 4.1 添加课程

**API 端点**: `POST /courses`

**curl 命令**:
```bash
curl -X POST "${API_BASE_URL}/courses" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -d '{
    "student_id": 100,
    "course_name": "语文课",
    "course_type": "school",
    "weekday": "Monday",
    "start_time": "09:00",
    "end_time": "10:00",
    "location": "教室301",
    "teacher": "王老师"
  }'
```

**预期响应**:
```json
{
  "id": 200,
  "student_id": 100,
  "course_name": "语文课",
  "course_type": "school",
  "weekday": "Monday",
  "start_time": "09:00",
  "end_time": "10:00",
  "location": "教室301",
  "teacher": "王老师",
  "created_at": "2025-01-20T10:35:00Z"
}
```

---

### 4.2 获取周课程表

**API 端点**: `GET /students/{student_id}/schedule`

**curl 命令**:
```bash
curl -X GET "${API_BASE_URL}/students/100/schedule" \
  -H "Authorization: Bearer ${API_TOKEN}"
```

**预期响应**:
```json
{
  "student_id": 100,
  "student_name": "测试学生小明",
  "week_start": "2025-01-20",
  "week_end": "2025-01-26",
  "schedule": [
    {
      "weekday": "Monday",
      "courses": [
        {
          "id": 200,
          "course_name": "语文课",
          "start_time": "09:00",
          "end_time": "10:00",
          "location": "教室301",
          "teacher": "王老师"
        }
      ]
    }
  ]
}
```

---

### 4.3 更新课程

**API 端点**: `PUT /courses/{course_id}`

**curl 命令**:
```bash
curl -X PUT "${API_BASE_URL}/courses/200" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -d '{
    "start_time": "10:00",
    "end_time": "11:00"
  }'
```

**预期响应**:
```json
{
  "id": 200,
  "course_name": "语文课",
  "start_time": "10:00",
  "end_time": "11:00",
  "updated_at": "2025-01-20T10:40:00Z"
}
```

---

### 4.4 删除课程

**API 端点**: `DELETE /courses/{course_id}`

**curl 命令**:
```bash
curl -X DELETE "${API_BASE_URL}/courses/200" \
  -H "Authorization: Bearer ${API_TOKEN}"
```

**预期响应**:
```json
{
  "success": true,
  "message": "课程已成功删除"
}
```

---

## 模块五：作业管理功能

### 5.1 创建作业

**API 端点**: `POST /homeworks`

**curl 命令**:
```bash
curl -X POST "${API_BASE_URL}/homeworks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -d '{
    "student_id": 100,
    "title": "数学练习题",
    "subject": "数学",
    "description": "完成课本第10页的练习题",
    "due_date": "2025-01-25",
    "priority": "high"
  }'
```

**预期响应**:
```json
{
  "id": 300,
  "student_id": 100,
  "title": "数学练习题",
  "subject": "数学",
  "description": "完成课本第10页的练习题",
  "due_date": "2025-01-25T00:00:00Z",
  "status": "pending",
  "priority": "high",
  "created_at": "2025-01-20T10:45:00Z"
}
```

---

### 5.2 获取作业列表

**API 端点**: `GET /homeworks?student_id={student_id}&status={status}`

**curl 命令**:
```bash
curl -X GET "${API_BASE_URL}/homeworks?student_id=100&status=pending" \
  -H "Authorization: Bearer ${API_TOKEN}"
```

**预期响应**:
```json
{
  "total": 2,
  "homeworks": [
    {
      "id": 300,
      "title": "数学练习题",
      "subject": "数学",
      "due_date": "2025-01-25T00:00:00Z",
      "status": "pending",
      "priority": "high"
    }
  ]
}
```

---

### 5.3 提交作业

**API 端点**: `POST /homeworks/{homework_id}/submit`

**curl 命令**:
```bash
curl -X POST "${API_BASE_URL}/homeworks/300/submit" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -d '{
    "submission_url": "https://your-domain.com/files/homework_submission_1.jpg"
  }'
```

**预期响应**:
```json
{
  "success": true,
  "message": "作业已成功提交",
  "homework_id": 300,
  "points_awarded": 15,
  "status": "completed"
}
```

---

### 5.4 删除作业

**API 端点**: `DELETE /homeworks/{homework_id}`

**curl 命令**:
```bash
curl -X DELETE "${API_BASE_URL}/homeworks/300" \
  -H "Authorization: Bearer ${API_TOKEN}"
```

**预期响应**:
```json
{
  "success": true,
  "message": "作业已成功删除"
}
```

---

## 模块六：课件管理功能

### 6.1 上传课件

**API 端点**: `POST /coursewares`

**curl 命令**:
```bash
curl -X POST "${API_BASE_URL}/coursewares" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -d '{
    "student_id": 100,
    "title": "唐诗三百首",
    "subject": "语文",
    "file_type": "pdf",
    "file_url": "https://your-domain.com/files/tangshi.pdf",
    "file_size": 1048576,
    "description": "小学必背古诗"
  }'
```

**预期响应**:
```json
{
  "id": 400,
  "student_id": 100,
  "title": "唐诗三百首",
  "subject": "语文",
  "file_type": "pdf",
  "file_url": "https://your-domain.com/files/tangshi.pdf",
  "download_count": 0,
  "created_at": "2025-01-20T10:50:00Z"
}
```

---

### 6.2 获取课件列表

**API 端点**: `GET /coursewares?student_id={student_id}`

**curl 命令**:
```bash
curl -X GET "${API_BASE_URL}/coursewares?student_id=100" \
  -H "Authorization: Bearer ${API_TOKEN}"
```

**预期响应**:
```json
{
  "total": 1,
  "coursewares": [
    {
      "id": 400,
      "title": "唐诗三百首",
      "subject": "语文",
      "file_type": "pdf",
      "file_size": 1048576,
      "download_count": 0
    }
  ]
}
```

---

### 6.3 删除课件

**API 端点**: `DELETE /coursewares/{courseware_id}`

**curl 命令**:
```bash
curl -X DELETE "${API_BASE_URL}/coursewares/400" \
  -H "Authorization: Bearer ${API_TOKEN}"
```

---

## 模块七：运动管理功能

### 7.1 添加运动记录

**API 端点**: `POST /exercises`

**curl 命令**:
```bash
curl -X POST "${API_BASE_URL}/exercises" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -d '{
    "student_id": 100,
    "exercise_type": "run",
    "duration": 30,
    "distance": 3.5,
    "date": "2025-01-20"
  }'
```

**预期响应**:
```json
{
  "id": 500,
  "student_id": 100,
  "exercise_type": "run",
  "duration": 30,
  "distance": 3.5,
  "calories": 210,
  "date": "2025-01-20T00:00:00Z",
  "points": 10,
  "created_at": "2025-01-20T10:55:00Z"
}
```

---

### 7.2 获取运动记录

**API 端点**: `GET /exercises?student_id={student_id}`

**curl 命令**:
```bash
curl -X GET "${API_BASE_URL}/exercises?student_id=100" \
  -H "Authorization: Bearer ${API_TOKEN}"
```

**预期响应**:
```json
{
  "total": 1,
  "exercises": [
    {
      "id": 500,
      "exercise_type": "run",
      "duration": 30,
      "distance": 3.5,
      "date": "2025-01-20T00:00:00Z"
    }
  ]
}
```

---

## 模块八：成就管理功能

### 8.1 颁发成就

**API 端点**: `POST /achievements`

**curl 命令**:
```bash
curl -X POST "${API_BASE_URL}/achievements" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -d '{
    "student_id": 100,
    "achievement_type": "homework_exercise",
    "title": "作业小能手",
    "description": "连续完成5次作业",
    "level": "bronze",
    "points": 20
  }'
```

**预期响应**:
```json
{
  "id": 600,
  "student_id": 100,
  "achievement_type": "homework_exercise",
  "title": "作业小能手",
  "description": "连续完成5次作业",
  "level": "bronze",
  "points": 20,
  "achieved_date": "2025-01-20T11:00:00Z"
}
```

---

### 8.2 获取成就墙

**API 端点**: `GET /students/{student_id}/achievements`

**curl 命令**:
```bash
curl -X GET "${API_BASE_URL}/students/100/achievements" \
  -H "Authorization: Bearer ${API_TOKEN}"
```

**预期响应**:
```json
{
  "total_achievements": 1,
  "featured_achievements": [
    {
      "id": 600,
      "title": "作业小能手",
      "description": "连续完成5次作业",
      "level": "bronze",
      "achieved_date": "2025-01-20T11:00:00Z"
    }
  ]
}
```

---

## 模块九：文件管理功能

### 9.1 上传文件

**API 端点**: `POST /files/upload`

**curl 命令**:
```bash
curl -X POST "${API_BASE_URL}/files/upload" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -F "file=@/path/to/homework.jpg" \
  -F "student_id=100" \
  -F "file_type=homework_submission"
```

**预期响应**:
```json
{
  "success": true,
  "file_url": "https://your-domain.com/files/homework_20250120_abc123.jpg",
  "file_size": 512000,
  "filename": "homework.jpg"
}
```

---

### 9.2 下载文件

**API 端点**: `GET /files/download?file_url={file_url}`

**curl 命令**:
```bash
curl -X GET "${API_BASE_URL}/files/download?file_url=https://your-domain.com/files/homework_20250120_abc123.jpg" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -o downloaded_homework.jpg
```

---

### 9.3 删除文件

**API 端点**: `DELETE /files`

**curl 命令**:
```bash
curl -X DELETE "${API_BASE_URL}/files" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -d '{
    "file_url": "https://your-domain.com/files/homework_20250120_abc123.jpg"
  }'
```

---

## 模块十：历史对话功能（新增）⭐

### 10.1 创建对话会话

**API 端点**: `POST /conversations`

**curl 命令**:
```bash
curl -X POST "${API_BASE_URL}/conversations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -d '{
    "title": "数学作业辅导",
    "student_id": 100
  }'
```

**预期响应**:
```json
{
  "id": 700,
  "user_id": "user123",
  "student_id": 100,
  "title": "数学作业辅导",
  "message_count": 0,
  "created_at": "2025-01-20T11:05:00Z"
}
```

**验证点**:
- [ ] 状态码 201
- [ ] 返回对话ID
- [ ] 标题正确设置
- [ ] 消息计数为0

---

### 10.2 添加消息

**API 端点**: `POST /conversations/{conversation_id}/messages`

**curl 命令**:
```bash
curl -X POST "${API_BASE_URL}/conversations/700/messages" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -d '{
    "role": "user",
    "content": "这道数学题怎么做？"
  }'
```

**预期响应**:
```json
{
  "id": 1000,
  "conversation_id": 700,
  "role": "user",
  "content": "这道数学题怎么做？",
  "created_at": "2025-01-20T11:06:00Z"
}
```

---

### 10.3 获取对话列表（按时间倒序）

**API 端点**: `GET /conversations?student_id={student_id}&limit={limit}`

**curl 命令**:
```bash
curl -X GET "${API_BASE_URL}/conversations?student_id=100&limit=20" \
  -H "Authorization: Bearer ${API_TOKEN}"
```

**预期响应**:
```json
{
  "total": 5,
  "conversations": [
    {
      "id": 700,
      "title": "数学作业辅导",
      "student_id": 100,
      "message_count": 2,
      "created_at": "2025-01-20T11:05:00Z",
      "updated_at": "2025-01-20T11:06:00Z"
    }
  ]
}
```

**验证点**:
- [ ] 对话按时间倒序排列
- [ ] 最新对话在第一位
- [ ] 消息计数正确

---

### 10.4 获取对话详情（包含所有消息）

**API 端点**: `GET /conversations/{conversation_id}`

**curl 命令**:
```bash
curl -X GET "${API_BASE_URL}/conversations/700" \
  -H "Authorization: Bearer ${API_TOKEN}"
```

**预期响应**:
```json
{
  "id": 700,
  "title": "数学作业辅导",
  "student_id": 100,
  "message_count": 2,
  "created_at": "2025-01-20T11:05:00Z",
  "messages": [
    {
      "id": 1000,
      "role": "user",
      "content": "这道数学题怎么做？",
      "created_at": "2025-01-20T11:06:00Z"
    },
    {
      "id": 1001,
      "role": "assistant",
      "content": "这道题考查的是运算顺序哦...",
      "created_at": "2025-01-20T11:06:05Z"
    }
  ]
}
```

**验证点**:
- [ ] 返回对话基本信息
- [ ] 返回所有消息
- [ ] 消息按时间正序排列

---

### 10.5 搜索对话

**API 端点**: `GET /conversations/search?keyword={keyword}&limit={limit}`

**curl 命令**:
```bash
curl -X GET "${API_BASE_URL}/conversations/search?keyword=数学&limit=20" \
  -H "Authorization: Bearer ${API_TOKEN}"
```

**预期响应**:
```json
{
  "total": 1,
  "conversations": [
    {
      "id": 700,
      "title": "数学作业辅导",
      "message_count": 2,
      "created_at": "2025-01-20T11:05:00Z"
    }
  ]
}
```

---

### 10.6 更新对话标题

**API 端点**: `PUT /conversations/{conversation_id}`

**curl 命令**:
```bash
curl -X PUT "${API_BASE_URL}/conversations/700" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -d '{
    "title": "数学运算顺序辅导"
  }'
```

**预期响应**:
```json
{
  "id": 700,
  "title": "数学运算顺序辅导",
  "updated_at": "2025-01-20T11:07:00Z"
}
```

---

### 10.7 删除对话

**API 端点**: `DELETE /conversations/{conversation_id}`

**curl 命令**:
```bash
curl -X DELETE "${API_BASE_URL}/conversations/700" \
  -H "Authorization: Bearer ${API_TOKEN}"
```

**预期响应**:
```json
{
  "success": true,
  "message": "对话已成功删除"
}
```

---

### 10.8 自动生成对话标题

**API 端点**: `POST /conversations/{conversation_id}/generate-title`

**curl 命令**:
```bash
curl -X POST "${API_BASE_URL}/conversations/700/generate-title" \
  -H "Authorization: Bearer ${API_TOKEN}"
```

**预期响应**:
```json
{
  "success": true,
  "title": "数学运算顺序辅导",
  "conversation_id": 700
}
```

---

### 10.9 批量生成标题

**API 端点**: `POST /conversations/batch-generate-titles`

**curl 命令**:
```bash
curl -X POST "${API_BASE_URL}/conversations/batch-generate-titles" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -d '{
    "days": 7
  }'
```

**预期响应**:
```json
{
  "total": 5,
  "success": 5,
  "failed": 0,
  "results": [
    {
      "conversation_id": 700,
      "old_title": "对话 - 2025-01-20 11:05",
      "new_title": "数学运算顺序辅导"
    }
  ]
}
```

---

## 模块十一：仪表盘功能

### 11.1 获取学生仪表盘

**API 端点**: `GET /students/{student_id}/dashboard`

**curl 命令**:
```bash
curl -X GET "${API_BASE_URL}/students/100/dashboard" \
  -H "Authorization: Bearer ${API_TOKEN}"
```

**预期响应**:
```json
{
  "student_id": 100,
  "student_name": "测试学生小明",
  "magic_level": 1,
  "total_points": 20,
  "pending_homeworks": 1,
  "completed_homeworks": 0,
  "total_achievements": 1,
  "weekly_exercises": 1,
  "recent_activities": []
}
```

---

## 模块十二：健康检查

### 12.1 服务健康检查

**API 端点**: `GET /health`

**curl 命令**:
```bash
curl -X GET "${API_BASE_URL}/health"
```

**预期响应**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-01-20T12:00:00Z",
  "database": "connected",
  "model": "qwen-turbo"
}
```

---

## 📊 测试统计

### 测试用例汇总

| 模块 | 用例数量 | 优先级 |
|------|---------|--------|
| 基础对话功能 | 2 | 高 |
| 时间魔法功能 | 2 | 高 |
| 学生管理功能 | 5 | 高 |
| 课程管理功能 | 4 | 高 |
| 作业管理功能 | 4 | 高 |
| 课件管理功能 | 3 | 中 |
| 运动管理功能 | 2 | 中 |
| 成就管理功能 | 2 | 中 |
| 文件管理功能 | 3 | 中 |
| **历史对话功能（新增）** | **9** | **高** ⭐ |
| 仪表盘功能 | 1 | 中 |
| 健康检查 | 1 | 高 |
| **总计** | **38** | - |

---

## 📝 测试报告模板

```markdown
# API 测试报告

## 测试概述
- 测试日期：2025-01-20
- 测试人员：[姓名]
- 测试环境：[环境名称]
- API版本：1.0.0

## 测试结果汇总
- 总用例数：38
- 通过用例：[通过数]
- 失败用例：[失败数]
- 通过率：[通过率]%

## 详细测试结果

### 模块一：基础对话功能
| 用例编号 | 测试项 | 状态 | 响应时间 | 备注 |
|---------|-------|------|---------|------|
| 1.1 | 发送对话消息 | ✅/❌ | [时间] | |
| 1.2 | WebSocket流式对话 | ✅/❌ | [时间] | |

...

### 模块十：历史对话功能（新增）
| 用例编号 | 测试项 | 状态 | 响应时间 | 备注 |
|---------|-------|------|---------|------|
| 10.1 | 创建对话会话 | ✅/❌ | [时间] | |
| 10.2 | 添加消息 | ✅/❌ | [时间] | |
| 10.3 | 获取对话列表 | ✅/❌ | [时间] | |
| 10.4 | 获取对话详情 | ✅/❌ | [时间] | |
| 10.5 | 搜索对话 | ✅/❌ | [时间] | |
| 10.6 | 更新对话标题 | ✅/❌ | [时间] | |
| 10.7 | 删除对话 | ✅/❌ | [时间] | |
| 10.8 | 自动生成标题 | ✅/❌ | [时间] | |
| 10.9 | 批量生成标题 | ✅/❌ | [时间] | |

## 发现的问题
### 问题1
- **描述**：[问题描述]
- **严重程度**：高/中/低
- **影响范围**：[范围]
- **复现步骤**：[步骤]
- **API端点**：[端点]
- **请求参数**：[参数]
- **响应内容**：[响应]

## 性能测试
| 接口 | 平均响应时间 | 90%响应时间 | 最大响应时间 | 状态 |
|------|-------------|-------------|-------------|------|
| GET /conversations | [时间] | [时间] | [时间] | ✅/❌ |
| POST /chat | [时间] | [时间] | [时间] | ✅/❌ |

## 测试结论
[总体评价和改进建议]

## 测试人员签名
[签名和日期]
```

---

## ✅ 测试检查清单

### 基础功能测试

- [ ] 基础对话功能正常
- [ ] 时间功能准确
- [ ] 学生管理功能完整
- [ ] 课程管理功能正常
- [ ] 作业管理功能正常
- [ ] 课件管理功能正常
- [ ] 运动管理功能正常
- [ ] 成就系统功能正常
- [ ] 文件管理功能正常

### 历史对话功能测试（新增）⭐

- [ ] 创建对话会话
- [ ] 添加消息到对话
- [ ] 获取对话列表（按时间倒序）
- [ ] 获取对话详情（包含消息）
- [ ] 搜索对话
- [ ] 更新对话标题
- [ ] 删除对话
- [ ] 自动生成对话标题
- [ ] 批量生成标题

### 非功能性测试

- [ ] 响应时间符合要求
- [ ] API 认证正常
- [ ] 错误处理正确
- [ ] 数据一致性保持
- [ ] 日志记录完整

---

## 🚀 快速测试脚本

### Bash 快速测试脚本

```bash
#!/bin/bash

# 配置
API_BASE_URL="${API_BASE_URL:-https://your-domain.com/api}"
API_TOKEN="${API_TOKEN:-your_token_here}"

echo "🚀 开始 API 测试..."
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 测试计数
TOTAL=0
PASSED=0
FAILED=0

# 测试函数
test_api() {
  local name=$1
  local method=$2
  local endpoint=$3
  local data=$4

  TOTAL=$((TOTAL + 1))

  echo -n "测试 $TOTAL: $name ... "

  response=$(curl -s -w "\n%{http_code}" -X "${method}" \
    "${API_BASE_URL}${endpoint}" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${API_TOKEN}" \
    -d "${data}")

  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | sed '$d')

  if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
    echo -e "${GREEN}✅ PASSED${NC} (HTTP $http_code)"
    PASSED=$((PASSED + 1))
  else
    echo -e "${RED}❌ FAILED${NC} (HTTP $http_code)"
    echo "响应: $body"
    FAILED=$((FAILED + 1))
  fi
}

# 开始测试
echo "════════════════════════════════════════"
echo "基础功能测试"
echo "════════════════════════════════════════"

test_api "健康检查" "GET" "/health" ""
test_api "发送对话" "POST" "/chat" '{"message":"你好","user_id":"test"}'

echo ""
echo "════════════════════════════════════════"
echo "历史对话功能测试（新增）⭐"
echo "════════════════════════════════════════"

test_api "创建对话" "POST" "/conversations" '{"title":"测试对话"}'
test_api "获取对话列表" "GET" "/conversations?limit=10" ""
test_api "搜索对话" "GET" "/conversations/search?keyword=测试" ""

echo ""
echo "════════════════════════════════════════"
echo "测试结果汇总"
echo "════════════════════════════════════════"
echo "总计: $TOTAL"
echo -e "通过: ${GREEN}$PASSED${NC}"
echo -e "失败: ${RED}$FAILED${NC}"
echo "通过率: $(( PASSED * 100 / TOTAL ))%"

if [ $FAILED -eq 0 ]; then
  echo -e "\n🎉 所有测试通过！"
  exit 0
else
  echo -e "\n⚠️ 有测试失败，请检查日志"
  exit 1
fi
```

**使用方法**:

```bash
# 1. 保存为 test_api.sh
chmod +x test_api.sh

# 2. 设置环境变量
export API_BASE_URL="https://your-domain.com/api"
export API_TOKEN="your_jwt_token"

# 3. 运行测试
./test_api.sh
```

---

## 📱 Postman Collection

### 导入 Collection

可以创建一个 Postman Collection，包含所有测试用例：

```json
{
  "info": {
    "name": "魔法课桌学习助手 API 测试",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "基础对话",
      "item": [
        {
          "name": "发送对话",
          "request": {
            "method": "POST",
            "header": [],
            "url": "{{baseUrl}}/chat",
            "body": {
              "mode": "raw",
              "raw": "{\"message\":\"你好\",\"user_id\":\"{{userId}}\"}"
            }
          }
        }
      ]
    },
    {
      "name": "历史对话（新增）",
      "item": [
        {
          "name": "创建对话",
          "request": {
            "method": "POST",
            "header": [],
            "url": "{{baseUrl}}/conversations",
            "body": {
              "mode": "raw",
              "raw": "{\"title\":\"测试对话\"}"
            }
          }
        }
      ]
    }
  ],
  "variable": [
    {
      "key": "baseUrl",
      "value": "https://your-domain.com/api"
    },
    {
      "key": "token",
      "value": "your_jwt_token"
    },
    {
      "key": "userId",
      "value": "user123"
    }
  ]
}
```

---

## 🔍 调试技巧

### 1. 查看详细响应

```bash
curl -v -X GET "${API_BASE_URL}/conversations" \
  -H "Authorization: Bearer ${API_TOKEN}"
```

### 2. 保存响应到文件

```bash
curl -X GET "${API_BASE_URL}/conversations" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -o response.json

cat response.json | jq .
```

### 3. 使用 jq 格式化 JSON

```bash
curl -X GET "${API_BASE_URL}/conversations" \
  -H "Authorization: Bearer ${API_TOKEN}" | jq .
```

### 4. 查看响应头

```bash
curl -I -X GET "${API_BASE_URL}/conversations" \
  -H "Authorization: Bearer ${API_TOKEN}"
```

---

## ❓ 常见问题

### Q1: 认证失败（401）

**原因**: Token 无效或过期

**解决**:
```bash
# 重新获取 Token
curl -X POST "${API_BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username","password":"your_password"}'
```

### Q2: 数据库错误

**原因**: 数据库表未创建

**解决**: 执行数据库迁移（见部署文档）

### Q3: 新功能未生效

**原因**: 服务未重启或缓存问题

**解决**:
```bash
# 重启服务
sudo systemctl restart magic-school-backend

# 清除缓存
curl -X DELETE "${API_BASE_URL}/cache"
```

---

## 📞 测试支持

如果测试过程中遇到问题：

1. 查看日志：`tail -f /app/work/logs/bypass/app.log`
2. 检查服务状态：`systemctl status magic-school-backend`
3. 查看数据库连接：`psql -d magic_school -c "\dt"`
4. 联系开发团队

---

## 🎉 总结

本测试指南包含了魔法课桌学习助手智能体的所有功能模块，共计 **38 个 API 测试用例**，其中新增的**历史对话功能占 9 个用例**。

按照本指南进行测试，可以全面验证：
- ✅ 所有功能模块正常工作
- ✅ API 接口符合规范
- ✅ 数据一致性保持
- ✅ 新功能（历史对话）正常

**测试重点**：
1. 优先测试高优先级用例
2. 重点关注新增的历史对话功能
3. 验证数据库表是否正确创建
4. 检查对话标题生成功能

---

**文档版本**: 1.0.0
**最后更新**: 2025年1月
**维护者**: Coze Coding Team
**状态**: ✅ 已完成
