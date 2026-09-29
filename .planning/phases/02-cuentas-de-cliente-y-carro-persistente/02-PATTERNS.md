# Phase 2: Cuentas de cliente y carro persistente - Pattern Map

**Mapped:** 2026-09-29
**Files analyzed:** 14 (7 documentos nuevos + 7 extensiones de documentos existentes)
**Analogs found:** 14 / 14 con análogo exacto in-repo (a diferencia de la fase 1 greenfield, esta fase extiende un corpus ya establecido: todos los archivos a crear/modificar tienen su análogo dentro de `docs/`, git-trackeado)

## Nota de alcance: repo guide-only, fase documental (leer primero)

`D:/Repos/demo-carro` sigue **guide-only (D-17, ADR-008)**: la fase 2 entrega SOLO documentos. La diferencia con la fase 1 es que ahora el corpus existe — cada doc nuevo/extendid­o tiene análogo exacto dentro del propio repo:

1. **Los 7 documentos a modificar** (`02_requerimientos.md`, `03_diseno.md`, `contrato_api.yaml`, `04_arquitectura/README.md`, `05_desarrollo/README.md`, `docs/README.md`, `README.md` raíz) se extienden in-place: el análogo es el propio archivo, y el patrón a extraer es "cómo continúa cada serie sin romper la trazabilidad".
2. **Los 7 documentos nuevos** (ADRs 009-011, guías 05-08) replican formato de análogos existentes: ADR-007 para los ADRs; guia-03 (backend) + guia-04 (frontend y cierre) + guia-02 (rutas/Navbar) para las guías.
3. **El código que las guías narran** (`security.py`, `models/usuario.py`, stores Zustand, `RequireAuth.tsx`, interceptor 401) NO tiene precedente en ningún repo del ecosistema (demo-cine tampoco tiene auth ni SPA). Su fuente es `02-RESEARCH.md` Patterns 1-8 (verificados contra tutorial FastAPI / docs Zustand / swagger.io esta sesión). El planner copia de ahí; la guía lo traduce a la estructura canónica.
4. **Orden API-first obligatorio (D-15/ADR-007):** `contrato_api.yaml` se extiende y APRUEBA antes de escribir las guías. Orden de planes: (A) docs 02/03 → (B) contrato + ADRs 009-011 + README de arquitectura → (C) guías 05-08 → (D) READMEs de estado.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `docs/02_requerimientos.md` (EXTENDER) | doc requerimientos | — | sí mismo (continuar series RF/RNF/RN/HU + tabla §13) | exact (in-place) |
| `docs/03_diseno.md` (EXTENDER) | doc diseño | — | sí mismo (§2 ER/diccionario, §3 DFD, §4 pantallas, §5 trazabilidad) | exact (in-place) |
| `docs/04_arquitectura/contrato_api.yaml` (EXTENDER, antes de guías) | contract (OpenAPI) | request-response | sí mismo (tabla errores 22-32, tags 40-44, schemas, paths) | exact (in-place) |
| `docs/04_arquitectura/adr/009-*.md` (NUEVO: JWT larga vida + localStorage, D-19..D-22) | doc (decisión) | — | `docs/04_arquitectura/adr/007-api-first.md` | exact (formato) |
| `docs/04_arquitectura/adr/010-*.md` (NUEVO: carro client-side, D-27..D-30) | doc (decisión) | — | `docs/04_arquitectura/adr/007-api-first.md` | exact (formato) |
| `docs/04_arquitectura/adr/011-*.md` (NUEVO: roles desde el primer token, D-23/D-24/D-33) | doc (decisión) | — | `docs/04_arquitectura/adr/007-api-first.md` | exact (formato) |
| `docs/04_arquitectura/README.md` (EXTENDER) | doc índice/arquitectura | — | sí mismo (§3 stack, §4 árbol+reglas, §5 índice ADRs) | exact (in-place) |
| `docs/05_desarrollo/guia-05-*.md` (NUEVO: backend cuentas) | doc (guía paso a paso) | — | `guia-03-modelos-y-seed.md` + `guia-04` pasos 1-3 + `guia-01` (Settings/CORS) | exact (estructura) |
| `docs/05_desarrollo/guia-06-*.md` (NUEVO: sesión frontend) | doc (guía paso a paso) | — | `guia-04` paso 7 (lib/api.ts) + `guia-02` (main.tsx, Navbar) | exact (estructura) |
| `docs/05_desarrollo/guia-07-*.md` (NUEVO: carro) | doc (guía paso a paso) | — | `guia-04` pasos 5-7 (estados async, ApiError 404, hidratación) | exact (estructura) |
| `docs/05_desarrollo/guia-08-*.md` (NUEVO: checkout + Gran verificación final) | doc (guía de cierre) | — | `guia-04` §"Gran verificación final de la fase 1" (971-1005) + cierre (1009-1032) | exact (estructura) |
| `docs/05_desarrollo/README.md` (EXTENDER) | doc índice | — | sí mismo (tabla de guías 24-29) | exact (in-place) |
| `docs/README.md` (EXTENDER) | doc índice | — | sí mismo (tabla del ciclo, fila 5 línea 19) | exact (in-place) |
| `README.md` raíz (EXTENDER) | doc índice | — | sí mismo (tabla líneas 36-45 + stack líneas 68-78) | exact (in-place) |

