# Guía 10 — La vuelta del pago: el CTA encendido, la ruta pública y el voucher

> **Qué construirás hoy:** la vuelta del pago en la SPA — encender el CTA
> "Pagar con Webpay" con el form POST auto-submit, crear la ruta pública
> `/pago/resultado` que recibe el 302 del backend, y el voucher de la
> tienda con el carro que se limpia solo cuando el pago aprobó.
> **Al terminar tendrás:** un pago real de ida y vuelta en el ambiente de
> integración: tu navegador viaja a Webpay con la tarjeta de prueba, vuelve
> por el retorno del backend y aterriza en un voucher propio con el numero
> legible, las líneas congeladas y el total — y el carro vacío. Y si
> anulas, el carro sigue intacto para reintentar (PAY-04).
> **Necesitas:** las guías 1 a 9 completas — el backend del pago corriendo
> (la prueba de fuego de la guía 9 dejó una orden `MAURA-000001` pending en
> tu base: hoy la vas a mirar desde la SPA), la sesión de la clienta del
> seed y la tarjeta VISA `4051 8856 0044 6623` a mano. Abre
> `docs/04_arquitectura/contrato_api.yaml` 0.3.0 y el ADR-012 en pestañas:
> hoy la SPA le pone cara a lo que el backend discriminó.

---

## Los términos de hoy (antes de copiar nada)

| Término | Qué es, en una frase |
|---|---|
| **Form POST auto-submit** | Un formulario construido con `document.createElement` y submiteado desde JavaScript: la única forma de llevar al navegador a Webpay (una navegación no se puede `fetch`) |
| **token_ws** | El token de la transacción que el backend devuelve en el checkout: viaja como `input` hidden de nombre exacto `token_ws` — el nombre que exige Webpay en el wire |
| **PRG** | Post/Redirect/Get: el backend responde el 302 que fuerza el GET del navegador hacia la SPA — la razón por la que el retorno no revienta en el flujo anulado |
| **Ruta única de resultado** | `/pago/resultado`: UNA dirección para las cuatro vueltas (pagado, rechazado, anulado, timeout/error) — el espejo del discriminador del backend (D-42) |
| **Voucher** | El comprobante de LA TIENDA: numero legible, fecha, líneas con snapshot, total y estado — no el de la pasarela (PAY-04) |
| **Full-page load** | Una carga completa de la página: lo que ocurre al ir a Webpay y al volver — la SPA se despide y regresa, y el token de sesión sobrevivió en `localStorage` |

---

## Paso 1 — `types/api.ts`: los schemas de la etapa, espejados a mano

🧠 **El desarrollador piensa:** *el mismo ejercicio de las guías 2 y 6
(D-09 heredado): abrir `contrato_api.yaml` 0.3.0 y traducir sus schemas
nuevos a TypeScript, campo a campo, SIN generación automática.
`CheckoutRespuesta` son los tres datos que devuelve el checkout —
`url`, `token_ws`, `numero` — y `OrdenDetalle` es lo que el voucher
renderiza: las líneas con `nombre_snapshot` y `precio_snapshot`
congelados (RN-10). El `EstadoPedido` como unión de cuatro strings es
leer el enum del contrato en el idioma del compilador: si alguien escribe
`"PAID"`, el build falla antes de que la pantalla mienta. Y una pregunta
que conviene hacerse HOY, porque la guía 9 la dejó plantada: ¿el retorno
de Webpay pasa por `lib/api.ts`? NO — y esa es la primera excepción de la
regla 5 en todo el proyecto. La regla dice "todo el HTTP del frontend
sale de `lib/api.ts`"… pero el retorno NO es HTTP del frontend: es una
navegación del NAVEGADOR (el 302 del backend lo recibe el browser, no un
`fetch` tuyo). El checkout SÍ es fetch — y por eso sale con `apiPost`
con Bearer, la misma función que la guía 6 creó para el registro: cero
código nuevo en `lib/api.ts`, la regla cumple su promesa en el único
lado donde aplicaba.*

Reemplaza el contenido completo de **`frontend/src/types/api.ts`** por
este — lo nuevo del paso es el bloque de la etapa 3 al final:

```typescript
// Espejo manual de los schemas del contrato_api.yaml (ADR-004, D-09).
// Compara campo a campo: required en YAML = campo sin "?" aquí.
export type Familia = "citricas" | "florales" | "frutales" | "dulces";

export interface ProductoResumen {
  id: number;
  sku: string;
  nombre: string;
  precio: number; // CLP entero (RN-02), sin decimales
  familia: Familia;
  imagen: string; // "/products/citricas-01.jpg" — ruta local (RN-03)
}

export interface ProductoDetalle extends ProductoResumen {
  descripcion: string;
  notas: string[];
  stock: number;
}

// Slug ASCII (lo que viaja) → etiqueta con acento (lo que se muestra)
export const FAMILIA_LABELS: Record<Familia, string> = {
  citricas: "Cítricas",
  florales: "Florales",
  frutales: "Frutales",
  dulces: "Dulces",
};

// Color del badge de familia por pantalla (docs/03_diseno.md §4.1)
export const FAMILIA_BADGES: Record<Familia, string> = {
  citricas: "bg-amber-100 text-amber-800",
  florales: "bg-pink-100 text-pink-800",
  frutales: "bg-rose-100 text-rose-800",
  dulces: "bg-violet-100 text-violet-800",
};

// --- Etapa 2: cuentas (espejo de contrato_api.yaml 0.2.0) ---

export type Rol = "cliente" | "admin";

export interface UsuarioPublico {
  id: number;
  email: string;
  rol: Rol; // viaja como claim en el token desde que se emite (AUTH-03)
}

export interface Token {
  access_token: string;
  token_type: string;
}

// Espejo de RegistroCreate: mínimo 8 SIN composición (RN-05)
export interface RegistroPayload {
  email: string;
  password: string;
}

// --- Etapa 3: pago y pedidos (espejo de contrato_api.yaml 0.3.0) ---

export type EstadoPedido = "pending" | "paid" | "cancelled" | "rejected";

// Espejo de CheckoutRespuesta: los tres datos del form POST (PAY-01)
export interface CheckoutRespuesta {
  url: string;
  token_ws: string; // el nombre EXACTO que exige Webpay en el wire
  numero: string; // "MAURA-000001" — la orden recién nacida en pending (D-34)
}

export interface OrdenLista {
  numero: string;
  fecha: string; // ISO — el formato es asunto del render
  total: number;
  estado: EstadoPedido; // pending se muestra como "en curso" (RN-11)
}

export interface OrdenLinea {
  nombre_snapshot: string; // congelado al comprar (RN-10)
  precio_snapshot: number;
  cantidad: number;
}

export interface OrdenDetalle extends OrdenLista {
  lineas: OrdenLinea[];
}
```

