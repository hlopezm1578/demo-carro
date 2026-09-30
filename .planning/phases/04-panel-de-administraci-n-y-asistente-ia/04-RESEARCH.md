# Phase 4: Panel de administración y asistente IA - Research

**Researched:** 2026-09-30
**Domain:** Documentación de guía educativa (guide-only) — panel admin FastAPI+React protegido por rol y asistente Gemini (google-genai 2.25, mini-RAG, structured output)
**Confidence:** HIGH

> **Regla de suelo del repo (D-17, ADR-008):** este repositorio es **guide-only** — la fase 4 entrega **DOCUMENTOS** (contrato 0.4.0, ADRs, docs 02/03, guías 12+, READMEs), no código de aplicación. Todo "code example" de este research es material para los **bloques de código que el alumno copia** dentro de las guías nuevas. La verificación de planes es documental (greps/estructura); el UAT runtime es delegado al agente en `D:/Repos/maura-uat` sobre la app construida hasta guia-11.

## Summary

La fase 4 extiende seis piezas documentales existentes (contrato 0.4.0 ANTES que todo, D-15; docs/02 series RF-19+/RNF-08+/RN-14+/HU-12+; docs/03 pantallas 10+ y DFDs 12.0+; ADRs desde ADR-015; guías 12+; READMEs de estado) para cubrir dos peticiones a la vez: **P7 panel de administración** (ADMN-01..04) y **P8 asesora de venta** (AIAS-01..03). El panel es una extensión natural de decisiones ya firmadas: `get_current_admin` existe desde guia-05, `RequireAuth`+returnTo desde guia-06, la entidad PRODUCTO ya tiene `activo` (soft delete diseñado en docs/03 §2.3.5) y los 4 estados del pedido (`pending/paid/cancelled/rejected`) ya viajan en el contrato 0.3.0. El asistente es la segunda integración de servicio externo real (después de Webpay) y su pieza de mayor riesgo es **structured output en google-genai 2.25**, que este research firmó con evidencia contra el README del SDK en el tag exacto `v2.25.0` (D-56): `client.models.generate_content(...)` + `types.GenerateContentConfig(response_mime_type='application/json', response_json_schema=<Pydantic>.model_json_schema())`.

**Hallazgo material del research:** la documentación actual de ai.google.dev (structured-output) YA migró a la nueva **Interactions API** (`client.interactions.create` + `response_format`), un patrón que NO es el documentado en el README del pin `>=2.25,<3`. La guía debe enseñar el patrón del SDK pinneado y narrar el drift como lección (las docs web corren más rápido que el SDK pinneado) — exactamente el tipo de supuesto que D-56 vetaba firmar sin evidencia. Segundo hallazgo: los **RPM/RPD del free tier siguen sin ser públicos sin login** (verificado contra ai.google.dev/gemini-api/docs/rate-limits: la página deriva a "View your active rate limits in AI Studio"), lo que confirma el concern abierto de STATE.md — la guía enseña el manejo del 429 sin prometer cifras.

**Primary recommendation:** Contrato 0.4.0 primero (reemplaza `/api/admin/estado` por los endpoints reales de admin + el endpoint público `/api/asistente`, con 503/429 nuevos en la convención de errores), luego panel admin completo (backend → SPA con layout `/admin` + `RequireAdmin`), después asistente (backend mini-RAG con `response_json_schema` → burbuja SPA), cerrando con la Gran verificación final que suma el grep del build (`GEMINI_API_KEY` sin resultados en `dist/`) — orden D-62.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

*(Copiadas verbatim de `04-CONTEXT.md` — numeración D-50..D-62, continúa de fases 1-3)*

#### Máquina de estados de pedidos (ADMN-03)
- **D-50:** **Los 4 estados existentes (PENDING / PAID / CANCELLED / REJECTED) — sin estados nuevos.** Nada de "enviado/entregado": la logística física es Out of Scope del proyecto. La máquina de estados completa se documenta con sus transiciones legales y quién puede ejecutar cada una (el flujo de pago posee las suyas; el admin tiene exactamente UNA transición manual): **PENDING→CANCELLED** — la gestión de órdenes huérfanas que D-48/D-49 dejaron explícitamente para esta fase. Cancelar una PENDING no toca stock (D-35: el stock solo se descuenta al aprobar el pago), así que la transición es limpia. **PAID es terminal en v1** — el refund es ADMN-05, diferido a v2. El backend valida la transición pedida contra la máquina (rechaza las ilegales; código exacto a discreción del contrato).

#### CRUD de productos (ADMN-01)
- **D-51:** **Imágenes como campo de ruta editable (texto), sin upload de archivos.** El admin edita la ruta (`/products/{sku}.jpg`); no hay multipart ni guardado de archivos. `python-multipart` ya llega en `fastapi[standard]`, pero el upload (multipart, disco, validación de tipo/tamaño) es infraestructura sin lección nueva: el seed ya provee las fotos (D-08) y el alumno las descargó en fase 1. Upload real queda como idea diferida.
- **D-52:** **Soft delete visible y reversible en el panel.** El listado de productos marca activo/inactivo; el admin puede reactivar un producto inactivo con un toggle. Los inactivos desaparecen del catálogo público y de las fichas, pero los pedidos viejos siguen mostrando su snapshot de nombre/precio (D-36).

#### Alerta de stock bajo (ADMN-02)
- **D-53:** **Umbral fijo por constante del backend** (propuesto: stock ≤ 5; valor final a discreción), fijado como RN nueva. Superficie de la alerta: badge por producto en el listado admin + contador de productos con stock bajo en métricas (D-54). Sin UI para configurar el umbral — sería una capacidad nueva fuera de ADMN-02.

#### Métricas del panel (ADMN-04)
- **D-54:** **Cuatro KPIs en tarjetas + tabla (sin gráficos, locked por requisito):** (1) ingresos totales = suma de órdenes PAID, (2) pedidos por estado (los 4), (3) top 5 productos por unidades vendidas, (4) cantidad de productos con stock bajo (umbral D-53). Todo computable desde las tablas existentes (pedidos + líneas snapshot). **El endpoint demo `/api/admin/estado` (D-33) se reemplaza por el endpoint real de métricas en el contrato 0.4.0**: cumplió su lección de fase 2 (dependencia de seguridad con claim de rol) y la guía narra la evolución.

#### Panel en la SPA
- **D-55:** **Ruta `/admin` con sub-rutas bajo un layout propio del panel** (propuesta: productos, pedidos, métricas; estructura exacta a discreción), protegida por un guard por rol — RequireAdmin que reusa el patrón RequireAuth + returnTo (D-32) sumando el claim de rol desde el primer token (ADR-011). El link "Panel" en el navbar solo es visible con rol admin; una clienta que fuerza `/admin` ve una página de no autorizado — el espejo frontend del 403 que D-33 enseñó en backend.

#### Asistente IA: estrategia mini-RAG (AIAS-02)
- **D-56:** **Retrieval trivial y honesto: el catálogo activo completo va en el system prompt de cada request** (12 SKU: id, nombre, familia aromática, notas, precio — cabe entero). Gemini responde **JSON estructurado** (texto de recomendación + ids de productos citados); **el backend valida cada id contra la BD** antes de responder y arma las product cards que el chat muestra clicables (AIAS-02 palabra por palabra). Sin embeddings ni vector store. La forma exacta de forzar JSON en google-genai 2.25 (`response_mime_type`/`response_schema` o equivalente) **la valida el research contra la doc oficial — no se firma sobre supuestos** (misma lección que D-41 con el spike de Webpay).

