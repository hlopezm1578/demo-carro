# Phase 4: Panel de administración y asistente IA - Context

**Gathered:** 2026-09-30
**Status:** Ready for planning

<domain>
## Phase Boundary

**El repositorio sigue guide-only (D-17, fase 1): esta fase entrega DOCUMENTOS, no código.** La fase 4 documenta la etapa 4 del proyecto Maura — que en el ciclo del cliente son DOS peticiones a la vez: **P7 panel de administración** (ADMN-01..04) y **P8 asesora de venta** (AIAS-01..03), ambas ya trazadas a "etapa 4" en docs/02 §13 — y el código vive como bloques dentro de las guías nuevas que el alumno copia. Como documentos, la fase:

- **Extiende `contrato_api.yaml` a 0.4.0 ANTES de escribir las guías (D-15, API-first)** con los endpoints de administración (productos, pedidos, métricas) y del asistente de venta.
- Extiende `docs/02_requerimientos.md` con los requerimientos de la etapa 4 (las filas P7/P8 hoy dicen "llegan con la etapa 4"): CRUD de productos, stock con alerta, gestión de pedidos, métricas, asistente — nuevos RF/RN/HU que continúan las series existentes.
- Extiende `docs/03_diseno.md` con las pantallas nuevas del panel (10+) y la burbuja de chat, y las decisiones de diseño que las citan.
- Extiende `docs/04_arquitectura/adr/` con ADRs nuevos continuando desde ADR-015 (formato demo-cine).
- Extiende `docs/05_desarrollo/` con las guías 12+ bajo la estructura canónica 🧠/✅/📝 y la convención "Gran verificación final".
- Actualiza los READMEs de estado (`docs/README.md`, `README.md` raíz, `docs/05_desarrollo/README.md`).

La verificación de planes es documental (greps/estructura); el UAT runtime es delegado al agente en `D:/Repos/maura-uat` (instrucción persistida en AGENTS.md) sobre la app construida hasta guia-11.

Requisitos cubiertos: ADMN-01, ADMN-02, ADMN-03, ADMN-04, AIAS-01, AIAS-02, AIAS-03.

**Concern abierto (NO decidido en esta discusión, blocker heredado de STATE.md):** los límites RPM/RPD del free tier de Gemini requieren verificación logueada en `aistudio.google.com/rate-limit` — solo el usuario puede hacerla. La guía NO promete cifras de límites sin esa verificación; enseña el manejo del error 429 sin prometer números.

</domain>

<decisions>
## Implementation Decisions

*La numeración D continúa desde la fase 3 (D-01..D-18 en `01-CONTEXT.md`, D-19..D-33 en `02-CONTEXT.md`, D-34..D-49 en `03-CONTEXT.md`).*

### Máquina de estados de pedidos (ADMN-03)
- **D-50:** **Los 4 estados existentes (PENDING / PAID / CANCELLED / REJECTED) — sin estados nuevos.** Nada de "enviado/entregado": la logística física es Out of Scope del proyecto. La máquina de estados completa se documenta con sus transiciones legales y quién puede ejecutar cada una (el flujo de pago posee las suyas; el admin tiene exactamente UNA transición manual): **PENDING→CANCELLED** — la gestión de órdenes huérfanas que D-48/D-49 dejaron explícitamente para esta fase. Cancelar una PENDING no toca stock (D-35: el stock solo se descuenta al aprobar el pago), así que la transición es limpia. **PAID es terminal en v1** — el refund es ADMN-05, diferido a v2. El backend valida la transición pedida contra la máquina (rechaza las ilegales; código exacto a discreción del contrato) — **Reversibility:** costly — el contrato 0.4.0, la RN nueva, el ADR y las guías se estructuran alrededor de qué transiciones existen y quién las ejecuta.

