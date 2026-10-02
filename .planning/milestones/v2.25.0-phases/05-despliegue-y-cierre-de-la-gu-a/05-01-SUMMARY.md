---
phase: 05-despliegue-y-cierre-de-la-gu-a
plan: 01
subsystem: infra
tags: [deploy, vercel, render, free-tier, adr, sqlite, seed-idempotente, return-url]

requires:
  - phase: 04-panel-de-administraci-n-y-asistente-ia
    provides: ADRs 001-018 con el molde de evidencia firmada (ADR-018), guías 1-15 con el triple de env vars ya parametrizado (BACKEND_URL/CORS_ORIGINS/VITE_API_URL) y la vara free-sin-tarjeta (D-63)
provides:
  - ADR-019: la decisión de plataforma (Vercel Hobby + Render Free) firmada con evidencia documental (D-69/D-73) y las reglas de configuración que las guías 16/17 enseñarán
  - ADR-020: la persistencia efímera (SQLite + seed idempotente al build) como estrategia explícita (D-70) con la lección en dos capas build-time/runtime
  - docs/07_despliegue.md: la fase 7 del ciclo como doc de decisión (formato demo-cine, D-71) con narrativa P1/return_url y el Siguiente → 08_mantenimiento.md
  - Índice de ADRs del README de arquitectura a 20 filas (molde 017/018)
affects: [05-02 (docs 06/08 citan doc 07 y su Siguiente), 05-03 (guías 16/17 enseñan lo que ADR-019 firma), 05-04 (guía 18 y su Gran verificación final contra ADR-019/020), 05-05 (cierre de tablas con conteo 20 ADRs)]

actuals:
  tokens: 8100          # chars/4 sobre el diff realizado (32.476 chars / 4)
  tasks: 2
  commits: 2            # MEDIDO: git rev-list --count 44e6cc5..HEAD
  plan_head_before: 44e6cc5eed5d0f3a8ad65d043fa8a212e42c09d9
  plan_head_after: 82611094de0f183f5d771a3bccac8b03cc48c7fb

tech-stack:
  added: []             # fase documental (D-17/D-73): cero paquetes; los "proveedores" nuevos son las plataformas Vercel/Render, verificadas contra docs oficiales
  patterns: [Evidencia documental D-73 (URL oficial + "a la fecha" + fecha de lectura, sin runtime propio — extensión de D-68 a las plataformas)]

key-files:
  created:
    - docs/04_arquitectura/adr/019-despliegue-free-tier-vercel-render.md
    - docs/04_arquitectura/adr/020-persistencia-efimera-seed-idempotente.md
    - docs/07_despliegue.md
  modified:
    - docs/04_arquitectura/README.md

key-decisions:
  - "ADR-019 firma D-69 con evidencia DOCUMENTAL (D-73, D-72 superseded): una plataforma por tier, PYTHON_VERSION=3.12.x fully-qualified (techo Transbank vs default 3.14.3), triple de env vars congelado por el código existente, SECRET_KEY nueva por entorno, TLS de plataforma"
  - "ADR-020 firma D-70 con las DOS capas del Pitfall 5 en bullets separados: build-time SIEMPRE revive (seed al Build Command) / runtime se pierde (historial de pedidos NO sobrevive un ciclo); PostgreSQL mencionado como camino de crecimiento, no implementado"
  - "doc 07 es doc de DECISIÓN (D-71): no re-pasa los pasos de las guías 16-18 (gate negativo sin comandos de build) — los referencia por nombre de archivo y narra el porqué (P1, return_url congelado, orden API-first D-15)"

patterns-established:
  - "Cifras de free tier siempre con URL de doc oficial y 'a la fecha' (D-68 extendida a plataformas — prohibición de cifras desnudas cumplida en ADR-019/020 y doc 07)"
  - "Negativas honestas heredadas del molde demo-cine ADR-007 (hibernación, /docs público, free tier no es producción seria; historial de pedidos perdido)"

requirements-completed: [DEPL-01]

