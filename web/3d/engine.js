/**
 * 硅基世界 3D 引擎
 * 
 * 基于 Three.js 的 3D 渲染引擎
 */

import * as THREE from 'three';

/**
 * 3D 引擎类
 */
export class Engine3D {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.entities = [];
        this.lights = [];
        this.materials = [];
        this.animations = [];
        
        this.fps = 60;
        this.frameCount = 0;
        this.lastTime = performance.now();
        
        this.init();
    }
    
    /**
     * 初始化引擎
     */
    init() {
        // 创建场景
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x87ceeb);
        this.scene.fog = new THREE.Fog(0x87ceeb, 100, 500);
        
        // 创建相机
        this.camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        this.camera.position.set(0, 10, 20);
        
        // 创建渲染器
        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            antialias: true
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.setPixelRatio(window.devicePixelRatio);
        
        // 添加默认光照
        this.addDefaultLights();
        
        // 添加地面
        this.addGround();
        
        // 窗口大小调整
        window.addEventListener('resize', () => this.onWindowResize(), false);
        
        // 开始渲染循环
        this.animate();
    }
    
    /**
     * 添加默认光照
     */
    addDefaultLights() {
        // 环境光
        const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
        this.scene.add(ambientLight);
        this.lights.push(ambientLight);
        
        // 平行光
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(50, 100, 50);
        directionalLight.castShadow = true;
        directionalLight.shadow.camera.left = -100;
        directionalLight.shadow.camera.right = 100;
        directionalLight.shadow.camera.top = 100;
        directionalLight.shadow.camera.bottom = -100;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        this.scene.add(directionalLight);
        this.lights.push(directionalLight);
    }
    
    /**
     * 添加地面
     */
    addGround() {
        const groundGeometry = new THREE.PlaneGeometry(200, 200);
        const groundMaterial = new THREE.MeshStandardMaterial({ color: 0x228B22 });
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        this.scene.add(ground);
        this.entities.push(ground);
    }
    
    /**
     * 添加实体
     */
    addEntity(entity) {
        this.scene.add(entity);
        this.entities.push(entity);
    }
    
    /**
     * 移除实体
     */
    removeEntity(entity) {
        this.scene.remove(entity);
        const index = this.entities.indexOf(entity);
        if (index > -1) {
            this.entities.splice(index, 1);
        }
    }
    
    /**
     * 创建建筑
     */
    createBuilding(width, height, depth, position, color) {
        const geometry = new THREE.BoxGeometry(width, height, depth);
        const material = new THREE.MeshStandardMaterial({ 
            color: color || new THREE.Color().setHSL(Math.random(), 0.7, 0.5)
        });
        const building = new THREE.Mesh(geometry, material);
        building.position.copy(position);
        building.position.y = height / 2;
        building.castShadow = true;
        building.receiveShadow = true;
        this.addEntity(building);
        return building;
    }
    
    /**
     * 创建角色
     */
    createCharacter(position) {
        const group = new THREE.Group();
        
        // 身体
        const bodyGeometry = new THREE.CylinderGeometry(0.5, 0.5, 2, 16);
        const bodyMaterial = new THREE.MeshStandardMaterial({ color: 0x6200ee });
        const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
        body.castShadow = true;
        group.add(body);
        
        // 头部
        const headGeometry = new THREE.SphereGeometry(0.4, 16, 16);
        const headMaterial = new THREE.MeshStandardMaterial({ color: 0xffd700 });
        const head = new THREE.Mesh(headGeometry, headMaterial);
        head.position.y = 1.2;
        head.castShadow = true;
        group.add(head);
        
        group.position.copy(position);
        this.addEntity(group);
        return group;
    }
    
    /**
     * 创建粒子系统
     */
    createParticleSystem(count, color, position) {
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(count * 3);
        
        for (let i = 0; i < count * 3; i += 3) {
            positions[i] = (Math.random() - 0.5) * 10;
            positions[i + 1] = (Math.random() - 0.5) * 10;
            positions[i + 2] = (Math.random() - 0.5) * 10;
        }
        
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        
        const material = new THREE.PointsMaterial({
            color: color,
            size: 0.1,
            transparent: true,
            opacity: 0.8
        });
        
        const particles = new THREE.Points(geometry, material);
        particles.position.copy(position);
        this.addEntity(particles);
        return particles;
    }
    
    /**
     * 动画循环
     */
    animate() {
        requestAnimationFrame(() => this.animate());
        
        // FPS 计算
        this.frameCount++;
        const currentTime = performance.now();
        if (currentTime - this.lastTime >= 1000) {
            this.fps = this.frameCount;
            this.frameCount = 0;
            this.lastTime = currentTime;
        }
        
        // 更新动画
        this.animations.forEach(anim => anim.update());
        
        // 渲染场景
        this.renderer.render(this.scene, this.camera);
    }
    
    /**
     * 窗口大小调整
     */
    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }
    
    /**
     * 获取 FPS
     */
    getFPS() {
        return this.fps;
    }
    
    /**
     * 获取实体数量
     */
    getEntityCount() {
        return this.entities.length;
    }
    
    /**
     * 清理
     */
    dispose() {
        this.entities.forEach(entity => {
            if (entity.geometry) entity.geometry.dispose();
            if (entity.material) {
                if (Array.isArray(entity.material)) {
                    entity.material.forEach(m => m.dispose());
                } else {
                    entity.material.dispose();
                }
            }
        });
        this.renderer.dispose();
    }
}

