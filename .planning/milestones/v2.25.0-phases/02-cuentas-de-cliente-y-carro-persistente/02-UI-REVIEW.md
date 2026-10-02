# Phase 2 — UI Review

**Audited:** 2026-09-30
**Baseline:** 02-UI-SPEC.md (approved 2026-09-29, 6 PASS + 1 FLAG no bloqueante)
**Screenshots:** captured — 18 files (6 rutas × 3 viewports) en `.planning/ui-reviews/02-20260930-083914/` desde la implementación de referencia viva en `localhost:5173` (maura-uat, construida verbatim desde las guías). Nota: el entorno sube los PNG a CDN sin entregar el render al auditor, por lo que los hallazgos visuales/interacción son derivados del código (guías + referencia) y respaldados por el UAT runtime de hoy (02-UAT.md, 12/12 filas PASS, sin scroll horizontal a 375px).
**Interaction captures:** off (workflow.ui_interaction_capture is false)

**Naturaleza del auditado (D-17, guide-only):** el "frontend implementado" son los bloques TSX enseñados en guia-06/07/08; la referencia `D:/Repos/maura-uat/frontend/src` se usó como cross-check de drift (sin drift: copies locked, `aria-live`, `Math.min`, focus rings presentes en los 7 archivos).

---

## Pillar Scores

| Pillar | Score | Key Finding |
|--------|-------|-------------|
| 1. Copywriting | 3/4 | Los ~25 copies locked verbatim; 2 strings no declarados en el contrato, uno con redacción divergente de la familia de error contratada |
| 2. Visuals | 3/4 | Jerarquía/focal/a11y conformes; el skeleton del checkout no preserva el layout de la fila real y "Comprobando tu sesión…" queda fuera del sistema de cards |
| 3. Color | 4/4 | 60/30/10 respetado; accent estrictamente en la lista reservada; cero colores hardcodeados; banners semánticos según tabla |
| 4. Typography | 3/4 | Cero pesos prohibidos y presupuesto de tamaños intacto; el body del empty state usa `text-sm` siendo contratado como Body `text-base` |
| 5. Spacing | 3/4 | Cero valores fuera de escala y 44px en todo target; 4 variantes de utilidad fuera del whitelist literal (`py-4`, `pt-4`, `ms-2`, `space-y-2`) |
| 6. Experience Design | 3/4 | Las 15 consideraciones de estado implementadas y verificadas en runtime; la fila degradada 404 del checkout pierde la acción "Quitar" contratada |

**Overall: 19/24**

---

## Top 3 Priority Fixes

> Por instrucción persistida del usuario: los fixes se aplican en AMBOS lugares — la guía (`docs/05_desarrollo/*`, el producto) y la referencia (`maura-uat`, para mantener el UAT verde).

1. **Fila degradada 404 del checkout sin "Quitar"** (guia-08-checkout.md:158-165) — la clienta con un aroma eliminado del catálogo ve "Este aroma ya no está disponible" en el checkout pero no puede sacarlo ahí: debe regresar a /carro para limpiarlo, rompiendo el circuito sin puntos muertos que la propia guía promete — agregar el botón "Quitar" a la fila degradada del checkout (mismo `estiloQuitar` de FilaCarro) o amend el UI-SPEC para contractar explícitamente su ausencia ("el checkout no edita: vuelve al carro"); hoy el Copywriting Contract ("+ acción Quitar") y la sección Checkout ("mismas reglas ... que /carro") dicen una cosa y la guía hace otra.
2. **Copies de fallback de red no contratados y divergentes** (guia-06-sesion-frontend.md:510 y :655) — ante un error distinto de 401/409, login y registro muestran "No pudimos conectar con el servidor. Revisa que el backend esté corriendo en el puerto 8000.", string ausente del Copywriting Contract y que abandona el sufijo contratado de la familia ("...e inténtalo de nuevo.") con otra frase inicial — unificar la familia (o bien "Revisa que el backend esté corriendo en el puerto 8000 e inténtalo de nuevo." con lead "No pudimos conectar con el servidor.") y agregar la fila correspondiente al Copywriting Contract del UI-SPEC para que quede locked como D-26.
3. **Body del empty state en `text-sm` siendo Body `text-base`** (guia-07-carro.md:468) — la tabla Typography del UI-SPEC asigna "copy de estados vacíos" al rol Body (`text-base`); el `<p>` "Explora los aromas de Maura y agrega tus favoritos." usa `text-sm`, y lo mismo hacen las causas de error de carro (guia-07:491) y checkout (guia-08:98) — cambiar `text-sm` → `text-base` en el body del empty state (y decidir/Documentar si las causas de error son "avisos" Label `text-sm` o Body `text-base`; hoy están en el limbo).