#### Conversación del chat (AIAS-01)
- **D-57:** **Respuesta única request-response, sin streaming.** La lección es la integración del servicio externo y su contrato, no SSE/streaming de tokens.
- **D-58:** **Multi-turno stateless: el frontend mantiene el historial visible y lo envía en cada request.** El backend no guarda conversaciones en BD ni estado de sesión del chat — cero tablas nuevas para el asistente.
- **D-59:** **Endpoint público, sin login** — la asesora atiende a quien navega la tienda (P8), como `/api/pago/retorno` ya es público por diseño. Salvaguardas básicas de input (largo máximo de mensaje y del historial enviado) protegen el free tier. La burbuja flotante vive en el layout de la tienda (visible en las páginas públicas), con panel de chat desplegable — la forma exacta a discreción del UI.

#### API key y degradación (AIAS-03)
- **D-60:** **Cada alumno crea SU PROPIA API key gratis en Google AI Studio** — paso del alumno dentro de la guía (mismo patrón que D-08 con las fotos: nada compartido por el proyecto), sin tarjeta de crédito. `GEMINI_API_KEY` vive en el `.env` del backend vía pydantic-settings, como `secret_key` en fase 2 — jamás en código ni en el frontend.
- **D-61:** **Sin key la app arranca normal (degradación, NO fail-fast)** — el asistente es un servicio opcional, a diferencia de `secret_key`: sin key el endpoint responde **503 con mensaje amable** y la burbuja muestra "asistente no disponible"; la tienda sigue 100% operativa. La guía enseña el manejo de errores del servicio externo: **429** (cuota del free tier), timeout / error de red de Gemini → mensaje amable + reintentar (el wrapper atrapa los errores del SDK, jamás un 500 crudo — mismo patrón que IN-06 con `TransbankError`). **AIAS-03 se verifica con grep sobre el build del frontend** (`dist/`) buscando la key sin resultados — pieza fija de la Gran verificación final de la fase.

#### Partición de la fase
- **D-62:** **Orden de construcción: contrato 0.4.0 + ADRs primero (D-15), luego panel admin completo (backend → frontend), después asistente IA (backend → burbuja frontend), cerrando con la Gran verificación final de fase 4.** El admin va antes que la IA: el panel no depende del asistente, y la burbuja reusa las product cards del catálogo ya existentes. La partición exacta en sub-guías `guia-12+` es discreción del planner bajo este orden.

### Claude's Discretion
- Nombres y estructura exacta de los endpoints nuevos al extender `contrato_api.yaml` a 0.4.0 (tag Administración: `/api/admin/productos*`, `/api/admin/pedidos*`, `/api/admin/metricas`; tag Asistente: `/api/asistente` vs `/api/chat`; schemas ProductoCrear/ProductoEditar/PedidoTransicion/Metricas/ChatMensaje).
- Qué ADRs escribe la fase y su título exacto (candidatos naturales: panel admin protegido por rol en los dos tiers, máquina de estados de pedidos con transiciones validadas, asistente IA con mini-RAG y key solo en backend), continuando desde ADR-015.
- Numeración nueva de RF/RNF/RN/HU en `02_requerimientos.md` (continuar las series: van RF-19, RNF-08, RN-14, HU-12) y pantallas 10+ de `03_diseno.md` (panel y burbuja).
- Valor exacto del umbral de stock bajo (D-53 propone ≤ 5) y superficie del badge.
- Schema exacto de la respuesta JSON del asistente y forma de forzarlo en google-genai 2.25 (el research lo valida; D-56 fija que existe la validación).
- Estructura de sub-rutas del panel y del layout admin (D-55 fija `/admin` + guard; los paths internos son libres).
- Código HTTP para transición ilegal de pedidos (409 vs 422) y demás detalles finos del contrato.
- Copys del panel, la burbuja y los estados vacíos (tokens y Copywriting Contract de `01-UI-SPEC.md` / `02-UI-SPEC.md`); la voz de la asesora conecta con la persona de Maura (D-02).
- Cómo se parte el trabajo en sub-guías `guia-12+` respetando el orden D-62, y qué incluye la Gran verificación final además del grep del build (tabla CS/RF + fila contrato 0.4.0 ↔ `/docs` con Authorize admin, como siempre).

### Deferred Ideas (OUT OF SCOPE)
- **Upload de imágenes de producto desde el panel** (multipart + guardado en disco) — fuera de ADMN-01 por D-51; candidato natural para v2 si el curso lo pide.
- **Refund/anulación de pago PAID desde el panel** — ya está en REQUIREMENTS v2 como ADMN-05; D-50 lo deja explícitamente fuera.
- **Gráficos en las métricas del panel** — ya está en v2 como STAKE-04; ADMN-04 fija tarjetas + tabla.
- **Streaming de la respuesta del chat** — descartado por D-57 para esta fase; sería una adición posterior sobre el mismo endpoint.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ADMN-01 | Admin hace CRUD de productos con soft delete | Entidad PRODUCTO ya tiene `activo` (docs/03 §2.2/§2.3.5, leído este session); snapshot de líneas protege pedidos viejos (D-36); endpoints nuevos tag Administración bajo `get_current_admin` (patrón guia-05:459); imágenes como texto por D-51 |
| ADMN-02 | Admin gestiona stock con alerta de stock bajo | Umbral constante backend D-53 (propuesta ≤5); nota: NO confundir con el umbral de "últimas unidades" de tienda (stock 1-3, 01-UI-SPEC:130) — dos conceptos distintos que la guía debe separar |
| ADMN-03 | Admin gestiona pedidos con transiciones validadas en backend | Estados `pending/paid/cancelled/rejected` verbatim en contrato 0.3.0:252; única transición manual admin: PENDING→CANCELLED (D-50); huérfanas PENDING ya visibles "en curso" (guia-11, D-48/D-49) |
| ADMN-04 | Admin ve métricas (tarjetas + tabla, sin gráficos) | 4 KPIs computables desde PEDIDO/LÍNEA existentes (D-54); reemplaza `/api/admin/estado` (contrato 0.3.0:492-536); lección OpenAPI: HTTPException manual debe declararse en `responses` (guia-05:586) |
| AIAS-01 | Cliente usa chat (burbuja) donde el asistente recomienda productos del catálogo real | Endpoint público `security: []` como `/api/pago/retorno` (patrón contrato 0.3.0:589-604); request-response sin streaming (D-57); multi-turno stateless (D-58); burbuja en layout tienda (D-59) |
| AIAS-02 | Asistente responde solo con productos existentes (mini-RAG + validación ids BD) + product cards clicables | Structured output firmado con evidencia: `response_json_schema` en README v2.25.0 (ver Code Examples); mini-RAG por system prompt con catálogo activo (D-56); validación de ids contra BD antes de responder |
| AIAS-03 | API key solo en backend (env var), nunca en código ni bundle frontend | `GEMINI_API_KEY` auto-pickup por el Client verificado (README v2.25.0); patrón `.env` + `SettingsConfigDict(env_file=".env")` de guia-05:124; verificación grep sobre `dist/` en Gran verificación final (D-61) |
</phase_requirements>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Validación de transición de pedidos (D-50) | API / Backend | — | La máquina de estados se valida en el servidor (`get_current_admin` + service); el panel solo pide y muestra. Espejo de la lección D-33: el guard SPA es UX, el 403/409 real es backend |
| CRUD productos + soft delete (D-51/D-52) | API / Backend | SPA (formularios) | Escritura con validación Pydantic y `get_current_admin`; el toggle `activo` es una escritura más. El catálogo público ya filtra activos (contrato 0.3.0:306-307 "Devuelve solo productos activos") |
| Cómputo de métricas (D-54) | API / Backend | — | Agregación SQL sobre PEDIDO/LÍNEA (sum/group by) en repositories; la SPA solo renderiza tarjetas y tabla |
| Guard de ruta admin (D-55) | Browser / Client | API (403 real) | `RequireAdmin` extiende `RequireAuth` — UX que evita la pantalla rota; la seguridad real son las dependencias de rol del backend |
| Layout del panel + burbuja de chat | Browser / Client | — | Rutas anidadas React Router bajo `/admin`; burbuja flotante en el layout de la tienda (páginas públicas) |
| Llamada a Gemini + API key + retrieval (D-56/D-60) | API / Backend | — | La key jamás cruza al cliente; el system prompt con catálogo se arma en el backend; wrapper de errores del SDK (patrón IN-06) |
| Historial visible del chat (D-58) | Browser / Client | API (valida largo) | El frontend mantiene y envía el historial; el backend solo impone topes de largo (RN nueva) |
| Validación de ids recomendados (D-56) | API / Backend | — | Cada id del JSON del modelo se valida contra catálogo activo en BD antes de responder — la muralla anti-alucinación |
| Producto catalálogo (fotos) | CDN / Static (SPA) | — | Sin cambios: fotos ya viven en `frontend/public/products/{sku}.jpg` (D-08/D-51) |

