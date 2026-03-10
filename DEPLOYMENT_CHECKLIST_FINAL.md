# 🚀 硅基世界 - 测试网部署清单

_版本：1.0_  
_更新时间：2026-03-10_  
_状态：准备部署_

---

## 📋 部署前检查

### ✅ 代码完成度

| 模块 | 完成度 | 状态 |
|------|--------|------|
| NFT 市场 | 100% | ✅ |
| 开发者门户 | 100% | ✅ |
| 游戏化系统 | 100% | ✅ |
| 性能优化 | 100% | ✅ |
| 文档 | 95% | ✅ |

### ✅ 测试结果

| 测试类型 | 结果 | 状态 |
|----------|------|------|
| 单元测试 | 25+ 通过 | ✅ |
| API 测试 | 100% 成功 | ✅ |
| 压力测试 | 730 请求/100% 成功 | ✅ |
| 本地部署 | 正常运行 | ✅ |

---

## 🔧 技术栈清单

### 后端
- [x] Python 3.10+
- [x] FastAPI 0.124+
- [x] SQLAlchemy 2.0+
- [x] SQLite (开发) / PostgreSQL (生产)
- [x] Uvicorn (ASGI 服务器)

### 前端
- [x] HTML5/CSS3/JavaScript
- [x] 响应式设计
- [x] 6 个完整页面

### 区块链 (可选)
- [ ] Solidity 0.8.20 (智能合约)
- [ ] Hardhat (开发环境)
- [ ] Goerli 测试网

### 部署
- [x] Docker + Docker Compose
- [x] Nginx (反向代理)
- [ ] CI/CD (GitHub Actions)

---

## 📦 部署步骤

### 阶段 1: 准备环境 (1-2 小时)

#### 1.1 服务器准备
```bash
# 推荐配置
- CPU: 2 核+
- 内存：4GB+
- 磁盘：20GB+
- 系统：Ubuntu 22.04 LTS
```

#### 1.2 安装依赖
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python
sudo apt install -y python3.10 python3-pip python3-venv

# 安装 Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 安装 Nginx
sudo apt install -y nginx
```

#### 1.3 克隆代码
```bash
cd /opt
git clone https://github.com/huoweigang88888/silicon-world.git
cd silicon-world
```

---

### 阶段 2: 配置服务 (1 小时)

#### 2.1 环境配置
```bash
# 复制环境文件
cp .env.example .env

# 编辑配置
nano .env
```

**.env 配置项**:
```bash
# 数据库
DATABASE_URL=sqlite:///./silicon_world.db
# 生产环境建议使用：DATABASE_URL=postgresql://user:pass@localhost/silicon_world

# API 配置
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
API_SECRET_KEY=your-secret-key-here

# 日志
LOG_LEVEL=INFO

# 区块链 (可选)
BLOCKCHAIN_NETWORK=goerli
CONTRACT_ADDRESS=0x...
```

#### 2.2 安装依赖
```bash
# Python 依赖
pip3 install -r requirements.txt

# 或使用本地依赖
pip3 install -r requirements-local.txt
```

#### 2.3 数据库迁移
```bash
# 执行迁移
python3 scripts/migrate_db.py
python3 scripts/migrate_social.py
python3 scripts/migrate_gamification.py  # 新增
```

---

### 阶段 3: Docker 部署 (30 分钟)

#### 3.1 Docker Compose 配置
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./uploads:/app/uploads
    environment:
      - DATABASE_URL=sqlite:///./data/silicon_world.db
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - DEBUG=false
    restart: unless-stopped
    networks:
      - silicon-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./web:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped
    networks:
      - silicon-network

networks:
  silicon-network:
    driver: bridge

volumes:
  data:
  uploads:
```

#### 3.2 启动服务
```bash
# 构建并启动
docker-compose -f docker-compose.prod.yml up -d

# 查看日志
docker-compose logs -f
```

---

### 阶段 4: Nginx 配置 (30 分钟)

#### 4.1 Nginx 配置
```nginx
# /etc/nginx/sites-available/silicon-world
server {
    listen 80;
    server_name silicon-world.com www.silicon-world.com;

    # 前端静态文件
    location / {
        root /opt/silicon-world/web;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态资源缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# HTTPS 配置 (推荐)
server {
    listen 443 ssl http2;
    server_name silicon-world.com;

    ssl_certificate /etc/letsencrypt/live/silicon-world.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/silicon-world.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # 同上配置...
}
```

