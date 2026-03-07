"""
实体系统

管理世界中的对象和组件
"""

from typing import Dict, List, Optional, Any, Type, Set
from pydantic import BaseModel
from datetime import datetime
from abc import ABC, abstractmethod
import uuid

from .space import Vector3


# ==================== 组件系统 ====================

class Component(ABC, BaseModel):
    """组件基类"""
    id: str = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        super().__init__(**data)
    
    @abstractmethod
    def update(self, delta_time: float):
        """更新组件"""
        pass


class TransformComponent(Component):
    """变换组件 - 位置和旋转"""
    position: Vector3 = None
    rotation: Vector3 = None
    scale: Vector3 = None
    
    def __init__(self, **data):
        if 'position' not in data:
            data['position'] = Vector3()
        if 'rotation' not in data:
            data['rotation'] = Vector3()
        if 'scale' not in data:
            data['scale'] = Vector3(x=1, y=1, z=1)
        super().__init__(**data)
    
    def update(self, delta_time: float):
        """更新变换"""
        pass
    
    def translate(self, offset: Vector3):
        """平移"""
        self.position = self.position.add(offset)
    
    def rotate(self, angles: Vector3):
        """旋转"""
        self.rotation = self.rotation.add(angles)


class PhysicsComponent(Component):
    """物理组件"""
    mass: float = 1.0
    velocity: Vector3 = None
    gravity_enabled: bool = True
    
    def __init__(self, **data):
        if 'velocity' not in data:
            data['velocity'] = Vector3()
        super().__init__(**data)
    
    def update(self, delta_time: float):
        """更新物理"""
        if self.gravity_enabled:
            self.velocity.y += -9.8 * delta_time
        
        self.position = self.velocity  # 简化实现


class RenderComponent(Component):
    """渲染组件"""
    mesh_id: str = ""
    material_id: str = ""
    visible: bool = True
    
    def update(self, delta_time: float):
        """更新渲染"""
        pass


class ScriptComponent(Component):
    """脚本组件"""
    script_name: str = ""
    variables: Dict[str, Any] = {}
    
    def update(self, delta_time: float):
        """执行脚本"""
        # TODO: 执行脚本逻辑
        pass


class AIComponent(Component):
    """AI 组件"""
    agent_id: str = ""
    current_action: str = ""
    goals: List[str] = []
    
    def update(self, delta_time: float):
        """更新 AI"""
        # TODO: 更新 AI 决策
        pass


# ==================== 实体 ====================

class Entity(BaseModel):
    """
    实体
    
    由多个组件组成
    """
    id: str
    name: str
    description: str = ""
    components: Dict[str, Component] = {}
    tags: Set[str] = set()
    parent_id: Optional[str] = None
    children: List[str] = []
    active: bool = True
    created_at: datetime = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow()
        super().__init__(**data)
    
    def add_component(self, component: Component):
        """添加组件"""
        component_type = type(component).__name__
        self.components[component_type] = component
    
    def get_component(self, component_type: str) -> Optional[Component]:
        """获取组件"""
        return self.components.get(component_type)
    
    def remove_component(self, component_type: str):
        """移除组件"""
        if component_type in self.components:
            del self.components[component_type]
    
    def has_component(self, component_type: str) -> bool:
        """检查是否有组件"""
        return component_type in self.components
    
    def update(self, delta_time: float):
        """更新所有组件"""
        if not self.active:
            return
        
        for component in self.components.values():
            component.update(delta_time)
    
    def get_position(self) -> Optional[Vector3]:
        """获取位置"""
        transform = self.get_component("TransformComponent")
        if transform:
            return transform.position
        return None
    
    def set_position(self, position: Vector3):
        """设置位置"""
        transform = self.get_component("TransformComponent")
        if transform:
            transform.position = position
        else:
            self.add_component(TransformComponent(position=position))
    
    def add_tag(self, tag: str):
        """添加标签"""
        self.tags.add(tag)
    
    def remove_tag(self, tag: str):
        """移除标签"""
        self.tags.discard(tag)
    
    def has_tag(self, tag: str) -> bool:
        """检查标签"""
        return tag in self.tags


# ==================== 实体管理器 ====================

