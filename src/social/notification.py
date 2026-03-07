"""
通知系统

推送通知和消息提醒
"""

from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import uuid


# ==================== 通知类型 ====================

class NotificationType(str, Enum):
    """通知类型"""
    MESSAGE = "message"  # 新消息
    FRIEND_REQUEST = "friend_request"  # 好友请求
    MENTION = "mention"  # 被提及
    REACTION = "reaction"  # 被回复
    SYSTEM = "system"  # 系统通知
    GOVERNANCE = "governance"  # 治理通知
    TRANSACTION = "transaction"  # 交易通知


class NotificationPriority(str, Enum):
    """通知优先级"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


# ==================== 通知模型 ====================

class Notification(BaseModel):
    """通知"""
    id: str
    recipient_id: str
    notification_type: NotificationType
    title: str
    content: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    is_read: bool = False
    created_at: datetime = None
    read_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow()
        super().__init__(**data)
    
    def mark_as_read(self):
        """标记为已读"""
        self.is_read = True
        self.read_at = datetime.utcnow()


# ==================== 通知管理器 ====================

class NotificationManager:
    """
    通知管理器
    
    管理通知的发送、存储和检索
    """
    
    def __init__(self):
        self.notifications: Dict[str, List[Notification]] = {}  # user_id -> [notifications]
        self.push_subscriptions: Dict[str, Set[str]] = {}  # user_id -> {subscription_ids}
    
    def send_notification(
        self,
        recipient_id: str,
        notification_type: NotificationType,
        title: str,
        content: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        metadata: Dict[str, Any] = None
    ) -> Notification:
        """
        发送通知
        
        Args:
            recipient_id: 接收人 ID
            notification_type: 通知类型
            title: 标题
            content: 内容
            priority: 优先级
            metadata: 元数据
        
        Returns:
            Notification
        """
        notification = Notification(
            recipient_id=recipient_id,
            notification_type=notification_type,
            title=title,
            content=content,
            priority=priority,
            metadata=metadata or {}
        )
        
        # 存储通知
        if recipient_id not in self.notifications:
            self.notifications[recipient_id] = []
        self.notifications[recipient_id].append(notification)
        
        # TODO: 推送通知 (WebSocket/Push Service)
        
        return notification
    
    def get_notifications(
        self,
        user_id: str,
        limit: int = 50,
        unread_only: bool = False
    ) -> List[Notification]:
        """
        获取通知
        
        Args:
            user_id: 用户 ID
            limit: 返回数量
            unread_only: 仅未读
        
        Returns:
            通知列表
        """
        notifications = self.notifications.get(user_id, [])
        
        if unread_only:
            notifications = [n for n in notifications if not n.is_read]
        
        # 按时间倒序
        notifications.sort(key=lambda n: n.created_at, reverse=True)
        
        return notifications[:limit]
    
    def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """标记通知为已读"""
        for notification in self.notifications.get(user_id, []):
            if notification.id == notification_id:
                notification.mark_as_read()
                return True
        return False
    
    def mark_all_as_read(self, user_id: str):
        """标记所有通知为已读"""
        for notification in self.notifications.get(user_id, []):
            notification.mark_as_read()
    
    def get_unread_count(self, user_id: str) -> int:
        """获取未读通知数"""
        return sum(
            1 for n in self.notifications.get(user_id, [])
            if not n.is_read
        )
    
    def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """删除通知"""
        notifications = self.notifications.get(user_id, [])
        for i, notification in enumerate(notifications):
            if notification.id == notification_id:
                notifications.pop(i)
                return True
        return False
    
    def clear_notifications(self, user_id: str, older_than_days: int = None):
        """
        清空通知
        
        Args:
            user_id: 用户 ID
            older_than_days: 清空早于指定天数的通知
        """
        if user_id not in self.notifications:
            return
        
        if older_than_days:
            cutoff = datetime.utcnow() - timedelta(days=older_than_days)
            self.notifications[user_id] = [
                n for n in self.notifications[user_id]
                if n.created_at > cutoff
            ]
        else:
            self.notifications[user_id] = []
    
    def subscribe_push(self, user_id: str, subscription_id: str):
        """订阅推送通知"""
        if user_id not in self.push_subscriptions:
            self.push_subscriptions[user_id] = set()
        self.push_subscriptions[user_id].add(subscription_id)
    
    def unsubscribe_push(self, user_id: str, subscription_id: str):
        """取消订阅推送"""
        if user_id in self.push_subscriptions:
            self.push_subscriptions[user_id].discard(subscription_id)
    
    def get_statistics(self, user_id: str) -> Dict[str, Any]:
        """获取通知统计"""
        notifications = self.notifications.get(user_id, [])
        return {
            "total": len(notifications),
            "unread": sum(1 for n in notifications if not n.is_read),
            "by_type": self._count_by_type(notifications),
            "push_subscriptions": len(self.push_subscriptions.get(user_id, set()))
        }
    
    def _count_by_type(self, notifications: List[Notification]) -> Dict[str, int]:
        """按类型统计"""
        counts = {}
        for notification in notifications:
            type_name = notification.notification_type.value
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts


# 使用示例
if __name__ == "__main__":
    from datetime import timedelta
    
    # 创建通知管理器
    mgr = NotificationManager()
    
    print("发送通知...")
    
    # 发送各种通知
    mgr.send_notification(
        recipient_id="user_1",
        notification_type=NotificationType.MESSAGE,
        title="新消息",
        content="user_2 给你发送了一条消息",
        priority=NotificationPriority.NORMAL
    )
    
    mgr.send_notification(
        recipient_id="user_1",
        notification_type=NotificationType.FRIEND_REQUEST,
        title="好友请求",
        content="user_3 想和你成为好友",
        priority=NotificationPriority.HIGH
    )
    
    mgr.send_notification(
        recipient_id="user_1",
        notification_type=NotificationType.SYSTEM,
        title="系统通知",
        content="系统维护通知",
        priority=NotificationPriority.LOW
    )
    
    # 获取通知
    print("\nuser_1 的通知:")
    notifications = mgr.get_notifications("user_1", limit=10)
    for notif in notifications:
        status = "未读" if not notif.is_read else "已读"
        print(f"  [{status}] {notif.title}: {notif.content}")
    
    # 获取未读数
    unread_count = mgr.get_unread_count("user_1")
    print(f"\n未读通知数：{unread_count}")
    
    # 标记为已读
    print("\n标记所有为已读...")
    mgr.mark_all_as_read("user_1")
    unread_count = mgr.get_unread_count("user_1")
    print(f"未读通知数：{unread_count}")
    
    # 获取统计
    print("\n通知统计:")
    stats = mgr.get_statistics("user_1")
    for key, value in stats.items():
        print(f"  {key}: {value}")
