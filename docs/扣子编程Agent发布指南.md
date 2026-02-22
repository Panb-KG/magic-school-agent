# 🚀 扣子编程 Agent 发布指南

## 📋 需求说明

在扣子编程沙箱环境中已开发完成功能完整的后端 Agent，现在需要：
1. 将 Agent 发布为服务
2. 获取 API 端点
3. 使外部前端程序可以调用

---

## 🎯 发布方案

扣子编程环境支持将 Agent 发布为 **HTTP API 服务**，供外部调用。

---

## 步骤 1：确认 Agent 状态

### 1.1 检查 Agent 是否完成



### 1.2 查看项目结构

```
workspace/projects/
├── src/
│   ├── agents/agent.py          # Agent 主逻辑
│   ├── tools/                   # 工具定义
│   ├── main.py                  # 服务入口
│   └── api/                     # API 接口
├── config/agent_llm_config.json # 模型配置
└── requirements.txt             # 依赖
```

---

## 步骤 2：启动 Agent 服务

### 2.1 方式一：通过扣子编程界面启动（推荐）

1. 在扣子编程 IDE 右侧找到"运行"或"发布"按钮
2. 点击"发布"或"启动服务"
3. 选择发布方式：**HTTP 服务**
4. 系统会自动：
   - 启动 Agent 服务
   - 分配服务端口
   - 生成 API 端点地址

### 2.2 方式二：手动启动服务

如果需要手动启动，在扣子编程终端执行：

```bash
# 启动 HTTP 服务
python src/main.py -m http -p 5000
```

或者使用您之前创建的管理脚本：

```bash
./scripts/manage_agent.sh start
```

---

## 步骤 3：获取 API 信息

### 3.1 查看服务地址

启动成功后，系统会提供：

```
✅ 服务已启动
📍 服务地址: https://xxx.coze.cn/agent/xxx
📋 API 文档: https://xxx.coze.cn/agent/xxx/docs
🔑 API Key: xxxxxxxx
```

### 3.2 查看 API 端点

**基础端点**：
- **健康检查**: `GET /health`
- **对话接口**: `POST /run`
- **流式对话**: `POST /stream_run`
- **取消执行**: `POST /cancel/{run_id}`

**API 文档**：访问服务地址的 `/docs` 端点查看完整的 Swagger 文档。

---

## 步骤 4：配置访问权限

### 4.1 API 认证

扣子编程发布的 API 通常需要认证：

**方式一：API Key 认证**

在请求头中添加：

```http
Authorization: Bearer YOUR_API_KEY
```

**方式二：Token 认证**

```http
X-Coze-API-Key: YOUR_API_KEY
```

### 4.2 获取 API Key

1. 在扣子编程界面找到"API Key"或"密钥"选项
2. 点击生成新的 API Key
3. 复制并妥善保管

---

## 步骤 5：前端调用示例

### 5.1 健康检查

```javascript
// JavaScript/TypeScript
const response = await fetch('https://xxx.coze.cn/agent/xxx/health', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY'
  }
});

const result = await response.json();
console.log(result);
// {"status":"ok","message":"Service is running"}
```

### 5.2 对话接口

```javascript
// JavaScript/TypeScript
const response = await fetch('https://xxx.coze.cn/agent/xxx/run', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_API_KEY'
  },
  body: JSON.stringify({
    message: "你好",
    session_id: "session_001",
    user_id: "user_001"
  })
});

const result = await response.json();
console.log(result);

// 响应格式：
// {
//   "messages": [
//     {
//       "content": "你好呀，小巫师！...",
//       "type": "ai"
//     }
//   ],
//   "run_id": "xxx"
// }
```

### 5.3 流式对话

```javascript
// JavaScript/TypeScript
const response = await fetch('https://xxx.coze.cn/agent/xxx/stream_run', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_API_KEY'
  },
  body: JSON.stringify({
    message: "你好",
    session_id: "session_001",
    user_id: "user_001"
  })
});

// 处理流式响应
const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const text = decoder.decode(value);
  console.log(text); // 逐块输出
}
```

---

## 步骤 6：前端集成示例

### 6.1 React 集成

```typescript
// api/agent.ts
const AGENT_BASE_URL = 'https://xxx.coze.cn/agent/xxx';
const API_KEY = 'YOUR_API_KEY';

export async function chatWithAgent(message: string, sessionId: string, userId: string) {
  const response = await fetch(`${AGENT_BASE_URL}/run`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
      user_id: userId
    })
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}

export async function checkHealth() {
  const response = await fetch(`${AGENT_BASE_URL}/health`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${API_KEY}`
    }
  });

  return response.json();
}
```

### 6.2 Vue 集成

```javascript
// api/agent.js
const AGENT_BASE_URL = 'https://xxx.coze.cn/agent/xxx';
const API_KEY = 'YOUR_API_KEY';

