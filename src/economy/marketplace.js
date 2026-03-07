/**
 * NFT 市场系统
 * 
 * 高级市场功能
 */

const { EventEmitter } = require('events');

/**
 * NFT 市场管理器
 */
class Marketplace extends EventEmitter {
    constructor() {
        super();
        this.listings = new Map(); // listingId -> listing
        this.orders = new Map(); // orderId -> order
        this.collections = new Map(); // collectionId -> collection
        this.sales = new Map(); // saleId -> sale
        
        this.nextListingId = 1;
        this.nextOrderId = 1;
        this.nextSaleId = 1;
        
        // 统计数据
        this.stats = {
            totalVolume: 0,
            totalSales: 0,
            activeListings: 0,
            totalUsers: 0
        };
    }
    
    /**
     * 创建上架
     */
    createListing(sellerId, nftId, price, currency = 'SIL', duration = 7 * 24 * 60 * 60 * 1000) {
        const listingId = `listing_${this.nextListingId++}`;
        
        const listing = {
            id: listingId,
            sellerId,
            nftId,
            price,
            currency,
            status: 'active',
            createdAt: Date.now(),
            expiresAt: Date.now() + duration,
            views: 0,
            favorites: 0
        };
        
        this.listings.set(listingId, listing);
        this.stats.activeListings++;
        
        this.emit('listing_created', listing);
        
        return listing;
    }
    
    /**
     * 购买上架
     */
    purchaseListing(listingId, buyerId) {
        const listing = this.listings.get(listingId);
        if (!listing || listing.status !== 'active') {
            return { success: false, error: '上架无效' };
        }
        
        // 检查是否过期
        if (Date.now() > listing.expiresAt) {
            listing.status = 'expired';
            this.stats.activeListings--;
            return { success: false, error: '上架已过期' };
        }
        
        // 创建销售记录
        const saleId = `sale_${this.nextSaleId++}`;
        const sale = {
            id: saleId,
            listingId,
            nftId: listing.nftId,
            sellerId: listing.sellerId,
            buyerId,
            price: listing.price,
            currency: listing.currency,
            timestamp: Date.now(),
            status: 'completed'
        };
        
        this.sales.set(saleId, sale);
        
        // 更新上架状态
        listing.status = 'sold';
        this.stats.activeListings--;
        
        // 更新统计
        this.stats.totalVolume += listing.price;
        this.stats.totalSales++;
        
        this.emit('listing_purchased', { listing, sale });
        
        return { success: true, sale };
    }
    
    /**
     * 取消上架
     */
    cancelListing(listingId, sellerId) {
        const listing = this.listings.get(listingId);
        if (!listing || listing.sellerId !== sellerId) {
            return { success: false, error: '无权操作' };
        }
        
        if (listing.status !== 'active') {
            return { success: false, error: '上架已失效' };
        }
        
        listing.status = 'cancelled';
        this.stats.activeListings--;
        
        this.emit('listing_cancelled', listing);
        
        return { success: true };
    }
    
    /**
     * 搜索上架
     */
    searchListings(filters = {}) {
        let results = Array.from(this.listings.values());
        
        // 状态过滤
        if (filters.status) {
            results = results.filter(l => l.status === filters.status);
        }
        
        // 价格范围
        if (filters.minPrice !== undefined) {
            results = results.filter(l => l.price >= filters.minPrice);
        }
        if (filters.maxPrice !== undefined) {
            results = results.filter(l => l.price <= filters.maxPrice);
        }
        
        // NFT 类型过滤
        if (filters.nftType) {
            results = results.filter(l => l.nftId.startsWith(filters.nftType));
        }
        
        // 卖家过滤
        if (filters.sellerId) {
            results = results.filter(l => l.sellerId === filters.sellerId);
        }
        
        // 排序
        if (filters.sortBy) {
            switch (filters.sortBy) {
                case 'price_asc':
                    results.sort((a, b) => a.price - b.price);
                    break;
                case 'price_desc':
                    results.sort((a, b) => b.price - a.price);
                    break;
                case 'newest':
                    results.sort((a, b) => b.createdAt - a.createdAt);
                    break;
                case 'oldest':
                    results.sort((a, b) => a.createdAt - b.createdAt);
                    break;
            }
        }
        
        // 分页
        const page = filters.page || 1;
        const limit = filters.limit || 20;
        const start = (page - 1) * limit;
        const end = start + limit;
        
        return {
            results: results.slice(start, end),
            total: results.length,
            page,
            limit,
            totalPages: Math.ceil(results.length / limit)
        };
    }
    
