"""Catálogo de columnas (campos) y mercados disponibles en el scanner.

TradingView expone cientos de campos; aquí recogemos los más útiles con un
alias legible y su nombre técnico interno. Puedes usar cualquier campo técnico
aunque no esté en esta lista pasándolo directamente por su nombre.
"""

from __future__ import annotations

# alias legible -> nombre técnico de TradingView
FIELDS: dict[str, str] = {
    # Identidad
    "name": "name",
    "description": "description",
    "sector": "sector",
    "industry": "industry",
    "country": "country",
    "currency": "currency",
    "type": "type",
    "exchange": "exchange",
    "is_primary": "is_primary",
    # Precio y variación
    "close": "close",
    "open": "open",
    "high": "high",
    "low": "low",
    "change": "change",            # % variación día
    "change_abs": "change_abs",
    "change_week": "Perf.W",
    "change_month": "Perf.1M",
    "change_3m": "Perf.3M",
    "change_6m": "Perf.6M",
    "change_ytd": "Perf.YTD",
    "change_year": "Perf.Y",
    "high_52w": "price_52_week_high",
    "low_52w": "price_52_week_low",
    "gap": "gap",
    # Volumen y liquidez
    "volume": "volume",
    "avg_volume_10d": "average_volume_10d_calc",
    "avg_volume_90d": "average_volume_90d_calc",
    "rel_volume": "relative_volume_10d_calc",
    "value_traded": "Value.Traded",
    # Capitalización y fundamentales
    "market_cap": "market_cap_basic",
    "pe": "price_earnings_ttm",
    "eps": "earnings_per_share_basic_ttm",
    "eps_growth": "earnings_per_share_diluted_yoy_growth_ttm",
    "dividend_yield": "dividends_yield_current",
    "payout_ratio": "dividend_payout_ratio_ttm",
    "pb": "price_book_ratio",
    "ps": "price_sales_current",
    "debt_to_equity": "debt_to_equity",
    "roe": "return_on_equity",
    "gross_margin": "gross_margin_ttm",
    "net_margin": "net_margin_ttm",
    "revenue": "total_revenue_ttm",
    # Indicadores técnicos
    "rsi": "RSI",
    "rsi_7": "RSI7",
    "macd": "MACD.macd",
    "macd_signal": "MACD.signal",
    "atr": "ATR",
    "adx": "ADX",
    "sma20": "SMA20",
    "sma50": "SMA50",
    "sma200": "SMA200",
    "ema20": "EMA20",
    "ema50": "EMA50",
    "ema200": "EMA200",
    "beta_1y": "beta_1_year",
    "volatility_w": "Volatility.W",
    "volatility_m": "Volatility.M",
    # Señales / rating
    "rating": "Recommend.All",       # rating técnico global (-1 a 1)
    "rating_ma": "Recommend.MA",
    "rating_osc": "Recommend.Other",
}

# Columnas por defecto en la salida.
DEFAULT_COLUMNS = [
    "description",
    "close",
    "change",
    "volume",
    "market_cap",
    "pe",
    "sector",
]

# Mercados soportados por el scanner (subconjunto útil). El valor es el
# segmento de la URL. Hay muchos más países disponibles.
MARKETS: dict[str, str] = {
    "usa": "america",
    "america": "america",
    "spain": "spain",
    "españa": "spain",
    "germany": "germany",
    "france": "france",
    "italy": "italy",
    "uk": "uk",
    "netherlands": "netherlands",
    "portugal": "portugal",
    "switzerland": "switzerland",
    "euronext": "euronext",
    "crypto": "crypto",
    "forex": "forex",
    "cfd": "cfd",
    "global": "global",
}


def resolve_market(market: str) -> str:
    """Convierte un nombre amigable al segmento de URL del scanner."""
    key = market.strip().lower()
    return MARKETS.get(key, key)


def resolve_field(alias: str) -> str:
    """Convierte un alias legible a su nombre técnico; si no existe, lo devuelve tal cual."""
    return FIELDS.get(alias.strip(), alias.strip())


def resolve_columns(aliases: list[str]) -> list[str]:
    return [resolve_field(a) for a in aliases]
