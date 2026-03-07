/**
 * 社区论坛系统
 * 
 * 帖子、回复、分类、声望
 */

const { EventEmitter } = require('events');

/**
 * 论坛管理器
 */
class ForumManager extends EventEmitter {
    constructor() {
        super();
        this.categories = new Map(); // categoryId -> category
        this.threads = new Map(); // threadId -> thread
        this.posts = new Map(); // postId -> post
        this.userStats = new Map(); // userId -> stats
        
        this.nextCategoryId = 1;
        this.nextThreadId = 1;
        this.nextPostId = 1;
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
            threadCount: 0,
            postCount: 0,
            createdAt: Date.now(),
            order: 0
        };
        
        // 添加到父分类
        if (parentCategoryId) {
            const parent = this.categories.get(parentCategoryId);
            if (parent) {
                parent.subCategories.push(categoryId);
            }
        }
        
        this.categories.set(categoryId, category);
        
        this.emit('category_created', category);
        
        return category;
    }
    
    /**
     * 创建帖子
     */
    createThread(categoryId, authorId, title, content, tags = []) {
        const category = this.categories.get(categoryId);
        if (!category) {
            return { success: false, error: '分类不存在' };
        }
        
        const threadId = `thread_${this.nextThreadId++}`;
        
        const thread = {
            id: threadId,
            categoryId,
            authorId,
            title,
            content,
            tags,
            status: 'active', // active, locked, pinned, hidden
            viewCount: 0,
            replyCount: 0,
            likeCount: 0,
            createdAt: Date.now(),
            updatedAt: Date.now(),
            lastReplyAt: null,
            lastReplyBy: null
        };
        
        this.threads.set(threadId, thread);
        category.threadCount++;
        
        // 更新用户统计
        this.updateUserStats(authorId, { threads: 1 });
        
        this.emit('thread_created', thread);
        
        return { success: true, thread };
    }
    
    /**
     * 回复帖子
     */
    replyToThread(threadId, authorId, content) {
        const thread = this.threads.get(threadId);
        if (!thread) {
            return { success: false, error: '帖子不存在' };
        }
        
        if (thread.status === 'locked') {
            return { success: false, error: '帖子已锁定' };
        }
        
        const postId = `post_${this.nextPostId++}`;
        
        const post = {
            id: postId,
            threadId,
            authorId,
            content,
            likeCount: 0,
            createdAt: Date.now(),
            editedAt: null,
            isOriginal: false
        };
        
        this.posts.set(postId, post);
        
        // 更新帖子统计
        thread.replyCount++;
        thread.lastReplyAt = Date.now();
        thread.lastReplyBy = authorId;
        thread.updatedAt = Date.now();
        
        // 更新分类统计
        const category = this.categories.get(thread.categoryId);
        if (category) {
            category.postCount++;
        }
        
        // 更新用户统计
        this.updateUserStats(authorId, { posts: 1 });
        
        this.emit('post_created', { thread, post });
        
        return { success: true, post };
    }
    
    /**
     * 点赞帖子/回复
     */
    like(itemId, userId, type = 'thread') {
        let item;
        if (type === 'thread') {
            item = this.threads.get(itemId);
        } else {
            item = this.posts.get(itemId);
        }
        
        if (!item) {
            return { success: false, error: '项目不存在' };
        }
        
        if (!item.likedBy) {
            item.likedBy = new Set();
        }
        
        if (item.likedBy.has(userId)) {
            item.likedBy.delete(userId);
            item.likeCount--;
            this.emit('item_unliked', { itemId, userId, type });
        } else {
            item.likedBy.add(userId);
            item.likeCount++;
            this.emit('item_liked', { itemId, userId, type });
        }
        
        return { success: true, likeCount: item.likeCount };
    }
    
    /**
     * 浏览帖子
     */
    viewThread(threadId) {
        const thread = this.threads.get(threadId);
        if (thread) {
            thread.viewCount++;
        }
        return thread;
    }
    
    /**
     * 获取帖子列表
     */
    getThreads(categoryId = null, filters = {}) {
        let threads = Array.from(this.threads.values());
        
        // 分类过滤
        if (categoryId) {
            threads = threads.filter(t => t.categoryId === categoryId);
        }
        
        // 状态过滤
        if (filters.status) {
            threads = threads.filter(t => t.status === filters.status);
        }
        
        // 排序
        if (filters.sortBy) {
            switch (filters.sortBy) {
                case 'latest':
                    threads.sort((a, b) => b.createdAt - a.createdAt);
                    break;
                case 'latest_reply':
                    threads.sort((a, b) => (b.lastReplyAt || 0) - (a.lastReplyAt || 0));
                    break;
                case 'views':
                    threads.sort((a, b) => b.viewCount - a.viewCount);
                    break;
                case 'replies':
                    threads.sort((a, b) => b.replyCount - a.replyCount);
                    break;
                case 'likes':
                    threads.sort((a, b) => b.likeCount - a.likeCount);
                    break;
            }
        }
        
        // 分页
        const page = filters.page || 1;
        const limit = filters.limit || 20;
        const start = (page - 1) * limit;
        
        return {
            threads: threads.slice(start, start + limit),
            total: threads.length,
            page,
            limit,
            totalPages: Math.ceil(threads.length / limit)
        };
    }
    
    /**
     * 获取帖子详情
     */
    getThread(threadId) {
        const thread = this.threads.get(threadId);
        if (thread) {
            thread.viewCount++;
        }
        return thread;
    }
    
    /**
     * 获取帖子回复
     */
    getThreadReplies(threadId, page = 1, limit = 20) {
        const posts = Array.from(this.posts.values())
            .filter(p => p.threadId === threadId);
        
        posts.sort((a, b) => a.createdAt - b.createdAt);
        
        const start = (page - 1) * limit;
        
        return {
            posts: posts.slice(start, start + limit),
            total: posts.length,
            page,
            limit,
            totalPages: Math.ceil(posts.length / limit)
        };
    }
    
    /**
     * 更新用户统计
     */
    updateUserStats(userId, updates) {
        if (!this.userStats.has(userId)) {
            this.userStats.set(userId, {
                threads: 0,
                posts: 0,
                likes: 0,
                reputation: 0,
                level: 1,
                experience: 0
            });
        }
        
        const stats = this.userStats.get(userId);
        
        if (updates.threads) stats.threads += updates.threads;
        if (updates.posts) stats.posts += updates.posts;
        if (updates.likes) stats.likes += updates.likes;
        
        // 计算声望
        stats.reputation = stats.threads * 10 + stats.posts * 5 + stats.likes * 2;
        
        // 计算等级
        stats.experience = stats.reputation;
        stats.level = Math.floor(Math.sqrt(stats.experience / 100)) + 1;
        
        this.emit('stats_updated', { userId, stats });
    }
    
    /**
     * 获取用户统计
     */
    getUserStats(userId) {
        return this.userStats.get(userId) || null;
    }
    
    /**
     * 管理操作
     */
    moderateThread(threadId, action, moderatorId) {
        const thread = this.threads.get(threadId);
        if (!thread) {
            return { success: false, error: '帖子不存在' };
        }
        
        switch (action) {
            case 'lock':
                thread.status = 'locked';
                break;
            case 'unlock':
                thread.status = 'active';
                break;
            case 'pin':
                thread.status = 'pinned';
                break;
            case 'unpin':
                thread.status = 'active';
                break;
            case 'hide':
                thread.status = 'hidden';
                break;
            case 'delete':
                this.threads.delete(threadId);
                break;
        }
        
        thread.updatedAt = Date.now();
        
        this.emit('thread_moderated', { threadId, action, moderatorId });
        
        return { success: true };
    }
    
    /**
     * 获取统计
     */
    getStats() {
        return {
            categories: this.categories.size,
            threads: this.threads.size,
            posts: this.posts.size,
            users: this.userStats.size,
            totalViews: Array.from(this.threads.values())
                .reduce((sum, t) => sum + t.viewCount, 0),
            totalLikes: Array.from(this.threads.values())
                .reduce((sum, t) => sum + t.likeCount, 0)
        };
    }
    
    /**
     * 清除
     */
    clear() {
        this.categories.clear();
        this.threads.clear();
        this.posts.clear();
        this.userStats.clear();
    }
}

module.exports = {
    ForumManager
};

console.log('社区论坛系统已加载');
