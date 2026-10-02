---
status: complete
phase: 04-panel-de-administraci-n-y-asistente-ia
source: [04-VERIFICATION.md]
started: 2026-10-01T12:00:00.000Z
updated: 2026-10-01T15:24:57.000Z
verified_by: agent (user-delegated per AGENTS.md — taller D:/Repos/maura-uat)
---

## Current Test

[sin ítems pendientes — 5/5 pass; test 2 re-verificado tras el rework Groq (plan 04-08)]

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
  BACKSTOP ADMN-01 (dos admins, concurrencia) OBSERVADO con matiz: dos PUT
  concurrentes reales (threads) sobre el mismo producto con bodies que difieren en
  precio/stock → ambos 200 y el estado final fusiona POR CAMPO (precio del admin A,
  stock del admin B) — SIN corrupción ni writes a medias: el ORM solo re-escribe las
  columnas que cada sesión cambió, así que cada campo queda con el último valor que
  alguien le escribió explícitamente. La promesa "no corrompen datos" se sostiene;
  la frase "UPDATE completo por id… la última queda" era imprecisa bajo interleave →
  D-4-10: glosario (l.31) y docstring de actualizar() de guia-12 corregidos a
  last-write-wins POR CAMPO + docstring del taller sincronizado; g12-ok re-verde.
  Estado final del taller: 15 productos (13 activos), pedidos 0 pending / 4 paid /
  7 cancelled / 2 rejected, .env con la GEMINI_API_KEY del usuario (ver test 2),
  servidores detenidos y puertos libres.

### 2. Happy path del asistente con llamada real al servicio de IA (Groq)
expected: Con la GROQ_API_KEY del usuario (creada gratis en console.groq.com, D-63/D-60-supercedido), la burbuja responde recomendaciones del catálogo real con product cards válidas (AIAS-01/02 runtime); sin key, la degradación 503 amable con la tienda operativa (D-61). Re-verificado tras el rework Groq (planes 04-06..04-08, ADR-018).
result: pass
verified_by: agent (user-delegated)
evidence: |
  RE-VERIFICACIÓN Groq 2026-10-01 (plan 04-08 Task 3): taller D:/Repos/maura-uat
  re-integrado siguiendo la guia-14 REESCRITA como lo haría un alumno (regla dos
  lugares de AGENTS.md): (1) `uv add "groq>=1.7,<2"` → groq 1.7.0 instalado y
  `uv remove google-genai` → 2.26.0 removido (pyproject con el pin, sin genai);
  (2) services/asistente.py reescrito con los bloques del paso 5 de la guía
  (`from groq import Groq, GroqError, RateLimitError`, MODELO_ASISTENTE =
  "openai/gpt-oss-120b", client lazy construido DENTRO del try con
  api_key=settings.groq_api_key, chat.completions.create con response_format
  json_schema strict: true + Recomendacion.model_json_schema(),
  RateLimitError → CuotaAgotada, GroqError → AsistenteNoDisponible, jamás 500);
  Recomendacion del taller con model_config = ConfigDict(extra="forbid")
  (mini-verificación del paso 4 en verde: "500 500 10 3 | False ['productos',
  'respuesta']" — additionalProperties: false + required completos); Settings
  con groq_api_key: str | None = None (mini-verificación paso 3: "None |
  PydanticUndefined"); aislamiento grep "from groq" backend/app → SOLO
  services/asistente.py; .env.example con GROQ_API_KEY= vacía; router solo con
  las 2 descripciones agnósticas del contrato (D-66).
  BATERÍA DEL PASO 8 (backend `uv run fastapi dev app/main.py`, forma D-4-9):
  - HAPPY PATH 200 REAL: POST /api/asistente "algo cítrico para el día" → 200
    con respuesta en la voz de Maura ("Si buscas algo cítrico, te recomiendo
    Brisa de Naranja, una explosión de naranja...") e ids [1, 2] que EXISTEN en
    el catálogo activo del taller (ids validos: True contra /api/productos,
    cards: 2 — la muralla D-56 funcionó contra el modelo real).
  - TOPES 422: mensaje 501 chars → 422 e historial de 11 entradas → 422 (antes
    de tocar la red, RN-16).
  - DEGRADACIÓN SIN KEY: GROQ_API_KEY comentada + reinicio → POST → 503 con el
    copy exacto "La asesora no está disponible en este momento. Inténtalo más
    tarde." | salud: 200 | catálogo vivo (14 activos) — D-61 runtime: la tienda
    100% operativa sin key. Key restaurada y reinicio para volver al happy path.
  - MODELS.LIST (D-64): 11 modelos, INCLUYE openai/gpt-oss-120b — el
    MODELO_ASISTENTE existe hoy (calza con el probe del research).
  - BACKSTOP AIAS-03 (concurrencia): DOS llamadas en PARALELO (threads) al
    endpoint público → ambas 200 con respuestas en la voz de Maura, NINGUNA
    500 ni excepción, GET /api/salud 200 tras la ráfaga — sin estado compartido
    entre requests (junto al backstop del test 1 D-4-10, cierra la observación
    de los 3 gaps de 04-VERIFICATION salvo ratificación de cierre).
  - GREP DEL BUILD (fila 13, A6): npm run build verde (tsc -b && vite build,
    375.54 kB JS) y grep -r "GROQ_API_KEY" dist/ → CERO coincidencias (exit 1)
    con control positivo (grep "asesora" encuentra en el bundle) — AIAS-03: la
    key jamás salió del backend.
  NOTA taller-only (Pitfall 9, 04-RESEARCH — JAMÁS en la guía): el middlebox
  local de ESTA máquina bloquea la revocación TLS hacia api.groq.com; el
  service del taller inyecta truststore (import truststore +
  truststore.inject_into_ssl() al arranque del módulo, truststore 0.10.4 en el
  venv vía uv pip install — fuera de pyproject) y así corrió el happy path y
  las paralelas 200. El comando models.list del paso 8 ejecutado EN FRIO (sin
  importar el service) falla por TLS en esta máquina — variante taller-only
  con truststore inyectado a mano corre 200; las máquinas de los alumnos no
  tienen el middlebox. No es defecto de guía: la regla dos lugares NO aplica.
  Sin sesión de navegador en esta corrida: la burbuja ya fue validada EN VIVO
  en el test 1 (filas 8/11: bienvenida local, burbuja en pie en el 503) y el
  frontend NO cambió con el rework (rebuild de las mismas fuentes); el happy
  path se verificó a nivel de API (el contrato que la burbuja consume).
  NOTA de cierre: la GROQ_API_KEY del taller ES la key del usuario (creada por
  él en console.groq.com, sesión 04-UAT addenda) — el ítem humano end-of-phase
  de 04-VERIFICATION (happy path con la key del usuario) queda CUBIERTO punta
  a punta por esta corrida para su ratificación en el cierre de fase.
  Estado final del taller: servidores detenidos, puertos 8000/5173 libres,
  .env con GROQ_API_KEY activa.

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
passed: 5
issues: 0
pending: 0
skipped: 0
blocked: 0

## Addenda post-cierre (2026-10-01, a pedido del usuario): asistente Groq EN VIVO en navegador

Gap detectado por el usuario tras el cierre de la fase: la re-verificación del test 2 durante el
plan 04-08 fue a nivel API (curl al endpoint) y las verificaciones "EN VIVO en navegador" del UAT
original eran de la era Gemini. Corrida de cierre (agent, browser-use sobre el taller con los dos
servidores levantados — backend 8000, frontend 5173 —, sin workaround TLS: api.groq.com respondió
directo desde esta máquina):

1. Burbuja "Pregúntale a Maura" visible en la portada → panel "Asesora de aromas" abre con la
   bienvenida LOCAL (cero requests, cero cuota).
2. Mensaje "algo cítrico para el día" → respuesta REAL de Groq en la voz de Maura ("¡Hola! Te
   recomiendo Brisa de Naranja, Limón y Albahaca y Gajo de Pomelo, perfectos para darle frescura
   cítrica al día…") con **3 product cards** (Brisa de Naranja $7.990 → /productos/1, Limón y
   Albahaca $6.990 → /productos/2, Gajo de Pomelo $8.990 → /productos/3 — familia Cítricas,
   truncado a 3 por la muralla D-56).
3. Clic en la card "Brisa de Naranja" → navega a la ficha /productos/1 con su heading.
4. Smoke API paralelo: POST /api/asistente → 200 en 2,1 s con ids [1,2] válidos.

AIAS-01/02 verificados punta a punta EN NAVEGADOR contra el backend Groq re-integrado. Sin bugs —
nada que corregir en los dos lugares. Los servidores del taller quedaron CORRIENDO para que el
usuario pruebe personalmente (frontend http://localhost:5173, burbuja abajo a la derecha).

## Addenda 2 (2026-10-01): defecto reportado por el usuario — la asesora respondía off-topic

El usuario probó en vivo y reportó que la asesora contestaba preguntas ajenas a la tienda ("cuál
es la capital de Francia?" → "La capital de Francia es París."). **Diagnóstico:** hueco de diseño
en el prompt de guia-14 (D-56 define QUÉ productos recomendar, nunca DE QUÉ se habla — una
respuesta off-topic con lista vacía pasa tranquila por la muralla y el contrato). **Decisión del
usuario:** deflectar en personaje (opción recomendada). **Fix en los dos lugares** (guia-14 Paso 5
prompt + 🧠 + golpe "pregunta trampa" en la batería del Paso 8; espejo en taller
services/asistente.py): cláusula de alcance por primacía (regla primera), con ejemplo explícito
(la capital NO se dice) y anclada al campo `respuesta` del schema.

**Verificado en vivo post-fix** (API y navegador): capital → "No sé nada de eso, cuéntame qué
frescura buscas en tu aroma."; Don Quijote → deflexión equivalente; on-topic sin regresión
("algo floral para la noche" → Jazmín de Tarde/Rosa de Río/Peonía Blanca, ids [4,6,5] válidos).

**Nota de entorno del taller (NO defecto de guía):** durante el debugging el backend respondía
con el prompt VIEJO pese a los reinicios — habían quedado 3 procesos python simultáneos
escuchando el 8000 (reloads colgados de corridas anteriores) y las requests caían en
round-robin al más antiguo. `netstat -ano` mostraba PIDs fantasma que `taskkill` no mataba;
`Get-NetTCPConnection` (PowerShell) es la autoridad para ver el dueño real, y el arranque limpio
exige matar TODOS los python del taller y verificar el puerto libre antes de subir. Lección
hermana del "hot-reload se cuelga" ya documentada: si un fix de prompt "no funciona", verifica
que el proceso que responde sea el que crees.
