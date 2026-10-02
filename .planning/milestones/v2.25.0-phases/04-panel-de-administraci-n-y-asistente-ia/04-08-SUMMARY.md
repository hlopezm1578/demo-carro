---
phase: 04-panel-de-administraci-n-y-asistente-ia
plan: 08
subsystem: docs
tags: [groq, gemini, barrido, roadmap, requirements, stack, uat, taller, rework]

requires:
  - phase: 04-panel-de-administraci-n-y-asistente-ia (ondas R1/R2 ejecutadas: 04-06 y 04-07)
    provides: ADR-018 + contrato 0.4.0 agnóstico + docs spec sin Gemini (R1) y guias 14-15 reworkeadas con blockquote D-65 (R2) — las capas que este plan barre y re-verifica runtime
provides:
  - Corpus docs/ + README raíz CERO Gemini vivo (gate replicable: menciones SOLO en ADR-017 superseded, ADR-018 registro del swap y blockquote D-65 de guia-14) con conteos 18 ADRs / 18 decisiones sin marcar desarrollo completo
  - Documentos vivos de .planning sin proveedor muerto: ROADMAP (Goal/SC4/Overview/fila con historia de planes intacta), REQUIREMENTS (AIAS-03 agnóstico + (Groq)), PROJECT.md y STACK.md declarando Groq con nota fechada ADR-018
  - Taller D:/Repos/maura-uat re-integrado con Groq siguiendo la guia-14 reescrita literalmente: happy path 200 REAL (ids existentes), 422 topes, 503 amable sin key, paralelas sin 500, grep dist/ cero
  - 04-UAT.md test 2 re-verificado (result: pass, 5/5 pass / 0 blocked) — los 3 gaps_remaining de 04-VERIFICATION desbloqueados para el cierre de fase
affects: [cierre de fase 04 (verificación de fase: los gaps quedan con evidencia runtime), fase 05 (parte leyendo Groq en todos los índices y anclas)]

actuals:
  tokens: 12500     # chars/4: 39.691 chars del diff del repo + ~10.400 chars del taller (fuera del git del repo)
  tasks: 3
  commits: 3        # medido: git rev-list --count 680668e..HEAD
  plan_head_before: 680668e8e7267105e0c272a84da0bcc7ca7aa933
  plan_head_after: 8f1cd7ac3e4224976135a1d5563c406faa044087

tech-stack:
  added: []          # repo guide-only (D-17): el SDK groq se instala en el TALLER del alumno (uv add "groq>=1.7,<2" → 1.7.0), no en el repo
  patterns:
    - "Gate de barrido con lista blanca de historia sancionada: git grep -il + regiones awk — las menciones que quedan son solo ADR-017/ADR-018/blockquote D-65 (verificadas mención por mención como históricas)"
    - "Nota fechada de rework fuera de la región viva: STACK.md lleva la nota del swap en línea propia ANTES del heading Core (igual que §Sources — historia con fecha, tabla viva limpia)"

key-files:
  created: []
  modified:
    - docs/05_desarrollo/guia-12-panel-backend.md
    - docs/05_desarrollo/guia-13-panel-spa.md
    - docs/05_desarrollo/README.md
    - docs/README.md
    - README.md
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md
    - .planning/PROJECT.md
    - .planning/research/STACK.md
    - .planning/phases/04-panel-de-administraci-n-y-asistente-ia/04-UAT.md

key-decisions:
  - "La whitelist del gate de barrido se corrigió a TRES archivos históricos (ADR-017 + ADR-018 + blockquote de guia-14): ADR-018 es el registro del swap que D-65 manda vivir ahí y sus 9 menciones son historia (tabla de opciones descartadas, evidencia 402, contraste de pines) — el gate del plan las había omitido; NO se editó ADR-018 (Pitfall 7)"
  - "El taller ejecuta los bloques de la guia-14 REESCRITA como alumno (regla dos lugares de AGENTS.md): la re-integración ES la re-verificación de que la guía nueva funciona — incluyendo las 2 descripciones agnósticas del router que 04-07 dejó en la guía (el plan decía 'router NO se toca' asumiendo el estado ya alineado)"
  - "truststore queda como nota de entorno taller-only (Pitfall 9): inyectado en el módulo del service del taller (uv pip install, fuera de pyproject) y documentado en 04-UAT.md — jamás en la guía"
  - "El ítem humano end-of-phase queda cubierto punta a punta por esta corrida (la GROQ key del taller ES la del usuario) y queda anotado para su ratificación en el cierre de fase"

