---
phase: 05-despliegue-y-cierre-de-la-gu-a
plan: 04
subsystem: docs
tags: [deploy, webpay, 4-flujos, gran-verificacion-final, ciclo-efimero, cierre-de-serie, d-73, guia]

requires:
  - phase: 05-despliegue-y-cierre-de-la-gu-a
    provides: ADR-019/020 + doc 07 (05-01), docs 06/08 enlazables (05-02) y guías 16/17 con el eslabón Siguiente vivo y sus mini-verificaciones definidas (05-03)
provides:
  - docs/05_desarrollo/guia-18-despliegue-cierre.md: la guía de CIERRE de la fase 5 y de la SERIE — los 4 flujos de Webpay contra el ambiente desplegado con resultado esperado por estado, el ciclo efímero observado deliberadamente y la Gran verificación final de la serie DEFINIDA para el alumno (D-73)
  - La última tabla | # | Verificación | Origen | de la serie (9 filas): refresh/deep-link, los 4 flujos, las dos filas fijas heredadas (contrato 0.4.0 ↔ /docs público con Authorize, grep del build en producción), el ciclo efímero y la paridad cero drift
  - El cierre narrativo de la serie: el Siguiente de guia-18 no inventa una guia-19 — entrega el testigo al ciclo documental (06_pruebas/07_despliegue/08_mantenimiento) con el molde "El ciclo se cierra (y se reabre)" y las 18 guías + 20 ADRs como arco completo
  - El índice de guías llega a 18 archivos (las filas de los READMEs las agrega el plan 05-05)
affects: [05-05 (la quinta corrida de tablas cuenta guías 1-18 y la fila 5 a Lista; GUIDE-01/DEPL-02 cierran en REQUIREMENTS)]

actuals:
  tokens: 7287           # chars/4 sobre el diff realizado (29.147 chars, 479 líneas — un solo archivo nuevo)
  tasks: 2
  commits: 2             # MEDIDO: git rev-list --count a7a0816..HEAD
  plan_head_before: a7a081646b60d58edd8f195a80900a855a0c634e
  plan_head_after: a521e4a031ee71bfed9ab7e25dad528166d7e12b

tech-stack:
  added: []              # fase documental (D-17/D-73): cero paquetes, cero runtime
  patterns: [Nota D-73 "esta tabla la corres TÚ" como introducción de la tabla de cierre (nueva en la serie — tono de la nota honesta de guia-15:538-542), Siguiente de cierre de SERIE hacia los docs del ciclo (sin guía siguiente)]

key-files:
  created:
    - docs/05_desarrollo/guia-18-despliegue-cierre.md
  modified: []

key-decisions:
  - "El 'anulado con Rechazar en el simulador' del plan se resolvió fiel a la evidencia canónica del spike/ADR-012: el Paso 3 cubre los DOS caminos del simulador — 'Anular compra y volver' → cancelled (params TBK_*, sin commit) y Rechazar/TSN en el 3DS → rejected (commit response_code -1, criterio PAY-03) — declarando resultado esperado por estado en cada uno"
  - "El flujo error de formulario se enseña con la clave 3DS errada → error.cgi del banco SIN commit (transacción INITIALIZED) y el regreso posterior con params de timeout (22-78 s observado por el spike) — el 4º flujo de token doble queda nombrado como 'replicable solo en producción' cubierto por el discriminador por presencia (inmunidad ADR-012 sin corrida)"
  - "El wording del timeout hereda el cierre firmado por 03-UAT: pestaña activa CANCELA la orden (~10 min, 603 s cronometrados por la fase 3); la orden queda 'en curso' SOLO si la pestaña durmió y el retorno no llegó (RN-11) — la nota de los dos relojes (token 5 min / form ~10 min vs spin-down ~15 min / wake ~1 min) cita transbankdevelopers.cl y render.com/docs/free 'a la fecha'"
  - "La fila degradada del carro tras el ciclo se narra con física correcta: el carro (localStorage) sobrevive TODO; un aroma CREADO en runtime desaparece con el disco y su fila degrada ('Este aroma ya no está disponible' + Quitar) — mismo mecanismo de fase 2, otro origen del dato (no se inventó lib/badges.ts ni un mecanismo nuevo)"

