"""
成就系统

用户成就和徽章管理
"""

from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import uuid


# ==================== 成就类型 ====================

class AchievementType(str, Enum):
    """成就类型"""
    SOCIAL = "social"  # 社交类
    ECONOMIC = "economic"  # 经济类
    EXPLORATION = "exploration"  # 探索类
    CREATION = "creation"  # 创造类
    GOVERNANCE = "governance"  # 治理类
    SPECIAL = "special"  # 特殊类


class AchievementTier(str, Enum):
    """成就等级"""
    BRONZE = "bronze"  # 铜牌
    SILVER = "silver"  # 银牌
    GOLD = "gold"  # 金牌
    PLATINUM = "platinum"  # 铂金
    DIAMOND = "diamond"  # 钻石


# ==================== 成就模型 ====================

class Achievement(BaseModel):
    """成就定义"""
    id: str
    name: str
    description: str
    achievement_type: AchievementType
    tier: AchievementTier = AchievementTier.BRONZE
    requirement: Dict[str, Any] = {}  # 达成条件
    reward: Dict[str, Any] = {}  # 奖励
    icon_url: Optional[str] = None
    created_at: datetime = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow()
        super().__init__(**data)


class UserAchievement(BaseModel):
    """用户成就"""
    id: str
    user_id: str
    achievement_id: str
    unlocked_at: datetime = None
    progress: float = 0.0  # 进度 0-1
    is_unlocked: bool = False
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        super().__init__(**data)
    
    def update_progress(self, current_value: float, required_value: float):
        """更新进度"""
        self.progress = min(1.0, current_value / required_value)
        if self.progress >= 1.0:
            self.is_unlocked = True
            if not self.unlocked_at:
                self.unlocked_at = datetime.utcnow()


# ==================== 成就库 ====================

class AchievementLibrary:
    """成就库"""
    
    @staticmethod
    def get_default_achievements() -> List[Achievement]:
        """获取默认成就列表"""
        return [
            # 社交类成就
            Achievement(
                id="social_first_friend",
                name="第一个朋友",
                description="添加第一个好友",
                achievement_type=AchievementType.SOCIAL,
                tier=AchievementTier.BRONZE,
                requirement={"type": "count", "action": "add_friend", "target": 1},
                reward={"tokens": 100},
                icon_url="icons/social_first_friend.png"
            ),
            Achievement(
                id="social_popular",
                name="人气王",
                description="拥有 100 个好友",
                achievement_type=AchievementType.SOCIAL,
                tier=AchievementTier.GOLD,
                requirement={"type": "count", "action": "add_friend", "target": 100},
                reward={"tokens": 1000, "badge": "popular"},
                icon_url="icons/social_popular.png"
            ),
            
            # 经济类成就
            Achievement(
                id="economic_first_trade",
                name="第一桶金",
                description="完成第一次交易",
                achievement_type=AchievementType.ECONOMIC,
                tier=AchievementTier.BRONZE,
                requirement={"type": "count", "action": "trade", "target": 1},
                reward={"tokens": 50},
                icon_url="icons/economic_first_trade.png"
            ),
            Achievement(
                id="economic_millionaire",
                name="百万富翁",
                description="拥有 100 万代币",
                achievement_type=AchievementType.ECONOMIC,
                tier=AchievementTier.PLATINUM,
                requirement={"type": "balance", "target": 1000000},
                reward={"tokens": 10000, "badge": "millionaire"},
                icon_url="icons/economic_millionaire.png"
            ),
            
            # 探索类成就
            Achievement(
                id="exploration_first_step",
                name="第一步",
                description="第一次探索世界",
                achievement_type=AchievementType.EXPLORATION,
                tier=AchievementTier.BRONZE,
                requirement={"type": "count", "action": "explore", "target": 1},
                reward={"tokens": 50},
                icon_url="icons/exploration_first_step.png"
            ),
            Achievement(
                id="exploration_world_traveler",
                name="环游世界",
                description="探索 50 个区域",
                achievement_type=AchievementType.EXPLORATION,
                tier=AchievementTier.GOLD,
                requirement={"type": "count", "action": "visit_region", "target": 50},
                reward={"tokens": 5000, "badge": "traveler"},
                icon_url="icons/exploration_world_traveler.png"
            ),
            
            # 创造类成就
            Achievement(
                id="creation_first_work",
                name="处女作",
                description="创作第一个作品",
                achievement_type=AchievementType.CREATION,
                tier=AchievementTier.BRONZE,
                requirement={"type": "count", "action": "create", "target": 1},
                reward={"tokens": 100},
                icon_url="icons/creation_first_work.png"
            ),
            Achievement(
                id="creation_master",
                name="创作大师",
                description="创作 100 个作品",
                achievement_type=AchievementType.CREATION,
                tier=AchievementTier.DIAMOND,
                requirement={"type": "count", "action": "create", "target": 100},
                reward={"tokens": 50000, "badge": "master"},
                icon_url="icons/creation_master.png"
            ),
            
            # 治理类成就
            Achievement(
                id="governance_first_vote",
                name="公民责任",
                description="第一次投票",
                achievement_type=AchievementType.GOVERNANCE,
                tier=AchievementTier.BRONZE,
                requirement={"type": "count", "action": "vote", "target": 1},
                reward={"tokens": 100},
                icon_url="icons/governance_first_vote.png"
            ),
            
            # 特殊成就
            Achievement(
                id="special_early_adopter",
                name="早期采用者",
                description="前 1000 名用户",
                achievement_type=AchievementType.SPECIAL,
                tier=AchievementTier.PLATINUM,
                requirement={"type": "rank", "target": 1000},
                reward={"tokens": 10000, "badge": "early_adopter", "nft": "early_adopter_nft"},
                icon_url="icons/special_early_adopter.png"
            )
        ]


