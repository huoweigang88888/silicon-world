"""
徽章和奖励系统

用户徽章、成就奖励和特殊物品管理
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import uuid


# ==================== 徽章类型 ====================

class BadgeRarity(str, Enum):
    """徽章稀有度"""
    COMMON = "common"  # 普通
    RARE = "rare"  # 稀有
    EPIC = "epic"  # 史诗
    LEGENDARY = "legendary"  # 传说
    MYTHIC = "mythic"  # 神话


class BadgeCategory(str, Enum):
    """徽章类别"""
    SOCIAL = "social"  # 社交
    ECONOMIC = "economic"  # 经济
    EXPLORATION = "exploration"  # 探索
    CREATION = "creation"  # 创造
    GOVERNANCE = "governance"  # 治理
    SPECIAL = "special"  # 特殊
    EVENT = "event"  # 活动


# ==================== 徽章模型 ====================

class Badge(BaseModel):
    """徽章定义"""
    id: str
    name: str
    description: str
    category: BadgeCategory
    rarity: BadgeRarity
    icon_url: Optional[str] = None
    requirement: Dict[str, Any] = {}  # 获取条件
    created_at: datetime = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow()
        super().__init__(**data)


class UserBadge(BaseModel):
    """用户徽章"""
    id: str
    user_id: str
    badge_id: str
    earned_at: datetime = None
    metadata: Dict[str, Any] = {}  # 额外信息
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        if 'earned_at' not in data:
            data['earned_at'] = datetime.utcnow()
        super().__init__(**data)


# ==================== 徽章库 ====================

class BadgeLibrary:
    """徽章库"""
    
    @staticmethod
    def get_all_badges() -> List[Badge]:
        """获取所有徽章"""
        return [
            # 社交类徽章
            Badge(
                id="social_friend",
                name="友善之人",
                description="拥有 10 个好友",
                category=BadgeCategory.SOCIAL,
                rarity=BadgeRarity.COMMON,
                requirement={"type": "count", "action": "friends", "target": 10},
                icon_url="badges/social_friend.png"
            ),
            Badge(
                id="social_influencer",
                name="社交达人",
                description="拥有 100 个好友",
                category=BadgeCategory.SOCIAL,
                rarity=BadgeRarity.RARE,
                requirement={"type": "count", "action": "friends", "target": 100},
                icon_url="badges/social_influencer.png"
            ),
            Badge(
                id="social_celebrity",
                name="社交名人",
                description="拥有 1000 个好友",
                category=BadgeCategory.SOCIAL,
                rarity=BadgeRarity.EPIC,
                requirement={"type": "count", "action": "friends", "target": 1000},
                icon_url="badges/social_celebrity.png"
            ),
            
            # 经济类徽章
            Badge(
                id="economic_trader",
                name="交易者",
                description="完成 10 笔交易",
                category=BadgeCategory.ECONOMIC,
                rarity=BadgeRarity.COMMON,
                requirement={"type": "count", "action": "trades", "target": 10},
                icon_url="badges/economic_trader.png"
            ),
            Badge(
                id="economic_merchant",
                name="商人",
                description="完成 100 笔交易",
                category=BadgeCategory.ECONOMIC,
                rarity=BadgeRarity.RARE,
                requirement={"type": "count", "action": "trades", "target": 100},
                icon_url="badges/economic_merchant.png"
            ),
            Badge(
                id="economic_tycoon",
                name="商业大亨",
                description="拥有 100 万 SIL",
                category=BadgeCategory.ECONOMIC,
                rarity=BadgeRarity.LEGENDARY,
                requirement={"type": "balance", "target": 1000000},
                icon_url="badges/economic_tycoon.png"
            ),
            
            # 探索类徽章
            Badge(
                id="exploration_scout",
                name="侦察兵",
                description="探索 10 个区域",
                category=BadgeCategory.EXPLORATION,
                rarity=BadgeRarity.COMMON,
                requirement={"type": "count", "action": "regions", "target": 10},
                icon_url="badges/exploration_scout.png"
            ),
            Badge(
                id="exploration_pioneer",
                name="先驱者",
                description="探索 50 个区域",
                category=BadgeCategory.EXPLORATION,
                rarity=BadgeRarity.RARE,
                requirement={"type": "count", "action": "regions", "target": 50},
                icon_url="badges/exploration_pioneer.png"
            ),
            Badge(
                id="exploration_legend",
                name="探索传奇",
                description="探索所有区域",
                category=BadgeCategory.EXPLORATION,
                rarity=BadgeRarity.MYTHIC,
                requirement={"type": "count", "action": "regions", "target": 100},
                icon_url="badges/exploration_legend.png"
            ),
            
            # 创造类徽章
            Badge(
                id="creation_creator",
                name="创作者",
                description="创作 10 个作品",
                category=BadgeCategory.CREATION,
                rarity=BadgeRarity.COMMON,
                requirement={"type": "count", "action": "creations", "target": 10},
                icon_url="badges/creation_creator.png"
            ),
            Badge(
                id="creation_artist",
                name="艺术家",
                description="创作 50 个作品",
                category=BadgeCategory.CREATION,
                rarity=BadgeRarity.RARE,
                requirement={"type": "count", "action": "creations", "target": 50},
                icon_url="badges/creation_artist.png"
            ),
            Badge(
                id="creation_master",
                name="创作大师",
                description="创作 100 个作品",
                category=BadgeCategory.CREATION,
                rarity=BadgeRarity.EPIC,
                requirement={"type": "count", "action": "creations", "target": 100},
                icon_url="badges/creation_master.png"
            ),
            
            # 治理类徽章
            Badge(
                id="governance_citizen",
                name="公民",
                description="参与 10 次投票",
                category=BadgeCategory.GOVERNANCE,
                rarity=BadgeRarity.COMMON,
                requirement={"type": "count", "action": "votes", "target": 10},
                icon_url="badges/governance_citizen.png"
            ),
            Badge(
                id="governance_leader",
                name="领袖",
                description="发起 5 个提案",
                category=BadgeCategory.GOVERNANCE,
                rarity=BadgeRarity.RARE,
                requirement={"type": "count", "action": "proposals", "target": 5},
                icon_url="badges/governance_leader.png"
            ),
            
            # 特殊徽章
            Badge(
                id="special_early_adopter",
                name="早期采用者",
                description="前 1000 名用户",
                category=BadgeCategory.SPECIAL,
                rarity=BadgeRarity.LEGENDARY,
                requirement={"type": "rank", "target": 1000},
                icon_url="badges/special_early_adopter.png"
            ),
            Badge(
                id="special_founder",
                name="创始人",
                description="前 100 名用户",
                category=BadgeCategory.SPECIAL,
                rarity=BadgeRarity.MYTHIC,
                requirement={"type": "rank", "target": 100},
                icon_url="badges/special_founder.png"
            ),
            Badge(
                id="special_beta_tester",
                name="测试者",
                description="参与 Beta 测试",
                category=BadgeCategory.SPECIAL,
                rarity=BadgeRarity.RARE,
                requirement={"type": "event", "event": "beta_test"},
                icon_url="badges/special_beta_tester.png"
            ),
            
            # 活动徽章
            Badge(
                id="event_launch",
                name="发布纪念",
                description="参与发布活动",
                category=BadgeCategory.EVENT,
                rarity=BadgeRarity.RARE,
                requirement={"type": "event", "event": "launch_2026"},
                icon_url="badges/event_launch.png"
            ),
            Badge(
                id="event_anniversary",
                name="周年纪念",
                description="参与一周年活动",
                category=BadgeCategory.EVENT,
                rarity=BadgeRarity.EPIC,
                requirement={"type": "event", "event": "anniversary_1"},
                icon_url="badges/event_anniversary.png"
            ),
        ]


# ==================== 奖励类型 ====================

class RewardType(str, Enum):
    """奖励类型"""
    TOKENS = "tokens"  # 代币
    EXP = "exp"  # 经验
    BADGE = "badge"  # 徽章
    NFT = "nft"  # NFT
    TITLE = "title"  # 称号
    ITEM = "item"  # 物品
    BOOST = "boost"  # 增益


class Reward(BaseModel):
    """奖励定义"""
    id: str
    name: str
    reward_type: RewardType
    amount: int = 1
    metadata: Dict[str, Any] = {}
    description: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        super().__init__(**data)


# ==================== 奖励管理器 ====================

class RewardManager:
    """
    奖励管理器
    
    管理奖励发放和用户资产
    """
    
    def __init__(self):
        self.badges: Dict[str, Badge] = {}
        self.user_badges: Dict[str, Dict[str, UserBadge]] = {}  # user_id -> {badge_id -> UserBadge}
        self.user_rewards: Dict[str, Dict[str, Any]] = {}  # user_id -> {type -> amount}
        
        # 加载徽章库
        self._load_badges()
    
    def _load_badges(self):
        """加载徽章"""
        for badge in BadgeLibrary.get_all_badges():
            self.badges[badge.id] = badge
    
    def get_or_create_user(self, user_id: str):
        """初始化用户数据"""
        if user_id not in self.user_badges:
            self.user_badges[user_id] = {}
        if user_id not in self.user_rewards:
            self.user_rewards[user_id] = {
                "tokens": 0,
                "exp": 0,
                "titles": [],
                "items": []
            }
    
    def award_badge(self, user_id: str, badge_id: str, metadata: Dict[str, Any] = None) -> Optional[UserBadge]:
        """
        授予用户徽章
        
        Args:
            user_id: 用户 ID
            badge_id: 徽章 ID
            metadata: 额外信息
        
        Returns:
            用户徽章，如果已拥有返回 None
        """
        self.get_or_create_user(user_id)
        
        if badge_id not in self.badges:
            return None
        
        if badge_id in self.user_badges[user_id]:
            return None  # 已拥有
        
        user_badge = UserBadge(
            user_id=user_id,
            badge_id=badge_id,
            metadata=metadata or {}
        )
        self.user_badges[user_id][badge_id] = user_badge
        return user_badge
    
    def award_tokens(self, user_id: str, amount: int, reason: str = "") -> int:
        """
        奖励代币
        
        Args:
            user_id: 用户 ID
            amount: 数量
            reason: 原因
        
        Returns:
            新的代币余额
        """
        self.get_or_create_user(user_id)
        self.user_rewards[user_id]["tokens"] += amount
        return self.user_rewards[user_id]["tokens"]
    
    def award_exp(self, user_id: str, amount: int, reason: str = "") -> int:
        """
        奖励经验
        
        Args:
            user_id: 用户 ID
            amount: 数量
            reason: 原因
        
        Returns:
            新的经验值
        """
        self.get_or_create_user(user_id)
        self.user_rewards[user_id]["exp"] += amount
        return self.user_rewards[user_id]["exp"]
    
    def award_title(self, user_id: str, title: str) -> bool:
        """
        授予称号
        
        Args:
            user_id: 用户 ID
            title: 称号
        
        Returns:
            是否成功
        """
        self.get_or_create_user(user_id)
        if title not in self.user_rewards[user_id]["titles"]:
            self.user_rewards[user_id]["titles"].append(title)
            return True
        return False
    
    def distribute_reward(self, user_id: str, reward: Dict[str, Any]) -> Dict[str, Any]:
        """
        分发奖励
        
        Args:
            user_id: 用户 ID
            reward: 奖励字典
        
        Returns:
            实际获得的奖励
        """
        self.get_or_create_user(user_id)
        result = {}
        
        if "tokens" in reward:
            result["tokens"] = self.award_tokens(user_id, reward["tokens"])
        
        if "exp" in reward:
            result["exp"] = self.award_exp(user_id, reward["exp"])
        
        if "badge" in reward:
            badge = self.award_badge(user_id, reward["badge"])
            result["badge"] = badge.badge_id if badge else None
        
        if "title" in reward:
            result["title"] = self.award_title(user_id, reward["title"])
        
        return result
    
    def get_user_badges(self, user_id: str) -> List[UserBadge]:
        """获取用户的徽章"""
        self.get_or_create_user(user_id)
        return list(self.user_badges.get(user_id, {}).values())
    
    def get_user_balance(self, user_id: str) -> Dict[str, Any]:
        """获取用户资产"""
        self.get_or_create_user(user_id)
        return self.user_rewards[user_id].copy()
    
    def get_badge(self, badge_id: str) -> Optional[Badge]:
        """获取徽章定义"""
        return self.badges.get(badge_id)
    
    def get_statistics(self, user_id: str) -> Dict[str, Any]:
        """获取用户统计"""
        self.get_or_create_user(user_id)
        badges = self.get_user_badges(user_id)
        
        # 按稀有度统计
        by_rarity = {}
        by_category = {}
        
        for ub in badges:
            badge = self.get_badge(ub.badge_id)
            if badge:
                rarity = badge.rarity.value
                by_rarity[rarity] = by_rarity.get(rarity, 0) + 1
                
                category = badge.category.value
                by_category[category] = by_category.get(category, 0) + 1
        
        return {
            "total_badges": len(badges),
            "tokens": self.user_rewards[user_id]["tokens"],
            "exp": self.user_rewards[user_id]["exp"],
            "titles": len(self.user_rewards[user_id]["titles"]),
            "by_rarity": by_rarity,
            "by_category": by_category
        }


# 使用示例
if __name__ == "__main__":
    # 创建奖励管理器
    mgr = RewardManager()
    
    user_id = "user_1"
    
    print("可用徽章:")
    for badge in mgr.badges.values():
        print(f"  [{badge.rarity.value}] {badge.name} - {badge.description}")
    print()
    
    # 授予徽章
    print("授予用户徽章:")
    badge = mgr.award_badge(user_id, "social_friend")
    if badge:
        print(f"  ✅ 获得：{badge.badge_id}")
    
    # 奖励代币和经验
    print("\n奖励代币和经验:")
    tokens = mgr.award_tokens(user_id, 1000, "任务奖励")
    exp = mgr.award_exp(user_id, 500, "成就解锁")
    print(f"  💰 代币：{tokens}")
    print(f"  ⭐ 经验：{exp}")
    
    # 分发复合奖励
    print("\n分发复合奖励:")
    result = mgr.distribute_reward(user_id, {
        "tokens": 500,
        "exp": 200,
        "badge": "economic_trader",
        "title": "新手大师"
    })
    print(f"  奖励结果：{result}")
    
    # 获取统计
    print("\n用户统计:")
    stats = mgr.get_statistics(user_id)
    for key, value in stats.items():
        print(f"  {key}: {value}")