### CRUD de productos (ADMN-01)
- **D-51:** **Imágenes como campo de ruta editable (texto), sin upload de archivos.** El admin edita la ruta (`/products/{sku}.jpg`); no hay multipart ni guardado de archivos. `python-multipart` ya llega en `fastapi[standard]`, pero el upload (multipart, disco, validación de tipo/tamaño) es infraestructura sin lección nueva: el seed ya provee las fotos (D-08) y el alumno las descargó en fase 1. Upload real queda como idea diferida.
- **D-52:** **Soft delete visible y reversible en el panel.** El listado de productos marca activo/inactivo; el admin puede reactivar un producto inactivo con un toggle. Los inactivos desaparecen del catálogo público y de las fichas, pero los pedidos viejos siguen mostrando su snapshot de nombre/precio (D-36) — la lección honesta del soft delete ya diseñado en docs/03 §2.3.5: "un pedido viejo no puede quedar apuntando a un producto borrado".

### Alerta de stock bajo (ADMN-02)
- **D-53:** **Umbral fijo por constante del backend** (propuesto: stock ≤ 5; valor final a discreción), fijado como RN nueva. Superficie de la alerta: badge por producto en el listado admin + contador de productos con stock bajo en métricas (D-54). Sin UI para configurar el umbral — sería una capacidad nueva fuera de ADMN-02.

### Métricas del panel (ADMN-04)
- **D-54:** **Cuatro KPIs en tarjetas + tabla (sin gráficos, locked por requisito):** (1) ingresos totales = suma de órdenes PAID, (2) pedidos por estado (los 4), (3) top 5 productos por unidades vendidas, (4) cantidad de productos con stock bajo (umbral D-53). Todo computable desde las tablas existentes (pedidos + líneas snapshot). **El endpoint demo `/api/admin/estado` (D-33) se reemplaza por el endpoint real de métricas en el contrato 0.4.0**: cumplió su lección de fase 2 (dependencia de seguridad con claim de rol) y la guía narra la evolución — **Reversibility:** costly — cambia un path publicado en 0.3.0 que las guías 05/06 construyeron; la subida a 0.4.0 lo documenta.

### Panel en la SPA
- **D-55:** **Ruta `/admin` con sub-rutas bajo un layout propio del panel** (propuesta: productos, pedidos, métricas; estructura exacta a discreción), protegida por un guard por rol — RequireAdmin que reusa el patrón RequireAuth + returnTo (D-32) sumando el claim de rol desde el primer token (ADR-011). El link "Panel" en el navbar solo es visible con rol admin; una clienta que fuerza `/admin` ve una página de no autorizado — el espejo frontend del 403 que D-33 enseñó en backend.

### Asistente IA: estrategia mini-RAG (AIAS-02)
- **D-56:** **Retrieval trivial y honesto: el catálogo activo completo va en el system prompt de cada request** (12 SKU: id, nombre, familia aromática, notas, precio — cabe entero). Gemini responde **JSON estructurado** (texto de recomendación + ids de productos citados); **el backend valida cada id contra la BD** antes de responder y arma las product cards que el chat muestra clicables (AIAS-02 palabra por palabra). Sin embeddings ni vector store: el catálogo real cabe completo y el Out of Scope ya veta el motor de recomendación propio. La forma exacta de forzar JSON en google-genai 2.25 (`response_mime_type`/`response_schema` o equivalente) **la valida el research contra la doc oficial — no se firma sobre supuestos** (misma lección que D-41 con el spike de Webpay) — **Reversibility:** costly — define el contrato del endpoint de chat, el schema de respuesta y la estructura de las guías.

### Conversación del chat (AIAS-01)
- **D-57:** **Respuesta única request-response, sin streaming.** La lección es la integración del servicio externo y su contrato, no SSE/streaming de tokens.
- **D-58:** **Multi-turno stateless: el frontend mantiene el historial visible y lo envía en cada request.** El backend no guarda conversaciones en BD ni estado de sesión del chat — cero tablas nuevas para el asistente.
- **D-59:** **Endpoint público, sin login** — la asesora atiende a quien navega la tienda (P8: "recomiende aromas del catálogo a cada clienta, como lo haría Maura en persona"), como `/api/pago/retorno` ya es público por diseño. Salvaguardas básicas de input (largo máximo de mensaje y del historial enviado) protegen el free tier. La burbuja flotante vive en el layout de la tienda (visible en las páginas públicas), con panel de chat desplegable — la forma exacta a discreción del UI.

