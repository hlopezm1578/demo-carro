# Guía 8 — El checkout protegido y el cierre de la fase 2

> **Qué construirás hoy:** el checkout protegido — la pantalla que exige
> sesión y muestra el resumen del pedido listo para pagar — y el cierre de
> la fase 2 con su Gran verificación final: la comparación del contrato
> 0.2.0 contra `/docs`, ahora con el botón Authorize.
> **Al terminar tendrás:** la fase 2 completa y verificada de punta a punta:
> cuentas, sesión, carro y checkout — y la pantalla del pago construida para
> que la etapa 3 solo la encienda.
> **Necesitas:** las guías 1 a 7 completas — las cuentas del seed de la guía
> 5, la sesión con `RequireAuth` y el `returnTo` de la guía 6, y el carro
> hidratado de la guía 7. Ambos servidores corriendo y las credenciales demo
> de TU `.env` a mano: la Gran verificación final las usa.

---

## Los términos de hoy (antes de copiar nada)

| Término | Qué es, en una frase |
|---|---|
| **Ruta protegida** | Una ruta que solo se renderiza con sesión: `RequireAuth` la envuelve y sin token manda al login (guía 6) — hoy estrena su primera clienta |
| **returnTo** | "Volver a donde venía": el guard guarda la ruta destino en el `state` y el login te devuelve a ella — nadie hardcodea destinos (D-32) |
| **`replace`** | Redirigir PISANDO el historial: el redirect no queda como una entrada "atrás" que devolvería a la pantalla imposible |
| **CTA deshabilitado** | Un botón que existe, nombra su futuro y no se puede clickear: la pantalla queda construida para el paso siguiente (D-31) |
| **Gran verificación final** | La tabla de cierre de fase (guía 4): una fila por verificación con su origen citado, y la fila contrato ↔ `/docs` que detecta el drift (ADR-007) |

---

## Paso 1 — `features/checkout/Checkout.tsx`: el resumen de tu pedido

🧠 **El desarrollador piensa:** *¿por qué esta pantalla exige sesión si el
carro no la exigía? Porque el PEDIDO se asociará a una cuenta: cuando la
etapa 3 cree la orden, tendrá que saber de quién es — y esa es la razón que
el subtítulo pone a la vista: **"Comprando como {email}"** convierte la
exigencia en información, no en obstáculo (RF-09, HU-08). La segunda
decisión es qué NO existe: **un resumen sin líneas no es un estado visible**
— con sesión y carro vacío, `Navigate` manda a `/carro` con `replace` (el
redirect no queda en el historial como una entrada "atrás" que te devolvería
a una pantalla imposible: no hay empty state propio del checkout, hay un
redirect al lugar donde se arregla el problema). Y las líneas viajan SIN
stepper: el carro es la sala de edición (D-28); el resumen solo muestra y
totaliza — siempre con precios vigentes hidratados (RN-08), con las mismas
reglas de fila degradada y "Agotado" que la guía 7.*

Crea la carpeta **`frontend/src/features/checkout/`** y
**`frontend/src/features/checkout/Checkout.tsx`**:

