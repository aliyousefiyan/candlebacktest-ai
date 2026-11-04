import unittest
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import urlopen,Request
from urllib.error import HTTPError
from pathlib import Path
import json
from candlebacktest_ai.server import Handler

class ServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.thread=Thread(target=cls.srv.serve_forever,daemon=True);cls.thread.start()
        cls.base=f'http://127.0.0.1:{cls.srv.server_address[1]}'
    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown();cls.srv.server_close();cls.thread.join(timeout=2)
    def test_html(self):
        with urlopen(self.base,timeout=3) as r:
            self.assertIn('CandleBacktest AI',r.read().decode())
    def test_catalog(self):
        with urlopen(self.base+'/api/catalog',timeout=3) as r:
            self.assertIn('macd',json.loads(r.read())['catalog'])
    def test_api_replay(self):
        root=Path(__file__).resolve().parents[1]
        spec=json.loads((root/'examples'/'ema_cross.json').read_text())
        candles=(root/'examples'/'candles_synthetic_4h.csv').read_text()
        req=Request(self.base+'/api/backtest',data=json.dumps({'strategy':spec,'csv':candles}).encode(),headers={'Content-Type':'application/json'},method='POST')
        with urlopen(req,timeout=3) as r:
            data=json.loads(r.read())
            self.assertTrue(data['ok']);self.assertEqual(data['report']['candles'],420)
            self.assertIsNone(data['candleaudit'])
    def test_reject_script(self):
        req=Request(self.base+'/api/backtest',data=json.dumps({'strategy':{'python':'do bad things'},'csv':'oops'}).encode(),headers={'Content-Type':'application/json'},method='POST')
        with self.assertRaises(HTTPError) as cm:urlopen(req,timeout=3)
        self.assertEqual(cm.exception.code,400)

if __name__=='__main__':unittest.main()