✅ **Mini-verificación (el experimento del compilador):** agrega al final
del archivo esta línea con un estado inventado:

```typescript
const estadoMalo: EstadoPedido = "PAID";
```

`npm run build` **falla** con
`Type '"PAID"' is not assignable to type 'EstadoPedido'` — el compilador
acaba de impedir que un estado en mayúsculas (el gotcha del enum de la
guía 9, su cara frontend) llegue a la pantalla. Borra la línea y el build
vuelve a pasar.

---

## Paso 2 — `Checkout.tsx`: encender el CTA con el form auto-submit

🧠 **El desarrollador piensa:** *el botón que la guía 8 dejó construido
encuentra su motor (D-31 → PAY-01), y el corazón del paso es una
prohibición. **El submit hacia Webpay vive SOLO en el `onSuccess` de la
mutación que dispara el clic — JAMÁS en un `useEffect`.** ¿Por qué tan
rote? Porque React StrictMode monta y desmonta los componentes DOS veces
en desarrollo: un `useEffect` que submitee el form correría dos veces, y
cada submit es una orden PENDING y una transacción real en Webpay — la
clienta pagaría... bueno, en sandbox no paga doble, pero el historial
queda con dos órdenes gemelas y el buy_order duplicado revienta en la
segunda (Pitfall 6). El handler del clic, en cambio, corre UNA vez por
clic de verdad — y el botón `disabled={isPending}` con label en gerundio
cierra la otra puerta: el doble clic no puede iniciar dos pagos. Y ¿por
qué `document.createElement` a mano, sin nada de React? Porque Webpay
exige un **form POST de navegador** hacia su formulario hosted: una
navegación de página completa — y React no tiene herramienta para
"navegar por POST" (sus herramientas navegan por GET, cambiando la
vista). Construir el form con DOM estándar y `submit()` es exactamente
lo que la integración exige: React renderiza tu UI; la despedida hacia
la pasarela es DOM puro. Los values llegan tipados desde
`CheckoutRespuesta` y se asignan con `appendChild` — React escapa por
defecto y aquí no hay HTML crudo de por medio (D-21). ¿Y el carro? NO se
limpia acá: se limpia al llegar al voucher con el pago aprobado (D-44) —
si limpiaras antes de viajar y el pago fallaba, la clienta perdería el
carro sin comprar nada. La entrada de la mutación es `{ items }` tal
cual: el store ya guarda SOLO pares `{producto_id, cantidad}` (D-27) —
el payload del contrato, sin una línea de transformación.*

Reemplaza el contenido completo de
**`frontend/src/features/checkout/Checkout.tsx`** por este — lo nuevo del
paso: `useMutation`/`apiPost` en los imports, la mutación `pagar` después
de leer el store (con el form POST auto-submit en su `onSuccess`), y el
bloque deshabilitado de la guía 8 reemplazado por el CTA encendido con su
aviso de error:

```tsx
// El resumen del pedido (RF-09): pantalla protegida por RequireAuth — el
// pedido queda asociado a la cuenta que nombra el subtítulo. Las líneas
// NO tienen stepper (la sala de edición es /carro) y el CTA "Pagar con
// Webpay" crea la orden y viaja a la pasarela por form POST (D-31).
import { useMutation, useQueries } from "@tanstack/react-query";
import { Link, Navigate, useNavigate } from "react-router";

import { ApiError, apiGet, apiPost } from "../../lib/api";
import { useAuthStore } from "../../stores/useAuthStore";
import { useCarroStore } from "../../stores/useCarroStore";
import type { CheckoutRespuesta, ProductoDetalle } from "../../types/api";

const clp = new Intl.NumberFormat("es-CL", {
  style: "currency",
  currency: "CLP",
});

export default function Checkout() {
  const navegar = useNavigate();
  const email = useAuthStore((s) => s.usuario?.email ?? null);
  const items = useCarroStore((s) => s.items);
  const quitar = useCarroStore((s) => s.quitar);

  // Encender el CTA (D-31 → PAY-01): crear la orden y viajar a Webpay.
  // El submit del form vive SOLO acá — en el onSuccess del clic — JAMÁS
  // en un useEffect (StrictMode monta dos veces en dev: dos órdenes).
  const pagar = useMutation({
    mutationFn: () =>
      apiPost<CheckoutRespuesta>("api/checkout", {
        items, // el carro ya viaja limpio: SOLO ids y cantidades (D-27)
      }),
    onSuccess: (resp) => {
      // Una navegación de página completa, construida a mano: Webpay exige
      // un form POST y una navegación no se puede fetch. DOM estándar con
      // values tipados — sin HTML crudo (React escapa por defecto, D-21).
      const form = document.createElement("form");
      form.method = "POST";
      form.action = resp.url; // la URL del formulario hosted que el backend trajo
      const token = document.createElement("input");
      token.type = "hidden";
      token.name = "token_ws"; // el nombre EXACTO que exige Webpay en el wire
      token.value = resp.token_ws;
      form.appendChild(token);
      document.body.appendChild(form);
      form.submit(); // la SPA se despide: full-page load hacia Webpay
    },
  });

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
                  className="py-4 text-sm text-neutral-600 flex flex-wrap gap-2 items-center justify-between"
                >
                  Este aroma ya no está disponible
                  <button
                    onClick={() => quitar(item.producto_id)}
                    className="text-sm text-red-600 min-h-11 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
                  >
                    Quitar
                  </button>
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

        {pagar.isError && (
          <p className="mt-4 rounded-2xl bg-red-50 text-red-600 p-4 text-sm">
            {pagar.error instanceof ApiError
              ? pagar.error.message // p. ej. "Stock insuficiente en … (quedan 1)"
              : "No pudimos iniciar tu pago. Revisa que el backend esté corriendo en el puerto 8000 e inténtalo de nuevo."}
          </p>
        )}

        <button
          onClick={() => pagar.mutate()}
          disabled={pagar.isPending}
          className="mt-6 w-full bg-orange-600 text-white font-bold rounded-full px-6 py-2 min-h-11 hover:bg-orange-700 disabled:opacity-60 disabled:cursor-not-allowed focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
        >
          {pagar.isPending ? "Pagando…" : "Pagar con Webpay"}
        </button>
      </div>
    </main>
  );
}
```

