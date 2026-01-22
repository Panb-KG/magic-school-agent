#!/bin/bash

# 魔法课桌学习助手 - 前端开发环境快速启动脚本

set -e

echo "╔═════════════════════════════════════════════════════════╗"
echo "║      魔法课桌学习助手 - 前端开发环境启动              ║"
echo "╚═════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT=$(cd "$(dirname "$0")/.." && pwd)
FRONTEND_DIR="$PROJECT_ROOT/magic-school-frontend"

# 检查 Python
echo -e "${BLUE}[1/5]${NC} 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}警告:${NC} 未找到 Python 3，某些功能可能无法使用"
fi

# 检查 Node.js
echo -e "${BLUE}[2/5]${NC} 检查 Node.js 环境..."
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}错误:${NC} 未找到 Node.js，请先安装 Node.js"
    echo "下载地址: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v)
echo -e "${GREEN}✓${NC} Node.js 版本: $NODE_VERSION"

# 检查 npm
if ! command -v npm &> /dev/null; then
    echo -e "${YELLOW}错误:${NC} 未找到 npm"
    exit 1
fi

NPM_VERSION=$(npm -v)
echo -e "${GREEN}✓${NC} npm 版本: $NPM_VERSION"

# 安装前端依赖
echo ""
echo -e "${BLUE}[3/5]${NC} 检查前端依赖..."
cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}首次运行，正在安装前端依赖...${NC}"
    npm install
    echo -e "${GREEN}✓${NC} 前端依赖安装完成"
else
    echo -e "${GREEN}✓${NC} 前端依赖已存在"
fi

# 安装 Python 依赖
echo ""
echo -e "${BLUE}[4/5]${NC} 检查 Python 依赖..."
cd "$PROJECT_ROOT"

if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}正在安装 Python 依赖...${NC}"
    pip install -q fastapi uvicorn pydantic python-jose[cryptography]
    echo -e "${GREEN}✓${NC} Python 依赖安装完成"
else
    echo -e "${GREEN}✓${NC} Python 依赖已存在"
fi

# 启动服务
echo ""
echo -e "${BLUE}[5/5]${NC} 启动服务..."
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "  🚀 启动前端开发服务器"
echo -e "  📡 启动 Mock API 服务器"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "📍 前端地址: ${BLUE}http://localhost:5173${NC}"
echo -e "📍 API 地址: ${BLUE}http://localhost:3000${NC}"
echo -e "📍 API 文档: ${BLUE}http://localhost:3000/docs${NC}"
echo ""
echo -e "📝 测试账号:"
echo -e "   学生: ${YELLOW}student${NC} / ${YELLOW}password123${NC}"
echo -e "   家长: ${YELLOW}parent${NC} / ${YELLOW}password123${NC}"
echo ""
echo -e "按 ${YELLOW}Ctrl+C${NC} 停止所有服务"
echo ""

# 创建日志目录
mkdir -p "$PROJECT_ROOT/logs"

# 启动 Mock API 服务器（后台）
echo -e "${BLUE}启动 Mock API 服务器...${NC}"
cd "$PROJECT_ROOT"
nohup python3 scripts/mock_api_server.py > "$PROJECT_ROOT/logs/mock_api.log" 2>&1 &
API_PID=$!
echo -e "${GREEN}✓${NC} Mock API 服务器已启动 (PID: $API_PID)"

# 等待 API 服务器启动
sleep 2

# 检查 API 服务器是否成功启动
if ! kill -0 $API_PID 2>/dev/null; then
    echo -e "${YELLOW}错误:${NC} Mock API 服务器启动失败，查看日志:"
    cat "$PROJECT_ROOT/logs/mock_api.log"
    exit 1
fi

# 启动前端开发服务器（前台）
echo -e "${BLUE}启动前端开发服务器...${NC}"
cd "$FRONTEND_DIR"

# 保存 PID 以便清理
trap "echo ''; echo -e '${YELLOW}正在停止服务...${NC}'; kill $API_PID 2>/dev/null; exit 0" INT TERM

npm run dev

# 清理
echo ""
echo -e "${YELLOW}正在停止服务...${NC}"
kill $API_PID 2>/dev/null
echo -e "${GREEN}✓${NC} 所有服务已停止"
