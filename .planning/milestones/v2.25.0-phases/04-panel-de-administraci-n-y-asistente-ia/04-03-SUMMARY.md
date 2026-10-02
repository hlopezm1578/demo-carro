---
phase: 04-panel-de-administraci-n-y-asistente-ia
plan: "03"
subsystem: docs
tags: [guia-educativa, panel-admin, fastapi, react, soft-delete, transicion-409, update-condicional, metricas-sql, requireadmin, layout-admin, badges-modulo, cors, contrato-040, admn]

requires:
  - phase: 04-panel-de-administraci-n-y-asistente-ia (plan 01)
    provides: "contrato_api.yaml 0.4.0 (los 7 paths admin: allow-list ProductoEditar sin activo ni id, PATCH toggle, PATCH transición con 409 example locked, GET metricas) y ADRs 015-016 que los 🧠 de ambas guías citan"
  - phase: 04-panel-de-administraci-n-y-asistente-ia (plan 02)
    provides: "docs/02 etapa 4 (RF-19..24, RN-14/RN-15, HU-12) y docs/03 pantallas 10-13 con copys locked + DFDs 12.0-14.0 que las guías implementan sin desviarse"
  - phase: 04-panel-de-administraci-n-y-asistente-ia (research + ui-spec)
    provides: "04-RESEARCH.md (Ejemplo C transiciones, Ejemplo D las 4 agregaciones, Pattern 4 RequireAdmin, Pattern 7 BADGES verbatim, Pitfalls 5/6/7) y 04-UI-SPEC.md (rutas 148-169, pantallas 10-13, Copywriting Contract, estados async)"
provides:
  - "docs/05_desarrollo/guia-12-panel-backend.md: el backend del panel por capas — schemas admin espejo del contrato (ProductoEditar allow-list por AUSENCIA de id/activo, PedidoTransicion Literal[cancelled], Metricas con top_5 snapshot, PedidoAdmin con email_clienta), repositories/producto con crear/actualizar/toggle/todos() y STOCK_BAJO_UMBRAL=5, repositories/pedido con todos() (join email) + anular() UPDATE condicional rowcount→señal + las 3 agregaciones, services/admin (AdminService + TransicionIlegal + MetricasService), routers/admin con get_current_admin en CADA endpoint y responses heredadas del dict PROTEGIDO, version 0.4.0 y la retirada del demo /api/admin/estado narrada (Pitfall 7)"
  - "docs/05_desarrollo/guia-13-panel-spa.md: la SPA del panel — RequireAdmin (delega en RequireAuth sin sesión, NoAutorizado sin expulsar con sesión sin rol), rama /admin FUERA del Layout de tienda, LayoutAdmin con subnav NavLink end, las 3 pantallas con estados/copys locked del UI-SPEC, editor inline como estado de pantalla, anulación en dos pasos inline con banner 409, apiPut/apiPatch (primer PUT/PATCH del corpus), tipos admin espejados y BADGES bajada a src/lib/badges.ts (la tercera consumidora que guia-11 anticipó, D-45)"
  - "El eslabón 11→12 de la cadena: el Siguiente de guia-11 enlaza guia-12-panel-backend.md por nombre de archivo (única edición autorizada a una guía previa) — la cadena 11→12→13→14 queda grep-verificable"
affects: [04-panel-de-administraci-n-y-asistente-ia (planes 04-04, 04-05), docs/05_desarrollo/guia-14..15, Gran verificación final de fase 4, UAT delegado de fase 4 en maura-uat (panel runtime con las órdenes reales de fase 3)]

actuals:
  tokens: 35800     # chars/4 sobre el diff real commiteado (143226 chars en 3 archivos)
  tasks: 2
  commits: 2        # medido: git rev-list --count efb8910..HEAD

tech-stack:
  added: []         # plan documental (repo guide-only, D-17): cero paquetes — el único de la fase (google-genai) llega en guia-14
  patterns:
    - "La allow-list demostrada por herencia: ProductoEditar(ProductoCrear) sin agregar NADA — la promesa de que las dos listas son la misma lista, y el mass assignment vetado por ausencia (espejo del precio ausente de CheckoutCreate)"
    - "La transición admin reutiliza la muralla del guard ya-PAID: UPDATE condicional WHERE estado='pending' con rowcount 0 → señal TransicionIlegal → 409 copy locked — la misma traducción service-señal/router-código de CarroNoComprable → 400, hecha patrón"
    - "Invalidación por PREFIJO de queryKey como lección de dos pantallas que ven el mismo dato: ['productos', 'admin'] y ['pedidos', 'admin'] comparten prefijo con catálogo e historial — desactivar/anular reacciona la otra pantalla sola"
    - "El dict PROTEGIDO (401/403) heredado con {**PROTEGIDO, ...} en las 7 firmas del router admin: la lección G-01-4 escalada de endpoint a panel"

