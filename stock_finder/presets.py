"""Screens predefinidos listos para usar.

Cada preset define: filtros, columnas extra, orden y una descripción.
Se ejecutan con:  stock-finder preset <nombre> [--market usa]

Nota de unidades (TradingView):
  - roe, net_margin, gross_margin, eps_growth, dividend_yield y los Perf.* vienen
    en PORCENTAJE (18.5 = 18,5 %).  ->  usar 'roe>15', no 'roe>0.15'.
  - pb, ps, debt_to_equity, beta son ratios (fracción).
Casi todos los presets incluyen 'type=stock' para excluir ETFs y fondos cerrados.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Preset:
    name: str
    description: str
    filters: list[str] = field(default_factory=list)
    columns: list[str] | None = None
    sort_by: str | None = None
    sort_order: str = "desc"
    min_price: float | None = None  # precio mínimo específico del preset


PRESETS: dict[str, Preset] = {
    # ---------------------------------------------------------------- VALOR
    "undervalued": Preset(
        name="undervalued",
        description="Infravaloradas de calidad: baratas por múltiplos pero rentables y poco endeudadas.",
        filters=["type=stock", "pe:0..15", "pb<1.5", "roe>10", "debt_to_equity<1", "market_cap>2b"],
        columns=["description", "close", "pe", "pb", "roe", "dividend_yield", "market_cap", "sector"],
        sort_by="pe",
        sort_order="asc",
        min_price=2.0,
    ),
    "deep-value": Preset(
        name="deep-value",
        description="Deep value: cotizan por debajo de su valor contable y con PER muy bajo.",
        filters=["type=stock", "pb<1", "pe:0..10", "roe>5", "market_cap>1b"],
        columns=["description", "close", "pe", "pb", "roe", "debt_to_equity", "market_cap", "sector"],
        sort_by="pb",
        sort_order="asc",
        min_price=2.0,
    ),
    "large-cap-value": Preset(
        name="large-cap-value",
        description="Grandes empresas baratas por fundamentales (PER bajo, ROE alto).",
        filters=["type=stock", "market_cap>10b", "pe:0..15", "roe>15"],
        columns=["description", "close", "change", "market_cap", "pe", "roe", "dividend_yield", "sector"],
        sort_by="market_cap",
    ),
    "garp": Preset(
        name="garp",
        description="Growth at a reasonable price: crecimiento sólido a múltiplo contenido.",
        filters=["type=stock", "pe:0..20", "eps_growth>15", "roe>12", "market_cap>2b"],
        columns=["description", "close", "pe", "eps_growth", "roe", "net_margin", "market_cap", "sector"],
        sort_by="eps_growth",
        min_price=2.0,
    ),
    "high-dividend": Preset(
        name="high-dividend",
        description="Alta rentabilidad por dividendo con capitalización relevante.",
        filters=["type=stock", "dividend_yield>4", "market_cap>2b", "pe>0"],
        columns=["description", "close", "dividend_yield", "pe", "payout_ratio", "market_cap", "sector"],
        sort_by="dividend_yield",
        min_price=2.0,
    ),
    "quality-growth": Preset(
        name="quality-growth",
        description="Crecimiento de calidad: márgenes altos, ROE alto y crecimiento de BPA.",
        filters=["type=stock", "eps_growth>15", "net_margin>10", "roe>15", "market_cap>1b"],
        columns=["description", "close", "change", "eps_growth", "net_margin", "roe", "pe", "sector"],
        sort_by="eps_growth",
        min_price=2.0,
    ),
    # ------------------------------------------------ VALOR + TÉCNICO (mixtos)
    "undervalued-bullish": Preset(
        name="undervalued-bullish",
        description="Infravaloradas con rating técnico alcista (valor + momentum).",
        filters=["type=stock", "pe:0..18", "pb<2", "roe>10", "debt_to_equity<1.2",
                 "market_cap>2b", "rating>0.1"],
        columns=["description", "close", "pe", "pb", "roe", "rating", "market_cap", "sector"],
        sort_by="rating",
        min_price=2.0,
    ),
    "strong-buy": Preset(
        name="strong-buy",
        description="Rating técnico STRONG BUY con liquidez y tamaño relevantes.",
        filters=["type=stock", "rating>0.5", "avg_volume_10d>1m", "market_cap>2b"],
        columns=["description", "close", "change", "rating", "rsi", "volume", "market_cap", "sector"],
        sort_by="rating",
        min_price=2.0,
    ),
    # ------------------------------------------------------------- TÉCNICO
    "oversold": Preset(
        name="oversold",
        description="Sobreventa técnica: RSI bajo con liquidez suficiente.",
        filters=["type=stock", "rsi<30", "market_cap>1b", "avg_volume_10d>500k"],
        columns=["description", "close", "change", "rsi", "volume", "market_cap", "sector"],
        sort_by="rsi",
        sort_order="asc",
        min_price=1.0,
    ),
    "momentum": Preset(
        name="momentum",
        description="Momentum alcista: fuerte subida mensual, por encima de la SMA200.",
        filters=["type=stock", "change_month>10", "close>sma200", "avg_volume_10d>1m"],
        columns=["description", "close", "change", "change_month", "change_3m", "rel_volume", "sector"],
        sort_by="change_month",
        min_price=1.0,
    ),
    "breakout": Preset(
        name="breakout",
        description="Cerca de máximos de 52 semanas con volumen relativo alto.",
        filters=["type=stock", "rel_volume>1.5", "change>2", "market_cap>500m"],
        columns=["description", "close", "change", "rel_volume", "high_52w", "volume", "sector"],
        sort_by="rel_volume",
        min_price=1.0,
    ),
    "gainers": Preset(
        name="gainers",
        description="Mayores subidas del día con liquidez.",
        filters=["type=stock", "change>0", "avg_volume_10d>500k", "market_cap>300m"],
        columns=["description", "close", "change", "volume", "rel_volume", "market_cap", "sector"],
        sort_by="change",
        min_price=1.0,
    ),
    "losers": Preset(
        name="losers",
        description="Mayores caídas del día con liquidez.",
        filters=["type=stock", "change<0", "avg_volume_10d>500k", "market_cap>300m"],
        columns=["description", "close", "change", "volume", "rel_volume", "market_cap", "sector"],
        sort_by="change",
        sort_order="asc",
        min_price=1.0,
    ),
}


def get_preset(name: str) -> Preset:
    key = name.strip().lower()
    if key not in PRESETS:
        raise KeyError(name)
    return PRESETS[key]
