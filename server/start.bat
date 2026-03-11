@echo off
echo ============================================================
echo 硅基世界 - 后端服务启动
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/3] 检查 Python 环境...
python --version
if errorlevel 1 (
    echo ❌ Python 未安装或不在 PATH 中
    pause
    exit /b 1
)
echo ✅ Python 环境正常
echo.

echo [2/3] 安装依赖...
pip install -r requirements.txt -q
echo ✅ 依赖安装完成
echo.

echo [3/3] 启动 FastAPI 服务器...
echo.
echo 🌐 API 文档：http://localhost:8000/docs
echo 🏠 API 根路径：http://localhost:8000
echo 📊 健康检查：http://localhost:8000/api/health
echo.
echo 按 Ctrl+C 停止服务器
echo ============================================================
echo.

python main.py

pause
