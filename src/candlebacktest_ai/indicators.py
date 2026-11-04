"""Deterministic indicators from closed bars; None means not warmed up.

These conventions are explicitly documented and are NOT claimed to be
identical to every TradingView/Pine implementation or TA-Lib configuration.
"""
from __future__ import annotations
from math import sqrt
from typing import Optional

Number = Optional[float]


def sma(values: list[float], length: int) -> list[Number]:
    if length < 1:
        raise ValueError("length must be positive")
    result: list[Number] = [None] * len(values)
    total = 0.0
    for i, value in enumerate(values):
        total += value
        if i >= length:
            total -= values[i - length]
        if i >= length - 1:
            result[i] = total / length
    return result


def ema(values: list[float], length: int) -> list[Number]:
    """EMA seeded using the first full-window SMA (not first value)."""
    if length < 1:
        raise ValueError("length must be positive")
    out: list[Number] = [None] * len(values)
    if len(values) < length:
        return out
    prev = sum(values[:length]) / length
    out[length - 1] = prev
    k = 2.0 / (length + 1)
    for i in range(length, len(values)):
        prev = prev + k * (values[i] - prev)
        out[i] = prev
    return out


def rsi(values: list[float], length: int) -> list[Number]:
    """Wilder RSI with first value at index `length`; flat market = 50."""
    if length < 1:
        raise ValueError("length must be positive")
    out: list[Number] = [None] * len(values)
    if len(values) <= length:
        return out
    changes = [values[i] - values[i-1] for i in range(1, len(values))]
    avg_up = sum(max(c, 0) for c in changes[:length]) / length
    avg_down = sum(max(-c, 0) for c in changes[:length]) / length

    def result(up: float, down: float) -> float:
        if up == 0 and down == 0:
            return 50.0
        if down == 0:
            return 100.0
        return 100 - 100 / (1 + up / down)

    out[length] = result(avg_up, avg_down)
    for i in range(length + 1, len(values)):
        c = values[i] - values[i - 1]
        avg_up = (avg_up * (length - 1) + max(c, 0)) / length
        avg_down = (avg_down * (length - 1) + max(-c, 0)) / length
        out[i] = result(avg_up, avg_down)
    return out


def bollinger(values: list[float], length: int, deviations: float = 2.0) -> dict[str, list[Number]]:
    if length < 1 or deviations <= 0:
        raise ValueError("invalid Bollinger settings")
    middle = sma(values, length)
    upper: list[Number] = [None] * len(values)
    lower: list[Number] = [None] * len(values)
    for i in range(length - 1, len(values)):
        assert middle[i] is not None
        variance = sum((v - middle[i]) ** 2 for v in values[i-length+1:i+1]) / length
        std = sqrt(variance)
        upper[i] = middle[i] + deviations * std
        lower[i] = middle[i] - deviations * std
    return {"middle": middle, "upper": upper, "lower": lower}


def atr(highs: list[float], lows: list[float], closes: list[float], length: int) -> list[Number]:
    if length < 1:
        raise ValueError("length must be positive")
    n = len(closes)
    if len(highs) != n or len(lows) != n:
        raise ValueError("OHLC length mismatch")
    tr = [highs[0] - lows[0]] if n else []
    for i in range(1, n):
        tr.append(max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1])))
    out: list[Number] = [None] * n
    if n < length:
        return out
    previous = sum(tr[:length]) / length
    out[length-1] = previous
    for i in range(length, n):
        previous = (previous * (length-1) + tr[i]) / length
        out[i] = previous
    return out


def macd(values: list[float], fast: int, slow: int, signal: int) -> dict[str, list[Number]]:
    if not 1 <= fast < slow or signal < 1:
        raise ValueError("MACD fast/slow/signal invalid")
    fast_values = ema(values, fast)
    slow_values = ema(values, slow)
    line: list[Number] = [None if a is None or b is None else a - b for a, b in zip(fast_values, slow_values)]
    first = next((i for i, x in enumerate(line) if x is not None), len(line))
    signal_values = [None] * len(values)
    available = [float(x) for x in line[first:] if x is not None]
    if available:
        signal_values[first:] = ema(available, signal)
    hist = [None if a is None or b is None else a-b for a,b in zip(line,signal_values)]
    return {"line":line,"signal":signal_values,"histogram":hist}


CATALOG = {
    "close": {"params": [], "outputs": ["value"]},
    "open": {"params": [], "outputs": ["value"]},
    "high": {"params": [], "outputs": ["value"]},
    "low": {"params": [], "outputs": ["value"]},
    "volume": {"params": [], "outputs": ["value"]},
    "sma": {"params": ["length"], "outputs": ["value"]},
    "ema": {"params": ["length"], "outputs": ["value"]},
    "rsi": {"params": ["length"], "outputs": ["value"]},
    "atr": {"params": ["length"], "outputs": ["value"]},
    "bbands": {"params": ["length"], "outputs": ["upper", "middle", "lower"]},
    "macd": {"params": ["fast", "slow", "signal"], "outputs": ["line", "signal", "histogram"]},
}


def calculate(candles: list[dict], indicators: dict[str, dict]) -> dict[str, list[Number]]:
    data = {k: [float(c[k]) for c in candles] for k in ("open", "high", "low", "close", "volume")}
    result: dict[str, list[Number]] = {**data}
    closes = data["close"]
    for alias, spec in indicators.items():
        kind = spec["type"]
        if kind in ("sma","ema","rsi"):
            values = {"sma":sma,"ema":ema,"rsi":rsi}[kind](closes,int(spec["length"]))
            result[alias] = values
        elif kind == "atr":
            result[alias] = atr(data["high"],data["low"],closes,int(spec["length"]))
        elif kind == "bbands":
            for name, values in bollinger(closes,int(spec["length"]),float(spec.get("deviations",2))).items():
                result[f"{alias}.{name}"] = values
        elif kind == "macd":
            for name, values in macd(closes,int(spec["fast"]),int(spec["slow"]),int(spec["signal"])).items():
                result[f"{alias}.{name}"] = values
        else:
            raise ValueError(f"unsupported indicator {kind}")
    return result
