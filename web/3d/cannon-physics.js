/**
 * Cannon.js 物理引擎集成
 * 
 * 完整的 3D 物理模拟
 */

import * as THREE from 'three';

// 动态导入 Cannon.js
const CANNON = await import('https://cdn.skypack.dev/cannon-es@0.20.0');

/**
 * Cannon 物理世界
 */
export class CannonPhysicsWorld {
    constructor(options = {}) {
        this.world = new CANNON.World();
        this.world.gravity.set(0, options.gravity || -9.82, 0);
        this.world.broadphase = new CANNON.SAPBroadphase(this.world);
        this.world.solver.iterations = options.iterations || 10;
        this.world.allowSleep = true;
        
        this.bodies = [];
        this.meshes = [];
        this.constraints = [];
        
        this.initMaterials();
    }
    
    /**
     * 初始化物理材质
     */
    initMaterials() {
        // 地面材质
        this.groundMaterial = new CANNON.Material('groundMaterial');
        
        // 物体材质
        this.objectMaterial = new CANNON.Material('objectMaterial');
        
        // 定义材质间的作用
        const groundObjectContact = new CANNON.ContactMaterial(
            this.groundMaterial,
            this.objectMaterial,
            {
                friction: 0.5,
                restitution: 0.3
            }
        );
        
        this.world.addContactMaterial(groundObjectContact);
    }
    
    /**
     * 添加刚体
     */
    addRigidBody(mesh, mass, shape = 'box', position = null) {
        let shape;
        const size = new THREE.Vector3();
        mesh.geometry.computeBoundingBox();
        mesh.geometry.boundingBox.getSize(size);
        
        switch (shape) {
            case 'box':
                shape = new CANNON.Box(new CANNON.Vec3(size.x / 2, size.y / 2, size.z / 2));
                break;
            case 'sphere':
                shape = new CANNON.Sphere(Math.max(size.x, size.y, size.z) / 2);
                break;
            case 'cylinder':
                shape = new CANNON.Cylinder(size.x / 2, size.x / 2, size.y, 8);
                break;
        }
        
        const body = new CANNON.Body({
            mass: mass,
            material: mass > 0 ? this.objectMaterial : this.groundMaterial,
            shape: shape
        });
        
        if (position) {
            body.position.set(position.x, position.y, position.z);
        } else {
            body.position.set(mesh.position.x, mesh.position.y, mesh.position.z);
        }
        
        this.world.addBody(body);
        this.bodies.push(body);
        this.meshes.push(mesh);
        
        // 绑定 mesh 和 body
        mesh.userData.physicsBody = body;
        
        return body;
    }
    
    /**
     * 添加地面
     */
    addGround(size = 100) {
        const groundGeometry = new THREE.PlaneGeometry(size, size);
        const groundMaterial = new THREE.MeshStandardMaterial({ 
            color: 0x228B22,
            side: THREE.DoubleSide
        });
        const groundMesh = new THREE.Mesh(groundGeometry, groundMaterial);
        groundMesh.rotation.x = -Math.PI / 2;
        groundMesh.receiveShadow = true;
        
        const groundShape = new CANNON.Box(new CANNON.Vec3(size / 2, size / 2, 0.1));
        const groundBody = new CANNON.Body({
            mass: 0, // 静态物体
            material: this.groundMaterial
        });
        groundBody.addShape(groundShape);
        groundBody.quaternion.setFromAxisAngle(new CANNON.Vec3(1, 0, 0), -Math.PI / 2);
        
        this.world.addBody(groundBody);
        this.bodies.push(groundBody);
        this.meshes.push(groundMesh);
        
        return groundMesh;
    }
    
    /**
     * 更新物理
     */
    update(delta) {
        this.world.step(1 / 60, delta, 3);
        
        // 同步 mesh 和 body
        for (let i = 0; i < this.bodies.length; i++) {
            const body = this.bodies[i];
            const mesh = this.meshes[i];
            
            if (body && mesh) {
                mesh.position.copy(body.position);
                mesh.quaternion.copy(body.quaternion);
            }
        }
    }
    
