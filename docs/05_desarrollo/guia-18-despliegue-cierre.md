# Guía 18 — El gran final: los 4 flujos en producción y la Gran verificación final de la serie

> **Qué construirás hoy:** nada de código nuevo — la verificación de lo
> que construiste durante 17 guías, ahora contra TU tienda pública: los
> 4 flujos de retorno de Webpay ejercitados en tu ambiente desplegado, el
> ciclo efímero observado en el propio dato… y la **Gran verificación
> final** que cierra la fase 5 y la serie completa.
> **Al terminar tendrás:** la aplicación verificada de extremo a extremo
> en el ambiente desplegado — y el ciclo cerrado: las 18 guías y los 20
> ADRs cuentan, de punta a punta, el ciclo de vida completo.
> **Necesitas:** las guías 1 a 17 — tus dos tiers desplegados con sus
> mini-verificaciones en verde: la
> [guia-16](guia-16-despliegue-api.md) con `/api/salud` y `/docs`
> respondiendo en tu URL pública de Render, y la
> [guia-17](guia-17-despliegue-frontend.md) con el refresh sin 404 y el
> círculo del CORS cerrado en Vercel. Y a mano: la sesión de la clienta
> y la tarjeta VISA `4051 8856 0044 6623` de la guía 10.

---

## Los términos de hoy (antes de copiar nada)

| Término | Qué es, en una frase |
|---|---|
| **Ambiente desplegado** | Tu tienda de verdad en internet: la SPA en Vercel + la API en Render, cada una con su URL pública HTTPS ([ADR-019](../04_arquitectura/adr/019-despliegue-free-tier-vercel-render.md)) |
| **Flujo de retorno** | Cada una de las 4 vueltas oficiales de Webpay al `return_url`: normal (`token_ws`), anulado, timeout y error de formulario — discriminadas por PRESENCIA de params ([ADR-012](../04_arquitectura/adr/012-retorno-de-webpay.md)) |
| **Cadena congelada** | El recorrido completo de ida y vuelta — `return_url` público → Webpay → retorno GET o POST → 302 → ruta profunda de la SPA pública — fijado por las env vars de las guías 16/17 sin editar una línea |
| **Ciclo efímero** | La vida del disco de Render en dos capas: lo del BUILD siempre revive (el seed), lo de RUNTIME se pierde — una sola lección (D-70, [ADR-020](../04_arquitectura/adr/020-persistencia-efimera-seed-idempotente.md)) |
| **Idempotencia** | Que repetir una operación deje el mismo estado: el commit de Webpay la tiene — y tu backend la exige OUR-side con su guard de estado, porque el navegador puede repetir el retorno (guía 9, PAY-03) |

---

## Paso 1 — La cadena congelada, en una sola mirada

🧠 **El desarrollador piensa:** *hoy no se escribe código — y eso no es
una casualidad del final: es la tesis del deploy. Todo lo que vas a
ejercitar ya está construido desde la fase 3 y congelado desde las guías
16 y 17; lo único nuevo es la URL en la barra de direcciones. Recorre la
cadena completa con los ojos de quien la firma: **(1)** tu clienta —en
la SPA pública de Vercel— llena el carro y presiona "Pagar con Webpay";
el checkout sale por `lib/api.ts` con la `VITE_API_URL` horneada al
build (guía 17). **(2)** Tu backend público —en Render— crea la orden y
le dice a Webpay a dónde devolver al navegador, tal como lo construiste
en la `guia-09-ordenes-webpay.md`:

```python
return_url=f"{settings.backend_url}/api/pago/retorno",
```

*Ese `backend_url` que en dev era `localhost:8000` hoy lee
`BACKEND_URL` del dashboard de Render: la ida de la cadena quedó
congelada a tu URL pública. **(3)** La clienta paga (o no) en el
formulario hosted de Webpay. **(4)** El NAVEGADOR —no tu SPA— vuelve al
`return_url` público, por GET o por POST: tu endpoint está declarado en
los dos métodos y discrimina el flujo por PRESENCIA de params, jamás
por método (ADR-012 — la lección que la fase 3 firmó con evidencia:
ni siquiera las docs oficiales aciertan el método por flujo). **(5)** Si
llegó `token_ws`, el backend commitea contra Webpay; en todos los
casos responde el 302 explícito hacia la SPA — el bloque exacto de la
guía 9, byte a byte:

```python
url = f"{settings.cors_origins[0]}/pago/resultado?{urlencode(params)}"
return RedirectResponse(url, status_code=302)  # 302 EXPLÍCITO — jamás el 307 default
```

*Ese `cors_origins[0]` hoy lee `CORS_ORIGINS` del dashboard: la vuelta
de la cadena apunta a tu Vercel real. **(6)** El navegador hace un
full-page load a esa ruta profunda de la SPA pública — sostenido por el
rewrite del `vercel.json` de la guía 17 (DEPL-02: sin él, TODO el flujo
de pago muere aquí con un 404 de plataforma). **(7)** La SPA hidrata:
fetchea `GET /api/pedidos/{numero}` con el Bearer que sobrevivió el
full-page load en `localStorage`, y pinta el título por el **estado
REAL del pedido fetcheado** — no por el query param del 302 (guía 10).
Siete eslabones, tres env vars, cero líneas nuevas. La cadena está
congelada; lo que sigue es comprobar que sostiene el peso.*

✅ **Mini-verificación (el último eslabón, en frío):** pega en la barra
de direcciones `https://<tu-proyecto>.vercel.app/pago/resultado` — la
SPA responde con su cara honesta de siempre ("No tenemos un resultado
que mostrarte"), no el 404 de Vercel: rewrite + ruta pública + guard de
sesión, todo el eslabón 6 y 7 vivo sin tocar nada.

---

## Paso 2 — El flujo aprobado: la tarjeta de éxito contra tu tienda pública

🧠 **El desarrollador piensa:** *la misma corrida de la guía 10, con un
detalle que cambia todo el significado: el navegador ya no está en tu
máquina. Armas el carro en TU URL de Vercel, viajas al formulario
hosted de Webpay, pagas… y la vuelta recorre internet de vuelta: Webpay
→ tu API de Render (que commitea y decide) → el 302 → tu SPA pública.
El criterio que corre en tu servidor es el de siempre, PAY-03: el
commit del token devuelve `response_code 0` con `status AUTHORIZED`
— tú no lo ves en pantalla, y esa es exactamente la gracia: el estado
lo decide el servidor contra Webpay, no la pantalla contra la URL. Lo
que la clienta ve es la consecuencia: la orden transiciona a `paid`, el
stock se descuenta en el UPDATE condicional (ADR-013) y el voucher de
LA TIENDA —no el de la pasarela— recibe a tu clienta.*

Con la sesión de la clienta iniciada en tu tienda pública:

1. Agrega aromas al carro (anota el total y el stock del aroma que
   elegiste), entra a `/checkout` y presiona **"Pagar con Webpay"**.
2. En el formulario de Webpay paga con la tarjeta de éxito de la fase
   3: **VISA `4051 8856 0044 6623`**, CVV `123`, vencimiento cualquiera
   futuro — y en la autenticación bancaria, RUT `11.111.111-1`
   (**con** puntos) y clave `123`.

✅ **Mini-verificación (el ida y vuelta completo, en producción):**
vuelves del banco directo a `https://<tu-proyecto>.vercel.app/pago/resultado?…`
— mira la barra de direcciones y reconoce el viaje: pasaste por
`webpay3gint.transbank.cl`, tu API de Render te devolvió el 302 y
aterrizaste en TU SPA. En pantalla: **"¡Gracias por tu compra!"** con
el voucher **Pedido `MAURA-00000X` · fecha de hoy · badge Pagado**, las
líneas con su snapshot y el total al peso que anotaste. El badge del
carro del navbar en **0** (el vaciado corrió SOLO al confirmar `paid`,
D-44)… y la ficha del aroma que compraste muestra **una unidad menos**
de stock: el descuento fue real, del otro lado del internet.

---

## Paso 3 — El flujo anulado y el rechazado: el simulador decide que no

🧠 **El desarrollador piensa:** *dos caminos para no aprobar, y conviene
correrlos los dos porque viajan por rutas distintas del discriminador.
**El anulado** es el botón del propio formulario — "Anular compra y
volver": la vuelta trae `TBK_TOKEN` + `TBK_ID_SESION` +
`TBK_ORDEN_COMPRA` sin `token_ws`, tu backend NO commitea (no hay nada
que commitear: la transacción queda `INITIALIZED` en Webpay) y marca la
orden `cancelled`. **El rechazado** es la otra cara del flujo NORMAL:
pagas de verdad, pero en la segunda página del 3DS eliges **Rechazar**
(TSN) en vez de Aceptar — la vuelta trae `token_ws` como el aprobado,
el commit SÍ corre… y Webpay responde `response_code -1` con `FAILED`:
la orden termina `rejected` por el criterio del servidor. Dos flujos,
dos estados, dos badges — y una sola promesa de producto en común: el
carro restituido, porque la restitución de PAY-04 es que NUNCA se
borró (D-44).*

✅ **Mini-verificación (anulado → CANCELLED):** arma un carro, inicia
otro pago y, ya en el formulario de Webpay, presiona **"Anular compra
y volver"**. La SPA pública te recibe con **"Tu compra no se
concretó"** — la causa "Anulaste el pago en el formulario de Webpay",
el aviso "Tu carro sigue intacto" y el badge del navbar con las mismas
unidades: reintenta sin rearmar nada. En tu historial de pedidos, la
orden queda con su badge **Anulado**.

✅ **Mini-verificación (rechazado → REJECTED):** arma otro carro, paga
otra vez con la tarjeta… y en la pantalla del banco cambia el select de
Aceptar a **Rechazar**. Esta vez el commit corrió y respondió `-1`: la
pantalla pública dice **"Tu pago fue rechazado"** con el voucher de la
tienda y su badge **Rechazado** — el pedido `MAURA-…` visible con su
estado real, el carro intacto, y el stock sin descontar (el descuento
solo ocurre al aprobar, ADR-013).

---

## Paso 4 — El flujo timeout: dos relojes y una pestaña que no puede dormir

🧠 **El desarrollador piensa:** *el flujo más lento de la serie, y el
que más honestidad exige — porque en el camino hay DOS relojes
corriendo contra un tercero. **El reloj del token:** vive 5 minutos
desde el create
([transbankdevelopers.cl](https://www.transbankdevelopers.cl/documentacion/webpay-plus),
a la fecha). **El reloj del formulario:** si nadie completa el pago,
el form redirige de vuelta "de 10 minutos en integración" — la fase 3
lo cronometró contra el ambiente real: **603 segundos** con la pestaña
ACTIVA. Y contra esos dos corre **el reloj del tier gratis**: Render
duerme tu API tras ~15 min sin tráfico y la despierta en ~1 min
([render.com/docs/free](https://render.com/docs/free), a la fecha). La
aritmética calza por diseño: el `create` de tu checkout ES tráfico —
resetea la ventana del spin-down — así que el retorno del timeout
(t+10) llega con la API despierta, dentro de la ventana. ¿Y si algo
durmió igual (abandonaste el form, te fuiste a almorzar, el retorno
llega a t+16)? El retorno pega contra un servicio despertando: ~1 min
de latencia extra y listo — el retorno "lento pero funcional" es el
wake del tier gratis, no un bug. Y el matiz que la fase 3 firmó con
cronómetro: si la pestaña DUERME en background, la redirección del
timeout puede no llegar nunca — la orden queda huérfana "en curso"
para siempre. Estado honesto, no falla tuya.*

Inicia un pago más y esta vez **no hagas nada** en el formulario:
déjalo abierto, pestaña visible y activa, y espera (~10 minutos —
sí, TODO ese rato: es parte de la verificación).

✅ **Mini-verificación (timeout con pestaña activa → CANCELLED):** a
los ~10 minutos el formulario se solo-redirige: vuelves a tu SPA
pública con **"Tu compra no se concretó"** — la causa "Se agotó el
tiempo del formulario de pago", el pedido `MAURA-…` "guardado con su
estado real" (badge **Anulado** en tu historial) y el carro intacto
para reintentar. El retorno llegó SIN `token_ws`, tu backend no
commiteó y la orden se canceló localmente: exactamente el cierre que
firmó la fase 3. (¿Se te durmió la pestaña y no volvió nada? También
es el comportamiento firmado: la orden queda "en curso" — el estado
honesto de RN-11, visible para siempre en tu historial.)

---

## Paso 5 — El flujo error de formulario: la clave 3DS errada

🧠 **El desarrollador piensa:** *el cuarto flujo oficial es el más
raro: ocurre cuando el formulario se submitea dos veces y la vuelta
trae los CUATRO params juntos — y las docs de Transbank lo declaran
"replicable solo en producción": en integración, re-ingresar con un
token ya inicializado muere antes, en el `Error 21` del banco. Pero tu
discriminador por presencia de params lo cubre igual — esa es la
inmunidad por diseño de ADR-012: no necesitaste disparar un flujo para
que tu backend sepa qué hacer con él. Lo que SÍ puedes disparar en
integración es su primo hermano, y la fase 3 lo observó 9 veces: **la
clave 3DS errada** produce el `error.cgi` del banco ("Tu transacción
no se pudo llevar a cabo. Ten en cuenta que ningún cargo fue realizado
en tu tarjeta") — la transacción queda `INITIALIZED` en Webpay SIN
commit, y el navegador NO vuelve por esa vía. ¿Y la orden? Quedó
`pending` en tu BD… hasta que el formulario aún abierto se rinde y
redirige al `return_url` con params de TIMEOUT (22-78 s observados):
regreso SIN commit, cara "Se agotó el tiempo", orden cancelada. Un
camino torcido que termina en el mismo lugar honesto.*

Inicia un pago más, ingresa la tarjeta con éxito… y en la
autenticación bancaria escribe la clave **errada** (cualquier cosa que
no sea `123` — o el RUT sin puntos, que deriva al mismo error).

✅ **Mini-verificación (el error del banco, sin commit):** la pantalla
del banco muestra su error — "Tu transacción no se pudo llevar a
cabo… ningún cargo fue realizado en tu tarjeta" — y NO hay vuelta
inmediata: la transacción murió `INITIALIZED` sin commit. Si dejas la
pestaña del error abierta un momento (~1 minuto), el banco termina
redirigiendo al retorno con params de timeout: tu SPA pública recibe
la cara "Se agotó el tiempo" y el pedido queda con su estado real —
badge **Anulado**. Cero cargo, cero commit, carro intacto.

---

## Paso 6 — El ciclo efímero como verificación deliberada: apagar y prender la tienda

🧠 **El desarrollador piensa:** *la última verificación de la serie es
la que en cualquier otro proyecto sería un incidente: vamos a PERDER
datos a propósito. La guía 16 sembró la BD en el build y la 17 cerró
el círculo — hoy observas la decisión de D-70 en tu propio dato, con
las dos capas bien separadas. **Lo que revive siempre:** el catálogo —
nace del seed que corre en cada build (upsert que converge, D-05:
re-ejecutar el deploy es SEGURO por diseño, [ADR-020](../04_arquitectura/adr/020-persistencia-efimera-seed-idempotente.md)).
**Lo que se pierde:** todo lo escrito en runtime — el pedido que
acabas de aprobar, el descuento de stock (el seed restaura el stock
canónico), las cuentas que no sean las del seed. Y hay un tercer
actor que NO participa: el carro de tu clienta vive en su
`localStorage` — en el navegador, no en Render — y sobrevive TODO.
¿Y si el carro tenía un aroma que el ciclo se llevó? Uno CREADO con el
panel durante runtime, que el seed no conoce: la fila degrada igual
que en la fase 2 — **"Este aroma ya no está disponible"** con su
**Quitar**. Mismo mecanismo, otro origen del dato: allá era el soft
delete; hoy, el disco efímero.*

Con tu tienda pública viva y un pedido aprobado fresco en el
historial, fuerza el ciclo — cualquiera de las dos vías:

- **Redeploy:** un `git push` de un cambio menor en TU taller (un
  comentario en el README alcanza) — Render construye de nuevo: build
  nuevo, disco nuevo.
- **Spin-down:** no toques nada por ~15 min y deja que el free tier
  duerma al servicio ([render.com/docs/free](https://render.com/docs/free),
  a la fecha).

✅ **Mini-verificación (las dos capas, en tu propio dato):** despierta
la tienda (ábrela — la primera carga espera el wake de ~1 min, el
cold start de la guía 16) y mira con calma: el **catálogo está** —
doce aromas con fotos y precios, restaurado por el seed del build — y
el **pedido de runtime NO está**: el historial de la clienta muestra
su empty state honesto de siempre ("Todavía no hay pedidos"), la ficha
del aroma que compraste vuelve a su stock canónico, y el login sigue
aceptando las cuentas del seed (ellas nacen en cada build). Nada se
rompió: las dos capas de ADR-020, observadas en el dato y no en la
teoría. Si tu carro aún guardaba un aroma creado en runtime, su fila
aparece degradada — el mecanismo de fase 2 sobrevivió al ciclo.

---

## ❌ El error que este archivo evita

**1. Confiar el resultado al query param del 302.**

```text
❌ "el 302 trae estado=pagado, entonces pagó" — leer la URL y
   renderizar el título según lo que viaja en la query
   → un retorno forjado contra tu URL pública (alguien arma
   /api/pago/retorno?token_ws=inventado) compraría de mentira

✅ fetcheár el estado REAL: GET /api/pedidos/{numero} con el Bearer
   que sobrevivió, y pintar el título por pedido.estado
   → la orden solo transiciona con un commit real de Webpay (PAY-03,
   ADR-012): el query param dice qué flujo vino, el pedido dice qué
   pasó
```

El título de `/pago/resultado` lo decide el estado del pedido
fetcheado — la regla de la guía 10, que hoy protege una URL pública
que el mundo entero puede alcanzar. El endpoint del retorno jamás
confía en el navegador: sin commit, no hay `paid`.

**2. Culpar al deploy cuando es el tier gratis.**

```text
❌ "el retorno de Webpay se demoró un minuto: el deploy está roto"
   → diagnóstico apurado que abre el círculo de configuración que ya
   está cerrado

✅ leer la demora por lo que es: el wake (~1 min tras ~15 sin tráfico,
   render.com/docs/free, a la fecha) — retorno lento pero funcional
   = servicio despertando, no bug
```

El cold start fue nombrado con cifras en la guía 16 y la familia de
errores heredada (con su **Reintentar**) ya es la UX correcta para
despertarlo. Diagnóstico primero, pánico jamás.

**3. "Se perdió la base de datos" — sin distinguir las dos capas.**

```text
❌ "el redeploy borró TODO" — una sola frase para dos mundos
   → y el alumno no entiende por qué el catálogo sigue ahí pero su
   pedido desapareció

✅ las dos capas de ADR-020: build-time SIEMPRE revive (el seed corre
   en cada build) / runtime se pierde (pedidos, stock descontado,
   cuentas nuevas)
```

La distinción no es pedantería: es la estrategia de persistencia
firmada (D-70) — y el historial vacío tras un ciclo es el estado
honesto del free tier, no un incidente.

---

## 🔧 Errores típicos en producción (diagnóstico rápido)

| Síntoma | Causa | Remedio |
|---|---|---|
| El retorno de Webpay demora ~1 min pero funciona (el 302 tarda en llegar) | La API dormía (spin-down ~15 min) y el retorno pegó contra el wake: cold start de Render, cifras de render.com/docs/free a la fecha | Nada: es el tier gratis — cada reintento ayuda a despertar; si duele, la lección es el upgrade path de [ADR-020](../04_arquitectura/adr/020-persistencia-efimera-seed-idempotente.md) |
| Network muestra pedidos a `localhost:8000` o URLs con `//api` | `VITE_API_URL` mal horneada: sin setear en Vercel, con slash final, o cambiada sin redeploy (guía 17, Pitfall 3) | Entorno **Production**, valor **sin** slash final, redeploy — y el control positivo del grep del build en `dist/` |
| El refresh de `/pago/resultado` da 404 (y la tienda "funciona" navegando desde `/`) | El rewrite del `vercel.json` no está commiteado o el preset quedó "Other": el host sirve su 404 para rutas profundas (guía 17, DEPL-02) | Commitear `frontend/vercel.json`, pushear, redeployar — sin rewrite, TODO el flujo de pago muere en producción |

---

## ✅ Verificación de la guía 18

Con tus dos tiers desplegados y la sesión de la clienta iniciada en la
URL pública:

1. Deep-link frío a `/pago/resultado` en tu URL de Vercel: la SPA con
   su cara honesta — el último eslabón de la cadena (rewrite) responde
   (Paso 1).
2. Flujo aprobado con la VISA de la fase 3: voucher de la tienda
   `MAURA-…` con badge Pagado, carro en 0 y stock descontado (Paso 2).
3. Flujo anulado ("Anular compra y volver") → CANCELLED con carro
   intacto; y rechazado (Rechazar/TSN en el banco) → REJECTED con su
   voucher — dos estados, dos badges, un solo mecanismo de restitución
   (Paso 3).
4. Flujo timeout con pestaña activa: a los ~10 min la vuelta sin
   `token_ws`, la orden cancelada y el carro intacto — o, si la pestaña
   durmió, la huérfana "en curso" honesta (Paso 4).
5. Flujo error de formulario con clave 3DS errada: el `error.cgi` del
   banco sin cargo ni commit — y el regreso posterior sin commit
   (Paso 5).
6. El ciclo efímero observado: redeploy o spin-down → despertar →
   catálogo restaurado por el seed, pedido de runtime ausente, y la
   fila degradada del carro si un aroma runtime se perdió (Paso 6).

## 📝 Punto de control (respóndelas sin mirar la guía)

1. Alguien arma a mano la URL `https://<tu-api>.onrender.com/api/pago/retorno?token_ws=falso`
   contra tu tienda pública: ¿qué pieza de la cadena decide que ese
   intento no compra nada — y por qué el título de la pantalla NO puede
   salir del query param del 302? ([ADR-012](../04_arquitectura/adr/012-retorno-de-webpay.md),
   guía 10, PAY-03.)
2. Mañana haces `git push` y tu tienda re-deploya: ¿qué le pasa al
   catálogo, al pedido que aprobaste hoy y al stock que se descontó —
   y por qué esa diferencia es una estrategia firmada y no un bug del
   deploy? (D-70, [ADR-020](../04_arquitectura/adr/020-persistencia-efimera-seed-idempotente.md).)
3. Los relojes del paso 4: el token vive 5 min, el formulario
   redirige a los ~10 min y tu API duerme a los ~15 — ¿por qué el
   retorno del timeout suele llegar con la API despierta, cuándo NO
   llegaría, y qué estado honesto queda en tu historial en ese caso?
   (Pitfall 6, RN-11, cierre de la fase 3.)

## Lo que acabas de aprender

- La cadena congelada de punta a punta: `return_url` público
  (`BACKEND_URL`) → Webpay → retorno GET o POST discriminado por
  presencia de params (ADR-012) → 302 explícito a
  `cors_origins[0]/pago/resultado` → full-page load sostenido por el
  rewrite (DEPL-02) → la SPA pintando por el estado REAL del pedido
  fetcheado — tres env vars, cero líneas nuevas
- Los 4 flujos de Webpay contra el ambiente desplegado con resultado
  esperado por estado: aprobado → `paid` con voucher `MAURA-…` y stock
  descontado; anulado → `cancelled`; rechazado (TSN) → `rejected` por
  el commit `-1` del criterio PAY-03; timeout → cancelado con pestaña
  activa (603 s cronometrados por la fase 3) o huérfano "en curso" si
  la pestaña durmió; error de formulario → `error.cgi` sin commit y
  regreso con params de timeout
- Los dos relojes contra el tercero: token 5 min y form ~10 min
  (transbankdevelopers.cl, a la fecha) corriendo contra el spin-down
  ~15 min / wake ~1 min (render.com/docs/free, a la fecha) — el create
  resetea la ventana, y el retorno lento pero funcional es el wake, no
  un bug
- El ciclo efímero como verificación deliberada: catálogo que revive
  del seed del build, pedido de runtime que no vuelve, stock restaurado
  al canónico — y la fila degradada del carro como el mecanismo de
  fase 2 sobreviviendo con otro origen del dato (D-70/ADR-020)
- La idempotencia en su lugar exacto: el commit de Webpay la tiene, tu
  backend la exige OUR-side, y el navegador puede repetir el retorno —
  el estado solo cambia con un commit real
