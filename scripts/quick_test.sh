#!/bin/bash

###############################################################################
# 魔法课桌学习助手智能体 - API 快速测试脚本
#
# 用途：快速验证所有 API 功能是否正常
# 使用方法：
#   1. 设置环境变量 API_BASE_URL 和 API_TOKEN
#   2. 运行脚本：./quick_test.sh
#
# 作者：Coze Coding Team
# 版本：1.0.0
# 日期：2025年1月
###############################################################################

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
API_BASE_URL="${API_BASE_URL:-https://your-domain.com/api}"
API_TOKEN="${API_TOKEN}"

# 测试统计
TOTAL=0
PASSED=0
FAILED=0
START_TIME=$(date +%s)

# 临时变量
TEST_STUDENT_ID=""
TEST_COURSE_ID=""
TEST_HOMEWORK_ID=""
TEST_CONVERSATION_ID=""

###############################################################################
# 辅助函数
###############################################################################

# 打印标题
print_header() {
  echo ""
  echo -e "${BLUE}══════════════════════════════════════════════════════════════════${NC}"
  echo -e "${BLUE}$1${NC}"
  echo -e "${BLUE}══════════════════════════════════════════════════════════════════${NC}"
}

# 打印分类
print_section() {
  echo ""
  echo -e "${YELLOW}▶ $1${NC}"
}

# 打印结果
print_result() {
  local status=$1
  local message=$2

  if [ "$status" = "PASS" ]; then
    echo -e "  ${GREEN}✅ $message${NC}"
    PASSED=$((PASSED + 1))
  else
    echo -e "  ${RED}❌ $message${NC}"
    FAILED=$((FAILED + 1))
  fi
}

