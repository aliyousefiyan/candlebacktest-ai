"""Optional local LLM -> constrained JSON strategy proposal, never executable code."""
from __future__ import annotations
import json
import os
from urllib import request, error
from .schema import validate_spec, DEFAULTS

AI_SYSTEM = """You translate human trading strategies into a strictly declarative, auditable schema.
You NEVER generate Python/Pine code or claim to run a backtest. Reply ONLY with a JSON object:
{"strategy": {"name":"...","symbol":"DEMOUSDT","timeframe":"4h", "initial_cash":10000,
"allocation_pct":20,"fee_bps":5,"slippage_bps":0,"tp_pct":10,"sl_pct":5,
"indicators":{"fast":{"type":"ema","length":20},"slow":{"type":"ema","length":50}},
"entry":{"all":[{"left":"fast","op":"crosses_above","right":"slow"}]},
"exit":{"all":[{"left":"fast","op":"crosses_below","right":"slow"}]}},
"questions": ["one clarifying question about every unspecified important trading rule"],
"assumptions": ["every proposed default that was not explicitly given by the user"]}
Supported types: ema, sma, rsi, atr, macd, bbands. Raw fields: open,high,low,close,volume.
References to macd outputs are alias.line, alias.signal, alias.histogram;
bbands outputs alias.upper, alias.middle, alias.lower.
Comparison operators: crosses_above, crosses_below, gt, gte, lt, lte.
Only AND conjunction is supported via `all`; no Python, no OR, no arbitrary execution.
Ask about price fill timing, TP/SL, fees, timeframe, short or long, allocation.
If the strategy cannot be represented by supported features, list it as an unsupported
question and do not invent an approximation. Only long-only spot is supported.
For Pine scripts, never claim full native Pine Script support or compile them.
"""


def interpret(description: str, model: str | None = None) -> dict:
    if not isinstance(description,str) or not 5<=len(description.strip())<=10000:
        raise ValueError("strategy description must be between 5 and 10000 characters")
    model=model or os.environ.get("CANDLEBACKTEST_OLLAMA_MODEL", "qwen2.5:7b")
    # Fixed localhost endpoint to limit accidental exfiltration of strategy descriptions.
    url="http://127.0.0.1:11434/api/chat"
    prompt={"model":model,"stream":False,"format":"json","options":{"temperature":0},
            "messages":[{"role":"system","content":AI_SYSTEM},
                        {"role":"user","content":description}]}
    data=json.dumps(prompt).encode("utf-8")
    try:
        req=request.Request(url,data=data,headers={"Content-Type":"application/json"},method="POST")
        with request.urlopen(req,timeout=90) as reply:
            if reply.status != 200:
                raise ValueError("local AI service returned a non-success status")
            payload=json.loads(reply.read(2_000_000).decode("utf-8"))
    except (error.URLError,TimeoutError) as exc:
        raise ValueError("Local Ollama AI is unavailable. Install/start Ollama and pull the configured model, or use manual rules.") from exc
    try:
        response=json.loads(payload["message"]["content"])
        if not isinstance(response,dict) or set(response)!={"strategy","questions","assumptions"}:
            raise ValueError("AI must return strategy/questions/assumptions")
        if not isinstance(response["strategy"],dict) or set(DEFAULTS) - set(response["strategy"]):
            raise ValueError("AI must provide every top-level strategy field explicitly, including assumptions")
        spec=validate_spec(response["strategy"])
        questions=response["questions"]
        assumptions=response["assumptions"]
        if (not isinstance(questions,list) or not isinstance(assumptions,list)
                or any(not isinstance(x,str) for x in questions+assumptions)):
            raise ValueError("invalid clarification lists")
        if len(questions)>20 or len(assumptions)>30:
            raise ValueError("too many clarification items")
        return {"strategy":spec,"questions":questions,"assumptions":assumptions,
                "notice":"AI proposal only. Human review/confirmation required before running. No AI-generated code is executed."}
    except (TypeError,KeyError,ValueError,json.JSONDecodeError) as exc:
        raise ValueError(f"Model output does not match the supported strategy schema: {exc}") from exc
