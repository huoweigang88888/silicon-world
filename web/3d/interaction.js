/**
 * 交互系统
 * 
 * 物体拾取、使用、交互
 */

import * as THREE from 'three';

/**
 * 交互类型
 */
export const InteractionType = {
    PICKUP: 'pickup',
    USE: 'use',
    EXAMINE: 'examine',
    TALK: 'talk',
    OPEN: 'open',
    CLOSE: 'close'
};

/**
 * 交互管理器
 */
export class InteractionManager {
    constructor(camera, scene) {
        this.camera = camera;
        this.scene = scene;
        this.interactables = [];
        this.highlightedObject = null;
        this.selectedObject = null;
        this.maxDistance = 5;
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        
        this.init();
    }
    
    /**
     * 初始化交互系统
     */
    init() {
        // 鼠标移动事件
        document.addEventListener('mousemove', (e) => this.onMouseMove(e), false);
        
        // 点击事件
        document.addEventListener('click', (e) => this.onClick(e), false);
        
        // 键盘事件
        document.addEventListener('keydown', (e) => this.onKeyDown(e), false);
    }
    
    /**
     * 添加可交互物体
     */
    addInteractable(object, interactionType, data = {}) {
        object.userData.interactable = true;
        object.userData.interactionType = interactionType;
        object.userData.interactionData = data;
        
        this.interactables.push(object);
    }
    
    /**
     * 移除可交互物体
     */
    removeInteractable(object) {
        const index = this.interactables.indexOf(object);
        if (index > -1) {
            this.interactables.splice(index, 1);
        }
    }
    
    /**
     * 鼠标移动
     */
    onMouseMove(event) {
        this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
        
        this.updateHighlight();
    }
    
    /**
     * 鼠标点击
     */
    onClick(event) {
        if (this.highlightedObject) {
            this.interact(this.highlightedObject);
        }
    }
    
    /**
     * 键盘按下
     */
    onKeyDown(event) {
        switch (event.code) {
            case 'KeyE':
            case 'KeyF':
                if (this.highlightedObject) {
                    this.interact(this.highlightedObject);
                }
                break;
        }
    }
    
    /**
     * 更新高亮
     */
    updateHighlight() {
        this.raycaster.setFromCamera(this.mouse, this.camera);
        
        const intersects = this.raycaster.intersectObjects(this.interactables);
        
        // 移除旧高亮
        if (this.highlightedObject && this.highlightedObject !== this.selectedObject) {
            this.removeHighlight(this.highlightedObject);
        }
        
        if (intersects.length > 0 && intersects[0].distance <= this.maxDistance) {
            this.highlightedObject = intersects[0].object;
            this.addHighlight(this.highlightedObject);
        } else {
            this.highlightedObject = null;
        }
    }
    
    /**
     * 添加高亮
     */
    addHighlight(object) {
        if (object.material) {
            object.userData.originalEmissive = object.material.emissive.clone();
            object.material.emissive.setHex(0xffff00);
        }
    }
    
    /**
     * 移除高亮
     */
    removeHighlight(object) {
        if (object.material && object.userData.originalEmissive) {
            object.material.emissive.copy(object.userData.originalEmissive);
        }
    }
    
    /**
     * 交互
     */
    interact(object) {
        const type = object.userData.interactionType;
        const data = object.userData.interactionData;
        
        switch (type) {
            case InteractionType.PICKUP:
                this.pickup(object, data);
                break;
            case InteractionType.USE:
                this.use(object, data);
                break;
            case InteractionType.EXAMINE:
                this.examine(object, data);
                break;
            case InteractionType.TALK:
                this.talk(object, data);
                break;
            case InteractionType.OPEN:
                this.open(object, data);
                break;
            case InteractionType.CLOSE:
                this.close(object, data);
                break;
        }
        
        // 触发事件
        if (data.onInteract) {
            data.onInteract(object);
        }
    }
    
    /**
     * 拾取
     */
    pickup(object, data) {
        console.log(`拾取：${object.name}`);
        
        // 从场景移除
        this.scene.remove(object);
        this.removeInteractable(object);
        
        // 添加到物品栏
        if (data.onPickup) {
            data.onPickup(object);
        }
    }
    
    /**
     * 使用
     */
    use(object, data) {
        console.log(`使用：${object.name}`);
        
        if (data.onUse) {
            data.onUse(object);
        }
    }
    
    /**
     * 检查
     */
    examine(object, data) {
        console.log(`检查：${object.name}`);
        console.log(`描述：${data.description || '无描述'}`);
        
        if (data.onExamine) {
            data.onExamine(object);
        }
    }
    
    /**
     * 对话
     */
    talk(object, data) {
        console.log(`对话：${object.name}`);
        
        if (data.onTalk) {
            data.onTalk(object);
        }
    }
    