### API key y degradación (AIAS-03)
- **D-60:** **Cada alumno crea SU PROPIA API key gratis en Google AI Studio** — paso del alumno dentro de la guía (mismo patrón que D-08 con las fotos: nada compartido por el proyecto), sin tarjeta de crédito. `GEMINI_API_KEY` vive en el `.env` del backend vía pydantic-settings, como `secret_key` en fase 2 — jamás en código ni en el frontend.
- **D-61:** **Sin key la app arranca normal (degradación, NO fail-fast)** — el asistente es un servicio opcional, a diferencia de `secret_key`: sin key el endpoint responde **503 con mensaje amable** y la burbuja muestra "asistente no disponible"; la tienda sigue 100% operativa. La guía enseña el manejo de errores del servicio externo: **429** (cuota del free tier), timeout / error de red de Gemini → mensaje amable + reintentar (el wrapper atrapa los errores del SDK, jamás un 500 crudo — mismo patrón que IN-06 con `TransbankError`). **AIAS-03 se verifica con grep sobre el build del frontend** (`dist/`) buscando la key sin resultados — pieza fija de la Gran verificación final de la fase.

### Partición de la fase
- **D-62:** **Orden de construcción: contrato 0.4.0 + ADRs primero (D-15), luego panel admin completo (backend → frontend), después asistente IA (backend → burbuja frontend), cerrando con la Gran verificación final de fase 4.** El admin va antes que la IA: el panel no depende del asistente, y la burbuja reusa las product cards del catálogo ya existentes. La partición exacta en sub-guías `guia-12+` es discreción del planner bajo este orden.

### Claude's Discretion
- Nombres y estructura exacta de los endpoints nuevos al extender `contrato_api.yaml` a 0.4.0 (tag Administración: `/api/admin/productos*`, `/api/admin/pedidos*`, `/api/admin/metricas`; tag Asistente: `/api/asistente` vs `/api/chat`; schemas ProductoCrear/ProductoEditar/PedidoTransicion/Metricas/ChatMensaje).
- Qué ADRs escribe la fase y su título exacto (candidatos naturales: panel admin protegido por rol en los dos tiers, máquina de estados de pedidos con transiciones validadas, asistente IA con mini-RAG y key solo en backend), continuando desde ADR-015.
- Numeración nueva de RF/RNF/RN/HU en `02_requerimientos.md` (continuar las series: van RF-19, RNF-08, RN-14, HU-12) y pantallas 10+ de `03_diseno.md` (panel y burbuja).
- Valor exacto del umbral de stock bajo (D-53 propone ≤ 5) y superficie del badge.
- Schema exacto de la respuesta JSON del asistente y forma de forzarlo en google-genai 2.25 (el research lo valida; D-56 fija que existe la validación).
- Estructura de sub-rutas del panel y del layout admin (D-55 fija `/admin` + guard; los paths internos son libres).
- Código HTTP para transición ilegal de pedidos (409 vs 422) y demás detalles finos del contrato.
- Copys del panel, la burbuja y los estados vacíos (tokens y Copywriting Contract de `01-UI-SPEC.md` / `02-UI-SPEC.md`); la voz de la asesora conecta con la persona de Maura (D-02).
- Cómo se parte el trabajo en sub-guías `guia-12+` respetando el orden D-62, y qué incluye la Gran verificación final además del grep del build (tabla CS/RF + fila contrato 0.4.0 ↔ `/docs` con Authorize admin, como siempre).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Planificación del proyecto
- `.planning/PROJECT.md` — Constraints (Gemini vía `google-genai` con key solo en backend, free tier), Key Decisions pendientes (panel admin + asistente IA) y pautas de la exploración (quickstart del SDK, API key gratis sin tarjeta).
- `.planning/REQUIREMENTS.md` — La fase 4 cubre ADMN-01..04 y AIAS-01..03 (ver Traceability); ojo con v2 diferidos que delimitan el alcance: ADMN-05 (refund desde el panel) y STAKE-04 (gráficos en métricas) NO van.
- `.planning/ROADMAP.md` §Phase 4 — Goal, success criteria (el SC 4 ya fija la verificación por grep del build) y límites de la fase.
- `.planning/STATE.md` §Blockers/Concerns — RPM/RPD de Gemini (requiere login del usuario; concern abierto, no decidir cifras).
- `.planning/phases/01-fundaciones-de-dos-tiers-y-cat-logo/01-CONTEXT.md` — Decisiones D-01..D-18 heredadas (D-17 guide-only, D-15 API-first, D-16 sub-guías, D-02 persona de Maura, D-08 fotos).
- `.planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-CONTEXT.md` — Decisiones D-19..D-33 heredadas (D-23/D-24 seed de cuentas, D-32 returnTo, D-33 endpoint demo admin).
- `.planning/phases/03-checkout-webpay-y-rdenes/03-CONTEXT.md` — Decisiones D-34..D-49 heredadas (D-35 stock al aprobar, D-36 snapshot, D-48/D-49 huérfanas → gestión admin en fase 4).

