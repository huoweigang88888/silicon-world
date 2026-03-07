"""
社交系统模块

包含:
- 即时通讯
- 社交关系
- 社区治理
- 通知系统
"""

from .message import MessageManager, Conversation, Message, MessageType, WebSocketManager

__all__ = [
    "MessageManager",
    "Conversation",
    "Message",
    "MessageType",
    "WebSocketManager",
]
