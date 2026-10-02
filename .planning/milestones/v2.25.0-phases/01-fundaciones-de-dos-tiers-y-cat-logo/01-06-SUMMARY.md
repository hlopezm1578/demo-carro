---
phase: 01-fundaciones-de-dos-tiers-y-cat-logo
plan: 06
subsystem: docs
tags: [guia-educativa, gap-closure, uat, fastapi, uv, gitignore, openapi, responses]

# Dependency graph
requires:
  - phase: 01-fundaciones-de-dos-tiers-y-cat-logo
    provides: "Guias 1-4 escritas (planes 01-04/01-05) y gaps G-01-1/G-01-4 diagnosticados por el UAT (01-UAT.md, status diagnosed)"
provides:
  - "Cierre del gap G-01-1: guia-01 Paso 1 enumera solo los 4 archivos que uv genera de verdad y Paso 5 instruye CREAR backend/.gitignore con el contenido entregado"
  - "Cierre del gap G-01-4: guia-04 implementa el tercer schema del contrato (Error) y declara la respuesta 404 en el decorator del router para que /docs la documente"
affects: [verify-work (re-verificacion de tests 1 y 4 del UAT), fase 2 (guias heredan la convencion responses declarativos)]

# Actuals (#2632) — mismo escala que el estimate del plan (estimateTokens = chars/4)
actuals:
  tokens: 1667
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "responses={404: {...}} declarativo en el decorator: FastAPI no documenta en OpenAPI los raise HTTPException de runtime; declararlos en la firma es lo que los sube a /docs"

key-files:
  created: []
  modified:
    - docs/05_desarrollo/guia-01-proyecto-backend.md
    - docs/05_desarrollo/guia-04-catalogo.md

key-decisions:
  - "G-01-4 cerrado por Opcion A (declarar el 404 en la firma del router) y no por Opcion B (nota que normaliza el desvio): la fila 11 existe para detectar drift — cuatro lineas declarativas ensenan un concepto real de FastAPI y cierran el eje 404 por la razon correcta"
  - "Direccion del fix: guia -> contrato, nunca al reves. contrato_api.yaml queda intacto y WR-01/WR-02 siguen abiertos en 01-REVIEW-DISPOSITION.md; prohibido declarar el 422 de validacion en responses"
  - "El bloque de contenido del .gitignore de guia-01 queda byte-identico: el gap era QUIEN crea el archivo, no su contenido; las dos menciones de guia-03 quedan validas sin editarla"

patterns-established:
  - "Respuestas de error documentadas por declaracion: el schema Error del contrato vive junto a los schemas de exito y el decorator declara cada respuesta no-automatizada con su description palabra por palabra del contrato"

requirements-completed: [GUIDE-02, GUIDE-03]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "guia-01 corregida (G-01-1): Paso 1 sin .gitignore en la enumeracion + nota que anticipa la creacion manual; Paso 5 instruye CREAR backend/.gitignore con el contenido entregado y su mini-verificacion valida el archivo recien creado"
    requirement: GUIDE-03
    verification:
      - kind: other
        ref: "gate automatizado Task 1 (greps de contenido: crea el archivo **`backend/.gitignore`** / escribe junto al VCS / uv solo lo genera cuando inicializa el VCS / que acabas de crear; bloque .gitignore en unica ocurrencia exacta; ast.parse de los 5 bloques python)"
        status: pass
    human_judgment: false
  - id: D2
    description: "guia-04 corregida (G-01-4): schema Error en Paso 1, responses={404} con description y model Error palabra por palabra del contrato en el router del Paso 3, prosa docente sobre excepciones de runtime e item 5 de la mini-verificacion"
    requirement: GUIDE-02
    verification:
      - kind: other
        ref: "gate automatizado Task 2 (git diff --quiet HEAD sobre contrato_api.yaml; greps: class Error(BaseModel): / \"model\": Error / Producto inexistente (o inactivo) / esquema `Error`; conteo responses={ == 1; ausencia de 422: {; ast.parse de los 6 bloques python)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Cierre por re-ejecucion: tests 1 y 4 del UAT re-ejecutados en el taller confirmando que ls backend/ no muestra .gitignore tras uv init --vcs none y que /docs documenta 200/404/422 para /api/productos/{producto_id}"
    requirement: GUIDE-02
    verification: []
    human_judgment: true
    rationale: "La re-ejecucion de las guias en una maquina limpia (uv 0.9.x, Node >= 22.22) vive en el taller UAT (D:/Repos/maura-uat) y el plan la asigna explicitamente a /gsd-verify-work (verificacion item 2); ningun test local puede sustituirla"

# Metrics
duration: 4min
completed: 2026-09-29
status: complete
commits: 2
plan_head_before: b4a8f04219890dcb72a693a859f5ecc890194ef6
plan_head_after: 7d8ca85aa4269d87347f1e89eb18d15aff704459
---

