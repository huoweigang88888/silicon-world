# 🔐 Web3 私钥安全最佳实践

_整理时间：2026-03-10_  
_目标：用户完全掌控私钥，系统零知识_

---

## 🎯 核心原则

### 1. 零知识架构 (Zero-Knowledge)
- ✅ **私钥永远不离开用户设备**
- ✅ 服务器不存储、不传输、不接触私钥
- ✅ 所有签名操作在客户端完成
- ✅ 服务器只接收已签名的交易

### 2. 用户完全掌控
- ✅ 用户自己生成私钥 (或客户端生成)
- ✅ 私钥加密存储由用户管理
- ✅ 助记词/私钥导出功能
- ✅ 没有"忘记密码"选项 (去中心化特性)

### 3. 多层安全
- ✅ 本地加密存储
- ✅ 生物识别/密码保护
- ✅ 硬件钱包支持
- ✅ 多重签名选项

---

## 📦 推荐技术方案

### 方案 1: 客户端钱包库 (推荐 ⭐⭐⭐)

**技术栈**:
- **前端**: ethers.js / web3.js
- **移动端**: React Native + @react-native-async-storage
- **桌面**: Electron + Node.js crypto

**工作流程**:
```
1. 用户在浏览器生成钱包 (ethers.js)
2. 私钥加密存储在本地 (IndexedDB/LocalStorage)
3. 密码由用户保管 (可选：生物识别)
4. 交易签名在浏览器完成
5. 只发送签名后的交易到服务器
```

**优点**:
- ✅ 私钥永不离开客户端
- ✅ 开源库，可审计
- ✅ 用户完全掌控
- ✅ 兼容现有钱包 (MetaMask 等)

**参考项目**:
- **MetaMask**: https://github.com/MetaMask/metamask-extension
- **ethers.js**: https://github.com/ethers-io/ethers.js
- **web3.js**: https://github.com/web3/web3.js

---

### 方案 2: MPC 多重计算 (高级 ⭐⭐⭐)

**技术**: Multi-Party Computation (MPC)

**工作原理**:
- 私钥被分成多个分片 (shares)
- 分片存储在不同位置 (客户端 + 服务器 + 备份)
- 签名时多方协作，私钥永不完整出现
- 需要阈值签名 (如 2/3)

**优点**:
- ✅ 私钥从不完整存在
- ✅ 可恢复 (丢失一个分片仍可签名)
- ✅ 企业级安全

**参考项目**:
- **Fireblocks**: https://www.fireblocks.com/
- **Unbound Security**: https://unboundsecurity.com/
- **OpenMPC**: https://github.com/LAIF-Northwestern/OpenMPC

---

### 方案 3: 智能合约钱包 (AA 账户抽象) ⭐⭐

**技术**: ERC-4337 Account Abstraction

**工作原理**:
- 用户拥有智能合约钱包
- 支持社交恢复 (可信联系人)
- 支持多签名
- 支持 Gas 代付

**优点**:
- ✅ 可恢复
- ✅ 灵活的安全策略
- ✅ 更好的用户体验

**参考项目**:
- **Safe (Gnosis)**: https://safe.global/
- **Stackup**: https://www.stackup.sh/
- **Pimlico**: https://pimlico.io/

---

## 🔧 硅基世界实现方案

### 推荐：方案 1 (客户端钱包) + 硬件钱包支持

#### 架构设计

```
┌─────────────────────────────────────────────────────┐
│                    用户浏览器                        │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐   │
│  │  钱包生成  │    │  交易签名  │    │  私钥加密  │   │
│  │  (ethers) │    │  (本地)   │    │  (AES)    │   │
│  └───────────┘    └───────────┘    └───────────┘   │
│         │                │                │         │
│         └────────────────┴────────────────┘         │
│                          │                          │
│              ┌───────────▼───────────┐             │
│              │   本地加密存储         │             │
│              │   (IndexedDB)         │             │
│              └───────────────────────┘             │
└─────────────────────────────────────────────────────┘
                         │
                         │ 只传输签名后的交易
                         ▼
┌─────────────────────────────────────────────────────┐
│                  硅基世界服务器                      │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐   │
│  │  广播交易  │    │  查询状态  │    │  事件监听  │   │
│  │  (RPC)    │    │  (RPC)    │    │  (WebSocket)│  │
│  └───────────┘    └───────────┘    └───────────┘   │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                  区块链 (Goerli)                     │
└─────────────────────────────────────────────────────┘
```

