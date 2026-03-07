/**
 * 特效和后处理系统
 * 
 * 粒子、天气、光影效果
 */

import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/examples/jsm/postprocessing/ShaderPass.js';

/**
 * 粒子系统
 */
export class ParticleSystem {
    constructor(scene) {
        this.scene = scene;
        this.particles = [];
        this.clock = new THREE.Clock();
    }
    
    /**
     * 创建粒子发射器
     */
    createEmitter(options = {}) {
        const config = {
            position: options.position || new THREE.Vector3(0, 0, 0),
            direction: options.direction || new THREE.Vector3(0, 1, 0),
            spread: options.spread || 0.5,
            count: options.count || 100,
            speed: options.speed || 1,
            size: options.size || 0.1,
            color: options.color || 0xffffff,
            lifetime: options.lifetime || 2,
            gravity: options.gravity || 0,
            ...options
        };
        
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(config.count * 3);
        const velocities = [];
        const ages = [];
        
        for (let i = 0; i < config.count; i++) {
            positions[i * 3] = config.position.x;
            positions[i * 3 + 1] = config.position.y;
            positions[i * 3 + 2] = config.position.z;
            
            // 随机速度
            const velocity = config.direction.clone();
            velocity.x += (Math.random() - 0.5) * config.spread;
            velocity.y += (Math.random() - 0.5) * config.spread;
            velocity.z += (Math.random() - 0.5) * config.spread;
            velocity.normalize().multiplyScalar(config.speed);
            velocities.push(velocity);
            
            ages.push(Math.random() * config.lifetime);
        }
        
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        
        const material = new THREE.PointsMaterial({
            color: config.color,
            size: config.size,
            transparent: true,
            opacity: 0.8,
            blending: THREE.AdditiveBlending
        });
        
        const particleSystem = new THREE.Points(geometry, material);
        particleSystem.userData = {
            velocities,
            ages,
            config
        };
        
        this.scene.add(particleSystem);
        this.particles.push(particleSystem);
        
        return particleSystem;
    }
    
    /**
     * 更新粒子
     */
    update(delta) {
        for (const system of this.particles) {
            const positions = system.geometry.attributes.position.array;
            const velocities = system.userData.velocities;
            const ages = system.userData.ages;
            const config = system.userData.config;
            
            for (let i = 0; i < config.count; i++) {
                ages[i] += delta;
                
                if (ages[i] >= config.lifetime) {
                    // 重置粒子
                    ages[i] = 0;
                    positions[i * 3] = config.position.x;
                    positions[i * 3 + 1] = config.position.y;
                    positions[i * 3 + 2] = config.position.z;
                } else {
                    // 更新位置
                    positions[i * 3] += velocities[i].x * delta;
                    positions[i * 3 + 1] += velocities[i].y * delta;
                    positions[i * 3 + 2] += velocities[i].z * delta;
                    
                    // 应用重力
                    velocities[i].y += config.gravity * delta;
                }
            }
            
            system.geometry.attributes.position.needsUpdate = true;
            
            // 淡出效果
            const alpha = 1 - (ages[0] / config.lifetime);
            system.material.opacity = alpha * 0.8;
        }
    }
    
    /**
     * 创建火焰效果
     */
    createFire(position) {
        return this.createEmitter({
            position,
            direction: new THREE.Vector3(0, 1, 0),
            spread: 0.3,
            count: 50,
            speed: 2,
            size: 0.2,
            color: 0xff4400,
            lifetime: 1,
            gravity: -0.5
        });
    }
    
    /**
     * 创建烟雾效果
     */
    createSmoke(position) {
        return this.createEmitter({
            position,
            direction: new THREE.Vector3(0, 0.5, 0),
            spread: 0.5,
            count: 30,
            speed: 1,
            size: 0.3,
            color: 0x888888,
            lifetime: 3,
            gravity: -0.2
        });
    }
    
