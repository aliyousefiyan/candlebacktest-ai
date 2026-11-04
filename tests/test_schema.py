import unittest
from candlebacktest_ai.schema import validate_spec, DEFAULTS

class ValidationTest(unittest.TestCase):
    def test_default_valid(self):
        self.assertEqual(validate_spec({})['timeframe'],'4h')
    def test_no_arbitrary_code(self):
        with self.assertRaisesRegex(ValueError,'unsupported strategy fields'):
            validate_spec({'python':'import os'})
    def test_bad_indicator_alias(self):
        with self.assertRaises(ValueError):
            validate_spec({'indicators':{'close':{'type':'ema','length':3}}})
    def test_invalid_reference(self):
        with self.assertRaises(ValueError):
            validate_spec({'entry':{'all':[{'left':'UNKNOWN','op':'gt','right':1}]}})
    def test_unknown_op(self):
        with self.assertRaises(ValueError):
            validate_spec({'entry':{'all':[{'left':'close','op':'python','right':1}]}})
    def test_no_short(self):
        with self.assertRaises(ValueError):
            validate_spec({'direction':'short'})
    def test_no_leverage(self):
        with self.assertRaises(ValueError):
            validate_spec({'leverage':10})
    def test_reject_bool_as_amount(self):
        with self.assertRaises(ValueError):
            validate_spec({'tp_pct':True})
    def test_reject_unsupported_indicator(self):
        with self.assertRaises(ValueError):
            validate_spec({'indicators':{'x':{'type':'custom_future','length':10}}})
    def test_empty_exit_supported(self):
        self.assertEqual(validate_spec({'exit':{'all':[]}})['exit'],{'all':[]})

if __name__=='__main__':unittest.main()
