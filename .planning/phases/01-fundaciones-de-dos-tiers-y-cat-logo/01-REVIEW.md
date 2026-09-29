---
phase: 01-fundaciones-de-dos-tiers-y-cat-logo
reviewed: 2026-09-28T20:40:57Z
depth: standard
files_reviewed: 21
files_reviewed_list:
  - README.md
  - docs/README.md
  - docs/01_necesidad_del_cliente.md
  - docs/02_requerimientos.md
  - docs/03_diseno.md
  - docs/04_arquitectura/README.md
  - docs/04_arquitectura/contrato_api.yaml
  - docs/04_arquitectura/adr/001-arquitectura-en-capas.md
  - docs/04_arquitectura/adr/002-dos-tiers-spa-y-api.md
  - docs/04_arquitectura/adr/003-monorepo.md
  - docs/04_arquitectura/adr/004-frontend-typescript.md
  - docs/04_arquitectura/adr/005-sqlite-y-create-all.md
  - docs/04_arquitectura/adr/006-uv-como-gestor.md
  - docs/04_arquitectura/adr/007-api-first.md
  - docs/04_arquitectura/adr/008-repositorio-solo-guias.md
  - docs/05_desarrollo/README.md
  - docs/05_desarrollo/guia-01-proyecto-backend.md
  - docs/05_desarrollo/guia-02-proyecto-frontend.md
  - docs/05_desarrollo/guia-03-modelos-y-seed.md
  - docs/05_desarrollo/guia-04-catalogo.md
findings:
  critical: 0
  warning: 7
  info: 8
  total: 15
status: issues_found
---

# Phase 01: Code Review Report

**Reviewed:** 2026-09-28T20:40:57Z
**Depth:** standard
**Files Reviewed:** 21
**Status:** issues_found

## Summary

Repositorio guide-only (D-17): los entregables son las guías markdown + el contrato OpenAPI, no código de aplicación. La revisión verificó trazabilidad de la cadena D/P/C/CS → RF/RNF/RN/HU → diseño → ADRs → contrato → guías, corrección del código enseñado, integridad del contrato, invariante guide-only y salud markdown/enlaces.

**Verificado sin hallazgos (base sólida):**
- El invariante guide-only se cumple: no existe `backend/` ni `frontend/` en el repo; ningún documento instruye commitear código a ESTE repo (la "Sugerencia commit" de guia-04 dice explícitamente "en TU proyecto"); el commit `fc93522` citado por ADR-008 existe.
- `contrato_api.yaml` parsea como OpenAPI 3.0.3 válido (3 paths, schemas `Error`/`ProductoResumen`/`ProductoDetalle`).
- Los 12 SKU canónicos coinciden entre diseño §4.3/§4.4 (wireframes con precios), seed de guia-03 y verificaciones de guia-04; precios 6990–12990 CLP, stocks con exactamente dos valores ≤3 (`citricas-03`=3, `florales-03`=2), ninguno en 0.
- Slugs `citricas/florales/frutales/dulces` idénticos caracter por caracter en RN-01, contrato, enum Python, tipos TS y `FAMILIA_LABELS`.
- Los IDs citados existen: STORE-01..04, GUIDE-02, CART-01..03, AUTH-01..04, PAY-01..04, ADMN-01..04, AIAS-01..03 (cuentas exactas en `.planning/REQUIREMENTS.md`); los 8 ADRs existen y todos los links relativos resuelven.
- Los estados de las tablas de fases de ambos READMEs son actuales (fases 1-4 ✅, fase 5 🚧 parcial guías 1-4, 6-8 ⏳); vallas de código balanceadas en los 21 archivos; los bloques de código de guia-01..04 son coherentes entre sí (rutas, nombres, firmas, verificaciones ✅ ejecutables).

**Problemas principales:** el contrato omite el 422 que FastAPI genera inevitablemente en `GET /api/productos/{producto_id}` y documenta mal el cuerpo del 422 (schema `Error` con `detail` string vs array real de FastAPI) — la fila 11 de la Gran Verificación (contrato ↔ `/docs`) produce un desvío falso en el cierre formal de fase. En el frontend enseñado, el catálogo no distingue el 422 de una familia inválida por URL editada (incumple diseño §3.4 "rechazada con un mensaje claro") y `apiGet` degrada el mensaje de todo 422 a `"[object Object]"`. Hay dos cortes de trazabilidad en la cadena (diseño §5 sin RNF-02/RNF-03; validación de §10 de requerimientos sin implementación) y una mezcla "etapa"/"fase" que hace que "fase 3" signifique dos cosas distintas en el README raíz.

