#!/bin/bash

# 魔法课桌智能体 - 简单 API 测试

BASE_URL="http://localhost:5000"

echo "=========================================="
echo "魔法课桌智能体 - API 测试"
echo "=========================================="
echo ""

# 1. 测试健康检查
echo "1️⃣  测试健康检查接口..."
curl -s "$BASE_URL/health"
echo -e "\n✅ 健康检查完成\n"

# 2. 测试对话接口（使用 /run 端点）
echo "2️⃣  测试对话接口（简单问候）..."
echo "发送：你好"
curl -s -X POST "$BASE_URL/run" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好",
    "session_id": "test_session_001",
    "user_id": "test_user"
  }'
echo -e "\n✅ 对话测试完成\n"

echo "=========================================="
echo "✨ 基础测试完成！"
echo "=========================================="
