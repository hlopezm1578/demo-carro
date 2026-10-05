# Guía 7 — El carro: el store que guarda tus aromas

> **Qué construirás hoy:** el carro de compras — el store que lo recuerda
> entre visitas, la ficha que agrega, la página `/carro` que lo edita con
> precios vigentes y el badge del navbar que lo anuncia.
> **Al terminar tendrás:** un carro que sobrevive recargas y cierres del
> navegador sin exigir cuenta (CART-01, CART-02) y la pantalla lista para el
> checkout que llega en la guía 8.
> **Necesitas:** las guías 1 a 6 completas — la ficha con su `queryKey` y su
> `ApiError` de la guía 4, el store de sesión con `persist` de la guía 6
> (el carro replica su mecánica), el seed de cuentas hecho y ambos
> servidores corriendo (`backend/` en el puerto 8000, `frontend/` con
> `npm run dev`).

---

## Los términos de hoy (antes de copiar nada)

| Término | Qué es, en una frase |
|---|---|
| **Estado de cliente** | Lo que vive SOLO en el navegador: la sesión de la guía 6 y ahora el carro — dos stores hermanos con el mismo mecanismo |
| **Persistencia** | Que el estado sobreviva recargas y cierres del navegador: `persist` lo guarda en `localStorage` y lo devuelve intacto al partir |
| **Hidratación** | Rellenar los datos vivos (nombre, precio, stock) consultando la API a partir del id guardado: el carro guarda la llave, la tienda pone el resto |
| **Merge de cantidad** | Agregar dos veces el mismo aroma SUMA unidades en una sola fila — jamás crea filas repetidas |
| **Confirmación en dos pasos** | La forma de la primera acción destructiva del sistema: el primer clic transforma la zona en la pregunta y las acciones reales — sin modal ni diálogos del navegador |

---

## Paso 1 — `stores/useCarroStore.ts`: solo ids y cantidades, jamás precios

🧠 **El desarrollador piensa:** *el carro es el segundo estado de cliente de
la tienda — el hermano del store de sesión: mismo mecanismo (`persist` sobre
`localStorage`), distinto contenido. ¿Y qué guarda? ADR-010 lo dejó escrito
(D-27): **solo pares `{producto_id, cantidad}`** — nada de nombres, nada de
precios, jamás. ¿Por qué tan severo? Porque un precio guardado en el
navegador es una foto vieja esperando el momento de engañar (RN-08): si la
dueña mueve el precio mañana, el carro lo mostrará igual de mañana, porque el
precio se mira SIEMPRE a la API. Esa es además la lección que la etapa 3
convertirá en segunda barrera: cuando el backend recalcule el total de la
orden sin confiar en nadie (CART-03), el cliente que jamás decidió precios no
tendrá nada que "decidir". Las acciones son cuatro: `agregar` con MERGE (si
el aroma ya está, las cantidades se suman en la misma fila — HU-07),
`cambiarCantidad` (el stepper del paso 3), `quitar` (una fila) y `vaciar`
(todo — con la confirmación del paso 6). Y `partialize` persiste solo los
items: la regla de la guía 6 palabra por palabra, porque las funciones no se
serializan a JSON.*

Crea **`frontend/src/stores/useCarroStore.ts`**:

```typescript
// El carro de compras: SOLO pares {producto_id, cantidad} persistidos en
// localStorage bajo la clave "maura-carro" (ADR-010, D-27). Sin nombres y
// sin precios JAMÁS: lo que se muestra se hidrata contra la API — el
// navegador no decide precios (RN-08).
import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

export interface ItemCarro {
  producto_id: number;
  cantidad: number;
}

interface EstadoCarro {
  items: ItemCarro[];
  agregar: (producto_id: number, cantidad?: number) => void;
  cambiarCantidad: (producto_id: number, cantidad: number) => void;
  quitar: (producto_id: number) => void;
  vaciar: () => void;
}

export const useCarroStore = create<EstadoCarro>()(
  persist(
    (set, get) => ({
      items: [],
      // Merge: si el aroma ya está, las cantidades se SUMAN (HU-07) —
      // agregar dos veces el mismo producto es una fila, no dos.
      agregar: (producto_id, cantidad = 1) => {
        const existente = get().items.find(
          (i) => i.producto_id === producto_id
        );
        if (existente) {
          set({
            items: get().items.map((i) =>
              i.producto_id === producto_id
                ? { ...i, cantidad: i.cantidad + cantidad }
                : i
            ),
          });
        } else {
          set({ items: [...get().items, { producto_id, cantidad }] });
        }
      },
      cambiarCantidad: (producto_id, cantidad) =>
        set({
          items: get().items.map((i) =>
            i.producto_id === producto_id ? { ...i, cantidad } : i
          ),
        }),
      quitar: (producto_id) =>
        set({
          items: get().items.filter((i) => i.producto_id !== producto_id),
        }),
      vaciar: () => set({ items: [] }),
    }),
    {
      name: "maura-carro", // la clave exacta en localStorage
      storage: createJSONStorage(() => localStorage), // explícito (didáctico)
      // SOLO los items: jamás funciones — la misma regla de maura-auth.
      partialize: (state) => ({ items: state.items }),
    }
  )
);
```

✅ **Mini-verificación:** `npm run build` pasa — y el archivo es el store de
sesión de la guía 6 con otro contenido: `persist` + `createJSONStorage` +
`partialize`, la misma forma. La prueba de fuego del `localStorage` (ver el
JSON mínimo de `maura-carro` con tus propios ojos) llega en el paso 2; hoy el
store nace y espera consumidores.

