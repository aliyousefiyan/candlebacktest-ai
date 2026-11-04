# Strategy schema and deterministic execution contract (v0.1)

Strategies are **declarative JSON objects**. No `eval`, Python callback, plugins, arbitrary source code, Pine execution or command shell is accepted as a strategy definition. See `examples/ema_cross.json` as the canonical fully specified example.

## Strategy keys

- `name`: nonempty descriptive title.
- `symbol`, `timeframe`: one instrument; timeframes `5m`, `15m`, `1h`, `4h`, `1d`.
- `initial_cash`: positive starting quote currency, e.g. 10000 USDT.
- `allocation_pct`: 0–100% of **available cash** used per entry. This is *NOT* a stop-distance risk percent.
- `fee_bps`, `slippage_bps`: numeric bps (5 = 0.05%). Both charged adversely; entry cost includes fee.
- `tp_pct`, `sl_pct`: fixed relative to entry fill; both required in v0.1.
- `indicators`: alias → supported type with required integer parameters. Multi-output references use dotted output aliases like `m.line`.
- `entry`, `exit`: `{"all": [{"left": "fast", "op": "crosses_above", "right": "slow"}]}`. `exit.all` may be empty; `entry.all` cannot. All conditions must hold. No OR/NOT in this version.

**Missing top-level keys** receive explicit code defaults defined by `DEFAULTS` in `schema.py`. Always inspect the full validated JSON before running. The AI prompt is instructed to list such assumptions, but model answers are not independently guaranteed complete.

## Execution timeline

1. At bar `t` **close**, evaluate conditions using values at `t` and earlier only.
2. Schedule one order for bar `t+1` **open**; there are no same-close fills.
3. Buy uses `open * (1+slippage)`, selling uses adverse slippage `*(1-slippage)`.
4. Only a long spot position; no overlapping entries or shorting.
5. Stops/TP use bar high/low **after** the open and apply even on an entry bar.
6. If both TP and SL touched within the same bar, **SL first**; count ambiguous bars. An open beyond a stop yields the worse opening fill. An open beyond TP yields the better opening fill, but intrabar path is unknown.
7. A conditional signal exit, if triggered at `t` close, fills at `t+1` open. SL/TP take priority during the bar.
8. End-of-data signals are **not filled**; open positions are marked at last candle close, not force-closed.
9. Cash account, entry and exit fees, and open position quantity produce end-of-bar equity. Max drawdown is measured **between bar closes**, not from intrabar extremes; avoid treating this as a validated live floating DD.
10. `close`-bar prices in the generated equity curve include the live marked position but not hypothetical future exit fee. Reported closed-trade PnL includes both fees.

## Data conventions

Required CSV fields: `timestamp,symbol,open,high,low,close,volume`. Open timestamp must be UTC ISO-8601 including a timezone, exact to seconds, aligned to the timeframe and consecutive with no missing interval. All prices > 0, volume >= 0, OHLC internally consistent, one symbol only. Initial v0.1 rejects session gaps; crypto continuous market is the principal application.

## AI processing

The local model proposes JSON and includes a `questions` list and `assumptions` list. The validator checks type/field/parameter constraints; it **cannot verify** that the model understood the original user statement correctly. The browser shows the full JSON to approve; there is no model-generated code execution. Unknown indicator types or unsupported rule forms produce a validation error rather than silent reinterpretation.

## Reproducibility

Fix the exact candle data checksum, UTC/timeframe, JSON file, software commit/package version and indicator conventions. Run with the same Python version; floating-point operations can vary slightly across runtimes. Save the output ledger and compare. For high stakes, independently cross-validate reference examples against another engine before trusting performance.

## Versioned evidence

Each result stores SHA-256 fingerprints of the fully normalized JSON strategy and a canonical per-bar OHLCV stream, as well as the first/last candle timestamp. Store these with the source CSV checksum and Git commit when comparing reruns. The internal OHLCV hash is not the raw file hash: different whitespace or encoding may yield the same parsed candle hash.
