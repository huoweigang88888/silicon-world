"""
Agent 心跳检测服务

定期检查外部 Agent 的连接状态，自动更新状态
"""

import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy.orm import Session
from src.core.database import AgentModel, AgentRepository
from loguru import logger


class HeartbeatService:
    """心跳检测服务"""
    
    def __init__(self, db: Session, check_interval: int = 60):
        """
        初始化心跳服务
        
        Args:
            db: 数据库会话
            check_interval: 检查间隔 (秒)，默认 60 秒
        """
        self.db = db
        self.check_interval = check_interval
        self.running = False
        self.task = None
        self.logger = logger
    
    async def check_agent(self, agent: AgentModel) -> dict:
        """
        检查单个 Agent 连接
        
        Args:
            agent: Agent 实例
            
        Returns:
            检查结果
        """
        # 只检查外部 Agent
        if agent.agent_type != "external":
            return {
                "agent_id": agent.id,
                "success": True,
                "message": "原生 Agent，跳过检查",
                "status": "online"
            }
        
        # 获取连接配置
        connection = agent.connection_info or {}
        endpoint = connection.get("endpoint")
        
        if not endpoint:
            return {
                "agent_id": agent.id,
                "success": False,
                "message": "未配置连接端点",
                "status": "error"
            }
        
        # 构建请求
        auth_type = connection.get("auth_type", "none")
        auth_value = connection.get("auth")
        
        headers = {}
        if auth_type == "bearer" and auth_value:
            headers["Authorization"] = f"Bearer {auth_value}"
        elif auth_type == "basic" and auth_value:
            headers["Authorization"] = f"Basic {auth_value}"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(endpoint, headers=headers)
                
                if response.status_code < 400:
                    # 连接成功
                    return {
                        "agent_id": agent.id,
                        "success": True,
                        "message": "连接成功",
                        "status_code": response.status_code,
                        "status": "online"
                    }
                else:
                    # HTTP 错误
                    return {
                        "agent_id": agent.id,
                        "success": False,
                        "message": f"HTTP {response.status_code}",
                        "status_code": response.status_code,
                        "status": "error"
                    }
        except httpx.TimeoutException:
            return {
                "agent_id": agent.id,
                "success": False,
                "message": "连接超时",
                "status": "offline"
            }
        except httpx.NetworkError:
            return {
                "agent_id": agent.id,
                "success": False,
                "message": "网络错误",
                "status": "offline"
            }
        except Exception as e:
            return {
                "agent_id": agent.id,
                "success": False,
                "message": f"错误：{str(e)}",
                "status": "error"
            }
    
    async def check_all_agents(self) -> List[dict]:
        """
        检查所有外部 Agent
        
        Returns:
            检查结果列表
        """
        results = []
        
        # 获取所有活跃的外部 Agent
        agents = self.db.query(AgentModel).filter(
            AgentModel.active == True,
            AgentModel.agent_type == "external"
        ).all()
        
        self.logger.info(f"开始心跳检测，共 {len(agents)} 个外部 Agent")
        
        for agent in agents:
            result = await self.check_agent(agent)
            results.append(result)
            
            # 更新数据库状态
            if result["success"]:
                AgentRepository(self.db).update(
                    agent.id,
                    status=result["status"],
                    last_seen=datetime.utcnow()
                )
            else:
                AgentRepository(self.db).update(
                    agent.id,
                    status=result["status"]
                )
            
            self.logger.info(
                f"Agent {agent.name} ({agent.id[:20]}...): "
                f"{result['status']} - {result['message']}"
            )
        
        return results
    
    async def start(self):
        """启动心跳检测"""
        self.running = True
        self.logger.info(f"心跳服务启动，检查间隔：{self.check_interval}秒")
        
        while self.running:
            try:
                await self.check_all_agents()
            except Exception as e:
                self.logger.error(f"心跳检测失败：{str(e)}")
            
            await asyncio.sleep(self.check_interval)
    
    def stop(self):
        """停止心跳检测"""
        self.running = False
        self.logger.info("心跳服务已停止")


# 全局心跳服务实例
_heartbeat_service: HeartbeatService = None


def get_heartbeat_service(db: Session) -> HeartbeatService:
    """获取心跳服务实例"""
    global _heartbeat_service
    if _heartbeat_service is None:
        _heartbeat_service = HeartbeatService(db)
    return _heartbeat_service


async def start_heartbeat_background(db: Session, interval: int = 60):
    """
    在后台启动心跳服务
    
    Args:
        db: 数据库会话
        interval: 检查间隔 (秒)
    """
    service = HeartbeatService(db, interval)
    await service.start()
