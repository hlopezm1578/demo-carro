# Roadmap: Demo Carro — Guía educativa e-commerce (body splash)

## Overview

La guía se construye por slices verticales MVP: cada fase deja una capability de usuario
operativa de extremo a extremo y su documentación (ADRs, contrato de API, guía de desarrollo
paso a paso). Se parte con los dos tiers (SPA React + API FastAPI en capas) ya navegables con
catálogo y datos demo; siguen las cuentas JWT y el carro persistente; luego el corazón
pedagógico — checkout con Webpay Plus sandbox, sus 4 flujos de retorno y órdenes con stock
transaccional (con el spike de retorno resuelto antes de redactar la guía de la fase); después
el panel de administración para la dueña y el asistente IA (Groq, mini-RAG sobre el
catálogo); y al final el despliegue en free tier — último porque congela el `return_url` que
Webpay exige — junto con el cierre del ciclo de vida documentado de la guía.

Ordenamiento con dependencias duras: catálogo antes de carro/checkout/asistente; auth antes
del checkout; spike de retorno Webpay dentro de (y antes de redactar) la fase de checkout;
despliegue al final.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Fundaciones de dos tiers y catálogo** - Esqueleto SPA React + API FastAPI en capas con guía paso a paso, ADRs fundacionales, contrato de API, landing, catálogo filtrable y páginas de producto con seed demo. (completed 2026-09-29)
- [x] **Phase 2: Cuentas de cliente y carro persistente** - Registro/login JWT con roles desde el primer token, carro en localStorage que sobrevive full-page loads y checkout protegido por sesión. (completed 2026-09-30)
- [x] **Phase 3: Checkout Webpay y órdenes** - Spike de retorno, form POST a Webpay Plus sandbox, 4 flujos de retorno, voucher propio, idempotencia, stock atómico e historial de pedidos. (completed 2026-09-30)
- [x] **Phase 4: Panel de administración y asistente IA** - CRUD de productos, stock con alertas, pedidos con máquina de estados y métricas para la dueña; asistente IA (Groq) con mini-RAG y API key solo en backend. (completed 2026-10-01)
- [ ] **Phase 5: Despliegue y cierre de la guía** - Frontend estático + API en free tier con CORS de producción, verificación de los 4 flujos Webpay en el ambiente desplegado y cierre del ciclo de vida documentado.

## Phase Details

### Phase 1: Fundaciones de dos tiers y catálogo

**Goal**: Un visitante navega una tienda de dos tiers operativa (SPA React que consume API FastAPI en capas, sin plantillas en el servidor) con landing de marca, catálogo filtrable y páginas de producto sobre datos demo sembrados; la guía de esta fase es paso a paso y establece las convenciones de ADRs y contrato de API que las fases siguientes mantienen.
**Mode:** mvp
**Depends on**: Nothing (first phase)
**Requirements**: GUIDE-02, GUIDE-03, STORE-01, STORE-02, STORE-03, STORE-04
**Success Criteria** (what must be TRUE):
  1. Visitante ve una landing con identidad de marca de la PYME ficticia y navega la grilla del catálogo filtrando por familia aromática y rango de precio (STORE-01, STORE-02)
  2. Visitante abre la página de un producto y ve descripción, precio, familia aromática, notas y disponibilidad de stock (STORE-03)
  3. El seed idempotente deja datos demo reproducibles (re-ejecutable sin duplicar) para desarrollo y UAT (STORE-04)
  4. Un alumno que sigue la guía de esta fase paso a paso levanta desde cero los dos tiers con el catálogo funcionando; la fase documenta sus ADRs y el contrato de API inicial, y cada fase posterior actualiza ambos (GUIDE-02, GUIDE-03)

**Plans**: 6/6 plans complete (5 executed + 1 gap closure from UAT) *(replanned 2026-09-28 — corrección de alcance D-17 guide-only: los planes 01-03..01-07 originales, que construían código de aplicación, fueron reemplazados por planes docs-only)*
**UI hint**: yes