## Warnings

### WR-01: Contrato omite el 422 de `GET /api/productos/{producto_id}` — la verificación de cierre de fase produce un desvío falso

**File:** `docs/04_arquitectura/contrato_api.yaml:191-203`
**Issue:** El contrato declara solo `200` y `404` para la ficha. Pero el router enseñado en guia-04 (`producto_id: int` como path param) hace que FastAPI genere automáticamente una respuesta `422` en el `/docs` para validación del parámetro de ruta (p. ej. `/api/productos/abc`). La fila 11 de la Gran Verificación final (guia-04:911) ordena comparar "los códigos de respuesta (200, 404, 422)" de los 3 paths contra `/docs`: cualquier alumno que compare fielmente encuentra un 422 en `/docs` que el contrato no declara — un desvío que no es del código del alumno sino una omisión del contrato, y cuyo protocolo de resolución ("el código corrige, o el contrato se versiona y se aprueba de nuevo") convertiría el cierre de fase 1 de cada estudiante en una revisión espuria del contrato.
**Fix:**
```yaml
# en paths./api/productos/{producto_id}.get.responses, agregar junto a '200' y '404':
        '422':
          description: Path parameter mal formado (producto_id no entero)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
```

### WR-02: Schema `Error` documenta mal el cuerpo del 422 (`detail` string vs array real de FastAPI)

**File:** `docs/04_arquitectura/contrato_api.yaml:51-57` (uso en 171-176)
**Issue:** El contrato define `Error.detail` como `type: string` y lo referencia para el 422 de `GET /api/productos`. El 422 producido por la validación declarativa de FastAPI (la que guia-04 enseña y celebra en el paso 3) tiene cuerpo `{"detail": [{"type": ..., "loc": ["query","familia"], "msg": ..., ...}]}` — un array de objetos, no un string. El contrato, declarado "fuente de la verdad de la interfaz", documenta incorrectamente la forma del único cuerpo de error 422 que la fase 1 produce realmente.
**Fix:** Agregar un schema separado y referenciarlo en las respuestas 422:
```yaml
    ValidationError:
      type: object
      properties:
        detail:
          type: array
          items:
            type: object
            properties:
              loc: { type: array, items: { type: string } }
              msg: { type: string }
              type: { type: string }
      required: [detail]
```
(Mantener `Error` con `detail: string` para el 404, que sí es string.)

### WR-03: El catálogo enseñado no distingue el 422 de familia inválida — incumple el diseño §3.4 ("se rechaza con un mensaje claro")

**File:** `docs/05_desarrollo/guia-04-catalogo.md:452-469`
**Issue:** El diseño pone los filtros en la URL precisamente para compartirla (§4.1) y su proceso 2.0 exige que "una familia fuera de la lista cerrada se rechaza con un mensaje claro (RN-01)" (`docs/03_diseno.md:160-164`). Pero el `Catalogo.tsx` de guia-04 trata todo error con el mismo bloque: "No pudimos cargar el catálogo / Revisa que el backend esté corriendo en el puerto 8000 e inténtalo de nuevo" — abrir `/productos?familia=vinagre` (URL editada o compartida mal) con el backend perfecto muestra un diagnóstico falso de "backend apagado". La ficha sí distingue el 404 con `ApiError.status` (paso 7); el catálogo no aplica el mismo patrón al 422.
**Fix:**
```tsx
if (query.isError) {
  const esValidacion =
    query.error instanceof ApiError && query.error.status === 422;
  return (
    // … mismo bloque, pero:
    // título: esValidacion ? "Filtro inválido" : "No pudimos cargar el catálogo"
    // texto:  esValidacion
    //   ? "La familia de la dirección no es válida. Limpia los filtros e intenta de nuevo."
    //   : "Revisa que el backend esté corriendo en el puerto 8000 e inténtalo de nuevo."
    // acción: esValidacion ? botón "Limpiar filtros" (limpiarFiltros) : "Reintentar"
  );
}
```