/**
 * 动画类
 */
export class Animation {
    constructor(target, properties, duration) {
        this.target = target;
        this.properties = properties;
        this.duration = duration;
        this.elapsed = 0;
        this.startValues = {};
        this.isComplete = false;
        
        // 保存起始值
        for (const key in properties) {
            this.startValues[key] = target[key];
        }
    }
    
    update() {
        if (this.isComplete) return;
        
        this.elapsed += 16; // 约 60fps
        const progress = Math.min(this.elapsed / this.duration, 1);
        
        // 缓动函数 (easeInOutQuad)
        const ease = progress < 0.5
            ? 2 * progress * progress
            : -1 + (4 - 2 * progress) * progress;
        
        // 更新属性
        for (const key in this.properties) {
            const start = this.startValues[key];
            const end = this.properties[key];
            this.target[key] = start + (end - start) * ease;
        }
        
        if (progress >= 1) {
            this.isComplete = true;
        }
    }
}

// 导出便捷函数
export function createScene() {
    return new THREE.Scene();
}

export function createCamera(fov, aspect, near, far) {
    return new THREE.PerspectiveCamera(fov, aspect, near, far);
}

export function createRenderer(options) {
    return new THREE.WebGLRenderer(options);
}

export function createLight(type, color, intensity) {
    switch (type) {
        case 'ambient':
            return new THREE.AmbientLight(color, intensity);
        case 'directional':
            return new THREE.DirectionalLight(color, intensity);
        case 'point':
            return new THREE.PointLight(color, intensity);
        case 'spot':
            return new THREE.SpotLight(color, intensity);
        default:
            return new THREE.AmbientLight(color, intensity);
    }
}

export function createMaterial(type, options) {
    switch (type) {
        case 'basic':
            return new THREE.MeshBasicMaterial(options);
        case 'standard':
            return new THREE.MeshStandardMaterial(options);
        case 'phong':
            return new THREE.MeshPhongMaterial(options);
        case 'lambert':
            return new THREE.MeshLambertMaterial(options);
        default:
            return new THREE.MeshStandardMaterial(options);
    }
}

export function createGeometry(type, params) {
    switch (type) {
        case 'box':
            return new THREE.BoxGeometry(params.width, params.height, params.depth);
        case 'sphere':
            return new THREE.SphereGeometry(params.radius, params.widthSegments, params.heightSegments);
        case 'cylinder':
            return new THREE.CylinderGeometry(params.radiusTop, params.radiusBottom, params.height);
        case 'plane':
            return new THREE.PlaneGeometry(params.width, params.height);
        default:
            return new THREE.BoxGeometry(1, 1, 1);
    }
}
