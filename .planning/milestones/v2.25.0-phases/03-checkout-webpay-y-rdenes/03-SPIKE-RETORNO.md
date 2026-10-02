---
status: complete
phase: 03-checkout-webpay-y-rdenes
source: [03-RESEARCH.md]
started: 2026-09-30T14:24:18Z
updated: 2026-09-30T15:32:00Z
verified_by: agent (user-delegated per AGENTS.md — taller D:/Repos/maura-uat)
---

# Spike de retorno de Webpay Plus — hallazgos runtime

Corrida runtime contra el ambiente de integración real de Transbank
(`webpay3gint.transbank.cl`, credenciales públicas del SDK: comercio
`597055555532`, sin registro) desde el taller `D:/Repos/maura-uat/spike-retorno/`.
El código del spike es desechable por diseño (D-38): vive SOLO en maura-uat y su
único producto duradero es este documento (D-17/D-40).

## Cómo se corrió (para reproducir)

- **Mini-backend**: FastAPI + `transbank-sdk` 6.1.0 (Python 3.12.10, uv 0.9.3),
  dos endpoints: `POST /iniciar` que llama
  `Transaction.build_for_integration(IntegrationCommerceCodes.WEBPAY_PLUS, IntegrationApiKeys.WEBPAY).create(buy_order, session_id, amount, return_url)`
  con `buy_order` corto único por corrida (`SPK-XXXXXXXX`, 11 chars) y
  `return_url` apuntando al propio spike (`http://127.0.0.1:8901/retorno`), y
  responde el HTML mínimo con form auto-submit (`input token_ws`, action la url
  devuelta); y `/retorno` declarado GET **y** POST que registra por request el
  método, todos los params presentes y timestamp en un log JSONL append-only.
  En el flujo normal llama `tx.commit(token_ws)`; en los no-normales NO llama
  commit (Pitfall 3). Cada request queda en `eventos.jsonl` — la observación ES
  el producto.
- **Navegador real**: Edge headless dirigido por CDP (eventos reales de teclado y
  mouse; los forms Angular del checkout exigieron native-setter + eventos
  input/change por campo — detalle operativo, no hallazgo del dominio).
- **Tarjeta de éxito oficial**: VISA `4051 8856 0044 6623`, CVV `123`,
  vencimiento cualquiera futuro (se usó 12/28), 3DS del simulador bancario:
  RUT `11.111.111-1` (CON puntos — ver hallazgo 6 del cierre) + clave `123`.
- **Tokens TRUNCADOS**: toda la evidencia de este documento registra prefijo +
  largo (`01abd2…(len=64)`), jamás el token completo (T-03-01). El extracto del
  commit omite `card_detail`.

## Tests (flujos corroborados runtime)

### 1. Flujo normal APROBADO — qué llega y por dónde

expected: Según las docs oficiales + Pattern 3 del research: desde API 1.1 el
retorno del flujo normal llega **por GET** con SOLO `token_ws` en query; el
commit de ese token debe devolver `response_code == 0` y `status == AUTHORIZED`
(criterio literal de PAY-03). El plugin oficial discrimina "normal" por
presencia exclusiva de `token_ws`.

result: pass

evidence: |
  Orden SPK-E871B543 ($1.990), corrida 2026-09-30 14:49–14:50 UTC:
  - create 14:49:29 → form hosted cargado; pago con VISA oficial + 3DS TSY.
  - Retorno recibido 14:50:30:
      metodo=GET
      token_ws=01abd2…(len=64)
      TBK_TOKEN=null  TBK_ID_SESION=null  TBK_ORDEN_COMPRA=null
  - Commit (llamado por el spike al recibir el retorno):
      response_code=0  status=AUTHORIZED  authorization_code=1213
      vci=TSY  payment_type_code=VN  amount=1990
      buy_order=SPK-E871B543  session_id=ses-c34572dd
      transaction_date=2026-09-30T14:49:29.848Z  card_detail=(omitido)
  - Duración total create→retorno: 61.6 s (el grueso es la interacción guiada
    del formulario hosted: tarjeta → exp/cvv → Pagar → 3DS banco → elección).
  - El navegador llega a /retorno?token_ws=… por GET: coincide con Pattern 3.

### 2. Flujo ANULADO por la clienta — qué llega y por dónde

