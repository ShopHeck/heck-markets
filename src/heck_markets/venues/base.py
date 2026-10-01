from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol


@dataclass
class Market:
    venue: str
    market_id: str
    title: str
    yes_bid: float | None = None  # dollars, 0-1
    yes_ask: float | None = None
    volume_24h: float = 0.0
    close_time: datetime | None = None
    active: bool = True
    raw: dict = field(default_factory=dict, repr=False)


@dataclass
class PriceLevel:
    price: float  # dollars, 0-1
    size: float   # contracts


@dataclass
class OrderBook:
    market_id: str
    yes_bids: list[PriceLevel]
    yes_asks: list[PriceLevel]


class VenueClient(Protocol):
    venue: str

    def list_markets(self, limit: int = 20) -> list[Market]: ...

    def get_orderbook(self, market_id: str) -> OrderBook: ...
