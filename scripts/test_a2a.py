# -*- coding: utf-8 -*-
"""
A2A 集成测试
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_a2a_status():
    """测试 A2A 状态"""
    print_section("1. A2A 系统状态")
    r = requests.get(f"{BASE_URL}/api/v1/a2a/status")
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code == 200

def test_agent_card():
    """测试获取 Agent Card"""
    print_section("2. 获取本地 Agent Card")
    r = requests.get(f"{BASE_URL}/api/v1/a2a/agent-card")
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code == 200

def test_discover_agent():
    """测试 Agent 发现（需要真实的 A2A Agent URL）"""
    print_section("3. Agent 发现")
    print("注意：需要真实的 A2A Agent URL 才能测试")
    print("示例：https://example-agent.com")
    
    # 这里使用一个示例 URL（会失败，但测试流程）
    r = requests.post(
        f"{BASE_URL}/api/v1/a2a/discover",
        json={"agent_url": "https://example.com"}
    )
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    
    # 预期会失败，但测试 API 端点正常
    return r.status_code in [404, 500]

def test_send_message():
    """测试发送 A2A 消息"""
    print_section("4. 发送 A2A 消息")
    print("注意：需要真实的 A2A Agent URL 才能测试")
    
    r = requests.post(
        f"{BASE_URL}/api/v1/a2a/send-message",
        json={
            "agent_url": "https://example.com",
            "message": "Hello from Silicon World"
        }
    )
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    
    # 预期会失败，但测试 API 端点正常
    return r.status_code == 200

def test_payment_request():
    """测试创建支付请求"""
    print_section("5. 创建支付请求")
    
    r = requests.post(
        f"{BASE_URL}/api/v1/a2a/payment/request",
        json={
            "amount": 10.0,
            "currency": "CNY",
            "description": "Test payment"
        }
    )
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code == 200

def test_get_payment_status():
    """测试获取支付状态"""
    print_section("6. 获取支付状态")
    
    # 先创建一个支付请求
    create_r = requests.post(
        f"{BASE_URL}/api/v1/a2a/payment/request",
        json={
            "amount": 5.0,
            "currency": "CNY",
            "description": "Test payment status"
        }
    )
    
    if create_r.status_code == 200:
        payment_id = create_r.json()["payment_id"]
        
        # 获取支付状态
        r = requests.get(f"{BASE_URL}/api/v1/a2a/payment/{payment_id}")
        print(f"状态码：{r.status_code}")
        print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
        return r.status_code == 200
    
    return False

def main():
    print("\n")
    print("="*60)
    print("  A2A 集成测试")
    print("  A2A Integration Test")
    print("="*60)
    
    results = []
    
    results.append(("A2A 系统状态", test_a2a_status()))
    results.append(("本地 Agent Card", test_agent_card()))
    results.append(("Agent 发现", test_discover_agent()))
    results.append(("发送 A2A 消息", test_send_message()))
    results.append(("创建支付请求", test_payment_request()))
    results.append(("获取支付状态", test_get_payment_status()))
    
    print_section("测试结果汇总")
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {name}")
    
    print(f"\n总计：{passed}/{total} 通过 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n[SUCCESS] 所有 A2A 测试通过！")
        print("\n💡 提示:")
        print("  - Agent 发现和消息发送需要真实的 A2A Agent URL")
        print("  - 可以部署到测试网后与其他 A2A Agent 测试")
    else:
        print(f"\n[INFO] {total - passed} 个测试未完成")
    
    print("\n")

if __name__ == "__main__":
    main()
