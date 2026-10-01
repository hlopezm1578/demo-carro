# Guía 17 — La SPA en internet: Vercel, el rewrite que evita el 404 y la URL que se hornea al build

> **Qué construirás hoy:** la publicación de tu SPA en Vercel Hobby — con
> el `vercel.json` cuyo rewrite ES el requisito de rutas (DEPL-02), la
> `VITE_API_URL` horneada al build y el círculo del CORS cerrado contra tu
> URL real.
> **Al terminar tendrás:** tu tienda abierta al mundo en
> `https://<tu-proyecto>.vercel.app` — el refresh y los deep-links cargan
> la SPA (jamás el 404 de plataforma) y la tienda hablando con tu API
> pública de la guía 16.
> **Necesitas:** la
> [guia-16](guia-16-despliegue-api.md) completa — tu API pública viva y su
> `CORS_ORIGINS` esperando tu URL de Vercel — y una cuenta de correo —
> nada de tarjetas
> ([ADR-019](../04_arquitectura/adr/019-despliegue-free-tier-vercel-render.md)).

---

## Los términos de hoy (antes de copiar nada)

| Término | Qué es, en una frase |
|---|---|
| **Fallback SPA / rewrite** | La regla del host estático que sirve `index.html` para CUALQUIER ruta — sin ella, el refresh de `/pago/resultado` da 404 (DEPL-02) |
| **Env var horneada (`VITE_*`)** | Las variables de Vite con prefijo `VITE_` se reemplazan estáticamente **al build** — cambiarlas en el dashboard no hace nada hasta el redeploy |
| **Framework Preset** | La plantilla de build que Vercel deduce para tu proyecto — hoy la elegimos TÚ: **Vite**, nunca "Other" |
| **Redeploy** | Volver a construir y publicar: obligatorio después de cambiar cualquier env var de build — el valor viejo sigue horneado hasta que existe un build nuevo |
| **Deep-link** | Una URL compartible a una ruta PROFUNDA (`/productos/1`, `/pago/resultado`) — la prueba de fuego del rewrite |

---

## Paso 1 — `vercel.json` ANTES de importar: el rewrite que no admite segunda oportunidad silenciosa

