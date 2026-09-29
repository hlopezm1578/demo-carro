---
phase: 02-cuentas-de-cliente-y-carro-persistente
verified: 2026-09-29T18:26:06Z
status: human_needed
score: 41/45 must-haves verified
covered_files:
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
  - README.md
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
  - docs/README.md
covered_digest: "v2:sha256:0a471a64d2ba20d9146416a0f574507341f50df410b4767eda2f1fde3e92fdb0"
behavior_unverified: 4 # Las 4 Success Criteria del ROADMAP (runtime del alumno) — presentes y cableadas documentalmente, no ejecutadas aún: el taller maura-uat no tiene artefactos de fase 2
overrides_applied: 0
behavior_unverified_items:
  - truth: "SC1: Cliente crea cuenta con email y contraseña, inicia sesión y mantiene la sesión entre recargas de la SPA (AUTH-01/02)"
    test: "En maura-uat: seguir guia-05 (seed + login form) y guia-06 (store persist); registrar cuenta nueva, login con clienta seed, F5"
    expected: "201 en registro nuevo, 409 con email duplicado, login devuelve token, navbar muestra email, F5 conserva sesión sin parpadeo (Gran verificación filas 1-4)"
    why_human: "Persistencia de estado entre recargas: grep no puede ver si localStorage hidrata sincrónico al primer render; los planes la declaran asunción (A4/Pitfall 7) con runtime delegado al UAT"
  - truth: "SC2: Admin recibe claim de rol desde el primer token y accede al endpoint protegido; cliente recibe 403 (AUTH-03)"
    test: "En maura-uat: login con admin y clienta del seed (incluida re-siembra), decodificar token offline, GET /api/admin/estado con ambos tokens (también vía Authorize en /docs)"
    expected: "Token con claims sub/rol/exp/iat (exp-iat=604800); 200 con conteos para admin, 403 'Requiere rol admin' para clienta — también tras re-ejecutar el seed (Gran verificación filas 3 y 6)"
    why_human: "Autorización runtime bajo concurrencia/re-siembra: el claim incondicional (guia-05 l.422-427) y el upsert que fija rol (l.856-868) son greppables, pero ningún proceso ha emitido un token real todavía"
  - truth: "SC3: Visitante agrega/edita/vacía el carro; persiste en localStorage y sobrevive un full-page load (CART-01/02)"
    test: "En maura-uat: seguir guia-07; agregar desde ficha, stepper, quitar, vaciar en dos pasos; F5 y cierre/reapertura de pestaña; editar localStorage a mano (cantidad 5 vs stock 2)"
    expected: "Badge y filas persisten tras F5; write-back WR-03 corrige cantidad 5→2 en store y badge; '+' deshabilitado en el stock (Gran verificación filas 7-9)"
    why_human: "Invariante de persistencia + corrección de estado (useEffect l.452-458 de guia-07, fix WR-03 marcado requires-human-verification): transición de estado que ninguna ejecución ha ejercido"
  - truth: "SC4: El checkout exige sesión: visitante sin sesión → login → vuelve al checkout al autenticarse (AUTH-04)"
    test: "En maura-uat: seguir guia-08; con carro armado, cerrar sesión, navegar /checkout, autenticarse; además corromper el token en maura-auth y navegar"
    expected: "/login con retorno AL checkout tras autenticarse (returnTo, nadie hardcodea la ruta); token corrupto → expulsión con aviso ámbar 'Tu sesión expiró, ingresa de nuevo' (Gran verificación filas 5 y 10)"
    why_human: "Flujo de navegación con estado del router + interceptor 401 (guard sinAuth/llevaBearer, fix WR-02 marcado requires-human-verification): invariantes de orden/limpieza que greps no ejercen"
human_verification:
  - test: "UAT delegado en D:/Repos/maura-uat (agente, user-delegated per AGENTS.md): construir guias 05-08 en orden y ejecutar la Gran verificación final de guia-08 (12 filas + Authorize)"
    expected: "12/12 filas PASS registradas en 02-UAT.md con verified_by: agent (user-delegated); el taller hoy NO tiene auth.py/admin.py/stores (solo fase 1) — la capa runtime completa está pendiente"
    why_human: "Repo guide-only (D-17): el runtime vive en la máquina del alumno/taller; esta verificación comprobo el contenido documental, no la ejecución"
  - test: "Confirmar runtime de los dos fixes marcados requires-human-verification: WR-02 (login viaja sinAuth — el 401 del propio login jamas dispara el interceptor) y WR-03 (write-back del tapado al stock)"
    expected: "WR-02: login con credenciales malas NO redirige a ?expirada=1 (banner rojo en la card); WR-03: localStorage con cantidad>stock se corrige solo al hidratar y el badge cuenta las unidades tapadas"
    why_human: "02-REVIEW-FIX.md marca ambos fixes como 'requires human verification (cambia lógica enseñada)' — la lógica nueva esta en las guías pero no ha corrido"
  - test: "Revisión humana de las 7 prohibiciones judgment-tier (flag autonomous: unverified-prohibition — human review recommended; veredicto LLM no autoritativo)"
    expected: "Confirmar el muestreo: P1 XSS en ADR-009 Negativas; P2 RN-05 sin composición; P3 cero secretos literales en guias 05/06; P4 401 generico unico en login; P5 store carro sin precios; P6 guard=UX dicho; P7 fila 5 Parcial (no ✅)"
    why_human: "ADR-550 D4: en corrida autónoma las prohibiciones sin tier test reciben veredicto no autoritativo + flag; nunca pasan en silencio"
  - test: "Formato del goal: correr /gsd mvp-phase 2 para dejar la User Story canónica en ROADMAP.md"
    expected: "Goal del ROADMAP en formato 'As a..., I want to..., so that...' (hoy user-story.validate = false; la versión canónica vive en los PLANs 02-03/02-04)"
    why_human: "El verificador MVP exige User Story canónica para el framede cobertura; discrepancia heredada de fase 1 (01-VERIFICATION nota la misma)"
