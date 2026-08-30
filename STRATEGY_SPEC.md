# Strategy specification

## Core idea
Trade only when short-horizon order-flow and microprice information imply enough expected movement to overcome fees, slippage, adverse selection and spread.

## Features
- `OBI_L = (BidVol_L - AskVol_L)/(BidVol_L + AskVol_L)` for L=1,2,3,5,10,20.
- `MicroPrice = (Ask*BidSize + Bid*AskSize)/(BidSize+AskSize)`.
- `MicroMinusMidBps = (MicroPrice-Mid)/Mid * 10,000`.
- trade-flow imbalance = `(buy_qty-sell_qty)/(buy_qty+sell_qty)` over a rolling short window.
- spread_bps, near-mid depth, short returns and realized volatility.

## Signal
Probability of TP before SL is preferred. When no trained model exists, the code's logistic-like baseline is only a placeholder prior and not an empirical claim.

## Execution
Passive limit orders are preferred only when fill probability remains high enough and adverse-selection conditions are benign. Aggressive execution is used when immediate edge dominates waiting value.

## Stops
TP/SL are adaptive to recent realized volatility. Exact optimal distances must be learned from OOS data.

## Position sizing
Risk per trade is a fraction of equity. Exposure is capped. No martingale.