# ==================== 成就管理器 ====================

class AchievementManager:
    """
    成就管理器
    
    管理用户成就的解锁和进度
    """
    
    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self.user_achievements: Dict[str, Dict[str, UserAchievement]] = {}  # user_id -> {achievement_id -> UserAchievement}
        
        # 加载默认成就
        self._load_default_achievements()
    
    def _load_default_achievements(self):
        """加载默认成就"""
        for achievement in AchievementLibrary.get_default_achievements():
            self.achievements[achievement.id] = achievement
    
    def register_achievement(self, achievement: Achievement):
        """注册成就"""
        self.achievements[achievement.id] = achievement
    
    def get_user_achievements(self, user_id: str) -> List[UserAchievement]:
        """获取用户的所有成就"""
        return list(self.user_achievements.get(user_id, {}).values())
    
    def get_unlocked_achievements(self, user_id: str) -> List[UserAchievement]:
        """获取用户已解锁的成就"""
        return [
            ua for ua in self.user_achievements.get(user_id, {}).values()
            if ua.is_unlocked
        ]
    
    def update_progress(
        self,
        user_id: str,
        action: str,
        current_value: float
    ) -> List[Achievement]:
        """
        更新成就进度
        
        Args:
            user_id: 用户 ID
            action: 行为类型
            current_value: 当前值
        
        Returns:
            新解锁的成就列表
        """
        newly_unlocked = []
        
        # 初始化用户成就
        if user_id not in self.user_achievements:
            self.user_achievements[user_id] = {}
        
        # 遍历所有成就
        for achievement in self.achievements.values():
            # 检查是否匹配行为
            req = achievement.requirement
            if req.get("action") != action:
                continue
            
            # 获取或创建用户成就
            if achievement.id not in self.user_achievements[user_id]:
                self.user_achievements[user_id][achievement.id] = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id
                )
            
            user_achievement = self.user_achievements[user_id][achievement.id]
            
            # 如果已解锁，跳过
            if user_achievement.is_unlocked:
                continue
            
            # 更新进度
            target = req.get("target", 0)
            user_achievement.update_progress(current_value, target)
            
            # 检查是否解锁
            if user_achievement.is_unlocked:
                newly_unlocked.append(achievement)
        
        return newly_unlocked
    
    def check_and_unlock(
        self,
        user_id: str,
        condition_type: str,
        **kwargs
    ) -> List[Achievement]:
        """
        检查并解锁成就
        
        Args:
            user_id: 用户 ID
            condition_type: 条件类型
            **kwargs: 条件参数
        
        Returns:
            新解锁的成就列表
        """
        newly_unlocked = []
        
        if user_id not in self.user_achievements:
            self.user_achievements[user_id] = {}
        
        for achievement in self.achievements.values():
            req = achievement.requirement
            
            # 检查条件类型
            if req.get("type") != condition_type:
                continue
            
            # 获取或创建用户成就
            if achievement.id not in self.user_achievements[user_id]:
                self.user_achievements[user_id][achievement.id] = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id
                )
            
            user_achievement = self.user_achievements[user_id][achievement.id]
            
            if user_achievement.is_unlocked:
                continue
            
            # 检查条件
            target = req.get("target", 0)
            current_value = kwargs.get("value", 0)
            
            if condition_type == "balance":
                user_achievement.update_progress(current_value, target)
            elif condition_type == "rank":
                rank = kwargs.get("rank", 999999)
                user_achievement.update_progress(1 if rank <= target else 0, 1)
            
            if user_achievement.is_unlocked:
                newly_unlocked.append(achievement)
        
        return newly_unlocked
    
    def get_achievement(self, achievement_id: str) -> Optional[Achievement]:
        """获取成就定义"""
        return self.achievements.get(achievement_id)
    
    def get_statistics(self, user_id: str) -> Dict[str, Any]:
        """获取用户成就统计"""
        all_achievements = self.get_user_achievements(user_id)
        unlocked = self.get_unlocked_achievements(user_id)
        
        # 按类型统计
        by_type = {}
        by_tier = {}
        
        for ua in unlocked:
            achievement = self.get_achievement(ua.achievement_id)
            if achievement:
                # 按类型
                type_name = achievement.achievement_type.value
                by_type[type_name] = by_type.get(type_name, 0) + 1
                
                # 按等级
                tier_name = achievement.tier.value
                by_tier[tier_name] = by_tier.get(tier_name, 0) + 1
        
        return {
            "total_achievements": len(all_achievements),
            "unlocked_count": len(unlocked),
            "locked_count": len(all_achievements) - len(unlocked),
            "completion_rate": len(unlocked) / len(self.achievements) if self.achievements else 0,
            "by_type": by_type,
            "by_tier": by_tier
        }


