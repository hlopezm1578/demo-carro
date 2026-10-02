# Phase 1: Fundaciones de dos tiers y catálogo - Pattern Map

**Mapped:** 2026-09-28
**Files analyzed:** 31 (archivos/grupos nuevos a crear; el repo no tiene archivos que modificar)
**Analogs found:** 9 / 31 con análogo de formato exacto (docs, repo hermano demo-cine) · 22 / 31 sin análogo de código (greenfield → usar patrones verificados de `01-RESEARCH.md`)

## Nota de alcance: repo greenfield (leer primero)

`D:/Repos/demo-carro` **no contiene código de aplicación**: `git ls-files` lista 41 archivos, todos en `.planning/` más `AGENTS.md` y `.gitignore` [VERIFICADO esta sesión]. Por lo tanto:

1. **Los 9 artefactos de `docs/`** tienen análogo de FORMATO exacto y obligatorio (D-13): el repo hermano `D:/Repos/demo-cine/docs/`. Todos sus archivos están trackeados en el repo `D:/Repos/demo-cine` (`git ls-files docs/` ejecutado dentro de ese repo los lista completos) — no son mirrors ni rutas gitignored. Es referencia de formato/tono/estructura, **no** de decisiones técnicas (demo-cine es SSR Jinja2 monolito; ver "Divergencias" en Shared Patterns).
2. **Los 22 archivos de código** (backend + frontend) no tienen análogo dentro de este repo ni en demo-cine (que tampoco tiene código SPA/TS). Su fuente de patrones es `01-RESEARCH.md` (Patterns 1–6 con código listo, verificado contra registros/docs oficiales) y `.planning/research/ARCHITECTURE.md` (estructura y reglas de dependencia). Donde 01-RESEARCH.md y ARCHITECTURE.md difieren (naming, modo de router), **manda 01-RESEARCH.md** (más reciente y específico para esta fase).
3. **Gate bloqueante antes del scaffold frontend:** Node instalado es v22.18.0 y `react-router@8.4.0` exige `>=22.22.0` (01-RESEARCH.md, Pitfall 1). El plan debe abrir con upgrade de Node + `node -v` verificado. *(Actualización replan D-17: este repo no ejecuta scaffold — el gate vive como prerrequisito en prosa en el paso 1 de guia-02, plan 01-04; no es checkpoint del pipeline.)*

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `docs/README.md` | doc index | — | `D:/Repos/demo-cine/docs/README.md` | exact (formato) |
| `docs/01_necesidad_del_cliente.md` | doc (fase 1 ciclo) | — | `D:/Repos/demo-cine/docs/01_necesidad_del_cliente.md` | exact (formato) |
| `docs/02_requerimientos.md` | doc (fase 2 ciclo) | — | `D:/Repos/demo-cine/docs/02_requerimientos.md` | exact (formato) |
| `docs/03_diseno.md` | doc (fase 3 ciclo) | — | `D:/Repos/demo-cine/docs/03_diseno.md` | exact (formato) |
| `docs/04_arquitectura/README.md` | doc (fase 4 ciclo) | — | `D:/Repos/demo-cine/docs/04_arquitectura/README.md` | exact (formato; contenido diverge: 2 tiers vs 3 capas SSR) |
| `docs/04_arquitectura/adr/001..008-*.md` (8 ADRs — replan D-17 agrega 008 guide-only; supera la cuenta original de 7) | doc (decisión) | — | `D:/Repos/demo-cine/docs/04_arquitectura/adr/001-arquitectura-en-capas.md` + `adr/008-api-first.md` | exact (formato) |
| `docs/04_arquitectura/contrato_api.yaml` | contract (OpenAPI) | request-response | `D:/Repos/demo-cine/docs/04_arquitectura/contrato_api.yaml` | exact (formato) |
| `docs/05_desarrollo/README.md` | doc index | — | `D:/Repos/demo-cine/docs/05_desarrollo/README.md` | exact (formato) |
| `docs/05_desarrollo/guia-01..04-*.md` (4 guías) | doc (guía paso a paso) | — | `D:/Repos/demo-cine/docs/05_desarrollo/guia-01-esqueleto.md` (+ `guia-08-datos-iniciales.md` para seed) | exact (formato) |
| `backend/pyproject.toml` (+ `.python-version`, `.gitignore`) | config | — | ninguno (lo genera `uv init --vcs none`; ajustes en Pitfall 2/3) | none (greenfield, tool-generated) |
| `backend/app/__init__.py` | package marker | — | ninguno | none (greenfield) |
| `backend/app/main.py` | entry / composición | request-response | conceptual: demo-cine `guia-01` Paso 4 (patrón "main compone, no piensa"); código: 01-RESEARCH.md Pattern 4 (CORS) | none in-repo (patrón doc) |
| `backend/app/config.py` | config (Settings) | — | conceptual: demo-cine `guia-01` Paso 3 (env vars); código: 01-RESEARCH.md estructura (pydantic-settings) | none in-repo (patrón doc) |
| `backend/app/database.py` | utility / infra DB | CRUD | 01-RESEARCH.md estructura + ARCHITECTURE.md Pattern 1 (get_session) | none (greenfield) |
| `backend/app/models/producto.py` | model | CRUD | 01-RESEARCH.md Pattern 2 (líneas 300-313, código completo) | none (greenfield) |
| `backend/app/schemas/producto.py` | schema (contrato Pydantic) | transform | 01-RESEARCH.md Pattern 1 (response_model) + contrato demo-cine schemas | none (greenfield) |
| `backend/app/repositories/producto.py` | repository | CRUD (read + filtros) | ARCHITECTURE.md Pattern 1 (líneas 116-133, DI de sesión) | none (greenfield) |
| `backend/app/services/catalogo.py` | service | request-response | 01-RESEARCH.md Pattern 1 (líneas 269-282) | none (greenfield) |
| `backend/app/routers/productos.py` | route (controller) | request-response | 01-RESEARCH.md Pattern 1 (líneas 272-281, código completo) | none (greenfield) |
| `backend/app/routers/salud.py` | route | request-response | conceptual: demo-cine `guia-01` Paso 4 (`/salud` desde día 1); contrato demo-cine path `/salud` | none (greenfield) |
| `backend/app/seed.py` | script batch (seed) | batch / CRUD upsert | conceptual: demo-cine `guia-08` Paso 2 (semilla.py idempotente); código: 01-RESEARCH.md Pattern 5 (upsert por SKU) | none in-repo (patrón doc) |
| `frontend/` (scaffold react-ts) | scaffold | — | ninguno (lo genera `npm create vite@latest -- --template react-ts`) | none (tool-generated) |
| `frontend/vite.config.ts` | config (build) | — | 01-RESEARCH.md Pattern 4 (líneas 377-390, código completo) | none (greenfield) |
| `frontend/src/main.tsx` | entry / providers | request-response | 01-RESEARCH.md Pattern 3 (líneas 350-371, código completo) | none (greenfield) |
| `frontend/src/index.css` | config (estilos) | — | 01-RESEARCH.md estructura (línea 253: `@import "tailwindcss";`) | none (greenfield) |
| `frontend/src/lib/api.ts` | utility (API client) | request-response | ARCHITECTURE.md "lib/api único punto HTTP" (líneas 56, 91-92, 106) | none (greenfield) |
| `frontend/src/types/api.ts` | types (espejo contrato) | transform | 01-RESEARCH.md Pattern 3 (líneas 321-346, código completo) | none (greenfield) |
| `frontend/src/features/landing/` | component | static render | ninguno (direction visual D-03 la formaliza `/gsd:ui-phase`) | none (greenfield) |
| `frontend/src/features/catalogo/` (grilla, ProductCard, filtros, ficha) | component | request-response (+ estado en URL) | 01-RESEARCH.md Code Example filtros (líneas 564-579) | none (greenfield) |
| `frontend/src/components/` (Navbar, Footer, layout) | component | static render | ninguno | none (greenfield) |
| `frontend/public/products/*.jpg` (12 fotos) | static assets | file-I/O (descarga manual) | ninguno (selección en ejecución, A12 de RESEARCH) | none |