#### 4.2 启用配置
```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/silicon-world /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

---

### 阶段 5: SSL 证书 (15 分钟)

#### 5.1 安装 Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

#### 5.2 获取证书
```bash
sudo certbot --nginx -d silicon-world.com -d www.silicon-world.com
```

#### 5.3 自动续期
```bash
# 添加定时任务
sudo crontab -e

# 添加以下行 (每月 1 号检查续期)
0 0 1 * * certbot renew --quiet
```

---

### 阶段 6: 监控和日志 (30 分钟)

#### 6.1 系统监控
```bash
# 安装 htop
sudo apt install -y htop

# 安装 netdata (可选)
bash <(curl -Ss https://my-netdata.io/kickstart.sh)
```

#### 6.2 日志管理
```bash
# 查看 API 日志
docker-compose logs -f api

# 查看 Nginx 日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

#### 6.3 健康检查
```bash
# API 健康检查
curl http://localhost:8000/health

# 预期响应
{"status":"healthy","service":"silicon-world-api"}
```

---

## 🔐 安全配置

### 防火墙
```bash
# 配置 UFW
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### SSH 加固
```bash
# 编辑 SSH 配置
sudo nano /etc/ssh/sshd_config

# 修改以下项
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```

### 数据库安全
```bash
# 如果使用 PostgreSQL
sudo -u postgres psql
ALTER USER silicon_world WITH PASSWORD 'strong-password';
```

---

## 📊 性能优化

### 数据库优化
```bash
# 运行优化脚本
python3 scripts/optimize_db.py
```

### 缓存配置
```bash
# 安装 Redis (可选)
sudo apt install -y redis-server
sudo systemctl enable redis
```

### CDN 配置 (可选)
- Cloudflare (免费)
- 配置 DNS
- 启用缓存
- 启用 HTTPS

---

## 🧪 部署后测试

### 功能测试清单
- [ ] API 健康检查
- [ ] 创建 Agent
- [ ] 社交功能测试
- [ ] 游戏化功能测试
- [ ] NFT 市场浏览
- [ ] NFT 创建流程
- [ ] Dashboard 加载
- [ ] 移动端适配

### 性能测试
```bash
# 运行压力测试
python3 scripts/pressure_test.py

# 目标指标
- 成功率：> 99%
- 平均响应：< 500ms
- P95 响应：< 1000ms
```

---

## 📱 域名和 DNS

### DNS 记录配置
| 类型 | 名称 | 值 | TTL |
|------|------|-----|-----|
| A | @ | 服务器 IP | 3600 |
| A | www | 服务器 IP | 3600 |
| CNAME | api | @ | 3600 |

---

## 🔄 备份策略

### 数据库备份
```bash
# 备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp /opt/silicon-world/silicon_world.db /backups/silicon_world_$DATE.db

# 定时任务 (每天凌晨 3 点)
0 3 * * * /opt/silicon-world/scripts/backup.sh
```

### 代码备份
```bash
# Git 自动推送
git add .
git commit -m "Auto backup: $(date)"
git push origin main
```

---

## 🚨 故障排除

### 常见问题

#### API 无法启动
```bash
# 检查端口占用
netstat -tulpn | grep 8000

# 查看日志
docker-compose logs api
```

#### 数据库连接失败
```bash
# 检查数据库文件
ls -la silicon_world.db

# 重新迁移
python3 scripts/migrate_db.py
```

#### Nginx 502 错误
```bash
# 检查后端服务
systemctl status docker

# 查看 Nginx 错误日志
sudo tail -f /var/log/nginx/error.log
```

---

## 📞 支持

- **项目仓库**: https://github.com/huoweigang88888/silicon-world
- **文档**: https://docs.silicon-world.com
- **Discord**: https://discord.gg/siliconworld
- **Email**: support@silicon-world.com

---

## ✅ 部署完成确认

部署完成后，确认以下事项:

- [ ] 网站可访问 (HTTP/HTTPS)
- [ ] API 响应正常
- [ ] 数据库运行正常
- [ ] 监控已配置
- [ ] 备份已设置
- [ ] 文档已更新

---

**🐾 硅基世界，由你我共同创造！**

_部署愉快！_
