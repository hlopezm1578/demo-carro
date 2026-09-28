# Roadmap: Demo Carro — Guía educativa e-commerce (body splash)

## Overview

La guía se construye por slices verticales MVP: cada fase deja una capability de usuario
operativa de extremo a extremo y su documentación (ADRs, contrato de API, guía de desarrollo
paso a paso). Se parte con los dos tiers (SPA React + API FastAPI en capas) ya navegables con
catálogo y datos demo; siguen las cuentas JWT y el carro persistente; luego el corazón
pedagógico — checkout con Webpay Plus sandbox, sus 4 flujos de retorno y órdenes con stock
transaccional (con el spike de retorno resuelto antes de redactar la guía de la fase); después
el panel de administración para la dueña y el asistente IA (Gemini, mini-RAG sobre el
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

- [ ] **Phase 1: Fundaciones de dos tiers y catálogo** - Esqueleto SPA React + API FastAPI en capas con guía paso a paso, ADRs fundacionales, contrato de API, landing, catálogo filtrable y páginas de producto con seed demo.
- [ ] **Phase 2: Cuentas de cliente y carro persistente** - Registro/login JWT con roles desde el primer token, carro en localStorage que sobrevive full-page loads y checkout protegido por sesión.
- [ ] **Phase 3: Checkout Webpay y órdenes** - Spike de retorno, form POST a Webpay Plus sandbox, 4 flujos de retorno, voucher propio, idempotencia, stock atómico e historial de pedidos.
- [ ] **Phase 4: Panel de administración y asistente IA** - CRUD de productos, stock con alertas, pedidos con máquina de estados y métricas para la dueña; asistente Gemini con mini-RAG y API key solo en backend.
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

**Plans**: 3/5 plans executed *(replanned 2026-09-28 — corrección de alcance D-17 guide-only: los planes 01-03..01-07 originales, que construían código de aplicación, fueron reemplazados por planes docs-only)*
**UI hint**: yes

Plans:
**Wave 1** *(executada antes de la corrección de alcance)*
- [x] 01-01-PLAN.md — Contrato OpenAPI API-first (entregable vigente; el backend verificado fue retirado del árbol y pasa a las guías — commits 364dee6/de0253e como fuente)
- [x] 01-02-PLAN.md — Docs del ciclo 01-03 (necesidad Maura, requerimientos, diseño) + docs/README

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 01-03-PLAN.md — README raíz (D-18) + arquitectura en una página + 8 ADRs fundacionales, incluido ADR-008 guide-only (GUIDE-02)

**Wave 3** *(blocked on Wave 2 completion)*
- [ ] 01-04-PLAN.md — 05_desarrollo README + guías 01-02: proyecto backend (uv) y proyecto frontend con landing de marca (GUIDE-03, STORE-01)

**Wave 4** *(blocked on Wave 3 completion)*
- [ ] 01-05-PLAN.md — Guías 03-04 (modelos y seed 12 SKU, catálogo con fotos/filtros/ficha) + gran verificación final contrato ↔ /docs + estado de los READMEs (STORE-02/03/04, GUIDE-02/03)

### Phase 2: Cuentas de cliente y carro persistente

**Goal**: Un visitante se convierte en cliente identificado: crea cuenta, inicia sesión con JWT que persiste entre recargas, arma un carro que sobrevive los full-page loads (los que impondrá la redirección de Webpay) y el checkout le exige sesión iniciada.
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: AUTH-01, AUTH-02, AUTH-03, AUTH-04, CART-01, CART-02
**Success Criteria** (what must be TRUE):
  1. Cliente crea cuenta con email y contraseña, inicia sesión y mantiene la sesión entre recargas de la SPA (AUTH-01, AUTH-02)
  2. Un usuario con rol admin recibe desde el primer token el claim de rol y accede a un endpoint protegido de administración; un cliente sin rol recibe 403 (AUTH-03)
  3. Visitante agrega productos al carro, edita cantidades y puede vaciarlo; el carro persiste en localStorage y sobrevive un full-page load (CART-01, CART-02)
  4. El checkout exige sesión iniciada: un visitante sin sesión que intenta finalizar compra es llevado al login y vuelve al checkout al autenticarse (AUTH-04)

**Plans**: TBD
**UI hint**: yes

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

**Plans**: TBD
**UI hint**: yes

### Phase 4: Panel de administración y asistente IA

**Goal**: La dueña de la PYME gestiona su negocio en un panel protegido por rol (productos, stock, pedidos, métricas) y los clientes reciben recomendaciones del asistente Gemini sobre el catálogo real, con la API key solo en el backend.
**Mode:** mvp
**Depends on**: Phase 3
**Requirements**: ADMN-01, ADMN-02, ADMN-03, ADMN-04, AIAS-01, AIAS-02, AIAS-03
**Success Criteria** (what must be TRUE):
  1. Admin hace CRUD de productos con soft delete y gestiona el stock con alerta de stock bajo (ADMN-01, ADMN-02)
  2. Admin gestiona pedidos con transiciones de estado validadas en el backend y ve métricas básicas del negocio en tarjetas y tabla, sin librerías de gráficos (ADMN-03, ADMN-04)
  3. Cliente usa la burbuja de chat de la tienda y el asistente recomienda solo productos existentes del catálogo real, con product cards clicables desde el chat (mini-RAG + validación de ids contra BD) (AIAS-01, AIAS-02)
  4. La API key de Gemini vive solo en el backend (variable de entorno): no aparece en el código ni en el bundle del frontend, verificable con grep sobre el build (AIAS-03)

**Plans**: TBD
**UI hint**: yes

### Phase 5: Despliegue y cierre de la guía

**Goal**: La aplicación queda pública y operativa en free tier (frontend estático + API con CORS de producción) y la guía cierra su ciclo de vida completo con trazabilidad de extremo a extremo. Va al final porque el despliegue congela las URLs que Webpay exige en `return_url`.
**Mode:** mvp
**Depends on**: Phase 4
**Requirements**: DEPL-01, DEPL-02, GUIDE-01
**Success Criteria** (what must be TRUE):
  1. El frontend estático y la API quedan desplegados en free tier con URLs públicas y CORS de producción configurado; la tienda funciona completa contra el ambiente desplegado (DEPL-01)
  2. El refresh de rutas de la SPA no da 404 (fallback a index.html) y los 4 flujos de retorno de Webpay se verifican contra el ambiente desplegado (DEPL-02)
  3. La guía documenta el ciclo de vida completo (necesidad → requerimientos → diseño → arquitectura con ADRs → desarrollo guiado → pruebas → despliegue → mantenimiento) con trazabilidad entre fases: un alumno que la sigue en orden termina con la aplicación construida, desplegada y operativa (GUIDE-01)

**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Fundaciones de dos tiers y catálogo | 3/5 | In Progress|  |
| 2. Cuentas de cliente y carro persistente | 0/TBD | Not started | - |
| 3. Checkout Webpay y órdenes | 0/TBD | Not started | - |
| 4. Panel de administración y asistente IA | 0/TBD | Not started | - |
| 5. Despliegue y cierre de la guía | 0/TBD | Not started | - |