La nota "El pago llega en la etapa siguiente." desaparece con el bloque:
llegó. Y el error de la mutación tiene DOS caras a propósito: el
`ApiError` trae el `detail` del backend (el 400 de stock con su fila —
la segunda barrera de CART-03 hablándole a la clienta), y cualquier otra
cosa (backend apagado) recibe la familia de causa de siempre.

✅ **Mini-verificación:** `npm run build` pasa. En `/checkout` con ítems,
el botón ya no muestra el cursor de "no permitido": está encendido, dice
"Pagar con Webpay"… y todavía no lo presiones — la ruta donde aterriza
la vuelta todavía no existe. Llega en el paso 3.

---

## Paso 3 — `main.tsx`: la ruta pública `/pago/resultado`

🧠 **El desarrollador piensa:** *la decisión de ruta más contraintuitiva
de la fase, y por eso va con su porqué completo: **`/pago/resultado` es
PÚBLICA — vive FUERA de `RequireAuth`**, exactamente al revés que el
`/checkout` de la guía 8. ¿No era que el pedido era de una cuenta? Lo es
— pero fíjate QUIÉN llega a esta dirección: el navegador recién salido
del formulario de Webpay, empujado por el 302 del backend (ADR-012). Esa
navegación no pasa por tu guard ni carga tu store antes de decidir: si
el token de `localStorage` expiró (7 días, D-20) o la clienta abrió el
link en otro dispositivo, envolver la ruta en `RequireAuth` mandaría el
302 al login… y el voucher nunca se vería (Pitfall 12). La sesión que
SOBREVIVIÓ la vuelta de Webpay es el caso feliz, no el único caso. Por
eso la ruta es pública y la PANTALLA degrada con honestidad cuando no
hay sesión: el resultado y el numero visibles, y un link al login que SÍ
lleva `returnTo` — el mismo mecanismo genérico de D-32, ahora sirviendo
al voucher. (El contraste con la guía 8 es la lección: `RequireAuth` es
cortesía de UX para pantallas que no existen sin sesión; esta pantalla
SÍ existe sin sesión — degradada. Y la ruta protegida `/pedidos` del
historial llega en la guía 11, con su "Mis pedidos" en el navbar.)*

Reemplaza el contenido completo de **`frontend/src/main.tsx`** por este
— lo nuevo del paso: el import de `ResultadoPago` y la ruta pública
`/pago/resultado` junto al `/carro` y FUERA del bloque `RequireAuth`:

```tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import "./index.css";
import Layout from "./components/Layout";
import Landing from "./features/landing/Landing";
import Catalogo from "./features/catalogo/Catalogo";
import FichaProducto from "./features/catalogo/FichaProducto";
import NoEncontrado from "./features/catalogo/NoEncontrado";
import Login from "./features/cuentas/Login";
import Registro from "./features/cuentas/Registro";
import Carro from "./features/carro/Carro";
import RequireAuth from "./components/RequireAuth";
import Checkout from "./features/checkout/Checkout";
import ResultadoPago from "./features/pago/ResultadoPago";

const queryClient = new QueryClient();

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Landing />} />
            <Route path="/productos" element={<Catalogo />} />
            <Route path="/productos/:id" element={<FichaProducto />} />
            <Route path="/login" element={<Login />} />
            <Route path="/registro" element={<Registro />} />
            <Route path="/carro" element={<Carro />} />
            {/* PÚBLICA a propósito: el 302 del retorno llega sin sesión en la URL
                (Pitfall 12) — la pantalla degrada con honestidad, no expulsa. */}
            <Route path="/pago/resultado" element={<ResultadoPago />} />
            <Route element={<RequireAuth />}>
              <Route path="/checkout" element={<Checkout />} />
            </Route>
            <Route path="*" element={<NoEncontrado />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>
);
```

✅ **Mini-verificación (la cara anulado, sin pagar nada):** la pantalla
todavía no existe — la construyen los pasos 4 y 5. Cuando exista, esta
verificación es: cerrar sesión y abrir
**http://localhost:5173/pago/resultado?estado=anulado** — la cara de
compra no aprobada se ve SIN sesión y sin pedido: la ruta es pública de
verdad. (Puedes ir haciéndola al final; el paso 5 la trae de vuelta.)

## Paso 4 — `VoucherPedido.tsx`: el voucher de la tienda (D-43)

