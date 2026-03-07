"""
物理系统

实现物理引擎集成和碰撞检测
"""

from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel
from datetime import datetime
import math

from .space import Vector3


# ==================== 物理属性 ====================

class PhysicsBody(BaseModel):
    """
    物理刚体
    """
    id: str
    position: Vector3
    velocity: Vector3 = None
    acceleration: Vector3 = None
    mass: float = 1.0
    size: Vector3 = None  # 包围盒大小
    
    # 物理属性
    gravity_enabled: bool = True
    collision_enabled: bool = True
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'velocity' not in data:
            data['velocity'] = Vector3()
        if 'acceleration' not in data:
            data['acceleration'] = Vector3()
        super().__init__(**data)
    
    def apply_force(self, force: Vector3):
        """施加力"""
        # F = ma => a = F/m
        self.acceleration = self.acceleration.add(
            force.scale(1.0 / self.mass)
        )
    
    def update(self, delta_time: float):
        """更新物理状态"""
        # 更新速度
        self.velocity = self.velocity.add(
            self.acceleration.scale(delta_time)
        )
        
        # 更新位置
        self.position = self.position.add(
            self.velocity.scale(delta_time)
        )
        
        # 重置加速度
        self.acceleration = Vector3()


# ==================== 碰撞体 ====================

class Collider(BaseModel):
    """
    碰撞体
    """
    id: str
    position: Vector3
    size: Vector3  # 包围盒大小
    
    def intersects(self, other: "Collider") -> bool:
        """检查是否与另一个碰撞体相交"""
        return (
            abs(self.position.x - other.position.x) < (self.size.x + other.size.x) / 2 and
            abs(self.position.y - other.position.y) < (self.size.y + other.size.y) / 2 and
            abs(self.position.z - other.position.z) < (self.size.z + other.size.z) / 2
        )
    
    def contains_point(self, point: Vector3) -> bool:
        """检查点是否在碰撞体内"""
        half_size = self.size.scale(0.5)
        return (
            abs(point.x - self.position.x) <= half_size.x and
            abs(point.y - self.position.y) <= half_size.y and
            abs(point.z - self.position.z) <= half_size.z
        )


# ==================== 物理世界 ====================

