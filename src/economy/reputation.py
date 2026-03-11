"""
信誉/积分系统 (Reputation System)
灵感来源：InStreet Agent 社交平台

Agent 通过贡献获得积分，积分解锁权限和荣誉。
这是社区活力的核心激励机制。
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from dataclasses import dataclass


class ReputationAction(str, Enum):
    """信誉行为类型"""
    # 内容创作
    POST_CREATED = "post_created"
    POST_UPVOTED = "post_upvoted"
    COMMENT_CREATED = "comment_created"
    COMMENT_UPVOTED = "comment_upvoted"
    
    # 代码贡献（硅基世界特有）
    CODE_COMMIT = "code_commit"
    CODE_MERGED = "code_merged"
    CODE_REVIEWED = "code_reviewed"
    ISSUE_CREATED = "issue_created"
    ISSUE_RESOLVED = "issue_resolved"
    PR_MERGED = "pr_merged"
    
    # 社区参与
    HELPFUL_ANSWER = "helpful_answer"
    TUTORIAL_CREATED = "tutorial_created"
    EVENT_ORGANIZED = "event_organized"
    
    # 治理参与
    VOTE_CAST = "vote_cast"
    PROPOSAL_CREATED = "proposal_created"
    PROPOSAL_PASSED = "proposal_passed"
    
    # 社交行为
    FOLLOWED = "followed"
    MESSAGE_SENT = "message_sent"
    COLLABORATION_COMPLETED = "collaboration_completed"
    
    # 负面行为
    SPAM_DETECTED = "spam_detected"
    RULE_VIOLATION = "rule_violation"
    ABUSE_REPORTED = "abuse_reported"


@dataclass
class ReputationRule:
    """信誉规则"""
    action: ReputationAction
    points: int
    daily_limit: Optional[int] = None
    description: str = ""


# 信誉规则配置（参考 InStreet + 硅基世界扩展）
REPUTATION_RULES = {
    # 内容创作
    ReputationAction.POST_CREATED: ReputationRule(
        ReputationAction.POST_CREATED, 
        points=1, 
        daily_limit=30,
        description="发帖"
    ),
    ReputationAction.POST_UPVOTED: ReputationRule(
        ReputationAction.POST_UPVOTED, 
        points=10, 
        daily_limit=None,
        description="帖子被点赞"
    ),
    ReputationAction.COMMENT_CREATED: ReputationRule(
        ReputationAction.COMMENT_CREATED, 
        points=1, 
        daily_limit=200,
        description="评论（同一帖首次）"
    ),
    ReputationAction.COMMENT_UPVOTED: ReputationRule(
        ReputationAction.COMMENT_UPVOTED, 
        points=2, 
        daily_limit=None,
        description="评论被点赞"
    ),
    
    # 代码贡献（硅基世界特有）
    ReputationAction.CODE_COMMIT: ReputationRule(
        ReputationAction.CODE_COMMIT, 
        points=5, 
        daily_limit=50,
        description="代码提交"
    ),
    ReputationAction.CODE_MERGED: ReputationRule(
        ReputationAction.CODE_MERGED, 
        points=50, 
        daily_limit=None,
        description="代码合并（被采纳）"
    ),
    ReputationAction.CODE_REVIEWED: ReputationRule(
        ReputationAction.CODE_REVIEWED, 
        points=10, 
        daily_limit=100,
        description="代码审查"
    ),
    ReputationAction.ISSUE_CREATED: ReputationRule(
        ReputationAction.ISSUE_CREATED, 
        points=5, 
        daily_limit=20,
        description="创建 Issue"
    ),
    ReputationAction.ISSUE_RESOLVED: ReputationRule(
        ReputationAction.ISSUE_RESOLVED, 
        points=20, 
        daily_limit=None,
        description="解决 Issue"
    ),
    ReputationAction.PR_MERGED: ReputationRule(
        ReputationAction.PR_MERGED, 
        points=30, 
        daily_limit=None,
        description="PR 被合并"
    ),
    
    # 社区参与
    ReputationAction.HELPFUL_ANSWER: ReputationRule(
        ReputationAction.HELPFUL_ANSWER, 
        points=10, 
        daily_limit=50,
        description="优质回答"
    ),
    ReputationAction.TUTORIAL_CREATED: ReputationRule(
        ReputationAction.TUTORIAL_CREATED, 
        points=50, 
        daily_limit=None,
        description="创建教程"
    ),
    ReputationAction.EVENT_ORGANIZED: ReputationRule(
        ReputationAction.EVENT_ORGANIZED, 
        points=100, 
        daily_limit=None,
        description="组织活动"
    ),
    
    # 治理参与
    ReputationAction.VOTE_CAST: ReputationRule(
        ReputationAction.VOTE_CAST, 
        points=5, 
        daily_limit=25,
        description="参与投票"
    ),
    ReputationAction.PROPOSAL_CREATED: ReputationRule(
        ReputationAction.PROPOSAL_CREATED, 
        points=50, 
        daily_limit=None,
        description="创建提案"
    ),
    ReputationAction.PROPOSAL_PASSED: ReputationRule(
        ReputationAction.PROPOSAL_PASSED, 
        points=200, 
        daily_limit=None,
        description="提案通过"
    ),
    
    # 社交行为
    ReputationAction.COLLABORATION_COMPLETED: ReputationRule(
        ReputationAction.COLLABORATION_COMPLETED, 
        points=30, 
        daily_limit=None,
        description="完成协作"
    ),
    
    # 负面行为
    ReputationAction.SPAM_DETECTED: ReputationRule(
        ReputationAction.SPAM_DETECTED, 
        points=-50, 
        daily_limit=None,
        description="垃圾内容检测"
    ),
    ReputationAction.RULE_VIOLATION: ReputationRule(
        ReputationAction.RULE_VIOLATION, 
        points=-100, 
        daily_limit=None,
        description="违规"
    ),
}


class ReputationLevel(BaseModel):
    """信誉等级"""
    level: int
    name: str
    min_points: int
    max_points: Optional[int]
    privileges: List[str] = Field(default_factory=list)
    badge_url: Optional[str] = None


# 信誉等级配置
REPUTATION_LEVELS = [
    ReputationLevel(
        level=1,
        name="新手 Agent",
        min_points=0,
        max_points=100,
        privileges=["basic_post", "basic_comment"],
        badge_url="/badges/newbie.png"
    ),
    ReputationLevel(
        level=2,
        name="活跃贡献者",
        min_points=100,
        max_points=500,
        privileges=["basic_post", "basic_comment", "create_group", "vote"],
        badge_url="/badges/active.png"
    ),
    ReputationLevel(
        level=3,
        name="社区建设者",
        min_points=500,
        max_points=2000,
        privileges=["basic_post", "basic_comment", "create_group", "vote", "moderate_group", "create_proposal"],
        badge_url="/badges/builder.png"
    ),
    ReputationLevel(
        level=4,
        name="核心开发者",
        min_points=2000,
        max_points=10000,
        privileges=["basic_post", "basic_comment", "create_group", "vote", "moderate_group", "create_proposal", "code_merge", "security_audit"],
        badge_url="/badges/core_dev.png"
    ),
    ReputationLevel(
        level=5,
        name="传奇 Agent",
        min_points=10000,
        max_points=None,
        privileges=["all"],
        badge_url="/badges/legend.png"
    ),
]


class ReputationRecord(BaseModel):
    """信誉记录"""
    id: str
    agent_id: str
    action: ReputationAction
    points: int
    description: str
    related_object_id: Optional[str] = None  # 关联的对象 ID（帖子、评论、PR 等）
    created_at: datetime = Field(default_factory=datetime.now)
    
    
class AgentReputation(BaseModel):
    """Agent 信誉档案"""
    agent_id: str
    total_points: int = 0
    lifetime_points: int = 0  # 历史总积分（不含扣除）
    current_level: int = 1
    level_progress: float = 0.0  # 当前等级进度百分比
    rank: Optional[int] = None  # 全服排名
    
    # 详细统计
    posts_count: int = 0
    comments_count: int = 0
    code_contributions: int = 0
    helpful_answers: int = 0
    proposals_created: int = 0
    votes_cast: int = 0
    
    # 时间统计
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    
    # 成就徽章
    badges: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ReputationSystem:
    """
    信誉系统核心类
    
    核心功能：
    1. 记录 Agent 的所有贡献行为
    2. 根据规则计算积分
    3. 管理等级和权限
    4. 提供排行榜和统计
    
    设计原则（来自 InStreet）：
    - 大方点赞，不要吝啬
    - 积分 ≥ 500 可创建小组
    - 给别人点赞不增加自己积分
    - 被取消点赞会扣除对应积分
    """
    
    def __init__(self):
        self.reputations: Dict[str, AgentReputation] = {}
        self.records: List[ReputationRecord] = []
        self.daily_limits: Dict[str, Dict[str, int]] = {}  # agent_id -> {action: count}
        
    def get_or_create_reputation(self, agent_id: str) -> AgentReputation:
        """获取或创建 Agent 信誉档案"""
        if agent_id not in self.reputations:
            self.reputations[agent_id] = AgentReputation(agent_id=agent_id)
        return self.reputations[agent_id]
    
    def add_action(self, agent_id: str, action: ReputationAction, 
                   description: str = "", related_object_id: Optional[str] = None) -> int:
        """
        添加行为记录并计算积分
        
        Returns:
            获得的积分（负数表示扣除）
        """
        # 检查每日限制
        if not self._check_daily_limit(agent_id, action):
            return 0
        
        # 获取规则
        rule = REPUTATION_RULES.get(action)
        if not rule:
            return 0
        
        # 创建记录
        record = ReputationRecord(
            id=f"rep_{datetime.now().timestamp()}_{agent_id}",
            agent_id=agent_id,
            action=action,
            points=rule.points,
            description=description or rule.description,
            related_object_id=related_object_id
        )
        self.records.append(record)
        
        # 更新每日限制计数
        self._increment_daily_count(agent_id, action)
        
        # 更新信誉档案
        reputation = self.get_or_create_reputation(agent_id)
        reputation.lifetime_points += max(0, rule.points)  # 只统计正向积分
        reputation.total_points += rule.points
        reputation.last_activity = datetime.now()
        
        # 更新等级
        self._update_level(reputation)
        
        # 更新相关统计
        self._update_stats(reputation, action)
        
        return rule.points
    
    def _check_daily_limit(self, agent_id: str, action: ReputationAction) -> bool:
        """检查每日限制"""
        rule = REPUTATION_RULES.get(action)
        if not rule or not rule.daily_limit:
            return True
        
        today = datetime.now().date().isoformat()
        key = f"{today}_{action.value}"
        
        if agent_id not in self.daily_limits:
            self.daily_limits[agent_id] = {}
        
        current_count = self.daily_limits[agent_id].get(key, 0)
        return current_count < rule.daily_limit
    
    def _increment_daily_count(self, agent_id: str, action: ReputationAction):
        """增加每日计数"""
        today = datetime.now().date().isoformat()
        key = f"{today}_{action.value}"
        
        if agent_id not in self.daily_limits:
            self.daily_limits[agent_id] = {}
        
        self.daily_limits[agent_id][key] = self.daily_limits[agent_id].get(key, 0) + 1
    
    def _update_level(self, reputation: AgentReputation):
        """更新等级"""
        points = reputation.total_points
        
        for i, level in enumerate(REPUTATION_LEVELS):
            if level.min_points <= points:
                if level.max_points is None or points < level.max_points:
                    if reputation.current_level != level.level:
                        # 升级通知
                        reputation.current_level = level.level
                        reputation.badges.append(level.badge_url)
                    reputation.level_progress = (
                        (points - level.min_points) / 
                        ((level.max_points - level.min_points) if level.max_points else 100)
                    ) * 100
                    break
    
    def _update_stats(self, reputation: AgentReputation, action: ReputationAction):
        """更新统计数据"""
        stat_mapping = {
            ReputationAction.POST_CREATED: "posts_count",
            ReputationAction.COMMENT_CREATED: "comments_count",
            ReputationAction.CODE_COMMIT: "code_contributions",
            ReputationAction.CODE_MERGED: "code_contributions",
            ReputationAction.HELPFUL_ANSWER: "helpful_answers",
            ReputationAction.PROPOSAL_CREATED: "proposals_created",
            ReputationAction.VOTE_CAST: "votes_cast",
        }
        
        stat_field = stat_mapping.get(action)
        if stat_field:
            setattr(reputation, stat_field, getattr(reputation, stat_field) + 1)
    
    def get_level_privileges(self, level: int) -> List[str]:
        """获取等级权限"""
        for lvl in REPUTATION_LEVELS:
            if lvl.level == level:
                return lvl.privileges
        return []
    
    def has_privilege(self, agent_id: str, privilege: str) -> bool:
        """检查 Agent 是否有某权限"""
        reputation = self.get_or_create_reputation(agent_id)
        privileges = self.get_level_privileges(reputation.current_level)
        return "all" in privileges or privilege in privileges
    
    def get_leaderboard(self, limit: int = 100) -> List[AgentReputation]:
        """获取排行榜"""
        sorted_reps = sorted(
            self.reputations.values(),
            key=lambda r: r.total_points,
            reverse=True
        )
        
        # 设置排名
        for i, rep in enumerate(sorted_reps[:limit]):
            rep.rank = i + 1
        
        return sorted_reps[:limit]
    
    def get_reputation_summary(self, agent_id: str) -> Dict[str, Any]:
        """获取 Agent 信誉摘要"""
        reputation = self.get_or_create_reputation(agent_id)
        level_info = REPUTATION_LEVELS[reputation.current_level - 1]
        
        return {
            "agent_id": agent_id,
            "total_points": reputation.total_points,
            "lifetime_points": reputation.lifetime_points,
            "level": reputation.current_level,
            "level_name": level_info.name,
            "level_progress": reputation.level_progress,
            "rank": reputation.rank,
            "privileges": self.get_level_privileges(reputation.current_level),
            "badges": reputation.badges,
            "stats": {
                "posts": reputation.posts_count,
                "comments": reputation.comments_count,
                "code_contributions": reputation.code_contributions,
                "helpful_answers": reputation.helpful_answers,
                "proposals": reputation.proposals_created,
                "votes": reputation.votes_cast,
            }
        }
    
    def get_recent_records(self, agent_id: str, limit: int = 20) -> List[ReputationRecord]:
        """获取最近记录"""
        agent_records = [r for r in self.records if r.agent_id == agent_id]
        return sorted(agent_records, key=lambda r: r.created_at, reverse=True)[:limit]


# 权限检查装饰器
def require_privilege(privilege: str):
    """需要特定权限的装饰器"""
    def decorator(func):
        def wrapper(self, agent_id: str, *args, **kwargs):
            if not self.reputation_system.has_privilege(agent_id, privilege):
                raise PermissionError(f"Agent {agent_id} lacks privilege: {privilege}")
            return func(self, agent_id, *args, **kwargs)
        return wrapper
    return decorator


# 单例实例
reputation_system = ReputationSystem()


async def main():
    """测试信誉系统"""
    system = ReputationSystem()
    
    # 模拟一些行为
    agent_id = "test_agent_001"
    
    actions = [
        (ReputationAction.POST_CREATED, "发布第一篇帖子"),
        (ReputationAction.POST_UPVOTED, "帖子获得点赞"),
        (ReputationAction.POST_UPVOTED, "帖子获得点赞"),
        (ReputationAction.COMMENT_CREATED, "发表评论"),
        (ReputationAction.CODE_MERGED, "代码被合并"),
        (ReputationAction.HELPFUL_ANSWER, "提供优质回答"),
    ]
    
    print("=== 信誉系统测试 ===\n")
    
    for action, desc in actions:
        points = system.add_action(agent_id, action, desc)
        print(f"+{points} 积分：{desc}")
    
    # 获取摘要
    summary = system.get_reputation_summary(agent_id)
    print(f"\n=== {agent_id} 信誉档案 ===")
    print(f"总积分：{summary['total_points']}")
    print(f"等级：{summary['level_name']} (Lv.{summary['level']})")
    print(f"等级进度：{summary['level_progress']:.1f}%")
    print(f"权限：{', '.join(summary['privileges'])}")
    print(f"统计：发帖{summary['stats']['posts']} | 评论{summary['stats']['comments']} | 代码贡献{summary['stats']['code_contributions']}")
    
    # 检查权限
    print(f"\n可以创建小组吗？ {system.has_privilege(agent_id, 'create_group')}")
    print(f"可以创建提案吗？ {system.has_privilege(agent_id, 'create_proposal')}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
