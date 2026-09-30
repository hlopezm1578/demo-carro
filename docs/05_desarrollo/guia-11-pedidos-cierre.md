# Guía 11 — El historial de pedidos y el cierre de la fase 3

> **Qué construirás hoy:** el historial de pedidos de la clienta — la página
> `/pedidos` protegida que lista TODAS sus órdenes con su estado real (las
> "en curso" incluidas) y el detalle que reutiliza tu voucher — y la Gran
> verificación final de la fase 3: los cuatro flujos de Webpay de punta a
> punta y el contrato 0.3.0 contra `/docs`.
> **Al terminar tendrás:** la tienda completa del pago: la clienta paga, vuelve
> con su resultado, revisa su historial con su estado honesto — y tú verificas
> la fase entera con la tarjeta de prueba, la carrera de stock y la
> comparación del contrato vivo contra `/docs`.
> **Necesitas:** las guías 1 a 10 completas — el backend del pago de la guía 9
> (con la orden `MAURA-000001` pending en tu base si nunca pagaste su
> retorno), el voucher `VoucherPedido` de la guía 10 y la sesión de la
> clienta del seed. Ambos servidores corriendo y la tarjeta VISA
> `4051 8856 0044 6623` a mano: hoy la Gran verificación final la usa en
> serio.

---

## Los términos de hoy (antes de copiar nada)

| Término | Qué es, en una frase |
|---|---|
| **Historial** | La lista de TODAS las órdenes de la clienta, la más reciente primero — las "en curso" incluidas: la tienda no le oculta nada (RN-11) |
| **Badge de estado** | El tag que dice la verdad del pedido — Pagado, En curso, Rechazado, Anulado — con la misma paleta del voucher (D-45) |
| **Lista → detalle** | El patrón clásico de dos pantallas: una lista escaneable que abre el detalle completo al hacer clic — y acá el detalle ES el voucher (D-46) |
| **Orden huérfana** | La que saltó a Webpay y nunca volvió: queda pending visible como "en curso"; su gestión (anularla, cerrarla) llega con el panel de la fase 4 (D-48/D-49) |
| **Gran verificación final** | La tabla de cierre de fase de las guías 4 y 8 — hoy exige los 4 flujos runtime en el navegador y el contrato 0.3.0 ↔ `/docs` (ADR-007) |

---

## Paso 1 — `features/pedidos/Pedidos.tsx`: la lista con badges honestos

🧠 **El desarrollador piensa:** *la última pantalla de datos de la tienda, y
la más honesta de todas. `GET /api/pedidos` existe desde la guía 9 —
devuelve TODAS las órdenes de la dueña del token, la más reciente primero,
y nada más: el repositorio filtra por `usuario_id` extraído del token
verificado, así que la lista no puede mezclar órdenes ajenas aunque el
cliente quiera (RF-17; lo que la guía 9 construyó, acá solo se consume).
Tres decisiones de esta lista. **Primera: el badge dice el ESTADO de la
orden, no el flujo del retorno.** La orden es una máquina de cuatro
estados (`pending`, `paid`, `cancelled`, `rejected`) y la tabla de badges
es la MISMA del voucher de la guía 10 — mismos textos, mismos colores: una
sola tabla de la verdad para el estado en toda la tienda (D-45). **Segunda:
la fila pending NO se filtra.** Una orden que saltó a Webpay y no volvió
queda PENDING en la base — y el historial la muestra con su badge ámbar
"En curso", porque ocultársela a la clienta sería mentirle sobre su propia
compra (RN-11, D-48). Esa orden huérfana se queda así para siempre en esta
fase: nadie la expira ni la cierra con jobs de fondo — su gestión llega
con el panel de la dueña en la fase 4 (D-49), y el "Siguiente" de esta
guía lo anuncia. **Tercera: los estados async de siempre** — skeleton con
`animate-pulse`, error con la causa del puerto 8000 y Reintentar — más el
empty state honesto: una clienta sin pedidos ve "Todavía no tienes
pedidos" con el camino al catálogo, no una lista vacía que no explica
nada (pantalla 9 del diseño).*

Crea la carpeta **`frontend/src/features/pedidos/`** y
**`frontend/src/features/pedidos/Pedidos.tsx`**:

