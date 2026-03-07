/**
 * 经济平衡系统
 * 
 * 通胀控制、奖励机制、税收系统、经济监控
 */

const { EventEmitter } = require('events');

/**
 * 通胀控制系统
 */
class InflationControl extends EventEmitter {
    constructor(options = {}) {
        super();
        this.options = {
            targetInflationRate: options.targetInflationRate || 0.05, // 5% 年通胀率
            maxMoneySupply: options.maxMoneySupply || 1000000000, // 10 亿上限
            ...options
        };
        
        this.moneySupply = 0; // 货币供应量
        this.inflationRate = 0;
        this.lastAdjustment = Date.now();
        this.history = [];
    }
    
    /**
     * 更新货币供应量
     */
    updateMoneySupply(amount) {
        const oldSupply = this.moneySupply;
        this.moneySupply += amount;
        
        // 检查是否超过上限
        if (this.moneySupply > this.options.maxMoneySupply) {
            this.emit('supply_limit_warning', {
                current: this.moneySupply,
                max: this.options.maxMoneySupply
            });
        }
        
        // 计算通胀率
        if (oldSupply > 0) {
            this.inflationRate = (this.moneySupply - oldSupply) / oldSupply;
        }
        
        // 记录历史
        this.history.push({
            timestamp: Date.now(),
            supply: this.moneySupply,
            inflationRate: this.inflationRate
        });
        
        // 限制历史记录
        if (this.history.length > 1000) {
            this.history.shift();
        }
        
        this.emit('supply_updated', {
            supply: this.moneySupply,
            inflationRate: this.inflationRate
        });
    }
    
    /**
     * 获取建议的货币调整
     */
    getSuggestedAdjustment() {
        const currentRate = this.inflationRate;
        const targetRate = this.options.targetInflationRate;
        
        if (currentRate > targetRate * 1.5) {
            // 通胀过高，建议收紧
            return {
                action: 'tighten',
                reason: '通胀率过高',
                suggestedRate: currentRate - targetRate
            };
        } else if (currentRate < targetRate * 0.5) {
            // 通胀过低，建议放松
            return {
                action: 'loosen',
                reason: '通胀率过低',
                suggestedRate: targetRate - currentRate
            };
        }
        
        return {
            action: 'maintain',
            reason: '通胀率正常'
        };
    }
    
    /**
     * 获取统计数据
     */
    getStats() {
        return {
            moneySupply: this.moneySupply,
            inflationRate: this.inflationRate,
            targetRate: this.options.targetInflationRate,
            maxSupply: this.options.maxMoneySupply,
            utilizationRate: this.moneySupply / this.options.maxMoneySupply
        };
    }
}

/**
 * 奖励系统
 */
class RewardSystem extends EventEmitter {
    constructor() {
        super();
        this.rewardPools = new Map(); // poolId -> pool
        this.userRewards = new Map(); // userId -> [rewards]
        this.nextPoolId = 1;
    }
    
    /**
     * 创建奖励池
     */
    createRewardPool(name, totalAmount, currency = 'SIL', duration = 30 * 24 * 60 * 60 * 1000) {
        const poolId = `pool_${this.nextPoolId++}`;
        
        const pool = {
            id: poolId,
            name,
            totalAmount,
            remainingAmount: totalAmount,
            currency,
            status: 'active',
            createdAt: Date.now(),
            expiresAt: Date.now() + duration,
            participants: new Set(),
            totalClaims: 0
        };
        
        this.rewardPools.set(poolId, pool);
        
        this.emit('pool_created', pool);
        
        return pool;
    }
    
    /**
     * 参与奖励池
     */
    joinPool(poolId, userId) {
        const pool = this.rewardPools.get(poolId);
        if (!pool || pool.status !== 'active') {
            return { success: false, error: '奖励池无效' };
        }
        
        pool.participants.add(userId);
        
        this.emit('pool_joined', { poolId, userId });
        
        return { success: true };
    }
    
    /**
     * 领取奖励
     */
    claimReward(poolId, userId, amount) {
        const pool = this.rewardPools.get(poolId);
        if (!pool) {
            return { success: false, error: '奖励池不存在' };
        }
        
        if (pool.status !== 'active') {
            return { success: false, error: '奖励池已失效' };
        }
        
        if (amount > pool.remainingAmount) {
            return { success: false, error: '奖励池余额不足' };
        }
        
        pool.remainingAmount -= amount;
        pool.totalClaims++;
        
        // 记录用户奖励
        if (!this.userRewards.has(userId)) {
            this.userRewards.set(userId, []);
        }
        this.userRewards.get(userId).push({
            poolId,
            amount,
            currency: pool.currency,
            timestamp: Date.now()
        });
        
        // 检查是否分配完毕
        if (pool.remainingAmount <= 0) {
            pool.status = 'exhausted';
            this.emit('pool_exhausted', { poolId });
        }
        
        this.emit('reward_claimed', {
            poolId,
            userId,
            amount
        });
        
        return { success: true, amount };
    }
    
    /**
     * 获取用户奖励历史
     */
    getUserRewards(userId, limit = 50) {
        const rewards = this.userRewards.get(userId) || [];
        return rewards.slice(-limit);
    }
    
    /**
     * 获取奖励池统计
     */
    getPoolStats(poolId) {
        const pool = this.rewardPools.get(poolId);
        if (!pool) return null;
        
        return {
            id: pool.id,
            name: pool.name,
            totalAmount: pool.totalAmount,
            remainingAmount: pool.remainingAmount,
            distributedAmount: pool.totalAmount - pool.remainingAmount,
            participants: pool.participants.size,
            totalClaims: pool.totalClaims,
            status: pool.status,
            progress: (pool.totalAmount - pool.remainingAmount) / pool.totalAmount
        };
    }
    
