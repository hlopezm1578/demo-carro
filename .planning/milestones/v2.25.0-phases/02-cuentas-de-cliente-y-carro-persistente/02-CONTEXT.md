# Phase 2: Cuentas de cliente y carro persistente - Context

**Gathered:** 2026-09-29
**Status:** Ready for planning

<domain>
## Phase Boundary

**El repositorio sigue guide-only (D-17, fase 1): esta fase entrega DOCUMENTOS, no código.** La fase 2 documenta la etapa 2 del proyecto Maura — cuentas de cliente y carro persistente — y el código vive como bloques dentro de las guías nuevas que el alumno copia. Como documentos, la fase:

- Extiende `docs/02_requerimientos.md` con los requerimientos de la etapa 2 (cuentas: registro, login, sesión persistente, rol admin; carro: agregar/editar/vaciar, persistencia localStorage) — nuevos actores (clienta con cuenta, admin), RF/HU/RN que continúan la numeración existente, y la trazabilidad P5 del doc 01.
- Extiende `docs/03_diseno.md` con el modelo de datos de usuarios y las pantallas nuevas (login, registro, carro, checkout).
- Extiende `docs/04_arquitectura/` con ADRs nuevos (JWT y su almacenamiento, carro client-side, roles) continuando desde ADR-009, y **extiende `contrato_api.yaml` ANTES de escribir las guías (D-15, API-first)** con los endpoints de autenticación, perfil y el endpoint admin protegido — el contrato ya reserva 401/403/409 "para fases 2+".
- Extiende `docs/05_desarrollo/` con las guías 5+ (autenticación backend, autenticación frontend con rutas protegidas, carro, checkout guard) bajo la estructura canónica 🧠/✅/📝 y la convención "Gran verificación final" de guia-04 que las fases 2-5 replican.
- Actualiza los READMEs de estado (`docs/README.md`, `README.md` raíz, `docs/05_desarrollo/README.md`).

La verificación de planes es documental (greps/estructura); el UAT runtime es delegado al agente en `D:/Repos/maura-uat` (instrucción persistida en AGENTS.md).

Requisitos cubiertos: AUTH-01, AUTH-02, AUTH-03, AUTH-04, CART-01, CART-02 (CART-03 queda en fase 3 como segunda barrera del stock).

</domain>

<decisions>
## Implementation Decisions

*La numeración D continúa desde la fase 1 (D-01..D-18 en `01-CONTEXT.md`).*

### Sesión JWT
- **D-19:** **Token único de larga vida — sin refresh tokens.** Un solo access token emitido al login; no existe endpoint `/refresh`. La complejidad de renovación queda fuera de la guía (comentario para el alumno curioso, no código) — **Reversibility:** reversible — agregar refresh después solo suma un endpoint y no rompe contrato publicado previo.
- **D-20:** **Duración del token: 7 días** (claim `exp`) — sesión cómoda para una tienda; el claim se lee claro en jwt.io durante la mini-verificación de la guía.
- **D-21:** **La SPA guarda el token en localStorage** vía el store de auth de Zustand con middleware `persist`: sobrevive recargas, cierre de pestaña y los full-page loads de Webpay (fase 3). El ADR de JWT deja dicha la desventaja honesta (XSS) como el costo enseñado del patrón — **Reversibility:** costly — cambiar el almacenamiento después reescribe `lib/api.ts`, el store de auth y las guías de las fases 2-4.
- **D-22:** **Interceptor 401 → login.** `lib/api.ts` detecta 401 en cualquier llamada autenticada: limpia la sesión, redirige a `/login` y muestra "Tu sesión expiró, ingresa de nuevo". Se enseña una sola vez y las fases 3-4 lo heredan gratis.

### Cuenta admin
- **D-23:** **El admin nace del seed con variables de entorno.** La siembra idempotente (mismo patrón upsert de los 12 SKU, ahora por email) crea/actualiza el usuario admin leyendo `ADMIN_EMAIL` y `ADMIN_PASSWORD` del `.env` — cada alumno reinicia su admin sin miedo y la guía enseña secretos por variable de entorno, jamás en código. Nada de credenciales fijas escritas en la guía ni de "primer registrado = admin".
- **D-24:** **El seed crea también una clienta demo** (`CLIENTE_EMAIL`/`CLIENTE_PASSWORD`, rol cliente): la guía verifica el login de ambos roles sin pasos manuales previos y el UAT delegado tiene cuentas predecibles en maura-uat.
- **D-25:** **Regla de contraseña: largo mínimo 8, sin complejidad obligatoria** (recomendación NIST moderna, igual que el tutorial oficial de FastAPI). La guía explica por qué NO forzar complejidad es la práctica actual.
- **D-26:** **409 claro en registro / 401 genérico en login.** Registro con email existente → 409 "Ese email ya tiene cuenta, inicia sesión"; login fallido → 401 genérico "Credenciales incorrectas" sin revelar si el email existe. La asimetría es deliberada y la guía la explica (enumerar cuentas no ayuda a quien se registra, sí a quien intenta entrar).

