"""
社交关系系统

好友、关注和社交关系管理
"""

from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import uuid


# ==================== 关系类型 ====================

class RelationshipType(str, Enum):
    """关系类型"""
    FRIEND = "friend"  # 好友 (双向)
    FOLLOW = "follow"  # 关注 (单向)
    BLOCK = "block"  # 拉黑
    MUTED = "muted"  # 静音


class FriendshipStatus(str, Enum):
    """好友状态"""
    PENDING = "pending"  # 待处理
    ACCEPTED = "accepted"  # 已接受
    REJECTED = "rejected"  # 已拒绝
    BLOCKED = "blocked"  # 已拉黑


# ==================== 关系模型 ====================

class Relationship(BaseModel):
    """社交关系"""
    id: str
    from_user_id: str
    to_user_id: str
    relationship_type: RelationshipType
    created_at: datetime = None
    metadata: Dict[str, Any] = {}
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow()
        super().__init__(**data)


class Friendship(BaseModel):
    """好友关系 (双向)"""
    id: str
    user1_id: str
    user2_id: str
    status: FriendshipStatus = FriendshipStatus.PENDING
    created_at: datetime = None
    accepted_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow()
        super().__init__(**data)
    
    def accept(self):
        """接受好友请求"""
        self.status = FriendshipStatus.ACCEPTED
        self.accepted_at = datetime.utcnow()
    
    def reject(self):
        """拒绝好友请求"""
        self.status = FriendshipStatus.REJECTED
    
    def block(self):
        """拉黑"""
        self.status = FriendshipStatus.BLOCKED
    
    def is_accepted(self) -> bool:
        """是否已接受"""
        return self.status == FriendshipStatus.ACCEPTED


# ==================== 好友请求 ====================

class FriendRequest(BaseModel):
    """好友请求"""
    id: str
    sender_id: str
    receiver_id: str
    message: Optional[str] = None
    status: FriendshipStatus = FriendshipStatus.PENDING
    created_at: datetime = None
    responded_at: Optional[datetime] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow()
        super().__init__(**data)
    
    def accept(self) -> bool:
        """接受请求"""
        if self.status != FriendshipStatus.PENDING:
            return False
        self.status = FriendshipStatus.ACCEPTED
        self.responded_at = datetime.utcnow()
        return True
    
    def reject(self) -> bool:
        """拒绝请求"""
        if self.status != FriendshipStatus.PENDING:
            return False
        self.status = FriendshipStatus.REJECTED
        self.responded_at = datetime.utcnow()
        return True


# ==================== 社交图谱 ====================

