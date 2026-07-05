"""Interfaz de línea de comandos para el screener."""

from __future__ import annotations

import json as _json
from enum import Enum
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from .api import ScannerError
from .fields import DEFAULT_COLUMNS, FIELDS, MARKETS
from .output import render_analysis, render_mtf, render_table, to_csv, to_json
from .presets import PRESETS
from . import service
from . import prompt_lib

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


def _emit_screen(payload: dict, fmt: Fmt, title: str = "") -> None:
    if fmt is Fmt.table:
        render_table(payload, title=title)
    elif fmt is Fmt.csv:
        print(to_csv(payload))
    else:
        print(to_json(payload))


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
    try:
        payload = service.run_screen(
            market=market, filter_exprs=filter_, column_aliases=col_aliases,
            sort_by=sort_by, order=order, limit=limit, offset=offset,
            primary_only=primary_only, exclude_otc=exclude_otc, min_price=min_price,
        )
    except ValueError as exc:
        err.print(f"[red]Error de filtro:[/red] {exc}")
        raise typer.Exit(2)
    except ScannerError as exc:
        err.print(f"[red]Error del scanner:[/red] {exc}")
        raise typer.Exit(1)
    _emit_screen(payload, fmt)


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
        payload = service.run_preset(
            name, market=market, limit=limit, offset=offset,
            primary_only=primary_only, exclude_otc=exclude_otc, min_price=min_price,
        )
    except KeyError:
        err.print(f"[red]Preset desconocido:[/red] {name}. Usa 'presets' para ver la lista.")
        raise typer.Exit(2)
    except ScannerError as exc:
        err.print(f"[red]Error del scanner:[/red] {exc}")
        raise typer.Exit(1)
    _emit_screen(payload, fmt, title=f"{payload['preset']} · {payload['description']}")


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
    try:
        results = service.analyze(symbols, market=market, interval=interval)
    except ScannerError as exc:
        err.print(f"[red]Error del scanner:[/red] {exc}")
        raise typer.Exit(1)
    if fmt is Fmt.json:
        print(_json.dumps(results, indent=2, ensure_ascii=False))
    else:
        render_analysis(results)


@app.command()
def mtf(
    symbol: str = typer.Argument(..., help="Ticker a analizar. Ej: AAPL."),
    market: str = typer.Option("usa", "--market", "-m"),
    intervals: str = typer.Option(
        "15m,1h,4h,1D,1W,1M", "--intervals", "-i",
        help="Temporalidades separadas por coma.",
    ),
    fmt: Fmt = typer.Option(Fmt.table, "--format"),
) -> None:
    """Comparación multi-temporalidad del rating técnico de un valor."""
    tfs = [t.strip() for t in intervals.split(",") if t.strip()]
    try:
        payload = service.multi_timeframe(symbol, market=market, intervals=tfs)
    except ScannerError as exc:
        err.print(f"[red]Error del scanner:[/red] {exc}")
        raise typer.Exit(1)
    if fmt is Fmt.json:
        print(_json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        render_mtf(payload)


@app.command()
def presets(
    fmt: Fmt = typer.Option(Fmt.table, "--format", help="table o json."),
) -> None:
    """Lista los screens predefinidos."""
    if fmt is Fmt.json:
        data = [
            {"name": p.name, "description": p.description, "filters": p.filters,
             "columns": p.columns, "sort_by": p.sort_by, "sort_order": p.sort_order,
             "min_price": p.min_price}
            for p in PRESETS.values()
        ]
        print(_json.dumps(data, indent=2, ensure_ascii=False))
        return
    table = Table(title="Presets disponibles", header_style="bold cyan")
    table.add_column("nombre", style="bold")
    table.add_column("descripción")
    table.add_column("filtros", style="dim")
    for p in PRESETS.values():
        table.add_row(p.name, p.description, " · ".join(p.filters))
    console.print(table)


@app.command()
def fields(
    search: Optional[str] = typer.Argument(None, help="Filtra por texto."),
    fmt: Fmt = typer.Option(Fmt.table, "--format", help="table o json."),
) -> None:
    """Lista los alias de campos disponibles y su nombre técnico."""
    items = {
        a: t for a, t in sorted(FIELDS.items())
        if not search or search.lower() in a.lower() or search.lower() in t.lower()
    }
    if fmt is Fmt.json:
        print(_json.dumps(items, indent=2, ensure_ascii=False))
        return
    table = Table(title="Campos", header_style="bold cyan")
    table.add_column("alias", style="bold")
    table.add_column("campo técnico")
    for alias, tech in items.items():
        table.add_row(alias, tech)
    console.print(table)
    console.print("[dim]Puedes usar cualquier nombre técnico de TradingView aunque no esté aquí.[/dim]")


@app.command()
def markets(
    fmt: Fmt = typer.Option(Fmt.table, "--format", help="table o json."),
) -> None:
    """Lista los mercados soportados."""
    if fmt is Fmt.json:
        print(_json.dumps(MARKETS, indent=2, ensure_ascii=False))
        return
    table = Table(title="Mercados", header_style="bold cyan")
    table.add_column("alias", style="bold")
    table.add_column("segmento API")
    for alias, seg in sorted(MARKETS.items()):
        table.add_row(alias, seg)
    console.print(table)


@app.command()
def prompt(
    name: Optional[str] = typer.Argument(None, help="Nombre de la plantilla (vacío = listar)."),
    symbols: Optional[list[str]] = typer.Argument(None, help="Símbolo(s) para rellenar la plantilla."),
    market: str = typer.Option("usa", "--market", "-m"),
) -> None:
    """Imprime una plantilla de prompt para generar la ficha/report de un valor.

    Sin argumentos lista las plantillas. Con nombre (y símbolos opcionales) imprime
    el prompt listo para pasárselo a un LLM. Ej: stock-finder prompt deep-dive AAPL.
    """
    if not name:
        table = Table(title="Plantillas de prompt", header_style="bold cyan")
        table.add_column("nombre", style="bold")
        for n in prompt_lib.list_prompts():
            table.add_row(n)
        console.print(table)
        console.print("[dim]Uso: stock-finder prompt <nombre> [SIMBOLOS...] [-m mercado][/dim]")
        return
    try:
        text = prompt_lib.get_prompt(name, symbols=symbols or None, market=market)
    except KeyError:
        err.print(
            f"[red]Plantilla desconocida:[/red] {name}. "
            f"Disponibles: {', '.join(prompt_lib.list_prompts())}"
        )
        raise typer.Exit(2)
    print(text)


@app.command()
def version() -> None:
    """Muestra la versión."""
    console.print(f"stock-finder {__version__}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
