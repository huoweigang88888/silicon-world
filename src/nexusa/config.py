"""
NexusA 配置模块

区块链网络配置、合约地址等
"""

from typing import Dict, Optional
from pydantic import BaseModel
import os
from pathlib import Path


class NetworkConfig(BaseModel):
    """网络配置"""
    name: str
    rpc_url: str
    chain_id: int
    explorer_url: str
    currency_symbol: str


class NexusAConfig(BaseModel):
    """
    NexusA 配置
    
    支持多个网络配置
    """
    # 当前网络
    network: str = "goerli"
    
    # 合约地址
    marketplace_contract: Optional[str] = None
    payment_contract: Optional[str] = None
    token_contract: Optional[str] = None
    
    # API 配置
    api_timeout: int = 30
    max_retries: int = 3
    
    class Config:
        arbitrary_types_allowed = True
    
    # 预定义网络配置
    NETWORKS: Dict[str, NetworkConfig] = {
        "goerli": NetworkConfig(
            name="Goerli",
            rpc_url=os.getenv("NEXUSA_GOERLI_RPC", "https://goerli.infura.io/v3/YOUR_KEY"),
            chain_id=5,
            explorer_url="https://goerli.etherscan.io",
            currency_symbol="GoerliETH"
        ),
        "sepolia": NetworkConfig(
            name="Sepolia",
            rpc_url=os.getenv("NEXUSA_SEPOLIA_RPC", "https://sepolia.infura.io/v3/YOUR_KEY"),
            chain_id=11155111,
            explorer_url="https://sepolia.etherscan.io",
            currency_symbol="SepoliaETH"
        ),
        "mainnet": NetworkConfig(
            name="Ethereum Mainnet",
            rpc_url=os.getenv("NEXUSA_MAINNET_RPC", "https://mainnet.infura.io/v3/YOUR_KEY"),
            chain_id=1,
            explorer_url="https://etherscan.io",
            currency_symbol="ETH"
        ),
        "local": NetworkConfig(
            name="Local Development",
            rpc_url=os.getenv("NEXUSA_LOCAL_RPC", "http://localhost:8545"),
            chain_id=31337,
            explorer_url="",
            currency_symbol="ETH"
        )
    }
    
    def get_network(self) -> NetworkConfig:
        """获取当前网络配置"""
        return self.NETWORKS.get(self.network, self.NETWORKS["goerli"])
    
    def get_rpc_url(self) -> str:
        """获取 RPC URL"""
        return self.get_network().rpc_url
    
    def get_chain_id(self) -> int:
        """获取 Chain ID"""
        return self.get_network().chain_id
    
    def get_explorer_url(self, tx_hash: str) -> str:
        """获取交易浏览器 URL"""
        base = self.get_network().explorer_url
        if base:
            return f"{base}/tx/{tx_hash}"
        return tx_hash
    
    @classmethod
    def from_env(cls) -> "NexusAConfig":
        """从环境变量加载配置"""
        return cls(
            network=os.getenv("NEXUSA_NETWORK", "goerli"),
            marketplace_contract=os.getenv("NEXUSA_MARKETPLACE_CONTRACT"),
            payment_contract=os.getenv("NEXUSA_PAYMENT_CONTRACT"),
            token_contract=os.getenv("NEXUSA_TOKEN_CONTRACT"),
            api_timeout=int(os.getenv("NEXUSA_API_TIMEOUT", "30")),
            max_retries=int(os.getenv("NEXUSA_MAX_RETRIES", "3"))
        )


# 全局配置实例
_config: Optional[NexusAConfig] = None


def get_config() -> NexusAConfig:
    """获取全局配置"""
    global _config
    if _config is None:
        _config = NexusAConfig.from_env()
    return _config


def set_config(config: NexusAConfig):
    """设置全局配置"""
    global _config
    _config = config


# 使用示例
if __name__ == "__main__":
    config = get_config()
    print(f"当前网络：{config.network}")
    print(f"RPC URL: {config.get_rpc_url()}")
    print(f"Chain ID: {config.get_chain_id()}")
