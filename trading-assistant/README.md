# Trading Assistant v1 (MVP)

Engineering MVP for disciplined semi-automatic trading workflow with **$150 capital baseline**, focused on **risk checks** and **trade journaling**.

## Product Overview

Trading Assistant v1 supports two operational modes:
- **signal mode**: generate trade ideas and validate against risk rules;
- **paper mode**: simulate/record trades without broker execution.

Core objective: reject non-compliant trade ideas before they reach execution and keep an auditable SQLite journal.

## Why `dataclasses` (instead of Pydantic)

For v1 we use Python standard library `dataclasses` because:
- zero external runtime dependencies;
- predictable, lightweight domain models (`TradeIdea`, `RiskDecision`, `TradeRecord`);
- enough for current validation rules performed in `RiskEngine`.

Pydantic can be added later when external API payload validation becomes a priority.

## v1 Constraints

- `capital_usd = 150`
- `max_risk_per_trade_usd = 2`
- `max_daily_loss_usd = 4`
- `max_weekly_loss_usd = 8`
- `max_monthly_trades = 10`
- `min_reward_risk = 1.2`
- Trade without valid stop-loss is forbidden.
- New trades are blocked if daily loss limit is reached.
- New trades are blocked if monthly trade limit is reached.
- **Auto trading is disabled in v1**.
- Broker execution layer is a safe stub.

## Installation

```bash
cd trading-assistant
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
```

## Run tests

```bash
cd trading-assistant
pytest
```

## Run demo flow

```bash
cd trading-assistant
python -m app.main
```

Demo flow in `app/main.py`:
1. Build `TradeIdea`.
2. Read daily/monthly stats from SQLite journal.
3. Evaluate through `RiskEngine`.
4. Persist approved trade to journal.
5. Print user-friendly decision to console.

## Why auto trading is off in v1

Safety-first scope: this MVP is for risk governance and operator discipline only. Automated broker execution is intentionally disabled until:
- signal quality metrics are statistically validated;
- additional protections (idempotency, circuit breakers, monitoring, failover) are in place;
- compliance and operational controls are reviewed.

`app/broker/tradernet_client.py::place_order()` always returns denial in v1.

## Roadmap

1. Add richer strategy modules and backtesting.
2. Add Telegram/email notifications.
3. Add broker auth and read-only portfolio sync.
4. Introduce execution safeguards for staged live rollout.
5. Add dashboards for PnL, risk usage, and discipline metrics.

## Disclaimer

This project is an engineering tool for workflow automation and risk checks. It does **not** provide financial advice.
