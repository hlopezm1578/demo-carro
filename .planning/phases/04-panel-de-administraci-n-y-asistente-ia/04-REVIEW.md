---
phase: 04-panel-de-administraci-n-y-asistente-ia
reviewed: 2026-09-30T21:30:00Z
depth: standard
files_reviewed: 15
files_reviewed_list:
  - README.md
  - docs/README.md
  - docs/05_desarrollo/README.md
  - docs/02_requerimientos.md
  - docs/03_diseno.md
  - docs/04_arquitectura/contrato_api.yaml
  - docs/04_arquitectura/README.md
  - docs/04_arquitectura/adr/015-panel-admin-protegido-por-rol.md
  - docs/04_arquitectura/adr/016-maquina-de-estados-con-transicion-admin.md
  - docs/04_arquitectura/adr/017-asistente-ia-mini-rag-key-solo-backend.md
  - docs/05_desarrollo/guia-11-pedidos-cierre.md
  - docs/05_desarrollo/guia-12-panel-backend.md
  - docs/05_desarrollo/guia-13-panel-spa.md
  - docs/05_desarrollo/guia-14-asistente-backend.md
  - docs/05_desarrollo/guia-15-asistente-cierre.md
findings:
  critical: 1
  warning: 3
  info: 4
  total: 8
status: issues_found
---

# Phase 4: Code Review Report

**Reviewed:** 2026-09-30T21:30:00Z
**Depth:** standard
**Files Reviewed:** 15
**Status:** issues_found

## Summary

Fase 4 revisada como corpus documental guide-only (D-17): el "código" bajo
revisión son los bloques Python/TSX embebidos en las guías 12-15, el contrato
OpenAPI 0.4.0, los ADRs 015-017 y las extensiones de requerimientos/diseño.
La revisión cruzó cada bloque embebido contra `contrato_api.yaml` 0.4.0,
contra las piezas que las guías 1-11 construyeron (verificadas presentes y
con las firmas asumidas en el workspace runtime `D:/Repos/maura-uat`, hoy en
estado guía-11: `include_router(admin.router, prefix="/api/admin")`,
`por_numero`/`por_id`, `Settings` con las cuatro credenciales, `pedir()` con
su tercer parámetro `sinAuth`, `RequireAuth` por token, ficha con queryKey
`["producto", id]` string, `ProductCard` tipada `ProductoResumen`), contra
`04-RESEARCH.md` (patrones google-genai firmados @ v2.25.0: re-verificados
los citations de `response_json_schema`, `gemini-flash-latest`,
`errors.APIError.code` y el retry 4x del SDK) y contra `04-UI-SPEC.md`
(copys locked de pantallas 10-14: todos presentes verbatim en las guías).

El corpus es sólido en lo estructural: las series RF-19..24 / RNF-08/09 /
RN-14..16 / HU-12/13 continúan sin renumerar, las pantallas 10-14 y DFDs
12.0-15.0 calzan con el código enseñado, los ADRs 015-017 enlazan y heredan
correctamente (011/012/013/014), la cadena 11→12→13→14→15→fase 5 es
grep-verificable, los índices dicen 17 ADRs (contados: 17 archivos) y guías
1-15, y las 20 prohibiciones de los cinco PLANs se respetan (máquina de 4
estados, endpoint público sin bearerAuth, allow-list sin `activo`/`id`,
retirada del demo narrada, key jamás `VITE_`, muralla de ids en el backend,
sin retry casero). Sin embargo hay **un defecto que rompe la guía al
seguirla** — el router admin enseñado monta 4 de sus 7 paths fuera del
contrato — y tres warnings, incluida una mini-verificación que imprime otra
cosa de lo que promete y un campo de entrada sin tope en el endpoint público
de IA.

## Critical Issues

### CR-01: El router admin enseñado monta los paths de PRODUCTOS bajo `/api/admin*` — 4 de 7 operaciones quedan fuera del contrato 0.4.0 y la guía revienta en su propia mini-verificación