expected: Según las docs oficiales citadas en Pattern 3: el anulado redirige con
`TBK_TOKEN` + `TBK_ORDEN_COMPRA` + `TBK_ID_SESION` (SIN `token_ws`) —
corrección ya registrada en research vs la hipótesis original de D-39. Las docs
además dicen: "para el entorno de integración, este redireccionamiento es
realizado con el método POST". El plugin oficial NO llama commit en este flujo.

result: pass — con CORRECCIÓN MATERIAL: en integración el anulado llegó por
**GET**, no por POST (la cita de las docs no calza con el comportamiento real
observado; exactamente la ambigüedad que el endpoint GET+POST inmuniza, Pitfall 2).

evidence: |
  Orden SPK-E8F80C75, corrida 2026-09-30 14:51 UTC (botón "Anular compra y
  volver" del propio formulario hosted, tras ingresar el número de tarjeta):
  - Retorno recibido 14:51:06 (6.8 s después del create):
      metodo=GET
      token_ws=null
      TBK_TOKEN=01abde…(len=64)
      TBK_ID_SESION=ses-3c…(len=12)
      TBK_ORDEN_COMPRA=SPK-E8F80C75
  - El spike clasificó flujo=anulado por presencia de params (TBK_ID_SESION +
    TBK_TOKEN sin token_ws) y NO llamó commit (no_commit, Pitfall 3).
  - Consulta status(TBK_TOKEN) posterior: status=INITIALIZED — la transacción
    anulada queda abierta en Webpay (jamás autorizada); el descuento de stock
    de la fase real jamás ocurre por esta vía.

### 3. Flujo TIMEOUT del formulario — qué llega, por dónde y cuánto tarda

expected: Según Pattern 3: `TBK_ID_SESION` + `TBK_ORDEN_COMPRA` SIN ningún
token; método NO declarado explícitamente por las docs (Pitfall 2). Reloj
documentado: "4 minutos en producción y de 10 minutos en integración" (Pitfall 9).

result: pass — corroborado runtime con cronómetro, con DOS hallazgos que
las docs no dicen (ver evidence): (a) el retorno del timeout NO está
garantizado — depende de la página del form (SPA) detectando la sesión muerta;
(b) cuando sí llega, es por GET.

evidence: |
  Tres observaciones independientes (2026-09-30, todas UTC):
  (a) Espontánea (form abandonado por una sesión previa del spike, con
      interacción inicial): orden SPK-E6515F01, create 14:19:08, form abierto
      ~14:19:10 → PRIMER retorno timeout 14:25:45 ≈ 6 min 35 s desde la
      apertura del form:
        metodo=GET
        token_ws=null  TBK_TOKEN=null
        TBK_ID_SESION=ses-74…(len=12)
        TBK_ORDEN_COMPRA=SPK-E6515F01
      El navegador REPITIÓ el retorno 7 veces entre 14:25:45 y 14:28:34
      (recargas del mismo tab) — el backend debe tolerar retornos duplicados.
  (b) Controlada A — form abandonado SIN ninguna interacción, tab en segundo
      plano (orden SPK-5CAF879B, form cargado 14:54:04): SIN retorno en
      780 s (13 min completos de espera activa). La página del formulario
      nunca redirigió: el "timeout de 10 minutos" de las docs NO es un
      redirect garantizado del servidor — si la clienta se fue sin interactuar
      (o el tab quedó dormido), el retorno del timeout PUEDE NO LLEGAR NUNCA.
      La orden queda huérfana PENDING: exactamente el escenario que D-48/D-49
      ya cubren con estados honestos y gestión admin en fase 4.
  (c) Controlada B — form abandonado TRAS interacción inicial (clic en el
      medio de pago) y tab activo (orden SPK-111B70EF, create 15:09:19, form
      cargado 15:09:22): retorno timeout a los **603 s (10 min 3 s)** desde la
      carga del form — el reloj documentado de "10 minutos en integración"
      calza casi al segundo:
        15:19:24  metodo=GET
        token_ws=null  TBK_TOKEN=null
        TBK_ID_SESION=ses-75…(len=12)
        TBK_ORDEN_COMPRA=SPK-111B70EF
  Conclusión del reloj (Q3): el timeout cronometrado REAL es ~10 min desde la
  carga del formulario (603 s medidos), PERO el redirect depende de la página
  del form viva para dispararlo — un tab dormido en background puede no
  redirigir nunca (observación b). La guía enseña al alumno a esperar ~10 min
  activos y el dominio tolera que el retorno del timeout NO llegue.
  NOTA común: cuando el retorno del timeout llega, SIEMPRE llegó por GET con
  TBK_ID_SESION + TBK_ORDEN_COMPRA (sin token) — 20 retornos observados.

### 4. Cuarto flujo — ERROR DE FORMULARIO (documentado, no replicable runtime en integración)

expected: Según las docs oficiales (Pattern 3 del research): ocurre cuando la
clienta abre el formulario, cierra el tab y luego lo RECUPERA — la cita oficial
es que es "**replicable solo en producción**". El retorno trae los 4 params
JUNTOS: `token_ws` + `TBK_TOKEN` + `TBK_ID_SESION` + `TBK_ORDEN_COMPRA` (token
doble = el form fue submiteado dos veces). El discriminador del plugin oficial
lo clasifica en su PRIMERA rama (`token_ws && TBK_TOKEN` → WEBPAY_ERROR_FLOW /
`DoubleTokenWebpayException`) y NO commitea.

result: documented — el spike no depende de dispararlo runtime (A3 del
research): PAY-02 queda íntegro porque el discriminador por presencia de params
lo maneja sin corrida. Se intentó replicarlo en integración igual (ver
evidence) y produjo un error previo, no el retorno.

evidence: |
  Intento runtime de replicación (2026-09-30 14:55 UTC, orden SPK-95FE5530):
  receta oficial aplicada — form abierto con token T1 (tab A), tab A CERRADO,
  re-POST del MISMO token T1 al formulario (tab B, la "recuperación"). El
  re-ingreso NO reabrió el form: el navegador quedó en
  webpay3gint.transbank.cl/webpayserver/init_transaction.cgi con
  "Tu transacción no se pudo llevar a cabo. Ten en cuenta que ningún cargo fue
  realizado en tu tarjeta (Error 21)". Conclusión: en integración el token ya
  inicializado rechaza el segundo ingreso al form (Error 21) ANTES de poder
  producir el retorno de token doble — corrobora empíricamente la cita
  "replicable solo en producción". La rama del plugin oficial (token_ws+
  TBK_TOKEN juntos → error de formulario sin commit) queda como fuente
  documental: [CITED: docs oficiales Webpay Plus + CommitWebpayController del
  plugin oficial de Transbank para WooCommerce, vía 03-RESEARCH Pattern 3].

## Tabla resumen — veredicto por flujo (runtime) contra Pattern 3 del research

| Flujo | Pattern 3 esperado | Observado runtime | Veredicto |
|---|---|---|---|
| Normal (aprobado) | `token_ws` solo, **GET** (API ≥1.1) | GET, `token_ws` solo; commit `response_code=0`/`AUTHORIZED` | **CONFIRMADO** |
| Normal (rechazado) | `token_ws` solo, GET; commit con `response_code != 0` | GET, `token_ws` solo; commit `response_code=-1`/`FAILED` vía 3DS "Rechazar" | **CONFIRMADO** (detalle en hallazgos del cierre) |
| Anulado por la clienta | `TBK_TOKEN`+`TBK_ORDEN_COMPRA`+`TBK_ID_SESION`, sin `token_ws`; docs dicen **POST en integración** | Params exactos; método **GET** | **CONFIRMADO en params; CORREGIDO en método** (GET, no POST) |
| Timeout del form | `TBK_ID_SESION`+`TBK_ORDEN_COMPRA` sin token; método no declarado; reloj 10 min | GET, params exactos; **603 s (10:03) cronometrados** desde la carga del form (tab activo); **puede no llegar nunca** si el tab duerme (13 min sin retorno, tab en background sin interacción) | **CONFIRMADO en params, método (GET) y reloj (~10 min); matiz: el redirect no está garantizado** |
| Error de formulario | 4 params juntos (`token_ws`+`TBK_TOKEN`) | No disparable runtime en integración (re-ingreso con mismo token → Error 21); fuente: docs oficiales + plugin oficial | **DOCUMENTADO (A3)** — la rama token_ws+TBK_TOKEN del discriminador lo cubre |

## Decisión de mecánica (D-41)

**Opción elegida: redirect 302 del backend a la ruta única de resultado de la
SPA (`/pago/resultado`)** — `RedirectResponse(url, status_code=302)` con el 302
EXPLÍCITO, llevando el resultado como query params (p. ej.
`/pago/resultado?estado=pagado&orden=MAURA-000001`).

**Descartada: página intermedia HTML que auto-submitea el POST hacia la SPA.**
Más piezas móviles (una plantilla intermedia + un form + un submit automático),
cero ganancia: la SPA no necesita el body del POST — con saber el FLUJO y la
ORDEN basta para fetchear `GET /api/pedidos/{numero}` con el Bearer del
localStorage. Es la variante que usa el plugin oficial para WordPress
(`wp_redirect`, o sea 302 igualmente, hacia la página del comercio).

**Por qué 302 y no el 307 default de starlette:** `RedirectResponse(url)` sin
`status_code` usa 307, que preserva método + body. Si el retorno de Webpay
llegó por POST, la "redirección" re-POSTearía el form de Webpay contra la ruta
de la SPA — que no tiene handler POST — y la pantalla revienta (Pitfall 1).
El 302 fuerza el GET del navegador (patrón PRG). Evidencia por flujo que firma
la decisión:

- **Aprobado y rechazado** (llegan por GET con `token_ws`): commit en el
  backend → 302 a `/pago/resultado` con estado. Acá 302/307 serían
  equivalentes (el redirect parte de un GET), pero se usa 302 uniforme.
- **Anulado**: llegó por GET en integración (corrección material de este
  spike), pero las docs oficiales lo declaran POST en integración — y el
  método documentado YA no es confiable (este spike lo demostró). Si cualquier
  flujo llega por POST, solo el 302 evita el re-POST contra la SPA.
- **Timeout**: GET observado en 20 retornos; mismo argumento defensivo.
- **Error de formulario**: solo en producción, método no documentado — el 302
  es la única elección segura para lo no observado.

**El discriminador va por PRESENCIA de params, jamás por método HTTP** — este
spike lo corroboró de la forma más convincente posible: el método real del
anulado CONTRADIJO a la documentación oficial (GET en vez de POST), mientras
que la presencia de params fue 100% estable en los 25+ retornos observados
(Pitfall 2). El endpoint se declara GET **y** POST, y lee query Y body.

## Hallazgos extra del spike

### (a) Camino reproducible a REJECTED en integración (Q2 — RESUELTO empíricamente)

- **VERIFICADO — elegir "Rechazar" en el simulador bancario**: la segunda
  página del 3DS (`authenticatorProcess.cgi`) muestra un select con
  Aceptar (`TSY`) / Rechazar (`TSN`). Con `TSN` el pago SIGUE el flujo normal:
  retorno por GET con SOLO `token_ws`, y el commit devuelve
  `response_code=-1`, `status=FAILED`, `authorization_code="000000"`,
  `vci=TSN` (orden SPK-D2EACCB6, 14:52 UTC). **Es el camino que la guía
  documenta** — mismo discrimine que el aprobado (token_ws solo), la
  diferencia la decide el criterio de PAY-03 en el commit.
- **CVV incorrecto NO rechaza**: con CVV `999` el pago APRUEBA igual
  (SPK-F5A0D819: `response_code=0`, `AUTHORIZED`) — el ambiente de
  integración no valida el CVV. No sirve como camino a REJECTED.
- **Clave 3DS errada NO rechaza**: produce `error.cgi` ("Tu transacción no se
  pudo llevar a cabo") con la transacción quedando `INITIALIZED` y SIN commit
  — el navegador jamás llega al return_url por esa vía. No es REJECTED.
  (El RUT del simulador exige el formato CON puntos `11.111.111-1`: sin
  puntos el authenticator también deriva a este error — nota operativa para
  la guía y el UAT.)
- **Fallback declarado (se mantiene)**: la carrera de stock de D-35 también
  produce REJECTED (commit aprobado que no puede descontar) y el UAT de fase
  la ejercita igual.

### (b) Idempotencia del commit de Webpay (A1 — CONFIRMADA runtime)

Re-navegar al retorno aprobado (segundo `commit` del MISMO token,
SPK-E871B543 a las 14:54 UTC) devolvió la respuesta **idéntica byte a byte en
los campos que importan**: `response_code=0`, `AUTHORIZED`, mismo
`authorization_code=1213`, mismo `transaction_date`. Sin doble efecto
observable. El diseño NO depende de ello — el guard de estado de la orden
(checkIsAlreadyProcessed del plugin oficial) sigue siendo obligatorio (Pitfall
4) — pero la asunción A1 pasa de consenso de comunidad a observación runtime.

### (c) Tiempo real del timeout (Q3 — CRONOMETRADO)

603 s (10 min 3 s) desde la carga del formulario hasta el retorno, medidos en
corrida controlada con tab activo (SPK-111B70EF) — el reloj documentado de
"10 minutos en integración" calza casi al segundo. La guía le dice al alumno
que espere ~10 minutos activos. Detalle completo y contraindicaciones en el
flujo 3 arriba (el redirect NO está garantizado si el tab duerme).

### (d) Hallazgos operativos menores (para guías/UAT, no cambian diseño)

- El SDK 6.1.0 devuelve el token del `create` bajo la clave `"token"` (NO
  `"token_ws"`); el `input` del form SÍ se llama `token_ws` — nombre que
  exige Webpay en el wire.
- Tras un fallo del banco (`error.cgi`), el form aún abierto redirige al
  retorno con **params de TIMEOUT** a los 22-78 s (observado 9 veces, con
  repeticiones) — no todo retorno con params de timeout fue un timeout real
  de 10 min: el backend no debe inferir la causa, solo el flujo.
- El navegador puede REPETIR el mismo retorno (recargas del tab): 7
  repeticiones observadas para un mismo timeout — el backend debe tolerar
  retornos duplicados (refuerza Pitfall 4).
- `status(TBK_TOKEN)` funciona para transacciones anuladas (queda
  `INITIALIZED`) y `status(token)` para commiteadas (`AUTHORIZED` /
  `FAILED`) — ventana de 7 días, útil para la fase 4.

## Tabla final de veredictos — evidencia por flujo (la que ADR-012 cita)

| Flujo | Método observado | Params observados | vs Pattern 3 / docs | Cita para ADR-012 |
|---|---|---|---|---|
| Normal aprobado | **GET** | `token_ws` solo | CONFIRMADO (docs: GET desde API 1.1) | SPK-E871B543: commit `response_code=0`+`AUTHORIZED`, 61.6 s create→retorno |
| Normal rechazado | **GET** | `token_ws` solo | CONFIRMADO (mismo flujo; decide el commit) | SPK-D2EACCB6: commit `response_code=-1`+`FAILED` vía 3DS "Rechazar" (TSN) |
| Anulado | **GET** | `TBK_TOKEN`+`TBK_ID_SESION`+`TBK_ORDEN_COMPRA`, sin `token_ws` | Params CONFIRMADOS; método CORREGIDO (docs decían POST en integración) | SPK-E8F80C75: 6.8 s create→retorno; status(TBK_TOKEN)=INITIALIZED; sin commit |
| Timeout | **GET** | `TBK_ID_SESION`+`TBK_ORDEN_COMPRA`, sin token | CONFIRMADO; reloj cronometrado 603 s; redirect NO garantizado | SPK-111B70EF: 10:03 desde carga del form; SPK-5CAF879B: 13 min sin retorno (tab dormido) |
| Error de formulario | (no observable en integración) | los 4 juntos (`token_ws`+`TBK_TOKEN`+`TBK_ID_SESION`+`TBK_ORDEN_COMPRA`) | DOCUMENTADO (docs + plugin oficial; A3) | Re-ingreso con mismo token en integración → Error 21 (SPK-95FE5530): corrobora "solo producción" |

**Lectura para el contrato 0.3.0 (plan 03-02):** el endpoint
`GET+POST /api/pago/retorno` queda INMUNE a la ambigüedad GET/POST (Pitfall 2)
— este spike demostró que ni siquiera las docs oficiales aciertan el método
por flujo. La respuesta del endpoint es SIEMPRE un 302 (no 307) hacia
`/pago/resultado`; el discriminador lee los 4 params de query Y body.