---

## Paso 2 — La ficha gana "Agregar al carro" (y solo la ficha)

🧠 **El desarrollador piensa:** *dónde vive el botón es una decisión de
producto, no de comodidad: **solo en la ficha** (D-29), donde el stock está
a la vista y la clienta ya se enamoró del aroma — las tarjetas del catálogo
siguen navegando, igual que en la fase 1. El botón es un CTA full-width bajo
la disponibilidad, y se deshabilita en DOS casos: stock 0 (el badge
"Agotado" ya lo comunica, el botón no contradice) y **la cantidad en el
carro ya alcanza el stock** (D-30) — con su helper "Ya tienes todo el stock
disponible en tu carro." para que el bloqueo no sea un misterio. ¿Y el
feedback de la acción? Ninguno modal, ninguno flotante: el badge del navbar
incrementa en vivo (paso 7, con `aria-live`) — la prueba de que agregaste
está en la barra que acompaña toda la tienda. Un clic agrega UNA unidad y
hace merge con lo que ya iba: la edición fina de cantidades vive en `/carro`
(D-28). Y ojo con la honestidad de la barrera: esto tapa la sobreventa EN
PANTALLA; la barrera real la pondrá el backend al crear la orden en la etapa
3 (CART-03) — primera barrera hoy, segunda barrera después.*

Reemplaza el contenido completo de
**`frontend/src/features/catalogo/FichaProducto.tsx`** por este — lo nuevo
del paso son tres cosas y van marcadas por donde quedan: el import del
store junto a los demás imports, las constantes `agregar`/`productoId`/
`enCarro` debajo de los `useParams`/`useNavigate`, y el botón con su
helper al final de la columna de información:

```tsx
import { useQuery } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router";
import { ApiError, apiGet } from "../../lib/api";
import { useCarroStore } from "../../stores/useCarroStore";
import {
  FAMILIA_BADGES,
  FAMILIA_LABELS,
  type ProductoDetalle,
} from "../../types/api";

const clp = new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP" });

function BadgeDisponibilidad({ stock }: { stock: number }) {
  if (stock === 0) {
    return (
      <span className="text-sm rounded-full px-2 py-1 bg-neutral-200 text-neutral-700">
        Agotado
      </span>
    );
  }
  if (stock <= 3) {
    return (
      <span className="text-sm rounded-full px-2 py-1 bg-amber-100 text-amber-800">
        ¡Últimas {stock} unidades!
      </span>
    );
  }
  return (
    <span className="text-sm rounded-full px-2 py-1 bg-emerald-100 text-emerald-800">
      Disponible
    </span>
  );
}

export default function FichaProducto() {
  const { id } = useParams();
  const navigate = useNavigate();
  const agregar = useCarroStore((s) => s.agregar);
  // ¿Cuántas unidades de ESTE aroma ya van en el carro? Para el tope (D-30).
  // Number(id): el id del useParams es un string; el store guarda número.
  const productoId = Number(id);
  const enCarro = useCarroStore(
    (s) => s.items.find((i) => i.producto_id === productoId)?.cantidad ?? 0
  );

  const query = useQuery({
    queryKey: ["producto", id],
    queryFn: () => apiGet<ProductoDetalle>(`api/productos/${id}`),
  });

  if (query.isPending) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-10 grid md:grid-cols-2 gap-10">
        <div className="aspect-square animate-pulse bg-neutral-200 rounded-3xl" />
        <div className="space-y-4">
          <div className="h-6 w-24 animate-pulse bg-neutral-200 rounded-full" />
          <div className="h-8 w-3/4 animate-pulse bg-neutral-200 rounded-2xl" />
          <div className="h-4 w-1/2 animate-pulse bg-neutral-200 rounded-2xl" />
        </div>
      </div>
    );
  }

  if (
    query.isError &&
    query.error instanceof ApiError &&
    query.error.status === 404
  ) {
    return (
      <div className="max-w-xl mx-auto px-4 py-16 text-center">
        <h1 className="text-xl font-bold text-neutral-900">
          Producto no encontrado
        </h1>
        <p className="mt-2 text-sm text-neutral-600">
          Puede que el enlace esté viejo.
        </p>
        <Link
          to="/productos"
          className="mt-6 inline-flex items-center text-sm text-orange-600 min-h-11 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
        >
          Volver al catálogo
        </Link>
      </div>
    );
  }

  if (query.isError) {
    return (
      <div className="max-w-xl mx-auto px-4 py-16 text-center">
        <h1 className="text-xl font-bold text-neutral-900">
          No pudimos cargar este producto
        </h1>
        <p className="mt-2 text-sm text-neutral-600">
          Revisa que el backend esté corriendo en el puerto 8000 e inténtalo
          de nuevo.
        </p>
        <button
          onClick={() => query.refetch()}
          className="mt-6 bg-orange-600 text-white font-bold rounded-full px-6 py-2 min-h-11 hover:bg-orange-700 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
        >
          Reintentar
        </button>
      </div>
    );
  }

  const producto = query.data;

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <button
        onClick={() => navigate(-1)}
        className="text-sm text-orange-600 min-h-11 flex items-center focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
      >
        ← Volver al catálogo
      </button>

      <div className="mt-4 grid md:grid-cols-2 gap-10">
        <img
          src={producto.imagen}
          alt={producto.nombre}
          className="rounded-3xl aspect-square object-cover bg-neutral-200 w-full shadow-md"
        />
        <div>
          <div className="flex flex-wrap gap-2">
            <span
              className={`text-sm rounded-full px-2 py-1 ${FAMILIA_BADGES[producto.familia]}`}
            >
              {FAMILIA_LABELS[producto.familia]}
            </span>
            <BadgeDisponibilidad stock={producto.stock} />
          </div>
          <h1 className="mt-3 text-2xl md:text-3xl font-extrabold text-neutral-900">
            {producto.nombre}
          </h1>
          <p className="mt-1 text-2xl font-extrabold text-orange-700">
            {clp.format(producto.precio)}
          </p>
          <p className="mt-5 text-base leading-relaxed text-neutral-600">
            {producto.descripcion}
          </p>
          {producto.notas.length > 0 && (
            <div className="mt-6">
              <p className="text-sm font-bold text-neutral-900">
                Notas aromáticas
              </p>
              <div className="mt-2 flex flex-wrap gap-2">
                {producto.notas.map((nota) => (
                  <span
                    key={nota}
                    className="text-sm rounded-full px-2 py-1 bg-orange-50 text-neutral-700"
                  >
                    {nota}
                  </span>
                ))}
              </div>
            </div>
          )}
          <p className="mt-6 text-sm font-semibold text-neutral-600">
            {producto.stock === 0
              ? "Agotado"
              : `${producto.stock} ${producto.stock === 1 ? "unidad" : "unidades"} disponibles`}
          </p>
          <button
            onClick={() => agregar(producto.id, 1)}
            disabled={producto.stock === 0 || enCarro >= producto.stock}
            className="mt-4 w-full bg-orange-600 text-white font-bold rounded-full px-6 py-2 min-h-11 hover:bg-orange-700 disabled:opacity-60 disabled:cursor-not-allowed focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
          >
            Agregar al carro
          </button>
          {producto.stock > 0 && enCarro >= producto.stock && (
            <p className="mt-2 text-sm text-neutral-600">
              Ya tienes todo el stock disponible en tu carro.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
```

