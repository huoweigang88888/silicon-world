"""
x402 支付扩展模块

基于 A2A x402 协议，实现 Agent 之间的支付功能
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import asyncio


@dataclass
class PaymentRequest:
    """支付请求"""
    id: str
    amount: float
    currency: str
    description: str
    payment_url: str
    expires_at: str
    status: str = "pending"


@dataclass
class PaymentProof:
    """支付证明"""
    payment_id: str
    transaction_hash: str
    amount: float
    currency: str
    timestamp: str
    signature: str


class SiliconWorldPayment:
    """硅基世界支付处理器"""
    
    def __init__(self, wallet_address: str = None):
        """
        初始化支付处理器
        
        Args:
            wallet_address: 收款钱包地址
        """
        self.wallet_address = wallet_address
        self.payment_requests: Dict[str, PaymentRequest] = {}
    
    async def create_payment_request(
        self,
        amount: float,
        currency: str = "CNY",
        description: str = "Agent service payment",
        expiry_hours: int = 1
    ) -> PaymentRequest:
        """
        创建支付请求
        
        Args:
            amount: 金额
            currency: 货币类型 (CNY/USD/BTC 等)
            description: 支付描述
            expiry_hours: 过期时间（小时）
            
        Returns:
            PaymentRequest 对象
        """
        from datetime import timedelta
        
        payment_id = str(uuid.uuid4())
        expires_at = (datetime.utcnow() + timedelta(hours=expiry_hours)).isoformat()
        
        # TODO: 集成真实的支付网关（如 NexusA 钱包）
        # 这里生成模拟的支付 URL
        payment_url = f"/api/v1/a2a/payment/{payment_id}/pay"
        
        payment_request = PaymentRequest(
            id=payment_id,
            amount=amount,
            currency=currency,
            description=description,
            payment_url=payment_url,
            expires_at=expires_at,
            status="pending"
        )
        
        # 保存支付请求
        self.payment_requests[payment_id] = payment_request
        
        print(f"[x402] 创建支付请求：{payment_id}, 金额：{amount} {currency}")
        return payment_request
    
    async def verify_payment(self, payment_proof: PaymentProof) -> bool:
        """
        验证支付
        
        Args:
            payment_proof: 支付证明
            
        Returns:
            是否验证成功
        """
        # TODO: 实现真实的支付验证逻辑
        # 这里模拟验证
        print(f"[x402] 验证支付：{payment_proof.payment_id}")
        print(f"  交易哈希：{payment_proof.transaction_hash}")
        print(f"  金额：{payment_proof.amount} {payment_proof.currency}")
        
        # 模拟验证通过
        return True
    
    def get_payment_request(self, payment_id: str) -> Optional[PaymentRequest]:
        """获取支付请求"""
        return self.payment_requests.get(payment_id)
    
    def update_payment_status(self, payment_id: str, status: str):
        """
        更新支付状态
        
        Args:
            payment_id: 支付 ID
            status: 新状态 (pending/paid/failed/expired)
        """
        payment = self.payment_requests.get(payment_id)
        if payment:
            payment.status = status
            print(f"[x402] 支付状态更新：{payment_id} -> {status}")


# ==================== A2A x402 中间件 ====================

class A2AX402Middleware:
    """
    A2A x402 支付中间件
    
    自动处理需要付费的请求
    """
    
    def __init__(self, payment_processor: SiliconWorldPayment, required_payment: float = 0.0):
        """
        初始化中间件
        
        Args:
            payment_processor: 支付处理器
            required_payment: 需要的支付金额
        """
        self.payment_processor = payment_processor
        self.required_payment = required_payment
    
    async def __call__(self, request: Dict[str, Any], call_next):
        """
        处理请求
        
        Args:
            request: 请求数据
            call_next: 下一个处理函数
            
        Returns:
            响应
        """
        # 检查是否有支付证明
        payment_proof = request.get("payment_proof")
        
        if self.required_payment > 0 and not payment_proof:
            # 需要付费但没有支付证明
            # 返回 402 Payment Required
            payment_request = await self.payment_processor.create_payment_request(
                amount=self.required_payment,
                description="Agent service payment"
            )
            
            return {
                "error": "Payment Required",
                "status_code": 402,
                "payment_request": {
                    "id": payment_request.id,
                    "amount": payment_request.amount,
                    "currency": payment_request.currency,
                    "payment_url": payment_request.payment_url
                }
            }
        
        # 有支付证明，验证
        if payment_proof:
            is_valid = await self.payment_processor.verify_payment(payment_proof)
            if not is_valid:
                return {
                    "error": "Payment verification failed",
                    "status_code": 402
                }
        
        # 继续处理请求
        return await call_next(request)


# ==================== 支付证明验证 ====================

class PaymentVerifier:
    """
    支付验证器
    
    支持多种支付方式验证
    """
    
    def __init__(self):
        """初始化验证器"""
        self.verified_payments: Dict[str, PaymentProof] = {}
    
    async def verify_crypto_payment(
        self,
        transaction_hash: str,
        expected_amount: float,
        currency: str = "CNY"
    ) -> bool:
        """
        验证加密货币支付
        
        Args:
            transaction_hash: 交易哈希
            expected_amount: 预期金额
            currency: 货币类型
            
        Returns:
            是否验证成功
        """
        # TODO: 集成真实的区块链节点验证
        # 这里模拟验证
        
        print(f"[PaymentVerifier] 验证加密货币支付:")
        print(f"  交易哈希：{transaction_hash}")
        print(f"  预期金额：{expected_amount} {currency}")
        
        # 模拟验证延迟
        await asyncio.sleep(0.5)
        
        # 模拟验证通过（实际应该查询区块链）
        is_valid = len(transaction_hash) > 10  # 简单验证
        
        if is_valid:
            print(f"  验证结果：成功")
        else:
            print(f"  验证结果：失败")
        
        return is_valid
    
    async def verify_offchain_payment(
        self,
        payment_id: str,
        signature: str
    ) -> bool:
        """
        验证链下支付
        
        Args:
            payment_id: 支付 ID
            signature: 签名
            
        Returns:
            是否验证成功
        """
        # TODO: 集成支付宝/微信支付等
        print(f"[PaymentVerifier] 验证链下支付：{payment_id}")
        
        # 模拟验证
        await asyncio.sleep(0.3)
        
        return len(signature) > 20
    
    def record_payment(self, proof: PaymentProof):
        """
        记录已验证的支付
        
        Args:
            proof: 支付证明
        """
        self.verified_payments[proof.payment_id] = proof
        print(f"[PaymentVerifier] 记录支付：{proof.payment_id}")
    
    def is_payment_verified(self, payment_id: str) -> bool:
        """
        检查支付是否已验证
        
        Args:
            payment_id: 支付 ID
            
        Returns:
            是否已验证
        """
        return payment_id in self.verified_payments


# 全局支付验证器实例
payment_verifier = PaymentVerifier()
