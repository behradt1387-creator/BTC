from __future__ import annotations
import math,random
from dataclasses import dataclass
import pandas as pd
from strategy.strategy import MicrostructureStrategy

@dataclass
class BacktestResult:
    equity_curve: pd.Series
    trades: pd.DataFrame

class EventBacktester:
    def __init__(self,cfg,strategy): self.cfg=cfg; self.strategy=strategy
    def run(self,events,initial_capital=15.0):
        equity=initial_capital; curve=[]; trades=[]; pos=None
        for e in events:
            ts=e["ts_ms"]; f=e["features"]; mid=f["mid"]
            if pos:
                move=(mid/pos["entry"]-1)*10000*(1 if pos["side"]=="LONG" else -1)
                held=(ts-pos["ts"])/1000
                if move>=pos["tp"] or move<=-pos["sl"] or held>=self.cfg.max_hold_seconds:
                    exit_px=mid
                    gross=(exit_px-pos["entry"])*pos["qty"]*(1 if pos["side"]=="LONG" else -1)
                    notional_in=pos["entry"]*pos["qty"]
                    fee=notional_in*self.cfg.taker_fee_rate + exit_px*pos["qty"]*self.cfg.taker_fee_rate
                    slip=(notional_in+exit_px*pos["qty"])*self.cfg.assumed_slippage_bps/10000
                    pnl=gross-fee-slip; equity+=pnl
                    trades.append({"ts_ms":pos["ts"],"side":pos["side"],"entry":pos["entry"],"exit":exit_px,"qty":pos["qty"],"pnl":pnl,"fees":fee,"slippage":slip,"holding_s":held,"prob":pos["prob"],"ev_bps":pos["ev"]})
                    pos=None
            if pos is None:
                sig=self.strategy.decide(f)
                if sig:
                    qty=(equity*self.cfg.risk_per_trade)/(max(sig.sl_bps,1)/10000)/mid
                    max_notional=equity*self.cfg.max_exposure_fraction*self.cfg.default_leverage
                    qty=min(qty,max_notional/mid)
                    pos={"ts":ts,"side":sig.side,"entry":mid,"qty":qty,"tp":sig.tp_bps,"sl":sig.sl_bps,"prob":sig.probability,"ev":sig.net_edge_bps}
            curve.append((ts,equity))
        return BacktestResult(pd.Series({t:v for t,v in curve}),pd.DataFrame(trades))
