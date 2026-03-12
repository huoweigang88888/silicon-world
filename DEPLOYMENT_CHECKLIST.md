# 硅基世界部署检查清单

**日期**: 2026-03-12  
**目标**: Sepolia 测试网部署  
**状态**: 准备就绪 ✅

---

## ✅ 已完成准备

- [x] 智能合约编译完成
- [x] 部署脚本更新 (Goerli → Sepolia)
- [x] Hardhat 配置完成
- [x] .env 配置文件 (RPC URL 已填写)
- [x] 部署文档创建

---

## 📋 部署步骤

### 步骤 1: 确认环境

```bash
cd C:\Users\zzz\.openclaw\workspace\silicon-world\contracts

# 检查 Node.js 版本
node --version  # 应该 >= 18

# 检查依赖
npm list hardhat  # 应该显示已安装
```

### 步骤 2: 编译合约

```bash
# 编译所有合约
npx hardhat compile

# 预期输出:
# Compiled X Solidity files successfully
```

### 步骤 3: 检查账户余额

```bash
# 使用 cast 检查 (需要安装 foundry)
cast balance 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 --rpc-url https://eth-sepolia.g.alchemy.com/v2/AP6EAjqS9hYALHJAFuk1K

# 或使用 web3 检查
npx hardhat console --network sepolia
> const [signer] = await ethers.getSigners()
> await ethers.provider.getBalance(signer.address)
```

### 步骤 4: 部署合约

```bash
# 部署到 Sepolia
node scripts/deploy-testnet.js

# 或
npx hardhat run scripts/deploy-testnet.js --network sepolia
```

### 步骤 5: 验证合约 (可选)

```bash
# 验证代币合约
npx hardhat verify --network sepolia <TOKEN_ADDRESS> 1000000000000000000000000 "Silicon World Token" "SWT"
```

### 步骤 6: 记录合约地址

部署成功后，合约地址会保存在:
- `contracts/deployments/sepolia-latest.json`
- 控制台输出

### 步骤 7: 更新前端配置

编辑以下文件，填入部署的合约地址:

1. `web/js/contracts.js` - 前端合约地址
2. `server/main.py` - 后端合约配置
3. `web/economy.html` - 钱包连接配置

### 步骤 8: 测试

1. 打开 `web/world.html` - 检查主世界
2. 打开 `web/economy.html` - 连接钱包
3. 打开 `web/marketplace.html` - 查看 NFT

---

## 🔧 快速部署脚本

创建 `deploy-quick.bat` (Windows):

```batch
@echo off
echo ========================================
echo 硅基世界 Sepolia 部署
echo ========================================

cd /d "%~dp0contracts"

echo.
echo [1/4] 检查环境...
node --version
npm --version

echo.
echo [2/4] 编译合约...
npx hardhat compile

echo.
echo [3/4] 部署合约...
node scripts\deploy-testnet.js

echo.
echo [4/4] 完成！
echo 查看部署信息：contracts\deployments\sepolia-latest.json
echo.

pause
```

---

## 📊 部署状态追踪

| 步骤 | 状态 | 时间 | 备注 |
|------|------|------|------|
| 环境检查 | ⏳ 待执行 | - | - |
| 合约编译 | ⏳ 待执行 | - | - |
| 余额检查 | ⏳ 待执行 | - | 需要 Sepolia ETH |
| 合约部署 | ⏳ 待执行 | - | 4 个合约 |
| 合约验证 | ⏳ 待执行 | - | Etherscan |
| 前端配置 | ⏳ 待执行 | - | 更新合约地址 |
| 功能测试 | ⏳ 待执行 | - | 端到端测试 |

---

## 🎯 部署后任务

1. **GitHub 更新** - 提交部署信息
2. **文档更新** - 记录合约地址
3. **测试用户通知** - 准备测试
4. **监控设置** - 合约监控

---

## 📞 获取帮助

遇到问题？

1. 检查 `.env` 配置
2. 查看 Hardhat 错误日志
3. 检查 Etherscan Gas Tracker
4. 参考文档：`docs/DEPLOYMENT_TESTNET.md`

---

_准备就绪，等待执行部署命令_