patterns-established:
  - "Filas fijas heredadas con la URL pública y la versión quieta: la fila contrato ↔ /docs y la fila grep del build replican el wording de guia-15:529-530 cambiando localhost por https://<tu-servicio>.onrender.com — 0.4.0 quieto por D-66 (gate negativo 0.5.0 en verde)"

requirements-completed: [DEPL-02, GUIDE-01]

coverage:
  - id: D1
    description: "Cuerpo de guia-18 (479 líneas totales del archivo): cabecera de cierre (Necesitas: guías 1 a 17 — dos tiers desplegados), 5 términos, la cadena congelada en una mirada citando guia-09 verbatim (return_url/302/estado REAL), un paso por flujo con QUÉ HACER y QUÉ ESPERAR por estado (paid/cancelled/rejected/en curso honesto), nota de los dos relojes con cifras citadas, ciclo efímero deliberado (seed revive/runtime se pierde + fila degradada), 3 pares ❌/✅, tabla de errores típicos (wake/VITE_API_URL/rewrite), verificación numerada, punto de control y aprendizajes"
    requirement: DEPL-02
    verification:
      - kind: other
        ref: "grep gate del plan (g18-cuerpo-ok, GNU grep): título Guía 18, los 4 flujos nombrados, ADR-012 + estado REAL, cadena return_url/302/rewrite, ciclo efímero con seed (D-70/ADR-020), tarjeta + MAURA-, El desarrollador piensa (6), >= 4 Mini-verificación (7), Punto de control, Lo que acabas de aprender; gate de conteo: 18 archivos guia-*.md"
        status: pass
      - kind: other
        ref: "chequeo de AC: timeout con wording del cierre de fase 3 (pestaña activa CANCELA; dormida → en curso RN-11); cifras de relojes con URL + 'a la fecha'; cero re-enseñanza de guia-16/17 (citadas como prerrequisito en verde); cero UI nueva (solo prosa + copys locked heredados citados); placeholders <tu-servicio>/<tu-proyecto> verificados (cero subdominios reales)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Gran verificación final de la SERIE definida para el alumno (D-73): tabla de 9 filas con Origen cada una (refresh DEPL-02, 4 flujos PAY-03/04/02, contrato 0.4.0 ↔ /docs público con Authorize clienta 200/admin-endpoint 403 — fila fija heredada guia-15:529 con versión quieta D-66, grep del build en producción con comando por shell — fila fija guia-15:530/AIAS-03, ciclo efímero D-70/ADR-020, paridad cero drift), nota D-73 en la introducción ('esta tabla la corres TÚ'), sugerencia de commit de cierre de serie, bullets del ciclo vivido y Siguiente a 06_pruebas/07_despliegue/08_mantenimiento sin inventar guia-19"
    requirement: GUIDE-01
    verification:
      - kind: other
        ref: "grep gate del plan (g18-cierre-ok, GNU grep): Gran verificación final, 'la corres TÚ', 0.4.0 presente y 0.5.0 AUSENTE, /docs + Authorize + contrato_api.yaml, GROQ_API_KEY/AIAS-03, DEPL-02/PAY-0x, 06_pruebas/07_despliegue/08_mantenimiento, ciclo se cierra/ciclo completo + 20 ADRs, Sugerencia de commit; NEGATIVOS en verde (cero 'verificamos', cero 'aprobamos la gran verificación')"
        status: pass
      - kind: other
        ref: "chequeo de AC: las dos filas fijas replican el wording de guia-15:529-530 (UNO A UNO; comando por shell) con la URL pública; nota D-73 en la introducción de la tabla (no enterrada); 9/9 filas con Origen; links relativos resueltos 10/10 (docs 06/07/08, README, ADRs 012/013/019/020, guías 16/17)"
        status: pass
    human_judgment: false

duration: 8 min
completed: 2026-10-01
status: complete
---

# Phase 5 Plan 4: guia-18 — los 4 flujos en producción y la Gran verificación final de la serie Summary