    /**
     * 清除
     */
    clear() {
        this.rewardPools.clear();
        this.userRewards.clear();
    }
}

/**
 * 税收系统
 */
class TaxSystem extends EventEmitter {
    constructor() {
        super();
        this.taxRates = {
            transaction: 0.02, // 交易税 2%
            listing: 0.01, // 上架税 1%
            auction: 0.03, // 拍卖税 3%
            withdrawal: 0.005 // 提现税 0.5%
        };
        
        this.collected = {
            transaction: 0,
            listing: 0,
            auction: 0,
            withdrawal: 0,
            total: 0
        };
        
        this.taxHistory = [];
    }
    
    /**
     * 设置税率
     */
    setTaxRate(type, rate) {
        if (this.taxRates.hasOwnProperty(type)) {
            this.taxRates[type] = rate;
            this.emit('tax_rate_updated', { type, rate });
        }
    }
    
    /**
     * 计算税费
     */
    calculateTax(type, amount) {
        const rate = this.taxRates[type] || 0;
        return amount * rate;
    }
    
    /**
     * 收取税费
     */
    collectTax(type, amount, payerId) {
        const tax = this.calculateTax(type, amount);
        
        if (tax <= 0) {
            return { success: false, error: '无效税费' };
        }
        
        // 更新统计
        this.collected[type] += tax;
        this.collected.total += tax;
        
        // 记录历史
        this.taxHistory.push({
            type,
            amount,
            tax,
            payerId,
            timestamp: Date.now()
        });
        
        // 限制历史记录
        if (this.taxHistory.length > 1000) {
            this.taxHistory.shift();
        }
        
        this.emit('tax_collected', {
            type,
            amount,
            tax,
            payerId
        });
        
        return { success: true, tax };
    }
    
    /**
     * 获取税收统计
     */
    getStats() {
        return {
            rates: this.taxRates,
            collected: this.collected,
            totalCollected: this.collected.total,
            recentTransactions: this.taxHistory.slice(-10)
        };
    }
    
    /**
     * 清除
     */
    clear() {
        this.taxHistory = [];
        this.collected = {
            transaction: 0,
            listing: 0,
            auction: 0,
            withdrawal: 0,
            total: 0
        };
    }
}

/**
 * 经济监控器
 */
class EconomyMonitor extends EventEmitter {
    constructor() {
        super();
        this.metrics = new Map();
        this.alerts = [];
        this.thresholds = {
            inflationRate: 0.1, // 10% 通胀率告警
            transactionVolume: 1000000, // 日交易额告警
            activeTraders: 1000 // 活跃交易者告警
        };
    }
    
    /**
     * 记录指标
     */
    recordMetric(name, value) {
        if (!this.metrics.has(name)) {
            this.metrics.set(name, []);
        }
        
        const data = {
            value,
            timestamp: Date.now()
        };
        
        this.metrics.get(name).push(data);
        
        // 限制历史记录
        while (this.metrics.get(name).length > 1000) {
            this.metrics.get(name).shift();
        }
        
        // 检查告警
        this.checkAlerts(name, value);
        
        this.emit('metric_recorded', { name, value });
    }
    
    /**
     * 检查告警
     */
    checkAlerts(name, value) {
        const threshold = this.thresholds[name];
        if (threshold && value > threshold) {
            const alert = {
                name,
                value,
                threshold,
                timestamp: Date.now(),
                level: 'warning'
            };
            
            this.alerts.push(alert);
            
            // 限制告警数量
            if (this.alerts.length > 100) {
                this.alerts.shift();
            }
            
            this.emit('alert_triggered', alert);
        }
    }
    
    /**
     * 获取指标趋势
     */
    getMetricTrend(name, period = 24 * 60 * 60 * 1000) {
        const data = this.metrics.get(name) || [];
        const cutoff = Date.now() - period;
        
        const recent = data.filter(d => d.timestamp > cutoff);
        
        if (recent.length < 2) {
            return { trend: 'stable', change: 0 };
        }
        
        const first = recent[0].value;
        const last = recent[recent.length - 1].value;
        const change = (last - first) / first;
        
        let trend = 'stable';
        if (change > 0.1) trend = 'increasing';
        if (change < -0.1) trend = 'decreasing';
        
        return { trend, change, first, last };
    }
    
    /**
     * 获取告警
     */
    getAlerts(limit = 20) {
        return this.alerts.slice(-limit);
    }
    
    /**
     * 获取经济健康度
     */
    getEconomyHealth() {
        const inflationData = this.getMetricTrend('inflationRate');
        const volumeData = this.getMetricTrend('transactionVolume');
        
        let health = 100;
        
        // 通胀率过高扣分
        if (inflationData.trend === 'increasing' && inflationData.change > 0.2) {
            health -= 20;
        }
        
        // 交易量异常扣分
        if (volumeData.trend === 'decreasing' && volumeData.change < -0.3) {
            health -= 15;
        }
        
        // 告警扣分
        const recentAlerts = this.alerts.filter(
            a => Date.now() - a.timestamp < 24 * 60 * 60 * 1000
        ).length;
        health -= recentAlerts * 5;
        
        return {
            score: Math.max(0, health),
            inflationTrend: inflationData.trend,
            volumeTrend: volumeData.trend,
            recentAlerts
        };
    }
    
    /**
     * 清除
     */
    clear() {
        this.metrics.clear();
        this.alerts = [];
    }
}

module.exports = {
    InflationControl,
    RewardSystem,
    TaxSystem,
    EconomyMonitor
};

console.log('经济平衡系统已加载');
