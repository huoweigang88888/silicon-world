"""
3D 空间引擎

管理虚拟世界的空间结构
"""

from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel, Field
from datetime import datetime
import math


# ==================== 坐标系统 ====================

class Vector3(BaseModel):
    """3D 向量"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def distance_to(self, other: "Vector3") -> float:
        """计算到另一点的距离"""
        return math.sqrt(
            (self.x - other.x) ** 2 +
            (self.y - other.y) ** 2 +
            (self.z - other.z) ** 2
        )
    
    def add(self, other: "Vector3") -> "Vector3":
        """向量相加"""
        return Vector3(
            x=self.x + other.x,
            y=self.y + other.y,
            z=self.z + other.z
        )
    
    def scale(self, factor: float) -> "Vector3":
        """缩放"""
        return Vector3(
            x=self.x * factor,
            y=self.y * factor,
            z=self.z * factor
        )
    
    def to_tuple(self) -> Tuple[float, float, float]:
        """转换为元组"""
        return (self.x, self.y, self.z)


class Rotation(BaseModel):
    """旋转"""
    yaw: float = 0.0    # 偏航角 (左右)
    pitch: float = 0.0  # 俯仰角 (上下)
    roll: float = 0.0   # 翻滚角 (旋转)


# ==================== 空间区域 ====================

class Region(BaseModel):
    """
    空间区域
    
    定义世界中的一个区域
    """
    id: str
    name: str
    description: str = ""
    
    # 边界
    min_point: Vector3
    max_point: Vector3
    
    # 父区域 (用于层级结构)
    parent_id: Optional[str] = None
    
    # 子区域
    children: List[str] = []
    
    # 元数据
    metadata: Dict[str, Any] = {}
    created_at: datetime = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow()
        super().__init__(**data)
    
    def contains_point(self, point: Vector3) -> bool:
        """检查点是否在区域内"""
        return (
            self.min_point.x <= point.x <= self.max_point.x and
            self.min_point.y <= point.y <= self.max_point.y and
            self.min_point.z <= point.z <= self.max_point.z
        )
    
    def get_center(self) -> Vector3:
        """获取区域中心"""
        return Vector3(
            x=(self.min_point.x + self.max_point.x) / 2,
            y=(self.min_point.y + self.max_point.y) / 2,
            z=(self.min_point.z + self.max_point.z) / 2
        )
    
    def get_size(self) -> Vector3:
        """获取区域大小"""
        return Vector3(
            x=self.max_point.x - self.min_point.x,
            y=self.max_point.y - self.min_point.y,
            z=self.max_point.z - self.min_point.z
        )
    
    def get_volume(self) -> float:
        """获取区域体积"""
        size = self.get_size()
        return size.x * size.y * size.z


# ==================== 传送点 ====================

class Portal(BaseModel):
    """
    传送点
    
    用于在不同区域间传送
    """
    id: str
    name: str
    position: Vector3
    rotation: Rotation = None
    target_region_id: str
    target_position: Vector3
    active: bool = True
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'rotation' not in data:
            data['rotation'] = Rotation()
        super().__init__(**data)


# ==================== 空间管理器 ====================

class SpaceManager:
    """
    空间管理器
    
    管理整个世界空间
    """
    
    def __init__(self):
        self.regions: Dict[str, Region] = {}
        self.portals: Dict[str, Portal] = {}
        self.entities: Dict[str, Any] = {}  # 实体位置
    
    def create_region(
        self,
        id: str,
        name: str,
        min_point: Vector3,
        max_point: Vector3,
        description: str = "",
        parent_id: str = None
    ) -> Region:
        """
        创建区域
        
        Args:
            id: 区域 ID
            name: 区域名称
            min_point: 最小坐标
            max_point: 最大坐标
            description: 描述
            parent_id: 父区域 ID
        
        Returns:
            Region
        """
        region = Region(
            id=id,
            name=name,
            description=description,
            min_point=min_point,
            max_point=max_point,
            parent_id=parent_id
        )
        
        self.regions[id] = region
        
        # 添加到父区域的子区域列表
        if parent_id and parent_id in self.regions:
            self.regions[parent_id].children.append(id)
        
        return region
    
    def get_region(self, region_id: str) -> Optional[Region]:
        """获取区域"""
        return self.regions.get(region_id)
    
    def get_region_at_point(self, point: Vector3) -> Optional[Region]:
        """获取包含某点的区域"""
        for region in self.regions.values():
            if region.contains_point(point):
                return region
        return None
    
    def create_portal(
        self,
        id: str,
        name: str,
        position: Vector3,
        target_region_id: str,
        target_position: Vector3
    ) -> Portal:
        """
        创建传送点
        
        Args:
            id: 传送点 ID
            name: 名称
            position: 位置
            target_region_id: 目标区域 ID
            target_position: 目标位置
        
        Returns:
            Portal
        """
        portal = Portal(
            id=id,
            name=name,
            position=position,
            target_region_id=target_region_id,
            target_position=target_position
        )
        
        self.portals[id] = portal
        return portal
    
    def teleport(
        self,
        entity_id: str,
        portal_id: str
    ) -> Tuple[bool, str]:
        """
        传送实体
        
        Args:
            entity_id: 实体 ID
            portal_id: 传送点 ID
        
        Returns:
            (成功，消息)
        """
        portal = self.portals.get(portal_id)
        if not portal:
            return False, "传送点不存在"
        
        if not portal.active:
            return False, "传送点未激活"
        
        # 更新实体位置
        self.entities[entity_id] = {
            "region_id": portal.target_region_id,
            "position": portal.target_position
        }
        
        return True, f"传送到 {portal.name}"
    
    def get_entities_in_region(self, region_id: str) -> List[str]:
        """获取区域内的所有实体"""
        entities = []
        for entity_id, data in self.entities.items():
            if data.get("region_id") == region_id:
                entities.append(entity_id)
        return entities
    
    def get_nearby_entities(
        self,
        position: Vector3,
        radius: float
    ) -> List[Tuple[str, float]]:
        """
        获取附近的实体
        
        Args:
            position: 位置
            radius: 半径
        
        Returns:
            [(实体 ID, 距离), ...]
        """
        nearby = []
        
        for entity_id, data in self.entities.items():
            entity_pos = data.get("position")
            if entity_pos:
                distance = position.distance_to(entity_pos)
                if distance <= radius:
                    nearby.append((entity_id, distance))
        
        # 按距离排序
        nearby.sort(key=lambda x: x[1])
        
        return nearby
    
    def get_world_stats(self) -> Dict[str, Any]:
        """获取世界统计信息"""
        return {
            "total_regions": len(self.regions),
            "total_portals": len(self.portals),
            "total_entities": len(self.entities),
            "total_volume": sum(r.get_volume() for r in self.regions.values())
        }


# ==================== 预设世界 ====================

def create_default_world() -> SpaceManager:
    """创建默认世界"""
    manager = SpaceManager()
    
    # 创建主城区域
    hub = manager.create_region(
        id="hub_center",
        name="中心城",
        min_point=Vector3(x=-500, y=0, z=-500),
        max_point=Vector3(x=500, y=100, z=500),
        description="硅基世界的中心城市"
    )
    
    # 创建广场子区域
    manager.create_region(
        id="hub_plaza",
        name="中心广场",
        min_point=Vector3(x=-100, y=0, z=-100),
        max_point=Vector3(x=100, y=50, z=100),
        description="世界的中心广场",
        parent_id="hub_center"
    )
    
    # 创建居住区
    manager.create_region(
        id="residential",
        name="居住区",
        min_point=Vector3(x=500, y=0, z=-500),
        max_point=Vector3(x=1000, y=100, z=500),
        description="Agent 和人类的居住区"
    )
    
    # 创建商业区
    manager.create_region(
        id="commercial",
        name="商业区",
        min_point=Vector3(x=-1000, y=0, z=-500),
        max_point=Vector3(x=-500, y=100, z=500),
        description="交易和商业活动区"
    )
    
    # 创建传送点
    manager.create_portal(
        id="portal_hub_to_residential",
        name="主城 - 居住区传送点",
        position=Vector3(x=400, y=0, z=0),
        target_region_id="residential",
        target_position=Vector3(x=600, y=0, z=0)
    )
    
    return manager


# 使用示例
if __name__ == "__main__":
    # 创建世界
    world = create_default_world()
    
    # 获取世界统计
    stats = world.get_world_stats()
    print(f"世界统计：{stats}")
    
    # 获取区域
    region = world.get_region("hub_center")
    if region:
        print(f"\n中心城信息:")
        print(f"  名称：{region.name}")
        print(f"  描述：{region.description}")
        print(f"  体积：{region.get_volume():.2f}")
        print(f"  中心：{region.get_center().to_tuple()}")
    
    # 测试点是否在区域内
    test_point = Vector3(x=0, y=10, z=0)
    containing_region = world.get_region_at_point(test_point)
    if containing_region:
        print(f"\n点 {test_point.to_tuple()} 在区域：{containing_region.name}")
    
    # 创建传送
    world.entities["agent_1"] = {
        "region_id": "hub_center",
        "position": Vector3(x=400, y=0, z=0)
    }
    
    success, message = world.teleport("agent_1", "portal_hub_to_residential")
    print(f"\n传送结果：{message}")
    print(f"新位置：{world.entities['agent_1']}")
