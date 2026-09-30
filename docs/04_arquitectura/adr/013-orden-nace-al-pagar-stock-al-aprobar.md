# ADR-013 — La orden nace al iniciar el pago y el stock se descuenta al aprobar

- **Estado:** Aceptada
- **Fecha:** 2026-09-30
- **Resuelve:** en qué momento nace la orden y en qué momento se descuenta el stock del catálogo (CART-03, ORDR-02; decisiones D-34/D-35)

## Contexto

El carro vive en el navegador y guarda solo ids y cantidades
([ADR-010](010-carro-client-side.md)); su regla 3 ya prometía que "el
servidor volverá a validar el stock y a recalcular el total al crear la
orden (CART-03) — nunca confía en el cliente". Llegó la etapa de pagar esa
promesa. Hay que decidir dos cosas juntas: **cuándo existe la orden** (el
commit de Webpay necesita mapear token → orden para saber a quién volver) y
**cuándo se toca el stock** (tocarlo dos veces — reservar y confirmar —
duplica los puntos donde el inventario puede quedar inconsistente). El
estado PENDING existe en ORDR-01 precisamente porque hay una ventana entre
"inicié el pago" y "Webpay me confirmó".

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| **A. La orden nace al iniciar el pago; el stock se valida al crear y se descuenta atómico al aprobar** | El commit siempre tiene a quién volver (token → orden por buy_order); el stock se toca en UN solo punto; la validación del checkout es la segunda barrera de CART-03 que ADR-010 prometía | Existen órdenes PENDING huérfanas (la clienta que no vuelve de Webpay); una compra concurrente que pierde el stock ve REJECTED |
| **B. La orden nace al volver del pago** | Sin huérfanas: solo se guarda lo pagado | El commit no tiene a quién mapear el token: la transacción de Webpay existiría antes que la orden — el retorno llega a un backend que no sabe de qué compra hablan |
| **C. Reservar el stock al crear la orden** (descontar al crear, restituir si falla) | El checkout garantiza el stock durante todo el pago | Duplica los puntos donde se toca el stock (reservar + confirmar/restituir) y agrega estados intermedios que los requisitos no piden; las huérfanas ahora además DEJAN STOCK SECUESTRADO |

## Decisión

**Opción A.** `POST /api/checkout` valida, crea y delega; el commit aprobado
descuenta — cada pieza en su momento (D-34/D-35):

1. **La orden nace PENDING al iniciar el pago** (D-34): el checkout valida
   el carro recalculando precios y stock contra el catálogo (CART-03 — el
   monto que viaja a Webpay sale únicamente de ese recálculo), crea la
   orden PENDING con sus líneas y recién entonces crea la transacción en
   Webpay. Si algo falla entre ambos, la transacción de BD revierte la
   orden: todo en el mismo bloque.
2. **Crear SOLO VALIDA el stock, no lo toca** (D-35): la primera barrera es
   RN-09 en pantalla; esta es la segunda, en backend. Insuficiente → 400
   con la fila que no alcanzó (la fila 400 de la tabla de errores del
   contrato pasa a "En uso (fase 3)").
3. **El descuento ocurre al aprobarse el commit, atómico y transaccional**
   (D-35, ORDR-02): un UPDATE condicional `WHERE stock >= cantidad` por
   línea, en la MISMA transacción SQLAlchemy que transiciona la orden a
   PAID. La condición va dentro del SQL, no leída en Python: dos threads
   que leen el mismo stock no pueden ambos "alcanzar".
4. **`rowcount` 0 → la orden pasa a REJECTED**: si una compra concurrente
   ganó el stock en el intertanto, el UPDATE no encuentra filas, la
   transacción revierte el descuento parcial y la orden queda REJECTED con
   el pago aprobado — la clienta ve la verdad, no un voucher falso. Es la
   lección real de concurrencia de ORDR-02.

## Consecuencias

**Positivas**
- El stock se modifica en un único punto del sistema: el commit aprobado.
  No hay reserva que restituir ni estados intermedios que inventar.
- La carrera de stock queda **demostrable en clase**: stock=1 y dos
  checkout concurrentes terminan en un PAID y un REJECTED — sin
  infraestructura de carga, con el dev server y dos requests.
- El monto pagado siempre fue calculado por el servidor (CART-03): el
  carro del cliente jamás decide precios, ni siquiera pudo intentarlos
  (el schema de entrada no tiene campo de precio).

**Negativas (honestas)**
- **La huérfana PENDING queda visible sin gestión** (D-48/D-49): una
  clienta que salta a Webpay y no vuelve deja una orden "en curso" que
  nada expira ni anula — sin jobs de fondo ni ventanas de tiempo en esta
  fase; su gestión (anular/cerrar) llega con el panel admin de la fase 4.
- **Una compra concurrente que pierde el stock ve REJECTED**: el pago se
  autorizó en la tarjeta pero la orden se rechaza por no poder
  descontar — honesto para el inventario, incómodo para la clienta
  (con tarjeta de prueba sandbox, sin plata real de por medio).
- **Validar al crear no garantiza el stock al aprobar**: entre el
  checkout y el commit hay una ventana — por eso mismo el descuento es
  condicional y no una simple resta.

## Para conversar en clase

1. Dos clientas pagan a la vez la última unidad: ¿qué ve cada una, en qué
   orden se decide, y por qué el `WHERE stock >= cantidad` del UPDATE es
   la muralla y no el `if` de Python?
2. ¿Qué tendría que pasar (tabla nueva, job de fondo, ventana de tiempo)
   para que las órdenes PENDING huérfanas se expiren solas — y por qué
   esta fase deliberadamente no lo hace?
3. La opción "reservar stock al crear" suena más amable con la clienta:
   ¿qué nuevos estados y qué nuevas ventanas de inconsistencia exigiría?

Relacionada: el snapshot de precio que las líneas de esa orden congelan al
nacer está en el [ADR-014](014-snapshot-de-precio-en-la-orden.md).
