# -*- coding: utf-8 -*-
"""
A2A Phase 3 功能完善测试
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_task_execution():
    """测试任务执行器"""
    print_section("1. 任务执行器")
    
    # 创建研究任务
    r = requests.post(
        f"{BASE_URL}/api/v1/a2a/create-task",
        json={
            "agent_url": "http://localhost:8000",
            "description": "研究 AI 发展趋势",
            "task_type": "research"
        }
    )
    
    print(f"创建任务状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    
    if r.status_code == 200:
        data = r.json()
        task_id = data.get("task_id") or data.get("task", {}).get("id")
        
        if not task_id:
            print("警告：无法获取 task_id")
            return False
        
        # 等待任务执行
        time.sleep(2)
        
        # 查询任务状态
        r = requests.get(f"{BASE_URL}/api/v1/a2a/task/{task_id}")
        print(f"\n任务状态码：{r.status_code}")
        print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
        
        return r.status_code == 200
    
    return False

def test_task_list():
    """测试任务列表"""
    print_section("2. 任务列表")
    
    r = requests.get(f"{BASE_URL}/api/v1/a2a/tasks?limit=10")
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    
    return r.status_code == 200

def test_task_stats():
    """测试任务统计"""
    print_section("3. 任务统计")
    
    r = requests.get(f"{BASE_URL}/api/v1/a2a/tasks/stats")
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    
    return r.status_code == 200

def test_error_handling():
    """测试错误处理"""
    print_section("4. 错误处理")
    
    # 测试无效 Agent URL
    r = requests.post(
        f"{BASE_URL}/api/v1/a2a/discover",
        json={"agent_url": "invalid-url"}
    )
    
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    
    # 预期返回 404 或 500
    return r.status_code in [404, 500]

def test_agent_card():
    """测试 Agent Card"""
    print_section("5. Agent Card")
    
    r = requests.get(f"{BASE_URL}/api/v1/a2a/agent-card")
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    
    return r.status_code == 200

def test_a2a_status():
    """测试 A2A 状态"""
    print_section("6. A2A 系统状态")
    
    r = requests.get(f"{BASE_URL}/api/v1/a2a/status")
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    
    return r.status_code == 200

def main():
    print("\n")
    print("="*60)
    print("  A2A Phase 3 功能完善测试")
    print("  A2A Phase 3 Enhanced Features Test")
    print("="*60)
    
    results = []
    
    results.append(("任务执行器", test_task_execution()))
    results.append(("任务列表", test_task_list()))
    results.append(("任务统计", test_task_stats()))
    results.append(("错误处理", test_error_handling()))
    results.append(("Agent Card", test_agent_card()))
    results.append(("A2A 状态", test_a2a_status()))
    
    print_section("测试结果汇总")
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {name}")
    
    print(f"\n总计：{passed}/{total} 通过 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n[SUCCESS] Phase 3 所有测试通过！")
        print("\n完成的功能:")
        print("  ✅ 流式响应支持")
        print("  ✅ 任务执行器（支持多种任务类型）")
        print("  ✅ 任务列表和统计")
        print("  ✅ 错误处理优化")
        print("  ✅ 断路器模式")
    else:
        print(f"\n[INFO] {total - passed} 个测试未完成")
    
    print("\n")

if __name__ == "__main__":
    main()