```tsx
// El resumen del pedido (RF-09): pantalla protegida por RequireAuth — el
// pedido quedará asociado a la cuenta que nombra el subtítulo. Las líneas
// NO tienen stepper (la sala de edición es /carro) y el CTA de pago nace
// deshabilitado: Webpay llega en la etapa 3 (D-31).
import { useQueries } from "@tanstack/react-query";
import { Link, Navigate, useNavigate } from "react-router";

import { ApiError, apiGet } from "../../lib/api";
import { useAuthStore } from "../../stores/useAuthStore";
import { useCarroStore } from "../../stores/useCarroStore";
import type { ProductoDetalle } from "../../types/api";

const clp = new Intl.NumberFormat("es-CL", {
  style: "currency",
  currency: "CLP",
});

export default function Checkout() {
  const navegar = useNavigate();
  const email = useAuthStore((s) => s.usuario?.email ?? null);
  const items = useCarroStore((s) => s.items);

  // Misma hidratación por ítem que /carro: el MISMO queryKey (con String),
  // la misma caché — llegar al checkout desde el carro no consulta nada
  // nuevo.
  const resultados = useQueries({
    queries: items.map((item) => ({
      queryKey: ["producto", String(item.producto_id)],
      queryFn: () =>
        apiGet<ProductoDetalle>(`api/productos/${item.producto_id}`),
    })),
  });

  // Carro vacío CON sesión: un resumen sin líneas no existe como pantalla
  // — no hay empty state propio del checkout, hay un redirect al carro.
  if (items.length === 0) {
    return <Navigate to="/carro" replace />;
  }

  // Error general (no-404): el backend no responde.
  const falloGeneral = resultados.some(
    (r) => r.isError && !(r.error instanceof ApiError && r.error.status === 404)
  );
  if (falloGeneral) {
    return (
      <main className="max-w-xl mx-auto px-4 py-16 text-center">
        <h1 className="text-xl font-bold text-neutral-900">
          No pudimos cargar tu pedido
        </h1>
        <p className="mt-2 text-sm text-neutral-600">
          Revisa que el backend esté corriendo en el puerto 8000 e inténtalo
          de nuevo.
        </p>
        <button
          onClick={() => resultados.forEach((r) => r.isError && r.refetch())}
          className="mt-6 bg-orange-600 text-white font-bold rounded-full px-6 py-2 min-h-11 hover:bg-orange-700 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
        >
          Reintentar
        </button>
      </main>
    );
  }

  const cargando = resultados.some((r) => r.isPending);

  // El total usa la cantidad tapada (RN-09), igual que en /carro.
  const total = resultados.reduce((suma, r, i) => {
    if (!r.data) return suma;
    const { cantidad } = items[i];
    return suma + Math.min(cantidad, r.data.stock) * r.data.precio;
  }, 0);

  return (
    <main className="max-w-2xl mx-auto px-4 py-16">
      <button
        onClick={() => navegar(-1)}
        className="text-sm text-orange-600 min-h-11 flex items-center focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
      >
        ← Volver al carro
      </button>

      <h1 className="mt-4 text-2xl md:text-3xl font-extrabold text-neutral-900">
        Resumen de tu pedido
      </h1>
      {email && (
        <p className="mt-1 text-sm text-neutral-600">
          Comprando como {email}
        </p>
      )}

      <div className="mt-6 bg-white rounded-2xl border border-orange-100 p-6">
        <ul className="divide-y divide-orange-100">
          {items.map((item, i) => {
            const r = resultados[i];
            if (r.isPending) {
              return (
                <li
                  key={item.producto_id}
                  className="py-4 flex gap-4 items-center"
                >
                  <div className="h-6 w-2/3 animate-pulse bg-neutral-200 rounded-2xl" />
                </li>
              );
            }
            if (
              r.isError &&
              r.error instanceof ApiError &&
              r.error.status === 404
            ) {
              return (
                <li
                  key={item.producto_id}
                  className="py-4 text-sm text-neutral-600"
                >
                  Este aroma ya no está disponible
                </li>
              );
            }
            const producto = r.data;
            if (!producto) return null;
            const { cantidad } = item;
            const enPantalla = Math.min(cantidad, producto.stock); // RN-09
            return (
              <li
                key={item.producto_id}
                className="py-4 flex flex-wrap gap-2 items-center justify-between"
              >
                <div>
                  <Link
                    to={`/productos/${producto.id}`}
                    className="text-xl font-bold text-neutral-900 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
                  >
                    {producto.nombre}
                  </Link>
                  {producto.stock === 0 ? (
                    <span className="ms-2 text-sm rounded-full px-2 py-1 bg-neutral-200 text-neutral-700">
                      Agotado
                    </span>
                  ) : (
                    <span className="ms-2 text-sm text-neutral-600">
                      × {enPantalla}
                    </span>
                  )}
                </div>
                {producto.stock > 0 && (
                  <p className="text-lg font-extrabold text-orange-700">
                    {clp.format(enPantalla * producto.precio)}
                  </p>
                )}
              </li>
            );
          })}
        </ul>

        <div className="mt-2 pt-4 border-t-2 border-orange-100 flex items-baseline justify-between gap-4">
          <span className="text-base font-bold text-neutral-900">Total</span>
          {cargando ? (
            <div className="h-8 w-28 animate-pulse bg-neutral-200 rounded-2xl" />
          ) : (
            <span className="text-2xl font-extrabold text-orange-700">
              {clp.format(total)}
            </span>
          )}
        </div>

        <button
          disabled
          className="mt-6 w-full bg-orange-600 text-white font-bold rounded-full px-6 py-2 min-h-11 disabled:opacity-60 disabled:cursor-not-allowed focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
        >
          Pagar con Webpay
        </button>
        <p className="mt-2 text-sm text-neutral-600">
          El pago llega en la etapa siguiente.
        </p>
      </div>
    </main>
  );
}
```

