---
phase: 03-checkout-webpay-y-rdenes
plan: "03"
subsystem: payments
tags: [requerimientos, diseño, webpay, snapshot-de-precio, dfd, pantallas, trazabilidad]

requires:
  - phase: 03-checkout-webpay-y-rdenes (plan 01)
    provides: "03-SPIKE-RETORNO.md — el veredicto por flujo que la redacción del retorno respeta (anulado con TBK_TOKEN por presencia de params, jamás por método)"
  - phase: 03-checkout-webpay-y-rdenes (plan 02)
    provides: "ADRs 012-014 ya escritos — las decisiones de diseño 11+ los citan por número y estos citan el soft delete de §2.3.5 (ida y vuelta)"
provides:
  - "docs/02_requerimientos.md con la etapa 3 completa: RF-12..RF-18 (los 7 IDs CART-03/PAY-01..04/ORDR-01/02 con origen P6), RNF-07, RN-10..RN-13, HU-09..HU-11, fila P6 real, alcance/entradas/pantallas/aprobación"
  - "docs/03_diseno.md con PEDIDO/LÍNEA (snapshot D-36, numero legible D-37) conectando USUARIO↔PRODUCTO, Webpay como primer servicio externo, almacén D3, DFDs 9.0-11.0, pantallas 8-9 y variante del CTA en la 7"
affects: [03-checkout-webpay-y-rdenes (planes 03-04, 03-05), guia-09/10/11, Gran verificación final de fase 3]

actuals:
  tokens: 12010     # chars/4 sobre el diff real commiteado (48043 chars en 2 archivos)
  tasks: 2
  commits: 2        # medido: git rev-list --count ea1c478..HEAD

tech-stack:
  added: []         # plan documental puro (guide-only, D-17) — sin paquetes
  patterns:
    - "Tercera extensión in-place de los docs del ciclo: continuar series sin renumerar + el marcador '(desde la etapa N)' en ítems existentes (ítem 7 de §12 repite el patrón que la etapa 2 fijó en el ítem 3)"
    - "La evidencia del spike como fuente de redacción de requerimientos: el RF-14 del retorno dice 'presencia de params, jamás método HTTP' porque el spike lo demostró con el anulado por GET"

key-files:
  created: []
  modified:
    - docs/02_requerimientos.md
    - docs/03_diseno.md

key-decisions:
  - "RF-12..RF-18 cubren los 7 IDs de la fase en orden de flujo (recalculo CART-03 primero, órdenes al final): la numeración sigue el recorrido de la clienta y no el orden del plan"
  - "La redacción del retorno (RF-14 + reglas del DFD 10.0) respeta el veredicto del spike: discriminación por presencia de params con TBK_TOKEN en el anulado — la hipótesis original de D-39 quedó enterrada por la evidencia"
  - "PAY-03 quedó como regla literal en RF-15: response_code == 0 Y status == AUTHORIZED, ambos, con el refresh que no paga dos veces"
  - "Las 3 reglas nuevas existen como RN con su porqué ANTES de las guías: RN-10 snapshot con la asimetría RN-08 dicha, RN-11 estados honestos 'en curso' sin expiración (D-48/D-49), RN-12 stock atómico con la condición dentro del UPDATE (D-35), RN-13 numero legible jamás el id (D-37)"
  - "PEDIDO/LÍNEA en el ER con las primeras relaciones del sistema (USUARIO ||--o{ PEDIDO, PEDIDO ||--|{ LÍNEA, LÍNEA }o--|| PRODUCTO) y el diccionario fija los campos exactos de Pattern 6 del research"
  - "P7/P8 de §13 re-redactadas ('llegan con la etapa 4') porque el verify exige que la frase 'sin requerimiento en esta etapa' desaparezca del documento completo"

patterns-established:
  - "Variante de pantalla por etapa: la pantalla 7 gana 'Variante de la etapa 3 — el CTA se enciende' espejando la variante 'Agregar al carro' que la etapa 2 añadió a la ficha (pantalla 3)"
  - "Un DFD por HU nueva con su bloque 'Reglas del proceso' citando RF/RN: 9.0 checkout, 10.0 retorno (las reglas del discriminador), 11.0 historial"

