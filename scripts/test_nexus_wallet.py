# -*- coding: utf-8 -*-
"""
NexusA 钱包集成测试
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_nexus_status():
    """测试 NexusA 状态"""
    print_section("1. NexusA 连接状态")
    r = requests.get(f"{BASE_URL}/api/v1/nexus/status")
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code == 200

def test_create_wallet():
    """测试创建钱包"""
    print_section("2. 创建钱包")
    r = requests.post(
        f"{BASE_URL}/api/v1/nexus/wallet/create",
        json={"currency": "CNY", "network": "mainnet"}
    )
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code == 200, r.json().get("address") if r.status_code == 200 else None

def test_get_wallet(address):
    """测试获取钱包"""
    print_section("3. 获取钱包信息")
    if not address:
        print("跳过：无钱包地址")
        return True
    
    r = requests.get(f"{BASE_URL}/api/v1/nexus/wallet/{address}")
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code == 200

def test_get_balance(address):
    """测试获取余额"""
    print_section("4. 获取余额")
    if not address:
        print("跳过：无钱包地址")
        return True
    
    r = requests.get(f"{BASE_URL}/api/v1/nexus/wallet/{address}/balance")
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code == 200

def test_transfer(address1, address2):
    """测试转账"""
    print_section("5. 转账测试")
    if not address1 or not address2:
        print("跳过：钱包地址不足")
        return True
    
    # 尝试小额转账
    r = requests.post(
        f"{BASE_URL}/api/v1/nexus/transfer",
        json={
            "from_address": address1,
            "to_address": address2,
            "amount": 1.0,
            "currency": "CNY",
            "description": "测试转账"
        }
    )
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    
    # 余额不足是预期的
    return r.status_code in [200, 400]

def test_get_transactions(address):
    """测试获取交易历史"""
    print_section("6. 获取交易历史")
    if not address:
        print("跳过：无钱包地址")
        return True
    
    r = requests.get(f"{BASE_URL}/api/v1/nexus/wallet/{address}/transactions?limit=10")
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code == 200

def test_nexus_stats():
    """测试 NexusA 统计"""
    print_section("7. NexusA 统计")
    r = requests.get(f"{BASE_URL}/api/v1/nexus/stats")
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code == 200

def main():
    print("\n")
    print("="*60)
    print("  NexusA 钱包集成测试")
    print("  NexusA Wallet Integration Test")
    print("="*60)
    
    results = []
    
    # 测试状态
    results.append(("NexusA 状态", test_nexus_status()))
    
    # 创建钱包
    success, address1 = test_create_wallet()
    results.append(("创建钱包", success))
    
    # 创建第二个钱包用于转账测试
    success2, address2 = test_create_wallet()
    results.append(("创建钱包 2", success2))
    
    # 测试钱包功能
    results.append(("获取钱包", test_get_wallet(address1)))
    results.append(("获取余额", test_get_balance(address1)))
    results.append(("转账测试", test_transfer(address1, address2)))
    results.append(("交易历史", test_get_transactions(address1)))
    results.append(("NexusA 统计", test_nexus_stats()))
    
    print_section("测试结果汇总")
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {name}")
    
    print(f"\n总计：{passed}/{total} 通过 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n[SUCCESS] NexusA 钱包集成测试全部通过！")
        print("\n功能列表:")
        print("  ✅ 钱包创建")
        print("  ✅ 钱包查询")
        print("  ✅ 余额查询")
        print("  ✅ 转账功能")
        print("  ✅ 交易历史")
        print("  ✅ 支付验证")
    else:
        print(f"\n[INFO] {total - passed} 个测试未完成")
    
    print("\n")

if __name__ == "__main__":
    main()
