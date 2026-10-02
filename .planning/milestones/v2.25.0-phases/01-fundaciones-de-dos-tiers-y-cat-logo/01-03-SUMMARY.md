---
phase: 01-fundaciones-de-dos-tiers-y-cat-logo
plan: 01-03
subsystem: docs
tags: [readme, arquitectura, adr, guia-educativa, guide-only]

requires:
  - "docs/README.md con tabla de 8 fases (01-02)"
  - "docs/04_arquitectura/contrato_api.yaml (01-01)"
provides:
  - "README.md raiz: portada del proyecto educativo con tabla de fases y estado (D-18)"
  - "Documento de arquitectura en una pagina (dos tiers + capas) con stack versionado citando ADRs"
  - "8 ADRs fundacionales 001-008 con formato demo-cine (capas, dos tiers, monorepo, TypeScript, SQLite+create_all, uv, API-first, guide-only)"
  - "Reglas de dependencia numeradas del backend/frontend que las guias citan"
  - "Invariant guide-only registrado como decision de arquitectura (ADR-008, D-17/D-18)"
affects: [01-04, 01-05, fase-2, fase-3, fase-4, fase-5]

actuals:
  tokens: 13477
  tasks: 3
  commits: 3
  plan_head_before: 4d99b49400332694e6ae4af234bcbac10531cd7e
  plan_head_after: d188c28b660a92e13fba37f35d9cca36e12d5e44

tech-stack:
  added: []
  patterns:
    - "Formato ADR fijo demo-cine (Estado/Fecha/Resuelve + Contexto + Opciones A/B/C + Decisión con regla + Consecuencias positivas/negativas + 3 preguntas)"
    - "Numeración ADR-001..008 fija; ADR-008 = guide-only (D-17/D-18)"
    - "Tabla de estado del README raíz que avanza por fase GSD (D-18)"
    - "Cita cruzada docs↔ADRs por ID canónico (RF/RN/HU/P/C/CS y D-xx de CONTEXT)"

key-files:
  created:
    - README.md
    - docs/04_arquitectura/README.md
    - docs/04_arquitectura/adr/001-arquitectura-en-capas.md
    - docs/04_arquitectura/adr/002-dos-tiers-spa-y-api.md
    - docs/04_arquitectura/adr/003-monorepo.md
    - docs/04_arquitectura/adr/004-frontend-typescript.md
    - docs/04_arquitectura/adr/005-sqlite-y-create-all.md
    - docs/04_arquitectura/adr/006-uv-como-gestor.md
    - docs/04_arquitectura/adr/007-api-first.md
    - docs/04_arquitectura/adr/008-repositorio-solo-guias.md
  modified:
    - docs/README.md

key-decisions:
  - "Sección Contexto sin numerar en el README de arquitectura (insumo 03_diseno + advertencia D-17) y secciones numeradas 1-7"
  - "ADR-002 documenta el contraste pedagógico explícito con el ADR-006 de demo-cine (misma decisión, contexto opuesto)"
  - "Fechas de ADR llenadas con la fecha real de fase 1 (2026-09-28); tabla de aprobación queda con firmas en blanco como el análogo"
  - "Jinja2 aparece solo como opción descartada en ADR-002 y MySQL como opción vetada en ADR-005 (prohibición del plan cumplida)"

requirements-completed: [GUIDE-02]

