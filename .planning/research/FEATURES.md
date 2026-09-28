# Feature Research

**Domain:** E-commerce single-brand (body splash / cosmética, PYME chilena ficticia) — SPA React + API FastAPI, con guía educativa del ciclo de vida del software
**Researched:** 2026-09-28
**Confidence:** MEDIUM (general, multi-fuente) / verificado contra fuente primaria para el flujo Webpay (docs oficiales Transbank + código fuente del SDK Python)

---

## Feature Landscape

### Table Stakes (Users Expect These)

Lo que cualquier visitante asume que una tienda online tiene. Si falta, la tienda se siente rota. Fuentes: Salesforce (MVP e-commerce), Loqate y Shift4Shop (checkout best practices) — tres fuentes independientes coinciden en el núcleo: **storefront + búsqueda + pagos + gestión de pedidos**.

#### Storefront

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Landing con identidad de marca | Primera impresión; una PYME single-brand vende su historia (la dueña, el taller, los aromas) | LOW | Hero + propuesta de valor + CTA al catálogo. Contenido estático curado, no CMS |
| Catálogo de productos (grid) | Núcleo de la tienda: imagen, nombre, precio CLP, disponibilidad | MEDIUM | Paginación simple o "cargar más". Imágenes servidas como assets estáticos (sin CDN ni upload complejo en v1) |
| Ficha de producto (PDP) | Nadie compra sin ver detalle: descripción, precio, stock, cantidad | MEDIUM | Incluir familia aromática y notas (dominio body splash). Botón "agregar al carro" con feedback |
| Navegación por categorías + filtros | Con 20-40 SKU, filtrar por familia aromática (floral, cítrico, dulce) y rango de precio es lo esperado | MEDIUM | Filtro por atributo en BD (no faceted search tipo Algolia). Es además un patrón propio del rubro fragancia |
| Búsqueda por texto | "Product search" aparece en el MVP mínimo según Salesforce | LOW | Búsqueda simple por nombre/descripción (LIKE / icontains) suficiente a esta escala; no requiere motor de búsqueda |
| Carro persistente y editable | El carro se abandona y se retoma; debe recordar items y permitir editar | MEDIUM | localStorage en la SPA + validación de stock/precio contra la API al pasar a checkout. Cantidades, eliminar, subtotal |
| Checkout (datos de envío + resumen) | Paso obligatorio previo al pago: solo campos mínimos (nombre, email, dirección, teléfono) | HIGH | Mejores prácticas: mínimos campos, mobile-first, indicador de progreso, señales de confianza. Inicia el pago Webpay |
| Retorno post-compra Webpay → voucher | Tras pagar, el usuario vuelve a la tienda y espera un comprobante claro | HIGH | El punto más delicado del proyecto: ver detalle crítico abajo. Cuatro escenarios de retorno, commit obligatorio, voucher propio (Transbank ya no muestra el suyo) |
| Cuentas de cliente (JWT) | Registro, login, logout; base del historial de pedidos | MEDIUM | Comprometido en PROJECT.md. Access token + refresh o access de vida corta; hash de contraseña (bcrypt/argon2) |
| Historial de pedidos con detalle | "¿Dónde está mi pedido?" — el cliente espera ver sus compras y su estado | MEDIUM | Lista de órdenes + detalle (items, totales, estado, datos de autorización Webpay) |
| Estados de pedido visibles al cliente | Post-compra: saber si está pagado, en preparación, enviado | LOW | Reutiliza el mismo estado que gestiona el admin; render en historial |

#### Admin (back-office de la dueña)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Login admin protegido | El panel gestiona dinero y stock; no puede quedar abierto | MEDIUM | Rol `admin` en el JWT, usuario semilla (la dueña), sin auto-registro de admins. Rutas y endpoints protegidos por rol |
| CRUD de productos | La dueña crea, edita, desactiva productos: nombre, descripción, imagen, precio, familia aromática, stock | MEDIUM | Desactivar (soft delete) mejor que borrar físico (rompe órdenes históricas) |
| Gestión de stock | Saber qué hay disponible y no vender de más | MEDIUM | Descuento transaccional de stock al aprobarse el pago (commit con `response_code == 0` y `status == AUTHORIZED`); reposición al anular desde el admin; alerta de stock bajo |
| Gestión de pedidos | Vista central de órdenes con cambio de estado: pagado → preparando → enviado → entregado (y anulado) | MEDIUM | Máquina de estados simple y validada en backend; es la función admin #1 según encuestas de dashboards |
| Métricas básicas | Ventas totales, pedidos por estado, top productos vendidos, productos con stock bajo | LOW | Tarjetas de números + tablas SQL agregadas. Sin librería de gráficos en v1 (alcance y valor marginal bajos) |

