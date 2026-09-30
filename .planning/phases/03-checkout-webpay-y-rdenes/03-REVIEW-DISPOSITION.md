---
phase: 03
review: 03-REVIEW.md
titles: json
findings:
  - id: CR-01
    severity: critical
    disposition: open
    title: "`routers/retorno.py` importa `Error` desde un módulo que no lo define — ImportError al copiar la guía tal cual"
  - id: WR-01
    severity: warning
    disposition: open
    title: "`services/pedidos.py` importa `transbank` — viola la regla \"único archivo que importa transbank\" que la guía enseña y verifica"
  - id: WR-02
    severity: warning
    disposition: open
    title: "`return_url` construido desde `settings.cors_origins[0]` (origen de la SPA) — semánticamente es una URL del backend y solo funciona por el proxy de Vite"
  - id: WR-03
    severity: warning
    disposition: open
    title: "El guard de idempotencia ya-PAID (y el de `_cancelar`) es read-check-write en Python — la ventana de carrera que la propia guía enseña a evitar"
  - id: WR-04
    severity: warning
    disposition: open
    title: "La narrativa del F5 es factualmente incorrecta — el F5 sobre `/pago/resultado` NO repite el retorno del backend"
  - id: WR-05
    severity: warning
    disposition: open
    title: "El diccionario de datos de PEDIDO (diseño §2.2) no declara `fecha`, pero la guía 9 agrega la columna y afirma coincidencia \"campo a campo... ni una más\""
  - id: IN-01
    severity: info
    disposition: open
    title: "Typo en HU-09/HU-10 — \"se descuento stock una segunda vez\""
  - id: IN-02
    severity: info
    disposition: open
    title: "El título de `ResultadoPago` no cubre el estado `cancelled` del pedido fetcheado"
  - id: IN-03
    severity: info
    disposition: open
    title: "Contrato declara `requestBody.required: true` en POST /api/pago/retorno, pero la implementación enseñada acepta body ausente"
  - id: IN-04
    severity: info
    disposition: open
    title: "El 400 de `/api/checkout` por \"aroma no disponible/inexistente\" no está documentado en el contrato"
  - id: IN-05
    severity: info
    disposition: open
    title: "Wireframe de la pantalla 9 muestra \"Carro (0)\", contradiciendo la regla \"contador oculto en cero\" de la pantalla 6"
  - id: IN-06
    severity: info
    disposition: open
    title: "Una falla de red durante `webpay.commit` escapa como 500 al navegador — la promesa \"jamás un 500\" solo cubre `TransactionCommitError`"
open: 12
total: 12
recorded: 2026-09-30T19:02:01.379Z
---

# Phase 03: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| CR-01 | critical | open | - |
| WR-01 | warning | open | - |
| WR-02 | warning | open | - |
| WR-03 | warning | open | - |
| WR-04 | warning | open | - |
| WR-05 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | open | - |
| IN-06 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
