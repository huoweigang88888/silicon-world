/**
 * 硅基世界 - WebSocket 服务器
 * 
 * 多人在线服务
 */

const WebSocket = require('ws');
const http = require('http');
const express = require('express');
const { v4: uuidv4 } = require('uuid');

// 创建 Express 应用
const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// 中间件
app.use(express.json());

// 健康检查
app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// API 路由
app.get('/api/stats', (req, res) => {
    res.json({
        players: players.size,
        rooms: rooms.size,
        uptime: process.uptime()
    });
});

// 玩家管理
const players = new Map();
const rooms = new Map();

// WebSocket 连接处理
wss.on('connection', (ws) => {
    const playerId = uuidv4();
    
    console.log(`玩家连接：${playerId}`);
    
    // 玩家数据
    const player = {
        id: playerId,
        ws: ws,
        name: `Player_${playerId.slice(0, 6)}`,
        position: { x: 0, y: 0, z: 0 },
        rotation: { x: 0, y: 0, z: 0 },
        room: null,
        connectedAt: new Date()
    };
    
    players.set(playerId, player);
    
    // 发送欢迎消息
    sendToPlayer(ws, {
        type: 'welcome',
        playerId: playerId,
        message: '欢迎来到硅基世界！'
    });
    
    // 接收消息
    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);
            handleMessage(player, data);
        } catch (error) {
            console.error('消息解析错误:', error);
        }
    });
    
    // 断开连接
    ws.on('close', () => {
        console.log(`玩家断开：${playerId}`);
        
        // 离开房间
        if (player.room) {
            leaveRoom(player);
        }
        
        // 移除玩家
        players.delete(playerId);
        
        // 通知其他玩家
        broadcast({
            type: 'player_left',
            playerId: playerId
        }, playerId);
    });
    
    // 错误处理
    ws.on('error', (error) => {
        console.error(`玩家 ${playerId} 错误:`, error);
    });
    
    // 心跳
    const heartbeat = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
            sendToPlayer(ws, { type: 'heartbeat', timestamp: Date.now() });
        } else {
            clearInterval(heartbeat);
        }
    }, 30000);
});

// 消息处理
function handleMessage(player, data) {
    switch (data.type) {
        case 'join_room':
            joinRoom(player, data.roomId);
            break;
            
        case 'leave_room':
            leaveRoom(player);
            break;
            
        case 'player_move':
            handlePlayerMove(player, data);
            break;
            
        case 'chat_message':
            handleChatMessage(player, data);
            break;
            
        case 'player_action':
            handlePlayerAction(player, data);
            break;
            
        default:
            console.log('未知消息类型:', data.type);
    }
}

// 加入房间
function joinRoom(player, roomId) {
    // 离开当前房间
    if (player.room) {
        leaveRoom(player);
    }
    
    // 创建或加入房间
    let room = rooms.get(roomId);
    if (!room) {
        room = {
            id: roomId,
            players: new Set(),
            createdAt: new Date()
        };
        rooms.set(roomId, room);
    }
    
    // 加入房间
    room.players.add(player.id);
    player.room = roomId;
    
    // 发送房间信息
    sendToPlayer(player.ws, {
        type: 'room_joined',
        roomId: roomId,
        players: Array.from(room.players)
    });
    
    // 通知房间内其他玩家
    broadcastToRoom(roomId, {
        type: 'player_joined',
        playerId: player.id,
        playerName: player.name
    }, player.id);
}

// 离开房间
function leaveRoom(player) {
    if (!player.room) return;
    
    const room = rooms.get(player.room);
    if (room) {
        room.players.delete(player.id);
        
        // 如果房间为空，删除房间
        if (room.players.size === 0) {
            rooms.delete(player.room);
        } else {
            // 通知其他玩家
            broadcastToRoom(player.room, {
                type: 'player_left',
                playerId: player.id
            }, player.id);
        }
    }
    
    player.room = null;
}

// 处理玩家移动
function handlePlayerMove(player, data) {
    player.position = data.position;
    player.rotation = data.rotation;
    
    // 广播给房间内其他玩家
    if (player.room) {
        broadcastToRoom(player.room, {
            type: 'player_moved',
            playerId: player.id,
            position: player.position,
            rotation: player.rotation
        }, player.id);
    }
}

// 处理聊天消息
function handleChatMessage(player, data) {
    const message = {
        type: 'chat_message',
        playerId: player.id,
        playerName: player.name,
        message: data.message,
        timestamp: Date.now()
    };
    
    // 广播给房间内所有玩家
    if (player.room) {
        broadcastToRoom(player.room, message);
    }
}

// 处理玩家动作
function handlePlayerAction(player, data) {
    // 广播给房间内其他玩家
    if (player.room) {
        broadcastToRoom(player.room, {
            type: 'player_action',
            playerId: player.id,
            action: data.action,
            data: data.data
        }, player.id);
    }
}

// 发送消息给玩家
function sendToPlayer(ws, data) {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(data));
    }
}

// 广播消息 (排除指定玩家)
function broadcast(data, excludePlayerId = null) {
    for (const [playerId, player] of players) {
        if (playerId !== excludePlayerId) {
            sendToPlayer(player.ws, data);
        }
    }
}

// 广播给房间内玩家
function broadcastToRoom(roomId, data, excludePlayerId = null) {
    const room = rooms.get(roomId);
    if (!room) return;
    
    for (const playerId of room.players) {
        if (playerId !== excludePlayerId) {
            const player = players.get(playerId);
            if (player) {
                sendToPlayer(player.ws, data);
            }
        }
    }
}

// 启动服务器
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`🚀 硅基世界服务器启动在端口 ${PORT}`);
    console.log(`📊 健康检查：http://localhost:${PORT}/health`);
    console.log(`📈 统计信息：http://localhost:${PORT}/api/stats`);
});

// 优雅关闭
process.on('SIGTERM', () => {
    console.log('服务器正在关闭...');
    
    // 通知所有玩家
    broadcast({
        type: 'server_shutdown',
        message: '服务器即将关闭，请重新连接'
    });
    
    // 关闭所有连接
    wss.clients.forEach((client) => {
        client.close(1001, '服务器关闭');
    });
    
    server.close(() => {
        console.log('服务器已关闭');
        process.exit(0);
    });
});

console.log('硅基世界 WebSocket 服务器已加载');
