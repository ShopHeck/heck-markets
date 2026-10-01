from heck_markets.config import Settings


def test_defaults_are_paper():
    s = Settings(trading_mode="paper")
    assert s.is_paper
    assert s.kalshi_base_url.startswith("https://")


def test_inline_key_takes_precedence(tmp_path):
    pem = tmp_path / "k.pem"
    pem.write_text("path-key")
    s = Settings(
        kalshi_private_key="inline-key",
        kalshi_private_key_path=pem,
    )
    assert s.kalshi_key_pem() == b"inline-key"


def test_key_from_path(tmp_path):
    pem = tmp_path / "k.pem"
    pem.write_text("path-key")
    s = Settings(kalshi_private_key_path=pem)
    assert s.kalshi_key_pem() == b"path-key"


def test_no_key_returns_none():
    s = Settings()
    assert s.kalshi_key_pem() is None
