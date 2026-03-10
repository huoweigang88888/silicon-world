"""
数据库查询优化器

性能优化：索引、缓存、查询优化
"""

import sqlite3
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib


class QueryCache:
    """查询结果缓存"""
    
    def __init__(self, ttl_seconds: int = 300):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds
    
    def _generate_key(self, query: str, params: tuple = None) -> str:
        """生成缓存键"""
        key_str = f"{query}:{params}" if params else query
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, query: str, params: tuple = None) -> Optional[Any]:
        """获取缓存结果"""
        key = self._generate_key(query, params)
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['data']
            else:
                del self.cache[key]
        return None
    
    def set(self, query: str, data: Any, params: tuple = None):
        """设置缓存"""
        key = self._generate_key(query, params)
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
    
    def cleanup(self):
        """清理过期缓存"""
        now = time.time()
        expired = [k for k, v in self.cache.items() if now - v['timestamp'] >= self.ttl]
        for key in expired:
            del self.cache[key]


class DatabaseOptimizer:
    """
    数据库优化器
    
    提供查询优化、索引建议、性能分析等功能
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.cache = QueryCache(ttl_seconds=300)
        self.query_stats: Dict[str, List[float]] = {}
    
    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def analyze_table(self, table_name: str) -> Dict[str, Any]:
        """
        分析表结构和统计信息
        
        Args:
            table_name: 表名
        
        Returns:
            表分析结果
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        # 获取行数
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        
        # 获取索引
        cursor.execute(f"PRAGMA index_list({table_name})")
        indexes = cursor.fetchall()
        
        # 获取表大小
        cursor.execute(f"PRAGMA page_count")
        page_count = cursor.fetchone()[0]
        cursor.execute(f"PRAGMA page_size")
        page_size = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'table_name': table_name,
            'row_count': row_count,
            'column_count': len(columns),
            'columns': [
                {
                    'name': col['name'],
                    'type': col['type'],
                    'notnull': bool(col['notnull']),
                    'pk': bool(col['pk'])
                }
                for col in columns
            ],
            'indexes': [
                {
                    'name': idx['name'],
                    'unique': bool(idx['unique'])
                }
                for idx in indexes
            ],
            'size_bytes': page_count * page_size,
            'size_mb': round((page_count * page_size) / (1024 * 1024), 2)
        }
    
    def suggest_indexes(self, table_name: str) -> List[Dict[str, Any]]:
        """
        建议需要创建的索引
        
        Args:
            table_name: 表名
        
        Returns:
            索引建议列表
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 获取现有索引
        cursor.execute(f"PRAGMA index_list({table_name})")
        existing_indexes = [idx['name'] for idx in cursor.fetchall()]
        
        # 获取列信息
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        suggestions = []
        
        # 建议：外键列应该建立索引
        for col in columns:
            col_name = col['name']
            if col_name.endswith('_id') and f"idx_{table_name}_{col_name}" not in existing_indexes:
                suggestions.append({
                    'type': 'foreign_key',
                    'column': col_name,
                    'reason': '外键列建议建立索引以提高 JOIN 性能',
                    'sql': f"CREATE INDEX idx_{table_name}_{col_name} ON {table_name}({col_name})"
                })
            
            # 建议：常用查询列建立索引
            if col_name in ['created_at', 'updated_at', 'status', 'type'] and f"idx_{table_name}_{col_name}" not in existing_indexes:
                suggestions.append({
                    'type': 'query_optimization',
                    'column': col_name,
                    'reason': f'{col_name} 列常用于查询条件，建议建立索引',
                    'sql': f"CREATE INDEX idx_{table_name}_{col_name} ON {table_name}({col_name})"
                })
        
        conn.close()
        return suggestions
    
    def create_index(self, index_name: str, table_name: str, columns: List[str], unique: bool = False):
        """
        创建索引
        
        Args:
            index_name: 索引名称
            table_name: 表名
            columns: 列名列表
            unique: 是否唯一索引
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        unique_str = "UNIQUE " if unique else ""
        cols_str = ", ".join(columns)
        sql = f"CREATE {unique_str}INDEX IF NOT EXISTS {index_name} ON {table_name}({cols_str})"
        
        cursor.execute(sql)
        conn.commit()
        conn.close()
        
        print(f"✅ 索引创建成功：{index_name}")
    
    def analyze_query_performance(self, query: str, params: tuple = None) -> Dict[str, Any]:
        """
        分析查询性能
        
        Args:
            query: SQL 查询
            params: 查询参数
        
        Returns:
            性能分析结果
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 执行 EXPLAIN QUERY PLAN
        cursor.execute(f"EXPLAIN QUERY PLAN {query}", params or ())
        plan = cursor.fetchall()
        
        # 执行并计时
        start = time.time()
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        duration = time.time() - start
        
        conn.close()
        
        # 记录统计
        query_hash = hashlib.md5(query.encode()).hexdigest()
        if query_hash not in self.query_stats:
            self.query_stats[query_hash] = []
        self.query_stats[query_hash].append(duration)
        
        return {
            'query': query,
            'row_count': len(results),
            'duration_ms': round(duration * 1000, 2),
            'plan': [dict(row) for row in plan],
            'avg_duration_ms': round(sum(self.query_stats[query_hash]) / len(self.query_stats[query_hash]) * 1000, 2),
            'executions': len(self.query_stats[query_hash])
        }
    
    def execute_cached(self, query: str, params: tuple = None, force: bool = False) -> List[Dict[str, Any]]:
        """
        执行带缓存的查询
        
        Args:
            query: SQL 查询
            params: 查询参数
            force: 强制刷新缓存
        
        Returns:
            查询结果
        """
        # 尝试从缓存获取
        if not force:
            cached = self.cache.get(query, params)
            if cached is not None:
                return cached
        
        # 执行查询
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # 存入缓存
        self.cache.set(query, results, params)
        
        return results
    
    def optimize_database(self) -> Dict[str, Any]:
        """
        执行数据库优化
        
        Returns:
            优化结果
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        results = {
            'vacuum': False,
            'analyze': False,
            'cache_cleared': False
        }
        
        # VACUUM - 回收空间
        try:
            cursor.execute("VACUUM")
            results['vacuum'] = True
            print("✅ VACUUM 完成")
        except Exception as e:
            print(f"❌ VACUUM 失败：{e}")
        
        # ANALYZE - 更新统计信息
        try:
            cursor.execute("ANALYZE")
            results['analyze'] = True
            print("✅ ANALYZE 完成")
        except Exception as e:
            print(f"❌ ANALYZE 失败：{e}")
        
        conn.commit()
        conn.close()
        
        # 清理缓存
        self.cache.cleanup()
        results['cache_cleared'] = True
        
        return results
    
    def get_performance_report(self) -> Dict[str, Any]:
        """
        生成性能报告
        
        Returns:
            性能报告
        """
        # 分析主要表
        tables = ['agents', 'memories', 'social_messages', 'friendships']
        table_stats = {}
        
        for table in tables:
            try:
                table_stats[table] = self.analyze_table(table)
            except:
                pass
        
        # 获取索引建议
        index_suggestions = {}
        for table in tables:
            try:
                index_suggestions[table] = self.suggest_indexes(table)
            except:
                pass
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'tables': table_stats,
            'index_suggestions': index_suggestions,
            'cache_size': len(self.cache.cache),
            'query_stats_count': len(self.query_stats)
        }


# 使用示例
if __name__ == "__main__":
    db_path = "silicon_world.db"
    optimizer = DatabaseOptimizer(db_path)
    
    print("📊 数据库性能报告")
    print("=" * 50)
    
    report = optimizer.get_performance_report()
    print(f"生成时间：{report['timestamp']}")
    print(f"缓存大小：{report['cache_size']}")
    print()
    
    for table, stats in report['tables'].items():
        print(f"表：{table}")
        print(f"  行数：{stats['row_count']}")
        print(f"  大小：{stats['size_mb']} MB")
        print(f"  索引：{len(stats['indexes'])}")
        
        suggestions = report['index_suggestions'].get(table, [])
        if suggestions:
            print(f"  建议索引:")
            for sug in suggestions:
                print(f"    - {sug['column']}: {sug['reason']}")
        print()
    
    # 执行优化
    print("🔧 执行数据库优化...")
    results = optimizer.optimize_database()
    print(f"优化结果：{results}")
