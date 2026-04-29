from app.config import Settings
from app.models import Side, TradeIdea
from app.risk.engine import PortfolioStats, RiskEngine


def _default_stats() -> PortfolioStats:
    return PortfolioStats(realized_pnl_day=0.0, realized_pnl_week=0.0, monthly_trade_count=0)


def test_valid_buy_trade_allowed() -> None:
    engine = RiskEngine(Settings())
    idea = TradeIdea(symbol="AAPL", side=Side.BUY, entry_price=10.0, stop_loss=9.0, take_profit=11.5, quantity=1)

    decision = engine.evaluate(idea, _default_stats())

    assert decision.allowed is True


def test_trade_without_valid_stop_rejected() -> None:
    engine = RiskEngine(Settings())
    idea = TradeIdea(symbol="AAPL", side=Side.BUY, entry_price=10.0, stop_loss=10.0, take_profit=12.0, quantity=1)

    decision = engine.evaluate(idea, _default_stats())

    assert decision.allowed is False
    assert "stop loss" in decision.reason.lower()


def test_bad_reward_risk_rejected() -> None:
    engine = RiskEngine(Settings())
    idea = TradeIdea(symbol="AAPL", side=Side.BUY, entry_price=10.0, stop_loss=9.0, take_profit=10.5, quantity=1)

    decision = engine.evaluate(idea, _default_stats())

    assert decision.allowed is False
    assert "reward/risk" in decision.reason.lower()


def test_position_too_expensive_rejected() -> None:
    engine = RiskEngine(Settings())
    idea = TradeIdea(symbol="AAPL", side=Side.BUY, entry_price=100.0, stop_loss=99.0, take_profit=102.0, quantity=2)

    decision = engine.evaluate(idea, _default_stats())

    assert decision.allowed is False
    assert "exceeds capital" in decision.reason.lower()
