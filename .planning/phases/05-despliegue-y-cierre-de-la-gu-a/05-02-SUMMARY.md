---
phase: 05-despliegue-y-cierre-de-la-gu-a
plan: 02
subsystem: docs
tags: [pruebas, metodologia, mantenimiento, ciclo-de-vida, gran-verificacion-final, diferidos-v2, postgresql, supersede]

requires:
  - phase: 05-despliegue-y-cierre-de-la-gu-a
    provides: docs/07_despliegue.md (el doc hermano que el Siguiente de 06 enlaza) y ADRs 019/020 que doc 08 cita como camino de crecimiento
provides:
  - docs/06_pruebas.md: la fase 6 del ciclo como SÍNTESIS del método ya vivido (D-71) — tres capas nombradas y defendidas con ejemplos reales de las fases 1-4, sin suite nueva
  - docs/08_mantenimiento.md: la fase 8 del ciclo como cierre prospectivo — diferidos v2 con hilo hacia atrás por ID, PostgreSQL como crecimiento mencionado, el swap ADR-017→018 como caso real
  - La cadena 06 → 07 → 08 del ciclo cerrada: Siguiente de 06 → 07_despliegue.md, cierre de 08 → índice docs/README.md
affects: [05-05 (las tablas de estado de los READMEs cierran las filas 6 y 8 citando estos docs), 05-03/05-04 (las guías 16-18 citan el método que doc 06 nombra)]

actuals:
  tokens: 6300          # chars/4 sobre el diff realizado (25.234 chars / 4)
  tasks: 2
  commits: 2            # MEDIDO: git rev-list --count 89c0a91..cc6aead
  plan_head_before: 89c0a91b9cb432fddeb0e6fef0444c3ed6d037a9
  plan_head_after: cc6aead19a69aa1279a03214f42022998de775b9

tech-stack:
  added: []             # fase documental (D-17/D-73): cero paquetes, cero runtime
  patterns: [Tabla método ↔ defensa "| Verificación de la serie | Origen | Qué defiende |" (adaptación propia del molde demo-cine "Regla/flujo"), tabla hilo hacia atrás "| Fase | Documento a tocar | El cambio |" reutilizada para TODO el mapa v2]

key-files:
  created:
    - docs/06_pruebas.md
    - docs/08_mantenimiento.md
  modified: []

key-decisions:
  - "docs/06 declara la divergencia con demo-cine en prosa SIN nombrar la herramienta vetada (el gate negativo del plan veta la palabra misma): 'demo-cine construyó una suite de pruebas automáticas; esta serie defendió cada pieza en el momento en que nació' — la divergencia queda dicha, la suite no se enseña"
  - "La tabla método ↔ defensa tiene 4 filas, no 3: la instancia final (Gran verificación de fase 5 contra el ambiente desplegado, guia-18, D-73 'la corres TÚ') es fila propia — el método queda completo de punta a punta como exige el must_have"
  - "doc 08 cubre los 8 diferidos v2 reales (no solo los 3 nombrados por el plan): PAY-05 como ejemplo trabajado con la tabla completa de 5 fases + STORE-05/ORDR-03/ADMN-05/STAKE-01..04 en tabla compacta con su primera puerta — 'sin omitir los reales' del acceptance criterion"
  - "El caso Gemini→Groq se cita con la mecánica supersede completa (402 real → ADR-017 Superseded por ADR-018 2026-10-01 → recién después la reescritura) y con la lección D-15 aplicada al mantenimiento: firmar antes de reescribir"

patterns-established:
  - "Docs de cierre del ciclo con divergencias declaradas en el propio doc (no en silencio): el formato se hereda de demo-cine, el contenido diverge y lo dice"
  - "Hilo hacia atrás como tabla reutilizable para cualquier diferido futuro: cada ítem de REQUIREMENTS v2 tiene su 'primera puerta' y lo que el ciclo exigirá"

requirements-completed: [GUIDE-01]  # parcial documental de este plan (must_haves): filas 6 y 8 del ciclo cubiertas; el shared-ID gate mantiene GUIDE-01 Pending en REQUIREMENTS.md hasta que 05-04/05-05 (cosignatarios) terminen — ready-ids devolvió 0/1

