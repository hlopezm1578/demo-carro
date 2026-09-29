---
phase: 02-cuentas-de-cliente-y-carro-persistente
plan: 02
subsystem: docs
tags: [requerimientos, diseno, gherkin, dfd, er, cuentas, carro, jwt, trazabilidad, etapa-2]

# Dependency graph
requires:
  - phase: 01-fundaciones-de-dos-tiers-y-cat-logo
    provides: docs/02_requerimientos.md y docs/03_diseno.md de fase 1 con las series RF/RNF/RN/HU, DFDs 1.0-4.0 y pantallas 1-3 que esta etapa continúa sin renumerar
provides:
  - docs/02_requerimientos.md con la especificación de la etapa 2 (RF-06..RF-11, RNF-05..RNF-06, RN-05..RN-09, HU-05..HU-08, actores Clienta (con cuenta) y Admin (dueña), P5 mapeada en §13 y firma de etapa en §14)
  - docs/03_diseno.md con la entidad USUARIO (ER + diccionario), decisiones de diseño 7-10, almacenes D2/A2, procesos 5.0-8.0, pantallas 4-7 y la variante "Agregar al carro" de la ficha, todo trazado en §5 y anclado a ADR-009/010/011
affects: [02-03 y 02-04 (las guías 05-08 citan los RF/HU/RN y pantallas nuevos), 02-05 (READMEs de estado), fase 3 (checkout Webpay parte de esta especificación: RF-09/HU-08/D-31), fase 4 (panel admin hereda el actor Admin y RF-08)]

# Actuals (#2632) — mismo scale que el estimate (chars/4 sobre el diff realizado)
actuals:
  tokens: 12378     # 49513 chars / 4 sobre el diff 6bcbe4a..b298925 (docs/02 + docs/03)
  tasks: 2
  commits: 3        # medido: git rev-list --count 6bcbe4a..HEAD
plan_head_before: 6bcbe4ad1e94d93c20a627be514c107929500c65
plan_head_after: b2989250dc8080fe0e9e8bf8f2192068dcc244c9

# Tech tracking
tech-stack:
  added: []          # D-17 guide-only: nada se instala; la etapa 2 queda especificada como documentos
  patterns:
    - "Extensión por etapas de documentos vivientes: las series RF/RNF/RN/HU y las secciones del diseño continúan sin renumerar nada, y §14 acumula una firma por etapa"
    - "Traducción del UI-SPEC al lenguaje de diseño: wireframes ASCII + estados de carga/error/vacío SIN clases de implementación (eso es contenido de guías)"

key-files:
  created: []
  modified:
    - docs/02_requerimientos.md
    - docs/03_diseno.md

key-decisions:
  - "docs/02 extiende las series sin renumerar: etapa 2 = RF-06..RF-11 (AUTH-01..04 + CART-01/02, todas con origen P5), RNF-05/06, RN-05..RN-09 y HU-05..HU-08; actores Clienta (con cuenta) y Admin (dueña); P5 mapeada y CART-03/PAY-01..04 explícitos para etapa 3"
  - "RN-05 fija mínimo 8 SIN composición obligatoria citando NIST longitud-sobre-complejidad (D-25, prohibición del plan respetada) y RN-06 la asimetría 401 genérico/409 claro con su porqué (D-26)"
  - "docs/03: USUARIO con email único como clave del upsert (D-23/D-24) y hash que jamás cruza la frontera (RN-07); almacén A2 localStorage documentado como decisión de diseño, no de tecnología"
  - "Pantallas 4-7 con los copys locked del UI-SPEC (avisos login, 409, vaciado en dos pasos, 'Tu carro está vacío', CTA deshabilitado 'El pago llega en la etapa siguiente' D-31) y la ficha gana 'Agregar al carro' como variante (D-29)"
  - "Las decisiones de diseño §2.3 continúan la serie (7-10) y citan ADR-009/010/011: la cadena P5 → RF-06+ → HU-05+ → pantalla 4+ → ADR-009+ queda continua"

patterns-established:
  - "Patrón de extensión de etapa que las fases 3-5 replican en docs/02 y docs/03: continuar series, mover la fila P de 'fuera del alcance' a 'dentro' con mapeo real en §13, y sumar firma de etapa"
  - "Pantallas de diseño con estados traducidos del Copywriting Contract del UI-SPEC — el diseño cita los textos, la guía los implementa"

requirements-completed: [AUTH-01, AUTH-02, AUTH-03, AUTH-04, CART-01, CART-02]