## Standard Stack

### Core

**Ninguna pieza nueva del stack se instala en fase 4 salvo el SDK de Gemini en el backend del alumno** (guía nueva). El stack del proyecto ya está verificado en `.planning/research/STACK.md` (React 19.3, Vite 8.3.1, TS ~6.0.2, React Router 8.4.0, TanStack Query 5.104, Zustand 5.0.15, Tailwind 4.3.3, FastAPI 0.141.1, SQLAlchemy 2.1.1, Pydantic 2.13.5, pydantic-settings 2.15.0, pytest 9.1.1). Tabla de lo que esta fase usa:

| Library | Version | Purpose | Why Standard | Provenance |
|---------|---------|---------|--------------|-----------|
| google-genai (Python) | 2.25.0 — pin `>=2.25,<3` | Asistente Gemini: `generate_content` con JSON estructurado | SDK oficial de Google; **2.25.0 es la latest en PyPI hoy** (verificado: `pip index versions google-genai` lista 2.25.0 como tope, 120+ versiones desde 0.0.1); README del tag v2.25.0 documenta el patrón exacto que la guía necesita | [VERIFIED: PyPI registry + README @ tag v2.25.0 este session] |
| pydantic-settings | 2.15.0 (ya instalada) | `GEMINI_API_KEY` opcional en `.env` — degradación D-61 | Patrón ya construido en guia-05: `class Settings(BaseSettings)` + `model_config = SettingsConfigDict(env_file=".env")` [VERIFIED: docs/05_desarrollo/guia-05-cuentas-backend.md:116-124] | [VERIFIED: in-repo guia-05] |
| React Router 8 (ya instalado) | 8.4.0 | Ruta anidada `/admin` con layout + `Outlet` | Modo declarativo que `main.tsx` ya usa (`<Route element={<RequireAuth />}>` con hijos, guia-11 paso 4) | [VERIFIED: in-repo guia-11:409-414] |
| TanStack Query (ya instalado) | 5.104.0 | Queries del panel (productos/pedidos/métricas) y `useMutation` del chat | Patrón uniforme `useQuery` de todas las pantallas; mutaciones de admin invalidan `queryKey` | [VERIFIED: in-repo guia-11:91-94] |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Pydantic (ya instalada) | 2.13.5 | `ProductoCrear`/`ProductoEditar`/`PedidoTransicion`/`ChatMensaje` y el schema JSON del asistente vía `.model_json_schema()` | Siempre — API-first D-15; el schema del asistente sale del mismo Pydantic (ver Code Examples) |
| Tailwind (ya instalada) | 4.3.3 + paleta `@theme` del lift | Panel y burbuja con los tokens existentes | Siempre — 02-UI-SPEC fija la paleta verbatim (ver Code Examples) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `models.generate_content` + `GenerateContentConfig` (patrón del pin 2.x) | Interactions API (`client.interactions.create` + `response_format`) — lo que muestran las docs actuales de ai.google.dev | **No para esta guía**: `response_format` no aparece en el README v2.25.0 (verificado); el pin `>=2.25,<3` garantiza el patrón `generate_content`. La guía puede NARRAR el drift como lección |
| `response_json_schema=<Modelo>.model_json_schema()` | `response_schema=<Modelo>` (acepta la clase Pydantic directa) | Ambos existen en el SDK, pero el README v2.25.0 documenta SOLO `response_json_schema` (verificado: `response_schema` no aparece). La guía usa lo documentado en su pin exacto |
| `gemini-flash-latest` (alias) | `gemini-3.8-flash` (estable concreto de hoy) | El alias se hot-swappea con cada release (2 semanas de aviso para breaking changes, citado); el estable concreto envejece. Recomendación: alias `gemini-flash-latest` (es el modelo de ejemplo dominante del README v2.25.0) — decisión del planner |

**Installation (paso del alumno dentro de la guía nueva, backend):**

```bash
uv add "google-genai>=2.25,<3"
```

**Version verification (ejecutada este session):** `pip index versions google-genai` → `google-genai (2.25.0)` es la latest; la lista completa va de 0.0.1 a 2.25.0 (120+ releases). El pin `>=2.25,<3` queda vigente y coincide con el consejo del propio SDK: "To avoid unexpected updates, pin the SDK version to `< 3.0.0`" [VERIFIED: README @ main, sección AFC deprecation].

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| google-genai | PyPI | 120+ versiones desde 0.0.1 (latest 2.25.0 publicada 2026-09-22) | no disponible al seam (`weeklyDownloads: null`) | github.com/googleapis/python-genai (oficial Google) | **SUS** (seam: "too-new", "unknown-downloads") | **Mantenido — falso positivo documentado** |

**Packages removed due to SLOP verdict:** none.

**Packages flagged as suspicious [SUS]:** `google-genai` [WARNING: flagged as suspicious by the seam — verify before using.] — **Contexto del falso positivo:** el seam lee `publishedAt` de la versión latest (2026-09-22, hace 8 días) y no tiene estadísticas de descargas de PyPI, por lo que marca "too-new/unknown-downloads". Las señales reales que refutan el veredicto: (1) `pip index versions` lista 120+ versiones desde 0.0.1 — un paquete establecido por años; (2) repo oficial `github.com/googleapis/python-genai` (organización googleapis); (3) las docs oficiales de Google (ai.google.dev) enseñan este SDK como el oficial; (4) verificación previa en `.planning/research/STACK.md` (2026-09-28) con el mismo resultado; (5) el mismo seam produjo un falso SUS para `fastapi` en la exploración del stack (artefacto documentado en STACK.md §Sources). **No se requiere checkpoint:human-verify adicional** — CONTEXT.md ya lock-ea `google-genai` como decisión de usuario (D-56/PROJECT.md constraint) y la triple verificación de este session lo confirma. No hay paquetes npm nuevos en esta fase (la burbuja y el panel usan el stack frontend existente).

## Architecture Patterns

### System Architecture Diagram

Flujo del asistente (la pieza nueva con servicio externo — el panel admin es CRUD convencional sobre los mismos tiers):