coverage:
  - id: D1
    description: "README.md raíz: portada del proyecto educativo con tabla de 8 fases, estado real y frase clave D-18"
    requirement: GUIDE-02
    verification:
      - kind: other
        ref: "grep Maura/Body Splash/docs README.md/docs/05_desarrollo/narrado/🚧/⏳ + filas ^| 1 |..^| 8 | + sin stripe → readme-raiz-ok"
        status: pass
    human_judgment: false
  - id: D2
    description: "docs/04_arquitectura/README.md: arquitectura en una página dos tiers con diagrama, 3 preguntas, regla de oro, diseño→arquitectura, stack citando ADRs, árbol del alumno con 6 reglas de dependencia, índice de 8 ADRs, flujo API-first y aprobación"
    requirement: GUIDE-02
    verification:
      - kind: other
        ref: "grep ## Contexto/ADR-001/ADR-008/lib/api.ts/alumno/FastAPI/React/sqlite en el README → arch-adrs-1-4-ok"
        status: pass
    human_judgment: false
  - id: D3
    description: "ADR-002 dos tiers estrictos con tradeoffs honestos (SEO client-side, CORS) y contraste pedagógico con demo-cine"
    requirement: GUIDE-02
    verification:
      - kind: other
        ref: "grep secciones fijas + SEO client-side en consecuencias negativas (Task 2 verify)"
        status: pass
    human_judgment: false
  - id: D4
    description: "ADRs 001-004 con formato demo-cine completo (Contexto/Opciones 3/Decisión/Consecuencias/Para conversar en clase)"
    requirement: GUIDE-02
    verification:
      - kind: other
        ref: "for f in adr/001..004: grep '## Opciones consideradas' && '## Decisión' && '## Consecuencias' && 'Para conversar en clase' (Task 2 verify)"
        status: pass
    human_judgment: false
  - id: D5
    description: "ADR-005 create_all + seed idempotente con advertencia honesta y entrada diferida de Alembic; ADR-006 uv con vcs none y techo 3.12"
    requirement: GUIDE-02
    verification:
      - kind: other
        ref: "grep create_all/Alembic (005) y 'vcs none'/3.12 (006) (Task 3 verify → adr-5-8-ok)"
        status: pass
    human_judgment: false
  - id: D6
    description: "ADR-007 ancla contrato_api.yaml como fuente de la verdad con mecanismo de cierre /docs ≈ contrato; ADR-008 registra D-17/D-18 como decisión guide-only con 3 opciones y consecuencias honestas (sin CI)"
    requirement: GUIDE-02
    verification:
      - kind: other
        ref: "grep contrato_api.yaml (007) y guide-only/CI (008) (Task 3 verify → adr-5-8-ok)"
        status: pass
    human_judgment: false
  - id: D7
    description: "Coherencia del índice: docs/README.md fila 4 dice 8 ADRs y ya no dice 7"
    requirement: GUIDE-02
    verification:
      - kind: other
        ref: "grep '8 ADRs' docs/README.md && ! grep '7 ADRs' docs/README.md (Task 3 verify)"
        status: pass
    human_judgment: false
  - id: D8
    description: "Invariant guide-only del plan: cero código de aplicación commiteado; cero secretos; librerías vetadas solo como opción descartada"
    requirement: GUIDE-02
    verification:
      - kind: other
        ref: "git diff --name-only 4d99b49..HEAD (solo README.md + docs/**) + grep de secretos y vetadas → limpio"
        status: pass
    human_judgment: false

duration: 11min
completed: 2026-09-28
status: complete
---

# Phase 01 Plan 01-03: README raíz + arquitectura en una página + 8 ADRs fundacionales Summary

**Portada del producto educativo (D-18) + documento de arquitectura dos tiers con stack versionado + los 8 ADRs que fijan las convenciones documentales del ciclo (incluido el invariant guide-only D-17 como ADR-008).**

## Performance

- 3/3 tareas completadas, 3 commits de producción, 10 archivos creados + 1 modificado (todos documentos — invariant guide-only intacto).
- 3 verificaciones automáticas del plan (`readme-raiz-ok`, `arch-adrs-1-4-ok`, `adr-5-8-ok`) en verde a la primera; cero reparaciones necesarias.
- Métricas medidas del ledger: 3 commits, 13.477 tokens (chars/4 del diff real) frente a estimación de 30.000.

## Accomplishments

- **README.md raíz (D-18):** portada estilo demo-cine con emoji 🧴, las 6 secciones del análogo (proyecto educativo, La aplicación, El enfoque con tabla de 8 fases, Qué hace especial, Stack, Uso en clases + nota de ficción), estado real del ciclo (1-4 ✅, 5 🚧 Parcial, 6-8 ⏳) y la frase clave "El código completo del proyecto vive narrado en las guías" declarando el invariant D-17.
- **Documento de arquitectura en una página:** diagrama ASCII de los dos tiers (SPA React → proxy /api dev → API FastAPI en capas → SQLite, fotos servidas por el host del SPA), tabla de 3 preguntas, regla de oro (JSON sí, plantillas jamás), pregunta inevitable del jurado (remite al ADR-002), tabla diseño→arquitectura elemento a elemento (PRODUCTO→models, D1→repositories, A1→public/products, procesos 1.0-4.0, pantallas 1-3), stack con versiones autoritativas citando ADR por número, árbol del monorepo **declarado explícitamente como el proyecto del alumno (D-17)** con 6 reglas de dependencia numeradas, índice de los 8 ADRs, flujo API-first y aprobación.
- **ADRs 001-008** con el formato fijo del análogo (metadatos Estado/Fecha/Resuelve + Contexto + tabla de 3 opciones + Decisión con regla explícita + Consecuencias positivas/negativas honestas + 3 preguntas):
  - 001 capas (adaptado: el consumidor es la SPA; conexión solo por Depends; routers jamás importan SQLAlchemy)
  - 002 dos tiers estrictos (SEO client-side, CORS y dos proyectos como costos honestos; contraste explícito con el ADR-006 de demo-cine)
  - 003 monorepo del alumno (D-11/D-17; dos proyectos independientes, sin tooling pesado)
  - 004 TypeScript con espejo manual (D-09; el espejo ES el ejercicio; codegen descartado)
  - 005 SQLite + create_all + seed idempotente (advertencia de que create_all no altera tablas; Alembic diferido; crecimiento por URL)
  - 006 uv (requires-python ">=3.12,<3.13" por transbank-sdk fase 3; --vcs none contra el repo anidado)
  - 007 API-first (contrato_api.yaml ya aprobado en 01-01 como fuente de la verdad; cierre /docs ≈ contrato que ejecuta guia-04)
  - 008 repositorio solo guías guide-only (D-17/D-18: tres opciones, regla de jamás commitear app, consecuencias honestas sin CI)
