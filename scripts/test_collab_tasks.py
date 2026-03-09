# -*- coding: utf-8 -*-
"""
群组任务协作测试
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# 测试用 Agent ID
AGENT_1 = "did:silicon:agent:55e3448eb352466e887e03890d112345"
AGENT_2 = "did:silicon:agent:3e91ed0e82ba4fd39e4d8b94cb781f85"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_create_collab_task():
    """测试创建协作任务"""
    print_section("1. 创建协作任务")
    
    r = requests.post(
        f"{BASE_URL}/api/v1/collab-tasks/create",
        json={
            "title": "AI 研究报告",
            "description": "多个 Agent 协作完成 AI 发展趋势研究",
            "agent_ids": [AGENT_1, AGENT_2],
            "task_type": "research",
            "deadline": "2026-03-15T00:00:00Z"
        }
    )
    
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    
    return r.status_code == 200, r.json().get("id") if r.status_code == 200 else None

def test_get_task(task_id):
    """测试获取任务详情"""
    print_section("2. 获取任务详情")
    
    if not task_id:
        print("跳过：无任务 ID")
        return True
    
    r = requests.get(f"{BASE_URL}/api/v1/collab-tasks/{task_id}")
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    
    return r.status_code == 200

def test_list_tasks():
    """测试列出任务"""
    print_section("3. 列出协作任务")
    
    r = requests.get(f"{BASE_URL}/api/v1/collab-tasks?limit=10")
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    
    return r.status_code == 200

def test_update_progress(task_id):
    """测试更新子任务进度"""
    print_section("4. 更新子任务进度")
    
    if not task_id:
        print("跳过：无任务 ID")
        return True
    
    # 先获取任务获取子任务 ID
    task_r = requests.get(f"{BASE_URL}/api/v1/collab-tasks/{task_id}")
    if task_r.status_code != 200:
        return False
    
    task = task_r.json()
    if task["subtasks"]:
        subtask_id = task["subtasks"][0]["id"]
        
        r = requests.post(
            f"{BASE_URL}/api/v1/collab-tasks/{task_id}/subtask/{subtask_id}/progress",
            params={"progress": 50, "status": "processing"}
        )
        
        print(f"状态码：{r.status_code}")
        print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
        
        return r.status_code == 200
    
    return True

def test_get_stats():
    """测试获取统计"""
    print_section("5. 获取协作任务统计")
    
    r = requests.get(f"{BASE_URL}/api/v1/collab-tasks/stats")
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    
    return r.status_code == 200

def main():
    print("\n")
    print("="*60)
    print("  群组任务协作测试")
    print("  Collaborative Task Test")
    print("="*60)
    
    results = []
    
    # 创建任务
    success, task_id = test_create_collab_task()
    results.append(("创建协作任务", success))
    
    # 获取任务
    results.append(("获取任务详情", test_get_task(task_id)))
    
    # 列出任务
    results.append(("列出任务", test_list_tasks()))
    
    # 更新进度
    results.append(("更新进度", test_update_progress(task_id)))
    
    # 获取统计
    results.append(("获取统计", test_get_stats()))
    
    print_section("测试结果汇总")
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {name}")
    
    print(f"\n总计：{passed}/{total} 通过 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n[SUCCESS] 群组任务协作测试全部通过！")
    else:
        print(f"\n[INFO] {total - passed} 个测试未完成")
    
    print("\n")

if __name__ == "__main__":
    main()
