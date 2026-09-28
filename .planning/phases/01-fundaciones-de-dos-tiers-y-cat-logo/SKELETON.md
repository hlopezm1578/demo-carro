# Walking Skeleton — Demo Carro (Maura · Body Splash)

**Phase:** 1
**Generated:** 2026-09-28

## Capability Proven End-to-End

> Un visitante abre `http://localhost:5173/productos` y ve la grilla del catálogo con los 12
> body splash sembrados en SQLite, servidos por la API FastAPI en capas
> (router → service → repository → SQLAlchemy) a través del proxy `/api` de Vite: el stack
> completo navegador → SPA React → proxy → API → SQLite queda probado de punta a punta.

El skeleton se completa en dos planes por una razón de ambiente (no de arquitectura):
`01-01-PLAN.md` (ola 1) entrega el tier servidor completo con seed real, y `01-03-PLAN.md`
(ola 2) entrega el tier cliente, porque el upgrade de Node a >= 22.22 (exigencia de
`react-router@8.4.0`, RESEARCH Pitfall 1) requiere acción humana antes del scaffold.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Framework (SPA) | React 19.3 + TypeScript ~6.0.2 sobre Vite 8.3.1 (`react-ts` template) | Stack verificado en `.planning/research/STACK.md`; el pin TS es del template (no subir a 7.x) |
| Framework (API) | FastAPI 0.141.1 con `fastapi[standard]`, gestionado por uv | Doc oficial FastAPI enseña uv-first (D-10) |
| Arquitectura backend | Capas `routers → services → repositories` con DI de FastAPI | Objetivo pedagógico declarado del proyecto |
| Data layer | SQLite (stdlib 3.12) + SQLAlchemy 2.1, `Base.metadata.create_all` + seed upsert por SKU | Cero setup de aula; Alembic diferido al primer cambio de schema sobre datos (ADR-005, Pitfall 8) |
| Routing SPA | React Router 8 library mode (`BrowserRouter`, imports desde `react-router`) | v8 elimina `react-router-dom`; data mode descartado |
| Estado servidor | TanStack Query 5.104 (`useQuery`) | Cache/estados de carga gratis; patrón que reusan las fases 2-4 |
| Contrato de API | OpenAPI 3.0.3 manual API-first (`docs/04_arquitectura/contrato_api.yaml`) ANTES del código | D-15; punto pedagógico diseño por contrato |
| Styling | Tailwind 4 vía `@tailwindcss/vite` (sin config file) + Nunito self-hosted | Contrato UI aprobado (`01-UI-SPEC.md`) |
| Auth | Ninguna en fase 1 (público de solo lectura) | JWT llega en fase 2 |
| Deployment | Dev local documentado: `uv run fastapi dev` (8000) + `npm run dev` (5173) + proxy `/api` | Free tier público se congela para la fase 5 (decisiones de `return_url`) |
| Directory layout | Monorepo `backend/` + `frontend/`; `frontend/src/lib/api.ts` único punto HTTP; features por dominio | D-11; regla de único punto de salida HTTP |

## Stack Touched in Phase 1

- [x] Project scaffold — uv (`uv init backend --vcs none`) + create-vite (`react-ts`) — planes 01-01 y 01-03
- [x] Routing — rutas `/`, `/productos`, `/productos/:id`, `*` (React Router 8) — plan 01-03
- [x] Database — lectura real (`GET /api/productos`, `GET /api/productos/{id}`) Y escritura real (seed upsert por SKU) — plan 01-01
- [x] UI — grilla con datos reales + navegación grilla → ficha vía Link — planes 01-03 y 01-05
- [x] Deployment — comando local full-stack documentado (backend 8000 + frontend 5173 + proxy) y reproducido en las guías — planes 01-01, 01-03, 01-06

## Out of Scope (Deferred to Later Slices)

- Carro de compras y cuentas JWT (fase 2)
- Checkout Webpay, órdenes, stock transaccional (fase 3)
- Panel admin y asistente Gemini (fase 4)
- Despliegue free tier y CORS de producción (fase 5 — congela `return_url`)
- Alembic (entra al primer cambio de schema que toque datos existentes)
- Búsqueda textual y paginación (STORE-05, v2)

## Subsequent Slice Plan

Cada fase posterior agrega un slice vertical sobre este skeleton sin alterar sus decisiones:

- Phase 2: cliente identificado — cuentas JWT + carro persistente en localStorage
- Phase 3: checkout Webpay sandbox + órdenes con stock atómico
- Phase 4: panel admin + asistente IA (mini-RAG sobre el catálogo)
- Phase 5: despliegue free tier + cierre del ciclo documentado
