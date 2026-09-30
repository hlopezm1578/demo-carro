---
phase: 03-checkout-webpay-y-rdenes
plan: "05"
subsystem: payments
tags: [historial-pedidos, ordres, badge-estado, voucher-reutilizado, gran-verificacion-final, readmes-de-estado, webpay, uat-delegado]

requires:
  - phase: 03-checkout-webpay-y-rdenes (plan 03-04)
    provides: "guia-09 (GET /api/pedidos que lista TODAS las órdenes de la dueña del token con 404 uniforme del detalle) y guia-10 (VoucherPedido presentation pura que el historial reutiliza tal cual, D-43/D-46)"
  - phase: 03-checkout-webpay-y-rdenes (plan 03-02)
    provides: "contrato_api.yaml 0.3.0 y ADRs 012-014 que la fila contrato ↔ /docs de la Gran verificación final compara y cita"
  - phase: 03-checkout-webpay-y-rdenes (plan 03-03)
    provides: "RF-12..18/RN-10..13/HU-09..11 de docs/02 y pantalla 9 (historial) de docs/03 que guia-11 aterriza y cita como Origen"
provides:
  - "docs/05_desarrollo/guia-11-pedidos-cierre.md: el historial /pedidos (lista con badges honestos PENDING 'En curso' incluida, detalle que reutiliza VoucherPedido, 'Mis pedidos' en el navbar, ruta protegida heredada) + la Gran verificación final de la fase 3 (12 filas: 4 flujos runtime, carrera de stock, contrato 0.3.0 ↔ /docs con 302 y Authorize)"
  - "Los tres índices de estado al cierre real de la fase 3: guías 1-11 / 14 ADRs / Webpay como stack construido, fila 5 honesta en Parcial (fases 4+)"
  - "El gate de cierre documental replicado y en verde: 11 archivos guia-*.md y repo guide-only (git ls-files -- backend frontend vacío, D-17/ADR-008)"
affects: [fase 4 (panel admin hereda las huérfanas PENDING visibles), /gsd-verify-work 03 (UAT delegado en maura-uat), transición de fase 3]

actuals:
  tokens: 9728       # chars/4 sobre el diff real commiteado (38914 chars en 4 archivos)
  tasks: 2
  commits: 2         # medido: git rev-list --count a702d33..HEAD

tech-stack:
  added: []          # plan documental (guide-only, D-17) — sin paquetes
  patterns:
    - "Reutilización entre features como excepción narrada de la regla 6: el import cruzado ../pago/VoucherPedido con su razón firmada (D-46) — la misma forma honesta de la excepción de la regla 5 con el retorno de Webpay"
    - "La Gran verificación final de fase escala con la fase: sus filas citan el Origen nuevo (RF-12+/RN-10+/HU-09+/ADR-012..014) y exigen lo runtime de la etapa (4 flujos con tarjeta oficial, timeout cronometrado, carrera de stock)"
    - "Fila contrato ↔ /docs con las piezas nuevas comparadas: el 302 con Location declarado en ambos métodos y el endpoint público del retorno junto a los protegidos"

key-files:
  created:
    - docs/05_desarrollo/guia-11-pedidos-cierre.md
  modified:
    - docs/05_desarrollo/README.md
    - docs/README.md
    - README.md

key-decisions:
  - "El detalle del historial importa VoucherPedido cruzando features 'con razón' (regla 6): moverlo a components/ re-editaría la guía 10 para cero ganancia funcional y duplicarlo serían dos verdades del mismo detalle — D-46 manda y la excepción va narrada"
  - "La tabla BADGES se copia una vez por pantalla (historial y voucher) en vez de extraerla: con dos consumidoras, copiar es más honesto que adelantarse; el día que nazca la tercera, baja a un módulo propio"
  - "La URL del detalle es /pedidos/MAURA-000001 (numero legible, RN-13) y el 404 uniforme se narra con cara de SPA: el numero ajeno se trata exactamente como el inexistente (ORDR-01)"
  - "La Gran verificación final de fase 3 suma DOS piezas a la fila contrato ↔ /docs: el 302 con su Location (sin declaración /docs ni lo lista y la fila cantaría un desvío falso) y el endpoint público del retorno conviviendo con los protegidos — Authorize probado clienta 200 en /api/pedidos y 403 en /api/admin/estado"

