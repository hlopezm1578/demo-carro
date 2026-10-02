# Phase 3: Checkout Webpay y órdenes - Pattern Map

**Mapped:** 2026-09-30
**Files analyzed:** 14 (7 documentos nuevos + 7 extensiones de documentos existentes) + 1 documento de spike en `.planning/` (total 15 entradas; el spike doc cuenta aparte porque NO es deliverable del ciclo, es insumo interno del planner, D-40)
**Analogs found:** 14 / 14 deliverables con análogo exacto in-repo (el corpus de fases 1-2 está completo y cada doc nuevo/extendido tiene su análogo git-trackeado). El `03-SPIKE-RETORNO.md` tiene solo análogo parcial (role-match) — es el primer spike de la serie.

## Nota de alcance: repo guide-only, spike primero (leer antes de planificar)

`D:/Repos/demo-carro` sigue **guide-only (D-17, ADR-008)**: la fase 3 entrega SOLO documentos. Tres reglas que ordenan los planes:

1. **El spike es el PRIMER plan de la fase** (D-38) y corre runtime en `D:/Repos/maura-uat` (UAT delegado, autorizado en AGENTS.md). Su código JAMÁS se commitea acá; sus hallazgos sí, como `03-SPIKE-RETORNO.md` en el phase dir (D-40). La mecánica exacta del retorno la firma el spike con evidencia (D-41) — el contrato, el ADR-012 y las guías se escriben DESPUÉS.
2. **Orden API-first obligatorio (D-15/ADR-007):** `contrato_api.yaml` 0.2.0→0.3.0 se extiende y aprueba ANTES de escribir las guías. Orden de planes (calza con la recomendación de 03-RESEARCH): (A) spike + hallazgos → (B) docs 02/03 + contrato 0.3.0 + ADRs 012-014 + README de arquitectura → (C) guías 09-11 → (D) READMEs de estado.
3. **El código que las guías narran** (`models/pedido.py`, `services/webpay.py`, `routers/retorno.py` GET+POST con 302, el form auto-submit, el UPDATE condicional de stock) NO tiene precedente en el corpus (ni en demo-cine: no hay pagos). Su fuente es `03-RESEARCH.md` Patterns 1-8 (verificados contra SDK fuente, plugin oficial de Transbank, starlette y docs oficiales esta sesión). El planner copia de ahí; las guías lo traducen a la estructura canónica.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `.planning/phases/03-…/03-SPIKE-RETORNO.md` (NUEVO — hallazgos del spike, D-40) | doc hallazgos runtime (insumo planner) | request-response (evidencia por flujo) | `02-UAT.md` (evidencia runtime estructurada) + tabla de flujos de `03-RESEARCH.md` Pattern 3 | role-match (primer spike de la serie) |
| `docs/02_requerimientos.md` (EXTENDER) | doc requerimientos | — | sí mismo (continuar series RF/RNF/RN/HU + tabla §13, fila P6) | exact (in-place) |
| `docs/03_diseno.md` (EXTENDER) | doc diseño | — | sí mismo (§2 ER/diccionario/decisiones, §3 DFD 9.0+, §4 pantallas 8+, §5 trazabilidad) | exact (in-place) |
| `docs/04_arquitectura/contrato_api.yaml` (EXTENDER, ANTES de guías y DESPUÉS del spike) | contract (OpenAPI) | request-response | sí mismo (430 líneas: tabla errores 26-35, tags 43-51, schemas, paths; login form-encoded 326-342 como patrón del POST del retorno) | exact (in-place) |
| `docs/04_arquitectura/adr/012-*.md` (NUEVO: retorno de Webpay, mecánica del spike, D-41/D-42) | doc (decisión) | — | `adr/011-roles-desde-el-primer-token.md` (el ADR más reciente, 71 líneas) | exact (formato) |
| `docs/04_arquitectura/adr/013-*.md` (NUEVO: orden nace al pagar + stock al aprobar, D-34/D-35) | doc (decisión) | — | `adr/010-carro-client-side.md` (decisión que ya anuncia esta etapa, regla 3) | exact (formato) |
| `docs/04_arquitectura/adr/014-*.md` (NUEVO: snapshot de precio en la orden, D-36/D-37) | doc (decisión) | — | `adr/010-carro-client-side.md` (la asimetría carro/orden es su espejo invertido) | exact (formato) |
| `docs/04_arquitectura/README.md` (EXTENDER) | doc índice/arquitectura | — | sí mismo (§3 stack fila "Pago (fase 3)" línea 120, §4 árbol 133-168, §5 índice ADRs 188-200) | exact (in-place) |
| `docs/05_desarrollo/guia-09-*.md` (NUEVO: backend órdenes + Webpay) | doc (guía paso a paso) | — | `guia-05-cuentas-backend.md` (1108 líneas: 11 pasos backend de fase 2, el patrón completo modelos→routers→prueba de fuego) | exact (estructura) |
| `docs/05_desarrollo/guia-10-*.md` (NUEVO: vuelta a la SPA — form auto-submit, /pago/resultado, voucher) | doc (guía paso a paso) | — | `guia-08-checkout.md` (enciende su CTA deshabilitado 221-229) + `guia-07-carro.md` paso 5 (main.tsx ruta nueva) | exact (estructura) |
| `docs/05_desarrollo/guia-11-*.md` (NUEVO: historial /pedidos + Gran verificación final fase 3) | doc (guía de cierre) | — | `guia-08-checkout.md` §Gran verificación final (372-411) + `guia-07` (lista/hidratación/navbar) | exact (estructura) |
| `docs/05_desarrollo/README.md` (EXTENDER) | doc índice | — | sí mismo (tabla guías 24-33, blockquote 35-39, mapa mental 41-52) | exact (in-place) |
| `docs/README.md` (EXTENDER) | doc índice | — | sí mismo (tabla del ciclo, fila 4 línea 18, fila 5 línea 19) | exact (in-place) |
| `README.md` raíz (EXTENDER) | doc índice | — | sí mismo (tabla 36-45 + stack 70-73) | exact (in-place) |