✅ **Mini-verificación (D-27, con tus ojos):** abre la ficha de **Brisa de
Naranja** (`http://localhost:5173/productos/1`, stock 14) y clic en "Agregar
al carro" DOS veces. Abre DevTools → Application → Local Storage →
`maura-carro`: el valor es exactamente
`{"state":{"items":[{"producto_id":1,"cantidad":2}]},"version":0}` — un par
de id y cantidad, SIN nombre y SIN precio (D-27 en el JSON). El segundo clic
hizo merge: una fila con cantidad 2, no dos filas. Vuelve a la ficha y sigue
agregando hasta 14: el botón se deshabilita con el helper "Ya tienes todo el
stock disponible en tu carro." — el tope de la ficha trabajando (D-30).

---

## Paso 3 — `features/carro/FilaCarro.tsx`: una fila, tres caras

🧠 **El desarrollador piensa:** *cada fila del carro es un ítem persistido
que hay que rellenar con datos vivos — y la hidratación puede salir de tres
maneras, así que la fila nace sabiendo estar en tres caras. **Cargando:**
esqueleto con el MISMO layout de la fila real (thumbnail + textos +
stepper): la página no salta cuando llegan los precios. **Degradada:** el
ítem apunta a un producto que ya no existe — la hidratación responde 404 y
la fila muestra "Este aroma ya no está disponible" + "Quitar", sin stepper:
feo pero honesto, y el resto del carro sigue operando. ¿Cómo DISTINGO el
404 de un error de red? Con el mismo truco de la ficha de la guía 4:
`error instanceof ApiError && error.status === 404` — dos errores distintos,
dos caras distintas. **Normal:** la fila completa con stepper tapado al
stock. Y el tapado tiene nombre propio en tres valores: la cantidad
GUARDADA (que puede estar vieja), el stock VIGENTE (recién hidratado) y la
cantidad EN PANTALLA — `Math.min(cantidad, stock)` (D-30/RN-09): guardaste 5,
hay 2, la pantalla muestra 2 y el total cobra 2. La pantalla nunca promete
más de lo que hay.*

Crea la carpeta **`frontend/src/features/carro/`** y
**`frontend/src/features/carro/FilaCarro.tsx`**:

