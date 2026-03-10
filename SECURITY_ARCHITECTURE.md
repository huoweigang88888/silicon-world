# 🔐 硅基世界 - 零知识安全架构

_版本：1.0_  
_更新时间：2026-03-10_  
_核心原则：私钥永远属于用户_

---

## 🎯 安全架构概述

### 零知识设计 (Zero-Knowledge Architecture)

```
┌─────────────────────────────────────────────────────────┐
│                    用户浏览器/客户端                     │
│                                                         │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐  │
│  │  钱包生成    │   │  交易签名    │   │  私钥加密    │  │
│  │  (ethers.js)│   │  (本地)     │   │  (AES-256)  │  │
│  └─────────────┘   └─────────────┘   └─────────────┘  │
│         │                │                │            │
│         └────────────────┴────────────────┘            │
│                          │                             │
│              ┌───────────▼───────────┐                │
│              │   本地加密存储          │                │
│              │   (IndexedDB)         │                │
│              └───────────────────────┘                │
└─────────────────────────────────────────────────────────┘
                           │
                           │ ⚠️ 只传输：
                           │   - 钱包地址 (公开)
                           │   - 签名后的交易
                           │   - 签名消息
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  硅基世界服务器                          │
│                                                         │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐  │
│  │  地址注册    │   │  签名验证    │   │  交易广播    │  │
│  │  (只存地址) │   │  (公钥)     │   │  (RPC)      │  │
│  └─────────────┘   └─────────────┘   └─────────────┘  │
│                                                         │
│  ⚠️ 服务器 NEVER:                                      │
│  - 存储私钥                                             │
│  - 传输私钥                                             │
│  - 生成签名                                             │
│  - 请求私钥                                             │
└─────────────────────────────────────────────────────────┘
```

---

## 🔑 关键安全特性

### 1. 私钥管理

| 操作 | 位置 | 说明 |
|------|------|------|
| 生成 | ✅ 客户端 | ethers.Wallet.createRandom() |
| 存储 | ✅ 客户端 | IndexedDB + AES-256 加密 |
| 使用 | ✅ 客户端 | 本地签名后发送 |
| 导出 | ✅ 客户端 | 需要密码解密 |
| 备份 | ✅ 客户端 | 助记词用户自存 |

### 2. 加密方案

```javascript
// 私钥加密 (客户端)
const wallet = ethers.Wallet.createRandom();
const encryptedJson = await wallet.encrypt(password);
// encryptedJson 使用 AES-256-CBC 加密

// 私钥解密 (客户端)
const wallet = await ethers.Wallet.fromEncryptedJson(
    encryptedJson,
    password
);
```

### 3. 签名流程

```
1. 用户发起交易 (前端)
        ↓
2. 本地签名 (ethers.js)
        ↓
3. 发送签名交易到服务器
        ↓
4. 服务器验证签名 (公钥)
        ↓
5. 广播到区块链 (RPC)
```

---

## 📦 技术实现

### 前端钱包模块

**文件**: `web/js/wallet.js`

```javascript
class SiliconWallet {
    // 创建钱包 (客户端生成)
    async createWallet(password) {
        const wallet = ethers.Wallet.createRandom();
        const encrypted = await wallet.encrypt(password);
        await this.saveEncryptedWallet(encrypted);
        return { address: wallet.address };
    }

    // 签名交易 (本地)
    async signTransaction(tx) {
        return await this.signer.signTransaction(tx);
    }

    // 发送交易
    async sendTransaction(to, amount) {
        return await this.signer.sendTransaction({
            to,
            value: ethers.parseEther(amount)
        });
    }
}
```

### 后端钱包管理

**文件**: `src/nexusa/wallet.py`

```python
class WalletManager:
    """零知识钱包管理器"""
    
    def create_wallet(self, label=None):
        """
        创建钱包 (占位符)
        ⚠️ 实际应由客户端生成
        """
        # 只生成地址，无私钥
        wallet = Wallet(
            address="0x...",
            metadata={
                "private_key_never_stored": True
            }
        )
        return wallet
    
    def register_wallet(self, address, label=None):
        """
        注册客户端生成的钱包
        ⚠️ 推荐方式
        """
        # 只存储地址
        pass
    
    def verify_signature(self, address, message, signature):
        """
        验证客户端签名
        ⚠️ 只验证，不生成
        """
        recovered = Account.recover_hash(message, signature=signature)
        return recovered.lower() == address.lower()
```

---

## 🛡️ 安全最佳实践

### 必须实现

1. ✅ **私钥不出客户端**
   - 所有签名在浏览器完成
   - 服务器只接收签名结果

2. ✅ **加密存储**
   - AES-256 加密私钥
   - 密码由用户设定

3. ✅ **助记词备份**
   - 创建时显示助记词
   - 提示用户安全保存

4. ✅ **密码强度**
   - 最少 8 位
   - 建议大小写 + 数字 + 符号

5. ✅ **自动锁定**
   - 一段时间不操作自动锁定
   - 关闭标签页清除内存

### 推荐实现

1. ⭐ **生物识别**
   - WebAuthn API
   - FaceID / TouchID

2. ⭐ **硬件钱包**
   - Ledger 支持
   - Trezor 支持

3. ⭐ **多签支持**
   - 2/3 多签名
   - 社交恢复

4. ⭐ **交易确认**
   - 显示交易详情
   - 二次确认大额交易

---

## 🔍 审计清单

### 代码审计

- [ ] 私钥不在服务器存储
- [ ] 私钥不在网络传输
- [ ] 加密算法正确实现
- [ ] 随机数生成安全
- [ ] 无内存泄漏
- [ ] XSS 防护
- [ ] CSRF 防护

### 用户教育

- [ ] 助记词备份提示
- [ ] 密码强度要求
- [ ] 钓鱼网站警告
- [ ] 私钥保管说明
- [ ] 安全最佳实践

---

## 📚 参考资源

### 开源库

- **ethers.js**: https://github.com/ethers-io/ethers.js
- **web3.js**: https://github.com/web3/web3.js
- **MetaMask**: https://github.com/MetaMask/metamask-extension

### 安全标准

- **ERC-4337**: 账户抽象
- **EIP-712**: 类型化签名
- **BIP-39**: 助记词
- **BIP-44**: 钱包层级

### 审计工具

- **Slither**: Solidity 静态分析
- **Mythril**: 智能合约安全
- **OpenZeppelin**: 安全合约库

---

## 🚀 实施状态

| 模块 | 状态 | 完成度 |
|------|------|--------|
| 客户端钱包 | ✅ 完成 | 100% |
| 本地加密存储 | ✅ 完成 | 100% |
| 交易签名 | ✅ 完成 | 100% |
| 后端零知识改造 | ✅ 完成 | 100% |
| 签名验证 | ✅ 完成 | 100% |
| 助记词备份 | ⏳ 待实现 | 0% |
| 硬件钱包 | ⏳ 待实现 | 0% |

---

## 🎯 下一步

1. **助记词备份** (优先级：高)
   - 创建时显示助记词
   - 12/24 词选项
   - 验证备份

2. **生物识别** (优先级：中)
   - WebAuthn 集成
   - FaceID/TouchID

3. **硬件钱包** (优先级：中)
   - Ledger Live
   - WalletConnect

4. **多签支持** (优先级：低)
   - Safe 集成
   - 社交恢复

---

**🐾 安全第一！私钥永远属于用户！**

_硅基世界开发团队_
