#!/bin/bash

# 硅基世界 - 开发环境快速启动脚本
# 使用：./start-dev.sh

echo "🚀 硅基世界 - 开发环境启动中..."
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python 3"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 错误：未找到 Node.js"
    exit 1
fi

# 进入项目目录
cd "$(dirname "$0")"

echo "✅ 环境检查通过"
echo ""

# 启动 API 服务
echo "📡 启动 API 服务..."
cd silicon-world
python3 -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000 &
API_PID=$!
echo "✅ API 服务已启动 (PID: $API_PID)"
echo "   访问：http://localhost:8000"
echo "   API 文档：http://localhost:8000/docs"
echo ""

# 启动 Dashboard
echo "🖥️  启动 Dashboard..."
cd web/dashboard
python3 -m http.server 3000 &
DASHBOARD_PID=$!
echo "✅ Dashboard 已启动 (PID: $DASHBOARD_PID)"
echo "   访问：http://localhost:3000"
echo ""

# 启动 NFT 市场
echo "🎨 启动 NFT 市场..."
cd ../marketplace
python3 -m http.server 3001 &
MARKET_PID=$!
echo "✅ NFT 市场已启动 (PID: $MARKET_PID)"
echo "   访问：http://localhost:3001"
echo ""

echo "============================================================"
echo "✅ 所有服务已启动！"
echo "============================================================"
echo ""
echo "📊 服务列表:"
echo "   API 服务：     http://localhost:8000"
echo "   Dashboard:     http://localhost:3000"
echo "   NFT 市场：     http://localhost:3001"
echo "   API 文档：     http://localhost:8000/docs"
echo ""
echo "🛑 停止服务：按 Ctrl+C 或运行 ./stop-dev.sh"
echo ""
echo "🐾 硅基世界，由你我共同创造！"
echo ""

# 等待进程
wait