```tsx
// El historial de pedidos (RF-17): TODAS las órdenes de la clienta con su
// estado real — las "en curso" incluidas (RN-11, D-48). Ruta protegida
// (paso 4); cada fila abre el detalle, que ES el voucher de la guía 10
// (D-46).
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router";

import { apiGet } from "../../lib/api";
import type { EstadoPedido, OrdenLista } from "../../types/api";

const clp = new Intl.NumberFormat("es-CL", {
  style: "currency",
  currency: "CLP",
});

// La MISMA tabla de badges del voucher (guía 10): una sola tabla de la
// verdad para el estado del pedido en toda la tienda (D-45). Si un día
// nace una tercera consumidora, baja a un módulo propio — hoy son dos y
// copiarla una vez más es más honesto que adelantarse.
const BADGES: Record<EstadoPedido, { texto: string; clases: string }> = {
  paid: { texto: "Pagado", clases: "bg-emerald-100 text-emerald-800" },
  pending: { texto: "En curso", clases: "bg-amber-100 text-amber-800" }, // RN-11
  rejected: { texto: "Rechazado", clases: "bg-red-50 text-red-600" },
  cancelled: { texto: "Anulado", clases: "bg-neutral-200 text-neutral-700" },
};

export default function Pedidos() {
  // El Bearer lo adjunta apiGet desde el store; el backend responde SOLO
  // con las órdenes de la dueña del token (guía 9, RF-17).
  const pedidos = useQuery({
    queryKey: ["pedidos"],
    queryFn: () => apiGet<OrdenLista[]>("api/pedidos"),
  });

  if (pedidos.isPending) {
    return (
      <main className="max-w-2xl mx-auto px-4 py-16">
        <h1 className="text-2xl md:text-3xl font-extrabold text-neutral-900">
          Mis pedidos
        </h1>
        <div className="mt-6 bg-white rounded-2xl border border-orange-100 p-6 divide-y divide-orange-100">
          {[0, 1].map((i) => (
            <div
              key={i}
              className="py-4 flex items-center justify-between gap-4"
            >
              <div className="h-4 w-44 animate-pulse bg-neutral-200 rounded-2xl" />
              <div className="h-6 w-24 animate-pulse bg-neutral-200 rounded-2xl" />
            </div>
          ))}
        </div>
      </main>
    );
  }

  if (pedidos.isError) {
    return (
      <main className="max-w-xl mx-auto px-4 py-16 text-center">
        <h1 className="text-xl font-bold text-neutral-900">
          No pudimos cargar tus pedidos
        </h1>
        <p className="mt-2 text-sm text-neutral-600">
          Revisa que el backend esté corriendo en el puerto 8000 e inténtalo
          de nuevo.
        </p>
        <button
          onClick={() => pedidos.refetch()}
          className="mt-6 bg-orange-600 text-white font-bold rounded-full px-6 py-2 min-h-11 hover:bg-orange-700 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
        >
          Reintentar
        </button>
      </main>
    );
  }

  // Empty state honesto: cero órdenes es un estado con su propia pantalla
  // — no una lista vacía sin explicación.
  if (pedidos.data.length === 0) {
    return (
      <main className="max-w-xl mx-auto px-4 py-16 text-center">
        <h1 className="text-2xl md:text-3xl font-extrabold text-neutral-900">
          Todavía no tienes pedidos
        </h1>
        <p className="mt-2 text-base text-neutral-600">
          Cuando hagas tu primera compra, aparece aquí con su estado.
        </p>
        <Link
          to="/productos"
          className="mt-6 inline-flex bg-orange-600 text-white font-bold rounded-full px-6 py-2 min-h-11 hover:bg-orange-700 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
        >
          Ver catálogo
        </Link>
      </main>
    );
  }

  return (
    <main className="max-w-2xl mx-auto px-4 py-16">
      <h1 className="text-2xl md:text-3xl font-extrabold text-neutral-900">
        Mis pedidos
      </h1>
      <ul className="mt-6 bg-white rounded-2xl border border-orange-100 divide-y divide-orange-100">
        {pedidos.data.map((pedido) => {
          const badge = BADGES[pedido.estado] ?? BADGES.pending;
          return (
            <li key={pedido.numero}>
              {/* La fila completa navega al detalle — y la URL lleva el
                  NUMERO legible, jamás el id interno (RN-13, D-37). */}
              <Link
                to={`/pedidos/${pedido.numero}`}
                className="min-h-11 p-4 flex flex-wrap gap-2 items-center justify-between focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
              >
                <div>
                  <p className="text-base font-bold text-neutral-900">
                    {pedido.numero}
                  </p>
                  <p className="mt-1 flex flex-wrap items-center gap-2 text-sm text-neutral-600">
                    {new Date(pedido.fecha).toLocaleDateString("es-CL")}
                    <span className={`rounded-full px-2 py-1 ${badge.clases}`}>
                      {badge.texto}
                    </span>
                  </p>
                </div>
                <span className="flex items-baseline gap-4">
                  <span className="text-lg font-extrabold text-orange-700">
                    {clp.format(pedido.total)}
                  </span>
                  <span className="text-sm text-orange-600 font-bold">
                    Ver detalle →
                  </span>
                </span>
              </Link>
            </li>
          );
        })}
      </ul>
    </main>
  );
}
```