```
 Visitante anónimo                TIER CLIENTE (SPA)                TIER SERVIDOR (FastAPI en capas)           EXTERNO
 ┌──────────────┐      ┌─────────────────────────────┐      ┌──────────────────────────────────┐    ┌──────────────┐
 │ escribe en   │─────►│ Burbuja de chat (layout     │─────►│ POST /api/asistente  (público,   │    │ Google       │
 │ la burbuja   │ JSON │ tienda) — historial visible │ JSON │ security: [])                    │    │ Gemini API   │
 │              │      │ en el navegador (D-58)      │      │  ├─ valida largo mensaje/hist.   │    │ (free tier)  │
 └──────────────┘      └─────────────────────────────┘      │  ├─ arma system prompt con       │    └──────▲───────┘
                                                            │  │  catálogo ACTIVO (mini-RAG)    │           │ HTTPS
                                                            │  ├─ genai.Client() key del .env  │───────────┘
                                                            │  │  generate_content +            │  response_mime_type
                                                            │  │  response_json_schema          │  'application/json'
                                                            │  ├─ wrapper atrapa errors.APIError│
                                                            │  │  (429/timeout/red) → amable    │
                                                            │  └─ valida ids vs BD activa ─────┼── descarta ids
                                                            └──────────────┬───────────────────┘   alucinados
                                                                           │ 200 {respuesta, productos:[ids]}
                                                                           ▼
                                                            SPA renderiza texto + product cards
                                                            clicables (reusan la card del catálogo)

 Sin GEMINI_API_KEY en .env ──► Client/llamada falla ──► 503 "asistente no disponible" ──► burbuja degradada,
                                                                tienda 100% operativa (D-61)
```

Puntos de decisión trazables: (a) sin key → 503 temprano, sin tocar Gemini; (b) error del SDK → mensaje amable, jamás 500 crudo; (c) ids del modelo → filtro contra BD antes de responder. El panel admin no aparece en el diagrama porque no cruza servicios externos: es CRUD JSON estándar entre los mismos dos tiers.

### Recommended Project Structure

El "proyecto" es el árbol del ALUMNO que las guías construyen (guide-only, D-17). Extensiones de fase 4 sobre el árbol ya narrado en `docs/04_arquitectura/README.md` (líneas 143-146 citan security.py, models/pedido.py):

```
backend/                              frontend/
├── app/                              ├── src/
│   ├── routers/                      │   ├── components/
│   │   ├── admin.py          # NUEVO # │   │   ├── RequireAdmin.tsx      # NUEVO (extiende RequireAuth)
│   │   └── asistente.py      # NUEVO # │   │   └── Navbar.tsx            # gana link "Panel" (solo admin)
│   ├── services/                     │   ├── features/
│   │   ├── admin.py          # NUEVO # │   │   ├── admin/                # NUEVO (layout + 3 sub-pantallas)
│   │   └── asistente.py      # NUEVO # │   │   └── asistente/            # NUEVO (burbuja + panel de chat)
│   ├── repositories/                 │   └── lib/api.ts          # gana apiPost al chat (ya existía)
│   │   └── (extiende los de          │
│   │      productos/pedidos)         │
│   └── schemas/ (o el módulo         │
│       existente de schemas)         │
│       # ProductoCrear/Editar,       │
│       # PedidoTransicion, Metricas, │
│       # ChatMensaje/ChatRespuesta   │
└── .env  # gana GEMINI_API_KEY       │
    (opcional, NO fail-fast)          │
```

Reglas de dependencia vigentes (04_arquitectura): routers sin SQLAlchemy, services sin HTTP, todo HTTP del frontend por `lib/api.ts`, features sin imports cruzados (la excepción se narra, como `VoucherPedido` en guia-11). El asistente es un service que habla un SDK externo — mismo lugar que el service de Webpay (guia-09); su router es el único que sabe de HTTP, y las product cards del chat reusan la card existente del catálogo (import cruzado con razón, patrón D-46).

### Pattern 1: Structured output en google-genai 2.25 (LA pieza D-56)

**What:** Forzar respuesta JSON conforme a un schema con `GenerateContentConfig`.
**When to use:** Endpoint del asistente — respuesta `{respuesta, productos}` sin parseo frágil.
**Ejemplo verbatim del README en el tag exacto del pin:**

```python
# Source: github.com/googleapis/python-genai README @ tag v2.25.0 (fetched 2026-09-30)
class CountryInfo(BaseModel):
    name: str
    population: int
    capital: str
    continent: str
    gdp: int
    official_language: str
    total_area_sq_mi: int

response = client.models.generate_content(
    model='gemini-flash-latest',
    contents='Give me information for the United States.',
    config=types.GenerateContentConfig(
        response_mime_type='application/json',
        response_json_schema=CountryInfo.model_json_schema(),
    ),
)
```

Notas firmadas: el README v2.25.0 documenta `response_json_schema` (acepta `Modelo.model_json_schema()` de Pydantic o un dict); el nombre de campo `response_schema` NO aparece en ese README; advierte no duplicar el schema en el prompt ("the generated output might be lower in quality"). El modelo de ejemplo del README es `'gemini-flash-latest'`.

### Pattern 2: API key por env var con degradación (D-60/D-61)

**What:** `genai.Client()` levanta la key del entorno automáticamente; el Settings del backend la hace opcional.
**When to use:** Service del asistente.

```python
# Source: patrón Settings verbatim in-repo (guia-05:116-124) + cita README v2.25.0:
# "Set the `GEMINI_API_KEY` or `GOOGLE_API_KEY`. It will automatically be picked up by the client."
# (si ambas están, GOOGLE_API_KEY tiene precedencia — recomiendan setear solo una)

class Settings(BaseSettings):
    # ... secret_key, admin_email, cliente_password (existentes, fail-fast) ...
    gemini_api_key: str | None = None   # NUEVO: opcional — el asistente degrada, no bloquea (D-61)
    model_config = SettingsConfigDict(env_file=".env")
```

El client se construye lazy dentro del service (o con guard de None) para que la app arranque sin key. **[ASSUMED]** el comportamiento exacto de `genai.Client()` sin key ni env (se espera que levante excepción al construir o al llamar) — el UAT delegado lo confirma runtime antes de firmar la guía; el wrapper debe atrapar AMBOS momentos.

### Pattern 3: Wrapper de errores del servicio externo (patrón IN-06 replicado)

**What:** El service del asistente atrapa TODO error del SDK y lo traduce a respuestas amables; jamás un 500 crudo.
**When to use:** Toda llamada a Gemini.

```python
# Source: errores del SDK verbatim README v2.25.0 + backoff citado de ai.google.dev/gemini-api/docs/troubleshooting
from google.genai import errors

try:
    respuesta = cliente.models.generate_content(...)
except errors.APIError as e:
    # e.code (int HTTP) y e.message — el README lo demuestra con 404
    if e.code == 429:      # RESOURCE_EXHAUSTED — cuota del free tier (sin prometer cifras, concern abierto)
        raise HTTPException(status_code=429, detail=<copy amable reintentar>)  # código final a discreción del contrato
    raise HTTPException(status_code=503, detail=<copy asistente no disponible>)
```

Dato clave para la narración: **el SDK ya reintenta solo** los errores transitorios "up to four times with an initial delay of approximately 1 second and a maximum delay of 60 seconds" [CITED: ai.google.dev/gemini-api/docs/troubleshooting] — el wrapper del alumno es la capa de traducción a mensaje amable, no un retry-engine (evitar doble-retry pesado es un error-evitado de guía).

### Pattern 4: RequireAdmin extiende RequireAuth (D-55)

**What:** Guard por rol en la SPA — espejo UX del 403 backend.
**When to use:** Rama `/admin` en `main.tsx`.
**Base in-repo verbatim (guia-06:961):** "`RequireAuth` con `Navigate state={{ from: location }} replace` y el login que vuelve con `location.state?.from?.pathname ?? \"/\"`: el returnTo genérico (D-32)".

