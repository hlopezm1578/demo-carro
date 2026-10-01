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
el servicio de IA de Groq en la fase 4).

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
| Estado de cliente | **zustand 5.0** (con `persist`) | Stores de sesión y carro que sobreviven recargas y full-page loads en el `localStorage` ([ADR-009](adr/009-jwt-larga-vida-localstorage.md), [ADR-010](adr/010-carro-client-side.md)) |
| Runtime frontend | **Node ≥ 22.22** (o 24) | Techo de react-router 8 — prerrequisito que la guía 2 de desarrollo hace verificar (`node -v`) |
| Framework del API | **FastAPI 0.141.1** | Validación declarativa (422 automático), inyección de dependencias y `/docs` autogenerado para comparar con el contrato ([ADR-001](adr/001-arquitectura-en-capas.md), [ADR-007](adr/007-api-first.md)) |
| ORM | **SQLAlchemy 2.1.1** | Modelos declarativos; el mismo código para SQLite y un futuro Postgres ([ADR-005](adr/005-sqlite-y-create-all.md)) |
| Base de datos | **SQLite** (fase 1) | Cero instalación, archivo local; BD demo desechable con seed idempotente ([ADR-005](adr/005-sqlite-y-create-all.md)) |
| Configuración | **pydantic-settings 2.15** | `DATABASE_URL` y orígenes CORS como variables de entorno tipadas — sin secretos en código |
| Tokens de sesión | **pyjwt 2.15** | Emisión y verificación del JWT (`HS256`, claim de rol desde el primer token); la librería que usa hoy el tutorial oficial de FastAPI ([ADR-009](adr/009-jwt-larga-vida-localstorage.md)) |
| Hash de contraseñas | **pwdlib[argon2] 0.3** | Argon2 con `PasswordHash.recommended()`; reemplaza a la librería legada sin mantenimiento ([ADR-009](adr/009-jwt-larga-vida-localstorage.md), [ADR-011](adr/011-roles-desde-el-primer-token.md)) |
| Formularios HTTP | **python-multipart 0.0.32** | Parseo del form de login (`OAuth2PasswordRequestForm`) que exige el `/api/auth/login` del contrato 0.2.0; ya viene dentro de `fastapi[standard]` |
| Gestor Python | **uv** (pyproject + uv.lock) | El flujo que enseña hoy la documentación oficial de FastAPI ([ADR-006](adr/006-uv-como-gestor.md)) |
| Lenguaje backend | **Python 3.12** | Techo declarado por `transbank-sdk` (fase 3); fijado con `requires-python ">=3.12,<3.13"` ([ADR-006](adr/006-uv-como-gestor.md)) |
| Pago (fase 3) | **Webpay Plus REST, ambiente de integración** | Pasarela real chilena en sandbox con credenciales públicas sin registro (597055555532); el retorno del navegador hacia la SPA queda firmado con evidencia runtime ([ADR-012](adr/012-retorno-de-webpay.md)) |
| SDK Webpay | **transbank-sdk 6.1.0** | Único SDK oficial (repo TransbankDevelopers); `Transaction.build_for_integration(...)` trae las credenciales públicas — sin `.env` nuevo en esta fase; sync `requests` → rutas `def` sincronizadas ([ADR-012](adr/012-retorno-de-webpay.md), [ADR-013](adr/013-orden-nace-al-pagar-stock-al-aprobar.md)) |
| IA (fase 4) | **groq 1.7.0** (pin `>=1.7,<2`) | SDK oficial de Groq para la asesora de venta: JSON estructurado con `json_schema` strict + validación de ids contra la BD (mini-RAG, D-56); la API key vive solo en el `.env` del backend y sin key el asistente degrada a 503 amable ([ADR-018](adr/018-asistente-ia-groq-structured-outputs.md), que supersede al [ADR-017](adr/017-asistente-ia-mini-rag-key-solo-backend.md)) |

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
│       ├── security.py         # módulo transversal de seguridad: hash Argon2, JWT HS256 y las dependencias de sesión/rol (ADR-009, ADR-011)
│       ├── models/             # tablas SQLAlchemy: la entidad PRODUCTO (diseño §2)
│       ├── models/usuario.py   # la entidad USUARIO: email único, hash de contraseña y rol
│       ├── models/pedido.py    # las entidades PEDIDO y LÍNEA: estados honestos, total recalculado y snapshot (ADR-013, ADR-014)
│       ├── schemas/            # frontera: validación Pydantic (RN-01, RN-02)
│       ├── schemas/usuario.py  # RegistroCreate, UsuarioPublico y Token — espejan el contrato 0.2.0
│       ├── schemas/pedido.py   # CheckoutCreate, CheckoutRespuesta, OrdenLista y OrdenDetalle — espejan el contrato 0.3.0
│       ├── repositories/       # solo acceso a datos: el almacén D1
│       ├── repositories/producto.py # el almacén de productos: lecturas del catálogo y las escrituras admin (crear, editar, toggle activo — D-52)
│       ├── repositories/usuario.py  # el almacén de usuarios: búsqueda por email y creación
│       ├── repositories/pedido.py   # el almacén de pedidos: crear, buscar por numero/dueña, el UPDATE condicional de stock, la transición admin validada y las agregaciones de métricas (D-50, D-54)
│       ├── services/           # las reglas del negocio: los procesos 1.0–3.0
│       ├── services/cuentas.py # registrar (409 claro) y autenticar (401 genérico)
│       ├── services/pedidos.py # iniciar_checkout (recalculo CART-03) y procesar_retorno (discriminador + commit + transición)
│       ├── services/webpay.py  # wrapper de Transaction.build_for_integration — el ÚNICO lugar que importa transbank
│       ├── services/admin.py   # las reglas del panel: escrituras de productos con allow-list, transición validada y métricas (ADMN-01..04)
│       ├── services/asistente.py # la asesora: mini-RAG + structured output — el ÚNICO lugar que importa groq
│       ├── routers/            # endpoints HTTP: /api/salud, /api/productos
│       ├── routers/auth.py     # /api/auth/registro, /api/auth/login, /api/auth/perfil
│       ├── routers/admin.py    # el CRUD real de administración: /api/admin/productos, /api/admin/pedidos y /api/admin/metricas — get_current_admin en cada endpoint (ADMN-01..04, ADR-015)
│       ├── routers/asistente.py # POST /api/asistente — público, topes en el borde y 503/429 amables (AIAS-01..03, ADR-017)
│       ├── routers/checkout.py # POST /api/checkout — Bearer, valida el carro y crea la orden PENDING (D-34)
│       ├── routers/retorno.py  # GET+POST /api/pago/retorno — público, discrimina por params y responde 302 a la SPA (ADR-012)
│       ├── routers/pedidos.py  # GET /api/pedidos y /api/pedidos/{numero} — Bearer con ownership 404 uniforme
│       └── seed.py             # siembra idempotente: el proceso 4.0 (RF-05)
└── frontend/                   ← TIER CLIENTE — proyecto npm
    ├── public/products/        # las 12 fotos locales /products/{sku}.jpg (A1, RN-03)
    └── src/
        ├── main.tsx            # composición: BrowserRouter + QueryClientProvider
        ├── lib/api.ts          # ÚNICO punto de salida HTTP de la SPA
        ├── lib/badges.ts       # BADGES a módulo propio: una sola verdad del estado del pedido (D-45) — voucher, historial y panel admin importan de aquí
        ├── types/api.ts        # interfaces TS que espejan los schemas (ADR-004)
        ├── stores/             # useAuthStore y useCarroStore: sesión y carro persistente en localStorage (ADR-009, ADR-010)
        ├── features/           # una carpeta por dominio: landing/, catalogo/
        ├── features/cuentas/   # login y registro (fase 2)
        ├── features/carro/     # la página /carro con hidratación de precios vigentes
        ├── features/checkout/  # el resumen protegido del pedido (AUTH-04)
        ├── features/pago/      # la ruta única /pago/resultado: el voucher que renderiza los 4 flujos (D-42, D-43)
        ├── features/pedidos/   # el historial /pedidos: lista y detalle que reutiliza el voucher (D-46)
        ├── features/admin/     # el panel /admin: LayoutAdmin con subnav + AdminProductos, AdminPedidos, AdminMetricas y NoAutorizado (D-55, ADR-015)
        ├── features/asistente/ # la burbuja BurbujaAsesora en el layout de la tienda, con historial stateless (D-58/D-59)
        └── components/         # Navbar, Footer, layout compartido
            ├── RequireAuth.tsx # guard de rutas protegidas con returnTo genérico (D-32)
            └── RequireAdmin.tsx # guard por rol: espejo UX del 403 — sin sesión delega en RequireAuth, con sesión sin rol muestra NoAutorizado (ADR-015)
