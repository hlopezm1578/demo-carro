# Requirements: Demo Carro — Guía educativa e-commerce (body splash)

**Defined:** 2026-09-28
**Core Value:** La guía documenta el ciclo de vida completo y, siguiéndola en orden, la aplicación queda construida y operativa: tienda con catálogo, carro, checkout Webpay sandbox, cuentas JWT, panel admin y asistente IA sobre el catálogo real.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Guía educativa

- [ ] **GUIDE-01**: La guía documenta el ciclo de vida completo (necesidad del cliente → requerimientos → diseño → arquitectura con ADRs → desarrollo guiado paso a paso → pruebas → despliegue → mantenimiento) con trazabilidad entre fases al estilo demo-cine
- [ ] **GUIDE-02**: Cada fase documenta sus ADRs y mantiene el contrato de API de la aplicación actualizado
- [ ] **GUIDE-03**: Las guías de desarrollo son paso a paso — un alumno siguiéndolas en orden construye la aplicación operativa

### Tienda (storefront)

- [ ] **STORE-01**: Visitante ve una landing con identidad de marca de la PYME ficticia
- [ ] **STORE-02**: Visitante navega el catálogo en grilla con filtros por familia aromática y rango de precio
- [ ] **STORE-03**: Visitante ve la página de producto con descripción, precio, familia aromática, notas y disponibilidad de stock
- [ ] **STORE-04**: El catálogo incluye datos demo sembrados (seed idempotente) para desarrollo y UAT

### Carro de compras

- [ ] **CART-01**: Visitante agrega productos al carro, edita cantidades y puede vaciarlo
- [ ] **CART-02**: El carro persiste en el navegador (localStorage) y sobrevive los full-page loads que impone la redirección de Webpay
- [ ] **CART-03**: El backend recalcula y valida precios y stock del carro al crear la orden — nunca confía en los valores del cliente

### Cuentas

- [ ] **AUTH-01**: Cliente puede crear cuenta con email y contraseña
- [ ] **AUTH-02**: Cliente puede iniciar sesión y mantener la sesión (JWT) entre recargas de la SPA
- [ ] **AUTH-03**: Usuarios con rol admin acceden a endpoints y vistas de administración protegidas (claim de rol desde el primer token emitido)
- [ ] **AUTH-04**: El checkout requiere sesión iniciada (v1 sin guest checkout)

### Checkout y pago (Webpay sandbox)

- [ ] **PAY-01**: Cliente inicia checkout y es redirigido a Webpay Plus (Transbank, ambiente de integración) mediante form POST auto-submit con el token
- [ ] **PAY-02**: El retorno de Webpay llega a un endpoint del backend (GET+POST) que discrimina los 4 flujos oficiales (aprobado, anulado, timeout, error de formulario) y redirige a la SPA con el resultado
- [ ] **PAY-03**: La orden se marca pagada solo con `response_code == 0` y `status == AUTHORIZED`, con idempotencia anti doble-commit (el refresh del retorno no paga dos veces)
- [ ] **PAY-04**: Cliente ve un voucher de la tienda (no de Transbank) tras el pago, y el carro se restituye si el pago fue anulado

### Órdenes

- [ ] **ORDR-01**: Cliente ve su historial de pedidos con estados visibles (PENDING / PAID / CANCELLED / REJECTED)
- [ ] **ORDR-02**: El stock se descuenta de forma atómica y transaccional al aprobarse el pago, sin oversell ante compras concurrentes

### Administración

- [ ] **ADMN-01**: Admin hace CRUD de productos con soft delete
- [ ] **ADMN-02**: Admin gestiona stock con alerta de stock bajo
- [ ] **ADMN-03**: Admin gestiona pedidos con transiciones de estado validadas en el backend
- [ ] **ADMN-04**: Admin ve métricas básicas del negocio (tarjetas y tabla, sin librerías de gráficos)

### Asistente IA (Gemini)

- [ ] **AIAS-01**: Cliente usa un chat (burbuja en la tienda) donde el asistente recomienda productos del catálogo real
- [ ] **AIAS-02**: El asistente responde solo con productos existentes (mini-RAG sobre el catálogo + validación de ids contra BD) y muestra product cards clicables desde el chat
- [ ] **AIAS-03**: La API key de Gemini vive solo en el backend (variable de entorno), nunca en el código ni el bundle del frontend

