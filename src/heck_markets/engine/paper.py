from dataclasses import dataclass, field


@dataclass
class Position:
    venue: str
    market_id: str
    side: str  # "yes" | "no"
    contracts: float
    avg_price: float  # dollars paid per contract, 0-1


@dataclass
class PaperBroker:
    cash: float = 10_000.0
    positions: dict[str, Position] = field(default_factory=dict)

    def _key(self, venue: str, market_id: str, side: str) -> str:
        return f"{venue}:{market_id}:{side}"

    def buy(
        self, venue: str, market_id: str, side: str, contracts: float, price: float
    ) -> Position:
        cost = contracts * price
        if cost > self.cash:
            raise ValueError(f"insufficient cash: need {cost:.2f}, have {self.cash:.2f}")
        self.cash -= cost
        key = self._key(venue, market_id, side)
        existing = self.positions.get(key)
        if existing:
            total = existing.contracts + contracts
            existing.avg_price = (
                existing.avg_price * existing.contracts + price * contracts
            ) / total
            existing.contracts = total
            return existing
        pos = Position(venue=venue, market_id=market_id, side=side,
                       contracts=contracts, avg_price=price)
        self.positions[key] = pos
        return pos

    def sell(self, venue: str, market_id: str, side: str, contracts: float, price: float) -> float:
        key = self._key(venue, market_id, side)
        pos = self.positions.get(key)
        if not pos or contracts > pos.contracts:
            raise ValueError("insufficient position to sell")
        proceeds = contracts * price
        self.cash += proceeds
        pos.contracts -= contracts
        if pos.contracts == 0:
            del self.positions[key]
        return proceeds

    def mark_to_market(self, prices: dict[str, float]) -> dict[str, float]:
        """prices maps position key -> current YES price (dollars)."""
        unrealized = 0.0
        for key, pos in self.positions.items():
            yes_price = prices.get(key)
            if yes_price is None:
                continue
            current = yes_price if pos.side == "yes" else 1 - yes_price
            unrealized += (current - pos.avg_price) * pos.contracts
        equity = self.cash + sum(
            (prices.get(k, p.avg_price if p.side == "yes" else 1 - p.avg_price)
             if p.side == "yes" else 1 - prices.get(k, 1 - p.avg_price))
            * p.contracts
            for k, p in self.positions.items()
        )
        return {"cash": self.cash, "unrealized_pnl": unrealized, "equity": equity}
