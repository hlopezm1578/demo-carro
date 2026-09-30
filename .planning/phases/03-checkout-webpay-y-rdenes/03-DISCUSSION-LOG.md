# Phase 3: Checkout Webpay y órdenes - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-30
**Phase:** 3-Checkout Webpay y órdenes
**Areas discussed:** Orden y stock: cuándo nacen, Spike de retorno Webpay, Vuelta: voucher y carro, Historial de pedidos

---

## Orden y stock: cuándo nacen

| Option | Description | Selected |
|--------|-------------|----------|
| Al iniciar el pago (Recomendado) | POST /api/checkout valida el carro (CART-03), crea la orden PENDING con sus líneas y recién entonces crea la transacción en Webpay y devuelve el form POST. El retorno actualiza esa orden existente. | ✓ |
| Solo al aprobar | La orden solo se materializa cuando el commit dice AUTHORIZED; el carro viaja implícito en sesión del servidor. Menos filas PENDING huérfanas, pero estado transitorio en backend y complica anulado/timeout. | |

**User's choice:** Al iniciar el pago (Recomendado)
**Notes:** Es el ADR pendiente anotado en STATE.md como blocker de fase 3.

| Option | Description | Selected |
|--------|-------------|----------|
| Validar→descontar al aprobar (Recomendado) | Crear PENDING solo VALIDA stock (sin tocarlo). Descuento atómico en el commit aprobado (UPDATE ... WHERE stock >= cantidad en transacción). Si otro compró en el intertanto, el commit falla y la orden pasa a REJECTED. | ✓ |
| Reservar al crear PENDING | Crear la orden descuenta stock de inmediato (reserva); anulado/timeout lo devuelve. Sin riesgo de oversell intermedio, pero "reserva" no es requisito y duplica los puntos donde se toca el stock. | |

**User's choice:** Validar→descontar al aprobar (Recomendado)
**Notes:** Calza literal con ORDR-02 ("descuento al aprobarse el pago"); la carrera perdida es la lección de concurrencia.

| Option | Description | Selected |
|--------|-------------|----------|
| Sí, snapshot de precio y nombre (Recomendado) | Cada línea congela precio unitario y nombre al comprar. El pedido viejo muestra siempre lo que se pagó. Asimetría con RN-08 (carro sin precios) como lección. | ✓ |
| Solo FKs, precio vigente | Las líneas solo traen producto_id + cantidad; el total se recalcula del catálogo actual. Un pedido viejo mostraría precios actuales — el histórico miente. | |

**User's choice:** Sí, snapshot de precio y nombre (Recomendado)
**Notes:** Calza con el soft delete ya diseñado en docs/03 (pedido viejo no queda apuntando a producto borrado).

| Option | Description | Selected |
|--------|-------------|----------|
| Número legible = buy_order (Recomendado) | Número de pedido legible (ej. MAURA-000001) usado a la vez como buy_order ante Webpay (≤26 chars, único). Voucher e historial muestran ese número. Identificador público ≠ clave primaria. | ✓ |
| id interno como buy_order | buy_order = id de BD como string ("orden-42"); se muestra el mismo. Sin campo nuevo, pero enumera filas y revela volumen. | |
| Tú decides el formato | Dejar formato a research/planner sujeto al límite de 26 chars y unicidad; solo fijar que exista identificador visible. | |

**User's choice:** Número legible = buy_order (Recomendado)
**Notes:** Formato exacto queda como Claude's Discretion.

---

## Spike de retorno Webpay

| Option | Description | Selected |
|--------|-------------|----------|
| Plan runtime en maura-uat (Recomendado) | Primer plan de la fase: mini-backend con SDK + credenciales públicas en D:/Repos/maura-uat corre los flujos reales y documenta GET vs POST con parámetros. Hallazgos alimentan contrato/ADRs/guías. Código no se commitea (D-17). | ✓ |
| Spike documental (sin runtime) | Research lee docs de Transbank + SDK y deduce el patrón. Riesgo alto: el spike existe porque la docs no detalla qué trae cada flujo. | |
| Dejarlo para el UAT final | Validar recién en el UAT con la guía ya redactada — contradice el roadmap (spike ANTES de la guía). | |

**User's choice:** Plan runtime en maura-uat (Recomendado)
**Notes:** Resuelve el blocker #1 de STATE.md.

| Option | Description | Selected |
|--------|-------------|----------|
| Los 4 flujos oficiales (Recomendado) | Aprobado (token_ws GET), anulado (token_ws GET), timeout (TBK_ID_SESION POST), error de formulario (TBK_TOKEN/TBK_ORDEN_COMPRA POST). PAY-02 completo de una vez; costo marginal mínimo. | ✓ |
| Mínimo: aprobado/anulado/timeout | Solo el mínimo del roadmap; el 4° flujo se corrobora en UAT con la guía ya escrita sobre un flujo nunca corrido. | |

**User's choice:** Los 4 flujos oficiales (Recomendado)
**Notes:** El roadmap fijaba 3; se amplió al 4° en esta discusión.

| Option | Description | Selected |
|--------|-------------|----------|
| .planning + guía narra (Recomendado) | Hallazgos en .planning/ como insumo del planner; la guía narra "lo que el spike reveló"; el ADR cita el spike como evidencia. Código solo en maura-uat. | ✓ |
| Documento propio en docs/ | Hallazgos como documento del ciclo (anexo de 04_arquitectura). Más visible, pero agrega documento que demo-cine no tiene y mezcla insumo interno con producto. | |
| Solo .planning, guía directa | Hallazgos solo internos y la guía enseña el patrón sin narrar el spike — pierde la lección de cómo se investiga una integración desconocida. | |