coverage:
  - id: D1
    description: "ADR-019: despliegue free tier Vercel (SPA) + Render (API) firmado con evidencia documental y reglas de configuración (PYTHON_VERSION, triple de env vars, SECRET_KEY nueva)"
    requirement: DEPL-01
    verification:
      - kind: other
        ref: "grep gate del plan (adrs05-ok): ADR-019 con D-69/D-73/DEPL-01, PYTHON_VERSION 3.12, triple env vars, SECRET_KEY, 6 URLs oficiales + 'a la fecha', Opciones consideradas con 4 alternativas, Evidencia firmada, Negativas, ADR-012, hibernación, sin wording de runtime propio"
        status: pass
    human_judgment: false
  - id: D2
    description: "ADR-020: persistencia efímera SQLite + seed idempotente como estrategia (D-70) con las dos capas build-time/runtime y PostgreSQL mencionado no implementado"
    requirement: DEPL-01
    verification:
      - kind: other
        ref: "grep gate del plan (adrs05-ok): ADR-020 con D-70, seed idempotente, cita textual 'local SQLite databases' con URL, uv run python -m app.seed, capas runtime/build, PostgreSQL/Neon + DATABASE_URL, molde ADR-012 completo"
        status: pass
    human_judgment: false
  - id: D3
    description: "docs/07_despliegue.md: la fase 7 del ciclo como doc de decisión con formato demo-cine, Decisión de fondo ADR-019+020, narrativa P1/return_url, lección D-70, caveat puerto 8000 y Siguiente → 08_mantenimiento"
    verification:
      - kind: other
        ref: "grep gate del plan (doc07-ok): fase del ciclo 7, ADR-019/020 + Decisión de fondo, P1, return_url, guías 16-18 por nombre, 'local SQLite databases' con URL y 'a la fecha', puerto 8000, Errores típicos/Punto de control/aprendizajes, 08_mantenimiento, sin 'uv sync'"
        status: pass
    human_judgment: false
  - id: D4
    description: "Índice de ADRs del README de arquitectura a 20 filas (019/020 con molde exacto de 017/018)"
    verification:
      - kind: other
        ref: "grep gate del plan (doc07-ok): filas 019/020 presentes; grep -c '^| \\[0' == 20; ls docs/04_arquitectura/adr/0*.md | wc -l == 20; diff de precisión pre-commit = solo 2 filas nuevas"
        status: pass
    human_judgment: false

duration: 8 min
completed: 2026-10-01
status: complete
---

# Phase 5 Plan 1: ADRs 019/020 + doc 07_despliegue Summary

**ADR-019 firma Vercel Hobby + Render Free con evidencia documental (6 URLs oficiales + "a la fecha") y ADR-020 firma SQLite efímero + seed idempotente con la lección en dos capas; doc 07 convierte la decisión en fase del ciclo (narrativa P1/return_url) y el índice de ADRs llega a 20**

## Performance

- **Duration:** 8 min
- **Started:** 2026-10-01T17:54:04Z
- **Completed:** 2026-10-01T18:02:15Z
- **Tasks:** 2/2
- **Files modified:** 4 (3 creados, 1 editado)

## Accomplishments

- ADR-019 firma D-69 con evidencia documental (D-73, D-72 superseded declarado en Resuelve y Contexto): tabla de opciones con Netlify/Cloudflare/Fly.io/Railway/una-sola-plataforma descartadas, decisión numerada con las reglas que las guías 16/17 enseñan (PYTHON_VERSION=3.12.x fully-qualified, triple BACKEND_URL/CORS_ORIGINS/VITE_API_URL congelado por el código existente, SECRET_KEY nueva por entorno con el comando generador sin valor pegado, TLS de plataforma), negativas honestas (hibernación ~15 min/wake ~1 min, /docs público como trade-off declarado, free tier no es producción seria) y Evidencia firmada con 6 URLs oficiales + fecha de lectura 2026-10-01 + link relativo a 05-RESEARCH.md
- ADR-020 firma D-70 con el esqueleto de ADR-012: seed al Build Command (`uv sync --locked && uv run python -m app.seed`), upsert que converge (D-05/D-06/D-07 — re-ejecutar el deploy es seguro), las DOS capas del Pitfall 5 en bullets separados (build-time SIEMPRE revive / runtime se pierde), negativa honesta central nombrando el historial de pedidos como lo que NO sobrevive, PostgreSQL (Neon + cambio de DATABASE_URL) mencionado como camino de crecimiento
- docs/07_despliegue.md como doc de DECISIÓN (D-71): cabecera de la serie demo-carro con "Decisión de fondo" anclando ADR-019+020 con links relativos, narrativa P1 ("que se abra desde cualquier dispositivo" — primera petición de Maura, última en cumplirse), por qué la fase va al final (congela el return_url), tabla de 8 términos, lección D-70 en dos capas con la cita textual "local SQLite databases" (URL + "a la fecha"), cold start honesto en prosa (sin UI nueva), caveat "puerto 8000" con su regla de decisión, referencia por nombre a las guías 16-18 y doc 06, errores típicos con los Pitfalls 1/3/4/7/9, y Siguiente → 08_mantenimiento.md
- README de arquitectura: filas 019/020 agregadas con el molde exacto de 017/018 — el índice llega a 20 filas (diff de precisión verificado: solo 2 filas nuevas)

