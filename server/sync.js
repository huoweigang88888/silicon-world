/**
 * 状态同步系统
 * 
 * 玩家状态、位置、动作同步
 */

const { EventEmitter } = require('events');

/**
 * 状态同步管理器
 */
class StateSyncManager extends EventEmitter {
    constructor(options = {}) {
        super();
        this.options = {
            tickRate: options.tickRate || 20, // 20 ticks per second
            interpolationDelay: options.interpolationDelay || 100, // ms
            extrapolationLimit: options.extrapolationLimit || 500, // ms
            ...options
        };
        
        this.states = new Map(); // playerId -> state
        this.history = new Map(); // playerId -> [states]
        this.lastTick = 0;
        
        this.startTickLoop();
    }
    
    /**
     * 更新玩家状态
     */
    updateState(playerId, state) {
        const timestamp = Date.now();
        
        const fullState = {
            playerId,
            timestamp,
            position: state.position || { x: 0, y: 0, z: 0 },
            rotation: state.rotation || { x: 0, y: 0, z: 0 },
            velocity: state.velocity || { x: 0, y: 0, z: 0 },
            action: state.action || null,
            metadata: state.metadata || {}
        };
        
        // 保存状态
        this.states.set(playerId, fullState);
        
        // 保存历史记录
        if (!this.history.has(playerId)) {
            this.history.set(playerId, []);
        }
        
        const playerHistory = this.history.get(playerId);
        playerHistory.push(fullState);
        
        // 限制历史记录大小 (保留最近 2 秒)
        const maxHistorySize = Math.ceil(this.options.tickRate * 2);
        while (playerHistory.length > maxHistorySize) {
            playerHistory.shift();
        }
        
        this.emit('state_updated', fullState);
        
        return fullState;
    }
    
    /**
     * 获取玩家状态
     */
    getState(playerId, timestamp = null) {
        if (!timestamp) {
            return this.states.get(playerId);
        }
        
        // 获取历史状态 (用于插值)
        const history = this.history.get(playerId);
        if (!history || history.length === 0) {
            return null;
        }
        
        // 找到timestamp前后的两个状态
        let before = null;
        let after = null;
        
        for (let i = 0; i < history.length - 1; i++) {
            if (history[i].timestamp <= timestamp && history[i + 1].timestamp >= timestamp) {
                before = history[i];
                after = history[i + 1];
                break;
            }
        }
        
        if (!before && !after) {
            return history[history.length - 1];
        }
        
        if (!before) {
            return after;
        }
        
        if (!after) {
            return before;
        }
        
        // 插值
        return this.interpolate(before, after, timestamp);
    }
    
    /**
     * 插值两个状态
     */
    interpolate(before, after, timestamp) {
        const t = (timestamp - before.timestamp) / (after.timestamp - before.timestamp);
        
        return {
            playerId: before.playerId,
            timestamp,
            position: {
                x: before.position.x + (after.position.x - before.position.x) * t,
                y: before.position.y + (after.position.y - before.position.y) * t,
                z: before.position.z + (after.position.z - before.position.z) * t
            },
            rotation: {
                x: before.rotation.x + (after.rotation.x - before.rotation.x) * t,
                y: before.rotation.y + (after.rotation.y - before.rotation.y) * t,
                z: before.rotation.z + (after.rotation.z - before.rotation.z) * t
            },
            velocity: before.velocity,
            action: before.action
        };
    }
    
    /**
     * 预测状态 (外推)
     */
    extrapolate(playerId, timestamp) {
        const history = this.history.get(playerId);
        if (!history || history.length < 2) {
            return this.getState(playerId);
        }
        
        const latest = history[history.length - 1];
        const previous = history[history.length - 2];
        
        const dt = (latest.timestamp - previous.timestamp) / 1000; // seconds
        const extrapolateTime = (timestamp - latest.timestamp) / 1000;
        
        // 限制外推时间
        if (extrapolateTime * 1000 > this.options.extrapolationLimit) {
            return latest;
        }
        
        // 使用速度外推位置
        const velocity = {
            x: (latest.position.x - previous.position.x) / dt,
            y: (latest.position.y - previous.position.y) / dt,
            z: (latest.position.z - previous.position.z) / dt
        };
        
        return {
            ...latest,
            timestamp,
            position: {
                x: latest.position.x + velocity.x * extrapolateTime,
                y: latest.position.y + velocity.y * extrapolateTime,
                z: latest.position.z + velocity.z * extrapolateTime
            }
        };
    }
    
    /**
     * 开始 tick 循环
     */
    startTickLoop() {
        const tickInterval = 1000 / this.options.tickRate;
        
        setInterval(() => {
            this.lastTick++;
            this.emit('tick', this.lastTick);
        }, tickInterval);
    }
    
