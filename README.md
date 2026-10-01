# heck-markets

Prediction-market trading bot for **Kalshi** and **Polymarket**, in Python.

Scaffold status: read-only market data clients + a paper-trading engine + CLI.
**Live order placement is intentionally not implemented** — wire it up only behind
explicit approval, and keep `TRADING_MODE=paper` until then.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env   # fill in credentials, or use real env vars / Devin secrets
```

## Credentials

Read-only market data works with no credentials at all. Signed Kalshi endpoints
(account, orders) need:

- `KALSHI_KEY_ID` — key ID (UUID) from the Kalshi dashboard
- `KALSHI_PRIVATE_KEY` — the RSA private key PEM **contents** (paste the whole
  `-----BEGIN PRIVATE KEY-----` block). `KALSHI_PRIVATE_KEY_PATH` works only for a
  file that exists on the machine — store the contents, not a path, in Devin secrets.

Polymarket authenticated trading (not yet wired) uses CLOB API creds
`POLYMARKET_KEY_ID`, `POLYMARKET_SECRET_KEY`, `POLYMARKET_PASSPHRASE`, plus the
wallet `POLYMARKET_PRIVATE_KEY` and `POLYMARKET_FUNDER_ADDRESS` for signing —
install with `pip install -e '.[polymarket]'`.

In Devin, these live as org secrets and are bound to shell commands on demand —
never commit them (`.env` and `keys/` are gitignored).

## Usage

```bash
# Top markets by 24h volume
heck-markets markets --venue kalshi --limit 10
heck-markets markets --venue polymarket --limit 10
```

## Layout

```
src/heck_markets/
  config.py            # pydantic-settings env config
  cli.py               # `heck-markets` entrypoint
  venues/
    base.py            # Market / OrderBook types + VenueClient protocol
    kalshi.py          # Kalshi API v2 client (RSA-PSS request signing)
    polymarket.py      # Polymarket Gamma API client (read-only)
  engine/
    paper.py           # PaperBroker: positions, cash, mark-to-market PnL
tests/
```

## Test & lint

```bash
pytest
ruff check src tests
```
