---
phase: 04-panel-de-administraci-n-y-asistente-ia
plan: 07
subsystem: docs
tags: [groq, sdk-pin, structured-outputs, json-schema, strict-mode, guias, rework]

requires:
  - phase: 04-panel-de-administraci-n-y-asistente-ia (planes 04-01..06 ejecutados; 04-06 onda R1)
    provides: ADR-018 (swap firmado con evidencia), contrato 0.4.0 agnóstico (D-66), 04-RESEARCH.md regenerado (Patterns 1-3/6 + Ejemplos A/B probe-verified 2026-10-01) — la FUENTE del contenido nuevo de guia-14
provides:
  - guia-14 reescrita "como si Groq siempre hubiera sido" (D-65): blockquote del swap, SDK groq pinneado >=1.7,<2, key del alumno en console.groq.com, json_schema strict con extra="forbid", wrapper RateLimitError/GroqError sin retry casero, MODELO_ASISTENTE + models.list, cifras 30 RPM/1.000 RPD con fuente (D-68)
  - guia-15 ajustada sin tocar el esqueleto: grep del build con GROQ_API_KEY + control positivo + variante Select-String (Pitfall 8), filas 8-10/13 de la Gran verificación final, nota honesta console.groq.com/D-63, conteo 18 ADRs
affects: [04-08 (barrido D-67 final + taller: re-verifica el grep del build contra esta guía; las guias 12-13 one-liners siguen pendientes ahí)]

actuals:
  tokens: 17283      # chars/4 sobre el diff realizado (69.135 chars en 2 archivos)
  tasks: 2
  commits: 2         # medido: git rev-list --count 753816c..HEAD
  plan_head_before: 753816c97a3019533cca3ea91de92fd166258648
  plan_head_after: 61aff278563b1803c7f2c9357d8c1dd01f1533c1

tech-stack:
  added: []          # guide-only (D-17): sin código; el SDK groq >=1.7,<2 se enseña DENTRO de guia-14
  patterns:
    - "Blockquote de migración D-65: TODA mención al proveedor muerto confinada a un solo blockquote pre-términos, gates awk de región en ambas direcciones"
    - "Pin piso/techo del corpus aplicado a groq: piso probe-verified 1.7.0, techo <2 (misma forma del fix D-4-6)"
    - "json_schema strict + ConfigDict(extra=\"forbid\") como doble duty: requisito del servicio Y validación backend más estricta (Pitfall 2)"

key-files:
  created: []
  modified:
    - docs/05_desarrollo/guia-14-asistente-backend.md
    - docs/05_desarrollo/guia-15-asistente-cierre.md

key-decisions:
  - "guia-14 enseña el aislamiento con `grep -r \"from groq\" backend/app` (no `grep -r groq` a secas como decía el plan): config.py contiene groq_api_key y el grep pelado listaría DOS archivos — la lección de IN-06 es sobre el IMPORT, y así el comando es literalmente cierto para el alumno"
  - "El wrapper del service conserva un tercer `except Exception` → AsistenteNoDisponible además de RateLimitError/GroqError: un model_validate_json fallido no es GroqError y sin esa frontera cruzaría como 500 — la regla jamás-500 (IN-06) queda completa como en la guía vieja"
  - "Las dos descripciones del router se alinearon al wording agnóstico EXACTO que el plan 04-06 dejó en contrato_api.yaml l.1463/1471 ('del servicio de IA', 'servicio caído') — responses y copys locked byte-intactos (D-66, diff de precisión verificado pre y post commit)"
  - "Fila 8 de la Gran verificación final cita 'ADR-017/ADR-018' (la historia y el registro vigente, mismo criterio del corpus de no borrar la historia)"

patterns-established:
  - "Gate de región awk bidireccional para barridos de proveedor: ≥1 mención histórica ANTES del ancla (el blockquote narra la migración), CERO después (el cuerpo vive en presente)"
  - "Cifras de terceros citadas con URL + 'a la fecha de esta guía' + pointer a la fuente viva de la org (D-68) — nunca la cifra refutada"

requirements-completed: [AIAS-01, AIAS-02, AIAS-03]

