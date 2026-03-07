"""
决策系统

实现 Agent 的智能决策算法
"""

from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel
from datetime import datetime
import random


# ==================== 决策模型 ====================

class Decision(BaseModel):
    """决策模型"""
    action: str
    reason: str
    confidence: float = 0.0  # 置信度 0-1
    priority: int = 0  # 优先级
    parameters: Dict[str, Any] = {}
    timestamp: datetime = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)


class DecisionContext(BaseModel):
    """决策上下文"""
    situation: str  # 当前情况
    goals: List[str] = []  # 当前目标
    constraints: List[str] = []  # 约束条件
    available_resources: Dict[str, Any] = {}  # 可用资源
    social_context: Optional[str] = None  # 社交上下文
    emotional_state: Optional[str] = None  # 情绪状态


# ==================== 决策算法 ====================

class DecisionMaker:
    """
    决策引擎
    
    基于规则 + 效用理论的混合决策
    """
    
    def __init__(self):
        self.rules: List[Dict[str, Any]] = []
        self.utilities: Dict[str, callable] = {}
    
    def add_rule(self, condition: callable, action: str, priority: int = 0):
        """
        添加决策规则
        
        Args:
            condition: 条件函数
            action: 动作
            priority: 优先级
        """
        self.rules.append({
            "condition": condition,
            "action": action,
            "priority": priority
        })
    
    def make_decision(
        self,
        context: DecisionContext,
        personality_traits: Dict[str, float] = None
    ) -> Decision:
        """
        做出决策
        
        Args:
            context: 决策上下文
            personality_traits: 人格特质
        
        Returns:
            Decision
        """
        # 1. 规则匹配
        rule_decision = self._match_rules(context)
        
        # 2. 效用计算
        utility_decision = self._calculate_utilities(context, personality_traits)
        
        # 3. 综合决策
        final_decision = self._combine_decisions(
            rule_decision,
            utility_decision,
            personality_traits
        )
        
        return final_decision
    
    def _match_rules(self, context: DecisionContext) -> Optional[Decision]:
        """规则匹配"""
        matched_rules = []
        
        for rule in self.rules:
            if rule["condition"](context):
                matched_rules.append(rule)
        
        if not matched_rules:
            return None
        
        # 选择优先级最高的规则
        best_rule = max(matched_rules, key=lambda r: r["priority"])
        
        return Decision(
            action=best_rule["action"],
            reason=f"规则匹配 (优先级：{best_rule['priority']})",
            confidence=0.8
        )
    
    def _calculate_utilities(
        self,
        context: DecisionContext,
        personality_traits: Dict[str, float] = None
    ) -> Decision:
        """
        效用计算
        
        基于人格特质计算各选项的效用值
        """
        if not personality_traits:
            personality_traits = {}
        
        # 定义可能的动作
        actions = [
            "communicate",  # 交流
            "explore",  # 探索
            "create",  # 创造
            "rest",  # 休息
            "learn",  # 学习
            "trade",  # 交易
            "help"  # 帮助
        ]
        
        # 计算每个动作的效用
        utilities = {}
        for action in actions:
            utility = self._calculate_action_utility(
                action,
                context,
                personality_traits
            )
            utilities[action] = utility
        
        # 选择效用最高的动作
        best_action = max(utilities, key=utilities.get)
        
        return Decision(
            action=best_action,
            reason=f"效用最大化 ({utilities[best_action]:.2f})",
            confidence=utilities[best_action],
            parameters={"utilities": utilities}
        )
    
    def _calculate_action_utility(
        self,
        action: str,
        context: DecisionContext,
        personality_traits: Dict[str, float]
    ) -> float:
        """
        计算动作效用
        
        Returns:
            效用值 0-1
        """
        base_utility = 0.5
        
        # 根据人格特质调整
        if action == "communicate":
            base_utility += personality_traits.get("extraversion", 0.5) * 0.3
            base_utility += personality_traits.get("agreeableness", 0.5) * 0.2
        
        elif action == "explore":
            base_utility += personality_traits.get("openness", 0.5) * 0.4
            base_utility += personality_traits.get("creativity", 0.5) * 0.1
        
        elif action == "create":
            base_utility += personality_traits.get("creativity", 0.5) * 0.5
        
        elif action == "help":
            base_utility += personality_traits.get("agreeableness", 0.5) * 0.4
            base_utility += personality_traits.get("morality", 0.8) * 0.1
        
        elif action == "learn":
            base_utility += personality_traits.get("openness", 0.5) * 0.3
            base_utility += personality_traits.get("conscientiousness", 0.5) * 0.2
        
        # 根据情境调整
        if context.emotional_state == "bored":
            if action in ["explore", "create"]:
                base_utility += 0.2
        
        if context.emotional_state == "tired":
            if action == "rest":
                base_utility += 0.3
        
        # 根据目标调整
        if context.goals:
            for goal in context.goals:
                if goal == "make_friends" and action == "communicate":
                    base_utility += 0.3
                elif goal == "earn_money" and action == "trade":
                    base_utility += 0.3
        
        return min(1.0, max(0.0, base_utility))
    
    def _combine_decisions(
        self,
        rule_decision: Optional[Decision],
        utility_decision: Decision,
        personality_traits: Dict[str, float] = None
    ) -> Decision:
        """
        综合决策
        
        结合规则决策和效用决策
        """
        if not rule_decision:
            return utility_decision
        
        # 如果规则决策置信度高，优先规则
        if rule_decision.confidence > 0.9:
            return rule_decision
        
        # 否则综合考虑
        if not personality_traits:
            personality_traits = {}
        
        # 谨慎性高的人格更倾向规则
        if personality_traits.get("conscientiousness", 0.5) > 0.7:
            return rule_decision
        
        # 开放性高的人格更倾向效用计算
        if personality_traits.get("openness", 0.5) > 0.7:
            return utility_decision
        
        # 默认选择效用决策
        return utility_decision


