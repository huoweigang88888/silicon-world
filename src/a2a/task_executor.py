"""
A2A 任务执行器

负责任务的调度和执行
"""

import asyncio
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json

# 导入 WebSocket 管理器
try:
    from .websocket_tasks import task_ws_manager
    HAS_WEBSOCKET = True
except ImportError:
    HAS_WEBSOCKET = False
    task_ws_manager = None


class TaskStatus(Enum):
    """任务状态"""
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


@dataclass
class TaskResult:
    """任务结果"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskExecution:
    """任务执行实例"""
    id: str
    type: str
    description: str
    status: TaskStatus
    created_at: str
    updated_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[TaskResult] = None
    progress: int = 0  # 0-100
    logs: List[str] = field(default_factory=list)


class TaskExecutor:
    """任务执行器"""
    
    def __init__(self):
        """初始化任务执行器"""
        self.tasks: Dict[str, TaskExecution] = {}
        self.task_handlers: Dict[str, Callable] = {}
        self.running = False
        
        # 注册默认处理器
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """注册默认任务处理器"""
        
        @self.register_handler("general")
        async def handle_general_task(task: TaskExecution):
            """通用任务处理"""
            task.logs.append("开始处理通用任务")
            task.progress = 25
            
            await asyncio.sleep(1)  # 模拟处理
            task.progress = 75
            task.logs.append("任务处理完成")
            
            return TaskResult(
                success=True,
                data={"message": "任务完成"},
                metadata={"processing_time": 1.0}
            )
        
        @self.register_handler("research")
        async def handle_research_task(task: TaskExecution):
            """研究任务处理"""
            task.logs.append("开始研究任务")
            task.progress = 10
            
            # 模拟研究步骤
            steps = [
                "收集信息",
                "分析数据",
                "整理结论",
                "生成报告"
            ]
            
            for i, step in enumerate(steps):
                task.logs.append(f"步骤 {i+1}/{len(steps)}: {step}")
                task.progress = 25 * (i + 1)
                await asyncio.sleep(0.5)
            
            return TaskResult(
                success=True,
                data={
                    "report": "研究报告内容",
                    "sources": ["source1", "source2"]
                },
                metadata={"steps_completed": len(steps)}
            )
        
        @self.register_handler("analysis")
        async def handle_analysis_task(task: TaskExecution):
            """分析任务处理"""
            task.logs.append("开始数据分析")
            task.progress = 20
            
            await asyncio.sleep(1)
            task.progress = 60
            task.logs.append("数据预处理完成")
            
            await asyncio.sleep(1)
            task.progress = 100
            task.logs.append("分析完成")
            
            return TaskResult(
                success=True,
                data={
                    "insights": ["洞察 1", "洞察 2"],
                    "confidence": 0.95
                },
                metadata={"analysis_type": "data"}
            )
        
        @self.register_handler("chat")
        async def handle_chat_task(task: TaskExecution):
            """聊天任务处理"""
            task.logs.append("开始对话")
            task.progress = 50
            
            # 模拟对话响应
            await asyncio.sleep(0.5)
            task.progress = 100
            
            return TaskResult(
                success=True,
                data={"response": "您好！有什么可以帮助您的？"},
                metadata={"response_time": 0.5}
            )
    
    def register_handler(self, task_type: str):
        """
        注册任务处理器
        
        Args:
            task_type: 任务类型
            
        Returns:
            装饰器函数
        """
        def decorator(func: Callable):
            self.task_handlers[task_type] = func
            return func
        return decorator
    
    async def execute_task(
        self,
        task_type: str,
        description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> TaskExecution:
        """
        执行任务
        
        Args:
            task_type: 任务类型
            description: 任务描述
            context: 任务上下文
            
        Returns:
            TaskExecution 对象
        """
        # 创建任务实例
        task_id = str(uuid.uuid4())
        task = TaskExecution(
            id=task_id,
            type=task_type,
            description=description,
            status=TaskStatus.SUBMITTED,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )
        
        self.tasks[task_id] = task
        
        # 异步执行任务
        asyncio.create_task(self._run_task(task, context))
        
        return task
    
    async def _run_task(self, task: TaskExecution, context: Optional[Dict] = None):
        """
        运行任务
        
        Args:
            task: 任务实例
            context: 任务上下文
        """
        try:
            # 更新状态
            task.status = TaskStatus.PROCESSING
            task.started_at = datetime.utcnow().isoformat()
            task.updated_at = datetime.utcnow().isoformat()
            
            # WebSocket 推送状态更新
            if HAS_WEBSOCKET and task_ws_manager:
                await task_ws_manager.send_status_update(
                    task.id,
                    "processing",
                    {"progress": 0}
                )
            
            # 获取处理器
            handler = self.task_handlers.get(task.type)
            if not handler:
                # 使用通用处理器
                handler = self.task_handlers.get("general")
            
            # 执行任务
            result = await handler(task)
            
            # 更新结果
            task.result = result
            task.status = TaskStatus.COMPLETED if result.success else TaskStatus.FAILED
            task.completed_at = datetime.utcnow().isoformat()
            task.progress = 100
            
            # WebSocket 推送完成
            if HAS_WEBSOCKET and task_ws_manager:
                await task_ws_manager.send_status_update(
                    task.id,
                    task.status.value,
                    {
                        "progress": 100,
                        "result": {
                            "success": result.success,
                            "data": result.data,
                            "error": result.error
                        }
                    }
                )
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.result = TaskResult(
                success=False,
                error=str(e)
            )
            task.logs.append(f"错误：{str(e)}")
            
            # WebSocket 推送失败
            if HAS_WEBSOCKET and task_ws_manager:
                await task_ws_manager.send_status_update(
                    task.id,
                    "failed",
                    {
                        "error": str(e),
                        "progress": task.progress
                    }
                )
        
        finally:
            task.updated_at = datetime.utcnow().isoformat()
    
    def get_task(self, task_id: str) -> Optional[TaskExecution]:
        """获取任务"""
        return self.tasks.get(task_id)
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态
        
        Args:
            task_id: 任务 ID
            
        Returns:
            任务状态信息
        """
        task = self.tasks.get(task_id)
        if not task:
            return {"error": "Task not found"}
        
        return {
            "id": task.id,
            "type": task.type,
            "status": task.status.value,
            "progress": task.progress,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "logs": task.logs[-10:],  # 最近 10 条日志
            "result": {
                "success": task.result.success if task.result else None,
                "data": task.result.data if task.result else None,
                "error": task.result.error if task.result else None
            } if task.result else None
        }
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            是否取消成功
        """
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        # 只能取消正在处理的任务
        if task.status != TaskStatus.PROCESSING and task.status != TaskStatus.SUBMITTED:
            return False
        
        task.status = TaskStatus.CANCELED
        task.updated_at = datetime.utcnow().isoformat()
        task.logs.append("任务已取消")
        
        return True
    
    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        limit: int = 50
    ) -> List[TaskExecution]:
        """
        列出任务
        
        Args:
            status: 状态过滤
            limit: 返回数量限制
            
        Returns:
            任务列表
        """
        tasks = list(self.tasks.values())
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        # 按创建时间倒序
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        return tasks[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取任务统计"""
        total = len(self.tasks)
        by_status = {}
        
        for task in self.tasks.values():
            status = task.status.value
            by_status[status] = by_status.get(status, 0) + 1
        
        return {
            "total": total,
            "by_status": by_status,
            "handlers": list(self.task_handlers.keys())
        }


# 全局任务执行器实例
executor = TaskExecutor()
