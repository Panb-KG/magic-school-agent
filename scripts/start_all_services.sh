#!/bin/bash

# 魔法课桌智能体 - 一键启动所有后端服务

set -e

echo "╔═════════════════════════════════════════════════════════╗"
echo "║      魔法课桌智能体 - 后端服务一键启动                  ║"
echo "╚═════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="${COZE_WORKSPACE_PATH:-/workspace/projects}"
cd "$PROJECT_ROOT"

# 检查端口占用
check_port() {
    local port=$1
    local service=$2
    if netstat -tlnp 2>/dev/null | grep -q ":$port " || ss -tlnp 2>/dev/null | grep -q ":$port "; then
        echo -e "${YELLOW}⚠${NC}  $service 服务端口 $port 已被占用"
        echo -e "   进程信息:"
        netstat -tlnp 2>/dev/null | grep ":$port " || ss -tlnp 2>/dev/null | grep ":$port "
        return 1
    fi
    return 0
}

# 停止现有服务
stop_services() {
    echo -e "${BLUE}[清理]${NC} 停止现有服务..."
    pkill -f "python.*main.py" 2>/dev/null || true
    pkill -f "python.*mock_api_server" 2>/dev/null || true
    pkill -f "python.*websocket_server" 2>/dev/null || true
    sleep 2
    echo -e "${GREEN}✓${NC} 现有服务已停止"
}

# 启动服务
start_service() {
    local name=$1
    local command=$2
    local port=$3
    local log_file=$4
    
    echo -e "${BLUE}[启动]${NC} $name 服务..."
    
    # 检查端口
    if ! check_port $port "$name"; then
        read -p "是否强制停止并重新启动？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            lsof -ti:$port 2>/dev/null | xargs kill -9 2>/dev/null || true
            sleep 1
        else
            return 1
        fi
    fi
    
    # 创建日志目录
    mkdir -p logs
    
    # 启动服务（后台）
    nohup bash -c "$command" > "$log_file" 2>&1 &
    local pid=$!
    
    # 等待服务启动
    sleep 3
    
    # 检查服务是否启动成功
    if kill -0 $pid 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $name 服务已启动 (PID: $pid, 端口: $port)"
        echo -e "   日志文件: $log_file"
        return 0
    else
        echo -e "${RED}✗${NC} $name 服务启动失败"
        echo -e "   查看日志: cat $log_file"
        return 1
    fi
}

# 主流程
main() {
    # 选项
    SKIP_AGENT=false
    SKIP_MOCK=false
    SKIP_WS=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-agent)
                SKIP_AGENT=true
                shift
                ;;
            --skip-mock)
                SKIP_MOCK=true
                shift
                ;;
            --skip-ws)
                SKIP_WS=true
                shift
                ;;
            --help|-h)
                echo "用法: $0 [选项]"
                echo ""
                echo "选项:"
                echo "  --skip-agent   跳过智能体 API 服务"
                echo "  --skip-mock    跳过 Mock API 服务"
                echo "  --skip-ws      跳过 WebSocket 服务"
                echo "  --help, -h     显示帮助信息"
                exit 0
                ;;
            *)
                echo "未知选项: $1"
                echo "使用 --help 查看帮助信息"
                exit 1
                ;;
        esac
    done
    
    # 停止现有服务
    read -p "是否停止现有服务？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        stop_services
    fi
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # 启动智能体 API 服务器（必需）
    if [ "$SKIP_AGENT" = false ]; then
        echo -e "${BLUE}[1/3]${NC} 启动智能体 API 服务器..."
        if start_service \
            "智能体 API" \
            "python src/main.py -m http -p 5000" \
            5000 \
            "logs/agent_api.log"; then
            # 等待服务完全启动
            sleep 3
            # 测试服务
            if curl -s -f http://localhost:5000/docs > /dev/null 2>&1; then
                echo -e "${GREEN}✓${NC} 智能体 API 服务测试通过"
            else
                echo -e "${YELLOW}⚠${NC} 智能体 API 服务未响应，请检查日志"
            fi
        else
            echo -e "${RED}✗${NC} 智能体 API 服务启动失败"
            exit 1
        fi
        echo ""
    else
        echo -e "${YELLOW}[1/3]${NC} 跳过智能体 API 服务"
        echo ""
    fi
    
    # 启动 Mock API 服务器（可选）
    if [ "$SKIP_MOCK" = false ]; then
        echo -e "${BLUE}[2/3]${NC} 启动 Mock API 服务器..."
        if start_service \
            "Mock API" \
            "python3 scripts/mock_api_server.py" \
            3000 \
            "logs/mock_api.log"; then
            # 测试服务
            if curl -s -f http://localhost:3000/docs > /dev/null 2>&1; then
                echo -e "${GREEN}✓${NC} Mock API 服务测试通过"
            else
                echo -e "${YELLOW}⚠${NC} Mock API 服务未响应，请检查日志"
            fi
        fi
        echo ""
    else
        echo -e "${YELLOW}[2/3]${NC} 跳过 Mock API 服务"
        echo ""
    fi
    
    # 启动 WebSocket 服务器（可选）
    if [ "$SKIP_WS" = false ]; then
        echo -e "${BLUE}[3/3]${NC} 启动 WebSocket 服务器..."
        if start_service \
            "WebSocket" \
            "python3 src/websocket_server.py" \
            8765 \
            "logs/websocket.log"; then
            echo -e "${GREEN}✓${NC} WebSocket 服务已启动"
        fi
        echo ""
    else
        echo -e "${YELLOW}[3/3]${NC} 跳过 WebSocket 服务"
        echo ""
    fi
    
    # 显示服务状态
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${GREEN}═════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ 后端服务启动完成！${NC}"
    echo ""
    echo -e "📊 服务状态:"
    echo -e "   智能体 API:     ${GREEN}运行中${NC} (http://localhost:5000)"
    echo -e "   Mock API:       ${GREEN}运行中${NC} (http://localhost:3000)"
    echo -e "   WebSocket:      ${GREEN}运行中${NC} (ws://localhost:8765)"
    echo ""
    echo -e "📚 API 文档:"
    echo -e "   智能体: ${BLUE}http://localhost:5000/docs${NC}"
    echo -e "   Mock:   ${BLUE}http://localhost:3000/docs${NC}"
    echo ""
    echo -e "📝 日志文件:"
    echo -e "   智能体 API: ${BLUE}logs/agent_api.log${NC}"
    echo -e "   Mock API:   ${BLUE}logs/mock_api.log${NC}"
    echo -e "   WebSocket:  ${BLUE}logs/websocket.log${NC}"
    echo ""
    echo -e "🔍 查看服务状态:"
    echo -e "   ps aux | grep python"
    echo ""
    echo -e "🛑 停止所有服务:"
    echo -e "   pkill -f 'python.*main.py'"
    echo -e "   pkill -f 'python.*mock_api'"
    echo -e "   pkill -f 'python.*websocket'"
    echo ""
    echo -e "📱 前端访问: ${BLUE}http://localhost:5173${NC}"
    echo ""
}

# 运行主函数
main "$@"
