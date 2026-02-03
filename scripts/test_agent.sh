#!/bin/bash

# 魔法课桌 - 简单Agent测试脚本
# 用于验证Agent服务是否正常工作

echo "=========================================="
echo "🤖 魔法课桌Agent服务测试"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Agent服务地址（使用localhost，因为公网IP安全组未开放）
AGENT_URL="http://localhost:5000"

echo -e "${BLUE}📡 测试Agent服务连接${NC}"
echo "----------------------------------------"

# 测试1: 健康检查
echo -n "1. 健康检查 ... "
health_response=$(curl -s "$AGENT_URL/health" --max-time 10)
if echo "$health_response" | grep -q "ok"; then
    echo -e "${GREEN}✅ 通过${NC}"
    echo "   响应: $health_response"
else
    echo -e "${RED}❌ 失败${NC}"
    echo "   响应: $health_response"
    echo ""
    echo -e "${YELLOW}💡 Agent服务可能未运行，请检查:${NC}"
    echo "   ps aux | grep 'main.py'"
    echo "   netstat -tlnp | grep 5000"
    exit 1
fi

echo ""

# 测试2: 简单对话
echo -e "${BLUE}💬 测试Agent对话功能${NC}"
echo "----------------------------------------"

echo "发送消息: 你好"
echo ""

chat_response=$(curl -s -X POST "$AGENT_URL/run" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "你好",
    "session_id": "test_session_'$(date +%s)'"
  }' --max-time 30)

# 检查响应
if echo "$chat_response" | grep -q "run_id"; then
    echo -e "${GREEN}✅ 对话成功${NC}"
    echo ""

    # 尝试提取最后的AI回复
    if echo "$chat_response" | python3 -c "import sys, json; data=json.load(sys.stdin); msgs=data.get('messages',[]); ai_msgs=[m for m in msgs if m.get('type')=='ai' and 'content' in m and m['content']]; print(ai_msgs[-1]['content'] if ai_msgs else '无直接回复')" 2>/dev/null; then
        echo ""
    fi

    echo ""
    echo "完整响应:"
    echo "$chat_response" | python3 -m json.tool | head -50
else
    echo -e "${RED}❌ 对话失败${NC}"
    echo "响应: $chat_response"
fi

echo ""
echo "=========================================="
echo -e "${BLUE}🔗 访问地址${NC}"
echo "=========================================="
echo ""
echo "Agent API文档: $AGENT_URL/docs"
echo "Agent健康检查: $AGENT_URL/health"
echo ""

echo -e "${GREEN}✅ 测试完成！${NC}"
echo ""
echo -e "${YELLOW}💡 下一步:${NC}"
echo "1. 在本地配置前端环境变量连接到Agent服务"
echo "2. 访问本地前端: http://localhost:5173"
echo "3. 使用测试账号登录: student / password123"
echo "4. 在智能对话页面测试Agent功能"
echo ""
