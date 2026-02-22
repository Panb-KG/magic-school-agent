# ⚡ 扣子编程 Agent 部署快速指南

## 3步完成部署

---

## 步骤 1：点击"部署"按钮 🚀

在扣子编程 IDE 顶部工具栏，找到 **"部署"** 按钮

---

## 步骤 2：配置部署选项

| 选项 | 选择 |
|------|------|
| **部署类型** | HTTP 服务 |
| **访问权限** | 私有（需要 API Key） |

点击"确认"或"部署"

---

## 步骤 3：复制信息

部署成功后，系统会显示：

```
✅ 部署成功！

📍 服务地址: https://api.coze.cn/v1/agent/your_agent_id
🔑 API Key: sk-xxxxxxxxxxxxxxxx
```

**重要**：复制并保存这两个信息！

---

## 🧪 快速测试

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"message":"你好","session_id":"test","user_id":"user"}' \
  https://api.coze.cn/v1/agent/your_agent_id/run
```

---

## 💻 前端集成代码

```javascript
const API_URL = 'https://api.coze.cn/v1/agent/your_agent_id/run';
const API_KEY = 'YOUR_API_KEY';

async function chat(message, sessionId, userId) {
  const response = await fetch(API_URL, {
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

  const result = await response.json();
  return result.messages[result.messages.length - 1].content;
}

// 使用
chat('你好', 'session_001', 'user_001')
  .then(reply => console.log('AI:', reply));
```

---

## ✅ 检查清单

- [ ] 点击"部署"按钮
- [ ] 选择"HTTP 服务"
- [ ] 复制服务地址
- [ ] 复制 API Key
- [ ] 测试 API 调用
- [ ] 集成到前端

---

**现在点击"部署"按钮开始部署！** 🚀
