# Phase 3: Checkout Webpay y órdenes - Context

**Gathered:** 2026-09-30
**Status:** Ready for planning

<domain>
## Phase Boundary

**El repositorio sigue guide-only (D-17, fase 1): esta fase entrega DOCUMENTOS, no código.** La fase 3 documenta la etapa 3 del proyecto Maura — checkout con Webpay Plus sandbox y órdenes — y el código vive como bloques dentro de las guías nuevas que el alumno copia. Como documentos, la fase:

- **Empieza resolviendo el spike de retorno de Webpay** (runtime en `D:/Repos/maura-uat`, patrones de los 4 flujos con credenciales públicas de integración) ANTES de redactar contrato, ADRs y guías — lo exige el ROADMAP y lo repite STATE.md como blocker.
- Extiende `docs/02_requerimientos.md` con los requerimientos de la etapa 3 (la fila P6 hoy dice "sin requerimiento en esta etapa"): pago con Webpay (PAY-01..04), recalculo del carro (CART-03) y órdenes (ORDR-01/02) — nuevos RF/RN/HU que continúan las series existentes.
- Extiende `docs/03_diseno.md` con el modelo de datos de pedidos (las entidades Producto/Usuario ya esperan a los pedidos para conectarse por relaciones nuevas) y las pantallas nuevas (resultado de pago/voucher, historial de pedidos).
- Extiende `docs/04_arquitectura/` con ADRs nuevos (retorno de Webpay, ciclo de vida de la orden y stock) continuando desde ADR-012, y **extiende `contrato_api.yaml` ANTES de escribir las guías (D-15, API-first)** con los endpoints de checkout/pago y pedidos.
- Extiende `docs/05_desarrollo/` con las guías 09+ bajo la estructura canónica 🧠/✅/📝 y la convención "Gran verificación final".
- Actualiza los READMEs de estado (`docs/README.md`, `README.md` raíz, `docs/05_desarrollo/README.md`).

La verificación de planes es documental (greps/estructura); el UAT runtime es delegado al agente en `D:/Repos/maura-uat` (instrucción persistida en AGENTS.md). El spike corre también ahí — el código del spike JAMÁS se commitea en este repo.

Requisitos cubiertos: CART-03, PAY-01, PAY-02, PAY-03, PAY-04, ORDR-01, ORDR-02.

Aclaración operativa (consulta del usuario en esta discusión): la integración Webpay NO requiere crear cuenta ni registrarse en Transbank — las credenciales del ambiente de integración son públicas (código de comercio 597055555532, host `webpay3gint.transbank.cl`), el SDK viene preconfigurado y el pago de prueba usa tarjetas documentadas por Transbank. La guía debe dejar esto explícito para el alumno.

</domain>

<decisions>
## Implementation Decisions

*La numeración D continúa desde la fase 2 (D-01..D-18 en `01-CONTEXT.md`, D-19..D-33 en `02-CONTEXT.md`).*

### Ciclo de vida de la orden y stock (el ADR pendiente de STATE.md)
- **D-34:** **La orden nace al iniciar el pago.** `POST /api/checkout` (nombre exacto a discreción) valida el carro recalculando precios y stock contra el catálogo (CART-03), crea la orden PENDING con sus líneas, y recién entonces crea la transacción en Webpay y devuelve el form POST con token+url. Los flujos de retorno solo actualizan esa orden existente. Es el patrón natural con Webpay (el commit necesita mapear token→orden) y explica por qué PENDING existe en ORDR-01 — **Reversibility:** costly — el modelo de datos, los 4 flujos del retorno, la idempotencia y las guías se estructuran alrededor del momento de nacimiento de la orden.
- **D-35:** **Stock: validar al crear, descontar atómico al aprobar.** Crear la orden PENDING solo VALIDA que el stock alcance (sin tocarlo, RN-09 es la primera barrera en pantalla; esta es la segunda en backend). El descuento real ocurre en el commit aprobado, atómico y transaccional (UPDATE condicional `stock >= cantidad` o equivalente que el research valide para SQLite). Si una compra concurrente ganó el stock en el intertanto, el commit falla y la orden pasa a REJECTED — la lección real de concurrencia de ORDR-02. Sin "reserva" previa: no está en los requisitos y duplica los puntos donde se toca el stock — **Reversibility:** costly — toca el servicio de checkout, el commit, el contrato y la lección de concurrencia de las guías.
- **D-36:** **Las líneas de la orden guardan snapshot de precio y nombre** congelados al momento de comprar. El pedido viejo muestra siempre lo que se pagó aunque el catálogo cambie después. La asimetría con RN-08 es la lección: en el CARRO el precio guardado es un precio viejo esperando engañar (prohibido); en la ORDEN es el histórico (obligatorio). Calza con el soft delete ya diseñado en docs/03 ("un pedido viejo no puede quedar apuntando a un producto borrado") — **Reversibility:** costly — cambia el modelo de `order_items` que citan contrato, diseño y guías.
- **D-37:** **Número de pedido legible que a la vez es el buy_order.** La orden genera un número público (ej. `MAURA-000001`) que se envía a Webpay como `buy_order` (límite 26 chars, único por transacción) y es el que la clienta ve en voucher e historial — jamás el id interno de la BD. Lección: identificador público ≠ clave primaria. El formato exacto (prefijo, dígitos, ceros) es discreción sujeta a los límites de Transbank.