key-files:
  created:
    - docs/05_desarrollo/guia-12-panel-backend.md
    - docs/05_desarrollo/guia-13-panel-spa.md
  modified:
    - docs/05_desarrollo/guia-11-pedidos-cierre.md   # solo su línea Siguiente (6 líneas): el eslabón a guia-12

key-decisions:
  - "ProductoEditar hereda de ProductoCrear sin cuerpo: la MISMA allow-list por herencia y la lección mass assignment leída por ausencia; el sku se GENERA en el repo (panel-{uuid8}) porque el upsert por sku es del seed — crear dos veces crea DOS productos, el idempotente por diseño es el ESTADO (ADMN-01 edge)"
  - "PedidoTransicion usa Literal[\"cancelled\"] en el schema en vez de un enum nuevo de un valor: la meta única es la FORMA de la entrada; la máquina completa vive en ADR-016 y el WHERE del UPDATE"
  - "El editor de productos hidrata descripción y notas desde la FICHA pública (ProductoAdmin es liviano a propósito en 0.4.0): reusa la key ['producto', id] del catálogo; para inactivos la ficha 404a y el form parte con esas dos vacías — hueco narrado como deseo 0.5.0, jamás desvío improvisado"
  - "Los badges de producto (Activo/Inactivo/Stock bajo) y el espejo STOCK_BAJO=5 viven en lib/badges.ts junto a BADGES: una sola verdad del estado del pedido (D-45) y el contraste Pitfall 6 en el mismo módulo que lo enseña"
  - "main.py: el include_router del admin ya existía desde guia-05 (cambió el contenido, no el registro) — lo único del archivo es la versión 0.4.0 y el CORS (ver desviación)"

patterns-established:
  - "La retirada narrada de un endpoint: el demo /api/admin/estado se va con honors en la intro (Pitfall 7) — las guías viejas jamás se re-editan, el contrato cuenta su propia historia"
  - "La asimetría de confirmación como regla citable: toggle SIN confirmación (reversible, feedback = badge en el lugar) contra Anular en dos pasos inline (irreversible, patrón 'Vaciar carro') — la confirmación se cobra donde no hay vuelta"
  - "Cero honesto desde el SQL: COALESCE(SUM(...), 0) para ingresos y {estado: 0 para los 4} pisado por el group_by — el KPI sin datos muestra $0/0, no None"

requirements-completed: [ADMN-01, ADMN-02, ADMN-03, ADMN-04]  # copiado verbatim del PLAN; el flip en REQUIREMENTS.md queda diferido por el shared-ID gate (04-05 declara los mismos IDs y no tiene SUMMARY)

