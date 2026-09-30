---
phase: 02-cuentas-de-cliente-y-carro-persistente
verified: 2026-09-30T12:10:00Z
status: passed
score: 45/45 must-haves verified
covered_files:
  - .planning/ROADMAP.md
  - .planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-01-PLAN.md
  - .planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-01-SUMMARY.md
  - .planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-02-PLAN.md
  - .planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-02-SUMMARY.md
  - .planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-03-PLAN.md
  - .planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-03-SUMMARY.md
  - .planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-04-PLAN.md
  - .planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-04-SUMMARY.md
  - .planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-05-PLAN.md
  - .planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-05-SUMMARY.md
  - .planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-REVIEW-FIX.md
  - .planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-SECURITY.md
  - .planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-UAT.md
  - .planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-UI-REVIEW.md
  - README.md
  - docs/README.md
  - docs/02_requerimientos.md
  - docs/03_diseno.md
  - docs/04_arquitectura/README.md
  - docs/04_arquitectura/adr/009-jwt-larga-vida-localstorage.md
  - docs/04_arquitectura/adr/010-carro-client-side.md
  - docs/04_arquitectura/adr/011-roles-desde-el-primer-token.md
  - docs/04_arquitectura/contrato_api.yaml
  - docs/05_desarrollo/README.md
  - docs/05_desarrollo/guia-05-cuentas-backend.md
  - docs/05_desarrollo/guia-06-sesion-frontend.md
  - docs/05_desarrollo/guia-07-carro.md
  - docs/05_desarrollo/guia-08-checkout.md
covered_digest: "v2:sha256:5d64407124fe9011864a28d399ad3443649bca4d4abad60553ef0920c074af4c"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: human_needed
  previous_score: 41/45
  gaps_closed:
    - "SC1: cuenta + login + sesión entre recargas — runtime ejecutado en UAT delegado (guia-05/06 construidas, F5 sin parpadeo, token exp−iat=604800, pestaña nueva conserva sesión+carro+badge)"
    - "SC2: claim de rol desde el primer token; admin 200 / clienta 403 — runtime (decodificación offline del token, /api/admin/estado 200 admin / 403 clienta, Authorize en /docs probado con ambos roles)"
    - "SC3: carro agregar/editar/vaciar + persistencia full-page load — runtime (merge, tope, write-back WR-03 con localStorage sembrado cantidad 5→2, badge unidades 0→1→2→4, F5, fila degradada 999)"
    - "SC4: checkout exige sesión con retorno — runtime (sin sesión → /login → vuelve AL checkout via returnTo D-32; token corrupto → expulsión con aviso ámbar)"
    - "Runtime de WR-02 (login viaja sinAuth, interceptor jamás dispara en el 401 del login — incluido el caso borde con token viejo en maura-auth) y WR-03 (write-back del tapado al stock)"
    - "Revisión de las 7 prohibiciones judgment-tier — ratificadas por revisión delegada con muestreo independiente (02-UAT.md test 3)"
    - "Formato del goal: ROADMAP.md ahora lleva la User Story canónica (commit cca863e; user-story.validate → true)"
  gaps_remaining: []
  regressions: []
---

# Phase 2: Cuentas de cliente y carro persistente Verification Report

**Phase Goal (ROADMAP, User Story canónica):** As a visitante de la tienda, I want to crear una cuenta, iniciar sesión con un token que persiste entre recargas y armar un carro que sobreviva los full-page loads hasta un checkout que me exige sesión, so that la tienda me reconoce en cada visita y mi compra queda lista para el pago real que llega con Webpay en la fase 3.
**Verified:** 2026-09-30T12:10:00Z
**Status:** passed
**Re-verification:** Yes — tras cierre del UAT delegado (previous: human_needed 41/45)

## Scope frame (D-17, heredado)

