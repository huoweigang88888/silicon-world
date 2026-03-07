"""
代币系统

$SILICON 代币经济管理
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
import uuid


# ==================== 代币模型 ====================

class TokenInfo(BaseModel):
    """代币信息"""
    name: str = "SILICON"
    symbol: str = "SIL"
    decimals: int = 18
    total_supply: int = 1000000000  # 10 亿枚
    
    def get_total_supply_wei(self) -> int:
        """获取以 Wei 为单位的总供应量"""
        return self.total_supply * (10 ** self.decimals)


class TokenDistribution(BaseModel):
    """代币分配"""
    # 初始流通 20%
    initial_circulation: float = 0.20
    
    # 挖矿奖励 40% (10 年释放)
    mining_rewards: float = 0.40
    mining_release_years: int = 10
    
    # 团队储备 20% (4 年线性释放)
    team_reserve: float = 0.20
    team_release_years: int = 4
    
    # 生态基金 20%
    ecosystem_fund: float = 0.20


# ==================== 钱包 ====================

class Wallet(BaseModel):
    """钱包"""
    id: str
    address: str
    owner_id: str  # 所有者 ID (DID)
    balance: int = 0  # 代币余额 (Wei)
    locked_balance: int = 0  # 锁定余额
    created_at: datetime = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow()
        super().__init__(**data)
    
    def get_unlocked_balance(self) -> int:
        """获取可用余额"""
        return self.balance - self.locked_balance
    
    def to_eth(self) -> str:
        """转换为 ETH 格式地址"""
        if self.address.startswith("0x"):
            return self.address
        return f"0x{self.address}"


# ==================== 锁定计划 ====================

class VestingSchedule(BaseModel):
    """解锁计划"""
    beneficiary: str  # 受益人
    total_amount: int  # 总数量
    released_amount: int = 0  # 已释放数量
    start_time: datetime
    end_time: datetime
    cliff_duration: int = 0  # 锁定期 (秒)
    
    def get_releasable_amount(self, current_time: datetime) -> int:
        """
        计算可释放数量
        
        Args:
            current_time: 当前时间
        
        Returns:
            可释放数量
        """
        if current_time < self.start_time:
            return 0
        
        if current_time < self.start_time + timedelta(seconds=self.cliff_duration):
            return 0
        
        total_duration = (self.end_time - self.start_time).total_seconds()
        elapsed_time = (current_time - self.start_time).total_seconds()
        
        if elapsed_time >= total_duration:
            return self.total_amount - self.released_amount
        
        vested_amount = int(self.total_amount * elapsed_time / total_duration)
        return vested_amount - self.released_amount
    
    def release(self, amount: int):
        """
        释放代币
        
        Args:
            amount: 释放数量
        """
        self.released_amount += amount


# ==================== 转账记录 ====================

class TransferRecord(BaseModel):
    """转账记录"""
    id: str
    from_address: str
    to_address: str
    amount: int
    timestamp: datetime = None
    status: str = "pending"  # pending, confirmed, failed
    tx_hash: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow()
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        super().__init__(**data)


# ==================== 代币管理器 ====================

class TokenManager:
    """
    代币管理器
    
    管理代币的发行、转账、锁定等
    """
    
    def __init__(self):
        self.token_info = TokenInfo()
        self.distribution = TokenDistribution()
        self.wallets: Dict[str, Wallet] = {}
        self.transfers: List[TransferRecord] = []
        self.vesting_schedules: List[VestingSchedule] = []
    
    def create_wallet(self, owner_id: str, address: str) -> Wallet:
        """
        创建钱包
        
        Args:
            owner_id: 所有者 ID
            address: 钱包地址
        
        Returns:
            Wallet
        """
        wallet = Wallet(
            id=str(uuid.uuid4()),
            address=address,
            owner_id=owner_id
        )
        
        self.wallets[address] = wallet
        return wallet
    
    def get_wallet(self, address: str) -> Optional[Wallet]:
        """获取钱包"""
        return self.wallets.get(address)
    
    def transfer(
        self,
        from_address: str,
        to_address: str,
        amount: int
    ) -> TransferRecord:
        """
        转账
        
        Args:
            from_address: 发送地址
            to_address: 接收地址
            amount: 数量 (Wei)
        
        Returns:
            TransferRecord
        """
        from_wallet = self.get_wallet(from_address)
        to_wallet = self.get_wallet(to_address)
        
        if not from_wallet:
            raise ValueError("发送钱包不存在")
        
        if not to_wallet:
            raise ValueError("接收钱包不存在")
        
        # 检查余额
        if from_wallet.get_unlocked_balance() < amount:
            raise ValueError("余额不足")
        
        # 执行转账
        from_wallet.balance -= amount
        to_wallet.balance += amount
        
        # 创建记录
        record = TransferRecord(
            from_address=from_address,
            to_address=to_address,
            amount=amount,
            status="confirmed"
        )
        
        self.transfers.append(record)
        return record
    
    def lock_tokens(
        self,
        address: str,
        amount: int,
        unlock_time: datetime
    ) -> VestingSchedule:
        """
        锁定代币
        
        Args:
            address: 钱包地址
            amount: 锁定数量
            unlock_time: 解锁时间
        
        Returns:
            VestingSchedule
        """
        wallet = self.get_wallet(address)
        if not wallet:
            raise ValueError("钱包不存在")
        
        if wallet.balance < amount:
            raise ValueError("余额不足")
        
        # 更新锁定余额
        wallet.locked_balance += amount
        
        # 创建解锁计划
        schedule = VestingSchedule(
            beneficiary=address,
            total_amount=amount,
            start_time=datetime.utcnow(),
            end_time=unlock_time
        )
        
        self.vesting_schedules.append(schedule)
        return schedule
    
    def unlock_tokens(self, address: str) -> int:
        """
        解锁代币
        
        Args:
            address: 钱包地址
        
        Returns:
            解锁数量
        """
        wallet = self.get_wallet(address)
        if not wallet:
            return 0
        
        total_unlocked = 0
        current_time = datetime.utcnow()
        
        for schedule in self.vesting_schedules:
            if schedule.beneficiary == address:
                releasable = schedule.get_releasable_amount(current_time)
                if releasable > 0:
                    schedule.release(releasable)
                    total_unlocked += releasable
        
        if total_unlocked > 0:
            wallet.locked_balance -= total_unlocked
        
        return total_unlocked
    
    def get_distribution_info(self) -> Dict[str, Any]:
        """获取代币分配信息"""
        total = self.token_info.total_supply
        
        return {
            "total_supply": total,
            "initial_circulation": {
                "amount": int(total * self.distribution.initial_circulation),
                "percentage": self.distribution.initial_circulation * 100
            },
            "mining_rewards": {
                "amount": int(total * self.distribution.mining_rewards),
                "percentage": self.distribution.mining_rewards * 100,
                "release_years": self.distribution.mining_release_years
            },
            "team_reserve": {
                "amount": int(total * self.distribution.team_reserve),
                "percentage": self.distribution.team_reserve * 100,
                "release_years": self.distribution.team_release_years
            },
            "ecosystem_fund": {
                "amount": int(total * self.distribution.ecosystem_fund),
                "percentage": self.distribution.ecosystem_fund * 100
            }
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取代币统计"""
        total_balance = sum(w.balance for w in self.wallets.values())
        total_locked = sum(w.locked_balance for w in self.wallets.values())
        
        return {
            "total_wallets": len(self.wallets),
            "total_balance": total_balance,
            "total_locked": total_locked,
            "total_transfers": len(self.transfers),
            "total_vesting": len(self.vesting_schedules)
        }


