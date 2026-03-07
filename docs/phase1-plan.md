# 📅 Phase 1 开发计划 - MVP

**时间**: Week 1-10 (2026-03-07 至 2026-05-16)  
**目标**: 最小可行产品 (MVP)  
**状态**: 🟢 进行中

---

## 🎯 Phase 1 目标

交付一个可用的 MVP，包含：
- ✅ Agent DID 身份系统
- ✅ Agent 核心框架
- ✅ 基础记忆系统
- ✅ 代币智能合约
- ✅ 基础 RESTful API

---

## 📋 Week 1-2: DID 身份系统

### 任务清单

| 任务 | 优先级 | 工时 | 状态 | 负责人 |
|------|--------|------|------|--------|
| **1.1 技术选型** | P0 | 2h | ⬜ 待办 | - |
| **1.2 设计 DID 数据结构** | P0 | 4h | ⬜ 待办 | - |
| **1.3 实现 DID 生成** | P0 | 1d | ⬜ 待办 | - |
| **1.4 实现 DID 验证** | P0 | 1d | ⬜ 待办 | - |
| **1.5 区块链集成** | P0 | 2d | ⬜ 待办 | - |
| **1.6 编写 API** | P0 | 1d | ⬜ 待办 | - |
| **1.7 单元测试** | P0 | 1d | ⬜ 待办 | - |

### 交付物

- [ ] `src/blockchain/did.py` - DID 生成/验证
- [ ] `src/blockchain/contracts/Identity.sol` - 身份合约
- [ ] `src/api/identity.py` - 身份 API
- [ ] `tests/test_did.py` - 测试用例
- [ ] `docs/did-spec.md` - DID 规范文档

### 技术方案

```python
# DID 数据结构
{
  "did": "did:silicon:agent:0x1234...",
  "controller": "0xaddress...",
  "created": "2026-03-07T00:00:00Z",
  "updated": "2026-03-07T00:00:00Z",
  "publicKey": [...],
  "service": [...]
}
```

---

## 📋 Week 3-5: Agent 核心框架

### 任务清单

| 任务 | 优先级 | 工时 | 状态 | 负责人 |
|------|--------|------|------|--------|
| **2.1 Agent 基类设计** | P0 | 1d | ⬜ 待办 | - |
| **2.2 人格系统实现** | P0 | 2d | ⬜ 待办 | - |
| **2.3 LLM 集成** | P0 | 2d | ⬜ 待办 | - |
| **2.4 决策系统** | P0 | 2d | ⬜ 待办 | - |
| **2.5 行为执行器** | P0 | 2d | ⬜ 待办 | - |
| **2.6 Agent 管理器** | P0 | 1d | ⬜ 待办 | - |
| **2.7 集成测试** | P0 | 1d | ⬜ 待办 | - |

### 交付物

- [ ] `src/agent/core.py` - Agent 基类
- [ ] `src/agent/personality.py` - 人格系统
- [ ] `src/agent/llm.py` - LLM 集成
- [ ] `src/agent/decision.py` - 决策系统
- [ ] `src/agent/executor.py` - 行为执行器
- [ ] `src/agent/manager.py` - Agent 管理器
- [ ] `tests/test_agent.py` - 测试用例

### 技术方案

```python
class Agent:
    def __init__(self, did, personality, llm):
        self.did = did
        self.personality = personality
        self.memory = MemorySystem()
        self.llm = llm
    
    async def think(self, context):
        """思考决策"""
        prompt = self._build_prompt(context)
        response = await self.llm.generate(prompt)
        return self._parse_action(response)
    
    async def act(self, action):
        """执行动作"""
        return await self.executor.execute(action)
```

---

## 📋 Week 6-7: 基础记忆系统

### 任务清单

| 任务 | 优先级 | 工时 | 状态 | 负责人 |
|------|--------|------|------|--------|
| **3.1 记忆数据模型** | P0 | 1d | ⬜ 待办 | - |
| **3.2 短期记忆实现** | P0 | 1d | ⬜ 待办 | - |
| **3.3 长期记忆实现** | P0 | 2d | ⬜ 待办 | - |
| **3.4 语义记忆实现** | P0 | 2d | ⬜ 待办 | - |
| **3.5 记忆巩固机制** | P0 | 1d | ⬜ 待办 | - |
| **3.6 记忆检索 API** | P0 | 1d | ⬜ 待办 | - |
| **3.7 性能优化** | P0 | 1d | ⬜ 待办 | - |

### 交付物

- [ ] `src/agent/memory/models.py` - 记忆模型
- [ ] `src/agent/memory/short_term.py` - 短期记忆
- [ ] `src/agent/memory/long_term.py` - 长期记忆
- [ ] `src/agent/memory/semantic.py` - 语义记忆
- [ ] `src/agent/memory/consolidation.py` - 记忆巩固
- [ ] `tests/test_memory.py` - 测试用例

