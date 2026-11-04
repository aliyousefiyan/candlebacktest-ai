import unittest
from candlebacktest_ai.indicators import sma, ema, rsi, macd, atr, bollinger, calculate

class IndicatorsTest(unittest.TestCase):
    def test_sma_warmup(self):
        self.assertEqual(sma([1,2,3,4],3),[None,None,2,3])
    def test_ema_seed_and_values(self):
        self.assertEqual(ema([1,2,3,4,5],3),[None,None,2,3,4])
    def test_ema_no_values_until_warm(self):
        self.assertEqual(ema([1,2],3),[None,None])
    def test_rsi_increasing_and_flat(self):
        self.assertEqual(rsi([1,2,3,4,5],3)[3:], [100.0,100.0])
        self.assertEqual(rsi([2,2,2,2,2],3)[3:], [50.0,50.0])
    def test_rsi_decreasing(self):
        self.assertEqual(rsi([5,4,3,2,1],3)[3:], [0.0,0.0])
    def test_macd_stays_none_until_signal_warm(self):
        r=macd(list(range(1,20)),3,5,3)
        self.assertIsNone(r['line'][3]);self.assertIsNotNone(r['line'][4]);self.assertIsNone(r['signal'][5]);self.assertIsNotNone(r['signal'][6]);self.assertAlmostEqual(r['histogram'][18],0,places=8)
    def test_atr_true_range(self):
        a=atr([11,14,15],[9,12,12],[10,13,14],2)
        self.assertEqual(a[0],None);self.assertEqual(a[1],3.0)
    def test_bbands(self):
        b=bollinger([1,2,3],3,2)
        self.assertEqual(b['middle'],[None,None,2])
        self.assertAlmostEqual(b['upper'][2]-2,2*(2/3)**0.5)
    def test_calculate_register(self):
        data=[{'open':1,'high':2,'low':.5,'close':i+1,'volume':100} for i in range(10)]
        r=calculate(data,{'m':{'type':'macd','fast':2,'slow':4,'signal':3},'b':{'type':'bbands','length':3}})
        self.assertIn('m.histogram',r);self.assertIn('b.upper',r)

if __name__=='__main__':unittest.main()
