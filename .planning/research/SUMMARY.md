# Project Research Summary

**Project:** Demo Carro — Guía educativa e-commerce (body splash)
**Domain:** E-commerce single-brand educativo de dos tiers (SPA React + API FastAPI en capas) con Webpay Plus sandbox (Transbank) y asistente Gemini
**Researched:** 2026-09-28
**Confidence:** HIGH (stack y arquitectura verificados contra fuentes primarias; priorización de features por consenso multi-fuente)

## Executive Summary

Demo Carro es una tienda de body splash para una PYME chilena ficticia, construida como aplicación de dos tiers estrictamente separados — SPA React 19 + Vite 8 en el cliente, API FastAPI organizada en capas (routers → services → repositories) en el servidor — con dos integraciones externas reales en modo de pruebas: Webpay Plus (Transbank, credenciales públicas de integración) y Gemini (`google-genai`, asistente de venta con mini-RAG sobre el catálogo). El producto real es la guía educativa del ciclo de vida completo: la arquitectura en capas, los ADRs y la trazabilidad entre fases son parte del objetivo pedagógico, no solo un medio. Eso tiene dos consecuencias para el roadmap: la estructura de capas debe quedar definida en las fundaciones (no puede "refactorizarse después" sin invalidar el aprendizaje), y cada fase debe presupuestar tiempo de documentación además de código.

La recomendación de research es un stack con versiones verificadas contra registry APIs y docs oficiales el mismo día: Python 3.12 (techo duro impuesto por el SDK de Transbank), Node >= 22.22 (piso impuesto por React Router 8), sync-by-default en el backend (el SDK de Transbank es `requests` bloqueante; endpoints `def` planos van al threadpool de FastAPI), SQLite + Alembic + seed idempotente como base de datos de la guía. Los tres patrones arquitectónicos que definen al proyecto: (1) el retorno de Webpay apunta a un endpoint del backend que acepta GET y POST, discrimina los 4 flujos de retorno y redirige 302/303 a la SPA — la SPA jamás recibe el POST de Transbank; (2) JWT bearer con API client centralizado y claim de rol desde el día uno; (3) asistente IA backend-proxied con la API key solo en el servidor y el catálogo real inyectado en el prompt.

El mayor riesgo técnico del proyecto es el flujo de retorno de Webpay: los flujos anómalos (anulado en integración) llegan por POST cuyo body ningún JavaScript puede leer, y el token vive ~5 minutos — por eso el spike de retorno es obligatorio ANTES de redactar la fase de checkout. Le siguen el doble commit por refresh (idempotencia a nivel orden), la race condition de stock (UPDATE condicional con verificación de rowcount, nunca SELECT-then-UPDATE en Python), la API key de Gemini en el bundle (solo backend, `.gitignore` desde el primer commit) y el event loop congelado por I/O bloqueante en `async def`. El mayor riesgo de producto es el scope creep: la lista de anti-features es larga y deliberada (sin i18n, sin marketplace, sin reviews, sin cupones, sin email transaccional en v1).

## Key Findings

### Recommended Stack

Stack verificado contra npm/PyPI registry APIs, GitHub y docs oficiales el 2026-09-28. Los dos números que gatillan todo lo demás: **Python 3.12** (única versión declarada soportada simultáneamente por Transbank SDK, SQLAlchemy 2.1 y FastAPI 0.141 — 3.13/3.14 exceden los classifiers del SDK) y **Node 22 LTS >= 22.22** (React Router 8 es la restricción vinculante, más estricta que los engines de Vite 8).

