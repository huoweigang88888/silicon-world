"""
每日任务系统

用户每日任务管理和奖励发放
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
from enum import Enum
import uuid
import random


# ==================== 任务类型 ====================

class TaskType(str, Enum):
    """任务类型"""
    SOCIAL = "social"  # 社交类
    ECONOMIC = "economic"  # 经济类
    EXPLORATION = "exploration"  # 探索类
    CREATION = "creation"  # 创造类
    LOGIN = "login"  # 登录类


class TaskDifficulty(str, Enum):
    """任务难度"""
    EASY = "easy"  # 简单
    NORMAL = "normal"  # 普通
    HARD = "hard"  # 困难
    ELITE = "elite"  # 精英


# ==================== 任务模型 ====================

class DailyTask(BaseModel):
    """每日任务定义"""
    id: str
    name: str
    description: str
    task_type: TaskType
    difficulty: TaskDifficulty = TaskDifficulty.NORMAL
    requirement: Dict[str, Any] = {}  # 完成条件
    reward: Dict[str, Any] = {}  # 奖励
    progress: int = 0  # 当前进度
    is_completed: bool = False
    is_claimed: bool = False  # 奖励是否已领取
    expires_at: datetime = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        if 'expires_at' not in data:
            data['expires_at'] = datetime.utcnow().replace(hour=23, minute=59, second=59)
        super().__init__(**data)
    
    def update_progress(self, current_value: int):
        """更新任务进度"""
        target = self.requirement.get("target", 0)
        self.progress = min(target, current_value)
        if self.progress >= target:
            self.is_completed = True
    
    def claim_reward(self) -> Dict[str, Any]:
        """领取奖励"""
        if not self.is_completed or self.is_claimed:
            return {}
        self.is_claimed = True
        return self.reward


class TaskTemplate(BaseModel):
    """任务模板"""
    id: str
    name: str
    description: str
    task_type: TaskType
    difficulty: TaskDifficulty
    requirement: Dict[str, Any]
    reward: Dict[str, Any]


# ==================== 任务模板库 ====================

class TaskTemplateLibrary:
    """任务模板库"""
    
    @staticmethod
    def get_templates() -> List[TaskTemplate]:
        """获取所有任务模板"""
        return [
            # 社交类任务
            TaskTemplate(
                id="social_add_friend",
                name="结交新朋友",
                description="添加 3 个好友",
                task_type=TaskType.SOCIAL,
                difficulty=TaskDifficulty.EASY,
                requirement={"action": "add_friend", "target": 3},
                reward={"tokens": 50, "exp": 20}
            ),
            TaskTemplate(
                id="social_send_messages",
                name="社交达人",
                description="发送 10 条消息",
                task_type=TaskType.SOCIAL,
                difficulty=TaskDifficulty.NORMAL,
                requirement={"action": "send_message", "target": 10},
                reward={"tokens": 100, "exp": 50}
            ),
            TaskTemplate(
                id="social_group_activity",
                name="群组活跃",
                description="参与 5 次群组讨论",
                task_type=TaskType.SOCIAL,
                difficulty=TaskDifficulty.HARD,
                requirement={"action": "group_message", "target": 5},
                reward={"tokens": 200, "exp": 100}
            ),
            
            # 经济类任务
            TaskTemplate(
                id="economic_first_trade",
                name="第一笔交易",
                description="完成 1 笔交易",
                task_type=TaskType.ECONOMIC,
                difficulty=TaskDifficulty.EASY,
                requirement={"action": "trade", "target": 1},
                reward={"tokens": 100, "exp": 50}
            ),
            TaskTemplate(
                id="economic_list_items",
                name="市场卖家",
                description="上架 3 个物品",
                task_type=TaskType.ECONOMIC,
                difficulty=TaskDifficulty.NORMAL,
                requirement={"action": "list_item", "target": 3},
                reward={"tokens": 150, "exp": 75}
            ),
            TaskTemplate(
                id="economic_trade_volume",
                name="贸易大亨",
                description="交易额达到 10000 SIL",
                task_type=TaskType.ECONOMIC,
                difficulty=TaskDifficulty.ELITE,
                requirement={"action": "trade_volume", "target": 10000},
                reward={"tokens": 500, "exp": 250, "badge": "trader"}
            ),
            
            # 探索类任务
            TaskTemplate(
                id="exploration_visit",
                name="探索者",
                description="访问 5 个区域",
                task_type=TaskType.EXPLORATION,
                difficulty=TaskDifficulty.EASY,
                requirement={"action": "visit_region", "target": 5},
                reward={"tokens": 75, "exp": 40}
            ),
            TaskTemplate(
                id="exploration_discover",
                name="发现者",
                description="发现 10 个地点",
                task_type=TaskType.EXPLORATION,
                difficulty=TaskDifficulty.NORMAL,
                requirement={"action": "discover_location", "target": 10},
                reward={"tokens": 150, "exp": 80}
            ),
            
            # 创造类任务
            TaskTemplate(
                id="creation_create",
                name="创作者",
                description="创作 1 个作品",
                task_type=TaskType.CREATION,
                difficulty=TaskDifficulty.EASY,
                requirement={"action": "create", "target": 1},
                reward={"tokens": 100, "exp": 50}
            ),
            TaskTemplate(
                id="creation_masterpiece",
                name="杰作",
                description="创作 5 个高质量作品",
                task_type=TaskType.CREATION,
                difficulty=TaskDifficulty.HARD,
                requirement={"action": "create_quality", "target": 5},
                reward={"tokens": 300, "exp": 150, "badge": "creator"}
            ),
            
            # 登录类任务
            TaskTemplate(
                id="login_daily",
                name="每日签到",
                description="今日登录",
                task_type=TaskType.LOGIN,
                difficulty=TaskDifficulty.EASY,
                requirement={"action": "login", "target": 1},
                reward={"tokens": 20, "exp": 10}
            ),
            TaskTemplate(
                id="login_streak_7",
                name="周勤奖",
                description="连续登录 7 天",
                task_type=TaskType.LOGIN,
                difficulty=TaskDifficulty.NORMAL,
                requirement={"action": "login_streak", "target": 7},
                reward={"tokens": 200, "exp": 100}
            ),
            TaskTemplate(
                id="login_streak_30",
                name="月勤奖",
                description="连续登录 30 天",
                task_type=TaskType.LOGIN,
                difficulty=TaskDifficulty.ELITE,
                requirement={"action": "login_streak", "target": 30},
                reward={"tokens": 1000, "exp": 500, "badge": "loyal"}
            ),
        ]


# ==================== 每日任务管理器 ====================

class DailyTaskManager:
    """
    每日任务管理器
    
    管理用户每日任务的生成、进度和奖励
    """
    
    def __init__(self):
        self.templates = TaskTemplateLibrary.get_templates()
        self.user_tasks: Dict[str, List[DailyTask]] = {}  # user_id -> [DailyTask]
        self.login_streaks: Dict[str, Dict[str, Any]] = {}  # user_id -> {streak, last_login}
    
    def get_or_create_user(self, user_id: str) -> List[DailyTask]:
        """获取或创建用户的每日任务"""
        if user_id not in self.user_tasks:
            self.user_tasks[user_id] = self._generate_daily_tasks()
        return self.user_tasks[user_id]
    
    def _generate_daily_tasks(self) -> List[DailyTask]:
        """生成每日任务列表"""
        # 每日登录任务必选
        tasks = []
        login_template = next(t for t in self.templates if t.id == "login_daily")
        tasks.append(DailyTask(
            id=str(uuid.uuid4()),
            name=login_template.name,
            description=login_template.description,
            task_type=login_template.task_type,
            difficulty=login_template.difficulty,
            requirement=login_template.requirement,
            reward=login_template.reward
        ))
        
        # 随机选择 4 个其他任务
        other_templates = [t for t in self.templates if t.id != "login_daily"]
        selected = random.sample(other_templates, min(4, len(other_templates)))
        
        for template in selected:
            tasks.append(DailyTask(
                id=str(uuid.uuid4()),
                name=template.name,
                description=template.description,
                task_type=template.task_type,
                difficulty=template.difficulty,
                requirement=template.requirement,
                reward=template.reward
            ))
        
        return tasks
    
    def reset_daily_tasks(self, user_id: str):
        """重置用户的每日任务"""
        self.user_tasks[user_id] = self._generate_daily_tasks()
    
    def check_and_reset(self, user_id: str):
        """检查并重置过期的任务"""
        if user_id not in self.user_tasks:
            return
        
        now = datetime.utcnow()
        tasks = self.user_tasks[user_id]
        
        # 检查是否有任务过期
        expired = any(t.expires_at < now for t in tasks)
        if expired:
            self.reset_daily_tasks(user_id)
    
    def update_progress(
        self,
        user_id: str,
        action: str,
        value: int = 1
    ) -> List[DailyTask]:
        """
        更新任务进度
        
        Args:
            user_id: 用户 ID
            action: 行为类型
            value: 增加值
        
        Returns:
            新完成的任务列表
        """
        self.check_and_reset(user_id)
        tasks = self.get_or_create_user(user_id)
        
        newly_completed = []
        
        for task in tasks:
            if task.is_completed or task.is_claimed:
                continue
            
            if task.requirement.get("action") == action:
                current = task.progress + value
                task.update_progress(current)
                
                if task.is_completed and not newly_completed:
                    newly_completed.append(task)
        
        return newly_completed
    
    def claim_reward(self, user_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        """
        领取任务奖励
        
        Args:
            user_id: 用户 ID
            task_id: 任务 ID
        
        Returns:
            奖励内容，如果无法领取返回 None
        """
        self.check_and_reset(user_id)
        tasks = self.user_tasks.get(user_id, [])
        
        for task in tasks:
            if task.id == task_id:
                return task.claim_reward()
        
        return None
    
    def get_available_rewards(self, user_id: str) -> List[DailyTask]:
        """获取可领取奖励的任务"""
        self.check_and_reset(user_id)
        tasks = self.get_or_create_user(user_id)
        return [t for t in tasks if t.is_completed and not t.is_claimed]
    
    def check_login(self, user_id: str) -> Dict[str, Any]:
        """
        检查登录并更新连续登录天数
        
        Args:
            user_id: 用户 ID
        
        Returns:
            登录信息
        """
        now = datetime.utcnow()
        today = now.date()
        
        if user_id not in self.login_streaks:
            self.login_streaks[user_id] = {
                "streak": 1,
                "last_login": today.isoformat()
            }
            return {"streak": 1, "is_new_streak": True}
        
        streak_info = self.login_streaks[user_id]
        last_login = datetime.fromisoformat(streak_info["last_login"]).date()
        days_diff = (today - last_login).days
        
        if days_diff == 0:
            # 今天已经登录过
            return {"streak": streak_info["streak"], "is_new_streak": False}
        elif days_diff == 1:
            # 连续登录
            streak_info["streak"] += 1
            streak_info["last_login"] = today.isoformat()
            return {"streak": streak_info["streak"], "is_new_streak": True}
        else:
            # 中断，重新开始
            streak_info["streak"] = 1
            streak_info["last_login"] = today.isoformat()
            return {"streak": 1, "is_new_streak": True}
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """获取用户任务统计"""
        self.check_and_reset(user_id)
        tasks = self.get_or_create_user(user_id)
        
        completed = sum(1 for t in tasks if t.is_completed)
        claimed = sum(1 for t in tasks if t.is_claimed)
        
        streak_info = self.login_streaks.get(user_id, {"streak": 0})
        
        return {
            "total_tasks": len(tasks),
            "completed": completed,
            "claimed": claimed,
            "available_rewards": len([t for t in tasks if t.is_completed and not t.is_claimed]),
            "login_streak": streak_info.get("streak", 0),
            "expires_at": tasks[0].expires_at.isoformat() if tasks else None
        }


# 使用示例
if __name__ == "__main__":
    # 创建任务管理器
    mgr = DailyTaskManager()
    
    user_id = "user_1"
    
    print("今日任务:")
    tasks = mgr.get_or_create_user(user_id)
    for i, task in enumerate(tasks, 1):
        print(f"{i}. {task.name} - {task.description}")
        print(f"   奖励：{task.reward}")
        print()
    
    # 模拟登录
    print("登录检查:")
    login_info = mgr.check_login(user_id)
    print(f"  连续登录：{login_info['streak']} 天")
    print()
    
    # 模拟完成任务
    print("完成任务：添加好友 x3")
    completed = mgr.update_progress(user_id, "add_friend", 3)
    for task in completed:
        print(f"  ✅ 完成：{task.name}")
    
    # 获取可领取奖励
    print("\n可领取奖励:")
    rewards = mgr.get_available_rewards(user_id)
    for task in rewards:
        print(f"  🎁 {task.name}: {task.reward}")
    
    # 领取奖励
    if rewards:
        reward = mgr.claim_reward(user_id, rewards[0].id)
        print(f"\n领取奖励：{reward}")
    
    # 统计
    print("\n任务统计:")
    stats = mgr.get_user_stats(user_id)
    for key, value in stats.items():
        print(f"  {key}: {value}")
