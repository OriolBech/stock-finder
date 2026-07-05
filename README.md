# stock-finder

Screener de acciones desde la línea de comandos. Usa la **API interna del scanner de
TradingView** (`scanner.tradingview.com/{mercado}/scan`) en lugar de scrapear HTML:
mismo dato que ves en la web, pero en JSON, estable y rápido.

> Uso personal / educativo. Es una API no oficial; respeta un ritmo de peticiones razonable.

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Queda disponible el comando `stock-finder` (o `python -m stock_finder`).

## Uso rápido

```bash
# Screens predefinidos
stock-finder presets                       # lista los presets
stock-finder preset oversold -m usa        # RSI bajo en EE.UU.
stock-finder preset high-dividend -m spain # dividendos altos en España

# Screen personalizado
stock-finder screen -m usa \
  -f 'market_cap>10b' -f 'pe>0' -f 'pe<15' -f 'roe>0.15' \
  -s market_cap -l 20

# Descubrir campos y mercados
stock-finder fields rsi     # busca alias de campos
stock-finder markets        # mercados soportados

# Análisis técnico de uno o varios valores
stock-finder analyze AAPL NVDA -m usa           # diario
stock-finder analyze SAN -m spain -i 4h         # 4 horas
stock-finder analyze NVDA -i 1W                 # semanal
```

## Análisis técnico (`analyze`)

Muestra, por símbolo, el **rating técnico** que TradingView precalcula (resumen
global, medias móviles y osciladores) traducido a `STRONG BUY … STRONG SELL`,
más los indicadores clave interpretados (RSI, MACD, estocástico, CCI, ADX) y el
precio frente a las SMA 20/50/200.

```bash
stock-finder analyze <TICKER...> [-m mercado] [-i temporalidad] [--format json]
```

| Opción            | Valores                                             |
|-------------------|-----------------------------------------------------|
| `-m, --market`    | `usa`, `spain`, `germany`, `crypto`…                |
| `-i, --interval`  | `1m 5m 15m 30m 1h 2h 4h 1D 1W 1M` (defecto `1D`)    |
| `--format`        | `table` (defecto) o `json`                          |

> El rating es una señal automática basada en ~26 indicadores; úsalo como punto
> de partida, no como recomendación de inversión.

## Filtros (`-f`, repetible)

| Sintaxis            | Significado             | Ejemplo               |
|---------------------|-------------------------|-----------------------|
| `campo>valor`       | mayor que               | `market_cap>1b`       |
| `campo>=valor`      | mayor o igual           | `rsi>=50`             |
| `campo<valor`       | menor que               | `pe<15`               |
| `campo=valor`       | igual (texto o número)  | `sector=Technology`   |
| `campo!=valor`      | distinto                | `type!=dr`            |
| `campo:a..b`        | rango (inclusive)       | `rsi:30..70`          |
| `campo>otrocampo`   | comparar dos campos     | `close>sma200`        |

Los números aceptan sufijos: `k`, `m`, `b`, `t` (`1.5b` = 1 500 000 000).
El `campo` puede ser un **alias** (`rsi`, `market_cap`, `dividend_yield`…) o el
**nombre técnico** de TradingView (`RSI`, `market_cap_basic`…). Ver `stock-finder fields`.

## Opciones de `screen`

| Opción              | Descripción                                    |
|---------------------|------------------------------------------------|
| `-m, --market`      | Mercado: `usa`, `spain`, `germany`, `france`, `crypto`… |
| `-f, --filter`      | Filtro (repetible)                             |
| `-c, --columns`     | Columnas separadas por coma                    |
| `-s, --sort`        | Campo de ordenación                            |
| `-o, --order`       | `asc` / `desc`                                 |
| `-l, --limit`       | Número de resultados                           |
| `--offset`          | Paginación                                     |
| `--format`          | `table` (defecto), `csv`, `json`               |
| `--primary / --all-listings` | Solo listado primario (defecto) o todos los cross-listed |
| `--exclude-otc / --include-otc` | Excluir mercado OTC / pink sheets (defecto: excluir) |
| `--min-price N`     | Precio de cierre mínimo (filtra penny stocks)  |

### Saneo por defecto

Todos los screens aplican por defecto **solo listados primarios** (`is_primary`) —
elimina duplicados de un mismo valor cotizado en varias bolsas (p.ej. una acción
USA cross-listed 5 veces en bolsas alemanas)— y **excluyen OTC**. Desactívalo con
`--all-listings` / `--include-otc`. Los presets volátiles (`gainers`, `losers`,
`momentum`, `breakout`) además fijan `min_price=1` para descartar penny stocks;
sobrescríbelo con `--min-price`.

## Ejemplos

```bash
# Exportar a CSV
stock-finder screen -m usa -f 'change>5' -f 'avg_volume_10d>1m' \
  -c description,close,change,volume -s change --format csv > gainers.csv

# JSON para pipes (jq)
stock-finder preset momentum -m usa --format json | jq '.rows[].symbol'

# Cripto sobrevendida
stock-finder screen -m crypto -f 'RSI<30' -c description,close,RSI -s RSI -o asc
```

## Presets incluidos

**Valor / fundamentales:** `undervalued`, `deep-value`, `large-cap-value`,
`garp`, `high-dividend`, `quality-growth`.
**Técnicos / momentum:** `oversold`, `momentum`, `breakout`, `gainers`, `losers`.

Ejecuta `stock-finder presets` para ver filtros y descripción de cada uno.

> Unidades TradingView: `roe`, márgenes, `eps_growth`, `dividend_yield` y los
> `Perf.*` van en **porcentaje** (`roe>15` = ROE > 15 %); `pb`, `ps`,
> `debt_to_equity` y `beta` son ratios.

## Estructura

```
stock_finder/
  api.py       cliente HTTP del scanner (peticiones, reintentos)
  fields.py    catálogo de campos (alias→técnico) y mercados
  filters.py   parseo del mini-lenguaje de filtros
  presets.py   screens predefinidos
  output.py    render tabla / csv / json
  cli.py       comandos (typer)
```

## Añadir un preset

Edita `stock_finder/presets.py` y añade una entrada al dict `PRESETS` con sus
`filters`, `columns` y `sort_by`.
```