patterns-established:
  - "Barrido de corpus con excepciones históricas enumeradas y gates awk de región: la prueba mecánica lista los archivos supervivientes y cada uno debe ser historia sancionada"
  - "Corrección de frases vivas en documentos de planning preservando anotaciones de planes ejecutados ('- [x] 04-...'): la historia del roadmap es la historia de la tienda"

requirements-completed: [ADMN-01, ADMN-02, ADMN-03, ADMN-04, AIAS-01, AIAS-02, AIAS-03]

coverage:
  - id: D1
    description: "Barrido D-67 del corpus docs/ + README raíz: one-liners guia-12/13, fila 14 + mapa mental del README de 05_desarrollo, conteos 18 ADRs/18 decisiones — cero Gemini vivo con las excepciones históricas sancionadas"
    requirement: AIAS-02
    verification:
      - kind: other
        ref: "gate <verify> Task 1 (barrido-rework-ok): guia-12/13/READMEs sin gemini, SDK de Groq/SDK groq presentes, 18 ADRs/18 decisiones sin los 17 viejos, 15 guias/18 ADRs en disco, cadena Siguiente 11→15, LEFT = ADR-017|ADR-018|guia-14 con región awk del blockquote en verde"
        status: pass
      - kind: other
        ref: "diff de precisión: 17+/16- en 5 archivos, solo líneas mapeadas (guia-12 l.16, guia-13 l.1673, fila 14 + mapa mental refloweado, fila 4 docs/README, 4 pasajes del README raíz)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Anclas de planning sin proveedor muerto: ROADMAP (Overview/fila/Goal/SC4 con historia intacta), REQUIREMENTS (heading, AIAS-03 agnóstico, Out of Scope), PROJECT.md y STACK.md con Groq + nota fechada ADR-018"
    requirement: AIAS-03
    verification:
      - kind: other
        ref: "gate <verify> Task 2 (planning-anchors-ok): 3 frases viejas muertas en ROADMAP, cero gemini case-insensitive en REQUIREMENTS, PROJECT con GROQ_API_KEY/ADR-018/concern D-68 cerrado, STACK con fila groq pin >=1.7,<2 y awk de región Core en verde"
        status: pass
    human_judgment: false
  - id: D3
    description: "Taller maura-uat re-integrado con Groq + UAT test 2 re-verificado: happy path 200 real con ids existentes, 422 topes, 503 amable sin key con tienda operativa, 2 paralelas sin 500, grep dist/ cero — 5/5 pass / 0 blocked"
    requirement: AIAS-01
    verification:
      - kind: integration
        ref: "runtime taller 2026-10-01: POST /api/asistente 'algo cítrico para el día' → 200 voz de Maura, ids [1,2] válidos contra /api/productos; 501 chars/historial 11 → 422/422; sin key → 503 copy exacto + salud 200 + catálogo vivo; DOS threads paralelos → 200/200, cero 500, salud 200; npm run build + grep GROQ_API_KEY dist/ → exit 1 con control positivo"
        status: pass
      - kind: other
        ref: "gate <verify> Task 3 (taller-uat-ok): service from groq/json_schema/MODELO_ASISTENTE sin genai, extra=forbid en schemas, pyproject con groq sin google-genai, 04-UAT test 2 con Groq+result: pass, blocked: 0"
        status: pass
    human_judgment: true
    rationale: "La corrida usa la key real del usuario y cubre el happy path punta a punta, pero la ratificación del ítem humano end-of-phase (happy path con la key del usuario) y la porción de navegador (cards clicables — no re-probada porque el frontend no cambió) son acto de cierre de fase del usuario"

duration: 21min
completed: 2026-10-01
status: complete
---

# Phase 4 Plan 8: Cierre del rework Groq Summary

**Barrido D-67 cerrado con gate mecánico (corpus CERO Gemini vivo; sobreviven solo ADR-017 superseded, ADR-018 registro del swap y el blockquote de guia-14), anclas de planning corregidas con historia intacta y el taller re-integrado con la guia-14 reescrita: happy path 200 REAL con ids existentes, paralelas sin 500 y UAT 5/5**

