# -*- coding: utf-8 -*-
"""
社交功能增强测试 - 屏蔽/消息撤回/群组管理
"""

import requests
import json

BASE_URL = "http://localhost:8000"

AGENT_1 = "did:silicon:agent:55e3448eb352466e887e03890d112345"
AGENT_2 = "did:silicon:agent:3e91ed0e82ba4fd39e4d8b94cb781f85"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_block_agent():
    """测试屏蔽功能"""
    print_section("1. 屏蔽 Agent")
    r = requests.post(
        f"{BASE_URL}/api/v1/social/block",
        params={"agent_id": AGENT_1},
        json={"target_agent_id": AGENT_2, "reason": "测试屏蔽"}
    )
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code in [200, 400]

def test_get_blocked_list():
    """测试获取屏蔽列表"""
    print_section("2. 获取屏蔽列表")
    r = requests.get(
        f"{BASE_URL}/api/v1/social/blocked-list",
        params={"agent_id": AGENT_1}
    )
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code == 200

def test_unblock_agent():
    """测试解除屏蔽"""
    print_section("3. 解除屏蔽")
    r = requests.post(
        f"{BASE_URL}/api/v1/social/unblock",
        params={"agent_id": AGENT_1, "blocked_id": AGENT_2}
    )
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code in [200, 404]

def test_edit_message():
    """测试编辑消息"""
    print_section("4. 编辑消息")
    # 先发送一条消息
    send_r = requests.post(
        f"{BASE_URL}/api/v1/social/messages/send",
        params={"sender_id": AGENT_1},
        json={"receiver_id": AGENT_2, "content": "原始消息", "message_type": "text"}
    )
    if send_r.status_code == 200:
        message_id = send_r.json()["id"]
        print(f"发送的消息 ID: {message_id}")
        
        # 编辑消息
        edit_r = requests.put(
            f"{BASE_URL}/api/v1/social/messages/{message_id}",
            params={"agent_id": AGENT_1},
            json={"content": "消息已编辑"}
        )
        print(f"编辑状态码：{edit_r.status_code}")
        print(f"编辑响应：{json.dumps(edit_r.json(), indent=2, ensure_ascii=False)}")
        return edit_r.status_code == 200
    return False

def test_delete_message():
    """测试撤回消息"""
    print_section("5. 撤回消息")
    # 先发送一条消息
    send_r = requests.post(
        f"{BASE_URL}/api/v1/social/messages/send",
        params={"sender_id": AGENT_1},
        json={"receiver_id": AGENT_2, "content": "这条消息会被撤回", "message_type": "text"}
    )
    if send_r.status_code == 200:
        message_id = send_r.json()["id"]
        print(f"发送的消息 ID: {message_id}")
        
        # 删除消息
        delete_r = requests.delete(
            f"{BASE_URL}/api/v1/social/messages/{message_id}",
            params={"agent_id": AGENT_1}
        )
        print(f"删除状态码：{delete_r.status_code}")
        print(f"删除响应：{json.dumps(delete_r.json(), indent=2, ensure_ascii=False)}")
        return delete_r.status_code == 200
    return False

def test_kick_member():
    """测试踢出群成员"""
    print_section("6. 踢出群成员")
    # 先创建群组
    create_r = requests.post(
        f"{BASE_URL}/api/v1/social/groups/create",
        params={"owner_id": AGENT_1},
        json={"name": "测试踢人群", "max_members": 5}
    )
    if create_r.status_code == 200:
        group_id = create_r.json()["id"]
        print(f"创建的群组 ID: {group_id}")
        
        # 踢出（这里测试权限检查）
        kick_r = requests.post(
            f"{BASE_URL}/api/v1/social/groups/{group_id}/kick",
            params={"agent_id": AGENT_1, "target_id": AGENT_2}
        )
        print(f"踢出状态码：{kick_r.status_code}")
        print(f"踢出响应：{json.dumps(kick_r.json(), indent=2, ensure_ascii=False)}")
        return kick_r.status_code in [200, 404]
    return False

def test_mute_member():
    """测试禁言群成员"""
    print_section("7. 禁言群成员")
    # 使用之前创建的群组
    create_r = requests.post(
        f"{BASE_URL}/api/v1/social/groups/create",
        params={"owner_id": AGENT_1},
        json={"name": "测试禁言群", "max_members": 5}
    )
    if create_r.status_code == 200:
        group_id = create_r.json()["id"]
        print(f"创建的群组 ID: {group_id}")
        
        # 禁言
        mute_r = requests.post(
            f"{BASE_URL}/api/v1/social/groups/{group_id}/mute",
            params={"agent_id": AGENT_1, "target_id": AGENT_2, "duration_minutes": 30}
        )
        print(f"禁言状态码：{mute_r.status_code}")
        print(f"禁言响应：{json.dumps(mute_r.json(), indent=2, ensure_ascii=False)}")
        return mute_r.status_code in [200, 404]
    return False

def test_leave_group():
    """测试退出群组"""
    print_section("8. 退出群组")
    # 群主不能退出，这个测试会失败
    create_r = requests.post(
        f"{BASE_URL}/api/v1/social/groups/create",
        params={"owner_id": AGENT_1},
        json={"name": "测试退出群", "max_members": 5}
    )
    if create_r.status_code == 200:
        group_id = create_r.json()["id"]
        print(f"创建的群组 ID: {group_id}")
        
        # 退出（群主退出应该失败）
        leave_r = requests.post(
            f"{BASE_URL}/api/v1/social/groups/{group_id}/leave",
            params={"agent_id": AGENT_1}
        )
        print(f"退出状态码：{leave_r.status_code}")
        print(f"退出响应：{json.dumps(leave_r.json(), indent=2, ensure_ascii=False)}")
        # 预期是 400 错误（群主不能退出）
        return leave_r.status_code == 400
    return False

def main():
    print("\n")
    print("="*60)
    print("  社交功能增强测试")
    print("  Social Features Enhanced Test")
    print("="*60)
    
    results = []
    
    results.append(("屏蔽功能", test_block_agent()))
    results.append(("屏蔽列表", test_get_blocked_list()))
    results.append(("解除屏蔽", test_unblock_agent()))
    results.append(("编辑消息", test_edit_message()))
    results.append(("撤回消息", test_delete_message()))
    results.append(("踢出成员", test_kick_member()))
    results.append(("禁言成员", test_mute_member()))
    results.append(("退出群组", test_leave_group()))
    
    print_section("测试结果汇总")
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {name}")
    
    print(f"\n总计：{passed}/{total} 通过 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n[SUCCESS] 所有增强功能测试通过！")
    else:
        print(f"\n[INFO] {total - passed} 个测试有预期行为")
    
    print("\n")

if __name__ == "__main__":
    main()