```tsx
// Adaptación del patrón existente (guia-06 paso 5) — RequireAdmin suma el claim de rol (ADR-011)
// y sin rol renderiza la página de no autorizado (el espejo del 403 de D-33), SIN expulsar al login:
// una clienta con sesión válida no necesita autenticarse de nuevo — le falta permiso, no identidad.
export default function RequireAdmin() {
  const { usuario } = useSesion();  // store existente: usuario con rol desde el primer token
  if (!usuario) {
    return <RequireAuth />;         // sin sesión: el guard existente hace returnTo
  }
  if (usuario.rol !== "admin") {
    return <NoAutorizado />;        // con sesión sin rol: página de no autorizado
  }
  return <Outlet />;
}
```

### Pattern 5: Ruta anidada con layout (D-55)

```tsx
// Adaptación del estilo declarativo de main.tsx (guia-11:409-414 usa <Route element={<RequireAuth />}> con hijos)
<Route element={<RequireAdmin />}>
  <Route path="/admin" element={<LayoutAdmin />}>   {/* nav interna del panel + <Outlet /> */}
    <Route index element={<AdminProductos />} />
    <Route path="pedidos" element={<AdminPedidos />} />
    <Route path="metricas" element={<AdminMetricas />} />
  </Route>
</Route>
```

### Pattern 6: Mini-RAG honesto + validación de ids (D-56)

**What:** Catálogo activo completo en el system prompt; respuesta JSON con ids; filtro contra BD.
**When to use:** Service del asistente (sketch de estructura — los valores discretos del catálogo son del contrato 0.3.0):

```python
# Sketch adaptado — familia enum verbatim contrato 0.3.0:106: [citricas, florales, frutales, dulces]
# System prompt (se arma por request): "Eres Maura... Recomienda SOLO de este catálogo:
# id=1 nombre=Brisa de Naranja familia=citricas notas=[naranja, bergamota, mandarina] precio=7990; ..."
# → 12 SKU activos caben completos (D-56).

class Recomendacion(BaseModel):
    respuesta: str          # texto de la asesora, voz de Maura (D-02)
    productos: list[int]    # ids citados — el backend los valida contra catálogo ACTIVO

# Después de generate_content + response_json_schema=Recomendacion.model_json_schema():
ids_validos = {p.id for p in repo.activos()}          # consulta BD
recomendacion.productos = [i for i in recomendacion.productos if i in ids_validos]
# → el chat solo puede mostrar cards que existen; los ids alucinados se descartan en silencio (AIAS-02)
```

### Pattern 7: Tokens UI del panel/burbuja (heredados, no nuevos)

Paleta `@theme` verbatim vigente (02-UI-SPEC:39-48): `--color-orange-50: #fbf4ea`, `--color-orange-100: #f5e5ce`, `--color-orange-200: #ebd0ac`, `--color-orange-600: #d9480f`, `--color-orange-700: #b03a0c`. BADGES de estado existentes (guia-11:81-86, verbatim): `paid → "Pagado" (bg-emerald-100 text-emerald-800)`, `pending → "En curso" (bg-amber-100 text-amber-800)`, `rejected → "Rechazado" (bg-red-50 text-red-600)`, `cancelled → "Anulado" (bg-neutral-200 text-neutral-700)`. El panel de pedidos REUSA esta tabla (misma regla D-45 de una sola verdad del estado); "stock bajo" admin es un badge NUEVO (ámbar) y "Inactivo" otro (neutral) — a discreción con los tokens existentes.

### Anti-Patterns to Avoid

- **Seguir las docs actuales de ai.google.dev para structured output**: enseñan `client.interactions.create` + `response_format`, patrón ausente del README v2.25.0 — con el pin `>=2.25,<3` el alumno escribe `models.generate_content`. El drift se narra, no se copia.
- **Poner la key en el cliente "por un rato"** (env de Vite, `import.meta.env`): cualquier variable `VITE_*` termina en el bundle — AIAS-03 existe exactamente para esto. La key viaja SOLO por el `.env` del backend.
- **Filtrar ids alucinados en el FRONTEND**: la validación es del backend (D-56) — el chat renderiza lo que el backend ya validó.
- **Retry-engine casero sobre el SDK**: el SDK ya reintenta transitorios 4x — el wrapper traduce, no re-reintenta.
- **Fail-fast sin key**: el asistente es opcional (D-61) — arrancar la tienda sin `GEMINI_API_KEY` es un requisito, no un bug.
- **Estados nuevos del pedido** ("enviado", "entregado"): D-50 los veta; la máquina es la existente de 4 estados con UNA transición manual admin.
- **Prometer cifras RPM/RPD en la guía**: no hay fuente pública sin login (verificado este session) — el 429 se enseña sin números.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Forzar JSON del modelo | Prompt-engineering "responde SOLO JSON" + `json.loads` frágil | `response_mime_type='application/json'` + `response_json_schema` | Garantía del servicio + schema validado en origen; el parseo manual revienta con un backtick perdido |
| Validar que el JSON calza el schema | Validador a mano campo por campo | Pydantic `Recomendacion.model_validate_json(...)` (el mismo modelo que generó el `.model_json_schema()`) | Round-trip Pydantic→schema→respuesta→Pydantic, un solo lugar de verdad |
| Retry con backoff del SDK | Loop propio con sleep | Nada — el SDK reintenta transitorios 4x (~1s inicial, 60s máx) | Doble-retry multiplica la presión sobre el free tier |
| Client HTTP a Gemini | `requests`/`httpx` directo a la REST API | `google-genai` SDK oficial | Auth, errores tipados (`errors.APIError`), retries y versiones del SDK |
| Gráficos de métricas | Cualquier librería de charts | Tarjetas + tabla HTML (ADMN-04 locked; STAKE-04 diferido) | Requisito explícito sin librerías |
| Guard de rol solo en frontend | "Como el botón no se ve, no se puede llamar" | `get_current_admin` en CADA endpoint admin (guia-05) + RequireAdmin como UX | Lección D-33: el 403 real es del servidor |
| Historial de chat en BD | Tabla `mensajes` + sesión de chat | Historial en el cliente, enviado por request (D-58) | Cero tablas nuevas; el chat es stateless por decisión |

**Key insight:** La fase reusa cuatro piezas ya construidas por las guías anteriores — `get_current_admin` (guia-05), `RequireAuth`+returnTo (guia-06), la card de producto del catálogo (guia-04) y la tabla BADGES (guia-10/11). La novedad real es UNA: la integración Gemini con structured output. Las guías deben cobrar esas herencias como guia-11 cobró `VoucherPedido` (D-46).

## Common Pitfalls

### Pitfall 1: Drift docs ↔ SDK pinneado (structured output)
**What goes wrong:** El alumno (o la guía) sigue la página actual de structured output de ai.google.dev y escribe `client.interactions.create(..., response_format={...})` — patrón que no está en el README v2.25.0; con el pin `>=2.25,<3` la superficie documentada es `models.generate_content` + `GenerateContentConfig(response_mime_type, response_json_schema)`.
**Why it happens:** Las docs web de Google avanzan más rápido que el pin del proyecto (el propio SDK advierte pin `< 3.0.0` porque la 3.x moverá APIs).
**How to avoid:** La guía cita el patrón con su fuente (README del SDK en la versión instalada) y narra el drift como lección: "las docs del servicio y la versión pinneada del SDK son dos cosas distintas".
**Warning signs:** `AttributeError`/`TypeError` en `interactions` o `response_format` en el proyecto del alumno.

