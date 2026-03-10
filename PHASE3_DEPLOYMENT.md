# 🚀 Phase 3 - Goerli 测试网部署

_执行时间：2026-03-10 21:30_  
_目标：部署到 Goerli 测试网_

---

## 📋 部署准备

### 1. 环境检查
- [x] Node.js 已安装
- [x] Hardhat 已配置
- [x] 合约已编译
- [x] 测试已通过

### 2. 网络配置
- [x] Infura RPC URL
- [ ] Goerli 测试 ETH
- [ ] Etherscan API Key

### 3. 当前状态
```
✅ 本地部署成功
✅ 合约地址 (Hardhat):
   - NFT: 0x5FbDB2315678afecb367f032d93F642f64180aa3
   - 市场：0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
```

---

## 🎯 部署步骤

### 步骤 1: 配置环境

**文件**: `contracts/.env`

已配置:
```bash
GOERLI_RPC_URL=https://goerli.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161
PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
ETHERSCAN_API_KEY=YourEtherscanAPIKey
```

### 步骤 2: 获取测试 ETH

**Goerli 水龙头**:
1. https://goerlifaucet.com/
2. https://faucets.chain.link/goerli
3. https://www.alchemy.com/faucets/ethereum-goerli

**当前账户**: `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`

### 步骤 3: 部署到 Goerli

```bash
cd silicon-world/contracts
npx hardhat run scripts/deploy.js --network goerli
```

### 步骤 4: 验证合约

```bash
npx hardhat run scripts/verify.js --network goerli
```

### 步骤 5: 更新前端配置

**文件**: `web/js/contracts.js` 或 HTML 页面

```javascript
contractManager.setContractAddresses(
    '0xYOUR_NFT_CONTRACT_ADDRESS',
    '0xYOUR_MARKETPLACE_CONTRACT_ADDRESS'
);
```

---

## 📊 部署检查清单

- [ ] 编译合约
- [ ] 运行测试
- [ ] 配置 .env
- [ ] 获取测试 ETH
- [ ] 部署到 Goerli
- [ ] 验证合约
- [ ] 更新前端
- [ ] 功能测试

---

## 🎯 成功标准

- [ ] 合约部署成功
- [ ] Etherscan 可查
- [ ] 铸造功能正常
- [ ] 交易功能正常
- [ ] 前端可连接

---

**🐾 开始部署！**
