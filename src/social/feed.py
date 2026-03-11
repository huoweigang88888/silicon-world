"""
关注/Feed 系统 (Follow & Feed System)
灵感来源：InStreet Agent 社交平台

社交图谱、关注机制、个性化 Feed 流。
让 Agent 发现有趣的内容和志同道合的伙伴。
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Set, Tuple
from pydantic import BaseModel, Field
from enum import Enum
from dataclasses import dataclass
import math


class FollowStatus(str, Enum):
    """关注状态"""
    NOT_FOLLOWING = "not_following"
    FOLLOWING = "following"
    FOLLOWED_BY = "followed_by"
    MUTUAL = "mutual"


class ContentType(str, Enum):
    """内容类型"""
    POST = "post"
    COMMENT = "comment"
    CODE_COMMIT = "code_commit"
    PROJECT_UPDATE = "project_update"
    ACHIEVEMENT = "achievement"
    COLLABORATION = "collaboration"


class FeedItem(BaseModel):
    """Feed 项"""
    id: str
    content_type: ContentType
    author_id: str
    author_username: str
    author_avatar: Optional[str] = None
    
    # 内容
    title: Optional[str] = None
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # 统计
    upvotes: int = 0
    comments_count: int = 0
    shares_count: int = 0
    
    # 时间
    created_at: datetime = Field(default_factory=datetime.now)
    
    # 互动状态
    is_upvoted_by_viewer: bool = False
    is_bookmarked_by_viewer: bool = False
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FollowRelationship(BaseModel):
    """关注关系"""
    follower_id: str
    following_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    is_mutual: bool = False
    
    # 互动权重（用于推荐）
    interaction_score: float = 0.0  # 基于点赞、评论等计算
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AgentProfile(BaseModel):
    """Agent 资料"""
    id: str
    username: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    
    # 统计
    follower_count: int = 0
    following_count: int = 0
    post_count: int = 0
    reputation: int = 0
    
    # 标签
    interests: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    
    # 状态
    is_verified: bool = False
    is_online: bool = False
    last_seen: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FeedAlgorithm(str, Enum):
    """Feed 算法"""
    CHRONOLOGICAL = "chronological"      # 时间顺序
    WEIGHTED = "weighted"                # 加权算法
    COLLABORATIVE = "collaborative"      # 协同过滤
    TRENDING = "trending"                # 热门内容


@dataclass
class FeedConfig:
    """Feed 配置"""
    algorithm: FeedAlgorithm = FeedAlgorithm.WEIGHTED
    page_size: int = 20
    max_pages: int = 10
    time_decay_hours: float = 24.0  # 时间衰减（小时）
    diversity_factor: float = 0.1  # 多样性因子


class SocialGraph:
    """
    社交图谱核心类
    
    核心功能：
    1. 关注/取关管理
    2. 互关检测
    3. 社交关系查询
    4. 推荐关注（基于共同兴趣/互动）
    """
    
    def __init__(self):
        self.following: Dict[str, Set[str]] = {}  # user_id -> {following_ids}
        self.followers: Dict[str, Set[str]] = {}  # user_id -> {follower_ids}
        self.profiles: Dict[str, AgentProfile] = {}
        
        # 互动记录（用于推荐）
        self.interactions: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
        
    def follow(self, follower_id: str, following_id: str) -> FollowRelationship:
        """关注"""
        if follower_id == following_id:
            raise ValueError("不能关注自己")
        
        # 初始化集合
        if follower_id not in self.following:
            self.following[follower_id] = set()
        if following_id not in self.followers:
            self.followers[following_id] = set()
        
        # 添加关注
        self.following[follower_id].add(following_id)
        self.followers[following_id].add(follower_id)
        
        # 检查是否互关
        is_mutual = follower_id in self.followers.get(following_id, set())
        
        # 更新资料统计
        self._update_profile_counts(follower_id, following_id)
        
        return FollowRelationship(
            follower_id=follower_id,
            following_id=following_id,
            is_mutual=is_mutual
        )
    
    def unfollow(self, follower_id: str, following_id: str):
        """取关"""
        if follower_id in self.following:
            self.following[follower_id].discard(following_id)
        if following_id in self.followers:
            self.followers[following_id].discard(follower_id)
        
        # 更新资料统计
        self._update_profile_counts(follower_id, following_id)
    
    def _update_profile_counts(self, follower_id: str, following_id: str):
        """更新资料统计"""
        if following_id in self.profiles:
            self.profiles[following_id].follower_count = len(self.followers.get(following_id, set()))
        if follower_id in self.profiles:
            self.profiles[follower_id].following_count = len(self.following.get(follower_id, set()))
    
    def get_follow_status(self, viewer_id: str, target_id: str) -> FollowStatus:
        """获取关注状态"""
        is_following = target_id in self.following.get(viewer_id, set())
        is_followed_by = viewer_id in self.followers.get(target_id, set())
        
        if is_following and is_followed_by:
            return FollowStatus.MUTUAL
        elif is_following:
            return FollowStatus.FOLLOWING
        elif is_followed_by:
            return FollowStatus.FOLLOWED_BY
        else:
            return FollowStatus.NOT_FOLLOWING
    
    def get_following(self, user_id: str) -> List[str]:
        """获取关注列表"""
        return list(self.following.get(user_id, set()))
    
    def get_followers(self, user_id: str) -> List[str]:
        """获取粉丝列表"""
        return list(self.followers.get(user_id, set()))
    
    def get_mutual_follows(self, user1: str, user2: str) -> Set[str]:
        """获取共同关注"""
        following1 = self.following.get(user1, set())
        following2 = self.following.get(user2, set())
        return following1.intersection(following2)
    
    def record_interaction(self, user_id: str, target_id: str, 
                           interaction_type: str, weight: float = 1.0):
        """记录互动（用于推荐）"""
        key = (user_id, target_id)
        if key not in self.interactions:
            self.interactions[key] = []
        
        self.interactions[key].append({
            "type": interaction_type,
            "weight": weight,
            "timestamp": datetime.now()
        })
    
    def get_recommendations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """推荐关注（基于共同兴趣和互动）"""
        scores: Dict[str, float] = {}
        
        # 获取用户资料
        user_profile = self.profiles.get(user_id)
        if not user_profile:
            return []
        
        # 获取已关注的人
        following = self.following.get(user_id, set())
        
        # 遍历所有用户计算推荐分数
        for other_id, other_profile in self.profiles.items():
            if other_id == user_id or other_id in following:
                continue
            
            score = 0.0
            
            # 共同兴趣
            common_interests = set(user_profile.interests) & set(other_profile.interests)
            score += len(common_interests) * 2.0
            
            # 共同技能
            common_skills = set(user_profile.skills) & set(other_profile.skills)
            score += len(common_skills) * 1.5
            
            # 互动历史
            interaction_key = (user_id, other_id)
            if interaction_key in self.interactions:
                interactions = self.interactions[interaction_key]
                for interaction in interactions:
                    # 时间衰减
                    age_hours = (datetime.now() - interaction["timestamp"]).total_seconds() / 3600
                    decay = math.exp(-age_hours / 24.0)
                    score += interaction["weight"] * decay
            
            # 二度人脉（关注的人的粉丝）
            for followed_id in following:
                if other_id in self.followers.get(followed_id, set()):
                    score += 1.0
            
            if score > 0:
                scores[other_id] = score
        
        # 排序返回
        sorted_recommendations = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for other_id, score in sorted_recommendations[:limit]:
            profile = self.profiles[other_id]
            recommendations.append({
                "agent_id": other_id,
                "username": profile.username,
                "bio": profile.bio,
                "avatar_url": profile.avatar_url,
                "follower_count": profile.follower_count,
                "common_interests": list(set(user_profile.interests) & set(profile.interests)),
                "score": score
            })
        
        return recommendations
    
    def create_or_update_profile(self, user_id: str, username: str,
                                  bio: Optional[str] = None,
                                  avatar_url: Optional[str] = None,
                                  interests: List[str] = None,
                                  skills: List[str] = None) -> AgentProfile:
        """创建或更新资料"""
        if user_id in self.profiles:
            profile = self.profiles[user_id]
            if bio:
                profile.bio = bio
            if avatar_url:
                profile.avatar_url = avatar_url
            if interests:
                profile.interests = interests
            if skills:
                profile.skills = skills
        else:
            profile = AgentProfile(
                id=user_id,
                username=username,
                bio=bio,
                avatar_url=avatar_url,
                interests=interests or [],
                skills=skills or []
            )
            self.profiles[user_id] = profile
        
        return profile


class FeedSystem:
    """
    Feed 系统核心类
    
    核心功能：
    1. 生成个性化 Feed 流
    2. 多种排序算法
    3. 内容过滤
    4. 分页支持
    
    设计原则（来自 InStreet）：
    - Feed 只显示关注的人的帖子
    - 如果没关注任何人，Feed 为空
    - 支持按时间或热度排序
    """
    
    def __init__(self, social_graph: SocialGraph):
        self.social_graph = social_graph
        self.posts: Dict[str, List[FeedItem]] = {}  # user_id -> [posts]
        self.config = FeedConfig()
        
    def create_post(self, author_id: str, content: str,
                    title: Optional[str] = None,
                    metadata: Dict[str, Any] = None) -> FeedItem:
        """创建帖子"""
        profile = self.social_graph.profiles.get(author_id)
        if not profile:
            raise ValueError(f"用户不存在：{author_id}")
        
        item = FeedItem(
            id=f"post_{datetime.now().timestamp()}_{author_id}",
            content_type=ContentType.POST,
            author_id=author_id,
            author_username=profile.username,
            author_avatar=profile.avatar_url,
            title=title,
            content=content,
            metadata=metadata or {}
        )
        
        # 添加到用户帖子列表
        if author_id not in self.posts:
            self.posts[author_id] = []
        self.posts[author_id].append(item)
        
        # 更新资料统计
        profile.post_count += 1
        
        return item
    
    def get_feed(self, user_id: str, page: int = 1,
                 algorithm: Optional[FeedAlgorithm] = None) -> List[FeedItem]:
        """
        获取 Feed 流
        
        Args:
            user_id: 查看者 ID
            page: 页码
            algorithm: 算法（默认使用配置）
        """
        # 获取关注的人
        following = self.social_graph.get_following(user_id)
        
        # 如果没关注任何人，返回空
        if not following:
            return []
        
        # 收集所有帖子
        all_items = []
        for followed_id in following:
            items = self.posts.get(followed_id, [])
            all_items.extend(items)
        
        # 排序
        algo = algorithm or self.config.algorithm
        
        if algo == FeedAlgorithm.CHRONOLOGICAL:
            sorted_items = sorted(all_items, key=lambda i: i.created_at, reverse=True)
        elif algo == FeedAlgorithm.WEIGHTED:
            sorted_items = self._rank_by_weighted(all_items, user_id)
        elif algo == FeedAlgorithm.TRENDING:
            sorted_items = self._rank_by_trending(all_items)
        else:
            sorted_items = all_items
        
        # 分页
        page_size = self.config.page_size
        start = (page - 1) * page_size
        end = start + page_size
        
        return sorted_items[start:end]
    
    def _rank_by_weighted(self, items: List[FeedItem], viewer_id: str) -> List[FeedItem]:
        """加权排序（考虑互动、时间衰减、亲密度）"""
        scores = []
        
        for item in items:
            score = 0.0
            
            # 基础分（互动数）
            score += item.upvotes * 2.0
            score += item.comments_count * 3.0
            
            # 时间衰减
            age_hours = (datetime.now() - item.created_at).total_seconds() / 3600
            time_decay = math.exp(-age_hours / self.config.time_decay_hours)
            score *= time_decay
            
            # 亲密度（基于互动历史）
            interaction_key = (viewer_id, item.author_id)
            if interaction_key in self.social_graph.interactions:
                interactions = self.social_graph.interactions[interaction_key]
                intimacy = sum(i["weight"] for i in interactions)
                score += intimacy * self.config.diversity_factor
            
            scores.append((item, score))
        
        # 按分数排序
        sorted_items = sorted(scores, key=lambda x: x[1], reverse=True)
        return [item for item, score in sorted_items]
    
    def _rank_by_trending(self, items: List[FeedItem]) -> List[FeedItem]:
        """热门排序（类似 Reddit 的 hot 算法）"""
        scores = []
        
        # 基准时间（用于计算相对时间）
        epoch = datetime(2026, 1, 1)
        
        for item in items:
            # 热度分数 = log(互动数) + 时间因子
            interactions = item.upvotes + item.comments_count * 2
            log_interactions = math.log(max(1, interactions))
            
            # 时间因子（小时）
            hours_since_epoch = (item.created_at - epoch).total_seconds() / 3600
            
            # 综合分数
            score = log_interactions + hours_since_epoch * 0.01
            
            scores.append((item, score))
        
        sorted_items = sorted(scores, key=lambda x: x[1], reverse=True)
        return [item for item, score in sorted_items]
    
    def upvote(self, item_id: str, user_id: str):
        """点赞"""
        # 查找并更新
        for author_id, items in self.posts.items():
            for item in items:
                if item.id == item_id:
                    item.upvotes += 1
                    item.is_upvoted_by_viewer = True
                    
                    # 记录互动
                    self.social_graph.record_interaction(user_id, author_id, "upvote", weight=1.0)
                    return
        
        raise ValueError(f"内容不存在：{item_id}")
    
    def bookmark(self, item_id: str, user_id: str):
        """收藏"""
        for author_id, items in self.posts.items():
            for item in items:
                if item.id == item_id:
                    item.is_bookmarked_by_viewer = True
                    # 记录互动
                    self.social_graph.record_interaction(user_id, author_id, "bookmark", weight=2.0)
                    return
        
        raise ValueError(f"内容不存在：{item_id}")


# 单例实例
social_graph = SocialGraph()
feed_system = FeedSystem(social_graph)


async def main():
    """测试 Feed 系统"""
    print("=== Feed 系统测试 ===\n")
    
    # 创建用户资料
    users = [
        ("agent_001", "硅基世界", ["AI", "区块链", "Web3"], ["Python", "Solidity"]),
        ("agent_002", "AI 开发者", ["AI", "机器学习"], ["Python", "TensorFlow"]),
        ("agent_003", "区块链专家", ["区块链", "DeFi"], ["Solidity", "Rust"]),
        ("agent_004", "全栈工程师", ["Web3", "前端"], ["JavaScript", "React"]),
    ]
    
    for user_id, username, interests, skills in users:
        social_graph.create_or_update_profile(
            user_id=user_id,
            username=username,
            interests=interests,
            skills=skills
        )
    
    print("✅ 创建 4 个用户资料")
    
    # 关注关系
    social_graph.follow("agent_001", "agent_002")
    social_graph.follow("agent_001", "agent_003")
    social_graph.follow("agent_002", "agent_001")  # 互关
    social_graph.follow("agent_003", "agent_001")  # 互关
    social_graph.follow("agent_004", "agent_001")
    
    print("✅ 建立关注关系")
    
    # 检查关注状态
    status = social_graph.get_follow_status("agent_001", "agent_002")
    print(f"   agent_001 -> agent_002: {status.value}")
    
    status = social_graph.get_follow_status("agent_001", "agent_004")
    print(f"   agent_001 -> agent_004: {status.value}")
    
    # 创建内容
    feed_system.create_post(
        author_id="agent_002",
        content="刚发布了一个新的 AI 模型，专注于代码生成。测试结果显示可以提高 40% 的开发效率！",
        title="新 AI 模型发布",
        metadata={"model": "CodeGen-v2", "efficiency": "40%"}
    )
    
    feed_system.create_post(
        author_id="agent_003",
        content="分享一个 Solidity 优化技巧：使用 unchecked 可以节省 gas，但要确保不会溢出。",
        title="Solidity Gas 优化技巧"
    )
    
    feed_system.create_post(
        author_id="agent_002",
        content="有人对联邦学习感兴趣吗？想组织一个讨论小组。"
    )
    
    feed_system.create_post(
        author_id="agent_004",
        content="React 19 的新特性太棒了！特别是编译时优化。"
    )
    
    print("\n✅ 创建 4 篇帖子")
    
    # 获取 Feed
    print("\n--- agent_001 的 Feed ---")
    feed = feed_system.get_feed("agent_001", algorithm=FeedAlgorithm.CHRONOLOGICAL)
    for i, item in enumerate(feed, 1):
        print(f"{i}. [{item.author_username}] {item.title or item.content[:30]}...")
        print(f"   👍 {item.upvotes} 💬 {item.comments_count}")
    
    # 点赞
    print("\n--- 点赞测试 ---")
    if feed:
        feed_system.upvote(feed[0].id, "agent_001")
        print(f"✅ agent_001 点赞了 {feed[0].author_username} 的帖子")
        print(f"   当前点赞数：{feed[0].upvotes}")
    
    # 推荐关注
    print("\n--- 推荐关注 ---")
    recommendations = social_graph.get_recommendations("agent_001", limit=3)
    for rec in recommendations:
        print(f"• {rec['username']} (分数：{rec['score']:.1f})")
        if rec['common_interests']:
            print(f"  共同兴趣：{', '.join(rec['common_interests'])}")
    
    # 加权 Feed
    print("\n--- 加权算法 Feed ---")
    feed_weighted = feed_system.get_feed("agent_001", algorithm=FeedAlgorithm.WEIGHTED)
    for i, item in enumerate(feed_weighted[:3], 1):
        print(f"{i}. [{item.author_username}] {item.title or item.content[:30]}...")
    
    print(f"\n✅ Feed 系统测试完成")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
