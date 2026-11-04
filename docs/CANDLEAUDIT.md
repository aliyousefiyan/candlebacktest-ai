# Integration with CandleAudit

[CandleAudit](https://github.com/aliyousefiyan/candleaudit) is an independent open-source audit tool. CandleBacktest AI does not use private project files, live orders or exchange secrets.

## Working now: candle quality gate via CLI

Install CandleAudit separately, then:

```bash
candlebacktest run --strategy examples/ema_cross.json --candles examples/candles_synthetic_4h.csv --audit --output report.json
```

The `--audit` adapter runs `candleaudit candles CSV --interval TIMEFRAME` and fails closed if CandleAudit reports errors. The integrated browser uses its own strict loader and has an optional checkbox to run the installed CandleAudit subprocess. When requested, the independent candle check must pass before replay; a missing installation or failed audit stops the run.

## Planned, not yet implemented: complete time/ledger audit

CandleAudit can independently assess feature availability and next-bar entry times from its own CSV input. This MVP's event ledger is not yet exported to that schema, and **same-bar TP/SL exits** need an explicit compatibility contract: CandleAudit's current trade validation requires `exit_time > entry_candle_open`, while an OHLC backtest may enter and exit inside the same candle. Fabricating an exit time to make the audit pass would be incorrect.

Therefore this project must not claim a full trade-level CandleAudit PASS until event time semantics, same-bar exits and data representation are agreed and regression-tested.

## Coverage statement

- Internal loader: checks OHLC range, timestamps, gaps, duplicate/out-of-order bars, volume and positive prices.
- Optional independent CandleAudit: currently candle-level only, CLI and browser checkbox.
- Future: feature-availability logs and trade-ledger parity validation with explicit treatment of within-bar ambiguity.