**Core technologies:**
- **React 19.3 + Vite 8.3.1 + TypeScript ~6.0.2** — lo que scaffoldea `npm create vite` (react-ts); no bumpear TS a 7.x a ciegas (el template aún valida 6.x)
- **React Router 8.4.0** (library mode, `createBrowserRouter`) — major actual, ESM-only, baselines Node 22.22+/React 19.2.7+
- **TanStack Query 5.104 + Zustand 5.0.15** — consenso 2026: server state (catálogo, órdenes) y client state (carro, UI) separados
- **Tailwind CSS 4.3.3** via `@tailwindcss/vite` — v4 no tiene config file ni PostCSS; una línea de import
- **FastAPI 0.141.1 + SQLAlchemy 2.1.1 + Alembic 1.20 + Pydantic 2.13.5** — el patrón layered mainstream; schemas Pydantic separados de models SQLAlchemy (la separación ES el objetivo pedagógico)
- **SQLite** (stdlib) — el tutorial oficial de FastAPI lo usa; upgrade a PostgreSQL = cambio de connection string (Neon free tier + psycopg 3 si se necesita persistencia entre redeploys)
- **transbank-sdk 6.1.0** — SDK oficial, sync (`requests`), preconfigurado para integración (commerce code público 597055555532)
- **google-genai >= 2.25, < 3** — SDK oficial; el README advierte 3.x rompe APIs, por eso el pin de techo
- **PyJWT 2.15 + pwdlib[argon2]** — la elección del tutorial oficial de seguridad de FastAPI; NUNCA python-jose (CVEs abiertos) ni passlib (sin mantención desde 2020)
- **pytest 9.1.1 + ruff + uv** — tooling Python 2026; pip+venv como fallback de sala de clases

**Avoid list (verificado):** google-generativeai (EOL 2025-11-30), python-jose, passlib, Stripe (no opera para comercios registrados en Chile), MySQL, Next.js en este scope, el "tbk-qa" commerce code (rumor falso).

### Expected Features

El núcleo table stakes (3 fuentes independientes coinciden): storefront + filtros + carro + checkout + pagos + gestión de pedidos. El detalle crítico verificado contra docs oficiales de Transbank y el código fuente del SDK: el retorno de Webpay tiene **4 escenarios** (normal con `token_ws`; timeout con `TBK_ID_SESION`+`TBK_ORDEN_COMPRA`; anulado con `TBK_TOKEN`+sesión+orden; error de formulario con los 4 juntos), el commit es obligatorio e inmediato, y el voucher lo muestra la tienda, no Transbank.

**Must have (table stakes, v1):**
- Landing con identidad de marca + catálogo grid + PDP con familia aromática y notas
- Filtros por familia aromática y rango de precio (atributo propio del rubro fragancia, costo bajísimo)
- Carro persistente (localStorage) editable con validación server-side de stock/precios al checkout
- Checkout + Webpay Plus sandbox con los 4 escenarios de retorno y voucher propio — el corazón pedagógico
- Órdenes con descuento atómico y transaccional de stock al aprobarse el pago
- Cuentas JWT (cliente + admin con roles) e historial de pedidos con estados visibles
- Admin: login protegido por rol, CRUD productos (soft delete), gestión de stock con alerta baja, gestión de pedidos con máquina de estados, métricas básicas (tarjetas + tabla, sin librerías de gráficos)

**Should have (differentiators):**
- Asistente IA mini-RAG con product cards clicables desde el chat (compromido; complejidad HIGH)
- Webpay Plus real en sandbox (compromido; el valor pedagógico es la integración real)
- Guía educativa con ADRs + contrato API + trazabilidad entre fases (el diferenciador real; es esfuerzo de documentación que consume tiempo de CADA fase — presupuestarlo)
- Seed/reset de datos demo (repetibilidad educativa y UAT)

**Defer (v1.x / v2+):**
- v1.x: guest checkout, búsqueda por texto (cuando el catálogo pase ~30 SKU), email transaccional, refund desde admin
- v2+: reviews, wishlist, cupones, suscripción "beauty box", gráficos en métricas
- Nunca en esta guía: i18n/multi-moneda, marketplace multi-vendedor, logística courier, motor ML propio, Webpay Mall, SSR

### Architecture Approach

API en capas con DI de FastAPI (routers validan y delegan → services contienen casos de uso → repositories son los únicos que tocan SQLAlchemy, sesión inyectada por request), SPA organizada por features con un único API client que centraliza base URL y Bearer. Estructura de referencia `backend/app/{core,database,models,schemas,repositories,services,routers,dependencies.py}` + `frontend/src/{routes,features,lib,context,components}`.