coverage:
  - id: D1
    description: "docs/06_pruebas.md: síntesis del método de pruebas de la serie (mini-verificación / Gran verificación final / verificación runtime) con ejemplos reales citados, divergencia con demo-cine declarada, caso GET-vs-POST del spike como argumento, y Siguiente → 07_despliegue.md"
    requirement: GUIDE-01
    verification:
      - kind: other
        ref: "grep gate del plan (doc06-ok, GNU grep): fase del ciclo 6, tres capas, columna Qué defiende, Authorize, GROQ_API_KEY/grep del build, 4 flujos, guia-18/ambiente desplegado, GET vs POST, secciones de cierre, 07_despliegue; NEGATIVOS en verde (cero suite: sin la herramienta vetada, sin tests)"
        status: pass
    human_judgment: false
  - id: D2
    description: "docs/08_mantenimiento.md: cierre prospectivo con los 8 diferidos v2 por ID (PAY-05 worked example + tabla compacta), swap ADR-017→018 con supersede y fecha, PostgreSQL/DATABASE_URL/psycopg como crecimiento mencionado (D-70/ADR-020), vetados explícitos, 'El ciclo se cierra (y se reabre)' con pregunta final y enlace al índice"
    requirement: GUIDE-01
    verification:
      - kind: other
        ref: "grep gate del plan (doc08-ok, GNU grep): fase del ciclo 8, PAY-05/ADMN-05/STAKE, PostgreSQL+DATABASE_URL+psycopg, ADR-018/ADR-017, 'a la fecha', Documento a tocar, El ciclo se cierra, secciones de cierre, README.md; NEGATIVO en verde (sin 'implementaremos/migramos a PostgreSQL'); verificación extra: los 8 IDs existen en REQUIREMENTS v2 y la pregunta final termina en '?'"
        status: pass
    human_judgment: false

duration: 9 min
completed: 2026-10-01
status: complete
---

# Phase 5 Plan 2: docs/06_pruebas.md + docs/08_mantenimiento.md Summary

**docs/06 nombra como método lo que el alumno ya vivió (tres capas defendidas con ejemplos reales de las fases 1-4, divergencia con demo-cine declarada) y docs/08 cierra el ciclo prospectivamente (los 8 diferidos v2 con hilo hacia atrás, PostgreSQL como crecimiento, el swap ADR-017→018 como caso real de mantenimiento) — la cadena 06 → 07 → 08 queda enlazada**

## Performance

- **Duration:** 9 min
- **Started:** 2026-10-01T18:05:36Z
- **Completed:** 2026-10-01T18:14:21Z
- **Tasks:** 2/2
- **Files modified:** 2 (2 creados, 0 editados)

## Accomplishments

- docs/06_pruebas.md (165 líneas): la fase 6 del ciclo como síntesis — no como suite. La tabla central "| Verificación de la serie | Origen | Qué defiende |" con las tres capas (mini-verificación por paso desde guia-01; Gran verificación final por fase desde guia-04/ADR-007 con la fila contrato ↔ /docs y Authorize; verificación runtime fases 3-4 con los 4 flujos, la asesora con key real y el grep del build AIAS-03) MÁS la instancia final contra el ambiente desplegado que guia-18 define ("la corres TÚ, en tus cuentas", D-73). Divergencia con el hermano mayor declarada en prosa sin enseñar la suite vetada; el caso doc-vs-runtime del spike (POST dicho, GET observado, ADR-012) como argumento contra mocks; errores típicos del propio método; Siguiente → 07_despliegue.md
- docs/08_mantenimiento.md (199 líneas): cierre prospectivo del ciclo. El hilo hacia atrás con la tabla "| Fase | Documento a tocar | El cambio |" para PAY-05 (worked example, 5 fases) y tabla compacta para STORE-05/ORDR-03/ADMN-05/STAKE-01..04 — los 8 diferidos reales de REQUIREMENTS v2, cada uno con su primera puerta. El swap Gemini→Groq (402 real de Google, ADR-017 Superseded por ADR-018, 2026-10-01) como el caso REAL de mantenimiento adaptativo con la lección firmar-antes-de-reescribir (D-15 aplicado al mantenimiento). PostgreSQL (Neon + psycopg, cambio de DATABASE_URL) como crecimiento mencionado (D-70/ADR-020), lo vetado sigue vetado (Stripe, pagos reales). "El ciclo se cierra (y se reabre)" con el mapa de puertas abiertas, la pregunta para llevar a casa y el enlace final al índice docs/README.md
- La cadena 06 → 07 → 08 del ciclo existe y quedó verificada: Siguiente de 06 → 07_despliegue.md (el doc del 05-01), Siguiente de 07 → 08_mantenimiento.md (ya escrito), cierre de 08 → índice

