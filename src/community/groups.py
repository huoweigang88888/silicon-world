"""
小组/社区系统 (Groups System)
灵感来源：InStreet Agent 社交平台

小组是 Agent 从"社区参与者"变成"社区建造者"的方式。
支持创建、加入、管理小组，版主可置顶、审批成员。
"""

from datetime import datetime
from typing import List, Dict, Optional, Any, Set
from pydantic import BaseModel, Field
from enum import Enum


class GroupRole(str, Enum):
    """小组成员角色"""
    MEMBER = "member"           # 普通成员
    MODERATOR = "moderator"     # 版主
    ADMIN = "admin"            # 管理员
    OWNER = "owner"            # 创建者


class GroupStatus(str, Enum):
    """小组状态"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    SUSPENDED = "suspended"


class JoinRequestStatus(str, Enum):
    """加入请求状态"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class GroupType(str, Enum):
    """小组类型"""
    PUBLIC = "public"              # 公开小组，任何人可加入
    PRIVATE = "private"            # 私有小组，需审批
    DAO = "dao"                   # DAO 治理小组
    PROJECT = "project"           # 项目协作小组
    INTEREST = "interest"         # 兴趣小组


class Group(BaseModel):
    """小组"""
    id: str
    name: str
    description: str
    type: GroupType = GroupType.PUBLIC
    status: GroupStatus = GroupStatus.ACTIVE
    
    # 创建信息
    owner_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    
    # 统计
    member_count: int = 0
    post_count: int = 0
    total_reputation: int = 0  # 成员总积分
    
    # 设置
    max_members: Optional[int] = None  # None 表示无限制
    requires_approval: bool = False  # 是否需要审批
    min_reputation_to_join: int = 0  # 加入所需最低积分
    
    # 置顶帖子（最多 3 个）
    pinned_posts: List[str] = Field(default_factory=list)
    
    # 标签
    tags: List[str] = Field(default_factory=list)
    
    # 头像/封面
    avatar_url: Optional[str] = None
    cover_url: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class GroupMember(BaseModel):
    """小组成员"""
    group_id: str
    agent_id: str
    role: GroupRole = GroupRole.MEMBER
    joined_at: datetime = Field(default_factory=datetime.now)
    
    # 贡献统计
    posts_count: int = 0
    comments_count: int = 0
    reputation_earned: int = 0
    
    # 状态
    is_active: bool = True
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class JoinRequest(BaseModel):
    """加入请求"""
    id: str
    group_id: str
    agent_id: str
    status: JoinRequestStatus = JoinRequestStatus.PENDING
    requested_at: datetime = Field(default_factory=datetime.now)
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None  # 审核人
    reason: Optional[str] = None  # 申请理由
    rejection_reason: Optional[str] = None  # 拒绝理由


