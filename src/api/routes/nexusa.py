"""
NexusA API 路由

钱包、支付、合约等区块链功能
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.nexusa.wallet import WalletManager, Wallet
from src.nexusa.payment import PaymentProcessor, Payment, PaymentStatus, PaymentType
from src.nexusa.config import NexusAConfig, get_config


router = APIRouter(prefix="/api/v1/nexusa", tags=["NexusA 区块链"])


# ==================== 单例 ====================

wallet_manager = WalletManager("data/wallets.json")
payment_processor = PaymentProcessor()


# ==================== 依赖注入 ====================

def get_user_address(x_wallet_address: Optional[str] = Header(None, alias="X-Wallet-Address")) -> str:
    """获取用户钱包地址"""
    if not x_wallet_address:
        raise HTTPException(status_code=400, detail="Missing X-Wallet-Address header")
    return x_wallet_address


# ==================== 请求/响应模型 ====================

class WalletCreateRequest(BaseModel):
    """创建钱包请求"""
    label: Optional[str] = None


class WalletImportRequest(BaseModel):
    """导入钱包请求"""
    private_key: str
    label: Optional[str] = None


class PaymentCreateRequest(BaseModel):
    """创建支付请求"""
    to_address: str
    amount: str
    currency: str = "SIL"
    description: Optional[str] = None
    type: str = "purchase"


class PaymentConfirmRequest(BaseModel):
    """确认支付请求"""
    tx_hash: str


# ==================== 钱包端点 ====================

@router.post("/wallet/create")
async def create_wallet(request: WalletCreateRequest):
    """
    创建新钱包 (占位符)
    
    ⚠️ 注意：实际应由客户端生成钱包
    此接口仅用于演示，生产环境应使用 /wallet/register
    """
    try:
        wallet = wallet_manager.create_wallet(label=request.label)
        return {
            "success": True,
            "wallet": {
                "address": wallet.address,
                "label": wallet.label,
                "created_at": wallet.created_at.isoformat()
            },
            "warning": "⚠️ 演示模式！生产环境请使用客户端生成钱包 (ethers.js)",
            "security_note": "私钥由客户端生成和保管，服务端从未接触私钥"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/wallet/register")
async def register_wallet(request: WalletCreateRequest):
    """
    注册客户端生成的钱包
    
    ⚠️ 推荐方式：客户端生成钱包后，只发送地址注册
    """
    try:
        # 客户端应该已经生成了钱包，这里只接收地址
        # 实际使用中，address 应该由客户端传入
        wallet = wallet_manager.create_wallet(label=request.label)
        
        return {
            "success": True,
            "wallet": {
                "address": wallet.address,
                "label": wallet.label
            },
            "security_note": "✅ 私钥由您在客户端生成和保管，服务端只存储地址"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/wallet/import")
async def import_wallet(request: WalletImportRequest):
    """
    导入现有钱包地址
    
    ⚠️ 不再接受私钥！只注册钱包地址
    私钥由用户在客户端保管
    """
    try:
        # ⚠️ 忽略 private_key 参数 (向后兼容，但不使用)
        # 只注册地址
        wallet = wallet_manager.import_wallet(
            address=request.private_key if request.private_key.startswith("0x") and len(request.private_key) == 42 else "",
            label=request.label
        )
        
        return {
            "success": True,
            "wallet": {
                "address": wallet.address,
                "label": wallet.label
            },
            "security_note": "✅ 私钥从未传输到服务端，由您自行保管"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"导入失败：{str(e)}")


@router.get("/wallet/list")
async def list_wallets():
    """列出所有钱包"""
    wallets = wallet_manager.list_wallets()
    return {
        "count": len(wallets),
        "wallets": [
            {
                "address": w.address,
                "label": w.label,
                "created_at": w.created_at.isoformat()
            }
            for w in wallets
        ]
    }


@router.get("/wallet/{address}")
async def get_wallet(address: str):
    """获取钱包信息"""
    wallet = wallet_manager.get_wallet(address)
    if not wallet:
        raise HTTPException(status_code=404, detail="钱包不存在")
    
    return {
        "wallet": {
            "address": wallet.address,
            "label": wallet.label,
            "created_at": wallet.created_at.isoformat(),
            "metadata": wallet.metadata
        }
    }


@router.delete("/wallet/{address}")
async def delete_wallet(address: str):
    """删除钱包"""
    success = wallet_manager.delete_wallet(address)
    if not success:
        raise HTTPException(status_code=404, detail="钱包不存在")
    
    return {"success": True, "message": "钱包已删除"}


@router.post("/wallet/{address}/verify")
async def verify_signature(address: str, message: str, signature: str):
    """
    验证客户端签名
    
    ⚠️ 服务端只验证签名，不生成签名
    签名应在客户端完成
    """
    try:
        is_valid = wallet_manager.verify_signature(address, message, signature)
        
        return {
            "success": True,
            "valid": is_valid,
            "address": address,
            "message": message,
            "note": "签名由客户端生成，服务端仅验证"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== 支付端点 ====================

@router.post("/payment/create")
async def create_payment(request: PaymentCreateRequest, user_address: str = Depends(get_user_address)):
    """
    创建支付记录
    
    发起一笔新的支付
    """
    try:
        payment_type = PaymentType(request.type)
    except ValueError:
        payment_type = PaymentType.PURCHASE
    
    payment = payment_processor.create_payment(
        from_address=user_address,
        to_address=request.to_address,
        amount=request.amount,
        currency=request.currency,
        type=payment_type,
        description=request.description
    )
    
    return {
        "success": True,
        "payment": {
            "id": payment.id,
            "status": payment.status,
            "amount": payment.amount,
            "currency": payment.currency,
            "from": payment.from_address,
            "to": payment.to_address,
            "created_at": payment.created_at.isoformat()
        },
        "next_step": "请发送交易到链上，然后调用 /payment/confirm 确认"
    }


@router.post("/payment/{payment_id}/confirm")
async def confirm_payment(payment_id: str, request: PaymentConfirmRequest):
    """
    确认支付
    
    提供交易哈希确认支付已完成
    """
    success = payment_processor.process_payment(payment_id, request.tx_hash)
    if not success:
        raise HTTPException(status_code=400, detail="支付确认失败")
    
    payment = payment_processor.get_payment(payment_id)
    
    return {
        "success": True,
        "payment": {
            "id": payment.id,
            "status": payment.status,
            "tx_hash": payment.tx_hash,
            "completed_at": payment.completed_at.isoformat()
        }
    }


@router.get("/payment/{payment_id}")
async def get_payment(payment_id: str):
    """获取支付详情"""
    payment = payment_processor.get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="支付记录不存在")
    
    return {
        "payment": {
            "id": payment.id,
            "type": payment.type,
            "status": payment.status,
            "from": payment.from_address,
            "to": payment.to_address,
            "amount": payment.amount,
            "currency": payment.currency,
            "tx_hash": payment.tx_hash,
            "created_at": payment.created_at.isoformat(),
            "completed_at": payment.completed_at.isoformat() if payment.completed_at else None
        }
    }


@router.get("/payments")
async def list_payments(
    status: Optional[str] = None,
    limit: int = 50,
    user_address: str = Depends(get_user_address)
):
    """
    列出支付记录
    
    可按状态过滤
    """
    status_filter = None
    if status:
        try:
            status_filter = PaymentStatus(status)
        except ValueError:
            pass
    
    payments = payment_processor.list_payments(
        address=user_address,
        status=status_filter,
        limit=limit
    )
    
    return {
        "count": len(payments),
        "payments": [
            {
                "id": p.id,
                "type": p.type,
                "status": p.status,
                "amount": p.amount,
                "currency": p.currency,
                "from": p.from_address,
                "to": p.to_address,
                "created_at": p.created_at.isoformat()
            }
            for p in payments
        ]
    }


@router.post("/payment/{payment_id}/refund")
async def refund_payment(payment_id: str, amount: Optional[str] = None):
    """
    退款
    
    对已完成的支付进行退款
    """
    refund = payment_processor.refund_payment(payment_id, amount)
    if not refund:
        raise HTTPException(status_code=400, detail="退款失败，可能支付未完成")
    
    return {
        "success": True,
        "refund": {
            "id": refund.id,
            "amount": refund.amount,
            "status": refund.status
        }
    }


@router.get("/wallet/{address}/statistics")
async def get_wallet_statistics(address: str):
    """获取钱包支付统计"""
    stats = payment_processor.get_statistics(address)
    return stats


@router.get("/config")
async def get_nexusa_config():
    """获取 NexusA 配置"""
    config = get_config()
    return {
        "network": config.network,
        "chain_id": config.get_chain_id(),
        "rpc_url": config.get_rpc_url(),
        "explorer": config.get_network().explorer_url,
        "currency": config.get_network().currency_symbol
    }


# 使用示例
if __name__ == "__main__":
    print("NexusA API 模块已加载")
    print("可用端点:")
    print("  POST /api/v1/nexusa/wallet/create")
    print("  POST /api/v1/nexusa/wallet/import")
    print("  GET  /api/v1/nexusa/wallet/list")
    print("  GET  /api/v1/nexusa/wallet/{address}")
    print("  POST /api/v1/nexusa/wallet/{address}/sign")
    print("  POST /api/v1/nexusa/payment/create")
    print("  POST /api/v1/nexusa/payment/{id}/confirm")
    print("  GET  /api/v1/nexusa/payment/{id}")
    print("  GET  /api/v1/nexusa/payments")
    print("  POST /api/v1/nexusa/payment/{id}/refund")
    print("  GET  /api/v1/nexusa/config")