**User's choice:** .planning + guía narra (Recomendado)
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| El spike elige (Recomendado) | El spike corre los 4 flujos y elige la mecánica más simple que funcione para todos (redirect 302 con query params vs página intermedia auto-submit); el ADR registra la elegida con evidencia. | ✓ |
| Hipótesis fija + validación | Fijar hoy redirect 302 a la SPA y que el spike solo valide. Más determinista, pero si cae, se replantea a mitad de fase. | |

**User's choice:** El spike elige (Recomendado)
**Notes:** Nadie firma mecánica sobre supuestos.

---

## Vuelta: voucher y carro

| Option | Description | Selected |
|--------|-------------|----------|
| Ruta única de resultado (Recomendado) | Una ruta (ej. /pago/resultado) renderiza voucher/anulado/timeout/error según el flujo. Espeja el endpoint backend GET+POST que discrimina. | ✓ |
| Rutas separadas por flujo | Cuatro rutas (/pago/exito, /pago/anulado, /pago/timeout, /pago/error). URLs explícitas pero 4 páginas de la misma información. | |

**User's choice:** Ruta única de resultado (Recomendado)
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Voucher = detalle completo (Recomendado) | Número, fecha, líneas con nombre y precio snapshot, total, estado PAID, CTA "Seguir comprando". El historial reutiliza la misma vista. | ✓ |
| Voucher mínimo | Solo número + total + "pagado"; el detalle vive solo en el historial. Dos vistas para la misma información y un clic extra. | |

**User's choice:** Voucher = detalle completo (Recomendado)
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Solo se limpia al aprobar (Recomendado) | El carro se limpia en UN punto: pago aprobado (llegada al voucher). Anulado/timeout/error lo dejan intacto. PAY-04 sin snapshots ni restauración: nunca se borró. | ✓ |
| Vaciar al iniciar + restaurar | Vaciar al iniciar el pago y restaurar desde respaldo si vuelve anulado. Estado extra y casos borde (otro carro mientras tanto). | |

**User's choice:** Solo se limpia al aprobar (Recomendado)
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Copys a discreción (Recomendado) | Copys de la vuelta fijados por Claude en guías/UI-SPEC con tono Maura establecido (como fase 2 con sus mensajes de sesión). | ✓ |
| Fijar copys ahora | Fijar aquí los 4 titulares literales (éxito/anulado/timeout/error). | |

**User's choice:** Copys a discreción (Recomendado)
**Notes:** —

---

## Historial de pedidos

| Option | Description | Selected |
|--------|-------------|----------|
| Lista + detalle navegable (Recomendado) | /pedidos lista (número, fecha, total, badge de estado) y clic abre el detalle reutilizando la vista del voucher. | ✓ |
| Lista expandible inline | Acordeón en una sola página, sin detalle propio. El reuso del voucher se complica. | |

**User's choice:** Lista + detalle navegable (Recomendado)
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| "Mis pedidos" en navbar (Recomendado) | Entrada visible con sesión iniciada junto a nombre/cerrar sesión de fase 2; ruta protegida con RequireAuth + returnTo (D-32) heredado. | ✓ |
| Solo desde el voucher | Sin entrada permanente; el historial queda escondido tras el flujo de pago — contradice el espíritu de ORDR-01. | |

**User's choice:** "Mis pedidos" en navbar (Recomendado)
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Todas, PENDING incluida (Recomendado) | Todas las órdenes de la clienta con estado real; PENDING se muestra "en curso". La honestidad del estado es la lección ORDR-01. | ✓ |
| Solo estados terminales | Filtrar a PAID/CANCELLED/REJECTED; una orden a medio pagar desaparece para la clienta. | |

**User's choice:** Todas, PENDING incluida (Recomendado)
**Notes:** —

| Option | Description | Selected |
|--------|-------------|----------|
| Sin expiración en fase 3 (Recomendado) | La PENDING huérfana queda visible tal cual; su gestión llega con el admin de fase 4. La guía no enseña jobs ni ventanas de tiempo. | ✓ |
| Lazy expiry al consultar | Al consultar, PENDING > X minutos → CANCELLED perezosamente. Patrón real sin cron, pero agrega lógica de tiempo y constante arbitraria. | |

**User's choice:** Sin expiración en fase 3 (Recomendado)
**Notes:** —

---

## Consulta del usuario durante el cierre

**Pregunta:** "¿En esta etapa es la integración con Webpay? De ser así, ¿se necesita crear una cuenta o algo así para usar la integración?"

**Respuesta:** Sí, la fase 3 es la integración con Webpay Plus sandbox, pero NO requiere cuenta ni registro en Transbank: las credenciales del ambiente de integración son públicas (código de comercio 597055555532 contra `webpay3gint.transbank.cl`), el SDK Python viene preconfigurado y el pago de prueba usa tarjetas documentadas por Transbank. Solo producción (fuera de alcance) exigiría contrato real. La guía debe dejarlo explícito — registrado en `<domain>` y `<specifics>` de CONTEXT.md.

## Claude's Discretion

- Formato exacto del número de pedido legible (sujeto a límite 26 chars / unicidad de Transbank).
- Nombres/estructura exacta de endpoints y schemas nuevos del contrato 0.3.0.
- Qué ADRs escribe la fase (candidatos: retorno Webpay, orden+stock, snapshot de precio) continuando desde ADR-012.
- Numeración nueva RF/RNF/RN/HU (continuar series) y partición en sub-guías guia-09+.
- Mecánica concreta del stock atómico en SQLite (research valida el patrón).
- Alcance mínimo del mini-backend del spike.
- Badges/colores por estado y copys de la vuelta (D-45).

## Deferred Ideas

None — discussion stayed within phase scope
