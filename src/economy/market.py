"""
交易市场

去中心化交易市场
"""

from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import uuid


# ==================== 订单类型 ====================

class OrderType(str, Enum):
    """订单类型"""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    """订单状态"""
    PENDING = "pending"
    PARTIAL_FILLED = "partial_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


# ==================== 订单模型 ====================

class Order(BaseModel):
    """订单"""
    id: str
    maker: str  # 挂单者
    taker: Optional[str] = None  # 吃单者
    order_type: OrderType
    asset_type: str  # 资产类型 (token, nft, land, etc)
    asset_id: Optional[str] = None  # 资产 ID
    amount: int  # 数量
    price: int  # 单价 (Wei)
    filled_amount: int = 0  # 已成交数量
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = None
    expires_at: Optional[datetime] = None
    signature: Optional[str] = None  # 签名
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow()
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())
        super().__init__(**data)
    
    def get_remaining_amount(self) -> int:
        """获取剩余数量"""
        return self.amount - self.filled_amount
    
    def is_filled(self) -> bool:
        """是否已完全成交"""
        return self.filled_amount >= self.amount
    
    def is_expired(self) -> bool:
        """是否已过期"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    def fill(self, amount: int, taker: str):
        """
        成交订单
        
        Args:
            amount: 成交数量
            taker: 吃单者地址
        """
        self.filled_amount += amount
        self.taker = taker
        
        if self.is_filled():
            self.status = OrderStatus.FILLED
        elif self.filled_amount > 0:
            self.status = OrderStatus.PARTIAL_FILLED


# ==================== 订单簿 ====================

class OrderBook:
    """
    订单簿
    
    管理买卖订单
    """
    
    def __init__(self, asset_type: str, asset_id: str = None):
        self.asset_type = asset_type
        self.asset_id = asset_id
        self.buy_orders: List[Order] = []
        self.sell_orders: List[Order] = []
    
    def add_order(self, order: Order):
        """添加订单"""
        if order.order_type == OrderType.BUY:
            self.buy_orders.append(order)
            # 按价格降序排序 (高价优先)
            self.buy_orders.sort(key=lambda o: o.price, reverse=True)
        else:
            self.sell_orders.append(order)
            # 按价格升序排序 (低价优先)
            self.sell_orders.sort(key=lambda o: o.price)
    
    def remove_order(self, order_id: str):
        """移除订单"""
        self.buy_orders = [o for o in self.buy_orders if o.id != order_id]
        self.sell_orders = [o for o in self.sell_orders if o.id != order_id]
    
    def get_best_bid(self) -> Optional[Order]:
        """获取最高买价"""
        return self.buy_orders[0] if self.buy_orders else None
    
    def get_best_ask(self) -> Optional[Order]:
        """获取最低卖价"""
        return self.sell_orders[0] if self.sell_orders else None
    
    def get_spread(self) -> Optional[int]:
        """获取买卖价差"""
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        
        if best_bid and best_ask:
            return best_ask.price - best_bid.price
        return None
    
    def get_orders(self, limit: int = 100) -> Dict[str, List[Order]]:
        """获取订单簿"""
        return {
            "bids": self.buy_orders[:limit],
            "asks": self.sell_orders[:limit]
        }


# ==================== 撮合引擎 ====================

class MatchResult(BaseModel):
    """撮合结果"""
    buy_order_id: str
    sell_order_id: str
    price: int
    amount: int
    timestamp: datetime = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)


class MatchingEngine:
    """
    撮合引擎
    
    匹配买卖订单
    """
    
    def __init__(self):
        self.order_books: Dict[str, OrderBook] = {}
        self.trades: List[MatchResult] = []
    
    def get_or_create_order_book(self, asset_type: str, asset_id: str = None) -> OrderBook:
        """获取或创建订单簿"""
        key = f"{asset_type}:{asset_id}" if asset_id else asset_type
        
        if key not in self.order_books:
            self.order_books[key] = OrderBook(asset_type, asset_id)
        
        return self.order_books[key]
    
    def place_order(self, order: Order) -> List[MatchResult]:
        """
        挂单并撮合
        
        Args:
            order: 订单
        
        Returns:
            撮合结果列表
        """
        order_book = self.get_or_create_order_book(order.asset_type, order.asset_id)
        
        matches = []
        
        # 尝试撮合
        if order.order_type == OrderType.BUY:
            matches = self._match_buy_order(order, order_book)
        else:
            matches = self._match_sell_order(order, order_book)
        
        # 剩余数量加入订单簿
        if order.get_remaining_amount() > 0 and order.status != OrderStatus.CANCELLED:
            order_book.add_order(order)
        
        return matches
    
    def _match_buy_order(self, buy_order: Order, order_book: OrderBook) -> List[MatchResult]:
        """匹配买单"""
        matches = []
        
        for sell_order in order_book.sell_orders[:]:
            if buy_order.get_remaining_amount() <= 0:
                break
            
            # 价格不匹配
            if sell_order.price > buy_order.price:
                break
            
            # 计算成交量
            buy_remaining = buy_order.get_remaining_amount()
            sell_remaining = sell_order.get_remaining_amount()
            fill_amount = min(buy_remaining, sell_remaining)
            
            # 成交
            buy_order.fill(fill_amount, sell_order.maker)
            sell_order.fill(fill_amount, buy_order.maker)
            
            # 记录成交
            match = MatchResult(
                buy_order_id=buy_order.id,
                sell_order_id=sell_order.id,
                price=sell_order.price,
                amount=fill_amount
            )
            matches.append(match)
            self.trades.append(match)
            
            # 移除已完成的卖单
            if sell_order.is_filled():
                order_book.remove_order(sell_order.id)
        
        return matches
    
    def _match_sell_order(self, sell_order: Order, order_book: OrderBook) -> List[MatchResult]:
        """匹配卖单"""
        matches = []
        
        for buy_order in order_book.buy_orders[:]:
            if sell_order.get_remaining_amount() <= 0:
                break
            
            # 价格不匹配
            if buy_order.price < sell_order.price:
                break
            
            # 计算成交量
            buy_remaining = buy_order.get_remaining_amount()
            sell_remaining = sell_order.get_remaining_amount()
            fill_amount = min(buy_remaining, sell_remaining)
            
            # 成交
            buy_order.fill(fill_amount, sell_order.maker)
            sell_order.fill(fill_amount, buy_order.maker)
            
            # 记录成交
            match = MatchResult(
                buy_order_id=buy_order.id,
                sell_order_id=sell_order.id,
                price=buy_order.price,
                amount=fill_amount
            )
            matches.append(match)
            self.trades.append(match)
            
            # 移除已完成的买单
            if buy_order.is_filled():
                order_book.remove_order(buy_order.id)
        
        return matches
    
    def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        for order_book in self.order_books.values():
            for order in order_book.buy_orders + order_book.sell_orders:
                if order.id == order_id:
                    order.status = OrderStatus.CANCELLED
                    order_book.remove_order(order_id)
                    return True
        return False
    
    def get_trades(self, asset_type: str, asset_id: str = None, limit: int = 100) -> List[MatchResult]:
        """获取成交记录"""
        return self.trades[-limit:]
    
    def get_market_stats(self, asset_type: str, asset_id: str = None) -> Dict[str, Any]:
        """获取市场统计"""
        order_book = self.get_or_create_order_book(asset_type, asset_id)
        
        best_bid = order_book.get_best_bid()
        best_ask = order_book.get_best_ask()
        
        return {
            "best_bid": best_bid.price if best_bid else 0,
            "best_ask": best_ask.price if best_ask else 0,
            "spread": order_book.get_spread() or 0,
            "total_buy_orders": len(order_book.buy_orders),
            "total_sell_orders": len(order_book.sell_orders),
            "total_trades": len(self.trades)
        }


# ==================== 市场管理器 ====================

class MarketManager:
    """
    市场管理器
    
    统一管理所有市场
    """
    
    def __init__(self):
        self.matching_engine = MatchingEngine()
        self.orders: Dict[str, Order] = {}
    
    def create_order(
        self,
        maker: str,
        order_type: OrderType,
        asset_type: str,
        amount: int,
        price: int,
        asset_id: str = None,
        expires_in_hours: int = 24
    ) -> Order:
        """
        创建订单
        
        Args:
            maker: 挂单者地址
            order_type: 订单类型
            asset_type: 资产类型
            amount: 数量
            price: 单价
            asset_id: 资产 ID
            expires_in_hours: 过期时间 (小时)
        
        Returns:
            Order
        """
        expires_at = datetime.utcnow()
        if expires_in_hours > 0:
            from datetime import timedelta
            expires_at += timedelta(hours=expires_in_hours)
        
        order = Order(
            maker=maker,
            order_type=order_type,
            asset_type=asset_type,
            asset_id=asset_id,
            amount=amount,
            price=price,
            expires_at=expires_at
        )
        
        self.orders[order.id] = order
        return order
    
    def place_order(self, order: Order) -> List[MatchResult]:
        """挂单"""
        return self.matching_engine.place_order(order)
    
    def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        if order_id in self.orders:
            self.orders[order_id].status = OrderStatus.CANCELLED
        return self.matching_engine.cancel_order(order_id)
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """获取订单"""
        return self.orders.get(order_id)
    
    def get_orders_by_maker(self, maker: str) -> List[Order]:
        """获取用户的订单"""
        return [o for o in self.orders.values() if o.maker == maker]
    
    def get_market_stats(self, asset_type: str, asset_id: str = None) -> Dict[str, Any]:
        """获取市场统计"""
        return self.matching_engine.get_market_stats(asset_type, asset_id)
    
    def get_recent_trades(self, asset_type: str, asset_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """获取最近成交"""
        trades = self.matching_engine.get_trades(asset_type, asset_id, limit)
        return [
            {
                "price": t.price,
                "amount": t.amount,
                "timestamp": t.timestamp.isoformat(),
                "buy_order_id": t.buy_order_id,
                "sell_order_id": t.sell_order_id
            }
            for t in trades
        ]


# 使用示例
if __name__ == "__main__":
    # 创建市场管理器
    manager = MarketManager()
    
    print("创建订单...")
    
    # 创建卖单
    sell_order = manager.create_order(
        maker="0x1234567890abcdef",
        order_type=OrderType.SELL,
        asset_type="nft",
        asset_id="land_001",
        amount=1,
        price=1000 * (10 ** 18),  # 1000 SIL
        expires_in_hours=24
    )
    print(f"卖单：ID={sell_order.id}, 价格={sell_order.price / 10**18} SIL")
    
    # 创建买单
    buy_order = manager.create_order(
        maker="0xabcdef1234567890",
        order_type=OrderType.BUY,
        asset_type="nft",
        asset_id="land_001",
        amount=1,
        price=1000 * (10 ** 18),  # 1000 SIL
        expires_in_hours=24
    )
    print(f"买单：ID={buy_order.id}, 价格={buy_order.price / 10**18} SIL")
    
    # 挂单并撮合
    print("\n挂单撮合...")
    manager.place_order(sell_order)
    matches = manager.place_order(buy_order)
    
    print(f"成交笔数：{len(matches)}")
    for match in matches:
        print(f"  成交：{match.amount} @ {match.price / 10**18} SIL")
    
    # 获取市场统计
    print("\n市场统计:")
    stats = manager.get_market_stats("nft", "land_001")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 获取订单状态
    print(f"\n卖单状态：{sell_order.status}")
    print(f"买单状态：{buy_order.status}")
