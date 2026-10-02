---
phase: 03-checkout-webpay-y-rdenes
plan: 02
subsystem: payments
tags: [openapi, contrato-api, webpay, retorno-302, adr, api-first, snapshot-precio]

requires:
  - phase: 03-checkout-webpay-y-rdenes (plan 01)
    provides: "03-SPIKE-RETORNO.md — evidencia runtime de los 4 flujos del retorno (tabla de veredictos por flujo) y la mecánica firmada D-41 que el contrato y el ADR-012 declaran"
provides:
  - "contrato_api.yaml 0.3.0: POST /api/checkout (Bearer, sin campo de precio — CART-03 en el contrato), GET+POST /api/pago/retorno público con 302 en ambos métodos, GET /api/pedidos y /api/pedidos/{numero} con 404 uniforme de ownership; schemas CheckoutCreate/CheckoutRespuesta/OrdenLista/OrdenDetalle y enum estado [pending, paid, cancelled, rejected]"
  - "ADRs 012-014 (índice a 14): retorno de Webpay con la evidencia del spike citada, orden nace al pagar + stock atómico al aprobar, snapshot de precio + numero legible como buy_order"
  - "README de 04_arquitectura: pago como stack construido (transbank-sdk 6.1.0 citando ADR-012/013), árbol del alumno con los 10 archivos de la etapa, regla 5 con la excepción del retorno"
affects: [03-checkout-webpay-y-rdenes (planes 03-03, 03-04, 03-05), guia-09/10/11, Gran verificación final de fase 3 (fila contrato 0.3.0 ↔ /docs)]

actuals:
  tokens: 10700      # chars/4 sobre el diff real commiteado (42871 chars en 5 archivos)
  tasks: 3
  commits: 3         # medido: git rev-list --count 4b0b9c2..HEAD

tech-stack:
  added: []          # sin paquetes nuevos en el repo (guide-only, D-17); transbank-sdk 6.1.0 se documenta y las guías de 03-04 lo enseñarán a instalar
  patterns:
    - "El contrato como testigo de garantías estructurales: la entrada del checkout SIN campo de precio (la prohibición CART-03 vive en el schema), security: [] deliberado con el porqué narrado, el 302 como primer response no-JSON"
    - "ADR firmado con evidencia runtime: ADR-012 cita el documento del spike por flujo (D-40/D-41) en vez de supuestos de documentación"

key-files:
  created:
    - docs/04_arquitectura/adr/012-retorno-de-webpay.md
    - docs/04_arquitectura/adr/013-orden-nace-al-pagar-stock-al-aprobar.md
    - docs/04_arquitectura/adr/014-snapshot-de-precio-en-la-orden.md
  modified:
    - docs/04_arquitectura/contrato_api.yaml
    - docs/04_arquitectura/README.md

key-decisions:
  - "Contrato 0.3.0 aprobado ANTES de las guías (D-15/ADR-007 honrado): la superficie de la etapa 3 queda declarada con las garantías verificables — CheckoutCreate sin precio, retorno GET+POST con 302 en ambos métodos (Pitfall 13), 404 uniforme en pedidos"
  - "ADR-012 firma la mecánica del retorno citando la evidencia por flujo del spike (D-40/D-41): discriminador por PRESENCIA de params jamás por método HTTP (la corrección del anulado por GET lo justifica), 302 explícito contra la trampa del 307, security: [] deliberado"
  - "ADR-013 registra D-34/D-35: la orden nace PENDING al iniciar el pago, crear solo VALIDA stock, el descuento es atómico y transaccional al aprobar el commit (UPDATE condicional + rowcount; rowcount 0 → REJECTED); recoge la regla 3 de ADR-010 y deja la huérfana PENDING sin gestión hasta fase 4 en Negativas honestas (D-48/D-49)"
  - "ADR-014 fija D-36/D-37: snapshot de nombre/precio obligatorio en la orden con la asimetría RN-08 como lección central, soportado por el soft delete de docs/03 §2.3.5, y numero legible MAURA-{id:06d} como buy_order ≤26 chars distinto del id interno"

