---
phase: 02-cuentas-de-cliente-y-carro-persistente
plan: 04
subsystem: docs
tags: [guia-paso-a-paso, zustand, persist, usequeries, tanstack-query, carro-client-side, hidratacion, badge-aria-live, confirmacion-dos-pasos, requireauth, returnto, checkout-protegido, gran-verificacion-final, contrato-020]

# Dependency graph
requires:
  - phase: 02-cuentas-de-cliente-y-carro-persistente (plan 03)
    provides: guías 05-06 con el patrón store persist/partialize, lib/api.ts con pedir()+interceptor 401, RequireAuth con returnTo y Navbar extendida con sesión — todo lo que guia-07 replica y guia-08 consume
  - phase: 02-cuentas-de-cliente-y-carro-persistente (plan 01)
    provides: contrato_api.yaml 0.2.0 (fila final de la Gran verificación) y ADR-010 (la decisión que guia-07 implementa)
  - phase: 02-cuentas-de-cliente-y-carro-persistente (plan 02)
    provides: RF-06..RF-11, RN-06/RN-08/RN-09, HU-05..HU-08 y pantallas 4-7 — los orígenes que cita la tabla de cierre
provides:
  - docs/05_desarrollo/guia-07-carro.md — el carro client-side completo: useCarroStore persist (maura-carro, solo {producto_id, cantidad}), CTA en ficha con tope, página /carro con hidratación tolerante y vaciado en dos pasos, badge del navbar (CART-01/02)
  - docs/05_desarrollo/guia-08-checkout.md — el checkout protegido con returnTo (AUTH-04) y el CTA deshabilitado (D-31) + la Gran verificación final de la fase 2 con la fila contrato 0.2.0 ↔ /docs y el botón Authorize (GUIDE-02)
  - Convenciones heredables: la confirmación destructiva en dos pasos inline (la replican futuras acciones destructivas), la fila degradada por 404 como patrón de hidratación tolerante, la Gran verificación final con Authorize que replican las fases 3-5
affects: [02-05 (READMEs citan guías 7-8), fase 3 (hereda el CTA deshabilitado listo para encender, el carro sin precios para CART-03 y el spike de retorno Webpay), fase 4 (hereda returnTo y la lección guard=UX), fases 3-5 (replican la Gran verificación final)]

# Actuals (#2632) — mismo scale que el estimate (chars/4 sobre el diff realizado)
actuals:
  tokens: 15443     # 61772 chars / 4 sobre el diff e784575..2a4cd9e (las 2 guías)
  tasks: 2
  commits: 2        # medido: git rev-list --count e784575..2a4cd9e
plan_head_before: e784575fc0b72e1321cc89565dfd7b95d9ad7fbd
plan_head_after: 2a4cd9e7926a40605ff8408434ea69bf45baf844

# Tech tracking
tech-stack:
  added: []          # D-17 guide-only: nada se instala; useQueries llega como parte de @tanstack/react-query ya enseñado en guia-02
  patterns:
    - "Hidratación por ítem con useQueries (número variable de queries en paralelo) reusando el queryKey de la ficha con String(id) — 1 !== \"1\" son cachés distintas"
    - "Confirmación destructiva en dos pasos inline (booleano de estado, sin modal ni window.confirm) — la replican las acciones destructivas futuras"
    - "Fila degradada por 404 y badge Agotado como hidratación tolerante: reusan el chequeo ApiError.status === 404 de guia-04 y el resto de la lista sigue operando"

key-files:
  created:
    - docs/05_desarrollo/guia-07-carro.md
    - docs/05_desarrollo/guia-08-checkout.md
  modified: []

key-decisions:
  - "useQueries para hidratar N ítems variables (los hooks en un loop de largo variable están prohibidos por React) con el queryKey idéntico al de la ficha PERO con String(id): la ficha guarda el id del useParams como string y (\"producto\", 1) es otra caché — el gotcha quedó narrado como error-evitado nº 3"
  - "El tapado D-30 narrado con tres valores con nombre (cantidad guardada / stock vigente / cantidad en pantalla = Math.min(cantidad, stock)) aplicado en stepper, total de línea y Total del panel — y la mini-verificación de guia-07 lo castiga editando localStorage a mano (5 guardadas, stock 2, pantalla 2)"
  - "Ítem con stock 0: fila semi-degradada con badge Agotado, sin stepper y SIN total de línea (nada comprable, nada que sumar); ítem 404: fila degradada con Quitar — el resto del carro sigue operando (T-02-15)"
  - "guia-08 muestra Checkout.tsx completo UNA vez (paso 1) y los pasos 2-4 recorren sus decisiones (guard/vacío/CTA) citando extractos — un solo copy-paste seguro para el alumno"
  - "La Gran verificación final de la fase 2: 12 filas con columna Origen citando RF-06..11/HU-05..08/RN-06/RN-09/ADRs 009-011/D-19..D-33, y la fila 12 comparando el contrato 0.2.0 ↔ /docs con el botón Authorize probado con las cuentas del seed — la pieza que la fase 1 no podía tener (razón de ser del login form-encoded)"

