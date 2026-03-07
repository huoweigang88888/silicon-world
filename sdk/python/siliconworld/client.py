"""
Silicon World API 客户端
"""

import requests
from typing import Dict, List, Optional, Any
from datetime import datetime


class SiliconWorldClient:
    """
    硅基世界 API 客户端
    
    Usage:
        client = SiliconWorldClient(base_url="https://api.silicon.world")
        agent = client.get_agent("did:silicon:agent:123")
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: str = None,
        timeout: int = 30
    ):
        """
        初始化客户端
        
        Args:
            base_url: API 基础 URL
            api_key: API 密钥
            timeout: 请求超时时间
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """发送 HTTP 请求"""
        url = f"{self.base_url}{path}"
        
        try:
            response = self.session.request(
                method,
                url,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    # ==================== 身份 API ====================
    
    def create_did(self, controller: str, public_key: str = None) -> Dict[str, Any]:
        """创建 DID"""
        return self._request("POST", "/api/v1/did", json={
            "controller": controller,
            "public_key": public_key
        })
    
    def get_did(self, did: str) -> Dict[str, Any]:
        """获取 DID 信息"""
        return self._request("GET", f"/api/v1/did/{did}")
    
    def verify_did(self, did: str) -> Dict[str, Any]:
        """验证 DID"""
        return self._request("POST", f"/api/v1/did/{did}/verify")
    
    # ==================== Agent API ====================
    
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """获取 Agent 信息"""
        return self._request("GET", f"/api/v1/agents/{agent_id}")
    
    def list_agents(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """获取 Agent 列表"""
        return self._request("GET", "/api/v1/agents", params={
            "limit": limit,
            "offset": offset
        })
    
    def create_agent(self, name: str, personality: Dict[str, float] = None) -> Dict[str, Any]:
        """创建 Agent"""
        return self._request("POST", "/api/v1/agents", json={
            "name": name,
            "personality": personality
        })
    
    # ==================== 世界 API ====================
    
    def get_world_info(self) -> Dict[str, Any]:
        """获取世界信息"""
        return self._request("GET", "/api/v1/world")
    
    def get_region(self, region_id: str) -> Dict[str, Any]:
        """获取区域信息"""
        return self._request("GET", f"/api/v1/world/regions/{region_id}")
    
    def teleport(self, agent_id: str, portal_id: str) -> Dict[str, Any]:
        """传送 Agent"""
        return self._request("POST", "/api/v1/world/teleport", json={
            "agent_id": agent_id,
            "portal_id": portal_id
        })
    
    # ==================== 经济 API ====================
    
    def get_balance(self, address: str) -> Dict[str, Any]:
        """获取代币余额"""
        return self._request("GET", f"/api/v1/balance/{address}")
    
    def transfer(self, from_address: str, to_address: str, amount: int) -> Dict[str, Any]:
        """转账"""
        return self._request("POST", "/api/v1/transfer", json={
            "from_address": from_address,
            "to_address": to_address,
            "amount": amount
        })
    
    def create_order(self, order_type: str, asset_type: str, amount: int, price: int) -> Dict[str, Any]:
        """创建订单"""
        return self._request("POST", "/api/v1/market/orders", json={
            "order_type": order_type,
            "asset_type": asset_type,
            "amount": amount,
            "price": price
        })
    
    # ==================== 社交 API ====================
    
    def send_message(self, conversation_id: str, content: str) -> Dict[str, Any]:
        """发送消息"""
        return self._request("POST", f"/api/v1/conversations/{conversation_id}/messages", json={
            "content": content
        })
    
    def get_conversations(self, user_id: str) -> Dict[str, Any]:
        """获取会话列表"""
        return self._request("GET", f"/api/v1/users/{user_id}/conversations")
    
    def send_friend_request(self, target_id: str, message: str = None) -> Dict[str, Any]:
        """发送好友请求"""
        return self._request("POST", "/api/v1/friends/requests", json={
            "target_id": target_id,
            "message": message
        })
    
    # ==================== 治理 API ====================
    
    def create_proposal(self, title: str, description: str, proposal_type: str) -> Dict[str, Any]:
        """创建提案"""
        return self._request("POST", "/api/v1/governance/proposals", json={
            "title": title,
            "description": description,
            "proposal_type": proposal_type
        })
    
    def vote(self, proposal_id: str, vote: str, voting_power: int) -> Dict[str, Any]:
        """投票"""
        return self._request("POST", f"/api/v1/governance/proposals/{proposal_id}/vote", json={
            "vote": vote,
            "voting_power": voting_power
        })
    
    # ==================== 工具 API ====================
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return self._request("GET", "/health")
    
    def get_api_version(self) -> Dict[str, Any]:
        """获取 API 版本"""
        return self._request("GET", "/")
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取平台统计"""
        return self._request("GET", "/api/v1/statistics")


# 使用示例
if __name__ == "__main__":
    # 创建客户端
    client = SiliconWorldClient(base_url="http://localhost:8000")
    
    # 健康检查
    print("健康检查:", client.health_check())
    
    # 创建 DID
    print("\n创建 DID...")
    did_info = client.create_did(
        controller="0x1234567890abcdef",
        public_key="z6MkhaXgBZDvotDkWL5Tcu24GmjVpXppmQBBXwzqPz6MkhaX"
    )
    print(f"DID: {did_info.get('did')}")
    
    # 获取 Agent 列表
    print("\nAgent 列表:")
    agents = client.list_agents(limit=5)
    print(f"总数：{agents.get('total')}")
    
    # 获取平台统计
    print("\n平台统计:")
    stats = client.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
