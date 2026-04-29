from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.config import Settings
from app.journal.sqlite_journal import SQLiteJournal
from app.models import Side, TradeIdea
from app.notifications.console import notify
from app.risk.engine import PortfolioStats, RiskEngine


def run_demo() -> None:
    settings = Settings.from_env()
    journal = SQLiteJournal(settings.sqlite_path)
    engine = RiskEngine(settings)

    now = datetime.now(timezone.utc)
    daily_pnl = journal.realized_pnl_for_day(now.date())

    week_start = now.date() - timedelta(days=now.weekday())
    weekly_pnl = sum(journal.realized_pnl_for_day(week_start + timedelta(days=i)) for i in range(7))

    monthly_count = journal.monthly_trade_count(now.year, now.month)

    stats = PortfolioStats(
        realized_pnl_day=daily_pnl,
        realized_pnl_week=weekly_pnl,
        monthly_trade_count=monthly_count,
    )

    idea = TradeIdea(
        symbol="AAPL",
        side=Side.BUY,
        entry_price=10.0,
        stop_loss=9.0,
        take_profit=11.5,
        quantity=1,
        note="demo trade idea",
    )

    decision = engine.evaluate(idea, stats)

    if decision.allowed:
        trade_id = journal.add_trade(idea)
        notify(
            f"APPROVED: trade_id={trade_id}, symbol={idea.symbol}, risk=${decision.risk_amount_usd:.2f}, RR={decision.reward_risk_ratio:.2f}"
        )
    else:
        notify(f"REJECTED: {decision.reason}")


if __name__ == "__main__":
    run_demo()
