---
status: testing
phase: 01-fundaciones-de-dos-tiers-y-cat-logo
source: [01-VERIFICATION.md]
started: 2026-09-28
updated: 2026-09-28
---

## Current Test

number: 1
name: guia-01 — proyecto backend de cero a /api/salud
expected: |
  Siguiendo docs/05_desarrollo/guia-01-proyecto-backend.md en una máquina con Python 3.12 y uv:
  `uv init --vcs none` (sin repo anidado), dependencias instaladas, `uv run fastapi dev` levanta,
  y GET http://127.0.0.1:8000/api/salud responde {"estado": "ok"}; /docs abre Swagger.
awaiting: user response

## Tests

### 1. guia-01 — proyecto backend de cero a /api/salud
expected: Siguiendo la guía en una máquina con Python 3.12 + uv: `uv init backend --vcs none` (sin repo git anidado), `uv add` de dependencias, `uv run fastapi dev` levanta sin errores, `GET /api/salud` → `{"estado": "ok"}`, `/docs` muestra Swagger.
result: [pending]

### 2. guia-02 — proyecto frontend y landing de Maura
expected: Siguiendo la guía con Node >= 22.22: scaffold vite react-ts, Tailwind 4 + Nunito, `npm run dev` → http://localhost:5173 muestra la landing con eyebrow "Maura · Body Splash", tagline "Frescura que te acompaña", párrafo en primera persona, CTA "Ver catálogo" y las 4 mini-cards de familia; `/productos` queda en estado de error controlado con botón "Reintentar" (el endpoint aún no existe — primera lección de estados async).
result: [pending]

### 3. guia-03 — modelos y seed idempotente
expected: Siguiendo la guía: `uv run python -m app.seed` dos veces — primera corrida imprime doce marcas `[+]`, segunda corrida imprime doce `[=]` y cero `[+]`; sin filas duplicadas (12 productos exactos).
result: [pending]

### 4. guia-04 — catálogo completo y cierre contrato ↔ /docs
expected: Siguiendo la guía: grilla con 12 productos, filtros por familia y rango de precio reflejados en la URL (compartibles con back/forward), ficha de producto con badge ámbar "¡Últimas N unidades!" cuando stock <= 3, familia inválida por URL editada → 422 con mensaje claro, descarga de las 12 fotos a frontend/public/products/, y la fila 11 de la Gran Verificación Final compara /docs contra contrato_api.yaml. NOTA: WR-01/WR-02 del review (abiertos) harán aparecer un desvío falso en esa fila (422 faltante en el contrato para /api/productos/{id} y schema Error detail string vs array) — revisar con esa lectura.
result: [pending]

## Summary

total: 4
passed: 0
issues: 0
pending: 4
skipped: 0
blocked: 0

## Gaps