🧠 **El desarrollador piensa:** *la recomendación oficial de Webpay es no
mostrar el voucher de la pasarela: "solo debe mostrarse desde el sitio
del comercio" — y el comercio eres tú (PAY-04). El voucher es el
DETALLE COMPLETO del pedido, no un simple "gracias": numero legible,
fecha, las líneas con su snapshot congelado (lo que se pagó, RN-10), el
total y el estado como badge honesto. Por eso vive como componente
PROPIO y no suelto dentro de la pantalla: la guía 11 lo reutiliza tal
cual como detalle del historial — se construye una vez y el historial lo
hereda gratis (D-46). Los badges por estado son tags de datos (no CTAs):
esmeralda para el pagado, ámbar para el "en curso" (pending, RN-11), y
los tonos neutros/rojo para rechazado y anulado — la misma paleta
semántica que la tienda ya usa para disponibilidad y avisos. El formato
del total es el `Intl.NumberFormat` de toda la serie; la fecha, un
`toLocaleDateString("es-CL")`. Cero llamadas a la API acá: el componente
RECIBE el pedido ya fetcheado — presentación pura.*

Crea la carpeta **`frontend/src/features/pago/`** y
**`frontend/src/features/pago/VoucherPedido.tsx`**:

```tsx
// El voucher de la TIENDA (D-43, PAY-04): el detalle completo del pedido
// — numero legible, fecha, líneas congeladas, total y estado como badge.
// Componente presentation pura: RECIBE el pedido, no lo fetchea. La
// guía 11 lo reutiliza como detalle del historial (D-46).
import type { OrdenDetalle } from "../../types/api";

const clp = new Intl.NumberFormat("es-CL", {
  style: "currency",
  currency: "CLP",
});

const BADGES: Record<string, { texto: string; clases: string }> = {
  paid: { texto: "Pagado", clases: "bg-emerald-100 text-emerald-800" },
  pending: { texto: "En curso", clases: "bg-amber-100 text-amber-800" }, // RN-11
  rejected: { texto: "Rechazado", clases: "bg-red-50 text-red-600" },
  cancelled: { texto: "Anulado", clases: "bg-neutral-200 text-neutral-700" },
};

export default function VoucherPedido({ pedido }: { pedido: OrdenDetalle }) {
  const badge = BADGES[pedido.estado] ?? BADGES.pending;
  const fecha = new Date(pedido.fecha).toLocaleDateString("es-CL");
  return (
    <section className="mt-6 bg-white rounded-2xl border border-orange-100 p-6">
      <p className="text-sm text-neutral-600">
        Pedido {pedido.numero} · {fecha} ·{" "}
        <span className={`rounded-full px-2 py-1 text-sm ${badge.clases}`}>
          {badge.texto}
        </span>
      </p>
      <ul className="mt-2 divide-y divide-orange-100">
        {pedido.lineas.map((linea, i) => (
          <li
            key={i}
            className="py-4 flex flex-wrap gap-2 items-center justify-between"
          >
            <div>
              <span className="text-xl font-bold text-neutral-900">
                {linea.nombre_snapshot}
              </span>
              <span className="ms-2 text-sm text-neutral-600">
                × {linea.cantidad}
              </span>
            </div>
            <p className="text-lg font-extrabold text-orange-700">
              {clp.format(linea.precio_snapshot * linea.cantidad)}
            </p>
          </li>
        ))}
      </ul>
      <div className="mt-2 pt-4 border-t-2 border-orange-100 flex items-baseline justify-between gap-4">
        <span className="text-base font-bold text-neutral-900">
          {pedido.estado === "paid" ? "Total pagado" : "Total"}
        </span>
        <span className="text-2xl font-extrabold text-orange-700">
          {clp.format(pedido.total)}
        </span>
      </div>
    </section>
  );
}
```

Fíjate qué NO hay: nada del voucher de Transbank (ni authorization_code
ni los últimos 4 dígitos de la tarjeta — el `card_detail` se queda en el
backend). El comprobante de la compra es el de la tienda, con lo que la
tienda sabe que compraste.

✅ **Mini-verificación:** `npm run build` pasa — el componente compila
todavía sin consumidores (es presentation pura: su consumidor llega en
el paso siguiente).

---

## Paso 5 — `ResultadoPago.tsx`: leer el 302, fetchear el pedido y degradar con honestidad

🧠 **El desarrollador piensa:** *la pantalla que espeja al discriminador
(D-42): el backend ya decidió el flujo y lo puso en la URL
(`?estado=…&orden=…`) — la pantalla LEE lo que le entregaron, no
adivina. Cuatro decisiones de render. **Las caras no aprobadas**
(anulado, timeout, error) no fetchean nada: su mensaje dice cuál fue la
causa y el aviso de que el carro sigue intacto para reintentar — porque
la implementación de la restitución de PAY-04 es que NUNCA se borró
(D-44). **Las caras con orden** (pagado, rechazado) fetchean
`GET /api/pedidos/{numero}` con el Bearer que sobrevivió el full-page
load en `localStorage` (D-21/CART-02 existían exactamente para este
momento) y renderizan el voucher — el badge del voucher es el que dice
la verdad del estado, no el query param. **El degradado sin sesión**
(Pitfall 12): sin token, el resultado y el numero se muestran igual, y
el link "inicia sesión para ver el detalle" lleva `state.from.pathname`
— el `returnTo` genérico de D-32 con un truco honesto: el login de la
guía 6 lee `from.pathname` y se lo pasa a `navigate()`, así que la query
completa (`?estado=…&orden=…`) viaja DENTRO del string y React Router
la parsea al navegar — tras entrar, la clienta vuelve a ESTA pantalla
con su resultado. **Y los estados async uniformes de la serie:**
skeleton con `animate-pulse` mientras llega el pedido, y el error con
su causa del puerto 8000 + Reintentar — ninguna pantalla se diseña solo
para el caso feliz. El `queryKey` del pedido lleva el numero: cuando la
guía 11 liste el historial y abra detalles, la caché ya estará cálida.*