Tres notas del bloque, antes de que pregunten:

- **La línea del checkout no importa a `FilaCarro`**: regla 6 de las reglas
  de dependencia — features no se importan cruzados. La línea de acá es más
  simple (sin stepper, sin foto), así que vive local: quien la necesite, la
  escribe.
- **La hidratación es literalmente la misma de `/carro`**: mismo `useQueries`
  con el mismo `queryKey` — por eso llegar al checkout desde el carro es
  instantáneo: los productos ya están en caché.
- **El total y las líneas usan la cantidad tapada** (RN-09): el resumen
  muestra lo mismo que el carro mostraría, sin sobreventa en pantalla.

✅ **Mini-verificación:** `npm run build` pasa. La pantalla todavía no tiene
ruta — se cablea protegida en el paso siguiente.

---

## Paso 2 — La ruta protegida en `main.tsx` (AUTH-04)

🧠 **El desarrollador piensa:** *`RequireAuth` nació en la guía 6 esperando
exactamente este momento: una ruta layout de guardia que envuelve a
`/checkout` DENTRO del Layout (Navbar y Footer siguen visibles — es una
página de la tienda). Sin token, `Navigate` manda a `/login` llevando la
ubicación en el `state` — y el login devuelve AL CHECKOUT sin que nadie
hardcodeara esa ruta: el `returnTo` es genérico (D-32), y la fase 4 lo
reutilizará para el panel admin sin tocar una línea. Ahora, la lección
honesta que este paso existe para dejar dicha: **el guard es cortesía de
UX, no seguridad**. Ocultar el botón y proteger la ruta evita que la
clienta sin sesión vea una pantalla rota — pero cualquiera con las devtools
puede falsificar el store y "pasar" el guard. Lo que de verdad protege al
pedido que viene es el **401/403 del backend**: cuando la etapa 3 cree la
orden, el servidor validará el token y el rol, y no se puede falsificar.
Ocultar botones es cortesía; rechazar requests es ley — y esta pantalla
nace sabiendo la diferencia (T-02-13).*

En **`frontend/src/main.tsx`**, agrega los imports junto a los de las
features y componentes:

```tsx
import RequireAuth from "./components/RequireAuth";
import Checkout from "./features/checkout/Checkout";
```

Y la ruta protegida dentro de `<Route element={<Layout />}>`, junto a las
existentes:

```tsx
<Route path="/carro" element={<Carro />} />
<Route element={<RequireAuth />}>
  <Route path="/checkout" element={<Checkout />} />
</Route>
<Route path="*" element={<NoEncontrado />} />
```

✅ **Mini-verificación (AUTH-04 y el returnTo, en vivo):** CIERRA la sesión
(botón "Cerrar sesión" del navbar) y abre
**http://localhost:5173/checkout**: no ves el resumen — caes al **login**.
Entra con tu `CLIENTE_EMAIL` de la guía 5… y al terminar NO vas al inicio:
vuelves **al checkout**, con "Resumen de tu pedido" y "Comprando como" tu
email. Nadie escribió `/checkout` en el login: el guard guardó el destino,
el login lo leyó — el returnTo genérico (D-32) trabajando. Esa es la
verificación de RF-09 y HU-08 de punta a punta.