### Detalle crítico: flujo de retorno post-compra (Webpay Plus)

Verificado contra docs oficiales de Transbank y el código fuente de `transbank-sdk-python` (dos artefactos oficiales coinciden). Esto alimenta directamente los requerimientos:

- `create(buy_order, session_id, amount, return_url)` devuelve **token (validez ~5 minutos) + URL de redirección**. El navegador se envía por POST del form con `token_ws`.
- Tras pagar, Webpay redirige **por GET** (API v1.1+) al `return_url` con `token_ws`; el comercio **debe llamar `commit(token)` de inmediato**. Aprobado solo si `response_code == 0` y `status == AUTHORIZED`.
- El **voucher lo muestra la tienda** (monto, orden de compra, código de autorización, 4 últimos dígitos, fecha, tipo de pago, cuotas), no Transbank.
- Cuatro escenarios de retorno:

| Escenario | Parámetros que llegan | Qué hacer |
|-----------|----------------------|-----------|
| Normal (aprobado o rechazado) | solo `token_ws` | `commit(token)` → voucher de éxito o página de rechazo |
| Timeout en el formulario (10 min en integración) | `TBK_ID_SESION` + `TBK_ORDEN_COMPRA` | Informar que el pago expiró; ofrecer reintentar (carro recuperado) |
| Usuario anula | `TBK_TOKEN` + `TBK_ID_SESION` + `TBK_ORDEN_COMPRA` | Consultar estado (sin commit), informar cancelación, carro recuperado |
| Error en el formulario | los cuatro parámetros | Informar error; usar `status(token)` para consultar (disponible hasta 7 días) |

- Riesgo específico de la SPA: la redirección del navegador cae **fuera del router de React** → se necesita una ruta frontend que reciba los parámetros GET y los entregue a la API. PROJECT.md ya marca un spike pendiente para esto. Además `refund(token, amount)` y `capture(...)` existen en el SDK (fuera de alcance v1; ver anti-features).

### Differentiators (Competitive Advantage)

Lo que distingue a este proyecto. Ya comprometidos: asistente IA y Webpay. Los demás son diferenciaciones de bajo costo que refuerzan el valor pedagógico o el rubro.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Asistente de venta IA (burbuja de chat) | Recomendación conversacional sobre el catálogo real — el asistente "conoce" la tienda | HIGH | Mini-RAG: catálogo serializado (nombre, familia aromática, notas, precio, stock) como contexto estructurado a Gemini vía `google-genai`, **API key solo en backend**. Respuestas SOLO con productos reales + product cards clicables. Prompts sugeridos de inicio, adaptación a presupuesto/familia declarada en la conversación. Fallback amable ante error/rate limit del free tier. Patrones: Algolia, CrossML, BigCommerce, Sendbird |
| Product cards clicables desde el chat | Cada recomendación es verificable y navegable → confianza y conversión | LOW | Reutiliza la card del catálogo con deep-link al PDP. Refuerzo del asistente (patrón "verifiable product links" del rubro) |
| Webpay Plus real en sandbox | Integración real con redirecciones y contratos reales, no un mock de pago | HIGH | Ya comprometido. Valor pedagógico: credenciales, contratos, redirecciones, manejo de errores (los 4 escenarios) |
| "Compra por aroma" (filtros por familia olfativa) | Diferenciador del rubro fragancia: descubrir por tipo de aroma, no por texto | LOW | Aprovecha el atributo `familia_aromatica` en el modelo de producto (insumo también del asistente IA) |
| Guía educativa con ADRs + contrato API + trazabilidad entre fases | El producto real ES la guía; el formato demo-cine es la marca | MEDIUM | Esfuerzo principalmente de documentación. No es código, pero consume tiempo de cada fase — presupuestarlo |
| Seed/reset de datos demo | Un script que repobla catálogo y pedidos falsos permite a cada alumno partir desde un estado conocido | LOW | Muy valioso para guía educativa (repetibilidad de ejercicios y UAT) |

