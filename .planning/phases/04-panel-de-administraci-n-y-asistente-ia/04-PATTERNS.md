# Phase 4: Panel de administración y asistente IA - Pattern Map

**Mapped:** 2026-09-30
**Files analyzed:** 14 (7 extensiones de documentos existentes + 3 ADRs nuevos + 4 guías nuevas `guia-12+`; la partición exacta en sub-guías es discreción del planner bajo el orden D-62 — este mapa clasifica por unidad funcional)
**Analogs found:** 14 / 14 con análogo exacto in-repo (el corpus de fases 1-3 está completo: cada doc nuevo/extendido tiene su análogo git-trackeado, la mayoría "sí mismo" por tercera extensión in-place consecutiva)

## Nota de alcance: repo guide-only, contrato primero, UI-SPEC ya aprobado (leer antes de planificar)

`D:/Repos/demo-carro` sigue **guide-only (D-17, ADR-008)**: la fase 4 entrega SOLO documentos. Cuatro reglas que ordenan los planes:

1. **Orden D-62 (locked):** (A) contrato 0.4.0 + ADRs 015+ PRIMERO (D-15, API-first — junto con docs 02/03 de la etapa, como la fase 3 agrupó su Grupo B) → (B) panel admin completo (backend → SPA) → (C) asistente IA (backend → burbuja SPA) → (D) Gran verificación final de fase 4. El admin va antes que la IA: el panel no depende del asistente y la burbuja reusa las ProductCard del catálogo.
2. **No hay spike en esta fase.** La pieza de riesgo (structured output en google-genai 2.25, D-56) ya fue firmada con evidencia por `04-RESEARCH.md` contra el README del tag `v2.25.0` (Patterns 1-3, verbatim). El ADR del asistente cita esa evidencia — mismo patrón de ADR-012 citando `03-SPIKE-RETORNO.md`, pero la fuente ya vive en RESEARCH, no en un doc de spike nuevo.
3. **`04-UI-SPEC.md` (approved, mismo phase dir) es el contrato de pantallas y copy de las guías 12+**: pantallas 10-14 con clases Tailwind exactas, tabla de rutas (líneas 148-154), montaje en `main.tsx` con dos ramas de layout (158-169), Copywriting Contract completo (247-276) y defaults fijados en modo auto (≤5 stock, 500 chars, 10 mensajes, 3 cards — líneas 26-29, a confirmar como RN por el planner). Las guías no inventan UI: traducen ese contrato a pasos.
4. **UAT runtime delegado** en `D:/Repos/maura-uat` (AGENTS.md) sobre la app construida hasta guia-11 (con órdenes reales de los 4 flujos y cuentas seed admin/clienta). **Open Question 1 de RESEARCH:** la `GEMINI_API_KEY` del happy path NO existe en maura-uat — el planner deja esa fila de UAT tras `checkpoint:human-verify`; la ruta de degradación (sin key → 503 + burbuja "no disponible") y el grep del build se verifican sin key.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `docs/04_arquitectura/contrato_api.yaml` (EXTENDER 0.3.0→0.4.0, ANTES de las guías) | contract (OpenAPI) | request-response | sí mismo (778 líneas: header 1-8, tabla errores 30-40, tags 48-60, `/api/admin/estado` 492-536 a reemplazar D-54, `security: []` de retorno 589-604 como patrón del endpoint público del asistente) | exact (in-place, tercera subida de versión) |
| `docs/02_requerimientos.md` (EXTENDER) | doc requerimientos | — | sí mismo (392 líneas: bloque alcance etapa 3 53-58, filas P7/P8 §13 349-350, series vigentes RF-18:118 / RNF-07:132 / RN-13:150 / HU-11:252-259) | exact (in-place) |
| `docs/03_diseno.md` (EXTENDER) | doc diseño | — | sí mismo (1002 líneas: §2.3.5 `activo` 155-158 que D-52 implementa, DFD 11.0 477-495, pantallas 8-9 851-938, trazabilidad §5 944-984) | exact (in-place) |
| `docs/04_arquitectura/adr/015-*.md` (NUEVO: panel admin protegido por rol en los dos tiers, D-55) | doc (decisión) | — | `adr/011-roles-desde-el-primer-token.md` (la base del guard, citado por CONTEXT) + `adr/012` (formato más reciente) | exact (formato) |
| `docs/04_arquitectura/adr/016-*.md` (NUEVO: máquina de estados de pedidos, transición admin única, D-50) | doc (decisión) | — | `adr/013-orden-nace-al-pagar-stock-al-aprobar.md` (la máquina que este ADR extiende) + `adr/014` (formato) | exact (formato) |
| `docs/04_arquitectura/adr/017-*.md` (NUEVO: asistente IA mini-RAG, key solo backend, degradación D-56/D-60/D-61) | doc (decisión) | — | `adr/012-retorno-de-webpay.md` (el ADR que cita evidencia externa firmada — mismo patrón con la evidencia de RESEARCH vs README v2.25.0) | exact (formato) |
| `docs/04_arquitectura/README.md` (EXTENDER) | doc índice/arquitectura | — | sí mismo (250 líneas: fila "IA (fase 4)" placeholder 122, árbol 134-178, índice ADRs 201-216) | exact (in-place) |
| `docs/05_desarrollo/guia-12-*.md` (NUEVO: backend del panel — CRUD productos, transición pedidos, métricas) | doc (guía paso a paso) | — | `guia-05-cuentas-backend.md` (1108 líneas, la guía backend de fase 2: Settings 119-137, get_current_admin 459-468, lección responses 586-589) + `guia-09` (la de fase 3: repos sin commit innecesario, main.py 1194-1216) | exact (estructura) |
| `docs/05_desarrollo/guia-13-*.md` (NUEVO: SPA del panel — `/admin` layout, RequireAdmin, 3 pantallas) | doc (guía paso a paso) | — | `guia-11-pedidos-cierre.md` (lista useQuery 88-115, BADGES 77-86, navbar condicionado 358-371, rutas 408-414) + `guia-10` (mutación + CTA 179-194) | exact (estructura) |
| `docs/05_desarrollo/guia-14-*.md` (NUEVO: asistente backend — service Gemini, key opcional, wrapper errores) | doc (guía paso a paso) | — | `guia-09` Paso 5 `services/webpay.py` (460-547: el ÚNICO importador del SDK externo + traducción de errores — el patrón exacto de `services/asistente.py`) | exact (estructura) |
| `docs/05_desarrollo/guia-15-*.md` o fusión en la 14 (NUEVO: burbuja SPA + Gran verificación final de fase 4) | doc (guía de cierre) | — | `guia-11` §Gran verificación final (469-515) + `guia-10` rutas main.tsx (233-248) | exact (estructura) |
| `docs/05_desarrollo/README.md` (EXTENDER) | doc índice | — | sí mismo (58 líneas: tabla 24-36, blockquote 38-41, mapa mental 43-58) | exact (in-place) |
| `docs/README.md` (EXTENDER) | doc índice | — | sí mismo (26 líneas: fila 4 línea 18 "14 ADRs", fila 5 línea 19 "guías 1-11") | exact (in-place) |
| `README.md` raíz (EXTENDER) | doc índice | — | sí mismo (92 líneas: filas 41-42, "las 14 decisiones" línea 54, stack 70-74 "Google Gemini (fase 4)") | exact (in-place) |

