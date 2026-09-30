---
phase: 03-checkout-webpay-y-rdenes
plan: "04"
subsystem: payments
tags: [webpay, transbank-sdk, ordenes, snapshot-precio, retorno-302, stock-atomico, form-auto-submit, voucher, spa]

requires:
  - phase: 03-checkout-webpay-y-rdenes (plan 01)
    provides: "03-SPIKE-RETORNO.md — el veredicto por flujo (anulado por GET con TBK_TOKEN, presencia 100% estable) que las guías narran como 'lo que el spike reveló' (D-40)"
  - phase: 03-checkout-webpay-y-rdenes (plan 02)
    provides: "contrato_api.yaml 0.3.0 (4 paths nuevos, CheckoutCreate sin precio, retorno GET+POST con 302, 404 uniforme) y ADRs 012-014 que las guías implementan y citan"
  - phase: 03-checkout-webpay-y-rdenes (plan 03)
    provides: "RF-12..18/RN-10..13/HU-09..11 de docs/02 y entidades PEDIDO/LÍNEA con DFDs 9.0-11.0 y pantallas 8-9 de docs/03 que las guías aterrizan en código"
provides:
  - "docs/05_desarrollo/guia-09-ordenes-webpay.md: el backend del pago por capas — modelo con snapshot y numero MAURA-{id:06d} (D-36/D-37), iniciar_checkout que recalcula sin confiar en el cliente (CART-03), procesar_retorno con discriminador por presencia + criterio doble + guard ya-PAID (PAY-02/PAY-03), descontar_stock_atomico UPDATE condicional + rowcount (ORDR-02) y la carrera de stock demostrable"
  - "docs/05_desarrollo/guia-10-retorno-voucher.md: la vuelta a la SPA — CTA encendido con form POST auto-submit en el handler del clic (PAY-01), ruta pública /pago/resultado con voucher de la tienda (D-43) y carro vaciado SOLO al aprobar + invalidateQueries de stock (D-44)"
  - "Los tres conceptos nuevos de la etapa como bloques de guía citando ADR-012/013/014, Patterns 1-8 del research y las 13 mini-verificaciones accionables (incluida la del pago real con la VISA oficial)"
affects: [03-checkout-webpay-y-rdenes (plan 03-05 — guia-11 reutiliza VoucherPedido y cierra la fase), docs/05_desarrollo/README.md (filas 9-10), Gran verificación final de fase 3]

actuals:
  tokens: 27324      # chars/4 sobre el diff real commiteado (109298 chars en 2 guías nuevas, 2330 líneas)
  tasks: 2
  commits: 2         # medido: git rev-list --count 3473c39..HEAD

tech-stack:
  added: []          # guide-only (D-17): transbank-sdk 6.1.0 lo instala el ALUMNO con uv add (Paso 1 de guia-09); el repo no ejecuta installs
  patterns:
    - "Bloques de guía con código sin precedente en el corpus (pagos): fuente Patterns 1-8 de 03-RESEARCH verificada contra SDK/plugin oficial/starlette/SQLAlchemy, con los imports del SDK confirmados contra el spike que corrió runtime"
    - "La transacción de pedidos la cierra el SERVICE (repo hace flush sin commit): abarca la llamada a Webpay (Pitfall 11) y la pareja descuento+transición (ADR-013)"
    - "Mini-verificación de carrera en dos fases: httpx concurrente para los checkouts (validar no reserva) + dos threads por el MISMO bloque del commit aprobado para el veredicto (un PAID, un REJECTED, stock 0)"
    - "El título de la pantalla de resultado se decide por el estado REAL fetcheado, no por el query param — el badge del voucher jamás miente"

key-files:
  created:
    - docs/05_desarrollo/guia-09-ordenes-webpay.md
    - docs/05_desarrollo/guia-10-retorno-voucher.md
  modified: []

