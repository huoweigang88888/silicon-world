"""
A2A 错误处理工具

统一的错误处理和重试机制
"""

from typing import Optional, Dict, Any, Callable, TypeVar
from functools import wraps
import asyncio
import time
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("a2a")

T = TypeVar('T')


class A2AError(Exception):
    """A2A 基础错误"""
    
    def __init__(self, message: str, code: str = "unknown", details: Optional[Dict] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "error": {
                "type": self.__class__.__name__,
                "code": self.code,
                "message": self.message,
                "details": self.details,
                "timestamp": self.timestamp
            }
        }


class AgentNotFoundError(A2AError):
    """Agent 未找到"""
    
    def __init__(self, agent_url: str):
        super().__init__(
            message=f"Agent 未找到：{agent_url}",
            code="agent_not_found",
            details={"agent_url": agent_url}
        )


class MessageSendError(A2AError):
    """消息发送错误"""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"消息发送失败：{message}",
            code="message_send_error",
            details=details or {}
        )


class TaskExecutionError(A2AError):
    """任务执行错误"""
    
    def __init__(self, task_id: str, error: str):
        super().__init__(
            message=f"任务执行失败：{task_id}",
            code="task_execution_error",
            details={
                "task_id": task_id,
                "error": error
            }
        )


class PaymentError(A2AError):
    """支付错误"""
    
    def __init__(self, message: str, payment_id: Optional[str] = None):
        super().__init__(
            message=f"支付失败：{message}",
            code="payment_error",
            details={"payment_id": payment_id} if payment_id else {}
        )


class RateLimitError(A2AError):
    """频率限制错误"""
    
    def __init__(self, retry_after: int):
        super().__init__(
            message="请求频率超限",
            code="rate_limit_exceeded",
            details={
                "retry_after": retry_after,
                "retry_after_seconds": retry_after
            }
        )


def retry_async(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    异步重试装饰器
    
    Args:
        max_attempts: 最大重试次数
        delay: 初始延迟（秒）
        backoff: 延迟倍数
        exceptions: 需要重试的异常类型
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(
                            f"[A2A] {func.__name__} 失败，已达最大重试次数：{e}"
                        )
                        raise
                    
                    logger.warning(
                        f"[A2A] {func.__name__} 失败，{current_delay}秒后重试 ({attempt}/{max_attempts}): {e}"
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            
            # 不应该到达这里
            raise last_exception
        
        return wrapper
    return decorator


def handle_a2a_errors(func: Callable):
    """
    A2A 错误处理装饰器
    
    统一处理 A2A 相关错误
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except A2AError as e:
            logger.error(f"[A2A] {func.__name__} A2A 错误：{e.message}")
            raise
        except Exception as e:
            logger.error(f"[A2A] {func.__name__} 未知错误：{e}")
            raise A2AError(
                message=str(e),
                code="internal_error",
                details={
                    "function": func.__name__,
                    "type": type(e).__name__
                }
            )
    
    return wrapper


class CircuitBreaker:
    """
    断路器模式实现
    
    防止级联故障
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_attempts: int = 3
    ):
        """
        初始化断路器
        
        Args:
            failure_threshold: 失败阈值
            recovery_timeout: 恢复超时（秒）
            half_open_attempts: 半开状态尝试次数
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_attempts = half_open_attempts
        
        self.failures = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half-open
        self.half_open_successes = 0
    
    def call(self, func: Callable):
        """
        断路器调用装饰器
        
        Args:
            func: 要保护的函数
        """
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 检查是否需要打开断路器
            if self.state == "open":
                time_since_failure = time.time() - self.last_failure_time
                
                if time_since_failure >= self.recovery_timeout:
                    logger.info("[CircuitBreaker] 进入半开状态")
                    self.state = "half-open"
                    self.half_open_successes = 0
                else:
                    raise A2AError(
                        message="服务不可用（断路器打开）",
                        code="circuit_breaker_open",
                        details={
                            "retry_after": int(self.recovery_timeout - time_since_failure)
                        }
                    )
            
            try:
                result = await func(*args, **kwargs)
                
                # 成功处理
                if self.state == "half-open":
                    self.half_open_successes += 1
                    if self.half_open_successes >= self.half_open_attempts:
                        logger.info("[CircuitBreaker] 断路器关闭，服务恢复")
                        self.state = "closed"
                        self.failures = 0
                
                return result
                
            except Exception as e:
                self.failures += 1
                self.last_failure_time = time.time()
                
                if self.failures >= self.failure_threshold:
                    logger.error(f"[CircuitBreaker] 断路器打开，失败次数：{self.failures}")
                    self.state = "open"
                
                raise
        
        return wrapper
    
    def reset(self):
        """重置断路器"""
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"
        self.half_open_successes = 0
    
    def get_status(self) -> Dict[str, Any]:
        """获取断路器状态"""
        return {
            "state": self.state,
            "failures": self.failures,
            "last_failure_time": self.last_failure_time,
            "half_open_successes": self.half_open_successes
        }


# 全局断路器实例
circuit_breaker = CircuitBreaker()
