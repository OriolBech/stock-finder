"""Servidor MCP para stock-finder.

Expone el screener y el análisis técnico como herramientas MCP, de modo que un
agente (Claude Code, Claude Desktop, etc.) pueda llamarlas directamente. El LLM
aporta el contexto cualitativo (noticias vía websearch); este servidor aporta
los datos cuantitativos de TradingView.

Ejecutar:  stock-finder-mcp        (requiere el extra 'mcp':  pip install -e '.[mcp]')

Registro en Claude Code:
    claude mcp add stock-finder -- stock-finder-mcp
"""

from __future__ import annotations

from typing import Optional

from .api import ScannerError
from .fields import FIELDS, MARKETS
from .presets import PRESETS
from . import service
from . import prompt_lib

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Falta la dependencia 'mcp'. Instálala con:  pip install -e '.[mcp]'"
    ) from exc

mcp = FastMCP("stock-finder")


@mcp.tool()
def screen(
    market: str = "usa",
    filters: Optional[list[str]] = None,
    columns: Optional[list[str]] = None,
    sort_by: Optional[str] = None,
    order: str = "desc",
    limit: int = 50,
    primary_only: bool = True,
    exclude_otc: bool = True,
    min_price: Optional[float] = None,
) -> dict:
    """Filtra acciones por fundamentales/técnicos y devuelve las coincidencias.

    filters: lista de expresiones. Ej: ["market_cap>10b", "pe:0..15", "rsi<40",
             "sector=Technology", "close>sma200"]. Sufijos numéricos k/m/b/t.
    columns: alias o nombres técnicos (usa list_fields). Por defecto un set básico.
    sort_by: campo por el que ordenar (alias o técnico). order: asc|desc.
    Ojo unidades: roe, márgenes, eps_growth, dividend_yield y Perf.* van en %.
    Devuelve {market, total_count, count, columns, rows:[{ticker,symbol,...}]}.
    """
    try:
        return service.run_screen(
            market=market, filter_exprs=filters, column_aliases=columns,
            sort_by=sort_by, order=order, limit=limit,
            primary_only=primary_only, exclude_otc=exclude_otc, min_price=min_price,
        )
    except ValueError as exc:
        return {"error": f"filtro inválido: {exc}"}
    except ScannerError as exc:
        return {"error": f"scanner: {exc}"}


@mcp.tool()
def run_preset(name: str, market: str = "usa", limit: int = 50) -> dict:
    """Ejecuta un screen predefinido por nombre (usa list_presets para verlos).

    Presets útiles: 'undervalued', 'deep-value', 'pullback' (recorte sano en
    tendencia alcista → candidato a rebote), 'dip-value', 'undervalued-bullish',
    'strong-buy', 'oversold', 'momentum', 'high-dividend', etc.
    """
    try:
        return service.run_preset(name, market=market, limit=limit)
    except KeyError:
        return {"error": f"preset desconocido: {name}", "available": list(PRESETS)}
    except ScannerError as exc:
        return {"error": f"scanner: {exc}"}


@mcp.tool()
def analyze(symbols: list[str], market: str = "usa", interval: str = "1D") -> list[dict]:
    """Análisis técnico de uno o varios valores en una temporalidad.

    Devuelve, por símbolo: rating global/medias/osciladores (Recommend.* en
    [-1,1]) y valores de RSI, MACD, estocástico, CCI, ADX y las SMA/EMA.
    interval: 1m,5m,15m,30m,1h,2h,4h,1D,1W,1M.
    """
    try:
        return service.analyze(symbols, market=market, interval=interval)
    except ScannerError as exc:
        return [{"error": f"scanner: {exc}"}]


@mcp.tool()
def multi_timeframe(symbol: str, market: str = "usa", intervals: Optional[list[str]] = None) -> dict:
    """Rating técnico de un valor a través de varias temporalidades (alineación de señales).

    Útil para ver si la tendencia de fondo (1D/1W/1M) sigue alcista aunque el
    corto plazo (15m/1h) esté sobrecomprado o corrigiendo.
    """
    try:
        return service.multi_timeframe(symbol, market=market, intervals=intervals)
    except ScannerError as exc:
        return {"error": f"scanner: {exc}"}


@mcp.tool()
def list_presets() -> list[dict]:
    """Lista los presets disponibles con su descripción y filtros."""
    return [
        {"name": p.name, "description": p.description, "filters": p.filters}
        for p in PRESETS.values()
    ]


@mcp.tool()
def list_fields() -> dict:
    """Diccionario alias -> nombre técnico de los campos disponibles para filtros/columnas."""
    return FIELDS


@mcp.tool()
def list_markets() -> dict:
    """Diccionario alias -> segmento de los mercados soportados."""
    return MARKETS


@mcp.tool()
def list_prompts() -> list[str]:
    """Nombres de las plantillas de report/ficha disponibles (deep-dive, rebound-check, compare)."""
    return prompt_lib.list_prompts()


@mcp.tool()
def get_prompt(
    name: str,
    symbols: Optional[list[str]] = None,
    market: str = "usa",
) -> dict:
    """Devuelve una plantilla de prompt lista para generar la ficha/report de un valor.

    Úsala como BASE: recupera la plantilla, ejecuta las herramientas que indica
    (analyze/multi_timeframe/screen) y completa con tu búsqueda web. Plantillas:
    'deep-dive' (ficha completa), 'rebound-check' (rebote vs trampa), 'compare'.
    """
    try:
        return {"name": name, "prompt": prompt_lib.get_prompt(name, symbols=symbols, market=market)}
    except KeyError:
        return {"error": f"plantilla desconocida: {name}", "available": prompt_lib.list_prompts()}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
