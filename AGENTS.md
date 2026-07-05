# stock-finder — guía para agentes (LLM)

Esta herramienta aporta **datos cuantitativos** de mercado (screening + análisis
técnico de TradingView). Tú, el agente, aportas el **contexto cualitativo**: usa
tu búsqueda web para averiguar *por qué* se mueve un valor (noticias, resultados,
guidance, sector) antes de concluir nada.

## Cómo llamarla

Dos vías equivalentes; ambas devuelven JSON:

- **CLI:** cualquier comando con `--format json`.
- **MCP:** herramientas `screen`, `run_preset`, `analyze`, `multi_timeframe`,
  `list_presets`, `list_fields`, `list_markets`.

## Flujo recomendado (rebotes / infravaloradas)

1. **Filtra candidatos** con un preset o un screen:
   - `run_preset("pullback")` → recortes sanos en tendencia alcista.
   - `run_preset("undervalued")` / `run_preset("dip-value")` → valor / valor+caída.
   - o `screen(filters=[...])` a medida.
2. **Confirma la estructura técnica** de los que te interesen:
   - `multi_timeframe("WDC")` → ¿la tendencia de fondo (1D/1W/1M) sigue alcista
     pese al recorte de corto plazo? Señala trampas vs. pullbacks.
   - `analyze(["WDC","STLD"])` → RSI, MACD, medias, rating.
3. **Investiga el "porqué" con tu websearch** para CADA candidato:
   - ¿La caída es por *ruido* externo (macro, rotación sectorial, tarifas) o por
     *deterioro real* (profit warning, guidance a la baja, fraude, demanda)?
   - Un pullback sano = negocio intacto + caída por causa externa/temporal.
4. **Sintetiza**: combina la señal cuantitativa (tendencia + fundamentales) con la
   causa cualitativa. Descarta los que cayeron por deterioro del negocio.

## Reglas de filtros (`screen`)

`campo op valor`, repetible. Operadores: `>` `>=` `<` `<=` `=` `!=`, rango
`campo:a..b`, y campo-vs-campo `close>sma200`. Sufijos numéricos `k m b t`.

**Unidades (importante):** `roe`, `net_margin`, `gross_margin`, `eps_growth`,
`dividend_yield` y los `Perf.*` van en **porcentaje** (`roe>15` = ROE > 15 %).
`pe`, `pb`, `ps`, `debt_to_equity`, `beta` son ratios. Usa `list_fields` para el
mapa completo alias → nombre técnico; `type=stock` excluye ETFs/fondos.

## Saneo por defecto

`screen`/`run_preset` aplican por defecto: solo listado primario (sin duplicados
cross-listed), sin OTC. Los ratings `Recommend.*` van en `[-1, 1]`
(≥0.5 STRONG BUY, ≥0.1 BUY, >-0.1 NEUTRAL, >-0.5 SELL, resto STRONG SELL).

## Aviso

Son señales automáticas, no recomendaciones de inversión. Verifica siempre la
causa real antes de concluir.