---

## Detailed Findings

### Pillar 1: Copywriting (3/4)

Conformidad verificada por grep string a string contra el Copywriting Contract — presentes y verbatim en las guías (y en la referencia maura-uat): "Agregar al carro", "Finalizar compra", "Pagar con Webpay" + "El pago llega en la etapa siguiente.", "Iniciar sesión"/"Crear cuenta" + "Ingresando…"/"Creando cuenta…", "Tu carro está vacío" + body + "Ver catálogo", "Credenciales incorrectas", "Ese email ya tiene cuenta, inicia sesión", "Escribe un email válido."/"La contraseña debe tener al menos 8 caracteres.", "No pudimos cargar tu carro"/"No pudimos cargar tu pedido" + causa puerto 8000 + "Reintentar", "Este aroma ya no está disponible" + "Quitar" (en /carro), "Ya tienes todo el stock disponible en tu carro.", "Tu sesión expiró, ingresa de nuevo", "Cuenta creada. Ingresa con tu email y contraseña.", "Mínimo 8 caracteres.", "¿Vaciar todo el carro?" + "Sí, vaciar"/"Cancelar", cross-links, links del navbar, los 4 h1, labels "Email"/"Contraseña", "Comprando como {email}", "← Volver al carro". Cero labels genéricos (sin "Submit"/"OK"/"Click here"); español de Chile con tuteo consistente; precios con `Intl.NumberFormat es-CL CLP`.

**Findings:**
- **WARNING:** string no declarado "No pudimos conectar con el servidor. Revisa que el backend esté corriendo en el puerto 8000." como fallback de error no-401/no-409 en Login (guia-06:510) y Registro (guia-06:655) — diverge de la familia contratada ("Revisa que el backend esté corriendo en el puerto 8000 e inténtalo de nuevo.") en lead y sufijo.
- **WARNING:** string no declarado "Comprobando tu sesión…" (guia-06:452) — estado de carga del login con sesión guardada, ausente del contrato (el contrato solo declara gerundios de submit).
- **Minor:** aria-label del badge hace pluralización correcta ("1 unidad"/"N unidades") — bien, pero el patrón no está en el contrato (informativo).

### Pillar 2: Visuals (3/4)

Focal claro por pantalla (CTA full-width terracota + PageTitle `text-2xl md:text-3xl font-extrabold`), un solo `h1` por pantalla en las 4 rutas y en los estados de error, jerarquía exclusivamente por tamaño/peso/color contratados. Sistema sin íconos según spec: steppers de texto "−"/"+" con `aria-label` por botón y nombre de producto (guia-07:334, :345); punto decorativo del navbar con `aria-hidden` (heredado). Thumbnails con `alt` = nombre y `loading="lazy"` (guia-07:300-305). Focus rings `focus-visible:ring-2 ring-orange-600` en todo interactivo nuevo (grep: 26 ocurrencias en las guías; presentes en los 7 archivos de la referencia).

