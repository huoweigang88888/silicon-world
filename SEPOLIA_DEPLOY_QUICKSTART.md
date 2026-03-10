# 🚀 Sepolia 快速部署指南 (5 分钟)

_版本：1.0_  
_更新时间：2026-03-10_  
_目标：5 分钟内部署到 Sepolia 测试网_

---

## ⚡ 快速步骤

### 1️⃣ 获取 Alchemy API Key (2 分钟)

**步骤**:
1. 访问：https://www.alchemy.com/
2. 点击右上角 **"Sign Up"**
3. 使用 GitHub/Google/Email 注册 (免费)
4. 登录后点击 **"Create App"**
5. 填写信息:
   - **Name**: Silicon World
   - **Chain**: Ethereum
   - **Network**: Sepolia
   - **System**: Hardhat (默认)
6. 点击 **"Create App"**
7. 复制 **HTTPS** URL (类似：`https://eth-sepolia.g.alchemy.com/v2/YOUR_KEY`)

**截图指引**:
```
Alchemy Dashboard → Apps → Create App → 复制 HTTPS URL
```

### 2️⃣ 配置 .env (1 分钟)

**文件**: `contracts/.env`

```bash
# 替换 YOUR_KEY 为你的 Alchemy API Key
SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_KEY

# 使用 Hardhat 默认测试私钥 (仅用于测试！)
PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
```

### 3️⃣ 获取 Sepolia ETH (1 分钟)

**方法 1: Alchemy Faucet (推荐)**
1. 访问：https://www.alchemy.com/faucets/ethereum-sepolia
2. 粘贴你的钱包地址
3. 点击 **"Send 0.5 ETH"**
4. 等待 1-2 分钟到账

**钱包地址**: `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266` (Hardhat 默认 #0)

**方法 2: Sepolia 官方 Faucet**
1. 访问：https://sepoliafaucet.com/
2. 需要 Twitter/GitHub 验证
3. 每日 0.5 ETH

### 4️⃣ 部署合约 (1 分钟)

```bash
cd silicon-world/contracts
npx hardhat run scripts/deploy.js --network sepolia
```

**预期输出**:
```
🚀 开始部署硅基世界智能合约...
📝 部署者地址：0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
💰 账户余额：0.5 ETH

📦 部署 SiliconWorldNFT 合约...
✅ SiliconWorldNFT 部署成功：0x...

🏪 部署 SiliconWorldMarketplace 合约...
✅ SiliconWorldMarketplace 部署成功：0x...

============================================================
📊 部署完成！
============================================================
```

### 5️⃣ 验证合约 (可选，1 分钟)

**获取 Etherscan API Key**:
1. 访问：https://sepolia.etherscan.io/myapikey
2. 注册/登录
3. 创建 API Key
4. 复制到 `.env`:
```bash
SEPOLIA_ETHERSCAN_API_KEY=your_api_key
```

**验证命令**:
```bash
npx hardhat run scripts/verify.js --network sepolia
```

---

## 📊 部署后配置

### 更新前端

**文件**: `web/js/contracts.js` 或 HTML 页面

```javascript
// 在初始化时设置合约地址
contractManager.setContractAddresses(
    '0xYOUR_NFT_CONTRACT_ADDRESS',
    '0xYOUR_MARKETPLACE_CONTRACT_ADDRESS'
);
```

### 更新 RPC

**文件**: `web/js/wallet.js`

```javascript
const rpcUrl = 'https://eth-sepolia.g.alchemy.com/v2/YOUR_KEY';
await contractManager.init(rpcUrl, wallet);
```

---

## 🎯 完整命令清单

```bash
# 1. 进入合约目录
cd silicon-world/contracts

# 2. 编译合约
npx hardhat compile

# 3. 运行测试
npx hardhat test

# 4. 部署到 Sepolia
npx hardhat run scripts/deploy.js --network sepolia

# 5. 验证合约 (可选)
npx hardhat run scripts/verify.js --network sepolia
```

---

## 🐛 故障排除

### 问题 1: "invalid project id"

**原因**: Alchemy API Key 无效或未配置

**解决**:
1. 检查 `.env` 中的 `SEPOLIA_RPC_URL`
2. 确保 URL 格式正确：`https://eth-sepolia.g.alchemy.com/v2/YOUR_KEY`
3. 重新创建 Alchemy App 获取新 Key

### 问题 2: "sender doesn't have enough funds"

**原因**: 账户余额不足

**解决**:
1. 从 Faucet 获取更多 ETH
2. 检查钱包地址是否正确
3. 等待交易确认

### 问题 3: "network timeout"

**原因**: 网络连接问题

**解决**:
1. 检查网络连接
2. 增加超时配置：
```javascript
// hardhat.config.js
sepolia: {
  timeout: 120000, // 2 分钟
  gas: 3000000,
  gasPrice: 25000000000
}
```

---

## ✅ 检查清单

部署前:
- [ ] Alchemy 账号已注册
- [ ] Sepolia App 已创建
- [ ] API Key 已复制到 .env
- [ ] 已从 Faucet 获取 ETH
- [ ] 合约已编译
- [ ] 测试已通过

部署后:
- [ ] 合约地址已记录
- [ ] Etherscan 可查
- [ ] 前端已更新
- [ ] 功能测试通过

---

## 📞 资源链接

### 必备
- **Alchemy 注册**: https://www.alchemy.com/
- **Sepolia Faucet**: https://www.alchemy.com/faucets/ethereum-sepolia
- **Sepolia Etherscan**: https://sepolia.etherscan.io/

### 备选 Faucet
- **官方**: https://sepoliafaucet.com/
- **Chainlink**: https://faucets.chain.link/sepolia

---

## 🎉 成功标准

- ✅ 合约部署成功
- ✅ Etherscan 可查
- ✅ 铸造功能正常
- ✅ 交易功能正常
- ✅ 前端可连接

---

**🐾 硅基世界，由你我共同创造！**

_预计总时间：5-7 分钟_
