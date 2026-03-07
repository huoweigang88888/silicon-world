/**
 * 交易系统
 * 
 * 批量交易、订单管理、交易历史
 */

const { EventEmitter } = require('events');

/**
 * 订单管理器
 */
class OrderManager extends EventEmitter {
    constructor() {
        super();
        this.orders = new Map(); // orderId -> order
        this.orderHistory = new Map(); // playerId -> [orders]
        this.nextOrderId = 1;
    }
    
    /**
     * 创建订单
     */
    createOrder(buyerId, items, totalAmount, currency = 'SIL') {
        const orderId = `order_${this.nextOrderId++}`;
        
        const order = {
            id: orderId,
            buyerId,
            items, // [{sellerId, nftId, price}]
            totalAmount,
            currency,
            status: 'pending', // pending, processing, completed, cancelled, failed
            createdAt: Date.now(),
            updatedAt: Date.now(),
            paidAt: null,
            completedAt: null
        };
        
        this.orders.set(orderId, order);
        
        // 添加到历史记录
        if (!this.orderHistory.has(buyerId)) {
            this.orderHistory.set(buyerId, []);
        }
        this.orderHistory.get(buyerId).push(order);
        
        // 添加到每个卖家的历史记录
        for (const item of items) {
            if (!this.orderHistory.has(item.sellerId)) {
                this.orderHistory.set(item.sellerId, []);
            }
            this.orderHistory.get(item.sellerId).push(order);
        }
        
        this.emit('order_created', order);
        
        return order;
    }
    
    /**
     * 更新订单状态
     */
    updateOrderStatus(orderId, status, userId) {
        const order = this.orders.get(orderId);
        if (!order) {
            return { success: false, error: '订单不存在' };
        }
        
        // 状态转换验证
        const validTransitions = {
            'pending': ['processing', 'cancelled'],
            'processing': ['completed', 'failed'],
            'completed': [],
            'cancelled': [],
            'failed': ['pending'] // 允许重试
        };
        
        if (!validTransitions[order.status].includes(status)) {
            return { success: false, error: '无效的状态转换' };
        }
        
        order.status = status;
        order.updatedAt = Date.now();
        
        if (status === 'completed') {
            order.completedAt = Date.now();
        }
        
        this.emit('order_updated', { order, status });
        
        return { success: true, order };
    }
    
    /**
     * 取消订单
     */
    cancelOrder(orderId, userId, reason = '') {
        const order = this.orders.get(orderId);
        if (!order) {
            return { success: false, error: '订单不存在' };
        }
        
        if (order.buyerId !== userId) {
            return { success: false, error: '无权操作' };
        }
        
        if (order.status !== 'pending') {
            return { success: false, error: '订单无法取消' };
        }
        
        order.status = 'cancelled';
        order.updatedAt = Date.now();
        order.cancelReason = reason;
        
        this.emit('order_cancelled', { order, reason });
        
        return { success: true };
    }
    
    /**
     * 获取订单
     */
    getOrder(orderId) {
        return this.orders.get(orderId);
    }
    
    /**
     * 获取用户订单历史
     */
    getUserOrders(userId, status = null, limit = 50) {
        const orders = this.orderHistory.get(userId) || [];
        
        let filtered = orders;
        if (status) {
            filtered = orders.filter(o => o.status === status);
        }
        
        // 按时间排序
        filtered.sort((a, b) => b.createdAt - a.createdAt);
        
        return filtered.slice(0, limit);
    }
    
    /**
     * 批量交易
     */
    createBatchOrder(buyerId, listings) {
        const items = [];
        let totalAmount = 0;
        
        for (const listing of listings) {
            items.push({
                sellerId: listing.sellerId,
                nftId: listing.nftId,
                price: listing.price
            });
            totalAmount += listing.price;
        }
        
        return this.createOrder(buyerId, items, totalAmount);
    }
    
    /**
     * 获取统计
     */
    getStats() {
        const allOrders = Array.from(this.orders.values());
        
        return {
            totalOrders: allOrders.length,
            pendingOrders: allOrders.filter(o => o.status === 'pending').length,
            completedOrders: allOrders.filter(o => o.status === 'completed').length,
            cancelledOrders: allOrders.filter(o => o.status === 'cancelled').length,
            failedOrders: allOrders.filter(o => o.status === 'failed').length,
            totalVolume: allOrders
                .filter(o => o.status === 'completed')
                .reduce((sum, o) => sum + o.totalAmount, 0)
        };
    }
    
    /**
     * 清除
     */
    clear() {
        this.orders.clear();
        this.orderHistory.clear();
    }
}

/**
 * 交易历史管理器
 */
class TradeHistory extends EventEmitter {
    constructor() {
        super();
        this.trades = new Map(); // tradeId -> trade
        this.userTrades = new Map(); // playerId -> [tradeIds]
        this.nextTradeId = 1;
    }
    
