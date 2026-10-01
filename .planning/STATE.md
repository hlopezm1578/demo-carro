---
gsd_state_version: "1.0"
milestone: v2.25.0
current_phase: 04
current_phase_name: Panel de administración y asistente IA
current_plan: 3
status: executing
stopped_at: Completed 04-07-PLAN.md
last_updated: "2026-10-01T15:02:41.670Z"
last_activity: 2026-10-01
last_activity_desc: Phase 04 execution started
state_head: 61aff278563b1803c7f2c9357d8c1dd01f1533c1
progress:
  total_phases: 5
  completed_phases: 3
  total_plans: 24
  completed_plans: 23
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-09-30)

**Core value:** La guía documenta el ciclo de vida completo y, siguiéndola en orden, la aplicación queda construida y operativa: tienda con catálogo, carro, checkout Webpay sandbox, cuentas JWT, panel admin y asistente IA sobre el catálogo real.
**Current focus:** Phase 04 — Panel de administración y asistente IA

## Current Position

Phase: 04 (Panel de administración y asistente IA) — EXECUTING
Current Plan: 3
Total Plans in Phase: 8
Status: Ready to execute
Last activity: 2026-10-01 — Phase 04 execution started

Progress: [██████░░░░] 60%

## Performance Metrics

**Velocity:**
- Total plans completed: 16
- Average duration: -
- Total execution time: -

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01 | 6 | - | - |
| 02 | 5 | - | - |
| 03 | 5 | - | - |