## Pattern Assignments

### Grupo A — Documentación del ciclo (replica formato demo-cine, D-13/D-14)

> Regla transversal del grupo: se copia **estructura, tono y mecánica de trazabilidad** de demo-cine; el contenido es de Maura (D-01..D-08). Demo-cine usa SSR Jinja2 monolito — sus decisiones técnicas NO se copian (ver Divergencias al final).

#### `docs/README.md`

**Analog:** `D:/Repos/demo-cine/docs/README.md` (22 líneas, copiar estructura completa)

**Formato** (líneas 9-22): tabla de 8 fases del ciclo con columnas `# | Fase | Documento | Estado` + regla del proyecto en negrita:

```markdown
| # | Fase del ciclo de vida | Documento | Estado |
|---|---|---|---|
| 1 | Necesidad del cliente | `01_necesidad_del_cliente.md` | ✅ Listo |
...
**Regla del proyecto:** ninguna fase se escribe sin aprobar la anterior.
```

**Ajuste Maura:** el Estado avanza POR FASE GSD (D-13): en fase 1 quedan filas 1–4 ✅, fila 5 parcial (solo guías 1–4), filas 6–8 pendientes. Header (líneas 3-7): módulos/producto/método — cambiar "Cartelera" por "Maura · Body Splash".

---

#### `docs/01_necesidad_del_cliente.md`

**Analog:** `D:/Repos/demo-cine/docs/01_necesidad_del_cliente.md` (107 líneas)

**Secciones a replicar** (con líneas del análogo):
- Header con regla de fase (líneas 1-7): "el documento habla el idioma del CLIENTE. Cero tecnología" — mantener textual.
- §1 El cliente → Maura y su persona breve (D-02: 2-3 frases fijadas).
- §2 Situación actual (bullets concretos: hoy vende por Instagram/WhatsApp, catálogo en fotos del celular — redacción a discreción dentro del contexto PYME chilena).
- §3 Dolores en tabla `# | Dolor | Consecuencia` (líneas 33-38).
- §4 Cita textual del cliente + tabla de peticiones **P1..Pn** (líneas 40-55) — solo las que la fase 1/ciclo completo cubre (catálogo, tienda online).
- §5 Objetivos O1..On · §6 Lo que NO pide (gestión de expectativas) · §7 Condiciones C1..Cn (presupuesto, sola, móvil) (líneas 57-80).
- §8 Criterios de éxito **CS1..CSn** con columna "Cómo se verifica" (líneas 82-89).
- §9 Aprobación con firmas (líneas 91-99) + nota final de trazabilidad P/CS → fase 2 (líneas 101-107).

