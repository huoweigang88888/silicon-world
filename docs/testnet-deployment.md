# 🚀 测试网部署指南

将硅基世界部署到测试网

---

## 📋 前置要求

- Python 3.11+
- Docker & Docker Compose
- Node.js 18+ (可选，用于合约部署)
- Infura/Alchemy API Key (用于区块链交互)

---

## 🔧 快速部署

### 1. 克隆项目

```bash
git clone https://github.com/huoweigang88888/silicon-world.git
cd silicon-world
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
# 网络配置
NETWORK=testnet

# 区块链配置
PRIVATE_KEY=your_private_key
INFURA_KEY=your_infura_key

# API 配置
API_HOST=0.0.0.0
API_PORT=8000

# 数据库配置
DATABASE_URL=postgresql://postgres:postgres@localhost/silicon_world
REDIS_URL=redis://localhost:6379
```

### 3. 运行部署脚本

```bash
# 设置环境变量
export NETWORK=testnet
export PRIVATE_KEY=your_private_key

# 运行部署
python scripts/deploy.py
```

### 4. 验证部署

```bash
# 健康检查
curl http://localhost:8000/health

# 查看 API 文档
open http://localhost:8000/docs
```

---

## 🐳 Docker 部署

### 使用 Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| API | 8000 | RESTful API |
| PostgreSQL | 5432 | 数据库 |
| Redis | 6379 | 缓存 |
| Qdrant | 6333 | 向量数据库 |

---

## ⛓️ 合约部署

### 使用 Hardhat

```bash
# 安装依赖
npm install

# 配置网络
# 编辑 hardhat.config.js

# 编译合约
npx hardhat compile

# 部署到测试网
npx hardhat run scripts/deploy.js --network goerli
```

### 合约地址

部署后记录合约地址：

```json
{
  "SILICONToken": "0x...",
  "WorldNFT": "0x...",
  "Marketplace": "0x..."
}
```

---

## 📊 监控和日志

### 查看日志

```bash
# API 日志
docker-compose logs api

# 数据库日志
docker-compose logs db

# 实时日志
docker-compose logs -f
```

### 健康检查

```bash
# API 健康
curl http://localhost:8000/health

# 数据库连接
docker-compose exec db psql -U postgres -c "SELECT 1"

# Redis 连接
docker-compose exec redis redis-cli ping
```

---

## 🔒 安全配置

### 防火墙

```bash
# 只开放必要端口
ufw allow 8000/tcp
ufw allow 443/tcp
ufw enable
```

### HTTPS 配置

使用 Nginx + Let's Encrypt:

```bash
# 安装 certbot
apt install certbot python3-certbot-nginx

# 获取证书
certbot --nginx -d api.silicon.world
```

---

## 📈 性能优化

### 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_agents_id ON agents(id);
CREATE INDEX idx_memories_agent_id ON memories(agent_id);

-- 分析表
ANALYZE agents;
ANALYZE memories;
```

### Redis 缓存

```python
# 配置缓存
REDIS_URL=redis://localhost:6379
CACHE_TTL=300  # 5 分钟
```

---

## 🐛 故障排查

### API 无法启动

```bash
# 检查端口占用
lsof -i :8000

# 查看日志
docker-compose logs api

# 重启服务
docker-compose restart api
```

### 数据库连接失败

```bash
# 检查数据库状态
docker-compose ps db

# 查看数据库日志
docker-compose logs db

# 重启数据库
docker-compose restart db
```

### 合约部署失败

```bash
# 检查余额
# 确保账户有足够的测试币

# 检查 RPC 连接
# 确认 Infura/Alchemy Key 有效

# 增加 Gas
# 编辑 hardhat.config.js 增加 gas 配置
```

---

## 📞 获取帮助

- **文档**: https://github.com/huoweigang88888/silicon-world/docs
- **Issues**: https://github.com/huoweigang88888/silicon-world/issues
- **Discord**: (待创建)

---

**🐾 部署完成，开始构建硅基世界！**
