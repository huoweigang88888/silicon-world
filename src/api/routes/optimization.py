"""
性能优化 API 路由

数据库优化、缓存管理、性能监控
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.optimization.db_optimizer import DatabaseOptimizer
import os
from pathlib import Path


router = APIRouter(prefix="/api/v1/optimization", tags=["性能优化"])


# 单例优化器
db_optimizer = None


def get_db_path() -> str:
    """获取数据库路径"""
    # 尝试常见路径
    possible_paths = [
        "silicon_world.db",
        Path(__file__).parent.parent.parent / "silicon_world.db",
        Path.cwd() / "silicon_world.db"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return str(path)
    
    return "silicon_world.db"


def get_optimizer() -> DatabaseOptimizer:
    """获取数据库优化器实例"""
    global db_optimizer
    if db_optimizer is None:
        db_path = get_db_path()
        db_optimizer = DatabaseOptimizer(db_path)
    return db_optimizer


# ==================== 响应模型 ====================

class TableStats(BaseModel):
    """表统计信息"""
    table_name: str
    row_count: int
    column_count: int
    size_mb: float
    index_count: int


class IndexSuggestion(BaseModel):
    """索引建议"""
    type: str
    column: str
    reason: str
    sql: str


class PerformanceReport(BaseModel):
    """性能报告"""
    timestamp: str
    tables: Dict[str, TableStats]
    index_suggestions: Dict[str, List[IndexSuggestion]]
    cache_size: int


class OptimizationResult(BaseModel):
    """优化结果"""
    vacuum: bool
    analyze: bool
    cache_cleared: bool


# ==================== API 端点 ====================

@router.get("/report")
async def get_performance_report():
    """
    获取数据库性能报告
    
    包含表统计、索引建议、缓存状态等
    """
    optimizer = get_optimizer()
    report = optimizer.get_performance_report()
    
    return report


@router.get("/table/{table_name}")
async def get_table_stats(table_name: str):
    """
    获取指定表的统计信息
    
    - **table_name**: 表名
    """
    optimizer = get_optimizer()
    
    try:
        stats = optimizer.analyze_table(table_name)
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"分析失败：{str(e)}")


@router.get("/table/{table_name}/index-suggestions")
async def get_index_suggestions(table_name: str):
    """
    获取指定表的索引建议
    
    - **table_name**: 表名
    """
    optimizer = get_optimizer()
    
    try:
        suggestions = optimizer.suggest_indexes(table_name)
        return {
            "table": table_name,
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取建议失败：{str(e)}")


@router.post("/index/create")
async def create_index(
    index_name: str,
    table_name: str,
    columns: List[str],
    unique: bool = False
):
    """
    创建索引
    
    - **index_name**: 索引名称
    - **table_name**: 表名
    - **columns**: 列名列表
    - **unique**: 是否唯一索引
    """
    optimizer = get_optimizer()
    
    try:
        optimizer.create_index(index_name, table_name, columns, unique)
        return {
            "success": True,
            "index_name": index_name,
            "table": table_name,
            "columns": columns
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建索引失败：{str(e)}")


@router.post("/optimize")
async def run_optimization():
    """
    执行数据库优化
    
    包括：
    - VACUUM: 回收空间
    - ANALYZE: 更新统计信息
    - 清理缓存
    """
    optimizer = get_optimizer()
    results = optimizer.optimize_database()
    
    return {
        "success": True,
        "results": results
    }


@router.get("/query-performance")
async def analyze_query_performance(
    query: str,
    params: Optional[str] = None
):
    """
    分析查询性能
    
    - **query**: SQL 查询语句
    - **params**: 查询参数 (JSON 格式)
    """
    optimizer = get_optimizer()
    
    try:
        import json
        params_tuple = tuple(json.loads(params)) if params else None
        result = optimizer.analyze_query_performance(query, params_tuple)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"分析失败：{str(e)}")


@router.post("/cache/clear")
async def clear_cache():
    """清空查询缓存"""
    optimizer = get_optimizer()
    optimizer.cache.clear()
    
    return {
        "success": True,
        "message": "缓存已清空"
    }


@router.get("/cache/stats")
async def get_cache_stats():
    """获取缓存统计"""
    optimizer = get_optimizer()
    
    return {
        "cache_size": len(optimizer.cache.cache),
        "query_stats_count": len(optimizer.query_stats)
    }


@router.get("/health")
async def optimization_health():
    """优化模块健康检查"""
    try:
        optimizer = get_optimizer()
        report = optimizer.get_performance_report()
        
        return {
            "status": "healthy",
            "database_size_mb": sum(t.get('size_mb', 0) for t in report['tables'].values()),
            "tables_analyzed": len(report['tables']),
            "cache_size": report['cache_size']
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }


# 使用示例
if __name__ == "__main__":
    print("性能优化 API 模块已加载")
    print("可用端点:")
    print("  GET  /api/v1/optimization/report")
    print("  GET  /api/v1/optimization/table/{table_name}")
    print("  GET  /api/v1/optimization/table/{table_name}/index-suggestions")
    print("  POST /api/v1/optimization/index/create")
    print("  POST /api/v1/optimization/optimize")
    print("  GET  /api/v1/optimization/query-performance")
    print("  POST /api/v1/optimization/cache/clear")
    print("  GET  /api/v1/optimization/cache/stats")
