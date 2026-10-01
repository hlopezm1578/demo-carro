# Phase 4: Panel de administración y asistente IA - Research

**Researched:** 2026-10-01 (REGENERACIÓN — rework Gemini→Groq, D-63..D-68; reemplaza el research del 2026-09-30)
**Domain:** Documentación de guía educativa (guide-only) — panel admin FastAPI+React protegido por rol (EJECUTADO y verificado) + asistente IA con Groq (SDK `groq`, Structured Outputs `json_schema`, mini-RAG)
**Confidence:** HIGH

> **Regla de suelo del repo (D-17, ADR-008):** este repositorio es **guide-only** — la fase entrega **DOCUMENTOS** (contrato, ADRs, docs 02/03, guías, READMEs), no código de aplicación. Todo "code example" de este research es material para los **bloques de código que el alumno copia** dentro de las guías. Esta regeneración NO reabre la fase completa: la mitad PANEL (guias 12/13, contrato 0.4.0, ADRs 015/016, docs 02/03) ya está ejecutada y verificada (22/25, UAT delegado 4/5) — ese conocimiento se PRESERVA abajo marcado como *carried over*. Lo nuevo es la mitad de INTEGRACIÓN del asistente: **todo lo que decía Gemini/google-genai queda reemplazado por hallazgos Groq firmados con evidencia fresca (2026-10-01, URL + probe punta a punta con SDK `groq` 1.7.0)**.

## Summary

La fase 4 entregó las dos peticiones P7/P8 (panel admin ADMN-01..04 + asesora AIAS-01..03) en 5 planes, guías 12-15 y 17 ADRs. El camino Gemini se cerró en el aula: Google exige cuenta de facturación para crear keys nuevas y la primera key del usuario devolvió un 402 real con créditos agotados (04-UAT.md test 2) — D-60 roto. El usuario decidió **Groq** (D-63..D-68) y este research valida esa decisión con evidencia de primera mano: el SDK oficial `groq` **1.7.0** (latest en PyPI) fue instalado en un venv desechable y ejercitado punta a punta contra api.groq.com — `models.list()` 200, `chat.completions.create` con `response_format` `json_schema` y **`strict: true`** → 200 con respuesta en la voz de Maura e ids válidos del catálogo real en `openai/gpt-oss-120b` (548 tokens), excepciones tipadas importables y `AuthenticationError` con `.status_code == 401` reproducida con key inválida.

**Hallazgo material nº 1 (D-68 — disciplina firmar-con-evidencia):** la nota del usuario citaba "free tier 30 RPM / 14.400 RPD", pero la tabla pública oficial de límites (console.groq.com/docs/rate-limits, leída 2026-10-01) lista `openai/gpt-oss-120b` con **30 RPM / 1.000 RPD / 8K TPM / 200K TPD** — el par "30 / 14.4K" existe en esa tabla SOLO para los modelos de moderación `meta-llama/llama-prompt-guard-2-*`, y el header `x-ratelimit-limit-requests: 14400` que muestra la propia página es un ejemplo "illustrative". Confirmación independiente: los headers VIVOS de la org del usuario (probe `with_raw_response`) devuelven `x-ratelimit-limit-requests = 1000` y `x-ratelimit-limit-tokens = 8000`, calzando exacto con la tabla. **La guía debe citar 30 RPM / 1.000 RPD (8K TPM / 200K TPD) con fuente y "a la fecha de esta guía"** — D-68 ya ordena citar lo que la doc dice, jamás firmar sobre supuestos.

**Hallazgo material nº 2:** la sintaxis exacta que la guía enseñará quedó firmada DOS veces (doc oficial + probe local): `response_format={"type": "json_schema", "json_schema": {"name": ..., "strict": True, "schema": <draft 2020-12>}}`. Con `strict: true` Groq hace *constrained decoding* (respuesta SIEMPRE conforme al schema) y `openai/gpt-oss-120b` está en la lista de modelos con soporte — pero el modo strict exige `additionalProperties: false` en cada objeto, y `Modelo.model_json_schema()` de Pydantic NO lo emite por defecto (probe local: pydantic 2.13.5) — `model_config = ConfigDict(extra="forbid")` lo agrega y ambos campos ya nacen en `required`. El round-trip Pydantic→schema→respuesta queda sellado.

**Hallazgo material nº 3 (IN-03):** el SDK `groq` auto-pickupea `GROQ_API_KEY` del entorno ("This is the default and can be omitted" — README) pero NO lee el archivo `.env` (recomienda python-dotenv aparte). La cláusula IN-03 se traslada intacta: pydantic-settings carga el `.env` → `Settings.groq_api_key` → `Groq(api_key=...)` explícita. Y la degradación D-61 queda firmada: `Groq()` sin key lanza `groq.GroqError` EN LA CONSTRUCCIÓN ("The api_key client option must be set...") — el client lazy de guia-14 sigue siendo el patrón correcto, con la construcción DENTRO del try.

**Primary recommendation:** Rework en el orden que D-62/D-63 ya fijan: ADR-018 (supersede ADR-017) + reescritura de la mitad de integración de guia-14 con el patrón probe-verified (`from groq import Groq`, json_schema strict, `RateLimitError` → 429 amable, resto → 503 amable), ajustes puntuales de guia-15 (fila 8 + grep `GROQ_API_KEY`), contrato 0.4.0 agnóstico (D-66), barrido de las menciones Gemini en 12 archivos (D-67) y re-verificación del UAT test 2 — el taller ya tiene `GROQ_API_KEY` en el `.env` y el probe de este research es la receta exacta (con la nota truststore de la máquina del taller).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

*(Copiadas verbatim de `04-CONTEXT.md` — numeración D-50..D-68, continúa de fases 1-3; D-63..D-68 son las del rework Groq 2026-10-01)*

#### Máquina de estados de pedidos (ADMN-03)
- **D-50:** **Los 4 estados existentes (PENDING / PAID / CANCELLED / REJECTED) — sin estados nuevos.** Nada de "enviado/entregado": la logística física es Out of Scope del proyecto. La máquina de estados completa se documenta con sus transiciones legales y quién puede ejecutar cada una (el flujo de pago posee las suyas; el admin tiene exactamente UNA transición manual): **PENDING→CANCELLED** — la gestión de órdenes huérfanas que D-48/D-49 dejaron explícitamente para esta fase. Cancelar una PENDING no toca stock (D-35: el stock solo se descuenta al aprobar el pago), así que la transición es limpia. **PAID es terminal en v1** — el refund es ADMN-05, diferido a v2. El backend valida la transición pedida contra la máquina (rechaza las ilegales; código exacto a discreción del contrato) — **Reversibility:** costly — el contrato 0.4.0, la RN nueva, el ADR y las guías se estructuran alrededor de qué transiciones existen y quién las ejecuta.

#### CRUD de productos (ADMN-01)
- **D-51:** **Imágenes como campo de ruta editable (texto), sin upload de archivos.** El admin edita la ruta (`/products/{sku}.jpg`); no hay multipart ni guardado de archivos. `python-multipart` ya llega en `fastapi[standard]`, pero el upload (multipart, disco, validación de tipo/tamaño) es infraestructura sin lección nueva: el seed ya provee las fotos (D-08) y el alumno las descargó en fase 1. Upload real queda como idea diferida.
- **D-52:** **Soft delete visible y reversible en el panel.** El listado de productos marca activo/inactivo; el admin puede reactivar un producto inactivo con un toggle. Los inactivos desaparecen del catálogo público y de las fichas, pero los pedidos viejos siguen mostrando su snapshot de nombre/precio (D-36) — la lección honesta del soft delete ya diseñado en docs/03 §2.3.5: "un pedido viejo no puede quedar apuntando a un producto borrado".

#### Alerta de stock bajo (ADMN-02)
- **D-53:** **Umbral fijo por constante del backend** (propuesto: stock ≤ 5; valor final a discreción), fijado como RN nueva. Superficie de la alerta: badge por producto en el listado admin + contador de productos con stock bajo en métricas (D-54). Sin UI para configurar el umbral — sería una capacidad nueva fuera de ADMN-02.

#### Métricas del panel (ADMN-04)
- **D-54:** **Cuatro KPIs en tarjetas + tabla (sin gráficos, locked por requisito):** (1) ingresos totales = suma de órdenes PAID, (2) pedidos por estado (los 4), (3) top 5 productos por unidades vendidas, (4) cantidad de productos con stock bajo (umbral D-53). Todo computable desde las tablas existentes (pedidos + líneas snapshot). **El endpoint demo `/api/admin/estado` (D-33) se reemplaza por el endpoint real de métricas en el contrato 0.4.0**: cumplió su lección de fase 2 (dependencia de seguridad con claim de rol) y la guía narra la evolución — **Reversibility:** costly — cambia un path publicado en 0.3.0 que las guías 05/06 construyeron; la subida a 0.4.0 lo documenta.

#### Panel en la SPA
- **D-55:** **Ruta `/admin` con sub-rutas bajo un layout propio del panel** (propuesta: productos, pedidos, métricas; estructura exacta a discreción), protegida por un guard por rol — RequireAdmin que reusa el patrón RequireAuth + returnTo (D-32) sumando el claim de rol desde el primer token (ADR-011). El link "Panel" en el navbar solo es visible con rol admin; una clienta que fuerza `/admin` ve una página de no autorizado — el espejo frontend del 403 que D-33 enseñó en backend.

