from __future__ import annotations
import math,numpy as np,pandas as pd

def metrics(trades,equity_curve):
    out={}; n=len(trades); wins=trades[trades.pnl>0] if n else trades; losses=trades[trades.pnl<=0] if n else trades
    out['trades']=n; out['win_rate']=len(wins)/n if n else 0
    aw=float(wins.pnl.mean()) if len(wins) else 0; al=float(-losses.pnl.mean()) if len(losses) else 0
    out['avg_win']=aw; out['avg_loss']=al; out['expectancy']=float(trades.pnl.mean()) if n else 0
    gross_profit=float(wins.pnl.sum()) if n else 0; gross_loss=float(-losses.pnl.sum()) if n else 0
    out['profit_factor']=gross_profit/gross_loss if gross_loss else float('inf')
    if len(equity_curve)>1:
        r=equity_curve.pct_change().replace([np.inf,-np.inf],np.nan).dropna(); out['sharpe']=float((r.mean()/r.std())*math.sqrt(len(r))) if r.std()>0 else 0
        downside=r[r<0]; out['sortino']=float((r.mean()/downside.std())*math.sqrt(len(r))) if len(downside)>1 and downside.std()>0 else 0
        peak=equity_curve.cummax(); dd=(equity_curve/peak-1); out['max_drawdown']=float(dd.min())
    else: out.update({'sharpe':0,'sortino':0,'max_drawdown':0})
    out['max_consecutive_losses']=_max_streak(trades.pnl.tolist() if n else [], lambda x:x<=0)
    return out

def _max_streak(a,pred):
    best=cur=0
    for x in a:
        cur=cur+1 if pred(x) else 0; best=max(best,cur)
    return best
