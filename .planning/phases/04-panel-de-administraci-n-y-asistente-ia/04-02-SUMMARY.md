---
phase: 04-panel-de-administraci-n-y-asistente-ia
plan: "02"
subsystem: docs
tags: [requerimientos, diseno, rf, rnf, rn, hu, panel-admin, asesora-ia, gemini, mini-rag, maquina-de-estados, soft-delete, stock-bajo, dfd, trazabilidad]

requires:
  - phase: 04-panel-de-administraci-n-y-asistente-ia (plan 01)
    provides: "contrato_api.yaml 0.4.0 (paths admin + asistente que los RF nuevos nombran: allow-list sin activo D-52, 409 de transición, topes 500/10/3, 503/429 sin cifras) y ADRs 015-017 que las decisiones de diseño 15-18 citan"
  - phase: 04-panel-de-administraci-n-y-asistente-ia (research + ui-spec)
    provides: "04-CONTEXT.md (D-50..D-62 con el punto delicado de RN-04 y el actor Admin) y 04-UI-SPEC.md (defaults auto a confirmar como RN: ≤ 5 stock, 500 chars, 10 mensajes, 3 cards; copys locked; Pitfall 6 de los dos umbrales)"
provides:
  - "docs/02 etapa 4 completa: RF-19..RF-24 con origen ADMN/AIAS y decisión D, RNF-08/09 como filas de la tabla de §5, RN-14 (umbral ≤ 5 activos distinto del 1-3 de tienda), RN-15 (máquina con dueño por transición citando a RN-04), RN-16 (topes 500/10/3), HU-12/HU-13 con Dado/Cuando/Entonces, bloque 'Dentro del alcance de la etapa 4', actor Admin sin postergar, procesos 12-15, entradas nuevas, pantallas 10-14, filas P7/P8 reales en §13, bloque de aprobación 'Etapa 4 —' y nota de cero entidades nuevas en §8 (D-58)"
  - "docs/03 etapa 4 completa: pantallas 10-14 en el formato vigente con los copys locked del UI-SPEC, decisiones de diseño 15-18 citando ADR-015..017 (la 15 cita §2.3.5 para el soft delete), DFDs 12.0-15.0 con bloque 'Reglas del proceso' (13.0 UPDATE condicional espejo del 10.0; 15.0 topes ANTES de Gemini e ids DESPUÉS contra D1 activo), nodo GEM como segunda entidad externa con el contraste request-response vs redirecciones, y nota del historial del chat en memoria del componente"
  - "Cadena de trazabilidad continua P7/P8 → RF-19+ → HU-12+ → pantallas 10-14 → ADR-015+ (§13 filas reales + Origen de cada pantalla + §5 con una fila por ítem nuevo)"
affects: [04-panel-de-administraci-n-y-asistente-ia (planes 04-03, 04-04, 04-05), docs/05_desarrollo/guia-12..15, Gran verificación final de fase 4, UAT delegado de fase 4]

actuals:
  tokens: 14210     # chars/4 sobre el diff real commiteado (56840 chars en 2 archivos)
  tasks: 2
  commits: 2        # medido: git rev-list --count 6e74dfb2..HEAD

tech-stack:
  added: []         # plan documental (repo guide-only, D-17): cero paquetes
  patterns:
    - "La RN nueva supersede citando sin reescribir: RN-15 cita a RN-04 byte-intacta ('la regla se cumple en vez de romperse') — la mecánica de supersedencia para series que la historia cita"
    - "Dos umbrales con nombre como regla numerada (RN-14 + decisión 16): el mismo dato (stock) con dos significados por audiencia queda veteado por RN, no por convención — Pitfall 6 hecho serie"
    - "DFD espejo: el 13.0 (anular) reutiliza la forma del UPDATE condicional del 10.0 (descuento atómico) — la condición de estado vive dentro de la sentencia, rowcount 0 → 409"

key-files:
  created: []
  modified:
    - docs/02_requerimientos.md
    - docs/03_diseno.md

