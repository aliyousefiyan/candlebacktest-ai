# Roadmap: fixed, specialized strategy interpreter

MVP v0.1 uses a **single optional local Ollama model** with a consistent prompt and strict JSON validation. The model has **not been trained or fine-tuned** on a private strategy dataset. Enforced output shape is not proof of semantic correctness.

## Evaluation corpus to build next

Create at least 100 original, permission-safe examples with expert-reviewed gold JSON: Persian and English, crossovers, thresholds, TP/SL timing, contradictory requests, ambiguous RSI conditions, unsupported multi-timeframe scripts, short and margin, future-data traps, and Pine-style descriptions. Keep this corpus synthetic and publicly redistributable.

## Metrics

- Exact match of validated rules (entry, exit, timeframe, timing and risk) against gold annotations.
- Ambiguity recall: proportion of missing/contradictory requirements that generate explicit questions.
- Unsupported-rule rejection rate and false-accept rate.
- Parse success and JSON schema validation rates.
- Cost, latency, privacy, local hardware footprint and model drift.

## Quality gates

1. Pin exact LLM version and system prompt, with an independent holdout test set.
2. Never invent missing values without labeling them as assumptions.
3. Mandatory explicit human approval of the full normalized JSON before replay.
4. No arbitrary AI code is compiled or executed.
5. Build regression examples from legitimate user reports with sensitive details removed.
6. Only consider fine-tuning after measuring failures and demonstrating improvement over constrained prompting + examples.

## Security

User text is supplied to a local model over loopback. Untrusted prompt content must not be treated as system directives, commands or API credentials. The engine reads only constrained JSON. Never expose the local server externally without adding authentication, TLS and request controls.