key-decisions:
  - "La carrera de stock se demuestra en dos fases (dos checkouts concurrentes → dos PENDING; luego dos threads ejecutando el bloque del retorno aprobado sin Webpay en el medio): commitear tokens no pagados NO aprueba en integración y el alumno de guia-09 todavía no tiene SPA para pagar — el UPDATE condicional es exactamente el código que el commit aprobado ejecuta"
  - "services/pedidos.py recibe la SESIÓN (no un repo) y sus repos hacen flush sin commit: las fronteras de transacción de la orden abarcan la llamada a Webpay y la pareja descuento+transición (Pitfall 11, ADR-013)"
  - "El 302 viaja con estado ∈ {pagado, rechazado, anulado, timeout, error} + orden como query params, pero el voucher renderiza el estado REAL del pedido fetcheado — el query param nombra el flujo, el badge dice la verdad"
  - "apiPost ya existía desde guia-06 (el registro): guia-10 lo reusa con Bearer y narra la primera excepción de la regla 5 — el checkout ES fetch, el retorno es navegación del navegador"
  - "El degradado sin sesión usa el returnTo genérico con la query DENTRO del string (el login lee from.pathname y navigate() la parsea) — Pitfall 12 resuelto sin editar el login de guia-06"

patterns-established:
  - "Tercera vuelta del gotcha del enum cerrada con lección explícita (familias → roles → estados): la guía la narra citando las dos vueltas previas"
  - "El discriminador por presencia de params como función pura y testeable (clasificar_flujo) verificable offline en la máquina del alumno"
  - "Efectos no idempotentes jamás en useEffect (el submit del form) versus efectos idempotentes que sí (el vaciado del carro) — el criterio enseñado con su porqué (Pitfall 6)"

requirements-completed: [CART-03, PAY-01, PAY-02, PAY-03, PAY-04, ORDR-02]

coverage:
  - id: D1
    description: "guia-09-ordenes-webpay: el backend completo de la etapa por capas implementando el contrato 0.3.0 — instalación de transbank-sdk con credenciales públicas sin registro, EstadoPedido (tercera vuelta del gotcha), Pedido/LineaPedido con snapshot y numero legible, schemas sin campo precio (CART-03), repository con flush sin commit y descontar_stock_atomico (UPDATE condicional + rowcount), services/webpay único importador de transbank, iniciar_checkout que recalcula y crea PENDING antes de Webpay, procesar_retorno con discriminador/criterio doble/guard ya-PAID, routers con 302 declarado y 404 uniforme, main.py 0.3.0 con CORS intacto, y la carrera de stock de dos threads"
    requirement: CART-03
    verification:
      - kind: other
        ref: "grep chain del Task 1 (g9-ok, re-ejecutado post-commit): transbank-sdk/build_for_integration/EstadoPedido/snapshots/MAURA-/RedirectResponse 302/rowcount/params TBK/Form(default=None)/597055555532/criterio doble/estados/ADRs/contrato/tarjeta oficial + >=5 bloques 🧠 y >=5 mini-verificaciones — pass"
        status: pass
      - kind: other
        ref: "AST syntax check de los 11 bloques Python completos de la guía (models/schemas/repo/webpay/service completo/routers×3/carrera.py) — todos parsean"
        status: pass
    human_judgment: false
  - id: D2
    description: "guia-10-retorno-voucher: la vuelta a la SPA — CTA encendido con useMutation + form POST auto-submit por document.createElement submiteado SOLO en el handler del clic con disabled={isPending}, ruta pública /pago/resultado fuera de RequireAuth con degradado sin sesión y returnTo, VoucherPedido de la tienda (numero/fecha/líneas snapshot/total/badge) y ResultadoPago que lee el 302 y fetcha el pedido, vaciado del carro SOLO con paid + invalidateQueries de stock, y las tres mini-verificaciones reales (aprobado/anulado/F5)"
    requirement: PAY-04
    verification:
      - kind: other
        ref: "grep chain del Task 2 (g10-ok, re-ejecutado post-commit) con gates negativos: sin dangerouslySetInnerHTML ni iframes — pass (7 🧠, 9 mini-verificaciones)"
        status: pass
      - kind: other
        ref: "Parse TypeScript de los bloques tsx/ts con el compilador del taller maura-uat: los archivos completos (VoucherPedido, ResultadoPago, tipos) parsean; el único fragmento no standalone es el excerpt de rutas de main.tsx, misma forma que el de guia-08"
        status: pass
    human_judgment: false

