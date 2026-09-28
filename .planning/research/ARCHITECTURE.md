# Architecture Research

**Domain:** E-commerce educativo de dos tiers — SPA React + API REST FastAPI en capas, con Webpay Plus (sandbox) y asistente Gemini
**Researched:** 2026-09-28
**Confidence:** HIGH para la estructura general y el flujo Webpay (fuentes primarias); MEDIUM en auth SPA y deployment; LOW en detalle fino del schema de BD

## Standard Architecture

### System Overview

```
┌────────────────────────── NAVEGADOR ──────────────────────────┐
│  SPA React (React Router)                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────────┐ │
│  │ Catálogo │ │ Carro    │ │ Cuenta/  │ │ Chat asistente IA │ │
│  │ + admin  │ │ checkout │ │ JWT      │ │ (burbuja)         │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └─────────┬─────────┘ │
│       └────────────┴─────┬──────┴─────────────────┘           │
│                  API client (fetch/axios, Bearer)             │
└──────────────────────────┼────────────────────────────────────┘
                           │ HTTPS / JSON (cross-origin → CORS)
┌──────────────────────────┼────────────────────────────────────┐
│  API FastAPI ─────────────▼  (tier servidor, en capas)        │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Routers (HTTP): products, auth, orders, payments,       │  │
│  │                 admin, assistant  → validan schemas     │  │
│  ├─────────────────────────────────────────────────────────┤  │
│  │ Services (casos de uso): CatalogService, OrderService,  │  │
│  │         PaymentService, AuthService, AssistantService   │  │
│  ├─────────────────────────────────────────────────────────┤  │
│  │ Repositories (acceso a datos): ProductRepo, OrderRepo,  │  │
│  │         UserRepo  (SQLAlchemy)                          │  │
│  ├─────────────────────────────────────────────────────────┤  │
│  │ External integrations: Transbank SDK │ google-genai     │  │
│  └─────────────────────────────────────────────────────────┘  │
│        │                        │                    │        │
└────────┼────────────────────────┼────────────────────┼────────┘
         ▼                        ▼                    ▼
   ┌──────────┐        ┌──────────────────┐   ┌───────────────┐
   │ Base de  │        │ Webpay Plus      │   │ Gemini API    │
   │ datos    │        │ webpay3gint      │   │ (google-genai │
   │ (SQLite/ │        │ (sandbox Trans-  │   │  solo desde   │
   │ Postgres)│        │  bank)           │   │  el backend)  │
   └──────────┘        └────────▲─────────┘   └───────────────┘
                                │ redirección del navegador
                     (form POST token_ws → tarjeta → return_url)
```

Flujo clave que cruza los tiers: la redirección de pago de Webpay **vuelve al backend, no a la SPA** (ver Data Flow).

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| SPA Router | Navegación client-side (rutas públicas, cuenta, admin, resultado de pago) | React Router `createBrowserRouter` + rutas anidadas con layout y `ErrorBoundary` |
| SPA API client | Único punto de salida HTTP: base URL por env, adjunta `Authorization: Bearer`, maneja 401 | Módulo `lib/api` (fetch wrapper o axios) + context de auth |
| SPA state de carro | Carro persistente client-side (localStorage) que se convierte en orden al checkout | Context/Zustand; validación de precios SIEMPRE en backend |
| Routers (API) | Contrato HTTP: parsea/valida schemas Pydantic, auth via `Depends`, delega en services | `APIRouter` por recurso con `prefix`/`tags` (patrón oficial "Bigger Applications") |
| Services | Lógica de negocio: reglas de orden, estados de pago, prompt del asistente | Clases/funciones puras inyectadas a routers via `Depends` |
| Repositories | Única capa que toca SQLAlchemy; una clase por agregado | Sesión de BD inyectada como dependencia (sesión por request) |
| AuthService | Hash de claves, emisión/validación JWT | pwdlib[argon2] + PyJWT; `OAuth2PasswordBearer(tokenUrl="token")` |
| PaymentService | Orquesta Webpay: create → return → commit/status; mapea los 4 flujos de retorno a estados de orden | `transbank-sdk` con `WebpayOptions` (integración) |
| AssistantService | Mini-RAG: arma prompt con catálogo real + system instruction; llama Gemini | `google-genai`, `GEMINI_API_KEY` solo en el backend |
| Webpay return endpoint | Recibe el POST/GET del navegador que vuelve de Webpay (fuera del router React) y redirige 302 a la SPA | Endpoint backend `GET+POST /api/payments/webpay/return` |

## Recommended Project Structure