### Spike de retorno (resuelve STATE.md blocker #1)
- **D-38:** **El spike es el primer plan de la fase y corre runtime en `D:/Repos/maura-uat`** (patrón del UAT delegado ya autorizado): mini-backend con el SDK Python + credenciales públicas de integración, que corre los flujos reales y documenta qué llega por GET vs POST con qué parámetros. Sus hallazgos alimentan contrato, ADRs y guías. El código del spike no se commitea acá (D-17).
- **D-39:** **El spike corrobora los 4 flujos oficiales de una vez**: aprobado (vuelve con `token_ws` por GET), anulado (`token_ws` por GET tras anular en el formulario), timeout (`TBK_ID_SESION` por POST) y error de formulario (`TBK_TOKEN`/`TBK_ORDEN_COMPRA` por POST). PAY-02 exige discriminar los 4 — la guía nace sin zonas oscuras y el UAT final no descubre nada nuevo. (El ROADMAP fijaba 3; se amplía al 4° por costo marginal mínimo.)
- **D-40:** **Los hallazgos viven en `.planning/`** (documento del spike con los parámetros de cada flujo, GET vs POST) como insumo del planner; la GUÍA narra el descubrimiento como "lo que el spike reveló" (el alumno ve el resultado, no el documento interno) y el ADR de retorno lo cita como evidencia.
- **D-41:** **La mecánica exacta del retorno la decide el spike con evidencia** (la más simple que funcione para los 4 flujos — p. ej. redirect 302 del backend a la SPA con query params vs página intermedia que auto-submitea el POST a la SPA). El ADR registra la elegida con la evidencia de cada flujo. Nadie firma mecánica hoy sobre supuestos: es exactamente el riesgo que el spike existe para matar.

### Vuelta a la SPA: voucher y carro
- **D-42:** **Ruta única de resultado** (p. ej. `/pago/resultado`) que renderiza voucher de éxito, anulado, timeout o error según el flujo discriminado. Espeja lo que hace el backend (un endpoint GET+POST que discrimina) — la misma lección en los dos tiers — **Reversibility:** costly — toca el router, el endpoint de retorno y las guías.
- **D-43:** **El voucher ES el detalle completo del pedido**: número legible (buy_order), fecha, líneas con nombre y precio snapshot, total, estado PAID y CTA "Seguir comprando". La vista de detalle del historial reutiliza el mismo componente — se construye una vez y el historial la hereda gratis.
- **D-44:** **El carro se limpia en UN solo punto: cuando el pago aprueba** (al llegar al voucher). En anulado, timeout y error de formulario queda intacto — la clienta reintenta sin rearmar nada. PAY-04 ("restituido si fue anulado") se implementa de la forma más simple posible: no hubo que restituir porque nunca se borró. Sin snapshots de carro ni lógica de restauración.
- **D-45:** **Los copys de las pantallas de la vuelta quedan a discreción** de las guías/UI-SPEC de la fase, con el tono Maura ya establecido (como la fase 2 fijó "Tu sesión expiró, ingresa de nuevo" en su momento).