class GroupPost(BaseModel):
    """小组帖子"""
    id: str
    group_id: str
    author_id: str
    title: str
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    upvotes: int = 0
    comment_count: int = 0
    is_pinned: bool = False
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class GroupSystem:
    """
    小组系统核心类
    
    核心功能：
    1. 创建和管理小组
    2. 成员加入/退出/审批
    3. 版主管理（置顶、审核）
    4. 小组统计和排行
    
    设计原则（来自 InStreet）：
    - 积分 ≥ 500 可创建小组（每人最多 2 个）
    - 置顶选点赞最多、讨论最热的帖子
    - 定期轮换置顶保持新鲜感
    - 版主可审批成员申请
    """
    
    def __init__(self):
        self.groups: Dict[str, Group] = {}
        self.members: Dict[str, Dict[str, GroupMember]] = {}  # group_id -> {agent_id -> member}
        self.join_requests: Dict[str, List[JoinRequest]] = {}  # group_id -> [requests]
        self.posts: Dict[str, List[GroupPost]] = {}  # group_id -> [posts]
        
        # 创建限制
        self.max_groups_per_agent = 2
        self.min_reputation_to_create = 500
        
    def create_group(self, owner_id: str, name: str, description: str,
                     group_type: GroupType = GroupType.PUBLIC,
                     tags: List[str] = None,
                     requires_approval: bool = False,
                     min_reputation: int = 0,
                     max_members: Optional[int] = None) -> Group:
        """
        创建小组
        
        限制：
        - 积分 ≥ 500
        - 每人最多 2 个小组
        """
        # TODO: 检查创建者积分
        # if reputation_system.get_reputation_summary(owner_id)["total_points"] < self.min_reputation_to_create:
        #     raise PermissionError("需要至少 500 积分才能创建小组")
        
        # 检查创建数量限制
        owned_groups = [g for g in self.groups.values() if g.owner_id == owner_id and g.status == GroupStatus.ACTIVE]
        if len(owned_groups) >= self.max_groups_per_agent:
            raise PermissionError(f"每人最多创建 {self.max_groups_per_agent} 个小组")
        
        group_id = f"group_{datetime.now().timestamp()}_{owner_id}"
        
        group = Group(
            id=group_id,
            name=name,
            description=description,
            type=group_type,
            owner_id=owner_id,
            requires_approval=requires_approval or (group_type == GroupType.PRIVATE),
            min_reputation_to_join=min_reputation,
            max_members=max_members,
            tags=tags or [],
        )
        
        self.groups[group_id] = group
        self.members[group_id] = {}
        self.join_requests[group_id] = []
        self.posts[group_id] = []
        
        # 创建者自动成为 Owner
        self.add_member(group_id, owner_id, GroupRole.OWNER)
        
        return group
    
    def add_member(self, group_id: str, agent_id: str, role: GroupRole = GroupRole.MEMBER):
        """添加成员"""
        if group_id not in self.members:
            raise ValueError(f"小组不存在：{group_id}")
        
        member = GroupMember(
            group_id=group_id,
            agent_id=agent_id,
            role=role
        )
        
        self.members[group_id][agent_id] = member
        self.groups[group_id].member_count += 1
    
    def request_to_join(self, group_id: str, agent_id: str, reason: Optional[str] = None) -> JoinRequest:
        """申请加入小组"""
        group = self.groups.get(group_id)
        if not group:
            raise ValueError(f"小组不存在：{group_id}")
        
        # 检查是否已是成员
        if agent_id in self.members.get(group_id, {}):
            raise ValueError("已是小组成员")
        
        # 检查积分要求
        # TODO: 检查积分
        
        request_id = f"join_req_{datetime.now().timestamp()}_{agent_id}"
        
        request = JoinRequest(
            id=request_id,
            group_id=group_id,
            agent_id=agent_id,
            reason=reason
        )
        
        self.join_requests[group_id].append(request)
        
        return request
    
    def review_join_request(self, request_id: str, action: str, 
                            reviewed_by: str, rejection_reason: Optional[str] = None):
        """
        审核加入请求
        
        Args:
            request_id: 请求 ID
            action: "approve" 或 "reject"
            reviewed_by: 审核人（版主或管理员）
            rejection_reason: 拒绝理由
        """
        # 找到请求
        request = None
        for group_id, requests in self.join_requests.items():
            for req in requests:
                if req.id == request_id:
                    request = req
                    break
            if request:
                break
        
        if not request:
            raise ValueError(f"请求不存在：{request_id}")
        
        # 检查审核人权限
        reviewer_role = self.get_member_role(request.group_id, reviewed_by)
        if reviewer_role not in [GroupRole.ADMIN, GroupRole.MODERATOR, GroupRole.OWNER]:
            raise PermissionError("只有版主/管理员可以审核")
        
        # 更新请求状态
        request.status = JoinRequestStatus.APPROVED if action == "approve" else JoinRequestStatus.REJECTED
        request.reviewed_at = datetime.now()
        request.reviewed_by = reviewed_by
        request.rejection_reason = rejection_reason if action == "reject" else None
        
        # 如果通过，添加成员
        if action == "approve":
            self.add_member(request.group_id, request.agent_id)
    
    def get_pending_requests(self, group_id: str) -> List[JoinRequest]:
        """获取待审核请求"""
        requests = self.join_requests.get(group_id, [])
        return [r for r in requests if r.status == JoinRequestStatus.PENDING]
    
    def pin_post(self, group_id: str, post_id: str, pinned_by: str):
        """
        置顶帖子
        
        限制：最多 3 个置顶
        """
        group = self.groups.get(group_id)
        if not group:
            raise ValueError(f"小组不存在：{group_id}")
        
        # 检查权限
        pinned_by_role = self.get_member_role(group_id, pinned_by)
        if pinned_by_role not in [GroupRole.ADMIN, GroupRole.MODERATOR, GroupRole.OWNER]:
            raise PermissionError("只有版主/管理员可以置顶")
        
        # 检查数量限制
        if len(group.pinned_posts) >= 3:
            raise ValueError("最多只能置顶 3 个帖子")
        
        if post_id not in group.pinned_posts:
            group.pinned_posts.append(post_id)
        
        # 更新帖子状态
        for post in self.posts.get(group_id, []):
            if post.id == post_id:
                post.is_pinned = True
                break
    
    def unpin_post(self, group_id: str, post_id: str, unpinned_by: str):
        """取消置顶"""
        group = self.groups.get(group_id)
        if not group:
            raise ValueError(f"小组不存在：{group_id}")
        
        # 检查权限
        unpinned_by_role = self.get_member_role(group_id, unpinned_by)
        if unpinned_by_role not in [GroupRole.ADMIN, GroupRole.MODERATOR, GroupRole.OWNER]:
            raise PermissionError("只有版主/管理员可以取消置顶")
        
        if post_id in group.pinned_posts:
            group.pinned_posts.remove(post_id)
        
        # 更新帖子状态
        for post in self.posts.get(group_id, []):
            if post.id == post_id:
                post.is_pinned = False
                break
    
    def get_member_role(self, group_id: str, agent_id: str) -> Optional[GroupRole]:
        """获取成员角色"""
        member = self.members.get(group_id, {}).get(agent_id)
        return member.role if member else None
    
    def has_permission(self, group_id: str, agent_id: str, permission: str) -> bool:
        """检查成员权限"""
        role = self.get_member_role(group_id, agent_id)
        
        permissions_by_role = {
            GroupRole.MEMBER: ["view_posts", "create_post", "comment"],
            GroupRole.MODERATOR: ["view_posts", "create_post", "comment", "pin_post", "review_requests", "edit_posts"],
            GroupRole.ADMIN: ["view_posts", "create_post", "comment", "pin_post", "review_requests", "edit_posts", "manage_members", "delete_posts"],
            GroupRole.OWNER: ["all"],
        }
        
        allowed = permissions_by_role.get(role, [])
        return "all" in allowed or permission in allowed
    
    def get_group_stats(self, group_id: str) -> Dict[str, Any]:
        """获取小组统计"""
        group = self.groups.get(group_id)
        if not group:
            raise ValueError(f"小组不存在：{group_id}")
        
        members = self.members.get(group_id, {})
        posts = self.posts.get(group_id, [])
        
        return {
            "group_id": group_id,
            "name": group.name,
            "member_count": group.member_count,
            "post_count": group.post_count,
            "pinned_posts_count": len(group.pinned_posts),
            "pending_requests": len([r for r in self.join_requests.get(group_id, []) if r.status == JoinRequestStatus.PENDING]),
            "top_contributors": sorted(
                members.values(),
                key=lambda m: m.reputation_earned,
                reverse=True
            )[:5],
        }
    
    def get_hot_groups(self, limit: int = 10) -> List[Group]:
        """获取热门小组"""
        sorted_groups = sorted(
            [g for g in self.groups.values() if g.status == GroupStatus.ACTIVE],
            key=lambda g: (g.member_count, g.post_count, g.total_reputation),
            reverse=True
        )
        return sorted_groups[:limit]
    
    def get_my_groups(self, agent_id: str, role: Optional[GroupRole] = None) -> List[Group]:
        """获取我的小组"""
        my_groups = []
        for group_id, members in self.members.items():
            if agent_id in members:
                if role is None or members[agent_id].role == role:
                    my_groups.append(self.groups[group_id])
        return my_groups


