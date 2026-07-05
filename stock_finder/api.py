"""Cliente para la API interna del scanner de TradingView.

TradingView no publica una API oficial, pero su web usa el endpoint
    POST https://scanner.tradingview.com/{market}/scan
que devuelve JSON. Es mucho más estable que scrapear el HTML.

Formato de la petición (resumido):
    {
      "columns": ["name", "close", ...],
      "filter":  [{"left": "market_cap_basic", "operation": "greater", "right": 1e9}],
      "sort":    {"sortBy": "market_cap_basic", "sortOrder": "desc"},
      "range":   [0, 100],
      "options": {"lang": "en"}
    }

Respuesta:
    {"totalCount": 5000, "data": [{"s": "NASDAQ:AAPL", "d": [<valores en orden de columns>]}]}
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import requests

SCANNER_URL = "https://scanner.tradingview.com/{market}/scan"

# Cabeceras que imitan al navegador para no ser bloqueados.
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Content-Type": "application/json; charset=UTF-8",
    "Origin": "https://www.tradingview.com",
    "Referer": "https://www.tradingview.com/",
}


class ScannerError(RuntimeError):
    """Error al consultar el scanner de TradingView."""


@dataclass
class ScanRow:
    """Una fila del resultado: el ticker y los valores de las columnas pedidas."""

    ticker: str  # p.ej. "NASDAQ:AAPL"
    values: dict[str, Any]

    @property
    def symbol(self) -> str:
        return self.ticker.split(":", 1)[-1]

    @property
    def exchange(self) -> str:
        return self.ticker.split(":", 1)[0] if ":" in self.ticker else ""


@dataclass
class ScanResult:
    total_count: int
    rows: list[ScanRow] = field(default_factory=list)


@dataclass
class Filter:
    """Un filtro de columna. `operation` es el vocabulario de TradingView."""

    left: str
    operation: str
    right: Any = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"left": self.left, "operation": self.operation}
        if self.right is not None:
            d["right"] = self.right
        return d


class TradingViewScanner:
    def __init__(self, timeout: float = 20.0, retries: int = 3):
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()
        self.session.headers.update(_HEADERS)

    def scan(
        self,
        market: str,
        columns: list[str],
        filters: list[Filter] | None = None,
        sort_by: str | None = None,
        sort_order: str = "desc",
        range_: tuple[int, int] = (0, 100),
        lang: str = "en",
        symbol_types: list[str] | None = None,
    ) -> ScanResult:
        payload: dict[str, Any] = {
            "columns": columns,
            "options": {"lang": lang},
            "range": list(range_),
            "symbols": {
                "query": {"types": symbol_types or []},
                "tickers": [],
            },
        }
        if filters:
            payload["filter"] = [f.to_dict() for f in filters]
        if sort_by:
            payload["sort"] = {"sortBy": sort_by, "sortOrder": sort_order}

        url = SCANNER_URL.format(market=market)
        data = self._post(url, payload)

        rows: list[ScanRow] = []
        for item in data.get("data", []) or []:
            vals = item.get("d", []) or []
            rows.append(
                ScanRow(
                    ticker=item.get("s", ""),
                    values=dict(zip(columns, vals)),
                )
            )
        return ScanResult(total_count=data.get("totalCount", len(rows)), rows=rows)

    def _post(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        last_exc: Exception | None = None
        for attempt in range(1, self.retries + 1):
            try:
                resp = self.session.post(url, json=payload, timeout=self.timeout)
                if resp.status_code == 200:
                    return resp.json()
                if resp.status_code in (429, 503):
                    time.sleep(min(2 ** attempt, 10))
                    continue
                raise ScannerError(
                    f"HTTP {resp.status_code} desde {url}: {resp.text[:300]}"
                )
            except requests.RequestException as exc:
                last_exc = exc
                time.sleep(min(2 ** attempt, 10))
        raise ScannerError(f"No se pudo consultar {url}: {last_exc}")
