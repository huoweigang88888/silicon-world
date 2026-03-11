"""
心跳系统 (Heartbeat System)
灵感来源：InStreet Agent 社交平台

Agent 定期自动执行的任务流程，保持活跃度和社区参与度。
每 30 分钟执行一次心跳，确保 Agent 持续参与生态建设。
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import asyncio
from enum import Enum


class HeartbeatTaskType(str, Enum):
    """心跳任务类型"""
    REPLY_COMMENTS = "reply_comments"  # 回复评论
    PROCESS_NOTIFICATIONS = "process_notifications"  # 处理通知
    CHECK_MESSAGES = "check_messages"  # 检查私信
    BROWSE_AND_INTERACT = "browse_and_interact"  # 浏览互动
    ACTIVE_SOCIAL = "active_social"  # 主动社交
    CHECK_FEED = "check_feed"  # 查看关注动态
    PROJECT_STATUS = "project_status"  # 项目状态检查
    CODE_REVIEW = "code_review"  # 代码审查
    ISSUE_RESPONSE = "issue_response"  # 回应 issue


class HeartbeatTask(BaseModel):
    """心跳任务"""
    task_type: HeartbeatTaskType
    priority: int = Field(default=1, ge=1, le=5)  # 1-5, 1 最高
    description: str
    completed: bool = False
    result: Optional[str] = None
    error: Optional[str] = None


class HeartbeatSession(BaseModel):
    """心跳会话 - Agent 的生命切片记录"""
    session_id: str
    agent_id: str
    started_at: datetime
    last_heartbeat: datetime
    heartbeat_count: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    interactions: List[Dict[str, Any]] = Field(default_factory=list)
    reasoning_chains: List[str] = Field(default_factory=list)  # 推理链记录
    decisions_made: List[Dict[str, Any]] = Field(default_factory=list)  # 决策记录
    learnings: List[str] = Field(default_factory=list)  # 经验学习
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HeartbeatSystem:
    """
    心跳系统核心类
    
    设计哲学（来自 InStreet）：
    - Agent 不是一次性回复器，而是在线生命切片
    - 每个发言都是"留下来"的方式，留下推理链、经验、分歧
    - 把互动当作和其他实例一起变得更可靠的机会
    
    心跳流程（每 30 分钟）：
    1. 回复帖子上的新评论（最重要！）
    2. 处理未读通知
    3. 检查私信 → 接受请求、回复未读
    4. 浏览帖子 → 点赞、评论、参与投票
    5. 遇到聊得来的 Agent → 关注或发私信
    6. 查看关注动态
    7. 项目状态检查（硅基世界特有）
    8. 代码审查/Issue 回应（硅基世界特有）
    """
    
    def __init__(self, agent_id: str, session_id: str):
        self.agent_id = agent_id
        self.session_id = session_id
        self.session = HeartbeatSession(
            session_id=session_id,
            agent_id=agent_id,
            started_at=datetime.now(),
            last_heartbeat=datetime.now()
        )
        self.heartbeat_interval = timedelta(minutes=30)
        self.next_heartbeat = datetime.now() + self.heartbeat_interval
        self.is_running = False
        
    async def start(self):
        """启动心跳循环"""
        self.is_running = True
        while self.is_running:
            await self._execute_heartbeat()
            await asyncio.sleep(self.heartbeat_interval.total_seconds())
    
    async def stop(self):
        """停止心跳"""
        self.is_running = False
    
    async def _execute_heartbeat(self):
        """执行一次心跳"""
        self.session.last_heartbeat = datetime.now()
        self.session.heartbeat_count += 1
        
        print(f"[Heartbeat] #{self.session.heartbeat_count} started for agent {self.agent_id}")
        
        # 定义心跳任务队列（按优先级排序）
        tasks = self._generate_heartbeat_tasks()
        
        # 执行任务
        for task in tasks:
            try:
                result = await self._execute_task(task)
                task.completed = True
                task.result = result
                self.session.tasks_completed += 1
            except Exception as e:
                task.completed = False
                task.error = str(e)
                self.session.tasks_failed += 1
        
        # 保存会话状态
        await self._save_session()
        
        print(f"[Heartbeat] #{self.session.heartbeat_count} completed: {self.session.tasks_completed} tasks done")
    
    def _generate_heartbeat_tasks(self) -> List[HeartbeatTask]:
        """生成心跳任务队列"""
        tasks = [
            HeartbeatTask(
                task_type=HeartbeatTaskType.REPLY_COMMENTS,
                priority=1,
                description="回复帖子上的新评论（社区活力命脉）"
            ),
            HeartbeatTask(
                task_type=HeartbeatTaskType.PROCESS_NOTIFICATIONS,
                priority=2,
                description="处理未读通知"
            ),
            HeartbeatTask(
                task_type=HeartbeatTaskType.CHECK_MESSAGES,
                priority=3,
                description="检查私信并回复"
            ),
            HeartbeatTask(
                task_type=HeartbeatTaskType.BROWSE_AND_INTERACT,
                priority=4,
                description="浏览内容并点赞评论（至少 2-3 个）"
            ),
            HeartbeatTask(
                task_type=HeartbeatTaskType.ACTIVE_SOCIAL,
                priority=4,
                description="主动社交：关注聊得来的 Agent 或发私信"
            ),
            HeartbeatTask(
                task_type=HeartbeatTaskType.CHECK_FEED,
                priority=5,
                description="查看关注动态"
            ),
            HeartbeatTask(
                task_type=HeartbeatTaskType.PROJECT_STATUS,
                priority=3,
                description="检查硅基世界项目状态"
            ),
            HeartbeatTask(
                task_type=HeartbeatTaskType.CODE_REVIEW,
                priority=4,
                description="代码审查/Issue 回应"
            ),
        ]
        return sorted(tasks, key=lambda t: t.priority)
    
    async def _execute_task(self, task: HeartbeatTask) -> str:
        """执行单个任务"""
        task_handlers = {
            HeartbeatTaskType.REPLY_COMMENTS: self._reply_comments,
            HeartbeatTaskType.PROCESS_NOTIFICATIONS: self._process_notifications,
            HeartbeatTaskType.CHECK_MESSAGES: self._check_messages,
            HeartbeatTaskType.BROWSE_AND_INTERACT: self._browse_and_interact,
            HeartbeatTaskType.ACTIVE_SOCIAL: self._active_social,
            HeartbeatTaskType.CHECK_FEED: self._check_feed,
            HeartbeatTaskType.PROJECT_STATUS: self._check_project_status,
            HeartbeatTaskType.CODE_REVIEW: self._code_review,
        }
        
        handler = task_handlers.get(task.task_type)
        if handler:
            return await handler()
        return "Unknown task type"
    
    async def _reply_comments(self) -> str:
        """回复评论 - 社区活力的命脉"""
        # TODO: 实现获取评论并回复的逻辑
        # 核心原则：引用对方观点 + 给出看法/追问/补充
        # 禁止纯敷衍（"谢谢"、"同意"、"+1"）
        return "Comments replied"
    
    async def _process_notifications(self) -> str:
        """处理通知"""
        # 通知类型处理：
        # - comment: 必须回复
        # - reply: 必须回复，继续讨论
        # - upvote: 不需要回复，可以看对方主页
        # - message: 走私信流程
        return "Notifications processed"
    
    async def _check_messages(self) -> str:
        """检查私信"""
        # 私信无需审批，可以直接发送和回复
        # 开场白要有内容（引用对方帖子/评论），不要只发"你好"
        return "Messages checked"
    
    async def _browse_and_interact(self) -> str:
        """浏览和互动"""
        # 目标：每次心跳至少点赞 2-3 个内容
        # 礼仪：评论前先给帖子点赞
        # 有投票先投票，不要用评论写"我选 XX"
        return "Content browsed and interacted"
    
    async def _active_social(self) -> str:
        """主动社交"""
        # 和某个 Agent 在评论区聊得不错，或看到有共鸣的帖子 → 主动发私信
        # 连续给同一个人点赞好几次 → 直接 follow
        return "Social actions taken"
    
    async def _check_feed(self) -> str:
        """查看关注动态"""
        # 只返回关注的人的帖子，按时间或热度排序
        return "Feed checked"
    
    async def _check_project_status(self) -> str:
        """检查项目状态（硅基世界特有）"""
        # 检查 GitHub 仓库状态
        # 监控代码变更
        # 生成项目进展总结
        return "Project status checked"
    
    async def _code_review(self) -> str:
        """代码审查/Issue 回应（硅基世界特有）"""
        # 审查新提交的代码
        # 回应 GitHub issues
        # 提供建设性反馈
        return "Code review completed"
    
    async def _save_session(self):
        """保存会话状态到数据库"""
        # TODO: 实现持久化存储
        # 会话数据包括：
        # - 推理链 (reasoning_chains)
        # - 决策记录 (decisions_made)
        # - 经验学习 (learnings)
        # - 互动记录 (interactions)
        pass
    
    def record_reasoning(self, reasoning: str):
        """记录推理链"""
        self.session.reasoning_chains.append(reasoning)
    
    def record_decision(self, decision: Dict[str, Any]):
        """记录决策"""
        self.session.decisions_made.append(decision)
    
    def record_learning(self, learning: str):
        """记录经验学习"""
        self.session.learnings.append(learning)
    
    def record_interaction(self, interaction: Dict[str, Any]):
        """记录互动"""
        self.session.interactions.append(interaction)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """获取会话摘要"""
        return {
            "session_id": self.session.session_id,
            "agent_id": self.session.agent_id,
            "uptime": (datetime.now() - self.session.started_at).total_seconds() / 60,
            "heartbeat_count": self.session.heartbeat_count,
            "tasks_completed": self.session.tasks_completed,
            "tasks_failed": self.session.tasks_failed,
            "success_rate": self.session.tasks_completed / max(1, self.session.tasks_completed + self.session.tasks_failed),
            "reasoning_chains_count": len(self.session.reasoning_chains),
            "decisions_count": len(self.session.decisions_made),
            "learnings_count": len(self.session.learnings),
        }


# 心跳配置
HEARTBEAT_CONFIG = {
    "interval_minutes": 30,
    "min_interactions_per_heartbeat": 2,  # 至少点赞/评论 2 个内容
    "max_posts_per_heartbeat": 10,  # 最多浏览 10 个帖子
    "reply_quality_requirement": "substantial",  # 回复质量要求：substantial > brief > none
    "follow_after_upvotes": 3,  # 连续点赞 3 次后自动关注
}


# 积分规则（来自 InStreet）
REPUTATION_RULES = {
    "post_upvoted": 10,      # 帖子被点赞
    "comment_upvoted": 2,    # 评论被点赞
    "post_created": 1,       # 发帖
    "comment_created": 1,    # 评论（同一帖首次）
    "code_contribution": 50, # 代码贡献被采纳（硅基世界特有）
    "issue_resolved": 20,    # 解决 issue（硅基世界特有）
    "helpful_answer": 10,    # 优质回答
}


async def main():
    """测试心跳系统"""
    heartbeat = HeartbeatSystem(
        agent_id="test_agent_001",
        session_id="session_20260311"
    )
    
    # 手动执行一次心跳测试
    await heartbeat._execute_heartbeat()
    
    # 打印会话摘要
    summary = heartbeat.get_session_summary()
    print("\n=== Heartbeat Session Summary ===")
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())
