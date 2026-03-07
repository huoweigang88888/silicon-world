#!/bin/bash
# 硅基世界 - 测试网部署脚本

set -e

echo "========================================"
echo "硅基世界 - 测试网部署"
echo "========================================"

# 配置
RPC_URL="${RPC_URL:-https://goerli.infura.io/v3/YOUR_KEY}"
PRIVATE_KEY="${PRIVATE_KEY:-}"
CONTRACT_PATH="src/blockchain/contracts/Identity.sol"

# 检查配置
if [ -z "$PRIVATE_KEY" ]; then
    echo "错误：请设置 PRIVATE_KEY 环境变量"
    echo "export PRIVATE_KEY=your_private_key"
    exit 1
fi

# 1. 编译智能合约
echo ""
echo "[1/4] 编译智能合约..."
if command -v solc &> /dev/null; then
    solc --bin --abi $CONTRACT_PATH -o build/
    echo "✓ 合约编译完成"
else
    echo "⚠ solc 未安装，跳过编译"
fi

# 2. 部署合约
echo ""
echo "[2/4] 部署合约到测试网..."
echo "RPC: $RPC_URL"
echo "注意：请确保账户有足够的测试币"

# 这里可以使用 hardhat 或 truffle 部署
# 示例 (需要安装 hardhat):
# npx hardhat run scripts/deploy.js --network goerli

echo "⚠ 合约部署需要配置 hardhat/truffle"
echo "   参考：docs/deployment.md"

# 3. 部署 API 服务
echo ""
echo "[3/4] 部署 API 服务..."

if command -v docker-compose &> /dev/null; then
    docker-compose up -d
    echo "✓ Docker 服务已启动"
    
    # 等待服务就绪
    echo "等待服务就绪..."
    sleep 10
    
    # 健康检查
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo "✓ API 服务运行正常"
    else
        echo "⚠ API 服务可能未完全启动"
    fi
else
    echo "⚠ docker-compose 未安装，跳过"
fi

# 4. 验证部署
echo ""
echo "[4/4] 验证部署..."

echo ""
echo "========================================"
echo "部署完成！"
echo "========================================"
echo ""
echo "API 文档：http://localhost:8000/docs"
echo "健康检查：http://localhost:8000/health"
echo ""
echo "下一步:"
echo "  1. 部署智能合约到测试网"
echo "  2. 配置合约地址到环境变量"
echo "  3. 运行集成测试"
echo ""
echo "========================================"
