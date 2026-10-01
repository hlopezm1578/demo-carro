# ADR-018 — Asistente de venta con Groq: structured outputs json_schema y la key que sigue solo en el backend

- **Estado:** Aceptada
- **Fecha:** 2026-10-01
- **Resuelve:** reemplazar el proveedor del
  [ADR-017](017-asistente-ia-mini-rag-key-solo-backend.md) — Google pasó a
  exigir cuenta de facturación para crear API keys nuevas y la primera key
  devolvió un 402 real con créditos agotados (D-60 roto para el aula) —
  manteniendo intactas la muralla anti-alucinación y la key solo en el
  backend (AIAS-01, AIAS-02, AIAS-03; decisiones D-63..D-68 que superseden
  el mecanismo de ADR-017)

## Contexto

El camino de Gemini se cerró en el aula: la key del proyecto autenticó pero
su cuenta tenía créditos prepagados agotados — un 402 real de Google — y
crear keys nuevas exige hoy cuenta de facturación (evidencia firmada en el
test 2 de
[`04-UAT.md`](../../../.planning/phases/04-panel-de-administraci-n-y-asistente-ia/04-UAT.md):
el paso del alumno "key gratis sin tarjeta" quedó imposible, D-60 roto). El
usuario decidió migrar a **Groq** (D-63): key gratis sin tarjeta en
console.groq.com, Structured Outputs `json_schema` nativo con modo strict y
límites del free tier **públicos**. Nada de esto se firmó sobre supuestos:
el research de la fase instaló el SDK oficial `groq` **1.7.0** y lo ejercitó
punta a punta el 2026-10-01 — `models.list()` 200 y
`chat.completions.create` con `response_format` `json_schema` `strict: true`
→ 200 con respuesta en la voz de Maura e ids válidos del catálogo real en
`openai/gpt-oss-120b` (ver Evidencia firmada). Lo que NO cambia es la
lección: el endpoint `/api/asistente`, la burbuja, la degradación D-61 y la
muralla D-56 se mantienen; cambia UN motor.

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| **A. Quedarse en Gemini** (el mecanismo de ADR-017 con `google-genai`) | Cero rework: la mitad de integración de guia-14 ya estaba construida y verificada | El flujo del alumno quedó imposible: Google exige cuenta de facturación para keys nuevas y la key existente devolvió 402 real — una guía que no se puede ejecutar no es una guía (descartada) |
| **B. Groq con el SDK oficial `groq`** | Mismo patrón del corpus — SDK oficial como `transbank-sdk` y como fue `google-genai`: excepciones tipadas importables, retries nativos, `json_schema` strict nativo; key gratis sin tarjeta (el paso del alumno se restaura); límites públicos citables con fuente | Un segundo proveedor de IA en la vida del curso: los modelos se deprecian periódicamente y hay que aislar el nombre en una constante |
| **C. REST directo con httpx** (la API es OpenAI-compatible) | Cero dependencia de SDK; la forma de la llamada es HTTP plano | Veta el patrón del corpus (wrapper sobre SDK oficial, IN-06): sin excepciones tipadas ni retries habría que escribirlos; la OpenAI-compatibility queda como conocimiento transferible para NARRAR en clase, no como vía de implementación |

## Decisión

**Opción B.** El proveedor cambia; la muralla no (D-63..D-68):

1. **SDK oficial `groq` con pin `>=1.7,<2`**: el piso es la versión
   probe-verified (1.7.0, latest en PyPI el día del research) y el techo el
   próximo major — el mismo criterio de `transbank-sdk` y del que fue
   `google-genai >=2.25,<3`. El README del SDK no recomienda pin oficial;
   el corpus sí tiene criterio.
2. **El modelo vive en una constante del backend (D-64)**:
   `MODELO_ASISTENTE = "openai/gpt-oss-120b"`, mismo ceremonial que
   `STOCK_BAJO_UMBRAL` — nombre propio, valor fijo, respaldo de decisión.
   El `.env` del alumno queda mínimo: SOLO `GROQ_API_KEY`. Si Groq depreca
   el modelo, la constante aísla el cambio.
