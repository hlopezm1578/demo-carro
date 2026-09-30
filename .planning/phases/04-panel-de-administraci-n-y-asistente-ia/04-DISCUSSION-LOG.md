# Phase 4: Panel de administración y asistente IA - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-30
**Phase:** 4-Panel de administración y asistente IA
**Mode:** `--auto` (fully autonomous — no interactive user prompts; every question auto-resolved with the recommended option, logged below)
**Areas discussed:** Máquina de estados de pedidos, Alcance del CRUD de productos, Umbral y superficie de la alerta de stock bajo, Métricas del panel y reemplazo de /api/admin/estado, Routing y guard del panel en la SPA, Estrategia mini-RAG del asistente, Forma de la conversación del chat, API key y degradación de Gemini, Partición de la fase

---

## Máquina de estados de pedidos (ADMN-03)

| Option | Description | Selected |
|--------|-------------|----------|
| 4 estados existentes + única transición manual del admin (PENDING→CANCELLED), PAID terminal | Sin estados nuevos de logística (Out of Scope); el admin gestiona las huérfanas D-48/D-49; refund es ADMN-05 v2 | ✓ |
| Agregar estados de fulfillment (enviado/entregado) | Nuevos estados + transiciones — logística física explícitamente fuera del proyecto | |
| Admin con transiciones libres entre estados | Contradice ADMN-03 ("transiciones validadas en el backend") | |

`[auto]` Selected: "4 estados existentes, única transición manual PENDING→CANCELLED, PAID terminal" (recommended default) → **D-50**
**Notes:** Cancelar PENDING no toca stock (D-35: descuento solo al aprobar). El código HTTP de la transición ilegal queda a discreción del contrato.

## Alcance del CRUD de productos (ADMN-01)

| Option | Description | Selected |
|--------|-------------|----------|
| Imagen como ruta editable (texto) + soft delete con reactivación | Sin multipart/disco; el seed ya provee fotos (D-08); el toggle activo/inactivo enseña el soft delete de docs/03 §2.3.5 | ✓ |
| Upload de imágenes (multipart + guardado en disco) | Infra sin lección nueva; diferido | |
| Soft delete oculto (el admin solo desactiva, sin ver inactivos) | Menos honesto pedagógicamente: el producto inactivo desaparece del catálogo pero los pedidos viejos lo citan (D-36) | |

`[auto]` Selected: "Ruta editable sin upload; toggle activo/inactivo con reactivación" (recommended default) → **D-51, D-52**
**Notes:** Upload real queda como idea diferida (v2 si el curso lo pide).

## Alerta de stock bajo (ADMN-02)

| Option | Description | Selected |
|--------|-------------|----------|
| Umbral fijo por constante backend (≤5), badge en listado admin + contador en métricas | Simple, fijado como RN nueva; superficie mínima que cumple ADMN-02 | ✓ |
| Umbral por producto (columna en el modelo) | Migración + UI de edición — capacidad nueva fuera del requisito | |
| Umbral configurable en UI del panel | Ídem, scope creep | |

`[auto]` Selected: "Umbral fijo por constante (≤5), badge + contador en métricas" (recommended default) → **D-53**

## Métricas del panel y reemplazo de /api/admin/estado (ADMN-04)

| Option | Description | Selected |
|--------|-------------|----------|
| 4 KPIs (ingresos PAID, pedidos por estado, top 5 unidades, count stock bajo) + reemplazo del endpoint demo | Tarjetas + tabla (locked por requisito); el endpoint D-33 evoluciona a métricas reales en 0.4.0 | ✓ |
| Conservar /api/admin/estado y agregar /metricas en paralelo | Dos verdades del mismo concepto; el endpoint demo ya cumplió su lección de fase 2 | |
| KPIs con gráficos | Vetado por REQUIREMENTS (STAKE-04 es v2) | |

`[auto]` Selected: "4 KPIs en tarjetas+tabla; el endpoint demo se reemplaza en 0.4.0" (recommended default) → **D-54**

## Routing y guard del panel en la SPA

| Option | Description | Selected |
|--------|-------------|----------|
| /admin con sub-rutas + layout propio; RequireAdmin reusando patrón D-32; link solo visible para admin | Extiende RequireAuth con el claim de rol (ADR-011); espejo frontend del 403 de D-33 | ✓ |
| Páginas admin dispersas por rutas existentes | Sin borde claro del panel; el layout propio es la lección de sección protegida | |
| Guard solo por ruta sin layout común | Duplicación de verificación de rol por página | |

