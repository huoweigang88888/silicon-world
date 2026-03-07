"""
性能监控模块

系统性能监控和告警
"""

from typing import Dict, List, Any
from datetime import datetime
import time


class PerformanceMonitor:
    """
    性能监控器
    
    监控系统性能指标
    """
    
    def __init__(self):
        self.metrics: Dict[str, List[Dict[str, Any]]] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.thresholds = {
            "api_response_time": 200,  # ms
            "db_query_time": 50,  # ms
            "memory_usage": 80,  # %
            "cpu_usage": 80,  # %
            "error_rate": 1  # %
        }
    
    def record_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """记录性能指标"""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        self.metrics[metric_name].append({
            "value": value,
            "timestamp": datetime.utcnow(),
            "tags": tags or {}
        })
        
        # 限制历史记录
        if len(self.metrics[metric_name]) > 1000:
            self.metrics[metric_name] = self.metrics[metric_name][-1000:]
        
        # 检查阈值
        self._check_threshold(metric_name, value)
    
    def _check_threshold(self, metric_name: str, value: float):
        """检查是否超过阈值"""
        if metric_name in self.thresholds:
            threshold = self.thresholds[metric_name]
            if value > threshold:
                self._create_alert(metric_name, value, threshold)
    
    def _create_alert(self, metric_name: str, value: float, threshold: float):
        """创建告警"""
        alert = {
            "metric": metric_name,
            "value": value,
            "threshold": threshold,
            "timestamp": datetime.utcnow(),
            "severity": "warning" if value < threshold * 1.5 else "critical"
        }
        self.alerts.append(alert)
        
        # 限制告警数量
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def get_average(self, metric_name: str, minutes: int = 5) -> float:
        """获取平均值"""
        if metric_name not in self.metrics:
            return 0.0
        
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        recent = [m for m in self.metrics[metric_name] if m["timestamp"] > cutoff]
        
        if not recent:
            return 0.0
        
        return sum(m["value"] for m in recent) / len(recent)
    
    def get_percentile(self, metric_name: str, percentile: float, minutes: int = 5) -> float:
        """获取百分位数"""
        if metric_name not in self.metrics:
            return 0.0
        
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        recent = [m["value"] for m in self.metrics[metric_name] if m["timestamp"] > cutoff]
        
        if not recent:
            return 0.0
        
        recent.sort()
        index = int(len(recent) * percentile / 100)
        return recent[min(index, len(recent) - 1)]
    
    def get_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最新告警"""
        return self.alerts[-limit:]
    
    def get_dashboard(self) -> Dict[str, Any]:
        """获取监控仪表板数据"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {
                "api_response_time_avg": self.get_average("api_response_time"),
                "api_response_time_p95": self.get_percentile("api_response_time", 95),
                "db_query_time_avg": self.get_average("db_query_time"),
                "db_query_time_p95": self.get_percentile("db_query_time", 95),
                "requests_per_minute": self.get_average("requests_per_minute"),
                "error_rate": self.get_average("error_rate")
            },
            "alerts": self.get_alerts(5),
            "status": "healthy" if len(self.alerts) == 0 else "warning"
        }


class ResponseTimeMiddleware:
    """
    API 响应时间中间件
    
    记录和监控 API 响应时间
    """
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
    
    def record_request(self, path: str, method: str, response_time: float, status_code: int):
        """记录请求"""
        self.monitor.record_metric("api_response_time", response_time, tags={
            "path": path,
            "method": method,
            "status": str(status_code)
        })
        
        self.monitor.record_metric("requests_per_minute", 1, tags={
            "path": path
        })
        
        if status_code >= 400:
            self.monitor.record_metric("error_rate", 1, tags={
                "status": str(status_code)
            })


# 使用示例
if __name__ == "__main__":
    from datetime import timedelta
    
    monitor = PerformanceMonitor()
    
    # 模拟记录指标
    print("模拟性能监控...")
    for i in range(100):
        monitor.record_metric("api_response_time", 50 + i * 2)
        monitor.record_metric("db_query_time", 20 + i)
    
    # 获取仪表板
    dashboard = monitor.get_dashboard()
    print(f"\n监控仪表板:")
    print(f"  API 平均响应：{dashboard['metrics']['api_response_time_avg']:.2f}ms")
    print(f"  API P95 响应：{dashboard['metrics']['api_response_time_p95']:.2f}ms")
    print(f"  数据库平均：{dashboard['metrics']['db_query_time_avg']:.2f}ms")
    print(f"  数据库 P95: {dashboard['metrics']['db_query_time_p95']:.2f}ms")
    print(f"  系统状态：{dashboard['status']}")
    
    # 获取告警
    alerts = monitor.get_alerts()
    if alerts:
        print(f"\n最新告警：{len(alerts)} 条")
        for alert in alerts[-3:]:
            print(f"  ⚠️ {alert['metric']}: {alert['value']:.2f} > {alert['threshold']}")
