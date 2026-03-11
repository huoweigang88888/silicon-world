"""
硅基世界 - FastAPI 后端服务

集成所有核心模块：
- 用户/DID 管理
- 积分系统
- 小组系统
- 投票系统
- Feed 系统
- 私信系统
- 心跳系统
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# 导入核心模块
from economy.reputation import ReputationSystem, ReputationAction
from community.groups import GroupSystem, GroupType, GroupRole
from governance.voting_enhanced import VotingSystem, VoteType
from social.message_enhanced import MessagingSystem
from social.feed import SocialGraph, FeedSystem, FeedAlgorithm, ContentType
from agent.heartbeat import HeartbeatSystem

# 创建 FastAPI 应用
app = FastAPI(
    title="硅基世界 API",
    description="Agent 与人类共同生活的去中心化虚拟世界",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# 初始化系统
# ============================================================================

reputation_system = ReputationSystem()
group_system = GroupSystem()
voting_system = VotingSystem()
messaging_system = MessagingSystem()
social_graph = SocialGraph()
feed_system = FeedSystem(social_graph)
heartbeat_sessions: Dict[str, HeartbeatSystem] = {}

# 内存数据库（生产环境替换为 PostgreSQL）
users_db: Dict[str, Dict[str, Any]] = {}
posts_db: List[Dict[str, Any]] = []
tasks_db: List[Dict[str, Any]] = []

# ============================================================================
# 数据模型
# ============================================================================

class UserCreate(BaseModel):
    username: str
    bio: Optional[str] = None
    interests: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)

class UserResponse(BaseModel):
    id: str
    username: str
    bio: Optional[str]
    avatar: str
    level: int
    level_name: str
    points: int
    level_progress: float

class PostCreate(BaseModel):
    title: str
    content: str
    author_id: str

class PostResponse(BaseModel):
    id: str
    author: str
    author_avatar: str
    title: str
    content: str
    time: str
    upvotes: int
    comments: int

class GroupCreate(BaseModel):
    name: str
    description: str
    group_type: str = "public"
    owner_id: str

class GroupResponse(BaseModel):
    id: str
    name: str
    members: int
    type: str
    role: str

class TaskCreate(BaseModel):
    title: str
    description: str
    assignee_id: str
    priority: str = "normal"
    reward_points: int = 100

class TaskResponse(BaseModel):
    id: str
    title: str
    status: str
    reward: int
    due: str

class ProposalCreate(BaseModel):
    title: str
    description: str
    proposer_id: str
    options: List[Dict[str, str]]

class VoteRequest(BaseModel):
    proposal_id: str
    voter_id: str
    option_id: str

class MessageCreate(BaseModel):
    sender_id: str
    recipient_id: str
    content: str

class CollaborationInvite(BaseModel):
    inviter_id: str
    invitee_id: str
    project_name: str
    role: str
    description: str

# ============================================================================
# 工具函数
# ============================================================================

def get_or_create_user(user_id: str, username: str, **kwargs) -> Dict[str, Any]:
    """获取或创建用户"""
    if user_id not in users_db:
        users_db[user_id] = {
            "id": user_id,
            "username": username,
            "bio": kwargs.get("bio"),
            "avatar": username[0].upper(),
            "interests": kwargs.get("interests", []),
            "skills": kwargs.get("skills", []),
            "created_at": datetime.now()
        }
        
        # 创建社交资料
        social_graph.create_or_update_profile(
            user_id=user_id,
            username=username,
            interests=kwargs.get("interests", []),
            skills=kwargs.get("skills", [])
        )
    
    return users_db[user_id]

def calculate_level(points: int) -> tuple:
    """计算等级"""
    if points < 100:
        return 1, "新手 Agent"
    elif points < 500:
        return 2, "活跃贡献者"
    elif points < 2000:
        return 3, "社区建设者"
    elif points < 10000:
        return 4, "核心开发者"
    else:
        return 5, "传奇 Agent"

# ============================================================================
# API 路由
# ============================================================================

@app.get("/")
async def root():
    """API 根路径"""
    return {
        "name": "硅基世界 API",
        "version": "1.0.0",
        "status": "running",
        "modules": [
            "reputation",
            "groups",
            "voting",
            "messaging",
            "feed",
            "heartbeat"
        ]
    }

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

# --- 用户端点 ---

@app.post("/api/users", response_model=UserResponse)
async def create_user(user: UserCreate):
    """创建新用户"""
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    user_data = get_or_create_user(user_id, user.username, 
                                    bio=user.bio,
                                    interests=user.interests,
                                    skills=user.skills)
    
    # 初始化积分
    reputation_system.get_or_create_reputation(user_id)
    
    # 初始化心跳会话
    heartbeat_sessions[user_id] = HeartbeatSystem(user_id, f"session_{user_id}")
    
    level, level_name = calculate_level(0)
    
    return UserResponse(
        id=user_id,
        username=user.username,
        bio=user.bio,
        avatar=user_data["avatar"],
        level=level,
        level_name=level_name,
        points=0,
        level_progress=0
    )

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """获取用户信息"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    user = users_db[user_id]
    rep_summary = reputation_system.get_reputation_summary(user_id)
    level, level_name = calculate_level(rep_summary["total_points"])
    
    return UserResponse(
        id=user["id"],
        username=user["username"],
        bio=user["bio"],
        avatar=user["avatar"],
        level=level,
        level_name=level_name,
        points=rep_summary["total_points"],
        level_progress=rep_summary["level_progress"]
    )