**guia-18 cierra la serie: los 4 flujos de Webpay contra el ambiente desplegado con resultado esperado por estado (paid/cancelled/rejected/en curso honesto), el ciclo efímero observado deliberadamente y la Gran verificación final de 9 filas DEFINIDA para el alumno (D-73: "la corres TÚ") con las dos filas fijas heredadas en 0.4.0 — y el Siguiente entrega el testigo a los docs 06/07/08 sin inventar una guia-19**

## Performance

- **Duration:** 8 min
- **Started:** 2026-10-01T18:33:48Z
- **Completed:** 2026-10-01T18:42:09Z
- **Tasks:** 2/2
- **Files modified:** 1 (1 creado)

## Accomplishments

- guia-18-despliegue-cierre.md (479 líneas) con la estructura canónica completa de guia-15: cabecera de cierre ("nada de código nuevo — la verificación de lo que construiste durante 17 guías, ahora contra TU tienda pública"; Necesitas: guías 1 a 17 con sus mini-verificaciones en verde), 5 términos (ambiente desplegado, flujo de retorno, cadena congelada, ciclo efímero, idempotencia) y el Paso 1 que recorre la cadena congelada en una sola mirada citando los bloques de guia-09 byte-exactos (return_url con BACKEND_URL, _hacia_spa con cors_origins[0] y el 302 explícito) — tres env vars, cero líneas nuevas
- Pasos 2-5, un flujo por paso con QUÉ HACER y QUÉ ESPERAR por estado del pedido observable en la URL pública: aprobado (VISA 4051 8856 0044 6623 → response_code 0/AUTHORIZED en el servidor, voucher MAURA-00000X badge Pagado, carro en 0, stock descontado); anulado y rechazado (los DOS caminos del simulador: "Anular compra y volver" → cancelled sin commit; Rechazar/TSN → rejected por commit -1 — carro restituido porque nunca se borró, PAY-04); timeout (pestaña activa ~10 min → cancelled con "Se agotó el tiempo"; dormida → huérfana "en curso" honesta, el cierre que firmó 03-UAT); error de formulario (clave 3DS errada → error.cgi sin cargo ni commit + regreso posterior con params de timeout; el token doble queda como "solo producción" cubierto por el discriminador)
- La nota de los dos relojes en el 🧠 del timeout: token 5 min / form ~10 min (603 s cronometrados por la fase 3) contra el spin-down ~15 min / wake ~1 min — el create resetea la ventana, el retorno lento pero funcional es el wake (Pitfall 6, cifras de transbankdevelopers.cl y render.com/docs/free "a la fecha")
- Paso 6: el ciclo efímero como verificación deliberada — crear pedido → redeploy o spin-down → despertar → catálogo restaurado por el seed / pedido de runtime ausente (las dos capas de D-70/ADR-020 en el propio dato), stock restaurado al canónico, y la fila degradada del carro ("Este aroma ya no está disponible" + Quitar) como el mecanismo de fase 2 sobreviviendo con otro origen del dato
- La Gran verificación final de la SERIE (Task 2): tabla de 9 filas con Origen cada una, la nota D-73 en la introducción ("esta tabla la corres TÚ, en tus cuentas free — el proyecto que la escribió la define y no la ejecuta"), las dos filas fijas heredadas de guia-15:529-530 con la URL pública y la versión QUIETA en 0.4.0 (D-66), la sugerencia de commit de cierre de serie, los bullets del ciclo vivido y el Siguiente que cierra la serie hacia 06_pruebas/07_despliegue/08_mantenimiento con el molde "El ciclo se cierra (y se reabre)" y las 18 guías + 20 ADRs como arco — sin guia-19

## Task Commits

Each task was committed atomically:

1. **Task 1: guia-18 — cuerpo: la cadena congelada, los 4 flujos contra el ambiente desplegado y el ciclo efímero** - `c1cdc22` (docs)
2. **Task 2: guia-18 — la Gran verificación final de la SERIE (D-73) + commit de cierre y Siguiente al ciclo documental** - `a521e4a` (docs)