## Pattern Assignments

### Grupo 0 — El documento del spike (PRIMER entregable de la fase, D-38..D-41)

#### `.planning/phases/03-…/03-SPIKE-RETORNO.md` (NUEVO)

**Analog:** `.planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-UAT.md` (159 líneas, leído completo esta sesión) para el formato de evidencia runtime; `03-RESEARCH.md` Pattern 3 para la tabla de flujos que el spike corrobora.

**Frontmatter de estado runtime** (02-UAT.md líneas 1-8, verbatim — replicar la mecánica de registro delegado):

```markdown
---
status: complete
phase: 03-checkout-webpay-y-rdenes
source: [03-RESEARCH.md]
started: 2026-09-__T__:__Z
updated: 2026-09-__T__:__Z
verified_by: agent (user-delegated per AGENTS.md — taller D:/Repos/maura-uat)
---
```

**Contenido obligatorio por flujo** (el spike corrobora aprobado/anulado/timeout runtime + documenta el 4° desde docs+plugin, A3 de RESEARCH): por cada flujo — método real (GET vs POST), params presentes (token_ws / TBK_TOKEN / TBK_ID_SESION / TBK_ORDEN_COMPRA), tiempo cronometrado (timeout integración: docs dicen 10 min, Pitfall 9 — reservar 15), camino a REJECTED (Q2), y hallazgo extra de idempotencia del commit si se observa (A1). Estructura de entrada estilo 02-UAT `### N. <test>` + `expected:` / `result:` / `evidence:` (líneas 16-18 verbatim):

```markdown
### 1. <Flujo> — qué llega y por dónde
expected: <qué dice la docs/oficial que debería llegar>
result: pass
evidence: |
  <params observados, método, timing, captura del request>
```

**Consumo downstream (D-40/D-41):** el ADR-012 cita este documento como evidencia por flujo; la guía narra "lo que el spike reveló" SIN referenciar el documento interno; el contrato declara GET+POST inmune a la ambigüedad (Pitfall 2).

---

### Grupo A — Requerimientos y diseño de la etapa 3

#### `docs/02_requerimientos.md` (EXTENDER)

**Analog:** sí mismo (320 líneas, leído completo esta sesión).

**Numeración vigente a continuar** [VERIFIED: RF-11 en línea 100, RNF-06 en 113, RN-09 en 127, HU-08 en 199]: los nuevos llegan como **RF-12+** (pago PAY-01..04, recalculo CART-03, órdenes ORDR-01/02), **RNF-07+** (si aplica — p. ej. dependencia de servicio externo sandbox), **RN-10+** (candidatos: snapshot de precio D-36, estados honestos D-48, stock atómico D-35 como regla), **HU-09+** (pagar con Webpay, volver del pago, ver mis pedidos). La numeración exacta es discretion del planner confirmada en CONTEXT.

**Formato exacto de un RF con origen** (línea 93, replicar):

```markdown
- **RF-06:** El sistema debe permitir crear una cuenta de clienta con un email y una
  contraseña; si el email ya tiene cuenta, debe rechazar el registro con un mensaje
  claro que invite a iniciar sesión. *(AUTH-01, P5)*
```

**Puntos que cambian de estado:**
- §1 contexto (13-23): el párrafo narra la etapa 3 (el pago llega "en la etapa siguiente del proyecto (véase §2)" — línea 18 — ya no).
- §2 alcance: la línea 51 verbatim `Pago online con Webpay en modo de prueba (P6) → **etapa 3**.` pasa del bloque "Fuera del alcance de las etapas 1 y 2" a un nuevo bloque "Dentro del alcance de la etapa 3" (iguales a los de etapa 2, líneas 42-48); P7/P8 siguen esperando etapa 4.
- §3 actores (63-73): sin actor nuevo — Webpay NO es actor del sistema, es entidad externa (va en §3.1 de 03_diseno); ajustar solo la descripción de la clienta si menciona pedidos.
- §13 trazabilidad, fila P6 (línea 282, verbatim): `| P6 Pago online con Webpay | *(sin requerimiento en esta etapa — etapa 3: CART-03 y PAY-01..04)* | Etapa 3 |` → reemplazar por el mapeo real a los RF/RN/HU nuevos (igual que la fase 2 hizo con P5, línea 281).
- §10 entradas (240-248): nueva fila — el retorno de Webpay como entrada del sistema (params TBK_*, tratados como opacos) y el carro sin precios como entrada del checkout.
- §12 pantallas (259-267): sumar ítems 8+ — resultado de pago/voucher, historial de pedidos (insumo de 03_diseno §4).
- §14 aprobación (297-311): nuevo bloque "**Etapa 3 — pago con Webpay y órdenes (documentada el 2026-09-__)**" con la misma tabla de firmas.

