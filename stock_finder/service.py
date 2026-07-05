"""Lógica de negocio compartida por la CLI y el servidor MCP.

Todas las funciones devuelven estructuras JSON-serializables (dicts / listas)
para que un agente (LLM) las consuma directamente.
"""

from __future__ import annotations

from typing import Any, Optional

from .api import Filter, TradingViewScanner
from .fields import DEFAULT_COLUMNS, resolve_columns, resolve_field, resolve_market
from .filters import parse_filters
from .presets import get_preset
from .signals import interval_suffix

# Campos técnicos que usan analyze / mtf (nombres base, sin sufijo de intervalo).
RATING_FIELDS = ["Recommend.All", "Recommend.MA", "Recommend.Other"]
INDICATOR_FIELDS = [
    "RSI", "MACD.macd", "MACD.signal", "Stoch.K", "Stoch.D",
    "CCI20", "ADX", "close", "SMA20", "SMA50", "SMA200", "EMA50", "EMA200",
]


def _sanitize_filters(
    filters: list[Filter], primary_only: bool, exclude_otc: bool, min_price: Optional[float]
) -> list[Filter]:
    if primary_only:
        filters.append(Filter(left="is_primary", operation="equal", right=True))
    if exclude_otc:
        filters.append(Filter(left="exchange", operation="nequal", right="OTC"))
    if min_price is not None:
        filters.append(Filter(left="close", operation="egreater", right=min_price))
    return filters


def run_screen(
    market: str = "usa",
    filter_exprs: Optional[list[str]] = None,
    column_aliases: Optional[list[str]] = None,
    sort_by: Optional[str] = None,
    order: str = "desc",
    limit: int = 50,
    offset: int = 0,
    primary_only: bool = True,
    exclude_otc: bool = True,
    min_price: Optional[float] = None,
) -> dict[str, Any]:
    """Ejecuta un screen. Lanza ValueError si un filtro es inválido."""
    columns = resolve_columns(column_aliases or DEFAULT_COLUMNS)
    filters = parse_filters(filter_exprs or [])
    filters = _sanitize_filters(filters, primary_only, exclude_otc, min_price)

    scanner = TradingViewScanner()
    res = scanner.scan(
        market=resolve_market(market),
        columns=columns,
        filters=filters,
        sort_by=resolve_field(sort_by) if sort_by else None,
        sort_order=order,
        range_=(offset, offset + limit),
    )
    return {
        "market": resolve_market(market),
        "total_count": res.total_count,
        "count": len(res.rows),
        "columns": columns,
        "rows": [
            {"ticker": r.ticker, "exchange": r.exchange, "symbol": r.symbol,
             **{c: r.values.get(c) for c in columns}}
            for r in res.rows
        ],
    }


def run_preset(
    name: str,
    market: str = "usa",
    limit: int = 50,
    offset: int = 0,
    primary_only: bool = True,
    exclude_otc: bool = True,
    min_price: Optional[float] = None,
) -> dict[str, Any]:
    """Ejecuta un preset por nombre. Lanza KeyError si no existe."""
    p = get_preset(name)
    payload = run_screen(
        market=market,
        filter_exprs=p.filters,
        column_aliases=p.columns or DEFAULT_COLUMNS,
        sort_by=p.sort_by,
        order=p.sort_order,
        limit=limit,
        offset=offset,
        primary_only=primary_only,
        exclude_otc=exclude_otc,
        min_price=min_price if min_price is not None else p.min_price,
    )
    payload["preset"] = p.name
    payload["description"] = p.description
    return payload


def _fetch_symbol(scanner: TradingViewScanner, market: str, name: str, columns: list[str]):
    res = scanner.scan(
        market=resolve_market(market),
        columns=columns,
        filters=[
            Filter(left="name", operation="equal", right=name),
            Filter(left="is_primary", operation="equal", right=True),
        ],
        range_=(0, 1),
    )
    return res.rows[0] if res.rows else None


def analyze(symbols: list[str], market: str = "usa", interval: str = "1D") -> list[dict[str, Any]]:
    """Análisis técnico (ratings + indicadores) de uno o varios símbolos."""
    suffix = interval_suffix(interval)
    base = RATING_FIELDS + INDICATOR_FIELDS
    columns = ["description"] + [f"{f}{suffix}" for f in base]

    scanner = TradingViewScanner()
    out: list[dict[str, Any]] = []
    for sym in symbols:
        name = sym.split(":", 1)[-1].upper()
        row = _fetch_symbol(scanner, market, name, columns)
        if row is None:
            out.append({"symbol": name, "found": False})
            continue
        out.append({
            "found": True,
            "ticker": row.ticker,
            "symbol": row.symbol,
            "name": str(row.values.get("description") or row.symbol),
            "interval": interval,
            "values": {f: row.values.get(f"{f}{suffix}") for f in base},
        })
    return out


def multi_timeframe(
    symbol: str, market: str = "usa", intervals: Optional[list[str]] = None
) -> dict[str, Any]:
    """Rating técnico de un valor a través de varias temporalidades (una sola petición)."""
    tfs = intervals or ["15m", "1h", "4h", "1D", "1W", "1M"]
    base = ["Recommend.All", "Recommend.MA", "Recommend.Other", "RSI"]

    columns = ["description"]
    for tf in tfs:
        s = interval_suffix(tf)
        columns += [f"{f}{s}" for f in base]

    scanner = TradingViewScanner()
    name = symbol.split(":", 1)[-1].upper()
    row = _fetch_symbol(scanner, market, name, columns)
    if row is None:
        return {"symbol": name, "found": False}

    timeframes = []
    for tf in tfs:
        s = interval_suffix(tf)
        timeframes.append({
            "tf": tf,
            "all": row.values.get(f"Recommend.All{s}"),
            "ma": row.values.get(f"Recommend.MA{s}"),
            "osc": row.values.get(f"Recommend.Other{s}"),
            "rsi": row.values.get(f"RSI{s}"),
        })
    return {
        "found": True,
        "ticker": row.ticker,
        "symbol": row.symbol,
        "name": str(row.values.get("description") or row.symbol),
        "timeframes": timeframes,
    }