```
backend/
├── app/
│   ├── main.py               # FastAPI(), CORSMiddleware, include_router
│   ├── core/                 # config (env vars), seguridad JWT, constantes
│   │   ├── config.py         # Settings por env (pydantic-settings)
│   │   └── security.py       # hash + create/decode token
│   ├── database.py           # engine, SessionLocal, Base, get_db dependency
│   ├── models/               # SQLAlchemy: user, product, order, order_item
│   ├── schemas/              # Pydantic: request/response por recurso
│   ├── repositories/         # acceso a datos por agregado
│   ├── services/             # lógica de negocio (orders, payments, assistant)
│   ├── routers/              # HTTP: auth, products, orders, payments, admin, assistant
│   └── dependencies.py       # get_current_user, get_current_admin, get_session
├── tests/
└── requirements.txt / pyproject.toml

frontend/
├── src/
│   ├── main.jsx              # createBrowserRouter + RouterProvider
│   ├── routes/               # definición de rutas (públicas/cuenta/admin)
│   ├── features/             # dominios de UI: catalog, cart, checkout,
│   │                         #   account, admin, assistant-chat
│   ├── lib/
│   │   ├── api.js            # API client: base URL, Bearer, errores 401
│   │   └── cart.js           # carro en localStorage + sincronización
│   ├── context/AuthContext.jsx  # token en memoria + login/logout/refresh
│   └── components/           # UI compartida (Navbar, ProductCard, ChatBubble)
├── .env                      # VITE_API_URL (dev: http://localhost:8000)
└── vite.config.js
```

### Structure Rationale

- **routers/ → services/ → repositories/:** cada capa solo conoce a la inferior; los routers no importan SQLAlchemy y los repositorios no conocen HTTP. Es el patrón que la doc oficial de FastAPI ("Bigger Applications") siembra con `APIRouter` + `dependencies.py`, extendido con services/repositories que la doc deja a criterio.
- **schemas/ separado de models/:** Pydantic (contrato HTTP) y SQLAlchemy (persistencia) evolucionan por razones distintas; mezclarlos acopla el contrato a la BD.
- **services/payments aislado:** toda la complejidad Webpay (4 flujos de retorno, timeout de token) vive en un solo service testeable sin HTTP.
- **features/ en el frontend:** agrupa por dominio funcional, no por tipo de archivo; el chat del asistente y el admin son features desmontables.
- **lib/api.js único:** la URL del backend y el attach del Bearer viven en un solo lugar — crítico porque dev y producción tienen orígenes distintos.

## Architectural Patterns

### Pattern 1: API en capas con DI de FastAPI

**Qué:** routers validan y delegan; services contienen casos de uso; repositories tocan la BD; todo se conecta con `Depends`.
**Cuándo usar:** siempre en este proyecto — es el objetivo pedagógico declarado.
**Trade-offs:** más archivos que un monolito `main.py`; a cambio, cada capa es testeable y el material educativo muestra bordes explícitos.

```python
# dependencies.py — sesión por request + usuario actual
def get_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# routers/orders.py — el router no sabe cómo se persiste ni cómo se paga
@router.post("/orders", response_model=OrderOut, status_code=201)
def create_order(
    payload: OrderCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    return OrderService(OrderRepository(db)).create_from_cart(user, payload)
```

### Pattern 2: Return-URL bridge para Webpay → SPA

**Qué:** `return_url` de Webpay apunta a un **endpoint del backend** que procesa el retorno y redirige (302) a una ruta de la SPA. La SPA nunca recibe el POST de Webpay.
**Cuándo usar:** siempre que una pasarela redirige el navegador con POST a la vuelta — un SPA con router client-side no puede ser destino directo de ese POST porque React Router solo enruta una vez que la app cargó, y un POST de navegador externo a un host estático no ejecuta JS.
**Trade-offs:** el backend participa en la vuelta (no es puro static); a cambio se resuelven los 4 flujos de retorno en el servidor, donde está el SDK, y la SPA solo consulta el resultado.

```python
# El endpoint de retorno ACEPTA POST y GET (la doc oficial: POST siempre,
# GET desde API 1.1+; el abort en integración vuelve por POST)
@router.api_route("/payments/webpay/return", methods=["GET", "POST"])
async def webpay_return(request: Request, db=Depends(get_session)):
    params = await _params_from(request)          # form POST o query GET
    result = PaymentService(...).resolve_return(params)  # token_ws vs TBK_*
    return RedirectResponse(f"{FRONTEND_URL}/checkout/result?order={result.order_id}")
```

### Pattern 3: JWT bearer con API client central