# Metrics
duration: 25 min
completed: 2026-09-30
status: complete
plan_head_before: 3473c3941ec30bdd56b03174ad26bacbd3870569
plan_head_after: 26dd3625138046e0411bd3cd377873a7b43c9eb8
---

# Phase 3 Plan 4: Guías 09-10 — backend del pago y vuelta a la SPA Summary

**guia-09 (backend: orden con snapshot que nace al pagar, checkout que recalcula sin confiar en el cliente, retorno que discrimina los 4 flujos con 302 y stock atómico con carrera demostrable) y guia-10 (vuelta: form POST auto-submit del CTA en el handler del clic, ruta pública de resultado con voucher de la tienda y carro que se limpia solo al aprobar)**

## Performance

- **Duration:** 25 min
- **Started:** 2026-09-30T16:02:38Z
- **Completed:** 2026-09-30T16:27:30Z
- **Tasks:** 2
- **Files modified:** 2 (guia-09 1501 líneas + guia-10 829 líneas, ambas nuevas)

## Accomplishments

- **El código nuevo sin precedente del corpus vive como bloques en las guías (D-17)** con su fuente en los Patterns 1-8 del research: la instancia `build_for_integration`, el discriminador por presencia en el orden del plugin oficial, el `RedirectResponse(url, status_code=302)`, el UPDATE condicional + rowcount y el form auto-submit — con los imports del SDK confirmados contra el spike que corrió runtime (incluido el gotcha `"token"` vs `token_ws` del create).
- **CART-03 enseñado como forma, no como chequeo**: `CheckoutCreate` sin campo precio (el experimento de la mini-verificación muestra un `"precio": 1` inyectado desapareciendo en las narices de Pydantic) y `iniciar_checkout` que hidrata contra el catálogo, recalcula con precio vigente, valida stock sin tocarlo (400) y SOLO DESPUÉS llama a Webpay (D-34, Pitfall 11).
- **PAY-02/PAY-03 con las defensas en orden y narradas con la evidencia del spike**: discriminador `clasificar_flujo` puro y testeable offline, commit solo en la rama `token_ws`-solo con `TransactionCommitError` atrapado (nunca 500), mapeo token→orden por `buy_order` del commit, guard ya-PAID sin side effects y criterio doble `response_code == 0` AND `AUTHORIZED` — ambos.
- **ORDR-02 observable en la máquina del alumno**: `carrera.py` con stock=1 — dos checkouts concurrentes crean DOS órdenes PENDING (validar no reserva, D-35) y dos threads ejecutan el bloque del retorno aprobado: exactamente un PAID, un REJECTED y stock 0, con la salida esperada impresa en la guía.
- **PAY-01/PAY-04 en la vuelta**: CTA encendido con `document.createElement` + submit SOLO en el handler del clic (Pitfall 6 con el criterio completo: efectos no idempotentes jamás en useEffect; el vaciado sí, porque vaciar dos veces es vaciar), ruta pública `/pago/resultado` con degradado honesto y returnTo que lleva la query, voucher de la tienda reutilizable por guia-11 (D-43/D-46) y carro limpio solo con `paid` + invalidateQueries de stock (D-44).
- **Las llaves del sandbox documentadas verbatim**: VISA `4051 8856 0044 6623` (CVV 123, RUT `11.111.111-1` con puntos, clave 123), el anulado por el botón del formulario, el camino a REJECTED por TSN del simulador 3DS y el timeout de ~10 min con la advertencia del tab dormido (hallazgos del spike puestos a trabajar).

## Task Commits

