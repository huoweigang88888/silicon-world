"""
A2A 客户端 - 用于与其他 A2A Agent 通信
"""

import httpx
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass
class AgentCard:
    """Agent 名片"""
    name: str
    description: str
    url: str
    version: str
    capabilities: List[str]
    provider: Optional[Dict[str, str]] = None


@dataclass
class Task:
    """A2A 任务"""
    id: str
    description: str
    status: str
    created_at: str
    updated_at: str
    agent_url: str


class SiliconWorldA2AClient:
    """硅基世界 A2A 客户端"""
    
    def __init__(self, default_server_url: str = None):
        """
        初始化 A2A 客户端
        
        Args:
            default_server_url: 默认 A2A 服务器 URL
        """
        self.default_server_url = default_server_url
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.http_client.aclose()
    
    async def discover_agent(self, agent_url: str) -> Optional[AgentCard]:
        """
        发现 Agent（获取 Agent Card）
        
        Args:
            agent_url: Agent 的基础 URL
            
        Returns:
            AgentCard 对象，如果失败返回 None
        """
        try:
            # A2A 标准：Agent Card 在 .well-known/agent-card.json
            card_url = agent_url.rstrip('/') + '/.well-known/agent-card.json'
            
            response = await self.http_client.get(card_url)
            response.raise_for_status()
            
            data = response.json()
            
            card = AgentCard(
                name=data.get('name', 'Unknown'),
                description=data.get('description', ''),
                url=data.get('url', agent_url),
                version=data.get('version', '1.0.0'),
                capabilities=data.get('capabilities', []),
                provider=data.get('provider')
            )
            
            print(f"[A2A] 发现 Agent: {card.name}")
            return card
            
        except Exception as e:
            print(f"[A2A] 发现 Agent 失败：{e}")
            return None
    
    async def send_message(
        self,
        agent_url: str,
        message: str,
        context_id: Optional[str] = None
    ) -> str:
        """
        发送消息给 A2A Agent
        
        Args:
            agent_url: Agent URL
            message: 消息内容
            context_id: 会话上下文 ID（可选）
            
        Returns:
            Agent 响应文本
        """
        try:
            # A2A 消息端点
            message_url = agent_url.rstrip('/') + '/message'
            
            # 构建 A2A 消息请求
            payload = {
                "message": {
                    "role": "user",
                    "content": message,
                    "timestamp": datetime.utcnow().isoformat()
                },
                "context_id": context_id or str(uuid.uuid4())
            }
            
            response = await self.http_client.post(
                message_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            data = response.json()
            response_text = data.get('response', data.get('message', ''))
            
            print(f"[A2A] 消息已发送，收到响应")
            return response_text
            
        except Exception as e:
            print(f"[A2A] 发送消息失败：{e}")
            return f"错误：{str(e)}"
    
    async def create_task(
        self,
        agent_url: str,
        description: str,
        task_type: str = "general"
    ) -> Task:
        """
        在远程 Agent 创建任务
        
        Args:
            agent_url: Agent URL
            description: 任务描述
            task_type: 任务类型
            
        Returns:
            Task 对象
        """
        try:
            # A2A 任务创建端点
            task_url = agent_url.rstrip('/') + '/task'
            
            payload = {
                "task": {
                    "description": description,
                    "type": task_type,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            response = await self.http_client.post(
                task_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            data = response.json()
            task_data = data.get('task', data)
            
            task = Task(
                id=task_data.get('id', str(uuid.uuid4())),
                description=description,
                status=task_data.get('status', 'submitted'),
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat(),
                agent_url=agent_url
            )
            
            print(f"[A2A] 任务已创建：{task.id}")
            return task
            
        except Exception as e:
            print(f"[A2A] 创建任务失败：{e}")
            raise
    
    async def get_task_status(
        self,
        agent_url: str,
        task_id: str
    ) -> Dict[str, Any]:
        """
        获取任务状态
        
        Args:
            agent_url: Agent URL
            task_id: 任务 ID
            
        Returns:
            任务状态信息
        """
        try:
            status_url = agent_url.rstrip('/') + f'/task/{task_id}'
            
            response = await self.http_client.get(status_url)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"[A2A] 获取任务状态失败：{e}")
            return {"error": str(e)}
    
    async def cancel_task(
        self,
        agent_url: str,
        task_id: str
    ) -> bool:
        """
        取消任务
        
        Args:
            agent_url: Agent URL
            task_id: 任务 ID
            
        Returns:
            是否取消成功
        """
        try:
            cancel_url = agent_url.rstrip('/') + f'/task/{task_id}/cancel'
            
            response = await self.http_client.post(cancel_url)
            response.raise_for_status()
            
            print(f"[A2A] 任务已取消：{task_id}")
            return True
            
        except Exception as e:
            print(f"[A2A] 取消任务失败：{e}")
            return False
    
    async def stream_message(
        self,
        agent_url: str,
        message: str,
        context_id: Optional[str] = None
    ):
        """
        流式发送消息（用于长响应）
        
        Args:
            agent_url: Agent URL
            message: 消息内容
            context_id: 会话上下文 ID
            
        Yields:
            流式响应片段
        """
        try:
            stream_url = agent_url.rstrip('/') + '/message/stream'
            
            payload = {
                "message": {
                    "role": "user",
                    "content": message,
                    "timestamp": datetime.utcnow().isoformat()
                },
                "context_id": context_id or str(uuid.uuid4())
            }
            
            async with self.http_client.stream(
                "POST",
                stream_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line:
                        yield line
            
        except Exception as e:
            print(f"[A2A] 流式消息失败：{e}")
            yield f"错误：{str(e)}"