# 使用示例
if __name__ == "__main__":
    # 创建成就管理器
    mgr = AchievementManager()
    
    print("默认成就列表:")
    for ach in mgr.achievements.values():
        print(f"  {ach.name} ({ach.tier.value}): {ach.description}")
    
    # 模拟用户行为
    print("\n模拟用户行为...")
    user_id = "user_1"
    
    # 添加好友
    print("\n添加第一个好友...")
    unlocked = mgr.update_progress(user_id, "add_friend", 1)
    for ach in unlocked:
        print(f"  🏆 解锁成就：{ach.name} - 奖励：{ach.reward}")
    
    # 第一次交易
    print("\n完成第一次交易...")
    unlocked = mgr.update_progress(user_id, "trade", 1)
    for ach in unlocked:
        print(f"  🏆 解锁成就：{ach.name} - 奖励：{ach.reward}")
    
    # 第一次探索
    print("\n第一次探索...")
    unlocked = mgr.update_progress(user_id, "explore", 1)
    for ach in unlocked:
        print(f"  🏆 解锁成就：{ach.name} - 奖励：{ach.reward}")
    
    # 获取统计
    print("\n成就统计:")
    stats = mgr.get_statistics(user_id)
    print(f"  总成就：{stats['total_achievements']}")
    print(f"  已解锁：{stats['unlocked_count']}")
    print(f"  完成率：{stats['completion_rate']:.1%}")
    print(f"  按类型：{stats['by_type']}")