## Pattern Assignments

### Grupo A — Requerimientos y diseño de la etapa 2

#### `docs/02_requerimientos.md` (EXTENDER)

**Analog:** sí mismo (223 líneas, leído completo esta sesión).

**Numeración vigente a continuar** [VERIFIED líneas 66-134]: `RF-01..RF-05` (agrupados por tema con encabezado "(soportan P.., C..)"), `RNF-01..RNF-04` (tabla `Código | Categoría | Descripción | Origen`), `RN-01..RN-04` (bullets con cita de origen en cursiva), `HU-01..HU-04` (Gherkin *Como/quiero/para* + **Dado/Cuando/Entonces**). Los nuevos llegan como RF-06+, RNF-05+, RN-05+, HU-05+ (candidatos: registro/login/sesión/rol desde AUTH-01..03, carro desde CART-01..02, checkout AUTH-04).

**Formato exacto de un RF con origen** (línea 67):

```markdown
- **RF-01:** El sistema debe mostrar una página de inicio con la identidad de la
  marca Maura · Body Splash — ... *(STORE-01, P1)*
```

**Puntos que cambian de estado:**
- §2 alcance (líneas 40-44): la fila "Carro de compras y cuentas de clientas (P5) → **etapa 2**" pasa de "fuera del alcance" a dentro; P6/P7/P8 siguen esperando su etapa.
- §3 actores (líneas 54-60): hoy tabla con único actor `Visitante (anónimo)` + blockquote que relega clientas/admin a §13. La etapa 2 agrega filas `Clienta (con cuenta)` y `Admin (dueña)` con columna `Origen` (P5, P7) — el blockquote se ajusta (los actores de pago/IA siguen en trazabilidad).
- §13 trazabilidad, fila P5 (línea 194, verbatim): `| P5 Carro y cuentas | *(sin requerimiento en esta etapa — etapa 2: CART-01..03, AUTH-01..04 del requisitos v1)* | Etapa 2 |` → se reemplaza por el mapeo real a los RF/HU nuevos (CART-03/PAY siguen en etapa 3).
- §10 entradas (159-165): nueva fila para formulario de registro (email formato, password ≥ 8, D-25) y login.
- §12 pantallas (176-181): se suman login, registro, carro, checkout como ítems 4-7 (insumo de 03_diseno §4).
- §14 aprobación (210-215): nueva fecha de firma de la etapa.

---

#### `docs/03_diseno.md` (EXTENDER)

**Analog:** sí mismo (367 líneas, leído completo esta sesión).

**§2.1 Diagrama ER en mermaid** (líneas 32-46): entidad PRODUCTO con comentarios citando RF/RN en cada campo — replicar el formato para USUARIO (id, email UK "clave natural del upsert de cuentas (RF-nuevo)", hashed_password, rol "cliente | admin"). La nota "Lectura del diagrama" (48-53) ya anuncia que "las cuentas de clientas y los pedidos llegan en las etapas 2 y 3": la etapa 2 la actualiza en esos términos.

**§2.2 Diccionario de datos** (formato, líneas 59-70):

```markdown
| Atributo | Tipo | Longitud | Obligatorio | Restricción / origen |
|---|---|---|---|---|
| sku | Texto | 20 | Sí | **Único**; clave natural estable del catálogo demo: ... (RF-05) |
```

Nueva tabla **USUARIO** con las mismas 5 columnas. Los valores exactos de longitud los fija el planner (02-RESEARCH.md "Code Examples — Modelo Usuario" trae el borrador: email 255 único+índice, hashed_password 255 `"$argon2id$..."`).

**§2.3 Decisiones de diseño numeradas "(y por qué)"** (74-103): continuar la numeración con las decisiones de la etapa 2 — email como clave del upsert de cuentas (D-23/D-24), el hash jamás cruza la frontera, el carro guarda solo `{producto_id, cantidad}` (D-27) con hidratación contra precios vigentes, cantidades tapadas al stock en pantalla (D-30).

**§3 Procesos**: §3.1 contexto (117-127) agrega entidades externas; §3.2 almacenes (131-134) agrega `D2 Usuarios` y el almacén cliente `A2 localStorage` (sesión + carro — decisión de diseño, no de tecnología); §3.3-3.6 DFDs numerados 1.0-4.0 → continuar con 5.0+ (crear cuenta, iniciar sesión, armar/editar carro, ver checkout protegido), cada uno con `flowchart TD` + bloque "**Reglas del proceso:**" (146-148, 160-164).

**§4 Pantallas** — formato obligatorio por pantalla (260-266): wireframe ASCII + encabezado:

```markdown
**Origen:** RF-02, RF-03, HU-01, HU-02 · **Estados:** carga (...) / error (...) /
vacío con filtros ("No encontramos aromas con esos filtros" + Limpiar filtros) / ...
```

Pantallas 4-7 nuevas (login, registro, carro, checkout): el wireframe y los estados los aporta `02-UI-SPEC.md` (Screens & Interaction Contract, líneas 128-211 — contenedor, filas, stepper, banners, empty states ya contratados); 03_diseno los traduce al lenguaje de diseño (sin clases Tailwind — eso es implementación). La ficha existente (299-331) gana el botón "Agregar al carro" (D-29) como variante de la pantalla 3.

**§5 Trazabilidad** (formato, líneas 337-350): tabla `| Requerimiento | Dónde se resuelve en este diseño |` — una fila por RF/RN nuevo de la etapa 2.

---

### Grupo B — Contrato, ADRs y README de arquitectura

#### `docs/04_arquitectura/contrato_api.yaml` (EXTENDER — primer entregable de código-adjacente, ANTES de las guías, D-15)

**Analog:** sí mismo (203 líneas, leído completo esta sesión).

**Header de regencia** (líneas 1-8): mantener textual el bloque `# Maura — Contrato de la API ... FUENTE DE LA VERDAD ... Se aprueba antes de codificar`.

**Cambios puntuales con línea exacta:**
- `info.version: 0.1.0` (línea 13) → `0.2.0` (el contrato versiona su crecimiento).
- `info.description` nota de autenticación (líneas 19-20, verbatim): `**Autenticación:** ninguna por ahora — los endpoints de la fase 1 son públicos y de solo lectura. Las cuentas JWT llegan en la fase 2.` → reescribir: sesión JWT Bearer en `/api/auth/*` y `/api/admin/estado`.
- **Tabla de convención de errores** (líneas 22-32): las filas 401/403/409 pasan de `Reservado (fases 2+)` a `En uso (fase 2)`; evaluar agregar fila 201 (registro). Verbatim actual:

```yaml
    | Código | Significado | Estado |
    |---|---|---|
    | 200 | OK (listado, ficha, salud) | En uso (fase 1) |
    | 400 | Regla de negocio violada | Reservado (fases 2+) |
    | 401 | Sin sesión o credenciales incorrectas | Reservado (fases 2+) |
    | 403 | Con sesión, pero sin permiso | Reservado (fases 2+) |
    | 404 | Recurso inexistente | En uso (fase 1) |
    | 409 | Conflicto | Reservado (fases 2+) |
    | 422 | Datos mal formados (validación de esquema) | En uso (fase 1) |
```

- **tags** (formato, líneas 40-44 — citan el requisito que los origina): nuevos `Autenticación` (cita AUTH-01..03) y `Administración` (cita AUTH-03/D-33) igual que `Productos` cita `(STORE-02, STORE-03)`.
- **schemas** (convención, líneas 59-108): cada schema con `description` citando requisito + `description` por campo + `example` + `required`. Nuevos: `UsuarioPublico` (sin hashed_password — Pitfall 10), `Token`, `RegistroCreate` (`password: minLength: 8`, D-25) según 02-RESEARCH.md Pattern 8; `components.securitySchemes.bearerAuth` (`type: http, scheme: bearer, bearerFormat: JWT`).
- **paths** (convención, líneas 128-203): `description` citando el RF + responses declaradas. Nuevos: `/api/auth/registro` (POST JSON → 201/409/422), `/api/auth/login` (POST `application/x-www-form-urlencoded` username/password → 200 Token/401), `/api/auth/perfil` (GET `security: [{bearerAuth: []}]` → 200/401), `/api/admin/estado` (GET bearerAuth → 200/401/403, D-33).
- **Detalle 401/403/409 declarados en cada path**: misma lección del 404 de guia-04 (líneas 274-281: `responses={404: {"description": ..., "model": Error}}`) — sin declaración, `/docs` no los lista y la fila contrato↔`/docs` de la Gran verificación final detecta un falso desvío (Pitfall 11 de RESEARCH).

---

#### `docs/04_arquitectura/adr/009..011-*.md` (NUEVO — 3 ADRs)

**Analog:** `docs/04_arquitectura/adr/007-api-first.md` (54 líneas, leído completo; ADR-001 es el segundo ejemplo del formato).

**Esqueleto obligatorio** (ADR-007 líneas 1-5 y secciones):

```markdown
# ADR-009 — <Decisión en una frase>

- **Estado:** Aceptada
- **Fecha:** 2026-09-__ (fecha de la fase 2)
- **Resuelve:** <pregunta de decisión>

## Contexto
## Opciones consideradas        → tabla | Opción | A favor | En contra | (3 opciones A/B/C)
## Decisión                     → "**Opción X.**" + reglas numeradas
## Consecuencias                → **Positivas** / **Negativas (honestas)**
## Para conversar en clase      → 3 preguntas numeradas
```

