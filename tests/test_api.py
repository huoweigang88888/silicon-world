"""
API 集成测试
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


def test_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    print("[OK] 根路径测试通过")


def test_health():
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("[OK] 健康检查测试通过")


def test_create_did():
    """测试创建 DID"""
    response = client.post(
        "/api/v1/did",
        json={
            "controller": "0x1234567890abcdef",
            "public_key": "z6MkhaXgBZDvotDkWL5Tcu24GmjVpXppmQBBXwzqPz6MkhaX"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["did"].startswith("did:silicon:agent:")
    assert data["controller"] == "0x1234567890abcdef"
    assert data["active"] == True
    print(f"[OK] 创建 DID 测试通过：{data['did']}")


def test_get_did():
    """测试查询 DID"""
    did = "did:silicon:agent:1234567890abcdef1234567890abcdef"
    response = client.get(f"/api/v1/did/{did}")
    assert response.status_code == 200
    data = response.json()
    assert data["did"] == did
    print("[OK] 查询 DID 测试通过")


def test_verify_did():
    """测试验证 DID"""
    # 有效 DID
    valid_did = "did:silicon:agent:1234567890abcdef1234567890abcdef"
    response = client.post(f"/api/v1/did/{valid_did}/verify")
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] == True
    
    # 无效 DID
    invalid_did = "invalid-did"
    response = client.post(f"/api/v1/did/{invalid_did}/verify")
    assert response.status_code == 400
    print("[OK] 验证 DID 测试通过")


def test_list_agents():
    """测试获取 Agent 列表"""
    response = client.get("/api/v1/agents")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert "agents" in data
    print("[OK] 获取 Agent 列表测试通过")


def test_api_docs():
    """测试 API 文档"""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "Swagger UI" in response.text or "swagger" in response.text.lower()
    print("[OK] API 文档测试通过")


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("API 集成测试")
    print("=" * 50)
    print()
    
    tests = [
        test_root,
        test_health,
        test_create_did,
        test_get_did,
        test_verify_did,
        test_list_agents,
        test_api_docs
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {test.__name__}: {e}")
            failed += 1
    
    print()
    print("=" * 50)
    print(f"测试结果：{passed} 通过，{failed} 失败")
    print("=" * 50)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