### WR-04: `apiGet` asigna el `detail` del 422 (array) a una variable string — el mensaje de todo 422 se degrada a "[object Object]"

**File:** `docs/05_desarrollo/guia-04-catalogo.md:685-699` (reemplaza el de guia-02:371-388)
**Issue:** `let mensaje = \`Error HTTP ${res.status}\`; ... if (cuerpo?.detail) mensaje = cuerpo.detail;` — para el 422 de FastAPI, `cuerpo.detail` es un array de objetos, no un string: `new Error(array)` lo stringifica a `"[object Object]"`. La guía enseña que el 422 "nombra el valor rechazado" (paso 3) pero ese valor jamás sobrevive el paso por `apiGet` en el frontend; queda un `Error.message` inútil que además contradice la disciplina de tipos que la propia guía predica (compila solo porque `res.json()` es `any`). Si un alumno renderiza `{query.error.message}` (patrón natural), muestra basura.
**Fix:**
```typescript
const cuerpo = await res.json();
const detalle = cuerpo?.detail;
if (typeof detalle === "string") mensaje = detalle;        // 404 del backend
else if (Array.isArray(detalle) && detalle[0]?.msg)        // 422 de FastAPI
  mensaje = String(detalle[0].msg);
```

### WR-05: Diseño §5 (trazabilidad requerimiento → diseño) omite RNF-02 y RNF-03

**File:** `docs/03_diseno.md:335-351` (promesa en línea 5)
**Issue:** El encabezado de la fase promete "cada elemento de este diseño **nace de un requerimiento** (RF/RNF/RN/HU) y la trazabilidad está en §5", pero la tabla §5 no tiene fila para **RNF-02** (rendimiento local) ni para **RNF-03** (recorrido sin cuenta). RNF-03 aparece mencionado en las reglas de §3.3 pero no en la tabla formal; RNF-02 no aparece en ninguna sección del diseño. Para un material cuya propuesta de valor central es "trazabilidad completa", dos RNF sin fila en la tabla de trazabilidad son un corte del hilo que los alumnos replicarán como plantilla.
**Fix:** Agregar a la tabla §5: `| RNF-02 (respuesta rápida local) | §4.3 estados de carga (esqueletos sin esperas largas; caché de TanStack Query en guia-04) |` y `| RNF-03 (todo sin cuenta) | §3.3 reglas del proceso 1.0 |`, o declarar explícitamente por qué quedan fuera del diseño (p. ej. propiedad de la fase de arquitectura/pruebas).

### WR-06: Requerimientos §10 declara una validación de rango de precio que ni el contrato ni la guía 4 implementan

**File:** `docs/02_requerimientos.md:164`
**Issue:** La tabla de entradas declara como validación clave del rango de precio: "Enteros ≥ 0; mínimo no mayor que el máximo efectivo de resultados esperados". Ninguna pieza posterior la implementa: el contrato solo valida `minimum: 0` por parámetro individual (contrato_api.yaml:146-161) y el router de guia-04 solo declara `ge=0`. Un rango invertido (`precio_min=11000&precio_max=8000`) no se "rechaza" en ninguna parte — produce 0 resultados y cae en el estado vacío. Además la redacción "máximo efectivo de resultados esperados" no corresponde a ningún concepto definido en la cadena. La regla declarada en fase 2 muere ahí: quiebra la trazabilidad que el documento promete.
**Fix:** O bien eliminar la segunda mitad de la validación en §10 (dejar "Enteros ≥ 0", que es lo implementado, y remitir el rango invertido al estado vacío de HU-02), o bien implementarla en el contrato como regla documentada (p. ej. `description` del parámetro `precio_max`: "debe ser ≥ precio_min si ambos vienen") y en el router con `Query` + validación explícita de 400/422 — pero algo debe ceder: no pueden quedar divergentes.

### WR-07: "Fase" vs "etapa": el mismo eje (carro → pago → panel/IA) recibe dos nombres y "fase 3" significa dos cosas distintas en el README raíz