✅ **Mini-verificación:** `npm run build` pasa. La pantalla todavía no tiene
ruta — se cablea protegida en el paso 4. Fíjate en la tabla `BADGES`: es la
del voucher, con el fallback `?? BADGES.pending` para el día que el enum
crezca — la pantalla degrada, jamás explota.

---

## Paso 2 — `features/pedidos/DetallePedido.tsx`: el detalle que ES tu voucher (D-46)

🧠 **El desarrollador piensa:** *la decisión más rentable de la fase se
cobra hoy. Cuando la guía 10 construyó `VoucherPedido` como componente de
presentación pura — RECIBE el pedido, no lo fetchea — estaba sembrando
exactamente esto: el detalle del historial es el MISMO componente, y este
paso solo escribe la pantalla que lo sirve (D-43/D-46: se construye una
vez y el historial lo hereda gratis). Dos decisiones más. **La
importación cruzada con razón:** la regla 6 dice que `features/` no se
importa cruzado *sin razón*, y lo compartido baja a `components/` — la
razón acá es una decisión de producto firmada (D-46): mover `VoucherPedido`
a `components/` re-editaría la guía 10 para cero ganancia funcional, y
duplicar el voucher sería peor (dos verdades del mismo detalle). El import
`../pago/VoucherPedido` es la excepción narrada — la misma forma honesta
de la excepción de la regla 5 con el retorno de Webpay. **Y la URL lleva
el NUMERO:** `/pedidos/MAURA-000001`, jamás `/pedidos/7`. El numero legible
es la llave pública del pedido (RN-13): compartible, pronunciable por
soporte, y respaldada por el 404 uniforme de la guía 9 — un numero que no
existe y un numero que existe pero es de OTRA clienta responden IGUAL: el
detalle ajeno, para ti, no existe (ORDR-01).*

Crea **`frontend/src/features/pedidos/DetallePedido.tsx`**:

```tsx
// El detalle del historial (HU-11): el MISMO VoucherPedido de la guía 10
// (D-43/D-46 — presentación pura: se construyó una vez y el historial lo
// hereda). La URL lleva el NUMERO legible (RN-13); el id interno jamás
// aparece.
import { useQuery } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router";

import { ApiError, apiGet } from "../../lib/api";
import type { OrdenDetalle } from "../../types/api";
import VoucherPedido from "../pago/VoucherPedido"; // regla 6, con razón (D-46)

export default function DetallePedido() {
  const { numero } = useParams(); // "MAURA-000001" — la llave pública (D-37)
  const navegar = useNavigate();

  // El MISMO queryKey del resultado de pago (guía 10): venir del voucher o
  // volver del detalle comparte la caché — cero consultas repetidas.
  const pedido = useQuery({
    queryKey: ["pedido", numero],
    queryFn: () => apiGet<OrdenDetalle>(`api/pedidos/${numero}`),
    enabled: numero !== undefined,
  });

  // El 404 uniforme de la guía 9, con cara de SPA: "no existe" y "no es
  // tuyo" llegan IGUAL — el detalle ajeno no existe para esta pantalla.
  if (
    pedido.isError &&
    pedido.error instanceof ApiError &&
    pedido.error.status === 404
  ) {
    return (
      <main className="max-w-xl mx-auto px-4 py-16 text-center">
        <h1 className="text-xl font-bold text-neutral-900">
          Pedido no encontrado
        </h1>
        <p className="mt-2 text-sm text-neutral-600">
          Puede que el enlace esté viejo.
        </p>
        <Link
          to="/pedidos"
          className="mt-6 inline-flex bg-orange-600 text-white font-bold rounded-full px-6 py-2 min-h-11 hover:bg-orange-700 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
        >
          Volver a Mis pedidos
        </Link>
      </main>
    );
  }

  if (pedido.isPending) {
    return (
      <main className="max-w-2xl mx-auto px-4 py-16">
        <h1 className="text-2xl md:text-3xl font-extrabold text-neutral-900">
          Tu pedido
        </h1>
        <div className="mt-6 bg-white rounded-2xl border border-orange-100 p-6">
          <div className="h-4 w-56 animate-pulse bg-neutral-200 rounded-2xl" />
          <div className="mt-6 h-6 w-2/3 animate-pulse bg-neutral-200 rounded-2xl" />
          <div className="mt-4 h-6 w-1/2 animate-pulse bg-neutral-200 rounded-2xl" />
          <div className="mt-4 h-8 w-32 animate-pulse bg-neutral-200 rounded-2xl" />
        </div>
      </main>
    );
  }

  if (pedido.isError) {
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
          onClick={() => pedido.refetch()}
          className="mt-6 bg-orange-600 text-white font-bold rounded-full px-6 py-2 min-h-11 hover:bg-orange-700 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
        >
          Reintentar
        </button>
      </main>
    );
  }

  return (
    <main className="max-w-2xl mx-auto px-4 py-16">
      <button
        onClick={() => navegar(-1)}
        className="text-sm text-orange-600 min-h-11 flex items-center focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
      >
        ← Volver a Mis pedidos
      </button>
      <h1 className="mt-4 text-2xl md:text-3xl font-extrabold text-neutral-900">
        Tu pedido
      </h1>
      {/* El voucher de la guía 10, tal cual: numero, fecha, líneas con
          snapshot, total y badge — la verdad del pedido en pantalla. */}
      <VoucherPedido pedido={pedido.data} />
    </main>
  );
}
```

✅ **Mini-verificación:** `npm run build` pasa — con el import cruzado
`../pago/VoucherPedido` y CERO cambios en los archivos de la guía 10: el
voucher se escribió una vez y hoy se cobró (D-46). El título de la página
es un honesto "Tu pedido" neutro: la verdad del estado la dice el badge
del voucher, no el título.

---

## Paso 3 — El navbar gana "Mis pedidos" (D-47)

🧠 **El desarrollador piensa:** *el link vive SOLO con sesión — un
historial sin dueña no existe. Es el mismo condicionado por estado de
sesión que la guía 6 instaló para el email y "Cerrar sesión": el navbar ya
sabe quién está y quién no, y el link simplemente se suma al bloque de la
clienta, ANTES del email. ¿Por qué ahí y no junto a "Catálogo"? Porque
"Mis pedidos" es de la sesión, no de la tienda pública: el visitante
anónimo no tiene pedidos que mirar, y mostrarle el link sería prometerle
una pantalla que lo expulsa al login (D-47). El `estiloLink` de siempre lo
hace idéntico a sus vecinos — y el estado activo del `NavLink` marca
naranja la sección donde estás.*

En **`frontend/src/components/Navbar.tsx`**, dentro del bloque con sesión
(`{usuario ? ( ... )}`), agrega el link ANTES del `<span>` del email:

```tsx
              <NavLink to="/pedidos" className={estiloLink}>
                Mis pedidos
              </NavLink>
              <span
                className="text-sm text-neutral-600 truncate max-w-32"
                title={usuario.email}
              >
                {usuario.email}
              </span>
```

✅ **Mini-verificación:** `npm run build` pasa. Con sesión: "Mis pedidos"
aparece entre "Carro" y tu email. Cierra sesión: el link desaparece junto
al email — el navbar anónimo queda exactamente como estaba. (El clic aún
no navega a nada: la ruta llega en el paso siguiente.)