**Plan metadata:** (commit final de este plan, ver abajo)

## Files Created/Modified

- `docs/05_desarrollo/guia-18-despliegue-cierre.md` - Guía 18: la guía de cierre de la fase 5 y de la serie — los 4 flujos en producción, el ciclo efímero observado y la Gran verificación final definida para el alumno (D-73)

## Decisions Made

- El "anulado con Rechazar en el simulador" del plan se implementó fiel a la evidencia canónica (spike fase 3 / ADR-012): el Paso 3 corre los DOS caminos del simulador con resultado esperado por estado distinto (cancelled vs rejected) — nombrar "Rechazar" como productor de cancelled habría sido un error factual contra lo que 03-UAT firmó
- El flujo de error de formulario usa la clave 3DS errada (el único disparador real en integración): error.cgi SIN commit + regreso posterior con params de timeout (22-78 s observados por el spike); el token doble se nombra como "replicable solo en producción" — la inmunidad por presencia de params lo cubre sin corrida
- La fila degradada tras el ciclo se narró con física correcta: el carro sobrevive en localStorage; lo que degrada la fila es un aroma CREADO en runtime que el disco se llevó (el seed no lo conoce) — mismo mecanismo de fase 2, otro origen del dato; NO se inventó `lib/badges.ts` (los badges viven en los componentes de las guías 10/11 como la serie construyó)
- Las URLs siempre con placeholder `<tu-servicio>`/`<tu-proyecto>` (verificado por grep: cero subdominios reales, cero localhost enseñado como valor) — higiene heredada de 05-03

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Dos micro-correcciones de autoría atrapadas antes del commit (sin impacto): un voseo ("vos no lo ves" → "tú no lo ves" — la serie es tuteo chileno) y una errata ("declama" → "declara"). Ambas corregidas dentro del ciclo de redacción de cada task; los gates g18-cuerpo-ok y g18-cierre-ok pasaron con el texto final (GNU grep por el tema ugrep documentado en 05-02-SUMMARY).

## User Setup Required

None - no external service configuration required. (D-73: los 4 flujos y la Gran verificación final los corre el ALUMNO en sus cuentas free — este plan solo escribe la guía que los define.)

## Next Phase Readiness

- guia-18 existe y el directorio 05_desarrollo llega a exactamente 18 guías (gate de conteo en verde) — el plan 05-05 cierra las tablas de estado de los tres READMEs (fila 5 a Lista con guías 1-18, filas 6-8 a Listo) y el mapa mental de 05_desarrollo/README.md
- La cadena Siguiente queda CERRADA por diseño: 15 → 16 → 17 → 18 → docs 06/07/08 (guia-18 no deja eslabón de guía pendiente — no hay guia-19)
- El Siguiente de guia-18 enlaza los tres docs del ciclo por nombre de archivo exacto y el índice de docs/README.md queda referido con "las 8 filas en verde" — 05-05 lo hace realidad (quinta corrida D-13/D-18)
- DEPL-02 y GUIDE-01 son los requirements de este plan: al existir este SUMMARY, todos sus planes declarantes (05-02/03/04 para GUIDE-01; 05-03/04 para DEPL-02) tienen SUMMARY — el shared-ID gate debería liberarlos en el paso requirements.mark-complete de este plan; 05-05 no declara requirements compartidos pendientes
- El contrato_api.yaml sigue INTACTO en 0.4.0 (D-66 verificado por el gate negativo del plan: 0.5.0 ausente)

## Self-Check: PASSED

Archivo creado existe en disco (docs/05_desarrollo/guia-18-despliegue-cierre.md, 479 líneas / 29.147 chars); commits c1cdc22 y a521e4a presentes en el log; commits medidos contra el ledger (a7a0816..HEAD = 2); gates del plan re-ejecutados en verde (g18-cuerpo-ok, g18-cierre-ok con GNU grep); conteo 18 guías verificado; sin deletions ni untracked en el árbol.

---
*Phase: 05-despliegue-y-cierre-de-la-gu-a*
*Completed: 2026-10-01*
