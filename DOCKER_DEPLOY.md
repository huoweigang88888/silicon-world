# 🐳 硅基世界 - Docker 部署指南

_使用 Docker 快速部署硅基世界_

---

## 📋 前提条件

- Docker 20.10+
- Docker Compose 2.0+

---

## 🚀 快速开始

### 方法 1: Docker Compose (推荐)

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

**访问地址**:
- API: http://localhost:8000
- Dashboard: http://localhost:3000
- Redis: localhost:6379

---

### 方法 2: 单独构建 API

```bash
# 构建镜像
docker build -t silicon-world .

# 运行容器
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/silicon_world.db:/app/silicon_world.db \
  -v $(pwd)/uploads:/app/uploads \
  --name silicon-api \
  silicon-world
```

---

## 🔧 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| DATABASE_URL | 数据库 URL | sqlite:///./silicon_world.db |
| API_HOST | API 监听地址 | 0.0.0.0 |
| API_PORT | API 端口 | 8000 |
| REDIS_URL | Redis URL | redis://localhost:6379 |

### 数据卷

| 路径 | 说明 |
|------|------|
| ./silicon_world.db | SQLite 数据库 |
| ./uploads | 上传文件存储 |
| redis-data | Redis 数据 |

---

## 📊 服务说明

### API 服务

- **端口**: 8000
- **镜像**: 基于 python:3.13-slim
- **功能**: 提供所有 API 端点

### Dashboard

- **端口**: 3000
- **镜像**: nginx:alpine
- **功能**: 前端管理界面

### Redis (可选)

- **端口**: 6379
- **镜像**: redis:7-alpine
- **功能**: 缓存层

---

## 🔍 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看 API 日志
docker-compose logs api

# 重启 API 服务
docker-compose restart api

# 进入 API 容器
docker-compose exec api bash

# 备份数据库
docker-compose exec api cp silicon_world.db /tmp/backup.db
docker-compose cp api:/tmp/backup.db ./backup.db

# 恢复数据库
docker-compose cp ./backup.db api:/app/silicon_world.db
docker-compose restart api
```

---

## 🎯 生产环境部署

### 1. 配置 HTTPS

使用 Nginx 反向代理：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:3000;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

### 2. 配置域名

修改 docker-compose.yml：

```yaml
services:
  api:
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
```

### 3. 持久化数据

确保数据卷正确挂载：

```yaml
volumes:
  - ./data:/app/data
  - ./uploads:/app/uploads
```

---

## ❓ 故障排除

### Q: 容器启动失败？

A: 查看日志：
```bash
docker-compose logs api
```

### Q: 数据库无法写入？

A: 检查文件权限：
```bash
chmod 666 silicon_world.db
```

### Q: 无法访问 Dashboard？

A: 检查端口是否被占用：
```bash
netstat -tlnp | grep 3000
```

---

## 📞 更多信息

- **API 文档**: http://localhost:8000/docs
- **项目仓库**: https://github.com/huoweigang88888/silicon-world

---

**🐳 使用 Docker，3 分钟部署硅基世界！**
