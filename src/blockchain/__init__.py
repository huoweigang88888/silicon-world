"""
区块链模块

包含:
- DID 身份系统
- 智能合约
- Web3 集成
"""

from .did import DIDManager, DIDDocument, PublicKey, Service

__all__ = [
    "DIDManager",
    "DIDDocument",
    "PublicKey",
    "Service",
]
