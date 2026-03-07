"""
性能优化工具

包含:
- 数据库连接池
- 查询优化
- 性能监控
"""

from sqlalchemy import create_engine, event
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from datetime import datetime
from typing import Generator
import time
import os


# ==================== 数据库连接池 ====================

# 从环境变量读取配置
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost/silicon_world"
)

# 创建引擎，配置连接池
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # 连接池大小
    max_overflow=40,       # 最大溢出连接数
    pool_pre_ping=True,    # 使用前检查连接
    pool_recycle=3600,     # 连接回收时间 (秒)
    echo=False             # 是否打印 SQL
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db() -> Generator:
    """
    获取数据库会话 (上下文管理器)
    
    Usage:
        with get_db() as db:
            # 使用 db 进行数据库操作
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== 性能监控 ====================

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.queries = []
        self.start_time = None
    
    def start(self):
        """开始监控"""
        self.start_time = time.time()
        self.queries = []
    
    def stop(self) -> dict:
        """
        停止监控并返回报告
        
        Returns:
            性能报告
        """
        duration = time.time() - self.start_time
        
        return {
            "duration": duration,
            "query_count": len(self.queries),
            "queries": self.queries
        }
    
    def record_query(self, sql: str, duration: float, params: tuple = None):
        """
        记录查询
        
        Args:
            sql: SQL 语句
            duration: 执行时间
            params: 参数
        """
        self.queries.append({
            "sql": sql,
            "duration": duration,
            "params": params
        })


# 监听 SQL 执行
@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """SQL 执行前记录"""
    conn.info.setdefault('query_start_time', []).append(time.time())


@event.listens_for(engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """SQL 执行后记录"""
    total = time.time() - conn.info['query_start_time'].pop(-1)
    
    # 记录慢查询 (>100ms)
    if total > 0.1:
        print(f"[SLOW QUERY] {total:.3f}s: {statement[:100]}")


# ==================== 索引优化建议 ====================

def analyze_indexes(db):
    """
    分析索引使用情况
    
    Args:
        db: 数据库会话
    
    Returns:
        索引使用报告
    """
    from sqlalchemy import text
    
    # 查询表大小
    result = db.execute(text("""
        SELECT 
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
    """))
    
    tables = result.fetchall()
    
    # 查询索引使用情况
    result = db.execute(text("""
        SELECT
            schemaname,
            tablename,
            indexname,
            idx_scan,
            idx_tup_read,
            idx_tup_fetch
        FROM pg_stat_user_indexes
        ORDER BY idx_scan DESC;
    """))
    
    indexes = result.fetchall()
    
    return {
        "tables": tables,
        "indexes": indexes
    }


# ==================== 缓存优化 ====================

def optimize_queries():
    """
    查询优化建议
    
    Returns:
        优化建议列表
    """
    suggestions = [
        "为常用查询字段添加索引",
        "使用连接池减少连接开销",
        "对热点数据使用 Redis 缓存",
        "批量操作使用 executemany",
        "避免 N+1 查询问题",
        "使用懒加载减少初始查询",
        "定期分析表统计信息",
        "对大表使用分区"
    ]
    
    return suggestions


# 使用示例
if __name__ == "__main__":
    # 测试连接池
    print("测试数据库连接池...")
    
    with get_db() as db:
        # 执行一些查询
        result = db.execute(
            "SELECT version()",
        )
        version = result.scalar()
        print(f"数据库版本：{version}")
    
    print("✓ 连接池测试通过")
    
    # 性能监控示例
    print("\n性能监控示例...")
    monitor = PerformanceMonitor()
    monitor.start()
    
    with get_db() as db:
        # 模拟查询
        for i in range(5):
            result = db.execute("SELECT version()")
            result.scalar()
    
    report = monitor.stop()
    print(f"执行时间：{report['duration']:.3f}s")
    print(f"查询次数：{report['query_count']}")
    
    # 索引优化建议
    print("\n索引优化建议:")
    for suggestion in optimize_queries():
        print(f"  - {suggestion}")
