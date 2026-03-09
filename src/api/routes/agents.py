"""
Agent 路由 - 创建和管理 Agent
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.database import SessionLocal, AgentRepository, MemoryRepository, AgentModel, MemoryModel

router = APIRouter(tags=["Agent"])


# ==================== 模板系统 ====================

@router.get("/api/v1/templates")
async def list_templates(category: str = None):
    """
    获取 Agent 模板列表
    
    - **category**: 分类 (messaging, ai, native)
    """
    from src.core.templates import get_all_templates, get_templates_by_category
    
    if category:
        templates = get_templates_by_category(category)
    else:
        templates = get_all_templates()
    
    return {
        "count": len(templates),
        "templates": templates
    }


@router.get("/api/v1/templates/{template_id}")
async def get_template(template_id: str):
    """
    获取单个模板详情
    
    - **template_id**: 模板 ID
    """
    from src.core.templates import get_template
    
    template = get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return template


@router.post("/api/v1/templates/{template_id}/apply")
async def apply_template(template_id: str, user_inputs: dict):
    """
    应用模板配置
    
    - **template_id**: 模板 ID
    - **user_inputs**: 用户输入的配置值
    """
    from src.core.templates import apply_template, get_template
    
    # 验证模板存在
    template = get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # 应用模板
    try:
        config = apply_template(template_id, user_inputs)
        return {
            "success": True,
            "template_id": template_id,
            "config": config
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== 数据模型 ====================

class AgentCreate(BaseModel):
    """创建 Agent 请求"""
    name: str
    controller: str
    personality: Optional[dict] = None
    agent_type: Optional[str] = "native"  # native 或 external
    connection_info: Optional[dict] = None
    capabilities: Optional[list] = None


class AgentResponse(BaseModel):
    """Agent 响应"""
    id: str
    name: str
    controller: str
    personality: Optional[dict]
    created_at: str
    active: bool
    agent_type: Optional[str]
    connection_info: Optional[dict]
    capabilities: Optional[list]
    status: Optional[str]
    last_seen: Optional[str]


class AgentUpdate(BaseModel):
    """更新 Agent 请求"""
    name: Optional[str] = None
    personality: Optional[dict] = None
    active: Optional[bool] = None
    connection_info: Optional[dict] = None
    capabilities: Optional[list] = None
    status: Optional[str] = None


class MemoryCreate(BaseModel):
    """创建记忆请求"""
    content: str
    memory_type: str  # short_term, long_term, semantic


class MemoryResponse(BaseModel):
    """记忆响应"""
    id: str
    agent_id: str
    content: str
    memory_type: str
    created_at: str


# ==================== Agent 路由 ====================

@router.post("/api/v1/agents", response_model=AgentResponse)
async def create_agent(data: AgentCreate):
    """
    创建新的 Agent
    
    - **name**: Agent 名称
    - **controller**: 控制者地址
    - **personality**: 人格配置 (可选)
    - **agent_type**: 类型 (native 或 external)
    - **connection_info**: 连接配置 (外部 Agent 需要)
    - **capabilities**: 能力列表
    """
    import uuid
    from datetime import datetime
    
    db = SessionLocal()
    try:
        agent_repo = AgentRepository(db)
        
        # 生成 Agent ID (DID)
        agent_id = f"did:silicon:agent:{uuid.uuid4().hex}"
        
        # 创建 Agent
        agent = agent_repo.create(
            agent_id=agent_id,
            name=data.name,
            controller=data.controller,
            personality=data.personality or {},
            agent_type=data.agent_type or "native",
            connection_info=data.connection_info or {},
            capabilities=data.capabilities or []
        )
        
        return AgentResponse(
            id=agent.id,
            name=agent.name,
            controller=agent.controller,
            personality=agent.personality,
            created_at=agent.created_at.isoformat(),
            active=agent.active,
            agent_type=agent.agent_type,
            connection_info=agent.connection_info,
            capabilities=agent.capabilities,
            status=agent.status,
            last_seen=None
        )
    finally:
        db.close()


@router.get("/api/v1/agents", response_model=List[AgentResponse])
async def list_agents(limit: int = 10, offset: int = 0):
    """
    获取 Agent 列表
    
    - **limit**: 返回数量限制
    - **offset**: 偏移量
    """
    db = SessionLocal()
    try:
        agent_repo = AgentRepository(db)
        agents = agent_repo.list(limit=limit, offset=offset)
        
        return [
            AgentResponse(
                id=a.id,
                name=a.name,
                controller=a.controller,
                personality=a.personality,
                created_at=a.created_at.isoformat(),
                active=a.active,
                agent_type=a.agent_type,
                connection_info=a.connection_info,
                capabilities=a.capabilities,
                status=a.status,
                last_seen=a.last_seen.isoformat() if a.last_seen else None
            )
            for a in agents
        ]
    finally:
        db.close()


@router.get("/api/v1/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """
    获取 Agent 详细信息
    
    - **agent_id**: Agent ID (DID)
    """
    db = SessionLocal()
    try:
        agent_repo = AgentRepository(db)
        agent = agent_repo.get(agent_id)
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return AgentResponse(
            id=agent.id,
            name=agent.name,
            controller=agent.controller,
            personality=agent.personality,
            created_at=agent.created_at.isoformat(),
            active=agent.active,
            agent_type=agent.agent_type,
            connection_info=agent.connection_info,
            capabilities=agent.capabilities,
            status=agent.status,
            last_seen=agent.last_seen.isoformat() if agent.last_seen else None
        )
    finally:
        db.close()


@router.post("/api/v1/agents/{agent_id}/memories", response_model=MemoryResponse)
async def create_memory(agent_id: str, data: MemoryCreate):
    """
    为 Agent 创建记忆
    
    - **agent_id**: Agent ID
    - **content**: 记忆内容
    - **memory_type**: 记忆类型 (short_term, long_term, semantic)
    """
    # 验证 Agent 是否存在
    db = SessionLocal()
    try:
        agent_repo = AgentRepository(db)
        agent = agent_repo.get(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # 创建记忆
        memory_repo = MemoryRepository(db)
        memory = memory_repo.create(
            agent_id=agent_id,
            content=data.content,
            memory_type=data.memory_type,
            meta={}
        )
        
        return MemoryResponse(
            id=memory.id,
            agent_id=memory.agent_id,
            content=memory.content,
            memory_type=memory.memory_type,
            created_at=memory.created_at.isoformat()
        )
    finally:
        db.close()


@router.get("/api/v1/agents/{agent_id}/memories", response_model=List[MemoryResponse])
async def get_memories(agent_id: str, limit: int = 100, memory_type: str = None):
    """
    获取 Agent 的记忆列表
    
    - **agent_id**: Agent ID
    - **limit**: 返回数量限制
    - **memory_type**: 过滤记忆类型 (short_term, long_term, semantic)
    """
    db = SessionLocal()
    try:
        # 验证 Agent 是否存在
        agent_repo = AgentRepository(db)
        agent = agent_repo.get(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # 获取记忆
        memory_repo = MemoryRepository(db)
        if memory_type:
            memories = memory_repo.get_by_agent_and_type(agent_id, memory_type, limit=limit)
        else:
            memories = memory_repo.get_by_agent(agent_id, limit=limit)
        
        return [
            MemoryResponse(
                id=m.id,
                agent_id=m.agent_id,
                content=m.content,
                memory_type=m.memory_type,
                created_at=m.created_at.isoformat()
            )
            for m in memories
        ]
    finally:
        db.close()


@router.get("/api/v1/agents/{agent_id}/memories/search")
async def search_memories(agent_id: str, q: str, limit: int = 20):
    """
    搜索 Agent 的记忆
    
    - **agent_id**: Agent ID
    - **q**: 搜索关键词
    - **limit**: 返回数量限制
    """
    db = SessionLocal()
    try:
        agent_repo = AgentRepository(db)
        agent = agent_repo.get(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        memory_repo = MemoryRepository(db)
        memories = memory_repo.search(agent_id, q, limit=limit)
        
        return [
            MemoryResponse(
                id=m.id,
                agent_id=m.agent_id,
                content=m.content,
                memory_type=m.memory_type,
                created_at=m.created_at.isoformat()
            )
            for m in memories
        ]
    finally:
        db.close()


@router.delete("/api/v1/agents/{agent_id}/memories/{memory_id}")
async def delete_memory(agent_id: str, memory_id: str):
    """
    删除指定记忆
    
    - **agent_id**: Agent ID
    - **memory_id**: 记忆 ID
    """
    db = SessionLocal()
    try:
        agent_repo = AgentRepository(db)
        agent = agent_repo.get(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        memory_repo = MemoryRepository(db)
        success = memory_repo.delete(memory_id, agent_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return {"message": "Memory deleted", "id": memory_id}
    finally:
        db.close()


@router.post("/api/v1/agents/{agent_id}/test-connection")
async def test_connection(agent_id: str):
    """
    测试外部 Agent 连接
    
    - **agent_id**: Agent ID
    """
    import httpx
    
    db = SessionLocal()
    try:
        agent_repo = AgentRepository(db)
        agent = agent_repo.get(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # 如果是原生 Agent，直接返回成功
        if agent.agent_type == "native":
            return {
                "success": True,
                "message": "原生 Agent，无需连接测试",
                "agent_type": "native"
            }
        
        # 测试外部连接
        connection = agent.connection_info or {}
        endpoint = connection.get("endpoint")
        auth_type = connection.get("auth_type", "none")
        auth_value = connection.get("auth")
        
        if not endpoint:
            return {
                "success": False,
                "message": "未配置连接端点",
                "agent_type": "external"
            }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {}
                if auth_type == "bearer" and auth_value:
                    headers["Authorization"] = f"Bearer {auth_value}"
                elif auth_type == "basic" and auth_value:
                    headers["Authorization"] = f"Basic {auth_value}"
                
                response = await client.get(endpoint, headers=headers)
                
                if response.status_code < 400:
                    # 更新状态
                    from datetime import datetime
                    agent_repo.update(agent_id, status="online", last_seen=datetime.utcnow())
                    
                    return {
                        "success": True,
                        "message": "连接成功",
                        "status_code": response.status_code,
                        "agent_type": "external"
                    }
                else:
                    agent_repo.update(agent_id, status="error")
                    return {
                        "success": False,
                        "message": f"连接失败：HTTP {response.status_code}",
                        "agent_type": "external"
                    }
        except Exception as e:
            agent_repo.update(agent_id, status="error")
            return {
                "success": False,
                "message": f"连接错误：{str(e)}",
                "agent_type": "external"
            }
    finally:
        db.close()


@router.post("/api/v1/agents/{agent_id}/invoke")
async def invoke_agent(agent_id: str, action: str, input_data: dict = None, timeout: int = 30):
    """
    调用外部 Agent
    
    - **agent_id**: Agent ID
    - **action**: 动作 (chat, query, execute 等)
    - **input_data**: 输入数据
    - **timeout**: 超时时间 (秒)
    """
    from src.core.adapters import get_adapter
    from src.core.invocation_log import create_log
    from urllib.parse import urlparse
    
    db = SessionLocal()
    try:
        agent_repo = AgentRepository(db)
        agent = agent_repo.get(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # 原生 Agent 暂不支持
        if agent.agent_type == "native":
            raise HTTPException(
                status_code=400,
                detail="原生 Agent 需要通过其他方式调用"
            )
        
        # 获取连接配置
        connection = agent.connection_info or {}
        endpoint = connection.get("endpoint")
        
        if not endpoint:
            raise HTTPException(status_code=400, detail="未配置连接端点")
        
        # 解析协议
        parsed = urlparse(endpoint)
        protocol = parsed.scheme or "http"
        
        # 获取适配器
        adapter = get_adapter(protocol)
        
        # 构建认证信息
        auth = None
        auth_type = connection.get("auth_type")
        auth_value = connection.get("auth")
        
        if auth_type and auth_value:
            auth = {
                "type": auth_type,
                "value": auth_value
            }
        
        # 调用 Agent
        result = await adapter.invoke(
            endpoint=endpoint,
            action=action,
            input_data=input_data or {},
            auth=auth
        )
        
        # 记录日志
        create_log(agent_id, action, input_data or {}, result)
        
        # 更新状态
        if result.get("success"):
            from datetime import datetime
            agent_repo.update(
                agent_id,
                status="online",
                last_seen=datetime.utcnow()
            )
        else:
            agent_repo.update(agent_id, status="error")
        
        return {
            "agent_id": agent_id,
            "action": action,
            "result": result
        }
        
    finally:
        db.close()


@router.get("/api/v1/agents/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """
    获取 Agent 状态
    
    - **agent_id**: Agent ID
    """
    db = SessionLocal()
    try:
        agent_repo = AgentRepository(db)
        agent = agent_repo.get(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {
            "agent_id": agent_id,
            "name": agent.name,
            "agent_type": agent.agent_type,
            "status": agent.status,
            "active": agent.active,
            "last_seen": agent.last_seen.isoformat() if agent.last_seen else None
        }
    finally:
        db.close()


@router.post("/api/v1/agents/heartbeat/check")
async def check_all_heartbeats():
    """
    手动触发所有 Agent 心跳检测
    
    立即检查所有外部 Agent 的连接状态
    """
    from src.core.heartbeat import HeartbeatService
    import asyncio
    
    db = SessionLocal()
    try:
        service = HeartbeatService(db)
        results = await service.check_all_agents()
        
        return {
            "success": True,
            "checked": len(results),
            "results": results
        }
    finally:
        db.close()


@router.get("/api/v1/agents/heartbeat/stats")
async def get_heartbeat_stats():
    """
    获取心跳统计信息
    
    返回所有 Agent 的状态统计
    """
    db = SessionLocal()
    try:
        from sqlalchemy import func
        
        # 统计各状态数量
        status_counts = db.query(
            AgentModel.status,
            func.count(AgentModel.id).label('count')
        ).filter(
            AgentModel.active == True
        ).group_by(AgentModel.status).all()
        
        # 统计类型分布
        type_counts = db.query(
            AgentModel.agent_type,
            func.count(AgentModel.id).label('count')
        ).filter(
            AgentModel.active == True
        ).group_by(AgentModel.agent_type).all()
        
        # 最近 24 小时更新的数量
        from datetime import datetime, timedelta
        day_ago = datetime.utcnow() - timedelta(days=1)
        recent_active = db.query(AgentModel).filter(
            AgentModel.active == True,
            AgentModel.last_seen >= day_ago
        ).count()
        
        return {
            "total_active": db.query(AgentModel).filter(AgentModel.active == True).count(),
            "by_status": {r.status: r.count for r in status_counts},
            "by_type": {r.agent_type: r.count for r in type_counts},
            "recent_24h": recent_active
        }
    finally:
        db.close()


@router.post("/api/v1/agents/{agent_id}/heartbeat")
async def trigger_single_heartbeat(agent_id: str):
    """
    触发单个 Agent 的心跳检测
    
    - **agent_id**: Agent ID
    """
    from src.core.heartbeat import HeartbeatService
    
    db = SessionLocal()
    try:
        agent_repo = AgentRepository(db)
        agent = agent_repo.get(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        service = HeartbeatService(db)
        result = await service.check_agent(agent)
        
        # 更新状态
        if result["success"]:
            from datetime import datetime
            agent_repo.update(
                agent_id,
                status=result["status"],
                last_seen=datetime.utcnow()
            )
        else:
            agent_repo.update(agent_id, status=result["status"])
        
        return result
    finally:
        db.close()


@router.get("/api/v1/agents/{agent_id}/invocations")
async def get_invocation_logs(agent_id: str, limit: int = 50, offset: int = 0):
    """
    获取 Agent 调用日志
    
    - **agent_id**: Agent ID
    - **limit**: 返回数量
    - **offset**: 偏移量
    """
    from src.core.invocation_log import get_logs
    
    db = SessionLocal()
    try:
        agent_repo = AgentRepository(db)
        agent = agent_repo.get(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        logs = get_logs(agent_id, limit, offset)
        
        return {
            "agent_id": agent_id,
            "count": len(logs),
            "logs": [
                {
                    "id": log.id,
                    "action": log.action,
                    "success": log.success == 1,
                    "duration": log.duration,
                    "status_code": log.status_code,
                    "created_at": log.created_at.isoformat()
                }
                for log in logs
            ]
        }
    finally:
        db.close()


@router.get("/api/v1/agents/{agent_id}/invocations/stats")
async def get_invocation_stats(agent_id: str, hours: int = 24):
    """
    获取 Agent 调用统计
    
    - **agent_id**: Agent ID
    - **hours**: 统计时长 (小时)
    """
    from src.core.invocation_log import get_stats
    
    db = SessionLocal()
    try:
        agent_repo = AgentRepository(db)
        agent = agent_repo.get(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        stats = get_stats(agent_id, hours)
        
        return stats
    finally:
        db.close()


@router.delete("/api/v1/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """
    删除 Agent
    
    - **agent_id**: Agent ID
    """
    db = SessionLocal()
    try:
        agent_repo = AgentRepository(db)
        success = agent_repo.delete(agent_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {"message": "Agent deleted successfully", "id": agent_id}
    finally:
        db.close()


@router.get("/api/v1/agents/{agent_id}/stats")
async def get_agent_stats(agent_id: str):
    """
    获取 Agent 统计信息
    
    - **agent_id**: Agent ID
    """
    db = SessionLocal()
    try:
        agent_repo = AgentRepository(db)
        agent = agent_repo.get(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        memory_repo = MemoryRepository(db)
        memory_stats = memory_repo.count_by_type(agent_id)
        
        return {
            "agent_id": agent_id,
            "name": agent.name,
            "created_at": agent.created_at.isoformat(),
            "memories": {
                "total": sum(memory_stats.values()),
                "by_type": memory_stats
            },
            "active": agent.active
        }
    finally:
        db.close()


@router.put("/api/v1/agents/{agent_id}")
async def update_agent(agent_id: str, data: AgentUpdate):
    """
    更新 Agent 信息
    
    - **agent_id**: Agent ID
    - **name**: 新名字 (可选)
    - **personality**: 新人格配置 (可选)
    - **active**: 激活状态 (可选)
    - **connection_info**: 连接配置 (可选)
    - **capabilities**: 能力列表 (可选)
    - **status**: 状态 (可选)
    """
    db = SessionLocal()
    try:
        agent_repo = AgentRepository(db)
        agent = agent_repo.get(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        updates = {}
        if data.name is not None:
            updates["name"] = data.name
        if data.personality is not None:
            updates["personality"] = data.personality
        if data.active is not None:
            updates["active"] = data.active
        if data.connection_info is not None:
            updates["connection_info"] = data.connection_info
        if data.capabilities is not None:
            updates["capabilities"] = data.capabilities
        if data.status is not None:
            updates["status"] = data.status
        
        if updates:
            agent_repo.update(agent_id, **updates)
            agent = agent_repo.get(agent_id)
        
        return AgentResponse(
            id=agent.id,
            name=agent.name,
            controller=agent.controller,
            personality=agent.personality,
            created_at=agent.created_at.isoformat(),
            active=agent.active,
            agent_type=agent.agent_type,
            connection_info=agent.connection_info,
            capabilities=agent.capabilities,
            status=agent.status,
            last_seen=agent.last_seen.isoformat() if agent.last_seen else None
        )
    finally:
        db.close()
