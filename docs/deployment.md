# 🚀 硅基世界 - 部署指南

---

## 📋 前置要求

- Docker & Docker Compose
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

---

## 🐳 Docker 部署 (推荐)

### 1. 启动所有服务

```bash
docker-compose up -d
```

### 2. 检查服务状态

```bash
docker-compose ps
```

应该看到：
- api (运行中)
- db (运行中)
- redis (运行中)
- qdrant (运行中)

### 3. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看 API 日志
docker-compose logs -f api
```

### 4. 访问 API 文档

打开浏览器访问：http://localhost:8000/docs

### 5. 停止服务

```bash
docker-compose down
```

---

## 💻 本地开发部署

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动数据库

```bash
# 使用 Docker 启动 PostgreSQL
docker run -d \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=silicon_world \
  -p 5432:5432 \
  postgres:15
```

### 3. 初始化数据库

```bash
cd silicon-world
python -c "from src.core.database import init_db; init_db()"
```

### 4. 启动 API 服务

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问 API 文档

http://localhost:8000/docs

---

## ☁️ 生产环境部署

### 1. 配置环境变量

创建 `.env` 文件：

```bash
# 数据库
DATABASE_URL=postgresql://user:password@host:5432/silicon_world

# Redis
REDIS_URL=redis://host:6379

# 区块链
WEB3_RPC_URL=https://mainnet.infura.io/v3/YOUR_KEY

# API
API_HOST=0.0.0.0
API_PORT=8000
```

### 2. 使用 Kubernetes 部署

```bash
# 创建命名空间
kubectl create namespace silicon-world

# 部署应用
kubectl apply -f k8s/

# 检查状态
kubectl get pods -n silicon-world
```

### 3. 配置 Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: silicon-world
  namespace: silicon-world
spec:
  rules:
  - host: api.silicon.world
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8000
```

---

## 📊 监控和日志

### 1. Prometheus 监控

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'silicon-world'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
```

### 2. Grafana 仪表板

导入仪表板 ID: `10956` (FastAPI 监控)

### 3. 日志收集

使用 ELK Stack:
- Elasticsearch: 存储日志
- Logstash: 处理日志
- Kibana: 可视化

---

## 🔒 安全配置

### 1. HTTPS 配置

使用 Let's Encrypt:

```bash
certbot --nginx -d api.silicon.world
```

### 2. 防火墙规则

```bash
# 只开放必要端口
ufw allow 8000/tcp
ufw allow 443/tcp
ufw enable
```

### 3. 数据库安全

```sql
-- 创建只读用户
CREATE USER readonly WITH PASSWORD 'password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
```

---

## 📈 性能优化

### 1. 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_agents_id ON agents(id);
CREATE INDEX idx_memories_agent_id ON memories(agent_id);
CREATE INDEX idx_memories_type ON memories(memory_type);
```

### 2. Redis 缓存

```python
# 缓存热点数据
@cache(ttl=300)
async def get_agent(did: str):
    ...
```

### 3. 异步处理

```python
# 使用 Celery 处理耗时任务
@app.post("/api/v1/agents")
async def create_agent(data: AgentCreate):
    task = create_agent_task.delay(data)
    return {"task_id": task.id}
```

---

## 🐛 故障排查

### 1. 数据库连接失败

```bash
# 检查数据库是否运行
docker-compose ps db

# 查看数据库日志
docker-compose logs db
```

### 2. API 无法启动

```bash
# 检查端口占用
lsof -i :8000

# 查看 API 日志
docker-compose logs api
```

### 3. 内存不足

```bash
# 查看资源使用
docker stats

# 限制容器内存
docker-compose up --memory="2g"
```

---

## 📞 获取帮助

- **文档**: https://github.com/huoweigang88888/silicon-world/docs
- **Issues**: https://github.com/huoweigang88888/silicon-world/issues
- **Discord**: (待创建)

---

**🐾 部署完成，开始构建硅基世界！**
