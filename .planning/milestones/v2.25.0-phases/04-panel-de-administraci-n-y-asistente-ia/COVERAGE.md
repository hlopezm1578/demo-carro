# API Coverage — Groq API (SDK oficial `groq` 1.7.0, pin `>=1.7,<2`)

> Full coverage by default. Opt-outs are explicit, reasoned decisions.
>
> **Scan date:** 2026-10-01 (planner, rework plan-time — reemplaza la matriz Gemini del 2026-09-30)
> **Scan result:** el rework D-63..D-68 reemplaza el proveedor del asistente (Gemini → Groq).
> Regla del checkpoint: una segunda integración contra la misma necesidad NO hereda los opt-outs
> de la primera — cada capability se re-decide para la superficie nueva. Superficie verificada
> contra las docs oficiales de Groq (console.groq.com/docs/structured-outputs y /rate-limits) +
> probe punta a punta del SDK 1.7.0 en win32 (2026-10-01: models.list 200 con 11 modelos;
> chat.completions con json_schema strict 200, voz de Maura e ids válidos en
> openai/gpt-oss-120b; AuthenticationError 401 con key inválida; Groq() sin key → GroqError en
> construcción; headers vivos x-ratelimit-limit-requests=1000). La matriz Gemini anterior queda
> como historia en el git de este archivo.

| capability | decision | reason |
|---|---|---|
| `client.chat.completions.create` (texto) | INTEGRATE | el corazón del asistente: la recomendación de la asesora (AIAS-01) |
| structured outputs (`response_format` `json_schema` con `strict: true`) | INTEGRATE | la respuesta `{respuesta, productos}` conforme al schema `Recomendacion` con `extra="forbid"` — constrained decoding, probe-verified (D-63/Pitfall 2) |
| API key por Settings explícita (env var `GROQ_API_KEY`) | INTEGRATE | D-63/AIAS-03 + IN-03: pydantic-settings lee el `.env` y la key se pasa EXPLÍCITA a `Groq(api_key=...)` — el auto-pickup del SDK queda documentado como gotcha (no lee .env) |
| manejo de errores tipados (`RateLimitError`, `GroqError` y subclases) | INTEGRATE | wrapper que traduce 429 (cuota) y resto (construcción sin key/red/timeout/servicio) a respuestas amables — jamás un 500 crudo (D-61, patrón IN-06) |
| retries nativos del SDK (2x, connection/408/409/429/5xx, backoff corto) | INTEGRATE | de forma pasiva: se documentan como comportamiento del SDK (incluye el 429 — diferencia con google-genai); el wrapper NO duplica el retry |
| `client.models.list()` (GET /models) | INTEGRATE | mini-exploración de diagnóstico ante deprecación de modelos (D-64 — probado 200 en el probe; Groq avisa típicamente 30 días) |
| streaming (`stream: true` / SSE) | OPT-OUT | D-57: respuesta única request-response — el streaming es una idea diferida explícita de CONTEXT |
| sesiones/historial server-side | OPT-OUT | D-58: multi-turno stateless — el historial vive en el frontend y viaja en cada request; cero tablas nuevas |
| embeddings / vector store | OPT-OUT | mini-RAG honesto por system prompt con el catálogo activo completo (D-56); "motor ML de recomendación propio" figura en Out of Scope de REQUIREMENTS.md |
| function calling / tools | OPT-OUT | fuera del objetivo pedagógico de la etapa (la validación de ids contra BD reemplaza cualquier herramienta) |
| multimodal (imágenes/audio/vídeo) | OPT-OUT | el asistente es texto sobre el catálogo; las product cards las arma el backend con la BD |
| token counting / batch | OPT-OUT | no requerido; los topes de largo (500/10, RN-16) acotan tokens por diseño |
| moderación (`meta-llama/llama-prompt-guard-2-*`) | OPT-OUT | no requerido — nota D-68: la fila "30 RPM / 14.400 RPD" de la tabla pública es de ESTOS modelos, no del asistente |
| generación asíncrona / files / tuning | OPT-OUT | no requeridos por la guía |

Notas de cobertura:

- **`chat.completions` + json_schema strict + errores tipados es el corazón del rework**
  (AIAS-01/02/03): se enseña en guia-14 reescrita (plan 04-07, `services/asistente.py` ÚNICO
  importador del SDK — patrón de `services/webpay.py` en guia-09) con la evidencia firmada por
  04-RESEARCH.md (docs oficiales + probe SDK 1.7.0 del 2026-10-01).
- **`models.list` pasa de OPT-OUT (matriz Gemini) a INTEGRATE**: D-64 añade la mini-exploración
  como herramienta de diagnóstico de deprecación — re-decisión explícita, no herencia.
- **La validación de ids contra BD (D-56) NO es capability del SDK**: es la muralla
  anti-alucinación del backend — cubierta por diseño propio, citada aquí para que no se busque
  del lado del proveedor.
- **El modelo**: `openai/gpt-oss-120b` como constante `MODELO_ASISTENTE` (D-64); qwen/qwen3.8-27b
  verificado también en el probe, queda como ejemplo de exploración.
- **Los límites del free tier SON públicos** (cierre del concern de STATE.md): 30 RPM /
  1.000 RPD / 8K TPM / 200K TPD para gpt-oss-120b a la fecha — la guía los cita con URL y "a la
  fecha" (D-68); jamás "14.400 RPD".
