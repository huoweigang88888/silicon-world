"""
WebSocket 任务推送

实时推送任务状态更新
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import asyncio
import json
from datetime import datetime


class TaskWebSocketManager:
    """
    任务 WebSocket 管理器
    
    管理任务状态的 WebSocket 推送
    """
    
    def __init__(self):
        """初始化管理器"""
        # task_id -> List[WebSocket]
        self.task_connections: Dict[str, List[WebSocket]] = {}
        # agent_id -> List[WebSocket]
        self.agent_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect_task(
        self,
        websocket: WebSocket,
        task_id: str
    ):
        """
        连接到任务
        
        Args:
            websocket: WebSocket 连接
            task_id: 任务 ID
        """
        await websocket.accept()
        
        if task_id not in self.task_connections:
            self.task_connections[task_id] = []
        
        self.task_connections[task_id].append(websocket)
        
        # 发送连接确认
        await websocket.send_json({
            "type": "connected",
            "task_id": task_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def connect_agent(
        self,
        websocket: WebSocket,
        agent_id: str
    ):
        """
        连接到 Agent（接收该 Agent 的所有任务更新）
        
        Args:
            websocket: WebSocket 连接
            agent_id: Agent ID
        """
        await websocket.accept()
        
        if agent_id not in self.agent_connections:
            self.agent_connections[agent_id] = []
        
        self.agent_connections[agent_id].append(websocket)
    
    def disconnect_task(
        self,
        websocket: WebSocket,
        task_id: str
    ):
        """
        断开任务连接
        
        Args:
            websocket: WebSocket 连接
            task_id: 任务 ID
        """
        if task_id in self.task_connections:
            if websocket in self.task_connections[task_id]:
                self.task_connections[task_id].remove(websocket)
                
                if len(self.task_connections[task_id]) == 0:
                    del self.task_connections[task_id]
    
    def disconnect_agent(
        self,
        websocket: WebSocket,
        agent_id: str
    ):
        """
        断开 Agent 连接
        
        Args:
            websocket: WebSocket 连接
            agent_id: Agent ID
        """
        if agent_id in self.agent_connections:
            if websocket in self.agent_connections[agent_id]:
                self.agent_connections[agent_id].remove(websocket)
                
                if len(self.agent_connections[agent_id]) == 0:
                    del self.agent_connections[agent_id]
    
    async def send_task_update(
        self,
        task_id: str,
        update: Dict
    ):
        """
        发送任务更新
        
        Args:
            task_id: 任务 ID
            update: 更新数据
        """
        if task_id in self.task_connections:
            message = {
                "type": "task_update",
                "task_id": task_id,
                "data": update,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # 发送给所有订阅该任务的客户端
            disconnected = []
            
            for websocket in self.task_connections[task_id]:
                try:
                    await websocket.send_json(message)
                except Exception:
                    disconnected.append(websocket)
            
            # 清理断开的连接
            for ws in disconnected:
                self.task_connections[task_id].remove(ws)
    
    async def send_progress_update(
        self,
        task_id: str,
        progress: int,
        logs: List[str] = None
    ):
        """
        发送进度更新
        
        Args:
            task_id: 任务 ID
            progress: 进度 (0-100)
            logs: 日志列表
        """
        update = {
            "progress": progress,
            "logs": logs or []
        }
        
        await self.send_task_update(task_id, update)
    
    async def send_status_update(
        self,
        task_id: str,
        status: str,
        result: Dict = None
    ):
        """
        发送状态更新
        
        Args:
            task_id: 任务 ID
            status: 状态 (submitted/processing/completed/failed/canceled)
            result: 任务结果
        """
        update = {
            "status": status,
            "result": result
        }
        
        await self.send_task_update(task_id, update)
    
    def get_subscriber_count(self, task_id: str) -> int:
        """
        获取任务订阅者数量
        
        Args:
            task_id: 任务 ID
            
        Returns:
            订阅者数量
        """
        return len(self.task_connections.get(task_id, []))
    
    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            统计字典
        """
        return {
            "task_connections": len(self.task_connections),
            "agent_connections": len(self.agent_connections),
            "total_subscribers": sum(
                len(conns) for conns in self.task_connections.values()
            )
        }


# 全局任务 WebSocket 管理器实例
task_ws_manager = TaskWebSocketManager()


# ==================== WebSocket 路由 ====================

def register_websocket_routes(app):
    """
    注册 WebSocket 路由
    
    Args:
        app: FastAPI 应用
    """
    
    @app.websocket("/ws/tasks/{task_id}")
    async def task_websocket_endpoint(
        websocket: WebSocket,
        task_id: str
    ):
        """
        任务 WebSocket 端点
        
        订阅特定任务的状态更新
        
        - **task_id**: 任务 ID
        """
        await task_ws_manager.connect_task(websocket, task_id)
        
        try:
            while True:
                # 接收客户端消息（心跳等）
                data = await websocket.receive_text()
                
                if data == "ping":
                    await websocket.send_text("pong")
                
                elif data.startswith("subscribe:"):
                    # 订阅其他任务
                    other_task_id = data.split(":")[1]
                    await task_ws_manager.connect_task(websocket, other_task_id)
        
        except WebSocketDisconnect:
            task_ws_manager.disconnect_task(websocket, task_id)
        except Exception as e:
            task_ws_manager.disconnect_task(websocket, task_id)
            raise
    
    @app.websocket("/ws/agent/{agent_id}/tasks")
    async def agent_tasks_websocket_endpoint(
        websocket: WebSocket,
        agent_id: str
    ):
        """
        Agent 任务 WebSocket 端点
        
        接收该 Agent 的所有任务更新
        
        - **agent_id**: Agent ID
        """
        await task_ws_manager.connect_agent(websocket, agent_id)
        
        try:
            while True:
                data = await websocket.receive_text()
                
                if data == "ping":
                    await websocket.send_text("pong")
        
        except WebSocketDisconnect:
            task_ws_manager.disconnect_agent(websocket, agent_id)
        except Exception as e:
            task_ws_manager.disconnect_agent(websocket, agent_id)
            raise
    
    @app.get("/api/v1/ws/tasks/stats")
    async def get_websocket_stats():
        """获取 WebSocket 统计"""
        return task_ws_manager.get_stats()
