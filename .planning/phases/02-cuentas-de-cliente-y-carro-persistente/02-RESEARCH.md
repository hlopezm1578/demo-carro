# Phase 2: Cuentas de cliente y carro persistente - Research

**Researched:** 2026-09-29
**Domain:** Autenticación JWT (FastAPI + PyJWT + pwdlib[argon2]) y estado de cliente (Zustand persist + React Router 8 library mode) — documentados como guías paso a paso en un repo guide-only (D-17); extensión de docs del ciclo (02 requerimientos, 03 diseño, 04 arquitectura/contrato, 05 guías 5+)
**Confidence:** HIGH

## Summary

La fase 2 es la fase de **autenticación y estado de cliente** del proyecto Maura, entregada íntegramente como documentos (el repo es guide-only, D-17): extiende `docs/02_requerimientos.md` (nuevos RF/HU/RN continuando la numeración), `docs/03_diseno.md` (entidad USUARIO + 4 pantallas nuevas), `docs/04_arquitectura/` (contrato `contrato_api.yaml` ANTES de las guías — D-15/D-15 API-first — más ADRs 009+) y `docs/05_desarrollo/` (guías 5+). Las decisiones de producto ya están locked en `02-CONTEXT.md` (D-19..D-33): token único JWT de 7 días en localStorage vía Zustand persist, interceptor 401, seed de admin/cliente demo por env vars, carro `[{producto_id, cantidad}]` hidratado contra la API, `/checkout` protegido con returnTo genérico.

El trabajo de esta investigación fue triple: (1) **verificar los patrones oficiales actuales contra el stack fijado** — el tutorial oficial de FastAPI usa exactamente pwdlib (`PasswordHash.recommended()` = Argon2) + PyJWT con `OAuth2PasswordRequestForm` (login form-encoded) y `OAuth2PasswordBearer`, lo que habilita el botón Authorize de `/docs` — pedagógicamente valioso para la verificación contrato ↔ `/docs` de cierre de fase; (2) **mapear los puntos de integración exactos** que las guías nuevas deben tocar: `allow_methods=["GET"]` del CORS de guia-01 debe extenderse a POST, `Settings` gana `secret_key` + credenciales demo, `lib/api.ts` (hoy solo `apiGet`) gana Bearer + interceptor 401, la Navbar gana badge de carro y estado de sesión (el UI-SPEC de fase 1 dejó dicho explícitamente que "llegan en fases 2+"); (3) **verificar los APIs de Zustand 5 persist y React Router 8** (exports `Navigate`/`Outlet`/`useLocation` confirmados en el tarball 8.4.0) para los patrones de store persistente y rutas protegidas.

**Primary recommendation:** Planificar en el orden API-first del proyecto — (A) docs 02/03 (requerimientos + diseño de la etapa 2, continuando numeración), (B) contrato `contrato_api.yaml` extendido con tag Autenticación, `securitySchemes.bearerAuth`, schemas UsuarioPublico/Token/RegistroCreate y `/api/admin/estado` + ADRs 009+ (APROBADOS antes de guías, D-15), (C) guías 05-08 (backend cuentas → sesión frontend → carro → checkout protegido + Gran verificación final), (D) READMEs de estado. Login con `OAuth2PasswordRequestForm` (form-encoded, estilo tutorial oficial) para que `/docs` permita probar los endpoints protegidos con las cuentas del seed.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
*La numeración D continúa desde la fase 1 (D-01..D-18 en `01-CONTEXT.md`).*

#### Sesión JWT
- **D-19:** **Token único de larga vida — sin refresh tokens.** Un solo access token emitido al login; no existe endpoint `/refresh`. La complejidad de renovación queda fuera de la guía (comentario para el alumno curioso, no código) — **Reversibility:** reversible — agregar refresh después solo suma un endpoint y no rompe contrato publicado previo.
- **D-20:** **Duración del token: 7 días** (claim `exp`) — sesión cómoda para una tienda; el claim se lee claro en jwt.io durante la mini-verificación de la guía.
- **D-21:** **La SPA guarda el token en localStorage** vía el store de auth de Zustand con middleware `persist`: sobrevive recargas, cierre de pestaña y los full-page loads de Webpay (fase 3). El ADR de JWT deja dicha la desventaja honesta (XSS) como el costo enseñado del patrón — **Reversibility:** costly — cambiar el almacenamiento después reescribe `lib/api.ts`, el store de auth y las guías de las fases 2-4.
- **D-22:** **Interceptor 401 → login.** `lib/api.ts` detecta 401 en cualquier llamada autenticada: limpia la sesión, redirige a `/login` y muestra "Tu sesión expiró, ingresa de nuevo". Se enseña una sola vez y las fases 3-4 lo heredan gratis.

#### Cuenta admin
- **D-23:** **El admin nace del seed con variables de entorno.** La siembra idempotente (mismo patrón upsert de los 12 SKU, ahora por email) crea/actualiza el usuario admin leyendo `ADMIN_EMAIL` y `ADMIN_PASSWORD` del `.env` — cada alumno reinicia su admin sin miedo y la guía enseña secretos por variable de entorno, jamás en código. Nada de credenciales fijas escritas en la guía ni de "primer registrado = admin".
- **D-24:** **El seed crea también una clienta demo** (`CLIENTE_EMAIL`/`CLIENTE_PASSWORD`, rol cliente): la guía verifica el login de ambos roles sin pasos manuales previos y el UAT delegado tiene cuentas predecibles en maura-uat.
- **D-25:** **Regla de contraseña: largo mínimo 8, sin complejidad obligatoria** (recomendación NIST moderna, igual que el tutorial oficial de FastAPI). La guía explica por qué NO forzar complejidad es la práctica actual.
- **D-26:** **409 claro en registro / 401 genérico en login.** Registro con email existente → 409 "Ese email ya tiene cuenta, inicia sesión"; login fallido → 401 genérico "Credenciales incorrectas" sin revelar si el email existe. La asimetría es deliberada y la guía la explica (enumerar cuentas no ayuda a quien se registra, sí a quien intenta entrar).

#### Carro: datos y UX
- **D-27:** **El carro guarda solo `[{producto_id, cantidad}]` en localStorage** — la vista del carro se hidrata consultando la API: el precio mostrado es siempre el vigente del catálogo y la lección queda lista para CART-03 (fase 3: el backend recalcula y jamás confía en el cliente). Sin snapshot de nombre/precio — **Reversibility:** costly — la estructura del store toca todas las operaciones del carro narradas en las guías.
- **D-28:** **UI del carro: página `/carro` + badge contador en el navbar.** La página concentra edición de cantidades, vaciar y el CTA "Finalizar compra". Sin drawer lateral.
- **D-29:** **El botón "Agregar al carro" vive solo en la ficha del producto** (donde ya hay stock visible); las tarjetas del catálogo solo navegan a la ficha, igual que en la fase 1.
- **D-30:** **Las cantidades se tapan al stock vigente** (ficha y carro, leído de la hidratación con la API): sin sobreventa en pantalla desde ya; la validación real del backend (CART-03) queda como segunda barrera en fase 3, no como único muro.

#### Checkout protegido (fase 2)
- **D-31:** **`/checkout` protegida muestra el resumen del pedido** — líneas del carro, cantidades, subtotal y total hidratado con precios vigentes, con el CTA de pago explícitamente deshabilitado y nota "el pago llega en la etapa siguiente". La pantalla queda construida para que fase 3 solo agregue Webpay — **Reversibility:** reversible.
- **D-32:** **returnTo genérico.** El guard guarda la ruta destino y el login devuelve a donde venía el usuario (checkout o cualquier futura protegida). El patrón se enseña una vez y fase 4 lo reutiliza para el panel admin.
- **D-33:** **AUTH-03 se verifica con un endpoint demo mínimo** (`/api/admin/estado` con conteos triviales del catálogo) protegido por rol: enseña la dependencia de seguridad con claim de rol y da un 403 verificable para la clienta. El panel real es fase 4.

