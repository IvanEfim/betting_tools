from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TradernetClient:
    """Safe stub client for Freedom24/Tradernet integration in v1."""

    base_url: str = "https://api.tradernet.example"

    def get_candles(self, symbol: str, timeframe: str = "1h", limit: int = 200) -> list[dict]:
        return [
            {"symbol": symbol, "timeframe": timeframe, "close": 10.0, "open": 9.8, "high": 10.2, "low": 9.7}
            for _ in range(max(limit, 1))
        ]

    def get_quote(self, symbol: str) -> dict:
        return {"symbol": symbol, "bid": 10.0, "ask": 10.05, "last": 10.02}

    def place_order(self, *args, **kwargs) -> dict:
        return {
            "accepted": False,
            "reason": "Auto trading is disabled in Trading Assistant v1",
        }
