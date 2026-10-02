---
phase: "01"
slug: "fundaciones-de-dos-tiers-y-cat-logo"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-29"
---

# Phase 01 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

> **Naturaleza de la fase (D-17):** fase de documentación — el código vive dentro de las
> guías (`docs/05_desarrollo/`), nada se ejecuta en este repo. La mitigación se verifica
> en el texto de las guías (L1) y en la ejecución runtime delegada en `D:/Repos/maura-uat`
> (UAT 4/4 PASS, 2026-09-29).

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| navegador/SPA → API (/api/productos) | Input no confiable: query params familia/precio_min/precio_max y path param producto_id cruzan aquí (guia-04) | query params / path param — públicos, validados |
| seed → SQLite | Escritura local confiable (script del repo, sin input externo) (guia-03) | datos ficticios de Maura |
| guía → máquina del alumno | Los comandos y bloques que el alumno copia: superficie de confianza del material (guia-01..04) | comandos shell / código — auditados |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-01-01 | Tampering | GET /api/productos (filtros) | medium | mitigate | SQLAlchemy select parameterizado + familia como Enum de Pydantic (guia-04 Paso 2/3); verificado en runtime maura-uat | closed |
| T-01-02 | DoS/Tampering | query params (rangos absurdos, familia inválida) | low | mitigate | Validación declarativa Query(ge=0) + Enum → 422 automático (guia-04 Paso 3); /docs documenta el 422 | closed |
| T-01-03 | Information Disclosure | CORS en app/main.py | medium | mitigate | allow_origins lista explícita desde Settings, jamás comodín (guia-01:287,388 + sección "el error que este archivo evita") | closed |
| T-01-04 | Information Disclosure | docs/01..03 | low | mitigate | Solo datos ficticios de Maura; grep L1 sin secretos con valor en docs/ | closed |
| T-01-11 | Information Disclosure | README.md y docs/04_arquitectura/ | medium | mitigate | Cero secretos ni API keys (grep L1 vacío); credenciales Webpay/Gemini declaradas fuera de alcance hasta fases 3/4, como variables de entorno | closed |
| T-01-12 | Tampering | ADRs con recomendaciones técnicas | medium | mitigate | Ningún ADR recomienda librerías vetadas como opción elegida (grep L1: solo menciones como descartadas); versiones citadas contra el stack autoritativo | closed |
| T-01-13 | Tampering | comandos y bloques de código de guia-01/02 | high | mitigate | Todo comando del Package Legitimacy Audit (01-RESEARCH); bloques anclados en implementación verificada; sin curl-bash de terceros; ejecutados con éxito en maura-uat (refix 2026-09-29) | closed |
| T-01-14 | Information Disclosure | ejemplos de código de las guías | medium | mitigate | Settings con defaults de desarrollo sin secretos; pedagogía explícita "los secretos jamás van en el código" (guia-01 Paso 4) | closed |
| T-01-15 | Tampering | deriva contrato ↔ guía | medium | mitigate | Gran verificación final fila 11: /docs comparado UNO A UNO contra contrato_api.yaml (guia-04:945-952); re-ejecutada 2026-09-29 con solo desvíos ya advertidos (WR-01/02/08, disposition open consciente) | closed |
| T-01-16 | Information Disclosure / Spoofing | paso de descarga de fotos | medium | mitigate | Solo fotos stock licencia libre (Unsplash/Pexels, guia-04 Paso 4); única sección con URLs de terceros; sin datos personales | closed |
| T-01-17 | Tampering | comandos y bloques de guia-03/04 | high | mitigate | Bloques narran implementación verificada; comandos auditados; repositorio no ejecuta nada (D-17); seed y catálogo re-ejecutados OK en maura-uat | closed |
| T-01-18 | Tampering | deriva guía ↔ contrato al editar el router (G-01-4) | medium | mitigate | description del 404 copiada palabra por palabra del contrato (contrato_api.yaml:199); contrato intacto (git limpio); /docs runtime muestra "Producto inexistente (o inactivo)" con schema Error | closed |
| T-01-19 | Tampering | reescritura de guia-01 (G-01-1) | low | mitigate | Fix solo prosa existente (revisar → crear); bloque .gitignore byte-idéntico; re-ejecución 2026-09-29 en maura-uat/refix con el contenido literal de la guía | closed |
| T-01-SC (01-01) | Tampering | installs pypi (uv add) | high | mitigate | Package Legitimacy Audit de 01-RESEARCH.md: todos Approved; versiones confirmadas contra pypi.org; instalados OK en runtime | closed |
| T-01-SC (01-02) | Tampering | installs | high | accept | Plan de documentación pura: no instala dependencias; el audit de RESEARCH gobierna los planes con installs | closed |
| T-01-SC (01-03) | Tampering | installs npm/pip | high | accept | Documentación pura; comandos documentados ya auditados y verificados por ejecución en 01-01 | closed |
| T-01-SC (01-04) | Tampering | installs npm/pip | high | accept | Documentación pura (D-17); sin cambios de paquetes | closed |
| T-01-SC (01-05) | Tampering | installs npm/pip | high | accept | Documentación pura; comandos auditados y ejecutados con éxito antes de la corrección de alcance | closed |
| T-01-SC (01-06) | Tampering | installs npm/pip | high | accept | Fix de documentación; sin cambios de paquetes ni ejecución de código del repo | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-01-1 | T-01-SC (01-02..01-06) | Planes de documentación pura (D-17): no instalan dependencias; los comandos npm/uv que las guías enseñan están cubiertos por el Package Legitimacy Audit de 01-RESEARCH.md (plan 01-01, disposition mitigate) | plan-time (plans 01-02..01-06) | 2026-09-28 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-29 | 19 | 19 | 0 | agent (user-delegated /gsd-secure-phase, L1 grep-depth, ASVS 1) |

Metodología: registro autorizado a tiempo de planificación (los 6 PLANs con bloque
`<threat_model>`), clasificación L1 (grep) contra `docs/` + verificación runtime delegada
en `D:/Repos/maura-uat` (UAT 01: 4/4 PASS). ASVS 1 + `register_authored_at_plan_time: true`
+ `threats_open: 0` → sin spawn de auditor profundo (short-circuit del workflow).

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-29
