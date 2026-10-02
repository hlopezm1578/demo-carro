# Phase 3: Checkout Webpay y órdenes - Research

**Researched:** 2026-09-30
**Domain:** Integración Webpay Plus REST (transbank-sdk Python 6.1.0, ambiente de integración) + ciclo de vida de órdenes con stock transaccional (SQLAlchemy 2.1 + SQLite) + retorno del navegador externo a una SPA — documentados como guías paso a paso en un repo guide-only (D-17); extensión de docs del ciclo (02 requerimientos, 03 diseño, 04 arquitectura/contrato 0.3.0, 05 guías 09+); spike de retorno runtime en `D:/Repos/maura-uat` como PRIMER plan de la fase (D-38)
**Confidence:** HIGH

## Summary

La fase 3 es el corazón de la guía: el pago real (sandbox) de extremo a extremo. Como las fases 1-2, entrega DOCUMENTOS (D-17): extiende `docs/02_requerimientos.md` (etapa 3: PAY/CART-03/ORDR continuando las series), `docs/03_diseno.md` (entidades PEDIDO/LÍNEA que conectan USUARIO↔PRODUCTO — docs/03 las tenía reservadas — y pantallas 8+ de la vuelta y el historial), `docs/04_arquitectura/` (contrato 0.2.0→0.3.0 ANTES de las guías, D-15; ADRs desde ADR-012) y `docs/05_desarrollo/` (guías 09+). El spike de retorno corre ANTES de todo lo demás (D-38, ROADMAP, STATE.md blocker #1) en `D:/Repos/maura-uat` y sus hallazgos viven en `.planning/` (D-40).

Esta investigación resolvió los tres frentes técnicos que el planner y el spike necesitan: **(1) El flujo de retorno oficial, verbatim desde transbankdevelopers.cl + el código del plugin oficial de Transbank para WooCommerce.** Los 4 flujos existen tal como CONTEXT los lista, con dos correcciones materiales: el flujo **anulado llega con `TBK_TOKEN` (no `token_ws`)** y en integración llega **por POST**; y el flujo **error de formulario es "replicable solo en producción"** según la propia documentación — el spike runtime corroborará 3 flujos, el 4° queda documentado por las docs + el patrón del plugin oficial (rama `token_ws`+`TBK_TOKEN` juntos). El plugin oficial además entrega el orden exacto de discriminación y el guard anti doble-procesamiento (`checkIsAlreadyProcessed`). **(2) El SDK Python 6.1.0 leído en fuente:** instancia vía `Transaction.build_for_integration(IntegrationCommerceCodes.WEBPAY_PLUS, IntegrationApiKeys.WEBPAY)`, validaciones client-side 26/61/255 chars (buy_order/session_id/return_url), `amount: float`, errores tipados (`TransactionCommitError`), credenciales públicas hardcodeadas en constantes (sin registro ni `.env`). **(3) El criterio de aprobación es literal el de PAY-03:** "confirmar que el código de respuesta `response_code` sea exactamente `0` y que el estado `status` sea exactamente `AUTHORIZED`" — cita que el ADR y la guía reproducen. El stock atómico usa UPDATE condicional + rowcount dentro de la MISMA transacción del commit (patrón SQLAlchemy 2.x documentado).

**Primary recommendation:** Planificar en 4 ondas: **(A) spike primero** (mini-backend en maura-uat, credenciales públicas, corrobora aprobado/anulado/timeout + documenta el 4° desde las docs; hallazgos a `.planning/`); **(B) docs 02/03 + contrato 0.3.0 + ADRs 012+** (API-first, D-15 — el ADR de retorno cita la evidencia del spike, D-40/D-41); **(C) guías 09+** (backend órdenes/Webpay → vuelta SPA/voucher → historial + Gran verificación final con los 4 flujos runtime); **(D) READMEs de estado**. El endpoint de retorno es GET+POST público que discrimina los 4 flujos y responde **302** (no 307, que es el default de `RedirectResponse` y re-POSTea) hacia la ruta única de resultado de la SPA (D-42).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
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

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CART-03 | El backend recalcula y valida precios y stock del carro al crear la orden — nunca confía en los valores del cliente | `POST /api/checkout` (D-34): el service recibe SOLO `[{producto_id, cantidad}]` (D-27 — el carro ya no guarda precios, RN-08), consulta el catálogo por id, recalcula total desde precio vigente y valida stock >= cantidad (400, regla de negocio). La entrada no tiene campo precio que confiar: recalculo por construcción [VERIFIED: docs/02_requerimientos.md:126 RN-08 "El carro guarda **solo identificadores de producto y cantidades**"]. Docs/03 ya lo anunciaba: "el backend recalculará el pedido completo sin confiar en lo que el navegador mande" [VERIFIED: docs/03_diseno.md:132-138] |
| PAY-01 | Redirigido a Webpay Plus (integración) mediante form POST auto-submit con el token | `Transaction.build_for_integration(...).create(buy_order, session_id, amount, return_url)` devuelve `{url, token_ws}` [VERIFIED: SDK fuente + docs oficiales]; la SPA construye un `<form method="POST" action={url}>` con `<input name="token_ws" value={token}>` y lo submitea — patrón textual de las docs oficiales ("Con estos datos debes crear un formulario en el cual debes poner un `input` de nombre `token_ws`...") [CITED: transbankdevelopers.cl/documentacion/webpay-plus] |
| PAY-02 | El retorno llega a un endpoint del backend (GET+POST) que discrimina los 4 flujos y redirige a la SPA | Discriminador verbatim del plugin oficial de Transbank (orden de ramas + params de cada flujo — Pattern 3); endpoint GET+POST público; respuesta 302 (NO 307) a la ruta única de resultado (D-41/D-42). Los 4 flujos documentados [CITED: docs oficiales + VERIFIED: CommitWebpayController del plugin oficial]. El spike corrobora runtime (D-38/D-39) |
| PAY-03 | Orden pagada solo con `response_code == 0` y `status == AUTHORIZED`; idempotencia anti doble-commit | Criterio oficial verbatim: "confirmar que el código de respuesta `response_code` sea exactamente `0` y que el estado `status` sea exactamente `AUTHORIZED`" [CITED: docs oficiales]. Idempotencia OUR-side: guard de estado de la orden (si ya PAID → re-mostrar sin side effects) + descuento y transición en UNA transacción — mismo patrón `checkIsAlreadyProcessed` del plugin oficial [VERIFIED: CommitWebpayController]. La idempotencia del commit de Webpay es [ASSUMED] (consenso de comunidad, no documentado verbatim) — el diseño NO depende de ella |
| PAY-04 | Voucher de la tienda (no de Transbank) tras el pago; carro restituido si fue anulado | Recomendación oficial: "ya no se debe mostrar el voucher de Transbank, solo debe mostrarse desde el sitio del comercio" [CITED: docs oficiales]. Voucher = detalle del pedido (D-43); carro se limpia SOLO al aprobar (D-44) — la restitución de PAY-04 es "nunca se borró" |
| ORDR-01 | Historial de pedidos con estados visibles (PENDING / PAID / CANCELLED / REJECTED) | Modelo Pedido con `estado` enum (4 valores, nombre==valor — el gotcha del enum ya cerrado dos veces); `GET /api/pedidos` + `GET /api/pedidos/{numero}` protegidos por Bearer con ownership (404 si no es de la clienta); `/pedidos` lista→detalle reutilizando el voucher (D-46); PENDING visible como "en curso" (D-48) |
| ORDR-02 | Stock descontado de forma atómica y transaccional al aprobarse, sin oversell ante compras concurrentes | UPDATE condicional `WHERE stock >= cantidad` + `rowcount` dentro de la transacción del commit aprobado (Pattern 5) — "The value returned is the number of rows matched by the WHERE clause" [CITED: docs.sqlalchemy.org]; rowcount 0 → stock perdido por concurrente → orden REJECTED (D-35). SQLite serializa escrituras; el UPDATE es atómico en el motor |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

No existe `./CLAUDE.md` ni `./.zcode/CLAUDE.md` [VERIFIED: `ls` esta sesión]. Las instrucciones del proyecto viven en `D:/Repos/demo-carro/AGENTS.md` (workspace instructions). Directivas accionables para el planner:

- **Repo guide-only (D-17/ADR-008):** esta fase escribe SOLO documentos (`docs/**`, `.planning/**`). Jamás código de aplicación en el repo; el código vive como bloques dentro de las guías. Verificación de planes: documental (greps/estructura). **El código del spike tampoco se commitea acá** (D-38) — sus hallazgos sí, como documento en `.planning/` (D-40).
- **UAT delegado al agente** en `D:/Repos/maura-uat` (instrucción persistida en AGENTS.md): el spike corre ahí; el UAT runtime de la fase (los 4 flujos en el navegador) también, con Node portátil v22.23.3. **Bugs: se corrigen SIEMPRE en los dos lugares** — maura-uat Y la guía `docs/05_desarrollo/*`. Autorización explícita para editar guías directamente cuando son fixes de bugs.
- **Stack versionado autoritativo** (AGENTS.md / `.planning/research/STACK.md`): transbank-sdk Python 6.1.0 (verificado vigente esta sesión en PyPI), sync `requests` → **rutas sync (`def`, no `async def`)** para Webpay. SQLAlchemy 2.1.1, FastAPI 0.141.1. "What NOT to use" se mantiene (python-jose, passlib, Stripe, google-generativeai viejo).
- **Sin emojis en comunicación con el usuario** (los docs de la guía usan sus marcadores propios 🧠/✅/📝 — contenido del producto).
- **Comandos de guías agnósticos de terminal (D-12).**
- **Respuestas en español chileno, tuteo** (convención del producto ya establecida).
- **Contrato API-first (D-15/ADR-007):** `contrato_api.yaml` se extiende y aprueba ANTES de las guías; el cierre de fase verifica contrato ↔ `/docs` (Gran verificación final).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Crear transacción Webpay (create) | API / Backend | — | La API key/comercio viven solo en el backend; el cliente jamás habla con Webpay directamente. SDK sync → ruta sync |
| Nacer la orden PENDING + validar carro recalculado (CART-03) | API / Backend | — | El servidor es la única autoridad de precios/stock (RN-08/RN-09 prepararon exactamente esto) |
| Form POST auto-submit hacia Webpay | Browser / Client | — | El navegador navega a Webpay: la SPA construye y submitea el form con token_ws (PAY-01) |
| Recibir el retorno del navegador (GET+POST, 4 flujos) | API / Backend | — | El endpoint responde al NAVEGADOR externo, no a la SPA — la primera respuesta no-JSON del proyecto (302) |
| Commit + criterio de aprobación (PAY-03) | API / Backend | — | `response_code == 0 && status == AUTHORIZED` se evalúa en el servidor; el cliente solo recibe el resultado |
| Descuento atómico de stock (ORDR-02) | API / Backend (SQLite) | — | UPDATE condicional + rowcount en la transacción del commit; el motor serializa la escritura |
| Voucher + pantallas de resultado | Browser / Client (SPA) | — | Ruta única `/pago/resultado` (D-42) que fetcha el pedido autenticado; voucher propio, no el de Transbank |
| Limpiar el carro al aprobar | Browser / Client | — | El carro vive en localStorage (D-27): solo el cliente puede limpiarlo (D-44) |
| Historial de pedidos (lista/detalle) | API / Backend (datos + ownership) | Browser / Client (render) | `/api/pedidos` protegido por Bearer; la validación de dueño es del servidor (404), no del render |
| Discriminación de flujos (UX espejo) | Browser / Client | API / Backend | La misma tabla de 4 flujos vive en los dos tiers — la lección central (D-42) |
| Spike de retorno (runtime) | Workspace externo (`D:/Repos/maura-uat`) | — | D-38: primer plan de la fase; hallazgos a `.planning/` (D-40) |
| ADRs + contrato 0.3.0 | Documentación (`docs/04_arquitectura/`) | — | ANTES de las guías (D-15); el ADR de retorno cita la evidencia del spike |

## Standard Stack

> Fuente base: `.planning/research/STACK.md` (verificado 2026-09-28). Ítems re-verificados contra registro/fuente esta sesión (2026-09-30).

### Nuevos paquetes que las guías enseñan a instalar (fase 3)

| Library | Version | Registry check (esta sesión) | Purpose | Why Standard |
|---------|---------|------------------------------|---------|--------------|
| transbank-sdk | 6.1.0 | PyPI JSON API → 6.1.0, publicada 2025-06-24 [VERIFIED: pypi.org] | Webpay Plus REST (create/commit/status) en ambiente de integración | Único SDK oficial (repo `TransbankDevelopers/transbank-sdk-python`, exigido por PROJECT.md); ya fijado en STACK.md con verificación previa en PROJECT.md. README: "Python 3.12+" [VERIFIED: GitHub README fetch esta sesión] — calza con el techo Python 3.12 del backend |

**Instalación que las guías narran (comandos del alumno):**

```bash
# Backend (desde backend/ del proyecto del alumno)
uv add transbank-sdk
```

**No hay otros paquetes nuevos.** El resto de la fase reutiliza lo ya instalado en las guías 1-8: FastAPI, SQLAlchemy 2.1, python-multipart (crítico acá: parsea el POST del retorno de Webpay — misma pieza que parsea el form de login de la fase 2), PyJWT (Bearer del checkout/pedidos), Zustand persist (carro que sobrevive el full-page load de Webpay, CART-02 ya lo garantizó), TanStack Query, React Router 8.

**Nota de versiones:** transbank-sdk 6.1.0 es la misma versión que registró STACK.md en la exploración (publicada 2025-06-24, sin cambios) — estable. `pip index versions transbank-sdk` no es necesario; el JSON API de PyPI confirmó esta sesión que 6.1.0 sigue siendo `latest`.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| SDK Python transbank | REST crudo (httpx contra `/rswebpaytransaction/api/webpay/v1.2`) | El REST crudo es didáctico para ver el contrato, pero el SDK es la vía oficial mantenida, ya validada client-side (26/61/255) y con errores tipados. La guía puede MOSTRAR qué hace el SDK por debajo (endpoint + PUT del commit) sin dejar de usarlo |
| UPDATE condicional + rowcount | `SELECT ... FOR UPDATE` / transacción serializada BEGIN IMMEDIATE | SQLite no tiene `FOR UPDATE` (lock es a nivel de archivo de BD al escribir); el UPDATE condicional es el patrón portable y el que la discretion de CONTEXT pide validar. Ver Pattern 5 |
| Redirect 302 del backend a la SPA (D-41 candidato) | Página intermedia HTML que auto-submitea el POST a la SPA | El 302 es más simple y es lo que hace el plugin oficial (wp_redirect). El POST a la SPA exige una ruta que lea el body del form en el navegador — más piezas, cero ganancia. **El spike firma la decisión con evidencia (D-41)** |
| Ruta única de resultado (D-42) | Una ruta por flujo (/pago/exito, /pago/anulado...) | Ruta única = discriminación en un solo lugar, espejo del backend, voucher/anulado/timeout comparten estados de carga. Locked por CONTEXT |

## Package Legitimacy Audit

> Protocolo ejecutado vía seam `package-legitimacy check` esta sesión. Mismo artefacto de ambiente documentado en STACK.md/02-RESEARCH: PyPI no expone weekly-downloads (`unknown-downloads` es inherente) y el seam marca SUS por eso.

| Package | Registry | Age | Downloads | Source Repo | Verdict (seam) | Disposition |
|---------|----------|-----|-----------|-------------|----------------|-------------|
| transbank-sdk | pypi | ~5 años desde v1 (6.x desde 2023; 6.1.0 publicada 2025-06-24) | n/d (PyPI no expone) | github.com/TransbankDevelopers/transbank-sdk-python | SUS (artefacto: `unknown-downloads`; repo oficial presente, no deprecado) | Approved — cross-check autoritativo: es el SDK oficial que ordena la documentación de Transbank [CITED: transbankdevelopers.cl], exigido por la constraint de PROJECT.md ("SDK oficial Python `transbank-sdk`"), ya verificado en la exploración previa registrada en PROJECT.md. Sin postinstall (n/a en PyPI) |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** transbank-sdk por el seam — veredicto explicado como artefacto de métricas PyPI (idéntico patrón que pyjwt/pwdlib en la fase 2); respaldado por las fuentes más autoritativas posibles (docs oficiales de Transbank + PROJECT.md ya verificado). No se exige `checkpoint:human-verify`; si el planner prefiere el gate conservador, es barato de añadir.

## Architecture Patterns

### System Architecture Diagram

```
     FLUJO 1 — IDA: CHECKOUT → ORDEN PENDING → WEBPAY (PAY-01, CART-03, D-34)
     ═════════════════════════════════════════════════════════════════════

  [Clienta en /checkout]
        │ CTA "Pagar con Webpay" (enciende el deshabilitado de guia-08, D-31)
        ▼
   POST /api/checkout  (Bearer ── el pedido es de ESTA cuenta, AUTH-04 ya lo garantiza)
        │
   ┌── API FASTAPI (capas) ─────────────────────────────────────────────┐
   │ routers/checkout → services/pedidos:                                │
   │  1. Lee items [{producto_id, cantidad}] — SIN precios (D-27/RN-08)  │
   │  2. Hidrata contra catálogo: recalcula total con precio VIGENTE     │
   │     y valida stock >= cantidad  (CART-03: jamás confía en el cliente)│
   │     └ stock insuficiente → 400 "regla de negocio"                   │
   │  3. Crea orden PENDING + líneas con snapshot nombre/precio (D-36)   │
   │     + numero = "MAURA-000001" (buy_order, ≤26 chars, D-37)          │
   │  4. tx = Transaction.build_for_integration(...)...create(           │
   │       buy_order=numero, session_id, amount=total, return_url)       │
   │     └── POST https://webpay3gint.transbank.cl/... (sync requests)   │
   └───────┬─────────────────────────────────────────────────────────────┘
        ◄── 201 {url, token_ws, numero}
   [SPA] construye <form method="POST" action={url}>
         <input hidden name="token_ws" value={token}> + submit()
         └─ FULL-PAGE LOAD fuera de la SPA (el navegador viaja a Webpay)


     FLUJO 2 — VUELTA: EL NAVEGADOR EXTERNO VUELVE AL BACKEND (PAY-02, D-41)
     ═════════════════════════════════════════════════════════════════════

   [Webpay redirige el NAVEGADOR al return_url — GET o POST según flujo]

   GET|POST /api/pago/retorno   (PÚBLICO — el navegador no trae Bearer)
        │  params posibles: token_ws · TBK_TOKEN · TBK_ID_SESION · TBK_ORDEN_COMPRA
        ▼
   DISCRIMINADOR (orden del plugin oficial de Transbank):
        ├─ token_ws + TBK_TOKEN          → ERROR FORMULARIO (no commitear)
        ├─ TBK_ID_SESION + TBK_TOKEN     → ANULADO por la clienta
        ├─ TBK_ID_SESION solo            → TIMEOUT (sin token; buscar por TBK_ORDEN_COMPRA)
        └─ token_ws solo                 → FLUJO NORMAL → commit(token_ws)
                                             │
                                             ├─ response_code==0 && status==AUTHORIZED
                                             │    → UNA transacción SQLAlchemy:
                                             │       por línea: UPDATE productos
                                             │         SET stock = stock - n
                                             │         WHERE id=? AND stock >= n
                                             │       (rowcount 0 en alguna → REJECTED)
                                             │       orden PENDING → PAID
                                             │    → 302 a /pago/resultado?estado=pagado&orden=…
                                             ├─ commit OK pero response_code != 0 → REJECTED
                                             └─ orden ya PAID (refresh) → re-mostrar SIN
                                                side effects (idempotencia, PAY-03)

   302 (RedirectResponse status_code=302 — NO el 307 default) → SPA /pago/resultado
        │
   [SPA] lee params → fetcha GET /api/pedidos/{numero} (Bearer del localStorage,
         que sobrevivió el full-page load — D-21/CART-02) → voucher de la TIENDA
         (D-43) → si PAID: vaciar carro (D-44) + invalidateQueries de stock


     FLUJO 3 — HISTORIAL (ORDR-01, D-46..D-49)
     ══════════════════════════════════════════
   [Navbar "Mis pedidos"] → /pedidos (RequireAuth + returnTo, D-32/D-47)
        → GET /api/pedidos (Bearer): TODAS las órdenes de la clienta, estado real
          (PENDING="en curso", D-48) → clic → detalle = MISMO componente voucher (D-43)

   PARALELO API-FIRST (D-15): contrato 0.2.0 → 0.3.0 + ADRs 012+ ANTES de las guías;
   cierre: /docs ≈ contrato + los 4 flujos runtime en el UAT delegado (maura-uat)
```

### Recommended Project Structure

Archivos que la fase crea/extiende en ESTE repo (todo documento):

```
demo-carro/
├── .planning/phases/03-…/03-SPIKE-RETORNO.md   # NUEVO (hallazgos, D-40 — insumo del planner;
│                                               #   la guía narra "lo que el spike reveló")
├── docs/
│   ├── README.md                        # EXTENDER: fila 6 del ciclo avanza (guías 9+)
│   ├── 02_requerimientos.md             # EXTENDER: etapa 3 — RF-12+, RNF-07+, RN-10+, HU-09+, §13 P6
│   ├── 03_diseno.md                     # EXTENDER: entidades PEDIDO/LÍNEA (relaciones nuevas
│   │                                    #   Usuario→Pedidos→Productos), procesos 9.0+, pantallas 8+
│   ├── 04_arquitectura/
│   │   ├── contrato_api.yaml            # EXTENDER ANTES DE GUÍAS (D-15): 0.2.0→0.3.0, tag Pago/Pedidos,
│   │   │                                #   POST /api/checkout, GET+POST /api/pago/retorno (302!),
│   │   │                                #   GET /api/pedidos, GET /api/pedidos/{numero}
│   │   ├── README.md                    # EXTENDER: índice ADRs 012+, árbol del proyecto del alumno
│   │   └── adr/
│   │       ├── 012-*.md                 # NUEVO: retorno de Webpay — mecánica elegida por el spike (D-41)
│   │       ├── 013-*.md                 # NUEVO (candidato): orden nace al iniciar el pago + stock al aprobar (D-34/D-35)
│   │       └── 014-*.md                 # NUEVO (candidato): snapshot de precio en la orden (D-36)
│   └── 05_desarrollo/
│       ├── README.md                    # EXTENDER: filas guías 9+ con estado
│       ├── guia-09-*.md                 # NUEVO: backend de órdenes + Webpay (modelo Pedido, checkout, retorno)
│       ├── guia-10-*.md                 # NUEVO: vuelta a la SPA — form auto-submit, /pago/resultado, voucher
│       └── guia-11-*.md                 # NUEVO: historial /pedidos + Gran verificación final de la fase 3
└── README.md                            # EXTENDER: tabla fase 6 (guías 1-11), stack menciona Webpay
```

*(El particionado exacto de guías 09+ y qué ADRs son 3 o 2 es discretion del planner, D-16 partición por hito.)*

Estructura del proyecto del alumno que las guías construyen (fuera del repo, D-17):

```
backend/app/
├── models/pedido.py    # NUEVO: EstadoPedido enum (pending/paid/cancelled/rejected — nombre==valor),
│                       #   Pedido (numero unique, estado, total, usuario_id FK, buy_order=numero),
│                       #   LineaPedido (producto_id FK, nombre_snapshot, precio_snapshot, cantidad)
├── schemas/pedido.py   # NUEVO: CheckoutCreate (items ids+cantidades), CheckoutRespuesta (url, token, numero),
│                       #   OrdenLista, OrdenDetalle, OrdenLinea — espejo del contrato 0.3.0
├── repositories/pedido.py  # NUEVO: crear, por_numero, por_usuario, descontar_stock_atomico (UPDATE condicional)
├── services/pedidos.py     # NUEVO: iniciar_checkout (recalculo+validación CART-03, 400 stock),
│                           #   procesar_retorno (discriminador + commit + transición), listar/detalle (ownership 404)
├── services/webpay.py      # NUEVO (o parte de pedidos): Transaction.build_for_integration(...) wrapper
│                           #   — ÚNICO lugar que importa transbank
├── routers/checkout.py     # NUEVO: POST /api/checkout (Bearer, sync def)
├── routers/retorno.py      # NUEVO: GET+POST /api/pago/retorno (público, RedirectResponse 302)
├── routers/pedidos.py      # NUEVO: GET /api/pedidos, GET /api/pedidos/{numero} (Bearer)
└── main.py                 # EXTENDER: include_router nuevos; create_all agrega tablas (ADR-005)
frontend/src/
├── lib/api.ts           # EXTENDER: apiPost (checkout) — el retorno NO pasa por acá (es navegación)
├── types/api.ts         # EXTENDER: CheckoutRespuesta, OrdenLista, OrdenDetalle, OrdenLinea
├── features/checkout/Checkout.tsx  # EXTENDER: encender el CTA (D-31→PAY-01): mutación + form auto-submit
├── features/pago/ResultadoPago.tsx # NUEVO: ruta única /pago/resultado (D-42) — lee params, fetcha orden,
│                                    #   voucher (D-43) + vaciar carro si PAID (D-44) — componente VoucherPedido
├── features/pedidos/   # NUEVO: Pedidos.tsx (lista, D-46) reutilizando VoucherPedido como detalle
├── components/Navbar.tsx  # EXTENDER: link "Mis pedidos" con sesión (D-47)
└── main.tsx            # EXTENDER: rutas /pago/resultado (pública: el 302 llega sin sesión en URL)
                        #   y /pedidos (protegida RequireAuth, D-47)
```

### Pattern 1: Webpay Plus con el SDK Python — instancia de integración (PAY-01)

**Qué:** la vía oficial. El SDK trae las credenciales públicas de integración como constantes — sin registro, sin `.env` para Webpay en esta fase (la aclaración que CONTEXT pidió dejar explícita al alumno).

```python
# Source: transbank-sdk-python master, firmas verificadas en fuente esta sesión
#   transbank/webpay/webpay_plus/transaction.py + common/webpay_transaction.py + constantes
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys

# Credenciales PÚBLICAS de integración (no requieren registro en Transbank):
#   IntegrationCommerceCodes.WEBPAY_PLUS = "597055555532"
#   IntegrationApiKeys.WEBPAY = "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C"
tx = Transaction.build_for_integration(
    IntegrationCommerceCodes.WEBPAY_PLUS, IntegrationApiKeys.WEBPAY
)

resp = tx.create(
    buy_order=orden.numero,      # "MAURA-000001" — max 26 chars (ApiConstants.BUY_ORDER_LENGTH = 26)
    session_id=str(orden.usuario_id),  # max 61 chars (SESSION_ID_LENGTH = 61)
    amount=float(orden.total),   # CLP entero como float — el precio es entero (RN-02)
    return_url=f"{base}/api/pago/retorno",  # max 255 chars (RETURN_URL_LENGTH = 255)
)
# resp["token_ws"], resp["url"]  → la SPA arma el form POST con el token (PAY-01)

commit_resp = tx.commit(token_ws)   # PUT .../transactions/{token}
# commit_resp["response_code"], commit_resp["status"], commit_resp["buy_order"],
# commit_resp["amount"], commit_resp["authorization_code"], commit_resp["transaction_date"],
# commit_resp["card_detail"], commit_resp["vci"], ...

status_resp = tx.status(token)      # consulta sin confirmar — 7 días de ventana (fase 4 lo usa)
```

**Notas verificadas en fuente/registro:**
- `Transaction` es **instancia-basada** en 6.x: `build_for_integration(commerce_code, api_key)` es el classmethod de fábrica [VERIFIED: transbank/common/webpay_transaction.py — `@classmethod def build_for_integration(cls, commerce_code, api_key)`]. No existe el estilo clase-estática de SDKs viejos.
- Validaciones client-side ANTES de llamar a la API: `ValidationUtil.has_text_with_max_length(...)` → `TransbankError` → envuelto en `TransactionCreateError` [VERIFIED: transaction.py]. `buy_order` vacío también revienta (`can't be null or white space`) — el numero legible jamás es vacío.
- Errores tipados: `TransactionCreateError`, `TransactionCommitError`, `TransactionStatusError` [VERIFIED: transaction.py imports] — la guía atrapa `TransactionCommitError` en el retorno para no tirar la 302.
- El SDK usa `requests` (sync) [VERIFIED: STACK.md + request_service] → **rutas `def` sincronizadas** (FastAPI las corre en threadpool — ya decidido por STACK "keep Webpay calls in sync routes").
- Endpoint API: `/rswebpaytransaction/api/webpay/v1.2` [VERIFIED: api_constants.py] — **v1.2 ≥ 1.1: el retorno del flujo normal es por GET** (ver Pattern 3).
- `amount: float` — para CLP entero, `float(total)` sin decimales; docs oficiales del plugin/contrato aceptan entero como float.

### Pattern 2: El form POST auto-submit en la SPA (PAY-01, D-31 encendido)

**Qué:** la salida de la SPA hacia Webpay es una navegación de página completa construida en JS — la primera vez que la SPA "se va" del navegador.

```tsx
// Source: patrón textual de las docs oficiales ("Con estos datos debes crear un formulario
// en el cual debes poner un input de nombre token_ws y su valor el token devuelto.
// El formulario debe usar el método POST y su acción la URL devuelta por Webpay Plus")
// — adaptado a React con el CTA de guia-08 que estaba deshabilitado (D-31)
const pagar = useMutation({
  mutationFn: () =>
    apiPost<CheckoutRespuesta>("api/checkout", { items }), // items = [{producto_id, cantidad}] (D-27)
  onSuccess: (resp) => {
    const form = document.createElement("form");
    form.method = "POST";
    form.action = resp.url;                 // la URL que devolvió tx.create()
    const token = document.createElement("input");
    token.type = "hidden";
    token.name = "token_ws";                // nombre EXACTO que exige Webpay
    token.value = resp.token_ws;
    form.appendChild(token);
    document.body.appendChild(form);
    form.submit();                          // full-page load: la SPA se despide
  },
});
// CTA: <button disabled={pagar.isPending} onClick={() => pagar.mutate()}>Pagar con Webpay</button>
```

- El submit vive en el **handler del clic**, jamás en un `useEffect` (StrictMode monta dos veces en dev → doble submit → dos órdenes PENDING). Pitfall 6.
- `document.createElement` es DOM estándar — la lección: React renderiza la UI, pero una navegación con form construido a mano es exactamente lo que Webpay exige (no se puede `fetch`).
- El carro NO se limpia acá (D-44): solo al llegar al voucher con PAID.

### Pattern 3: El discriminador de los 4 flujos — orden verbatim del plugin oficial (PAY-02)

**Qué:** el endpoint de retorno lee `token_ws` / `TBK_TOKEN` / `TBK_ID_SESION` / `TBK_ORDEN_COMPRA` de query (GET) o body form-encoded (POST) y discrimina. La tabla oficial de flujos + el orden de ramas del plugin oficial de Transbank:

| Flujo | Parámetros que llegan | Método (docs oficiales) | Acción del backend |
|-------|----------------------|--------------------------|--------------------|
| **Normal (aprobado o rechazado por la tarjeta)** | `token_ws` | **GET** (API ≥1.1; POST en versiones viejas) | `commit(token_ws)` → criterio PAY-03 |
| **Anulado por la clienta** | `TBK_TOKEN` + `TBK_ORDEN_COMPRA` + `TBK_ID_SESION` (SIN token_ws) | **GET en producción, POST en integración** | NO commitear; opcional `status(TBK_TOKEN)`; orden → CANCELLED |
| **Timeout del formulario** | `TBK_ID_SESION` + `TBK_ORDEN_COMPRA` (SIN token) | no declarado explícito en docs (ver nota) | buscar orden por `TBK_ORDEN_COMPRA`; → CANCELLED |
| **Error de formulario** | `token_ws` + `TBK_TOKEN` + `TBK_ID_SESION` + `TBK_ORDEN_COMPRA` (los 4 juntos) | no declarado explícito | NO commitear; orden → CANCELLED |

```python
# Source: transbank-plugin-woocommerce-webpay-rest CommitWebpayController (repo oficial
# TransbankDevelopers) — orden de ramas verbatim traducido a Python
def clasificar_flujo(token_ws, tbk_token, tbk_id_sesion):
    if token_ws and tbk_token:
        return "error_formulario"      # WEBPAY_ERROR_FLOW (token doble)
    if tbk_id_sesion and tbk_token and not token_ws:
        return "anulado"               # WEBPAY_ABORTED_FLOW
    if tbk_id_sesion and not tbk_token and not token_ws:
        return "timeout"               # WEBPAY_TIMEOUT_FLOW
    if token_ws and not tbk_token and not tbk_id_sesion:
        return "normal"                # WEBPAY_NORMAL_FLOW → commit
    return "desconocido"               # defensivo: 302 con estado=error
```

**Notas críticas (todas alimentan el spike, D-41):**
- **El flujo anulado NO trae `token_ws`**: trae el token bajo `TBK_TOKEN`. La descripción de D-39 ("anulado: `token_ws` por GET tras anular") era hipótesis razonable pero las docs oficiales dicen otra cosa: "se envía por método GET el token de la transacción en la variable `TBK_TOKEN` además de las variables `TBK_ORDEN_COMPRA` y `TBK_ID_SESION` **(para el entorno de integración, este redireccionamiento es realizado con el método POST)**" [CITED: transbankdevelopers.cl/documentacion/webpay-plus]. El spike lo confirma con evidencia runtime.
- El resumen oficial: "A la URL de `return_url` **siempre se llega por POST**, aunque desde la versión 1.1 del API, en adelante, la redirección es por GET (**solo en el caso de pago abortado en el ambiente de integración, el retorno se mantiene por POST**)" [CITED: ídem] — y para el normal: "En la versión 1.1 y superiores de la API, esta redirección es por GET. Para versiones anteriores se envía por método POST". El método del timeout queda ambiguo en las docs → **el endpoint se declara GET+POST y lee query Y body**: inmune a la ambigüedad.
- Para el anulado, las docs recomiendan: "El comercio con la variable TBK_TOKEN consulta la transacción para validar el estado (**no es necesario confirmar la transacción**)" [CITED: ídem] — `status(TBK_TOKEN)` existe; commitear un token anulado no es la vía. El plugin oficial directamente NO llama a la API en los flujos no-normales: solo marca local y redirige [VERIFIED: CommitWebpayController — "The other flows (timeout, aborted, error) do not call a status/refund SDK method here — they only mark the transaction locally"].
- **El timeout tiene reloj distinto por ambiente**: "El formulario de pago tiene un tiempo máximo de espera de **4 minutos en producción y de 10 minutos en integración**" [CITED: ídem] — el spike y el UAT deben presupuestar ~10 min de espera para este flujo.
- **El flujo de error de formulario es "replicable solo en producción"** según las docs [CITED: ídem — "(replicable solo en producción si inicias una transacción, abres el formulario de pago, cierras el tab de Chrome y luego lo recuperas)"]. D-39 esperaba los 4 corroborados runtime: el spike corroborará 3 y documentará el 4° desde las docs + la rama `token_ws`+`TBK_TOKEN` del plugin oficial (que sí lo maneja en producción). Ver Open Questions Q1.
- Token de create tiene vida corta: "el token que es entregado tiene un periodo reducido de vida de **5 minutos**" [CITED: ídem] — irrelevante para el flujo normal (el form se submitea al instante), pero explica huérfanas PENDING de clientas que abandonan.

**Lectura del request en FastAPI (GET y POST a la vez):**

```python
# El retorno es navegación del navegador: GET trae query params, POST trae form-encoded
# (python-multipart ya está instalado — la misma pieza del form de login, fase 2)
from fastapi import Request, Form
from fastapi.responses import RedirectResponse

@router.get("/api/pago/retorno")
def retorno_get(request: Request):
    q = request.query_params
    return _procesar(q.get("token_ws"), q.get("TBK_TOKEN"),
                     q.get("TBK_ID_SESION"), q.get("TBK_ORDEN_COMPRA"))

@router.post("/api/pago/retorno")
def retorno_post(
    token_ws: str | None = Form(default=None),
    TBK_TOKEN: str | None = Form(default=None),        # nombre literal de Transbank
    TBK_ID_SESION: str | None = Form(default=None),
    TBK_ORDEN_COMPRA: str | None = Form(default=None),
):
    return _procesar(token_ws, TBK_TOKEN, TBK_ID_SESION, TBK_ORDEN_COMPRA)
```

### Pattern 4: El 302 del backend a la SPA — PRG y el default 307 (D-41, D-42)

**Qué:** procesado el flujo, el backend responde una redirección al navegador hacia la ruta única de la SPA (`/pago/resultado`) con el resultado como query params — la mecánica candidata a más simple (la que usa el plugin oficial con `wp_redirect`).

```python
# Source: patrón del plugin oficial (redirect final a la URL del comercio) + starlette
# RedirectResponse default status_code=307 [VERIFIED: starlette/responses.py:207-212
#   `def __init__(self, url, status_code: int = 307, ...)`]
from urllib.parse import urlencode

def _hacia_spa(estado: str, numero: str | None = None) -> RedirectResponse:
    params = {"estado": estado}
    if numero:
        params["orden"] = numero
    url = f"{frontend_url}/pago/resultado?{urlencode(params)}"
    return RedirectResponse(url, status_code=302)   # 302 EXPLÍCITO — el default 307 re-POSTearía
```

- **El 307 por defecto es la trampa:** 307 preserva método+body → si el retorno llegó por POST, la "redirección" re-POSTea el form de Webpay contra la SPA (que no tiene handler POST) → pantalla rota. 302 (o 303) fuerza el GET del navegador a la ruta de resultado. Es la lección PRG (Post/Redirect/Get) del patrón clásico, dicha por primera vez en el proyecto. Pitfall 1.
- La SPA en `/pago/resultado` es **ruta pública del router** (el 302 no lleva sesión en la URL): lee `estado`/`orden`, y fetcha `GET /api/pedidos/{numero}` con el Bearer del localStorage (que sobrevivió el full-page load — D-21/CART-02 fue diseñado exactamente para este momento). Si no hay sesión (clienta en otro dispositivo), el voucher degrada a "inicia sesión para ver tu pedido" con el estado visible igualmente (copy a discreción).
- `frontend_url` en Settings (ya existe `cors_origins` con el mismo valor — reutilizar la pieza: la fase 5 lo congela al desplegar, STATE.md ya lo advierte).

### Pattern 5: Stock atómico — UPDATE condicional + rowcount en la transacción del commit (ORDR-02, D-35)

**Qué:** el descuento ocurre SOLO al aprobar (D-35), en la MISMA transacción SQLAlchemy que transiciona la orden, con un UPDATE que lleva la condición adentro del SQL — el motor (SQLite serializa escrituras) es la muralla contra el oversell.

```python
# Source: patrón SQLAlchemy 2.0 documentado (update + where + values por Session.execute)
#   [CITED: docs.sqlalchemy.org/en/20/tutorial/data_update.html + /orm/queryguide/dml.html]
from sqlalchemy import update

def descontar_stock(sesion: Session, lineas: list[LineaPedido]) -> bool:
    """True si TODAS las líneas descontaron; False si alguna perdió el stock (→ REJECTED)."""
    for linea in lineas:
        resultado = sesion.execute(
            update(Producto)
            .where(Producto.id == linea.producto_id, Producto.stock >= linea.cantidad)
            .values(stock=Producto.stock - linea.cantidad)
            .execution_options(synchronize_session=False)
        )
        if resultado.rowcount == 0:      # 0 filas = el WHERE no encontró stock suficiente
            raise StockInsuficiente(linea.producto_id)  # revierte TODA la transacción
    return True
```

- `rowcount`: "The value returned is the number of rows matched by the WHERE clause" [CITED: docs.sqlalchemy.org tutorial/data_update — CursorResult.rowcount]. Con SQLite el rowcount de UPDATE es confiable (sin RETURNING en juego).
- `synchronize_session=False`: el WHERE es una expresión SQL (`stock >= n`) que Python no puede evaluar contra el identity map — las docs recomiendan 'fetch' o False para criterios no evaluables [CITED: /orm/queryguide/dml.html]. Con `False`, los objetos Producto en sesión quedan stale — la guía lo narra y hace `sesion.expire_all()` o simplemente no relee los productos en el mismo request.
- **Todo en UNA transacción**: la dependencia `get_session` (fase 1) ya la abre por request; el service hace descuento + `orden.estado = PAID` y el commit sale al final — o queda todo (REJECTED incluida la transición) o nada.
- La **condición va en el SQL, no en Python**: leer `producto.stock`, comparar y escribir en dos pasos NO es atómico (dos threads leen el mismo stock y ambos "alcanzan"). La asimetría es la lección de ORDR-02 — la misma que RN-09 enseñó en pantalla pero ahora con consecuencias reales de plata.
- **Cómo demostrar el oversell evitado** (para la guía/UAT): un stock=1 y dos commits concurrentes — solo uno descuenta. Con el dev server de uvicorn (single process, threads) alcanza; un mini-script con `httpx` y dos threads contra dos tokens distintos es la mini-verificación natural. La guía NO necesita infraestructura de carga.
- Nota SQLite: el lock de escritura es a nivel de archivo — los writers se serializan solos; el UPDATE condicional es correcto con o sin WAL. No hay `SELECT ... FOR UPDATE` en SQLite (no hace falta: el UPDATE lleva su guarda).

### Pattern 6: Modelo de datos — snapshot en las líneas, numero legible, estados honestos (D-34..D-37, ORDR-01)

```python
# Source: decisiones D-34..D-37 + patrón Producto/Usuario de guia-03/05 (enum nombre==valor,
# tercera vuelta del gotcha) + soft delete ya diseñado en docs/03 §2.3.5
import enum

class EstadoPedido(str, enum.Enum):
    pending = "pending"      # nació en el checkout, saltó a Webpay, aún no vuelve (D-48: "en curso")
    paid = "paid"            # commit aprobado: response_code==0 && status==AUTHORIZED
    cancelled = "cancelled"  # anulado por la clienta / timeout / error de formulario
    rejected = "rejected"    # tarjeta rechazada (response_code != 0) o stock perdido en el commit (D-35)

class Pedido(Base):
    __tablename__ = "pedidos"
    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(26), unique=True, index=True)  # "MAURA-000001" = buy_order (D-37)
    estado: Mapped[EstadoPedido] = mapped_column(Enum(EstadoPedido), default=EstadoPedido.pending)
    total: Mapped[int] = mapped_column(Integer)          # CLP entero recalculado por el backend (CART-03)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    # Opcionales del commit (discretion): authorization_code, transaction_date (texto ISO de Transbank)

class LineaPedido(Base):
    __tablename__ = "pedidos_lineas"
    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"))
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))  # soft delete lo mantiene vivo (D-36)
    nombre_snapshot: Mapped[str] = mapped_column(String(120))   # congelado al comprar (D-36)
    precio_snapshot: Mapped[int] = mapped_column(Integer)       # lo que se PAGÓ, jamás el precio vigente
    cantidad: Mapped[int] = mapped_column(Integer)
```

- **El numero nace del id**: insertar la orden (id autoincrement) → `numero = f"MAURA-{pedido.id:06d}"` en la misma transacción → único por construcción (11 chars << límite 26 [VERIFIED: ApiConstants.BUY_ORDER_LENGTH = 26]). Nada de `max(id)+1` en Python (condiciones de carrera consigo mismo).
- La FK a productos + el snapshot resuelven el soft delete: "un pedido viejo no puede quedar apuntando a un producto borrado" [VERIFIED: docs/03_diseno.md:111-114 — decisión 5 de §2.3]. El detalle del pedido renderiza `nombre_snapshot`/`precio_snapshot`, no el catálogo.
- `create_all` de ADR-005 agrega las tablas nuevas sin tocar las existentes — sin migraciones en esta fase (guía lo narra como decisión heredada).

### Pattern 7: Extensión del contrato 0.2.0 → 0.3.0 (D-15, ANTES de las guías)

```yaml
# Source: estructura vigente del contrato [VERIFIED: docs/04_arquitectura/contrato_api.yaml
#   esta sesión] + swagger.io para form-encoded requestBody (fase 2 ya lo usó en /login)
info:
  version: 0.3.0        # 0.2.0 → 0.3.0 (ADR-007: fuente de verdad versionada)
tags:
  - name: Pago          # nuevo (o "Pedidos" — discretion CONTEXT)
    description: Checkout y retorno de Webpay Plus en ambiente de integración (PAY-01..04, CART-03)

paths:
  /api/checkout:
    post:
      security: [{ bearerAuth: [] }]     # el pedido es de ESTA cuenta
      requestBody: { application/json: { schema: CheckoutCreate } }   # items ids+cantidades (D-27)
      responses:
        '201': { description: Orden PENDING creada + form POST, schema: CheckoutRespuesta }
        '400': { description: Stock insuficiente — regla de negocio (CART-03) }   # la fila reservada pasa a "En uso (fase 3)"
        '401': { ... }                   # sin sesión
  /api/pago/retorno:
    get:   # query params opcionales token_ws / TBK_TOKEN / TBK_ID_SESION / TBK_ORDEN_COMPRA
    post:  # requestBody application/x-www-form-urlencoded con los mismos 4 campos (python-multipart)
      security: []                       # PÚBLICO: navegación del navegador, sin Bearer
      responses:
        '302': { description: Redirección del navegador a la SPA con el resultado (headers.Location) }
        '400': { description: Flujo irreconocible o token no comiteable }   # defensivo
  /api/pedidos:
    get:
      security: [{ bearerAuth: [] }]
      responses: { '200': { array de OrdenLista }, '401': ... }
  /api/pedidos/{numero}:
    get:
      security: [{ bearerAuth: [] }]
      responses: { '200': OrdenDetalle, '401': ..., '404': ... }   # 404 = no existe O no es tuya (ownership)
```

- **El 302 es el primer response no-JSON del contrato** — la lección documental de la fase: este endpoint le habla al NAVEGADOR, no a la SPA. Declararlo con `Location` header explícito en el contrato.
- La fila 400 de la tabla de convención de errores pasa de "Reservado (fases 2+)" a "En uso (fase 3)" [VERIFIED: contrato_api.yaml:30 — verbatim `| 400 | Regla de negocio violada | Reservado (fases 2+) |`].
- `security: []` en el retorno es deliberado y pedagógico: contrasta con los Bearer de alrededor (¿por qué este no exige sesión? porque quien llama es el navegador recién salido de Webpay — la sesión está en el localStorage que la SPA retomará después).
- Schemas nuevos (discretion de nombres): `CheckoutCreate {items: [{producto_id, cantidad}]}` — **sin campo precio**: CART-03 escrito en el contrato; `CheckoutRespuesta {url, token_ws, numero}`; `OrdenLista {numero, fecha, total, estado}`; `OrdenDetalle` (+ líneas con snapshot); enum `estado: [pending, paid, cancelled, rejected]`.

### Pattern 8: Convenciones documentales que la fase replica (verificadas en repo)

| Convención | Valor vigente (verbatim) | Fuente |
|---|---|---|
| Series a continuar | `RF-11`, `RNF-06`, `RN-09`, `HU-08` son los últimos de cada serie | [VERIFIED: docs/02_requerimientos.md:100 (RF-11), :113 (RNF-06), :127 (RN-09), :199 (HU-08)] |
| Fila P6 a llenar | "`\| P6 Pago online con Webpay \| *(sin requerimiento en esta etapa — etapa 3: CART-03 y PAY-01..04)* \| Etapa 3 \|`" | [VERIFIED: docs/02_requerimientos.md:282] |
| Entidades esperando pedidos | "los pedidos de la etapa 3 se conectarán a esta entidad" (PRODUCTO) / "los pedidos de la etapa 3 conectarán usuarios con productos" (USUARIO) | [VERIFIED: docs/03_diseno.md:214-215 §8] |
| Soft delete para el snapshot | "**`activo` permite ocultar sin borrar.** ... cuando lleguen pedidos (etapa 3), un pedido viejo no puede quedar apuntando a un producto borrado" | [VERIFIED: docs/03_diseno.md:111-114 §2.3.5] |
| El CTA que esta fase enciende | "`Pagar con Webpay`" deshabilitado + "El pago llega en la etapa siguiente." | [VERIFIED: guia-08-checkout.md:221-229] |
| Siguiente de guia-08 ya anunciado | "fase 3 — el pago con Webpay y las órdenes... la orden que descuenta stock en el backend (la segunda barrera de CART-03) y el retorno de la pasarela a tu SPA" | [VERIFIED: guia-08-checkout.md:496-501] |
| Índice de guías | 8 filas ✅ + "Las guías 9+ llegan con las fases siguientes (pago Webpay, panel admin, IA)" | [VERIFIED: docs/05_desarrollo/README.md:24-39] |
| ADRs existentes | 001-011; la fase continúa desde ADR-012 (formato demo-cine) | [VERIFIED: ls docs/04_arquitectura/adr/ esta sesión] |
| Gran verificación final | tabla numerada con columna Origen + fila contrato ↔ `/docs` con Authorize (fase 2 la extendió) — la fase 3 suma los 4 flujos runtime | [VERIFIED: guia-08-checkout.md:372-401] |
| Estados de pantalla | "cada pantalla declara sus estados de carga, error y vacío. Ninguna pantalla se diseña solo para el caso feliz" | [VERIFIED: docs/03_diseno.md:353-355 §4.1] |

### Anti-Patterns to Avoid

- **Commitear un flujo anulado/timeout/error** — el commit es SOLO del flujo normal (`token_ws` solo). Las docs lo dicen para el anulado ("no es necesario confirmar") y el plugin oficial no llama a la API en los otros flujos.
- **Leer stock en Python y escribir después** — read-check-write NO es atómico; la condición (`stock >= n`) va DENTRO del UPDATE. La lección de ORDR-02.
- **`RedirectResponse(url)` sin status_code** — el default 307 re-POSTea el form de Webpay contra la SPA. 302 explícito. Pitfall 1.
- **Poner `bearerAuth` al endpoint de retorno** — quien llega es el navegador externo sin Bearer; el endpoint es público por diseño y la sesión se retoma DESPUÉS en la SPA.
- **Confiar en el monto/cantidad que envía el cliente** — CART-03: la entrada del checkout es ids+cantidades; el total lo calcula el servidor con precio vigente.
- **Limpiar el carro antes del voucher** — D-44: solo con PAID visible; en anulado/timeout queda intacto (esa ES la implementación de PAY-04).
- **`dangerouslySetInnerHTML` para el form de Webpay** — construir el form con `document.createElement` (Pitfall de seguridad heredado: React escapa por defecto, D-21 lo documentó en ADR-009).
- **Usar el id interno de BD como buy_order** — D-37: numero legible público; además topa el límite de 26 chars si se le pegan cosas.
- **Expirar/anular PENDING en fase 3** — D-49 lo prohíbe: sin jobs de fondo ni ventanas de tiempo; la huérfana queda visible ("en curso") y fase 4 la gestiona.
- **`status == "AUTHORIZED"` sin comparar `response_code`** — PAY-03 exige AMBOS (la cita oficial es literal en los dos); un commit puede traer status con response_code != 0 → REJECTED.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Llamar a Webpay | httpx manual contra `/rswebpaytransaction/api/webpay/v1.2` con firma de headers | `transbank-sdk` `Transaction.build_for_integration(...)` | El SDK trae credenciales públicas, validaciones client-side (26/61/255), errores tipados y el endpoint versionado — todo verificado en fuente esta sesión |
| Discriminación de flujos | adivinar por método HTTP ("si es POST es timeout") | tabla de PRESENCIA de params (token_ws/TBK_TOKEN/TBK_ID_SESION) — Pattern 3 | El método varía por ambiente/versión de API; la presencia de params es la firma estable de cada flujo (plugin oficial) |
| Redirección del retorno | responder JSON con la URL y que la SPA "navegue" | `RedirectResponse(url, status_code=302)` | Quien recibe la respuesta es el NAVEGADOR tras un POST/GET de Webpay — solo una redirección HTTP sirve; JSON no navega |
| Descuento atómico | SELECT + IF en Python + UPDATE | UPDATE condicional `WHERE stock >= n` + `rowcount` | La condición dentro del SQL es la única muralla real contra el oversell; rowcount es el veredicto |
| Formato del total CLP | concatenar "$" + puntos | `Intl.NumberFormat("es-CL", {style:"currency", currency:"CLP"})` | Ya verificado en fases 1-2: produce `$26.970` — el voucher y el historial lo heredan |
| Parseo del form de retorno | leer el body crudo a mano | `Form(default=None)` params (python-multipart, ya instalado) | Misma pieza del login de fase 2; FastAPI + python-multipart parsea application/x-www-form-urlencoded |
| Voucher | iframes/links a Webpay | vista propia de la orden (D-43) | "ya no se debe mostrar el voucher de Transbank, solo debe mostrarse desde el sitio del comercio" [CITED: docs oficiales] |

**Key insight:** igual que fases 1-2, cada "no lo hagas a mano" ES contenido del curso — la redirección de pago (form POST construido en JS), el retorno que discrimina 4 flujos y el stock transaccional son LOS tres conceptos nuevos de la etapa.

## Runtime State Inventory

*(Step 2.5: OMITIDO como inventario formal — la fase NO renombra/refactoriza strings existentes. Dos notas de estado runtime que el planner sí debe saber: (1) el workspace `D:/Repos/maura-uat` ya tiene la app construida hasta guia-08 (backend con seed de 12 SKU + cuentas, frontend con carro/checkout) — el spike corre SOBRE ese backend o en un mini-backend aparte dentro del mismo workspace (discretion CONTEXT: "alcance mínimo que corrobore los 4 flujos"); (2) el modelo nuevo agrega TABLAS (pedidos, pedidos_lineas) vía create_all — las tablas existentes (productos, usuarios) NO se tocan, sin migración.)*

## Common Pitfalls

### Pitfall 1: RedirectResponse con 307 por defecto (el retorno re-POSTea)
**What goes wrong:** `RedirectResponse(url)` sin `status_code` usa **307** [VERIFIED: starlette/responses.py:207-212 — `status_code: int = 307`]: preserva método+body → cuando el retorno de Webpay llegó por POST (anulado en integración, y los flujos que el spike confirme), el navegador re-POSTea el form contra la ruta de la SPA → React Router no tiene handler POST → 405/pantalla rota.
**Why:** 307 es "redirige sin perder nada" (útil para POST→POST de APIs); PRG necesita 302/303 que fuerzan GET.
**How to avoid:** `RedirectResponse(url, status_code=302)` explícito en TODO el endpoint de retorno. La guía lo narra como la primera lección PRG del proyecto.
**Warning signs:** la pantalla de resultado funciona en el flujo aprobado (GET) pero revienta en el anulado (POST en integración).

### Pitfall 2: La ambigüedad GET vs POST del retorno
**What goes wrong:** diseñar el endpoint solo GET (porque "v1.1 es GET") y que el anulado en integración llegue por POST → 405 Method Not Allowed del propio FastAPI; o diseñarlo solo POST (por el blocker de STATE.md) y que el aprobado llegue por GET.
**Why:** las docs describen GET para normal (API ≥1.1), GET-producción/POST-integración para abortado, y NO declaran el método para timeout ni error-de-formulario [CITED: transbankdevelopers.cl].
**How to avoid:** endpoint GET+POST que lee query Y body (Pattern 3); discriminar por PRESENCIA de params, jamás por método. El spike registra la evidencia real por flujo (D-41).
**Warning signs:** cualquier código que ramifique por `request.method` en vez de por qué params llegaron.

### Pitfall 3: Commitear flujos no-normales
**What goes wrong:** llamar `commit(TBK_TOKEN)` en el anulado → la API rechaza (transacción sin autorización) → `TransactionCommitError` → la 302 nunca sale y el navegador ve un 500.
**Why:** el commit confirma una AUTORIZACIÓN; en los flujos abortados/timeout no hay nada que confirmar — las docs lo dicen explícito ("no es necesario confirmar la transacción").
**How to avoid:** commit SOLO en la rama `token_ws`-solo; los otros flujos marcan la orden CANCELLED localmente y redirigen. Envolver el commit en try/except `TransactionCommitError` → 302 con estado de error (nunca 500 al navegador).
**Warning signs:** un 500 crudo desde webpay al volver de anular.

### Pitfall 4: El doble-commit por refresh (PAY-03)
**What goes wrong:** la clienta refresca `/pago/resultado`... o mejor: el navegador re-envía el POST del retorno (retry/back) → el backend re-procesa → segundo descuento de stock / segunda transición.
**Why:** el token_ws se re-entrega idempotentemente; NUESTRO side effect (stock + estado) es lo que debe ser idempotente. Que el commit de Webpay sea idempotente es consenso de comunidad [ASSUMED] — el diseño no depende de ello.
**How to avoid:** guard de estado ANTES de los side effects: si la orden ya está PAID → re-mostrar el voucher sin tocar nada (el patrón `checkIsAlreadyProcessed` del plugin oficial [VERIFIED: CommitWebpayController]); el descuento+transición viven en una sola transacción con la guarda adentro.
**Warning signs:** stock que baja de a 2 tras un refresh; dos filas de auditoría para el mismo token.

### Pitfall 5: stock leído en Python (race) — el falso atómico
**What goes wrong:** `if producto.stock >= cantidad: producto.stock -= cantidad` — dos requests leen stock=1, ambos pasan el if, ambos escriben 0 → se vendieron 2 con stock 1.
**Why:** el check y el write son dos operaciones; entre ellas vive la carrera. SQLite serializa los WRITES, no el par read+write.
**How to avoid:** UPDATE condicional con rowcount (Pattern 5). Mini-verificación de la guía: stock=1 + script con dos threads → un PAID y un REJECTED.
**Warning signs:** la palabra `if` antes de un descuento de stock en el diff.

### Pitfall 6: El form auto-submit dentro de useEffect (StrictMode)
**What goes wrong:** el form a Webpay se arma en un `useEffect` → React StrictMode monta/desmonta dos veces en dev → doble submit → dos órdenes PENDING y dos creates en Webpay.
**How to avoid:** submit SOLO en el handler del clic del CTA (Pattern 2); el CTA deshabilitado mientras corre la mutación (`isPending`).
**Warning signs:** dos filas PENDING idénticas al pagar una sola vez.

### Pitfall 7: Enum de estado — el gotcha del enum, TERCERA vuelta
**What goes wrong:** `class EstadoPedido(str, enum.Enum): PENDING = "pending"` guarda "PENDING" en la BD; el contrato enum `[pending, ...]` diverge — mismo bug ya cerrado en guia-03 (familias) y guia-05 (roles).
**How to avoid:** nombre == valor: `pending = "pending"` (Pattern 6). SQLAlchemy persiste NOMBRES.
**Warning signs:** badge "PENDING" en mayúsculas en el historial.

### Pitfall 8: buy_order fuera de límite o duplicado
**What goes wrong:** un numero de pedido con prefijo largo o timestamp (`MAURA-20260930-000001` = 21 chars, pasa; `PEDIDO-WEBPAY-2026-000001` = 25, borderline; cualquiera más largo → `TransactionCreateError` client-side ANTES de ir a Webpay); o dos órdenes con el mismo numero → el commit no sabe a cuál volver.
**How to avoid:** `MAURA-{id:06d}` (11 chars, único por construction desde el autoincrement — Pattern 6); el límite 26 es la constante `ApiConstants.BUY_ORDER_LENGTH` [VERIFIED: api_constants.py].
**Warning signs:** TransactionCreateError "'buy_order' is too long".

### Pitfall 9: El timeout del formulario tarda 10 minutos en integración
**What goes wrong:** el spike/UAT planifica "probar el timeout" y alguien espera 1-2 minutos → nada llega → se concluye que el flujo no existe.
**Why:** el reloj oficial es "4 minutos en producción y de 10 minutos en integración" [CITED: docs oficiales].
**How to avoid:** presupuestar ≥10 min de espera activa en el formulario (la sesión del spike lo cronometra — el dato exacto es parte del hallazgo, D-40); documentarlo en la guía para que el alumno no se aburra antes.
**Warning signs:** un plan de spike sin 15 minutos reservados para el flujo timeout.

### Pitfall 10: CORS confundido con el retorno
**What goes wrong:** alguien "agrega Webpay al CORS" del backend — el POST del retorno es una NAVEGACIÓN de form (full-page), no un fetch: CORS no aplica y jamás aplicó.
**Why:** CORS gobierna lecturas de script cross-origin; el form POST del navegador es navegación clásica.
**How to avoid:** CORS queda como está (fase 2 lo dejó en GET+POST para los fetch de la SPA). La guía aprovecha de ENSEÑAR la diferencia — es exactamente el tipo de lección de la etapa.
**Warning signs:** cualquier `allow_origins` que mencione transbank.cl.

### Pitfall 11: El checkout crea la orden DESPUÉS del create de Webpay
**What goes wrong:** tx.create() primero y "luego guardo la orden" → si algo falla entre ambos, vuelve un token huérfano sin orden; o el retorno llega antes de que la orden exista (race con el propio flujo).
**How to avoid:** D-34 es literal: crear orden PENDING → crear transacción → guardar token → responder. Si tx.create falla, la transacción de BD revierte la orden (todo en el mismo bloque). El orden de la ceremonia ES la decisión.
**Warning signs:** un service que llama a transbank antes de `sesion.add(pedido)`.

### Pitfall 12: La ruta de resultado exige sesión a secas
**What goes wrong:** poner `/pago/resultado` dentro de RequireAuth tal cual → la clienta vuelve de Webpay, el 302 aterriza, y si el token de localStorage expiró (7 días D-20) o abre el link en otro dispositivo, `Navigate to="/login"` con returnTo… al resultado → el voucher nunca se ve tras loguearse si el state se pierde en el full-page load intermedio.
**How to avoid:** ruta pública que degrada con honestidad (estado + numero visibles; "inicia sesión para ver el detalle" con link que SÍ lleva returnTo). La sesión RETOMADA es el caso feliz (localStorage sobrevivió), no el único caso. Discretion de copy (D-45).
**Warning signs:** RequireAuth envolviendo /pago/resultado en el router.

### Pitfall 13: El contrato se olvida del 302 y del form-encoded
**What goes wrong:** el contrato declara el retorno con JSON responses → la fila contrato ↔ `/docs` del cierre detecta desvío (o el router no lo declara y `/docs` muestra solo 200/422 — la lección del 404 de G-01-4, ahora con 302).
**How to avoid:** declarar `responses={'302': ...}` en AMBOS métodos (get/post) del router; requestBody `application/x-www-form-urlencoded` en el POST — el contrato 0.3.0 documenta el endpoint que le habla al navegador (Pattern 7).
**Warning signs:** un `responses=` sin el 302 en el diff del router de retorno.

## Code Examples

> Los ejemplos canónicos ya están inline en Architecture Patterns 1-8 con su fuente. Resumen de verificación de fuentes: SDK transbank (firmas, constantes, validaciones, errores) [VERIFIED: fuente en GitHub master vía raw fetch esta sesión]; docs Webpay Plus oficiales (4 flujos, criterio de aprobación, tarjeta de prueba, form POST, voucher propio, timeouts 4/10 min) [CITED: transbankdevelopers.cl/documentacion/webpay-plus, fetch esta sesión]; discriminador + already-processed + redirect [VERIFIED: CommitWebpayController del plugin oficial WooCommerce, raw fetch esta sesión]; starlette RedirectResponse 307 default [VERIFIED: starlette/responses.py:207-212]; SQLAlchemy update+where+rowcount+synchronize_session [CITED: docs.sqlalchemy.org tutorial/data_update + orm/queryguide/dml, fetch esta sesión].

### Tarjeta y credenciales de prueba (verbatim oficiales — la guía las reproduce)

```text
# Source: transbankdevelopers.cl/documentacion/webpay-plus (fetch esta sesión)
Tarjeta de éxito (integración):  VISA 4051 8856 0044 6623 — CVV 123 —
  vencimiento: cualquiera superior a la fecha actual.
  Autenticación bancaria (3DS): RUT 11.111.111-1 — clave 123.

Credenciales de integración (PÚBLICAS, sin registro — viven en el SDK):
  IntegrationCommerceCodes.WEBPAY_PLUS = "597055555532"
  IntegrationApiKeys.WEBPAY = "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C"
  Host: https://webpay3gint.transbank.cl  (alcance verificado esta sesión: HTTP 404 en / —
  el host responde; los endpoints viven bajo /rswebpaytransaction/api/webpay/v1.2)
```

- **Anulado:** con cualquier pago iniciado, el botón "anular" del propio formulario hosted de Webpay produce el flujo — sin tarjeta especial.
- **Tarjeta de RECHAZO:** las docs oficiales de Webpay Plus no documentan un número de rechazo en la página principal (solo la de éxito verbatim arriba). Ver Open Questions Q2 — el spike/UAT lo resuelve empíricamente (CVV incorrecto, o autenticación bancaria fallida con la clave errada) y la guía documenta el camino que funcione.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Retorno de Webpay por POST (API <1.1) | GET desde API 1.1+ (excepción: abortado en integración sigue POST) | API REST v1.2 vigente | El endpoint se declara GET+POST; discriminar por params, no por método |
| SOAP Webpay (KCC/TBK) | REST `/rswebpaytransaction/api/webpay/v1.2` | REST desde 2018+ | El SDK Python actual es REST-only; los params TBK_* son herencia del protocolo que sobrevive en el retorno |
| Voucher de Transbank al cliente | Voucher del comercio | Doc oficial actual: "ya no se debe mostrar el voucher de Transbank" | PAY-04/D-43 son la práctica oficial, no una ocurrencia |
| Reservar stock al crear la orden | Validar al crear, descontar al aprobar (sin reserva) | Decisión D-35 (esta fase) | Menos estados intermedios; REJECTED por carrera es la lección |

**Deprecated/outdated (no introducir en docs):**
- `transbank-sdk` estilo clase-estática (`Transaction.create(...)` a secas como en ejemplos viejos de internet) — en 6.x es `build_for_integration(...)` instancia [VERIFIED: fuente].
- iframes para el formulario de Webpay: "no se recomienda el uso de Iframe para WebPay Plus" [CITED: docs oficiales].
- python-jose / passlib / Stripe / google-generativeai viejo — se mantienen fuera (STACK "What NOT to Use").

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | El commit de Webpay es idempotente ante re-llamadas (mismo resultado, sin doble cargo) | Pitfall 4, PAY-03 | Bajo — es consenso de comunidad [ASSUMED] (no hallado verbatim en docs oficiales); el diseño NO depende de él: el guard de estado de la orden + transacción única bastan. El spike puede confirmarlo como hallazgo extra (re-entrar al retorno aprobado y observar) |
| A2 | El método HTTP del flujo timeout (y error de formulario) — las docs no lo declaran por flujo (solo el resumen general GET + abortado-integración POST) | Pattern 3, Pitfall 2 | Bajo — el endpoint GET+POST + discriminación por params es inmune; el spike registra la evidencia real (D-41) |
| A3 | El flujo "error de formulario" no es reproducible runtime en integración ("replicable solo en producción" — cita oficial) — el spike corroborará 3 flujos | Pattern 3, Open Q1 | Medio — D-39 esperaba los 4 corroborados: ajustar el alcance del spike (3 runtime + 1 documentado) es un cambio al texto de D-39 que el planner debe reflejar; el manejo del flujo queda igual (rama token_ws+TBK_TOKEN, cubierta por el patrón del plugin oficial) |
| A4 | Existirá un camino reproducible en integración para el estado REJECTED (tarjeta rechazada): candidato CVV incorrecto o clave 3DS errada — no documentado como número de tarjeta | Code Examples, Open Q2 | Bajo-Medio — ORDR-01 necesita exhibir REJECTED; si ningún camino funciona, la guía muestra REJECTED vía la carrera de stock (D-35 también lo produce) y el UAT lo cubre así |
| A5 | Los estados se nombran `pending/paid/cancelled/rejected` (minúsculas en el cable, como `cliente/admin` y las familias) | Pattern 6/7 | Bajo — discretion de nombres; REQUIREMENTS usa PENDING/PAID/CANCELLED/REJECTED (mayúsculas en el requisito) — el contrato/badge mapea mayúsculas solo en presentación |
| A6 | `guia-09/10/11` como partición (backend Webpay+órdenes / vuelta SPA+voucher / historial+cierre) | Project Structure | Bajo — discretion (D-16): 2 o 4 guías también funcionan; la Gran verificación final vive en la última |
| A7 | ADRs 012 (retorno de Webpay), 013 (orden nace al pagar + stock al aprobar), 014 (snapshot de precio) | Project Structure | Bajo — discretion CONTEXT explícita; 012+013 juntas también es defendible |
| A8 | El voucher degrada (no exige login) cuando no hay sesión al volver de Webpay — ruta `/pago/resultado` pública | Pattern 4, Pitfall 12 | Bajo — la sesión sobreviviente es el caso feliz; el degradado es fallback. Copy a discretion (D-45) |
| A9 | `session_id` de Webpay = `str(usuario.id)` (o el numero) — solo espejo informativo; el mapeo real token→orden va por `buy_order` del commit | Pattern 1 | Bajo — discretion; el commit devuelve AMBOS |
| A10 | Tag del contrato `Pago` (+ Pedidos dentro del mismo tag o separado) y nombres `/api/checkout`, `/api/pago/retorno`, `/api/pedidos` | Pattern 7 | Bajo — discretion CONTEXT explícita ("/api/checkout vs /api/pagos; /api/pedidos vs /api/ordenes") |
| A11 | El 400 del checkout por stock insuficiente (vs 409) | Pattern 7 | Bajo — la fila 400 "Regla de negocio violada" ya está reservada con ese texto en el contrato [VERIFIED: contrato_api.yaml:30]; 409 también es defendible, decidir al escribir el contrato |
| A12 | `vci` y `payment_type_code` del commit se muestan solo como nota (no gating) — PAY-03 fija el par response_code+status como criterio único | Pattern 1 | Bajo — locked por REQUIREMENTS; mencionar vci (3DS) como nota educativa es optional |

## Open Questions (RESOLVED)

> Las tres preguntas quedaron resueltas por los planes de la fase 3 — el spike del plan 03-01 (onda 1) resuelve las tres antes de todo plan dependiente. Resolución inline citando plan/tarea (convención de 01/02-RESEARCH). Los valores empíricos los entrega el spike en runtime y aterrizan en 03-SPIKE-RETORNO.md (D-40).

1. **¿El spike corrobora 3 o 4 flujos runtime? (impacto directo en D-39)**
   - What we know: las docs oficiales dicen que el flujo de error de formulario es "replicable solo en producción" [CITED]. El plugin oficial lo maneja (rama doble token) pero corre en producción.
   - What's unclear: si existe alguna forma de dispararlo en integración.
   - Recommendation: planificar el spike para corroborar runtime aprobado/anulado/timeout y DOCUMENTAR el 4° desde las docs + el patrón del plugin (A3). Si el spike encuentra forma de disparar el 4°, mejor — el plan no debe depender de ello.
   - Resolution: (RESOLVED) adoptada la Recommendation — 03-01 Task 1 corre runtime los 3 flujos (aprobado/anulado/timeout) entregando el valor empírico por flujo: método real GET vs POST y params presentes, con veredicto fila a fila contra la tabla de Pattern 3; 03-01 Task 2(1) deja el 4° (error de formulario) como sección DOCUMENTADA (result: documented) desde las docs oficiales + la rama token_ws+TBK_TOKEN del plugin oficial (A3) — PAY-02 queda íntegro porque el discriminador por presencia de params lo maneja sin corrida. La evidencia aterriza en 03-SPIKE-RETORNO.md y alimenta contrato 0.3.0 + ADR-012 (onda 2, D-40/D-41).
2. **¿Cómo se produce un REJECTED reproducible en integración (tarjeta rechazada)?**
   - What we know: solo la tarjeta de éxito está documentada verbatim; las docs no listan número de rechazo en la página principal.
   - What's unclear: si CVV errado / clave 3DS errada / tarjeta genérica producida en el formulario dan response_code != 0 con status FAILED (flujo normal sin aprobación).
   - Recommendation: el spike lo prueba empíricamente (5 minutos extra) y la guía documenta el camino que funcione; fallback garantizado: la carrera de stock produce REJECTED (D-35) y el UAT la ejercita igual.
   - Resolution: (RESOLVED) adoptada la Recommendation — 03-01 Task 2(3a) prueba empíricamente en runtime CVV incorrecto y/o clave 3DS errada en el flujo normal y registra el camino que funcione con el response_code observado; si ninguno funciona, declara el fallback garantizado (la carrera de stock de D-35 también produce REJECTED y el UAT la ejercita igual). El hallazgo queda en 03-SPIKE-RETORNO.md y la guía documenta el camino verificado.
3. **¿Cuál es el tiempo REAL del timeout en integración (¿exactamente 10 min)?**
   - What we know: "4 minutos en producción y de 10 minutos en integración" [CITED].
   - What's unclear: nada sustantivo — el spike lo cronometra y el hallazgo se documenta (D-40).
   - Recommendation: reservar ~15 min en la sesión de spike; la guía le dice al alumno cuánto esperar.
   - Resolution: (RESOLVED) adoptada la Recommendation — 03-01 Task 1(4) cronometra en runtime la espera del flujo timeout (sesión del spike con los 15 min activos reservados, Pitfall 9) y 03-01 Task 2(3c) registra el tiempo real medido como hallazgo en 03-SPIKE-RETORNO.md; la guía (planes 03-04/03-05) le dice al alumno cuánto esperar con el dato cronometrado, no con el estimado de las docs.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Red → `webpay3gint.transbank.cl` | spike + UAT (flujos reales) | ✓ (host responde: HTTP 404 en raíz esta sesión — esperado; los endpoints viven bajo `/rswebpaytransaction/...`) | — | Sin fallback: es el servicio externo real de la fase |
| transbank-sdk (PyPI) | guías backend + spike | ✓ | 6.1.0 (latest, 2025-06-24) [VERIFIED: PyPI JSON API esta sesión] | — |
| Python 3.12 | spike + UAT (backend) | ✓ | 3.12.10 [VERIFIED: 02-RESEARCH Environment] | — |
| uv | spike + UAT (`uv add transbank-sdk`) | ✓ | 0.9.3 [VERIFIED: 02-RESEARCH] | — |
| Node >= 22.22 | UAT (frontend maura-uat) | ✓ portátil | v22.23.3 en `D:/Repos/maura-uat/.tools/node-v22.23.3-win-x64` [VERIFIED: ls esta sesión] | Node sistema 22.18.0 no cumple — usar el portátil (sesión 01-UAT) |
| Workspace `D:/Repos/maura-uat` | spike (D-38) + UAT delegado | ✓ | `backend/`, `frontend/`, `.tools/` presentes [VERIFIED: ls esta sesión] | — |
| python-multipart | parseo del form de retorno | ✓ | 0.0.32 (instalado con fastapi[standard] desde fase 2) | — |
| git | commits del repo (guide-only) | ✓ | 2.50.1 | — |

**Missing dependencies with no fallback:** ninguna.
**Missing dependencies with fallback:** ninguna — el único servicio externo (Webpay integración) está alcanzable y con credenciales públicas que viajan dentro del SDK.

*(Validation Architecture: OMITIDA — `workflow.nyquist_validation: false` explícito en .planning/config.json [VERIFIED: config leída esta sesión]. La validación runtime de la fase es el UAT delegado en maura-uat — los 4 flujos + la carrera de stock — registrado en el `03-UAT.md` correspondiente.)*

## Security Domain

> `security_enforcement: true`, `security_asvs_level: 1`, `security_block_on: high` [VERIFIED: .planning/config.json workflow section, esta sesión]. La fase 3 abre una superficie nueva: dinero (sandbox), stock y un endpoint público que responde navegaciones externas.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | indirecto | Hereda JWT de fase 2 (Bearer en checkout/pedidos); sin superficie nueva de credenciales |
| V3 Session Management | yes | El token JWT sobrevive el full-page load a Webpay (D-21/CART-02 — ya diseñado); voucher degrada sin sesión (Pitfall 12); sin sesiones nuevas |
| V4 Access Control | **yes** | `POST /api/checkout` y `/api/pedidos*` exigen Bearer; **ownership**: `GET /api/pedidos/{numero}` de otra clienta → 404 (no 403 — no revelar existencia); retorno público por diseño (navegación sin Bearer) |
| V5 Input Validation | **yes** | CART-03 como control de integridad: el cliente envía SOLO ids+cantidades, el servidor recalcula precios y valida stock (jamás valores del cliente); Pydantic en checkout; params del retorno tratados como opacos (strings acotados por el SDK: token ≤64) |
| V6 Cryptography | no (nuevo) | Sin cripto nueva — HTTPS lo pone Transbank; las "credenciales" de integración son públicas por diseño |
| V14 Configuration | yes | Credenciales Webpay = constantes públicas del SDK (sin secretos nuevos en `.env` esta fase); `frontend_url`/return_url como Settings; la fase 5 congelará la URL pública (STATE.md ya lo anota) |

### Known Threat Patterns for {Webpay return + órdenes + stock}

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Manipulación de precios/total desde el cliente | Tampering | La entrada no tiene precio (D-27) y el servidor recalcula (CART-03) — el contrato es testigo: CheckoutCreate sin campo precio |
| Oversell por carrera concurrente | Tampering/Elevation | UPDATE condicional `stock >= n` + rowcount en una transacción (Pattern 5); REJECTED honesto al perdedor (D-35) |
| Doble cobro/doble descuento por re-POST del retorno (refresh) | Tampering | Guard de estado de la orden (already-PAID → re-mostrar) + side effects en UNA transacción (Pitfall 4) |
| Falsificar el retorno (POST manual al retorno con token inventado) | Spoofing | Solo token_ws reales commitean; token inválido → `TransactionCommitError` → 302 error (nunca 500); la orden solo transiciona con commit aprobado REAL de Webpay |
| Enumeración de pedidos ajenos (numero secuencial legible) | Information Disclosure | Ownership en `GET /api/pedidos/{numero}` → 404 uniforme; la lista devuelve SOLO las de la dueña del token (filtro por `usuario_id` del claim) |
| IDOR vía usuario_id manipulado en el checkout | Elevation | El `usuario_id` sale del token verificado (`get_current_user` de fase 2), jamás del body |
| Confirmar/consultar transacciones de OTRO comercio | Spoofing | No aplica: el SDK firma con las credenciales propias de integración; tokens ajenos fallan en la API de Transbank |
| Token de Webpay logueado/filtrado en logs | Information Disclosure | El retorno loguea FLUJO y numero, jamás token completo; `card_detail` (últimos 4) solo al voucher dueño — la guía lo enseña explícito |
| CSRF del form de retorno (POST cross-site forjado) | Tampering | El endpoint no muta nada sensible sin validar contra Webpay (commit real); el efecto máximo de un POST forjado con params basura es una 302 a estado de error — sin estado que corromper |
| XSS en la construcción del form de Webpay | Tampering | `document.createElement` con values tipados (nunca `innerHTML`/`dangerouslySetInnerHTML`); hereda el costo enseñado de D-21 (ADR-009) |

## Sources

### Primary (HIGH confidence)
- Código de repo leído esta sesión (valores citados verbatim con línea): `03-CONTEXT.md`, `REQUIREMENTS.md`, `STATE.md`, `ROADMAP.md` §Phase 3, `.planning/config.json`, `docs/04_arquitectura/contrato_api.yaml` (íntegro), `docs/02_requerimientos.md` (íntegro), `docs/03_diseno.md` (íntegro), `docs/05_desarrollo/README.md`, `docs/05_desarrollo/guia-08-checkout.md` (íntegra), `ls docs/04_arquitectura/adr/` (001-011), `01-CONTEXT.md`, `02-CONTEXT.md`, `02-RESEARCH.md`, `PROJECT.md`, `ls D:/Repos/maura-uat` (backend/frontend/.tools).
- Fuente del SDK transbank-sdk-python (master, vía raw.githubusercontent): `transaction.py` (firmas create/commit/status/refund + errores tipados), `webpay_transaction.py` (`build_for_integration`), `api_constants.py` (26/61/255/64 + endpoint v1.2), `integration_commerce_codes.py` (`WEBPAY_PLUS = "597055555532"`), `integration_api_keys.py` (API key pública), `validation_util.py`, README ("Python 3.12+").
- Plugin oficial transbank-plugin-woocommerce-webpay-rest (master, vía raw fetch): `CommitWebpayController.php` (discriminador de 4 flujos, checkIsAlreadyProcessed, redirect final) + árbol de excepciones (`DoubleTokenWebpayException`, `TimeoutWebpayException`, `UserCancelWebpayException`, `AlreadyProcessedException`, `RejectedCommitWebpayException`) vía GitHub API.
- starlette `responses.py:207-212` (RedirectResponse default `status_code: int = 307`).
- PyPI JSON API transbank-sdk → 6.1.0 (2025-06-24, latest). Probe de red: `webpay3gint.transbank.cl` responde (HTTP 404 raíz).

### Secondary (MEDIUM confidence)
- transbankdevelopers.cl/documentacion/webpay-plus (fetch completo esta sesión): los 4 flujos de retorno verbatim, GET vs POST (v1.1+, abortado-integración POST), timeouts 4/10 min, vida del token post-create 5 min, criterio `response_code == 0 && status == AUTHORIZED`, campos del commit (vci/amount/status/buy_order/session_id/card_detail/accounting_date/transaction_date/authorization_code/payment_type_code/response_code/...), form POST con token_ws, "ya no se debe mostrar el voucher de Transbank", tarjeta VISA 4051885600446623 + RUT 11.111.111-1, sin iframes, status() 7 días.
- docs.sqlalchemy.org/en/20/tutorial/data_update.html (update+where, CursorResult.rowcount verbatim) y /orm/queryguide/dml.html (update(Entity).where().values(), synchronize_session auto/fetch/evaluate/False).

### Tertiary (LOW confidence)
- Idempotencia del commit de Webpay ante re-llamada: consenso de comunidad (múltiples resultados de búsqueda) — [ASSUMED], el diseño no depende de ella (A1).
- Tiempo exacto del timeout en integración ("10 minutos" documentado; el valor real lo cronometra el spike — Q3).

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — transbank-sdk re-verificado contra PyPI y leído en FUENTE esta sesión (firmas, constantes, validaciones); sin otros paquetes nuevos.
- Arquitectura (retorno + órdenes): HIGH — los 4 flujos verbatim de docs oficiales + discriminador y guard verbatim del plugin OFICIAL de Transbank; discrepancies GET/POST documentadas y delegadas al spike exactamente como D-41 ordena.
- Pitfalls: HIGH — 13 pitfalls; los críticos (307 default, método ambiguo, commit en anulado, race de stock, doble-commit) provienen de fuente primaria (starlette/SQLAlchemy/SDK/plugin oficial) o de las docs oficiales; los de implementación React son MEDIUM.
- Docs del ciclo: HIGH — series, filas P6, entidades reservadas, CTA de guia-08 y convenciones leídas verbatim de los archivos que la fase extiende.

**Research date:** 2026-09-30
**Valid until:** 2026-10-30 (SDK 6.1.0 estable desde 2025-06; re-verificar si transbank-sdk publica major, si las docs de transbankdevelopers.cl cambian el flujo de retorno, o si el spike encuentra desviaciones materialmente distintas a lo documentado)