1. **Task 1: guia-09-ordenes-webpay.md — modelo con snapshot, checkout que recalcula, retorno que discrimina y stock atómico** - `dedbef0` (docs)
2. **Task 2: guia-10-retorno-voucher.md — form auto-submit del CTA, ruta pública /pago/resultado y voucher de la tienda** - `26dd362` (docs)

## Files Created/Modified

- `docs/05_desarrollo/guia-09-ordenes-webpay.md` - Guía del backend del pago (10 pasos + error evitado + cierre): instalación con credenciales públicas, models/pedido, schemas espejo 0.3.0, repository con la muralla del stock, wrapper webpay, services ida/vuelta, routers con 302, main.py 0.3.0 y la prueba de fuego con la carrera.
- `docs/05_desarrollo/guia-10-retorno-voucher.md` - Guía de la vuelta (7 pasos + error evitado + cierre): tipos espejo, CTA encendido, ruta pública, VoucherPedido, ResultadoPago con degradado, el vaciado en un punto y el pago real de ida y vuelta.

## Decisions Made

- La mini-verificación de la carrera se diseñó en dos fases (ver Deviations #1): los httpx concurrentes crean las dos PENDING y los dos threads ejecutan el MISMO bloque del commit aprobado que producción corre — el veredicto (un PAID, un REJECTED, stock 0) queda determinista sin depender de que Webpay apruebe tokens no pagados.
- `services/pedidos.py` recibe la sesión y sus repos hacen flush sin commit: la transacción de la orden abarca la llamada a Webpay y la pareja descuento+transición — la diferencia con `UsuarioRepository.crear` (que commitea) está narrada como decisión de la etapa.
- El título de ResultadoPago se decide por el estado REAL del pedido fetcheado (paid/pending/rechazado) y no por el query param del 302: el param nombra el flujo, el badge dice la verdad — cubre también el borde del refresh sobre una orden aún pending.
- El link del degradado sin sesión lleva el returnTo con la query dentro del string (`from.pathname`): el login de guia-06 no se edita y React Router parsea la query al navegar — el truco está comentado en el código y narrado en el 🧠.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] La mini-verificación de la carrera no puede producir PAID vía httpx sin pago real**
- **Found during:** Task 1 (diseño del paso 10 de guia-09)
- **Issue:** El plan pedía "script httpx de dos threads contra dos checkouts → exactamente un PAID y un REJECTED". Pero el checkout solo crea PENDING (valida sin tocar stock) y commitear en Webpay un token que nadie pagó NO aprueba (la clienta no tiene SPA en guia-09 para pagar; el commit de un token no autorizado termina en TransactionCommitError o response_code != 0) — el script literal habría terminado con dos errores y cero lección de stock.
- **Fix:** `carrera.py` en dos fases: (1) dos `POST /api/checkout` concurrentes con httpx contra la última unidad → dos órdenes PENDING (la primera mitad de la lección: validar no reserva, D-35); (2) dos threads ejecutando el bloque del retorno aprobado — el MISMO `descontar_stock_atomico` + transición que producción corre cuando el criterio doble aprueba — → un PAID, un REJECTED, stock 0. La narración lo dice explícito: "el commit de la pasarela YA aprobó cuando este código corre en la app real".
- **Files modified:** docs/05_desarrollo/guia-09-ordenes-webpay.md
- **Verification:** la salida esperada del script está impresa en la guía (un PAID, un REJECTED, stock 0, con la nota de que el ganador varía y la cuenta no); la runtime queda para el UAT delegado (flagged_assumption del plan).
- **Committed in:** dedbef0 (Task 1)