coverage:
  - id: D1
    description: "guia-14 reescrita a Groq punta a punta (blockquote D-65, pin >=1.7,<2, key console.groq.com, json_schema strict + extra=forbid, wrapper 429/503 sin retry casero, MODELO_ASISTENTE + models.list, cifras 30 RPM/1.000 RPD con fuente)"
    requirement: AIAS-02
    verification:
      - kind: other
        ref: "gate <verify> Task 1 (g14-rework-ok): pin/key/import/constante/json_schema/strict/extra=forbid/model_json_schema/model_validate_json/RateLimitError/GroqError/additionalProperties/models.list/30 RPM/1.000 RPD/rate-limits/'a la fecha'/reintenta/auto-pickup/ADR-018/uv remove google-genai presentes; sin gsk_/AIza/14.400/truststore/Interactions API; gates awk de región en ambas direcciones; 8 🧠 / 11 mini-verificaciones"
        status: pass
      - kind: other
        ref: "diff de precisión del bloque router (Paso 6) vs HEAD pre-commit: SOLO 2 descripciones a 'servicio de IA'/'servicio caído'; Paso 7 y Siguiente byte-idénticos (diff vacío)"
        status: pass
    human_judgment: false
  - id: D2
    description: "guia-15 ajustada: grep del build con GROQ_API_KEY (CERO coincidencias + control positivo, Select-String, Pitfall 8), filas 8-10, nota honesta console.groq.com/D-63, ADR-018 en Origen, 18 ADRs — esqueleto intacto"
    requirement: AIAS-03
    verification:
      - kind: other
        ref: "gate <verify> Task 2 (g15-rework-ok): cero gemini/google-genai; GROQ_API_KEY+dist/, Select-String, console.groq.com/D-63, ADR-018, 18 ADRs sin 17; locked content (BurbujaAsesora, bienvenida, aria-live, ProductCard, useMutation, copy 503, Reintentar, 0.4.0, Authorize, npm run build, fase 5) intacto; sin dangerouslySetInnerHTML"
        status: pass
      - kind: other
        ref: "diff de precisión pre-commit: 19+/17- líneas, solo las menciones mapeadas + conteo 17→18 + fix AI Studio (desviación documentada)"
        status: pass
    human_judgment: false

duration: 16min
completed: 2026-10-01
status: complete
---

# Phase 4 Plan 7: Rework guias Groq Summary

**guia-14 reescrita "como si Groq siempre hubiera sido" (blockquote D-65 → ADR-018, SDK groq >=1.7,<2 con json_schema strict + extra="forbid", wrapper 429/503 sin retry casero, cifras 30 RPM/1.000 RPD con fuente) y guia-15 ajustada al grep del build GROQ_API_KEY con 18 ADRs — con las menciones históricas confinadas al blockquote por gates awk de región**

## Performance

- **Duration:** 16 min
- **Started:** 2026-10-01T14:44:18Z
- **Completed:** 2026-10-01T15:00:47Z
- **Tasks:** 2/2 (2 auto)
- **Files modified:** 2

## Accomplishments
- guia-14 (869 → 1005 líneas, 393+/257-): mitad de integración reescrita con contenido 100% de 04-RESEARCH.md — Paso 1 `uv add "groq>=1.7,<2"` piso/techo + nota OpenAI-compatible; Paso 2 key del alumno en console.groq.com (mostrada UNA sola vez, patrón D-08/D-63) con `.env.example` GROQ_API_KEY= vacía; Paso 3 `groq_api_key: str | None = None` con el 🧠 fail-fast byte-casi-intacto; Paso 4 `Recomendacion` gana `ConfigDict(extra="forbid")` con mini-verificación del schema emitido (`False ['productos', 'respuesta']`); Paso 5 con `from groq import Groq, GroqError, RateLimitError`, `MODELO_ASISTENTE = "openai/gpt-oss-120b"` (ceremonial D-64 + 🧠 de deprecación), client lazy con construcción DENTRO del try, `api_key` explícita (IN-03), response_format json_schema strict firmado doc+probe, muralla D-56 intacta, cifras 30 RPM / 1.000 RPD / 8K TPM / 200K TPD con URL + "a la fecha" (D-68)
- Pasos 6-7 y Siguiente byte-intactos salvo las 2 descripciones del router al wording agnóstico del contrato (D-66) — verificado con diff quirúrgico pre y post commit
- "❌ El error que este archivo evita" reescrito a 6 lecciones: VITE_ (con grep del build GROQ_API_KEY), `model_json_schema()` pelado con strict (nueva lección nº 2, reemplaza al drift de la Interactions API), ids en el frontend, fail-fast + 500 crudo, retry casero (SDK reintenta 2x INCLUYENDO el 429, ~2-4 s), auto-pickup del entorno
- guia-15 (19+/17-): GEMINI_API_KEY → GROQ_API_KEY en paso 4/filas 10-13/punto de control 5/aprendizajes; fila 13 con control positivo + Select-String + findstr-from-Git-Bash anotado como corrosivo (Pitfall 8); fila 9 "antes de tocar el servicio de IA"; nota honesta (console.groq.com, D-63); fila 8 Origen ADR-017/ADR-018; 17→18 ADRs en commit sugerido y Siguiente — BurbujaAsesora, copys locked, montaje y Gran verificación final intactos

## Task Commits

Each task was committed atomically:

1. **Task 1: guia-14 reescrita — Groq con json_schema strict** - `95904f7` (docs)
2. **Task 2: guia-15 ajustada — grep GROQ_API_KEY, filas 8-13, 18 ADRs** - `61aff27` (docs)

