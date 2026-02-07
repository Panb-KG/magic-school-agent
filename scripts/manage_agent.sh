#!/bin/bash

# 魔法课桌智能体 - 启动脚本

PROJECT_DIR="/workspace/projects"
AGENT_PORT=5000
LOG_FILE="/var/log/magic-school-agent.log"
PID_FILE="/var/run/magic-school-agent.pid"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "魔法课桌智能体 - 服务管理"
echo "=========================================="
echo ""

case "$1" in
    start)
        echo "🚀 启动魔法课桌智能体服务..."

        # 检查是否已运行
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p $PID > /dev/null 2>&1; then
                echo -e "${YELLOW}⚠️  服务已在运行 (PID: $PID)${NC}"
                exit 1
            else
                rm -f "$PID_FILE"
            fi
        fi

        # 创建日志目录
        mkdir -p "$(dirname "$LOG_FILE")"

        # 启动服务
        cd "$PROJECT_DIR"
        nohup python3 src/main.py -m http -p $AGENT_PORT >> "$LOG_FILE" 2>&1 &
        PID=$!

        # 保存PID
        echo $PID > "$PID_FILE"

        # 等待服务启动
        sleep 3

        # 检查服务是否成功启动
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 服务启动成功 (PID: $PID)${NC}"
            echo "📝 日志文件: $LOG_FILE"
            echo "🌐 服务地址: http://localhost:$AGENT_PORT"
            echo ""
            echo "查看日志: tail -f $LOG_FILE"
            echo "停止服务: $0 stop"
            echo "查看状态: $0 status"
        else
            echo -e "${RED}❌ 服务启动失败${NC}"
            echo "查看日志: cat $LOG_FILE"
            rm -f "$PID_FILE"
            exit 1
        fi
        ;;

    stop)
        echo "🛑 停止魔法课桌智能体服务..."

        if [ ! -f "$PID_FILE" ]; then
            echo -e "${YELLOW}⚠️  服务未运行${NC}"
            exit 1
        fi

        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID
            sleep 2

            # 如果进程仍在运行，强制终止
            if ps -p $PID > /dev/null 2>&1; then
                kill -9 $PID
            fi

            rm -f "$PID_FILE"
            echo -e "${GREEN}✅ 服务已停止${NC}"
        else
            echo -e "${YELLOW}⚠️  进程不存在，清理PID文件${NC}"
            rm -f "$PID_FILE"
        fi
        ;;

    restart)
        echo "🔄 重启魔法课桌智能体服务..."
        $0 stop
        sleep 2
        $0 start
        ;;

    status)
        echo "📊 服务状态检查..."
        echo ""

        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p $PID > /dev/null 2>&1; then
                echo -e "${GREEN}✅ 服务正在运行${NC}"
                echo "PID: $PID"
                echo "端口: $AGENT_PORT"
                echo ""

                # 检查端口监听
                if netstat -tuln 2>/dev/null | grep -q ":$AGENT_PORT "; then
                    echo -e "${GREEN}✅ 端口 $AGENT_PORT 正在监听${NC}"
                else
                    echo -e "${RED}❌ 端口 $AGENT_PORT 未监听${NC}"
                fi

                # 检查健康状态
                echo ""
                echo "健康检查:"
                HEALTH_CHECK=$(curl -s http://localhost:$AGENT_PORT/health 2>/dev/null)
                if [ -n "$HEALTH_CHECK" ]; then
                    echo -e "${GREEN}✅ 服务健康${NC}"
                    echo "响应: $HEALTH_CHECK"
                else
                    echo -e "${RED}❌ 服务不健康${NC}"
                fi
            else
                echo -e "${RED}❌ 服务未运行（PID文件存在但进程不存在）${NC}"
                rm -f "$PID_FILE"
            fi
        else
            echo -e "${YELLOW}⚠️  服务未运行${NC}"
        fi
        ;;

    logs)
        echo "📝 查看服务日志 (最近50行):"
        echo ""
        if [ -f "$LOG_FILE" ]; then
            tail -50 "$LOG_FILE"
        else
            echo "日志文件不存在: $LOG_FILE"
        fi
        ;;

    monitor)
        echo "📡 监控服务日志 (Ctrl+C 退出):"
        echo ""
        tail -f "$LOG_FILE"
        ;;

    *)
        echo "使用方法: $0 {start|stop|restart|status|logs|monitor}"
        echo ""
        echo "命令说明:"
        echo "  start    - 启动服务"
        echo "  stop     - 停止服务"
        echo "  restart  - 重启服务"
        echo "  status   - 查看服务状态"
        echo "  logs     - 查看日志"
        echo "  monitor  - 实时监控日志"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
