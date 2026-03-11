/**
 * 硅基世界 - 智能合约交互模块
 * 
 * 封装与区块链合约的交互
 */

class ContractManager {
    constructor() {
        this.provider = null;
        this.signer = null;
        this.nftContract = null;
        this.marketplaceContract = null;
        this.nftAddress = null;
        this.marketplaceAddress = null;
    }

    /**
     * 初始化合约管理器
     * @param {string} rpcUrl - RPC 节点 URL
     * @param {object} wallet - 钱包对象 (需要有 signer)
     */
    async init(rpcUrl, wallet) {
        try {
            const ethers = window.ethers;
            
            // 默认使用本地网络
            const defaultRpcUrl = 'http://127.0.0.1:8545';
            
            // 创建 Provider
            this.provider = new ethers.JsonRpcProvider(rpcUrl || defaultRpcUrl);
            
            // 设置 Signer
            if (wallet && wallet.signer) {
                this.signer = wallet.signer;
            }
            
            console.log('✅ 合约管理器初始化成功');
            console.log('📡 RPC URL:', rpcUrl || defaultRpcUrl);
            return true;
        } catch (error) {
            console.error('❌ 合约管理器初始化失败:', error);
            return false;
        }
    }

    /**
     * 设置合约地址
     * @param {string} nftAddress - NFT 合约地址
     * @param {string} marketplaceAddress - 市场合约地址
     */
    setContractAddresses(nftAddress, marketplaceAddress) {
        this.nftAddress = nftAddress;
        this.marketplaceAddress = marketplaceAddress;
        console.log('📍 合约地址已设置');
        console.log('  NFT 合约:', nftAddress);
        console.log('  市场合约:', marketplaceAddress);
        
        // 保存到 localStorage 方便下次使用
        localStorage.setItem('nftContractAddress', nftAddress);
        localStorage.setItem('marketplaceContractAddress', marketplaceAddress);
    }
    
    /**
     * 从 localStorage 加载合约地址
     */
    loadContractAddresses() {
        const nftAddress = localStorage.getItem('nftContractAddress');
        const marketplaceAddress = localStorage.getItem('marketplaceContractAddress');
        
        if (nftAddress && marketplaceAddress) {
            this.nftAddress = nftAddress;
            this.marketplaceAddress = marketplaceAddress;
            console.log('📍 已从本地存储加载合约地址');
            return true;
        }
        return false;
    }

    /**
     * 加载 NFT 合约
     * @returns {Promise<boolean>}
     */
    async loadNFTContract() {
        if (!this.nftAddress) {
            console.error('❌ NFT 合约地址未设置');
            return false;
        }

        try {
            const ethers = window.ethers;
            
            // NFT 合约 ABI (最小化版本)
            const nftABI = [
                "function mint(address to, string memory tokenURI, string memory nftType) public returns (uint256)",
                "function ownerOf(uint256 tokenId) public view returns (address)",
                "function tokenURI(uint256 tokenId) public view returns (string)",
                "function getNFTInfo(uint256 tokenId) public view returns (tuple(uint256 tokenId, address creator, string nftType, uint256 createdAt, bool exists))",
                "function totalSupply() public view returns (uint256)",
                "function approve(address to, uint256 tokenId) public",
                "function getApproved(uint256 tokenId) public view returns (address)",
                "function isApprovedForAll(address owner, address operator) public view returns (bool)",
                "function setApprovalForAll(address operator, bool approved) public",
                "function balanceOf(address owner) public view returns (uint256)",
                
                // 事件
                "event NFTMinted(uint256 indexed tokenId, address indexed creator, address indexed owner, string nftType, string tokenURI)",
                "event Transfer(address indexed from, address indexed to, uint256 indexed tokenId)"
            ];

            // 创建合约实例
            if (this.signer) {
                this.nftContract = new ethers.Contract(this.nftAddress, nftABI, this.signer);
            } else {
                this.nftContract = new ethers.Contract(this.nftAddress, nftABI, this.provider);
            }

            console.log('✅ NFT 合约加载成功');
            return true;
        } catch (error) {
            console.error('❌ NFT 合约加载失败:', error);
            return false;
        }
    }