**Ejemplo de tabla de opciones** (ADR-007 líneas 22-27, replicar densidad: 3 opciones, pros/contras honestos):

```markdown
| Opción | A favor | En contra |
|---|---|---|
| **A. Code-first** ... | Cero pasos extra ... | El contrato llega tarde ... |
| **B. API-first manual** ... | La interfaz se discute ... | Doble mantenimiento ... |
| **C. API-first con generación** ... | Drift imposible ... | Tooling pesado ... |
```

**Contenido candidato (discretion confirmada en CONTEXT, asumptions A6):** 009 = JWT token único de larga vida + localStorage (D-19..D-22; la desventaja XSS va en **Negativas (honestas)** tal cual exige D-21); 010 = carro client-side hidratado (D-27..D-30; alternativa server-side en tabla); 011 = roles desde el primer token + seed por env vars (D-23/D-24/D-33; "primer registrado = admin" y credenciales fijas como opciones descartadas).

---

#### `docs/04_arquitectura/README.md` (EXTENDER)

**Analog:** sí mismo (215 líneas, leído completo esta sesión).

- **§3 Stack** (tabla `| Pieza | Elección | Por qué (decisión completa) |`, líneas 101-117): agregar filas para pyjwt, pwdlib[argon2], python-multipart, zustand — cada una citando su ADR nuevo (009/010) o el tutorial oficial, igual que las filas existentes citan ADR-001..007.
- **§4 Árbol del proyecto del alumno** (129-152): agregar `security.py` (módulo transversal, A12), `models/usuario.py`, `schemas/usuario.py`, `repositories/usuario.py`, `services/cuentas.py`, `routers/auth.py`, `routers/admin.py`, `stores/` (o `lib/`), `components/RequireAuth.tsx`, `features/cuentas/`, `features/carro/`, `features/checkout/`. Mantener intacto el disclaimer guide-only (123-127).
- **Reglas de dependencia 1-6** (154-166): no cambian — la regla 5 ("todo HTTP pasa por `src/lib/api.ts`") es justo la que el interceptor 401 (D-22) refuerza; las guías nuevas la citan igual que las de fase 1.
- **§5 Índice de ADRs** (formato, líneas 172-182): `| [ADR](adr/NNN-slug.md) | Decisión | Resuelto por |` → 3 filas nuevas (009, 010, 011).

---

### Grupo C — Guías 05-08

> Regla transversal del grupo: las 4 guías replican la **estructura canónica** fijada en guia-01..04 (ver Shared Patterns). Lo que cambia es el contenido; nada de la mecánica. La convención "Gran verificación final" de guia-04 (971-1005) la replica guia-08 como cierre de la fase 2 (CONTEXT boundary: "las fases 2-5 replican").

#### `docs/05_desarrollo/guia-05-*.md` (NUEVO — backend cuentas)

**Analog:** `guia-03-modelos-y-seed.md` (636 líneas, completa) para modelo+seed; `guia-04-catalogo.md` pasos 1-3 para capas; `guia-01-proyecto-backend.md` (434 líneas, completa) para Settings/CORS.

**Modelo Usuario — espejo del patrón Producto de guia-03:**
- Enum con EL GOTCHA nombre==valor (guia-03 líneas 123-135) — segunda vuelta del mismo bug (Pitfall 6 de RESEARCH): `RolUsuario` se declara `cliente = "cliente"`, `admin = "admin"`, y la guía lo remite explícitamente a la lección cerrada de guia-03:

```python
# Source: guia-03-modelos-y-seed.md lines 123-135 (patrón a replicar para RolUsuario)
class FamiliaAromatica(str, enum.Enum):
    citricas = "citricas"    # nombre == valor: la BD guarda "citricas",
```

- Modelo con `Mapped[]`/`mapped_column` (guia-03 líneas 179-197): `Usuario` con `email` `unique=True, index=True` (la clave del upsert, D-23/D-24), `hashed_password`, `rol` con `default`.

**Seed de usuarios — espejo del upsert por SKU, ahora por email** (guia-03 líneas 279-287 + main 470-490):

```python
# Source: guia-03-modelos-y-seed.md lines 279-287 — upsert_producto; guia-05 narra
# upsert_usuario(sesion, email, password, rol) con la MISMA forma (email en vez de sku)
def upsert_producto(sesion: Session, datos: dict) -> str:
    existente = sesion.scalar(select(Producto).where(Producto.sku == datos["sku"]))
    if existente is None:
        sesion.add(Producto(**datos))
        return "[+]"
    for campo, valor in datos.items():
        setattr(existente, campo, valor)
    return "[=]"
```

Convenciones a copiar: docstring con uso (`uv run python -m app.seed`), prints `[+]`/`[=]` por fila, resumen final `Seed listo: N creados [+], M actualizados [=]`, mini-verificación de idempotencia re-ejecutando (guia-03 líneas 531-537). La restore de credenciales al re-ejecutar se narra como feature deliberada (D-23: "cada alumno reinicia su admin sin miedo"). Usuarios después de productos en `main()` (A: sin FK entre sí hoy).

