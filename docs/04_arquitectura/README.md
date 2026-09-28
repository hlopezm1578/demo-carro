# Fase 4 — Documento de Arquitectura: Maura

> **Guía:** Demo Carro — ciclo de vida del software en una tienda de body splash (segunda guía de la serie, hermana de demo-cine)
> **Fase del ciclo de vida:** 4. Arquitectura
> **Insumo obligatorio:** `03_diseno.md` — la arquitectura **no cambia el diseño**: elige tecnología y define cómo se organiza el código para construir exactamente lo diseñado.
> **Decisiones detalladas:** cada elección de esta fase tiene su ADR (Architecture Decision Record) en `adr/`, formato: contexto → opciones → decisión → consecuencias → preguntas para la clase.
> **Fecha:** 2026-09-28

---

## Contexto

Este documento decide el CÓMO: cómo se sirven las pantallas del diseño, cómo se
organiza el código de los dos tiers y con qué tecnología. La decisión central
ya está tomada en la exploración del proyecto y aquí se registra como ADR:
**dos tiers estrictamente separados** — una SPA React que renderiza y una API
FastAPI que expone JSON — porque el objetivo pedagógico de la guía es la
integración entre tiers y con servicios externos reales (Webpay en la fase 3,
Gemini en la fase 4).

> **Alcance del repositorio (decisión D-17, ADR-008):** el proyecto de código
> que describe este documento — `backend/` + `frontend/` — es el que construye
> el **alumno** siguiendo las guías de `docs/05_desarrollo/`. Este repositorio
> contiene **solo la guía**: el código vive narrado dentro de las guías, como
> bloques para copiar. Aquí no hay `backend/` ni `frontend/`.

---

## 1. La arquitectura en una página

**Nombre:** arquitectura **de dos tiers estrictamente separados** (SPA + API),
con el tier servidor organizado **en capas**.

```
┌─────────────────────────────┐           ┌──────────────────────────────────┐        ┌─────────────────┐
│   TIER CLIENTE              │   JSON    │   TIER SERVIDOR                  │  SQL   │                 │
│   (lo que se ve)            │◄─────────►│   (lo que decide)                │◄──────►│  SQLite         │
│                             │   /api    │                                  │        │  (lo que queda) │
│  Navegador                  │           │  API FastAPI (en capas)          │        │                 │
│  SPA React 19 + TypeScript  │           │   · routers     validan HTTP     │        │  tabla          │
│   · React Router 8          │           │   · services    las reglas       │        │  productos      │
│   · TanStack Query (caché)  │           │   · repositories  SQL            │        │  (12 aromas     │
│   · Tailwind CSS 4          │           │   · models / schemas             │        │   demo)         │
│                             │           │                                  │        │                 │
│  Fotos /products/*.jpg      │           │  En dev: el proxy /api de Vite   │        │                 │
│  (estáticas, del propio SPA)│           │  hace la llamada same-origin     │        │                 │
└─────────────────────────────┘           └──────────────────────────────────┘        └─────────────────┘
```

**Las tres preguntas** (memorizables):

| Pregunta | Respuesta | En Maura |
|---|---|---|
| ¿Qué ve el usuario? | Lo que renderiza el tier cliente | Landing, catálogo con filtros, ficha del aroma (diseño §4) |
| ¿Dónde vive cada cosa? | Datos y reglas en el servidor; pantalla y fotos en el cliente | El catálogo y el stock en SQLite; las fotos como archivos del SPA (`RN-03`); los filtros en la dirección de la página |
| ¿Cómo hablan entre sí? | JSON sobre HTTP, definido por el contrato | `GET /api/productos?familia=citricas`, `GET /api/productos/1` (`contrato_api.yaml`) |

**Regla de oro:** *el backend expone JSON y nada más; la SPA renderiza todo; jamás hay plantillas en el servidor. La única conversación entre los dos tiers es el contrato de la API (ADR-007).*

