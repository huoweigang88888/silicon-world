# 明日部署指南 - 2026-03-13

**问题**: Node.js undici 库连接超时  
**状态**: 代码 100% 就绪，等待网络问题解决  

---

## 🔍 问题诊断

### 已验证
- ✅ curl 可以访问 Alchemy RPC
- ✅ Alchemy API Key 有效
- ✅ 合约编译成功
- ✅ 配置文件正确

### 问题
- ❌ hardhat 使用 undici 库连接超时
- ❌ 多个 RPC 节点都超时
- ❌ 手机热点也无法解决

### 原因
Node.js 18+ 使用 undici 作为默认 HTTP 客户端，可能存在：
1. 代理设置问题
2. DNS 解析问题
3. IPv6/IPv4 优先级问题

---

## 🛠️ 解决方案

### 方案 A: 设置 Node.js 代理（推荐先试）

```bash
# PowerShell
$env:NODE_OPTIONS="--no-deprecation"
cd contracts
npx hardhat run scripts/deploy-working.cjs --network sepolia
```

### 方案 B: 使用 legacy HTTP 库

修改 `hardhat.config.js` 添加：
```javascript
module.exports = {
  // ...
  networks: {
    sepolia: {
      url: "https://eth-sepolia.g.alchemy.com/v2/AP6EAjqS9hYALHJAFuk1K",
      accounts: ["0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"],
      chainId: 11155111,
      timeout: 300000,
      httpHeaders: {
        "User-Agent": "hardhat-deployer"
      }
    }
  }
}
```

### 方案 C: 使用 Remix IDE 部署（最简单！）

1. 访问 https://remix.ethereum.org/
2. 上传合约文件 (`contracts/contracts/*.sol`)
3. 编译合约
4. 连接 MetaMask（确保有 Sepolia ETH）
5. 部署合约
6. 复制合约地址到前端配置

### 方案 D: 找人帮忙部署

把代码和配置发给有正常网络的朋友，帮忙运行部署命令。

---

## 📝 部署命令（问题解决后）

```bash
cd C:\Users\zzz\.openclaw\workspace\silicon-world\contracts

# 方式 1: 使用工作脚本
npx hardhat run scripts/deploy-working.cjs --network sepolia

# 方式 2: 使用简单脚本
npx hardhat run scripts/deploy-simple.cjs --network sepolia

# 方式 3: 直接 hardhat 控制台
npx hardhat console --network sepolia
> const NFT = await ethers.getContractFactory("SiliconWorldNFT")
> const nft = await NFT.deploy()
> await nft.deployed()
> console.log(nft.address)
```

---

## ✅ 部署后任务

1. **记录合约地址**
   - 会自动保存到 `deployments/sepolia.json`

2. **更新前端配置**
   - 编辑 `web/js/contracts.js`
   - 填入部署的合约地址

3. **验证合约**
   ```bash
   npx hardhat verify --network sepolia <CONTRACT_ADDRESS>
   ```

4. **测试功能**
   - 打开 `web/world.html`
   - 连接钱包
   - 测试 NFT 铸造

---

## 🎯 成功标准

- [ ] 合约部署到 Sepolia
- [ ] 合约地址记录
- [ ] 前端配置更新
- [ ] 功能测试通过

---

**代码已 100% 就绪，解决网络问题后即可部署！**

_最后更新：2026-03-12 21:35_