### Carro: datos y UX
- **D-27:** **El carro guarda solo `[{producto_id, cantidad}]` en localStorage** — la vista del carro se hidrata consultando la API: el precio mostrado es siempre el vigente del catálogo y la lección queda lista para CART-03 (fase 3: el backend recalcula y jamás confía en el cliente). Sin snapshot de nombre/precio — **Reversibility:** costly — la estructura del store toca todas las operaciones del carro narradas en las guías.
- **D-28:** **UI del carro: página `/carro` + badge contador en el navbar.** La página concentra edición de cantidades, vaciar y el CTA "Finalizar compra". Sin drawer lateral.
- **D-29:** **El botón "Agregar al carro" vive solo en la ficha del producto** (donde ya hay stock visible); las tarjetas del catálogo solo navegan a la ficha, igual que en la fase 1.
- **D-30:** **Las cantidades se tapan al stock vigente** (ficha y carro, leído de la hidratación con la API): sin sobreventa en pantalla desde ya; la validación real del backend (CART-03) queda como segunda barrera en fase 3, no como único muro.

### Checkout protegido (fase 2)
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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Planificación del proyecto
- `.planning/PROJECT.md` — Contexto, constraints y decisiones clave (guide-only, Webpay sandbox, stack).
- `.planning/REQUIREMENTS.md` — Requisitos v1; la fase 2 cubre AUTH-01..04 y CART-01..02 (ver Traceability); CART-03/PAY quedan en fase 3.
- `.planning/ROADMAP.md` §Phase 2 — Goal, success criteria y límites de la fase.
- `.planning/phases/01-fundaciones-de-dos-tiers-y-cat-logo/01-CONTEXT.md` — Decisiones D-01..D-18 de la fase 1 que esta fase hereda (D-17 guide-only, D-15 API-first, D-16 sub-guías).

### Docs del ciclo que esta fase extiende
- `docs/02_requerimientos.md` — Numeración RF/RNF/RN/HU a continuar; tabla de trazabilidad P5 (carro y cuentas → etapa 2); actores.
- `docs/03_diseno.md` — Modelo de datos y pantallas a extender (tabla `users`, pantallas login/registro/carro/checkout).
- `docs/04_arquitectura/contrato_api.yaml` — Fuente de verdad API-first (D-15/ADR-007): se extiende ANTES de las guías; ya reserva 401/403/409 "para fases 2+".
- `docs/04_arquitectura/adr/` — ADRs 001-008 existentes; la fase continúa desde ADR-009 (formato demo-cine).
- `docs/05_desarrollo/README.md` — Índice de guías (la fase agrega guia-05+), reglas del alumno, mapa mental de la serie.
- `docs/README.md` y `README.md` (raíz) — Tablas de estado del ciclo que avanzan por fase (D-13/D-18).

### Investigación y UI heredadas
- `.planning/research/STACK.md` — Stack versionado: PyJWT 2.15.0, pwdlib[argon2] 0.3.1, Zustand 5, TanStack Query 5, python-multipart (form de login), "What NOT to use" (python-jose, passlib).
- `.planning/phases/01-fundaciones-de-dos-tiers-y-cat-logo/01-UI-SPEC.md` — Tokens de UI Maura (paleta fresco-luminosa, tipografía) que las pantallas nuevas respetan.
- `.planning/phases/01-fundaciones-de-dos-tiers-y-cat-logo/01-RESEARCH.md` — Patrones backend verificados en runtime (capas, sesión inyectada, seed) que las guías nuevas citan.
- `D:/Repos/demo-cine/docs/` — Referencia externa de formato (repo hermano): estructura y tono de guías y ADRs para replicar.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Ninguno de código — **el repo es guide-only (D-17)**. Los assets reutilizables son patrones documentados:
- Estructura canónica de guías (blockquote de intro / pasos con 🧠 "El desarrollador piensa" + código + ✅ mini-verificación / cierre) fijada en guia-01..04.
- Convención "Gran verificación final" de guia-04 (tabla numerada CS/RF + fila contrato ↔ `/docs`) que esta fase replica.
- `contrato_api.yaml` como fuente de verdad viva a extender (D-15).

### Established Patterns
- Backend en capas routers → services → repositories con sesión inyectada; routers sin SQLAlchemy; solo `main.py` arma la app (reglas de dependencia de 04_arquitectura).
- Seed converge por upsert a estado canónico (SKU para productos — ahora email para usuarios, D-23/D-24).
- Numeración trazable del ciclo: P1-P8 / C1-C4 / CS1-CS5 → RF/RNF/RN/HU → ADRs → guías; todas las series continúan en esta fase.
- Mini-verificaciones ✅ por paso; comandos agnósticos de terminal (D-12); todo HTTP del frontend por `lib/api.ts`.

### Integration Points
- `guia-03` (modelos y seed) se referencia/extiende al agregar la tabla `users` y las cuentas demo al seed.
- `lib/api.ts` gana el interceptor 401 (D-22) y helpers autenticados (Bearer).
- El navbar de `guia-02` gana badge de carro (D-28) y estado de sesión.
- El contrato gana el tag de autenticación, schemas de usuario/token y `/api/admin/estado` (D-33) — la fila "contrato ↔ /docs" de la verificación final se actualiza.

</code_context>

<specifics>
## Specific Ideas

- Mensajes literales acordados: "Tu sesión expiró, ingresa de nuevo" (interceptor 401, D-22); "Ese email ya tiene cuenta, inicia sesión" (409 registro) y "Credenciales incorrectas" (401 login genérico, D-26); "el pago llega en la etapa siguiente" (nota del CTA deshabilitado, D-31).
- Variables de entorno del seed: `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `CLIENTE_EMAIL`, `CLIENTE_PASSWORD` en el `.env` del backend — con `.env.example` en la guía.
- La clienta demo y el admin permiten verificar los dos roles (200/403 en `/api/admin/estado`) sin pasos manuales previos — claves para el UAT delegado en maura-uat.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 2-Cuentas de cliente y carro persistente*
*Context gathered: 2026-09-29*
