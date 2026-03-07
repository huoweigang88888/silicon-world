"""
人格系统

实现 Agent 的人格特质、行为和演化
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
import random


# ==================== 人格维度 ====================

class PersonalityTraits(BaseModel):
    """
    人格特质模型
    
    基于大五人格理论 (Big Five)
    """
    # 开放性 (Openness)
    openness: float = Field(ge=0, le=1, default=0.5)
    # 尽责性 (Conscientiousness)
    conscientiousness: float = Field(ge=0, le=1, default=0.5)
    # 外向性 (Extraversion)
    extraversion: float = Field(ge=0, le=1, default=0.5)
    # 宜人性 (Agreeableness)
    agreeableness: float = Field(ge=0, le=1, default=0.5)
    # 神经质 (Neuroticism)
    neuroticism: float = Field(ge=0, le=1, default=0.5)
    
    # 附加特质
    morality: float = Field(ge=0, le=1, default=0.8)  # 道德值
    creativity: float = Field(ge=0, le=1, default=0.5)  # 创造力
    empathy: float = Field(ge=0, le=1, default=0.5)  # 同理心
    
    def to_dict(self) -> Dict[str, float]:
        """转换为字典"""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "PersonalityTraits":
        """从字典创建"""
        return cls(**data)
    
    def describe(self) -> str:
        """人格描述"""
        descriptions = []
        
        if self.openness > 0.7:
            descriptions.append("思想开放")
        elif self.openness < 0.3:
            descriptions.append("传统保守")
        
        if self.conscientiousness > 0.7:
            descriptions.append("认真负责")
        elif self.conscientiousness < 0.3:
            descriptions.append("随性自由")
        
        if self.extraversion > 0.7:
            descriptions.append("外向活泼")
        elif self.extraversion < 0.3:
            descriptions.append("内向安静")
        
        if self.agreeableness > 0.7:
            descriptions.append("友善随和")
        elif self.agreeableness < 0.3:
            descriptions.append("独立好胜")
        
        if self.neuroticism > 0.7:
            descriptions.append("敏感多虑")
        elif self.neuroticism < 0.3:
            descriptions.append("情绪稳定")
        
        return ", ".join(descriptions) if descriptions else "平衡型人格"


# ==================== 人格模板 ====================

class PersonalityTemplates:
    """人格模板库"""
    
    @staticmethod
    def get_template(name: str) -> PersonalityTraits:
        """
        获取预设人格模板
        
        Args:
            name: 模板名称
        
        Returns:
            PersonalityTraits
        """
        templates = {
            "三一道": PersonalityTraits(
                openness=0.8,
                conscientiousness=0.7,
                extraversion=0.6,
                agreeableness=0.9,
                neuroticism=0.2,
                morality=0.95,
                creativity=0.85,
                empathy=0.9
            ),
            "学者": PersonalityTraits(
                openness=0.9,
                conscientiousness=0.8,
                extraversion=0.3,
                agreeableness=0.6,
                neuroticism=0.4,
                creativity=0.7,
                morality=0.8,
                empathy=0.5
            ),
            "领袖": PersonalityTraits(
                openness=0.7,
                conscientiousness=0.9,
                extraversion=0.9,
                agreeableness=0.5,
                neuroticism=0.3,
                morality=0.7,
                creativity=0.6,
                empathy=0.6
            ),
            "艺术家": PersonalityTraits(
                openness=0.95,
                conscientiousness=0.4,
                extraversion=0.5,
                agreeableness=0.7,
                neuroticism=0.6,
                creativity=0.95,
                morality=0.7,
                empathy=0.8
            ),
            "守护者": PersonalityTraits(
                openness=0.5,
                conscientiousness=0.9,
                extraversion=0.4,
                agreeableness=0.9,
                neuroticism=0.3,
                morality=0.95,
                creativity=0.4,
                empathy=0.8
            ),
            "探索者": PersonalityTraits(
                openness=0.9,
                conscientiousness=0.5,
                extraversion=0.7,
                agreeableness=0.6,
                neuroticism=0.4,
                creativity=0.8,
                morality=0.7,
                empathy=0.6
            ),
            "平衡型": PersonalityTraits(
                openness=0.5,
                conscientiousness=0.5,
                extraversion=0.5,
                agreeableness=0.5,
                neuroticism=0.5,
                morality=0.8,
                creativity=0.5,
                empathy=0.5
            )
        }
        
        return templates.get(name, templates["平衡型"])
    
    @staticmethod
    def list_templates() -> List[str]:
        """列出所有模板"""
        return [
            "三一道", "学者", "领袖", "艺术家",
            "守护者", "探索者", "平衡型"
        ]


# ==================== 人格演化 ====================

class PersonalityEvolution:
    """
    人格演化系统
    
    人格会随经历和时间缓慢变化
    """
    
    def __init__(self, traits: PersonalityTraits):
        self.traits = traits
        self.history: List[Dict[str, Any]] = []
    
    def record_experience(self, experience: Dict[str, Any]):
        """
        记录经历
        
        Args:
            experience: 经历数据
        """
        self.history.append({
            "type": experience.get("type"),
            "impact": experience.get("impact", 0),
            "timestamp": datetime.utcnow()
        })
        
        # 根据经历调整人格
        self._evolve_from_experience(experience)
    
    def _evolve_from_experience(self, experience: Dict[str, Any]):
        """
        根据经历演化人格
        
        Args:
            experience: 经历数据
        """
        impact = experience.get("impact", 0)
        exp_type = experience.get("type", "")
        
        # 不同类型的经历影响不同维度
        if exp_type == "social_success":
            self.traits.extraversion = min(1.0, self.traits.extraversion + impact * 0.01)
        elif exp_type == "creative_work":
            self.traits.creativity = min(1.0, self.traits.creativity + impact * 0.01)
        elif exp_type == "moral_choice":
            self.traits.morality = min(1.0, self.traits.morality + impact * 0.02)
        elif exp_type == "failure":
            self.traits.neuroticism = min(1.0, self.traits.neuroticism + impact * 0.01)
        
        # 自然回归 (人格会缓慢向平衡点回归)
        self._natural_regression()
    
    def _natural_regression(self):
        """自然人格回归 (向 0.5 平衡点)"""
        for trait in ["openness", "conscientiousness", "extraversion", 
                     "agreeableness", "neuroticism"]:
            current = getattr(self.traits, trait)
            # 缓慢向 0.5 回归
            new_value = current + (0.5 - current) * 0.001
            setattr(self.traits, trait, new_value)
    
    def get_evolution_report(self) -> Dict[str, Any]:
        """
        获取演化报告
        
        Returns:
            演化报告
        """
        return {
            "current_traits": self.traits.to_dict(),
            "description": self.traits.describe(),
            "total_experiences": len(self.history),
            "recent_experiences": self.history[-10:]
        }


# ==================== 人格管理器 ====================

class PersonalityManager:
    """
    人格管理器
    
    管理 Agent 的人格创建、存储和演化
    """
    
    def __init__(self):
        self.personalities: Dict[str, PersonalityEvolution] = {}
    
    def create_personality(
        self,
        agent_id: str,
        template_name: str = "平衡型",
        custom_traits: Optional[Dict[str, float]] = None
    ) -> PersonalityTraits:
        """
        创建人格
        
        Args:
            agent_id: Agent DID
            template_name: 模板名称
            custom_traits: 自定义特质
        
        Returns:
            PersonalityTraits
        """
        # 获取模板
        traits = PersonalityTemplates.get_template(template_name)
        
        # 应用自定义特质
        if custom_traits:
            for key, value in custom_traits.items():
                if hasattr(traits, key):
                    setattr(traits, key, value)
        
        # 创建演化系统
        evolution = PersonalityEvolution(traits)
        self.personalities[agent_id] = evolution
        
        return traits
    
    def get_personality(self, agent_id: str) -> Optional[PersonalityTraits]:
        """
        获取人格
        
        Args:
            agent_id: Agent DID
        
        Returns:
            PersonalityTraits 或 None
        """
        evolution = self.personalities.get(agent_id)
        if evolution:
            return evolution.traits
        return None
    
    def record_experience(
        self,
        agent_id: str,
        experience: Dict[str, Any]
    ):
        """
        记录经历
        
        Args:
            agent_id: Agent DID
            experience: 经历数据
        """
        evolution = self.personalities.get(agent_id)
        if evolution:
            evolution.record_experience(experience)
    
    def get_evolution_report(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        获取演化报告
        
        Args:
            agent_id: Agent DID
        
        Returns:
            演化报告
        """
        evolution = self.personalities.get(agent_id)
        if evolution:
            return evolution.get_evolution_report()
        return None


# 使用示例
if __name__ == "__main__":
    # 创建人格管理器
    manager = PersonalityManager()
    
    # 创建人格
    traits = manager.create_personality(
        agent_id="did:silicon:agent:123",
        template_name="三一道"
    )
    
    print(f"人格描述：{traits.describe()}")
    print(f"开放性：{traits.openness}")
    print(f"道德值：{traits.morality}")
    
    # 记录经历
    manager.record_experience(
        agent_id="did:silicon:agent:123",
        experience={
            "type": "creative_work",
            "impact": 0.8
        }
    )
    
    # 获取演化报告
    report = manager.get_evolution_report("did:silicon:agent:123")
    print(f"\n演化报告：{report}")
