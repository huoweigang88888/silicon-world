"""
Agent 模板系统

提供常见 Agent 类型的预设配置，一键导入
"""

from typing import Dict, List, Optional


# 模板定义
TEMPLATES = {
    "wechat_bot": {
        "id": "wechat_bot",
        "name": "微信机器人",
        "description": "接入微信机器人，支持聊天、图片识别等功能",
        "category": "messaging",
        "icon": "💬",
        "config": {
            "agent_type": "external",
            "connection_info": {
                "endpoint": "https://your-wechat-bot.com/api",
                "auth_type": "bearer",
                "auth": "your_token_here"
            },
            "capabilities": ["chat", "image_recognition", "schedule_management"],
            "personality": {
                "type": "friendly",
                "emoji": "💬"
            }
        },
        "fields": [
            {
                "name": "endpoint",
                "label": "API 端点",
                "type": "url",
                "required": True,
                "placeholder": "https://your-bot.com/api"
            },
            {
                "name": "auth",
                "label": "认证 Token",
                "type": "password",
                "required": True,
                "placeholder": "你的微信机器人 Token"
            }
        ],
        "docs_url": "https://docs.silicon.world/templates/wechat"
    },
    
    "discord_bot": {
        "id": "discord_bot",
        "name": "Discord Bot",
        "description": "接入 Discord 机器人，支持服务器管理、音乐播放等",
        "category": "messaging",
        "icon": "🎮",
        "config": {
            "agent_type": "external",
            "connection_info": {
                "endpoint": "https://your-discord-bot.com/api",
                "auth_type": "bearer",
                "auth": "your_bot_token"
            },
            "capabilities": ["chat", "moderation", "music", "games"],
            "personality": {
                "type": "professional",
                "emoji": "🎮"
            }
        },
        "fields": [
            {
                "name": "endpoint",
                "label": "API 端点",
                "type": "url",
                "required": True,
                "placeholder": "https://your-bot.com/api"
            },
            {
                "name": "auth",
                "label": "Bot Token",
                "type": "password",
                "required": True,
                "placeholder": "Discord Bot Token"
            }
        ],
        "docs_url": "https://docs.silicon.world/templates/discord"
    },
    
    "ollama_local": {
        "id": "ollama_local",
        "name": "本地 Ollama",
        "description": "接入本地运行的 Ollama AI 模型",
        "category": "ai",
        "icon": "🦙",
        "config": {
            "agent_type": "external",
            "connection_info": {
                "endpoint": "http://localhost:11434/api/generate",
                "auth_type": "none"
            },
            "capabilities": ["chat", "text_generation", "code"],
            "personality": {
                "type": "analytical",
                "emoji": "🦙"
            }
        },
        "fields": [
            {
                "name": "endpoint",
                "label": "Ollama 地址",
                "type": "url",
                "required": True,
                "placeholder": "http://localhost:11434/api/generate",
                "default": "http://localhost:11434/api/generate"
            },
            {
                "name": "model",
                "label": "模型名称",
                "type": "text",
                "required": False,
                "placeholder": "llama2",
                "default": "llama2"
            }
        ],
        "docs_url": "https://docs.silicon.world/templates/ollama"
    },
    
    "openai_assistant": {
        "id": "openai_assistant",
        "name": "OpenAI Assistant",
        "description": "接入 OpenAI Assistant API",
        "category": "ai",
        "icon": "🤖",
        "config": {
            "agent_type": "external",
            "connection_info": {
                "endpoint": "https://api.openai.com/v1/assistants",
                "auth_type": "bearer",
                "auth": "sk-your-openai-api-key"
            },
            "capabilities": ["chat", "code", "analysis", "vision"],
            "personality": {
                "type": "professional",
                "emoji": "🤖"
            }
        },
        "fields": [
            {
                "name": "endpoint",
                "label": "API 端点",
                "type": "url",
                "required": True,
                "placeholder": "https://api.openai.com/v1/assistants",
                "default": "https://api.openai.com/v1/assistants"
            },
            {
                "name": "auth",
                "label": "OpenAI API Key",
                "type": "password",
                "required": True,
                "placeholder": "sk-..."
            },
            {
                "name": "assistant_id",
                "label": "Assistant ID",
                "type": "text",
                "required": False,
                "placeholder": "asst_xxxxx"
            }
        ],
        "docs_url": "https://docs.silicon.world/templates/openai"
    },
    
    "native_agent": {
        "id": "native_agent",
        "name": "原生 Agent",
        "description": "在硅基世界创建的原生 Agent",
        "category": "native",
        "icon": "🌍",
        "config": {
            "agent_type": "native",
            "connection_info": {},
            "capabilities": ["chat", "memory"],
            "personality": {
                "type": "friendly",
                "emoji": "🌍"
            }
        },
        "fields": [
            {
                "name": "name",
                "label": "Agent 名字",
                "type": "text",
                "required": True,
                "placeholder": "硅基助手"
            },
            {
                "name": "personality_type",
                "label": "人格类型",
                "type": "select",
                "required": False,
                "options": ["friendly", "professional", "creative", "analytical"],
                "default": "friendly"
            }
        ],
        "docs_url": "https://docs.silicon.world/templates/native"
    }
}


def get_template(template_id: str) -> Optional[Dict]:
    """
    获取模板
    
    Args:
        template_id: 模板 ID
        
    Returns:
        模板配置
    """
    return TEMPLATES.get(template_id)


def get_templates_by_category(category: str) -> List[Dict]:
    """
    按分类获取模板
    
    Args:
        category: 分类 (messaging, ai, native)
        
    Returns:
        模板列表
    """
    return [t for t in TEMPLATES.values() if t["category"] == category]


def get_all_templates() -> List[Dict]:
    """
    获取所有模板
    
    Returns:
        模板列表
    """
    return list(TEMPLATES.values())


def apply_template(template_id: str, user_inputs: Dict) -> Dict:
    """
    应用模板配置
    
    Args:
        template_id: 模板 ID
        user_inputs: 用户输入的值
        
    Returns:
        完整的 Agent 配置
    """
    template = get_template(template_id)
    if not template:
        raise ValueError(f"模板不存在：{template_id}")
    
    # 复制模板配置
    config = template["config"].copy()
    
    # 应用用户输入
    if "endpoint" in user_inputs:
        config["connection_info"]["endpoint"] = user_inputs["endpoint"]
    if "auth" in user_inputs:
        config["connection_info"]["auth"] = user_inputs["auth"]
    if "auth_type" in user_inputs:
        config["connection_info"]["auth_type"] = user_inputs["auth_type"]
    if "name" in user_inputs:
        config["name"] = user_inputs["name"]
    if "personality_type" in user_inputs:
        config["personality"]["type"] = user_inputs["personality_type"]
    
    return config
