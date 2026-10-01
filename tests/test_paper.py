import pytest

from heck_markets.engine.paper import PaperBroker


def test_buy_deducts_cash_and_opens_position():
    b = PaperBroker(cash=100.0)
    pos = b.buy("kalshi", "MKT-1", "yes", contracts=10, price=0.40)
    assert b.cash == pytest.approx(96.0)
    assert pos.contracts == 10
    assert pos.avg_price == pytest.approx(0.40)


def test_buy_averages_into_existing():
    b = PaperBroker(cash=100.0)
    b.buy("kalshi", "MKT-1", "yes", 10, 0.40)
    pos = b.buy("kalshi", "MKT-1", "yes", 10, 0.60)
    assert pos.contracts == 20
    assert pos.avg_price == pytest.approx(0.50)


def test_buy_insufficient_cash():
    b = PaperBroker(cash=1.0)
    with pytest.raises(ValueError, match="insufficient cash"):
        b.buy("kalshi", "MKT-1", "yes", 10, 0.50)


def test_sell_returns_proceeds_and_closes():
    b = PaperBroker(cash=100.0)
    b.buy("kalshi", "MKT-1", "yes", 10, 0.40)
    proceeds = b.sell("kalshi", "MKT-1", "yes", 10, 0.55)
    assert proceeds == pytest.approx(5.5)
    assert not b.positions


def test_mark_to_market_unrealized_pnl():
    b = PaperBroker(cash=100.0)
    b.buy("kalshi", "MKT-1", "yes", 10, 0.40)
    key = "kalshi:MKT-1:yes"
    out = b.mark_to_market({key: 0.60})
    assert out["unrealized_pnl"] == pytest.approx(2.0)
    assert out["equity"] == pytest.approx(96.0 + 6.0)