**Recent Trend:**
- Last 5 plans: -
- Trend: -

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 01 P01-01 | 9min | 3 tasks | 22 files |
| Phase 01 P01-02 | 12min | 3 tasks | 5 files |
| Phase 01 P01-03 | 11min | 3 tasks | 11 files |
| Phase 01 P01-04 | 11min | 3 tasks | 3 files |
| Phase 01 P01-05 | 6min | 3 tasks | 7 files |
| Phase 01 P06 | 4min | 2 tasks | 2 files |
| Phase 02 P01 | 15 min | 3 tasks | 5 files |
| Phase 02 P02 | 8 min | 2 tasks | 2 files |
| Phase 02 P03 | 16 min | 2 tasks | 2 files |
| Phase 02 P04 | 13 min | 2 tasks | 2 files |
| Phase 02 P05 | 3 min | 2 tasks | 4 files |
| Phase 03 P03-01 | 60 min | 2 tasks | 1 files |
| Phase 03 P02 | 8 min | 3 tasks | 5 files |
| Phase 03 P03 | 13 min | 2 tasks | 2 files |
| Phase 03 P04 | 25 min | 2 tasks | 2 files |
| Phase 03 P05 | 10 min | 2 tasks | 4 files |
| Phase 04 P01 | 12 min | 3 tasks | 5 files |
| Phase 04 P02 | 9 min | 2 tasks | 2 files |
| Phase 04 P03 | 18 min | 2 tasks | 3 files |
| Phase 4 P05 | 2 min | 2 tasks | 3 files |
| Phase 04 P06 | 10 min | 3 tasks | 7 files |
| Phase 04 P07 | 16 min | 2 tasks | 2 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Roadmap: granularidad coarse → 5 fases MVP verticales (consolida las 8 fases sugeridas por research); orden: catálogo → auth/carro → checkout → admin+IA → deploy
- Roadmap: spike de retorno Webpay vive dentro de la Phase 3, antes de redactar su guía de desarrollo
- Roadmap: GUIDE-02/GUIDE-03 se anclan en Phase 1 (convenciones ADR + contrato API + primera guía paso a paso); GUIDE-01 se cierra en Phase 5 con el ciclo completo
- [Phase 01]: Contrato API-first aprobado antes del codigo: docs/04_arquitectura/contrato_api.yaml (OpenAPI 3.0.3, paths /api/salud, /api/productos, /api/productos/{producto_id}; schemas Error/ProductoResumen/ProductoDetalle) — GUIDE-02/D-15
- [Phase 01]: Backend en capas routers->services->repositories con sesion inyectada; los routers no importan sqlalchemy (Session se re-exporta desde app.database) y solo main.py arma la app
- [Phase 01]: Seed converge por upsert de SKU al estado canonico de 12 productos (D-05/D-06/D-07): re-ejecutar restaura stock/precios demo sin duplicar filas ni resetear IDs (STORE-04)
- [Phase 01]: Numeracion canonica del ciclo fijada en docs 01-02 (D1-D6/P1-P8/C1-C4/CS1-CS5 y RF-01..05/RNF/RN/HU-01..04): ADRs, contrato y guias la citan en cadena; renumerar rompe la trazabilidad (costly)
- [Phase 01]: docs/README.md refleja el cierre de fase 1 por fase GSD (D-13): filas 1-4 OK, fila 5 parcial guias 1-4, filas 6-8 pendientes; P5-P8 del doc 02 quedan trazadas a las etapas 2/3/4 del roadmap
- [Phase 01]: El repositorio es guide-only (D-17): solo guias, sin codigo de aplicacion en el repo — el codigo vive dentro de las guias como bloques que el alumno copia (modelo demo-cine). Codigo backend retirado en fc93522. — El usuario corrigio el alcance a mitad de la ejecucion de la fase 1: el producto es la guia documental, no la aplicacion construida por GSD. Afecta planes, verificaciones (docs-only) y decisiones D-08/D-09/D-10/D-11 reinterpretadas como contenido de guia.
- [Phase 01]: Fase 1 cierra su arquitectura con 8 ADRs 001-008 (formato demo-cine); ADR-008 registra el invariant guide-only D-17/D-18 como decision de arquitectura y ADR-007 ancla contrato_api.yaml con cierre /docs = contrato
- [Phase 01]: README raiz (D-18) es la portada viva del producto: tabla de 8 fases con estado real que avanza por fase GSD; el arbol de carpetas de 04_arquitectura se declara como el proyecto del alumno, no contenido del repo
- [Phase 01]: Reglas de dependencia numeradas fijadas en 04_arquitectura (routers sin SQLAlchemy, repositories sin reglas, services sin HTTP, solo main.py arma la app, todo HTTP frontend por lib/api.ts, features sin imports cruzados) — las guias 01-04/01-05 las citan
- [Phase 01]: Guias 01-02 de 05_desarrollo: estructura canonica fijada (blockquote/terminos/pasos con piensa+mini-verificacion/error evitado/cierre); guia-01 narra el backend verificado retirado (git 364dee6) y guia-02 ancla sus bloques en los patrones verificados de 01-RESEARCH + copies del UI-SPEC
- [Phase 01]: Tabla del README de 05_desarrollo con estado honesto por fase (D-13): guia-03/04 pendientes hasta que 01-05 las escriba; el gate node >= 22.22 vive como paso 1 del alumno en guia-02 (D-17), no del pipeline
- [Phase 01]: Guias 03-04 de 05_desarrollo cierran la fase: guia-03 narra el seed verificado (upsert 12 SKU, git de0253e) con el gotcha del Enum; guia-04 une los tiers y fija la convencion 'Gran verificacion final' (tabla numerada CS/RF + fila contrato <-> /docs, ADR-007) que replican las fases 2-5
- [Phase 01]: Paso de descarga de fotos (D-08 reinterpretado): la guia ensena al alumno a bajar 12 fotos stock licencia libre a SU frontend/public/products/{sku}.jpg — unica seccion con URLs de terceros y gate negativo sin src https; fila 5 del ciclo queda en Parcial (guias 1-4 listas; continua en fases 2+)
- [Phase 01]: [Phase 01 P06] G-01-4 cerrado por Opcion A (declarar el 404 en responses del router) y no por Opcion B (nota que normaliza el desvio): la fila 11 existe para detectar drift; cuatro lineas declarativas ensenan un concepto real de FastAPI
- [Phase 01]: [Phase 01 P06] Direccion del fix guia -> contrato: contrato_api.yaml intacto y WR-01/WR-02 abiertos; prohibido declarar el 422 en responses de guia-04
- [Phase 01]: [Phase 01 P06] Bloque de contenido del .gitignore de guia-01 byte-identico (el gap era quien crea el archivo); menciones de guia-03 quedan validas sin editarla
- [Phase 01 cierre]: UAT delegado al agente (instrucción persistida en AGENTS.md): las verificaciones runtime se ejecutan construyendo/modificando D:/Repos/maura-uat siguiendo las guías; sesión 01-UAT 4/4 PASS (re-ejecuciones G-01-1 en maura-uat/refix y G-01-4 sobre el backend existente)
- [Phase 01 cierre]: Seguridad verificada en 01-SECURITY.md (19 amenazas, threats_open 0, ASVS 1, registro de plan-time); ui-review omitido con causa (repo guide-only D-17: sin código frontend que auditar)
- [Phase 02]: Login form-urlencoded OAuth2 (username=email) en el contrato 0.2.0: habilita Authorize en /docs con las cuentas del seed y calza con el tutorial oficial de FastAPI
- [Phase 02]: Copies locked D-26 grabados como example.detail del 409/401 en el contrato; sin endpoint de renovacion (D-19) y bearerAuth type http + scheme bearer
- [Phase 02]: [02-01] ADRs 009-011 con negativas honestas (XSS dicha por D-21); arbol del alumno extendido con rutas completas manteniendo fase 1 byte-intacta
- [Phase 02]: docs/02 extiende sus series sin renumerar: etapa 2 = RF-06..RF-11 (AUTH-01..04 + CART-01/02, origen P5), RNF-05/06, RN-05..RN-09, HU-05..HU-08; actores Clienta (con cuenta) y Admin (dueña); P5 mapeada en §13 y CART-03/PAY-01..04 explícitos para etapa 3
- [Phase 02]: RN-05 fija contraseña mínimo 8 SIN composición obligatoria citando NIST longitud-sobre-complejidad (D-25) y RN-06 la asimetría 401 genérico/409 claro con su porqué (D-26) — ambas como reglas de requerimiento antes de las guías
- [Phase 02]: docs/03: USUARIO con email único como clave del upsert (D-23/D-24) y hash que jamás cruza la frontera (RN-07); almacén A2 localStorage documentado como decisión de diseño, no de tecnología
- [Phase 02]: Pantallas 4-7 con copys locked del UI-SPEC (avisos login, 409 registro, vaciado en dos pasos, CTA pago deshabilitado D-31) y ficha gana 'Agregar al carro' como variante (D-29)
- [Phase 02]: Decisiones de diseño §2.3 de docs/03 continúan la serie (7-10) y citan ADR-009/010/011: la cadena P5 → RF-06+ → HU-05+ → pantalla 4+ → ADR-009+ queda continua
- [Phase 02]: [02-03] Orden de pasos de guia-05 reordenado por dependencia de imports (models->schemas->repository->security->services->routers, como guia-04): security.py importa UsuarioRepository y el orden literal del plan reventaria con ImportError
- [Phase 02]: [02-03] Settings gana SettingsConfigDict(env_file=.env): sin env_file pydantic-settings jamas lee el archivo — una linea que hace real al .env de guia-01 y habilita el fail-fast de secret_key
- [Phase 02]: [02-03] Login de guia-06 consulta /api/auth/perfil en dos tiempos (token primero, usuario despues) y comprueba la sesion guardada al entrar: vuelve observable al interceptor 401 (D-22) con un token corrupto sin esperar a guia-08
- [Phase 02]: [02-03] Espejo de validacion honesto: login valida solo email (el backend no valida forma de contrasena ahi); registro valida las dos reglas del 422 (RN-05). /api/admin/estado reusa CatalogService: cero SQL en el router
- [Phase 02]: [02-04] useQueries hidrata los N ítems variables del carro (regla de hooks veta useQuery en loop de largo variable) con el queryKey de la ficha PERO String(id): ("producto", 1) y ("producto", "1") son cachés distintas — gotcha narrado como error-evitado
- [Phase 02]: [02-04] Tapado D-30 narrado con tres valores con nombre (guardada/vigente/enPantalla=min(cantidad, stock)) aplicado a stepper, línea y Total; stock 0 degrada la fila con badge Agotado sin stepper ni total (nada comprable, nada que suma)
- [Phase 02]: [02-04] Primera acción destructiva del sistema como patrón: 'Vaciar carro' confirma en dos pasos inline (booleano de estado, sin modal ni window.confirm) y 'Quitar' no confirma — la asimetría por impacto
- [Phase 02]: [02-04] Gran verificación final de la fase 2: 12 filas con Origen de la etapa 2 y fila final contrato 0.2.0 ↔ /docs con el botón Authorize probado con las cuentas del seed — el pago pedagógico del login form-encoded; la replican las fases 3-5
- [Phase 02]: [02-05] Cierre de fase 2 en los índices: fila 5 queda en Parcial (guias 1-8 listas; continua en fases 3+) en docs/README y README raiz — D-13/D-18 honrados sin marcar el desarrollo completo
- [Phase 02]: [02-05] El Siguiente de guia-04 enlaza guia-05 por nombre de archivo (misma forma que los demas Siguiente): la cadena 04->05->06->07->08->fase 3 quedo grep-verificada sin eslabones sueltos
- [Phase 02]: [02-05] Portadas cuentan 11 ADRs (= numero real del directorio 001-011) y el stack del README raiz agrega cuentas JWT y Zustand en tono telegrafico
- [Phase 02]: [02-05] Gate de cierre de fase documental replicable (fases 3-5): greps de estado + conteo de guias + invariant guide-only (git ls-files vacio para backend/frontend, D-17/ADR-008)
- [Phase 02 cierre]: UAT delegado 4/4 PASS (sesión 02-UAT.md): guías 05-08 construidas literales en maura-uat, Gran verificación final 12/12 incluido Authorize en /docs (admin 200 / clienta 403); WR-02 verificado en su caso borde (sinAuth con token viejo en store) y WR-03 (write-back + badge coherentes); 7 prohibiciones judgment-tier ratificadas con muestreo propio
- [Phase 02 cierre]: Goal de fase 2 reescrito como User Story canónica en ROADMAP (mvp-phase equivalente --force, validada por user-story.validate; SPIDR omitido con causa: fase ya ejecutada como slice vertical)
- [Phase 02 cierre]: 3 bugs de guía corregidos en caliente en ambos lugares (regla maura-uat): version 0.2.0 en main.py (guia-05 paso 8 + ítem de MV), Quitar en fila degradada del checkout (guia-08 + taller, verificado runtime), copy fallback "…e inténtalo de nuevo." unificado (guia-06 + fila nueva en Copywriting Contract) y empty state text-base (guia-07)
- [Phase 02 cierre]: Seguridad 02-SECURITY.md 21/21 cerradas con evidencia runtime (threats_open 0, ASVS 1); ui-review 19/24 sin drift guías↔taller (los 3 hallazgos de contrato = los fixes arriba); verificación re-ejecutada passed 45/45 con digest fresco
- [Phase 03]: Spike de retorno (03-01): el flujo anulado llega por GET (corrección material — docs decían POST en integración) con TBK_TOKEN+TBK_ID_SESION+TBK_ORDEN_COMPRA sin token_ws; endpoint GET+POST con discriminador por presencia de params queda inmune (Pitfall 2)
- [Phase 03]: Mecánica del retorno firmada con evidencia (D-41): RedirectResponse con 302 EXPLICITO a /pago/resultado; página intermedia descartada; el 307 default de starlette re-POSTearía el form contra la SPA (Pitfall 1)
- [Phase 03]: REJECTED reproducible en integración (Q2): elegir Rechazar/TSN en el simulador bancario → retorno normal token_ws → commit response_code=-1/FAILED; CVV errado NO rechaza (aprueba igual); clave 3DS errada → error.cgi+INITIALIZED sin commit; fallback: carrera de stock de D-35
- [Phase 03]: Timeout cronometrado (Q3): 603 s (10:03) desde la carga del form con tab activo; PERO el redirect NO está garantizado si el tab duerme (13 min sin retorno observado) — PENDING huérfanas reales, D-48/D-49 las cubren con honestidad de estado
- [Phase 03]: Idempotencia del commit de Webpay confirmada runtime (A1): segunda llamada con el mismo token devuelve respuesta idéntica — el guard de estado OUR-side sigue obligatorio (Pitfall 4); además el navegador puede repetir retornos (7 repeticiones observadas de un mismo timeout)
- [Phase 03]: Contrato 0.3.0 aprobado ANTES de las guías (D-15 honrado): CheckoutCreate sin campo de precio (CART-03 estructural en el schema), retorno GET+POST público con 302 en ambos métodos (Pitfall 13), pedidos con 404 uniforme de ownership
- [Phase 03]: ADR-012 firma la mecánica del retorno citando la evidencia por flujo del spike (D-40/D-41): discriminador por PRESENCIA de params jamás por método, 302 explícito contra la trampa del 307, security: [] deliberado
- [Phase 03]: ADR-013 registra D-34/D-35 (cierra el blocker de STATE.md): orden PENDING nace al iniciar el pago, crear solo VALIDA stock, descuento atómico al aprobar (UPDATE condicional + rowcount; rowcount 0 → REJECTED); huérfana PENDING sin gestión hasta fase 4; recoge la regla 3 de ADR-010
- [Phase 03]: ADR-014 fija D-36/D-37: snapshot nombre/precio obligatorio en la orden (asimetría con RN-08 como lección), soportado por el soft delete de docs/03 §2.3.5, y numero legible MAURA-{id:06d} como buy_order ≤26 chars distinto del id interno
- [Phase 03]: docs/02 etapa 3: RF-12..18 en orden de flujo de la clienta (recalculo CART-03 primero), RNF-07 sandbox sin registro, RN-10..13 con su porqué (snapshot/asimetría RN-08, estados honestos en curso, stock atómico en el UPDATE, numero legible), HU-09..11; fila P6 real y bloque de aprobación — series 1-2 intactas
- [Phase 03]: docs/03 etapa 3: PEDIDO/LÍNEA con snapshot conectan USUARIO↔PRODUCTO (primeras relaciones), Webpay como primer servicio externo, D3, DFDs 9.0-11.0 con las reglas del retorno por presencia de params (evidencia del spike), pantallas 8-9 con degradado sin sesión y variante del CTA en la 7; decisiones 11-14 citan ADR-012..014
- [Phase 03]: [Phase 03 P04] La carrera de stock de guia-09 se demuestra en dos fases (httpx concurrente crea dos PENDING; dos threads ejecutan el MISMO bloque del commit aprobado sin Webpay): commitear tokens no pagados no aprueba en integracion y el alumno aun no tiene SPA — el UPDATE condicional es lo que se ejercita
- [Phase 03]: [Phase 03 P04] services/pedidos.py recibe la SESION y sus repos hacen flush sin commit: la transaccion de la orden abarca la llamada a Webpay (Pitfall 11) y la pareja descuento+transicion (ADR-013) — el service decide cuando cerrar
- [Phase 03]: [Phase 03 P04] El titulo de ResultadoPago lo decide el estado REAL del pedido fetcheado (no el query param del 302) y el degradado sin sesion lleva el returnTo con la query DENTRO del string — el login de guia-06 no se edita
- [Phase 03]: [Phase 03 P04] apiPost ya existia desde guia-06: guia-10 lo reusa con Bearer y narra la primera excepcion de la regla 5 (el checkout ES fetch, el retorno es navegacion del navegador — Pitfall 10)
- [Phase 03]: guia-11 reutiliza VoucherPedido con import cruzado entre features 'con razon' (regla 6, D-46): moverlo a components/ re-editaria la guia 10 para cero ganancia y duplicarlo serian dos verdades del mismo detalle
- [Phase 03]: La tabla BADGES se copia una vez por pantalla (historial y voucher): con dos consumidoras copiar es mas honesto que adelantar un modulo compartido — el dia que nazca la tercera, baja
- [Phase 03]: Gran verificacion final de fase 3 (guia-11): 12 filas con Origen citando RF-12..18/RN-10..13/HU-09..11/ADR-012..014 y la fila contrato 0.3.0 vs /docs suma dos piezas — el 302 con Location en ambos metodos y el endpoint publico del retorno — con Authorize probado clienta 200 / admin-endpoint 403
- [Phase 03]: Cierre de fase 3 en los indices (D-13/D-18): guias 1-11 listas + 14 ADRs + Webpay construido en el stack, fila 5 honesta en Parcial (fases 4+) y gate documental en verde (11 guia-*.md + repo guide-only)
- [Phase 03 cierre]: UAT delegado 3/3 PASS (03-UAT.md): guias 09-11 construidas literales en maura-uat, Gran verificación final 12/12 runtime real contra Webpay integración (aprobado/anulado/timeout ~603 s/F5/carrera/404/contrato↔docs), huérfanas PENDING visibles "en curso"
- [Phase 03 cierre]: 3 desvíos corregidos en ambos lugares (regla maura-uat): D-1 default _numero_provisorio() para el INSERT NOT NULL de pedidos.numero, D-2 carrera.py importa app.models.usuario (FK metadata), D-3 timeout con pestaña activa CANCELA la orden (guias 10/11 decían "en curso")
- [Phase 03 cierre]: El usuario aceptó la evidencia runtime del flujo anulado (GET, no POST) como canónica (03-UAT test 2) y decidió cerrar IN-01..IN-06 del review vía /gsd-code-review 3 --fix --all (pendiente de ejecutar)
- [Phase 03 cierre]: Code review fixer ejecutado (decisión del test 3 del 03-UAT): IN-01..IN-06 cerrados 6/6 con espejos en maura-uat (IN-06: wrapper Webpay atrapa TransbankError y errores de red → 302 estado=error, jamás 500); disposition 12/12 fixed. Verificación re-ejecutada passed 12/12 con digest fresco v2 sobre el texto post-fixes — fase 03 canónicamente completa (sesión /gsd-verify-work 3 del 2026-09-30)
- [Phase 03 cierre]: Seguridad 03-SECURITY.md 14/14 amenazas cerradas (threats_open 0, ASVS 1, register plan-time, evidencia runtime en 7 de ellas); verificación re-ejecutada passed 12/12 con digest fresco (26 archivos)
- [Phase 04]: Contrato 0.4.0 aprobado ANTES de las guias (D-15 honrado): 7 paths de administracion + asistente publico, allow-list ProductoEditar SIN activo ni id (D-52, mass assignment vetado), 409 para transicion ilegal con copy locked, 503/429 sin cifras, retiro del demo /api/admin/estado narrado (D-54, Pitfall 7)
- [Phase 04]: ADRs 015-017 (indice a 17): RequireAdmin espejo UX del 403 con get_current_admin en CADA endpoint como seguridad real (D-55); maquina de 4 estados con UNA transicion admin PENDING->CANCELLED cobrando las huerfanas D-48/D-49, PAID terminal y refund ADMN-05 diferido (D-50); mini-RAG con structured output citando la evidencia de 04-RESEARCH contra el README @ v2.25.0 y degradacion 503 en contraste con el fail-fast de secret_key (D-56/D-60/D-61)
- [Phase 04]: Defaults del UI-SPEC confirmados como contrato 0.4.0: stock bajo <= 5 (D-53), mensaje <= 500 chars, historial <= 10, maximo 3 cards; 429 declarado SIN cifras de limites (concern abierto de STATE.md)
- [Phase 04]: [04-02] docs/02 etapa 4: RF-19..24, RNF-08/09, RN-14..16, HU-12/13 con filas P7/P8 reales — RN-15 supersede a RN-04 citándola (byte-intacta) y RN-14 fija el umbral ≤ 5 activos como constante DISTINTA del 1-3 de tienda (Pitfall 6 hecho serie)
- [Phase 04]: [04-02] docs/03 etapa 4: pantallas 10-14 con copys locked del UI-SPEC, decisiones 15-18 citando ADR-015..017 (la 15 cita §2.3.5 en vez de duplicar el soft delete), DFDs 12.0-15.0 (13.0 UPDATE condicional espejo del 10.0; 15.0 topes ANTES de Gemini e ids DESPUÉS contra D1 activo) y GEM como segunda entidad externa: request-response JSON sin redirecciones, el contraste con Webpay
- [Phase 04]: [04-02] Los defaults del UI-SPEC quedaron confirmados como RN numeradas (RN-14 ≤ 5, RN-16 500/10/3): las guías 04-03/04-04 enseñan constantes con respaldo de requerimiento; pantalla 13 (No autorizado) traza a RF-08+D-55 — el espejo UX del 403 no inventa RF
- [Phase 04]: [04-03] guia-12: ProductoEditar hereda de ProductoCrear sin cuerpo (allow-list identica por herencia, mass assignment vetado por ausencia), PedidoTransicion con Literal[cancelled] y sku generado panel-{uuid8} en el repo (el upsert es del seed: crear dos veces crea dos productos, el idempotente por diseno es el ESTADO)
- [Phase 04]: [04-03] guia-13: el editor hidrata descripcion/notas desde la ficha publica (ProductoAdmin liviano a proposito en 0.4.0, key ['producto', id] compartida) con hueco honesto para inactivos (la ficha 404a) — el detalle admin seria un 0.5.0, jamas desvio improvisado; queryKeys ['productos','admin'] y ['pedidos','admin'] invalidan por prefijo junto a catalogo e historial (D-48/D-49 cobrados sin editar guia-11)
- [Phase 04]: [04-03] Desviacion Rule 2: guia-12 sube el CORS a [GET,POST,PUT,PATCH] (el plan solo decia version 0.4.0) — la leccion 'el CORS crece con la API' de guia-05 aplicada antes del deploy de fase 5, con mini-verificacion del preflight
- [Phase 4]: Cierre de fase 4 en los índices (D-13/D-18, cuarta corrida): guías 1-15 listas + 17 ADRs + 17 decisiones + panel y asesora Gemini como stack construido en el tono telegráfico de Webpay; fila 5 honesta en Parcial (fases 5+)
- [Phase 4]: Mapa mental de 05_desarrollo suma la capa de IA como segundo servicio externo de tipo nuevo: request-response JSON desde el backend sin redirecciones (contraste explícito con Webpay), API key como env var del servidor
- [Phase 4]: Gate documental de cierre de fase 4 en verde: 15 guia-*.md, 17 ADRs 001-017, cadena Siguiente 11→15 grep-verificada sin eslabones sueltos y repo guide-only (git ls-files backend/frontend vacío, D-17/ADR-008)
- [Phase 04]: [04-06] ADR-018 firma el swap Gemini->Groq (D-63..D-68) con evidencia firmada (doc oficial + probe SDK 1.7.0 + 402/billing de 04-UAT test 2): pin >=1.7,<2, MODELO_ASISTENTE=openai/gpt-oss-120b, json_schema strict + ConfigDict(extra=forbid), GROQ_API_KEY via pydantic-settings con api_key explicita (IN-03), cifras 30 RPM / 1.000 RPD / 8K TPM / 200K TPD con fuente; muralla D-56 y degradacion D-61 preservadas; ADR-017 Superseded con cuerpo byte-intacto
- [Phase 04]: [04-06] Contrato 0.4.0 agnostico del proveedor (D-66): las 8 descripciones reescritas con 'servicio de IA' / 'API key del asistente', el parentesis 'no son publicos sin login' muere (D-68), version NO sube y paths/schemas/copys locked intactos — cero churn para guia-12 y la fila contrato<->/docs
- [Phase 04]: [04-07] guia-14 reescrita como si Groq siempre hubiera sido (D-65): blockquote del swap cita ADR-018 y confina TODA menciona a Gemini/google-genai (gates awk de region); SDK groq >=1.7,<2 piso/techo, key del alumno en console.groq.com (D-63), json_schema strict con ConfigDict(extra=forbid) doble duty (Pitfall 2), MODELO_ASISTENTE=openai/gpt-oss-120b + models.list (D-64), cifras 30 RPM/1.000 RPD con URL y 'a la fecha' (D-68)
- [Phase 04]: [04-07] guia-15 ajustada sin tocar esqueleto: grep del build con GROQ_API_KEY (CERO coincidencias + control positivo + Select-String, Pitfall 8), filas 8-10/13, nota honesta console.groq.com/D-63 y conteo 18 ADRs; router/copys locked de guia-14 byte-intactos salvo 2 descripciones al wording agnostico del contrato (D-66 verificado con diff de precision)

### Pending Todos

None yet.

### Blockers/Concerns

- Phase 4: confirmar límites RPM/RPD del free tier de Gemini logueado en aistudio.google.com/rate-limit antes de fijar material
- Phase 5: elegir plataforma de despliegue free tier (pendiente en PROJECT.md); el deploy congela `return_url`

## Deferred Items

Items acknowledged and deferred at milestone close, most recent first:

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| *(none)* | | | | |

## Session Continuity

Last session: 2026-10-01T15:02:24.908Z
Stopped at: Completed 04-07-PLAN.md
Resume file: None