patterns-established:
  - "Cierre de fase documental replicable (tercera vez): índices que cuentan lo que existe + gate de conteo de guías + invariant guide-only — la fila 5 avanza por fase sin marcar el desarrollo completo (D-13/D-18)"
  - "La honestidad de estado como contenido enseñable: PENDING visible 'En curso' sin expiración ni jobs de fondo (D-48/D-49), con el Siguiente anunciando que la gestión de huérfanas es de fase 4"

requirements-completed: [ORDR-01, ORDR-02]

coverage:
  - id: D1
    description: "guia-11-pedidos-cierre: el historial completo — Pedidos.tsx con useQuery de GET /api/pedidos, lista con numero/fecha/total y badges por estado (PENDING visible 'En curso', D-48/D-45), empty state honesto y estados async uniformes; DetallePedido que reutiliza VoucherPedido tal cual (D-43/D-46) con URL por numero legible (D-37/RN-13) y 404 uniforme con cara de SPA; 'Mis pedidos' en el navbar solo con sesión (D-47); ruta protegida con el RequireAuth+returnTo heredado (D-32); tres mini-verificaciones runtime (aprobado+anulado juntos, la huérfana 'en curso', el detalle ajeno) y la Gran verificación final de la fase 3: 12 filas con Origen citando RF-12..18/RN-10..13/HU-09..11/ADR-012..014 (4 flujos runtime con la VISA oficial, timeout con su espera cronometrada 603 s, cuarto flujo explicado como documentado, F5 sin doble pago, carrera de stock un PAID/un REJECTED, carro vacío SOLO en el aprobado, voucher propio, numero legible) y la fila final contrato 0.3.0 ↔ /docs con el 302 y el Authorize"
    requirement: ORDR-01
    verification:
      - kind: other
        ref: "grep chain del Task 1 (g11-ok, re-ejecutado post-commit): Gran verificación final/Mis pedidos/en curso/RequireAuth/0.3.0/4051 8856 0044 6623/MAURA-000001/PENDING/REJECTED/carro/Authorize/ADR-012/huérfana/fase 4 + >=4 bloques 🧠 y >=3 mini-verificaciones — pass"
      - kind: other
        ref: "Parse TypeScript de los 8 bloques tsx con el compilador del taller maura-uat (transpileModule con diagnostics): Pedidos.tsx (140 líneas) y DetallePedido.tsx (102) completos + 6 excerpts (Navbar/rutas/imports) — todos parsean"
        status: pass
    human_judgment: false
  - id: D2
    description: "Los tres índices de estado al cierre real de la fase 3: docs/05_desarrollo/README con filas 9-11 (hitos de una frase), blockquote 'La fase 3 completa sus tres guías (9-11: pago, vuelta, historial)' y mapa mental con la capa de integración externa; docs/README con fila 4 a 14 ADRs y fila 5 a 'Parcial (guías 1-11 listas; continúa en fases 4+)'; README raíz con 14 ADRs, 'las 14 decisiones', fila 5 a guías 1–11 y el párrafo de stack con Webpay construido (pago sandbox operativo, órdenes con snapshot y stock transaccional)"
    requirement: ORDR-02
    verification:
      - kind: other
        ref: "grep chain del Task 2 (cierre-fase3-ok, con gates negativos): guia-09/10/11 en el índice, 1-11 listas y 14 ADRs en docs/README y README raíz, sin 1-8 listas ni 11 ADRs, webpay en README, exactamente 11 archivos guia-*.md en disco y git ls-files -- backend frontend vacío (D-17/ADR-008) — pass"
        status: pass
    human_judgment: false

# Metrics
duration: 10 min
completed: 2026-09-30
status: complete
plan_head_before: a702d33dbbab18ca5e765d438d5319fa417f24e
plan_head_after: dde677408fd449a5e39b4876dfa41d4fab13a1c5
---

# Phase 3 Plan 5: Guía 11 y el cierre de la fase 3 Summary

**El historial /pedidos que hace visible el ciclo de vida de la orden (PENDING "En curso" incluida, detalle que es el MISMO voucher de la guía 10) y la Gran verificación final de la fase 3 — 12 filas con los 4 flujos runtime de Webpay y el contrato 0.3.0 ↔ /docs — más los tres índices de estado contando lo que existe: 11 guías, 14 ADRs, Webpay construido**

