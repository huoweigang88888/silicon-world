"""
硅基世界 API - 单元测试

运行测试：
    pytest tests/test_api.py -v

生成覆盖率报告：
    pytest tests/test_api.py -v --cov=src --cov-report=html
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.main import app

# 创建测试客户端
client = TestClient(app)


class TestHealth:
    """健康检查测试"""
    
    def test_root(self):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
    
    def test_health(self):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestAgents:
    """Agent API 测试"""
    
    @pytest.fixture
    def test_agent(self):
        """创建测试 Agent"""
        agent_data = {
            "name": "测试 Agent",
            "controller": "0x1234567890abcdef",
            "personality": {"type": "test"}
        }
        response = client.post("/api/v1/agents", json=agent_data)
        return response.json()
    
    def test_create_agent(self):
        """测试创建 Agent"""
        agent_data = {
            "name": "测试 Agent",
            "controller": "0x1234567890abcdef",
            "personality": {"type": "test", "emoji": "🧪"}
        }
        response = client.post("/api/v1/agents", json=agent_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "测试 Agent"
        assert data["controller"] == "0x1234567890abcdef"
        assert "id" in data
        assert data["active"] == True
    
    def test_get_agent(self, test_agent):
        """测试获取 Agent"""
        agent_id = test_agent["id"]
        response = client.get(f"/api/v1/agents/{agent_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == agent_id
        assert data["name"] == "测试 Agent"
    
    def test_list_agents(self, test_agent):
        """测试获取 Agent 列表"""
        response = client.get("/api/v1/agents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_agent_stats(self, test_agent):
        """测试获取 Agent 统计"""
        agent_id = test_agent["id"]
        response = client.get(f"/api/v1/agents/{agent_id}/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == agent_id
        assert "memories" in data
        assert "total" in data["memories"]
    
    def test_update_agent(self, test_agent):
        """测试更新 Agent"""
        agent_id = test_agent["id"]
        response = client.put(
            f"/api/v1/agents/{agent_id}",
            params={"name": "更新后的名字", "active": False}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "更新后的名字"
        assert data["active"] == False
        assert data["updated"] == True
    
    def test_get_nonexistent_agent(self):
        """测试获取不存在的 Agent"""
        response = client.get("/api/v1/agents/did:silicon:agent:nonexistent")
        assert response.status_code == 404


class TestMemories:
    """记忆 API 测试"""
    
    @pytest.fixture
    def test_agent_with_memories(self):
        """创建带记忆的测试 Agent"""
        # 创建 Agent
        agent_data = {
            "name": "记忆测试 Agent",
            "controller": "0x1234567890abcdef"
        }
        agent_response = client.post("/api/v1/agents", json=agent_data)
        agent_id = agent_response.json()["id"]
        
        # 创建记忆
        memories = [
            {"content": "短期记忆 1", "memory_type": "short_term"},
            {"content": "长期记忆 1", "memory_type": "long_term"},
            {"content": "长期记忆 2", "memory_type": "long_term"}
        ]
        for memory in memories:
            client.post(f"/api/v1/agents/{agent_id}/memories", json=memory)
        
        return agent_id
    
    def test_create_memory(self, test_agent_with_memories):
        """测试创建记忆"""
        agent_id = test_agent_with_memories
        memory_data = {
            "content": "新记忆",
            "memory_type": "semantic"
        }
        response = client.post(
            f"/api/v1/agents/{agent_id}/memories",
            json=memory_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "新记忆"
        assert data["memory_type"] == "semantic"
    
    def test_get_memories(self, test_agent_with_memories):
        """测试获取记忆列表"""
        agent_id = test_agent_with_memories
        response = client.get(f"/api/v1/agents/{agent_id}/memories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3
    
    def test_get_memories_by_type(self, test_agent_with_memories):
        """测试按类型获取记忆"""
        agent_id = test_agent_with_memories
        response = client.get(
            f"/api/v1/agents/{agent_id}/memories?memory_type=long_term"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # 至少有 2 条长期记忆
        assert len(data) >= 2
        for memory in data:
            assert memory["memory_type"] == "long_term"
    
    def test_search_memories(self, test_agent_with_memories):
        """测试搜索记忆"""
        agent_id = test_agent_with_memories
        response = client.get(
            f"/api/v1/agents/{agent_id}/memories/search?q=长期"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for memory in data:
            assert "长期" in memory["content"]


class TestDID:
    """DID API 测试"""
    
    def test_create_did(self):
        """测试创建 DID"""
        did_data = {
            "controller": "0x1234567890abcdef",
            "public_key": "test_public_key"
        }
        response = client.post("/api/v1/did", json=did_data)
        assert response.status_code == 200
        data = response.json()
        assert "did" in data
        assert data["controller"] == "0x1234567890abcdef"
        assert data["active"] == True
    
    def test_verify_did(self):
        """测试验证 DID"""
        # 先创建 DID
        did_data = {
            "controller": "0x1234567890abcdef"
        }
        create_response = client.post("/api/v1/did", json=did_data)
        did = create_response.json()["did"]
        
        # 验证 DID
        response = client.post(f"/api/v1/did/{did}/verify")
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        assert data["did"] == did
    
    def test_get_did(self):
        """测试获取 DID 信息"""
        did_data = {
            "controller": "0x1234567890abcdef"
        }
        create_response = client.post("/api/v1/did", json=did_data)
        did = create_response.json()["did"]
        
        response = client.get(f"/api/v1/did/{did}")
        assert response.status_code == 200
        data = response.json()
        assert data["did"] == did


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
