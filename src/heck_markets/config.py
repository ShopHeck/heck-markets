from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    trading_mode: str = "paper"

    kalshi_key_id: str | None = None
    kalshi_private_key_path: Path | None = None
    kalshi_private_key: str | None = None
    kalshi_base_url: str = "https://api.elections.kalshi.com/trade-api/v2"

    # Polymarket CLOB API credentials (created on polymarket.com)
    polymarket_key_id: str | None = None
    polymarket_secret_key: str | None = None
    polymarket_passphrase: str | None = None
    # Wallet credentials for signing orders (L1)
    polymarket_private_key: str | None = None
    polymarket_funder_address: str | None = None
    polymarket_gamma_url: str = "https://gamma-api.polymarket.com"
    polymarket_clob_url: str = "https://clob.polymarket.com"

    @property
    def is_paper(self) -> bool:
        return self.trading_mode != "live"

    def kalshi_key_pem(self) -> bytes | None:
        if self.kalshi_private_key:
            return self.kalshi_private_key.encode()
        if self.kalshi_private_key_path and self.kalshi_private_key_path.exists():
            return self.kalshi_private_key_path.read_bytes()
        return None


def get_settings() -> Settings:
    return Settings()
