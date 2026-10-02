---
phase: 01-fundaciones-de-dos-tiers-y-cat-logo
reviewed: 2026-09-29T14:31:12Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - AGENTS.md
  - docs/05_desarrollo/guia-02-proyecto-frontend.md
  - docs/05_desarrollo/guia-04-catalogo.md
findings:
  critical: 0
  warning: 7
  info: 8
  total: 15
status: issues_found
---

# Phase 01: Code Review Report (incremental #3661)

**Reviewed:** 2026-09-29T14:31:12Z
**Depth:** standard
**Files Reviewed:** 3 (AGENTS.md, guia-02-proyecto-frontend.md, guia-04-catalogo.md)
**Status:** issues_found

## Summary

Revisión incremental de los 3 archivos que cambiaron desde el último commit de review (`a70c0b7`): el bloque nuevo de UAT delegado en `AGENTS.md`, el rediseño de la landing/paleta de `guia-02` (bloque `@theme` con la escala orange-* de Maura, `import "./index.css"` explícito, Navbar/Footer y landing a dos columnas con anillos/chips) y la sub-sección nueva de `guia-04` ("Las fotos también visten la landing") más ajustes visuales de espaciados.

`AGENTS.md` no genera hallazgos: es un bloque de memoria de instrucciones del usuario, consistente con lo registrado en `01-UAT.md` (workspace, `verified_by: agent (user-delegated)`, fix en dos lugares).

Lo nuevo verificado **sin** hallazgos: el override de `--color-orange-*` desde `@theme` es la forma documentada de Tailwind v4 y la fuente Nunito sí gobierna toda la página (preflight usa `--font-sans`); la advertencia nueva del `import "./index.css"` y la verificación del `dist/assets/index-*.css` son correctas y valiosas; el snippet del hero (foto `absolute inset-0` con `ring-8 ring-white`) calza exacto con los tres `div` de anillos que `guia-02` enseña; los valores citados contra la siembra de `guia-03` (Rosa de Río stock 2, Brisa de Naranja stock 14, 3 dulces, precios $6.990–$12.990, rangos 8000–9500 y 10000–11000) fueron verificados campo a campo contra `PRODUCTOS_DEMO`; el estado UAT en `D:/Repos/maura-uat` confirma que la landing rediseñada y las fotos se ejecutaron de punta a punta.

**Problemas:** 7 warnings y 8 infos. Cinco warnings y cuatro infos re-verifican hallazgos ya registrados como `open` en `01-REVIEW-DISPOSITION.md` que viven en los archivos de este scope (mismos defectos, re-anclados a las líneas actuales, IDs reutilizados sin pérdida en el disposition). Dos warnings y cuatro infos son nuevos del delta: el invariante de paleta que el propio código de `guia-04` rompe (`border-orange-300`), la instrucción de la foto en la card de familia que produce el kicker pegado a la imagen (el workspace UAT necesitó un `mt-4` que la guía no enseña), el `alt` del hero inerte bajo `aria-hidden` heredado, la landing rediseñada presentada como ejecución de §4.2 cuando el wireframe muestra otra estructura, el claim "npm install falla con EBADENGINE" y un typo.

**Nota de numeración:** los IDs `WR-01`..`WR-04`, `WR-08`, `IN-01`, `IN-02`, `IN-04`, `IN-05` se reutilizan para los mismos defectos de las filas `open` del disposition (ahora con anclas en este scope); los hallazgos inéditos usan `WR-09`, `WR-10`, `IN-10`..`IN-13` para no colisionar.

## Warnings

### WR-01: Contrato omite el 422 de `GET /api/productos/{producto_id}` — la fila 11 sigue mandando a compararlo sin advertirlo