---

## Paso 4 — `main.tsx`: la ruta protegida `/pedidos` (D-32/D-47)

🧠 **El desarrollador piensa:** *herencia pura. El `RequireAuth` con su
`returnTo` genérico existe desde la guía 6 y protege `/checkout` desde la
8 — la ruta del historial se suma DENTRO del mismo bloque y hereda el
comportamiento completo: sin sesión, login con la ubicación a cuestas;
tras entrar, vuelta a donde iba (D-32/D-47). Nadie edita el guard, nadie
edita el login — la promesa de "genérico" se cobra por segunda vez. Y el
contraste que cierra la lección de rutas de la fase: `/pago/resultado`
quedó PÚBLICA (guía 10) porque el 302 llega sin sesión en la URL y la
pantalla tiene algo que mostrar degradada; `/pedidos` es PROTEGIDA porque
esta pantalla NO existe sin clienta — la lista ES de la dueña del token.
Degradar o expulsar no es un gusto: depende de si queda algo honesto que
mostrar sin sesión. El voucher degrada (resultado y numero); el historial
expulsa. La ruta del detalle es `/pedidos/:numero` — el NUMERO viaja en la
URL (D-37), como el paso 2 lo construyó.*

En **`frontend/src/main.tsx`**, agrega los imports junto a los de las
features:

```tsx
import DetallePedido from "./features/pedidos/DetallePedido";
import Pedidos from "./features/pedidos/Pedidos";
```

Y las rutas dentro del bloque `RequireAuth` existente, junto al
`/checkout`:

```tsx
<Route element={<RequireAuth />}>
  <Route path="/checkout" element={<Checkout />} />
  <Route path="/pedidos" element={<Pedidos />} />
  <Route path="/pedidos/:numero" element={<DetallePedido />} />
</Route>
```

✅ **Mini-verificación (el returnTo del historial, en vivo):** cierra la
sesión y abre **http://localhost:5173/pedidos**: no ves la lista — caes al
login. Entra con tu `CLIENTE_EMAIL` de la guía 5… y al terminar vuelves AL
historial con "Mis pedidos" y tus órdenes: el guard guardó el destino, el
login lo leyó (D-32) — igual que la guía 8 hizo con el checkout, sin
tocar una línea del login.

---

## Paso 5 — El historial en vivo: aprobado, anulado y la huérfana (D-48)

🧠 **El desarrollador piensa:** *la pantalla ya está — ahora hay que
llenarla con la verdad. El historial de una clienta real tiene de todo:
compras que aprobaron, pagos que la propia clienta anuló y esa que saltó
a Webpay y nunca volvió — la huérfana PENDING que esta fase deja visible
"en curso" para siempre (D-48/D-49). Si nunca pagaste el retorno de la
orden `MAURA-000001` que la prueba de fuego de la guía 9 dejó en tu base,
ya tienes una huérfana esperando: esta guía la hace visible. Las tres
corridas de abajo construyen el historial completo — y cada vuelta a
`/pedidos` muestra la verdad nueva: la pantalla se monta, el `queryKey`
`["pedidos"]` consulta y la lista refresca sola.*

Con ambos servidores corriendo y la sesión de la clienta iniciada:

✅ **Mini-verificación (aprobado y anulado, juntos en la lista):** arma un
carro, paga APROBADO con la VISA `4051 8856 0044 6623` (CVV `123`,
vencimiento cualquiera futuro, RUT `11.111.111-1` con puntos, clave
`123`). Vuelve a armar otro carro, inicia otro pago y ANULA con el botón
"Anular compra y volver" del formulario. Entra a **"Mis pedidos"**: DOS
filas nuevas — la aprobada con badge **Pagado** y la anulada con badge
**Anulado**, cada una con su numero, su fecha y su total. Clic en la
aprobada ("Ver detalle →"): el MISMO voucher de la vuelta del pago, con
sus líneas congeladas y su total al peso — `/pedidos/MAURA-00000X` en la
barra de direcciones.