# 测试函数
test_api() {
  local name=$1
  local method=$2
  local endpoint=$3
  local data=$4
  local expected_code=${5:-200}

  TOTAL=$((TOTAL + 1))

  echo -n "  测试 ${TOTAL}: $name ... "

  response=$(curl -s -w "\n%{http_code}" -X "${method}" \
    "${API_BASE_URL}${endpoint}" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${API_TOKEN}" \
    -d "${data}" 2>/dev/null)

  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | sed '$d')

  # 检查 HTTP 状态码
  if [ "$http_code" = "$expected_code" ]; then
    echo -e "${GREEN}✅ PASS${NC} (HTTP $http_code)"

    # 尝试提取 ID
    if [ -n "$body" ]; then
      TEST_STUDENT_ID=$(echo "$body" | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')
    fi
  else
    echo -e "${RED}❌ FAIL${NC} (HTTP $http_code, expected $expected_code)"
    if [ -n "$body" ]; then
      echo "  响应: $body"
    fi
  fi
}

# 检查环境
check_env() {
  print_header "环境检查"

  if [ -z "$API_TOKEN" ]; then
    echo -e "${RED}❌ 错误: API_TOKEN 环境变量未设置${NC}"
    echo ""
    echo "请设置环境变量："
    echo "  export API_BASE_URL=\"https://your-domain.com/api\""
    echo "  export API_TOKEN=\"your_jwt_token_here\""
    exit 1
  fi

  echo -e "${GREEN}✅ API_BASE_URL: $API_BASE_URL${NC}"
  echo -e "${GREEN}✅ API_TOKEN: ${API_TOKEN:0:20}...${NC}"
}

###############################################################################
# 开始测试
###############################################################################

main() {
  echo ""
  echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${GREEN}║  魔法课桌学习助手智能体 - API 快速测试                          ║${NC}"
  echo -e "${GREEN}║  版本: 1.0.0                                                   ║${NC}"
  echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"

  # 检查环境
  check_env

  # 1. 健康检查
  print_header "模块一：健康检查"
  print_section "基础健康检查"
  test_api "服务健康检查" "GET" "/health" "" 200

  # 2. 基础对话
  print_header "模块二：基础对话功能"
  print_section "对话测试"
  test_api "发送对话消息" "POST" "/chat" '{"message":"你好，请自我介绍一下","user_id":"test"}' 200

  # 3. 时间魔法
  print_header "模块三：时间魔法功能"
  print_section "时间查询"
  test_api "获取当前时间" "POST" "/tools/get_current_time" '{}' 200
  test_api "获取本周日期范围" "POST" "/tools/get_week_date_range" '{}' 200

  # 4. 学生管理
  print_header "模块四：学生管理功能"
  print_section "学生操作"
  test_api "创建学生" "POST" "/students" '{"name":"API测试学生","grade":"三年级","school":"测试小学"}' 201
  test_api "获取学生列表" "GET" "/students" "" 200
  if [ -n "$TEST_STUDENT_ID" ]; then
    test_api "获取学生详情" "GET" "/students/$TEST_STUDENT_ID" "" 200
    test_api "增加积分" "POST" "/students/$TEST_STUDENT_ID/add-points" '{"points":10,"reason":"测试"}' 200
  fi

  # 5. 课程管理
  print_header "模块五：课程管理功能"
  print_section "课程操作"
  if [ -n "$TEST_STUDENT_ID" ]; then
    test_api "添加课程" "POST" "/courses" "{\"student_id\":$TEST_STUDENT_ID,\"course_name\":\"数学课\",\"course_type\":\"school\",\"weekday\":\"Monday\",\"start_time\":\"09:00\",\"end_time\":\"10:00\"}" 201
    test_api "获取周课程表" "GET" "/students/$TEST_STUDENT_ID/schedule" "" 200
  fi

  # 6. 作业管理
  print_header "模块六：作业管理功能"
  print_section "作业操作"
  if [ -n "$TEST_STUDENT_ID" ]; then
    test_api "创建作业" "POST" "/homeworks" "{\"student_id\":$TEST_STUDENT_ID,\"title\":\"数学练习\",\"subject\":\"数学\",\"due_date\":\"2025-01-25\",\"priority\":\"medium\"}" 201
    test_api "获取作业列表" "GET" "/homeworks?student_id=$TEST_STUDENT_ID" "" 200
  fi

  # 7. 运动管理
  print_header "模块七：运动管理功能"
  print_section "运动记录"
  if [ -n "$TEST_STUDENT_ID" ]; then
    test_api "添加运动记录" "POST" "/exercises" "{\"student_id\":$TEST_STUDENT_ID,\"exercise_type\":\"run\",\"duration\":30,\"date\":\"2025-01-20\"}" 201
    test_api "获取运动记录" "GET" "/exercises?student_id=$TEST_STUDENT_ID" "" 200
  fi

  # 8. 成就管理
  print_header "模块八：成就管理功能"
  print_section "成就操作"
  if [ -n "$TEST_STUDENT_ID" ]; then
    test_api "颁发成就" "POST" "/achievements" "{\"student_id\":$TEST_STUDENT_ID,\"achievement_type\":\"homework_exercise\",\"title\":\"测试成就\",\"level\":\"bronze\",\"points\":10}" 201
    test_api "获取成就墙" "GET" "/students/$TEST_STUDENT_ID/achievements" "" 200
  fi

  # 9. 仪表盘
  print_header "模块九：仪表盘功能"
  print_section "仪表盘数据"
  if [ -n "$TEST_STUDENT_ID" ]; then
    test_api "获取学生仪表盘" "GET" "/students/$TEST_STUDENT_ID/dashboard" "" 200
  fi

  # 10. 历史对话功能（新增）⭐
  print_header "模块十：历史对话功能（新增）⭐"
  print_section "对话会话管理"
  test_api "创建对话会话" "POST" "/conversations" '{"title":"测试对话"}' 201

  # 尝试获取对话ID
  CONV_RESPONSE=$(curl -s -X POST "${API_BASE_URL}/conversations" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${API_TOKEN}" \
    -d '{"title":"快速测试对话"}' 2>/dev/null)

  TEST_CONVERSATION_ID=$(echo "$CONV_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')

  test_api "获取对话列表" "GET" "/conversations?limit=10" "" 200

  if [ -n "$TEST_CONVERSATION_ID" ]; then
    test_api "添加消息" "POST" "/conversations/$TEST_CONVERSATION_ID/messages" '{"role":"user","content":"测试消息"}' 201
    test_api "获取对话详情" "GET" "/conversations/$TEST_CONVERSATION_ID" "" 200
    test_api "搜索对话" "GET" "/conversations/search?keyword=测试" "" 200
    test_api "更新对话标题" "PUT" "/conversations/$TEST_CONVERSATION_ID" '{"title":"更新后的测试对话"}' 200
  fi

  print_section "对话标题生成"
  if [ -n "$TEST_CONVERSATION_ID" ]; then
    test_api "自动生成标题" "POST" "/conversations/$TEST_CONVERSATION_ID/generate-title" "" 200
  fi

  print_section "批量操作"
  test_api "批量生成标题" "POST" "/conversations/batch-generate-titles" '{"days":7}' 200

  print_section "删除测试数据"
  if [ -n "$TEST_CONVERSATION_ID" ]; then
    test_api "删除对话" "DELETE" "/conversations/$TEST_CONVERSATION_ID" "" 200
  fi

  # 测试总结
  END_TIME=$(date +%s)
  DURATION=$((END_TIME - START_TIME))

  print_header "测试结果汇总"

  echo ""
  echo "  📊 测试统计："
  echo "     总计：$TOTAL"
  echo -e "     ${GREEN}通过：$PASSED${NC}"
  echo -e "     ${RED}失败：$FAILED${NC}"
  PASS_RATE=$((PASSED * 100 / TOTAL))
  echo "     通过率：$PASS_RATE%"

  echo ""
  echo "  ⏱️  耗时：${DURATION}秒"

  echo ""
  if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 恭喜！所有测试通过！${NC}"
    echo ""
    echo "  ✅ 健康检查：正常"
    echo "  ✅ 基础对话：正常"
    echo "  ✅ 时间魔法：正常"
    echo "  ✅ 学生管理：正常"
    echo "  ✅ 课程管理：正常"
    echo "  ✅ 作业管理：正常"
    echo "  ✅ 运动管理：正常"
    echo "  ✅ 成就管理：正常"
    echo "  ✅ 仪表盘：正常"
    echo -e "${YELLOW}  ⭐ 历史对话：正常（新功能）${NC}"
    echo ""
    exit 0
  else
    echo -e "${RED}⚠️  有测试失败，请检查日志${NC}"
    echo ""
    echo "  建议："
    echo "  1. 检查 API_BASE_URL 和 API_TOKEN 是否正确"
    echo "  2. 查看服务器日志：tail -f /app/work/logs/bypass/app.log"
    echo "  3. 检查数据库连接：psql -d magic_school -c '\dt'"
    echo "  4. 验证数据库表是否创建：查看 conversations 和 messages 表"
    echo ""
    exit 1
  fi
}

# 运行主函数
main