---

# Phase 2: Cuentas de cliente y carro persistente Verification Report

**Phase Goal:** Un visitante se convierte en cliente identificado: crea cuenta, inicia sesión con JWT que persiste entre recargas, arma un carro que sobrevive los full-page loads (los que impondrá la redirección de Webpay) y el checkout le exige sesión iniciada.
**Verified:** 2026-09-29T18:26:06Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Scope frame (D-17, heredado de la fase 1)

Repositorio **guide-only** (D-17/ADR-008): los entregables son DOCUMENTOS. Verificación por contenido sobre docs/ — greps, parseo `yaml.safe_load` del contrato, `ast.parse` de los bloques Python de las guías, conteos, diffs git, y chequeo material del taller `D:/Repos/maura-uat` (UAT delegado per AGENTS.md). Nada se ejecuta ni instala en este repo.

**Hallazgo clave del taller:** `D:/Repos/maura-uat` contiene SOLO artefactos de fase 1 (routers: productos.py, salud.py; features: catalogo, landing; sin stores/). Las guías 05-08 NO han sido construidas ni ejecutadas ahí — la capa runtime de la fase está íntegramente pendiente del UAT delegado.

## MVP Mode — User Flow Coverage

**Nota (no bloqueante, heredada de fase 1):** el goal del ROADMAP no valida como User Story canónica (`user-story.validate` → false); la versión canónica vive en los PLANs 02-03/02-04: "As a visitante de la tienda, I want to crear una cuenta, iniciar sesión con un token que persiste entre recargas y armar un carro que sobrevive los full-page loads, so that llego al checkout con mi identidad y mi compra listas". Recomendación: `/gsd mvp-phase 2`.

| Step | Expected | Evidence | Status |
|------|----------|----------|--------|
| Crear cuenta | Form /registro → 201; email duplicado → 409 "Ese email ya tiene cuenta, inicia sesión"; contraseña mínimo 8 | Contrato 0.2.0 (201/409/422 parseados); guia-05 routers con responses declaradas (l.620-648); guia-06 Registro con espejo RN-05 y banner 409; HU-05 Gherkin con escenario duplicado | ✓ documentado / ⚠️ runtime en UAT |
| Iniciar sesión | Form /login → token; navbar muestra email truncado; F5 conserva sesión | Contrato login 200/401 form-urlencoded; guia-05 OAuth2PasswordRequestForm + HS256; guia-06 store maura-auth + partialize; mini-verificación AUTH-02 F5 (guia-06 l.847, 927) | ✓ documentado / ⚠️ runtime en UAT |
| Armar carro | "Agregar al carro" solo en ficha; /carro con stepper/vaciado dos pasos; badge aria-live; sobrevive F5 | guia-07 store maura-carro solo {producto_id, cantidad}; useQueries + queryKey; Math.min ×4; vaciado dos pasos; mini-verificación RF-11 F5 (l.734, 828) | ✓ documentado / ⚠️ runtime en UAT |
| Checkout exige sesión | /checkout con RequireAuth → login → vuelve al checkout; CTA "Pagar con Webpay" deshabilitado + nota D-31 | guia-08 RequireAuth + returnTo location.state?.from; CTA deshabilitado con "El pago llega en la etapa siguiente."; Gran verificación fila 10 | ✓ documentado / ⚠️ runtime en UAT |
| Outcome | "Llego al checkout con identidad y compra listas para Webpay (fase 3)" | Pantalla 7 completa (docs/03 l.638-659); resumen hidratado sin steppers; contrato sin endpoint de pago (correcto — fase 3) | ✓ documentado / ⚠️ runtime en UAT |

## Goal Achievement

### Observable Truths

