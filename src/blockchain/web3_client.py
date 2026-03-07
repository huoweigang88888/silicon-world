"""
Web3 客户端

用于与区块链交互
"""

from typing import Optional, Dict, Any
from web3 import Web3
from web3.contract import Contract
import json
from pathlib import Path


class Web3Client:
    """Web3 客户端"""
    
    def __init__(self, rpc_url: str = "http://localhost:8545"):
        """
        初始化 Web3 客户端
        
        Args:
            rpc_url: RPC 节点地址
        """
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.identity_contract: Optional[Contract] = None
        self.token_contract: Optional[Contract] = None
    
    def is_connected(self) -> bool:
        """检查是否连接到区块链"""
        return self.w3.is_connected()
    
    def get_balance(self, address: str) -> int:
        """
        获取账户余额
        
        Args:
            address: 账户地址
        
        Returns:
            余额 (Wei)
        """
        return self.w3.eth.get_balance(address)
    
    def load_contract(self, abi_path: str, address: Optional[str] = None) -> Contract:
        """
        加载智能合约
        
        Args:
            abi_path: ABI 文件路径
            address: 合约地址 (可选)
        
        Returns:
            合约对象
        """
        with open(abi_path, 'r', encoding='utf-8') as f:
            abi = json.load(f)
        
        if address:
            return self.w3.eth.contract(address=address, abi=abi)
        else:
            return self.w3.eth.contract(abi=abi)
    
    def deploy_identity_contract(
        self,
        private_key: str,
        gas_limit: int = 3000000
    ) -> Dict[str, Any]:
        """
        部署身份合约
        
        Args:
            private_key: 私钥
            gas_limit: Gas 限制
        
        Returns:
            部署结果
        """
        # 读取合约字节码 (需要先编译)
        contract_path = Path(__file__).parent / "contracts" / "Identity.bin"
        
        if not contract_path.exists():
            raise FileNotFoundError(
                "合约字节码文件不存在，请先编译合约"
            )
        
        with open(contract_path, 'r', encoding='utf-8') as f:
            contract_data = json.load(f)
        
        bytecode = contract_data['bytecode']
        abi = contract_data['abi']
        
        # 创建合约实例
        contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)
        
        # 构建交易
        account = self.w3.eth.account.from_key(private_key)
        nonce = self.w3.eth.get_transaction_count(account.address)
        
        tx = contract.constructor().build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': gas_limit,
            'gasPrice': self.w3.eth.gas_price
        })
        
        # 签名交易
        signed_tx = account.sign_transaction(tx)
        
        # 发送交易
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # 等待交易确认
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            'tx_hash': tx_hash.hex(),
            'contract_address': tx_receipt.contractAddress,
            'status': tx_receipt.status
        }
    
    def create_did(
        self,
        contract_address: str,
        private_key: str,
        did: str,
        public_key: str
    ) -> Dict[str, Any]:
        """
        在链上创建 DID
        
        Args:
            contract_address: 合约地址
            private_key: 私钥
            did: DID 字符串
            public_key: 公钥
        
        Returns:
            交易结果
        """
        # 加载合约
        abi_path = Path(__file__).parent / "contracts" / "Identity.abi"
        contract = self.load_contract(str(abi_path), contract_address)
        
        # 构建交易
        account = self.w3.eth.account.from_key(private_key)
        nonce = self.w3.eth.get_transaction_count(account.address)
        
        tx = contract.functions.createDID(did, public_key).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        # 签名交易
        signed_tx = account.sign_transaction(tx)
        
        # 发送交易
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # 等待交易确认
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            'tx_hash': tx_hash.hex(),
            'status': tx_receipt.status,
            'block_number': tx_receipt.block_number
        }
    
    def get_did(
        self,
        contract_address: str,
        did: str
    ) -> Dict[str, Any]:
        """
        查询 DID 信息
        
        Args:
            contract_address: 合约地址
            did: DID 字符串
        
        Returns:
            DID 信息
        """
        # 加载合约
        abi_path = Path(__file__).parent / "contracts" / "Identity.abi"
        contract = self.load_contract(str(abi_path), contract_address)
        
        result = contract.functions.getDID(did).call()
        
        return {
            'did': result[0],
            'controller': result[1],
            'created': result[2],
            'updated': result[3],
            'public_key': result[4],
            'active': result[5]
        }


# 使用示例
if __name__ == "__main__":
    # 连接到本地测试链
    client = Web3Client("http://localhost:8545")
    
    if client.is_connected():
        print("✓ 已连接到区块链")
        
        # 获取余额
        balance = client.get_balance("0x1234567890123456789012345678901234567890")
        print(f"余额：{client.w3.from_wei(balance, 'ether')} ETH")
    else:
        print("✗ 未连接到区块链，请启动本地测试链")
