---
phase: 04-panel-de-administraci-n-y-asistente-ia
plan: 01
subsystem: api
tags: [openapi, contrato-api, admin-panel, asistente-ia, gemini, google-genai, mini-rag, maquina-de-estados, adr, api-first, soft-delete]

requires:
  - phase: 03-checkout-webpay-y-rdenes
    provides: "contrato_api.yaml 0.3.0 (bearerAuth, roles, convención de errores, security: [] del retorno) y ADRs 011-014 — la base que este contrato extiende y los ADRs nuevos citan (015→011, 016→013)"
  - phase: 04-panel-de-administraci-n-y-asistente-ia (research + ui-spec)
    provides: "04-RESEARCH.md — Patterns 1-3 firmados contra el README del SDK @ v2.25.0 (response_json_schema, errors.APIError, GEMINI_API_KEY auto-pickup) que ADR-017 cita como evidencia; 04-UI-SPEC.md — copys locked (409 'Ese pedido ya no está en curso.', 429/503 del chat) y defaults (≤5 stock, 500 chars, 10 mensajes, 3 cards) confirmados como contrato"
provides:
  - "contrato_api.yaml 0.4.0: GET/POST /api/admin/productos, PUT /api/admin/productos/{producto_id} (allow-list ProductoEditar SIN activo ni id — D-52), PATCH /api/admin/productos/{producto_id}/activo (primer PATCH del proyecto), GET /api/admin/pedidos, PATCH /api/admin/pedidos/{numero}/estado con 409 (copy locked), GET /api/admin/metricas con la evolución del demo /api/admin/estado narrada (D-54), POST /api/asistente público (security: [], D-59) con 422/429/503; schemas ProductoCrear/ProductoEditar/ProductoAdmin/PedidoAdmin/PedidoTransicion/Metricas/ChatMensaje/ChatRespuesta; filas 503/429 nuevas sin cifras y 409 con segundo uso"
  - "ADRs 015-017 (índice a 17): RequireAdmin como espejo UX del 403 sobre ADR-011, máquina de estados con UNA transición admin PENDING→CANCELLED (huérfanas D-48/D-49 cobradas), asistente mini-RAG con structured output citando la evidencia de 04-RESEARCH contra el README @ v2.25.0 y la degradación 503 contrastada con el fail-fast de secret_key"
  - "README de 04_arquitectura: IA como stack construido (google-genai 2.25.0 pin >=2.25,<3 citando ADR-017), árbol del alumno con los archivos de la etapa (routers/admin reescrito a CRUD real, asistente backend/frontend, RequireAdmin, badges.ts, features/admin y features/asistente), regla 3 con la nota del wrapper, regla 6 con su SEGUNDA excepción narrada (ProductCard del chat)"
affects: [04-panel-de-administraci-n-y-asistente-ia (planes 04-02, 04-03, 04-04, 04-05), guia-12..15, Gran verificación final de fase 4 (fila contrato 0.4.0 ↔ /docs con Authorize admin)]

actuals:
  tokens: 16239     # chars/4 sobre el diff real commiteado (64957 chars en 5 archivos)
  tasks: 3
  commits: 3        # medido: git rev-list --count e3b4e425..HEAD

tech-stack:
  added: []         # sin paquetes nuevos en el repo (guide-only, D-17); google-genai 2.25.0 (pin >=2.25,<3) queda documentado en stack y ADR-017 — las guías de 04-04 lo enseñarán a instalar
  patterns:
    - "El contrato como testigo de garantías estructurales (segunda aparición): la allow-list de edición SIN activo ni id veta el mass assignment por AUSENCIA de campo (la misma lección de CheckoutCreate sin precio), y el toggle de D-52 es escritura propia en su PATCH"
    - "ADR firmado con evidencia externa: ADR-017 cita 04-RESEARCH.md con link relativo (Patterns 1-3 contra el README @ v2.25.0) igual que ADR-012 citó el spike — no se firma sobre supuestos (D-56)"
    - "security: [] deliberado con el porqué narrado en description: el asistente es la segunda aparición del patrón del retorno (D-59)"

key-files:
  created:
    - docs/04_arquitectura/adr/015-panel-admin-protegido-por-rol.md
    - docs/04_arquitectura/adr/016-maquina-de-estados-con-transicion-admin.md
    - docs/04_arquitectura/adr/017-asistente-ia-mini-rag-key-solo-backend.md
  modified:
    - docs/04_arquitectura/contrato_api.yaml
    - docs/04_arquitectura/README.md

