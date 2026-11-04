# Indicator catalog and TradingView interoperability

**No claim of full TradingView compatibility.** TradingView provides popular built-ins, public Pine Script source, protected scripts and invite-only scripts with different rights and access. It does not follow that every indicator can be imported or executed outside its platform.

## What is implemented now

- SMA: exact arithmetic rolling mean, warmup `length` bars.
- EMA: alpha `2/(length+1)` with the **first full SMA window as seed**; other platforms may seed EMA differently.
- RSI: Wilder smoothing, initial value after `length` price changes, flat prices return 50.
- ATR: Wilder smoothing of true range with the first `length` bar ranges as seed.
- MACD: difference of EMAs with same seed conventions; signal EMA seeded after complete MACD values become available.
- BBands: SMA plus/minus population standard deviation × deviations, not sample std.
- OHLCV raw price and volume fields.

These definitions are *testable* but **not guaranteed** to numerically match Pine `ta.*` or TA-Lib. Timing, missing values, warmup, `security()`/multi-timeframe semantics, history and realtime updates can differ.

## Future indicator providers

1. **Core deterministic definitions** (today): fixed math, tests, versioned and reproducible.
2. **Optional TA-Lib backend** (planned, not implemented): functions are numerous, but version/pin/output aliases and parity must be verified independently. See https://github.com/TA-Lib/ta-lib-python. A provider must expose supported types/parameters, signal availability, warmup, and output names.
3. **Optional user-supplied open-source Pine adapter** (research stage, not implemented): run only source the user has the right to use, isolate execution and test numerical equivalence on synthetic fixtures. An independent project such as PineTS exists, but third-party compatibility should be evaluated, not presumed. See https://www.npmjs.com/package/pinets.
4. **Protected/invite-only scripts**: never try to extract hidden code or bypass licensing/access protections.

## Required gates for a new indicator

- Open-source license and attribution reviewed.
- Known formula, version, warmup and `na` behavior documented.
- At least three reference fixtures (normal/rising, missing/flat, edge) with expected values.
- No access to future bars or lookahead during computation.
- Multi-output aliases and cross operators validated.
- Reference results compared with the intended TradingView/Pine function if TV parity is advertised. Distinguish **closed historical bars** from realtime recalculation or repainting behavior.
- Regression tests and CI passing before inclusion in the advertised catalog.

## Legal and practical note

TradingView script-publication rules and default open-source script licenses do not make protected or invite-only scripts freely reusable. TradingView's own publication rules also restrict public reuse. Consult the official documentation and the actual license of each script before distributing third-party code. Our project is independent and is not affiliated with TradingView.