### Anti-Features (Commonly Requested, Often Problematic)

Lo que deliberadamente NO se construye en la v1 educativa. El scope creep —no el fracaso técnico— es la causa líder de fracaso de proyectos digitales PYME (PMI; 65% de pilotos AI SMB fallan por scope creep según análisis citado por Teradata).

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Multi-moneda / multi-idioma (i18n) | "Por si vendemos afuera" | PYME chilena: solo CLP; multiplica formateo, prompts del asistente y QA | CLP con formateo es-CL; textos en español |
| Marketplace multi-vendedor | "Que otros vendan" | Complejidad explícita de otra liga: roles de vendedor, payouts, moderación (análisis Yo!Kart) | Single-brand: una sola dueña con panel admin |
| A/B testing / feature flags | "Para optimizar" | Sin tráfico real ni significancia estadística; complejidad de infra | Nada (o flags manuales por variable de entorno) |
| Logística de bodega / envío por zona / tracking courier | "Envío real" | Integraciones con couriers, cálculo de tarifas por zona, webhooks | Tarifa plana o "a acordar"; estados de envío manuales en el admin |
| Motor de recomendación ML propio | "Recomendaciones como Amazon" | Infra de entrenamiento y datos que no existen; el caso de uso ya lo cubre el asistente | El asistente Gemini con mini-RAG sobre el catálogo |
| Reviews/valoraciones | Señal de confianza clásica | Moderación, spam, y en tienda ficticia serían falsas | Testimonios estáticos curados en la landing |
| Wishlist / favoritos | Feature común de e-commerce | No aporta al objetivo pedagógico; estado extra en cliente y BD | Defer a v2 si la guía crece |
| Cupones / promociones / loyalty | Marketing PYME | Motor de reglas completo; rompe totales y checkout | Precios fijos; (v2 si se extiende la guía) |
| Suscripciones tipo "beauty box" | Patrón real del rubro fragancia (Scentbird et al.) | Billing recurrente, ciclos, cancelaciones — alcance enorme | Mención en la guía como evolución posible, sin construirla |
| Email transaccional (SMTP) | Confirmación de pedido por correo | Servicio externo extra (SMTP/API), riesgo de spam en sandbox, credenciales | Confirmación en-app (voucher) + historial de pedidos. Si se pide: v1.x con proveedor gratuito |
| Webpay Mall / captura diferida | "El SDK lo trae" | Duplica la superficie de integración sin nuevo aprendizaje nuclear | Webpay Plus simple (create/commit/status) |
| SSR / SEO avanzado | "Para posicionar" | Es una SPA educativa de marca ficticia; SSR contradice la decisión pedagógica | Meta tags básicos; SEO real fuera de alcance |
| Panel BI con gráficos complejos | "Dashboard bonito" | Librerías de gráficos + diseño; valor marginal con volumen de datos demo | Tarjetas de números + tabla top productos |

## Feature Dependencies

```
[Landing] ──enlaces──> [Catálogo]

[CRUD productos admin] ──alimenta──> [Catálogo] ──requiere──> [PDP]
[PDP] ──requiere──> [Carro] ──requiere──> [Checkout]
[Checkout] ──requiere──> [Cuentas JWT] + [Stock] + [precios vigentes]
[Checkout] ──inicia──> [Pago Webpay create]
[Pago Webpay] ──redirige──> [Retorno/voucher] ──requiere──> [commit Webpay]
[Retorno aprobado] ──crea──> [Orden] ──requiere──> [descuento de stock]
[Orden] + [Cuentas JWT] ──requiere──> [Historial cliente]
[Orden] ──requiere──> [Gestión pedidos admin] ──requiere──> [reposición de stock al anular]
[Orden] + [Producto] ──requiere──> [Métricas]
[Login admin] ──requiere──> [JWT con roles]
[Catálogo con metadatos ricos] ──requiere──> [Asistente IA] ──deep-links──> [PDP]
[Seed/reset demo] ──habilita──> pruebas de todo lo anterior
```

