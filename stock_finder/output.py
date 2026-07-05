"""Renderizado de resultados: tabla en terminal, CSV o JSON."""

from __future__ import annotations

import csv
import io
import json
from typing import Any

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .api import ScanResult
from .signals import (
    adx_label,
    macd_label,
    rating_label,
    rsi_label,
    stoch_label,
    vs_ma_label,
)

console = Console()

# Campos que se muestran como porcentaje coloreado.
_PCT_FIELDS = {
    "change", "Perf.W", "Perf.1M", "Perf.3M", "Perf.6M",
    "Perf.YTD", "Perf.Y", "dividends_yield_current",
}
# Campos con formato numérico grande (miles/millones).
_BIG_FIELDS = {"market_cap_basic", "volume", "average_volume_10d_calc",
               "average_volume_90d_calc", "total_revenue_ttm", "Value.Traded"}


def _fmt_big(v: float) -> str:
    for unit, div in (("T", 1e12), ("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if abs(v) >= div:
            return f"{v / div:.2f}{unit}"
    return f"{v:.0f}"


def _fmt_cell(col: str, value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, (int, float)):
        if col in _BIG_FIELDS:
            return _fmt_big(value)
        if col in _PCT_FIELDS:
            return f"{value:+.2f}%"
        return f"{value:,.2f}"
    return str(value)


def _color_for(col: str, value: Any) -> str | None:
    if col in _PCT_FIELDS and isinstance(value, (int, float)) and col != "dividends_yield_current":
        return "green" if value > 0 else "red" if value < 0 else None
    return None


def render_table(result: ScanResult, columns: list[str], title: str = "") -> None:
    table = Table(title=title or None, header_style="bold cyan", expand=False)
    table.add_column("#", justify="right", style="dim")
    table.add_column("symbol", style="bold")
    for col in columns:
        table.add_column(col, justify="right" if col != "name" else "left")

    for i, row in enumerate(result.rows, 1):
        cells = [str(i), row.symbol]
        for col in columns:
            val = row.values.get(col)
            text = _fmt_cell(col, val)
            color = _color_for(col, val)
            cells.append(f"[{color}]{text}[/{color}]" if color else text)
        table.add_row(*cells)

    console.print(table)
    console.print(
        f"[dim]{len(result.rows)} filas mostradas · {result.total_count} coincidencias totales[/dim]"
    )


def _num(v, fmt="{:.2f}"):
    return fmt.format(v) if isinstance(v, (int, float)) else "-"


def render_analysis(results: list[dict]) -> None:
    """Renderiza un panel de análisis técnico por cada símbolo."""
    for r in results:
        v = r["values"]
        close = v.get("close")

        # Ratings agregados (los precalcula TradingView).
        all_txt, all_c = rating_label(v.get("Recommend.All"))
        ma_txt, ma_c = rating_label(v.get("Recommend.MA"))
        osc_txt, osc_c = rating_label(v.get("Recommend.Other"))

        title = f"{r['symbol']}  ·  {r['name']}  ({r['ticker']} · {r['interval']})"
        summary = Text.from_markup(
            f"Precio: [bold]{_num(close)}[/bold]\n\n"
            f"Resumen:      [{all_c}]{all_txt}[/{all_c}] "
            f"[dim]({_num(v.get('Recommend.All'), '{:+.2f}')})[/dim]\n"
            f"Medias:       [{ma_c}]{ma_txt}[/{ma_c}] "
            f"[dim]({_num(v.get('Recommend.MA'), '{:+.2f}')})[/dim]\n"
            f"Osciladores:  [{osc_c}]{osc_txt}[/{osc_c}] "
            f"[dim]({_num(v.get('Recommend.Other'), '{:+.2f}')})[/dim]"
        )

        table = Table(show_header=True, header_style="bold cyan", box=None, pad_edge=False)
        table.add_column("indicador")
        table.add_column("valor", justify="right")
        table.add_column("lectura")

        def add(name, value, label_pair, valfmt="{:.2f}"):
            txt, color = label_pair
            table.add_row(name, _num(value, valfmt), f"[{color}]{txt}[/{color}]")

        add("RSI (14)", v.get("RSI"), rsi_label(v.get("RSI")))
        macd, sig = v.get("MACD.macd"), v.get("MACD.signal")
        add("MACD", macd, macd_label(macd, sig), "{:+.3f}")
        add("Estocástico %K", v.get("Stoch.K"), stoch_label(v.get("Stoch.K")))
        add("CCI (20)", v.get("CCI20"),
            ("sobrecompra", "red") if (v.get("CCI20") or 0) > 100
            else ("sobreventa", "green") if (v.get("CCI20") or 0) < -100
            else ("neutral", "yellow"))
        add("ADX (14)", v.get("ADX"), adx_label(v.get("ADX")))
        add("Precio vs SMA20", v.get("SMA20"), vs_ma_label(close, v.get("SMA20")))
        add("Precio vs SMA50", v.get("SMA50"), vs_ma_label(close, v.get("SMA50")))
        add("Precio vs SMA200", v.get("SMA200"), vs_ma_label(close, v.get("SMA200")))

        body = Group(summary, Text(""), table)
        panel = Panel(body, title=title, title_align="left", border_style=all_c, expand=False)
        console.print(panel)


def to_csv(result: ScanResult, columns: list[str]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["ticker", "exchange", "symbol", *columns])
    for row in result.rows:
        writer.writerow(
            [row.ticker, row.exchange, row.symbol, *[row.values.get(c) for c in columns]]
        )
    return buf.getvalue()


def to_json(result: ScanResult, columns: list[str]) -> str:
    out = {
        "total_count": result.total_count,
        "count": len(result.rows),
        "rows": [
            {"ticker": r.ticker, "exchange": r.exchange, "symbol": r.symbol,
             **{c: r.values.get(c) for c in columns}}
            for r in result.rows
        ],
    }
    return json.dumps(out, indent=2, ensure_ascii=False)