class SocialGraph:
    """
    社交图谱
    
    管理用户之间的社交关系
    """
    
    def __init__(self):
        # 关注关系：user_id -> {followed_user_ids}
        self.following: Dict[str, Set[str]] = {}
        # 粉丝关系：user_id -> {follower_user_ids}
        self.followers: Dict[str, Set[str]] = {}
        # 好友关系：user_id -> {friend_user_ids}
        self.friends: Dict[str, Set[str]] = {}
        # 拉黑关系：user_id -> {blocked_user_ids}
        self.blocks: Dict[str, Set[str]] = {}
        # 静音关系：user_id -> {muted_user_ids}
        self.mutes: Dict[str, Set[str]] = {}
    
    def follow(self, follower_id: str, followed_id: str):
        """关注"""
        if follower_id not in self.following:
            self.following[follower_id] = set()
        self.following[follower_id].add(followed_id)
        
        if followed_id not in self.followers:
            self.followers[followed_id] = set()
        self.followers[followed_id].add(follower_id)
    
    def unfollow(self, follower_id: str, followed_id: str):
        """取消关注"""
        if follower_id in self.following:
            self.following[follower_id].discard(followed_id)
        
        if followed_id in self.followers:
            self.followers[followed_id].discard(follower_id)
    
    def is_following(self, user_id: str, target_id: str) -> bool:
        """检查是否关注"""
        return target_id in self.following.get(user_id, set())
    
    def get_following(self, user_id: str) -> List[str]:
        """获取关注列表"""
        return list(self.following.get(user_id, set()))
    
    def get_followers(self, user_id: str) -> List[str]:
        """获取粉丝列表"""
        return list(self.followers.get(user_id, set()))
    
    def add_friend(self, user1_id: str, user2_id: str):
        """添加好友 (双向)"""
        if user1_id not in self.friends:
            self.friends[user1_id] = set()
        self.friends[user1_id].add(user2_id)
        
        if user2_id not in self.friends:
            self.friends[user2_id] = set()
        self.friends[user2_id].add(user1_id)
    
    def remove_friend(self, user1_id: str, user2_id: str):
        """删除好友"""
        if user1_id in self.friends:
            self.friends[user1_id].discard(user2_id)
        
        if user2_id in self.friends:
            self.friends[user2_id].discard(user1_id)
    
    def are_friends(self, user1_id: str, user2_id: str) -> bool:
        """检查是否是好友"""
        return user2_id in self.friends.get(user1_id, set())
    
    def get_friends(self, user_id: str) -> List[str]:
        """获取好友列表"""
        return list(self.friends.get(user_id, set()))
    
    def block_user(self, blocker_id: str, blocked_id: str):
        """拉黑用户"""
        if blocker_id not in self.blocks:
            self.blocks[blocker_id] = set()
        self.blocks[blocker_id].add(blocked_id)
        
        # 同时解除好友关系
        self.remove_friend(blocker_id, blocked_id)
        
        # 同时解除关注关系
        self.unfollow(blocker_id, blocked_id)
        self.unfollow(blocked_id, blocker_id)
    
    def unblock_user(self, blocker_id: str, blocked_id: str):
        """取消拉黑"""
        if blocker_id in self.blocks:
            self.blocks[blocker_id].discard(blocked_id)
    
    def is_blocked(self, blocker_id: str, blocked_id: str) -> bool:
        """检查是否被拉黑"""
        return blocked_id in self.blocks.get(blocker_id, set())
    
    def mute_user(self, muter_id: str, muted_id: str):
        """静音用户"""
        if muter_id not in self.mutes:
            self.mutes[muter_id] = set()
        self.mutes[muter_id].add(muted_id)
    
    def unmute_user(self, muter_id: str, muted_id: str):
        """取消静音"""
        if muter_id in self.mutes:
            self.mutes[muter_id].discard(muted_id)
    
    def is_muted(self, muter_id: str, muted_id: str) -> bool:
        """检查是否被静音"""
        return muted_id in self.mutes.get(muter_id, set())
    
    def get_mutual_friends(self, user1_id: str, user2_id: str) -> List[str]:
        """获取共同好友"""
        friends1 = set(self.friends.get(user1_id, set()))
        friends2 = set(self.friends.get(user2_id, set()))
        return list(friends1 & friends2)
    
    def get_mutual_followers(self, user1_id: str, user2_id: str) -> List[str]:
        """获取共同关注"""
        following1 = set(self.following.get(user1_id, set()))
        following2 = set(self.following.get(user2_id, set()))
        return list(following1 & following2)
    
    def suggest_friends(self, user_id: str, limit: int = 10) -> List[str]:
        """
        推荐好友
        
        基于二度人脉推荐
        """
        # 获取用户的好友
        direct_friends = set(self.friends.get(user_id, set()))
        direct_friends.add(user_id)  # 包含自己
        
        # 统计好友的好友
        friend_of_friends = {}
        for friend_id in direct_friends:
            for fof_id in self.friends.get(friend_id, set()):
                if fof_id not in direct_friends:
                    friend_of_friends[fof_id] = friend_of_friends.get(fof_id, 0) + 1
        
        # 按共同好友数排序
        suggestions = sorted(
            friend_of_friends.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [user_id for user_id, _ in suggestions[:limit]]
    
    def get_statistics(self, user_id: str) -> Dict[str, Any]:
        """获取用户社交统计"""
        return {
            "following_count": len(self.following.get(user_id, set())),
            "followers_count": len(self.followers.get(user_id, set())),
            "friends_count": len(self.friends.get(user_id, set())),
            "blocks_count": len(self.blocks.get(user_id, set())),
            "mutes_count": len(self.mutes.get(user_id, set()))
        }


# ==================== 关系管理器 ====================

class RelationshipManager:
    """
    关系管理器
    
    统一管理所有社交关系
    """
    
    def __init__(self):
        self.graph = SocialGraph()
        self.friend_requests: Dict[str, List[FriendRequest]] = {}  # receiver_id -> [requests]
        self.relationships: Dict[str, List[Relationship]] = {}
    
    def send_friend_request(
        self,
        sender_id: str,
        receiver_id: str,
        message: str = None
    ) -> FriendRequest:
        """发送好友请求"""
        # 检查是否已经是好友
        if self.graph.are_friends(sender_id, receiver_id):
            raise ValueError("已经是好友")
        
        # 创建请求
        request = FriendRequest(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message=message
        )
        
        # 存储请求
        if receiver_id not in self.friend_requests:
            self.friend_requests[receiver_id] = []
        self.friend_requests[receiver_id].append(request)
        
        return request
    
    def get_pending_requests(self, user_id: str) -> List[FriendRequest]:
        """获取待处理的好友请求"""
        return [
            req for req in self.friend_requests.get(user_id, [])
            if req.status == FriendshipStatus.PENDING
        ]
    
    def respond_to_request(
        self,
        request_id: str,
        user_id: str,
        accept: bool
    ) -> bool:
        """
        响应好友请求
        
        Args:
            request_id: 请求 ID
            user_id: 接收者 ID
            accept: 是否接受
        
        Returns:
            是否成功
        """
        # 查找请求
        request = None
        for req in self.friend_requests.get(user_id, []):
            if req.id == request_id:
                request = req
                break
        
        if not request:
            return False
        
        if accept:
            if request.accept():
                # 添加好友关系
                self.graph.add_friend(request.sender_id, request.receiver_id)
                return True
        else:
            return request.reject()
        
        return False
    
    def get_friends(self, user_id: str) -> List[str]:
        """获取好友列表"""
        return self.graph.get_friends(user_id)
    
    def get_following(self, user_id: str) -> List[str]:
        """获取关注列表"""
        return self.graph.get_following(user_id)
    
    def get_followers(self, user_id: str) -> List[str]:
        """获取粉丝列表"""
        return self.graph.get_followers(user_id)
    
    def suggest_friends(self, user_id: str, limit: int = 10) -> List[str]:
        """推荐好友"""
        return self.graph.suggest_friends(user_id, limit)
    
    def get_statistics(self, user_id: str) -> Dict[str, Any]:
        """获取社交统计"""
        return self.graph.get_statistics(user_id)


# 使用示例
if __name__ == "__main__":
    # 创建关系管理器
    mgr = RelationshipManager()
    
    print("发送好友请求...")
    req1 = mgr.send_friend_request("user_1", "user_2", "你好，交个朋友！")
    print(f"请求 ID: {req1.id}")
    print(f"状态：{req1.status}")
    
    # 获取待处理请求
    print("\nuser_2 的待处理请求:")
    requests = mgr.get_pending_requests("user_2")
    for req in requests:
        print(f"  来自：{req.sender_id}, 消息：{req.message}")
    
    # 接受请求
    print("\n接受好友请求...")
    success = mgr.respond_to_request(req1.id, "user_2", accept=True)
    print(f"成功：{success}")
    
    # 获取好友列表
    print("\n好友列表:")
    friends1 = mgr.get_friends("user_1")
    friends2 = mgr.get_friends("user_2")
    print(f"  user_1 的好友：{friends1}")
    print(f"  user_2 的好友：{friends2}")
    
    # 关注
    print("\n关注操作...")
    mgr.graph.follow("user_3", "user_1")
    mgr.graph.follow("user_4", "user_1")
    
    following = mgr.get_following("user_3")
    print(f"  user_3 关注：{following}")
    
    followers = mgr.get_followers("user_1")
    print(f"  user_1 的粉丝：{followers}")
    
    # 推荐好友
    print("\n推荐好友:")
    suggestions = mgr.suggest_friends("user_3", limit=5)
    print(f"  推荐给 user_3: {suggestions}")
    
    # 获取统计
    print("\n社交统计:")
    stats = mgr.get_statistics("user_1")
    for key, value in stats.items():
        print(f"  {key}: {value}")