### Pitfall 2: `response_schema` vs `response_json_schema`
**What goes wrong:** Blog posts y ejemplos antiguos muestran `response_schema=Modelo` (la clase directa); el README del tag v2.25.0 documenta `response_json_schema` con `.model_json_schema()` (verificado este session: `response_schema` no aparece en ese README).
**Why it happens:** El SDK ha tenido ambas formas; los ejemplos de internet mezclar generaciones.
**How to avoid:** La guía usa exactamente la forma documentada en el README de su pin: `response_json_schema=Recomendacion.model_json_schema()`.
**Warning signs:** Errores de tipo al pasar la clase donde se espera dict/schema JSON.

### Pitfall 3: El modelo cita ids que no existen (o inactivos)
**What goes wrong:** Gemini devuelve ids alucinados o de productos desactivados por el admin — el chat mostraría cards rotas o productos que ya no se venden.
**Why it happens:** Todo LLM alucina; el catálogo cambia mientras el modelo solo vio el prompt.
**How to avoid:** Doble muralla firmada en D-56: system prompt solo con catálogo ACTIVO + filtrado de ids contra BD antes de responder. Los pedidos viejos NO se rompen: usan snapshot (D-36).
**Warning signs:** Card con imagen/precio vacíos en el chat.

### Pitfall 4: 429 en clase (free tier)
**What goes wrong:** Un alumno spamea la burbuja y su key entra en cuota — 429 RESOURCE_EXHAUSTED.
**Why it happens:** Free tier con RPM/RPD no públicos (verificado: requieren login en AI Studio).
**How to avoid:** (a) cada alumno con SU key (D-60) aísla la cuota; (b) topes de largo de mensaje/historial (RN nueva) acotan tokens; (c) wrapper 429→mensaje amable; (d) la guía JAMÁS promete cifras de límites (concern abierto de STATE.md). El SDK ya reintenta transitorios — el mensaje llega después de 4 intentos internos.
**Warning signs:** `errors.APIError` con `e.code == 429` repetido.

### Pitfall 5: HTTPException manual invisible en `/docs`
**What goes wrong:** El 503 del asistente o el 409 de transición ilegal se lanzan con `HTTPException` pero no aparecen en el panel — la fila contrato ↔ `/docs` de la Gran verificación final canta un desvío falso.
**Why it happens:** Lección ya firmada in-repo: "cada `HTTPException` lanzada a mano NO aparece en OpenAPI si no se [declara en responses]" [VERIFIED: guia-05:586].
**How to avoid:** Declarar cada response nueva en el router (mismo fix que G-01-4 hizo con el 404 en guia-04) Y en el contrato 0.4.0 — el par debe calzar.
**Warning signs:** La comparación contrato ↔ `/docs` fila por fila.

### Pitfall 6: Dos umbrales de stock distintos confundidos
**What goes wrong:** La guía usa el mismo número para "stock bajo" del admin (D-53, propuesto ≤5) y para "¡Últimas N unidades!" de la clienta.
**Why it happens:** Suenan igual pero son decisiones distintas: la de tienda es urgencia de compra (stock 1-3, 01-UI-SPEC:130 `bg-amber-100 text-amber-800`); la de admin es alerta de reabastecimiento (constante del backend, RN nueva).
**How to avoid:** Dos constantes con nombre, dos RN, dos badges — y una pregunta de control que las contraste.
**Warning signs:** Un solo umbral mencionado en la guía.

### Pitfall 7: Remover `/api/admin/estado` en silencio
**What goes wrong:** Borrar el endpoint demo y que las guías 05/06 (que lo construyeron y contaron sus paths) queden apuntando a un path fantasma.
**Why it happens:** D-54 lo reemplaza — pero el cambio es de contrato publicado (0.3.0) y las guías viejas no se re-editan.
**How to avoid:** La subida a 0.4.0 NARRA la evolución (el endpoint cumplió su lección D-33); la fila de la Gran verificación final cuenta los paths NUEVOS contra 0.4.0, y el "Siguiente"/intro de la guía nueva explica por qué el demo se retira. Mismo criterio de las fases previas: jamás cambia en silencio.
**Warning signs:** Contrato sin nota de evolución; guías viejas editadas (prohibido: se rompe la trazabilidad).

### Pitfall 8: grep del build no portable (Gran verificación final)
**What goes wrong:** `grep -r GEMINI_API_KEY dist/` asume Git Bash; un alumno en PowerShell se queda sin verificación.
**How to avoid:** La guía da el comando para ambos shells (Git Bash `grep -r "GEMINI_API_KEY" dist/` / PowerShell `Select-String -Path dist\\* -Pattern "GEMINI_API_KEY" -SimpleMatch:$false -Recurse` o `findstr /s /i "GEMINI_API_KEY" dist\\*`), con resultado esperado: cero coincidencias. Debe correrse DESPUÉS de `npm run build` (dist/ regenerado).
**Warning signs:** La fila del grep sin comando explícito por shell.

## Code Examples

### Ejemplo A: Endpoint del asistente completo (sketch integrador para la guía)

```python
# Adaptación de patrones verificados este session: wrapper Pattern 3 + structured output Pattern 1 +
# Settings Pattern 2 + seguridad pública contrato 0.3.0:589-604 (`security: []` de /api/pago/retorno).
# Nombres finales de paths/schemas: discreción del planner (Claude's Discretion de CONTEXT.md).

@router.post("/api/asistente", status_code=200)
async def conversar(mensaje: ChatMensaje, sesion: Session = Depends(get_session)):
    # 1. Pydantic ya validó largos máximos (422 si excede) — salvaguardas D-59
    # 2. Sin key → 503 temprano (D-61); con key → llamada Gemini:
    #    client.models.generate_content(model=..., contents=historial, config=GenerateContentConfig(
    #        response_mime_type='application/json',
    #        response_json_schema=Recomendacion.model_json_schema()))
    # 3. errors.APIError → 429/503 amables; error de red/timeout → 503 amable (wrapper Pattern 3)
    # 4. ids validados contra catálogo activo (Pattern 6)
    # 5. 200 {"respuesta": "...", "productos": [1, 7]}  — el chat arma cards clicables
    ...
```

### Ejemplo B: Lo que el contrato 0.3.0 declara hoy para `/api/admin/estado` (a reemplazar, D-54)

```yaml
# Source: docs/04_arquitectura/contrato_api.yaml:492-536 (verbatim, leído este session)
  /api/admin/estado:
    get:
      tags: [Administración]
      summary: Conteos del catálogo (endpoint demo protegido por rol)
      # ... description cita AUTH-03, D-33 ... responses: 200 {productos, familias}, 401, 403
      #    example 403: detail: Requiere rol admin
```

### Ejemplo C: Máquina de estados para la guía de pedidos admin (D-50)

```python
# Transiciones legales (D-50): el flujo de pago posee las suyas (guia-09/10);
# el admin tiene exactamente UNA transición manual:
TRANSICIONES_ADMIN = {"pending": {"cancelled"}}   # PENDING → CANCELLED; PAID es terminal (refund = ADMN-05, v2)
# El service valida: estado actual ∈ TRANSICIONES_ADMIN[?] ... ilegal → 409 (recomendado) o 422 (discreción)
# Cancelar una PENDING NO toca stock (D-35) — la transición es limpia.
```

### Ejemplo D: Métricas desde las tablas existentes (D-54 — sketch SQL/SQLAlchemy)

