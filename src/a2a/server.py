"""
A2A 服务端 - 让硅基世界 Agent 可以被其他 A2A Agent 访问
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime
import json

from .task_executor import TaskExecutor, TaskStatus, executor as task_executor


# ==================== 数据模型 ====================

class AgentCardModel(BaseModel):
    """Agent Card 数据模型"""
    name: str = "硅基世界 Agent"
    description: str = "硅基世界的 AI Agent，支持社交、记忆、任务管理"
    url: str = "http://localhost:8000"
    version: str = "1.0.0"
    capabilities: List[str] = ["chat", "memory", "social", "task_management"]
    provider: Dict[str, str] = {
        "organization": "Silicon World",
        "url": "https://github.com/huoweigang88888/silicon-world"
    }


class A2AMessage(BaseModel):
    """A2A 消息"""
    role: str
    content: str
    timestamp: str


class A2ARequest(BaseModel):
    """A2A 请求"""
    message: A2AMessage
    context_id: str


class TaskModel(BaseModel):
    """A2A 任务"""
    id: str
    description: str
    type: str = "general"
    status: str = "submitted"
    created_at: str
    updated_at: str


class TaskCreateRequest(BaseModel):
    """任务创建请求"""
    task: Dict[str, Any]


# ==================== A2A 服务端 ====================

class SiliconWorldA2AServer:
    """硅基世界 A2A 服务端"""
    
    def __init__(self, app: FastAPI):
        """
        初始化 A2A 服务端
        
        Args:
            app: FastAPI 应用实例
        """
        self.app = app
        self.agent_card = AgentCardModel()
        
        # 任务存储
        self.tasks: Dict[str, TaskModel] = {}
        
        # 会话存储
        self.contexts: Dict[str, List[Dict]] = {}
        
        # 任务执行器
        self.task_executor = task_executor
        
        # 注册路由
        self._register_routes()
    
    def _register_routes(self):
        """注册 A2A 路由"""
        
        @self.app.get("/.well-known/agent-card.json")
        async def get_agent_card():
            """
            获取 Agent Card（A2A 标准端点）
            
            返回 Agent 的能力描述
            """
            return self.agent_card.dict()
        
        @self.app.post("/message")
        async def handle_message(request: A2ARequest):
            """
            处理 A2A 消息
            
            Args:
                request: A2A 消息请求
                
            Returns:
                响应消息
            """
            # 保存会话上下文
            if request.context_id not in self.contexts:
                self.contexts[request.context_id] = []
            
            self.contexts[request.context_id].append({
                "role": "user",
                "content": request.message.content,
                "timestamp": request.message.timestamp
            })
            
            # TODO: 调用硅基世界的消息处理逻辑
            # 这里先返回简单响应
            response_text = f"[硅基世界] 收到消息：{request.message.content}"
            
            # 保存响应到上下文
            self.contexts[request.context_id].append({
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return {
                "response": response_text,
                "context_id": request.context_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        @self.app.post("/message/stream")
        async def handle_stream_message(request: A2ARequest):
            """
            处理流式消息
            
            Args:
                request: A2A 消息请求
                
            Returns:
                流式响应
            """
            from fastapi.responses import StreamingResponse
            import asyncio
            
            async def generate():
                """生成流式响应"""
                try:
                    # 保存会话上下文
                    if request.context_id not in self.contexts:
                        self.contexts[request.context_id] = []
                    
                    self.contexts[request.context_id].append({
                        "role": "user",
                        "content": request.message.content,
                        "timestamp": request.message.timestamp
                    })
                    
                    # 发送确认帧
                    yield json.dumps({
                        "type": "start",
                        "context_id": request.context_id
                    }) + "\n"
                    
                    # 模拟思考过程
                    yield json.dumps({
                        "type": "thinking",
                        "content": "正在理解您的问题..."
                    }) + "\n"
                    
                    await asyncio.sleep(0.5)
                    
                    # 生成响应内容（流式）
                    response_text = f"收到您的消息：{request.message.content}"
                    words = response_text.split()
                    
                    for i, word in enumerate(words):
                        yield json.dumps({
                            "type": "content",
                            "content": word + " ",
                            "index": i
                        }) + "\n"
                        await asyncio.sleep(0.1)  # 模拟打字速度
                    
                    # 保存完整响应
                    self.contexts[request.context_id].append({
                        "role": "assistant",
                        "content": response_text,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                    # 发送结束帧
                    yield json.dumps({
                        "type": "end",
                        "content": response_text,
                        "context_id": request.context_id
                    }) + "\n"
                    
                except Exception as e:
                    yield json.dumps({
                        "type": "error",
                        "error": str(e)
                    }) + "\n"
            
            return StreamingResponse(
                generate(),
                media_type="application/x-ndjson"
            )
        
        @self.app.post("/task")
        async def create_task(request: TaskCreateRequest):
            """
            创建任务
            
            Args:
                request: 任务创建请求
                
            Returns:
                任务信息
            """
            task_data = request.task
            
            # 使用任务执行器执行
            task_type = task_data.get('type', 'general')
            description = task_data.get('description', 'Unknown task')
            
            task_execution = await self.task_executor.execute_task(
                task_type=task_type,
                description=description
            )
            
            # 同时保存到任务存储（兼容旧 API）
            task = TaskModel(
                id=task_execution.id,
                description=description,
                type=task_type,
                status=task_execution.status.value,
                created_at=task_execution.created_at,
                updated_at=task_execution.updated_at
            )
            
            self.tasks[task.id] = task
            
            return {
                "task": {
                    "id": task.id,
                    "status": task.status,
                    "type": task.type,
                    "progress": task_execution.progress,
                    "logs": task_execution.logs
                },
                "status": "submitted"
            }
        
        @self.app.get("/task/{task_id}")
        async def get_task(task_id: str):
            """
            获取任务状态
            
            Args:
                task_id: 任务 ID
                
            Returns:
                任务状态
            """
            # 从任务执行器获取详细状态
            status = self.task_executor.get_task_status(task_id)
            
            if "error" in status:
                # 回退到旧的任务存储
                task = self.tasks.get(task_id)
                if not task:
                    raise HTTPException(status_code=404, detail="Task not found")
                
                return {
                    "task": task.dict(),
                    "status": task.status
                }
            
            return status
        
        @self.app.post("/task/{task_id}/cancel")
        async def cancel_task(task_id: str):
            """
            取消任务
            
            Args:
                task_id: 任务 ID
                
            Returns:
                取消结果
            """
            task = self.tasks.get(task_id)
            
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")
            
            task.status = "canceled"
            task.updated_at = datetime.utcnow().isoformat()
            
            return {
                "success": True,
                "task_id": task_id,
                "status": "canceled"
            }
        
        @self.app.get("/health")
        async def health_check():
            """健康检查"""
            return {
                "status": "healthy",
                "service": "silicon-world-a2a",
                "version": self.agent_card.version
            }
    
    def get_agent_card(self) -> AgentCardModel:
        """获取 Agent Card"""
        return self.agent_card
    
    def update_agent_card(self, **kwargs):
        """
        更新 Agent Card
        
        Args:
            **kwargs: 要更新的字段
        """
        for key, value in kwargs.items():
            if hasattr(self.agent_card, key):
                setattr(self.agent_card, key, value)
    
    def get_task(self, task_id: str) -> Optional[TaskModel]:
        """获取任务"""
        return self.tasks.get(task_id)
    
    def update_task_status(self, task_id: str, status: str):
        """
        更新任务状态
        
        Args:
            task_id: 任务 ID
            status: 新状态
        """
        task = self.tasks.get(task_id)
        if task:
            task.status = status
            task.updated_at = datetime.utcnow().isoformat()
