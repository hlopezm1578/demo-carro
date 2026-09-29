---
phase: 02-cuentas-de-cliente-y-carro-persistente
plan: 03
subsystem: docs
tags: [guia-paso-a-paso, jwt, argon2, pwdlib, pyjwt, oauth2-form, zustand, persist, interceptor-401, requireauth, returnto, seed-upsert, cors, auth-backend, sesion-frontend]

# Dependency graph
requires:
  - phase: 02-cuentas-de-cliente-y-carro-persistente (plan 01)
    provides: contrato_api.yaml 0.2.0 con /api/auth/*, /api/admin/estado, UsuarioPublico/Token/RegistroCreate y copies locked D-26 como examples; ADR-009/011 como decisiones que las guías citan
  - phase: 02-cuentas-de-cliente-y-carro-persistente (plan 02)
    provides: RF-06..RF-11, RN-05..RN-09, HU-05..HU-08 citables y pantallas 4-7 del UI-SPEC que las guías implementan
provides:
  - docs/05_desarrollo/guia-05-cuentas-backend.md — el backend de cuentas completo por capas (security Argon2+JWT, schemas/repository/service/routers, seed por email, CORS GET+POST) implementando el contrato 0.2.0 (AUTH-01/02/03)
  - docs/05_desarrollo/guia-06-sesion-frontend.md — la sesión en la SPA (useAuthStore persist maura-auth, interceptor 401 con exclusión del login, RequireAuth con returnTo, login/registro con copies locked, navbar con sesión)
  - Convenciones heredables: interceptor 401 en lib/api.ts (fases 3-4 lo heredan gratis, D-22), patrón RequireAuth+returnTo (fase 4 lo reutiliza, D-32), .env.example con placeholders como forma canónica de secretos
affects: [02-04 (guia-07 carro reusa el patrón store persist y lib/api.ts extendido), 02-05 (READMEs citan guías 5-6), fase 3 (checkout hereda interceptor/sesión/returnTo), fase 4 (panel admin hereda ADR-011 y RequireAuth)]

# Actuals (#2632) — mismo scale que el estimate (chars/4 sobre el diff realizado)
actuals:
  tokens: 22437     # 89751 chars / 4 sobre el diff 47094bb..e4ed5e9 (las 2 guías)
  tasks: 2
  commits: 2        # medido: git rev-list --count 47094bb..e4ed5e9 (antes del commit de metadata)
plan_head_before: 47094bb2dea7b1cda0ebf53b590cd95e315cad49
plan_head_after: e4ed5e9b27102b46dbba2273713133cbeaf56d54

# Tech tracking
tech-stack:
  added: []          # D-17 guide-only: nada se instala en ESTE repo; pyjwt/pwdlib[argon2]/python-multipart/zustand quedan enseñados como comandos del alumno dentro de las guías
  patterns:
    - "security.py como módulo transversal (hash+JWT+dependencias) fuera de las 4 capas, junto a database.py — routers siguen sin importar SQLAlchemy"
    - "Interceptor 401 con regla con-Bearer-adjunto (el login queda eximido por construcción: la pantalla /login redirige si hay sesión, así su 401 nunca lleva token)"
    - "Login en dos tiempos: token al store primero (el Bearer ya viaja), usuario desde /api/auth/perfil después (quién eres lo dice el servidor)"

key-files:
  created:
    - docs/05_desarrollo/guia-05-cuentas-backend.md
    - docs/05_desarrollo/guia-06-sesion-frontend.md
  modified: []

key-decisions:
  - "Orden de pasos de guia-05 reordenado por dependencia de imports (models→schemas→repository→security→services→routers, el mismo orden de guia-04): security.py importa UsuarioRepository, así que con el orden literal del plan el primer mini-verificación reventaría con ImportError"
  - "Settings gana SettingsConfigDict(env_file=\".env\"): sin env_file pydantic-settings jamás lee el archivo — una línea que hace real al .env que guia-01 dejó gitignoreado y habilita el fail-fast de secret_key"
  - "El login de guia-06 consulta /api/auth/perfil en dos tiempos (token primero, usuario después) y comprueba la sesión guardada al entrar al login: vuelve observable al interceptor D-22 con un token corrupto SIN esperar al checkout de guia-08"
  - "Espejo de validación honesto: el login valida solo formato de email (el backend no valida forma de contraseña ahí — clave corta = 401 genérico); el registro valida las dos reglas del 422 (RN-05)"
  - "routers/admin.py reusa CatalogService/ProductoRepository para los conteos de /api/admin/estado: cero SQL nuevo en el router (regla de dependencia 1)"
  - "UsuarioRepository gana por_id además de por_email/crear: lo necesitan las dependencias de seguridad (lookup por sub del token, Pattern 1 del research)"

patterns-established:
  - "Guía de backend con seguridad: el módulo transversal security.py + responses 401/403/409 declaradas en la firma (lección G-01-4 extendida a tres códigos)"
  - "Guía de frontend con estado de cliente: store persist con partialize + consumo por lib/api.ts vía getState() — el patrón que guia-07 replica para el carro"

requirements-completed: [AUTH-01, AUTH-02, AUTH-03]

# Coverage (#1602) — un entry por entregable
coverage:
  - id: D1
    description: "guia-05-cuentas-backend: backend de cuentas completo por capas implementando el contrato 0.2.0 — uv add de los 3 paquetes auditados, Settings fail-fast + env_file + .env.example con placeholders, RolUsuario nombre==valor, security.py (Argon2 password-primero, create_access_token sub/rol incondicional/exp 7 días/iat HS256, get_current_user 401 genérico con WWW-Authenticate, get_current_admin 403), schemas sin hashed_password, servicio con hash dummy anti-enumeración, routers con responses 401/403/409, CORS GET+POST y seed upsert por email con restauración de credenciales"
    requirement: AUTH-01
    verification:
      - kind: other
        ref: "command: plan Task 1 <automated> grep-chain (23 checks: OAuth2PasswordRequestForm, HS256, GET+POST, copies locked, ADR-009/011, token_hex, ADMIN_EMAIL, gates negativos de secreto/librerías vetadas) — g5-ok"
        status: pass
      - kind: other
        ref: "command: acceptance criteria 5/5 verificados por grep (orden password-primero, rol SIN condición, sub string, timezone-aware, iat; login form OAuth2 username=email; response_model=UsuarioPublico x2 + responses x4; 4 variables env + restauración + usuarios después; 10 🧠 / 13 mini-verificaciones)"
        status: pass
    human_judgment: false
  - id: D2
    description: "guia-06-sesion-frontend: sesión SPA completa — useAuthStore persist (maura-auth, createJSONStorage, partialize solo token+usuario), lib/api.ts extendido (pedir() con Bearer vía getState, apiPostForm sin Content-Type manual, apiPost JSON, interceptor 401 solo-con-Bearer → /login?expirada=1), RequireAuth con Navigate state from location + returnTo location.state?.from ?? \"/\", login/registro según UI-SPEC (labels persistentes, banners copies locked, espejo al submit, gerundios, cross-links), navbar con email truncado + Cerrar sesión"
    requirement: AUTH-02
    verification:
      - kind: other
        ref: "command: plan Task 2 <automated> grep-chain (21 checks: partialize, maura-auth, RequireAuth/Navigate/location.state, copies locked D-22/D-26, Mínimo 8 caracteres, Cuenta creada, truncate, zustand, D-22) — g6-ok"
        status: pass
      - kind: other
        ref: "command: acceptance criteria 5/5 verificados por grep (store literal partialize + createJSONStorage; interceptor con-Bearer + Pitfall 5 x7; state from location + from ?? / + guard-UX x4; htmlFor x4, gerundios, cross-links; F5 + navbar email)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Comportamiento runtime de AUTH-01/02/03 según lo que las guías enseñan (201/409/422 del registro, login form-encoded de ambos roles, decodificación offline del token con exp-iat=604800, 200 vs 403 en /api/admin/estado, sesión que sobrevive F5, interceptor con token corrupto)"
    requirement: AUTH-03
    verification: []
    human_judgment: true
    rationale: "Repo guide-only (D-17): nada se ejecuta aquí — la verificación de este plan es documental (greps sobre las guías, D1/D2). El runtime queda delegado al UAT del agente en D:/Repos/maura-uat (instrucción persistida en AGENTS.md), igual que la sesión 01-UAT de la fase 1."

# Metrics
duration: 16 min
completed: 2026-09-29
status: complete
---

# Phase 2 Plan 3: Guías 05-06 — backend de cuentas y sesión frontend Summary

**guia-05 (security Argon2+JWT HS256 con claim de rol incondicional, capas espejo del contrato 0.2.0, seed por email con restauración y CORS GET+POST) y guia-06 (store persist maura-auth, interceptor 401 solo-con-Bearer, RequireAuth con returnTo genérico y login/registro con copies locked) — con 10 y 9 bloques 🧠 y 13 y 12 mini-verificaciones accionables**

## Performance

- **Duration:** 16 min
- **Started:** 2026-09-29T17:10:32Z
- **Completed:** 2026-09-29T17:26:03Z
- **Tasks:** 2 (2 auto)
- **Files modified:** 2 (2 nuevas guías)

## Accomplishments
- guia-05 implementa el contrato 0.2.0 sin desviarse (D-15): registro 201/409/422 con copies locked, login form OAuth2 (username transporta el email, habilita Authorize en /docs), perfil 200/401 y /api/admin/estado 200/401/403 (D-33) — con el claim de rol construido SIN condición (AUTH-03, ADR-011) y la mini-verificación 200-admin vs 403-clienta
- La seguridad de la etapa queda enseñada como código leíble: Argon2 con el orden password-primero, 401 genérico + hash dummy anti-enumeración (RN-06/D-26), UsuarioPublico sin hash en ningún endpoint (RN-07), responses 401/403/409 declaradas (G-01-4) y la tabla única 422/401/403/409 en "el error que este archivo evita"
- guia-06 instala el patrón de sesión que las fases 3-4 heredan: store persist con partialize (Pitfall 7), interceptor 401 en lib/api.ts que NO dispara en el propio login (Pitfall 5, D-22), RequireAuth con returnTo genérico (D-32) y la lección explícita guard=UX/seguridad=backend
- AUTH-02 observable de punta a punta: login con la clienta seed, navbar con email, F5 que conserva la sesión al primer render — y el interceptor provocable hoy corrompiendo el token a mano (sin esperar al checkout de guia-08)

## Task Commits

Each task was committed atomically:

1. **Task 1: guia-05-cuentas-backend.md — security, capas y seed de cuentas** - `d2d17b6` (docs)
2. **Task 2: guia-06-sesion-frontend.md — store persist, interceptor 401, RequireAuth, login/registro y navbar** - `e4ed5e9` (docs)

**Plan metadata:** (ver commit docs final)

## Files Created/Modified
- `docs/05_desarrollo/guia-05-cuentas-backend.md` - Guía del backend de cuentas (1088 líneas): 11 pasos con estructura canónica — instalación auditada, .env/Settings fail-fast, modelo+enum (segunda vuelta del gotcha), schemas espejo, repository, security.py, service con hash dummy, routers con responses declaradas, CORS GET+POST, seed upsert por email y prueba de fuego (login, decode offline, 200 vs 403)
- `docs/05_desarrollo/guia-06-sesion-frontend.md` - Guía de sesión frontend (934 líneas): 10 pasos — zustand, useAuthStore persist, types espejo, lib/api.ts extendido con interceptor, RequireAuth, Login (avisos ámbar/esmeralda + returnTo), Registro (espejo RN-05 + 409), Navbar con sesión, rutas y prueba de fuego (F5, token corrupto)

## Decisions Made
- Orden de pasos de guia-05 reordenado por dependencia de imports (models→schemas→repository→security→services→routers): security.py importa UsuarioRepository, así que con el orden literal del plan (security antes que el repositorio) el mini-verificación del paso intermedio reventaría con ImportError — el orden quedó igual al de guia-04 y el contenido del plan intacto
- `SettingsConfigDict(env_file=".env")`: sin env_file, pydantic-settings solo lee variables del shell y nunca el archivo — el .env que guia-01 dejó gitignoreado por fin existe para la app (y el fail-fast de `secret_key` sin default funciona como el plan lo exige)
- El login de guia-06 hace dos llamadas (login → token al store → perfil → usuario): quién eres lo dice el servidor, no el formulario; y la entrada al login CON sesión comprueba el token contra perfil — es lo que vuelve observable al interceptor D-22 hoy (la mini-verificación del plan lo exige)
- Espejo de validación honesto por formulario: login solo email (el backend no valida forma de contraseña ahí), registro las dos reglas del 422 — coherente con el "error evitado" nº 3 de guia-05 (422 de clave corta en el login)
- /api/admin/estado reusa CatalogService/ProductoRepository para los conteos: cero SQL en el router, regla de dependencia 1 intacta

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Orden de pasos de guia-05 reordenado por dependencia de imports**
- **Found during:** Task 1 (redacción de guia-05)
- **Issue:** El plan ordena los pasos (3) models → (4) security.py → (5) schemas → (6) repositories+services → (7) routers; pero security.py importa UsuarioRepository (para el lookup por sub del token, Pattern 1 del research) — copiado en el orden literal, el archivo no importa y el mini-verificación del propio paso 4 (`from app.security import ...`) revienta con ImportError
- **Fix:** Reordené a models → schemas → repository → security → services → routers → CORS → seed → prueba de fuego (11 pasos): cada archivo importa solo lo ya existente, igual que guia-04 (schemas → repo → service → router). Todo el contenido de los ítems (1)-(10) del plan está, incluidos los 🧠 y mini-verificaciones por paso; UsuarioRepository gana por_id además de por_email/crear (lo exige get_current_user)
- **Files modified:** docs/05_desarrollo/guia-05-cuentas-backend.md
- **Verification:** greps del Task 1 (g5-ok) + 5/5 acceptance criteria; la narración sigue el flujo dependiente de guia-04
- **Committed in:** d2d17b6 (Task 1 commit)

**2. [Rule 2 - Missing critical] Settings necesita env_file=".env" para que el .env exista**
- **Found during:** Task 1 (paso 2 de guia-05)
- **Issue:** El plan manda "genera el secreto, ponlo en el .env, Settings gana secret_key sin default (fail-fast)" — pero el Settings de guia-01 no configura env_file: pydantic-settings por defecto NO lee archivos .env, solo variables de entorno del shell. Sin esa línea, la narrativa completa del paso 2 (y el fail-fast, y las 4 credenciales del seed leídas del .env) no funciona en la máquina del alumno
- **Fix:** Una línea en el Settings extendido: `model_config = SettingsConfigDict(env_file=".env")`, narrada como "el .env entra en acción" (guia-01 lo dejó gitignoreado esperando este momento)
- **Files modified:** docs/05_desarrollo/guia-05-cuentas-backend.md
- **Verification:** el mini-verificación del paso 2 imprime `7` + ADMIN_EMAIL leídos del .env; el fail-fast comentando SECRET_KEY está narrado y verificado
- **Committed in:** d2d17b6 (Task 1 commit)

**3. [Rule 2 - Missing critical] El interceptor 401 necesita una llamada autenticada observable en guia-06**
- **Found during:** Task 2 (paso de mini-verificaciones)
- **Issue:** La mini-verificación del plan ("borrar la firma del token y navegar → la app expulsa a login con aviso ámbar") exige una llamada autenticada disparada por navegación; pero en el alcance de guia-06 ninguna pantalla hace llamadas autenticadas al navegar (el catálogo es público y el perfil solo se llama dentro del login) — el interceptor sería inverificable hasta guia-08
- **Fix:** Login comprueba la sesión guardada al entrar con token (useQuery perfil → vivo: Navigate "/", muerto: el interceptor expulsa), y el flujo de login consulta perfil tras recibir el token (quién eres lo dice el servidor). La mini-verificación corrompe el token, entra a /login y observa la expulsión ámbar — el mismo mecanismo que la etapa 3 hereda
- **Files modified:** docs/05_desarrollo/guia-06-sesion-frontend.md
- **Verification:** greps del Task 2 (g6-ok) + mini-verificación del paso 10 con pasos concretos; coherente con UI-SPEC (el redirect a "/" se mantiene) y con T-02-11 del threat model ("la mini-verificación lo provoca con un token corrupto a mano")
- **Committed in:** e4ed5e9 (Task 2 commit)

---

**Total deviations:** 3 auto-fixed (1 blocking, 2 missing critical)
**Impact on plan:** Las tres cierran huecos de ejecutabilidad del material (import order, env loading, interceptor observable) sin tocar alcance: no se agregaron endpoints, pantallas ni copys fuera del contrato 0.2.0 y el UI-SPEC.

## Issues Encountered
- Ninguna bloqueante. Nota de entorno heredada de 02-01: los greps del verify se corrieron con `export MSYS_NO_PATHCONV=1` y patrones sin slash inicial (artefacto MSYS/ugrep de este host); ambas cadenas pasaron limpio a la primera (g5-ok, g6-ok).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Las guías 05-06 existen con la estructura canónica y encadenadas (guia-05 → guia-06 → guia-07): 02-04 (guia-07 carro + guia-08 checkout/Gran verificación final) puede citar el useAuthStore, el lib/api.ts extendido y el RequireAuth ya enseñados
- El interceptor 401 y el patrón store-persist quedaron establecidos para que guia-07 replique el patrón con useCarroStore (D-27) y guia-08 use RequireAuth para /checkout (AUTH-04)
- Sin bloqueos para 02-04; el gate ready-ids de AUTH-01..03 se desbloquea con este SUMMARY (02-04 declara CART-01/02/AUTH-04 y 02-05 GUIDE-02 — sin solape)

## Self-Check: PASSED

- Archivos en disco: docs/05_desarrollo/guia-05-cuentas-backend.md, docs/05_desarrollo/guia-06-sesion-frontend.md — FOUND
- Commits: d2d17b6 (Task 1), e4ed5e9 (Task 2) — FOUND
- Verify del plan re-ejecutado: g5-ok + g6-ok; key_links verificadas (/api/auth/registro en guia-05, lib/api.ts en guia-06); commits medidos desde ledger = 2
