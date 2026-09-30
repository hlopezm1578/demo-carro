---
phase: 03
review: 03-REVIEW.md
titles: json
findings:
  - id: CR-01
    severity: critical
    disposition: fixed
    title: "`routers/retorno.py` importa `Error` desde un módulo que no lo define — ImportError al copiar la guía tal cual"
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "`services/pedidos.py` importa `transbank` — viola la regla \"único archivo que importa transbank\" que la guía enseña y verifica"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "`return_url` construido desde `settings.cors_origins[0]` (origen de la SPA) — semánticamente es una URL del backend y solo funciona por el proxy de Vite"
  - id: WR-03
    severity: warning
    disposition: fixed
    title: "El guard de idempotencia ya-PAID (y el de `_cancelar`) es read-check-write en Python — la ventana de carrera que la propia guía enseña a evitar"
  - id: WR-04
    severity: warning
    disposition: fixed
    title: "La narrativa del F5 es factualmente incorrecta — el F5 sobre `/pago/resultado` NO repite el retorno del backend"
  - id: WR-05
    severity: warning
    disposition: fixed
    title: "El diccionario de datos de PEDIDO (diseño §2.2) no declara `fecha`, pero la guía 9 agrega la columna y afirma coincidencia \"campo a campo... ni una más\""
  - id: IN-01
    severity: info
    disposition: fixed
    title: "Typo en HU-09/HU-10 — \"se descuento stock una segunda vez\""
  - id: IN-02
    severity: info
    disposition: fixed
    title: "El título de `ResultadoPago` no cubre el estado `cancelled` del pedido fetcheado"
  - id: IN-03
    severity: info
    disposition: fixed
    title: "Contrato declara `requestBody.required: true` en POST /api/pago/retorno, pero la implementación enseñada acepta body ausente"
  - id: IN-04
    severity: info
    disposition: fixed
    title: "El 400 de `/api/checkout` por \"aroma no disponible/inexistente\" no está documentado en el contrato"
  - id: IN-05
    severity: info
    disposition: fixed
    title: "Wireframe de la pantalla 9 muestra \"Carro (0)\", contradiciendo la regla \"contador oculto en cero\" de la pantalla 6"
  - id: IN-06
    severity: info
    disposition: fixed
    title: "Una falla de red durante `webpay.commit` escapa como 500 al navegador — la promesa \"jamás un 500\" solo cubre `TransactionCommitError`"
open: 0
total: 12
recorded: 2026-09-30T19:03:15.687Z
---

# Phase 03: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| CR-01 | critical | fixed | 03-REVIEW-FIX.md |
| WR-01 | warning | fixed | 03-REVIEW-FIX.md |
| WR-02 | warning | fixed | 03-REVIEW-FIX.md |
| WR-03 | warning | fixed | 03-REVIEW-FIX.md |
| WR-04 | warning | fixed | 03-REVIEW-FIX.md |
| WR-05 | warning | fixed | 03-REVIEW-FIX.md |
| IN-01 | info | fixed | 03-REVIEW-FIX.md |
| IN-02 | info | fixed | 03-REVIEW-FIX.md |
| IN-03 | info | fixed | 03-REVIEW-FIX.md |
| IN-04 | info | fixed | 03-REVIEW-FIX.md |
| IN-05 | info | fixed | 03-REVIEW-FIX.md |
| IN-06 | info | fixed | 03-REVIEW-FIX.md |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