#### Asistente IA: estrategia mini-RAG (AIAS-02)
- **D-56:** **Retrieval trivial y honesto: el catálogo activo completo va en el system prompt de cada request** (12 SKU: id, nombre, familia aromática, notas, precio — cabe entero). Gemini responde **JSON estructurado** (texto de recomendación + ids de productos citados); **el backend valida cada id contra la BD** antes de responder y arma las product cards que el chat muestra clicables (AIAS-02 palabra por palabra). Sin embeddings ni vector store: el catálogo real cabe completo y el Out of Scope ya veta el motor de recomendación propio. La forma exacta de forzar JSON en google-genai 2.25 (`response_mime_type`/`response_schema` o equivalente) **la valida el research contra la doc oficial — no se firma sobre supuestos** (misma lección que D-41 con el spike de Webpay) — **Reversibility:** costly — define el contrato del endpoint de chat, el schema de respuesta y la estructura de las guías. **[Rework 2026-10-01: la muralla mini-RAG (prompt + validación de ids + truncado a 3) se MANTIENE íntegra; el mecanismo de JSON estructurado pasa a `response_format` `json_schema` de Groq, ya verificado punta a punta — D-63.]**

#### Conversación del chat (AIAS-01)
- **D-57:** **Respuesta única request-response, sin streaming.** La lección es la integración del servicio externo y su contrato, no SSE/streaming de tokens.
- **D-58:** **Multi-turno stateless: el frontend mantiene el historial visible y lo envía en cada request.** El backend no guarda conversaciones en BD ni estado de sesión del chat — cero tablas nuevas para el asistente.
- **D-59:** **Endpoint público, sin login** — la asesora atiende a quien navega la tienda (P8: "recomiende aromas del catálogo a cada clienta, como lo haría Maura en persona"), como `/api/pago/retorno` ya es público por diseño. Salvaguardas básicas de input (largo máximo de mensaje y del historial enviado) protegen el free tier. La burbuja flotante vive en el layout de la tienda (visible en las páginas públicas), con panel de chat desplegable — la forma exacta a discreción del UI.

#### API key y degradación (AIAS-03)
- **D-60:** **Cada alumno crea SU PROPIA API key gratis en Google AI Studio** — paso del alumno dentro de la guía (mismo patrón que D-08 con las fotos: nada compartido por el proyecto), sin tarjeta de crédito. `GEMINI_API_KEY` vive en el `.env` del backend vía pydantic-settings, como `secret_key` en fase 2 — jamás en código ni en el frontend. **[ROTO 2026-10-01: Google exige cuenta de facturación para crear keys nuevas — el flujo del alumno quedó imposible para el aula. SUPERSEDED por D-63: el PATRÓN (key propia del alumno, gratis, sin tarjeta) se mantiene con console.groq.com y `GROQ_API_KEY`.]**
- **D-61:** **Sin key la app arranca normal (degradación, NO fail-fast)** — el asistente es un servicio opcional, a diferencia de `secret_key`: sin key el endpoint responde **503 con mensaje amable** y la burbuja muestra "asistente no disponible"; la tienda sigue 100% operativa. La guía enseña el manejo de errores del servicio externo: **429** (cuota del free tier), timeout / error de red de Gemini → mensaje amable + reintentar (el wrapper atrapa los errores del SDK, jamás un 500 crudo — mismo patrón que IN-06 con `TransbankError`). **AIAS-03 se verifica con grep sobre el build del frontend** (`dist/`) buscando la key sin resultados — pieza fija de la Gran verificación final de la fase.

#### Partición de la fase
- **D-62:** **Orden de construcción: contrato 0.4.0 + ADRs primero (D-15), luego panel admin completo (backend → frontend), después asistente IA (backend → burbuja frontend), cerrando con la Gran verificación final de fase 4.** El admin va antes que la IA: el panel no depende del asistente, y la burbuja reusa las product cards del catálogo ya existentes. La partición exacta en sub-guías `guia-12+` es discreción del planner bajo este orden.

#### Rework 2026-10-01: reemplazo de Gemini por Groq (D-63..D-68)

*Base factual: decisión del usuario registrada en `04-UAT.md` test 2 (Google exige cuenta de facturación → D-60 roto; 402 real con créditos agotados) y probe punta a punta de Groq (models 200 + json_schema 200 con voz de Maura e ids válidos en `openai/gpt-oss-120b` y `qwen/qwen3.8-27b`). D-57/D-58/D-59/D-61 y la muralla D-56 se mantienen intactas.*

- **D-63:** **Proveedor Groq con SDK oficial `groq`** — mismo patrón del corpus (SDK oficial como `transbank-sdk` y como fue `google-genai`): `from groq import Groq`, `client.chat.completions.create(...)` forzando JSON con `response_format` `json_schema` (shape `Recomendacion {respuesta, productos}`). El wrapper de guia-14 atrapa las excepciones tipadas del SDK (`RateLimitError` → 429 amable, el resto → 503 amable, jamás 500 — D-61 intacto). El paso del alumno se traslada: SU PROPIA key gratis SIN tarjeta en console.groq.com (`GROQ_API_KEY` en el `.env` del backend vía pydantic-settings). La cláusula IN-03 se mantiene con el nuevo SDK: `api_key` explícita desde Settings, no auto-pickup del entorno (el SDK `groq` también auto-pickupea — mismo gotcha, el ADR-018 lo dice). El research valida pin de versión y sintaxis exacta contra la doc oficial — **Reversibility:** costly — reescribe la mitad de integración de guia-14, agrega ADR-018 y dispara el barrido D-67.
- **D-64:** **Modelo por defecto `openai/gpt-oss-120b` como constante del backend** (`MODELO_ASISTENTE`), mismo patrón que `STOCK_BAJO_UMBRAL=5` en guia-12: constante con nombre y respaldo de requerimiento. El `.env` del alumno queda mínimo: solo `GROQ_API_KEY`. La guía advierte el riesgo de deprecación de modelos (🧠: Groq depreca periódicamente) e incluye mini-exploración `GET /models` (probado 200 en el probe) como herramienta de diagnóstico.
- **D-65:** **Narrativa limpia con nota breve: guia-14 se reescribe como si Groq siempre hubiera sido, abriendo con un blockquote breve (≈5 líneas) que narra el swap y apunta a ADR-018** — mismo patrón honesto de guia-12 con el retiro de `/api/admin/estado` (D-54). El registro completo del cambio (402 real, exigencia de billing, probe Groq) vive en **ADR-018, que supersede ADR-017**; ADR-017 solo recibe la marca de superseded, cuerpo byte-intacto.
- **D-66:** **El contrato queda 0.4.0 AGNÓSTICO del proveedor: las 8 menciones a Gemini en `contrato_api.yaml` se reescriben sin nombrar proveedor** ("el servicio de IA", "cuota del free tier consumida", "sin la API key del asistente en el `.env`") y la versión NO sube. El contrato describe QUÉ hace el endpoint, no CON QUÉ proveedor: una migración futura no vuelve a tocar el yaml, y el bump artificial a 0.4.1 se evita (0.4.0 nunca salió por separado — se construyó completo en guias 12-15). El paréntesis "sin cifras de límites (no son públicos sin login)" muere con Groq (D-68). Cero churn en guia-12 y en la fila contrato ↔ `/docs` de la Gran verificación final — **Reversibility:** costly — reescribe descripciones publicadas del yaml 0.4.0.
- **D-67:** **Barrido COMPLETO del corpus: las 64 menciones a Gemini/google-genai en 12 archivos se actualizan** (guias 12-15, contrato, ADRs, docs/02/03, READMEs de docs y raíz, índice de ADRs): el alumno nunca lee "asesora Gemini" en un documento vigente. ADR-002 también se toca (2 líneas: describe el sistema vigente, no un momento histórico); ADR-017 es la única excepción (marca de superseded, cuerpo intacto). El taller `maura-uat` ya quedó con `GROQ_API_KEY` (GEMINI removida); el UAT test 2 se re-verifica tras el rework — **Reversibility:** costly — toca 12 archivos del producto.
- **D-68:** **Cifras del free tier: la guía las cita con fuente, la RN no.** Guía/🧠 del 429 citan **30 RPM / 14.400 RPD** con link a las docs de límites de Groq y "a la fecha de esta guía" (el research las valida contra la fuente oficial antes de fijarlas — disciplina firmar-con-evidencia de D-56). RNF-08 queda estable SIN números: "degrada amable ante cuota consumida; los límites exactos son los documentados públicamente por el proveedor". Cierra el concern RPM/RPD de STATE.md (moría con Gemini; Groq los publica). **[VALIDACIÓN DEL RESEARCH 2026-10-01: la doc oficial DICE OTRA COSA — `openai/gpt-oss-120b` sale con 30 RPM / 1.000 RPD / 8K TPM / 200K TPD; "14.4K" solo aparece para los modelos prompt-guard. Ver Open Question 1: la guía cita lo que la doc dice.]**