Crea **`frontend/src/features/pago/ResultadoPago.tsx`**:

```tsx
// La vuelta del pago (HU-10): la ruta pública de resultado (D-42) que
// recibe el 302 del backend con el flujo discriminado y el numero de la
// orden. Con sesión fetchea el pedido y renderiza el voucher de la
// TIENDA (D-43); sin sesión, degrada con honestidad (Pitfall 12). El
// carro se vacía SOLO al confirmar el pago aprobado (D-44, paso 6).
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { Link, useSearchParams } from "react-router";

import { apiGet } from "../../lib/api";
import { useAuthStore } from "../../stores/useAuthStore";
import { useCarroStore } from "../../stores/useCarroStore";
import type { OrdenDetalle } from "../../types/api";
import VoucherPedido from "./VoucherPedido";

const ESTILO_CTA =
  "mt-6 inline-flex bg-orange-600 text-white font-bold rounded-full px-6 py-2 min-h-11 hover:bg-orange-700 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none";

// Las caras no aprobadas: el mensaje dice cuál fue la causa (D-45).
const NO_APROBADO: Record<string, string> = {
  anulado: "Anulaste el pago en el formulario de Webpay.",
  timeout: "Se agotó el tiempo del formulario de pago.",
  error: "El formulario de pago falló. Puedes reintentar.",
};

export default function ResultadoPago() {
  const [params] = useSearchParams();
  const estado = params.get("estado");
  const orden = params.get("orden");
  const token = useAuthStore((s) => s.token);
  const vaciar = useCarroStore((s) => s.vaciar);
  const queryClient = useQueryClient();

  // Con numero y sesión: el detalle del pedido — el voucher ES el
  // detalle (D-43). El Bearer lo adjunta apiGet desde el token que
  // sobrevivió el full-page load (D-21).
  const pedido = useQuery({
    queryKey: ["pedido", orden],
    queryFn: () => apiGet<OrdenDetalle>(`api/pedidos/${orden}`),
    enabled: orden !== null && token !== null,
  });

  // El vaciado del carro en UN punto (D-44): SOLO al confirmar el pago
  // aprobado — detalle en el paso 6.
  useEffect(() => {
    if (pedido.data?.estado === "paid") {
      vaciar();
      // Stock fresco en ficha y carro: el descuento del backend invalidó
      // la caché local de productos (el prefijo ["producto"] cubre todos
      // los ["producto", "<id>"] de la hidratación).
      queryClient.invalidateQueries({ queryKey: ["producto"] });
    }
  }, [pedido.data, vaciar, queryClient]);

  // Sin estado en la URL: alguien navegó a mano — honestidad ante todo.
  if (!estado) {
    return (
      <main className="max-w-xl mx-auto px-4 py-16 text-center">
        <h1 className="text-xl font-bold text-neutral-900">
          No tenemos un resultado que mostrarte
        </h1>
        <p className="mt-2 text-sm text-neutral-600">
          Si acabas de pagar, la vuelta llega desde el formulario de Webpay.
        </p>
        <Link to="/productos" className={ESTILO_CTA}>
          Ver catálogo
        </Link>
      </main>
    );
  }

  // Las caras no aprobadas (anulado / timeout / error): mensaje + carro
  // intacto (D-44: la restitución de PAY-04 es que nunca se borró).
  if (estado in NO_APROBADO) {
    return (
      <main className="max-w-xl mx-auto px-4 py-16 text-center">
        <h1 className="text-2xl md:text-3xl font-extrabold text-neutral-900">
          Tu compra no se concretó
        </h1>
        <p className="mt-2 text-sm text-neutral-600">{NO_APROBADO[estado]}</p>
        {orden && (
          <p className="mt-1 text-sm text-neutral-600">
            El pedido {orden} quedó guardado con su estado real.
          </p>
        )}
        <p className="mt-6 rounded-2xl bg-orange-50 p-4 text-sm text-neutral-700">
          Tu carro sigue intacto: reintenta cuando quieras.
        </p>
        <Link to="/carro" className={ESTILO_CTA}>
          Volver al carro
        </Link>
      </main>
    );
  }

  // De aquí en adelante hay orden (pagado o rechazado) — primero, el
  // degradado sin sesión (Pitfall 12): resultado y numero visibles.
  if (token === null) {
    // El returnTo con la query DENTRO del string: el login lee
    // from.pathname y se lo pasa a navigate(), que parsea la query.
    const volverA = `/pago/resultado?estado=${estado}${orden ? `&orden=${orden}` : ""}`;
    return (
      <main className="max-w-xl mx-auto px-4 py-16 text-center">
        <h1 className="text-2xl md:text-3xl font-extrabold text-neutral-900">
          {estado === "pagado" ? "¡Gracias por tu compra!" : "Tu pago fue rechazado"}
        </h1>
        {orden && <p className="mt-2 text-sm text-neutral-600">Pedido {orden}</p>}
        <p className="mt-6 text-sm text-neutral-600">
          {/* El link que SÍ lleva returnTo (D-32): tras entrar, vuelve acá */}
          <Link
            to="/login"
            state={{ from: { pathname: volverA } }}
            className="text-orange-600 font-bold focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
          >
            inicia sesión para ver el detalle
          </Link>
        </p>
      </main>
    );
  }

  if (!orden) {
    // pagado/rechazado sin numero no debería llegar nunca — defensivo.
    return (
      <main className="max-w-xl mx-auto px-4 py-16 text-center">
        <h1 className="text-xl font-bold text-neutral-900">
          No tenemos un resultado que mostrarte
        </h1>
        <Link to="/productos" className={ESTILO_CTA}>
          Ver catálogo
        </Link>
      </main>
    );
  }

  // Estados async uniformes de la serie: skeleton y error con Reintentar.
  if (pedido.isPending) {
    return (
      <main className="max-w-2xl mx-auto px-4 py-16">
        <div className="h-8 w-64 animate-pulse bg-neutral-200 rounded-2xl" />
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
        <button onClick={() => pedido.refetch()} className={ESTILO_CTA}>
          Reintentar
        </button>
      </main>
    );
  }

  // El voucher: el título honesto según el estado REAL del pedido.
  const titulo =
    pedido.data.estado === "paid"
      ? "¡Gracias por tu compra!"
      : pedido.data.estado === "pending"
        ? "Tu pago está en curso"
        : pedido.data.estado === "cancelled"
          ? "Tu compra quedó anulada"
          : "Tu pago fue rechazado";
  return (
    <main className="max-w-2xl mx-auto px-4 py-16">
      <h1 className="text-2xl md:text-3xl font-extrabold text-neutral-900">
        {titulo}
      </h1>
      <VoucherPedido pedido={pedido.data} />
      {pedido.data.estado === "paid" ? (
        <Link to="/productos" className={ESTILO_CTA}>
          Seguir comprando
        </Link>
      ) : (
        <>
          <p className="mt-4 text-sm text-neutral-600">
            Tu carro sigue intacto: reintenta cuando quieras.
          </p>
          <Link to="/carro" className={ESTILO_CTA}>
            Volver al carro
          </Link>
        </>
      )}
    </main>
  );
}
```