**File:** `README.md:72` (también `README.md:42`, `docs/04_arquitectura/README.md:115-117`, `docs/04_arquitectura/adr/002-dos-tiers-spa-y-api.md:14`, `docs/05_desarrollo/guia-03-modelos-y-seed.md:39-44`, `docs/05_desarrollo/guia-04-catalogo.md:953`)
**Issue:** `02_requerimientos.md` define el eje de construcción del proyecto como **etapas** ("etapa 1 del proyecto… P5 → etapa 2, P6 → etapa 3, P7/P8 → etapa 4", líneas 24-44) y ADR-001/005 también usan "etapa". Pero el README raíz, el documento de arquitectura, ADR-002/006 y las guías usan **"fase"** para el mismo eje ("Webpay… (fase 3)", "Gemini (fase 4)", "fase 2 — cuentas y carro"). Mientras tanto, "fase" ya nombra las 8 fases del ciclo de vida en las tablas de ambos READMEs, donde la fase 3 es **Diseño**. Resultado: en el mismo archivo, `README.md:40` dice "Fase 3: Diseño ✅" y `README.md:72` dice "Webpay… (fase 3)" — dos significados de "fase 3" a 30 líneas de distancia, en la portada del producto. Para material educativo cuyo eje es el ciclo de vida por fases, la ambigüedad es un defecto real de consistencia.
**Fix:** Normalizar en una pasada: usar "fase" exclusivamente para las 8 fases del ciclo (docs) y "etapa" para las etapas de construcción del proyecto (como ya lo hace 02_requerimientos), ajustando README:42/72, 04_arquitectura §3, ADR-002/006 y las menciones "fase 2/3/4" de guías 3-4 (p. ej. "Webpay… (etapa 3)").

## Info

### IN-01: URLs externas fuera del paso de fotos — contradice el invariante declarado de "única sección con URLs de terceros"

**File:** `docs/05_desarrollo/guia-01-proyecto-backend.md:9`, `docs/05_desarrollo/guia-02-proyecto-frontend.md:48`
**Issue:** El invariante registrado en `.planning/STATE.md:87` (y repetido en guia-04:318-319: "Esta es la única sección de toda la guía con URLs de terceros") no se sostiene: guia-01 enlaza `https://docs.astral.sh/uv/` y guia-02 enlaza `https://nodejs.org` (prerrequisitos de instalación), fuera del paso de descarga de fotos (guia-04 paso 4). Son benignas (documentación de herramientas, no assets), pero la afirmación de unicidad es falsa tal cual.
**Fix:** O restringir la afirmación a "única sección con URLs de terceros para **assets** de la aplicación", o quitar los enlaces (dejar "busca uv docs / nodejs.org" como texto plano). Nota: guia-04:325 menciona `unsplash.com`/`pexels.com` sin esquema — esas sí son del paso permitido.

### IN-02: guia-02 indica borrar `src/react.svg`, pero en el template actual el archivo vive en `src/assets/react.svg`; y el reemplazo de `index.html` es un tercer cambio no anunciado

**File:** `docs/05_desarrollo/guia-02-proyecto-frontend.md:154-170, 272-274`
**Issue:** "Borra `src/App.tsx`, `src/App.css` y `src/react.svg`" — el scaffold react-ts de Vite trae el logo en `src/assets/react.svg` (no en `src/react.svg`): el alumno busca un archivo que no existe en la ruta dicha. Además el bloque de `index.html` se presenta como "dos cambios" (idioma y título) pero también elimina el `<link rel="icon">` del template, dejando `public/vite.svg` huérfano — un tercer cambio silencioso.
**Fix:** "borra `src/App.tsx`, `src/App.css` y `src/assets/react.svg`" y "tres cambios: idioma, título y fuera el favicon del template (queda huérfano; puedes borrar también `public/vite.svg`)".

### IN-03: Identificador "D1" sobrecargado entre fases y dolores D1–D6 sin trazabilidad explícita hacia P

**File:** `docs/01_necesidad_del_cliente.md:38-43`, `docs/03_diseno.md:131-134`, `docs/02_requerimientos.md:188-206`
**Issue:** "D1–D6" son los dolores en fase 1; "D1" es el almacén Productos del DFD en fase 3 (más "A1"); y las decisiones de planificación son "D-XX". Un alumno que siga el hilo "D1" entre documentos encuentra dos conceptos distintos sin notas que lo aclaren. Además, la tabla de trazabilidad de fase 2 (§13) mapea P/C/CS pero no los dolores D1–D6: la derivación D→P es solo narrativa. No rompe nada, pero el material enseña que "ningún requerimiento aparece de la nada" y el primer eslabón del hilo queda implícito.
**Fix:** Renombrar el almacén del DFD (p. ej. `A0` o `D-productos`) o una nota a pie en §3.2 de diseño ("el D1 de este DFD no guarda relación con los dolores D1–D6 de la fase 1"); opcionalmente agregar a §13 una mini-columna o nota que mapee cada P al dolor que resuelve (P2→D1, P5→D2/D3, P7→D5, …).

