/**
 * 社交网络系统
 * 
 * 动态、关注、点赞评论、分享
 */

const { EventEmitter } = require('events');

/**
 * 动态系统
 */
class ActivityFeed extends EventEmitter {
    constructor() {
        super();
        this.activities = new Map(); // activityId -> activity
        this.userActivities = new Map(); // userId -> [activityIds]
        this.userFeeds = new Map(); // userId -> [activityIds]
        this.nextActivityId = 1;
    }
    
    /**
     * 发布动态
     */
    postActivity(userId, content, type = 'text', data = {}) {
        const activityId = `activity_${this.nextActivityId++}`;
        
        const activity = {
            id: activityId,
            userId,
            content,
            type, // text, image, video, link, share
            data,
            likeCount: 0,
            commentCount: 0,
            shareCount: 0,
            viewCount: 0,
            createdAt: Date.now(),
            visibility: 'public' // public, friends, private
        };
        
        this.activities.set(activityId, activity);
        
        if (!this.userActivities.has(userId)) {
            this.userActivities.set(userId, []);
        }
        this.userActivities.get(userId).push(activityId);
        
        // 推送给粉丝
        this.pushToFollowers(userId, activityId);
        
        this.emit('activity_posted', activity);
        
        return activity;
    }
    
    /**
     * 推送到粉丝动态
     */
    pushToFollowers(userId, activityId) {
        // 获取用户的粉丝
        const followers = this.getFollowers(userId);
        
        for (const followerId of followers) {
            if (!this.userFeeds.has(followerId)) {
                this.userFeeds.set(followerId, []);
            }
            this.userFeeds.get(followerId).push(activityId);
        }
    }
    
    /**
     * 获取用户动态
     */
    getUserActivities(userId, limit = 20) {
        const activityIds = this.userActivities.get(userId) || [];
        const activities = activityIds.map(id => this.activities.get(id)).filter(Boolean);
        
        activities.sort((a, b) => b.createdAt - a.createdAt);
        
        return activities.slice(0, limit);
    }
    
    /**
     * 获取个人动态流
     */
    getUserFeed(userId, limit = 50) {
        const activityIds = this.userFeeds.get(userId) || [];
        const activities = activityIds.map(id => this.activities.get(id)).filter(Boolean);
        
        activities.sort((a, b) => b.createdAt - a.createdAt);
        
        return activities.slice(0, limit);
    }
    
    /**
     * 点赞动态
     */
    likeActivity(activityId, userId) {
        const activity = this.activities.get(activityId);
        if (!activity) {
            return { success: false, error: '动态不存在' };
        }
        
        if (!activity.likedBy) {
            activity.likedBy = new Set();
        }
        
        if (activity.likedBy.has(userId)) {
            activity.likedBy.delete(userId);
            activity.likeCount--;
            this.emit('activity_unliked', { activityId, userId });
        } else {
            activity.likedBy.add(userId);
            activity.likeCount++;
            this.emit('activity_liked', { activityId, userId });
        }
        
        return { success: true, likeCount: activity.likeCount };
    }
    