### 技术方案

```python
class MemorySystem:
    def __init__(self, agent_id):
        self.short_term = ShortTermMemory(capacity=100)
        self.long_term = LongTermMemory(agent_id)  # PostgreSQL
        self.semantic = SemanticMemory(agent_id)   # VectorDB
    
    async def remember(self, event):
        """存储记忆"""
        self.short_term.add(event)
        await self._consolidate()
    
    async def recall(self, query):
        """检索记忆"""
        semantic = await self.semantic.search(query)
        long_term = await self.long_term.query(query)
        return self._merge(semantic, long_term)
```

---

## 📋 Week 8: 代币智能合约

### 任务清单

| 任务 | 优先级 | 工时 | 状态 | 负责人 |
|------|--------|------|------|--------|
| **4.1 ERC20 合约编写** | P0 | 2d | ⬜ 待办 | - |
| **4.2 合约测试** | P0 | 1d | ⬜ 待办 | - |
| **4.3 部署脚本** | P0 | 1d | ⬜ 待办 | - |
| **4.4 Web3 集成** | P0 | 2d | ⬜ 待办 | - |
| **4.5 钱包集成** | P0 | 1d | ⬜ 待办 | - |
| **4.6 安全审计** | P0 | 1d | ⬜ 待办 | - |

### 交付物

- [ ] `src/blockchain/contracts/SILICONToken.sol` - 代币合约
- [ ] `src/blockchain/deploy.py` - 部署脚本
- [ ] `src/blockchain/web3_client.py` - Web3 客户端
- [ ] `tests/test_token.py` - 合约测试
- [ ] `docs/token-spec.md` - 代币规范

### 技术方案

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract SILICONToken is ERC20 {
    constructor() ERC20("SILICON", "SIL") {
        _mint(msg.sender, 1000000000 * 10 ** decimals());
    }
}
```

---

## 📋 Week 9-10: 基础 API

### 任务清单

| 任务 | 优先级 | 工时 | 状态 | 负责人 |
|------|--------|------|------|--------|
| **5.1 FastAPI 框架** | P0 | 1d | ⬜ 待办 | - |
| **5.2 身份 API** | P0 | 1d | ⬜ 待办 | - |
| **5.3 Agent API** | P0 | 2d | ⬜ 待办 | - |
| **5.4 记忆 API** | P0 | 1d | ⬜ 待办 | - |
| **5.5 代币 API** | P0 | 1d | ⬜ 待办 | - |
| **5.6 WebSocket 支持** | P0 | 1d | ⬜ 待办 | - |
| **5.7 API 文档** | P0 | 1d | ⬜ 待办 | - |
| **5.8 集成测试** | P0 | 1d | ⬜ 待办 | - |

### 交付物

- [ ] `src/api/main.py` - FastAPI 主应用
- [ ] `src/api/routes/identity.py` - 身份路由
- [ ] `src/api/routes/agent.py` - Agent 路由
- [ ] `src/api/routes/memory.py` - 记忆路由
- [ ] `src/api/routes/token.py` - 代币路由
- [ ] `docs/api.md` - API 文档
- [ ] `tests/test_api.py` - API 测试

### 技术方案

```python
from fastapi import FastAPI

app = FastAPI(
    title="硅基世界 API",
    description="Agent 与人类的虚拟世界",
    version="0.1.0"
)

@app.get("/api/v1/agents/{agent_id}")
async def get_agent(agent_id: str):
    """获取 Agent 信息"""
    ...

@app.post("/api/v1/agents")
async def create_agent(data: AgentCreate):
    """创建 Agent"""
    ...
```

---

## 📊 总体进度

```
Week 1-2:  [████████░░] 0%  DID 身份系统
Week 3-5:  [░░░░░░░░░░] 0%  Agent 核心框架
Week 6-7:  [░░░░░░░░░░] 0% 基础记忆系统
Week 8:    [░░░░░░░░░░] 0% 代币智能合约
Week 9-10: [░░░░░░░░░░] 0% 基础 API
```

---

## 🎯 里程碑

| 里程碑 | 预计日期 | 状态 |
|--------|----------|------|
| **M1: DID 系统完成** | 2026-03-21 | ⬜ 待完成 |
| **M2: Agent 核心完成** | 2026-04-11 | ⬜ 待完成 |
| **M3: 记忆系统完成** | 2026-04-25 | ⬜ 待完成 |
| **M4: 代币合约完成** | 2026-05-02 | ⬜ 待完成 |
| **M5: MVP 完成** | 2026-05-16 | ⬜ 待完成 |

---

## 🚀 立即开始

**今天任务 (Week 1 Day 1)**:

1. [ ] 技术选型确认
2. [ ] 搭建开发环境
3. [ ] 创建项目结构
4. [ ] 设计 DID 数据结构

---

**🐾 Phase 1 启动！开工！**
