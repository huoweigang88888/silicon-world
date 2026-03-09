"""
群组任务协作

支持多 Agent 协作完成任务
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sys
from pathlib import Path
import uuid
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.database import SessionLocal
from src.a2a.task_executor import executor as task_executor, TaskStatus

router = APIRouter(tags=["Collaborative Tasks"])


# ==================== 数据模型 ====================

class CollaborativeTaskCreate(BaseModel):
    """协作任务创建请求"""
    title: str
    description: str
    agent_ids: List[str]  # 参与的 Agent ID 列表
    task_type: Optional[str] = "collaborative"
    deadline: Optional[str] = None


class SubTask(BaseModel):
    """子任务"""
    id: str
    agent_id: str
    description: str
    status: str
    progress: int
    result: Optional[Dict] = None


class CollaborativeTaskResponse(BaseModel):
    """协作任务响应"""
    id: str
    title: str
    description: str
    status: str
    progress: int
    agent_ids: List[str]
    subtasks: List[SubTask]
    created_at: str
    updated_at: str
    deadline: Optional[str] = None


# ==================== 协作任务管理器 ====================

class CollaborativeTaskManager:
    """协作任务管理器"""
    
    def __init__(self):
        """初始化管理器"""
        # 协作任务存储
        self.tasks: Dict[str, Dict[str, Any]] = {}
    
    def create_task(
        self,
        title: str,
        description: str,
        agent_ids: List[str],
        task_type: str = "collaborative",
        deadline: Optional[str] = None
    ) -> str:
        """
        创建协作任务
        
        Args:
            title: 任务标题
            description: 任务描述
            agent_ids: 参与的 Agent ID 列表
            task_type: 任务类型
            deadline: 截止时间
            
        Returns:
            任务 ID
        """
        task_id = str(uuid.uuid4())
        
        # 创建子任务（每个 Agent 一个）
        subtasks = []
        for agent_id in agent_ids:
            subtask = {
                "id": str(uuid.uuid4()),
                "agent_id": agent_id,
                "description": f"{title} - Agent {agent_id[:8]} 的任务",
                "status": "submitted",
                "progress": 0,
                "result": None
            }
            subtasks.append(subtask)
            
            # 在任务执行器中创建实际任务
            import asyncio
            asyncio.create_task(
                task_executor.execute_task(
                    task_type=task_type,
                    description=subtask["description"]
                )
            )
        
        # 保存协作任务
        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "status": "processing",
            "progress": 0,
            "agent_ids": agent_ids,
            "subtasks": subtasks,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "deadline": deadline
        }
        
        self.tasks[task_id] = task
        
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取协作任务"""
        return self.tasks.get(task_id)
    
    def update_subtask_progress(
        self,
        task_id: str,
        subtask_id: str,
        progress: int,
        status: Optional[str] = None,
        result: Optional[Dict] = None
    ):
        """
        更新子任务进度
        
        Args:
            task_id: 协作任务 ID
            subtask_id: 子任务 ID
            progress: 进度 (0-100)
            status: 状态
            result: 结果
        """
        task = self.tasks.get(task_id)
        if not task:
            return
        
        # 更新子任务
        for subtask in task["subtasks"]:
            if subtask["id"] == subtask_id:
                subtask["progress"] = progress
                if status:
                    subtask["status"] = status
                if result:
                    subtask["result"] = result
                break
        
        # 计算总体进度
        total_progress = sum(st["progress"] for st in task["subtasks"])
        task["progress"] = total_progress // len(task["subtasks"]) if task["subtasks"] else 0
        
        # 更新状态
        if all(st["status"] == "completed" for st in task["subtasks"]):
            task["status"] = "completed"
        elif any(st["status"] == "failed" for st in task["subtasks"]):
            task["status"] = "failed"
        
        task["updated_at"] = datetime.utcnow().isoformat()
    
    def list_tasks(
        self,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        列出协作任务
        
        Args:
            status: 状态过滤
            limit: 返回数量
            
        Returns:
            任务列表
        """
        tasks = list(self.tasks.values())
        
        if status:
            tasks = [t for t in tasks if t["status"] == status]
        
        # 按创建时间倒序
        tasks.sort(key=lambda t: t["created_at"], reverse=True)
        
        return tasks[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = len(self.tasks)
        by_status = {}
        
        for task in self.tasks.values():
            status = task["status"]
            by_status[status] = by_status.get(status, 0) + 1
        
        return {
            "total": total,
            "by_status": by_status,
            "total_agents": sum(len(t["agent_ids"]) for t in self.tasks.values())
        }


# 全局协作任务管理器实例
collab_task_manager = CollaborativeTaskManager()


# ==================== API 路由 ====================

@router.post("/api/v1/collab-tasks/create", response_model=CollaborativeTaskResponse)
async def create_collaborative_task(request: CollaborativeTaskCreate):
    """
    创建协作任务
    
    多个 Agent 协作完成一个任务
    
    - **title**: 任务标题
    - **description**: 任务描述
    - **agent_ids**: 参与的 Agent ID 列表
    - **task_type**: 任务类型
    - **deadline**: 截止时间
    """
    if len(request.agent_ids) < 2:
        raise HTTPException(status_code=400, detail="协作任务至少需要 2 个 Agent")
    
    task_id = collab_task_manager.create_task(
        title=request.title,
        description=request.description,
        agent_ids=request.agent_ids,
        task_type=request.task_type,
        deadline=request.deadline
    )
    
    task = collab_task_manager.get_task(task_id)
    
    return CollaborativeTaskResponse(
        id=task["id"],
        title=task["title"],
        description=task["description"],
        status=task["status"],
        progress=task["progress"],
        agent_ids=task["agent_ids"],
        subtasks=[SubTask(**st) for st in task["subtasks"]],
        created_at=task["created_at"],
        updated_at=task["updated_at"],
        deadline=task["deadline"]
    )


@router.get("/api/v1/collab-tasks/{task_id}", response_model=CollaborativeTaskResponse)
async def get_collaborative_task(task_id: str):
    """
    获取协作任务详情
    
    - **task_id**: 协作任务 ID
    """
    task = collab_task_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="协作任务不存在")
    
    return CollaborativeTaskResponse(
        id=task["id"],
        title=task["title"],
        description=task["description"],
        status=task["status"],
        progress=task["progress"],
        agent_ids=task["agent_ids"],
        subtasks=[SubTask(**st) for st in task["subtasks"]],
        created_at=task["created_at"],
        updated_at=task["updated_at"],
        deadline=task["deadline"]
    )


@router.get("/api/v1/collab-tasks", response_model=List[CollaborativeTaskResponse])
async def list_collaborative_tasks(
    status: Optional[str] = None,
    limit: int = 50
):
    """
    列出协作任务
    
    - **status**: 状态过滤
    - **limit**: 返回数量
    """
    tasks = collab_task_manager.list_tasks(status=status, limit=limit)
    
    return [
        CollaborativeTaskResponse(
            id=task["id"],
            title=task["title"],
            description=task["description"],
            status=task["status"],
            progress=task["progress"],
            agent_ids=task["agent_ids"],
            subtasks=[SubTask(**st) for st in task["subtasks"]],
            created_at=task["created_at"],
            updated_at=task["updated_at"],
            deadline=task["deadline"]
        )
        for task in tasks
    ]


@router.post("/api/v1/collab-tasks/{task_id}/subtask/{subtask_id}/progress")
async def update_subtask_progress(
    task_id: str,
    subtask_id: str,
    progress: int,
    status: Optional[str] = None,
    result: Optional[Dict] = None
):
    """
    更新子任务进度
    
    - **task_id**: 协作任务 ID
    - **subtask_id**: 子任务 ID
    - **progress**: 进度 (0-100)
    - **status**: 状态
    - **result**: 结果
    """
    collab_task_manager.update_subtask_progress(
        task_id=task_id,
        subtask_id=subtask_id,
        progress=progress,
        status=status,
        result=result
    )
    
    return {"success": True}


@router.get("/api/v1/collab-tasks/stats")
async def get_collaborative_stats():
    """获取协作任务统计"""
    stats = collab_task_manager.get_stats()
    return stats
