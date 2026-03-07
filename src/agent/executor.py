"""
行为执行器

执行 Agent 的决策和动作
"""

from typing import Dict, List, Optional, Any, Callable
from pydantic import BaseModel
from datetime import datetime
import asyncio


# ==================== 动作定义 ====================

class Action(BaseModel):
    """动作模型"""
    name: str
    description: str
    parameters: Dict[str, Any] = {}
    preconditions: List[str] = []  # 前置条件
    effects: List[str] = []  # 效果
    duration: float = 1.0  # 持续时间 (秒)
    cost: float = 0.0  # 成本


class ActionResult(BaseModel):
    """动作执行结果"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    duration: float = 0.0
    timestamp: datetime = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)


# ==================== 动作库 ====================

class ActionLibrary:
    """动作库"""
    
    def __init__(self):
        self.actions: Dict[str, Action] = {}
        self._register_default_actions()
    
    def _register_default_actions(self):
        """注册默认动作"""
        
        # 交流动作
        self.register(Action(
            name="communicate",
            description="与他人交流",
            parameters={"message": str, "tone": str},
            duration=5.0
        ))
        
        # 探索动作
        self.register(Action(
            name="explore",
            description="探索新环境",
            parameters={"location": str},
            duration=30.0
        ))
        
        # 创造动作
        self.register(Action(
            name="create",
            description="创造内容",
            parameters={"content_type": str, "topic": str},
            duration=60.0
        ))
        
        # 学习动作
        self.register(Action(
            name="learn",
            description="学习新知识",
            parameters={"subject": str, "resource": str},
            duration=120.0
        ))
        
        # 交易动作
        self.register(Action(
            name="trade",
            description="进行交易",
            parameters={"item": str, "price": float},
            duration=10.0
        ))
        
        # 帮助动作
        self.register(Action(
            name="help",
            description="帮助他人",
            parameters={"target": str, "task": str},
            duration=15.0
        ))
        
        # 休息动作
        self.register(Action(
            name="rest",
            description="休息恢复",
            parameters={"duration": float},
            duration=300.0
        ))
    
    def register(self, action: Action):
        """注册动作"""
        self.actions[action.name] = action
    
    def get(self, name: str) -> Optional[Action]:
        """获取动作"""
        return self.actions.get(name)
    
    def list_actions(self) -> List[str]:
        """列出所有动作"""
        return list(self.actions.keys())


# ==================== 执行器 ====================

class ActionExecutor:
    """
    动作执行器
    
    负责执行各种动作
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.library = ActionLibrary()
        self.executing: bool = False
        self.current_action: Optional[Action] = None
        self.action_history: List[ActionResult] = []
    
    async def execute(
        self,
        action_name: str,
        parameters: Dict[str, Any] = None
    ) -> ActionResult:
        """
        执行动作
        
        Args:
            action_name: 动作名称
            parameters: 动作参数
        
        Returns:
            执行结果
        """
        # 获取动作
        action = self.library.get(action_name)
        if not action:
            return ActionResult(
                success=False,
                message=f"未知动作：{action_name}"
            )
        
        # 检查前置条件
        if not self._check_preconditions(action):
            return ActionResult(
                success=False,
                message="前置条件不满足"
            )
        
        # 执行动作
        self.executing = True
        self.current_action = action
        
        start_time = datetime.utcnow()
        
        try:
            # 根据动作类型执行
            result = await self._execute_action(action, parameters or {})
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            action_result = ActionResult(
                success=True,
                message=f"动作 {action_name} 执行成功",
                data=result,
                duration=duration
            )
            
        except Exception as e:
            action_result = ActionResult(
                success=False,
                message=f"执行失败：{str(e)}"
            )
        
        finally:
            self.executing = False
            self.current_action = None
        
        # 记录历史
        self.action_history.append(action_result)
        
        return action_result
    
    async def _execute_action(
        self,
        action: Action,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行具体动作
        
        Args:
            action: 动作
            parameters: 参数
        
        Returns:
            执行结果数据
        """
        # 根据动作类型分发
        if action.name == "communicate":
            return await self._execute_communicate(parameters)
        elif action.name == "explore":
            return await self._execute_explore(parameters)
        elif action.name == "create":
            return await self._execute_create(parameters)
        elif action.name == "learn":
            return await self._execute_learn(parameters)
        elif action.name == "trade":
            return await self._execute_trade(parameters)
        elif action.name == "help":
            return await self._execute_help(parameters)
        elif action.name == "rest":
            return await self._execute_rest(parameters)
        else:
            raise ValueError(f"未知动作：{action.name}")
    
    async def _execute_communicate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行交流动作"""
        message = params.get("message", "")
        tone = params.get("tone", "normal")
        
        # 模拟发送消息
        await asyncio.sleep(1)
        
        return {
            "message_sent": message,
            "tone": tone,
            "recipients": 1
        }
    
    async def _execute_explore(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行探索动作"""
        location = params.get("location", "unknown")
        
        # 模拟探索
        await asyncio.sleep(2)
        
        return {
            "location": location,
            "discoveries": ["new_area", "interesting_object"],
            "experience_gained": 10
        }
    
    async def _execute_create(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行创造动作"""
        content_type = params.get("content_type", "text")
        topic = params.get("topic", "general")
        
        # 模拟创造
        await asyncio.sleep(3)
        
        return {
            "content_type": content_type,
            "topic": topic,
            "quality": 0.8,
            "creativity_score": 0.7
        }
    
    async def _execute_learn(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行学习动作"""
        subject = params.get("subject", "general")
        
        # 模拟学习
        await asyncio.sleep(2)
        
        return {
            "subject": subject,
            "knowledge_gained": 15,
            "skill_improvement": 0.1
        }
    
    async def _execute_trade(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行交易动作"""
        item = params.get("item", "")
        price = params.get("price", 0.0)
        
        # 模拟交易
        await asyncio.sleep(1)
        
        return {
            "item": item,
            "price": price,
            "transaction_id": "tx_123"
        }
    
    async def _execute_help(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行帮助动作"""
        target = params.get("target", "")
        task = params.get("task", "")
        
        # 模拟帮助
        await asyncio.sleep(2)
        
        return {
            "target": target,
            "task": task,
            "reputation_gained": 5,
            "relationship_improved": 0.1
        }
    
    async def _execute_rest(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行休息动作"""
        duration = params.get("duration", 300.0)
        
        # 模拟休息
        await asyncio.sleep(min(duration, 5))  # 最多等 5 秒
        
        return {
            "energy_restored": 50,
            "stress_reduced": 30
        }
    
    def _check_preconditions(self, action: Action) -> bool:
        """检查前置条件"""
        # TODO: 实现前置条件检查
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """获取执行器状态"""
        return {
            "agent_id": self.agent_id,
            "executing": self.executing,
            "current_action": self.current_action.name if self.current_action else None,
            "total_actions_executed": len(self.action_history),
            "success_rate": self._calculate_success_rate()
        }
    
    def _calculate_success_rate(self) -> float:
        """计算成功率"""
        if not self.action_history:
            return 0.0
        
        successful = sum(1 for r in self.action_history if r.success)
        return successful / len(self.action_history)


# 使用示例
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # 创建执行器
        executor = ActionExecutor("did:silicon:agent:123")
        
        # 执行动作
        print("执行交流动作...")
        result = await executor.execute(
            "communicate",
            {"message": "你好！", "tone": "friendly"}
        )
        print(f"结果：{result.message}")
        print(f"耗时：{result.duration:.2f}秒")
        
        # 执行探索动作
        print("\n执行探索动作...")
        result = await executor.execute(
            "explore",
            {"location": "central_plaza"}
        )
        print(f"结果：{result.data}")
        
        # 获取状态
        print("\n执行器状态:")
        status = executor.get_status()
        print(f"已执行动作数：{status['total_actions_executed']}")
        print(f"成功率：{status['success_rate']:.2%}")
    
    asyncio.run(main())