**Frase para el informe:**

> *"El sistema se construye con una arquitectura de dos tiers estrictamente
> separados: una SPA React en el cliente que renderiza la interfaz, y una API
> FastAPI en el servidor organizada en capas (routers → services →
> repositories), que se comunican exclusivamente a través de un contrato
> OpenAPI definido antes del código."*

> **Pregunta inevitable del jurado: "¿por qué no un monolito con plantillas,
> como el proyecto hermano demo-cine?"** Porque el objetivo pedagógico cambió:
> demo-cine enseñaba el camino más corto a una URL pública; esta guía enseña
> la **integración** entre tiers y con servicios externos reales. La pregunta
> merece su discusión completa — la responde el [ADR-002](adr/002-dos-tiers-spa-y-api.md).

---

## 2. Del diseño a la arquitectura (traducción elemento a elemento)

| Elemento de diseño (fase 3) | Dónde vive en la arquitectura |
|---|---|
| Entidad PRODUCTO (§2.1–2.2) | **Modelo SQLAlchemy** — `backend/app/models/` (tier servidor) |
| Almacén D1 Productos (§3.2) | **Repositorio** — `backend/app/repositories/` (un almacén = un repositorio) |
| Almacén A1 Imágenes (§3.2, RN-03) | **Archivos estáticos del SPA** — `frontend/public/products/` (los sirve el host del SPA; el backend solo guarda la ruta) |
| Procesos 1.0–3.0: explorar, filtrar, ficha (§3.3–3.5) | **Services + routers del API** (la regla y el endpoint) y **pantallas de la SPA** (la interacción) |
| Proceso 4.0: sembrar datos demo (§3.6) | **Script de seed** — `backend/app/seed.py`, ejecutado con uv sobre el mismo código (tier servidor) |
| Pantallas 1–3 (§4.2–4.4) | **SPA React** — `frontend/src/features/landing/` y `frontend/src/features/catalogo/` (tier cliente) |
| Validaciones RN-01/RN-02 | **Schemas Pydantic en la frontera del API** (422 automático) + filtros como URL search params en la SPA |
| Estados de carga/error/vacío (§4.1) | **TanStack Query** en la SPA — cada pantalla declara sus estados sin flags manuales |

Detalle clave para la clase: **el DFD del diseño se convierte literalmente en la
estructura del código.** El proceso 2.0 "Filtrar catálogo" del DFD = un
servicio `catalogo` que aplica RN-01 y RN-02 + un endpoint
`GET /api/productos` que valida los query params con Pydantic; el almacén D1 =
un repositorio que solo consulta la tabla `productos`.

---

## 3. Stack tecnológico (y por qué)

Versiones del stack autoritativo del proyecto (AGENTS.md / `.planning/research/STACK.md`).