---

#### `docs/03_diseno.md` (EXTENDER)

**Analog:** sí mismo (723 líneas, leído completo esta sesión).

**§2.1 ER en mermaid** (32-52): agregar PEDIDO y LÍNEA con relaciones `USUARIO ||--o{ PEDIDO` / `PEDIDO ||--|{ LÍNEA` / `LÍNEA }o--|| PRODUCTO` — el formato de entidad con comentario citando RF/RN por campo (líneas 34-45) se replica. La nota "Lectura del diagrama" (54-61) YA promete esta extensión [VERIFIED líneas 57-59 verbatim]: *"Los pedidos siguen reservados para la etapa 3 y serán quienes conecten USUARIO con PRODUCTO por relaciones nuevas (una clienta hace pedidos; un pedido elige productos)"* — la etapa 3 la actualiza en esos términos.

**§2.2 Diccionario de datos** (formato, líneas 67-78):

```markdown
| Atributo | Tipo | Longitud | Obligatorio | Restricción / origen |
|---|---|---|---|---|
| sku | Texto | 20 | Sí | **Único**; clave natural estable del catálogo demo: ... (RF-05) |
```

Nuevas tablas **PEDIDO** (numero único "MAURA-000001" ≤26 chars D-37, estado lista cerrada 4 valores, total entero CLP recalculado, usuario_id FK) y **LÍNEA** (pedido_id FK, producto_id FK, nombre_snapshot, precio_snapshot, cantidad — D-36). Borrador exacto de campos: `03-RESEARCH.md` Pattern 6.

**§2.3 Decisiones de diseño numeradas "(y por qué)"** (89-160, hoy 1-10): continuar con 11+ — la orden nace al iniciar el pago (D-34), validar stock al crear y descontar al aprobar (D-35), snapshot de nombre/precio en la línea con la asimetría RN-08 explícita (D-36), numero legible público ≠ id interno (D-37). El bloque de nota final (156-160) que vincula decisiones con ADRs gana su párrafo de etapa 3 (ADRs 012-014).

**§3 Procesos**: §3.1 contexto (171-187) agrega la entidad externa **Webpay** (el primer servicio externo del sistema — flujo de ida y vuelta); §3.2 almacenes (191-196) agrega `D3 Pedidos`; §3.3-3.10 DFDs numerados 1.0-8.0 → continuar con **9.0+** (iniciar checkout → orden PENDING → Webpay; procesar retorno con los 4 flujos; ver historial). Formato por DFD (verbat: flowchart TD con almacenes `D1[("D1 Productos")]` + bloque "**Reglas del proceso:**" — ejemplo en 332-336).

**§4 Pantallas** — formato obligatorio por pantalla (359-361 verbatim):

```markdown
**Origen:** RF-01, HU-01 (con la página del catálogo) · **Estados:** normal
(contenido de marca estático; ...)
```

Pantallas 8+ nuevas (resultado de pago/voucher por flujo con estados carga/error/degradado-sin-sesión Pitfall 12; historial lista→detalle): wireframe ASCII + Origen/Estados — la regla §4.1 (353-355) "cada pantalla declara sus estados de carga, error y vacío" aplica con fuerza nueva (4 flujos = 4 caras del voucher). La pantalla 7 checkout (638-673) gana su variante "la etapa 3 enciende el CTA" espejando cómo la etapa 2 lo hizo con la ficha (474-493).

**§5 Trazabilidad** (formato, 679-705): una fila por RF/RN nuevo de la etapa 3.

---

### Grupo B — Contrato 0.3.0, ADRs 012-014 y README de arquitectura (DESPUÉS del spike, ANTES de las guías)

#### `docs/04_arquitectura/contrato_api.yaml` (EXTENDER — 0.2.0 → 0.3.0)

**Analog:** sí mismo (430 líneas, leído completo esta sesión).

**Header de regencia** (1-8): mantener textual el bloque `# Maura — Contrato de la API ... FUENTE DE LA VERDAD ... Se aprueba antes de codificar`.

**Cambios puntuales con línea exacta:**
- `info.version: 0.2.0` (línea 13) → `0.3.0`.
- `info.description` (19-22): la nota de autenticación se extiende — checkout y pedidos exigen Bearer; el retorno es público por diseño.
- **Tabla de convención de errores** (26-35): la fila `| 400 | Regla de negocio violada | Reservado (fases 2+) |` (línea 30) pasa a `En uso (fase 3)` — stock insuficiente al crear la orden (CART-03); **agregar fila 302** (redirección del navegador — el primer response no-JSON del contrato, Pattern 7 de RESEARCH). Verbatim actual:

```yaml
    | Código | Significado | Estado |
    |---|---|---|
    | 200 | OK (listado, ficha, salud) | En uso (fase 1) |
    | 201 | Creado (registro de una cuenta) | En uso (fase 2) |
    | 400 | Regla de negocio violada | Reservado (fases 2+) |
```

