# ADR-012 — El retorno de Webpay: 302 hacia la ruta única de la SPA, discriminando por presencia de params

- **Estado:** Aceptada
- **Fecha:** 2026-09-30
- **Resuelve:** cómo vuelve el navegador de la clienta desde el formulario de Webpay a la tienda, y cómo el backend distingue los 4 flujos oficiales del retorno (PAY-02)

## Contexto

Cuando la clienta termina (o abandona) el formulario hosted de Webpay, es el
**navegador** — no la SPA — el que vuelve al `return_url` del backend: una
navegación de página completa, sin Bearer y sin `fetch` de por medio. Las
docs oficiales describen 4 flujos de retorno con distintos parámetros
(`token_ws`, `TBK_TOKEN`, `TBK_ID_SESION`, `TBK_ORDEN_COMPRA`), pero el
método HTTP por flujo resultó poco confiable: el spike de la fase corrió los
flujos reales contra el ambiente de integración y observó el flujo anulado
llegando **por GET** cuando las docs declaraban POST para integración
(corrección material registrada en la tabla de veredictos por flujo de
[`03-SPIKE-RETORNO.md`](../../../.planning/phases/03-checkout-webpay-y-rdenes/03-SPIKE-RETORNO.md),
D-40/D-41). La decisión cubre dos preguntas juntas: **qué responde** el
endpoint del retorno y **cómo discrimina** el flujo.

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| **A. Redirect 302 del backend a la ruta única `/pago/resultado` de la SPA**, con el resultado como query params | La más simple que funciona para los 4 flujos; es la variante del plugin oficial de Transbank para WordPress (`wp_redirect`, o sea 302); la SPA no necesita el body del POST — le basta el flujo y la orden para fetchear el pedido | El resultado viaja visible en la URL (query params) |
| **B. Página intermedia HTML que auto-submitea el POST hacia la SPA** | Entrega intacto el body del POST a la ruta de destino | Más piezas móviles (plantilla intermedia + form + submit automático); cero ganancia: la SPA no necesita el body |
| **C. Responder JSON y que la SPA navegue** | Reutiliza el patrón JSON del resto de la API | JSON no navega: quien recibe la respuesta es el navegador tras un POST/GET de Webpay, no un `fetch` de la SPA |

## Decisión

**Opción A.** El backend responde siempre una redirección **302 explícita**
hacia la ruta única de resultado de la SPA (`/pago/resultado`, D-42), con el
flujo discriminado y el numero de la orden como query params. La mecánica
queda firmada con la evidencia runtime del spike:

1. **El endpoint se declara GET y POST, y discrimina por PRESENCIA de
   params — jamás por método HTTP.** El spike lo corroboró de la forma más
   convincente posible: el método real del anulado CONTRADIJO a la
   documentación oficial (GET en vez de POST en integración), mientras que
   la presencia de parámetros fue 100% estable en los 25+ retornos
   observados: flujo normal con `token_ws` solo; anulado con `TBK_TOKEN` +
   `TBK_ID_SESION` + `TBK_ORDEN_COMPRA` sin `token_ws`; timeout con
   `TBK_ID_SESION` + `TBK_ORDEN_COMPRA` sin token; error de formulario con
   los 4 juntos.
2. **El redirect usa 302 explícito, no el default.** `RedirectResponse(url)`
   sin `status_code` responde **307**, que preserva método + body: si el
   retorno llegó por POST, la "redirección" re-POSTearía el form de Webpay
   contra la SPA — que no tiene handler POST — y la pantalla revienta. El
   302 fuerza el GET del navegador: la primera lección PRG
   (Post/Redirect/Get) del proyecto.
3. **`security: []` deliberado** (PAY-02): quien llama es el navegador
   recién salido de Webpay, sin Bearer. La sesión se retoma después en la
   SPA, con el JWT que sobrevivió el full-page load en `localStorage`
   ([ADR-009](009-jwt-larga-vida-localstorage.md)). Un retorno forjado con
   params inventados solo produce una 302 a estado de error: la orden
   únicamente transiciona con un commit real de Webpay.
4. **El commit se llama SOLO en la rama `token_ws`-solo** (flujo normal,
   aprobado o rechazado por la tarjeta): los flujos anulado, timeout y
   error de formulario no commitean — marcan la orden localmente y
   redirigen. La transición de la orden la evalúa el criterio doble de
   PAY-03 junto al descuento de stock del
   [ADR-013](013-orden-nace-al-pagar-stock-al-aprobar.md).

## Consecuencias

**Positivas**
- El diseño queda inmune a la ambigüedad GET/POST: ni siquiera las docs
  oficiales aciertan el método por flujo, y el contrato 0.3.0 lo declara
  así (`GET+POST /api/pago/retorno` con `security: []`).
- Una sola ruta de resultado en la SPA (D-42) sirve voucher, anulado,
  timeout y error — el espejo del discriminador del backend.
- El 302 es la primera respuesta no-JSON del contrato: la lección de que
  este endpoint le habla al navegador, no a la SPA.

**Negativas (honestas)**
- **El resultado viaja en la URL**: `estado` y `orden` quedan visibles en
  la barra de direcciones y el historial del navegador — aceptable para
  una tienda sandbox; el detalle sensible exige sesión.
- **El navegador puede repetir el retorno** (el spike observó 7
  repeticiones de un mismo timeout): el backend debe tolerar duplicados —
  la idempotencia OUR-side del ADR-013 lo cubre.
- **El retorno del timeout no está garantizado**: si el tab duerme, la
  redirección puede no llegar nunca (13 min observados sin retorno) — la
  orden huérfana PENDING queda visible y su gestión llega en la fase 4.

## Para conversar en clase

1. ¿Por qué confiar en el método HTTP para discriminar el flujo habría
   roto la tienda el día que Webpay cambiara de ambiente o versión de API?
   ¿Qué quedó como firma estable en su lugar?
2. Un compañero propone `RedirectResponse(url)` sin `status_code` "porque
   igual redirige": ¿qué vería la clienta al volver de un flujo que llegó
   por POST, y por qué exactamente?
3. ¿Por qué el endpoint del retorno NO lleva candado de sesión si todos
   los endpoints de pago y pedidos sí? ¿Qué podría hacer un atacante que
   descubra la URL y le haga POST a mano?
