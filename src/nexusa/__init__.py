# NexusA 集成模块
# 硅基世界 x NexusA 金融基础设施

from .config import NexusaConfig
from .wallet import WalletConnector
from .payment import PaymentProcessor
from .did import DIDManager

__version__ = "1.0.0"
__all__ = [
    "NexusaConfig",
    "WalletConnector",
    "PaymentProcessor",
    "DIDManager",
]
