/**
 * 活动系统
 * 
 * 节日活动、限时活动、竞赛活动
 */

const { EventEmitter } = require('events');

/**
 * 活动管理器
 */
class EventManager extends EventEmitter {
    constructor() {
        super();
        this.events = new Map(); // eventId -> event
        this.participations = new Map(); // eventId -> [userIds]
        this.rewards = new Map(); // rewardId -> reward
        this.nextEventId = 1;
        this.nextRewardId = 1;
    }
    
    /**
     * 创建活动
     */
    createEvent(name, description, type, startTime, endTime, config = {}) {
        const eventId = `event_${this.nextEventId++}`;
        
        const event = {
            id: eventId,
            name,
            description,
            type, // festival, limited, competition, daily
            startTime,
            endTime,
            status: 'upcoming', // upcoming, active, ended
            config,
            participants: 0,
            totalRewards: 0,
            createdAt: Date.now()
        };
        
        this.events.set(eventId, event);
        
        this.emit('event_created', event);
        
        return event;
    }
    
    /**
     * 参与活动
     */
    participateEvent(eventId, userId, data = {}) {
        const event = this.events.get(eventId);
        if (!event) {
            return { success: false, error: '活动不存在' };
        }
        
        if (event.status !== 'active') {
            return { success: false, error: '活动未开始或已结束' };
        }
        
        // 检查是否已参与
        if (!this.participations.has(eventId)) {
            this.participations.set(eventId, new Set());
        }
        
        if (this.participations.get(eventId).has(userId)) {
            return { success: false, error: '已参与过活动' };
        }
        
        this.participations.get(eventId).add(userId);
        event.participants++;
        
        this.emit('event_participated', { eventId, userId, data });
        
        return { success: true };
    }
    
    /**
     * 完成任务
     */
    completeEventTask(eventId, userId, taskId, data = {}) {
        const event = this.events.get(eventId);
        if (!event) {
            return { success: false, error: '活动不存在' };
        }
        
        // 检查是否已参与
        if (!this.participations.has(eventId) || 
            !this.participations.get(eventId).has(userId)) {
            return { success: false, error: '未参与活动' };
        }
        
        // 发放奖励
        const reward = event.config.taskReward || 100;
        this.grantReward(userId, reward, `event_${eventId}_${taskId}`);
        
        this.emit('task_completed', { eventId, userId, taskId, reward });
        
        return { success: true, reward };
    }
    
    /**
     * 发放奖励
     */
    grantReward(userId, amount, source) {
        const rewardId = `reward_${this.nextRewardId++}`;
        
        const reward = {
            id: rewardId,
            userId,
            amount,
            source,
            claimed: false,
            createdAt: Date.now()
        };
        
        this.rewards.set(rewardId, reward);
        
        // 更新活动统计
        const event = this.getEventBySource(source);
        if (event) {
            event.totalRewards += amount;
        }
        
        this.emit('reward_granted', reward);
        
        return reward;
    }
    
    /**
     * 领取奖励
     */
    claimReward(rewardId, userId) {
        const reward = this.rewards.get(rewardId);
        if (!reward || reward.userId !== userId) {
            return { success: false, error: '奖励无效' };
        }
        
        if (reward.claimed) {
            return { success: false, error: '奖励已领取' };
        }
        
        reward.claimed = true;
        reward.claimedAt = Date.now();
        
        this.emit('reward_claimed', reward);
        
        return { success: true, reward };
    }
    
    /**
     * 更新活动状态
     */
    updateEventStatus(eventId) {
        const event = this.events.get(eventId);
        if (!event) return;
        
        const now = Date.now();
        
        if (now < event.startTime) {
            event.status = 'upcoming';
        } else if (now >= event.startTime && now < event.endTime) {
            event.status = 'active';
            this.emit('event_started', event);
        } else {
            event.status = 'ended';
            this.emit('event_ended', event);
        }
    }
    
