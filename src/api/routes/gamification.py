"""
游戏化 API 路由

成就、排行榜、每日任务、徽章和奖励的 REST API
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime

# 导入游戏化模块
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.gamification.achievements import AchievementManager, Achievement, AchievementType, AchievementTier
from src.gamification.leaderboard import LeaderboardManager, LeaderboardType, TimePeriod
from src.gamification.daily_tasks import DailyTaskManager, TaskType, TaskDifficulty
from src.gamification.rewards import RewardManager, BadgeCategory, BadgeRarity


router = APIRouter(prefix="/api/v1/gamification", tags=["游戏化"])


# ==================== 依赖注入 ====================

# 单例管理器
achievement_mgr = AchievementManager()
leaderboard_mgr = LeaderboardManager()
task_mgr = DailyTaskManager()
reward_mgr = RewardManager()


def get_user_id(x_user_id: Optional[str] = Header(None, alias="X-User-ID")) -> str:
    """获取用户 ID"""
    if not x_user_id:
        raise HTTPException(status_code=400, detail="Missing X-User-ID header")
    return x_user_id


# ==================== 请求/响应模型 ====================

class ActionUpdate(BaseModel):
    """行为更新请求"""
    action: str
    value: int = 1
    metadata: Dict[str, Any] = {}


class RewardClaim(BaseModel):
    """奖励领取请求"""
    task_id: Optional[str] = None
    achievement_id: Optional[str] = None


# ==================== 成就端点 ====================

@router.get("/achievements")
async def get_achievements(
    user_id: str = Depends(get_user_id),
    include_locked: bool = True
):
    """
    获取用户成就列表
    
    - **user_id**: 用户 ID (通过 Header 传递)
    - **include_locked**: 是否包含未解锁的成就
    """
    if include_locked:
        achievements = achievement_mgr.get_user_achievements(user_id)
    else:
        achievements = achievement_mgr.get_unlocked_achievements(user_id)
    
    return {
        "count": len(achievements),
        "achievements": [
            {
                "id": ua.achievement_id,
                "name": achievement_mgr.get_achievement(ua.achievement_id).name if achievement_mgr.get_achievement(ua.achievement_id) else "Unknown",
                "progress": ua.progress,
                "is_unlocked": ua.is_unlocked,
                "unlocked_at": ua.unlocked_at.isoformat() if ua.unlocked_at else None
            }
            for ua in achievements
        ]
    }


@router.get("/achievements/statistics")
async def get_achievement_statistics(user_id: str = Depends(get_user_id)):
    """获取用户成就统计"""
    stats = achievement_mgr.get_statistics(user_id)
    return stats


@router.post("/achievements/update")
async def update_achievement_progress(
    update: ActionUpdate,
    user_id: str = Depends(get_user_id)
):
    """
    更新成就进度
    
    当用户完成某个行为时调用此接口
    """
    newly_unlocked = achievement_mgr.update_progress(
        user_id,
        update.action,
        update.value
    )
    
    # 如果有新解锁的成就，发放奖励
    rewards = []
    for achievement in newly_unlocked:
        reward_result = reward_mgr.distribute_reward(user_id, achievement.reward)
        rewards.append({
            "achievement_id": achievement.id,
            "achievement_name": achievement.name,
            "rewards": reward_result
        })
    
    return {
        "newly_unlocked": [
            {
                "id": a.id,
                "name": a.name,
                "tier": a.tier.value,
                "reward": a.reward
            }
            for a in newly_unlocked
        ],
        "rewards_distributed": rewards
    }


# ==================== 排行榜端点 ====================

@router.get("/leaderboard")
async def get_leaderboard(
    type: str = "comprehensive",
    period: str = "all_time",
    limit: int = 100
):
    """
    获取排行榜
    
    - **type**: 排行榜类型 (comprehensive, wealth, social, creation, etc.)
    - **period**: 时间周期 (daily, weekly, monthly, all_time)
    - **limit**: 返回数量
    """
    try:
        leaderboard_type = LeaderboardType(type)
    except ValueError:
        leaderboard_type = LeaderboardType.COMPREHENSIVE
    
    try:
        time_period = TimePeriod(period)
    except ValueError:
        time_period = TimePeriod.ALL_TIME
    
    ranking = leaderboard_mgr.get_ranking(leaderboard_type, time_period, limit)
    
    return {
        "type": type,
        "period": period,
        "count": len(ranking),
        "ranking": ranking
    }


@router.get("/leaderboard/my-rank")
async def get_my_rank(
    type: str = "comprehensive",
    period: str = "all_time",
    user_id: str = Depends(get_user_id)
):
    """获取我的排名"""
    try:
        leaderboard_type = LeaderboardType(type)
    except ValueError:
        leaderboard_type = LeaderboardType.COMPREHENSIVE
    
    try:
        time_period = TimePeriod(period)
    except ValueError:
        time_period = TimePeriod.ALL_TIME
    
    rank_info = leaderboard_mgr.get_user_rank(user_id, leaderboard_type, time_period)
    
    if not rank_info:
        return {"rank": None, "message": "Not ranked yet"}
    
    return rank_info


@router.post("/leaderboard/add-points")
async def add_points(
    points: int,
    reason: str = "",
    user_id: str = Depends(get_user_id)
):
    """添加积分"""
    leaderboard_mgr.add_points(user_id, points, reason)
    return {
        "success": True,
        "points_added": points,
        "reason": reason
    }


# ==================== 每日任务端点 ====================

@router.get("/daily-tasks")
async def get_daily_tasks(user_id: str = Depends(get_user_id)):
    """获取每日任务列表"""
    task_mgr.check_and_reset(user_id)
    tasks = task_mgr.get_or_create_user(user_id)
    
    return {
        "count": len(tasks),
        "expires_at": tasks[0].expires_at.isoformat() if tasks else None,
        "tasks": [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "type": t.task_type.value,
                "difficulty": t.difficulty.value,
                "progress": t.progress,
                "target": t.requirement.get("target", 0),
                "is_completed": t.is_completed,
                "is_claimed": t.is_claimed,
                "reward": t.reward
            }
            for t in tasks
        ]
    }


@router.post("/daily-tasks/update")
async def update_task_progress(
    update: ActionUpdate,
    user_id: str = Depends(get_user_id)
):
    """更新任务进度"""
    newly_completed = task_mgr.update_progress(user_id, update.action, update.value)
    
    return {
        "newly_completed": [
            {
                "id": t.id,
                "name": t.name,
                "reward": t.reward
            }
            for t in newly_completed
        ]
    }


@router.post("/daily-tasks/claim")
async def claim_task_reward(
    task_id: str,
    user_id: str = Depends(get_user_id)
):
    """领取任务奖励"""
    reward = task_mgr.claim_reward(user_id, task_id)
    
    if not reward:
        raise HTTPException(status_code=400, detail="Task not completed or reward already claimed")
    
    # 发放奖励
    reward_result = reward_mgr.distribute_reward(user_id, reward)
    
    return {
        "success": True,
        "reward": reward,
        "distributed": reward_result
    }


@router.get("/daily-tasks/statistics")
async def get_task_statistics(user_id: str = Depends(get_user_id)):
    """获取任务统计"""
    stats = task_mgr.get_user_stats(user_id)
    return stats


@router.post("/daily-tasks/login")
async def check_login(user_id: str = Depends(get_user_id)):
    """检查登录并更新连续登录"""
    login_info = task_mgr.check_login(user_id)
    
    # 如果是新登录，更新登录任务进度
    if login_info.get("is_new_streak"):
        task_mgr.update_progress(user_id, "login", 1)
        
        # 检查连续登录奖励
        streak = login_info["streak"]
        if streak == 7:
            reward = {"tokens": 200, "exp": 100}
            reward_mgr.distribute_reward(user_id, reward)
            login_info["bonus"] = reward
        elif streak == 30:
            reward = {"tokens": 1000, "exp": 500, "badge": "loyal"}
            reward_mgr.distribute_reward(user_id, reward)
            login_info["bonus"] = reward
    
    return login_info


# ==================== 徽章端点 ====================

@router.get("/badges")
async def get_badges(user_id: str = Depends(get_user_id)):
    """获取用户徽章列表"""
    badges = reward_mgr.get_user_badges(user_id)
    
    return {
        "count": len(badges),
        "badges": [
            {
                "id": b.badge_id,
                "earned_at": b.earned_at.isoformat(),
                "metadata": b.metadata
            }
            for b in badges
        ]
    }


@router.get("/badges/statistics")
async def get_badge_statistics(user_id: str = Depends(get_user_id)):
    """获取徽章统计"""
    stats = reward_mgr.get_statistics(user_id)
    return stats


@router.get("/balance")
async def get_balance(user_id: str = Depends(get_user_id)):
    """获取用户资产余额"""
    balance = reward_mgr.get_user_balance(user_id)
    return balance


# ==================== 综合端点 ====================

@router.get("/profile")
async def get_gamification_profile(user_id: str = Depends(get_user_id)):
    """
    获取用户游戏化综合档案
    
    包含成就、排行榜、任务、徽章等所有信息
    """
    return {
        "user_id": user_id,
        "achievements": achievement_mgr.get_statistics(user_id),
        "leaderboard": leaderboard_mgr.get_user_rank(user_id),
        "tasks": task_mgr.get_user_stats(user_id),
        "badges": reward_mgr.get_statistics(user_id),
        "balance": reward_mgr.get_user_balance(user_id)
    }


@router.get("/statistics")
async def get_system_statistics():
    """获取系统游戏化统计"""
    return {
        "achievements": {
            "total": len(achievement_mgr.achievements),
            "by_type": {},
            "by_tier": {}
        },
        "leaderboard": leaderboard_mgr.get_statistics(),
        "tasks": {
            "templates": len(task_mgr.templates)
        },
        "badges": {
            "total": len(reward_mgr.badges),
            "by_category": {},
            "by_rarity": {}
        }
    }


# ==================== 初始化示例数据 ====================

def init_example_data():
    """初始化示例数据用于测试"""
    # 模拟一些用户数据
    for i in range(1, 11):
        user_id = f"user_{i}"
        
        # 添加积分
        leaderboard_mgr.add_points(user_id, (10 - i) * 100 + i * 50, "示例积分")
        
        # 模拟一些成就进度
        achievement_mgr.update_progress(user_id, "add_friend", i * 2)
        achievement_mgr.update_progress(user_id, "trade", i)
        
        # 模拟登录
        for _ in range(i):
            task_mgr.check_login(user_id)
        
        # 奖励一些代币
        reward_mgr.award_tokens(user_id, 1000 * i)
        reward_mgr.award_exp(user_id, 500 * i)
        
        # 授予一些徽章
        if i >= 3:
            reward_mgr.award_badge(user_id, "social_friend")
        if i >= 5:
            reward_mgr.award_badge(user_id, "economic_trader")
        if i >= 8:
            reward_mgr.award_badge(user_id, "exploration_scout")


# 使用示例
if __name__ == "__main__":
    print("游戏化 API 模块已加载")
    print("可用端点:")
    print("  GET  /api/v1/gamification/achievements")
    print("  POST /api/v1/gamification/achievements/update")
    print("  GET  /api/v1/gamification/leaderboard")
    print("  GET  /api/v1/gamification/daily-tasks")
    print("  POST /api/v1/gamification/daily-tasks/update")
    print("  POST /api/v1/gamification/daily-tasks/claim")
    print("  GET  /api/v1/gamification/badges")
    print("  GET  /api/v1/gamification/balance")
    print("  GET  /api/v1/gamification/profile")