patterns-established:
  - "Fila 302 en la tabla de convención de errores del contrato: la respuesta no-JSON documentada con su header Location — las guías de 03-04 replicarán la declaración en responses={} de ambos métodos"
  - "El description del schema como lugar pedagógico del contrato: por qué NO hay campo de precio (CART-03), por qué el retorno es público (PAY-02)"

requirements-completed: [CART-03, PAY-01, PAY-02, PAY-03, ORDR-01]

coverage:
  - id: D1
    description: "Contrato 0.3.0 con la superficie completa de la etapa 3: 4 paths nuevos (checkout Bearer, retorno GET+POST público con 302 en ambos métodos y los 4 params TBK_* por query y form-urlencoded, pedidos lista/detalle con 404 uniforme), 4 schemas nuevos, enum estado, fila 400 en 'En uso (fase 3)', fila 302 nueva, examples MAURA-000001 — superficie de fases 1-2 intacta"
    requirement: CART-03
    verification:
      - kind: other
        ref: "grep chain del Task 1 (contrato03-ok): versión, 4 paths, 4 schemas, nombre_snapshot, 4 params, '302'+Location, En uso (fase 3), form-urlencoded, MAURA-000001, cancelled/rejected, paths fases 1-2 presentes, sin property precio en CheckoutCreate — pass"
        status: pass
      - kind: other
        ref: "PyYAML safe_load: parse ok, version 0.3.0, tags Pago/Pedidos, retorno get+post con security=[] y responses 302+400 en ambos, checkout 201/400/401/422, enum exacto — pass"
        status: pass
    human_judgment: false
  - id: D2
    description: "ADRs 012-014 (directorio llega a 14) con el formato canónico: 012 firma el retorno con la evidencia del spike citada y la corrección del anulado; 013 registra orden al pagar + stock atómico con la opción 'reservar' en descartadas, REJECTED por carrera y huérfana PENDING hasta fase 4 en Negativas; 014 fija snapshot + numero legible con la asimetría RN-08"
    requirement: ORDR-01
    verification:
      - kind: other
        ref: "grep chain del Task 2 (adrs03-ok): 14 ADRs numerados, 012 cita 03-SPIKE-RETORNO/302/TBK_TOKEN/pago/resultado, 013 con REJECTED/rowcount/ADR-010/PENDING, 014 con MAURA-000001/RN-08/nombre_snapshot/soft delete, los tres con Opciones consideradas y Para conversar en clase — pass"
        status: pass
    human_judgment: false
  - id: D3
    description: "README de 04_arquitectura: fila de pago real del stack (Webpay Plus integración + transbank-sdk 6.1.0 citando ADR-012/013, sin el placeholder 'llega en su fase' que solo queda en IA fase 4), árbol del alumno con models/schemas/repositories/pedido.py, services/pedidos.py, services/webpay.py (único importador de transbank), routers/checkout|retorno|pedidos.py, features/pago y features/pedidos; regla 5 con la nota de la excepción; índice con exactamente 3 filas nuevas"
    verification:
      - kind: other
        ref: "grep chain del Task 3 (readme-arq03-ok): transbank-sdk, 3 links de ADRs, archivos nuevos del árbol, features/pago, features/pedidos, ADR-009 presente, disclaimer guide-only presente — pass"
        status: pass
    human_judgment: false

duration: 8 min
completed: 2026-09-30
status: complete
plan_head_before: 4b0b9c20aa7faaaf78f407a845da353ec6f42809
plan_head_after: 3cee63de07eb0bb5541836a1d990897e4dec4f2f
---

# Phase 3 Plan 2: Contrato 0.3.0 y ADRs 012-014 Summary

**El contrato 0.3.0 declara la superficie completa de la etapa 3 con sus garantías estructurales (checkout sin campo de precio, retorno público GET+POST con 302, ownership 404) y los ADRs 012-014 registran las decisiones del corazón pedagógico firmadas con la evidencia runtime del spike**

## Performance

- **Duration:** 8 min
- **Started:** 2026-09-30T15:31:13Z
- **Completed:** 2026-09-30T15:39:12Z
- **Tasks:** 3
- **Files modified:** 5 (1 contrato extendido, 3 ADRs nuevos, 1 README extendido)

## Accomplishments

