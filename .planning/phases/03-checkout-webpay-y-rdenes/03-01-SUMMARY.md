---
phase: 03-checkout-webpay-y-rdenes
plan: 01
subsystem: payments
tags: [webpay, transbank, spike, retorno, redirect-302, integration-testing]

requires:
  - phase: 02-cuentas-de-cliente-y-carro-persistente
    provides: taller maura-uat con backend/frontend hasta guia-08 (base del spike) y el formato de evidencia delegada 02-UAT
provides:
  - "03-SPIKE-RETORNO.md: evidencia runtime de los 4 flujos del retorno de Webpay Plus integración (método, params, timing) — insumo del contrato 0.3.0, ADR-012 y guías 09-11 (D-40)"
  - "Decisión de mecánica firmada (D-41): redirect 302 del backend a /pago/resultado — la que el ADR-012 registrará"
  - "Camino reproducible a REJECTED verificado (Q2) + idempotencia del commit confirmada (A1) + timeout cronometrado 603 s (Q3)"
affects: [03-checkout-webpay-y-rdenes (planes 03-02..03-05), ADR-012, contrato_api.yaml 0.3.0, guia-09/10/11]

actuals:
  tokens: 4739        # chars/4 sobre el diff real commiteado (18956 chars); el código del spike vive en maura-uat y jamás toca este repo (D-17/D-38)
  tasks: 2
  commits: 2

tech-stack:
  added: []            # transbank-sdk 6.1.0 se instaló SOLO en maura-uat/spike-retorno (fuera del repo); las guías de 03-04 lo enseñarán al alumno
  patterns:
    - "Documento de hallazgos de spike (formato 02-UAT + tabla de veredictos) — reutilizable por fases futuras"
    - "Evidencia runtime delegada al agente sobre ambiente real de integración (credenciales públicas 597055555532)"

key-files:
  created:
    - .planning/phases/03-checkout-webpay-y-rdenes/03-SPIKE-RETORNO.md
  modified: []

key-decisions:
  - "Spike corrobora 3 flujos runtime y corrige las docs en el anulado: llega por GET (no POST como decían las docs de integración) con TBK_TOKEN+TBK_ID_SESION+TBK_ORDEN_COMPRA sin token_ws — el endpoint GET+POST con discriminador por presencia de params es inmune (Pitfall 2)"
  - "Mecánica del retorno firmada (D-41): RedirectResponse con 302 EXPLÍCITO a /pago/resultado con query params; página intermedia descartada; el 307 default de starlette re-POSTearía el form contra la SPA (Pitfall 1)"
  - "Camino a REJECTED reproducible (Q2): elegir Rechazar/TSN en el simulador bancario → retorno normal con token_ws → commit response_code=-1/FAILED; CVV errado NO rechaza (aprueba igual); clave 3DS errada → error.cgi+INITIALIZED sin commit; fallback carrera de stock declarado"
  - "Timeout cronometrado (Q3): 603 s (10:03) desde la carga del form; PERO el redirect NO está garantizado si el tab duerme (13 min sin retorno observado) — las PENDING huérfanas son reales y D-48/D-49 las cubren"
  - "Idempotencia del commit de Webpay confirmada runtime (A1): segunda llamada con el mismo token devuelve respuesta idéntica; el guard de estado OUR-side sigue obligatorio (Pitfall 4)"
  - "4° flujo (error de formulario) documentado sin corrida (A3): intento de replicación en integración produce Error 21 — corrobora la cita oficial 'replicable solo en producción'"

patterns-established:
  - "Spike doc pattern: frontmatter verified_by delegado + expected/result/evidence por flujo + tabla de veredictos con cita para el ADR"
  - "Los retornos del navegador pueden REPETIRSE (7 repeticiones observadas de un mismo timeout): el backend del retorno debe tolerar duplicados"

requirements-completed: [PAY-01, PAY-02]

coverage:
  - id: D1
    description: "Los 4 flujos oficiales del retorno de Webpay documentados con evidencia: 3 corroborados runtime (aprobado con VISA oficial, anulado con el botón del form, timeout cronometrado 603 s) y el 4° (error de formulario) documentado desde docs oficiales + plugin oficial"
    requirement: PAY-02
    verification:
      - kind: other
        ref: "grep chain del Task 1 (spike-flujos-ok): verified_by/aprobado/anulado/timeout/token_ws/TBK_TOKEN/TBK_ID_SESION/TBK_ORDEN_COMPRA/evidence + >=3 result — pass"
        status: pass
      - kind: manual_procedural
        ref: "03-SPIKE-RETORNO.md ## Tests secciones 1-4 (eventos.jsonl del taller maura-uat/spike-retorno, corridas 2026-09-30 14:49-15:19 UTC)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Decisión de mecánica del retorno (D-41) firmada con evidencia por flujo: 302 explícito a /pago/resultado, página intermedia descartada, trampa del 307 registrada"
    verification:
      - kind: other
        ref: "grep chain del Task 2 (spike-cierre-ok): error de formulario/Decisión de mecánica/302/rechaz/plugin oficial + >=4 result — pass (patrón /pago/resultado verificado con clase [/]: 4 matches; el grep plano falla solo por path-mangling de Git Bash)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Hallazgos extra: camino a REJECTED empírico (TSN), idempotencia del commit confirmada, timeout real cronometrado, y notas operativas (RUT con puntos, retornos duplicados, redirecciones con params de timeout tras error de banco)"
    verification:
      - kind: other
        ref: "03-SPIKE-RETORNO.md ## Hallazgos extra del spike (a)-(d) con órdenes SPK-* citadas por hallazgo"
        status: pass
    human_judgment: false

duration: 60 min
completed: 2026-09-30
status: complete
plan_head_before: abac4142e8d2cae50d31b2128a48ba10a51252bd
plan_head_after: 0445089f4adcf20bc177cb11c01d2788584221c3
---

# Phase 3 Plan 1: Spike de retorno de Webpay Summary

**Los 4 flujos del retorno de Webpay Plus corroborados contra el ambiente real de integración (3 runtime + 1 documentado), con corrección material del anulado (GET, no POST), la mecánica firmada (302 a /pago/resultado), REJECTED empírico vía TSN y el timeout cronometrado en 603 s**

## Performance

- **Duration:** 60 min
- **Started:** 2026-09-30T14:24:18Z
- **Completed:** 2026-09-30T15:26:00Z
- **Tasks:** 2
- **Files modified:** 1 (solo 03-SPIKE-RETORNO.md — el código del spike vive en maura-uat, D-17/D-38)

## Accomplishments

- **Blocker #1 de STATE.md resuelto con evidencia runtime, no supuestos**: el camino create → form POST → retorno → commit se probó real contra webpay3gint.transbank.cl con las credenciales públicas (597055555532), en el taller `D:/Repos/maura-uat/spike-retorno` (mini-backend FastAPI + transbank-sdk 6.1.0, navegador real Edge dirigido por CDP).
- **Los 3 flujos runtime corroborados con método+params+timing**: aprobado (GET token_ws solo; commit response_code=0/AUTHORIZED), anulado (GET con TBK_TOKEN+TBK_ID_SESION+TBK_ORDEN_COMPRA — corrección material: las docs decían POST en integración), timeout (GET con TBK_ID_SESION+TBK_ORDEN_COMPRA; 603 s cronometrados; además NO garantizado si el tab duerme).
- **La mecánica del retorno quedó firmada (D-41)**: 302 explícito del backend a la ruta única /pago/resultado — alimenta el contrato 0.3.0 (plan 03-02), el ADR-012 y las guías 09-11.
- **Las 3 Open Questions del research cerradas con datos**: Q1 (3 runtime + 1 documentado, A3), Q2 (REJECTED vía "Rechazar"/TSN del simulador: response_code=-1/FAILED; CVV errado NO rechaza), Q3 (603 s reales).
- **Hallazgos que las docs no decían**: idempotencia del commit confirmada runtime; retornos duplicados del navegador; params de timeout tras fallo del banco (22-78 s); Error 21 al re-entrar un form con el mismo token; RUT del simulador exige puntos.

