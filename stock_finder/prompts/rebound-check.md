# Veredicto rebote vs. trampa — {SYMBOL}

El valor `{SYMBOL}` (mercado `{MARKET}`) ha caído recientemente. Determina si es un
**recorte sano en tendencia alcista** (candidato a rebote / seguir subiendo) o una
**trampa** (caída por deterioro real del negocio). Sé conciso y decídete.

## Pasos

1. `multi_timeframe("{SYMBOL}", market="{MARKET}")` — ¿la tendencia de fondo
   (1D/1W/1M) sigue alcista aunque el corto (15m/1h) corrija?
2. `analyze(["{SYMBOL}"], market="{MARKET}")` — RSI (¿sobreventa?), MACD, y precio
   frente a SMA200 (¿sigue por encima = tendencia intacta?).
3. `screen(filters=["name={SYMBOL}"], columns=["pe","roe","debt_to_equity","net_margin","eps_growth","change_week","change_6m"])`
   — ¿fundamentales sanos? ¿sigue positivo a 6 meses?
4. **Websearch**: ¿por qué ha caído? Busca noticias/resultados de los últimos días.

## Entregable (formato fijo)

- **Causa de la caída:** [ruido externo | deterioro real | mixto] — 1-2 frases con fuente.
- **Tendencia de fondo:** [intacta / debilitándose / rota] — según medias y multi-TF.
- **Fundamentales:** [sanos / mixtos / deteriorados] — 3-4 métricas clave.
- **Momentum/entrada:** RSI y nivel técnico relevante (soporte cercano).
- **Veredicto:** [Rebote probable / Seguir tendencia / Esperar confirmación / Evitar]
  con nivel de convicción y **qué señal confirmaría** la tesis.
- **Riesgo principal** que invalidaría el rebote.

Recuerda: la señal cuantitativa detecta la *huella* del pullback; el *porqué* solo
lo confirma la noticia. No es recomendación de inversión.