---

## Paso 3 — El carro vacío y el resumen que calza

🧠 **El desarrollador piensa:** *dos comprobaciones de coherencia que la
pantalla exige. **Con sesión y carro vacío**, `/checkout` no muestra un
esqueleto vacío ni un "no hay nada acá": manda a `/carro` con `replace` —
el único lugar donde el problema se arregla (agregar aromas). ¿Por qué
`replace`? Para que el botón atrás no te devuelva a un checkout sin pedido:
el redirect pisa la entrada del historial en vez de apilar una nueva.
**Y el resumen debe calzar con el carro**: mismo store, misma hidratación,
mismo tapado — si el total de acá difiere del total de `/carro`, algo está
mintiendo, y el mentiroso siempre es el que calcula distinto. Por eso las
dos pantallas comparten literalmente la misma fórmula del mínimo y el mismo
`queryKey`: una sola fuente de verdad para el precio y la cantidad
(RN-08/RN-09).*

El redirect ya vive al tope del componente (paso 1):

```tsx
  // Carro vacío CON sesión: un resumen sin líneas no existe como pantalla
  // — no hay empty state propio del checkout, hay un redirect al carro.
  if (items.length === 0) {
    return <Navigate to="/carro" replace />;
  }
```

✅ **Mini-verificación (el redirect y la cuenta):** con la sesión puesta,
vacía el carro (dos pasos en `/carro`) y abre **/checkout**: terminas en
`/carro` — la dirección cambió sola (`replace`: el atrás no vuelve al
checkout vacío). Vuelve a llenar el carro, entra al checkout y compara:
mismas líneas, mismas cantidades tapadas y el MISMO total que el panel de
`/carro` — al peso (2 × $7.990 + 1 × $10.990 = $26.980 en ambos lados).

---

## Paso 4 — El CTA que nace deshabilitado (D-31)

🧠 **El desarrollador piensa:** *el botón ya dice su futuro: "Pagar con
Webpay" — nombra la pasarela que la etapa 3 integrará, con el estilo CTA
primario de toda la tienda… y deshabilitado, con `opacity` reducida y el
cursor de "no permitido". ¿Por qué mostrar un botón que no funciona? Porque
así la pantalla nace COMPLETA: la fase 3 no rediseñará nada — solo
reemplazará el `disabled` por el flujo real de Webpay (crear la transacción,
redirigir a la pasarela, volver del pago). La nota bajo el botón lo dice
todo: **"El pago llega en la etapa siguiente."** — la clienta (y el alumno)
saben exactamente dónde está el proyecto. Y el link "← Volver al carro"
cierra el circuito con `navigate(-1)`, el mismo volver que preserva el
contexto de la ficha en la guía 4: atrás está el carro de donde viniste.*

El bloque ya vive al final de la card (paso 1):

```tsx
        <button
          disabled
          className="mt-6 w-full bg-orange-600 text-white font-bold rounded-full px-6 py-2 min-h-11 disabled:opacity-60 disabled:cursor-not-allowed focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
        >
          Pagar con Webpay
        </button>
        <p className="mt-2 text-sm text-neutral-600">
          El pago llega en la etapa siguiente.
        </p>
```

✅ **Mini-verificación:** en `/checkout` con ítems: el botón "Pagar con
Webpay" está deshabilitado (el cursor sobre él muestra el de "no
permitido", con la opacidad reducida), la nota "El pago llega en la etapa
siguiente." bajo él, y "← Volver al carro" te regresa al carro — el
circuito carro → checkout → carro completo sin puntos muertos.

---

## ✅ Gran verificación final de la fase 2

La tabla de cierre del ciclo — como en la fase 1, cada fila cita su origen
y se marca solo si TÚ la comprobaste. Las credenciales son las de TU `.env`
(las sembró la guía 5):

