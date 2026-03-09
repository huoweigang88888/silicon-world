# -*- coding: utf-8 -*-
"""
文件上传和消息已读回执测试
"""

import requests

BASE_URL = "http://localhost:8000"
AGENT_1 = "did:silicon:agent:55e3448eb352466e887e03890d112345"
AGENT_2 = "did:silicon:agent:3e91ed0e82ba4fd39e4d8b94cb781f85"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_upload_image():
    """测试上传图片"""
    print_section("1. 上传图片")
    
    # 创建测试图片
    test_image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
    
    files = {'file': ('test.png', test_image, 'image/png')}
    r = requests.post(f"{BASE_URL}/api/v1/files/upload/image", files=files)
    
    print(f"状态码：{r.status_code}")
    print(f"响应：{r.json()}")
    
    return r.status_code == 200, r.json().get('file_url') if r.status_code == 200 else None

def test_send_image_message(file_url):
    """测试发送图片消息"""
    print_section("2. 发送图片消息")
    
    r = requests.post(
        f"{BASE_URL}/api/v1/social/messages/send",
        params={"sender_id": AGENT_1},
        json={
            "receiver_id": AGENT_2,
            "content": "这是一张图片",
            "message_type": "image",
            "file_url": file_url
        }
    )
    
    print(f"状态码：{r.status_code}")
    print(f"响应：{r.json()}")
    
    return r.status_code == 200

def test_get_unread_count():
    """测试获取未读消息数量"""
    print_section("3. 获取未读消息数量")
    
    r = requests.get(
        f"{BASE_URL}/api/v1/social/messages/unread/count",
        params={"agent_id": AGENT_2}
    )
    
    print(f"状态码：{r.status_code}")
    print(f"响应：{r.json()}")
    
    return r.status_code == 200

def test_mark_conversation_read():
    """测试标记对话为已读"""
    print_section("4. 标记对话为已读")
    
    r = requests.post(
        f"{BASE_URL}/api/v1/social/messages/mark-conversation-read",
        params={"agent_id": AGENT_2, "other_id": AGENT_1}
    )
    
    print(f"状态码：{r.status_code}")
    print(f"响应：{r.json()}")
    
    return r.status_code == 200

def test_verify_read_status():
    """验证已读状态"""
    print_section("5. 验证已读状态")
    
    # 获取未读数量，应该为 0
    r = requests.get(
        f"{BASE_URL}/api/v1/social/messages/unread/count",
        params={"agent_id": AGENT_2}
    )
    
    print(f"状态码：{r.status_code}")
    print(f"响应：{r.json()}")
    
    return r.status_code == 200 and r.json().get('unread_count', 1) == 0

def main():
    print("\n")
    print("="*60)
    print("  文件上传和消息已读测试")
    print("  File Upload & Read Receipt Test")
    print("="*60)
    
    results = []
    
    # 测试图片上传
    success, file_url = test_upload_image()
    results.append(("图片上传", success))
    
    if success:
        # 测试发送图片消息
        results.append(("发送图片消息", test_send_image_message(file_url)))
    
    # 测试未读消息
    results.append(("未读消息数量", test_get_unread_count()))
    
    # 测试标记已读
    results.append(("标记对话已读", test_mark_conversation_read()))
    
    # 验证已读状态
    results.append(("验证已读状态", test_verify_read_status()))
    
    print_section("测试结果汇总")
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {name}")
    
    print(f"\n总计：{passed}/{total} 通过 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n[SUCCESS] 所有测试通过！")
    else:
        print(f"\n[INFO] {total - passed} 个测试未完成")
    
    print("\n")

if __name__ == "__main__":
    main()