**Status:** fixed — commit `9f2411b` (decoradores `/productos`, `/productos/{producto_id}`, `/productos/{producto_id}/activo` + comentario de la regla prefijo+segmento; pedidos/métricas ya montaban bien)
**File:** `docs/05_desarrollo/guia-12-panel-backend.md:835` (y 844-849, 859-866, 881-888, 996-998)
**Issue:** El paso 6 reemplaza `backend/app/routers/admin.py` COMPLETO con
`router = APIRouter(tags=["Administración"])` — SIN prefijo propio — y
decoradores `@router.get("")`, `@router.post("")`, `@router.put("/{producto_id}")`
y `@router.patch("/{producto_id}/activo")`, cuyos docstrings dicen
"GET /api/admin/productos", etc. Pero el registro en `main.py` es el de la
guía 5 y el propio paso 7 ordena NO tocarlo: *"¿Y el `include_router` del
admin? NADA que hacer: existe desde la guía 5 — hoy cambió el CONTENIDO del
router, no su registro"* (línea 996). Ese registro (verificado en el
workspace runtime `maura-uat/backend/app/main.py:36`, construido con las
guías 1-11) es:

```python
app.include_router(admin.router, prefix="/api/admin")
```

Con ese prefijo, los paths finales quedan: `GET/POST /api/admin`,
`PUT /api/admin/{producto_id}`, `PATCH /api/admin/{producto_id}/activo` — y
SOLO los tres de pedidos/métricas (`/api/admin/pedidos`,
`/api/admin/pedidos/{numero}/estado`, `/api/admin/metricas`) caen donde el
contrato 0.4.0 (paths `contrato_api.yaml:804`, `888`, `952`) los declara.
Consecuencias en cadena, todas verificables por el alumno que sigue la guía:

1. La mini-verificación del paso 6 (guia-12:973-976) exige que `/docs`
   liste "GET+POST /api/admin/productos, PUT
   /api/admin/productos/{producto_id}, PATCH
   /api/admin/productos/{producto_id}/activo" — mostrará `/api/admin` y
   `/api/admin/{producto_id}` en su lugar: falla.
2. Los golpes httpx del paso 8 contra `http://localhost:8000/api/admin/productos`
   (guia-12:1069, 1085, 1099) responden 404, no `200 12 True` ni `201`.
3. La pantalla `AdminProductos` de la guía 13 (guia-13:580-604:
   `apiGet("api/admin/productos")`, `apiPut`/`apiPost`/`apiPatch` a
   `api/admin/productos/...`) queda rota de punta a punta — mientras
   AdminPedidos y AdminMetricas sí funcionan, una partición imposible de
   diagnosticar para el alumno.
4. La Gran verificación final fila 12 (guia-15:528) compara "los paths
   NUEVOS (los 7 de administración)" uno a uno contra el contrato: 4 de 7
   cantan desvío.

La app NO revienta al arrancar (paths mal montados son paths válidos), así
que el defecto es silencioso hasta la primera verificación. El UAT runtime
de fase 4 quedó diferido (04-03-SUMMARY: "la verificación runtime del panel
queda para el UAT delegado en maura-uat"; el workspace sigue en 0.3.0 sin
`schemas/admin.py`), y la verificación documental del plan fue grep-only —
por eso no se detectó. Es el mismo patrón que CR-01 de la fase 3: código
enseñado que falla al copiarlo tal cual, en el proyecto donde la
implementación del contrato "sin desviarse" es el producto (D-15/ADR-007).
**Fix:** los paths de productos deben llevar SU segmento en el decorador,
como ya lo hacen `/pedidos` y `/metricas` en el mismo archivo (el prefijo
`/api/admin` heredado del `include_router` se mantiene):

```python
@router.get("/productos", response_model=list[ProductoAdmin], responses={**PROTEGIDO})
@router.post("/productos", ...)
@router.put("/productos/{producto_id}", ...)
@router.patch("/productos/{producto_id}/activo", ...)
```

## Warnings

### WR-01: La mini-verificación del paso 6 de la guía 14 promete `dict_keys([200, 422, 429, 503])` — FastAPI guarda `route.responses` tal cual se pasa y NO incluye el 200: imprime `dict_keys([422, 429, 503])`