**File:** `docs/05_desarrollo/guia-04-catalogo.md:294-302` (prose del Paso 3; ver también la fila 11 en `guia-04:988` y `docs/04_arquitectura/contrato_api.yaml:191-203`)
**Issue:** El prose enseña que con el `responses` declarado el panel lista 200, 404 y 422 para la ficha. Pero el contrato declara solo `'200'` y `'404'` para ese path: el 422 automático (validación del path param `producto_id: int`) no existe en `contrato_api.yaml`. La fila 11 (`guia-04:988`) ordena comparar "los códigos de respuesta (200, 404, 422)" UNO A UNO bajo el protocolo "cualquier diferencia entre el panel y el contrato es un desvío" (`guia-04:990-992`): el alumno encuentra un 422 en `/docs` que el contrato no declara, sin que la guía le diga que es un desvío del contrato (no de su código). Re-verificación del WR-01 del review anterior (disposition: open); el UAT test 4 confirmó que el alumno topa con este desvío no advertido.
**Fix:** Elegir un lado: (a) versionar `contrato_api.yaml` añadiendo `'422'` al path de la ficha (con `description: Path parameter mal formado (producto_id no entero)` y schema `Error`), o (b) una oración en el Paso 3 que nombre el desvío: "el 422 que verás junto al 404 es la validación del path param; el contrato aún no lo declara — desvío conocido del contrato, no un error de tu código".

### WR-02: `Error` presentado como "el cuerpo de los errores" — el 422 real de FastAPI trae `detail` como array, no string

**File:** `docs/05_desarrollo/guia-04-catalogo.md:87-89` (prose del Paso 1; ver `contrato_api.yaml:51-57` y `171-176`)
**Issue:** La oración presenta `Error` como "el cuerpo de los errores (`{"detail": "…"}`)". Es exacta para el 404 (string), pero el contrato referencia el mismo schema `Error` para el 422 de `GET /api/productos`, y el 422 real que FastAPI produce y documenta usa `detail` como ARRAY de objetos (`loc`, `msg`, `type`). El alumno que compara el 422 del panel contra el contrato en la fila 11 encuentra que ni la forma del cuerpo ni el schema coinciden — desvío no advertido, reforzado por una generalización ("los errores") que solo el 404 cumple. Re-verificación del WR-02 del review anterior (disposition: open).
**Fix:** Acotar la frase ("el cuerpo del 404 de la ficha — y, según el contrato, también del 422; ojo: el 422 real de FastAPI trae `detail` como array, desvío conocido del contrato") o versionar el contrato con un schema separado `ValidationError` para las 422.

### WR-03: El catálogo enseñado no distingue el 422 de familia inválida — incumple el diseño §3.4 ("se rechaza con un mensaje claro")

**File:** `docs/05_desarrollo/guia-04-catalogo.md:527-545` (bloque `isError` del `Catalogo`; ver prose del Paso 7 en `guia-04:741-745`)
**Issue:** La guía 4 le enseña al alumno a distinguir el 404 del error de red en la ficha (`ApiError` + `status`), pero el `Catalogo` sigue sin distinguir el 422: si el visitante llega con `?familia=vinagre` en la dirección (por ejemplo desde un link mal copiado), la API responde 422 y la pantalla muestra "Revisa que el backend esté corriendo en el puerto 8000 e inténtalo de nuevo" — consejo falso: el backend está arriba y corriendo. El diseño §3.4 fija "una familia fuera de la lista cerrada se rechaza con un mensaje claro (RN-01)". Re-verificación del WR-03 del review de fase (disposition: open).
**Fix:** Reutilizar el `ApiError` que el propio Paso 7 introduce: en el `Catalogo`, si `query.error instanceof ApiError && query.error.status === 422`, mostrar "El filtro de la dirección no es válido (familia o precio mal formado)" con un botón "Limpiar filtros" que llame a `limpiarFiltros()`.

### WR-04: `apiGet` asigna el `detail` del 422 (array) a una variable string — el mensaje de todo 422 se degrada a "[object Object]"

