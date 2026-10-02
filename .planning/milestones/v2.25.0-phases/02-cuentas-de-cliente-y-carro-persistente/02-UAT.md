---
status: complete
phase: 02-cuentas-de-cliente-y-carro-persistente
source: [02-VERIFICATION.md]
started: 2026-09-29T18:40:00Z
updated: 2026-09-30T12:05:00Z
verified_by: agent (user-delegated per AGENTS.md — taller D:/Repos/maura-uat)
---

## Current Test

[testing complete]

## Tests

### 1. UAT delegado en D:/Repos/maura-uat (agente, user-delegated per AGENTS.md)
expected: Construir guías 05-08 en orden en el taller y ejecutar la Gran verificación final de guia-08 (12 filas + Authorize) — 12/12 filas PASS registradas acá. Cubre las 4 Success Criteria del ROADMAP: sesión tras F5 (SC1), admin 200 vs clienta 403 en /api/admin/estado (SC2), carro tras full-page load con badge (SC3), y checkout: sin sesión → /login → vuelve al checkout (SC4).
result: pass
evidence: |
  Guías construidas con los comandos literales, todas las mini-verificaciones en PASS:
  - guia-05 (11 pasos): uv add pyjwt 2.15.1/pwdlib[argon2]/python-multipart; .env con
    SECRET_KEY fail-fast verificado (ValidationError nombra secret_key); enum rol
    ['cliente','admin'] == valores del contrato; seed [+]→[=] idempotente; login 200 bearer
    ambos roles; 401 genérico con clave mala; token offline {sub:'2', rol, exp, iat} con
    exp−iat=604800 (7 días, D-20); admin /api/admin/estado 200 {productos:12, familias:4};
    clienta 403 'Requiere rol admin'; preflight CORS OPTIONS→200.
  - guia-06 (10 pasos): zustand ^5.0.15; experimento del compilador TS2322 con rol
    "superadmin" (falla/borra/pasa); credenciales malas → banner rojo DENTRO de la card sin
    redirección (Pitfall 5); registro vacío → espejos cliente; email seed → 409 con copy
    locked; cuenta nueva → login con aviso esmeralda; navbar ambos estados; maura-auth
    persiste SOLO {token, usuario} (partialize); F5 sin parpadeo; token corrupto →
    expulsión a /login?expirada=1 con aviso ámbar (D-22); sin scroll horizontal a 375px.
  - guia-07 (8 pasos): maura-carro guarda SOLO {producto_id, cantidad} (D-27, sin precios);
    merge 2 clics → una fila cantidad 2; tope de ficha (Rosa de Río stock 2: botón
    deshabilitado + helper); /carro con total $37.960 = 2×7.990+2×10.990 exacto; "+"
    deshabilitado al stock; Quitar recalcula al instante; vaciar en dos pasos inline con
    Cancelar; badge unidades (no ítems): 0→1→2→4, oculto en 0, aria-live; F5 carro vivo;
    castigo del tapado: cantidad 5 sembrada a mano → fila/total cobran 2, write-back al
    store ({6,cantidad:2}) y badge corrige a 4; fila degradada 999 → "Este aroma ya no está
    disponible" + Quitar sin stepper, resto operativo; backend detenido → "No pudimos cargar
    tu carro" + Reintentar recupera sin recargar.
  - guia-08 (4 pasos + Gran verificación final): checkout sin sesión → login → vuelve AL
    checkout con "Comprando como" (returnTo D-32, nadie hardcodeó la ruta); carro vacío con
    sesión → redirect a /carro; totales idénticos carro↔checkout ($26.970 = 2×7.990+1×10.990);
    CTA "Pagar con Webpay" disabled + nota; admin entra vía UI (navbar admin@maura.cl);
    pestaña nueva: sesión + carro + badge intactos (equiv. cerrar/reabrir).
  - Gran verificación final 12/12: filas 1-11 cubiertas arriba; fila 12 contrato↔/docs:
    7/7 paths exactos, códigos por path calzados, schemas UsuarioPublico (rol enum
    [cliente,admin] vía $ref)/Token/RegistroCreate (minLength 8) presentes, perfil y
    admin/estado con candado, registro/login públicos; botón Authorize probado en /docs:
    admin → GET /api/admin/estado → 200 {"productos":12,"familias":4}; clienta → 403.
  - Hallazgo menor corregido en caliente (ambos lugares, regla maura-uat): /docs mostraba
    info.version 0.1.0 vs contrato 0.2.0 — ninguna guía subía la versión. Fix: taller
    main.py version="0.2.0" (verificado: openapi.json sirve 0.2.0) y guia-05 paso 8 enseña
    el bump + ítem 4 en su mini-verificación (commit 9cbd4af).
  - Observaciones (no desvíos): (a) 422 automático de FastAPI aparece además en login y
  productos/{id} — inherente al framework, no eliminable con lo enseñado; (b) el esquema en
  /docs se llama OAuth2PasswordBearer y no bearerAuth — deliberado (guia-05 paso 8: es lo
  que habilita el botón Authorize que la fila 12 exige); (c) Token.token_type viaja con
  default "bearer" → el schema lo lista como no-required (el valor siempre va en la
  respuesta); (d) la fila degradada tarda ~7s en asentarse (retries por defecto de
  useQueries) — la guía no promete timing.