# Coverage (#1602) — un entry por entregable
coverage:
  - id: D1
    description: "docs/02_requerimientos.md especifica la etapa 2 completa y trazable: RF-06..RF-11 con origen (AUTH-01..04, CART-01..02, P5), RNF-05/06, RN-05..RN-09 citando D-25/D-26/D-27/D-30, HU-05..HU-08 en Gherkin (17 líneas Dado: incluye email duplicado 409 y checkout sin sesión con retorno), actores Clienta/Admin, entradas §10, pantallas §12 (4-7), P5 mapeada en §13 con CART-03/PAY explícitos en etapa 3 y firma de etapa 2"
    requirement: AUTH-01
    verification:
      - kind: other
        ref: "command: plan Task 1 <automated> grep-chain (req02-ok) + 4/4 acceptance criteria (regex de formato RF con origen AUTH/CART+P5 = 6/6; 401/409 presentes; 17 Dado; P5/P6 mapeadas)"
        status: pass
    human_judgment: false
  - id: D2
    description: "docs/03_diseno.md diseña la etapa 2: entidad USUARIO en ER + diccionario de 5 columnas (email 255 único índice, hashed_password Argon2 RN-07, rol enum RF-08), decisiones 7-10 con su porqué, D2/A2 en almacenes, DFDs 5.0-8.0 con Reglas del proceso (total 8), pantallas 4-7 con wireframe/Origen/Estados (CTA pago deshabilitado D-31, vaciado en dos pasos, empty state), variante 'Agregar al carro' en la ficha (D-29), 13 filas nuevas en §5 y ancla a ADR-009/010/011"
    requirement: CART-01
    verification:
      - kind: other
        ref: "command: plan Task 2 <automated> grep-chain (dis03-ok, Reglas del proceso = 8) + 4/4 acceptance criteria + adr-link-ok + diff sin renumeración de fase 1"
        status: pass
    human_judgment: false

# Metrics
duration: 8 min
completed: 2026-09-29
status: complete
---

# Phase 2 Plan 2: Requerimientos y diseño de la etapa 2 Summary

**docs/02 y docs/03 extendidos con la etapa 2 completa y trazable: RF-06..11/HU-05..08/RN-05..09 desde P5 con actores Clienta y Admin, y el diseño USUARIO + procesos 5.0-8.0 + pantallas 4-7 ancladas a ADR-009/010/011 — sin renumerar nada de fase 1**

## Performance

- **Duration:** 8 min
- **Started:** 2026-09-29T16:58:01Z
- **Completed:** 2026-09-29T17:06:12Z
- **Tasks:** 2 (2 auto)
- **Files modified:** 2

## Accomplishments
- Los 6 requisitos de la fase (AUTH-01..04, CART-01/02) quedaron especificados como RF/HU trazables desde P5: la fila P5 de §13 pasó del placeholder al mapeo real (RF-06..RF-11 + HU-05..HU-08) y CART-03/PAY-01..04 quedaron explícitos como etapa 3
- Las reglas de seguridad de la etapa quedaron como RN verificables: mínimo 8 sin composición citando NIST (RN-05/D-25), asimetría 401 genérico/409 claro con su porqué (RN-06/D-26), hash confinado (RN-07), precio siempre vigente (RN-08/D-27), tope al stock en pantalla (RN-09/D-30) — T-02-05/T-02-06 mitigados en la capa de especificación
- El diseño agrega USUARIO (email único como clave del upsert D-23/D-24, hash Argon2 que jamás sale RN-07, rol desde el primer token RF-08), los almacenes D2/A2 (localStorage como decisión de diseño), los procesos 5.0-8.0 y las pantallas 4-7 con wireframe + Origen + Estados traducidos del UI-SPEC
- La cadena de trazabilidad P5 → RF-06+ → HU-05+ → pantalla/proceso → §5 → ADR-009/010/011 quedó continua y lista para que las guías 05-08 (planes 02-03/02-04) la citen

## Task Commits

Each task was committed atomically:

1. **Task 1: docs/02_requerimientos.md — requerimientos de la etapa 2 (RF-06..11, RN-05..09, HU-05..08)** - `952ffc2` (docs)
2. **Task 2: docs/03_diseno.md — entidad USUARIO, procesos 5.0-8.0 y pantallas 4-7** - `34e465b` (docs)

Complementario (key_link del plan): ancla de §2.3 a ADR-009/010/011 - `b298925` (docs)

**Plan metadata:** (ver commit docs final)

## Files Created/Modified
- `docs/02_requerimientos.md` - Etapa 2 completa: §1 alcance temporal a etapas 1-2, §2 P5 dentro del alcance, §3 actores Clienta/Admin, RF-06..11, RNF-05/06, RN-05..09, HU-05..08 (Gherkin), §8 USUARIO preliminar, §9 procesos 5-8, §10 formularios registro/login, §12 pantallas 4-7, §13 P5 mapeada + P6 con CART-03, §14 firma de etapa 2 (2026-09-29)
- `docs/03_diseno.md` - Diseño de la etapa 2: USUARIO en ER+diccionario, decisiones 7-10 + ancla ADR-009/010/011, contexto con clienta identificada y admin, almacenes D2/A2, DFDs 5.0-8.0, pantallas 4-7 (login/registro/carro/checkout) con estados del UI-SPEC, variante "Agregar al carro" en la ficha, 13 filas nuevas en §5