    /**
     * 打开
     */
    open(object, data) {
        console.log(`打开：${object.name}`);
        
        if (data.onOpen) {
            data.onOpen(object);
        }
        
        // 更改交互类型
        object.userData.interactionType = InteractionType.CLOSE;
    }
    
    /**
     * 关闭
     */
    close(object, data) {
        console.log(`关闭：${object.name}`);
        
        if (data.onClose) {
            data.onClose(object);
        }
        
        // 更改交互类型
        object.userData.interactionType = InteractionType.OPEN;
    }
    
    /**
     * 获取最近的交互物体
     */
    getNearestInteractable(position, maxDistance = this.maxDistance) {
        let nearest = null;
        let nearestDistance = maxDistance;
        
        for (const object of this.interactables) {
            const distance = object.position.distanceTo(position);
            if (distance < nearestDistance) {
                nearest = object;
                nearestDistance = distance;
            }
        }
        
        return nearest;
    }
    
    /**
     * 更新
     */
    update() {
        this.updateHighlight();
    }
    
    /**
     * 清理
     */
    dispose() {
        this.interactables = [];
        this.highlightedObject = null;
        this.selectedObject = null;
    }
}

/**
 * 物品栏
 */
export class Inventory {
    constructor(maxSlots = 10) {
        this.maxSlots = maxSlots;
        this.slots = new Array(maxSlots).fill(null);
        this.selectedSlot = 0;
    }
    
    /**
     * 添加物品
     */
    addItem(item, slot = -1) {
        if (slot === -1) {
            // 找空位
            slot = this.slots.findIndex(s => s === null);
        }
        
        if (slot === -1 || slot >= this.maxSlots) {
            return false; // 物品栏已满
        }
        
        this.slots[slot] = item;
        return true;
    }
    
    /**
     * 移除物品
     */
    removeItem(slot) {
        if (slot >= 0 && slot < this.maxSlots) {
            const item = this.slots[slot];
            this.slots[slot] = null;
            return item;
        }
        return null;
    }
    
    /**
     * 获取物品
     */
    getItem(slot) {
        if (slot >= 0 && slot < this.maxSlots) {
            return this.slots[slot];
        }
        return null;
    }
    
    /**
     * 选择物品
     */
    selectSlot(slot) {
        if (slot >= 0 && slot < this.maxSlots) {
            this.selectedSlot = slot;
            return this.slots[slot];
        }
        return null;
    }
    
    /**
     * 获取选中物品
     */
    getSelectedItem() {
        return this.slots[this.selectedSlot];
    }
    
    /**
     * 查找物品
     */
    findItem(itemName) {
        return this.slots.findIndex(item => item && item.name === itemName);
    }
    
    /**
     * 清空
     */
    clear() {
        this.slots.fill(null);
    }
    
    /**
     * 导出为 JSON
     */
    toJSON() {
        return {
            maxSlots: this.maxSlots,
            slots: this.slots,
            selectedSlot: this.selectedSlot
        };
    }
    
    /**
     * 从 JSON 加载
     */
    fromJSON(data) {
        this.maxSlots = data.maxSlots;
        this.slots = data.slots;
        this.selectedSlot = data.selectedSlot;
    }
}

/**
 * 交互提示 UI
 */
export class InteractionUI {
    constructor() {
        this.element = null;
        this.init();
    }
    
    /**
     * 初始化 UI
     */
    init() {
        this.element = document.createElement('div');
        this.element.style.cssText = `
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 16px;
            pointer-events: none;
            display: none;
            z-index: 1000;
        `;
        document.body.appendChild(this.element);
    }
    
    /**
     * 显示提示
     */
    show(text) {
        this.element.textContent = text;
        this.element.style.display = 'block';
    }
    
    /**
     * 隐藏提示
     */
    hide() {
        this.element.style.display = 'none';
    }
    
    /**
     * 更新
     */
    update(object) {
        if (object && object.userData.interactable) {
            const type = object.userData.interactionType;
            const text = this.getInteractionText(type);
            this.show(text);
        } else {
            this.hide();
        }
    }
    
    /**
     * 获取交互文本
     */
    getInteractionText(type) {
        const texts = {
            [InteractionType.PICKUP]: '[E] 拾取',
            [InteractionType.USE]: '[E] 使用',
            [InteractionType.EXAMINE]: '[E] 检查',
            [InteractionType.TALK]: '[E] 对话',
            [InteractionType.OPEN]: '[E] 打开',
            [InteractionType.CLOSE]: '[E] 关闭'
        };
        return texts[type] || '[E] 交互';
    }
    
    /**
     * 清理
     */
    dispose() {
        if (this.element && this.element.parentNode) {
            this.element.parentNode.removeChild(this.element);
        }
    }
}

// 使用示例
if (typeof window !== 'undefined') {
    console.log('交互系统已加载');
    console.log('交互类型:', Object.keys(InteractionType));
}
