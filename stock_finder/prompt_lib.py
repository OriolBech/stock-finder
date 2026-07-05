"""Carga de plantillas de prompts para generar fichas/reports de un valor.

Las plantillas viven en stock_finder/prompts/*.md y se distribuyen con el paquete.
Un agente (LLM) las recupera por CLI (`stock-finder prompt <nombre>`) o por MCP
(`list_prompts` / `get_prompt`) y las usa como base para el informe.
"""

from __future__ import annotations

from importlib import resources


def _prompts_dir():
    return resources.files("stock_finder") / "prompts"


def list_prompts() -> list[str]:
    """Nombres de las plantillas disponibles (sin extensión)."""
    return sorted(
        p.name[:-3] for p in _prompts_dir().iterdir() if p.name.endswith(".md")
    )


def get_prompt(
    name: str,
    symbol: str | None = None,
    symbols: list[str] | None = None,
    market: str = "usa",
) -> str:
    """Devuelve la plantilla rellenando los marcadores {SYMBOL}/{SYMBOLS}/{MARKET}.

    Lanza KeyError si la plantilla no existe.
    """
    path = _prompts_dir() / f"{name}.md"
    if not path.is_file():
        raise KeyError(name)
    text = path.read_text(encoding="utf-8")

    syms = symbols or ([symbol] if symbol else [])
    if syms:
        text = text.replace("{SYMBOL}", syms[0])
        text = text.replace("{SYMBOLS}", ", ".join(syms))
    text = text.replace("{MARKET}", market)
    return text
