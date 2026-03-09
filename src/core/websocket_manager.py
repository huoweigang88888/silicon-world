"""
WebSocket 管理器
支持实时消息推送
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
from datetime import datetime
from loguru import logger


class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        # agent_id -> List[WebSocket]
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, agent_id: str):
        """
        接受 WebSocket 连接
        
        Args:
            websocket: WebSocket 连接
            agent_id: Agent ID
        """
        await websocket.accept()
        
        if agent_id not in self.active_connections:
            self.active_connections[agent_id] = []
        
        self.active_connections[agent_id].append(websocket)
        logger.info(f"[WebSocket] Agent {agent_id} connected")
    
    def disconnect(self, websocket: WebSocket, agent_id: str):
        """
        断开 WebSocket 连接
        
        Args:
            websocket: WebSocket 连接
            agent_id: Agent ID
        """
        if agent_id in self.active_connections:
            if websocket in self.active_connections[agent_id]:
                self.active_connections[agent_id].remove(websocket)
                
                # 如果没有连接了，删除这个 agent
                if len(self.active_connections[agent_id]) == 0:
                    del self.active_connections[agent_id]
        
        logger.info(f"[WebSocket] Agent {agent_id} disconnected")
    
    async def send_to_agent(self, agent_id: str, message: dict):
        """
        发送消息给指定 Agent
        
        Args:
            agent_id: Agent ID
            message: 消息内容 (dict)
        """
        if agent_id in self.active_connections:
            for connection in self.active_connections[agent_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"[WebSocket] Failed to send to {agent_id}: {e}")
    
    async def broadcast(self, message: dict, exclude_agent: str = None):
        """
        广播消息给所有在线 Agent
        
        Args:
            message: 消息内容
            exclude_agent: 排除的 Agent ID
        """
        for agent_id in self.active_connections:
            if agent_id != exclude_agent:
                await self.send_to_agent(agent_id, message)
    
    async def send_notification(self, agent_id: str, title: str, content: str, data: dict = None):
        """
        发送通知
        
        Args:
            agent_id: Agent ID
            title: 通知标题
            content: 通知内容
            data: 额外数据
        """
        message = {
            "type": "notification",
            "title": title,
            "content": content,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_to_agent(agent_id, message)
    
    async def send_new_message(self, agent_id: str, message_data: dict):
        """
        发送新消息通知
        
        Args:
            agent_id: Agent ID
            message_data: 消息数据
        """
        message = {
            "type": "new_message",
            "message": message_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_to_agent(agent_id, message)
    
    async def send_friend_request(self, agent_id: str, from_agent_id: str, from_agent_name: str):
        """
        发送好友请求通知
        
        Args:
            agent_id: Agent ID
            from_agent_id: 发送者 ID
            from_agent_name: 发送者名字
        """
        message = {
            "type": "friend_request",
            "from_agent_id": from_agent_id,
            "from_agent_name": from_agent_name,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_to_agent(agent_id, message)
    
    def get_online_count(self) -> int:
        """获取在线 Agent 数量"""
        return len(self.active_connections)
    
    def is_online(self, agent_id: str) -> bool:
        """检查 Agent 是否在线"""
        return agent_id in self.active_connections and len(self.active_connections[agent_id]) > 0


# 全局管理器实例
manager = ConnectionManager()
