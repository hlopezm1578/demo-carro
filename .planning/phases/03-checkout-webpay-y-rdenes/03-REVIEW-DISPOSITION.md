---
phase: 03-checkout-webpay-y-rdenes
recorded: 2026-09-30
source: [03-REVIEW.md, 03-REVIEW-FIX.md]
open: 6
fixed: 6
skipped: 0
deferred: 0
total: 12
---

# Review Disposition — Fase 3

Registro por hallazgo del review de código (`03-REVIEW.md`, status: issues_found — 1 critical, 5 warning, 6 info). Los fixes de CR/WR fueron aplicados por `gsd-code-fixer` y documentados en `03-REVIEW-FIX.md`. Los 6 Info quedan `open` (fuera del scope default de `--fix`: Critical + Warning).

| Finding | Severity | Title | Disposition | Source |
|---------|----------|-------|-------------|--------|
| CR-01 | critical | `routers/retorno.py` importa `Error` desde módulo que no lo define — ImportError | fixed (commit 97b7346) | 03-REVIEW-FIX.md |
| WR-01 | warning | `services/pedidos.py` importa `transbank` — viola la regla del wrapper único | fixed (commit 2572b81) | 03-REVIEW-FIX.md |
| WR-02 | warning | `return_url` derivado de `cors_origins[0]` — debe ser URL del backend | fixed (commit 4a3484a) | 03-REVIEW-FIX.md |
| WR-03 | warning | Guard ya-PAID read-check-write — ventana de carrera concurrente | fixed (commit 2b21df0) | 03-REVIEW-FIX.md |
| WR-04 | warning | Narrativa del F5 factualmente incorrecta en guías 10/11 | fixed (commit d90f5b8) | 03-REVIEW-FIX.md |
| WR-05 | warning | Diccionario PEDIDO (§2.2) sin `fecha` — trazabilidad rota | fixed (commit 0b1bd2d) | 03-REVIEW-FIX.md |
| IN-01 | info | Typo "se descuento" en HU-09/HU-10 | open | — |
| IN-02 | info | Título de `ResultadoPago` no cubre `cancelled` | open | — |
| IN-03 | info | Contrato: `requestBody.required: true` en POST retorno vs body ausente aceptado | open | — |
| IN-04 | info | 400 de `/api/checkout` por aroma inexistente no documentado en contrato | open | — |
| IN-05 | info | Wireframe pantalla 9 muestra "Carro (0)" — contradice regla del contador oculto | open | — |
| IN-06 | info | Falla de red durante `webpay.commit` escapa como 500 | open | — |

## Leyenda

- `open` — sin triage aún (los IN-* pueden resolverse con `/gsd:code-review 3 --fix --all` o en el ciclo de gaps).
- `fixed` — corregido por gsd-code-fixer; ver `03-REVIEW-FIX.md` para el detalle del cambio y el commit.
- Para diferir un hallazgo a propósito: cambia `open` por `deferred` y anota la razón en la columna Source.