**Status:** fixed — commit `630ccb2` (la guía espera `dict_keys([422, 429, 503])` y explica que el 200 vive en el OpenAPI generado; /docs del paso 7 sigue mostrando las cuatro)
**File:** `docs/05_desarrollo/guia-14-asistente-backend.md:565-570`
**Issue:** El comando enseñado es
`print(len(router.routes), router.routes[0].responses.keys())` y el texto
exige "Debe imprimir `1 dict_keys([200, 422, 429, 503])`". Verificado contra
el FastAPI real del proyecto (ejecutado en el venv de `maura-uat`,
fastapi 0.141.x): `APIRoute.__init__` hace `self.responses = responses or {}`
— el dict del decorador, verbatim; el 200 de éxito se agrega recién al
GENERAR el OpenAPI (`app.openapi()`), no en el atributo `responses`. El
alumno que corre la verificación tal cual ve `1 dict_keys([422, 429, 503])`,
sin el 200 prometido, y no tiene cómo saber si su router está mal o la guía.
El endpoint en sí funciona y `/docs` (paso 7) muestra las cuatro responses —
solo la verificación intermedia está mal escrita.
**Fix:** o esperar lo que realmente imprime — "Debe imprimir `1
dict_keys([422, 429, 503])` — las tres que se lanzan a mano (el 200 vive en
el OpenAPI generado, no en el atributo)" — o verificar contra el schema
generado: `print(200 in app.openapi()['paths']['/api/asistente']['post']['responses'])`.

### WR-02: `historial[].texto` viaja SIN tope en un endpoint público — la protección del free tier (RN-16) cubre el mensaje nuevo y el largo del historial, pero no el CONTENIDO de cada entrada: el prompt puede inflarse sin límite

**Status:** fixed — commit `f4f2f0e` (`Field(max_length=500)` en `MensajeHistorial.texto` + `maxLength: 500` en el contrato; prosa de topes y descripción 422 actualizadas en espejo guía↔contrato; mini-verificación ahora imprime `500 500 10 3`)
**File:** `docs/05_desarrollo/guia-14-asistente-backend.md:212` (`texto: str` en `MensajeHistorial`) contra `guia-14:397-404` (`_conversacion` concatena todo) y `docs/04_arquitectura/contrato_api.yaml:566-568`
**Issue:** RN-16 y el contrato venden los topes como lo que "protege el tier
gratuito" validando "en el borde" (mensaje ≤ 500, historial ≤ 10, cards ≤ 3).
Pero `MensajeHistorial.texto` es un `str` sin `max_length` — y el contrato
tampoco declara `maxLength` para ese campo. `POST /api/asistente` es público
(`security: []`, D-59): cualquier visitante puede mandar 10 entradas de
historial de un megabyte cada una; `_conversacion` las concatena TODAS en
`contents` y viajan al modelo. El mensaje NUEVO está tapado (500), pero el
vector de costo real de un endpoint público — el texto que el cliente
controla — queda abierto justamente por el campo más grande. La muralla de
ids (D-56) protege la CORRECCIÓN de la respuesta, no el COSTO del request.
**Fix:** cerrar el tope en el borde, igual que los otros dos:

```python
class MensajeHistorial(BaseModel):
    rol: Literal["clienta", "asesora"]
    texto: str = Field(max_length=500)  # mismo tope que el mensaje nuevo (RN-16)
