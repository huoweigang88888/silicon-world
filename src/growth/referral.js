/**
 * 用户增长系统
 * 
 * 邀请奖励、新手引导、每日任务、签到、等级
 */

const { EventEmitter } = require('events');

/**
 * 邀请系统
 */
class ReferralSystem extends EventEmitter {
    constructor() {
        super();
        this.invitations = new Map(); // invitationCode -> invitation
        this.userInvites = new Map(); // userId -> [invitationCodes]
        this.rewards = new Map(); // rewardId -> reward
        this.config = {
            inviterReward: 100, // 邀请人奖励
            inviteeReward: 50, // 被邀请人奖励
            maxInvites: 100 // 最大邀请数
        };
        this.nextInvitationId = 1;
        this.nextRewardId = 1;
    }
    
    /**
     * 生成邀请码
     */
    generateInvitationCode(userId) {
        const code = `INV_${userId}_${Math.random().toString(36).substr(2, 6).toUpperCase()}`;
        
        const invitation = {
            code,
            inviterId: userId,
            createdAt: Date.now(),
            usedAt: null,
            usedBy: null,
            status: 'active'
        };
        
        this.invitations.set(code, invitation);
        
        if (!this.userInvites.has(userId)) {
            this.userInvites.set(userId, []);
        }
        this.userInvites.get(userId).push(code);
        
        this.emit('invitation_created', invitation);
        
        return invitation;
    }
    
    /**
     * 使用邀请码
     */
    useInvitation(code, inviteeId) {
        const invitation = this.invitations.get(code);
        if (!invitation) {
            return { success: false, error: '邀请码无效' };
        }
        
        if (invitation.status !== 'active') {
            return { success: false, error: '邀请码已使用' };
        }
        
        if (invitation.inviterId === inviteeId) {
            return { success: false, error: '不能邀请自己' };
        }
        
        invitation.usedAt = Date.now();
        invitation.usedBy = inviteeId;
        invitation.status = 'used';
        
        // 发放奖励
        this.grantReward(invitation.inviterId, this.config.inviterReward, 'inviter');
        this.grantReward(inviteeId, this.config.inviteeReward, 'invitee');
        
        this.emit('invitation_used', invitation);
        
        return { success: true, invitation };
    }
    