patterns-established:
  - "Patrón de carro client-side de ADR-010 hecho código de guía: store sin precios + hidratación por queryKey compartido + tapado al stock — la lección que CART-03 (fase 3) convierte en segunda barrera"
  - "La convención de cierre de fase con Authorize: contratos con securitySchemes se verifican probando los endpoints protegidos desde /docs con las cuentas del seed (GUIDE-02/ADR-007)"

requirements-completed: [CART-01, CART-02, AUTH-04]

# Coverage (#1602) — un entry por entregable
coverage:
  - id: D1
    description: "guia-07-carro: el carro client-side completo — useCarroStore persist (maura-carro, partialize items, merge en agregar) SIN precios jamás (D-27/RN-08/T-02-12), ficha con 'Agregar al carro' deshabilitado en stock 0 y en el tope con su helper (D-29/D-30), FilaCarro con tres caras (esqueleto/degradada 404/normal con stepper tapado Math.min(cantidad, stock) y aria-label), Carro.tsx con useQueries + queryKey String(id), total tapado, empty state, error general con Reintentar, vaciado en dos pasos inline y badge del navbar con unidades totales/oculto en 0/aria-live (D-28/T-02-14)"
    requirement: CART-01
    verification:
      - kind: other
        ref: "command: plan Task 1 <automated> grep-chain (19 checks: useCarroStore, maura-carro, producto_id, partialize, copies locked, aria-live, queryKey, ADR-010, D-27, min(cantidad, Reintentar, conteos ≥5) — g7-ok"
        status: pass
      - kind: other
        ref: "command: acceptance criteria 5/5 verificados por grep (store sin precio en bloques typescript, Math.min ×4, disabled del stepper y de la ficha en ambos casos, ApiError 404 ×2 + copy error, useState(false) de la confirmación, reduce de unidades + oculto en 0 + mini-verif F5)"
        status: pass
    human_judgment: false
  - id: D2
    description: "guia-08-checkout: /checkout envuelta en RequireAuth con returnTo verificado tras login (AUTH-04/D-32) y la lección explícita guard=UX/seguridad=401-403 (T-02-13), redirect a /carro con replace cuando el carro está vacío, resumen con 'Comprando como {email}' y líneas sin steppers con las mismas reglas de hidratación, CTA 'Pagar con Webpay' deshabilitado con la nota locked (D-31), y la Gran verificación final de la fase 2: tabla numerada con columna Origen + fila contrato 0.2.0 ↔ /docs con Authorize (GUIDE-02/ADR-007)"
    requirement: AUTH-04
    verification:
      - kind: other
        ref: "command: plan Task 2 <automated> grep-chain (19 checks: Gran verificación final, Pagar con Webpay, nota locked, Comprando como, RequireAuth, contrato_api.yaml, Authorize, 0.2.0, 403, RF-09, RF-11, ADR-011, se repite al final de cada fase, fase 3, Volver al carro, copy de error, conteos ≥4) — g8-ok"
        status: pass
      - kind: other
        ref: "command: acceptance criteria 4/4 verificados por grep (ruta envuelta en RequireAuth + Navigate to=/carro replace ×2, disabled attrs + nota ×4 + navegar(-1), tabla | # | Verificación | Origen | + 0.2.0/Authorize/fila ADR-007-GUIDE-02, cortesía de UX + 401/403 del servidor ×3 + Siguiente fase 3)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Comportamiento runtime de CART-01/02 y AUTH-04 según lo que las guías enseñan (badge incrementando en vivo con aria-live, carro y badge tras F5 y cierre de pestaña, tope del stepper con stock editado a mano, fila degradada con id 999 sembrado en localStorage, checkout sin sesión → login → vuelta al checkout, Authorize en /docs con las cuentas del seed)"
    requirement: CART-02
    verification: []
    human_judgment: true
    rationale: "Repo guide-only (D-17): nada se ejecuta aquí — la verificación de este plan es documental (greps sobre las guías, D1/D2). El runtime queda delegado al UAT del agente en D:/Repos/maura-uat (instrucción persistida en AGENTS.md), igual que la sesión 01-UAT de la fase 1."