Plans:
**Wave 1** *(executada antes de la corrección de alcance)*
- [x] 01-01-PLAN.md — Contrato OpenAPI API-first (entregable vigente; el backend verificado fue retirado del árbol y pasa a las guías — commits 364dee6/de0253e como fuente)
- [x] 01-02-PLAN.md — Docs del ciclo 01-03 (necesidad Maura, requerimientos, diseño) + docs/README

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 01-03-PLAN.md — README raíz (D-18) + arquitectura en una página + 8 ADRs fundacionales, incluido ADR-008 guide-only (GUIDE-02)

**Wave 3** *(blocked on Wave 2 completion)*
- [x] 01-04-PLAN.md — 05_desarrollo README + guías 01-02: proyecto backend (uv) y proyecto frontend con landing de marca (GUIDE-03, STORE-01)

**Wave 4** *(blocked on Wave 3 completion)*
- [x] 01-05-PLAN.md — Guías 03-04 (modelos y seed 12 SKU, catálogo con fotos/filtros/ficha) + gran verificación final contrato ↔ /docs + estado de los READMEs (STORE-02/03/04, GUIDE-02/03)

**Wave 5** *(gap closure — blocked on Wave 4; origen: gaps G-01-1/G-01-4 del 01-UAT.md)*
- [x] 01-06-PLAN.md — Cierre de gaps del UAT: guia-01 (con `--vcs none` uv no genera el .gitignore; la guía enseña a crearlo en el Paso 5) y guia-04 (declarar el 404 del contrato en el router para que /docs lo documente — fila 11 sin el tercer desvío)

### Phase 2: Cuentas de cliente y carro persistente

**Goal**: As a visitante de la tienda, I want to crear una cuenta, iniciar sesión con un token que persiste entre recargas y armar un carro que sobreviva los full-page loads hasta un checkout que me exige sesión, so that la tienda me reconoce en cada visita y mi compra queda lista para el pago real que llega con Webpay en la fase 3.
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: AUTH-01, AUTH-02, AUTH-03, AUTH-04, CART-01, CART-02
**Success Criteria** (what must be TRUE):
  1. Cliente crea cuenta con email y contraseña, inicia sesión y mantiene la sesión entre recargas de la SPA (AUTH-01, AUTH-02)
  2. Un usuario con rol admin recibe desde el primer token el claim de rol y accede a un endpoint protegido de administración; un cliente sin rol recibe 403 (AUTH-03)
  3. Visitante agrega productos al carro, edita cantidades y puede vaciarlo; el carro persiste en localStorage y sobrevive un full-page load (CART-01, CART-02)
  4. El checkout exige sesión iniciada: un visitante sin sesión que intenta finalizar compra es llevado al login y vuelve al checkout al autenticarse (AUTH-04)

**Plans**: 5/5 plans complete *(planeados 2026-09-29 — orden API-first D-15: contrato y ADRs aprobados antes de las guías; docs 02/03 en paralelo con el contrato por ser independientes en archivos)*
**UI hint**: yes

