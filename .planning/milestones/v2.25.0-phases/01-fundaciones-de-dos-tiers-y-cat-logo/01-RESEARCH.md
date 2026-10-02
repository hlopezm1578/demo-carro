# Phase 1: Fundaciones de dos tiers y catálogo - Research

**Researched:** 2026-09-28
**Domain:** Greenfield two-tier e-commerce skeleton — SPA React 19 + TS (Vite 8, Tailwind 4, React Router 8, TanStack Query) que consume API FastAPI 0.141 en capas (uv, SQLAlchemy 2.1, SQLite) + guía educativa estilo demo-cine (docs/, ADRs, contrato OpenAPI API-first, sub-guías paso a paso)
**Confidence:** HIGH

## Summary

La fase 1 es greenfield total: levanta el monorepo `backend/` + `frontend/`, el catálogo público con filtros, el seed idempotente de 12 SKU y toda la convención documental del ciclo (docs 01–05, ADRs fundacionales, `contrato_api.yaml`). El stack está ya verificado contra registros y docs oficiales el mismo día por `.planning/research/STACK.md` y `.planning/research/ARCHITECTURE.md`; esta investigación re-verificó los puntos que la fase 1 toca directamente (engines de react-router 8, export map de react-router 8, proxy de Vite, setup de TanStack Query, layout de `uv init`, tipos Enum/JSON de SQLAlchemy, formato CLP) y auditó el ambiente de ejecución.

**Hallazgo crítico de ambiente:** el Node instalado es **v22.18.0**, pero `react-router@8.4.0` declara `engines: { node: '>=22.22.0' }` [VERIFIED: npm view react-router@8.4.0 engines, esta sesión]. El plan NECESITA un paso de upgrade de Node (>= 22.22 o Node 24) o un `checkpoint:human-verify` antes de instalar el frontend; sin él, `npm install` emite EBADENGINE y el stack bloqueado (AGENTS.md Technology Stack exige Node >= 22.22) no se cumple. Todo lo demás del ambiente está OK (Python 3.12.10, uv 0.9.3, npm 11.16.0, git 2.50.1, puertos 5173/8000 libres).

**Hallazgos de verificación que corrigen conocimiento previo:** (1) React Router 8 ELIMINA el paquete `react-router-dom` — los imports van a `react-router`; el subpath `react-router/dom` solo exporta `RouterProvider`/`HydratedRouter` (data mode), NO `BrowserRouter` [VERIFIED: inspección del tarball react-router@8.4.0 esta sesión; corregido contra un resumen web que decía lo contrario]. (2) `uv init` ejecuta `git init` interno — en el monorepo crea un repo embebido que rompe el tracking del padre; usar `uv init --vcs none` [VERIFIED: ejecución de uv init en temp + uv init --help, esta sesión]. (3) `Enum` de SQLAlchemy persiste los NOMBRES de los miembros, no los valores — la tabla de familias debe declarar miembros cuyo nombre sea el slug.

**Primary recommendation:** Planificar en 4 frentes secuenciales — (A) docs fundacionales 01–04 con ADRs + contrato YAML ANTES del código (API-first, D-15), (B) backend con uv (`--vcs none`, `requires-python >=3.12,<3.13`, create_all + seed upsert por SKU), (C) frontend con el scaffold react-ts + Tailwind 4 + RR8 library mode + TanStack Query + proxy `/api`, (D) guías 05_desarrollo por hito (backend → frontend → modelos/seed → catálogo) replicando el formato demo-cine (🧠 razonamiento, pasos, ✅ mini-verificaciones). Gate inicial: resolver Node >= 22.22.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** La tienda ficticia se llama **Maura** — marca eponima de la dueña, presentación "Maura · Body Splash", estilo emprendimiento chileno real — *Reversibility: costly*.
- **D-02:** La dueña Maura tiene **persona breve**: 2-3 frases fijadas en la guía (quién es, qué vende, por qué necesita la tienda online).
- **D-03:** Dirección visual de la marca: **fresco y luminoso** — pasteles cítricos, mucho blanco, tipografía redondeada. El contrato de UI (`/gsd:ui-phase`) formaliza la paleta Tailwind concreta.
- **D-04:** Tagline del hero de la landing: **"Frescura que te acompaña"**.
- **D-05:** El catálogo se organiza en **4 familias aromáticas: Cítricas, Florales, Frutales y Dulces** (gourmand) — *Reversibility: costly*.
- **D-06:** El seed contiene **12 SKU** (4 familias × 3 productos).
- **D-07:** Rango de precios: **$6.990–$12.990 CLP**.
- **D-08:** Imágenes de producto: **fotos stock reales (Unsplash/Pexels, licencia libre) descargadas al repo** en `frontend/public/products/`; el seed referencia rutas locales (`/products/*.jpg`). La guía incluye el paso de descarga — nada de hotlinks externos.
- **D-09:** El frontend va en **TypeScript** (template `react-ts` de Vite). Las interfaces TS espejan los schemas Pydantic — *Reversibility: costly*.
- **D-10:** El backend se maneja con **uv** (`uv add` / `uv run fastapi dev`, pyproject + lock).
- **D-11:** El proyecto vive en un **monorepo** `backend/` + `frontend/` — *Reversibility: costly*.
- **D-12:** Comandos de la guía **agnósticos de terminal**: todo vía npm scripts y `uv run`, sin sintaxis exclusiva de bash. Debe funcionar igual en PowerShell, cmd y Git Bash.
- **D-13:** `docs/` **replica la estructura de demo-cine**: `01_necesidad_del_cliente.md` … `08_mantenimiento.md`, con `04_arquitectura/` (documento + `adr/` + `contrato_api.yaml`) y `05_desarrollo/` (guías numeradas). Los documentos se escriben por fase GSD conforme la app se construye — *Reversibility: costly*.
- **D-14:** La fase 1 escribe **todo lo fundacional del ciclo**: `01_necesidad` (Maura), `02_requerimientos` (los cubiertos por la fase), `03_diseno` (modelo de datos de producto + pantallas del catálogo), `04_arquitectura` (ADRs fundacionales + contrato API inicial) y las primeras guías de `05_desarrollo`.
- **D-15:** Contrato de API **YAML API-first manual** (`docs/04_arquitectura/contrato_api.yaml`): se escribe ANTES del código y FastAPI lo implementa.
- **D-16:** Las guías de desarrollo se parten en **sub-guías numeradas por hito** dentro de cada fase (en la fase 1, del orden: proyecto backend, proyecto frontend, modelos y seed, catálogo).

