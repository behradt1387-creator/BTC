from __future__ import annotations
import hashlib, hmac, json, logging, time
from typing import Any
from urllib.parse import urlencode
import requests
from .base import ExchangeAdapter

log = logging.getLogger(__name__)

class TrueTradeAPIError(RuntimeError):
    def __init__(self, status: int, payload: Any):
        self.status = status
        self.payload = payload
        super().__init__(f"TrueTrade HTTP {status}: {payload}")

class TrueTradeAdapter(ExchangeAdapter):
    """TrueTrade REST adapter using only routes documented in the supplied guide.

    Signing is timestamp + METHOD + URI; body is explicitly excluded.
    """
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://apiv2.thetruetrade.io", timeout: float = 8.0):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _signed_headers(self, method: str, uri: str) -> dict[str, str]:
        ts = str(int(time.time() * 1000))
        payload = f"{ts}{method.upper()}{uri}"
        sig = hmac.new(self.api_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return {"X-API-Key": self.api_key, "X-Timestamp": ts, "X-Signature": sig, "Content-Type": "application/json"}

    def _request(self, method: str, path: str, params: dict[str, Any] | None = None, body: dict[str, Any] | None = None, allow_429_retry: bool = True) -> Any:
        query = urlencode([(k, str(v).lower() if isinstance(v, bool) else str(v)) for k, v in (params or {}).items() if v is not None], doseq=True)
        uri = path + (f"?{query}" if query else "")
        headers = self._signed_headers(method, uri) if self.api_key and self.api_secret else {"Content-Type": "application/json"}
        url = self.base_url + uri
        started = time.perf_counter()
        resp = self.session.request(method.upper(), url, params=None, json=body, headers=headers, timeout=self.timeout)
        elapsed_ms = (time.perf_counter() - started) * 1000
        if resp.status_code == 429 and allow_429_retry:
            time.sleep(min(2.0, 0.25 + elapsed_ms / 1000))
            return self._request(method, path, params, body, allow_429_retry=False)
        try:
            data = resp.json()
        except Exception:
            data = resp.text
        if not resp.ok:
            raise TrueTradeAPIError(resp.status_code, data)
        return data

    def markets(self): return self._request("GET", "/futures/markets")
    def orderbook(self, symbol, precision=None): return self._request("GET", "/futures/markets/orderbook", {"symbol": symbol, "precision": precision})
    def trades(self, symbol): return self._request("GET", "/futures/markets/trades", {"symbol": symbol})
    def funding_history(self, symbol, page=1, start=None, end=None): return self._request("GET", "/futures/markets/funding-history", {"symbol": symbol, "page": page, "start": start, "end": end})
    def candle_history(self, symbol, resolution, start_s, end_s, countback):
        return self._request("GET", "/futures/udf/history", {"symbol": symbol, "resolution": resolution, "from": start_s, "to": end_s, "countback": countback})
    def quote_rates(self): return self._request("GET", "/futures/quote-rates")
    def balances(self): return self._request("GET", "/futures/assets")
    def accounting_assets(self): return self._request("GET", "/accounting/assets")
    def pnl_history(self): return self._request("GET", "/futures/assets/pnl")
    def positions(self, symbol=None, active=None): return self._request("GET", "/futures/positions", {"symbol": symbol, "active": active})
    def orders(self, symbol=None, active=None, order_type=None, side=None, direction=None, status=None):
        return self._request("GET", "/futures/orders", {"symbol": symbol, "active": active, "type": order_type, "side": side, "direction": direction, "status": status})
    def trades_history(self, **params): return self._request("GET", "/futures/trades", params)

    def open_position(self, payload): return self._request("POST", "/futures/positions", body=payload)
    def close_position(self, position_id, payload): return self._request("POST", f"/futures/positions/{position_id}/close", body=payload)
    def close_all_positions(self): return self._request("POST", "/futures/positions/close-all")
    def set_tpsl(self, position_id, payload): return self._request("PATCH", f"/futures/positions/{position_id}/tpsl", body=payload)
    def add_margin(self, position_id, amount): return self._request("PATCH", f"/futures/positions/{position_id}/add-margin", body={"amount": str(amount)})
    def cancel_order(self, order_id): return self._request("DELETE", f"/futures/orders/{order_id}")
    def cancel_all_orders(self, order_types=None): return self._request("POST", "/futures/orders/close-all", body={"type": order_types} if order_types else None)

    def discover_btc_spec(self) -> dict[str, Any]:
        markets = self.markets()
        if isinstance(markets, dict):
            items = markets.get("data") or markets.get("markets") or markets.get("result") or []
        else:
            items = markets
        if not isinstance(items, list):
            return {"raw": markets, "found": False}
        for item in items:
            if isinstance(item, dict) and str(item.get("symbol", "")).upper() == "BTCUSDT":
                return {"raw": item, "found": True}
        return {"raw": markets, "found": False}
