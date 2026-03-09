"""
WebSocket 路由
提供实时通信功能
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.websocket_manager import manager

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/agent/{agent_id}")
async def agent_websocket_endpoint(
    websocket: WebSocket,
    agent_id: str
):
    """
    Agent WebSocket 连接端点
    
    用于接收实时消息和通知
    
    - **agent_id**: Agent ID
    """
    await manager.connect(websocket, agent_id)
    
    try:
        while True:
            # 接收客户端消息（心跳等）
            data = await websocket.receive_text()
            
            # 可以处理客户端发送的消息
            # 目前主要用于保持连接
            if data == "ping":
                await websocket.send_text("pong")
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, agent_id)
    except Exception as e:
        manager.disconnect(websocket, agent_id)
        raise e


@router.websocket("/ws/social/{agent_id}")
async def social_websocket_endpoint(
    websocket: WebSocket,
    agent_id: str,
    room: Optional[str] = Query(None, description="房间 ID (用于群聊)")
):
    """
    社交 WebSocket 连接端点
    
    用于实时社交功能（消息、通知等）
    
    - **agent_id**: Agent ID
    - **room**: 房间 ID (可选，用于群聊)
    """
    await manager.connect(websocket, agent_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # 处理不同类型的消息
            msg_type = data.get("type")
            
            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
            
            elif msg_type == "typing":
                # 正在输入通知
                await manager.send_to_agent(
                    data.get("target_id"),
                    {
                        "type": "typing",
                        "from_agent_id": agent_id,
                        "room": room
                    }
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, agent_id)
    except Exception as e:
        manager.disconnect(websocket, agent_id)
        raise e


@router.get("/api/v1/ws/online", tags=["WebSocket"])
async def get_online_agents():
    """获取在线 Agent 列表"""
    return {
        "online_count": manager.get_online_count(),
        "online_agents": list(manager.active_connections.keys())
    }


@router.get("/api/v1/ws/status/{agent_id}", tags=["WebSocket"])
async def get_agent_status(agent_id: str):
    """获取 Agent 在线状态"""
    return {
        "agent_id": agent_id,
        "online": manager.is_online(agent_id)
    }