Repositorio **guide-only** (D-17/ADR-008): los entregables son DOCUMENTOS bajo `docs/`. Verificación por contenido (greps, `yaml.safe_load`, `ast.parse`, conteos, diffs git) + evidencia runtime del taller delegado `D:/Repos/maura-uat` (canal user-delegado sancionado en AGENTS.md). Nada se ejecuta en este repo.

**Qué cambió desde la verificación previa (2026-09-29T18:26:06Z):** guia-05 (version bump 0.2.0, commit 9cbd4af, +10 líneas), guia-06/07/08 (3 fixes del UI-REVIEW, commit 5b1b718, 6 líneas netas), ROADMAP.md (goal user story, cca863e), y artefactos de fase nuevos (02-UAT.md, 02-SECURITY.md, 02-UI-REVIEW.md, 02-UI-SPEC.md, COVERAGE.md). docs/02, docs/03, docs/04 y los 3 READMEs: **0 commits** desde la verificación previa — sus verdades sostienen por regresión.

## MVP Mode — User Flow Coverage

`user-story.validate --story <goal>` → **true** (la discrepancia de formato heredada quedó resuelta; commit cca863e; mode: mvp confirmado vía roadmap.get-phase).

| Step | Expected | Evidence | Status |
|------|----------|----------|--------|
| Crear cuenta | Form /registro → 201; duplicado → 409 con copy locked | Doc: contrato 0.2.0 (parseado) + guia-05/06. Runtime UAT: 201 en registro nuevo, 409 "Ese email ya tiene cuenta, inicia sesión" con email seed, aviso esmeralda tras crear | ✓ VERIFIED |
| Iniciar sesión | Token; navbar con email; F5 conserva sesión | Doc: guia-05 HS256 + guia-06 store maura-auth partialize. Runtime UAT: login 200 ambos roles, 401 genérico byte a byte idéntico, token offline {sub,rol,exp,iat} con exp−iat=604800, F5 sin parpadeo, token corrupto → expulsión con aviso ámbar (D-22) | ✓ VERIFIED |
| Armar carro | Agregar solo en ficha; stepper; vaciar dos pasos; badge; sobrevive F5 | Doc: guia-07 store/hidratación/Math.min. Runtime UAT: merge 2 clics→una fila, tope stock 2 deshabilita "+", total $37.960 exacto, vaciar dos pasos, badge unidades 0→1→2→4 oculto en 0, F5 carro vivo, pestaña nueva intacta | ✓ VERIFIED |
| Checkout exige sesión | /checkout → login → vuelve al checkout; CTA deshabilitado | Doc: guia-08 RequireAuth + returnTo + D-31. Runtime UAT: sin sesión → /login → vuelta AL checkout con "Comprando como" (nadie hardcodeó la ruta), carro vacío con sesión → /carro, CTA "Pagar con Webpay" disabled + nota | ✓ VERIFIED |
| Outcome | "Tienda me reconoce + compra lista para Webpay fase 3" | Sesión y carro sobreviven full-page loads (mecanismo exacto que la redirección Webpay impondrá en fase 3); resumen hidratado sin steppers con totales idénticos carro↔checkout ($26.970); contrato sin endpoint de pago (correcto — fase 3) | ✓ VERIFIED |

## Goal Achievement

### Observable Truths