**Plan metadata:** commit final de cierre (docs: complete plan)

## Files Created/Modified
- `docs/05_desarrollo/guia-14-asistente-backend.md` - La mitad de integración reescrita de google-genai a groq; blockquote del swap D-65; estructura canónica completa (8 🧠, 11 mini-verificaciones, errores evitados, punto de control, aprendizajes, Siguiente)
- `docs/05_desarrollo/guia-15-asistente-cierre.md` - Ajustes puntuales de clave y conteo sin tocar el esqueleto (burbuja, copys locked, montaje, Siguiente → fase 5)

## Decisions Made
- Aislamiento enseñado como `grep -r "from groq" backend/app`: el `grep -r groq` pelado del plan listaría también `config.py` (campo `groq_api_key`) y la guía enseñaría un comando falso; la lección IN-06 es sobre el import
- Tercer `except Exception` → AsistenteNoDisponible conservado en el wrapper: `model_validate_json` fallido no es GroqError y sin esa frontera cruzaría como 500 — jamás-500 (IN-06) completo
- Descripciones del router alineadas al wording exacto que 04-06 dejó en el contrato (l.1463/1471): "del servicio de IA" / "servicio caído"
- Fila 13 de guia-15 reescrita con la mecánica completa que exige el acceptance criterion (CERO coincidencias + control positivo con "Pregúntale a Maura", Select-String como variante PowerShell, findstr-from-Git-Bash corrosivo — Pitfall 8); el Origen conserva D-60 (historia, mismo criterio que ADR-017 en fila 8)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Puntero muerto "key de AI Studio" en la intro de la Gran verificación final (guia-15 l.513)**
- **Found during:** Task 2 (sustitución de la clave)
- **Issue:** La línea "para la fila 8 necesitas TU key de AI Studio (guía 14)" no estaba entre las 9 menciones mapeadas del plan (el grep del planner buscaba Gemini/google-genai literales) — pero AI Studio es la consola del flujo ROTO (D-60): dejada ahí, mandaría al alumno al camino muerto que el rework existe para cerrar
- **Fix:** "TU key de AI Studio (guía 14)" → "TU key de console.groq.com (guía 14)"
- **Files modified:** docs/05_desarrollo/guia-15-asistente-cierre.md
- **Verification:** el gate `! grep -qi gemini` pasa; cero punteros al flujo viejo en el archivo
- **Committed in:** 61aff27 (Task 2 commit)

**2. [Rule 1 - Bug] Segundo "17 ADRs" partido entre líneas en la sugerencia de commit (guia-15 l.549-550)**
- **Found during:** Task 2 (conteo 17→18)
- **Issue:** El plan mapeaba solo el "los 17 ADRs" de l.706 (grep de una línea); el mismo conteo vivía además en el commit sugerido de cierre partido como "los 17\nADRs del proyecto" — invisible para el gate pero incoherente con el conteo nuevo dentro del mismo archivo
- **Fix:** "respeta los 17" → "respeta los 18" (misma frase, conteo nuevo)
- **Files modified:** docs/05_desarrollo/guia-15-asistente-cierre.md
- **Verification:** `grep -c "los 17" guia-15` = 0; "18 ADRs" presente; el gate `! grep -q "17 ADRs"` sigue en verde
- **Committed in:** 61aff27 (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (1 missing critical, 1 bug)
**Impact on plan:** Ambos fixes cierran huecos del mapeo de líneas del plan, no scope creep: la guía queda sin NINGÚN puntero al flujo Gemini muerto y con un solo conteo de ADRs coherente.

## Issues Encountered
- Entorno (no defecto del producto): mismo fenómeno documentado en 04-06 — patrones grep que parten con `/` se corrompen vía MSYS en esta máquina; los gates de este plan no usan ese patrón y corrieron limpios. El diff de precisión del router se hizo con sed-extracción de bloques + diff (más confiable que leer el diff unificado completo).

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- La capa de guías del rework está completa: 04-08 queda con el barrido D-67 final (READMEs, docs/02-03 ya hechos en 04-06; one-liners de guias 12-13, mapa mental), la re-verificación runtime en el taller (SDK groq aún NO instalado en maura-uat — `uv add "groq>=1.7,<2"` + `uv remove google-genai` es el primer paso) y el cierre de la verificación de fase (22/25 → 25/25)
- Las menciones históricas sancionadas quedaron exactamente donde D-67 las permite: el blockquote de guia-14 y el cuerpo de ADR-017 (superseded)

## Self-Check: PASSED

Both modified files exist on disk; both task commits (95904f7, 61aff27) verified in git log; both task gates re-run post-commit and passing (g14-rework-ok / g15-rework-ok); commits measured from ledger: 2.

---
*Phase: 04-panel-de-administraci-n-y-asistente-ia*
*Completed: 2026-10-01*