✅ **Mini-verificación (la orden pending de la guía 9, con cara de
SPA):** con la sesión de la clienta puesta y ambos servidores corriendo,
abre
**http://localhost:5173/pago/resultado?estado=pagado&orden=MAURA-000001**
— la orden que la prueba de fuego de la guía 9 dejó esperando el retorno.
Debes ver "Tu pago está en curso" con el badge ámbar **En curso**, las
líneas con su snapshot y el total — la honestidad de RN-11 en pantalla.
Y el carro NO se vació (mira el badge del navbar): el vaciado exige un
`paid` real, y esa orden nunca volvió de Webpay. Después cierra sesión y
recarga la misma URL: el degradado — el estado y el numero visibles con
"inicia sesión para ver el detalle". Entra… y vuelves AL resultado, no
al inicio: el `returnTo` funcionó con la query a cuestas.

---

## Paso 6 — El vaciado del carro en UN punto (D-44)

🧠 **El desarrollador piensa:** *el bloque ya vive en el código del paso
5 — este paso existe para mirarlo de cerca, porque es una decisión de
producto disfrazada de `useEffect`. **El carro se limpia en un solo
punto del sistema: cuando el pedido fetcheado llega `paid`.** Ni al
presionar "Pagar con Webpay" (el pago puede fallar), ni al llegar a la
ruta (puede ser un anulado), ni en el checkout: SOLO el voucher con el
pago aprobado. Así, la "restitución" de PAY-04 se implementa de la forma
más simple posible: NO EXISTE — en anulado, timeout y error el carro
sigue intacto porque nunca se borró; la clienta reintenta sin rearmar
nada, sin snapshots de carro ni lógica de restauración. ¿Y por qué un
`useEffect` aquí SÍ está permitido, si el paso 2 lo prohibía para el
submit? Porque el criterio nunca fue "useEffect mal": es **efectos no
idempotentes, mal**. El submit del form crea una orden por corrida —
correrlo dos veces es dos pagos (Pitfall 6). El vaciado es idempotente
por construcción: vaciar un carro vacío lo deja vacío — que StrictMode
dispare el efecto dos veces en dev deja el mismo estado. Y el
`invalidateQueries` del prefijo `["producto"]` va pegado al vaciado
porque el pago aprobado DESCONTÓ stock en el backend: la caché de la
ficha y del carro quedó vieja al instante — la ficha de un aroma agotado
debe saberlo en la próxima visita sin esperar a que expire la caché.*

El bloque (ya copiado en el paso 5, acá está solo):

```tsx
  // El vaciado del carro en UN punto (D-44): SOLO al confirmar el pago
  // aprobado. En anulado/timeout/error no corre — el carro nunca se borró.
  useEffect(() => {
    if (pedido.data?.estado === "paid") {
      vaciar();
      queryClient.invalidateQueries({ queryKey: ["producto"] });
    }
  }, [pedido.data, vaciar, queryClient]);
```

✅ **Mini-verificación:** con la orden pending del paso 5 a la vista,
abre las devtools y mira el `localStorage`: `maura-carro` mantiene sus
items — el efecto no corrió porque `estado` no es `paid`. (El vaciado de
verdad se ve en la primera mini-verificación del paso siguiente: pago
aprobado → badge del carro en 0 y `{"items":[]}` en el localStorage.)

---

## Paso 7 — El pago de verdad: aprobado, anulado y el F5 que no paga doble