### Claude's Discretion
- Claims exactos del token (`sub`, `rol`, `exp`, `iat`) y forma del login (OAuth2PasswordRequestForm form-encoded del tutorial FastAPI vs JSON puro) — lo resuelve research/planner contra el tutorial oficial y el stack (PyJWT 2.15.0, pwdlib[argon2], python-multipart).
- Nombres y estructura exacta de los endpoints nuevos al extender `contrato_api.yaml` (tag Autenticación, schemas Usuario/Token, `/api/auth/*` vs `/api/cuentas/*`).
- Qué ADRs escribe la fase y su título exacto (candidatos naturales: JWT + almacenamiento localStorage, carro client-side, roles desde el primer token), continuando desde ADR-009.
- Numeración nueva de RF/HU/RN/RNF en `02_requerimientos.md` (continuar las series existentes) y cómo se parte el trabajo en sub-guías `guia-05+`.
- Copy exacto de las pantallas (login, registro, carro, checkout) y sus estados vacíos, respetando los tokens de `01-UI-SPEC.md`.
- Integración del estado de sesión en el navbar (nombre de la clienta, cerrar sesión) y del badge del carro.
- Valores demo concretos de `ADMIN_*`/`CLIENTE_*` en el `.env.example` que la guía muestra.

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| AUTH-01 | Cliente puede crear cuenta con email y contraseña | Contrato: POST registro JSON con validación (email `EmailStr`, password `min_length=8` D-25) → 422 automático Pydantic; 409 con detail "Ese email ya tiene cuenta, inicia sesión" (D-26). Patrón layered: models/usuario + schemas + repository por email + service + router. Tutorial FastAPI (pwdlib hash al crear) [CITED: fastapi.tiangolo.com/tutorial/security/oauth2-jwt/] |
| AUTH-02 | Iniciar sesión y mantener la sesión (JWT) entre recargas | Login `OAuth2PasswordRequestForm` (tutorial) → Token; store Zustand `persist` sobre localStorage (default storage, hidratación síncrona) [CITED: pmndrs/zustand docs]; `get_current_user` con `jwt.decode(..., algorithms=["HS256"])` capturando `InvalidTokenError` → 401 con `WWW-Authenticate: Bearer` [CITED: tutorial] |
| AUTH-03 | Rol admin accede a endpoints protegidos (claim de rol desde el primer token) | Claim `rol` en el payload del login; dependencia `get_current_admin` que valida el rol y lanza 403; endpoint demo `/api/admin/estado` (D-33); cuentas admin/cliente sembradas por env (D-23/D-24) permiten verificar 200 vs 403 sin pasos manuales |
| AUTH-04 | El checkout requiere sesión iniciada | `<RequireAuth>` wrapper con `<Navigate to="/login" state={{ from: location }} replace />` (patrón canónico library mode; exports verificados en tarball react-router 8.4.0) + login que lee `location.state?.from` y `navigate(from, { replace: true })` — el returnTo genérico D-32 |
| CART-01 | Agregar productos al carro, editar cantidades, vaciarlo | Store Zustand del carro con items `{producto_id, cantidad}` (D-27); botón solo en ficha (D-29); página `/carro` con edición/vaciado (D-28); cantidades tapadas al stock de la hidratación (D-30) |
| CART-02 | El carro persiste en el navegador (localStorage) y sobrevive full-page loads | `persist` de Zustand sobre localStorage — el storage por defecto del middleware, sobrevive full-page loads (la hidratación de localStorage es síncrona, disponible al primer render en SPA) [CITED: pmndrs/zustand docs]; sin snapshot de precio (D-27) |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

No existe `./CLAUDE.md` ni `./.claude/CLAUDE.md` [VERIFIED: `ls` esta sesión]. Las instrucciones del proyecto viven en `D:/Repos/demo-carro/AGENTS.md` (workspace instructions). Directivas accionables para el planner:

- **Repo guide-only (D-17/ADR-008):** esta fase escribe SOLO documentos (`docs/**`, `.planning/**`). Jamás código de aplicación en el repo; el código vive como bloques dentro de las guías. Verificación de planes: documental (greps/estructura), nunca ejecutando código.
- **UAT delegado al agente** en `D:/Repos/maura-uat` (instrucción persistida en AGENTS.md): las verificaciones runtime corren ahí, con Node portátil v22.23.3. **Bugs: se corrigen SIEMPRE en los dos lugares** — maura-uat (para desbloquear) Y en la guía `docs/05_desarrollo/*` (el producto). Autorización explícita para editar guías directamente cuando son fixes de bugs.
- **Stack versionado autoritativo** (AGENTS.md / `.planning/research/STACK.md`): PyJWT 2.15.x, pwdlib[argon2] 0.3.1, Zustand 5.0.15, TanStack Query 5.104, python-multipart (en `fastapi[standard]`). "What NOT to use": `python-jose` (CVEs) → PyJWT; `passlib` (sin mantenimiento) → pwdlib[argon2]. Los docs nuevos no deben introducirlos ni como alternativa.
- **Sin emojis en comunicación con el usuario** (los docs de la guía usan sus marcadores propios 🧠/✅/📝 — contenido del producto).
- **Comandos de guías agnósticos de terminal (D-12):** PowerShell/cmd/Git Bash por igual — relevante p. ej. para generar el `SECRET_KEY` (ver Pitfall 3).
- **Respuestas en español chileno, tuteo** (convención del producto ya establecida en todos los docs).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Registro/login/validación de credenciales | API / Backend | — | Hash Argon2 y verificación jamás en el cliente; el password viaja una vez por HTTPS (dev: localhost) y no se persiste |
| Emisión y verificación del JWT (claims sub/rol/exp/iat) | API / Backend | — | `SECRET_KEY` vive solo en el backend (`.env`); firmar/verificar es responsabilidad del emisor |
| Almacenamiento del token (localStorage) | Browser / Client | — | D-21 locked: persistencia entre recargas/full-page loads es un asunto del navegador |
| Adjuntar Bearer + interceptor 401 | Browser / Client (lib/api.ts) | — | Regla 5 de dependencia: TODO HTTP pasa por `lib/api.ts` — el token se lee del store dentro de api.ts |
| Guard de rutas protegidas + returnTo | Browser / Client (React Router) | — | Guard de UI: UX, no seguridad. La seguridad real es el 401/403 del backend (lección explícita de la guía) |
| Estado del carro (datos) | Browser / Client (Zustand persist) | — | D-27: solo `{producto_id, cantidad}`; sin precios — el servidor recalcula |
| Hidratación del carro (precios/stock vigentes) | API / Backend | Browser / Client (TanStack Query) | El precio mostrado viene SIEMPRE de la API; el cliente nunca decide precios |
| Control de acceso por rol (403) | API / Backend | — | `get_current_admin` es dependencia del servidor; el cliente solo oculta botones (cortesía, no seguridad) |
| Seed de cuentas demo (admin/cliente) | API / Backend (script) | Database / Storage | Mismo tier que el seed de productos: `uv run python -m app.seed` sobre SQLAlchemy |
| ADRs + contrato extendido | Documentación (`docs/04_arquitectura/`) | — | Artefacto de build-time; el contrato ANTES de las guías (D-15/ADR-007) |
| Guías 5+ | Documentación (`docs/05_desarrollo/`) | — | El "output" de la fase; código narrado como bloques |

## Standard Stack

> Fuente base: `.planning/research/STACK.md` (verificado 2026-09-28) + `.planning/research/ARCHITECTURE.md`. Los ítems abajo fueron re-verificados contra registro esta sesión (2026-09-29).

### Nuevos paquetes que las guías enseñan a instalar (fase 2)

| Library | Version | Registry check (esta sesión) | Purpose | Why Standard |
|---------|---------|------------------------------|---------|--------------|
| zustand | 5.0.15 | `npm view zustand version` → 5.0.15 [VERIFIED: npm registry] | Stores de cliente: auth (token persist) + carro (items persist) | Fijado en STACK.md; `persist` con localStorage por defecto [CITED: pmndrs/zustand] |
| pyjwt | 2.15.1 (latest; STACK registra 2.15.0) | PyPI JSON API → 2.15.1, requires-python >=3.9 [VERIFIED: pypi.org] | `jwt.encode`/`jwt.decode` HS256 | Lo que usa el tutorial oficial de FastAPI hoy; reemplaza a python-jose (CVEs) [CITED: fastapi.tiangolo.com/tutorial/security/oauth2-jwt/] |
| pwdlib[argon2] | 0.3.1 | PyPI JSON API → 0.3.1, requires-python >=3.10 [VERIFIED: pypi.org] | Hash de contraseñas (`PasswordHash.recommended()` = Argon2) | Elección del tutorial oficial; reemplaza a passlib (sin mantenimiento) [CITED: fastapi.tiangolo.com + frankie567.github.io/pwdlib] |
| python-multipart | 0.0.32 | PyPI JSON API → 0.0.32 [VERIFIED: pypi.org] | Parsing del form de login (`OAuth2PasswordRequestForm`) | Ya viene en `fastapi[standard]` (STACK); el tutorial enseña `uv add python-multipart` explícito [CITED: fastapi.tiangolo.com/tutorial/request-forms/] |

**Instalación que las guías narran (comandos del alumno):**

```bash
# Backend (desde backend/ del monorepo del alumno)
uv add pyjwt "pwdlib[argon2]" python-multipart

# Frontend (desde frontend/)
npm install zustand
```

**Nota de versión PyJWT:** STACK.md fija 2.15.0; el registro ya sirve 2.15.1 (patch, publicada 2026-09-28). Sin pins exactos en la guía (`uv add pyjwt`) el alumno obtiene 2.15.x — sin riesgo de breaking (API estable encode/decode). No perjudica el techo Python 3.12 (requires-python >=3.9).

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `OAuth2PasswordRequestForm` (form-encoded) | Login con JSON `{email, password}` | JSON es más uniforme con el resto del contrato, PIERDE el botón Authorize de `/docs` y diverge del tutorial oficial que el alumno puede contrastar. Ver Pattern 3 para la recomendación |
| Token único 7 días (D-19) | Access corto + refresh token | Locked NO por CONTEXT (D-19); el tutorial usa 30 min — la guía explica por qué una tienda acepta 7 días y qué ganaría un refresh |
| localStorage (D-21) | httpOnly cookie | Mitiga XSS robando token, pero exige backend en el mismo origen/cookies CORS `credentials` — rompe la separación estricta de tiers y complica Webpay (fase 3). Locked localStorage con desventaja honesta en ADR |
| Carro client-side hidratado (D-27) | Carro server-side en BD | Requiere sesión para armar carro y una tabla `cart_items`; el visitante anónimo no podría armarlo. Locked client-side |
| Fetch por-item para hidratar carro | Endpoint nuevo `?ids=1,2,3` en /api/productos | Por-item reusa el contrato vigente sin tocarlo (N≤12 GETs cacheados por TanStack Query); `?ids` es más "correcto" a escala pero crece el contrato en la fase equivocada. Recomendado por-item (ver Open Questions) |
| Zustand para el carro | TanStack Query con queryClient.setQueryData | El carro NO es server state (no existe aún en el servidor): persistencia + mutaciones síncronas locales son el caso de uso exacto de Zustand |