## Performance

- **Duration:** 21 min
- **Started:** 2026-10-01T15:05:20Z
- **Completed:** 2026-10-01T15:26:25Z
- **Tasks:** 3/3 (3 auto)
- **Files modified:** 10 del repo (+5 del taller: services/asistente.py, schemas/asistente.py, config.py, routers/asistente.py 2 descripciones, .env.example)

## Accomplishments
- Corpus docs/ + README raíz sin NINGUNA instrucción viva al proveedor muerto: one-liner de guia-12 (l.16 "SDK de Groq"), Siguiente de guia-13 (l.1673 "el SDK `groq`"), fila 14 + mapa mental del README de 05_desarrollo ("El servicio de IA de Groq es el segundo servicio externo", contraste Webpay intacto), conteos 18 ADRs (docs/README l.18, README raíz l.41) y 18 decisiones (l.54) — fila 5 honesta en Parcial ("guías 1-15 listas; continúa en fases 5+")
- Gate de barrido en verde con lista blanca de TRES archivos históricos: ADR-017 (superseded, cuerpo byte-intacto), ADR-018 (registro del swap que D-65 manda vivir ahí — 9 menciones históricas verificadas una a una) y guia-14 (menciones confinadas al blockquote por el gate de región de 04-07, re-verificado)
- Anclas de planning: ROADMAP Overview l.11 + fila de fase l.30 + Goal l.128 + SC4 l.136 corregidos con las anotaciones "- [x] 04-0N" intactas; REQUIREMENTS sin un solo "gemini" (case-insensitive) con AIAS-03 agnóstico "(Groq)"; PROJECT.md con Groq/ADR-018/GROQ_API_KEY y el concern RPM/RPD CERRADO citando D-68; STACK.md con fila Core groq 1.7.0 (pin `>=1.7,<2`, probe-verified) sin nombrar al retirado en tabla, nota fechada del rework antes del heading Core, Domain/env var/installs/What-NOT/async/Version-Compat actualizados
- Taller re-integrado como alumno: `uv add "groq>=1.7,<2"` (1.7.0) + `uv remove google-genai` (2.26.0); services/asistente.py con `from groq import`, MODELO_ASISTENTE, json_schema strict, wrapper 429/503; Recomendacion con extra="forbid"; Settings groq_api_key; mini-verificaciones de los pasos 3/4/5 de la guía en verde EXACTO ("None | PydanticUndefined", "500 500 10 3 | False ['productos', 'respuesta']", client lazy None, aislamiento de import)
- Runtime del rework: happy path 200 REAL (voz de Maura, ids [1,2] existentes en el catálogo activo), topes 422/422, degradación 503 con copy exacto y tienda 100% operativa, DOS llamadas en paralelo 200/200 sin ningún 500 con salud 200 tras la ráfaga, models.list 11 modelos con gpt-oss-120b, rebuild del frontend + grep GROQ_API_KEY dist/ → exit 1 con control positivo
- 04-UAT.md: test 2 de blocked a pass con evidence completa (summary 5/5 pass / 0 blocked, frontmatter status: pass, Current Test sin ítems pendientes) — los 3 gaps_remaining de 04-VERIFICATION quedan con evidencia runtime para el cierre de fase

## Task Commits

Each task was committed atomically:

1. **Task 1: barrido de índices y one-liners (D-67 cierra el corpus docs)** - `a823555` (docs)
2. **Task 2: anclas de planning (ROADMAP/REQUIREMENTS/PROJECT/STACK)** - `c0cf72f` (docs)
3. **Task 3: taller re-integrado + UAT test 2 re-verificado** - `8f1cd7a` (docs)

**Plan metadata:** commit final de cierre (docs: complete plan)