*Numeración de guías y de ADRs: títulos y partición exacta son discretion del planner (CONTEXT §Claude's Discretion); D-62 fija el orden funcional. Fase 3 partió su feature mayor en backend (9) / SPA (10) / cierre (11) — el espejo natural para el admin es 12/13 y para el asistente 14/(15), con la Gran verificación final en la última guía de la fase (como guia-08 y guia-11 la llevaron).*

## Pattern Assignments

### Grupo A — Requerimientos y diseño de la etapa 4

#### `docs/02_requerimientos.md` (EXTENDER)

**Analog:** sí mismo (392 líneas, leído completo esta sesión).

**Series vigentes a continuar** [VERIFIED: RF-18 línea 118, RNF-07 línea 132, RN-13 línea 150, HU-11 líneas 252-259]: los nuevos llegan como **RF-19+** (CRUD productos ADMN-01, stock+alerta ADMN-02, gestión pedidos ADMN-03, métricas ADMN-04, chat/burbuja AIAS-01, recomendación validada AIAS-02), **RNF-08+** (candidato: dependencia del servicio Gemini free tier con degradación — espejo de RNF-07 de Webpay, línea 132), **RN-14+** (candidatos locked por CONTEXT/UI-SPEC: umbral stock bajo ≤ 5 como constante del backend D-53, transición única admin PENDING→CANCELLED D-50, topes del chat 500 chars/10 mensajes D-58/D-59), **HU-12+** (la dueña gestiona; la clienta pregunta a la asesora).

**Formato exacto de un RF con origen** (línea 112, replicar):

```markdown
- **RF-12:** El sistema debe recalcular el pedido completo al crear la orden: el backend
  consulta el catálogo vigente por cada par `{producto_id, cantidad}` del carro... *(CART-03, P6)*
```

**Puntos que cambian de estado:**
- §1 contexto (13-26): el párrafo narra la etapa 4 (panel + asesora) — hoy termina en la etapa 3 (líneas 17-20).
- §2 alcance: nuevo bloque "**Dentro del alcance de la etapa 4**" después del de etapa 3 (53-58); las filas P7/P8 del bloque "Fuera del alcance de las etapas 1 a 3" (líneas 61-62 verbatim: `Panel de administración de productos, stock y pedidos (P7) → **etapa 4**.` / `Asesora de venta con recomendación de aromas (P8) → **etapa 4**.`) se mudan al bloque nuevo — igual que la fase 3 hizo con P6.
- §3 actor Admin (línea 76): su descripción hoy dice "su panel de gestión llega en la etapa 4" — se actualiza; el blockquote 78-82 ("la asesora de venta (P8) y el panel completo... siguen siendo alcances de etapas futuras") se retira o invierte.
- **RN-04 (líneas 141-142)** — punto delicado: dice "El catálogo de esta etapa es de **solo lectura**... crear, editar y desactivar llegan con el panel de administración de la etapa 4". Con el panel construido, la regla cambia de estado. Mecánica de fases previas: nunca renumerar; el planner elige la forma honesta (reescribir el alcance de RN-04 a "las clientas no escriben el catálogo; la escritura es del admin (etapa 4)" o dejar el texto histórico y que la RN nueva lo supersede citándolo) — misma decisión editorial que la tabla de errores del contrato enfrentó con el 400 en fase 3.
- §9 procesos (288-298): nuevos numerados 12+ (gestionar productos/stock, anular pedido huérfano, ver métricas, conversar con la asesora) — insumo de los DFDs de docs/03.
- §10 entradas (304-312): filas nuevas — editor de producto (familia enum RN-01, precio/stock ≥ 0), transición de estado, mensaje+historial del chat con topes.
- §12 pantallas (325-333): ítems **10-14** (productos admin, pedidos admin, métricas, no autorizado, asesora/burbuja) — numeración propuesta por `04-UI-SPEC.md` §Nota para el planner (línea 345).
- §13 trazabilidad, filas P7/P8 (líneas 349-350 verbatim): `| P7 Panel de administración | *(llegan con la etapa 4: ADMN-01..04)* | Etapa 4 |` → mapeo real a los RF/RN/HU nuevos (igual que fase 3 hizo con P6 en línea 348).
- §14 aprobación (379-384): nuevo bloque "**Etapa 4 — panel de administración y asesora (documentada el 2026-09-__)**" con la misma tabla de firmas.
- §8 modelo de datos (265-269): **sin entidades nuevas** (D-58: cero tablas para el asistente) — la nota del bloque puede decirlo explícitamente: la etapa 4 no toca el esquema.

---

#### `docs/03_diseno.md` (EXTENDER)

**Analog:** sí mismo (1002 líneas, leído completo esta sesión).

- **§2 datos SIN cambios de esquema**: cero entidades nuevas (D-58). La nota "Lectura del diagrama" (73-83) puede ganar su párrafo de etapa 4. **§2.3.5 `activo` (155-158 verbatim)** ya diseñó el soft delete que D-52 implementa: *"Desactivar un producto lo saca del catálogo sin destruir su historial... Ocultar es reversible; borrar no"* — la decisión nueva lo cita en vez de reinventarlo.
- **§2.3 decisiones numeradas** (hoy 1-14, líneas 133-217): continuar con **15+** — candidatos: la máquina de estados completa con su única transición manual admin (D-50), el umbral de stock bajo como constante del backend distinta del umbral de tienda (D-53 + Pitfall 6), el mini-RAG honesto con validación de ids (D-56), la degradación sin key (D-61). El blockquote final (236-245) gana su párrafo de etapa 4 (ADRs 015-017).
- **§3.1 contexto (251-277)**: agrega **Gemini** como segunda entidad externa — el mermaid `flowchart LR` gana `GEM["Gemini (asesora IA)"]` con su arco ida/vuelta, igual que Webpay entró en fase 3 (265, 276-277). El bloque de texto (253-257) narra: la etapa 4 suma el segundo servicio externo — y este es de tipo nuevo (request-response JSON del backend, sin redirecciones).
- **§3.2 almacenes (280-294)**: sin almacenes nuevos; nota posible: el historial del chat vive en memoria del componente (D-58), no en A2 ni BD.
- **§3.3-3.13 DFDs 1.0-11.0** → continuar con **12.0+**: gestionar catálogo (admin escribe D1 por primera vez fuera del seed), anular pedido huérfano (UPDATE condicional sobre D3 — espejo del 10.0), calcular métricas (agregación de solo lectura sobre D3+D1), conversar con la asesora (admin NO: visitante → validar topes → system prompt con D1 activo → Gemini → validar ids contra D1 → respuesta+cards). Formato por DFD (verbatim del 11.0, 479-487): flowchart TD con almacenes `D1[("D1 Productos")]` + bloque "**Reglas del proceso:**" (489-495).
- **§4 pantallas 10-14**: el contenido YA ESTÁ especificado por `04-UI-SPEC.md` (pantallas 10-14, líneas 178-232) — el doc de diseño lo traduce al formato vigente. Formato obligatorio por pantalla (910-912 verbatim):

```markdown
**Origen:** RF-17, HU-11, RN-11 · **Estados:** carga (filas esqueleto) /
error de carga (mensaje con la causa y Reintentar) / vacío ("Todavía no
tienes pedidos" + botón Ver catálogo que reemplaza la página)
```

  ...más wireframe ASCII (como 914-927) y viñetas con las decisiones (como 929-938). La regla §4.1 (513-514) "cada pantalla declara sus estados de carga, error y vacío" aplica con fuerza: la burbuja declara 503/429/red (UI-SPEC 227-231) y el panel declara empty/error por tabla (UI-SPEC 288-300).
- **§5 trazabilidad (944-984)**: una fila por RF/RN/HU nuevo de la etapa 4.

---

### Grupo B — Contrato 0.4.0, ADRs 015+ y README de arquitectura (ANTES de las guías)

#### `docs/04_arquitectura/contrato_api.yaml` (EXTENDER — 0.3.0 → 0.4.0)

**Analog:** sí mismo (778 líneas, leído completo esta sesión).

**Cambios puntuales con línea exacta:**
- `info.version: 0.3.0` (línea 13) → `0.4.0`.
- `info.description` (19-26): la nota de autenticación se extiende — los paths `/api/admin/*` nuevos exigen rol admin; `/api/asistente` es público como el retorno.
- **Tabla de convención de errores (30-40)**: **agregar fila 503** (servicio externo del asistente no disponible — degradación D-61, sin key o Gemini caído) y **fila 429** (cuota del free tier de Gemini, traducida amable). La fila 409 (línea 39, "Conflicto (email ya registrado)") gana su segundo uso: **transición ilegal de pedido** — RESEARCH Open Question 3 recomienda 409 con detail claro ("Ese pedido ya no está en curso"). Verbatim actual del encabezado:

```yaml
    **Convención de errores:**

    | Código | Significado | Estado |
    |---|---|---|
```

- **tags (48-60)**: el tag `Administración` (57-58, hoy `Endpoints protegidos por rol admin (AUTH-03, D-33)`) se reescribe citando ADMN-01..04; nuevo tag `Asistente` (o `Chat` — discretion) citando AIAS-01..03.
- **schemas**: la convención es `description` citando requisito + description por campo + `example` + `required` (patrón ProductoResumen 85-112). Nuevos: `ProductoCrear`/`ProductoEditar` (familia enum cerrado 106, precio/stock enteros ≥ 0, imagen como texto D-51; **sin campo `activo` en el editor** — el toggle es escritura propia, UI-SPEC 185), `PedidoTransicion`, `Metricas`, `ChatMensaje`/`ChatRespuesta`. **Lección estructural heredable de CheckoutCreate (185-212)**: aquel schema demostró una regla por AUSENCIA de campo (ningún precio de entrada, CART-03); el editor de productos hace lo mismo con la allow-list de campos editables (mass assignment, Security Domain de RESEARCH).
- **paths**: `/api/admin/estado` (492-536) **se RETIRA y se reemplaza** por los paths reales (D-54) — la subida a 0.4.0 NARRA la evolución en la description de los paths nuevos o en `info.description` (Pitfall 7: jamás en silencio; las guías 05/06 no se re-editan). El patrón de TODOS los endpoints admin nuevos es el 403 del endpoint demo (529-536 verbatim):

```yaml
        '403':
          description: Con sesión, pero sin rol admin
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              example:
                detail: Requiere rol admin
```

- **El endpoint del asistente copia el `security: []` del retorno** [VERIFIED líneas 602 (GET) y 661 (POST): `security: []` con la explicación en description 594-601 "Público por diseño"] — mismo contraste pedagógico, segunda aparición (D-59).
- **Cada response nueva declarada en el contrato Y en el `responses={...}` del router de la guía** (Pitfall 5, lección guia-05:586): el 503/429 del asistente y el 409 de transición deben aparecer en `/docs` o la fila contrato ↔ `/docs` de la Gran verificación final canta un desvío falso.

---

#### `docs/04_arquitectura/adr/015..017-*.md` (NUEVO — 3 ADRs)

**Analog:** `adr/012-retorno-de-webpay.md` (97 líneas, leído completo) y `adr/014-snapshot-de-precio-en-la-orden.md` (84 líneas, leído completo) — los más recientes; ADR-011 es la base temática del 015.

**Esqueleto obligatorio** (ADR-012 líneas 1-5 + secciones fijas, idéntico en 014):

```markdown
# ADR-015 — <Decisión en una frase>

- **Estado:** Aceptada
- **Fecha:** 2026-09-__ (fecha de la fase 4)
- **Resuelve:** <pregunta de decisión>

## Contexto
## Opciones consideradas        → tabla | Opción | A favor | En contra | (3 opciones A/B/C)
## Decisión                     → "**Opción X.**" + reglas numeradas
## Consecuencias                → **Positivas** / **Negativas (honestas)**
## Para conversar en clase      → 3 preguntas numeradas
```

**Contenido candidato (discretion CONTEXT):**
- **015 — Panel admin protegido por rol en los dos tiers (D-55):** `RequireAdmin` como espejo UX del 403 (base ADR-011: el claim de rol viaja desde el primer token); el guard SPA NO es la seguridad — `get_current_admin` en CADA endpoint lo es (lección D-33 hecha patrón). Consecuencia negativa honesta candidata: dos niveles de "quién puede" que deben mantenerse en sync.
- **016 — Máquina de estados de pedidos con transición admin única (D-50):** los 4 estados existentes sin nuevos; transiciones legales documentadas con dueño (el flujo de pago posee las suyas — ADR-012/013; el admin tiene exactamente UNA: PENDING→CANCELLED, la gestión de huérfanas que D-48/D-49 dejaron para esta fase); cancelar PENDING no toca stock (D-35); PAID terminal en v1 (refund = ADMN-05 v2). El ADR-013 y RN-11/RN-12 son su contexto; cita la fila que guia-11:28 y docs/02 RN-11 dejaron prometida.
- **017 — Asistente IA con mini-RAG y key solo en backend (D-56/D-60/D-61):** catálogo activo completo en el system prompt (12 SKU caben); structured output JSON + validación de ids contra BD (la muralla anti-alucinación es del servidor); endpoint público deliberado; key por `.env` opcional con degradación 503 (NO fail-fast, contraste explícito con `secret_key` de fase 2). **Este ADR cita la evidencia externa firmada** — `04-RESEARCH.md` Patterns 1-3 contra el README del tag v2.25.0 (`response_json_schema`, `errors.APIError`, env var auto-pickup) — replicando el patrón de ADR-012 citando `03-SPIKE-RETORNO.md` (012:18-19, link relativo `.md`), y narra el drift docs-web/SDK-pinneado como lección (Pitfall 1).

**Referencias cruzadas:** links relativos entre ADRs (012:55-56 cita ADR-009/013) — 015 cita 011; 016 cita 013 y el futuro panel; 017 cita 007 (contrato) y 009 (dónde viven los secretos).

---

#### `docs/04_arquitectura/README.md` (EXTENDER)

**Analog:** sí mismo (250 líneas, leído completo esta sesión).

- **§3 Stack**: la fila placeholder (línea 122 verbatim) `| IA (fase 4) | **google-genai** | SDK oficial de Gemini; la API key vive solo en el backend — llega en su fase |` se convierte en fila real `google-genai 2.25.0 (pin >=2.25,<3)` citando ADR-017 — igual que la fila "Pago (fase 3)" lo hizo en fase 3 con ADR-012/013.
- **§4 árbol (134-178)**: agregar con el comentario de una línea por archivo (estilo línea 156 `services/webpay.py  # wrapper ... el ÚNICO lugar que importa transbank`): `routers/admin.py` (SU comentario cambia: hoy línea 159 dice `# /api/admin/estado — protegido por rol admin (D-33)` → CRUD real de administración), `routers/asistente.py`, `services/asistente.py  # el ÚNICO lugar que importa google.genai`, `repositories/producto.py`/`pedido.py` extendidos (CRUD admin, transiciones, agregaciones de métricas), `components/RequireAdmin.tsx`, `lib/badges.ts` (BADGES a módulo propio — tercera consumidora, UI-SPEC 138), `features/admin/` (LayoutAdmin + 3 sub-pantallas + NoAutorizado), `features/asistente/` (BurbujaAsesora). Mantener intacto el disclaimer guide-only (128-132).
- **Reglas de dependencia 1-6 (181-195)**: no cambian — la regla 6 ("features sin imports cruzados sin razón") gana su SEGUNDA excepción narrada (ProductCard del catálogo reusada en el chat, patrón D-46 igual que `VoucherPedido` en guia-11); la regla 3 (services sin HTTP) es la que el wrapper del asistente respeta (traduce errores del SDK a señales de dominio; el 503/429 lo decide el router).
- **§5 índice de ADRs (201-216)**: 3 filas nuevas (015, 016, 017) con el formato `| [ADR](adr/NNN-slug.md) | Decisión | Resuelto por |`.

---

### Grupo C — Guías 12+ (orden D-62: admin backend → admin SPA → asistente backend → burbuja + cierre)

> Regla transversal: cada guía replica la **estructura canónica** (ver Shared Patterns) y abre con la lista de prerrequisitos por número de guía ("Necesitas: las guías 1 a N completas...", como guia-10:12-17 y guia-11:12-17).

#### `guia-12-*` (NUEVO — backend del panel admin)

**Analog:** `guia-05-cuentas-backend.md` (mapa estructural por lectura dirigida esta sesión) + `guia-09-ordenes-webpay.md` (1614 líneas, leído completo — la guía backend más reciente).

**Correspondencia paso a paso con guia-05/guia-09:**
- **Instalación**: guia-09 Paso 1 (35-72) narró "un paquete, cero `.env` nuevo" — el admin NO instala nada (todo el stack ya está); el paso de instalación real es de la guía del asistente.
- **Schemas espejo del contrato**: guia-09 Paso 3 (214-318) "abro `contrato_api.yaml` ... y escribo sus schemas en Pydantic" — el admin espeja el 0.4.0 (`ProductoCrear/Editar`, `PedidoTransicion`, `Metricas`) con la lección de allow-list (sin `model_dump` ciego sobre el ORM).
- **Repositories**: guia-09 Paso 4 (321-457) — el repo de productos gana escrituras admin (crear/actualizar por id, toggle `activo`, listado TODOS incluidos inactivos D-52); el de pedidos gana `todos()` (el admin ve todo el mundo, sin filtro de dueña — contraste con `por_usuario`) y la **transición validada**: UPDATE condicional `WHERE estado == pending` (la MISMA muralla del guard ya-PAID de guia-09:887-897, aplicada a la transición admin — rowcount 0 → 409, D-50).
- **Services**: guia-09 Paso 6/7 (559-924) — `AdminService`/`MetricasService` sin conocer HTTP; la señal `TransicionIlegal` la traduce el router a 409 (igual que `CarroNoComprable` → 400 en guia-09:999-1003). Las métricas son agregaciones SQL en el repo (research Ejemplo D: sum PAID, group_by estado, top 5 por líneas snapshot, count stock bajo con `activo == True`).
- **Routers bajo `get_current_admin`** [VERIFIED guia-05:459-468 verbatim — la dependencia existe desde fase 2]:

```python
def get_current_admin(
    current: Usuario = Depends(get_current_user),
) -> Usuario:
    """Dependencia: la sesión actual debe tener rol admin — o 403."""
    if current.rol != RolUsuario.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requiere rol admin",  # el detail del 403 del contrato
        )
    return current
```

  ...con `responses` declaradas por endpoint (lección guia-05:586-589: "cada `HTTPException` lanzada a mano NO aparece en OpenAPI si no se declara") — el 409 de la transición incluido.
- **main.py**: guia-09 Paso 9 (1194-1216) — solo `include_router` + `version="0.4.0"` (subir la versión que la app declara de sí misma, misma coherencia ADR-007).
- **Prueba de fuego**: guia-09 Paso 10 (1235-1456) — mini-verificaciones con httpx una línea: 200 admin vs 403 clienta en cada path nuevo, el 409 de anular dos veces, el soft delete (inactivo desaparece del catálogo público pero el pedido viejo conserva su snapshot, D-52/D-36).

---

#### `guia-13-*` (NUEVO — la SPA del panel: `/admin`, RequireAdmin, 3 pantallas)

**Analog:** `guia-11-pedidos-cierre.md` (636 líneas, leído completo) + `guia-10-retorno-voucher.md` (847 líneas, leído completo).

- **`RequireAdmin` extiende `RequireAuth`** [VERIFIED guia-06:961 verbatim: "`RequireAuth` con `Navigate state={{ from: location }} replace` y el login que vuelve con `location.state?.from?.pathname ?? \"/\"`: el returnTo genérico (D-32)"] — el sketch exacto de RESEARCH Pattern 4 lo implementa: sin sesión delega en `<RequireAuth />`; con sesión sin rol → `<NoAutorizado />` SIN expulsar al login (le falta permiso, no identidad). El 🧠 cita ADR-011 y D-33 (el espejo frontend del 403).
- **Montaje en `main.tsx`** — patrón guia-10 Paso 3 (233-248) y guia-11 Paso 4 (408-414) con la novedad del layout intermedio: rama `<Route element={<RequireAdmin />}>` FUERA del Layout de tienda con `<Route path="/admin" element={<LayoutAdmin />}>` + hijos index/pedidos/metricas (UI-SPEC 158-169 verbatim ya trae el bloque completo).
- **Pantalla de lista**: guia-11 Paso 1 (61-201) es el patrón de tabla/lista con `useQuery` + skeleton `animate-pulse` + error puerto 8000 + Reintentar + empty state — AdminProductos/AdminPedidos lo replican con tabla semántica (UI-SPEC pantalla 10-11).
- **BADGES a módulo propio**: guia-11:77-86 dejó la tabla BADGES con la nota exacta [VERIFIED]: *"Si un día nace una tercera consumidora, baja a un módulo propio — hoy son dos y copiarla una vez más es más honesto que adelantarse"* — el panel ES la tercera consumidora: la guía mueve BADGES a `src/lib/badges.ts` y las tres consumidoras importan de ahí (UI-SPEC 138; el refactor toca el código del alumno, jamás re-edita guia-10/11).
- **El navbar gana "Panel" (solo admin)**: patrón guia-11 Paso 3 (345-376) — el link condicionado por `usuario.rol === "admin"` dentro del bloque con sesión, ANTES del email (D-55; espejo de "Mis pedidos" D-47).
- **Mutaciones (toggle, editor, anular)**: guia-10 Paso 2 (146-194) — `useMutation` + `disabled={isPending}` + label en gerundio; éxito = dato actualizado en el lugar + `invalidateQueries` (la queryKey `productos` compartida con el catálogo público reacciona sola, UI-SPEC 187). **"Anular" con confirmación en dos pasos inline**: patrón "Vaciar carro" de fase 2 (UI-SPEC 196 lo fija).
- **Editor inline como estado de la pantalla 10** (`editando: producto | "nuevo" | null`, sin ruta propia): sin precedente directo en el corpus — la forma vive completa en UI-SPEC 183-189 (campos, helpers, validación espejo del 422).

---

#### `guia-14-*` (NUEVO — el asistente en el backend)

**Analog:** `guia-09` Paso 5 `services/webpay.py` (460-547) — el patrón estructural exacto: **UN ÚNICO archivo importa el SDK externo**, habla el vocabulario del negocio y traduce TODOS los errores del SDK a señales de dominio antes de que crucen la frontera.

**La correspondencia wrapper por wrapper** [VERIFIED guia-09:497-547 verbatim]: como `services/webpay.py` es el único que escribe `import transbank` y su `commit` devuelve `None` ante `TransbankError`/errores de red, `services/asistente.py` es el único que escribe `from google import genai` y su llamada atrapa `errors.APIError` → 429 (cuota, copy amable sin cifras — concern abierto) / 503 (todo lo demás), jamás un 500 crudo (D-61, patrón IN-06). El código fuente firmado: RESEARCH Patterns 1-3 (verbatim del README v2.25.0).

- **Paso de instalación + key del alumno (D-60):** `uv add "google-genai>=2.25,<3"` (RESEARCH Installation) + crear SU key gratis en Google AI Studio — mismo patrón de "paso del alumno, nada compartido" que D-08 con las fotos y que guia-05:92-101 con las claves demo: la guía versiona una PLANTILLA `.env.example` (agrega `GEMINI_API_KEY=`) y jamás escribe una key real.
- **Settings con degradación (D-61)** [VERIFIED guia-05:119-137 — el patrón Settings]: `gemini_api_key: str | None = None` con su comentario de etapa, en CONTRASTE explícito con `secret_key: str  # SIN default: sin .env la app no parte (fail-fast)` (guia-05:130) — el 🧠 de la guía hace esa comparación: el asistente es opcional, la firma de sesiones no. Client construido lazy/guardado para que la app arranque sin key.
- **Router público**: `security: []` espejo del retorno (contrato 589-604); Pydantic valida topes (500/10, RN nueva → 422); `responses` declara 200/422/**503/429** (Pitfall 5).
- **Mini-RAG + validación de ids (D-56)**: system prompt con catálogo ACTIVO por request; `Recomendacion` Pydantic con `.model_json_schema()` al `GenerateContentConfig`; ids filtrados contra BD antes de responder (RESEARCH Pattern 6 + Ejemplo A).
- **Mini-verificación sin key (degradación)**: comentar la key del `.env`, `GET/POST /api/asistente` → 503 amable y la tienda sigue 100% operativa — verificable sin depender del usuario (Open Question 1).

---

#### `guia-15-*` o cierre de la 14 (NUEVO — la burbuja en la SPA + Gran verificación final de fase 4)

**Analog:** `guia-11` §Gran verificación final (469-515) + `guia-10` (mutación, rutas).

- **La burbuja (`BurbujaAsesora`) en el Layout de la tienda**: visible en páginas públicas, NO en `/admin` (rama de layout propia). UI-SPEC pantalla 14 (218-231) trae el contrato completo: botón flotante "Pregúntale a Maura", panel `fixed bottom-20 right-6` con header/mensajes/input, historial stateless en estado del componente (D-58), bienvenida local (no gasta cuota), `useMutation` por request (no useQuery), burbuja `animate-pulse` en vuelo, product cards = **reuso literal de `ProductCard`** (import cruzado con razón, patrón D-46 — la segunda excepción de la regla 6).
- **Estados del chat**: 503 → "La asesora no está disponible en este momento." + Reintentar; 429 → "recibiendo muchas consultas" SIN cifras; red → familia puerto 8000 (UI-SPEC Copywriting 271-273 verbatim).
- **Gran verificación final de fase 4** — formato guia-11 (469-515): tabla numerada `| # | Verificación | Origen |` con cada fila citando CS/RF/HU/ADR de la etapa, y la **fila final contrato 0.4.0 ↔ `/docs`** (los paths nuevos, el 503/429/409 declarados, el endpoint público del asistente, **Authorize probado con la cuenta admin del seed** — ahora authoriza de verdad contra el CRUD completo). **Novedad fija de esta fase: la fila del grep del build** (AIAS-03, D-61): `grep -r "GEMINI_API_KEY" dist/` → **cero coincidencias**, con el comando por shell (Git Bash y PowerShell — Pitfall 8) y DESPUÉS de `npm run build`. Verbatim del cierre a replicar (guia-11:501-505): *"**Cualquier diferencia entre el panel y el contrato es un desvío** — o el código corrige, o el contrato se versiona y se aprueba de nuevo; jamás cambia en silencio... este mismo mecanismo se repite al final de cada fase del proyecto."* Más sugerencia de commit de cierre (guia-11:507-515, adaptada: "Cumple el contrato OpenAPI 0.4.0 ... respeta los 17 ADRs").
- **El "Siguiente" de guia-11 se cobra**: su cierre (guia-11:631-636) ya anuncia esta fase — la guía nueva referencia las huérfanas PENDING que guia-11 dejó visibles y las anula de verdad (D-50); la clienta las ve CANCELLED en su historial sin editar guia-11.

---

### Grupo D — READMEs de estado (D-13/D-18: el estado avanza por fase)

#### `docs/05_desarrollo/README.md` (EXTENDER)

**Analog:** sí mismo (58 líneas). Tabla (24-36) gana filas 12+ con el estilo "Construye" de una frase (ej. fila 11: "El historial de pedidos y la Gran verificación final de la fase 3"). Blockquote (38-41) se actualiza: "La fase 4 completa sus guías (12-14/15: panel admin, asistente). La guía siguiente llega con la fase 5 (despliegue)". Mapa mental (43-58) suma la capa de IA (el segundo servicio externo: request-response JSON, sin redirecciones — contraste con Webpay).

#### `docs/README.md` (EXTENDER)

**Analog:** sí mismo (26 líneas). Fila 4 (línea 18): "`04_arquitectura/` (documento + 14 ADRs + `contrato_api.yaml`)" → **17 ADRs**. Fila 5 (línea 19): `🚧 Parcial (guías 1-11 listas; continúa en fases 4+)` → `(guías 1-14/15 listas; continúa en fases 5+)`.

#### `README.md` raíz (EXTENDER)

**Analog:** sí mismo (92 líneas). Fila 4 (41): "Arquitectura + 14 ADRs + contrato OpenAPI" → 17. Fila 5 (42) igual que docs/README. Línea 54 "las 14 decisiones de arquitectura" → 17. Stack (70-74): "Google Gemini (fase 4)" pasa de promesa a construido, en el tono telegráfico vigente (como "Webpay Plus en ambiente de integración: pago sandbox operativo..." lo hizo en fase 3).

---

## Shared Patterns

### Estructura canónica de guía (obligatoria en guia-12+)

**Source:** `guia-09`/`guia-10`/`guia-11` completas — la secuencia más reciente del corpus.
**Apply to:** todas las guías nuevas. Secuencia fija: (1) header `# Guía N — Título` + blockquote `**Qué construirás hoy:** / **Al terminar tendrás:** / **Necesitas:**` (guia-11:3-17, con prerrequisitos por número de guía); (2) `## Los términos de hoy (antes de copiar nada)` tabla término/frase (guia-11:21-29 — candidatos fase 4: rol/guard, soft delete, umbral de stock bajo vs últimas unidades, KPI, system prompt, structured output, mini-RAG, degradación, rate limit); (3) pasos `## Paso N —` con 🧠 **El desarrollador piensa:** en cursiva citando ADR/RN/D, código con nombre de archivo en negrita y docstring de módulo, ✅ **Mini-verificación** con comando + output esperado; (4) `## ❌ El error que este archivo evita` con pares ❌/✅ (guia-11:519-573 — candidatos: la key en `VITE_`, validar ids en el frontend, fail-fast sin key, retry casero sobre el SDK, un solo umbral de stock confundido, 409/422 sin declarar en responses); (5) `## ✅ Verificación de la guía N`; (6) `## 📝 Punto de control`; (7) `## Lo que acabas de aprender`; (8) `**Siguiente:**`.

### Gran verificación final de fase

**Source:** `guia-11-pedidos-cierre.md` 469-515 (la versión más reciente).
**Apply to:** la última guía de la fase 4. Tabla numerada con columna Origen + fila contrato 0.4.0 ↔ `/docs` con **Authorize admin** (ahora contra el CRUD real, no solo el 403 del demo) + párrafo "se repite al final de cada fase" + sugerencia de commit. **Novedades fase 4:** la fila del grep del build (`GEMINI_API_KEY` sin resultados en `dist/`, comando por shell, Pitfall 8) y las corridas de roles con las cuentas seed (admin 200 / clienta 403 / clienta fuerza `/admin` → NoAutorizado). El UAT runtime de estas filas corre en maura-uat (delegado); el happy path del asistente queda tras `checkpoint:human-verify` (Open Question 1 de RESEARCH).

### Formato ADR

**Source:** `adr/012-retorno-de-webpay.md` (97L) y `adr/014-snapshot-de-precio-en-la-orden.md` (84L) completos (los más recientes).
**Apply to:** ADRs 015-017. Estado/Fecha/Resuelve → Contexto → Opciones consideradas (tabla 3 opciones con pros/contras honestos) → Decisión ("**Opción X.**" + reglas numeradas) → Consecuencias (**Positivas** / **Negativas (honestas)**) → Para conversar en clase (3 preguntas). El ADR-017 cita la evidencia de RESEARCH contra el README v2.25.0 (patrón ADR-012:14-19 citando el spike con link relativo).

### API-first con la subida de versión narrada (D-15/ADR-007 + D-54)

**Source:** `contrato_api.yaml` header (1-8) + la historia 0.1.0→0.2.0→0.3.0 del propio archivo.
**Apply to:** orden de los planes: docs 02/03 + contrato 0.4.0 + ADRs 015-017 aprobados ANTES de toda guía (D-62). La retirada de `/api/admin/estado` se NARRA (description del contrato o intro de la guía nueva: el endpoint cumplió su lección D-33); las guías 05/06 NO se re-editan (Pitfall 7).

### Trazabilidad numerada continua

**Source:** series vigentes verificadas esta sesión: RF-18 (02_requerimientos.md:118), RNF-07 (:132), RN-13 (:150), HU-11 (:252-259); pantallas 1-9 (03_diseno.md §4); DFDs 1.0-11.0 (§3.3-3.13); ADRs 001-014; decisión de diseño 14 (03_diseno.md:211-217); tags del contrato citando requisitos.
**Apply to:** todo doc nuevo: RF-19+/RNF-08+/RN-14+/HU-12+; pantallas 10-14 (numeración UI-SPEC 345); DFDs 12.0+; decisiones de diseño 15+; ADRs 015-017; READMEs contando 17 ADRs y guías 1-14/15.

### Extensiones in-place de los docs del ciclo

**Source:** la historia de los archivos — cada doc ya vivió DOS extensiones (01→02→03) cuya mecánica se replica: bloque de alcance de etapa nuevo, series continuadas, fila de §13 completada, bloque de aprobación nuevo; ER/DFD/pantallas solo agregan; el contrato sube versión con la tabla de errores cambiando de estado (el 400 pasó de "Reservado" a "En uso" en fase 3 — el 503/429 nuevos y el 409 con segundo uso siguen la mecánica).
**Apply to:** idéntica mecánica para 03→04. Nunca renumerar lo existente; solo agregar y cambiar estados de fila (caso delicado: RN-04 y la descripción del actor Admin — ver Grupo A).

### Copys locked literales + tokens Maura

**Source:** `04-UI-SPEC.md` (approved) — Copywriting Contract completo (247-276): "Nuevo producto"/"Crear producto"/"Guardar cambios", "Anular" → "¿Anular el pedido {numero}?" + "Sí, anular", "Ese pedido ya no está en curso." (409), "Pregúntale a Maura", "Asesora de aromas", bienvenida "¡Hola! Soy la asesora de Maura...", errores 503/429/red sin cifras de límites, voz de la asesora en primera persona con tuteo chileno (D-02). Tokens: paleta `@theme` verbatim (46-54), presupuesto tipográfico congelado (94-104), badges BADGES + Stock bajo + Activo/Inactivo (127-136), `shadow-lg` SOLO en los dos elementos flotantes (63).
**Apply to:** guías 12+, pantallas 10-14 de docs/03, y (como `detail` de Error) los copies de error del contrato 0.4.0.

### Mini-verificaciones accionables + comandos agnósticos de terminal (D-12)

**Source:** guia-09 Paso 10 (1235-1456: one-liners httpx con credenciales del Settings, la carrera de stock con script), guia-11 Paso 5 (440-465: corridas de navegador con la tarjeta oficial), guia-05:471-481 (`uv run python -c` con output esperado).
**Apply to:** todas las guías. Casos concretos de la fase: 200/403 por rol en cada path admin (token admin vs clienta del seed), anular → 409 al repetir, soft delete → producto desaparece del catálogo y el pedido viejo conserva snapshot, métricas con las órdenes de fase 3 ya sembradas en maura-uat, sin key → 503 amable, grep del build por shell.

### BADGES a módulo propio (refactor contratado)

**Source:** `guia-11:77-86` (la tabla BADGES con la nota "si un día nace la tercera consumidora, baja a un módulo propio") + `04-UI-SPEC.md:138` (el contrato del refactor: `src/lib/badges.ts`, tres consumidoras, D-45 una sola verdad del estado).
**Apply to:** guia-13. El refactor toca el código del alumno en SU máquina; las guías 10/11 no se re-editan (trazabilidad).

### Idioma y marcadores del producto

Español de Chile, tuteo, tono cercano (todos los docs vigentes). Los marcadores 🧠/✅/❌/📝 son contenido del producto SOLO dentro de las guías; los docs del ciclo (02/03/04) usan tablas, blockquotes y notas — mantener esa separación por tipo de documento. Sin emojis en comunicación con el usuario (AGENTS.md).

## No Analog Found

Todo deliverable del ciclo tiene análogo exacto de formato. Los bloques de CÓDIGO que las guías narran por primera vez no tienen precedente in-repo (el repo no contiene código, D-17 — y el corpus no ha construido admin ni IA):

| Bloque de código nuevo | Razón sin análogo | Fuente firmada |
|---|---|---|
| `services/asistente.py` completo: `genai.Client()` lazy, `GenerateContentConfig(response_mime_type='application/json', response_json_schema=...)`, wrapper `errors.APIError` → 429/503, validación de ids contra catálogo activo | Ninguna guía integró Gemini; el patrón STRUCTURAL (único importador + traducción de errores) sí tiene análogo: `services/webpay.py` (guia-09:497-547) | `04-RESEARCH.md` Patterns 1-3 y 6 + Ejemplo A (verbatim del README del SDK @ v2.25.0, fetched 2026-09-30) |
| `RequireAdmin.tsx` / `NoAutorizado` / `LayoutAdmin` / sub-rutas anidadas con `Outlet` | El corpus tiene `RequireAuth` (guia-06) pero jamás un guard por rol ni layout intermedio con Outlet | RESEARCH Pattern 4 (sketch sobre RequireAuth verificado) + Pattern 5 (nested routes, base guia-11:409-414) + UI-SPEC 158-176 |
| `BurbujaAsesora` (chat stateless, `aria-live`, auto-scroll, estados 503/429/red) | No existe chat ni elemento flotante en el corpus | UI-SPEC pantalla 14 (218-231, contrato completo de comportamiento y copys) + RESEARCH D-57..D-61 |
| Agregaciones SQL de métricas (sum PAID, group_by estado, top 5 desde líneas snapshot, count stock bajo) | El corpus solo ha hecho SELECT/WHERE y UN UPDATE condicional — nunca GROUP BY/agregación | RESEARCH Ejemplo D (sketch SQLAlchemy verificado contra las tablas existentes) |
| Transición admin validada con 409 (`TRANSICIONES_ADMIN`, UPDATE condicional sobre `estado`) | El guard ya-PAID de guia-09:887-897 es el análogo PARCIAL más cercano (misma muralla, otro dueño) — la transición ejecutada por admin y el 409 con su copy son nuevos | RESEARCH Ejemplo C + Open Question 3 (409 recomendado) + D-50 |
| `lib/badges.ts` (BADGES a módulo) | Refactor nuevo; la tabla existe duplicada en guia-10/11 (código del alumno) | UI-SPEC 138 + guia-11:77-86 (la nota que lo promete) |

**Nota UAT:** el happy path del asistente (llamada real a Gemini) depende de una `GEMINI_API_KEY` que NO está en maura-uat — el planner marca esa verificación tras `checkpoint:human-verify` (el usuario entrega la key o autoriza crearla); degradación, grep del build y todo el panel se verifican sin ella (RESEARCH Environment Availability + Open Question 1).

## Metadata

**Analog search scope:** `D:/Repos/demo-carro/docs/` completo (33 archivos git-trackeados listados con `git ls-files docs/`) + `README.md` raíz + `.planning/phases/03-*/03-PATTERNS.md` (análogo directo de formato de este documento) + `04-UI-SPEC.md` del phase dir (insumo approved, no deliverable).
**Tracked-source gate:** todos los análogos nombrados verificados con `git ls-files -- <path>` (salida no vacía, corrida esta sesión): contrato_api.yaml, adr/012, adr/014, adr/011 (vía listado completo de docs/), 02_requerimientos.md, 03_diseno.md, 04_arquitectura/README.md, 05_desarrollo/README.md, guia-05, guia-06, guia-09, guia-10, guia-11, docs/README.md, README.md, 03-PATTERNS.md, 04-UI-SPEC.md. Ninguna ruta mirror/gitignored emitida.
**Files scanned:** 13 análogos leídos esta sesión — 8 completos (contrato_api.yaml 778L, 02_requerimientos.md 392L, 03_diseno.md 1002L, guia-10 847L, guia-11 636L, adr/012 97L, adr/014 84L, 04_arquitectura/README.md 250L, los 3 READMEs de estado) + guia-09 1614L completa (dos pasadas contiguas 1-1386 + 1387-1614) + lecturas dirigidas no solapadas de guia-05 (90-140, 445-595) y guia-06 (258-303, 935-969) — más 03-PATTERNS.md (393L, análogo de este documento), 04-CONTEXT.md y 04-RESEARCH.md del phase dir.
**Pattern extraction date:** 2026-09-30