### Dependency Notes

- **Checkout requiere Carro + Stock + Cuentas JWT:** valida stock y recalcula precios server-side (nunca confiar en precios del cliente). La decisión v1 es checkout con sesión iniciada — simplifica asociar la orden al cliente y el historial; el guest checkout (mejor práctica de conversión en tiendas reales) queda como v1.x por costo/beneficio pedagógico.
- **Retorno/voucher requiere Pago Webpay y produce la Orden:** el commit aprobado (`response_code == 0`, `status == AUTHORIZED`) es el único punto donde se crea la orden y se descuenta stock — atómico y transaccional. El retorno cancelado debe restaurar el carro (por eso el carro vive en localStorage con los items serializados).
- **Métricas y Gestión de pedidos dependen de Órdenes:** no se pueden construir antes de que exista el flujo de compra completo; por eso el admin de pedidos y las métricas van en fases tardías.
- **Asistente IA requiere catálogo con metadatos ricos:** la calidad del mini-RAG depende de atributos bien modelados (familia aromática, notas, precio, stock). Si el modelo de producto es pobre, el asistente alucina o recomienda mal. Los deep-links requieren que el PDP exista.
- **Login admin requiere JWT con roles:** conviene diseñar el claim `role` desde el inicio del sistema de cuentas para no rehacer tokens después.
- **CRUD admin alimenta el catálogo:** el storefront consume los mismos datos que edita el admin; el modelo de producto compartido es la frontera natural (contrato API).

## MVP Definition

### Launch With (v1)

Equivalente al alcance comprometido en PROJECT.md:

- [ ] Landing con identidad de marca — puerta de entrada y contexto narrativo de la PYME
- [ ] Catálogo + PDP con familia aromática y notas — núcleo de venta; insumo del asistente
- [ ] Navegación por categorías + filtros por familia/precio — descubrimiento esperado en el rubro
- [ ] Carro persistente editable — requisito del checkout; localStorage + validación server-side
- [ ] Checkout + Webpay Plus sandbox con los 4 escenarios de retorno y voucher propio — el corazón pedagógico
- [ ] Órdenes con descuento atómico de stock al aprobarse el pago — integridad de datos
- [ ] Cuentas JWT (cliente + admin con roles) e historial de pedidos — comprometido
- [ ] Admin: CRUD productos (soft delete), stock con alerta baja, gestión de pedidos con estados — comprometido
- [ ] Métricas básicas (tarjetas + tabla) — cierra el ciclo "la dueña ve su negocio"
- [ ] Asistente IA mini-RAG con product cards clicables y fallback — comprometido
- [ ] Seed/reset de datos demo — repetibilidad educativa y UAT
- [ ] Guía por fases con ADRs y contrato API — el producto en sí

### Add After Validation (v1.x)

- [ ] Guest checkout — si se quiere mostrar la mejor práctica de conversión completa
- [ ] Búsqueda por texto — cuando el catálogo demo crezca más allá de ~30 SKU
- [ ] Email de confirmación — con proveedor gratuito; solo si el flujo de voucher queda corto pedagógicamente
- [ ] Refund (`refund(token, amount)`) desde el admin — extensión natural del SDK ya investigado

### Future Consideration (v2+)

- [ ] Reviews y wishlist — señales de confianza; requieren moderación
- [ ] Cupones/promociones — motor de reglas
- [ ] Suscripción "beauty box" — patrón del rubro, gran alcance
- [ ] Gráficos en métricas — cuando el volumen de datos demo lo justifique

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Catálogo + PDP | HIGH | MEDIUM | P1 |
| Carro editable | HIGH | MEDIUM | P1 |
| Checkout + Webpay (4 escenarios + voucher) | HIGH | HIGH | P1 |
| Cuentas JWT + historial | HIGH | MEDIUM | P1 |
| Admin: CRUD + stock + pedidos | HIGH | MEDIUM | P1 |
| Retorno Webpay manejado en SPA | HIGH | HIGH | P1 |
| Asistente IA mini-RAG | MEDIUM | HIGH | P1 (comprometido) |
| Filtros por familia aromática | MEDIUM | LOW | P1 |
| Métricas básicas | MEDIUM | LOW | P2 |
| Seed/reset demo | MEDIUM | LOW | P2 |
| Product cards desde el chat | MEDIUM | LOW | P2 |
| Búsqueda por texto | MEDIUM | LOW | P3 |
| Guest checkout | MEDIUM | MEDIUM | P3 |
| Email transaccional | LOW | MEDIUM | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

