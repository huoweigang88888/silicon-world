# 🚀 硅基世界 - Phase 3 快速启动指南

_版本：1.0_  
_更新时间：2026-03-10_  
_阶段：Phase 3 - 测试网部署_

---

## 📋 快速启动 (本地开发)

### 方法 1: 使用启动脚本

**Windows**:
```bash
start-dev.bat
```

**Linux/Mac**:
```bash
chmod +x start-dev.sh
./start-dev.sh
```

### 方法 2: 手动启动

**1. 启动 API 服务**:
```bash
cd silicon-world
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**2. 启动 Dashboard**:
```bash
cd web/dashboard
python -m http.server 3000
```

**3. 启动 NFT 市场**:
```bash
cd web/marketplace
python -m http.server 3001
```

### 访问服务

| 服务 | URL | 说明 |
|------|-----|------|
| API 服务 | http://localhost:8000 | 后端 API |
| API 文档 | http://localhost:8000/docs | Swagger UI |
| Dashboard | http://localhost:3000 | 主界面 |
| NFT 市场 | http://localhost:3001 | NFT 交易 |
| 铸造页面 | http://localhost:3001/mint.html | 铸造 NFT |
| 交易页面 | http://localhost:3001/trade.html | 买卖 NFT |

---

## 🔧 智能合约部署

### 本地部署 (测试)

**1. 编译合约**:
```bash
cd silicon-world/contracts
npx hardhat compile
```

**2. 运行测试**:
```bash
npx hardhat test
```

**3. 部署到本地网络**:
```bash
npx hardhat run scripts/deploy.js --network hardhat
```

**预期输出**:
```
✅ SiliconWorldNFT 部署成功：0x...
✅ SiliconWorldMarketplace 部署成功：0x...
```

### Goerli 部署 (测试网)

**1. 配置环境**:
```bash
cd silicon-world/contracts
cp .env.example .env
# 编辑 .env 填入你的私钥和 RPC URL
```

**2. 获取测试 ETH**:
- https://goerlifaucet.com/
- https://faucets.chain.link/goerli

**3. 部署合约**:
```bash
npx hardhat run scripts/deploy.js --network goerli
```

**4. 验证合约**:
```bash
npx hardhat run scripts/verify.js --network goerli
```

---

## 🧪 功能测试

### 测试清单

#### 1. NFT 铸造
- [ ] 访问铸造页面
- [ ] 连接钱包
- [ ] 填写 NFT 信息
- [ ] 上传作品
- [ ] 点击铸造
- [ ] 确认交易
- [ ] 查看结果

#### 2. NFT 交易
- [ ] 访问交易页面
- [ ] 浏览可购买 NFT
- [ ] 点击购买
- [ ] 确认支付
- [ ] 查看交易记录

#### 3. NFT 上架
- [ ] 选择 NFT
- [ ] 设置价格
- [ ] 点击上架
- [ ] 授权合约
- [ ] 确认上架

---

## 📝 测试用户指南

### 第一步：创建钱包

1. 访问 Dashboard
2. 点击"钱包"
3. 点击"创建钱包"
4. 设置密码
5. **备份助记词** (重要！)

### 第二步：获取测试 ETH

1. 复制钱包地址
2. 访问水龙头网站
3. 粘贴地址
4. 领取测试 ETH
5. 等待到账 (约 1-2 分钟)

### 第三步：铸造 NFT

1. 访问铸造页面
2. 解锁钱包
3. 填写 NFT 信息
4. 上传作品
5. 点击铸造
6. 确认交易
7. 等待确认

### 第四步：交易 NFT

**购买**:
1. 访问交易页面
2. 选择"购买"标签
3. 浏览 NFT
4. 点击购买
5. 确认支付

**出售**:
1. 访问交易页面
2. 选择"出售"标签
3. 选择 NFT
4. 设置价格
5. 点击上架

---

## 🐛 常见问题

### Q1: 无法连接钱包

**解决**:
1. 检查浏览器控制台
2. 清除浏览器缓存
3. 刷新页面重试

### Q2: 交易失败

**解决**:
1. 检查余额是否足够
2. 增加 Gas 费用
3. 稍后重试

### Q3: 页面加载慢

**解决**:
1. 检查网络连接
2. 清除浏览器缓存
3. 更换浏览器

### Q4: 找不到合约

**解决**:
1. 检查合约地址是否正确
2. 确认网络是否正确 (Goerli)
3. 重新部署合约

---

## 📞 获取帮助

### 技术支持
- **Discord**: #support 频道
- **Email**: support@silicon-world.com
- **GitHub**: 提交 Issue

### 文档资源
- **部署指南**: DEPLOYMENT_GUIDE_PHASE2.md
- **测试计划**: PHASE4_TESTING_PLAN.md
- **安全实践**: WEB3_SECURITY_BEST_PRACTICES.md

---

## 🎯 下一步

### 完成本地测试后:
1. ✅ 部署到 Goerli 测试网
2. ✅ 验证合约
3. ✅ 更新前端配置
4. ✅ 开始公开测试

### 公开测试准备:
1. ✅ 准备测试数据
2. ✅ 编写用户指南
3. ✅ 招募测试用户
4. ✅ 设置反馈渠道

---

**🐾 硅基世界，由你我共同创造！**

_祝测试顺利！_