```tsx
// Una fila del carro: hidrata su ítem contra el catálogo (ADR-010) y sabe
// estar en tres caras — cargando (esqueleto), degradada (el aroma ya no
// existe) y normal (stepper tapado al stock, RN-09).
import { Link } from "react-router";

import { useCarroStore, type ItemCarro } from "../../stores/useCarroStore";
import {
  FAMILIA_BADGES,
  FAMILIA_LABELS,
  type ProductoDetalle,
} from "../../types/api";

const clp = new Intl.NumberFormat("es-CL", {
  style: "currency",
  currency: "CLP",
});

const estiloQuitar =
  "text-sm text-red-600 min-h-11 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none";

export default function FilaCarro({
  item,
  isPending,
  noDisponible,
  producto,
}: {
  item: ItemCarro;
  isPending: boolean;
  noDisponible: boolean; // la hidratación respondió 404
  producto?: ProductoDetalle;
}) {
  const cambiarCantidad = useCarroStore((s) => s.cambiarCantidad);
  const quitar = useCarroStore((s) => s.quitar);

  if (isPending) {
    // Esqueleto con el MISMO layout de la fila real: sin salto de layout.
    return (
      <div className="flex gap-4 items-center p-4 bg-white rounded-2xl border border-orange-100">
        <div className="w-20 h-20 shrink-0 rounded-2xl animate-pulse bg-neutral-200" />
        <div className="flex-1 space-y-2">
          <div className="h-5 w-24 animate-pulse bg-neutral-200 rounded-full" />
          <div className="h-6 w-3/4 animate-pulse bg-neutral-200 rounded-2xl" />
          <div className="h-4 w-1/3 animate-pulse bg-neutral-200 rounded-2xl" />
        </div>
        <div className="h-11 w-11 rounded-full animate-pulse bg-neutral-200" />
      </div>
    );
  }

  if (noDisponible) {
    // El aroma ya no está en el catálogo: fila degradada, sin stepper —
    // el resto del carro sigue operando.
    return (
      <div className="flex gap-4 items-center justify-between p-4 bg-white rounded-2xl border border-orange-100">
        <div className="flex gap-4 items-center">
          <div className="w-20 h-20 shrink-0 rounded-2xl bg-neutral-200" />
          <p className="text-sm text-neutral-600">
            Este aroma ya no está disponible
          </p>
        </div>
        <button
          onClick={() => quitar(item.producto_id)}
          className={estiloQuitar}
        >
          Quitar
        </button>
      </div>
    );
  }

  if (!producto) return null; // (los estados de arriba cubren el resto)

  // D-30/RN-09, en tres valores con nombre: lo guardado, lo vigente y lo
  // que la pantalla muestra — el mínimo entre ambos. La pantalla jamás
  // promete más unidades de las que hay.
  const { cantidad } = item; // lo GUARDADO (puede estar viejo)
  const stock = producto.stock; // lo VIGENTE (recién hidratado)
  const enPantalla = Math.min(cantidad, stock); // lo que se muestra

  return (
    <div className="flex flex-wrap gap-4 items-center p-4 bg-white rounded-2xl border border-orange-100">
      <Link
        to={`/productos/${producto.id}`}
        className="shrink-0 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
      >
        <img
          src={producto.imagen}
          alt={producto.nombre}
          loading="lazy"
          className="w-20 h-20 rounded-2xl object-cover bg-neutral-200"
        />
      </Link>

      <div className="flex-1 min-w-40">
        <span
          className={`text-sm rounded-full px-2 py-1 ${FAMILIA_BADGES[producto.familia]}`}
        >
          {FAMILIA_LABELS[producto.familia]}
        </span>
        <Link
          to={`/productos/${producto.id}`}
          className="mt-1 block text-xl font-bold text-neutral-900 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
        >
          {producto.nombre}
        </Link>
        <p className="mt-1 text-sm text-neutral-600">
          {clp.format(producto.precio)} c/u
        </p>
      </div>

      {producto.stock === 0 ? (
        <span className="text-sm rounded-full px-2 py-1 bg-neutral-200 text-neutral-700">
          Agotado
        </span>
      ) : (
        <div className="flex items-center gap-2">
          <button
            onClick={() => cambiarCantidad(item.producto_id, enPantalla - 1)}
            disabled={enPantalla <= 1}
            aria-label={`Quitar una unidad de ${producto.nombre}`}
            className="h-11 w-11 rounded-full border border-orange-200 bg-white text-base disabled:opacity-40 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
          >
            −
          </button>
          <span className="text-base font-bold w-8 text-center">
            {enPantalla}
          </span>
          <button
            onClick={() => cambiarCantidad(item.producto_id, enPantalla + 1)}
            disabled={enPantalla >= producto.stock}
            aria-label={`Agregar una unidad de ${producto.nombre}`}
            className="h-11 w-11 rounded-full border border-orange-200 bg-white text-base disabled:opacity-40 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
          >
            +
          </button>
        </div>
      )}

      {producto.stock > 0 && (
        <p className="text-lg font-extrabold text-orange-700">
          {clp.format(enPantalla * producto.precio)}
        </p>
      )}

      <button
        onClick={() => quitar(item.producto_id)}
        className={estiloQuitar}
      >
        Quitar
      </button>
    </div>
  );
}
```

Fíjate en las reglas del stepper: "−" se deshabilita en 1 — para eliminar
una fila está "Quitar" (un stepper jamás borra), y "+" se deshabilita en el
stock VIGENTE con `opacity-40`. Y "Quitar" va sin confirmación: un ítem es
de bajo impacto y se revuelve volviendo a la ficha — la confirmación se
reserva para "Vaciar carro" (paso 6).

✅ **Mini-verificación:** `npm run build` pasa. La fila es un componente
presentacional: recibe el ítem, sus banderas de estado y el producto
hidratado — quien decide qué mostrar es la página que llega en el paso
siguiente.

---

## Paso 4 — `features/carro/Carro.tsx`: la página que hidrata y totaliza

🧠 **El desarrollador piensa:** *la página tiene que hidratar TODOS los ítems
a la vez — y ahí aparece la pieza nueva del día: `useQueries`, de la misma
TanStack Query que ya usamos. Hasta ahora cada pantalla tenía UN `useQuery`;
el carro tiene N, y N cambia cuando la clienta agrega o quita (los hooks en
un loop de largo variable están prohibidos por las reglas de React — y
`useQueries` existe justamente para eso: un número variable de queries en
paralelo, una por ítem, manteniendo el orden: `resultados[i]` corresponde a
`items[i]`). Ahora, el detalle que ahorra la mitad de las consultas: el
`queryKey` es el MISMO de la ficha — `["producto", String(id)]`. Misma
librería, misma caché: venir de la ficha al carro no vuelve a consultar ese
producto. Y el `String(id)` no es decorativo: la ficha guarda el id del
`useParams` (string); si el carro lo pasara como número, `("producto", "1")`
y `("producto", 1)` serían cachés DISTINTAS y la consulta se repetiría. En
pantalla: el total del panel suma las líneas con la cantidad tapada (lo que
no hay en stock no suma) y muestra un esqueleto mientras alguna fila carga —
sin shift. Y el tapado no es solo visual: al hidratar, si lo guardado supera
el stock vigente, el ajuste se ESCRIBE de vuelta al store — el diseño lo
promete así ("la cantidad guardada se ajusta sola", §4.7) y así el badge del
navbar queda contando las mismas unidades que la fila muestra. Con 0 ítems
la página COMPLETA se reemplaza por el estado vacío: un carro sin aromas no
tiene filas que mostrar ni total que cobrar (HU-07). Sin envío en el
desglose: la logística está fuera de alcance del proyecto — el total es la
suma de las líneas y nada más.*

