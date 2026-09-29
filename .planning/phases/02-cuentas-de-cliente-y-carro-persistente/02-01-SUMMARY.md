---
phase: 02-cuentas-de-cliente-y-carro-persistente
plan: 01
subsystem: api
tags: [openapi, jwt, bearer-auth, adr, api-first, contrato]

# Dependency graph
requires:
  - phase: 01-fundaciones-de-dos-tiers-y-cat-logo
    provides: contrato_api.yaml 0.1.0 con paths de catálogo, ADR-007 (API-first) como formato canónico de ADR y README de 04_arquitectura
provides:
  - contrato_api.yaml 0.2.0 con toda la superficie de autenticación (bearerAuth, UsuarioPublico/Token/RegistroCreate, /api/auth/registro|login|perfil, /api/admin/estado)
  - ADR-009 (JWT 7 días + localStorage con desventaja XSS dicha), ADR-010 (carro client-side {producto_id, cantidad}), ADR-011 (roles desde el primer token + seed por env)
  - Índice de ADRs al día (011), stack con pyjwt/pwdlib/python-multipart/zustand y árbol del alumno extendido
affects: [02-02 (docs 02/03 citan contrato y ADRs), 02-03 y 02-04 (guías 05-08 implementan el contrato), fase 3 (checkout/Webpay hereda interceptor y sesión), fase 4 (panel admin hereda ADR-011)]

# Actuals (#2632) — mismo scale que el estimate (chars/4 sobre el diff realizado)
actuals:
  tokens: 7842      # 31367 chars / 4 sobre el diff 151e8b2..HEAD
  tasks: 3
  commits: 3        # medido: git rev-list --count 151e8b2..HEAD
plan_head_before: 151e8b28e6a8d55108c3bd23bad3127b1d38da38
plan_head_after: 9d5e55b739c5f44f8e857501d8c221c33ea016bb

# Tech tracking
tech-stack:
  added: []          # nada se instala (D-17 guide-only); pyjwt/pwdlib/python-multipart/zustand quedan DOCUMENTADOS como stack que las guías enseñarán
  patterns:
    - "Extensión in-place del contrato API-first: versionar (0.1.0→0.2.0), tabla de errores como fuente del drift y copies locked como examples de detail"
    - "ADR de 3 opciones con negativas honestas obligatorias cuando la decisión tiene costo de seguridad conocido (D-21)"

key-files:
  created:
    - docs/04_arquitectura/adr/009-jwt-larga-vida-localstorage.md
    - docs/04_arquitectura/adr/010-carro-client-side.md
    - docs/04_arquitectura/adr/011-roles-desde-el-primer-token.md
  modified:
    - docs/04_arquitectura/contrato_api.yaml
    - docs/04_arquitectura/README.md

key-decisions:
  - "Login como form-urlencoded OAuth2 (username transporta el email) en el contrato: habilita el botón Authorize de /docs con las cuentas del seed y calza con el tutorial oficial de FastAPI"
  - "Copies locked D-26 viajan en el contrato como examples de detail del 409/401 — la asimetría anti-enumeración queda lockeada antes de las guías"
  - "El árbol del alumno en §4 se extendió con rutas completas (models/usuario.py, features/cuentas/...) conservando las líneas de fase 1 byte-intactas"
  - "Sin endpoint de renovación en el contrato (D-19) y bearerAuth declarado type http + scheme bearer (no apiKey), forma correcta OpenAPI 3.0"

patterns-established:
  - "Fase 2 replica el patrón API-first: contrato versionado aprobado en el primer plan de la fase, antes de cualquier guía"
  - "ADRs 009-011 con formato ADR-007: tabla de 3 opciones, decisión con reglas numeradas, negativas honestas y 3 preguntas para la clase"

requirements-completed: [AUTH-01, AUTH-02, AUTH-03]

# Coverage (#1602) — un entry por entregable
coverage:
  - id: D1
    description: "Contrato 0.2.0 con la superficie completa de autenticación: bearerAuth http/bearer/JWT, 4 paths con todas las responses declaradas, UsuarioPublico sin hash, RegistroCreate minLength 8, tabla de errores al día y copies locked del 409/401"
    requirement: AUTH-01
    verification:
      - kind: other
        ref: "command: plan Task 1 <automated> grep-chain (18 checks) + YAML parse — contrato02-ok / yaml-ok / TRACER-VERIFY-PASS"
        status: pass
    human_judgment: false
  - id: D2
    description: "ADRs 009-011 (JWT localStorage con XSS dicha, carro client-side {producto_id, cantidad}, roles desde el primer token con ADMIN_EMAIL) en formato ADR-007 con 3 opciones y negativas honestas"
    requirement: AUTH-02
    verification:
      - kind: other
        ref: "command: plan Task 2 <automated> grep-chain (11 ADRs exactos, XSS en 009, ADMIN_EMAIL/403 en 011) — adrs-ok"
        status: pass
    human_judgment: false
  - id: D3
    description: "README de 04_arquitectura: índice de ADRs 009-011, 4 piezas nuevas de stack citando sus ADRs y árbol del alumno extendido con reglas de dependencia y disclaimer byte-intactos"
    requirement: AUTH-03
    verification:
      - kind: other
        ref: "command: plan Task 3 <automated> grep-chain (ADR-009/010/011, pyjwt, zustand, security.py, RequireAuth, features/cuentas, lib/api.ts, guide-only) — readme-arq-ok + diff sin líneas eliminadas"
        status: pass
    human_judgment: false