---

#### `docs/02_requerimientos.md`

**Analog:** `D:/Repos/demo-cine/docs/02_requerimientos.md` (225 líneas)

**Secciones a replicar:**
- Header "Insumo obligatorio: 01_necesidad" (líneas 1-8) — cada RF/RNF/RN **nace de una P, C o CS**.
- §2 Alcance dentro/fuera citando secciones del doc 01 (líneas 19-34).
- §3 Actores y roles con columna Origen (líneas 37-43) — fase 1: solo Visitante (las cuentas llegan en fase 2).
- §4 RF agrupados por tema con "(soportan P.., C..)" (líneas 47-63). Fase 1: STORE-01..04 del `.planning/REQUIREMENTS.md`.
- §5 RNF en tabla `Código | Categoría | Descripción | Origen` (líneas 67-77).
- §6 Reglas de negocio RN-01..n con cita de origen en cursiva (líneas 81-87) — candidatas: familia ∈ 4 slugs, precio entero CLP, slugs ASCII en API (Pitfall 5).
- §7 Historias de usuario Gherkin **Dado/Cuando/Entonces** (líneas 91-140).
- §8 Modelo de datos preliminar (insumo doc 03) (líneas 143-153).
- §13 Tabla de trazabilidad `Necesidad → Se convierte en → Se verifica con` (líneas 192-209) — **ninguna petición sin requerimiento, ningún requerimiento sin origen**.
- §14 Aprobación con firmas (líneas 213-218).

---

#### `docs/03_diseno.md`

**Analog:** `D:/Repos/demo-cine/docs/03_diseno.md` (352 líneas)

**Secciones a replicar:**
- Header: "se diseña QUÉ... aún sin elegir tecnología" (líneas 1-9) + nota Mermaid (línea 9).
- §1 Tabla "Qué diseña este documento" (líneas 13-20).
- §2.1 Diagrama ER en `mermaid erDiagram` (líneas 25-56) — fase 1: una sola entidad PRODUCTO extendida (familia Enum + notas JSON, ver specifics CONTEXT).
- §2.2 Diccionario de datos por entidad: tabla `Atributo | Tipo | Longitud | Obligatorio | Restricción/origen` (líneas 60-94). Campos desde 01-RESEARCH.md Pattern 2: id, sku (único), nombre, descripcion, precio (Integer CLP), stock, familia (enum 4 slugs), notas (JSON list), activo, imagen.
- §2.3 "Decisiones de diseño de datos (y por qué)" numeradas (líneas 96-105) — aquí van: precio entero sin decimales (A4), slugs ASCII (A2), notas como list JSON (A3), imagen = ruta no blob (hereda decisión demo-cine línea 100).
- §3 Diagrama de contexto + DFDs por proceso en mermaid (líneas 109-190) — fase 1: explorar catálogo / ver ficha / filtrar.
- §4 Pantallas: lineamientos + wireframes ASCII por pantalla con "Origen: RF/HU · Estados:" (líneas 194-320) — 3 pantallas: landing (STORE-01), grilla con filtros (STORE-02), ficha producto (STORE-03). Dirección visual fresco-luminosa D-03 (no copiar el tema oscuro de demo-cine línea 198).
- §5 Trazabilidad requerimiento → diseño (líneas 324-341) + §6 Aprobación (líneas 345-351).

---

#### `docs/04_arquitectura/README.md`

**Analog:** `D:/Repos/demo-cine/docs/04_arquitectura/README.md` (152 líneas)

**Secciones a replicar (formato), contenido nuevo (dos tiers):**
- §1 "La arquitectura en una página": diagrama ASCII + tabla de 3 preguntas + regla de oro + "Pregunta inevitable del jurado" (líneas 11-41) — para Maura: **SPA React + API FastAPI en capas, dos tiers estrictos** (el diagrama del System Architecture de 01-RESEARCH.md líneas 170-210 ya es el borrador).
- §2 "Del diseño a la arquitectura" tabla elemento a elemento (líneas 45-56).
- §3 Stack con porqué, tabla `Pieza | Elección | Por qué` citando ADRs (líneas 60-71) — stack autoritativo: sección Technology Stack de `AGENTS.md` / `.planning/research/STACK.md` (React 19.3, Vite 8.3.1, TS ~6.0.2, RR 8.4.0, TanStack Query 5.104, Tailwind 4.3.3, FastAPI 0.141.1, SQLAlchemy 2.1.1, pydantic-settings, SQLite, Python 3.12, Node >=22.22).
- §4 Organización del código: árbol de carpetas + **reglas de dependencia numeradas verificables** (líneas 75-96) — adaptar a la estructura de 01-RESEARCH.md líneas 233-260 (backend/app con models/schemas/repositories/services/routers; frontend/src con features/ + lib/api.ts como único punto HTTP).
- §6 Índice de ADRs `ADR | Decisión | Resuelto por` (líneas 118-129).
- §7 API-first con el flujo `contrato → código → /docs ≈ contrato` (líneas 133-141).
- §8 Aprobación (líneas 145-152).