**Qué:** login POST a `/token` (form OAuth2), el SPA guarda el access token y el API client lo adjunta como `Authorization: Bearer`; `get_current_user` decodifica con PyJWT.
**Cuándo usar:** SPA + API en orígenes separados (este proyecto); las cookies same-site no aplican bien cross-origin.
**Trade-offs:** storage del token en el navegador expuesto a XSS. Recomendación opinada para la guía: access token ~30 min en memoria (context) + opcional persistencia en localStorage documentando el riesgo; refresh token es extensión extra-oficial (la doc de FastAPI solo cubre access token). Para alcance educativo, access token + re-login es suficiente y más simple.

### Pattern 4: Asistente IA backend-proxied con mini-RAG de catálogo

**Qué:** la burbuja de chat llama a `POST /api/assistant`; el backend arma el prompt con system instruction (persona vendedora) + el catálogo real (o un subconjunto filtrado) e invoca Gemini con `google-genai`. La API key jamás sale del backend.
**Cuándo usar:** catálogo pequeño (decenas de productos) — inyectar el catálogo completo en el prompt funciona sin embeddings ni vector store.
**Trade-offs:** el prompt crece con el catálogo (token cost); suficiente aquí. Si creciera, filtrar por categoría/keyword antes de inyectar.

```python
# services/assistant.py
client = genai.Client()  # lee GEMINI_API_KEY del entorno

PROMPT = f"""Eres la asesora de ventas de {TIENDA}. Recomienda SOLO de este
catálogo, con precios reales:\n{catalogo_como_texto}\nResponde breve, en español,
y sugiere agregar al carro."""

resp = client.models.generate_content(
    model="gemini-flash-latest",
    contents=historial_y_mensaje,
    config=types.GenerateContentConfig(system_instruction=SYSTEM),
)
```

## Data Flow

### Request Flow (normal)

```
[Usuario en la SPA]
    ↓ acción (ver producto, comprar)
[API client] → [Router FastAPI] → [Service] → [Repository] → [BD]
    ↓                ↓ (valida schema    ↓ (reglas)     ↓ (SQL)
[JSON response] ← (Pydantic + auth DI) ←───────────────┘
```

### Key Data Flows

1. **Webpay round-trip (el flujo que cruza todo):**
   ```
   SPA checkout → POST /api/payments/create
     → PaymentService crea orden PENDING + SDK create(buy_order, session_id,
       amount, return_url) → respuesta {url, token}
     → SPA recibe url+token y redirige al navegador (form POST token_ws a Webpay)
   [Usuario paga tarjeta en Webpay, hosted por Transbank — ~10 min máx en integración]
   Webpay redirige el navegador a return_url (POST, o GET desde API 1.1+) con:
     a) normal: token_ws            → commit(token_ws); aprobado ⇔ response_code==0
                                          y status==AUTHORIZED; orden → PAID
     b) timeout: TBK_ID_SESION + TBK_ORDEN_COMPRA (sin token)
                                          → orden → CANCELLED (recuperable por sesión)
     c) abort:   TBK_TOKEN + TBK_ID_SESION + TBK_ORDEN_COMPRA
                                          → status(TBK_TOKEN); sin commit; → CANCELLED
     d) error form: los 4 parámetros    → tratar como fallido → CANCELLED
   Backend resuelve, persiste el estado de la orden y responde 302 a
   /checkout/result?order=ID  →  la SPA carga, consulta GET /api/orders/ID
   y muestra voucher/fracaso.  (El token de Webpay vive ~5 min: el commit
   debe ocurrir apenas vuelve el navegador.)
   ```

2. **Gemini request path:**
   ```
   ChatBubble (SPA) → POST /api/assistant {mensaje, historial}
     → AssistantService: lee catálogo de la BD (repositories) → arma prompt
     → google-genai generate_content (system_instruction + catálogo)
     → respuesta reducida a texto/productos → JSON a la SPA → burbuja
   La API key vive solo en env del backend (GEMINI_API_KEY).
   ```

3. **Auth flow:**
   ```
   SPA /login → POST /token (form: username, password)
     → AuthService verifica hash (pwdlib[argon2]) → firma JWT {sub, exp}
   SPA guarda token (context en memoria ± localStorage) → API client
   adjunta Bearer → get_current_user decodifica (PyJWT) → 401 si expiró
   Roles: claim extra (is_admin) → dependency get_current_admin para /admin/*
   ```

4. **Carro → orden:** el carro vive en la SPA (localStorage); al checkout el backend re-valida precios y stock contra la BD y crea la orden (PENDING) + order_items con `unit_price` congelado. El mando de la verdad de precios/stock es siempre el backend.

## State del backend: modelo de datos (borrador)