# Phase 01 Plan 06: Cierre de gaps del UAT (G-01-1, G-01-4) Summary

**guia-01 ahora ensena a crear el backend/.gitignore a mano (uv --vcs none no lo genera) y guia-04 declara el 404 del contrato via responses={404} con el schema Error, para que el /docs del alumno documente lo que el contrato promete.**

## Performance

- **Duration:** 4 min
- **Started:** 2026-09-29T12:02:02Z
- **Completed:** 2026-09-29T12:06:08Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- **G-01-1 cerrado:** el Paso 1 de guia-01 ya no afirma que `uv init backend --vcs none --app` genera un `.gitignore` — la enumeracion queda en pyproject.toml, .python-version, README.md y main.py, con nota corta que explica la causa (uv solo lo escribe cuando inicializa el VCS) y anticipa la creacion manual; el Paso 5 pasa de "revisar el .gitignore que genero uv" a CREAR el archivo con el contenido que la guia ya entregaba (bloque byte-identico) y la mini-verificacion valida el archivo recien creado.
- **G-01-4 cerrado (Opcion A):** guia-04 implementa el tercer schema del contrato (Error, con detail: str) junto a ProductoResumen/ProductoDetalle en el Paso 1; el router del Paso 3 importa Error y su decorator pasa a multilinea con responses={404} cuya description ("Producto inexistente (o inactivo)") y cuerpo (model Error) son palabra por palabra del contrato; prosa docente explica que FastAPI no documenta en OpenAPI los raise de runtime; la mini-verificacion agrega el item 5 (404 documentado con esquema Error en /docs) y el bullet de cierre se extiende.
- **Prohibiciones respetadas:** contrato_api.yaml sin cambios (gate git diff --quiet HEAD), WR-01/WR-02 siguen abiertos en 01-REVIEW-DISPOSITION.md, cero 422 declarado en responses (unico responses={ de la guia es el 404), cero comandos o URLs nuevos, guia-03 intacta y sus dos menciones al .gitignore siguen siendo ciertas (el alumno llega con el archivo creado en el Paso 5).

## Task Commits

Each task was committed atomically:

1. **Task 1: guia-01 — el .gitignore se crea a mano, uv no lo genero (G-01-1)** - `7d28520` (fix)
2. **Task 2: guia-04 — declarar el 404 en el router para que /docs refleje el contrato (G-01-4, Opcion A)** - `7d8ca85` (fix)

**Plan metadata:** (docs: complete plan) — ver Commit de metadatos al final del archivo.

## Files Created/Modified

- `docs/05_desarrollo/guia-01-proyecto-backend.md` - Paso 1 (enumeracion corregida + nota del VCS) y Paso 5 (crear el .gitignore + mini-verificacion del archivo creado)
- `docs/05_desarrollo/guia-04-catalogo.md` - Paso 1 (schema Error + oracion de anclaje al contrato), Paso 3 (import, decorator con responses={404}, prosa docente, item 5 de mini-verificacion) y bullet de "Lo que acabas de aprender"

## Decisions Made

- Opcion A sobre Opcion B para G-01-4 (justificacion completa en el objective del plan): la fila 11 existe para detectar drift entre contrato y /docs; normalizar un desvio con una nota le ensenaria al alumno que las advertencias excusan la divergencia.
- La direccion del fix es guia -> contrato: el contrato no se toca mientras WR-01/WR-02 esten abiertos.
- El contenido del .gitignore no se toca: el gap era quien crea el archivo, no su contenido.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Los dos gaps diagnosticados por el UAT quedan cerrados a nivel de guia; G-01-1 y G-01-4 pasan a resolved por linkage (gap_ids del frontmatter) al existir este SUMMARY.
- Pendiente de verify-work: re-ejecutar los tests 1 y 4 del UAT en el taller (D:/Repos/maura-uat) para confirmar el cierre por re-ejecucion — registrado en el ledger de windows como unrun-verify.
- WR-01 a WR-07 e IN-01 a IN-08 siguen abiertos en 01-REVIEW-DISPOSITION.md (fuera del alcance de este plan, por diseno).

## Self-Check: PASSED

- Archivos verificados en disco: 01-06-SUMMARY.md, guia-01-proyecto-backend.md, guia-04-catalogo.md
- Commits verificados en el historial: 7d28520 (Task 1), 7d8ca85 (Task 2)
- Ambos gates `<automated>` del plan en verde (contenido + ast.parse de 5 y 6 bloques python)
- contrato_api.yaml y guia-03 sin cambios respecto de plan_head_before

---
*Phase: 01-fundaciones-de-dos-tiers-y-cat-logo*
*Completed: 2026-09-29*