---

#### `docs/04_arquitectura/adr/001..008-*.md` (8 ADRs fundacionales — replan D-17 supera la cuenta original de 7)

**Analog:** `D:/Repos/demo-cine/docs/04_arquitectura/adr/001-arquitectura-en-capas.md` (47 líneas, formato completo) y `adr/008-api-first.md` (43 líneas)

**Formato obligatorio** (ADR-001 líneas 1-47): título `ADR-00N — Decisión` + metadatos → secciones fijas:

```markdown
- **Estado:** Aceptada
- **Fecha:** 2026-09-__ (fecha de la fase)
- **Resuelve:** [pregunta de decisión]

## Contexto
## Opciones consideradas   → tabla | Opción | A favor | En contra | (3 opciones A/B/C)
## Decisión                → "Opción X" + regla explícita
## Consecuencias           → **Positivas** / **Negativas (honestas)**
## Para conversar en clase → 3 preguntas numeradas
```

**Numeración sugerida** (discretion, Open Question 2 de RESEARCH): 001 capas routers→services→repositories (adaptar ADR-001 demo-cine, cambia "rutas HTML" por "SPA consume API"), 002 dos tiers SPA+API (análogo inverso del ADR-006 SSR-vs-SPA de demo-cine — Maura elige la opción que Cartelera rechazó, buen contraste pedagógico), 003 monorepo, 004 TypeScript (D-09), 005 SQLite+create_all (documentar Pitfall 8: Alembic diferido), 006 uv (D-10), 007 API-first (adaptar `adr/008-api-first.md` casi textual: misma lógica, cita contrato_api.yaml, líneas 19-26 con el mecanismo de drift /docs vs contrato). Replan D-17: se agrega **ADR-008 repositorio-solo-guias** (guide-only, D-17/D-18; lo escribe 01-03 Task 3) — 8 en total.

---

#### `docs/04_arquitectura/contrato_api.yaml`

**Analog:** `D:/Repos/demo-cine/docs/04_arquitectura/contrato_api.yaml` (400 líneas, formato OpenAPI 3.0.3)

**Esqueleto a replicar** — el Code Example de 01-RESEARCH.md (líneas 503-562) ya lo trae adaptado a Maura. Del análogo demo-cine copiar:
- Header comentario de regencia (líneas 1-8): "FUENTE DE LA VERDAD... Se aprueba antes de codificar... Trazabilidad: cada operación cita el RF/RN".
- `info.description` con tabla de **convención de errores** 400/401/403/404/409/422 (líneas 21-29) — fase 1 usa 200/404/422.
- `servers` dev/prod (líneas 31-35).
- `tags` con cita de origen P/C (líneas 37-45).
- `components.schemas`: `Error` (líneas 64-70), **Resumen** con required + example por campo (líneas 72-98), **Detalle con `allOf`** (líneas 100-115) — para Maura: `ProductoResumen` (id, sku, nombre, precio, familia, imagen) y `ProductoDetalle` (allOf Resumen + descripcion, notas[], stock).
- Paths con `description` citando RF (líneas 217-270): `/api/salud`, `/api/productos` (query params familia enum + precio_min/max), `/api/productos/{producto_id}` con 404.

**Se escribe ANTES del código backend** (D-15) — es el primer entregable del frente A de la fase.

---

#### `docs/05_desarrollo/README.md`

**Analog:** `D:/Repos/demo-cine/docs/05_desarrollo/README.md` (21 líneas)

**Formato** (líneas 1-21): blockquote "cómo funcionan estas guías" + **Reglas del alumno** numeradas (1. no saltear ✅ Verificaciones, 2. leer 🧠 antes de copiar, 3. el error es información) + tabla `# | Guía | Construye | Estado` + "Mapa mental de la serie" (de adentro hacia afuera).

**Ajuste Maura:** 4 guías en fase 1 (D-16): guia-01 proyecto backend, guia-02 proyecto frontend, guia-03 modelos y seed, guia-04 catálogo. El README crece por fase igual que docs/README.md.

---

#### `docs/05_desarrollo/guia-01..04-*.md` (4 guías)

**Analog:** `D:/Repos/demo-cine/docs/05_desarrollo/guia-01-esqueleto.md` (247 líneas) para guias 01/02/04; `guia-08-datos-iniciales.md` (210 líneas) para la guía de seed

**Estructura obligatoria por guía** (guia-01 demo-cine):
1. Header blockquote: `Qué construirás hoy / Al terminar tendrás / Necesitas` (líneas 3-5).
2. "Los términos de hoy" — tabla término/frase (líneas 9-18).
3. Pasos numerados `## Paso N — título` donde cada paso tiene: bloque **🧠 El desarrollador piensa** en cursiva con el porqué citando ADR/RN (línea 23 es el patrón exacto), código en bloque con nombre de archivo en negrita, y **✅ Mini-verificación** accionable (línea 87).
4. `❌ El error que este archivo evita` contrapuesto ❌/✅ cuando aplique (líneas 147-157).
5. Cierre: `✅ Verificación de la guía` con URLs concretas a abrir (líneas 213-228), `📝 Punto de control` preguntas sin mirar la guía (líneas 232-237), `Lo que acabas de aprender` bullets + "**Siguiente:**" (líneas 239-247).