`[auto]` Selected: "/admin con sub-rutas + layout propio; RequireAdmin (patrón D-32 + rol); link solo para admin" (recommended default) → **D-55**

## Estrategia mini-RAG del asistente (AIAS-02)

| Option | Description | Selected |
|--------|-------------|----------|
| Catálogo completo en el system prompt + respuesta JSON estructurada + validación de ids en backend | Con 12 SKU el retrieval es trivial y honesto; el backend valida contra BD y arma las cards (AIAS-02 literal) | ✓ |
| Function calling / tools (Gemini consulta el catálogo) | Más maquinaria para el mismo resultado con 12 SKU; útil con catálogos grandes | |
| Embeddings + vector store | Out of Scope (motor ML propio); sobre-ingeniería para 12 SKU | |

`[auto]` Selected: "Catálogo completo en el system prompt + JSON estructurado + validación de ids en backend; sin embeddings" (recommended default) → **D-56**
**Notes:** La forma exacta de forzar JSON en google-genai 2.25 la valida el research contra doc oficial (no firmar sobre supuestos — lección D-41).

## Forma de la conversación del chat (AIAS-01)

| Option | Description | Selected |
|--------|-------------|----------|
| Respuesta única (sin streaming), multi-turno stateless, endpoint público sin login, burbuja flotante | La lección es la integración del servicio externo, no SSE; el frontend envía el historial; la asesora atiende a quien navega (P8) | ✓ |
| Streaming de tokens (SSE) | Complejidad de transporte fuera de la lección; diferido | |
| Chat solo para clientas con sesión | La recomendación ocurre mientras se navega, antes del login; salvaguardas de input protegen el free tier | |
| Persistencia de conversaciones en BD | Tablas nuevas sin requisito que las pida | |

`[auto]` Selected: "Respuesta única; multi-turno stateless (frontend envía historial); público sin login con límite de largo; burbuja flotante" (recommended default) → **D-57, D-58, D-59**

## API key y degradación de Gemini (AIAS-03)

| Option | Description | Selected |
|--------|-------------|----------|
| Key propia del alumno (AI Studio, gratis) en .env; sin key → 503 amable + burbuja "no disponible"; guía enseña 429/timeout; verificación por grep del build | Patrón D-08 (paso del alumno); el asistente es opcional (sin fail-fast, a diferencia de secret_key); AIAS-03 verificado en la Gran verificación final | ✓ |
| Key compartida del proyecto | Riesgo de cuota compartida y dependencia externa del material; cada alumno con su key gratis es el patrón establecido | |
| Fail-fast al iniciar sin key | La tienda no puede depender de la IA para arrancar | |

`[auto]` Selected: "Degradación 503 amable; cada alumno crea su key gratis en AI Studio; guía enseña 429/timeout; grep del build" (recommended default) → **D-60, D-61**
**Notes:** Concern abierto NO auto-decidido (blocker de STATE.md): límites RPM/RPD del free tier requieren login del usuario en aistudio.google.com/rate-limit — la guía no promete cifras.

## Partición de la fase

| Option | Description | Selected |
|--------|-------------|----------|
| Contrato 0.4.0 + ADRs primero (D-15); admin (backend→frontend) antes que IA (backend→burbuja); Gran verificación final al cierre | El panel no depende de la IA; la burbuja reusa product cards existentes | ✓ |
| IA antes que admin | La burbuja reusa componentes del catálogo, no del panel; además P7 antecede P8 en el ciclo del cliente | |
| Contrato al final (code-first) | Viola D-15/ADR-007 | |

`[auto]` Selected: "Contrato 0.4.0 primero (D-15); admin antes que IA; ADRs desde 015; guías desde 12" (recommended default) → **D-62**
**Notes:** Partición exacta en sub-guías = discreción del planner.

## Claude's Discretion

- Endpoints/schemas exactos del contrato 0.4.0; ADRs nuevos y títulos; numeración RF-19+/RNF-08+/RN-14+/HU-12+; pantallas 10+.
- Valor final del umbral de stock (propuesto ≤5); schema JSON del asistente; sub-rutas del panel; código HTTP de transición ilegal.
- Copys del panel y la burbuja (tokens 01/02-UI-SPEC); voz de la asesora ligada a la persona de Maura (D-02).
- Partición en guia-12+ bajo el orden D-62; piezas extra de la Gran verificación final.

## Deferred Ideas

- Upload de imágenes desde el panel (v2 candidato).
- Refund de PAID desde el panel — ya es ADMN-05 en REQUIREMENTS v2.
- Gráficos en métricas — ya es STAKE-04 en REQUIREMENTS v2.
- Streaming del chat sobre el mismo endpoint.