requirements-completed: [CART-03, PAY-01, PAY-02, PAY-03, PAY-04, ORDR-01, ORDR-02]

coverage:
  - id: D1
    description: "docs/02_requerimientos documenta la etapa 3: RF-12..RF-18 con origen P6, RNF-07 (dependencia sandbox sin registro), RN-10..RN-13 con su porqué, HU-09..HU-11 (7 escenarios Dado nuevos), fila P6 con mapeo real, bloque de alcance de etapa 3, entradas (retorno Webpay opaco + carro sin precios), pantallas 8-9 y bloque de aprobación — series etapas 1-2 intactas"
    requirement: CART-03
    verification:
      - kind: other
        ref: "grep chain del Task 1 (req03-ok): RF-12/RNF-07/RN-10/HU-09/CART-03/PAY-01/ORDR-01/response_code/AUTHORIZED/snapshot-congelado/en curso/MAURA-000001/TBK_TOKEN/Etapa 3/RF-11/HU-08 presentes, 'sin requerimiento en esta etapa' ausente, 24 escenarios Dado (>=19) — pass, re-ejecutado post-commit"
        status: pass
    human_judgment: false
  - id: D2
    description: "docs/03_diseno diseña la etapa 3: entidades PEDIDO/LÍNEA con snapshot (nombre_snapshot/precio_snapshot, numero MAURA-000001 <=26) conectando USUARIO con PRODUCTO, Webpay como entidad externa del contexto, almacén D3, DFDs 9.0-11.0 con Reglas del proceso (discriminación por params, commit solo normal, criterio doble, guard ya-PAID, descuento atómico), pantallas 8-9 con estados (incluido degradado sin sesión) y variante del CTA en la 7, decisiones 11-14 citando ADR-012..014, 16 filas nuevas de trazabilidad"
    requirement: ORDR-01
    verification:
      - kind: other
        ref: "grep chain del Task 2 (dis03-ok): PEDIDO/nombre_snapshot/precio_snapshot/MAURA-000001/9.0/10.0/11.0/Webpay/D3/en curso/Seguir comprando/pago/resultado/ADR-013/RN-08 presentes, 11 bloques Reglas del proceso (>=10) y 9 Origen de pantalla (>=9) — pass, re-ejecutado post-commit"
        status: pass
    human_judgment: false

duration: 13 min
completed: 2026-09-30
status: complete
plan_head_before: ea1c47864d69e2a3448b4218b3046af0c467fbaf
plan_head_after: c82e6883224b0577dd167bfdb5958461cc2b4298
---

# Phase 3 Plan 3: Especificación de la etapa 3 en docs/02 y docs/03 Summary

**Los requerimientos del pago con Webpay y las órdenes (RF-12..18, RNF-07, RN-10..13, HU-09..11 con la fila P6 real) y el diseño que los aterriza — PEDIDO/LÍNEA con snapshot congelado conectando USUARIO↔PRODUCTO, Webpay como primer servicio externo, DFDs 9.0-11.0 y las pantallas 8-9 de la vuelta del pago — sin renumerar nada de las etapas 1-2**

## Performance

- **Duration:** 13 min
- **Started:** 2026-09-30T15:44:05Z
- **Completed:** 2026-09-30T15:57:32Z
- **Tasks:** 2
- **Files modified:** 2 (docs/02_requerimientos.md +87/-14, docs/03_diseno.md +294/-15)

## Accomplishments