    /**
     * 射线检测
     */
    raycast(from, to) {
        const fromVec = new CANNON.Vec3(from.x, from.y, from.z);
        const toVec = new CANNON.Vec3(to.x, to.y, to.z);
        
        const ray = new CANNON.Ray(fromVec, toVec);
        const result = new CANNON.RaycastResult();
        
        ray.intersectWorld(this.world, {
            mode: CANNON.Ray.CLOSEST,
            result: result
        });
        
        if (result.hasHit) {
            return {
                hit: true,
                point: new THREE.Vector3(result.hitPointWorld.x, result.hitPointWorld.y, result.hitPointWorld.z),
                body: result.body,
                distance: from.distanceTo(new THREE.Vector3(result.hitPointWorld.x, result.hitPointWorld.y, result.hitPointWorld.z))
            };
        }
        
        return { hit: false };
    }
    
    /**
     * 添加约束
     */
    addConstraint(bodyA, bodyB, pivotA = null, pivotB = null) {
        const pivotAVec = pivotA ? new CANNON.Vec3(pivotA.x, pivotA.y, pivotA.z) : new CANNON.Vec3(0, 0, 0);
        const pivotBVec = pivotB ? new CANNON.Vec3(pivotB.x, pivotB.y, pivotB.z) : new CANNON.Vec3(0, 0, 0);
        
        const constraint = new CANNON.PointToPointConstraint(
            bodyA, pivotAVec,
            bodyB, pivotBVec
        );
        
        this.world.addConstraint(constraint);
        this.constraints.push(constraint);
        
        return constraint;
    }
    
    /**
     * 添加铰链约束
     */
    addHingeConstraint(bodyA, bodyB, axis = new THREE.Vector3(0, 1, 0)) {
        const axisVec = new CANNON.Vec3(axis.x, axis.y, axis.z);
        
        const constraint = new CANNON.HingeConstraint(bodyA, bodyB, {
            pivotA: new CANNON.Vec3(0, 0, 0),
            axisA: axisVec,
            pivotB: new CANNON.Vec3(0, 0, 0),
            axisB: axisVec
        });
        
        this.world.addConstraint(constraint);
        this.constraints.push(constraint);
        
        return constraint;
    }
    
    /**
     * 清除
     */
    dispose() {
        this.bodies.forEach(body => this.world.removeBody(body));
        this.constraints.forEach(constraint => this.world.removeConstraint(constraint));
        this.bodies = [];
        this.meshes = [];
        this.constraints = [];
    }
}

/**
 * 车辆物理
 */
export class VehiclePhysics {
    constructor(physicsWorld) {
        this.physicsWorld = physicsWorld;
        this.vehicles = [];
    }
    
    /**
     * 创建车辆
     */
    createVehicle(position, chassisMesh) {
        // 车身
        const chassisShape = new CANNON.Box(new CANNON.Vec3(1, 0.5, 2));
        const chassisBody = new CANNON.Body({ mass: 150 });
        chassisBody.addShape(chassisShape);
        chassisBody.position.set(position.x, position.y, position.z);
        chassisBody.angularVelocity.set(0, 0, 0);
        
        this.physicsWorld.world.addBody(chassisBody);
        
        // 创建车辆
        const vehicle = new CANNON.RaycastVehicle({
            chassisBody: chassisBody
        });
        
        // 添加车轮
        const wheelOptions = {
            radius: 0.5,
            directionLocal: new CANNON.Vec3(0, -1, 0),
            suspensionStiffness: 30,
            suspensionRestLength: 0.3,
            frictionSlip: 1.4,
            dampingRelaxation: 2.3,
            dampingCompression: 4.4,
            maxSuspensionForce: 100000,
            rollInfluence: 0.01,
            axleLocal: new CANNON.Vec3(1, 0, 0),
            chassisConnectionPointLocal: new CANNON.Vec3(0, 0, 0),
            maxSuspensionTravel: 0.3,
            customSlidingRotationalSpeed: -30,
            useCustomSlidingRotationalSpeed: true
        };
        
        // 前左轮
        wheelOptions.chassisConnectionPointLocal.set(1, -0.5, 1.2);
        vehicle.addWheel(wheelOptions);
        
        // 前右轮
        wheelOptions.chassisConnectionPointLocal.set(-1, -0.5, 1.2);
        vehicle.addWheel(wheelOptions);
        
        // 后左轮
        wheelOptions.chassisConnectionPointLocal.set(1, -0.5, -1.2);
        vehicle.addWheel(wheelOptions);
        
        // 后右轮
        wheelOptions.chassisConnectionPointLocal.set(-1, -0.5, -1.2);
        vehicle.addWheel(wheelOptions);
        
        vehicle.addToWorld(this.physicsWorld.world);
        
        // 创建车轮网格
        const wheelBodies = [];
        const wheelMeshes = [];
        
        vehicle.wheelInfos.forEach((wheel) => {
            const wheelGeometry = new THREE.CylinderGeometry(wheel.radius, wheel.radius, wheel.radius / 2, 20);
            wheelGeometry.rotateZ(Math.PI / 2);
            const wheelMaterial = new THREE.MeshStandardMaterial({ color: 0x333333 });
            const wheelMesh = new THREE.Mesh(wheelGeometry, wheelMaterial);
            wheelMesh.castShadow = true;
            
            this.physicsWorld.meshes.push(wheelMesh);
            wheelBodies.push(null); // 车轮由 RaycastVehicle 管理
            wheelMeshes.push(wheelMesh);
        });
        
        this.vehicles.push({
            vehicle,
            chassisBody,
            chassisMesh,
            wheelMeshes
        });
        
        return { vehicle, chassisBody };
    }
    
