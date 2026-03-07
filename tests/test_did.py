"""
DID 系统测试
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.blockchain.did import DIDManager, DIDDocument


def test_generate_did():
    """测试 DID 生成"""
    manager = DIDManager()
    controller = "0x1234567890abcdef"
    
    did = manager.generate_did(controller)
    
    assert did.startswith("did:silicon:agent:")
    # DID 长度：did:silicon:agent: (20) + uuid (32) = 50
    assert len(did) == 50
    print(f"[OK] DID 生成测试通过：{did}")


def test_verify_did():
    """测试 DID 验证"""
    manager = DIDManager()
    
    # 有效 DID
    valid_did = "did:silicon:agent:1234567890abcdef1234567890abcdef"
    assert manager.verify_did(valid_did) == True
    
    # 无效 DID - 格式错误
    invalid_did = "invalid-did"
    assert manager.verify_did(invalid_did) == False
    
    # 无效 DID - 网络错误
    wrong_network = "did:ethereum:agent:1234567890abcdef1234567890abcdef"
    assert manager.verify_did(wrong_network) == False
    
    print("[OK] DID 验证测试通过")


def test_create_document():
    """测试 DID 文档创建"""
    manager = DIDManager()
    controller = "0x1234567890abcdef"
    did = manager.generate_did(controller)
    
    doc = manager.create_document(
        did=did,
        controller=controller,
        public_key="z6MkhaXgBZDvotDkWL5Tcu24GmjVpXppmQBBXwzqPz6MkhaX",
        services=[
            {"type": "Messaging", "endpoint": "https://silicon.world/msg"}
        ]
    )
    
    assert doc.id == did
    assert doc.controller == controller
    assert len(doc.publicKey) == 1
    assert len(doc.service) == 1
    assert doc.created < doc.updated or doc.created == doc.updated
    
    print("[OK] DID 文档创建测试通过")


def test_parse_did():
    """测试 DID 解析"""
    manager = DIDManager()
    did = "did:silicon:agent:1234567890abcdef1234567890abcdef"
    
    parsed = manager.parse_did(did)
    
    assert parsed["method"] == "silicon"
    assert parsed["type"] == "agent"
    assert parsed["id"] == "1234567890abcdef1234567890abcdef"
    
    print(f"[OK] DID 解析测试通过")


def test_hash_document():
    """测试文档哈希"""
    manager = DIDManager()
    controller = "0x1234567890abcdef"
    did = manager.generate_did(controller)
    
    doc1 = manager.create_document(did=did, controller=controller)
    doc2 = manager.create_document(did=did, controller=controller)
    
    hash1 = manager.hash_document(doc1)
    hash2 = manager.hash_document(doc2)
    
    # 相同内容应该产生相同哈希
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 哈希长度
    
    print(f"[OK] 文档哈希测试通过")


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("DID 系统测试")
    print("=" * 50)
    print()
    
    try:
        test_generate_did()
        test_verify_did()
        test_create_document()
        test_parse_did()
        test_hash_document()
        
        print()
        print("=" * 50)
        print("[SUCCESS] 所有测试通过！")
        print("=" * 50)
        return True
        
    except AssertionError as e:
        print()
        print("=" * 50)
        print(f"[FAIL] 测试失败：{e}")
        print("=" * 50)
        return False
    except Exception as e:
        print()
        print("=" * 50)
        print(f"[ERROR] 错误：{e}")
        print("=" * 50)
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