🧠 **El desarrollador piensa:** *la regla de hoy se escribe antes de tocar
Vercel, y la razón es una limitación honesta de la plataforma: **Vercel NO
adivina que tu proyecto es una SPA**. Tu router es `BrowserRouter` de
react-router v8 — TODAS tus rutas (`/carro`, `/pago/resultado`,
`/admin/pedidos`…) viven solo en el cliente: cuando el navegador pide
`/pago/resultado` al servidor, ahí NO hay un archivo con ese nombre — hay
un único `index.html` que la SPA lee de la barra de direcciones. Sin una
regla que lo diga, Vercel busca el archivo, no lo encuentra y responde su
propio 404. El rewrite es esa regla: "cualquier ruta que no matchee un
archivo, entrégala como `index.html`". Y el detalle que tumba deploys
reales: **si el `vercel.json` no está commiteado, el rewrite silenciosamente
no aplica** — Vercel construye desde GitHub, no desde tu disco; un archivo
local que no viajó en el push, para Vercel no existe
([vercel.com/kb/guide/why-is-my-deployed-project-giving-404](https://vercel.com/kb/guide/why-is-my-deployed-project-giving-404),
a la fecha). Por eso este paso va PRIMERO: el archivo nace commiteado o no
nace.*

Crea **`frontend/vercel.json`** — junto al `package.json` del frontend:

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

Y commitealo YA — este archivo no conoce el estado "borrador":

```
git add frontend/vercel.json
git commit -m "Deploy: rewrite SPA para que el refresh no de 404 (DEPL-02)"
git push
```

✅ **Mini-verificación:** `git log --oneline -1 -- frontend/vercel.json`
muestra el commit — y en el navegador, tu repo de GitHub lista el archivo
en `frontend/`. Si no está en GitHub, no está en Vercel: el rewrite que no
viajó es el rewrite que no existe.

---

## Paso 2 — El import en Vercel: preset Vite, Root `frontend` y la URL que se hornea

Entra a **[vercel.com](https://vercel.com)** y créate una cuenta (puede ser
con GitHub — el plan **Hobby** es gratis y sin tarjeta, para uso personal y
no-comercial
([vercel.com/docs/plans/hobby](https://vercel.com/docs/plans/hobby), a la
fecha); si algún flujo de la plataforma te pidiera verificación extra, esa
pantalla pertenece a tu cuenta, no a la guía). Luego: **Add New... →
Project**, importa el repo del taller y configura:

| Campo | Valor |
|---|---|
| Framework Preset | **Vite** — no lo dejes en "Other" |
| Root Directory | `frontend` |
| Environment Variables | `VITE_API_URL` = `https://<tu-servicio>.onrender.com` — entorno **Production**, **sin** slash final |

Presiona **Deploy** y espera el build (Vercel corre el mismo `npm run
build` que tú — con `tsc -b` incluido).

🧠 **El desarrollador piensa:** *dos decisiones en esta tabla y las dos
tienen trampa conocida. **El preset "Other"** es la trampa silenciosa del
Pitfall 7: con Other, Vercel no aplica las convenciones de Vite y el
proyecto queda un huérfano de configuración — el rewrite deja de ser la
única pieza que puede fallar. **La env var es la trampa doble del Pitfall
3.** Primera cara: `VITE_API_URL` no "se lee en runtime" — Vite la
reemplaza estáticamente al construir el bundle ("statically replaced at
build time", [vite.dev/guide/env-and-mode](https://vite.dev/guide/env-and-mode),
a la fecha): cambiarla en el dashboard SIN redeploy no hace NADA, porque
el valor ya está horneado dentro de los `.js` que se sirven. Segunda cara:
el slash final. Tu `api.ts` hace la concatenación exacta que la
`guia-04-catalogo.md` construyó:*

```ts
const base = import.meta.env.VITE_API_URL ?? "";

export async function apiGet<T>(ruta: string): Promise<T> {
  const res = await fetch(`${base}/${ruta}`);
```

*Con slash final, `${base}/${ruta}` produce
`https://<tu-servicio>.onrender.com//api/productos` — el doble slash que
muere en silencio. Sin slash, la URL pública calza exacta. Y nota la
promesa cobrada: la `guia-02-proyecto-frontend.md` dejó escrita esta
variable el día que nació `api.ts` — "`VITE_API_URL` es una variable de
entorno de Vite: vacía (o ausente) en desarrollo — el proxy hace el
trabajo — y la URL pública de la API en producción (fase de despliegue)".
Hoy es esa fase: en dev el valor era `""` y el proxy de Vite hacía el
trabajo; en producción el valor es TU URL pública de Render, horneada al
build.*

✅ **Mini-verificación:** el deploy queda en verde y Vercel te entrega tu
URL: `https://<tu-proyecto>.vercel.app` — anótala literal (sin slash
final), la necesitas en el paso siguiente. Si abres la tienda ahora, la
portada carga… pero los productos no llegan: falta la mitad del círculo.

---

## Paso 3 — Cerrar el círculo del CORS: tu URL real en el dashboard de Render

🧠 **El desarrollador piensa:** *vuelve al dashboard de Render — esta guía
no termina sin cerrar el círculo que la guía 16 dejó a medias. En
**Environment**, edita `CORS_ORIGINS` y deja el JSON array apuntando a tu
URL REAL de Vercel (la que acabas de anotar): guarda, y si el servicio no
re-deploya solo, **Manual Deploy → Deploy latest commit**. Lo que estás
cerrando no es "un permiso de CORS": es una CADENA. La
`guia-09-ordenes-webpay.md` lo dejó construido byte a byte — el backend no
redirige "a la SPA" en abstracto, redirige al PRIMER origen de la lista:*

```python
url = f"{settings.cors_origins[0]}/pago/resultado?{urlencode(params)}"
return RedirectResponse(url, status_code=302)  # 302 EXPLÍCITO — jamás el 307 default
```

*`CORS_ORIGINS` hace dos trabajos con un solo valor: es la lista que el
middleware de CORS acepta (la regla de la serie: lista explícita, jamás
comodín) **y** es el destino del 302 del retorno de Webpay. Apuntarlo a
`localhost` habría roto las DOS cosas a la vez. Y hay un regalo escondido
en esa decisión: como el 302 vuelve al MISMO origen público de la SPA, tu
`localStorage` — el carro y el token de sesión — cruza el full-page load
del retorno exactamente igual que en dev (CART-02/D-27): la clienta vuelve
de Webpay con su carro y su sesión intactos, sin que hayas tocado una
línea.*

✅ **Mini-verificación:** con la tienda abierta en tu URL de Vercel, mira
la pestaña **Network** de DevTools: los `fetch` a `/api/productos` salen a
`https://<tu-servicio>.onrender.com/api/productos` y responden `200` — el
catálogo de la portada y del listado carga con precios y fotos. La SPA
pública habla con tu API pública: DEPL-01 cerrado de punta a punta.

---

## Paso 4 — La mini-verificación que ES el DEPL-02: refresh y deep-links, jamás 404

🧠 **El desarrollador piensa:** *este es el momento que justifica todo el
paso 1 — y conviene entenderlo como lo que es: el host estático haciendo,
por configuración, lo que ningún middleware del backend podría. Navega tu
tienda desde `/`: portada, catálogo, ficha, carro… TODO funciona. Ahora el
golpe: **F5** en `/carro`. Y luego pega direcciones DIRECTO en la barra:
`/pago/resultado`, `/admin/pedidos`, `/productos/1`. Cada una de esas
cargas es un pedido completo al servidor de Vercel por una ruta que "no
existe" como archivo — y el rewrite responde `index.html` con `200` en
todas. El síntoma docente del rewrite faltante es inconfundible: la tienda
funciona navegando desde `/` pero MUERE al refresh — porque la navegación
interna nunca toca al servidor (la SPA decide) y el refresh sí. Y la
cadena crítica que sostiene: el retorno de Webpay ES un full-page load a
`/pago/resultado` — cuando tu clienta vuelva del formulario bancario, no
habrá navegación interna que la salve: sin rewrite, TODO el flujo de pago
muere en producción con un 404 de plataforma. El rewrite ES el DEPL-02.*

Con tu tienda abierta en `https://<tu-proyecto>.vercel.app`:

✅ **Mini-verificación (el refresh):** navega a **/carro** con la tienda
viva y presiona **F5**: la página recarga y el carro vuelve a renderizar
(con lo que tenía tu `localStorage`) — `200`, jamás 404. Prueba lo mismo
en `/pedidos` (con tu sesión de clienta) y en `/admin/pedidos` (con la de
admin): el refresh respeta rutas, guard y sesión igual que en dev.

✅ **Mini-verificación (los deep-links):** pega DIRECTO en la barra de
direcciones y entra frío a cada una — `/productos/1` (la ficha del primer
aroma carga), `/pago/resultado` (la pantalla de resultado con su degradado
honesto de "sin orden que mostrar") y `/admin/pedidos` (te recibe el login
con `returnTo`, como manda el guard). Las tres: la SPA, jamás el 404 de
Vercel.

---

## Paso 5 — El grep del build, ahora contra producción: URL presente, key ausente

🧠 **El desarrollador piensa:** *la fila 13 de la guía 15 te dejó un
mecanismo, no un trámite: grep el bundle para saber qué viajó en él. Hoy
el mecanismo se EXTIENDE, porque el bundle de producción ahora lleva algo
nuevo — la URL pública horneada. La verificación tiene dos caras y las dos
importan: el control POSITIVO (la URL de tu API DEBE estar en el bundle —
prueba de que `VITE_API_URL` quedó horneada y el build la usó) y el
NEGATIVO (`GROQ_API_KEY` → CERO coincidencias — la prueba de siempre,
AIAS-03, ahora contra el entorno que el mundo puede ver). Vercel corre el
mismo `npm run build` que tú, con la variable de SU dashboard; reproduce
ese build exacto localmente con la misma variable y Vite hará el mismo
reemplazo estático — el `dist/` regenerado es tu copia del bundle de
producción.*

En `frontend/`, regenera el build de producción con la MISMA variable de
Vercel y grep el `dist/`:

```
# Git Bash
VITE_API_URL=https://<tu-servicio>.onrender.com npm run build
grep -r "onrender.com" dist/          # control POSITIVO: la URL pública, horneada
grep -r "GROQ_API_KEY" dist/          # CERO coincidencias — sin output es el éxito
```

```powershell
# PowerShell
$env:VITE_API_URL="https://<tu-servicio>.onrender.com"; npm run build
Select-String -Path dist\* -Pattern "onrender.com"    # control positivo: SÍ encuentra
Select-String -Path dist\* -Pattern "GROQ_API_KEY"    # cero resultados — el éxito
```

✅ **Mini-verificación:** el primer grep ENCUENTRA la URL pública (la que
pusiste en Vercel — confirma que el reemplazo estático funcionó) y el
segundo no encuentra NADA. La live-confirmation en el sitio deployado ya
la tienes del paso 3: Network mostrando cada llamada a
`https://<tu-servicio>.onrender.com/api/...` — jamás `localhost`, jamás
`//api`.

---

## Lo heredado viaja tal cual (cero UI nueva)

Nada de lo que la tienda MUESTRA cambió hoy — el deploy es configuración,
no código. Lo que sí conviene nombrar para reconocerlo en producción:

- **El 401 de sesión expirada redirige igual** (D-22): el interceptor que
  la guía 6 construyó manda a `/login?expirada=1` con `returnTo` — sobre
  la URL pública funciona idéntico: la sesión vence a los 7 días, el
  login te recibe con la explicación y te devuelve a donde ibas.
- **La familia de errores heredada sigue siendo el estado visible**: si la
  API duerme (cold start de Render, guía 16), la tienda muestra el
  *"No pudimos conectar con el servidor…"* de siempre con su
  **Reintentar** — que es accidentalmente la UX correcta: cada reintento
  ayuda a despertar el servicio.
- **Los síntomas de entorno roto** se leen en la pestaña Network: la SPA
  pidiendo a `localhost:8000` o apareciendo `//api` en las URLs =
  `VITE_API_URL` mal horneada (mal escrita o cambiada sin redeploy). El
  diagnóstico de la tabla de errores de abajo los resuelve.

---

## ❌ El error que este archivo evita

**1. El rewrite que "está" pero no viajó.**

```text
❌ frontend/vercel.json creado en el disco… y nunca commiteado/pusheado
   → para Vercel no existe: el deploy sale verde y el refresh de
   /pago/resultado muere en 404 — silenciosamente

✅ git add frontend/vercel.json && git commit && git push
   → el rewrite commiteado ANTES del import: la regla aplica desde el
   primer deploy
```

Vercel construye desde GitHub, no desde tu disco. La mini-verificación del
paso 1 existe porque este error no da ninguna señal hasta que una clienta
hace F5.

**2. `VITE_API_URL` con slash final.**

```text
❌ VITE_API_URL=https://<tu-servicio>.onrender.com/
   → ${base}/${ruta} produce //api/productos — el doble slash que muere
   en silencio

✅ VITE_API_URL=https://<tu-servicio>.onrender.com
   → la concatenación de guia-04 calza exacta: URL pública + /api/...
```

Una barra de más en un dashboard puede tumbar una tienda: la
concatenación `${base}/${ruta}` no perdona el regalo doble.

**3. El Framework Preset dejado en "Other".**

```text
❌ Framework Preset: Other
   → Vercel no aplica las convenciones de Vite: build y rutas quedan a
   tu suerte — otra pieza que puede fallar en silencio

✅ Framework Preset: Vite
   → la plantilla oficial del andamio que la guía 2 usó: build detectado,
   convenciones aplicadas
```

---

## 🔧 Errores típicos del deploy (diagnóstico rápido)

| Síntoma | Causa | Remedio |
|---|---|---|
| Navegar desde `/` funciona, pero el refresh o un link directo a `/pago/resultado` da 404 | El `vercel.json` con el rewrite no está commiteado (o el Framework Preset quedó "Other"): el rewrite silenciosamente no aplica | Commitear `frontend/vercel.json`, pushear y redeployar; preset **Vite** — el refresh de una ruta profunda ES la mini-verificación (Paso 1 y 4) |
| La SPA carga pero los productos nunca llegan; Network muestra error de CORS en cada `/api/...` | `CORS_ORIGINS` de Render sigue apuntando a `localhost` (o no incluye tu URL real de Vercel) | Paso 3: el JSON array con la URL real de Vercel — y recuerda: ese valor también decide a dónde vuelve el 302 de Webpay |
| Network muestra pedidos a `https://localhost:8000` o URLs con `//api` | `VITE_API_URL` sin setear en Vercel, escrita con slash final, o cambiada sin redeploy | Entorno **Production**, valor **sin** slash final — y redeploy después de cada cambio: el valor se hornea al build |
| Cambiaste `VITE_API_URL` en el dashboard y la SPA siguió pidiendo a la URL vieja | La env var se reemplaza estáticamente AL BUILD: sin un build nuevo, el valor horneado en los `.js` servidos es el viejo | Redeployar — y el control positivo del Paso 5 (grep de la URL en el `dist/`) para comprobar el reemplazo |

---

## ✅ Verificación de la guía 17

Con el deploy en verde en Vercel y la URL anotada:

1. `frontend/vercel.json` commiteado y visible en GitHub — con el rewrite
   `/(.*)` → `/index.html` (Paso 1).
2. La tienda carga en `https://<tu-proyecto>.vercel.app` y el catálogo
   llega: Network mostrando cada llamada a tu API pública de Render, `200`
   (Paso 3).
3. `CORS_ORIGINS` de Render apunta a tu URL real de Vercel — el círculo
   cerrado (Paso 3).
4. **F5** en `/carro` y deep-links fríos a `/productos/1`,
   `/pago/resultado` y `/admin/pedidos`: la SPA con `200`, jamás el 404
   de plataforma (Paso 4 — el DEPL-02).
5. El grep del build extendido: control positivo (URL pública presente en
   `dist/`) y negativo (`GROQ_API_KEY` → cero) (Paso 5).

## 📝 Punto de control (respóndelas sin mirar la guía)

1. Tu SPA funciona navegando desde `/` pero tu companera no puede abrir el
   link directo a `/productos/1` que le enviaste: ¿qué archivo falta, dónde
   debe vivir, en qué estado (commiteado o no) — y por qué la navegación
   interna nunca delató el problema? (DEPL-02,
   [ADR-019](../04_arquitectura/adr/019-despliegue-free-tier-vercel-render.md),
   Pitfall 7.)
2. Cambiaste `VITE_API_URL` en el dashboard de Vercel y guardaste — pero
   la tienda siguió pidiendo a la URL vieja: ¿qué significa que la variable
   se "hornea al build", y qué tuvo que pasar después de guardar para que
   el cambio exista? ¿Y qué habría pasado con un slash final de más?
   (Pitfall 3.)
3. Tu clienta vuelve del formulario de Webpay y aterriza en
   `/pago/resultado` de tu URL pública: enumera la cadena completa que la
   trajo hasta ahí — ¿quién eligió esa URL, desde qué variable la leyó el
   backend, y por qué su carro y su sesión sobrevivieron el viaje?
   (`guia-09`, ADR-012, `CORS_ORIGINS`.)

## Lo que acabas de aprender

- El `vercel.json` con el rewrite `/(.*)` → `/index.html` commiteado
  ANTES del import: Vercel no adivina que tu proyecto es SPA — el rewrite
  es configuración del host y ES el DEPL-02
- `VITE_API_URL` horneada al build (reemplazo estático de Vite): scope
  Production, SIN slash final (la concatenación `${base}/${ruta}` de la
  guia-04 no perdona el doble slash) — y todo cambio exige redeploy
- El círculo cerrado del CORS: `CORS_ORIGINS` apuntando a tu URL real de
  Vercel — un solo valor, dos trabajos (el origen aceptado Y el destino
  del 302 del retorno: `cors_origins[0]`)
- La mini-verificación DEPL-02 como hábito: refresh y deep-links de rutas
  profundas (`/carro`, `/pago/resultado`, `/admin/pedidos`,
  `/productos/1`) contra la URL pública — el retorno de Webpay ES un
  full-page load, y sin rewrite todo el flujo de pago muere en producción
- El grep del build extendido a producción: control positivo (la URL
  pública horneada en el bundle) y negativo (`GROQ_API_KEY` → cero,
  AIAS-03) — el mismo mecanismo de la guía 15, ahora contra el entorno
  público
- Lo heredado viaja tal cual (cero UI nueva): el 401 con `returnTo` (D-22),
  la familia de errores con su Reintentar (la UX accidentalmente correcta
  del cold start) y los síntomas de entorno roto leídos en Network

**Siguiente:** `guia-18-despliegue-cierre.md` — los 4 flujos de Webpay
contra TU tienda en producción y la Gran verificación final de la serie.
