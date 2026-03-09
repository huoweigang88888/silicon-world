"""
API 限流中间件

保护 API 免受滥用和 DDOS 攻击
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib


class RateLimiter:
    """
    限流器
    
    支持多种限流策略
    """
    
    def __init__(self):
        """初始化限流器"""
        # IP 限流：{ip: [(timestamp, count)]}
        self.ip_requests: Dict[str, list] = defaultdict(list)
        
        # 用户限流：{user_id: [(timestamp, count)]}
        self.user_requests: Dict[str, list] = defaultdict(list)
        
        # API 端点限流：{endpoint: [(timestamp, count)]}
        self.endpoint_requests: Dict[str, list] = defaultdict(list)
        
        # 清理间隔（秒）
        self.cleanup_interval = 60
        
        # 上次清理时间
        self.last_cleanup = datetime.utcnow()
    
    def _cleanup_old_records(self, records: list, window_seconds: int) -> list:
        """
        清理过期记录
        
        Args:
            records: 请求记录列表
            window_seconds: 时间窗口（秒）
            
        Returns:
            清理后的记录
        """
        cutoff = datetime.utcnow() - timedelta(seconds=window_seconds)
        return [(ts, count) for ts, count in records if ts > cutoff]
    
    def _periodic_cleanup(self):
        """定期清理过期记录"""
        now = datetime.utcnow()
        if (now - self.last_cleanup).total_seconds() >= self.cleanup_interval:
            # 清理 10 分钟前的记录
            cutoff = now - timedelta(seconds=600)
            
            for key in list(self.ip_requests.keys()):
                self.ip_requests[key] = [
                    (ts, count) for ts, count in self.ip_requests[key]
                    if ts > cutoff
                ]
                if not self.ip_requests[key]:
                    del self.ip_requests[key]
            
            for key in list(self.user_requests.keys()):
                self.user_requests[key] = [
                    (ts, count) for ts, count in self.user_requests[key]
                    if ts > cutoff
                ]
                if not self.user_requests[key]:
                    del self.user_requests[key]
            
            self.last_cleanup = now
    
    def check_rate_limit(
        self,
        identifier: str,
        requests_per_window: int,
        window_seconds: int,
        identifier_type: str = "ip"
    ) -> Tuple[bool, int]:
        """
        检查限流
        
        Args:
            identifier: 标识符（IP/用户 ID/端点）
            requests_per_window: 时间窗口内允许的请求数
            window_seconds: 时间窗口（秒）
            identifier_type: 标识符类型 (ip/user/endpoint)
            
        Returns:
            (是否允许，剩余请求数)
        """
        self._periodic_cleanup()
        
        # 选择存储
        if identifier_type == "ip":
            storage = self.ip_requests
        elif identifier_type == "user":
            storage = self.user_requests
        else:
            storage = self.endpoint_requests
        
        # 获取当前记录
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window_seconds)
        
        # 清理过期记录并计算当前窗口内的请求数
        current_requests = [
            (ts, count) for ts, count in storage[identifier]
            if ts > cutoff
        ]
        
        total_requests = sum(count for _, count in current_requests)
        
        if total_requests >= requests_per_window:
            # 超过限流
            remaining = 0
            
            # 计算重置时间
            if current_requests:
                oldest = min(ts for ts, _ in current_requests)
                reset_seconds = int((oldest + timedelta(seconds=window_seconds) - now).total_seconds())
            else:
                reset_seconds = window_seconds
            
            return False, remaining, reset_seconds
        
        # 记录新请求
        current_requests.append((now, 1))
        storage[identifier] = current_requests
        
        remaining = requests_per_window - total_requests - 1
        
        return True, remaining, 0
    
    def get_stats(self) -> Dict:
        """获取限流统计"""
        return {
            "tracked_ips": len(self.ip_requests),
            "tracked_users": len(self.user_requests),
            "tracked_endpoints": len(self.endpoint_requests),
            "last_cleanup": self.last_cleanup.isoformat()
        }


# 全局限流器实例
rate_limiter = RateLimiter()


# ==================== 限流配置 ====================

class RateLimitConfig:
    """限流配置"""
    
    # 全局限流：每分钟 60 次
    GLOBAL_LIMIT = 60
    GLOBAL_WINDOW = 60
    
    # 每端点限流：每分钟 100 次
    ENDPOINT_LIMIT = 100
    ENDPOINT_WINDOW = 60
    
    # 每用户限流：每分钟 30 次
    USER_LIMIT = 30
    USER_WINDOW = 60
    
    # 严格端点（支付等）：每分钟 10 次
    STRICT_LIMIT = 10
    STRICT_WINDOW = 60
    
    # 严格端点列表
    STRICT_ENDPOINTS = [
        "/api/v1/nexus/transfer",
        "/api/v1/nexus/payment/verify",
        "/api/v1/a2a/payment"
    ]


# ==================== FastAPI 中间件 ====================

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI 限流中间件
    """
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        
        # 获取客户端 IP
        client_ip = request.client.host if request.client else "unknown"
        
        # 获取端点
        endpoint = request.url.path
        
        # 获取用户 ID（如果有）
        user_id = request.headers.get("X-User-ID")
        
        # 1. 检查全局限流
        allowed, remaining, reset = rate_limiter.check_rate_limit(
            client_ip,
            RateLimitConfig.GLOBAL_LIMIT,
            RateLimitConfig.GLOBAL_WINDOW,
            "ip"
        )
        
        if not allowed:
            return self._rate_limit_response(remaining, reset)
        
        # 2. 检查端点限流
        if endpoint in RateLimitConfig.STRICT_ENDPOINTS:
            # 严格限流端点
            allowed, remaining, reset = rate_limiter.check_rate_limit(
                f"{client_ip}:{endpoint}",
                RateLimitConfig.STRICT_LIMIT,
                RateLimitConfig.STRICT_WINDOW,
                "endpoint"
            )
        else:
            # 普通端点
            allowed, remaining, reset = rate_limiter.check_rate_limit(
                endpoint,
                RateLimitConfig.ENDPOINT_LIMIT,
                RateLimitConfig.ENDPOINT_WINDOW,
                "endpoint"
            )
        
        if not allowed:
            return self._rate_limit_response(remaining, reset)
        
        # 3. 检查用户限流（如果有用户 ID）
        if user_id:
            allowed, remaining, reset = rate_limiter.check_rate_limit(
                user_id,
                RateLimitConfig.USER_LIMIT,
                RateLimitConfig.USER_WINDOW,
                "user"
            )
            
            if not allowed:
                return self._rate_limit_response(remaining, reset)
        
        # 执行请求
        response = await call_next(request)
        
        # 添加限流头
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset)
        
        return response
    
    def _rate_limit_response(self, remaining: int, reset: int):
        """返回限流响应"""
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too Many Requests",
                "message": "请求频率超限",
                "remaining": remaining,
                "reset_seconds": reset
            },
            headers={
                "Retry-After": str(reset),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(reset)
            }
        )


# ==================== 限流装饰器 ====================

def rate_limit(
    requests_per_window: int,
    window_seconds: int,
    identifier_type: str = "ip"
):
    """
    限流装饰器
    
    Args:
        requests_per_window: 时间窗口内允许的请求数
        window_seconds: 时间窗口（秒）
        identifier_type: 标识符类型
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 获取请求对象（从参数中）
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                return await func(*args, **kwargs)
            
            # 生成标识符
            if identifier_type == "ip":
                identifier = request.client.host if request.client else "unknown"
            else:
                identifier = request.headers.get("X-User-ID", "anonymous")
            
            # 检查限流
            allowed, remaining, reset = rate_limiter.check_rate_limit(
                identifier,
                requests_per_window,
                window_seconds,
                identifier_type
            )
            
            if not allowed:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Too Many Requests",
                        "message": "请求频率超限",
                        "remaining": remaining,
                        "reset_seconds": reset
                    },
                    headers={
                        "Retry-After": str(reset)
                    }
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