| Pieza | Elección | Por qué (decisión completa) |
|---|---|---|
| Interfaz (tier cliente) | **SPA React 19.3** | La decisión central: dos tiers estrictos ([ADR-002](adr/002-dos-tiers-spa-y-api.md)) |
| Lenguaje del frontend | **TypeScript ~6.0.2** | El espejo manual de los schemas tipa la frontera de punta a punta ([ADR-004](adr/004-frontend-typescript.md)) |
| Bundler y dev server | **Vite 8.3.1** | Estándar SPA; en dev su proxy `/api` hace la llamada same-origin (sin CORS) ([ADR-002](adr/002-dos-tiers-spa-y-api.md)) |
| Routing | **React Router 8.4.0** (library mode) | Rutas de la SPA (`/`, `/productos`, `/productos/:id`); filtros en URL search params compartibles |
| Server state | **TanStack Query 5.104** | Caché, reintentos y estados de carga/error/vacío del diseño §4.1 sin fetch manual |
| Estilos | **Tailwind CSS 4.3.3** | La dirección fresco-luminosa de la marca con utilidades; v4 sin archivo de configuración |
| Runtime frontend | **Node ≥ 22.22** (o 24) | Techo de react-router 8 — prerrequisito que la guía 2 de desarrollo hace verificar (`node -v`) |
| Framework del API | **FastAPI 0.141.1** | Validación declarativa (422 automático), inyección de dependencias y `/docs` autogenerado para comparar con el contrato ([ADR-001](adr/001-arquitectura-en-capas.md), [ADR-007](adr/007-api-first.md)) |
| ORM | **SQLAlchemy 2.1.1** | Modelos declarativos; el mismo código para SQLite y un futuro Postgres ([ADR-005](adr/005-sqlite-y-create-all.md)) |
| Base de datos | **SQLite** (fase 1) | Cero instalación, archivo local; BD demo desechable con seed idempotente ([ADR-005](adr/005-sqlite-y-create-all.md)) |
| Configuración | **pydantic-settings 2.15** | `DATABASE_URL` y orígenes CORS como variables de entorno tipadas — sin secretos en código |
| Gestor Python | **uv** (pyproject + uv.lock) | El flujo que enseña hoy la documentación oficial de FastAPI ([ADR-006](adr/006-uv-como-gestor.md)) |
| Lenguaje backend | **Python 3.12** | Techo declarado por `transbank-sdk` (fase 3); fijado con `requires-python ">=3.12,<3.13"` ([ADR-006](adr/006-uv-como-gestor.md)) |
| Pago (fase 3) | **Webpay Plus, ambiente de integración** | Pasarela real chilena en sandbox con credenciales públicas — llega en su fase |
| IA (fase 4) | **google-genai** | SDK oficial de Gemini; la API key vive solo en el backend — llega en su fase |

---

## 4. Organización del código (la regla de oro hecha carpetas)

> **Este árbol es el proyecto que construye el alumno** siguiendo las guías de
> `docs/05_desarrollo/`. **Este repositorio contiene solo la guía (D-17):** aquí
> no existe `backend/` ni `frontend/` — el código vive narrado dentro de las
> guías como bloques que el alumno copia en su máquina. La forma de este árbol
> es, sin embargo, obligatoria: es la que las guías construyen pieza por pieza.

```
maura/                          ← raíz del proyecto del alumno (D-11, ADR-003)
├── backend/                    ← TIER SERVIDOR — proyecto Python, administrado con uv
│   ├── pyproject.toml          # uv: dependencias + requires-python ">=3.12,<3.13"
│   ├── uv.lock                 # entorno reproducible (ADR-006)
│   └── app/
│       ├── main.py             # composición: arma la aplicación (no tiene lógica)
│       ├── config.py           # Settings: DATABASE_URL, CORS_ORIGINS (variables de entorno)
│       ├── database.py         # engine, SessionLocal, Base, get_session
│       ├── models/             # tablas SQLAlchemy: la entidad PRODUCTO (diseño §2)
│       ├── schemas/            # frontera: validación Pydantic (RN-01, RN-02)
│       ├── repositories/       # solo acceso a datos: el almacén D1
│       ├── services/           # las reglas del negocio: los procesos 1.0–3.0
│       ├── routers/            # endpoints HTTP: /api/salud, /api/productos
│       └── seed.py             # siembra idempotente: el proceso 4.0 (RF-05)
└── frontend/                   ← TIER CLIENTE — proyecto npm
    ├── public/products/        # las 12 fotos locales /products/{sku}.jpg (A1, RN-03)
    └── src/
        ├── main.tsx            # composición: BrowserRouter + QueryClientProvider
        ├── lib/api.ts          # ÚNICO punto de salida HTTP de la SPA
        ├── types/api.ts        # interfaces TS que espejan los schemas (ADR-004)
        ├── features/           # una carpeta por dominio: landing/, catalogo/
        └── components/         # Navbar, Footer, layout compartido
```