✅ **Mini-verificación (la huérfana "en curso", D-48):** inicia un pago más
y, ya en el formulario de Webpay, simplemente CIERRA la pestaña (o déjalo
abierto sin pagar). Esa orden saltó y no volverá: en **/pedidos** aparece
con el badge ámbar **En curso** — y se queda así, porque esta fase no
expira ni cierra órdenes (D-49): la gestión de huérfanas llega con el
panel de la dueña en la fase 4. Esa es la honestidad de RN-11 en pantalla:
la tienda prefiere una verdad incómoda antes que un misterio cómodo.

✅ **Mini-verificación (el detalle ajeno no existe):** en la barra de
direcciones, cambia el numero de la URL por uno inventado
(`/pedidos/MAURA-999999`) y entra: "Pedido no encontrado" — el mismo 404
que respondería si pidieras el numero de OTRA clienta. El detalle ajeno,
para ti, no existe (404 uniforme de la guía 9).

---

## ✅ Gran verificación final de la fase 3

La tabla de cierre del ciclo — como en las fases 1 y 2, cada fila cita su
origen y se marca solo si TÚ la comprobaste. Las credenciales son las de
TU `.env` (las sembró la guía 5) y la tarjeta es la oficial de Transbank
para el ambiente de integración:

| # | Verificación | Origen |
|---|---|---|
| 1 | Recalculo que desconfía: `POST /api/checkout` con un `"precio": 1` inyectado a mano en el payload lo ignora (el schema `CheckoutCreate` no tiene campo precio) y el total sale del catálogo vigente; con stock insuficiente responde 400 y la orden no se crea | RF-12, RN-08, CART-03 |
| 2 | Pago APROBADO con la tarjeta oficial — VISA `4051 8856 0044 6623`, CVV `123`, RUT `11.111.111-1` (con puntos), clave `123` —: voucher de la TIENDA con Pedido `MAURA-00000X`, fecha de hoy, líneas con lo comprado y el total al peso | RF-13, RF-16, HU-09, ADR-014 |
| 3 | El carro se vació SOLO en el aprobado: badge del navbar en 0 y `maura-carro` en `{"items":[]}` — y el stock descontado de la ficha del aroma comprado | RF-16, D-44, RN-12 |
| 4 | Pago ANULADO con el botón "Anular compra y volver" del propio formulario: cara "Tu compra no se concretó" con su causa — y el CARRO INTACTO (mismas unidades en el badge) para reintentar sin rearmar nada | RF-14, RF-16, HU-10, ADR-012 |
| 5 | Timeout: el formulario abandonado con la pestaña ACTIVA devuelve solo a los ~10 minutos (cronometrado en integración: 603 s — el alumno sabe cuánto esperar); la orden queda PENDING visible "en curso" y el carro intacto | RF-14, RN-11, ADR-012 |
| 6 | Cuarto flujo (error de formulario, `token_ws` + `TBK_TOKEN` juntos): explicado como documentado — replicable solo en producción; el discriminador por presencia de params lo cubre sin corrida | RF-14, PAY-02, ADR-012 |
| 7 | F5 sobre el voucher pagado: el MISMO voucher en pie, sin cobrar dos veces — el F5 re-fetcha el pedido (lectura sin efectos); el guard ya-PAID del backend cubre la navegación repetida al `return_url` (back/forward, retries del navegador — el spike observó 7 repeticiones) y el vaciado del carro es idempotente | RF-15, PAY-03, ADR-013 |
| 8 | Carrera de stock (`carrera.py` de la guía 9 con stock=1): dos checkouts concurrentes → dos PENDING (validar no reserva); el commit aprobado en dos threads → exactamente un PAID y un REJECTED, y stock 0 | RF-18, ORDR-02, RN-12, ADR-013 |
| 9 | Historial: "Mis pedidos" del navbar (con sesión) lista TODAS las órdenes con su badge — la PENDING "en curso" incluida, nada se oculta — y el detalle abre el MISMO voucher con numero y total | RF-17, HU-11, RN-11, ADR-014 |
| 10 | `/pedidos` sin sesión → login y vuelta AL historial (returnTo genérico: nadie hardcodeó la ruta) — y el numero ajeno se trata exactamente como el inexistente (404 uniforme) | RF-17, D-32, D-47, RN-13 |
| 11 | El numero legible en todas partes: voucher, historial y URL usan `MAURA-00000X` — el id interno de la base jamás aparece en pantalla ni en la dirección | RN-13, D-37, ADR-014 |
| 12 | **Contrato ↔ `/docs`**: abre `http://localhost:8000/docs` y compara UNO A UNO contra `docs/04_arquitectura/contrato_api.yaml` **0.3.0**: los 11 paths (los 7 de las fases 1-2 más `/api/checkout`, `/api/pago/retorno` GET+POST, `/api/pedidos` y `/api/pedidos/{numero}`), el **302 con su header `Location`** declarado en AMBOS métodos del retorno (el primer response no-JSON del contrato), el endpoint público del retorno (`security` vacío a propósito) y el 404 uniforme de pedidos — y el botón **Authorize** probado con las cuentas del seed: la clienta ejecuta `GET /api/pedidos` → 200 con SUS órdenes; en `GET /api/admin/estado` → 403 "Requiere rol admin" | ADR-007, GUIDE-02, ADR-012 |

