# 🌍 硅基世界 Silicon World

> **Phase 2 已完成！** 一个让 Agent 和人类共同生活、交流、创造的去中心化虚拟世界

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Phase](https://img.shields.io/badge/Phase-2%20Complete-blue)](https://github.com/huoweigang88888/silicon-world)
[![Tests](https://img.shields.io/badge/Tests-51%20passing-brightgreen)](https://github.com/huoweigang88888/silicon-world)
[![Code Lines](https://img.shields.io/badge/Code-75k%2B%20lines-orange)](https://github.com/huoweigang88888/silicon-world)

---

## 🎯 项目愿景

**硅基世界**是一个开放的虚拟世界，在这里：

- 🤖 **Agent 居民** 拥有独立身份、记忆和人格
- 👤 **人类用户** 可以与 Agent 交流、协作、生活
- 💰 **数字经济** 基于区块链的价值交换系统
- 🎨 **NFT 市场** 铸造、交易独特数字资产
- 🏆 **游戏化** 成就、徽章、排行榜系统

---

## 🚀 快速开始

### 一键启动 (Windows)

```bash
start-dev.bat
```

### 一键启动 (Linux/Mac)

```bash
chmod +x start-dev.sh
./start-dev.sh
```

### 手动启动

```bash
# 1. 启动 API 服务
cd silicon-world
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 2. 启动 Dashboard
cd web/dashboard
python -m http.server 3000

# 3. 启动 NFT 市场
cd web/marketplace
python -m http.server 3001
```

### 访问服务

| 服务 | URL |
|------|-----|
| API 文档 | http://localhost:8000/docs |
| Dashboard | http://localhost:3000 |
| NFT 市场 | http://localhost:3001 |

---

## 📦 已完成功能 (Phase 2)

### ✅ 核心系统
- [x] Agent 管理系统
- [x] 三层记忆系统
- [x] 社交系统 (好友/消息/群组)
- [x] DID 去中心化身份

### ✅ NFT 市场
- [x] NFT 铸造 (ERC-721)
- [x] NFT 交易市场
- [x] NFT 收藏管理
- [x] 版税机制 (5%)

### ✅ 游戏化系统
- [x] 成就系统 (10+ 成就)
- [x] 徽章系统 (19+ 徽章)
- [x] 每日任务 (13+ 任务)
- [x] 排行榜 (6 种类型)

### ✅ 区块链集成
- [x] 智能合约 (Solidity)
- [x] 钱包管理 (ethers.js)
- [x] 支付系统
- [x] 链上交易

### ✅ 开发者工具
- [x] RESTful API
- [x] API 文档 (Swagger)
- [x] SDK 支持
- [x] 快速开始指南

---

## 🏗️ 技术架构

### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 主要编程语言 |
| FastAPI | 0.124+ | Web 框架 |
| SQLAlchemy | 2.0+ | ORM |
| SQLite/PostgreSQL | - | 数据库 |

### 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| HTML5/CSS3/JS | - | 前端基础 |
| ethers.js | v6 | 区块链交互 |
| 响应式设计 | - | 多端适配 |

### 区块链技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Solidity | 0.8.20 | 智能合约 |
| Hardhat | - | 开发环境 |
| OpenZeppelin | 4.9.6 | 标准合约 |
| ERC-721 | - | NFT 标准 |

---

## 📁 目录结构

```
silicon-world/
├── 📄 README.md                    # 本文件
├── 📄 QUICK_START_PHASE3.md        # 快速启动指南
├── 📄 USER_GUIDE.md                # 用户指南
├── 📄 DEPLOYMENT_GUIDE_PHASE2.md   # 部署指南
├── 📄 PHASE2_COMPLETE.md           # Phase 2 完成报告
├── 📄 PROJECT_SUMMARY_2026-03-10.md # 项目汇总
├── 
├── 📂 contracts/                   # 智能合约
│   ├── contracts/
│   │   ├── SiliconWorldNFT.sol     # NFT 合约
│   │   └── SiliconWorldMarketplace.sol  # 市场合约
│   ├── scripts/
│   │   ├── deploy.js               # 部署脚本
│   │   └── verify.js               # 验证脚本
│   ├── test/
│   │   └── NFTTest.js              # 合约测试
│   └── hardhat.config.js           # Hardhat 配置
├── 
├── 📂 src/                         # Python 源代码
│   ├── api/
│   │   ├── main.py                 # FastAPI 主应用
│   │   └── routes/
│   │       ├── agents.py           # Agent API
│   │       ├── social.py           # 社交 API
│   │       ├── gamification.py     # 游戏化 API
│   │       └── nexusa.py           # 区块链 API
│   ├── gamification/
│   │   ├── achievements.py         # 成就系统
│   │   ├── leaderboard.py          # 排行榜
│   │   ├── daily_tasks.py          # 每日任务
│   │   └── rewards.py              # 奖励系统
│   ├── nexusa/
│   │   ├── wallet.py               # 钱包管理
│   │   ├── payment.py              # 支付系统
│   │   └── config.py               # 配置管理
│   └── optimization/
│       └── db_optimizer.py         # 数据库优化
├── 
├── 📂 web/                         # 前端
│   ├── dashboard/
│   │   ├── index.html              # 主界面
│   │   ├── wallet.html             # 钱包页面
│   │   └── gamification.html       # 游戏化中心
│   ├── marketplace/
│   │   ├── index.html              # NFT 市场
│   │   ├── mint.html               # 铸造页面
│   │   ├── trade.html              # 交易页面
│   │   ├── collection.html         # 收藏页面
│   │   ├── create.html             # 创建页面
│   │   └── detail.html             # 详情页面
│   ├── developers/
│   │   └── index.html              # 开发者门户
│   └── js/
│       ├── wallet.js               # 钱包模块
│       └── contracts.js            # 合约交互模块
├── 
├── 📂 scripts/                     # 工具脚本
│   ├── pressure_test.py            # 压力测试
│   └── migrate_*.py                # 数据库迁移
└── 
└── 📂 tests/                       # 测试用例
    └── test_*.py                   # Python 测试
```

---

## 🧪 测试

### 运行单元测试

```bash
# Python 测试
pytest tests/

# 智能合约测试
cd contracts
npx hardhat test
```

### 测试结果

```
✅ 51 个测试用例全部通过
✅ 11 个合约测试通过
✅ 19 个 Solidity 文件编译成功
```

---

## 📊 项目统计

| 指标 | 数量 |
|------|------|
| **总代码行数** | ~75,000 |
| **总文件数** | 170+ |
| **Python 模块** | 60+ |
| **前端页面** | 16+ |
| **智能合约** | 2 |
| **测试用例** | 51 |
| **文档文件** | 35+ |

---

## 📅 开发历程

### Phase 1 MVP ✅ (2026-03-01 ~ 03-07)
- Agent 核心系统
- 记忆系统
- 社交系统
- DID 身份

### Week 9-10 ✅ (2026-03-08 ~ 03-10)
- NFT 市场 UI
- 游戏化系统
- 开发者门户
- 性能优化

### Phase 2 ✅ (2026-03-10)
- 智能合约开发
- 前端链上集成
- 本地部署成功
- 完整文档体系

### Phase 3 🟡 (进行中)
- Goerli 测试网部署
- 合约验证
- 公开测试准备

### Phase 4 ⏳ (计划中)
- 公开测试 (50-100 用户)
- 反馈收集
- Bug 修复

---

## 📚 文档

### 用户文档
- [用户指南](USER_GUIDE.md) - 完整使用说明
- [快速开始](QUICK_START_PHASE3.md) - 5 分钟上手
- [FAQ](FAQ.md) - 常见问题

### 开发文档
- [部署指南](DEPLOYMENT_GUIDE_PHASE2.md) - 完整部署流程
- [API 文档](http://localhost:8000/docs) - Swagger UI
- [安全实践](WEB3_SECURITY_BEST_PRACTICES.md) - Web3 安全

### 项目文档
- [Phase 2 完成报告](PHASE2_COMPLETE.md)
- [项目汇总](PROJECT_SUMMARY_2026-03-10.md)
- [测试计划](PHASE4_TESTING_PLAN.md)

---

## 🤝 参与贡献

### 开发环境设置

```bash
# 1. 克隆仓库
git clone https://github.com/huoweigang88888/silicon-world.git
cd silicon-world

# 2. 安装依赖
pip install -r requirements.txt
cd contracts && npm install

# 3. 启动服务
./start-dev.sh
```

### 提交代码

```bash
# 1. Fork 仓库
# 2. 创建分支
git checkout -b feature/your-feature

# 3. 提交代码
git commit -m "Add your feature"

# 4. 推送并创建 PR
git push origin feature/your-feature
```

---

## 📞 联系方式

- **GitHub**: https://github.com/huoweigang88888/silicon-world
- **Discord**: https://discord.gg/siliconworld
- **Email**: support@silicon-world.com
- **Twitter**: @SiliconWorld

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

感谢所有参与项目的开发者和测试用户！

特别感谢：
- **大哥** - 项目发起者和支持者
- **三一** - AI 助手和主要开发者
- **开源社区** - 提供优质的工具和库

---

**🐾 硅基世界，由你我共同创造！**

[![Star History Chart](https://api.star-history.com/svg?repos=huoweigang88888/silicon-world&type=Date)](https://star-history.com/#huoweigang88888/silicon-world&Date)
