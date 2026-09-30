# ADR-016 — Máquina de estados de pedidos con UNA transición manual admin

- **Estado:** Aceptada
- **Fecha:** 2026-09-30
- **Resuelve:** qué transiciones de estado tiene un pedido, quién es dueño de ejecutar cada una y cómo se gestionan por fin las huérfanas PENDING (ADMN-03; decisión D-50)

## Contexto

El pedido ya tiene 4 estados desde la fase 3 — pending, paid, cancelled,
rejected (RF-17) — y todos nacieron del flujo de pago: la orden nace
PENDING al iniciar el pago (D-34), el commit aprobado la pasa a PAID con
descuento atómico de stock, REJECTED cubre la carrera de stock perdida y
el flujo anulado de Webpay la marca CANCELLED por sí mismo
([ADR-013](013-orden-nace-al-pagar-stock-al-aprobar.md),
[ADR-012](012-retorno-de-webpay.md)). Pero quedó una cuenta pendiente
dicha con todas sus letras: la huérfana PENDING — la clienta que salta a
Webpay y no vuelve deja una orden "en curso" que nada expira ni anula
(D-48/D-49). El historial de la fase 3 la muestra honesta y pendiente para
precisamente esto: **su gestión llega con el panel admin de la fase 4**
(guia-11 y RN-11 lo dejaron prometido). Ahora el panel existe y hay que
decidir la máquina completa: qué transiciones son legales, quién es dueño
de cada una y si hacen falta estados nuevos.

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| **A. Los 4 estados existentes, cada transición con dueño, y UNA manual admin: PENDING→CANCELLED** | Cero estados nuevos; cada transición tiene un dueño claro y único; cobra la promesa de las huérfanas (D-48/D-49) con la acción más pequeña posible | La dueña no puede "reabrir" un pedido ni marcar nada como entregado; el refund queda fuera de v1 |
| **B. Estados nuevos de logística (enviado / entregado / despachado)** | Rastreo físico del paquete en el panel | La logística física es Out of Scope del proyecto; infla la máquina con estados que nadie transiciona de verdad en una tienda sandbox |
| **C. Transiciones libres: el admin cambia el estado a lo que sea, sin validar** | Máxima flexibilidad; cero código de validación | Sin máquina no hay invariantes: un PAID "anulado" a mano rompe la contabilidad de ingresos (ADMN-04) y miente sobre un pago que sí ocurrió |

## Decisión

**Opción A.** La máquina son exactamente los 4 estados existentes; cada
transición tiene dueño y las ilegales se rechazan con 409 (D-50):

1. **El flujo de pago posee sus transiciones** (ADR-012/ADR-013):
   PENDING→PAID al aprobar el commit con stock disponible; PENDING→REJECTED
   al perder la carrera de stock; y el propio flujo de Webpay deja la orden
   CANCELLED cuando la clienta anula en el formulario. Nadie más las toca.
2. **El admin tiene exactamente UNA transición manual: PENDING→CANCELLED**
   — la gestión de las huérfanas que guia-11 y RN-11 dejaron prometida
   ("en curso" hasta esta fase): la dueña anula la orden que quedó
   colgando y la clienta la ve CANCELLED en su historial, sin re-editar
   ninguna guía anterior.
3. **Cancelar una PENDING NO toca stock** (D-35): el stock solo se
   descuenta al aprobar el pago, y la huérfana nunca llegó a aprobarse —
   nunca se descontó nada. La transición es limpia: un UPDATE condicional
   `WHERE estado = 'pending'` y nada más, la misma muralla del guard
   ya-PAID de la fase 3 aplicada al otro dueño.
4. **PAID es terminal en v1**: anular un pago real es un refund —
   ADMN-05, diferido explícitamente a v2 (tabla de descartadas junto a
   los estados de logística). Los ingresos del panel (ADMN-04) suman PAID
   sin excepciones manuales que los falseen.
5. **El backend valida contra la máquina y las ilegales responden 409**
   (contrato 0.4.0, con el detail locked "Ese pedido ya no está en
   curso."): es un conflicto de ESTADO del recurso, no un dato mal
   formado — el cuerpo `{estado: "cancelled"}` es sintácticamente válido,
   pero el pedido ya no está donde se pide (OQ3 del research resuelta).

## Consecuencias

**Positivas**
- Las invariantes sobreviven al panel: la contabilidad (suma de PAID) y
  el stock no pueden falsearse desde la interfaz.
- La huérfana PENDING por fin tiene gestión sin jobs de fondo ni ventanas
  de expiración: un humano decide, caso a caso, con la orden a la vista.
- El enum del contrato ES la máquina: `PedidoTransicion` acepta un solo
  valor (`cancelled`) y el 409 cubre la carrera de dos pestañas del panel
  que anulan a la vez — una gana, la otra ve la verdad.

**Negativas (honestas)**
- **No hay salida de CANCELLED ni reapertura**: si la dueña anula por
  error, hay que crear el pedido de nuevo — una transición de vuelta
  agregaría consistencia que v1 no necesita (¿y el stock? ¿y Webpay si
  el pago después llega?).
- **El refund sigue siendo manual y fuera del sistema**: una clienta que
  pagó y quiere su plata de vuelta depende de Webpay por fuera del
  panel (ADMN-05, v2) — el ADR lo declara en vez de fingirlo.
- **La anulación puede perder la carrera con el propio Webpay**: si el
  commit aprobado llega justo después de que la dueña anuló, el guard de
  estado del flujo de pago (guia-09) lo detiene — el pago queda sin orden
  PAID que lo respalde y se gestiona por fuera, como todo refund en v1.

## Para conversar en clase

1. ¿Por qué "enviado" y "entregado" NO son estados de esta máquina, y qué
   tendría que cambiar en el negocio real de Maura para que lo fueran?
2. La dueña anula una PENDING el jueves y la clienta vuelve de Webpay el
   viernes con el pago aprobado: ¿qué pasó con esa plata, quién le
   explica a la clienta y por qué esta decisión lo deja fuera de v1?
3. ¿Por qué 409 y no 422 para la transición ilegal? ¿Qué diferencia hay
   entre "el dato está mal escrito" y "el recurso ya no está donde lo
   pides"?

Relacionada: [ADR-013](013-orden-nace-al-pagar-stock-al-aprobar.md) (la
máquina que este ADR extiende) y
[ADR-014](014-snapshot-de-precio-en-la-orden.md) (el snapshot que hace que
anular o desactivar no rompa la historia).
