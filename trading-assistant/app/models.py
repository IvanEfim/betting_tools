from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"


class TradeStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


@dataclass(frozen=True)
class TradeIdea:
    symbol: str
    side: Side
    entry_price: float
    stop_loss: float
    take_profit: float
    quantity: int
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    note: str = ""

    @property
    def position_cost(self) -> float:
        return self.entry_price * self.quantity


@dataclass(frozen=True)
class RiskDecision:
    allowed: bool
    reason: str
    risk_amount_usd: float
    reward_risk_ratio: float


@dataclass
class TradeRecord:
    id: int
    symbol: str
    side: Side
    entry_price: float
    stop_loss: float
    take_profit: float
    quantity: int
    status: TradeStatus
    opened_at: datetime
    closed_at: Optional[datetime]
    close_price: Optional[float]
    realized_pnl: Optional[float]
    note: str = ""
