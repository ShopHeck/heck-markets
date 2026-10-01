import argparse

from heck_markets.config import get_settings
from heck_markets.venues import KalshiClient, PolymarketClient


def _fmt_price(p: float | None) -> str:
    return f"{p * 100:.0f}¢" if p is not None else "—"


def cmd_markets(args: argparse.Namespace) -> int:
    settings = get_settings()
    clients = {
        "kalshi": KalshiClient,
        "polymarket": PolymarketClient,
    }
    venues = [args.venue] if args.venue != "all" else list(clients)
    for venue in venues:
        client = clients[venue](settings)
        print(f"\n== {venue.upper()} (top {args.limit} by 24h volume) ==")
        for m in client.list_markets(limit=args.limit):
            print(
                f"{_fmt_price(m.yes_bid):>5}/{_fmt_price(m.yes_ask):<5} "
                f"vol {m.volume_24h:>10,.0f}  {m.title[:80]}"
            )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="heck-markets")
    sub = parser.add_subparsers(dest="command", required=True)

    p_markets = sub.add_parser("markets", help="list top markets by 24h volume")
    p_markets.add_argument(
        "--venue", choices=["kalshi", "polymarket", "all"], default="all"
    )
    p_markets.add_argument("--limit", type=int, default=20)
    p_markets.set_defaults(func=cmd_markets)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