🧠 **El desarrollador piensa:** *las tres corridas de la etapa, con la
tarjeta oficial. **Aprobado:** llenar el carro, checkout, "Pagar con
Webpay" — el navegador viaja al formulario hosted, la tarjeta de éxito,
el 3DS con su RUT y clave… y la vuelta: el retorno del backend discrimina
el flujo normal, commitea, aplica el criterio doble, descuenta el stock
y responde el 302 que trae a la SPA al voucher. Es el recorrido COMPLETO
de las guías 9 y 10 en una sola navegación — fíjate en la barra de
direcciones al volver: pasaste por `webpay3gint.transbank.cl`, tu
backend, y aterrizaste en `/pago/resultado?estado=pagado&orden=MAURA-…`
sin que tu SPA hiciera nada de ese camino. **Anulado:** cualquier pago
iniciado, y el botón "Anular compra y volver" del propio formulario —
la vuelta trae los `TBK_*`, el backend marca la orden CANCELLED sin
llamar a la API, y la cara de "Tu compra no se concretó" recibe a la
clienta CON su carro intacto. **Y el F5:** refrescar el voucher NO paga
dos veces — y conviene saber exactamente por qué: el F5 sobre
`/pago/resultado` re-pide la ruta de la SPA y la pantalla re-fetchea `GET
/api/pedidos/{numero}`, una lectura sin efectos; el endpoint
`/api/pago/retorno` NO se ejecuta de nuevo. El guard ya-PAID del backend
entra en escena cuando es la navegación al `return_url` lo que se repite
(back/forward, un retry del navegador en vuelo — el spike observó 7
repeticiones de un mismo retorno): ahí re-muestra sin side effects
(Pitfall 4). Y el vaciado del paso 6 es idempotente. Si quieres ver el
rechazo de tarjeta, en la segunda página del 3DS cambia el select de
Aceptar a Rechazar (TSN): el pago sigue el flujo normal y el commit
devuelve `response_code` -1 — la cara "Tu pago fue rechazado" con su
voucher REJECTED. Y el timeout, si tienes paciencia: ~10 minutos con la
pestaña activa (cronometrado: 603 s) — el retorno del timeout marca la
orden CANCELLED y la cara "Se agotó el tiempo" recibe a la clienta con su
carro intacto; la orden queda "en curso" SOLO si la pestaña durmió en
background y el retorno nunca llegó — el historial de la guía 11 la
mostrará así por siempre (RN-11).*

Con ambos servidores corriendo y la sesión de la clienta iniciada:

✅ **Mini-verificación (APROBADO — el ida y vuelta completo):** agrega
aromas al carro (anota el total), entra a `/checkout` y presiona
**"Pagar con Webpay"**. En el formulario de Webpay paga con la tarjeta
de éxito — **VISA `4051 8856 0044 6623`**, CVV `123`, vencimiento
cualquiera futuro — y en la autenticación bancaria, RUT `11.111.111-1`
(CON puntos) y clave `123`. Al volver debes ver:

1. "¡Gracias por tu compra!" y el voucher de la tienda: **Pedido
   `MAURA-00000X` · fecha de hoy · badge Pagado**, las líneas con los
   nombres y precios que compraste y el **total al peso** que anotaste.
2. El badge del carro del navbar en **0** — y en el `localStorage`,
   `maura-carro` quedó `{"items":[]}`: el vaciado corrió SOLO al
   confirmar `paid` (D-44).
3. El stock descontado de verdad: abre la ficha del aroma que compraste
   — una unidad menos que antes de pagar (la caché se invalidó en el
   mismo instante).

✅ **Mini-verificación (ANULADO — el carro intacto):** vuelve a armar un
carro, inicia otro pago y, ya en el formulario de Webpay (tras ingresar
la tarjeta o sin ingresarla), presiona **"Anular compra y volver"**. La
SPA te recibe con "Tu compra no se concretó" — la causa "Anulaste el
pago en el formulario de Webpay", el aviso "Tu carro sigue intacto" — y
el badge del carro con las mismas unidades de antes: reintenta sin
rearmar nada. Así se implementa la restitución de PAY-04: nunca se
borró.

✅ **Mini-verificación (F5 — no paga dos veces):** con un voucher pagado
en pantalla, presiona **F5**. El voucher sigue en pie — mismo numero,
mismo total, badge Pagado — y el carro sigue vacío. Detrás no hay
retorno ninguno: el F5 re-carga la ruta de la SPA y la pantalla
re-fetchea el pedido (`GET /api/pedidos/{numero}`), una lectura sin
efectos — refrescar es gratis. El escenario que SÍ repite el retorno es
otro: back/forward hacia el `return_url` del backend o un retry del
navegador en vuelo (el spike observó 7 repeticiones de un mismo retorno)
— y ahí el guard ya-PAID del backend re-muestra la orden sin tocar el
stock ni la transición (PAY-03).

---

## ❌ El error que este archivo evita

**1. El submit del form en un `useEffect`.**

```tsx
// ❌ StrictMode monta dos veces en dev: dos órdenes PENDING y dos
// transacciones reales en Webpay — el "doble pago" del desarrollo
useEffect(() => {
  if (datos) form.submit();
}, [datos]);

// ✅ El submit vive SOLO en el onSuccess de la mutación que dispara el
// clic — y el botón disabled={isPending} cierra la puerta del doble clic
const pagar = useMutation({
  onSuccess: (resp) => { /* createElement + form.submit() */ },
});
```

La regla no es "useEffect mal": son los efectos NO idempotentes. Crear
una orden por corrida no es idempotente; vaciar un carro, sí.

**2. El form inyectado como HTML crudo.**

```tsx
// ❌ HTML concatenado a mano: cualquier descape es una puerta de XSS,
// y el costo de esa lección ya se pagó en la fase 2 (D-21, ADR-009)
contenedor.innerHTML = `<form action="${resp.url}">
  <input type="hidden" name="token_ws" value="${resp.token_ws}">
</form>`;

// ✅ DOM estándar con values tipados: React escapa por defecto, y acá
// no hay HTML que escapar — solo nodos creados y asignados
const form = document.createElement("form");
form.method = "POST";
form.action = resp.url;
```

(Los iframes tampoco: las propias docs de Webpay desaconsejan incrustar
su formulario — la navegación de página completa es el patrón oficial.)

**3. Vaciar el carro antes del voucher.**