key-decisions:
  - "La supersede de RN-04 vive dentro de RN-15 (dueño por transición → dueño de la escritura del catálogo): ningún RN nuevo extra porque el plan fija exactamente RN-14..16 y RN-04 queda byte-intacta y citada"
  - "La decisión 15 de docs/03 cita §2.3.5 para el soft delete (ocultar sin borrar) en vez de duplicarla — la decisión nueva de escritura de catálogo reutiliza el diseño existente (paralelo con la cita de RN-10 en el DFD 12.0)"
  - "El copy locked 'Pregúntale a Maura' aparece como string literal en la viñeta de la pantalla 14 (no solo en el wireframe, donde el ancho lo corta): los copys del Copywriting Contract quedan grep-verificables"
  - "Pantalla 13 (No autorizado) con Origen RF-08 + D-55: el espejo UX del 403 se traza al 403 por rol de la etapa 2, no a un RF nuevo — la seguridad es la misma, lo nuevo es la cortesía"
  - "El estado 'editor abierto' de la pantalla 10 se declara como estado más de la pantalla (no ruta): el editor inline no suma numeración de pantallas ni de rutas"

patterns-established:
  - "Extensión de etapa documentada con la mecánica 2-3 exacta: narrativa §1 al pasado + bloque de alcance nuevo + series solo agregadas + tabla resumen §1 de docs/03 actualizada a la nueva cuenta (14 pantallas, HU-01…HU-13)"
  - "Pregunta para la clase por etapa (etapa 4: por qué la validación de ids vive en el backend y no en el chat) — la serie didáctica continúa con las de etapas 2-3"

requirements-completed: [ADMN-01, ADMN-02, ADMN-03, ADMN-04, AIAS-01, AIAS-02, AIAS-03]  # copiado verbatim del PLAN; el flip en REQUIREMENTS.md queda diferido por el shared-ID gate (04-03..05 declaran los mismos IDs)

coverage:
  - id: D1
    description: "docs/02_requerimientos.md documenta la etapa 4 completa: 6 RF + 2 RNF + 3 RN + 2 HU nuevos con origen, el bloque 'Dentro del alcance de la etapa 4' (P7/P8 adentro), el actor Admin sin postergar y el blockquote invertido, los procesos 12-15, las entradas nuevas, las pantallas 10-14 en §12, las filas P7/P8 con mapeo real en §13, el bloque de aprobación 'Etapa 4 —' y la nota de cero entidades nuevas en §8 — series de etapas 1-3 intactas (RN-04 byte-intacta y citada)"
    requirement: ADMN-01
    verification:
      - kind: other
        ref: "grep chain del Task 1 (req04-ok): 13 ids nuevos presentes, conteos ≥24 RF / ≥16 RN (bullets) / ≥13 HU (headings ###), RNF-08/09 como filas ^| RNF-, bloque de alcance etapa 4, placeholder '(llegan con la etapa 4' ausente, citas RN-04/PENDING/CANCELLED/500/≤5/soft delete, ítems ^12.–^15. de §9, 'Etapa 4 —' con em-dash, bloques **Dado** en HU-12/HU-13 (awk acotado por sección) — pass"
      - kind: other
        ref: "git diff del Task 1: 84 insertions / 20 deletions — las líneas eliminadas son solo el bloque P7/P8 de §2, las filas placeholder de §13, la fila del actor Admin y los párrafos de narrativa/blockquote que la mecánica de etapa reescribe (igual que 02-02→03-03); cero items de series RF/RNF/RN/HU eliminados — pass"
        status: pass
    human_judgment: false
  - id: D2
    description: "docs/03_diseno.md agrega las pantallas 10-14 con estados carga/error/vacío y copys locked del UI-SPEC, las decisiones de diseño 15-18 citando D-50/D-53/D-56/D-61 y ADR-015..017 (la 15 cita §2.3.5), los DFDs 12.0-15.0 con sus bloques 'Reglas del proceso' (13.0 UPDATE condicional con 409 sin tocar stock; 15.0 topes antes de Gemini e ids después contra D1 activo), el nodo GEM como segunda entidad externa con el contraste request-response vs redirecciones de Webpay, la nota del historial en memoria del componente y una fila por ítem nuevo en §5 — ER y diccionario intactos (cero entidades, D-58)"
    requirement: AIAS-01
    verification:
      - kind: other
        ref: "grep chain del Task 2 (dis04-ok): Pantalla 10-14, 'Pregúntale a Maura', 'No tienes acceso al panel', 'Top 5 aromas vendidos', 'Stock bajo', 'Gemini', GEM/asesora IA, 'Reglas del proceso' ≥14 (15 medidos), 12.0/15.0, cita 2.3.5, mini-RAG, degradación, Origen RF-19/HU-13, acción Anular — pass"
      - kind: other
        ref: "git diff del Task 2: 424 insertions / 8 deletions — las eliminadas son las 3 celdas de la tabla resumen §1, la frase 'suma a Webpay' (→ 'sumó' + cláusula Gemini) y las 3 líneas del mermaid (label SISTEMA y arcos del admin); cero decisiones/pantallas/DFD/filas existentes reescritos — pass"
        status: pass
    human_judgment: false