```

y reflejarlo en el contrato (`ChatMensaje.historial.items.texto.maxLength:
500`) para que guía y fuente de verdad sigan calzando campo a campo.

### WR-03: La mini-verificación del preflight (guia-12 paso 7) no puede fallar — el middleware CORS responde el OPTIONS ANTES del routing, así que da 200 incluso por un path que no existe (exactamente el estado de CR-01)

**Status:** fixed — commit `b284377` (la lección de CORS se mantiene y se complementa con un GET sin token a `/api/admin/productos` esperando `401` — un `404` delataría el path no montado)
**File:** `docs/05_desarrollo/guia-12-panel-backend.md:1034-1039`
**Issue:** El golpe `httpx.request('OPTIONS', '.../api/admin/productos',
headers={Origin, Access-Control-Request-Method: PATCH})` se presenta como
"el preflight que el panel de la guía 13 mandará antes de cada PATCH ya
tiene luz verde". `CORSMiddleware` corta-circuita el preflight con 200 para
cualquier path cuando origen y método están en las listas — el path jamás
llega al router. Es decir: esta verificación habría respondido 200 también
con los paths de productos sin registrar (el estado real de CR-01), dando
luz verde falsa a la pieza exacta que estaba rota. Como lección de CORS
está bien; como verificación del paso es un check que no puede fallar.
**Fix:** complementarla con un golpe que SÍ pruebe el registro de la ruta,
p. ej. `GET /api/admin/productos` SIN token esperando **401** (un 404
delataría un path no montado — y habría atrapado CR-01 en el propio paso 7).

## Info

### IN-01: El "espejo honesto del 422" del editor cubre 5 de los 7 campos requeridos — `descripcion` e `imagen` pueden disparar un 422 sin copys de campo, y el caso más probable es el flujo de producto INACTIVO que la propia guía enseña

**Status:** open — deferido al usuario: decisión editorial/narrativa (agregar dos copys cambia los "copys locked" del UI-SPEC o suavizar la narrativa), fuera del alcance de esta corrida de fixes
**File:** `docs/05_desarrollo/guia-13-panel-spa.md:558-570` (`validar`) contra `613-643` (`abrirEditor`) y `guia-12:120-126` (backend `min_length=1`)
**Issue:** El backend exige `descripcion` e `imagen` no vacías
(`Field(min_length=1)`), pero `validar()` solo revisa nombre, precio, stock,
familia y notas (los 5 copys locked del UI-SPEC:536/186 — spec y guía
calzan entre sí). El hueco tiene un disparador documentado: al editar un
producto inactivo, `abrirEditor` hidrata `descripcion: ""` (la ficha pública
404a) — si la dueña corrige las notas (que SÍ tienen espejo) y guarda, el
422 de `descripcion` llega al banner genérico "No pudimos guardar el
producto. Revisa los datos…" sin indicar el campo, aunque ya hizo todo lo
que el formulario le pidió. Funciona (degrada al banner spec-eado), pero la
afirmación "el espejo HONESTO del 422: los CINCO copys" promete una cobertura
que el schema de 7 campos desmiente.
**Fix:** agregar los dos espejos (`errores.descripcion = "Escribe una
descripción."` / `errores.imagen = "Escribe la ruta de la foto."`), o suavizar
la narrativa a "los cinco copys de los campos que el usuario escribe mal con
más frecuencia; descripción e imagen caen al banner genérico".

### IN-02: El guard de degradación compara contra `None`, pero la plantilla versionada modela el estado VACÍO — con `GEMINI_API_KEY=` en el `.env` la "degradación temprana, sin tocar la red" no aplica

**Status:** fixed — commit `f4f57ba` (`if not settings.gemini_api_key:` cubre `None` y `""`; comentario enseña los dos estados)
**File:** `docs/05_desarrollo/guia-14-asistente-backend.md:420` contra `104` y `110-112`
**Issue:** `.env.example` enseña la línea `GEMINI_API_KEY=` con valor vacío.
pydantic-settings carga un string vacío (`""`), no `None`, así que un alumno
que copió la plantilla y no llenó su key no pasa por el `if
settings.gemini_api_key is None` temprano: construye el client con key vacía
y la primera llamada es la que degrada (via `except` → 503). El resultado
observable es el correcto (503 amable, tienda operativa), pero la promesa
narrada ("la señal sale TEMPRANO, sin tocar la red", y la mini-verificación
del paso 3 que presume key ausente vs. presente) no cubre el estado que la
propia plantilla produce.
**Fix:** `if not settings.gemini_api_key:` — cubre `None` y `""` con la
misma línea, sin cambiar nada más.

### IN-03: ADR-017 dice que el SDK "toma `GEMINI_API_KEY` automáticamente" justo donde la guía 14 enseña a NO confiar en ese auto-pickup

**Status:** open — deferido al usuario: decisión editorial sobre la redacción de la cláusula en el ADR, fuera del alcance de esta corrida de fixes
**File:** `docs/04_arquitectura/adr/017-asistente-ia-mini-rag-key-solo-backend.md:113-114` contra `docs/05_desarrollo/guia-14-asistente-backend.md:281-287, 361-368`
**Issue:** La sección "Evidencia firmada" del ADR cita "la env var
GEMINI_API_KEY tomada automáticamente por el `genai.Client`" como rasgo del
SDK, mientras la guía dedica un gotcha completo a pasar `api_key=
settings.gemini_api_key` EXPLÍCITA porque pydantic-settings lee el `.env`
hacia el objeto Settings, no hacia el entorno del proceso. No son
contradictorias (capacidad del SDK vs. decisión del proyecto), pero son los
dos documentos que el alumno tendrá abiertos en pestañas simultáneas (la
propia guía lo manda: "Abre el contrato y el ADR-017 en pestañas").
**Fix:** una cláusula en el ADR cerrando la lectura: "(capacidad del SDK;
el proyecto pasa la key explícita desde `Settings` — ver el gotcha de la
guía 14)".

