/**
 * 软体物理系统
 * 
 * 布料、绳索、弹簧模拟
 */

import * as THREE from 'three';

/**
 * 布料模拟器
 */
export class ClothSimulation {
    constructor(scene, physicsWorld) {
        this.scene = scene;
        this.physicsWorld = physicsWorld;
        this.cloths = [];
    }
    
    /**
     * 创建布料
     */
    createCloth(width, height, segments, position, mass = 1) {
        const particles = [];
        const constraints = [];
        
        // 创建粒子网格
        for (let y = 0; y <= height; y++) {
            particles[y] = [];
            for (let x = 0; x <= width; x++) {
                const px = position.x + (x / width) * 2;
                const py = position.y - (y / height) * 2;
                const pz = position.z;
                
                // 创建粒子
                const particle = {
                    position: new THREE.Vector3(px, py, pz),
                    previous: new THREE.Vector3(px, py, pz),
                    mass: mass,
                    pinned: y === 0 // 顶部固定
                };
                
                particles[y][x] = particle;
                
                // 水平约束
                if (x > 0) {
                    constraints.push({
                        p1: particles[y][x - 1],
                        p2: particle,
                        restLength: 2 / width
                    });
                }
                
                // 垂直约束
                if (y > 0) {
                    constraints.push({
                        p1: particles[y - 1][x],
                        p2: particle,
                        restLength: 2 / height
                    });
                }
                
                // 对角约束 (增加稳定性)
                if (x > 0 && y > 0) {
                    constraints.push({
                        p1: particles[y - 1][x - 1],
                        p2: particle,
                        restLength: Math.sqrt(2) * 2 / Math.max(width, height)
                    });
                }
            }
        }
        
        // 创建网格
        const geometry = new THREE.PlaneGeometry(2, 2, width, height);
        const material = new THREE.MeshStandardMaterial({
            color: 0x6200ee,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.9
        });
        const mesh = new THREE.Mesh(geometry, material);
        mesh.castShadow = true;
        this.scene.add(mesh);
        
        const cloth = {
            particles,
            constraints,
            mesh,
            gravity: new THREE.Vector3(0, -9.8, 0),
            damping: 0.99,
            stiffness: 1.0
        };
        
        this.cloths.push(cloth);
        return cloth;
    }
    
    /**
     * 更新布料
     */
    update(delta, iterations = 5) {
        for (const cloth of this.cloths) {
            // 更新粒子位置 (Verlet 积分)
            for (const row of cloth.particles) {
                for (const particle of row) {
                    if (particle.pinned) continue;
                    
                    const velocity = particle.position.clone().sub(particle.previous);
                    velocity.multiplyScalar(cloth.damping);
                    
                    particle.previous.copy(particle.position);
                    particle.position.add(velocity);
                    particle.position.add(cloth.gravity.clone().multiplyScalar(delta * delta));
                }
            }
            
            // 满足约束
            for (let i = 0; i < iterations; i++) {
                for (const constraint of cloth.constraints) {
                    const delta = constraint.p2.position.clone().sub(constraint.p1.position);
                    const distance = delta.length();
                    const difference = distance - constraint.restLength;
                    
                    if (distance > 0) {
                        const correction = delta.normalize().multiplyScalar(difference * 0.5 * cloth.stiffness);
                        
                        if (!constraint.p1.pinned) {
                            constraint.p1.position.add(correction);
                        }
                        if (!constraint.p2.pinned) {
                            constraint.p2.position.sub(correction);
                        }
                    }
                }
            }
            
            // 更新网格顶点
            const positions = cloth.mesh.geometry.attributes.position.array;
            let index = 0;
            
            for (let y = 0; y < cloth.particles.length; y++) {
                for (let x = 0; x < cloth.particles[y].length; x++) {
                    const particle = cloth.particles[y][x];
                    positions[index * 3] = particle.position.x;
                    positions[index * 3 + 1] = particle.position.y;
                    positions[index * 3 + 2] = particle.position.z;
                    index++;
                }
            }
            
            cloth.mesh.geometry.attributes.position.needsUpdate = true;
            cloth.mesh.geometry.computeVertexNormals();
        }
    }
    
    /**
     * 添加风力
     */
    addWind(cloth, force, direction = new THREE.Vector3(1, 0, 0)) {
        for (const row of cloth.particles) {
            for (const particle of row) {
                if (!particle.pinned) {
                    particle.position.add(direction.clone().multiplyScalar(force * 0.01));
                }
            }
        }
    }
    
    /**
     * 清除
     */
    dispose() {
        for (const cloth of this.cloths) {
            this.scene.remove(cloth.mesh);
            cloth.mesh.geometry.dispose();
            cloth.mesh.material.dispose();
        }
        this.cloths = [];
    }
}

/**
 * 绳索系统
 */
export class RopeSimulation {
    constructor(scene) {
        this.scene = scene;
        this.ropes = [];
    }
    
