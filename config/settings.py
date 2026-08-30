from __future__ import annotations
import os
from dataclasses import dataclass


def _bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "y", "on"}


def _float(name: str, default: float) -> float:
    v = os.getenv(name)
    return default if v is None or v == "" else float(v)


def _int(name: str, default: int) -> int:
    v = os.getenv(name)
    return default if v is None or v == "" else int(v)


@dataclass(frozen=True)
class Settings:
    mode: str = os.getenv("MODE", "paper").lower()
    symbol: str = os.getenv("SYMBOL", "BTCUSDT")
    api_key: str = os.getenv("TRUETRADE_API_KEY", "")
    api_secret: str = os.getenv("TRUETRADE_API_SECRET", "")
    rest_base_url: str = os.getenv("TRUETRADE_REST_BASE_URL", "https://apiv2.thetruetrade.io")
    request_timeout_s: float = _float("REQUEST_TIMEOUT_S", 8.0)
    market_poll_interval_s: float = _float("MARKET_POLL_INTERVAL_S", 1.0)
    stale_data_ms: int = _int("STALE_DATA_MS", 5000)

    initial_capital: float = _float("INITIAL_CAPITAL", 15.0)
    maker_fee_rate: float = _float("MAKER_FEE_RATE", 0.0)
    taker_fee_rate: float = _float("TAKER_FEE_RATE", 0.0)
    funding_rate_per_period: float = _float("FUNDING_RATE_PER_PERIOD", 0.0)
    assumed_slippage_bps: float = _float("ASSUMED_SLIPPAGE_BPS", 5.0)
    max_latency_ms: int = _int("MAX_LATENCY_MS", 1500)

    risk_per_trade: float = _float("RISK_PER_TRADE", 0.01)
    max_daily_loss: float = _float("MAX_DAILY_LOSS", 0.05)
    max_consecutive_losses: int = _int("MAX_CONSECUTIVE_LOSSES", 5)
    max_leverage: int = _int("MAX_LEVERAGE", 5)
    default_leverage: int = _int("DEFAULT_LEVERAGE", 2)
    max_exposure_fraction: float = _float("MAX_EXPOSURE_FRACTION", 0.25)
    min_signal_probability: float = _float("MIN_SIGNAL_PROBABILITY", 0.58)
    min_net_edge_bps: float = _float("MIN_NET_EDGE_BPS", 2.0)
    max_spread_bps: float = _float("MAX_SPREAD_BPS", 8.0)
    max_realized_vol_1s: float = _float("MAX_REALIZED_VOL_1S", 0.02)
    min_depth_quote: float = _float("MIN_DEPTH_QUOTE", 10.0)
    max_hold_seconds: int = _int("MAX_HOLD_SECONDS", 10)

    # Live trading is intentionally opt-in and REST-only unless a documented WS adapter is added.
    allow_live: bool = _bool("ALLOW_LIVE", False)
    allow_rest_live: bool = _bool("ALLOW_REST_LIVE", False)

    db_path: str = os.getenv("DB_PATH", "data/btc_hft.db")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    def validate(self) -> None:
        if self.mode not in {"backtest", "paper", "live"}:
            raise ValueError("MODE must be backtest, paper, or live")
        if self.mode == "live" and not self.allow_live:
            raise RuntimeError("Live mode blocked: set ALLOW_LIVE=true only after validation.")
        if self.mode == "live" and not self.allow_rest_live:
            raise RuntimeError("Live mode blocked: supplied TrueTrade guide documents REST only; set ALLOW_REST_LIVE=true only after accepting that limitation.")
        if not (0 < self.risk_per_trade <= 0.05):
            raise ValueError("RISK_PER_TRADE must be in (0, 0.05]")
        if self.default_leverage < 1 or self.default_leverage > self.max_leverage:
            raise ValueError("Invalid leverage settings")
