# Phase 1: Fundaciones de dos tiers y catálogo - Context

**Gathered:** 2026-09-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Un visitante navega una tienda de dos tiers operativa: SPA React (TypeScript) que consume API FastAPI en capas (routers → services → repositories), sin plantillas en el servidor. La fase entrega landing con identidad de marca de la PYME ficticia, catálogo filtrable por familia aromática y rango de precio, páginas de producto y seed idempotente con datos demo. Además establece las convenciones documentales de la guía (ADRs, contrato de API API-first, guías paso a paso) que las fases siguientes mantienen.

</domain>

<decisions>
## Implementation Decisions

### Identidad de la PYME ficticia
- **D-01:** La tienda ficticia se llama **Maura** — marca eponima de la dueña, presentación "Maura · Body Splash", estilo emprendimiento chileno real — **Reversibility:** costly — el nombre impregna docs del ciclo, copy de landing, tagline y narrativa de la guía; cambiarlo después reescribe todos los documentos y pantallas.
- **D-02:** La dueña Maura tiene **persona breve**: 2-3 frases fijadas en la guía (quién es, qué vende, por qué necesita la tienda online). Suficiente para la narrativa de necesidad del cliente y para la voz de la asesora IA de la fase 4.
- **D-03:** Dirección visual de la marca: **fresco y luminoso** — pasteles cítricos, mucho blanco, tipografía redondeada. El contrato de UI (`/gsd:ui-phase`) formaliza la paleta Tailwind concreta sobre esta dirección.
- **D-04:** Tagline del hero de la landing: **"Frescura que te acompaña"**.

### Catálogo demo y seed
- **D-05:** El catálogo se organiza en **4 familias aromáticas: Cítricas, Florales, Frutales y Dulces** (gourmand) — **Reversibility:** costly — la familia es campo del modelo de datos, eje de los filtros del catálogo y categoría narrativa de los docs; cambiarla después migra schema y reescribe guías.
- **D-06:** El seed contiene **12 SKU** (4 familias × 3 productos).
- **D-07:** Rango de precios: **$6.990–$12.990 CLP** (realista del body splash chileno de perfumería masiva).
- **D-08:** Imágenes de producto: **fotos stock reales (Unsplash/Pexels, licencia libre) descargadas al repo** en `frontend/public/products/`; el seed referencia rutas locales (`/products/*.jpg`). La guía incluye el paso de descarga — nada de hotlinks externos.

### Toolchain del alumno
- **D-09:** El frontend va en **TypeScript** (template `react-ts` de Vite). Las interfaces TS espejan los schemas Pydantic — el contrato dos-tiers queda tipado de punta a punta — **Reversibility:** costly — migrar TS→JS después reescribe todo el frontend y las guías de las 5 fases.
- **D-10:** El backend se maneja con **uv** (`uv add` / `uv run fastapi dev`, pyproject + lock), igual que enseña la documentación oficial de FastAPI.
- **D-11:** El proyecto vive en un **monorepo** `backend/` + `frontend/` (estructura propuesta en la investigación de arquitectura) — **Reversibility:** costly — dividir el repo después rompe todas las rutas y comandos de las guías.
- **D-12:** Comandos de la guía **agnósticos de terminal**: todo vía npm scripts y `uv run`, sin sintaxis exclusiva de bash. Debe funcionar igual en PowerShell, cmd y Git Bash.

### Convenciones de la guía
- **D-13:** `docs/` **replica la estructura de demo-cine**: `01_necesidad_del_cliente.md` … `08_mantenimiento.md`, con `04_arquitectura/` (documento + `adr/` + `contrato_api.yaml`) y `05_desarrollo/` (guías numeradas). La diferencia con demo-cine: los documentos se escriben por fase GSD conforme la app se construye — **Reversibility:** costly — reestructurar docs después reescribe la trazabilidad del ciclo completo.
- **D-14:** La fase 1 escribe **todo lo fundacional del ciclo**: `01_necesidad` (Maura), `02_requerimientos` (los cubiertos por la fase), `03_diseno` (modelo de datos de producto + pantallas del catálogo), `04_arquitectura` (ADRs fundacionales + contrato API inicial) y las primeras guías de `05_desarrollo`.
- **D-15:** Contrato de API **YAML API-first manual** (`docs/04_arquitectura/contrato_api.yaml`): se escribe ANTES del código y FastAPI lo implementa — metodología demo-cine, punto pedagógico de diseño por contrato.
- **D-16:** Las guías de desarrollo se parten en **sub-guías numeradas por hito** dentro de cada fase (en la fase 1, del orden: proyecto backend, proyecto frontend, modelos y seed, catálogo).

### Claude's Discretion
- Nombres concretos, notas aromáticas y descripciones de los 12 productos (dentro de las 4 familias fijadas).
- Selección concreta de las fotos stock (criterio: consistencia visual entre productos de una misma familia).
- Qué ADRs fundacionales se numeran exactamente y su redacción (candidatos naturales: stack, arquitectura en capas, SQLite, TypeScript, uv, monorepo, API-first).
- Stock inicial por producto y valores exactos de precios dentro del rango fijado.
- Paleta Tailwind concreta bajo la dirección fresco-luminosa (la formaliza `/gsd:ui-phase`).
- Rutas de la SPA, prefijos de API y detalles de estructura de carpetas (seguir la investigación de arquitectura).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Planificación del proyecto
- `.planning/PROJECT.md` — Contexto, constraints y decisiones clave del proyecto (stack, Webpay sandbox, Gemini).
- `.planning/REQUIREMENTS.md` — Requisitos v1; la fase 1 cubre GUIDE-02, GUIDE-03, STORE-01..04 (ver Traceability).
- `.planning/ROADMAP.md` §Phase 1 — Goal, success criteria y límites de la fase.

### Investigación previa
- `.planning/research/STACK.md` — Stack versionado completo (React 19 + Vite 8 + TS ~6.0 + Tailwind 4; FastAPI 0.141 + SQLAlchemy 2.1 + SQLite + Alembic; variantes y "what NOT to use").
- `.planning/research/ARCHITECTURE.md` — Estructura recomendada del monorepo (backend/app en capas + frontend/src con features/), patterns y data model borrador (`products` necesita agregar familia aromática y notas — ver specifics).

### Formato de la guía (referencia externa)
- `D:/Repos/demo-cine/docs/` — **Referencia de formato obligatoria para replicar**: `README.md` (tabla de fases con estados y regla del proyecto), `01_necesidad_del_cliente.md` … `08_mantenimiento.md`, `04_arquitectura/adr/` + `contrato_api.yaml`, `05_desarrollo/guia-01..08`. Es un repo hermano fuera de demo-carro; leer para imitar estructura, tono y convenciones de trazabilidad.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Ninguno — repo greenfield (solo documentación de planificación). Todo el código de la fase es nuevo.

### Established Patterns
- Backend en capas routers → services → repositories con DI de FastAPI (objetivo pedagógico declarado; ver `.planning/research/ARCHITECTURE.md`).
- Frontend organizado por `features/` (catalog, cart, …) con `lib/api` como único punto de salida HTTP.
- Monorepo `backend/` + `frontend/` confirmado como estructura de la guía.

### Integration Points
- Esta fase crea los puntos de integración que las demás fases consumen: contrato API inicial (`contrato_api.yaml`), health check + CORS del backend, API client del frontend, seed idempotente y tabla `products`.

</code_context>

<specifics>
## Specific Ideas

- Presentación de marca: "Maura · Body Splash"; tagline del hero: "Frescura que te acompaña".
- El modelo de datos borrador de la investigación (`products(id, sku, name, description, price, stock, active, image_url)`) debe extenderse para esta fase: campo **familia aromática** y **notas** (la página de producto muestra ambos, STORE-03).
- docs/README.md de demo-cine usa tabla de fases con estado (✅ Listo) y la regla "ninguna fase se escribe sin aprobar la anterior" — replicar esa mecánica de trazabilidad.
- Guías de demo-cine se llaman `guia-01-*.md` … con razonamiento y código — mantener el patrón de guías cortas verificables entre hitos.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 1-Fundaciones de dos tiers y catálogo*
*Context gathered: 2026-09-28*