3. **JSON estructurado vía `response_format` `json_schema` con
   `strict: true`** y `Recomendacion` con
   `model_config = ConfigDict(extra="forbid")`: el modo strict es
   *constrained decoding* (el servicio garantiza respuesta conforme al
   schema), pero EXIGE `additionalProperties: false` y todos los campos en
   `required` — y `Modelo.model_json_schema()` de Pydantic NO emite eso
   solo (probe local, pydantic 2.13.5); `extra="forbid"` lo agrega y de
   paso endurece la validación de la vuelta. El round-trip
   Pydantic→schema→respuesta queda sellado con
   `Recomendacion.model_validate_json(...)`.
4. **`GROQ_API_KEY` en el `.env` del backend vía pydantic-settings y
   `Groq(api_key=settings.groq_api_key)` EXPLÍCITA** (D-63, IN-03
   re-firmada): el SDK auto-pickupea la env var `GROQ_API_KEY` del entorno
   ("This is the default and can be omitted", README) y NO lee el archivo
   `.env` — mismo gotcha que `google-genai`, mismo criterio
   explicit-over-implicit: la fuente de la key es `Settings`, no el entorno
   del proceso.
5. **El wrapper traduce los errores tipados, jamás un 500 crudo
   (D-61/IN-06)**: `RateLimitError` → 429 amable (cuota del free tier) y
   el resto de `GroqError` → 503 amable (incluido el caso sin key:
   `Groq()` sin `api_key` lanza `GroqError` EN LA CONSTRUCCIÓN — probe
   verificado — así que el client lazy mantiene la construcción DENTRO del
   `try`).
6. **Sin retry casero**: el SDK reintenta solo ciertos errores 2 veces por
   defecto con backoff corto — INCLUYENDO el 429, diferencia concreta con
   `google-genai`: el `RateLimitError` le llega al wrapper después de esos
   reintentos internos, y el wrapper traduce, no re-reintenta (doble-retry
   multiplicaría la presión sobre el free tier).