    /**
     * 创建魔法效果
     */
    createMagic(position, color = 0x00ffff) {
        return this.createEmitter({
            position,
            direction: new THREE.Vector3(0, 0, 0),
            spread: 1,
            count: 20,
            speed: 0.5,
            size: 0.1,
            color: color,
            lifetime: 2,
            gravity: 0
        });
    }
    
    /**
     * 清除
     */
    dispose() {
        for (const system of this.particles) {
            this.scene.remove(system);
            system.geometry.dispose();
            system.material.dispose();
        }
        this.particles = [];
    }
}

/**
 * 天气系统
 */
export class WeatherSystem {
    constructor(scene, camera) {
        this.scene = scene;
        this.camera = camera;
        this.currentWeather = 'clear';
        this.rain = null;
        this.snow = null;
        this.fog = null;
    }
    
    /**
     * 设置天气
     */
    setWeather(type, intensity = 1) {
        this.clearWeather();
        
        switch (type) {
            case 'rain':
                this.createRain(intensity);
                break;
            case 'snow':
                this.createSnow(intensity);
                break;
            case 'fog':
                this.createFog(intensity);
                break;
        }
        
        this.currentWeather = type;
    }
    
    /**
     * 创建雨
     */
    createRain(intensity) {
        const count = 1000 * intensity;
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(count * 3);
        
        for (let i = 0; i < count; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 100;
            positions[i * 3 + 1] = Math.random() * 50;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 100;
        }
        
        const material = new THREE.PointsMaterial({
            color: 0xaaaaaa,
            size: 0.1,
            transparent: true
        });
        
        this.rain = new THREE.Points(geometry, material);
        this.scene.add(this.rain);
    }
    
    /**
     * 创建雪
     */
    createSnow(intensity) {
        const count = 500 * intensity;
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(count * 3);
        
        for (let i = 0; i < count; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 100;
            positions[i * 3 + 1] = Math.random() * 50;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 100;
        }
        
        const material = new THREE.PointsMaterial({
            color: 0xffffff,
            size: 0.2,
            transparent: true
        });
        
        this.snow = new THREE.Points(geometry, material);
        this.scene.add(this.snow);
    }
    
    /**
     * 创建雾
     */
    createFog(intensity) {
        this.scene.fog = new THREE.FogExp2(0x888888, 0.02 * intensity);
        this.fog = this.scene.fog;
    }
    
    /**
     * 清除天气
     */
    clearWeather() {
        if (this.rain) {
            this.scene.remove(this.rain);
            this.rain.geometry.dispose();
            this.rain.material.dispose();
            this.rain = null;
        }
        
        if (this.snow) {
            this.scene.remove(this.snow);
            this.snow.geometry.dispose();
            this.snow.material.dispose();
            this.snow = null;
        }
        
        if (this.fog) {
            this.scene.fog = null;
            this.fog = null;
        }
        
        this.currentWeather = 'clear';
    }
    
    /**
     * 更新天气
     */
    update(delta) {
        if (this.rain) {
            const positions = this.rain.geometry.attributes.position.array;
            for (let i = 0; i < positions.length / 3; i++) {
                positions[i * 3 + 1] -= 0.5;
                if (positions[i * 3 + 1] < 0) {
                    positions[i * 3 + 1] = 50;
                }
            }
            this.rain.geometry.attributes.position.needsUpdate = true;
        }
        
        if (this.snow) {
            const positions = this.snow.geometry.attributes.position.array;
            for (let i = 0; i < positions.length / 3; i++) {
                positions[i * 3 + 1] -= 0.1;
                positions[i * 3] += Math.sin(Date.now() * 0.001 + i) * 0.01;
                if (positions[i * 3 + 1] < 0) {
                    positions[i * 3 + 1] = 50;
                }
            }
            this.snow.geometry.attributes.position.needsUpdate = true;
        }
    }
}

/**
 * 后处理管理器
 */
