---
phase: 04
review: 04-REVIEW.md
recorded: 2026-10-01T15:45:00.000Z
findings:
  critical: 0
  warning: 8
  info: 5
  total: 13
open: 13
---

# Phase 04: Code Review Disposition (rework Groq, 2026-10-01)

Review del rework Gemini→Groq (planes 04-06..08, base incremental ccf683b, profundidad standard, 14 archivos del corpus). **13 findings: 0 critical / 8 warning / 5 info — todos `open` a la espera de triage.**

> La disposición pre-rework (CR-01..IN-04, 8 findings, todas `fixed` con commits y decisiones del usuario del UAT 2026-10-01) pertenece al review anterior y quedó supersededa por este; su registro completo vive en git (`28480d4`, `0b0df1b`) y en [04-REVIEW-FIX.md](04-REVIEW-FIX.md).

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 Aritmética falsa: "1.000 RPD ≈ 16 consultas/min sostenidas" (real ~0,7/min; 16/min × 1.440 ≈ 23.000 RPD) — contradice la disciplina cifras-con-fuente de D-68 | warning | open | guia-14-asistente-backend.md:40,376 |
| WR-02 Justificación Gemini-era del 429 ("no son públicas (sin login)" / "concern abierto") sobrevive en guia-15 pese a D-66 (el paréntesis muere con Groq); contradice guia-14 y ADR-018 | warning | open | guia-15-asistente-cierre.md:142,257,473 |
| WR-03 README de arquitectura cita ADR-017 como capa técnica vigente tras la supersession (barrido incompleto) | warning | open | docs/04_arquitectura/README.md:163,199 |
| WR-04 docs/03 sigue declarando "su capa técnica es ADR-017" para el mini-RAG | warning | open | docs/03_diseno.md:243,289 |
| WR-05 La fila del índice de ADR-017 cita D-63, que el cuerpo del propio ADR-017 no registra (registra D-60) | warning | open | docs/04_arquitectura/README.md:235 |
| WR-06 RN-08 (regla del carro) citada 4 veces para el "404 uniforme de ownership" del detalle, que es RF-17/§3.13 | warning | open | guia-13-panel-spa.md:1032,1044,1563,1667 |
| WR-07 `uv run fastapi dev app/main` sin `.py` — único caso en 9 guías (lección D-4-9 del UAT) | warning | open | guia-14-asistente-backend.md:701 |
| WR-08 Variante PowerShell del grep de seguridad (fila 13, AIAS-03) no es recursiva: `Select-String -Path dist\*` no escanea `dist/assets/*.js` — posible falso éxito en Windows | warning | open | guia-15-asistente-cierre.md:530 |
| IN-01 "1-3 cards" en encabezado y fila 8 de guia-15, pero el contrato permite 0-3 | info | open | guia-15-asistente-cierre.md:9,525 |
| IN-02 Fechas de documento/aprobación anteriores al contenido reworkado que contienen | info | open | docs/02_requerimientos.md, docs/03_diseno.md |
| IN-03 Import `Pedido` sin uso en el bloque enseñado de `services/admin.py` | info | open | guia-12-panel-backend.md:620 |
| IN-04 Filas 10 y 12 de la Gran verificación citan solo ADR-017 (superseded) | info | open | guia-15-asistente-cierre.md |
| IN-05 Drift fuera del diff: AGENTS.md aún recomienda `google-genai` en el stack (observación para cerrar el círculo D-67 vía flujo GSD) | info | open | AGENTS.md:25,58 |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently.
