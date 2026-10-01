import time
from datetime import datetime

import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from heck_markets.config import Settings
from heck_markets.venues.base import Market, OrderBook, PriceLevel


class KalshiClient:
    """Kalshi API v2 client.

    Market data endpoints are public; signing is applied whenever credentials
    are configured so authed endpoints (portfolio, orders) work with no changes.
    """

    venue = "kalshi"

    def __init__(self, settings: Settings, client: httpx.Client | None = None):
        self._base = settings.kalshi_base_url.rstrip("/")
        self._key_id = settings.kalshi_key_id
        self._client = client or httpx.Client(timeout=15)
        pem = settings.kalshi_key_pem()
        self._rsa_key: rsa.RSAPrivateKey | None = (
            serialization.load_pem_private_key(pem, password=None) if pem else None
        )

    def _auth_headers(self, method: str, path: str) -> dict[str, str]:
        if not (self._key_id and self._rsa_key):
            return {}
        timestamp = str(int(time.time() * 1000))
        message = (timestamp + method.upper() + path).encode()
        signature = self._rsa_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.DIGEST_LENGTH,
            ),
            hashes.SHA256(),
        )
        import base64

        return {
            "KALSHI-ACCESS-KEY": self._key_id,
            "KALSHI-ACCESS-SIGNATURE": base64.b64encode(signature).decode(),
            "KALSHI-ACCESS-TIMESTAMP": timestamp,
        }

    def _get(self, path: str, params: dict | None = None) -> dict:
        resp = self._client.get(
            f"{self._base}{path}",
            params=params,
            headers=self._auth_headers("GET", f"/trade-api/v2{path}"),
        )
        resp.raise_for_status()
        return resp.json()

    def list_markets(self, limit: int = 20) -> list[Market]:
        data = self._get("/markets", params={"limit": min(limit, 100), "status": "open"})
        markets = [self._to_market(m) for m in data.get("markets", [])]
        markets.sort(key=lambda m: m.volume_24h, reverse=True)
        return markets[:limit]

    def get_orderbook(self, market_id: str) -> OrderBook:
        data = self._get(f"/markets/{market_id}/orderbook")
        book = data.get("orderbook", {})
        yes_bids = [
            PriceLevel(price=p / 100, size=s) for p, s in book.get("yes", [])
        ]
        # Kalshi returns only bids; asks are implied by NO bids at (1 - no_bid)
        no_bids = book.get("no", [])
        yes_asks = [
            PriceLevel(price=1 - p / 100, size=s) for p, s in reversed(no_bids)
        ]
        return OrderBook(market_id=market_id, yes_bids=yes_bids, yes_asks=yes_asks)

    @staticmethod
    def _to_market(raw: dict) -> Market:
        close = raw.get("close_time") or raw.get("expected_expiration_time")
        return Market(
            venue="kalshi",
            market_id=raw.get("ticker", ""),
            title=raw.get("title") or raw.get("subtitle") or raw.get("ticker", ""),
            yes_bid=(raw.get("yes_bid_dollars") or raw.get("yes_bid", 0) or 0)
            if isinstance(raw.get("yes_bid_dollars"), (int, float))
            else (raw.get("yes_bid", 0) or 0) / 100,
            yes_ask=(raw.get("yes_ask_dollars") or raw.get("yes_ask", 0) or 0)
            if isinstance(raw.get("yes_ask_dollars"), (int, float))
            else (raw.get("yes_ask", 0) or 0) / 100,
            volume_24h=float(raw.get("volume_24h", 0) or 0),
            close_time=datetime.fromisoformat(close.replace("Z", "+00:00")) if close else None,
            active=raw.get("status") == "open",
            raw=raw,
        )