**Capas (schemas → repository → service → router)** — espejo de guia-04 pasos 1-3:
- Schemas implementan el contrato con `model_config = ConfigDict(from_attributes=True)` y docstring "espejan contrato_api.yaml" (guia-04 líneas 47-84). Nota obligatoria estilo "`activo` no aparece" (guia-04 líneas 91-95): **`hashed_password` no aparece en ningún schema** — Pydantic filtra por omisión (Pitfall 10).
- Repository clase con sesión inyectada, `select` parameterizado, sin reglas de negocio (guia-04 líneas 143-171): `UsuarioRepository` con `por_email` y `crear`.
- Service sin HTTP (guia-04 líneas 215-234): `CuentasService.registrar` (devuelve señal de 409) y `autenticar` (401 genérico D-26).
- Router con `responses` declaradas (guia-04 líneas 272-291): los endpoints de auth declaran 401/403/409 igual que `obtener_producto` declara el 404 — y la guía remite a esa lección (G-01-4).

**Config y CORS — extensiones puntuales de guia-01:**

```python
# Source: guia-01-proyecto-backend.md lines 199-206 — Settings vigente (base VERIFIED)
class Settings(BaseSettings):
    database_url: str = "sqlite:///./maura.db"
    cors_origins: list[str] = ["http://localhost:5173"]
# guia-05 agrega: secret_key (sin default, fail-fast), token_dias=7 (D-20),
# admin_email/password, cliente_email/password (D-23/D-24)
```

```python
# Source: guia-01-proyecto-backend.md lines 285-290 — CORS vigente
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET"],      # ← guia-05 lo actualiza a ["GET", "POST"] (Pitfall 1)
    allow_headers=["*"],
)
```

**Instalación narrada** (estilo guia-01 línea 136 `uv add "fastapi[standard]" sqlalchemy pydantic-settings`): `uv add pyjwt "pwdlib[argon2]" python-multipart`. **SECRET_KEY** con one-liner agnóstico `uv run python -c "import secrets; print(secrets.token_hex(32))"` (D-12, Pitfall 3). **`.env.example`** con placeholders demo — jamás credenciales literales (D-23, Pitfall 12); `.env` ya está gitignoreado desde guia-01 (líneas 315-317). **Mini-verificaciones** con `uv run python -c "..."` + output esperado; el decode offline del token (`options={"verify_signature": False}}`) muestra los claims sub/rol/exp/iat (D-20).

---

#### `docs/05_desarrollo/guia-06-*.md` (NUEVO — sesión frontend)

**Analog:** `guia-04-catalogo.md` paso 7 (lib/api.ts) + `guia-02-proyecto-frontend.md` (main.tsx, Navbar).

**`lib/api.ts` — base intocable que se extiende** [VERIFIED guia-04 líneas 750-776]:

```typescript
// Source: guia-04-catalogo.md lines 751-775 — ApiError + apiGet vigentes (la fase 2
// AGREGA authHeaders() con useAuthStore.getState().token, interceptor 401 →
// "/login?expirada=1" (D-22) y apiPostForm (FormData sin Content-Type manual))
export class ApiError extends Error {
  readonly status: number;
  constructor(mensaje: string, status: number) { super(mensaje); this.status = status; }
}
const base = import.meta.env.VITE_API_URL ?? "";
export async function apiGet<T>(ruta: string): Promise<T> {
  const res = await fetch(`${base}/${ruta}`);
  if (!res.ok) {
    let mensaje = `Error HTTP ${res.status}`;
    try { const cuerpo = await res.json(); if (cuerpo?.detail) mensaje = cuerpo.detail; }
    catch { /* cuerpo sin JSON */ }
    throw new ApiError(mensaje, res.status);
  }
  return res.json();
}
```

El interceptor NO dispara en el propio login (Pitfall 5). Código nuevo completo: 02-RESEARCH.md Pattern 4.

**Rutas — extensión de main.tsx** [VERIFIED guia-02 líneas 231-262]: las 4 rutas vigentes (`/`, `/productos`, `/productos/:id`, `*`) dentro de `<Route element={<Layout />}>`; guia-06 agrega `/login` y `/registro` (y guia-07/08 las suyas — `/carro` y `<Route element={<RequireAuth />}><Route path="/checkout" .../></Route>`). Mantener el orden de providers StrictMode > QueryClientProvider > BrowserRouter y los imports desde `"react-router"` (guia-02 líneas 216-234 narran por qué).

**Navbar — extensión** [VERIFIED guia-02 líneas 434-467]: `estiloLink` y el header `sticky top-0 z-10 bg-orange-50/90 backdrop-blur border-b border-orange-100` se conservan; el grupo de links gana "Carro" con badge (guia-07) y el estado de sesión ("Ingresar" / email truncado + "Cerrar sesión") — especificación exacta en `02-UI-SPEC.md` §"Navbar — extensión" (líneas 144-151).