**Findings:**
- **WARNING:** el skeleton de línea del checkout es una sola barra `h-6 w-2/3` (guia-08:149) — la sección "Estados async" del UI-SPEC exige "fila skeleton con el mismo layout de la fila real (sin shift)" para carro Y checkout; la fila real del checkout es nombre-enlazado + "× N" + precio alineado a la derecha. El skeleton de FilaCarro (guia-07:252-260) sí cumple.
- **WARNING (minor):** "Comprobando tu sesión…" (guia-06:451-453) se renderiza como texto plano fuera del sistema de cards/skeletons — estado transitorio sin tratamiento visual, inconsistente con el patrón skeleton del resto de la fase.
- **Minor:** la fila de /carro recibe tratamiento de card (`bg-white rounded-2xl border border-orange-100`, guia-07:295) no prescrito en el contrato de fila ("`flex gap-4 items-center`, `p-4`") — consistente con el design system (rounded-2xl para cards, bordes orange-100), informativo.
- **Minor:** divisor del Total del checkout con `border-t-2` (guia-08:203) vs `divide-y` (1px) entre líneas — dos pesos de divisor en la misma card.

### Pillar 3: Color (4/4)

Distribución 60/30/10 verificada por conteo de clases: dominante blanco (página, cards de login/registro/checkout, filas, inputs `bg-white`); secundario crema orange-50 (navbar heredado, panel de resumen guia-07:571, `bg-orange-50/90` navbar) con bordes suaves orange-100/200; accent terracota estrictamente acotado. Conteos en las guías: `bg-orange-600` ×11 (2 submits, Agregar al carro guia-07:169, Finalizar compra guia-07:586, Pagar con Webpay guia-08:216, badge del navbar guia-07:713, Ver catálogo guia-07:473, Reintentar ×2), `text-orange-600` ×5 (Cerrar sesión, cross-links ×2, ← Volver al carro, link activo), `hover:bg-orange-700` ×7, `ring-orange-600` ×26. Banners semánticos exactos a la tabla: ámbar `bg-amber-100 text-amber-800` (guia-06:473), esmeralda `bg-emerald-100 text-emerald-800` (guia-06:478), rojo `bg-red-50 text-red-600` (guia-06:507, :652), todos `rounded-2xl p-4 text-sm`. "Agotado" `bg-neutral-200 text-neutral-700` (guia-07:326). Destructive red-600 en "Quitar"/"Vaciar carro"/"Sí, vaciar" y espejos de validación. Cero colores hex/rgb en los bloques TSX de las guías (grep vacío). El accent jamás aparece en headings (neutral-900), fondos de sección ni banners.

**Findings:**
- **Minor (informativo):** "Ver catálogo" y "Reintentar" ×2 se implementan como botones llenos orange-600; la lista reservada del UI-SPEC los describe como "acciones de texto" (item 6) o no prescribe estilo — defendible porque el sistema tiene UN solo estilo de botón y la propia sección Typography del spec agrupa "Ver catálogo" con los CTAs de fase 1. Sugerencia: aclarar en el spec cuáles son las superficies llenas autorizadas.

### Pillar 4: Typography (3/4)

Pesos usados: `font-bold` ×25 y `font-extrabold` ×9 — exactamente los declarados (400 implícito, 700, 800); **cero** `font-medium`/`font-semibold`/`font-light` (grep vacío, prohibición respetada). Tamaños: `text-sm` ×39, `text-base` ×7, `text-lg` ×2 (token de precio por línea), `text-xl` ×5 (headings/nombres), `text-2xl`/`text-3xl` (PageTitle con `md:`) — presupuesto de 6 tamaños/3 pesos intacto, sin tamaños nuevos. Tokens de precio correctos: línea `text-lg font-extrabold text-orange-700` (guia-07:354, guia-08:194), Total `text-2xl font-extrabold text-orange-700` (guia-07:579, guia-08:208). Labels `text-sm font-bold` con `htmlFor` ×4 (guia-06:487, :495, :626, :636).