coverage:
  - id: D1
    description: "guia-12-panel-backend.md enseña el backend del panel por capas implementando el contrato 0.4.0 sin desviarse: intro que narra la retirada de /api/admin/estado (Pitfall 7) SIN paso de instalación, schemas admin espejo (ProductoEditar allow-list sin activo ni id con la lección mass assignment, PedidoTransicion Literal[cancelled], Metricas top_5 snapshot, PedidoAdmin email_clienta), repositories con escribir/todos()/toggle y STOCK_BAJO_UMBRAL=5 (Pitfall 6 narrado), la transición como UPDATE condicional con rowcount→TransicionIlegal→409 copy locked sin tocar stock (D-35/D-50), métricas como agregaciones SQL (sum COALESCE, group_by 4 estados, top 5 snapshot, count solo activos), router con get_current_admin en CADA endpoint y responses 401/403/404/409/422 declaradas (ADR-015, Pitfall 5), main.py version=0.4.0, prueba de fuego httpx (200/403 por rol, idempotencia de estado del PUT, huérfana 200→409→422, soft delete vs snapshot, métricas contra las órdenes reales de fase 3) con estructura canónica (8 🧠, 13 mini-verificaciones, cierre con Siguiente→guia-13)"
    requirement: ADMN-01
    verification:
      - kind: other
        ref: "grep chain del Task 1 (g12-ok) re-ejecutada post-ediciones: get_current_admin, STOCK_BAJO_UMBRAL, rowcount, TransicionIlegal, 409 + 'Ese pedido ya no está en curso', 403 + 'Requiere rol admin', activo, snapshot, group_by/func./sum(, version=\"0.4.0\", admin/estado, ProductoEditar, PedidoTransicion, Metricas, ADR-015, ADR-016, contrato_api.yaml, todos(), 8×'El desarrollador piensa' (≥5), 13×'Mini-verificación' (≥4), Punto de control, Siguiente→guia-13-panel-spa — pass"
      - kind: other
        ref: "chequeo de no-instalación: la única aparición de 'uv add' en guia-12 es la negación 'ni `uv add`, ni `.env` nuevo' (cero pasos de instalación, el stack ya está) — pass"
        status: pass
    human_judgment: false
  - id: D2
    description: "guia-13-panel-spa.md enseña la SPA del panel: RequireAdmin que delega en RequireAuth sin sesión y muestra NoAutorizado con sesión sin rol SIN expulsar (D-55, ADR-011/015), BADGES bajada a src/lib/badges.ts con las tres consumidoras importando del módulo (D-45, guías 10/11 byte-intactas — verificado por diff), apiPut/apiPatch + tipos admin espejo del contrato, rama /admin FUERA del Layout con LayoutAdmin (subnav NavLink end + Outlet, sin Footer ni burbuja), Navbar con Panel solo si usuario.rol === 'admin', AdminProductos (tabla de TODOS, editor inline como estado sin ruta propia, form sin activo, validación espejo con los 5 copys, toggle sin confirmación), AdminPedidos (Anular solo en pending, dos pasos inline, banner 409 copy locked, sin vista de detalle RN-08, invalidación por prefijo que refresca el historial de la clienta D-48/D-49), AdminMetricas (3 KPI + top 5 snapshot texto plano, cero honesto), prueba de fuego en el navegador (clienta rechazada sin expulsión, returnTo al panel, vitrina que reacciona sola, huérfana anulada en dos pestañas) con 9 🧠 y 14 mini-verificaciones, cierre Siguiente→guia-14-asistente-backend"
    requirement: ADMN-02
    verification:
      - kind: other
        ref: "grep chain del Task 2 (g13-ok): RequireAdmin, NoAutorizado, LayoutAdmin, Outlet, badges.ts/lib/badges, BADGES, 'Nuevo producto', 'Guardar cambios', 'Anular el pedido', 'Sí, anular', 'Ese pedido ya no está en curso', 'Ingresos totales', 'Top 5 aromas vendidos', 'Stock bajo', 'Aún no hay productos', 'No tienes acceso al panel', useMutation, invalidateQueries, usuario.rol, ADR-011/ADR-015, 9×'El desarrollador piensa' (≥5), 14×'Mini-verificación' (≥3), Punto de control, Siguiente→guia-14-asistente-backend, y guia-11 contiene guia-12-panel-backend — pass"
      - kind: other
        ref: "git diff de guia-11: 6 insertions / 6 deletions, todas dentro del bloque 'Siguiente:' (única edición autorizada a una guía previa); guia-10 sin cambios — pass"
        status: pass
    human_judgment: false

duration: 18 min
completed: 2026-09-30
status: complete
plan_head_before: efb8910eea89b56e3fb265e08634805a9a6f40bb
plan_head_after: 2cc278edbde2b9af8554a7ddd4358292571cf7c3
---

# Phase 4 Plan 03: El panel de administración (guías 12-13) Summary

**guia-12 enseña el backend del panel por capas (CRUD con soft delete visible, la transición única como UPDATE condicional con 409 copy locked, métricas SQL agregadas, todo bajo get_current_admin con responses declaradas y el demo /api/admin/estado retirado con narración) y guia-13 la SPA (RequireAdmin sin expulsión, LayoutAdmin con subnav, las 3 pantallas con copys locked, apiPut/apiPatch y BADGES a lib/badges.ts) — el eslabón 11→12→13→14 queda grep-verificable**

## Performance

- **Duration:** 18 min
- **Started:** 2026-09-30T21:40:01Z
- **Completed:** 2026-09-30T21:58:29Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- El backend del panel completo en guia-12: siete operaciones admin espejo del contrato 0.4.0, con la lección de mass assignment por ausencia de campo y la máquina de estados validada en el servidor (D-50, T-04-08)
- La huérfana PENDING de fase 3 por fin tiene gestión: la mini-verificación la anula en runtime y la clienta la ve "Anulado" en su historial sin editar guia-11 (D-48/D-49)
- La SPA del panel en guia-13: guard por rol con su pantalla de no autorizado, layout paralelo sin Footer ni burbuja, editor inline como estado de pantalla, anulación en dos pasos con banner 409 y las métricas con cero honesto
- BADGES bajó a módulo propio cobrando la nota de guia-11 (D-45), y los primeros PUT/PATCH del corpus viven en lib/api.ts con la hidratación del editor resuelta honestamente contra un ProductoAdmin liviano

