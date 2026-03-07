/**
 * UGC 内容系统
 * 
 * 用户创作内容、审核、推荐、版权
 */

const { EventEmitter } = require('events');

/**
 * UGC 内容管理器
 */
class UGCManager extends EventEmitter {
    constructor() {
        super();
        this.contents = new Map(); // contentId -> content
        this.userContents = new Map(); // userId -> [contentIds]
        this.categories = new Map(); // categoryId -> category
        this.nextContentId = 1;
        this.nextCategoryId = 1;
        
        this.config = {
            maxContentLength: 10000,
            reviewRequired: true,
            copyrightProtection: true
        };
    }
    
    /**
     * 创建分类
     */
    createCategory(name, description, parentCategoryId = null) {
        const categoryId = `cat_${this.nextCategoryId++}`;
        
        const category = {
            id: categoryId,
            name,
            description,
            parentCategoryId,
            subCategories: [],
            contentCount: 0,
            createdAt: Date.now()
        };
        
        this.categories.set(categoryId, category);
        
        if (parentCategoryId) {
            const parent = this.categories.get(parentCategoryId);
            if (parent) {
                parent.subCategories.push(categoryId);
            }
        }
        
        this.emit('category_created', category);
        
        return category;
    }
    
    /**
     * 发布内容
     */
    publishContent(userId, title, content, type, categoryId, tags = []) {
        if (content.length > this.config.maxContentLength) {
            return { success: false, error: '内容超长' };
        }
        
        const contentId = `content_${this.nextContentId++}`;
        
        const contentData = {
            id: contentId,
            userId,
            title,
            content,
            type, // article, video, image, audio, nft
            categoryId,
            tags,
            status: this.config.reviewRequired ? 'pending' : 'published',
            viewCount: 0,
            likeCount: 0,
            commentCount: 0,
            shareCount: 0,
            earnings: 0,
            createdAt: Date.now(),
            publishedAt: null,
            reviewedAt: null,
            reviewedBy: null
        };
        
        this.contents.set(contentId, contentData);
        
        if (!this.userContents.has(userId)) {
            this.userContents.set(userId, []);
        }
        this.userContents.get(userId).push(contentId);
        
        // 更新分类统计
        const category = this.categories.get(categoryId);
        if (category) {
            category.contentCount++;
        }
        
        this.emit('content_published', contentData);
        
        return { success: true, content: contentData };
    }
    
    /**
     * 审核内容
     */
    reviewContent(contentId, reviewerId, approved, reason = '') {
        const content = this.contents.get(contentId);
        if (!content) {
            return { success: false, error: '内容不存在' };
        }
        
        if (content.status !== 'pending') {
            return { success: false, error: '内容无需审核' };
        }
        
        content.status = approved ? 'published' : 'rejected';
        content.reviewedAt = Date.now();
        content.reviewedBy = reviewerId;
        content.reviewReason = reason;
        
        if (approved) {
            content.publishedAt = Date.now();
            this.emit('content_approved', { contentId, reviewerId });
        } else {
            this.emit('content_rejected', { contentId, reviewerId, reason });
        }
        
        return { success: true, status: content.status };
    }
    
    /**
     * 浏览内容
     */
    viewContent(contentId) {
        const content = this.contents.get(contentId);
        if (content) {
            content.viewCount++;
        }
        return content;
    }
    
    /**
     * 点赞内容
     */
    likeContent(contentId, userId) {
        const content = this.contents.get(contentId);
        if (!content) {
            return { success: false, error: '内容不存在' };
        }
        
        if (!content.likedBy) {
            content.likedBy = new Set();
        }
        
        if (content.likedBy.has(userId)) {
            content.likedBy.delete(userId);
            content.likeCount--;
            this.emit('content_unliked', { contentId, userId });
        } else {
            content.likedBy.add(userId);
            content.likeCount++;
            this.emit('content_liked', { contentId, userId });
        }
        
        return { success: true, likeCount: content.likeCount };
    }
    
    /**
     * 获取内容列表
     */
    getContents(filters = {}) {
        let contents = Array.from(this.contents.values());
        
        // 状态过滤
        if (filters.status) {
            contents = contents.filter(c => c.status === filters.status);
        }
        
        // 分类过滤
        if (filters.categoryId) {
            contents = contents.filter(c => c.categoryId === filters.categoryId);
        }
        
        // 用户过滤
        if (filters.userId) {
            contents = contents.filter(c => c.userId === filters.userId);
        }
        
        // 类型过滤
        if (filters.type) {
            contents = contents.filter(c => c.type === filters.type);
        }
        
        // 排序
        if (filters.sortBy) {
            switch (filters.sortBy) {
                case 'latest':
                    contents.sort((a, b) => b.createdAt - a.createdAt);
                    break;
                case 'popular':
                    contents.sort((a, b) => b.viewCount - a.viewCount);
                    break;
                case 'liked':
                    contents.sort((a, b) => b.likeCount - a.likeCount);
                    break;
                case 'earnings':
                    contents.sort((a, b) => b.earnings - a.earnings);
                    break;
            }
        }
        
        // 分页
        const page = filters.page || 1;
        const limit = filters.limit || 20;
        const start = (page - 1) * limit;
        
        return {
            contents: contents.slice(start, start + limit),
            total: contents.length,
            page,
            limit,
            totalPages: Math.ceil(contents.length / limit)
        };
    }
    
