"""Optional actual CandleAudit integration using its documented local CLI."""
from __future__ import annotations
import json
import shutil
import subprocess


def require_candleaudit_ok(candles_path: str, interval: str) -> dict:
    exe=shutil.which("candleaudit")
    if not exe:
        raise ValueError("CandleAudit not installed; install git+https://github.com/aliyousefiyan/candleaudit.git")
    proc=subprocess.run([exe,"candles",str(candles_path),"--interval",interval],
                        capture_output=True,text=True,timeout=90,check=False)
    if proc.returncode not in (0,1):
        raise ValueError(f"CandleAudit input failure: {proc.stderr[:500]}")
    try: report=json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("CandleAudit produced unreadable JSON") from exc
    if not report.get("ok") or proc.returncode!=0:
        raise ValueError("CandleAudit rejected this candle dataset; fix input before backtesting")
    return report
