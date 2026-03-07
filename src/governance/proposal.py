"""
社区治理系统

DAO 治理框架：提案 + 投票 + 执行
"""

from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel
from datetime import datetime, timedelta
from enum import Enum
import uuid


# ==================== 提案类型 ====================

class ProposalType(str, Enum):
    """提案类型"""
    PROTOCOL_UPGRADE = "protocol_upgrade"  # 协议升级
    PARAMETER_CHANGE = "parameter_change"  # 参数修改
    FUND_ALLOCATION = "fund_allocation"  # 资金分配
    GOVERNANCE_CHANGE = "governance_change"  # 治理变更
    COMMUNITY_PROJECT = "community_project"  # 社区项目


class ProposalStatus(str, Enum):
    """提案状态"""
    DRAFT = "draft"  # 草稿
    ACTIVE = "active"  # 进行中
    PASSED = "passed"  # 已通过
    REJECTED = "rejected"  # 已拒绝
    EXECUTED = "executed"  # 已执行
    CANCELLED = "cancelled"  # 已取消


# ==================== 提案模型 ====================

class Proposal(BaseModel):
    """治理提案"""
    id: str
    proposer: str  # 提案人
    title: str
    description: str
    proposal_type: ProposalType
    status: ProposalStatus = ProposalStatus.DRAFT
    votes_for: int = 0  # 赞成票
    votes_against: int = 0  # 反对票
    votes_abstain: int = 0  # 弃权票
    total_supply: int = 0  # 总供应量 (用于计算通过率)
    voting_power_required: float = 0.5  # 通过所需票数比例 (50%)
    quorum_required: float = 0.1  # 法定人数比例 (10%)
    created_at: datetime = None
    voting_start: Optional[datetime] = None
    voting_end: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow()
        super().__init__(**data)
    
    def activate(self, voting_duration_days: int = 7):
        """激活提案"""
        if self.status != ProposalStatus.DRAFT:
            raise ValueError("只有草稿提案可以激活")
        
        self.status = ProposalStatus.ACTIVE
        self.voting_start = datetime.utcnow()
        self.voting_end = self.voting_start + timedelta(days=voting_duration_days)
    
    def cast_vote(self, voter_id: str, vote: str, voting_power: int):
        """
        投票
        
        Args:
            voter_id: 投票人 ID
            vote: 投票选项 (for/against/abstain)
            voting_power: 投票权重
        """
        if self.status != ProposalStatus.ACTIVE:
            raise ValueError("提案不在投票期")
        
        if datetime.utcnow() > self.voting_end:
            raise ValueError("投票已结束")
        
        if vote == "for":
            self.votes_for += voting_power
        elif vote == "against":
            self.votes_against += voting_power
        elif vote == "abstain":
            self.votes_abstain += voting_power
    
    def tally_votes(self) -> bool:
        """
        计票并确定是否通过
        
        Returns:
            是否通过
        """
        if self.status != ProposalStatus.ACTIVE:
            return False
        
        if datetime.utcnow() < self.voting_end:
            return False
        
        total_votes = self.votes_for + self.votes_against + self.votes_abstain
        
        # 检查法定人数
        quorum_met = total_votes >= (self.total_supply * self.quorum_required)
        
        if not quorum_met:
            self.status = ProposalStatus.REJECTED
            return False
        
        # 检查通过率
        approval_rate = self.votes_for / (self.votes_for + self.votes_against) if (self.votes_for + self.votes_against) > 0 else 0
        passed = approval_rate >= self.voting_power_required
        
        self.status = ProposalStatus.PASSED if passed else ProposalStatus.REJECTED
        return passed
    
    def execute(self):
        """执行提案"""
        if self.status != ProposalStatus.PASSED:
            raise ValueError("只有通过的提案可以执行")
        
        self.status = ProposalStatus.EXECUTED
        self.executed_at = datetime.utcnow()
    
    def cancel(self):
        """取消提案"""
        if self.status in [ProposalStatus.EXECUTED, ProposalStatus.CANCELLED]:
            raise ValueError("提案已执行或已取消")
        
        self.status = ProposalStatus.CANCELLED
    
    def get_approval_rate(self) -> float:
        """获取支持率"""
        total = self.votes_for + self.votes_against
        if total == 0:
            return 0.0
        return self.votes_for / total
    
    def get_participation_rate(self) -> float:
        """获取参与率"""
        if self.total_supply == 0:
            return 0.0
        total_votes = self.votes_for + self.votes_against + self.votes_abstain
        return total_votes / self.total_supply


# ==================== 投票记录 ====================

class Vote(BaseModel):
    """投票记录"""
    id: str
    proposal_id: str
    voter_id: str
    vote: str  # for/against/abstain
    voting_power: int
    timestamp: datetime = None
    signature: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)


# ==================== 治理管理器 ====================

