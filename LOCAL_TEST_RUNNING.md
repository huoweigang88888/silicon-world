# 🎉 硅基世界 - 本地测试环境已启动！

_启动时间：2026-03-08 14:02_

---

## ✅ 服务状态

| 服务 | 状态 | 地址 |
|------|------|------|
| API 服务 | 🟢 运行中 | http://localhost:8000 |
| API 文档 | 🟢 可用 | http://localhost:8000/docs |
| 数据库 | 🟢 SQLite | ./silicon_world.db |

---

## 🚀 访问方式

### 1. API 交互式文档 (推荐)
浏览器打开：**http://localhost:8000/docs**

这是 Swagger UI，可以：
- 查看所有 API 端点
- 在线测试 API
- 查看请求/响应格式

### 2. 健康检查
```bash
curl http://localhost:8000/health
```

### 3. ReDoc 文档
浏览器打开：**http://localhost:8000/redoc**

---

## 📁 项目结构

```
silicon-world/
├── src/
│   ├── api/          # API 路由
│   ├── core/         # 核心配置
│   ├── models/       # 数据模型
│   ├── services/     # 业务逻辑
│   └── blockchain/   # 智能合约
├── tests/            # 测试用例
├── docs/             # 文档
├── scripts/          # 部署脚本
└── .env              # 环境配置
```

---

## 🔧 常用操作

### 停止服务
在运行 uvicorn 的终端按 `Ctrl+C`

### 重启服务
```bash
cd C:\Users\zzz\.openclaw\workspace\silicon-world
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 查看日志
服务日志会实时显示在运行 uvicorn 的终端窗口

---

## 📝 下一步

1. **浏览 API 文档** → http://localhost:8000/docs
2. **测试 API 功能** → 在 Swagger UI 中尝试调用
3. **查看现有数据** → 检查数据库和模型
4. **继续开发** → 添加新功能或修复 bug

---

## ⚠️ 注意事项

- 当前使用 **SQLite** 数据库，数据存储在 `./silicon_world.db`
- 服务运行在 **本地**，外部无法访问
- **DEBUG 模式已开启**，详细日志会显示在终端
- 如需部署到测试网，参考 `DEPLOYMENT_CHECKLIST.md`

---

**🐾 本地测试环境就绪，开始探索硅基世界！**