### Despliegue

- [ ] **DEPL-01**: Frontend estático y API quedan desplegados en free tier con URLs públicas y CORS de producción configurado
- [ ] **DEPL-02**: El refresh de rutas de la SPA no da 404 (fallback a index.html) y los 4 flujos de retorno de Webpay se verifican contra el ambiente desplegado

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Checkout y tienda (v1.x)

- **PAY-05**: Guest checkout (comprar sin cuenta)
- **STORE-05**: Búsqueda por texto en el catálogo (cuando supere ~30 SKU)
- **ORDR-03**: Email transaccional de confirmación de pedido
- **ADMN-05**: Refund (anulación/cancelación) de pago desde el panel admin

### Engagement (v2+)

- **STAKE-01**: Reviews y calificaciones de productos
- **STAKE-02**: Wishlist
- **STAKE-03**: Cupones de descuento
- **STAKE-04**: Gráficos en métricas del panel admin

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Pagos reales en producción | La guía opera solo en sandbox/integración con credenciales públicas de Transbank |
| Stripe como pasarela | No permite comercios registrados en Chile (verificado contra stripe.com/global) |
| SDK `google-generativeai` | Deprecado (EOL 2025-11-30); se usa `google-genai` |
| Mercado Pago, Flow o Khipu | Requisitos de sandbox no verificables contra fuente primaria en la exploración |
| i18n / multi-moneda | Fuera del objetivo pedagógico; esencia chilena single-locale |
| Marketplace multi-vendedor | Complejidad de plataforma, no aplica a una PYME single-brand |
| Logística courier / envíos con tracking | Se modela el pedido, no la logística física |
| Motor ML de recomendación propio | El asistente usa Gemini con mini-RAG; no se entrena un modelo |
| Webpay Mall / captura diferida | Modalidades fuera del caso de la PYME |
| SSR / SEO server-side | La decisión pedagógica es SPA + API estrictamente separadas |
| Renderizado de plantillas en el servidor | Ídem — dos tiers separados es decisión de arquitectura de la guía |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| GUIDE-01 | Phase 5 | Pending |
| GUIDE-02 | Phase 1 | Pending |
| GUIDE-03 | Phase 1 | Pending |
| STORE-01 | Phase 1 | Pending |
| STORE-02 | Phase 1 | Pending |
| STORE-03 | Phase 1 | Pending |
| STORE-04 | Phase 1 | Pending |
| CART-01 | Phase 2 | Pending |
| CART-02 | Phase 2 | Pending |
| CART-03 | Phase 3 | Pending |
| AUTH-01 | Phase 2 | Pending |
| AUTH-02 | Phase 2 | Pending |
| AUTH-03 | Phase 2 | Pending |
| AUTH-04 | Phase 2 | Pending |
| PAY-01 | Phase 3 | Pending |
| PAY-02 | Phase 3 | Pending |
| PAY-03 | Phase 3 | Pending |
| PAY-04 | Phase 3 | Pending |
| ORDR-01 | Phase 3 | Pending |
| ORDR-02 | Phase 3 | Pending |
| ADMN-01 | Phase 4 | Pending |
| ADMN-02 | Phase 4 | Pending |
| ADMN-03 | Phase 4 | Pending |
| ADMN-04 | Phase 4 | Pending |
| AIAS-01 | Phase 4 | Pending |
| AIAS-02 | Phase 4 | Pending |
| AIAS-03 | Phase 4 | Pending |
| DEPL-01 | Phase 5 | Pending |
| DEPL-02 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 29 total
- Mapped to phases: 29
- Unmapped: 0

Nota: el conteo previo indicaba 27; el recuento real por categorías es 29 (GUIDE 3, STORE 4, CART 3, AUTH 4, PAY 4, ORDR 2, ADMN 4, AIAS 3, DEPL 2).

---
*Requirements defined: 2026-09-28*
*Last updated: 2026-09-28 after roadmap creation*
