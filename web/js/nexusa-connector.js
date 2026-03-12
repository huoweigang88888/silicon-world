/**
 * NexusA 连接器 - 前端 JavaScript SDK 封装
 * 硅基世界 x NexusA 集成
 */

class NexusaConnector {
    constructor(config = {}) {
        this.config = {
            network: config.network || 'sepolia',
            rpcUrl: config.rpcUrl || '',
            chainId: config.chainId || 11155111,
            ...config
        };
        
        this.connected = false;
        this.account = null;
        this.provider = null;
        
        // 合约地址 (占位符，部署后更新)
        this.contracts = {
            DIDRegistry: '',
            AIWallet: '',
            Payment: '',
            CreditEngine: '',
            InsurancePool: ''
        };
    }

    /**
     * 连接钱包
     */
    async connectWallet() {
        // 检查 MetaMask
        if (typeof window.ethereum !== 'undefined') {
            try {
                // 请求账户访问
                const accounts = await window.ethereum.request({ 
                    method: 'eth_requestAccounts' 
                });
                
                this.account = accounts[0];
                this.provider = window.ethereum;
                this.connected = true;
                
                console.log('✅ 钱包已连接:', this.account);
                
                // 监听账户变化
                window.ethereum.on('accountsChanged', this.handleAccountsChanged.bind(this));
                window.ethereum.on('chainChanged', this.handleChainChanged.bind(this));
                
                return {
                    success: true,
                    account: this.account
                };
            } catch (error) {
                console.error('❌ 连接钱包失败:', error);
                return {
                    success: false,
                    error: error.message
                };
            }
        } else {
            // 没有安装 MetaMask
            return {
                success: false,
                error: '请安装 MetaMask 钱包扩展'
            };
        }
    }

    /**
     * 断开钱包
     */
    disconnectWallet() {
        this.connected = false;
        this.account = null;
        this.provider = null;
        console.log('🔌 钱包已断开');
    }

    /**
     * 切换网络
     */
    async switchNetwork(chainId) {
        try {
            await window.ethereum.request({
                method: 'wallet_switchEthereumChain',
                params: [{ chainId: `0x${chainId.toString(16)}` }],
            });
            return { success: true };
        } catch (error) {
            // 如果网络不存在，尝试添加
            if (error.code === 4902) {
                return await this.addNetwork(chainId);
            }
            return { success: false, error: error.message };
        }
    }

    /**
     * 添加新网络
     */
    async addNetwork(chainId) {
        const networks = {
            11155111: {
                chainId: '0x250de0',
                chainName: 'Sepolia',
                nativeCurrency: { name: 'ETH', symbol: 'ETH', decimals: 18 },
                rpcUrls: ['https://eth-sepolia.g.alchemy.com/v2/'],
                blockExplorerUrls: ['https://sepolia.etherscan.io']
            },
            31337: {
                chainId: '0x7a69',
                chainName: 'Hardhat Local',
                nativeCurrency: { name: 'ETH', symbol: 'ETH', decimals: 18 },
                rpcUrls: ['http://127.0.0.1:8545'],
                blockExplorerUrls: []
            }
        };

        const network = networks[chainId];
        if (!network) {
            return { success: false, error: '不支持的网络' };
        }

        try {
            await window.ethereum.request({
                method: 'wallet_addEthereumChain',
                params: [network]
            });
            return { success: true };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    /**
     * 创建 DID
     */
    async createDID() {
        if (!this.connected) {
            return { success: false, error: '钱包未连接' };
        }

        // 模拟 DID 创建 (实际应调用合约)
        const did = `did:nexusa:${this.config.chainId}:${this.account.toLowerCase()}`;
        
        return {
            success: true,
            did: did,
            controller: this.account
        };
    }

    /**
     * 解析 DID
     */
    async resolveDID(did) {
        // 模拟 DID 解析
        return {
            '@context': [
                'https://www.w3.org/ns/did/v1',
                'https://w3id.org/security/suites/secp256k1-2019/v1'
            ],
            id: did,
            controller: this.account,
            verificationMethod: [],
            service: []
        };
    }

    /**
     * 发送支付
     */
    async sendPayment(to, amount, token = 'SWC') {
        if (!this.connected) {
            return { success: false, error: '钱包未连接' };
        }

        try {
            // 转换金额到 Wei (假设 18 位小数)
            const value = BigInt(Math.floor(amount * Math.pow(10, 18))).toString(16);
            
            // 发送交易
            const txHash = await window.ethereum.request({
                method: 'eth_sendTransaction',
                params: [{
                    from: this.account,
                    to: to,
                    value: '0x' + value
                }]
            });

            return {
                success: true,
                txHash: txHash,
                status: 'pending'
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 获取余额
     */
    async getBalance(address = null) {
        const addr = address || this.account;
        if (!addr) {
            return { success: false, error: '没有地址' };
        }

        try {
            const balance = await window.ethereum.request({
                method: 'eth_getBalance',
                params: [addr, 'latest']
            });

            // 转换到 ETH
            const ethBalance = parseInt(balance, 16) / Math.pow(10, 18);
            
            return {
                success: true,
                balance: ethBalance,
                address: addr
            };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    /**
     * 签名消息
     */
    async signMessage(message) {
        if (!this.connected) {
            return { success: false, error: '钱包未连接' };
        }

        try {
            const signature = await window.ethereum.request({
                method: 'personal_sign',
                params: [message, this.account]
            });

            return {
                success: true,
                signature: signature
            };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    /**
     * 处理账户变化
     */
    handleAccountsChanged(accounts) {
        if (accounts.length === 0) {
            this.disconnectWallet();
        } else if (accounts[0] !== this.account) {
            this.account = accounts[0];
            console.log('👤 账户已切换:', this.account);
            window.dispatchEvent(new CustomEvent('nexusa:accountChanged', { 
                detail: { account: this.account } 
            }));
        }
    }

    /**
     * 处理链变化
     */
    handleChainChanged(chainId) {
        console.log('🔗 网络已切换:', chainId);
        window.location.reload();
    }

    /**
     * 获取连接状态
     */
    getConnectionStatus() {
        return {
            connected: this.connected,
            account: this.account,
            network: this.config.network,
            chainId: this.config.chainId
        };
    }
}

// 快捷函数
async function connectNexusa() {
    const connector = new NexusaConnector();
    return await connector.connectWallet();
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { NexusaConnector, connectNexusa };
} else {
    window.NexusaConnector = NexusaConnector;
    window.connectNexusa = connectNexusa;
}

console.log('🔗 NexusaConnector 已加载');
