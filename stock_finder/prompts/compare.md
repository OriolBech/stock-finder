# Comparativa y ranking — {SYMBOLS}

Compara los valores `{SYMBOLS}` (mercado `{MARKET}`) y **rankéalos** para el
objetivo indicado (por defecto: mejor relación oportunidad/riesgo para un rebote o
continuación alcista). Usa datos de la tool + websearch para el contexto.

## Pasos

1. Para cada símbolo: `analyze([...])` y, si dudas de la tendencia, `multi_timeframe(...)`.
2. Un `screen(filters=["name=<SYM>"], columns=[...])` por valor (o pídelos juntos)
   con: pe, pb, roe, net_margin, eps_growth, debt_to_equity, dividend_yield,
   change_week, change_6m, market_cap, sector.
3. **Websearch** por cada uno: catalizador reciente y riesgo principal.

## Entregable

### Tabla comparativa
Una fila por valor con las columnas clave (valoración, calidad, momentum, rating
técnico, variación reciente). Marca el mejor/peor de cada columna.

### Ranking
Ordena de más a menos atractivo **para el objetivo**, con 1-2 frases de
justificación por puesto (qué lo sube o lo baja).

### Ganador y descartados
- **Top pick:** tesis en 2-3 frases (por qué gana).
- **Descartados:** por qué caen al final (deterioro, caro, tendencia rota...).

### Matices
- Diferencias de sector/ciclo que hagan la comparación no del todo homogénea.
- No es recomendación de inversión.

## Reglas
Datos de la tool = hechos; el resto, cítalo. Unidades: roe/márgenes/crecimiento en
%, múltiplos como ratio. Si falta un dato, indícalo como "n/d".
