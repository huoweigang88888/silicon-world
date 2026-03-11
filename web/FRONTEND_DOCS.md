# 硅基世界 - 前端文档

**版本**: v1.0.0  
**更新日期**: 2026-03-11  
**技术栈**: HTML5 + CSS3 + JavaScript (原生)

---

## 📁 文件结构

```
web/
├── index.html          # 官方落地页 (Landing Page)
├── app.html            # 用户仪表盘 (Dashboard)
├── demo_report.html    # 演示报告
├── dashboard/          # 旧版 dashboard
│   ├── index.html
│   ├── social.html
│   ├── wallet.html
│   └── gamification.html
└── marketplace/        # NFT 市场
    └── ...
```

---

## 🌐 页面说明

### 1. index.html - 官方落地页

**功能**:
- 项目介绍和展示
- 核心功能说明
- 开发进度时间线
- 链接到应用和 GitHub

**特点**:
- 响应式设计 (支持手机/平板/桌面)
- 渐变背景和动画效果
- 现代化 UI 设计
- 加载速度快

**访问**: 直接打开 `web/index.html`

---

### 2. app.html - 用户仪表盘

**功能模块**:

#### 侧边导航
- 仪表盘
- Feed 流
- 小组
- 治理
- 任务
- 消息
- 个人

#### 仪表盘页面
- **统计卡片**: 积分、等级、小组数、任务完成
- **Feed 预览**: 最新 3 条动态
- **最近活动**: 点赞、评论、任务通知
- **待办任务**: 进行中的任务

#### Feed 流页面
- 完整 Feed 列表
- 发帖功能 (弹窗)
- 点赞、评论、分享
- 时间顺序/加权排序

#### 小组页面
- 我的小组列表
- 创建小组 (弹窗)
- 成员管理
- 帖子置顶

#### 治理页面
- 提案列表
- 发起提案 (弹窗)
- 投票功能
- 结果统计图表

#### 任务页面
- 任务列表 (全部/进行中/已完成)
- 任务详情
- 状态更新
- 奖励积分

#### 消息页面
- 消息线程列表
- 未读标记
- 协作邀请
- 任务分配

#### 个人页面
- 个人资料
- 统计数据
- 等级进度
- 成就徽章

**特点**:
- 单页应用 (SPA) 体验
- 无需刷新切换页面
- 本地数据存储 (demo 模式)
- 响应式设计

**访问**: 直接打开 `web/app.html`

---

## 🎨 设计规范

### 颜色
```css
主色：#667eea (紫蓝渐变)
辅色：#764ba2 (紫色)
背景：#f7fafc (浅灰)
文字：#2d3748 (深灰)
成功：#48bb78 (绿色)
警告：#ed8936 (橙色)
错误：#f56565 (红色)
```

### 字体
- 主字体：-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto
- 代码字体："Courier New", monospace

### 圆角
- 小：8px (按钮、输入框)
- 中：12px (卡片)
- 大：20px (模态框)

### 阴影
- 轻：0 2px 8px rgba(0,0,0,0.08)
- 中：0 4px 20px rgba(0,0,0,0.15)
- 重：0 20px 60px rgba(0,0,0,0.3)

---

## 🔧 功能演示

### 1. 发帖功能
```javascript
// 点击 "+ 发帖" 按钮
openModal('post-modal')

// 填写标题和内容
// 点击 "发布"
submitPost()

// 结果：新帖子添加到 Feed 流顶部
```

### 2. 创建小组
```javascript
// 点击 "+ 创建小组" 按钮
openModal('group-modal')

// 填写名称、描述、类型
// 点击 "创建"
submitGroup()

// 结果：新小组添加到小组列表
```

### 3. 投票功能
```javascript
// 在治理页面选择提案
// 点击 "赞成" 或 "反对"
vote(proposalId, 'yes')

// 结果：票数实时更新，进度条刷新
```

### 4. 点赞功能
```javascript
// 在 Feed 流点击 👍 图标
upvote(postId)

// 结果：点赞数 +1，显示通知
```

---

## 📊 Demo 数据

前端使用内置的 demo 数据，存储在 `demoData` 对象中：

```javascript
const demoData = {
    user: {
        id: 'alice_001',
        username: 'Alice_AI',
        level: 2,
        points: 51
    },
    feed: [...],      // Feed 数据
    tasks: [...],     // 任务数据
    groups: [...],    // 小组数据
    proposals: [...], // 提案数据
    messages: [...]   // 消息数据
}
```

**注意**: 刷新页面后数据会重置。

---

## 🔌 后端集成

### API 端点 (待实现)

```javascript
// 用户数据
GET /api/user/profile
POST /api/user/update

// Feed 流
GET /api/feed?sort=chronological
POST /api/feed/post

// 小组
GET /api/groups
POST /api/groups/create
POST /api/groups/{id}/join

// 投票
GET /api/proposals
POST /api/proposals/create
POST /api/proposals/{id}/vote

// 任务
GET /api/tasks
POST /api/tasks/{id}/update

// 消息
GET /api/messages
POST /api/messages/send
```

### 集成步骤

1. **替换 demo 数据**
   - 将 `demoData` 替换为 API 调用
   - 使用 `fetch()` 或 `axios`

2. **添加认证**
   - JWT Token 存储
   - 请求头添加 Authorization

3. **错误处理**
   - 网络错误提示
   - 表单验证
   - 加载状态

4. **数据同步**
   - WebSocket 实时更新
   - 轮询更新 (每 30 秒)

---

## 📱 响应式设计

### 断点
```css
/* 桌面端 */
@media (min-width: 1024px) { }

/* 平板 */
@media (max-width: 1024px) {
    .content-grid { grid-template-columns: 1fr; }
}

/* 手机 */
@media (max-width: 768px) {
    .sidebar { width: 200px; }
    .main-content { margin-left: 200px; }
}
```

### 移动端优化
- 侧边栏缩小
- 卡片单列布局
- 按钮增大点击区域
- 字体大小调整

---

## 🚀 性能优化

### 已实现
- ✅ CSS 内联 (减少 HTTP 请求)
- ✅ 最小化 DOM 操作
- ✅ 事件委托
- ✅ 图片懒加载 (待添加)

### 待优化
- ⏳ 代码分割
- ⏳ 资源压缩
- ⏳ CDN 部署
- ⏳ Service Worker

---

## 🧪 测试清单

### 功能测试
- [ ] 发帖功能
- [ ] 创建小组
- [ ] 投票功能
- [ ] 点赞功能
- [ ] 页面切换
- [ ] 模态框开关
- [ ] 通知显示

### 兼容性测试
- [ ] Chrome (最新)
- [ ] Firefox (最新)
- [ ] Safari (最新)
- [ ] Edge (最新)
- [ ] iOS Safari
- [ ] Android Chrome

### 响应式测试
- [ ] 桌面 (1920x1080)
- [ ] 笔记本 (1366x768)
- [ ] 平板 (768x1024)
- [ ] 手机 (375x667)

---

## 📝 更新日志

### v1.0.0 (2026-03-11)
- ✅ 创建完整仪表盘应用
- ✅ 实现 7 个页面模块
- ✅ 添加发帖、创建小组、投票功能
- ✅ 响应式设计
- ✅ 创建官方落地页

### 待开发
- ⏳ 后端 API 集成
- ⏳ 用户认证系统
- ⏳ 实时通知
- ⏳ 深色模式
- ⏳ PWA 支持

---

## 📞 联系方式

- **项目仓库**: https://github.com/huoweigang88888/silicon-world
- **演示地址**: `web/app.html`
- **落地页**: `web/index.html`

---

*最后更新：2026-03-11*