- **La cadena P6 → RF-12+ → HU-09+ → pantalla 8+ → ADR-012+ quedó continua** (el patrón que la fase 2 estableció con P5): la fila P6 de §13 mapea a los RF/RN/HU nuevos, el diseño los cita por número y las decisiones 11-14 citan los ADRs 012-014 que el plan 03-02 ya escribió.
- **La redacción del retorno respeta la evidencia del spike, no la hipótesis**: RF-14 y las reglas del DFD 10.0 discriminan los 4 flujos SOLO por presencia de params (`token_ws` / `TBK_TOKEN` / `TBK_ID_SESION` / `TBK_ORDEN_COMPRA`), jamás por método HTTP — exactamente el veredicto de 03-SPIKE-RETORNO.md (el anulado llegó por GET con TBK_TOKEN, contradiciendo la documentación oficial).
- **Las 3 reglas nuevas existen como RN con su porqué antes de que las guías las enseñen**: RN-10 snapshot obligatorio con la asimetría RN-08 dicha en el mismo párrafo (prohibido en el carro, obligatorio en la orden), RN-11 estados honestos con PENDING visible "en curso" y sin expiración en esta etapa, RN-12 stock validado al crear y descontado atómico al aprobar con la condición dentro del UPDATE.
- **PAY-03 como regla literal (RF-15)**: la orden pasa a pagada solo con `response_code == 0` Y `status == AUTHORIZED` — ambos — y refrescar no paga dos veces.
- **El modelo de datos del pedido quedó fijado**: PEDIDO (numero legible `MAURA-000001` ≤26 = buy_order, estado de 4 valores, total entero recalculado por el backend) y LÍNEA (nombre_snapshot/precio_snapshot congelados, FKs con el soft delete vivo) — los campos exactos del Pattern 6 del research que contrato, ADR-014 y guías citan.
- **El diseño modela la vuelta del navegador externo**: Webpay como primera entidad externa del contexto, almacén D3 Pedidos, DFD 10.0 con las reglas del retorno (commit solo en el flujo normal, criterio doble, guard ya-PAID, descuento atómico en la misma transacción, 302 a la ruta única), pantalla 8 con sus 4 caras + degradado sin sesión, pantalla 9 con badges honestos que reutilizan el voucher.

## Task Commits

1. **Task 1: docs/02_requerimientos — etapa 3 del pago: RF/RNF/RN/HU nuevos, fila P6 real y bloque de aprobación** - `352b6df` (docs)
2. **Task 2: docs/03_diseno — entidades PEDIDO/LÍNEA con snapshot, Webpay externa, DFDs 9.0+ y pantallas 8-9** - `c82e688` (docs)

## Files Created/Modified

- `docs/02_requerimientos.md` - Etapa 3: RF-12..RF-18 (subsección "Pago con Webpay y órdenes"), RNF-07, RN-10..RN-13, HU-09..HU-11 con 7 escenarios nuevos, §1 contexto/objetivo/alcance temporal actualizados, §2 bloque "Dentro del alcance de la etapa 3", §3 clienta con pedidos, §8 fila PEDIDO + nota, §9 procesos 9-11, §10 entradas (retorno Webpay opaco, carro sin precios), §12 ítem 7 con marcador de etapa + ítems 8-9, §13 fila P6 real + P7/P8 re-redactadas, §14 bloque de aprobación de etapa 3.
- `docs/03_diseno.md` - Etapa 3: §1 tabla de secciones, §2.1 ER con PEDIDO/LÍNEA y las 3 relaciones nuevas + nota actualizada, §2.2 diccionario con las tablas PEDIDO y LÍNEA, §2.3 decisiones 11-14 + pregunta etapa 3 + bloque ADRs 012-014, §3.1 Webpay como entidad externa, §3.2 almacén D3, §3.11-§3.13 DFDs 9.0/10.0/11.0 con Reglas del proceso, §4.8 variante del CTA encendido, §4.9 pantalla 8, §4.10 pantalla 9, §5 16 filas de trazabilidad nuevas.

## Decisions Made