Crea **`frontend/src/features/carro/Carro.tsx`**:

```tsx
// La página del carro (RF-10, RF-11): filas hidratadas con precios vigentes
// (ADR-010), edición tapada al stock (RN-09), vaciado en dos pasos y el
// resumen con el CTA hacia el checkout (D-28).
import { useQueries } from "@tanstack/react-query";
import { Link } from "react-router";
import { useEffect, useState } from "react";

import { ApiError, apiGet } from "../../lib/api";
import { useCarroStore } from "../../stores/useCarroStore";
import type { ProductoDetalle } from "../../types/api";
import FilaCarro from "./FilaCarro";

const clp = new Intl.NumberFormat("es-CL", {
  style: "currency",
  currency: "CLP",
});

export default function Carro() {
  const items = useCarroStore((s) => s.items);
  const vaciar = useCarroStore((s) => s.vaciar);
  const cambiarCantidad = useCarroStore((s) => s.cambiarCantidad);
  const [confirmando, setConfirmando] = useState(false);

  // Hidratación por ítem (ADR-010): el MISMO queryKey de la ficha — con
  // String(id), porque la ficha guarda el id del useParams como string:
  // ("producto", "1") y ("producto", 1) son cachés DISTINTAS. Un carro demo
  // tiene a lo más 12 aromas: 12 consultas, la mayoría ya cacheadas.
  const resultados = useQueries({
    queries: items.map((item) => ({
      queryKey: ["producto", String(item.producto_id)],
      queryFn: () =>
        apiGet<ProductoDetalle>(`api/productos/${item.producto_id}`),
    })),
  });

  // El ajuste se ESCRIBE de vuelta (D-30/RN-09): si lo guardado supera el
  // stock vigente, la hidratación corrige el store — así el badge del
  // navbar y el localStorage cuentan las mismas unidades que la pantalla
  // muestra. El efecto se calma solo: una vez tapado, la condición deja
  // de disparar.
  useEffect(() => {
    resultados.forEach((r, i) => {
      const item = items[i];
      if (r.data && item && item.cantidad > r.data.stock) {
        cambiarCantidad(item.producto_id, r.data.stock);
      }
    });
  }, [resultados, items, cambiarCantidad]);

  // Empty state: con 0 ítems la página completa se reemplaza (HU-07).
  if (items.length === 0) {
    return (
      <main className="max-w-xl mx-auto px-4 py-16 text-center">
        <h1 className="text-2xl md:text-3xl font-extrabold text-neutral-900">
          Tu carro está vacío
        </h1>
        <p className="mt-2 text-base text-neutral-600">
          Explora los aromas de Maura y agrega tus favoritos.
        </p>
        <Link
          to="/productos"
          className="mt-6 inline-flex items-center bg-orange-600 text-white font-bold rounded-full px-6 py-2 min-h-11 hover:bg-orange-700 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
        >
          Ver catálogo
        </Link>
      </main>
    );
  }

  // Error general (el 404 NO es error general: es una fila degradada).
  const falloGeneral = resultados.some(
    (r) => r.isError && !(r.error instanceof ApiError && r.error.status === 404)
  );
  if (falloGeneral) {
    return (
      <main className="max-w-xl mx-auto px-4 py-16 text-center">
        <h1 className="text-xl font-bold text-neutral-900">
          No pudimos cargar tu carro
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

  // El total usa la cantidad tapada (RN-09): lo que no hay en stock no
  // suma. Las filas aún cargando o degradadas todavía no aportan.
  const total = resultados.reduce((suma, r, i) => {
    if (!r.data) return suma;
    const { cantidad } = items[i];
    return suma + Math.min(cantidad, r.data.stock) * r.data.precio;
  }, 0);

  return (
    <main className="max-w-6xl mx-auto px-4 py-16">
      <h1 className="text-2xl md:text-3xl font-extrabold text-neutral-900">
        Tu carro
      </h1>

      <div className="mt-6 md:grid md:grid-cols-3 gap-6 items-start">
        <div className="md:col-span-2 flex flex-col gap-4">
          {items.map((item, i) => {
            const r = resultados[i];
            return (
              <FilaCarro
                key={item.producto_id}
                item={item}
                isPending={r.isPending}
                noDisponible={
                  r.isError &&
                  r.error instanceof ApiError &&
                  r.error.status === 404
                }
                producto={r.data}
              />
            );
          })}

          {confirmando ? (
            <div className="flex flex-wrap gap-4 items-center">
              <span className="text-sm text-neutral-900">
                ¿Vaciar todo el carro?
              </span>
              <button
                onClick={() => {
                  vaciar();
                  setConfirmando(false);
                }}
                className="text-sm text-red-600 font-bold min-h-11 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
              >
                Sí, vaciar
              </button>
              <button
                onClick={() => setConfirmando(false)}
                className="text-sm text-neutral-600 min-h-11 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
              >
                Cancelar
              </button>
            </div>
          ) : (
            <button
              onClick={() => setConfirmando(true)}
              className="self-start text-sm text-red-600 font-bold min-h-11 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
            >
              Vaciar carro
            </button>
          )}
        </div>

        <div className="mt-6 md:mt-0 bg-orange-50 rounded-2xl border border-orange-100 p-6">
          <div className="flex items-baseline justify-between gap-4">
            <span className="text-base font-bold text-neutral-900">
              Total
            </span>
            {cargando ? (
              <div className="h-8 w-28 animate-pulse bg-neutral-200 rounded-2xl" />
            ) : (
              <span className="text-2xl font-extrabold text-orange-700">
                {clp.format(total)}
              </span>
            )}
          </div>
          <Link
            to="/checkout"
            className="mt-6 block text-center bg-orange-600 text-white font-bold rounded-full px-6 py-2 min-h-11 hover:bg-orange-700 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
          >
            Finalizar compra
          </Link>
        </div>
      </div>
    </main>
  );
}
```