Verdades 1-4 = Success Criteria del ROADMAP (contrato no negociable). En la verificación previa quedaron ⚠️ PRESENT_BEHAVIOR_UNVERIFIED a la espera del UAT delegado; hoy el runtime fue ejecutado y registrado en 02-UAT.md (4/4 tests pass, 12/12 filas de la Gran verificación final), y este verificador confirmó de forma independiente los artefactos del taller (ver Behavioral Spot-Checks). Verdades 5-45 = must_haves.truths de los 5 planes (41), verificadas en la pasada previa contra los archivos y re-chequeadas hoy por regresión — los archivos de las olas 1-2 no cambiaron y los patrones de las guías modificadas siguen presentes (ver tabla de regresión).

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC1: cuenta + login + sesión entre recargas (AUTH-01/02) | ✓ VERIFIED | UAT delegado: registro 201/409, login 200/401, token exp−iat=604800, navbar email, F5 sin parpadeo, pestaña nueva conserva sesión. Artefactos taller verificados: features/cuentas/Login.tsx+Registro.tsx, stores/useAuthStore.ts |
| 2 | SC2: claim de rol desde el primer token; admin 200 / clienta 403 (AUTH-03) | ✓ VERIFIED | UAT: token decodificado con rol, /api/admin/estado 200 {productos:12, familias:4} admin / 403 'Requiere rol admin' clienta (también vía Authorize en /docs). Taller: security.py l.41 "rol": usuario.rol.value SIN condición; get_current_admin detail="Requiere rol admin" l.80 |
| 3 | SC3: carro agregar/editar/vaciar + persistencia full-page load (CART-01/02) | ✓ VERIFIED | UAT: merge/tope/stepper/vaciado, badge unidades, F5 + pestaña nueva, write-back WR-03 (cantidad 5 sembrada → cobra 2, store queda {cantidad:2}, badge corrige a 4). Taller: useCarroStore ItemCarro={producto_id,cantidad} + partialize SOLO items; Carro.tsx useEffect write-back |
| 4 | SC4: checkout exige sesión con retorno (AUTH-04) | ✓ VERIFIED | UAT: sin sesión → /login → vuelve AL checkout (returnTo), carro vacío con sesión → /carro, CTA disabled + nota. Taller: RequireAuth.tsx + features/checkout/Checkout.tsx |
| 5-12 | [02-01] Contrato 0.2.0 + bearerAuth, 4 paths nuevos, schemas sin hash, tabla errores, copies locked, sin renovación, ADRs 009-011, README arq | ✓ VERIFIED (regresión) | yaml.safe_load re-ejecutado hoy: version 0.2.0, 7 paths exactos, bearerAuth http/bearer/JWT única securityScheme. docs/04 sin commits desde la pasada previa |
| 13-18 | [02-02] docs/02 etapa 2 completa, P5/actores/formularios/pantallas, RN-05..09, docs/03 USUARIO+procesos+pantallas 4-7, ficha Agregar al carro, trazabilidad §5 | ✓ VERIFIED (regresión) | docs/02 y docs/03 sin commits desde la pasada previa (git log 0) |
| 19-28 | [02-03] guia-05 backend completo (rol incondicional l.425-428 re-grepado hoy, seed upsert, token_hex, CORS), guia-06 store+interceptor (sinAuth ×9 re-contado hoy), RequireAuth D-32, UI formularios, mini-verificación sesión | ✓ VERIFIED (regresión) | guia-05 modificada solo por 9cbd4af (+10 líneas, paso 8): ast.parse 16/16 bloques OK tras el edit; guia-06 modificada solo en 2 copies (5b1b718) |
| 29-41 | [02-04] guia-07 store sin precios (Math.min ×4, maura-carro ×11 re-contados), hidratación, UI estados, destructivos, botón ficha D-29; guia-08 RequireAuth ×8, CTA deshabilitado ×4 + nota, Gran verificación 12 filas re-contadas, totales WR-01 ($26.970 ×4 / $26.980 = 0) | ✓ VERIFIED (regresión) | Escritura de WR-03 re-grepada en guia-07 l.452-456; tabla de 12 filas íntegra tras el fix Quitar |
| 42-45 | [02-05] Índice filas 5-8, portadas 1-8 listas + 11 ADRs + fila 5 Parcial (P7), stack README raíz, cadena Siguiente + guide-only | ✓ VERIFIED (regresión) | READMEs sin commits; cadena 05→06→07→08→fase 3 re-grepada; 8 guías; `git ls-files -- backend frontend` = 0 |