    /**
     * 获取活动列表
     */
    getEvents(filters = {}) {
        let events = Array.from(this.events.values());
        
        if (filters.status) {
            events = events.filter(e => e.status === filters.status);
        }
        
        if (filters.type) {
            events = events.filter(e => e.type === filters.type);
        }
        
        // 排序
        events.sort((a, b) => b.startTime - a.startTime);
        
        // 分页
        const page = filters.page || 1;
        const limit = filters.limit || 20;
        const start = (page - 1) * limit;
        
        return {
            events: events.slice(start, start + limit),
            total: events.length,
            page,
            limit,
            totalPages: Math.ceil(events.length / limit)
        };
    }
    
    /**
     * 获取活动详情
     */
    getEvent(eventId) {
        const event = this.events.get(eventId);
        if (event) {
            const participants = this.participations.get(eventId);
            return {
                ...event,
                participantCount: participants ? participants.size : 0
            };
        }
        return null;
    }
    
    /**
     * 根据来源获取活动
     */
    getEventBySource(source) {
        const match = source.match(/event_(event_\d+)/);
        if (match) {
            return this.events.get(match[1]);
        }
        return null;
    }
    
    /**
     * 获取用户参与的活动
     */
    getUserEvents(userId) {
        const userEvents = [];
        
        for (const [eventId, participants] of this.participations) {
            if (participants.has(userId)) {
                const event = this.events.get(eventId);
                if (event) {
                    userEvents.push(event);
                }
            }
        }
        
        return userEvents;
    }
    
    /**
     * 清除
     */
    clear() {
        this.events.clear();
        this.participations.clear();
        this.rewards.clear();
    }
}

/**
 * 版本管理系统
 */
class VersionManager extends EventEmitter {
    constructor() {
        super();
        this.versions = new Map(); // version -> versionInfo
        this.currentVersion = '1.0.0';
        this.updateLogs = [];
    }
    
    /**
     * 添加版本
     */
    addVersion(version, name, description, changes, releaseDate) {
        const versionInfo = {
            version,
            name,
            description,
            changes, // [{type, description}]
            releaseDate,
            isCurrent: false
        };
        
        this.versions.set(version, versionInfo);
        
        this.emit('version_added', versionInfo);
        
        return versionInfo;
    }
    
    /**
     * 设置当前版本
     */
    setCurrentVersion(version) {
        if (!this.versions.has(version)) {
            return { success: false, error: '版本不存在' };
        }
        
        // 更新所有版本状态
        for (const v of this.versions.values()) {
            v.isCurrent = false;
        }
        
        const versionInfo = this.versions.get(version);
        versionInfo.isCurrent = true;
        this.currentVersion = version;
        
        this.emit('version_updated', versionInfo);
        
        return { success: true, version: versionInfo };
    }
    
    /**
     * 添加更新日志
     */
    addUpdateLog(type, description, version) {
        const log = {
            id: `log_${Date.now()}`,
            type, // feature, fix, improvement, security
            description,
            version,
            createdAt: Date.now()
        };
        
        this.updateLogs.push(log);
        
        // 限制日志数量
        if (this.updateLogs.length > 100) {
            this.updateLogs.shift();
        }
        
        this.emit('update_log_added', log);
        
        return log;
    }
    
    /**
     * 获取版本历史
     */
    getVersionHistory(limit = 10) {
        const versions = Array.from(this.versions.values());
        versions.sort((a, b) => new Date(b.releaseDate) - new Date(a.releaseDate));
        return versions.slice(0, limit);
    }
    
    /**
     * 获取更新日志
     */
    getUpdateLogs(filters = {}, limit = 50) {
        let logs = this.updateLogs;
        
        if (filters.type) {
            logs = logs.filter(l => l.type === filters.type);
        }
        
        if (filters.version) {
            logs = logs.filter(l => l.version === filters.version);
        }
        
        return logs.slice(-limit);
    }
    
    /**
     * 获取当前版本
     */
    getCurrentVersion() {
        return this.versions.get(this.currentVersion);
    }
    
    /**
     * 清除
     */
    clear() {
        this.versions.clear();
        this.updateLogs = [];
    }
}

/**
 * 安全加固系统
 */