**Reglas de dependencia** (verificables en revisión de código — las citan las guías):

1. `routers/` valida HTTP y delega: **jamás importa SQLAlchemy** (la `Session`
   inyectada llega re-exportada desde `app/database`) y jamás escribe SQL.
2. `repositories/` ejecuta SQL: **jamás decide reglas de negocio** — que un
   producto inactivo no aparezca lo decide el servicio; el repositorio solo consulta.
3. `services/` decide: **jamás conoce HTTP** — ni códigos de estado, ni JSON, ni cabeceras.
4. Solo `main.py` arma la aplicación (`FastAPI()`, CORS, `include_router`).
   Nadie más instancia la app.
5. En el frontend, **todo HTTP pasa por `src/lib/api.ts`**: ningún componente
   hace `fetch` por su cuenta.
6. Los componentes de `features/` **no se importan cruzados** sin razón: lo
   compartido baja a `components/`.

---

## 5. Índice de ADRs

| ADR | Decisión | Resuelto por |
|---|---|---|
| [001](adr/001-arquitectura-en-capas.md) | Arquitectura en capas (routers → services → repositories → models) | Cómo organizar el código del tier servidor |
| [002](adr/002-dos-tiers-spa-y-api.md) | Dos tiers estrictos: SPA React + API FastAPI | Cómo se sirven las pantallas (la decisión central) |
| [003](adr/003-monorepo.md) | Monorepo del alumno: `backend/` + `frontend/` en una sola raíz | Cómo se organiza el proyecto (D-11) |
| [004](adr/004-frontend-typescript.md) | TypeScript con espejo manual de los schemas | Cómo se tipa la frontera en el cliente (D-09) |
| [005](adr/005-sqlite-y-create-all.md) | SQLite + `create_all` + seed idempotente (Alembic diferido) | Cómo persistir el almacén D1 en la fase 1 |
| [006](adr/006-uv-como-gestor.md) | uv como gestor del proyecto Python (3.12 con techo) | Cómo se administra el backend (D-10) |
| [007](adr/007-api-first.md) | API-first: el contrato OpenAPI antes del código | Cómo se define la interfaz (D-15) |
| [008](adr/008-repositorio-solo-guias.md) | Repositorio solo guías (guide-only) | Qué contiene este repo y qué construye el alumno (D-17/D-18) |

---

## 6. API-first: el contrato antes del código

La única conversación entre los dos tiers es la interfaz del API, y se diseña
**antes** de implementarse. El contrato es
[`contrato_api.yaml`](contrato_api.yaml) (OpenAPI 3.0.3) y es la **fuente de la
verdad de la interfaz**: rutas, parámetros, códigos de respuesta y esquemas.
Las guías de desarrollo deben implementarlo sin desviarse, y la comparación del
`/docs` generado por FastAPI contra el contrato es la **verificación de
cierre** de la fase 1 — la ejecuta la guía 4 de `docs/05_desarrollo/`
([ADR-007](adr/007-api-first.md)).

Flujo de la decisión:

```
contrato_api.yaml (se aprueba)  →  el código lo implementa  →  /docs generado ≈ contrato (verificación de desvío)
```

---

## 7. Aprobación de la fase

| Rol | Nombre | Decisión | Fecha |
|---|---|---|---|
| Arquitecto | ______________ | ☐ Aprobado ☐ Con observaciones | 2026-09-__ |
| Revisión (pares) | ______________ | ☐ Aprobado ☐ Con observaciones | 2026-09-__ |

> **Nota para la clase:** con esta fase el CÓMO queda cerrado y **versionado en
> ADRs**: si dentro de un año alguien pregunta "¿por qué SPA y no plantillas
> como en demo-cine?", la respuesta no está en la memoria de quien estuvo ese
> día — está en el ADR-002. Las guías de desarrollo (`05_desarrollo/`) ya
> pueden escribir código sabiendo exactamente qué deben respetar.
