---
phase: "03"
slug: "checkout-webpay-y-rdenes"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-30"
---

# Phase 03 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| navegador → Webpay integración | Navegación real con formulario hosted de Transbank y tarjeta de prueba oficial | form POST con token_ws (navegación, no fetch) |
| Webpay → API (retorno) | El retorno del navegador externo llega SIN Bearer al endpoint público `/api/pago/retorno` (ADR-012) | token_ws / TBK_TOKEN / TBK_ID_SESION / TBK_ORDEN_COMPRA por query o form |
| SPA → API (checkout/pedidos) | fetch con Bearer — la clienta autenticada inicia el pago y lee SU historial | items {producto_id, cantidad} sin precios; OrdenLista/Detalle con snapshot |
| maura-uat → este repo | Evidencia runtime del spike y del UAT delegado cruza al repo guide-only (D-17) | Documentos de hallazgos con tokens TRUNCADOS; jamás código ejecutable |
| guía → máquina del alumno | Comandos `uv add`, tarjeta de prueba y bloques de código | Material educativo; el repo no ejecuta installs (D-17) |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-03-01 | Information Disclosure | tokens de Webpay en evidencia del spike | medium | mitigate | 03-SPIKE-RETORNO.md registra tokens truncados (prefijo+len); grep de 64-hex sobre el documento: 0 coincidencias | closed |
| T-03-02 | Tampering | código runtime commiteado en demo-carro (violación D-17) | high | mitigate | `git ls-files -- backend frontend` = vacío (re-verificado 2026-09-30); el código vive solo en maura-uat | closed |
| T-03-03 | Tampering | manipulación de precios/total desde el cliente (CART-03) | high | mitigate | Contrato: CheckoutCreate properties = ['items'] (sin precio, YAML-parseado); runtime UAT: `"precio":1` inyectado ignorado, total 17.980 = 2×8.990 catálogo | closed |
| T-03-04 | Information Disclosure | enumeración de pedidos ajenos vía numero secuencial | high | mitigate | 404 uniforme no-existe/no-es-tuya (runtime: token admin → 404 + lista vacía; token clienta → solo las suyas); lista filtra por usuario_id del token | closed |
| T-03-05 | Spoofing | retorno público forjado (token inventado) | medium | mitigate | Runtime UAT: token inventado → 302 estado=error, orden intocada; solo un commit REAL de Webpay transiciona (criterio doble evaluado en servidor) | closed |
| T-03-06 | Tampering | especificación del retorno contradiciendo la evidencia | high | mitigate | docs/02 menciona TBK_TOKEN (2 menciones); reglas por PRESENCIA de params jamás por método; aceptada por el dueño como canónica (03-UAT.md test 2, 2026-09-30) | closed |
| T-03-07 | Tampering | doble pago/doble descuento por repetición del retorno (PAY-03) | high | mitigate | Guard ya-PAID UPDATE condicional con rowcount + descuento/transición en UNA transacción; runtime: F5 sobre voucher pagado sin side effects (paid, stock intacto) | closed |
| T-03-08 | Tampering | oversell por carrera concurrente (ORDR-02) | high | mitigate | UPDATE condicional `WHERE stock >= cantidad` + rowcount; runtime carrera.py: exactamente un PAID + un REJECTED + stock 0 | closed |
| T-03-09 | Tampering | commit de flujo anulado → TransactionCommitError → 500 | medium | mitigate | Commit SOLO en rama token_ws-solo; excepción tipada atrapada en el wrapper (→ None → 302 error); runtime: anulado real y token inventado sin 500 | closed |
| T-03-10 | Information Disclosure | token_ws/TBK_*/card_detail completos en logs | medium | mitigate | La guía loguea flujo y numero, jamás tokens (grep: sin print/log de token en guia-09); card_detail queda en el backend | closed |
| T-03-11 | Tampering | XSS al construir el form de Webpay | medium | mitigate | document.createElement con values tipados; única mención de innerHTML en guia-10 es el ejemplo ❌ del anti-patrón (sección "El error que este archivo evita") | closed |
| T-03-12 | Information Disclosure | pedidos ajenos visibles en el historial (ORDR-01) | high | mitigate | Lista filtra por usuario_id del token verificado; detalle por numero con ownership 404; runtime: clienta ve solo sus 9 órdenes, MAURA-999999 → 404 | closed |
| T-03-13 | Tampering | Gran verificación final con datos incorrectos | medium | mitigate | Tarjeta oficial verbatim (3 menciones) y 603 s cronometrados presentes en guia-11; corrida runtime del UAT los usó con éxito | closed |
| T-03-SC | Tampering | supply chain: install pip narrado (transbank-sdk) | high | mitigate | Package Legitimacy Audit en 03-RESEARCH.md (SUS por artefacto PyPI unknown-downloads, aprobado por cross-check autoritativo: SDK oficial de TransbankDevelopers, PyPI+GitHub); las guías instalan EXACTAMENTE transbank-sdk; este repo no ejecuta installs (D-17) | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|

No accepted risks.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-30 | 14 | 14 | 0 | agent (inline secure-phase, /gsd-verify-work 3 verify:post hook) |

*Clasificación L1 (grep) reforzada con evidencia runtime del UAT delegado del mismo día (flujos reales contra Webpay integración en maura-uat) para T-03-03/04/05/07/08/09/12. Short-circuit ASVS 1 aplicado (threats_open 0 + register a la hora del plan + asvs 1).*

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-30