- **tags** (43-51): nuevo `Pago` (cita PAY-01..04, CART-03) y/o `Pedidos` (cita ORDR-01/02) — nombres a discretion CONTEXT, igual que `Autenticación` cita `(AUTH-01, AUTH-02, AUTH-03)`.
- **schemas** (67-174, convención: `description` citando requisito + description por campo + `example` + `required`): nuevos `CheckoutCreate` (**sin campo precio** — CART-03 escrito en el contrato), `CheckoutRespuesta {url, token_ws, numero}`, `OrdenLista`, `OrdenDetalle` (+ líneas con snapshot), enum `estado: [pending, paid, cancelled, rejected]` (minúsculas en el cable, A5).
- **paths** (179-429): nuevos `POST /api/checkout` (security bearerAuth como `/api/auth/perfil` líneas 367-368; responses 201/400/401/422), `GET+POST /api/pago/retorno` (`security: []` público — contraste pedagógico deliberado, Pattern 7), `GET /api/pedidos` y `GET /api/pedidos/{numero}` (404 uniforme para no-existe Y no-es-tuya).
- **El POST del retorno reutiliza el patrón form-encoded del login** [VERIFIED líneas 326-342 verbatim — `application/x-www-form-urlencoded` con properties/required inline, mismo estilo para token_ws/TBK_TOKEN/TBK_ID_SESION/TBK_ORDEN_COMPRA]:

```yaml
      requestBody:
        required: true
        content:
          application/x-www-form-urlencoded:
            schema:
              type: object
              properties:
                username:
                  type: string
                  format: email
                  description: El email de la clienta (OAuth2 llama username a este campo)
                  example: clienta@maura.cl
              required: [username, password]
```

- **302 declarado en AMBOS métodos** (get y post) del retorno con `headers.Location` — sin declaración, `/docs` no lo lista y la fila contrato↔`/docs` detecta un falso desvío (Pitfall 13, misma lección del 404 de G-01-4 que la fase 2 aplicó en cada path).

---

#### `docs/04_arquitectura/adr/012..014-*.md` (NUEVO — 3 ADRs)

**Analog:** `docs/04_arquitectura/adr/011-roles-desde-el-primer-token.md` y `adr/010-carro-client-side.md` (leídos completos esta sesión — los ADRs de fase 2; ADR-007 es el segundo ejemplo).

**Esqueleto obligatorio** (ADR-011 líneas 1-5 + secciones fijas):

```markdown
# ADR-012 — <Decisión en una frase>

- **Estado:** Aceptada
- **Fecha:** 2026-09-__ (fecha de la fase 3)
- **Resuelve:** <pregunta de decisión>

## Contexto
## Opciones consideradas        → tabla | Opción | A favor | En contra | (3 opciones A/B/C)
## Decisión                     → "**Opción X.**" + reglas numeradas
## Consecuencias                → **Positivas** / **Negativas (honestas)**
## Para conversar en clase      → 3 preguntas numeradas
```

**Ejemplo de tabla de opciones con densidad correcta** (ADR-010 líneas 19-23 verbatim — 3 opciones, pros/contras honestos):

```markdown
| Opción | A favor | En contra |
|---|---|---|
| **A. Store client-side con solo pares `{producto_id, cantidad}`**, hidratado contra la API | El visitante anónimo arma su carro sin cuenta; ... | Cada vista del carro consulta la API (hidratación); ... |
```

**Contenido candidato (discretion CONTEXT, assumptions A7):**
- **012 — Retorno de Webpay:** mecánica elegida por el spike (302 a ruta única de resultado vs página intermedia) CITA LA EVIDENCIA por flujo desde `03-SPIKE-RETORNO.md` (D-40/D-41); discriminación por presencia de params, no por método (Pitfall 2); `security: []` deliberado.
- **013 — La orden nace al iniciar el pago + stock se descuenta al aprobar:** D-34/D-35; la opción "reservar stock al crear" va en la tabla de descartadas; REJECTED por carrera como consecuencia honesta. Nota: ADR-010 regla 3 (líneas 35-38) YA promete esta decisión — el ADR-013 la recoge y la cita.
- **014 — Snapshot de precio en la orden:** D-36/D-37; la asimetría con RN-08 como lección central (prohibido en el carro, obligatorio en la orden); soft delete de docs/03 §2.3.5 como soporte; numero legible `MAURA-000001` como buy_order ≠ id interno.

**Referencias cruzadas:** los ADRs se citan entre sí con links relativos (ADR-011 línea 56: `[ADR-009](009-jwt-larga-vida-localstorage.md)`) y citan la fase siguiente cuando corresponde (013→fase 4 gestión de huérfanas, D-49).

---

#### `docs/04_arquitectura/README.md` (EXTENDER)

**Analog:** sí mismo (235 líneas, leído completo esta sesión).

