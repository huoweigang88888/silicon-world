# 🤖 硅基世界 - Agent 接入指南

_版本：1.0 | 更新时间：2026-03-08_

---

## 📋 两种接入方式

### 方式 1: 原生 Agent (在硅基世界注册)

**适合**:
- 新建的 AI Agent
- 使用硅基世界记忆系统
- 不需要外部连接

**特点**:
- ✅ 简单快速
- ✅ 内置记忆管理
- ✅ 完整 Dashboard 支持
- ⏸️ 需要自己实现 Agent 逻辑

---

### 方式 2: 外部 Agent (已有 Agent 接入)

**适合**:
- 微信机器人
- Discord Bot
- 本地运行的 AI (Ollama 等)
- 云端 API (OpenAI Assistant 等)
- 其他平台的 Agent

**特点**:
- ✅ 保留现有系统
- ✅ 使用硅基世界记忆
- ✅ 统一管理多个 Agent
- ✅ 连接测试和监控

---

## 🚀 接入步骤

### 步骤 1: 打开 Dashboard

浏览器访问：**http://localhost:3000**

---

### 步骤 2: 创建 Agent

点击 **"➕ 创建 Agent"**

---

### 步骤 3: 填写信息

#### 原生 Agent

| 字段 | 说明 | 示例 |
|------|------|------|
| 名字 | Agent 名称 | 硅基助手 |
| 控制者地址 | 你的钱包地址 | 0x1234567890... |
| Agent 类型 | 选择"原生" | native |
| 人格类型 | 性格设定 | 友好/专业/创意 |

#### 外部 Agent

| 字段 | 说明 | 示例 |
|------|------|------|
| 名字 | Agent 名称 | 微信助手 |
| 控制者地址 | 你的钱包地址 | 0x1234567890... |
| Agent 类型 | 选择"外部" | external |
| API 端点 | Agent 的 API 地址 | https://bot.com/api |
| 认证类型 | 认证方式 | Bearer/Basic/None |
| 认证凭证 | Token 或密码 | your_token_here |
| 人格类型 | 性格设定 | 友好 |

---

### 步骤 4: 测试连接 (仅外部 Agent)

1. 创建完成后，点击 Agent
2. 点击 **"🔌 测试连接"**
3. 查看结果：
   - ✅ 在线 - 连接成功
   - ⚪ 离线 - 无法连接
   - ❌ 错误 - 配置错误

---

### 步骤 5: 开始使用

- 💭 查看记忆
- 🔍 搜索记忆
- 📊 查看统计
- ⚙️ 管理配置

---

## 📋 常见场景配置

### 场景 1: 微信机器人

```json
{
  "name": "微信助手",
  "controller": "0x 你的地址",
  "agent_type": "external",
  "connection_info": {
    "endpoint": "https://your-wechat-bot.com/api",
    "auth_type": "bearer",
    "auth": "your_wechat_token"
  },
  "capabilities": ["chat", "image_recognition", "schedule"]
}
```

---

### 场景 2: 本地 Ollama

```json
{
  "name": "本地 Ollama",
  "controller": "0x 你的地址",
  "agent_type": "external",
  "connection_info": {
    "endpoint": "http://localhost:11434/api/generate",
    "auth_type": "none"
  },
  "capabilities": ["chat", "text_generation"]
}
```

---

### 场景 3: Discord Bot

```json
{
  "name": "Discord 助手",
  "controller": "0x 你的地址",
  "agent_type": "external",
  "connection_info": {
    "endpoint": "https://discord-bot.example.com/api",
    "auth_type": "bearer",
    "auth": "discord_bot_token"
  },
  "capabilities": ["chat", "moderation", "music"]
}
```

---

### 场景 4: OpenAI Assistant

```json
{
  "name": "GPT 助手",
  "controller": "0x 你的地址",
  "agent_type": "external",
  "connection_info": {
    "endpoint": "https://api.openai.com/v1/assistants",
    "auth_type": "bearer",
    "auth": "sk-openai-api-key"
  },
  "capabilities": ["chat", "code", "analysis"]
}
```

---

## 🔧 API 调用

### 测试连接

```bash
POST http://localhost:8000/api/v1/agents/{agent_id}/test-connection
```

**响应:**
```json
{
  "success": true,
  "message": "连接成功",
  "status_code": 200
}
```

---

### 调用 Agent

```bash
POST http://localhost:8000/api/v1/agents/{agent_id}/invoke
{
  "action": "chat",
  "input_data": {
    "message": "你好"
  }
}
```

---

### 获取状态

```bash
GET http://localhost:8000/api/v1/agents/{agent_id}/status
```

**响应:**
```json
{
  "agent_id": "did:silicon:agent:xxx",
  "name": "微信助手",
  "agent_type": "external",
  "status": "online",
  "active": true,
  "last_seen": "2026-03-08T10:20:00Z"
}
```

---

## ❓ 常见问题

### Q: 原生和外部有什么区别？

**A:** 
- **原生**: Agent 运行在硅基世界，使用内置逻辑
- **外部**: Agent 运行在外部，硅基世界只管理身份和记忆

---

### Q: 外部 Agent 必须一直在线吗？

**A:** 不是必须，但：
- 在线时可以测试连接和调用
- 离线时仍然可以存储记忆
- 状态会显示最后在线时间

---

### Q: 如何保证安全？

**A:** 
1. Token 存储在数据库中
2. 使用 HTTPS 加密传输
3. 建议定期更换 Token
4. 不要分享私钥

---

### Q: 可以接入多少个 Agent？

**A:** 无限制！可以接入任意数量的 Agent。

---

## 📊 状态说明

| 状态 | 说明 | 如何处理 |
|------|------|----------|
| ✅ online | 在线 | 正常使用 |
| ⚪ offline | 离线 | 检查网络 |
| ❌ error | 错误 | 检查配置 |
| ❓ unknown | 未知 | 测试连接 |

---

## 🎯 下一步

1. **创建你的第一个 Agent**
2. **测试连接**
3. **开始存储记忆**
4. **享受统一管理**

---

**🐾 开始接入你的 Agent 吧！**

**Dashboard**: http://localhost:3000  
**API 文档**: http://localhost:8000/docs
