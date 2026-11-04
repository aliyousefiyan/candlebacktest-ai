import unittest
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from threading import Thread
import json
from candlebacktest_ai.schema import DEFAULTS, validate_spec
from candlebacktest_ai.server import Handler

ROOT=Path(__file__).resolve().parents[1]
class PromptAndImportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.thr=Thread(target=cls.srv.serve_forever,daemon=True);cls.thr.start()
        cls.base=f'http://127.0.0.1:{cls.srv.server_address[1]}'
    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown();cls.srv.server_close();cls.thr.join(timeout=2)
    def post(self,spec):
        return Request(self.base+'/api/validate',data=json.dumps({'strategy':spec}).encode(),headers={'Content-Type':'application/json'},method='POST')
    def test_prompt_mentions_every_field(self):
        prompt=(ROOT/'docs/EXTERNAL_AI_PROMPT_FA.md').read_text(encoding='utf-8')
        for key in DEFAULTS: self.assertIn('`'+key+'`',prompt)
    def test_chatgpt_sample_envelope(self):
        envelope=json.loads((ROOT/'examples/ai_chatgpt_response.json').read_text(encoding='utf-8'))
        self.assertEqual(set(envelope),{'strategy','questions','assumptions'})
        self.assertEqual(envelope['questions'],[])
        self.assertEqual(envelope['assumptions'],[])
        self.assertEqual(set(envelope['strategy']),set(DEFAULTS))
        validate_spec(envelope['strategy'])

    def test_external_prompt_in_ui(self):
        with urlopen(self.base,timeout=3) as reply: html=reply.read().decode()
        for needle in ['copyExternalPrompt','externalOutput','loadExternal','externalJsonFile','/api/validate','پرامپت رسمی']:
            self.assertIn(needle,html)
    def test_validate_explicit_complete(self):
        spec=json.loads((ROOT/'examples/ema_cross.json').read_text())
        with urlopen(self.post(spec),timeout=3) as reply:
            data=json.loads(reply.read())
        self.assertTrue(data['ok'])
        self.assertEqual(data['strategy'],validate_spec(spec))
    def test_reject_missing_explicit_field(self):
        spec=json.loads((ROOT/'examples/ema_cross.json').read_text());spec.pop('fee_bps')
        with self.assertRaises(HTTPError) as err:urlopen(self.post(spec),timeout=3)
        self.assertEqual(err.exception.code,400)
    def test_reject_unsupported_indicator(self):
        spec=json.loads((ROOT/'examples/ema_cross.json').read_text());spec['indicators']['fast']['type']='orderblock'
        with self.assertRaises(HTTPError) as err:urlopen(self.post(spec),timeout=3)
        self.assertEqual(err.exception.code,400)

if __name__=='__main__':unittest.main()