`users(id, email único, password_hash, name, is_admin, created_at)` ·
`products(id, sku, name, description, price, stock, active, image_url)` ·
`orders(id, user_id FK, status ∈ {PENDING, PAID, CANCELLED, REJECTED}, total, buy_order único, session_id, webpay_token, created_at)` ·
`order_items(id, order_id FK, product_id FK, quantity, unit_price snapshot)`.

Notas: `buy_order`/`session_id`/`webpay_token` en `orders` son la bisagra con los flujos de retorno de Webpay (b y c no traen token_ws). Stock: descuento atómico al crear la orden PENDING y restitución en CANCELLED/REJECTED (transacción BD). *(Borrador de práctica común — confidence LOW/MEDIUM; validar en la fase de diseño de BD.)*

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-1k usuarios (demo educativo) | Monolito en capas + SQLite/Postgres gratis; todo lo anterior sobra y basta |
| 1k-100k | Postgres gestionado; separar frontend/API en hosts (ya lo está); cache de catálogo en el prompt del asistente; colas no necesarias |
| 100k+ | Fuera de alcance pedagógico: aquí solo se documentan los límites (webhooks, réplicas, etc.) |

### Scaling Priorities

1. **Primer cuello:** cold starts del free tier de la API (~15 min idle) — irrelevante para una demo, documentarlo como trade-off.
2. **Segundo:** rate limits del free tier de Gemini (RPM/RPD — pendiente confirmar logueado según PROJECT.md); mitigar con cache de respuestas frecuentes o desactivar el chat al 429.

## Anti-Patterns

### Anti-Pattern 1: Crear/confirmar transacciones Webpay desde la SPA

**Qué hacen:** llamar al SDK de Transbank (o exponer la API key de integración) en código frontend.
**Por qué está mal:** rompe el modelo de confianza — todo lo que viaja al navegador es público; además el commit necesita credenciales y estado de servidor.
**Hacer esto:** la SPA solo consume endpoints propios (`POST /api/payments/create`, `GET /api/orders/{id}`); el SDK vive solo en `services/payments`.

### Anti-Pattern 2: Apuntar `return_url` directo a la SPA

**Qué hacen:** poner `return_url=https://mi-spa/checkout/result` esperando que React Router reciba a Webpay.
**Por qué está mal:** Webpay redirige con POST (y parámetros TBK_* en query/form) a una URL que el host estático no puede responder con lógica; la SPA pierde el token y no puede hacer commit — el pago queda huérfano.
**Hacer esto:** return_url → endpoint backend que procesa los 4 flujos y redirige 302 a la ruta SPA (Pattern 2). Este es exactamente el spike pendiente de PROJECT.md; queda resuelto arquitectónicamente con este patrón.

### Anti-Pattern 3: CORS comodín con credenciales

**Qué hacen:** `allow_origins=["*"]` junto a `allow_credentials=True` (o para dejar "de funcionar" el Bearer).
**Por qué está mal:** la spec CORS excluye el comodín en requests con credenciales — el navegador bloquea y falla de forma confusa.
**Hacer esto:** lista explícita de orígenes: dev (`http://localhost:5173`) + origen de producción, ambos desde settings/env.

### Anti-Pattern 4: Llamar a Gemini desde el frontend

**Qué hacen:** meter `GEMINI_API_KEY` en `VITE_...` del bundle.
**Por qué está mal:** todo lo compilado al SPA es extraíble por cualquiera; la key se quema en minutos.
**Hacer esto:** endpoint proxy `/api/assistant` con la key en env del backend (ya decidido en PROJECT.md).

### Anti-Pattern 5: Precio o stock calculados solo en el cliente

**Qué hacen:** confiar en el total del carro del navegador o en el stock mostrado.
**Por qué está mal:** manipulable; además el precio puede cambiar entre agregar al carro y pagar.
**Hacer esto:** backend recalcula el total al crear la orden y congela `unit_price` en `order_items`; stock se valida/descuenta en transacción.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Webpay Plus (sandbox) | SDK `transbank-sdk` (WebpayOptions: commerce code 597055555532 + api key pública); create → form POST token_ws → return endpoint (GET+POST) → commit/status | 4 flujos de retorno distintos; token ~5 min; formulario ~10 min en integración; aprobado ⇔ response_code==0 && status==AUTHORIZED; errores tipados (TransactionCreateError…) |
| Gemini (google-genai) | Cliente del SDK en el backend (`GEMINI_API_KEY` env); `generate_content` con `GenerateContentConfig(system_instruction=…)`; multi-turn con `client.chats.create` | Model alias `gemini-flash-latest`; mini-RAG inyectando catálogo en el prompt; rate limits del free tier aún por confirmar (PROJECT.md) |
| Host estático + host API | Frontend build estático (Vite) en un host; API en otro; `VITE_API_URL` por entorno | Topología host-agnostic; CORS explícito obligatorio; elegir plataforma queda pendiente en PROJECT.md |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| SPA ↔ API | Solo HTTP/JSON con Bearer; sin acceso a BD ni SDK | Contrato versionado `/api/...`; errores 401/422 normalizados |
| Router → Service | Llamada directa (DI) | Routers sin lógica de negocio |
| Service → Repository | Llamada directa con sesión inyectada | Transacciones de BD nacen y mueren en la request |
| PaymentService ↔ OrderService | PaymentService actualiza estado de orden via repositorio compartido | Estados de orden: PENDING → PAID/CANCELLED/REJECTED |

