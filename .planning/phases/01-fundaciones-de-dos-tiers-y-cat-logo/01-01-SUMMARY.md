---
phase: 01-fundaciones-de-dos-tiers-y-cat-logo
plan: 01-01
subsystem: api
tags: [fastapi, sqlalchemy, sqlite, openapi, uv, pydantic-settings, seed]

requires: []
provides:
  - Contrato OpenAPI 3.0.3 API-first de la tienda (docs/04_arquitectura/contrato_api.yaml) con /api/salud, /api/productos (familia + precio_min/max) y /api/productos/{producto_id}
  - Backend FastAPI 0.141.1 en capas (routers → services → repositories) sobre SQLAlchemy 2.1 + SQLite con CORS explícito desde Settings
  - Tabla productos con FamiliaAromatica (enum slug ASCII), notas JSON y precio Integer CLP
  - Seed idempotente por upsert de SKU con los 12 productos demo canónicos (datos fijados: nombres, precios, notas, stock)
  - Settings (pydantic-settings): database_url y cors_origins sobreescribibles por entorno
affects: [01-02, 01-03, 01-04, 01-05, 01-06, 01-07, Phase 2, Phase 3, Phase 4, Phase 5]

actuals:
  tokens: 26651   # chars/4 sobre el diff realizado (106603 chars / 4)
  tasks: 3
  commits: 3
  plan_head_before: 76693810dd79c90655f9a15f08a13fee4e26b5ed
  plan_head_after: de0253e2fc774bfce4df028f0d7e04e284021f96

tech-stack:
  added: ["fastapi[standard] 0.141.1", "sqlalchemy 2.1.1", "pydantic-settings 2.15.0", "uv 0.9.3 (workflow D-10)", "SQLite (stdlib 3.12)"]
  patterns:
    - "API-first: contrato YAML aprobado antes del código; Pydantic espeja sus schemas"
    - "Capas routers → services → repositories con DI de FastAPI (sesión por request); routers sin importar sqlalchemy"
    - "Enum con nombre == valor (slug ASCII) para que BD y API transmitan 'citricas' sin acentos"
    - "Seed idempotente por upsert de SKU: re-ejecutar converge al estado canónico"

key-files:
  created:
    - docs/04_arquitectura/contrato_api.yaml
    - backend/app/main.py
    - backend/app/config.py
    - backend/app/database.py
    - backend/app/models/producto.py
    - backend/app/schemas/producto.py
    - backend/app/repositories/producto.py
    - backend/app/services/catalogo.py
    - backend/app/routers/productos.py
    - backend/app/routers/salud.py
    - backend/app/seed.py
    - backend/pyproject.toml (+ uv.lock, .python-version, .gitignore, README.md)
  modified: []

key-decisions:
  - "Contrato API-first (D-15/GUIDE-02): el YAML se aprobó en Task 1 ANTES de cualquier línea de backend; convención de errores declara 200/404/422 en uso y 400/401/403/409 reservados para fases 2+"
  - "Los routers no importan sqlalchemy: Session se importa desde app.database (re-export), cumpliendo la regla de dependencia verificable sin perder tipado"
  - "ProductoRepository.obtener filtra activo además de id, alineado con el 404 '(o inactivo)' del contrato — la ficha jamás sirve productos desactivados"
  - "Seed upsert por SKU (no DELETE+reinsert): re-ejecutar restaura stock/precios demo — compatible con las FK de order_items de la fase 3 (STORE-04)"
  - "Los 12 SKU demo quedan fijados como datos canónicos (precios 6990–12990 CLP, stock 14/9/3/11/7/2/16/8/5/6/12/10, imágenes /products/{sku}.jpg) para que guías y UI citen siempre los mismos valores"
  - "Commits directos a master: el proyecto configura git.branching_strategy 'none' (GSD no crea branches) y el despacho es secuencial sobre el working tree principal"

patterns-established:
  - "Capas con DI: router valida HTTP (Enum + Query(ge=0) → 422 automático) → CatalogService → ProductoRepository(select parameterizado)"
  - "Seed ejecutable agnóstico de terminal: uv run python -m app.seed, con marcas [+] / [=] por producto"
  - "create_all vive en el seed (no en main.py): schema y datos existen antes de cualquier verificación de endpoints"

