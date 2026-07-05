"""Interpretación de señales técnicas.

TradingView precalcula tres ratings agregados y los expone en el scanner:
  - Recommend.All   -> resumen global
  - Recommend.MA    -> medias móviles
  - Recommend.Other -> osciladores
Cada uno es un número en [-1, 1] que se traduce a STRONG SELL … STRONG BUY.

Los indicadores individuales (RSI, MACD, etc.) se piden por su valor crudo y
aquí los interpretamos con reglas sencillas y explícitas.
"""

from __future__ import annotations

# Temporalidad amigable -> sufijo de intervalo de TradingView.
# El diario ("1D") no lleva sufijo; el resto se añade como "<campo>|<intervalo>".
INTERVALS: dict[str, str] = {
    "1m": "1", "5m": "5", "15m": "15", "30m": "30",
    "1h": "60", "2h": "120", "4h": "240",
    "1d": "", "1D": "",
    "1w": "1W", "1W": "1W",
    "1M": "1M",
}


def interval_suffix(timeframe: str) -> str:
    tf = timeframe.strip()
    code = INTERVALS.get(tf, INTERVALS.get(tf.lower(), ""))
    return f"|{code}" if code else ""


def rating_label(value: float | None) -> tuple[str, str]:
    """Traduce un rating [-1,1] a (etiqueta, color rich)."""
    if value is None:
        return ("N/D", "dim")
    if value >= 0.5:
        return ("STRONG BUY", "bold green")
    if value >= 0.1:
        return ("BUY", "green")
    if value > -0.1:
        return ("NEUTRAL", "yellow")
    if value > -0.5:
        return ("SELL", "red")
    return ("STRONG SELL", "bold red")


def rsi_label(v: float | None) -> tuple[str, str]:
    if v is None:
        return ("-", "dim")
    if v >= 70:
        return ("sobrecompra", "red")
    if v <= 30:
        return ("sobreventa", "green")
    return ("neutral", "yellow")


def macd_label(macd: float | None, signal: float | None) -> tuple[str, str]:
    if macd is None or signal is None:
        return ("-", "dim")
    if macd > signal:
        return ("alcista", "green")
    if macd < signal:
        return ("bajista", "red")
    return ("plano", "yellow")


def stoch_label(k: float | None) -> tuple[str, str]:
    if k is None:
        return ("-", "dim")
    if k >= 80:
        return ("sobrecompra", "red")
    if k <= 20:
        return ("sobreventa", "green")
    return ("neutral", "yellow")


def adx_label(v: float | None) -> tuple[str, str]:
    if v is None:
        return ("-", "dim")
    if v >= 25:
        return ("tendencia fuerte", "cyan")
    if v >= 20:
        return ("tendencia incipiente", "yellow")
    return ("sin tendencia", "dim")


def vs_ma_label(close: float | None, ma: float | None) -> tuple[str, str]:
    """Posición del precio respecto a una media móvil, en %."""
    if not close or not ma:
        return ("-", "dim")
    pct = (close / ma - 1) * 100
    color = "green" if pct >= 0 else "red"
    return (f"{pct:+.1f}%", color)
