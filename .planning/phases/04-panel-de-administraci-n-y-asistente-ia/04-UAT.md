---
status: testing
phase: 04-panel-de-administraci-n-y-asistente-ia
source: [04-VERIFICATION.md]
started: 2026-10-01T12:00:00.000Z
updated: 2026-10-01T12:00:00.000Z
---

## Current Test

number: 1
name: UAT delegado de fase 4 — construir guías 12-15 en D:/Repos/maura-uat y correr la Gran verificación final de guia-15
expected: |
  Construir las guías 12-15 en maura-uat como lo haría un alumno (comandos literales + mini-verificaciones),
  luego correr la Gran verificación final de guia-15 (13 filas): roles admin/clienta, CRUD con soft delete
  y toggle, anulación de huérfana PENDING 200→409, métricas vs órdenes reales de fase 3, degradación 503
  sin key, burbuja con states 503/429/red, contrato 0.4.0 ↔ /docs con Authorize admin, y grep del build
  (GEMINI_API_KEY sin resultados en dist/). Registrar resultados en este archivo con
  verified_by: agent (user-delegated) — instrucción persistida en AGENTS.md.
awaiting: user response

## Tests

### 1. UAT delegado de fase 4 (Gran verificación final de guia-15, 13 filas)
expected: Todas las filas de la Gran verificación final pasan runtime en maura-uat sobre la app construida hasta guia-15; resultados registrados acá con verified_by: agent (user-delegated).
result: [pending]

### 2. Happy path del asistente con llamada real a Gemini
expected: Con la GEMINI_API_KEY del usuario (creada gratis en aistudio.google.com, D-60), la burbuja responde recomendaciones del catálogo real con product cards válidas (AIAS-01/02 runtime). Sin key, este ítem queda bloqueado — la degradación 503 sí se verifica sin key.
result: [pending]

### 3. Ratificar las 5 flagged assumptions unclassified del edge probe (ADMN-02/03/04, AIAS-01/02)
expected: Confirmar contra la corrida UAT que los supuestos marcados (edge probe unclassified) se comportan como los planes asumieron; ratificar o abrir gaps.
result: [pending]

### 4. Decisión editorial IN-01 — espejo 422 del editor cubre 5/7 campos (guia-13)
expected: El usuario decide: agregar los copys de campo para descripcion/imagen (toca los copys locked del UI-SPEC) o dejar el espejo parcial con narrativa. Abierto por diseño en 04-REVIEW-DISPOSITION.md.
result: [pending]

### 5. Decisión editorial IN-03 — cláusula auto-pickup del SDK en ADR-017
expected: El usuario decide la redacción de la cláusula del ADR (cita del auto-pickup vs lo que guia-14 enseña). Abierto por diseño.
result: [pending]

## Summary

total: 5
passed: 0
issues: 0
pending: 5
skipped: 0
blocked: 0

## Gaps
