import unittest
from unittest.mock import patch
import json
from candlebacktest_ai.ai import interpret
from candlebacktest_ai.schema import DEFAULTS

class AIValidation(unittest.TestCase):
    def test_bad_description(self):
        with self.assertRaises(ValueError): interpret('hi')
    def test_fake_code_from_model_cannot_be_executed(self):
        class Answer:
            status=200
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self,*args):return json.dumps({'message':{'content':json.dumps({'strategy':{'python':'import os'},'questions':[],'assumptions':[]})}}).encode()
        with patch('candlebacktest_ai.ai.request.urlopen',return_value=Answer()):
            with self.assertRaisesRegex(ValueError,'supported strategy schema'):
                interpret('Cross EMA 20 above EMA 50, buy next bar')
    def test_strict_model_response(self):
        class Answer:
            status=200
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self,*args):return json.dumps({'message':{'content':json.dumps({'strategy':DEFAULTS,'questions':['Confirm rules'],'assumptions':['4h timeframe assumed']})}}).encode()
        with patch('candlebacktest_ai.ai.request.urlopen',return_value=Answer()):
            r=interpret('Cross EMA 20 above EMA 50, buy next bar')
            self.assertEqual(r['questions'],['Confirm rules'])

if __name__=='__main__':unittest.main()
