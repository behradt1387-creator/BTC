from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

@dataclass
class MarketSpec:
    symbol: str
    raw: dict[str, Any]
    min_size: float | None = None
    min_notional: float | None = None
    tick_size: float | None = None
    qty_step: float | None = None
    min_leverage: int | None = None
    max_leverage: int | None = None
    maker_fee: float | None = None
    taker_fee: float | None = None
    maintenance_margin_rate: float | None = None

class ExchangeAdapter(ABC):
    @abstractmethod
    def markets(self) -> list[dict[str, Any]]: ...
    @abstractmethod
    def orderbook(self, symbol: str, precision: str | None = None) -> dict[str, Any]: ...
    @abstractmethod
    def trades(self, symbol: str) -> dict[str, Any] | list[Any]: ...
    @abstractmethod
    def funding_history(self, symbol: str, page: int = 1, start: str | None = None, end: str | None = None) -> Any: ...
    @abstractmethod
    def balances(self) -> Any: ...
    @abstractmethod
    def positions(self, symbol: str | None = None, active: bool | None = None) -> Any: ...
    @abstractmethod
    def orders(self, symbol: str | None = None, active: bool | None = None) -> Any: ...
    @abstractmethod
    def open_position(self, payload: dict[str, Any]) -> dict[str, Any]: ...
    @abstractmethod
    def close_position(self, position_id: str | int, payload: dict[str, Any]) -> dict[str, Any]: ...
    @abstractmethod
    def close_all_positions(self) -> Any: ...
    @abstractmethod
    def set_tpsl(self, position_id: str | int, payload: dict[str, Any]) -> Any: ...
    @abstractmethod
    def cancel_order(self, order_id: str | int) -> Any: ...
    @abstractmethod
    def cancel_all_orders(self, order_types: list[str] | None = None) -> Any: ...

    def websocket(self, *args, **kwargs):
        raise NotImplementedError("No WebSocket contract was present in the supplied TrueTrade API guide. A protocol-specific adapter must be added from official WS documentation.")