class PhysicsWorld:
    """
    物理世界
    
    管理所有物理对象和碰撞检测
    """
    
    def __init__(self, gravity: float = -9.8):
        self.gravity = Vector3(x=0, y=gravity, z=0)
        self.bodies: Dict[str, PhysicsBody] = {}
        self.colliders: Dict[str, Collider] = {}
        self.collision_pairs: List[Tuple[str, str]] = []
    
    def add_body(self, body: PhysicsBody):
        """添加物理刚体"""
        self.bodies[body.id] = body
    
    def remove_body(self, body_id: str):
        """移除物理刚体"""
        if body_id in self.bodies:
            del self.bodies[body_id]
    
    def add_collider(self, collider: Collider):
        """添加碰撞体"""
        self.colliders[collider.id] = collider
    
    def remove_collider(self, collider_id: str):
        """移除碰撞体"""
        if collider_id in self.colliders:
            del self.colliders[collider_id]
    
    def step(self, delta_time: float):
        """
        物理世界步进
        
        Args:
            delta_time: 时间步长 (秒)
        """
        # 1. 应用重力
        for body in self.bodies.values():
            if body.gravity_enabled:
                body.apply_force(
                    self.gravity.scale(body.mass)
                )
        
        # 2. 更新所有刚体
        for body in self.bodies.values():
            body.update(delta_time)
        
        # 3. 碰撞检测
        self._detect_collisions()
        
        # 4. 碰撞响应
        self._resolve_collisions()
    
    def _detect_collisions(self):
        """检测碰撞"""
        self.collision_pairs = []
        
        collider_list = list(self.colliders.values())
        n = len(collider_list)
        
        for i in range(n):
            for j in range(i + 1, n):
                c1 = collider_list[i]
                c2 = collider_list[j]
                
                if c1.intersects(c2):
                    self.collision_pairs.append((c1.id, c2.id))
    
    def _resolve_collisions(self):
        """碰撞响应"""
        # 简单实现：暂不处理复杂碰撞响应
        pass
    
    def get_collisions_for(self, collider_id: str) -> List[str]:
        """获取与指定碰撞体碰撞的所有碰撞体"""
        collisions = []
        for c1, c2 in self.collision_pairs:
            if c1 == collider_id:
                collisions.append(c2)
            elif c2 == collider_id:
                collisions.append(c1)
        return collisions
    
    def raycast(
        self,
        origin: Vector3,
        direction: Vector3,
        max_distance: float = 1000.0
    ) -> Optional[Tuple[str, Vector3]]:
        """
        射线投射
        
        Args:
            origin: 射线起点
            direction: 射线方向
            max_distance: 最大距离
        
        Returns:
            (碰撞体 ID, 碰撞点) 或 None
        """
        closest_distance = max_distance
        closest_collider = None
        closest_point = None
        
        for collider in self.colliders.values():
            hit, point = self._raycast_collider(
                origin, direction, collider, max_distance
            )
            
            if hit and point:
                distance = origin.distance_to(point)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_collider = collider.id
                    closest_point = point
        
        if closest_collider:
            return (closest_collider, closest_point)
        return None
    
    def _raycast_collider(
        self,
        origin: Vector3,
        direction: Vector3,
        collider: Collider,
        max_distance: float
    ) -> Tuple[bool, Optional[Vector3]]:
        """射线与碰撞体相交测试"""
        # 简化的 AABB 射线相交测试
        half_size = collider.size.scale(0.5)
        
        # 计算射线与包围盒的交点
        # 这里使用简化的实现
        if collider.contains_point(origin):
            return (True, origin)
        
        return (False, None)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取物理世界统计"""
        return {
            "total_bodies": len(self.bodies),
            "total_colliders": len(self.colliders),
            "active_collisions": len(self.collision_pairs)
        }


# ==================== 物理引擎管理器 ====================

class PhysicsEngine:
    """
    物理引擎管理器
    
    提供高级物理功能
    """
    
    def __init__(self):
        self.world = PhysicsWorld()
        self.fixed_timestep = 1.0 / 60.0  # 60 FPS
        self.accumulator = 0.0
    
    def update(self, delta_time: float):
        """
        更新物理引擎
        
        使用固定时间步长保证物理稳定性
        
        Args:
            delta_time: 帧时间 (秒)
        """
        self.accumulator += delta_time
        
        # 固定时间步长更新
        while self.accumulator >= self.fixed_timestep:
            self.world.step(self.fixed_timestep)
            self.accumulator -= self.fixed_timestep
    
    def add_object(
        self,
        id: str,
        position: Vector3,
        size: Vector3,
        mass: float = 1.0
    ):
        """添加物理对象"""
        # 创建刚体
        body = PhysicsBody(
            id=id,
            position=position,
            mass=mass,
            size=size
        )
        self.world.add_body(body)
        
        # 创建碰撞体
        collider = Collider(
            id=f"collider_{id}",
            position=position,
            size=size
        )
        self.world.add_collider(collider)
    
    def move_object(
        self,
        id: str,
        velocity: Vector3
    ):
        """移动对象"""
        body = self.world.bodies.get(id)
        if body:
            body.velocity = velocity
    
    def get_object_position(self, id: str) -> Optional[Vector3]:
        """获取对象位置"""
        body = self.world.bodies.get(id)
        if body:
            return body.position
        return None
    
    def check_collision(
        self,
        id1: str,
        id2: str
    ) -> bool:
        """检查两个对象是否碰撞"""
        collider1_id = f"collider_{id1}"
        collider2_id = f"collider_{id2}"
        
        return (collider1_id, collider2_id) in self.world.collision_pairs or \
               (collider2_id, collider1_id) in self.world.collision_pairs


# 使用示例
if __name__ == "__main__":
    import time
    
    # 创建物理引擎
    engine = PhysicsEngine()
    
    # 添加一个球
    engine.add_object(
        id="ball_1",
        position=Vector3(x=0, y=10, z=0),
        size=Vector3(x=1, y=1, z=1),
        mass=1.0
    )
    
    # 添加地面
    engine.add_object(
        id="ground",
        position=Vector3(x=0, y=0, z=0),
        size=Vector3(x=100, y=1, z=100),
        mass=0  # 无限质量，静止
    )
    
    # 模拟物理
    print("开始物理模拟...")
    for i in range(60):  # 模拟 60 帧
        engine.update(1.0 / 60.0)
        
        pos = engine.get_object_position("ball_1")
        if pos:
            print(f"帧 {i+1}: 位置 = ({pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f})")
        
        time.sleep(0.016)  # 约 60 FPS
    
    # 获取统计
    stats = engine.world.get_statistics()
    print(f"\n物理统计：{stats}")