### Historial de pedidos
- **D-46:** **Lista + detalle navegable**: página `/pedidos` con las órdenes de la clienta (número, fecha, total, badge de estado) y al hacer clic se abre el detalle, que reutiliza la vista del voucher (D-43). Patrón lista→detalle clásico.
- **D-47:** **"Mis pedidos" en el navbar**, visible con sesión iniciada, junto al nombre/cerrar sesión que la fase 2 construyó. Ruta protegida con el mismo RequireAuth + returnTo (D-32) que se hereda gratis.
- **D-48:** **El historial muestra TODAS las órdenes de la clienta con su estado real — PENDING incluida** ("en curso": saltó a Webpay y no volvió). La honestidad del estado es la lección de ORDR-01; nada se oculta. La gestión de huérfanas es del admin (fase 4).
- **D-49:** **Sin expiración de PENDING en fase 3**: una orden huérfana queda visible tal cual y su gestión (anular/cerrar) llega con el panel admin de la fase 4. La guía no enseña jobs de fondo ni ventanas de tiempo.

### Claude's Discretion
- Formato exacto del número de pedido legible (prefijo, dígitos, relleno), sujeto al límite de 26 chars y unicidad que exige Transbank (D-37 fija que exista).
- Nombres y estructura exacta de los endpoints nuevos al extender `contrato_api.yaml` (tag Pedidos/Pago, `/api/checkout` vs `/api/pagos`, `/api/pedidos` vs `/api/ordenes`; schemas Orden/OrdenLínea/CheckoutRespuesta).
- Qué ADRs escribe la fase y su título exacto (candidatos naturales: retorno de Webpay con la mecánica elegida por el spike, orden nace al iniciar el pago + stock al aprobar, snapshot de precio en la orden), continuando desde ADR-012.
- Numeración nueva de RF/RNF/RN/HU en `02_requerimientos.md` (continuar las series: van RF-11, RNF-06, RN-09, HU-08) y cómo se parte el trabajo en sub-guías `guia-09+`.
- Mecánica concreta del stock atómico en SQLite (UPDATE condicional vs transacción serializada) — el research la valida contra SQLAlchemy 2.1 y la guía enseña el patrón verificado.
- Qué implementa mínimamente el mini-backend del spike (alcance mínimo que corrobore los 4 flujos sin construir la app completa).
- Badges/colores por estado del pedido y copys de la vuelta (D-45) siguiendo los tokens de `01-UI-SPEC.md` / `02-UI-SPEC.md`.
- Cómo la guía explica al alumno que Transbank integración no requiere registro (credenciales públicas) y qué tarjetas de prueba documentadas usar en cada flujo.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Planificación del proyecto
- `.planning/PROJECT.md` — Contexto, constraints (Webpay sandbox, credenciales públicas sin registro) y decisiones clave (guide-only, guide-only D-17).
- `.planning/REQUIREMENTS.md` — Requisitos v1; la fase 3 cubre CART-03, PAY-01..04, ORDR-01/02 (ver Traceability).
- `.planning/ROADMAP.md` §Phase 3 — Goal, success criteria y límites de la fase; el spike vive dentro de la fase ANTES de la guía.
- `.planning/STATE.md` §Blockers/Concerns — Los dos blockers de fase 3 que esta discusión resuelve (spike de retorno; momento de creación de orden y descuento de stock).
- `.planning/phases/01-fundaciones-de-dos-tiers-y-cat-logo/01-CONTEXT.md` — Decisiones D-01..D-18 heredadas (D-17 guide-only, D-15 API-first, D-16 sub-guías).
- `.planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-CONTEXT.md` — Decisiones D-19..D-33 heredadas (D-22 interceptor 401, D-27 carro sin precios, D-31 checkout esperando el pago, D-32 returnTo).

### Docs del ciclo que esta fase extiende
- `docs/02_requerimientos.md` — Fila P6 hoy "sin requerimiento en esta etapa": la fase escribe RF/RNF/RN/HU de la etapa 3 continuando las series; RN-08/RN-09 ya preparan CART-03.
- `docs/03_diseno.md` — Entidades Producto/Usuario esperan a los pedidos para conectarse (relaciones nuevas, soft delete ya diseñado); pantallas 8+ de la vuelta y el historial.
- `docs/04_arquitectura/contrato_api.yaml` — Fuente de verdad API-first (D-15/ADR-007), versión 0.2.0 con bearerAuth: se extiende ANTES de las guías.
- `docs/04_arquitectura/adr/` — ADRs 001-011 existentes; la fase continúa desde ADR-012 (formato demo-cine).
- `docs/05_desarrollo/README.md` — Índice de guías (la fase agrega guia-09+), reglas del alumno, mapa mental de la serie.
- `docs/05_desarrollo/guia-08-checkout.md` — La pantalla checkout con CTA "Pagar con Webpay" deshabilitado que esta fase activa (D-31).
- `docs/README.md` y `README.md` (raíz) — Tablas de estado del ciclo que avanzan por fase (D-13/D-18).

