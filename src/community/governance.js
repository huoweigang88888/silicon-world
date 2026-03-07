/**
 * DAO 治理系统
 * 
 * 投票、提案、社区基金
 */

const { EventEmitter } = require('events');

/**
 * 提案系统
 */
class ProposalSystem extends EventEmitter {
    constructor() {
        super();
        this.proposals = new Map(); // proposalId -> proposal
        this.userProposals = new Map(); // userId -> [proposalIds]
        this.nextProposalId = 1;
        
        this.config = {
            minReputation: 100, // 最低声望要求
            votingPeriod: 7 * 24 * 60 * 60 * 1000, // 7 天投票期
            quorumRate: 0.1, // 10% 参与率
            passRate: 0.5 // 50% 通过率
        };
    }
    
    /**
     * 创建提案
     */
    createProposal(authorId, title, description, type, data = {}) {
        const proposalId = `prop_${this.nextProposalId++}`;
        
        const proposal = {
            id: proposalId,
            authorId,
            title,
            description,
            type, // feature, change, fund, emergency
            data,
            status: 'active', // active, passed, rejected, expired, executed
            createdAt: Date.now(),
            expiresAt: Date.now() + this.config.votingPeriod,
            votesFor: 0,
            votesAgainst: 0,
            votesAbstain: 0,
            voters: new Set(),
            executionCount: 0
        };
        
        this.proposals.set(proposalId, proposal);
        
        if (!this.userProposals.has(authorId)) {
            this.userProposals.set(authorId, []);
        }
        this.userProposals.get(authorId).push(proposalId);
        
        this.emit('proposal_created', proposal);
        
        return proposal;
    }
    
    /**
     * 投票
     */
    vote(proposalId, voterId, choice, weight = 1) {
        const proposal = this.proposals.get(proposalId);
        if (!proposal) {
            return { success: false, error: '提案不存在' };
        }
        
        if (proposal.status !== 'active') {
            return { success: false, error: '提案已结束' };
        }
        
        if (Date.now() > proposal.expiresAt) {
            proposal.status = 'expired';
            return { success: false, error: '提案已过期' };
        }
        
        // 检查是否已投票
        if (proposal.voters.has(voterId)) {
            return { success: false, error: '已投票' };
        }
        
        // 记录投票
        proposal.voters.add(voterId);
        
        switch (choice) {
            case 'for':
                proposal.votesFor += weight;
                break;
            case 'against':
                proposal.votesAgainst += weight;
                break;
            case 'abstain':
                proposal.votesAbstain += weight;
                break;
        }
        
        this.emit('vote_cast', { proposalId, voterId, choice, weight });
        
        return { success: true };
    }
    
    /**
     * 结束提案
     */
    concludeProposal(proposalId) {
        const proposal = this.proposals.get(proposalId);
        if (!proposal || proposal.status !== 'active') {
            return { success: false, error: '提案无效' };
        }
        
        // 检查参与率
        const totalVotes = proposal.votesFor + proposal.votesAgainst + proposal.votesAbstain;
        const eligibleVoters = this.userProposals.size;
        const participationRate = totalVotes / eligibleVoters;
        
        if (participationRate < this.config.quorumRate) {
            proposal.status = 'rejected';
            proposal.rejectReason = '参与率不足';
            this.emit('proposal_rejected', { proposalId, reason: '参与率不足' });
            return { success: false, error: '参与率不足' };
        }
        
        // 检查通过率
        const validVotes = proposal.votesFor + proposal.votesAgainst;
        const passRate = validVotes > 0 ? proposal.votesFor / validVotes : 0;
        
        if (passRate >= this.config.passRate) {
            proposal.status = 'passed';
            this.emit('proposal_passed', proposal);
            return { success: true, status: 'passed' };
        } else {
            proposal.status = 'rejected';
            this.emit('proposal_rejected', proposal);
            return { success: true, status: 'rejected' };
        }
    }
    
    /**
     * 执行提案
     */
    executeProposal(proposalId, executorId) {
        const proposal = this.proposals.get(proposalId);
        if (!proposal || proposal.status !== 'passed') {
            return { success: false, error: '提案未通过' };
        }
        
        proposal.executionCount++;
        proposal.executedAt = Date.now();
        proposal.executedBy = executorId;
        
        this.emit('proposal_executed', proposal);
        
        return { success: true };
    }
    
