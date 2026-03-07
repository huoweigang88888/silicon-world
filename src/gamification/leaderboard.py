"""
排行榜系统

用户排名和积分管理
"""

from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel
from datetime import datetime, timedelta
from enum import Enum
import uuid


# ==================== 排行榜类型 ====================

class LeaderboardType(str, Enum):
    """排行榜类型"""
    WEALTH = "wealth"  # 财富榜
    SOCIAL = "social"  # 社交榜
    CREATION = "creation"  # 创作榜
    GOVERNANCE = "governance"  # 治理榜
    EXPLORATION = "exploration"  # 探索榜
    COMPREHENSIVE = "comprehensive"  # 综合榜


class TimePeriod(str, Enum):
    """时间周期"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ALL_TIME = "all_time"


# ==================== 用户积分 ====================

class UserPoints(BaseModel):
    """用户积分"""
    user_id: str
    total_points: int = 0
    daily_points: int = 0
    weekly_points: int = 0
    monthly_points: int = 0
    last_updated: datetime = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'last_updated' not in data:
            data['last_updated'] = datetime.utcnow()
        super().__init__(**data)
    
    def add_points(self, points: int):
        """添加积分"""
        self.total_points += points
        self.daily_points += points
        self.weekly_points += points
        self.monthly_points += points
        self.last_updated = datetime.utcnow()
    
    def reset_period(self, period: str):
        """重置周期积分"""
        if period == "daily":
            self.daily_points = 0
        elif period == "weekly":
            self.weekly_points = 0
        elif period == "monthly":
            self.monthly_points = 0


# ==================== 排行榜管理器 ====================

class LeaderboardManager:
    """
    排行榜管理器
    
    管理各种排行榜
    """
    
    def __init__(self):
        self.user_points: Dict[str, UserPoints] = {}
        self.rankings: Dict[str, Dict[str, List[Tuple[str, int]]]] = {}  # type -> period -> [(user_id, points)]
    
    def get_or_create_user(self, user_id: str) -> UserPoints:
        """获取或创建用户积分"""
        if user_id not in self.user_points:
            self.user_points[user_id] = UserPoints(user_id=user_id)
        return self.user_points[user_id]
    
    def add_points(
        self,
        user_id: str,
        points: int,
        reason: str = ""
    ):
        """
        添加积分
        
        Args:
            user_id: 用户 ID
            points: 积分
            reason: 原因
        """
        user = self.get_or_create_user(user_id)
        user.add_points(points)
        
        # 更新排行榜
        self._update_rankings()
    
    def _update_rankings(self):
        """更新排行榜"""
        # 按总积分排序
        all_users = [
            (user_id, points.total_points)
            for user_id, points in self.user_points.items()
        ]
        all_users.sort(key=lambda x: x[1], reverse=True)
        
        if "comprehensive" not in self.rankings:
            self.rankings["comprehensive"] = {}
        self.rankings["comprehensive"]["all_time"] = all_users
        
        # TODO: 按周期排序
        # 这里简化处理，实际应该按天/周/月分别统计
    
    def get_ranking(
        self,
        leaderboard_type: LeaderboardType = LeaderboardType.COMPREHENSIVE,
        period: TimePeriod = TimePeriod.ALL_TIME,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取排行榜
        
        Args:
            leaderboard_type: 排行榜类型
            period: 时间周期
            limit: 返回数量
        
        Returns:
            排行榜列表
        """
        type_key = leaderboard_type.value
        period_key = period.value
        
        rankings = self.rankings.get(type_key, {}).get(period_key, [])
        
        # 返回前 N 名
        result = []
        for rank, (user_id, points) in enumerate(rankings[:limit], 1):
            user = self.user_points.get(user_id)
            result.append({
                "rank": rank,
                "user_id": user_id,
                "points": points,
                "daily_points": user.daily_points if user else 0,
                "weekly_points": user.weekly_points if user else 0,
                "monthly_points": user.monthly_points if user else 0
            })
        
        return result
    
    def get_user_rank(
        self,
        user_id: str,
        leaderboard_type: LeaderboardType = LeaderboardType.COMPREHENSIVE,
        period: TimePeriod = TimePeriod.ALL_TIME
    ) -> Optional[Dict[str, Any]]:
        """
        获取用户排名
        
        Args:
            user_id: 用户 ID
            leaderboard_type: 排行榜类型
            period: 时间周期
        
        Returns:
            用户排名信息
        """
        type_key = leaderboard_type.value
        period_key = period.value
        
        rankings = self.rankings.get(type_key, {}).get(period_key, [])
        
        for rank, (uid, points) in enumerate(rankings, 1):
            if uid == user_id:
                user = self.user_points.get(user_id)
                return {
                    "rank": rank,
                    "user_id": user_id,
                    "points": points,
                    "percentile": (len(rankings) - rank) / len(rankings) * 100 if rankings else 0
                }
        
        return None
    
    def get_top_users(
        self,
        limit: int = 10,
        period: TimePeriod = TimePeriod.ALL_TIME
    ) -> List[Dict[str, Any]]:
        """
        获取顶级用户
        
        Args:
            limit: 返回数量
            period: 时间周期
        
        Returns:
            顶级用户列表
        """
        return self.get_ranking(
            LeaderboardType.COMPREHENSIVE,
            period,
            limit
        )
    
    def reset_period(self, period: str):
        """重置周期积分"""
        for user in self.user_points.values():
            user.reset_period(period)
        
        # 重新计算排行榜
        self._update_rankings()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取排行榜统计"""
        return {
            "total_users": len(self.user_points),
            "total_points_awarded": sum(p.total_points for p in self.user_points.values()),
            "rankings_available": len(self.rankings),
            "last_updated": datetime.utcnow().isoformat()
        }


# ==================== 积分规则 ====================

class PointsRules:
    """积分规则"""
    
    @staticmethod
    def get_default_rules() -> Dict[str, int]:
        """获取默认积分规则"""
        return {
            # 社交行为
            "add_friend": 10,
            "send_message": 1,
            "receive_message": 1,
            
            # 经济行为
            "first_trade": 100,
            "trade_volume": 1,  # 每 1000 代币 1 分
            "list_item": 5,
            
            # 探索行为
            "visit_region": 10,
            "first_explore": 50,
            
            # 创造行为
            "create_item": 20,
            "create_artwork": 50,
            
            # 治理行为
            "create_proposal": 100,
            "vote": 10,
            
            # 登录奖励
            "daily_login": 5,
            "weekly_login": 50,
            "monthly_login": 200,
        }


# 使用示例
if __name__ == "__main__":
    # 创建排行榜管理器
    mgr = LeaderboardManager()
    
    print("模拟用户行为...")
    
    # 模拟 10 个用户
    for i in range(1, 11):
        user_id = f"user_{i}"
        
        # 添加不同积分
        points = (10 - i) * 100 + i * 50
        mgr.add_points(user_id, points, "模拟积分")
    
    # 获取排行榜
    print("\n综合排行榜 (前 10 名):")
    ranking = mgr.get_ranking(limit=10)
    for entry in ranking:
        print(f"  #{entry['rank']}: {entry['user_id']} - {entry['points']} 分")
    
    # 获取用户排名
    print("\nuser_5 的排名:")
    rank_info = mgr.get_user_rank("user_5")
    if rank_info:
        print(f"  排名：#{rank_info['rank']}")
        print(f"  积分：{rank_info['points']}")
        print(f"  百分位：{rank_info['percentile']:.1f}%")
    
    # 获取统计
    print("\n排行榜统计:")
    stats = mgr.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
