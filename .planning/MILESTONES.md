# Milestones

## v2.25.0 Guía Completa (Shipped: 2026-10-02)

**Phases completed:** 5 phases, 29 plans, 59 tasks

**Delivered:** Guía educativa completa del ciclo de vida del software para la tienda de body
splash de la PYME ficticia MAURA — 18 guías de desarrollo paso a paso, 20 ADRs, contrato API
0.4.0 y docs 01-08 del ciclo con las 8 filas del recorrido en ✅ Listo. Siguiéndola en orden,
el alumno construye y despliega la aplicación completa: SPA React + API FastAPI en capas con
catálogo, carro, cuentas JWT, checkout Webpay sandbox con sus 4 flujos, panel admin y
asistente IA (Groq, mini-RAG sobre el catálogo real).

**Stats:** 284 commits · 210 archivos · ~49.800 líneas insertadas (~21.900 LOC en `docs/`) ·
2026-09-28 → 2026-10-02 (5 días)

**Closeout:** override_closeout (aprobado por el usuario, 2026-10-02)

**Known verification overrides:** fases 1-4 con VERIFICATION.md `stale` por evolución
deliberada del corpus compartido (READMEs de estado D-13/D-18 y series de docs/02-03 editados
por fases posteriores por diseño del modelo guide-only); las 4 pasaron su verificación con
digest fresco en su propio cierre (registrado en STATE.md) y la fase 5 verificó el corpus
final completo (passed, 2026-10-02). audit-open al cierre: limpio, 0 acknowledged. Fix de
cierre: `04-UAT.md` `status: pass` → `complete` (88bb91c), vocabulario terminal del scanner.

**Known Gaps (deuda documentada):** 7 findings del code review de la fase 5 con disposition
deliberado (4 warnings + 3 infos, `05-REVIEW-DISPOSITION.md`); WR-02 y WR-04 tocan bloques
que el alumno copia y quedan como candidatos a fix menor de contenido.

