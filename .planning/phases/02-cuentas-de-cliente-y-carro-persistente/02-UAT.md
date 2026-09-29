---
status: testing
phase: 02-cuentas-de-cliente-y-carro-persistente
source: [02-VERIFICATION.md]
started: 2026-09-29T18:40:00Z
updated: 2026-09-29T18:40:00Z
verified_by: agent (user-delegated per AGENTS.md — taller D:/Repos/maura-uat)
---

## Current Test

number: 1
name: UAT delegado — construir guías 05-08 en el taller y ejecutar la Gran verificación final
expected: |
  12/12 filas PASS registradas en 02-UAT.md con verified_by: agent (user-delegated); el taller hoy
  NO tiene auth.py/admin.py/stores (solo fase 1) — la capa runtime completa está pendiente.
  Ejecución: en D:/Repos/maura-uat, seguir docs/05_desarrollo/guia-05-cuentas-backend.md →
  guia-06-sesion-frontend.md → guia-07-carro.md → guia-08-checkout.md en orden (comandos literales
  de las guías, mini-verificaciones incluidas), terminando con la "Gran verificación final" de
  guia-08 (tabla de 12 filas + botón Authorize de /docs contra contrato 0.2.0).
awaiting: agent execution (verify-work)

## Tests

### 1. UAT delegado en D:/Repos/maura-uat (agente, user-delegated per AGENTS.md)
expected: Construir guías 05-08 en orden en el taller y ejecutar la Gran verificación final de guia-08 (12 filas + Authorize) — 12/12 filas PASS registradas acá. Cubre las 4 Success Criteria del ROADMAP: sesión tras F5 (SC1), admin 200 vs clienta 403 en /api/admin/estado (SC2), carro tras full-page load con badge (SC3), y checkout: sin sesión → /login → vuelve al checkout (SC4).
result: [pending]

### 2. Runtime de los fixes WR-02 y WR-03 (marcados requires-human-verification en 02-REVIEW-FIX.md)
expected: |
  WR-02: login con credenciales malas NO redirige a ?expirada=1 (banner rojo "Credenciales incorrectas"
  dentro de la card — el login viaja sinAuth y jamás adjunta Bearer).
  WR-03: localStorage con cantidad > stock se corrige solo al hidratar (write-back) y el badge del
  navbar cuenta las unidades tapadas (mismo número que filas y total).
result: [pending]

### 3. Revisión de las 7 prohibiciones judgment-tier (flag unverified-prohibition)
expected: Confirmar el muestreo: P1 XSS en ADR-009 Negativas; P2 RN-05 sin composición; P3 cero secretos literales en guías 05/06; P4 401 genérico único en login; P5 store carro sin precios; P6 guard=UX dicho; P7 fila 5 Parcial (no ✅). El veredicto autónomo del verificador fue HONORED en las 7 — esta revisión lo ratifica.
result: [pending]

### 4. Formato del goal: User Story canónica en ROADMAP.md
expected: Correr `/gsd mvp-phase 2` para dejar el goal en formato "As a..., I want to..., so that..." (hoy user-story.validate = false; la versión canónica vive en los PLANs 02-03/02-04). Discrepancia heredada de fase 1 (01-VERIFICATION nota la misma).
result: [pending]

## Summary

total: 4
passed: 0
issues: 0
pending: 4
skipped: 0
blocked: 0

## Gaps