**Patrón seed** (guía-08 demo-cine, Paso 2, líneas 21-111): `semilla.py` idempotente con guardas `if` e impresiones `[+]`/`[=]` (líneas 84-106) + docstring con uso y variables de entorno. Para Maura: evolucionar a **upsert por SKU** (01-RESEARCH.md Pattern 5, líneas 409-417) y comando `uv run python -m app.seed`. La "gran verificación final" con tabla de chequeo numerada citando origen (guia-08 líneas 169-184) — la fila "comparación contrato ↔ /docs" (línea 182) es el mecanismo de cierre de ADR-008 que la guía 04 de Maura debe incluir.

**Ajustes de contenido:** comandos uv (`uv init --vcs none`, `uv add`, `uv run fastapi dev`) — NO pip/venv/requirements.txt de demo-cine (D-10); comandos agnósticos de terminal D-12 (una sola forma por comando, sin bloques bash/powershell separados como hace demo-cine en guia-01 líneas 27-42).

---

### Grupo B — Backend FastAPI (greenfield; patrones verificados de 01-RESEARCH.md)

> Sin código previo en ningún repo del ecosistema. Los excerpts abajo provienen de `01-RESEARCH.md` (verificados contra registros y docs oficiales 2026-09-28). El planner copia de ahí; el código vive además dentro de las guías 05_desarrollo (el alumno lo escribe siguiéndolas).

#### `backend/pyproject.toml` (+ `.python-version`, `.gitignore`)

**Generado por:** `uv init backend --vcs none --app` (01-RESEARCH.md Installation, líneas 137-141).
**Ajustes manuales obligatorios:** (1) `--vcs none` evita el `.git` anidado (Pitfall 2, verificado por ejecución); (2) editar `requires-python = ">=3.12,<3.13"` — uv genera `>=3.12` que permitiría 3.13/3.14 fuera del techo de transbank-sdk (Pitfall 3); (3) borrar el `main.py` hello-world que genera; (4) `.python-version` = 3.12.
**Dependencias:** `uv add "fastapi[standard]" sqlalchemy pydantic-settings`.

#### `backend/app/main.py` (entry, composición)

**Patrón conceptual:** demo-cine guia-01 Paso 4 — "`main.py` no tiene lógica de negocio: decide QUÉ existe y EN QUÉ orden" + health endpoint desde día 1.
**Código de referencia:** 01-RESEARCH.md Pattern 4 (líneas 393-400):

```python
# app/main.py — CORS con orígenes explícitos desde settings (nunca ["*"] con credentials)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,      # ["http://localhost:5173", "<prod>"]
    allow_methods=["GET"],
    allow_headers=["*"],
)
```

**Composición:** `FastAPI(title="Maura API", ...)` + CORSMiddleware + `include_router(..., prefix="/api")` (estructura 01-RESEARCH.md línea 239). Nadie más que main.py arma la app (regla demo-cine 04_arquitectura §4 regla 4).

#### `backend/app/config.py` (config, pydantic-settings)

**Patrón conceptual:** demo-cine guia-01 Paso 3 — "TODO lo configurable, en un solo lugar", env vars con defaults de desarrollo, con el bloque ❌/✅ del secreto pegado (líneas 147-157).
**Implementación Maura:** clase `Settings(pydantic_settings.BaseSettings)` con `database_url` y `cors_origins` (01-RESEARCH.md línea 240; stack: pydantic-settings 2.15.0). NO copiar el `os.getenv` plano de demo-cine.

#### `backend/app/database.py` (infra DB)

**Patrón:** ARCHITECTURE.md Pattern 1 (líneas 116-123) — sesión por request:

```python
# Source: .planning/research/ARCHITECTURE.md lines 117-123
def get_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Contiene: `engine` (SQLite vía `settings.database_url`), `SessionLocal`, `Base` (Declarative), `get_session` (Depends). En fase 1 la creación de tablas es `Base.metadata.create_all` (decisión A8/Pitfall 8 — documentarla en ADR-005).

#### `backend/app/models/producto.py` (model, SQLAlchemy)

**Código de referencia:** 01-RESEARCH.md Pattern 2 (líneas 293-313, completo) — dos piezas:
1. Enum con **nombre de miembro == slug** (Pitfall 4: SQLAlchemy persiste member names, no valores):

```python
# Source: 01-RESEARCH.md lines 294-298
class FamiliaAromatica(str, enum.Enum):
    citricas = "citricas"    # nombre == valor: la BD guarda "citricas",
    florales = "florales"    # la API devuelve "citricas", sin values_callable
    frutales = "frutales"
    dulces = "dulces"
