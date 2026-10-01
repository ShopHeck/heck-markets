import json
from datetime import datetime

import httpx

from heck_markets.config import Settings
from heck_markets.venues.base import Market, OrderBook


class PolymarketClient:
    """Polymarket client backed by the public Gamma API.

    Read-only: market discovery needs no credentials. Authenticated CLOB
    trading is out of scope for this scaffold (install the `polymarket`
    extra and wire py-clob-client when ready).
    """

    venue = "polymarket"

    def __init__(self, settings: Settings, client: httpx.Client | None = None):
        self._gamma = settings.polymarket_gamma_url.rstrip("/")
        self._client = client or httpx.Client(timeout=15)

    def list_markets(self, limit: int = 20) -> list[Market]:
        resp = self._client.get(
            f"{self._gamma}/markets",
            params={
                "active": "true",
                "closed": "false",
                "limit": min(limit, 100),
                "order": "volume24hr",
                "ascending": "false",
            },
        )
        resp.raise_for_status()
        return [self._to_market(m) for m in resp.json()][:limit]

    def get_orderbook(self, market_id: str) -> OrderBook:
        raise NotImplementedError(
            "Polymarket orderbook requires the CLOB API; install the "
            "'polymarket' extra and use py-clob-client"
        )

    @staticmethod
    def _to_market(raw: dict) -> Market:
        prices = raw.get("outcomePrices")
        if isinstance(prices, str):
            try:
                prices = json.loads(prices)
            except json.JSONDecodeError:
                prices = None
        yes_price = float(prices[0]) if prices else None
        close = raw.get("endDate") or raw.get("endDateIso")
        return Market(
            venue="polymarket",
            market_id=raw.get("conditionId") or raw.get("id", ""),
            title=raw.get("question") or raw.get("slug", ""),
            yes_bid=yes_price,
            yes_ask=yes_price,
            volume_24h=float(raw.get("volume24hr", 0) or 0),
            close_time=datetime.fromisoformat(close.replace("Z", "+00:00")) if close else None,
            active=raw.get("active", False) and not raw.get("closed", True),
            raw=raw,
        )
