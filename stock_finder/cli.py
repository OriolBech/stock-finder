"""Interfaz de línea de comandos para el screener."""

from __future__ import annotations

import sys
from enum import Enum
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from .api import Filter, ScanResult, ScannerError, TradingViewScanner
from .fields import (
    DEFAULT_COLUMNS,
    FIELDS,
    MARKETS,
    resolve_columns,
    resolve_field,
    resolve_market,
)
from .filters import parse_filters
from .output import render_analysis, render_table, to_csv, to_json
from .presets import PRESETS, get_preset
from .signals import interval_suffix

app = typer.Typer(
    add_completion=False,
    help="Screener de acciones sobre la API del scanner de TradingView.",
    no_args_is_help=True,
)
console = Console()
err = Console(stderr=True)


class Fmt(str, Enum):
    table = "table"
    csv = "csv"
    json = "json"


def _emit(result: ScanResult, columns: list[str], fmt: Fmt, title: str = "") -> None:
    if fmt is Fmt.table:
        render_table(result, columns, title=title)
    elif fmt is Fmt.csv:
        print(to_csv(result, columns))
    else:
        print(to_json(result, columns))


def _run_scan(
    market: str,
    column_aliases: list[str],
    filter_exprs: list[str],
    sort_alias: Optional[str],
    order: str,
    limit: int,
    offset: int,
    fmt: Fmt,
    title: str = "",
    primary_only: bool = True,
    exclude_otc: bool = True,
    min_price: Optional[float] = None,
) -> None:
    columns = resolve_columns(column_aliases)
    try:
        filters = parse_filters(filter_exprs)
    except ValueError as exc:
        err.print(f"[red]Error de filtro:[/red] {exc}")
        raise typer.Exit(2)

    # Filtros de saneo (se añaden a los del usuario/preset).
    if primary_only:
        filters.append(Filter(left="is_primary", operation="equal", right=True))
    if exclude_otc:
        filters.append(Filter(left="exchange", operation="nequal", right="OTC"))
    if min_price is not None:
        filters.append(Filter(left="close", operation="egreater", right=min_price))

    sort_by = resolve_field(sort_alias) if sort_alias else None
    scanner = TradingViewScanner()
    try:
        result = scanner.scan(
            market=resolve_market(market),
            columns=columns,
            filters=filters,
            sort_by=sort_by,
            sort_order=order,
            range_=(offset, offset + limit),
        )
    except ScannerError as exc:
        err.print(f"[red]Error del scanner:[/red] {exc}")
        raise typer.Exit(1)

    _emit(result, columns, fmt, title=title)


@app.command()
def screen(
    market: str = typer.Option("usa", "--market", "-m", help="Mercado (usa, spain, germany, crypto...)."),
    filter_: list[str] = typer.Option(
        [], "--filter", "-f",
        help="Filtro repetible. Ej: -f 'market_cap>1b' -f 'rsi<30' -f 'sector=Technology'.",
    ),
    columns: str = typer.Option(
        ",".join(DEFAULT_COLUMNS), "--columns", "-c",
        help="Columnas separadas por coma (alias o nombre técnico).",
    ),
    sort_by: Optional[str] = typer.Option(None, "--sort", "-s", help="Campo por el que ordenar."),
    order: str = typer.Option("desc", "--order", "-o", help="asc o desc."),
    limit: int = typer.Option(50, "--limit", "-l", help="Número de resultados."),
    offset: int = typer.Option(0, "--offset", help="Desplazamiento para paginar."),
    fmt: Fmt = typer.Option(Fmt.table, "--format", help="table, csv o json."),
    primary_only: bool = typer.Option(
        True, "--primary/--all-listings",
        help="Solo el listado primario de cada valor (evita duplicados cross-listed).",
    ),
    exclude_otc: bool = typer.Option(
        True, "--exclude-otc/--include-otc", help="Excluir mercado OTC / pink sheets.",
    ),
    min_price: Optional[float] = typer.Option(
        None, "--min-price", help="Precio de cierre mínimo (filtra penny stocks).",
    ),
) -> None:
    """Ejecuta un screen personalizado con filtros arbitrarios."""
    col_aliases = [c.strip() for c in columns.split(",") if c.strip()]
    _run_scan(
        market, col_aliases, filter_, sort_by, order, limit, offset, fmt,
        primary_only=primary_only, exclude_otc=exclude_otc, min_price=min_price,
    )


