"""
Agent 调用日志

记录所有外部 Agent 的调用历史
"""

from sqlalchemy import Column, String, DateTime, JSON, Integer, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from src.core.database import Base, SessionLocal


class InvocationLog(Base):
    """调用日志模型"""
    __tablename__ = "invocation_logs"
    
    id = Column(String, primary_key=True, index=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False, index=True)
    action = Column(String, nullable=False)
    input_data = Column(JSON, default=dict)
    output_data = Column(JSON, default=dict)
    success = Column(Integer, default=1)  # 1=成功，0=失败
    error_message = Column(Text, nullable=True)
    status_code = Column(Integer, nullable=True)
    duration = Column(Float, nullable=True)  # 耗时 (秒)
    protocol = Column(String, default="http")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<InvocationLog(id={self.id}, agent_id={self.agent_id}, success={self.success})>"


def create_log(agent_id: str, action: str, input_data: dict, result: dict) -> InvocationLog:
    """
    创建调用日志
    
    Args:
        agent_id: Agent ID
        action: 动作
        input_data: 输入数据
        result: 调用结果
        
    Returns:
        日志记录
    """
    import uuid
    
    log = InvocationLog(
        id=str(uuid.uuid4()),
        agent_id=agent_id,
        action=action,
        input_data=input_data,
        output_data=result.get("data", {}),
        success=1 if result.get("success") else 0,
        error_message=result.get("error") or result.get("message"),
        status_code=result.get("status_code"),
        duration=result.get("duration"),
        protocol=result.get("protocol", "http")
    )
    
    db = SessionLocal()
    try:
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    finally:
        db.close()


def get_logs(agent_id: str, limit: int = 50, offset: int = 0):
    """
    获取 Agent 的调用日志
    
    Args:
        agent_id: Agent ID
        limit: 返回数量
        offset: 偏移量
        
    Returns:
        日志列表
    """
    db = SessionLocal()
    try:
        logs = db.query(InvocationLog)\
            .filter(InvocationLog.agent_id == agent_id)\
            .order_by(InvocationLog.created_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
        
        return logs
    finally:
        db.close()


def get_stats(agent_id: str, hours: int = 24):
    """
    获取调用统计
    
    Args:
        agent_id: Agent ID
        hours: 统计时长 (小时)
        
    Returns:
        统计数据
    """
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    db = SessionLocal()
    try:
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # 总调用次数
        total = db.query(InvocationLog)\
            .filter(
                InvocationLog.agent_id == agent_id,
                InvocationLog.created_at >= since
            ).count()
        
        # 成功次数
        success = db.query(InvocationLog)\
            .filter(
                InvocationLog.agent_id == agent_id,
                InvocationLog.created_at >= since,
                InvocationLog.success == 1
            ).count()
        
        # 平均耗时
        avg_duration = db.query(func.avg(InvocationLog.duration))\
            .filter(
                InvocationLog.agent_id == agent_id,
                InvocationLog.created_at >= since,
                InvocationLog.duration != None
            ).scalar()
        
        return {
            "agent_id": agent_id,
            "period_hours": hours,
            "total_invocations": total,
            "success_count": success,
            "failure_count": total - success,
            "success_rate": (success / total * 100) if total > 0 else 0,
            "avg_duration_seconds": round(avg_duration, 2) if avg_duration else 0
        }
    finally:
        db.close()