    /**
     * 加载市场合约
     * @returns {Promise<boolean>}
     */
    async loadMarketplaceContract() {
        if (!this.marketplaceAddress) {
            console.error('❌ 市场合约地址未设置');
            return false;
        }

        try {
            const ethers = window.ethers;
            
            // 市场合约 ABI (最小化版本)
            const marketplaceABI = [
                "function listNFT(address nftContract, uint256 tokenId, uint256 price, uint256 duration) public returns (uint256)",
                "function delistNFT(uint256 listingId) public",
                "function buyNFT(uint256 listingId) public payable",
                "function listings(uint256 listingId) public view returns (tuple(uint256 listingId, address seller, address nftContract, uint256 tokenId, uint256 price, bool active, uint256 createdAt, uint256 expiresAt))",
                "function getSellerListings(address seller) public view returns (uint256[])",
                
                // 事件
                "event Listed(uint256 indexed listingId, address indexed seller, address indexed nftContract, uint256 tokenId, uint256 price)",
                "event Sold(uint256 indexed listingId, address indexed seller, address indexed buyer, uint256 tokenId, uint256 price)"
            ];

            // 创建合约实例
            if (this.signer) {
                this.marketplaceContract = new ethers.Contract(this.marketplaceAddress, marketplaceABI, this.signer);
            } else {
                this.marketplaceContract = new ethers.Contract(this.marketplaceAddress, marketplaceABI, this.provider);
            }

            console.log('✅ 市场合约加载成功');
            return true;
        } catch (error) {
            console.error('❌ 市场合约加载失败:', error);
            return false;
        }
    }

    // ==================== NFT 操作 ====================

    /**
     * 铸造 NFT
     * @param {string} tokenURI - 元数据 URI
     * @param {string} nftType - NFT 类型
     * @returns {Promise<object>} 交易结果
     */
    async mintNFT(tokenURI, nftType) {
        if (!this.nftContract) {
            throw new Error('NFT 合约未加载');
        }

        try {
            console.log('🔨 开始铸造 NFT...');
            console.log('  tokenURI:', tokenURI);
            console.log('  nftType:', nftType);

            // 调用铸造函数
            const tx = await this.nftContract.mint(
                await this.signer.getAddress(),
                tokenURI,
                nftType
            );

            console.log('⏳ 等待交易确认...', tx.hash);

            // 等待交易确认
            const receipt = await tx.wait();

            // 解析事件
            const mintEvent = receipt.logs.find(log => {
                try {
                    const parsed = this.nftContract.interface.parseLog(log);
                    return parsed && parsed.name === 'NFTMinted';
                } catch {
                    return false;
                }
            });

            let tokenId = null;
            if (mintEvent) {
                const parsed = this.nftContract.interface.parseLog(mintEvent);
                tokenId = parsed.args.tokenId.toString();
            }

            console.log('✅ NFT 铸造成功!');
            console.log('  Token ID:', tokenId);
            console.log('  交易哈希:', receipt.hash);

            return {
                success: true,
                tokenId: tokenId,
                txHash: receipt.hash,
                receipt: receipt
            };
        } catch (error) {
            console.error('❌ NFT 铸造失败:', error);
            throw error;
        }
    }

    /**
     * 获取 NFT 信息
     * @param {number} tokenId - Token ID
     * @returns {Promise<object>} NFT 信息
     */
    async getNFTInfo(tokenId) {
        if (!this.nftContract) {
            throw new Error('NFT 合约未加载');
        }

        try {
            const info = await this.nftContract.getNFTInfo(tokenId);
            return {
                tokenId: info.tokenId.toString(),
                creator: info.creator,
                nftType: info.nftType,
                createdAt: new Date(info.createdAt * 1000),
                exists: info.exists
            };
        } catch (error) {
            console.error('❌ 获取 NFT 信息失败:', error);
            throw error;
        }
    }

    /**
     * 获取 NFT 所有者
     * @param {number} tokenId - Token ID
     * @returns {Promise<string>} 所有者地址
     */
    async getOwner(tokenId) {
        if (!this.nftContract) {
            throw new Error('NFT 合约未加载');
        }

        try {
            const owner = await this.nftContract.ownerOf(tokenId);
            return owner;
        } catch (error) {
            console.error('❌ 获取所有者失败:', error);
            throw error;
        }
    }

    /**
     * 获取总供应量
     * @returns {Promise<number>} 总供应量
     */
    async getTotalSupply() {
        if (!this.nftContract) {
            throw new Error('NFT 合约未加载');
        }

        try {
            const supply = await this.nftContract.totalSupply();
            return parseInt(supply.toString());
        } catch (error) {
            console.error('❌ 获取总供应量失败:', error);
            throw error;
        }
    }

    // ==================== 市场操作 ====================

