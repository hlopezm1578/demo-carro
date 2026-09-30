---
phase: 03-checkout-webpay-y-rdenes
fixed_at: 2026-09-30T18:05:00Z
review_path: .planning/phases/03-checkout-webpay-y-rdenes/03-REVIEW.md
iteration: 1
findings_in_scope: 6
fixed: 6
skipped: 0
status: all_fixed
---

# Phase 3: Code Review Fix Report

**Fixed at:** 2026-09-30T18:05:00Z
**Source review:** .planning/phases/03-checkout-webpay-y-rdenes/03-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 6 (CR-01, WR-01..WR-05 — Critical + Warning; los 6 Info quedan fuera del scope por instrucción del orquestador)
- Fixed: 6
- Skipped: 0

**Modo de trabajo:** `workflow.use_worktrees=false` → todos los edits y commits se hicieron
directamente en el checkout principal (rama `master`), sin worktree. Toda la verificación de abajo
corrió en ese mismo checkout principal (reproducible desde el árbol actual).

## Fixed Issues

### CR-01: `routers/retorno.py` importa `Error` desde un módulo que no lo define — ImportError al copiar la guía tal cual

**Files modified:** `docs/05_desarrollo/guia-09-ordenes-webpay.md`
**Commit:** 97b7346
**Applied fix:** En el bloque de `backend/app/routers/retorno.py` (paso 8), el import se cambió a
`from app.schemas.producto import Error` con el mismo comentario de los otros dos routers de la
guía ("el cuerpo de error vive en schemas/producto desde la guía 4"). Verificado: los 3 routers
(checkout, retorno, pedidos) ahora importan `Error` desde `schemas/producto` y no queda ninguna
ocurrencia de `from app.schemas.pedido import Error`. Con esto, la mini-verificación del propio
paso 8 (`from app.routers import checkout, pedidos, retorno`) vuelve a pasar.

### WR-01: `services/pedidos.py` importa `transbank` — viola la regla "único archivo que importa transbank"

