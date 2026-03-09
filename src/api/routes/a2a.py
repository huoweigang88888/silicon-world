"""
A2A API 路由

提供 A2A 协议相关的 REST API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.a2a.client import SiliconWorldA2AClient
from src.a2a.x402 import SiliconWorldPayment

router = APIRouter(tags=["A2A"])

# 全局 A2A 客户端和支付处理器
a2a_client = SiliconWorldA2AClient()
payment_processor = SiliconWorldPayment()


# ==================== 请求/响应模型 ====================

class AgentDiscoveryRequest(BaseModel):
    """Agent 发现请求"""
    agent_url: str


class AgentCardResponse(BaseModel):
    """Agent Card 响应"""
    name: str
    description: str
    url: str
    version: str
    capabilities: List[str]
    provider: Optional[Dict[str, str]] = None


class A2AMessageRequest(BaseModel):
    """A2A 消息请求"""
    agent_url: str
    message: str
    context_id: Optional[str] = None


class A2AMessageResponse(BaseModel):
    """A2A 消息响应"""
    response: str
    context_id: str
    success: bool


class TaskCreateRequest(BaseModel):
    """任务创建请求"""
    agent_url: str
    description: str
    task_type: Optional[str] = "general"


class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    task_id: str
    status: str
    description: str
    created_at: str
    updated_at: str


class PaymentRequestModel(BaseModel):
    """支付请求"""
    amount: float
    currency: Optional[str] = "CNY"
    description: Optional[str] = "Agent service payment"


class PaymentResponse(BaseModel):
    """支付响应"""
    payment_id: str
    amount: float
    currency: str
    payment_url: str
    expires_at: str
    status: str


# ==================== A2A API ====================

@router.post("/api/v1/a2a/discover", response_model=AgentCardResponse)
async def discover_agent(request: AgentDiscoveryRequest):
    """
    发现 A2A Agent
    
    获取目标 Agent 的能力描述（Agent Card）
    
    - **agent_url**: Agent 的基础 URL
    """
    try:
        card = await a2a_client.discover_agent(request.agent_url)
        
        if not card:
            raise HTTPException(status_code=404, detail="Agent 未找到或不可访问")
        
        return AgentCardResponse(
            name=card.name,
            description=card.description,
            url=card.url,
            version=card.version,
            capabilities=card.capabilities,
            provider=card.provider
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发现 Agent 失败：{str(e)}")


@router.post("/api/v1/a2a/send-message", response_model=A2AMessageResponse)
async def send_a2a_message(request: A2AMessageRequest):
    """
    发送 A2A 消息
    
    向其他 A2A Agent 发送消息并获取响应
    
    - **agent_url**: 目标 Agent URL
    - **message**: 消息内容
    - **context_id**: 会话上下文 ID（可选，用于多轮对话）
    """
    try:
        response = await a2a_client.send_message(
            agent_url=request.agent_url,
            message=request.message,
            context_id=request.context_id
        )
        
        return A2AMessageResponse(
            response=response,
            context_id=request.context_id or "new",
            success=not response.startswith("错误：")
        )
        
    except Exception as e:
        return A2AMessageResponse(
            response=f"错误：{str(e)}",
            context_id=request.context_id or "error",
            success=False
        )


@router.post("/api/v1/a2a/create-task")
async def create_a2a_task(request: TaskCreateRequest):
    """
    创建 A2A 任务
    
    在远程 Agent 创建并执行任务
    
    - **agent_url**: 目标 Agent URL
    - **description**: 任务描述
    - **task_type**: 任务类型 (general/research/analysis 等)
    """
    try:
        task = await a2a_client.create_task(
            agent_url=request.agent_url,
            description=request.description,
            task_type=request.task_type
        )
        
        return {
            "success": True,
            "task_id": task.id,
            "status": task.status,
            "description": task.description,
            "created_at": task.created_at
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建任务失败：{str(e)}")


@router.get("/api/v1/a2a/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str, agent_url: str):
    """
    获取 A2A 任务状态
    
    - **task_id**: 任务 ID
    - **agent_url**: Agent URL
    """
    try:
        status = await a2a_client.get_task_status(
            agent_url=agent_url,
            task_id=task_id
        )
        
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        
        task_data = status.get("task", status)
        
        return TaskStatusResponse(
            task_id=task_id,
            status=task_data.get("status", "unknown"),
            description=task_data.get("description", ""),
            created_at=task_data.get("created_at", ""),
            updated_at=task_data.get("updated_at", "")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务状态失败：{str(e)}")


@router.get("/api/v1/a2a/task/{task_id}/cancel")
async def cancel_a2a_task(task_id: str, agent_url: str):
    """
    取消 A2A 任务
    
    - **task_id**: 任务 ID
    - **agent_url**: Agent URL
    """
    try:
        success = await a2a_client.cancel_task(
            agent_url=agent_url,
            task_id=task_id
        )
        
        return {
            "success": success,
            "task_id": task_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取消任务失败：{str(e)}")


@router.get("/api/v1/a2a/tasks")
async def list_tasks(
    status: Optional[str] = None,
    limit: int = 50
):
    """
    列出任务
    
    - **status**: 状态过滤 (submitted/processing/completed/failed/canceled)
    - **limit**: 返回数量限制
    """
    from src.a2a.task_executor import TaskStatus, executor
    
    if status:
        try:
            status_filter = TaskStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的状态：{status}")
    else:
        status_filter = None
    
    tasks = executor.list_tasks(status=status_filter, limit=limit)
    
    return {
        "count": len(tasks),
        "tasks": [
            {
                "id": task.id,
                "type": task.type,
                "status": task.status.value,
                "progress": task.progress,
                "created_at": task.created_at,
                "updated_at": task.updated_at
            }
            for task in tasks
        ]
    }


@router.get("/api/v1/a2a/tasks/stats")
async def get_task_stats():
    """
    获取任务统计
    """
    from src.a2a.task_executor import executor
    
    stats = executor.get_stats()
    
    return stats


# ==================== 支付 API ====================

@router.post("/api/v1/a2a/payment/request", response_model=PaymentResponse)
async def create_payment_request(request: PaymentRequestModel):
    """
    创建支付请求
    
    用于 Agent 服务的付费
    
    - **amount**: 金额
    - **currency**: 货币类型 (CNY/USD/BTC)
    - **description**: 支付描述
    """
    try:
        payment_request = await payment_processor.create_payment_request(
            amount=request.amount,
            currency=request.currency,
            description=request.description
        )
        
        return PaymentResponse(
            payment_id=payment_request.id,
            amount=payment_request.amount,
            currency=payment_request.currency,
            payment_url=payment_request.payment_url,
            expires_at=payment_request.expires_at,
            status=payment_request.status
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建支付请求失败：{str(e)}")


@router.get("/api/v1/a2a/payment/{payment_id}")
async def get_payment_status(payment_id: str):
    """
    获取支付状态
    
    - **payment_id**: 支付 ID
    """
    payment = payment_processor.get_payment_request(payment_id)
    
    if not payment:
        raise HTTPException(status_code=404, detail="支付请求不存在")
    
    return {
        "payment_id": payment.id,
        "amount": payment.amount,
        "currency": payment.currency,
        "status": payment.status,
        "expires_at": payment.expires_at
    }


# ==================== 本地 A2A 服务端信息 ====================

@router.get("/api/v1/a2a/agent-card")
async def get_local_agent_card():
    """
    获取本地 Agent Card
    
    返回硅基世界 Agent 的能力描述
    """
    from src.a2a.server import AgentCardModel
    
    card = AgentCardModel()
    return card.dict()


@router.get("/api/v1/a2a/status")
async def get_a2a_status():
    """
    获取 A2A 系统状态
    """
    return {
        "status": "healthy",
        "service": "silicon-world-a2a",
        "version": "1.0.0",
        "capabilities": [
            "agent_discovery",
            "message_sending",
            "task_management",
            "payment_support"
        ]
    }
