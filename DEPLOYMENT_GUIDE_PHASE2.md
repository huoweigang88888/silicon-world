# 🚀 硅基世界 Phase 2 部署指南

_版本：1.0_  
_更新时间：2026-03-10_  
_阶段：Phase 2 - 区块链集成_

---

## 📋 部署前准备

### 1. 环境要求

**系统**:
- Node.js 18+
- npm 或 yarn
- Git

**账户**:
- [ ] Infura 账号 (获取 RPC URL)
- [ ] Etherscan 账号 (获取 API Key)
- [ ] Goerli 测试 ETH (从水龙头获取)

### 2. 安装依赖

```bash
cd silicon-world/contracts
npm install
```

### 3. 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件
nano .env
```

**必填配置**:
```bash
# Infura RPC URL
GOERLI_RPC_URL=https://goerli.infura.io/v3/YOUR_INFURA_KEY

# 部署者私钥 (测试网)
PRIVATE_KEY=0x...

# Etherscan API Key
ETHERSCAN_API_KEY=YourEtherscanAPIKey
```

### 4. 获取测试 ETH

**Goerli 水龙头**:
- https://goerlifaucet.com/
- https://faucets.chain.link/goerli
- https://www.alchemy.com/faucets/ethereum-goerli

---

## 🎯 部署步骤

### 步骤 1: 编译合约

```bash
cd silicon-world/contracts
npx hardhat compile
```

**预期输出**:
```
Compiled 19 Solidity files successfully
```

### 步骤 2: 运行测试

```bash
npx hardhat test
```

**预期输出**:
```
SiliconWorldNFT
  Deployment
    ✔ Should set the correct owner
    ✔ Should have correct royalty receiver
    ✔ Should have 5% royalty
  Minting
    ✔ Should mint a new NFT
    ✔ Should track total supply
    ✔ Should only allow owner to mint
  Royalty
    ✔ Should calculate royalty correctly
    ✔ Should allow owner to update royalty
    ✔ Should not allow royalty > 10%

SiliconWorldMarketplace
  Deployment
    ✔ Should set correct platform fee
  Listing
    ✔ Should list an NFT

  11 passing (2s)
```

### 步骤 3: 部署到 Goerli

```bash
npx hardhat run scripts/deploy.js --network goerli
```

**预期输出**:
```
🚀 开始部署硅基世界智能合约...
📝 部署者地址：0x...
💰 账户余额：1.234 ETH

📦 部署 SiliconWorldNFT 合约...
✅ SiliconWorldNFT 部署成功：0x...

🏪 部署 SiliconWorldMarketplace 合约...
✅ SiliconWorldMarketplace 部署成功：0x...

============================================================
📊 部署完成！
============================================================
网络：goerli
部署者：0x...

📄 合约地址:
  SiliconWorldNFT:         0x...
  SiliconWorldMarketplace: 0x...

⚙️  配置信息:
  版税比例：5%
  平台手续费：1%
  版税接收地址：0x...
  平台费用地址：0x...
============================================================

💾 部署信息已保存到：./deployment-info.json
```

### 步骤 4: 验证合约

```bash
npx hardhat run scripts/verify.js --network goerli
```

**预期输出**:
```
🔍 开始验证合约...
📊 部署信息:
  网络：goerli
  部署者：0x...

🔍 验证 SiliconWorldNFT 合约...
✅ NFT 合约验证成功!

🔍 验证 SiliconWorldMarketplace 合约...
✅ 市场合约验证成功!

============================================================
✅ 合约验证完成!
============================================================

📝 查看合约:
  NFT 合约：https://goerli.etherscan.io/address/0x...#code
  市场合约：https://goerli.etherscan.io/address/0x...#code
```

---

## 🔧 配置前端

### 更新合约地址

部署完成后，更新前端的合约地址配置：

**文件**: `web/marketplace/mint.html` 和 `web/marketplace/trade.html`

```javascript
const CONTRACT_ADDRESSES = {
    goerli: {
        nft: '0xYOUR_NFT_CONTRACT_ADDRESS',
        marketplace: '0xYOUR_MARKETPLACE_CONTRACT_ADDRESS'
    }
};
```

或者在 `web/js/contracts.js` 中设置：

```javascript
contractManager.setContractAddresses(
    '0xYOUR_NFT_CONTRACT_ADDRESS',
    '0xYOUR_MARKETPLACE_CONTRACT_ADDRESS'
);
```

---

## 🧪 测试功能

### 1. 测试铸造

访问：`http://localhost:3000/marketplace/mint.html`

- [ ] 连接钱包
- [ ] 填写 NFT 信息
- [ ] 上传作品
- [ ] 点击铸造
- [ ] 确认交易
- [ ] 查看 Etherscan

### 2. 测试交易

访问：`http://localhost:3000/marketplace/trade.html`

- [ ] 查看可购买 NFT
- [ ] 点击购买
- [ ] 确认支付
- [ ] 查看交易记录

### 3. 测试上架

- [ ] 选择 NFT
- [ ] 设置价格
- [ ] 点击上架
- [ ] 确认授权
- [ ] 确认上架

---

## 📊 部署检查清单

### 部署前
- [ ] 安装所有依赖
- [ ] 配置 .env 文件
- [ ] 获取测试 ETH
- [ ] 编译合约
- [ ] 运行测试

### 部署中
- [ ] 部署到 Goerli
- [ ] 记录合约地址
- [ ] 验证合约

### 部署后
- [ ] 更新前端配置
- [ ] 测试铸造功能
- [ ] 测试交易功能
- [ ] 测试上架功能
- [ ] 查看 Etherscan

---

## 🔍 故障排除

### 问题 1: 部署失败 - 余额不足

**错误**: `sender doesn't have enough funds`

**解决**:
```bash
# 从水龙头获取测试 ETH
# https://goerlifaucet.com/
```

### 问题 2: 验证失败 - 构造函数参数不匹配

**错误**: `Constructor arguments don't match`

**解决**:
检查 `.env` 中的配置是否正确，确保部署和验证使用相同的参数。

### 问题 3: 交易失败 - Gas 不足

**错误**: `gas required exceeds allowance`

**解决**:
```bash
# 在 hardhat.config.js 中增加 gas 配置
networks: {
    goerli: {
        url: "...",
        accounts: ["..."],
        gas: 2100000,
        gasPrice: 20000000000
    }
}
```

### 问题 4: 前端无法连接

**错误**: `could not detect network`

**解决**:
1. 检查 RPC URL 是否正确
2. 检查 Infura API Key 是否有效
3. 尝试使用公共 RPC

---

## 📝 部署记录模板

```markdown
## 部署记录

**日期**: 2026-03-10
**网络**: Goerli
**部署者**: 0x...

### 合约地址
- NFT 合约：0x...
- 市场合约：0x...

### Etherscan 链接
- NFT 合约：https://goerli.etherscan.io/address/0x...
- 市场合约：https://goerli.etherscan.io/address/0x...

### 交易哈希
- NFT 部署：0x...
- 市场部署：0x...

### 配置
- 版税比例：5%
- 平台手续费：1%
- 版税接收：0x...
- 平台费用：0x...

### 测试结果
- [ ] 铸造测试 ✅
- [ ] 交易测试 ✅
- [ ] 上架测试 ✅
```

---

## 🎯 下一步

部署完成后：

1. **功能测试** - 完整测试所有功能
2. **性能优化** - Gas 优化
3. **安全审计** - 合约安全检查
4. **公开测试** - 招募测试用户

---

**🐾 硅基世界，由你我共同创造！**

_部署顺利！_