**Login/Registro** [VERIFIED 02-UI-SPEC.md líneas 153-172]: cards `bg-white rounded-2xl border border-orange-100 p-6 md:p-8`, banners ámbar/esmeralda/rojo `rounded-2xl p-4 text-sm`, returnTo `navigate(location.state?.from?.pathname ?? "/", { replace: true })` (D-32). Código RequireAuth: 02-RESEARCH.md Pattern 6.

---

#### `docs/05_desarrollo/guia-07-*.md` (NUEVO — carro)

**Analog:** `guia-04-catalogo.md` pasos 5-7 (estados async uniformes, ApiError, hidratación por id).

**Los cuatro estados async** — patrón uniforme de fase 1 [VERIFIED guia-04 líneas 514-545]: `isPending` → skeletons del mismo tamaño que la fila real (`animate-pulse bg-neutral-200 rounded-2xl`); `isError` → bloque centrado + causa puerto 8000 + "Reintentar" (`refetch()`); vacío con causa. La página `/carro` y su empty state ("Tu carro está vacío") están contratados en `02-UI-SPEC.md` líneas 180-191.

**Fila degradada por 404** — reuso del patrón ApiError de la ficha [VERIFIED guia-04 líneas 836-857]: `query.error instanceof ApiError && query.error.status === 404` distingue "ya no existe" del error de red → en el carro: "Este aroma ya no está disponible" + "Quitar" (Pitfall 8).

**Hidratación por item** — reuso del queryKey de la ficha [VERIFIED guia-04 líneas 818-821]: `useQuery({ queryKey: ["producto", id], queryFn: () => apiGet<ProductoDetalle>(`api/productos/${id}`) })` — el carro hidrata cada `{producto_id, cantidad}` con este mismo hook (cacheado si el alumno vino de la ficha; A5). Cantidad tapada: `min(cantidad, stock)` (D-30).

**Botón "Agregar al carro" en la ficha** (D-29): única mutación de una pantalla de fase 1 — la guía cita que las tarjetas del catálogo siguen solo navegando (decisión fase 1). Estilo CTA y tope de stock: `02-UI-SPEC.md` líneas 173-178.

---

#### `docs/05_desarrollo/guia-08-*.md` (NUEVO — checkout protegido + Gran verificación final de la fase 2)

**Analog:** `guia-04-catalogo.md` §Gran verificación final + cierre de guía.

**Gran verificación final — formato a replicar** [VERIFIED guia-04 líneas 971-1005, verbatim]:

```markdown
## ✅ Gran verificación final de la fase 1

La tabla de cierre del ciclo — como en el proyecto hermano, cada fila cita su
origen y se marca solo si TÚ la comprobaste:

| # | Verificación | Origen |
|---|---|---|
| 1 | Landing de marca: ... | RF-01, D-04 |
...
| 11 | **Contrato ↔ `/docs`**: abre http://localhost:8000/docs y compara UNO A UNO
  contra docs/04_arquitectura/contrato_api.yaml: los 3 paths ..., los códigos de
  respuesta (200, 404, 422) y los schemas ... | ADR-007, GUIDE-02 |
```

Guia-08 replica: tabla numerada con columna Origen citando CS/RF/HU/ADR nuevos de la etapa 2 (login ambos roles, 403 de la clienta en `/api/admin/estado`, persistencia del carro tras recarga, returnTo, interceptor 401), y la **fila final contrato ↔ `/docs`** actualizada al contrato 0.2.0 — ahora incluye el botón Authorize de `/docs` con las cuentas del seed (Pattern 3 de RESEARCH: esa es la razón de ser del form-encoded). Cierre con el párrafo "este mismo mecanismo se repite al final de cada fase" (993-995) y la **sugerencia de commit** (997-1005).

**Cierre de guía** — las tres secciones fijas [VERIFIED guia-04 líneas 1009-1032]: `## 📝 Punto de control (respóndelas sin mirar la guía)` (3 preguntas), `## Lo que acabas de aprender` (bullets), `**Siguiente:**` (apunta a fase 3 — Webpay).

**Checkout** [VERIFIED 02-UI-SPEC.md líneas 193-200]: resumen hidratado, CTA "Pagar con Webpay" deshabilitado + nota locked, `<Navigate to="/carro" replace />` con carro vacío. Código RequireAuth/returnTo: 02-RESEARCH.md Pattern 6.

---

### Grupo D — READMEs de estado (D-13/D-18: el estado avanza por fase)

#### `docs/05_desarrollo/README.md` (EXTENDER)

