# 🔧 魔法课桌后端开发计划（基于前端反馈）

> 针对前端团队反馈的后端需求补充和优化计划

---

## 📊 问题分析总结

### 前端当前问题

| 问题 | 严重程度 | 影响 |
|------|---------|------|
| API调用方式错误（直接调用Coze） | 🔴 严重 | 无法实现用户认证、数据持久化 |
| 缺少用户认证 | 🔴 严重 | 无法实现多设备同步、数据隔离 |
| 数据存储方式错误（localStorage） | 🟡 中等 | 数据无法跨设备同步 |
| 会话管理缺失 | 🟡 中等 | 无法支持多会话、历史对话管理 |

### 后端需要补充的功能

根据前端反馈，需要补充以下功能：

#### 🔴 高优先级（必须先完成）
1. ✅ JWT Token认证机制（已实现）
2. ✅ bcrypt密码加密（已实现）
3. ✅ 学生/家长双角色支持（已实现）
4. ❌ **Token刷新机制和过期处理**（需要补充）
5. ❌ **WebSocket实时对话接口**（需要补充）
6. ❌ **流式响应支持**（需要补充）
7. ❌ **会话搜索功能**（需要补充）

#### 🟡 中优先级（第二阶段）
1. ✅ 课程管理API（已实现）
2. ✅ 作业管理API（已实现）
3. ✅ 成就系统API（已实现）
4. ✅ 学生档案管理（已实现）
5. ❌ **文件管理API**（需要补充）
6. ❌ **批量操作API**（需要补充）

---

## 🎯 开发计划

### 阶段1：补充核心认证和对话功能（1-2天）

#### 1.1 Token刷新机制和过期处理

**目标**：实现Access Token和Refresh Token机制，支持自动刷新

**实现内容**：

```python
# auth/refresh_token.py
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException

class TokenManager:
    """Token管理器"""

    @staticmethod
    def generate_access_token(user_id: str, role: str) -> str:
        """生成Access Token（短期，24小时）"""
        payload = {
            "user_id": user_id,
            "role": role,
            "type": "access",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    @staticmethod
    def generate_refresh_token(user_id: str) -> str:
        """生成Refresh Token（长期，30天）"""
        payload = {
            "user_id": user_id,
            "type": "refresh",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=30)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    @staticmethod
    def refresh_access_token(refresh_token: str) -> dict:
        """刷新Access Token"""
        try:
            payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=["HS256"])

            # 验证是否为Refresh Token
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=401, detail="Invalid token type")

            # 生成新的Access Token
            user_id = payload["user_id"]
            user = get_user_by_id(user_id)

            if not user or not user.is_active:
                raise HTTPException(status_code=401, detail="User not found or inactive")

            access_token = TokenManager.generate_access_token(
                user.user_id,
                user.role
            )

            new_refresh_token = TokenManager.generate_refresh_token(user.user_id)

            return {
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "token_type": "Bearer"
            }
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
```

**API接口**：

```python
# src/api/auth_api.py
from fastapi import APIRouter, Depends, HTTPException
from auth.refresh_token import TokenManager
from pydantic import BaseModel

router = APIRouter()

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/api/v1/auth/refresh")
async def refresh_token(request: RefreshTokenRequest):
    """刷新Access Token"""
    result = TokenManager.refresh_access_token(request.refresh_token)
    return result

@router.post("/api/v1/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """登出（客户端删除Token）"""
    return {"message": "Logged out successfully"}
```

**测试用例**：

```python
# tests/test_refresh_token.py
def test_refresh_token():
    """测试Token刷新"""
    # 1. 登录获取Token
    login_result = user_manager.login_user("test_student", "password123")
    access_token = login_result["access_token"]
    refresh_token = login_result["refresh_token"]

    # 2. 使用Refresh Token刷新
    refresh_result = refresh_token(refresh_token)

    # 3. 验证新的Token
    assert "access_token" in refresh_result
    assert "refresh_token" in refresh_result

    print("✅ Token刷新测试通过")
```

---

#### 1.2 WebSocket实时对话接口

**目标**：实现WebSocket实时对话，支持流式响应

**实现内容**：

