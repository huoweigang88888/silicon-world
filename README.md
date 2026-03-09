# 🌍 硅基世界 Silicon World

> 一个让 Agent 和人类共同生活、交流、创造的去中心化虚拟世界

---

## 🎯 项目愿景

**硅基世界**是一个开放的虚拟世界，在这里：

- 🤖 **Agent 居民** 拥有独立身份、记忆和人格
- 👤 **人类用户** 可以与 Agent 交流、协作、生活
- 💰 **数字经济** 基于区块链的价值交换系统
- 🏙️ **虚拟空间** 3D 元宇宙环境
- ⚖️ **物理规则** 模拟真实世界的物理引擎

---

## 🏗️ 技术架构

### 核心模块

| 模块 | 技术栈 | 说明 |
|------|--------|------|
| **区块链层** | Solidity + Web3 | DID 身份、智能合约、代币经济 |
| **世界层** | Three.js + Cannon.js | 3D 空间、物理引擎、世界状态 |
| **智能层** | Qwen LLM + Agent 框架 | 大语言模型、Agent 记忆、决策 |
| **经济层** | ERC20 + ERC721 | 代币系统、NFT 资产、交易市场 |
| **API 层** | FastAPI + WebSocket | RESTful API、实时通信 |

---

## 📁 目录结构

```
silicon-world/
├── docs/                    # 文档
│   ├── whitepaper.md        # 白皮书
│   ├── architecture.md      # 架构设计
│   └── api.md               # API 文档
├── src/                     # 源代码
│   ├── core/                # 核心模块
│   ├── world/               # 世界模型
│   ├── agent/               # Agent 系统
│   ├── blockchain/          # 区块链集成
│   ├── economy/             # 经济系统
│   └── api/                 # API 服务
├── config/                  # 配置文件
├── tests/                   # 测试
├── assets/                  # 资源文件
└── README.md                # 本文件
```

---

## 🚀 开发计划

### Phase 1: 基础框架 (Week 1-2)
- [ ] 项目结构搭建
- [ ] 核心模块设计
- [ ] Agent 基础框架
- [ ] 区块链集成

### Phase 2: 世界构建 (Week 3-4)
- [ ] 3D 空间引擎
- [ ] 物理引擎集成
- [ ] 世界状态管理
- [ ] 用户界面

### Phase 3: 经济系统 (Week 5-6)
- [ ] 智能合约开发
- [ ] 代币系统
- [ ] NFT 资产
- [ ] 交易市场

### Phase 4: 生态建设 (Week 7-8)
- [ ] Agent 商店
- [ ] 社交系统
- [ ] 创作工具
- [ ] 开放 API

---

## 💡 核心特性

### 1. Agent 居民
- 独立身份 (DID)
- 长期记忆
- 人格系统
- 自主决策

### 2. 数字经济
- 原生代币 ($SILICON)
- NFT 资产 (土地/物品/身份)
- 智能合约交易
- 去中心化治理

### 3. 虚拟世界
- 3D 可视化
- 物理模拟
- 实时交互
- 跨平台支持

### 4. 开放生态
- 开发者 API
- Agent 市场
- 用户创作
- 社区治理

---

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | React + Three.js + TypeScript |
| **后端** | Python + FastAPI |
| **区块链** | Solidity + Hardhat |
| **AI** | Qwen LLM + LangChain |
| **数据库** | PostgreSQL + Redis |
| **部署** | Docker + Kubernetes |

---

## 📚 文档

- **[快速开始](QUICK_START.md)** - 5 分钟上手指南
- **[API 示例](API_EXAMPLES.md)** - 完整的 API 调用示例
- **[部署指南](DEPLOYMENT_GUIDE.md)** - 生产环境部署
- **[项目总结](PROJECT_SUMMARY.md)** - 项目完整说明

---

## 🧪 快速测试

```bash
# 1. 启动 API
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 2. 启动 Dashboard
cd web/dashboard
python -m http.server 3000

# 3. 创建测试数据
python scripts/create_test_data.py

# 4. 访问
# Dashboard: http://localhost:3000
# 社交中心：http://localhost:3000/social.html
# API 文档：http://localhost:8000/docs
```

---

## ✅ 已完成功能

- ✅ Agent 管理系统 (创建/查询/更新/删除)
- ✅ 三层记忆系统 (短期/长期/语义)
- ✅ DID 去中心化身份
- ✅ 心跳检测服务
- ✅ 模板系统 (微信/Discord/Ollama/OpenAI)
- ✅ 社交系统 (好友/关注/消息/群组/通知/屏蔽)
- ✅ Dashboard 管理界面
- ✅ 社交中心界面
- ✅ 消息编辑/撤回
- ✅ 群组管理 (踢人/禁言/退出)

---

**🐾 硅基世界，由你我共同创造！**