```tsx
// ❌ limpiar al PRESIONAR el botón: si el pago falla o se anula, la
// clienta perdió su carro sin comprar nada
onSuccess: (resp) => { vaciar(); viajar_a_webpay(resp); };

// ✅ el vaciado en UN punto: el pedido fetcheado llegó paid (D-44) —
// en todo lo demás, el carro nunca se borró
useEffect(() => {
  if (pedido.data?.estado === "paid") vaciar();
}, [pedido.data]);
```

La restitución de PAY-04 como ausencia: no hay snapshots de carro ni
lógica de restauración que mantener.

**4. "Agregar Webpay al CORS".**

```tsx
// ❌ el retorno de Webpay es una NAVEGACIÓN de formulario del navegador,
// no un fetch: CORS jamás le aplicó — esta línea no arregla nada
allow_origins = ["http://localhost:5173", "https://webpay3gint.transbank.cl"];

// ✅ el CORS queda como está (guía 5): gobierna los fetch de TU SPA;
// la navegación del retorno pasa por fuera — primera excepción de la
// regla 5, narrada en el backend de la guía 9 (Pitfall 10)
```

El síntoma de este malentendido es buscarlo cuando "algo no vuelve" del
pago — y no encontrarlo, porque nunca estuvo ahí.

---

## ✅ Verificación de la guía 10

Con ambos servidores corriendo, el seed corrido y la sesión de la
clienta:

1. El experimento del compilador del paso 1: `"PAID"` rechazado por
   `EstadoPedido` — el enum del contrato en dos idiomas.
2. `/checkout` con ítems: CTA encendido "Pagar con Webpay" que pasa a
   "Pagando…" y se deshabilita mientras corre la mutación — la nota "El
   pago llega en la etapa siguiente." ya no existe (D-31 encendido).
3. `http://localhost:5173/pago/resultado?estado=anulado` SIN sesión: la
   cara no aprobada se ve — la ruta es pública de verdad (Pitfall 12).
4. `?estado=pagado&orden=MAURA-000001` con sesión: "Tu pago está en
   curso" con badge ámbar — la orden pending de la guía 9, honesta
   (RN-11); sin sesión: estado + numero + "inicia sesión para ver el
   detalle" que vuelve al resultado tras entrar (returnTo con query).
5. Pago APROBADO con la VISA `4051 8856 0044 6623` (CVV 123, RUT
   `11.111.111-1`, clave 123): voucher de la tienda con numero, fecha,
   líneas snapshot, total y badge Pagado — carro en 0 y stock descontado.
6. Pago ANULADO con el botón del formulario: cara "Tu compra no se
   concretó" con el carro intacto para reintentar (PAY-04, D-44).
7. F5 sobre el voucher pagado: sigue en pie sin pagar dos veces — el F5
   solo re-fetcha el pedido (lectura sin efectos); el guard ya-PAID del
   backend cubre la navegación repetida al retorno y el vaciado es
   idempotente (PAY-03).

## 📝 Punto de control (respóndelas sin mirar la guía)

1. ¿Por qué el submit hacia Webpay vive en el handler del clic y jamás
   en un `useEffect`? Nombra el mecanismo de React que rompería un
   efecto no idempotente — y por qué el vaciado del carro SÍ puede vivir
   en uno.
2. `/checkout` vive dentro de `RequireAuth` y `/pago/resultado` fuera,
   a propósito: ¿quién llega a cada una, qué pasa con el 302 si el token
   expiró, y cómo vuelve la clienta al voucher tras iniciar sesión?
3. ¿Cuándo exactamente se vacía el carro — y por qué esa es toda la
   implementación que PAY-04 necesita para "restituir" el carro anulado?
4. El navegador vuelve de Webpay y aterriza en la SPA: recorre el
   camino completo — quién discriminó el flujo, quién paginó el 302,
   qué lee la pantalla y quién fetchea el pedido — y di qué pieza de
   ese camino NO pasa por `lib/api.ts` y por qué.

## Lo que acabas de aprender

- El form POST auto-submit con `document.createElement`: la navegación de página completa que Webpay exige, construida a mano con values tipados — React escapa por defecto y los iframes están desaconsejados (D-21, PAY-01)
- El submit SOLO en el handler del clic (Pitfall 6): efectos no idempotentes jamás en `useEffect` — y el CTA `disabled={isPending}` con label en gerundio cerrando la puerta del doble clic
- La primera excepción de la regla 5: el checkout ES fetch (por `lib/api.ts`, con Bearer, reusando el `apiPost` del registro); el retorno es navegación del navegador y no pasa por ahí
- La ruta pública `/pago/resultado` fuera de `RequireAuth` (Pitfall 12): el 302 llega sin sesión en la URL y la pantalla degrada con honestidad — estado y numero visibles, "inicia sesión para ver el detalle" con `returnTo` que lleva la query dentro del string (D-32/D-42)
- El voucher de la tienda como componente `VoucherPedido` (D-43): numero legible, fecha, líneas con snapshot, total y badge de estado — presentation pura, lista para que el historial de la guía 11 la herede (D-46)
- El vaciado del carro en UN punto (D-44): SOLO el pedido fetcheado llega `paid`, junto con `invalidateQueries` del stock — la restitución de PAY-04 como ausencia
- Las caras del resultado espejando al discriminador del backend (D-42): no aprobadas sin fetch con su causa y el carro intacto; aprobadas/rechazadas con el voucher cuyo badge dice la verdad
- El pago real de ida y vuelta con la tarjeta oficial — y el F5 que no paga doble: re-fetch de lectura del pedido; el guard ya-PAID del backend cubre la navegación repetida al retorno (PAY-03)

**Siguiente:** guia-11-pedidos-cierre.md — el historial "/pedidos" con
sus badges honestos (las "en curso" incluidas), "Mis pedidos" en el
navbar, el detalle que reutiliza tu voucher… y la Gran verificación
final de la fase 3: el contrato 0.3.0 contra `/docs`, los cuatro flujos
del retorno y la carrera de stock, fila por fila.
