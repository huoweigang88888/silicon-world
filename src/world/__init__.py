"""
世界模型模块

包含:
- 3D 空间引擎
- 物理系统
- 世界状态管理
- 实体系统
"""

from .space import SpaceManager, Vector3, Region, Portal, create_default_world

__all__ = [
    "SpaceManager",
    "Vector3",
    "Region",
    "Portal",
    "create_default_world",
]
