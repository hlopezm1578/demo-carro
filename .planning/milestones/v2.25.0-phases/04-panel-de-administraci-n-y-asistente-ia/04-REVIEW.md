---
phase: 04-panel-de-administraci-n-y-asistente-ia
reviewed: 2026-10-01T15:39:07Z
depth: standard
files_reviewed: 14
files_reviewed_list:
  - README.md
  - docs/02_requerimientos.md
  - docs/03_diseno.md
  - docs/04_arquitectura/README.md
  - docs/04_arquitectura/adr/002-dos-tiers-spa-y-api.md
  - docs/04_arquitectura/adr/017-asistente-ia-mini-rag-key-solo-backend.md
  - docs/04_arquitectura/adr/018-asistente-ia-groq-structured-outputs.md
  - docs/04_arquitectura/contrato_api.yaml
  - docs/05_desarrollo/README.md
  - docs/05_desarrollo/guia-12-panel-backend.md
  - docs/05_desarrollo/guia-13-panel-spa.md
  - docs/05_desarrollo/guia-14-asistente-backend.md
  - docs/05_desarrollo/guia-15-asistente-cierre.md
  - docs/README.md
findings:
  critical: 0
  warning: 8
  info: 5
  total: 13
status: issues_found
---

# Phase 4: Code Review Report

**Reviewed:** 2026-10-01T15:39:07Z
**Depth:** standard
**Files Reviewed:** 14
**Status:** issues_found

## Summary

Revisión adversarial del corpus documental post-rework Gemini→Groq (D-63..D-68). El rework está, en lo grueso, sólido: grep sobre los 14 archivos confirma **cero menciones de Gemini/google-genai fuera de las excepciones sancionadas** (cuerpo de ADR-017 byte-intacto, evidencia histórica de ADR-018, blockquote de apertura de guia-14), **cero apariciones de la cifra vetada 14.400** en todo `docs/`, **18 archivos ADR = 18 filas del índice = "18 ADRs" citados** en READMEs y guia-15, cadena `Siguiente` de guias 12→13→14→15 correcta, contrato 0.4.0 verificado agnóstico del proveedor, y los bloques de código enseñados de guia-12/13/14/15 son internamente consistentes con el contrato campo a campo (topes 500/10/3, copys locked del 409/429/503 idénticos entre yaml y routers, `ConfigDict(extra="forbid")` + `required` completo como exige strict, pin `groq>=1.7,<2` y `MODELO_ASISTENTE = "openai/gpt-oss-120b"` coherentes en guía/ADR/tabla de stack, límites siempre 30 RPM / 1.000 RPD / 8K TPM / 200K TPD con fuente).

Lo que queda son 8 warnings y 5 infos, concentrados en tres familias: (1) una **derivación aritmética falsa** de las cifras del free tier en guia-14 (1.000 RPD ≠ 16 consultas/minuto sostenidas), (2) **restos del barrido D-66/D-67**: la justificación Gemini-era del 429 ("no son públicas") que la decisión ordena que muera sigue viva en guia-15, y referencias operativas a ADR-017 como capa técnica vigente en docs/03 y docs/04 tras la supersession, y (3) defectos puntuales de trazabilidad y de verificación (RN-08 mal citada en guia-13, comando de arranque inconsistente, variante PowerShell del grep de seguridad no recursiva). Nada impide que el alumno complete las guías, pero todo son defectos del producto-educativo que deben corregirse.

## Critical Issues

_(ninguna)_

## Warnings

### WR-01: Aritmética falsa: "1.000 RPD ≈ 16 consultas por minuto sostenidas todo el día"