| # | Verificación | Origen |
|---|---|---|
| 1 | Registro: cuenta nueva en `/registro` → aviso esmeralda en el login; el email de la clienta seed otra vez → 409 con "Ese email ya tiene cuenta, inicia sesión" | RF-06, RN-06, HU-05 |
| 2 | Login de los dos roles del seed: la clienta y el admin entran; el navbar muestra su email truncado | RF-07, HU-06, D-24 |
| 3 | Token decodificado offline (`options={"verify_signature": False}`): los claims `sub`, `rol`, `exp` e `iat` a la vista — y `exp` menos `iat` son los 7 días | RF-07, D-20, ADR-009 |
| 4 | Sesión viva tras F5 y tras cerrar/abrir la pestaña: el navbar muestra el email desde el primer render, sin parpadeo | RF-07, RNF-06, HU-06 |
| 5 | Interceptor: token corrompido a mano en `maura-auth` + navegar → expulsión a `/login?expirada=1` con "Tu sesión expiró, ingresa de nuevo" | D-22, ADR-009 |
| 6 | `/api/admin/estado` (en `/docs` o por consola): con el token del admin → 200 con los conteos; con el de la clienta → 403 "Requiere rol admin" | RF-08, ADR-011, D-33 |
| 7 | Carro: agregar desde la ficha (merge), editar con el stepper, quitar un aroma y vaciar con la confirmación en dos pasos ("¿Vaciar todo el carro?" → "Sí, vaciar") | RF-10, HU-07 |
| 8 | Carro y badge vivos tras F5 — y tras cerrar y reabrir el navegador: mismas unidades, sin cuenta exigida | RF-11, RNF-06, HU-07 |
| 9 | Tope de stock: la ficha deshabilita "Agregar al carro" con "Ya tienes todo el stock disponible en tu carro." y el stepper del carro deshabilita "+" en el stock vigente | RN-09, D-30, ADR-010 |
| 10 | Checkout sin sesión → `/login` → tras entrar, vuelta AL checkout con el resumen listo (nadie hardcodeó la ruta) | RF-09, D-32, HU-08 |
| 11 | CTA de pago deshabilitado con opacidad reducida, cursor de "no permitido" y su nota "El pago llega en la etapa siguiente." | RF-09, D-31 |
| 12 | **Contrato ↔ `/docs`**: abre `http://localhost:8000/docs` y compara UNO A UNO contra `docs/04_arquitectura/contrato_api.yaml` **0.2.0**: los 7 paths (los 3 de la fase 1 más `/api/auth/registro`, `/api/auth/login`, `/api/auth/perfil` y `/api/admin/estado`), los códigos declarados (201, 401, 403, 409 — además de 200, 404 y 422), los schemas nuevos (`UsuarioPublico`, `Token`, `RegistroCreate`) — y el botón **Authorize** probado con las cuentas del seed: autoriza al admin y ejecuta `GET /api/admin/estado` desde el propio panel → 200 | ADR-007, GUIDE-02 |

La fila 12 es la evidencia formal del cierre — y esta fase suma una pieza
que la fase 1 no podía tener: **el botón Authorize de `/docs`**. El login
form-urlencoded del tutorial OAuth2 (guía 5) existe justamente para esto:
pegas las credenciales del seed una vez y el panel prueba los endpoints
protegidos por ti. **Cualquier diferencia entre el panel y el contrato es un
desvío** — o el código corrige, o el contrato se versiona y se aprueba de
nuevo; jamás cambia en silencio. El contrato vive en el repositorio de la
guía; el `/docs` vive en tu máquina — compararlos es tu trabajo de cierre, y
este mismo mecanismo se repite al final de cada fase del proyecto.

**Sugerencia de commit para cerrar la fase** (en TU proyecto):

```
git add -A
git commit -m "Fase 2 completa: cuentas, sesión y carro según guías 5-8

Cumple el contrato OpenAPI 0.2.0 (verificación /docs con Authorize, sin
desvíos) y respeta los 11 ADRs del proyecto."
```

---

## ❌ El error que este archivo evita

**1. Vender el guard como seguridad.**

```tsx
// ❌ "Ahora el checkout está SEGURO: RequireAuth bloquea el acceso"
// Cualquiera con las devtools puede falsificar el store y pasar el guard.

// ✅ El guard es UX (la clienta sin sesión no ve una pantalla rota); la
// seguridad real es el 401/403 del BACKEND, que no se puede falsificar
```

