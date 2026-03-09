# 🔌 A2A 协议集成方案

_基于 Google 的 Agent-to-Agent (A2A) 协议_

_创建时间：2026-03-09 08:35_

---

## 📋 项目概述

### 什么是 A2A 协议？

**A2A (Agent-to-Agent Protocol)** 是 Google 推出的开放协议，用于：
- 🤖 Agent 之间的发现和通信
- 📋 标准化的任务管理
- 🔄 实时状态跟踪
- 💬 支持流式响应

**官方项目**:
- [python-a2a](https://github.com/themanojdesai/python-a2a) - Python 实现 (881⭐)
- [a2a-x402](https://github.com/google-agentic-commerce/a2a-x402) - 支付扩展 (463⭐)
- [OpenClaw A2A Gateway](https://github.com/win4r/openclaw-a2a-gateway) - OpenClaw 集成 (89⭐)

---

## 🎯 集成价值

### 对硅基世界的价值

1. **标准化通信** - 与其他 AI Agent 互操作
2. **扩大生态** - 接入 Google Agent 生态
3. **降低集成成本** - 使用标准协议
4. **支付能力** - 通过 x402 实现 Agent 经济

### 与现有功能结合

| 现有功能 | A2A 增强 |
|---------|---------|
| Agent 管理 | 支持外部 A2A Agent |
| 社交系统 | 标准化的 Agent 通信 |
| 经济系统 | x402 支付协议 |
| WebSocket | A2A 流式响应 |

---

## 🏗️ 架构设计

### 集成架构

```
┌─────────────────────────────────────┐
│      硅基世界 Dashboard              │
│      http://localhost:3000          │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│      硅基世界 API (FastAPI)          │
│      http://localhost:8000          │
├─────────────────────────────────────┤
│  Agent 管理  │  社交  │  A2A Gateway │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│    OpenClaw A2A Gateway             │
│    (双向 Agent 通信)                  │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│    外部 A2A Agent (Google 生态)       │
│    - 其他 AI 助手                       │
│    - 第三方 Agent 服务                 │
└─────────────────────────────────────┘
```

### 模块划分

```
src/
├── a2a/                          # A2A 协议集成
│   ├── __init__.py
│   ├── client.py                 # A2A 客户端
│   ├── server.py                 # A2A 服务端
│   ├── models.py                 # A2A 数据模型
│   └── x402/                     # x402 支付扩展
│       ├── __init__.py
│       ├── payment.py            # 支付处理
│       └── models.py             # 支付模型
│
├── api/
│   └── routes/
│       └── a2a.py                # A2A API 路由
```

---

## 📦 依赖安装

```bash
# A2A Python 库
pip install a2a

# x402 支付扩展
pip install a2a-x402

# 或使用 requirements
echo "a2a>=0.3.0" >> requirements.txt
echo "a2a-x402>=0.1.0" >> requirements.txt
```

---

## 🔧 实现步骤

### 步骤 1: 创建 A2A 客户端

```python
# src/a2a/client.py

from a2a.client import A2AClient
from a2a.models import AgentCard, Task, Message
from typing import Optional, List

class SiliconWorldA2AClient:
    """硅基世界 A2A 客户端"""
    
    def __init__(self, server_url: str = None):
        """
        初始化 A2A 客户端
        
        Args:
            server_url: A2A 服务器 URL
        """
        self.server_url = server_url
        self.client = A2AClient(server_url=server_url) if server_url else None
        self.agent_card: Optional[AgentCard] = None
    
    async def discover_agent(self, agent_url: str) -> Optional[AgentCard]:
        """
        发现 Agent
        
        Args:
            agent_url: Agent 的 .well-known/agent-card.json URL
            
        Returns:
            AgentCard 对象
        """
        try:
            card = await self.client.get_agent_card(agent_url)
            return card
        except Exception as e:
            print(f"发现 Agent 失败：{e}")
            return None
    
    async def send_message(self, agent_url: str, message: str) -> str:
        """
        发送消息给 Agent
        
        Args:
            agent_url: Agent URL
            message: 消息内容
            
        Returns:
            Agent 响应
        """
        try:
            response = await self.client.send_message(
                url=agent_url,
                message=message
            )
            return response.text
        except Exception as e:
            print(f"发送消息失败：{e}")
            return f"错误：{str(e)}"
    
    async def create_task(self, agent_url: str, task_description: str) -> Task:
        """
        创建任务
        
        Args:
            agent_url: Agent URL
            task_description: 任务描述
            
        Returns:
            Task 对象
        """
        try:
            task = await self.client.create_task(
                url=agent_url,
                description=task_description
            )
            return task
        except Exception as e:
            print(f"创建任务失败：{e}")
            raise
```

---

### 步骤 2: 创建 A2A 服务端

```python
# src/a2a/server.py

from a2a.server import A2AServer
from a2a.models import AgentCard, Task, Message, TaskStatus
from typing import Dict, List
import uuid

class SiliconWorldA2AServer:
    """硅基世界 A2A 服务端"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        """
        初始化 A2A 服务端
        
        Args:
            host: 监听地址
            port: 监听端口
        """
        self.host = host
        self.port = port
        self.server = A2AServer(host=host, port=port)
        
        # 注册 Agent Card
        self.agent_card = AgentCard(
            name="硅基世界 Agent",
            description="硅基世界的 AI Agent，支持社交、记忆、任务管理",
            url="http://localhost:8000",
            version="1.0.0",
            capabilities=[
                "chat",
                "memory",
                "social",
                "task_management"
            ],
            provider={
                "organization": "Silicon World",
                "url": "https://github.com/huoweigang88888/silicon-world"
            }
        )
        
        # 任务存储
        self.tasks: Dict[str, Task] = {}
        
        # 注册处理函数
        self._register_handlers()
    
    def _register_handlers(self):
        """注册 A2A 处理函数"""
        
        @self.server.on_message()
        async def handle_message(message: Message) -> Message:
            """处理消息"""
            # 调用硅基世界的消息处理逻辑
            from src.social.models import MessageModel
            # ... 处理逻辑
            
            response_text = f"收到消息：{message.text}"
            return Message(text=response_text)
        
        @self.server.on_task_create()
        async def handle_task_create(task: Task) -> Task:
            """处理任务创建"""
            # 保存任务
            task.id = str(uuid.uuid4())
            task.status = TaskStatus.SUBMITTED
            self.tasks[task.id] = task
            
            # 异步执行任务
            # ... 任务执行逻辑
            
            return task
        
        @self.server.on_task_get()
        async def handle_task_get(task_id: str) -> Task:
            """获取任务状态"""
            task = self.tasks.get(task_id)
            if not task:
                raise ValueError(f"任务不存在：{task_id}")
            return task
    
    async def start(self):
        """启动 A2A 服务端"""
        print(f"[A2A] 启动服务端：http://{self.host}:{self.port}")
        await self.server.serve()
```

---

### 步骤 3: 创建 API 路由

```python
# src/api/routes/a2a.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.a2a.client import SiliconWorldA2AClient

router = APIRouter(tags=["A2A"])

# 全局 A2A 客户端
a2a_client = SiliconWorldA2AClient()


class AgentDiscoveryRequest(BaseModel):
    """Agent 发现请求"""
    agent_url: str


class AgentCardResponse(BaseModel):
    """Agent Card 响应"""
    name: str
    description: str
    url: str
    version: str
    capabilities: List[str]


class A2AMessageRequest(BaseModel):
    """A2A 消息请求"""
    agent_url: str
    message: str


class A2AMessageResponse(BaseModel):
    """A2A 消息响应"""
    response: str
    success: bool


class TaskCreateRequest(BaseModel):
    """任务创建请求"""
    agent_url: str
    description: str
    task_type: Optional[str] = "general"


@router.post("/api/v1/a2a/discover", response_model=AgentCardResponse)
async def discover_agent(request: AgentDiscoveryRequest):
    """
    发现 A2A Agent
    
    - **agent_url**: Agent 的 URL
    """
    try:
        card = await a2a_client.discover_agent(request.agent_url)
        if not card:
            raise HTTPException(status_code=404, detail="Agent 未找到")
        
        return AgentCardResponse(
            name=card.name,
            description=card.description,
            url=card.url,
            version=card.version,
            capabilities=card.capabilities
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/a2a/send-message", response_model=A2AMessageResponse)
async def send_a2a_message(request: A2AMessageRequest):
    """
    发送 A2A 消息
    
    - **agent_url**: 目标 Agent URL
    - **message**: 消息内容
    """
    try:
        response = await a2a_client.send_message(
            agent_url=request.agent_url,
            message=request.message
        )
        
        return A2AMessageResponse(
            response=response,
            success=True
        )
    except Exception as e:
        return A2AMessageResponse(
            response=f"错误：{str(e)}",
            success=False
        )


@router.post("/api/v1/a2a/create-task")
async def create_a2a_task(request: TaskCreateRequest):
    """
    创建 A2A 任务
    
    - **agent_url**: 目标 Agent URL
    - **description**: 任务描述
    - **task_type**: 任务类型
    """
    try:
        task = await a2a_client.create_task(
            agent_url=request.agent_url,
            task_description=request.description
        )
        
        return {
            "success": True,
            "task_id": task.id,
            "status": task.status.value
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/a2a/task/{task_id}")
async def get_task_status(task_id: str):
    """
    获取任务状态
    
    - **task_id**: 任务 ID
    """
    # TODO: 实现任务状态查询
    return {
        "task_id": task_id,
        "status": "unknown"
    }
```

---

### 步骤 4: 注册路由

```python
# src/api/main.py

# 添加 A2A 路由
from src.api.routes.a2a import router as a2a_router

# 注册路由
app.include_router(a2a_router)
```

---

## 💰 x402 支付集成

### 什么是 x402？

**x402** 是 A2A 协议的支付扩展，基于 HTTP 402 "Payment Required" 状态码。

**工作流程**:
1. Agent 提供服务，需要收费
2. 客户端请求服务
3. Agent 返回 402 + 支付要求
4. 客户端支付（加密货币）
5. Agent 验证支付，提供服务

### 集成 x402

```python
# src/a2a/x402/payment.py

from a2a_x402 import X402Payment
from typing import Optional, Dict

class SiliconWorldPayment:
    """硅基世界支付处理器"""
    
    def __init__(self, wallet_address: str):
        """
        初始化支付处理器
        
        Args:
            wallet_address: 收款钱包地址
        """
        self.wallet_address = wallet_address
        self.payment = X402Payment(wallet_address)
    
    async def create_payment_request(
        self,
        amount: float,
        currency: str = "USD",
        description: str = "Agent service payment"
    ) -> Dict:
        """
        创建支付请求
        
        Args:
            amount: 金额
            currency: 货币类型
            description: 描述
            
        Returns:
            支付请求信息
        """
        payment_request = await self.payment.create_request(
            amount=amount,
            currency=currency,
            description=description
        )
        
        return {
            "payment_url": payment_request.url,
            "amount": amount,
            "currency": currency,
            "description": description,
            "expires_at": payment_request.expires_at
        }
    
    async def verify_payment(self, payment_proof: str) -> bool:
        """
        验证支付
        
        Args:
            payment_proof: 支付证明
            
        Returns:
            是否支付成功
        """
        is_valid = await self.payment.verify(payment_proof)
        return is_valid
```

---

## 🧪 测试方案

### 测试 A2A 客户端

```python
# tests/test_a2a.py

import pytest
from src.a2a.client import SiliconWorldA2AClient

@pytest.mark.asyncio
async def test_discover_agent():
    """测试 Agent 发现"""
    client = SiliconWorldA2AClient()
    card = await client.discover_agent("http://example-agent.com")
    assert card is not None
    assert card.name == "Example Agent"

@pytest.mark.asyncio
async def test_send_message():
    """测试发送消息"""
    client = SiliconWorldA2AClient()
    response = await client.send_message(
        agent_url="http://example-agent.com",
        message="Hello"
    )
    assert "Hello" in response or "收到" in response
```

---

## 📊 实施计划

### Phase 1: 基础集成 (1-2 天)

- [ ] 安装 A2A 依赖
- [ ] 创建 A2A 客户端
- [ ] 创建 A2A 服务端
- [ ] 添加 API 路由
- [ ] 基础测试

### Phase 2: x402 支付 (2-3 天)

- [ ] 研究 x402 协议
- [ ] 集成支付功能
- [ ] 与 NexusA 钱包对接
- [ ] 支付流程测试

### Phase 3: 功能完善 (3-5 天)

- [ ] 支持流式响应
- [ ] 任务管理完善
- [ ] 错误处理优化
- [ ] 性能优化
- [ ] 文档完善

---

## 🎯 预期效果

### 集成后能力

1. **Agent 发现** - 发现并连接其他 A2A Agent
2. **消息通信** - 与其他 Agent 实时通信
3. **任务协作** - 创建和跟踪跨 Agent 任务
4. **支付能力** - Agent 可以有偿服务

### 使用场景

**场景 1: Agent 协作**
```
用户 → 硅基世界 Agent → A2A → 翻译 Agent → 翻译结果
```

**场景 2: 付费咨询**
```
用户 → 硅基世界 Agent → A2A x402 → 专家 Agent → 付费 → 专业建议
```

**场景 3: 任务分发**
```
用户 → 硅基世界 Agent → A2A → 多个专业 Agent → 汇总结果
```

---

## 📞 参考资源

- **A2A 官方文档**: https://google.github.io/A2A/
- **Python A2A**: https://github.com/themanojdesai/python-a2a
- **A2A x402**: https://github.com/google-agentic-commerce/a2a-x402
- **OpenClaw Gateway**: https://github.com/win4r/openclaw-a2a-gateway

---

**🐾 硅基世界 + A2A = 无限可能！**

_创建时间：2026-03-09 08:35_
