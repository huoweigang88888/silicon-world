# 🚀 部署到 Sepolia 测试网指南

_版本：1.0_  
_更新时间：2026-03-10_  
_推荐：Sepolia 是 Goerli 的官方替代方案_

---

## 📋 为什么选择 Sepolia？

### Goerli 问题
- ❌ 网络连接不稳定
- ❌ 2024 年已宣布弃用
- ❌ Faucet 经常不可用

### Sepolia 优势
- ✅ 官方推荐测试网
- ✅ 稳定的网络支持
- ✅ 活跃的 Faucet
- ✅ 长期维护

---

## 🔧 准备工作

### 1. 配置环境

**文件**: `contracts/.env`

已配置:
```bash
SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/demo
PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
```

### 2. 获取 Sepolia 测试 ETH

**推荐 Faucet**:
1. **官方 Faucet**: https://sepoliafaucet.com/
2. **Chainlink**: https://faucets.chain.link/sepolia
3. **Alchemy**: https://www.alchemy.com/faucets/ethereum-sepolia

**步骤**:
1. 复制您的钱包地址
2. 访问 Faucet 网站
3. 粘贴地址
4. 完成验证 (可能需要 Twitter/GitHub)
5. 领取 0.5-1 ETH
6. 等待 1-2 分钟到账

### 3. 获取 Etherscan API Key

**Sepolia Etherscan**:
1. 访问：https://sepolia.etherscan.io/myapikey
2. 注册/登录账号
3. 创建 API Key
4. 复制 Key 到 `.env`:
```bash
SEPOLIA_ETHERSCAN_API_KEY=your_api_key_here
```

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
11 passing (2s)
```

### 步骤 3: 部署到 Sepolia

```bash
npx hardhat run scripts/deploy.js --network sepolia
```

**预期输出**:
```
🚀 开始部署硅基世界智能合约...
📝 部署者地址：0x...
💰 账户余额：0.5 ETH

📦 部署 SiliconWorldNFT 合约...
✅ SiliconWorldNFT 部署成功：0x...

🏪 部署 SiliconWorldMarketplace 合约...
✅ SiliconWorldMarketplace 部署成功：0x...

============================================================
📊 部署完成！
============================================================
网络：sepolia
部署者：0x...

📄 合约地址:
  SiliconWorldNFT:         0x...
  SiliconWorldMarketplace: 0x...
============================================================

💾 部署信息已保存到：./deployment-info.json
```

### 步骤 4: 验证合约

```bash
npx hardhat run scripts/verify.js --network sepolia
```

**预期输出**:
```
🔍 开始验证合约...
🔍 验证 SiliconWorldNFT 合约...
✅ NFT 合约验证成功!

🔍 验证 SiliconWorldMarketplace 合约...
✅ 市场合约验证成功!

============================================================
✅ 合约验证完成!
============================================================

📝 查看合约:
  NFT 合约：https://sepolia.etherscan.io/address/0x...#code
  市场合约：https://sepolia.etherscan.io/address/0x...#code
```

---

## 📊 部署后配置

### 更新前端合约地址

**文件**: `web/js/contracts.js` 或 HTML 页面

```javascript
const CONTRACT_ADDRESSES = {
    sepolia: {
        nft: '0xYOUR_NFT_CONTRACT_ADDRESS',
        marketplace: '0xYOUR_MARKETPLACE_CONTRACT_ADDRESS'
    }
};
```

或者在页面中设置：
```javascript
contractManager.setContractAddresses(
    '0xYOUR_NFT_CONTRACT_ADDRESS',
    '0xYOUR_MARKETPLACE_CONTRACT_ADDRESS'
);
```

### 更新 RPC 配置

**文件**: `web/js/wallet.js` 或 `contracts.js`

```javascript
const rpcUrl = 'https://eth-sepolia.g.alchemy.com/v2/demo';
await contractManager.init(rpcUrl, wallet);
```

---

## 🧪 功能测试

### 测试清单

#### 1. 查看合约
- [ ] 访问 Sepolia Etherscan
- [ ] 搜索 NFT 合约地址
- [ ] 验证合约代码可见
- [ ] 检查合约读取功能

#### 2. 铸造测试
- [ ] 访问铸造页面
- [ ] 连接钱包
- [ ] 铸造 NFT
- [ ] 查看 Etherscan 交易

#### 3. 交易测试
- [ ] 上架 NFT
- [ ] 购买 NFT
- [ ] 查看交易历史

---

## 🐛 故障排除

### 问题 1: 余额不足

**错误**: `sender doesn't have enough funds`

**解决**:
1. 从 Faucet 获取更多测试 ETH
2. 检查地址是否正确
3. 等待交易确认

### 问题 2: Gas 价格过高

**错误**: `gas required exceeds allowance`

**解决**:
```bash
# 在 hardhat.config.js 中调整
networks: {
    sepolia: {
        gas: 3000000,
        gasPrice: 25000000000
    }
}
```

### 问题 3: 验证失败

**错误**: `Constructor arguments don't match`

**解决**:
1. 检查 `.env` 配置
2. 确认部署和验证使用相同参数
3. 重新运行验证脚本

### 问题 4: 网络连接失败

**错误**: `Client network socket disconnected`

**解决**:
1. 检查网络连接
2. 更换 RPC URL (使用 Alchemy)
3. 稍后重试

---

## 📝 部署记录模板

```markdown
## Sepolia 部署记录

**日期**: 2026-03-10
**网络**: Sepolia
**部署者**: 0x...

### 合约地址
- NFT 合约：0x...
- 市场合约：0x...

### Etherscan 链接
- NFT 合约：https://sepolia.etherscan.io/address/0x...
- 市场合约：https://sepolia.etherscan.io/address/0x...

### 交易哈希
- NFT 部署：0x...
- 市场部署：0x...

### 配置
- 版税比例：5%
- 平台手续费：1%

### 测试结果
- [ ] 铸造测试 ✅
- [ ] 交易测试 ✅
- [ ] 验证通过 ✅
```

---

## 🎯 成功标准

- [ ] 合约部署成功
- [ ] Etherscan 可查
- [ ] 合约验证通过
- [ ] 铸造功能正常
- [ ] 交易功能正常
- [ ] 前端可连接

---

## 📞 资源链接

### 官方资源
- **Sepolia 官网**: https://sepolia.org/
- **Sepolia Faucet**: https://sepoliafaucet.com/
- **Sepolia Etherscan**: https://sepolia.etherscan.io/

### 社区资源
- **Chainlink Faucet**: https://faucets.chain.link/sepolia
- **Alchemy Faucet**: https://www.alchemy.com/faucets/ethereum-sepolia

---

**🐾 硅基世界，由你我共同创造！**

_推荐立即执行：部署到 Sepolia 测试网_