key-decisions:
  - "Contrato 0.4.0 aprobado ANTES de las guías (D-15/ADR-007 honrado): 7 paths nuevos con TODAS las respuestas declaradas (el 403 'Requiere rol admin' verbatim del demo en cada path admin — Pitfall 5), 8 schemas con la convención vigente, y el retiro del demo /api/admin/estado NARRADO en description (Pitfall 7: jamás en silencio; las guías 05/06 no se re-editan)"
  - "OQ3 resuelta como 409 para la transición ilegal (conflicto de ESTADO del recurso, no un dato mal formado) con el copy locked del UI-SPEC 'Ese pedido ya no está en curso.'; la fila 409 de la tabla de errores gana su segundo uso"
  - "ADR-015 registra el guard por rol como UX cortés — get_current_admin en CADA endpoint es la seguridad real (lección D-33 hecha patrón); NoAutorizado SIN expulsar al login (le falta permiso, no identidad); negativa honesta del sync de dos niveles"
  - "ADR-016 fija la máquina en los 4 estados existentes con dueño por transición y UNA manual admin (PENDING→CANCELLED, las huérfanas de D-48/D-49); cancelar PENDING no toca stock (D-35); PAID terminal en v1 con el refund ADMN-05 explícitamente diferido a v2"
  - "ADR-017 firma el mini-RAG honesto (catálogo activo completo en el prompt + response_json_schema + validación de ids en el servidor) citando la evidencia de 04-RESEARCH contra el README @ v2.25.0; la degradación 503 sin key es regla numerada en contraste EXPLÍCITO con el fail-fast de secret_key; el drift Interactions API queda narrado como lección (Pitfall 1)"
  - "Defaults del UI-SPEC confirmados como contrato: stock bajo ≤ 5 (D-53), mensaje ≤ 500 chars, historial ≤ 10, máximo 3 cards — y el 429 declarado SIN cifras de límites (concern abierto de STATE.md: no hay fuente pública sin login)"

patterns-established:
  - "Filas 429/503 en la tabla de convención de errores con su segundo uso del 409: la degradación del servicio externo ES parte del contrato — las guías de 04-04 replicarán la declaración en responses={} (Pitfall 5)"
  - "El description del path como lugar de la evolución narrada: GET /api/admin/metricas cuenta por qué el demo se retira — el mecanismo de la subida 0.3.0→0.4.0 (D-54)"
  - "PedidoTransicion con enum de un solo valor (cancelled): el enum del contrato ES la máquina de estados de ADR-016 — lo que el cuerpo no puede llevar, la UI no puede pedir"

requirements-completed: [ADMN-01, ADMN-02, ADMN-03, ADMN-04, AIAS-01, AIAS-02, AIAS-03]

coverage:
  - id: D1
    description: "Contrato 0.4.0 con la superficie completa de la etapa 4: 7 paths nuevos (GET/POST /api/admin/productos, PUT con allow-list, PATCH activo — primer PATCH del proyecto, GET /api/admin/pedidos, PATCH /api/admin/pedidos/{numero}/estado con 409 copy locked, GET /api/admin/metricas con evolución narrada, POST /api/asistente público con 422/429/503), 8 schemas nuevos, filas 503/429 sin cifras, 409 con segundo uso, todos los paths admin con bearerAuth + 403 'Requiere rol admin' — superficie de fases 1-3 intacta (10 paths y 10 schemas existentes)"
    requirement: ADMN-01
    verification:
      - kind: other
        ref: "grep chain del Task 1 (contrato04-ok): versión 0.4.0, 7 paths, 8 schemas, copies locked 409/403, filas | 503 | / | 429 |, transición ilegal, topes maxLength 500/maxItems 10, bloque /api/asistente con security: [] y 'Público por diseño' (gates awk acotados), /api/admin/estado mencionado pero sin path key, ProductoEditar sin property activo (gate negativo), paths fases 1-3 presentes, MAURA-000001 — pass"
      - kind: other
        ref: "PyYAML safe_load: parse ok, openapi 0.4.0, 17 paths / 18 schemas, asistente security=[], PedidoTransicion enum ['cancelled'], topes 500/10, productos maxItems 3, ProductoEditar props = allow-list de 7 campos sin activo/id — pass"
        status: pass
    human_judgment: false
  - id: D2
    description: "ADRs 015-017 (directorio llega a 17) con el formato canónico: 015 con 3 opciones (guard que extiende RequireAuth / solo backend / lógica duplicada), NoAutorizado sin expulsar al login y la negativa honesta del sync; 016 con estados de logística Y transiciones libres en descartadas, huérfanas D-48/D-49 cobradas y refund ADMN-05 diferido; 017 con la evidencia de 04-RESEARCH citada con link relativo, el contraste 503-vs-fail-fast como regla numerada, la validación de ids como responsabilidad del servidor y el drift Interactions API narrado"
    requirement: ADMN-03
    verification:
      - kind: other
        ref: "grep chain del Task 2 (adrs04-ok): 17 ADRs numerados, 015 con RequireAdmin/ADR-011/get_current_admin, 016 con PENDING/CANCELLED/ADMN-05/ADR-013/409, 017 con 04-RESEARCH/response_json_schema/v2.25.0/GEMINI_API_KEY/503/fail-fast, los tres con Opciones consideradas y Para conversar en clase — pass"
      - kind: other
        ref: "verificación de links: los 10 targets de links relativos existen en disco (007/009/011/012/013/014 + 04-RESEARCH.md); ACs por contenido (NoAutorizado 3 menciones, sync dos niveles, D-48/D-49 + diferido, regla EXPLÍCITA del contraste, drift Interactions) — pass"
        status: pass
    human_judgment: false
  - id: D3
    description: "README de 04_arquitectura: fila de IA real del stack (google-genai 2.25.0 pin >=2.25,<3 citando ADR-017, sin el placeholder 'llega en su fase'), árbol del alumno extendido (routers/admin.py reescrito a CRUD real, routers/asistente.py, services/admin.py, services/asistente.py único importador de google.genai, repositories/producto.py + pedido.py con notas de extensión, components/RequireAdmin.tsx, lib/badges.ts como módulo propio de BADGES, features/admin/ con las 5 piezas y features/asistente/), regla 3 con la nota del wrapper, regla 6 con su SEGUNDA excepción narrada (ProductCard) sin renumerar, índice a 17 filas — disclaimer guide-only byte-intacto"
    requirement: ADMN-04
    verification:
      - kind: other
        ref: "grep chain del Task 3 (readme-arq04-ok): google-genai, >=2.25,<3, 3 links de ADRs nuevos, routers/asistente.py, services/asistente.py, RequireAdmin, badges.ts, features/admin, features/asistente, ProductCard, ADR-011 presente, disclaimer guide-only presente — pass"
      - kind: other
        ref: "ACs adicionales: 'llega en su fase' ausente, comentario admin.py nuevo (CRUD real), reglas 1-6 sin renumerar, índice con exactamente 17 filas linkadas, 0 líneas del disclaimer en el diff — pass"
        status: pass
    human_judgment: false

