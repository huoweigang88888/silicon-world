"""
NexusA 支付模块

x402 支付协议、交易处理、支付状态管理
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import uuid
import hashlib


class PaymentStatus(str, Enum):
    """支付状态"""
    PENDING = "pending"  # 待支付
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    REFUNDED = "refunded"  # 已退款
    CANCELLED = "cancelled"  # 已取消


class PaymentType(str, Enum):
    """支付类型"""
    TRANSFER = "transfer"  # 转账
    PURCHASE = "purchase"  # 购买
    REFUND = "refund"  # 退款
    STAKE = "stake"  # 质押
    CLAIM = "claim"  # 领取


class Payment(BaseModel):
    """
    支付记录
    """
    id: str
    type: PaymentType
    status: PaymentStatus = PaymentStatus.PENDING
    from_address: str
    to_address: str
    amount: str
    currency: str = "SIL"
    description: Optional[str] = None
    metadata: Dict[str, Any] = {}
    tx_hash: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    completed_at: Optional[datetime] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        now = datetime.utcnow()
        if 'created_at' not in data:
            data['created_at'] = now
        if 'updated_at' not in data:
            data['updated_at'] = now
        super().__init__(**data)
    
    def update_status(self, status: PaymentStatus, tx_hash: Optional[str] = None):
        """更新支付状态"""
        self.status = status
        self.updated_at = datetime.utcnow()
        if tx_hash:
            self.tx_hash = tx_hash
        if status == PaymentStatus.COMPLETED:
            self.completed_at = self.updated_at


class PaymentRequest(BaseModel):
    """支付请求"""
    to_address: str
    amount: str
    currency: str = "SIL"
    description: Optional[str] = None
    metadata: Dict[str, Any] = {}


class PaymentProcessor:
    """
    支付处理器
    
    处理支付请求、验证交易、更新状态
    """
    
    def __init__(self):
        self.payments: Dict[str, Payment] = {}
        self.callbacks: Dict[str, callable] = {}  # 支付完成回调
    
    def create_payment(
        self,
        from_address: str,
        to_address: str,
        amount: str,
        currency: str = "SIL",
        type: PaymentType = PaymentType.PURCHASE,
        description: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Payment:
        """
        创建支付记录
        
        Args:
            from_address: 付款方地址
            to_address: 收款方地址
            amount: 金额
            currency: 货币类型
            type: 支付类型
            description: 描述
            metadata: 元数据
        
        Returns:
            支付记录
        """
        payment = Payment(
            type=type,
            from_address=from_address,
            to_address=to_address,
            amount=amount,
            currency=currency,
            description=description,
            metadata=metadata or {}
        )
        
        self.payments[payment.id] = payment
        return payment
    
    def get_payment(self, payment_id: str) -> Optional[Payment]:
        """获取支付记录"""
        return self.payments.get(payment_id)
    
    def list_payments(
        self,
        address: Optional[str] = None,
        status: Optional[PaymentStatus] = None,
        limit: int = 50
    ) -> List[Payment]:
        """
        列出支付记录
        
        Args:
            address: 地址过滤 (付款方或收款方)
            status: 状态过滤
            limit: 返回数量限制
        
        Returns:
            支付记录列表
        """
        payments = list(self.payments.values())
        
        # 过滤
        if address:
            payments = [
                p for p in payments
                if p.from_address == address or p.to_address == address
            ]
        
        if status:
            payments = [p for p in payments if p.status == status]
        
        # 按时间倒序
        payments.sort(key=lambda p: p.created_at, reverse=True)
        
        return payments[:limit]
    
    def process_payment(self, payment_id: str, tx_hash: str) -> bool:
        """
        处理支付 (确认交易)
        
        Args:
            payment_id: 支付 ID
            tx_hash: 交易哈希
        
        Returns:
            是否成功
        """
        payment = self.get_payment(payment_id)
        if not payment:
            return False
        
        # 更新状态
        payment.update_status(PaymentStatus.PROCESSING, tx_hash)
        
        # TODO: 验证链上交易
        # 这里简化处理，直接标记为完成
        payment.update_status(PaymentStatus.COMPLETED)
        
        # 触发回调
        if payment_id in self.callbacks:
            try:
                self.callbacks[payment_id](payment)
            except Exception as e:
                print(f"支付回调失败：{e}")
        
        return True
    
    def cancel_payment(self, payment_id: str) -> bool:
        """取消支付"""
        payment = self.get_payment(payment_id)
        if not payment:
            return False
        
        if payment.status != PaymentStatus.PENDING:
            return False
        
        payment.update_status(PaymentStatus.CANCELLED)
        return True
    
    def refund_payment(self, payment_id: str, refund_amount: Optional[str] = None) -> Optional[Payment]:
        """
        退款
        
        Args:
            payment_id: 原支付 ID
            refund_amount: 退款金额 (默认全额)
        
        Returns:
            退款支付记录
        """
        payment = self.get_payment(payment_id)
        if not payment:
            return None
        
        if payment.status != PaymentStatus.COMPLETED:
            return None
        
        # 创建退款记录
        refund = self.create_payment(
            from_address=payment.to_address,
            to_address=payment.from_address,
            amount=refund_amount or payment.amount,
            currency=payment.currency,
            type=PaymentType.REFUND,
            description=f"退款：{payment.id}",
            metadata={"original_payment": payment_id}
        )
        
        # 更新原支付状态
        payment.update_status(PaymentStatus.REFUNDED)
        
        return refund
    
    def register_callback(self, payment_id: str, callback: callable):
        """注册支付完成回调"""
        self.callbacks[payment_id] = callback
    
    def get_statistics(self, address: str) -> Dict[str, Any]:
        """
        获取支付统计
        
        Args:
            address: 地址
        
        Returns:
            统计数据
        """
        payments = self.list_payments(address=address, limit=1000)
        
        total_sent = 0.0
        total_received = 0.0
        count_sent = 0
        count_received = 0
        
        for payment in payments:
            if payment.status != PaymentStatus.COMPLETED:
                continue
            
            amount = float(payment.amount)
            if payment.from_address == address:
                total_sent += amount
                count_sent += 1
            elif payment.to_address == address:
                total_received += amount
                count_received += 1
        
        return {
            "address": address,
            "total_sent": str(total_sent),
            "total_received": str(total_received),
            "count_sent": count_sent,
            "count_received": count_received,
            "total_payments": len(payments)
        }
    
    def generate_payment_proof(self, payment_id: str) -> Optional[str]:
        """
        生成支付证明
        
        Args:
            payment_id: 支付 ID
        
        Returns:
            支付证明哈希
        """
        payment = self.get_payment(payment_id)
        if not payment:
            return None
        
        # 生成证明数据
        proof_data = {
            "payment_id": payment.id,
            "from": payment.from_address,
            "to": payment.to_address,
            "amount": payment.amount,
            "tx_hash": payment.tx_hash,
            "timestamp": payment.created_at.isoformat()
        }
        
        # 生成哈希
        proof_str = json.dumps(proof_data, sort_keys=True)
        proof_hash = hashlib.sha256(proof_str.encode()).hexdigest()
        
        return proof_hash


# 导入 json
import json


# 使用示例
if __name__ == "__main__":
    # 创建处理器
    processor = PaymentProcessor()
    
    # 创建支付
    print("创建支付...")
    payment = processor.create_payment(
        from_address="0x1234567890123456789012345678901234567890",
        to_address="0x0987654321098765432109876543210987654321",
        amount="100.50",
        currency="SIL",
        type=PaymentType.PURCHASE,
        description="购买 NFT #001"
    )
    print(f"支付 ID: {payment.id}")
    print(f"状态：{payment.status}")
    
    # 处理支付
    print("\n处理支付...")
    success = processor.process_payment(
        payment.id,
        "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
    )
    print(f"处理结果：{success}")
    print(f"新状态：{payment.status}")
    
    # 获取统计
    print("\n支付统计:")
    stats = processor.get_statistics(payment.from_address)
    print(f"发送总额：{stats['total_sent']}")
    print(f"交易次数：{stats['count_sent']}")
