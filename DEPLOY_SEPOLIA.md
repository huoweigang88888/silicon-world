# 硅基世界 Sepolia 测试网部署指南

**版本**: v2.0.0  
**日期**: 2026-03-12  
**目标网络**: Sepolia Testnet (Goerli 已废弃)

---

## 📋 部署清单

### 前置准备

- [ ] MetaMask 钱包安装
- [ ] 获取 Sepolia ETH (水龙头)
- [ ] Etherscan API Key
- [ ] Alchemy/Infura RPC URL

### 部署步骤

1. [ ] 配置环境变量
2. [ ] 安装依赖
3. [ ] 编译合约
4. [ ] 部署合约到 Sepolia
5. [ ] 验证合约
6. [ ] 配置后端
7. [ ] 测试连接

---

## 1️⃣ 获取 Sepolia ETH

### 水龙头链接

1. **Alchemy 水龙头**: https://sepoliafaucet.com/
2. **Infura 水龙头**: https://www.infura.io/faucet/sepolia
3. **Google Cloud 水龙头**: https://cloud.google.com/application/web3/faucet/ethereum/sepolia

```bash
# 检查余额 (需要安装 foundry)
cast balance <YOUR_ADDRESS> --rpc-url https://sepolia.infura.io/v3/<API_KEY>
```

---

## 2️⃣ 配置环境变量

### 创建 .env 文件

```bash
cd C:\Users\zzz\.openclaw\workspace\silicon-world
cp .env.example .env
```

### 编辑 .env

```env
# Sepolia 网络配置
SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_ALCHEMY_KEY
SEPOLIA_CHAIN_ID=11155111

# Etherscan (用于合约验证)
ETHERSCAN_API_KEY=YOUR_ETHERSCAN_API_KEY

# 部署者钱包 (不要提交到 Git!)
DEPLOYER_PRIVATE_KEY=0x_your_private_key_here

# 代币配置
INITIAL_SUPPLY=1000000
TOKEN_NAME="Silicon World Token"
TOKEN_SYMBOL="SWT"

# NexusA 配置
NEXUSA_CONTRACT_ADDRESS=
NEXUSA_API_URL=https://api.nexusa.io
```

---

## 3️⃣ 安装依赖

```bash
# 进入合约目录
cd contracts

# 安装依赖
npm install

# 安装 Hardhat 工具
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
```

---

## 4️⃣ 编译合约

```bash
# 编译所有合约
npx hardhat compile

# 预期输出:
# Compiled X Solidity files successfully
```

---

## 5️⃣ 部署到 Sepolia

### 方式 1: 使用部署脚本

```bash
# 更新部署脚本网络为 sepolia
# 然后运行:
node scripts/deploy-testnet.js

# 或使用 npx
npx hardhat run scripts/deploy-testnet.js --network sepolia
```

### 方式 2: 手动部署

```bash
# 启动 Hardhat 控制台
npx hardhat console --network sepolia

# 在控制台中:
const [deployer] = await ethers.getSigners();
console.log("Deploying with account:", deployer.address);

// 部署代币
const Token = await ethers.getContractFactory("SiliconWorldToken");
const token = await Token.deploy(ethers.utils.parseEther("1000000"), "Silicon World Token", "SWT");
await token.deployed();
console.log("Token deployed to:", token.address);
```

---

## 6️⃣ 验证合约

```bash
# 自动验证所有合约
npx hardhat verify --network sepolia <CONTRACT_ADDRESS> <CONSTRUCTOR_ARGS>

# 示例: 验证代币合约
npx hardhat verify --network sepolia 0xYourTokenAddress 1000000 "Silicon World Token" "SWT"
```

---

## 7️⃣ 配置后端

### 更新后端配置

编辑 `server/main.py`:

```python
# NexusA 配置
nexusa_config = NexusaConfig.from_network("sepolia")
nexusa_config.rpc_url = "https://eth-sepolia.g.alchemy.com/v2/YOUR_KEY"
```

### 更新前端配置

编辑 `web/js/nexusa-connector.js`:

```javascript
const config = {
    network: 'sepolia',
    chainId: 11155111,
    rpcUrl: 'https://eth-sepolia.g.alchemy.com/v2/YOUR_KEY'
};
```

---

## 8️⃣ 测试连接

### 测试合约调用

```bash
# 使用 cast (foundry)
cast call <CONTRACT_ADDRESS> "name()" --rpc-url https://sepolia.infura.io/v3/<KEY>

# 应返回："Silicon World Token"
```

### 测试前端连接

1. 打开 `web/economy.html`
2. 点击"连接钱包"
3. 切换 MetaMask 到 Sepolia 网络
4. 检查控制台日志

---

## 📊 部署检查表

| 步骤 | 状态 | 备注 |
|------|------|------|
| 获取 Sepolia ETH | ⏳ 待执行 | 从水龙头 |
| 配置 .env | ⏳ 待执行 | 填写 RPC 和私钥 |
| 安装依赖 | ⏳ 待执行 | npm install |
| 编译合约 | ⏳ 待执行 | npx hardhat compile |
| 部署合约 | ⏳ 待执行 | 4 个合约 |
| 验证合约 | ⏳ 待执行 | Etherscan |
| 配置后端 | ⏳ 待执行 | 更新 RPC |
| 测试连接 | ⏳ 待执行 | 端到端测试 |

---

## 🔧 常见问题

### 1. Gas 费用过高

```bash
# 设置 Gas 价格
export HARDHAT_NETWORK=sepolia
export HARDHAT_GAS_PRICE=20000000000  # 20 Gwei
```

### 2. 部署失败

检查:
- 私钥格式正确 (0x 开头)
- 账户有足够 ETH
- RPC URL 正确

### 3. 验证失败

- 等待区块确认 (约 30 秒)
- 检查 Etherscan API Key
- 确认构造函数参数正确

---

## 📝 部署后任务

1. **更新文档** - 记录合约地址
2. **配置前端** - 更新合约地址
3. **通知测试用户** - 准备测试
4. **监控** - 设置告警

---

_最后更新：2026-03-12_
