# 🚀 硅基世界 - 测试网部署检查清单

_创建时间：2026-03-08 13:57_

---

## ⚠️ 当前状态

| 组件 | 状态 | 说明 |
|------|------|------|
| Docker | ❌ 未安装 | 需要安装 Docker Desktop |
| Python | ✅ 3.13.9 | 已安装 |
| 项目代码 | ✅ 2802 文件 | 完整 |
| 智能合约 | ✅ 已编译 | 待部署到测试网 |
| 环境变量 | ❌ 未配置 | 需要创建 .env 文件 |

---

## 📋 部署方案选择

### 方案 A: 本地测试部署 (推荐先做这个)
**无需 Docker，直接用 Python 运行 API 服务**

**步骤：**
1. 安装 Python 依赖
2. 配置 .env 文件
3. 启动 PostgreSQL (可用 Docker 或本地安装)
4. 启动 Redis (可用 Docker 或本地安装)
5. 运行 API 服务
6. 访问 http://localhost:8000/docs

**优点：** 快速验证，无需复杂配置  
**缺点：** 仅本地访问，非生产环境

---

### 方案 B: 完整测试网部署
**需要 Docker + 区块链测试网配置**

**前置条件：**
1. 安装 Docker Desktop for Windows
2. 获取 Infura API Key (https://infura.io)
3. 准备测试网 ETH (Goerli faucet)
4. 配置部署私钥

**步骤：**
1. 安装 Docker Desktop
2. 创建 .env 文件 (见下方模板)
3. 运行 `python scripts/deploy-testnet.py`
4. 合约部署到 Goerli 测试网
5. API 服务容器化部署

**优点：** 完整的生产环境模拟  
**缺点：** 需要额外配置和时间

---

## 🔧 立即执行：方案 A (本地测试)

### 1. 创建 .env 文件

```bash
# 数据库 (先使用 SQLite 简化部署)
DATABASE_URL=sqlite:///./silicon_world.db
DATABASE_TYPE=sqlite

# Redis (可选，初期可不用)
REDIS_URL=redis://localhost:6379

# API 配置
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# 区块链 (测试网部署时需要)
# PRIVATE_KEY=your_private_key_here
# INFURA_KEY=your_infura_key_here
# NETWORK=goerli

# LLM 配置
QWEN_API_KEY=your_qwen_key
OPENAI_API_KEY=your_openai_key
```

### 2. 安装依赖

```bash
cd C:\Users\zzz\.openclaw\workspace\silicon-world
pip install -r requirements.txt
```

### 3. 启动 API 服务

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问 API 文档

浏览器打开：http://localhost:8000/docs

---

## 📝 方案 B 补充配置 (后续需要时)

### .env 完整模板

```bash
# ============ 数据库 ============
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/silicon_world
DATABASE_TYPE=postgresql

# ============ Redis ============
REDIS_URL=redis://localhost:6379

# ============ API ============
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
API_SECRET_KEY=your-secret-key-here

# ============ 区块链 ============
PRIVATE_KEY=0xYOUR_PRIVATE_KEY
INFURA_KEY=your_infura_project_id
NETWORK=goerli
CHAIN_ID=5

# ============ LLM ============
QWEN_API_KEY=sk-xxx
OPENAI_API_KEY=sk-xxx

# ============ 监控 ============
SENTRY_DSN=https://xxx@sentry.io/xxx
LOG_LEVEL=INFO
```

### 获取测试网 ETH

- Goerli Faucet: https://goerlifaucet.com
- Alchemy Faucet: https://www.alchemy.com/faucets/ethereum-goerli

### 创建 Infura 项目

1. 注册 https://infura.io
2. 创建新项目
3. 选择 Ethereum 网络
4. 复制 Project ID (即 INFURA_KEY)

---

## 🎯 下一步行动

**大哥选择：**

1. **先本地测试** → 我马上创建 .env 并启动 API 服务
2. **直接完整部署** → 需要先安装 Docker，我提供安装指南
3. **只部署合约** → 配置钱包和 Infura 后单独部署智能合约

---

_三一 整理于 2026-03-08_