    /**
     * 获取用户内容统计
     */
    getUserContentStats(userId) {
        const contentIds = this.userContents.get(userId) || [];
        const contents = contentIds.map(id => this.contents.get(id)).filter(Boolean);
        
        return {
            totalContents: contents.length,
            totalViews: contents.reduce((sum, c) => sum + c.viewCount, 0),
            totalLikes: contents.reduce((sum, c) => sum + c.likeCount, 0),
            totalEarnings: contents.reduce((sum, c) => sum + c.earnings, 0),
            publishedCount: contents.filter(c => c.status === 'published').length,
            pendingCount: contents.filter(c => c.status === 'pending').length
        };
    }
    
    /**
     * 添加收益
     */
    addEarnings(contentId, amount) {
        const content = this.contents.get(contentId);
        if (!content) {
            return { success: false, error: '内容不存在' };
        }
        
        content.earnings += amount;
        
        this.emit('earnings_added', { contentId, amount });
        
        return { success: true, earnings: content.earnings };
    }
    
    /**
     * 清除
     */
    clear() {
        this.contents.clear();
        this.userContents.clear();
        this.categories.clear();
    }
}

/**
 * 创作者经济系统
 */
class CreatorEconomy extends EventEmitter {
    constructor() {
        super();
        this.creators = new Map(); // creatorId -> creator
        this.revenueStreams = new Map(); // streamId -> stream
        this.payouts = new Map(); // payoutId -> payout
        this.nextStreamId = 1;
        this.nextPayoutId = 1;
        
        this.config = {
            minPayout: 100, // 最低提现金额
            platformFee: 0.1, // 平台抽成 10%
            revenueShare: {
                views: 0.001, // 每浏览 0.001 SIL
                likes: 0.01, // 每点赞 0.01 SIL
                shares: 0.05 // 每分享 0.05 SIL
            }
        };
    }
    
    /**
     * 注册创作者
     */
    registerCreator(userId, name, description = '') {
        const creator = {
            id: userId,
            name,
            description,
            followers: 0,
            totalEarnings: 0,
            pendingEarnings: 0,
            withdrawnEarnings: 0,
            level: 1,
            verified: false,
            createdAt: Date.now()
        };
        
        this.creators.set(userId, creator);
        
        this.emit('creator_registered', creator);
        
        return creator;
    }
    
    /**
     * 计算收益
     */
    calculateRevenue(contentId, action, count = 1) {
        const rate = this.config.revenueShare[action];
        if (!rate) return 0;
        
        const grossRevenue = rate * count;
        const platformFee = grossRevenue * this.config.platformFee;
        const netRevenue = grossRevenue - platformFee;
        
        return {
            grossRevenue,
            platformFee,
            netRevenue
        };
    }
    
    /**
     * 添加收益
     */
    addRevenue(creatorId, contentId, action, count = 1) {
        const creator = this.creators.get(creatorId);
        if (!creator) {
            return { success: false, error: '创作者不存在' };
        }
        
        const revenue = this.calculateRevenue(contentId, action, count);
        
        creator.pendingEarnings += revenue.netRevenue;
        creator.totalEarnings += revenue.netRevenue;
        
        // 创建收益记录
        const streamId = `stream_${this.nextStreamId++}`;
        const stream = {
            id: streamId,
            creatorId,
            contentId,
            action,
            count,
            revenue: revenue.netRevenue,
            platformFee: revenue.platformFee,
            createdAt: Date.now()
        };
        
        this.revenueStreams.set(streamId, stream);
        
        this.emit('revenue_added', stream);
        
        return { success: true, revenue };
    }
    
    /**
     * 提现
     */
    requestPayout(creatorId, amount) {
        const creator = this.creators.get(creatorId);
        if (!creator) {
            return { success: false, error: '创作者不存在' };
        }
        
        if (amount < this.config.minPayout) {
            return { success: false, error: `最低提现${this.config.minPayout} SIL` };
        }
        
        if (amount > creator.pendingEarnings) {
            return { success: false, error: '余额不足' };
        }
        
        creator.pendingEarnings -= amount;
        creator.withdrawnEarnings += amount;
        
        const payoutId = `payout_${this.nextPayoutId++}`;
        const payout = {
            id: payoutId,
            creatorId,
            amount,
            status: 'pending',
            requestedAt: Date.now(),
            processedAt: null
        };
        
        this.payouts.set(payoutId, payout);
        
        this.emit('payout_requested', payout);
        
        return { success: true, payout };
    }
    
    /**
     * 处理提现
     */
    processPayout(payoutId, approved = true) {
        const payout = this.payouts.get(payoutId);
        if (!payout) {
            return { success: false, error: '提现记录不存在' };
        }
        
        payout.status = approved ? 'completed' : 'rejected';
        payout.processedAt = Date.now();
        
        this.emit('payout_processed', payout);
        
        return { success: true, payout };
    }
    
    /**
     * 获取创作者统计
     */
    getCreatorStats(creatorId) {
        const creator = this.creators.get(creatorId);
        if (!creator) return null;
        
        const streams = Array.from(this.revenueStreams.values())
            .filter(s => s.creatorId === creatorId);
        
        return {
            ...creator,
            totalStreams: streams.length,
            totalRevenue: streams.reduce((sum, s) => sum + s.revenue, 0),
            totalPlatformFee: streams.reduce((sum, s) => sum + s.platformFee, 0)
        };
    }
    
    /**
     * 更新配置
     */
    updateConfig(newConfig) {
        Object.assign(this.config, newConfig);
        this.emit('config_updated', this.config);
    }
    
    /**
     * 清除
     */
    clear() {
        this.creators.clear();
        this.revenueStreams.clear();
        this.payouts.clear();
    }
}

module.exports = {
    UGCManager,
    CreatorEconomy
};

console.log('UGC 内容系统已加载');
