"""
Redis 缓存层

用于缓存热点数据，提升性能
"""

import redis
import json
from typing import Any, Optional
from datetime import timedelta
import hashlib


class CacheManager:
    """
    缓存管理器
    
    提供统一的缓存接口
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """
        初始化缓存管理器
        
        Args:
            redis_url: Redis 连接 URL
        """
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = 300  # 默认 5 分钟
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
        
        Returns:
            缓存值，不存在返回 None
        """
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间 (秒)
        """
        if ttl is None:
            ttl = self.default_ttl
        
        data = json.dumps(value, ensure_ascii=False)
        self.redis.setex(key, ttl, data)
    
    def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
        
        Returns:
            是否成功删除
        """
        return bool(self.redis.delete(key))
    
    def exists(self, key: str) -> bool:
        """
        检查缓存是否存在
        
        Args:
            key: 缓存键
        
        Returns:
            是否存在
        """
        return bool(self.redis.exists(key))
    
    def clear_pattern(self, pattern: str):
        """
        清除匹配模式的缓存
        
        Args:
            pattern: 键模式 (支持通配符)
        """
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
    
    def generate_key(self, *args, **kwargs) -> str:
        """
        生成缓存键
        
        Args:
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            缓存键
        """
        key_data = f"{args}:{kwargs}"
        return hashlib.md5(key_data.encode()).hexdigest()


# 缓存装饰器
def cache(ttl: int = 300, prefix: str = ""):
    """
    缓存装饰器
    
    Args:
        ttl: 过期时间 (秒)
        prefix: 键前缀
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 获取缓存管理器 (从 args 或 kwargs)
            cache_manager = kwargs.get('cache_manager')
            if not cache_manager and len(args) > 0:
                cache_manager = getattr(args[0], 'cache_manager', None)
            
            if not cache_manager:
                # 没有缓存管理器，直接调用原函数
                return await func(*args, **kwargs)
            
            # 生成缓存键
            key = f"{prefix}:{func.__name__}:{cache_manager.generate_key(*args, **kwargs)}"
            
            # 尝试从缓存获取
            cached = cache_manager.get(key)
            if cached is not None:
                return cached
            
            # 调用原函数
            result = await func(*args, **kwargs)
            
            # 存入缓存
            cache_manager.set(key, result, ttl)
            
            return result
        return wrapper
    return decorator


# 使用示例
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # 创建缓存管理器
        cache_manager = CacheManager()
        
        # 设置缓存
        cache_manager.set("test:key", {"name": "三一", "age": 1}, ttl=60)
        
        # 获取缓存
        data = cache_manager.get("test:key")
        print(f"缓存数据：{data}")
        
        # 检查是否存在
        exists = cache_manager.exists("test:key")
        print(f"缓存存在：{exists}")
        
        # 删除缓存
        cache_manager.delete("test:key")
        exists = cache_manager.exists("test:key")
        print(f"删除后存在：{exists}")
    
    asyncio.run(main())
