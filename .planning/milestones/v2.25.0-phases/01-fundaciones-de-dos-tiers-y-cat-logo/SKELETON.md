# Walking Skeleton — Demo Carro (Maura · Body Splash)

**Phase:** 1
**Generated:** 2026-09-28
**Reinterpreted:** 2026-09-28 — corrección de alcance D-17 (repositorio guide-only)

## Capability Proven End-to-End

> **El walking skeleton es documental (D-17):** un alumno que sigue `guia-01` y `guia-02` de
> `docs/05_desarrollo/` construye EN SU MÁQUINA el camino completo navegador → SPA React →
> proxy `/api` de Vite → API FastAPI en capas (router → service → repository → SQLAlchemy) →
> SQLite, y lo VERIFICA por sí mismo con las ✅ mini-verificaciones de la guía (backend:
> `uv init --vcs none` → `/api/salud` responde `{"estado": "ok"}` en su navegador; frontend:
> node -v >= 22.22 → create-vite → landing de marca + rutas + estados async). La grilla cobra
> vida con los 12 SKU en `guia-03`/`guia-04` y se cierra comparando `/docs` contra
> `contrato_api.yaml`.

Este repositorio **no contiene ni ejecuta la aplicación**: el código vive narrado dentro de las
guías como bloques que el alumno copia (modelo demo-cine). La implementación que las guías
narran se construyó y verificó de verdad antes de la corrección de alcance (historial git:
`364dee6` backend en capas, `de0253e` seed de 12 SKU) — las guías no inventan código. Los
planes de la fase se verifican por contenido documental (greps/estructura), jamás ejecutando.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Modelo del repo | **Guide-only (D-17)**: docs/ + .planning/ únicamente; el código vive narrado en las guías; README raíz como portada (D-18) | El producto educativo ES la guía; ADR-008 registra la decisión con consecuencias honestas |
| Framework (SPA) | React 19.3 + TypeScript ~6.0.2 sobre Vite 8.3.1 (`react-ts` template) — lo que la guía ENSEÑA a instalar | Stack verificado en `.planning/research/STACK.md`; el pin TS es del template (no subir a 7.x) |
| Framework (API) | FastAPI 0.141.1 con `fastapi[standard]`, gestionado por uv (`uv init --vcs none`, `requires-python >=3.12,<3.13`) | Doc oficial FastAPI enseña uv-first (D-10); techo 3.13 por transbank-sdk (fase 3) |
| Arquitectura backend | Capas `routers → services → repositories` con DI de FastAPI | Objetivo pedagógico declarado del proyecto (ADR-001) |
| Data layer | SQLite (stdlib 3.12) + SQLAlchemy 2.1, `Base.metadata.create_all` + seed upsert por SKU | Cero setup de aula; Alembic diferido al primer cambio de schema sobre datos (ADR-005, Pitfall 8) |
| Routing SPA | React Router 8 library mode (`BrowserRouter`, imports desde `react-router`) | v8 elimina el paquete `-dom`; el gate Node >= 22.22 es prerrequisito EN PROSA de guia-02, no del pipeline (D-17) |
| Estado servidor | TanStack Query 5.104 (`useQuery`) | Cache/estados de carga gratis; patrón que reusan las fases 2-4 |
| Contrato de API | OpenAPI 3.0.3 manual API-first (`docs/04_arquitectura/contrato_api.yaml`) — único artefacto de código-adyacente del repo | D-15; entregado por 01-01; cierre por guía: `/docs` ≈ contrato (ADR-007) |
| Styling | Tailwind 4 vía `@tailwindcss/vite` (sin config file) + Nunito self-hosted | Contrato UI aprobado (`01-UI-SPEC.md`) |
| Auth | Ninguna en fase 1 (público de solo lectura) | JWT llega en fase 2 |
| Deployment | Dev local documentado en las guías: `uv run fastapi dev` (8000) + `npm run dev` (5173) + proxy `/api` | Free tier público se congela para la fase 5 (decisiones de `return_url`) |
| Directory layout | Monorepo `backend/` + `frontend/` EN LA MÁQUINA DEL ALUMNO; `frontend/src/lib/api.ts` único punto HTTP; features por dominio | D-11 reinterpretado (D-17): el árbol documentado en 04_arquitectura es lo que las guías construyen |

## Stack Touched in Phase 1 (como contenido de las guías)

- [x] Project scaffold — uv (`uv init backend --vcs none`) + create-vite (`react-ts`) — enseñado en guia-01/guia-02 (planes 01-04)
- [x] Routing — rutas `/`, `/productos`, `/productos/:id`, `*` (React Router 8) — enseñado en guia-02 (plan 01-04)
- [x] Database — escritura (seed upsert por SKU) y lectura (`GET /api/productos`, `GET /api/productos/{id}`) — enseñado en guia-03/guia-04 (plan 01-05)
- [x] UI — landing de marca + grilla con datos reales + navegación grilla → ficha — enseñado en guia-02/guia-04 (planes 01-04/01-05)
- [x] Contrato API-first — `contrato_api.yaml` vive en el repo (01-01); su cierre `/docs` ≈ contrato se enseña en guia-04 (01-05)

## Out of Scope (Deferred to Later Slices)

- Carro de compras y cuentas JWT (fase 2)
- Checkout Webpay, órdenes, stock transaccional (fase 3)
- Panel admin y asistente Gemini (fase 4)
- Despliegue free tier y CORS de producción (fase 5 — congela `return_url`)
- Alembic (entra al primer cambio de schema que toque datos existentes)
- Búsqueda textual y paginación (STORE-05, v2)
- Cualquier código de aplicación en ESTE repo — prohibido por D-17 (invariant permanente)

## Subsequent Slice Plan

Cada fase posterior agrega un slice vertical sobre este skeleton sin alterar sus decisiones —
siempre como guías que el alumno construye y verifica en su máquina:

- Phase 2: cliente identificado — cuentas JWT + carro persistente en localStorage
- Phase 3: checkout Webpay sandbox + órdenes con stock atómico
- Phase 4: panel admin + asistente IA (mini-RAG sobre el catálogo)
- Phase 5: despliegue free tier + cierre del ciclo documentado
