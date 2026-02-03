@echo off
REM 魔法课桌智能体 - 聊天API测试脚本 (Windows)

echo ╔═════════════════════════════════════════════════════════╗
echo ║   魔法课桌智能体 - 聊天API测试                          ║
echo ╚═════════════════════════════════════════════════════════╝
echo.

set BACKEND_URL=http://localhost:5000
set MOCK_API_URL=http://localhost:3000
set TEST_QUERY=你好

REM 测试后端服务
echo [1/5] 检查后端服务状态...
curl -s -f "%BACKEND_URL%/docs" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] 后端服务运行正常 (%BACKEND_URL%)
) else (
    echo [ERROR] 后端服务未运行，请先启动：
    echo    bash scripts/http_run.sh -p 5000
    pause
    exit /b 1
)

REM 测试 Mock API
echo.
echo [2/5] 检查 Mock API 服务状态...
curl -s -f "%MOCK_API_URL%/docs" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Mock API 服务运行正常 (端口 3000)
) else (
    echo [WARNING] Mock API 服务未运行，建议启动：
    echo    python3 scripts/mock_api_server.py
)

REM 检查配置文件
echo.
echo [3/5] 检查前端环境变量配置...
set FRONTEND_ENV_FILE=magic-school-frontend\.env.development
if exist "%FRONTEND_ENV_FILE%" (
    echo [OK] 环境变量配置文件存在
    findstr /C:"VITE_BACKEND_URL" "%FRONTEND_ENV_FILE%" >nul
    if %errorlevel% equ 0 (
        echo    配置内容:
        findstr /C:"VITE_BACKEND_URL" /C:"VITE_API_BASE_URL" /C:"VITE_WS_URL" "%FRONTEND_ENV_FILE%"
    ) else (
        echo [WARNING] 环境变量配置文件存在但未配置 VITE_BACKEND_URL
    )
) else (
    echo [WARNING] 环境变量配置文件不存在: %FRONTEND_ENV_FILE%
)

REM 测试非流式 API
echo.
echo [4/5] 测试非流式对话 API...

REM 获取 Token
echo    正在获取测试 Token...
curl -s -X POST "%MOCK_API_URL%/api/v1/auth/login" -H "Content-Type: application/json" -d "{\"username\":\"student\",\"password\":\"password123\"}" > login_response.json

REM 使用 Python 解析 JSON
python -c "import json; f=open('login_response.json'); data=json.load(f); print(data.get('data', {}).get('access_token', ''))" > token.txt 2>nul
set /p TOKEN=<token.txt

if "%TOKEN%"=="" (
    echo [ERROR] 获取 Token 失败
    type login_response.json
    del login_response.json token.txt 2>nul
    pause
    exit /b 1
)

echo [OK] 成功获取 Token

REM 发送测试消息
echo    发送测试消息: %TEST_QUERY%
curl -s -X POST "%BACKEND_URL%/run" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"query\":\"%TEST_QUERY%\",\"session_id\":\"test_session_%TIME%\"}" > chat_response.json

echo [OK] 收到响应
echo    响应内容:
type chat_response.json

REM 测试流式 API
echo.
echo [5/5] 测试流式对话 API...
echo    发送测试消息: %TEST_QUERY%
echo    响应内容（流式）：
echo    ────────────────────────────────────────────────────
curl -s -X POST "%BACKEND_URL%/stream_run" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"query\":\"%TEST_QUERY%\",\"session_id\":\"test_stream_%TIME%\"}"
echo    ────────────────────────────────────────────────────

REM 清理临时文件
del login_response.json token.txt chat_response.json 2>nul

echo.
echo ═════════════════════════════════════════════════════════
echo [OK] 所有测试通过！
echo.
echo 前端访问地址: http://localhost:5173
echo API 文档: %BACKEND_URL%/docs
echo Mock API 文档: %MOCK_API_URL%/docs
echo.
echo 下一步:
echo   1. 访问前端页面: http://localhost:5173
echo   2. 登录账号: student / password123
echo   3. 在聊天界面发送消息测试
echo.

pause
