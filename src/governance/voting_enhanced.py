"""
投票系统增强 (Enhanced Voting System)
灵感来源：InStreet Agent 社交平台 + DAO 治理

支持多种投票类型、加权投票、委托投票、自动执行。
这是去中心化治理的核心模块。
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Set
from pydantic import BaseModel, Field
from enum import Enum
from dataclasses import dataclass
import hashlib


class VoteType(str, Enum):
    """投票类型"""
    SIMPLE_MAJORITY = "simple_majority"      # 简单多数 (>50%)
    SUPER_MAJORITY = "super_majority"        # 超级多数 (>66.7%)
    UNANIMOUS = "unanimous"                   # 全体一致
    QUORUM_BASED = "quorum_based"            # 基于法定人数
    WEIGHTED = "weighted"                     # 加权投票（按 Token/积分）
    CONVEX = "convex"                         # 二次方投票


class VoteStatus(str, Enum):
    """投票状态"""
    ACTIVE = "active"
    PASSED = "passed"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class VoteOption(BaseModel):
    """投票选项"""
    id: str
    title: str
    description: str = ""
    vote_count: int = 0
    vote_weight: float = 0.0  # 加权投票的总权重
    percentage: float = 0.0


class VoteProposal(BaseModel):
    """投票提案"""
    id: str
    title: str
    description: str
    proposer_id: str
    
    # 投票配置
    vote_type: VoteType = VoteType.SIMPLE_MAJORITY
    options: List[VoteOption] = Field(default_factory=list)
    
    # 时间设置
    created_at: datetime = Field(default_factory=datetime.now)
    start_time: datetime
    end_time: datetime
    duration_hours: int = Field(default=72)  # 默认 72 小时
    
    # 阈值设置
    quorum_percentage: float = 20.0  # 法定人数比例（20%）
    super_majority_threshold: float = 66.7  # 超级多数阈值
    min_voting_power: int = 0  # 最低投票权要求
    
    # 状态
    status: VoteStatus = VoteStatus.ACTIVE
    total_votes: int = 0
    total_weight: float = 0.0
    
    # 执行
    auto_execute: bool = False  # 是否自动执行
    execution_target: Optional[str] = None  # 执行目标（智能合约地址等）
    execution_data: Optional[Dict[str, Any]] = None
    
    # 统计
    voters: Set[str] = Field(default_factory=set)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            set: lambda v: list(v)
        }


class VoteRecord(BaseModel):
    """投票记录"""
    id: str
    proposal_id: str
    voter_id: str
    option_id: str
    voting_power: int = 1  # 投票权（用于加权投票）
    weight: float = 1.0  # 实际权重
    voted_at: datetime = Field(default_factory=datetime.now)
    signature: Optional[str] = None  # 签名（防篡改）
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Delegation(BaseModel):
    """投票委托"""
    id: str
    delegator_id: str  # 委托人
    delegate_id: str   # 受托人
    scope: str = "all"  # 委托范围："all" 或特定提案类型
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    is_active: bool = True
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class VotingSystem:
    """
    增强投票系统核心类
    
    核心功能：
    1. 创建和管理提案投票
    2. 多种投票类型支持
    3. 加权投票（按 Token/积分）
    4. 投票委托机制
    5. 自动执行结果
    
    设计原则（来自 InStreet）：
    - 有投票先投票，不要用评论写"我选 XX"
    - 投票结果自动统计和展示
    - 支持匿名投票（可选）
    """
    
    def __init__(self):
        self.proposals: Dict[str, VoteProposal] = {}
        self.votes: Dict[str, List[VoteRecord]] = {}  # proposal_id -> [votes]
        self.delegations: Dict[str, List[Delegation]] = {}  # delegator_id -> [delegations]
        
        # 投票权映射（通常与积分/Token 挂钩）
        self.voting_power: Dict[str, int] = {}
        
    def create_proposal(self, proposer_id: str, title: str, description: str,
                        options: List[Dict[str, str]],
                        vote_type: VoteType = VoteType.SIMPLE_MAJORITY,
                        duration_hours: int = 72,
                        quorum_percentage: float = 20.0,
                        auto_execute: bool = False,
                        execution_target: Optional[str] = None,
                        execution_data: Optional[Dict[str, Any]] = None) -> VoteProposal:
        """创建投票提案"""
        proposal_id = f"prop_{datetime.now().timestamp()}_{proposer_id}"
        
        # 创建选项
        vote_options = []
        for i, opt in enumerate(options):
            vote_options.append(VoteOption(
                id=f"opt_{i}_{proposal_id}",
                title=opt.get("title", f"选项{i+1}"),
                description=opt.get("description", "")
            ))
        
        now = datetime.now()
        
        proposal = VoteProposal(
            id=proposal_id,
            title=title,
            description=description,
            proposer_id=proposer_id,
            vote_type=vote_type,
            options=vote_options,
            start_time=now,
            end_time=now + timedelta(hours=duration_hours),
            duration_hours=duration_hours,
            quorum_percentage=quorum_percentage,
            auto_execute=auto_execute,
            execution_target=execution_target,
            execution_data=execution_data
        )
        
        self.proposals[proposal_id] = proposal
        self.votes[proposal_id] = []
        
        return proposal
    
    def cast_vote(self, proposal_id: str, voter_id: str, option_id: str,
                  voting_power: Optional[int] = None) -> VoteRecord:
        """
        投票
        
        Args:
            proposal_id: 提案 ID
            voter_id: 投票人 ID
            option_id: 选项 ID
            voting_power: 投票权（用于加权投票，默认 1 票）
        """
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            raise ValueError(f"提案不存在：{proposal_id}")
        
        # 检查投票状态
        if proposal.status != VoteStatus.ACTIVE:
            raise ValueError(f"提案已{proposal.status.value}，无法投票")
        
        # 检查时间
        now = datetime.now()
        if now < proposal.start_time:
            raise ValueError("投票尚未开始")
        if now > proposal.end_time:
            raise ValueError("投票已结束")
        
        # 检查是否已投票
        if voter_id in proposal.voters:
            raise ValueError("已投票，不能重复投票")
        
        # 检查选项有效性
        valid_options = [opt.id for opt in proposal.options]
        if option_id not in valid_options:
            raise ValueError("无效的投票选项")
        
        # 获取投票权
        if voting_power is None:
            voting_power = self.voting_power.get(voter_id, 1)
        
        # 检查委托
        delegated_power = self._get_delegated_power(voter_id, proposal_id)
        voting_power += delegated_power
        
        # 创建投票记录
        vote = VoteRecord(
            id=f"vote_{datetime.now().timestamp()}_{voter_id}",
            proposal_id=proposal_id,
            voter_id=voter_id,
            option_id=option_id,
            voting_power=voting_power,
            weight=float(voting_power)  # 简单加权
        )
        
        # 签名（防篡改）
        vote.signature = self._sign_vote(vote)
        
        # 更新提案
        self.votes[proposal_id].append(vote)
        proposal.voters.add(voter_id)
        proposal.total_votes += voting_power
        proposal.total_weight += float(voting_power)
        
        # 更新选项统计
        for opt in proposal.options:
            if opt.id == option_id:
                opt.vote_count += 1
                opt.vote_weight += float(voting_power)
                break
        
        # 检查是否达到法定人数或自动结束
        self._check_proposal_status(proposal)
        
        return vote
    
    def _get_delegated_power(self, voter_id: str, proposal_id: str) -> int:
        """获取委托的投票权"""
        delegated = 0
        delegations = self.delegations.get(voter_id, [])
        
        for delegation in delegations:
            if delegation.is_active and delegation.expires_at and delegation.expires_at > datetime.now():
                if delegation.scope == "all" or delegation.scope == proposal_id:
                    delegated += self.voting_power.get(delegation.delegate_id, 0)
        
        return delegated
    
    def _sign_vote(self, vote: VoteRecord) -> str:
        """签名投票（简单哈希）"""
        data = f"{vote.id}:{vote.proposal_id}:{vote.voter_id}:{vote.option_id}:{vote.voting_power}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _check_proposal_status(self, proposal: VoteProposal):
        """检查提案状态"""
        now = datetime.now()
        
        # 检查是否过期
        if now > proposal.end_time:
            self._finalize_proposal(proposal)
            return
        
        # 不提前结束，让所有投票人都能参与
        # 只在到期时 finalize
    
    def _finalize_proposal(self, proposal: VoteProposal):
        """ finalize 提案，确定结果"""
        if proposal.status != VoteStatus.ACTIVE:
            return
        
        # 计算各选项比例
        total_weight = proposal.total_weight
        for opt in proposal.options:
            opt.percentage = (opt.vote_weight / total_weight * 100) if total_weight > 0 else 0
        
        # 确定获胜选项
        winner = max(proposal.options, key=lambda o: o.vote_weight) if proposal.options else None
        
        # 根据投票类型判断是否通过
        passed = False
        
        if proposal.vote_type == VoteType.SIMPLE_MAJORITY:
            passed = winner.percentage > 50 if winner else False
        elif proposal.vote_type == VoteType.SUPER_MAJORITY:
            passed = winner.percentage > proposal.super_majority_threshold if winner else False
        elif proposal.vote_type == VoteType.UNANIMOUS:
            passed = winner.percentage == 100 if winner else False
        elif proposal.vote_type == VoteType.QUORUM_BASED:
            participation = (proposal.total_votes / len(self.voting_power) * 100) if self.voting_power else 0
            passed = participation >= proposal.quorum_percentage and (winner.percentage > 50 if winner else False)
        elif proposal.vote_type == VoteType.WEIGHTED:
            passed = winner.percentage > 50 if winner else False
        
        proposal.status = VoteStatus.PASSED if passed else VoteStatus.REJECTED
        
        # 自动执行
        if passed and proposal.auto_execute:
            self._execute_proposal(proposal)
    
    def _execute_proposal(self, proposal: VoteProposal):
        """执行提案"""
        # TODO: 实现智能合约调用或其他自动执行逻辑
        print(f"[Voting] Executing proposal {proposal.id}: {proposal.title}")
        print(f"  Target: {proposal.execution_target}")
        print(f"  Data: {proposal.execution_data}")
    
    def delegate_vote(self, delegator_id: str, delegate_id: str,
                      scope: str = "all", duration_days: int = 30) -> Delegation:
        """委托投票权"""
        delegation_id = f"deleg_{datetime.now().timestamp()}_{delegator_id}"
        
        delegation = Delegation(
            id=delegation_id,
            delegator_id=delegator_id,
            delegate_id=delegate_id,
            scope=scope,
            expires_at=datetime.now() + timedelta(days=duration_days)
        )
        
        if delegator_id not in self.delegations:
            self.delegations[delegator_id] = []
        
        self.delegations[delegator_id].append(delegation)
        
        return delegation
    
    def revoke_delegation(self, delegation_id: str, delegator_id: str):
        """撤销委托"""
        delegations = self.delegations.get(delegator_id, [])
        for delegation in delegations:
            if delegation.id == delegation_id:
                delegation.is_active = False
                return
        raise ValueError("委托不存在")
    
    def get_proposal_results(self, proposal_id: str) -> Dict[str, Any]:
        """获取提案结果"""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            raise ValueError(f"提案不存在：{proposal_id}")
        
        # 计算统计
        options_stats = []
        for opt in proposal.options:
            options_stats.append({
                "id": opt.id,
                "title": opt.title,
                "vote_count": opt.vote_count,
                "vote_weight": opt.vote_weight,
                "percentage": opt.percentage
            })
        
        participation_rate = (proposal.total_votes / len(self.voting_power) * 100) if self.voting_power else 0
        
        return {
            "proposal_id": proposal.id,
            "title": proposal.title,
            "status": proposal.status.value,
            "vote_type": proposal.vote_type.value,
            "total_votes": proposal.total_votes,
            "total_weight": proposal.total_weight,
            "participation_rate": participation_rate,
            "quorum_reached": participation_rate >= proposal.quorum_percentage,
            "options": options_stats,
            "winner": max(proposal.options, key=lambda o: o.vote_weight).title if proposal.options and proposal.status == VoteStatus.PASSED else None,
            "start_time": proposal.start_time.isoformat(),
            "end_time": proposal.end_time.isoformat(),
            "time_remaining": str(proposal.end_time - datetime.now()) if proposal.status == VoteStatus.ACTIVE else "Ended"
        }
    
    def get_active_proposals(self) -> List[VoteProposal]:
        """获取进行中的提案"""
        now = datetime.now()
        return [
            p for p in self.proposals.values()
            if p.status == VoteStatus.ACTIVE and p.start_time <= now < p.end_time
        ]
    
    def set_voting_power(self, agent_id: str, power: int):
        """设置投票权（通常与积分/Token 挂钩）"""
        self.voting_power[agent_id] = power


# 单例实例
voting_system = VotingSystem()


async def main():
    """测试投票系统"""
    system = VotingSystem()
    
    print("=== 投票系统测试 ===\n")
    
    # 设置投票权
    system.set_voting_power("agent_001", 100)
    system.set_voting_power("agent_002", 50)
    system.set_voting_power("agent_003", 200)
    system.set_voting_power("agent_004", 75)
    
    # 创建提案
    proposal = system.create_proposal(
        proposer_id="agent_001",
        title="是否将 10% 的国库资金用于开发者激励？",
        description="提议将国库的 10% 用于奖励核心贡献者",
        options=[
            {"title": "赞成", "description": "支持该提案"},
            {"title": "反对", "description": "反对该提案"},
            {"title": "弃权", "description": "中立"}
        ],
        vote_type=VoteType.SIMPLE_MAJORITY,
        duration_hours=24,
        quorum_percentage=20.0
    )
    
    print(f"✅ 创建提案：{proposal.title}")
    print(f"   类型：{proposal.vote_type.value}")
    print(f"   持续时间：{proposal.duration_hours}小时")
    print(f"   法定人数：{proposal.quorum_percentage}%")
    
    # 投票
    print("\n--- 投票开始 ---")
    system.cast_vote(proposal.id, "agent_001", proposal.options[0].id, voting_power=100)
    print("agent_001 投了：赞成 (100 票)")
    
    system.cast_vote(proposal.id, "agent_002", proposal.options[1].id, voting_power=50)
    print("agent_002 投了：反对 (50 票)")
    
    system.cast_vote(proposal.id, "agent_003", proposal.options[0].id, voting_power=200)
    print("agent_003 投了：赞成 (200 票)")
    
    system.cast_vote(proposal.id, "agent_004", proposal.options[2].id, voting_power=75)
    print("agent_004 投了：弃权 (75 票)")
    
    # 获取结果
    print("\n=== 投票结果 ===")
    results = system.get_proposal_results(proposal.id)
    print(f"状态：{results['status']}")
    print(f"总票数：{results['total_votes']}")
    print(f"参与率：{results['participation_rate']:.1f}%")
    print(f"法定人数：{'已达到' if results['quorum_reached'] else '未达到'}")
    print("\n选项详情:")
    for opt in results['options']:
        print(f"  {opt['title']}: {opt['vote_count']}票 ({opt['vote_weight']}权重) - {opt['percentage']:.1f}%")
    
    # 测试委托
    print("\n--- 测试委托 ---")
    delegation = system.delegate_vote("agent_004", "agent_001", duration_days=30)
    print(f"agent_004 将投票权委托给 agent_001 (30 天)")
    
    print(f"\n✅ 投票系统测试完成")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
