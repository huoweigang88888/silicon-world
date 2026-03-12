"""
NexusA 配置模块
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class NexusaConfig:
    """NexusA 配置类"""
    
    # 网络配置
    network: str = "sepolia"  # mainnet, sepolia, localhost
    rpc_url: str = ""
    chain_id: int = 11155111  # Sepolia
    
    # 合约地址 (Sepolia 测试网)
    did_registry: str = ""
    ai_wallet: str = ""
    payment: str = ""
    credit_engine: str = ""
    insurance_pool: str = ""
    
    # API 配置
    api_url: str = "http://localhost:3000"
    api_key: str = ""
    
    # 钱包配置
    default_gas_limit: int = 21000
    max_fee_per_gas: Optional[int] = None
    
    @classmethod
    def from_network(cls, network: str = "sepolia") -> "NexusaConfig":
        """从预定义网络加载配置"""
        configs = {
            "mainnet": {
                "rpc_url": "https://eth-mainnet.g.alchemy.com/v2/",
                "chain_id": 1,
            },
            "sepolia": {
                "rpc_url": "https://eth-sepolia.g.alchemy.com/v2/",
                "chain_id": 11155111,
            },
            "localhost": {
                "rpc_url": "http://127.0.0.1:8545",
                "chain_id": 31337,
            }
        }
        
        if network not in configs:
            raise ValueError(f"未知网络：{network}")
        
        config = configs[network]
        return cls(
            network=network,
            rpc_url=config["rpc_url"],
            chain_id=config["chain_id"],
        )
    
    def validate(self) -> bool:
        """验证配置是否有效"""
        if not self.rpc_url:
            return False
        if self.network != "localhost" and not self.api_key:
            print("警告：生产环境需要 API Key")
        return True
    
    def __str__(self) -> str:
        return f"NexusaConfig(network={self.network}, chain_id={self.chain_id})"


# 全局配置实例
default_config = NexusaConfig.from_network("sepolia")