**Key accomplishments:**
- Contrato OpenAPI 3.0.3 API-first de la tienda (docs/04_arquitectura/contrato_api.yaml) — el único artefacto que permanece en el repo tras la corrección de alcance D-17 (guide-only).
- Los tres documentos fundacionales del ciclo con contenido Maura — 9 secciones de necesidad en idioma del cliente, 14 de requerimientos con trazabilidad P→RF sin huecos y 6 de diseño con ER/diccionario/DFDs/wireframes — más el README que gobierna el avance por fases, replicando estructura, tono y mecánica de demo-cine.
- Portada del producto educativo (D-18) + documento de arquitectura dos tiers con stack versionado + los 8 ADRs que fijan las convenciones documentales del ciclo (incluido el invariant guide-only D-17 como ADR-008).
- Serie de desarrollo bajo el modelo guide-only (D-17): README de 05_desarrollo con las reglas del alumno + guia-01 (backend uv → /api/salud con código verificado del historial git) + guia-02 (scaffold react-ts → landing STORE-01 con copies contractuales, tipos espejo del contrato y estados async honestos).
- Guía 3 (modelo + seed upsert de los 12 SKU canónicos, STORE-04) y guía 4 (API de productos + catálogo completo con fotos, filtros en URL, ficha y la Gran verificación final contrato ↔ /docs, STORE-02/03, GUIDE-02), con el estado del ciclo al día en ambos README.
- guia-01 ahora ensena a crear el backend/.gitignore a mano (uv --vcs none no lo genera) y guia-04 declara el 404 del contrato via responses={404} con el schema Error, para que el /docs del alumno documente lo que el contrato promete.
- contrato_api.yaml 0.2.0 con la superficie de autenticación completa (bearerAuth JWT, registro/login/perfil/admin-estado con copies locked D-26), ratificada por ADRs 009-011 con negativas honestas e indexada en el README de arquitectura
- docs/02 y docs/03 extendidos con la etapa 2 completa y trazable: RF-06..11/HU-05..08/RN-05..09 desde P5 con actores Clienta y Admin, y el diseño USUARIO + procesos 5.0-8.0 + pantallas 4-7 ancladas a ADR-009/010/011 — sin renumerar nada de fase 1
- guia-05 (security Argon2+JWT HS256 con claim de rol incondicional, capas espejo del contrato 0.2.0, seed por email con restauración y CORS GET+POST) y guia-06 (store persist maura-auth, interceptor 401 solo-con-Bearer, RequireAuth con returnTo genérico y login/registro con copies locked) — con 10 y 9 bloques 🧠 y 13 y 12 mini-verificaciones accionables
- guia-07 (useCarroStore persist bajo maura-carro con solo pares producto_id/cantidad, CTA con tope en la ficha, /carro con hidratación useQueries tolerante a 404/stock 0, vaciado en dos pasos y badge aria-live) y guia-08 (checkout tras RequireAuth con returnTo genérico, CTA deshabilitado D-31 y la Gran verificación final de la fase 2 con la fila contrato 0.2.0 ↔ /docs probada con Authorize) — con 7 y 4 bloques 🧠 y 11 y 4 mini-verificaciones accionables
- Los tres READMEs de estado avanzan a la verdad de la fase 2 (guías 1-8, 11 ADRs, stack con JWT/Zustand) y la cadena Siguiente queda continua de guia-04 a fase 3, con el invariant guide-only verificado
- Los 4 flujos del retorno de Webpay Plus corroborados contra el ambiente real de integración (3 runtime + 1 documentado), con corrección material del anulado (GET, no POST), la mecánica firmada (302 a /pago/resultado), REJECTED empírico vía TSN y el timeout cronometrado en 603 s
- El contrato 0.3.0 declara la superficie completa de la etapa 3 con sus garantías estructurales (checkout sin campo de precio, retorno público GET+POST con 302, ownership 404) y los ADRs 012-014 registran las decisiones del corazón pedagógico firmadas con la evidencia runtime del spike
- Los requerimientos del pago con Webpay y las órdenes (RF-12..18, RNF-07, RN-10..13, HU-09..11 con la fila P6 real) y el diseño que los aterriza — PEDIDO/LÍNEA con snapshot congelado conectando USUARIO↔PRODUCTO, Webpay como primer servicio externo, DFDs 9.0-11.0 y las pantallas 8-9 de la vuelta del pago — sin renumerar nada de las etapas 1-2
- guia-09 (backend: orden con snapshot que nace al pagar, checkout que recalcula sin confiar en el cliente, retorno que discrimina los 4 flujos con 302 y stock atómico con carrera demostrable) y guia-10 (vuelta: form POST auto-submit del CTA en el handler del clic, ruta pública de resultado con voucher de la tienda y carro que se limpia solo al aprobar)
- El historial /pedidos que hace visible el ciclo de vida de la orden (PENDING "En curso" incluida, detalle que es el MISMO voucher de la guía 10) y la Gran verificación final de la fase 3 — 12 filas con los 4 flujos runtime de Webpay y el contrato 0.3.0 ↔ /docs — más los tres índices de estado contando lo que existe: 11 guías, 14 ADRs, Webpay construido
- Contrato OpenAPI 0.4.0 con los 7 endpoints reales de administración (allow-list sin activo, 409 de transición, métricas que reemplazan al demo narrándolo) y el asistente público con 422/429/503, más los ADRs 015-017 que registran el guard por rol, la máquina de estados y el mini-RAG citando evidencia firmada
- docs/02 suma RF-19..24 + RNF-08/09 + RN-14..16 + HU-12/13 con las filas P7/P8 reales, y docs/03 agrega las pantallas 10-14 con copys locked, las decisiones 15-18 citando ADR-015..017, los DFDs 12.0-15.0 y a Gemini como segunda entidad externa — sin tocar una sola serie existente
- guia-12 enseña el backend del panel por capas (CRUD con soft delete visible, la transición única como UPDATE condicional con 409 copy locked, métricas SQL agregadas, todo bajo get_current_admin con responses declaradas y el demo /api/admin/estado retirado con narración) y guia-13 la SPA (RequireAdmin sin expulsión, LayoutAdmin con subnav, las 3 pantallas con copys locked, apiPut/apiPatch y BADGES a lib/badges.ts) — el eslabón 11→12→13→14 queda grep-verificable
- La mitad de desarrollo del asistente (AIAS-01..03): guia-14 enseña google-genai con structured output firmado contra el README del pin, key opcional con degradación y muralla anti-alucinación del servidor; guia-15 la burbuja SPA con la ProductCard reusada y la Gran verificación final de fase 4 que estrena la fila FIJA del grep del build
- Los tres índices declaran la fase 4 completa y honesta (guías 1-15, 17 ADRs, panel + asesora Gemini como stack construido, fila 5 en Parcial fases 5+) con el gate documental de cierre en verde
- ADR-018 firma el swap Gemini→Groq (SDK groq >=1.7,<2, json_schema strict, cifras 30 RPM/1.000 RPD con fuente) supersediendo ADR-017 con cuerpo intacto, el contrato 0.4.0 queda agnóstico y docs/02+03/ADR-002/README arq dejan de nombrar al proveedor muerto
- guia-14 reescrita "como si Groq siempre hubiera sido" (blockquote D-65 → ADR-018, SDK groq >=1.7,<2 con json_schema strict + extra="forbid", wrapper 429/503 sin retry casero, cifras 30 RPM/1.000 RPD con fuente) y guia-15 ajustada al grep del build GROQ_API_KEY con 18 ADRs — con las menciones históricas confinadas al blockquote por gates awk de región
- Barrido D-67 cerrado con gate mecánico (corpus CERO Gemini vivo; sobreviven solo ADR-017 superseded, ADR-018 registro del swap y el blockquote de guia-14), anclas de planning corregidas con historia intacta y el taller re-integrado con la guia-14 reescrita: happy path 200 REAL con ids existentes, paralelas sin 500 y UAT 5/5
- ADR-019 firma Vercel Hobby + Render Free con evidencia documental (6 URLs oficiales + "a la fecha") y ADR-020 firma SQLite efímero + seed idempotente con la lección en dos capas; doc 07 convierte la decisión en fase del ciclo (narrativa P1/return_url) y el índice de ADRs llega a 20
- docs/06 nombra como método lo que el alumno ya vivió (tres capas defendidas con ejemplos reales de las fases 1-4, divergencia con demo-cine declarada) y docs/08 cierra el ciclo prospectivamente (los 8 diferidos v2 con hilo hacia atrás, PostgreSQL como crecimiento, el swap ADR-017→018 como caso real de mantenimiento) — la cadena 06 → 07 → 08 queda enlazada
- guia-16 publica la API en Render Free (git del taller, Web Service con seed al build, triple congelado PYTHON_VERSION/BACKEND_URL/CORS_ORIGINS, SECRET_KEY nueva) y guia-17 publica la SPA en Vercel Hobby (vercel.json commiteado, VITE_API_URL horneada sin slash final, mini-verificación DEPL-02 del refresh sin 404 y grep del build con control positivo) — el eslabón Siguiente 15 → 16 → 17 queda grep-verificable
- guia-18 cierra la serie: los 4 flujos de Webpay contra el ambiente desplegado con resultado esperado por estado (paid/cancelled/rejected/en curso honesto), el ciclo efímero observado deliberadamente y la Gran verificación final de 9 filas DEFINIDA para el alumno (D-73: "la corres TÚ") con las dos filas fijas heredadas en 0.4.0 — y el Siguiente entrega el testigo a los docs 06/07/08 sin inventar una guia-19
- Las tres portadas (docs/README.md, README.md raíz, docs/05_desarrollo/README.md) ponen las 8 filas del ciclo en ✅ Listo con links relativos y conteos sincronizados (18 guías / 20 ADRs / 20 decisiones), el stack raíz gana su línea de despliegue y el gate documental de fase queda en verde (cadena Siguiente 15→16→17→18→docs + repo guide-only)

---