class GovernanceManager:
    """
    治理管理器
    
    管理提案和投票
    """
    
    def __init__(self):
        self.proposals: Dict[str, Proposal] = {}
        self.votes: Dict[str, List[Vote]] = {}  # proposal_id -> [votes]
        self.voter_has_voted: Dict[str, Set[str]] = {}  # voter_id -> {proposal_ids}
    
    def create_proposal(
        self,
        proposer: str,
        title: str,
        description: str,
        proposal_type: ProposalType,
        voting_duration_days: int = 7,
        metadata: Dict[str, Any] = None
    ) -> Proposal:
        """
        创建提案
        
        Args:
            proposer: 提案人
            title: 标题
            description: 描述
            proposal_type: 提案类型
            voting_duration_days: 投票时长 (天)
            metadata: 元数据
        
        Returns:
            Proposal
        """
        proposal = Proposal(
            proposer=proposer,
            title=title,
            description=description,
            proposal_type=proposal_type,
            metadata=metadata or {}
        )
        
        # 激活提案
        proposal.activate(voting_duration_days)
        
        self.proposals[proposal.id] = proposal
        self.votes[proposal.id] = []
        
        return proposal
    
    def cast_vote(
        self,
        proposal_id: str,
        voter_id: str,
        vote: str,
        voting_power: int
    ) -> Vote:
        """
        投票
        
        Args:
            proposal_id: 提案 ID
            voter_id: 投票人 ID
            vote: 投票选项
            voting_power: 投票权重
        
        Returns:
            Vote
        """
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            raise ValueError("提案不存在")
        
        # 检查是否已投票
        if voter_id in self.voter_has_voted:
            if proposal_id in self.voter_has_voted[voter_id]:
                raise ValueError("已投票")
        
        # 创建投票记录
        vote_record = Vote(
            proposal_id=proposal_id,
            voter_id=voter_id,
            vote=vote,
            voting_power=voting_power
        )
        
        # 更新提案
        proposal.cast_vote(voter_id, vote, voting_power)
        
        # 存储投票记录
        self.votes[proposal_id].append(vote_record)
        
        # 标记已投票
        if voter_id not in self.voter_has_voted:
            self.voter_has_voted[voter_id] = set()
        self.voter_has_voted[voter_id].add(proposal_id)
        
        return vote_record
    
    def get_proposal(self, proposal_id: str) -> Optional[Proposal]:
        """获取提案"""
        return self.proposals.get(proposal_id)
    
    def get_active_proposals(self) -> List[Proposal]:
        """获取进行中的提案"""
        return [
            p for p in self.proposals.values()
            if p.status == ProposalStatus.ACTIVE
        ]
    
    def get_proposals_by_proposer(self, proposer: str) -> List[Proposal]:
        """获取提案人的所有提案"""
        return [
            p for p in self.proposals.values()
            if p.proposer == proposer
        ]
    
    def get_user_votes(self, voter_id: str) -> List[Vote]:
        """获取用户的投票记录"""
        user_votes = []
        for proposal_votes in self.votes.values():
            for vote in proposal_votes:
                if vote.voter_id == voter_id:
                    user_votes.append(vote)
        return user_votes
    
    def tally_proposal(self, proposal_id: str) -> bool:
        """计票"""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return False
        
        return proposal.tally_votes()
    
    def execute_proposal(self, proposal_id: str):
        """执行提案"""
        proposal = self.proposals.get(proposal_id)
        if proposal:
            proposal.execute()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取治理统计"""
        return {
            "total_proposals": len(self.proposals),
            "active_proposals": len(self.get_active_proposals()),
            "passed_proposals": sum(1 for p in self.proposals.values() if p.status == ProposalStatus.PASSED),
            "rejected_proposals": sum(1 for p in self.proposals.values() if p.status == ProposalStatus.REJECTED),
            "executed_proposals": sum(1 for p in self.proposals.values() if p.status == ProposalStatus.EXECUTED),
            "total_votes": sum(len(votes) for votes in self.votes.values()),
            "total_voters": len(self.voter_has_voted)
        }


# 使用示例
if __name__ == "__main__":
    # 创建治理管理器
    gov = GovernanceManager()
    
    print("创建提案...")
    proposal = gov.create_proposal(
        proposer="user_1",
        title="增加挖矿奖励",
        description="建议将挖矿奖励从 40% 提升到 50%",
        proposal_type=ProposalType.PARAMETER_CHANGE,
        voting_duration_days=7
    )
    print(f"提案 ID: {proposal.id}")
    print(f"状态：{proposal.status}")
    print(f"投票截止：{proposal.voting_end}")
    
    # 投票
    print("\n投票...")
    gov.cast_vote(proposal.id, "user_2", "for", 1000)
    gov.cast_vote(proposal.id, "user_3", "for", 1500)
    gov.cast_vote(proposal.id, "user_4", "against", 500)
    gov.cast_vote(proposal.id, "user_5", "abstain", 200)
    
    print(f"赞成票：{proposal.votes_for}")
    print(f"反对票：{proposal.votes_against}")
    print(f"弃权票：{proposal.votes_abstain}")
    print(f"支持率：{proposal.get_approval_rate():.2%}")
    print(f"参与率：{proposal.get_participation_rate():.2%}")
    
    # 获取统计
    print("\n治理统计:")
    stats = gov.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