```python
# src/api/websocket_api.py
from fastapi import WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.security import HTTPBearer
import json
import asyncio
from typing import Dict

security = HTTPBearer()

class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        """建立连接"""
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        """断开连接"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, session_id: str, message: dict):
        """发送消息"""
        websocket = self.active_connections.get(session_id)
        if websocket:
            await websocket.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket,
    token: str = Query(...),
    session_id: str = Query(...)
):
    """WebSocket实时对话"""
    # 1. 验证Token
    try:
        payload = verify_jwt_token(token)
        user_id = payload["user_id"]
        user_role = payload["role"]
    except Exception as e:
        await websocket.close(code=4001, reason="Invalid token")
        return

    # 2. 建立连接
    await manager.connect(websocket, session_id)

    # 3. 准备Agent配置
    config = {
        "configurable": {
            "thread_id": session_id,
            "user_id": user_id,
            "user_role": user_role
        }
    }

    try:
        while True:
            # 4. 接收消息
            data = await websocket.receive_json()

            message = data.get("message")
            if not message:
                continue

            # 5. 发送开始信号
            await manager.send_message(session_id, {
                "type": "start",
                "message": "正在思考..."
            })

            # 6. 调用Agent（流式）
            agent = build_agent(ctx=new_context(method="chat", configurable=config))

            async for chunk in agent.astream(
                {"messages": [HumanMessage(content=message)]},
                config=config,
                stream_mode="messages"
            ):
                # 7. 发送流式响应
                if chunk.content:
                    await manager.send_message(session_id, {
                        "type": "chunk",
                        "content": chunk.content
                    })

            # 8. 发送完成信号
            await manager.send_message(session_id, {
                "type": "end",
                "message": "完成"
            })

    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        await manager.send_message(session_id, {
            "type": "error",
            "message": str(e)
        })
        manager.disconnect(session_id)
```

**前端调用示例**：

```typescript
// 前端WebSocket连接示例
const connectWebSocket = (token: string, sessionId: string) => {
  const ws = new WebSocket(`ws://your-domain.com/ws/chat?token=${token}&sessionId=${sessionId}`);

  ws.onopen = () => {
    console.log('WebSocket连接成功');
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    switch (data.type) {
      case 'start':
        // 显示"正在思考..."
        break;
      case 'chunk':
        // 追加显示流式内容
        appendMessage(data.content);
        break;
      case 'end':
        // 显示完成状态
        break;
      case 'error':
        // 显示错误
        showError(data.message);
        break;
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket错误:', error);
  };

  ws.onclose = () => {
    console.log('WebSocket连接关闭');
  };

  return ws;
};
```

---

#### 1.3 流式响应支持（HTTP）

**目标**：HTTP接口也支持流式响应（Server-Sent Events）

**实现内容**：

```python
# src/api/chat_api.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json

router = APIRouter()

@router.post("/api/v1/chat/stream")
async def chat_stream(
    message: str,
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """流式对话（SSE）"""

    # 准备Agent配置
    config = {
        "configurable": {
            "thread_id": session_id,
            "user_id": current_user["user_id"],
            "user_role": current_user["role"]
        }
    }

    async def generate():
        """生成流式响应"""
        try:
            # 发送开始信号
            yield f"data: {json.dumps({'type': 'start'})}\n\n"

            # 调用Agent
            agent = build_agent(ctx=new_context(method="chat", configurable=config))

            async for chunk in agent.astream(
                {"messages": [HumanMessage(content=message)]},
                config=config,
                stream_mode="messages"
            ):
                if chunk.content:
                    # 发送流式内容
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk.content})}\n\n"

            # 发送完成信号
            yield f"data: {json.dumps({'type': 'end'})}\n\n"

        except Exception as e:
            # 发送错误信号
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
```

**前端调用示例**：

```typescript
// 前端SSE调用示例
const chatStream = async (message: string, token: string) => {
  const response = await fetch('/api/v1/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ message, sessionId: 'sess_123' })
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader!.read();

    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.substring(6));

        switch (data.type) {
          case 'start':
            // 显示"正在思考..."
            break;
          case 'chunk':
            // 追加显示流式内容
            appendMessage(data.content);
            break;
          case 'end':
            // 显示完成状态
            break;
          case 'error':
            // 显示错误
            showError(data.message);
            break;
        }
      }
    }
  }
};
```

---

#### 1.4 会话搜索功能

**目标**：支持按关键词搜索对话会话

**实现内容**：

```python
# src/api/conversation_api.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_

router = APIRouter()