✅ **Mini-verificación:** `npm run build` pasa. La ruta se cablea en el paso
siguiente — si quieres verla ya, adelántate un paso y vuelve: con ítems en
el carro verás las filas con su precio `c/u` hidratado, el total de línea en
terracota y el panel con el Total que calza con la suma (compárala a mano:
2 × $7.990 + 1 × $10.990 = $26.970).

---

## Paso 5 — `main.tsx`: la ruta `/carro` dentro del Layout

🧠 **El desarrollador piensa:** *una línea de ruta, cero decisiones nuevas —
y eso ES la decisión: `/carro` es una página de la tienda más, no una isla.
Vive DENTRO del Layout (Navbar y Footer alrededor), los imports salen de
`"react-router"` y el orden de los providers no se toca — composición, como
siempre. ¿Protegida? NO: el carro es del visitante anónimo (RF-11) — la
sesión se exigirá donde sí importa, en el checkout de la guía 8.*

Reemplaza el contenido completo de **`frontend/src/main.tsx`** por este
— lo nuevo del paso: el import de `Carro` junto a los de las features, y
la ruta `/carro` dentro del `<Route element={<Layout />}>`:

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
            <Route path="*" element={<NoEncontrado />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>
);
```

✅ **Mini-verificación:** con `npm run dev`, abre
**http://localhost:5173/carro** con algo agregado: la página "Tu carro" con
Navbar y Footer alrededor. Clic en "Quitar" en una fila: desaparece al
instante y el total se recalcula — el stepper y "Quitar" mutando el mismo
store que la ficha alimenta.

---

## Paso 6 — "Vaciar carro" en dos pasos: la primera acción destructiva

🧠 **El desarrollador piensa:** *vaciar borra TODO de una vez — es la primera
acción destructiva del sistema, y merece confirmación. Pero no un modal ni
un `window.confirm`: esa sería una lección de componente, y lo que hay que
aprender aquí es **estado de confirmación**. El mecanismo es un booleano:
`confirmando` empieza falso y el botón "Vaciar carro" solo lo vuelve
verdadero — el clic uno PREGUNTA, no borra. Con `confirmando` en true, la
zona se transforma: "¿Vaciar todo el carro?" con "Sí, vaciar" (este sí
llama `vaciar()`) y "Cancelar" (vuelve al estado inicial sin tocar nada).
Todo inline, en el mismo lugar donde estaba el botón: la clienta ve la
pregunta donde hizo el clic, sin diálogos del navegador encima. La regla
que nace aquí la replican las acciones destructivas futuras: confirmación
en dos pasos, en el lugar, sin modales. ¿Y por qué "Quitar" de fila NO
confirma? Porque su impacto es una unidad reversible: la asimetría es el
criterio — se confirma lo que borra de una vez, no lo que se deshace
volviendo a la ficha.*

(La zona ya quedó escrita en el `Carro.tsx` del paso 4 — este paso la
explica; vuelve a leerla ahí.)

✅ **Mini-verificación (los dos pasos, en vivo):** en `/carro` con ítems,
clic en "Vaciar carro": la zona cambia a "¿Vaciar todo el carro?" con "Sí,
vaciar" y "Cancelar" — nada se borró todavía. Clic en "Cancelar": vuelve el
botón original y el carro sigue intacto. Ahora clic en "Vaciar carro" →
"Sí, vaciar": el carro desaparece y la página completa muestra el estado
vacío "Tu carro está vacío" con el botón "Ver catálogo" (HU-07 completa).

---

## Paso 7 — El badge del navbar: unidades, no ítems (D-28)

🧠 **El desarrollador piensa:** *el badge es el feedback vivo de cada
"Agregar al carro" — por eso el botón de la ficha no necesita toast ni
modal: la prueba está en la barra que acompaña toda la tienda. Tres reglas
lo definen. **Cuenta unidades totales, no ítems:** 2 de un aroma más 1 de
otro son 3 — `items.reduce((total, i) => total + i.cantidad, 0)`, lo mismo
que el diseño pide. **Se oculta en 0:** un badge en "0" es ruido que
ensucia la barra. **Se anuncia:** `aria-live="polite"` hace que el lector
de pantalla diga el nuevo número apenas cambia (ese ES el feedback de la
acción), y `aria-label` dice de qué se trata ("3 unidades en el carro"). El
estilo es el de siempre: pastilla redonda terracota con blanco, `px-2 py-1`
— a lo más dos dígitos sin romper el alto del link, porque el link ya tiene
su `min-h-11` desde la guía 2.*

Reemplaza el contenido completo de **`frontend/src/components/Navbar.tsx`**
por este — lo nuevo del paso: el import del store del carro, el selector
`unidades` junto a los otros, y el link "Carro" con su badge entre
"Catálogo" y la zona de sesión:

```tsx
// Navbar con estado de sesión (A9): sin sesión → "Ingresar"; con sesión →
// email truncado + "Cerrar sesión". El badge del carro llega en la guía 7.
import { Link, NavLink, useNavigate } from "react-router";

