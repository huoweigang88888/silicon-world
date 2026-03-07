# 🎮 3D 开发指南

硅基世界 3D 引擎开发文档

---

## 📖 概述

硅基世界使用 **Three.js** 作为 3D 渲染引擎，提供完整的 3D 场景、角色控制、光照和材质系统。

---

## 🚀 快速开始

### 1. 基础场景

```html
<!DOCTYPE html>
<html>
<head>
    <title>3D 场景</title>
</head>
<body>
    <canvas id="canvas"></canvas>
    <script type="module">
        import { Engine3D } from './engine.js';
        
        const engine = new Engine3D('canvas');
    </script>
</body>
</html>
```

### 2. 添加实体

```javascript
// 创建建筑
const building = engine.createBuilding(
    10,  // 宽度
    20,  // 高度
    10,  // 深度
    new THREE.Vector3(0, 0, 0),  // 位置
    0xff0000  // 颜色
);

// 创建角色
const character = engine.createCharacter(
    new THREE.Vector3(5, 0, 5)
);

// 创建粒子
const particles = engine.createParticleSystem(
    1000,  // 粒子数量
    0x00ff00,  // 颜色
    new THREE.Vector3(0, 5, 0)  // 位置
);
```

---

## 🎨 光照系统

### 环境光

```javascript
const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
scene.add(ambientLight);
```

### 平行光

```javascript
const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(50, 100, 50);
directionalLight.castShadow = true;
scene.add(directionalLight);
```

### 点光源

```javascript
const pointLight = new THREE.PointLight(0xff0000, 1, 100);
pointLight.position.set(0, 10, 0);
scene.add(pointLight);
```

---

## 🎭 材质系统

### 标准材质

```javascript
const material = new THREE.MeshStandardMaterial({
    color: 0x6200ee,
    metalness: 0.5,
    roughness: 0.5
});
```

### 物理材质

```javascript
const material = new THREE.MeshPhysicalMaterial({
    color: 0x00ff00,
    metalness: 0.0,
    roughness: 0.0,
    transmission: 1.0,  // 玻璃效果
    thickness: 0.5
});
```

### 纹理材质

```javascript
const texture = new THREE.TextureLoader().load('texture.jpg');
const material = new THREE.MeshStandardMaterial({
    map: texture,
    roughness: 0.5
});
```

---

## 🎬 动画系统

### 基础动画

```javascript
import { Animation } from './engine.js';

const animation = new Animation(
    object.position,  // 目标对象
    { x: 10, y: 5, z: 10 },  // 目标值
    1000  // 持续时间 (ms)
);

engine.animations.push(animation);
```

### 自定义动画

```javascript
class CustomAnimation {
    constructor(object) {
        this.object = object;
        this.elapsed = 0;
    }
    
    update() {
        this.elapsed += 0.016;
        this.object.rotation.y = Math.sin(this.elapsed);
    }
}

const anim = new CustomAnimation(object);
engine.animations.push(anim);
```

---

## ⚡ 性能优化

### 1. 几何体合并

```javascript
// 合并多个几何体减少绘制调用
const mergedGeometry = THREE.BufferGeometryUtils.mergeGeometries(geometries);
const mergedMesh = new THREE.Mesh(mergedGeometry, material);
```

### 2. 实例化渲染

```javascript
// 使用实例化渲染大量相同物体
const instancedMesh = new THREE.InstancedMesh(geometry, material, count);
for (let i = 0; i < count; i++) {
    instancedMesh.setMatrixAt(i, matrix);
}
scene.add(instancedMesh);
```

### 3. 层级细节 (LOD)

```javascript
const lod = new THREE.LOD();

// 高精度模型 (近距离)
lod.addLevel(highDetailMesh, 0);

// 中精度模型 (中距离)
lod.addLevel(mediumDetailMesh, 50);

// 低精度模型 (远距离)
lod.addLevel(lowDetailMesh, 100);

scene.add(lod);
```

### 4. 遮挡剔除

```javascript
// 使用视锥体剔除
const frustum = new THREE.Frustum();
const projScreenMatrix = new THREE.Matrix4();

projScreenMatrix.multiplyMatrices(
    camera.projectionMatrix,
    camera.matrixWorldInverse
);
frustum.setFromProjectionMatrix(projScreenMatrix);

// 检查物体是否在视锥体内
if (frustum.intersectsObject(object)) {
    // 渲染物体
}
```

---

## 🎮 控制器

### 第一人称控制器

```javascript
import { PointerLockControls } from 'three/examples/jsm/controls/PointerLockControls.js';

const controls = new PointerLockControls(camera, document.body);

document.addEventListener('click', () => {
    controls.lock();
});
```

### 轨道控制器

```javascript
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
```

---

## 📊 调试工具

### 性能监控

```javascript
// FPS 监控
const fps = engine.getFPS();
console.log(`FPS: ${fps}`);

// 实体数量
const count = engine.getEntityCount();
console.log(`实体数：${count}`);
```

### 调试辅助

```javascript
// 显示坐标轴
const axesHelper = new THREE.AxesHelper(5);
scene.add(axesHelper);

// 显示网格
const gridHelper = new THREE.GridHelper(100, 50);
scene.add(gridHelper);

// 显示边界盒
const boxHelper = new THREE.BoxHelper(object, 0xff0000);
scene.add(boxHelper);
```

---

## 🐛 常见问题

### 性能问题

**Q: FPS 过低怎么办？**
- 减少多边形数量
- 使用 LOD
- 合并几何体
- 优化阴影质量

**Q: 内存泄漏？**
- 及时 dispose 几何体和材质
- 移除不用的物体
- 清理纹理缓存

### 渲染问题

**Q: 模型闪烁？**
- 调整 z-fighting 偏移
- 增加深度精度

**Q: 阴影质量问题？**
- 增加阴影贴图分辨率
- 调整阴影相机范围
- 使用 PCF 或 VSM 阴影

---

## 📚 参考资源

- [Three.js 官方文档](https://threejs.org/docs/)
- [Three.js 示例](https://threejs.org/examples/)
- [WebGL 指南](https://webglfundamentals.org/)

---

**🎮 开始创建你的 3D 世界吧！**
