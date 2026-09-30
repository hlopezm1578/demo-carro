---
status: testing
phase: 03-checkout-webpay-y-rdenes
source: [03-VERIFICATION.md]
started: 2026-09-30T17:30:00Z
updated: 2026-09-30T17:30:00Z
---

## Current Test

number: 1
name: UAT delegado de fase 3 en D:/Repos/maura-uat (construye guías 09-11 y corre la Gran verificación final de guia-11 — per AGENTS.md lo ejecuta el agente)
expected: |
  Los 4 flujos runtime con la VISA oficial 4051 8856 0044 6623 (voucher + carro vaciado SOLO en
  aprobado; anulado con carro intacto), timeout ~603 s con pestaña activa, F5 sin doble pago,
  carrera.py → exactamente un PAID + un REJECTED + stock 0, PENDING huérfana visible "en curso",
  404 uniforme de ownership, y fila contrato 0.3.0 ↔ /docs (302 con Location, Authorize 200/403) —
  todo en verde, registrado con verified_by: agent (user-delegated).
awaiting: user response

## Tests

### 1. UAT delegado de fase 3 en maura-uat (resuelve los 5 Success Criteria runtime)
expected: Ejecutar `/gsd-verify-work 3`: el agente construye guías 09-11 en `D:/Repos/maura-uat` y corre la Gran verificación final de guia-11 — 4 flujos runtime, F5 sin doble pago, carrera de stock, PENDING huérfana, 404 uniforme, contrato ↔ /docs. Registra resultados en este archivo con `verified_by: agent (user-delegated)`.
result: [pending]

### 2. Aceptar la corrección del flujo anulado (evidencia runtime vs documentación oficial de Transbank)
expected: Confirmar que el corpus usa la evidencia del spike como canónica: el anulado llegó por GET (no POST) con TBK_TOKEN+TBK_ID_SESION+TBK_ORDEN_COMPRA sin token_ws — discriminador por presencia de params, inmune al método (03-SPIKE-RETORNO.md, corridas 2026-09-30).
result: [pending]

### 3. Disposición de los 6 hallazgos Info abiertos del code review (IN-01..IN-06)
expected: Decidir cierre vía `/gsd-code-review 3 --fix --all` o dejarlos para el ciclo de gaps (ver 03-REVIEW-DISPOSITION.md: typo "se descuento", título ResultadoPago/cancelled, requestBody.required del retorno, 400 del checkout no documentado, wireframe "Carro (0)", falla de red en commit → 500).
result: [pending]

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps
