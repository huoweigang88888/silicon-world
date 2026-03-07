/**
 * 脚本系统
 * 
 * 事件和触发器
 */

/**
 * 事件系统
 */
export class EventSystem {
    constructor() {
        this.events = {};
        this.triggers = [];
    }
    
    /**
     * 注册事件
     */
    on(eventName, callback) {
        if (!this.events[eventName]) {
            this.events[eventName] = [];
        }
        this.events[eventName].push(callback);
    }
    
    /**
     * 触发事件
     */
    emit(eventName, data) {
        if (this.events[eventName]) {
            for (const callback of this.events[eventName]) {
                callback(data);
            }
        }
    }
    
    /**
     * 移除事件
     */
    off(eventName, callback) {
        if (this.events[eventName]) {
            const index = this.events[eventName].indexOf(callback);
            if (index > -1) {
                this.events[eventName].splice(index, 1);
            }
        }
    }
    
    /**
     * 添加触发器
     */
    addTrigger(trigger) {
        this.triggers.push(trigger);
    }
    
    /**
     * 移除触发器
     */
    removeTrigger(trigger) {
        const index = this.triggers.indexOf(trigger);
        if (index > -1) {
            this.triggers.splice(index, 1);
        }
    }
    
    /**
     * 更新触发器
     */
    update(delta, worldState) {
        for (const trigger of this.triggers) {
            if (trigger.check(worldState)) {
                trigger.execute(worldState);
                if (trigger.once) {
                    this.removeTrigger(trigger);
                }
            }
        }
    }
}

/**
 * 触发器基类
 */
export class Trigger {
    constructor(condition, action, once = false) {
        this.condition = condition;
        this.action = action;
        this.once = once;
    }
    
    check(worldState) {
        return this.condition(worldState);
    }
    
    execute(worldState) {
        this.action(worldState);
    }
}

/**
 * 区域触发器
 */
export class RegionTrigger extends Trigger {
    constructor(region, onEnter, onExit, once = false) {
        super(
            (state) => {
                // 检查是否有物体进入区域
                for (const object of state.objects) {
                    if (region.containsPoint(object.position)) {
                        if (!object.wasInRegion) {
                            object.wasInRegion = true;
                            return { type: 'enter', object };
                        }
                    } else if (object.wasInRegion) {
                        object.wasInRegion = false;
                        return { type: 'exit', object };
                    }
                }
                return null;
            },
            (state) => {
                const result = this.condition(state);
                if (result) {
                    if (result.type === 'enter' && onEnter) {
                        onEnter(result.object);
                    } else if (result.type === 'exit' && onExit) {
                        onExit(result.object);
                    }
                }
            },
            once
        );
    }
}

/**
 * 时间触发器
 */
export class TimeTrigger extends Trigger {
    constructor(time, action, once = true) {
        super(
            (state) => state.time >= time,
            action,
            once
        );
        this.targetTime = time;
    }
}

/**
 * 交互触发器
 */
export class InteractionTrigger extends Trigger {
    constructor(object, onInteract, once = false) {
        super(
            (state) => {
                if (state.interactedObject === object) {
                    return true;
                }
                return false;
            },
            () => onInteract(object),
            once
        );
    }
}

/**
 * 脚本编辑器
 */
export class ScriptEditor {
    constructor(eventSystem) {
        this.eventSystem = eventSystem;
        this.scripts = {};
    }
    
    /**
     * 创建脚本
     */
    createScript(name, code) {
        this.scripts[name] = {
            code,
            enabled: true
        };
    }
    
    /**
     * 执行脚本
     */
    executeScript(name, context) {
        const script = this.scripts[name];
        if (!script || !script.enabled) return;
        
        try {
            // 创建安全的执行环境
            const env = {
                events: this.eventSystem,
                console: console,
                Math: Math,
                ...context
            };
            
            // 执行脚本
            const func = new Function(...Object.keys(env), script.code);
            func(...Object.values(env));
        } catch (error) {
            console.error(`脚本 "${name}" 执行错误:`, error);
        }
    }
    
    /**
     * 启用/禁用脚本
     */
    setScriptEnabled(name, enabled) {
        if (this.scripts[name]) {
            this.scripts[name].enabled = enabled;
        }
    }
    
    /**
     * 删除脚本
     */
    deleteScript(name) {
        delete this.scripts[name];
    }
    
    /**
     * 导出脚本
     */
    exportScripts() {
        return JSON.stringify(this.scripts, null, 2);
    }
    
    /**
     * 导入脚本
     */
    importScripts(json) {
        try {
            this.scripts = JSON.parse(json);
        } catch (error) {
            console.error('导入脚本失败:', error);
        }
    }
}

/**
 * 世界导出器
 */
export class WorldExporter {
    constructor(scene) {
        this.scene = scene;
    }
    
    /**
     * 导出世界
     */
    exportWorld(options = {}) {
        const config = {
            includeGeometry: options.includeGeometry !== false,
            includeMaterials: options.includeMaterials !== false,
            includeScripts: options.includeScripts !== false,
            ...options
        };
        
        const worldData = {
            version: '1.0',
            exportedAt: new Date().toISOString(),
            objects: [],
            terrain: null,
            buildings: [],
            scripts: {}
        };
        
        // 导出物体
        for (const object of this.scene.children) {
            if (object.userData.type) {
                const objectData = {
                    type: object.userData.type,
                    name: object.name,
                    position: object.position.toArray(),
                    rotation: object.rotation.toArray(),
                    scale: object.scale.toArray()
                };
                
                if (object.userData.buildingType) {
                    objectData.buildingType = object.userData.buildingType;
                    worldData.buildings.push(objectData);
                } else {
                    worldData.objects.push(objectData);
                }
            }
        }
        
        return worldData;
    }
    
    /**
     * 保存世界到文件
     */
    saveToFile(worldData, filename = 'world.json') {
        const blob = new Blob([JSON.stringify(worldData, null, 2)], {
            type: 'application/json'
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }
    
    /**
     * 从文件加载世界
     */
    loadFromFile(callback) {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const data = JSON.parse(e.target.result);
                    callback(data);
                } catch (error) {
                    console.error('加载世界失败:', error);
                }
            };
            reader.readAsText(file);
        });
        
        input.click();
    }
}

console.log('脚本和导出系统已加载');