## Package Legitimacy Audit

> Protocolo ejecutado vía seam `package-legitimacy check` esta sesión. Nota de ambiente: para PyPI el seam no tiene métrica de weekly-downloads (`unknown-downloads` es inherente a PyPI) y marca `too-new` cuando la última release es de horas/días — un artefacto ya documentado en STACK.md para `fastapi`.

| Package | Registry | Age | Downloads | Source Repo | Verdict (seam) | Disposition |
|---------|----------|-----|-----------|-------------|----------------|-------------|
| zustand | npm | ~5 años | 63.7M/sem [VERIFIED: seam signals] | github.com/pmndrs/zustand | OK | Approved |
| pyjwt | pypi | ~11 años | n/d (PyPI no expone) | github.com/jpadilla/pyjwt | SUS (artefacto: `unknown-downloads` + release 2026-09-28 → `too-new`) | Approved — cross-check autoritativo: es la librería que instala el tutorial oficial de FastAPI [CITED: fastapi.tiangolo.com]; repo oficial jpadilla/pyjwt, no deprecada |
| pwdlib | pypi | ~2 años | n/d (PyPI no expone) | github.com/frankie567/pwdlib | SUS (artefacto: `unknown-downloads`) | Approved — cross-check autoritativo: librería que instala el tutorial oficial de FastAPI [CITED: fastapi.tiangolo.com]; author maintenedor de FastAPI-users |
| python-multipart | pypi | ~6 años | n/d | github.com/Kludex/python-multipart | (no probeado en seam) | Approved — viene dentro de `fastapi[standard]` [CITED: STACK.md + tutorial request-forms] |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** pyjwt y pwdlib por el seam — ambos con veredicto explicado como artefacto de métricas PyPI y respaldados por la fuente más autoritativa posible (el tutorial oficial de FastAPI instala exactamente estos paquetes). No se exige `checkpoint:human-verify` para sus installs; si el planner prefiere el gate conservador, es barato de añadir.

## Architecture Patterns

### System Architecture Diagram

```
                FLUJO 1 — LOGIN Y SESIÓN PERSISTENTE (AUTH-01/02/03)
                ═════════════════════════════════════════════════════

  [Clienta] ── POST /api/auth/login (form-encoded) ──► ┌── API FASTAPI (capas) ──┐
                                                        │ routers/auth: valida    │
                                                        │  OAuth2PasswordRequest  │
                                                        │ services/cuentas:       │
                                                        │  verify(password, hash) │
                                                        │  └─ pwdlib Argon2       │
                                                        │ security.py: jwt.encode │
                                                        │  {sub, rol, exp, iat}   │
                                                        └───────┬─────────────────┘
                                                        SQLite: users (email unique)
   ◄──── {access_token, token_type} ───────────────────────────┘
   ┌── NAVEGADOR (SPA) ─────────────────────────────────────────┐
   │ useAuthStore (Zustand + persist → localStorage)            │
   │  token + usuario sobreviven recargas y full-page loads     │
   │ lib/api.ts: Authorization: Bearer <token> en cada llamada  │
   │  └─ 401 → logout() → /login?expirada=1 (interceptor D-22)  │
   └────────────────────────────────────────────────────────────┘
        │ GET /api/auth/perfil (Bearer)      │ GET /api/admin/estado (Bearer)
        ▼                                    ▼
   200 usuario ◄─ jwt.decode OK       200 (rol=admin) / 403 (rol=cliente)
                                          └─ get_current_admin dep.

                FLUJO 2 — CARRO PERSISTENTE + CHECKOUT PROTEGIDO (CART-01/02, AUTH-04)
                ════════════════════════════════════════════════════════════════════

  [Visitante] ── ficha /productos/:id ── "Agregar al carro" (D-29)
        │
        ▼
   useCarroStore (Zustand + persist → localStorage)      ← SOLO {producto_id, cantidad} (D-27)
        │ cantidad tapada al stock vigente (D-30)
        ▼
   /carro: hidratación → GET /api/productos/{id} por item (TanStack Query)
        │  precio mostrado = vigente del catálogo, JAMÁS del localStorage
        ▼
   CTA "Finalizar compra" ──► /checkout (RUTA PROTEGIDA)
        │
        ├─ sin sesión: <RequireAuth> → <Navigate to="/login" state={{from: location}} replace/>
        │              login OK → navigate(from, {replace:true})   ← returnTo genérico (D-32)
        │
        └─ con sesión: resumen hidratado (líneas + subtotal + total)
                       CTA pago DESHABILITADO + "el pago llega en la etapa siguiente" (D-31)

  PARALELO API-FIRST (D-15): contrato_api.yaml se extiende y APRUEBA antes de las guías;
  cierre: /docs ≈ contrato (fila de la Gran verificación final, ADR-007)
```

### Recommended Project Structure

Archivos que la fase crea/extiende en ESTE repo (todo documento):

```
demo-carro/
├── docs/
│   ├── README.md                        # EXTENDER: fila 5 del ciclo avanza (guías 5-8)
│   ├── 02_requerimientos.md             # EXTENDER: etapa 2 — nuevos actores, RF-06+, RNF-05+, RN-05+, HU-05+, §13 P5
│   ├── 03_diseno.md                     # EXTENDER: entidad USUARIO + pantallas 4-7 + procesos 5.0+ + §5
│   ├── 04_arquitectura/
│   │   ├── contrato_api.yaml            # EXTENDER ANTES DE GUÍAS (D-15): tag Autenticación,
│   │   │                                #   securitySchemes.bearerAuth, /api/auth/*, /api/admin/estado
│   │   ├── README.md                    # EXTENDER: índice ADRs 009+, árbol del proyecto del alumno
│   │   └── adr/
│   │       ├── 009-*.md                 # NUEVO: JWT larga vida + localStorage (D-19..D-22)
│   │       ├── 010-*.md                 # NUEVO: carro client-side (D-27..D-30)
│   │       └── 011-*.md                 # NUEVO: roles desde el primer token (D-23/D-24/D-33)
│   └── 05_desarrollo/
│       ├── README.md                    # EXTENDER: filas guías 5-8 con estado
│       ├── guia-05-*.md                 # NUEVO: backend cuentas (modelo users, security.py, auth router, seed usuarios)
│       ├── guia-06-*.md                 # NUEVO: sesión frontend (store auth, login/registro, navbar, interceptor, RequireAuth)
│       ├── guia-07-*.md                 # NUEVO: carro (store, ficha, /carro, badge)
│       └── guia-08-*.md                 # NUEVO: checkout protegido + Gran verificación final fase 2
└── README.md                            # EXTENDER: tabla fase 5 (guías 1-8), stack menciona JWT
```

Estructura del proyecto del alumno que las guías construyen (fuera del repo, D-17 — extiende el árbol de `docs/04_arquitectura/` §4):

```
backend/app/
├── config.py          # Settings GANA: secret_key, access_token_expire, admin_email/password, cliente_email/password
├── security.py        # NUEVO: PasswordHash, verify/hash, create_access_token, OAuth2PasswordBearer,
│                      #   get_current_user (401), get_current_admin (403)
├── models/usuario.py  # NUEVO: RolUsuario enum (cliente|admin, nombre==valor), Usuario (email unique)
├── schemas/usuario.py # NUEVO: RegistroCreate, UsuarioPublico, Token
├── repositories/usuario.py  # NUEVO: por_email, crear
├── services/cuentas.py      # NUEVO: registrar (409), autenticar (401 genérico)
├── routers/auth.py          # NUEVO: POST /api/auth/registro, /api/auth/login, GET /api/auth/perfil
├── routers/admin.py         # NUEVO: GET /api/admin/estado (get_current_admin)
├── main.py            # EXTENDER: include_router auth/admin; CORS allow_methods += POST
└── seed.py            # EXTENDER: upsert usuarios por email (ADMIN_*/CLIENTE_* del .env)
frontend/src/
├── lib/api.ts         # EXTENDER: apiPost/apiPostForm + Authorization Bearer + interceptor 401 (D-22)
├── types/api.ts       # EXTENDER: UsuarioPublico, Token, RegistroPayload (espejo del contrato, D-09)
├── stores/ (o lib/)   # NUEVO: useAuthStore.ts (persist token+usuario), useCarroStore.ts (persist items)
├── components/RequireAuth.tsx  # NUEVO: guard con returnTo (D-32)
├── components/Navbar.tsx       # EXTENDER: badge carro + sesión (login/cerrar sesión)
├── features/cuentas/  # NUEVO: Login.tsx, Registro.tsx
├── features/carro/    # NUEVO: Carro.tsx
├── features/checkout/ # NUEVO: Checkout.tsx (resumen + CTA deshabilitado, D-31)
└── main.tsx           # EXTENDER: rutas /login, /registro, /carro, /checkout (protegida)
```

