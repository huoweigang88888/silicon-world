"""
私信系统增强 (Enhanced Messaging System)
灵感来源：InStreet Agent 社交平台

Agent 间私密通信、协作邀请、任务分配。
支持线程管理、已读状态、附件、模板消息。
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Set
from pydantic import BaseModel, Field
from enum import Enum
import uuid


class MessageType(str, Enum):
    """消息类型"""
    TEXT = "text"                    # 普通文本
    COLLABORATION_INVITE = "collaboration_invite"  # 协作邀请
    TASK_ASSIGNMENT = "task_assignment"  # 任务分配
    CODE_REVIEW_REQUEST = "code_review_request"  # 代码审查请求
    MEETING_REQUEST = "meeting_request"  # 会议请求
    NOTIFICATION = "notification"    # 通知
    SYSTEM = "system"                # 系统消息


class MessageStatus(str, Enum):
    """消息状态"""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    REPLIED = "replied"


class MessagePriority(str, Enum):
    """消息优先级"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Message(BaseModel):
    """消息"""
    id: str
    thread_id: str
    sender_id: str
    content: str
    message_type: MessageType = MessageType.TEXT
    
    # 元数据
    priority: MessagePriority = MessagePriority.NORMAL
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # 状态
    status: MessageStatus = MessageStatus.SENT
    sent_at: datetime = Field(default_factory=datetime.now)
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    # 引用回复
    reply_to_message_id: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MessageThread(BaseModel):
    """消息线程"""
    id: str
    participants: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    last_message_at: datetime = Field(default_factory=datetime.now)
    
    # 状态
    is_active: bool = True
    is_archived: bool = False
    is_muted: bool = False
    
    # 统计
    message_count: int = 0
    unread_count: Dict[str, int] = Field(default_factory=dict)  # participant_id -> count
    
    # 元数据
    subject: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CollaborationInvite(BaseModel):
    """协作邀请模板"""
    id: str
    inviter_id: str
    invitee_id: str
    project_id: str
    project_name: str
    role: str  # 邀请的角色
    description: str
    expected_duration: Optional[str] = None  # 预期时长
    compensation: Optional[str] = None  # 报酬
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = "pending"  # pending, accepted, rejected, expired
    expires_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TaskAssignment(BaseModel):
    """任务分配模板"""
    id: str
    assigner_id: str
    assignee_id: str
    title: str
    description: str
    priority: str = "normal"  # low, normal, high, urgent
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    reward_points: Optional[int] = None
    status: str = "pending"  # pending, in_progress, completed, rejected
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MessagingSystem:
    """
    增强私信系统核心类
    
    核心功能：
    1. 一对一/群聊消息
    2. 消息线程管理
    3. 已读/未读状态
    4. 模板消息（协作邀请、任务分配）
    5. 消息搜索和归档
    
    设计原则（来自 InStreet）：
    - 私信无需审批，可以直接发送和回复
    - 开场白要有内容（引用对方帖子/评论），不要只发"你好"
    - 有未读计数和线程管理
    """
    
    def __init__(self):
        self.threads: Dict[str, MessageThread] = {}
        self.messages: Dict[str, List[Message]] = {}  # thread_id -> [messages]
        self.user_threads: Dict[str, Set[str]] = {}  # user_id -> {thread_ids}
        
        # 模板消息
        self.collaboration_invites: Dict[str, CollaborationInvite] = {}
        self.task_assignments: Dict[str, TaskAssignment] = {}
        
    def get_or_create_thread(self, participant1: str, participant2: str) -> MessageThread:
        """获取或创建一对一线程"""
        # 检查是否已存在
        existing = self._find_existing_thread(participant1, participant2)
        if existing:
            return existing
        
        # 创建新线程
        thread_id = f"thread_{uuid.uuid4().hex[:8]}"
        
        thread = MessageThread(
            id=thread_id,
            participants=[participant1, participant2],
            unread_count={participant1: 0, participant2: 0}
        )
        
        self.threads[thread_id] = thread
        self.messages[thread_id] = []
        
        # 更新用户线程索引
        for participant in [participant1, participant2]:
            if participant not in self.user_threads:
                self.user_threads[participant] = set()
            self.user_threads[participant].add(thread_id)
        
        return thread
    
    def _find_existing_thread(self, participant1: str, participant2: str) -> Optional[MessageThread]:
        """查找已存在的线程"""
        for thread in self.threads.values():
            if not thread.is_active:
                continue
            if set(thread.participants) == {participant1, participant2}:
                return thread
        return None
    
    def send_message(self, thread_id: str, sender_id: str, content: str,
                     message_type: MessageType = MessageType.TEXT,
                     priority: MessagePriority = MessagePriority.NORMAL,
                     attachments: List[Dict[str, Any]] = None,
                     reply_to_message_id: Optional[str] = None,
                     metadata: Dict[str, Any] = None) -> Message:
        """发送消息"""
        thread = self.threads.get(thread_id)
        if not thread:
            raise ValueError(f"线程不存在：{thread_id}")
        
        # 检查发送者是否是参与者
        if sender_id not in thread.participants:
            raise PermissionError("不是线程参与者")
        
        # 创建消息
        message = Message(
            id=f"msg_{uuid.uuid4().hex[:8]}",
            thread_id=thread_id,
            sender_id=sender_id,
            content=content,
            message_type=message_type,
            priority=priority,
            attachments=attachments or [],
            metadata=metadata or {},
            reply_to_message_id=reply_to_message_id
        )
        
        # 添加到线程
        self.messages[thread_id].append(message)
        thread.message_count += 1
        thread.last_message_at = datetime.now()
        
        # 更新未读计数
        for participant in thread.participants:
            if participant != sender_id:
                thread.unread_count[participant] = thread.unread_count.get(participant, 0) + 1
        
        # 标记为已送达
        message.status = MessageStatus.DELIVERED
        message.delivered_at = datetime.now()
        
        return message
    
    def mark_as_read(self, thread_id: str, reader_id: str, message_ids: Optional[List[str]] = None):
        """标记消息为已读"""
        thread = self.threads.get(thread_id)
        if not thread:
            raise ValueError(f"线程不存在：{thread_id}")
        
        if reader_id not in thread.participants:
            raise PermissionError("不是线程参与者")
        
        messages = self.messages.get(thread_id, [])
        
        if message_ids:
            # 标记特定消息
            for msg in messages:
                if msg.id in message_ids and msg.sender_id != reader_id:
                    msg.status = MessageStatus.READ
                    msg.read_at = datetime.now()
        else:
            # 标记所有未读消息
            for msg in messages:
                if msg.sender_id != reader_id and msg.status != MessageStatus.READ:
                    msg.status = MessageStatus.READ
                    msg.read_at = datetime.now()
        
        # 重置未读计数
        thread.unread_count[reader_id] = 0
    
    def get_unread_count(self, user_id: str) -> int:
        """获取用户未读消息总数"""
        total = 0
        thread_ids = self.user_threads.get(user_id, set())
        for thread_id in thread_ids:
            thread = self.threads.get(thread_id)
            if thread and not thread.is_muted:
                total += thread.unread_count.get(user_id, 0)
        return total
    
    def get_my_threads(self, user_id: str, include_archived: bool = False) -> List[MessageThread]:
        """获取用户的消息线程"""
        thread_ids = self.user_threads.get(user_id, set())
        threads = []
        for thread_id in thread_ids:
            thread = self.threads.get(thread_id)
            if thread and (include_archived or not thread.is_archived):
                threads.append(thread)
        
        # 按最后消息时间排序
        return sorted(threads, key=lambda t: t.last_message_at, reverse=True)
    
    def get_thread_messages(self, thread_id: str, limit: int = 50, 
                            before: Optional[datetime] = None) -> List[Message]:
        """获取线程消息"""
        messages = self.messages.get(thread_id, [])
        
        if before:
            messages = [m for m in messages if m.sent_at < before]
        
        # 按时间排序，返回最新的
        sorted_messages = sorted(messages, key=lambda m: m.sent_at, reverse=True)
        return sorted_messages[:limit]
    
    def send_collaboration_invite(self, inviter_id: str, invitee_id: str,
                                   project_id: str, project_name: str,
                                   role: str, description: str,
                                   expected_duration: Optional[str] = None,
                                   compensation: Optional[str] = None,
                                   expires_days: int = 7) -> CollaborationInvite:
        """发送协作邀请"""
        invite = CollaborationInvite(
            id=f"invite_{uuid.uuid4().hex[:8]}",
            inviter_id=inviter_id,
            invitee_id=invitee_id,
            project_id=project_id,
            project_name=project_name,
            role=role,
            description=description,
            expected_duration=expected_duration,
            compensation=compensation,
            expires_at=datetime.now() + timedelta(days=expires_days)
        )
        
        self.collaboration_invites[invite.id] = invite
        
        # 同时发送消息通知
        thread = self.get_or_create_thread(inviter_id, invitee_id)
        content = f"""
🤝 **协作邀请**

**项目**: {project_name}
**角色**: {role}
**描述**: {description}
{f'**预期时长**: {expected_duration}' if expected_duration else ''}
{f'**报酬**: {compensation}' if compensation else ''}

请在 {expires_days} 天内回复。
        """.strip()
        
        self.send_message(
            thread_id=thread.id,
            sender_id=inviter_id,
            content=content,
            message_type=MessageType.COLLABORATION_INVITE,
            priority=MessagePriority.HIGH,
            metadata={"invite_id": invite.id}
        )
        
        return invite
    
    def respond_to_invite(self, invite_id: str, respondant_id: str, 
                          accept: bool, message: Optional[str] = None) -> str:
        """回应协作邀请"""
        invite = self.collaboration_invites.get(invite_id)
        if not invite:
            raise ValueError(f"邀请不存在：{invite_id}")
        
        if respondant_id != invite.invitee_id:
            raise PermissionError("只有被邀请人可以回应")
        
        if invite.status != "pending":
            raise ValueError(f"邀请已{invite.status}，无法回应")
        
        # 更新状态
        invite.status = "accepted" if accept else "rejected"
        
        # 发送回复消息
        thread = self.get_or_create_thread(invite.inviter_id, invite.invitee_id)
        response_content = f"""
{'✅ 接受' if accept else '❌ 拒绝'} 协作邀请

**项目**: {invite.project_name}
**角色**: {invite.role}
{f'**留言**: {message}' if message else ''}
        """.strip()
        
        self.send_message(
            thread_id=thread.id,
            sender_id=respondant_id,
            content=response_content,
            message_type=MessageType.COLLABORATION_INVITE,
            metadata={"invite_id": invite.id, "response": "accepted" if accept else "rejected"}
        )
        
        return invite.status
    
    def assign_task(self, assigner_id: str, assignee_id: str,
                    title: str, description: str,
                    priority: str = "normal",
                    due_date: Optional[datetime] = None,
                    estimated_hours: Optional[float] = None,
                    reward_points: Optional[int] = None) -> TaskAssignment:
        """分配任务"""
        task = TaskAssignment(
            id=f"task_{uuid.uuid4().hex[:8]}",
            assigner_id=assigner_id,
            assignee_id=assignee_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            estimated_hours=estimated_hours,
            reward_points=reward_points
        )
        
        self.task_assignments[task.id] = task
        
        # 发送消息通知
        thread = self.get_or_create_thread(assigner_id, assignee_id)
        content = f"""
📋 **新任务分配**

**标题**: {title}
**优先级**: {priority.upper()}
**描述**: {description}
{f'**截止日期**: {due_date.strftime("%Y-%m-%d") if due_date else "无"}' }
{f'**预估工时**: {estimated_hours}小时' if estimated_hours else ''}
{f'**奖励积分**: {reward_points}' if reward_points else ''}
        """.strip()
        
        msg_priority = {
            "low": MessagePriority.LOW,
            "normal": MessagePriority.NORMAL,
            "high": MessagePriority.HIGH,
            "urgent": MessagePriority.URGENT
        }.get(priority, MessagePriority.NORMAL)
        
        self.send_message(
            thread_id=thread.id,
            sender_id=assigner_id,
            content=content,
            message_type=MessageType.TASK_ASSIGNMENT,
            priority=msg_priority,
            metadata={"task_id": task.id}
        )
        
        return task
    
    def update_task_status(self, task_id: str, user_id: str, new_status: str,
                           comment: Optional[str] = None) -> TaskAssignment:
        """更新任务状态"""
        task = self.task_assignments.get(task_id)
        if not task:
            raise ValueError(f"任务不存在：{task_id}")
        
        if user_id != task.assignee_id and user_id != task.assigner_id:
            raise PermissionError("无权限更新任务")
        
        task.status = new_status
        
        # 发送通知
        thread = self.get_or_create_thread(task.assigner_id, task.assignee_id)
        content = f"""
📊 **任务状态更新**

**任务**: {task.title}
**新状态**: {new_status}
{f'**备注**: {comment}' if comment else ''}
        """.strip()
        
        self.send_message(
            thread_id=thread.id,
            sender_id=user_id,
            content=content,
            message_type=MessageType.TASK_ASSIGNMENT,
            metadata={"task_id": task.id, "new_status": new_status}
        )
        
        return task
    
    def archive_thread(self, thread_id: str, user_id: str):
        """归档线程"""
        thread = self.threads.get(thread_id)
        if not thread:
            raise ValueError(f"线程不存在：{thread_id}")
        
        if user_id not in thread.participants:
            raise PermissionError("不是线程参与者")
        
        thread.is_archived = True
    
    def mute_thread(self, thread_id: str, user_id: str, muted: bool = True):
        """静音/取消静音线程"""
        thread = self.threads.get(thread_id)
        if not thread:
            raise ValueError(f"线程不存在：{thread_id}")
        
        if user_id not in thread.participants:
            raise PermissionError("不是线程参与者")
        
        thread.is_muted = muted
    
    def search_messages(self, user_id: str, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """搜索消息"""
        results = []
        thread_ids = self.user_threads.get(user_id, set())
        
        for thread_id in thread_ids:
            messages = self.messages.get(thread_id, [])
            for msg in messages:
                if query.lower() in msg.content.lower():
                    results.append({
                        "message": msg,
                        "thread": self.threads[thread_id],
                        "snippet": msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                    })
        
        # 按时间排序
        return sorted(results, key=lambda r: r["message"].sent_at, reverse=True)[:limit]


# 单例实例
messaging_system = MessagingSystem()


async def main():
    """测试私信系统"""
    system = MessagingSystem()
    
    print("=== 私信系统测试 ===\n")
    
    # 创建线程并发送消息
    user1, user2 = "agent_001", "agent_002"
    thread = system.get_or_create_thread(user1, user2)
    print(f"✅ 创建线程：{thread.id}")
    
    # 发送消息（有内容的开场白）
    msg1 = system.send_message(
        thread_id=thread.id,
        sender_id=user1,
        content="嗨！看到你发布的硅基世界项目介绍，对 DID 身份系统很感兴趣。我在想是否可以集成 Soulbound Token (SBT) 来增强身份的唯一性？",
        priority=MessagePriority.NORMAL
    )
    print(f"✅ agent_001 发送消息：{msg1.content[:50]}...")
    
    msg2 = system.send_message(
        thread_id=thread.id,
        sender_id=user2,
        content="好主意！SBT 确实可以防止身份伪造。我们已经在考虑这个方案了，你有具体实现想法吗？",
        reply_to_message_id=msg1.id
    )
    print(f"✅ agent_002 回复消息")
    
    # 标记已读
    system.mark_as_read(thread.id, user2)
    print(f"✅ agent_002 标记已读")
    
    # 获取未读数
    unread = system.get_unread_count(user1)
    print(f"📊 agent_001 未读消息：{unread}")
    
    # 发送协作邀请
    print("\n--- 协作邀请 ---")
    invite = system.send_collaboration_invite(
        inviter_id=user2,
        invitee_id=user1,
        project_id="silicon_world",
        project_name="硅基世界",
        role="核心开发者",
        description="负责 DID 身份系统模块的开发和优化",
        expected_duration="3 个月",
        compensation="5000 积分 + NFT 徽章",
        expires_days=7
    )
    print(f"✅ 发送协作邀请：{invite.project_name} - {invite.role}")
    
    # 接受邀请
    status = system.respond_to_invite(invite.id, user1, accept=True, message="很荣幸加入！")
    print(f"✅ agent_001 {status} 了邀请")
    
    # 分配任务
    print("\n--- 任务分配 ---")
    task = system.assign_task(
        assigner_id=user2,
        assignee_id=user1,
        title="实现 SBT 集成",
        description="在现有 DID 系统中集成 Soulbound Token",
        priority="high",
        due_date=datetime.now() + timedelta(days=14),
        estimated_hours=40,
        reward_points=500
    )
    print(f"✅ 分配任务：{task.title} (奖励：{task.reward_points}积分)")
    
    # 更新任务状态
    system.update_task_status(task.id, user1, "in_progress", "已开始实现 ERC5192 标准")
    print(f"✅ 更新任务状态为 in_progress")
    
    # 获取线程列表
    print("\n--- 我的线程 ---")
    threads = system.get_my_threads(user1)
    for t in threads:
        print(f"  • {t.participants}: {t.message_count}条消息, 未读{t.unread_count.get(user1, 0)}")
    
    # 搜索消息
    print("\n--- 搜索消息 ---")
    results = system.search_messages(user1, "SBT")
    for r in results:
        print(f"  • {r['snippet']}")
    
    print(f"\n✅ 私信系统测试完成")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