duration: 9 min
completed: 2026-09-30
status: complete
plan_head_before: 6e74dfb2a367ec4288fef38c81427ec8d93ca03a
plan_head_after: 26725b20f7b5c2b2d06f723be87570e298ce508c
---

# Phase 4 Plan 02: Especificación de la etapa 4 (docs 02/03) Summary

**docs/02 suma RF-19..24 + RNF-08/09 + RN-14..16 + HU-12/13 con las filas P7/P8 reales, y docs/03 agrega las pantallas 10-14 con copys locked, las decisiones 15-18 citando ADR-015..017, los DFDs 12.0-15.0 y a Gemini como segunda entidad externa — sin tocar una sola serie existente**

## Performance

- **Duration:** 9 min
- **Started:** 2026-09-30T21:27:51Z
- **Completed:** 2026-09-30T21:36:56Z
- **Tasks:** 2/2
- **Files modified:** 2 (docs/02_requerimientos.md, docs/03_diseno.md)

## Accomplishments

- docs/02 etapa 4 completa con la mecánica de las etapas 2-3 (solo agregar): 6 RF con origen ADMN/AIAS + decisión D, 2 RNF como filas de la tabla de §5, 3 RN (umbral ≤ 5 distinto del 1-3 de tienda Pitfall 6, máquina con dueño por transición citando RN-04 byte-intacta, topes 500/10/3) y 2 HU con Dado/Cuando/Entonces — más filas P7/P8 reales, procesos 12-15, bloque de aprobación y cero entidades nuevas (D-58)
- docs/03 etapa 4 completa: pantallas 10-14 con estados carga/error/vacío y los copys locked del UI-SPEC (Pregúntale a Maura, No tienes acceso al panel, Top 5 aromas vendidos, Stock bajo, Ese pedido ya no está en curso), decisiones 15-18, DFDs 12.0-15.0 y el nodo GEM con el contraste request-response vs redirecciones
- La cadena de trazabilidad quedó continua: P7/P8 → RF-19+ → HU-12+ → pantallas 10-14 → ADR-015+ (verificada por greps de conteo ≥24/≥16/≥13 y el awk acotado de las HU nuevas)

## Task Commits

Each task was committed atomically:

1. **Task 1: docs/02_requerimientos.md — etapa 4** - `467be8d` (docs)
2. **Task 2: docs/03_diseno.md — pantallas 10-14, decisiones 15-18, DFDs 12.0-15.0, GEM** - `26725b2` (docs)

## Files Created/Modified

- `docs/02_requerimientos.md` - Etapa 4: RF-19..RF-24 (CRUD soft delete D-51/D-52, stock bajo D-53, transición única D-50, métricas sin gráficos D-54, chat público D-57..59, mini-RAG D-56), RNF-08/09 (Gemini free tier, key solo backend D-60/D-61), RN-14..RN-16, HU-12/HU-13, §1-§3 actualizados, §8 cero entidades, §9 12-15, §10/§12 nuevos, §13 P7/P8 reales, §14 aprobación
- `docs/03_diseno.md` - Pantallas 10-14 (§4.11-§4.15), decisiones 15-18 + pregunta para la clase etapa 4 + párrafo ADR-015..017, §3.1 GEM en el mermaid con arcos admin actualizados, §3.2 nota del historial en memoria, DFDs 12.0-15.0 (§3.14-§3.17), §5 con 13 filas nuevas, tabla resumen §1 a 14 pantallas/HU-01…HU-13

## Decisions Made