**File:** `docs/05_desarrollo/guia-14-asistente-backend.md:40` y `:376`
**Issue:** 1.000 requests/día sostenidos parejos durante 24 h dan 1.000/1.440 ≈ **0,7 consultas por minuto** (≈41 por hora). "16 consultas por minuto" sale de dividir por 60 (una hora), no por 1.440 (un día): 16/min sostenido todo el día requeriría ~23.040 RPD — 23 veces la cuota real. La guía presenta esta equivalencia junto a la disciplina "cifras citadas con fuente" (D-68), así que el alumno que haga la cuenta encontrará una contradicción en el propio material que le enseña a no firmar cifras sin fuente. Ocurre dos veces: tabla de términos ("Free tier") y 🧠 del paso 5.
**Fix:**
```markdown
# en ambas ocurrencias, reemplazar la equivalencia:
- 1.000 RPD ≈ 41 consultas por hora (≈0,7 por minuto) sostenidas todo el día: de sobra para el curso
# o, si se quiere hablar de ráfaga:
- 1.000 RPD y 30 RPM: una hora de clase a 16 consultas por minuto consume el día entero de cuota
```

### WR-02: La justificación Gemini-era del 429 ("no son públicas") sobrevive al rework — D-66 ordena que muera

**File:** `docs/05_desarrollo/guia-15-asistente-cierre.md:142`, `:257`, `:473`
**Issue:** La decisión D-66 (04-CONTEXT.md) dice literalmente: *El paréntesis "sin cifras de límites (no son públicos sin login)" muere con Groq (D-68)*. Aun así, guia-15 lo conserva dos veces — 🧠 del paso 2 "(SIN cifras — no son públicas)" y comentario del código "429 cuota SIN cifras (no son públicas sin login)" — y el 🧠 del paso 4 repite el marco viejo "cifras que nadie puede verificar (concern abierto)". Esto contradice de frente a ADR-018 ("el concern RPM/RPD que Gemini dejaba abierto... muere con Groq") y a la propia guia-14 (🧠 paso 5: "con las cifras públicas a la vista, porque Groq SÍ las publica"). El copy sin cifras está bien (decisión de UX); la *razón* enseñada es la falsa. Es un miss del barrido D-67 en el propio archivo que el rework dice haber ajustado.
**Fix:** Cambiar la justificación, no el copy: "429 cuota SIN cifras (los límites por organización viven en la consola de Groq; el copy le habla a la clienta, no al dev — D-68)" y en el 🧠 del paso 4 reemplazar "(concern abierto)" por "(concern cerrado por D-68: las cifras del tier son públicas)".

### WR-03: Referencias operativas a ADR-017 como registro vigente tras la supersession (barrido incompleto en el README de arquitectura)

**File:** `docs/04_arquitectura/README.md:163` y `:199`
**Issue:** El barrido actualizó la tabla de stack (línea 122 cita ADR-018 "que supersede al ADR-017") pero dejó dos citas que apuntan a ADR-017 como la capa técnica *operativa* del asistente: el comentario del árbol de código "routers/asistente.py # POST /api/asistente — público, topes en el borde y 503/429 amables (AIAS-01..03, ADR-017)" (línea 163) y la regla de dependencia 3 "el 503/429 lo decide el router ([ADR-017](...))" (línea 199). El alumno que siga esos punteros aterriza en el ADR del proveedor muerto sin marca previa de supersession en el texto que lo cita. D-67 declaró el barrido "COMPLETO" incluyendo el índice de ADRs.
**Fix:** En ambas líneas citar ADR-018 (o "ADR-017 superseded por ADR-018"), como ya hace la línea 122 y la fila 017 del índice.

### WR-04: docs/03 sigue declarando "su capa técnica es ADR-017" para el mini-RAG

**File:** `docs/03_diseno.md:243` y `:289`
**Issue:** El mismo archivo fue actualizado a Groq por el rework (§3.1 "la etapa 4 suma a Groq", proceso 15.0 con `GEM["Groq (asesora IA)"]`), pero la decisión 17 mantiene "*(D-56; su capa técnica es ADR-017.)*" y la nota posterior "el asistente mini-RAG con la API key solo en el backend en **ADR-017**" — en presente, como registro vigente. Post-supersession, la capa técnica viva del mini-RAG/key-solo-backend es ADR-018 (que declara "la muralla D-56 queda PRESERVADA íntegra"). Inconsistencia interna del propio documento: nombra a Groq pero referencia al ADR del proveedor muerto.
**Fix:** "*(D-56; su capa técnica es ADR-018 — antes ADR-017, superseded.)*" o simplemente "ADR-018", en ambas líneas.

