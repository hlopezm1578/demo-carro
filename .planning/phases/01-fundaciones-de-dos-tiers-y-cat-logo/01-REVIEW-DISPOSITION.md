---
phase: 01
review: 01-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: open
    title: "Contrato omite el 422 de `GET /api/productos/{producto_id}` — el prose nuevo lo hace visible y la fila 11 sigue sin advertirlo"
  - id: WR-02
    severity: warning
    disposition: open
    title: "`Error` presentado como \"el cuerpo de los errores\" — el 422 real de FastAPI trae `detail` como array, no string"
  - id: WR-08
    severity: warning
    disposition: open
    title: "La fila 11 — invocada por el texto nuevo como \"la comparación que cierra\" — no incluye el schema `Error` en la comparación de schemas"
  - id: IN-09
    severity: info
    disposition: open
    title: "El `.gitignore` se crea en el Paso 5, pero `.venv/` existe desde el Paso 3 — ventana sin cobertura para quien commitea temprano"
  - id: WR-03
    severity: warning
    disposition: open
    title: "El catálogo enseñado no distingue el 422 de familia inválida — incumple el diseño §3.4 (\"se rechaza con un mensaje claro\")"
  - id: WR-04
    severity: warning
    disposition: open
    title: "`apiGet` asigna el `detail` del 422 (array) a una variable string — el mensaje de todo 422 se degrada a \"[object Object]\""
  - id: WR-05
    severity: warning
    disposition: open
    title: "Diseño §5 (trazabilidad requerimiento → diseño) omite RNF-02 y RNF-03"
  - id: WR-06
    severity: warning
    disposition: open
    title: "Requerimientos §10 declara una validación de rango de precio que ni el contrato ni la guía 4 implementan"
  - id: WR-07
    severity: warning
    disposition: open
    title: "\"Fase\" vs \"etapa\": el mismo eje (carro → pago → panel/IA) recibe dos nombres y \"fase 3\" significa dos cosas distintas en el README raíz"
  - id: IN-01
    severity: info
    disposition: open
    title: "URLs externas fuera del paso de fotos — contradice el invariante declarado de \"única sección con URLs de terceros\""
  - id: IN-02
    severity: info
    disposition: open
    title: "guia-02 indica borrar `src/react.svg`, pero en el template actual el archivo vive en `src/assets/react.svg`; y el reemplazo de `index.html` es un tercer cambio no anunciado"
  - id: IN-03
    severity: info
    disposition: open
    title: "Identificador \"D1\" sobrecargado entre fases y dolores D1–D6 sin trazabilidad explícita hacia P"
  - id: IN-04
    severity: info
    disposition: open
    title: "guia-04 atribuye al diseño §4.4 umbrales de stock que el diseño no fija"
  - id: IN-05
    severity: info
    disposition: open
    title: "`BadgeDisponibilidad` produce \"¡Últimas 1 unidades!\" para stock=1 — no pluraliza como el resto de la pantalla"
  - id: IN-06
    severity: info
    disposition: open
    title: "README de 05_desarrollo duplica el mismo párrafo de cierre a 8 líneas de distancia"
  - id: IN-07
    severity: info
    disposition: open
    title: "`descripcion` no reproduce la longitud 1000 del diccionario de datos, pese a la afirmación \"campo a campo, sin agregar ni quitar\""
  - id: IN-08
    severity: info
    disposition: open
    title: "Typo en requerimientos §3: \"para que el hilo quedé completo\""
open: 17
total: 17
recorded: 2026-09-29T12:29:07.909Z
---

# Phase 01: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | open | - |
| WR-02 | warning | open | - |
| WR-08 | warning | open | - |
| IN-09 | info | open | - |
| WR-03 | warning | open | - (not in the current review) |
| WR-04 | warning | open | - (not in the current review) |
| WR-05 | warning | open | - (not in the current review) |
| WR-06 | warning | open | - (not in the current review) |
| WR-07 | warning | open | - (not in the current review) |
| IN-01 | info | open | - (not in the current review) |
| IN-02 | info | open | - (not in the current review) |
| IN-03 | info | open | - (not in the current review) |
| IN-04 | info | open | - (not in the current review) |
| IN-05 | info | open | - (not in the current review) |
| IN-06 | info | open | - (not in the current review) |
| IN-07 | info | open | - (not in the current review) |
| IN-08 | info | open | - (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