### Claude's Discretion
- Nombres y estructura exacta de los endpoints nuevos al extender `contrato_api.yaml` a 0.4.0 (tag Administración: `/api/admin/productos*`, `/api/admin/pedidos*`, `/api/admin/metricas`; tag Asistente: `/api/asistente` vs `/api/chat`; schemas ProductoCrear/ProductoEditar/PedidoTransicion/Metricas/ChatMensaje).
- Qué ADRs escribe la fase y su título exacto, continuando desde ADR-015.
- Numeración nueva de RF/RNF/RN/HU en `02_requerimientos.md` (series: RF-19, RNF-08, RN-14, HU-12) y pantallas 10+ de `03_diseno.md`.
- Valor exacto del umbral de stock bajo (D-53 propone ≤ 5) y superficie del badge.
- Schema exacto de la respuesta JSON del asistente y forma de forzarlo (el research lo valida; D-56 fija que existe la validación).
- Estructura de sub-rutas del panel y del layout admin (D-55 fija `/admin` + guard; los paths internos son libres).
- Código HTTP para transición ilegal de pedidos (409 vs 422) y demás detalles finos del contrato.
- Copys del panel, la burbuja y los estados vacíos; la voz de la asesora conecta con la persona de Maura (D-02).
- Cómo se parte el trabajo en sub-guías `guia-12+` respetando el orden D-62, y qué incluye la Gran verificación final además del grep del build.

### Claude's Discretion (rework Groq)
- Pin de versión del SDK `groq` y sintaxis exacta de `response_format` `json_schema` (el research las valida contra la doc oficial — D-56/D-63 exigen firmar con evidencia, no supuestos).
- Wording agnóstico exacto de las 8 descripciones del yaml (D-66 fija el principio; las palabras concretas son libres).
- Estructura interna y título de ADR-018 (qué secciones de ADR-017 se re-narran, cuánta evidencia del 402/billing se cita).
- Cuáles mini-verificaciones de guia-14 cambian de texto (la de versión del SDK, la de json_schema ya probada en el probe) y la nota 🧠 OpenAI-compatible como conocimiento transferible.
- Re-escritura exacta de RNF-08/09 (docs/02) y de la entidad GEM/DFD 15.0 (docs/03) manteniendo las series sin renumerar.
- Si la actualización de los documentos vivos del proyecto (`.planning/PROJECT.md` constraints/Key Decisions de IA, nota groq en `.planning/research/STACK.md`) va dentro del rework o al cierre de fase (transición) — ambos son válidos mientras no queden diciendo Gemini al partir la fase 5.
- Cómo se re-verifica el UAT test 2 y se cierra la verificación de fase (los backstops de concurrencia AIAS-03 ya tienen evidencia parcial del probe; el planner decide la secuencia).

### Deferred Ideas (OUT OF SCOPE)
- **Upload de imágenes de producto desde el panel** (multipart + guardado en disco) — fuera de ADMN-01 por D-51; candidato natural para v2 si el curso lo pide.
- **Refund/anulación de pago PAID desde el panel** — ya está en REQUIREMENTS v2 como ADMN-05; D-50 lo deja explícitamente fuera.
- **Gráficos en las métricas del panel** — ya está en v2 como STAKE-04; ADMN-04 fija tarjetas + tabla.
- **Streaming de la respuesta del chat** — descartado por D-57 para esta fase; sería una adición posterior sobre el mismo endpoint.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ADMN-01 | Admin hace CRUD de productos con soft delete | **EJECUTADO/verificado (UAT fila 3/5)** — carried over del research original: `activo` en PRODUCTO, allow-list ProductoEditar, snapshot protege pedidos viejos |
| ADMN-02 | Admin gestiona stock con alerta de stock bajo | **EJECUTADO/verificado (UAT fila 4 + test 3)** — `STOCK_BAJO_UMBRAL=5` backend + espejo frontend; dos umbrales distintos (admin vs tienda) ratificado runtime |
| ADMN-03 | Admin gestiona pedidos con transiciones validadas en backend | **EJECUTADO/verificado (UAT fila 6 + test 3)** — UPDATE condicional PENDING→CANCELLED, 409 "Ese pedido ya no está en curso." |
| ADMN-04 | Admin ve métricas (tarjetas + tabla, sin gráficos) | **EJECUTADO/verificado (UAT fila 7 + test 3)** — 4 KPIs calzados contra BD real |
| AIAS-01 | Cliente usa chat (burbuja) donde el asistente recomienda productos del catálogo real | Burbuja + `POST /api/asistente` YA construidos (UAT filas 8/10/11); el rework solo cambia el proveedor detrás del service. Endpoint público `security: []`, request-response, multi-turno stateless (D-57/D-58/D-59 intactos) |
| AIAS-02 | Asistente responde solo con productos existentes (mini-RAG + validación ids BD) + product cards clicables | Muralla D-56 INTACTA; mecanismo de JSON firmado para Groq: `response_format` `json_schema` con `strict: true` probe-verified en `openai/gpt-oss-120b` (voz de Maura, ids válidos, 548 tokens) — ver Pattern 1 y Code Examples |
| AIAS-03 | La API key vive solo en el backend (variable de entorno), nunca en el código ni el bundle del frontend | Patrón trasladado: `GROQ_API_KEY` en `.env` backend vía pydantic-settings → `Groq(api_key=settings.groq_api_key)` explícita (IN-03); auto-pickup del SDK documentado como gotcha; grep del build pasa a `GROQ_API_KEY` (fila 13 guia-15) |
</phase_requirements>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Validación de transición de pedidos (D-50) | API / Backend | — | Máquina de estados validada en el servidor; el panel solo pide y muestra (espejo de D-33) |
| CRUD productos + soft delete (D-51/D-52) | API / Backend | SPA (formularios) | Escritura con Pydantic + `get_current_admin`; el catálogo público ya filtra activos |
| Cómputo de métricas (D-54) | API / Backend | — | Agregación SQL sobre PEDIDO/LÍNEA en repositories |
| Guard de ruta admin (D-55) | Browser / Client | API (403 real) | `RequireAdmin` extiende `RequireAuth` — UX; la seguridad real son las dependencias de rol del backend |
| Layout del panel + burbuja de chat | Browser / Client | — | Rutas anidadas bajo `/admin`; burbuja flotante en el layout de la tienda |
| Llamada a Groq + API key + retrieval (D-56/D-60→D-63) | API / Backend | — | La key jamás cruza al cliente; system prompt con catálogo armado en el backend; wrapper de errores tipados del SDK (patrón IN-06) |
| Historial visible del chat (D-58) | Browser / Client | API (valida largo) | El frontend mantiene y envía el historial; el backend impone topes (RN-16) |
| Validación de ids recomendados (D-56) | API / Backend | — | Cada id del JSON del modelo se valida contra catálogo activo ANTES de responder — la muralla anti-alucinación |
| Producto catálogo (fotos) | CDN / Static (SPA) | — | Sin cambios: `frontend/public/products/{sku}.jpg` (D-08/D-51) |

## Standard Stack

### Core

**La única pieza del stack que cambia con el rework es el SDK del asistente: `google-genai` (desinstalado) → `groq` (instalado) en el backend del alumno.** El resto está verificado en `.planning/research/STACK.md` y construido hasta guia-15. Tabla de lo que el rework usa:

| Library | Version | Purpose | Why Standard | Provenance |
|---------|---------|---------|--------------|-----------|
| groq (Python) | 1.7.0 — pin recomendado `>=1.7,<2` | Asistente Groq: `chat.completions.create` con JSON estructurado | SDK oficial de Groq (github.com/groq/groq-python); **1.7.0 es la latest en PyPI** (verificado este session: `pip index versions groq` → 1.7.0 tope, 50+ versiones desde 0.0.1; publicada 2026-08-26); **probe punta a punta 1.7.0 en win32 este session** (models.list, json_schema strict, excepciones, headers). Python "3.10 or higher" — calza con el baseline 3.12 del proyecto | [VERIFIED: PyPI + README oficial github.com/groq/groq-python + probe local 2026-10-01] |
| pydantic-settings | 2.15.0 (ya instalada) | `GROQ_API_KEY` opcional en `.env` — degradación D-61 | Patrón ya construido en guia-05: `class Settings(BaseSettings)` + `SettingsConfigDict(env_file=".env")` *(carried over)* | [CARRIED OVER: 04-RESEARCH 2026-09-30, guia-05:116-124 leída esa session] |
| React Router 8 (ya instalado) | 8.4.0 | Rama `/admin` anidada + `<Outlet>` — YA CONSTRUIDO (guia-13) | *(carried over — no lo toca el rework)* | [CARRIED OVER: 2026-09-30] |
| TanStack Query (ya instalado) | 5.104.0 | `useMutation` del chat — YA CONSTRUIDO (guia-15) | *(carried over — no lo toca el rework)* | [CARRIED OVER: 2026-09-30] |