```

**Reglas de dependencia** (verificables en revisión de código — las citan las guías):

1. `routers/` valida HTTP y delega: **jamás importa SQLAlchemy** (la `Session`
   inyectada llega re-exportada desde `app/database`) y jamás escribe SQL.
2. `repositories/` ejecuta SQL: **jamás decide reglas de negocio** — que un
   producto inactivo no aparezca lo decide el servicio; el repositorio solo consulta.
3. `services/` decide: **jamás conoce HTTP** — ni códigos de estado, ni JSON, ni
   cabeceras. El wrapper del asistente (`services/asistente.py`) respeta la
   regla con la misma técnica que `services/webpay.py`: traduce los errores
   del SDK de IA a señales de dominio — el 503/429 lo decide el router
   ([ADR-017](adr/017-asistente-ia-mini-rag-key-solo-backend.md)).
4. Solo `main.py` arma la aplicación (`FastAPI()`, CORS, `include_router`).
   Nadie más instancia la app.
5. En el frontend, **todo HTTP pasa por `src/lib/api.ts`**: ningún componente
   hace `fetch` por su cuenta. *Única excepción, narrada en las guías: el
   retorno de Webpay es navegación del navegador (302 del backend), no
   `fetch` — CORS no aplica ([ADR-012](adr/012-retorno-de-webpay.md)).*
6. Los componentes de `features/` **no se importan cruzados** sin razón: lo
   compartido baja a `components/`. *Excepciones narradas en las guías, con
   su razón: `VoucherPedido` reutilizado por el historial (guia-11, D-46) y
   ahora la `ProductCard` del catálogo reusada en el chat de la asesora
   (fase 4, mismo patrón D-46) — la card completa es un Link a la ficha y
   duplicarla serían dos verdades del mismo producto.*

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
| [009](adr/009-jwt-larga-vida-localstorage.md) | Sesión con un JWT de larga vida (7 días) en `localStorage` | Cómo mantiene la SPA la sesión entre recargas y full-page loads (D-19..D-22) |
| [010](adr/010-carro-client-side.md) | Carro client-side hidratado con precios vigentes | Dónde vive el carro de compras y qué datos guarda (D-27..D-30) |
| [011](adr/011-roles-desde-el-primer-token.md) | Roles desde el primer token: el admin nace del seed | Cómo nacen los roles y cómo se verifica el acceso por rol (D-23, D-24, D-33) |
| [012](adr/012-retorno-de-webpay.md) | El retorno de Webpay: 302 hacia la ruta única de la SPA, discriminando por presencia de params | Cómo vuelve el navegador de Webpay a la tienda (PAY-02, D-40, D-41) |
| [013](adr/013-orden-nace-al-pagar-stock-al-aprobar.md) | La orden nace al iniciar el pago y el stock se descuenta al aprobar | Cuándo nace la orden y cuándo se descuenta el stock (CART-03, ORDR-02, D-34, D-35) |
| [014](adr/014-snapshot-de-precio-en-la-orden.md) | Snapshot de precio en la orden y numero legible como buy_order | Qué muestra un pedido viejo cuando el catálogo cambia (ORDR-01, D-36, D-37) |
| [015](adr/015-panel-admin-protegido-por-rol.md) | El panel protegido por rol en los dos tiers: RequireAdmin como espejo UX del 403 | Cómo entra la dueña a `/admin` y quién responde cada endpoint (ADMN-01..04, D-55) |
| [016](adr/016-maquina-de-estados-con-transicion-admin.md) | Máquina de estados de pedidos con UNA transición manual admin (PENDING→CANCELLED) | Qué transiciones existen, quién las ejecuta y cómo se gestionan las huérfanas (ADMN-03, D-50) |
| [017](adr/017-asistente-ia-mini-rag-key-solo-backend.md) | Asistente IA con mini-RAG, structured output y key solo en el backend | Cómo recomienda la asesora sin alucinar y dónde vive la API key (AIAS-01..03, D-56, D-63, D-61; superseded por 018) |
| [018](adr/018-asistente-ia-groq-structured-outputs.md) | Asistente IA con Groq: structured outputs json_schema y key solo en el backend | Reemplaza el proveedor de ADR-017 tras el cierre del free tier de Google (AIAS-01..03, D-63..D-68) |
| [019](adr/019-despliegue-free-tier-vercel-render.md) | Despliegue en free tier: Vercel para la SPA y Render para la API | Cómo se publican los dos tiers con URL pública sin costo (DEPL-01, D-69, D-73) |
| [020](adr/020-persistencia-efimera-seed-idempotente.md) | Persistencia efímera: SQLite + seed idempotente como estrategia | Cómo sobrevive la BD al disco efímero del free tier (DEPL-01/DEPL-02, D-70) |

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
