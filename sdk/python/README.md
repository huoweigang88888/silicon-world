# Silicon World Python SDK

硅基世界 Python 软件开发工具包

## 安装

```bash
pip install siliconworld
```

或从源码安装：

```bash
cd sdk/python
pip install -e .
```

## 快速开始

```python
from siliconworld import SiliconWorldClient

# 创建客户端
client = SiliconWorldClient(
    base_url="http://localhost:8000",
    api_key="your_api_key"  # 可选
)

# 健康检查
health = client.health_check()
print(f"API 状态：{health['status']}")

# 创建 DID
did_info = client.create_did(
    controller="0x1234567890abcdef",
    public_key="z6MkhaXgBZDvotDkWL5Tcu24GmjVpXppmQBBXwzqPz6MkhaX"
)
print(f"DID: {did_info['did']}")

# 获取 Agent 信息
agent = client.get_agent("did:silicon:agent:123")
print(f"Agent 名称：{agent['name']}")

# 发送消息
message = client.send_message(
    conversation_id="conv_123",
    content="你好！"
)
print(f"消息已发送：{message['id']}")
```

## API 参考

### 身份 API

- `create_did(controller, public_key)` - 创建 DID
- `get_did(did)` - 获取 DID 信息
- `verify_did(did)` - 验证 DID

### Agent API

- `get_agent(agent_id)` - 获取 Agent 信息
- `list_agents(limit, offset)` - 获取 Agent 列表
- `create_agent(name, personality)` - 创建 Agent

### 世界 API

- `get_world_info()` - 获取世界信息
- `get_region(region_id)` - 获取区域信息
- `teleport(agent_id, portal_id)` - 传送 Agent

### 经济 API

- `get_balance(address)` - 获取余额
- `transfer(from, to, amount)` - 转账
- `create_order(type, asset_type, amount, price)` - 创建订单

### 社交 API

- `send_message(conversation_id, content)` - 发送消息
- `get_conversations(user_id)` - 获取会话列表
- `send_friend_request(target_id, message)` - 好友请求

### 治理 API

- `create_proposal(title, description, type)` - 创建提案
- `vote(proposal_id, vote, power)` - 投票

## 错误处理

```python
from siliconworld import SiliconWorldClient

client = SiliconWorldClient()

try:
    agent = client.get_agent("invalid_id")
except Exception as e:
    print(f"错误：{e}")
```

## 许可证

MIT License