### IN-04: guia-04 atribuye al diseño §4.4 umbrales de stock que el diseño no fija

**File:** `docs/05_desarrollo/guia-04-catalogo.md:652-655` (vs `docs/03_diseno.md:327-329`)
**Issue:** El 🧠 del paso 7 dice "el diseño fija tres formas de disponibilidad (más de 3 → verde; 1 a 3 → ámbar «¡Últimas N unidades!»; 0 → «Agotado»)". El diseño §4.4 define las tres formas pero **sin umbrales numéricos** (solo ejemplifica stock 2 con el badge ámbar). El corte `<= 3` es una decisión de la guía presentada como si viniera del diseño — exactamente el tipo de atribución imprecisa que el material pide evitar al razonar el alumno.
**Fix:** "el diseño fija tres formas (normal / últimas / agotado, §4.4); el corte numérico lo decido yo aquí: ≤ 3 unidades cuenta como «últimas» (con `citricas-03`=3 y `florales-03`=2 en el demo)".

### IN-05: `BadgeDisponibilidad` produce "¡Últimas 1 unidades!" para stock=1 — no pluraliza como el resto de la pantalla

**File:** `docs/05_desarrollo/guia-04-catalogo.md:715-735`
**Issue:** El contador del catálogo pluraliza correctamente ("1 aroma", línea 539) y la línea de la ficha también ("1 unidad", líneas 854-858), pero el badge enseña `¡Últimas {stock} unidades!` sin condicional: con stock=1 renderiza "¡Últimas 1 unidades!". El demo no tiene stock=1, pero el componente se declara reutilizable para el panel de la etapa 4, donde aparecerá.
**Fix:** `stock === 1 ? "¡Última unidad!" : \`¡Últimas ${stock} unidades!\`` — o el mismo patrón ternario que ya enseña el contador.

### IN-06: README de 05_desarrollo duplica el mismo párrafo de cierre a 8 líneas de distancia

**File:** `docs/05_desarrollo/README.md:31-34, 40-43`
**Issue:** "Las guías 5+ llegan con las fases siguientes… cada una asumiendo que estas están construidas y verificadas en tu máquina" (líneas 31-34) y "Las fases siguientes del proyecto… agregan las guías 5+ sobre esta base — cada una asumiendo que las anteriores están construidas y verificadas en tu máquina" (40-43) repiten la misma idea casi textual en el mismo bloque "Mapa mental".
**Fix:** Dejar una sola formulación (la del mapa mental) y cerrar la tabla anterior con solo "Las guías 5+ llegan con las etapas siguientes del proyecto."

### IN-07: `descripcion` no reproduce la longitud 1000 del diccionario de datos, pese a la afirmación "campo a campo, sin agregar ni quitar"

**File:** `docs/05_desarrollo/guia-03-modelos-y-seed.md:187` (vs `docs/03_diseno.md:64`, afirmación en guia-03:153-156, 199-202)
**Issue:** El diccionario §2.2 fija `descripcion` con longitud 1000; el modelo enseñado usa `Text` sin límite (`sku`=20, `nombre`=120, `imagen`=200 sí llevan longitud). La guía afirma traducir el diccionario "sin agregar ni quitar" y "Diez campos, diez columnas" — la restricción de longitud de `descripcion` es la única que se pierde en el camino, sin mencionarlo.
**Fix:** O `mapped_column(String(1000))` (equivalente en SQLite, explícito para el alumno), o una nota: "la longitud 1000 del diccionario es de diseño; el modelo usa `Text` y la frontera no la exige (el schema Pydantic la validará si algún día importa)".

### IN-08: Typo en requerimientos §3: "para que el hilo quedé completo"

**File:** `docs/02_requerimientos.md:60`
**Issue:** "quedé" (pretérito, 1ª persona) por "quede" (subjuntivo).
**Fix:** "…para que el hilo **quede** completo desde hoy."

---

_Reviewed: 2026-09-28T20:40:57Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