## Suggested Build Order (dependencias entre componentes)

1. **Esqueleto de ambos tiers + contrato de API**: backend `main.py` + CORS + health check; frontend Vite + router + API client apuntando a dev. *(Nada más puede existir sin esto.)*
2. **BD + catálogo**: models/migrations seed, repositorios y endpoints públicos de productos; SPA catálogo/landing. *(Checkout y asistente consumen este catálogo.)*
3. **Auth JWT**: users, `/token`, `get_current_user`/`get_current_admin`; SPA login/registro y guards. *(Las órdenes con historial pertenecen a usuarios; el admin se protege por rol.)*
4. **Carro + órdenes PENDING**: carro SPA, validación de precios/stock backend, `POST /orders`. *(El pago necesita una orden que cobrar; además deja probar órdenes sin Webpay.)*
5. **Webpay**: PaymentService, `POST /payments/create`, return endpoint (GET+POST) con los 4 flujos, página `/checkout/result`. *(Depende de 3 y 4; hacer spike de redirección aquí — patrón ya definido arriba.)*
6. **Panel admin**: CRUD productos/stock + vista de pedidos, protegido con `get_current_admin`. *(Depende de 2 y 4; independiente de 5 y 7.)*
7. **Asistente Gemini**: `/api/assistant` + AssistantService + ChatBubble SPA. *(Solo depende del catálogo (2); ir al final evita acoplar el core de la tienda a la disponibilidad de Gemini.)*
8. **Deploy**: hosts free tier, env vars de producción, CORS con origen real, seed sandbox. *(Último: congela URLs que Webpay requiere en `return_url`.)*

## Sources

- Transbank Developers — Documentación Webpay Plus (flujo create/redirect/return/commit, 4 flujos de retorno, POST/GET return_url, timeouts): https://www.transbankdevelopers.cl/documentacion/webpay-plus — **primaria, HIGH**
- Transbank SDK Python — código fuente `transaction.py` (create/commit/status/refund, WebpayOptions, errores tipados): https://github.com/TransbankDevelopers/transbank-sdk-python — **primaria, HIGH**
- FastAPI — Bigger Applications (APIRouter, estructura de paquete): https://fastapi.tiangolo.com/tutorial/bigger-applications/ — **primaria, HIGH**
- FastAPI — OAuth2 con JWT (pwdlib[argon2], PyJWT, Bearer): https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/ — **primaria, HIGH**
- FastAPI — CORS (comodín excluido con credenciales): https://fastapi.tiangolo.com/tutorial/cors/ — **primaria, HIGH**
- google-genai Python SDK README (Client, generate_content, system_instruction, chats): https://github.com/googleapis/python-genai — **primaria, HIGH** · Gemini System Instructions: https://ai.google.dev/gemini-api/docs/system-instructions (nota: docs migrando a API "interactions"; apegarse a la superficie del SDK README)
- React Router — Routing data mode (createBrowserRouter, anidadas, error boundary): https://reactrouter.com/start/data/routing — **primaria, HIGH**
- Deployment free tier (Render/Vercel/Netlify/Fly, cold starts) — artículos secundarios 2026 (dev.to, render.com/docs/deploy-fastapi, snapdeploy.dev) — **secundarias, MEDIUM/LOW**
- Schema e-commerce canónico (users/products/orders/order_items, unit_price snapshot) — práctica común de comunidad, resultados de búsqueda débiles — **LOW, validar en fase de diseño**
- Patrón return-URL → backend → 302 SPA: derivado del contrato oficial POST-a-return_url de Transbank (primaria) + consenso de comunidad; no existe guía primaria de Transbank para SPA — **MEDIUM como patrón derivado**

---
*Architecture research for: e-commerce educativo SPA React + FastAPI con Webpay y Gemini*
*Researched: 2026-09-28*