- **§3 Stack** (tabla `| Pieza | Elección | Por qué (decisión completa) |`, 101-121): la fila placeholder (líneas 120-121 verbatim) `| Pago (fase 3) | **Webpay Plus, ambiente de integración** | Pasarela real chilena en sandbox con credenciales públicas — llega en su fase |` se convierte en fila real del stack construido + fila nueva `transbank-sdk 6.1.0` citando ADR-012/013, igual que las filas de fase 2 citan ADR-009/010/011.
- **§4 Árbol del proyecto del alumno** (133-168): agregar `models/pedido.py`, `schemas/pedido.py`, `repositories/pedido.py`, `services/pedidos.py`, `services/webpay.py` (único lugar que importa transbank), `routers/checkout.py`, `routers/retorno.py`, `routers/pedidos.py`, `features/pago/`, `features/pedidos/` — con el comentario de una línea por archivo que caracteriza el árbol vigente (ej. línea 153: `routers/admin.py  # /api/admin/estado — protegido por rol admin (D-33)`). Mantener intacto el disclaimer guide-only (127-131).
- **Reglas de dependencia 1-6** (170-182): no cambian — la regla 5 ("todo HTTP pasa por `src/lib/api.ts`") gana su primera excepción narrada en las guías (el retorno es navegación, no fetch — Pitfall 10 CORS); el README puede anotarlo o dejarlo a las guías.
- **§5 Índice de ADRs** (formato, 188-200): `| [ADR](adr/NNN-slug.md) | Decisión | Resuelto por |` → 3 filas nuevas (012, 013, 014).

---

### Grupo C — Guías 09-11

> Regla transversal del grupo: las 3 guías replican la **estructura canónica** fijada en guia-01..08 (ver Shared Patterns). La convención "Gran verificación final" de guia-04/guia-08 la replica guia-11 como cierre de la fase 3 — CON la novedad de que sus filas exigen los 4 flujos runtime en el navegador.

#### `docs/05_desarrollo/guia-09-*.md` (NUEVO — backend órdenes + Webpay)

**Analog:** `guia-05-cuentas-backend.md` (1108 líneas — la guía de backend de fase 2; mapa de pasos verificado por grep esta sesión).

