---
status: testing
phase: 05-Despliegue y cierre de la guía
source: [05-VERIFICATION.md]
started: 2026-10-01T19:10:00Z
updated: 2026-10-01T19:10:00Z
verified_by: pending
---

## Current Test

number: 1
name: Confirmación runtime D-73 — aceptar el cierre documental (override del backstop) o comisionar una corrida real de las guías 16-18
expected: |
  Decisión del usuario bajo D-73 (fase writing-only): la verdad backstop
  "API desplegada con URL pública + SPA refresh sin 404" solo es confirmable
  en la corrida del ALUMNO con sus cuentas. Opciones: (a) aceptar el cierre
  documental registrando el override para la verdad backstop; (b) autorizar
  una reversión parcial de D-73 (corrida real en maura-uat, que el usuario
  excluyó explícitamente con "no la probaremos").
awaiting: user decision

## Tests

### 1. Confirmación runtime D-73 (cierre documental vs corrida real)
expected: Decisión del usuario: aceptar override del backstop "API desplegada con URL pública + SPA refresh sin 404" (cierre documental D-73) O comisionar corrida real de guías 16-18 (reversión parcial de D-73 que solo el usuario puede autorizar).
result: [pending]

### 2. Supuesto A4 — Webpay integración acepta `https://*.onrender.com` como return_url
expected: Flagged assumption del plan 05-04: que el ambiente de integración de Transbank acepta un return_url en el dominio de Render. Solo confirmable en la corrida del alumno (primer flujo de pago en producción); documentado como supuesto señalado en guia-16/18.
result: [pending]

## Summary

total: 2
passed: 0
issues: 0
pending: 2
skipped: 0
blocked: 0

## Gaps

Ninguno automatizado — 34/35 must-haves verificados documentalmente (VERDE); los 7 findings del code review están en disposition deliberado (CR-01 fixed, 4 warnings + 3 infos open para triage del usuario).
