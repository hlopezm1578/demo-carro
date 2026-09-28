---
phase: 01-fundaciones-de-dos-tiers-y-cat-logo
plan: 01-05
subsystem: docs
tags: [guias-desarrollo, seed, catalogo, filtros, clp, contrato-api]
requires: [01-03, 01-04]
provides:
  - "guia-03: modelo Producto + seed idempotente por upsert de los 12 SKU canonicos (STORE-04)"
  - "guia-04: API de productos con filtros + catalogo SPA con fotos, filtros URL, ficha y Gran verificación final contrato-<->-/docs (STORE-02/03, GUIDE-02)"
  - "Serie de desarrollo 1-4 completa de la fase 1 (GUIDE-03) y estado del ciclo al dia en ambos README (D-13/D-18)"
affects: [fase-2-cuentas-y-carro, docs/05_desarrollo, README ciclo]
actuals:
  tokens: 18600
  tasks: 3
  commits: 3
plan_head_before: 6190a60e8d3f7a88255f9dd1c175c83721273b54
plan_head_after: c472ce919dba8c332752a3453a92405e2a343b58
tech-stack:
  added: []
  patterns:
    - "guia que narra codigo verificado del historial git (de0253e seed, 364dee6 capas del catalogo)"
    - "Gran verificación final por fase: tabla numerada CS/RF + fila contrato <-> /docs (ADR-007) — convencion que replican las fases 2-5"
    - "paso de descarga de assets por el alumno (D-08 reinterpretado): fotos {sku}.jpg en SU frontend/public/products"
    - "filtros como URL search params con queryKey por combinacion; ApiError con status para distinguir 404 de error de red"
key-files:
  created:
    - docs/05_desarrollo/guia-03-modelos-y-seed.md
    - docs/05_desarrollo/guia-04-catalogo.md
  modified:
    - docs/README.md
    - README.md
    - docs/05_desarrollo/README.md
    - docs/05_desarrollo/guia-01-proyecto-backend.md
    - docs/05_desarrollo/guia-02-proyecto-frontend.md
key-decisions:
  - "Los bloques backend de guia-03/04 narran el codigo verificado del historial (de0253e/364dee6) casi verbatim; solo se adaptaron comentarios que referenciaban pitfalls internos de .planning"
  - "La ficha distingue 404 de error de red extendiendo lib/api.ts con ApiError(status) — ensenanza alineada al UI-SPEC (dos errores, dos pantallas)"
  - "Gran verificación final de guia-04 = 11 filas numeradas citando CS/RF/RN/HU, con la fila 11 contrato <-> /docs como evidencia de cierre de fase"
  - "Estado fila 5 = 'Parcial (guias 1-4 listas; continua en fases 2+)' en AMBOS README: el desarrollo no termina, la fase 1 si"
requirements-completed: [GUIDE-02, GUIDE-03, STORE-02, STORE-03, STORE-04]
coverage:
  - id: GUIDE-02
    description: "La guia-04 implementa el contrato y lo cierra comparando /docs contra contrato_api.yaml (fila 11 de la tabla de chequeo)"
    requirement: GUIDE-02
    verification:
      - {kind: other, ref: "grep 'Gran verificación final' + fila 'Contrato ↔ /docs' en guia-04", status: pass}
      - {kind: other, ref: "grep contrato_api.yaml en guia-03 y guia-04", status: pass}
    human_judgment: false
  - id: GUIDE-03
    description: "Las 4 guias permiten construir la fase desde cero con mini-verificaciones accionables por paso (guia-03: 6 ✅, guia-04: 7 ✅)"
    requirement: GUIDE-03
    verification:
      - {kind: other, ref: "grep -c 'Mini-verificación' >= 4 (g3) y >= 5 (g4)", status: pass}
      - {kind: other, ref: "grep -c 'El desarrollador piensa' >= 4 (g3) y >= 5 (g4)", status: pass}
    human_judgment: false
  - id: STORE-02
    description: "Guia-04 ensena grilla filtrable (chips familia + rango precio en useSearchParams, contador con plural, estados async)"
    requirement: STORE-02
    verification:
      - {kind: other, ref: "grep useSearchParams + contador plural + estados vacio/error en guia-04", status: pass}
    human_judgment: false
  - id: STORE-03
    description: "Guia-04 ensena la ficha completa: regla de stock en 3 niveles, notas como chips, navigate(-1), 404 con ApiError"
    requirement: STORE-03
    verification:
      - {kind: other, ref: "grep 'Notas aromáticas' + navigate(-1) + BadgeDisponibilidad en guia-04", status: pass}
    human_judgment: false
  - id: STORE-04
    description: "Guia-03 ensena el seed upsert por SKU con idempotencia observable ([+] -> [=]) y restauracion canonica"
    requirement: STORE-04
    verification:
      - {kind: other, ref: "grep upsert + app.seed + doce [=] en guia-03", status: pass}
    human_judgment: false
duration: 6min
completed: 2026-09-28
status: complete
---

# Phase 01 Plan 01-05: Guías 03-04 y cierre del ciclo de desarrollo Summary

**Guía 3 (modelo + seed upsert de los 12 SKU canónicos, STORE-04) y guía 4 (API de productos + catálogo completo con fotos, filtros en URL, ficha y la Gran verificación final contrato ↔ /docs, STORE-02/03, GUIDE-02), con el estado del ciclo al día en ambos README.**

## Performance

- **Duración:** 6 min (estimado: 38000 tokens / 3 tasks, confianza low)
- **Actual:** 3 tasks, 3 commits, ~18600 tokens medidos (chars/4 del diff 6190a60..c472ce9) — 49 % del estimado: el material verificado ya existía en el historial git y el formato canónico venía fijado por las guías 01-02
- **Commits medidos:** `git rev-list --count 6190a60..HEAD` = 3 (ledger `gsd-plan-head-before-01-05`)