### WR-05: La fila del índice de ADR-017 cita D-63, que el cuerpo del propio ADR no registra

**File:** `docs/04_arquitectura/README.md:235`
**Issue:** La fila 017 del índice dice "(AIAS-01..03, D-56, **D-63**, D-61; superseded por 018)", pero el cuerpo de ADR-017 (byte-intacto por mandato de D-65) resuelve "decisiones **D-56/D-59/D-60/D-61**". D-63 es la decisión del rework y pertenece a ADR-018 — que la fila 236 ya cita como "D-63..D-68". El sweep reemplazó D-60 por D-63 en la fila 017, rompiendo la correspondencia índice↔cuerpo y la semántica histórica de la fila (lo que ese ADR decidió fue el patrón D-60, hoy roto/superseded por D-63).
**Fix:** Restaurar D-60 en la fila 017: "(AIAS-01..03, D-56, D-60, D-61; superseded por 018)" — D-63 vive en la fila 018.

### WR-06: RN-08 citada cuatro veces para el "404 uniforme de ownership", que es otra regla

**File:** `docs/05_desarrollo/guia-13-panel-spa.md:1032`, `:1044`, `:1563`, `:1667`
**Issue:** Guia-13 justifica el link ausente al voucher con "el endpoint de detalle es del DUEÑO del pedido (404 uniforme de ownership, **RN-08**)" — en el 🧠 del paso 7, el comentario del código de `AdminPedidos.tsx`, el bloque de errores 3 y el cierre. RN-08 es la regla del carro ("el carro guarda solo identificadores y cantidades"): no tiene relación con el ownership del detalle. La referencia correcta es RF-17/§3.13 del diseño ("el pedido de otra clienta no existe para el sistema") o D-47. En un corpus cuya propuesta de valor es la trazabilidad exacta, cuatro citas al número equivocado son un defecto real del material.
**Fix:** Reemplazar "RN-08" por "RF-17 (§3.13 del diseño)" — o "D-47" — en las cuatro ocurrencias.

### WR-07: Comando de arranque `uv run fastapi dev app/main` (sin `.py`) — único caso en todo el corpus

**File:** `docs/05_desarrollo/guia-14-asistente-backend.md:701`
**Issue:** La mini-verificación del paso 7 manda encender la API con `uv run fastapi dev app/main`. Ocho guías (1, 2, 4, 5, 9, 12, 13 y la propia 15) usan `uv run fastapi dev app/main.py`. Las formas documentadas de fastapi-cli son archivo `.py` o import string con `:` (`app/main:app`); la ruta con slash sin extensión ni `:app` no está soportada documentadamente y, según la versión del CLI, puede no resolverse — el alumno tropezaría en el paso de verificación más simple de la guía. Aun en el mejor caso (que el CLI lo tolere), la inconsistencia con el resto del corpus es un copy-paste desalineado.
**Fix:** `uv run fastapi dev app/main.py desde backend/`.

### WR-08: La variante PowerShell del grep de seguridad (fila 13) no es recursiva — puede dar un falso éxito

**File:** `docs/05_desarrollo/guia-15-asistente-cierre.md:530`
**Issue:** La fila 13 (la prueba mecánica de AIAS-03: que la key jamás llegó al bundle) ofrece como alternativa PowerShell `Select-String -Path dist\* -Pattern "GROQ_API_KEY"`. `-Path dist\*` solo expande los hijos directos de `dist/`: el bundle JS vive en `dist/assets/*.js`, así que el comando **jamás escanea el único archivo donde una key filtrada aparecería**, y además emite errores no terminales al toparse con los subdirectorios. Un alumno en PowerShell obtiene "cero coincidencias" sin haber mirado el bundle — exactamente el falso éxito que una verificación de seguridad no puede permitirse, en el único entorno (Windows) donde el curso corre.
**Fix:** `Get-ChildItem dist -Recurse -File | Select-String -Pattern "GROQ_API_KEY"` (y control positivo equivalente con `"Pregúntale a Maura"`), dejando `grep -r` de Git Bash como ruta primaria.

