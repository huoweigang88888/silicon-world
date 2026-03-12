"""
NexusA 支付集成模块
基于 NexusA ERC8004Payment 合约
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class PaymentRecord:
    """支付记录"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    from_address: str = ""
    to_address: str = ""
    amount: float = 0.0
    token: str = "SWC"
    status: str = "pending"  # pending, completed, failed
    tx_hash: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None


class PaymentProcessor:
    """支付处理器"""
    
    def __init__(self, wallet_connector=None):
        """初始化支付处理器"""
        self.wallet_connector = wallet_connector
        self.payment_history: List[PaymentRecord] = []
    
    def process_payment(
        self,
        to_address: str,
        amount: float,
        token: str = "SWC",
        memo: str = ""
    ) -> PaymentRecord:
        """
        处理支付
        返回：支付记录
        """
        if not self.wallet_connector or not self.wallet_connector.connected_wallet:
            raise Exception("钱包未连接")
        
        # 创建支付记录
        record = PaymentRecord(
            from_address=self.wallet_connector.connected_wallet.address,
            to_address=to_address,
            amount=amount,
            token=token,
            status="pending"
        )
        
        # 模拟交易处理
        try:
            # 发送交易
            tx_result = self.wallet_connector.send_transaction(
                to=to_address,
                amount=amount,
                data=memo
            )
            
            record.tx_hash = tx_result["hash"]
            record.status = "completed"
            record.completed_at = datetime.now().isoformat()
            
        except Exception as e:
            record.status = "failed"
            print(f"支付失败：{e}")
        
        # 添加到历史记录
        self.payment_history.append(record)
        
        return record
    
    def request_payment(
        self,
        from_address: str,
        amount: float,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        请求支付
        返回：支付请求信息
        """
        request_id = str(uuid.uuid4())
        
        return {
            "request_id": request_id,
            "from": from_address,
            "to": self.wallet_connector.connected_wallet.address if self.wallet_connector else "",
            "amount": amount,
            "description": description,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "expires_at": None,  # 永不过期
        }
    
    def get_payment_status(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """获取支付状态"""
        for record in self.payment_history:
            if record.tx_hash == tx_hash:
                return {
                    "id": record.id,
                    "status": record.status,
                    "amount": record.amount,
                    "token": record.token,
                    "from": record.from_address,
                    "to": record.to_address,
                    "tx_hash": record.tx_hash,
                    "created_at": record.created_at,
                    "completed_at": record.completed_at,
                }
        return None
    
    def get_payment_history(
        self,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """获取支付历史"""
        history = self.payment_history[offset:offset + limit]
        
        return [
            {
                "id": record.id,
                "status": record.status,
                "amount": record.amount,
                "token": record.token,
                "from": record.from_address,
                "to": record.to_address,
                "tx_hash": record.tx_hash,
                "created_at": record.created_at,
            }
            for record in history
        ]
    
    def estimate_gas(self, to_address: str, amount: float) -> Dict[str, Any]:
        """估算 Gas 费用"""
        # 模拟 Gas 估算
        return {
            "gas_limit": 21000,
            "gas_price": 20,  # Gwei
            "estimated_fee": 0.00042,  # ETH
            "estimated_fee_usd": 1.05,
        }
    
    def batch_transfer(
        self,
        recipients: List[Dict[str, Any]]
    ) -> List[PaymentRecord]:
        """
        批量转账
        recipients: [{"address": "0x...", "amount": 100}, ...]
        """
        records = []
        
        for recipient in recipients:
            record = self.process_payment(
                to_address=recipient["address"],
                amount=recipient["amount"]
            )
            records.append(record)
        
        return records


# 快捷函数
def pay(to: str, amount: float, token: str = "SWC") -> PaymentRecord:
    """快速支付"""
    from nexusa.wallet import WalletConnector
    from nexusa.config import default_config
    
    wallet = WalletConnector(config=default_config)
    processor = PaymentProcessor(wallet_connector=wallet)
    
    return processor.process_payment(to, amount, token)
