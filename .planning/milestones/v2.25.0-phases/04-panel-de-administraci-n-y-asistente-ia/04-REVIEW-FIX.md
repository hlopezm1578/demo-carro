---
phase: 04-panel-de-administraci-n-y-asistente-ia
fixed_at: 2026-09-30T22:15:00-03:00
review_path: .planning/phases/04-panel-de-administraci-n-y-asistente-ia/04-REVIEW.md
iteration: 1
findings_in_scope: 6
fixed: 6
skipped: 0
status: all_fixed
---

# Phase 4: Code Review Fix Report

**Fixed at:** 2026-09-30T22:15:00-03:00
**Source review:** .planning/phases/04-panel-de-administraci-n-y-asistente-ia/04-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope (esta corrida): 6 — CR-01, WR-01, WR-02, WR-03, IN-02, IN-04
- Fixed: 6
- Skipped: 0
- Fuera de alcance por instrucción del orquestador (quedan **open** en el ledger): IN-01, IN-03 — decisiones editoriales/narrativas deferidas al usuario

## Fixed Issues

### CR-01: Router admin montaba los paths de productos bajo `/api/admin*`

**Files modified:** `docs/05_desarrollo/guia-12-panel-backend.md`
**Commit:** `9f2411b`
**Applied fix:** Los cuatro decoradores de productos ganan su segmento — `@router.get("/productos")`, `@router.post("/productos")`, `@router.put("/productos/{producto_id}")`, `@router.patch("/productos/{producto_id}/activo")` — y un comentario encima de `router = APIRouter(...)` enseña la regla: prefijo del `include_router` de la guía 5 (`/api/admin`) + segmento del decorador = path del contrato. Pedidos (`/pedidos`, `/pedidos/{numero}/estado`) y `/metricas` ya montaban correctamente — verificado, sin cambios. Docstrings y golpes httpx de los pasos 6/8 ya usaban los paths del contrato (no requirieron edición). Verificación: AST-parse del bloque embebido — 7/7 rutas resuelven a los paths del contrato 0.4.0.

### WR-01: Mini-verificación prometía `dict_keys([200, 422, 429, 503])`

**Files modified:** `docs/05_desarrollo/guia-14-asistente-backend.md`
**Commit:** `630ccb2`
**Applied fix:** La mini-verificación del paso 6 ahora espera `1 dict_keys([422, 429, 503])` y explica por qué: FastAPI guarda `route.responses` tal cual y agrega el 200 recién al generar el OpenAPI — coherente con el paso 7, donde `/docs` lista las cuatro.

### WR-02: `historial[].texto` sin tope en endpoint público

**Files modified:** `docs/05_desarrollo/guia-14-asistente-backend.md`, `docs/04_arquitectura/contrato_api.yaml`
**Commit:** `f4f2f0e`
**Applied fix:** `MensajeHistorial.texto` pasa a `str = Field(max_length=500)` (mismo tope del mensaje nuevo, RN-16) y el contrato agrega `maxLength: 500` en `ChatMensaje.historial.items.texto`. Coherencia narrativa: el "piensa" del paso 4, la mini-verificación (ahora imprime `500 500 10 3`, agregando el `maxLength` del texto del historial), la descripción del 422 en el router y la descripción del path + esquema `ChatMensaje` en el contrato — todo actualizado en espejo (string del 422 idéntico guía↔contrato, verificado). Verificación: YAML parse + AST del bloque de schemas + assert de espejo.

### WR-03: Mini-verificación del preflight no podía fallar

**Files modified:** `docs/05_desarrollo/guia-12-panel-backend.md`
**Commit:** `b284377`
**Applied fix:** Se mantiene la lección de CORS (OPTIONS → 200) pero se advierte que el middleware responde antes del routing, y se complementa con un GET sin token a `/api/admin/productos` esperando `401` — un `404` delataría un path no montado (habría atrapado CR-01 en el propio paso 7).

### IN-02: Guard de degradación no cubría la key VACÍA

**Files modified:** `docs/05_desarrollo/guia-14-asistente-backend.md`
**Commit:** `f4f57ba`
**Applied fix:** `if settings.gemini_api_key is None:` → `if not settings.gemini_api_key:` con comentario que nombra los DOS estados sin key (ausente `None` y línea vacía `GEMINI_API_KEY=` que el `.env.example` modela).
**Nota:** cambia una condición de lógica — marcado como **fixed: requires human verification** (truthiness estándar, riesgo bajo, pero la verificación aquí es estructural, no runtime).

### IN-04: `Metricas.top_5` sin el `maxItems: 5` del contrato

**Files modified:** `docs/05_desarrollo/guia-12-panel-backend.md`
**Commit:** `2f152e2`
**Applied fix:** `top_5: list[TopAroma] = Field(max_length=5)` — el espejo declarativo del `maxItems: 5` del contrato, ya no solo el `.limit(5)` del SQL. `Field` ya estaba importado en el bloque (verificado por AST).

## Skipped Issues

Ninguno de los 6 findings en alcance fue saltado.

**Fuera de alcance de esta corrida (quedan open en 04-REVIEW.md, con razón registrada en el ledger):**

- **IN-01** — espejo del 422 en el editor (5 de 7 campos): decisión editorial (agregar copys tocaría los "copys locked" del UI-SPEC, o suavizar la narrativa) deferida al usuario.
- **IN-03** — cláusula aclaratoria en ADR-017: decisión editorial de redacción, diferida al usuario.

## Verification

**Dónde corrió la verificación:** en el checkout principal (`workflow.use_worktrees: false` — no se creó worktree; los números son reproducibles directamente desde este árbol).

- Por fix (Tier 1+2): re-lectura de cada sección editada + AST-parse de los bloques Python embebidos (router admin, schemas, service), YAML-parse del contrato, asserts de espejo guía↔contrato (string 422, maxLength/maxItems) — todos en verde.
- Cadenas de verificación de los PLANs re-ejecutadas (`MSYS_NO_PATHCONV=1`), todas exit 0:
  - 04-01-PLAN: `contrato04-ok`, `adrs04-ok`, `readme-arq04-ok`
  - 04-03-PLAN: `g12-ok`, `g13-ok`
  - 04-04-PLAN: `g14-ok`, `g15-ok`

## Ledger

04-REVIEW.md actualizado con `**Status:**` por finding (fixed + hash de commit para los 6; open + razón de deferencia para IN-01/IN-03) — commit `ccf683b`.

---

_Fixed: 2026-09-30T22:15:00-03:00_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