## Info

### IN-01: "1-3 cards" en el encabezado y fila 8 de guia-15, pero el contrato permite 0-3

**File:** `docs/05_desarrollo/guia-15-asistente-cierre.md:9` y `:525`
**Issue:** El encabezado ("con 1-3 cards del catálogo real") y la fila 8 de la Gran verificación prometen "1-3 cards", mientras guia-14 (paso 8: "cards: entre 0 y 3"), el propio prompt del sistema ("Si nada del catálogo calza, responde sin productos") y la verificación #4 de guia-15 ("0-3 cards") establecen que **0** cards es una respuesta correcta del contrato.
**Fix:** "con 0-3 cards" en ambas ocurrencias.

### IN-02: Fechas de documento/aprobación anteriores al contenido reworkado que contienen

**File:** `docs/02_requerimientos.md:7`, `:443-448`; `docs/03_diseno.md:7`
**Issue:** docs/02 (header "Fecha: 2026-09-28", aprobación de etapa 4 "documentada el 2026-09-30") y docs/03 (mismo header) fueron editados por el rework (RNF-09 ya cita D-63, decidida el 2026-10-01; §3.1 ya dice Groq) sin nota de actualización ni ajuste de fecha. En un corpus que data cada decisión, el contenido ahora postdata su propia aprobación en silencio.
**Fix:** Agregar una línea "Actualizado 2026-10-01 (rework proveedor IA, D-63..D-68)" al header de ambos documentos, sin tocar las tablas de aprobación históricas.

### IN-03: Import `Pedido` sin uso en el bloque enseñado de `services/admin.py`

**File:** `docs/05_desarrollo/guia-12-panel-backend.md:620`
**Issue:** El bloque de `services/admin.py` importa `from app.models.pedido import EstadoPedido, Pedido`; `EstadoPedido` se usa en `MetricasService.calcular`, pero `Pedido` no aparece en ninguna anotación ni uso del archivo mostrado. El ruff del alumno cantará F401 sobre código copiado literal.
**Fix:** `from app.models.pedido import EstadoPedido`.

### IN-04: Filas 10 y 12 de la Gran verificación citan solo ADR-017 (superseded)

**File:** `docs/05_desarrollo/guia-15-asistente-cierre.md:527`, `:529`
**Issue:** Defendible (ADR-018 declara que la lógica de degradación D-61 y la muralla D-56 de ADR-017 "se mantienen íntegras"), pero la fila 8 de la misma tabla ya usa la forma completa "ADR-017/ADR-018". Uniformar evita que el alumno rastree el ADR muerto como primera parada.
**Fix:** "ADR-017/ADR-018" en las filas 10 y 12, como la 8.

### IN-05: Drift fuera del diff: el stack de investigación aún recomienda `google-genai` (observación, fuera de los 14 archivos)

**File:** `D:\Repos\demo-carro\AGENTS.md:25`, `:58` (espejo de `.planning/research/STACK.md`)
**Issue:** El stack autoritativo del proyecto (embebido en AGENTS.md) sigue diciendo "IA: Google Gemini vía SDK oficial `google-genai`" con pin `>=2.25,<3`, mientras el corpus revisado enseña `groq>=1.7,<2`. No está en el alcance de este review (D-67 cubrió 12 archivos de `docs/`), pero cualquier investigación futura que consulte el STACK heredará el proveedor muerto.
**Fix:** Actualizar la fila IA de `.planning/research/STACK.md` a groq (por flujo GSD), que se refleja en AGENTS.md.

---

_Reviewed: 2026-10-01T15:39:07Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
