"""
压力测试脚本

测试 API 性能、并发处理能力、响应时间
"""

import asyncio
import aiohttp
import time
import statistics
from typing import Dict, List, Any
from datetime import datetime
import json


class PressureTester:
    """
    压力测试器
    
    测试 API 端点在不同并发下的性能表现
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: Dict[str, List[float]] = {}
    
    async def request(self, session: aiohttp.ClientSession, method: str, endpoint: str) -> Dict[str, Any]:
        """
        发送单个请求
        
        Args:
            session: aiohttp 会话
            method: HTTP 方法
            endpoint: API 端点
        
        Returns:
            请求结果
        """
        url = f"{self.base_url}{endpoint}"
        start = time.time()
        
        try:
            async with session.request(method, url) as response:
                duration = (time.time() - start) * 1000  # 毫秒
                status = response.status
                await response.read()
                
                return {
                    "success": True,
                    "status": status,
                    "duration_ms": duration,
                    "error": None
                }
        except Exception as e:
            duration = (time.time() - start) * 1000
            return {
                "success": False,
                "status": 0,
                "duration_ms": duration,
                "error": str(e)
            }
    
    async def stress_test(
        self,
        endpoint: str,
        method: str = "GET",
        concurrent_users: int = 10,
        requests_per_user: int = 10
    ) -> Dict[str, Any]:
        """
        压力测试
        
        Args:
            endpoint: API 端点
            method: HTTP 方法
            concurrent_users: 并发用户数
            requests_per_user: 每个用户请求数
        
        Returns:
            测试结果
        """
        print(f"\n[TEST] Endpoint: {endpoint}")
        print(f"   Concurrent Users: {concurrent_users}")
        print(f"   Requests per User: {requests_per_user}")
        print(f"   Total Requests: {concurrent_users * requests_per_user}")
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for _ in range(concurrent_users):
                for _ in range(requests_per_user):
                    tasks.append(self.request(session, method, endpoint))
            
            start_time = time.time()
            results = await asyncio.gather(*tasks)
            total_time = time.time() - start_time
        
        # 分析结果
        durations = [r["duration_ms"] for r in results if r["success"]]
        success_count = sum(1 for r in results if r["success"])
        fail_count = len(results) - success_count
        
        if durations:
            stats = {
                "endpoint": endpoint,
                "method": method,
                "total_requests": len(results),
                "success_count": success_count,
                "fail_count": fail_count,
                "success_rate": f"{success_count / len(results) * 100:.1f}%",
                "total_time_seconds": round(total_time, 2),
                "requests_per_second": round(len(results) / total_time, 2),
                "min_ms": round(min(durations), 2),
                "max_ms": round(max(durations), 2),
                "avg_ms": round(statistics.mean(durations), 2),
                "median_ms": round(statistics.median(durations), 2),
                "p95_ms": round(statistics.quantiles(durations, n=20)[18], 2) if len(durations) >= 20 else round(max(durations), 2),
                "p99_ms": round(statistics.quantiles(durations, n=100)[98], 2) if len(durations) >= 100 else round(max(durations), 2)
            }
        else:
            stats = {
                "endpoint": endpoint,
                "method": method,
                "total_requests": len(results),
                "success_count": 0,
                "fail_count": len(results),
                "error": "All requests failed"
            }
        
        return stats
    
    async def run_all_tests(self) -> List[Dict[str, Any]]:
        """
        运行所有测试
        
        Returns:
            所有测试结果
        """
        # 定义测试端点
        endpoints = [
            ("/api/v1/health", "GET", 50, 10),  # 健康检查 - 低负载
            ("/api/v1/agents", "GET", 20, 5),   # Agent 列表 - 中负载
            ("/api/v1/gamification/statistics", "GET", 20, 5),  # 游戏化统计 - 中负载
            ("/api/v1/optimization/report", "GET", 10, 3),  # 性能报告 - 低负载
        ]
        
        all_results = []
        
        for endpoint, method, concurrent, requests in endpoints:
            try:
                result = await self.stress_test(endpoint, method, concurrent, requests)
                all_results.append(result)
                
                # 打印结果
                print(f"\n[RESULT] Test Complete:")
                print(f"   Success Rate: {result.get('success_rate', 'N/A')}")
                if 'avg_ms' in result:
                    print(f"   Avg Response: {result['avg_ms']} ms")
                    print(f"   P95 Response: {result.get('p95_ms', 'N/A')} ms")
                    print(f"   Requests/sec: {result.get('requests_per_second', 'N/A')}")
            except Exception as e:
                print(f"[ERROR] Test Failed: {e}")
                all_results.append({
                    "endpoint": endpoint,
                    "error": str(e)
                })
        
        return all_results
    
    def generate_report(self, results: List[Dict[str, Any]]) -> str:
        """
        生成测试报告
        
        Args:
            results: 测试结果列表
        
        Returns:
            格式化的测试报告
        """
        report = []
        report.append("=" * 60)
        report.append("Silicon World API Pressure Test Report")
        report.append(f"   Generated: {datetime.utcnow().isoformat()}")
        report.append("=" * 60)
        report.append("")
        
        for result in results:
            report.append(f"端点：{result.get('endpoint', 'Unknown')}")
            report.append(f"方法：{result.get('method', 'Unknown')}")
            
            if 'success_rate' in result:
                report.append(f"   总请求：{result['total_requests']}")
                report.append(f"   成功：{result['success_count']}")
                report.append(f"   失败：{result['fail_count']}")
                report.append(f"   成功率：{result['success_rate']}")
                report.append(f"   总耗时：{result['total_time_seconds']} s")
                report.append(f"   吞吐量：{result['requests_per_second']} req/s")
                report.append(f"   最小响应：{result.get('min_ms', 'N/A')} ms")
                report.append(f"   最大响应：{result.get('max_ms', 'N/A')} ms")
                report.append(f"   平均响应：{result.get('avg_ms', 'N/A')} ms")
                report.append(f"   中位响应：{result.get('median_ms', 'N/A')} ms")
                report.append(f"   P95 响应：{result.get('p95_ms', 'N/A')} ms")
                report.append(f"   P99 响应：{result.get('p99_ms', 'N/A')} ms")
            else:
                report.append(f"   错误：{result.get('error', 'Unknown')}")
            
            report.append("")
        
        # 总结
        report.append("=" * 60)
        report.append("Summary")
        report.append("=" * 60)
        
        total_requests = sum(r.get('total_requests', 0) for r in results)
        total_success = sum(r.get('success_count', 0) for r in results)
        overall_success_rate = f"{total_success / total_requests * 100:.1f}%" if total_requests > 0 else "N/A"
        
        report.append(f"Total Requests: {total_requests}")
        report.append(f"Successful: {total_success}")
        report.append(f"Success Rate: {overall_success_rate}")
        
        avg_response_times = [r.get('avg_ms', 0) for r in results if 'avg_ms' in r]
        if avg_response_times:
            report.append(f"Avg Response Time: {statistics.mean(avg_response_times):.2f} ms")
        
        report.append("")
        report.append("Silicon World - Created by Agents and Humans!")
        
        return "\n".join(report)


async def main():
    """主函数"""
    print("Silicon World API Pressure Test")
    print(f"Start Time: {datetime.utcnow().isoformat()}")
    
    tester = PressureTester("http://localhost:8000")
    
    # 运行测试
    results = await tester.run_all_tests()
    
    # 生成报告
    report = tester.generate_report(results)
    print("\n" + report)
    
    # 保存报告
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    report_file = f"pressure_test_{timestamp}.md"
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n[INFO] Report saved: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())
