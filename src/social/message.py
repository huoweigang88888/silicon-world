"""
即时通讯系统

实时聊天和消息管理
"""

from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import uuid


# ==================== 消息类型 ====================

class MessageType(str, Enum):
    """消息类型"""
    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    VIDEO = "video"
    FILE = "file"
    SYSTEM = "system"


class MessageStatus(str, Enum):
    """消息状态"""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


# ==================== 消息模型 ====================

class Message(BaseModel):
    """消息"""
    id: str
    conversation_id: str
    sender_id: str
    content: str
    message_type: MessageType = MessageType.TEXT
    metadata: Dict[str, Any] = {}
    status: MessageStatus = MessageStatus.SENT
    timestamp: datetime = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)
    
    def mark_as_read(self):
        """标记为已读"""
        self.status = MessageStatus.READ
    
    def mark_as_delivered(self):
        """标记为已送达"""
        self.status = MessageStatus.DELIVERED


# ==================== 会话模型 ====================

class ConversationType(str, Enum):
    """会话类型"""
    PRIVATE = "private"
    GROUP = "group"
    CHANNEL = "channel"


class Conversation(BaseModel):
    """聊天会话"""
    id: str
    name: Optional[str] = None
    conversation_type: ConversationType
    participants: Set[str] = set()
    creator_id: str
    created_at: datetime = None
    last_message_id: Optional[str] = None
    last_message_time: Optional[datetime] = None
    message_count: int = 0
    metadata: Dict[str, Any] = {}
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow()
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        super().__init__(**data)
    
    def add_participant(self, participant_id: str):
        """添加参与者"""
        self.participants.add(participant_id)
    
    def remove_participant(self, participant_id: str):
        """移除参与者"""
        self.participants.discard(participant_id)
    
    def is_member(self, participant_id: str) -> bool:
        """检查是否是成员"""
        return participant_id in self.participants
    
    def update_last_message(self, message_id: str):
        """更新最后一条消息"""
        self.last_message_id = message_id
        self.last_message_time = datetime.utcnow()
        self.message_count += 1


# ==================== 消息管理器 ====================

class MessageManager:
    """
    消息管理器
    
    管理消息的发送、存储和检索
    """
    
    def __init__(self):
        self.messages: Dict[str, Message] = {}
        self.conversations: Dict[str, Conversation] = {}
        self.conversation_messages: Dict[str, List[str]] = {}  # conversation_id -> [message_ids]
        self.user_conversations: Dict[str, Set[str]] = {}  # user_id -> {conversation_ids}
    
    def create_conversation(
        self,
        conversation_type: ConversationType,
        creator_id: str,
        participants: List[str] = None,
        name: str = None
    ) -> Conversation:
        """
        创建会话
        
        Args:
            conversation_type: 会话类型
            creator_id: 创建者 ID
            participants: 参与者列表
            name: 会话名称
        
        Returns:
            Conversation
        """
        conversation = Conversation(
            conversation_type=conversation_type,
            creator_id=creator_id,
            participants=set(participants or [creator_id]),
            name=name
        )
        
        self.conversations[conversation.id] = conversation
        self.conversation_messages[conversation.id] = []
        
        # 更新用户会话索引
        for participant in conversation.participants:
            if participant not in self.user_conversations:
                self.user_conversations[participant] = set()
            self.user_conversations[participant].add(conversation.id)
        
        return conversation
    
    def send_message(
        self,
        conversation_id: str,
        sender_id: str,
        content: str,
        message_type: MessageType = MessageType.TEXT,
        metadata: Dict[str, Any] = None
    ) -> Message:
        """
        发送消息
        
        Args:
            conversation_id: 会话 ID
            sender_id: 发送者 ID
            content: 消息内容
            message_type: 消息类型
            metadata: 元数据
        
        Returns:
            Message
        """
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            raise ValueError("会话不存在")
        
        if not conversation.is_member(sender_id):
            raise ValueError("不是会话成员")
        
        # 创建消息
        message = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
            message_type=message_type,
            metadata=metadata or {}
        )
        
        # 存储消息
        self.messages[message.id] = message
        
        # 更新会话消息列表
        if conversation_id not in self.conversation_messages:
            self.conversation_messages[conversation_id] = []
        self.conversation_messages[conversation_id].append(message.id)
        
        # 更新会话最后消息
        conversation.update_last_message(message.id)
        
        return message
    
    def get_messages(
        self,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """
        获取消息历史
        
        Args:
            conversation_id: 会话 ID
            limit: 返回数量
            offset: 偏移量
        
        Returns:
            消息列表
        """
        message_ids = self.conversation_messages.get(conversation_id, [])
        
        # 分页
        paginated_ids = message_ids[offset:offset + limit]
        
        messages = [
            self.messages[mid]
            for mid in paginated_ids
            if mid in self.messages
        ]
        
        return messages
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """获取会话"""
        return self.conversations.get(conversation_id)
    
    def get_user_conversations(self, user_id: str) -> List[Conversation]:
        """获取用户的所有会话"""
        conversation_ids = self.user_conversations.get(user_id, set())
        return [
            self.conversations[cid]
            for cid in conversation_ids
            if cid in self.conversations
        ]
    
    def mark_message_as_read(self, message_id: str):
        """标记消息为已读"""
        message = self.messages.get(message_id)
        if message:
            message.mark_as_read()
    
    def mark_conversation_as_read(self, conversation_id: str, user_id: str):
        """标记会话所有消息为已读"""
        message_ids = self.conversation_messages.get(conversation_id, [])
        for mid in message_ids:
            message = self.messages.get(mid)
            if message and message.sender_id != user_id:
                message.mark_as_read()
    
    def get_unread_count(self, conversation_id: str, user_id: str) -> int:
        """获取未读消息数"""
        message_ids = self.conversation_messages.get(conversation_id, [])
        unread = 0
        
        for mid in message_ids:
            message = self.messages.get(mid)
            if message and message.sender_id != user_id and message.status != MessageStatus.READ:
                unread += 1
        
        return unread
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_conversations": len(self.conversations),
            "total_messages": len(self.messages),
            "total_users": len(self.user_conversations),
            "private_conversations": sum(1 for c in self.conversations.values() if c.conversation_type == ConversationType.PRIVATE),
            "group_conversations": sum(1 for c in self.conversations.values() if c.conversation_type == ConversationType.GROUP)
        }