    /**
     * 评论动态
     */
    commentActivity(activityId, userId, content) {
        const activity = this.activities.get(activityId);
        if (!activity) {
            return { success: false, error: '动态不存在' };
        }
        
        const commentId = `comment_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        const comment = {
            id: commentId,
            activityId,
            userId,
            content,
            createdAt: Date.now(),
            likeCount: 0
        };
        
        if (!activity.comments) {
            activity.comments = [];
        }
        activity.comments.push(comment);
        activity.commentCount++;
        
        this.emit('activity_commented', { activityId, comment });
        
        return { success: true, comment };
    }
    
    /**
     * 分享动态
     */
    shareActivity(activityId, userId, comment = '') {
        const activity = this.activities.get(activityId);
        if (!activity) {
            return { success: false, error: '动态不存在' };
        }
        
        // 创建分享动态
        const shareActivity = this.postActivity(userId, comment, 'share', {
            originalActivityId: activityId,
            originalUserId: activity.userId
        });
        
        activity.shareCount++;
        
        this.emit('activity_shared', { activityId, shareActivity });
        
        return { success: true, shareActivity };
    }
    
    /**
     * 浏览动态
     */
    viewActivity(activityId) {
        const activity = this.activities.get(activityId);
        if (activity) {
            activity.viewCount++;
        }
        return activity;
    }
    
    /**
     * 删除动态
     */
    deleteActivity(activityId, userId) {
        const activity = this.activities.get(activityId);
        if (!activity || activity.userId !== userId) {
            return { success: false, error: '无权操作' };
        }
        
        this.activities.delete(activityId);
        
        // 从用户动态列表移除
        const userActivities = this.userActivities.get(activity.userId);
        if (userActivities) {
            const index = userActivities.indexOf(activityId);
            if (index > -1) userActivities.splice(index, 1);
        }
        
        this.emit('activity_deleted', { activityId });
        
        return { success: true };
    }
    
    /**
     * 获取粉丝
     */
    getFollowers(userId) {
        // 简化实现，实际应该从关注系统获取
        return [];
    }
    
    /**
     * 获取统计
     */
    getStats(userId) {
        const activities = this.getUserActivities(userId, 1000);
        return {
            totalActivities: activities.length,
            totalLikes: activities.reduce((sum, a) => sum + a.likeCount, 0),
            totalComments: activities.reduce((sum, a) => sum + a.commentCount, 0),
            totalShares: activities.reduce((sum, a) => sum + a.shareCount, 0),
            totalViews: activities.reduce((sum, a) => sum + a.viewCount, 0)
        };
    }
    
    /**
     * 清除
     */
    clear() {
        this.activities.clear();
        this.userActivities.clear();
        this.userFeeds.clear();
    }
}

/**
 * 关注系统
 */
class FollowSystem extends EventEmitter {
    constructor() {
        super();
        this.following = new Map(); // userId -> [followingIds]
        this.followers = new Map(); // userId -> [followerIds]
    }
    
    /**
     * 关注用户
     */
    follow(userId, targetId) {
        if (userId === targetId) {
            return { success: false, error: '不能关注自己' };
        }
        
        // 添加到关注列表
        if (!this.following.has(userId)) {
            this.following.set(userId, new Set());
        }
        this.following.get(userId).add(targetId);
        
        // 添加到粉丝列表
        if (!this.followers.has(targetId)) {
            this.followers.set(targetId, new Set());
        }
        this.followers.get(targetId).add(userId);
        
        this.emit('user_followed', { userId, targetId });
        
        return { success: true };
    }
    
    /**
     * 取消关注
     */
    unfollow(userId, targetId) {
        // 从关注列表移除
        if (this.following.has(userId)) {
            this.following.get(userId).delete(targetId);
        }
        
        // 从粉丝列表移除
        if (this.followers.has(targetId)) {
            this.followers.get(targetId).delete(userId);
        }
        
        this.emit('user_unfollowed', { userId, targetId });
        
        return { success: true };
    }
    
    /**
     * 检查是否关注
     */
    isFollowing(userId, targetId) {
        const following = this.following.get(userId);
        return following ? following.has(targetId) : false;
    }
    
    /**
     * 获取关注列表
     */
    getFollowing(userId) {
        const following = this.following.get(userId);
        return following ? Array.from(following) : [];
    }
    
    /**
     * 获取粉丝列表
     */
    getFollowers(userId) {
        const followers = this.followers.get(userId);
        return followers ? Array.from(followers) : [];
    }
    
    /**
     * 获取关注数
     */
    getFollowingCount(userId) {
        const following = this.following.get(userId);
        return following ? following.size : 0;
    }
    
    /**
     * 获取粉丝数
     */
    getFollowerCount(userId) {
        const followers = this.followers.get(userId);
        return followers ? followers.size : 0;
    }
    
    /**
     * 获取互相关注
     */
    getMutualFollowing(userId1, userId2) {
        const following1 = this.following.get(userId1);
        const following2 = this.following.get(userId2);
        
        if (!following1 || !following2) {
            return [];
        }
        
        return Array.from(following1).filter(id => following2.has(id));
    }
    
    /**
     * 推荐关注
     */
    suggestFollowing(userId, limit = 10) {
        // 获取用户的好友的好友
        const following = this.getFollowing(userId);
        const suggestions = new Map();
        
        for (const followId of following) {
            const theirFollowing = this.getFollowing(followId);
            for (const suggestionId of theirFollowing) {
                if (suggestionId !== userId && !this.isFollowing(userId, suggestionId)) {
                    suggestions.set(suggestionId, (suggestions.get(suggestionId) || 0) + 1);
                }
            }
        }
        
        // 按共同好友数排序
        const sorted = Array.from(suggestions.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, limit)
            .map(([id]) => id);
        
        return sorted;
    }
    
    /**
     * 清除
     */
    clear() {
        this.following.clear();
        this.followers.clear();
    }
}

/**
 * 分享系统
 */
class ShareSystem extends EventEmitter {
    constructor() {
        super();
        this.shares = new Map(); // shareId -> share
        this.itemShares = new Map(); // itemId -> [shareIds]
    }
    
    /**
     * 分享内容
     */
    share(userId, itemType, itemId, comment = '', platform = 'internal') {
        const shareId = `share_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        const share = {
            id: shareId,
            userId,
            itemType, // activity, thread, nft, etc.
            itemId,
            comment,
            platform, // internal, twitter, weibo, etc.
            likeCount: 0,
            commentCount: 0,
            createdAt: Date.now()
        };
        
        this.shares.set(shareId, share);
        
        if (!this.itemShares.has(itemId)) {
            this.itemShares.set(itemId, []);
        }
        this.itemShares.get(itemId).push(shareId);
        
        this.emit('content_shared', share);
        
        return share;
    }
    
    /**
     * 获取分享列表
     */
    getItemShares(itemId, limit = 50) {
        const shareIds = this.itemShares.get(itemId) || [];
        const shares = shareIds.map(id => this.shares.get(id)).filter(Boolean);
        
        shares.sort((a, b) => b.createdAt - a.createdAt);
        
        return shares.slice(0, limit);
    }
    
    /**
     * 获取分享统计
     */
    getShareStats(itemId) {
        const shares = this.getItemShares(itemId);
        return {
            totalShares: shares.length,
            byPlatform: shares.reduce((acc, s) => {
                acc[s.platform] = (acc[s.platform] || 0) + 1;
                return acc;
            }, {})
        };
    }
    
    /**
     * 清除
     */
    clear() {
        this.shares.clear();
        this.itemShares.clear();
    }
}

module.exports = {
    ActivityFeed,
    FollowSystem,
    ShareSystem
};

console.log('社交网络系统已加载');