```

2. `Producto(Base)` con `Mapped[]`/`mapped_column`: precio `Integer` CLP (nunca float, A4), `notas` columna `JSON` con `default=list` (A3), `familia` columna `Enum(FamiliaAromatica)`, `sku` único e indexado, `imagen` guarda ruta local `/products/{sku}.jpg` (D-08).

#### `backend/app/schemas/producto.py` (schemas Pydantic = contrato)

**Fuentes:** el contrato YAML define los schemas (API-first D-15); Pydantic los implementa. Nombres en español espejo del contrato: `ProductoResumen` / `ProductoDetalle` (01-RESEARCH.md líneas 322-338 traen la forma exacta de los campos, que es también la de las interfaces TS de Pattern 3). Query params validados: `familia: FamiliaAromatica | None`, `precio_min/max: int | None = Query(default=None, ge=0)` (Pattern 1, líneas 274-276). Regla: schemas/ separado de models/ (ARCHITECTURE.md línea 103).

#### `backend/app/repositories/producto.py` (repository, CRUD read)

**Patrón:** clase por agregado con sesión inyectada; única capa que toca SQLAlchemy; `select` componiendo filtros, jamás strings SQL (ARCHITECTURE.md líneas 60, 116-133; 01-RESEARCH.md "Don't Hand-Roll" fila SQL del catálogo). Formato de firma: `ProductoRepository(db)` usado por el service (Pattern 1 línea 280).

#### `backend/app/services/catalogo.py` (service)

**Código de referencia:** 01-RESEARCH.md Pattern 1 (líneas 272-281):

```python
# Source: 01-RESEARCH.md lines 279-281 — el service recibe repos inyectados
return CatalogService(ProductoRepository(db)).listar(
    familia=familia, precio_min=precio_min, precio_max=precio_max
)
```

Reglas de negocio de listado/detalle viven aquí (solo activos, 404 si no existe); el service nunca sabe de HTTP.

#### `backend/app/routers/productos.py` (route, request-response)

**Código de referencia:** 01-RESEARCH.md Pattern 1 (líneas 272-281, handler completo):

```python
# Source: 01-RESEARCH.md lines 272-281
@router.get("", response_model=list[ProductoResumen])
def listar_productos(
    familia: FamiliaAromatica | None = None,
    precio_min: int | None = Query(default=None, ge=0),
    precio_max: int | None = Query(default=None, ge=0),
    db: Session = Depends(get_session),
):
    return CatalogService(ProductoRepository(db)).listar(...)
```

`APIRouter` por recurso con prefix/tags (patrón "Bigger Applications", ARCHITECTURE.md línea 58). Regla verificable: routers/ nunca importa SQLAlchemy (reglas de dependencia, ARCHITECTURE.md líneas 91-96 adaptadas al naming inglés de carpetas de 01-RESEARCH.md línea 237-247).

#### `backend/app/routers/salud.py` (route)

**Patrón conceptual:** demo-cine guia-01 Paso 4 — `@app.get("/salud")` devuelve `{"estado": "ok"}` desde día 1; en Maura es router con prefix `/api/salud` (A10; path ya presente en el esqueleto de contrato, 01-RESEARCH.md líneas 515-520).

#### `backend/app/seed.py` (batch, upsert idempotente)

**Código de referencia:** 01-RESEARCH.md Pattern 5 (líneas 407-417, completo):

```python
# Source: 01-RESEARCH.md lines 409-417 — converge siempre al estado canónico
def upsert_producto(sesion: Session, datos: dict) -> str:
    existente = sesion.scalar(select(Producto).where(Producto.sku == datos["sku"]))
    if existente is None:
        sesion.add(Producto(**datos))
        return "[+]"
    for campo, valor in datos.items():
        setattr(existente, campo, valor)   # actualiza precios/stock al valor canónico
    return "[=]"
```

Convences a copiar del análogo conceptual (demo-cine guia-08): docstring con uso, prints `[+]`/`[=]`, datos de ejemplo como constante tipada al tope del archivo. **Diferencia deliberada:** upsert por SKU (no insert-only como demo-cine) — única clave natural estable, compatible con FKs de fase 3 (Pitfall 6: jamás DELETE FROM + reinsert). Ejecución: `uv run python -m app.seed`. Contenido: 12 SKU (4 familias × 3), precios dentro de $6.990–$12.990 (D-07), imágenes `/products/{sku}.jpg` (D-08), stock con 1-2 valores bajos y ninguno en 0 (Open Question 4).

---

### Grupo C — Frontend SPA (greenfield; scaffold + patrones verificados)

#### `frontend/` (scaffold)

**Generado por:** `npm create vite@latest frontend -- --template react-ts` desde la raíz del monorepo (01-RESEARCH.md Installation líneas 130-136). El template trae react 19.3, vite 8.3.1, TS ~6.0.2 (NO subir a 7, Pitfall 9) y oxlint (no reemplazar por ESLint). **Gate:** requiere Node >= 22.22 resuelto antes (Pitfall 1). Luego: `npm install react-router @tanstack/react-query` y `npm install tailwindcss @tailwindcss/vite`.

#### `frontend/vite.config.ts` (config)

**Código de referencia:** 01-RESEARCH.md Pattern 4 (líneas 377-390, completo):

```ts
// Source: 01-RESEARCH.md lines 383-390
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: { "/api": "http://localhost:8000" },
  },
});
```

Tailwind 4 = plugin de Vite, sin tailwind.config.js ni PostCSS.

#### `frontend/src/main.tsx` (entry, providers)

**Código de referencia:** 01-RESEARCH.md Pattern 3 (líneas 350-371, completo) — puntos críticos verificados contra el tarball de react-router 8.4.0:

```tsx
// Source: 01-RESEARCH.md lines 352-353 — v8 ELIMINA react-router-dom
import { BrowserRouter, Routes, Route } from "react-router";  // NO "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
```

Orden de providers: StrictMode > QueryClientProvider > BrowserRouter > Routes. Rutas fase 1: `/` (landing), `/productos` (grilla), `/productos/:id` (ficha), `*` (404). **Anti-pattern:** `createBrowserRouter` data mode (01-RESEARCH.md línea 437 — override explícito a ARCHITECTURE.md línea 55/87 que lo menciona).

#### `frontend/src/index.css`

Única línea requerida sobre el scaffold: `@import "tailwindcss";` al tope (01-RESEARCH.md línea 253; verificado tailwindcss.com/docs vía STACK). La paleta concreta la formaliza `/gsd:ui-phase` (D-03).

#### `frontend/src/lib/api.ts` (utility, único punto HTTP)

**Patrón estructural:** ARCHITECTURE.md — "la URL del backend y el attach del Bearer viven en un solo lugar" (líneas 56, 91-92, 106). Fase 1 (sin auth todavía): `const base = import.meta.env.VITE_API_URL ?? ""` + helper `apiGet<T>(path)` con `fetch`, `res.ok` check y `throw` del `detail` (contrato Error schema). Regla innegociable: **ningún componente hace fetch directo** — todo pasa por lib/api (01-RESEARCH.md línea 263).

#### `frontend/src/types/api.ts` (types, espejo del contrato)

**Código de referencia:** 01-RESEARCH.md Pattern 3 (líneas 321-346, completo):

```typescript
// Source: 01-RESEARCH.md lines 323-345 (resumen)
export type Familia = "citricas" | "florales" | "frutales" | "dulces";

