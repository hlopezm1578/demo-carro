---
phase: 02-cuentas-de-cliente-y-carro-persistente
fixed_at: 2026-09-29T18:16:11Z
review_path: .planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-REVIEW.md
iteration: 1
findings_in_scope: 8
fixed: 8
skipped: 0
status: all_fixed
---

# Phase 02: Code Review Fix Report

**Fixed at:** 2026-09-29T18:16:11Z
**Source review:** `.planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope (critical + warning): 8
- Fixed: 8
- Skipped: 0

**Scope note:** repo guide-only (D-17) — todos los "fixes" son ediciones a documentación
(contrato, diseño, guías 5-8); el código vive dentro de los bloques de las guías.

**Verificación (dónde corrió):** `workflow.use_worktrees=false` — los fixes se editaron y
commitearon directamente en el checkout principal `D:/Repos/demo-carro` (sin worktree
aislado). Tier 1 (re-read de cada sección editada) en todos; Tier 2: `ast.parse` sobre los
16 bloques Python de guia-05 (16/16 OK) y `yaml.safe_load` del contrato (OK). La
re-ejecución UAT de las mini-verificaciones afectadas (CR-01 en especial) corresponde al
flujo delegado en `D:/Repos/maura-uat`, con la regla de corregir en los dos lugares
(la guía ya quedó corregida acá).

## Fixed Issues

### CR-01: Los routers de guia-05 importan `Error` desde `app.schemas.usuario` — ese módulo no define `Error`

**Files modified:** `docs/05_desarrollo/guia-05-cuentas-backend.md`
**Commit:** a1983ff
**Applied fix:** Ambos routers (`auth.py` y `admin.py`) ahora importan `Error` desde su
módulo real `app.schemas.producto`, con comentario inline que señala que vive ahí desde la
guía 4 (opción mínima y consistente con la lección de capas: `schemas/usuario.py` define
solo `RegistroCreate`, `UsuarioPublico`, `Token`). Verificado: los 16 bloques Python de la
guía parsean y no queda ningún `from app.schemas.usuario import Error`.

### WR-01: Total aritméticamente erróneo ($26.980; el correcto es $26.970)

**Files modified:** `docs/03_diseno.md`, `docs/05_desarrollo/guia-07-carro.md`, `docs/05_desarrollo/guia-08-checkout.md`
**Commit:** b6474a7
**Applied fix:** `$26.980` → `$26.970` en los cuatro lugares (wireframes de carro y
checkout en 03_diseno:613/656, mini-verificación de guia-07 y de guia-08). Aritmética
verificada por script (2×7990 + 10990 = 26970); grep confirma cero ocurrencias de
`$26.980` restantes en docs/.

### WR-02: El interceptor 401 podía disparar dentro del propio login

**Files modified:** `docs/05_desarrollo/guia-06-sesion-frontend.md`
**Commit:** 6fcad69 — **fixed: requires human verification** (cambia lógica enseñada)
**Applied fix:** Guard por construcción (opción preferida del review, alineada con Pitfall 5
/ D-22 / T-02-11): `pedir()` acepta `{ sinAuth }`; `apiPostForm` marca el login
`sinAuth: true`, así el login JAMÁS adjunta `Authorization` — ni con un token viejo en el
store tras un error de red en `verificar`. El interceptor ahora condiciona a
`llevaBearer` (`token !== null && !sinAuth`). Prose del paso 4 (:189-196) reescrito para
describir la garantía real, y el Pitfall 3 del cierre actualizado al guard real
(`res.status === 401 && llevaBearer`). La invariante declarada queda verdadera por el
código, no por el estado de la pantalla.

### WR-03: La cantidad guardada nunca se corregía y el badge contaba unidades sin tapar

**Files modified:** `docs/05_desarrollo/guia-07-carro.md`
**Commit:** d22e080 — **fixed: requires human verification** (cambia lógica enseñada)
**Applied fix:** Opción (a) del review — write-back al hidratar: `Carro.tsx` agrega un
`useEffect` que, al llegar la hidratación, si `cantidad > stock` llama
`cambiarCantidad(producto_id, stock)`. Con esto la promesa de 03_diseno §2.3.10 y §4.7
("la cantidad guardada se ajusta sola") se hace verdadera sin editar el diseño (el WHAT
queda coherente con el HOW), y el badge del navbar — que lee el store — cuenta las mismas
unidades que filas y total muestran. Prose del paso 4, mini-verificación del paso 8
(editar a 5 → recargar → store/badge corrigen a 2) y bullet de cierre actualizados. El
efecto va antes de los early returns (regla de hooks) y se calma solo (una vez tapado, la
condición no vuelve a disparar).

### WR-04: `mensaje = cuerpo.detail` degrada el detail-array del 422 a "[object Object]"

**Files modified:** `docs/05_desarrollo/guia-06-sesion-frontend.md`
**Commit:** f3cf4d4
**Applied fix:** En el `pedir()` del `lib/api.ts` rehecho por guia-06: normalización
`typeof detalle === "string" ? … : Array.isArray(detalle) && detalle[0]?.msg ?
detalle[0].msg : …` con comentario-lección ("el detail tiene DOS caras"). Ajustados el
prose del paso 4, el comentario de cabecera del archivo y la mini-verificación (la
lectura del `detail` ya no es "la de la guía 4"). Resuelve el WR-04 abierto de la fase 1
en el archivo que esta fase reescribe completo.

### WR-05: Contrato y guia-05 documentaban el 422 del registro con `Error {detail: string}`

**Files modified:** `docs/04_arquitectura/contrato_api.yaml`, `docs/05_desarrollo/guia-05-cuentas-backend.md`
**Commit:** b8db43b
**Applied fix:** Nota de desvío documentado (opción honesta del review, mismo estilo de
lección que G-01-4): la descripción del 422 en el contrato ahora declara que el 422 real
de FastAPI trae `detail` como array de validación y que el contrato lo simplifica como
`Error`; guia-05 agrega el prose equivalente tras el bloque de `auth.py` (con puntero a
que la guía 6 normaliza ese `detail` en el cliente). YAML re-validado con
`yaml.safe_load` (7 paths intactos).

### WR-06: Bloque "agrega" de guia-07 paso 2 re-listaba hooks existentes (redeclaración TS)

**Files modified:** `docs/05_desarrollo/guia-07-carro.md`
**Commit:** 5fe42d9
**Applied fix:** El bloque ahora muestra solo las tres líneas nuevas (`agregar`,
`productoId`, `enCarro`) y el intro dice "DEBAJO de los `useParams`/`useNavigate` que ya
tienes desde la guía 4 (no los copies otra vez: redeclararlos rompe el build)" — la
convención establecida de las demás guías de la fase.

### WR-07: Conteo de paths contradictorio (8 vs 7)

**Files modified:** `docs/05_desarrollo/guia-05-cuentas-backend.md`
**Commit:** e9c2491
**Applied fix:** `guia-05` cierre: "los 8 paths" → "los 7 paths" (calza con el contrato
real — 7, verificado por parse — y con la fila 12 de guia-08). De paso, la mini-verificación
del paso 8 aclara "los 4 paths **nuevos** del contrato 0.2.0" para eliminar la ambigüedad
señalada por el review.

## Skipped Issues

None — all findings were skipped: none. Los 8 findings en scope se fixearon.

---

_Fixed: 2026-09-29T18:16:11Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
