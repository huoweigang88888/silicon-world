"""
记忆系统

三层记忆架构:
- 短期记忆：当前会话上下文
- 长期记忆：持久化存储
- 语义记忆：向量数据库检索
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import deque
import uuid


class ShortTermMemory:
    """
    短期记忆
    
    存储当前会话上下文，容量有限，自动过期
    """
    
    def __init__(self, capacity: int = 100, ttl_hours: int = 24):
        """
        初始化短期记忆
        
        Args:
            capacity: 最大容量
            ttl_hours: 过期时间 (小时)
        """
        self.capacity = capacity
        self.ttl = timedelta(hours=ttl_hours)
        self.memories = deque(maxlen=capacity)
    
    def add(self, event: Dict[str, Any]):
        """
        添加记忆
        
        Args:
            event: 事件数据
        """
        event['timestamp'] = datetime.utcnow()
        event['type'] = 'short_term'
        self.memories.append(event)
    
    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的记忆
        
        Args:
            limit: 返回数量
        
        Returns:
            记忆列表
        """
        return list(self.memories)[-limit:]
    
    def clear_expired(self):
        """清理过期记忆"""
        now = datetime.utcnow()
        while self.memories and (now - self.memories[0]['timestamp']) > self.ttl:
            self.memories.popleft()
    
    def search(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索记忆
        
        Args:
            keyword: 关键词
        
        Returns:
            匹配的记忆
        """
        results = []
        for memory in self.memories:
            content = str(memory.get('content', ''))
            if keyword.lower() in content.lower():
                results.append(memory)
        return results
    
    def __len__(self):
        return len(self.memories)


class LongTermMemory:
    """
    长期记忆
    
    持久化存储到数据库
    """
    
    def __init__(self, agent_id: str, db_session=None):
        """
        初始化长期记忆
        
        Args:
            agent_id: Agent DID
            db_session: 数据库会话
        """
        self.agent_id = agent_id
        self.db = db_session
    
    def add(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """
        添加记忆
        
        Args:
            content: 记忆内容
            metadata: 元数据
        
        Returns:
            记忆 ID
        """
        memory_id = str(uuid.uuid4())
        
        # TODO: 保存到数据库
        # memory = MemoryModel(
        #     id=memory_id,
        #     agent_id=self.agent_id,
        #     content=content,
        #     memory_type='long_term',
        #     metadata=metadata or {}
        # )
        # self.db.add(memory)
        # self.db.commit()
        
        return memory_id
    
    def get(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取记忆
        
        Args:
            limit: 返回数量
        
        Returns:
            记忆列表
        """
        # TODO: 从数据库查询
        return []
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        搜索记忆
        
        Args:
            query: 搜索关键词
        
        Returns:
            匹配的记忆
        """
        # TODO: 数据库全文搜索
        return []
    
    def delete(self, memory_id: str) -> bool:
        """
        删除记忆
        
        Args:
            memory_id: 记忆 ID
        
        Returns:
            是否成功
        """
        # TODO: 从数据库删除
        return True


class SemanticMemory:
    """
    语义记忆
    
    向量数据库存储，支持语义相似度检索
    """
    
    def __init__(self, agent_id: str, vector_db=None):
        """
        初始化语义记忆
        
        Args:
            agent_id: Agent DID
            vector_db: 向量数据库客户端
        """
        self.agent_id = agent_id
        self.vector_db = vector_db
    
    def add(self, content: str, embedding: List[float] = None):
        """
        添加记忆
        
        Args:
            content: 记忆内容
            embedding: 向量嵌入 (可选)
        """
        # TODO: 生成向量嵌入
        # if embedding is None:
        #     embedding = await self._generate_embedding(content)
        
        # TODO: 存储到向量数据库
        # self.vector_db.upsert(
        #     collection=f"agent_{self.agent_id}",
        #     vectors=[embedding],
        #     metadata=[{"content": content}]
        # )
        pass
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        语义搜索
        
        Args:
            query: 查询文本
            top_k: 返回数量
        
        Returns:
            相似记忆列表
        """
        # TODO: 向量相似度搜索
        # query_embedding = await self._generate_embedding(query)
        # results = self.vector_db.search(
        #     collection=f"agent_{self.agent_id}",
        #     query_vector=query_embedding,
        #     top_k=top_k
        # )
        return []
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """
        生成向量嵌入
        
        Args:
            text: 文本
        
        Returns:
            向量
        """
        # TODO: 使用嵌入模型
        return []


class MemorySystem:
    """
    记忆系统
    
    统一管理三层记忆
    """
    
    def __init__(self, agent_id: str, db_session=None):
        """
        初始化记忆系统
        
        Args:
            agent_id: Agent DID
            db_session: 数据库会话
        """
        self.agent_id = agent_id
        self.short_term = ShortTermMemory(capacity=100)
        self.long_term = LongTermMemory(agent_id, db_session)
        self.semantic = SemanticMemory(agent_id, db_session)
    
    async def remember(self, event: Dict[str, Any]):
        """
        存储记忆
        
        自动存储到短期记忆，并触发记忆巩固
        
        Args:
            event: 事件数据
        """
        # 添加到短期记忆
        self.short_term.add(event)
        
        # 触发记忆巩固
        await self._consolidate()
    
    async def recall(self, query: str) -> List[Dict[str, Any]]:
        """
        检索记忆
        
        从三层记忆中检索并合并结果
        
        Args:
            query: 查询
        
        Returns:
            记忆列表
        """
        # 从各层检索
        short_results = self.short_term.search(query)
        long_results = self.long_term.search(query)
        semantic_results = self.semantic.search(query)
        
        # 合并结果
        all_results = short_results + long_results + semantic_results
        
        # 去重和排序
        return self._merge_results(all_results)
    
    async def _consolidate(self):
        """
        记忆巩固
        
        将重要的短期记忆转移到长期记忆
        """
        # 检查是否需要巩固
        if len(self.short_term) < self.short_term.capacity * 0.8:
            return
        
        # 获取最近的记忆
        recent = self.short_term.get_recent(limit=10)
        
        # 筛选重要的记忆
        for memory in recent:
            if self._is_important(memory):
                # 转移到长期记忆
                self.long_term.add(
                    content=memory.get('content', ''),
                    metadata=memory
                )
                
                # 生成语义记忆
                await self.semantic.add(memory.get('content', ''))
    
    def _is_important(self, memory: Dict[str, Any]) -> bool:
        """
        判断记忆是否重要
        
        Args:
            memory: 记忆数据
        
        Returns:
            是否重要
        """
        # 简单规则：包含情感标记的记忆更重要
        return memory.get('emotional_weight', 0) > 0.5
    
    def _merge_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        合并搜索结果
        
        Args:
            results: 结果列表
        
        Returns:
            合并后的结果
        """
        # 去重
        seen = set()
        unique_results = []
        
        for result in results:
            key = result.get('content', '')
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        # 按时间排序
        unique_results.sort(
            key=lambda x: x.get('timestamp', datetime.min),
            reverse=True
        )
        
        return unique_results


# 使用示例
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # 创建记忆系统
        memory = MemorySystem("did:silicon:agent:1234567890abcdef")
        
        # 存储记忆
        await memory.remember({
            "content": "今天学习了记忆系统",
            "emotional_weight": 0.8
        })
        
        await memory.remember({
            "content": "明天要继续开发",
            "emotional_weight": 0.3
        })
        
        # 检索记忆
        results = await memory.recall("学习")
        print(f"检索结果：{len(results)} 条")
        
        # 查看短期记忆
        print(f"短期记忆数量：{len(memory.short_term)}")
    
    asyncio.run(main())
