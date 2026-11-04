# CandleBacktest AI

**An early local-first, auditable strategy builder and historical-bar backtester.**

CandleBacktest AI brings strategy description, a constrained AI interpreter, a manual no-code strategy builder, and a deterministic replay engine into **one browser interface**. Users can describe an idea in Persian or English, **review** the proposed JSON rules, then run an illustrative backtest on their own OHLCV CSV. The AI is optional; manual strategy creation and deterministic replay work without AI or internet.

> **Status: experimental MVP v0.1.1.** This is NOT a generalized TradingView/Pine Script execution engine, NOT a trustworthy replacement for all TradingView strategies, NOT a validated real-money performance engine, and NOT a packaged/hosted AI model. There is no proof of live performance or independent trading-strategy profitability.

[راهنمای فارسی](README.fa.md) · [Indicator support](docs/INDICATORS_AND_TRADINGVIEW.md) · [Execution assumptions](docs/EXECUTION_AND_SCHEMA.md) · [AI evaluation plan](docs/AI_EVALUATION.md) · [CandleAudit integration](docs/CANDLEAUDIT.md)

## Fastest local demo (no API key)

Requires **Python 3.10+**. On Windows, double-click `start_windows.cmd` for a guided local start. On Linux/macOS, run `sh start_linux_mac.sh`. The runtime uses only Python standard-library modules. No exchange credentials, trading orders or network requests are needed to run CSV backtests.

```bash
python -m pip install -e .
python -m candlebacktest_ai web --port 8765
```

Open **http://127.0.0.1:8765** in the browser. Select **examples/candles_synthetic_4h.csv**, optionally use the no-code SMA/EMA form to customize parameters, review the generated JSON, confirm the explicit approval checkbox and press Run. The example is generated **synthetically**; its returns are illustrative and must not be interpreted as investment evidence.

### Windows PowerShell without script activation

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m candlebacktest_ai web
```

This approach does not require changing PowerShell execution policies.

## No-install external AI workflow (ChatGPT, Gemini, etc.)

The default free route requires **no Ollama and no API key**: click **Copy official prompt** in the browser or use [the Persian versioned prompt](docs/EXTERNAL_AI_PROMPT_FA.md); answer clarifying questions in your own AI app; paste its final JSON into the web app's **External AI output** field; validate, review, and confirm before running. An external model is **never trusted** to supply executable code or calculations. Unsupported ICT/SMC and market-session constructs must be rejected rather than silently approximated.

This is community software, **not approved, sponsored or certified by OpenAI/ChatGPT**. A GitHub repository does not grant ChatGPT directory listing or app approval. [Free product scope](docs/PRODUCT_SCOPE_FA.md).

## Optional integrated local AI

A locally installed **Ollama** service is used through its loopback API. No API key is required, but the model must be downloaded locally once and the computer must be able to run it. The default model is `qwen2.5:7b`. Install Ollama using its official instructions, then:

```bash
ollama pull qwen2.5:7b
ollama serve  # only if not already running
```

To use a different installed model, set `CANDLEBACKTEST_OLLAMA_MODEL` before starting the application. The app sends user text **only to http://127.0.0.1:11434/api/chat**, and never executes generated Python, Pine Script or external commands from a model. Models **have not been specially trained or fine-tuned for this application**: the current constrained prompt/schema is only a first step. The model can misunderstand strategies; always verify every rule and clarification before running.

### CLI: deterministic replay

```bash
candlebacktest catalog
candlebacktest run --strategy examples/ema_cross.json --candles examples/candles_synthetic_4h.csv --output report.json
```

Optional *external* CandleAudit quality gate (audits candles before replay; requires CandleAudit installed):

```bash
python -m pip install git+https://github.com/aliyousefiyan/candleaudit.git
candlebacktest run --strategy examples/ema_cross.json --candles examples/candles_synthetic_4h.csv --audit --output report.json
```

`--audit` only invokes CandleAudit's **candle integrity audit**; its other independent feature/trade audits have not yet been wired into this replay engine. The browser runs its own strict OHLCV validator and also offers a checkbox to run the external CandleAudit **candle** check when CandleAudit is installed. The full trade/feature audits are not yet integrated.

## Initial capabilities

- Indicators: **SMA, EMA, RSI, ATR, MACD, Bollinger Bands**, plus OHLCV raw series. Comparisons `gt`, `gte`, `lt`, `lte`, `crosses_above`, `crosses_below`, combined with AND. A simple no-code SMA/EMA crossover form is provided. Advanced strategies currently require editable JSON or careful AI interpretation.
- Historical OHLCV: UTF-8 CSV, **one symbol**, continuous equal-spaced UTC candle opens; rejected gaps/duplicates/invalid OHLC and timestamps.
- Order model: **long-only spot**; signal at candle close, entry on next candle open, TP/SL intrabar using OHLC (stop wins when both hit), conservative gap-stop handling, explicit fee/slippage, single position, 0 or 1 open position.
- Results: JSON trade ledger, closed-bar equity curve, total return, *closed-bar* drawdown, win rate and fees; local browser displays chart/table.

## Explicit exclusions

No full Pine Script interpreter; no proprietary/restricted TradingView scripts; no short, margin/futures, leverage, margin calls, funding, realistic queue fills, partial fills, order-book depth, multi-symbol portfolios, variable market sessions, dividends, corporate actions, multi-timeframe alignment, stop-distance position sizing, intrabar path reconstruction or floating intrabar drawdown.

The initial indicators **do not claim numerical parity with TradingView**. Some Pine indicators have different initialization/warmup or realtime bar semantics. [Parity verification plan](docs/INDICATORS_AND_TRADINGVIEW.md) is a gate before advertising any matching behavior.

## Quality

```bash
python -m unittest discover -s tests -v
```

Fixture and tests are local. All market data in this repository is **invented synthetic data**. File ingest rejects missing time intervals rather than silently pretending a run is valid.

## License, privacy and support

MIT, see [LICENSE](LICENSE). No TradingView affiliation. Open-source repos/code must be used according to their original licenses; do not upload protected/invite-only scripts or private strategy rules. Not financial advice. [Security](SECURITY.md) · [Contributing](CONTRIBUTING.md).
