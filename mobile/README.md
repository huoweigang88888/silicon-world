# Silicon World Mobile App

硅基世界移动端应用 - React Native

## 🚀 快速开始

### 前置要求

- Node.js 18+
- React Native CLI
- Android Studio (Android 开发)
- Xcode (iOS 开发，仅 macOS)

### 安装依赖

```bash
cd mobile
npm install
```

### 运行应用

**Android:**
```bash
npm run android
```

**iOS:**
```bash
npm run ios
```

### 开发服务器

```bash
npm start
```

## 📱 功能模块

### 已完成
- ✅ 登录/注册界面
- ✅ 主屏幕
- ✅ 钱包界面框架
- ✅ 消息界面框架
- ✅ 个人中心框架
- ✅ 成就界面
- ✅ 排行榜界面

### 待完成
- ⬜ Web3 钱包集成
- ⬜ 生物识别登录
- ⬜ 推送通知
- ⬜ 离线模式
- ⬜ 深色模式

## 🏗️ 项目结构

```
mobile/
├── src/
│   ├── screens/        # 屏幕组件
│   ├── components/     # 可复用组件
│   ├── navigation/     # 导航配置
│   ├── services/       # API 服务
│   ├── store/          # 状态管理
│   └── utils/          # 工具函数
├── assets/             # 资源文件
├── App.tsx             # 应用入口
└── package.json        # 依赖配置
```

## 🔧 技术栈

- **框架**: React Native 0.73
- **导航**: React Navigation 6
- **状态管理**: React Context / Redux (可选)
- **HTTP 客户端**: Axios
- **存储**: AsyncStorage
- **钱包**: WalletConnect

## 📝 开发指南

### 添加新屏幕

1. 在 `src/screens/` 创建新组件
2. 在 `App.tsx` 注册路由
3. 添加导航链接

### API 调用

```typescript
import api from '../services/api';

// 获取用户信息
const user = await api.get('/api/v1/users/me');

// 发送消息
await api.post('/api/v1/messages', { content: 'Hello' });
```

### 状态管理

```typescript
import { useContext } from 'react';
import { UserContext } from '../store/UserContext';

const user = useContext(UserContext);
```

## 🐛 常见问题

### Android 构建失败
```bash
cd android
./gradlew clean
cd ..
npm run android
```

### iOS 构建失败
```bash
cd ios
pod install
cd ..
npm run ios
```

### Metro 缓存问题
```bash
npm start -- --reset-cache
```

## 📄 许可证

MIT License
