@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 魔法课桌学习助手 - 前端开发环境快速启动脚本 (Windows)

echo ╔═════════════════════════════════════════════════════════╗
echo ║      魔法课桌学习助手 - 前端开发环境启动              ║
echo ╚═════════════════════════════════════════════════════════╝
echo.

REM 项目根目录
set "PROJECT_ROOT=%~dp0.."
set "FRONTEND_DIR=%PROJECT_ROOT%\magic-school-frontend"

REM 检查 Node.js
echo [1/5] 检查 Node.js 环境...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到 Node.js，请先安装 Node.js
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node -v') do set NODE_VERSION=%%i
echo ✓ Node.js 版本: %NODE_VERSION%

REM 检查 npm
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到 npm
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('npm -v') do set NPM_VERSION=%%i
echo ✓ npm 版本: %NPM_VERSION%

REM 安装前端依赖
echo.
echo [2/5] 检查前端依赖...
cd /d "%FRONTEND_DIR%"

if not exist "node_modules" (
    echo 首次运行，正在安装前端依赖...
    call npm install
    echo ✓ 前端依赖安装完成
) else (
    echo ✓ 前端依赖已存在
)

REM 检查 Python
echo.
echo [3/5] 检查 Python 环境...
where python >nul 2>&1
if %errorlevel% neq 0 (
    where py >nul 2>&1
    if %errorlevel% neq 0 (
        echo 警告: 未找到 Python，Mock API 服务器将无法启动
        echo 你可以只启动前端服务器进行静态页面调试
        echo.
        echo 是否继续？ (Y/N)
        set /p choice=
        if /i not "!choice!"=="Y" (
            pause
            exit /b 1
        )
        goto START_FRONTEND_ONLY
    )
    set PYTHON_CMD=py
) else (
    set PYTHON_CMD=python
)

REM 安装 Python 依赖
echo.
echo [4/5] 检查 Python 依赖...
cd /d "%PROJECT_ROOT%"
"%PYTHON_CMD%" -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装 Python 依赖...
    pip install -q fastapi uvicorn pydantic python-jose[cryptography]
    echo ✓ Python 依赖安装完成
) else (
    echo ✓ Python 依赖已存在
)

REM 启动服务
echo.
echo [5/5] 启动服务...
echo.
echo ========================================
echo   🚀 启动前端开发服务器
echo   📡 启动 Mock API 服务器
echo ========================================
echo.
echo 📍 前端地址: http://localhost:5173
echo 📍 API 地址: http://localhost:3000
echo 📍 API 文档: http://localhost:3000/docs
echo.
echo 📝 测试账号:
echo    学生: student / password123
echo    家长: parent / password123
echo.
echo 按 Ctrl+C 停止所有服务
echo.

REM 创建日志目录
if not exist "%PROJECT_ROOT%\logs" mkdir "%PROJECT_ROOT%\logs"

REM 启动 Mock API 服务器（后台）
echo 启动 Mock API 服务器...
cd /d "%PROJECT_ROOT%"
start /B "" "%PYTHON_CMD%" scripts\mock_api_server.py > "%PROJECT_ROOT%\logs\mock_api.log" 2>&1

REM 等待 API 服务器启动
timeout /t 2 /nobreak >nul

REM 启动前端开发服务器（前台）
echo 启动前端开发服务器...
cd /d "%FRONTEND_DIR%"
call npm run dev

REM 清理（当用户按 Ctrl+C 时）
REM Windows 会自动关闭后台进程

:START_FRONTEND_ONLY
echo.
echo [4/4] 启动前端服务器（仅前端）...
echo.
echo ========================================
echo   🚀 启动前端开发服务器
echo ========================================
echo.
echo 📍 前端地址: http://localhost:5173
echo.
echo 注意: Mock API 服务器未启动，部分功能可能无法正常使用
echo.
echo 按 Ctrl+C 停止服务
echo.

cd /d "%FRONTEND_DIR%"
call npm run dev

pause