### Claude's Discretion
- Nombres concretos, notas aromáticas y descripciones de los 12 productos (dentro de las 4 familias fijadas).
- Selección concreta de las fotos stock (criterio: consistencia visual entre productos de una misma familia).
- Qué ADRs fundacionales se numeran exactamente y su redacción (candidatos naturales: stack, arquitectura en capas, SQLite, TypeScript, uv, monorepo, API-first).
- Stock inicial por producto y valores exactos de precios dentro del rango fijado.
- Paleta Tailwind concreta bajo la dirección fresco-luminosa (la formaliza `/gsd:ui-phase`).
- Rutas de la SPA, prefijos de API y detalles de estructura de carpetas (seguir la investigación de arquitectura).

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GUIDE-02 | Cada fase documenta sus ADRs y mantiene el contrato de API actualizado | Formato ADR demo-cine verificado (contexto → opciones → decisión → consecuencias → preguntas); formato contrato OpenAPI 3.0.3 verbatim de `D:/Repos/demo-cine/docs/04_arquitectura/contrato_api.yaml`; mecanismo de drift (/docs vs contrato) de ADR-008 demo-cine |
| GUIDE-03 | Las guías de desarrollo son paso a paso — un alumno siguiéndolas construye la app operativa | Estructura de guía demo-cine verificada (🧠 desarrollador piensa → pasos numerados → ✅ mini-verificación → 📝 punto de control); comandos agnósticos de terminal (D-12) validados (npm scripts + uv run); secuencia de sub-guías D-16 |
| STORE-01 | Landing con identidad de marca de la PYME ficticia | Marca/tagline locked (D-01..D-04); hero SPA con Tailwind 4 (setup verificado); persona de Maura para el copy |
| STORE-02 | Catálogo en grilla con filtros por familia aromática y rango de precio | Familia como Enum (4 slugs) + filtros server-side como query params validados con Pydantic; estado de filtros en URL search params de React Router 8 (import surface verificado) |
| STORE-03 | Página de producto con descripción, precio, familia, notas y stock | Modelo `products` extendido (familia + notas JSON list[str]) según specifics del CONTEXT; schemas ProductoResumen/ProductoDetalle estilo demo-cine; precio int CLP + Intl.NumberFormat es-CL (verificado: `$6.990`) |
| STORE-04 | Datos demo sembrados (seed idempotente) re-ejecutable sin duplicar | Patrón seed demo-cine (guía-08) + recomendación upsert por SKU (converge al estado canónico, compatible con FKs de la fase 3); `uv run python -m app.seed` |
</phase_requirements>

## Project Constraints (from AGENTS.md)

No existe `./CLAUDE.md` ni `./.claude/CLAUDE.md` [VERIFIED: ls esta sesión]. Las instrucciones del proyecto viven en `D:/Repos/demo-carro/AGENTS.md` (workspace instructions), que replica PROJECT.md + STACK.md. Directivas accionables:

- **Stack versionado es autoritativo** (sección Technology Stack): React 19.3.0, Vite 8.3.1, TypeScript ~6.0.2 (pin del template — NO subir a 7.0.2 aunque `latest` sea 7.0.2), React Router 8.4.0, @tanstack/react-query 5.104.0, Tailwind 4.3.3, FastAPI 0.141.1, SQLAlchemy 2.1.1, pydantic-settings 2.15.0, SQLite, Python 3.12 (techo por transbank-sdk), Node >= 22.22 o 24.
- **Two tiers estrictamente separados** — sin plantillas en el servidor (Out of Scope de REQUIREMENTS.md).
- **Dos tiers = SPA + API**; SSR/SEO y renderizado de plantillas explícitamente excluidos.
- **What NOT to use** (AGENTS.md): `google-generativeai` (EOL), `python-jose` (CVEs) → PyJWT, `passlib` → pwdlib[argon2] (ambos de fases posteriores, pero los ADRs de fase 1 no deben contradecirlos), Stripe, MySQL, server-side templating.
- **Sin emojis en comunicación con el usuario** (regla del agente; los docs de la guía educativa pueden usar sus propios marcadores al estilo demo-cine 🧠/✅ — es contenido del producto, no comunicación del agente).
- GSD workflow: no editar el repo fuera de un workflow GSD (esta fase ES el workflow).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Landing con identidad de marca (STORE-01) | Browser / Client (SPA) | — | Hero, tagline y copy son render puro del cliente; no hay lógica de servidor |
| Grilla de catálogo + interacción de filtros (STORE-02) | Browser / Client | API / Backend | La UX (chips de familia, sliders/inputs de precio) vive en la SPA; el backend valida y ejecuta el filtrado |
| Filtrado y validación de familia/precio (STORE-02) | API / Backend | — | Contrato API-first: query params validados con Pydantic (Enum + rangos); la SPA nunca filtra datos que no recibió |
| Página de producto (STORE-03) | Browser / Client | API / Backend | Render de ficha en SPA; detalle completo (notas, stock) solo por `GET /api/productos/{id}` |
| Datos demo idempotentes (STORE-04) | API / Backend (script) | Database / Storage | Seed corre contra SQLAlchemy en el tier servidor: `uv run python -m app.seed` |
| Imágenes de producto (D-08) | CDN / Static (Vite `public/`) | — | `frontend/public/products/*.jpg` se sirve estático desde el host del SPA (`/products/...`); el backend solo persiste la ruta |
| Health check + CORS | API / Backend | — | `/api/salud` + CORSMiddleware con orígenes explícitos desde settings |
| ADRs + contrato OpenAPI (GUIDE-02) | Documentación (repo `docs/`) | — | Artefacto de build-time del ciclo de vida; sin tier de runtime |
| Guías paso a paso (GUIDE-03) | Documentación (`docs/05_desarrollo/`) | — | Ídem — el "output" paralelo de la fase |

## Standard Stack

> Fuente base: `.planning/research/STACK.md` (verificado contra registros + docs oficiales el 2026-09-28, mismo día). Los ítems marcados abajo fueron RE-verificados directamente en esta sesión donde se indica.

### Core (instalados en esta fase)

| Library | Version | Purpose | Why Standard | Provenance |
|---------|---------|---------|--------------|------------|
| react / react-dom | 19.3.0 | UI runtime | Template Vite react-ts; satisface peer de RR8 (`>=19.2.7`) | [VERIFIED: npm view esta sesión] |
| vite | 8.3.1 | Dev server + bundler | Estándar SPA 2026; engines `^20.19.0 \|\| >=22.12.0` (22.18 lo cumple) | [VERIFIED: npm view esta sesión] |
| typescript | ~6.0.2 (pin del template) | Tipado frontend (D-09) | El template react-ts lo fija; `latest` es 7.0.2 pero NO subir a ciegas | [VERIFIED: npm view (latest 7.0.2) + STACK: template en main de vitejs/vite] |
| react-router | 8.4.0 | Routing SPA (library mode, BrowserRouter) | v8 elimina react-router-dom; ESM-only; engines `node >=22.22.0` | [VERIFIED: npm view engines + tarball exports, esta sesión] |
| @tanstack/react-query | 5.104.0 | Server state (catálogo) | Cache/invalidación sin fetch manual; quick-start verificado | [VERIFIED: npm view + CITED: tanstack.com/query/latest/docs/framework/react/quick-start] |
| tailwindcss + @tailwindcss/vite | 4.3.3 | Styling (dirección fresco-luminosa D-03) | v4 = plugin de Vite, sin config file ni PostCSS; peer vite `^5.2.0 \|\| ^6 \|\| ^7 \|\| ^8` | [VERIFIED: npm view peerDependencies esta sesión + STACK: tailwindcss.com/docs] |
| fastapi[standard] | 0.141.1 | API REST en capas | Incluye uvicorn[standard], fastapi-cli, httpx, python-multipart, email-validator | [VERIFIED: pypi.org JSON API vía STACK.md 2026-09-28] |
| sqlalchemy | 2.1.1 | ORM (models + repositories) | Declarativo + Session por request | [VERIFIED: pypi.org vía STACK.md 2026-09-28] |
| pydantic-settings | 2.15.0 | Config tipada por env (Settings) | DATABASE_URL, CORS_ORIGINS; sin secretos en código | [VERIFIED: pypi.org vía STACK.md 2026-09-28] |
| SQLite | stdlib 3.12 | DB por defecto | Cero setup, archivo local, camino a Postgres por URL | [CITED: STACK.md → tutorial oficial FastAPI SQL] |
| uv | 0.9.3 (instalado) | Gestor Python (D-10) | Flujo que enseña la doc oficial de FastAPI hoy | [VERIFIED: uv --version esta sesión] |