## Task Commits

Each task was committed atomically:

1. **Task 1: guia-12-panel-backend.md** - `0caf90d` (docs)
2. **Task 2: guia-13-panel-spa.md + eslabón guia-11** - `2cc278e` (docs)

**Plan metadata:** (se registra en el commit docs final de este plan)

## Files Created/Modified
- `docs/05_desarrollo/guia-12-panel-backend.md` - Guía del backend del panel: schemas admin allow-list, repos con toggle/transición/agregaciones, services con TransicionIlegal y MetricasService, router con get_current_admin en cada endpoint, prueba de fuego httpx
- `docs/05_desarrollo/guia-13-panel-spa.md` - Guía de la SPA del panel: RequireAdmin/NoAutorizado, lib/badges.ts, apiPut/apiPatch + tipos, rama /admin, LayoutAdmin + Navbar, las 3 pantallas, prueba de fuego en el navegador
- `docs/05_desarrollo/guia-11-pedidos-cierre.md` - Solo su línea Siguiente: enlaza guia-12-panel-backend.md por nombre de archivo (continuidad de la cadena, precedente 02-05)

## Decisions Made
- Ver `key-decisions` en el frontmatter: allow-list por herencia, Literal para la meta única, sku generado (upsert es del seed), hidratación del editor desde la ficha pública con hueco honesto para inactivos, queryKeys con prefijo compartido, badges de producto junto a BADGES

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] CORS de main.py crece a PUT y PATCH en guia-12**
- **Found during:** Task 1 (paso 7, main.py)
- **Issue:** El plan fija "main.py solo agrega include_router y sube version=0.4.0" — pero el panel introduce los primeros PUT/PATCH del proyecto y `allow_methods` quedó en `["GET", "POST"]` desde guia-05. En dev el proxy de Vite disimula la omisión (same-origin, el CORS ni actúa) y el olvido sería invisible hasta el despliegue de fase 5, cuando la SPA estática en otro origen rechace el preflight con un error que nada tiene que ver con el código del panel
- **Fix:** guia-12 paso 7 extiende la lista explícita a `["GET", "POST", "PUT", "PATCH"]` con la narración de la propia lección de guia-05 ("el CORS crece con la API") y una mini-verificación del preflight OPTIONS que responde 200 — la misma vacuna preventiva que guia-05 aplicó antes del primer POST cross-origin
- **Files modified:** docs/05_desarrollo/guia-12-panel-backend.md (paso 7)
- **Verification:** mini-verificación del paso 7 (preflight PATCH → 200) documentada en la guía
- **Committed in:** 0caf90d (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 missing critical)
**Impact on plan:** Sin scope creep: una línea de código de guía + su narración, aplicando la lección que el propio corpus estableció en la fase 2. Todo lo demás se ejecutó exactamente como el plan lo escribió.

## Issues Encountered
- El `read_first` del plan citaba `guia-06-cuentas-frontend.md`; el archivo real es `guia-06-sesion-frontend.md` (drift de nombre en el plan, sin impacto: se leyó el correcto para el patrón RequireAuth)
- Ninguna otra: ambas cadenas de verificación pasaron a la primera (g12-ok, g13-ok)

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Listo para 04-04 (guia-14/15: asistente con google-genai) — la SPA del panel dejó la rama de layout paralela montada y el UI-SPEC de la burbuja especifica que vive en el Layout de TIENDA, no en el del panel
- La verificación runtime del panel queda para el UAT delegado en maura-uat (regla AGENTS.md): construir guías 12-13 sobre el taller con las órdenes reales de los 4 flujos de fase 3, incluida la anulación de la huérfana y el 409 de la doble pestaña
- Los fixes de bugs que el UAT encuentre se corrigen en ambos lugares (maura-uat y la guía), según la instrucción persistida del usuario

## Self-Check: PASSED

- Files exist: docs/05_desarrollo/guia-12-panel-backend.md (1350 líneas), docs/05_desarrollo/guia-13-panel-spa.md (1655 líneas), docs/05_desarrollo/guia-11-pedidos-cierre.md (editado)
- Commits exist: 0caf90d (Task 1), 2cc278e (Task 2) — verificados en git log
- Ambas verificaciones del plan re-ejecutadas post-ediciones: g12-ok, g13-ok

---
*Phase: 04-panel-de-administraci-n-y-asistente-ia*
*Completed: 2026-09-30*