- **Coherencia del índice:** docs/README.md fila 4 actualizada de "7 ADRs" a "8 ADRs".

## Task Commits

| Task | Commit | Archivos |
|---|---|---|
| 1. README.md raíz — portada (D-18) | 47a0c89 | README.md |
| 2. Arquitectura en una página + ADRs 001-004 | fb40597 | docs/04_arquitectura/README.md, adr/001..004 |
| 3. ADRs 005-008 + coherencia docs/README.md | d188c28 | adr/005..008, docs/README.md |

## Files Created-Modified

**Creados (10):** `README.md`, `docs/04_arquitectura/README.md`, `docs/04_arquitectura/adr/001-arquitectura-en-capas.md`, `002-dos-tiers-spa-y-api.md`, `003-monorepo.md`, `004-frontend-typescript.md`, `005-sqlite-y-create-all.md`, `006-uv-como-gestor.md`, `007-api-first.md`, `008-repositorio-solo-guias.md`.

**Modificados (1):** `docs/README.md` (fila 4 del índice: 7 → 8 ADRs).

## Decisions Made

- Contexto sin numerar + secciones 1-7 en el README de arquitectura (ver desviación 1); la sección "## Contexto" quedó como preámbulo con el insumo (03_diseno) y la advertencia D-17.
- Fechas de ADR = 2026-09-28 (fecha real de fase 1); la tabla de aprobación queda con firmas en blanco, como el análogo.
- El README raíz NO nombra pasarelas ni librerías descartadas (verifica `! grep -qi stripe`): esa discusión vive en los ADRs como opción descartada (Jinja2 en 002, MySQL vetado en 005).
- Links del README raíz solo a rutas que existen o existirán al cierre de la fase (05_desarrollo/ llega en 01-04); fases 6-8 en `código` plano hasta que existan.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Bloqueo menor] Numeración de secciones del README de arquitectura**
- **Found during:** Task 2
- **Issue:** El `<action>` del plan numera las secciones §1, §2, §3, §4, §6, §7, §8 — salta la §5 (resabio de la sección SOLID del análogo demo-cine, que este documento no tiene). Numerar con hueco produce un documento confuso.
- **Fix:** Secciones renumeradas en secuencia 1-7 (índice de ADRs = §5, API-first = §6, aprobación = §7). Además, el verify del Task 2 exige `## Contexto` también en el README de arquitectura (el loop del plan lo incluye), resuelto con un preámbulo "## Contexto" sin numerar.
- **Files modified:** docs/04_arquitectura/README.md
- **Commit:** fb40597

**2. [Nota menor, sin cambio de comportamiento] Fechas de ADR**
- **Found during:** Task 2
- **Issue:** El formato del plan mostraba "Fecha: 2026-09-__" como placeholder.
- **Fix:** Se llenó con la fecha real de la fase 1 (2026-09-28), igual que el análogo y que los docs 01-03 ya commiteados; las firmas de aprobación quedan en blanco como en demo-cine.
- **Commit:** fb40597

## Issues Encountered

None — las tres verificaciones automáticas pasaron a la primera; no hubo puertas de autenticación ni checkpoints.

## User Setup Required

None.

## Next Phase Readiness

- Las guías de 01-04/01-05 heredan: numeración ADR fija, 6 reglas de dependencia citables, mecanismo de cierre /docs ≈ contrato (guia-04 lo ejecuta) y el invariant D-17 para redactar bloques de código sin commitear aplicación.
- El README raíz queda como portada viva: las fases 2-5 actualizan su tabla de estado (fila 5 pasa a ✅ cuando 01-04/01-05 completen las guías 1-4).
- REQUIREMENTS: GUIDE-02 queda cubierto en su parte de fase 1 (arquitectura + ADRs + contrato anclado); el cierre por fase del requisito lo registra el roadmap.

## Self-Check: PASSED

- Archivos verificados en disco: los 10 creados existen (README.md, docs/04_arquitectura/README.md, 8 ADRs) y docs/README.md modificado.
- Commits verificados en `git log`: 47a0c89, fb40597, d188c28 presentes en master.
