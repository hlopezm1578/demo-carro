---
phase: 03-checkout-webpay-y-rdenes
reviewed: 2026-09-30T16:53:10Z
depth: standard
files_reviewed: 12
files_reviewed_list:
  - docs/02_requerimientos.md
  - docs/03_diseno.md
  - docs/04_arquitectura/README.md
  - docs/04_arquitectura/adr/012-retorno-de-webpay.md
  - docs/04_arquitectura/adr/013-orden-nace-al-pagar-stock-al-aprobar.md
  - docs/04_arquitectura/adr/014-snapshot-de-precio-en-la-orden.md
  - docs/04_arquitectura/contrato_api.yaml
  - docs/05_desarrollo/README.md
  - docs/05_desarrollo/guia-09-ordenes-webpay.md
  - docs/05_desarrollo/guia-10-retorno-voucher.md
  - docs/05_desarrollo/guia-11-pedidos-cierre.md
  - docs/README.md
findings:
  critical: 1
  warning: 5
  info: 6
  total: 12
status: issues_found
---

# Phase 3: Code Review Report

**Reviewed:** 2026-09-30T16:53:10Z
**Depth:** standard
**Files Reviewed:** 12
**Status:** issues_found

## Summary

Fase 3 revisada como corpus documental guide-only (D-17): el "código" bajo revisión son
los bloques Python/TSX embebidos en las guías 09-11, el contrato OpenAPI 0.3.0, los ADRs
012-014 y las extensiones de requerimientos/diseño. La revisión cruzó cada bloque embebido
contra `contrato_api.yaml` 0.3.0, contra la evidencia runtime de `03-SPIKE-RETORNO.md` y
contra las piezas que las guías 1-8 construyeron (settings, `lib/api.ts`, stores, Navbar,
`RequireAuth`, proxy Vite — todas verificadas presentes y con las firmas asumidas).

La arquitectura general del pago es sólida y consistente con la evidencia del spike:
discriminador por presencia de params (orden del plugin oficial), 302 explícito, commit solo
en la rama `token_ws`-solo, criterio doble `response_code == 0 && status == AUTHORIZED`,
UPDATE condicional con rowcount para el stock, snapshot en las líneas, 404 uniforme de
ownership, y el contrato 0.3.0 calza campo a campo con los schemas de la guía 9. Sin embargo,
hay **un defecto que rompe la guía al seguirla** (un `ImportError` en `routers/retorno.py`
tal como se enseña a copiar), y cinco warnings: una violación verificable de la propia regla
de aislamiento del SDK, un `return_url` construido desde el origen de la SPA, un guard de
idempotencia implementado con el patrón read-check-write que la propia guía condena, una
narrativa factualmente incorrecta sobre el F5 del voucher, y una divergencia diseño ↔ modelo
(columna `fecha` no declarada en el diccionario de datos).

## Critical Issues

### CR-01: `routers/retorno.py` importa `Error` desde un módulo que no lo define — ImportError al copiar la guía tal cual

**File:** `docs/05_desarrollo/guia-09-ordenes-webpay.md:929`
**Issue:** El bloque de `backend/app/routers/retorno.py` enseña:

```python
from app.schemas.pedido import Error
```

