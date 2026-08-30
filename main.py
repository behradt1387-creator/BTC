from __future__ import annotations
import logging,signal,time
from config.settings import Settings
from exchange.truetrade import TrueTradeAdapter
from data.market_data import RESTMarketData
from features.features import FeatureEngine
from strategy.strategy import MicrostructureStrategy
from execution.execution import ExecutionEngine
from risk.risk import RiskEngine
from risk.kill_switch import KillSwitch
from storage.database import Database

logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(name)s %(message)s')
log=logging.getLogger('main')
stop=False

def main():
    global stop
    cfg=Settings(); cfg.validate()
    db=Database(cfg.db_path); kill=KillSwitch(); risk=RiskEngine(cfg); fe=FeatureEngine()
    ex=TrueTradeAdapter(cfg.api_key,cfg.api_secret,cfg.rest_base_url,cfg.request_timeout_s) if cfg.api_key and cfg.api_secret else None
    if cfg.mode=='live' and ex is None: raise RuntimeError('Live mode requires credentials')
    strat=MicrostructureStrategy(cfg); exe=ExecutionEngine(cfg,ex)
    if ex:
        try:
            spec=ex.discover_btc_spec(); db.log_event(int(time.time()*1000),'market_spec',cfg.symbol,spec); log.warning('BTC market spec discovery: %s',spec)
            if not spec.get('found'): kill.trigger('BTCUSDT market spec unavailable'); log.critical('No BTCUSDT market specification; trading blocked')
        except Exception as e:
            kill.trigger(f'market spec error: {e}'); db.log_error('startup',str(e),int(time.time()*1000)); log.exception('startup exchange check failed')
    def handler(s):
        ts=s['ts_ms']
        try:
            f=fe.update(ts,s['orderbook'],s['trades']); db.log_event(ts,'features',cfg.symbol,f)
            if ts-int(time.time()*1000) < -cfg.stale_data_ms: kill.trigger('stale data')
            if not kill.check(): return
            sig=strat.decide(f)
            if not sig: return
            mark=f['mid']; rd=risk.check(cfg.initial_capital,mark,sig.sl_bps,sig.side)
            if not rd.allowed: return
            tp=mark*(1+sig.tp_bps/10000 if sig.side=='LONG' else 1-sig.tp_bps/10000)
            sl=mark*(1-sig.sl_bps/10000 if sig.side=='LONG' else 1+sig.sl_bps/10000)
            from execution.orders import OrderIntent
            intent=OrderIntent(sig.side,'LIMIT' if sig.passive else 'MARKET',rd.quantity,mark if sig.passive else None,rd.leverage,tp,sl)
            if cfg.mode=='live':
                # Duplicate protection uses state re-sync before opening because clientOrderId is not documented.
                ex.positions(symbol=cfg.symbol,active=True); ex.orders(symbol=cfg.symbol,active=True)
            result=exe.open(intent); db.log_event(ts,'order_intent',cfg.symbol,{'signal':sig.__dict__,'risk':rd.__dict__,'result':result})
        except Exception as e:
            db.log_error('handler',str(e),ts); log.exception('handler error'); kill.trigger(f'handler exception: {e}')
    for sig in (signal.SIGINT,signal.SIGTERM): signal.signal(sig,lambda *_:globals().__setitem__('stop',True))
    if kill.active: log.critical('Bot starts in kill state: %s',kill.reason)
    else: log.info('Starting %s mode for %s',cfg.mode,cfg.symbol)
    # Supplied TrueTrade guide does not document a websocket; this is polling research/paper mode, not true HFT transport.
    if ex is None: raise RuntimeError('No TrueTrade credentials configured; paper mode still requires signed market-data access per supplied guide.')
    RESTMarketData(ex,cfg.symbol,db,cfg.market_poll_interval_s).run(handler,lambda:stop)

if __name__=='__main__': main()