    /**
     * 获取上架详情
     */
    getListing(listingId) {
        const listing = this.listings.get(listingId);
        if (listing) {
            listing.views++;
        }
        return listing;
    }
    
    /**
     * 收藏上架
     */
    favoriteListing(listingId, userId) {
        const listing = this.listings.get(listingId);
        if (!listing) {
            return { success: false, error: '上架不存在' };
        }
        
        if (!listing.favoritedBy) {
            listing.favoritedBy = new Set();
        }
        
        if (listing.favoritedBy.has(userId)) {
            listing.favoritedBy.delete(userId);
            listing.favorites--;
            this.emit('listing_unfavorited', { listingId, userId });
        } else {
            listing.favoritedBy.add(userId);
            listing.favorites++;
            this.emit('listing_favorited', { listingId, userId });
        }
        
        return { success: true, favorites: listing.favorites };
    }
    
    /**
     * 创建拍卖
     */
    createAuction(sellerId, nftId, startingPrice, duration = 3 * 24 * 60 * 60 * 1000, reservePrice = null) {
        const auctionId = `auction_${this.nextOrderId++}`;
        
        const auction = {
            id: auctionId,
            type: 'auction',
            sellerId,
            nftId,
            startingPrice,
            currentPrice: startingPrice,
            highestBidder: null,
            reservePrice,
            status: 'active',
            createdAt: Date.now(),
            expiresAt: Date.now() + duration,
            bids: []
        };
        
        this.orders.set(auctionId, auction);
        
        this.emit('auction_created', auction);
        
        return auction;
    }
    
    /**
     * 竞价
     */
    placeBid(auctionId, bidderId, amount) {
        const auction = this.orders.get(auctionId);
        if (!auction || auction.type !== 'auction') {
            return { success: false, error: '拍卖无效' };
        }
        
        if (auction.status !== 'active') {
            return { success: false, error: '拍卖已结束' };
        }
        
        if (Date.now() > auction.expiresAt) {
            auction.status = 'expired';
            return { success: false, error: '拍卖已过期' };
        }
        
        if (amount <= auction.currentPrice) {
            return { success: false, error: '竞价必须高于当前价格' };
        }
        
        if (auction.reservePrice && amount < auction.reservePrice) {
            return { success: false, error: '竞价未达到保留价' };
        }
        
        // 创建竞价记录
        const bid = {
            bidderId,
            amount,
            timestamp: Date.now()
        };
        
        auction.bids.push(bid);
        auction.currentPrice = amount;
        auction.highestBidder = bidderId;
        
        this.emit('bid_placed', { auctionId, bid });
        
        return { success: true, currentPrice: amount };
    }
    
    /**
     * 结束拍卖
     */
    endAuction(auctionId) {
        const auction = this.orders.get(auctionId);
        if (!auction || auction.type !== 'auction') {
            return { success: false, error: '拍卖无效' };
        }
        
        if (auction.status !== 'active') {
            return { success: false, error: '拍卖已结束' };
        }
        
        auction.status = 'ended';
        
        if (auction.highestBidder) {
            // 创建销售记录
            const saleId = `sale_${this.nextSaleId++}`;
            const sale = {
                id: saleId,
                auctionId,
                nftId: auction.nftId,
                sellerId: auction.sellerId,
                buyerId: auction.highestBidder,
                price: auction.currentPrice,
                currency: 'SIL',
                timestamp: Date.now(),
                status: 'completed'
            };
            
            this.sales.set(saleId, sale);
            
            this.stats.totalVolume += auction.currentPrice;
            this.stats.totalSales++;
            
            this.emit('auction_ended', { auction, sale });
            
            return { success: true, sale };
        } else {
            this.emit('auction_ended', { auction, sale: null });
            return { success: false, error: '无竞价' };
        }
    }
    
    /**
     * 获取统计数据
     */
    getStats() {
        return {
            ...this.stats,
            activeAuctions: Array.from(this.orders.values()).filter(
                o => o.type === 'auction' && o.status === 'active'
            ).length
        };
    }
    
    /**
     * 获取销售历史
     */
    getSalesHistory(nftId = null, limit = 50) {
        let sales = Array.from(this.sales.values());
        
        if (nftId) {
            sales = sales.filter(s => s.nftId === nftId);
        }
        
        // 按时间排序
        sales.sort((a, b) => b.timestamp - a.timestamp);
        
        return sales.slice(0, limit);
    }
    
    /**
     * 清除
     */
    dispose() {
        this.listings.clear();
        this.orders.clear();
        this.collections.clear();
        this.sales.clear();
    }
}

module.exports = {
    Marketplace
};

console.log('NFT 市场系统已加载');