pero `schemas/pedido.py` (creado en el paso 3 de la misma guía, líneas 212-275) define
únicamente `CheckoutItem`, `CheckoutCreate`, `CheckoutRespuesta`, `OrdenLinea`, `OrdenLista`
y `OrdenDetalle` — no define ni re-exporta `Error`. El schema `Error` vive en
`app/schemas/producto` desde la guía 4, y los otros dos routers de la MISMA guía lo importan
correctamente (`from app.schemas.producto import Error` en `routers/checkout.py:873` y
`routers/pedidos.py:1018`, con el comentario explícito "el cuerpo de error vive en
schemas/producto desde la guía 4"). Verificado con grep: no existe ningún paso posterior de
las guías 9-11 que agregue `Error` a `schemas/pedido.py`.

Consecuencia para el alumno: al copiar el bloque tal cual, `from app.routers import
checkout, pedidos, retorno` (la mini-verificación del propio paso 8) falla con
`ImportError: cannot import name 'Error' from 'app.schemas.pedido'`, el `include_router`
del paso 9 revienta y la API no arranca — la guía queda bloqueada en su propio paso 8.
**Fix:**

```python
# en routers/retorno.py — igual que checkout.py y pedidos.py en la misma guía
from app.schemas.producto import Error  # el cuerpo de error vive en schemas/producto desde la guía 4
```

## Warnings

### WR-01: `services/pedidos.py` importa `transbank` — viola la regla "único archivo que importa transbank" que la guía enseña y verifica

**File:** `docs/05_desarrollo/guia-09-ordenes-webpay.md:562`
**Issue:** El paso 5 establece la regla de arquitectura ("ESTE [services/webpay.py] es el
único archivo del proyecto que escribe `import transbank`") y su mini-verificación exige
"`grep -r transbank backend/app` debe listar SOLO `services/webpay.py`". Pero el bloque de
`services/pedidos.py` del paso 6 incluye:

```python
from transbank.error.transaction_commit_error import TransactionCommitError
```

Al completar la guía, ese grep lista DOS archivos (`services/webpay.py` y
`services/pedidos.py`): la verificación enseñada deja de pasar y el aislamiento del SDK que
la regla proclama queda roto por el propio código del curso (un tipo de excepción del SDK
fugado a la capa de servicios).
**Fix:** atrapar la excepción tipada DENTRO del wrapper y exponer una señal de dominio:

```python
# services/webpay.py
def commit(token_ws: str) -> dict | None:
    """Confirma la transacción. None si Webpay no puede confirmar el token."""
    try:
        return tx.commit(token_ws)
    except TransactionCommitError:
        return None

# services/pedidos.py::_confirmar
commit = webpay.commit(token_ws)
if commit is None:
    return RetornoResultado(estado="error", numero=None)
```

### WR-02: `return_url` construido desde `settings.cors_origins[0]` (origen de la SPA) — semánticamente es una URL del backend y solo funciona por el proxy de Vite

**File:** `docs/05_desarrollo/guia-09-ordenes-webpay.md:622`
**Issue:** `iniciar_checkout` usa
`return_url=f"{settings.cors_origins[0]}/api/pago/retorno"`. `cors_origins[0]` es
`http://localhost:5173` (el origen de la SPA, verificado en guía 1/guía 5), así que el
retorno de Webpay apunta a la SPA + un path del backend: en dev funciona únicamente porque
el proxy `/api` de Vite (guía 2, `proxy: { "/api": "http://localhost:8000" }`) reenvía la
navegación. Dos problemas: (a) el `return_url` es por definición la URL pública del
BACKEND, no de la SPA — el research (Pattern 1) y el spike (`return_url` al propio backend,
puerto 8901) lo modelan así; (b) en el despliegue de la fase 5 (SPA estática en
Vercel/Netlify/Cloudflare, sin proxy) esta construcción rompe el retorno completo, y
reutilizar una lista de orígenes CORS como fuente de la URL base acopla dos conceptos
distintos (si mañana hay más orígenes en la lista, `[0]` deja de ser "la" URL). El
`_hacia_spa` del 302 SÍ usa correctamente `cors_origins[0]` (esa es la SPA de verdad); la
asimetría return_url-backend vs redirect-SPA se pierde al usar el mismo origen para ambos.
**Fix:** settings propia y explícita para la base del backend
(p. ej. `backend_url: str = "http://localhost:8000"`) y
`return_url=f"{settings.backend_url}/api/pago/retorno"`, narrando que la fase 5 la
congela junto con el origen público de la SPA.

### WR-03: El guard de idempotencia ya-PAID (y el de `_cancelar`) es read-check-write en Python — la ventana de carrera que la propia guía enseña a evitar

**File:** `docs/05_desarrollo/guia-09-ordenes-webpay.md:787-812`
**Issue:** `_confirmar` implementa el guard de PAY-03 como: leer `pedido.estado`, comparar
en Python, y solo entonces ejecutar descuento + transición. Bajo dos retornos CONCURRENTES
del mismo `token_ws` (dos tabs, retry del navegador en vuelo — el spike documentó que el
navegador repite retornos), ambos threads leen `pending`, ambos pasan el guard, y el
segundo UPDATE condicional de stock puede volver a encontrar stock suficiente: **doble
descuento y doble transición**, exactamente la clase de defecto que RN-12/ORDR-02 prohíben
y que Pitfall 5 de la propia guía describe ("el check y el write son dos operaciones; entre
ellas vive la carrera"). La muralla del stock (UPDATE condicional) protege el oversell
frente a órdenes distintas, pero no el doble efecto sobre el MISMO pedido, porque la
decisión de proceder vive en Python. Para duplicados secuenciales (los observados por el
spike) el guard funciona; la promesa "refrescar no paga dos veces" queda sin garantía bajo
concurrencia real. Mismo patrón en `_cancelar` (guard `estado == pending` leído en Python).
**Fix:** la misma muralla que el stock — transición condicional con rowcount:

```python
resultado = self.db.execute(
    update(Pedido)
    .where(Pedido.id == pedido.id, Pedido.estado == EstadoPedido.pending)
    .values(estado=EstadoPedido.paid)
)
if resultado.rowcount == 0:   # otro retorno ya decidió esta orden
    return RetornoResultado(estado="pagado", numero=pedido.numero)
self.pedidos.descontar_stock_atomico(pedido.lineas)  # dentro de la misma transacción
```

### WR-04: La narrativa del F5 es factualmente incorrecta — el F5 sobre `/pago/resultado` NO repite el retorno del backend

**File:** `docs/05_desarrollo/guia-10-retorno-voucher.md:692-696` y `docs/05_desarrollo/guia-11-pedidos-cierre.md:482`
**Issue:** La mini-verificación F5 de la guía 10 dice: "Detrás, el navegador repitió el
retorno y el guard ya-PAID del backend re-muestra la orden sin tocar el stock ni la
transición (PAY-03)", y la fila 7 de la Gran verificación final repite el mecanismo. Es
falso: al presionar F5 sobre `/pago/resultado?estado=…&orden=…` el navegador vuelve a hacer
GET de la ruta de la SPA (index.html) y la pantalla re-fetcha `GET /api/pedidos/{numero}` —
una lectura sin side effects. El endpoint `/api/pago/retorno` del backend NO se re-ejecuta
con F5 de la SPA (solo se re-ejecutaría re-navegando al `return_url` del backend, p. ej.
back/forward o un retry en vuelo del POST/GET de Webpay). El resultado verificado ("no se
paga dos veces") es correcto, pero el mecanismo atribuido es el equivocado — y en una guía
donde el mecanismo ES el contenido, el alumno aprende que F5 pasa por el retorno cuando no
es así.
**Fix:** corregir ambas narrativas: "el F5 re-fetcha el pedido (lectura sin efectos); el
guard ya-PAID entra en juego cuando es la NAVEGACIÓN al return_url del backend la que se
repite (back/forward, retries del navegador — el spike observó 7 repeticiones de un mismo
retorno)".

### WR-05: El diccionario de datos de PEDIDO (diseño §2.2) no declara `fecha`, pero la guía 9 agrega la columna y afirma coincidencia "campo a campo... ni una más"

**File:** `docs/03_diseno.md:111-119` (tabla PEDIDO) contra `docs/05_desarrollo/guia-09-ordenes-webpay.md:162-165`
**Issue:** La guía 9 (paso 2) dice: "La tabla contra el diccionario de §2.2 del diseño,
campo a campo: PEDIDO (`id`, `numero` único de 26, `estado` de 4 valores, `total` entero,
`fecha`, `usuario_id` FK) ... — ni una más". El diccionario real de §2.2 lista solo id,
numero, estado, total y usuario_id — sin `fecha` (verificado por grep: las únicas
apariciones de "fecha" en 03_diseno son el DFD 11.0 y la pantalla 8). El contrato 0.3.0
(`OrdenLista.fecha`, required) y el modelo de la guía sí la incluyen: el documento de diseño
quedó corto y la guía afirma una coincidencia que no existe, en un proyecto donde la
trazabilidad doc ↔ código es el producto.
**Fix:** agregar la fila al diccionario de §2.2 (p. ej. `fecha | Fecha-hora | — | Sí |
Momento en que la orden nace al iniciar el pago (D-34); viaja en OrdenLista del contrato`)
o, si no se toca el diseño, corregir la afirmación de la guía para reconocer la adición.

## Info

### IN-01: Typo en HU-09/HU-10 — "se descuento stock una segunda vez"

**File:** `docs/02_requerimientos.md:250`
**Issue:** El tercer criterio de HU-10 dice "sin que se me cobre ni se descuento stock una
segunda vez" — debe ser "se descuente".
**Fix:** Corregir la conjugación.

### IN-02: El título de `ResultadoPago` no cubre el estado `cancelled` del pedido fetcheado

**File:** `docs/05_desarrollo/guia-10-retorno-voucher.md:549-554`
**Issue:** `titulo` decide entre `paid` ("¡Gracias por tu compra!"), `pending` ("Tu pago
está en curso") y el resto ("Tu pago fue rechazado"). Una orden `cancelled` renderizada por
la rama con fetch (p. ej. link viejo del voucher de una orden luego anulada, o el caso
admin de fase 4) mostraría el título "Tu pago fue rechazado" junto al badge "Anulado" del
voucher — título y badge se contradicen.
**Fix:** agregar la rama `cancelled` al título (p. ej. "Tu compra quedó anulada").

### IN-03: Contrato declara `requestBody.required: true` en POST /api/pago/retorno, pero la implementación enseñada acepta body ausente

**File:** `docs/04_arquitectura/contrato_api.yaml:661-663` contra `docs/05_desarrollo/guia-09-ordenes-webpay.md:991-1000`
**Issue:** Todos los `Form(default=None)` hacen que FastAPI acepte un POST sin body
(clasifica "desconocido" → 400), mientras el contrato marca el requestBody como requerido.
Divergencia detectable en la comparación uno a uno de la fila 12 de la Gran verificación
final, en un proyecto que exige implementar el contrato "sin desviarse" (D-15/ADR-007).
**Fix:** quitar `required: true` del requestBody en el contrato (los cuatro params son
opcionales por diseño — el flujo se discrimina por presencia).

### IN-04: El 400 de `/api/checkout` por "aroma no disponible/inexistente" no está documentado en el contrato

**File:** `docs/04_arquitectura/contrato_api.yaml:565-572` contra `docs/05_desarrollo/guia-09-ordenes-webpay.md:596-597`
**Issue:** `iniciar_checkout` responde 400 "Un aroma de tu carro ya no está disponible"
cuando el producto no existe o está inactivo, pero la descripción del 400 en el contrato
cubre solo "Stock insuficiente para alguna línea" (el router de la guía sí menciona ambos
casos en su `responses`). Caso de borde del contrato incompleto en un proyecto API-first.
**Fix:** extender la descripción del 400 del contrato: "Stock insuficiente o aroma ya no
disponible — regla de negocio (CART-03); la orden no se crea".

### IN-05: Wireframe de la pantalla 9 muestra "Carro (0)", contradiciendo la regla "contador oculto en cero" de la pantalla 6

**File:** `docs/03_diseno.md:915` contra `docs/03_diseno.md:792-794`
**Issue:** §4.7 fija que el contador del navbar son "unidades totales, oculto en cero";
el wireframe de Mis pedidos dibuja `Carro (0)` visible.
**Fix:** dibujar `Carro` sin contador en el wireframe de la pantalla 9.

### IN-06: Una falla de red durante `webpay.commit` escapa como 500 al navegador — la promesa "jamás un 500" solo cubre `TransactionCommitError`

**File:** `docs/05_desarrollo/guia-09-ordenes-webpay.md:773-780`
**Issue:** `_confirmar` solo atrapa `TransactionCommitError`. Un timeout o conexión rota
hacia `webpay3gint.transbank.cl` durante el commit (`requests.ConnectionError` /
`requests.Timeout`, no tipadas por el SDK como commit error) sube sin atrapar y el navegador
ve un 500 crudo — el escenario que ADR-012/narrativa prometen que jamás ocurre. Es una
ventana pequeña (el navegador acaba de llegar DESDE Webpay), pero el endpoint es público y
la promesa es absoluta.
**Fix:** ampliar el `except` en el wrapper de `services/webpay.py` (junto al fix de WR-01)
a `transbank.error.TransbankError` + errores de red de `requests`, devolviendo la misma
señal de dominio → 302 con `estado=error`.

---

_Reseña complementaria de verificaciones sin hallazgos:_ los 11 paths del contrato calzan
con los 4 nuevos de las guías (paths, tags, `security` del retorno, 302 con `Location`,
enum `[pending, paid, cancelled, rejected]` minúsculas nombre==valor, `CheckoutCreate` sin
campo precio, `required` de `CheckoutRespuesta`/`OrdenLista` campo a campo); el
discriminador de `clasificar_flujo` reproduce el orden del plugin oficial y sus cinco
combinaciones de la mini-verificación son correctas contra la evidencia del spike
(incluido el anulado por GET); el commit vive solo en la rama `token_ws`-solo; el
`RedirectResponse(url, status_code=302)` explícito está en ambos métodos con `responses`
declarados; `descontar_stock_atomico` lleva la condición dentro del SQL con
`synchronize_session=False`; las series RF-12..18 / RNF-07 / RN-10..13 / HU-09..11 y la fila
P6 de trazabilidad resuelven; ADRs 012-014 enlazan correctamente (incluida la ruta relativa
al spike en `.planning/`); el índice de guías 9-11, "14 ADRs" y el rollup de `docs/README.md`
son consistentes; y las piezas asumidas de fases 1-2 (`settings` de cuentas,
`ApiError.status`, `apiPost`, `vaciar`/`maura-carro`, Navbar `usuario`/`estiloLink`,
`RequireAuth`+`from.pathname`, proxy `/api`) existen con las firmas que las guías nuevas
asumen.

_Reviewed: 2026-09-30T16:53:10Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
