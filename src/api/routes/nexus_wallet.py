"""
NexusA 钱包 API 路由

提供钱包管理和支付相关的 REST API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.a2a.nexus_wallet import NexusAWalletClient, wallet_client

router = APIRouter(tags=["NexusA Wallet"])

# 初始化钱包客户端
nexus_client = wallet_client


# ==================== 请求/响应模型 ====================

class CreateWalletRequest(BaseModel):
    """创建钱包请求"""
    currency: Optional[str] = "CNY"
    network: Optional[str] = "mainnet"


class WalletResponse(BaseModel):
    """钱包响应"""
    address: str
    balance: float
    currency: str
    network: str
    created_at: str


class TransferRequest(BaseModel):
    """转账请求"""
    from_address: str
    to_address: str
    amount: float
    currency: Optional[str] = "CNY"
    description: Optional[str] = None


class TransferResponse(BaseModel):
    """转账响应"""
    tx_id: str
    from_address: str
    to_address: str
    amount: float
    currency: str
    status: str
    tx_hash: Optional[str]
    created_at: str


class TransactionResponse(BaseModel):
    """交易响应"""
    id: str
    from_address: str
    to_address: str
    amount: float
    currency: str
    status: str
    tx_hash: Optional[str]
    created_at: str
    description: Optional[str]


class VerifyPaymentRequest(BaseModel):
    """验证支付请求"""
    tx_hash: str
    expected_amount: float


# ==================== 钱包管理 API ====================

@router.post("/api/v1/nexus/wallet/create", response_model=WalletResponse)
async def create_wallet(request: CreateWalletRequest):
    """
    创建 NexusA 钱包
    
    - **currency**: 货币类型 (CNY/USD/BTC 等)
    - **network**: 网络类型 (mainnet/testnet)
    """
    try:
        # 确保已连接
        if not nexus_client.connected:
            await nexus_client.connect()
        
        wallet = await nexus_client.create_wallet(
            currency=request.currency,
            network=request.network
        )
        
        return WalletResponse(
            address=wallet.address,
            balance=wallet.balance,
            currency=wallet.currency,
            network=wallet.network,
            created_at=wallet.created_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建钱包失败：{str(e)}")


@router.get("/api/v1/nexus/wallet/{address}", response_model=WalletResponse)
async def get_wallet(address: str):
    """
    获取钱包信息
    
    - **address**: 钱包地址
    """
    try:
        if not nexus_client.connected:
            await nexus_client.connect()
        
        wallet = await nexus_client.get_wallet(address)
        
        if not wallet:
            raise HTTPException(status_code=404, detail="钱包不存在")
        
        return WalletResponse(
            address=wallet.address,
            balance=wallet.balance,
            currency=wallet.currency,
            network=wallet.network,
            created_at=wallet.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取钱包失败：{str(e)}")


@router.get("/api/v1/nexus/wallet/{address}/balance")
async def get_balance(address: str):
    """
    获取钱包余额
    
    - **address**: 钱包地址
    """
    try:
        if not nexus_client.connected:
            await nexus_client.connect()
        
        balance = await nexus_client.get_balance(address)
        
        return {
            "address": address,
            "balance": balance,
            "currency": "CNY"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取余额失败：{str(e)}")


@router.get("/api/v1/nexus/wallet/{address}/transactions")
async def get_transactions(
    address: str,
    limit: int = 50,
    offset: int = 0
):
    """
    获取交易历史
    
    - **address**: 钱包地址
    - **limit**: 返回数量
    - **offset**: 偏移量
    """
    try:
        if not nexus_client.connected:
            await nexus_client.connect()
        
        transactions = await nexus_client.get_transactions(address, limit)
        
        return {
            "count": len(transactions),
            "transactions": [
                {
                    "id": tx.id,
                    "from_address": tx.from_address,
                    "to_address": tx.to_address,
                    "amount": tx.amount,
                    "currency": tx.currency,
                    "status": tx.status,
                    "tx_hash": tx.tx_hash,
                    "created_at": tx.created_at,
                    "description": tx.description
                }
                for tx in transactions[offset:offset+limit]
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取交易历史失败：{str(e)}")


# ==================== 转账 API ====================

@router.post("/api/v1/nexus/transfer", response_model=TransferResponse)
async def transfer(request: TransferRequest):
    """
    转账
    
    - **from_address**: 发送方地址
    - **to_address**: 接收方地址
    - **amount**: 金额
    - **currency**: 货币类型
    - **description**: 描述
    """
    try:
        if not nexus_client.connected:
            await nexus_client.connect()
        
        transaction = await nexus_client.transfer(
            from_address=request.from_address,
            to_address=request.to_address,
            amount=request.amount,
            currency=request.currency,
            description=request.description
        )
        
        return TransferResponse(
            tx_id=transaction.id,
            from_address=transaction.from_address,
            to_address=transaction.to_address,
            amount=transaction.amount,
            currency=transaction.currency,
            status=transaction.status,
            tx_hash=transaction.tx_hash,
            created_at=transaction.created_at
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转账失败：{str(e)}")


@router.get("/api/v1/nexus/transaction/{tx_id}")
async def get_transaction(tx_id: str):
    """
    获取交易详情
    
    - **tx_id**: 交易 ID
    """
    try:
        if not nexus_client.connected:
            await nexus_client.connect()
        
        transaction = await nexus_client.get_transaction(tx_id)
        
        if not transaction:
            raise HTTPException(status_code=404, detail="交易不存在")
        
        return {
            "id": transaction.id,
            "from_address": transaction.from_address,
            "to_address": transaction.to_address,
            "amount": transaction.amount,
            "currency": transaction.currency,
            "status": transaction.status,
            "tx_hash": transaction.tx_hash,
            "created_at": transaction.created_at,
            "confirmed_at": transaction.confirmed_at,
            "description": transaction.description
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取交易失败：{str(e)}")


# ==================== 支付验证 API ====================

@router.post("/api/v1/nexus/payment/verify")
async def verify_payment(request: VerifyPaymentRequest):
    """
    验证支付
    
    - **tx_hash**: 交易哈希
    - **expected_amount**: 预期金额
    """
    try:
        if not nexus_client.connected:
            await nexus_client.connect()
        
        is_valid = await nexus_client.verify_transaction(
            tx_hash=request.tx_hash,
            expected_amount=request.expected_amount
        )
        
        return {
            "valid": is_valid,
            "tx_hash": request.tx_hash,
            "expected_amount": request.expected_amount
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"验证失败：{str(e)}")


# ==================== 统计 API ====================

@router.get("/api/v1/nexus/stats")
async def get_nexus_stats():
    """获取 NexusA 钱包统计"""
    try:
        stats = nexus_client.get_stats()
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计失败：{str(e)}")


@router.get("/api/v1/nexus/status")
async def get_nexus_status():
    """获取 NexusA 连接状态"""
    return {
        "connected": nexus_client.connected,
        "api_endpoint": nexus_client.api_endpoint,
        "service": "nexus-wallet"
    }