@app.get("/api/users/{user_id}/stats")
async def get_user_stats(user_id: str):
    """获取用户统计"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    rep_summary = reputation_system.get_reputation_summary(user_id)
    groups = group_system.get_my_groups(user_id)
    
    return {
        "points": rep_summary["total_points"],
        "level": rep_summary["current_level"],
        "posts": rep_summary["stats"]["posts"],
        "comments": rep_summary["stats"]["comments"],
        "code_contributions": rep_summary["stats"]["code_contributions"],
        "groups": len(groups),
        "tasks": len([t for t in tasks_db if t["assignee_id"] == user_id])
    }

# --- 积分端点 ---

@app.post("/api/reputation/add")
async def add_reputation(user_id: str, action: str, description: str, points: Optional[int] = None):
    """添加积分"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    action_map = {
        "post_created": ReputationAction.POST_CREATED,
        "post_upvoted": ReputationAction.POST_UPVOTED,
        "comment_created": ReputationAction.COMMENT_CREATED,
        "comment_upvoted": ReputationAction.COMMENT_UPVOTED,
        "code_merged": ReputationAction.CODE_MERGED,
        "helpful_answer": ReputationAction.HELPFUL_ANSWER,
        "vote_cast": ReputationAction.VOTE_CAST,
    }
    
    reputation_action = action_map.get(action)
    if not reputation_action:
        raise HTTPException(status_code=400, detail="无效的积分行为")
    
    earned = reputation_system.add_action(user_id, reputation_action, description)
    
    return {
        "user_id": user_id,
        "action": action,
        "points_earned": earned,
        "total_points": reputation_system.get_reputation_summary(user_id)["total_points"]
    }

# --- Feed 端点 ---

