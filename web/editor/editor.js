/**
 * 世界编辑器核心
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { TransformControls } from 'three/examples/jsm/controls/TransformControls.js';

/**
 * 世界编辑器类
 */
export class WorldEditor {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.transformControl = null;
        
        this.objects = [];
        this.selectedObject = null;
        this.currentTool = 'select';
        
        this.history = [];
        this.historyIndex = -1;
        
        this.init();
        this.animate();
    }
    
    /**
     * 初始化编辑器
     */
    init() {
        // 创建场景
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x87ceeb);
        
        // 创建相机
        this.camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        this.camera.position.set(20, 20, 20);
        this.camera.lookAt(0, 0, 0);
        
        // 创建渲染器
        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            antialias: true
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.shadowMap.enabled = true;
        
        // 添加光照
        this.addLights();
        
        // 添加地面
        this.addGround();
        
        // 轨道控制器
        this.controls = new OrbitControls(this.camera, this.canvas);
        this.controls.enableDamping = true;
        
        // 变换控制器
        this.transformControl = new TransformControls(this.camera, this.canvas);
        this.transformControl.addEventListener('dragging-changed', (event) => {
            this.controls.enabled = !event.value;
        });
        this.scene.add(this.transformControl);
        
        // 选择射线
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        
        // 事件监听
        this.addEventListeners();
        
        // 更新 UI
        this.updateSceneTree();
    }
    
    /**
     * 添加光照
     */
    addLights() {
        const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
        this.scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(50, 100, 50);
        directionalLight.castShadow = true;
        this.scene.add(directionalLight);
    }
    
    /**
     * 添加地面
     */
    addGround() {
        const groundGeometry = new THREE.PlaneGeometry(100, 100);
        const groundMaterial = new THREE.MeshStandardMaterial({ 
            color: 0x228B22,
            side: THREE.DoubleSide
        });
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        ground.name = '地面';
        this.addObject(ground);
    }
    
    /**
     * 添加事件监听
     */
    addEventListeners() {
        window.addEventListener('resize', () => this.onWindowResize(), false);
        this.canvas.addEventListener('mousedown', (e) => this.onMouseDown(e), false);
        this.canvas.addEventListener('keydown', (e) => this.onKeyDown(e), false);
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
     * 鼠标按下
     */
    onMouseDown(event) {
        if (event.target !== this.canvas) return;
        
        this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
        
        this.raycaster.setFromCamera(this.mouse, this.camera);
        
        const intersects = this.raycaster.intersectObjects(this.objects);
        
        if (intersects.length > 0) {
            this.selectObject(intersects[0].object);
        } else {
            this.deselectObject();
        }
    }
    
    /**
     * 键盘按下
     */
    onKeyDown(event) {
        switch (event.key.toLowerCase()) {
            case 'delete':
            case 'backspace':
                if (this.selectedObject) {
                    this.deleteObject(this.selectedObject);
                }
                break;
            case 'w':
                this.setTool('move');
                break;
            case 'e':
                this.setTool('rotate');
                break;
            case 'r':
                this.setTool('scale');
                break;
            case 'z':
                if (event.ctrlKey) {
                    if (event.shiftKey) {
                        this.redo();
                    } else {
                        this.undo();
                    }
                }
                break;
        }
    }
    
    /**
     * 设置工具
     */
    setTool(tool) {
        this.currentTool = tool;
        
        if (tool === 'select') {
            this.transformControl.detach();
        } else {
            if (this.selectedObject) {
                this.transformControl.attach(this.selectedObject);
                this.transformControl.setMode(tool);
            }
        }
        
        // 更新 UI
        document.querySelectorAll('.tool-btn[data-tool]').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tool === tool);
        });
    }
    
    /**
     * 选择物体
     */
    selectObject(object) {
        this.deselectObject();
        
        this.selectedObject = object;
        this.transformControl.attach(object);
        
        // 高亮
        if (object.material) {
            object.userData.originalEmissive = object.material.emissive.clone();
            object.material.emissive.setHex(0xffff00);
        }
        
        // 更新属性面板
        this.updatePropertiesPanel();
        
        // 更新场景树
        this.updateSceneTree();
        
        // 更新状态栏
        document.getElementById('selection-info').textContent = `选中：${object.name}`;
    }
    
    /**
     * 取消选择
     */
    deselectObject() {
        if (this.selectedObject) {
            // 恢复原色
            if (this.selectedObject.material && this.selectedObject.userData.originalEmissive) {
                this.selectedObject.material.emissive.copy(this.selectedObject.userData.originalEmissive);
            }
            
            this.transformControl.detach();
            this.selectedObject = null;
        }
        
        document.getElementById('selection-info').textContent = '未选择物体';
        this.updateSceneTree();
    }
    
    /**
     * 添加物体
     */
    addObject(object) {
        this.scene.add(object);
        this.objects.push(object);
        this.saveState();
        this.updateSceneTree();
        this.updateObjectCount();
    }
    
    /**
     * 删除物体
     */
    deleteObject(object) {
        const index = this.objects.indexOf(object);
        if (index > -1) {
            this.objects.splice(index, 1);
            this.scene.remove(object);
            this.deselectObject();
            this.saveState();
            this.updateSceneTree();
            this.updateObjectCount();
        }
    }
    
    /**
     * 添加资源
     */
    addAsset(type, model) {
        let geometry, material, mesh;
        
        switch (model) {
            case 'house':
                geometry = new THREE.BoxGeometry(4, 3, 4);
                material = new THREE.MeshStandardMaterial({ color: 0x8B4513 });
                mesh = new THREE.Mesh(geometry, material);
                mesh.name = '房屋';
                break;
            case 'tower':
                geometry = new THREE.CylinderGeometry(2, 2, 10, 8);
                material = new THREE.MeshStandardMaterial({ color: 0x808080 });
                mesh = new THREE.Mesh(geometry, material);
                mesh.name = '高楼';
                break;
            case 'tree':
                geometry = new THREE.ConeGeometry(1, 3, 8);
                material = new THREE.MeshStandardMaterial({ color: 0x228B22 });
                mesh = new THREE.Mesh(geometry, material);
                mesh.name = '树';
                break;
            case 'rock':
                geometry = new THREE.DodecahedronGeometry(1);
                material = new THREE.MeshStandardMaterial({ color: 0x808080 });
                mesh = new THREE.Mesh(geometry, material);
                mesh.name = '石头';
                break;
            default:
                geometry = new THREE.BoxGeometry(1, 1, 1);
                material = new THREE.MeshStandardMaterial({ color: 0xff0000 });
                mesh = new THREE.Mesh(geometry, material);
                mesh.name = '物体';
        }
        
        mesh.position.set(0, 1, 0);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        
        this.addObject(mesh);
        this.selectObject(mesh);
    }
    
    /**
     * 更新属性面板
     */
    updatePropertiesPanel() {
        if (!this.selectedObject) return;
        
        document.getElementById('prop-x').value = this.selectedObject.position.x.toFixed(2);
        document.getElementById('prop-y').value = this.selectedObject.position.y.toFixed(2);
        document.getElementById('prop-z').value = this.selectedObject.position.z.toFixed(2);
        document.getElementById('prop-name').value = this.selectedObject.name;
    }
    
    /**
     * 更新选中物体属性
     */
    updateSelectedProperty(prop, value) {
        if (!this.selectedObject) return;
        
        switch (prop) {
            case 'x':
                this.selectedObject.position.x = parseFloat(value);
                break;
            case 'y':
                this.selectedObject.position.y = parseFloat(value);
                break;
            case 'z':
                this.selectedObject.position.z = parseFloat(value);
                break;
            case 'name':
                this.selectedObject.name = value;
                this.updateSceneTree();
                break;
            case 'type':
                this.selectedObject.userData.type = value;
                break;
        }
        
        this.saveState();
    }
    
    /**
     * 更新场景树
     */
    updateSceneTree() {
        const list = document.getElementById('scene-list');
        list.innerHTML = '';
        
        for (const object of this.objects) {
            const item = document.createElement('div');
            item.className = 'scene-item';
            if (object === this.selectedObject) {
                item.classList.add('selected');
            }
            item.textContent = object.name;
            item.addEventListener('click', () => this.selectObject(object));
            list.appendChild(item);
        }
    }
    
    /**
     * 更新物体数量
     */
    updateObjectCount() {
        document.getElementById('object-count').textContent = `物体：${this.objects.length}`;
    }
    
    /**
     * 保存状态 (撤销/重做)
     */
    saveState() {
        const state = {
            objects: this.objects.map(obj => ({
                position: obj.position.clone(),
                rotation: obj.rotation.clone(),
                scale: obj.scale.clone(),
                name: obj.name
            }))
        };
        
        this.history = this.history.slice(0, this.historyIndex + 1);
        this.history.push(state);
        this.historyIndex++;
    }
    
    /**
     * 撤销
     */
    undo() {
        if (this.historyIndex > 0) {
            this.historyIndex--;
            this.loadState(this.history[this.historyIndex]);
        }
    }
    
    /**
     * 重做
     */
    redo() {
        if (this.historyIndex < this.history.length - 1) {
            this.historyIndex++;
            this.loadState(this.history[this.historyIndex]);
        }
    }
    
    /**
     * 加载状态
     */
    loadState(state) {
        // 恢复物体状态
        state.objects.forEach((objState, index) => {
            if (this.objects[index]) {
                this.objects[index].position.copy(objState.position);
                this.objects[index].rotation.copy(objState.rotation);
                this.objects[index].scale.copy(objState.scale);
                this.objects[index].name = objState.name;
            }
        });
        
        this.deselectObject();
        this.updateSceneTree();
    }
    
    /**
     * 保存世界
     */
    save() {
        const data = {
            objects: this.objects.map(obj => ({
                type: obj.userData.type || 'prop',
                position: obj.position.toArray(),
                rotation: obj.rotation.toArray(),
                scale: obj.scale.toArray(),
                name: obj.name
            }))
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'world.json';
        a.click();
        URL.revokeObjectURL(url);
        
        console.log('世界已保存');
    }
    
    /**
     * 加载世界
     */
    load() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = (e) => {
                const data = JSON.parse(e.target.result);
                this.loadWorld(data);
            };
            reader.readAsText(file);
        });
        
        input.click();
    }
    
    /**
     * 加载世界数据
     */
    loadWorld(data) {
        // 清除现有物体
        for (const object of this.objects) {
            this.scene.remove(object);
        }
        this.objects = [];
        
        // 创建新物体
        data.objects.forEach(objData => {
            const geometry = new THREE.BoxGeometry(1, 1, 1);
            const material = new THREE.MeshStandardMaterial({ color: Math.random() * 0xffffff });
            const mesh = new THREE.Mesh(geometry, material);
            
            mesh.position.fromArray(objData.position);
            mesh.rotation.fromArray(objData.rotation);
            mesh.scale.fromArray(objData.scale);
            mesh.name = objData.name;
            mesh.userData.type = objData.type;
            
            this.addObject(mesh);
        });
        
        console.log('世界已加载');
    }
    
    /**
     * 动画循环
     */
    animate() {
        requestAnimationFrame(() => this.animate());
        
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }
}

console.log('世界编辑器核心已加载');
