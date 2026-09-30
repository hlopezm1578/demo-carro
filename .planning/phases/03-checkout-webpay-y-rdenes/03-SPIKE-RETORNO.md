---
status: complete
phase: 03-checkout-webpay-y-rdenes
source: [03-RESEARCH.md]
started: 2026-09-30T14:24:18Z
updated: 2026-09-30T15:21:00Z
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

## Tabla resumen — veredicto por flujo (runtime) contra Pattern 3 del research

| Flujo | Pattern 3 esperado | Observado runtime | Veredicto |
|---|---|---|---|
| Normal (aprobado) | `token_ws` solo, **GET** (API ≥1.1) | GET, `token_ws` solo; commit `response_code=0`/`AUTHORIZED` | **CONFIRMADO** |
| Normal (rechazado) | `token_ws` solo, GET; commit con `response_code != 0` | GET, `token_ws` solo; commit `response_code=-1`/`FAILED` vía 3DS "Rechazar" | **CONFIRMADO** (detalle en hallazgos del cierre) |
| Anulado por la clienta | `TBK_TOKEN`+`TBK_ORDEN_COMPRA`+`TBK_ID_SESION`, sin `token_ws`; docs dicen **POST en integración** | Params exactos; método **GET** | **CONFIRMADO en params; CORREGIDO en método** (GET, no POST) |
| Timeout del form | `TBK_ID_SESION`+`TBK_ORDEN_COMPRA` sin token; método no declarado; reloj 10 min | GET, params exactos; **603 s (10:03) cronometrados** desde la carga del form (tab activo); **puede no llegar nunca** si el tab duerme (13 min sin retorno, tab en background sin interacción) | **CONFIRMADO en params, método (GET) y reloj (~10 min); matiz: el redirect no está garantizado** |
| Error de formulario | 4 params juntos (`token_ws`+`TBK_TOKEN`) | No disparable runtime en integración — se documenta en el cierre (A3) | (fila del cierre) |