# ==================== WebSocket 管理器 ====================

class WebSocketManager:
    """
    WebSocket 管理器
    
    管理实时连接
    """
    
    def __init__(self):
        self.connections: Dict[str, Set[str]] = {}  # user_id -> {connection_ids}
        self.connection_info: Dict[str, Dict[str, Any]] = {}  # connection_id -> info
    
    def add_connection(self, user_id: str, connection_id: str, info: Dict[str, Any] = None):
        """添加连接"""
        if user_id not in self.connections:
            self.connections[user_id] = set()
        self.connections[user_id].add(connection_id)
        self.connection_info[connection_id] = info or {}
    
    def remove_connection(self, connection_id: str):
        """移除连接"""
        for user_id, conn_ids in self.connections.items():
            if connection_id in conn_ids:
                conn_ids.remove(connection_id)
                if connection_id in self.connection_info:
                    del self.connection_info[connection_id]
                break
    
    def get_user_connections(self, user_id: str) -> Set[str]:
        """获取用户的连接"""
        return self.connections.get(user_id, set())
    
    def is_online(self, user_id: str) -> bool:
        """检查用户是否在线"""
        return bool(self.connections.get(user_id))
    
    def get_online_users(self) -> List[str]:
        """获取在线用户列表"""
        return [uid for uid, conns in self.connections.items() if conns]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计"""
        return {
            "total_connections": sum(len(conns) for conns in self.connections.values()),
            "online_users": len([uid for uid, conns in self.connections.items() if conns]),
            "total_users": len(self.connections)
        }


# 使用示例
if __name__ == "__main__":
    # 创建消息管理器
    msg_mgr = MessageManager()
    
    # 创建私聊会话
    print("创建私聊会话...")
    conv1 = msg_mgr.create_conversation(
        conversation_type=ConversationType.PRIVATE,
        creator_id="user_1",
        participants=["user_1", "user_2"]
    )
    print(f"会话 ID: {conv1.id}")
    print(f"参与者：{conv1.participants}")
    
    # 发送消息
    print("\n发送消息...")
    msg1 = msg_mgr.send_message(
        conversation_id=conv1.id,
        sender_id="user_1",
        content="你好！",
        message_type=MessageType.TEXT
    )
    print(f"消息：{msg1.content}")
    
    msg2 = msg_mgr.send_message(
        conversation_id=conv1.id,
        sender_id="user_2",
        content="你好啊！",
        message_type=MessageType.TEXT
    )
    print(f"回复：{msg2.content}")
    
    # 获取消息历史
    print("\n消息历史:")
    messages = msg_mgr.get_messages(conv1.id)
    for msg in messages:
        print(f"  {msg.sender_id}: {msg.content}")
    
    # 获取用户会话
    print("\nuser_1 的会话:")
    conversations = msg_mgr.get_user_conversations("user_1")
    for conv in conversations:
        print(f"  会话：{conv.id}, 消息数：{conv.message_count}")
    
    # 获取统计
    print("\n统计信息:")
    stats = msg_mgr.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
