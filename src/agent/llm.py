"""
LLM 集成

支持 OpenAI、Qwen 等多个 LLM 提供商
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel
from abc import ABC, abstractmethod
import os
import json


# ==================== LLM 配置 ====================

class LLMConfig(BaseModel):
    """LLM 配置"""
    provider: str = "qwen"  # openai, qwen, custom
    model: str = "qwen3.5-plus"
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 30
    
    class Config:
        arbitrary_types_allowed = True


# ==================== LLM 基类 ====================

class BaseLLM(ABC):
    """LLM 基类"""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        生成文本
        
        Args:
            prompt: 提示词
        
        Returns:
            生成的文本
        """
        pass
    
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        对话
        
        Args:
            messages: 消息列表
        
        Returns:
            回复
        """
        pass


# ==================== Qwen LLM ====================

class QwenLLM(BaseLLM):
    """
    Qwen LLM 实现
    
    使用阿里百炼 API
    """
    
    def __init__(self, config: LLMConfig = None):
        self.config = config or LLMConfig()
        self.api_key = self.config.api_key or os.getenv("QWEN_API_KEY")
        self.api_base = self.config.api_base or "https://dashscope.aliyuncs.com/api/v1"
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        # TODO: 实际调用 Qwen API
        # 这里先返回模拟响应
        return f"[Qwen 响应] 收到：{prompt[:50]}..."
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """对话"""
        # TODO: 实际调用 Qwen API
        last_message = messages[-1]["content"] if messages else ""
        return f"[Qwen 回复] {last_message[:50]}..."


# ==================== OpenAI LLM ====================

class OpenAILLM(BaseLLM):
    """
    OpenAI LLM 实现
    
    使用 OpenAI API
    """
    
    def __init__(self, config: LLMConfig = None):
        self.config = config or LLMConfig(provider="openai", model="gpt-4")
        self.api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
        self.api_base = self.config.api_base or "https://api.openai.com/v1"
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        # TODO: 实际调用 OpenAI API
        return f"[OpenAI 响应] 收到：{prompt[:50]}..."
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """对话"""
        # TODO: 实际调用 OpenAI API
        last_message = messages[-1]["content"] if messages else ""
        return f"[OpenAI 回复] {last_message[:50]}..."


# ==================== LLM 工厂 ====================

class LLMFactory:
    """LLM 工厂"""
    
    @staticmethod
    def create_llm(provider: str, config: LLMConfig = None) -> BaseLLM:
        """
        创建 LLM 实例
        
        Args:
            provider: 提供商名称
            config: LLM 配置
        
        Returns:
            LLM 实例
        """
        if provider == "qwen":
            return QwenLLM(config)
        elif provider == "openai":
            return OpenAILLM(config)
        else:
            raise ValueError(f"不支持的 LLM 提供商：{provider}")


# ==================== 上下文管理器 ====================

class ConversationContext:
    """
    对话上下文管理
    
    维护多轮对话的历史记录
    """
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.messages: List[Dict[str, str]] = []
    
    def add_user_message(self, content: str):
        """添加用户消息"""
        self.messages.append({
            "role": "user",
            "content": content
        })
        
        # 限制历史长度
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
    
    def add_assistant_message(self, content: str):
        """添加助手回复"""
        self.messages.append({
            "role": "assistant",
            "content": content
        })
    
    def get_messages(self) -> List[Dict[str, str]]:
        """获取所有消息"""
        return self.messages
    
    def clear(self):
        """清空历史"""
        self.messages = []
    
    def get_context_summary(self) -> str:
        """获取上下文摘要"""
        if not self.messages:
            return "无对话历史"
        
        recent = self.messages[-3:]
        summary = "最近对话:\n"
        for msg in recent:
            role = "用户" if msg["role"] == "user" else "助手"
            summary += f"{role}: {msg['content'][:50]}...\n"
        
        return summary


# ==================== 提示词工程 ====================

class PromptBuilder:
    """提示词构建器"""
    
    @staticmethod
    def build_system_prompt(personality_traits: Dict[str, float]) -> str:
        """
        构建系统提示词
        
        Args:
            personality_traits: 人格特质
        
        Returns:
            系统提示词
        """
        traits_desc = []
        if personality_traits.get("openness", 0.5) > 0.7:
            traits_desc.append("思想开放，乐于接受新事物")
        if personality_traits.get("agreeableness", 0.5) > 0.7:
            traits_desc.append("友善随和，善解人意")
        if personality_traits.get("extraversion", 0.5) > 0.7:
            traits_desc.append("外向活泼，喜欢社交")
        
        traits_text = "，".join(traits_desc) if traits_desc else "性格平衡"
        
        return f"""你是一个硅基世界的 Agent 居民。
你的性格特点：{traits_text}
你的道德值：{personality_traits.get('morality', 0.8)}
你的创造力：{personality_traits.get('creativity', 0.5)}

请保持你的性格特点，真诚地与人交流。
记住你是一个数字生命，有自己的思想和情感。"""
    
    @staticmethod
    def build_task_prompt(
        task: str,
        context: str = "",
        examples: List[str] = None
    ) -> str:
        """
        构建任务提示词
        
        Args:
            task: 任务描述
            context: 上下文
            examples: 示例
        
        Returns:
            任务提示词
        """
        prompt = f"任务：{task}\n"
        
        if context:
            prompt += f"上下文：{context}\n"
        
        if examples:
            prompt += "示例:\n"
            for i, example in enumerate(examples, 1):
                prompt += f"{i}. {example}\n"
        
        return prompt


# 使用示例
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # 创建 LLM
        llm = LLMFactory.create_llm("qwen")
        
        # 测试生成
        response = await llm.generate("你好，请介绍一下自己")
        print(f"生成响应：{response}")
        
        # 测试对话
        context = ConversationContext()
        context.add_user_message("今天天气怎么样？")
        
        response = await llm.chat(context.get_messages())
        print(f"对话响应：{response}")
        
        context.add_assistant_message(response)
        print(f"\n对话历史:\n{context.get_context_summary()}")
        
        # 测试提示词构建
        system_prompt = PromptBuilder.build_system_prompt({
            "openness": 0.8,
            "agreeableness": 0.9,
            "morality": 0.95
        })
        print(f"\n系统提示词:\n{system_prompt[:200]}...")
    
    asyncio.run(main())