    /**
     * 获取提案列表
     */
    getProposals(filters = {}) {
        let proposals = Array.from(this.proposals.values());
        
        if (filters.status) {
            proposals = proposals.filter(p => p.status === filters.status);
        }
        
        if (filters.type) {
            proposals = proposals.filter(p => p.type === filters.type);
        }
        
        if (filters.authorId) {
            proposals = proposals.filter(p => p.authorId === filters.authorId);
        }
        
        // 排序
        proposals.sort((a, b) => b.createdAt - a.createdAt);
        
        // 分页
        const page = filters.page || 1;
        const limit = filters.limit || 20;
        const start = (page - 1) * limit;
        
        return {
            proposals: proposals.slice(start, start + limit),
            total: proposals.length,
            page,
            limit,
            totalPages: Math.ceil(proposals.length / limit)
        };
    }
    
    /**
     * 获取提案详情
     */
    getProposal(proposalId) {
        const proposal = this.proposals.get(proposalId);
        if (proposal) {
            const totalVotes = proposal.votesFor + proposal.votesAgainst + proposal.votesAbstain;
            return {
                ...proposal,
                totalVotes,
                participationRate: proposal.voters.size / this.userProposals.size,
                passRate: totalVotes > 0 ? proposal.votesFor / totalVotes : 0
            };
        }
        return null;
    }
    
    /**
     * 更新配置
     */
    updateConfig(newConfig) {
        Object.assign(this.config, newConfig);
        this.emit('config_updated', this.config);
    }
    
    /**
     * 清除
     */
    clear() {
        this.proposals.clear();
        this.userProposals.clear();
    }
}

/**
 * 投票系统
 */
class VotingSystem extends EventEmitter {
    constructor() {
        super();
        this.elections = new Map(); // electionId -> election
        this.ballots = new Map(); // ballotId -> ballot
        this.nextElectionId = 1;
        this.nextBallotId = 1;
    }
    
    /**
     * 创建选举
     */
    createElection(title, description, positions, candidates, duration = 7 * 24 * 60 * 60 * 1000) {
        const electionId = `elec_${this.nextElectionId++}`;
        
        const election = {
            id: electionId,
            title,
            description,
            positions, // 可选职位数
            candidates, // [{id, name, manifesto}]
            status: 'active',
            createdAt: Date.now(),
            expiresAt: Date.now() + duration,
            votes: new Map(), // candidateId -> [voterIds]
            totalVoters: 0
        };
        
        this.elections.set(electionId, election);
        
        this.emit('election_created', election);
        
        return election;
    }
    
    /**
     * 投票
     */
    castBallot(electionId, voterId, candidateIds) {
        const election = this.elections.get(electionId);
        if (!election) {
            return { success: false, error: '选举不存在' };
        }
        
        if (election.status !== 'active') {
            return { success: false, error: '选举已结束' };
        }
        
        if (Date.now() > election.expiresAt) {
            election.status = 'expired';
            return { success: false, error: '选举已过期' };
        }
        
        // 检查是否已投票
        for (const [candidateId, voters] of election.votes) {
            if (voters.has(voterId)) {
                return { success: false, error: '已投票' };
            }
        }
        
        // 验证候选人数
        if (candidateIds.length > election.positions) {
            return { success: false, error: `最多选择${election.positions}个候选人` };
        }
        
        // 记录投票
        const ballotId = `ballot_${this.nextBallotId++}`;
        const ballot = {
            id: ballotId,
            electionId,
            voterId,
            candidateIds,
            timestamp: Date.now()
        };
        
        this.ballots.set(ballotId, ballot);
        
        for (const candidateId of candidateIds) {
            if (!election.votes.has(candidateId)) {
                election.votes.set(candidateId, new Set());
            }
            election.votes.get(candidateId).add(voterId);
        }
        
        election.totalVoters++;
        
        this.emit('ballot_cast', ballot);
        
        return { success: true, ballotId };
    }
    
    /**
     * 结束选举
     */
    concludeElection(electionId) {
        const election = this.elections.get(electionId);
        if (!election || election.status !== 'active') {
            return { success: false, error: '选举无效' };
        }
        
        // 计算结果
        const results = [];
        for (const [candidateId, voters] of election.votes) {
            const candidate = election.candidates.find(c => c.id === candidateId);
            results.push({
                candidateId,
                candidateName: candidate ? candidate.name : 'Unknown',
                votes: voters.size
            });
        }
        
        // 按票数排序
        results.sort((a, b) => b.votes - a.votes);
        
        // 选出获胜者
        const winners = results.slice(0, election.positions);
        
        election.status = 'completed';
        election.results = results;
        election.winners = winners.map(w => w.candidateId);
        
        this.emit('election_completed', { electionId, results, winners });
        
        return { success: true, results, winners };
    }
    