**Major components:**
1. **Webpay return endpoint (backend)** — `GET+POST /api/payments/webpay/return`: discrimina los 4 flujos, commitea solo con `token_ws` (sin `TBK_TOKEN` acompañando), persiste el estado de la orden y redirige 302/303 a `/checkout/result?order=ID` en la SPA. Este patrón resuelve arquitectónicamente el spike pendiente de PROJECT.md
2. **PaymentService** — orquesta create → return → commit/status; crea la orden con `buy_order`/`session_id`/`webpay_token` como bisagra con los flujos de retorno (los flujos b y c no traen `token_ws`)
3. **AuthService** — pwdlib[argon2] + PyJWT, claim `is_admin`, dependencias `get_current_user`/`get_current_admin`
4. **AssistantService** — mini-RAG: system instruction restrictiva + catálogo real en el prompt + `google-genai` con la key solo en env del backend; validación posterior de ids contra BD antes de renderizar links
5. **Carro SPA (localStorage)** — sobrevive los full-page loads que impone la redirección de Webpay; los precios/stock SIEMPRE se recalculan en el backend

**Anti-patterns documentados:** SDK Transbank o key Gemini en el frontend, `return_url` apuntando a la SPA, CORS wildcard con credentials, precios/stock confiados del cliente, carro solo en memoria de React.

### Critical Pitfalls

1. **`return_url` apuntando a la SPA** (el flujo anulado llega por POST que el JS no puede leer; página en blanco en sandbox) — return_url al backend GET+POST que discrimina los 4 flujos y redirige a la SPA; **spike obligatorio antes de escribir la fase checkout**
2. **Redirección inicial a Webpay con `window.location`** (debe ser form POST con `token_ws` oculto auto-subido) — renderizar `<form method="POST">` y auto-subealo; documentar por qué un link no funciona
3. **Doble commit por refresh/reintento** — idempotencia a nivel orden (si ya tiene resultado, saltar el commit); recuperación con `transaction.status(token)` (ventana de 7 días); aprobar solo si `response_code == 0` Y `status == "AUTHORIZED"`
4. **Race condition de stock (oversell)** — `UPDATE ... SET stock = stock - :qty WHERE id = :id AND stock >= :qty` verificando rowcount; con SQLite usar `BEGIN IMMEDIATE` + `busy_timeout`; prueba concurrente incluida en la guía
5. **API key de Gemini en el bundle** (`VITE_*` es público) — key solo en backend; `.gitignore` con `.env` desde el primer commit; `grep` al build como verificación de la guía

Pitfalls moderados que igual cruzan el proyecto: I/O bloqueante en `async def` (regla: librería sin `await` → endpoint `def` plano), CORS que explota solo tras deploy (orígenes desde env con local + producción), fat routers que erosionan las capas (test de arquitectura: routers sin importar SQLAlchemy, repos sin importar transbank/google-genai), carro que muere en el full-page load del retorno, alucinaciones del asistente (mini-RAG + system instruction + validación de ids), 429 de Gemini en clases (streaming + key propia por alumno + manejo amable de errores), JWT que expira a mitad de checkout (ADR de storage + 401 graceful que preserva el carro).

## Implications for Roadmap

Estructura sugerida: **8 fases**, alineada con el build order de ARCHITECTURE.md, las dependencias de FEATURES.md y el pitfall-to-phase mapping de PITFALLS.md. La decisión de ordering más relevante: auth ANTES del checkout (la decisión v1 de FEATURES.md es checkout con login; el guest checkout queda v1.x), pero el ADR de storage del token se decide en fundaciones para no reescribir el cliente HTTP después.