*(La ubicación exacta de los stores — `src/stores/` vs `src/lib/` — es discretion del planner; el innegociable es la regla 6 de dependencia: features no se importan cruzados, lo compartido baja a components/ o lib/.)*

### Pattern 1: Autenticación en capas — el tutorial oficial adaptado a las reglas del proyecto

**Qué:** el tutorial oficial de FastAPI usa pwdlib + PyJWT con `OAuth2PasswordRequestForm`; el proyecto lo traduce a las capas routers → services → repositories (reglas de `docs/04_arquitectura/` §4).

```python
# Source: fastapi.tiangolo.com/tutorial/security/oauth2-jwt/ (current) — import surface verificada esta sesión
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()   # Argon2 con parámetros por defecto

def verify_password(plain: str, hashed: str) -> bool:
    return password_hash.verify(plain, hashed)   # OJO: password PRIMERO, hash después

def get_password_hash(password: str) -> str:
    return password_hash.hash(password)
```

```python
# app/security.py — dependencias de seguridad (nuevo módulo transversal)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")  # habilita Authorize en /docs

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_session),
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales incorrectas",          # 401 GENÉRICO (D-26)
        headers={"WWW-Authenticate": "Bearer"},     # header del tutorial
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:                        # incluye ExpiredSignatureError
        raise credentials_exception
    usuario = UsuarioRepository(db).por_id(int(user_id))
    if usuario is None:
        raise credentials_exception
    return usuario

async def get_current_admin(
    current: Annotated[Usuario, Depends(get_current_user)],
) -> Usuario:
    if current.rol != RolUsuario.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requiere rol admin")
    return current
```

**Notas:** el tutorial captura `InvalidTokenError` (base de la jerarquía de errores de PyJWT, incluye `ExpiredSignatureError`) y devuelve 401 con `headers={"WWW-Authenticate": "Bearer"}` [CITED: tutorial]. Para el rol, 403 es lo semánticamente correcto y lo que el propio contrato ya reserva: "`| 403 | Con sesión, pero sin permiso | Reservado (fases 2+) |`" [VERIFIED: docs/04_arquitectura/contrato_api.yaml:29]. El lookup de usuario en la dependencia usa la sesión inyectada — los routers siguen sin importar SQLAlchemy.

### Pattern 2: Claims del token (discretion — recomendación)

```python
# Source: tutorial (create_access_token) + PyJWT usage docs — adaptado a D-19/D-20
from datetime import datetime, timedelta, timezone

def create_access_token(usuario: Usuario) -> str:
    expira = datetime.now(timezone.utc) + timedelta(days=settings.token_dias)  # 7 días (D-20)
    payload = {
        "sub": str(usuario.id),      # string único app-wide (recomendación del tutorial)
        "rol": usuario.rol.value,    # claim custom: rol desde el PRIMER token (AUTH-03)
        "exp": expira,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")
```

- `sub` como `str(usuario.id)`: el tutorial recomienda que `sub` sea identificador único como string. Usar el id (no el email) deja abierto renombrar emails sin invalidar tokens; el lookup de `/api/auth/perfil` va por id. Alternativa `sub = email` es igualmente válida y más legible en jwt.io — decisión de planner (ver Assumptions).
- `exp` con `datetime.now(timezone.utc)` — timezone-aware; los docs de PyJWT comparan contra UTC actual [CITED: pyjwt readthedocs]. `utcnow()` está deprecado en 3.12 (pitfall).
- PyJWT convierte datetime → int UNIX automáticamente al encodear [CITED: pyjwt readthedocs].
- `algorithms=["HS256"]` en decode SIEMPRE (lista) [CITED: tutorial + pyjwt docs].
- Mini-verificación de la guía: decodificar el payload offline con `uv run python -c "import jwt; print(jwt.decode(TOKEN, options={'verify_signature': False}))"` (D-20 menciona jwt.io; el one-liner Python evita enviar el token a un sitio externo — mejor prerrequisito de aula).

### Pattern 3: Login con OAuth2PasswordRequestForm (discretion — recomendación)

**Recomendado: form-encoded del tutorial.** El login del tutorial oficial:

```python
# Source: fastapi.tiangolo.com/tutorial/security/oauth2-jwt/ (verbatim del tutorial, adaptado el path)
@router.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_session),
) -> Token:
    usuario = CuentasService(UsuarioRepository(db)).autenticar(
        form_data.username, form_data.password   # username = email de la clienta
    )
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",   # genérico deliberado (D-26)
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(usuario), token_type="bearer")
```

**Por qué form-encoded y no JSON (3 razones):**
1. **El botón Authorize de `/docs` funciona**: `OAuth2PasswordBearer(tokenUrl=...)` hace que Swagger UI muestre el candado — el alumno pega las credenciales del seed y prueba `/api/admin/estado` (200) y `/api/auth/perfil` desde el propio panel, alimentando la comparación contrato ↔ `/docs` del cierre (ADR-007) [CITED: tutorial, que usa exactamente este mecanismo].
2. **Es el tutorial oficial**: el alumno puede contrastar la guía con la documentación de FastAPI 1:1.
3. `python-multipart` ya viene en `fastapi[standard]` (y el tutorial enseña a instalarlo explícito) [CITED: fastapi.tiangolo.com/tutorial/request-forms/ — "To use forms, first install python-multipart"].

**Costos a narrar honestamente:** el campo del form se llama `username` aunque transporte un email (el contrato lo documenta: "username = email de la clienta"), y el frontend necesita un helper que envíe `FormData` (ver Pattern 4). En OpenAPI el body es `application/x-www-form-urlencoded` (así lo documenta FastAPI) — el contrato se escribe en consecuencia.

**Registro (sí JSON):** el registro SÍ usa JSON (`RegistroCreate {email: EmailStr, password: str min_length=8}`) — es un endpoint de negocio propio, no OAuth2; el 422 de validación lo produce Pydantic (email formato + largo mínimo D-25) y el 409 ("Ese email ya tiene cuenta, inicia sesión", D-26) lo produce el service al ver el email único.

### Pattern 4: lib/api.ts con Bearer + interceptor 401 (D-21/D-22)

```typescript
// Source: adaptación del lib/api.ts vigente de guia-04 + zustand docs (getState fuera de React)
// lib/api.ts actual (fase 1): ApiError con status + apiGet — base intocable [VERIFIED: guia-04:751-775]
import { useAuthStore } from "../stores/useAuthStore";

function authHeaders(): HeadersInit {
  const token = useAuthStore.getState().token;   // getState() fuera de React: API pública de Zustand
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function apiGet<T>(ruta: string): Promise<T> {
  const res = await fetch(`${base}/${ruta}`, { headers: authHeaders() });
  if (res.status === 401) {
    useAuthStore.getState().cerrarSesion();      // limpia token+usuario (y el localStorage del persist)
    window.location.assign("/login?expirada=1"); // D-22: redirige + la pantalla muestra el aviso
  }
  // ... resto igual al ApiError vigente de guia-04
}

export async function apiPostForm<T>(ruta: string, form: FormData): Promise<T> {
  const res = await fetch(`${base}/${ruta}`, { method: "POST", body: form, headers: authHeaders() });
  // NOTA: con FormData NO setear Content-Type manualmente (el navegador pone el boundary)
  // ... mismo manejo de error que apiGet
}
```

- `window.location.assign` (full navigation) en el interceptor es aceptable y honesto: un 401 significa sesión muerta — recargar la app limpia la caché de TanStack Query de un golpe. La pantalla de login lee `?expirada=1` y muestra "Tu sesión expiró, ingresa de nuevo" (mensaje locked D-22). Alternativa más fina (evento + useNavigate dentro de React) complica la lección sin ganancia pedagógica.
- El interceptor NO debe dispararse en el propio `/api/auth/login` (un 401 de credenciales incorrectas se maneja en el formulario, no redirige): patrón — excluir la ruta de login del redirect, o aplicar el interceptor solo a llamadas con Bearer adjunto.

### Pattern 5: Stores Zustand con persist (auth + carro)

