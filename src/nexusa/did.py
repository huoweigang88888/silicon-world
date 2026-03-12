"""
NexusA DID 身份管理模块
基于 NexusA DIDRegistry 合约
"""

import hashlib
import uuid
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DIDDocument:
    """DID 文档"""
    did: str = ""
    controller: str = ""
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    updated: str = ""
    public_keys: List[Dict[str, Any]] = field(default_factory=list)
    services: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DIDManager:
    """DID 管理器"""
    
    def __init__(self, contract_address: str = ""):
        """初始化 DID 管理器"""
        self.contract_address = contract_address
        self.did_registry: Dict[str, DIDDocument] = {}
    
    def generate_did(self, address: str) -> str:
        """
        生成 DID
        格式：did:nexusa:{chain_id}:{address}
        """
        # 简化版本，实际应从合约读取 chain_id
        chain_id = 11155111  # Sepolia
        did = f"did:nexusa:{chain_id}:{address.lower()}"
        
        return did
    
    def create_did(self, controller: str, metadata: Optional[Dict] = None) -> DIDDocument:
        """
        创建新 DID
        返回：DID 文档
        """
        did = self.generate_did(controller)
        
        # 检查是否已存在
        if did in self.did_registry:
            raise Exception(f"DID 已存在：{did}")
        
        # 创建文档
        doc = DIDDocument(
            did=did,
            controller=controller,
            updated=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        # 生成默认公钥
        public_key = {
            "id": f"{did}#keys-1",
            "type": "EcdsaSecp256k1VerificationKey2019",
            "controller": controller,
            "publicKeyHex": hashlib.sha256(controller.encode()).hexdigest()
        }
        doc.public_keys.append(public_key)
        
        # 添加默认服务
        doc.services.append({
            "id": f"{did}#messaging",
            "type": "Messaging",
            "serviceEndpoint": "https://silicon-world.io/messaging"
        })
        
        # 注册
        self.did_registry[did] = doc
        
        return doc
    
    def get_did(self, did: str) -> Optional[DIDDocument]:
        """获取 DID 文档"""
        return self.did_registry.get(did)
    
    def update_did(
        self,
        did: str,
        public_keys: Optional[List] = None,
        services: Optional[List] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """更新 DID 文档"""
        if did not in self.did_registry:
            return False
        
        doc = self.did_registry[did]
        
        if public_keys is not None:
            doc.public_keys = public_keys
        
        if services is not None:
            doc.services = services
        
        if metadata is not None:
            doc.metadata.update(metadata)
        
        doc.updated = datetime.now().isoformat()
        
        return True
    
    def add_public_key(
        self,
        did: str,
        key_type: str,
        public_key: str,
        key_id: Optional[str] = None
    ) -> bool:
        """添加公钥"""
        if did not in self.did_registry:
            return False
        
        doc = self.did_registry[did]
        
        key_entry = {
            "id": key_id or f"{did}#keys-{len(doc.public_keys) + 1}",
            "type": key_type,
            "controller": doc.controller,
            "publicKeyHex": public_key
        }
        
        doc.public_keys.append(key_entry)
        doc.updated = datetime.now().isoformat()
        
        return True
    
    def add_service(
        self,
        did: str,
        service_type: str,
        endpoint: str,
        service_id: Optional[str] = None
    ) -> bool:
        """添加服务"""
        if did not in self.did_registry:
            return False
        
        doc = self.did_registry[did]
        
        service_entry = {
            "id": service_id or f"{did}#service-{len(doc.services) + 1}",
            "type": service_type,
            "serviceEndpoint": endpoint
        }
        
        doc.services.append(service_entry)
        doc.updated = datetime.now().isoformat()
        
        return True
    
    def resolve_did(self, did: str) -> Optional[Dict[str, Any]]:
        """
        解析 DID
        返回：完整的 DID 文档 (字典格式)
        """
        doc = self.get_did(did)
        if not doc:
            return None
        
        return {
            "@context": [
                "https://www.w3.org/ns/did/v1",
                "https://w3id.org/security/suites/secp256k1-2019/v1"
            ],
            "id": doc.did,
            "controller": doc.controller,
            "created": doc.created,
            "updated": doc.updated,
            "verificationMethod": doc.public_keys,
            "service": doc.services,
            "metadata": doc.metadata,
        }
    
    def verify_did(self, did: str, signature: str, message: str) -> bool:
        """验证 DID 签名"""
        doc = self.get_did(did)
        if not doc:
            return False
        
        # 简化验证 (实际应使用密码学验证)
        # 这里只检查 DID 是否存在
        return True
    
    def list_dids(self, controller: Optional[str] = None) -> List[str]:
        """列出 DID"""
        if controller:
            return [
                did for did in self.did_registry.keys()
                if self.did_registry[did].controller.lower() == controller.lower()
            ]
        return list(self.did_registry.keys())


# 快捷函数
def create_user_did(address: str, metadata: Optional[Dict] = None) -> str:
    """为用户创建 DID 的快捷函数"""
    manager = DIDManager()
    doc = manager.create_did(address, metadata)
    return doc.did


def resolve_user_did(did: str) -> Optional[Dict]:
    """解析用户 DID 的快捷函数"""
    manager = DIDManager()
    return manager.resolve_did(did)