**Findings:**
- **WARNING:** la tabla Typography asigna "copy de estados vacíos" al rol Body `text-base`; el body del empty state del carro usa `text-sm` (guia-07:468 "Explora los aromas de Maura y agrega tus favoritos."). Las causas de error (guia-07:491, guia-08:98) también van en `text-sm` — defendibles como "avisos" (Label), pero el spec no las clasifica.
- **Minor:** los headings de bloque de error usan el rol Heading (`text-xl font-bold`, guia-07:488, guia-08:95) en vez de PageTitle — mapeo razonable no contratado (informativo).
- Se hereda el FLAG del checker 2026-09-29: la tabla de roles omite el token de precio `text-lg` que la sección contrata — inconsistencia interna del spec, no de la implementación.

### Pillar 5: Spacing (3/4)

Inventario completo de spacing en los bloques TSX de fase 2: `gap-2/4/6` ✓, `p-4/6/8` ✓ (`md:p-8` en cards), `px-2/4/6` ✓, `py-1/2/16` ✓, páginas `px-4 py-16` ✓, grilla carro `md:grid-cols-3 gap-6` con filas `md:col-span-2` ✓ (guia-07:521-522). **Cero valores fuera de la escala de 8 puntos**: sin `py-3`/`px-3`/`2.5` en código nuevo (el único `py-3` es la estructura del navbar heredada que el propio UI-SPEC preserva textualmente) y sin valores arbitrarios `[px]`/`[rem]` (grep vacío). Targets interactivos: `min-h-11` ×19 + stepper `h-11 w-11` ×3 (44×44) ✓; número del stepper `w-8 text-center` ✓; email `truncate max-w-32` ✓; thumbnail `w-20 h-20` (80px) ✓.

**Findings:**
- **WARNING:** 4 variantes de utilidad fuera del whitelist literal del spec ("Solo utilidades de esta escala... Exceptions: none"): `py-4` ×3 (filas `<li>` del checkout, guia-08:147/161/174), `pt-4` ×1 (divisor del Total, guia-08:203), `ms-2` ×3 (badge/× N/chip Agotado, guia-07:713, guia-08:184/188), `space-y-2` ×1 (skeleton de fila, guia-07:254) — todas con valores ON-scale (16px/8px), o sea la escala se respalda pero el whitelist se excede en la letra.
- **Minor:** los márgenes (`mt-1/2/4/6`, `md:mt-0`) nunca fueron enumerados por el spec — todos en pasos de la escala (4/8/16/24); hueco del contrato, no drift.
- **Nota:** el navbar heredado `px-4 py-3` y el punto `h-2.5 w-2.5` provienen de guia-02 (fase 1) y el UI-SPEC los declara inalterables — no son hallazgos de esta fase.

### Pillar 6: Experience Design (3/4)

Cobertura de estados verificada contra las 15 filas del UI-Considerations probe — todas implementadas en el código de las guías y runtime-verificadas hoy por el UAT delegado (02-UAT.md: 12/12 filas PASS de la Gran verificación final, incluyendo badge vivo tras F5, tope castigado editando localStorage, fila degradada con id 999, checkout returnTo de punta a punta, sin scroll horizontal a 375px):
- **Empty:** carro → página completa reemplazada (guia-07:462-479); checkout → `Navigate /carro replace` (guia-08:84-86); forms inician vacíos con labels persistentes sin placeholders.
- **Loading:** fila skeleton con layout real en /carro (guia-07:252-260) + skeleton del Total (guia-07:577, guia-08:206); submits `disabled` + gerundio (guia-06:519, :664); badge sin estado de carga (store síncrono) según contrato.
- **Error:** 401/409 en banner dentro de la card con copies locked (guia-06:506-512, :651-657); error general con Reintentar (`refetch`, guia-07:485-503, guia-08:88-110); fila degradada 404 distinguendo error de red vía `ApiError.status` (guia-07:530-534); interceptor 401 solo-con-Bearer eximiendo el login (guia-06 paso 4, Pitfall 5 narrado 3 veces).
- **Partial/overflow/zero-one-many/long-text:** stock 0 → badge "Agotado" sin stepper sin total (guia-07:325-328, :353); navbar y fila con `flex-wrap`; badge oculto en 0, unidades no ítems, `aria-live="polite"` + `aria-label` (guia-07:707-717); email `truncate max-w-32` + `title`.
- **Destructivos:** vaciado en dos pasos inline con booleano de estado, sin modal ni `window.confirm` (guia-07:540-568); "Quitar" sin confirmación con la asimetría justificada.
- **Guard:** `RequireAuth` con `Navigate state={{ from: location }} replace` (guia-06:340) y login devolviendo `location.state?.from?.pathname ?? "/"` (guia-06:428); lección guard=UX/seguridad=401/403 dicha explícita (guia-06 paso 5, guia-08 paso 2).