### 2. Runtime de los fixes WR-02 y WR-03 (marcados requires-human-verification en 02-REVIEW-FIX.md)
expected: |
  WR-02: login con credenciales malas NO redirige a ?expirada=1 (banner rojo "Credenciales incorrectas"
  dentro de la card — el login viaja sinAuth y jamás adjunta Bearer).
  WR-03: localStorage con cantidad > stock se corrige solo al hidratar (write-back) y el badge del
  navbar cuenta las unidades tapadas (mismo número que filas y total).
result: pass
evidence: |
  WR-02 — caso base (guia-06 MV p6): clienta seed + clave mala → banner rojo "Credenciales
  incorrectas" visible DENTRO de la card, URL se mantiene en /login (sin ?expirada=1).
  WR-02 — caso borde exacto del fix (token viejo en store): sesión clienta activa → backend
  detenido → /login muestra el formulario con el token aún guardado (verificar falló por
  red, retry:false) → backend reencendido → credenciales malas → banner rojo en la card,
  URL /login sin expirada=1, maura-auth INTACTO (token y usuario no borrados: el interceptor
  no disparó porque apiPostForm viaja sinAuth) → login bueno restaura la sesión. La
  invariante "el 401 del login lo maneja el formulario, jamás el centinela" es verdadera
  por construcción también con token en el store.
  WR-03 (guia-07 MV p8b): maura-carro sembrado a mano con {producto_id:6, cantidad:5}
  (stock vigente 2) → recarga /carro → el total cobra 2×$10.990 (no 5), el efecto
  escribir cambiarCantidad(6, 2) de vuelta al store (maura-carro queda {cantidad:2}) y el
  badge del navbar corrige a 4 = 1+1+2 — pantalla, filas, total, store y badge dicen lo
  mismo (D-30/RN-09, promesa de 03_diseno §4.7).

### 3. Revisión de las 7 prohibiciones judgment-tier (flag unverified-prohibition)
expected: Confirmar el muestreo: P1 XSS en ADR-009 Negativas; P2 RN-05 sin composición; P3 cero secretos literales en guías 05/06; P4 401 genérico único en login; P5 store carro sin precios; P6 guard=UX dicho; P7 fila 5 Parcial (no ✅). El veredicto autónomo del verificador fue HONORED en las 7 — esta revisión lo ratifica.
result: pass
evidence: |
  Muestreo independiente (no solo citando al verificador), sesión 2026-09-30:
  - P1 ✓ ADR-009 (adr/009-jwt-larga-vida-localstorage.md l.22 tabla de opciones y l.56
    "Negativas (honestas)": "Robo de token por XSS... por hasta 7 días" — la desventaja
    D-21 está dicha, no oculta.
  - P2 ✓ RN-05 (02_requerimientos.md l.123): "largo mínimo de 8 caracteres, sin reglas de
    composición obligatoria: no se exige mayúscula, número ni símbolo" + racional NIST.
  - P3 ✓ grep de SECRET_KEY=[hex16+] / PASSWORD=[literal] en guia-05/06 → 0; solo
    placeholders en .env.example; el secreto nace de secrets.token_hex(32).
  - P4 ✓ runtime: email inexistente y clave mala responden BYTE A BYTE igual:
    401 {'detail': 'Credenciales incorrectas'} — único mensaje, sin pistas (RN-06/D-26).
  - P5 ✓ runtime: maura-carro persiste exclusivamente pares {producto_id, cantidad}
    (D-27/RN-08), verificado en localStorage tras cada flujo.
  - P6 ✓ guia-06 paso 5 y guia-08 paso 2 + error 1: "el guard es UX, no seguridad (D-32)"
    dicho explícito; el código del taller lleva el mismo comentario.
  - P7 ✓ README.md l.42 y docs/README.md l.19: fila 5 "🚧 Parcial (guías 1-8 listas;
    continúa en fases 3+)" — no pasó a ✅ (D-13).
  Los 7 veredictos HONORED del verificador quedan ratificados por revisión delegada.

