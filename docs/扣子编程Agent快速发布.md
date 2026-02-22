# ⚡ 扣子编程 Agent 快速发布指南

## 🎯 5 分钟快速发布

---

## 步骤 1：启动服务（1 分钟）

在扣子编程 IDE 中：

1. **找到发布按钮**
   - 通常在 IDE 顶部或右侧
   - 图标：🚀 或 "发布"

2. **点击"发布"**
   - 选择发布类型：**HTTP 服务** 或 **API 服务**
   - 点击确认

3. **等待发布完成**
   - 系统会自动启动服务
   - 显示发布成功提示

---

## 步骤 2：获取 API 信息（1 分钟）

发布成功后，系统会显示：

```
✅ 发布成功

📍 服务地址: https://api.coze.cn/v1/agent/your_agent_id
🔑 API Key: sk-xxxxxxxxxxxxxxxx
📖 API 文档: https://api.coze.cn/v1/agent/your_agent_id/docs
```

**重要**：请复制并保存：
- **服务地址**
- **API Key**

---

## 步骤 3：测试 API（1 分钟）

使用 curl 测试：

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"message":"你好","session_id":"test","user_id":"user"}' \
  https://api.coze.cn/v1/agent/your_agent_id/run
```

应该收到响应：
```json
{
  "messages": [
    {
      "content": "你好呀，小巫师！...",
      "type": "ai"
    }
  ]
}
```

---

## 步骤 4：前端集成（2 分钟）

### 基础调用代码

```javascript
// 配置
const API_URL = 'https://api.coze.cn/v1/agent/your_agent_id/run';
const API_KEY = 'YOUR_API_KEY';

// 调用函数
async function chat(message, sessionId, userId) {
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`
    },
    body: JSON.stringify({
      message: message,
      session_id: sessionId,
      user_id: userId
    })
  });

  const result = await response.json();
  return result.messages;
}

// 使用示例
chat('你好', 'session_001', 'user_001')
  .then(messages => {
    console.log('AI 回复:', messages[messages.length - 1].content);
  });
```

---

## 📋 前端配置文件

创建 `config/agent.config.js`:

```javascript
export const agentConfig = {
  apiUrl: 'https://api.coze.cn/v1/agent/your_agent_id',
  apiKey: 'YOUR_API_KEY',

  // 调用方法
  async chat(message, sessionId, userId) {
    const response = await fetch(`${this.apiUrl}/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        user_id: userId
      })
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }
};
```

---

## 🔧 环境变量配置（推荐）

在生产环境，使用环境变量存储 API Key：

### 前端（React/Vue）

```javascript
// .env
VITE_AGENT_API_URL=https://api.coze.cn/v1/agent/your_agent_id
VITE_AGENT_API_KEY=YOUR_API_KEY
```

```javascript
// 使用
const API_URL = import.meta.env.VITE_AGENT_API_URL;
const API_KEY = import.meta.env.VITE_AGENT_API_KEY;
```

### 后端（Node.js）

```bash
# .env
AGENT_API_URL=https://api.coze.cn/v1/agent/your_agent_id
AGENT_API_KEY=YOUR_API_KEY
```

```javascript
// 使用
const API_URL = process.env.AGENT_API_URL;
const API_KEY = process.env.AGENT_API_KEY;
```

---

## ✅ 完成检查清单

- [ ] Agent 已发布
- [ ] 获取到服务地址
- [ ] 获取到 API Key
- [ ] API 测试通过
- [ ] 前端集成完成
- [ ] API Key 安全存储

---

## 🆘 常见问题

### Q: 找不到发布按钮？

A: 检查 IDE 顶部工具栏，通常在"运行"按钮旁边。

### Q: 发布失败怎么办？

A: 检查：
- Agent 测试是否通过
- 配置文件是否正确
- 网络连接是否正常

### Q: API Key 在哪里？

A: 发布成功后，系统会显示 API Key，或在扣子编程的设置中查看。

### Q: 前端调用跨域怎么办？
# ⚡ 扣子编程 Agent 快速发布指南

## 🎯 5 分钟快速发布

---

## 步骤 1：启动服务（1 分钟）

在扣子编程 IDE 中：

1. **找到发布按钮**
   - 通常在 IDE 顶部或右侧
   - 图标：🚀 或 "发布"

2. **点击"发布"**
   - 选择发布类型：**HTTP 服务** 或 **API 服务**
   - 点击确认

3. **等待发布完成**
   - 系统会自动启动服务
   - 显示发布成功提示

---

## 步骤 2：获取 API 信息（1 分钟）

发布成功后，系统会显示：

```
✅ 发布成功

