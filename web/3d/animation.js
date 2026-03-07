/**
 * 角色动画系统
 * 
 * 支持骨骼动画、状态机、混合动画
 */

import * as THREE from 'three';

/**
 * 动画状态
 */
export const AnimationState = {
    IDLE: 'idle',
    WALK: 'walk',
    RUN: 'run',
    JUMP: 'jump',
    FALL: 'fall'
};

/**
 * 角色动画控制器
 */
export class CharacterAnimator {
    constructor(character) {
        this.character = character;
        this.currentState = AnimationState.IDLE;
        this.previousState = AnimationState.IDLE;
        this.animations = {};
        this.mixer = null;
        this.clock = new THREE.Clock();
        
        this.init();
    }
    
    /**
     * 初始化动画系统
     */
    init() {
        // 创建动画剪辑
        this.createIdleAnimation();
        this.createWalkAnimation();
        this.createRunAnimation();
        this.createJumpAnimation();
        
        // 创建动画混合器
        this.mixer = new THREE.AnimationMixer(this.character);
        
        // 播放空闲动画
        this.play(AnimationState.IDLE);
    }
    
    /**
     * 创建空闲动画
     */
    createIdleAnimation() {
        const duration = 2;
        const times = [0, duration];
        const values = [0, 0.1]; // 轻微上下浮动
        
        const track = new THREE.NumberKeyframeTrack(
            '.position.y',
            times,
            values,
            THREE.InterpolateSmooth
        );
        
        this.animations[AnimationState.IDLE] = new THREE.AnimationClip('idle', duration, [track]);
    }
    
    /**
     * 创建行走动画
     */
    createWalkAnimation() {
        const duration = 1;
        const times = [0, 0.25, 0.5, 0.75, 1];
        const values = [0, 0.2, 0, -0.2, 0];
        
        const track = new THREE.NumberKeyframeTrack(
            '.rotation.y',
            times,
            values,
            THREE.InterpolateSmooth
        );
        
        this.animations[AnimationState.WALK] = new THREE.AnimationClip('walk', duration, [track]);
    }
    
    /**
     * 创建跑步动画
     */
    createRunAnimation() {
        const duration = 0.5;
        const times = [0, 0.25, 0.5, 0.75, 1];
        const values = [0, 0.3, 0, -0.3, 0];
        
        const track = new THREE.NumberKeyframeTrack(
            '.rotation.y',
            times,
            values,
            THREE.InterpolateSmooth
        );
        
        this.animations[AnimationState.RUN] = new THREE.AnimationClip('run', duration, [track]);
    }
    
    /**
     * 创建跳跃动画
     */
    createJumpAnimation() {
        const duration = 1;
        const times = [0, 0.5, 1];
        const values = [0, 2, 0];
        
        const track = new THREE.NumberKeyframeTrack(
            '.position.y',
            times,
            values,
            THREE.InterpolateSmooth
        );
        
        this.animations[AnimationState.JUMP] = new THREE.AnimationClip('jump', duration, [track]);
    }
    
    /**
     * 播放动画
     */
    play(state, fadeIn = 0.3) {
        if (this.currentState === state) return;
        
        const clip = this.animations[state];
        if (!clip) return;
        
        const action = this.mixer.clipAction(clip);
        
        if (fadeIn > 0) {
            action.reset();
            action.fadeIn(fadeIn);
        }
        
        action.play();
        this.previousState = this.currentState;
        this.currentState = state;
    }
    
    /**
     * 更新动画
     */
    update(delta) {
        if (this.mixer) {
            this.mixer.update(delta);
        }
    }
    
    /**
     * 根据速度更新动画状态
     */
    updateFromVelocity(velocity) {
        const speed = Math.sqrt(velocity.x * velocity.x + velocity.z * velocity.z);
        
        if (velocity.y > 0.1) {
            this.play(AnimationState.JUMP);
        } else if (velocity.y < -0.1) {
            this.play(AnimationState.FALL);
        } else if (speed > 5) {
            this.play(AnimationState.RUN);
        } else if (speed > 0.1) {
            this.play(AnimationState.WALK);
        } else {
            this.play(AnimationState.IDLE);
        }
    }
    
    /**
     * 获取当前状态
     */
    getState() {
        return this.currentState;
    }
}

/**
 * 动画状态机
 */
export class AnimationStateMachine {
    constructor() {
        this.states = {};
        this.transitions = {};
        this.currentState = null;
    }
    