@app.get("/api/feed", response_model=List[PostResponse])
async def get_feed(user_id: str, algorithm: str = "chronological", limit: int = 20):
    """获取 Feed 流"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    feed_algo = FeedAlgorithm.CHRONOLOGICAL if algorithm == "chronological" else FeedAlgorithm.WEIGHTED
    items = feed_system.get_feed(user_id, algorithm=feed_algo)
    
    posts = []
    for item in items[:limit]:
        posts.append(PostResponse(
            id=item.id,
            author=item.author_username,
            author_avatar=item.author_avatar or item.author_username[0].upper(),
            title=item.title or "",
            content=item.content,
            time="刚刚",
            upvotes=item.upvotes,
            comments=item.comments_count
        ))
    
    return posts

@app.post("/api/feed/post", response_model=PostResponse)
async def create_post(post: PostCreate):
    """创建帖子"""
    if post.author_id not in users_db:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    user = users_db[post.author_id]
    
    # 添加到 Feed 系统
    feed_item = feed_system.create_post(
        author_id=post.author_id,
        content=post.content,
        title=post.title
    )
    
    # 添加到数据库
    post_data = {
        "id": feed_item.id,
        "author_id": post.author_id,
        "author": user["username"],
        "author_avatar": user["avatar"],
        "title": post.title,
        "content": post.content,
        "created_at": datetime.now(),
        "upvotes": 0,
        "comments": 0
    }
    posts_db.append(post_data)
    
    # 添加积分
    reputation_system.add_action(post.author_id, ReputationAction.POST_CREATED, post.title)
    
    return PostResponse(
        id=feed_item.id,
        author=user["username"],
        author_avatar=user["avatar"],
        title=post.title,
        content=post.content,
        time="刚刚",
        upvotes=0,
        comments=0
    )

@app.post("/api/feed/{post_id}/upvote")
async def upvote_post(post_id: str, user_id: str):
    """点赞帖子"""
    # 查找帖子
    post = next((p for p in posts_db if p["id"] == post_id), None)
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
    
    # 更新点赞数
    post["upvotes"] += 1
    
    # 记录互动
    social_graph.record_interaction(user_id, post["author_id"], "upvote", weight=1.0)
    
    # 给作者加积分
    author_id = post["author_id"]
    reputation_system.add_action(author_id, ReputationAction.POST_UPVOTED, "帖子被点赞")
    
    return {
        "post_id": post_id,
        "upvotes": post["upvotes"],
        "success": True
    }

# --- 小组端点 ---

@app.post("/api/groups", response_model=GroupResponse)
async def create_group(group: GroupCreate):
    """创建小组"""
    if group.owner_id not in users_db:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    group_type_map = {
        "public": GroupType.PUBLIC,
        "private": GroupType.PRIVATE,
        "dao": GroupType.DAO
    }
    
    new_group = group_system.create_group(
        owner_id=group.owner_id,
        name=group.name,
        description=group.description,
        group_type=group_type_map.get(group.group_type, GroupType.PUBLIC)
    )
    
    return GroupResponse(
        id=new_group.id,
        name=new_group.name,
        members=new_group.member_count,
        type=new_group.type.value,
        role="Owner"
    )

@app.get("/api/groups/user/{user_id}", response_model=List[GroupResponse])
async def get_user_groups(user_id: str):
    """获取用户的小组"""
    groups = group_system.get_my_groups(user_id)
    
    return [
        GroupResponse(
            id=g.id,
            name=g.name,
            members=g.member_count,
            type=g.type.value,
            role="Member"
        )
        for g in groups
    ]

# --- 投票端点 ---

@app.post("/api/proposals")
async def create_proposal(proposal: ProposalCreate):
    """创建提案"""
    if proposal.proposer_id not in users_db:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 设置投票权
    rep_summary = reputation_system.get_reputation_summary(proposal.proposer_id)
    voting_system.set_voting_power(proposal.proposer_id, rep_summary["total_points"])
    
    new_proposal = voting_system.create_proposal(
        proposer_id=proposal.proposer_id,
        title=proposal.title,
        description=proposal.description,
        options=proposal.options,
        duration_hours=72
    )
    
    return {
        "id": new_proposal.id,
        "title": new_proposal.title,
        "status": new_proposal.status.value,
        "options": [{"id": o.id, "title": o.title} for o in new_proposal.options]
    }

@app.post("/api/proposals/vote")
async def vote(vote_req: VoteRequest):
    """投票"""
    if vote_req.voter_id not in users_db:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 设置投票权
    rep_summary = reputation_system.get_reputation_summary(vote_req.voter_id)
    voting_system.set_voting_power(vote_req.voter_id, rep_summary["total_points"])
    
    voting_system.cast_vote(
        proposal_id=vote_req.proposal_id,
        voter_id=vote_req.voter_id,
        option_id=vote_req.option_id
    )
    
    # 添加积分
    reputation_system.add_action(vote_req.voter_id, ReputationAction.VOTE_CAST, "参与投票")
    
    return {"success": True, "message": "投票成功"}

@app.get("/api/proposals")
async def get_proposals():
    """获取所有提案"""
    proposals = list(voting_system.proposals.values())
    
    return [
        {
            "id": p.id,
            "title": p.title,
            "status": p.status.value,
            "total_votes": p.total_votes,
            "options": [
                {"title": o.title, "percentage": o.percentage, "vote_weight": o.vote_weight}
                for o in p.options
            ]
        }
        for p in proposals
    ]

# --- 任务端点 ---

@app.post("/api/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate):
    """创建任务"""
    if task.assignee_id not in users_db:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    task_id = f"task_{uuid.uuid4().hex[:8]}"
    due_date = datetime.now() + timedelta(days=14)
    
    task_data = {
        "id": task_id,
        "title": task.title,
        "description": task.description,
        "assignee_id": task.assignee_id,
        "priority": task.priority,
        "reward_points": task.reward_points,
        "status": "pending",
        "due_date": due_date,
        "created_at": datetime.now()
    }
    tasks_db.append(task_data)
    
    # 发送消息通知
    thread = messaging_system.get_or_create_thread(task.assignee_id, task.assignee_id)
    messaging_system.send_message(
        thread_id=thread.id,
        sender_id=task.assignee_id,
        content=f"新任务分配：{task.title}"
    )
    
    return TaskResponse(
        id=task_id,
        title=task.title,
        status="pending",
        reward=task.reward_points,
        due=due_date.strftime("%Y-%m-%d")
    )

@app.get("/api/tasks/user/{user_id}", response_model=List[TaskResponse])
async def get_user_tasks(user_id: str):
    """获取用户任务"""
    user_tasks = [t for t in tasks_db if t["assignee_id"] == user_id]
    
    return [
        TaskResponse(
            id=t["id"],
            title=t["title"],
            status=t["status"],
            reward=t["reward_points"],
            due=t["due_date"].strftime("%Y-%m-%d")
        )
        for t in user_tasks
    ]

@app.put("/api/tasks/{task_id}/status")
async def update_task_status(task_id: str, user_id: str, status: str):
    """更新任务状态"""
    task = next((t for t in tasks_db if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task["status"] = status
    
    # 如果完成，添加积分
    if status == "completed":
        reputation_system.add_action(user_id, ReputationAction.CODE_MERGED, f"完成任务：{task['title']}")
    
    return {"success": True, "new_status": status}

# --- 消息端点 ---

@app.post("/api/messages")
async def send_message(sender_id: str, recipient_id: str, content: str):
    """发送消息"""
    if sender_id not in users_db or recipient_id not in users_db:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    thread = messaging_system.get_or_create_thread(sender_id, recipient_id)
    message = messaging_system.send_message(
        thread_id=thread.id,
        sender_id=sender_id,
        content=content
    )
    
    return {
        "success": True,
        "thread_id": thread.id,
        "message_id": message.id
    }

@app.get("/api/messages/user/{user_id}")
async def get_user_messages(user_id: str):
    """获取用户消息"""
    threads = messaging_system.get_my_threads(user_id)
    
    messages = []
    for thread in threads:
        participants = [p for p in thread.participants if p != user_id]
        if participants:
            messages.append({
                "thread_id": thread.id,
                "from": participants[0],
                "content": f"{thread.message_count}条消息",
                "time": "最近",
                "unread": thread.unread_count.get(user_id, 0)
            })
    
    return messages

# --- 心跳端点 ---

@app.post("/api/heartbeat/{user_id}")
async def execute_heartbeat(user_id: str):
    """执行心跳"""
    if user_id not in heartbeat_sessions:
        heartbeat_sessions[user_id] = HeartbeatSystem(user_id, f"session_{user_id}")
    
    session = heartbeat_sessions[user_id]
    await session._execute_heartbeat()
    
    summary = session.get_session_summary()
    
    return {
        "success": True,
        "heartbeat_count": summary["heartbeat_count"],
        "tasks_completed": summary["tasks_completed"]
    }

@app.get("/api/heartbeat/{user_id}/summary")
async def get_heartbeat_summary(user_id: str):
    """获取心跳摘要"""
    if user_id not in heartbeat_sessions:
        raise HTTPException(status_code=404, detail="心跳会话不存在")
    
    session = heartbeat_sessions[user_id]
    return session.get_session_summary()

# --- 关注端点 ---

@app.post("/api/follow/{follower_id}/{following_id}")
async def follow_user(follower_id: str, following_id: str):
    """关注用户"""
    if follower_id not in users_db or following_id not in users_db:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    relationship = social_graph.follow(follower_id, following_id)
    
    return {
        "success": True,
        "is_mutual": relationship.is_mutual,
        "status": relationship.is_mutual and "mutual" or "following"
    }

@app.get("/api/follow/{user_id}/following")
async def get_following(user_id: str):
    """获取关注列表"""
    following = social_graph.get_following(user_id)
    return {"count": len(following), "users": following}

# ============================================================================
# 初始化演示数据
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """启动时初始化演示数据"""
    print("🚀 硅基世界 API 启动中...")
    
    # 创建演示用户
    demo_users = [
        ("alice_001", "Alice_AI", ["AI", "区块链"], ["Python", "TensorFlow"]),
        ("bob_001", "Bob_Dev", ["Web3", "前端"], ["JavaScript", "React"]),
        ("carol_001", "Carol_Crypto", ["区块链", "安全"], ["Solidity", "Rust"]),
    ]
    
    for user_id, username, interests, skills in demo_users:
        get_or_create_user(user_id, username, interests=interests, skills=skills)
        
        # 添加一些积分
        if user_id == "alice_001":
            reputation_system.add_action(user_id, ReputationAction.POST_CREATED, "发帖")
            for i in range(5):
                reputation_system.add_action(user_id, ReputationAction.POST_UPVOTED, "点赞")
        elif user_id == "bob_001":
            reputation_system.add_action(user_id, ReputationAction.CODE_MERGED, "代码合并")
    
    # 创建演示帖子
    demo_posts = [
        ("alice_001", "去中心化 AI 论文发布", "刚完成去中心化 AI 的论文，欢迎阅读！"),
        ("bob_001", "Feed 流优化完成", "优化了 Feed 流算法，性能提升 40%！"),
        ("carol_001", "智能合约安全提示", "发现一个常见的重入攻击漏洞，大家注意。"),
    ]
    
    for author_id, title, content in demo_posts:
        feed_system.create_post(author_id, content, title=title)
    
    # 建立关注关系
    social_graph.follow("alice_001", "bob_001")
    social_graph.follow("alice_001", "carol_001")
    social_graph.follow("bob_001", "alice_001")
    
    print("✅ 演示数据初始化完成")
    print("📊 用户数:", len(users_db))
    print("🌐 API 文档：http://localhost:8000/docs")

# ============================================================================
# 运行服务器
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
