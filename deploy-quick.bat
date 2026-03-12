@echo off
chcp 65001 >nul
echo ========================================
echo 硅基世界 Sepolia 测试网部署
echo ========================================
echo.

cd /d "%~dp0contracts"

echo [1/4] 检查环境...
node --version
npm --version
echo.

echo [2/4] 编译合约...
npx hardhat compile
if errorlevel 1 (
    echo ❌ 合约编译失败！
    pause
    exit /b 1
)
echo ✅ 合约编译完成
echo.

echo [3/4] 部署合约到 Sepolia...
node scripts\deploy-testnet.js
if errorlevel 1 (
    echo ❌ 合约部署失败！
    echo 请检查:
    echo   1. .env 配置是否正确
    echo   2. 账户是否有足够的 Sepolia ETH
    echo   3. RPC URL 是否可用
    pause
    exit /b 1
)
echo.

echo [4/4] 部署完成！
echo.
echo ========================================
echo ✅ 部署成功！
echo ========================================
echo.
echo 合约地址已保存到:
echo   contracts\deployments\sepolia-latest.json
echo.
echo 下一步:
echo   1. 更新前端合约地址
echo   2. 验证合约 (可选)
echo   3. 测试功能
echo.

pause
