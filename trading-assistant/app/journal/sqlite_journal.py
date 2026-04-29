from __future__ import annotations

import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

from app.models import Side, TradeIdea, TradeRecord, TradeStatus


class SQLiteJournal:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    stop_loss REAL NOT NULL,
                    take_profit REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    opened_at TEXT NOT NULL,
                    closed_at TEXT,
                    close_price REAL,
                    realized_pnl REAL,
                    note TEXT NOT NULL DEFAULT ''
                )
                """
            )

    def add_trade(self, idea: TradeIdea) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO trades (
                    symbol, side, entry_price, stop_loss, take_profit, quantity,
                    status, opened_at, note
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    idea.symbol,
                    idea.side.value,
                    idea.entry_price,
                    idea.stop_loss,
                    idea.take_profit,
                    idea.quantity,
                    TradeStatus.OPEN.value,
                    idea.created_at.isoformat(),
                    idea.note,
                ),
            )
            return int(cur.lastrowid)

    def close_trade(self, trade_id: int, close_price: float, closed_at: Optional[datetime] = None) -> None:
        trade = self.get_trade(trade_id)
        if trade is None:
            raise ValueError(f"Trade {trade_id} not found")
        if trade.status == TradeStatus.CLOSED:
            raise ValueError(f"Trade {trade_id} is already closed")

        close_dt = closed_at or datetime.now(timezone.utc)
        direction = 1 if trade.side == Side.BUY else -1
        pnl = (close_price - trade.entry_price) * trade.quantity * direction

        with self._connect() as conn:
            conn.execute(
                """
                UPDATE trades
                SET status = ?, closed_at = ?, close_price = ?, realized_pnl = ?
                WHERE id = ?
                """,
                (TradeStatus.CLOSED.value, close_dt.isoformat(), close_price, pnl, trade_id),
            )

    def get_trade(self, trade_id: int) -> Optional[TradeRecord]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM trades WHERE id = ?", (trade_id,)).fetchone()
        if row is None:
            return None
        return self._row_to_trade(row)

    def list_trades(self) -> list[TradeRecord]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM trades ORDER BY opened_at DESC").fetchall()
        return [self._row_to_trade(r) for r in rows]

    def realized_pnl_for_day(self, day: date) -> float:
        day_start = datetime.combine(day, datetime.min.time(), tzinfo=timezone.utc).isoformat()
        day_end = datetime.combine(day, datetime.max.time(), tzinfo=timezone.utc).isoformat()
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT COALESCE(SUM(realized_pnl), 0.0) AS pnl
                FROM trades
                WHERE status = ? AND closed_at BETWEEN ? AND ?
                """,
                (TradeStatus.CLOSED.value, day_start, day_end),
            ).fetchone()
        return float(row["pnl"])

    def monthly_trade_count(self, year: int, month: int) -> int:
        prefix = f"{year:04d}-{month:02d}-%"
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS cnt FROM trades WHERE opened_at LIKE ?",
                (prefix,),
            ).fetchone()
        return int(row["cnt"])

    @staticmethod
    def _row_to_trade(row: sqlite3.Row) -> TradeRecord:
        return TradeRecord(
            id=int(row["id"]),
            symbol=str(row["symbol"]),
            side=Side(row["side"]),
            entry_price=float(row["entry_price"]),
            stop_loss=float(row["stop_loss"]),
            take_profit=float(row["take_profit"]),
            quantity=int(row["quantity"]),
            status=TradeStatus(row["status"]),
            opened_at=datetime.fromisoformat(row["opened_at"]),
            closed_at=datetime.fromisoformat(row["closed_at"]) if row["closed_at"] else None,
            close_price=float(row["close_price"]) if row["close_price"] is not None else None,
            realized_pnl=float(row["realized_pnl"]) if row["realized_pnl"] is not None else None,
            note=str(row["note"]),
        )
