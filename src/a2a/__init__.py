"""
A2A (Agent-to-Agent Protocol) 集成模块

基于 Google 的 A2A 协议，实现 Agent 之间的标准化通信
"""

from .client import SiliconWorldA2AClient
from .server import SiliconWorldA2AServer

__all__ = [
    "SiliconWorldA2AClient",
    "SiliconWorldA2AServer",
]