@app.command()
def preset(
    name: str = typer.Argument(..., help="Nombre del preset (ver 'presets')."),
    market: str = typer.Option("usa", "--market", "-m"),
    limit: int = typer.Option(50, "--limit", "-l"),
    offset: int = typer.Option(0, "--offset"),
    fmt: Fmt = typer.Option(Fmt.table, "--format"),
    primary_only: bool = typer.Option(True, "--primary/--all-listings"),
    exclude_otc: bool = typer.Option(True, "--exclude-otc/--include-otc"),
    min_price: Optional[float] = typer.Option(
        None, "--min-price", help="Sobrescribe el precio mínimo del preset.",
    ),
) -> None:
    """Ejecuta un screen predefinido."""
    try:
        p = get_preset(name)
    except KeyError:
        err.print(f"[red]Preset desconocido:[/red] {name}. Usa 'presets' para ver la lista.")
        raise typer.Exit(2)

    cols = p.columns or DEFAULT_COLUMNS
    _run_scan(
        market, cols, p.filters, p.sort_by, p.sort_order, limit, offset, fmt,
        title=f"{p.name} · {p.description}",
        primary_only=primary_only, exclude_otc=exclude_otc,
        min_price=min_price if min_price is not None else p.min_price,
    )


# Campos técnicos que pide 'analyze' (nombres base, sin sufijo de intervalo).
_RATING_FIELDS = ["Recommend.All", "Recommend.MA", "Recommend.Other"]
_INDICATOR_FIELDS = [
    "RSI", "MACD.macd", "MACD.signal", "Stoch.K", "Stoch.D",
    "CCI20", "ADX", "close", "SMA20", "SMA50", "SMA200", "EMA50", "EMA200",
]


@app.command()
def analyze(
    symbols: list[str] = typer.Argument(..., help="Uno o más tickers. Ej: AAPL MSFT NVDA."),
    market: str = typer.Option("usa", "--market", "-m", help="Mercado del símbolo."),
    interval: str = typer.Option(
        "1D", "--interval", "-i",
        help="Temporalidad: 1m,5m,15m,30m,1h,2h,4h,1D,1W,1M.",
    ),
    fmt: Fmt = typer.Option(Fmt.table, "--format", help="table o json."),
) -> None:
    """Análisis técnico de uno o varios valores (rating, medias, osciladores)."""
    suffix = interval_suffix(interval)
    base_fields = _RATING_FIELDS + _INDICATOR_FIELDS
    columns = ["description"] + [f"{f}{suffix}" for f in base_fields]

    scanner = TradingViewScanner()
    results = []
    for sym in symbols:
        name = sym.split(":", 1)[-1].upper()
        try:
            res = scanner.scan(
                market=resolve_market(market),
                columns=columns,
                filters=[
                    Filter(left="name", operation="equal", right=name),
                    Filter(left="is_primary", operation="equal", right=True),
                ],
                range_=(0, 1),
            )
        except ScannerError as exc:
            err.print(f"[red]Error del scanner ({sym}):[/red] {exc}")
            continue
        if not res.rows:
            err.print(f"[yellow]No encontrado:[/yellow] {sym} en mercado '{market}'.")
            continue
        row = res.rows[0]
        # Reindexa los valores quitando el sufijo de intervalo para simplificar.
        vals = {f: row.values.get(f"{f}{suffix}") for f in base_fields}
        results.append({
            "ticker": row.ticker,
            "symbol": row.symbol,
            "name": vals_desc(row),
            "interval": interval,
            "values": vals,
        })

    if fmt is Fmt.json:
        import json
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        render_analysis(results)


def vals_desc(row) -> str:
    return str(row.values.get("description") or row.symbol)


@app.command()
def presets() -> None:
    """Lista los screens predefinidos."""
    table = Table(title="Presets disponibles", header_style="bold cyan")
    table.add_column("nombre", style="bold")
    table.add_column("descripción")
    table.add_column("filtros", style="dim")
    for p in PRESETS.values():
        table.add_row(p.name, p.description, " · ".join(p.filters))
    console.print(table)


@app.command()
def fields(search: Optional[str] = typer.Argument(None, help="Filtra por texto.")) -> None:
    """Lista los alias de campos disponibles y su nombre técnico."""
    table = Table(title="Campos", header_style="bold cyan")
    table.add_column("alias", style="bold")
    table.add_column("campo técnico")
    for alias, tech in sorted(FIELDS.items()):
        if search and search.lower() not in alias.lower() and search.lower() not in tech.lower():
            continue
        table.add_row(alias, tech)
    console.print(table)
    console.print("[dim]Puedes usar cualquier nombre técnico de TradingView aunque no esté aquí.[/dim]")


@app.command()
def markets() -> None:
    """Lista los mercados soportados."""
    table = Table(title="Mercados", header_style="bold cyan")
    table.add_column("alias", style="bold")
    table.add_column("segmento API")
    for alias, seg in sorted(MARKETS.items()):
        table.add_row(alias, seg)
    console.print(table)


@app.command()
def version() -> None:
    """Muestra la versión."""
    console.print(f"stock-finder {__version__}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