### 4. Formato del goal: User Story canónica en ROADMAP.md
expected: Correr `/gsd mvp-phase 2` para dejar el goal en formato "As a..., I want to..., so that..." (hoy user-story.validate = false; la versión canónica vive en los PLANs 02-03/02-04). Discrepancia heredada de fase 1 (01-VERIFICATION nota la misma).
result: pass
evidence: |
  Flujo mvp-phase aplicado sobre la fase 02 (equivalente --force: la fase está in_progress
  con 5/5 planes ejecutados — re-planificar no aplica y el test solo pedía el formato):
  - User story ensamblada desde las versiones canónicas de 02-03/02-04-PLAN (Phase Goal
    user story) y validada con el verbo central: user-story.validate --story → valid:true,
    slots {role: visitante de la tienda, capability: cuenta+sesión+carro+checkout,
    outcome: reconocimiento y compra lista para Webpay fase 3}.
  - ROADMAP.md editado: **Goal** = "As a visitante de la tienda, I want to crear una
    cuenta, iniciar sesión con un token que persiste entre recargas y armar un carro que
    sobreviva los full-page loads hasta un checkout que me exige sesión, so that la tienda
    me reconoce en cada visita y mi compra queda lista para el pago real que llega con
    Webpay en la fase 3." (Mode: mvp ya existía, sin duplicar).
  - Write verificado con roadmap.get-phase: mode=mvp, goal=story canónica exacta
    (commit cca863e).
  - SPIDR: la story supera 120 chars (capacidades compuestas) pero la división se evaluó y
    omitió con causa: la fase ya está planificada y ejecutada como un slice vertical (5
    planes ejecutados); un split post-hoc invalidaría trabajo ejecutado.
  - Nota: `user-story.validate "02"` (posicional) siempre da valid:false porque el verbo
    solo lee --story — la validación real es sobre el goal extraído (hecho: valid:true).

## Summary

total: 4
passed: 4
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none — el único hallazgo de los tests (info.version 0.1.0 vs contrato 0.2.0) se corrigió y
verificó en caliente en ambos lugares: taller main.py 0.2.0 confirmado vía openapi.json y
guia-05 paso 8 con el bump + ítem de verificación (commit 9cbd4af)]

## Post-UAT: verify:post hooks (2026-09-30)

- **secure-phase** (security_enforcement): 02-SECURITY.md creado — 21/21 amenazas CLOSED
  (evidencia L1 + runtime del propio UAT), threats_open: 0, short-circuit asvs_level 1
  (commit 291ad2e).
- **ui-review** (ui_review): 02-UI-REVIEW.md — 19/24 global, sin drift guías↔taller, cero
  violaciones de sistema. 3 hallazgos de contrato corregidos en ambos lugares (regla
  maura-uat, commit 5b1b718): (1) "Quitar" en la fila degradada del checkout (UI-SPEC:
  "mismas reglas que /carro" — verificado runtime desde el propio panel); (2) copy de
  fallback de red de login/registro unificado con la familia contratada "…e inténtalo de
  nuevo." + fila nueva en el Copywriting Contract; (3) cuerpo del empty state del carro a
  text-base (Tipografía Cuerpo). Build del taller OK tras los fixes.

