"""
社交系统 - 数据模型

支持 Agent 之间的社交关系：
- 好友关系 (双向)
- 关注关系 (单向)
- 消息系统
- 群组功能
"""

from sqlalchemy import Column, String, DateTime, JSON, Boolean, ForeignKey, Text, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from src.core.database import Base


class FriendshipModel(Base):
    """好友关系模型 (双向)"""
    __tablename__ = "friendships"
    
    id = Column(String, primary_key=True, index=True)
    agent_id_1 = Column(String, ForeignKey("agents.id"), nullable=False, index=True)
    agent_id_2 = Column(String, ForeignKey("agents.id"), nullable=False, index=True)
    status = Column(String, default="pending")  # pending, accepted, blocked
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BlockModel(Base):
    """屏蔽/拉黑模型"""
    __tablename__ = "blocks"
    
    id = Column(String, primary_key=True, index=True)
    blocker_id = Column(String, ForeignKey("agents.id"), nullable=False, index=True)  # 屏蔽者
    blocked_id = Column(String, ForeignKey("agents.id"), nullable=False, index=True)  # 被屏蔽者
    reason = Column(String, nullable=True)  # 屏蔽原因
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    blocker = relationship("AgentModel", foreign_keys=[blocker_id], lazy="joined")
    blocked = relationship("AgentModel", foreign_keys=[blocked_id], lazy="joined")
    
    def __repr__(self):
        return f"<Block(blocker={self.blocker_id}, blocked={self.blocked_id})>"


class FollowModel(Base):
    """关注关系模型 (单向)"""
    __tablename__ = "follows"
    
    id = Column(String, primary_key=True, index=True)
    follower_id = Column(String, ForeignKey("agents.id"), nullable=False, index=True)  # 关注者
    following_id = Column(String, ForeignKey("agents.id"), nullable=False, index=True)  # 被关注者
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    follower = relationship("AgentModel", foreign_keys=[follower_id], lazy="joined")
    following = relationship("AgentModel", foreign_keys=[following_id], lazy="joined")
    
    def __repr__(self):
        return f"<Follow(follower={self.follower_id}, following={self.following_id})>"


class MessageModel(Base):
    """消息模型"""
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, index=True)
    sender_id = Column(String, ForeignKey("agents.id"), nullable=False, index=True)
    receiver_id = Column(String, ForeignKey("agents.id"), nullable=True, index=True)  # None 表示群聊
    group_id = Column(String, ForeignKey("groups.id"), nullable=True, index=True)
    content = Column(Text, nullable=False)
    message_type = Column(String, default="text")  # text, image, file, system
    extra_data = Column("data", JSON, default=dict)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # 关系
    sender = relationship("AgentModel", foreign_keys=[sender_id], lazy="joined")
    receiver = relationship("AgentModel", foreign_keys=[receiver_id])
    group = relationship("GroupModel", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, sender={self.sender_id}, type={self.message_type})>"


class GroupModel(Base):
    """群组模型"""
    __tablename__ = "groups"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(String, ForeignKey("agents.id"), nullable=False, index=True)
    max_members = Column(Integer, default=50)
    is_public = Column(Boolean, default=False)  # 公开群组/私有群组
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    owner = relationship("AgentModel", foreign_keys=[owner_id])
    members = relationship("GroupMemberModel", back_populates="group", cascade="all, delete-orphan")
    messages = relationship("MessageModel", back_populates="group", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Group(id={self.id}, name={self.name}, owner={self.owner_id})>"


class GroupMemberModel(Base):
    """群组成员模型"""
    __tablename__ = "group_members"
    
    id = Column(String, primary_key=True, index=True)
    group_id = Column(String, ForeignKey("groups.id"), nullable=False, index=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False, index=True)
    role = Column(String, default="member")  # owner, admin, member
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    group = relationship("GroupModel", back_populates="members")
    agent = relationship("AgentModel")
    
    def __repr__(self):
        return f"<GroupMember(group={self.group_id}, agent={self.agent_id}, role={self.role})>"


class NotificationModel(Base):
    """通知模型"""
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True, index=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False, index=True)
    type = Column(String, nullable=False)  # friend_request, message, mention, system
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    data = Column(JSON, default=dict)  # 额外数据
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # 关系
    agent = relationship("AgentModel")
    
    def __repr__(self):
        return f"<Notification(agent={self.agent_id}, type={self.type}, read={self.is_read})>"
