---
status: partial
phase: 04-panel-de-administraci-n-y-asistente-ia
source: [04-VERIFICATION.md]
started: 2026-10-01T12:00:00.000Z
updated: 2026-10-01T22:05:00.000Z
verified_by: agent (user-delegated per AGENTS.md — taller D:/Repos/maura-uat)
---

## Current Test

[testing paused — 1 item outstanding: test 2 (happy path Gemini) blocked third-party a la espera de la GEMINI_API_KEY del usuario (D-60)]

## Tests

### 1. UAT delegado de fase 4 (Gran verificación final de guia-15, 13 filas)
expected: Todas las filas de la Gran verificación final pasan runtime en maura-uat sobre la app construida hasta guia-15; resultados registrados acá con verified_by: agent (user-delegated).
result: pass
verified_by: agent (user-delegated)
evidence: |
  Corrida 2026-10-01 (sesión /gsd-verify-work 4). Guías 12-15 construidas en maura-uat por
  agentes alumno (comandos literales + archivos byte-por-byte + mini-verificaciones): API
  0.3.0 → 0.4.0 con las 7 ops admin (guia-12, build verde), SPA del panel completa con
  RequireAdmin/LayoutAdmin/3 pantallas (guia-13, npm run build verde 169 módulos), backend
  del asistente con google-genai 2.26.0 dentro del pin >=2.25,<3 (guia-14, /api/asistente
  con responses 200/422/429/503 y security público), BurbujaAsesora montada en Layout +
  build final verde 170 módulos (guia-15). Gran verificación final — 12/13 filas en verde
  + fila 8 bloqueada por designio (requiere GEMINI_API_KEY del alumno, D-60; las filas 9,
  10 y 13 no dependen de key, como la propia guía advierte):
  (1) Roles: los 7 paths admin → admin 200/201 y clienta 403 "Requiere rol admin" uno a
  uno (batería curl propia); (2) clienta con sesión fuerza /admin → "No tienes acceso al
  panel" + "El panel de administración es solo para la dueña de la tienda." + "Volver a la
  tienda", A SECAS (sin navbar ni subnav — validado EN VIVO en navegador); "Volver a la
  tienda" la deja en el inicio con navbar saludándola (sesión viva) y SIN link "Panel";
  sin sesión /admin → login → admin entra → aterriza EN /admin (returnTo, verificado con
  waitForURL); (3) CRUD: POST nace activo (id 15, activo=True, sku panel-6d8d3786 generado
  — visible solo en BD, como el contrato manda), dos PUT mismo body → 200/200 mismo
  estado, inyección "activo": false en body → 200 y activo sigue True (allow-list);
  (4) badge "Stock bajo" EN VIVO exacto en los 3 activos ≤5 (Gajo de Pomelo 2 u., Rosa de
  Río 2 u., Frutilla Fresca 4 u.; ni en Vainilla 6 u. ni en inactivos) y calza con
  métricas productos_stock_bajo=3; (5) soft delete: PATCH prod 1 activo=false → catálogo
  14→13 (desaparece id 1), MAURA-000003 conserva snapshot nombre=Brisa de Naranja
  precio=7990, reactivar → 14; (6) huérfana PENDING fresca (MAURA-000012 y 000013 creadas
  por checkout clienta, el canon de fase 3): anular → 200, repetir → 409 "Ese pedido ya
  no está en curso.", clienta la ve cancelled en SU historial; (7) métricas vs BD real:
  ingresos 48440 == SUM(paid), conteos {pending 0, paid 4, cancelled 7, rejected 2} ==
  groupby, top_5 == agregación snapshot (Brisa de Naranja 4, Gajo de Pomelo 1, Frutilla
  Fresca 1 — mismo conjunto; orden de empate no especificado por diseño), stock bajo 3==3;
  (8) BLOQUEADA sin key — la burbuja SÍ abrió en vivo con la bienvenida LOCAL "¡Hola! Soy
  la asesora de Maura…" (cero requests: constante hardcodeada, sin fetch al montar) y el
  placeholder "¿Qué aroma buscas?"; el happy path con cards queda en test 2; (9) topes:
  mensaje 501 chars → 422 y historial 11 → 422 (antes de tocar Gemini); (10) sin key:
  POST → 503 "La asesora no está disponible en este momento. Inténtalo más tarde." y en
  vivo la burbuja roja con Reintentar + la burbuja SIGUE en su lugar; tienda operativa:
  salud/catálogo/login/pedidos/panel todos 200; (11) burbuja EN VIVO en portada, login y
  catálogo (con y sin sesión) y AUSENTE en /admin (dos ramas de layout, cero
  condicionales); (12) contrato ↔ /docs: versiones 0.4.0 == 0.4.0, 17 paths == 17 paths
  diferencia NINGUNA, /api/asistente sin candado con 200/422/429/503 declarados, PATCH
  estado con 401/403/404/409/422, Authorize admin = bearer flow probado en (1); (13) grep
  del build: grep -r "GEMINI_API_KEY" dist/ → CERO coincidencias (exit 1) con control
  positivo (grep "asesora" encuentra), PowerShell Select-String recursivo → 0. El estado
  429 no se provoca sin quemar cuota (la propia guía lo advierte y delega en el wrapper
  de guia-14, ya probado con los 422).
  DESVÍOS ENCONTRADOS Y CORREGIDOS EN GUÍA (+ taller cuando aplicó, regla dos lugares):
  D-4-1 (g12) la mini-verificación del POST imprimía r.json()['sku'] pero ProductoAdmin
  no expone sku (contrato 0.4.0; guia-13 jamás lo muestra) → KeyError; el print pasa a
  id+activo y la narrativa enseña que el sku vive solo en BD [fb6fb5d].
  D-4-2 (g13 paso 2) al bajar BADGES a lib/badges, Pedidos.tsx quedaba con EstadoPedido
  huérfano en el import type y noUnusedLocals rompía el build; la guía ahora indica
  quitarlo; taller: fix aplicado por el agente [c56c82f].
  D-4-3 (g13 paso 9 🧠 + verificación final #2 + g15 fila 2) "su navbar sigue en pie
  porque LayoutAdmin la renderiza" era FALSO: RequireAdmin veta la RAMA y la clienta ve
  NoAutorizado a secas (como el 🧠 del paso 4 y el comentario de main.tsx ya decían);
  corregido en los 3 pasajes + fila 2 y RATIFICADO EN VIVO en navegador [c56c82f].
  D-4-4 (g13 paso 6 🧠) la narrativa prometía hidratar "reusando la key [producto, id]"
  pero el código hace apiGet fresco; narrativa ahora enseña lo que el código hace
  [c56c82f].
  D-4-5 (g14 paso 4) el comando de la mini-verificación accedía
  historial.items.properties.texto pero Pydantic v2 emite $ref → $defs/MensajeHistorial
  → KeyError 'properties'; comando corregido + narrativa del $defs como lección
  [7a0b643].
  D-4-6 (g14 paso 1) "Debe imprimir 2.25.x" envejeció (hoy resuelve 2.26.0 dentro del
  pin) → texto enseña piso/techo [7a0b643]. D-4-7 (g14 paso 3) "(junto a las de la
  etapa 2)" era ambiguo → bloque Etapa 4 al final [7a0b643]. D-4-8 (g14 paso 8)
  "golpes 2, 3 y 4" → "golpes 2 y 3" (hay tres) [7a0b643].
  D-4-9 (g13/g15) "uv run fastapi dev app/main" sin .py aborta con el fastapi-cli
  vigente ("Path does not exist app\main"); uniformado a app/main.py como el resto del
  corpus (guias 01/02/04/05/09) [db1fd7f].
  Notas de entorno (NO desvíos de guía): paso del alumno D-60 omitido en el taller (sin
  key, por diseño de este UAT → test 2); findstr invocado desde Git Bash corrompe switches
  MSYS (la guía lo ofrece como variante PowerShell; resuelto con Select-String); el
  hot-reload de fastapi dev se cuelga tras editar main.py (la guía pide reinicio).
  Cadenas <verify> de los planes re-ejecutadas tras cada fix: g12-ok, g13-ok, g14-ok.
  Estado final del taller: 15 productos (13 activos), pedidos 0 pending / 4 paid /
  7 cancelled / 2 rejected, .env sin key real, servidores detenidos y puertos libres.

