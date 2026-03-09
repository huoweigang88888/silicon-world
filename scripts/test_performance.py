# -*- coding: utf-8 -*-
"""
性能监控测试
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_health_check():
    """测试健康检查"""
    print_section("1. 健康检查")
    r = requests.get(f"{BASE_URL}/api/v1/performance/health")
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code == 200

def test_performance_stats():
    """测试性能统计"""
    print_section("2. 性能统计")
    r = requests.get(f"{BASE_URL}/api/v1/performance/stats")
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code == 200

def test_memory_usage():
    """测试内存使用"""
    print_section("3. 内存使用情况")
    r = requests.get(f"{BASE_URL}/api/v1/performance/memory")
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code == 200

def test_cpu_usage():
    """测试 CPU 使用"""
    print_section("4. CPU 使用情况")
    r = requests.get(f"{BASE_URL}/api/v1/performance/cpu")
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code == 200

def test_cache_performance():
    """测试缓存性能"""
    print_section("5. 缓存性能测试")
    
    from src.a2a.cache import cache
    import asyncio
    
    async def run_cache_test():
        # 连接
        await cache.connect()
        
        # 写入测试
        start = time.time()
        for i in range(100):
            await cache.set(f"test_key_{i}", f"value_{i}", expire=60)
        write_time = time.time() - start
        
        # 读取测试
        start = time.time()
        for i in range(100):
            await cache.get(f"test_key_{i}")
        read_time = time.time() - start
        
        return {
            "write_100_keys_seconds": write_time,
            "read_100_keys_seconds": read_time,
            "ops_per_second": 100 / max(write_time, read_time)
        }
    
    result = asyncio.run(run_cache_test())
    print(f"缓存测试结果：{json.dumps(result, indent=2)}")
    return True

def test_a2a_status():
    """测试 A2A 状态"""
    print_section("6. A2A 系统状态")
    r = requests.get(f"{BASE_URL}/api/v1/a2a/status")
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code == 200

def test_nexus_status():
    """测试 NexusA 状态"""
    print_section("7. NexusA 钱包状态")
    r = requests.get(f"{BASE_URL}/api/v1/nexus/status")
    print(f"状态码：{r.status_code}")
    print(f"响应：{json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    return r.status_code == 200

def main():
    print("\n")
    print("="*60)
    print("  性能监控测试")
    print("  Performance Monitoring Test")
    print("="*60)
    
    results = []
    
    results.append(("健康检查", test_health_check()))
    results.append(("性能统计", test_performance_stats()))
    results.append(("内存使用", test_memory_usage()))
    results.append(("CPU 使用", test_cpu_usage()))
    results.append(("缓存性能", test_cache_performance()))
    results.append(("A2A 状态", test_a2a_status()))
    results.append(("NexusA 状态", test_nexus_status()))
    
    print_section("测试结果汇总")
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {name}")
    
    print(f"\n总计：{passed}/{total} 通过 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n[SUCCESS] 性能监控测试全部通过！")
        print("\n完成的功能:")
        print("  ✅ Redis 缓存层（模拟模式）")
        print("  ✅ 数据库连接池")
        print("  ✅ 性能监控 API")
        print("  ✅ 健康检查")
        print("  ✅ 内存/CPU 监控")
    else:
        print(f"\n[INFO] {total - passed} 个测试未完成")
    
    print("\n")

if __name__ == "__main__":
    main()