    /**
     * 添加状态
     */
    addState(name, animation) {
        this.states[name] = {
            name,
            animation,
            onEnter: null,
            onExit: null,
            onUpdate: null
        };
    }
    
    /**
     * 添加转换
     */
    addTransition(from, to, condition) {
        if (!this.transitions[from]) {
            this.transitions[from] = [];
        }
        
        this.transitions[from].push({
            to,
            condition
        });
    }
    
    /**
     * 设置状态回调
     */
    onEnter(state, callback) {
        if (this.states[state]) {
            this.states[state].onEnter = callback;
        }
    }
    
    onExit(state, callback) {
        if (this.states[state]) {
            this.states[state].onExit = callback;
        }
    }
    
    onUpdate(state, callback) {
        if (this.states[state]) {
            this.states[state].onUpdate = callback;
        }
    }
    
    /**
     * 更新状态机
     */
    update(delta, context) {
        // 检查转换
        if (this.transitions[this.currentState]) {
            for (const transition of this.transitions[this.currentState]) {
                if (transition.condition(context)) {
                    this.setState(transition.to);
                    break;
                }
            }
        }
        
        // 更新当前状态
        if (this.currentState && this.states[this.currentState]) {
            const state = this.states[this.currentState];
            if (state.onUpdate) {
                state.onUpdate(delta, context);
            }
        }
    }
    
    /**
     * 设置状态
     */
    setState(name) {
        if (this.currentState === name) return;
        
        // 退出当前状态
        if (this.currentState && this.states[this.currentState]) {
            const state = this.states[this.currentState];
            if (state.onExit) {
                state.onExit();
            }
        }
        
        // 进入新状态
        this.currentState = name;
        
        if (this.states[name]) {
            const state = this.states[name];
            if (state.onEnter) {
                state.onEnter();
            }
        }
    }
    
    /**
     * 获取当前状态
     */
    getState() {
        return this.currentState;
    }
}

/**
 * 骨骼辅助类
 */
export class SkeletonHelper {
    static createHumanoidSkeleton() {
        const bones = [];
        
        // 臀部
        const hipBone = new THREE.Bone();
        bones.push(hipBone);
        
        // 脊椎
        const spineBone = new THREE.Bone();
        spineBone.position.y = 0.5;
        hipBone.add(spineBone);
        bones.push(spineBone);
        
        // 头部
        const headBone = new THREE.Bone();
        headBone.position.y = 0.5;
        spineBone.add(headBone);
        bones.push(headBone);
        
        // 左腿
        const leftLegBone = new THREE.Bone();
        leftLegBone.position.y = -0.5;
        hipBone.add(leftLegBone);
        bones.push(leftLegBone);
        
        // 右腿
        const rightLegBone = new THREE.Bone();
        rightLegBone.position.y = -0.5;
        hipBone.add(rightLegBone);
        bones.push(rightLegBone);
        
        // 左臂
        const leftArmBone = new THREE.Bone();
        leftArmBone.position.y = 0.3;
        leftArmBone.position.x = -0.3;
        spineBone.add(leftArmBone);
        bones.push(leftArmBone);
        
        // 右臂
        const rightArmBone = new THREE.Bone();
        rightArmBone.position.y = 0.3;
        rightArmBone.position.x = 0.3;
        spineBone.add(rightArmBone);
        bones.push(rightArmBone);
        
        return new THREE.Skeleton(bones);
    }
    
    static createSkeletonVisualizer(skeleton) {
        return new THREE.SkeletonHelper(skeleton.bones[0]);
    }
}

/**
 * 加载外部动画
 */
export class AnimationLoader {
    static async loadGLTFAnimation(url, mixer) {
        const { GLTFLoader } = await import('three/examples/jsm/loaders/GLTFLoader.js');
        
        return new Promise((resolve, reject) => {
            const loader = new GLTFLoader();
            loader.load(url, (gltf) => {
                const model = gltf.scene;
                const animations = gltf.animations;
                
                resolve({ model, animations });
            }, undefined, reject);
        });
    }
    
    static async loadFBXAnimation(url, mixer) {
        const { FBXLoader } = await import('three/examples/jsm/loaders/FBXLoader.js');
        
        return new Promise((resolve, reject) => {
            const loader = new FBXLoader();
            loader.load(url, (object) => {
                const animations = object.animations;
                
                resolve({ object, animations });
            }, undefined, reject);
        });
    }
}

// 使用示例
if (typeof window !== 'undefined') {
    console.log('动画系统已加载');
    console.log('可用状态:', Object.keys(AnimationState));
}