**Analog:** sí mismo (43 líneas). Tabla `| # | Guía | Construye | Estado |` (líneas 24-29) gana filas 5-8 con el mismo estilo de columna "Construye" (una frase con el hito). El blockquote (31-34) "La fase 1 del proyecto completa sus cuatro guías. Las guías 5+ llegan con las fases siguientes (carro, pago, panel, IA)" se actualiza: fase 2 completa sus cuatro (5-8), las 9+ siguen llegando. El "Mapa mental de la serie" (36-43) gana la capa de estado de cliente sobre la base de fase 1.

#### `docs/README.md` (EXTENDER)

**Analog:** sí mismo (26 líneas). Fila 5 (línea 19): `🚧 Parcial (guías 1-4 listas; continúa en fases 2+)` → `(guías 1-8 listas; continúa en fases 3+)`. Fila 4 (línea 18): "`04_arquitectura/` (documento + 8 ADRs + `contrato_api.yaml`)" → **11 ADRs**.

#### `README.md` raíz (EXTENDER)

**Analog:** sí mismo (90 líneas). Tabla fila 5 (línea 42) igual que docs/README; referencias a "8 ADRs" (líneas 41, 54-55) → 11; párrafo de stack (líneas 68-73) menciona las piezas nuevas de la fase ("cuentas JWT", zustand) en el mismo tono telegráfico vigente: `React 19 + TypeScript + Vite 8 + Tailwind CSS 4 (SPA) · FastAPI + SQLAlchemy 2.1 + SQLite (API en capas) · uv ...`.

---

## Shared Patterns

### Estructura canónica de guía (obligatoria en guia-05..08)

**Source:** `guia-03`/`guia-04` completas; el patrón de paso está en guia-03 líneas 100-151.
**Apply to:** las 4 guías nuevas. Secuencia fija: (1) header `# Guía N — Título` + blockquote `**Qué construirás hoy:** / **Al terminar tendrás:** / **Necesitas:**` (guia-03 líneas 3-11); (2) `## Los términos de hoy (antes de copiar nada)` tabla término/frase (15-27); (3) pasos `## Paso N — título` con 🧠 **El desarrollador piensa:** en cursiva citando ADR/RN/D, código con nombre de archivo en negrita y docstring de módulo, ✅ **Mini-verificación** con comando + output esperado; (4) `## ❌ El error que este archivo evita` con pares ❌/✅ (guia-03 líneas 558-599); (5) `## ✅ Verificación de la guía N`; (6) `## 📝 Punto de control`; (7) `## Lo que acabas de aprender`; (8) `**Siguiente:**`.

```markdown
🧠 **El desarrollador piensa:** *...la decisión con su porqué, citando el ADR/RN...

Crea **`backend/app/models/usuario.py`**...:

```python
"""Docstring del módulo: qué es y qué regla encarna."""
```

✅ **Mini-verificación:** desde `backend/`, ejecuta:

uv run python -c "..."
Debe imprimir `...` — y por qué ese output es la prueba.
```

### Gran verificación final de fase

**Source:** `guia-04-catalogo.md` líneas 971-1005.
**Apply to:** guia-08 (cierre de la fase 2) y, por decisión de CONTEXT, TODAS las fases 2-5. Tabla numerada `| # | Verificación | Origen |` con origen citando CS/RF/HU/ADR + fila final contrato ↔ `/docs` + párrafo "se repite al final de cada fase" + sugerencia de commit. Ver excerpt completo en Grupo C / guia-08.

### Formato ADR

**Source:** `docs/04_arquitectura/adr/007-api-first.md` completo (54 líneas).
**Apply to:** ADRs 009-011. Estado/Fecha/Resuelve → Contexto → Opciones consideradas (tabla 3 opciones) → Decisión ("**Opción X.**" + reglas numeradas) → Consecuencias (**Positivas** / **Negativas (honestas)** — la desventaja XSS del ADR-009 va ahí por mandato de D-21) → Para conversar en clase (3 preguntas).

### API-first: contrato ANTES de las guías (D-15/ADR-007)

**Source:** `docs/04_arquitectura/adr/007-api-first.md` líneas 30-37 + `04_arquitectura/README.md` §6 (185-200).
**Apply to:** orden de los planes de la fase: docs 02/03 → contrato 0.2.0 + ADRs 009-011 aprobados → guías 05-08 → READMEs. Las guías implementan el contrato "sin desviarse" y guia-08 cierra con la comparación `/docs` ≈ contrato.

### Trazabilidad numerada continua

**Source:** series vigentes en `02_requerimientos.md` (RF/RNF/RN/HU + §13), `03_diseno.md` §5, ADRs 001-008, tags del contrato citando STORE-xx, filas de la Gran verificación citando origen.
**Apply to:** todo doc nuevo de la fase. Los tags nuevos del contrato citan AUTH-xx/CART-xx; los pasos de las guías citan los ADR-009..011 y las RN nuevas; la fila P5 de §13 se completa con los requerimientos de la etapa; el índice de ADRs llega a 011.

### Copys locked literales (aparecen VERBATIM en guías, contrato y UI)

