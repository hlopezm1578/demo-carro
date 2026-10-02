---
phase: "05"
slug: "05-despliegue-y-cierre-de-la-guia"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-02"
---

# Phase 05 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

> **Contexto de fase (D-17/D-73):** fase writing-only — el repo es guide-only (sin código de
> aplicación) y el deploy no se ejecuta en este proyecto. La "implementación" verificada es el
> corpus documental (ADRs 019/020, docs 06/07/08, guías 16-18, READMEs): las mitigaciones son
> disciplina documental que el alumno ejecutará en sus cuentas.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| ADR-019/020 (fuente de verdad) → doc 07, guías 16-18 y taller del alumno | La decisión firmada es lo que las guías enseñarán y el alumno ejecutará en SUS cuentas | Comandos, valores de dashboard, cifras de free tier |
| Docs oficiales de plataforma (evidencia) → ADR | La evidencia es documental (D-73): cita mal atribuida = afirmación sin respaldo | Cifras y límites citados con URL + "a la fecha" |
| Guías 16/17 → dashboards de plataforma del alumno | El alumno pega valores en dashboards reales con SUS cuentas | CORS_ORIGINS, SECRET_KEY, VITE_API_URL (placeholders) |
| .env / secrets del taller → bloques de guía | Los bloques que la guía enseña deben ser placeholders reproducibles | Credenciales (nunca en el repo) |
| Webpay integración (retorno público) → API desplegada del alumno | El endpoint del retorno es público en la URL real | token_ws / commit del token (estado OUR-side) |
| REQUIREMENTS v2 / ADR-018 → docs 06 y 08 | Los docs citan IDs y casos reales del corpus | Trazabilidad de mantenimiento |
| Tablas de estado de los READMEs → corpus real | Las tablas son la portada del producto: cantar completo sin corpus es drift | Conteos (18 guías / 20 ADRs) |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-05-01 | Tampering | cifras de free tier firmadas sin fuente en ADR-019/020 y doc 07 | high | mitigate | Disciplina D-68: verify gate exige "a la fecha" + URLs render.com/vercel.com; prohibición de cifras desnudas | closed |
| T-05-02 | Spoofing | SECRET_KEY de producción heredada del .env de dev | high | mitigate | ADR-019 firma la regla key nueva por entorno (Pitfall 9) con `secrets.token_hex(32)`; doc 07:160 la repite | closed |
| T-05-03 | Information Disclosure | secretos literales pegados en los documentos nuevos | medium | mitigate | Placeholders + comando generador; cero `gsk_`/valores reales (grep limpio) | closed |
| T-05-04 | Information Disclosure | wording que presenta runtime propio no ejecutado como verificado | medium | mitigate | Gate negativo: cero "verificamos en producción/lo probamos/lo deployamos" en ADR-019/020, doc 07, guia-18 (grep limpio) | closed |
| T-05-SC (05-01) | Tampering | installs de paquetes | high | mitigate | Fase docs-only (D-17): cero installs; audit del research declara sin gate requerido | closed |
| T-05-05 | Tampering | docs/06 presenta el método con garantías que las verificaciones no dan (overclaim) | medium | mitigate | Cada fila de la tabla método ↔ defensa cita su Origen real (docs/06:52,119); IDs reales de REQUIREMENTS | closed |
| T-05-06 | Information Disclosure | los docs revelan datos del taller (emails/keys reales) como ejemplos | medium | mitigate | Placeholders de las guías; cero emails/keys del taller en docs 06/07/08 (grep limpio) | closed |
| T-05-SC (05-02) | Tampering | installs de paquetes | high | mitigate | Fase docs-only (D-17): cero installs | closed |
| T-05-16 | Elevation of Privilege | CORS comodín enseñado "para que funcione en producción" | high | mitigate | guia-16:166,212 enseña `CORS_ORIGINS` como JSON array explícito `["https://<tu-proyecto>.vercel.app"]`; patrón comodín ausente | closed |
| T-05-07 | Information Disclosure | secretos que cruzan al bundle del frontend (VITE_*) | high | mitigate | guia-17 solo enseña `VITE_API_URL` (URL pública); grep del build `GROQ_API_KEY` extendido (AIAS-03, ×5 menciones) | closed |
| T-05-08 | Tampering | vercel.json no commiteado o preset Other → rewrite no aplica → 404 silencioso | high | mitigate | guia-17 Paso 1: rewrite ANTES del import con `git add frontend/vercel.json` + mini-verificación `git log` (guia-17:31-68) | closed |
| T-05-09 | Information Disclosure | .env del alumno pusheado a GitHub en el paso 0 | high | mitigate | guia-16 Paso 0: "¿qué NO debe subir?" + mini-verificación `git status` sin backend/.env ni *.db (guia-16:41-74) | closed |
| T-05-SC (05-03) | Tampering | installs de paquetes | high | mitigate | Fase docs-only (D-17): cero installs | closed |
| T-05-10 | Tampering | retorno forjado/manipulado contra la URL pública con params falsos | high | mitigate | guia-18 reafirma ADR-012: el endpoint JAMÁS confía en el navegador; estado real por commit del token (PAY-03), idempotencia OUR-side | closed |
| T-05-11 | Information Disclosure | /docs y /redoc públicos en la URL de la API | medium | accept | Decisión pedagógica deliberada, declarada en ADR-019:99-102 ("en un producto real se desactivaría"); fila contrato ↔ /docs de la Gran verificación lo exige accesible | closed (accepted risk) |
| T-05-12 | Tampering | la tabla promete resultados que el proyecto no verificó, presentados como probados | high | mitigate | Nota D-73 "la corres TÚ" en guia-18; gate negativo cero "verificamos/aprobamos la gran verificación"; esperados heredados de 03-SPIKE-RETORNO/03-UAT | closed |
| T-05-SC (05-04) | Tampering | installs de paquetes | high | mitigate | Fase docs-only (D-17): cero installs | closed |
| T-05-13 | Tampering | tablas de estado marcadas ✅ Listo con corpus ausente o desincronizado | high | mitigate | Gate de conteos ANTES del commit de estado; READMEs con conteos reales (18 guías/20 ADRs verificados a HEAD por 05-VERIFICATION) | closed |
| T-05-14 | Tampering | cadena Siguiente con eslabones sueltos (15→16→17→18→docs) | medium | mitigate | Gate grep de los 4 eslabones por nombre exacto; verificado: guia-15:705→16, guia-16:420→17, guia-17:379→18, guia-18:469→docs | closed |
| T-05-15 | Tampering | este plan edita checkboxes de REQUIREMENTS/ROADMAP que pertenecen a la transición | medium | mitigate | Prohibición explícita; files_modified del plan = solo 3 READMEs; el Status de fase quedó "In Progress" (la transición es la dueña — misma convención que el cierre de fase 4) | closed |
| T-05-SC (05-05) | Tampering | installs de paquetes | high | mitigate | Fase docs-only (D-17): cero installs | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-05-01 | T-05-11 | `/docs` y `/redoc` públicos en la URL desplegada de la API: decisión pedagógica de la serie (la fila contrato ↔ /docs de la Gran verificación final lo exige accesible al alumno). En un producto real se desactivaría en producción; ASVS L1 de aula con datos sandbox | ADR-019 (Negativas honestas, l.99-102) | 2026-10-01 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-02 | 21 | 21 | 0 | ZCode (verify-work verify:post hook, L1 grep-depth — short-circuit ASVS L1: register authored at plan time, threats_open 0) |

> Nota de alcance del registro: los 5 planes declararon su propio T-05-SC (cero installs,
> docs-only D-17) — se listan por plan de origen porque comparten ID pero son instancias
> independientes del mismo control. Total: 16 amenazas únicas + 5 instancias SC.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-02 (L1 short-circuit: todos los controles verificados a grep-depth contra el corpus a HEAD; evidencia citada por línea en el registro)