duration: 12 min
completed: 2026-09-30
status: complete
plan_head_before: e3b4e4258e9efc05576544d089175e213aaa47ab
plan_head_after: adbcf25084cdb429e49314f47be2f885d91998bd
---

# Phase 4 Plan 01: Contrato 0.4.0 + ADRs 015-017 Summary

**Contrato OpenAPI 0.4.0 con los 7 endpoints reales de administración (allow-list sin activo, 409 de transición, métricas que reemplazan al demo narrándolo) y el asistente público con 422/429/503, más los ADRs 015-017 que registran el guard por rol, la máquina de estados y el mini-RAG citando evidencia firmada**

## Performance

- **Duration:** 12 min
- **Started:** 2026-09-30T21:08:03Z
- **Completed:** 2026-09-30T21:20:14Z
- **Tasks:** 3/3
- **Files modified:** 5 (1 contrato extendido, 3 ADRs nuevos, 1 README extendido)

## Accomplishments

- Contrato 0.3.0 → 0.4.0 ANTES de las guías (D-15): 7 paths nuevos, 8 schemas nuevos, filas 503/429 nuevas sin cifras, 409 con segundo uso, retiro narrado del demo `/api/admin/estado` (D-33/D-54) — superficie de fases 1-3 byte-intacta
- ADRs 015-017 con el esqueleto canónico y negativas honestas: el guard como espejo UX del 403, la máquina de 4 estados con UNA transición admin (huérfanas D-48/D-49 cobradas, refund ADMN-05 diferido), y el mini-RAG con la evidencia de 04-RESEARCH citada contra el README @ v2.25.0 (patrón ADR-012→spike)
- README de arquitectura: IA como stack construido, árbol del alumno con la etapa completa, segunda excepción de la regla 6 (ProductCard del chat) e índice a 17 ADRs — con el disclaimer guide-only intacto

## Task Commits

Each task was committed atomically:

1. **Task 1 (tracer): contrato 0.4.0** - `24b0261` (docs)
2. **Task 2: ADRs 015-017** - `652f63e` (docs)
3. **Task 3: README de 04_arquitectura** - `adbcf25` (docs)

Tracer feedback gate (auto-mode): `<verify>` re-ejecutado end-to-end sobre HEAD tras el commit → pass, expansión continuada.

## Files Created/Modified