- La supersede de RN-04 se tejió como cierre de RN-15 (la RN del dueño por transición extiende su lógica a la escritura del catálogo): el plan fija exactamente RN-14..16 y prohibía un 4º bullet — la regla histórica queda citada y byte-intacta
- La "decisión de escritura de catálogo" que el plan pedía citar §2.3.5 vive en la decisión 15 (dueño por transición → dueño de la escritura), en paralelo con la RN-15 de docs/02 que cita RN-04 — mismo concepto, misma casa
- Pantalla 13 traza su Origen a RF-08 + D-55 (el 403 por rol de la etapa 2) en vez de inventar un RF nuevo: el espejo UX es cortesía nueva sobre seguridad existente
- El vacío de productos del panel ("Crea el primero con el botón «Nuevo producto»") quedó contrastado explícitamente con el vacío de tienda: el admin PUEDE crear — la asimetría es el contenido pedagógico
- Los estados de la burbuja se declararon como estados de pantalla completos (cerrada / bienvenida / en vuelo / 503 / 429 / red) para cumplir la regla §4.1 de estados obligatorios en una pantalla sin ruta propia

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Copy locked "Pregúntale a Maura" ausente como string literal**
- **Found during:** Task 2 (verify del plan — la cadena falló en ese eslabón)
- **Issue:** El copy solo existía cortado entre dos líneas del wireframe ("( Pregúntale" / "a Maura )"), por el ancho del ASCII art — el gate `grep -q "Pregúntale a Maura"` fallaba
- **Fix:** La primera viñeta de la pantalla 14 ahora nombra la etiqueta literal ("con su etiqueta **\"Pregúntale a Maura\"**") — los copys locked quedan grep-verificables fuera del arte ASCII
- **Files modified:** docs/03_diseno.md
- **Verification:** Cadena completa del Task 2 re-ejecutada → dis04-ok
- **Committed in:** 26725b2 (parte del commit del Task 2)

**2. [Rule 1 - Correctness] Tablas resumen §1 de docs/03 desactualizadas por la extensión**
- **Found during:** Task 2 (revisión de dif pre-commit)
- **Issue:** La tabla §1 de docs/03 decía "9 pantallas" y "HU-01…HU-11"; con 5 pantallas nuevas el resumen habría quedado falso (el plan no lo lista explícitamente, pero la etapa 3 hizo el mismo mantenimiento al pasar de 7 a 9)
- **Fix:** Celdas actualizadas: 14 pantallas, HU-01…HU-13, RF-06…RF-24, RN-05..RN-15 con "(etapa 4: sin entidades nuevas)" en la fila de §2
- **Files modified:** docs/03_diseno.md
- **Verification:** Lectura de la tabla coherente con el contenido; diff muestra solo esas 3 celdas cambiadas
- **Committed in:** 26725b2 (parte del commit del Task 2)

---

**Total deviations:** 2 auto-fixed (2 Rule 1: copy locked + tabla resumen)
**Impact on plan:** Ambos fixes son de corrección dentro del task que introdujo el contenido; cero alcance extra. Series existentes intactas en ambos documentos (verificado por diff).

## Issues Encountered

- **Wireframes cortan strings:** un copy locked partido entre líneas de ASCII art es invisible para el grep — la lección para 04-03/04-04 es que todo copy del Copywriting Contract debe existir también como texto plano fuera del wireframe. (La nota MSYS de 04-01 se aplicó de forma preventiva: `/usr/bin/grep` + `MSYS_NO_PATHCONV=1`, patrón por patrón idéntico — sin incidentes esta vez.)

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Series y pantallas de la etapa 4 listas para que 04-03 (guia-12/13: panel) y 04-04 (guia-14/15: asistente) citen por id: la cadena P7/P8 → RF-19+ → HU-12+ → pantallas 10-14 → ADR-015+ es grep-verificable de punta a punta
- Los defaults del UI-SPEC quedaron confirmados como RN numeradas (RN-14 ≤ 5, RN-16 500/10/3) — las guías enseñan constantes con respaldo de requerimiento, no números mágicos
- Blocker heredado vigente (no de este plan): límites RPM/RPD del free tier de Gemini requieren verificación logueada del usuario; RN-16/RNF-08 ya se abstienen de cifras por diseño

## Self-Check: PASSED

- Files: docs/02_requerimientos.md, docs/03_diseno.md — FOUND (2/2)
- Commits: 467be8d, 26725b2 — FOUND (2/2, verificados con git log)
- Verificaciones re-ejecutadas post-commit: req04-ok / dis04-ok — ambas PASS

---
*Phase: 04-panel-de-administraci-n-y-asistente-ia*
*Completed: 2026-09-30*