📍 服务地址: https://api.coze.cn/v1/agent/your_agent_id
🔑 API Key: sk-xxxxxxxxxxxxxxxx
📖 API 文档: https://api.coze.cn/v1/agent/your_agent_id/docs
```

**重要**：请复制并保存：
- **服务地址**
- **API Key**

---

## 步骤 3：测试 API（1 分钟）

使用 curl 测试：

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"message":"你好","session_id":"test","user_id":"user"}' \
  https://api.coze.cn/v1/agent/your_agent_id/run
```

应该收到响应：
```json
{
  "messages": [
    {
      "content": "你好呀，小巫师！...",
      "type": "ai"
    }
  ]
}
```

---

## 步骤 4：前端集成（2 分钟）

### 基础调用代码

```javascript
// 配置
const API_URL = 'https://api.coze.cn/v1/agent/your_agent_id/run';
const API_KEY = 'YOUR_API_KEY';

// 调用函数
async function chat(message, sessionId, userId) {
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`
    },
    body: JSON.stringify({
      message: message,
      session_id: sessionId,
      user_id: userId
    })
  });

  const result = await response.json();
  return result.messages;
}

// 使用示例
chat('你好', 'session_001', 'user_001')
  .then(messages => {
    console.log('AI 回复:', messages[messages.length - 1].content);
  });
```

---

## 📋 前端配置文件

创建 `config/agent.config.js`:

```javascript
export const agentConfig = {
  apiUrl: 'https://api.coze.cn/v1/agent/your_agent_id',
  apiKey: 'YOUR_API_KEY',

  // 调用方法
  async chat(message, sessionId, userId) {
    const response = await fetch(`${this.apiUrl}/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        user_id: userId
      })
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }
};
```

---

## 🔧 环境变量配置（推荐）

在生产环境，使用环境变量存储 API Key：

### 前端（React/Vue）

```javascript
// .env
VITE_AGENT_API_URL=https://api.coze.cn/v1/agent/your_agent_id
VITE_AGENT_API_KEY=YOUR_API_KEY
```

```javascript
// 使用
const API_URL = import.meta.env.VITE_AGENT_API_URL;
const API_KEY = import.meta.env.VITE_AGENT_API_KEY;
```

### 后端（Node.js）

```bash
# .env
AGENT_API_URL=https://api.coze.cn/v1/agent/your_agent_id
AGENT_API_KEY=YOUR_API_KEY
```

```javascript
// 使用
const API_URL = process.env.AGENT_API_URL;
const API_KEY = process.env.AGENT_API_KEY;
```

---

## ✅ 完成检查清单

- [ ] Agent 已发布
- [ ] 获取到服务地址
- [ ] 获取到 API Key
- [ ] API 测试通过
- [ ] 前端集成完成
- [ ] API Key 安全存储

---

## 🆘 常见问题

### Q: 找不到发布按钮？

A: 检查 IDE 顶部工具栏，通常在"运行"按钮旁边。

### Q: 发布失败怎么办？

A: 检查：
- Agent 测试是否通过
- 配置文件是否正确
- 网络连接是否正常

### Q: API Key 在哪里？

A: 发布成功后，系统会显示 API Key，或在扣子编程的设置中查看。

### Q: 前端调用跨域怎么办？

A: 在扣子编程的发布设置中配置 CORS，允许您的域名。

---

## 📚 完整文档

详细内容请查看：[扣子编程Agent发布指南.md](扣子编程Agent发布指南.md)

---

**预计耗时**: 5 分钟
**难度**: ⭐

A: 在扣子编程的发布设置中配置 CORS，允许您的域名。

---

## 📚 完整文档

详细内容请查看：[扣子编程Agent发布指南.md](扣子编程Agent发布指南.md)

---

**预计耗时**: 5 分钟
**难度**: ⭐
