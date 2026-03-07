/**
 * 社交系统
 * 
 * 好友、聊天、公会
 */

const { EventEmitter } = require('events');

/**
 * 好友系统
 */
class FriendSystem extends EventEmitter {
    constructor() {
        super();
        this.friends = new Map(); // playerId -> [friendIds]
        this.requests = new Map(); // requestId -> {from, to, timestamp}
    }
    
    /**
     * 发送好友请求
     */
    sendRequest(fromPlayerId, toPlayerId) {
        // 检查是否已是好友
        if (this.areFriends(fromPlayerId, toPlayerId)) {
            return { success: false, error: '已是好友' };
        }
        
        // 检查是否有待处理请求
        for (const [requestId, request] of this.requests) {
            if (request.from === fromPlayerId && request.to === toPlayerId) {
                return { success: false, error: '已有待处理请求' };
            }
        }
        
        const requestId = `friend_${fromPlayerId}_${toPlayerId}_${Date.now()}`;
        
        this.requests.set(requestId, {
            from: fromPlayerId,
            to: toPlayerId,
            timestamp: Date.now()
        });
        
        this.emit('friend_request', {
            requestId,
            from: fromPlayerId,
            to: toPlayerId
        });
        
        return { success: true, requestId };
    }
    
    /**
     * 接受好友请求
     */
    acceptRequest(requestId, playerId) {
        const request = this.requests.get(requestId);
        if (!request || request.to !== playerId) {
            return { success: false, error: '请求无效' };
        }
        
        // 添加好友
        this.addFriend(request.from, request.to);
        this.addFriend(request.to, request.from);
        
        // 删除请求
        this.requests.delete(requestId);
        
        this.emit('friend_added', {
            playerId1: request.from,
            playerId2: request.to
        });
        
        return { success: true };
    }
    
    /**
     * 拒绝好友请求
     */
    rejectRequest(requestId, playerId) {
        const request = this.requests.get(requestId);
        if (!request || request.to !== playerId) {
            return { success: false, error: '请求无效' };
        }
        
        this.requests.delete(requestId);
        
        this.emit('friend_request_rejected', {
            requestId,
            from: request.from,
            to: playerId
        });
        
        return { success: true };
    }
    
    /**
     * 添加好友
     */
    addFriend(playerId1, playerId2) {
        if (!this.friends.has(playerId1)) {
            this.friends.set(playerId1, new Set());
        }
        this.friends.get(playerId1).add(playerId2);
    }
    
    /**
     * 删除好友
     */
    removeFriend(playerId1, playerId2) {
        if (this.friends.has(playerId1)) {
            this.friends.get(playerId1).delete(playerId2);
        }
        if (this.friends.has(playerId2)) {
            this.friends.get(playerId2).delete(playerId1);
        }
        
        this.emit('friend_removed', {
            playerId1,
            playerId2
        });
    }
    
    /**
     * 检查是否是好友
     */
    areFriends(playerId1, playerId2) {
        const friends = this.friends.get(playerId1);
        return friends ? friends.has(playerId2) : false;
    }
    
    /**
     * 获取好友列表
     */
    getFriends(playerId) {
        const friends = this.friends.get(playerId);
        return friends ? Array.from(friends) : [];
    }
    
    /**
     * 获取待处理请求
     */
    getPendingRequests(playerId) {
        const requests = [];
        for (const [requestId, request] of this.requests) {
            if (request.to === playerId) {
                requests.push({
                    requestId,
                    from: request.from,
                    timestamp: request.timestamp
                });
            }
        }
        return requests;
    }
    
    /**
     * 清除玩家数据
     */
    clearPlayer(playerId) {
        this.friends.delete(playerId);
        
        // 删除相关请求
        for (const [requestId, request] of this.requests) {
            if (request.from === playerId || request.to === playerId) {
                this.requests.delete(requestId);
            }
        }
    }
}

/**
 * 聊天系统
 */