# ==================== 行为树 ====================

class BehaviorNode:
    """行为树节点"""
    
    def __init__(self, name: str):
        self.name = name
        self.children: List["BehaviorNode"] = []
    
    def execute(self, context: Dict[str, Any]) -> str:
        """执行节点"""
        raise NotImplementedError


class SelectorNode(BehaviorNode):
    """选择节点 - 执行第一个成功的子节点"""
    
    def execute(self, context: Dict[str, Any]) -> str:
        for child in self.children:
            result = child.execute(context)
            if result == "success":
                return "success"
        return "failure"


class SequenceNode(BehaviorNode):
    """序列节点 - 按顺序执行所有子节点"""
    
    def execute(self, context: Dict[str, Any]) -> str:
        for child in self.children:
            result = child.execute(context)
            if result == "failure":
                return "failure"
        return "success"


class ActionNode(BehaviorNode):
    """动作节点"""
    
    def __init__(self, name: str, action_func: callable):
        super().__init__(name)
        self.action_func = action_func
    
    def execute(self, context: Dict[str, Any]) -> str:
        try:
            result = self.action_func(context)
            return "success" if result else "failure"
        except Exception:
            return "failure"


class BehaviorTree:
    """
    行为树
    
    用于组织复杂的行为逻辑
    """
    
    def __init__(self, root: BehaviorNode):
        self.root = root
    
    def execute(self, context: Dict[str, Any] = None) -> str:
        """执行行为树"""
        return self.root.execute(context or {})
    
    @staticmethod
    def build_social_tree() -> "BehaviorTree":
        """构建社交行为树"""
        # 根节点 - 选择
        root = SelectorNode("social_root")
        
        # 分支 1: 紧急消息
        emergency_seq = SequenceNode("emergency_sequence")
        emergency_seq.children = [
            ActionNode("check_emergency", lambda ctx: True),
            ActionNode("respond_immediately", lambda ctx: True)
        ]
        root.children.append(emergency_seq)
        
        # 分支 2: 朋友消息
        friend_seq = SequenceNode("friend_sequence")
        friend_seq.children = [
            ActionNode("check_friend", lambda ctx: True),
            ActionNode("respond_warmly", lambda ctx: True)
        ]
        root.children.append(friend_seq)
        
        # 分支 3: 陌生人消息
        stranger_seq = SequenceNode("stranger_sequence")
        stranger_seq.children = [
            ActionNode("check_stranger", lambda ctx: True),
            ActionNode("respond_politely", lambda ctx: True)
        ]
        root.children.append(stranger_seq)
        
        return BehaviorTree(root)


# 使用示例
if __name__ == "__main__":
    # 创建决策引擎
    maker = DecisionMaker()
    
    # 添加规则
    maker.add_rule(
        condition=lambda ctx: "emergency" in ctx.situation.lower(),
        action="respond_immediately",
        priority=10
    )
    
    # 创建上下文
    context = DecisionContext(
        situation="收到朋友消息",
        goals=["maintain_friendship"],
        emotional_state="happy"
    )
    
    # 人格特质
    personality = {
        "extraversion": 0.8,
        "agreeableness": 0.9,
        "openness": 0.7
    }
    
    # 做出决策
    decision = maker.make_decision(context, personality)
    
    print(f"决策：{decision.action}")
    print(f"原因：{decision.reason}")
    print(f"置信度：{decision.confidence}")
    
    # 测试行为树
    print("\n行为树测试:")
    tree = BehaviorTree.build_social_tree()
    result = tree.execute()
    print(f"执行结果：{result}")
