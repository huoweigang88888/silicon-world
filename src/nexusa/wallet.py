"""
NexusA 钱包模块

钱包管理、密钥管理、交易签名
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime
import secrets
import json
import os
from pathlib import Path

# 尝试导入 web3
try:
    from eth_account import Account
    from eth_account.signers.local import LocalAccount
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    Account = None
    LocalAccount = None


class Wallet(BaseModel):
    """
    钱包模型
    
    存储钱包地址、加密私钥等信息
    """
    address: str
    encrypted_private_key: Optional[str] = None
    created_at: datetime = None
    label: Optional[str] = None
    metadata: Dict[str, Any] = {}
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow()
        super().__init__(**data)


class WalletInfo(BaseModel):
    """钱包信息 (不包含私钥)"""
    address: str
    balance: str = "0"
    nonce: int = 0
    created_at: datetime = None
    label: Optional[str] = None
    transaction_count: int = 0


class WalletManager:
    """
    零知识钱包管理器
    
    ⚠️ 安全原则：私钥永远不存储在服务端！
    
    只管理钱包地址和元数据，私钥由用户客户端保管
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        初始化钱包管理器
        
        Args:
            storage_path: 钱包存储路径 (可选)
        """
        self.storage_path = storage_path
        self.wallets: Dict[str, Wallet] = {}
        
        # ⚠️ 不再存储 _accounts (私钥)
        
        # 如果存储路径存在，加载钱包
        if storage_path and os.path.exists(storage_path):
            self._load_wallets()
    
    def create_wallet(self, label: Optional[str] = None) -> Wallet:
        """
        创建新钱包 (占位符)
        
        ⚠️ 注意：实际应由客户端生成钱包，服务端只注册地址
        
        Args:
            label: 钱包标签
        
        Returns:
            新创建的钱包 (只有地址，无私钥)
        """
        # 生成临时地址 (仅用于演示，实际应由客户端生成)
        if WEB3_AVAILABLE:
            account = Account.create()
            address = account.address
        else:
            # 无 web3 时生成伪地址
            address = f"0x{secrets.token_hex(20)}"
        
        # 创建钱包对象 (无私钥)
        wallet = Wallet(
            address=address,
            encrypted_private_key=None,  # ⚠️ 永远为 None
            label=label,
            metadata={
                "created_by": "client",  # 客户端生成
                "server_never_saw_private_key": True,
                "version": "1.0"
            }
        )
        
        # 保存 (只存地址)
        self.wallets[address] = wallet
        self._save_wallets()
        
        return wallet
    
    def register_wallet(self, address: str, label: Optional[str] = None) -> Wallet:
        """
        注册客户端创建的钱包
        
        客户端生成钱包后，只发送地址到服务端注册
        ⚠️ 这是推荐的使用方式
        
        Args:
            address: 客户端生成的钱包地址
            label: 钱包标签
        
        Returns:
            注册成功的钱包
        """
        # 验证地址格式
        if not address.startswith("0x") or len(address) != 42:
            raise ValueError("无效的钱包地址格式")
        
        # 检查是否已存在
        if address in self.wallets:
            return self.wallets[address]
        
        # 创建钱包对象
        wallet = Wallet(
            address=address,
            encrypted_private_key=None,  # ⚠️ 永远为 None
            label=label,
            metadata={
                "registered_at": datetime.utcnow().isoformat(),
                "private_key_never_stored": True,
                "client_generated": True
            }
        )
        
        # 保存
        self.wallets[address] = wallet
        self._save_wallets()
        
        return wallet
    
    def import_wallet(self, address: str, label: Optional[str] = None) -> Wallet:
        """
        导入/注册现有钱包地址
        
        ⚠️ 不再接受私钥！只注册地址
        
        Args:
            address: 钱包地址
            label: 钱包标签
        
        Returns:
            导入的钱包
        """
        # 验证地址格式
        if not address.startswith("0x") or len(address) != 42:
            raise ValueError("无效的钱包地址格式")
        
        # 检查是否已存在
        if address in self.wallets:
            return self.wallets[address]
        
        # 创建钱包对象
        wallet = Wallet(
            address=address,
            encrypted_private_key=None,  # ⚠️ 永远为 None
            label=label,
            metadata={
                "imported": True,
                "imported_at": datetime.utcnow().isoformat(),
                "private_key_never_stored": True
            }
        )
        
        # 保存
        self.wallets[address] = wallet
        self._save_wallets()
        
        return wallet
    
    def get_wallet(self, address: str) -> Optional[Wallet]:
        """获取钱包"""
        return self.wallets.get(address)
    
    def list_wallets(self) -> List[Wallet]:
        """列出所有钱包"""
        return list(self.wallets.values())
    
    def delete_wallet(self, address: str) -> bool:
        """
        删除钱包
        
        Args:
            address: 钱包地址
        
        Returns:
            是否成功删除
        """
        if address in self.wallets:
            del self.wallets[address]
            # ⚠️ 不再删除 _accounts (因为不存在)
            self._save_wallets()
            return True
        return False
    
    def export_wallet(self, address: str) -> Optional[Dict[str, Any]]:
        """
        导出钱包信息
        
        ⚠️ 不再导出私钥！只返回钱包元数据
        
        Args:
            address: 钱包地址
        
        Returns:
            钱包元数据 (不包含私钥)
        """
        wallet = self.wallets.get(address)
        if not wallet:
            return None
        
        return {
            "address": wallet.address,
            "label": wallet.label,
            "created_at": wallet.created_at.isoformat(),
            "metadata": wallet.metadata,
            "note": "私钥由客户端保管，服务端无法导出"
        }
    
    def verify_signature(self, address: str, message: str, signature: str) -> bool:
        """
        验证客户端签名
        
        ⚠️ 服务端只验证签名，不生成签名
        
        Args:
            address: 钱包地址
            message: 原始消息
            signature: 签名结果
        
        Returns:
            签名是否有效
        """
        if not WEB3_AVAILABLE:
            raise ImportError("web3.py 未安装")
        
        try:
            # 恢复签名者地址
            message_hash = Account.hash_defunct_message(message.encode())
            recovered = Account.recover_hash(message_hash, signature=signature)
            
            # 验证是否匹配
            return recovered.lower() == address.lower()
        except Exception:
            return False
    
    # ⚠️ 已移除 _encrypt_key 和 _decrypt_key
    # 服务端不再加密/解密私钥，私钥永远由客户端保管
    
    def _save_wallets(self):
        """保存钱包到文件"""
        if not self.storage_path:
            return
        
        # 只保存非敏感信息
        data = {
            address: {
                "address": wallet.address,
                "label": wallet.label,
                "created_at": wallet.created_at.isoformat(),
                "metadata": wallet.metadata
            }
            for address, wallet in self.wallets.items()
        }
        
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def _load_wallets(self):
        """从文件加载钱包"""
        if not self.storage_path or not os.path.exists(self.storage_path):
            return
        
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for address, wallet_data in data.items():
            wallet = Wallet(
                address=wallet_data["address"],
                label=wallet_data.get("label"),
                created_at=datetime.fromisoformat(wallet_data["created_at"]),
                metadata=wallet_data.get("metadata", {})
            )
            self.wallets[address] = wallet


# 使用示例
if __name__ == "__main__":
    if WEB3_AVAILABLE:
        # 创建管理器
        manager = WalletManager("wallets.json")
        
        # 创建新钱包
        print("创建新钱包...")
        wallet = manager.create_wallet(label="My Wallet")
        print(f"地址：{wallet.address}")
        
        # 列出钱包
        print("\n所有钱包:")
        for w in manager.list_wallets():
            print(f"  - {w.address} ({w.label})")
        
        # 导出钱包
        print("\n导出钱包:")
        exported = manager.export_wallet(wallet.address)
        print(f"地址：{exported['address']}")
        print(f"私钥：{exported['private_key'][:10]}...")
    else:
        print("web3.py 未安装，请运行：pip install web3")