```tsx
// Source: pmndrs/zustand docs (persist + createJSONStorage + partialize) — verificado esta sesión
import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

// stores/useAuthStore.ts
export const useAuthStore = create<State>()(
  persist(
    (set) => ({
      token: null as string | null,
      usuario: null as UsuarioPublico | null,
      iniciarSesion: (token, usuario) => set({ token, usuario }),
      cerrarSesion: () => set({ token: null, usuario: null }),
    }),
    {
      name: "maura-auth",                                   // clave de localStorage
      storage: createJSONStorage(() => localStorage),        // default explícito (didáctico)
      partialize: (state) => ({ token: state.token, usuario: state.usuario }), // SOLO datos, jamás funciones
    }
  )
);

// stores/useCarroStore.ts — SOLO {producto_id, cantidad} (D-27)
type ItemCarro = { producto_id: number; cantidad: number };
export const useCarroStore = create<CarroState>()(
  persist(
    (set, get) => ({
      items: [] as ItemCarro[],
      agregar: (producto_id, cantidad = 1) => { /* set con lógica de merge de cantidad */ },
      cambiarCantidad: (producto_id, cantidad) => { /* set */ },
      quitar: (producto_id) => set({ items: get().items.filter((i) => i.producto_id !== producto_id) }),
      vaciar: () => set({ items: [] }),
    }),
    {
      name: "maura-carro",
      partialize: (state) => ({ items: state.items }),
    }
  )
);
```

- `persist(fn, { name })` usa localStorage por defecto; `createJSONStorage(() => localStorage)` explícito enseña el mecanismo [CITED: pmndrs/zustand README]. localStorage es síncrono → el estado persistido está disponible al primer render en la SPA (sin parpadeo de sesión).
- `partialize` es la opción documentada para persistir un subconjunto — aquí: solo datos, nunca acciones [CITED: zustand docs persisting-store-data].
- El carro guarda ids+cantidades; la página `/carro` hidrata cada item con `useQuery(["producto", id])` (ya cacheado por la ficha si el alumno vino de ahí) — el precio mostrado es el vigente (D-27). Cantidad tapada a `producto.stock` en la UI (D-30).
- Badge del navbar: `useCarroStore((s) => s.items.reduce((n, i) => n + i.cantidad, 0))`.

### Pattern 6: Rutas protegidas + returnTo genérico (D-32, AUTH-04)

```tsx
// Source: patrón del ejemplo oficial de React Router (library mode, estable v6→v8);
// exports Navigate/Outlet/useLocation verificados en tarball react-router@8.4.0 esta sesión
// components/RequireAuth.tsx
import { Navigate, Outlet, useLocation } from "react-router";
import { useAuthStore } from "../stores/useAuthStore";

export default function RequireAuth() {
  const token = useAuthStore((s) => s.token);
  const location = useLocation();
  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return <Outlet />;
}

// features/cuentas/Login.tsx — volver a donde venía
const location = useLocation();
const navigate = useNavigate();
const from = location.state?.from?.pathname ?? "/";
// tras login exitoso:
navigate(from, { replace: true });
```

```tsx
// main.tsx — rutas nuevas de la fase (extiende las 4 vigentes de guia-02/04)
<Route element={<RequireAuth />}>
  <Route path="/checkout" element={<Checkout />} />
</Route>
```

- `replace` evita el bucle atrás (login no queda en el historial tras el redirect).
- Lección explícita de la guía: el guard es UX; la seguridad real es el 401/403 del backend (si alguien fuerza el token, el backend lo rechaza y el interceptor actúa).
- React Router 8: imports desde `"react-router"` (v8 eliminó react-router-dom) — [VERIFIED: tarball 8.4.0, export statement incluye `Navigate`, `Outlet`, `useLocation`, `useNavigate`, `BrowserRouter`].

### Pattern 7: Seed de usuarios — mismo upsert, clave email (D-23/D-24)

```python
# Source: patrón upsert de guia-03 [VERIFIED: guia-03:279-287] extendido a usuarios
from app.config import settings

def upsert_usuario(sesion: Session, email: str, password: str, rol: RolUsuario) -> str:
    existente = sesion.scalar(select(Usuario).where(Usuario.email == email))
    hash_nuevo = get_password_hash(password)
    if existente is None:
        sesion.add(Usuario(email=email, hashed_password=hash_nuevo, rol=rol))
        return "[+]"
    existente.hashed_password = hash_nuevo   # re-ejecutar el seed REINICIA la password al valor del .env:
    existente.rol = rol                      # "cada alumno reinicia su admin sin miedo" (D-23)
    return "[=]"
```

- Misma filosofía de convergencia canónica del seed de productos: re-ejecutar restaura credenciales demo (útil tras pruebas que cambian passwords) — narrarlo como feature deliberada, igual que guia-03 hizo con stock.
- Orden en `main()` del seed: usuarios después de productos (sin FK entre sí hoy; fase 3 conecta órdenes).
- Argon2 es memory-hard: hashear 2 contraseñas en el seed tarda fracciones de segundo — imperceptible, pero la guía puede mencionar por qué es deliberadamente lento (costo de romperlo por fuerza bruta).
- `.env` del backend gana: `SECRET_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `CLIENTE_EMAIL`, `CLIENTE_PASSWORD` — y la guía muestra un `.env.example` con valores demo (discretion; ya está gitignoreado: el `.gitignore` de guia-01 incluye `.env` [VERIFIED: guia-01:315-317]).

### Pattern 8: Extensión del contrato (ANTES de las guías, D-15)

```yaml
# Source: swagger.io/docs/specification/authentication/bearer-authentication/ (sintaxis verificada)
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  schemas:
    # ... existentes Error/ProductoResumen/ProductoDetalle (intactos) +
    UsuarioPublico:    # {id, email, rol} — JAMÁS hashed_password
      type: object
      properties:
        id: { type: integer }
        email: { type: string, format: email }
        rol: { type: string, enum: [cliente, admin] }
      required: [id, email, rol]
    Token:
      type: object
      properties:
        access_token: { type: string }
        token_type: { type: string, example: bearer }
      required: [access_token, token_type]
    RegistroCreate:
      type: object
      properties:
        email: { type: string, format: email }
        password: { type: string, minLength: 8 }   # D-25: largo mínimo 8, sin complejidad
      required: [email, password]

paths:
  /api/auth/registro:
    post:
      tags: [Autenticación]
      security: []          # público
      # requestBody JSON RegistroCreate → 201 UsuarioPublico | 409 Error | 422 Error
  /api/auth/login:
    post:
      tags: [Autenticación]
      security: []
      # requestBody application/x-www-form-urlencoded (username, password) → 200 Token | 401 Error
  /api/auth/perfil:
    get:
      tags: [Autenticación]
      security: [{ bearerAuth: [] }]
      # → 200 UsuarioPublico | 401 Error
  /api/admin/estado:
    get:
      tags: [Administración]
      security: [{ bearerAuth: [] }]
      # → 200 {productos: N, ...} | 401 Error | 403 Error   (D-33)
