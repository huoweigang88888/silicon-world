"""
Redis 缓存层

提供数据缓存功能，提升性能
"""

import json
import asyncio
from typing import Optional, Any, Dict, List
from datetime import datetime, timedelta
import hashlib


class RedisCache:
    """
    Redis 缓存客户端
    
    提供键值对缓存功能
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        use_mock: bool = True
    ):
        """
        初始化 Redis 客户端
        
        Args:
            host: Redis 主机
            port: Redis 端口
            db: 数据库编号
            password: 密码
            use_mock: 是否使用模拟模式（无 Redis 时）
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.use_mock = use_mock
        
        # 模拟缓存存储
        self._mock_cache: Dict[str, Dict[str, Any]] = {}
        self._mock_expiry: Dict[str, datetime] = {}
        
        # 连接状态
        self.connected = False
    
    async def connect(self) -> bool:
        """
        连接到 Redis
        
        Returns:
            是否连接成功
        """
        if self.use_mock:
            print(f"[Redis] 使用模拟模式 (无真实 Redis)")
            self.connected = True
            return True
        
        try:
            # TODO: 集成真实 Redis
            # import redis.asyncio as redis
            # self.client = redis.Redis(host=self.host, port=self.port, db=self.db, password=self.password)
            # await self.client.ping()
            
            print(f"[Redis] 尝试连接：{self.host}:{self.port}")
            await asyncio.sleep(0.5)  # 模拟连接
            
            self.connected = True
            print("[Redis] 连接成功")
            return True
            
        except Exception as e:
            print(f"[Redis] 连接失败：{e}，切换到模拟模式")
            self.use_mock = True
            self.connected = True
            return True
    
    def _get_key(self, key: str) -> str:
        """
        生成完整键名
        
        Args:
            key: 原始键名
            
        Returns:
            带前缀的键名
        """
        return f"silicon_world:{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，不存在返回 None
        """
        if not self.connected:
            await self.connect()
        
        full_key = self._get_key(key)
        
        if self.use_mock:
            # 模拟模式
            if full_key in self._mock_cache:
                # 检查是否过期
                if full_key in self._mock_expiry:
                    if datetime.utcnow() > self._mock_expiry[full_key]:
                        del self._mock_cache[full_key]
                        del self._mock_expiry[full_key]
                        return None
                
                value = self._mock_cache[full_key]
                print(f"[Redis] GET {key} = {value}")
                return value
            return None
        
        # TODO: 真实 Redis 实现
        # value = await self.client.get(full_key)
        # if value:
        #     return json.loads(value)
        # return None
        
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间（秒）
            
        Returns:
            是否设置成功
        """
        if not self.connected:
            await self.connect()
        
        full_key = self._get_key(key)
        
        if self.use_mock:
            # 模拟模式
            self._mock_cache[full_key] = value
            print(f"[Redis] SET {key} = {value}")
            
            if expire:
                self._mock_expiry[full_key] = datetime.utcnow() + timedelta(seconds=expire)
                print(f"[Redis] 设置过期时间：{expire}秒")
            
            return True
        
        # TODO: 真实 Redis 实现
        # serialized = json.dumps(value, ensure_ascii=False)
        # if expire:
        #     await self.client.setex(full_key, expire, serialized)
        # else:
        #     await self.client.set(full_key, serialized)
        # return True
        
        return True
    
    async def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否删除成功
        """
        if not self.connected:
            await self.connect()
        
        full_key = self._get_key(key)
        
        if self.use_mock:
            if full_key in self._mock_cache:
                del self._mock_cache[full_key]
                if full_key in self._mock_expiry:
                    del self._mock_expiry[full_key]
                print(f"[Redis] DELETE {key}")
                return True
            return False
        
        # TODO: 真实 Redis 实现
        # return await self.client.delete(full_key) > 0
        
        return False
    
    async def exists(self, key: str) -> bool:
        """
        检查键是否存在
        
        Args:
            key: 缓存键
            
        Returns:
            是否存在
        """
        if not self.connected:
            await self.connect()
        
        full_key = self._get_key(key)
        
        if self.use_mock:
            return full_key in self._mock_cache
        
        # TODO: 真实 Redis 实现
        # return await self.client.exists(full_key) > 0
        
        return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """
        清除匹配模式的键
        
        Args:
            pattern: 键模式（支持 * 通配符）
            
        Returns:
            删除的数量
        """
        if not self.connected:
            await self.connect()
        
        if self.use_mock:
            import fnmatch
            
            count = 0
            keys_to_delete = []
            
            for key in self._mock_cache.keys():
                if fnmatch.fnmatch(key, self._get_key(pattern)):
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self._mock_cache[key]
                if key in self._mock_expiry:
                    del self._mock_expiry[key]
                count += 1
            
            print(f"[Redis] CLEAR {pattern}, 删除 {count} 个键")
            return count
        
        # TODO: 真实 Redis 实现
        # keys = await self.client.keys(self._get_key(pattern))
        # if keys:
        #     return await self.client.delete(*keys)
        # return 0
        
        return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计
        
        Returns:
            统计信息
        """
        if self.use_mock:
            return {
                "mode": "mock",
                "keys_count": len(self._mock_cache),
                "host": self.host,
                "port": self.port
            }
        
        return {
            "mode": "redis",
            "host": self.host,
            "port": self.port,
            "connected": self.connected
        }


# 缓存装饰器

def cache_result(
    key_prefix: str,
    expire: int = 300
):
    """
    缓存结果装饰器
    
    Args:
        key_prefix: 键前缀
        expire: 过期时间（秒）
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            from .cache import cache
            
            # 生成缓存键
            key_data = f"{args}:{kwargs}"
            key_hash = hashlib.md5(key_data.encode()).hexdigest()
            cache_key = f"{key_prefix}:{key_hash}"
            
            # 尝试从缓存获取
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 存入缓存
            await cache.set(cache_key, result, expire=expire)
            
            return result
        
        return wrapper
    return decorator


# 全局缓存实例
cache = RedisCache(use_mock=True)