**File:** `docs/05_desarrollo/guia-04-catalogo.md:762-775` (`lib/api.ts` del Paso 7) y `docs/05_desarrollo/guia-02-proyecto-frontend.md:397-413` (`lib/api.ts` del Paso 8)
**Issue:** En ambas versiones enseñadas, `if (cuerpo?.detail) mensaje = cuerpo.detail;` asume que `detail` es string. El 422 de FastAPI trae `detail` como array de objetos; `mensaje` queda como array y `new Error(mensaje)` / `new ApiError(mensaje, ...)` coerciona con `String(array)` → `"[object Object]"`. El camino es real en el flujo de la guía: la mini-verificación 3 del Paso 3 provoca el 422, y el filtro por URL (`?precio_min=-5`, `?familia=vinagre`) lo hace llegar al `apiGet` de la SPA. Re-verificación del WR-04 del review de fase (disposition: open).
**Fix:** Normalizar antes de asignar, en ambos archivos:
```typescript
const cuerpo = await res.json();
const detalle = cuerpo?.detail;
if (typeof detalle === "string") mensaje = detalle;
else if (Array.isArray(detalle) && detalle[0]?.msg) mensaje = detalle[0].msg;
```

### WR-08: La fila 11 — "la comparación que cierra" la fase — no incluye el schema `Error` en la comparación de schemas

**File:** `docs/05_desarrollo/guia-04-catalogo.md:988` (fila 11)
**Issue:** La celda de schemas dice "los schemas (`ProductoResumen` con 6 campos, `ProductoDetalle` con 9)" — omite `Error`, el tercer schema del contrato y justamente el que la guía añadió en el Paso 1 para cerrar G-01-4. La evidencia formal de cierre no verifica `Error` contra `contrato_api.yaml:51-57`: si el schema enseñado divergiera del contrato, la tabla de cierre no lo detectaría. Re-verificación del WR-08 del review anterior (disposition: open).
**Fix:** Extender la celda: "los schemas (`ProductoResumen` con 6 campos, `ProductoDetalle` con 9, `Error` con `detail` string)".

### WR-09: El botón "Filtrar precio" usa `border-orange-300` — el único paso de la escala que el `@theme` nuevo NO sobrescribe, rompiendo el invariante enseñado