## Task Commits

1. **Task 1: Spike runtime — mini-backend + 3 flujos corroborados** - `1acdc93` (docs)
2. **Task 2: Cierre del documento — 4° flujo, decisión de mecánica, hallazgos extra** - `0445089` (docs)

## Files Created/Modified

- `.planning/phases/03-checkout-webpay-y-rdenes/03-SPIKE-RETORNO.md` - Documento de hallazgos runtime (formato 02-UAT): evidencia por flujo, tabla de veredictos vs Pattern 3, decisión de mecánica D-41, hallazgos extra. Único artefacto commiteado del plan (código del spike desechable en maura-uat).

## Decisions Made

None nuevas fuera de las que el plan pedía firmar — ver `key-decisions` (la corrección GET del anulado, el 302, el TSN como camino a REJECTED, el timeout no garantizado y la idempotencia confirmada son decisiones/hallazgos con evidencia que los documentos de onda 2 citarán).

## Deviations from Plan

None - plan executed exactly as written. (La continuación sobre artefactos de una sesión interrumpida del spike y el ajuste del grep `/pago/resultado` por path-mangling de Git Bash se documentan en Issues Encountered; ninguna cambió el alcance.)

## Issues Encountered

- **Sesión interrumpida previa**: el taller maura-uat/spike-retorno ya contenía app.py (correcto según plan), venv con SDK 6.1.0 y 11 creates sin retornos — la sesión anterior murió peleando con la automatización del navegador. Se continuó sobre esa base (maura-uat es scratch, jamás se commitea): la receta final (native setter para forms Angular, tipeo por tecla para máscaras exp/cvv, RUT con puntos, select vci del simulador bancario) quedó descubierta y documentada en el taller.
- **grep "/pago/resultado" del verify del Task 2**: falla bajo Git Bash por path-mangling del patrón que inicia con `/` (lo convierte en ruta de Windows); verificado con la clase `[/]pago/resultado` → 4 matches. Artefacto de ambiente, no un gap del documento.

## Authentication Gates

None - las credenciales de integración de Transbank son públicas y viajan dentro del SDK (sin registro, sin secretos).

## User Setup Required

None - no external service configuration required (Webpay integración no requiere cuenta ni registro; aclaración que las guías de la fase replicarán al alumno).

## Next Phase Readiness

- **El planner de las ondas 2-4 tiene el insumo cerrado**: tabla de veredictos por flujo (4 filas con cita para ADR-012) + mecánica firmada (302 a /pago/resultado) + hallazgos extra en `03-SPIKE-RETORNO.md`.
- **PAY-01/PAY-02 de-riesgados**: el camino create → form POST → retorno → commit se probó real; el contrato 0.3.0 puede declarar GET+POST /api/pago/retorno con el 302 y los 4 params con evidencia.
- Blockers de STATE.md que este plan NO resuelve (siguen para onda 2): el ADR del momento de creación de la orden y del descuento de stock (D-34/D-35 ya decididos en CONTEXT; el ADR-013 los registrará).

## Self-Check: PASSED

- FOUND: .planning/phases/03-checkout-webpay-y-rdenes/03-SPIKE-RETORNO.md
- FOUND: .planning/phases/03-checkout-webpay-y-rdenes/03-01-SUMMARY.md
- FOUND: commit 1acdc93 (Task 1)
- FOUND: commit 0445089 (Task 2)
- Verify Task 1 (spike-flujos-ok): pass — re-ejecutado post-commit
- Verify Task 2 (spike-cierre-ok): pass — re-ejecutado post-commit (patrón /pago/resultado via clase [/]: 4 matches)

---
*Phase: 03-checkout-webpay-y-rdenes*
*Completed: 2026-09-30*