### Phase 1: Fundaciones de dos tiers
**Rationale:** Nada más puede existir sin el esqueleto de ambos tiers + el contrato de API; las convenciones (capas, sync/async, secrets) deben fijarse aquí porque su ausencia se paga con refactor forzoso.
**Delivers:** Repo con `.gitignore`/`.env.example` desde el commit 1, backend `main.py` + CORS desde env + health check, esqueleto de carpetas en capas, SPA Vite + React Router + API client con `VITE_API_URL`, ADRs fundacionales (arquitectura en capas, convención sync/async, storage del JWT), logging (no `print`).
**Addresses:** Guía con ADRs (diferenciador núcleo).
**Avoids:** P4 (key en frontend), P6 (CORS), P7 (event loop), P8 (fat routers).

### Phase 2: Catálogo y storefront
**Rationale:** Checkout y asistente consumen este catálogo; los metadatos ricos (familia aromática, notas) son insumo del mini-RAG.
**Delivers:** Models + Alembic + seed inicial, repositories y endpoints públicos de productos (con `selectinload` desde el inicio), landing, grid de catálogo, PDP, filtros por familia/precio.
**Addresses:** Landing, catálogo, PDP, filtros, seed/reset demo.
**Avoids:** N+1 en listados; modelo de producto pobre que alimentaría alucinaciones del asistente.

### Phase 3: Cuentas JWT
**Rationale:** Las órdenes con historial pertenecen a usuarios y el admin se protege por rol; el claim `is_admin` debe existir desde el primer token para no rehacerlos después.
**Delivers:** users + hash argon2 + `/token` + `get_current_user`/`get_current_admin`, registro/login/logout en la SPA, guards de rutas, manejo 401.
**Addresses:** Cuentas de cliente, login admin protegido.
**Avoids:** P5 (expiry/storage sin ADR — el ADR ya se firmó en Fase 1; aquí se implementa y prueba la expiración).

### Phase 4: Carro y órdenes PENDING
**Rationale:** El pago necesita una orden que cobrar; construir carro + órdenes antes de Webpay deja probar el flujo de compra sin la pasarela.
**Delivers:** Carro persistente en localStorage con hidratación al montar, validación y recálculo server-side de precios/stock, `POST /orders` con `unit_price` congelado en order_items, decremento condicional atómico de stock.
**Addresses:** Carro persistente editable, base de órdenes.
**Avoids:** P12 (carro muere en full-page load), P9 (oversell).

### Phase 5: Checkout Webpay — con spike previo OBLIGATORIO
**Rationale:** Es el patrón de mayor riesgo del proyecto; el spike (pago aprobado, anulado y timeout en sandbox) debe correr antes de redactar la guía de la fase. Depende de Fases 3 y 4.
**Delivers:** Spike documentado; PaymentService, `POST /payments/create` (amount entero recalculado server-side), form POST auto-submit con `token_ws`, return endpoint GET+POST con los 4 flujos, voucher propio, idempotencia anti doble-commit, máquina de estados de orden (PENDING → PAID/CANCELLED/REJECTED), historial de pedidos con estados visibles al cliente.
**Addresses:** Checkout, Webpay sandbox, retorno/voucher, historial, estados de pedido.
**Avoids:** P1, P2, P3 (los tres pitfalls críticos de Webpay).

### Phase 6: Panel admin
**Rationale:** Depende del catálogo (F2) y las órdenes (F4/F5); es independiente del asistente, así que puede ir en cualquier orden relativo a Fase 7 — ponerla antes mantiene el core de la tienda completo antes de añadir IA.
**Delivers:** CRUD productos con soft delete, gestión de stock con alerta baja y reposición al anular, gestión de pedidos con transición de estados validada en backend, métricas básicas (tarjetas + tabla).
**Addresses:** Admin completo (CRUD, stock, pedidos, métricas).
**Avoids:** stock negativo desde la edición manual; estados ambiguos (consume la máquina de estados de F5).

### Phase 7: Asistente IA
**Rationale:** Solo depende del catálogo (F2), pero va al final para no acoplar el core de la tienda a la disponibilidad de Gemini; necesita las capas y el catálogo estables.
**Delivers:** `POST /api/assistant` con mini-RAG (catálogo real en prompt + system instruction restrictiva), streaming SSE con estado "escribiendo...", manejo de 429/timeout con mensaje amable, validación de ids contra BD antes de renderizar product cards clicables, instrucción de key propia por alumno.
**Addresses:** Asistente IA, product cards desde el chat.
**Avoids:** P10 (alucinaciones), P11 (latencia/429), refuerzo de P4 (key solo backend) y P7 (endpoint `def` plano).