**Sobre el pin `>=1.7,<2` (discreción que D-63 delega al research):** el README del SDK NO da una recomendación oficial de pin (verificado este session — ausencia constatada en README completo fetched); dice que el SDK "generally follows SemVer conventions" pero admite cambios backwards-incompatible en minors (type-only, internals). La recomendación del research replica el patrón del corpus (`transbank-sdk`, y el que fue `google-genai >=2.25,<3`): **piso = versión probe-verified (1.7.0), techo = próximo major**. La mini-verificación de versión de guia-14 paso 1 se reescribe piso/techo (el fix D-4-6 ya enseñaba esa forma — ahora para groq).

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Pydantic (ya instalada) | 2.13.5 | `Recomendacion` y su `.model_json_schema()` — con `ConfigDict(extra="forbid")` para strict-mode (ver Pattern 1) | Siempre — el schema del asistente sale del mismo Pydantic |
| httpx (llega como dep de `groq`) | — | El SDK es httpx por dentro ("powered by httpx" — README); nada que instalar aparte | Automático |
| truststore (SOLO taller, NO guía) | 0.x | Workaround TLS del middlebox de ESTA máquina para api.groq.com | Ver Environment Availability — jamás entra a la guía |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `strict: true` en `json_schema` (probe-verified) | `strict` omitido (best-effort) + validación Pydantic backend | Strict = *constrained decoding*, "Never produces invalid JSON" garantizado por el servicio (doc oficial) — RECOMENDADO; best-effort deja la garantía solo en el backend. Con strict el schema exige `additionalProperties: false` (Pydantic lo emite con `extra="forbid"` — probe local) |
| SDK `groq` | REST directo con httpx (la API es OpenAI-compatible) | Veta el patrón del corpus (SDK oficial como transbank-sdk, D-63 locked); el SDK aporta excepciones tipadas, retries y timeout — la guía puede NARRAR la OpenAI-compatibility como conocimiento transferible (🧠, discreción ya anotada en CONTEXT) |
| `openai/gpt-oss-120b` (D-64) | `qwen/qwen3.8-27b` | Ambos verificados en el probe del usuario (195 tokens, voz correcta) y presentes en `models.list()` hoy (probe: 11 modelos). D-64 fija gpt-oss-120b como default; qwen queda como ejemplo de exploración `GET /models` |

**Installation (paso del alumno dentro de guia-14 reescrita, backend):**

```bash
uv add "groq>=1.7,<2"
# y desinstalar el SDK viejo (el blockquote de apertura narra el swap, D-65):
uv remove google-genai
```

**Version verification (ejecutada este session):** `pip index versions groq` → `groq (1.7.0)` latest; 50+ versiones desde 0.0.1. Deps del SDK: `anyio, distro, httpx, pydantic, sniffio, typing-extensions` (`pip show groq` este session) — pydantic/httpx ya viven en el proyecto; cero conflictos.

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| groq | PyPI | 50+ versiones desde 0.0.1 (latest 1.7.0 publicada 2026-08-26) | no disponible al seam (`weeklyDownloads: null`) | github.com/groq/groq-python (organización groq oficial) | **SUS** (seam: "unknown-downloads") | **Mantenido — falso positivo documentado** |

**Packages removed due to SLOP verdict:** none.

**Packages flagged as suspicious [SUS]:** `groq` [WARNING: flagged as suspicious by the seam — verify before using.] — **Contexto del falso positivo (mismo artefacto ya documentado dos veces en este proyecto):** el seam no tiene estadísticas de descargas de PyPI (`weeklyDownloads: null` → "unknown-downloads"); marcó igual a `google-genai` (research original de fase 4) y a `fastapi` (exploración del stack, STACK.md §Sources). Señales que refutan el veredicto: (1) la documentación OFICIAL de Groq enseña `pip install groq` como instalación del SDK (console.groq.com/docs/structured-outputs, leído este session); (2) repo en la organización github.com/groq (la empresa); (3) 50+ versiones publicadas desde 0.0.1 — paquete establecido por años; (4) **probe punta a punta este session** con 1.7.0 contra api.groq.com (la mejor anti-slopsquat posible: el paquete hace lo que dice la doc); (5) D-63 es decisión de usuario locked que nombra este SDK. **No se requiere checkpoint:human-verify adicional.** No hay paquetes npm nuevos (burbuja y panel ya construidos con el stack existente).

## Architecture Patterns

### System Architecture Diagram

Flujo del asistente reworkeado (la pieza con servicio externo; el panel admin es CRUD convencional ya ejecutado):

```
 Visitante anónimo                TIER CLIENTE (SPA)                TIER SERVIDOR (FastAPI en capas)           EXTERNO
 ┌──────────────┐      ┌─────────────────────────────┐      ┌──────────────────────────────────┐    ┌──────────────┐
 │ escribe en   │─────►│ BurbujaAsesora (layout      │─────►│ POST /api/asistente  (público,   │    │ Groq API     │
 │ la burbuja   │ JSON │ tienda) — historial visible │ JSON │ security: []) — YA CONSTRUIDOS   │    │ api.groq.com │
 │              │      │ en el navegador (D-58)      │      │  ├─ valida largo mensaje/hist.   │    │ (free signup │
 └──────────────┘      └─────────────────────────────┘      │  │  (422 ANTES de tocar red)     │    │  sin tarjeta)│
                                                            │  ├─ arma system prompt con       │    └──────▲───────┘
                                                            │  │  catálogo ACTIVO (mini-RAG)    │           │ HTTPS
                                                            │  ├─ Groq(api_key=settings.…)     │───────────┘
                                                            │  │  client LAZY (D-61)            │  response_format
                                                            │  │  chat.completions.create(      │  {'type':'json_schema',
                                                            │  │    response_format=            │   'json_schema':{name,
                                                            │  │    {'type':'json_schema',…}}   │    strict:true, schema}}
                                                            │  ├─ wrapper: RateLimitError→429  │
                                                            │  │  amable; resto→503 amable;    │
                                                            │  │  jamás 500 (D-61/IN-06)        │
                                                            │  └─ valida ids vs BD activa ─────┼── descarta ids
                                                            └──────────────┬───────────────────┘   alucinados
                                                                           │ 200 {respuesta, productos:[ids]}
                                                                           ▼
                                                            SPA renderiza texto + product cards
                                                            clicables (reusan la card del catálogo)

 Sin GROQ_API_KEY en .env ──► Groq() lanza GroqError EN LA CONSTRUCCIÓN ──► 503 "asistente no disponible"
                                (client lazy: la construcción vive DENTRO del try)      ──► burbuja degradada,
                                                                                          tienda 100% operativa (D-61)
```

Puntos de decisión trazables: (a) sin key → `GroqError` en construcción (probe-verified) → 503 amable, sin tocar Groq; (b) error tipado del SDK → RateLimitError→429, resto→503, jamás 500; (c) ids del modelo → filtro contra BD antes de responder. La burbuja/frontend/endpoint NO cambian con el rework — solo el service y el paso del alumno.

### Recommended Project Structure

*(Carried over — el árbol del ALUMNO ya construido hasta guia-15; el rework toca SOLO los archivos marcados.)*

```
backend/                              frontend/  (SIN CAMBIOS en el rework)
├── app/                              ├── src/
│   ├── routers/                      │   ├── components/RequireAdmin.tsx   # construido (guia-13)
│   │   ├── admin.py        # HECHO   │   ├── features/admin/               # construido
│   │   └── asistente.py    # TOCA*:  │   └── features/asistente/           # construido (burbuja)
│   │                       #   solo si el wrapper        │
│   │                       #   de errores cambia de SDK │
│   ├── services/                     │
│   │   ├── admin.py        # HECHO   │
│   │   └── asistente.py    # ★ REESCRIBIR: de google.genai a groq │
│   └── schemas/ (asistente)# ★ AJUSTAR: Recomendacion gana extra="forbid" │
└── .env  # GROQ_API_KEY (taller ya la tiene; GEMINI removida)
```

*El router de guia-14 declara responses 200/422/429/503 que NO cambian (D-66: el contrato 0.4.0 es agnóstico); lo único que puede tocar el router es el import del service. Reglas de dependencia vigentes: routers sin SQLAlchemy, services sin HTTP, el asistente es un service que habla un SDK externo — mismo lugar que el service de Webpay (guia-09).

### Pattern 1: Structured output en groq 1.7 — `response_format` `json_schema` (LA pieza D-56/D-63)

**What:** Forzar respuesta JSON conforme a un schema, con modo strict (constrained decoding).
**When to use:** Endpoint del asistente — respuesta `{respuesta, productos}` sin parseo frágil.
**Evidencia doble (doc oficial + probe):** la doc oficial enseña el patrón con Pydantic; el probe de este research lo ejecutó con `strict: true` y obtuvo JSON válido con ids correctos en la voz de Maura.

```python
# Source: console.groq.com/docs/structured-outputs (fetched 2026-10-01) + probe local SDK 1.7.0 (mismo día)
# Patrón doc oficial (adaptado a Recomendacion — el ejemplo de la doc usa SQLQueryGeneration):
from pydantic import BaseModel, ConfigDict

class Recomendacion(BaseModel):
    model_config = ConfigDict(extra="forbid")   # ← emite additionalProperties: false (probe pydantic 2.13.5)
    respuesta: str                              #   — REQUISITO del modo strict
    productos: list[int]                        # ambos campos ya nacen en "required" (probe)

completion = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[...],                             # system prompt con catálogo activo (Pattern 6)
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "Recomendacion",
            "strict": True,                     # ← constrained decoding; soportado por gpt-oss-20b/120b (doc)
            "schema": Recomendacion.model_json_schema(),
        },
    },
)
recomendacion = Recomendacion.model_validate_json(completion.choices[0].message.content)
```

Notas firmadas: (1) el dict `response_format` es la forma nativa — la doc también acepta `client.chat.completions.create(..., response_format=...)` con tipos beta (`groq.types.chat.completion_create_params`) que el research NO recomienda para la guía (el dict es el patrón documentado en la página de Structured Outputs); (2) `strict: true` exige "all fields must be required" + `additionalProperties: false` en cada objeto — con `extra="forbid"` Pydantic cumple ambas (probe local: schema emitido con `"additionalProperties": false` y `"required": ["respuesta", "productos"]`); (3) sin strict, la validación queda solo del lado nuestro (best-effort — la doc lo describe como modo por defecto); (4) keywords de JSON Schema no soportadas se ignoran en strict mode (doc) — el tope de 3 cards (RN-16) SIGUE aplicándolo el backend después de filtrar ids, no el schema; (5) el probe: `parsed keys: ['productos', 'respuesta']`, `productos: [1]`, 548 tokens, modelo devuelto `openai/gpt-oss-120b`.