## Performance

- **Duration:** 10 min
- **Started:** 2026-09-30T16:30:30Z
- **Completed:** 2026-09-30T16:40:34Z
- **Tasks:** 2
- **Files modified:** 4 (guia-11 nueva 634 líneas + 3 READMEs extendidos)

## Accomplishments

- **El historial con estados honestos (ORDR-01)**: `Pedidos.tsx` consume `GET /api/pedidos` (que la guía 9 construyó filtrando por la dueña del token) y lista TODAS las órdenes con badge por estado — la PENDING visible como "En curso" (D-48/RN-11), sin filtro que la esconda, con empty state honesto ("Todavía no tienes pedidos") y los estados async uniformes de la serie.
- **La reutilización más rentable de la fase, cobrada**: `DetallePedido.tsx` importa `VoucherPedido` tal cual (D-43/D-46 — cero cambios en los archivos de la guía 10) con la excepción narrada de la regla 6 ("features no se importan cruzados *sin razón*"): moverlo a `components/` re-editaría la guía 10 para cero ganancia. La URL es `/pedidos/MAURA-000001` — el numero legible, jamás el id interno (D-37/RN-13) — y el 404 uniforme del backend se experimenta con cara de SPA ("Pedido no encontrado" para el ajeno y el inexistente, IGUAL).
- **"Mis pedidos" en el navbar (D-47) y la ruta protegida heredada (D-32)**: el link vive solo con sesión junto al email/"Cerrar sesión", y `/pedidos` + `/pedidos/:numero` se suman DENTRO del bloque `RequireAuth` existente — el returnTo genérico se cobra por segunda vez sin editar guard ni login. El contraste con `/pago/resultado` pública cierra la lección: degradar o expulsar depende de si queda algo honesto que mostrar sin sesión.
- **La Gran verificación final de la fase 3** replicando la convención de guías 4/8: 12 filas con columna Origen citando RF-12..18/RN-10..13/HU-09..11/ADR-012..014 — los 4 flujos runtime en el navegador (aprobado con la VISA oficial `4051 8856 0044 6623`, anulado con CARRO INTACTO, timeout con su espera cronometrada 603 s documentada, el cuarto flujo explicado como "replicable solo en producción"), la carrera de stock (un PAID y un REJECTED), el F5 sin doble pago, el carro vacío SOLO en el aprobado, y la fila final contrato 0.3.0 ↔ `/docs` con el **302 con su Location** y el **endpoint público del retorno** como piezas nuevas — más el Authorize probado (clienta 200 en `/api/pedidos`, 403 en `/api/admin/estado`).
- **El estado honesto en los tres índices (D-13/D-18)**: `docs/05_desarrollo/README` con filas 9-11, blockquote de fase 3 completa y el mapa mental sumando la **capa de integración externa**; `docs/README` y README raíz con fila 4 a 14 ADRs y fila 5 a "guías 1-11 listas; continúa en fases 4+" — sin marcar el desarrollo completo. El párrafo de stack del README raíz pasa a Webpay como construido: "pago sandbox operativo, órdenes con snapshot y stock transaccional".
- **El gate de cierre documental replicado y en verde**: exactamente 11 archivos `guia-*.md` en el directorio y `git ls-files -- backend frontend` vacío (D-17/ADR-008) — el invariant guide-only sigue vivo al cierre de la tercera fase.

## Task Commits

1. **Task 1: guia-11-pedidos-cierre.md — historial /pedidos que reutiliza el voucher + Gran verificación final de la fase 3** - `c725e10` (docs)
2. **Task 2: READMEs de estado — guías 1-11, 14 ADRs y Webpay construido** - `dde6774` (docs)

## Files Created/Modified

- `docs/05_desarrollo/guia-11-pedidos-cierre.md` - Guía de cierre (634 líneas, 8 pasos + Gran verificación + error evitado + cierre): Pedidos.tsx, DetallePedido.tsx, navbar, rutas protegidas, las corridas runtime y la tabla final de 12 filas.
- `docs/05_desarrollo/README.md` - Índice de guías con filas 9-11, blockquote de fase 3 completa y mapa mental con la capa de integración externa.
- `docs/README.md` - Tabla del ciclo: fila 4 a 14 ADRs, fila 5 a "Parcial (guías 1-11 listas; continúa en fases 4+)".
- `README.md` - Portada raíz: 14 ADRs, "las 14 decisiones", fila 5 a guías 1–11 y stack con Webpay construido.