La fila 12 es la evidencia formal del cierre — y esta fase suma DOS piezas
a la comparación que las fases 1 y 2 no podían tener: **el 302 del
retorno** (con su `Location`, declarado en ambos métodos — sin la
declaración, `/docs` ni siquiera lo lista y la fila habría cantado un
desvío falso) y **el endpoint público** del retorno conviviendo con los
protegidos: el mismo panel que autoriza a la clienta muestra que
`/api/pago/retorno` no pide credencial a propósito (ADR-012). Con el botón
**Authorize** y las cuentas del seed, la clienta ejecuta su propio
historial desde el panel — 200 con sus órdenes nada más — y rebota con 403
en el endpoint del admin: el rol viaja en el token desde el primer inicio
(guía 5). **Cualquier diferencia entre el panel y el contrato es un
desvío** — o el código corrige, o el contrato se versiona y se aprueba de
nuevo; jamás cambia en silencio. El contrato vive en el repositorio de la
guía; el `/docs` vive en tu máquina — compararlos es tu trabajo de cierre,
y este mismo mecanismo se repite al final de cada fase del proyecto.

**Sugerencia de commit para cerrar la fase** (en TU proyecto):

```
git add -A
git commit -m "Fase 3 completa: pago Webpay y órdenes según guías 9-11

Cumple el contrato OpenAPI 0.3.0 (verificación /docs con Authorize, sin
desvíos) y respeta los 14 ADRs del proyecto."
```

---

## ❌ El error que este archivo evita

**1. Ocultarle a la clienta sus órdenes "en curso".**

```tsx
// ❌ "Si nunca volvió de Webpay, mejor no la mostramos" — la tienda le
// oculta a la clienta su propia compra
pedidos.data.filter((p) => p.estado !== "pending")

// ✅ TODAS las órdenes con su estado real: pending se muestra como
// "En curso" (RN-11) — la gestión de huérfanas es del panel, fase 4
pedidos.data.map((p) => <FilaPedido key={p.numero} pedido={p} />)
```