### Pattern 2: API key por Settings explícita + degradación (D-63/IN-03/D-61)

**What:** pydantic-settings carga el `.env`; el client se construye con `api_key` EXPLÍCITA; sin key la app arranca y el endpoint degrada a 503.

```python
# Source: patrón Settings del corpus (guia-05) + README groq (fetched 2026-10-01) + probes locales
# README verbatim: api_key=os.environ.get("GROQ_API_KEY"),  # This is the default and can be omitted
#                  → el SDK AUTO-PICKUPEA la env var GROQ_API_KEY (gotcha IN-03: mismo que google-genai)
# PERO el SDK NO lee el archivo .env (recomienda python-dotenv aparte) — nuestro loader es pydantic-settings.

class Settings(BaseSettings):
    # ... secret_key, admin_email, cliente_password (existentes, fail-fast) ...
    groq_api_key: str | None = None   # NUEVO: opcional — el asistente degrada, no bloquea (D-61)
    model_config = SettingsConfigDict(env_file=".env")
```

Comportamientos firmados por probe local (2026-10-01, SDK 1.7.0):
- `groq.Groq()` sin `api_key` y sin `GROQ_API_KEY` en el entorno lanza **`groq.GroqError` EN LA CONSTRUCCIÓN**: "The api_key client option must be set either by passing api_key to the client or by setting the GROQ_API_KEY environment ..." → el client lazy de guia-14 (arranca None, se construye a la primera llamada) sigue siendo el patrón correcto, con la construcción DENTRO del `try` del wrapper.
- `Groq(api_key=settings.groq_api_key)` explícita funciona punta a punta (así corrió el probe) — la cláusula IN-03 se mantiene: la fuente de la key es Settings, no el entorno del proceso.
- El ADR-018 dice el gotcha: el SDK auto-pickupea la env var, y el proyecto deliberadamente NO confía en eso (explicit-over-implicit, mismo criterio que la decisión editorial IN-03 del ADR-017).

### Pattern 3: Wrapper de errores del servicio externo (patrón IN-06/D-61 con `groq`)

**What:** El service atrapa TODO error del SDK y lo traduce a respuestas amables; jamás un 500 crudo.

```python
# Source: README groq (tabla de excepciones, fetched 2026-10-01) + probe local (MROs verificados)
import groq
from groq import Groq, RateLimitError   # tipadas, importables de la raíz (probe)

try:
    client = Groq(api_key=settings.groq_api_key)      # lazy: construcción DENTRO del try (Pattern 2)
    completion = client.chat.completions.create(...)
except RateLimitError:                                 # 429 → HTTPException 429 amable ("cuota del free tier",
    raise HTTPException(status_code=429, detail=<copy amable reintentar>)  #  30 RPM/1.000 RPD citados con fuente, D-68)
except groq.GroqError:                                 # el resto (APIStatusError, APIConnectionError,
    raise HTTPException(status_code=503, detail=<copy asistente no disponible>)  # APITimeoutError⊂APIConnectionError, GroqError de construcción)
```

Jerarquía firmada por probe (MRO real): `APITimeoutError ⊂ APIConnectionError ⊂ APIError ⊂ GroqError`; `RateLimitError ⊂ APIStatusError ⊂ APIError`; `APIStatusError` expone `.status_code` y `.response` como atributos de instancia (probe: key inválida → `AuthenticationError` con `.status_code == 401`). Tabla completa del README: 400 `BadRequestError`, 401 `AuthenticationError`, 403 `PermissionDeniedError`, 404 `NotFoundError`, 422 `UnprocessableEntityError`, 429 `RateLimitError`, ≥500 `InternalServerError`.

Datos clave para la narración (README, fetched 2026-10-01): **el SDK reintenta solo** "Certain errors... 2 times by default, with a short exponential backoff" — connection errors, 408, 409, 429 y ≥500; configurable con `max_retries` (0 lo apaga). Timeout por defecto 1 minuto (`timeout=` en el constructor; `APITimeoutError` al vencer). **Diferencia con google-genai que la guía debe narrar:** groq reintenta TAMBIÉN el 429 (2x) — el RateLimitError le llega al wrapper después de esos reintentos internos; el wrapper traduce, no re-reintenta (error-evitado de guía, igual que antes).

### Pattern 4: RequireAdmin extiende RequireAuth (D-55) — *(carried over, EJECUTADO en guia-13 y verificado EN VIVO)*

**What:** Guard por rol en la SPA — espejo UX del 403 backend. La clienta con sesión sin rol ve NoAutorizado a secas (sin navbar); sin sesión cae al login con returnTo. Ratificado runtime en el UAT (fila 2, validado en navegador).

### Pattern 5: Ruta anidada con layout (D-55) — *(carried over, EJECUTADO)*

`<Route element={<RequireAdmin />}>` → `/admin` con `LayoutAdmin` + sub-rutas productos/pedidos/métricas — construido en guia-13, build verde 169 módulos. El rework NO lo toca.

### Pattern 6: Mini-RAG honesto + validación de ids (D-56) — intacto, cambia el motor

**What:** Catálogo activo completo en el system prompt; respuesta JSON con ids; filtro contra BD; truncado a 3 (RN-16).

```python
# Muralla D-56 — SIN CAMBIOS con Groq; solo el motor de generate_content → chat.completions.create
class Recomendacion(BaseModel):
    model_config = ConfigDict(extra="forbid")   # nuevo por strict-mode (Pattern 1)
    respuesta: str          # texto de la asesora, voz de Maura (D-02)
    productos: list[int]    # ids citados — el backend los valida contra catálogo ACTIVO

# Después de chat.completions.create + response_format json_schema (Pattern 1):
ids_validos = {p.id for p in repo.activos()}          # consulta BD
recomendacion.productos = [i for i in recomendacion.productos if i in ids_validos][:3]  # truncado RN-16
# → el chat solo puede mostrar cards que existen; ids alucinados se descartan (AIAS-02)
```

El probe de este research usó EXACTAMENTE esta forma: system prompt con 3 productos reales + pregunta "algo cítrico para el día" → `[1]` (Brisa de Naranja, cítrica) con texto "¡Claro! Te recomiendo la Brisa de Naranja, un aroma cítrico que te refrescará..." — la muralla funciona contra el modelo real.

### Pattern 7: Tokens UI del panel/burbuja — *(carried over, EJECUTADO)*

Paleta `@theme` y BADGES construidos en guias 12/13 (badge "Stock bajo" ámbar en vivo 3/3 contra métricas). El rework NO toca UI; los copys de la burbuja ("asistente no disponible", Reintentar) ya están locked del UI-SPEC.

### Anti-Patterns to Avoid

- **Citar "14.400 RPD" en la guía**: la doc oficial lista `openai/gpt-oss-120b` con **1.000 RPD** (30 RPM / 8K TPM / 200K TPD) y los headers vivos de la org del usuario lo confirman (`x-ratelimit-limit-requests = 1000`) — el 14.4K de la nota es de los modelos prompt-guard (ver Pitfall 1).
- **Confiar en el auto-pickup de `GROQ_API_KEY`**: el SDK lo hace ("default and can be omitted") pero NO lee el `.env` — sin pydantic-settings el alumno tendría la key en el archivo y el SDK no la vería; y confiar en el entorno del proceso es justo lo que IN-03 veta (D-63).
- **Poner la key en el cliente** (env de Vite, `import.meta.env`): cualquier `VITE_*` termina en el bundle — AIAS-03 existe para esto. El grep del build pasa a `GROQ_API_KEY`.
- **Filtrar ids alucinados en el FRONTEND**: la validación es del backend (D-56).
- **Retry-engine casero ENCIMA del SDK**: reintenta 2x connection/408/409/429/5xx por defecto — el wrapper traduce, no re-reintenta (y ojo: el 429 TAMBIÉN se reintenta internamente).
- **`.model_json_schema()` pelado con `strict: true`**: sin `additionalProperties: false` el schema viola los requisitos del modo strict — falta una línea (`extra="forbid"`) que la guía enseña con su porqué (Pitfall 2).
- **Fail-fast sin key**: el asistente es opcional (D-61) — la tienda arranca sin `GROQ_API_KEY` por requisito.
- **Estados nuevos del pedido / prometer cifras sin fuente**: vetados por D-50 / D-68.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Forzar JSON del modelo | Prompt-engineering "responde SOLO JSON" + `json.loads` frágil | `response_format` `json_schema` con `strict: true` | Constrained decoding del servicio — "Never produces invalid JSON" (doc oficial); el parseo manual revienta con un backtick perdido |
| Validar que el JSON calza el schema | Validador a mano campo por campo | `Recomendacion.model_validate_json(...)` (round-trip del mismo modelo que generó el schema) | Un solo lugar de verdad — y `extra="forbid"` hace doble duty (validación Pydantic + requisito strict) |
| Client HTTP a Groq | `requests`/`httpx` directo a la REST API | SDK oficial `groq` | Auth, excepciones tipadas (RateLimitError/APIStatusError), retries 2x, timeout — patrón del corpus (D-63) |
| Retry con backoff | Loop propio con sleep | Nada — el SDK reintenta 2x por defecto | Doble-retry multiplica presión sobre el free tier (30 RPM) |
| Gráficos de métricas | Librería de charts | Tarjetas + tabla HTML (ADMN-04 locked) | Requisito explícito — y ya ejecutado |
| Guard de rol solo en frontend | "Como el botón no se ve, no se puede llamar" | `get_current_admin` en CADA endpoint + RequireAdmin como UX | Lección D-33 — ya ejecutado |
| Historial de chat en BD | Tabla `mensajes` + sesión | Historial en el cliente, enviado por request (D-58) | Cero tablas nuevas — ya ejecutado |

