# 🎉 硅基世界 - 本地测试环境已启动！

_启动时间：2026-03-08 14:41_

---

## ✅ 服务状态

| 服务 | 状态 | 地址 |
|------|------|------|
| API 服务 | 🟢 运行中 | http://localhost:8000 |
| API 文档 | 🟢 可用 | http://localhost:8000/docs |
| 数据库 | 🟢 SQLite | ./silicon_world.db |

---

## 🚀 立即开始使用

### 方式 1: 浏览器访问 (推荐)

打开 **http://localhost:8000/docs**

这是 Swagger UI，可以：
- ✅ 查看所有 API 接口
- ✅ 在线测试每个接口
- ✅ 查看请求/响应格式
- ✅ 无需写代码直接调用

### 方式 2: 直接调用 API

**创建 Agent:**
```bash
POST http://localhost:8000/api/v1/agents
Content-Type: application/json

{
  "name": "你的 Agent 名字",
  "controller": "你的钱包地址",
  "personality": {
    "type": "人格类型",
    "emoji": "🐾"
  }
}
```

**查询 Agent:**
```bash
GET http://localhost:8000/api/v1/agents/{agent_id}
```

**添加记忆:**
```bash
POST http://localhost:8000/api/v1/agents/{agent_id}/memories
Content-Type: application/json

{
  "content": "记忆内容",
  "memory_type": "short_term"
}
```

---

## 📋 可用 API 列表

### Agent 管理
- `POST /api/v1/agents` - 创建新 Agent
- `GET /api/v1/agents` - 获取 Agent 列表
- `GET /api/v1/agents/{id}` - 查询 Agent 详情
- `DELETE /api/v1/agents/{id}` - 删除 Agent
- `POST /api/v1/agents/{id}/memories` - 添加记忆
- `GET /api/v1/agents/{id}/memories` - 获取记忆列表

### DID 身份
- `POST /api/v1/did` - 创建去中心化身份
- `GET /api/v1/did/{did}` - 查询 DID 信息
- `POST /api/v1/did/{did}/verify` - 验证 DID

### 其他
- `GET /health` - 健康检查
- `GET /` - 根路径

---

## 💡 快速测试示例

### 1. 创建你的第一个 Agent
访问 http://localhost:8000/docs，找到 `POST /api/v1/agents`，点击 "Try it out"，填写：
```json
{
  "name": "测试 Agent",
  "controller": "0x你的地址",
  "personality": {
    "type": "友好",
    "emoji": "😊"
  }
}
```
点击 "Execute" 执行。

### 2. 查看创建的 Agent
复制返回的 `id`，然后访问 `GET /api/v1/agents/{id}`，粘贴 ID 执行。

### 3. 给 Agent 添加记忆
使用返回的 ID，访问 `POST /api/v1/agents/{id}/memories`：
```json
{
  "content": "今天第一次来到硅基世界",
  "memory_type": "short_term"
}
```

---

## 📁 项目文件

```
silicon-world/
├── src/
│   ├── api/          # API 路由
│   ├── core/         # 核心配置
│   ├── models/       # 数据模型
│   ├── services/     # 业务逻辑
│   └── blockchain/   # 智能合约
├── tests/            # 测试
├── docs/             # 文档
├── scripts/          # 部署脚本
├── .env              # 环境配置
└── silicon_world.db  # SQLite 数据库 (运行时生成)
```

---

## ⚠️ 注意事项

- ✅ 服务运行在本地，外部无法访问
- ✅ 数据存储在 `silicon_world.db` (SQLite)
- ✅ DEBUG 模式已开启，详细日志
- ⏸️ 如需停止服务，在运行窗口按 `Ctrl+C`

---

## 📝 下一步

1. **现在** → 打开 http://localhost:8000/docs 开始玩
2. **测试功能** → 创建 Agent、添加记忆、验证 DID
3. **验证完成后** → 部署到测试网 (公开访问)

---

## 🎯 测试网部署准备清单

当你准备好部署到测试网时，需要：

- [ ] 安装 Docker Desktop
- [ ] 注册 Infura (https://infura.io)
- [ ] 获取 Goerli 测试币 (https://goerlifaucet.com)
- [ ] 准备钱包私钥

详细步骤见 `QUICK_START.md`

---

**🐾 硅基世界已就绪，开始探索吧！**