## Task Commits

Each task was committed atomically:

1. **Task 1 (tracer): ADR-019 + ADR-020 con evidencia documental** - `273e268` (docs)
2. **Task 2: docs/07_despliegue.md + índice de ADRs a 20** - `8261109` (docs)

**Plan metadata:** (ver commit final de este plan)

## Files Created/Modified

- `docs/04_arquitectura/adr/019-despliegue-free-tier-vercel-render.md` - ADR de despliegue free tier Vercel+Render (D-69/D-73) con Evidencia firmada
- `docs/04_arquitectura/adr/020-persistencia-efimera-seed-idempotente.md` - ADR de persistencia efímera + seed idempotente (D-70) con las dos capas del Pitfall 5
- `docs/07_despliegue.md` - Fase 7 del ciclo: la decisión de despliegue como doc (formato demo-cine, D-71)
- `docs/04_arquitectura/README.md` - Índice de ADRs a 20 filas (solo el índice: 2 filas nuevas)

## Decisions Made

- ADR-019 declara D-72 superseded por D-73 en Resuelve Y en Contexto (la corroboración es documental: docs oficiales citadas con URL y fecha de lectura, sin spike runtime — el runtime lo corre el alumno con las guías 16-18)
- Los nombres de env vars se toman EXACTOS del código existente (Pattern 1 del research): BACKEND_URL/CORS_ORIGINS/VITE_API_URL/PYTHON_VERSION — no se inventó ninguno
- doc 07 usa la cabecera de la serie demo-carro (línea "Guía: Demo Carro — …"), no la de "Módulos ISI601/ISI602" de demo-cine, y su tabla de errores típicos cubre exactamente los Pitfalls 1/3/4/7/9 del research
- La fila 019 del índice cita (DEPL-01, D-69, D-73) y la 020 (DEPL-01/DEPL-02, D-70), con link relativo al ADR — mismo molde de 017/018

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Los gates grep del propio plan atraparon 2 problemas de formato durante la redacción (antes del commit, sin impacto): la cita textual "local SQLite databases" quedó partida en dos líneas en ADR-020 (el grep opera por línea) y el bold de la cabecera de doc 07 partía "Fase del ciclo de vida: 7". Ambos corregidos en el mismo ciclo de autoría; los gates `adrs05-ok` y `doc07-ok` pasaron tras el fix.

## User Setup Required

None - no external service configuration required. (D-73: las cuentas de Vercel/Render las crea el ALUMNO en las guías 16/17 — este plan no ejecuta runtime.)

## Next Phase Readiness

- Los links de doc 07 a `guia-16/17/18`, `06_pruebas.md` y `08_mantenimiento.md` son forward references BY DESIGN: los escriben los planes 05-02 (docs 06/08), 05-03 (guías 16/17) y 05-04 (guía 18) — el Siguiente de doc 06 (05-02) apunta de vuelta a este doc 07
- El contrato_api.yaml quedó INTACTO (verificado: diff vacío contra 44e6cc5) — la fila contrato ↔ /docs de guia-18 seguirá contra 0.4.0 (D-66)
- La cadena D-15 honrada: la decisión (ADRs) quedó firmada antes que doc 07 y antes que las guías — 05-02/03/04 ya pueden citar ADR-019/020 como fuente de verdad
- Sin blockers ni concerns nuevos para los planes restantes de la fase

## Self-Check: PASSED

Todos los archivos creados existen en disco; ambos commits de task (273e268, 8261109) presentes; commits medidos contra el ledger (44e6cc5..HEAD = 2); gates de verificación del plan re-ejecutados y en verde (adrs05-ok, doc07-ok); contrato_api.yaml sin cambios.

---
*Phase: 05-despliegue-y-cierre-de-la-gu-a*
*Completed: 2026-10-01*