Ocultar el botón y proteger la ruta es cortesía; rechazar requests es ley.
Si la guía (o tu cliente) empieza a llamar "seguro" a un guard, el panel
admin de la fase 4 nacerá creyéndose protegido por un `if` — y la etapa 3
cobraría órdenes sin que el servidor validara nada.

**2. Hardcodear el retorno en el login.**

```tsx
// ❌ El login "sabe" que venías del checkout — rompe el returnTo genérico
navegar("/checkout", { replace: true });

// ✅ El destino lo trae el state del guard: cualquiera que sea la ruta
// protegida futura (panel admin de la fase 4 incluido), funciona solo
navegar(ubicacion.state?.from?.pathname ?? "/", { replace: true });
```

El `returnTo` de D-32 es genérico justamente para no editar el login cada
vez que la tienda gana una ruta protegida. Hardcodear `/checkout` acá
congela el mecanismo en su primer uso — y la fase 4 lo pagaría.

---

## ✅ Verificación de la guía 8

Con ambos servidores corriendo y el seed hecho:

1. **/checkout sin sesión** → `/login`; tras entrar con la clienta seed →
   vuelta al checkout con "Comprando como {email}" (AUTH-04, D-32).
2. **/checkout con sesión y carro vacío** → redirect a `/carro`, sin entrada
   "atrás" hacia el checkout vacío.
3. **/checkout con ítems**: líneas sin stepper con nombre enlazado, "× N"
   tapada al stock, total de línea y Total — idénticos a `/carro`; fila
   degradada si un aroma ya no existe.
4. CTA "Pagar con Webpay" deshabilitado con su nota y "← Volver al carro"
   funcional (D-31).
5. La tabla de la Gran verificación final, fila por fila — con la 12
   comparando el contrato 0.2.0 contra `/docs` y el Authorize probado con
   las cuentas del seed.

## 📝 Punto de control (respóndelas sin mirar la guía)

1. El guard de `/checkout` es seguridad o UX — y qué protege de verdad la
   pantalla? ¿Cómo vuelve la clienta al checkout tras el login sin que
   nadie hardcodee la ruta, y por qué ese mecanismo sirve también para el
   panel de la fase 4?
2. ¿Por qué el checkout no tiene empty state propio — qué pasa con sesión y
   carro vacío, y para qué sirve el `replace` del redirect?
3. El botón "Pagar con Webpay" nace deshabilitado con su nota: ¿qué falta
   para encenderlo y qué piezas de esta fase ya están listas para la
   etapa 3 (sesión, carro sin precios, total hidratado)?

## Lo que acabas de aprender

- La ruta protegida con `RequireAuth` envolviendo `/checkout` dentro del
  Layout — y el returnTo genérico funcionando en su primera ruta (AUTH-04,
  D-32)
- La lección honesta del guard: cortesía de UX del cliente, ley del
  401/403 del servidor — dicha explícita, no asumida
- El redirect del carro vacío con `replace`: un resumen sin líneas no
  existe como pantalla, y el "atrás" no vuelve a lo imposible
- Las líneas del resumen sin stepper (la sala de edición es el carro) con
  la hidratación compartida por `queryKey`: llegar del carro al checkout no
  consulta nada nuevo
- El CTA deshabilitado como decisión de diseño (D-31): la pantalla del pago
  nace construida — la etapa 3 solo la enciende
- La Gran verificación final de la fase 2, con el botón Authorize de
  `/docs` probando los endpoints protegidos con las cuentas del seed — la
  convención que las fases 3 a 5 replican (GUIDE-02, ADR-007)

**Siguiente:** fase 3 — el pago con Webpay y las órdenes. El checkout que
dejaste construido se enciende: la transacción en el ambiente de integración
de Transbank, la orden que descuenta stock en el backend (la segunda barrera
de CART-03) y el retorno de la pasarela a tu SPA. Las cuentas, la sesión y
el carro sin precios que sembraste en esta fase son exactamente lo que esa
etapa necesita.