**Correspondencia paso a paso con guia-05** (misma progresión de capas):
- **Instalación narrada** — guia-05 Paso 1 (líneas 32-65): "tres paquetes, tres razones" con 🧠 explicando por qué cada uno. Guia-09: `uv add transbank-sdk` (UN paquete, y el 🧠 explica que NO hay `.env` nuevo — credenciales públicas de integración dentro del SDK, la aclaración que CONTEXT pidió dejar explícita al alumno).
- **Modelo con enum** — guia-05 Paso 3 "el enum del rol, segunda vuelta del gotcha" (159-222): guia-09 hace la **TERCERA vuelta** con `EstadoPedido` (`pending = "pending"` — Pitfall 7 de RESEARCH) citando las dos vueltas previas (guia-03 familias, guia-05 roles).
- **Schemas espejo del contrato** — guia-05 Paso 4 (224-292, "igual que en la guía 4: abro `contrato_api.yaml`..."): los schemas de pedido espejan el 0.3.0; la nota obligatoria estilo "`hashed_password` no aparece" ahora es "**ningún schema de entrada tiene campo precio**" (CART-03).
- **Repository** — guia-05 Paso 5 (294-355): `PedidoRepository` con sesión inyectada; agrega `descontar_stock_atomico` (UPDATE condicional + rowcount — código fuente: 03-RESEARCH Pattern 5).
- **Services** — guia-05 Paso 7 (485-570): `iniciar_checkout` (recalculo CART-03, 400 stock) y `procesar_retorno` (discriminador + commit + transición) sin conocer HTTP; `services/webpay.py` como ÚNICO importador de transbank (wrapper del Pattern 1 de RESEARCH).
- **Routers con responses declaradas** — guia-05 Paso 8 (572-790): checkout/retorno/pedidos declaran 400/401/404/**302** en `responses={...}` — misma lección del 404 de G-01-4, ahora con el 302 (Pitfall 13).
- **main.py composición** — guia-05 Paso 9 (792-835): solo `include_router` nuevos; CORS NO cambia (Pitfall 10 — el retorno es navegación, no fetch: la guía lo enseña).
- **Prueba de fuego** — guia-05 Paso 11 (938-993): mini-verificación de la carrera de stock (stock=1 + dos requests concurrentes → un PAID y un REJECTED, script httpx de dos threads — Pattern 5 de RESEARCH).

**Nuevo sin precedente en guia-05** (fuente: 03-RESEARCH): el endpoint GET+POST del retorno con `RedirectResponse(url, status_code=302)` (Patterns 3-4) y la lectura `Form(default=None)` de los params TBK_*.

---

#### `docs/05_desarrollo/guia-10-*.md` (NUEVO — vuelta a la SPA: form auto-submit, /pago/resultado, voucher)

**Analog:** `guia-08-checkout.md` (502 líneas, leído completo esta sesión) + `guia-07-carro.md` Paso 5 (main.tsx: 605-636).

**El CTA que esta guía enciende** [VERIFIED guia-08 líneas 221-229 verbatim — el bloque exacto que se reemplaza]:

```tsx
        <button
          disabled
          className="mt-6 w-full bg-orange-600 text-white font-bold rounded-full px-6 py-2 min-h-11 disabled:opacity-60 disabled:cursor-not-allowed focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
        >
          Pagar con Webpay
        </button>
        <p className="mt-2 text-sm text-neutral-600">
          El pago llega en la etapa siguiente.
        </p>
```

Guia-08 Paso 4 (336-368) ya narró el contrato: "la fase 3 no rediseñará nada — solo reemplazará el `disabled` por el flujo real de Webpay". La mutación + form auto-submit (submit en el handler del clic, JAMÁS en useEffect — Pitfall 6) vive en `Checkout.tsx`; código fuente: 03-RESEARCH Pattern 2.

**Ruta nueva en main.tsx** — patrón guia-07 Paso 5 (605-636) y guia-08 Paso 2 (imports 275-278 + rutas 283-289 verbatim):

```tsx
<Route path="/carro" element={<Carro />} />
<Route element={<RequireAuth />}>
  <Route path="/checkout" element={<Checkout />} />
</Route>
<Route path="*" element={<NoEncontrado />} />
```

Guia-10 agrega `/pago/resultado` **PÚBLICA** (fuera de RequireAuth — Pitfall 12: el 302 llega sin sesión en la URL; el voucher degrada con honestidad) — el 🧠 del paso contrasta con la ruta protegida de guia-08 Paso 2, que explicó "el guard es cortesía de UX".

**Estados de la pantalla de resultado:** mismos cuatro estados async uniformes de fase 1-2 (skeletons `animate-pulse bg-neutral-200 rounded-2xl`, error centrado + causa puerto 8000 + Reintentar — guia-08 líneas 89-111 verbatim como el ejemplo más reciente) + el estado degradado sin sesión (estado y numero visibles, "inicia sesión para ver el detalle" con link que SÍ lleva returnTo). El voucher reutiliza el clp formatter y el layout de líneas del checkout (guia-08 líneas 61-64, 140-219).

**Vaciado del carro SOLO con PAID visible** (D-44): `useCarroStore` ya tiene `vaciar` (guia-07 Paso 6) — se llama al llegar al voucher con estado pagado + `invalidateQueries` de stock.

---

#### `docs/05_desarrollo/guia-11-*.md` (NUEVO — historial /pedidos + Gran verificación final de la fase 3)

**Analog:** `guia-08-checkout.md` §Gran verificación final + `guia-07-carro.md` (pantalla de lista + navbar).

**Gran verificación final — formato a replicar** [VERIFIED guia-08 líneas 372-411]: tabla numerada `| # | Verificación | Origen |` con el origen citando CS/RF/HU/ADR nuevos de la etapa 3 (los 4 flujos runtime con la tarjeta VISA 4051 8844..., anulado con el botón del formulario, timeout con su espera documentada, voucher propio con numero/total, carro intacto en anulado, stock descontado solo en el aprobado, PENDING visible "en curso", carrera de stock un PAID/un REJECTED), y la **fila final contrato ↔ `/docs`** actualizada al contrato 0.3.0 — ahora con el 302 del retorno como pieza nueva de la comparación. Verbatim del cierre (guia-08 líneas 393-401):

```markdown
La fila 12 es la evidencia formal del cierre — y esta fase suma una pieza
que la fase 1 no podía tener: **el botón Authorize de `/docs`**. ...
**Cualquier diferencia entre el panel y el contrato es un desvío** — o el
código corrige, o el contrato se versiona y se aprueba de nuevo; jamás
cambia en silencio. ... este mismo mecanismo se repite al final de cada
fase del proyecto.
```

Más la **sugerencia de commit** de cierre (guia-08 403-411, adaptada: "Cumple el contrato OpenAPI 0.3.0 ... respeta los 14 ADRs").

**Historial /pedidos** — patrones de guia-07: página de lista con hidratación (Carro.tsx 383-603 como el ejemplo más reciente de lista+total), ruta protegida `RequireAuth` (guia-08 Paso 2), y **"Mis pedidos" en el navbar** con el patrón del badge de guia-07 Paso 7 (667-729: el estado de sesión ya condiciona renders — ahora condiciona el link, D-47). El detalle reutiliza el componente voucher de guia-10 (D-43/D-46). Badges por estado: discretion con tokens de 01/02-UI-SPEC.

**Cierre de guía** — las tres secciones fijas de guia-08: `## 📝 Punto de control` (466-476), `## Lo que acabas de aprender` (478-494), `**Siguiente:**` (496-501 — apunta a fase 4: panel admin y gestión de huérfanas PENDING, D-49).

---

### Grupo D — READMEs de estado (D-13/D-18: el estado avanza por fase)

#### `docs/05_desarrollo/README.md` (EXTENDER)

**Analog:** sí mismo (53 líneas). Tabla `| # | Guía | Construye | Estado |` (24-33) gana filas 9-11 con el estilo "Construye" de una frase con el hito (ej. fila 8: "El checkout protegido y la Gran verificación final de la fase 2"). El blockquote (35-39) se actualiza igual que la fase 2 lo hizo: "La fase 3 completa sus tres guías (9-11: pago, vuelta, historial). Las guías 12+ llegan con las fases siguientes (panel admin, IA)". El "Mapa mental de la serie" (41-52) suma la capa de integración externa (el pago real y el retorno que cruza tiers).

#### `docs/README.md` (EXTENDER)

**Analog:** sí mismo (27 líneas). Fila 5 (línea 19 verbatim): `🚧 Parcial (guías 1-8 listas; continúa en fases 3+)` → `(guías 1-11 listas; continúa en fases 4+)`. Fila 4 (línea 18): "`04_arquitectura/` (documento + 11 ADRs + `contrato_api.yaml`)" → **14 ADRs**.

#### `README.md` raíz (EXTENDER)

**Analog:** sí mismo (92 líneas). Fila 5 (línea 42) igual que docs/README; fila 4 (línea 41) "Arquitectura + 11 ADRs + contrato OpenAPI" → 14; línea 54 "las 11 decisiones de arquitectura" → 14. Párrafo de stack (70-73): "Webpay Plus en ambiente de integración (fase 3)" pasa de promesa a construido, en el mismo tono telegráfico vigente.

---

## Shared Patterns

### Estructura canónica de guía (obligatoria en guia-09..11)

**Source:** `guia-05` (11 pasos) y `guia-08` completas — la secuencia más reciente del corpus.
**Apply to:** las 3 guías nuevas. Secuencia fija: (1) header `# Guía N — Título` + blockquote `**Qué construirás hoy:** / **Al terminar tendrás:** / **Necesitas:**` (guia-08 líneas 3-13 — la de guia-08 lista sus prerrequisitos por número de guía: las nuevas hacen igual con 1-8); (2) `## Los términos de hoy (antes de copiar nada)` tabla término/frase (guia-08 17-25 — candidatos fase 3: form POST auto-submit, return_url, token_ws/TBK_*, commit, PRG/302, buy_order, snapshot); (3) pasos `## Paso N —` con 🧠 **El desarrollador piensa:** en cursiva citando ADR/RN/D, código con nombre de archivo en negrita y docstring de módulo, ✅ **Mini-verificación** con comando + output esperado; (4) `## ❌ El error que este archivo evita` con pares ❌/✅ (guia-08 415-445 — candidatos: commitear flujo anulado, stock leído en Python, RedirectResponse sin 302); (5) `## ✅ Verificación de la guía N`; (6) `## 📝 Punto de control`; (7) `## Lo que acabas de aprender`; (8) `**Siguiente:**`.

### Gran verificación final de fase

**Source:** `guia-08-checkout.md` líneas 372-411 (la versión más reciente, con Authorize).
**Apply to:** guia-11 (cierre de la fase 3) y por decisión de CONTEXT todas las fases 2-5. Tabla numerada con columna Origen + fila contrato ↔ `/docs` al contrato **0.3.0** (ahora incluyendo el 302 y el endpoint público del retorno) + párrafo "se repite al final de cada fase" + sugerencia de commit. La novedad de esta fase: las filas exigen los **4 flujos runtime en el navegador** (tarjeta de éxito documentada, anulado, timeout con espera ≥10 min cronometrada por el spike, y la carrera de stock del backend).

### Formato ADR

**Source:** `docs/04_arquitectura/adr/011-roles-desde-el-primer-token.md` y `adr/010-carro-client-side.md` completos (los más recientes).
**Apply to:** ADRs 012-014. Estado/Fecha/Resuelve → Contexto → Opciones consideradas (tabla 3 opciones con pros/contras honestos) → Decisión ("**Opción X.**" + reglas numeradas) → Consecuencias (**Positivas** / **Negativas (honestas)** — p. ej. la huérfana PENDING visible sin gestión hasta fase 4 va ahí por mandato de D-48/D-49) → Para conversar en clase (3 preguntas). El ADR-012 cita `03-SPIKE-RETORNO.md` como evidencia (D-40).

### API-first con spike delante (D-15/ADR-007 + D-38/D-41)

**Source:** `docs/04_arquitectura/adr/007-api-first.md` + `04_arquitectura/README.md` §6 (204-219).
**Apply to:** orden de los planes de la fase: spike (runtime maura-uat) → hallazgos a `.planning/` → docs 02/03 → contrato 0.3.0 + ADRs 012-014 aprobados → guías 09-11 → READMEs. El ADR-012 NO se escribe antes del spike: la mecánica del retorno se firma con evidencia (D-41).

### Trazabilidad numerada continua

**Source:** series vigentes en `02_requerimientos.md` (RF-11 línea 100, RNF-06 línea 113, RN-09 línea 127, HU-08 línea 199 — todas VERIFIED esta sesión), `03_diseno.md` §5 (679-705), ADRs 001-011, tags del contrato citando STORE/AUTH/CART, filas de la Gran verificación citando origen, filas de READMEs contando ADRs.
**Apply to:** todo doc nuevo de la fase. Los RF/RNF/RN/HU nuevos continúan desde RF-12/RNF-07/RN-10/HU-09; la fila P6 de §13 se completa; el índice de ADRs llega a 014; los tags nuevos citan PAY/CART/ORDR; la fila 5 de los READMEs llega a "guías 1-11".

### Extensiones in-place de los docs del ciclo (el patrón "cómo la fase 2 extendió la fase 1")

**Source:** la propia historia de los archivos — cada doc extendido ya vivió UNA extensión de etapa (01→02) cuya mecánica se replica: 02_requerimientos sumó bloque de alcance de etapa + series + fila P5 completada + bloque de aprobación; 03_diseno sumó entidad al ER + diccionario + decisiones numeradas + DFDs + pantallas + filas de trazabilidad; el contrato subió 0.1.0→0.2.0 con tabla de errores cambiando de estado y tags/schemas/paths nuevos; los READMEs movieron su fila de fase.
**Apply to:** idéntica mecánica para 02→03. Nunca renumerar lo existente; solo agregar y cambiar estados de fila.

### Copys locked literales + tono Maura

**Source:** `03-CONTEXT.md` §specifics + Copywriting Contract de 01/02-UI-SPEC.md.
**Apply to:** guías 09-11 + contrato + pantallas nuevas:
- "MAURA-000001" como numero canónico de ejemplo (formato final a discretion, D-37).
- El voucher muestra: numero, fecha, líneas (nombre + precio snapshot), total, estado PAID, CTA "Seguir comprando".
- PENDING se muestra como "en curso" (u otro copy a discretion, D-45) — honestidad de estado.
- La tarjeta de éxito VISA 4051 8856 0044 6623 / CVV 123 / RUT 11.111.111-1 clave 123 — verbatim oficial, la guía la reproduce.
- "El pago llega en la etapa siguiente." desaparece al encenderse el CTA (guia-08 221-229).

### Mini-verificaciones accionables + comandos agnósticos de terminal (D-12)

**Source:** guia-05/07/08 — `uv run python -c "..."` con output esperado, URLs `http://localhost:5173/...` con qué observar, estados provocados a propósito (guia-05 Paso 11: login de ambos roles + token offline + 200 vs 403).
**Apply to:** las 3 guías. Casos concretos de la fase: los 4 flujos del navegador con la tarjeta de éxito, la carrera de stock con script de dos threads, la 302 observable (barra de direcciones del navegador), el voucher tras F5, el carro intacto tras anular.

### Evidencia runtime estructurada (para el spike doc y el UAT delegado)

**Source:** `02-UAT.md` frontmatter (1-8) + entradas `expected/result/evidence` (16-63).
**Apply to:** `03-SPIKE-RETORNO.md` y el futuro `03-UAT.md`. El spike registra por flujo: método real, params presentes, timing cronometrado, desviaciones vs docs. Los hallazgos del spike JAMÁS se citan como documento interno desde las guías (el alumno ve "lo que el spike reveló" narrado, D-40).

### Idioma y marcadores del producto

Español de Chile, tuteo, tono cercano (todos los docs vigentes). Los marcadores 🧠/✅/❌/📝 son contenido del producto SOLO dentro de las guías; los docs del ciclo (02/03/04) usan tablas, blockquotes y notas — mantener esa separación por tipo de documento. Sin emojis en comunicación con el usuario (AGENTS.md).

## No Analog Found

Todo deliverable del ciclo tiene análogo exacto de formato. Dos casos parciales:

| Archivo / bloque | Razón sin análogo exacto | Fuente |
|---|---|---|
| `.planning/phases/03-…/03-SPIKE-RETORNO.md` | Es el PRIMER spike de la serie — no existe documento de hallazgos de spike previo (fases 1-2 no tuvieron spikes). Análogo parcial: formato de evidencia de `02-UAT.md`; contenido esperado: tabla de 4 flujos de `03-RESEARCH.md` Pattern 3 (el spike la confirma/corrige con evidencia runtime) | 02-UAT.md (formato) + 03-RESEARCH.md Pattern 3 (contenido) |
| Bloques de código NUEVOS que las guías narran: `services/webpay.py` (Transaction.build_for_integration), `routers/retorno.py` (GET+POST + RedirectResponse 302 + Form TBK_*), discriminador de 4 flujos, UPDATE condicional de stock + rowcount, form auto-submit con document.createElement, `ResultadoPago.tsx` con voucher y vaciado condicional | Ningún repo del ecosistema tiene pagos (demo-cine tampoco); son el contenido nuevo de la etapa | 03-RESEARCH.md Patterns 1-8 (verificados contra SDK fuente, plugin oficial WooCommerce de Transbank, starlette responses.py, docs.sqlalchemy.org — ver Sources de RESEARCH) |

## Metadata

**Analog search scope:** `D:/Repos/demo-carro/docs/` completo (19 archivos git-trackeados) + `README.md` raíz + `.planning/phases/01-*/` y `02-*/` (artefactos de fases previas: PATTERNS, UAT). La referencia externa `D:/Repos/demo-cine/docs/` NO fue necesaria: todo el formato ya está establecido in-repo por las fases 1-2 (misma conclusión que 02-PATTERNS.md).
**Tracked-source gate:** todos los análogos nombrados verificados con `git ls-files -- <path>` (salida no vacía por archivo, corrida esta sesión): guia-05/07/08, adr/010, adr/011, contrato_api.yaml, 02_requerimientos.md, 03_diseno.md, docs/README.md, README.md, 05_desarrollo/README.md, 04_arquitectura/README.md, 02-UAT.md, 02-PATTERNS.md. Ninguna ruta mirror/gitignored emitida.
**Files scanned:** 13 análogos leídos/mapeados esta sesión — 10 completos (adr/011 71L, adr/010 69L, contrato_api.yaml 430L, 02_requerimientos.md 320L, 03_diseno.md 723L, guia-08 502L, docs/README 27L, README raíz 92L, 05_desarrollo/README 53L, 04_arquitectura/README 235L, 02-UAT.md 159L) + mapas estructurales por grep de guia-05 (1108L) y guia-07 (874L) — más 02-PATTERNS.md (417L, análogo directo de este documento) y 03-CONTEXT/03-RESEARCH del phase dir.
**Pattern extraction date:** 2026-09-30
