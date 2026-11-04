"""Fail-closed, declarative strategy validation; never eval model-generated code."""
from __future__ import annotations
import copy
import math
from .indicators import CATALOG

OPS = {"crosses_above", "crosses_below", "gt", "gte", "lt", "lte"}
INTERVALS = {"5m":300,"15m":900,"1h":3600,"4h":14400,"1d":86400}
DEFAULTS = {"name":"EMA crossover demo", "symbol":"DEMOUSDT", "timeframe":"4h", "initial_cash":10000,
            "allocation_pct":20,"fee_bps":5,"slippage_bps":0,"tp_pct":10,"sl_pct":5,
            "indicators":{"fast":{"type":"ema","length":20},"slow":{"type":"ema","length":50}},
            "entry":{"all":[{"left":"fast","op":"crosses_above","right":"slow"}]},
            "exit":{"all":[{"left":"fast","op":"crosses_below","right":"slow"}]}}


def _number(x, name, lower, upper, inclusive_lower=True):
    if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x):
        raise ValueError(f"{name}: expected finite numeric value")
    if x < lower or (x == lower and not inclusive_lower) or x > upper:
        raise ValueError(f"{name}: expected {lower}..{upper}")
    return float(x)


def validate_spec(value: dict) -> dict:
    if not isinstance(value,dict):
        raise ValueError("strategy must be a JSON object")
    unknown = set(value) - set(DEFAULTS)
    if unknown:
        raise ValueError(f"unsupported strategy fields: {sorted(unknown)}")
    s = copy.deepcopy(DEFAULTS)
    s.update(copy.deepcopy(value))
    for key in ("name","symbol","timeframe"):
        if not isinstance(s[key],str) or not s[key].strip() or len(s[key]) > 100:
            raise ValueError(f"invalid {key}")
    if s["timeframe"] not in INTERVALS:
        raise ValueError(f"unsupported timeframe: {s['timeframe']}")
    if not (s["symbol"].replace("_","").isalnum()):
        raise ValueError("symbol must contain only letters, digits or underscore")
    for key,lo,hi,inc in [("initial_cash",0,1e12,False),("allocation_pct",0,100,False),
                           ("fee_bps",0,1000,True),("slippage_bps",0,1000,True),
                           ("tp_pct",0,1000,False),("sl_pct",0,99.9,False)]:
        s[key] = _number(s[key],key,lo,hi,inc)
    indicators = s["indicators"]
    if not isinstance(indicators,dict) or len(indicators) > 30:
        raise ValueError("indicators must be an object with <=30 entries")
    references = {"open","high","low","close","volume"}
    for alias,spec in indicators.items():
        if not isinstance(alias,str) or not alias.isidentifier() or len(alias)>40 or alias in references:
            raise ValueError(f"invalid/duplicate indicator alias {alias!r}")
        if not isinstance(spec,dict) or spec.get("type") not in CATALOG:
            raise ValueError(f"unknown indicator type in {alias}")
        kind=spec["type"]
        if kind in references:
            raise ValueError("base price/volume are automatically available; do not alias them")
        allowed={"type",*CATALOG[kind]["params"]}
        if kind=="bbands": allowed.add("deviations")
        if set(spec)-allowed or set(CATALOG[kind]["params"])-set(spec):
            raise ValueError(f"{alias}: unexpected or missing indicator parameters")
        for param in CATALOG[kind]["params"]:
            n=spec[param]
            if isinstance(n,bool) or not isinstance(n,int) or not 1<=n<=1000:
                raise ValueError(f"{alias}.{param} must be integer 1..1000")
        if kind=="macd" and spec["fast"]>=spec["slow"]:
            raise ValueError("MACD fast must be < slow")
        if "deviations" in spec: _number(spec["deviations"],"deviations",0,20,False)
        if kind in ("macd","bbands"):
            references.update(f"{alias}.{k}" for k in CATALOG[kind]["outputs"])
        else:
            references.add(alias)
    for part in ("entry","exit"):
        cond=s[part]
        if not isinstance(cond,dict) or set(cond)!={"all"} or not isinstance(cond["all"],list) or len(cond["all"])>15 or (part=="entry" and not cond["all"]):
            raise ValueError(f"{part} must be {{'all': [conditions]}} (entry requires a condition)")
        for c in cond["all"]:
            if not isinstance(c,dict) or set(c)!={"left","op","right"}:
                raise ValueError(f"{part} condition must contain left/op/right only")
            if c["op"] not in OPS:
                raise ValueError(f"unsupported comparison operator {c['op']}")
            for side in ("left","right"):
                item=c[side]
                if isinstance(item,str):
                    if item not in references:
                        raise ValueError(f"unknown indicator/field reference {item!r}")
                elif isinstance(item,bool) or not isinstance(item,(int,float)) or not math.isfinite(item):
                    raise ValueError(f"invalid numeric/reference {side}")
    return s
