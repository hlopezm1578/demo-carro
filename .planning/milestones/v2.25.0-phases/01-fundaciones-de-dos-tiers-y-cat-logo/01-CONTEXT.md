# Phase 1: Fundaciones de dos tiers y catálogo - Context

**Gathered:** 2026-09-28
**Status:** Ready for planning

<domain>
## Phase Boundary

**CORRECCIÓN DE ALCANCE (2026-09-28, decisión del usuario): el repositorio contiene SOLO LAS GUÍAS — nunca código de aplicación.** El modelo es exactamente demo-cine: un repo docs-only donde el ciclo de vida se documenta y el código vive DENTRO de las guías de desarrollo como bloques que el alumno copia. Los "visitante ve/navega" de STORE-01..04 describen lo que el ALUMNO construye siguiendo la guía, no un artefacto de este repo.

La fase 1 entrega, como documentos: docs/README (índice del ciclo), 01_necesidad, 02_requerimientos, 03_diseno, 04_arquitectura (documento + ADRs fundacionales + contrato_api.yaml API-first) y 05_desarrollo (guías paso a paso que enseñan a levantar los dos tiers con el catálogo — esqueleto backend FastAPI en capas, esqueleto frontend React/TS, modelos y seed, landing/catálogo/ficha — con mini-verificaciones ✅ que corre el alumno). La verificación de los planes es por contenido documental (greps/estructura), jamás ejecutando código.

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
- Qué ADRs fundacionales se numeran exactamente y su redacción (candidatos naturales: stack, arquitectura en capas, SQLite, TypeScript, uv, monorepo, API-first, guide-only).
- Stock inicial por producto y valores exactos de precios dentro del rango fijado.
- Paleta Tailwind concreta bajo la dirección fresco-luminosa (ya formalizada en 01-UI-SPEC.md).
- Rutas de la SPA, prefijos de API y detalles de estructura de carpetas (seguir la investigación de arquitectura).

### Corrección de alcance (2026-09-28 — decisión del usuario, SUPERA lo anterior donde choquen)
- **D-17: El repositorio es GUIDE-ONLY.** Este repo contiene únicamente documentación de la guía (docs/ + .planning); jamás se commitea código de aplicación (sin backend/, sin frontend/, sin .venv, sin dependencias instaladas). El código de la tienda vive exclusivamente como bloques dentro de las guías de desarrollo (docs/05_desarrollo) que el alumno copia y ejecuta en su máquina — **Reversibility:** one-way — es el contrato del producto entero; cada fase y cada verificación se diseña alrededor de esto.
- **Reinterpretación de decisiones previas bajo D-17** (el texto original se mantiene como decisión de CONTENIDO de la guía, no de construcción en este repo):
  - D-08 (fotos): la GUÍA instruye al alumno descargar las 12 fotos a su `frontend/public/products/`; nada se commitea acá.
  - D-09/D-10/D-11/D-12 (TS, uv, monorepo, comandos agnósticos): describen lo que la guía ENSEÑA al alumno; el gate Node >=22.22 pasa a ser nota de prerrequisito en la guía, no un gate de ejecución del pipeline.
  - STORE-01..04 y los success criteria "visitante..." del ROADMAP: describen lo que el alumno logra siguiendo la guía; en los planes se verifican como cobertura documental de las guías (que la guía enseñe y haga verificar cada punto).
- **Verificación de planes:** por contenido documental (greps sobre docs/, estructura, conteos) — como ya lo hacían los planes de docs; nunca ejecutando la aplicación.
- **D-18: README.md en la raíz del repo, como demo-cine** (`D:/Repos/demo-cine/README.md` es el formato de referencia): portada del proyecto educativo — qué es (recorrido documentado del ciclo de vida), la aplicación (Maura · Body Splash, PYME ficticia), el enfoque fase-a-fase con tabla de las 8 fases y estado, qué hace especial al material (ADRs honestos, API-first, guías senior→junior), stack y la frase clave "el código completo vive narrado en las guías", uso en clases y nota de ficción. Debe crear/actualizar la tabla de estado conforme avanza el ciclo.

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
- Ninguno de código — **el repo es guide-only (D-17)**: solo documentación (docs/, .planning/, AGENTS.md).
- Ya entregado en esta fase: docs/README.md + 01_necesidad + 02_requerimientos + 03_diseno (plan 01-02, commits 0ba8eed..ab20e70) y docs/04_arquitectura/contrato_api.yaml (plan 01-01 Task 1, commit 1dc84d7).

### Established Patterns
- Formato demo-cine verificado (docs/README con tabla de fases y regla del proyecto; numeración trazable P/C/CS → RF/RNF/RN/HU → diseño → contrato → guías; guías con 🧠/✅/📝 por paso).
- Trazabilidad numerada del ciclo ya fijada por 01-02: D1-D6 / P1-P8 / C1-C4 / CS1-CS5 / RF-01..05 / RNF-01..04 / RN-01..04 / HU-01..04 — los ADRs y guías DEBEN citar estos IDs.
- 12 SKU canónicos fijados (nombres, precios $6.990–$12.990, notas, stocks) — docs y guías citan siempre los mismos valores.

### Integration Points
- Los ADRs (04_arquitectura/adr/) citan RF/RN de 02_requerimientos y decisiones D de este CONTEXT.
- Las guías (05_desarrollo) citan el contrato_api.yaml y el diseño de 03_diseno; contienen el código como bloques con mini-verificaciones ✅ del alumno.

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