**Key insight (rework):** el rework NO construye nada nuevo — reusa TODO lo ya construido (endpoint público, responses 422/429/503 declaradas, burbuja, muralla, topes RN-16, grep del build) y cambia UN motor: `google-genai.models.generate_content` → `groq.chat.completions.create` con `response_format` json_schema. La superficie de la lección se mantiene: SDK oficial + JSON estructurado + key que no sale del `.env` + degradación amable. Las guías cobran las herencias igual que antes (patrón D-46).

## Common Pitfalls

### Pitfall 1: Citar límites equivocados — 14.400 vs 1.000 RPD (D-68, el hallazgo material)
**What goes wrong:** la guía promete "30 RPM / 14.400 RPD" (la nota del usuario) y el alumno descubre otro número en su consola o se agota antes de lo esperado.
**Why it happens:** en la tabla pública, "30 / 14.4K" es la fila de los modelos de moderación `meta-llama/llama-prompt-guard-2-22m/86m`; el header de ejemplo `x-ratelimit-limit-requests: 14400` de la propia página es "illustrative"; y las cifras 14.4K circulan en fuentes community de la era 2024 (llama-3.1-8b free tier).
**How to avoid:** la guía cita la tabla oficial VERBATIM para el modelo por defecto: **`openai/gpt-oss-120b` → 30 RPM / 1K RPD / 8K TPM / 200K TPD** [CITED: console.groq.com/docs/rate-limits, fetched 2026-10-01] con "a la fecha de esta guía" + link + el pointer a la página Limits de la consola ("You can view the current, exact rate limits for your organization on the limits page in your account settings" — la misma doc). Respaldo runtime: headers vivos de la org del usuario = 1000 RPD / 8000 TPM (probe). RNF-08 se queda SIN números (D-68).
**Warning signs:** cualquier cifra de límites en la guía sin URL y sin "a la fecha".

### Pitfall 2: `strict: true` sin `additionalProperties: false`
**What goes wrong:** la guía pasa `Modelo.model_json_schema()` pelado con `strict: true` — el schema NO cumple los requisitos del modo strict y la llamada falla o degrada a best-effort.
**Why it happens:** Pydantic v2 NO emite `additionalProperties: false` por defecto (probe local pydantic 2.13.5: el schema sale con `required` completo pero SIN additionalProperties).
**How to avoid:** una línea con lección: `model_config = ConfigDict(extra="forbid")` — Pydantic la emite (probe) Y de paso la validación backend queda más estricta. Alternativa honesta: omitir strict (best-effort) y confiar en `model_validate_json` — decisión del planner; el research recomienda strict porque el modelo por defecto lo soporta (gpt-oss-120b en la lista oficial) y el probe lo validó.
**Warning signs:** error 400 de la API al crear el completion, o respuestas que a veces violan el schema.

### Pitfall 3: El modelo cita ids que no existen (o inactivos) — *(carried over, más vigente que nunca)*
**What goes wrong:** el LLM devuelve ids alucinados o de productos desactivados — cards rotas en el chat.
**How to avoid:** doble muralla D-56: system prompt solo con catálogo ACTIVO + filtrado contra BD antes de responder. El probe demostró el comportamiento correcto contra el modelo real.
**Warning signs:** card con imagen/precio vacíos en el chat.

### Pitfall 4: 429 en clase (free tier) — cifras y comportamiento
**What goes wrong:** un alumno spamea la burbuja y su key entra en cuota — `RateLimitError`.
**Why it happens:** 30 RPM / 1.000 RPD por ORGANIZACIÓN (cada alumno con SU key = SU cuota aislada, D-63/patrón D-60); además el SDK reintentó el 429 2 veces antes de entregarlo (llega ~2-4s después).
**How to avoid:** (a) cada alumno con SU key aísla la cuota; (b) topes RN-16 acotan tokens; (c) wrapper 429→mensaje amable; (d) la guía cita las cifras CON fuente y "a la fecha" (Pitfall 1). Para el aula: 1.000 RPD son ~16 consultas/minuto sostenidas todo el día — de sobra para un taller, y la lección del 429 no cambia.
**Warning signs:** `RateLimitError` repetido; burbuja lenta antes del error (reintentos internos).

### Pitfall 5: HTTPException manual invisible en `/docs` — *(carried over; las responses YA están declaradas en 0.4.0)*
**What goes wrong:** tocar el router del asistente y perder las responses 422/429/503 declaradas — la fila contrato ↔ `/docs` de la Gran verificación final canta desvío falso.
**How to avoid:** el router declarado en guia-14 NO cambia con el rework (D-66: contrato agnóstico intacto); si el plan toca `routers/asistente.py`, la verificación fila 12 (17 paths, diferencia NINGUNA) debe seguir en verde.
**Warning signs:** diff del contrato ↔ `/docs` con el 429/503 del asistente.

### Pitfall 6: Dos umbrales de stock distintos confundidos — *(carried over, EJECUTADO con dos constantes con nombre)*
El umbral admin `STOCK_BAJO_UMBRAL=5` (backend) + espejo frontend `STOCK_BAJO=5` vs el "¡Últimas N unidades!" de tienda (1-3). Ya resuelto en guias 12/13; el rework no lo toca — se preserva para no reabrir.

### Pitfall 7: Remover/renombrar en silencio lo ya publicado — *(la lección D-54 aplicada al rework mismo)*
**What goes wrong:** el barrido D-67 borra menciones sin narrar el cambio, o edita ADR-017 de cuerpo.
**Why it happens:** 64 menciones en 12 archivos invitan al sed global.
**How to avoid:** el blockquote de apertura de guia-14 (D-65) narra el swap y apunta a ADR-018; ADR-017 SOLO marca superseded (cuerpo byte-intacto); ADR-002 cambia 2 líneas porque describe el sistema vigente. Mismo criterio de las fases previas: nada cambia en silencio.
**Warning signs:** diffs que tocan guias 01-11 o el cuerpo de ADR-017.

### Pitfall 8: grep del build no portable — *(carried over, actualizado a GROQ_API_KEY)*
`grep -r "GROQ_API_KEY" dist/` (Git Bash) / `Select-String -Path dist\* -Pattern "GROQ_API_KEY" -Recurse` (PowerShell), DESPUÉS de `npm run build`, resultado esperado cero coincidencias + control positivo. Ya corrido en fase 4 con GEMINI (fila 13, exit 1 + control positivo) — el rework cambia el patrón y re-verifica. Nota taller: findstr desde Git Bash corrompe switches MSYS (D-4-9 del UAT) — ofrecer Select-String como variante.

### Pitfall 9: TLS del taller ≠ TLS del alumno (truststore)
**What goes wrong:** el taller (esta máquina, win32) no alcanza api.groq.com por un middlebox local que intercepta TLS (revocación bloqueada) — el re-verification del UAT test 2 fallaría por RED, no por código.
**Why it happens:** ambiente de red del taller, documentado en 04-UAT test 2; NO es un bug de guía ni del SDK.
**How to avoid:** taller-only: `pip install truststore` + `truststore.inject_into_ssl()` ANTES de construir el client (el probe de este research corrió así y funcionó). La guía NO menciona truststore — los alumnos no tienen el middlebox. Regla dos lugares NO aplica (no es defecto de la guía); se documenta como nota de entorno del taller en el UAT.
**Warning signs:** `SSLError`/`SELF_SIGNED_CERT_IN_CHAIN` en el taller con el mismo código que funciona afuera.

## Code Examples

### Ejemplo A: Service del asistente reworkeado (sketch integrador probe-verified para guia-14)

```python
# Firmado por el probe de este research (SDK groq 1.7.0, 2026-10-01) + doc oficial.
# Los nombres finales son del corpus existente (services/asistente.py de guia-14).
MODELO_ASISTENTE = "openai/gpt-oss-120b"   # D-64: constante backend, patrón STOCK_BAJO_UMBRAL

_client: Groq | None = None                 # lazy (D-61): arranca None; se construye a la primera llamada

def _obtener_client() -> Groq:
    # SIN key → GroqError EN LA CONSTRUCCIÓN (probe) → el wrapper la traduce a 503 amable
    return Groq(api_key=settings.groq_api_key, timeout=30.0)  # IN-03: explícita desde Settings

def recomendar(historial, catalogo_activo) -> Recomendacion:
    global _client
    try:
        if _client is None:
            _client = _obtener_client()
        completion = _client.chat.completions.create(
            model=MODELO_ASISTENTE,
            messages=_armar_mensajes(historial, catalogo_activo),  # system prompt mini-RAG (Pattern 6)
            response_format={"type": "json_schema", "json_schema": {
                "name": "Recomendacion", "strict": True,
                "schema": Recomendacion.model_json_schema()}},     # extra="forbid" en el modelo (Pattern 1)
        )
        return Recomendacion.model_validate_json(completion.choices[0].message.content)
    except RateLimitError:
        raise HTTPException(status_code=429, detail=<copy amable — cifras citadas con fuente, D-68>)
    except GroqError:                         # cubre APIStatusError, APIConnectionError, APITimeoutError(⊂conn), GroqError de construcción
        raise HTTPException(status_code=503, detail=<copy asistente no disponible>)
```