### IN-04: `Metricas.top_5` no declara el `maxItems: 5` que el contrato promete — el tope vive solo en el `.limit(5)` del SQL

**Status:** fixed — commit `2f152e2` (`top_5: list[TopAroma] = Field(max_length=5)` — espejo declarativo del `maxItems: 5`)
**File:** `docs/05_desarrollo/guia-12-panel-backend.md:214` (schema `top_5: list[TopAroma]`) contra `docs/04_arquitectura/contrato_api.yaml:516-519` (`maxItems: 5`) y `guia-12:564` (`.limit(5)`)
**Issue:** El contrato declara `top_5` con `maxItems: 5`; el schema Pydantic
de respuesta no reproduce el tope (`list[TopAroma]` sin `max_length`). Hoy
no desvía nunca (el `.limit(5)` de la consulta lo garantiza), pero en un
proyecto API-first el schema de respuesta es el espejo del contrato: si
mañana alguien toca el SQL, el contrato se incumple en silencio y la fila
contrato ↔ `/docs` no puede detectarlo.
**Fix:** `top_5: list[TopAroma] = Field(max_length=5)` — la misma técnica
que `ChatRespuesta.productos` usa en la guía 14 para su `maxItems: 3`.

---

_Reseña complementaria de verificaciones sin hallazgos:_ los 8 paths nuevos
del contrato 0.4.0 calzan schema a schema con las guías
(`ProductoCrear/ProductoEditar` de 7 campos required sin `id`/`activo`,
`PedidoTransicion` enum de un valor, `PedidoAdmin` con `email_clienta`,
`Metricas` con los 4 KPI, `ChatMensaje` 500/10 y `ChatRespuesta` con
`max_length=3`, 409 con el copy locked "Ese pedido ya no está en curso.",
503/429 con sus examples amables y `/api/asistente` con `security: []`);
`get_current_admin` está en las SIETE firmas del router admin con el dict
`PROTEGIDO` heredado; la transición es UPDATE condicional con rowcount →
`TransicionIlegal` → 409 y no toca stock (D-35/D-50); las métricas usan
`COALESCE`, los 4 estados siempre y el top 5 desde `nombre_snapshot` con
`limit(5)`; el sku del panel se genera `panel-{uuid8}` (14 < 20 chars); los
métodos y atributos que las guías asumen existen con esas firmas en el
runtime (`por_numero`, `por_id`, `Settings.admin_email` & co., `pedir()`
con `sinAuth`, queryKey de ficha `["producto", id]` string — el `String(id)`
de la burbuja calza con la caché de la guía 7, `ProductCard` acepta
`ProductoDetalle` por ser `ProductoResumen` extendido, `Layout.tsx`
reemplazado es idéntico al existente + burbuja); el texto del modelo se
renderiza como TEXTO (`{m.texto}`) sin `dangerouslySetInnerHTML` en todo el
corpus; la key vive solo en backend (`str | None`, client lazy, plantilla
vacía, fila 13 del grep del build); las series RF-19..24 / RNF-08/09 (filas
de tabla) / RN-14..16 (bullets) / HU-12/13 (headings Dado/Cuando/Entonces)
y las filas P7/P8 de trazabilidad resuelven sin renumerar; pantallas 10-14
y DFDs 12.0-15.0 calzan con los copys locked del UI-SPEC (los 5 copys del
editor, el 409, "No tienes acceso al panel", "Pregúntale a Maura", la
bienvenida y los tres estados del chat); guia-11 cambió SOLO su bloque
"Siguiente" (6/6 líneas, diff verificado); ADRs 015-017 con formato
demo-cine, opciones/consecuencias honestas y enlaces relativos correctos;
los READMEs dicen 17 ADRs (17 archivos contados) y guías 1-15 con la fila 5
en Parcial; las prohibiciones de los 5 PLANs se respetan en su totalidad; y
el "Gran verificación final" de guia-15 mantiene el formato de tabla
numerada CS/Origen de guia-11, sumando la fila fija del grep del build.

_Reviewed: 2026-09-30T21:30:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
