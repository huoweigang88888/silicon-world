"""
世界状态管理

管理世界状态的快照、同步和持久化
"""

from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel
from datetime import datetime
import json
import hashlib


# ==================== 状态快照 ====================

class WorldState(BaseModel):
    """
    世界状态快照
    """
    timestamp: datetime
    version: int
    entities: Dict[str, Any] = {}
    regions: Dict[str, Any] = {}
    physics_state: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow()
        if 'version' not in data:
            data['version'] = 1
        super().__init__(**data)
    
    def get_hash(self) -> str:
        """获取状态哈希"""
        state_json = self.model_dump_json(exclude={'timestamp'})
        return hashlib.sha256(state_json.encode()).hexdigest()
    
    def diff(self, other: "WorldState") -> Dict[str, Any]:
        """
        计算与另一个状态的差异
        
        Args:
            other: 另一个状态
        
        Returns:
            差异字典
        """
        diff = {
            "added": {},
            "removed": {},
            "modified": {}
        }
        
        # 比较实体
        for entity_id, entity_data in self.entities.items():
            if entity_id not in other.entities:
                diff["added"]["entities"] = entity_id
            elif entity_data != other.entities[entity_id]:
                diff["modified"]["entities"] = {
                    "id": entity_id,
                    "old": other.entities[entity_id],
                    "new": entity_data
                }
        
        for entity_id in other.entities:
            if entity_id not in self.entities:
                if "removed" not in diff:
                    diff["removed"]["entities"] = []
                diff["removed"]["entities"].append(entity_id)
        
        return diff


# ==================== 状态管理器 ====================

class StateManager:
    """
    状态管理器
    
    管理世界状态的快照历史
    """
    
    def __init__(self, max_history: int = 60):
        self.max_history = max_history  # 最多保存 60 个快照 (1 秒@60fps)
        self.states: List[WorldState] = []
        self.current_version = 0
    
    def create_snapshot(
        self,
        entities: Dict[str, Any],
        regions: Dict[str, Any],
        physics_state: Dict[str, Any],
        metadata: Dict[str, Any] = None
    ) -> WorldState:
        """
        创建状态快照
        
        Args:
            entities: 实体状态
            regions: 区域状态
            physics_state: 物理状态
            metadata: 元数据
        
        Returns:
            WorldState
        """
        self.current_version += 1
        
        snapshot = WorldState(
            version=self.current_version,
            entities=entities,
            regions=regions,
            physics_state=physics_state,
            metadata=metadata or {}
        )
        
        self.states.append(snapshot)
        
        # 限制历史长度
        if len(self.states) > self.max_history:
            self.states = self.states[-self.max_history:]
        
        return snapshot
    
    def get_latest(self) -> Optional[WorldState]:
        """获取最新状态"""
        return self.states[-1] if self.states else None
    
    def get_at_version(self, version: int) -> Optional[WorldState]:
        """获取指定版本的状态"""
        for state in self.states:
            if state.version == version:
                return state
        return None
    
    def get_changes_since(self, version: int) -> Optional[Dict[str, Any]]:
        """
        获取从指定版本以来的变化
        
        Args:
            version: 版本号
        
        Returns:
            变化字典
        """
        old_state = self.get_at_version(version)
        if not old_state:
            return None
        
        new_state = self.get_latest()
        if not new_state:
            return None
        
        return new_state.diff(old_state)
    
    def rollback_to(self, version: int) -> bool:
        """
        回滚到指定版本
        
        Args:
            version: 版本号
        
        Returns:
            是否成功
        """
        target_state = self.get_at_version(version)
        if not target_state:
            return False
        
        # 删除版本之后的所有状态
        self.states = [s for s in self.states if s.version <= version]
        self.current_version = version
        
        return True
    
    def get_state_history(self) -> List[Dict[str, Any]]:
        """获取状态历史摘要"""
        return [
            {
                "version": state.version,
                "timestamp": state.timestamp,
                "hash": state.get_hash(),
                "entity_count": len(state.entities)
            }
            for state in self.states
        ]


# ==================== 状态同步 ====================

class StateSynchronizer:
    """
    状态同步器
    
    负责客户端与服务端的状态同步
    """
    
    def __init__(self):
        self.state_manager = StateManager()
        self.pending_updates: List[Dict[str, Any]] = []
        self.subscribers: Set[str] = set()
    
    def subscribe(self, client_id: str):
        """订阅状态更新"""
        self.subscribers.add(client_id)
    
    def unsubscribe(self, client_id: str):
        """取消订阅"""
        if client_id in self.subscribers:
            self.subscribers.remove(client_id)
    
    def update_state(
        self,
        entities: Dict[str, Any],
        regions: Dict[str, Any],
        physics_state: Dict[str, Any]
    ):
        """
        更新状态并通知订阅者
        
        Args:
            entities: 实体状态
            regions: 区域状态
            physics_state: 物理状态
        """
        # 创建快照
        snapshot = self.state_manager.create_snapshot(
            entities=entities,
            regions=regions,
            physics_state=physics_state
        )
        
        # 计算增量更新
        if len(self.state_manager.states) > 1:
            delta = self.state_manager.get_changes_since(
                self.state_manager.current_version - 1
            )
        else:
            delta = None
        
        # 通知订阅者
        update_message = {
            "type": "state_update",
            "version": snapshot.version,
            "timestamp": snapshot.timestamp.isoformat(),
            "full_state": snapshot.model_dump(),
            "delta": delta
        }
        
        self.pending_updates.append(update_message)
    
    def get_pending_updates(self, client_id: str) -> List[Dict[str, Any]]:
        """获取待发送的更新"""
        if client_id not in self.subscribers:
            return []
        
        updates = self.pending_updates.copy()
        return updates
    
    def clear_pending_updates(self):
        """清空待发送更新"""
        self.pending_updates = []
    
    def get_sync_status(self) -> Dict[str, Any]:
        """获取同步状态"""
        return {
            "subscribers": len(self.subscribers),
            "pending_updates": len(self.pending_updates),
            "current_version": self.state_manager.current_version,
            "history_size": len(self.state_manager.states)
        }