### Ejemplo B: Mini-exploración `GET /models` (D-64, herramienta de diagnóstico ante deprecación)

```python
# Probe-verified: client.models.list() → 11 modelos el 2026-10-01, incluye openai/gpt-oss-120b y qwen/qwen3.8-27b
for m in client.models.list().data:
    print(m.id)
# La guía lo usa como diagnóstico: "si tu modelo fue deprecado, lista los vigentes"
# Política oficial (console.groq.com/docs/deprecations, fetched 2026-10-01):
#   "Groq may occasionally deprecate and replace models... typically 30 days notice via
#    documentation updates, email, and console banners" — y los PRODUCTION models (los de la
#   primera tabla de /docs/models, donde vive gpt-oss-120b) NO se decomisionan como los labs.
```

### Ejemplo C: Máquina de estados / métricas — *(carried over, EJECUTADOS y verificados runtime)*

`TRANSICIONES_ADMIN = {"pending": {"cancelled"}}` (D-50, 409 con copy locked) y las 4 agregaciones de D-54 (ingresos PAID, group_by estado, top 5 por líneas snapshot, count stock bajo) — construidos en guias 12/13 y calzados contra la BD real en el UAT (filas 6/7). El rework NO los toca.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| google-genai 2.25/2.26 (`generate_content` + `response_json_schema`) | **SDK `groq` 1.7.0** (`chat.completions.create` + `response_format` json_schema) | Decisión 2026-10-01 (D-63): Google exige billing para keys nuevas + 402 real | El swap se narra una vez (blockquote guia-14 + ADR-018); ADR-017 superseded, cuerpo intacto |
| API key gratis en Google AI Studio (D-60) | API key gratis en **console.groq.com** (signup email/Google/GitHub → API Keys → Create API Key; sin tarjeta) | 2026-10-01 | Mismo patrón del alumno; key mostrada una sola vez — la guía enseña copiarla al `.env` de inmediato |
| Límites Gemini sin cifras (no públicos sin login) | **Límites públicos con tabla** — 30 RPM / 1K RPD / 8K TPM / 200K TPD para gpt-oss-120b | Docs fetched 2026-10-01 | Cierra el concern de STATE.md; D-68 fija cómo citarlos (fuente + "a la fecha"); OJO: la nota "14.400 RPD" no calza (Pitfall 1) |
| Modelo `gemini-flash-latest` (alias hot-swap) | `openai/gpt-oss-120b` como CONSTANTE (D-64) — production model, no alias | 2026-10-01 | 🧠 de deprecación: Groq avisa "typically 30 days" y publica timeline; production models no se decomisionan como los labs; `models.list()` es el diagnóstico |
| Docs structured output con drift (Interactions API vs SDK pinneado — Pitfall 1 del research viejo) | Doc y SDK alineados HOY (ambos `response_format` json_schema) — pero la lección de verificar contra el pin queda | — | La vieja Pitfall 1 muere; la disciplina de firmar-con-evidencia (D-56) queda y este research la ejercitó de nuevo |

**Deprecated/outdated:**
- `google-genai` en ESTE proyecto: desinstalado del backend del alumno (paso de guia-14 reescrita) — queda como contexto histórico en ADR-017/018.
- `google-generativeai`: sigue EOL y vetado (REQUIREMENTS Out of Scope).
- Cifras "14.4K RPD" de fuentes community: no firmar — la tabla oficial actual dice 1K RPD para el modelo por defecto.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | El paso del alumno "crear API key en console.groq.com" (signup → API Keys → Create API Key → copiar una sola vez) es estable en su forma general | Pattern 2 / Sources | Bajo: la UI puede cambiar cosméticamente; la guía lo redacta resistente a cambios (mismo criterio que A2 del research original). Corroborado por fuentes community consistentes + la key del usuario creada así |
| A2 | Los límites del free signup SON los de la tabla pública ("base limits for the Developer plan") | Pitfall 1/4 | Bajo-medio: la página rotula la tabla como base del Developer plan y NO publica una tabla separada "free"; los headers vivos de la org del usuario (creada sin tarjeta, sin pago) devuelven exactamente esos valores (1000 RPD / 8000 TPM) — la evidencia disponible dice que calzan. La guía cita la tabla + pointer a Limits de la consola, cubriendo el caso org-específico |
| A3 | Las máquinas de los alumnos NO necesitan el workaround truststore (el middlebox es del taller) | Pitfall 9 / Environment | Bajo: si un alumno tuviera un proxy similar, el mensaje de error es diagnostizable; la guía NO lo enseña (ruido para el 99%). El taller sí lo necesita — documentado |
| A4 | `qwen/qwen3.8-27b` sigue disponible como ejemplo de exploración cuando la guía se publique | D-64 / Ejemplo B | Bajo: los modelos cambian; la guía enseña `models.list()` como diagnóstico exactamente para eso (30 días de aviso oficial) |
| A5 | El SDK `groq` en Windows no tiene gotchas propios | Standard Stack | Bajo: nada documentado en docs/README (ausencia constatada este session); el probe corrió EN win32 sin más problema que el TLS del taller (middleware de red, no del SDK) |
| A6 | `dist/` del taller ya no contiene `GEMINI_API_KEY` tras el rebuild post-rework y el grep con `GROQ_API_KEY` da cero | Pitfall 8 | Bajo: idéntico mecánicamente al grep ya pasado con GEMINI (fila 13, exit 1 + control positivo); se re-verifica en el UAT |

## Open Questions

> Las tres del research original quedaron RESUELTAS por los planes de la fase 4 (happy path tras checkpoint → hoy desbloqueado por Groq; 429 sin cifras → D-68 ahora publica cifras CON fuente; 409 para transición ilegal → ejecutado y verificado runtime). Se listan colapsadas; la única pregunta nueva es la nº 1.

1. **D-68 — la nota del usuario (30 RPM / 14.400 RPD) no calza con la doc oficial (30 RPM / 1.000 RPD para `openai/gpt-oss-120b`)**
   - What we know: tabla oficial verbatim [CITED: console.groq.com/docs/rate-limits, 2026-10-01] + headers vivos de la org del usuario (probe: `x-ratelimit-limit-requests = 1000`, `x-ratelimit-limit-tokens = 8000`) coinciden. "30 / 14.4K" en esa tabla es la fila de `meta-llama/llama-prompt-guard-2-*`; el header 14400 de la página es "illustrative".
   - What's unclear: de dónde salió el 14.400 de la nota (¿limits page de la consola? ¿fuente community 2024?) — y si la consola del usuario muestra algo distinto a los headers que su propia org devuelve.
   - Recommendation: D-68 ya decide el caso: "If the official doc differs, record what the doc actually says — never sign on assumptions". La guía cita **30 RPM / 1.000 RPD / 8K TPM / 200K TPD** con URL y "a la fecha de esta guía" + pointer a la página Limits de la consola; RNF-08 sin números. El planner redacta guia-14/🧠 del 429 con esas cifras y el usuario lo ve en el checkpoint de revisión del rework (human_verify_mode: end-of-phase). Nota para el cierre: actualizar también la frase de CONTEXT/UAT si se re-registra el dato.
2. *(RESOLVED, carried over)* Happy path con key → desbloqueado: la GROQ_API_KEY del taller ya está verificada punta a punta (04-UAT test 2 + probe de este research con el SDK).
3. *(RESOLVED, carried over)* 429 sin cifras → D-68 lo reemplaza: cifras públicas CON fuente (ver OQ 1).
4. *(RESOLVED, carried over)* 409 para transición ilegal → contrato 0.4.0 ejecutado y verificado runtime (copy locked "Ese pedido ya no está en curso.").

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js | Frontend del taller (rebuild + grep fila 13) | ✓ | v24.21.0 (≥ 22.22 requerido) *(carried over)* | — |
| uv | Backend del taller | ✓ | 0.9.3 *(carried over)* | — |
| Python | Backend (baseline 3.12; groq pide ≥3.10) | ✓ | 3.12.10 | — |
| `D:/Repos/maura-uat` app hasta guia-15 | UAT delegado | ✓ | taller completo, servidores detenidos, puertos libres (04-UAT) | — |
| GROQ_API_KEY | UAT happy path (test 2) | ✓ **presente en `maura-uat/backend/.env`** (GEMINI removida — 04-UAT; leída por el probe de este research) | — | — |
| SDK `groq` en el taller | reintegración del service | ✗ aún NO instalado en el taller (verificado: `pip list` sin groq) | — | `uv add "groq>=1.7,<2"` como primer paso del rework del taller (+ `uv remove google-genai`) |
| Red → pypi.org | instalación groq | ✓ (pip index respondió este session) | — | — |
| Red → api.groq.com | llamada real en UAT | ✓ **CON truststore en el taller** (probe 200 con `truststore.inject_into_ssl()`; SIN truststore el middlebox local bloquea TLS — Pitfall 9) | taller: truststore; alumnos: directo |
| `pip`/venv scratch | probes de research | ✓ (venv desechable con groq 1.7.0 corriendo este session) | — | eliminable |