- **D-15 honrado**: contrato 0.2.0 → 0.3.0 aprobado DESPUÉS del spike (que ya dejó su evidencia en `.planning/`) y ANTES de las guías 09-11 — la fuente de verdad de la interfaz quedó versionada con la superficie de checkout/pago/pedidos completa.
- **CART-03 escrito en el contrato**: el schema `CheckoutCreate` contiene SOLO `items [{producto_id, cantidad}]` — la ausencia de campo de precio es estructural (gate automatizado: ninguna property `precio` en el schema) y el description explica que el monto sale únicamente del recálculo del servidor.
- **PAY-02 decidido arquitectónicamente**: `/api/pago/retorno` declarado GET+POST con `security: []` narrado, los 4 params de Transbank por query y por form-urlencoded (patrón del login de fase 2), y el response `'302'` con header `Location` en AMBOS métodos (Pitfall 13).
- **ADR-012 firma la mecánica con la evidencia del spike** (D-40/D-41): cita `03-SPIKE-RETORNO.md` por flujo, registra la corrección material del anulado (GET en integración, no POST como decían las docs) como la justificación del discriminador por presencia de params, y documenta la trampa del 307 como primera lección PRG del proyecto.
- **ADR-013 cierra el blocker de STATE.md** (momento de creación de la orden y del descuento de stock, D-34/D-35): la opción "reservar stock al crear" queda en la tabla de descartadas, el descuento atómico (UPDATE condicional + rowcount) en reglas numeradas, y la huérfana PENDING sin gestión hasta fase 4 + el REJECTED por carrera en Negativas honestas (D-48/D-49).
- **ADR-014 fija la asimetría carro/orden como lección** (D-36/D-37): snapshot obligatorio en la orden vs precio prohibido en el carro (RN-08), soportado por el soft delete, y `MAURA-{id:06d}` como buy_order público ≠ id interno.

## Task Commits

1. **Task 1: contrato_api.yaml 0.2.0 → 0.3.0 — checkout, retorno GET+POST con 302 y pedidos** - `7620eee` (docs)
2. **Task 2: ADRs 012-014 — retorno con evidencia del spike, orden nace al pagar + stock al aprobar, snapshot de precio** - `31054fb` (docs)
3. **Task 3: README de 04_arquitectura — fila de pago real, árbol del alumno extendido, índice de 14 ADRs** - `3cee63d` (docs)

## Files Created/Modified

- `docs/04_arquitectura/contrato_api.yaml` - 0.3.0: tags Pago/Pedidos, schemas CheckoutCreate/CheckoutRespuesta/OrdenLista/OrdenDetalle, paths /api/checkout, /api/pago/retorno (GET+POST), /api/pedidos, /api/pedidos/{numero}; tabla de errores con 302 nueva y 400 "En uso (fase 3)"
- `docs/04_arquitectura/adr/012-retorno-de-webpay.md` - Mecánica del retorno firmada con evidencia del spike por flujo
- `docs/04_arquitectura/adr/013-orden-nace-al-pagar-stock-al-aprobar.md` - Ciclo de vida de la orden y del stock (D-34/D-35) con negativas honestas
- `docs/04_arquitectura/adr/014-snapshot-de-precio-en-la-orden.md` - Snapshot de nombre/precio y numero legible como buy_order (D-36/D-37)
- `docs/04_arquitectura/README.md` - Stack con pago construido, árbol del alumno +10 archivos, regla 5 con la excepción del retorno, índice a 14 ADRs

## Decisions Made

- La fila 201 de la tabla de convención de errores se extendió a "En uso (fases 2-3)" con "(registro de una cuenta; orden PENDING al iniciar el pago)": el checkout agrega un segundo uso del 201 en fase 3 y dejar la fila como estaba habría dejado la tabla incompleta respecto de la superficie declarada.
- El índice de ADRs cita en "Resuelto por" los requisitos/decisiones de origen (PAY-02; D-34+D-35; D-36+D-37), igual que las filas de fase 2 citan sus D.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Colon dentro de un scalar plano YAML rompía el parseo del contrato**
- **Found during:** Task 1 (verificación)
- **Issue:** El description de `OrdenLista` decía "liviana: sin líneas" — el par colon+espacio dentro de un scalar plano de una línea hace inválido el YAML (PyYAML: "mapping values are not allowed here", línea 234)
- **Fix:** Reescrito como "liviana, sin líneas"; el resto de las líneas nuevas fue revisado contra el mismo patrón
- **Files modified:** docs/04_arquitectura/contrato_api.yaml
- **Verification:** `yaml.safe_load` parsea el contrato completo; estructura confirmada por script (versión, tags, 11 paths, 11 schemas, security/responses por método)
- **Committed in:** 7620eee (parte del commit del Task 1, corregido antes de commitear)