    /**
     * 发放奖励
     */
    grantReward(userId, amount, type) {
        const rewardId = `reward_${this.nextRewardId++}`;
        
        const reward = {
            id: rewardId,
            userId,
            amount,
            type, // inviter, invitee, daily_task, checkin, etc.
            claimed: false,
            createdAt: Date.now()
        };
        
        this.rewards.set(rewardId, reward);
        
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
     * 获取用户邀请统计
     */
    getUserInviteStats(userId) {
        const codes = this.userInvites.get(userId) || [];
        const invitations = codes.map(code => this.invitations.get(code)).filter(Boolean);
        
        const used = invitations.filter(i => i.status === 'used').length;
        const active = invitations.filter(i => i.status === 'active').length;
        
        const totalRewards = this.rewards.values()
            .filter(r => r.userId === userId && r.type === 'inviter')
            .reduce((sum, r) => sum + r.amount, 0);
        
        return {
            totalInvites: invitations.length,
            usedInvites: used,
            activeInvites: active,
            totalRewards,
            maxInvites: this.config.maxInvites
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
        this.invitations.clear();
        this.userInvites.clear();
        this.rewards.clear();
    }
}

/**
 * 新手引导系统
 */
class OnboardingSystem extends EventEmitter {
    constructor() {
        super();
        this.tasks = new Map(); // taskId -> task
        this.userProgress = new Map(); // userId -> { completedTasks: [], currentStep }
        
        this.defaultTasks = [
            { id: 'complete_profile', name: '完善个人资料', reward: 50 },
            { id: 'follow_5_users', name: '关注 5 个用户', reward: 100 },
            { id: 'post_first_activity', name: '发布第一条动态', reward: 100 },
            { id: 'join_forum', name: '加入论坛讨论', reward: 50 },
            { id: 'first_trade', name: '完成第一次交易', reward: 200 }
        ];
        
        this.init();
    }
    
    init() {
        for (const task of this.defaultTasks) {
            this.tasks.set(task.id, task);
        }
    }
    
    /**
     * 获取用户进度
     */
    getUserProgress(userId) {
        if (!this.userProgress.has(userId)) {
            this.userProgress.set(userId, {
                completedTasks: [],
                currentStep: 0,
                joinedAt: Date.now()
            });
        }
        return this.userProgress.get(userId);
    }
    
    /**
     * 完成任务
     */
    completeTask(userId, taskId) {
        const progress = this.getUserProgress(userId);
        
        if (progress.completedTasks.includes(taskId)) {
            return { success: false, error: '任务已完成' };
        }
        
        const task = this.tasks.get(taskId);
        if (!task) {
            return { success: false, error: '任务不存在' };
        }
        
        progress.completedTasks.push(taskId);
        progress.currentStep++;
        
        // 发放奖励
        const reward = {
            taskId,
            reward: task.reward,
            completedAt: Date.now()
        };
        
        this.emit('task_completed', { userId, task, reward });
        
        return { success: true, reward };
    }
    
    /**
     * 检查任务完成
     */
    checkTaskCompletion(userId, action, data = {}) {
        const progress = this.getUserProgress(userId);
        
        const taskMap = {
            'profile_updated': 'complete_profile',
            'user_followed': 'follow_5_users',
            'activity_posted': 'post_first_activity',
            'forum_joined': 'join_forum',
            'trade_completed': 'first_trade'
        };
        
        const taskId = taskMap[action];
        if (!taskId) return;
        
        // 特殊处理需要计数的任务
        if (taskId === 'follow_5_users') {
            const followCount = data.count || 0;
            if (followCount >= 5 && !progress.completedTasks.includes(taskId)) {
                this.completeTask(userId, taskId);
            }
        } else if (!progress.completedTasks.includes(taskId)) {
            this.completeTask(userId, taskId);
        }
    }
    
    /**
     * 获取新手状态
     */
    getOnboardingStatus(userId) {
        const progress = this.getUserProgress(userId);
        const totalTasks = this.tasks.size;
        const completedCount = progress.completedTasks.length;
        
        return {
            currentStep: progress.currentStep,
            totalSteps: totalTasks,
            completedTasks: progress.completedTasks,
            completionRate: completedCount / totalTasks,
            isCompleted: completedCount === totalTasks
        };
    }
    
    /**
     * 清除
     */
    clear() {
        this.userProgress.clear();
    }
}

/**
 * 每日任务系统
 */
class DailyTaskSystem extends EventEmitter {
    constructor() {
        super();
        this.tasks = new Map();
        this.userProgress = new Map();
        this.config = {
            resetHour: 0 // 每日重置时间 (0-23)
        };
        
        this.defaultTasks = [
            { id: 'daily_login', name: '每日登录', reward: 20, type: 'daily' },
            { id: 'daily_post', name: '发布动态', reward: 30, type: 'daily', limit: 1 },
            { id: 'daily_like', name: '点赞 10 次', reward: 20, type: 'daily', target: 10 },
            { id: 'daily_comment', name: '评论 5 次', reward: 30, type: 'daily', target: 5 }
        ];
        
        this.init();
    }
    
    init() {
        for (const task of this.defaultTasks) {
            this.tasks.set(task.id, task);
        }
    }
    
    /**
     * 获取用户今日任务
     */
    getUserTasks(userId) {
        const today = this.getTodayKey();
        
        if (!this.userProgress.has(userId)) {
            this.userProgress.set(userId, {});
        }
        
        const userProgress = this.userProgress.get(userId);
        
        if (!userProgress[today]) {
            userProgress[today] = {
                date: today,
                tasks: {}
            };
        }
        
        const progress = userProgress[today];
        
        return Array.from(this.tasks.values()).map(task => ({
            ...task,
            current: progress.tasks[task.id] || 0,
            completed: progress.tasks[task.id] >= (task.target || 1)
        }));
    }
    
    /**
     * 更新任务进度
     */
    updateTaskProgress(userId, action, count = 1) {
        const today = this.getTodayKey();
        const userProgress = this.userProgress.get(userId);
        
        if (!userProgress || !userProgress[today]) return;
        
        const taskMap = {
            'activity_posted': 'daily_post',
            'activity_liked': 'daily_like',
            'activity_commented': 'daily_comment'
        };
        
        const taskId = taskMap[action];
        if (!taskId) return;
        
        const task = this.tasks.get(taskId);
        if (!task) return;
        
        if (!userProgress[today].tasks[taskId]) {
            userProgress[today].tasks[taskId] = 0;
        }
        
        userProgress[today].tasks[taskId] += count;
        
        // 检查是否完成
        const current = userProgress[today].tasks[taskId];
        const target = task.target || 1;
        
        if (current >= target && current - count < target) {
            this.emit('task_completed', { userId, taskId, reward: task.reward });
        }
    }
    
    /**
     * 领取任务奖励
     */
    claimTaskReward(userId, taskId) {
        const today = this.getTodayKey();
        const userProgress = this.userProgress.get(userId);
        
        if (!userProgress || !userProgress[today]) {
            return { success: false, error: '无任务数据' };
        }
        
        const task = this.tasks.get(taskId);
        if (!task) {
            return { success: false, error: '任务不存在' };
        }
        
        const current = userProgress[today].tasks[taskId] || 0;
        const target = task.target || 1;
        
        if (current < target) {
            return { success: false, error: '任务未完成' };
        }
        
        if (userProgress[today].claimed && userProgress[today].claimed.includes(taskId)) {
            return { success: false, error: '奖励已领取' };
        }
        
        if (!userProgress[today].claimed) {
            userProgress[today].claimed = [];
        }
        userProgress[today].claimed.push(taskId);
        
        this.emit('reward_claimed', { userId, taskId, reward: task.reward });
        
        return { success: true, reward: task.reward };
    }
    
    /**
     * 获取今日日期键
     */
    getTodayKey() {
        const now = new Date();
        return `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()}`;
    }
    
    /**
     * 清除
     */
    clear() {
        this.userProgress.clear();
    }
}

/**
 * 签到系统
 */
class CheckInSystem extends EventEmitter {
    constructor() {
        super();
        this.userCheckIns = new Map();
        this.config = {
            baseReward: 10,
            streakBonus: {
                3: 20,
                7: 50,
                14: 100,
                30: 300
            }
        };
    }
    
    /**
     * 签到
     */
    checkIn(userId) {
        const today = this.getTodayKey();
        
        if (!this.userCheckIns.has(userId)) {
            this.userCheckIns.set(userId, {
                history: [],
                streak: 0,
                lastCheckIn: null
            });
        }
        
        const userCheckIn = this.userCheckIns.get(userId);
        
        // 检查是否已签到
        if (userCheckIn.history.includes(today)) {
            return { success: false, error: '今日已签到' };
        }
        
        // 计算连续签到
        const yesterday = this.getYesterdayKey();
        if (userCheckIn.lastCheckIn === yesterday) {
            userCheckIn.streak++;
        } else {
            userCheckIn.streak = 1;
        }
        
        userCheckIn.history.push(today);
        userCheckIn.lastCheckIn = today;
        
        // 限制历史记录
        if (userCheckIn.history.length > 90) {
            userCheckIn.history.shift();
        }
        
        // 计算奖励
        const baseReward = this.config.baseReward;
        const streakBonus = this.config.streakBonus[userCheckIn.streak] || 0;
        const totalReward = baseReward + streakBonus;
        
        this.emit('checkin_completed', {
            userId,
            streak: userCheckIn.streak,
            reward: totalReward,
            baseReward,
            streakBonus
        });
        
        return {
            success: true,
            streak: userCheckIn.streak,
            reward: totalReward
        };
    }
    
    /**
     * 获取签到状态
     */
    getCheckInStatus(userId) {
        const userCheckIn = this.userCheckIns.get(userId);
        
        if (!userCheckIn) {
            return {
                streak: 0,
                lastCheckIn: null,
                checkedInToday: false,
                history: []
            };
        }
        
        const today = this.getTodayKey();
        
        return {
            streak: userCheckIn.streak,
            lastCheckIn: userCheckIn.lastCheckIn,
            checkedInToday: userCheckIn.history.includes(today),
            history: userCheckIn.history.slice(-30)
        };
    }
    
    /**
     * 获取今日日期键
     */
    getTodayKey() {
        const now = new Date();
        return `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()}`;
    }
    
    /**
     * 获取昨日日期键
     */
    getYesterdayKey() {
        const yesterday = new Date();
        yesterday.setDate(yesterday.getDate() - 1);
        return `${yesterday.getFullYear()}-${yesterday.getMonth() + 1}-${yesterday.getDate()}`;
    }
    
    /**
     * 清除
     */
    clear() {
        this.userCheckIns.clear();
    }
}

module.exports = {
    ReferralSystem,
    OnboardingSystem,
    DailyTaskSystem,
    CheckInSystem
};

console.log('用户增长系统已加载');
