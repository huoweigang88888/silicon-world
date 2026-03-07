/**
 * 流体模拟系统
 * 
 * 简化的水效果
 */

import * as THREE from 'three';

/**
 * 水效果
 */
export class WaterEffect {
    constructor(scene, options = {}) {
        this.scene = scene;
        this.options = {
            width: options.width || 100,
            height: options.height || 100,
            segments: options.segments || 50,
            color: options.color || new THREE.Color(0x006994),
            ...options
        };
        
        this.water = null;
        this.time = 0;
        
        this.init();
    }
    
    /**
     * 初始化水面
     */
    init() {
        const geometry = new THREE.PlaneGeometry(
            this.options.width,
            this.options.height,
            this.options.segments,
            this.options.segments
        );
        
        const material = new THREE.MeshStandardMaterial({
            color: this.options.color,
            transparent: true,
            opacity: 0.8,
            roughness: 0.1,
            metalness: 0.8
        });
        
        this.water = new THREE.Mesh(geometry, material);
        this.water.rotation.x = -Math.PI / 2;
        this.water.receiveShadow = true;
        this.scene.add(this.water);
    }
    
    /**
     * 更新水面
     */
    update(delta) {
        this.time += delta;
        
        const positions = this.water.geometry.attributes.position.array;
        const size = this.options.segments;
        
        for (let i = 0; i < positions.length; i += 3) {
            const x = i / 3 % (size + 1);
            const y = Math.floor(i / 3 / (size + 1));
            
            // 波浪效果
            const wave1 = Math.sin(x * 0.5 + this.time) * 0.5;
            const wave2 = Math.cos(y * 0.3 + this.time * 0.8) * 0.3;
            const wave3 = Math.sin((x + y) * 0.2 + this.time * 1.2) * 0.2;
            
            positions[i + 2] = wave1 + wave2 + wave3;
        }
        
        this.water.geometry.attributes.position.needsUpdate = true;
        this.water.geometry.computeVertexNormals();
    }
    
    /**
     * 清除
     */
    dispose() {
        this.scene.remove(this.water);
        this.water.geometry.dispose();
        this.water.material.dispose();
    }
}

/**
 * 粒子流体
 */
export class ParticleFluid {
    constructor(scene, count = 500) {
        this.scene = scene;
        this.count = count;
        this.particles = null;
        this.velocities = [];
        
        this.init();
    }
    
    /**
     * 初始化
     */
    init() {
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(this.count * 3);
        
        for (let i = 0; i < this.count; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 10;
            positions[i * 3 + 1] = Math.random() * 10;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 10;
            
            this.velocities.push(new THREE.Vector3(0, 0, 0));
        }
        
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        
        const material = new THREE.PointsMaterial({
            color: 0x006994,
            size: 0.2,
            transparent: true,
            opacity: 0.6
        });
        
        this.particles = new THREE.Points(geometry, material);
        this.scene.add(this.particles);
    }
    
    /**
     * 更新流体
     */
    update(delta, gravity = new THREE.Vector3(0, -9.8, 0)) {
        const positions = this.particles.geometry.attributes.position.array;
        
        for (let i = 0; i < this.count; i++) {
            // 应用重力
            this.velocities[i].add(gravity.clone().multiplyScalar(delta));
            
            // 更新位置
            positions[i * 3] += this.velocities[i].x * delta;
            positions[i * 3 + 1] += this.velocities[i].y * delta;
            positions[i * 3 + 2] += this.velocities[i].z * delta;
            
            // 地面碰撞
            if (positions[i * 3 + 1] < 0) {
                positions[i * 3 + 1] = 0;
                this.velocities[i].y *= -0.5; // 弹性碰撞
                this.velocities[i].multiplyScalar(0.9); // 摩擦
            }
            
            // 边界碰撞
            if (Math.abs(positions[i * 3]) > 5) {
                positions[i * 3] = Math.sign(positions[i * 3]) * 5;
                this.velocities[i].x *= -0.5;
            }
            
            if (Math.abs(positions[i * 3 + 2]) > 5) {
                positions[i * 3 + 2] = Math.sign(positions[i * 3 + 2]) * 5;
                this.velocities[i].z *= -0.5;
            }
        }
        
        this.particles.geometry.attributes.position.needsUpdate = true;
    }
    
    /**
     * 清除
     */
    dispose() {
        this.scene.remove(this.particles);
        this.particles.geometry.dispose();
        this.particles.material.dispose();
    }
}

/**
 * 破坏系统
 */
export class DestructionSystem {
    constructor(scene, physicsWorld) {
        this.scene = scene;
        this.physicsWorld = physicsWorld;
        this.debris = [];
    }
    
    /**
     * 破坏物体
     */
    destroyObject(mesh, fragmentCount = 10) {
        const parent = mesh.parent || this.scene;
        const position = mesh.position.clone();
        const geometry = mesh.geometry;
        const material = mesh.material;
        
        // 移除原物体
        this.scene.remove(mesh);
        
        // 创建碎片
        for (let i = 0; i < fragmentCount; i++) {
            const fragmentGeometry = new THREE.BoxGeometry(
                Math.random() * 0.5 + 0.2,
                Math.random() * 0.5 + 0.2,
                Math.random() * 0.5 + 0.2
            );
            const fragment = new THREE.Mesh(fragmentGeometry, material);
            
            fragment.position.copy(position);
            fragment.position.x += (Math.random() - 0.5) * 2;
            fragment.position.y += (Math.random() - 0.5) * 2;
            fragment.position.z += (Math.random() - 0.5) * 2;
            
            fragment.rotation.set(
                Math.random() * Math.PI,
                Math.random() * Math.PI,
                Math.random() * Math.PI
            );
            
            fragment.castShadow = true;
            fragment.receiveShadow = true;
            
            parent.add(fragment);
            
            // 添加物理
            if (this.physicsWorld) {
                const body = this.physicsWorld.addRigidBody(
                    fragment,
                    1,
                    'box',
                    fragment.position
                );
                
                // 添加爆炸力
                body.velocity.set(
                    (Math.random() - 0.5) * 10,
                    Math.random() * 5,
                    (Math.random() - 0.5) * 10
                );
                
                this.debris.push({ fragment, body });
            }
        }
    }
    
    /**
     * 更新碎片
     */
    update(delta) {
        // 碎片由物理系统更新
    }
    
    /**
     * 清除
     */
    dispose() {
        for (const { fragment, body } of this.debris) {
            this.scene.remove(fragment);
            fragment.geometry.dispose();
            fragment.material.dispose();
        }
        this.debris = [];
    }
}

// 使用示例
if (typeof window !== 'undefined') {
    console.log('流体和破坏系统已加载');
    console.log('可用功能:', ['水效果', '粒子流体', '破坏系统']);
}