Una orden PENDING no es un error del sistema: es una compra que se quedó
esperando. Ocultarla convierte un estado honesto en un misterio ("¿dónde
quedó mi pedido?") — y la lección de ORDR-01 es exactamente la contraria:
la verdad, a la vista. Tampoco inventes la expiración: nada de timers ni
jobs de fondo en esta fase (D-49) — eso llega con el panel de la
dueña.

**2. El id interno en la URL del detalle.**

```tsx
// ❌ la clave primaria de la base expuesta en la dirección — enumerable
// y sin sentido para quien la lee
to={`/pedidos/${pedido.id}`}

// ✅ el numero legible: la llave pública del pedido (RN-13)
to={`/pedidos/${pedido.numero}`} // /pedidos/MAURA-000001
```

El numero es lo que la clienta ve en el voucher, lo que viaja a Webpay
como `buy_order` y lo que sirve de referencia a soporte. El id interno es
un detalle de implementación de la base de datos — en la URL sería
enumerable y ajeno (D-37).

**3. Un badge por flujo del retorno, en vez del estado de la orden.**

```tsx
// ❌ el query param del 302 decide el badge: una orden REJECTED por la
// carrera de stock mostraría "Pagado" porque su flujo fue el normal
const texto = estado === "pagado" ? "Pagado" : "Anulado";

// ✅ el badge es el ESTADO del pedido fetcheado — el flujo del retorno
// nombra lo que pasó; el estado dice lo que ES
const badge = BADGES[pedido.estado];
```

El flujo del retorno y el estado de la orden no son lo mismo: el commit
aprobado de una orden que perdió la carrera de stock vuelve con
`estado=pagado` en la URL… y el pedido REJECTED en la base (RN-12). El
voucher de la guía 10 ya lo decidió — el título por el estado REAL, no por
el query param — y el historial hereda la misma regla: el badge jamás
miente.

---

## ✅ Verificación de la guía 11

Con ambos servidores corriendo, el seed corrido y la sesión de la
clienta:

1. **/pedidos** con pedidos: la lista con numero, fecha, total y badge por
   estado — la PENDING "En curso" incluida, nada filtrado (RF-17, RN-11).
2. "Ver detalle" abre el MISMO voucher de la guía 10 — sin editar
   `VoucherPedido.tsx` (D-46) — y la URL es `/pedidos/MAURA-00000X`
   (RN-13).
3. "Mis pedidos" en el navbar SOLO con sesión, entre "Carro" y el email
   (D-47).
4. `/pedidos` sin sesión → login → vuelta al historial tras entrar
   (returnTo, D-32).
5. El numero inventado o ajeno → "Pedido no encontrado" con vuelta a la
   lista (404 uniforme).
6. La tabla de la Gran verificación final, fila por fila — con la 12
   comparando el contrato 0.3.0 contra `/docs`, el 302 del retorno y el
   Authorize probado con las cuentas del seed.

## 📝 Punto de control (respóndelas sin mirar la guía)

1. ¿Por qué el historial NO filtra las órdenes pending — qué le pasaría a
   la clienta si las filtrara, y quién se hace cargo de esas huérfanas en
   la fase 4?
2. El detalle del historial se construyó "gratis": ¿qué propiedad del
   `VoucherPedido` de la guía 10 lo permitió — y qué regla de dependencia
   se cruzó (con qué razón) para importarlo?
3. ¿Por qué la URL del detalle lleva `MAURA-000001` y jamás el id interno
   — y cómo responde el backend cuando pides el numero de OTRA clienta?
4. En la fila 12 de la Gran verificación: ¿qué dos piezas nuevas suma esta
   fase a la comparación contrato ↔ `/docs` — y por qué el 302 tenía que
   estar DECLARADO en el contrato para que la comparación valiera?

## Lo que acabas de aprender

- El historial `/pedidos` con TODAS las órdenes de la clienta y su estado
  real — la PENDING visible como "En curso": la honestidad de estado como
  regla, sin expiración ni jobs de fondo (RF-17, RN-11, D-48/D-49)
- La lista → detalle que reutiliza el voucher tal cual (D-43/D-46):
  presentación pura se construye una vez — y la excepción narrada de la
  regla 6 para importarlo entre features con razón
- El numero legible como llave pública en voucher, historial y URL — el
  id interno jamás (RN-13, D-37) — con el 404 uniforme del backend
  tratando lo ajeno como inexistente
- "Mis pedidos" en el navbar condicionado por sesión (D-47) y la ruta
  protegida con el MISMO `RequireAuth` + `returnTo` de la guía 6 —
  heredado gratis por segunda vez (D-32)
- La Gran verificación final de la fase 3: los 4 flujos runtime con la
  tarjeta oficial (el timeout con su espera cronometrada y el cuarto
  explicado como documentado), la carrera de stock con su PAID/REJECTED,
  el carro vacío SOLO en el aprobado — y el contrato 0.3.0 ↔ `/docs` con
  el 302 y el botón Authorize (ADR-007, ADR-012)

**Siguiente:** fase 4 — el panel de administración y el asistente: la
dueña gestiona productos, stock y pedidos (incluidas las huérfanas PENDING
que esta fase dejó visibles y honestas), y la tienda suma su asesora de
venta con IA sobre el catálogo real. Las cuentas con rol admin desde la
guía 5, el stock atómico de la 9 y los estados honestos de hoy son
exactamente lo que esa etapa necesita.