    /**
     * 更新车辆
     */
    update(delta) {
        for (const { vehicle, chassisMesh, wheelMeshes } of this.vehicles) {
            // 更新车身
            chassisMesh.position.copy(vehicle.chassisBody.position);
            chassisMesh.quaternion.copy(vehicle.chassisBody.quaternion);
            
            // 更新车轮
            for (let i = 0; i < vehicle.wheelInfos.length; i++) {
                vehicle.updateWheelTransform(i);
                const t = vehicle.wheelInfos[i].worldTransform;
                wheelMeshes[i].position.copy(t.position);
                wheelMeshes[i].quaternion.copy(t.quaternion);
            }
        }
    }
    
    /**
     * 控制车辆
     */
    controlVehicle(vehicleIndex, engineForce, steering) {
        const vehicle = this.vehicles[vehicleIndex].vehicle;
        
        // 引擎力 (后轮驱动)
        vehicle.applyEngineForce(-engineForce, 2);
        vehicle.applyEngineForce(-engineForce, 3);
        
        // 转向 (前轮)
        vehicle.setSteeringValue(steering, 0);
        vehicle.setSteeringValue(steering, 1);
    }
    
    /**
     * 清除
     */
    dispose() {
        for (const { vehicle } of this.vehicles) {
            vehicle.removeFromWorld(this.physicsWorld.world);
        }
        this.vehicles = [];
    }
}

/**
 * 物理助手
 */
export class PhysicsHelper {
    /**
     * 创建物理可视化
     */
    static createBodyVisualizer(body, color = 0x00ff00) {
        const helper = new CANNON.Body(body.mass);
        
        // 添加形状可视化
        for (const shape of body.shapes) {
            if (shape instanceof CANNON.Box) {
                const geometry = new THREE.BoxGeometry(
                    shape.halfExtents.x * 2,
                    shape.halfExtents.y * 2,
                    shape.halfExtents.z * 2
                );
                const material = new THREE.MeshBasicMaterial({
                    color: color,
                    wireframe: true
                });
                return new THREE.Mesh(geometry, material);
            } else if (shape instanceof CANNON.Sphere) {
                const geometry = new THREE.SphereGeometry(shape.radius, 16, 16);
                const material = new THREE.MeshBasicMaterial({
                    color: color,
                    wireframe: true
                });
                return new THREE.Mesh(geometry, material);
            }
        }
        
        return null;
    }
    
    /**
     * 创建碰撞调试器
     */
    static createContactDebugger(world) {
        const contacts = [];
        
        world.addEventListener('postStep', () => {
            for (const contact of world.contacts) {
                contacts.push({
                    bodyA: contact.bi,
                    bodyB: contact.bj,
                    point: contact.rj
                });
            }
        });
        
        return contacts;
    }
}

// 使用示例
if (typeof window !== 'undefined') {
    console.log('Cannon.js 物理引擎已加载');
    console.log('CANNON 版本:', CANNON.version);
}
