"""
NexusA 集成模块

AI Agent 金融基础设施集成
- 钱包管理
- 支付系统 (x402)
- 智能合约
- 经济系统
"""

from .wallet import WalletManager, Wallet
from .payment import PaymentProcessor, Payment
from .config import NexusAConfig

__version__ = "1.0.0"
__all__ = [
    "WalletManager",
    "Wallet",
    "PaymentProcessor",
    "Payment",
    "NexusAConfig",
]