**File:** `docs/05_desarrollo/guia-02-proyecto-frontend.md:185-203` (bloque `@theme` + claim) y `docs/05_desarrollo/guia-04-catalogo.md:599` (uso)
**Issue:** El `@theme` nuevo de `guia-02` sobrescribe `orange-50/100/200/600/700` y enseña: "Cambiar el color de TODA la tienda será siempre editar esas cinco líneas: un solo lugar, cero componentes tocados". Pero el botón "Filtrar precio" del `Catalogo` (`guia-04:599`) usa `border-orange-300` — el único uso en ambas guías de un paso NO sobrescrito. Resultado doble: (a) el borde se pinta con el naranja genérico del framework (#fdba74, saturado), desentonando con la paleta crema/terracota de Maura (#ebd0ac / #d9480f) que lo rodea en la barra de filtros; (b) el invariante enseñado es falso — rebrandear editando las cinco líneas deja ese borde clavado en el default de Tailwind.
**Fix:** Añadir el paso que falta al `@theme` de `guia-02` (p. ej. `--color-orange-300: #e0a878;` en la línea de la paleta) — o, si la paleta de Maura no necesita 300, cambiar el botón a `border-orange-200`/`border-orange-600` en `guia-04:599`. Verificar después que ningún otro `orange-*` de las guías quede fuera del set sobrescrito.

### WR-10: La instrucción de la foto en la card de familia produce el kicker "Familia 0X" pegado a la imagen — el fix de espaciado (`mt-4`) no está enseñado

**File:** `docs/05_desarrollo/guia-04-catalogo.md:416-425` (instrucción "primera hija de la card, justo antes del kicker" + snippet sin margen)
**Issue:** El snippet enseña insertar el `<img>` como primera hija de la card de familia. En el `Landing.tsx` de `guia-02` (líneas 648-660), el kicker `<p>Familia 0{i + 1}</p>` no tiene margen superior (era primer hijo; todos los espaciados de la card son `mt-*` de los hermanos siguientes). Siguiendo la guía literalmente, el texto del kicker queda a distancia CERO del borde inferior de la foto — card visualmente aplastada, distinta de la que muestra la mini-verificación. Evidencia de que el defecto se materializa: el workspace UAT (`D:/Repos/maura-uat/frontend/src/features/landing/Landing.tsx:115`) necesitó agregar `mt-4` al kicker para separarlo de la foto — un parche que la guía nunca enseña y que el alumno no tiene por qué inventar.
**Fix:** Incluir el ajuste en la instrucción (o en el snippet): "…justo antes del kicker 'Familia 0X' — y súbele el margen: su clase pasa a ser `mt-4 text-xs font-bold uppercase tracking-widest text-orange-600`" (o `className="aspect-[4/3] w-full rounded-xl object-cover mb-4"` en el propio `<img>`).

## Info

### IN-01: "Única sección de toda la guía con URLs de terceros" — cierto dentro de guia-04, falso si "la guía" es la serie

**File:** `docs/05_desarrollo/guia-04-catalogo.md:353-357`
**Issue:** Verificado: dentro de `guia-04` la única sección con URLs externas es el Paso 4 (`unsplash.com`, `pexels.com`). Pero `guia-02:48-50` (Paso 1) contiene `nodejs.org` y `nvm-windows` — URLs de terceros en la misma serie de guías. La frase "de toda la guía" es ambigua y, leída como serie, contradice el invariante que anuncia. Re-verificación del IN-01 del review de fase (disposition: open).
**Fix:** Aclarar el alcance: "Esta es la única sección de ESTA guía con URLs de terceros" (o "…de las guías 2 a 4 fuera de los enlaces de instalación del Paso 1 de la guía 2").

### IN-02: `index.html` anuncia "dos cambios" pero son tres; y `src/react.svg` vive en `src/assets/` en el template actual

**File:** `docs/05_desarrollo/guia-02-proyecto-frontend.md:154-156` y `295-297`
**Issue:** El reemplazo de `index.html` elimina además el `<link rel="icon" … href="/vite.svg">` del template (y deja `public/vite.svg` huérfano, que la guía nunca manda borrar) — un tercer cambio no anunciado. Y el borrado final dice `src/react.svg`, pero el template react-ts actual lo trae en `src/assets/react.svg` (el alumno que busque `src/react.svg` no lo encuentra). Re-verificación del IN-02 del review de fase (disposition: open).
**Fix:** "tres cambios: el idioma, el título y fuera el favicon del template" + añadir `public/vite.svg` a la lista de borrado; corregir la ruta a `src/assets/react.svg`.

### IN-04: `guia-04` atribuye al diseño §4.4 umbrales de stock que el diseño no fija

**File:** `docs/05_desarrollo/guia-04-catalogo.md:729-731`
**Issue:** El prose dice "el diseño fija tres formas de disponibilidad (más de 3 → verde; 1 a 3 → ámbar '¡Últimas N unidades!'; 0 → 'Agotado')". El diseño §4.4 (`docs/03_diseno.md:325-327`) fija las tres FORMAS ("normal / última / agotada") pero ningún umbral ni color. Los umbrales (>3, 1-3) son decisión del código presentada como decisión del diseño — exactamente el patrón que la propia guía enseña a evitar. Re-verificación del IN-04 del review de fase (disposition: open).
**Fix:** "el diseño fija tres formas de disponibilidad (§4.4); los umbrales concretos (más de 3, 1 a 3) los fija este componente".

### IN-05: `BadgeDisponibilidad` produce "¡Últimas 1 unidades!" para stock=1 — no pluraliza como el resto de la pantalla

**File:** `docs/05_desarrollo/guia-04-catalogo.md:800-807`
**Issue:** `¡Últimas {stock} unidades!` con `stock === 1` rinde "¡Últimas 1 unidades!" — mientras el contador del catálogo (líneas 615-617) sí pluraliza ("1 aroma"). Con la siembra demo nunca ocurre (stocks 2 y 3 son los bajos), pero el componente es la regla que el panel de la fase 4 reutilizará. Re-verificación del IN-05 del review de fase (disposition: open).
**Fix:** `¡Últimas {stock} {stock === 1 ? "unidad" : "unidades"}!`

### IN-10: El `alt` de la foto del hero no tiene efecto — el contenedor conserva el `aria-hidden="true"` de los anillos y la guía no indica quitarlo

**File:** `docs/05_desarrollo/guia-04-catalogo.md:404-409` (snippet del hero) y `docs/05_desarrollo/guia-02-proyecto-frontend.md:609` (`aria-hidden` heredado)
**Issue:** `guia-02` marca la columna visual con `aria-hidden="true"` (correcto para anillos decorativos). La sub-sección nueva de `guia-04` convierte esos anillos en la foto del producto y le enseña un `alt="Body splash artesanal de Maura"` — pero como el `aria-hidden` del ancestro sigue (la guía no dice quitarlo), ese `alt` jamás llega al árbol de accesibilidad: se enseña a escribir un atributo que no hace nada. El workspace UAT lo remedió quitando el `aria-hidden` (`maura-uat/.../Landing.tsx:63`), divergencia que la guía no refleja.
**Fix:** En el Paso 4 de `guia-04`, al instruir el reemplazo, añadir: "y quita el `aria-hidden=\"true\"` del contenedor — los anillos eran decoración, la foto ya es contenido".

### IN-11: La landing rediseñada se presenta como §4.2 "cómo se ve" — pero el wireframe de §4.2 es de una columna centrada, un solo CTA y footer de una línea

**File:** `docs/05_desarrollo/guia-02-proyecto-frontend.md:525-542` (prose del Paso 10; el diseño en `docs/03_diseno.md:216-258`)
**Issue:** El prose abre citando `docs/03_diseno.md §4.2: cómo se ve` y afirma "Tres decisiones de copy ya están tomadas y no se negocian en código". Lo que §4.2 efectivamente fija (tagline como texto más grande, párrafo en primera persona, cards de familia con "Ver aromas →" al catálogo filtrado) está respetado. Pero el hero a dos columnas con anillos/chips, el segundo CTA "Conoce las familias ↓", el link "Ver todo el catálogo →", los kickers numerados "Familia 0X", el eyebrow "en mayúsculas espaciadas" y el footer en tres piezas no existen en el diseño — el wireframe de §4.2 muestra un hero centrado de una columna con un solo botón y un footer de una línea. El alumno que compare contra §4.2 (que la cita lo invita a hacer) encuentra otra estructura sin que la guía distinga qué viene del diseño y qué es decisión libre del desarrollador. Mismo patrón que IN-04.
**Fix:** Una oración que separe las fuentes: "del diseño vienen el tagline, el párrafo y las cards con su link filtrado (§4.2); la composición a dos columnas, el círculo y los chips son decisión de esta guía — el wireframe es un boceto, no una cárcel".

### IN-12: "npm install falla con el warning EBADENGINE" — npm no falla: con la configuración por defecto es un warning no fatal

**File:** `docs/05_desarrollo/guia-02-proyecto-frontend.md:30-37`
**Issue:** Con Node < 22.22, `npm install` de react-router 8 emite `EBADENGINE` como WARNING y completa la instalación (solo falla si el alumno tiene `engine-strict=true`). La guía dice "falla con el warning EBADENGINE y un proyecto inválido": el alumno con Node 22.18 verá el install terminar bien y con un warning, contradiciendo la advertencia que lo motivó a actualizar. El gate (verificar `node -v`) sigue siendo correcto; la descripción del síntoma no.
**Fix:** "por debajo de eso, `npm install` completa con el warning `EBADENGINE` — y te deja un proyecto en una combinación de versiones que nadie probó".

### IN-13: Typo en la mini-verificación del Paso 10: "el tagline … ENorme"

**File:** `docs/05_desarrollo/guia-02-proyecto-frontend.md:687`
**Issue:** "el tagline 'Frescura que te acompaña' ENorme" — capitalización media ("ENorme") que se lee como typo de "enorme" (no es un recurso estilístico usado en el resto de la guía).
**Fix:** "el tagline 'Frescura que te acompaña' enorme".

---

_Reviewed: 2026-09-29T14:31:12Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
