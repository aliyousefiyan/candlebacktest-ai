import unittest
from pathlib import Path
import tempfile
from candlebacktest_ai.engine import backtest,read_candles


def dataset(closes, highs=None,lows=None, opens=None):
    out=[]
    for i,close in enumerate(closes):
        o=opens[i] if opens is not None else close
        h=highs[i] if highs is not None else max(o,close)+1
        l=lows[i] if lows is not None else min(o,close)-1
        out.append({'timestamp':f'candle-{i}','_time':i*14400,'symbol':'DEMOUSDT','open':float(o),'high':float(h),'low':float(l),'close':float(close),'volume':10.0})
    return out


def strat(**overrides):
    s={'name':'test','symbol':'DEMOUSDT','timeframe':'4h','initial_cash':1000.,'allocation_pct':100.,'fee_bps':0.,'slippage_bps':0.,'tp_pct':50.,'sl_pct':50.,'indicators':{},'entry':{'all':[{'left':'close','op':'crosses_above','right':10}]},'exit':{'all':[]}}
    s.update(overrides);return s

class EngineTest(unittest.TestCase):
    def test_entry_next_open_not_signal_close(self):
        bars=dataset([9,11,12,13,13],[10,12,13,14,14],[8,10,11,12,12],opens=[9,11,12,13,13])
        r=backtest(strat(),bars)
        self.assertIsNotNone(r['open_position'])
        self.assertEqual(r['open_position']['entry_time'],'candle-2')
        self.assertEqual(r['open_position']['entry_price'],12)
    def test_stops_prioritize_same_bar_tie(self):
        bars=dataset([9,11,12,12],[10,12,16,13],[8,10,7,11],opens=[9,11,12,12])
        r=backtest(strat(tp_pct=20,sl_pct=20),bars)
        self.assertEqual(r['trades'][0]['exit_reason'],'SL')
        self.assertEqual(r['metrics']['same_bar_stop_tp_ties'],1)
    def test_fee_and_slippage_reduce_return(self):
        bars=dataset([9,11,12,14,14],[10,12,13,15,15],[8,10,11,13,13],opens=[9,11,12,14,14])
        zero=backtest(strat(tp_pct=10,sl_pct=20),bars)
        fees=backtest(strat(tp_pct=10,sl_pct=20,fee_bps=5,slippage_bps=10),bars)
        self.assertGreater(zero['metrics']['final_equity'],fees['metrics']['final_equity'])
        self.assertEqual(fees['metrics']['closed_trades'],1)
        self.assertGreater(fees['metrics']['fees_paid'],0)
    def test_stop_gap_uses_open(self):
        bars=dataset([9,11,12,8],[10,12,13,9],[8,10,11,7],opens=[9,11,12,8])
        r=backtest(strat(tp_pct=90,sl_pct=20),bars)
        self.assertEqual(r['trades'][0]['exit_price'],8)
    def test_last_signal_unfilled(self):
        bars=dataset([9,9,11],[10,10,12],[8,8,10],opens=[9,9,11])
        r=backtest(strat(),bars)
        self.assertEqual(r['metrics']['closed_trades'],0)
        self.assertIsNone(r['open_position'])
        self.assertEqual(r['metrics']['pending_order_unfilled_at_end'],1)
    def test_no_future_read_on_indicator(self):
        base=dataset([8,9,11,12,13],[9,10,12,13,14],[7,8,10,11,12])
        extended=base+dataset([5000])[0:1]
        extended[-1]['timestamp']='candle-5';extended[-1]['_time']=5*14400
        a=backtest(strat(),base);b=backtest(strat(),extended)
        self.assertEqual(a['equity_curve'],b['equity_curve'][:-1])
    def test_valid_csv(self):
        file=Path(__file__).resolve().parents[1]/'examples'/'candles_synthetic_4h.csv'
        rows=read_candles(file,'DEMOUSDT','4h')
        self.assertEqual(len(rows),420)
    def test_reject_missing_bar(self):
        data='timestamp,symbol,open,high,low,close,volume\n2026-01-01T00:00:00Z,DEMOUSDT,1,2,1,1,1\n2026-01-01T08:00:00Z,DEMOUSDT,1,2,1,1,1\n2026-01-01T12:00:00Z,DEMOUSDT,1,2,1,1,1\n'
        with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',suffix='.csv',delete=False) as f:
            f.write(data);path=f.name
        try:
            with self.assertRaisesRegex(ValueError,'missing, duplicated'):
                read_candles(path,'DEMOUSDT','4h')
        finally:Path(path).unlink()
    def test_reject_other_symbol(self):
        file=Path(__file__).resolve().parents[1]/'examples'/'candles_synthetic_4h.csv'
        with self.assertRaisesRegex(ValueError,'different symbol'):
            read_candles(file,'BTCUSDT','4h')

if __name__=='__main__':unittest.main()

class TimestampPrecisionTest(unittest.TestCase):
    def test_reject_microsecond_time_shift(self):
        data='timestamp,symbol,open,high,low,close,volume\n2026-01-01T00:00:00Z,DEMOUSDT,1,2,1,1,1\n2026-01-01T04:00:00.500Z,DEMOUSDT,1,2,1,1,1\n2026-01-01T08:00:00Z,DEMOUSDT,1,2,1,1,1\n'
        with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',suffix='.csv',delete=False) as f:
            f.write(data);path=f.name
        try:
            with self.assertRaisesRegex(ValueError,'not aligned'):
                read_candles(path,'DEMOUSDT','4h')
        finally:Path(path).unlink()

class ReproducibilityTest(unittest.TestCase):
    def test_hashes_and_replay_are_deterministic(self):
        bars=dataset([9,11,12,14],[10,12,13,15],[8,10,11,13],opens=[9,11,12,14])
        a=backtest(strat(),bars)
        b=backtest(strat(),bars)
        self.assertEqual(a,b)
        self.assertEqual(len(a['input_fingerprints']['strategy_sha256']),64)
        self.assertEqual(len(a['input_fingerprints']['candles_sha256']),64)
