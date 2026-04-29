from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    capital_usd: float = 150.0
    max_risk_per_trade_usd: float = 2.0
    max_daily_loss_usd: float = 4.0
    max_weekly_loss_usd: float = 8.0
    max_monthly_trades: int = 10
    min_reward_risk: float = 1.2
    sqlite_path: Path = Path("trades.db")

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            capital_usd=float(os.getenv("CAPITAL_USD", "150")),
            max_risk_per_trade_usd=float(os.getenv("MAX_RISK_PER_TRADE_USD", "2")),
            max_daily_loss_usd=float(os.getenv("MAX_DAILY_LOSS_USD", "4")),
            max_weekly_loss_usd=float(os.getenv("MAX_WEEKLY_LOSS_USD", "8")),
            max_monthly_trades=int(os.getenv("MAX_MONTHLY_TRADES", "10")),
            min_reward_risk=float(os.getenv("MIN_REWARD_RISK", "1.2")),
            sqlite_path=Path(os.getenv("SQLITE_PATH", "trades.db")),
        )