# ==================== 状态持久化 ====================

class StatePersistence:
    """
    状态持久化
    
    将世界状态保存到存储
    """
    
    def __init__(self, storage_path: str = "world_states"):
        self.storage_path = storage_path
    
    def save_state(self, state: WorldState) -> str:
        """
        保存状态到存储
        
        Args:
            state: 世界状态
        
        Returns:
            保存的文件路径
        """
        import os
        from pathlib import Path
        
        # 创建存储目录
        storage_dir = Path(self.storage_path)
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        filename = f"state_v{state.version}_{state.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = storage_dir / filename
        
        # 序列化并保存
        state_data = state.model_dump(mode='json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def load_state(self, version: int) -> Optional[WorldState]:
        """
        从存储加载状态
        
        Args:
            version: 版本号
        
        Returns:
            WorldState 或 None
        """
        import os
        from pathlib import Path
        
        storage_dir = Path(self.storage_path)
        
        # 查找匹配的文件
        for filepath in storage_dir.glob(f"state_v{version}_*.json"):
            with open(filepath, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            return WorldState(**state_data)
        
        return None
    
    def list_saved_states(self) -> List[Dict[str, Any]]:
        """列出所有已保存的状态"""
        import os
        from pathlib import Path
        
        storage_dir = Path(self.storage_path)
        states = []
        
        for filepath in storage_dir.glob("state_v*.json"):
            # 从文件名解析信息
            parts = filepath.stem.split('_')
            version = int(parts[1].replace('v', ''))
            timestamp_str = '_'.join(parts[2:])
            
            states.append({
                "version": version,
                "filename": filepath.name,
                "filepath": str(filepath),
                "size": filepath.stat().st_size
            })
        
        states.sort(key=lambda x: x["version"], reverse=True)
        return states
    
    def cleanup_old_states(self, keep_count: int = 100):
        """
        清理旧状态
        
        Args:
            keep_count: 保留的数量
        """
        states = self.list_saved_states()
        
        if len(states) <= keep_count:
            return
        
        # 删除多余的状态
        for state in states[keep_count:]:
            filepath = Path(state["filepath"])
            filepath.unlink()


# 使用示例
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # 创建状态管理器
        state_mgr = StateManager()
        
        # 创建一些测试数据
        entities = {
            "agent_1": {"position": [0, 0, 0], "name": "三一"},
            "agent_2": {"position": [10, 0, 0], "name": "大哥"}
        }
        regions = {
            "hub": {"name": "中心城", "population": 2}
        }
        physics = {
            "gravity": -9.8,
            "bodies": 2
        }
        
        # 创建快照
        print("创建状态快照...")
        snapshot1 = state_mgr.create_snapshot(
            entities=entities,
            regions=regions,
            physics_state=physics
        )
        print(f"版本 {snapshot1.version}: 哈希={snapshot1.get_hash()[:16]}...")
        
        # 修改状态
        entities["agent_1"]["position"] = [1, 0, 0]
        entities["agent_3"] = {"position": [5, 0, 0], "name": "新朋友"}
        
        snapshot2 = state_mgr.create_snapshot(
            entities=entities,
            regions=regions,
            physics_state=physics
        )
        print(f"版本 {snapshot2.version}: 哈希={snapshot2.get_hash()[:16]}...")
        
        # 获取变化
        changes = state_mgr.get_changes_since(1)
        print(f"\n从版本 1 到版本 2 的变化:")
        print(f"  修改：{changes.get('modified', {})}")
        print(f"  新增：{changes.get('added', {})}")
        
        # 状态历史
        history = state_mgr.get_state_history()
        print(f"\n状态历史:")
        for h in history:
            print(f"  版本 {h['version']}: {h['entity_count']} 个实体")
        
        # 测试同步器
        print("\n测试状态同步...")
        sync = StateSynchronizer()
        sync.subscribe("client_1")
        sync.update_state(entities, regions, physics)
        
        updates = sync.get_pending_updates("client_1")
        print(f"待发送更新：{len(updates)} 条")
        
        # 测试持久化
        print("\n测试状态持久化...")
        persistence = StatePersistence()
        filepath = persistence.save_state(snapshot1)
        print(f"保存状态：{filepath}")
        
        saved_states = persistence.list_saved_states()
        print(f"已保存状态：{len(saved_states)} 个")
    
    asyncio.run(main())
