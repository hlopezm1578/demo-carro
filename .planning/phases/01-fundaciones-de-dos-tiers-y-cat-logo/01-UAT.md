---
status: testing
phase: 01-fundaciones-de-dos-tiers-y-cat-logo
source: [01-VERIFICATION.md]
started: 2026-09-28
updated: 2026-09-29
---

## Current Test

number: 1
name: Re-ejecución post-fix de guia-01 (G-01-1) — uv init sin .gitignore y creación manual en Paso 5
expected: |
  Tras el fix del plan 01-06: `uv init backend --vcs none --app` genera exactamente 4 archivos
  (pyproject.toml, .python-version, README.md, main.py) y NO genera .gitignore; el Paso 5
  instruye crear backend/.gitignore con el contenido entregado y su mini-verificación valida
  el archivo recién creado.
awaiting: user response

## Tests

### 1. Re-ejecución guia-01 post-fix (G-01-1)
expected: En una máquina con Python 3.12 + uv: `uv init backend --vcs none --app` → `ls -a backend/` muestra solo pyproject.toml, .python-version, README.md, main.py (sin .gitignore; la guía lo explica en el Paso 1); en el Paso 5, crear `backend/.gitignore` con el contenido entregado por la guía y verificar que la mini-verificación del paso valida el archivo creado.
result: [pending]
notes: "Re-ejecución requerida: el UAT anterior corrió PRE-fix (result: issue → gap G-01-1, cerrado por plan 01-06 commit 7d28520). Reporte previo conservado en el historial del ciclo (01-VERIFICATION.md 2026-09-28)."

### 2. guia-02 — proyecto frontend y landing de Maura
expected: Siguiendo la guía con Node >= 22.22: scaffold vite react-ts, Tailwind 4 + Nunito, `npm run dev` → http://localhost:5173 muestra la landing con eyebrow "Maura · Body Splash", tagline "Frescura que te acompaña", párrafo en primera persona, CTA "Ver catálogo" y las 4 mini-cards de familia; `/productos` queda en estado de error controlado con botón "Reintentar" (el endpoint aún no existe — primera lección de estados async).
result: pass
verified_by: agent (user-delegated)
notes: "Ejecutada en D:/Repos/maura-uat con Node portátil v22.23.3. Todo OK (detalle en historial). PASS definitivo — el fix 01-06 no toca guia-02."

### 3. guia-03 — modelos y seed idempotente
expected: Siguiendo la guía: `uv run python -m app.seed` dos veces — primera corrida imprime doce marcas `[+]`, segunda corrida imprime doce `[=]` y cero `[+]`; sin filas duplicadas (12 productos exactos).
result: pass
verified_by: agent (user-delegated)
notes: "Salida byte-a-byte igual a la prometida (detalle en historial). PASS definitivo — el fix 01-06 no toca guia-03; el alumno llega con el .gitignore creado en el Paso 5 de guia-01, así que sus 2 menciones siguen siendo ciertas."

### 4. Re-ejecución guia-04 post-fix (G-01-4)
expected: Con el router corregido (schema Error en Paso 1 + responses={404} en el decorator de obtener_producto, Paso 3): http://localhost:8000/docs documenta 200, 404 (con cuerpo Error) y 422 para `GET /api/productos/{producto_id}`; la fila 11 de la Gran Verificación Final queda solo con los desvíos ya advertidos (WR-01/WR-02 del review); la mini-verificación del Paso 3 incluye el ítem 5 (404 documentado en /docs).
result: [pending]
notes: "Re-ejecución requerida: el UAT anterior corrió PRE-fix (result: issue → gap G-01-4, cerrado por plan 01-06 commit 7d8ca85, verificado a nivel documental por 01-VERIFICATION.md 2026-09-29). El 404 runtime ya funcionaba; lo nuevo es que /docs lo documenta."

## Summary

total: 4
passed: 2
issues: 0
pending: 2
skipped: 0
blocked: 0

## Gaps

- gap_id: G-01-1
  truth: "guia-01 Paso 1 afirmaba que `uv init backend --vcs none --app` genera un `.gitignore` en `backend/`, y el Paso 5 pedía 'revisar el .gitignore que generó uv'"
  status: fixed
  reason: "Cerrado por plan 01-06 (commit 7d28520): Paso 1 enumera solo los 4 archivos reales con nota de la causa (uv solo escribe .gitignore al inicializar el VCS); Paso 5 instruye CREAR backend/.gitignore con el contenido entregado; mini-verificación habla del archivo creado. Verificación documental 2026-09-29: cerrado; falta re-ejecución runtime (test 1 pendiente)."
  severity: minor
  test: 1
  artifacts:
    - path: "docs/05_desarrollo/guia-01-proyecto-backend.md"
      issue: "[resuelto] Paso 1 ya no lista .gitignore; Paso 5 enseña a crearlo"
  root_cause: "uv init solo genera .gitignore cuando crea el VCS: con --vcs none el archivo no existe (verificado empíricamente con uv 0.9.3)"
  debug_session: ""
- gap_id: G-01-4
  truth: "La fila 11 de la Gran Verificación Final de guia-04 debería mostrar solo los desvíos ya conocidos (WR-01/WR-02), pero el contrato declara respuesta 404 para /api/productos/{producto_id} y el panel /docs generado siguiendo la guía no la documentaba"
  status: fixed
  reason: "Cerrado por plan 01-06 (commit 7d8ca85, Opción A): schema Error en Paso 1 + responses={404} declarado en el decorator de obtener_producto con description palabra por palabra del contrato y model Error; prosa docente (FastAPI no documenta raise de runtime) + mini-verificación ítem 5. Verificación documental 2026-09-29: cerrado; falta re-ejecución runtime (test 4 pendiente)."
  severity: minor
  test: 4
  artifacts:
    - path: "docs/05_desarrollo/guia-04-catalogo.md"
      issue: "[resuelto] router declara la 404 del contrato; /docs la documenta"
  root_cause: "FastAPI no documenta en OpenAPI las HTTPException lanzadas a runtime si el endpoint no declara la respuesta vía el parámetro responses del decorator"
  debug_session: ""
