#!/bin/bash

# 魔法课桌智能体 API 测试脚本

BASE_URL="http://localhost:5000"

echo "=========================================="
echo "魔法课桌智能体 - API 测试"
echo "=========================================="
echo ""

# 1. 测试健康检查
echo "1️⃣  测试健康检查接口..."
curl -s "$BASE_URL/health" | jq .
echo ""
echo "✅ 健康检查完成"
echo ""

# 2. 测试对话接口（简单问候）
echo "2️⃣  测试对话接口（简单问候）..."
echo "发送：你好"
RESPONSE=$(curl -s -X POST "$BASE_URL/agent" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好",
    "session_id": "test_session_001",
    "user_id": "test_user"
  }')

echo "$RESPONSE" | jq .
echo ""
echo "✅ 对话测试完成"
echo ""

# 3. 测试时间查询功能
echo "3️⃣  测试时间查询功能..."
echo "发送：现在几点了？"
curl -s -X POST "$BASE_URL/agent" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "现在几点了？",
    "session_id": "test_session_002",
    "user_id": "test_user"
  }' | jq .
echo ""
echo "✅ 时间查询测试完成"
echo ""

# 4. 测试创建学生功能
echo "4️⃣  测试创建学生功能..."
echo "发送：帮我创建一个学生档案，姓名叫小明"
curl -s -X POST "$BASE_URL/agent" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "帮我创建一个学生档案，姓名叫小明，三年级二班",
    "session_id": "test_session_003",
    "user_id": "test_user"
  }' | jq .
echo ""
echo "✅ 创建学生测试完成"
echo ""

# 5. 测试课程表功能
echo "5️⃣  测试课程表功能..."
echo "发送：查看今天的课程表"
curl -s -X POST "$BASE_URL/agent" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "查看今天的课程表",
    "session_id": "test_session_004",
    "user_id": "test_user"
  }' | jq .
echo ""
echo "✅ 课程表测试完成"
echo ""

# 6. 测试作业功能
echo "6️⃣  测试作业功能..."
echo "发送：查看我的作业"
curl -s -X POST "$BASE_URL/agent" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "查看我的作业",
    "session_id": "test_session_005",
    "user_id": "test_user"
  }' | jq .
echo ""
echo "✅ 作业功能测试完成"
echo ""

# 7. 测试成就功能
echo "7️⃣  测试成就功能..."
echo "发送：查看我的成就"
curl -s -X POST "$BASE_URL/agent" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "查看我的成就",
    "session_id": "test_session_006",
    "user_id": "test_user"
  }' | jq .
echo ""
echo "✅ 成就功能测试完成"
echo ""

echo "=========================================="
echo "✨ 所有测试完成！"
echo "=========================================="
