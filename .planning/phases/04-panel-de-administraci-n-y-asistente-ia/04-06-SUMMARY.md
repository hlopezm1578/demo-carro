---
phase: 04-panel-de-administraci-n-y-asistente-ia
plan: 06
subsystem: docs
tags: [groq, adr, openapi, structured-outputs, agnostic-contract, rework]

requires:
  - phase: 04-panel-de-administraci-n-y-asistente-ia (planes 04-01..05 ejecutados)
    provides: corpus spec vigente (contrato 0.4.0, ADRs 001-017, docs 02/03) que este plan reescribe
provides:
  - ADR-018 (swap Gemini→Groq firmado con evidencia: doc oficial + probe SDK 1.7.0 + 402/billing de 04-UAT test 2) que supersede ADR-017
  - contrato_api.yaml 0.4.0 agnóstico del proveedor (8 descripciones reescritas, superficie intacta)
  - RNF-08/RNF-09 agnósticas (docs/02) y entidad externa Groq + DFD 15.0 + trazabilidad (docs/03)
  - README de arquitectura con fila groq 1.7.0 (pin >=1.7,<2) e índice de 18 ADRs
affects: [04-07 (guias 14-15 citan ADR-018 y el contrato agnóstico), 04-08 (barrido/re-verificación se mide contra esta capa)]

actuals:
  tokens: 8200        # chars/4 sobre el diff realizado (32.839 chars en 7 archivos)
  tasks: 3
  commits: 3          # medido: git rev-list --count 3ff6118..HEAD
  plan_head_before: 3ff611826c0e798be2aacdf5c3f46ba97142294f
  plan_head_after: d4f67d90e49eef399bece477f2cc497c032c7be2

tech-stack:
  added: ["groq 1.7.0 (pin >=1.7,<2) — firmado en documentación (ADR-018/README arq); el repo sigue guide-only, sin código"]
  patterns:
    - "ADR supersede con cuerpo byte-intacto: la marca vive SOLO en la línea de Estado (Pitfall 7)"
    - "Wording-only contract sweep: descripciones agnósticas sin tocar versión/paths/schemas/copys locked (D-66)"

key-files:
  created:
    - docs/04_arquitectura/adr/018-asistente-ia-groq-structured-outputs.md
  modified:
    - docs/04_arquitectura/adr/017-asistente-ia-mini-rag-key-solo-backend.md
    - docs/04_arquitectura/contrato_api.yaml
    - docs/02_requerimientos.md
    - docs/03_diseno.md
    - docs/04_arquitectura/adr/002-dos-tiers-spa-y-api.md
    - docs/04_arquitectura/README.md

key-decisions:
  - "ADR-018 firma D-63..D-68 con evidencia firmada (triple cadena: doc oficial + registry + probe punta a punta SDK 1.7.0 del 2026-10-01 + 402/billing de 04-UAT test 2); cifras EXACTAS 30 RPM / 1.000 RPD / 8K TPM / 200K TPD con 'a la fecha' y fuente — la cifra RPD de la nota original jamás se firma (gate negativo)"
  - "ADR-017 Superseded por ADR-018 (2026-10-01) con cuerpo byte-intacto (diff de 1 línea, verificado pre y post commit) — registro histórico sancionado"
  - "Contrato 0.4.0 agnóstico (D-66): 'el servicio de IA'/'la API key del asistente', el paréntesis 'no son públicos sin login' muere, versión NO sube, cero churn para guia-12 y la fila contrato ↔ /docs"

patterns-established:
  - "Supersede de ADR con marca mínima: solo la línea Estado cambia, el cuerpo queda como registro histórico (extensible a futuros ADRs)"
  - "Sweep agnóstico de spec: la serie numerada se reescribe fila por fila in-place, sin renumerar (RF/RNF/RN/HU/P/DFD/pantallas/decisiones intactos)"

requirements-completed: [AIAS-02, AIAS-03]

coverage:
  - id: D1
    description: "ADR-018 firma el swap Gemini→Groq (D-63..D-68) con evidencia y ADR-017 queda Superseded con cuerpo byte-intacto"
    requirement: AIAS-02
    verification:
      - kind: other
        ref: "gate <verify> Task 1 (adrs-rework-ok): 18 ADRs, pin >=1.7,<2, openai/gpt-oss-120b, json_schema strict, ConfigDict, RateLimitError/GroqError/503, 30 RPM/1.000 RPD, rate-limits, D-63/D-68, models.list, secciones, sin gsk_/14.400; ADR-017 con response_json_schema/v2.25.0/GEMINI_API_KEY intactos"
        status: pass
      - kind: other
        ref: "diff de precisión: git diff HEAD --stat adr/017 = 1 inserción/1 eliminación (línea Estado) — pre-commit y git show --stat eb5a8fa post-commit"
        status: pass
    human_judgment: false
  - id: D2
    description: "contrato_api.yaml 0.4.0 agnóstico del proveedor — 8 descripciones reescritas, versión y superficie intactas, YAML válido"
    requirement: AIAS-02
    verification:
      - kind: other
        ref: "gate <verify> Task 2 (contrato-rework-ok): version 0.4.0 sin 0.4.1, cero gemini, servicio de IA, API key del asistente, paréntesis muerto, copys locked (asesora 429/503, 409, 403), paths asistente/admin, MAURA-000001, yaml.safe_load OK"
        status: pass
    human_judgment: false
  - id: D3
    description: "Barrido spec: docs/02 RNF-08/09 agnósticas, docs/03 entidad Groq/DFD 15.0/trazabilidad, ADR-002 (2 líneas) y README arq (fila groq + índice 18)"
    requirement: AIAS-03
    verification:
      - kind: other
        ref: "gate <verify> Task 3 (specdocs-rework-ok): cero gemini en los 4 archivos, RNF-08/09 filas de tabla, 'documentados públicamente', D-63, series ≥24 RF/≥13 HU/≥14 Reglas del proceso, Pantalla 14/15.0/Top 5, fila groq con pin, link ADR-018, superseded, guide-only"
        status: pass
    human_judgment: false

duration: 10min
completed: 2026-10-01
status: complete
---

# Phase 4 Plan 6: Rework spec layer Groq Summary

**ADR-018 firma el swap Gemini→Groq (SDK groq >=1.7,<2, json_schema strict, cifras 30 RPM/1.000 RPD con fuente) supersediendo ADR-017 con cuerpo intacto, el contrato 0.4.0 queda agnóstico y docs/02+03/ADR-002/README arq dejan de nombrar al proveedor muerto**

## Performance

- **Duration:** 10 min
- **Started:** 2026-10-01T14:30:02Z
- **Completed:** 2026-10-01T14:40:16Z
- **Tasks:** 3/3 (1 tracer + 2 auto)
- **Files modified:** 7 (1 creado, 6 modificados)

## Accomplishments
- ADR-018 nuevo (formato demo-cine completo): 9 reglas numeradas que firman D-63..D-68 — pin `>=1.7,<2`, `MODELO_ASISTENTE = "openai/gpt-oss-120b"`, `json_schema` strict + `ConfigDict(extra="forbid")`, `GROQ_API_KEY` vía pydantic-settings con `api_key` explícita (IN-03), wrapper 429/503 jamás 500, sin retry casero (el SDK reintenta 2x incluido el 429), cifras 30 RPM / 1.000 RPD / 8K TPM / 200K TPD con fuente y "a la fecha", muralla D-56 preservada, models.list como diagnóstico — con Evidencia firmada (3 URLs oficiales + probe punta a punta SDK 1.7.0 win32 del 2026-10-01 + 402/billing de 04-UAT test 2, links relativos patrón ADR-012)
- ADR-017 Superseded por ADR-018 con cuerpo byte-intacto (diff de exactamente 1 línea, verificado pre y post commit)
- Contrato 0.4.0 agnóstico: las 8 descripciones reescritas ("el servicio de IA" / "la API key del asistente"), el paréntesis "no son públicos sin login" muere, versión queda 0.4.0, paths/schemas/example detail locked intactos, YAML parsea
- Barrido spec: RNF-08 agnóstica sin cifras con cláusula de límites públicos + RNF-09 con API key del asistente (D-60→D-63 en Origen); decisión 18, párrafo de contexto, nodo `GEM["Groq (asesora IA)"]` (diagrama + DFD 15.0), l.1335 y trazabilidad §5 en docs/03; las 2 líneas de ADR-002; contexto + fila IA groq + regla 3 + fila 017 anotada + fila 018 nueva en README arq (índice a 18)

## Task Commits

Each task was committed atomically:

1. **Task 1 (tracer): ADR-018 + marca superseded en ADR-017** - `eb5a8fa` (docs)
2. **Task 2: contrato 0.4.0 agnóstico (8 descripciones)** - `e1ddef1` (docs)
3. **Task 3: barrido spec docs/02+03, ADR-002, README arq** - `d4f67d9` (docs)

**Plan metadata:** commit final de cierre (docs: complete plan)

Tracer feedback gate (modo auto activo): verify re-ejecutado post-commit → PASS → expansión continuada.

## Files Created/Modified
- `docs/04_arquitectura/adr/018-asistente-ia-groq-structured-outputs.md` - ADR del rework: proveedor/SDK/pin/modelo/strict/cifras firmados con evidencia; supersede ADR-017
- `docs/04_arquitectura/adr/017-asistente-ia-mini-rag-key-solo-backend.md` - SOLO la línea Estado: Superseded por ADR-018 (2026-10-01); cuerpo byte-intacto
- `docs/04_arquitectura/contrato_api.yaml` - 8 descripciones agnósticas; versión y superficie intactas (D-66)
- `docs/02_requerimientos.md` - RNF-08/RNF-09 reescritas in-place; series intactas
- `docs/03_diseno.md` - decisión 18, contexto, nodo GEM→Groq, DFD 15.0, l.1335, trazabilidad §5
- `docs/04_arquitectura/adr/002-dos-tiers-spa-y-api.md` - l.13/l.46 describiendo el sistema vigente
- `docs/04_arquitectura/README.md` - contexto, fila IA groq 1.7.0 (pin, ADR-018 supersede 017), regla 3, índice con 18 filas

## Decisions Made
- La fila IA del README arq cita la relación 018-supersede-017 dentro de la propia fila (el acceptance criterion lo exige aunque el texto del action no la incluía)
- En la trazabilidad §5 de docs/03, "§3.1 Gemini como entidad externa" pasó a "§3.1 Groq como entidad externa" (el gate `! grep -qi gemini` sobre docs/03 lo requiere; nombra la entidad concreta como el análogo Webpay del mismo diagrama)
- Las reglas del DFD 15.0 (l.628-636) NO necesitaron edición: ya decían "con el servicio caído" y la cita a RNF-08 sigue cubierta por la RNF reescrita

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Referencia viva al SDK muerto en README arq l.159**
- **Found during:** Task 3 (barrido spec)
- **Issue:** El árbol de código del README arq decía "el ÚNICO lugar que importa google.genai" (forma con punto). Ningún gate la atrapa — el gate de este plan busca `gemini|google-genai` (guion) y el gate del barrido de 04-08 usa el mismo patrón — pero describe el sistema VIGENTE: tras el rework, `services/asistente.py` importa `groq`. Dejarla dejaría una mención viva del proveedor muerto que el barrido final jamás detectaría (gap de planing: ni 04-06 ni 04-08 la mapean).
- **Fix:** "importa google.genai" → "importa groq" (molde de la línea vecina: "el ÚNICO lugar que importa transbank" de services/webpay.py)
- **Files modified:** docs/04_arquitectura/README.md
- **Verification:** `! grep -q "google.genai" README-arq` agregado al gate del task (pasa); el diff de precisión muestra el toque adicional documentado
- **Committed in:** d4f67d9 (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 missing critical)
**Impact on plan:** Fix de una palabra alineado con el objetivo D-67 (barrido completo, "el alumno nunca lee" al proveedor muerto en un documento vigente). Cero scope creep.

## Issues Encountered
- Entorno (no defecto del producto): el grep del Git Bash de esta máquina es ugrep + MSYS convierte patrones que parten con `/` a rutas Windows, así que `grep -q "/api/asistente"` falla espuriamente. Resuelto ejecutando los gates con patrón `[/]api/asistente` (equivalente semántico exacto; lo verificado no cambia). El YAML se validó con python -c "import yaml; yaml.safe_load(...)" como pedía el plan.
- Los requirements AIAS-02/AIAS-03 NO se marcaron completos en REQUIREMENTS.md: el shared-ID gate los bloquea porque los sibling 04-07/04-08 también los declaran y no tienen SUMMARY — se re-evaluarán cuando el último plan declarante cierre (comportamiento correcto del gate #2388).

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Fuente de verdad del rework lista para 04-07: guia-14 reescrita apunta a ADR-018 y el contrato agnóstico ya no la ata a proveedor
- Pendiente del barrido D-67 (asignado a 04-07/04-08): guias 12-15, READMEs de docs/raíz/05_desarrollo, documentos vivos de .planning
- Cifras de límites quedaron firmadas una sola vez (ADR-018); guia-14 las citará con fuente y "a la fecha"

## Self-Check: PASSED

All 8 created/modified files exist on disk; all 3 task commits (eb5a8fa, e1ddef1, d4f67d9) verified in git log; the 3 task gates re-run post-commit and passing (adrs-rework-ok / contrato-rework-ok / specdocs-rework-ok).

---
*Phase: 04-panel-de-administraci-n-y-asistente-ia*
*Completed: 2026-10-01*