### Phase 8: Despliegue y verificación de extremo a extremo
**Rationale:** Va al final porque congela las URLs que Webpay requiere en `return_url`; la elección de host queda pendiente en PROJECT.md.
**Delivers:** Frontend estático + API en hosts free tier, env vars de producción, CORS con origen real, fallback a index.html para rutas SPA (refresh en `/orden/123`), seed sandbox, UAT final de los 4 flujos de Webpay + checklist "looks done but isn't" completa, documentación de cold starts.
**Addresses:** Deploy operativo, cierre del ciclo de la guía.
**Avoids:** P6 en producción, 404 en refresh de rutas SPA, demo con API "caída" por spin-down.

### Phase Ordering Rationale

- **Dependencias duras:** catálogo → (carro → checkout) y catálogo → asistente; órdenes → admin/métricas; el deploy congela `return_url` → va último.
- **Auth antes de checkout** (siguiendo FEATURES/ARCHITECTURE) en vez del orden alternativo sugerido en PITFALLS (auth después para guest checkout), porque la decisión v1 es checkout con login; el ADR de storage se adelanta a Fase 1 de todas formas.
- **Spike de Webpay antes de la Fase 5:** P1/P2 dependen de su resultado y PROJECT.md ya lo exige; no redactar la guía de checkout sin él.
- **Asistente al final:** evita acoplar el core a Gemini y concentra la investigación pendiente (rate limits, streaming) en una sola fase.
- **La guía educativa es deliverable transversal:** cada fase presupuesta tiempo de documentación (ADRs, contrato API, trazabilidad) además de código — es el diferenciador del proyecto.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 5 (Checkout Webpay):** los snippets exactos de Webpay Plus REST no se re-inspeccionaron hoy; restricciones de formato de `buy_order`/`session_id`/`amount` y el comportamiento del segundo commit están sin verificar. El spike + `--research-phase` son imprescindibles.
- **Phase 7 (Asistente IA):** límites RPM/RPD del free tier requieren confirmación logueada en AI Studio; la superficie de streaming del SDK `google-genai` 2.25 está en transición (`interactions.create` vs `models.generate_content_stream`) y debe verificarse contra la referencia del SDK al escribir la fase.
- **Phase 8 (Deploy):** la elección de plataforma sigue pendiente en PROJECT.md; los trade-offs (ephemeral disk de Render free para SQLite vs PostgreSQL gratis) necesitan decisión.

Phases with standard patterns (skip research-phase):
- **Phase 1 (Fundaciones):** docs oficiales de FastAPI (Bigger Applications, CORS, async) y Vite (env vars) cubren todo el patrón.
- **Phase 2 (Catálogo):** CRUD + filtros con SQLAlchemy es el patrón mejor documentado del stack.
- **Phase 3 (Cuentas JWT):** el tutorial oficial de FastAPI (OAuth2 + JWT con pwdlib/PyJWT) es exactamente el patrón a implementar.
- **Phase 6 (Admin):** reusa patrones ya establecidos (CRUD + máquina de estados + guards por rol).

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Versiones verificadas contra npm/PyPI registry APIs + GitHub + docs oficiales el mismo día; doble verificación independiente de los claims de PROJECT.md |
| Features | MEDIUM | Consenso multi-fuente para table stakes; flujo Webpay HIGH (docs Transbank + código fuente del SDK); análisis competitivo LOW (sin audit de competidores chilenos — no bloquea) |
| Architecture | HIGH | Estructura general y flujo Webpay desde fuentes primarias; MEDIUM en auth SPA y deployment; LOW en el detalle fino del schema de BD (borrador) |
| Pitfalls | HIGH | Hallazgos principales leídos directamente de docs oficiales (Transbank, FastAPI, Vite, Gemini); MEDIUM en consensos de comunidad (JWT storage, cold starts) |

