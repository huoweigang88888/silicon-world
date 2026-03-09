@echo off
REM 硅基世界 - Windows 快速部署脚本

echo ========================================
echo   硅基世界 Silicon World
echo   快速部署脚本
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)
echo [OK] Python 已安装

REM 检查依赖
echo.
echo [信息] 检查并安装依赖...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [警告] 部分依赖安装失败，但可能不影响运行
)

REM 初始化数据库
echo.
echo [信息] 初始化数据库...
python scripts\migrate_db.py
python scripts\migrate_social.py

REM 启动 API 服务
echo.
echo ========================================
echo   启动 API 服务...
echo   访问地址：http://localhost:8000
echo   API 文档：http://localhost:8000/docs
echo ========================================
echo.

start uvicorn src.api.main:app --host 0.0.0.0 --port 8000

REM 等待 3 秒
timeout /t 3 /nobreak >nul

REM 启动 Dashboard
echo.
echo ========================================
echo   启动 Dashboard...
echo   访问地址：http://localhost:3000
echo ========================================
echo.

cd web\dashboard
start python -m http.server 3000
cd ..\..

REM 打开浏览器
echo.
echo [信息] 打开浏览器...
timeout /t 2 /nobreak >nul
start http://localhost:3000

echo.
echo ========================================
echo   部署完成！
echo   
echo   API 服务：http://localhost:8000
echo   Dashboard: http://localhost:3000
echo   API 文档：http://localhost:8000/docs
echo   
echo   按 Ctrl+C 停止服务
echo ========================================
echo.

pause