- `docs/04_arquitectura/contrato_api.yaml` - 0.4.0: tag Administración reescrito (ADMN-01..04) + tag Asistente (AIAS-01..03), 7 paths admin/asistente, 8 schemas (ProductoCrear/ProductoEditar allow-list/ProductoAdmin/PedidoAdmin/PedidoTransicion/Metricas/ChatMensaje/ChatRespuesta), tabla de errores con 503/429 y 409 de segundo uso
- `docs/04_arquitectura/adr/015-panel-admin-protegido-por-rol.md` - RequireAdmin espejo UX del 403; get_current_admin en CADA endpoint como seguridad real (D-55, ADR-011)
- `docs/04_arquitectura/adr/016-maquina-de-estados-con-transicion-admin.md` - 4 estados con dueño por transición; UNA manual admin PENDING→CANCELLED; PAID terminal (D-50, ADR-013)
- `docs/04_arquitectura/adr/017-asistente-ia-mini-rag-key-solo-backend.md` - mini-RAG + structured output + key solo backend con degradación 503 vs fail-fast (D-56/D-60/D-61, evidencia 04-RESEARCH)
- `docs/04_arquitectura/README.md` - fila IA real, árbol extendido, reglas 3/6 anotadas, índice 17 ADRs

## Decisions Made

- OQ3 del research resuelta e implementada como **409** para la transición ilegal, con el copy locked "Ese pedido ya no está en curso." del UI-SPEC como example detail del contrato
- Los defaults auto del UI-SPEC quedaron confirmados como contrato: stock bajo ≤ 5 (D-53), mensaje ≤ 500, historial ≤ 10, máximo 3 cards — y el 429 declarado SIN cifras (concern abierto: límites no públicos sin login)
- El requestBody del PATCH de activo es un schema inline mínimo `{activo: boolean}` (sin schema nombrado): una escritura de un solo campo no merece símbolo propio en components
- El orden interno del bloque de administración respeta el orden del archivo original (reemplaza in situ al demo `/api/admin/estado`), y `/api/asistente` cierra el archivo como superficie más nueva

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Dos scalars YAML inválidos (colon-space en línea simple)**
- **Found during:** Task 1 (validación PyYAML posterior a la edición)
- **Issue:** Las descriptions de una sola línea `activo` de ProductoAdmin y `respuesta` de ChatRespuesta contenían `: ` interno ("(D-52): false saca…" / "…Naranja: naranja recién pelada…"), lo que rompía el parse YAML (mapping values are not allowed here, líneas 426 y 584)
- **Fix:** Reformulación con guion largo en ambos casos, conservando el contenido
- **Files modified:** docs/04_arquitectura/contrato_api.yaml
- **Verification:** `yaml.safe_load` pasa: openapi 0.4.0, 17 paths, 18 schemas; cadena completa del Task 1 re-ejecutada → contrato04-ok
- **Committed in:** 24b0261 (parte del commit del Task 1)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Fix menor de formato dentro del mismo task que lo introdujo; sin alcance extra. La validación YAML se sumó a la verificación del contrato como pieza permanente del gate.

## Issues Encountered

- **Path mangling de MSYS/Git Bash en Windows**: los patrones grep que comienzan con `/` (p. ej. `"/api/productos"`) son convertidos por MSYS a rutas Windows antes de llegar al grep — la cadena de verificación del Task 1 fallaba silenciosamente en TODOS los patrones con barra inicial (además, `grep` en este entorno es una función que delega en ugrep). Resuelto ejecutando las cadenas con `/usr/bin/grep` + `MSYS_NO_PATHCONV=1`, patrón por patrón idéntico al plan. Sin impacto en los artefactos; documentado aquí para los ejecutores futuros de esta fase.

## User Setup Required

None - no external service configuration required. (La `GEMINI_API_KEY` es paso del ALUMNO dentro de las guías de 04-04, no de este repo guide-only.)

## Next Phase Readiness

- Contrato 0.4.0 y ADRs 015-017 aprobados ANTES de las guías: 04-02 (docs 02/03 de la etapa) puede citarlos directamente; 04-03 (guia-12/13) y 04-04 (guia-14/15) implementan paths y schemas sin desviarse
- La Gran verificación final de fase 4 ya tiene su fila definida: contrato 0.4.0 ↔ `/docs` con Authorize admin + grep del build (`GEMINI_API_KEY` sin resultados en `dist/`)
- Blocker heredado vigente (no de este plan): los límites RPM/RPD del free tier de Gemini siguen requiriendo verificación logueada del usuario; el contrato y los ADRs ya se abstienen de cifras por diseño

## Self-Check: PASSED

- Files: contrato_api.yaml, adr/015-*.md, adr/016-*.md, adr/017-*.md, README.md — FOUND (5/5)
- Commits: 24b0261, 652f63e, adbcf25 — FOUND (3/3, verificados con git log)
- Verificaciones re-ejecutadas post-commit: contrato04-ok / adrs04-ok / readme-arq04-ok — todas PASS

---
*Phase: 04-panel-de-administraci-n-y-asistente-ia*
*Completed: 2026-09-30*
