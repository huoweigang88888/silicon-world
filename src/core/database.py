"""
数据库配置和模型
"""

from sqlalchemy import create_engine, Column, String, DateTime, JSON, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import Optional
import os

# 数据库 URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./silicon_world.db"
)

# 创建引擎
if DATABASE_URL.startswith("sqlite"):
    # SQLite 特定配置
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=os.getenv("DEBUG", "false").lower() == "true"
    )
    # 启用外键支持
    from sqlalchemy import event
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    engine = create_engine(DATABASE_URL)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基类
Base = declarative_base()


# ==================== 数据模型 ====================

class AgentModel(Base):
    """Agent 数据模型"""
    __tablename__ = "agents"
    
    id = Column(String, primary_key=True, index=True)  # DID
    name = Column(String, nullable=False)
    controller = Column(String, nullable=False)
    personality = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True)
    
    # 新增字段 - Agent 类型
    agent_type = Column(String, default="native")  # native: 原生，external: 外部
    connection_info = Column("connection", JSON, default=dict)  # 连接配置
    capabilities = Column(JSON, default=list)  # 能力列表
    status = Column(String, default="unknown")  # online, offline, error, unknown
    last_seen = Column(DateTime, nullable=True)  # 最后在线时间
    
    # 关系
    memories = relationship("MemoryModel", back_populates="agent", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name={self.name}, type={self.agent_type})>"


class MemoryModel(Base):
    """记忆数据模型"""
    __tablename__ = "memories"
    
    id = Column(String, primary_key=True, index=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    memory_type = Column(String, nullable=False)  # short_term, long_term, semantic
    embedding = Column(JSON, default=list)  # 向量嵌入
    meta = Column("metadata", JSON, default=dict)  # 使用 meta 避免保留字冲突
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    agent = relationship("AgentModel", back_populates="memories")
    
    def __repr__(self):
        return f"<Memory(id={self.id}, agent_id={self.agent_id}, type={self.memory_type})>"


class IdentityModel(Base):
    """身份数据模型"""
    __tablename__ = "identities"
    
    id = Column(String, primary_key=True, index=True)  # DID
    controller = Column(String, nullable=False, index=True)
    public_key = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True)
    blockchain_tx = Column(String)  # 区块链交易哈希
    
    def __repr__(self):
        return f"<Identity(id={self.id}, controller={self.controller})>"


class TokenTransaction(Base):
    """代币交易记录"""
    __tablename__ = "token_transactions"
    
    id = Column(String, primary_key=True, index=True)
    from_address = Column(String, nullable=False, index=True)
    to_address = Column(String, nullable=False, index=True)
    amount = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    tx_hash = Column(String, unique=True)
    status = Column(String, default="pending")  # pending, confirmed, failed
    
    def __repr__(self):
        return f"<TokenTransaction(id={self.id}, amount={self.amount})>"


# ==================== 数据库管理 ====================

def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)
    print("[INFO] Database initialized successfully")


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== CRUD 操作 ====================

class AgentRepository:
    """Agent 数据仓库"""
    
    def __init__(self, db):
        self.db = db
    
    def create(self, agent_id: str, name: str, controller: str, personality: dict = None,
               agent_type: str = "native", connection_info: dict = None, capabilities: list = None) -> AgentModel:
        """创建 Agent"""
        agent = AgentModel(
            id=agent_id,
            name=name,
            controller=controller,
            personality=personality or {},
            agent_type=agent_type,
            connection_info=connection_info or {},
            capabilities=capabilities or []
        )
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        return agent
    
    def get(self, agent_id: str) -> Optional[AgentModel]:
        """获取 Agent"""
        return self.db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    
    def list(self, limit: int = 10, offset: int = 0):
        """列出 Agent"""
        return self.db.query(AgentModel).offset(offset).limit(limit).all()
    
    def update(self, agent_id: str, **kwargs):
        """更新 Agent"""
        agent = self.get(agent_id)
        if agent:
            for key, value in kwargs.items():
                setattr(agent, key, value)
            self.db.commit()
            self.db.refresh(agent)
        return agent
    
    def delete(self, agent_id: str) -> bool:
        """删除 Agent"""
        agent = self.get(agent_id)
        if agent:
            self.db.delete(agent)
            self.db.commit()
            return True
        return False


class MemoryRepository:
    """记忆数据仓库"""
    
    def __init__(self, db):
        self.db = db
    
    def create(self, agent_id: str, content: str, memory_type: str, 
               embedding: list = None, meta: dict = None) -> MemoryModel:
        """创建记忆"""
        import uuid
        memory = MemoryModel(
            id=str(uuid.uuid4()),
            agent_id=agent_id,
            content=content,
            memory_type=memory_type,
            embedding=embedding or [],
            meta=meta or {}
        )
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)
        return memory
    
    def get_by_agent(self, agent_id: str, limit: int = 100):
        """获取 Agent 的记忆"""
        return self.db.query(MemoryModel)\
            .filter(MemoryModel.agent_id == agent_id)\
            .order_by(MemoryModel.created_at.desc())\
            .limit(limit)\
            .all()
    
    def get_by_agent_and_type(self, agent_id: str, memory_type: str, limit: int = 100):
        """按类型获取 Agent 的记忆"""
        return self.db.query(MemoryModel)\
            .filter(MemoryModel.agent_id == agent_id)\
            .filter(MemoryModel.memory_type == memory_type)\
            .order_by(MemoryModel.created_at.desc())\
            .limit(limit)\
            .all()
    
    def search(self, agent_id: str, query: str, limit: int = 20):
        """搜索记忆 (简单文本搜索)"""
        return self.db.query(MemoryModel)\
            .filter(MemoryModel.agent_id == agent_id)\
            .filter(MemoryModel.content.contains(query))\
            .order_by(MemoryModel.created_at.desc())\
            .limit(limit)\
            .all()
    
    def delete(self, memory_id: str, agent_id: str) -> bool:
        """删除记忆"""
        memory = self.db.query(MemoryModel)\
            .filter(MemoryModel.id == memory_id)\
            .filter(MemoryModel.agent_id == agent_id)\
            .first()
        if memory:
            self.db.delete(memory)
            self.db.commit()
            return True
        return False
    
    def count_by_type(self, agent_id: str):
        """统计各类型记忆数量"""
        from sqlalchemy import func
        results = self.db.query(
            MemoryModel.memory_type,
            func.count(MemoryModel.id).label('count')
        ).filter(MemoryModel.agent_id == agent_id)\
         .group_by(MemoryModel.memory_type)\
         .all()
        return {r.memory_type: r.count for r in results}


# 使用示例
if __name__ == "__main__":
    # 初始化数据库
    init_db()
    
    # 创建会话
    db = SessionLocal()
    
    # 创建 Agent
    agent_repo = AgentRepository(db)
    agent = agent_repo.create(
        agent_id="did:silicon:agent:1234567890abcdef1234567890abcdef",
        name="三一",
        controller="0x1234567890abcdef"
    )
    print(f"创建 Agent: {agent}")
    
    # 创建记忆
    memory_repo = MemoryRepository(db)
    memory = memory_repo.create(
        agent_id=agent.id,
        content="今天学习了数据库知识",
        memory_type="long_term"
    )
    print(f"创建记忆：{memory}")
    
    # 查询记忆
    memories = memory_repo.get_by_agent(agent.id)
    print(f"记忆数量：{len(memories)}")
    
    db.close()
