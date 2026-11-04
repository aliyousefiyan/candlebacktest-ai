---
name: Bug report / گزارش خطا
about: Report a reproducible engine, indicator, import or UI defect
title: "[BUG] "
labels: []
assignees: []
---

## Summary / خلاصه

Describe the defect and why the result is incorrect.

## Reproduction / بازتولید

1. Repository commit SHA:
2. Python version and operating system:
3. Command or UI action:
4. Strategy JSON (minimal, non-sensitive):
5. Minimal **synthetic** OHLCV CSV (or generator):
6. Exact steps:

## Expected and actual / انتظار و نتیجه

- Expected result:
- Actual result:
- Error output or relevant trade ledger rows:
- Does it reproduce twice with the same inputs?

## Execution and timing checks

- Candle timestamps and timeframe in UTC:
- Signal bar and planned next-open entry:
- Fee, slippage and TP/SL collision assumptions:
- Did the external AI suggest a rule that differs from the intended strategy?

## Privacy and safety

Do **not** publish API keys, account identifiers, real private trading logs, copyrighted Pine scripts, or non-redistributable datasets. Report security issues privately via SECURITY.md.