## Accomplishments

- **guia-03-modelos-y-seed.md** (636 líneas): `database.py` con sesión por request (ADR-001), el enum `FamiliaAromatica` con el gotcha nombre==slug demostrado y verificado por el alumno, el modelo `Producto` de 10 campos traducido campo a campo del diccionario del doc 03, `create_all` con la advertencia honesta de ADR-005 (Alembic diferido), y el seed completo de los 12 SKU canónicos con upsert `[+]`/`[=]` narrando el código verificado (`git show de0253e:backend/app/seed.py`).
- **guia-04-catalogo.md** (955 líneas): schemas espejo del contrato, repository con select parameterizado, service con el 404, router con Enum + `Query(ge=0)` y el 422 verificado en el navegador; paso de descarga de las 12 fotos stock a `frontend/public/products/{sku}.jpg` (única sección con URLs de terceros, gate negativo sin `src="https…"`); catálogo con filtros en URL search params, contador con plural y los cuatro estados async; ficha completa con regla de stock, notas como chips, `navigate(-1)` y 404 distinguido vía `ApiError`; **Gran verificación final** de 11 filas citando CS/RF con la fila contrato ↔ `/docs` obligatoria (ADR-007) — el mecanismo que replican las fases 2-5.
- **Cierre:** fila 5 del ciclo al día en `docs/README.md` y `README.md` ("guías 1-4 listas; continúa en fases 2+"), README de `05_desarrollo` con las filas 3-4 en ✅ Listo, cadena Siguiente continua 01→02→03→04→fase 2, y el repo sigue sin código de aplicación (`git ls-files -- backend frontend` vacío).

## Task Commits

| Task | Commit | Descripción |
|---|---|---|
| 1 — guia-03 modelos y seed | `4b951c0` | docs(01-05): guia-03 modelos y seed |
| 2 — guia-04 catálogo y gran verificación | `66c6589` | docs(01-05): guia-04 catalogo y gran verificación final |
| 3 — cierre READMEs y coherencia | `c472ce9` | docs(01-05): cierre — estado de los README y coherencia de la serie |

## Files Created-Modified

**Creados:** `docs/05_desarrollo/guia-03-modelos-y-seed.md`, `docs/05_desarrollo/guia-04-catalogo.md`

**Modificados:** `docs/README.md`, `README.md`, `docs/05_desarrollo/README.md`, `docs/05_desarrollo/guia-01-proyecto-backend.md` (enlace Siguiente), `docs/05_desarrollo/guia-02-proyecto-frontend.md` (enlace Siguiente)

## Decisions Made

- Los bloques backend provienen del código verificado del historial (de0253e/364dee6); solo se adaptaron comentarios que citaban "Pitfall 4/6" interno de `.planning` — referencias sin sentido para el alumno.
- `lib/api.ts` se extiende con `ApiError` (status) en guia-04 para que la ficha distinga 404 de error de red: dos errores, dos pantallas (HU-03 + UI-SPEC).
- La Gran verificación final usa 11 filas numeradas con origen CS/RF/RN/HU y la fila 11 contrato ↔ `/docs` como evidencia formal de cierre; se documenta que el contrato vive en el repo de la guía y el `/docs` en la máquina del alumno.
- El estado de la fila 5 NO pasa a ✅: las guías 1-4 de la fase 1 están listas, pero el desarrollo continúa en las fases 2+ (portada e índice dicen la misma verdad, D-18).

## Deviations from Plan

**1. [Regla 3 - coherencia] Archivos tocados más allá de `files_modified` (guia-01, guia-02, README de 05_desarrollo)**
- **Found during:** Task 3 (verificación de coherencia de la serie)
- **Issue:** los enlaces "Siguiente" de guia-01/guia-02 envolvían el nombre de archivo en backticks, rompiendo el gate de cadena del propio plan (`Siguiente:** guia-0N`); y el README de 05_desarrollo mantenía las filas 3-4 como "⏳ Pendiente" pese a existir las guías.
- **Fix:** backticks eliminados en los dos enlaces (2 líneas) y filas 3-4 a "✅ Listo" con nota actualizada. Estaba explícitamente mandateado por la acción 3 del Task 3 ("corregir cualquier eslabón suelto"); se documenta porque excede la lista `files_modified` del frontmatter.
- **Files modified:** guia-01-proyecto-backend.md, guia-02-proyecto-frontend.md, docs/05_desarrollo/README.md
- **Commit:** c472ce9

Fuera de eso: **ninguna** — los tres tasks se ejecutaron tal como estaban escritos y los tres gates de verificación pasaron a la primera.

## Issues Encountered

None.

## User Setup Required

None.

## Next Phase Readiness

- La fase 1 completa su serie de desarrollo: las guías 1-4 permiten construir backend en capas + SPA + datos + catálogo de punta a punta con verificación observable por paso (GUIDE-03) y el cierre contrato ↔ `/docs` queda establecido como convención permanente (GUIDE-02).
- REQUIREMENTS.md: GUIDE-02, GUIDE-03, STORE-02, STORE-03, STORE-04 marcados completos (los 5 reportados ready por el shared-ID gate).
- La cadena "Siguiente" apunta a la fase 2 (cuentas y carro): los bloqueos conocidos de fases posteriores siguen registrados en STATE.md (spike Webpay fase 3, ADR de órdenes, límites Gemini fase 4, plataforma de deploy fase 5).

## Self-Check: PENDING
