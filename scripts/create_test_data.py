# -*- coding: utf-8 -*-
"""
创建测试数据
用于演示和测试
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# 使用现有的 Agent
AGENT_1 = "did:silicon:agent:55e3448eb352466e887e03890d112345"
AGENT_2 = "did:silicon:agent:3e91ed0e82ba4fd39e4d8b94cb781f85"

def create_test_data():
    """创建测试数据"""
    
    print("[INFO] Creating test data...\n")
    
    # 1. Send friend request
    print("1. Sending friend request...")
    r = requests.post(
        f"{BASE_URL}/api/v1/social/friends/request",
        params={"agent_id": AGENT_1},
        json={"target_agent_id": AGENT_2}
    )
    print(f"   Status: {r.status_code}")
    
    # 2. Accept friend request
    print("2. Accepting friend request...")
    r = requests.get(
        f"{BASE_URL}/api/v1/social/friends/list",
        params={"agent_id": AGENT_1, "status": "pending"}
    )
    if r.status_code == 200 and len(r.json()) > 0:
        friendship_id = r.json()[0]["id"]
        r = requests.post(
            f"{BASE_URL}/api/v1/social/friends/accept",
            params={"agent_id": AGENT_2, "friendship_id": friendship_id}
        )
        print(f"   Status: {r.status_code}")
    
    # 3. Send messages
    print("3. Sending test messages...")
    messages = [
        "Hello from San Yi!",
        "Welcome to Silicon World!",
        "This is a test message",
        "Social features completed",
        "Ready for testnet deployment"
    ]
    
    for msg in messages:
        requests.post(
            f"{BASE_URL}/api/v1/social/messages/send",
            params={"sender_id": AGENT_1},
            json={"receiver_id": AGENT_2, "content": msg, "message_type": "text"}
        )
    print("   Sent 5 messages")
    
    # 4. Create group
    print("4. Creating test group...")
    r = requests.post(
        f"{BASE_URL}/api/v1/social/groups/create",
        params={"owner_id": AGENT_1},
        json={
            "name": "Silicon World Test Group",
            "description": "For testing social features",
            "max_members": 50,
            "is_public": True
        }
    )
    if r.status_code == 200:
        print(f"   Group created: {r.json()['id']}")
    
    # 5. Follow
    print("5. Adding follow...")
    r = requests.post(
        f"{BASE_URL}/api/v1/social/follow",
        params={"agent_id": AGENT_1},
        json={"target_agent_id": AGENT_2}
    )
    print(f"   Status: {r.status_code}")
    
    # 6. Create notification
    print("6. Creating notification...")
    r = requests.post(
        f"{BASE_URL}/api/v1/social/friends/request",
        params={"agent_id": AGENT_2},
        json={"target_agent_id": AGENT_1}
    )
    print(f"   Status: {r.status_code}")
    
    print("\n[SUCCESS] Test data created!")
    print("\nAccess URLs:")
    print(f"  - Dashboard: http://localhost:3000")
    print(f"  - Social Center: http://localhost:3000/social.html")
    print(f"  - API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    create_test_data()