    /**
     * 记录交易
     */
    recordTrade(sellerId, buyerId, nftId, price, currency = 'SIL') {
        const tradeId = `trade_${this.nextTradeId++}`;
        
        const trade = {
            id: tradeId,
            sellerId,
            buyerId,
            nftId,
            price,
            currency,
            timestamp: Date.now(),
            status: 'completed'
        };
        
        this.trades.set(tradeId, trade);
        
        // 添加到用户历史记录
        if (!this.userTrades.has(sellerId)) {
            this.userTrades.set(sellerId, []);
        }
        this.userTrades.get(sellerId).push(tradeId);
        
        if (!this.userTrades.has(buyerId)) {
            this.userTrades.set(buyerId, []);
        }
        this.userTrades.get(buyerId).push(tradeId);
        
        this.emit('trade_recorded', trade);
        
        return trade;
    }
    
    /**
     * 获取用户交易历史
     */
    getUserTrades(userId, limit = 50) {
        const tradeIds = this.userTrades.get(userId) || [];
        const trades = tradeIds.map(id => this.trades.get(id)).filter(Boolean);
        
        // 按时间排序
        trades.sort((a, b) => b.timestamp - a.timestamp);
        
        return trades.slice(0, limit);
    }
    
    /**
     * 获取 NFT 交易历史
     */
    getNFTTrades(nftId, limit = 50) {
        const trades = Array.from(this.trades.values())
            .filter(t => t.nftId === nftId);
        
        trades.sort((a, b) => b.timestamp - a.timestamp);
        
        return trades.slice(0, limit);
    }
    
    /**
     * 获取价格历史
     */
    getPriceHistory(nftId) {
        const trades = this.getNFTTrades(nftId);
        
        return trades.map(t => ({
            timestamp: t.timestamp,
            price: t.price,
            currency: t.currency
        }));
    }
    
    /**
     * 获取统计数据
     */
    getStats(userId = null) {
        if (userId) {
            const trades = this.getUserTrades(userId, 1000);
            return {
                totalTrades: trades.length,
                totalVolume: trades.reduce((sum, t) => sum + t.price, 0),
                asSeller: trades.filter(t => t.sellerId === userId).length,
                asBuyer: trades.filter(t => t.buyerId === userId).length,
                avgPrice: trades.length > 0 ? 
                    trades.reduce((sum, t) => sum + t.price, 0) / trades.length : 0
            };
        } else {
            const allTrades = Array.from(this.trades.values());
            return {
                totalTrades: allTrades.length,
                totalVolume: allTrades.reduce((sum, t) => sum + t.price, 0),
                uniqueSellers: new Set(allTrades.map(t => t.sellerId)).size,
                uniqueBuyers: new Set(allTrades.map(t => t.buyerId)).size
            };
        }
    }
    
    /**
     * 清除
     */
    clear() {
        this.trades.clear();
        this.userTrades.clear();
    }
}

/**
 * 通知系统
 */
class TradeNotification extends EventEmitter {
    constructor() {
        super();
        this.notifications = new Map(); // playerId -> [notifications]
        this.maxNotifications = 100;
    }
    
    /**
     * 发送通知
     */
    sendNotification(playerId, type, data) {
        const notification = {
            id: `notif_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            playerId,
            type, // order_created, order_completed, bid_placed, etc.
            data,
            timestamp: Date.now(),
            read: false
        };
        
        if (!this.notifications.has(playerId)) {
            this.notifications.set(playerId, []);
        }
        
        const playerNotifs = this.notifications.get(playerId);
        playerNotifs.push(notification);
        
        // 限制数量
        while (playerNotifs.length > this.maxNotifications) {
            playerNotifs.shift();
        }
        
        this.emit('notification_sent', notification);
        
        return notification;
    }
    
    /**
     * 获取通知
     */
    getNotifications(playerId, unreadOnly = false) {
        const notifications = this.notifications.get(playerId) || [];
        
        if (unreadOnly) {
            return notifications.filter(n => !n.read);
        }
        
        return notifications;
    }
    
    /**
     * 标记为已读
     */
    markAsRead(playerId, notificationId = null) {
        const notifications = this.notifications.get(playerId) || [];
        
        if (notificationId) {
            const notification = notifications.find(n => n.id === notificationId);
            if (notification) {
                notification.read = true;
            }
        } else {
            notifications.forEach(n => n.read = true);
        }
    }
    
    /**
     * 获取未读数量
     */
    getUnreadCount(playerId) {
        const notifications = this.notifications.get(playerId) || [];
        return notifications.filter(n => !n.read).length;
    }
    
    /**
     * 清除
     */
    clear() {
        this.notifications.clear();
    }
}

module.exports = {
    OrderManager,
    TradeHistory,
    TradeNotification
};

console.log('交易系统已加载');