    /**
     * 获取选举结果
     */
    getElectionResults(electionId) {
        const election = this.elections.get(electionId);
        if (!election || election.status !== 'completed') {
            return null;
        }
        
        return {
            electionId,
            title: election.title,
            results: election.results,
            winners: election.winners,
            totalVoters: election.totalVoters
        };
    }
    
    /**
     * 清除
     */
    clear() {
        this.elections.clear();
        this.ballots.clear();
    }
}

/**
 * 社区基金管理
 */
class CommunityFund extends EventEmitter {
    constructor(initialBalance = 0) {
        super();
        this.balance = initialBalance;
        this.transactions = [];
        this.budgets = new Map(); // budgetId -> budget
        this.nextBudgetId = 1;
    }
    
    /**
     * 存入资金
     */
    deposit(amount, source, description = '') {
        if (amount <= 0) {
            return { success: false, error: '金额必须大于 0' };
        }
        
        this.balance += amount;
        
        const transaction = {
            id: `tx_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            type: 'deposit',
            amount,
            balance: this.balance,
            source,
            description,
            timestamp: Date.now()
        };
        
        this.transactions.push(transaction);
        
        this.emit('fund_deposited', transaction);
        
        return { success: true, balance: this.balance };
    }
    
    /**
     * 提取资金
     */
    withdraw(amount, destination, description = '', approvalRequired = true) {
        if (amount <= 0) {
            return { success: false, error: '金额必须大于 0' };
        }
        
        if (amount > this.balance) {
            return { success: false, error: '余额不足' };
        }
        
        this.balance -= amount;
        
        const transaction = {
            id: `tx_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            type: 'withdraw',
            amount,
            balance: this.balance,
            destination,
            description,
            approvalRequired,
            timestamp: Date.now()
        };
        
        this.transactions.push(transaction);
        
        this.emit('fund_withdrawn', transaction);
        
        return { success: true, balance: this.balance };
    }
    
    /**
     * 创建预算
     */
    createBudget(name, amount, category, description = '') {
        const budgetId = `budget_${this.nextBudgetId++}`;
        
        const budget = {
            id: budgetId,
            name,
            amount,
            spent: 0,
            category,
            description,
            status: 'active',
            createdAt: Date.now()
        };
        
        this.budgets.set(budgetId, budget);
        
        this.emit('budget_created', budget);
        
        return budget;
    }
    
    /**
     * 预算支出
     */
    spendFromBudget(budgetId, amount, description = '') {
        const budget = this.budgets.get(budgetId);
        if (!budget) {
            return { success: false, error: '预算不存在' };
        }
        
        if (budget.status !== 'active') {
            return { success: false, error: '预算已失效' };
        }
        
        if (budget.spent + amount > budget.amount) {
            return { success: false, error: '超出预算' };
        }
        
        budget.spent += amount;
        
        // 从基金扣除
        this.withdraw(amount, budgetId, description, false);
        
        this.emit('budget_spent', { budgetId, amount });
        
        return { success: true, remaining: budget.amount - budget.spent };
    }
    
    /**
     * 获取交易历史
     */
    getTransactions(limit = 50) {
        return this.transactions.slice(-limit);
    }
    
    /**
     * 获取统计
     */
    getStats() {
        const totalDeposits = this.transactions
            .filter(t => t.type === 'deposit')
            .reduce((sum, t) => sum + t.amount, 0);
        
        const totalWithdraws = this.transactions
            .filter(t => t.type === 'withdraw')
            .reduce((sum, t) => sum + t.amount, 0);
        
        return {
            balance: this.balance,
            totalDeposits,
            totalWithdraws,
            transactionCount: this.transactions.length,
            activeBudgets: Array.from(this.budgets.values())
                .filter(b => b.status === 'active').length
        };
    }
    
    /**
     * 清除
     */
    clear() {
        this.transactions = [];
        this.budgets.clear();
    }
}

module.exports = {
    ProposalSystem,
    VotingSystem,
    CommunityFund
};

console.log('DAO 治理系统已加载');
