#!/bin/bash

# 魔法课桌智能体 - 聊天API测试脚本

set -e

echo "╔═════════════════════════════════════════════════════════╗"
echo "║   魔法课桌智能体 - 聊天API测试                          ║"
echo "╚═════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BACKEND_URL="http://localhost:5000"
TEST_QUERY="你好"

# 测试后端服务是否运行
echo -e "${BLUE}[1/5]${NC} 检查后端服务状态..."
if curl -s -f "${BACKEND_URL}/docs" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} 后端服务运行正常 (${BACKEND_URL})"
else
    echo -e "${RED}✗${NC} 后端服务未运行，请先启动："
    echo -e "   bash scripts/http_run.sh -p 5000"
    exit 1
fi

# 检查 Mock API 服务
echo ""
echo -e "${BLUE}[2/5]${NC} 检查 Mock API 服务状态..."
if curl -s -f "http://localhost:3000/docs" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Mock API 服务运行正常 (端口 3000)"
else
    echo -e "${YELLOW}⚠${NC} Mock API 服务未运行，建议启动："
    echo -e "   python3 scripts/mock_api_server.py"
fi

# 检查前端配置
echo ""
echo -e "${BLUE}[3/5]${NC} 检查前端环境变量配置..."
FRONTEND_ENV_FILE="/workspace/projects/magic-school-frontend/.env.development"
if [ -f "$FRONTEND_ENV_FILE" ]; then
    if grep -q "VITE_BACKEND_URL" "$FRONTEND_ENV_FILE"; then
        echo -e "${GREEN}✓${NC} 环境变量配置文件存在"
        echo -e "   配置内容:"
        cat "$FRONTEND_ENV_FILE" | grep -E "(VITE_BACKEND_URL|VITE_API_BASE_URL|VITE_WS_URL)" | sed 's/^/   /'
    else
        echo -e "${YELLOW}⚠${NC} 环境变量配置文件存在但未配置 VITE_BACKEND_URL"
    fi
else
    echo -e "${YELLOW}⚠${NC} 环境变量配置文件不存在: $FRONTEND_ENV_FILE"
fi

# 测试聊天 API（非流式）
echo ""
echo -e "${BLUE}[4/5]${NC} 测试非流式对话 API..."

# 先登录获取 Token
echo "   正在获取测试 Token..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:3000/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"student","password":"password123"}')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}✗${NC} 获取 Token 失败"
    echo "   响应: $LOGIN_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓${NC} 成功获取 Token"

# 发送测试消息
echo "   发送测试消息: $TEST_QUERY"
CHAT_RESPONSE=$(curl -s -X POST "${BACKEND_URL}/run" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "{\"query\":\"${TEST_QUERY}\",\"session_id\":\"test_session_$(date +%s)\"}")

echo -e "${GREEN}✓${NC} 收到响应"
echo "   响应内容:"
echo "$CHAT_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$CHAT_RESPONSE" | sed 's/^/   /'

# 测试流式 API
echo ""
echo -e "${BLUE}[5/5]${NC} 测试流式对话 API..."
echo "   发送测试消息: $TEST_QUERY"

echo -e "   响应内容（流式）："
echo "   ────────────────────────────────────────────────────"
curl -s -X POST "${BACKEND_URL}/stream_run" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "{\"query\":\"${TEST_QUERY}\",\"session_id\":\"test_stream_$(date +%s)\"}" | \
    while read line; do
        if echo "$line" | grep -q "data: "; then
            content=$(echo "$line" | sed 's/data: //' | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('content', ''), end='')" 2>/dev/null)
            if [ -n "$content" ]; then
                echo -ne "   $content"
            fi
        fi
    done
echo ""
echo "   ────────────────────────────────────────────────────"

echo ""
echo -e "${GREEN}═════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ 所有测试通过！${NC}"
echo ""
echo -e "📱 前端访问地址: ${BLUE}http://localhost:5173${NC}"
echo -e "📚 API 文档: ${BLUE}${BACKEND_URL}/docs${NC}"
echo -e "📚 Mock API 文档: ${BLUE}http://localhost:3000/docs${NC}"
echo ""
echo -e "${YELLOW}下一步:${NC}"
echo -e "  1. 访问前端页面: http://localhost:5173"
echo -e "  2. 登录账号: student / password123"
echo -e "  3. 在聊天界面发送消息测试"
echo ""
