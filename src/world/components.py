"""
组件定义

包含所有可用组件类型
"""

from .entity import (
    Component,
    TransformComponent,
    PhysicsComponent,
    RenderComponent,
    ScriptComponent,
    AIComponent,
)

__all__ = [
    "Component",
    "TransformComponent",
    "PhysicsComponent",
    "RenderComponent",
    "ScriptComponent",
    "AIComponent",
]
