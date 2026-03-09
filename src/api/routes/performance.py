"""
性能监控 API 路由

提供系统性能监控相关的 REST API
"""

from fastapi import APIRouter
from typing import Dict, Any
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

router = APIRouter(tags=["Performance"])


@router.get("/api/v1/performance/stats")
async def get_performance_stats():
    """获取性能统计"""
    
    stats = {
        "cache": {},
        "database": {},
        "memory": {},
        "system": {}
    }
    
    # 缓存统计
    try:
        from src.a2a.cache import cache
        cache_stats = await cache.get_stats()
        stats["cache"] = cache_stats
    except Exception as e:
        stats["cache"] = {"error": str(e)}
    
    # 数据库连接池统计
    try:
        from src.a2a.db_pool import db_pool
        if db_pool:
            stats["database"] = db_pool.get_stats()
        else:
            stats["database"] = {"status": "not_initialized"}
    except Exception as e:
        stats["database"] = {"error": str(e)}
    
    # 内存使用
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        stats["memory"] = {
            "rss_mb": memory_info.rss / 1024 / 1024,  # 物理内存
            "vms_mb": memory_info.vms / 1024 / 1024,  # 虚拟内存
            "percent": process.memory_percent()
        }
    except ImportError:
        stats["memory"] = {"status": "psutil_not_installed"}
    except Exception as e:
        stats["memory"] = {"error": str(e)}
    
    # 系统信息
    try:
        import psutil
        stats["system"] = {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
            "memory_available_gb": psutil.virtual_memory().available / 1024 / 1024 / 1024
        }
    except Exception as e:
        stats["system"] = {"error": str(e)}
    
    return stats


@router.get("/api/v1/performance/health")
async def get_health_check():
    """健康检查"""
    
    health = {
        "status": "healthy",
        "services": {}
    }
    
    # 检查缓存
    try:
        from src.a2a.cache import cache
        if cache.connected:
            health["services"]["cache"] = "healthy"
        else:
            health["services"]["cache"] = "disconnected"
    except Exception as e:
        health["services"]["cache"] = f"error: {str(e)}"
        health["status"] = "degraded"
    
    # 检查数据库
    try:
        from src.a2a.db_pool import db_pool
        if db_pool:
            health["services"]["database"] = "healthy"
        else:
            health["services"]["database"] = "not_initialized"
    except Exception as e:
        health["services"]["database"] = f"error: {str(e)}"
        health["status"] = "degraded"
    
    # 检查 API
    health["services"]["api"] = "healthy"
    
    return health


@router.get("/api/v1/performance/memory")
async def get_memory_usage():
    """获取内存使用情况"""
    
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "process": {
                "rss_mb": memory_info.rss / 1024 / 1024,
                "vms_mb": memory_info.vms / 1024 / 1024,
                "percent": process.memory_percent()
            },
            "system": {
                "total_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
                "available_gb": psutil.virtual_memory().available / 1024 / 1024 / 1024,
                "percent": psutil.virtual_memory().percent
            }
        }
    except ImportError:
        return {"error": "psutil not installed"}
    except Exception as e:
        return {"error": str(e)}


@router.get("/api/v1/performance/cpu")
async def get_cpu_usage():
    """获取 CPU 使用情况"""
    
    try:
        import psutil
        
        return {
            "process_percent": psutil.Process().cpu_percent(interval=0.1),
            "system_percent": psutil.cpu_percent(interval=0.1),
            "cpu_count": psutil.cpu_count(),
            "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        }
    except ImportError:
        return {"error": "psutil not installed"}
    except Exception as e:
        return {"error": str(e)}