export function chatWithAgent(message, sessionId, userId) {
  return fetch(`${AGENT_BASE_URL}/run`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
      user_id: userId
    })
  }).then(res => res.json());
}
```

### 6.3 Python 集成

```python
import requests

AGENT_BASE_URL = 'https://xxx.coze.cn/agent/xxx'
API_KEY = 'YOUR_API_KEY'

def chat_with_agent(message, session_id, user_id):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }

    data = {
        'message': message,
        'session_id': session_id,
        'user_id': user_id
    }

    response = requests.post(
        f'{AGENT_BASE_URL}/run',
        headers=headers,
        json=data
    )

    return response.json()

# 使用示例
result = chat_with_agent(
    message="你好",
    session_id="session_001",
    user_id="user_001"
)

print(result)
```

---

## 步骤 7：配置 CORS（如果需要）

如果前端和 API 服务不在同一个域，需要配置 CORS。

### 7.1 在扣子编程配置中添加 CORS

查找扣子编程环境的 CORS 配置选项，允许前端域名：

```json
{
  "allowed_origins": [
    "https://your-frontend.com",
    "http://localhost:3000"
  ],
  "allowed_methods": ["GET", "POST", "PUT", "DELETE"],
  "allowed_headers": ["Content-Type", "Authorization"]
}
```

### 7.2 或者在代理服务器中配置

如果无法在扣子编程中配置，可以使用 Nginx 代理：

```nginx
location /api/agent/ {
    proxy_pass https://xxx.coze.cn/agent/;
    proxy_set_header Host $host;
    proxy_set_header Authorization "Bearer YOUR_API_KEY";
    add_header Access-Control-Allow-Origin *;
}
```

---

## 步骤 8：测试 API

### 8.1 使用 curl 测试

```bash
# 健康检查
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://xxx.coze.cn/agent/xxx/health

# 对话测试
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"message":"你好","session_id":"test","user_id":"user"}' \
  https://xxx.coze.cn/agent/xxx/run
```

### 8.2 使用 Postman 测试

1. 创建新的请求
2. 设置方法为 POST
3. 输入 URL: `https://xxx.coze.cn/agent/xxx/run`
4. 添加 Headers：
   - `Content-Type`: `application/json`
   - `Authorization`: `Bearer YOUR_API_KEY`
5. 添加 Body（JSON）：
   ```json
   {
     "message": "你好",
     "session_id": "test",
     "user_id": "user"
   }
   ```
6. 发送请求

---

## 📋 发布检查清单

发布前确认：

- [ ] Agent 测试通过
- [ ] 配置文件正确
- [ ] 依赖已安装
- [ ] 服务可以正常启动

发布时确认：

- [ ] 服务启动成功
- [ ] 获取到服务地址和 API Key
- [ ] API 文档可访问
- [ ] 健康检查接口正常

前端集成前确认：

- [ ] API 地址正确
- [ ] API Key 已配置
- [ ] CORS 配置完成
- [ ] 测试调用成功

---

## 🔐 安全建议

### 1. 保护 API Key

- ❌ 不要将 API Key 提交到公开仓库
- ✅ 使用环境变量存储 API Key
- ✅ 定期轮换 API Key

### 2. 限制访问频率

在扣子编程配置中设置：
- 每分钟最大请求数
- 每天最大请求数

### 3. 日志监控

定期查看扣子编程平台的日志，监控：
- API 调用次数
- 错误率
- 响应时间

---

## 🆘 常见问题

### Q: 如何获取 API 端点地址？

A: 在扣子编程界面点击"发布"后，系统会显示服务地址和 API Key。

### Q: API Key 怎么获取？

A: 在扣子编程的设置或发布页面，可以生成和管理 API Key。

### Q: 如何设置 CORS？

A: 查看扣子编程的 CORS 配置选项，或使用代理服务器。

### Q: 前端调用失败怎么办？

A: 检查：
- API 地址是否正确
- API Key 是否有效
- CORS 是否配置
- 网络是否通畅

---

## 📚 相关文档

- [扣子编程官方文档](https://www.coze.cn/docs/)
- [API 文档](https://xxx.coze.cn/agent/xxx/docs)
- [前端集成示例](#步骤-5前端调用示例)

---

## 🎯 总结

发布流程：
1. 确认 Agent 状态
2. 启动服务（发布）
3. 获取 API 信息
4. 配置访问权限
5. 前端集成调用
6. 测试验证

---

**预计耗时**: 10-15 分钟
**难度**: ⭐⭐