## Decisions Made

- El detalle importa `VoucherPedido` cruzando features con la razón firmada (D-46) en vez de moverlo a `components/`: la regla 6 dice "*sin razón*" y la razón es una decisión de producto — la misma forma honesta de la excepción de la regla 5 que la guía 10 narró para el retorno.
- La tabla `BADGES` se copia una vez por pantalla (historial + voucher) con el fallback `?? BADGES.pending`: con dos consumidoras, copiar es más honesto que adelantar un módulo compartido; el 🧠 deja dicho que la tercera consumidora lo baja a módulo propio.
- El título del detalle es un neutro "Tu pedido": la verdad del estado la dice el badge del voucher — herencia directa de la regla de la guía 10 (el título por el estado REAL, no por el query param).
- La fila 12 de la Gran verificación compara DOS piezas nuevas: el 302 con su `Location` (declarado en ambos métodos — sin declaración, `/docs` ni lo lista y la fila cantaría un desvío falso) y el endpoint público del retorno conviviendo con los protegidos (ADR-012).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Dos typos en la redacción original de guia-11**
- **Found during:** Task 1 (revisión post-escritura, pre-commit)
- **Issue:** "VoucherPago" por "VoucherPedido" en el 🧠 del paso 2 y "approbaron" (doble p) en el 🧠 del paso 5
- **Fix:** Corregidos ambos antes del commit
- **Files modified:** docs/05_desarrollo/guia-11-pedidos-cierre.md
- **Verification:** greps de typos en verde; verify completo del Task 1 re-ejecutado post-commit (g11-ok)
- **Committed in:** c725e10 (parte del commit del Task 1)

---

**Total deviations:** 1 auto-fixed (bug tipográfico, corregido antes de commitear)
**Impact on plan:** Sin impacto de alcance — las must_haves truths se cumplen tal cual.

## Issues Encountered

None - ambos verifies corrieron planos (ningún patrón inicia con "/", así que el path-mangling de Git Bash documentado en fases anteriores no aplicó) y se re-ejecutaron post-commit.

## Authentication Gates

None - sin servicios externos ni credenciales en este plan (documental puro).

## User Setup Required

None - no external service configuration required.

## Known Stubs

None - los bloques de código de la guía están completos (verificados por parse TypeScript); no hay placeholders ni TODOs.

## Next Phase Readiness

- **Fase 3 completa**: 5/5 planes con SUMMARY (spike → contrato/ADRs → docs 02/03 → guías 09-10 → guia-11 + índices). La cadena de guías 01→11 está grep-verificada por los gates de cada plan y el "Siguiente" de guia-11 anuncia la fase 4 con la gestión de huérfanas PENDING (D-49).
- **La runtime queda delegada al UAT en maura-uat** (verificación documental D-17): los 4 flujos en el navegador, el historial con los 4 estados visibles, la carrera de stock y la fila contrato ↔ /docs con Authorize — el flagged_assumption del plan (ORDR-01 runtime) se cierra ahí, construyendo guia-11 en el taller como las guías 05-10.
- **La fase 4 hereda el terreno listo**: cuentas con rol admin desde la guía 5, stock atómico y estados honestos desde la 9/11, y las huérfanas PENDING visibles esperando gestión.

## Self-Check: PASSED

- FOUND: docs/05_desarrollo/guia-11-pedidos-cierre.md (634 líneas)
- FOUND: docs/05_desarrollo/README.md, docs/README.md, README.md (los tres extendidos)
- FOUND: commit c725e10 (Task 1)
- FOUND: commit dde6774 (Task 2)
- Verify Task 1 (g11-ok): pass — re-ejecutado post-commit
- Verify Task 2 (cierre-fase3-ok): pass — re-ejecutado post-commit (11 guías + guide-only)

---
*Phase: 03-checkout-webpay-y-rdenes*
*Completed: 2026-09-30*
