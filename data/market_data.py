from __future__ import annotations
import time, logging
log=logging.getLogger(__name__)
class RESTMarketData:
    def __init__(self,exchange,symbol,db=None,interval_s=1.0): self.exchange=exchange; self.symbol=symbol; self.db=db; self.interval_s=interval_s
    def snapshot(self):
        ts=int(time.time()*1000)
        ob=self.exchange.orderbook(self.symbol)
        tr=self.exchange.trades(self.symbol)
        snap={"ts_ms":ts,"orderbook":ob,"trades":tr}
        if self.db: self.db.log_event(ts,"market_snapshot",self.symbol,snap)
        return snap
    def run(self,handler,stop_flag):
        while not stop_flag():
            started=time.perf_counter()
            try: handler(self.snapshot())
            except Exception as e: log.exception("market snapshot failed: %s",e)
            time.sleep(max(0,self.interval_s-(time.perf_counter()-started)))