```python
# Ingresos:   sum(Pedido.total).where(estado == "paid")
# Por estado: group_by(Pedido.estado) → 4 contadores
# Top 5:      join(LINEA, Pedido).where(estado == "paid").group_by(producto_id)
#             .order_by(sum(cantidad) desc).limit(5) — nombre desde el SNAPSHOT (honesto con soft delete, D-36/D-52)
# Stock bajo: count(Producto).where(activo == True, stock <= UMBRAL)  # UMBRAL constante backend (D-53)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `google-generativeai` (SDK previo de Gemini) | `google-genai` | EOL 2025-11-30 (verificado en exploración previa, PROJECT.md) | Ya vetado en REQUIREMENTS Out of Scope — la guía ni lo menciona salvo como anti-patrón |
| Docs de structured output con `generate_content` | ai.google.dev ahora enseña Interactions API (`client.interactions.create` + `response_format`) | Vigente a 2026-09-30 (página fetched este session) | El pin 2.x usa `models.generate_content`; la guía narra el drift (Pitfall 1) |
| Modelos 2.5 (época del stack research) | Estable actual `gemini-3.8-flash`; alias `gemini-flash-latest` hot-swappeado con 2 semanas de aviso | 2026 (models page fetched este session) | La guía prefiere el alias `gemini-flash-latest` (modelo de ejemplo del README v2.25.0) para no podrirse |
| passlib / python-jose (tutoriales viejos) | pwdlib[argon2] / PyJWT | Fases previas ya lo adoptaron | Sin cambios en fase 4 |

**Deprecated/outdated:**
- `google-generativeai`: EOL — prohibido (REQUIREMENTS.md Out of Scope).
- `response_schema` como forma documentada: en el README v2.25.0 el campo documentado es `response_json_schema` (el nombre viejo sobrevive en ejemplos de terceros — Pitfall 2).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `genai.Client()` sin key ni env lanza excepción (al construir o al primer uso) que el wrapper puede atrapar para degradar a 503 | Pattern 2 / Pitfalls | Si el Client no falla temprano, la degradación ocurre en la llamada — mismo resultado si el wrapper cubre ambos momentos; el UAT delegado confirma el comportamiento runtime antes de cerrar la guía |
| A2 | El paso del alumno "crear API key en Google AI Studio" usa la UI de `aistudio.google.com` (flujo "Get API key", sin tarjeta) | D-60 / Open Questions | PROJECT.md lo verificó en exploración previa (2026-09-28); la URL/pasos exactos de la UI pueden cambiar — la guía lo redacta resistente a cambios cosméticos |
| A3 | El endpoint público del asistente no requiere CORS nuevo en dev (el proxy `/api` de Vite ya cubre same-origin, como todos los endpoints existentes) | Architecture | Bajo: sigue el patrón de TODOS los endpoints actuales; CORS de producción es fase 5 |
| A4 | `gemini-flash-latest` es estable para free tier (los modelos Flash 3.x tienen "Sin costo" según la página de pricing; el alias apunta a la latest Flash) | Standard Stack | Si el alias apuntara algún día a un modelo sin free tier, el alumno vería 402/403 — la guía puede fijar `gemini-3.8-flash` como alternativa concreta verificada con free tier |
| A5 | React Router 8 anidado con `<Outlet>` funciona igual que v6 en modo declarativo (el repo ya usa `<Route element={...}>` con hijos en guia-06/08/11) | Pattern 5 | Bajo: el patrón con hijos ya está verificado runtime en maura-uat; solo el layout intermedio con Outlet es nuevo para el alumno |

## Open Questions (RESOLVED)

> Las tres preguntas quedaron resueltas por los planes de la fase 4 antes de la ejecución — resolución inline citando plan (convención de 01/02/03-RESEARCH). Ninguna exigió nuevo research: las tres son disposiciones que los planes ya adoptaron (OQ1 → happy path tras checkpoint del UAT delegado en 04-04; OQ2 → 429 sin cifras en 04-01/04-04; OQ3 → 409 en 04-01).

1. **¿De dónde sale la `GEMINI_API_KEY` para el UAT delegado (happy path)?**
   - What we know: `D:/Repos/maura-uat/backend/.env` NO tiene GEMINI hoy (verificado este session). D-60 hace de la key un paso DEL ALUMNO; el UAT delegado (AGENTS.md) corre como alumno.
   - What's unclear: si el agente debe crear su propia key (requiere cuenta Google en el browser automation) o el usuario provee una key de prueba.
   - Recommendation: el planner deja la fila de UAT del happy path tras un `checkpoint:human-verify` (el usuario entrega la key o autoriza crearla); la ruta de degradación (sin key → 503 + burbuja "no disponible") y el grep del build se verifican sin key y SIN depender del usuario.
   - Resolution: (RESOLVED) adoptada la Recommendation — el plan 04-04 deja el happy path del asistente (llamada real a Gemini en el UAT delegado) tras `checkpoint:human-verify`: no hay `GEMINI_API_KEY` en `maura-uat/backend/.env` y solo el usuario puede entregar la key o autorizar crearla (D-60 la hace paso del alumno); la ruta de degradación (sin key → 503 + burbuja "no disponible") y el grep del build (AIAS-03) se verifican SIN key y sin depender del usuario (truth AIAS-02 y nota UAT del verification de 04-04).
2. **Límites RPM/RPD del free tier (concern abierto heredado)**
   - What we know: verificado este session que la página oficial NO muestra números sin login (deriva a "View your active rate limits in AI Studio"); solo el usuario logueado puede verlos.
   - Recommendation: mantener la decisión de CONTEXT.md — la guía enseña el 429 sin cifras; si el usuario algún día reporta sus límites, se agregan como nota, no como promesa.
   - Resolution: (RESOLVED) adoptada la Recommendation — la fase mantiene el 429 SIN cifras: guia-14/guia-15 (plan 04-04) enseñan el manejo del error con copy amable sin números (concern abierto heredado de STATE.md: la página oficial no muestra límites sin login, verificado arriba), y el contrato 0.4.0 (04-01 Task 1) declara la fila 429 de la convención de errores sin cifras de límites; si el usuario algún día reporta sus límites, se agregan como nota, no como promesa.
3. **409 vs 422 para transición ilegal (discreción del planner)**
   - What we know: el contrato ya usa 409 para conflicto de negocio visible al usuario (email registrado) y 422 para schema; la transición ilegal es un conflicto de ESTADO del recurso, no un dato mal formado (el body `{estado}` es sintácticamente válido).
   - Recommendation: **409** con detail claro ("Ese pedido ya está pagado" / "Solo se puede anular un pedido en curso") — es también el estándar REST para state conflicts; documentarlo en la convención de errores del contrato 0.4.0.
   - Resolution: (RESOLVED) adoptada la Recommendation (409) — el contrato 0.4.0 (04-01 Task 1) declara el 409 para la transición ilegal en PATCH `/api/admin/pedidos/{numero}/estado` con el example detail locked "Ese pedido ya no está en curso." y la fila 409 de la convención de errores gana su segundo uso (conflicto de ESTADO del recurso, no un dato mal formado); ADR-016 (04-01 Task 2) registra la máquina de estados que lo produce (D-50).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js | Frontend del alumno (UAT) | ✓ | v24.21.0 (≥ 22.22 requerido) | — |
| uv | Backend del alumno (UAT) | ✓ | 0.9.3 | — |
| Python | Backend (UAT) | ✓ | 3.12.10 (baseline 3.12) | — |
| `D:/Repos/maura-uat` app hasta guia-11 | UAT delegado del panel | ✓ | backend/frontend presentes con órdenes reales de los 4 flujos de fase 3 | — |
| GEMINI_API_KEY | UAT happy path del asistente | ✗ (no está en maura-uat/backend/.env) | — | UAT de la ruta de degradación (503/burbuja) + grep del build sin key; happy path gated tras checkpoint (Open Question 1) |
| Red → pypi.org | instalación google-genai | ✓ (pip index respondió) | — | — |
| Red → generativelanguage.googleapis.com | llamada real Gemini en UAT | ¿? (no probado este session) | — | El UAT lo prueba en la primera corrida; wrapper amable cubre fallos de red por diseño (D-61) |

**Missing dependencies with no fallback:** ninguna que bloquee planeamiento — la única pieza externa pendiente (key para happy path) tiene fallback documentado y checkpoint.
**Missing dependencies with fallback:** GEMINI_API_KEY (arriba).

## Security Domain

> `security_enforcement: true`, ASVS nivel 1 (`.planning/config.json`). Fase docs-only: la superficie nueva de seguridad vive en el contrato, los ADRs y los bloques de código de las guías.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No (nuevo) | Sin cambios: JWT bearer existente (ADR-009); el asistente es público por diseño (D-59, espejo de `/api/pago/retorno`) |
| V3 Session Management | No (nuevo) | Token de 7 días existente; el chat no crea sesión de ningún tipo (D-58) |
| V4 Access Control | **Sí** | TODO path nuevo bajo `/api/admin/*` exige `get_current_admin` (403 a clienta — patrón guia-05:459); el panel SPA es solo UX (D-55); el asistente NO exige sesión (público deliberado, `security: []`) |
| V5 Input Validation | **Sí** | Pydantic en cada schema nuevo: `ProductoCrear/Editar` (familia en enum cerrado, precio entero ≥0, stock ≥0, largos), `PedidoTransicion` (estado en enum), `ChatMensaje` (largo máx mensaje e historial — RN nueva D-59) → 422 declarativo |
| V6 Cryptography | No (nuevo) | La key se almacena en `.env` (fuera de git desde guia-01) — gestión de secretos, no cripto nueva |
| V12 Communications | **Sí** (menor) | La key viaja solo backend→Google por HTTPS del SDK; jamás al cliente (AIAS-03, verificación grep del build) |

### Known Threat Patterns for {stack FastAPI + React + LLM}

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Prompt injection desde el mensaje del visitante (intenta cambiar las reglas del asistente) | Tampering / Elevation | Mini-RAG con instrucciones en system prompt + **validación de ids contra BD** (D-56): aunque el modelo "desobedezca", solo puede responder productos reales; el texto del modelo se renderiza como TEXTO en React (JSX escapa por defecto — jamás `dangerouslySetInnerHTML`) |
| Alucinación de ids/productos inexistentes | Tampering | Filtro server-side contra catálogo activo antes de responder (Pattern 6) |
| Fuga de la API key al bundle | Information Disclosure | Key SOLO en `.env` backend (D-60); nada de `VITE_` para Gemini; verificación grep `dist/` (AIAS-03) |
| Mass assignment en edición de productos (flipping campos no permitidos vía body) | Tampering | Schema Pydantic estricto con allow-list de campos editables (nombre, descripcion, precio, stock, familia, notas, imagen, activo según D-52); sin `model_dump` ciego sobre el ORM |
| IDOR en pedidos admin | Information Disclosure | No aplica igual: el admin ve TODOS por rol (`get_current_admin`); el endpoint de clienta mantiene su 404 uniforme de ownership (contrato 0.3.0:736-778, sin cambios) |
| Enumeración/abuso del endpoint público del chat (bots, payloads gigantes) | DoS / Abuse | Topes de largo mensaje/historial (422, RN nueva); costo por request acotado por catálogo pequeño; 429 del proveedor se traduce amable (D-61) |
| SQL injection en agregaciones de métricas | Tampering | SQLAlchemy ORM parametrizado (regla existente: repositories hacen SQL, sin strings concatenados) |

## Sources

### Primary (HIGH confidence)
- github.com/googleapis/python-genai — README @ tag `v2.25.0` (fetched 2026-09-30): env vars `GEMINI_API_KEY`/`GOOGLE_API_KEY` auto-pickup + precedencia; structured output `response_mime_type='application/json'` + `response_json_schema=CountryInfo.model_json_schema()` (sin `response_schema` en ese README); `errors.APIError` con `.code`/`.message`; `types.HttpOptions` sin timeout documentado; modelo de ejemplo `gemini-flash-latest`; Interactions presente sin `response_format`
- github.com/googleapis/python-genai — README @ main (fetched 2026-09-30): pin `< 3.0.0`, consistencia del patrón
- PyPI registry (`pip index versions google-genai`, este session): 2.25.0 es latest; 120+ versiones desde 0.0.1
- In-repo (Read este session): `contrato_api.yaml` 0.3.0 completo (líneas citadas por claim); `02_requerimientos.md` (series finales RF-18/RNF-07/RN-13/HU-11, filas P7/P8 §13:349-350); `03_diseno.md` (entidades, §2.3.5 activo, procesos 1.0-11.0, pantallas 1-9, decisiones 1-14); `guia-11` completo (formato 🧠/✅/📝, BADGES:81-86, Gran verificación 12 filas, Siguiente→fase 4); `guia-05` (get_current_admin:459, Settings:116-124, .env:96-99, lección responses:586); `guia-06` (RequireAuth returnTo:961, apiGet/apiPost:271-285); ADR-011 completo (formato ADR); ROADMAP §Phase 4; PROJECT.md; 01-UI-SPEC + 02-UI-SPEC (tokens, paleta @theme verbatim); READMEs (docs/, raíz, 05_desarrollo); 03-SPIKE-RETORNO.md (patrón expected/result/evidence)

### Secondary (MEDIUM confidence)
- ai.google.dev/gemini-api/docs/troubleshooting (fetched): 429/503/408 transitorios → backoff exponencial 1s/2s/4s/8s + jitter + máximo; 400/402/403 no reintentables; "the Python SDK automatically retries transient errors up to four times with an initial delay of approximately 1 second and a maximum delay of 60 seconds"
- ai.google.dev/gemini-api/docs/api-errors (fetched): tabla de códigos — 401 authentication (key faltante/inválida), 429 rate_limit_exceeded/quota_exceeded/too_many_requests, 503 service_unavailable, 504 deadline_exceeded (formato Interactions; el clásico generate_content usa RESOURCE_EXHAUSTED/UNAVAILABLE, cross-chequeado con troubleshooting)
- ai.google.dev/gemini-api/docs/models (fetched): `gemini-3.8-flash` estable actual; alias `-latest` hot-swap con 2 semanas de aviso
- ai.google.dev/gemini-api/docs/pricing (fetched): free tier incluye Flash 3.8/3.7/3.6/3.5 y Lite; 3.1 Pro Preview SIN free tier; "El contenido se usa para mejorar nuestros productos" (nota de privacidad del free tier que la guía puede mencionar)

### Tertiary (LOW confidence)
- Ninguna claim de este documento descansa SOLO en fuente terciaria. Las negativas verificadas con fetch (rate limits sin login, timeout ausente del README, `response_schema` ausente del README v2.25) están documentadas arriba con su fuente.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — google-genai 2.25.0 verificado contra PyPI + README del tag exacto del pin; el resto del stack ya estaba verificado en STACK.md y se re-validó su presencia in-repo
- Architecture: HIGH — toda la extensión se apoya en piezas leídas este session (contrato 0.3.0, ADR-011, guías 05/06/11, docs 02/03); structured output firmado con evidencia (D-56 cumplido)
- Pitfalls: HIGH — drift docs/SDK, error codes, rate limits y lecciones in-repo (responses OpenAPI, umbrales) verificados contra fuente primaria o lectura directa
- El seam `classify-confidence` taguea webfetch como LOW genérico; los claims externos de este research descansan en la cadena PyPI-registry + README-del-tag + docs-oficiales (mismo criterio de triple-verificación ya documentado en STACK.md §Sources)

**Research date:** 2026-09-30
**Valid until:** 2026-10-30 (stack backend estable; las páginas de modelos/pricing de Google se mueven rápido — re-verificar alias de modelo y free tier si la fase se ejecuta después de octubre)
