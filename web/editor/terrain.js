/**
 * 地形系统
 * 
 * 地形生成和编辑
 */

import * as THREE from 'three';

/**
 * 地形生成器
 */
export class TerrainGenerator {
    constructor(scene) {
        this.scene = scene;
        this.terrains = [];
    }
    
    /**
     * 生成程序化地形
     */
    generateTerrain(width, depth, segments, options = {}) {
        const config = {
            heightScale: options.heightScale || 10,
            noiseScale: options.noiseScale || 0.1,
            octaves: options.octaves || 4,
            persistence: options.persistence || 0.5,
            lacunarity: options.lacunarity || 2,
            ...options
        };
        
        const geometry = new THREE.PlaneGeometry(width, depth, segments, segments);
        const positions = geometry.attributes.position.array;
        
        // 生成高度图
        for (let i = 0; i < positions.length; i += 3) {
            const x = positions[i];
            const y = positions[i + 1];
            
            // 叠加噪声
            let height = 0;
            let amplitude = 1;
            let frequency = config.noiseScale;
            
            for (let o = 0; o < config.octaves; o++) {
                height += this.simpleNoise(x * frequency, y * frequency) * amplitude;
                amplitude *= config.persistence;
                frequency *= config.lacunarity;
            }
            
            positions[i + 2] = height * config.heightScale;
        }
        
        geometry.computeVertexNormals();
        
        // 创建材质
        const material = new THREE.MeshStandardMaterial({
            color: 0x3d8c40,
            roughness: 0.8,
            metalness: 0.1,
            flatShading: true
        });
        
        const terrain = new THREE.Mesh(geometry, material);
        terrain.rotation.x = -Math.PI / 2;
        terrain.receiveShadow = true;
        
        this.scene.add(terrain);
        this.terrains.push(terrain);
        
        return terrain;
    }
    
    /**
     * 简单噪声函数
     */
    simpleNoise(x, y) {
        const X = Math.floor(x) & 255;
        const Y = Math.floor(y) & 255;
        
        x -= Math.floor(x);
        y -= Math.floor(y);
        
        const u = this.fade(x);
        const v = this.fade(y);
        
        const A = this.perm[X] + Y;
        const B = this.perm[X + 1] + Y;
        
        return this.lerp(
            this.lerp(this.grad(this.perm[A], x, y), this.grad(this.perm[B], x - 1, y), u),
            this.lerp(this.grad(this.perm[A + 1], x, y - 1), this.grad(this.perm[B + 1], x - 1, y - 1), u),
            v
        );
    }
    
    fade(t) {
        return t * t * t * (t * (t * 6 - 15) + 10);
    }
    
    lerp(t, a, b) {
        return a + t * (b - a);
    }
    
    grad(hash, x, y) {
        const h = hash & 3;
        const u = h < 2 ? x : y;
        const v = h < 2 ? y : x;
        return ((h & 1) === 0 ? u : -u) + ((h & 2) === 0 ? v : -v);
    }
    
    get perm() {
        if (!this._perm) {
            this._perm = new Uint8Array(512);
            const p = new Uint8Array(256);
            for (let i = 0; i < 256; i++) p[i] = i;
            
            // 洗牌
            for (let i = 255; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [p[i], p[j]] = [p[j], p[i]];
            }
            
            for (let i = 0; i < 512; i++) {
                this._perm[i] = p[i & 255];
            }
        }
        return this._perm;
    }
    
    /**
     * 创建高原地形
     */
    createPlateau(width, depth, height, plateauWidth, plateauDepth) {
        const geometry = new THREE.PlaneGeometry(width, depth, 64, 64);
        const positions = geometry.attributes.position.array;
        
        for (let i = 0; i < positions.length; i += 3) {
            const x = positions[i];
            const y = positions[i + 1];
            
            // 计算到中心的距离
            const dx = Math.abs(x);
            const dy = Math.abs(y);
            
            // 高原区域
            if (dx < plateauWidth / 2 && dy < plateauDepth / 2) {
                positions[i + 2] = height;
            } else {
                // 渐变到边缘
                const distX = Math.max(0, dx - plateauWidth / 2);
                const distY = Math.max(0, dy - plateauDepth / 2);
                const dist = Math.sqrt(distX * distX + distY * distY);
                const maxDist = Math.sqrt((width / 2) ** 2 + (depth / 2) ** 2);
                
                positions[i + 2] = height * (1 - dist / maxDist);
            }
        }
        
        geometry.computeVertexNormals();
        
        const material = new THREE.MeshStandardMaterial({
            color: 0x8B7355,
            roughness: 0.9
        });
        
        const terrain = new THREE.Mesh(geometry, material);
        terrain.rotation.x = -Math.PI / 2;
        terrain.receiveShadow = true;
        
        this.scene.add(terrain);
        this.terrains.push(terrain);
        
        return terrain;
    }
    
    /**
     * 清除
     */
    dispose() {
        for (const terrain of this.terrains) {
            this.scene.remove(terrain);
            terrain.geometry.dispose();
            terrain.material.dispose();
        }
        this.terrains = [];
    }
}

/**
 * 地形编辑器
 */