class SecuritySystem extends EventEmitter {
    constructor() {
        super();
        this.auditLogs = [];
        this.securityLevels = new Map(); // userId -> level
        this.bannedUsers = new Set();
        this.config = {
            maxLoginAttempts: 5,
            banDuration: 24 * 60 * 60 * 1000, // 24 小时
            suspiciousActivityThreshold: 100
        };
    }
    
    /**
     * 记录审计日志
     */
    logAudit(userId, action, details, riskLevel = 'low') {
        const log = {
            id: `audit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            userId,
            action,
            details,
            riskLevel, // low, medium, high, critical
            timestamp: Date.now(),
            ip: details.ip || null,
            userAgent: details.userAgent || null
        };
        
        this.auditLogs.push(log);
        
        // 限制日志数量
        if (this.auditLogs.length > 10000) {
            this.auditLogs.shift();
        }
        
        // 检查可疑活动
        this.checkSuspiciousActivity(userId);
        
        this.emit('audit_logged', log);
        
        return log;
    }
    
    /**
     * 检查可疑活动
     */
    checkSuspiciousActivity(userId) {
        const recentLogs = this.auditLogs.filter(
            log => log.userId === userId && 
                   Date.now() - log.timestamp < 60 * 60 * 1000 // 1 小时内
        );
        
        if (recentLogs.length > this.config.suspiciousActivityThreshold) {
            this.logAudit(userId, 'suspicious_activity', {
                count: recentLogs.length,
                threshold: this.config.suspiciousActivityThreshold
            }, 'high');
            
            this.emit('suspicious_activity', { userId, count: recentLogs.length });
        }
    }
    
    /**
     * 封禁用户
     */
    banUser(userId, reason, duration = null) {
        const banInfo = {
            userId,
            reason,
            duration: duration || this.config.banDuration,
            bannedAt: Date.now(),
            expiresAt: Date.now() + (duration || this.config.banDuration)
        };
        
        this.bannedUsers.add(userId);
        this.securityLevels.set(userId, 'banned');
        
        this.emit('user_banned', banInfo);
        
        return banInfo;
    }
    
    /**
     * 解封用户
     */
    unbanUser(userId) {
        this.bannedUsers.delete(userId);
        this.securityLevels.delete(userId);
        
        this.emit('user_unbanned', { userId });
        
        return { success: true };
    }
    
    /**
     * 检查用户是否被封禁
     */
    isBanned(userId) {
        if (!this.bannedUsers.has(userId)) return false;
        
        const banInfo = this.getBanInfo(userId);
        if (banInfo && Date.now() > banInfo.expiresAt) {
            this.unbanUser(userId);
            return false;
        }
        
        return this.bannedUsers.has(userId);
    }
    
    /**
     * 获取封禁信息
     */
    getBanInfo(userId) {
        // 简化实现
        return null;
    }
    
    /**
     * 获取审计日志
     */
    getAuditLogs(filters = {}, limit = 100) {
        let logs = this.auditLogs;
        
        if (filters.userId) {
            logs = logs.filter(l => l.userId === filters.userId);
        }
        
        if (filters.riskLevel) {
            logs = logs.filter(l => l.riskLevel === filters.riskLevel);
        }
        
        if (filters.action) {
            logs = logs.filter(l => l.action === filters.action);
        }
        
        return logs.slice(-limit);
    }
    
    /**
     * 获取安全统计
     */
    getSecurityStats() {
        const now = Date.now();
        const last24Hours = now - 24 * 60 * 60 * 1000;
        
        const recentLogs = this.auditLogs.filter(log => log.timestamp > last24Hours);
        
        return {
            totalLogs: this.auditLogs.length,
            recentLogs: recentLogs.length,
            bannedUsers: this.bannedUsers.size,
            highRiskLogs: recentLogs.filter(l => l.riskLevel === 'high' || l.riskLevel === 'critical').length,
            suspiciousActivities: recentLogs.filter(l => l.action === 'suspicious_activity').length
        };
    }
    
    /**
     * 清除
     */
    clear() {
        this.auditLogs = [];
        this.securityLevels.clear();
        this.bannedUsers.clear();
    }
}

module.exports = {
    EventManager,
    VersionManager,
    SecuritySystem
};

console.log('持续运营系统已加载');