Las 4 verdades 1-4 son las Success Criteria del ROADMAP (contrato no negociable) — todas behavior-dependent y sin ejecución aún en el taller: presentas + cableadas documentalmente, estado runtime no ejercido. Las verdades 5-45 son las must_haves.truths de los 5 planes (41), todas documentales y verificadas contra los archivos.

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC1: cuenta + login + sesión entre recargas (AUTH-01/02) | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Documentario completo (filas 13-27 abajo); runtime pendiente: maura-uat sin stores/auth.py; planes declaran asunciones A4/Pitfall 7 con runtime en UAT |
| 2 | SC2: claim de rol desde el primer token; admin 200 / clienta 403 (AUTH-03) | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Documentario completo (rol incondicional guia-05 l.422-427; upsert fija rol l.856-868; 403 l.975); ningún token real emitido aún |
| 3 | SC3: carro agregar/editar/vaciar + persistencia full-page load (CART-01/02) | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Documentario completo (guia-07 store/hidratación/badge); persistencia localStorage no ejercida; WR-03 write-back marcado requires-human-verification |
| 4 | SC4: checkout exige sesión con retorno (AUTH-04) | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Documentario completo (guia-08 RequireAuth/returnTo); flujo de navegación no ejecutado; WR-02 interceptor marcado requires-human-verification |
| 5 | [02-01] Contrato 0.2.0 + bearerAuth ANTES de las guías (D-15) | ✓ VERIFIED | `yaml.safe_load`: version 0.2.0, openapi 3.0.3, bearerAuth {http, bearer, JWT}, única securityScheme (sin apiKey); commits: contrato 9bd6e3f (wave 1) antes de guia-05 d2d17b6 (wave 2) |
| 6 | [02-01] 4 paths nuevos con responses declaradas | ✓ VERIFIED | registro 201/409/422, login 200/401 (requestBody x-www-form-urlencoded), perfil 200/401 security bearerAuth, admin/estado 200/401/403 security bearerAuth — parseados del YAML; 7 paths totales (3 fase 1 intactos) |
| 7 | [02-01] Schemas UsuarioPublico/Token/RegistroCreate sin hash | ✓ VERIFIED | UsuarioPublico props exactamente {id, email, rol} (rol enum [cliente, admin] l.142); Token {access_token, token_type}; RegistroCreate password minLength 8 con description D-25 |
| 8 | [02-01] Tabla de errores: 401/403/409 → En uso (fase 2) + fila 201 | ✓ VERIFIED | info.description: filas 201/401/403/409 "En uso (fase 2)", 200/404/422 "En uso (fase 1)", 400 Reservado |
| 9 | [02-01] Copies locked literales en contrato | ✓ VERIFIED | 409 detail "Ese email ya tiene cuenta, inicia sesión"; 401 detail "Credenciales incorrectas" — extraídos del example de cada response |
| 10 | [02-01] Sin endpoint de renovación (D-19) | ✓ VERIFIED | 7 paths, ninguno de refresh; grep -i refresh/apiKey/api-key → 0 matches; description lo declara explícito |
| 11 | [02-01] ADRs 009-011 con negativas honestas | ✓ VERIFIED | 11 ADRs exactos (ls adr/0*.md = 11); ADR-009 "Negativas (honestas)" con "Robo de token por XSS" l.55-57 + interceptor 401 l.36 + 3 opciones; ADR-010 {producto_id, cantidad} sin precios D-27 + fila degradada + no cruza dispositivos l.50-56; ADR-011 ADMIN_EMAIL/CLIENTE_EMAIL l.31-32 + 403 l.36 + Para conversar en clase |
| 12 | [02-01] README arq: índice + stack + árbol, reglas y disclaimer intactos | ✓ VERIFIED | §5 filas 009/010/011 (l.198-200); §3 zustand/pyjwt/pwdlib/python-multipart citando ADRs (l.109-117); §4 security.py l.142, stores l.161, features/cuentas|carro|checkout l.163-165, RequireAuth l.167; regla 5 lib/api.ts l.179; disclaimer guide-only presente |
| 13 | [02-02] docs/02 etapa 2 completa sin renumerar | ✓ VERIFIED | RF-06..RF-11 (definiciones con origen AUTH/CART+P5 l.93-96+), RF-12 = 0; RNF-05/06 (l.112+); RN-05..09; HU-05..08; 17 líneas "Dado" (baseline 7 de fase 1 + ≥1 por HU nueva) |
| 14 | [02-02] P5 mapeada, §2 alcance, §3 actores, §10 formularios, §12 pantallas | ✓ VERIFIED | §13 fila "P5 Carro y cuentas → RF-06..RF-11, HU-05..HU-08" (l.281) + P6 etapa 3 con CART-03/PAY (l.282); alcance l.43-48; actores Clienta (con cuenta)/Admin (dueña) l.66-67; §10 l.247-248; §12 ítems 4-7 |
| 15 | [02-02] RN de seguridad: mínimo 8 sin composición, 401/409, hash confinado, D-27, D-30 | ✓ VERIFIED | RN-05 "sin reglas de composición obligatoria: no se exige mayúscula, número ni símbolo... NIST... longitud sobre la complejidad" (l.123); RN-06 asimetría deliberada (l.124); RN-07 (l.125); RN-08 D-27 (l.126); RN-09 D-30 (l.127) |
| 16 | [02-02] docs/03: USUARIO, diccionario, D2/A2, procesos 5.0-8.0, pantallas 4-7 | ✓ VERIFIED | USUARIO en ER l.46-49 + diccionario 5 columnas l.80-86 (email único, hash Argon2 RN-07, rol enum); D2 l.194 + A2 localStorage l.196 con nota "decisión de diseño" l.198; DFDs 5.0-8.0 (l.269/286/306/324); "Reglas del proceso" = 8; Pantallas 4-7 (§4.5-4.8) |
| 17 | [02-02] Ficha gana "Agregar al carro" (D-29); checkout CTA deshabilitado (D-31) | ✓ VERIFIED | Variante §4.4 l.474-479 con regla de deshabilitado por stock l.485; pantalla 7: CTA "(deshabilitado)" + "El pago llega en la etapa siguiente." l.658-659; nota D-31 también l.336 |
| 18 | [02-02] §5 trazabilidad: cadena P5 → RF → HU → pantalla → ADR continua | ✓ VERIFIED | Filas RF-06..RF-11 (l.692-697, 24 citas RF); ancla §2.3 → ADR-009/010/011 (l.158-160); §14 firma Etapa 2 2026-09-29 |
| 19 | [02-03] guia-05 backend completo implementando el contrato | ✓ VERIFIED | 1098 líneas; OAuth2PasswordRequestForm ×4, create_access_token HS256 ×8, get_current_admin ×9, RolUsuario ×19 (nombre==valor), token_hex, ADMIN_EMAIL/CLIENTE_EMAIL, CORS GET+POST (l.782-807), copies locked, responses={ ×4 (l.620/648/679/724), SettingsConfigDict(env_file), 10 🧠 / 13 mini-verificaciones |
| 20 | [02-03] AUTH-03: rol construido INCONDICIONALMENTE + upsert asigna rol | ✓ VERIFIED | create_access_token l.422-427: payload con "rol": usuario.rol.value y comentario "SIN condición"; upsert_usuario l.856-868: "restaura credenciales y rol", "El rol también se fija" en cada re-siembra |
| 21 | [02-03] Seed por email con 4 variables .env + restauración + 200 vs 403 | ✓ VERIFIED | upsert_usuario docstring (l.856-861); l.835 restauración como feature deliberada; mini-verificación l.975 "403 {'detail': 'Requiere rol admin'}"; l.1048 idempotencia |
| 22 | [02-03] Secreto via token_hex + .env.example solo placeholders + .env gitignoreado | ✓ VERIFIED | token_hex l.87-97; .env.example con "pega-aqui-el-resultado-del-comando-token-hex" y placeholders (l.92-97); grep hex-literal de secreto/password → 0 |
| 23 | [02-03] guia-06: store persist maura-auth + interceptor 401 con exclusión del login | ✓ VERIFIED | useAuthStore ×15, partialize ×9, createJSONStorage ×4, maura-auth ×8; sinAuth ×9 + llevaBearer ×4 (fix WR-02: el login jamás adjunta Bearer); "Tu sesión expiró, ingresa de nuevo" presente; D-22 ×8 |
| 24 | [02-03] RequireAuth con returnTo genérico (D-32) | ✓ VERIFIED | RequireAuth ×8, Navigate ×13, location.state; D-32 ×9; login vuelve con from ?? "/" |
| 25 | [02-03] UI formularios: labels persistentes, validación espejo al submit | ✓ VERIFIED | htmlFor ×4 sin placeholders; "Escribe un email válido." ×2; "al menos 8 caracteres" ×2; "Mínimo 8 caracteres" ×2 |
| 26 | [02-03] UI submits disabled en gerundio + banners dentro de card + avisos ámbar/esmeralda | ✓ VERIFIED | "Ingresando…" ×2 / "Creando cuenta…" ×1; expirada ×14; "Cuenta creada" ×2; copies 401/409 dentro del formulario |
| 27 | [02-03] UI navbar flex-wrap + email truncado + cerrar sesión | ✓ VERIFIED | flex-wrap ×2; max-w-32 ×2 + truncate ×3 (con title); "Cerrar sesión" ×6 |
| 28 | [02-03] Mini-verificación sesión punta a punta (AUTH-02) | ✓ VERIFIED | guia-06 l.847-848 (navbar email tras login) y l.927 (F5 sesión viva al primer render) — presente como instrucción; ejecución en UAT (truth 1) |
| 29 | [02-04] guia-07: useCarroStore maura-carro SOLO pares id/cantidad | ✓ VERIFIED | ItemCarro {producto_id: number, cantidad: number} — interfaz exacta; partialize ×4; acciones agregar (merge)/cambiarCantidad/quitar/vaciar (cambiarCantidad ×9) |
| 30 | [02-04] Hidratación por ítem reusando queryKey + precio vigente + tope stock | ✓ VERIFIED | useQueries ×6, queryKey ×9, String(id) (gotcha error-evitado 3); Math.min ×4 con enPantalla ×7 (tres valores con nombre); "precio c/u" l.321 |
| 31 | [02-04] UI empty state | ✓ VERIFIED | "Tu carro está vacío" ×2 + "Explora los aromas de Maura y agrega tus favoritos." + "Ver catálogo" ×3 |
| 32 | [02-04] UI carga skeleton + error general con Reintentar | ✓ VERIFIED | animate-pulse ×6 (fila skeleton mismo layout); "No pudimos cargar tu carro" + causa puerto 8000 + Reintentar ×3 |
| 33 | [02-04] UI ítem degradado 404 + Agotado | ✓ VERIFIED | "Este aroma ya no está disponible" ×3 + "Quitar"; Agotado ×3 sin stepper |
| 34 | [02-04] UI fila poblada: thumbnail, badge familia, stepper 44px, total, panel CTA | ✓ VERIFIED | 44px/h-11/size-11 ×12; aria-label ×4; bg-orange-50 ×1 (panel resumen); "Finalizar compra" enlazando /checkout |
| 35 | [02-04] UI overflow + badge navbar unidades totales (D-28) | ✓ VERIFIED | items-center wrap natural; badge reduce de unidades totales l.672-695; oculto en 0 l.869; aria-live ×5 |
| 36 | [02-04] UI destructivos: Quitar sin confirmación, Vaciar en dos pasos inline | ✓ VERIFIED | "¿Vaciar todo el carro?" ×4 + "Sí, vaciar" ×3 + "Cancelar"; useState booleano, sin modal ni window.confirm |
| 37 | [02-04] Botón "Agregar al carro" SOLO en ficha (D-29) con helper de tope | ✓ VERIFIED | "Agregar al carro" ×5 en guia-07 (todas en el paso de la ficha); "Ya tienes todo el stock disponible en tu carro." ×1; deshabilitado en stock 0 y en tope |
| 38 | [02-04] guia-08: /checkout con RequireAuth + carro vacío Navigate + "Comprando como" | ✓ VERIFIED | RequireAuth ×8; Navigate a /carro con replace; "Comprando como" ×4 |
| 39 | [02-04] Resumen sin steppers + CTA deshabilitado + nota locked (D-31) | ✓ VERIFIED | "Pagar con Webpay" ×4 deshabilitado con opacity/cursor; "El pago llega en la etapa siguiente." ×4; "← Volver al carro" ×4; "No pudimos cargar tu pedido" ×1 |
| 40 | [02-04] Gran verificación final: 12 filas + fila contrato ↔ /docs con Authorize | ✓ VERIFIED | Tabla 12 filas numeradas con columna Origen (RF/HU/RN/ADR/D); fila 12 (l.383) compara contrato 0.2.0 uno a uno (7 paths, códigos, schemas) con botón Authorize + GET /api/admin/estado desde /docs; "se repite al final de cada fase"; "Siguiente: fase 3" l.488 |
| 41 | [02-04] Totales aritméticamente correctos (fix WR-01) | ✓ VERIFIED | $26.970 en docs/03 (l.613, 656), guia-07 y guia-08; grep $26.980 → 0 en docs/ |
| 42 | [02-05] Índice 05_desarrollo filas 5-8 + blockquote + mapa mental | ✓ VERIFIED | Filas 5-8 con hito por guía (l.30-33); blockquote "La fase 2 del proyecto completa sus cuatro guías (5-8...)" l.35; mapa mental "capa de estado de cliente" l.46 |
| 43 | [02-05] Portadas: fila 5 Parcial 1-8 + 11 ADRs | ✓ VERIFIED | README.md l.42 y docs/README.md l.19: "🚧 Parcial (guías 1-8 listas; continúa en fases 3+)"; "11 ADRs" en fila 4 de ambos; sin "1-4 listas" ni "8 ADRs" |
| 44 | [02-05] Stack del README raíz menciona JWT y zustand | ✓ VERIFIED | README.md: jwt ×2, zustand ×1 (párrafo de stack) |
| 45 | [02-05] Cadena Siguiente continua + guide-only | ✓ VERIFIED | guia-04→05 (l.1030), 05→06 (l.1096), 06→07 (l.966), 07→08 (l.872), 08→fase 3 (l.488); exactamente 8 guia-*.md; `git ls-files -- backend frontend` → 0 |

**Score:** 41/45 truths verified (4 present, behavior-unverified — las 4 Success Criteria del ROADMAP, cuyo runtime se ejecuta en el UAT delegado)

### Decision Coverage

```
gsd-tools query check.decision-coverage-verify 02-CONTEXT.md →
{ skipped: false, blocking: false, total: 15, honored: 15, not_honored: [], message: "All trackable CONTEXT.md decisions are honored by shipped artifacts." }
```

15/15 decisiones D-19..D-33 rastreadas en 02-CONTEXT.md aparecen en los artefactos entregados. Gate no-bloqueante por diseño.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|-----------|--------|---------|
| docs/04_arquitectura/contrato_api.yaml | Contrato 0.2.0 superficie auth (D-15) | ✓ VERIFIED | yaml.safe_load OK: 7 paths, 6 schemas, bearerAuth, copies locked; nota de desvío del 422 (WR-05) l.308-309 |
| docs/04_arquitectura/adr/009-jwt-larga-vida-localstorage.md | ADR JWT con desventaja XSS (D-21) | ✓ VERIFIED | XSS en "Negativas (honestas)" l.55-57 — prohibición P1 honrada |
| docs/04_arquitectura/adr/010-carro-client-side.md | ADR carro client-side (D-27..D-30) | ✓ VERIFIED | Solo pares {producto_id, cantidad}; negativas honestas (fila degradada, no cruza dispositivos) |
| docs/04_arquitectura/adr/011-roles-desde-el-primer-token.md | ADR roles + seed env (D-23/D-24/D-33) | ✓ VERIFIED | ADMIN_EMAIL/CLIENTE_EMAIL, upsert restaura, 403, Para conversar en clase |
| docs/04_arquitectura/README.md | Índice 011 + stack + árbol | ✓ VERIFIED | §5 filas 009-011; §3 4 piezas; §4 extendido; regla 5 y disclaimer intactos |
| docs/02_requerimientos.md | Etapa 2: RF/RNF/RN/HU + actores + P5 | ✓ VERIFIED | Series completas sin renumerar (RF-12 = 0); 17 Dado; §13 P5 mapeada; §14 firma |
| docs/03_diseno.md | USUARIO + procesos 5.0-8.0 + pantallas 4-7 | ✓ VERIFIED | ER + diccionario 5 col; 8 Reglas del proceso; pantallas 4-7 + variante ficha; $26.970 |
| docs/05_desarrollo/guia-05-cuentas-backend.md | Backend de cuentas (AUTH-01/02/03) | ✓ VERIFIED | 1098 líneas; 16/16 bloques Python ast.parse OK; CR-01: `from app.schemas.producto import Error` l.608/715 (0 imports de Error desde schemas.usuario); WR-05 l.691-696; WR-07 l.772/1067 |
| docs/05_desarrollo/guia-06-sesion-frontend.md | Sesión SPA (AUTH-01/02) | ✓ VERIFIED | 968 líneas; store persist + interceptor con sinAuth/llevaBearer (WR-02); normalización detail array (WR-04) l.259-262 |
| docs/05_desarrollo/guia-07-carro.md | Carro persistente (CART-01/02) | ✓ VERIFIED | 874 líneas; store sin precios; write-back WR-03 l.452-458; WR-06 l.149 "no los copies otra vez"; error-evitado "Guardar el precio en el store" l.768 |
| docs/05_desarrollo/guia-08-checkout.md | Checkout protegido + Gran verificación (AUTH-04/GUIDE-02) | ✓ VERIFIED | 493 líneas; guard=UX l.256/475; tabla 12 filas con Authorize; $26.970 |
| docs/05_desarrollo/README.md + docs/README.md + README.md | Estado de fase al día (D-13/D-18) | ✓ VERIFIED | Filas 5-8, 1-8 listas, 11 ADRs, fila 5 🚧 Parcial (no ✅ — prohibición P7) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| contrato 0.2.0 | guías 05-08 | guías implementan el contrato sin desviarse + guia-08 compara /docs contra 0.2.0 | ✓ WIRED | guia-05 cita contrato ×6 con los 4 paths y copies idénticos (parseados ambos lados); guia-08 fila 12 compara uno a uno (7 paths) |
| ADR-009 | contrato | ADR ratifica bearer JWT sin renovación | ✓ WIRED | ADR-009 decide token 7 días; contrato declara "no existe endpoint de renovación (D-19)" |
| README arq §5 | ADRs 009-011 | tabla índice | ✓ WIRED | l.198-200 con decisión y resuelto-por |
| docs/02 | docs/03 §5 | cada RF/HU nuevo tiene fila | ✓ WIRED | l.692-697 (RF-06..RF-11 → sección/proceso/pantalla); ancla ADR l.158-160 |
| docs/02 RN | 02-CONTEXT decisiones | RN citan D-25/D-26/D-27/D-30 | ✓ WIRED | l.123-127 con origen en cursiva |
| guia-05 | ADR-009/011 | pasos citan su decisión | ✓ WIRED | ADR-009 ×2, ADR-011 ×6 |
| guia-06 | guia-04 lib/api.ts + guia-02 | extiende la base con interceptor | ✓ WIRED | lib/api.ts ×3; regla 5 citada l.207 "TODO el HTTP del frontend sale de este archivo" |
| guia-07 | ADR-010 + guia-04 queryKey | store sin precios + hidratación | ✓ WIRED | ADR-010 ×7, D-27 ×6, queryKey ×9, String(id) |
| guia-08 | guia-06 RequireAuth | /checkout envuelta en el guard | ✓ WIRED | RequireAuth ×8 con returnTo |
| guia-04 | guia-05 | eslabón Siguiente | ✓ WIRED | l.1030 enlaza guia-05-cuentas-backend.md |
| Portadas | adr/ | conteo 11 ADRs = directorio | ✓ WIRED | ls = 11 archivos; ambos READMEs dicen "11 ADRs" |

### Data-Flow Trace (Level 4 — equivalente documental)

| Dato | Fuente canónica | Consumidores | Status |
|------|----------------|--------------|--------|
| Copies locked 409/401 | contrato example.detail (parseado) | guia-05 (×3/×5), guia-06 (×3/×4), docs/02 RN-06 | ✓ FLOWING |
| Paths/schemas auth | contrato 0.2.0 | guia-05 routers/schemas espejo; guia-08 fila 12 | ✓ FLOWING |
| Precio del carro | API vigente (hidratación useQueries) | fila, total de línea, Total panel — nunca el store | ✓ FLOWING (D-27: store sin precio verificado en la interfaz ItemCarro) |
| Cantidad en pantalla | min(cantidad guardada, stock) + write-back | stepper, totales, badge (post WR-03) | ✓ FLOWING |
| Rol del token | usuario.rol.value incondicional (guia-05 l.427) | get_current_admin → 403; Authorize /docs | ✓ FLOWING |
| Estado de fase | archivos reales (8 guías, 11 ADRs) | 3 READMEs con 1-8 listas + 11 ADRs | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Contrato 0.2.0 válido y completo | python yaml.safe_load | version 0.2.0; 7 paths; 6 schemas; bearerAuth http/bearer/JWT; responses 201/409/422 + 200/401 + 200/401 + 200/401/403; enum [cliente, admin] | ✓ PASS |
| Bloques Python de guia-05 sintácticamente válidos | python ast.parse × 16 | 16/16 OK | ✓ PASS |
| CR-01: Error importado desde su módulo real | grep schemas.producto/usuario | l.608/715 desde producto; 0 `from app.schemas.usuario import Error` | ✓ PASS |
| WR-01: total correcto | grep 26.970/26.980 en docs/ | $26.970 presente (docs/03 + guia-07 + guia-08); $26.980 = 0 | ✓ PASS |
| WR-02: login exento del interceptor | grep sinAuth/llevaBearer guia-06 | sinAuth ×9, llevaBearer ×4; apiPostForm marca el login | ✓ PASS |
| WR-03: write-back del tapado | grep useEffect guia-07 | l.452-458: cambiarCantidad(producto_id, stock) si cantidad > stock | ✓ PASS |
| WR-04: detail string/array | grep Array.isArray guia-06 | l.259-262 normalización | ✓ PASS |
| WR-06: sin redeclaración de hooks | grep "no los copies" guia-07 | l.149 + bloque solo líneas nuevas | ✓ PASS |
| WR-07: conteo de paths | grep "7 paths"/"4 paths" guia-05 | l.772/1050 "4 paths nuevos", l.1067 "los 7 paths" — calza con parse (7) | ✓ PASS |
| Gates negativos (secreto/librerías vetadas) | grep hex-literals + jose/passlib | 0 matches | ✓ PASS |
| Conteos de estructura canónica | grep -c | piensa 10/9/7/4; mini 13/12/11/4 (≥5/≥5/≥5/≥4) | ✓ PASS |
| Cadena Siguiente + guide-only | grep Siguiente + git ls-files | 04→05→06→07→08→fase 3; 8 guías; 0 archivos backend/frontend | ✓ PASS |
| Runtime de las guías 05-08 en el taller | ls maura-uat | SOLO artefactos fase 1 (sin auth.py/stores/features cuentas-carro-checkout) | ⚠️ PENDIENTE (UAT delegado) |

### Probe Execution

SKIPPED — sin probes declarados en PLAN/SUMMARY ni scripts/ en el repo; las gates de los planes son de contenido documental y fueron re-ejecutadas arriba (yaml, ast.parse, greps, conteos).

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| AUTH-01 | 02-01, 02-02, 02-03 | Crear cuenta con email y contraseña | ✓ SATISFIED (doc) | Contrato registro 201/409/422 + guia-05 + guia-06 Registro; runtime en UAT (truth 1) |
| AUTH-02 | 02-01, 02-02, 02-03 | Login + sesión persistente JWT | ✓ SATISFIED (doc) | Contrato login/perfil + guia-05 token 7 días + guia-06 store persist; runtime en UAT (truth 1) |
| AUTH-03 | 02-01, 02-02, 02-03 | Endpoint admin por rol, claim desde el primer token | ✓ SATISFIED (doc) | Contrato admin/estado 200/401/403 + rol incondicional guia-05 l.422-427 + seed por env; runtime en UAT (truth 2) |
| AUTH-04 | 02-02, 02-04 | Checkout exige sesión con retorno | ✓ SATISFIED (doc) | RF-09 + guia-08 RequireAuth/returnTo + CTA deshabilitado D-31; runtime en UAT (truth 4) |
| CART-01 | 02-02, 02-04 | Agregar/editar/vaciar carro | ✓ SATISFIED (doc) | RF-10 + guia-07 store/stepper/dos pasos; runtime en UAT (truth 3) |
| CART-02 | 02-02, 02-04 | Carro persiste en localStorage, sobrevive full-page loads | ✓ SATISFIED (doc) | RF-11 + guia-07 maura-carro persist + mini-verif F5; runtime en UAT (truth 3) |
| GUIDE-02 | 02-05 | ADRs por fase + contrato actualizado | ✓ SATISFIED | 11 ADRs + contrato 0.2.0 + Gran verificación con fila contrato ↔ /docs; portadas honestas |

Orphans: ninguno — REQUIREMENTS.md mapea exactamente AUTH-01..04 + CART-01/02 a Phase 2 (los 6 [x] Complete); GUIDE-02 (Phase 1) es declarado por 02-05 como cierre transversal. La unión de los campos `requirements` de los 5 planes cubre los 6 IDs de la fase.

### Test Quality Audit

N/A — repo guide-only (D-17): no existen archivos de test. Los "tests" del producto son las mini-verificaciones documentales dentro de las guías (47 en las guías 05-08: 13+12+11+4 más las de la Gran verificación) y la Gran verificación final de 12 filas, cuya ejecución es precisely el UAT delegado pendiente (ver Human Verification).

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| guia-05 l.110/480/991, guia-06 l.207/871, guia-07 l.639 | — | "TODO" en mayúsculas (español: "todo el HTTP", "TODO el estado") | ℹ️ Info | Falsos positivos conocidos heredados de fase 1; no son debt markers |
| (todos los archivos de la fase) | — | TBD/FIXME/XXX/HACK/PLACEHOLDER | — | 0 matches reales |

Sin debt markers sin referencia, sin placeholders de implementación, sin stubs.

### Prohibitions Review (7, judgment-tier — veredicto LLM no autoritativo, flagged for human review)

| # | Prohibición | Status | Evidence |
|---|-------------|--------|----------|
| P1 | No ocultar desventaja XSS en ADR-009 (D-21) | HONORED (grep) | "Negativas (honestas)" l.55-57: "Robo de token por XSS... por hasta 7 días"; también en tabla de opciones l.22 |
| P2 | No inventar reglas de composición de contraseña (D-25) | HONORED (grep) | RN-05 "sin reglas de composición obligatoria: no se exige mayúscula, número ni símbolo" con porqué NIST; contrato description password igual (D-25); grep sin exigencias de composición |
| P3 | Sin credenciales/secretos literales en guías (D-23) | HONORED (grep) | grep SECRET_KEY=[hex] / PASSWORD=[literal] → 0; .env.example solo placeholders (l.92-97); secreto via token_hex(32) |
| P4 | Login sin revelar existencia de email (D-26) | HONORED (grep) | RN-06 + guia-05: 401 único genérico "Credenciales incorrectas" + hash dummy (l.497-510); el 409 claro vive solo en registro; asimetría explicada |
| P5 | Sin precios/snapshots en el carro persistente (D-27) | HONORED (grep) | ItemCarro = {producto_id, cantidad} exacto; error-evitado nº 1 "Guardar el precio en el store" l.768; precio siempre de la hidratación |
| P6 | Guard no presentado como seguridad (D-32) | HONORED (grep) | guia-08 l.256 "UX, no seguridad... Ocultar el botón y proteger la ruta evita que la clienta se pierda, no que un atacante entre" + l.475 lección honesta; guia-06 también lo enseña |
| P7 | Fila 5 del ciclo NO pasa a ✅ (D-13) | HONORED (grep) | README.md l.42 y docs/README.md l.19: "🚧 Parcial (guías 1-8 listas; continúa en fases 3+)" |

**unverified-prohibition — human review recommended**: corrida autónoma (ADR-550 D4): los 7 veredictos anteriores son no autoritativos; se solicita confirmación humana en el checkpoint de fin de fase (o cierre via UAT delegado).

## Human Verification Required

### 1. UAT delegado de la fase 2 (bloqueante para cerrar la fase)

**Test:** En `D:/Repos/maura-uat` (agente, user-delegated per AGENTS.md): construir las guías 05-08 en orden (guia-05: uv add pyjwt "pwdlib[argon2]" python-multipart, .env con SECRET_KEY + 4 credenciales, seed; guia-06: npm install zustand; guia-07/08) y ejecutar la Gran verificación final de guia-08 (12 filas + Authorize en /docs con las cuentas del seed).
**Expected:** Registro nuevo → 201 y aviso esmeralda en /login; email duplicado → 409 con "Ese email ya tiene cuenta, inicia sesión"; login clienta/admin → navbar con email truncado; F5 → sesión viva sin parpadeo; token decodificado con sub/rol/exp/iat (exp−iat = 604800); /api/admin/estado → 200 admin / 403 clienta "Requiere rol admin"; carro: agregar (badge pasa de oculto a N), stepper, quitar, vaciar en dos pasos; carro y badge vivos tras F5 y cierre de pestaña; checkout sin sesión → /login → vuelta AL checkout; CTA "Pagar con Webpay" deshabilitado con su nota; Authorize en /docs ejecuta GET /api/admin/estado → 200. Registrar 12/12 en `02-UAT.md` con `verified_by: agent (user-delegated)`.
**Why human:** Repo guide-only: el runtime vive en la máquina del alumno; esta verificación comprobó el contenido documental de las guías, no su ejecución. El taller hoy NO tiene artefactos de fase 2.

### 2. Runtime de los fixes WR-02 y WR-03 (marcados requires-human-verification)

**Test:** WR-02 — login con credenciales malas (token viejo presente en maura-auth) y observar que NO hay redirección a /login?expirada=1. WR-03 — editar maura-carro en localStorage (cantidad 5 con stock 2), recargar /carro.
**Expected:** WR-02: banner rojo "Credenciales incorrectas" DENTRO de la card (el 401 del login jamás dispara el interceptor). WR-03: filas, total y badge corrigen solos a 2 (write-back del useEffect).
**Why human:** 02-REVIEW-FIX.md marca ambos como "requires human verification (cambia lógica enseñada)" — el código está en las guías pero la lógica nueva no ha corrido.

### 3. Confirmación de las 7 prohibiciones (flag autonomous)

**Test:** Revisar el muestreo de evidencia de la tabla Prohibitions Review (P1-P7).
**Expected:** Confirmar cada HONORED o levantar desviación.
**Why human:** Veredictos LLM no autoritativos en corrida autónoma (ADR-550 D4).

### 4. Formato del goal del ROADMAP (informativo, heredado)

**Test:** `/gsd mvp-phase 2`.
**Expected:** Goal en formato User Story canónico (hoy `user-story.validate` = false; la canónica vive en los PLANs).
**Why human:** El marco MVP exige User Story canónica para el framing de cobertura.

### Gaps Summary

Sin gaps documentales. Las 41 verdades de los 5 planes verifican contra los archivos reales (contrato parseado, 16/16 bloques Python de guia-05 con ast.parse OK, copies locked extraídos de ambos lados, conteos de estructura canónica, cadena Siguiente, invariante guide-only), los 8 findings del review (CR-01 + WR-01..07) están efectivamente corregidos en el código de las guías (verificado grep a grep), las 15 decisiones del CONTEXT están honradas y los 7 requisitos de la fase tienen cobertura sin huérfanos.

Lo que queda es la capa runtime de las 4 Success Criteria del ROADMAP: las guías enseñan el comportamiento y las mini-verificaciones/Gran verificación final instruyen comprobarlo, pero ninguna ejecución ha ocurrido aún (el taller maura-uat contiene solo fase 1). Por eso el estado es **human_needed**: el UAT delegado (agente en maura-uat, esquema user-delegated persistido en AGENTS.md) debe construir las guías 05-08 y ejecutar la Gran verificación final de 12 filas — en particular los dos fixes que cambiaron lógica enseñada (WR-02 interceptor exento del login, WR-03 write-back del stock).

---

_Verified: 2026-09-29T18:26:06Z_
_Verifier: Claude (gsd-verifier)_