import { useAuthStore } from "../stores/useAuthStore";
import { useCarroStore } from "../stores/useCarroStore";

const estiloLink = ({ isActive }: { isActive: boolean }) =>
  `text-sm min-h-11 flex items-center focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none ${
    isActive ? "text-orange-600 font-bold" : "text-neutral-600"
  }`;

export default function Navbar() {
  const navegar = useNavigate();
  const usuario = useAuthStore((s) => s.usuario);
  const cerrarSesion = useAuthStore((s) => s.cerrarSesion);
  // D-28: unidades TOTALES del carro (no ítems): 2 de un aroma + 1 de
  // otro = 3.
  const unidades = useCarroStore((s) =>
    s.items.reduce((total, i) => total + i.cantidad, 0)
  );

  function salir() {
    cerrarSesion(); // borra token+usuario — y el persist limpia localStorage
    navegar("/"); // sin confirmación: entrar de nuevo son dos campos
  }

  return (
    <header className="sticky top-0 z-10 bg-orange-50/90 backdrop-blur border-b border-orange-100">
      <nav className="max-w-6xl mx-auto flex items-center justify-between gap-4 px-4 py-3">
        <Link
          to="/"
          className="flex items-center gap-2 text-xl font-bold text-neutral-900 truncate focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
        >
          <span
            aria-hidden="true"
            className="h-2.5 w-2.5 rounded-full bg-orange-600"
          />
          Maura · Body Splash
        </Link>
        <div className="flex flex-wrap items-center gap-4">
          <NavLink to="/" end className={estiloLink}>
            Inicio
          </NavLink>
          <NavLink to="/productos" className={estiloLink}>
            Catálogo
          </NavLink>
          <NavLink to="/carro" className={estiloLink}>
            Carro
            {unidades > 0 && (
              <span
                aria-live="polite"
                aria-label={`${unidades} ${
                  unidades === 1 ? "unidad" : "unidades"
                } en el carro`}
                className="ms-2 rounded-full bg-orange-600 text-white text-sm px-2 py-1"
              >
                {unidades}
              </span>
            )}
          </NavLink>
          {usuario ? (
            <>
              <span
                className="text-sm text-neutral-600 truncate max-w-32"
                title={usuario.email}
              >
                {usuario.email}
              </span>
              <button
                onClick={salir}
                className="text-sm text-orange-600 font-bold min-h-11 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
              >
                Cerrar sesión
              </button>
            </>
          ) : (
            <NavLink to="/login" className={estiloLink}>
              Ingresar
            </NavLink>
          )}
        </div>
      </nav>
    </header>
  );
}
```

✅ **Mini-verificación (el contador vivo):** con el carro vacío, el navbar
no muestra badge junto a "Carro". Entra a una ficha y agrega un aroma: el
badge aparece con **1** sin recargar nada (el `aria-live` lo anuncia). Agrega
el mismo aroma otra vez: **2** — unidades, no ítems. Clic en "Carro": la
página del paso 4. Vacía en dos pasos: el badge desaparece — oculto en 0,
otra vez.

---

## Paso 8 — La prueba de fuego: el carro que sobrevive (CART-02)

Con ambos servidores corriendo y algo en el carro. Los cuatro momentos:

✅ **Mini-verificación (RF-11: F5 y sigue vivo):** con 2 aromas en el carro,
presiona **F5** en `/carro`: las filas siguen ahí y el badge del navbar
muestra las mismas unidades DESDE EL PRIMER render — `maura-carro` hidrató
síncrono, como la sesión en la guía 6. Cierra la pestaña, ábrela de nuevo y
vuelve a `/carro`: intacto. Sin cuenta, sin sesión, sin pedir nada — el
carro es del navegador (ADR-010).

✅ **Mini-verificación (el tope del stepper):** elige un aroma con stock bajo
(**Rosa de Río**, `florales-03`, stock 2) y agrega 2 desde su ficha (el
botón se deshabilita con el helper). En `/carro`, el "+" de su fila está
deshabilitado — el stock vigente manda (RN-09). Ahora castigo el tapado:
con la fila en 2, EDITA `maura-carro` en DevTools cambiando su cantidad a 5,
guarda y recarga: la fila muestra **2**, el total cobra 2 × el precio Y el
ajuste se guardó — al llegar la hidratación, `maura-carro` vuelve a valer 2
y el badge del navbar corrige a **2**: pantalla, store y badge dicen lo
mismo. La pantalla nunca prometió las 5 — y ahora tampoco las guarda.

✅ **Mini-verificación (la fila degradada):** en DevTools → Local Storage →
`maura-carro`, agrega a mano un ítem imposible —
`{"producto_id":999,"cantidad":1}` dentro de `items` — guarda y recarga
`/carro`: la fila del 999 muestra "Este aroma ya no está disponible" con
"Quitar", SIN stepper… y el resto del carro sigue operando normalmente (el
404 de la hidratación, distinguido del error de red con el `ApiError` de la
guía 4). Quita la fila degradada y todo vuelve a la normalidad.

✅ **Mini-verificación (el error general):** DETÉN el backend y recarga
`/carro`: "No pudimos cargar tu carro" con la causa del puerto 8000 y el
botón "Reintentar" — el mismo bloque de siempre. Vuelve a encender el
backend y clic en "Reintentar": el carro regresa sin recargar la página.

---

## ❌ El error que este archivo evita

**1. Guardar el precio en el store.**

```typescript
// ❌ El precio guardado es una foto vieja: si la dueña lo mueve, el carro
// miente — y un atacante puede editarlo a mano antes del checkout
items: [{ producto_id: 1, cantidad: 2, precio: 7990 }]