# Metrics
duration: 13 min
completed: 2026-09-29
status: complete
---

# Phase 2 Plan 4: Guías 07-08 — carro persistente y checkout protegido Summary

**guia-07 (useCarroStore persist bajo maura-carro con solo pares producto_id/cantidad, CTA con tope en la ficha, /carro con hidratación useQueries tolerante a 404/stock 0, vaciado en dos pasos y badge aria-live) y guia-08 (checkout tras RequireAuth con returnTo genérico, CTA deshabilitado D-31 y la Gran verificación final de la fase 2 con la fila contrato 0.2.0 ↔ /docs probada con Authorize) — con 7 y 4 bloques 🧠 y 11 y 4 mini-verificaciones accionables**

## Performance

- **Duration:** 13 min
- **Started:** 2026-09-29T17:31:12Z
- **Completed:** 2026-09-29T17:44:02Z
- **Tasks:** 2 (2 auto)
- **Files modified:** 2 (2 guías nuevas, 1346 líneas)

## Accomplishments
- El carro client-side de ADR-010 quedó enseñado sin desviarse de D-27: el store narra SOLO pares {producto_id, cantidad} con partialize (ningún precio ni snapshot — el error-evitado nº 1 muestra el anti-patrón), y la mini-verificación del paso 2 lo hace visible en el JSON de localStorage (T-02-12 mitigado)
- El tapado al stock (D-30/RN-09) vive en los tres lugares que cuentan — stepper con "+" deshabilitado en el stock vigente, total de línea y Total del panel — narrado con tres valores con nombre (guardado/vigente/en pantalla) y castigado en la mini-verificación editando localStorage a mano (T-02-14)
- La hidratación tolerante quedó como patrón reutilizable: fila esqueleto sin shift, fila degradada por 404 que reusa el chequeo ApiError.status de guia-04, badge "Agotado" sin stepper y el resto del carro operando (T-02-15) — más el gotcha del queryKey String(id) como error-evitado nº 3
- La primera acción destructiva del sistema quedó contratada como patrón: confirmación en dos pasos inline con estado booleano (sin modal ni window.confirm), y la asimetría con "Quitar" explicada por impacto
- guia-08 cierra la fase: returnTo observable de punta a punta (sin sesión → login → vuelta AL checkout), la lección honesta guard=UX/seguridad=401-403 (T-02-13), y la Gran verificación final con 12 filas con Origen de la etapa 2 — la fila 12 compara el contrato 0.2.0 ↔ /docs CON el botón Authorize probado con las cuentas del seed, la pieza que la fase 1 no podía tener

## Task Commits

Each task was committed atomically:

1. **Task 1: guia-07-carro.md — store persistente, CTA en ficha, página /carro y badge** - `f07e4c4` (docs)
2. **Task 2: guia-08-checkout.md — checkout protegido + Gran verificación final de la fase 2** - `2a4cd9e` (docs)

**Plan metadata:** (ver commit docs final)

## Files Created/Modified
- `docs/05_desarrollo/guia-07-carro.md` - Guía del carro (853 líneas), 8 pasos: useCarroStore (maura-carro, partialize), botón de la ficha con tope y helper, FilaCarro con tres caras, Carro.tsx con useQueries/total tapado/empty/error, ruta /carro, vaciado en dos pasos, badge del navbar y prueba de fuego (F5, tope castigado, id 999)
- `docs/05_desarrollo/guia-08-checkout.md` - Guía de cierre (493 líneas), 5 pasos: Checkout.tsx completo (redirect carro vacío, Comprando como, líneas sin stepper, CTA deshabilitado), ruta protegida con RequireAuth y returnTo en vivo, redirect + resumen que calza, CTA deshabilitado, y la Gran verificación final de la fase 2 (tabla 12 filas + fila contrato 0.2.0 con Authorize + sugerencia de commit + Siguiente hacia fase 3)

