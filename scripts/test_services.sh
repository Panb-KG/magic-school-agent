#!/bin/bash

# 魔法课桌 - 服务连通性测试脚本
# 用于测试后端服务是否正常运行并可访问

echo "=========================================="
echo "🔍 魔法课桌服务连通性测试"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数器
total_tests=0
passed_tests=0
failed_tests=0

# 测试函数
test_service() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}

    total_tests=$((total_tests + 1))
    echo -n "测试 $total_tests: $name ... "

    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" --max-time 5)

    if [ "$response" = "$expected_code" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $response)"
        passed_tests=$((passed_tests + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP $response, 期望 $expected_code)"
        failed_tests=$((failed_tests + 1))
        return 1
    fi
}

echo "📊 测试本地服务"
echo "----------------------------------------"

test_service "Agent服务健康检查" "http://localhost:5000/health"
test_service "Agent API文档" "http://localhost:5000/docs"
test_service "API后端服务" "http://localhost:3000/health"
test_service "前端服务首页" "http://localhost:5173"
test_service "测试页面" "http://localhost:5173/agent-test.html"

echo ""
echo "📊 测试Agent API功能"
echo "----------------------------------------"

test_service "Agent对话API (非流式)" "http://localhost:5000/run" -X POST \
  -H "Content-Type: application/json" \
  -d '{"query":"test","session_id":"test"}'

echo ""
echo "📊 测试CORS配置"
echo "----------------------------------------"

echo -n "测试 CORS预检请求 ... "
cors_response=$(curl -s -X OPTIONS "http://localhost:5000/run" \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -w "\n%{http_code}" 2>/dev/null)

http_code=$(echo "$cors_response" | tail -n1)
allow_origin=$(echo "$cors_response" | grep -i "access-control-allow-origin" | head -n1)

total_tests=$((total_tests + 1))
if [ "$http_code" = "200" ] && [ -n "$allow_origin" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    echo "   $allow_origin"
    passed_tests=$((passed_tests + 1))
else
    echo -e "${RED}❌ FAIL${NC}"
    failed_tests=$((failed_tests + 1))
fi

echo ""
echo "=========================================="
echo "📈 测试结果汇总"
echo "=========================================="
echo -e "总测试数: $total_tests"
echo -e "${GREEN}通过: $passed_tests${NC}"
echo -e "${RED}失败: $failed_tests${NC}"
echo ""

if [ $failed_tests -eq 0 ]; then
    echo -e "${GREEN}🎉 所有测试通过！服务运行正常。${NC}"
    exit 0
else
    echo -e "${RED}⚠️  部分测试失败，请检查服务状态。${NC}"
    exit 1
fi
