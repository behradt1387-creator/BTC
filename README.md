# BTC Microstructure / HFT Research System for TrueTrade

This repository is deliberately **evidence-first**. It implements the documented TrueTrade REST contract, an event-driven feature/simulation stack, risk controls, paper mode, logging, Monte Carlo, and deployment scaffolding. It does **not** invent a TrueTrade WebSocket protocol or undocumented trading fields.

## Important exchange limitation
The supplied TrueTrade API guide documents signed REST routes, including `/futures/markets`, `/futures/markets/orderbook`, `/futures/markets/trades`, funding history, balances, positions, orders, position open/close, TP/SL and cancellation. It does not document a WebSocket protocol, tick-size/minimum-size responses, maker/taker fee schedule, maintenance-margin formula, liquidation formula, or finalized rate limits. The code therefore refuses to treat those facts as known.

## Modes
`MODE=backtest`, `paper`, `live`; default `paper`. Live additionally requires `ALLOW_LIVE=true` and `ALLOW_REST_LIVE=true` because the supplied contract has no documented WS adapter.

## Install
```bash
sudo apt update && sudo apt -y upgrade
sudo apt -y install python3 python3-venv python3-pip git
sudo mkdir -p /root/btc-hft-bot && sudo chown -R $USER:$USER /root/btc-hft-bot
cd /root/btc-hft-bot
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
chmod 600 .env
```

## Run tests
```bash
venv/bin/python -m pytest -q
```

## Paper trading
Populate `.env` with the TrueTrade API key and secret, leave `MODE=paper`, then:
```bash
venv/bin/python main.py
```

## Dashboard
```bash
venv/bin/streamlit run monitoring/dashboard.py --server.address 127.0.0.1
```

## Systemd
Copy `systemd/btc-hft-bot.service` to `/etc/systemd/system/`, adjust the WorkingDirectory if necessary, then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable btc-hft-bot
sudo systemctl start btc-hft-bot
sudo systemctl status btc-hft-bot
sudo journalctl -u btc-hft-bot -f
```
Stop/restart:
```bash
sudo systemctl stop btc-hft-bot
sudo systemctl restart btc-hft-bot
```

## Emergency shutdown
```bash
sudo systemctl stop btc-hft-bot
```
For an account-level emergency, only after verifying the account state, use the documented `/futures/positions/close-all` and `/futures/orders/close-all` routes through a trusted operator script. Do not paste secrets into shell history or chat.

## Virtual environments
Create: `python3 -m venv venv`
Activate: `source venv/bin/activate`
Deactivate: `deactivate`
Install: `python -m pip install -r requirements.txt`
Run without activating: `venv/bin/python main.py`
Repair by deleting and recreating `venv/`, then reinstalling `requirements.txt`.

## Data collection limitation
The TrueTrade guide provides recent trades and snapshots via REST and historical klines/funding, but not a documented historical depth/event archive. For real microstructure research, collect and persist order-book/trade snapshots first. The supplied API is insufficient by itself to reconstruct a faithful years-long tick/order-book backtest.