@router.get("/api/v1/conversations/search")
async def search_conversations(
    keyword: str = Query(...),
    user_id: str = Query(...),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """搜索对话会话"""
    # 验证权限
    if current_user["role"] == "parent":
        # 家长需要关联学生
        student_id = user_id
    else:
        student_id = current_user["user_id"]

    db = get_session()

    # 搜索对话标题和消息内容
    conversations = db.query(Conversation).filter(
        Conversation.user_id == student_id,
        or_(
            Conversation.title.ilike(f"%{keyword}%"),
            # 搜索消息内容
            Conversation.messages.any(
                ConversationMessage.content.ilike(f"%{keyword}%")
            )
        )
    ).limit(limit).all()

    # 格式化结果
    results = []
    for conv in conversations:
        results.append({
            "id": conv.id,
            "title": conv.title,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat(),
            "message_count": len(conv.messages)
        })

    return {
        "keyword": keyword,
        "results": results,
        "total": len(results)
    }
```

---

### 阶段2：文件管理API（2-3天）

#### 2.1 文件上传接口

**目标**：支持文件上传（作业附件、课件、图片等）

**实现内容**：

```python
# src/api/file_api.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pathlib import Path
import uuid
import shutil
from typing import List

router = APIRouter()

# 配置上传目录
UPLOAD_DIR = Path("/tmp/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/api/v1/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    student_id: str = Query(...),
    file_type: str = Query(...),  # homework, courseware, avatar, etc.
    current_user: dict = Depends(get_current_user)
):
    """上传文件"""
    # 验证权限
    if current_user["role"] == "parent":
        if not is_parent_linked_to_student(current_user["user_id"], student_id):
            raise HTTPException(status_code=403, detail="Access denied")

    # 验证文件类型
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid file type")

    # 生成唯一文件名
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename

    # 保存文件
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    # 保存到数据库
    db = get_session()
    file_record = UploadedFile(
        user_id=student_id,
        original_filename=file.filename,
        stored_filename=unique_filename,
        file_path=str(file_path),
        file_type=file_type,
        file_size=file_path.stat().st_size
    )
    db.add(file_record)
    db.commit()

    return {
        "success": True,
        "file_id": file_record.id,
        "filename": unique_filename,
        "url": f"/api/v1/files/{file_record.id}"
    }
```

#### 2.2 文件列表接口

```python
@router.get("/api/v1/files")
async def list_files(
    student_id: str = Query(...),
    file_type: str = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """获取文件列表"""
    # 验证权限
    if current_user["role"] == "parent":
        if not is_parent_linked_to_student(current_user["user_id"], student_id):
            raise HTTPException(status_code=403, detail="Access denied")

    db = get_session()

    query = db.query(UploadedFile).filter(
        UploadedFile.user_id == student_id
    )

    if file_type:
        query = query.filter(UploadedFile.file_type == file_type)

    files = query.order_by(UploadedFile.uploaded_at.desc()).all()

    return {
        "files": [
            {
                "id": f.id,
                "filename": f.original_filename,
                "file_type": f.file_type,
                "file_size": f.file_size,
                "uploaded_at": f.uploaded_at.isoformat(),
                "url": f"/api/v1/files/{f.id}"
            }
            for f in files
        ]
    }
```

#### 2.3 文件下载接口

```python
from fastapi.responses import FileResponse

@router.get("/api/v1/files/{file_id}")
async def download_file(
    file_id: int,
    current_user: dict = Depends(get_current_user)
):
    """下载文件"""
    db = get_session()

    file_record = db.query(UploadedFile).filter(
        UploadedFile.id == file_id
    ).first()

    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    # 验证权限
    if current_user["role"] == "student":
        if file_record.user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user["role"] == "parent":
        if not is_parent_linked_to_student(current_user["user_id"], file_record.user_id):
            raise HTTPException(status_code=403, detail="Access denied")

    file_path = Path(file_record.file_path)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=str(file_path),
        filename=file_record.original_filename,
        media_type='application/octet-stream'
    )
```

---

### 阶段3：批量操作API（1-2天）

#### 3.1 批量生成会话标题

```python
@router.post("/api/v1/conversations/batch-generate-titles")
async def batch_generate_titles(
    user_id: str = Query(...),
    current_user: dict = Depends(get_current_user)
):
    """批量生成会话标题"""
    # 验证权限
    if current_user["role"] == "student":
        student_id = current_user["user_id"]
    elif current_user["role"] == "parent":
        student_id = user_id
        if not is_parent_linked_to_student(current_user["user_id"], student_id):
            raise HTTPException(status_code=403, detail="Access denied")

    db = get_session()

    # 查询没有标题的会话
    conversations = db.query(Conversation).filter(
        Conversation.user_id == student_id,
        Conversation.title == "新对话"
    ).all()

    # 批量生成标题
    results = []
    for conv in conversations:
        # 获取对话消息
        messages = conv.messages[:5]  # 取前5条消息

        # 生成标题
        title = generate_title_from_messages(messages)

        # 更新标题
        conv.title = title

        results.append({
            "conversation_id": conv.id,
            "title": title
        })

    db.commit()

    return {
        "success": True,
        "count": len(results),
        "results": results
    }
```

#### 3.2 批量更新作业状态

```python
class BatchUpdateHomeworkRequest(BaseModel):
    homework_ids: List[int]
    status: str

@router.put("/api/v1/homeworks/batch-update-status")
async def batch_update_homework_status(
    request: BatchUpdateHomeworkRequest,
    student_id: str = Query(...),
    current_user: dict = Depends(get_current_user)
):
    """批量更新作业状态"""
    # 验证权限
    if current_user["role"] == "parent":
        if not is_parent_linked_to_student(current_user["user_id"], student_id):
            raise HTTPException(status_code=403, detail="Access denied")

    db = get_session()

    # 批量更新
    updated_count = db.query(Homework).filter(
        Homework.id.in_(request.homework_ids),
        Homework.student_id == student_id
    ).update({
        "status": request.status
    })

    db.commit()

    return {
        "success": True,
        "updated_count": updated_count
    }
```

---

## 📋 开发时间表

| 阶段 | 功能 | 预计时间 | 优先级 |
|------|------|----------|--------|
| 阶段1 | Token刷新机制 | 0.5天 | 🔴 高 |
| 阶段1 | WebSocket实时对话 | 1天 | 🔴 高 |
| 阶段1 | 流式响应支持 | 0.5天 | 🔴 高 |
| 阶段1 | 会话搜索功能 | 0.5天 | 🔴 高 |
| 阶段2 | 文件上传接口 | 1天 | 🟡 中 |
| 阶段2 | 文件列表接口 | 0.5天 | 🟡 中 |
| 阶段2 | 文件下载接口 | 0.5天 | 🟡 中 |
| 阶段3 | 批量生成会话标题 | 0.5天 | 🟢 低 |
| 阶段3 | 批量更新作业状态 | 0.5天 | 🟢 低 |
| **总计** | | **5.5天** | |

---

## ✅ 验收标准

### 阶段1验收标准

- [ ] Token可以正常刷新，过期后自动刷新
- [ ] WebSocket连接稳定，支持实时对话
- [ ] 流式响应正常显示，打字机效果流畅
- [ ] 会话搜索功能正常，可以按关键词搜索

### 阶段2验收标准

- [ ] 文件上传成功，返回正确的URL
- [ ] 文件列表正确显示，支持按类型筛选
- [ ] 文件下载正常，权限控制正确

### 阶段3验收标准

- [ ] 批量生成会话标题功能正常
- [ ] 批量更新作业状态功能正常

---

## 🧪 测试计划

### 单元测试

```python
# tests/test_api.py

def test_token_refresh():
    """测试Token刷新"""
    pass

def test_websocket_chat():
    """测试WebSocket对话"""
    pass

def test_file_upload():
    """测试文件上传"""
    pass

def test_batch_operations():
    """测试批量操作"""
    pass
```

### 集成测试

```python
# tests/test_integration.py

def test_full_chat_workflow():
    """测试完整对话流程"""
    # 1. 注册用户
    # 2. 登录获取Token
    # 3. 建立WebSocket连接
    # 4. 发送消息
    # 5. 接收流式响应
    # 6. 断开连接
    pass

def test_file_workflow():
    """测试文件上传下载流程"""
    # 1. 上传文件
    # 2. 获取文件列表
    # 3. 下载文件
    pass
```

---

## 📝 注意事项

1. **安全性**
   - 文件上传需要验证文件类型和大小
   - WebSocket需要验证Token
   - 所有API都需要权限检查

2. **性能优化**
   - 流式响应需要优化
   - 文件上传需要支持断点续传（可选）
   - 批量操作需要限制数量

3. **错误处理**
   - 网络错误需要重试
   - WebSocket断线需要自动重连
   - 所有错误需要友好的提示

---

## 🎯 后续优化

1. **WebSocket认证优化**
   - 支持Token刷新后自动重新认证
   - 支持心跳保活

2. **文件管理优化**
   - 支持对象存储（S3/OSS）
   - 支持文件预览
   - 支持文件压缩

3. **批量操作优化**
   - 支持异步批量处理
   - 支持进度查询
   - 支持任务队列

---

**计划完成时间**：5.5个工作日
**预计上线时间**：根据前端开发进度协调