- El orden de los RF nuevos sigue el recorrido de la clienta (RF-12 recalculo CART-03 → RF-13 iniciar pago → RF-14 retorno → RF-15 criterio → RF-16 voucher → RF-17 historial → RF-18 stock atómico) en vez del orden de la lista del plan: la serie se lee como el flujo.
- Las filas P7/P8 de §13 se re-redactaron a "*(llegan con la etapa 4: …)*": el verify del plan exige que la frase "sin requerimiento en esta etapa" desaparezca del documento completo, y las dos filas restantes la contenían.
- En el ER, la entidad se nombra `LINEA` dentro del mermaid (sin acento, siguiendo la convención sin acentos de los comentarios existentes del diagrama) y "LÍNEA" en el diccionario y la prosa.
- HU-08 quedó verbatim (incluido su paréntesis histórico "que llega en la etapa siguiente"): el criterio de aceptación exige que las series existentes queden intactas — la narración del pago nuevo vive en HU-09+.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Consistencia documental] docs/02: secciones no enumeradas por el plan pero exigidas por las convenciones del documento**
- **Found during:** Task 1 (redacción de docs/02)
- **Issue:** El plan enumera 10 puntos de edición, pero el documento tiene promesas de la etapa 2 que quedaban falsas al documentarse la etapa 3: la fila de la clienta en §3 decía "(más adelante) revisar sus pedidos", §8 no tenía la fila PEDIDO (la convención es que cada etapa agrega su entidad — fase 2 agregó USUARIO), §9 no tenía los procesos 9-11 (insumo de los DFDs nuevos de docs/03) y el ítem 7 de §12 decía "deshabilitada hasta la etapa siguiente"
- **Fix:** Fila de clienta actualizada (P5, P6 con "pagar con Webpay y revisar sus pedidos"), fila PEDIDO + nota de decision de datos agregadas a §8, procesos 9-11 agregados a §9, ítem 7 con el marcador "(desde la etapa 3)" — el mismo patrón que el ítem 3 usa para "Agregar al carro"
- **Files modified:** docs/02_requerimientos.md
- **Verification:** grep chain req03-ok pasa; diff confirma que ninguna serie RF/RN/HU existente fue tocada
- **Committed in:** 352b6df (parte del commit del Task 1)

**2. [Rule 2 - Consistencia documental] docs/03: enumeraciones de §1 desactualizadas**
- **Found during:** Task 2 (redacción de docs/03)
- **Issue:** La tabla de §1 ("Qué diseña este documento") decía "HU-01…HU-08" y "7 pantallas" — falsas con 3 HUs, 2 pantallas y 3 DFDs nuevos
- **Fix:** §1 actualizada a "HU-01…HU-11", "9 pantallas" y las filas §2/§4 con los RF/RN de etapa 3
- **Files modified:** docs/03_diseno.md
- **Verification:** grep chain dis03-ok pasa; los 8 DFDs previos, las 7 pantallas previas y las decisiones 1-10 intactas (diff sin eliminaciones fuera de lo planificado)
- **Committed in:** c82e688 (parte del commit del Task 2)

---

**Total deviations:** 2 auto-fixed (2 consistencia documental)
**Impact on plan:** Ambas dentro de los archivos que las tareas ya extendían; ninguna tocó numeración existente ni el alcance del plan. Mantiene la regla de la fase 2 de que cada extensión deja el documento coherente consigo mismo.

## Issues Encountered

None - sin artefactos de ambiente esta vez (ningún grep del verify usa patrón que inicie con `/`; el de "pago/resultado" pasa plano).

## Authentication Gates

None - plan documental puro.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **Onda 4 (03-04) desbloqueada**: las guías 09-11 citan RF/RN/HU por número, los DFDs con sus reglas y las pantallas con sus estados — la materia prima que esperaban ya existe, junto al contrato 0.3.0 (03-02).
- **La redacción del retorno es la del spike**: las guías pueden enseñar el discriminador por presencia de params sabiendo que ni la documentación oficial acertó el método — la lección ya está dicha en las reglas del DFD 10.0.
- **Nota para 03-04**: la pantalla 8 declara el degradado sin sesión (Pitfall 12) y la pantalla 9 reutiliza el voucher (D-43/D-46) — las guías deben construir exactamente eso; el CTA de la pantalla 7 se enciende con el form auto-submit (variante documentada en §4.8).

## Self-Check: PASSED

- FOUND: docs/02_requerimientos.md (RF-12..18, RNF-07, RN-10..13, HU-09..11, fila P6 real, bloque Etapa 3)
- FOUND: docs/03_diseno.md (PEDIDO/LÍNEA con snapshot, Webpay, D3, DFDs 9.0-11.0, pantallas 8-9, decisiones 11-14)
- FOUND: commit 352b6df (Task 1)
- FOUND: commit c82e688 (Task 2)
- Verify Task 1 (req03-ok): pass — re-ejecutado post-commit
- Verify Task 2 (dis03-ok): pass — re-ejecutado post-commit

---
*Phase: 03-checkout-webpay-y-rdenes*
*Completed: 2026-09-30*