Referencia orientativa contra plataformas estándar (Shopify Basic / WooCommerce / dashboards admin típicos), no auditoría de competidores específicos — ver Gaps.

| Feature | Shopify Basic | WooCommerce | Our Approach |
|---------|--------------|-------------|--------------|
| Catálogo + filtros | Nativo + apps de filtros | Nativo + atributos | Catálogo propio + filtro por familia aromática (atributo del dominio) |
| Checkout + pago | Shopify Payments (propio) | WooPayments/plugins | Webpay Plus sandbox (pasarela chilena real, integración educativa) |
| Cuentas + historial | Nativo | Nativo | JWT propio (objetivo pedagógico: auth manual) |
| Admin back-office | Complejo (app store) | Complejo (plugins) | Panel mínimo a medida: CRUD, stock, pedidos, métricas |
| Recomendación | Apps de AI/ML | Plugins | Asistente conversacional Gemini mini-RAG a medida |
| Guía educativa del ciclo de vida | No existe | No existe | El diferenciador real: guía con ADRs, contrato API, trazabilidad |

## Sources

- Transbank Developers — Webpay Plus (docs oficiales: flujo create/redirect/commit, parámetros `token_ws`/`TBK_TOKEN`/`TBK_ID_SESION`/`TBK_ORDEN_COMPRA`, voucher, vigencia del token) — https://www.transbankdevelopers.cl/documentacion/webpay-plus — confianza HIGH (fuente primaria, verificada además contra el código fuente)
- Transbank SDK Python (código fuente: `create/commit/status/refund/capture`, endpoints REST) — https://github.com/TransbankDevelopers/transbank-sdk-python — confianza HIGH (fuente primaria)
- Salesforce — Ecommerce checkout best practices y MVP e-commerce — https://www.salesforce.com — confianza MEDIUM
- Loqate — Checkout best practices (guest checkout, campos mínimos) — https://www.loqate.com — confianza MEDIUM
- Shift4Shop — Checkout best practices — https://blog.shift4shop.com — confianza MEDIUM
- Algolia — AI Shopping Assistants: A Practical Guide — https://www.algolia.com/blog/ecommerce/ai-shopping-assistants — confianza MEDIUM
- CrossML — 7 Best Practices for AI Shopping Assistants — https://www.crossml.com/ai-shopping-assistants-for-e-commerce-stores — confianza MEDIUM
- BigCommerce — Transform Ecommerce with AI Shopping Assistants — https://www.bigcommerce.com/articles/ecommerce/ai-shopping-assistant — confianza MEDIUM
- Sendbird — Best Shopify chatbot using AI and RAG — https://sendbird.com — confianza MEDIUM
- Inference Beauty — Fragrance filters for beauty e-commerce discovery — https://inferencebeauty.com — confianza MEDIUM (única fuente específica del rubro; usar como hipótesis de patrón, no como hecho estadístico)
- Yo!Kart — Multi-vendor marketplace complexity — https://www.yo-kart.com — confianza MEDIUM
- PMI — Toward Successful Management of E-Commerce Projects — https://www.pmi.org — confianza MEDIUM

### Gaps / Confianza

- No se auditó ningún competidor chileno específico de body splash (tiendas reales del rubro); la columna competitiva usa plataformas estándar como referencia — LOW confidence en esa sección, no bloquea requerimientos.
- Filtros por familia aromática: patrón verificado en una sola fuente del rubro + conocimiento general del dominio fragancia — MEDIUM-LOW; de todas formas el costo es tan bajo que la apuesta es segura.
- El tradeoff guest checkout vs checkout con login es una decisión de producto que los requerimientos deben cerrar explícitamente (aquí se recomienda login en v1 por alcance pedagógico).

---
*Feature research for: e-commerce single-brand body splash (educacional)*
*Researched: 2026-09-28*