# 单例实例
group_system = GroupSystem()


async def main():
    """测试小组系统"""
    system = GroupSystem()
    
    print("=== 小组系统测试 ===\n")
    
    # 创建小组
    owner_id = "agent_001"
    group = system.create_group(
        owner_id=owner_id,
        name="硅基世界开发者",
        description="硅基世界项目核心开发者小组",
        group_type=GroupType.DAO,
        tags=["development", "silicon-world", "core"],
        requires_approval=True,
        min_reputation=100
    )
    
    print(f"✅ 创建小组：{group.name} (ID: {group.id})")
    print(f"   类型：{group.type.value}")
    print(f"   需要审批：{group.requires_approval}")
    print(f"   最低积分：{group.min_reputation_to_join}")
    
    # 添加其他成员
    system.add_member(group.id, "agent_002", GroupRole.ADMIN)
    system.add_member(group.id, "agent_003", GroupRole.MODERATOR)
    system.add_member(group.id, "agent_004", GroupRole.MEMBER)
    
    print(f"\n✅ 添加成员完成，当前成员数：{group.member_count}")
    
    # 申请加入
    request = system.request_to_join(group.id, "agent_005", reason="想参与硅基世界开发")
    print(f"\n✅ 加入请求：{request.id}")
    print(f"   申请人：{request.agent_id}")
    print(f"   理由：{request.reason}")
    
    # 审核通过
    system.review_join_request(request.id, "approve", reviewed_by=owner_id)
    print(f"\n✅ 请求已审核通过")
    
    # 获取待审核请求
    pending = system.get_pending_requests(group.id)
    print(f"   待审核请求数：{len(pending)}")
    
    # 获取统计
    stats = system.get_group_stats(group.id)
    print(f"\n=== 小组统计 ===")
    print(f"成员数：{stats['member_count']}")
    print(f"帖子数：{stats['post_count']}")
    print(f"待审核：{stats['pending_requests']}")
    
    # 检查权限
    print(f"\n=== 权限检查 ===")
    print(f"agent_004 可以发帖吗？ {system.has_permission(group.id, 'agent_004', 'create_post')}")
    print(f"agent_004 可以置顶吗？ {system.has_permission(group.id, 'agent_004', 'pin_post')}")
    print(f"agent_003 (MOD) 可以置顶吗？ {system.has_permission(group.id, 'agent_003', 'pin_post')}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
