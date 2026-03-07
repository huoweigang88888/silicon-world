"""
身份管理 API 路由
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.blockchain.did import DIDManager

router = APIRouter(prefix="/api/v1/identity", tags=["Identity"])

did_manager = DIDManager()


class IdentityCreate(BaseModel):
    """创建身份请求"""
    controller: str
    public_key: Optional[str] = None


class IdentityResponse(BaseModel):
    """身份响应"""
    did: str
    controller: str
    public_key: Optional[str]
    created_at: str
    updated_at: str
    active: bool


@router.post("/", response_model=IdentityResponse)
async def create_identity(data: IdentityCreate):
    """
    创建新的去中心化身份
    
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
        "public_key": data.public_key,
        "created_at": doc.created,
        "updated_at": doc.updated,
        "active": True
    }


@router.get("/{did}", response_model=IdentityResponse)
async def get_identity(did: str):
    """
    查询身份信息
    
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
        "public_key": None,
        "created_at": "2026-03-07T00:00:00Z",
        "updated_at": "2026-03-07T00:00:00Z",
        "active": True
    }


@router.post("/{did}/verify")
async def verify_identity(did: str):
    """
    验证身份
    
    - **did**: DID 字符串
    """
    is_valid = did_manager.verify_did(did)
    
    return {
        "valid": is_valid,
        "did": did
    }


@router.get("/controller/{controller}")
async def get_controller_identities(
    controller: str,
    limit: int = 10,
    offset: int = 0
):
    """
    获取控制者的所有身份
    
    - **controller**: 控制者地址
    - **limit**: 返回数量限制
    - **offset**: 偏移量
    """
    # TODO: 从数据库查询
    
    return {
        "total": 0,
        "limit": limit,
        "offset": offset,
        "identities": []
    }