class ChatSystem extends EventEmitter {
    constructor() {
        super();
        this.messages = new Map(); // roomId -> [messages]
        this.privateMessages = new Map(); // playerId -> [messages]
        this.maxHistory = 100; // 每个房间最多保存 100 条消息
    }
    
    /**
     * 发送房间消息
     */
    sendRoomMessage(roomId, playerId, playerName, content) {
        const message = {
            id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            roomId,
            playerId,
            playerName,
            content,
            timestamp: Date.now(),
            type: 'room'
        };
        
        // 保存消息
        if (!this.messages.has(roomId)) {
            this.messages.set(roomId, []);
        }
        
        const roomMessages = this.messages.get(roomId);
        roomMessages.push(message);
        
        // 限制历史消息数量
        while (roomMessages.length > this.maxHistory) {
            roomMessages.shift();
        }
        
        this.emit('message', message);
        
        return message;
    }
    
    /**
     * 发送私聊消息
     */
    sendPrivateMessage(fromPlayerId, toPlayerId, fromPlayerName, content) {
        const message = {
            id: `pm_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            from: fromPlayerId,
            to: toPlayerId,
            fromName: fromPlayerName,
            content,
            timestamp: Date.now(),
            type: 'private',
            read: false
        };
        
        // 保存消息
        if (!this.privateMessages.has(fromPlayerId)) {
            this.privateMessages.set(fromPlayerId, []);
        }
        if (!this.privateMessages.has(toPlayerId)) {
            this.privateMessages.set(toPlayerId, []);
        }
        
        this.privateMessages.get(fromPlayerId).push(message);
        this.privateMessages.get(toPlayerId).push(message);
        
        this.emit('private_message', message);
        
        return message;
    }
    
    /**
     * 获取房间消息历史
     */
    getRoomHistory(roomId, limit = 50) {
        const messages = this.messages.get(roomId) || [];
        return messages.slice(-limit);
    }
    
    /**
     * 获取私聊历史
     */
    getPrivateHistory(playerId1, playerId2, limit = 50) {
        const messages1 = this.privateMessages.get(playerId1) || [];
        const messages2 = this.privateMessages.get(playerId2) || [];
        
        const allMessages = [...messages1, ...messages2];
        
        // 过滤出两人之间的消息
        const conversations = allMessages.filter(msg =>
            (msg.from === playerId1 && msg.to === playerId2) ||
            (msg.from === playerId2 && msg.to === playerId1)
        );
        
        // 按时间排序
        conversations.sort((a, b) => a.timestamp - b.timestamp);
        
        return conversations.slice(-limit);
    }
    
    /**
     * 标记私聊为已读
     */
    markAsRead(playerId, fromPlayerId) {
        const messages = this.privateMessages.get(playerId) || [];
        for (const message of messages) {
            if (message.from === fromPlayerId) {
                message.read = true;
            }
        }
    }
    
    /**
     * 获取未读消息数
     */
    getUnreadCount(playerId) {
        const messages = this.privateMessages.get(playerId) || [];
        return messages.filter(msg => msg.to === playerId && !msg.read).length;
    }
    
    /**
     * 清除房间消息
     */
    clearRoom(roomId) {
        this.messages.delete(roomId);
    }
    
    /**
     * 清除玩家数据
     */
    clearPlayer(playerId) {
        this.privateMessages.delete(playerId);
    }
}

/**
 * 公会系统
 */
class GuildSystem extends EventEmitter {
    constructor() {
        super();
        this.guilds = new Map(); // guildId -> guild
        this.playerGuilds = new Map(); // playerId -> guildId
        this.nextGuildId = 1;
    }
    
    /**
     * 创建公会
     */
    createGuild(name, leaderId, description = '') {
        const guildId = `guild_${this.nextGuildId++}`;
        
        const guild = {
            id: guildId,
            name,
            leaderId,
            description,
            members: new Set([leaderId]),
            officers: new Set(),
            createdAt: Date.now(),
            level: 1,
            experience: 0
        };
        
        this.guilds.set(guildId, guild);
        this.playerGuilds.set(leaderId, guildId);
        
        this.emit('guild_created', guild);
        
        return guild;
    }
    
    /**
     * 加入公会
     */
    joinGuild(guildId, playerId) {
        const guild = this.guilds.get(guildId);
        if (!guild) {
            return { success: false, error: '公会不存在' };
        }
        
        if (guild.members.has(playerId)) {
            return { success: false, error: '已在公会中' };
        }
        
        guild.members.add(playerId);
        this.playerGuilds.set(playerId, guildId);
        
        this.emit('member_joined', {
            guildId,
            playerId
        });
        
        return { success: true };
    }
    
    /**
     * 离开公会
     */
    leaveGuild(playerId) {
        const guildId = this.playerGuilds.get(playerId);
        if (!guildId) {
            return { success: false, error: '不在公会中' };
        }
        
        const guild = this.guilds.get(guildId);
        
        // 如果是会长，转移或解散公会
        if (guild.leaderId === playerId) {
            if (guild.members.size > 1) {
                // 转移给第一个官员
                const newLeader = Array.from(guild.officers)[0] || 
                                 Array.from(guild.members).find(id => id !== playerId);
                guild.leaderId = newLeader;
            } else {
                // 解散公会
                this.disbandGuild(guildId);
                return { success: true };
            }
        }
        
        guild.members.delete(playerId);
        guild.officers.delete(playerId);
        this.playerGuilds.delete(playerId);
        
        this.emit('member_left', {
            guildId,
            playerId
        });
        
        return { success: true };
    }
    
    /**
     * 解散公会
     */
    disbandGuild(guildId) {
        const guild = this.guilds.get(guildId);
        if (!guild) return;
        
        // 清除所有成员的公会信息
        for (const memberId of guild.members) {
            this.playerGuilds.delete(memberId);
        }
        
        this.guilds.delete(guildId);
        
        this.emit('guild_disbanded', {
            guildId
        });
    }
    
    /**
     * 设置官员
     */
    setOfficer(guildId, playerId, isOfficer) {
        const guild = this.guilds.get(guildId);
        if (!guild || guild.leaderId !== playerId) {
            return { success: false, error: '无权操作' };
        }
        
        if (isOfficer) {
            guild.officers.add(playerId);
        } else {
            guild.officers.delete(playerId);
        }
        
        return { success: true };
    }
    
    /**
     * 获取公会信息
     */
    getGuild(guildId) {
        const guild = this.guilds.get(guildId);
        if (!guild) return null;
        
        return {
            id: guild.id,
            name: guild.name,
            leaderId: guild.leaderId,
            description: guild.description,
            memberCount: guild.members.size,
            officers: Array.from(guild.officers),
            members: Array.from(guild.members),
            level: guild.level,
            experience: guild.experience,
            createdAt: guild.createdAt
        };
    }
    
    /**
     * 获取玩家公会
     */
    getPlayerGuild(playerId) {
        const guildId = this.playerGuilds.get(playerId);
        if (!guildId) return null;
        
        return this.getGuild(guildId);
    }
    
    /**
     * 添加公会经验
     */
    addExperience(guildId, exp) {
        const guild = this.guilds.get(guildId);
        if (!guild) return;
        
        guild.experience += exp;
        
        // 升级逻辑 (简化)
        const levelUpExp = guild.level * 1000;
        if (guild.experience >= levelUpExp) {
            guild.level++;
            guild.experience -= levelUpExp;
            
            this.emit('guild_level_up', {
                guildId,
                level: guild.level
            });
        }
    }
    
    /**
     * 清除玩家数据
     */
    clearPlayer(playerId) {
        this.leaveGuild(playerId);
    }
}

module.exports = {
    FriendSystem,
    ChatSystem,
    GuildSystem
};

console.log('社交系统已加载');