**Missing dependencies with no fallback:** ninguna — todo lo que el rework necesita está disponible (key presente, SDK en PyPI, taller íntegro; el truststore del taller tiene workaround probado).
**Missing dependencies with fallback:** SDK `groq` no instalado aún en el taller → el plan lo instala como primer paso.

## Security Domain

> `security_enforcement: true`, ASVS nivel 1 (`.planning/config.json`). Fase docs-only: la superficie de seguridad del rework vive en ADR-018, guia-14 reescrita y el taller.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No (nuevo) | Sin cambios: JWT bearer existente; el asistente sigue público por diseño (D-59) |
| V3 Session Management | No (nuevo) | El chat sigue stateless (D-58) |
| V4 Access Control | No (cambios) | Los 7 paths admin ya protegidos y verificados (UAT fila 1); el rework no abre ni cierra endpoints |
| V5 Input Validation | Sí (se mantiene) | `ChatMensaje` topes RN-16 (mensaje ≤500, historial ≤10, cards ≤3) ya construidos y verificados (fila 9); `Recomendacion` gana `extra="forbid"` (doble duty: strict-mode + validación) |
| V6 Cryptography | No (nuevo) | Key en `.env` fuera de git — gestión de secretos |
| V12 Communications | **Sí** | La key viaja solo backend→api.groq.com por HTTPS del SDK (httpx); jamás al cliente (AIAS-03 — grep del build con `GROQ_API_KEY`) |

### Known Threat Patterns for {stack FastAPI + React + LLM vía Groq}

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Prompt injection desde el mensaje del visitante | Tampering / Elevation | Mini-RAG con instrucciones en system prompt + validación de ids contra BD (D-56): aunque el modelo desobedezca, solo puede citar productos reales; el texto se renderiza como TEXTO en React (JSX escapa — jamás `dangerouslySetInnerHTML`) |
| Alucinación de ids/productos inexistentes | Tampering | Filtro server-side contra catálogo activo + truncado a 3 (Pattern 6, ratificado por probe con modelo real) |
| Fuga de la API key al bundle | Information Disclosure | Key SOLO en `.env` backend (D-63); nada de `VITE_` para Groq; grep `dist/` con `GROQ_API_KEY` (fila 13 re-verificada) |
| Auto-pickup involuntario de `GROQ_API_KEY` del entorno | Information Disclosure | IN-03: `api_key` EXPLÍCITA desde Settings; el auto-pickup del SDK queda documentado como gotcha en ADR-018 (mismo criterio editorial que IN-03/ADR-017) |
| Enumeración/abuso del endpoint público del chat | DoS / Abuse | Topes RN-16 (422 antes de red); 30 RPM/1K RPD por org del proveedor; 429 traducido amable (D-61) |
| Mass assignment / IDOR / SQLi | — | Sin cambios: allow-list ya construida (fila 3), 404 uniforme de ownership, ORM parametrizado (carried over) |

## Sources

### Primary (HIGH confidence — evidencia fresca 2026-10-01)
- **console.groq.com/docs/rate-limits** (webReader, 2026-10-01) — tabla verbatim: `openai/gpt-oss-120b | 30 | 1K | 8K | 200K`; prompt-guard 22m/86m `30 | 14.4K`; "Rate limits apply at the organization level"; "the limits shown below are the base limits for the Developer plan"; "You can view the current, exact rate limits for your organization on the limits page in your account settings"; 429 + retry-after "will only be set when a 429 status code is returned"
- **console.groq.com/docs/structured-outputs** (webReader, 2026-10-01) — sintaxis `response_format` json_schema verbatim (ejemplo Pydantic `model_json_schema()`), modo strict: "constrained decoding", "Never produces invalid JSON", "Limited (GPT-OSS 20B, 120B)", requisitos strict (all required + additionalProperties: false), json_object fallback, keywords no soportadas ignoradas
- **console.groq.com/docs/models** (webReader, 2026-10-01) — gpt-oss-120b en tabla PRODUCTION, 32K contexto, $0.15/$0.60 por 1M; Developer-plan limits "250K TPM; 1K RPM" (columna de la página models — ver nota Pitfall 1: la página de rate-limits es la fuente canónica de RPM/RPD y dice 30 RPM)
- **console.groq.com/docs/deprecations** (webReader, 2026-10-01) — "Groq may occasionally deprecate and replace models... typically 30 days notice via documentation updates, email, and console banners"; "Production models are not subject to decommissioning" (labs sí); timeline de end-of-life publicado
- **github.com/groq/groq-python README** (WebFetch x2, 2026-10-01) — `pip install groq`; Python 3.10+; sync/async httpx; `api_key=os.environ.get("GROQ_API_KEY"), # This is the default and can be omitted`; python-dotenv recomendado para `.env`; tabla excepciones tipadas completa; "Certain errors are automatically retried 2 times by default, with a short exponential backoff" (connection errors, 408, 409, 429, ≥500); "By default requests time out after 1 minute"; "generally follows SemVer conventions" SIN recomendación de pin (ausencia constatada)
- **groq.com/pricing** (webReader, 2026-10-01) — "Get started for free and upgrade as your needs grow"; pricing on-demand por token
- **PyPI registry** (`pip index versions groq`, este session) — 1.7.0 latest; 50+ versiones desde 0.0.1; `pip show groq`: deps anyio, distro, httpx, pydantic, sniffio, typing-extensions
- **Probe local SDK 1.7.0 en win32 (venv desechable, 2026-10-01)** — models.list() 200 (11 modelos, gpt-oss-120b y qwen3.8-27b presentes); chat.completions.create json_schema strict:true 200 (voz Maura, productos [1], 548 tokens); `with_raw_response` headers: `x-ratelimit-limit-requests=1000`, `x-ratelimit-limit-tokens=8000`; key inválida → `AuthenticationError` `.status_code==401`; `Groq()` sin key → `groq.GroqError` en construcción; MROs: `APITimeoutError ⊂ APIConnectionError ⊂ APIError ⊂ GroqError`, `RateLimitError ⊂ APIStatusError ⊂ APIError`; `Groq(timeout=5.0, max_retries=0)` OK
- **Probe local Pydantic 2.13.5 (venv del taller, 2026-10-01)** — `model_json_schema()` sin `additionalProperties` por defecto; con `ConfigDict(extra="forbid")` lo emite; ambos campos en `required`

### Secondary (MEDIUM confidence)
- **WebSearch (2026-10-01)** — flujo de creación de key: console.groq.com/keys → "Create API Key", mostrada una vez, sin tarjeta (corroborado por [Traverba](https://traverba.com/en/groq-api-key), [SfiaiLabs](https://sfailabs.com/guides/how-to-get-groq-api-key), [CrazyRouter](https://crazyrouter.com/en/blog/groq-api-complete-guide-fastest-inference-2026); la página oficial requiere login)
- **04-UAT.md test 2 + addenda** (in-repo, leído este session) — evidencia del 402 real de Google, exigencia de billing, decisión Groq del usuario, probe punta a punta previo, nota TLS truststore del taller, estado del `.env` (GROQ presente / GEMINI removida)

### Tertiary (LOW confidence)
- Ninguna claim de este documento descansa SOLO en fuente terciaria. Las ausencias (sin recomendación de pin oficial; sin doc oficial TLS/Windows del SDK) fueron constatadas fetch-eando README y páginas oficiales este session.

### Carried over (del research original 2026-09-30 — verificado esa session contra in-repo)
- Lecturas in-repo: contrato 0.3.0/0.4.0, ADR-011/015/016/017, guias 05/06/11 (patrones RequireAuth, Settings, responses), docs 02/03, UI-SPECs (tokens/paleta/BADGES), ROADMAP, PROJECT.md — citadas con línea en el documento original; la mitad PANEL se preserva aquí como EJECUTADA.
- In-repo re-verificado ESTE session por grep/lectura dirigida: estructura de guia-14 (headings), conteos de menciones Gemini (guia-14: 67; guia-15: 9; corpus docs+READMEs: 13 archivos), `.env` del taller con GROQ_API_KEY (leído por el probe), 04-VERIFICATION 22/25 con gaps_remaining.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — groq 1.7.0 verificado contra PyPI + README oficial + docs oficiales + probe punta a punta con el SDK exacto que la guía enseñará (la cadena más fuerte posible: registry + doc + runtime)
- Architecture: HIGH — el rework cambia UN motor sobre piezas ya construidas y verificadas; toda pieza nueva (json_schema strict, excepciones, degradación) firmada con probe local del 2026-10-01
- Pitfalls: HIGH — la discrepancia 14.400/1.000 RPD quedó refutada con DOS fuentes independientes (tabla oficial + headers vivos); el resto son lecciones in-repo ya ejecutadas o probes
- Nota de método: el seam `classify-confidence` taguea webfetch/websearch como LOW-MEDIUM genérico; los claims externos descansan en la cadena docs-oficiales + registry + probe-runtime (mismo criterio de triple verificación ya documentado en STACK.md §Sources y en el research original)

**Research date:** 2026-10-01
**Valid until:** 2026-10-15 (rework inmediato: seguro. Ojo con lo que se mueve solo: modelos en /docs/models y la tabla de rate-limits — la guía las cita con "a la fecha" exactamente para eso; el SDK va estable en 1.x)
