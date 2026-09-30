---
status: complete
phase: 03-checkout-webpay-y-rdenes
source: [03-VERIFICATION.md]
started: 2026-09-30T17:30:00Z
updated: 2026-09-30T18:35:00Z
---

## Current Test

[testing complete]

## Tests

### 1. UAT delegado de fase 3 en maura-uat (resuelve los 5 Success Criteria runtime)
expected: Ejecutar `/gsd-verify-work 3`: el agente construye guías 09-11 en `D:/Repos/maura-uat` y corre la Gran verificación final de guia-11 — 4 flujos runtime, F5 sin doble pago, carrera de stock, PENDING huérfana, 404 uniforme, contrato ↔ /docs. Registra resultados en este archivo con `verified_by: agent (user-delegated)`.
result: pass
verified_by: agent (user-delegated)
evidence: |
  Corrida 2026-09-30 (sesión /gsd-verify-work 3). Guías 09-11 construidas en maura-uat con los
  comandos literales de las guías: uv add transbank-sdk → 597055555532; seed 14 [=] con tablas
  pedidos/pedidos_lineas creadas; discriminador imprime `normal anulado timeout error_formulario
  desconocido`; /docs 0.3.0 con los 4 paths nuevos y sus códigos. Gran verificación final 12/12:
  (1) precio inyectado `"precio":1` ignorado por HTTP — orden total 17.980 = 2×8.990 del catálogo;
  stock insuficiente → 400 y la orden NO se crea; (2) APROBADO con VISA 4051 8856 0044 6623 + 3DS
  (RUT 11.111.111-1, clave 123): voucher de la tienda "MAURA-000006 · Pagado" con líneas snapshot y
  total $15.980; (3) carro vaciado SOLO en aprobado (maura-carro `{"items":[]}`) y stock 14→12;
  (4) ANULADO con el botón del formulario: "Tu compra no se concretó" + carro intacto (badge en 1);
  (5) TIMEOUT con pestaña activa: retorno a los ~11 min → cara "Se agotó el tiempo" + carro intacto
  (ver desvío D-3); (6) cuarto flujo documentado solo-producción, cubierto por el discriminador;
  (7) F5 sobre el voucher pagado: mismo voucher, estado paid, stock sin segundo descuento;
  (8) carrera.py: exactamente un PAID + un REJECTED + stock 0; (9) /pedidos lista TODAS las órdenes
  con badges honestos — huérfanas MAURA-000001/000002/000009 visibles "En curso" (RN-11), detalle =
  MISMO VoucherPedido; (10) /pedidos sin sesión → login → vuelve AL historial (returnTo);
  MAURA-999999 → 404 uniforme; (11) numero legible en voucher, historial y URL (/pedidos/MAURA-000006);
  (12) contrato 0.3.0 ↔ /docs: versiones y 11 paths idénticos, 302+400 declarados en GET y POST del
  retorno, retorno sin candado, clienta 200 en /api/pedidos y 403 "Requiere rol admin" en
  /api/admin/estado. Además MVs de guia-10/11 en verde (compilador rechaza "PAID", huérfana "Tu pago
  está en curso" con badge ámbar sin vaciar el carro, cara anulado visible sin sesión en ruta pública).
  DESVÍOS ENCONTRADOS Y CORREGIDOS EN GUÍA + APP (regla dos lugares):
  D-1 (blocker runtime) `PedidoRepository.crear` reventaba con `IntegrityError NOT NULL
  pedidos.numero`: el INSERT exige numero antes de que exista el id del que nace. Fix: default
  `_numero_provisorio()` (uuid, 24 chars) en models/pedido.py, reemplazado por MAURA-{id:06d} antes
  del commit — guia-09 paso 2 (código + narrativa del gallina-y-huevo).
  D-2 (blocker runtime) carrera.py moría con `NoReferencedTableError` (FK pedidos.usuario_id →
  usuarios sin registrar): faltaba el import del modelo usuario en el script. Fix:
  `from app.models import usuario  # noqa: F401` — guia-09 paso 10.
  D-3 (doc) fila 5 de guia-11 y paso 7 de guia-10 decían que el timeout con pestaña ACTIVA deja la
  orden PENDING "en curso": runtime demuestra que el retorno del timeout SÍ llega (~603 s) y marca
  CANCELLED (badge "Anulado"); "en curso" queda solo para el retorno que no llega (pestaña dormida).
  Fix en ambos pasajes + precisión en la MV de la huérfana (guia-11 paso 5).

### 2. Aceptar la corrección del flujo anulado (evidencia runtime vs documentación oficial de Transbank)
expected: Confirmar que el corpus usa la evidencia del spike como canónica: el anulado llegó por GET (no POST) con TBK_TOKEN+TBK_ID_SESION+TBK_ORDEN_COMPRA sin token_ws — discriminador por presencia de params, inmune al método (03-SPIKE-RETORNO.md, corridas 2026-09-30).
result: pass
decided_by: user (2026-09-30)
decision: Aceptar la evidencia runtime como canónica — el corpus se queda como está (discriminador por presencia, ADR-012/contrato/guias 09-11); el UAT delegado del test 1 re-corroboró los flujos anulado y timeout reales.

### 3. Disposición de los 6 hallazgos Info abiertos del code review (IN-01..IN-06)
expected: Decidir cierre vía `/gsd-code-review 3 --fix --all` o dejarlos para el ciclo de gaps (ver 03-REVIEW-DISPOSITION.md: typo "se descuento", título ResultadoPago/cancelled, requestBody.required del retorno, 400 del checkout no documentado, wireframe "Carro (0)", falla de red en commit → 500).
result: pass
decided_by: user (2026-09-30)
decision: Cerrar con `/gsd-code-review 3 --fix --all` — decisión de cierre dentro de la fase 3; ejecución del fixer es el paso inmediato siguiente al cierre de esta sesión UAT.

## Summary

total: 3
passed: 3
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps
