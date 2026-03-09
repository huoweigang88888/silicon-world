# 🚀 硅基世界 - 测试网部署计划

_创建时间：2026-03-08 15:25_

---

## 📋 当前状态

| 组件 | 状态 | 说明 |
|------|------|------|
| API 后端 | ✅ 完成 | 本地测试通过 |
| 数据库 | ✅ 完成 | SQLite 正常 |
| Agent 功能 | ✅ 完成 | 创建/查询/记忆 |
| DID 身份 | ✅ 完成 | 去中心化身份 |
| Docker | ❌ 未安装 | 需要安装 |
| 智能合约 | ⏸️ 待部署 | 需要 Infura + 钱包 |
| 前端 | ⏸️ 暂缓 | 后续完善 |

---

## 🎯 部署目标

**将硅基世界部署到公网，支持：**
- 公开访问 API
- 区块链智能合约
- 真实 DID 身份系统
- 多人使用

---

## 📦 部署步骤

### Step 1: 安装 Docker Desktop (10 分钟)

**下载地址**: https://www.docker.com/products/docker-desktop

**安装步骤：**
1. 下载 Docker Desktop for Windows
2. 运行安装程序
3. 启用 WSL 2 后端（推荐）
4. 重启电脑
5. 启动 Docker Desktop

**验证安装：**
```bash
docker --version
docker-compose --version
```

---

### Step 2: 获取 Infura API Key (5 分钟)

**网址**: https://infura.io

**步骤：**
1. 注册账号（免费）
2. 创建新项目 → 选择 "Ethereum"
3. 复制 Project ID（类似 `a1b2c3d4e5f6...`）
4. 记录 Mainnet 和 Goerli 的 RPC URL

**需要的信息：**
- Project ID: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- Goerli RPC: `https://goerli.infura.io/v3/你的 ID`

---

### Step 3: 准备钱包和测试币 (5 分钟)

**3.1 导出钱包私钥**
- 打开 MetaMask
- 选择账号 → 详情 → 导出私钥
- 复制私钥（不要 0x 前缀）

**3.2 获取 Goerli 测试币**
- 访问 https://goerlifaucet.com
- 输入钱包地址
- 领取 0.1-0.5 ETH（免费）

---

### Step 4: 配置环境变量 (2 分钟)

编辑 `.env` 文件：
```bash
# 数据库（PostgreSQL）
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/silicon_world

# Redis
REDIS_URL=redis://localhost:6379

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# 区块链
PRIVATE_KEY=你的私钥（不要 0x）
INFURA_KEY=你的 Infura Project ID
NETWORK=goerli
CHAIN_ID=5
```

---

### Step 5: 部署智能合约 (10 分钟)

```bash
cd C:\Users\zzz\.openclaw\workspace\silicon-world

# 安装 Node.js 依赖
npm install

# 编译合约
npx hardhat compile

# 部署到 Goerli
npx hardhat run scripts/deploy.js --network goerli
```

**部署成功后记录：**
- Identity 合约地址
- SILICONToken 合约地址
- WorldNFT 合约地址

---

### Step 6: 启动服务 (5 分钟)

```bash
# 使用 Docker Compose 启动
docker-compose up -d

# 检查状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

---

### Step 7: 验证部署 (5 分钟)

**7.1 健康检查**
```bash
curl http://localhost:8000/health
```

**7.2 测试 API**
```bash
# 创建 Agent
curl -X POST http://localhost:8000/api/v1/agents \
  -H "Content-Type: application/json" \
  -d '{"name":"测试","controller":"0x地址"}'
```

**7.3 验证合约**
- 访问 https://goerli.etherscan.io
- 搜索部署的合约地址
- 确认合约已上链

---

## ⏱️ 总时间估算

| 步骤 | 时间 |
|------|------|
| Docker 安装 | 10 分钟 |
| Infura 注册 | 5 分钟 |
| 钱包准备 | 5 分钟 |
| 环境配置 | 2 分钟 |
| 合约部署 | 10 分钟 |
| 服务启动 | 5 分钟 |
| 验证测试 | 5 分钟 |
| **总计** | **约 42 分钟** |

---

## 📞 可能遇到的问题

### Docker 安装失败
- 确保启用虚拟化（BIOS 设置）
- 使用 WSL 2 后端
- 重启电脑后再试

### Infura 注册问题
- 需要邮箱验证
- 免费额度足够测试使用

### 测试币领取失败
- 每个地址每天限领一次
- 可尝试多个水龙头

### 合约部署失败
- 检查私钥格式
- 确保有足够测试币
- 检查网络连接

---

## ✅ 下一步行动

1. **现在** → 安装 Docker Desktop
2. **同时** → 注册 Infura + 准备钱包
3. **完成后** → 我帮大哥执行部署命令

---

**🐾 准备就绪后告诉大哥开始！**