requirements-completed: [GUIDE-02, STORE-02, STORE-03, STORE-04]

coverage:
  - id: D1
    description: "Contrato OpenAPI 3.0.3 API-first de la tienda con convención de errores y trazabilidad STORE-02/STORE-03"
    requirement: GUIDE-02
    verification:
      - kind: other
        ref: "grep chain del plan (openapi 3.0.3, /api/salud, /api/productos/{producto_id}, ProductoResumen/ProductoDetalle, allOf, enum 4 slugs, precio_min) → contrato-ok; yaml.safe_load OK"
        status: pass
    human_judgment: false
  - id: D2
    description: "Backend FastAPI en capas que implementa el contrato: salud, listado con filtros validados, detalle, 404 y 422"
    requirement: STORE-02
    verification:
      - kind: integration
        ref: "TestClient (backend): /api/salud 200, familia=xyz 422, /api/productos/999 404, familia=citricas 3 items, precio 8000-11000 → 7 items todos en rango, todas las respuestas application/json"
        status: pass
    human_judgment: false
  - id: D3
    description: "Seed idempotente de 12 SKU demo con datos canónicos re-ejecutable sin duplicar"
    requirement: STORE-04
    verification:
      - kind: integration
        ref: "uv run python -m app.seed x2 → segunda corrida imprime doce [=] y cero [+]; count == 12; GET /api/productos == 12; ficha /1 con notas y stock → seed-ok-12"
        status: pass
    human_judgment: false

duration: 9min
completed: 2026-09-28
status: complete
---

# Phase 01 Plan 01-01: Contrato API-first y backend en capas Summary

**Contrato OpenAPI 3.0.3 aprobado antes del código + backend FastAPI en capas (routers → services → repositories) sobre SQLite con seed idempotente de 12 SKU: la API sirve salud, catálogo filtrable y ficha con 404/422 de punta a punta.**

## Performance
- **Duration:** 9min
- **Started:** 2026-09-28T18:41:09Z
- **Completed:** 2026-09-28T18:49:47Z
- **Tasks:** 3
- **Files modified:** 22

## Accomplishments
- El contrato `docs/04_arquitectura/contrato_api.yaml` (OpenAPI 3.0.3) existe ANTES que el código backend (commit 1dc84d7 → 364dee6) — punto pedagógico API-first (D-15) materializado con convención de errores y descriptions que citan STORE-02/STORE-03.
- Backend completo en capas con `uv init --vcs none` (sin repo anidado), `requires-python >=3.12,<3.13` (techo transbank-sdk) y las cuatro capas cruzadas por TestClient: validación declarativa (Enum → 422 sin código manual), filtros componibles parameterizados y 404 desde el service.
- Seed canónico de 12 SKU (4 familias × 3) con upsert por SKU: la re-ejecución imprime doce `[=]` y cero `[+]` y restaura stock/precios demo sin duplicar filas (STORE-04).

## Task Commits
1. **Task 1: Contrato OpenAPI API-first** - `1dc84d7` (feat)
2. **Task 2 (tracer): Backend FastAPI en capas** - `364dee6` (feat) — tracer feedback gate re-run en modo auto: `tracer-ok`, verificado end-to-end antes de expandir
3. **Task 3: Seed completo de 12 SKU** - `de0253e` (feat)
**Plan metadata:** commit docs posterior (SUMMARY + STATE + ROADMAP)

