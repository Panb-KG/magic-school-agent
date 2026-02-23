# API 快速测试执行指南

## 🚀 快速开始

### 步骤1：设置环境变量

```bash
# 设置 API 地址
export API_BASE_URL="https://your-domain.com/api"

# 设置认证 Token（替换为你的 Token）
export API_TOKEN="your_jwt_token_here"
```

### 步骤2：运行测试脚本

```bash
cd /workspace/projects
./scripts/quick_test.sh
```

### 步骤3：查看结果

脚本会自动运行所有测试并显示结果：
- ✅ PASS：测试通过
- ❌ FAIL：测试失败
- 📊 统计信息：总计、通过、失败、通过率

---

## 📋 测试覆盖

测试脚本会自动测试以下功能：

### 基础功能（9个测试）
1. ✅ 服务健康检查
2. ✅ 发送对话消息
3. ✅ 获取当前时间
4. ✅ 获取本周日期范围
5. ✅ 创建学生
6. ✅ 获取学生列表
7. ✅ 获取学生详情
8. ✅ 增加积分
9. ✅ 添加课程

### 核心功能（8个测试）
10. ✅ 获取周课程表
11. ✅ 创建作业
12. ✅ 获取作业列表
13. ✅ 添加运动记录
14. ✅ 获取运动记录
15. ✅ 颁发成就
16. ✅ 获取成就墙
17. ✅ 获取学生仪表盘

### 历史对话功能（新增）⭐（9个测试）
18. ✅ 创建对话会话
19. ✅ 添加消息
20. ✅ 获取对话列表（按时间倒序）
21. ✅ 获取对话详情
22. ✅ 搜索对话
23. ✅ 更新对话标题
24. ✅ 自动生成标题
25. ✅ 批量生成标题
26. ✅ 删除对话

**总计：26 个自动测试**

---

## 📊 测试输出示例

```
╔════════════════════════════════════════════════════════════════╗
║  魔法课桌学习助手智能体 - API 快速测试                          ║
║  版本: 1.0.0                                                   ║
╚════════════════════════════════════════════════════════════════╝

══════════════════════════════════════════════════════════════════
环境检查
══════════════════════════════════════════════════════════════════
✅ API_BASE_URL: https://your-domain.com/api
✅ API_TOKEN: eyJhbGciOiJIUzI1NiIs...

══════════════════════════════════════════════════════════════════
模块一：健康检查
══════════════════════════════════════════════════════════════════
▶ 基础健康检查
  测试 1: 服务健康检查 ... ✅ PASS (HTTP 200)

══════════════════════════════════════════════════════════════════
模块十：历史对话功能（新增）⭐
══════════════════════════════════════════════════════════════════
▶ 对话会话管理
  测试 18: 创建对话会话 ... ✅ PASS (HTTP 201)
  测试 19: 获取对话列表 ... ✅ PASS (HTTP 200)
  ...

══════════════════════════════════════════════════════════════════
测试结果汇总
══════════════════════════════════════════════════════════════════

  📊 测试统计：
     总计：26
     通过：26
     失败：0
     通过率：100%

  ⏱️  耗时：15秒

🎉 恭喜！所有测试通过！

  ✅ 健康检查：正常
  ✅ 基础对话：正常
  ✅ 时间魔法：正常
  ✅ 学生管理：正常
  ✅ 课程管理：正常
  ✅ 作业管理：正常
  ✅ 运动管理：正常
  ✅ 成就管理：正常
  ✅ 仪表盘：正常
  ⭐ 历史对话：正常（新功能）
```

---

## ❌ 测试失败处理

### 常见问题

#### 1. 认证失败（401）

**错误信息**:
```
测试 1: 服务健康检查 ... ❌ FAIL (HTTP 401, expected 200)
```

**解决方法**:
```bash
# 重新获取 Token
export API_TOKEN="new_token_here"
./scripts/quick_test.sh
```

#### 2. 服务未响应

**错误信息**:
```
curl: (7) Failed to connect to your-domain.com
```

**解决方法**:
```bash
# 检查服务状态
curl https://your-domain.com/health

# 检查 DNS
ping your-domain.com

# 检查防火墙
telnet your-domain.com 443
```

#### 3. 数据库表未创建

**错误信息**:
```
错误：relation "conversations" does not exist
```

**解决方法**:
```bash
# 执行数据库迁移
python -c "
import sys
sys.path.insert(0, 'src')
from storage.database.db import engine
from storage.database.shared.model import Base
Base.metadata.create_all(bind=engine)
print('✅ 数据库表创建成功')
"
```

#### 4. 新功能未生效

**检查项**:
```bash
# 1. 检查数据库表
psql -d magic_school -c "\dt conversations"
psql -d magic_database -c "\dt messages"

# 2. 检查服务日志
tail -50 /app/work/logs/bypass/app.log

# 3. 重启服务
sudo systemctl restart magic-school-backend
```

---

## 🔧 手动测试（可选）

如果你想手动测试特定功能：

### 测试历史对话功能

```bash
# 1. 创建对话
curl -X POST "${API_BASE_URL}/conversations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -d '{"title":"测试对话"}'

# 2. 获取对话列表
curl -X GET "${API_BASE_URL}/conversations?limit=10" \
  -H "Authorization: Bearer ${API_TOKEN}"

# 3. 搜索对话
curl -X GET "${API_BASE_URL}/conversations/search?keyword=测试" \
  -H "Authorization: Bearer ${API_TOKEN}"

# 4. 生成标题
curl -X POST "${API_BASE_URL}/conversations/1/generate-title" \
  -H "Authorization: Bearer ${API_TOKEN}"
```

---

## 📝 测试报告

测试完成后，脚本会显示：
- 测试总数
- 通过数量
- 失败数量
- 通过率
- 耗时

**示例报告**:
```
📊 测试统计：
   总计：26
   通过：26
   失败：0
   通过率：100%

⏱️  耗时：15秒
```

---

## 🎯 测试标准

### 通过标准
- 所有测试用例通过
- 通过率 ≥ 95%
- 无关键功能失败

### 失败标准
- 关键功能失败（健康检查、认证、基础对话）
- 历史对话功能失败（新增功能）
- 数据库操作失败

---

## 📞 获取帮助

如果测试失败：

1. **查看日志**
   ```bash
   tail -f /app/work/logs/bypass/app.log
   ```

2. **检查数据库**
   ```bash
   psql -d magic_school -c "\dt"
   ```

3. **重启服务**
   ```bash
   sudo systemctl restart magic-school-backend
   ```

4. **联系支持**
   - 提供错误信息
   - 提供日志片段
   - 提供环境信息

---

## ✅ 测试检查清单

测试前：
- [ ] 已设置 API_BASE_URL
- [ ] 已设置 API_TOKEN
- [ ] 服务已启动
- [ ] 数据库已连接

测试中：
- [ ] 所有测试运行
- [ ] 查看输出结果
- [ ] 记录失败信息

测试后：
- [ ] 通过率 ≥ 95%
- [ ] 新功能正常
- [ ] 无关键错误
- [ ] 保存测试报告

---

## 🎉 成功标准

✅ **所有测试通过**
- 通过率：100%
- 耗时：< 30秒
- 无错误日志

✅ **新功能验证**
- 历史对话功能：正常
- 对话标题生成：正常
- 批量操作：正常

✅ **系统健康**
- 服务响应正常
- 数据库连接正常
- 认证系统正常

---

**文档版本**: 1.0.0
**最后更新**: 2025年1月
**维护者**: Coze Coding Team