**Score:** 45/45 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|-----------|--------|---------|
| docs/04_arquitectura/contrato_api.yaml | Contrato 0.2.0 superficie auth (D-15) | ✓ VERIFIED | Re-parseado hoy: 7 paths, bearerAuth, version 0.2.0 |
| docs/04_arquitectura/adr/009/010/011 | ADRs con negativas honestas | ✓ VERIFIED | Sin cambios desde pasada previa (git log 0) |
| docs/04_arquitectura/README.md | Índice 011 + stack + árbol | ✓ VERIFIED | Sin cambios |
| docs/02_requerimientos.md | Etapa 2 completa | ✓ VERIFIED | Sin cambios |
| docs/03_diseno.md | USUARIO + procesos + pantallas | ✓ VERIFIED | Sin cambios |
| docs/05_desarrollo/guia-05-cuentas-backend.md | Backend de cuentas | ✓ VERIFIED | 16/16 bloques ast.parse OK tras version bump; paso 8 enseña subida 0.1.0→0.2.0 con mini-verificación ítem 4 (hallazgo UAT corregido en ambos lugares) |
| docs/05_desarrollo/guia-06-sesion-frontend.md | Sesión SPA | ✓ VERIFIED | sinAuth ×9 intacto; fallback copy unificado "…e inténtalo de nuevo." ×2 (fix UI-REVIEW) |
| docs/05_desarrollo/guia-07-carro.md | Carro persistente | ✓ VERIFIED | Write-back l.452-456 intacto; empty state text-sm→text-base l.468 (fix UI-REVIEW) |
| docs/05_desarrollo/guia-08-checkout.md | Checkout protegido + Gran verificación | ✓ VERIFIED | 12 filas íntegras; botón Quitar en fila degradada l.169 + narrativa actualizada l.241 (fix UI-REVIEW) |
| READMEs (raíz, docs, 05_desarrollo) | Estado de fase al día | ✓ VERIFIED | Fila 5 🚧 Parcial (P7 honrada); 1-8 listas; 11 ADRs |
| 02-SECURITY.md | Registro de amenazas de fase | ✓ VERIFIED | threats_open: 0; 21/21 cerradas con evidencia L1 + runtime UAT (commit 291ad2e) |
| 02-UI-REVIEW.md | Auditoría UI post-UAT | ✓ VERIFIED | 19/24, 3 priority fixes aplicados en ambos lugares (5b1b718); 6 minor recommendations documentadas (informativas) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| contrato 0.2.0 | guías 05-08 + /docs | implementación sin desvío + fila 12 | ✓ WIRED | UAT runtime: 7/7 paths calzados, códigos y schemas idénticos, /docs sirve 0.2.0 (fix verificado en taller main.py l.16) |
| guia-06/07/08 ↔ taller maura-uat | código de las guías | drift check | ✓ WIRED | WR-02/WR-03/Quitar/copy/text-base verificados grep a grep en AMBOS lugares (regla maura-uat) |
| Cadena Siguiente | guia-04→05→…→fase 3 | links literales | ✓ WIRED | Re-grepado hoy: 4 eslabones + origen intacto |
| ROADMAP goal | User Story canónica | mvp-phase | ✓ WIRED | user-story.validate → true; mode: mvp |

### Data-Flow Trace (Level 4 — equivalente documental + runtime)