    /**
     * 创建绳索
     */
    createRope(start, end, segments = 10, mass = 0.5) {
        const particles = [];
        const segmentLength = start.distanceTo(end) / segments;
        
        // 创建粒子
        for (let i = 0; i <= segments; i++) {
            const t = i / segments;
            const position = start.clone().lerp(end, t);
            
            particles.push({
                position: position.clone(),
                previous: position.clone(),
                mass: mass,
                pinned: i === 0 || i === segments
            });
        }
        
        // 创建约束
        const constraints = [];
        for (let i = 0; i < segments; i++) {
            constraints.push({
                p1: particles[i],
                p2: particles[i + 1],
                restLength: segmentLength
            });
        }
        
        // 创建线网格
        const geometry = new THREE.BufferGeometry().setFromPoints(particles.map(p => p.position));
        const material = new THREE.LineBasicMaterial({ color: 0x888888 });
        const line = new THREE.Line(geometry, material);
        this.scene.add(line);
        
        const rope = {
            particles,
            constraints,
            line,
            gravity: new THREE.Vector3(0, -9.8, 0),
            damping: 0.99
        };
        
        this.ropes.push(rope);
        return rope;
    }
    
    /**
     * 更新绳索
     */
    update(delta, iterations = 3) {
        for (const rope of this.ropes) {
            // 更新粒子
            for (const particle of rope.particles) {
                if (particle.pinned) continue;
                
                const velocity = particle.position.clone().sub(particle.previous);
                velocity.multiplyScalar(rope.damping);
                
                particle.previous.copy(particle.position);
                particle.position.add(velocity);
                particle.position.add(rope.gravity.clone().multiplyScalar(delta * delta));
            }
            
            // 满足约束
            for (let i = 0; i < iterations; i++) {
                for (const constraint of rope.constraints) {
                    const delta = constraint.p2.position.clone().sub(constraint.p1.position);
                    const distance = delta.length();
                    const difference = distance - constraint.restLength;
                    
                    if (distance > 0) {
                        const correction = delta.normalize().multiplyScalar(difference * 0.5);
                        
                        if (!constraint.p1.pinned) {
                            constraint.p1.position.add(correction);
                        }
                        if (!constraint.p2.pinned) {
                            constraint.p2.position.sub(correction);
                        }
                    }
                }
            }
            
            // 更新线
            const positions = rope.line.geometry.attributes.position.array;
            for (let i = 0; i < rope.particles.length; i++) {
                positions[i * 3] = rope.particles[i].position.x;
                positions[i * 3 + 1] = rope.particles[i].position.y;
                positions[i * 3 + 2] = rope.particles[i].position.z;
            }
            rope.line.geometry.attributes.position.needsUpdate = true;
        }
    }
    
    /**
     * 清除
     */
    dispose() {
        for (const rope of this.ropes) {
            this.scene.remove(rope.line);
            rope.line.geometry.dispose();
            rope.line.material.dispose();
        }
        this.ropes = [];
    }
}

/**
 * 弹簧系统
 */
export class SpringSystem {
    constructor(scene) {
        this.scene = scene;
        this.springs = [];
    }
    
    /**
     * 创建弹簧
     */
    createSpring(start, end, stiffness = 10, damping = 0.5, restLength = null) {
        const spring = {
            start: start.clone(),
            end: end.clone(),
            stiffness: stiffness,
            damping: damping,
            restLength: restLength || start.distanceTo(end),
            velocity: new THREE.Vector3()
        };
        
        // 创建弹簧网格
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(6);
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        
        const material = new THREE.LineBasicMaterial({ color: 0xff0000 });
        const line = new THREE.Line(geometry, material);
        this.scene.add(line);
        
        spring.line = line;
        this.springs.push(spring);
        
        return spring;
    }
    
    /**
     * 更新弹簧
     */
    update(delta) {
        for (const spring of this.springs) {
            // 计算弹簧力 (胡克定律)
            const displacement = spring.end.clone().sub(spring.start);
            const distance = displacement.length();
            const force = displacement.normalize().multiplyScalar(
                -spring.stiffness * (distance - spring.restLength)
            );
            
            // 应用阻尼
            force.multiplyScalar(1 - spring.damping);
            
            // 更新端点
            spring.end.add(force.clone().multiplyScalar(delta));
            
            // 更新网格
            const positions = spring.line.geometry.attributes.position.array;
            positions[0] = spring.start.x;
            positions[1] = spring.start.y;
            positions[2] = spring.start.z;
            positions[3] = spring.end.x;
            positions[4] = spring.end.y;
            positions[5] = spring.end.z;
            spring.line.geometry.attributes.position.needsUpdate = true;
        }
    }
    
    /**
     * 清除
     */
    dispose() {
        for (const spring of this.springs) {
            this.scene.remove(spring.line);
            spring.line.geometry.dispose();
            spring.line.material.dispose();
        }
        this.springs = [];
    }
}

// 使用示例
if (typeof window !== 'undefined') {
    console.log('软体物理系统已加载');
    console.log('可用功能:', ['布料', '绳索', '弹簧']);
}
