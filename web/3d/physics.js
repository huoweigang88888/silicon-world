/**
 * 物理系统
 * 
 * 基于 Cannon.js 的物理引擎
 */

import * as THREE from 'three';

/**
 * 物理世界
 */
export class PhysicsWorld {
    constructor() {
        this.gravity = -9.82;
        this.bodies = [];
        this.collisions = [];
        
        this.init();
    }
    
    /**
     * 初始化物理世界
     */
    init() {
        // 如果使用 Cannon.js
        if (typeof CANNON !== 'undefined') {
            this.world = new CANNON.World();
            this.world.gravity.set(0, this.gravity, 0);
            this.world.broadphase = new CANNON.NaiveBroadphase();
            this.world.solver.iterations = 10;
        } else {
            // 简化物理实现
            this.world = null;
        }
    }
    
    /**
     * 添加刚体
     */
    addRigidBody(mesh, mass, shape = 'box') {
        if (this.world) {
            // Cannon.js 实现
            let shape;
            if (shape === 'box') {
                shape = new CANNON.Box(new CANNON.Vec3(1, 1, 1));
            } else if (shape === 'sphere') {
                shape = new CANNON.Sphere(1);
            }
            
            const body = new CANNON.Body({
                mass: mass,
                position: new CANNON.Vec3(
                    mesh.position.x,
                    mesh.position.y,
                    mesh.position.z
                ),
                shape: shape
            });
            
            this.world.addBody(body);
            this.bodies.push({ mesh, body });
        } else {
            // 简化实现
            this.bodies.push({
                mesh,
                mass,
                velocity: new THREE.Vector3(),
                position: mesh.position.clone()
            });
        }
    }
    
    /**
     * 更新物理
     */
    update(delta) {
        if (this.world) {
            this.world.step(1 / 60, delta, 3);
            
            // 同步网格和刚体
            for (const { mesh, body } of this.bodies) {
                mesh.position.copy(body.position);
                mesh.quaternion.copy(body.quaternion);
            }
        } else {
            // 简化物理更新
            for (const body of this.bodies) {
                if (body.mass > 0) {
                    // 应用重力
                    body.velocity.y += this.gravity * delta;
                    
                    // 更新位置
                    body.position.add(body.velocity.clone().multiplyScalar(delta));
                    
                    // 地面碰撞
                    if (body.position.y < 0) {
                        body.position.y = 0;
                        body.velocity.y = 0;
                    }
                    
                    // 同步网格
                    body.mesh.position.copy(body.position);
                }
            }
        }
    }
    
    /**
     * 射线检测
     */
    raycast(from, to) {
        // 简化射线检测
        const direction = new THREE.Vector3().subVectors(to, from);
        const distance = direction.length();
        direction.normalize();
        
        const raycaster = new THREE.Raycaster(from, direction);
        
        const intersects = raycaster.intersectObjects(
            this.bodies.map(b => b.mesh)
        );
        
        if (intersects.length > 0 && intersects[0].distance <= distance) {
            return {
                hit: true,
                point: intersects[0].point,
                object: intersects[0].object,
                distance: intersects[0].distance
            };
        }
        
        return { hit: false };
    }
    
    /**
     * 碰撞检测
     */
    checkCollision(mesh1, mesh2) {
        const box1 = new THREE.Box3().setFromObject(mesh1);
        const box2 = new THREE.Box3().setFromObject(mesh2);
        
        return box1.intersectsBox(box2);
    }
    
    /**
     * 清除
     */
    dispose() {
        this.bodies = [];
        if (this.world) {
            this.world.bodies = [];
        }
    }
}

/**
 * 碰撞体
 */
export class Collider {
    constructor(mesh, type = 'box') {
        this.mesh = mesh;
        this.type = type;
        this.size = new THREE.Vector3(1, 1, 1);
        this.radius = 1;
        this.isTrigger = false;
        
        this.updateSize();
    }
    
    /**
     * 更新碰撞体大小
     */
    updateSize() {
        if (this.type === 'box') {
            const box = new THREE.Box3().setFromObject(this.mesh);
            this.size.subVectors(box.max, box.min);
        } else if (this.type === 'sphere') {
            const box = new THREE.Box3().setFromObject(this.mesh);
            this.radius = box.getSize(new THREE.Vector3()).length() / 2;
        }
    }
    
    /**
     * 检查碰撞
     */
    intersects(other) {
        if (this.type === 'box' && other.type === 'box') {
            return this.boxIntersects(other);
        } else if (this.type === 'sphere' && other.type === 'sphere') {
            return this.sphereIntersects(other);
        }
        return false;
    }
    
    /**
     * 盒形碰撞检测
     */
    boxIntersects(other) {
        const box1 = new THREE.Box3().setFromObject(this.mesh);
        const box2 = new THREE.Box3().setFromObject(other.mesh);
        
        return box1.intersectsBox(box2);
    }
    
    /**
     * 球形碰撞检测
     */
    sphereIntersects(other) {
        const distance = this.mesh.position.distanceTo(other.mesh.position);
        return distance < (this.radius + other.radius);
    }
}

/**
 * 物理材质
 */
export class PhysicsMaterial {
    constructor(options = {}) {
        this.friction = options.friction || 0.5;
        this.restitution = options.restitution || 0.3;
        this.density = options.density || 1.0;
    }
}

/**
 * 物理助手
 */
export class PhysicsHelper {
    /**
     * 创建物理可视化
     */
    static createWireframe(mesh, color = 0xff0000) {
        const helper = new THREE.BoxHelper(mesh, color);
        return helper;
    }
    
    /**
     * 创建刚体可视化
     */
    static createRigidBodyVisualizer(body, type = 'box') {
        let geometry;
        if (type === 'box') {
            geometry = new THREE.BoxGeometry(1, 1, 1);
        } else if (type === 'sphere') {
            geometry = new THREE.SphereGeometry(1, 16, 16);
        }
        
        const material = new THREE.MeshBasicMaterial({
            color: 0x00ff00,
            wireframe: true,
            transparent: true,
            opacity: 0.5
        });
        
        return new THREE.Mesh(geometry, material);
    }
}

// 使用示例
if (typeof window !== 'undefined') {
    console.log('物理系统已加载');
    
    // 创建物理世界
    const physics = new PhysicsWorld();
    
    // 添加刚体
    const mesh = new THREE.Mesh(
        new THREE.BoxGeometry(1, 1, 1),
        new THREE.MeshStandardMaterial({ color: 0xff0000 })
    );
    physics.addRigidBody(mesh, 1, 'box');
    
    console.log('物理系统就绪');
}
