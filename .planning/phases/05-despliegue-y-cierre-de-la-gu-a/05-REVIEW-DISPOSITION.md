# Phase 5 — Code Review Disposition

**Review:** `05-REVIEW.md` (2026-10-01, depth standard, 13 files)
**Counts:** 1 critical, 4 warning, 3 info (total 8)

| Finding | Severity | Title | Disposition |
|---------|----------|-------|-------------|
| CR-01 | critical | `Select-String -Path dist\*` no es recursivo — el grep del build PowerShell no escanea `dist/assets/*.js` (control positivo siempre falla; AIAS-03 falso negativo) — guia-17:226-231, guia-18:297, heredado de guia-15:530 | fixed (regla persistida de bugs de guía: fix aplicado por gsd-code-fixer en guia-15/17/18) |
| WR-01 | warning | `docs/06_pruebas.md:70` inventa el marcador `[-]` del seed (solo existen `[+]`/`[=]`, guia-03:246-287) y mezcla corridas primera/segunda | open |
| WR-02 | warning | Copy del empty state del historial: "Todavía no hay pedidos" (panel admin) vs real "Todavía no tienes pedidos" (guia-11:143) — guia-18:268, ADR-020:85, doc 07:103 | open |
| WR-03 | warning | "SIEMPRE revive" la capa build afirmado como hecho; la revivencia es el supuesto A5 del research (interpretación registrada), no un hecho citado — ADR-020/doc 07/guia-16 | open |
| WR-04 | warning | `SECRET_KEY`: guia-16:174-179 usa `python -c ...` sin `uv run` ni directorio `backend/` (el comando de siempre es `uv run python -c ...` desde `backend/`, guia-05:86) | open |
| IN-01 | info | guia-16:146 dice que las env vars viven en `config.py` "desde las guías 5 y 9"; `cors_origins` nació en guia-01:203 | open |
| IN-02 | info | Gramática en `docs/06_pruebas.md:107` ("y no la corrido") | open |
| IN-03 | info | guia-18:81 rotula `/pago/resultado` con "guard de sesión" cuando la ruta es deliberadamente pública (guia-10:212-225) | open |