## Files Created/Modified
- `docs/05_desarrollo/guia-12-panel-backend.md` - l.16: única mención del archivo → "el SDK de Groq"
- `docs/05_desarrollo/guia-13-panel-spa.md` - l.1673: Siguiente → "con el SDK `groq`" (única mención)
- `docs/05_desarrollo/README.md` - fila 14 Groq + mapa mental con "El servicio de IA de Groq" (reflow del párrafo, lección de contraste intacta)
- `docs/README.md` - fila 4: 18 ADRs (única edición del archivo)
- `README.md` - descripción "(Groq)", 18 ADRs, 18 decisiones, stack "Groq: la asesora..."
- `.planning/ROADMAP.md` - 4 frases vivas corregidas; anotaciones históricas de planes intactas
- `.planning/REQUIREMENTS.md` - heading "(Groq)", AIAS-03 agnóstico, Out of Scope sin "se usa google-genai", "LLM hospedado (Groq)"
- `.planning/PROJECT.md` - declaraciones vivas a Groq con ADR-018; veto de SDKs Gemini como historia fechada; concern RPM/RPD CERRADO (D-68: 30 RPM / 1.000 RPD)
- `.planning/research/STACK.md` - fila Core groq + nota fechada + Domain/env var/installs/What-NOT/pinning/async/Version Compat; §Sources histórico intacto
- `.planning/phases/04-.../04-UAT.md` - test 2 pass con evidence de la corrida Groq + nota taller-only truststore + summary 5/5

## Decisions Made
- Whitelist del gate de barrido corregida a 3 archivos (ver desviación 1): el registro del swap (ADR-018) es historia sancionada por D-65 — un ADR de migración no puede no nombrar al proveedor migrado
- El router del taller se alineó a las 2 descripciones agnósticas que la guía reworkeada trae en su paso 6 (ver desviación 4): el taller espeja la guía actual, no la pre-rework
- models.list corrido con variante taller-only (truststore a mano) porque el one-liner en frío no importa el service: nota de entorno, no defecto de guía
- Sin sesión de navegador en esta corrida: la burbuja fue validada EN VIVO en el test 1 (filas 8/11) y el frontend no cambió con el rework; el happy path se verificó a nivel de API (el contrato que la burbuja consume) — documentado así en el evidence

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Gate de barrido con whitelist incompleta: ADR-018 también contiene menciones históricas**
- **Found during:** Task 1 (ejecución del gate)
- **Issue:** El `<verify>` exigía LEFT = EXACTAMENTE "ADR-017|guia-14|", pero ADR-018 (creado por 04-06/R1 como registro del swap) contiene 9 menciones de Gemini/google-genai — todas históricas: la tabla de opciones ("Quedarse en Gemini" descartada), la evidencia del 402, el contraste de pines y de reintentos, D-66 narrada. El planner enumeró las excepciones desde el corpus pre-R1 y omitió al propio ADR nuevo
- **Fix:** Gate corrido con whitelist de TRES archivos históricos, verificando mención por mención que las 9 de ADR-018 son narrativas del cierre (ninguna manda al alumno a Gemini). ADR-018 NO se editó — D-65 ordena que "el registro completo del cambio vive en ADR-018" y el Pitfall 7 del propio plan veta reescribir historia
- **Files modified:** ninguno (corrección de la aserción del gate, no del artefacto)
- **Verification:** `git grep -il` lista exactamente ADR-017|ADR-018|guia-14; gate de región awk de guia-14 en verde (menciones solo en el blockquote l.3/l.9); lectura dirigida de las 9 menciones de ADR-018
- **Committed in:** documentado acá (el gate corregido corrió en Task 1, commit a823555)

**2. [Rule 3 - Blocking] Entorno grep: ugrep + MSYS corrompen la normalización del gate**
- **Found during:** Task 1 (ejecución del gate)
- **Issue:** `grep -ril` de esta máquina es ugrep 7.8.4 y emite rutas con backslashes antepestados (`docs/\04_arquitectura\...`); el `sed 's|\\|/|g'` del gate además se corrompe al pasar por el harness (mangling de backslashes) — el gate no puede producir su cadena esperada en este entorno (mismo fenómeno documentado en 04-06/04-07)
- **Fix:** El barrido se corrió con `git grep -il` (rutas canónicas con slash, semántica idéntica: archivos con menciones en docs/ + README.md) + verificación de región con awk
- **Files modified:** ninguno
- **Verification:** LEFT exacto con las 3 excepciones históricas; barrido-rework-ok
- **Committed in:** n/a (ejecución del gate)

