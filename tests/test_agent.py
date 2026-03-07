"""
Agent 系统测试
"""

import pytest
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent.core import Agent, AgentManager, AgentState


def test_agent_creation():
    """测试 Agent 创建"""
    agent = Agent(
        id="did:silicon:agent:1234567890abcdef1234567890abcdef",
        name="三一"
    )
    
    assert agent.id == "did:silicon:agent:1234567890abcdef1234567890abcdef"
    assert agent.name == "三一"
    assert agent.state == AgentState.IDLE
    assert agent.created_at is not None
    print(f"[OK] Agent 创建测试通过：{agent.name}")


def test_agent_state():
    """测试 Agent 状态"""
    agent = Agent(id="did:silicon:agent:123", name="Test")
    
    # 初始状态应该是 IDLE
    assert agent.state == AgentState.IDLE
    
    print("[OK] Agent 状态测试通过")


def test_agent_manager():
    """测试 Agent 管理器"""
    manager = AgentManager()
    
    # 创建 Agent
    agent1 = manager.create_agent(
        did="did:silicon:agent:111",
        name="Agent 1"
    )
    agent2 = manager.create_agent(
        did="did:silicon:agent:222",
        name="Agent 2"
    )
    
    # 获取 Agent
    assert manager.get_agent_count() == 2
    assert manager.get_agent("did:silicon:agent:111") == agent1
    assert manager.get_agent("did:silicon:agent:222") == agent2
    
    # 列出所有 Agent
    agents = manager.list_agents()
    assert len(agents) == 2
    
    # 删除 Agent
    manager.remove_agent("did:silicon:agent:111")
    assert manager.get_agent_count() == 1
    assert manager.get_agent("did:silicon:agent:111") is None
    
    print("[OK] Agent 管理器测试通过")


async def test_agent_process():
    """测试 Agent 处理流程"""
    agent = Agent(id="did:silicon:agent:123", name="Test")
    
    # 处理输入
    result = await agent.process({"message": "你好"})
    
    # 检查状态变化
    assert agent.state == AgentState.IDLE  # 处理完应该回到 IDLE
    
    print("[OK] Agent 处理流程测试通过")


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("Agent 系统测试")
    print("=" * 50)
    print()
    
    tests = [
        test_agent_creation,
        test_agent_state,
        test_agent_manager,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {test.__name__}: {e}")
            failed += 1
    
    # 异步测试
    try:
        asyncio.run(test_agent_process())
        passed += 1
    except Exception as e:
        print(f"[ERROR] test_agent_process: {e}")
        failed += 1
    
    print()
    print("=" * 50)
    print(f"测试结果：{passed} 通过，{failed} 失败")
    print("=" * 50)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
