from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.models import Side, TradeIdea


@dataclass(frozen=True)
class TrendPullbackStrategy:
    """Placeholder strategy: basic uptrend + pullback heuristic."""

    def generate_trade_idea(self, symbol: str, candles: Sequence[dict]) -> TradeIdea | None:
        if len(candles) < 3:
            return None

        c1, c2, c3 = candles[-3], candles[-2], candles[-1]
        if c1["close"] < c2["close"] and c3["close"] < c2["close"]:
            entry = float(c3["close"])
            return TradeIdea(
                symbol=symbol,
                side=Side.BUY,
                entry_price=entry,
                stop_loss=round(entry * 0.99, 2),
                take_profit=round(entry * 1.02, 2),
                quantity=1,
                note="trend_pullback_placeholder",
            )
        return None
