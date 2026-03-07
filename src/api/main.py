"""
硅基世界 API

FastAPI 主应用
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.blockchain.did import DIDManager


# 创建 FastAPI 应用
app = FastAPI(
    title="硅基世界 API",
    description="Agent 与人类的虚拟世界 - RESTful API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化 DID 管理器
did_manager = DIDManager()


# 数据模型
class DIDCreate(BaseModel):
    """创建 DID 请求"""
    controller: str
    public_key: Optional[str] = None


class DIDResponse(BaseModel):
    """DID 响应"""
    did: str
    controller: str
    created: str
    updated: str
    active: bool


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str


# API 路由
@app.get("/", response_model=HealthResponse)
async def root():
    """根路径 - 健康检查"""
    return {
        "status": "ok",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "silicon-world-api"
    }


@app.post("/api/v1/did", response_model=DIDResponse, tags=["DID"])
async def create_did(data: DIDCreate):
    """
    创建新的 DID
    
    - **controller**: 控制者地址
    - **public_key**: 公钥 (可选)
    """
    # 生成 DID
    did = did_manager.generate_did(data.controller)
    
    # 创建 DID 文档
    doc = did_manager.create_document(
        did=did,
        controller=data.controller,
        public_key=data.public_key
    )
    
    # TODO: 保存到数据库
    # TODO: 部署到区块链
    
    return {
        "did": doc.id,
        "controller": doc.controller,
        "created": doc.created,
        "updated": doc.updated,
        "active": True
    }


@app.get("/api/v1/did/{did}", response_model=DIDResponse, tags=["DID"])
async def get_did(did: str):
    """
    查询 DID 信息
    
    - **did**: DID 字符串
    """
    # 验证 DID 格式
    if not did_manager.verify_did(did):
        raise HTTPException(status_code=400, detail="Invalid DID format")
    
    # TODO: 从数据库查询
    # TODO: 从区块链查询
    
    # 临时返回示例数据
    return {
        "did": did,
        "controller": "0x1234567890abcdef",
        "created": "2026-03-07T00:00:00Z",
        "updated": "2026-03-07T00:00:00Z",
        "active": True
    }


@app.post("/api/v1/did/{did}/verify", tags=["DID"])
async def verify_did(did: str):
    """
    验证 DID
    
    - **did**: DID 字符串
    """
    is_valid = did_manager.verify_did(did)
    
    return {
        "valid": is_valid,
        "did": did
    }


@app.get("/api/v1/agents", tags=["Agent"])
async def list_agents(limit: int = 10, offset: int = 0):
    """
    获取 Agent 列表
    
    - **limit**: 返回数量限制
    - **offset**: 偏移量
    """
    # TODO: 从数据库查询
    return {
        "total": 0,
        "limit": limit,
        "offset": offset,
        "agents": []
    }


@app.get("/api/v1/agents/{agent_id}", tags=["Agent"])
async def get_agent(agent_id: str):
    """
    获取 Agent 信息
    
    - **agent_id**: Agent ID (DID)
    """
    # TODO: 从数据库查询
    raise HTTPException(status_code=404, detail="Agent not found")


# 启动信息
if __name__ == "__main__":
    import uvicorn
    
    print("=" * 50)
    print("硅基世界 API")
    print("=" * 50)
    print("文档：http://localhost:8000/docs")
    print("Redoc: http://localhost:8000/redoc")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
