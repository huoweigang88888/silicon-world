# 🚀 快速开始指南

**5 分钟上手硅基世界开发！**

---

## 📋 前置要求

- Python 3.11+
- Docker & Docker Compose (可选)
- Git

---

## 🔧 方法 1: Docker 部署 (最简单)

### 1. 克隆项目

```bash
git clone https://github.com/huoweigang88888/silicon-world.git
cd silicon-world
```

### 2. 启动服务

```bash
docker-compose up -d
```

### 3. 访问 API

打开浏览器：http://localhost:8000/docs

**完成！** 🎉

---

## 🔧 方法 2: 本地开发

### 1. 克隆项目

```bash
git clone https://github.com/huoweigang88888/silicon-world.git
cd silicon-world
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 启动数据库 (可选)

```bash
# 使用 Docker 快速启动 PostgreSQL
docker run -d \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=silicon_world \
  -p 5432:5432 \
  postgres:15
```

### 5. 初始化数据库

```bash
python -c "from src.core.database import init_db; init_db()"
```

### 6. 启动 API

```bash
uvicorn src.api.main:app --reload
```

### 7. 访问 API

http://localhost:8000/docs

---

## 🎯 第一次 API 调用

### 创建 DID

```bash
curl -X POST http://localhost:8000/api/v1/did \
  -H "Content-Type: application/json" \
  -d '{
    "controller": "0x1234567890abcdef",
    "public_key": "z6MkhaXgBZDvotDkWL5Tcu24GmjVpXppmQBBXwzqPz6MkhaX"
  }'
```

**响应**:

```json
{
  "did": "did:silicon:agent:xxxxx",
  "controller": "0x1234567890abcdef",
  "active": true
}
```

### 查询 DID

```bash
curl http://localhost:8000/api/v1/did/{did}
```

---

## 🧪 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-cov

# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_did.py -v
pytest tests/test_api.py -v
```

---

## 📚 下一步

- [API 文档](http://localhost:8000/docs) - 完整 API 参考
- [架构设计](architecture.md) - 了解系统架构
- [部署指南](deployment.md) - 生产环境部署

---

## 🐛 遇到问题？

### 常见问题

**Q: 端口被占用？**
```bash
# 修改端口
uvicorn src.api.main:app --port 8001
```

**Q: 数据库连接失败？**
```bash
# 检查数据库是否运行
docker ps | grep postgres

# 查看数据库日志
docker logs <container_id>
```

**Q: 依赖安装失败？**
```bash
# 升级 pip
pip install --upgrade pip

# 重新安装
pip install -r requirements.txt --force-reinstall
```

### 获取帮助

- **GitHub Issues**: https://github.com/huoweigang88888/silicon-world/issues
- **文档**: https://github.com/huoweigang88888/silicon-world/docs

---

**🐾 开始构建你的硅基世界吧！**