#### 实现步骤

### 1. 前端钱包模块 (`web/js/wallet.js`)

```javascript
import { ethers } from 'https://cdn.ethers.io/lib/ethers-5.7.2.umd.min.js';

class SiliconWallet {
    constructor() {
        this.provider = null;
        this.signer = null;
        this.address = null;
    }

    // 创建新钱包 (客户端生成)
    async createWallet(password) {
        // 生成随机钱包
        const wallet = ethers.Wallet.createRandom();
        
        // 加密私钥 (使用用户密码)
        const encryptedJson = await wallet.encrypt(password);
        
        // 存储到本地
        await this.saveEncryptedWallet(encryptedJson);
        
        return {
            address: wallet.address,
            // ⚠️ 不返回私钥！用户通过密码解密
        };
    }

    // 导入钱包
    async importWallet(privateKey, password) {
        const wallet = new ethers.Wallet(privateKey);
        const encryptedJson = await wallet.encrypt(password);
        await this.saveEncryptedWallet(encryptedJson);
        return { address: wallet.address };
    }

    // 解锁钱包
    async unlockWallet(password) {
        const encryptedJson = await this.loadEncryptedWallet();
        const wallet = await ethers.Wallet.fromEncryptedJson(
            encryptedJson,
            password
        );
        this.signer = wallet;
        this.address = wallet.address;
        return wallet.address;
    }

    // 签名交易 (本地完成)
    async signTransaction(transaction) {
        if (!this.signer) {
            throw new Error('钱包未解锁');
        }
        // 在客户端签名
        const signedTx = await this.signer.signTransaction(transaction);
        return signedTx;
    }

    // 签名消息
    async signMessage(message) {
        if (!this.signer) {
            throw new Error('钱包未解锁');
        }
        const signature = await this.signer.signMessage(message);
        return signature;
    }

    // 本地存储 (加密)
    async saveEncryptedWallet(encryptedJson) {
        // 使用 IndexedDB 安全存储
        const db = await this.openDB();
        await db.put('wallets', {
            id: 'primary',
            encrypted: encryptedJson,
            timestamp: Date.now()
        });
    }

    // 加载加密钱包
    async loadEncryptedWallet() {
        const db = await this.openDB();
        const record = await db.get('wallets', 'primary');
        return record.encrypted;
    }

    // 打开 IndexedDB
    openDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open('SiliconWorldWallet', 1);
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains('wallets')) {
                    db.createObjectStore('wallets', { keyPath: 'id' });
                }
            };
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    // 导出私钥 (需要密码)
    async exportPrivateKey(password) {
        const encryptedJson = await this.loadEncryptedWallet();
        const wallet = await ethers.Wallet.fromEncryptedJson(
            encryptedJson,
            password
        );
        return wallet.privateKey;
    }

    // 清除本地钱包
    async clearWallet() {
        const db = await this.openDB();
        await db.delete('wallets', 'primary');
        this.signer = null;
        this.address = null;
    }
}

export default SiliconWallet;
```

---

### 2. 后端修改 (零私钥架构)

**当前问题**: `src/nexusa/wallet.py` 存储私钥

**修改方案**:

```python
# src/nexusa/wallet.py (修改后)

class WalletManager:
    """
    零知识钱包管理器
    
    ⚠️ 不再存储私钥！
    只管理钱包地址和元数据
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path
        self.wallets: Dict[str, Wallet] = {}  # 只存地址和元数据
    
    def create_wallet(self, label: Optional[str] = None) -> Wallet:
        """
        创建钱包
        
        ⚠️ 返回地址，私钥由客户端生成和保管
        """
        # 生成新地址 (不生成私钥！)
        # 实际上应该由客户端生成，这里只是占位
        wallet = Wallet(
            address="0x...",  # 客户端传入
            label=label,
            metadata={
                "created_by": "client",  # 客户端生成
                "server_never_saw_private_key": True
            }
        )
        
        # 只保存地址
        self.wallets[wallet.address] = wallet
        self._save_wallets()
        
        return wallet
    
    def register_wallet(self, address: str, label: Optional[str] = None) -> Wallet:
        """
        注册客户端创建的钱包
        
        客户端生成钱包后，只发送地址到服务器注册
        """
        wallet = Wallet(
            address=address,
            label=label,
            metadata={
                "registered_at": datetime.utcnow().isoformat(),
                "private_key_never_stored": True
            }
        )
        
        self.wallets[address] = wallet
        self._save_wallets()
        
        return wallet
```