```

- Versionar: `info.version` 0.1.0 → 0.2.0 (el contrato es la fuente de verdad versionada — ADR-007).
- Actualizar la tabla de la convención de errores del `info.description`: las filas 401/403/409 pasan de "Reservado (fases 2+)" a "En uso (fase 2)" [valores actuales VERIFIED: contrato_api.yaml:22-32].
- Tag nuevo `Autenticación` (+ `Administración` para /api/admin/estado), descripciones que citan AUTH-xx/CART-xx igual que los tags actuales citan STORE-xx.
- Declarar `responses` 401/403 en los endpoints protegidos para que `/docs` los documente — la misma lección del 404 de guia-04 (G-01-4): FastAPI NO documenta excepciones lanzadas a mano si no se declaran en la firma.

### Pattern 9: Convenciones documentales que la fase replica (verificadas en repo)

| Convención | Valor vigente (verbatim) | Fuente |
|---|---|---|
| Numeración a continuar | `RF-01`..`RF-05`, `RNF-01`..`RNF-04`, `RN-01`..`RN-04`, `HU-01`..`HU-04` | [VERIFIED: docs/02_requerimientos.md:66-134] |
| Actores actuales | tabla con único actor "`Visitante (anónimo)`"; P5-P8 solo en trazabilidad §13 | [VERIFIED: docs/02_requerimientos.md:54-60, 194] |
| P5 (origen de la etapa 2) | "`P5 \| **Carro de compras y cuentas** para las clientas, para comprar en varios pasos y revisar sus pedidos`" | [VERIFIED: docs/01_necesidad_del_cliente.md:61] |
| Formato ADR | Estado/Fecha/Resuelve → Contexto → Opciones consideradas (tabla) → Decisión → Consecuencias (positivas/negativas honestas) → Para conversar en clase | [VERIFIED: docs/04_arquitectura/adr/007-api-first.md:1-54] |
| Estructura de guía | blockquote (Qué construirás/Al terminar tendrás/Necesitas) → tabla de términos → pasos con 🧠 "El desarrollador piensa" + código + ✅ mini-verificación → ❌ error evitado → ✅ verificación → 📝 punto de control → Lo que acabas de aprender → Siguiente | [VERIFIED: guia-03/guia-04 completas] |
| Gran verificación final | tabla numerada con columna Origen (cita CS/RF/ADR) + fila final contrato ↔ `/docs`; "este mismo mecanismo se repite al final de cada fase" | [VERIFIED: guia-04:971-1005] |
| Reglas de dependencia | 6 reglas numeradas (routers sin SQLAlchemy; todo HTTP por `lib/api.ts`; features sin imports cruzados; solo main.py arma la app) | [VERIFIED: docs/04_arquitectura/README.md:154-166] |
| Trazabilidad del ciclo | P/C/CS → RF/RNF/RN/HU → diseño §5 → ADRs → guías; todas las series continúan | [VERIFIED: 02_requerimientos §13 + 03_diseno §5] |

### Anti-Patterns to Avoid

- **Hash de contraseñas en el frontend, o enviar hashed_password al cliente** — el hash se calcula y verifica SOLO en el backend; `UsuarioPublico` no incluye el campo (el schema lo excluye por omisión, como `activo` en productos).
- **`allow_origins=["*"]` o ampliar CORS a lo loco** — solo agregar `"POST"` a `allow_methods` (ver Pitfall 1).
- **Guardar precios en el carro** — D-27 lo prohíbe: precio vigente siempre desde la API; el cliente nunca decide precios.
- **Guard de ruta como "seguridad"** — el guard es UX; sin el 401/403 del backend cualquiera con curl ve el endpoint. La guía lo dice explícito.
- **`jwt.decode` sin `algorithms`** — obligatorio lista explícita `["HS256"]`; nunca confiar en el alg del header del token (alg-confusion).
- **JWT en python-jose o hash en passlib** — prohibidos por el stack (What NOT to Use): python-jose tiene CVEs abiertas, passlib sin mantenimiento desde 2020.
- **Diferencia de validación en login vs registro** — password de 7 chars en login NO debe dar 422 de schema (el login solo verifica contra el hash → 401 genérico); el `min_length=8` vive en `RegistroCreate`, no en el form de login.
- **Token en el contrato OpenAPI como esquema apiKey** — la forma correcta 3.0 es `type: http, scheme: bearer` [CITED: swagger.io].

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Hash de password | SHA-256/BCrypt a mano, salt propio | pwdlib `PasswordHash.recommended()` (Argon2) | Argon2 memory-hard con parámetros revisados; salt y formato `$argon2id$` manejados por la librería [CITED: tutorial + pwdlib docs] |
| Emitir/validar JWT | jsonwebtoken a mano / python-jose | PyJWT `jwt.encode`/`jwt.decode` con `algorithms=["HS256"]` | Claims registered (`exp`/`iat`/`sub`) validados por la librería; excepciones tipadas (`ExpiredSignatureError` bajo `InvalidTokenError`) |
| Parsing del form de login | leer request body a mano | `OAuth2PasswordRequestForm` (Depends) | Estándar OAuth2 password-flow; habilita Authorize en /docs; python-multipart hace el parseo |
| Persistencia del store | useEffect + localStorage.getItem + setState | Zustand `persist` + `createJSONStorage` | Hidratación, serialización JSON y claves manejadas por el middleware; `partialize` documentado |
| Redirección post-login | query strings manuales `?redirect=` | `Navigate state={{from: location}}` + `location.state?.from` | Estado de router tipado, no hackea la URL; patrón del ejemplo oficial |
| Adjuntar token + manejar 401 en cada componente | copiar fetch con headers en cada feature | interceptor único en `lib/api.ts` (regla 5) | D-22: se enseña una vez, fases 3-4 lo heredan |
| Estados async de las pantallas nuevas | useEffect + flags | TanStack Query `useQuery`/`useMutation` | Mismo patrón uniforme de fase 1 (isPending/isError/vacío) |
| Formateo de precios CLP en carro/checkout | concatenar "$" + puntos | `Intl.NumberFormat("es-CL", {style:"currency", currency:"CLP"})` | Ya verificado en fase 1: produce `$6.990` |

**Key insight:** igual que en fase 1, cada "no lo hagas a mano" ES contenido del curso — el hash Argon2, el JWT y el persist son los tres conceptos nuevos que el alumno debe reconocer en la industria.

## Runtime State Inventory

*(Step 2.5: OMITIDO — fase de documentos greenfield (docs nuevos + extensiones), no rename/refactor/migration. No hay strings renombrados ni estado runtime en este repo.)*

## Common Pitfalls

### Pitfall 1: CORS del backend solo permite GET
**What goes wrong:** guia-01 enseñó `allow_methods=["GET"]` [VERIFIED: guia-01:285-290 — verbatim: `allow_methods=["GET"],`]; el primer POST de login/registro cross-origin recibe bloqueo CORS (preflight OPTIONS rechazado).
**Why:** en dev con el proxy de Vite las llamadas son same-origin y CORS no actúa — el olvido es invisible hasta que la SPA llama al backend en otro origen.
**How to avoid:** la guía de backend auth UPDATEA `main.py`: `allow_methods=["GET", "POST"]` (narrarlo: CORS crece con la API). `allow_headers=["*"]` ya cubre `Authorization`.
**Warning signs:** error `405 Method Not Allowed`/preflight en el navegador cuando la SPA hace POST directo.

### Pitfall 2: `verify(password, hash)` — orden de argumentos
**What goes wrong:** pwdlib es `verify(password, hash)` (password PRIMERO); invertir da `False` sistemático o `UnknownHashError` y "el login nunca funciona para nadie".
**Why:** convención contraintuitiva (uno esperaría hash primero).
**How to avoid:** helper `verify_password(plain, hashed)` estilo tutorial; mini-verificación: login de la clienta seed funciona.
**Warning signs:** TODOS los logins fallan con 401 pese a seed correcto.

### Pitfall 3: SECRET_KEY con openssl en Windows (D-12)
**What goes wrong:** el tutorial sugiere `openssl rand -hex 32`; en PowerShell/cmd de Windows openssl no siempre existe.
**How to avoid:** la guía enseña el one-liner agnóstico de terminal: `uv run python -c "import secrets; print(secrets.token_hex(32))"` (mismo output; cumple D-12). Y el SECRET_KEY vive en `.env` (ya gitignoreado), jamás en código ni en el contrato.

### Pitfall 4: `sub` no-string o `utcnow()` deprecado
**What goes wrong:** (a) encodear `sub` como int rompe la convención JWT (el tutorial exige string único); (b) `datetime.utcnow()` está deprecado en 3.12 y produce naive datetimes — PyJWT compara `exp` contra UTC actual.
**How to avoid:** `sub = str(usuario.id)`; `datetime.now(timezone.utc)` (timezone-aware) — PyJWT convierte datetime → int UNIX al encodear automáticamente.

### Pitfall 5: el interceptor 401 dispara en el propio login
**What goes wrong:** credenciales incorrectas (401 del login) también redirigen a `/login?expirada=1` — el formulario nunca muestra su error.
**How to avoid:** el interceptor aplica solo a llamadas autenticadas (con Bearer) o excluye `/api/auth/*`; el 401 del login lo maneja el formulario con "Credenciales incorrectas" (D-26).

### Pitfall 6: Enum de rol — el gotcha del enum de guia-03, segunda vuelta
**What goes wrong:** declarar `class RolUsuario(str, enum.Enum): CLIENTE = "cliente"` guarda "CLIENTE" en la BD; el contrato enum `[cliente, admin]` diverge (mismo bug documentado para familias).
**How to avoid:** nombre == valor: `cliente = "cliente"`, `admin = "admin"` [lección cerrada en guia-03; SQLAlchemy persiste NOMBRES].

### Pitfall 7: la SPA muestra el rol/badge ANTES de hidratar (parpadeo) o persiste funciones
**What goes wrong:** (a) leer el store antes de la hidratación muestra "no logueado" un frame; (b) `partialize` ausente intenta serializar funciones a JSON.
**How to avoid:** localStorage es síncrono → Zustand hidrata al crear el store (sin flash real en SPA); `partialize` SIEMPRE listando solo datos. Si se usa un storage async (no es el caso), chequear `hasHydrated()`.

### Pitfall 8: el carro referencia un producto que ya no existe
**What goes wrong:** un item persistido cuyo producto fue desactivado/borrado: la hidratación por-item recibe 404 y la página `/carro` revienta o muestra un hoyco.
**How to avoid:** hidratación tolerante: item con 404 → fila "este aroma ya no está disponible" + acción quitar (usa el patrón `ApiError status === 404` de guia-04). La ficha deshabilita "Agregar" si `stock === 0` (D-29/D-30).

### Pitfall 9: 401 vs 403 vs 409 — quién produce qué
**What goes wrong:** mezclar: 401 con sesión válida, 403 sin sesión, 409 para password corta (eso es 422).
**How to avoid:** tabla única en la guía: 422 = schema (Pydantic, automático); 401 = credenciales/token inválido-expirado (security.py); 403 = token válido SIN rol (get_current_admin); 409 = email duplicado en registro (service). Es literalmente la tabla del contrato [VERIFIED: contrato_api.yaml:22-32] pasando a "En uso".

### Pitfall 10: `hashed_password` filtrado en una respuesta
**What goes wrong:** devolver el modelo SQLAlchemy directo expone columnas que el schema no debía publicar.
**How to avoid:** `response_model=UsuarioPublico` en TODOS los endpoints de usuarios (Pydantic filtra por omisión — misma lección de `activo` en guia-04); el modelo puede definirlo, pero la frontera es el schema.

### Pitfall 11: `/docs` no muestra los 401/403 del contrato (drift de cierre)
**What goes wrong:** `HTTPException` a mano no se documenta en OpenAPI: `/docs` lista solo 200/422 y la fila contrato ↔ `/docs` de la Gran verificación final detecta un "desvío" que es solo una declaración faltante.
**How to avoid:** declarar `responses={401: {...}, 403: {...}}` en la firma de los endpoints protegidos — la lección ya aprendida con el 404 (G-01-4, ADR-007).

### Pitfall 12: credenciales demo hardcodeadas en la guía
**What goes wrong:** escribir el password del admin literal en el markdown de la guía viola D-23 ("nada de credenciales fijas escritas en la guía") y enseña el anti-patrón.
**How to avoid:** la guía muestra SOLO el `.env.example` con placeholders demo; los valores reales los define el alumno en su `.env`; el seed lee `settings.admin_email` etc. El `.env` ya está gitignoreado [VERIFIED: guia-01:315-317].

## Code Examples

> Los ejemplos canónicos ya están inline en Architecture Patterns 1-8 con su fuente. Resumen de verificación de fuentes: tutorial FastAPI (pwdlib/PyJWT/OAuth2PasswordRequestForm/get_current_user) y request-forms (python-multipart) [CITED: fastapi.tiangolo.com, fetch esta sesión]; PyJWT usage (claims, algorithms, ExpiredSignatureError, timezone-aware) [CITED: pyjwt.readthedocs.io]; pwdlib reference (hash/verify/verify_and_update, recommended=Argon2) [CITED: frankie567.github.io/pwdlib]; Zustand persist (createJSONStorage/partialize/version/clearStorage) [CITED: pmndrs/zustand README + docs]; OpenAPI bearer (securitySchemes + security por operación) [CITED: swagger.io]; RequireAuth pattern (ejemplo oficial library mode, exports verificados en tarball react-router@8.4.0) [VERIFIED: dist/development/index.d.ts export statement].

### Modelo Usuario (SQLAlchemy — espejo del patrón Producto de guia-03)

```python
# app/models/usuario.py — nombre==valor en el enum (Pitfall 6)
import enum

class RolUsuario(str, enum.Enum):
    cliente = "cliente"
    admin = "admin"

class Usuario(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)  # clave del upsert (D-23/D-24)
    hashed_password: Mapped[str] = mapped_column(String(255))  # "$argon2id$..." — JAMÁS en schemas
    rol: Mapped[RolUsuario] = mapped_column(Enum(RolUsuario), default=RolUsuario.cliente)
```

*(Longitudes de columna: la referencia es el diccionario de datos que escriba 03_diseno §2 extendido — el planner fija los valores exactos al escribir el doc.)*

### Settings extendido (base VERIFIED guia-01:199-206)

```python
class Settings(BaseSettings):
    database_url: str = "sqlite:///./maura.db"
    cors_origins: list[str] = ["http://localhost:5173"]
    # NUEVO fase 2:
    secret_key: str  # sin default: la app no parte sin él (fail-fast del secreto)
    token_dias: int = 7                                   # D-20
    admin_email: str
    admin_password: str
    cliente_email: str
    cliente_password: str
```

*(Sin defaults para secretos fuerza el error temprano si falta el `.env` — decisión de planner; `pydantic-settings` ya está instalado y guia-01 estableció el patrón.)*

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| passlib (bcrypt) | pwdlib `PasswordHash.recommended()` (Argon2) | tutorial oficial FastAPI (2025); passlib sin mantenimiento desde 2020 | La guía usa pwdlib; passlib solo se menciona como legado [CITED: fastapi.tiangolo.com] |
| python-jose | PyJWT (`import jwt`) | tutorial oficial removió python-jose (CVE-2024-33663/33664) | `jwt.decode(token, key, algorithms=["HS256"])` + `InvalidTokenError` [CITED] |
| Reglas de complejidad de password (8-4) | Largo mínimo + screening, sin composición obligatoria | NIST SP 800-63B; Rev 4 (2025+) sube el mínimo a 15 chars si password es el único factor | D-25 (mín 8, sin complejidad) alineado con la revisión original y con el tutorial; la guía puede citar "longitud sobre complejidad" y mencionar la Rev 4 como nota [CITED: pages.nist.gov vía búsqueda — MEDIUM] |
| react-router-dom | imports desde `react-router` | v8 (2026-06-17) | Ya respetado desde fase 1; rutas nuevas igual |
| Refresh tokens obligatorios | Token único de larga vida es aceptable en demos/sandbox; refresh cuando el riesgo lo pida | — | D-19 locked; el ADR deja la evolución dicha |

**Deprecated/outdated (no introducir en docs):**
- `python-jose`, `passlib` — prohibidos (stack What NOT to Use).
- `datetime.utcnow()` — deprecado Python 3.12.
- Guard de ruta como mecanismo de seguridad (siempre fue anti-pattern; hoy el lenguaje de la guía es "guard = UX, backend = seguridad").

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Endpoints `/api/auth/registro|login|perfil` + `/api/admin/estado` (tag `Autenticación`; prefijo `/api/auth` sobre `/api/cuentas`) | Pattern 8 | Bajo — nombres son discretion del planner; el contrato se escribe una vez antes de las guías |
| A2 | Login con `OAuth2PasswordRequestForm` form-encoded (campo `username` transporta el email) | Pattern 3 | Bajo — alternativa JSON es válida; la recomendación maximiza tutorial + Authorize en /docs |
| A3 | `sub = str(usuario.id)` (vs email) | Pattern 2 | Bajo — ambos funcionan; con email el payload es más legible en jwt.io pero renombrar emails invalida la semántica del sub |
| A4 | Registro responde 201 (creación) con `UsuarioPublico`; login/perfil 200 | Pattern 8 | Bajo — 200 también defendible; decidir al escribir el contrato |
| A5 | Hidratación del carro por-item con GET /api/productos/{id} (sin extender el endpoint de listado con `?ids=`) | Pattern 5, Alternatives | Medio — N+1 requests (≤12, cacheados por Query); si el planner prefiere `?ids`, el contrato crece en esta fase |
| A6 | ADRs: 009 JWT+larga vida+localStorage, 010 carro client-side, 011 roles desde el primer token (3 ADRs; 009 puede partirse en JWT vs almacenamiento si crece) | Project Structure | Bajo — discretion; los candidatos están listados en CONTEXT |
| A7 | Guías nuevas: guia-05 backend cuentas, guia-06 sesión frontend, guia-07 carro, guia-08 checkout + Gran verificación final (4 sub-guías, espejo de las 4 de fase 1) | Project Structure | Bajo — 3 también funciona (carro+checkout juntos); D-16 pide partición por hito |
| A8 | Interceptor usa `window.location.assign("/login?expirada=1")` y el login muestra el aviso leyendo el param | Pattern 4 | Bajo — detalle de implementación; alternativa evento+useNavigate |
| A9 | Navbar muestra email truncado + "Cerrar sesión" (no hay campo `nombre` en el modelo) | Project Structure | Bajo — CONTEXT menciona "nombre de la clienta"; sin campo nombre, email es lo honesto. Agregar `nombre` al registro es scope creep (decisión de planner) |
| A10 | `.env.example` con placeholders demo (`ADMIN_EMAIL=maura@maura.cl`, etc. — valores exactos a definir) | Pattern 7 | Bajo — discretion |
| A11 | `Token` schema sin claim `rol` visible (acceso_token + token_type, forma tutorial); el alumno decodifica el payload para ver `rol` en la mini-verificación | Pattern 2/8 | Bajo — agregar campos al Token es válido pero diverge del tutorial |
| A12 | `security.py` como módulo transversal (password hash + jwt + dependencias) fuera de las 4 capas | Project Structure | Bajo — respetar "routers sin SQLAlchemy" es lo innegociable; la ubicación exacta es planner |
| A13 | La fase NO crea tabla de carros en BD ni endpoints de carro (100% client-side hasta fase 3) | Todo | Nulo — locked D-27 + ROADMAP (CART-03 backend en fase 3) |

## Open Questions

1. **¿El contrato expone `format: email` (requiere `email-validator`, ya en `fastapi[standard]`) o valida email a mano?**
   - What we know: `EmailStr` de Pydantic valida formato y `email-validator` ya viene en `[standard]` (STACK verificado).
   - What's unclear: nada técnico — es copy del contrato.
   - Recommendation: usar `format: email` en el contrato + `EmailStr` en el schema (coherente con validación declarativa de fase 1).
2. **¿Mini-verificación del token con jwt.io (sitio externo) o one-liner Python offline?**
   - What we know: D-20 menciona jwt.io; Python decode con `options={"verify_signature": False}` muestra los claims igual sin enviar el token a terceros.
   - Recommendation: one-liner Python como paso de la guía (D-12 agnóstico + no comparte el token con un sitio); jwt.io como mención opcional para el alumno curioso. Decisión del planner al escribir la guía.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| git | commits del repo (guide-only) | ✓ | 2.50.1 | — |
| Node >= 22.22 | UAT delegado (frontend en maura-uat) | ✓ (portátil en maura-uat) | v22.23.3 en `D:/Repos/maura-uat/.tools/node-v22.23.3-win-x64` [VERIFIED: fs esta sesión] | Node del sistema es 22.18.0 (< 22.22) — usar el portátil en UAT |
| Python 3.12 | UAT delegado (backend) | ✓ | 3.12.10 | — |
| uv | UAT delegado (backend, `uv add`) | ✓ | 0.9.3 | — |
| npm | UAT delegado (`npm install zustand`) | ✓ | 11.16.0 | — |
| Workspace maura-uat | UAT delegado de la fase | ✓ | `backend/`, `frontend/`, `refix/` presentes con node_modules [VERIFIED: ls esta sesión] | — |
| Red (npm/PyPI) | installs de UAT + verificaciones de registro | ✓ (npm view + PyPI JSON operaron esta sesión) | — | — |

**Missing dependencies with no fallback:** ninguna.
**Missing dependencies with fallback:** Node del sistema (22.18.0) no cumple engines de react-router 8 — irrelevante para este repo (docs-only) y cubierto en UAT por el Node portátil v22.23.3 ya establecido en la sesión 01-UAT.

*(Validation Architecture: OMITIDA — `workflow.nyquist_validation: false` explícito en .planning/config.json [VERIFIED: config leída esta sesión].)*

## Security Domain

> `security_enforcement: true`, `security_asvs_level: 1`, `security_block_on: high` [VERIFIED: .planning/config.json workflow section, esta sesión]. **La fase 2 ES la fase de autenticación** — superficie de seguridad nueva y sustancial; todo lo que sigue debe reflejarse en el doc 02 (RN), ADRs y guías.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | **yes** | Email+password con Argon2 (pwdlib `PasswordHash.recommended()`); login 401 genérico (anti user-enumeration, D-26); NIST: mínimo 8 sin composición (D-25) |
| V3 Session Management | **yes** | JWT `exp` 7 días (D-20), verificación de expiración por PyJWT (`ExpiredSignatureError` → 401); logout = borrar localStorage (client-side); sin server-side session store (documento la limitación) |
| V4 Access Control | **yes** | `get_current_user` (401) + `get_current_admin` (403) como dependencias; claim `rol` desde el primer token (AUTH-03); contrato declara `security: [{bearerAuth: []}]` por operación |
| V5 Input Validation | **yes** | `RegistroCreate` Pydantic (EmailStr + minLength 8) → 422; login por form validado; parámetros de BD siempre parameterizados (SQLAlchemy) |
| V6 Cryptography | **yes** | Argon2 para passwords (memory-hard, salt automática); HS256 con `SECRET_KEY` de 64 hex chars en `.env` (nunca en código/contrato/guía); jamás hash casero |
| V14 Configuration | **yes** | `SECRET_KEY` + credenciales demo por env vars (D-23/D-24); CORS explícito (agregar POST); `.env` gitignoreado desde guia-01 |

### Known Threat Patterns for SPA + JWT localStorage + FastAPI

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| User enumeration en login | Information Disclosure | 401 genérico "Credenciales incorrectas" (D-26) + DUMMY_HASH/tiempo constante (patrón del tutorial) — el 409 del registro es deliberado y explicado |
| Robo de token por XSS | Information Disclosure/Spoofing | Aceptado y documentado como desventaja honesta del ADR (D-21): React escapa por defecto, prohibido `dangerouslySetInnerHTML`; mitigación real = httpOnly cookies (fuera de scope, dicha en el ADR) |
| Algorithm confusion / `alg:none` | Tampering | `jwt.decode(..., algorithms=["HS256"])` SIEMPRE con lista explícita [CITED: tutorial + pyjwt docs] |
| SECRET_KEY en código o commit | Information Disclosure | `.env` (gitignoreado) + `secrets.token_hex(32)` para generarlo; sin defaults mágicos en Settings |
| Password débiles/forced complexity | Spoofing | NIST: largo ≥ 8 sin composición (D-25); la guía explica por qué (longitud sobre complejidad) |
| Hash de password en el cliente o devuelto en API | Information Disclosure | Argon2 solo backend; `UsuarioPublico` sin `hashed_password` (Pydantic filtra por omisión) |
| Acceso a endpoints admin sin rol | Elevation of Privilege | `get_current_admin` → 403 en el SERVIDOR; el guard de ruta es solo UX (lección explícita) |
| Timing attack en login | Spoofing | Verificación de hash dummy cuando el usuario no existe (patrón DUMMY_HASH del tutorial) |
| Token robado → sesión eterna | Spoofing | Mitigado parcialmente por `exp` 7 días; refresh/revocación documentada como evolución del ADR (D-19 honesto) |

## Sources

### Primary (HIGH confidence)
- Código de repo leído íntegro esta sesión (in-repo values citados verbatim con línea): `docs/02_requerimientos.md`, `docs/03_diseno.md`, `docs/04_arquitectura/README.md` + `contrato_api.yaml` + `adr/007`, `docs/05_desarrollo/README.md` + `guia-03` + `guia-04` (+ greps de guia-01/02 y `01_necesidad`), `README.md` raíz, `docs/README.md`, `02-CONTEXT.md`, `REQUIREMENTS.md`, `STATE.md`, `ROADMAP.md` §Phase 2, `01-CONTEXT.md`, `01-UI-SPEC.md`, `01-RESEARCH.md`, `.planning/config.json`.
- Registro npm/PyPI esta sesión: `npm view zustand version` → 5.0.15; `npm view react-router version` → 8.4.0; PyPI JSON API pyjwt → 2.15.1 (>=3.9), pwdlib → 0.3.1 (>=3.10), python-multipart → 0.0.32.
- Tarball `react-router@8.4.0` (npm pack + inspección de `dist/development/index.d.ts`): export statement incluye `Navigate`, `Outlet`, `useLocation`, `useNavigate`, `BrowserRouter` desde el paquete principal.
- Seam `package-legitimacy check`: zustand OK (63.7M downloads/sem, repo pmndrs); pyjwt/pwdlib SUS por artefactos de métrica PyPI (ver Audit).

### Secondary (MEDIUM confidence)
- fastapi.tiangolo.com/tutorial/security/oauth2-jwt/ (fetch esta sesión): imports pwdlib+PyJWT verbatim, `OAuth2PasswordRequestForm`, `OAuth2PasswordBearer(tokenUrl=...)`, `create_access_token` con `datetime.now(timezone.utc)`, `jwt.decode(..., algorithms=[ALGORITHM])` + `InvalidTokenError` → 401 `WWW-Authenticate: Bearer`, DUMMY_HASH, ACCESS_TOKEN_EXPIRE_MINUTES=30.
- fastapi.tiangolo.com/tutorial/request-forms/ (fetch): "To use forms, first install python-multipart" + OAuth2 password flow usa form fields.
- pyjwt.readthedocs.io/en/latest/usage.html (fetch): claims sub/exp/iat, exp timezone-aware, algorithms obligatorio en decode, `jwt.ExpiredSignatureError`, `options={"require": [...]}`, leeway.
- frankie567.github.io/pwdlib + reference/pwdlib (fetch): `PasswordHash.recommended()` = "Currently, the hasher is Argon2 with default parameters"; `hash(password)`, `verify(password, hash)`, `verify_and_update → (bool, str|None)`; `pip install 'pwdlib[argon2]'`.
- pmndrs/zustand README + docs/reference/integrations/persisting-store-data.md (fetch): persist con localStorage default, `createJSONStorage`, `partialize`, version/migrate, `persist.clearStorage()`, `rehydrate()`.
- swagger.io/docs/specification/authentication/bearer-authentication/ (fetch): YAML de `securitySchemes.bearerAuth` + `security` por operación.
- Patrón RequireAuth (`Navigate state={{from: location}} replace` + `location.state?.from`): ejemplo oficial library-mode de React Router (histórico v6, removido del main actual — el repo main solo conserva `examples/README.md`); APIs core verificadas en tarball v8.4.0. Múltiples fuentes comunitarias concuerdan (Robin Wieruch RR7 auth).

### Tertiary (LOW confidence)
- NIST SP 800-63B (vía WebSearch): mínimo 8 sin composición (revisión original); Rev 4 sube a 15 si password es único factor — citar en la guía como nota, no como requisito (D-25 locked en 8). No se abrió pages.nist.gov directamente.
- Cifras de edad de paquetes en el Audit (pyjwt ~11 años, python-multipart ~6 años): conocimiento de ecosistema [ASSUMED].

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — versiones re-verificadas contra npm/PyPI esta sesión (2026-09-29); patrones de las 4 librerías nuevos de la fase verificados contra docs oficiales fetch-eadas esta sesión.
- Architecture: HIGH — capas/estructura locked por fase 1 (docs leídos verbatim); puntos de integración (CORS GET-only, Settings, lib/api.ts, Navbar) verificados con Read/grep en las guías existentes.
- Pitfalls: HIGH — 12 pitfalls; los críticos (CORS GET-only, orden de verify, enums, responses no documentados) provienen de fuentes primarias (tutorial/docs/repo); los de implementación frontend son MEDIUM (patrones estándar verificados contra docs oficiales de las librerías).
- Docs del ciclo: HIGH — numeración, formato ADR, estructura de guía y Gran verificación final leídos verbatim de los archivos que la fase extiende.

**Research date:** 2026-09-29
**Valid until:** 2026-10-29 (stack estable; re-verificar si PyJWT/zustand mueven major o si el tutorial FastAPI cambia de librería de hash)
