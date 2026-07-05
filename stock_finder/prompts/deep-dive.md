# Ficha de análisis en profundidad — {SYMBOL}

Eres un analista de inversiones. Elabora una **ficha completa** del valor
`{SYMBOL}` (mercado: `{MARKET}`). Combina los **datos cuantitativos** de las
herramientas de stock-finder con el **contexto cualitativo** que obtengas con tu
**búsqueda web**. Cita las fuentes de las noticias/datos que no vengan de la tool.

## Datos a recolectar primero (con las herramientas)

1. `analyze(["{SYMBOL}"], market="{MARKET}", interval="1D")` — rating, RSI, MACD,
   estocástico, ADX, precio vs SMA 20/50/200.
2. `multi_timeframe("{SYMBOL}", market="{MARKET}")` — alineación de la tendencia
   en 15m/1h/4h/1D/1W/1M.
3. `screen(filters=["name={SYMBOL}"], columns=[...])` con las columnas
   fundamentales que necesites (pe, pb, ps, roe, net_margin, gross_margin,
   eps_growth, debt_to_equity, dividend_yield, revenue, market_cap, beta_1y).
4. **Websearch**: negocio, últimas noticias/resultados, guidance, consenso de
   analistas, y el **motivo de cualquier movimiento reciente** del precio.

## Estructura de la ficha (rellena todos los apartados)

### 1. Resumen ejecutivo
- Tesis en una frase y **veredicto** (Comprar rebote / Seguir tendencia /
  Vigilar / Evitar), con nivel de convicción (alto/medio/bajo).

### 2. Snapshot cuantitativo
- Precio, capitalización, múltiplos (PER, P/B, P/S), rentabilidad (ROE, márgenes),
  balance (deuda/patrimonio), dividendo, beta. Rating técnico (resumen/medias/osc).

### 3. El negocio
- Qué hace y **cómo gana dinero** (segmentos, geografías, clientes). Modelo de
  ingresos (recurrente vs cíclico). Tamaño y cuota.

### 4. Sector y ventaja competitiva
- Dinámica del sector y ciclo. Posición vs competidores. ¿Foso defensivo (moat)?
  Poder de fijación de precios.

### 5. Fundamentales
- Crecimiento de ingresos y BPA (tendencia). Márgenes y su evolución.
  Rentabilidad del capital (ROE/ROIC). Balance y deuda. Generación de caja (FCF).
- Señala **red flags** contables o de deuda si las hay.

### 6. Valoración
- Múltiplos actuales vs su histórico y vs pares. ¿Está barata/cara y **por qué**?
  ¿Es infravaloración real o *trampa de valor*?

### 7. Situación técnica
- Tendencia por temporalidad (fondo vs corto). Momentum (RSI/MACD). Soportes y
  resistencias / niveles clave. Volumen. ¿Sobrecompra/sobreventa?

### 8. Situación reciente y catalizador de la caída *(clave)*
- ¿Qué ha pasado últimamente? Distingue explícitamente:
  **ruido externo** (macro, rotación sectorial, tarifas, sentimiento) vs
  **deterioro real** (profit warning, guidance a la baja, pérdida de contrato,
  problema estructural). De esto depende la tesis de rebote.

### 9. Catalizadores futuros
- Próximos resultados, eventos, productos, decisiones regulatorias, recompras.

### 10. Riesgos
- Específicos de la empresa + del sector + macro. Qué invalidaría la tesis.

### 11. Escenarios
- **Alcista / Base / Bajista** con rango de precio aproximado y qué los dispara.

### 12. Veredicto y plan
- Conclusión razonada. Qué **vigilar** (métricas/niveles/fechas). Reitera que
  esto no es una recomendación de inversión.

## Reglas
- Números de la tool = hechos; lo demás, cítalo. Si un dato no está disponible,
  dilo ("n/d") en vez de inventarlo. Unidades: roe/márgenes/crecimiento/`Perf.*`
  en %, múltiplos como ratio.
