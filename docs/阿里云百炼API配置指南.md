# 🔧 阿里云百炼 API 配置指南

## 📋 配置概览

本项目已成功配置阿里云百炼（DashScope）API，使用 qwen-turbo 模型为魔法课桌智能体提供大语言模型服务。

---

## ✅ 配置状态

| 配置项 | 值 | 状态 |
|--------|-----|------|
| **API 提供商** | 阿里云百炼 (DashScope) | ✅ 已配置 |
| **模型** | qwen-turbo | ✅ 已启用 |
| **API Key** | sk-f02e3eb3ddff4251a1aaddac91ccb724 | ✅ 已配置 |
| **Base URL** | https://dashscope.aliyuncs.com/compatible-mode/v1 | ✅ 已配置 |
| **温度** | 0.7 | ✅ 已优化 |
| **Top P** | 0.95 | ✅ 已优化 |

---

## 📁 配置文件

### 1. 模型配置文件

**位置**: `/workspace/projects/config/agent_llm_config.json`

```json
{
    "config": {
        "model": "qwen-turbo",
        "temperature": 0.7,
        "top_p": 0.95,
        "max_completion_tokens": 4000,
        "timeout": 600,
        "thinking": "disabled"
    },
    "api_config": {
        "api_key": "sk-f02e3eb3ddff4251a1aaddac91ccb724",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
    },
    "sp": "...",
    "tools": [...]
}
```

---

## 🔧 代码修改

### Agent 代码修改

**位置**: `/workspace/projects/src/agents/agent.py`

修改了 `build_agent` 函数，支持从配置文件读取 API 配置：

```python
# 从配置文件读取 API 配置，如果不存在则使用环境变量
api_config = cfg.get('api_config', {})
api_key = api_config.get('api_key') or os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
base_url = api_config.get('base_url') or os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")

llm = ChatOpenAI(
    model=cfg['config'].get("model"),
    api_key=api_key,
    base_url=base_url,
    # ...
)
```

---

## 🧪 测试结果

### 测试 1: 基础对话

```bash
curl -X POST http://localhost:5000/run \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，请介绍一下你自己",
    "session_id": "test_qwen_001",
    "user_id": "test_user"
  }'
```

**结果**: ✅ 成功
- 模型正常响应
- 使用 qwen-turbo 模型
- 返回友好的问候和功能介绍

### 测试 2: 健康检查

```bash
curl http://localhost:5000/health
```

**结果**: ✅ 成功
```json
{"status":"ok","message":"Service is running"}
```

---

## 🚀 支持的阿里云百炼模型

### 可用模型列表

| 模型名称 | 说明 | 推荐场景 |
|---------|------|----------|
| **qwen-turbo** | 速度快、成本低 | 当前使用，适合实时对话 |
| **qwen-plus** | 性能更强、推理能力更好 | 复杂推理、工具调用 |
| **qwen-max** | 最强性能、成本最高 | 高质量输出、复杂任务 |
| **qwen-long** | 长上下文支持 | 长文档处理 |

### 切换模型

如需切换到其他模型，修改 `config/agent_llm_config.json` 中的 `model` 字段：

```json
{
    "config": {
        "model": "qwen-plus",  // 或 "qwen-max"
        // ...
    }
}
```

然后重启服务：
```bash
./scripts/manage_agent.sh restart
```

---

## 🔐 安全注意事项

### API Key 安全

1. **不要将 API Key 提交到公开仓库**
   - 已在 `.gitignore` 中配置敏感文件
   - 生产环境建议使用环境变量

2. **使用环境变量（推荐）**

   可以通过环境变量配置，而不是硬编码在配置文件中：

   ```bash
   export ALIYUN_API_KEY="sk-f02e3eb3ddff4251a1aaddac91ccb724"
   export ALIYUN_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
   ```

   然后修改代码优先使用环境变量：
   ```python
   api_key = os.getenv("ALIYUN_API_KEY") or api_config.get('api_key')
   base_url = os.getenv("ALIYUN_BASE_URL") or api_config.get('base_url')
   ```

3. **定期轮换 API Key**
   - 建议定期更换 API Key
   - 使用 API Key 管理工具（如 HashiCorp Vault）

---

## 📊 性能监控

### 查看模型调用日志

```bash
# 查看实时日志
tail -f /var/log/magic-school-agent.log

# 搜索模型调用
grep "model_name" /var/log/magic-school-agent.log

# 搜索错误
grep -i "error" /var/log/magic-school-agent.log
```

### API 调用统计

查看 LangGraph 日志：
```bash
tail -f /app/work/logs/bypass/app.log
```

---

## 🔧 故障排查

### 问题 1: API 调用失败

**症状**: 服务返回错误或超时

**解决方案**:

1. 检查 API Key 是否正确
   ```bash
   grep "api_key" /workspace/projects/config/agent_llm_config.json
   ```

2. 检查网络连接
   ```bash
   curl -I https://dashscope.aliyuncs.com
   ```

3. 检查 API 配额
   - 登录阿里云百炼控制台
   - 查看 API 调用次数和配额

### 问题 2: 模型响应慢

**症状**: 响应时间过长

**解决方案**:

1. 切换到更快的模型（如 qwen-turbo）
2. 减少 `max_completion_tokens`
3. 优化系统提示词长度

### 问题 3: 工具调用不触发

**症状**: 模型不调用工具

**解决方案**:

1. 调整 `temperature` 和 `top_p` 参数
2. 优化系统提示词，明确说明工具使用规则
3. 尝试使用更强的模型（如 qwen-plus）

---

## 📚 相关文档

- [阿里云百炼官方文档](https://help.aliyun.com/zh/dashscope/)
- [OpenAI 兼容接口文档](https://help.aliyun.com/zh/dashscope/developer-reference/use-qwen-by-calling-api)
- [Qwen 模型介绍](https://help.aliyun.com/zh/dashscope/developer-reference/models)

---

## 📝 更新日志

### 2025-02-22

- ✅ 配置阿里云百炼 API key
- ✅ 修改 Agent 代码支持配置文件读取
- ✅ 切换到 qwen-turbo 模型
- ✅ 测试服务正常运行
- ✅ 创建配置文档

---

**配置完成时间**: 2025-02-22
**维护者**: Magic School Team
