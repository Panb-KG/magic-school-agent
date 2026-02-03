@echo off
REM 魔法课桌智能体 - 一键启动所有后端服务 (Windows)

echo ╔═════════════════════════════════════════════════════════╗
echo ║      魔法课桌智能体 - 后端服务一键启动                  ║
echo ╚═════════════════════════════════════════════════════════╝
echo.

set PROJECT_ROOT=%~dp0..
cd /d "%PROJECT_ROOT%"

REM 检查端口占用
:check_port
setlocal
set PORT=%1
set SERVICE=%2
netstat -ano | findstr ":%PORT% " >nul 2>&1
if %errorlevel% equ 0 (
    echo [警告] %SERVICE% 服务端口 %PORT% 已被占用
    echo    进程信息:
    netstat -ano | findstr ":%PORT% "
    endlocal
    exit /b 1
)
endlocal
exit /b 0

REM 停止现有服务
:stop_services
echo [清理] 停止现有服务...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *main.py*" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *mock_api*" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *websocket*" >nul 2>&1
timeout /t 2 >nul
echo [OK] 现有服务已停止
goto :eof

REM 主流程
set SKIP_AGENT=0
set SKIP_MOCK=0
set SKIP_WS=0

REM 解析参数
:parse_args
if "%1"=="--skip-agent" (
    set SKIP_AGENT=1
    shift
    goto parse_args
)
if "%1"=="--skip-mock" (
    set SKIP_MOCK=1
    shift
    goto parse_args
)
if "%1"=="--skip-ws" (
    set SKIP_WS=1
    shift
    goto parse_args
)
if "%1"=="--help" goto help
if "%1"=="-h" goto help
shift
if not "%1"=="" goto parse_args
goto main

:help
echo 用法: %~nx0 [选项]
echo.
echo 选项:
echo   --skip-agent   跳过智能体 API 服务
echo   --skip-mock    跳过 Mock API 服务
echo   --skip-ws      跳过 WebSocket 服务
echo   --help, -h     显示帮助信息
goto :eof

:main
REM 询问是否停止现有服务
set /p STOP_SERVICES="是否停止现有服务？(y/n) "
if /i "%STOP_SERVICES%"=="y" (
    call :stop_services
)

echo.
echo ══════════════════════════════════════════════════════════
echo.

REM 启动智能体 API 服务器
if %SKIP_AGENT%==0 (
    echo [1/3] 启动智能体 API 服务器...
    
    REM 检查端口
    call :check_port 5000 "智能体 API"
    if %errorlevel% equ 1 (
        set /p FORCE_START="是否强制停止并重新启动？(y/n) "
        if /i "!FORCE_START!"=="y" (
            for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000 "') do taskkill /F /PID %%a >nul 2>&1
            timeout /t 1 >nul
        ) else (
            goto :skip_agent
        )
    )
    
    REM 启动服务
    start "Magic School Agent API" python src/main.py -m http -p 5000
    
    echo [OK] 智能体 API 服务已启动 (端口 5000)
    echo.
    timeout /t 3 >nul
) else (
    echo [1/3] 跳过智能体 API 服务
    echo.
)

:skip_agent

REM 启动 Mock API 服务器
if %SKIP_MOCK%==0 (
    echo [2/3] 启动 Mock API 服务器...
    
    call :check_port 3000 "Mock API"
    if %errorlevel% equ 1 (
        set /p FORCE_START="是否强制停止并重新启动？(y/n) "
        if /i "!FORCE_START!"=="y" (
            for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000 "') do taskkill /F /PID %%a >nul 2>&1
            timeout /t 1 >nul
        ) else (
            goto :skip_mock
        )
    )
    
    start "Magic School Mock API" python scripts/mock_api_server.py
    
    echo [OK] Mock API 服务已启动 (端口 3000)
    echo.
) else (
    echo [2/3] 跳过 Mock API 服务
    echo.
)

:skip_mock

REM 启动 WebSocket 服务器
if %SKIP_WS%==0 (
    echo [3/3] 启动 WebSocket 服务器...
    
    call :check_port 8765 "WebSocket"
    if %errorlevel% equ 1 (
        set /p FORCE_START="是否强制停止并重新启动？(y/n) "
        if /i "!FORCE_START!"=="y" (
            for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8765 "') do taskkill /F /PID %%a >nul 2>&1
            timeout /t 1 >nul
        ) else (
            goto :skip_ws
        )
    )
    
    start "Magic School WebSocket" python src/websocket_server.py
    
    echo [OK] WebSocket 服务已启动 (端口 8765)
    echo.
) else (
    echo [3/3] 跳过 WebSocket 服务
    echo.
)

:skip_ws

echo ══════════════════════════════════════════════════════════
echo.
echo ══════════════════════════════════════════════════════════
echo [OK] 后端服务启动完成！
echo.
echo 📊 服务状态:
echo    智能体 API:     运行中 (http://localhost:5000)
echo    Mock API:       运行中 (http://localhost:3000)
echo    WebSocket:      运行中 (ws://localhost:8765)
echo.
echo 📚 API 文档:
echo    智能体: http://localhost:5000/docs
echo    Mock:   http://localhost:3000/docs
echo.
echo 🔍 查看服务状态:
echo    tasklist | findstr python
echo.
echo 🛑 停止所有服务:
echo    taskkill /F /IM python.exe /FI "WINDOWTITLE eq *Magic School*"
echo.
echo 📱 前端访问: http://localhost:5173
echo.

pause