# Metrics
duration: 15 min
completed: 2026-09-29
status: complete
---

# Phase 2 Plan 1: Contrato 0.2.0 + ADRs 009-011 (tracer API-first) Summary

**contrato_api.yaml 0.2.0 con la superficie de autenticación completa (bearerAuth JWT, registro/login/perfil/admin-estado con copies locked D-26), ratificada por ADRs 009-011 con negativas honestas e indexada en el README de arquitectura**

## Performance

- **Duration:** 15 min
- **Started:** 2026-09-29T16:36:37Z
- **Completed:** 2026-09-29T16:51:10Z
- **Tasks:** 3 (1 tracer + 2 auto)
- **Files modified:** 5 (2 extendidos, 3 nuevos)

## Accomplishments
- Contrato 0.2.0 declara la superficie de autenticación API-first ANTES de cualquier guía de la fase (D-15 honrado de forma verificable): registro 201/409/422, login form-urlencoded 200/401, perfil 200/401 y admin/estado 200/401/403 (D-33)
- ADRs 009-011 registran D-19..D-33 como decisiones de arquitectura con desventajas honestas — el XSS del localStorage queda dicho por mandato de D-21 (T-02-04 mitigado)
- README de arquitectura llega a 11 ADRs indexados, documenta pyjwt/pwdlib/python-multipart/zustand y extiende el árbol del alumno sin tocar las 6 reglas de dependencia ni el disclaimer guide-only
- Tracer feedback gate: verify re-ejecutado end-to-end en auto-mode — PASS ("Tracer verified end-to-end — expanding") antes de las tareas de expansión

## Task Commits

Each task was committed atomically:

1. **Task 1: contrato_api.yaml 0.2.0 — superficie de autenticación (tracer)** - `9bd6e3f` (feat)
2. **Task 2: ADRs 009-011 — JWT localStorage, carro client-side, roles** - `5850700` (docs)
3. **Task 3: README de 04_arquitectura — stack, árbol e índice** - `9d5e55b` (docs)

**Plan metadata:** (ver commit docs final)

## Files Created/Modified
- `docs/04_arquitectura/contrato_api.yaml` - Contrato 0.2.0: securitySchemes.bearerAuth, schemas UsuarioPublico/Token/RegistroCreate, 4 paths nuevos, tabla de errores con 401/403/409 en uso y fila 201; fase 1 byte-intacta (6 líneas eliminadas, todas previstas por el plan)
- `docs/04_arquitectura/adr/009-jwt-larga-vida-localstorage.md` - ADR token único 7 días + localStorage (D-19..D-22) con robo por XSS en Negativas
- `docs/04_arquitectura/adr/010-carro-client-side.md` - ADR carro client-side {producto_id, cantidad} hidratado (D-27..D-30)
- `docs/04_arquitectura/adr/011-roles-desde-el-primer-token.md` - ADR claim de rol + seed ADMIN_EMAIL/CLIENTE_EMAIL (D-23/D-24/D-33)
- `docs/04_arquitectura/README.md` - §3 +4 filas de stack, §4 árbol extendido (solo inserciones), §5 +3 ADRs

## Decisions Made
- Login documentado como `application/x-www-form-urlencoded` OAuth2 (username = email de la clienta): maximiza tutorial oficial + botón Authorize de /docs para la comparación de cierre (ADR-007)
- Copys locked D-26 ("Ese email ya tiene cuenta, inicia sesión" / "Credenciales incorrectas") grabados como `example.detail` de las responses 409/401 del contrato — las guías los heredan literales
- 403 de /api/admin/estado con detail "Requiere rol admin" (espejo del patrón get_current_admin del research)
- Árbol del alumno extendido con entradas de ruta completa (models/usuario.py, features/cuentas/, …) — mismo estilo que public/products/ de fase 1; cero líneas existentes modificadas

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- Entorno de verificación (sin impacto en artefactos): los greps del plan con patrones que empiezan con `/` fallan en este host por doble artefacto — MSYS convierte argumentos con slash inicial a rutas Windows y el grep del sistema (ugrep) parsea dichos patrones como opciones. Solución de ejecución: `export MSYS_NO_PATHCONV=1` + patrón anclado con `-e`. El mismo check ejecutado así pasa limpio (contrato02-ok). Las corridas de verify-work en Windows necesitarán el mismo tratamiento.
- requirements.ready-ids bloqueó AUTH-01..03 (shared-ID gate #2388): los planes hermanos 02-02+ declaran los mismos IDs y aún no tienen SUMMARY — se marcan completos cuando el último plan declarante cierre. Comportamiento esperado, no un problema.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Contrato 0.2.0 aprobado y ADRs 009-011 aceptados: los planes 02-02 (docs 02/03), 02-03/02-04 (guías 05-08) pueden citarlos e implementarlos sin desviarse (D-15)
- La tabla de errores del contrato vuelve a ser detectable en la fila contrato ↔ /docs de la Gran verificación final de guia-08 (401/403/409/201 ahora En uso)
- Los ADRs citan las reglas que las guías enseñarán (interceptor 401 = regla 5 de dependencia; seed por email = patrón upsert de guia-03)

## Self-Check: PASSED
