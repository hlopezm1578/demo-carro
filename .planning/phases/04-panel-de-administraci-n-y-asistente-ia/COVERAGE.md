# API Coverage — Google Gemini API (SDK oficial `google-genai` 2.25.0, pin `>=2.25,<3`)

> Full coverage by default. Opt-outs are explicit, reasoned decisions.
>
> **Scan date:** 2026-09-30 (planner, plan-time)
> **Scan result:** la fase 4 integra la Gemini API vía el SDK oficial `google-genai`
> (segundo servicio externo real del proyecto, después de Webpay en fase 3). El detector
> de scope corrió sin input (roadmap query vacía → `skipped/no_input`), pero la integración
> es un hecho lock-eado por el usuario: D-56/D-60/D-61 (04-CONTEXT.md) y el constraint de
> PROJECT.md (Gemini vía `google-genai`, key solo en backend). Superficie verificada contra
> el README del SDK en el tag exacto `v2.25.0` (04-RESEARCH.md Patterns 1-3, fetched
> 2026-09-30). Este archivo se produce en plan time para el gate `api-coverage.verify-pre`.

| capability | decision | reason |
|---|---|---|
| `client.models.generate_content` (texto) | INTEGRATE | el corazón del asistente: la recomendación de la asesora (AIAS-01) |
| structured output (`response_json_schema`) | INTEGRATE | la respuesta `{respuesta, productos}` conforme al schema Pydantic `Recomendacion`, vía `response_mime_type='application/json'` + `response_json_schema` — D-56 exige exactamente la forma documentada en el README v2.25.0 (no `response_schema`, Pitfall 2) |
| API key por env var (`GEMINI_API_KEY` auto-pickup del Client) | INTEGRATE | D-60/AIAS-03: key en el `.env` del backend vía pydantic-settings; el Client la levanta solo |
| manejo de errores tipados (`errors.APIError` con `.code`/`.message`) | INTEGRATE | wrapper que traduce 429 (cuota) y resto (red/timeout/servicio) a respuestas amables — jamás un 500 crudo (D-61, patrón IN-06) |
| retries nativos del SDK (transitorios 4x, ~1s→60s) | INTEGRATE | de forma pasiva: se documentan como comportamiento del SDK; el wrapper NO duplica el retry (anti-pattern: doble-retry presiona el free tier) |
| streaming (`generate_content_stream` / SSE) | OPT-OUT | D-57: respuesta única request-response — el streaming es una idea diferida explícita de CONTEXT |
| sesiones/historial server-side (módulo chats) | OPT-OUT | D-58: multi-turno stateless — el historial vive en el frontend y viaja en cada request; cero tablas nuevas |
| embeddings / vector store | OPT-OUT | mini-RAG honesto por system prompt con el catálogo activo completo (D-56); "motor ML de recomendación propio" figura en Out of Scope de REQUIREMENTS.md |
| function calling / tools | OPT-OUT | fuera del objetivo pedagógico de la etapa (la validación de ids contra BD reemplaza cualquier herramienta) |
| multimodal (imágenes/audio/vídeo) | OPT-OUT | el asistente es texto sobre el catálogo; las product cards las arma el backend con la BD |
| token counting / batch | OPT-OUT | no requerido; los topes de largo (500/10, RN-16) acotan tokens por diseño |
| Interactions API (`client.interactions.create` + `response_format`) | OPT-OUT | ausente del README del pin 2.x — es el patrón de las docs web actuales; la guía narra el drift como lección (Pitfall 1) pero enseña el patrón del pin |
| listado de modelos / tuning / files | OPT-OUT | no requeridos por la guía |

Notas de cobertura:

- **`generate_content` + structured output + errores es el corazón de la fase** (AIAS-01/02/03):
  se enseña en guia-14 (`services/asistente.py`, ÚNICO importador del SDK — patrón de
  `services/webpay.py` en guia-09) con la evidencia firmada por 04-RESEARCH.md contra el
  README @ v2.25.0 (misma lección de D-41: no se firma sobre supuestos).
- **La validación de ids contra BD (D-56) NO es capability del SDK**: es la muralla
  anti-alucinación del backend (Pattern 6) — cubierta por diseño propio, citada aquí para
  que no se busque del lado del proveedor.
- **El modelo**: alias `gemini-flash-latest` (modelo de ejemplo del README v2.25.0; los
  alias avisan breaking changes con 2 semanas) con `gemini-3.8-flash` como alternativa
  concreta estable — decisión del planner registrada en 04-04-PLAN.md.
- **Los límites RPM/RPD del free tier NO son públicos sin login** (verificado contra
  ai.google.dev/gemini-api/docs/rate-limits — concern abierto de STATE.md): la guía enseña
  el 429 sin prometer cifras.
