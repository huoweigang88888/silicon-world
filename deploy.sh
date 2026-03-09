#!/bin/bash
# 硅基世界 - Linux/Mac 快速部署脚本

echo "========================================"
echo "  硅基世界 Silicon World"
echo "  快速部署脚本"
echo "========================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python3，请先安装 Python 3.10+"
    exit 1
fi
echo "[OK] Python 已安装：$(python3 --version)"

# 检查依赖
echo ""
echo "[信息] 检查并安装依赖..."
pip3 install -r requirements.txt -q
if [ $? -ne 0 ]; then
    echo "[警告] 部分依赖安装失败，但可能不影响运行"
fi

# 初始化数据库
echo ""
echo "[信息] 初始化数据库..."
python3 scripts/migrate_db.py
python3 scripts/migrate_social.py

# 启动 API 服务
echo ""
echo "========================================"
echo "  启动 API 服务..."
echo "  访问地址：http://localhost:8000"
echo "  API 文档：http://localhost:8000/docs"
echo "========================================"
echo ""

uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# 等待 3 秒
sleep 3

# 启动 Dashboard
echo ""
echo "========================================"
echo "  启动 Dashboard..."
echo "  访问地址：http://localhost:3000"
echo "========================================"
echo ""

cd web/dashboard
python3 -m http.server 3000 &
DASHBOARD_PID=$!
cd ../..

# 打开浏览器
echo ""
echo "[信息] 服务已启动"
sleep 2

# 尝试打开浏览器
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000
elif command -v open &> /dev/null; then
    open http://localhost:3000
fi

echo ""
echo "========================================"
echo "  部署完成！"
echo ""
echo "  API 服务：http://localhost:8000 (PID: $API_PID)"
echo "  Dashboard: http://localhost:3000 (PID: $DASHBOARD_PID)"
echo "  API 文档：http://localhost:8000/docs"
echo ""
echo "  按 Ctrl+C 停止服务"
echo "========================================"
echo ""

# 等待进程
wait
