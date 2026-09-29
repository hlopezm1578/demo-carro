---
phase: 02
review: 02-REVIEW.md
titles: json
fix_log: 02-REVIEW-FIX.md
findings:
  - id: CR-01
    severity: critical
    disposition: fixed
    title: "Routers de guia-05 importan `Error` desde `app.schemas.usuario` (no existe ahí) — ImportError al include_router"
    fix_commit: a1983ff
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "Total aritmético erróneo $26.980 → $26.970 (repetido en 03_diseno ×2, guia-07, guia-08)"
    fix_commit: b6474a7
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "Interceptor 401 podía disparar dentro del login con token viejo — login ahora viaja sinAuth"
    fix_commit: 6fcad69
  - id: WR-03
    severity: warning
    disposition: fixed
    title: "Badge contaba unidades sin tapar al stock — write-back al hidratar alinea badge/filas/total"
    fix_commit: d22e080
  - id: WR-04
    severity: warning
    disposition: fixed
    title: "`mensaje = cuerpo.detail` renderiza \"[object Object]\" en el 422 — normalización string/array (cierra WR-04 de fase 1)"
    fix_commit: f3cf4d4
  - id: WR-05
    severity: warning
    disposition: fixed
    title: "Contrato y guia-05 documentaban el 422 del registro con detail string — desvío documentado (detail es array)"
    fix_commit: b8db43b
  - id: WR-06
    severity: warning
    disposition: fixed
    title: "guia-07 re-listaba imports de guia-04 — copiar el bloque completo redeclaraba (TS)"
    fix_commit: 5fe42d9
  - id: WR-07
    severity: warning
    disposition: fixed
    title: "\"los 8 paths\" en guia-05 — el contrato tiene 7"
    fix_commit: e9c2491
  - id: IN-01
    severity: info
    disposition: open
    title: "Comentarios citan `authHeaders()`, función inexistente en el código final (guia-06)"
  - id: IN-02
    severity: info
    disposition: open
    title: "Typos: \"nieza\", \"EXPLÍPITA\" (en código copiable), \"consuela\", \"se revuelve\""
  - id: IN-03
    severity: info
    disposition: open
    title: "Snippets de rutas re-listan rutas existentes (guia-07/guia-08) — duplicados silenciosos"
  - id: IN-04
    severity: info
    disposition: open
    title: "RNF-06 nombra `localStorage` en el doc de QUÉ mientras 03_diseno difiere el mecanismo a la fase 4"
  - id: IN-05
    severity: info
    disposition: open
    title: "README de arquitectura enlaza pwdlib a ADR-009/011, que no lo mencionan"
  - id: IN-06
    severity: info
    disposition: open
    title: "Contrato declara `format: email` en el `username` del login — el form OAuth2 no lo aplica"
  - id: IN-07
    severity: info
    disposition: open
    title: "`int(user_id)` fuera del try en guia-05 — sub firmado no numérico daría 500 (no explotable sin secreto)"
---

# Review Disposition — Phase 02

**Review:** 02-REVIEW.md (2026-09-29) · **Fix log:** 02-REVIEW-FIX.md · 8/15 fixed (1 critical + 7 warnings, commits a1983ff..e9c2491), 7 info open (cosmetic/consistency, none blocks the phase goal).

Los 7 findings info quedan abiertos por decisión del flujo `--fix` default scope (Critical + Warning): son typos y notas de consistencia sin impacto en la construción del alumno; se absorben naturalmente en las fases 3+ que vuelven a tocar estas guías o cierran con el UAT delegado en maura-uat.