## Files Created/Modified
- `docs/04_arquitectura/contrato_api.yaml` - Contrato OpenAPI 3.0.3 API-first: 3 paths, schemas Error/ProductoResumen/ProductoDetalle (allOf), convención de errores
- `backend/app/main.py` - FastAPI(title="Maura API") + CORSMiddleware explícito + include_router /api/salud y /api/productos
- `backend/app/config.py` - Settings (pydantic-settings): database_url, cors_origins
- `backend/app/database.py` - engine, SessionLocal, Base(DeclarativeBase), get_session (sesión por request)
- `backend/app/models/producto.py` - FamiliaAromatica (nombre == slug) y Producto (precio Integer CLP, notas JSON, activo)
- `backend/app/schemas/producto.py` - ProductoResumen / ProductoDetalle espejando el contrato (from_attributes)
- `backend/app/repositories/producto.py` - Única capa SQL: select parameterizado con filtros componibles y orden estable
- `backend/app/services/catalogo.py` - CatalogService: casos de uso listar/obtener, sin HTTP
- `backend/app/routers/productos.py` - GET "" y GET /{producto_id} con Query(ge=0), Enum y HTTPException 404
- `backend/app/routers/salud.py` - GET "" → {"estado": "ok"}
- `backend/app/seed.py` - upsert_producto + PRODUCTOS_DEMO (12 SKU canónicos) + create_all + resumen [+] / [=]
- `backend/pyproject.toml`, `backend/uv.lock`, `backend/.python-version`, `backend/.gitignore`, `backend/README.md` - Proyecto uv con dependencias (fastapi[standard], sqlalchemy, pydantic-settings)

## Decisions Made
- **Routers sin sqlalchemy (cumplimiento literal de la regla de dependencia):** `Session` se importa desde `app.database` (que la re-exporta), así `grep -L "sqlalchemy" backend/app/routers/*.py` devuelve todos los routers — AC del plan cumplida sin perder el tipado de la sesión inyectada.
- **`obtener` filtra `activo`:** el contrato declara el 404 como "Producto inexistente (o inactivo)"; el repositorio lo implementa así desde el día 1 (coherencia contrato ↔ código).
- **Seed con enum members (no strings) en `familia`:** `FamiliaAromatica.citricas` es la forma documentada por SQLAlchemy; el slug persistido es idéntico.
- **Commits a master:** `git.branching_strategy: "none"` en `.planning/config.json` (GSD no crea branches en este proyecto) + despacho secuencial sobre el working tree principal; los 3 commits del ciclo de planificación previos ya seguían esta convención.
- Ninguna otra — el resto del plan se ejecutó tal como estaba escrito.

## Deviations from Plan
None - plan executed exactly as written.

**Total deviations:** 0 auto-fixed. **Impact:** ninguno — las tres tasks pasaron sus `<verify>` y acceptance criteria en la primera corrida.

## Issues Encountered
- **Artefacto de ambiente (no del código):** en Git Bash (MSYS) los argumentos que comienzan con `/` se convierten a rutas de Windows, por lo que los greps del plan tipo `grep -q "/api/salud"` fallaban sin razón aparente. Solución: ejecutar la verificación con `MSYS2_ARG_CONV_EXCL='*'`. El archivo siempre estuvo correcto; documentado aquí para el verificador y para las guías (los alumnos de PowerShell/cmd no se ven afectados).
- Deprecation warning de Starlette al importar TestClient (httpx → httpx2): solo ruido del tooling de pruebas, no afecta los asserts ni la API.

## Authentication Gates
None - no se requirió autenticación (paquetes instalados desde la lista auditada del Package Legitimacy Audit de 01-RESEARCH.md: fastapi/sqlalchemy/pydantic-settings, todos Approved).

## User Setup Required
None - no external service configuration required. (`backend/maura.db` se genera localmente al correr el seed; ya está gitignored.)

## Next Phase Readiness
- El contrato y la API quedan listos para que 01-03 (frontend) consuma `/api/productos` con los tipos espejo (D-09) y para que 01-02/01-04 documenten ADRs y guías citando esta implementación.
- Los 12 SKU canónicos están fijados; las fotos `/products/{sku}.jpg` aún no existen (llegan con el frontend, D-08) — el seed referencia las rutas finales.
- `requirements.ready-ids` devolvió 0/4: los IDs GUIDE-02/STORE-02/STORE-03/STORE-04 son compartidos con otros planes de la fase (p. ej. 01-03, 01-04) que aún no tienen SUMMARY — se marcarán complete cuando todos los planes declarantes terminen (shared-ID gate).
