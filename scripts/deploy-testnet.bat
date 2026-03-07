@echo off
REM 硅基世界 - Windows 测试网部署脚本

echo ========================================
echo 硅基世界 - 测试网部署
echo ========================================

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：Python 未安装
    exit /b 1
)

REM 检查 Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo 警告：Docker 未安装，跳过容器部署
    goto :skip_docker
)

REM 启动数据库
echo.
echo [1/3] 启动数据库...
docker run -d ^
  -e POSTGRES_USER=postgres ^
  -e POSTGRES_PASSWORD=postgres ^
  -e POSTGRES_DB=silicon_world ^
  -p 5432:5432 ^
  --name silicon-db ^
  postgres:15

echo ✓ 数据库已启动

:skip_docker

REM 安装依赖
echo.
echo [2/3] 安装依赖...
pip install -r requirements.txt
echo ✓ 依赖安装完成

REM 初始化数据库
echo.
echo [3/3] 初始化数据库...
python -c "from src.core.database import init_db; init_db()"
echo ✓ 数据库初始化完成

REM 启动 API
echo.
echo ========================================
echo 部署完成！
echo ========================================
echo.
echo API 文档：http://localhost:8000/docs
echo.
echo 启动 API 服务:
echo   uvicorn src.api.main:app --reload
echo.
echo ========================================

pause