## Decisions Made
- `useQueries` para hidratar los ítems del carro: la regla de hooks prohíbe un `useQuery` por ítem en un loop de largo variable (el carro cambia de largo al agregar/quitar), y la misma TanStack Query trae la herramienta exacta para N queries en paralelo — con el queryKey idéntico al de la ficha para compartir caché, PERO con `String(id)`: la ficha guarda el id del useParams como string y `("producto", 1)` es una caché distinta de `("producto", "1")` (error-evitado nº 3 de guia-07)
- El tapado D-30 con nombres para los tres valores (`cantidad` guardada, `stock` vigente, `enPantalla = Math.min(cantidad, stock)`) en vez de un min() anónimo — hace la regla RN-09 legible como lección y no como fórmula
- Ítem con stock 0: badge "Agotado" sin stepper y sin total de línea (nada comprable, nada que sumar al Total); ítem 404: fila degradada "Este aroma ya no está disponible" + Quitar — dos niveles de degradación distintos
- guia-08 publica Checkout.tsx completo una sola vez (paso 1) y los pasos 2-4 recorren sus decisiones citando extractos: un solo punto de copy-paste para el alumno, y los temas del plan (guard, vacío, CTA) cada uno con su 🧠 y mini-verificación
- La fila final de la Gran verificación exige el Authorize probado con las cuentas del seed ejecutando GET /api/admin/estado desde /docs — cierra la justificación del login form-urlencoded del contrato 0.2.0 (02-01) con su pago pedagógico visible

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Paso de la ruta /carro adelantado dentro de guia-07**
- **Found during:** Task 1 (redacción de guia-07)
- **Issue:** El plan ordena la ruta de /carro como ítem (9), después del badge del navbar (8) y de las secciones de vaciado (5) — pero las mini-verificaciones de esas secciones exigen navegar /carro y observar el badge en la página real; sin la ruta, cada paso intermedio manda al alumno a una dirección que no existe
- **Fix:** La ruta se cablea en el paso 5 (inmediatamente después de crear Carro.tsx) y el vaciado-en-dos-pasos/badge pasaron a pasos 6-7 con sus mini-verificaciones navegando la página real. Todos los ítems de contenido del plan (1)-(10) están, incluidos los 🧠 y mini-verificaciones por tema; guia-08 distribuyó sus mini-verificaciones (ítem 5) en los pasos 2-4 temáticos por la misma razón
- **Files modified:** docs/05_desarrollo/guia-07-carro.md
- **Verification:** greps del Task 1 (g7-ok) + 5/5 acceptance criteria; estructura canónica completa (7 🧠 / 11 mini-verificaciones)
- **Committed in:** f07e4c4 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Reorganización de la secuencia de pasos por ejecutabilidad del material; cero alcance nuevo y cero contenido del plan omitido (los 10 ítems de guia-07 y los 7 de guia-08 íntegros).

## Issues Encountered
- Ninguna bloqueante. Nota de entorno heredada de 02-01/02-03: los greps del verify se corrieron con `export MSYS_NO_PATHCONV=1` y patrones sin slash inicial (artefacto MSYS/ugrep de este host); ambas cadenas pasaron limpio a la primera (g7-ok, g8-ok).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Las guías 05-08 de la fase existen y encadenan (guia-06 → guia-07 → guia-08 → fase 3): 02-05 (READMEs de estado) puede citarlas con sus hitos y marcar la fase 2 completa
- La fase 3 hereda construido: el checkout con el CTA "Pagar con Webpay" deshabilitado listo para encender (D-31), el carro sin precios que CART-03 convierte en recálculo del backend, la sesión/interceptor que sobreviven los full-page loads de Webpay y el returnTo genérico
- La Gran verificación final de la fase 2 queda como la convención que las fases 3-5 replican (fila contrato ↔ /docs + Authorize ahora que existe securitySchemes)
- Bloqueos de fase vigentes (no de este plan): spike de retorno Webpay obligatorio antes de redactar la guía de pago (flujos anulado/timeout llegan por POST que el JS no puede leer) y la decisión ADR del momento de creación de la orden/descuento de stock

## Self-Check: PASSED

- Archivos en disco: docs/05_desarrollo/guia-07-carro.md, docs/05_desarrollo/guia-08-checkout.md, 02-04-SUMMARY.md — FOUND
- Commits: f07e4c4 (Task 1), 2a4cd9e (Task 2) — FOUND
- Verify del plan re-ejecutado: g7-ok + g8-ok; key_links verificadas (ADR-010/queryKey en guia-07; contrato_api.yaml/RequireAuth en guia-08); commits medidos desde ledger = 2; cadena Siguiente guia-07→guia-08→fase 3 confirmada
