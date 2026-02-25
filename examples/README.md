# 📚 Coze API 集成示例

> 本目录包含了魔法课桌学习助手的 Coze API 集成示例代码

---

## 📁 文件列表

| 文件 | 说明 | 适用场景 |
|------|------|---------|
| `coze-api-demo.html` | 纯 HTML/JS 演示页面 | 快速测试、演示 |
| `react-integration-example.md` | React 完整集成文档 | React 项目集成 |
| `coze_client.py` | Python SDK 封装 | Python 后端集成 |

---

## 🚀 快速开始

### 方式 1：使用 HTML 演示页面（最快）

1. 打开 `coze-api-demo.html` 文件
2. 在浏览器中打开
3. 输入您的 Coze API Key 和 Bot ID
4. 开始对话！

**优点**：
- ✅ 无需安装任何依赖
- ✅ 打开即用
- ✅ 适合快速测试

---

### 方式 2：集成到 React 项目

参考 `react-integration-example.md` 文档，包含：
- 完整的 React 组件代码
- Coze API 客户端封装
- 配置管理
- 流式对话实现
- 错误处理

**优点**：
- ✅ 完整的前端解决方案
- ✅ TypeScript 支持
- ✅ 可直接复制使用

---

### 方式 3：Python SDK

使用 `coze_client.py` 文件：

```bash
# 安装依赖
pip install requests aiohttp

# 使用示例
from coze_client import MagicDeskAssistant

assistant = MagicDeskAssistant(
    api_key="your_api_key",
    bot_id="your_bot_id"
)

answer = assistant.ask("你好", "session_123", stream=True)
print(answer)
```

**优点**：
- ✅ 简单易用
- ✅ 支持同步和异步
- ✅ 支持流式和非流式

---

## 📖 使用前提

### 获取 API 凭证

在使用任何示例之前，您需要：

1. **登录 Coze 平台**
   - 访问：https://www.coze.cn/

2. **创建或进入 Bot**
   - 创建一个新的 Bot
   - 或进入已有的 Bot

3. **获取 Bot ID**
   - 在 Bot 设置页面找到 Bot ID
   - 格式：`7381xxxx`

4. **获取 API Key**
   - 在个人设置 → API Key 中获取
   - 格式：`pat_xxxxxxxxxxxxxxxx`

⚠️ **安全提示**：API Key 相当于密码，请妥善保管！

### 配置 Bot

在 Coze 平台的 Bot 中：

1. 上传您的 Agent 代码
2. 配置环境变量（如果需要）
3. 测试 Agent 功能
4. 发布 Bot

---

## 🎯 功能对比

| 功能 | HTML 演示 | React 集成 | Python SDK |
|------|-----------|-----------|-----------|
| 流式对话 | ✅ | ✅ | ✅ |
| 非流式对话 | ❌ | ✅ | ✅ |
| 文件上传 | ❌ | ❌ | ✅ |
| 异步支持 | ❌ | ❌ | ✅ |
| 配置管理 | ✅ | ✅ | ❌ |
| 历史记录 | ❌ | ✅ | ❌ |
| 错误处理 | ✅ | ✅ | ✅ |
| TypeScript | ❌ | ✅ | ❌ |
| 类型提示 | ❌ | ✅ | ✅ |

---

## 📋 API 调用示例

### 流式对话

```javascript
// JavaScript
const response = await fetch('https://api.coze.com/open_api/v2/stream_run', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
    'Content-Type': 'application/json',
    'Accept': 'text/event-stream'
  },
  body: JSON.stringify({
    bot_id: BOT_ID,
    user_id: 'session_123',
    additional_messages: [{
      role: 'user',
      content: '你好',
      content_type: 'text'
    }],
    stream: true
  })
});
```

```python
# Python
from coze_client import CozeClient

client = CozeClient(api_key=API_KEY, bot_id=BOT_ID)

for chunk in client.chat_stream("你好", "session_123"):
    print(chunk, end="", flush=True)
```

### 非流式对话

```javascript
// JavaScript
const response = await fetch('https://api.coze.com/open_api/v2/chat', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    bot_id: BOT_ID,
    user_id: 'session_123',
    additional_messages: [{
      role: 'user',
      content: '你好',
      content_type: 'text'
    }],
    stream: false
  })
});

const result = await response.json();
console.log(result.data.content);
```

```python
# Python
result = client.chat("你好", "session_123")
print(result["data"]["content"])
```

---

## 🔧 配置说明

### HTML 演示页面

配置存储在浏览器的 `localStorage` 中：
- `coze_api_key`: API Key
- `coze_bot_id`: Bot ID

### React 集成

配置通过 `ConfigPanel` 组件管理：
```typescript
const [config, setConfig] = useState({
  apiKey: '',
  botId: ''
});
```

### Python SDK

配置在初始化时传入：
```python
client = CozeClient(
    api_key="your_api_key",
    bot_id="your_bot_id"
)
```

---

## 🐛 常见问题

### Q1: API Key 从哪里获取？

**A**：
1. 登录 Coze 平台
2. 点击"个人设置" → "API Key"
3. 点击"新建 API Key"
4. 复制 API Key

### Q2: Bot ID 是什么？

**A**：
- Bot ID 是您创建的 Bot 的唯一标识
- 在 Bot 设置页面可以找到
- 格式：`7381xxxx`

### Q3: 如何测试 API 是否可用？

**A**：
1. 打开 `coze-api-demo.html`
2. 输入您的 API Key 和 Bot ID
3. 点击"发送"按钮
4. 查看是否有响应

### Q4: 流式响应和非流式响应有什么区别？

**A**：
| 特性 | 流式 | 非流式 |
|------|------|--------|
| 响应速度 | 逐字符显示 | 一次性返回 |
| 用户体验 | 更流畅 | 稍有延迟 |
| 适用场景 | 对话界面 | 后台任务 |

### Q5: 如何处理错误？

**A**：
所有示例都包含了错误处理：
- 检查响应状态码
- 捕获异常
- 显示错误消息

### Q6: 可以在生产环境使用吗？

**A**：
- ✅ 可以，但需要注意：
  - API Key 安全（不要暴露在前端）
  - 请求频率限制
  - 错误处理和重试
  - 日志记录

### Q7: 如何优化性能？

**A**：
- 使用流式响应减少延迟
- 缓存常用查询结果
- 使用异步处理
- 实现请求去重

---

## 📚 相关文档

- [Coze API 调用指南](../COZE_API_GUIDE.md) - 详细的 API 使用文档
- [API 部署说明](../API_DEPLOYMENT_GUIDE.md) - 部署架构说明
- [Agent 技术实现详解](../AGENT_TECHNICAL_SPECIFICATION.md) - Agent 功能说明
- [部署指南](../DEPLOYMENT_GUIDE_COMPLETE.md) - 完整部署文档

---

## 🤝 贡献

如果您有改进建议或发现问题，欢迎反馈！

---

## 📄 许可证

MIT License

---

**最后更新**: 2025-02-24
**版本**: 1.0.0
**维护者**: Coze Coding