---

### 3. 前端集成示例

```html
<!-- web/dashboard/wallet.html -->
<script type="module">
import SiliconWallet from './js/wallet.js';

const wallet = new SiliconWallet();

// 创建钱包
document.getElementById('createBtn').addEventListener('click', async () => {
    const password = document.getElementById('password').value;
    
    // 客户端生成钱包
    const result = await wallet.createWallet(password);
    
    // 只发送地址到服务器注册
    await fetch('/api/v1/nexusa/wallet/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            address: result.address,
            label: 'My Wallet'
        })
    });
    
    alert('钱包创建成功！请牢记密码，无法恢复！');
});

// 发送交易
document.getElementById('sendBtn').addEventListener('click', async () => {
    const to = document.getElementById('toAddress').value;
    const amount = document.getElementById('amount').value;
    const password = document.getElementById('unlockPassword').value;
    
    // 解锁钱包
    await wallet.unlockWallet(password);
    
    // 本地签名交易
    const signedTx = await wallet.signTransaction({
        to: to,
        value: ethers.utils.parseEther(amount)
    });
    
    // 发送签名后的交易到服务器广播
    const response = await fetch('/api/v1/nexusa/transaction/broadcast', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            signed_transaction: signedTx
        })
    });
    
    const data = await response.json();
    alert(`交易已广播！TX: ${data.tx_hash}`);
});
</script>
```

---

## 🔐 安全建议

### 必须实现
1. ✅ 私钥永远不出客户端
2. ✅ 本地加密存储 (AES-256)
3. ✅ 密码强度验证
4. ✅ 助记词备份提示
5. ✅ 导出功能

### 推荐实现
1. ⭐ 生物识别 (FaceID/TouchID)
2. ⭐ 硬件钱包支持 (Ledger/Trezor)
3. ⭐ 社交恢复 (可信联系人)
4. ⭐ 交易确认提示
5. ⭐ 钓鱼网站检测

### 高级功能
1. 🔥 MPC 多重签名
2. 🔥 智能合约钱包
3. 🔥 Gas 代付
4. 🔥 批量交易

---

## 📚 参考资源

### 开源库
- **ethers.js**: https://github.com/ethers-io/ethers.js
- **web3.js**: https://github.com/web3/web3.js
- **MetaMask SDK**: https://github.com/MetaMask/metamask-sdk
- **WalletConnect**: https://github.com/WalletConnect/walletconnect-monorepo

### 安全标准
- **ERC-4337**: 账户抽象
- **EIP-712**: 类型化数据签名
- **BIP-39**: 助记词
- **BIP-44**: 多层级钱包

### 审计清单
- [ ] 私钥不出客户端
- [ ] 加密存储实现正确
- [ ] 随机数生成安全
- [ ] 密码验证强度足够
- [ ] 无内存泄漏
- [ ] XSS 防护
- [ ] CSRF 防护

---

## 🎯 硅基世界实施计划

### 阶段 1: 客户端钱包 (1-2 天)
- [ ] 集成 ethers.js
- [ ] 实现客户端钱包生成
- [ ] 本地加密存储
- [ ] 修改后端 (移除私钥存储)

### 阶段 2: 交易签名 (1 天)
- [ ] 客户端交易签名
- [ ] 服务器只广播
- [ ] 交易状态查询

### 阶段 3: 安全增强 (2-3 天)
- [ ] 助记词备份
- [ ] 密码强度验证
- [ ] 生物识别
- [ ] 安全提示

### 阶段 4: 硬件钱包 (可选)
- [ ] Ledger 支持
- [ ] Trezor 支持
- [ ] WalletConnect 集成

---

**🐾 安全 first！私钥永远属于用户！**