Plans:
**Wave 1** *(paralelos — sin solape de archivos)*
- [x] 02-01-PLAN.md — TRACER API-first: contrato 0.2.0 (bearerAuth, /api/auth/*, /api/admin/estado) + ADRs 009-011 + README de arquitectura (AUTH-01/02/03)
- [x] 02-02-PLAN.md — Especificación de la etapa 2: docs 02 (RF-06..11, RN-05..09, HU-05..08, actores, P5) + docs 03 (USUARIO, procesos 5.0-8.0, pantallas 4-7)

**Wave 2** *(blocked on Wave 1)*
- [x] 02-03-PLAN.md — Guías 05-06: backend de cuentas (security Argon2+JWT, capas, seed de usuarios) y sesión frontend (store persist, interceptor 401, RequireAuth, login/registro, navbar) (AUTH-01/02/03)

**Wave 3** *(blocked on Wave 2)*
- [x] 02-04-PLAN.md — Guías 07-08: carro persistente (store sin precios, /carro, badge) y checkout protegido + Gran verificación final fase 2 con fila contrato ↔ /docs (CART-01/02, AUTH-04)

**Wave 4** *(blocked on Wave 3)*
- [x] 02-05-PLAN.md — Cierre de fase: READMEs de estado (guías 1-8, 11 ADRs), eslabón guia-04→05 y verificación guide-only (D-13/D-18)

### Phase 3: Checkout Webpay y órdenes

**Goal**: Un cliente con sesión completa una compra de extremo a extremo contra Webpay Plus en ambiente de integración — ida por form POST auto-submit, vuelta por el endpoint del backend que discrimina los 4 flujos oficiales, voucher de la tienda, orden con estados y stock descontado de forma atómica. El spike del retorno de Webpay (aprobado, anulado y timeout en sandbox) se resuelve dentro de esta fase, ANTES de redactar su guía de desarrollo.
**Mode:** mvp
**Depends on**: Phase 2
**Requirements**: CART-03, PAY-01, PAY-02, PAY-03, PAY-04, ORDR-01, ORDR-02
**Success Criteria** (what must be TRUE):
  1. Cliente inicia checkout y es redirigido a Webpay Plus (Transbank, integración) mediante form POST auto-submit con el token (PAY-01)
  2. Los 4 flujos de retorno oficiales (aprobado, anulado, timeout, error de formulario) llegan al endpoint del backend (GET+POST), quedan discriminados con el resultado correcto en la SPA, el cliente ve un voucher de la tienda (no de Transbank) y el carro se restituye si el pago fue anulado (PAY-02, PAY-04)
  3. La orden se marca pagada solo con `response_code == 0` y `status == AUTHORIZED`, y el refresh de la página de retorno no paga dos veces (idempotencia anti doble-commit) (PAY-03)
  4. El backend recalcula y valida precios y stock al crear la orden — nunca confía en los valores del cliente (CART-03)
  5. El stock se descuenta de forma atómica y transaccional al aprobarse el pago (sin oversell ante compras concurrentes) y el cliente ve su historial de pedidos con estados PENDING / PAID / CANCELLED / REJECTED (ORDR-02, ORDR-01)

**Plans**: 5/5 plans complete *(planeados 2026-09-30 — spike primero D-38: el retorno se corrobora runtime ANTES de firmar contrato/ADRs/guías; luego API-first D-15 con docs 02/03 en paralelo)*
**UI hint**: yes

Plans:
**Wave 1** *(spike primero — D-38/D-41: la mecánica del retorno se firma con evidencia)*
- [x] 03-01-PLAN.md — TRACER: spike de retorno Webpay runtime en maura-uat (3 flujos + 4° documentado) + hallazgos en 03-SPIKE-RETORNO.md (PAY-01/02)

**Wave 2** *(paralelos — sin solape de archivos; blocked on Wave 1)*
- [x] 03-02-PLAN.md — Contrato 0.3.0 (checkout/retorno GET+POST 302/pedidos) + ADRs 012-014 + README de arquitectura (CART-03, PAY-01..03, ORDR-01)
- [x] 03-03-PLAN.md — Especificación de la etapa 3: docs 02 (RF-12+/RN-10+/HU-09+, fila P6 real) + docs 03 (entidades PEDIDO/LÍNEA, DFDs 9.0+, pantallas 8-9)

**Wave 3** *(blocked on Wave 2)*
- [x] 03-04-PLAN.md — Guías 09-10: backend de órdenes+Webpay (recalculo CART-03, discriminador, stock atómico) y vuelta SPA (form auto-submit, voucher, carro solo al aprobar)

**Wave 4** *(blocked on Wave 3)*
- [x] 03-05-PLAN.md — Guía 11 (historial /pedidos + Gran verificación final con 4 flujos runtime y contrato 0.3.0 ↔ /docs) + READMEs de estado (guías 1-11, 14 ADRs)

### Phase 4: Panel de administración y asistente IA

**Goal**: La dueña de la PYME gestiona su negocio en un panel protegido por rol (productos, stock, pedidos, métricas) y los clientes reciben recomendaciones del asistente IA (Groq) sobre el catálogo real, con la API key solo en el backend.
**Mode:** mvp
**Depends on**: Phase 3
**Requirements**: ADMN-01, ADMN-02, ADMN-03, ADMN-04, AIAS-01, AIAS-02, AIAS-03
**Success Criteria** (what must be TRUE):
  1. Admin hace CRUD de productos con soft delete y gestiona el stock con alerta de stock bajo (ADMN-01, ADMN-02)
  2. Admin gestiona pedidos con transiciones de estado validadas en el backend y ve métricas básicas del negocio en tarjetas y tabla, sin librerías de gráficos (ADMN-03, ADMN-04)
  3. Cliente usa la burbuja de chat de la tienda y el asistente recomienda solo productos existentes del catálogo real, con product cards clicables desde el chat (mini-RAG + validación de ids contra BD) (AIAS-01, AIAS-02)
  4. La API key del asistente vive solo en el backend (variable de entorno): no aparece en el código ni en el bundle del frontend, verificable con grep sobre el build (AIAS-03)

**Plans**: 8/8 plans complete (5 executed + 3 rework) *(planeados 2026-09-30 — orden D-62: contrato 0.4.0 + ADRs 015-017 y docs 02/03 primero (D-15, en paralelo sin solape de archivos como la fase 3), luego panel admin completo (backend → SPA), después asistente IA (backend → burbuja), cierre con READMEs; sin spike — la pieza de riesgo (structured output) ya quedó firmada con evidencia en 04-RESEARCH.md contra el README del SDK @ v2.25.0. Rework 2026-10-01: D-63..D-68 reemplazan Gemini por Groq — planes 04-06..08 con ondas frescas R1-R3; los 04-01..05 son historia ejecutada y no se modifican)*
**UI hint**: yes

Plans:
**Wave 1** *(paralelos — sin solape de archivos)*
- [x] 04-01-PLAN.md — TRACER API-first: contrato 0.4.0 (paths admin reales que reemplazan /api/admin/estado + /api/asistente público con 422/429/503) + ADRs 015-017 + README de arquitectura (ADMN-01..04, AIAS-01..03)
- [x] 04-02-PLAN.md — Especificación de la etapa 4: docs 02 (RF-19+/RNF-08+/RN-14+/HU-12+, filas P7/P8 reales) + docs 03 (pantallas 10-14, DFDs 12.0+, decisiones 15-18, Gemini como 2° servicio externo)

**Wave 2** *(blocked on Wave 1)*
- [x] 04-03-PLAN.md — Guías 12-13: backend del panel (CRUD soft delete, transición 409, métricas agregadas) y SPA /admin (RequireAdmin, LayoutAdmin, BADGES a lib/badges.ts) (ADMN-01..04)

**Wave 3** *(blocked on Wave 2)*
- [x] 04-04-PLAN.md — Guías 14-15: asistente backend (google-genai structured output, key opcional con degradación, muralla anti-alucinación) y burbuja SPA + Gran verificación final de fase 4 con el grep del build (AIAS-01..03)

**Wave 4** *(blocked on Wave 3)*
- [x] 04-05-PLAN.md — Cierre de fase: READMEs de estado (guías 1-15, 17 ADRs, panel+asesora construidos, fila 5 honesta en Parcial fases 5+) y gate documental guide-only

**Rework Gemini→Groq (2026-10-01, D-63..D-68)** *(ondas frescas R1-R3 — el camino Gemini se cerró: Google exige billing para keys nuevas + 402 real; ver 04-CONTEXT.md/04-UAT test 2)*
- [x] 04-06-PLAN.md — **Wave R1** — TRACER spec: ADR-018 (supersede ADR-017, cifras D-68 firmadas) + contrato 0.4.0 agnóstico (8 descripciones, versión NO sube, D-66) + docs 02/03/ADR-002/README arq sin Gemini (AIAS-02/03)
- [x] 04-07-PLAN.md — **Wave R2** *(blocked on R1)* — guia-14 reescrita (SDK groq pin >=1.7,<2, json_schema strict, MODELO_ASISTENTE, blockquote D-65, cifras 30 RPM/1.000 RPD con fuente) + guia-15 ajustada (grep del build GROQ_API_KEY, 18 ADRs) (AIAS-01..03)
- [x] 04-08-PLAN.md — **Wave R3** *(blocked on R1+R2)* — Cierre del rework: barrido D-67 con gate cero-Gemini (one-liners guia-12/13 + READMEs, 18 ADRs/18 decisiones), anclas de planning (ROADMAP Goal/SC4, REQUIREMENTS AIAS-03, PROJECT/STACK) y taller maura-uat re-integrado + UAT test 2 re-verificado (ADMN-01..04, AIAS-01..03)

### Phase 5: Despliegue y cierre de la guía

**Goal**: La aplicación queda pública y operativa en free tier (frontend estático + API con CORS de producción) y la guía cierra su ciclo de vida completo con trazabilidad de extremo a extremo. Va al final porque el despliegue congela las URLs que Webpay exige en `return_url`.
**Mode:** mvp
**Depends on**: Phase 4
**Requirements**: DEPL-01, DEPL-02, GUIDE-01
**Success Criteria** (what must be TRUE):
  1. El frontend estático y la API quedan desplegados en free tier con URLs públicas y CORS de producción configurado; la tienda funciona completa contra el ambiente desplegado (DEPL-01)
  2. El refresh de rutas de la SPA no da 404 (fallback a index.html) y los 4 flujos de retorno de Webpay se verifican contra el ambiente desplegado (DEPL-02)
  3. La guía documenta el ciclo de vida completo (necesidad → requerimientos → diseño → arquitectura con ADRs → desarrollo guiado → pruebas → despliegue → mantenimiento) con trazabilidad entre fases: un alumno que la sigue en orden termina con la aplicación construida, desplegada y operativa (GUIDE-01)

**Plans**: 2/5 plans executed *(planeados 2026-10-01 — D-73 gobierna toda la fase: SOLO escritura, sin spike runtime (D-72 superseded), sin deploy del taller y sin UAT de despliegue; la evidencia de ADR-019 es documental (docs oficiales citadas en 05-RESEARCH.md). Orden D-15: ADRs + doc 07 primero, docs del ciclo y guías en paralelo por archivos disjuntos, guía de cierre y índices al final)*

Plans:
**Wave 1** *(spec primero — D-15)*
- [x] 05-01-PLAN.md — TRACER: ADR-019 (despliegue free tier Vercel+Render con evidencia documental, D-69/D-73) + ADR-020 (persistencia efímera + seed, D-70) + docs/07_despliegue.md + índice de ADRs a 20 (DEPL-01)

**Wave 2** *(paralelos — sin solape de archivos; blocked on Wave 1)*
- [x] 05-02-PLAN.md — Docs del cierre del ciclo: 06_pruebas.md (síntesis del método, no suite) + 08_mantenimiento.md (diferidos v2 + PostgreSQL mencionado) (GUIDE-01)
- [ ] 05-03-PLAN.md — Guías 16-17: deploy API en Render (env vars congeladas, seed al build) y deploy SPA en Vercel (vercel.json rewrite, VITE_API_URL) + eslabón guia-15 → 16 (DEPL-01, DEPL-02)

**Wave 3** *(blocked on Wave 2)*
- [ ] 05-04-PLAN.md — Guía 18: los 4 flujos contra el ambiente desplegado + Gran verificación final de la SERIE definida para el alumno (D-73) + Siguiente al ciclo documental (DEPL-02, GUIDE-01)

**Wave 4** *(blocked on Waves 2-4)*
- [ ] 05-05-PLAN.md — Cierre de índices: READMEs ×3 con las 8 filas del ciclo en ✅ Listo (quinta corrida D-13/D-18, conteos 18 guías/20 ADRs) + gate documental de fase (GUIDE-01)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Fundaciones de dos tiers y catálogo | 6/6 | Complete    | 2026-09-29 |
| 2. Cuentas de cliente y carro persistente | 5/5 | Complete    | 2026-09-30 |
| 3. Checkout Webpay y órdenes | 5/5 | Complete    | 2026-09-30 |
| 4. Panel de administración y asistente IA | 8/8 | Complete    | 2026-10-01 |
| 5. Despliegue y cierre de la guía | 2/5 | In Progress|  |