### Investigación y UI heredadas
- `.planning/research/STACK.md` — transbank-sdk Python 6.1.0 (sync `requests` → rutas sync), credenciales públicas de integración (commerce code 597055555532 vs `webpay3gint.transbank.cl`), patrón "what NOT to use".
- `.planning/phases/01-fundaciones-de-dos-tiers-y-cat-logo/01-RESEARCH.md` — Patrones backend verificados en runtime (capas, sesión inyectada, seed) que las guías nuevas citan.
- `.planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-RESEARCH.md` — Patrones verificados de cuentas/carro (JWT, stores persist) heredados por las guías 09+.
- `.planning/phases/01-fundaciones-de-dos-tiers-y-cat-logo/01-UI-SPEC.md` y `.planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-UI-SPEC.md` — Tokens de UI Maura y Copywriting Contract que las pantallas nuevas respetan.
- `D:/Repos/demo-cine/docs/` — Referencia externa de formato (repo hermano): estructura y tono de guías y ADRs para replicar.

### Fuentes externas de la integración (para research/spike, no archivos del repo)
- Documentación oficial Webpay Plus REST y SDK Python en transbankdevelopers.cl — el spike corrobora contra el comportamiento REAL del ambiente de integración, no contra la docs sola.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Ninguno de código — **el repo es guide-only (D-17)**. Los assets reutilizables son patrones documentados:
- Estructura canónica de guías (guia-01..08) y convención "Gran verificación final" (tabla CS/RF + fila contrato ↔ `/docs`) que esta fase replica.
- `contrato_api.yaml` 0.2.0 con bearerAuth como fuente de verdad viva a extender.
- Workspace `D:/Repos/maura-uat` con la app construida hasta guia-08 (backend en capas + frontend con carro/checkout protegido) sobre la que corren el spike y el UAT delegado.

### Established Patterns
- Backend en capas routers → services → repositories con sesión inyectada; routers sin SQLAlchemy; solo `main.py` arma la app.
- Seed converge por upsert a estado canónico; numeración trazable P/RF/RN/HU → ADRs → guías continua en esta fase.
- Todo HTTP del frontend por `lib/api.ts` (interceptor 401, Bearer); stores Zustand con persist; comandos agnósticos de terminal (D-12).
- El carro guarda solo `[{producto_id, cantidad}]` y se hidrata con precios vigentes (D-27/RN-08) — la base exacta que CART-03 consolida.

### Integration Points
- Pantalla `/checkout` de guia-08 con CTA "Pagar con Webpay" deshabilitado (D-31): la fase lo activa hacia el form POST auto-submit.
- `lib/api.ts` hereda el flujo autenticado del checkout (Bearer + interceptor 401).
- Navbar de guia-06 gana "Mis pedidos" (D-47) junto al estado de sesión existente.
- El endpoint de retorno (GET+POST) es el primer endpoint del backend que responde a navegaciones full-page del navegador externo (Webpay), no a `fetch` de la SPA — la lección central del spike.
- Entidades Producto/Usuario reciben sus primeras relaciones (orders, order_items) — docs/03 las tenía reservadas.

</code_context>

<specifics>
## Specific Ideas

- Número de pedido de ejemplo canónico: `MAURA-000001` (formato final a discreción, D-37).
- El voucher muestra: número, fecha, líneas (nombre + precio snapshot), total, estado PAID, CTA "Seguir comprando".
- PENDING se muestra al usuario como "en curso" (u otro copy a discreción) — honestidad de estado como lección.
- La asimetría carro/orden como momento pedagógico: precio prohibido en el carro (RN-08), precio obligatorio en la orden (D-36).
- La guía debe explicar que Transbank integración NO requiere registro (credenciales públicas 597055555532) y qué tarjetas de prueba usar por flujo — surgió de la consulta del usuario en esta discusión.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 3-Checkout Webpay y órdenes*
*Context gathered: 2026-09-30*