| Dato | Fuente canónica | Consumidores | Status |
|------|----------------|--------------|--------|
| Copies locked 409/401 | contrato example.detail | guia-05/06, docs/02 RN-06, taller (runtime byte a byte) | ✓ FLOWING |
| Precio del carro | API vigente (useQueries) | fila, total, Total panel — store sin precio (runtime: localStorage solo pares) | ✓ FLOWING |
| Rol del token | usuario.rol.value incondicional | get_current_admin → 403; Authorize /docs (runtime probado ambos roles) | ✓ FLOWING |
| Estado de fase | archivos reales (8 guías, 11 ADRs) | 3 READMEs | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Contrato 0.2.0 válido | python yaml.safe_load | version 0.2.0; 7 paths; bearerAuth http/bearer/JWT | ✓ PASS |
| Bloques Python guia-05 tras version bump | python ast.parse × 16 | 16/16 OK | ✓ PASS |
| Taller fase 2 existe (claims UAT) | ls maura-uat backend/app + frontend/src | auth.py, admin.py, security.py, seed.py, stores ×2, features cuentas/carro/checkout, RequireAuth — todo presente | ✓ PASS |
| WR-02 en taller | grep sinAuth/apiPostForm | api.ts l.72-75: apiPostForm → pedir con sinAuth: true; login lo usa (Login.tsx l.37) | ✓ PASS |
| WR-03 en taller | grep cambiarCantidad Carro.tsx | useEffect l.452-456: write-back al stock | ✓ PASS |
| Fix Quitar checkout en taller | grep quitar Checkout.tsx | l.22 + l.118-121 botón Quitar en fila degradada | ✓ PASS |
| Version 0.2.0 en taller | grep main.py | l.16 version="0.2.0" | ✓ PASS |
| User story canónica | gsd_run query user-story.validate | true | ✓ PASS |
| Debt markers en guías modificadas | grep TBD/FIXME/XXX/HACK/PLACEHOLDER | 0 matches | ✓ PASS |

### Probe Execution

SKIPPED — sin probes declarados en PLAN/SUMMARY ni scripts/ en el repo. El rol de probe runtime lo cubre el UAT delegado (Gran verificación final 12/12 PASS registrada en 02-UAT.md con evidencia por fila).

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| AUTH-01 | 02-01, 02-02, 02-03 | Crear cuenta con email y contraseña | ✓ SATISFIED | Contrato + guia-05/06 + runtime UAT (201/409/copies) |
| AUTH-02 | 02-01, 02-02, 02-03 | Login + sesión persistente JWT | ✓ SATISFIED | Contrato + guias + runtime (token 7 días, F5, pestaña nueva, expulsión token corrupto) |
| AUTH-03 | 02-01, 02-02, 02-03 | Endpoints admin por rol, claim desde el primer token | ✓ SATISFIED | Contrato + guia-05 + runtime (admin 200 / clienta 403, Authorize /docs, re-siembra idempotente). Nota: las "vistas de administración" del wording requirement exceden el SC2 de la fase (endpoint); el panel completo es Phase 4 del ROADMAP |
| AUTH-04 | 02-02, 02-04 | Checkout exige sesión con retorno | ✓ SATISFIED | RF-09 + guia-08 + runtime (returnTo punta a punta) |
| CART-01 | 02-02, 02-04 | Agregar/editar/vaciar carro | ✓ SATISFIED | RF-10 + guia-07 + runtime (merge, stepper, tope, vaciado dos pasos) |
| CART-02 | 02-02, 02-04 | Carro persiste en localStorage, sobrevive full-page loads | ✓ SATISFIED | RF-11 + guia-07 + runtime (F5 + pestaña nueva; el full-page load de Webpay llega en fase 3 y usará este mismo mecanismo) |

Orphans: ninguno — REQUIREMENTS.md mapea exactamente los 6 IDs a Phase 2 (todos [x] Complete); la unión de los campos `requirements` de los 5 planes cubre los 6. GUIDE-02 (Phase 1) sigue como cierre transversal declarado por 02-05.

### Decision Coverage

```
gsd-tools query check.decision-coverage-verify 02-CONTEXT.md →
{ skipped: false, blocking: false, total: 15, honored: 15, not_honored: [], message: "All trackable CONTEXT.md decisions are honored by shipped artifacts." }
```

### Test Quality Audit

