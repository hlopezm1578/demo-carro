# ADR-014 — Snapshot de precio en la orden y numero legible como buy_order

- **Estado:** Aceptada
- **Fecha:** 2026-09-30
- **Resuelve:** qué muestra un pedido viejo cuando el catálogo cambia después, y con qué identificador lo ve la clienta (ORDR-01; decisiones D-36/D-37)

## Contexto

La dueña cambia precios y nombres del catálogo todo el tiempo: rebaja de
temporada, renombrado de un aroma, productos que se esconden del catálogo.
Pero un pedido es un hecho histórico — si la clienta abre en marzo su
pedido de enero, el detalle tiene que mostrar **lo que pagó ese día**, no
lo que vale hoy el producto. En el carro la pregunta ya se respondió al
revés (RN-08: el carro guarda SOLO ids y cantidades, jamás precios — un
precio guardado en el navegador es una foto vieja esperando engañar). La
orden necesita exactamente la decisión contraria. Además, Webpay exige un
identificador de compra (`buy_order`) único de hasta 26 caracteres, y la
clienta necesita un numero humano para voucher e historial.

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| **A. Las líneas guardan snapshot de nombre y precio congelados al comprar, y la orden tiene un numero legible público `MAURA-{id:06d}` que a la vez es el buy_order** | El pedido viejo siempre muestra lo que se pagó, aunque el catálogo cambie o el producto se borre; el numero es único por construcción (nace del autoincrement) y cabe con sobra en el límite de 26 chars; la clienta ve `MAURA-000001`, no un id interno | Cada línea guarda dos columnas extra (nombre_snapshot, precio_snapshot); el numero se genera, no se elige |
| **B. Calcular el detalle desde el catálogo vigente** | Cero columnas extra; una sola fuente de precios | El pedido miente: si cambió el precio, el "detalle" muestra un total distinto al pagado; si el producto se borró, el detalle revienta |
| **C. Snapshot solo del total en la orden, sin líneas** | Una columna; el total histórico queda bien | Se pierde el detalle de lo comprado: el voucher no puede mostrar qué aromas llevó ni a qué precio unitario |

## Decisión

**Opción A.** Cada línea de la orden congela `nombre_snapshot` y
`precio_snapshot` al momento de comprar, y la orden expone un numero
público legible (D-36/D-37):

1. **La asimetría con RN-08 ES la lección** (D-36): en el CARRO el precio
   guardado está **prohibido** — sería un precio viejo esperando engañar;
   en la ORDEN el snapshot es **obligatorio** — es el histórico de lo que
   se pagó. La diferencia es el contexto: "lo que vale hoy" versus "lo
   que se pagó". El detalle del pedido jamás consulta el catálogo
   vigente: renderiza el snapshot.
2. **El soft delete del diseño lo soporta** (docs/03 §2.3.5): la FK a
   productos sigue viva aunque el producto se oculte o se marque
   inactivo — un pedido viejo no puede quedar apuntando a un producto
   borrado, y con snapshot ni siquiera lo necesita para mostrarse.
3. **El id interno de BD jamás es identificador público** (D-37): el
   numero legible `MAURA-{id:06d}` (ej. `MAURA-000001`, 11 caracteres)
   nace del autoincrement en la misma transacción — único por
   construcción, muy bajo el límite de 26 chars que exige Webpay — y es
   a la vez el `buy_order` que viaja a la pasarela y el numero que la
   clienta ve en voucher e historial. Lección: identificador público ≠
   clave primaria.

## Consecuencias

**Positivas**
- El historial es un documento fiel: renombrados, rebajas y borrados del
  catálogo no reescriben la historia de ninguna clienta (ORDR-01).
- El numero legible sirve de llave única en los tres mundos a la vez —
  base de datos (unique), Webpay (buy_order) y pantalla (voucher) — sin
  sincronizar nada.
- El monto del snapshot cuadra siempre con el total recalculado por el
  servidor al crear la orden (CART-03,
  [ADR-013](013-orden-nace-al-pagar-stock-al-aprobar.md)): ambos nacen del
  mismo precio vigente en el mismo instante.

**Negativas (honestas)**
- **Cada línea duplica dos columnas** (nombre, precio): la orden deja de
  ser "viva" — si la dueña corrige un nombre mal escrito, los pedidos
  viejos conservan el error.
- **El numero revela volumen**: `MAURA-000042` le dice a una clienta
  cuántos pedidos hubo antes — aceptable para una PYME sandbox; el
  ownership del endpoint (404 uniforme) impide usarlo para husmear
  pedidos ajenos.

## Para conversar en clase

1. ¿Por qué la misma columna `precio` que está prohibida en el carro
   (RN-08) es obligatoria en la orden? ¿Qué pregunta distinta responde
   cada una?
2. La dueña rebaja un aroma de \$9.990 a \$6.990: ¿qué ve la clienta que
   compró ayer en su pedido, qué ve la que compra hoy, y dónde vive cada
   precio?
3. ¿Por qué usar el id interno de la tabla como numero público sería un
   problema de seguridad además de un problema de usabilidad? (Pista:
   ¿qué puede inferir un visitante de `/api/pedidos/17`?)
