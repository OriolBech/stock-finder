"""Parseo de filtros desde la CLI a objetos Filter de TradingView.

Sintaxis soportada por filtro (`--filter`):
    campo>valor        campo mayor que valor
    campo>=valor
    campo<valor
    campo<=valor
    campo=valor        igual
    campo!=valor
    campo:a..b         rango (between, inclusive)  ->  RSI:30..70
    campo=texto        igualdad de texto (p.ej. sector="Technology")

El `campo` puede ser un alias legible (rsi, market_cap...) o un nombre técnico.
Los valores numéricos aceptan sufijos: k, m, b, t  (1.5b = 1_500_000_000).
"""

from __future__ import annotations

import re

from .api import Filter
from .fields import resolve_field

_SUFFIXES = {"k": 1e3, "m": 1e6, "b": 1e9, "t": 1e12}

_OP_MAP = {
    ">=": "egreater",
    "<=": "eless",
    ">": "greater",
    "<": "less",
    "!=": "nequal",
    "=": "equal",
}


def _parse_value(raw: str):
    raw = raw.strip().strip('"').strip("'")
    m = re.fullmatch(r"(-?\d*\.?\d+)([kmbtKMBT])", raw)
    if m:
        return float(m.group(1)) * _SUFFIXES[m.group(2).lower()]
    try:
        if re.fullmatch(r"-?\d+", raw):
            return int(raw)
        return float(raw)
    except ValueError:
        return raw  # texto (sector, país, etc.)


def parse_filter(expr: str) -> Filter:
    expr = expr.strip()

    # Rango: campo:a..b
    m = re.fullmatch(r"([\w.]+):(.+)\.\.(.+)", expr)
    if m:
        field = resolve_field(m.group(1))
        lo = _parse_value(m.group(2))
        hi = _parse_value(m.group(3))
        return Filter(left=field, operation="in_range", right=[lo, hi])

    # Operadores (ordenados: los de 2 chars primero)
    for op in (">=", "<=", "!=", ">", "<", "="):
        idx = expr.find(op)
        if idx > 0:
            field = resolve_field(expr[:idx])
            value = _parse_value(expr[idx + len(op):])
            # Si el valor es texto y coincide con un alias/campo conocido,
            # lo tratamos como comparación campo-contra-campo (p.ej. close>sma200).
            if isinstance(value, str):
                value = resolve_field(value)
            return Filter(left=field, operation=_OP_MAP[op], right=value)

    raise ValueError(
        f"Filtro no reconocido: '{expr}'. "
        "Usa formatos como  market_cap>1b , rsi<30 , sector=Technology , rsi:30..70"
    )


def parse_filters(exprs: list[str]) -> list[Filter]:
    return [parse_filter(e) for e in exprs]
