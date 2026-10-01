# Phase 4 — Review Disposition

**Phase:** 4 — Panel de administración y asistente IA
**Source:** [04-REVIEW.md](04-REVIEW.md) (status: issues_found → fixer corrida 2026-10-01)
**Counts:** 1 Critical / 3 Warning / 4 Info — **6 fixed, 2 open**

| Finding | Severity | File | Status | Resolution |
|---------|----------|------|--------|------------|
| CR-01 Router admin monta productos sin segmento `/productos` (contrato 0.4.0 desviado) | Critical | guia-12-panel-backend.md | **fixed** | `9f2411b` — decoradores `/productos`, `/productos/{producto_id}`, `/productos/{producto_id}/activo` + regla prefijo+segmento enseñada; pedidos/métricas ya montaban bien |
| WR-01 Mini-verificación espera `dict_keys([200, 422, 429, 503])` pero route.responses no incluye el 200 | Warning | guia-14-asistente-backend.md | **fixed** | `630ccb2` — espera `dict_keys([422, 429, 503])` + explicación del 200 en el OpenAPI |
| WR-02 `historial[].texto` sin tope en endpoint público (RN-16 incompleta) | Warning | guia-14 + contrato_api.yaml | **fixed** | `f4f2f0e` — `Field(max_length=500)` + `maxLength: 500` en el contrato, prosa y 422 en espejo |
| WR-03 Mini-verificación del preflight no puede fallar (CORS responde antes del routing) | Warning | guia-12-panel-backend.md | **fixed** | `b284377` — complementada con GET sin token esperando 401 |
| IN-01 Espejo 422 del editor cubre 5/7 campos | Info | guia-13-panel-spa.md | **open** | Deferido al usuario: decisión editorial sobre copys locked del UI-SPEC vs narrativa |
| IN-02 Guard de degradación no cubre `GEMINI_API_KEY=` vacía | Info | guia-14-asistente-backend.md | **fixed** | `f4f57ba` — `if not settings.gemini_api_key:` (cubre None y "") |
| IN-03 ADR-017 cita auto-pickup del SDK donde la guía enseña a no confiar | Info | adr/017-*.md | **open** | Deferido al usuario: decisión editorial de redacción del ADR |
| IN-04 `Metricas.top_5` sin `max_length=5` espejo del `maxItems` | Info | guia-12-panel-backend.md | **fixed** | `2f152e2` — `Field(max_length=5)` declarativo |

**Verificación post-fix:** todas las cadenas `<verify>` de los planes re-ejecutadas en verde (`contrato04-ok`, `adrs04-ok`, `readme-arq04-ok`, `g12-ok`, `g13-ok`, `g14-ok`, `g15-ok`); AST-parse de los bloques Python (7/7 rutas admin resuelven a los paths del contrato) y YAML-parse del contrato. Detalle por fix: [04-REVIEW-FIX.md](04-REVIEW-FIX.md).