// ✅ Solo pares {producto_id, cantidad}; el precio se mira SIEMPRE a la API
items: [{ producto_id: 1, cantidad: 2 }]
```

La fuente de la verdad de los precios es la API (RN-08). El navegador que
guarda precios termina DECIDIÉNDOLOS — y la etapa 3 desconfiará del cliente
justo por eso: cuando el backend recalcule la orden (CART-03), este carro
que jamás guardó precios no tendrá nada que corregir.

**2. El `confirm` del navegador para vaciar.**

```tsx
// ❌ Un diálogo bloqueante del navegador: no se estila, no se prueba y no
// se enseña nada de React
if (window.confirm("¿Vaciar todo el carro?")) vaciar();

// ✅ Estado de confirmación en dos pasos, inline en la misma zona
const [confirmando, setConfirmando] = useState(false);
```

El `window.confirm` congela la página, no se puede estilizar y mezcla la
pregunta con el chrome del navegador. El booleano `confirmando` enseña el
patrón que las acciones destructivas futuras replican: el primer clic
pregunta en el lugar, el segundo actúa.

**3. El queryKey con otro tipo.**

```typescript
// ❌ La ficha guardó ("producto", "1") — string del useParams. Con número:
// ("producto", 1) es OTRA caché; el carro vuelve a consultar lo que la
// ficha ya tenía
queryKey: ["producto", item.producto_id]

// ✅ El mismo key, la misma caché: String(id)
queryKey: ["producto", String(item.producto_id)]
```

TanStack Query compara los keys por estructura y tipo: `1 !== "1"`. El
detalle es invisible hasta que abres la pestaña de red y ves la misma
consulta dos veces.

---

## ✅ Verificación de la guía 7

Con ambos servidores corriendo y el seed hecho:

1. La ficha de un aroma con stock agrega con merge: dos clics → una fila,
   cantidad 2 — y `maura-carro` en localStorage guarda SOLO
   `producto_id` y `cantidad` (D-27).
2. **/carro** con ítems: filas con foto, badge de familia, nombre enlazado,
   precio `c/u` hidratado, stepper, total de línea y panel con el Total que
   calza con la suma (RF-10).
3. **F5** y cierre/retorno de pestaña: el carro y el badge siguen intactos,
   sin cuenta (RF-11, CART-02).
4. Al tope del stock: la ficha deshabilita "Agregar al carro" con su
   helper, y el "+" del carro se deshabilita en el stock vigente (RN-09,
   D-30).
5. "Quitar" sin confirmación; "Vaciar carro" en dos pasos inline; el
   estado vacío reemplaza la página con "Ver catálogo".
6. Ítem imposible sembrado a mano → fila degradada "Este aroma ya no está
   disponible" + "Quitar" (hidratación tolerante).
7. `npm run build` pasa — con `useQueries` hidratando por ítem y el mismo
   `queryKey` de la ficha.

## 📝 Punto de control (respóndelas sin mirar la guía)

1. ¿Qué guarda exactamente `maura-carro` y qué JAMÁS debería guardar? ¿Qué
   gana la etapa 3 con que el carro haya nacido sin precios (CART-03)?
2. La clienta tiene 5 unidades guardadas de un aroma cuyo stock bajó a 2:
   ¿qué muestra el stepper, qué cobra el total — y quién tendrá la última
   palabra cuando confirme la compra en la etapa 3?
3. ¿Por qué "Vaciar carro" confirma en dos pasos y "Quitar" no? ¿Qué es un
   "estado de confirmación" y por qué se prefiere antes que un modal?

## Lo que acabas de aprender

- El store del carro con `persist` bajo `maura-carro`: solo pares
  `{producto_id, cantidad}` con `partialize` — sin precios jamás, porque la
  fuente de la verdad de precios es la API (ADR-010, D-27, RN-08)
- El botón "Agregar al carro" viviendo solo en la ficha (D-29), con tope al
  stock y su helper — y el badge del navbar como feedback vivo
- `useQueries`: un número variable de queries en paralelo, una por ítem — y
  la caché compartida con la ficha gracias al mismo `queryKey` (con
  `String(id)`)
- La hidratación tolerante: fila esqueleto sin shift, fila degradada por 404
  (reusando el `ApiError` de la guía 4) y badge "Agotado" sin stepper — el
  resto del carro sigue operando
- El tapado al stock (D-30/RN-09): `Math.min(cantidad, stock)` en el
  stepper y en el total, y el ajuste escrito de vuelta al store al hidratar
  — pantalla, badge y `localStorage` dicen lo mismo; primera barrera hoy,
  segunda barrera en el backend de la etapa 3
- La confirmación destructiva en dos pasos inline: el patrón que las
  acciones futuras replican, sin modal ni `window.confirm`
- El badge que cuenta unidades totales (no ítems), oculto en 0 y anunciado
  con `aria-live` (D-28)

**Siguiente:** guia-08-checkout.md — el checkout protegido: la pantalla que
exige sesión con el resumen listo para pagar, y la Gran verificación final
que cierra la fase 2 comparando el contrato 0.2.0 contra `/docs`.