    /**
     * 获取所有玩家状态
     */
    getAllStates() {
        return Array.from(this.states.values());
    }
    
    /**
     * 清除玩家数据
     */
    clearPlayer(playerId) {
        this.states.delete(playerId);
        this.history.delete(playerId);
        this.emit('player_cleared', playerId);
    }
    
    /**
     * 获取统计信息
     */
    getStats() {
        return {
            playerCount: this.states.size,
            tickRate: this.options.tickRate,
            lastTick: this.lastTick,
            historySizes: Array.from(this.history.entries()).map(
                ([playerId, history]) => ({ playerId, size: history.length })
            )
        };
    }
}

/**
 * 位置同步优化
 */
class PositionSync {
    constructor(stateSync) {
        this.stateSync = stateSync;
        this.deadReckoning = new Map(); // playerId -> predicted state
    }
    
    /**
     * 更新位置 (带死 reckoning)
     */
    updatePosition(playerId, position, rotation, velocity) {
        const state = this.stateSync.updateState(playerId, {
            position,
            rotation,
            velocity
        });
        
        // 保存预测状态
        this.deadReckoning.set(playerId, {
            position: { ...position },
            rotation: { ...rotation },
            velocity: { ...velocity },
            timestamp: Date.now()
        });
        
        return state;
    }
    
    /**
     * 获取平滑位置
     */
    getSmoothPosition(playerId, timestamp) {
        const predicted = this.deadReckoning.get(playerId);
        if (!predicted) {
            return this.stateSync.getState(playerId, timestamp);
        }
        
        // 使用预测 + 插值
        const elapsed = timestamp - predicted.timestamp;
        const dt = elapsed / 1000;
        
        return {
            x: predicted.position.x + predicted.velocity.x * dt,
            y: predicted.position.y + predicted.velocity.y * dt,
            z: predicted.position.z + predicted.velocity.z * dt
        };
    }
    
    /**
     * 校正位置 (当预测误差过大时)
     */
    correctPosition(playerId, actualPosition) {
        const predicted = this.deadReckoning.get(playerId);
        if (!predicted) return;
        
        const error = {
            x: actualPosition.x - predicted.position.x,
            y: actualPosition.y - predicted.position.y,
            z: actualPosition.z - predicted.position.z
        };
        
        const errorMagnitude = Math.sqrt(
            error.x * error.x +
            error.y * error.y +
            error.z * error.z
        );
        
        // 如果误差过大，立即校正
        if (errorMagnitude > 1.0) {
            this.deadReckoning.set(playerId, {
                position: { ...actualPosition },
                velocity: predicted.velocity,
                timestamp: Date.now()
            });
        } else {
            // 否则平滑校正
            const correctionFactor = 0.1;
            predicted.position.x += error.x * correctionFactor;
            predicted.position.y += error.y * correctionFactor;
            predicted.position.z += error.z * correctionFactor;
        }
    }
}

/**
 * 动作同步
 */
class ActionSync {
    constructor(stateSync) {
        this.stateSync = stateSync;
        this.activeActions = new Map(); // playerId -> action
    }
    
    /**
     * 开始动作
     */
    startAction(playerId, action) {
        const actionState = {
            type: action.type,
            startTime: Date.now(),
            duration: action.duration || 0,
            data: action.data || {},
            completed: false
        };
        
        this.activeActions.set(playerId, actionState);
        
        // 更新状态
        this.stateSync.updateState(playerId, {
            action: actionState
        });
        
        // 如果动作有持续时间，设置完成定时器
        if (actionState.duration > 0) {
            setTimeout(() => {
                this.completeAction(playerId);
            }, actionState.duration);
        }
        
        return actionState;
    }
    
    /**
     * 完成动作
     */
    completeAction(playerId) {
        const action = this.activeActions.get(playerId);
        if (!action) return;
        
        action.completed = true;
        this.activeActions.delete(playerId);
        
        this.stateSync.updateState(playerId, {
            action: null
        });
        
        this.stateSync.emit('action_completed', {
            playerId,
            action
        });
    }
    
    /**
     * 取消动作
     */
    cancelAction(playerId) {
        const action = this.activeActions.get(playerId);
        if (!action) return;
        
        this.activeActions.delete(playerId);
        
        this.stateSync.updateState(playerId, {
            action: null
        });
        
        this.stateSync.emit('action_cancelled', {
            playerId,
            action
        });
    }
    
    /**
     * 获取当前动作
     */
    getActiveAction(playerId) {
        return this.activeActions.get(playerId);
    }
}

module.exports = {
    StateSyncManager,
    PositionSync,
    ActionSync
};

console.log('状态同步系统已加载');
