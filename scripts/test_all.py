# -*- coding: utf-8 -*-
"""
硅基世界 - 功能测试脚本
测试所有核心功能
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    """打印章节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_health():
    """测试健康检查"""
    print_section("1. 健康检查")
    r = requests.get(f"{BASE_URL}/health")
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code == 200

def test_templates():
    """测试模板系统"""
    print_section("2. 模板系统")
    r = requests.get(f"{BASE_URL}/api/v1/templates")
    print(f"状态码：{r.status_code}")
    data = r.json()
    print(f"模板数量：{data.get('count', 0)}")
    print(f"\n可用模板:")
    for t in data.get('templates', []):
        print(f"  - [{t.get('id', '')}] {t.get('name', '')}: {t.get('description', '')[:50]}...")
    return r.status_code == 200

def test_agents_list():
    """测试 Agent 列表"""
    print_section("3. Agent 列表")
    r = requests.get(f"{BASE_URL}/api/v1/agents")
    print(f"状态码：{r.status_code}")
    if r.status_code == 200:
        agents = r.json()
        print(f"Agent 总数：{len(agents)}")
        for a in agents[:3]:  # 只显示前 3 个
            print(f"  - {a.get('name', '')} ({a.get('id', '')[:30]}...)")
            print(f"    类型：{a.get('agent_type', '')}, 状态：{a.get('status', '')}")
    return r.status_code == 200

def test_heartbeat_stats():
    """测试心跳统计"""
    print_section("4. 心跳统计")
    r = requests.get(f"{BASE_URL}/api/v1/agents/heartbeat/stats")
    print(f"状态码：{r.status_code}")
    if r.status_code == 200:
        print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code == 200

def test_invocation_logs():
    """测试调用日志"""
    print_section("5. 调用日志")
    # 先获取一个 Agent
    r = requests.get(f"{BASE_URL}/api/v1/agents")
    if r.status_code == 200:
        agents = r.json()
        if agents:
            agent_id = agents[0]['id']
            print(f"测试 Agent: {agent_id[:40]}...")
            
            # 获取调用日志
            r = requests.get(f"{BASE_URL}/api/v1/agents/{agent_id}/invocations")
            print(f"调用日志状态码：{r.status_code}")
            if r.status_code == 200:
                logs = r.json()
                print(f"调用记录数：{len(logs)}")
    return True

def test_dashboard():
    """测试 Dashboard 可访问性"""
    print_section("6. Dashboard 可访问性")
    try:
        r = requests.get("http://localhost:3000", timeout=5)
        print(f"状态码：{r.status_code}")
        print(f"Dashboard: http://localhost:3000")
        return r.status_code == 200
    except Exception as e:
        print(f"Dashboard 访问失败：{e}")
        return False

def main():
    """主测试函数"""
    print("\n")
    print("╔══════════════════════════════════════════════════╗")
    print("║                                                  ║")
    print("║       硅基世界 - 功能测试报告                    ║")
    print("║       Silicon World Function Test                ║")
    print("║                                                  ║")
    print(f"║       测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}              ║")
    print("║                                                  ║")
    print("╚══════════════════════════════════════════════════╝")
    
    results = []
    
    # 执行测试
    results.append(("健康检查", test_health()))
    results.append(("模板系统", test_templates()))
    results.append(("Agent 列表", test_agents_list()))
    results.append(("心跳统计", test_heartbeat_stats()))
    results.append(("调用日志", test_invocation_logs()))
    results.append(("Dashboard", test_dashboard()))
    
    # 汇总结果
    print_section("测试结果汇总")
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! System is running well!")
    else:
        print(f"\n[WARNING] {total - passed} tests failed, please check")
    
    print("\n")

if __name__ == "__main__":
    main()