**Source:** `02-CONTEXT.md` §specifics + `02-UI-SPEC.md` Copywriting Contract (líneas 215-245).
**Apply to:** guia-05..08 + `contrato_api.yaml` (details de error):
- "Tu sesión expiró, ingresa de nuevo" (401 interceptor, D-22)
- "Ese email ya tiene cuenta, inicia sesión" (409 registro) y "Credenciales incorrectas" (401 login genérico) (D-26)
- "el pago llega en la etapa siguiente" / "El pago llega en la etapa siguiente." (nota del CTA deshabilitado, D-31)

### Mini-verificaciones accionables (estilo establecido)

**Source:** guia-03/04 — `uv run python -c "..."` con output esperado exacto (guia-03 líneas 89-96, 492-500), URLs `http://localhost:5173/...` con qué observar (guia-04 líneas 678-684), estados provocados a propósito (guia-04 líneas 706-721).
**Apply to:** las 4 guías. Verificar 200 vs 403 con las cuentas del seed, decode offline del JWT, persistencia del carro tras recarga (F5), returnTo, interceptor 401 provocando expiración.

### Comandos agnósticos de terminal (D-12)

**Source:** guia-01..04 — todo `uv ...`/`npm ...`, una sola forma por comando.
**Apply to:** las 4 guías nuevas. Caso concreto de la fase: `uv run python -c "import secrets; print(secrets.token_hex(32))"` para el SECRET_KEY — NO `openssl rand -hex 32` (Pitfall 3).

### Idioma y marcadores del producto

Español de Chile, tuteo, tono cercano (todos los docs vigentes). Los marcadores 🧠/✅/❌/📝/🤯 son contenido del producto dentro de las guías — el resto de docs del ciclo (02/03/04) NO los usa (usan tablas, blockquotes y notas para la clase). Mantener esa separación por tipo de documento.

## No Analog Found

Todo archivo tiene análogo exacto de formato. Los **bloques de código NUEVOS** que las guías narran no tienen precedente en el corpus (ni en demo-cine) — el planner los toma de `02-RESEARCH.md`, ya verificado contra fuentes oficiales:

| Bloque nuevo (vive dentro de guia-05..08) | Razón sin análogo | Fuente |
|---|---|---|
| `app/security.py` (pwdlib hash/verify, `create_access_token`, `get_current_user`/`get_current_admin`, `OAuth2PasswordBearer`) | Ningún repo del ecosistema tiene auth; el tutorial FastAPI no usa capas | 02-RESEARCH.md Pattern 1-3 (tutorial adaptado a reglas de dependencia) |
| Stores Zustand `useAuthStore`/`useCarroStore` con `persist`/`partialize` | Estado de cliente no existía en fase 1 | 02-RESEARCH.md Pattern 5 (docs pmndrs/zustand) |
| `components/RequireAuth.tsx` + returnTo (`Navigate state={{from: location}}`) | Rutas protegidas no existían | 02-RESEARCH.md Pattern 6 (ejemplo oficial RR, exports verificados tarball 8.4.0) |
| Interceptor 401 + `apiPostForm` en `lib/api.ts` | Extiende la base vigente con código nuevo | 02-RESEARCH.md Pattern 4 (base VERIFIED guia-04:750-776) |
| `.env.example` con `ADMIN_*`/`CLIENTE_*` | Primera aparición del `.env` en las guías (guia-01 solo muestra el `.gitignore` que lo excluye, líneas 315-317) | 02-RESEARCH.md Pattern 7 + Pitfall 12 (placeholders, jamás credenciales literales) |

## Metadata

**Analog search scope:** `D:/Repos/demo-carro/docs/` completo (19 archivos git-trackeados, listados con `git ls-files docs/`) + `README.md` raíz + `.planning/phases/02-.../02-UI-SPEC.md`. Referencia externa demo-cine NO fue necesaria esta vez: todo el formato ya está establecido in-repo por la fase 1 (a diferencia de 01-PATTERNS.md, que usó demo-cine como análogo de formato).
**Tracked-source gate:** todos los análogos nombrados verificados con `git ls-files` (salida no vacía por archivo): README.md, docs/README.md, docs/02_requerimientos.md, docs/03_diseno.md, docs/04_arquitectura/{README.md, contrato_api.yaml, adr/007-api-first.md}, docs/05_desarrollo/{README.md, guia-01..04}. Ninguna ruta mirror/gitignored emitida.
**Files scanned:** 12 análogos leídos esta sesión — 9 completos (adr/007 54L, contrato 203L, 02_requerimientos 223L, 03_diseno 367L, 04_arquitectura/README 215L, 05_desarrollo/README 43L, docs/README 26L, README raíz 90L, guia-01 434L, guia-03 636L, guia-04 1032L, 02-UI-SPEC 299L) + 3 lecturas dirigidas no solapadas de guia-02 (1-40, 214-303, 428-517) — más 01-PATTERNS.md y 02-CONTEXT/02-RESEARCH del phase dir.
**Pattern extraction date:** 2026-09-29