### Docs del ciclo que esta fase extiende
- `docs/02_requerimientos.md` — §13: filas P7/P8 hoy "llegan con la etapa 4"; series a continuar (RF-19+, RNF-08+, RN-14+, HU-12+); actor Admin (dueña) ya definido con P7; RF-17 (estados del pedido) y RN-13 (número legible) son la base que el admin gestiona.
- `docs/03_diseno.md` — §2.3.5 soft delete ya diseñado (D-52 lo implementa); entidades PEDIDO/LÍNEA con snapshot completas; pantallas 8-9 existentes → las 10+ del panel y la burbuja.
- `docs/04_arquitectura/contrato_api.yaml` — 0.3.0, fuente de verdad API-first (D-15/ADR-007): se extiende a 0.4.0 ANTES de las guías; `/api/admin/estado` (D-33) se reemplaza (D-54).
- `docs/04_arquitectura/adr/` — ADRs 001-014 existentes; la fase continúa desde ADR-015 (formato demo-cine). ADR-011 (roles desde el primer token) es la base del guard del panel.
- `docs/05_desarrollo/README.md` — Índice de guías (la fase agrega guia-12+), reglas del alumno.
- `docs/05_desarrollo/guia-11-pedidos-cierre.md` — Último eslabón: su "Siguiente" apunta a la fase 4; su Gran verificación final es el formato que la guía nueva replica.
- `docs/README.md` y `README.md` (raíz) — Tablas de estado del ciclo que avanzan por fase (D-13/D-18).

### Investigación y UI heredadas
- `.planning/research/STACK.md` — google-genai 2.25.0 con pin `>=2.25,<3` (README del SDK: breaking changes en 3.x), patrones `genai.Client`/`generate_content`/config, "what NOT to use" (google-generativeai EOL 2025-11-30).
- `.planning/phases/01-fundaciones-de-dos-tiers-y-cat-logo/01-UI-SPEC.md` y `.planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-UI-SPEC.md` — Tokens de UI Maura y Copywriting Contract que el panel y la burbuja respetan.
- `.planning/phases/03-checkout-webpay-y-rdenes/03-SPIKE-RETORNO.md` — Patrón de "firmar con evidencia" que D-56 exige replicar contra la doc oficial de google-genai antes de escribir la guía del asistente.
- `D:/Repos/demo-cine/docs/` — Referencia externa de formato (repo hermano): estructura y tono de guías y ADRs para replicar.

