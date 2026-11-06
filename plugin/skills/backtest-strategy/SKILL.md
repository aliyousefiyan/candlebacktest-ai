---
name: backtest-strategy
description: Help beginners turn a trading idea into explicit auditable JSON rules, and when Python and user-provided candles are available, run CandleBacktest AI's deterministic single-symbol, long-only educational replay. Do not recommend trades.
---

# CandleBacktest AI — educational strategy workflow

Only use user-provided OHLCV CSVs and explicit rule definitions. The skill contains a **bundled deterministic CLI**, not a remote trading or market-data service.

1. Read the user's trading-strategy idea. Use `docs/STRATEGY_PROMPT_FA.md` and `docs/SCHEMA.md` to ask for essential missing rules: symbol and timeframe, indicators and thresholds, candle-close signal timing, next-open entry, TP/SL, fees/slippage and position allocation. Never invent missing values or quietly choose an ICT/SMC interpretation.
2. Produce **declarative JSON**, never executable code or arbitrary Python/Pine. Supported indicators: SMA, EMA, RSI, ATR, MACD, Bollinger Bands and OHLCV fields; supported conditions include comparisons, crosses and AND. No OR/NOT, session logic, order blocks, shorting, futures, leverage or multi-timeframe alignment in this version.
3. Show all rule assumptions for the user's confirmation. Check that `allocation_pct` is a percentage of available cash, **not** stop-distance account risk. Validation of JSON syntax does not prove that the model understood the original strategy.
4. When Python 3.10+ and input files are available, run:
   - `python skills/backtest-strategy/run.py catalog`
   - `python skills/backtest-strategy/run.py run --strategy "/path/strategy.json" --candles "/path/candles.csv" --output "/path/report.json"`
   The runner imports the packaged `runtime/src` and needs no package installation, exchange login or network access. Use synthetic examples under `runtime/examples` to demonstrate.
5. Give actual trade-count, return, fee and end-of-bar equity/drawdown readings with caveats. Trades enter **next candle open**; a single long spot position is simulated; when both stop and target are touched in the same bar, the **stop wins**. Intrabar path and worst floating drawdown are not known from OHLC alone.
6. Compare TP/SL variations only by rerunning the strategy, reserving untouched out-of-sample periods. Never claim optimized historical returns imply future profitability. If file access or Python is unavailable, explain how to run locally; do not invent numbers.

No financial advice, trading orders, proprietary Pine scripts, credentials, personal financial accounts or false endorsement by OpenAI. This is experimental educational software, not a TradingView replacement. Read `docs/SCHEMA.md` for exact behavior.