N/A como suite — repo guide-only (D-17): sin archivos de test. El rol de prueba lo cubren (a) las 47 mini-verificaciones documentales de las guías 05-08 y (b) la Gran verificación final de 12 filas, ejecutada runtime por el UAT delegado con registro por fila. Sin tests deshabilitados, sin patrones circulares (los valores esperados provienen del contrato 0.2.0, fuente externa al código generado).

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| guia-05/06/07 (varias) | — | "TODO" en mayúsculas (español: "todo el HTTP") | ℹ️ Info | Falsos positivos conocidos heredados; no son debt markers |
| 02-UI-REVIEW.md (registro) | — | 6 minor recommendations no aplicadas: skeleton de checkout en barra única vs layout de fila, "Comprobando tu sesión…" fuera del sistema visual, variantes de spacing fuera del whitelist literal (on-scale), superficies accent no enumeradas, border-t-2 vs divide-y, clasificación Label/Body de causas de error | ℹ️ Info | Refinamientos de spec UI posteriores al UAT, documentados en 02-UI-REVIEW.md; ninguno viola un must-have del PLAN ni un SC del ROADMAP. Los 3 priority fixes del mismo review SÍ se aplicaron en ambos lugares (5b1b718) |

Sin debt markers sin referencia (TBD/FIXME/XXX/HACK/PLACEHOLDER = 0 en los archivos modificados), sin placeholders de implementación, sin stubs.

### Prohibitions Review (7, judgment-tier — ratificadas por revisión delegada)

| # | Prohibición | Status | Evidence |
|---|-------------|--------|----------|
| P1 | No ocultar desventaja XSS en ADR-009 (D-21) | HONORED (ratificada) | "Negativas (honestas)" l.55-57 — muestreo independiente del UAT test 3 |
| P2 | RN-05 sin composición obligatoria (D-25) | HONORED (ratificada) | docs/02 l.123 + runtime: clave corta → 401 (no 422) |
| P3 | Cero secretos literales en guías (D-23) | HONORED (ratificada) | grep → 0; solo placeholders en .env.example |
| P4 | 401 genérico único en login (D-26) | HONORED (ratificada) | Runtime: email inexistente y clave mala responden byte a byte igual |
| P5 | Store carro sin precios (D-27) | HONORED (ratificada) | Runtime: localStorage con exclusivamente pares {producto_id, cantidad} |
| P6 | Guard=UX dicho explícitamente (D-32) | HONORED (ratificada) | guia-06 paso 5 + guia-08 paso 2/error 1 + mismo comentario en taller |
| P7 | Fila 5 del ciclo NO pasa a ✅ (D-13) | HONORED (ratificada) | "🚧 Parcial (guías 1-8 listas…)" en ambos READMEs (re-grepado hoy) |

Las 7 prohibiciones judgment-tier quedaron ratificadas por el canal de revisión delegada sancionado en AGENTS.md (02-UAT.md test 3, pass, con muestreo independiente del veredicto autónomo previo). Sin prohibiciones test-tier en la fase.

## Human Verification Required

Ninguna pendiente. Los 4 ítems de la verificación previa se cerraron por el canal delegado sancionado (instrucción persistente del usuario en AGENTS.md — UAT delegado al agente en D:/Repos/maura-uat):

1. UAT delegado guías 05-08 + Gran verificación final 12/12 — **pass** (02-UAT.md test 1)
2. Runtime WR-02/WR-03 (incluye caso borde token viejo en store) — **pass** (test 2)
3. Ratificación de las 7 prohibiciones judgment-tier — **pass** (test 3)
4. Goal en User Story canónica — **pass** (test 4; user-story.validate true confirmado por este verificador)

### Gaps Summary

Sin gaps. Las 4 Success Criteria del ROADMAP pasaron de present-but-unverified a verificadas con evidencia runtime (UAT delegado con registro por fila, confirmado por inspección independiente de los artefactos del taller). Las 41 verdades documentales sostienen la regresión: los archivos de las olas 1-2 no cambiaron desde la pasada previa y los patrones de las guías modificadas (version bump, fixes UI-REVIEW) se verificaron grep a grep en guías Y taller. Los 3 fixes del UI-REVIEW están aplicados en ambos lugares; sus 6 minor recommendations quedan como registro informativo en 02-UI-REVIEW.md. SECURITY.md cierra 21/21 amenazas (threats_open: 0). Cobertura de requerimientos 6/6 sin huérfanos; 15/15 decisiones honradas.

---

_Verified: 2026-09-30T12:10:00Z_
_Verifier: Claude (gsd-verifier)_
