# ADR-010 — El carro vive en el navegador y se hidrata con precios vigentes

- **Estado:** Aceptada
- **Fecha:** 2026-09-29
- **Resuelve:** dónde vive el carro de compras mientras la clienta arma su pedido, y qué datos guarda

## Contexto

En la fase 1 el catálogo es público y anónimo: no hay sesión, y sin sesión no
hay carro en el servidor — una tabla `carritos` exigiría cuenta para el
primer click en "Agregar". Pero el carro también es una lección de confianza:
si el navegador guardara precios, la clienta estaría comprando contra una
foto vieja del catálogo (y un atacante, editándolos a mano). La decisión
cubre dos preguntas juntas: **dónde** vive el carro y **qué** guarda (D-27).

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| **A. Store client-side con solo pares `{producto_id, cantidad}`**, hidratado contra la API | El visitante anónimo arma su carro sin cuenta; el precio mostrado es siempre el vigente; cero tablas y endpoints nuevos | Cada vista del carro consulta la API (hidratación); un producto puede desaparecer del catálogo dejando una fila degradada |
| **B. Carro en el servidor con tabla propia** | Fuente única de verdad; sobrevive cualquier navegador; listo para la orden de la fase 3 | Exige sesión iniciada para el primer ítem; tabla + endpoints + reglas que la fase 2 no necesita |
| **C. Snapshot completo en el navegador** (nombre y precio incluidos) | El carro se muestra sin consultar nada; sobrevive sin red | El precio mostrado puede estar viejo o manipulado; el cliente decide precios — el anti-patrón exacto del que la fase 3 debe desconfiar |

## Decisión

**Opción A.** El carro es un store de Zustand con `persist` sobre
`localStorage` que guarda **solo pares `{producto_id, cantidad}`** — nada de
nombres, nada de precios (D-27):

1. **Sin precios almacenados**: la página `/carro` hidrata cada ítem
   consultando la API y muestra siempre el precio vigente del catálogo — el
   navegador jamás decide precios (D-27).
2. **Las cantidades se tapan al stock vigente en pantalla** (ficha y carro,
   leído de la hidratación): sin sobreventa visible desde ya (D-30).
3. **La validación real del backend llega en la fase 3 como segunda
   barrera**: lo que se tapa en pantalla es cortesía de UX; el servidor
   volverá a validar el stock y a recalcular el total al crear la orden
   (CART-03) — nunca confía en el cliente.

## Consecuencias

**Positivas**
- El visitante sin cuenta arma su carro completo: la conversión no depende
  del registro, solo el checkout (AUTH-04, fase 2).
- Un cambio de precio del catálogo se refleja al instante en el carro — no
  existe la foto vieja.
- La estructura queda lista para la fase 3: el backend recibirá ids y
  cantidades, y nada más.

**Negativas (honestas)**
- **Hidratación requerida**: mostrar el carro cuesta una consulta a la API
  por ítem (cacheadas por TanStack Query); sin red no hay precios.
- **Un ítem puede apuntar a un producto que ya no existe**: la hidratación
  recibe 404 y el carro muestra una fila degradada ("este aroma ya no está
  disponible") con la opción de quitarlo — feo pero honesto.
- **El carro no cruza dispositivos**: vive en el navegador; la clienta que
  empieza en el celular y sigue en el computador parte de cero.

## Para conversar en clase

1. ¿Por qué guardar el precio en el `localStorage` es un problema de
   seguridad y no solo de frescura? ¿Quién se perjudica si alguien edita el
   JSON a mano antes del checkout?
2. La dueña baja el stock de un aroma a 2 unidades y la clienta tiene 5 en
   el carro persistido: ¿qué ve al abrir `/carro`, y quién tiene la última
   palabra cuando confirme la compra en la fase 3?
3. ¿Qué le sumaría a esta decisión un carro sincronizado entre dispositivos
   para usuarias con cuenta? ¿Qué tablas y endpoints nuevos exigiría?
