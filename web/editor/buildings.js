/**
 * 建筑放置和管理系统
 */

import * as THREE from 'three';

/**
 * 建筑放置助手
 */
export class BuildingPlacer {
    constructor(scene, camera) {
        this.scene = scene;
        this.camera = camera;
        this.previewMesh = null;
        this.isPlacing = false;
        this.currentType = null;
        this.snapToGrid = true;
        this.gridSize = 1;
        
        this.init();
    }
    
    /**
     * 初始化
     */
    init() {
        // 创建预览网格
        const geometry = new THREE.BoxGeometry(1, 1, 1);
        const material = new THREE.MeshBasicMaterial({
            color: 0x00ff00,
            transparent: true,
            opacity: 0.5,
            wireframe: true
        });
        
        this.previewMesh = new THREE.Mesh(geometry, material);
        this.previewMesh.visible = false;
        this.scene.add(this.previewMesh);
        
        // 创建网格助手
        const gridHelper = new THREE.GridHelper(100, 100, 0x444444, 0x444444);
        gridHelper.position.y = 0.01;
        this.scene.add(gridHelper);
    }
    
    /**
     * 开始放置
     */
    startPlacement(type) {
        this.currentType = type;
        this.isPlacing = true;
        this.previewMesh.visible = true;
        
        // 根据类型调整预览大小
        this.updatePreviewSize(type);
    }
    
    /**
     * 停止放置
     */
    stopPlacement() {
        this.isPlacing = false;
        this.previewMesh.visible = false;
        this.currentType = null;
    }
    
    /**
     * 更新预览大小
     */
    updatePreviewSize(type) {
        const sizes = {
            house: [4, 3, 4],
            tower: [3, 10, 3],
            castle: [8, 6, 8],
            bridge: [10, 1, 2]
        };
        
        const size = sizes[type] || [1, 1, 1];
        this.previewMesh.scale.set(size[0], size[1], size[2]);
    }
    
    /**
     * 更新预览位置
     */
    update(raycaster) {
        if (!this.isPlacing) return;
        
        const intersects = raycaster.intersectObjects(this.scene.children);
        
        if (intersects.length > 0) {
            const point = intersects[0].point;
            const normal = intersects[0].face.normal;
            
            if (this.snapToGrid) {
                point.x = Math.round(point.x / this.gridSize) * this.gridSize;
                point.z = Math.round(point.z / this.gridSize) * this.gridSize;
            }
            
            point.y += this.previewMesh.scale.y / 2;
            this.previewMesh.position.copy(point);
            
            // 检查是否有效位置
            const isValid = this.isValidPosition(point);
            this.previewMesh.material.color.setHex(isValid ? 0x00ff00 : 0xff0000);
        }
    }
    
    /**
     * 检查位置是否有效
     */
    isValidPosition(position) {
        // 检查是否在地面上
        if (position.y < 0.1) return false;
        
        // 检查是否与其他建筑重叠
        for (const object of this.scene.children) {
            if (object.userData.type === 'building') {
                const distance = position.distanceTo(object.position);
                const minDistance = (this.previewMesh.scale.x + object.geometry.parameters.width) / 2;
                if (distance < minDistance) return false;
            }
        }
        
        return true;
    }
    
    /**
     * 放置建筑
     */
    place(buildingSystem) {
        if (!this.isPlacing || !this.currentType) return null;
        
        const building = buildingSystem.createBuilding(
            this.currentType,
            this.previewMesh.position.clone()
        );
        
        if (building) {
            // 播放放置音效（如果有）
            console.log('建筑已放置');
        }
        
        return building;
    }
    
    /**
     * 清除
     */
    dispose() {
        this.scene.remove(this.previewMesh);
        this.previewMesh.geometry.dispose();
        this.previewMesh.material.dispose();
    }
}

/**
 * 建筑管理器
 */
export class BuildingManager {
    constructor(scene) {
        this.scene = scene;
        this.buildings = [];
        this.selectedBuilding = null;
    }
    
    /**
     * 添加建筑
     */
    addBuilding(building) {
        this.scene.add(building);
        this.buildings.push(building);
    }
    
    /**
     * 移除建筑
     */
    removeBuilding(building) {
        const index = this.buildings.indexOf(building);
        if (index > -1) {
            this.buildings.splice(index, 1);
            this.scene.remove(building);
        }
    }
    
    /**
     * 选择建筑
     */
    selectBuilding(building) {
        this.deselectBuilding();
        this.selectedBuilding = building;
        
        // 高亮
        if (building.material) {
            building.userData.originalEmissive = building.material.emissive.clone();
            building.material.emissive.setHex(0xffff00);
        }
    }
    
    /**
     * 取消选择
     */
    deselectBuilding() {
        if (this.selectedBuilding) {
            if (this.selectedBuilding.material && this.selectedBuilding.userData.originalEmissive) {
                this.selectedBuilding.material.emissive.copy(this.selectedBuilding.userData.originalEmissive);
            }
            this.selectedBuilding = null;
        }
    }
    
    /**
     * 获取所有建筑
     */
    getBuildings() {
        return this.buildings;
    }
    
    /**
     * 导出建筑数据
     */
    exportData() {
        return this.buildings.map(building => ({
            type: building.userData.buildingType,
            position: building.position.toArray(),
            rotation: building.rotation.toArray(),
            scale: building.scale.toArray()
        }));
    }
    
    /**
     * 导入建筑数据
     */
    importData(data, buildingSystem) {
        for (const item of data) {
            const building = buildingSystem.createBuilding(item.type, new THREE.Vector3().fromArray(item.position));
            if (building) {
                building.rotation.fromArray(item.rotation);
                building.scale.fromArray(item.scale);
            }
        }
    }
    
    /**
     * 清除
     */
    dispose() {
        for (const building of this.buildings) {
            this.scene.remove(building);
            building.geometry.dispose();
            building.material.dispose();
        }
        this.buildings = [];
    }
}

console.log('建筑放置系统已加载');