## Decisions Made
- La visita anónima puede armar el carro: el actor Visitante gana ese permiso en §3 (coherente con RF-11 "sin exigir cuenta" y A13), y HU-07 se escribió desde el visitante
- El admin entra como actor en la etapa 2 vía el rol de su cuenta (RF-08), con la nota explícita de que su herramienta (el panel) es etapa 4 — el blockquote de actores futuros quedó solo para P7-panel/P8
- Crear cuenta NO inicia sesión (HU-05 lleva al login con aviso esmeralda): espejo del UI-SPEC, la clienta confirma su contraseña entrando
- Los IDs D-25/D-26/D-27/D-30 se citan en cursiva como origen de las RN nuevas (key_link del plan con 02-CONTEXT), igual que las decisiones de fase 1 citan P/C/CS

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Completitud documental] Ajustes de coherencia interna más allá de los ítems literales de las tareas**
- **Found during:** Task 1 y Task 2
- **Issue:** El plan lista 10 ítems de acción para docs/02 y 8 para docs/03, pero dejar intactas las secciones narrativas que enmarcan esas secciones (alcance temporal de §1, modelo preliminar §8, procesos §9, permisos del visitante, tabla índice §1 de docs/03) habría dejado el documento viviente internamente inconsistente (p. ej. §1 diciendo "cubre la etapa 1" mientras §2 mete la etapa 2 al alcance)
- **Fix:** Ediciones mínimas de coherencia, todas aditivas salvo las que el propio plan manda (fila P5 de alcance, blockquote de actores, filas P5/P6 de §13): §1 de docs/02 (párrafo de contexto + blockquote a etapas 1-2), fila USUARIO + blockquote del email en §8, procesos 5-8 en §9, ítem 3 de §12 con la acción de agregar al carro, permiso "armar su carro sin cuenta" del visitante, tabla índice de docs/03 (7 pantallas, series nuevas en "Responde a")
- **Files modified:** docs/02_requerimientos.md, docs/03_diseno.md
- **Verification:** greps del plan + criterios de aceptación pasan; diff revisado línea a línea: ninguna serie RF/RNF/RN/HU ni sección numerada existente se renumeró ni borró
- **Committed in:** 952ffc2 y 34e465b (parte de los commits de tarea)

**2. [Rule 2 - Key link faltante] Ancla de las decisiones §2.3 a ADR-009/010/011**
- **Found during:** Cierre del plan (revisión de key_links)
- **Issue:** El key_link del plan exige que las decisiones de diseño numeradas de §2.3 citen ADR-009/010/011 (cadena P5 → RF-06+ → HU-05+ → pantalla 4+ → ADR-009+), pero los 8 ítems de acción del Task 2 no lo pedían y las decisiones escritas citaban solo D-xx
- **Fix:** Nota de bloque al final de §2.3 que mapea decisiones 7-10 a su capa técnica (sesión → ADR-009, carro client-side → ADR-010, cuentas con rol sembradas por env → ADR-011) sin romper la neutralidad tecnológica del diseño
- **Files modified:** docs/03_diseno.md
- **Verification:** `grep ADR-009/010/011` → adr-link-ok; re-run de los greps del plan → dis03-ok
- **Committed in:** b298925

---

**Total deviations:** 2 auto-fixed (2 missing critical / completitud)
**Impact on plan:** Ambas desviaciones cierran huecos de coherencia que el plan describe en must_haves/key_links pero no lista como ítems de acción. Cero scope creep: no se agregaron requerimientos, pantallas ni reglas fuera de lo planificado (sin RF-12, prohibición de composición de contraseña respetada).

## Issues Encountered
- Ninguna bloqueante. Nota de entorno heredada de 02-01: los greps se corrieron con `export MSYS_NO_PATHCONV=1` (artefacto MSYS/ugrep de este host); los patrones de este plan no comienzan con `/` y pasaron limpio (req02-ok / dis03-ok a la primera).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- La especificación de la etapa 2 está cerrada y trazada: los planes 02-03/02-04 (guías 05-08) pueden citar RF-06..11/HU-05..08/RN-05..09, las pantallas 4-7 y los procesos 5.0-8.0 sin ambigüedad, y el contrato 0.2.0 + ADRs 009-011 del plan 02-01 ya cubren la capa técnica
- La Gran verificación final de guia-08 tiene ahora su insumo: cada CS/RF/HU nuevo tiene fila en §13 (docs/02) y en §5 (docs/03)
- Sin bloqueos para este plan; los bloqueos de fase (spike Webpay, límites Gemini) siguen siendo de fase 3/4 y no afectan docs 02/03

## Self-Check: PASSED

- Archivos en disco: docs/02_requerimientos.md, docs/03_diseno.md, 02-02-SUMMARY.md — FOUND
- Commits: 952ffc2 (Task 1), 34e465b (Task 2), b298925 (ancla ADR) — FOUND
- Verify del plan re-ejecutado: req02-ok + dis03-ok; commits medidos desde ledger = 3
