"""
数据库连接池

优化数据库连接管理，提升性能
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Optional, Dict, Any
from contextlib import contextmanager
import threading
import time


class DatabaseConnectionPool:
    """
    数据库连接池
    
    管理数据库连接，提升性能
    """
    
    def __init__(
        self,
        database_url: str,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        echo: bool = False
    ):
        """
        初始化连接池
        
        Args:
            database_url: 数据库 URL
            pool_size: 连接池大小
            max_overflow: 最大溢出连接数
            pool_timeout: 获取连接超时（秒）
            pool_recycle: 连接回收时间（秒）
            echo: 是否打印 SQL
        """
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.echo = echo
        
        # 创建引擎
        self.engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            echo=echo
        )
        
        # 创建会话工厂
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # 统计信息
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "total_queries": 0,
            "start_time": time.time()
        }
        
        # 线程锁
        self._lock = threading.Lock()
        
        # 注册事件
        self._register_events()
    
    def _register_events(self):
        """注册连接池事件"""
        
        @event.listens_for(self.engine, "connect")
        def on_connect(dbapi_connection, connection_record):
            """连接创建事件"""
            with self._lock:
                self.stats["total_connections"] += 1
                self.stats["active_connections"] += 1
            print(f"[DB Pool] 创建连接，当前活跃：{self.stats['active_connections']}")
        
        @event.listens_for(self.engine, "checkout")
        def on_checkout(dbapi_connection, connection_record, connection_proxy):
            """连接检出事件"""
            print(f"[DB Pool] 检出连接")
        
        @event.listens_for(self.engine, "checkin")
        def on_checkin(dbapi_connection, connection_record):
            """连接归还事件"""
            with self._lock:
                self.stats["active_connections"] -= 1
            print(f"[DB Pool] 归还连接，当前活跃：{self.stats['active_connections']}")
    
    @contextmanager
    def get_session(self):
        """
        获取数据库会话（上下文管理器）
        
        Yields:
            Session: 数据库会话
            
        Example:
            with pool.get_session() as session:
                users = session.query(User).all()
        """
        session = self.SessionLocal()
        try:
            with self._lock:
                self.stats["total_queries"] += 1
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取连接池统计
        
        Returns:
            统计信息
        """
        uptime = time.time() - self.stats["start_time"]
        
        return {
            "database_url": self.database_url,
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "total_connections": self.stats["total_connections"],
            "active_connections": self.stats["active_connections"],
            "total_queries": self.stats["total_queries"],
            "queries_per_second": self.stats["total_queries"] / uptime if uptime > 0 else 0,
            "uptime_seconds": uptime
        }
    
    def dispose(self):
        """释放连接池"""
        self.engine.dispose()
        print("[DB Pool] 连接池已释放")


# 全局连接池实例
db_pool: Optional[DatabaseConnectionPool] = None


def init_db_pool(database_url: str, **kwargs):
    """
    初始化全局连接池
    
    Args:
        database_url: 数据库 URL
        **kwargs: 其他参数
    """
    global db_pool
    db_pool = DatabaseConnectionPool(database_url, **kwargs)
    print(f"[DB Pool] 连接池已初始化：{database_url}")


def get_db_pool() -> DatabaseConnectionPool:
    """获取全局连接池"""
    if db_pool is None:
        raise RuntimeError("数据库连接池未初始化")
    return db_pool


def get_db_session():
    """
    获取数据库会话（用于 FastAPI 依赖注入）
    
    Yields:
        Session: 数据库会话
    """
    pool = get_db_pool()
    with pool.get_session() as session:
        yield session