export class PostProcessingManager {
    constructor(renderer, scene, camera) {
        this.renderer = renderer;
        this.scene = scene;
        this.camera = camera;
        this.composer = null;
        this.passes = {};
        
        this.init();
    }
    
    /**
     * 初始化
     */
    init() {
        this.composer = new EffectComposer(this.renderer);
        
        const renderPass = new RenderPass(this.scene, this.camera);
        this.composer.addPass(renderPass);
    }
    
    /**
     * 添加 Bloom 效果
     */
    addBloom(strength = 1.5, radius = 0.4, threshold = 0.85) {
        const bloomPass = new UnrealBloomPass(
            new THREE.Vector2(window.innerWidth, window.innerHeight),
            strength,
            radius,
            threshold
        );
        
        this.composer.addPass(bloomPass);
        this.passes.bloom = bloomPass;
    }
    
    /**
     * 移除 Bloom
     */
    removeBloom() {
        if (this.passes.bloom) {
            this.composer.removePass(this.passes.bloom);
            this.passes.bloom = null;
        }
    }
    
    /**
     * 添加自定义着色器
     */
    addShaderPass(shader) {
        const pass = new ShaderPass(shader);
        this.composer.addPass(pass);
        return pass;
    }
    
    /**
     * 渲染
     */
    render() {
        this.composer.render();
    }
    
    /**
     * 调整大小
     */
    setSize(width, height) {
        this.composer.setSize(width, height);
    }
}

/**
 * 昼夜循环
 */
export class DayNightCycle {
    constructor(scene) {
        this.scene = scene;
        this.time = 0;
        this.duration = 60; // 60 秒一天
        this.sunLight = null;
        this.moonLight = null;
        this.ambientLight = null;
        
        this.init();
    }
    
    /**
     * 初始化光照
     */
    init() {
        // 太阳光
        this.sunLight = new THREE.DirectionalLight(0xffffff, 1);
        this.sunLight.position.set(50, 100, 50);
        this.sunLight.castShadow = true;
        this.scene.add(this.sunLight);
        
        // 月光
        this.moonLight = new THREE.DirectionalLight(0x4444ff, 0.3);
        this.moonLight.position.set(-50, 50, -50);
        this.scene.add(this.moonLight);
        
        // 环境光
        this.ambientLight = new THREE.AmbientLight(0x404040, 0.5);
        this.scene.add(this.ambientLight);
    }
    
    /**
     * 更新时间
     */
    update(delta) {
        this.time += delta / this.duration;
        
        if (this.time > 1) {
            this.time = 0;
        }
        
        // 太阳位置
        const sunAngle = this.time * Math.PI * 2;
        this.sunLight.position.x = Math.cos(sunAngle) * 100;
        this.sunLight.position.y = Math.sin(sunAngle) * 100;
        
        // 光照强度
        const sunIntensity = Math.max(0, Math.sin(sunAngle));
        this.sunLight.intensity = sunIntensity;
        this.ambientLight.intensity = 0.2 + sunIntensity * 0.3;
        
        // 月光
        this.moonLight.intensity = Math.max(0, -Math.sin(sunAngle)) * 0.3;
        
        // 天空颜色
        const skyColor = new THREE.Color();
        if (sunIntensity > 0.5) {
            skyColor.setHex(0x87ceeb); // 白天
        } else if (sunIntensity > 0.1) {
            skyColor.setHex(0xff7f50); // 黄昏
        } else {
            skyColor.setHex(0x000033); // 夜晚
        }
        
        this.scene.background = skyColor;
        if (this.scene.fog) {
            this.scene.fog.color = skyColor;
        }
    }
    
    /**
     * 设置时间
     */
    setTime(hour) {
        this.time = hour / 24;
    }
}

// 使用示例
if (typeof window !== 'undefined') {
    console.log('特效系统已加载');
    console.log('可用功能:', ['粒子', '天气', '后处理', '昼夜循环']);
}
