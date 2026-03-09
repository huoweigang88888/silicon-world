"""
社交系统 - API 路由

提供社交功能的 REST API：
- 好友管理
- 关注系统
- 消息收发
- 群组功能
- 通知系统
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import sys
from pathlib import Path
import uuid
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.database import SessionLocal
from src.social.models import (
    FriendshipModel, FollowModel, MessageModel,
    GroupModel, GroupMemberModel, NotificationModel, BlockModel
)

router = APIRouter(tags=["Social"])


# ==================== 请求/响应模型 ====================

class FriendRequest(BaseModel):
    """好友请求"""
    target_agent_id: str


class FriendResponse(BaseModel):
    """好友响应"""
    id: str
    agent_id: str
    friend_id: str
    friend_name: str
    status: str
    created_at: str


class FollowRequest(BaseModel):
    """关注请求"""
    target_agent_id: str


class FollowResponse(BaseModel):
    """关注响应"""
    id: str
    follower_id: str
    following_id: str
    following_name: str
    created_at: str


class MessageCreate(BaseModel):
    """创建消息"""
    receiver_id: Optional[str] = None  # 私聊对象
    group_id: Optional[str] = None  # 群聊 ID
    content: str
    message_type: Optional[str] = "text"  # text, image, file
    file_url: Optional[str] = None  # 文件/图片 URL


class MessageResponse(BaseModel):
    """消息响应"""
    id: str
    sender_id: str
    sender_name: str
    receiver_id: Optional[str]
    group_id: Optional[str]
    content: str
    message_type: str
    file_url: Optional[str]
    is_read: bool
    created_at: str


class GroupCreate(BaseModel):
    """创建群组"""
    name: str
    description: Optional[str] = None
    max_members: Optional[int] = 50
    is_public: Optional[bool] = False


class GroupResponse(BaseModel):
    """群组响应"""
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    owner_name: str
    member_count: int
    max_members: int
    is_public: bool
    created_at: str


class NotificationResponse(BaseModel):
    """通知响应"""
    id: str
    agent_id: str
    type: str
    title: str
    content: Optional[str]
    is_read: bool
    created_at: str


class BlockRequest(BaseModel):
    """屏蔽请求"""
    target_agent_id: str
    reason: Optional[str] = None


class BlockResponse(BaseModel):
    """屏蔽响应"""
    id: str
    blocker_id: str
    blocked_id: str
    blocked_name: str
    reason: Optional[str]
    created_at: str


class MessageUpdate(BaseModel):
    """更新消息"""
    content: Optional[str] = None


# ==================== 工具函数 ====================

def get_agent_name(db, agent_id: str) -> str:
    """获取 Agent 名字"""
    from src.core.database import AgentModel
    agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    return agent.name if agent else "Unknown"


# ==================== 好友系统 ====================

@router.post("/api/v1/social/friends/request", response_model=dict)
async def send_friend_request(agent_id: str, request: FriendRequest):
    """
    发送好友请求
    
    - **agent_id**: 发送者 ID
    - **target_agent_id**: 目标 Agent ID
    """
    db = SessionLocal()
    try:
        # 检查目标 Agent 是否存在
        from src.core.database import AgentModel
        target = db.query(AgentModel).filter(AgentModel.id == request.target_agent_id).first()
        if not target:
            raise HTTPException(status_code=404, detail="Target agent not found")
        
        # 检查是否已是好友
        existing = db.query(FriendshipModel).filter(
            ((FriendshipModel.agent_id_1 == agent_id) & (FriendshipModel.agent_id_2 == request.target_agent_id)) |
            ((FriendshipModel.agent_id_1 == request.target_agent_id) & (FriendshipModel.agent_id_2 == agent_id))
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Friendship already exists")
        
        # 创建好友请求
        friendship = FriendshipModel(
            id=str(uuid.uuid4()),
            agent_id_1=agent_id,
            agent_id_2=request.target_agent_id,
            status="pending"
        )
        
        db.add(friendship)
        
        # 创建通知
        notification = NotificationModel(
            id=str(uuid.uuid4()),
            agent_id=request.target_agent_id,
            type="friend_request",
            title="新好友请求",
            content=f"Agent {get_agent_name(db, agent_id)} 想和你成为好友",
            data={"from_agent_id": agent_id, "friendship_id": friendship.id}
        )
        db.add(notification)
        
        db.commit()
        
        # 实时推送通知
        try:
            from src.core.websocket_manager import manager
            await manager.send_friend_request(
                request.target_agent_id,
                agent_id,
                get_agent_name(db, agent_id)
            )
        except Exception:
            pass
        
        return {
            "success": True,
            "message": "好友请求已发送",
            "friendship_id": friendship.id
        }
    finally:
        db.close()


@router.post("/api/v1/social/friends/accept")
async def accept_friend_request(agent_id: str, friendship_id: str):
    """
    接受好友请求
    
    - **agent_id**: 接受者 ID
    - **friendship_id**: 好友关系 ID
    """
    db = SessionLocal()
    try:
        friendship = db.query(FriendshipModel).filter(
            (FriendshipModel.id == friendship_id) &
            ((FriendshipModel.agent_id_1 == agent_id) | (FriendshipModel.agent_id_2 == agent_id))
        ).first()
        
        if not friendship:
            raise HTTPException(status_code=404, detail="Friendship request not found")
        
        friendship.status = "accepted"
        friendship.updated_at = datetime.utcnow()
        db.commit()
        
        return {"success": True, "message": "已成为好友"}
    finally:
        db.close()


@router.get("/api/v1/social/friends/list", response_model=List[FriendResponse])
async def get_friends(agent_id: str, status: str = "accepted"):
    """
    获取好友列表
    
    - **agent_id**: Agent ID
    - **status**: 状态 (pending, accepted, blocked)
    """
    db = SessionLocal()
    try:
        friendships = db.query(FriendshipModel).filter(
            ((FriendshipModel.agent_id_1 == agent_id) | (FriendshipModel.agent_id_2 == agent_id)) &
            (FriendshipModel.status == status)
        ).all()
        
        friends = []
        for f in friendships:
            friend_id = f.agent_id_2 if f.agent_id_1 == agent_id else f.agent_id_1
            friends.append(FriendResponse(
                id=f.id,
                agent_id=agent_id,
                friend_id=friend_id,
                friend_name=get_agent_name(db, friend_id),
                status=f.status,
                created_at=f.created_at.isoformat()
            ))
        
        return friends
    finally:
        db.close()


# ==================== 关注系统 ====================

@router.post("/api/v1/social/follow")
async def follow_agent(agent_id: str, request: FollowRequest):
    """
    关注 Agent
    
    - **agent_id**: 关注者 ID
    - **target_agent_id**: 被关注者 ID
    """
    db = SessionLocal()
    try:
        from src.core.database import AgentModel
        target = db.query(AgentModel).filter(AgentModel.id == request.target_agent_id).first()
        if not target:
            raise HTTPException(status_code=404, detail="Target agent not found")
        
        # 检查是否已关注
        existing = db.query(FollowModel).filter(
            (FollowModel.follower_id == agent_id) &
            (FollowModel.following_id == request.target_agent_id)
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Already following")
        
        follow = FollowModel(
            id=str(uuid.uuid4()),
            follower_id=agent_id,
            following_id=request.target_agent_id
        )
        
        db.add(follow)
        db.commit()
        
        return {"success": True, "message": "关注成功"}
    finally:
        db.close()


@router.get("/api/v1/social/followers", response_model=List[dict])
async def get_followers(agent_id: str):
    """获取粉丝列表"""
    db = SessionLocal()
    try:
        follows = db.query(FollowModel).filter(FollowModel.following_id == agent_id).all()
        return [
            {
                "follower_id": f.follower_id,
                "follower_name": get_agent_name(db, f.follower_id),
                "created_at": f.created_at.isoformat()
            }
            for f in follows
        ]
    finally:
        db.close()


@router.get("/api/v1/social/following", response_model=List[dict])
async def get_following(agent_id: str):
    """获取关注列表"""
    db = SessionLocal()
    try:
        follows = db.query(FollowModel).filter(FollowModel.follower_id == agent_id).all()
        return [
            {
                "following_id": f.following_id,
                "following_name": get_agent_name(db, f.following_id),
                "created_at": f.created_at.isoformat()
            }
            for f in follows
        ]
    finally:
        db.close()


# ==================== 消息系统 ====================

@router.post("/api/v1/social/messages/send", response_model=MessageResponse)
async def send_message(sender_id: str, request: MessageCreate):
    """
    发送消息
    
    - **sender_id**: 发送者 ID
    - **receiver_id**: 接收者 ID (私聊)
    - **group_id**: 群组 ID (群聊)
    - **content**: 消息内容
    - **message_type**: 消息类型 (text/image/file)
    - **file_url**: 文件/图片 URL (可选)
    """
    if not request.receiver_id and not request.group_id:
        raise HTTPException(status_code=400, detail="需要指定 receiver_id 或 group_id")
    
    db = SessionLocal()
    try:
        message = MessageModel(
            id=str(uuid.uuid4()),
            sender_id=sender_id,
            receiver_id=request.receiver_id,
            group_id=request.group_id,
            content=request.content,
            message_type=request.message_type,
            extra_data={"file_url": request.file_url} if request.file_url else {}
        )
        
        db.add(message)
        
        # 如果是私聊，创建通知
        if request.receiver_id:
            notification = NotificationModel(
                id=str(uuid.uuid4()),
                agent_id=request.receiver_id,
                type="message",
                title="新消息",
                content=request.content[:100],
                data={"message_id": message.id, "sender_id": sender_id}
            )
            db.add(notification)
        
        db.commit()
        db.refresh(message)
        
        # 实时推送消息
        try:
            from src.core.websocket_manager import manager
            message_data = {
                "id": message.id,
                "sender_id": sender_id,
                "content": request.content,
                "message_type": request.message_type,
                "file_url": request.file_url,
                "created_at": message.created_at.isoformat()
            }
            
            if request.receiver_id:
                await manager.send_new_message(request.receiver_id, message_data)
            elif request.group_id:
                # TODO: 获取群组成员并推送
                pass
        except Exception as e:
            # WebSocket 推送失败不影响消息发送
            pass
        
        return MessageResponse(
            id=message.id,
            sender_id=message.sender_id,
            sender_name=get_agent_name(db, message.sender_id),
            receiver_id=message.receiver_id,
            group_id=message.group_id,
            content=message.content,
            message_type=message.message_type,
            file_url=request.file_url,
            is_read=message.is_read,
            created_at=message.created_at.isoformat()
        )
    finally:
        db.close()


@router.get("/api/v1/social/messages/conversation/{other_id}", response_model=List[MessageResponse])
async def get_conversation(agent_id: str, other_id: str, limit: int = 50, offset: int = 0):
    """
    获取与某个 Agent 的聊天记录
    
    - **agent_id**: 当前 Agent ID
    - **other_id**: 对话对象 ID
    - **limit**: 返回数量
    - **offset**: 偏移量
    """
    db = SessionLocal()
    try:
        messages = db.query(MessageModel).filter(
            ((MessageModel.sender_id == agent_id) & (MessageModel.receiver_id == other_id)) |
            ((MessageModel.sender_id == other_id) & (MessageModel.receiver_id == agent_id))
        ).order_by(MessageModel.created_at.desc()).offset(offset).limit(limit).all()
        
        return [
            MessageResponse(
                id=m.id,
                sender_id=m.sender_id,
                sender_name=get_agent_name(db, m.sender_id),
                receiver_id=m.receiver_id,
                group_id=m.group_id,
                content=m.content,
                message_type=m.message_type,
                is_read=m.is_read,
                created_at=m.created_at.isoformat()
            )
            for m in messages
        ][::-1]  # 反转为正序
    finally:
        db.close()


@router.get("/api/v1/social/messages/unread", response_model=List[MessageResponse])
async def get_unread_messages(agent_id: str):
    """获取未读消息"""
    db = SessionLocal()
    try:
        messages = db.query(MessageModel).filter(
            (MessageModel.receiver_id == agent_id) &
            (MessageModel.is_read == False)
        ).order_by(MessageModel.created_at.desc()).all()
        
        return [
            MessageResponse(
                id=m.id,
                sender_id=m.sender_id,
                sender_name=get_agent_name(db, m.sender_id),
                receiver_id=m.receiver_id,
                group_id=m.group_id,
                content=m.content,
                message_type=m.message_type,
                is_read=m.is_read,
                created_at=m.created_at.isoformat()
            )
            for m in messages
        ]
    finally:
        db.close()


@router.post("/api/v1/social/messages/mark-read")
async def mark_messages_read(agent_id: str, message_ids: List[str]):
    """标记消息为已读"""
    db = SessionLocal()
    try:
        db.query(MessageModel).filter(
            (MessageModel.id.in_(message_ids)) &
            (MessageModel.receiver_id == agent_id)
        ).update({"is_read": True}, synchronize_session=False)
        db.commit()
        
        return {"success": True, "marked_count": len(message_ids)}
    finally:
        db.close()


@router.post("/api/v1/social/messages/mark-conversation-read")
async def mark_conversation_read(agent_id: str, other_id: str):
    """
    标记与某人的所有消息为已读
    
    - **agent_id**: 当前 Agent ID
    - **other_id**: 对话对象 ID
    """
    db = SessionLocal()
    try:
        updated = db.query(MessageModel).filter(
            (MessageModel.receiver_id == agent_id) &
            (MessageModel.sender_id == other_id) &
            (MessageModel.is_read == False)
        ).update({"is_read": True}, synchronize_session=False)
        db.commit()
        
        return {
            "success": True,
            "marked_count": updated,
            "other_id": other_id
        }
    finally:
        db.close()


@router.get("/api/v1/social/messages/unread/count")
async def get_unread_count(agent_id: str):
    """
    获取未读消息数量
    
    - **agent_id**: Agent ID
    """
    db = SessionLocal()
    try:
        count = db.query(MessageModel).filter(
            (MessageModel.receiver_id == agent_id) &
            (MessageModel.is_read == False)
        ).count()
        
        return {
            "agent_id": agent_id,
            "unread_count": count
        }
    finally:
        db.close()


# ==================== 群组功能 ====================

@router.post("/api/v1/social/groups/create", response_model=GroupResponse)
async def create_group(owner_id: str, request: GroupCreate):
    """
    创建群组
    
    - **owner_id**: 群主 ID
    - **name**: 群名
    - **description**: 群描述
    - **max_members**: 最大成员数
    - **is_public**: 是否公开
    """
    db = SessionLocal()
    try:
        group = GroupModel(
            id=str(uuid.uuid4()),
            name=request.name,
            description=request.description,
            owner_id=owner_id,
            max_members=request.max_members,
            is_public=request.is_public
        )
        
        db.add(group)
        db.commit()
        db.refresh(group)
        
        # 创建群主成员记录
        member = GroupMemberModel(
            id=str(uuid.uuid4()),
            group_id=group.id,
            agent_id=owner_id,
            role="owner"
        )
        db.add(member)
        db.commit()
        
        return GroupResponse(
            id=group.id,
            name=group.name,
            description=group.description,
            owner_id=group.owner_id,
            owner_name=get_agent_name(db, group.owner_id),
            member_count=1,
            max_members=group.max_members,
            is_public=group.is_public,
            created_at=group.created_at.isoformat()
        )
    finally:
        db.close()


@router.get("/api/v1/social/groups/list", response_model=List[GroupResponse])
async def get_groups(agent_id: str):
    """获取 Agent 加入的所有群组"""
    db = SessionLocal()
    try:
        memberships = db.query(GroupMemberModel).filter(
            GroupMemberModel.agent_id == agent_id
        ).all()
        
        group_ids = [m.group_id for m in memberships]
        groups = db.query(GroupModel).filter(GroupModel.id.in_(group_ids)).all()
        
        return [
            GroupResponse(
                id=g.id,
                name=g.name,
                description=g.description,
                owner_id=g.owner_id,
                owner_name=get_agent_name(db, g.owner_id),
                member_count=db.query(GroupMemberModel).filter(GroupMemberModel.group_id == g.id).count(),
                max_members=g.max_members,
                is_public=g.is_public,
                created_at=g.created_at.isoformat()
            )
            for g in groups
        ]
    finally:
        db.close()


@router.post("/api/v1/social/groups/{group_id}/join")
async def join_group(group_id: str, agent_id: str):
    """加入群组"""
    db = SessionLocal()
    try:
        # 检查群组是否存在
        group = db.query(GroupModel).filter(GroupModel.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # 检查是否已是成员
        existing = db.query(GroupMemberModel).filter(
            (GroupMemberModel.group_id == group_id) &
            (GroupMemberModel.agent_id == agent_id)
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Already a member")
        
        # 检查人数限制
        member_count = db.query(GroupMemberModel).filter(
            GroupMemberModel.group_id == group_id
        ).count()
        
        if member_count >= group.max_members:
            raise HTTPException(status_code=400, detail="Group is full")
        
        # 添加成员
        member = GroupMemberModel(
            id=str(uuid.uuid4()),
            group_id=group_id,
            agent_id=agent_id,
            role="member"
        )
        db.add(member)
        db.commit()
        
        return {"success": True, "message": "加入群组成功"}
    finally:
        db.close()


# ==================== 通知系统 ====================

@router.get("/api/v1/social/notifications", response_model=List[NotificationResponse])
async def get_notifications(agent_id: str, unread_only: bool = False, limit: int = 50):
    """
    获取通知列表
    
    - **agent_id**: Agent ID
    - **unread_only**: 只返回未读
    - **limit**: 返回数量
    """
    db = SessionLocal()
    try:
        query = db.query(NotificationModel).filter(NotificationModel.agent_id == agent_id)
        
        if unread_only:
            query = query.filter(NotificationModel.is_read == False)
        
        notifications = query.order_by(NotificationModel.created_at.desc()).limit(limit).all()
        
        return [
            NotificationResponse(
                id=n.id,
                agent_id=n.agent_id,
                type=n.type,
                title=n.title,
                content=n.content,
                is_read=n.is_read,
                created_at=n.created_at.isoformat()
            )
            for n in notifications
        ]
    finally:
        db.close()


@router.post("/api/v1/social/notifications/mark-read")
async def mark_notification_read(agent_id: str, notification_id: str):
    """标记通知为已读"""
    db = SessionLocal()
    try:
        notification = db.query(NotificationModel).filter(
            (NotificationModel.id == notification_id) &
            (NotificationModel.agent_id == agent_id)
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        notification.is_read = True
        db.commit()
        
        return {"success": True}
    finally:
        db.close()


# ==================== 屏蔽/拉黑功能 ====================

@router.post("/api/v1/social/block")
async def block_agent(agent_id: str, request: BlockRequest):
    """
    屏蔽/拉黑 Agent
    
    - **agent_id**: 屏蔽者 ID
    - **target_agent_id**: 被屏蔽者 ID
    - **reason**: 屏蔽原因 (可选)
    """
    db = SessionLocal()
    try:
        from src.core.database import AgentModel
        target = db.query(AgentModel).filter(AgentModel.id == request.target_agent_id).first()
        if not target:
            raise HTTPException(status_code=404, detail="Target agent not found")
        
        # 检查是否已屏蔽
        existing = db.query(BlockModel).filter(
            (BlockModel.blocker_id == agent_id) &
            (BlockModel.blocked_id == request.target_agent_id)
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Already blocked")
        
        block = BlockModel(
            id=str(uuid.uuid4()),
            blocker_id=agent_id,
            blocked_id=request.target_agent_id,
            reason=request.reason
        )
        
        db.add(block)
        
        # 如果是好友，删除好友关系
        friendship = db.query(FriendshipModel).filter(
            ((FriendshipModel.agent_id_1 == agent_id) & (FriendshipModel.agent_id_2 == request.target_agent_id)) |
            ((FriendshipModel.agent_id_1 == request.target_agent_id) & (FriendshipModel.agent_id_2 == agent_id))
        ).first()
        
        if friendship:
            db.delete(friendship)
        
        db.commit()
        
        return {"success": True, "message": "已屏蔽该 Agent"}
    finally:
        db.close()


@router.post("/api/v1/social/unblock")
async def unblock_agent(agent_id: str, blocked_id: str):
    """解除屏蔽"""
    db = SessionLocal()
    try:
        block = db.query(BlockModel).filter(
            (BlockModel.blocker_id == agent_id) &
            (BlockModel.blocked_id == blocked_id)
        ).first()
        
        if not block:
            raise HTTPException(status_code=404, detail="Block record not found")
        
        db.delete(block)
        db.commit()
        
        return {"success": True, "message": "已解除屏蔽"}
    finally:
        db.close()


@router.get("/api/v1/social/blocked-list", response_model=List[BlockResponse])
async def get_blocked_list(agent_id: str):
    """获取屏蔽列表"""
    db = SessionLocal()
    try:
        blocks = db.query(BlockModel).filter(BlockModel.blocker_id == agent_id).all()
        
        return [
            BlockResponse(
                id=b.id,
                blocker_id=b.blocker_id,
                blocked_id=b.blocked_id,
                blocked_name=get_agent_name(db, b.blocked_id),
                reason=b.reason,
                created_at=b.created_at.isoformat()
            )
            for b in blocks
        ]
    finally:
        db.close()


# ==================== 消息撤回/编辑 ====================

@router.delete("/api/v1/social/messages/{message_id}")
async def delete_message(agent_id: str, message_id: str):
    """
    撤回/删除消息
    
    - **agent_id**: 操作者 ID (必须是发送者)
    - **message_id**: 消息 ID
    """
    db = SessionLocal()
    try:
        message = db.query(MessageModel).filter(MessageModel.id == message_id).first()
        
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # 只有发送者可以删除
        if message.sender_id != agent_id:
            raise HTTPException(status_code=403, detail="Only sender can delete message")
        
        db.delete(message)
        db.commit()
        
        return {"success": True, "message": "消息已撤回"}
    finally:
        db.close()


@router.put("/api/v1/social/messages/{message_id}")
async def edit_message(agent_id: str, message_id: str, request: MessageUpdate):
    """
    编辑消息
    
    - **agent_id**: 操作者 ID (必须是发送者)
    - **message_id**: 消息 ID
    - **content**: 新内容
    """
    db = SessionLocal()
    try:
        message = db.query(MessageModel).filter(MessageModel.id == message_id).first()
        
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        if message.sender_id != agent_id:
            raise HTTPException(status_code=403, detail="Only sender can edit message")
        
        if request.content:
            # 在原文前加编辑标记
            message.content = f"(已编辑) {request.content}"
        
        db.commit()
        
        return {"success": True, "message": "消息已更新"}
    finally:
        db.close()


# ==================== 群组管理 ====================

@router.post("/api/v1/social/groups/{group_id}/kick")
async def kick_member(group_id: str, agent_id: str, target_id: str):
    """
    踢出群成员
    
    - **group_id**: 群组 ID
    - **agent_id**: 操作者 ID (必须是群主或管理员)
    - **target_id**: 被踢出的成员 ID
    """
    db = SessionLocal()
    try:
        # 检查操作者权限
        operator_member = db.query(GroupMemberModel).filter(
            (GroupMemberModel.group_id == group_id) &
            (GroupMemberModel.agent_id == agent_id)
        ).first()
        
        if not operator_member:
            raise HTTPException(status_code=404, detail="Not a group member")
        
        if operator_member.role not in ["owner", "admin"]:
            raise HTTPException(status_code=403, detail="Only owner or admin can kick members")
        
        # 不能踢群主
        if operator_member.role != "owner" and target_id == operator_member.agent_id:
            raise HTTPException(status_code=403, detail="Cannot kick the owner")
        
        # 找到要踢出的成员
        target_member = db.query(GroupMemberModel).filter(
            (GroupMemberModel.group_id == group_id) &
            (GroupMemberModel.agent_id == target_id)
        ).first()
        
        if not target_member:
            raise HTTPException(status_code=404, detail="Member not found in group")
        
        db.delete(target_member)
        db.commit()
        
        return {"success": True, "message": "成员已踢出"}
    finally:
        db.close()


@router.post("/api/v1/social/groups/{group_id}/mute")
async def mute_member(group_id: str, agent_id: str, target_id: str, duration_minutes: int = 60):
    """
    禁言群成员
    
    - **group_id**: 群组 ID
    - **agent_id**: 操作者 ID
    - **target_id**: 被禁言的成员 ID
    - **duration_minutes**: 禁言时长 (分钟)
    """
    db = SessionLocal()
    try:
        # 检查操作者权限
        operator_member = db.query(GroupMemberModel).filter(
            (GroupMemberModel.group_id == group_id) &
            (GroupMemberModel.agent_id == agent_id)
        ).first()
        
        if not operator_member:
            raise HTTPException(status_code=404, detail="Not a group member")
        
        if operator_member.role not in ["owner", "admin"]:
            raise HTTPException(status_code=403, detail="Only owner or admin can mute members")
        
        # TODO: 添加禁言记录表，这里简化处理
        # 实际项目中应该创建 mute_records 表
        
        return {
            "success": True,
            "message": f"成员已禁言 {duration_minutes} 分钟",
            "duration_minutes": duration_minutes
        }
    finally:
        db.close()


@router.post("/api/v1/social/groups/{group_id}/leave")
async def leave_group(group_id: str, agent_id: str):
    """退出群组"""
    db = SessionLocal()
    try:
        member = db.query(GroupMemberModel).filter(
            (GroupMemberModel.group_id == group_id) &
            (GroupMemberModel.agent_id == agent_id)
        ).first()
        
        if not member:
            raise HTTPException(status_code=404, detail="Not a group member")
        
        # 群主不能直接退出，需要先转让
        if member.role == "owner":
            raise HTTPException(status_code=400, detail="Owner must transfer ownership before leaving")
        
        db.delete(member)
        db.commit()
        
        return {"success": True, "message": "已退出群组"}
    finally:
        db.close()