export interface ProductoResumen {
  id: number;
  sku: string;
  nombre: string;
  precio: number;       // CLP entero
  familia: Familia;
  imagen: string;       // "/products/citricas-01.jpg"
}

export interface ProductoDetalle extends ProductoResumen { ... }

export const FAMILIA_LABELS: Record<Familia, string> = {
  citricas: "Cítricas", ...
};
```

El espejo manual TS ↔ Pydantic ES el ejercicio pedagógico (D-09) — no hay codegen. `FAMILIA_LABELS` mapea slug ASCII → etiqueta con acento (Pitfall 5).

#### `frontend/src/features/catalogo/` (components: grilla, ProductCard, filtros, ficha)

**Código de referencia — filtros en URL + TanStack Query:** 01-RESEARCH.md Code Examples (líneas 566-579):

```tsx
// Source: 01-RESEARCH.md lines 568-579
const [params, setParams] = useSearchParams();
const familia = params.get("familia") ?? "";
const query = useQuery({
  queryKey: ["productos", familia, params.get("precio_min"), params.get("precio_max")],
  queryFn: () => apiGet<ProductoResumen[]>(`/api/productos?${new URLSearchParams(...)}`),
});
```

queryKey incluye los filtros (cache por combinación); filtros van en search params (URLs compartibles, A6); la SPA muestra la etiqueta con acento vía FAMILIA_LABELS y por el cable viaja el slug. Estilos: Tailwind utilities; estados loading/error/empty de useQuery obligatorios por pantalla (espíritu demo-cine 03_diseno §4.1 "estados obligatorios por pantalla").

#### `frontend/src/features/landing/` y `frontend/src/components/`

Sin análogo (greenfield). Contenido de marca: "Maura · Body Splash" + tagline "Frescura que te acompaña" (D-01/D-04) + bloque breve con la persona (Open Question 3). Navbar/Footer/Layout compartidos en `components/`. La dirección fresco-luminosa (pasteles cítricos, blanco, tipografía redondeada) la formaliza `/gsd:ui-phase` — esta fase deja la estructura lista.

#### `frontend/public/products/*.jpg` (assets)

Sin análogo. Fotos stock reales (Unsplash/Pexels) descargadas al repo, nombradas por SKU (`/products/{sku}.jpg`), 12 archivos (D-08). Criterio: consistencia visual por familia. Nada de hotlinks (Pitfall 10). Vite las sirve en dev y las copia al build.

## Shared Patterns

### API-first: contrato antes del código (D-15)

**Source:** `D:/Repos/demo-cine/docs/04_arquitectura/adr/008-api-first.md` líneas 19-26 + flujo en `04_arquitectura/README.md` líneas 139-141.
**Apply to:** orden de los planes de la fase (frente A docs → frente B/C código) + guía 04 (verificación de cierre /docs ≈ contrato).
```text
contrato_api.yaml (se aprueba)  →  el código lo implementa  →  /docs generado ≈ contrato (verificación de desvío)
```

### Formato de precio CLP (Integer + Intl)

**Source:** 01-RESEARCH.md líneas 583-587 (verificado por ejecución node).
**Apply to:** models (Integer), contrato (integer), ProductCard y FichaProducto.
```typescript
const clp = new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP" });
clp.format(6990); // "$6.990"
```

### CORS explícito desde settings

**Source:** 01-RESEARCH.md Pattern 4 líneas 393-402; ARCHITECTURE.md Anti-Pattern 3 (líneas 269-273).
**Apply to:** `backend/app/main.py` desde la guía 01 — lista explícita (`http://localhost:5173` + placeholder prod), nunca `["*"]`.

### Comandos agnósticos de terminal (D-12)

**Source:** 01-RESEARCH.md Installation (líneas 129-142) — todo `npm ...` y `uv ...`, una sola forma por comando.
**Apply to:** las 4 guías de 05_desarrollo. Difieren de demo-cine, que muestra bloques powershell/bash alternativos (guia-01 líneas 27-42) — NO replicar esa dualidad.

### Seed idempotente re-ejecutable (STORE-04)

**Source:** 01-RESEARCH.md Pattern 5 (líneas 404-419) + conceptual demo-cine guia-08 Paso 2.
**Apply to:** `backend/app/seed.py` + guía 03. Re-ejecutar restaura el estado canónico (documentarlo como feature).

### Trazabilidad numerada del ciclo

**Source:** demo-cine 01_necesidad (P/C/CS/D) → 02_requerimientos (RF/RNF/RN/HU + tabla §13) → 03_diseno (§5) → contrato (descriptions citan RF) → guías (pasos citan ADR/RN).
**Apply to:** los 9 documentos de docs/ — la numeración P/CS se fija en 01_necesidad y se cita en cadena.

### Divergencias demo-cine → demo-carro (NO copiar del análogo)

| Tema | demo-cine (análogo) hace | Maura debe hacer | Fuente |
|------|--------------------------|------------------|--------|
| Toolchain Python | pip + venv + requirements.txt + run.py | uv: `uv init --vcs none`, pyproject + uv.lock, `uv run fastapi dev` | D-10, Pitfall 2/3 |
| Arquitectura web | Monolito SSR Jinja2 (ADR-006) | Dos tiers SPA + API separados | PROJECT.md, CONTEXT boundary |
| Router React | (no tiene frontend) | `react-router` 8 library mode (BrowserRouter); `react-router-dom` NO existe en v8 | STACK, Pattern 3 |
| Estado servidor | (n/a) | TanStack Query `useQuery`, jamás useEffect+useState para datos | Don't Hand-Roll |
| Seed | Insert-only si vacío | Upsert por SKU | Pattern 5, Pitfall 6 |
| Idioma de campos API | `/api/peliculas`, `titulo` | Español también (`/api/productos`, `nombre`) — consistencia mantenida | A1 |
| create_all | (n/a) | create_all + seed idempotente; Alembic diferido y documentado en ADR | A8, Pitfall 8 |

## No Analog Found

Archivos sin análogo de código en este repo ni en demo-cine (el planner usa los patrones verificados de `01-RESEARCH.md` citados arriba; ninguno requiere investigación adicional):

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `backend/pyproject.toml` | config | — | Repo greenfield; generado por uv + ajustes Pitfall 2/3 |
| `backend/app/__init__.py` | package | — | Greenfield |
| `backend/app/main.py` | entry | request-response | Sin código backend previo; patrón doc demo-cine + Pattern 4 |
| `backend/app/config.py` | config | — | pydantic-settings nuevo en el ecosistema (demo-cine usa os.getenv) |
| `backend/app/database.py` | utility | CRUD | Greenfield |
| `backend/app/models/producto.py` | model | CRUD | Greenfield |
| `backend/app/schemas/producto.py` | schema | transform | Greenfield |
| `backend/app/repositories/producto.py` | repository | CRUD | Greenfield |
| `backend/app/services/catalogo.py` | service | request-response | Greenfield |
| `backend/app/routers/productos.py` | route | request-response | Greenfield |
| `backend/app/routers/salud.py` | route | request-response | Greenfield |
| `backend/app/seed.py` | script | batch | Greenfield (patrón doc en demo-cine guia-08) |
| `frontend/` (scaffold) | scaffold | — | Generado por create-vite |
| `frontend/vite.config.ts` | config | — | Greenfield |
| `frontend/src/main.tsx` | entry | request-response | Greenfield |
| `frontend/src/index.css` | config | — | Greenfield |
| `frontend/src/lib/api.ts` | utility | request-response | Greenfield |
| `frontend/src/types/api.ts` | types | transform | Greenfield (espejo manual deliberado, sin codegen) |
| `frontend/src/features/landing/` | component | static | Greenfield; paleta via `/gsd:ui-phase` |
| `frontend/src/features/catalogo/` | component | request-response | Greenfield |
| `frontend/src/components/` | component | static | Greenfield |
| `frontend/public/products/*.jpg` | assets | file-I/O | Selección manual en ejecución (A12) |

## Metadata

**Analog search scope:** `D:/Repos/demo-carro` (todo el repo trackeado — 41 archivos, solo planificación) · `D:/Repos/demo-cine/docs/` completo (26 archivos, repo hermano de referencia de formato D-13) · `.planning/research/{ARCHITECTURE,STACK}.md` (in-repo, trackeados).
**Tracked-source gate:** análogos demo-cine verificados con `git ls-files docs/` ejecutado dentro de `D:/Repos/demo-cine` (los 26 listados, incluidos todos los citados); análogos in-repo verificados con `git ls-files` en `D:/Repos/demo-carro`. Ninguna ruta mirror/gitignored emitida.
**Files scanned:** 12 análogos leídos completos (README, 01, 02, 03, 04 README, adr/001, adr/008, contrato_api.yaml, 05 README, guia-01, guia-08, ARCHITECTURE.md — 2.158 líneas) + 01-CONTEXT.md y 01-RESEARCH.md del phase dir.
**Pattern extraction date:** 2026-09-28