### 2. Happy path del asistente con llamada real a Gemini
expected: Con la GEMINI_API_KEY del usuario (creada gratis en aistudio.google.com, D-60), la burbuja responde recomendaciones del catálogo real con product cards válidas (AIAS-01/02 runtime). Sin key, este ítem queda bloqueado — la degradación 503 sí se verifica sin key.
result: blocked
blocked_by: third-party
reason: "Requiere la GEMINI_API_KEY del usuario (D-60, Open Question 1): en este entorno no hay key ni autorización para crearla. Lo verificable sin key quedó verde en el test 1: bienvenida local en vivo, topes 422, degradación 503 con copy exacto + Reintentar + burbuja en pie, y tienda 100% operativa. Con una key (crear gratis en aistudio.google.com, agregar GEMINI_API_KEY=... al .env del backend y reiniciar), este ítem se desbloquea y también la fila 8 de la Gran verificación."

### 3. Ratificar las 5 flagged assumptions unclassified del edge probe (ADMN-02/03/04, AIAS-01/02)
expected: Confirmar contra la corrida UAT que los supuestos marcados (edge probe unclassified) se comportan como los planes asumieron; ratificar o abrir gaps.
result: pass
verified_by: agent (user-delegated)
evidence: |
  Las 5 flagged assumptions de 04-03-PLAN y 04-04-PLAN ratificadas contra la corrida
  runtime — ninguna abrió gap:
  ADMN-02 RATIFICADA: el umbral vive en el backend como STOCK_BAJO_UMBRAL=5 sobre
  productos ACTIVOS (métricas productos_stock_bajo=3 == count SQL de activos ≤5) y NO
  existe endpoint propio ni UI de configuración del umbral; el badge del listado usa la
  constante espejo del frontend (lib/badges.ts STOCK_BAJO=5, RN-14/Pitfall 6: dos
  constantes con nombre en dos tiers que dicen lo mismo) — en vivo el badge calzó 3/3
  contra métricas.
  ADMN-03 RATIFICADA: el UPDATE condicional WHERE estado='pending' con rowcount 0 → 409
  bastó en runtime: anulación 200 → repetición 409 con el copy locked "Ese pedido ya no
  está en curso." (probado 3 veces: MAURA-000001 guia-12, 000002/000009 guia-13,
  000012/000013 batería final); dos pestañas concurrentes son el mismo mecanismo (la
  segunda escritura ve rowcount 0).
  ADMN-04 RATIFICADA: las 4 métricas computadas por agregaciones SQLAlchemy sobre las
  tablas existentes calzaron contra la BD real de fase 3: ingresos 48440, conteos por
  estado exactos, top_5 por líneas snapshot (conjunto exacto; el orden de empate no está
  especificado ni prometido) y stock bajo 3.
  AIAS-01 RATIFICADA: round-trip único por envío (useMutation → UN POST /api/asistente,
  sin polling ni streaming — el 503 llegó en un solo round-trip por el proxy /api de
  Vite, sin CORS nuevo); el historial visible vive en el estado del componente (la
  conversación persistió en pantalla entre navegaciones del panel de la burbuja; F5 parte
  de cero, D-58 verificado por código).
  AIAS-02 RATIFICADA (wiring runtime + happy path tras la key): la muralla doble está
  cableada y viva (system prompt con catálogo activo por request + validación de ids
  contra BD + truncado a 3 en el service; ChatRespuesta productos max_length=3; el 422
  de los topes validó ANTES de tocar la red); el efecto sobre una respuesta REAL de
  Gemini es exactamente la parte que el propio supuesto deja tras checkpoint:human-verify
  (Open Question 1) — mismo bloqueo del test 2, no un gap.