export class TerrainEditor {
    constructor(scene, camera) {
        this.scene = scene;
        this.camera = camera;
        this.brushSize = 5;
        this.brushStrength = 1;
        this.isEditing = false;
    }
    
    /**
     * 抬高地形
     */
    raiseTerrain(terrain, point, delta) {
        const geometry = terrain.geometry;
        const positions = geometry.attributes.position.array;
        
        // 转换点到局部坐标
        const localPoint = terrain.worldToLocal(point.clone());
        
        for (let i = 0; i < positions.length; i += 3) {
            const x = positions[i];
            const y = positions[i + 1];
            
            // 计算距离
            const dx = x - localPoint.x;
            const dy = y - localPoint.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            // 应用笔刷
            if (distance < this.brushSize) {
                const falloff = Math.cos((distance / this.brushSize) * (Math.PI / 2));
                positions[i + 2] += delta * this.brushStrength * falloff;
            }
        }
        
        geometry.attributes.position.needsUpdate = true;
        geometry.computeVertexNormals();
    }
    
    /**
     * 平滑地形
     */
    smoothTerrain(terrain, point) {
        const geometry = terrain.geometry;
        const positions = geometry.attributes.position.array;
        const normals = geometry.attributes.normal.array;
        
        const localPoint = terrain.worldToLocal(point.clone());
        
        for (let i = 0; i < positions.length; i += 3) {
            const x = positions[i];
            const y = positions[i + 1];
            
            const dx = x - localPoint.x;
            const dy = y - localPoint.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < this.brushSize) {
                // 简单的平滑：取相邻顶点的平均值
                const currentHeight = positions[i + 2];
                positions[i + 2] = currentHeight * 0.8 + this.getAverageHeight(positions, i) * 0.2;
            }
        }
        
        geometry.attributes.position.needsUpdate = true;
        geometry.computeVertexNormals();
    }
    
    /**
     * 获取平均高度
     */
    getAverageHeight(positions, index) {
        let sum = 0;
        let count = 0;
        
        // 简单的 3x3 邻域
        for (let dx = -1; dx <= 1; dx++) {
            for (let dy = -1; dy <= 1; dy++) {
                const i = index + (dx * 3 + dy * positions.length / 3);
                if (i >= 0 && i < positions.length) {
                    sum += positions[i + 2];
                    count++;
                }
            }
        }
        
        return count > 0 ? sum / count : 0;
    }
    
    /**
     * 设置笔刷大小
     */
    setBrushSize(size) {
        this.brushSize = size;
    }
    
    /**
     * 设置笔刷强度
     */
    setBrushStrength(strength) {
        this.brushStrength = strength;
    }
}

/**
 * 建筑系统
 */
export class BuildingSystem {
    constructor(scene) {
        this.scene = scene;
        this.buildings = [];
        this.buildingLibrary = {};
        
        this.initLibrary();
    }
    
    /**
     * 初始化建筑库
     */
    initLibrary() {
        // 房屋
        this.buildingLibrary.house = {
            name: '房屋',
            width: 4,
            height: 3,
            depth: 4,
            color: 0x8B4513
        };
        
        // 高楼
        this.buildingLibrary.tower = {
            name: '高楼',
            width: 3,
            height: 10,
            depth: 3,
            color: 0x808080
        };
        
        // 城堡
        this.buildingLibrary.castle = {
            name: '城堡',
            width: 8,
            height: 6,
            depth: 8,
            color: 0x696969
        };
        
        // 桥梁
        this.buildingLibrary.bridge = {
            name: '桥梁',
            width: 10,
            height: 1,
            depth: 2,
            color: 0x8B4513
        };
    }
    
    /**
     * 创建建筑
     */
    createBuilding(type, position, rotation = null) {
        const config = this.buildingLibrary[type];
        if (!config) return null;
        
        let geometry;
        
        switch (type) {
            case 'house':
                geometry = new THREE.BoxGeometry(config.width, config.height, config.depth);
                break;
            case 'tower':
                geometry = new THREE.CylinderGeometry(config.width / 2, config.width / 2, config.height, 8);
                break;
            case 'castle':
                geometry = new THREE.BoxGeometry(config.width, config.height, config.depth);
                break;
            case 'bridge':
                geometry = new THREE.BoxGeometry(config.width, config.height, config.depth);
                break;
            default:
                geometry = new THREE.BoxGeometry(1, 1, 1);
        }
        
        const material = new THREE.MeshStandardMaterial({
            color: config.color,
            roughness: 0.7
        });
        
        const building = new THREE.Mesh(geometry, material);
        building.position.copy(position);
        
        if (rotation) {
            building.rotation.copy(rotation);
        }
        
        building.castShadow = true;
        building.receiveShadow = true;
        building.name = config.name;
        building.userData.type = 'building';
        building.userData.buildingType = type;
        
        this.scene.add(building);
        this.buildings.push(building);
        
        return building;
    }
    
    /**
     * 放置建筑 (带对齐)
     */
    placeBuilding(type, point, normal) {
        const position = point.clone().add(normal.clone().multiplyScalar(0.1));
        return this.createBuilding(type, position);
    }
    
    /**
     * 获取建筑列表
     */
    getBuildings() {
        return this.buildings;
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

console.log('地形和建筑系统已加载');
