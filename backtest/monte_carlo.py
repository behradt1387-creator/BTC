from __future__ import annotations
import numpy as np

def simulate_trade_bootstrap(returns, start=15.0, n=10000, fee_noise=0.0, slippage_mult=(0.5,2.0), seed=7, milestones=(25,50,100,250,500,1000)):
    rng=np.random.default_rng(seed); ret=np.asarray(returns,dtype=float); ret=ret[np.isfinite(ret)]
    if len(ret)==0: raise ValueError('No trade returns')
    ends=[]; mdd=[]; reached={m:0 for m in milestones}; times={m:[] for m in milestones}
    for _ in range(n):
        idx=rng.integers(0,len(ret),size=max(1000,len(ret)*5)); eq=start; peak=start; worst=0; hit={m:None for m in milestones}
        for t,i in enumerate(idx):
            x=ret[i]
            slip=rng.uniform(*slippage_mult)
            noise=rng.normal(0,fee_noise)
            eq=max(0.0,eq*(1+x*slip)+noise)
            peak=max(peak,eq); worst=min(worst,eq/peak-1 if peak else -1)
            for m in milestones:
                if hit[m] is None and eq>=m: hit[m]=t+1
            if eq<=start*0.1: break
        ends.append(eq); mdd.append(worst)
        for m,h in hit.items():
            if h is not None: reached[m]+=1; times[m].append(h)
    return {"ending_capital_percentiles":dict(zip([5,25,50,75,95],np.percentile(ends,[5,25,50,75,95]))),"max_drawdown_percentiles":dict(zip([5,25,50,75,95],np.percentile(mdd,[5,25,50,75,95]))),"probability_reach":{m:reached[m]/n for m in milestones},"median_trade_count_to_milestone":{m:(float(np.median(times[m])) if times[m] else None) for m in milestones}}