**Findings:**
- **WARNING:** la fila degradada 404 del checkout (guia-08:158-165) no ofrece "Quitar" — el Copywriting Contract adjunta la acción a ese copy y la sección Checkout dice "mismas reglas que /carro". El ítem muerto solo se limpia volviendo al carro.
- **WARNING:** los estados de error de red de login/registro están cubiertos pero con copy no contratado (ver Pillar 1) — cobertura sí, contrato no.
- **Minor:** sin ErrorBoundary a nivel app — consistente con el patrón por-query de fase 1 y no contratado (informativo).
- **Nota:** el ajuste post-hidratación se escribe de vuelta al store (guia-07:452-459), más allá del "se tapa en pantalla" del UI-SPEC — cite docs/03 §4.7 y mantiene badge/localStorage/pantalla consistentes; excede en buen sentido.

---

## Registry Safety

Registry audit: skipped — no existe `components.json` (repo guide-only, D-17) y el UI-SPEC declara `shadcn_initialized: false` / third-party: none. Sin bloques de registro de terceros que vetar.

---

## Files Audited

**Entregable bajo auditoría (guías = el producto):**
- `docs/05_desarrollo/guia-06-sesion-frontend.md` (934 líneas — Login, Registro, Navbar, RequireAuth, useAuthStore, lib/api.ts + interceptor)
- `docs/05_desarrollo/guia-07-carro.md` (853 líneas — useCarroStore, botón de ficha, FilaCarro, Carro, badge del navbar)
- `docs/05_desarrollo/guia-08-checkout.md` (493 líneas — Checkout, ruta protegida, Gran verificación final)

**Referencia viva (cross-check de drift, read-only):**
- `D:/Repos/maura-uat/frontend/src/features/cuentas/Login.tsx`, `Registro.tsx`
- `D:/Repos/maura-uat/frontend/src/features/carro/Carro.tsx`, `FilaCarro.tsx`
- `D:/Repos/maura-uat/frontend/src/features/checkout/Checkout.tsx`
- `D:/Repos/maura-uat/frontend/src/components/Navbar.tsx`, `RequireAuth.tsx`
- `D:/Repos/maura-uat/frontend/src/stores/useAuthStore.ts`, `useCarroStore.ts`
- `D:/Repos/maura-uat/frontend/src/features/catalogo/FichaProducto.tsx` (botón Agregar al carro)

**Contexto y baseline:**
- `.planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-UI-SPEC.md` (baseline del audit)
- `.planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-CONTEXT.md`, `02-03-PLAN.md`, `02-04-PLAN.md`, `02-01..05-SUMMARY.md`, `02-UAT.md`
- `docs/05_desarrollo/guia-02-proyecto-frontend.md` (solo verificación de origen del navbar heredado)
- Screenshots: `.planning/ui-reviews/02-20260930-083914/` (18 PNG, git-ignored)

---

## Recommendation Count

- **Priority fixes:** 3 (fila 404 sin Quitar en checkout; familia de copy de error de red no contratada y divergente; empty-state body en `text-sm` vs Body `text-base`)
- **Minor recommendations:** 6 (skeleton de checkout sin layout de fila real; "Comprobando tu sesión…" fuera del sistema visual; variantes de spacing fuera del whitelist `py-4`/`pt-4`/`ms-2`/`space-y-2`; superficies accent llenas no enumeradas Ver catálogo/Reintentar; divisor `border-t-2` vs `divide-y`; clasificar causas de error como Label o Body en el spec)
