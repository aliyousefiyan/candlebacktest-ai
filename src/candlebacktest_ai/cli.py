"""Command line entry point for deterministic replay and local interface."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from .engine import read_candles, backtest
from .schema import validate_spec


def parser():
    p=argparse.ArgumentParser(prog="candlebacktest",description="Local-first auditable backtester")
    sub=p.add_subparsers(dest="command",required=True)
    r=sub.add_parser("run",help="replay a declarative strategy on OHLCV CSV")
    r.add_argument("--strategy",required=True)
    r.add_argument("--candles",required=True)
    r.add_argument("--output",help="write full report JSON to file")
    r.add_argument("--audit",action="store_true",help="run installed CandleAudit candle checks first (fail closed)")
    w=sub.add_parser("web",help="serve the integrated local browser interface")
    w.add_argument("--port",type=int,default=8765)
    w.add_argument("--browser",action="store_true",help="open the local browser page automatically")
    sub.add_parser("catalog",help="show supported indicators")
    return p


def main(argv=None) -> int:
    args=parser().parse_args(argv)
    try:
        if args.command=="catalog":
            from .indicators import CATALOG
            print(json.dumps(CATALOG,indent=2));return 0
        if args.command=="web":
            from .server import serve
            serve(args.port,open_browser=args.browser);return 0
        spec=validate_spec(json.loads(Path(args.strategy).read_text(encoding="utf-8")))
        if args.audit:
            from .audit import require_candleaudit_ok
            require_candleaudit_ok(args.candles,spec["timeframe"])
        result=backtest(spec,read_candles(args.candles,spec["symbol"],spec["timeframe"]))
        output=json.dumps(result,ensure_ascii=False,indent=2)
        if args.output: Path(args.output).write_text(output+"\n",encoding="utf-8")
        print(output)
        return 0
    except (OSError,ValueError,json.JSONDecodeError) as exc:
        print(json.dumps({"ok":False,"error":str(exc)}),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