# 使用示例
if __name__ == "__main__":
    from datetime import timedelta
    
    # 创建代币管理器
    manager = TokenManager()
    
    # 获取代币信息
    print(f"代币名称：{manager.token_info.name}")
    print(f"代币符号：{manager.token_info.symbol}")
    print(f"总供应量：{manager.token_info.total_supply:,} {manager.token_info.symbol}")
    
    # 获取分配信息
    print("\n代币分配:")
    dist = manager.get_distribution_info()
    for key, value in dist.items():
        if isinstance(value, dict):
            print(f"  {key}: {value['amount']:,} ({value['percentage']}%)")
        else:
            print(f"  {key}: {value}")
    
    # 创建钱包
    print("\n创建钱包...")
    wallet1 = manager.create_wallet(
        owner_id="did:silicon:agent:123",
        address="0x1234567890abcdef1234567890abcdef12345678"
    )
    wallet2 = manager.create_wallet(
        owner_id="did:silicon:user:456",
        address="0xabcdef1234567890abcdef1234567890abcdef12"
    )
    
    # 初始分配
    wallet1.balance = 1000000 * (10 ** 18)  # 100 万枚
    wallet2.balance = 500000 * (10 ** 18)   # 50 万枚
    
    # 转账
    print("\n执行转账...")
    amount = 1000 * (10 ** 18)  # 1000 枚
    record = manager.transfer(
        from_address=wallet1.address,
        to_address=wallet2.address,
        amount=amount
    )
    print(f"转账：{amount / 10**18:,.0f} {manager.token_info.symbol}")
    print(f"状态：{record.status}")
    
    # 锁定代币
    print("\n锁定代币...")
    unlock_time = datetime.utcnow() + timedelta(days=365)
    schedule = manager.lock_tokens(
        address=wallet1.address,
        amount=500000 * (10 ** 18),
        unlock_time=unlock_time
    )
    print(f"锁定：500,000 {manager.token_info.symbol}")
    print(f"解锁时间：{unlock_time}")
    
    # 获取统计
    print("\n代币统计:")
    stats = manager.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
