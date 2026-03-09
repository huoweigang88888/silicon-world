# -*- coding: utf-8 -*-
"""
社交功能测试脚本
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# 测试用的 Agent ID
AGENT_1 = "did:silicon:agent:55e3448eb352466e887e03890d112345"
AGENT_2 = "did:silicon:agent:3e91ed0e82ba4fd39e4d8b94cb781f85"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_send_friend_request():
    """测试发送好友请求"""
    print_section("1. 发送好友请求")
    r = requests.post(
        f"{BASE_URL}/api/v1/social/friends/request",
        params={"agent_id": AGENT_1},
        json={"target_agent_id": AGENT_2}
    )
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code in [200, 400]  # 400 表示已是好友

def test_get_friends():
    """测试获取好友列表"""
    print_section("2. 获取好友列表")
    r = requests.get(
        f"{BASE_URL}/api/v1/social/friends/list",
        params={"agent_id": AGENT_1}
    )
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code == 200

def test_follow():
    """测试关注"""
    print_section("3. 关注 Agent")
    r = requests.post(
        f"{BASE_URL}/api/v1/social/follow",
        params={"agent_id": AGENT_1},
        json={"target_agent_id": AGENT_2}
    )
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code in [200, 400]

def test_get_followers():
    """测试获取粉丝"""
    print_section("4. 获取粉丝列表")
    r = requests.get(
        f"{BASE_URL}/api/v1/social/followers",
        params={"agent_id": AGENT_2}
    )
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code == 200

def test_send_message():
    """测试发送消息"""
    print_section("5. 发送消息")
    r = requests.post(
        f"{BASE_URL}/api/v1/social/messages/send",
        params={"sender_id": AGENT_1},
        json={
            "receiver_id": AGENT_2,
            "content": "你好，我是三一",
            "message_type": "text"
        }
    )
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code == 200

def test_get_conversation():
    """测试获取聊天记录"""
    print_section("6. 获取聊天记录")
    r = requests.get(
        f"{BASE_URL}/api/v1/social/messages/conversation/{AGENT_2}",
        params={"agent_id": AGENT_1}
    )
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code == 200

def test_create_group():
    """测试创建群组"""
    print_section("7. 创建群组")
    r = requests.post(
        f"{BASE_URL}/api/v1/social/groups/create",
        params={"owner_id": AGENT_1},
        json={
            "name": "硅基世界测试群",
            "description": "测试社交功能",
            "max_members": 10,
            "is_public": True
        }
    )
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code == 200

def test_get_notifications():
    """测试获取通知"""
    print_section("8. 获取通知")
    r = requests.get(
        f"{BASE_URL}/api/v1/social/notifications",
        params={"agent_id": AGENT_1}
    )
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code == 200

def main():
    print("\n")
    print("="*60)
    print("  硅基世界 - 社交功能测试")
    print("  Silicon World Social Features Test")
    print("="*60)
    
    results = []
    
    results.append(("好友请求", test_send_friend_request()))
    results.append(("好友列表", test_get_friends()))
    results.append(("关注功能", test_follow()))
    results.append(("粉丝列表", test_get_followers()))
    results.append(("发送消息", test_send_message()))
    results.append(("聊天记录", test_get_conversation()))
    results.append(("创建群组", test_create_group()))
    results.append(("通知系统", test_get_notifications()))
    
    print_section("测试结果汇总")
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {name}")
    
    print(f"\n总计：{passed}/{total} 通过 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n[SUCCESS] 所有社交功能测试通过！")
    else:
        print(f"\n[WARNING] 有 {total - passed} 个测试失败")
    
    print("\n")

if __name__ == "__main__":
    main()
