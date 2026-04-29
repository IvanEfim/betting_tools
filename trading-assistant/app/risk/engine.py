from __future__ import annotations

from dataclasses import dataclass

from app.config import Settings
from app.models import RiskDecision, Side, TradeIdea


@dataclass(frozen=True)
class PortfolioStats:
    realized_pnl_day: float
    realized_pnl_week: float
    monthly_trade_count: int


class RiskEngine:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def evaluate(self, idea: TradeIdea, stats: PortfolioStats) -> RiskDecision:
        if idea.quantity <= 0:
            return RiskDecision(False, "Quantity must be positive", 0.0, 0.0)

        if idea.stop_loss <= 0 or idea.entry_price <= 0 or idea.take_profit <= 0:
            return RiskDecision(False, "Prices must be positive", 0.0, 0.0)

        if idea.position_cost > self.settings.capital_usd:
            return RiskDecision(
                False,
                f"Position cost ${idea.position_cost:.2f} exceeds capital ${self.settings.capital_usd:.2f}",
                0.0,
                0.0,
            )

        if stats.realized_pnl_day <= -self.settings.max_daily_loss_usd:
            return RiskDecision(False, "Daily loss limit reached", 0.0, 0.0)

        if stats.realized_pnl_week <= -self.settings.max_weekly_loss_usd:
            return RiskDecision(False, "Weekly loss limit reached", 0.0, 0.0)

        if stats.monthly_trade_count >= self.settings.max_monthly_trades:
            return RiskDecision(False, "Monthly trade limit reached", 0.0, 0.0)

        risk_per_share = self._risk_per_share(idea)
        if risk_per_share <= 0:
            return RiskDecision(False, "Trade without valid stop loss is forbidden", 0.0, 0.0)

        reward_per_share = self._reward_per_share(idea)
        rr = reward_per_share / risk_per_share

        risk_amount = risk_per_share * idea.quantity
        if risk_amount > self.settings.max_risk_per_trade_usd:
            return RiskDecision(
                False,
                f"Risk ${risk_amount:.2f} exceeds per-trade max ${self.settings.max_risk_per_trade_usd:.2f}",
                risk_amount,
                rr,
            )

        if rr < self.settings.min_reward_risk:
            return RiskDecision(
                False,
                f"Reward/risk ratio {rr:.2f} is below minimum {self.settings.min_reward_risk:.2f}",
                risk_amount,
                rr,
            )

        return RiskDecision(True, "Trade approved", risk_amount, rr)

    @staticmethod
    def _risk_per_share(idea: TradeIdea) -> float:
        if idea.side == Side.BUY:
            return idea.entry_price - idea.stop_loss
        return idea.stop_loss - idea.entry_price

    @staticmethod
    def _reward_per_share(idea: TradeIdea) -> float:
        if idea.side == Side.BUY:
            return idea.take_profit - idea.entry_price
        return idea.entry_price - idea.take_profit