**2. [Rule 3 - Blocking] El seed no creaba las tablas nuevas: `create_all` solo ve los modelos importados**
- **Found during:** Task 1 (paso 2 de guia-09)
- **Issue:** `Base.metadata.create_all` (dentro de `app/seed.py`) solo crea las tablas de los modelos cuyo módulo está importado al correrlo — `seed.py` importa producto y usuario, pero no pedido: las tablas `pedidos`/`pedidos_lineas` jamás habrían nacido.
- **Fix:** Una línea en la guía: `from app.models import pedido  # noqa: F401 — registra pedidos/pedidos_lineas en el create_all`, con la mini-verificación del seed re-ejecutado (14 `[=]` + tablas nuevas, ADR-005).
- **Files modified:** docs/05_desarrollo/guia-09-ordenes-webpay.md
- **Verification:** mini-verificación del paso 2 lo manda a ejecutar `uv run python -m app.seed` y verificar las tablas.
- **Committed in:** dedbef0 (Task 1)

**3. [Rule 2 - Consistencia] La versión de `main.py` sube a 0.3.0 (el plan decía "solo include_router")**
- **Found during:** Task 1 (paso 9 de guia-09)
- **Issue:** El paso (8) del plan decía "main.py: solo include_router nuevos" — pero el título de `/docs` muestra la versión declarada y la fila contrato ↔ `/docs` de la Gran verificación final (guia-11) comparará contra 0.3.0: una app que implementa 0.3.0 presentándose como 0.2.0 es un desvío que el cierre detectaría (la misma coherencia que guia-05 exigió con 0.2.0, ADR-007).
- **Fix:** `version="0.3.0"` con el comentario de siempre, narrado como decisión de coherencia (y fuera de la lista "solo include_router").
- **Files modified:** docs/05_desarrollo/guia-09-ordenes-webpay.md
- **Verification:** mini-verificación del paso 9 punto 1 ("el título dice Maura API 0.3.0").
- **Committed in:** dedbef0 (Task 1)

---

**Total deviations:** 3 auto-fixed (1 bug de diseño de verificación, 1 blocking, 1 consistencia)
**Impact on plan:** Las tres dentro del archivo que el Task 1 ya creaba; ninguna cambió el alcance (las must_haves truths se cumplen tal cual — la carrera sigue siendo "stock=1 y dos threads → un PAID y un REJECTED", solo que con las dos fases explícitas).

## Issues Encountered

None - sin artefactos de ambiente (ningún grep de los verify usa patrón que inicie con `/`; ambos corrieron planos y se re-ejecutaron post-commit).

## Authentication Gates

None - las credenciales de integración de Transbank son públicas y viajan dentro del SDK (guia-09 lo enseña explícito: sin registro ni `.env` nuevo, la aclaración pedida por el usuario).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **Onda 4 restante (03-05) desbloqueada**: guia-11 reutiliza `VoucherPedido` tal cual (D-46 — el componente es presentation pura a propósito), hereda la ruta `/pedidos` protegida con el patrón de guia-08, y su Gran verificación final compara el contrato 0.3.0 contra `/docs` incluyendo el 302 del retorno y los 4 flujos runtime.
- **La cadena de guías está lista para el eslabón final**: el "Siguiente" de guia-09 apunta a guia-10 por nombre de archivo, y el de guia-10 a guia-11-pedidos-cierre.md — grep-verificado por los gates de ambos verify.
- **La runtime queda delegada al UAT en maura-uat** (verificación documental D-17): los 4 flujos con la VISA oficial, la carrera de stock de `carrera.py`, el F5 sin doble pago y el degradado sin sesión — los flagged_assumptions del plan (CART-03/PAY-03/PAY-04/ORDR-02 runtime) se cierran ahí.

## Self-Check: PASSED

- FOUND: docs/05_desarrollo/guia-09-ordenes-webpay.md (1501 líneas)
- FOUND: docs/05_desarrollo/guia-10-retorno-voucher.md (829 líneas)
- FOUND: commit dedbef0 (Task 1)
- FOUND: commit 26dd362 (Task 2)
- Verify Task 1 (g9-ok): pass — re-ejecutado post-commit
- Verify Task 2 (g10-ok, con gates negativos): pass — re-ejecutado post-commit

---
*Phase: 03-checkout-webpay-y-rdenes*
*Completed: 2026-09-30*