**Files modified:** `docs/05_desarrollo/guia-09-ordenes-webpay.md`
**Commit:** 2572b81
**Applied fix:** (a) El wrapper `services/webpay.py` (paso 5) ahora importa
`TransactionCommitError` y su `commit()` declara `dict | None`, atrapando la excepción tipada
adentro y devolviendo `None` como señal de dominio. (b) `services/pedidos.py` (pasos 6-7) eliminó
el import de transbank; `_confirmar` cambió el `try/except` por `commit = webpay.commit(token_ws);
if commit is None: return RetornoResultado(estado="error", ...)`. (c) Narrativas actualizadas en
paso 5 (tercer detalle del wrapper: "ni imports, ni errores, ni vocabulario del SDK fuera de este
archivo"), paso 7 (🧠 y docstrings de `_cancelar`/`_confirmar`), mini-verificación del paso 10,
bloque "❌ El error que este archivo evita" #1 y bullets de cierre. La mini-verificación del propio
paso 5 (`grep -r transbank backend/app` → SOLO `services/webpay.py`) vuelve a ser cierta:
verificado que de los 20 fences Python de la guía, el único que menciona transbank es el del
wrapper. Runtime: cambió la señal del camino de error (excepción → `None`); re-verificar en el
próximo pase UAT.

### WR-02: `return_url` construido desde `settings.cors_origins[0]` (origen de la SPA)

**Files modified:** `docs/05_desarrollo/guia-09-ordenes-webpay.md`
**Commit:** 4a3484a
**Applied fix:** El paso 6 ahora instruye extender `app/config.py` con `backend_url: str =
"http://localhost:8000"` (sección "Etapa 3: pago Webpay (ADR-012)", misma forma que la extensión de
la etapa 2 en guía 5) y `iniciar_checkout` usa `return_url=f"{settings.backend_url}/api/pago/retorno"`.
La narrativa explica la asimetría ida/vuelta: el `return_url` apunta al BACKEND (Webpay devuelve el
navegador a la API) y el 302 de `_hacia_spa` sigue apuntando a la SPA (`cors_origins[0]`, uso que
es correcto y se conserva, ahora con nota de asimetría en su docstring); se narra que en dev el
proxy `/api` de Vite disimulaba la diferencia y que la fase 5 congela ambas URLs. La
mini-verificación del paso 6 se extendió para imprimir `settings.backend_url`. Runtime: la URL que
viaja a Webpay cambia (`localhost:8000` directo en vez de `localhost:5173` vía proxy); re-verificar
en el próximo pase UAT.

### WR-03: El guard ya-PAID (y el de `_cancelar`) es read-check-write en Python

**Files modified:** `docs/05_desarrollo/guia-09-ordenes-webpay.md`
**Commit:** 2b21df0
**Status:** fixed: requires human verification (cambio de semántica de concurrencia)
**Applied fix:** `_confirmar` reordenado: criterio doble primero (sin escritura) y la transición
`pending → paid` ES el guard — `UPDATE pedidos SET estado='paid' WHERE id=? AND estado='pending'`
con `rowcount == 0` → re-mostrar `pagado` sin side effects; el descuento atómico corre después,
dentro de la misma transacción (rollback en `StockInsuficiente` revierte transición + descuento
parcial, y la orden queda REJECTED igual que antes). `_cancelar` usa el mismo UPDATE condicional
`pending → cancelled` (el WHERE es el guard: un retorno tardío no pisa estado decidido). El script
`carrera.py` del paso 10 se actualizó para espejar el guard atómico (y `from sqlalchemy import
select, update`). Narrativas actualizadas: 🧠 del paso 7 ("la MISMA muralla del stock, ahora para
el estado — check y write en UNA sola operación"), bullet de cierre. Sintaxis de los fences
verificada con `ast.parse`; la semántica de concurrencia (rowcount decide, doble retorno del mismo
token) requiere verificación runtime — cubierta por la corrida `carrera.py` del próximo pase UAT.

### WR-04: La narrativa del F5 es factualmente incorrecta

**Files modified:** `docs/05_desarrollo/guia-10-retorno-voucher.md`, `docs/05_desarrollo/guia-11-pedidos-cierre.md`, `docs/05_desarrollo/guia-09-ordenes-webpay.md`
**Commit:** d90f5b8
**Applied fix:** (a) guia-10 paso 7: 🧠, mini-verificación F5, item 7 de la verificación de la guía
y bullet de cierre ahora explican el mecanismo real — el F5 sobre `/pago/resultado` re-carga la
ruta de la SPA y re-fetchea `GET /api/pedidos/{numero}` (lectura sin efectos; el retorno del
backend NO se ejecuta), y el guard ya-PAID cubre el caso donde lo que se repite es la NAVEGACIÓN al
`return_url` del backend (back/forward, retries — el spike observó 7 repeticiones). (b) guia-11
Gran verificación final fila 7 corregida con el mismo mecanismo. (c) guia-09 punto de control 3
re-enfocado a la navegación repetida al retorno (deja de atribuirle el guard al F5).

### WR-05: El diccionario de datos de PEDIDO (§2.2) no declara `fecha`

**Files modified:** `docs/03_diseno.md`
**Commit:** 0b1bd2d
**Applied fix:** Se agregó la fila `| fecha | Fecha-hora | — | Sí | Momento en que la orden nace
al iniciar el pago (D-34); viaja en OrdenLista del contrato y se muestra en voucher e historial
(RF-17) |` entre `total` y `usuario_id` (mismo orden que el modelo). Verificado programáticamente:
diccionario §2.2 PEDIDO == columnas `mapped_column` del modelo de guia-09, campo a campo y en el
mismo orden (`id, numero, estado, total, fecha, usuario_id`) — la afirmación "campo a campo… ni
una más" del paso 2 de la guía 9 ahora es cierta sin tocar la guía.

## Verification

**Dónde corrió:** checkout principal (`D:/Repos/demo-carro`, rama `master`) — `workflow.use_worktrees=false`.

**Cadenas de verificación de los planes de fase (re-ejecutadas post-fix, todas PASS):**

| Cadena | Plan de origen | Resultado |
|---|---|---|
| `g9-ok` | 03-04-PLAN.md Task 1 (guia-09) | PASS |
| `g10-ok` | 03-04-PLAN.md Task 2 (guia-10, con gates negativos) | PASS |
| `g11-ok` | 03-05-PLAN.md Task 1 (guia-11) | PASS |
| `dis03-ok` | 03-03-PLAN.md Task 2 (03_diseno.md) | PASS |

**Verificaciones adicionales (Tier 2 por fix):**
- CR-01: 0 ocurrencias de `from app.schemas.pedido import Error`; 3 de `from app.schemas.producto import Error` (los 3 routers).
- WR-01: de los 20 fences Python de guia-09, solo el de `services/webpay.py` menciona transbank (la mini-verificación `grep -r transbank backend/app` del paso 5 vuelve a pasar al seguir la guía). `ast.parse` OK en los fences de webpay.py, pedidos.py (ida) y métodos del paso 7.
- WR-02: snippet de config parsea (envuelto en clase); el bloque de pedidos usa `settings.backend_url` sin `cors_origins`; el único uso de código restante de `cors_origins[0]` es `_hacia_spa` (correcto: el 302 apunta a la SPA).
- WR-03: `ast.parse` OK en pedidos.py (ida), métodos del paso 7 y `carrera.py`; `update` importado donde se usa; guards read-check-write eliminados (no queda `pedido.estado == EstadoPedido.paid` ni `pedido.estado != EstadoPedido.pending` como guards).
- WR-05: assert programático diccionario §2.2 == columnas del modelo (campo a campo, mismo orden).

**Nota UAT:** el app de referencia (`D:/Repos/maura-uat`) quedó construido con las guías pre-fix;
los cambios de comportamiento embebido (WR-01 señal `None`, WR-02 URL `backend_url`, WR-03 guard
atómico — incluida la corrida de `carrera.py`) deben espejarse y re-verificarse en el próximo pase
UAT delegado al agente sobre `maura-uat`, siguiendo las guías ya corregidas (regla del workspace:
bug fix en guías + espejo en maura-uat para desbloquear la verificación runtime).

## Skipped Issues

Ninguno — los 6 hallazgos en scope fueron corregidos. Los 6 Info (IN-01..IN-06) quedan sin tocar
por decisión del orquestador (fuera del scope de este fix).

---

_Fixed: 2026-09-30T18:05:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