    /**
     * 上架 NFT
     * @param {number} tokenId - Token ID
     * @param {string} price - 价格 (ETH)
     * @param {number} duration - 上架时长 (秒)
     * @returns {Promise<object>} 上架结果
     */
    async listNFT(tokenId, price, duration = 86400 * 7) {
        if (!this.marketplaceContract) {
            throw new Error('市场合约未加载');
        }

        try {
            console.log('🏪 开始上架 NFT...');
            console.log('  Token ID:', tokenId);
            console.log('  价格:', price, 'ETH');
            console.log('  时长:', duration, '秒');

            // 首先授权市场合约
            const approveTx = await this.nftContract.approve(
                this.marketplaceAddress,
                tokenId
            );
            await approveTx.wait();
            console.log('✅ 授权成功');

            // 上架 NFT
            const ethers = window.ethers;
            const listTx = await this.marketplaceContract.listNFT(
                this.nftAddress,
                tokenId,
                ethers.parseEther(price),
                duration
            );

            console.log('⏳ 等待交易确认...', listTx.hash);
            const receipt = await listTx.wait();

            // 解析事件
            const listEvent = receipt.logs.find(log => {
                try {
                    const parsed = this.marketplaceContract.interface.parseLog(log);
                    return parsed && parsed.name === 'Listed';
                } catch {
                    return false;
                }
            });

            let listingId = null;
            if (listEvent) {
                const parsed = this.marketplaceContract.interface.parseLog(listEvent);
                listingId = parsed.args.listingId.toString();
            }

            console.log('✅ NFT 上架成功!');
            console.log('  上架 ID:', listingId);

            return {
                success: true,
                listingId: listingId,
                txHash: receipt.hash
            };
        } catch (error) {
            console.error('❌ NFT 上架失败:', error);
            throw error;
        }
    }

    /**
     * 购买 NFT
     * @param {number} listingId - 上架 ID
     * @returns {Promise<object>} 购买结果
     */
    async buyNFT(listingId) {
        if (!this.marketplaceContract) {
            throw new Error('市场合约未加载');
        }

        try {
            console.log('🛒 开始购买 NFT...');
            console.log('  上架 ID:', listingId);

            // 获取上架信息
            const listing = await this.marketplaceContract.listings(listingId);
            
            const ethers = window.ethers;
            // 购买 (发送 ETH)
            const buyTx = await this.marketplaceContract.buyNFT(listingId, {
                value: listing.price
            });

            console.log('⏳ 等待交易确认...', buyTx.hash);
            const receipt = await buyTx.wait();

            console.log('✅ NFT 购买成功!');

            return {
                success: true,
                txHash: receipt.hash
            };
        } catch (error) {
            console.error('❌ NFT 购买失败:', error);
            throw error;
        }
    }

    /**
     * 获取上架信息
     * @param {number} listingId - 上架 ID
     * @returns {Promise<object>} 上架信息
     */
    async getListing(listingId) {
        if (!this.marketplaceContract) {
            throw new Error('市场合约未加载');
        }

        try {
            const listing = await this.marketplaceContract.listings(listingId);
            const ethers = window.ethers;
            
            return {
                listingId: listing.listingId.toString(),
                seller: listing.seller,
                nftContract: listing.nftContract,
                tokenId: listing.tokenId.toString(),
                price: ethers.formatEther(listing.price),
                active: listing.active,
                createdAt: new Date(listing.createdAt * 1000),
                expiresAt: new Date(listing.expiresAt * 1000)
            };
        } catch (error) {
            console.error('❌ 获取上架信息失败:', error);
            throw error;
        }
    }

    // ==================== 工具方法 ====================

    /**
     * 获取当前网络
     * @returns {Promise<object>} 网络信息
     */
    async getNetwork() {
        if (!this.provider) {
            throw new Error('Provider 未初始化');
        }

        try {
            const network = await this.provider.getNetwork();
            return {
                name: network.name,
                chainId: parseInt(network.chainId.toString())
            };
        } catch (error) {
            console.error('❌ 获取网络信息失败:', error);
            throw error;
        }
    }

    /**
     * 获取余额
     * @param {string} address - 地址
     * @returns {Promise<string>} 余额 (ETH)
     */
    async getBalance(address) {
        if (!this.provider) {
            throw new Error('Provider 未初始化');
        }

        try {
            const ethers = window.ethers;
            const balance = await this.provider.getBalance(address);
            return ethers.formatEther(balance);
        } catch (error) {
            console.error('❌ 获取余额失败:', error);
            throw error;
        }
    }
}

// 导出
window.ContractManager = ContractManager;
console.log('📜 ContractManager 模块已加载');