**Overall confidence:** HIGH para las decisiones de planificación (stack, orden de fases, patrones núcleo), con gaps acotados y accionables listados abajo — todos asignables a una fase específica.

### Gaps to Address

- **Momento de creación de la orden y del descuento de stock (discrepancia real entre investigaciones):** FEATURES dice que la orden se crea al commit aprobado; ARCHITECTURE crea la orden PENDING en `POST /payments/create` con descuento al crear y restitución al cancelar; PITFALLS recomienda decidir y documentar (commit = lo simple). **Cerrar en requerimientos/diseño con ADR** — afecta el schema, la idempotencia y el panel admin.
- **Schema de BD incompleto para el dominio:** el borrador de ARCHITECTURE (`products` sin familia aromática ni notas) no cubre lo que FEATURES exige para filtros y mini-RAG. Extender el modelo en la fase de diseño de Fase 2.
- **Límites del free tier de Gemini:** confirmar RPM/RPD logueado en `aistudio.google.com/rate-limit` al planificar/escribir la Fase 7; dejar anotado como "límites al día de escritura".
- **Superficie de streaming de `google-genai` 2.25:** docs en migración (interactions vs models); verificar contra la referencia del SDK fijado en requirements antes de redactar la Fase 7.
- **Comportamiento del segundo `commit` con el mismo token:** no documentado por Transbank; verificar empíricamente en el spike de la Fase 5 (alimenta el diseño de idempotencia).
- **Formato de `buy_order`/`session_id`/`amount`:** longitud máxima, unicidad, enteros — confirmar contra la referencia de Transbank al redactar la Fase 5.
- **Host de deploy sin elegir:** decidir plataforma (y si se necesita PostgreSQL por disco efímero) durante roadmap/requerimientos; documentar el trade-off del seed idempotente con SQLite.
- **Guest checkout vs checkout con login:** FEATURES recomienda login en v1 por costo/beneficio pedagógico; los requerimientos deben cerrarlo explícitamente.

## Sources

### Primary (HIGH confidence)
- Transbank Developers — Webpay Plus (flujo create/redirect/return/commit, 4 flujos de retorno, timeouts, status 7 días): https://www.transbankdevelopers.cl/documentacion/webpay-plus — verificado además contra el código fuente de transbank-sdk-python
- FastAPI docs oficiales — Bigger Applications, OAuth2+JWT (pwdlib/PyJWT), CORS, async/def y threadpool: https://fastapi.tiangolo.com
- google-genai SDK README + Gemini API docs (system_instruction, rate limits por proyecto, streaming): https://github.com/googleapis/python-genai · https://ai.google.dev/gemini-api/docs
- Vite — Env Variables and Modes (advertencia `VITE_*` expuesto al cliente): https://vite.dev/guide/env-and-mode
- React Router — data routing (createBrowserRouter, rutas anidadas, error boundaries): https://reactrouter.com
- Registry APIs npm/PyPI (dist-tags, engines, requires_python, fetch 2026-09-28) + templates oficiales de create-vite en main

### Secondary (MEDIUM confidence)
- Salesforce/Loqate/Shift4Shop — checkout y MVP e-commerce best practices
- Algolia/CrossML/BigCommerce/Sendbird — patrones de AI shopping assistants y RAG
- Comunidad — JWT storage (localStorage vs httpOnly), cold starts de free tiers, fixes de SPA fallback en hosts estáticos
- PMI/Teradata — scope creep como causa líder de fracaso PYME/pilotos AI

### Tertiary (LOW confidence)
- Análisis competitivo vs Shopify/WooCommerce (referencia orientativa, sin auditoría de competidores chilenos del rubro)
- Inference Beauty — filtros por familia olfativa (fuente única del rubro; costo tan bajo que la apuesta es segura)
- Borrador de schema e-commerce canónico (validar en fase de diseño)

---
*Research completed: 2026-09-28*
*Ready for roadmap: yes*