class EntityManager:
    """
    实体管理器
    
    管理世界中所有实体
    """
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.entities_by_tag: Dict[str, Set[str]] = {}
        self.entities_by_name: Dict[str, Set[str]] = {}
    
    def create_entity(
        self,
        name: str,
        description: str = "",
        parent_id: str = None
    ) -> Entity:
        """
        创建实体
        
        Args:
            name: 实体名称
            description: 描述
            parent_id: 父实体 ID
        
        Returns:
            Entity
        """
        entity_id = str(uuid.uuid4())
        
        entity = Entity(
            id=entity_id,
            name=name,
            description=description,
            parent_id=parent_id
        )
        
        self.entities[entity_id] = entity
        
        # 更新索引
        if name not in self.entities_by_name:
            self.entities_by_name[name] = set()
        self.entities_by_name[name].add(entity_id)
        
        # 添加到父实体的子列表
        if parent_id and parent_id in self.entities:
            self.entities[parent_id].children.append(entity_id)
        
        return entity
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """获取实体"""
        return self.entities.get(entity_id)
    
    def delete_entity(self, entity_id: str) -> bool:
        """
        删除实体
        
        Args:
            entity_id: 实体 ID
        
        Returns:
            是否成功
        """
        if entity_id not in self.entities:
            return False
        
        entity = self.entities[entity_id]
        
        # 删除所有子实体
        for child_id in entity.children:
            self.delete_entity(child_id)
        
        # 从父实体的子列表移除
        if entity.parent_id and entity.parent_id in self.entities:
            parent = self.entities[entity.parent_id]
            if entity_id in parent.children:
                parent.children.remove(entity_id)
        
        # 从索引移除
        if entity.name in self.entities_by_name:
            self.entities_by_name[entity.name].discard(entity_id)
        
        for tag in entity.tags:
            if tag in self.entities_by_tag:
                self.entities_by_tag[tag].discard(entity_id)
        
        # 删除实体
        del self.entities[entity_id]
        
        return True
    
    def find_by_tag(self, tag: str) -> List[Entity]:
        """根据标签查找实体"""
        entity_ids = self.entities_by_tag.get(tag, set())
        return [
            self.entities[eid]
            for eid in entity_ids
            if eid in self.entities
        ]
    
    def find_by_name(self, name: str) -> List[Entity]:
        """根据名称查找实体"""
        entity_ids = self.entities_by_name.get(name, set())
        return [
            self.entities[eid]
            for eid in entity_ids
            if eid in self.entities
        ]
    
    def find_by_component(self, component_type: str) -> List[Entity]:
        """根据组件类型查找实体"""
        results = []
        for entity in self.entities.values():
            if entity.has_component(component_type):
                results.append(entity)
        return results
    
    def update_all(self, delta_time: float):
        """更新所有实体"""
        for entity in self.entities.values():
            entity.update(delta_time)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取实体统计"""
        return {
            "total_entities": len(self.entities),
            "active_entities": sum(1 for e in self.entities.values() if e.active),
            "total_tags": len(self.entities_by_tag),
            "unique_names": len(self.entities_by_name)
        }


# ==================== 世界 ====================

class World:
    """
    世界
    
    包含所有实体、空间和物理
    """
    
    def __init__(self, name: str = "Silicon World"):
        self.name = name
        self.entity_manager = EntityManager()
        self.created_at = datetime.utcnow()
    
    def update(self, delta_time: float):
        """更新世界"""
        self.entity_manager.update_all(delta_time)
    
    def get_info(self) -> Dict[str, Any]:
        """获取世界信息"""
        return {
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "entities": self.entity_manager.get_statistics()
        }


# 使用示例
if __name__ == "__main__":
    # 创建世界
    world = World("硅基世界")
    
    # 创建实体
    print("创建实体...")
    agent = world.entity_manager.create_entity(
        name="三一",
        description="AI 助手"
    )
    
    # 添加组件
    agent.add_component(
        TransformComponent(
            position=Vector3(x=0, y=0, z=0)
        )
    )
    agent.add_component(PhysicsComponent(mass=1.0))
    agent.add_component(AIComponent(agent_id="did:silicon:agent:123"))
    agent.add_tag("agent")
    agent.add_tag("friendly")
    
    print(f"实体：{agent.name}")
    print(f"组件：{list(agent.components.keys())}")
    print(f"标签：{agent.tags}")
    
    # 查找实体
    print("\n查找实体...")
    agents = world.entity_manager.find_by_tag("agent")
    print(f"找到 {len(agents)} 个 Agent")
    
    # 更新世界
    print("\n更新世界...")
    world.update(0.016)  # 60 FPS
    
    # 获取统计
    stats = world.entity_manager.get_statistics()
    print(f"\n实体统计：{stats}")
    
    # 获取世界信息
    info = world.get_info()
    print(f"\n世界信息：{info}")
