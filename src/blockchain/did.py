"""
DID 去中心化身份系统

W3C DID 标准实现
"""

import uuid
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class PublicKey(BaseModel):
    """公钥"""
    id: str
    type: str = "Ed25519VerificationKey2020"
    controller: str
    publicKeyMultibase: str


class Service(BaseModel):
    """服务"""
    id: str
    type: str
    serviceEndpoint: str


class DIDDocument(BaseModel):
    """DID 文档"""
    context: List[str] = Field(
        default=["https://www.w3.org/ns/did/v1"],
        alias="@context"
    )
    id: str
    controller: str
    created: str
    updated: str
    publicKey: List[PublicKey] = []
    service: List[Service] = []
    
    class Config:
        populate_by_name = True


class DIDManager:
    """DID 管理器"""
    
    def __init__(self, network: str = "silicon"):
        self.network = network
    
    def generate_did(self, controller: str) -> str:
        """
        生成 DID
        
        Args:
            controller: 控制者地址
        
        Returns:
            DID 字符串
        """
        # 生成唯一 ID
        unique_id = uuid.uuid4().hex
        return f"did:{self.network}:agent:{unique_id}"
    
    def create_document(
        self,
        did: str,
        controller: str,
        public_key: Optional[str] = None,
        services: Optional[List[Dict]] = None
    ) -> DIDDocument:
        """
        创建 DID 文档
        
        Args:
            did: DID 字符串
            controller: 控制者地址
            public_key: 公钥 (可选)
            services: 服务列表 (可选)
        
        Returns:
            DIDDocument
        """
        now = datetime.utcnow().isoformat() + "Z"
        
        doc = DIDDocument(
            id=did,
            controller=controller,
            created=now,
            updated=now
        )
        
        # 添加公钥
        if public_key:
            doc.publicKey.append(
                PublicKey(
                    id=f"{did}#keys-1",
                    controller=controller,
                    publicKeyMultibase=public_key
                )
            )
        
        # 添加服务
        if services:
            for i, service in enumerate(services):
                doc.service.append(
                    Service(
                        id=f"{did}#service-{i}",
                        type=service.get("type", "Generic"),
                        serviceEndpoint=service.get("endpoint", "")
                    )
                )
        
        return doc
    
    def verify_did(self, did: str) -> bool:
        """
        验证 DID 格式
        
        Args:
            did: DID 字符串
        
        Returns:
            是否有效
        """
        # 格式：did:silicon:agent:<unique-id>
        parts = did.split(":")
        if len(parts) != 4:
            return False
        
        if parts[0] != "did":
            return False
        
        if parts[1] != self.network:
            return False
        
        if parts[2] not in ["agent", "user"]:
            return False
        
        # 验证 unique-id 格式
        unique_id = parts[3]
        if len(unique_id) != 32:
            return False
        
        try:
            uuid.UUID(unique_id)
            return True
        except ValueError:
            return False
    
    def parse_did(self, did: str) -> Dict[str, str]:
        """
        解析 DID
        
        Args:
            did: DID 字符串
        
        Returns:
            解析结果
        """
        if not self.verify_did(did):
            raise ValueError(f"Invalid DID: {did}")
        
        parts = did.split(":")
        return {
            "method": parts[1],
            "type": parts[2],
            "id": parts[3]
        }
    
    def hash_document(self, doc: DIDDocument) -> str:
        """
        计算 DID 文档哈希
        
        Args:
            doc: DIDDocument
        
        Returns:
            SHA256 哈希
        """
        doc_json = doc.model_dump_json(exclude={"context"})
        return hashlib.sha256(doc_json.encode()).hexdigest()


# 使用示例
if __name__ == "__main__":
    manager = DIDManager()
    
    # 生成 DID
    controller = "0x1234567890abcdef"
    did = manager.generate_did(controller)
    print(f"Generated DID: {did}")
    
    # 创建 DID 文档
    doc = manager.create_document(
        did=did,
        controller=controller,
        public_key="z6MkhaXgBZDvotDkWL5Tcu24GmjVpXppmQBBXwzqPz6MkhaX",
        services=[
            {"type": "Messaging", "endpoint": "https://silicon.world/msg"}
        ]
    )
    
    print(f"DID Document: {doc.model_dump_json(indent=2)}")
    
    # 验证 DID
    is_valid = manager.verify_did(did)
    print(f"DID Valid: {is_valid}")
    
    # 解析 DID
    parsed = manager.parse_did(did)
    print(f"Parsed: {parsed}")
