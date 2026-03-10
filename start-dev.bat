@echo off
REM 硅基世界 - Windows 开发环境快速启动脚本
REM 使用：start-dev.bat

echo 🚀 硅基世界 - 开发环境启动中...
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到 Python
    pause
    exit /b 1
)

REM 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到 Node.js
    pause
    exit /b 1
)

echo ✅ 环境检查通过
echo.

REM 启动 API 服务
echo 📡 启动 API 服务...
start "硅基世界 API" cmd /k "cd silicon-world && uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000"
echo ✅ API 服务已启动
echo    访问：http://localhost:8000
echo    API 文档：http://localhost:8000/docs
echo.

REM 启动 Dashboard
echo 🖥️  启动 Dashboard...
start "硅基世界 Dashboard" cmd /k "cd web/dashboard && python -m http.server 3000"
echo ✅ Dashboard 已启动
echo    访问：http://localhost:3000
echo.

REM 启动 NFT 市场
echo 🎨 启动 NFT 市场...
start "硅基世界 NFT 市场" cmd /k "cd web/marketplace && python -m http.server 3001"
echo ✅ NFT 市场已启动
echo    访问：http://localhost:3001
echo.

echo ============================================================
echo ✅ 所有服务已启动！
echo ============================================================
echo.
echo 📊 服务列表:
echo    API 服务：     http://localhost:8000
echo    Dashboard:     http://localhost:3000
echo    NFT 市场：     http://localhost:3001
echo    API 文档：     http://localhost:8000/docs
echo.
echo 🛑 停止服务：关闭所有打开的命令行窗口
echo.
echo 🐾 硅基世界，由你我共同创造！
echo.

pause
