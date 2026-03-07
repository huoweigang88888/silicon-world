"""
性能优化模块

缓存策略和查询优化
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import hashlib
import json


class CacheManager:
    """
    缓存管理器
    
    提供多级缓存支持
    """
    
    def __init__(self):
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
    
    def generate_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = f"{prefix}:{args}:{kwargs}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if datetime.utcnow() < entry["expires_at"]:
                self.cache_stats["hits"] += 1
                return entry["data"]
            else:
                # 过期删除
                del self.memory_cache[key]
                self.cache_stats["evictions"] += 1
        
        self.cache_stats["misses"] += 1
        return None
    
    def set(self, key: str, data: Any, ttl_seconds: int = 300):
        """设置缓存"""
        self.memory_cache[key] = {
            "data": data,
            "expires_at": datetime.utcnow() + timedelta(seconds=ttl_seconds)
        }
        
        # 限制缓存大小
        if len(self.memory_cache) > 10000:
            self._evict_old()
    
    def delete(self, key: str):
        """删除缓存"""
        if key in self.memory_cache:
            del self.memory_cache[key]
    
    def clear(self):
        """清空缓存"""
        self.memory_cache.clear()
    
    def _evict_old(self):
        """清理过期缓存"""
        now = datetime.utcnow()
        expired_keys = [
            key for key, entry in self.memory_cache.items()
            if now >= entry["expires_at"]
        ]
        
        for key in expired_keys:
            del self.memory_cache[key]
            self.cache_stats["evictions"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = self.cache_stats["hits"] / total if total > 0 else 0
        
        return {
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "evictions": self.cache_stats["evictions"],
            "hit_rate": hit_rate,
            "cache_size": len(self.memory_cache)
        }


class QueryOptimizer:
    """
    查询优化器
    
    优化数据库查询性能
    """
    
    @staticmethod
    def add_pagination(query, page: int = 1, page_size: int = 20):
        """添加分页"""
        offset = (page - 1) * page_size
        return query.offset(offset).limit(page_size)
    
    @staticmethod
    def add_indexes_recommendations(table_name: str) -> List[str]:
        """推荐索引"""
        recommendations = {
            "agents": [
                "CREATE INDEX idx_agents_id ON agents(id);",
                "CREATE INDEX idx_agents_name ON agents(name);",
                "CREATE INDEX idx_agents_created_at ON agents(created_at);"
            ],
            "memories": [
                "CREATE INDEX idx_memories_agent_id ON memories(agent_id);",
                "CREATE INDEX idx_memories_type ON memories(memory_type);",
                "CREATE INDEX idx_memories_created_at ON memories(created_at);"
            ],
            "transactions": [
                "CREATE INDEX idx_transactions_from ON transactions(from_address);",
                "CREATE INDEX idx_transactions_to ON transactions(to_address);",
                "CREATE INDEX idx_transactions_timestamp ON transactions(timestamp);"
            ]
        }
        
        return recommendations.get(table_name, [])
    
    @staticmethod
    def optimize_batch_operations(operations: List[Dict], batch_size: int = 100):
        """批量操作优化"""
        batches = []
        for i in range(0, len(operations), batch_size):
            batches.append(operations[i:i + batch_size])
        return batches


# 使用示例
if __name__ == "__main__":
    # 测试缓存管理器
    cache = CacheManager()
    
    # 设置缓存
    cache.set("user:123", {"name": "张三", "age": 25}, ttl_seconds=60)
    
    # 获取缓存
    user = cache.get("user:123")
    print(f"用户数据：{user}")
    
    # 获取统计
    stats = cache.get_stats()
    print(f"缓存统计：{stats}")
    
    # 查询优化示例
    optimizer = QueryOptimizer()
    indexes = optimizer.add_indexes_recommendations("agents")
    print(f"\n推荐索引:")
    for idx in indexes:
        print(f"  {idx}")