### Fuentes externas de la integración (para research, no archivos del repo)
- Documentación oficial de la Gemini API y el SDK `python-genai` (github.com/googleapis/python-genai, README main) — validar structured output (JSON), errores del SDK y env var `GEMINI_API_KEY`.
- Google AI Studio (aistudio.google.com) — paso del alumno para crear su key gratis (D-60); la página de rate limits requiere login del usuario (concern abierto).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Ninguno de código — **el repo es guide-only (D-17)**. Los assets reutilizables son patrones documentados:
- Estructura canónica de guías (guia-01..11) y convención "Gran verificación final" (tabla CS/RF + fila contrato ↔ `/docs`) que esta fase replica.
- `contrato_api.yaml` 0.3.0 como fuente de verdad viva a extender (D-15) — ya tiene bearerAuth, roles y la convención de errores.
- Workspace `D:/Repos/maura-uat` con la app construida hasta guia-11 — incluye órdenes reales de los 4 flujos verificados en fase 3 (insumo directo para probar el panel admin) y las cuentas seed admin/clienta (D-23/D-24) para verificar roles en el UAT delegado.

### Established Patterns
- Backend en capas routers → services → repositories con sesión inyectada; routers sin SQLAlchemy; solo `main.py` arma la app.
- Seed converge por upsert (SKU, email); numeración trazable P/RF/RN/HU → ADRs → guías continua (P7/P8 ya reservadas a etapa 4).
- Todo HTTP del frontend por `lib/api.ts` (Bearer + interceptor 401, D-22); stores Zustand con persist.
- RequireAuth + returnTo (D-32) es el patrón que RequireAdmin extiende con el claim de rol (ADR-011).
- Estados del pedido PENDING/PAID/CANCELLED/REJECTED (RF-17) y snapshot de líneas (D-36) — la base de datos que las métricas y la máquina de estados administran.

### Integration Points
- Navbar de guia-06: gana el link "Panel" (solo admin, D-55); el layout de la tienda gana la burbuja del asistente (D-59).
- `/api/admin/estado` (D-33, guias 05/06): se reemplaza por el endpoint de métricas real (D-54) — cambio narrado en la guía.
- `guia-11-pedidos-cierre.md` es el eslabón previo; la fase agrega guia-12+ y actualiza su "Siguiente".
- Contrato 0.3.0 → 0.4.0: tags nuevos de administración y asistente antes de toda guía (D-15).
- El historial de pedidos del cliente (guia-11) ya muestra PENDING "en curso" — la cancelación del admin (D-50) se refleja ahí como CANCELLED sin editar la guía anterior.

</code_context>

<specifics>
## Specific Ideas

- Umbral de stock bajo propuesto: **≤ 5 unidades** (valor final a discreción, D-53).
- Las 4 tarjetas de métricas: ingresos PAID, pedidos por estado, top 5 por unidades, count stock bajo (D-54).
- Gran verificación final de fase 4: tabla numerada CS/RF + fila contrato 0.4.0 ↔ `/docs` (Authorize admin) **+ grep del build del frontend sin rastro de `GEMINI_API_KEY`** (AIAS-03).
- La asesora recomienda por familia aromática y notas (el eje del catálogo desde D-05) hablando con la voz de Maura (D-02) — ej. "si te gusta lo cítrico…".
- El admin anula una PENDING huérfana → la clienta la ve CANCELLED en su historial sin re-ediciones de la guía 11.
- Sin `GEMINI_API_KEY` en el `.env`: burbuja visible pero responde "asistente no disponible" (503 amable, D-61) — la tienda nunca depende de la IA para operar.

</specifics>

<deferred>
## Deferred Ideas

- **Upload de imágenes de producto desde el panel** (multipart + guardado en disco) — fuera de ADMN-01 por D-51; candidato natural para v2 si el curso lo pide.
- **Refund/anulación de pago PAID desde el panel** — ya está en REQUIREMENTS v2 como ADMN-05; D-50 lo deja explícitamente fuera.
- **Gráficos en las métricas del panel** — ya está en v2 como STAKE-04; ADMN-04 fija tarjetas + tabla.
- **Streaming de la respuesta del chat** — descartado por D-57 para esta fase; sería una adición posterior sobre el mismo endpoint.

</deferred>

---

*Phase: 4-Panel de administración y asistente IA*
*Context gathered: 2026-09-30*