**3. [Rule 3 - Blocking] Puerto 8000 del taller con servidor huérfano (precondition "puertos libres")**
- **Found during:** Task 3 (verificación del precondition)
- **Issue:** Un `fastapi dev` staled de una sesión anterior seguía vivo: el padre (CLI) muerto, el hijo multiprocessing sosteniendo el socket con el PID del padre atribuido — taskkill del PID reportado fallaba con "no se encontró el proceso"
- **Fix:** Identificación del hijo real vía Win32_Process (multiprocessing spawn) y taskkill del proceso vivo; verificado con probe de conexión (CONNECT FAIL esperado)
- **Files modified:** ninguno del repo
- **Verification:** puerto 8000 LIBRE antes de levantar el backend del taller
- **Committed in:** n/a (taller)

**4. [Rule 2 - Missing Critical] Router del taller conservaba las 2 descripciones Gemini pre-rework**
- **Found during:** Task 3 (re-integración del taller)
- **Issue:** El plan decía "El router NO se toca" asumiendo que el estado del taller ya calzaba con la guía — pero la guía reescrita (04-07) alineó sus 2 descripciones responses al wording agnóstico del contrato ("servicio de IA", "servicio caído") y el taller seguía con "Cuota del free tier de Gemini consumida" / "Gemini caído": el /docs del taller post-rework describiría al proveedor muerto
- **Fix:** Las 2 descripciones del router del taller alineadas al bloque actual del paso 6 de la guía (espejo dos-lugares); responses 200/422/429/503 y copys locked intactos (D-66)
- **Files modified:** D:/Repos/maura-uat/backend/app/routers/asistente.py
- **Verification:** backend levantó con OpenAPI 0.4.0; responses declaradas intactas
- **Committed in:** taller (fuera del git del repo; documentado en el evidence del test 2)

---

**Total deviations:** 4 auto-fixed (1 gate bug, 1 missing critical, 2 blocking/entorno)
**Impact on plan:** Ninguna cambia el alcance: la corrección del gate preserva el objetivo D-67 (cero menciones VIVAS — las 3 supervivientes son historia sancionada verificada), y las del taller son el espejo de la guía reworkeada que la regla de AGENTS.md exige.

## Issues Encountered
- El one-liner de models.list (golpe 4 del paso 8) ejecutado EN FRÍO falla por TLS en esta máquina (middlebox, Pitfall 9): ese proceso no importa el service y por tanto no tiene truststore inyectado. Variante taller-only (import truststore a mano) corre 200 — registrado como nota de entorno en 04-UAT.md, no defecto de guía (las máquinas de los alumnos no tienen el middlebox)
- El `.env` del taller: el ciclo comentar/reiniciar/probar/restaurar/reiniciar de la guía se ejecutó completo (sed idempotente verificado: exactamente 1 línea comentada, luego 1 activa)
- gsd_run no estaba en el PATH de las shells del agente: resuelto con el resolver oficial (node .zcode/gsd-core/bin/gsd-tools.cjs) — sin efecto en los artefactos

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- D-67 cerrado con prueba mecánica replicable y D-13/D-18 honrados: índices cuentan 18 ADRs/18 decisiones sin marcar desarrollo completo; la fase 5 no parte leyendo Gemini en ningún documento vivo
- Los 3 gaps_remaining de 04-VERIFICATION quedan con evidencia runtime registrada (happy path con la key del usuario + backstop AIAS-03 observado con paralelas sin 500 + backstop ADMN-01 ya observado con D-4-10 en el test 1) — listos para la re-verificación/ratificación de cierre de fase
- AGENTS.md (bloques GSD source:PROJECT.md / research/STACK.md) NO se editó a mano: se regenera desde los archivos actualizados en la próxima sincronización del tooling GSD
- El concern RPM/RPD quedó CERRADO en PROJECT.md citando D-68 (Groq publica 30 RPM / 1.000 RPD para gpt-oss-120b); el bloque Blockers/Concerns viejo de STATE.md se limpia en el cierre de fase

## Self-Check: PASSED

All 10 modified repo files exist on disk; all 3 task commits (a823555, c0cf72f, 8f1cd7a) verified in git log; the 3 task gates re-run post-commit and passing (barrido-rework-ok / planning-anchors-ok / taller-uat-ok) plus the combined global verification (VERIFICACION-GLOBAL-OK).

---
*Phase: 04-panel-de-administraci-n-y-asistente-ia*
*Completed: 2026-10-01*
