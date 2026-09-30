---
phase: "02"
slug: "cuentas-de-cliente-y-carro-persistente"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-30"
---

# Phase 02 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.
> Fase guide-only (ADR-008/D-17): la "implementación" son las guías de
> docs/05_desarrollo; la evidencia runtime proviene del UAT delegado ejecutado
> en el taller D:/Repos/maura-uat (2026-09-30, sesión 02-UAT.md).

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| (ninguna en runtime del repo) | Repo guide-only: nada se ejecuta ni instala aquí | — |
| contrato → guías/máquina del alumno | El contrato 0.2.0 define el esquema de seguridad que las guías enseñan | Esquemas, códigos de error, securitySchemes |
| guía → máquina del alumno | Comandos de instalación, generación del secreto y bloques de código | Paquetes pip/npm, SECRET_KEY, credenciales demo |
| navegador del alumno → su API | Token/credenciales del flujo didáctico JWT | Bearer token, form OAuth2, carro en localStorage |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-02-01 | Tampering | contrato 0.2.0 (deriva vs guías) | high | mitigate | Contrato aprobado antes (D-15) + fila contrato↔/docs de la Gran verificación (ADR-007). Evidencia runtime: 7/7 paths exactos, códigos y schemas calzados; /docs sirve 0.2.0 (fix del hallazgo version aplicado en ambos lugares) | closed |
| T-02-02 | Information Disclosure | schemas UsuarioPublico/RegistroCreate | high | mitigate | UsuarioPublico expone solo id/email/rol. Evidencia: required=[id,email,rol] sin hashed_password en openapi.json; respuesta 201 del registro sin hash (runtime) | closed |
| T-02-03 | Spoofing | securitySchemes del contrato | medium | mitigate | bearerAuth type http + scheme bearer + bearerFormat JWT (contrato §components). En /docs el esquema equivalente OAuth2PasswordBearer habilita el botón Authorize — probado admin→200 / clienta→403 | closed |
| T-02-04 | Information Disclosure | ADR-009 (venta honesta del localStorage) | medium | mitigate | D-21: desventaja XSS dicha en tabla de opciones (l.22) y "Negativas (honestas)" (l.56) del ADR-009 — verificado P1 del UAT | closed |
| T-02-05 | Information Disclosure | RNs de seguridad del doc 02 | medium | mitigate | RN-05 (mínimo 8 sin composición, NIST), RN-06 (401 genérico + 409 claro), RN-07 (hash confinado), RNF-05 (secreto por entorno) documentadas en docs/02_requerimientos.md — leídas en el UAT (P2) | closed |
| T-02-06 | Spoofing | regla de contraseña (RN-05, D-25) | low | mitigate | RN-05 sin composición obligatoria citando NIST; guia-05/06 enseñan exactamente eso; runtime: login con clave corta responde 401 (no 422) | closed |
| T-02-07 | Information Disclosure | login de guia-05 (enumeración) | high | mitigate | 401 SIEMPRE genérico + hash dummy (tiempo constante). Evidencia runtime (UAT P4): email inexistente y clave mala responden byte a byte idéntico 401 {'detail': 'Credenciales incorrectas'} | closed |
| T-02-08 | Information Disclosure | schemas de usuarios en guia-05 | high | mitigate | Ningún schema con hashed_password (RN-07); response_model UsuarioPublico en registro/perfil; perfil autenticado devuelve solo id/email/rol (runtime) | closed |
| T-02-09 | Information Disclosure | secreto y credenciales demo en guías | high | mitigate | Secreto via secrets.token_hex(32) (D-12), secret_key sin default (fail-fast verificado runtime: ValidationError), .env.example solo placeholders, 0 literales en guías 05/06 (grep UAT P3) | closed |
| T-02-10 | Elevation of Privilege | claim de rol (AUTH-03) | high | mitigate | Rol viaja en el token desde el primer login (decode offline: claim rol presente); get_current_admin valida EN EL SERVIDOR. Evidencia runtime: admin 200 {'productos':12,'familias':4} vs clienta 403 (consola y Authorize de /docs) | closed |
| T-02-11 | Tampering | interceptor 401 (D-22) | medium | mitigate | Interceptor limpia sesión y redirige con aviso; JAMÁS dispara en el propio login (sinAuth). Evidencia runtime: expulsión a /login?expirada=1 con aviso ámbar + caso borde WR-02 (token viejo en store + credenciales malas → banner en card, sin expulsión) | closed |
| T-02-12 | Tampering | precios del carro (D-27) | high | mitigate | Store guarda SOLO {producto_id, cantidad}. Evidencia runtime: maura-carro = {"state":{"items":[{"producto_id":1,"cantidad":2}]},"version":0} — sin nombre ni precio; precios siempre hidratados de la API | closed |
| T-02-13 | Elevation of Privilege | guard de /checkout | medium | mitigate | Guia-06 p5 y guia-08 p2 + error 1 dicen explícito "el guard es UX, no seguridad (D-32)" — verificado P6 del UAT | closed |
| T-02-14 | Tampering | cantidades vs stock en pantalla (D-30) | medium | mitigate | Math.min(cantidad, stock) en stepper/total + CTA deshabilitado al tope. Evidencia runtime: cantidad 5 sembrada → fila/total cobran 2, write-back al store, badge coherente | closed |
| T-02-15 | Information Disclosure | fila degradada por 404 (Pitfall 8) | low | mitigate | Hidratación tolerante con ApiError.status===404: "Este aroma ya no está disponible" sin detalles del error (runtime verificado con producto 999) | closed |
| T-02-16 | Tampering | estado de los README | medium | mitigate | README.md l.42 y docs/README.md l.19: fila 5 "🚧 Parcial (guías 1-8 listas; continúa en fases 3+)" — exactamente lo que existe (verificado P7) | closed |
| T-02-17 | Tampering | invariante guide-only (D-17/ADR-008) | high | mitigate | Repo sin backend/ ni frontend/ (ls raíz: AGENTS.md, README.md, docs) — el código de aplicación vive solo en las guías y en el taller externo | closed |
| T-02-SC (02-01) | Tampering | installs narrados (pyjwt, pwdlib, python-multipart, zustand) | high | mitigate | Package Legitimacy Audit de 02-RESEARCH (zustand OK; pyjwt/pwdlib cross-check contra tutorial oficial); el taller instaló EXACTAMENTE esos 4 (pyjwt 2.15.1, pwdlib 0.3.1, python-multipart, zustand 5.0.15) | closed |
| T-02-SC (02-02) | Tampering | installs npm/pip | high | accept | Plan documental: no instala ni narra installs — ver Accepted Risks Log | closed |
| T-02-SC (02-04) | Tampering | installs npm/pip | high | accept | guia-07/08 no narran installs nuevos (zustand ya auditado) — ver Accepted Risks Log | closed |
| T-02-SC (02-05) | Tampering | installs npm/pip | high | accept | Plan de índices/enlaces: no instala nada — ver Accepted Risks Log | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on (high) count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-02-1 | T-02-SC (02-02/02-04/02-05) | Planes documentales sin installs: el gate de legitimidad de paquetes vive en los planes que escriben guías (02-01/02-03, ambos mitigados con el audit de 02-RESEARCH) | plan-time (02-02/02-04/02-05 PLAN threat_model) | 2026-09-29 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-30 | 21 | 21 | 0 | agent (verify-work verify:post, L1 + evidencia runtime del UAT delegado en maura-uat) |

Short-circuit aplicado (workflow §3): threats_open 0 + register_authored_at_plan_time true + asvs_level 1 → clasificación L1 con evidencia grep/runtime, sin auditor adicional.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-30 (verify-work 02, sesión UAT delegada completa)