### 4. Decisión editorial IN-01 — espejo 422 del editor cubre 5/7 campos (guia-13)
expected: El usuario decide: agregar los copys de campo para descripcion/imagen (toca los copys locked del UI-SPEC) o dejar el espejo parcial con narrativa. Abierto por diseño en 04-REVIEW-DISPOSITION.md.
result: pass
decided_by: user (2026-10-01)
decision: Dejar el espejo 5/7 con narrativa — viñeta agregada al 🧠 del paso 6 de guia-13 que enseña el borde: el 422 de descripcion/imagen vacías cae en el banner genérico (copy textual citado); el espejo es parcial POR DISEÑO y la API sigue siendo la autoridad. UI-SPEC y copys locked intactos. Registrado en 04-REVIEW-DISPOSITION.md (IN-01 → fixed).

### 5. Decisión editorial IN-03 — cláusula auto-pickup del SDK en ADR-017
expected: El usuario decide la redacción de la cláusula del ADR (cita del auto-pickup vs lo que guia-14 enseña). Abierto por diseño.
result: pass
decided_by: user (2026-10-01)
decision: Cláusula aclaratoria — la cita del auto-pickup se conserva como evidencia firmada del SDK y se cierra la lectura: capacidad del SDK vs decisión del proyecto (api_key explícita desde Settings, con el gotcha del .env de guia-14). Aplicada en ADR-017 §Evidencia firmada. Registrado en 04-REVIEW-DISPOSITION.md (IN-03 → fixed).

## Summary

total: 5
passed: 4
issues: 0
pending: 0
skipped: 0
blocked: 1
