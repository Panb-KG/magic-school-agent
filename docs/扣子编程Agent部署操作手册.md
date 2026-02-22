# 🚀 扣子编程 Agent 部署操作手册

## 当前状态确认

✅ Agent 代码已开发完成
✅ 已通过测试（test_run）
✅ 配置文件正确（config/agent_llm_config.json）
✅ 工具已正确导入

---

## 🎯 部署操作步骤

### 步骤 1：查看 IDE 顶部工具栏

在扣子编程 IDE 顶部，您会看到工具栏，通常包含：

```
[运行] [调试] [部署 🚀] [设置]
```

找到 **"部署"** 按钮（显示为 🚀 图标或"部署"文字）

---

### 步骤 2：点击部署按钮

1. 点击 **"部署"** 按钮
2. 系统会弹出部署配置对话框

---

### 步骤 3：配置部署选项

在部署对话框中，您会看到以下选项：

#### 选项 1：部署类型

选择部署类型：

| 部署类型 | 说明 | 推荐度 |
|---------|------|--------|
| **HTTP 服务** | 部署为 HTTP API，可外部调用 | ⭐⭐⭐⭐⭐ |
| **Bot** | 部署为对话 Bot | ⭐⭐⭐ |
| **工作流** | 部署为工作流组件 | ⭐⭐ |

**请选择：HTTP 服务**

#### 选项 2：服务配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| 服务名称 | Agent 的名称 | magic-school-agent |
| 服务描述 | Agent 的描述 | 魔法课桌学习助手智能体 |
| 端口 | 服务端口（自动分配） | 自动 |
| 认证方式 | API Key 或 Token | API Key |

#### 选项 3：访问权限

| 权限类型 | 说明 |
|---------|------|
| **公开** | 任何人都可以调用（不推荐） |
| **私有** | 需要 API Key 认证（推荐） |

**请选择：私有**

---

### 步骤 4：确认部署

1. 检查所有配置项是否正确
2. 点击 **"确认"** 或 **"部署"** 按钮
3. 等待系统完成部署

**预计耗时**：30 秒 - 1 分钟

---

### 步骤 5：获取部署信息

部署成功后，系统会显示以下信息：

```
✅ 部署成功！

📦 服务信息
---------------------------
服务名称: magic-school-agent
服务类型: HTTP 服务

📍 API 端点
---------------------------
服务地址: https://api.coze.cn/v1/agent/your_agent_id
健康检查: https://api.coze.cn/v1/agent/your_agent_id/health
对话接口: https://api.coze.cn/v1/agent/your_agent_id/run
API 文档: https://api.coze.cn/v1/agent/your_agent_id/docs

🔑 认证信息
---------------------------
API Key: sk-xxxxxxxxxxxxxxxxxxxxxxxx

📝 使用说明
---------------------------
1. 使用 API Key 在请求头中认证
2. 访问 API 文档查看详细接口说明
3. 开始集成到您的应用中

⚠️  请妥善保管 API Key，不要泄露！
```

**重要**：请复制并保存：
- ✅ **服务地址**
- ✅ **API Key**

---

## 📋 部署后操作清单

### 1. 测试服务

使用 curl 测试（替换 YOUR_API_KEY 和 your_agent_id）：

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"message":"你好","session_id":"test","user_id":"user"}' \
  https://api.coze.cn/v1/agent/your_agent_id/run
```

预期响应：
```json
{
  "messages": [
    {
      "content": "你好呀，小巫师！...",
      "type": "ai"
    }
  ],
  "run_id": "xxx"
}
```

### 2. 查看 API 文档

访问 API 文档地址：
```
https://api.coze.cn/v1/agent/your_agent_id/docs
```

在 Swagger UI 中可以：
- 查看所有 API 端点
- 在线测试接口
- 查看请求/响应格式

### 3. 配置前端调用

在前端项目中，创建配置文件：

```javascript
// config/agent.js
export const agentConfig = {
  apiUrl: 'https://api.coze.cn/v1/agent/your_agent_id',
  apiKey: 'YOUR_API_KEY',
  
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

    return response.json();
  }
};
```

---

## 🔧 常见问题

### Q1: 找不到"部署"按钮？

**可能原因和解决方案**：

1. **工具栏被折叠**
   - 查看窗口顶部是否有折叠按钮
   - 点击展开工具栏

2. **在调试模式**
   - 退出调试模式
   - 查找部署按钮

3. **版本限制**
   - 确认您的扣子编程账号是否有部署权限
   - 联系扣子支持团队

### Q2: 点击部署后没有反应？

**解决方案**：

1. 检查网络连接
2. 刷新页面重试
3. 查看浏览器控制台是否有错误
4. 尝试使用其他浏览器

### Q3: 部署失败，提示错误？

**常见错误和解决方案**：

| 错误提示 | 原因 | 解决方案 |
|---------|------|---------|
| "配置文件错误" | config 文件格式不正确 | 检查 JSON 格式 |
| "依赖缺失" | requirements.txt 缺少依赖 | 补充缺失的包 |
| "测试未通过" | test_run 测试失败 | 运行 test_run 修复错误 |

### Q4: 如何查看部署历史？

1. 在扣子编程 IDE 中，点击"设置"
2. 找到"部署历史"或"部署记录"
3. 查看所有的部署记录和状态

### Q5: 如何更新已部署的 Agent？

1. 修改 Agent 代码
2. 运行 test_run 测试
3. 点击"部署"按钮
4. 系统会自动更新已部署的服务

---

## 🎯 部署完成确认清单

- [ ] 找到并点击"部署"按钮
- [ ] 选择部署类型：HTTP 服务
- [ ] 配置服务信息
- [ ] 点击确认部署
- [ ] 等待部署完成
- [ ] 复制服务地址
- [ ] 复制 API Key
- [ ] 测试 API 调用
- [ ] 访问 API 文档
- [ ] 配置前端集成

---

## 📝 下一步操作

部署成功后，您可以：

1. **集成到前端**
   - 使用提供的 JavaScript 代码
   - 配置环境变量
   - 实现聊天界面

2. **测试完整流程**
   - 前端调用 API
   - 验证响应格式
   - 测试各种场景

3. **部署到生产**
   - 使用生产环境 API Key
   - 配置监控和日志
   - 设置访问限制

---

## 🆘 需要帮助？

如果在部署过程中遇到问题：

1. 查看扣子编程官方文档
2. 联系扣子技术支持
3. 查看本文档的"常见问题"部分

---

## 🎯 快速开始（3步完成）

### 第一步：点击"部署" 🚀

在扣子编程 IDE 顶部，找到 **"部署"** 按钮

### 第二步：选择配置

- 部署类型：**HTTP 服务**
- 访问权限：**私有**

### 第三步：获取信息

部署成功后，复制：
- ✅ 服务地址
- ✅ API Key

---

**现在请在扣子编程 IDE 中点击"部署"按钮并开始部署！** 🚀

如有任何问题，随时告诉我。