**2. [Rule 2 - Consistencia documental] Fila 201 de la tabla de errores extendida a fases 2-3**
- **Found during:** Task 1 (redacción de la tabla de errores)
- **Issue:** El plan pedía cambiar la fila 400 y agregar la 302, pero el nuevo `POST /api/checkout` también responde 201 — la fila 201 habría quedado diciendo solo "registro de una cuenta / fase 2" con el contrato declarando un 201 nuevo
- **Fix:** Fila 201 extendida a "Creado (registro de una cuenta; orden PENDING al iniciar el pago) | En uso (fases 2-3)"
- **Files modified:** docs/04_arquitectura/contrato_api.yaml
- **Verification:** `grep "En uso (fase 3)"` (filas 302 y 400) pasa; la tabla queda completa respecto de los responses declarados
- **Committed in:** 7620eee (parte del commit del Task 1)

---

**Total deviations:** 2 auto-fixed (1 bug, 1 consistencia documental)
**Impact on plan:** Ambas correcciones dentro del archivo que el Task 1 ya extendía; ninguna tocó paths/schemas de fases 1-2 ni el alcance del plan.

## Issues Encountered

- **grep con patrón que inicia con `/` bajo Git Bash (path-mangling)**: los greps de `/api/checkout`, `/api/pago/retorno`, `/api/pedidos`, `/api/productos` y `/api/auth/registro` del verify del Task 1 fallan porque MSYS convierte el patrón en ruta de Windows — el mismo artefacto de ambiente ya documentado en 03-01-SUMMARY. Verificado con la clase `[/]api/...` (5/5 PASS); el contenido está, el grep plano es el que miente. La cadena completa del verify se re-ejecutó con ese ajuste y dio `contrato03-ok`.

## Authentication Gates

None - sin servicios externos ni credenciales en este plan (documental puro).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **Onda 3 desbloqueada**: los planes 03-03 (docs 02/03) y 03-04 (guías 09-11) tienen la fuente de verdad lista — las guías implementan el contrato 0.3.0 sin desviarse y la Gran verificación final comparará `/docs` contra 0.3.0 (fila contrato ↔ /docs, ahora con el 302 del retorno en la comparación).
- **Blockers de STATE.md que este plan resuelve**: "decisión pendiente de ADR — momento de creación de la orden y del descuento de stock" queda registrado en ADR-013; el del spike ya lo había resuelto 03-01.
- **Nota para 03-04**: el árbol del alumno y las reglas de dependencia del README ya mencionan los 10 archivos nuevos y la excepción de la regla 5 — las guías deben construir exactamente ese árbol.

## Self-Check: PASSED

- FOUND: docs/04_arquitectura/contrato_api.yaml (versión 0.3.0, parse YAML ok)
- FOUND: docs/04_arquitectura/adr/012-retorno-de-webpay.md
- FOUND: docs/04_arquitectura/adr/013-orden-nace-al-pagar-stock-al-aprobar.md
- FOUND: docs/04_arquitectura/adr/014-snapshot-de-precio-en-la-orden.md
- FOUND: docs/04_arquitectura/README.md (índice de 14 ADRs)
- FOUND: commit 7620eee (Task 1)
- FOUND: commit 31054fb (Task 2)
- FOUND: commit 3cee63d (Task 3)
- Verify Task 1 (contrato03-ok): pass — re-ejecutado post-commit (con workaround [/] por path-mangling de Git Bash)
- Verify Task 2 (adrs03-ok): pass — re-ejecutado post-commit
- Verify Task 3 (readme-arq03-ok): pass — re-ejecutado post-commit

---
*Phase: 03-checkout-webpay-y-rdenes*
*Completed: 2026-09-30*