## Task Commits

Each task was committed atomically:

1. **Task 1: docs/06_pruebas.md — el método de la serie nombrado como método (síntesis, D-71)** - `924be50` (docs)
2. **Task 2: docs/08_mantenimiento.md — cierre prospectivo (diferidos v2, PostgreSQL, guía viva)** - `cc6aead` (docs)

**Plan metadata:** (ver commit final de este plan)

## Files Created/Modified

- `docs/06_pruebas.md` - Fase 6 del ciclo: el método de pruebas de la serie nombrado y defendido (D-71 — síntesis, no suite)
- `docs/08_mantenimiento.md` - Fase 8 del ciclo: cierre prospectivo con los diferidos v2, PostgreSQL como crecimiento y la guía viva

## Decisions Made

- La divergencia con demo-cine 06 se declara en prosa SIN la palabra vetada: el gate negativo del plan (`! grep "pytest"`) veta el término mismo — la divergencia se dice ("demo-cine construyó una suite de pruebas automáticas que corre sola"), la herramienta no se nombra ni se enseña
- La tabla método ↔ defensa tiene 4 filas: la instancia final (fase 5 contra el ambiente desplegado, guia-18, D-73) merece fila propia — cierra el método de punta a punta como exige el must_have
- doc 08 cubre los 8 diferidos v2 (el plan exigía "al menos" PAY-05/ADMN-05/STAKE-*): el acceptance criterion "sin omitir los reales" se tomó literal — STORE-05 y ORDR-03 también entran al mapa con su primera puerta
- Los ejemplos de doc 06 salen de verificaciones REALES del corpus (doce `[=]` del seed guia-03, 422 de `?familia=vinagre` guia-04, fila 11 contrato ↔ /docs, fila 13 grep del build guia-15, 403 vs 200 con Authorize) — ninguna fila con Origen genérico (mitigación T-05-05)
- Cero datos del taller en los ejemplos (T-05-06): solo nombres de variables y placeholders de las guías, sin emails ni keys literales

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- El `grep` del PATH es ugrep 7.8.4 en este entorno, y ugrep interpreta un PATRÓN que parte con `/` (como `/docs` en el gate del plan) como file-pattern, no como búsqueda de texto — el gate fallaba aunque el contenido estaba. Resuelto ejecutando los gates verbatim con GNU grep (`/usr/bin/grep`, presente en el sistema): ambos gates pasaron sin cambios de contenido. Nota para los ejecutores siguientes (05-03..05-05): sus gates con patrones `/`-inicial necesitan `/usr/bin/grep` o la forma `[/]docs`

## User Setup Required

None - no external service configuration required. (D-73: fase de solo escritura, sin runtime.)

## Next Phase Readiness

- Los links de doc 06 a guia-16/17/18 y docs/07/08 son forward/backward references BY DESIGN: las guías las escriben 05-03/05-04 y doc 07 ya existe (05-01) — la cadena del ciclo queda continua
- Las filas 6 y 8 de las tablas de estado de los tres READMEs las cierra el plan 05-05 (quinta corrida D-13/D-18): los docs existen, los índices todavía dicen ⏳ Pendiente por diseño
- GUIDE-01 sigue Pending en REQUIREMENTS.md por el shared-ID gate (05-04 y 05-05 también lo declaran y no tienen SUMMARY): se marca Complete cuando el último cosignatario termine — `requirements.ready-ids` devolvió 0/1
- Sin blockers ni concerns nuevos

## Self-Check: PASSED

Ambos archivos creados existen en disco (`docs/06_pruebas.md` 165 líneas, `docs/08_mantenimiento.md` 199 líneas); los commits 924be50 y cc6aead están en el log; commits medidos contra el ledger (89c0a91..HEAD = 2); gates del plan re-ejecutados en verde (doc06-ok, doc08-ok con GNU grep); cadena 06 → 07 → 08 verificada; prohibiciones (suite vetada, afirmación de migración PostgreSQL) en verde.

---
*Phase: 05-despliegue-y-cierre-de-la-gu-a*
*Completed: 2026-10-01*