7. **Límites del free tier citados con fuente y "a la fecha" (D-68)**: la
   tabla pública de
   [console.groq.com/docs/rate-limits](https://console.groq.com/docs/rate-limits)
   lista `openai/gpt-oss-120b` con **30 RPM / 1.000 RPD / 8K TPM / 200K
   TPD** a la fecha de esta decisión — jamás la cifra RPD de la nota
   original, que resultó ser la fila de los modelos de moderación de esa
   misma página (Pitfall 1 del research; confirmado con los headers vivos
   de la org, `x-ratelimit-limit-requests = 1000` y
   `x-ratelimit-limit-tokens = 8000`). La página Limits de la consola es
   el pointer para los límites exactos de cada organización.
8. **La muralla D-56 queda PRESERVADA íntegra**: el system prompt de cada
   request lleva el catálogo ACTIVO completo (mini-RAG honesto), cada id
   que devuelve el modelo se valida contra la BD antes de responder y la
   respuesta se trunca a 3 cards (RN-16). Al cambiar el motor no cambian
   las murallas: lo que cambió es cómo se fuerza la forma del JSON.
9. **El riesgo de deprecación se gestiona con `models.list()` como
   herramienta de diagnóstico (D-64)**: Groq avisa "typically 30 days" por
   documentación, email y banners de consola, y los *production models*
   (donde vive `gpt-oss-120b`) no se decomisionan como los labs — la guía
   enseña a listar los modelos vigentes el día que el nombre de la
   constante deje de responder.

## Consecuencias

**Positivas**
- El paso del alumno queda restaurado: key gratis SIN tarjeta en
  console.groq.com, aislada por organización (cada alumno con su propia
  cuota) — el patrón D-60 revive con otro proveedor.
- Los límites del free tier son documentación pública y citables con
  fuente: el concern RPM/RPD que Gemini dejaba abierto (no había fuente sin
  login) muere con Groq.
- `strict: true` es *constrained decoding*: la garantía de JSON válido
  pasa a ser del servicio, y `extra="forbid"` hace doble duty (requisito
  del modo strict Y validación backend más estricta).

**Negativas (honestas)**
- Una migración ya pagada: el rework toca ADR, contrato, docs 02/03,
  READMEs y la mitad de integración de guia-14 — el costo de haber firmado
  un proveedor cuyo free tier cambió de reglas. La lección (firmar con
  evidencia) no evita el cambio de política de un tercero; lo documenta.
- Groq deprecia modelos periódicamente (30 días de aviso típico): el
  nombre del modelo es la pieza más frágil del stack — por eso vive en una
  constante y no regado por el código.
- Es el segundo proveedor de la lección en dos años de vida del curso: el
  material que hoy nombra a Groq en presente puede envejecer igual que el
  que nombraba a Gemini — el contrato 0.4.0 se dejó agnóstico
  (D-66) exactamente para que la próxima migración no vuelva a tocarlo.

## Para conversar en clase

1. El SDK cambió de proveedor, pero `contrato_api.yaml` quedó en 0.4.0 sin
   subir versión y sin nombrar a Groq. ¿Por qué el contrato describe QUÉ
   hace el endpoint y no CON QUÉ proveedor, y qué ganó la migración con
   eso?
2. De la muralla anti-alucinación (D-56): ¿qué piezas cambian al migrar de
   motor y cuáles no? (pista: el system prompt con catálogo activo y la
   validación de ids contra la BD no saben qué modelo respondió).
3. El SDK `groq` puede levantar la key del entorno solo ("default and can
   be omitted"). Si funciona solo, ¿por qué el proyecto pasa
   `api_key=settings.groq_api_key` explícita — y qué pasaría con el
   `.env` de guia-01 si confiáramos en ese auto-pickup?

## Evidencia firmada

Todo lo firmado acá descansa en la cadena doc oficial + registry + probe
runtime (disciplina D-56/D-41: no se firma sobre supuestos), verbatim en
los Patterns 1-3 y §Sources de
[`04-RESEARCH.md`](../../../.planning/phases/04-panel-de-administraci-n-y-asistente-ia/04-RESEARCH.md)
(regenerado 2026-10-01):

- **Doc oficial de límites**
  ([console.groq.com/docs/rate-limits](https://console.groq.com/docs/rate-limits),
  leída 2026-10-01): tabla verbatim `openai/gpt-oss-120b | 30 | 1K | 8K |
  200K` (RPM/RPD/TPM/TPD); los límites aplican por organización y la página
  recomienda la página Limits de la consola para los valores exactos de
  cada org.
- **Doc oficial de Structured Outputs**
  ([console.groq.com/docs/structured-outputs](https://console.groq.com/docs/structured-outputs)):
  `response_format` `json_schema` con ejemplo Pydantic
  `model_json_schema()`, modo strict como *constrained decoding*
  ("Never produces invalid JSON"), soporte limitado (GPT-OSS 20B/120B
  entre los listados) y los requisitos strict (todos los campos required +
  `additionalProperties: false`).
- **Doc oficial de deprecaciones**
  ([console.groq.com/docs/deprecations](https://console.groq.com/docs/deprecations)):
  aviso típico de 30 días por docs/email/banners; los production models no
  se someten a decommissioning como los labs.
- **Probe punta a punta SDK `groq` 1.7.0 en win32 (2026-10-01)**:
  `models.list()` 200 con 11 modelos (incluye `openai/gpt-oss-120b`);
  `chat.completions.create` con `json_schema` `strict: true` → 200 con
  productos `[1]` en la voz de Maura, 548 tokens, modelo devuelto
  `openai/gpt-oss-120b`; key inválida → `AuthenticationError` con
  `.status_code == 401`; `Groq()` sin key → `groq.GroqError` EN LA
  CONSTRUCCIÓN; headers vivos de la org con `x-ratelimit-limit-requests =
  1000` y `x-ratelimit-limit-tokens = 8000`; MROs verificados
  (`RateLimitError ⊂ APIStatusError ⊂ APIError ⊂ GroqError`). El README
  del SDK firma además el auto-pickup de `GROQ_API_KEY` ("This is the
  default and can be omitted") y los retries 2x por defecto.
- **La evidencia del cierre de Gemini**: test 2 de
  [`04-UAT.md`](../../../.planning/phases/04-panel-de-administraci-n-y-asistente-ia/04-UAT.md)
  — el 402 real de Google ("Your prepayment credits are depleted"), la
  exigencia de cuenta de facturación para keys nuevas y la decisión del
  usuario (2026-10-01) que este ADR registra.

Relacionada: [ADR-017](017-asistente-ia-mini-rag-key-solo-backend.md)
(superseded por esta — su lógica mini-RAG y degradación se mantiene
íntegra), [ADR-012](012-retorno-de-webpay.md) (el patrón del wrapper que
traduce errores del SDK y el `security: []` deliberado) y
[ADR-011](011-roles-desde-el-primer-token.md) (nada cambia en roles: el
endpoint del asistente sigue público por diseño, D-59).
