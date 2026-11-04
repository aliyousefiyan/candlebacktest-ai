"""Local-only integrated interface: untrusted strategy JSON never becomes code."""
from __future__ import annotations
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
from io import StringIO
from pathlib import Path
import csv, json, os, tempfile
from .schema import validate_spec, DEFAULTS
from .engine import read_candles, backtest
from .ai import interpret
from .indicators import CATALOG

MAX_BODY=5_000_000

class Handler(BaseHTTPRequestHandler):
    def _reply(self,status,payload):
        content=json.dumps(payload,ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(content)))
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        if self.path=="/":
            content=resources.files("candlebacktest_ai").joinpath("static/index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Content-Length",str(len(content)))
            self.send_header("X-Content-Type-Options","nosniff")
            self.end_headers()
            self.wfile.write(content)
        elif self.path=="/api/catalog":
            self._reply(200,{"catalog":CATALOG,"ai_model":os.environ.get("CANDLEBACKTEST_OLLAMA_MODEL","qwen2.5:7b")})
        else:self._reply(404,{"error":"not found"})

    def do_POST(self):
        if self.path not in ("/api/backtest","/api/interpret","/api/validate"):
            self._reply(404,{"error":"not found"});return
        try:
            n=int(self.headers.get("Content-Length","-1"))
            if n<0 or n>MAX_BODY:raise ValueError("JSON payload must be <5MB")
            content=self.rfile.read(n)
            data=json.loads(content)
            if not isinstance(data,dict):raise ValueError("JSON object required")
            if self.path=="/api/interpret":
                result=interpret(data.get("description",""))
                self._reply(200,{"ok":True,**result})
            elif self.path=="/api/validate":
                submitted=data.get("strategy")
                if not isinstance(submitted,dict) or set(submitted)!=set(DEFAULTS):
                    raise ValueError("External AI strategy must explicitly include all required top-level fields")
                self._reply(200,{"ok":True,"strategy":validate_spec(submitted),"warning":"Structural validity does not prove the strategy was interpreted correctly."})
            else:
                spec=validate_spec(data.get("strategy"))
                csv_text=data.get("csv")
                if not isinstance(csv_text,str) or not csv_text.strip():
                    raise ValueError("CSV file is required")
                # Files are local and temporary. User-selected paths never flow into subprocesses.
                with tempfile.TemporaryDirectory(prefix="candlebacktest_") as tmp:
                    path=Path(tmp)/"input.csv"
                    path.write_text(csv_text,encoding="utf-8")
                    rows=read_candles(path,spec["symbol"],spec["timeframe"])
                    independent_audit=None
                    if data.get("audit",False) is True:
                        from .audit import require_candleaudit_ok
                        independent_audit=require_candleaudit_ok(str(path),spec["timeframe"])
                result=backtest(spec,rows)
                self._reply(200,{"ok":True,"report":result,"candleaudit":independent_audit})
        except (ValueError,TypeError,json.JSONDecodeError) as exc:
            self._reply(400,{"ok":False,"error":str(exc)})


def serve(port:int=8765,open_browser:bool=False):
    if not 1024<=port<=65535:raise ValueError("port must be 1024..65535")
    address=("127.0.0.1",port)
    with ThreadingHTTPServer(address,Handler) as server:
        print(f"CandleBacktest AI running at http://127.0.0.1:{port}",flush=True)
        if open_browser:
            import webbrowser
            webbrowser.open_new_tab(f"http://127.0.0.1:{port}")
        server.serve_forever()
