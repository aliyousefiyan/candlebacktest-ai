# Reproducibility, testing and security boundaries

CandleBacktest AI v0.1.1 is an **experimental, long-only, single-symbol, OHLCV CSV backtester**. It is a teaching and prototyping tool, not an investment adviser or a general TradingView engine. All supplied example candles are synthetic.

## Reproduce the current checks

```bash
git clone https://github.com/aliyousefiyan/candlebacktest-ai.git
cd candlebacktest-ai
python -m pip install -e .
python -m unittest discover -s tests -v
candlebacktest catalog
candlebacktest run --strategy examples/ema_cross.json --candles examples/candles_synthetic_4h.csv --output report.json
```

The [GitHub Actions checks](https://github.com/aliyousefiyan/candlebacktest-ai/actions) run unit and smoke tests on Python 3.11 and 3.13. Green CI proves **those specific tests passed**, not that backtests are independently certified or realistic for live trades.

## Verify an individual result

1. Save the exact strategy JSON, candle source, SHA-256/fingerprints reported by the engine, commit SHA and Python version.
2. Check timestamps, completeness, market/timeframe assumptions, and absence of look-ahead.
3. Inspect indicator warmup and signals on several bars by hand or against an independently implemented reference; do not assume TradingView/Pine parity.
4. Inspect the generated trades one by one for next-bar fills, fees, adverse slippage and TP/SL ties (the engine chooses the stop when both occur in one bar).
5. Re-run the same inputs twice and compare trade ledgers and reported metrics.
6. For parameter searches, hold out dates and symbols for untouched out-of-sample testing. A better historical TP/SL setting is **not proof** of future profitability.

## AI and strategy import

The app accepts a constrained JSON strategy, not arbitrary generated code. The external AI prompt is [here](EXTERNAL_AI_PROMPT_FA.md). Its clarification process reduces ambiguity, but an AI can still misunderstand the strategy, even when the JSON passes validation. The human user must inspect and approve each trading rule.

## Current boundaries

- Long-only spot, one symbol/timeframe, one position at a time; no market sessions, shorts, margin, multi-timeframe portfolio, funding, liquidation or intrabar path reconstruction.
- End-of-bar drawdown is not a verified worst intrabar floating drawdown.
- Optional [CandleAudit](https://github.com/aliyousefiyan/candleaudit) integration currently checks candle integrity only; trade/feature audits are **not** automatically performed.
- The browser app binds to local loopback; **do not expose it on a public network**. See [SECURITY.md](../SECURITY.md).

## Report a reproducible defect

Use the [issue templates](../.github/ISSUE_TEMPLATE) with a minimal **synthetic** candle/strategy example, expected and actual outcomes, software commit and the relevant ledger rows. Never upload exchange secrets, real account data or proprietary scripts. Independent review and evidence of real use are welcome; fabricated community metrics are not.
