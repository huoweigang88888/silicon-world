# ⚡ 性能优化指南

硅基世界性能优化最佳实践

---

## 📊 性能目标

| 指标 | 目标值 | 当前值 |
|------|--------|--------|
| API 响应时间 | < 200ms | ~100ms |
| 数据库查询 | < 50ms | ~30ms |
| 页面加载 | < 2s | ~1.5s |
| 并发用户 | 10,000+ | 待测试 |
| 系统可用性 | > 99.9% | 待验证 |

---

## 🚀 优化策略

### 1. 缓存优化

#### 内存缓存
```python
from src.optimization.cache import CacheManager

cache = CacheManager()

# 设置缓存
cache.set("user:123", user_data, ttl_seconds=300)

# 获取缓存
user = cache.get("user:123")
```

#### Redis 缓存
```bash
# 配置 Redis
REDIS_URL=redis://localhost:6379
CACHE_TTL=300
```

### 2. 数据库优化

#### 添加索引
```sql
-- Agent 表
CREATE INDEX idx_agents_id ON agents(id);
CREATE INDEX idx_agents_name ON agents(name);
CREATE INDEX idx_agents_created_at ON agents(created_at);

-- 记忆表
CREATE INDEX idx_memories_agent_id ON memories(agent_id);
CREATE INDEX idx_memories_type ON memories(memory_type);

-- 交易表
CREATE INDEX idx_transactions_from ON transactions(from_address);
CREATE INDEX idx_transactions_to ON transactions(to_address);
```

#### 查询优化
```python
# 使用分页
results = query.offset(offset).limit(page_size)

# 批量操作
batches = QueryOptimizer.optimize_batch_operations(operations, batch_size=100)
```

### 3. API 优化

#### 响应压缩
```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

#### 异步处理
```python
@app.post("/api/v1/heavy-task")
async def heavy_task():
    # 使用后台任务
    background_tasks.add_task(process_heavy_data)
    return {"status": "processing"}
```

### 4. 前端优化

#### 懒加载
```html
<img src="placeholder.jpg" data-src="actual.jpg" loading="lazy">
```

#### 资源压缩
```bash
# 压缩图片
imagemin images/* --out-dir=images-optimized

# 压缩 CSS/JS
cssnano input.css output.css
terser input.js -o output.js
```

---

## 📈 性能监控

### 监控指标

```python
from src.optimization.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor()

# 记录指标
monitor.record_metric("api_response_time", response_time)
monitor.record_metric("db_query_time", query_time)

# 获取仪表板
dashboard = monitor.get_dashboard()
```

### 告警配置

```python
# 设置阈值
monitor.thresholds = {
    "api_response_time": 200,
    "db_query_time": 50,
    "error_rate": 1
}
```

---

## 🔧 优化检查清单

### 后端优化
- [ ] 启用数据库连接池
- [ ] 配置 Redis 缓存
- [ ] 添加数据库索引
- [ ] 优化慢查询
- [ ] 启用 Gzip 压缩
- [ ] 使用异步处理
- [ ] 配置 CDN

### 前端优化
- [ ] 启用资源压缩
- [ ] 配置懒加载
- [ ] 优化图片大小
- [ ] 使用 CDN
- [ ] 减少 HTTP 请求
- [ ] 启用浏览器缓存

### 数据库优化
- [ ] 分析慢查询日志
- [ ] 优化表结构
- [ ] 配置读写分离
- [ ] 定期清理数据
- [ ] 监控连接数

---

## 📊 性能测试

### 负载测试

```bash
# 使用 ab 测试
ab -n 10000 -c 100 http://localhost:8000/health

# 使用 wrk 测试
wrk -t12 -c400 -d30s http://localhost:8000/api/v1/agents
```

### 压力测试

```bash
# 使用 locust
locust -f locustfile.py --host=http://localhost:8000
```

---

## 🐛 常见问题排查

### API 响应慢

1. 检查数据库查询
2. 检查缓存命中率
3. 检查外部 API 调用
4. 检查网络延迟

### 内存占用高

1. 检查内存泄漏
2. 优化数据结构
3. 清理缓存
4. 增加内存限制

### 数据库慢

1. 分析慢查询日志
2. 添加索引
3. 优化查询语句
4. 考虑分库分表

---

## 📞 获取帮助

- **文档**: https://github.com/huoweigang88888/silicon-world/docs
- **Issues**: https://github.com/huoweigang88888/silicon-world/issues

---

**⚡ 持续优化，追求卓越性能！**
