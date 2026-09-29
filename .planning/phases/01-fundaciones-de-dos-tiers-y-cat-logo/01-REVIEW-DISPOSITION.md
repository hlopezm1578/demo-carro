---
phase: 01
review: 01-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: open
    title: "Contrato omite el 422 de `GET /api/productos/{producto_id}` — la fila 11 sigue mandando a compararlo sin advertirlo"
  - id: WR-02
    severity: warning
    disposition: open
    title: "`Error` presentado como \"el cuerpo de los errores\" — el 422 real de FastAPI trae `detail` como array, no string"
  - id: WR-03
    severity: warning
    disposition: open
    title: "El catálogo enseñado no distingue el 422 de familia inválida — incumple el diseño §3.4 (\"se rechaza con un mensaje claro\")"
  - id: WR-04
    severity: warning
    disposition: open
    title: "`apiGet` asigna el `detail` del 422 (array) a una variable string — el mensaje de todo 422 se degrada a \"[object Object]\""
  - id: WR-08
    severity: warning
    disposition: open
    title: "La fila 11 — \"la comparación que cierra\" la fase — no incluye el schema `Error` en la comparación de schemas"
  - id: WR-09
    severity: warning
    disposition: open
    title: "El botón \"Filtrar precio\" usa `border-orange-300` — el único paso de la escala que el `@theme` nuevo NO sobrescribe, rompiendo el invariante enseñado"
  - id: WR-10
    severity: warning
    disposition: open
    title: "La instrucción de la foto en la card de familia produce el kicker \"Familia 0X\" pegado a la imagen — el fix de espaciado (`mt-4`) no está enseñado"
  - id: IN-01
    severity: info
    disposition: open
    title: "\"Única sección de toda la guía con URLs de terceros\" — cierto dentro de guia-04, falso si \"la guía\" es la serie"
  - id: IN-02
    severity: info
    disposition: open
    title: "`index.html` anuncia \"dos cambios\" pero son tres; y `src/react.svg` vive en `src/assets/` en el template actual"
  - id: IN-04
    severity: info
    disposition: open
    title: "`guia-04` atribuye al diseño §4.4 umbrales de stock que el diseño no fija"
  - id: IN-05
    severity: info
    disposition: open
    title: "`BadgeDisponibilidad` produce \"¡Últimas 1 unidades!\" para stock=1 — no pluraliza como el resto de la pantalla"
  - id: IN-10
    severity: info
    disposition: open
    title: "El `alt` de la foto del hero no tiene efecto — el contenedor conserva el `aria-hidden=\"true\"` de los anillos y la guía no indica quitarlo"
  - id: IN-11
    severity: info
    disposition: open
    title: "La landing rediseñada se presenta como §4.2 \"cómo se ve\" — pero el wireframe de §4.2 es de una columna centrada, un solo CTA y footer de una línea"
  - id: IN-12
    severity: info
    disposition: open
    title: "\"npm install falla con el warning EBADENGINE\" — npm no falla: con la configuración por defecto es un warning no fatal"
  - id: IN-13
    severity: info
    disposition: open
    title: "Typo en la mini-verificación del Paso 10: \"el tagline … ENorme\""
  - id: IN-09
    severity: info
    disposition: open
    title: "El `.gitignore` se crea en el Paso 5, pero `.venv/` existe desde el Paso 3 — ventana sin cobertura para quien commitea temprano"
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
  - id: IN-03
    severity: info
    disposition: open
    title: "Identificador \"D1\" sobrecargado entre fases y dolores D1–D6 sin trazabilidad explícita hacia P"
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
open: 23
total: 23
recorded: 2026-09-29T14:33:50.397Z
---

# Phase 01: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | open | - |
| WR-02 | warning | open | - |
| WR-03 | warning | open | - |
| WR-04 | warning | open | - |
| WR-08 | warning | open | - |
| WR-09 | warning | open | - |
| WR-10 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | open | - |
| IN-10 | info | open | - |
| IN-11 | info | open | - |
| IN-12 | info | open | - |
| IN-13 | info | open | - |
| IN-09 | info | open | - (not in the current review) |
| WR-05 | warning | open | - (not in the current review) |
| WR-06 | warning | open | - (not in the current review) |
| WR-07 | warning | open | - (not in the current review) |
| IN-03 | info | open | - (not in the current review) |
| IN-06 | info | open | - (not in the current review) |
| IN-07 | info | open | - (not in the current review) |
| IN-08 | info | open | - (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
