/**
 * 硅基世界 - 客户端钱包模块
 * 
 * 安全原则：私钥永远不出客户端！
 * 使用 ethers.js 在浏览器生成和管理钱包
 */

// 从 CDN 加载 ethers.js
const ethers = window.ethers;

class SiliconWallet {
    constructor() {
        this.provider = null;
        this.signer = null;
        this.address = null;
        this.dbName = 'SiliconWorldWallet';
        this.dbVersion = 1;
    }

    /**
     * 初始化 - 连接 RPC 提供商
     */
    async init(rpcUrl = 'https://goerli.infura.io/v3/YOUR_KEY') {
        try {
            // 使用 ethers Provider
            this.provider = new ethers.providers.JsonRpcProvider(rpcUrl);
            console.log('✅ 钱包初始化成功');
            return true;
        } catch (error) {
            console.error('❌ 钱包初始化失败:', error);
            return false;
        }
    }

    /**
     * 创建新钱包 (客户端生成)
     * @param {string} password - 加密密码
     * @returns {Promise<{address: string}>}
     */
    async createWallet(password) {
        if (!password || password.length < 8) {
            throw new Error('密码至少 8 位');
        }

        // 生成随机钱包
        const wallet = ethers.Wallet.createRandom();
        
        // 加密私钥 (使用用户密码)
        const encryptedJson = await wallet.encrypt(password);
        
        // 存储到本地
        await this.saveEncryptedWallet(encryptedJson);
        
        console.log('✅ 钱包创建成功:', wallet.address);
        
        return {
            address: wallet.address,
            mnemonic: wallet.mnemonic.phrase, // ⚠️ 只显示一次，用户备份
            note: '请安全保存助记词！无法恢复！'
        };
    }

    /**
     * 导入钱包 (使用私钥)
     * @param {string} privateKey - 私钥
     * @param {string} password - 加密密码
     * @returns {Promise<{address: string}>}
     */
    async importWallet(privateKey, password) {
        if (!privateKey.startsWith('0x')) {
            privateKey = '0x' + privateKey;
        }
        
        const wallet = new ethers.Wallet(privateKey);
        const encryptedJson = await wallet.encrypt(password);
        await this.saveEncryptedWallet(encryptedJson);
        
        console.log('✅ 钱包导入成功:', wallet.address);
        
        return {
            address: wallet.address
        };
    }

    /**
     * 解锁钱包
     * @param {string} password - 密码
     * @returns {Promise<string>} 钱包地址
     */
    async unlockWallet(password) {
        const encryptedJson = await this.loadEncryptedWallet();
        if (!encryptedJson) {
            throw new Error('未找到钱包，请先创建或导入');
        }
        
        const wallet = await ethers.Wallet.fromEncryptedJson(
            encryptedJson,
            password
        );
        
        this.signer = wallet.connect(this.provider);
        this.address = wallet.address;
        
        console.log('✅ 钱包解锁成功:', this.address);
        return this.address;
    }

    /**
     * 锁定钱包 (清除内存中的私钥)
     */
    lockWallet() {
        this.signer = null;
        console.log('🔒 钱包已锁定');
    }

    /**
     * 获取余额
     * @returns {Promise<string>} 余额 (ETH)
     */
    async getBalance() {
        if (!this.address) {
            throw new Error('钱包未解锁');
        }
        
        const balance = await this.provider.getBalance(this.address);
        return ethers.utils.formatEther(balance);
    }

    /**
     * 签名交易 (本地完成)
     * @param {Object} transaction - 交易对象
     * @returns {Promise<string>} 签名后的交易
     */
    async signTransaction(transaction) {
        if (!this.signer) {
            throw new Error('钱包未解锁');
        }
        
        // 在客户端签名
        const signedTx = await this.signer.signTransaction(transaction);
        console.log('✅ 交易已签名');
        return signedTx;
    }

    /**
     * 发送交易 (签名并广播)
     * @param {string} to - 接收地址
     * @param {string} amount - 金额 (ETH)
     * @returns {Promise<{hash: string, wait: Function}>}
     */
    async sendTransaction(to, amount) {
        if (!this.signer) {
            throw new Error('钱包未解锁');
        }
        
        const tx = await this.signer.sendTransaction({
            to: to,
            value: ethers.utils.parseEther(amount)
        });
        
        console.log('✅ 交易已发送:', tx.hash);
        return tx;
    }

    /**
     * 签名消息
     * @param {string} message - 要签名的消息
     * @returns {Promise<string>} 签名
     */
    async signMessage(message) {
        if (!this.signer) {
            throw new Error('钱包未解锁');
        }
        
        const signature = await this.signer.signMessage(message);
        console.log('✅ 消息已签名');
        return signature;
    }

    /**
     * 导出私钥 (需要密码)
     * @param {string} password - 密码
     * @returns {Promise<string>} 私钥
     */
    async exportPrivateKey(password) {
        const encryptedJson = await this.loadEncryptedWallet();
        const wallet = await ethers.Wallet.fromEncryptedJson(
            encryptedJson,
            password
        );
        console.log('⚠️ 私钥已导出，请安全保管！');
        return wallet.privateKey;
    }

    /**
     * 导出助记词 (需要密码)
     * @param {string} password - 密码
     * @returns {Promise<string>} 助记词
     */
    async exportMnemonic(password) {
        const encryptedJson = await this.loadEncryptedWallet();
        const wallet = await ethers.Wallet.fromEncryptedJson(
            encryptedJson,
            password
        );
        console.log('⚠️ 助记词已导出，请安全保管！');
        return wallet.mnemonic.phrase;
    }

    /**
     * 清除本地钱包
     */
    async clearWallet() {
        const db = await this.openDB();
        const tx = db.transaction('wallets', 'readwrite');
        const store = tx.objectStore('wallets');
        await store.clear();
        
        this.signer = null;
        this.address = null;
        
        console.log('🗑️ 钱包已清除');
    }

    // ==================== 内部方法 ====================

    /**
     * 保存加密钱包到 IndexedDB
     */
    async saveEncryptedWallet(encryptedJson) {
        const db = await this.openDB();
        const tx = db.transaction('wallets', 'readwrite');
        const store = tx.objectStore('wallets');
        
        await store.put({
            id: 'primary',
            encrypted: encryptedJson,
            timestamp: Date.now()
        });
        
        await tx.done;
        console.log('💾 钱包已保存');
    }

    /**
     * 从 IndexedDB 加载加密钱包
     */
    async loadEncryptedWallet() {
        const db = await this.openDB();
        const tx = db.transaction('wallets', 'readonly');
        const store = tx.objectStore('wallets');
        
        const record = await store.get('primary');
        return record ? record.encrypted : null;
    }

    /**
     * 打开 IndexedDB
     */
    async openDB() {
        if (!window.indexedDB) {
            throw new Error('浏览器不支持 IndexedDB');
        }

        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains('wallets')) {
                    db.createObjectStore('wallets', { keyPath: 'id' });
                    console.log('📦 创建钱包存储');
                }
            };
            
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * 检查是否有钱包
     */
    async hasWallet() {
        try {
            const encrypted = await this.loadEncryptedWallet();
            return !!encrypted;
        } catch {
            return false;
        }
    }
}

// 导出
window.SiliconWallet = SiliconWallet;
console.log('🔐 SiliconWallet 模块已加载');