### Supporting

| Library | Version | Purpose | When to Use | Provenance |
|---------|---------|---------|-------------|------------|
| @vitejs/plugin-react | 6.1.1 | Fast refresh | Siempre (scaffold) | [VERIFIED: npm view esta sesión] |
| oxlint | ^1.85 | Linter frontend | Lo que trae el template — no reemplazar por ESLint | [CITED: STACK.md → template en main de vitejs/vite] |
| pytest | 9.1.1 | Tests backend | Fase 1 NO exige suite (nyquist_validation false); llega en fases posteriores | [VERIFIED: pypi.org vía STACK.md] |
| zustand | 5.0.15 | Client state (carro) | **Diferir a fase 2** — la fase 1 no tiene carro ni estado global real (filtros van en URL) | [VERIFIED: npm view esta sesión; recomendación de diferir es de esta investigación] |
| alembic | 1.20.0 | Migraciones | **Diferir** hasta el primer cambio de schema sobre datos existentes (ver Common Pitfalls #8) | [VERIFIED: pypi.org vía STACK.md; recomendación de diferir es de esta investigación] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| react-router@8.4.0 | react-router@7 (línea mantenida en lockstep) | Solo si el upgrade de Node >= 22.22 se vuelve inviable — pero AGENTS.md fija Node >= 22.22 + RR8, así que 7 es fallback de emergencia, no plan |
| Filtros server-side (query params) | Filtrar client-side los 12 SKU | Client-side es trivial con 12 items, pero no enseña query params/validación Pydantic y el contrato API debe definirlas igual; server-side escala a STORE-05 (búsqueda v2) |
| Seed upsert por SKU | Insert-only si vacío (patrón demo-cine guía-08) | Insert-only es más simple pero no actualiza datos demo si el seed evoluciona; upsert converge siempre al estado canónico |
| `Base.metadata.create_all` | Alembic desde la fase 1 | Alembin añade pasos a las primeras guías; con seed idempotente y DB desechable, create_all basta hasta que un cambio de schema toque datos existentes |

**Installation (comandos de la guía — agnósticos de terminal, D-12):**

```bash
# Frontend (desde la raíz del monorepo)
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install react-router @tanstack/react-query
npm install tailwindcss @tailwindcss/vite

# Backend (desde la raíz del monorepo) — --vcs none evita el .git anidado (ver Pitfall 2)
uv init backend --vcs none --app
cd backend
uv add "fastapi[standard]" sqlalchemy pydantic-settings
uv run fastapi dev app/main.py
```

## Package Legitimacy Audit

> El seam `package-legitimacy check` retornó salida vacía para todos los paquetes en este ambiente (artefacto ya documentado en STACK.md para `fastapi`). Se aplicó el fallback del protocolo: verificación directa de registro (npm view / pypi.org vía STACK mismo día) + chequeo de scripts postinstall.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| react / react-dom | npm | ~12 años | ~30M/sem | github.com/facebook/react | OK (fallback) | Approved |
| vite | npm | ~7 años | ~15M/sem | github.com/vitejs/vite | OK (fallback) | Approved |
| react-router | npm | ~10 años | ~14M/sem | github.com/remix-run/react-router | OK (fallback) | Approved |
| @tanstack/react-query | npm | ~6 años | ~3M/sem | github.com/TanStack/query | OK (fallback) | Approved |
| tailwindcss + @tailwindcss/vite | npm | ~7 años | ~12M/sem | github.com/tailwindlabs/tailwindcss | OK (fallback) | Approved |
| typescript | npm | ~12 años | ~50M/sem | github.com/microsoft/TypeScript | OK (fallback) | Approved |
| @vitejs/plugin-react | npm | ~6 años | ~12M/sem | github.com/vitejs/vitejs-plugin-react | OK (fallback) | Approved |
| fastapi[standard] / sqlalchemy / pydantic-settings | pypi | 6-15 años | 10-100M/mes | tiangolo / sqlalchemy / pydantic | OK (fallback) | Approved |

**Chequeo postinstall (protocolo paso 3):** ningún paquete npm listado define `scripts.postinstall` [VERIFIED: npm view scripts.postinstall por paquete, esta sesión — salida vacía para todos].

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

*Nota de edad/downloads: cifras aproximadas de conocimiento de ecosistema [ASSUMED]; la verificación primaria de esta auditoría es la existencia en registro con la versión actual + repo oficial + docs oficiales cruzadas en STACK.md (mismo día).*

## Architecture Patterns

### System Architecture Diagram

```
                        FLUJO PRINCIPAL DE LA FASE 1 (visitante → catálogo)
                        ═════════════════════════════════════════════════

  [Visitante] ── navega a localhost:5173 ──► ┌───────── NAVEGADOR ─────────┐
                                             │  SPA React 19 + TS          │
                                             │  BrowserRouter (RR8)        │
                                             │   /            landing      │
                                             │   /productos   grilla+filtros
                                             │   /productos/:id  ficha    │
                                             │  TanStack Query (cache)    │
                                             │  Tailwind 4                │
                                             └──────┬──────────────────────┘
                                                    │ fetch /api/productos?...
                                                    │ (relativa → Vite proxy en dev)
  [Imágenes /products/*.jpg] ◄── estático desde ──  │
  (Vite public/, mismo host SPA)                    ▼
                                             ┌───────── VITE DEV SERVER ───┐
                                             │  proxy: '/api' →            │
                                             │  http://localhost:8000      │
                                             └──────┬──────────────────────┘
                                                    │ HTTP (mismo origen en dev;
                                                    │ CORS explícito si cross-origin)
                                                    ▼
  [uv run fastapi dev] ────────────────────► ┌───────── API FASTAPI (capas)┐
  [uv run python -m app.seed] ── sembrar ──► │  routers/   validación HTTP │
  (upsert por SKU, idempotente)              │  services/  casos de uso    │
                                             │  repositories/ SQL          │
                                             │  schemas/  Pydantic         │
                                             │  models/   SQLAlchemy       │
                                             └──────┬──────────────────────┘
                                                    │ SQLAlchemy 2.1 (Session/req)
                                                    ▼
                                             ┌───────── SQLite ────────────┐
                                             │  productos (12 SKU seed)    │
                                             │  familia ENUM · notas JSON  │
                                             └─────────────────────────────┘

  PARALELO (API-first, D-15):
  docs/04_arquitectura/contrato_api.yaml ──(se aprueba ANTES)──► código FastAPI
  verificación de cierre: /docs generado ≈ contrato (mecanismo ADR-008 demo-cine)
```

### Recommended Project Structure

```
demo-carro/
├── docs/                              # D-13: replica demo-cine, se escribe POR FASE
│   ├── README.md                      # tabla de fases del ciclo con estado + regla
│   ├── 01_necesidad_del_cliente.md    # Maura (persona D-02, dolores, peticiones P, CS)
│   ├── 02_requerimientos.md           # RF/RN de la fase, trazables a REQUIREMENTS.md
│   ├── 03_diseno.md                   # entidad PRODUCTO + pantallas landing/grilla/ficha
│   ├── 04_arquitectura/
│   │   ├── README.md                  # arquitectura en una página + índice ADRs
│   │   ├── adr/                       # 001..00N (capas, dos tiers, monorepo, TS,
│   │   │                              #   SQLite, uv, API-first)
│   │   └── contrato_api.yaml          # OpenAPI 3.0.3 API-first (D-15)
│   └── 05_desarrollo/
│       ├── README.md                  # tabla de guías con estado
│       ├── guia-01-*.md               # proyecto backend (uv init → health)
│       ├── guia-02-*.md               # proyecto frontend (vite → tailwind → router)
│       ├── guia-03-*.md               # modelos + seed idempotente
│       └── guia-04-*.md               # catálogo: API productos + landing/grilla/ficha
├── backend/
│   ├── pyproject.toml                 # uv; requires-python ">=3.12,<3.13"
│   ├── uv.lock
│   ├── .python-version                # 3.12
│   └── app/
│       ├── __init__.py
│       ├── main.py                    # FastAPI() + CORS + include_router(prefix="/api")
│       ├── config.py                  # Settings (pydantic-settings): DATABASE_URL, CORS_ORIGINS
│       ├── database.py                # engine, SessionLocal, Base, get_session
│       ├── models/producto.py         # SQLAlchemy (familia Enum, notas JSON)
│       ├── schemas/producto.py        # Pydantic: ProductoResumen / ProductoDetalle / query params
│       ├── repositories/producto.py   # select + filtros
│       ├── services/catalogo.py       # reglas de listado/detalle
│       ├── routers/productos.py       # GET /api/productos, GET /api/productos/{id}
│       ├── routers/salud.py           # GET /api/salud
│       └── seed.py                    # uv run python -m app.seed (upsert por SKU)
└── frontend/
    ├── public/products/               # 12 fotos stock (D-08): {sku}.jpg
    ├── src/
    │   ├── main.tsx                   # BrowserRouter + QueryClientProvider
    │   ├── index.css                  # @import "tailwindcss";
    │   ├── lib/api.ts                 # único punto HTTP + tipos que espejan schemas
    │   ├── types/api.ts               # interfaces TS = contrato (D-09)
    │   ├── features/
    │   │   ├── landing/               # hero marca + tagline (STORE-01)
    │   │   └── catalogo/              # grilla, ProductCard, filtros, ficha (STORE-02/03)
    │   └── components/                # Navbar, Footer, layout compartido
    └── vite.config.ts                 # react() + tailwindcss() + server.proxy /api
```

*Nota: `features/landing` vs `features/catalogo` es ajustable (discretion); lo innegociable es `lib/api.ts` como único punto de salida HTTP y features por dominio (ARCHITECTURE.md).*

### Pattern 1: Backend en capas con DI de FastAPI (objetivo pedagógico declarado)

**Qué:** routers validan HTTP y delegan → services deciden → repositories tocan SQLAlchemy. Conexión solo con `Depends`.

```python
# Source: patrón .planning/research/ARCHITECTURE.md (Pattern 1) + demo-cine 04_arquitectura §4
# app/routers/productos.py — el router no sabe cómo se persiste
@router.get("", response_model=list[ProductoResumen])
def listar_productos(
    familia: FamiliaAromatica | None = None,
    precio_min: int | None = Query(default=None, ge=0),
    precio_max: int | None = Query(default=None, ge=0),
    db: Session = Depends(get_session),
):
    return CatalogService(ProductoRepository(db)).listar(
        familia=familia, precio_min=precio_min, precio_max=precio_max
    )
```

**Reglas de dependencia verificables** (espejo de demo-cine §4): `routers/` nunca importa SQLAlchemy; `repositories/` nunca decide reglas; solo `main.py` arma la app.

### Pattern 2: Enum de familia con slugs ASCII (evita el gotcha de Enum de SQLAlchemy)

**Qué:** la API y la BD guardan slugs (`citricas`, `florales`, `frutales`, `dulces`); la SPA mapea slug → etiqueta con acento ("Cítricas"). `Enum` de SQLAlchemy persiste NOMBRES de miembros [CITED: docs.sqlalchemy.org/en/20/core/type_basics.html — "the enum's member names are persisted"], así que los miembros se declaran con nombre = valor:

```python
# Source: verificación docs.sqlalchemy.org (esta sesión) — member names son lo persistido
import enum

class FamiliaAromatica(str, enum.Enum):
    citricas = "citricas"    # nombre == valor: la BD guarda "citricas",
    florales = "florales"    # la API devuelve "citricas", sin values_callable
    frutales = "frutales"
    dulces = "dulces"

# app/models/producto.py
class Producto(Base):
    __tablename__ = "productos"
    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120))
    descripcion: Mapped[str] = mapped_column(Text)
    precio: Mapped[int] = mapped_column(Integer)          # CLP entero, sin decimales
    stock: Mapped[int] = mapped_column(Integer, default=0)
    familia: Mapped[FamiliaAromatica] = mapped_column(Enum(FamiliaAromatica))
    notas: Mapped[list[str]] = mapped_column(JSON, default=list)  # ["bergamota", "limón"]
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    imagen: Mapped[str] = mapped_column(String(200))      # "/products/citricas-01.jpg"
```

`sqlalchemy.JSON` y `sqlalchemy.Enum` existen como tipos genéricos multi-vendor y funcionan sobre SQLite (JSON se guarda como texto; Enum degrada a VARCHAR sin ENUM nativo) [CITED: docs.sqlalchemy.org/en/20/core/type_basics.html].

### Pattern 3: Frontend tipado de punta a punta (D-09)

**Qué:** el contrato YAML define los schemas → Pydantic los implementa → TS los espeja a mano (el espejo manual ES el ejercicio pedagógico; no hay codegen).

```typescript
// src/types/api.ts — espeja ProductoResumen/ProductoDetalle del contrato
export type Familia = "citricas" | "florales" | "frutales" | "dulces";

export interface ProductoResumen {
  id: number;
  sku: string;
  nombre: string;
  precio: number;       // CLP entero
  familia: Familia;
  imagen: string;       // "/products/citricas-01.jpg"
}

export interface ProductoDetalle extends ProductoResumen {
  descripcion: string;
  notas: string[];
  stock: number;
}

export const FAMILIA_LABELS: Record<Familia, string> = {
  citricas: "Cítricas",
  florales: "Florales",
  frutales: "Frutales",
  dulces: "Dulces",
};
```

Imports de React Router 8 (v8 elimina `react-router-dom`; `BrowserRouter` sale del paquete principal, NO de `react-router/dom` que solo tiene `RouterProvider`/`HydratedRouter` de data mode) [VERIFIED: tarball react-router@8.4.0 — `dist/production/dom-export.js` exporta únicamente `HydratedRouter, RouterProvider, unstable_RSCHydratedRouter, unstable_createCallServer, unstable_getRSCStream`; `index.d.ts` principal declara `BrowserRouter`]:

```tsx
// src/main.tsx — library mode + TanStack Query
import { BrowserRouter, Routes, Route } from "react-router";  // NO "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient();

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/productos" element={<Catalogo />} />
          <Route path="/productos/:id" element={<FichaProducto />} />
          <Route path="*" element={<NoEncontrado />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>
);
```

Setup de TanStack Query verificado: `new QueryClient()` + `QueryClientProvider` en la raíz + `useQuery({ queryKey, queryFn })` [CITED: tanstack.com/query/latest/docs/framework/react/quick-start].

### Pattern 4: Proxy de Vite en dev + CORS explícito

```ts
// frontend/vite.config.ts
// Source: vite.dev/config/server-options (verificado esta sesión)
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: { "/api": "http://localhost:8000" },  // shorthand; changeOrigin no hace falta mismo-origen localhost
  },
});
```

```python
# app/main.py — CORS con orígenes explícitos desde settings (nunca ["*"] con credentials)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,      # ["http://localhost:5173", "<prod>"]
    allow_methods=["GET"],
    allow_headers=["*"],
)
```

El API client usa URL relativa en dev (el proxy hace same-origin) y `VITE_API_URL` en producción: `const base = import.meta.env.VITE_API_URL ?? ""`.

### Pattern 5: Seed idempotente por upsert de SKU

```python
# app/seed.py — re-ejecutable sin duplicar (STORE-04); converge al estado canónico
# Source: patrón demo-cine guia-08 (guardas idempotentes) + extensión upsert de esta investigación
def upsert_producto(sesion: Session, datos: dict) -> str:
    existente = sesion.scalar(select(Producto).where(Producto.sku == datos["sku"]))
    if existente is None:
        sesion.add(Producto(**datos))
        return "[+]"
    for campo, valor in datos.items():
        setattr(existente, campo, valor)   # actualiza precios/stock al valor canónico
    return "[=]"
```

Se ejecuta con `uv run python -m app.seed` (agnóstico de terminal). Re-ejecutar tras pruebas de UAT **restaura** stock y precios demo — deseable para reproducibilidad; documentarlo en la guía.

### Pattern 6: Docs del ciclo replicando demo-cine (D-13/D-14)

Estructura verificada leyendo `D:/Repos/demo-cine/docs/` esta sesión:

- `README.md`: tabla de 8 fases del ciclo con columna Estado (✅ Listo) + "Regla del proyecto: ninguna fase se escribe sin aprobar la anterior" [VERIFIED: D:/Repos/demo-cine/docs/README.md:9-22].
- `01_necesidad_del_cliente.md`: habla "idioma del CLIENTE, cero tecnología"; secciones: el cliente, situación actual, dolores (D1..), peticiones del cliente (P1..) con cita textual, objetivos, lo que NO pide, condiciones (C1..), criterios de éxito (CS1..), aprobación con firmas [VERIFIED: D:/Repos/demo-cine/docs/01_necesidad_del_cliente.md:1-107].
- `04_arquitectura/README.md`: "arquitectura en una página" + tabla diseño→arquitectura + stack con porqué + organización de carpetas con reglas de dependencia + índice de ADRs + sección API-first + aprobación [VERIFIED: D:/Repos/demo-cine/docs/04_arquitectura/README.md].
- ADRs: formato Estado/Fecha/Resuelve → Contexto → Opciones consideradas (tabla a favor/en contra) → Decisión → Consecuencias (positivas/negativas) → Para conversar en clase [VERIFIED: D:/Repos/demo-cine/docs/04_arquitectura/adr/008-api-first.md].
- `contrato_api.yaml`: `openapi: 3.0.3`, header con comentario de regencia API-first, info con convención de errores (400/401/403/404/409/422), servers dev/prod, tags, components.schemas (Error + Resumen/Detalle con allOf), paths con descripciones que citan RF/RN [VERIFIED: D:/Repos/demo-cine/docs/04_arquitectura/contrato_api.yaml:1-60].
- `05_desarrollo/README.md`: tabla de guías + "mapa mental de la serie"; cada guía: "> Qué construirás hoy / Al terminar tendrás / Necesitas", tabla de términos, pasos con 🧠 "El desarrollador piensa", ✅ mini-verificación por paso, 📝 punto de control, "Lo que acabas de aprender" [VERIFIED: D:/Repos/demo-cine/docs/05_desarrollo/guia-01-esqueleto.md:1-120 y README.md].
- Diferencia carro vs cine (D-13): los docs se escriben POR FASE GSD conforme la app se construye — la tabla del README avanza con las fases (en fase 1: 01–04 ✅, 05 parcial, 06–08 pendientes).

### Anti-Patterns to Avoid

- **`return_url`/lógica de pago en la SPA** — fase 1 no tiene pago, pero los ADRs fundacionales ya deben fijar que el SDK/keys viven solo en el backend (ANTI-Pattern 1 de ARCHITECTURE.md).
- **CORS comodín** (`allow_origins=["*"]`) — usar lista explícita desde settings [CITED: ARCHITECTURE.md anti-pattern 3 ← fastapi.tiangolo.com/tutorial/cors].
- **`createBrowserRouter` (data mode)** — el architecture research lo menciona, pero STACK.md fija **library mode (BrowserRouter)** para esta SPA; seguir STACK (más reciente y específico).
- **`react-router-dom`** — eliminado en v8; cualquier import de él rompe el build [VERIFIED: tarball + reactrouter.com/upgrading/v7].
- **Precio float** — CLP no usa decimales en la práctica; `Integer` evita errores de coma flotante y el formateo es `Intl.NumberFormat`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Validación de query params (familia, rangos de precio) | if/else manuales por parámetro | Pydantic `Enum` + `Query(ge=..., le=...)` | 422 automático coherente con el contrato; cero código de validación |
| Fetch + cache + loading/error del catálogo | `useEffect` + `useState` + flags | TanStack Query `useQuery` | Cache, reintentos y estados de carga gratis; patrón que las fases 2-4 reutilizan |
| Routing SPA | window.location /.history manual | React Router 8 (library mode) | Rutas anidadas, `useSearchParams` para filtros compartibles, 404 |
| Formateo de precios CLP | `toLocaleString` custom / concatenar "$" + puntos | `Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP" })` | Verificado esta sesión: produce `"$6.990"` [VERIFIED: node, esta sesión] |
| SQL del catálogo | strings SQL concatenadas | SQLAlchemy select + repositories | Parameterizado (SQLi imposible por construcción); filtros componibles |
| CSS del sistema de diseño | CSS custom global | Tailwind 4 via `@tailwindcss/vite` | Sin config file en v4; la paleta concreta la formaliza `/gsd:ui-phase` |
| Documentación de la API | prosa o /docs como fuente | `contrato_api.yaml` OpenAPI manual (D-15) | El contrato es la fuente de la verdad ANTES del código; /docs se compara contra él |

**Key insight:** el producto educativo ES la metodología — cada "no lo hagas a mano" es también una lección de la guía (API-first, validación declarativa, server state vs client state).

## Common Pitfalls

### Pitfall 1: Node 22.18 no satisface react-router 8 (BLOQUEANTE)
**What goes wrong:** `npm install` de react-router@8.4.0 emite EBADENGINE (engines `node >=22.22.0`) y el stack bloqueado no se cumple.
**Why:** el ambiente tiene Node v22.18.0 [VERIFIED: node --version esta sesión]; Vite 8 sí acepta 22.12+, el router es la restricción que ata.
**How to avoid:** paso inicial del plan: upgrade de Node a >= 22.22 (o 24 LTS) y verificación `node -v`. Agregar `checkpoint:human-verify` si el upgrade requiere acción del usuario.
**Warning signs:** warnings EBADENGINE en npm install; `npm ls react-router` con invalid.

### Pitfall 2: `uv init` crea un repo git anidado
**What goes wrong:** `uv init backend` ejecuta `git init` interno [VERIFIED: ejecución en temp esta sesión — crea `.git`, `main.py`, `pyproject.toml`, `.python-version`, `README.md`, `.gitignore`]; el `backend/.git` convierte el directorio en repositorio embebido y el repo padre deja de trackear sus archivos.
**How to avoid:** `uv init backend --vcs none` [VERIFIED: uv init --help documenta `--vcs <git|none>` esta sesión]. Borrar también el `main.py` hello-world que genera.
**Warning signs:** `git status` en la raíz muestra `backend/` sin contenido detallable.

### Pitfall 3: `requires-python = ">=3.12"` permite 3.13/3.14
**What goes wrong:** uv genera `requires-python = ">=3.12"` [VERIFIED: pyproject generado en temp esta sesión]; en otra máquina uv puede resolver Python 3.13/3.14, que exceden el techo de classifiers de transbank-sdk (fase 3).
**How to avoid:** editar a `requires-python = ">=3.12,<3.13"` (constraint presente que acota todos los valores) + `.python-version` = 3.12 (uv lo crea con 3.12 aquí, pero fijarlo explícito).

### Pitfall 4: Enum persiste NOMBRES, no valores
**What goes wrong:** `class Familia(str, enum.Enum): citricas = "citricas"` funciona, pero si los miembros se llaman `CITRICAS = "citricas"`, la BD guarda "CITRICAS" y el contrato (slugs lowercase) diverge.
**Why:** documentado: "the enum's member names are persisted" [CITED: docs.sqlalchemy.org/en/20/core/type_basics.html].
**How to avoid:** miembros con nombre == slug (Pattern 2); mini-verificación en la guía: re-ejecutar seed y hacer GET comprobando `"familia": "citricas"`.

### Pitfall 5: Acentos en query params
**What goes wrong:** filtrar por `?familia=Cítricas` exige URL-encoding del acento y acopla el contrato a la ortografía con tilde.
**How to avoid:** slugs ASCII en API/BD (`citricas`) + mapa de etiquetas en la SPA ("Cítricas"). La verificación STORE-01/02 muestra la etiqueta; el cable trasmite el slug.

### Pitfall 6: seed con DELETE FROM + reinsert
**What goes wrong:** borrar y reinsertar romperá las FK de `order_items` → `products` cuando llegue la fase 3; además reinicia los IDs.
**How to avoid:** upsert por SKU (Pattern 5) desde el día 1 — única clave natural estable del demo.

### Pitfall 7: CORS comodín o CORS ausente "porque el proxy lo arregla"
**What goes wrong:** en dev con proxy no se nota; al desplegar (fase 5) o al probar el backend en otro origen, todo falla de forma confusa.
**How to avoid:** CORSMiddleware desde la guía 1 con `allow_origins` desde Settings (`cors_origins`), lista explícita dev + placeholder prod.

### Pitfall 8: `create_all` no altera tablas existentes
**What goes wrong:** si en fases posteriores se cambia una columna de `productos`, `Base.metadata.create_all` no la aplica sobre una DB ya creada.
**How to avoid:** decisión consciente documentada en el ADR de SQLite: fase 1 usa create_all + seed idempotente (DB desechable); Alembic entra cuando el primer cambio de schema toque datos existentes. Las guías lo dicen explícito para no "aprenderlo mal".

### Pitfall 9: TypeScript 7.0.2 por `npm install typescript@latest`
**What goes wrong:** subir TS a 7.x (native port reciente) desalinea el proyecto del template validado (~6.0.2).
**How to avoid:** quedarse con el pin del scaffold react-ts; los ADRs/documentos de la guía no mencionan instalar TS aparte.

### Pitfall 10: hotlinks a imágenes externas
**What goes wrong:** URLs de Unsplash en el seed rompen la demo si el servicio cae o cambia; además D-08 lo prohíbe.
**How to avoid:** fotos descargadas a `frontend/public/products/` (rutas `/products/{sku}.jpg` en el seed); Vite las sirve en dev y las copia al build.

## Code Examples

### Contrato OpenAPI inicial (formato demo-cine, esqueleto)

```yaml
# Source: formato verbatim verificado en D:/Repos/demo-cine/docs/04_arquitectura/contrato_api.yaml
openapi: 3.0.3
info:
  title: Maura API
  version: 0.1.0
  description: |
    API de la tienda Maura · Body Splash. Contrato API-first (ADR-007):
    fuente de la verdad de la interfaz, se aprueba antes de codificar.
paths:
  /api/salud:
    get:
      tags: [Operación]
      summary: Chequeo de vida del servicio
      responses:
        '200': { description: Servicio arriba }
  /api/productos:
    get:
      tags: [Productos]
      summary: Listar el catálogo con filtros
      parameters:
        - name: familia
          in: query
          schema: { type: string, enum: [citricas, florales, frutales, dulces] }
        - name: precio_min
          in: query
          schema: { type: integer, minimum: 0 }
        - name: precio_max
          in: query
          schema: { type: integer, minimum: 0 }
      responses:
        '200':
          description: Productos activos que cumplen los filtros
          content:
            application/json:
              schema:
                type: array
                items: { $ref: '#/components/schemas/ProductoResumen' }
        '422': { description: Filtro mal formado }
  /api/productos/{producto_id}:
    get:
      tags: [Productos]
      summary: Ficha del producto
      parameters:
        - name: producto_id
          in: path
          required: true
          schema: { type: integer }
      responses:
        '200':
          description: El detalle
          content:
            application/json:
              schema: { $ref: '#/components/schemas/ProductoDetalle' }
        '404': { description: Producto inexistente }
# + components.schemas: Error, ProductoResumen (id, sku, nombre, precio,
#   familia, imagen), ProductoDetalle (allOf Resumen + descripcion, notas[], stock, activo)
```

### Filtros en URL search params (compartibles)

```tsx
// Source: patrón React Router library mode (useSearchParams) — API estable v6→v8
const [params, setParams] = useSearchParams();
const familia = params.get("familia") ?? "";
const query = useQuery({
  queryKey: ["productos", familia, params.get("precio_min"), params.get("precio_max")],
  queryFn: () =>
    apiGet<ProductoResumen[]>(
      `/api/productos?${new URLSearchParams(
        Object.fromEntries([...params].filter(([, v]) => v !== ""))
      )}`
    ),
});
```

### Precio CLP

```typescript
// Source: verificado por ejecución esta sesión (node): produce "$6.990"
const clp = new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP" });
clp.format(6990); // "$6.990"  — render en grilla y ficha
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `react-router-dom` como paquete de import | Eliminado; todo desde `react-router`, data-mode DOM desde `react-router/dom` | v8.0.0 (2026-06-17) | Los imports de la guía son `from "react-router"` [VERIFIED: tarball + changelog vía STACK] |
| Tailwind con `tailwind.config.js` + PostCSS | Plugin `@tailwindcss/vite` + `@import "tailwindcss"` | v4 | Cero config en fase 1 [CITED: STACK → tailwindcss.com/docs] |
| pip + venv + requirements.txt | uv (pyproject + uv.lock) | doc oficial FastAPI enseña uv-first hoy | D-10 ya lo fija; `uv init --vcs none` en monorepo |
| ESLint en el scaffold Vite | oxlint (default del template) | template actual | No pelear con el scaffold; lint corre con lo que trae |
| Fetch manual con useEffect | TanStack Query para server state | consenso 2026 | Catalogo con cache/loading gratis desde fase 1 |

**Deprecated/outdated:**
- `react-router-dom` (v8 lo elimina) — [VERIFIED].
- `google-generativeai`, `python-jose`, `passlib` — irrelevantes en fase 1 pero los ADRs no deben introductirlos (What NOT to Use de AGENTS.md).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Nombres de campos/rutas de la API en español (`/api/productos`, `nombre`, `precio`) por consistencia con demo-cine | Contrato, Patterns | Bajo — cosmético, reversible antes del freeze del contrato; confirmar en plan |
| A2 | Familia como slug ASCII en API/BD + etiquetas en frontend | Pattern 2, Pitfall 5 | Bajo — es la recomendación técnica; la alternativa (con acentos) solo complica encoding |
| A3 | `notas` como `list[str]` (columna JSON) | Modelo, Pattern 2 | Bajo — si se prefiere string plano, cambia schema TS/Pydantic pero no el alcance |
| A4 | Precio como Integer CLP sin decimales | Modelo | Bajo — CLP real no usa decimales; float sería el error |
| A5 | Filtros server-side vía query params (no client-side) | Contrato, STORE-02 | Medio — si el planner prefiere client-side, el contrato se simplifica pero se pierde la lección de query params; decidir en plan |
| A6 | Estado de filtros en URL search params de la SPA | Patterns | Bajo — alternativa: estado local simple |
| A7 | Seed upsert por SKU (vs insert-only demo-cine) | Pattern 5, STORE-04 | Bajo — ambos cumplen "re-ejecutable sin duplicar"; upsert además converge al canónico |
| A8 | create_all en fase 1; Alembic diferido al primer cambio de schema con datos | Stack, Pitfall 8 | Medio — decisión de ADR; si el curso exige Alembic desde ya, la guía 01 backend crece ~1 paso |
| A9 | Zustand diferido a fase 2 (fase 1 no tiene estado global) | Stack | Bajo — instalarlo ahora es inofensivo pero innecesario |
| A10 | Endpoint de salud `/api/salud` (español, estilo demo-cine) | Contrato | Bajo — nombre libre |
| A11 | Licencias Unsplash/Pexels permiten uso libre sin atribución obligatoria | STORE-04, imágenes | Bajo — conocimiento de ecosistema; la guía igual puede citar fuentes por buena práctica |
| A12 | Las 12 URLs concretas de fotos stock se seleccionan en tiempo de ejecución (consistencia visual por familia, D-08) | STORE-04 | Medio — necesita búsqueda/selección manual en ejecución; el repo debe commitear las imágenes |
| A13 | `npm create vite@latest frontend -- --template react-ts` escribe el scaffold dentro de `frontend/` en el monorepo existente | Installation | Bajo — comportamiento estándar de create-vite; verificar al ejecutar |

## Open Questions (RESOLVED)

> Todas las preguntas abiertas quedaron resueltas por los planes de la fase 1. Resolución inline citando plan/tarea.

1. **¿Cómo se resuelve el upgrade de Node a >= 22.22?**
   - What we know: Node v22.18.0 instalado; react-router 8 exige >= 22.22; el stack del proyecto fija Node >= 22.22 o 24.
   - What's unclear: quién/cómo actualiza Node en la máquina del usuario (nvm-windows, instalador MSI, etc.).
   - Recommendation: el plan abre con un `checkpoint:human-verify` o tarea explícita de upgrade + `node -v` como gate antes de cualquier `npm install` del frontend.
   - **RESOLVED (replan D-17) en 01-04 Task 3:** el gate Node >= 22.22 NO es un checkpoint del pipeline — bajo D-17 este repo jamás ejecuta npm; es el paso 1 de guia-02 como prerrequisito en prosa que el ALUMNO verifica (`node -v` >= 22.22 antes del primer comando npm, con guía de upgrade MSI/nvm-windows). [Supera la resolución anterior del replan pre-D-17: `checkpoint:human-action` en 01-03 Task 1.]
2. **¿Qué ADRs exactos se numeran en la fase 1?**
   - What we know: candidatos naturales listados en CONTEXT (stack, capas, SQLite, TypeScript, uv, monorepo, API-first) — es discretion.
   - Recommendation: 7 ADRs (001 capas, 002 dos tiers SPA+API, 003 monorepo, 004 TypeScript, 005 SQLite+SQLAlchemy, 006 uv, 007 API-first); el planner ajusta numeración y si separa el stack frontend.
   - **RESOLVED (replan D-17) en 01-03 (Tasks 2-3):** 8 ADRs numerados 001-008 — los 7 de la recomendación (001 capas, 002 dos tiers SPA+API, 003 monorepo, 004 TypeScript, 005 SQLite+create_all, 006 uv, 007 API-first) más 008 repositorio-solo-guias (guide-only, D-17/D-18). [Supera la resolución anterior del replan pre-D-17: exactamente 7 ADRs en 01-04.]
3. **¿La landing incluye ya sección de "sobre Maura" con la persona?**
   - What we know: STORE-01 pide identidad de marca; D-02 fija persona breve para docs/narrativa.
   - Recommendation: hero (marca + tagline) + bloque breve con la persona; la paleta concreta la formaliza `/gsd:ui-phase` (D-03) — coordinar que esta fase deja la estructura CSS lista.
   - **RESOLVED (replan D-17) en 01-04 Task 3:** guia-02 enseña al alumno a construir la landing — hero (eyebrow "Maura · Body Splash" + tagline D-04) con el párrafo de persona en primera persona según los copies del UI-SPEC (contrato UI ya formalizado en 01-UI-SPEC.md), más la sección "Nuestras familias"; la construcción vive en la máquina del alumno. [Supera la resolución anterior del replan pre-D-17: landing implementada en 01-03 Task 3.]
4. **¿Volúmenes de stock en el seed?**
   - What we know: discretion; sugerencia: valores variados incluyendo 1-2 productos con stock bajo (prepara la alerta ADMN-02 de fase 4) y ninguno en 0 (la ficha debe mostrar disponibilidad).
   - **RESOLVED en 01-01 Task 3:** stock exactos fijados en el seed (14, 9, 3, 11, 7, 2, 16, 8, 5, 6, 12, 10) — exactamente 2 productos con stock bajo (citricas-03 = 3, florales-03 = 2) y ninguno en 0.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js >= 22.22 | React Router 8 (engines), stack bloqueado | ✗ (hay 22.18.0) | v22.18.0 | Upgrade a >= 22.22 / Node 24 — **sin fallback real** (RR7 solo como emergencia) |
| npm | toolchain frontend | ✓ | 11.16.0 | — |
| Python 3.12 | backend (techo transbank-sdk) | ✓ | 3.12.10 | — |
| uv | D-10 workflow backend | ✓ | 0.9.3 | — |
| git | commits del repo | ✓ | 2.50.1.windows.1 | — |
| Puertos 5173 / 8000 | vite dev / fastapi dev | ✓ libres | — | Cambiar puertos si se ocupan al ejecutar |
| Acceso red (npm registry / pypi) | instalaciones | ✓ (npm view operó esta sesión) | — | — |

**Missing dependencies with no fallback:**
- Node >= 22.22 — bloqueante para react-router@8.4.0 según engines y según el stack fijado en AGENTS.md. El plan debe gatearlo (checkpoint o tarea de upgrade) ANTES del scaffold frontend.

**Missing dependencies with fallback:**
- Ninguno adicional.

*(Step 2.5 Runtime State Inventory: OMITIDO — fase greenfield, no rename/refactor/migration.)*
*(Step 2.6: completado arriba.)*
*(Validation Architecture: OMITIDA — `workflow.nyquist_validation: false` explícito en .planning/config.json.)*

## Security Domain

> `security_enforcement: true`, `security_asvs_level: 1`, `security_block_on: high` [VERIFIED: .planning/config.json:48-50 leído esta sesión]. Fase 1 = API pública de solo lectura + SPA estática: superficie mínima.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Fase 1 no tiene cuentas (llegan en fase 2); los ADRs dejan constancia |
| V3 Session Management | no | Sin sesiones |
| V4 Access Control | no (parcial) | Solo endpoints públicos; sin recursos protegidos aún |
| V5 Input Validation | **yes** | Pydantic en la frontera: `familia` como Enum (rechaza valores fuera de la lista), `precio_min/max` con `ge=0`, `producto_id` int — 422 automático; SQLAlchemy parameteriza todo (sin SQLi por construcción) |
| V6 Cryptography | no | Sin secretos ni hash en fase 1 (pydantic-settings establece el patrón para fases 2+) |
| V14 Configuration | **yes** | CORS con orígenes explícitos desde Settings; sin datos sensibles en el repo; `.env` fuera de git (uv crea .gitignore que lo incluye) |

### Known Threat Patterns for SPA + FastAPI pública

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| SQL injection vía filtros | Tampering | SQLAlchemy select parameterizado; jamás string SQL |
| XSS vía datos del catálogo | Tampering/Spoofing | React escapa por defecto; prohibir `dangerouslySetInnerHTML`; los datos vienen solo del seed |
| Abuso de query params (rangos absurdos, familia inválida) | DoS/Tampering | Validación Pydantic con Enum + `ge/le`; respuesta 422 acotada |
| CORS mal configurado que habilita lectura cross-origin de la API futura | Information Disclosure | Lista explícita de orígenes desde settings desde la guía 1 (nunca `["*"]`) |
| Ruta de imagen manipulable | Tampering | `imagen` es una ruta estática sembrada por el seed (no input del usuario); el host estático la sirve como-está |

## Sources

### Primary (HIGH confidence)
- Registro npm (npm view, esta sesión 2026-09-28): react/react-dom 19.3.0, vite 8.3.1 (+engines), react-router 8.4.0 (+engines `>=22.22.0`, +export map del tarball), @tanstack/react-query 5.104.0, tailwindcss + @tailwindcss/vite 4.3.3 (+peer vite `^\|8`), typescript 7.0.2 latest (pin template ~6.0.2), @vitejs/plugin-react 6.1.1, create-vite 9.2.1; sin postinstall en ninguno.
- Ejecuciones locales (esta sesión): `node --version` (22.18.0), `python --version` (3.12.10), `uv --version` (0.9.3), `uv init` en temp (layout + `.git` interno + `--vcs none`), `Intl.NumberFormat es-CL CLP` → `$6.990`.
- `.planning/research/STACK.md` (2026-09-28, mismo día) — verificación pypi.org + docs oficiales de fastapi/tailwind/react-router/transbank/google-genai; esta investigación hereda sus tags HIGH.
- `.planning/research/ARCHITECTURE.md` (2026-09-28) — capas, estructura monorepo, anti-patterns CORS.
- `D:/Repos/demo-cine/docs/` — README, 01_necesidad, 04_arquitectura (README + ADR-008 + contrato_api.yaml), 05_desarrollo (README + guia-01 + guia-08) leídos íntegros esta sesión: formato canónico de la guía (D-13).

### Secondary (MEDIUM confidence)
- vite.dev/config/server-options — proxy `/api` con shorthand y `changeOrigin` [CITED].
- tanstack.com/query/latest/docs/framework/react/quick-start — QueryClient + QueryClientProvider + useQuery [CITED].
- docs.sqlalchemy.org/en/20/core/type_basics.html — tipos `JSON` y `Enum`; Enum persiste member names [CITED].
- reactrouter.com/upgrading/v7 — eliminación de react-router-dom en v8 [CITED] (detalle fino de exports confirmado por tarball, primario).

### Tertiary (LOW confidence)
- Cifras de edad/downloads del Package Legitimacy Audit [ASSUMED] — la validez primaria descansa en registro + repos oficiales.
- Licencias Unsplash/Pexels sin atribución obligatoria [ASSUMED] — conocimiento de ecosistema.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — registro + docs oficiales verificados hoy (STACK.md) y re-verificados en los puntos que la fase toca (npm view + tarball + ejecuciones locales).
- Architecture: HIGH — monorepo y capas ya decididas (ARCHITECTURE.md + CONTEXT locked); decisiones abiertas son de bajo impacto y están en el Assumptions Log.
- Pitfalls: HIGH — 4 de 10 pitfalls verificados por ejecución directa esta sesión (Node, uv init/.git, Enum names, CLP); el resto citado de docs oficiales.
- Guía/docs: HIGH — formato demo-cine leído de fuente primaria (repo hermano) esta sesión.

**Research date:** 2026-09-28
**Valid until:** 2026-10-28 (stack estable; re-verificar si v8.x de react-router o Vite 8.x movieron engines)
