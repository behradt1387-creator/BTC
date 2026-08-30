# BTC Perpetual Futures Quant/HFT System — Research & Validation Report

## Executive conclusion
No statistically defensible $15→$1,000 probability is reported here, because the supplied exchange material does not contain the historical event-level BTC order-book/trade dataset or the complete economic rules required to validate such a number. Producing a numerical probability would be fabricated.

The strongest defensible implementation at this stage is an **order-flow/microstructure continuation strategy with explicit cost and execution gates**, coupled to a recorder that turns TrueTrade's live REST snapshots into the dataset needed for strict out-of-sample research. It is a research/paper system, not a claim of profitability.

## Phase 1 — TrueTrade integration audit
### Confirmed from supplied guide
- REST base: `https://apiv2.thetruetrade.io`; futures routes under `/futures`.
- Required signed headers: `X-API-Key`, `X-Timestamp` in milliseconds, `X-Signature`, and JSON content type for JSON bodies.
- Signature: HMAC-SHA256 over `{timestamp}{METHOD}{uri}`, uppercase method, including query string, never including the body.
- Timestamp acceptance window: 30 seconds.
- Futures permission: `api-keys.trade-futures`, which covers the entire `/futures` group and combines read/write access.
- Market endpoints: markets, 24h stats, orderbook, recent trades, funding history, klines, quote rates.
- Account endpoints: futures assets, PnL, positions, orders, trade history.
- Trading endpoints: open position, close position, close-all positions, set/update TP/SL, add margin, cancel order, close-all orders.

### Confirmed unknowns / blockers
- No WebSocket protocol or subscription schema is documented in the supplied guide.
- Exact API rate limits are explicitly stated as not yet finalized.
- The guide does not state BTC minimum size/notional, tick size, quantity step, maintenance margin rate, liquidation formula, or maker/taker fee schedule.
- The guide does not document client order IDs/idempotency primitives.
- Historical event-level order-book/trade data is not documented; only recent trades and historical candles/funding are documented.

The implementation therefore uses REST signatures exactly as documented and refuses to assume the missing exchange facts.

## Phase 2 — Strategy research
The research direction is microstructure rather than indicator crossover:
1. Order-book imbalance across L1/L2/L3/L5/L10/L20.
2. Microprice relative to mid-price and spread.
3. Short-horizon returns over 100ms–10s where data permits.
4. Aggressive trade-flow imbalance.
5. Depth and spread regime filters.
6. Realized short-horizon volatility.
7. Adverse-selection and fill priors for passive orders.
8. Hybrid continuation/mean-reversion selection by net edge.

External literature supports researching order-flow imbalance and queue effects: Cont, Kukanov & Stoikov find short-interval price changes are strongly related to order-flow imbalance and market depth; later work emphasizes queue position, imbalance and microprice for limit-order valuation. These are research motivations, not evidence that the same coefficients work on TrueTrade/BTC today.

## Phase 3 — $15 viability
A $15 account is only technically viable if the actual BTCUSDT market rules allow a sufficiently small order after margin, leverage, precision and fees. The supplied guide does not provide these values. Therefore the code performs market-spec discovery through `/futures/markets` but does not fabricate a pass/fail conclusion.

The economics are especially sensitive at $15 because fixed minimum notional and fee/slippage floors can consume a large fraction of each trade's expected edge.

## Phase 4–6 — Data, features, event-driven backtester
The system records raw snapshots and derived features. The backtester is event-driven over these recorded events rather than OHLC-only. It models spread, taker fees, slippage, holding time, and signal-driven TP/SL. Queue position and true partial-fill reconstruction remain unavailable until a genuine event-level feed is recorded or supplied.

## Phase 7–10 — Baselines, ML, OOS validation
Implemented baselines:
- transparent logistic model;
- random forest option;
- rule-based microstructure prior for bootstrapping only.

ML labels should be defined on actual trade outcomes: TP first / SL first / timeout, not next-candle direction. `scripts/train.py` performs chronological train/test separation. The final untouched test set must only be used once for the final report.

No model performance is claimed because no suitable labeled TrueTrade event dataset was supplied.

## Phase 11 — Monte Carlo
`backtest/monte_carlo.py` runs 10,000 bootstrap simulations by default and perturbs sequence and slippage. It must be fed empirical out-of-sample trade returns. It does not create evidence on its own.

## Phase 12–16 — Execution, risk, paper
Execution is modular. The TrueTrade adapter uses documented routes. Position sizing is fractional-risk-based; martingale and loss-doubling are absent. Kill-state blocks trading. Paper mode is the default.

## Phase 17–20 — Deployment and scaling
Systemd is provided with automatic restart. Restart does not bypass the strategy's internal kill-state logic. On process restart, production logic must reconcile balances, positions and active orders before resuming. Because client order IDs are not documented, the code uses pre-submit state reconciliation rather than pretending full idempotency is available.

## Mathematical framework
For a trade with win probability p, average win W, average loss L, fees F and slippage S:

`EV = p*W - (1-p)*L - F - S`

For a strategy, the decision rule is based on positive **net** edge after costs, plus probability and market-quality gates. Geometric growth is evaluated through the path of equity, not win rate alone.

## 90/92/95/97/99% win-rate configurations
These are not valid outputs until paired with empirically supported win/loss magnitudes and costs. A 99% win rate with sufficiently large rare losses can have negative geometric growth. The code therefore does not backfill these configurations with hypothetical numbers.

## Capital-growth table
| Starting | Target | Probability | Median Time | 5th Percentile Time | Risk of Ruin |
|---:|---:|---:|---:|---:|---:|
| $15 | $25 | N/A | N/A | N/A | N/A |
| $15 | $50 | N/A | N/A | N/A | N/A |
| $15 | $100 | N/A | N/A | N/A | N/A |
| $15 | $250 | N/A | N/A | N/A | N/A |
| $15 | $500 | N/A | N/A | N/A | N/A |
| $15 | $1,000 | N/A | N/A | N/A | N/A |

N/A is deliberate: no valid OOS trade sample from TrueTrade was supplied.

## Worst case
The practical worst case is a sequence of losses combined with fee/slippage drag, API disconnection, stale data, or an order-state mismatch. The kill switch and state reconciliation are designed to fail closed, but no software layer can guarantee against exchange-side failures.

## Best case
A persistent microstructure edge could produce positive expectancy and geometric growth, but its magnitude, capacity and persistence are empirical questions. No claim is made that such an edge exists on TrueTrade.

## Required evidence before live scaling
1. Multi-week event-level TrueTrade capture.
2. Verified market-spec payload for BTCUSDT.
3. Verified actual fee schedule and funding treatment.
4. Measured REST/WS latency and fill outcomes.
5. Chronological train/validation/test with untouched OOS period.
6. 10,000+ Monte Carlo simulations fed by OOS trade outcomes.
7. Paper trading showing agreement between expected and realized fills.
8. Crash/reboot and ambiguous-response tests.
9. Only then consider small live exposure.

## Final answer to the central question
**At this stage the probability that the system can grow $15 into $1,000 is not statistically estimable from the supplied evidence.** Any percentage would be made up. The implementation's purpose is to collect the missing evidence and produce that probability once the required OOS data and economic parameters exist.
