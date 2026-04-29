from datetime import datetime, timezone

from app.journal.sqlite_journal import SQLiteJournal
from app.models import Side, TradeIdea, TradeStatus


def test_add_trade_sqlite(tmp_path) -> None:
    journal = SQLiteJournal(tmp_path / "test.db")
    idea = TradeIdea(symbol="AAPL", side=Side.BUY, entry_price=10.0, stop_loss=9.0, take_profit=12.0, quantity=2)

    trade_id = journal.add_trade(idea)
    trade = journal.get_trade(trade_id)

    assert trade is not None
    assert trade.symbol == "AAPL"
    assert trade.status == TradeStatus.OPEN


def test_close_trade_and_realized_pnl(tmp_path) -> None:
    journal = SQLiteJournal(tmp_path / "test.db")
    idea = TradeIdea(symbol="AAPL", side=Side.BUY, entry_price=10.0, stop_loss=9.0, take_profit=12.0, quantity=2)
    trade_id = journal.add_trade(idea)

    closed_at = datetime(2026, 4, 28, 12, 0, tzinfo=timezone.utc)
    journal.close_trade(trade_id, close_price=11.0, closed_at=closed_at)

    trade = journal.get_trade(trade_id)
    assert trade is not None
    assert trade.status == TradeStatus.CLOSED
    assert trade.realized_pnl == 2.0

    pnl = journal.realized_pnl_for_day(closed_at.date())
    assert pnl == 2.0
