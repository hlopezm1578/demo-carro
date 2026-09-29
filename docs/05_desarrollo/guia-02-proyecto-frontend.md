# Guía 2 — El proyecto frontend: la SPA con la landing de Maura

> **Qué construirás hoy:** el proyecto del tier cliente de Maura — una SPA
> React con TypeScript, desde el scaffold hasta la landing con identidad de
> marca, la navegación y las cuatro rutas de la tienda.
> **Al terminar tendrás:** `http://localhost:5173` mostrando la landing de
> Maura (STORE-01), el layout compartido y las 4 rutas vivas — y el catálogo
> mostrando honestamente su estado de error hasta que la guía 4 le dé datos.
> **Necesitas:** Node.js >= 22.22 y el backend de la guía 1 corriendo
> (`uv run fastapi dev app/main.py` en la otra terminal).

---

## Los términos de hoy (antes de copiar nada)

| Término | Qué es, en una frase |
|---|---|
| **SPA** | Single-Page Application: una sola página HTML donde JavaScript cambia la pantalla sin recargar — todo el render es del cliente (ADR-002) |
| **Scaffold / template** | El andamio inicial que genera una herramienta: `npm create vite` crea el proyecto React + TypeScript completo en segundos |
| **TypeScript** | JavaScript con tipos verificados en compilación. Aquí los tipos **espejan a mano** el contrato de la API (ADR-004) |
| **Proxy de desarrollo** | El servidor de Vite reenvía las rutas `/api` al backend en el puerto 8000: en desarrollo la SPA siempre habla con su propio origen |
| **Providers** | Componentes de React que envuelven la app y le entregan un contexto: router, cliente de datos |
| **Server state** | El estado que viene del servidor (el catálogo): tiene caché, carga y error. Se administra con TanStack Query, no con `useState` |

---

## Paso 1 — PREREQUISITO: tu versión de Node (no lo saltees)

🧠 **El desarrollador piensa:** *antes del primer comando npm verifico el
runtime. `react-router` versión 8 — nuestro router — declara en sus
`engines` que requiere Node >= 22.22.0: por debajo de eso, `npm install`
falla con el warning `EBADENGINE` y un proyecto inválido. No es un capricho
del paquete: es un contrato de versión igual al techo de Python 3.12 que
fijamos en el backend — cada tier declara el runtime que necesita. Y ojo:
esta verificación es **tuya**, corre en tu máquina; la guía no puede
hacerla por ti (ni ningún tutorial: cualquier "funciona en mi máquina"
empieza exactamente aquí).*

En tu terminal, ejecuta:

```
node -v
```

Debe imprimir `v22.22.0` o mayor (por ejemplo `v22.24.0` o `v24.x.x`). Si
imprime menos (v22.18, v20…), actualiza Node **antes de continuar**:

- Instala la LTS desde [nodejs.org](https://nodejs.org) (el instalador de
  Windows), o
- usa `nvm-windows` si prefieres administrar varias versiones.

Instalar un runtime en tu máquina es decisión tuya: la guía te deja el
requisito, cómo comprobarlo y nada más. Cierra y reabre la terminal después
de instalar (para que pickée el nuevo `node` del PATH).

✅ **Mini-verificación:** `node -v` imprime `v22.22.0` o mayor. Anota el
número: es parte del entorno que tu proyecto asume.

---

## Paso 2 — El scaffold de Vite (react-ts)

🧠 **El desarrollador piensa:** *scaffold con el template `react-ts`: React 19
+ TypeScript ya configurado, con las versiones que el template valida en
conjunto. La tentación es "mejorarle" la versión de TypeScript a la última —
no lo hagas: el template fija `~6.0.2` porque es la combinación probada con
Vite 8 y React 19 (la 7.x es demasiado nueva). TypeScript **no se instala
aparte**: ya viene en el template, con su versión correcta. Mis únicas
decisiones de hoy son el nombre de la carpeta (`frontend`, la hermana de
`backend/` en el monorepo, ADR-003) y el template (`react-ts`, ADR-004).*

Desde la raíz de tu monorepo (donde está `backend/`), ejecuta:

```
npm create vite@latest frontend -- --template react-ts
```

Entra a la carpeta e instala las dependencias del scaffold:

```
cd frontend
npm install
```

✅ **Mini-verificación:** abre `frontend/package.json`: en `dependencies`
figura `"react": "^19.3.0"` (o 19.x) y en `devDependencies`
`"typescript": "~6.0.2"`. Si quieres adelantar la recompensa: `npm run dev`
muestra la página de demo de Vite en `http://localhost:5173` (detén con
`Ctrl+C`; la volveremos a encender más adelante).

---

## Paso 3 — Router, datos y estilo: las tres instalaciones

🧠 **El desarrollador piensa:** *tres comandos, tres decisiones de
arquitectura. **Router:** `react-router` versión 8 en *library mode* —
declarativo, `BrowserRouter` — que es el modo que el stack fijó para esta SPA.
**Datos:** `@tanstack/react-query` para el *server state* — el catálogo vive
en el servidor, y su caché, su carga y sus errores se administran con `useQuery`,
no a mano con `useState` (el estado del cliente —otra cosa— llegará con el
carro en una fase próxima). **Estilo:** Tailwind 4 como plugin de Vite — en
esta versión no hay archivo de configuración ni PostCSS: se instala y se
importa. Y la fuente: Nunito, la tipografía redondeada de la marca, la
instalo como paquete npm **self-hosted** — cero requests a servidores de
fuentes de terceros cuando la tienda corra (la misma independencia que
exigimos para las fotos de producto, RN-03).*

Desde `frontend/`, ejecuta los tres comandos (uno por línea):

```
npm install react-router @tanstack/react-query
npm install tailwindcss @tailwindcss/vite
npm install @fontsource-variable/nunito
```

✅ **Mini-verificación:** `frontend/package.json` ahora lista, en
`dependencies`: `react-router`, `@tanstack/react-query`, `tailwindcss`,
`@tailwindcss/vite` y `@fontsource-variable/nunito`.

---

## Paso 4 — `vite.config.ts`: plugins y proxy `/api`

🧠 **El desarrollador piensa:** *el navegador solo puede hablar a un origen
distinto del suyo si el servidor lo autoriza (CORS — ya lo configuramos en el
backend con lista explícita). Pero en desarrollo hay un truco mejor: el
**proxy**. Le digo a Vite "todo lo que empiece con `/api` reenvíalo a
`http://localhost:8000`". Así la SPA siempre pide `/api/...` a **su propio
origen**, el proxy lo reenvía al backend, y el código del frontend no conoce
ninguna URL cruzada: no hay CORS que resolver en dev, y el mismo código sirve
en producción cambiando una variable de entorno (`VITE_API_URL`, que
`lib/api.ts` leerá con un default vacío). Menos configuración, mismo
comportamiento en los dos mundos (ADR-002).*

Reemplaza **`frontend/vite.config.ts`** completo:

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: { "/api": "http://localhost:8000" },
  },
});
```

---

## Paso 5 — Identidad: `index.html` y la fuente de la marca

Abre **`frontend/index.html`** y déjalo así — dos cambios: el idioma de la
página (`es`) y el título con la marca:

```html
<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Maura · Body Splash</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

Y reemplaza **`frontend/src/index.css`** completo — aquí vive el contrato
visual base: Tailwind importado como una línea, la fuente Nunito self-hosted
importada del paquete npm, y el bloque `@theme` que declara la tipografía de
la marca (dirección visual: fresco y luminoso, tipografía redondeada —
docs/03_diseno.md §4.1):

```css
@import "tailwindcss";
@import "@fontsource-variable/nunito";

@theme {
  --font-sans: "Nunito Variable", system-ui, sans-serif;
}
```

Eso es toda la configuración de estilos del proyecto: Tailwind 4 no tiene
`tailwind.config.js` — el `@theme` reemplaza al archivo de configuración de
las versiones anteriores.

✅ **Mini-verificación:** `npm run dev` arranca sin errores y
`http://localhost:5173` sigue mostrando la página del template — ahora
escrita con la tipografía redondeada Nunito (compárala con la fuente del
sistema: se nota en la página de bienvenida de Vite).

---

## Paso 6 — `main.tsx`: providers, rutas y limpieza

🧠 **El desarrollador piensa:** *el orden de los providers importa y cuenta una
historia: `StrictMode` (desarrollo) envuelve todo; dentro, el
`QueryClientProvider` instala el cliente de datos que cualquier pantalla podrá
usar; dentro de él, el `BrowserRouter` instala el router que cualquier
componente podrá consultar. De afuera hacia adentro: primero las capacidades
globales, al final las rutas que las usan. Y una regla de la versión 8 que no
admite excepciones: **todos los imports del router salen del paquete
`react-router`**. La versión 8 eliminó el paquete separado que existía hasta
la versión 7 (`react-router-dom`): si copias una línea de import de ese
paquete de un tutorial viejo, el build falla con "package not found". Ese
nombre solo va a aparecer una vez más en esta guía — en la advertencia del
final —, jamás en nuestro código.*

Reemplaza **`frontend/src/main.tsx`** completo:

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
            <Route path="*" element={<NoEncontrado />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>
);
```

Fíjate en el `import "./index.css"`: es la línea que mantiene vivos los
estilos del paso 5. El template la traía y un reemplazo descuidado la
pierde — y su ausencia **no da ningún error**: la app compila, corre y se
ve sin un solo estilo, sin que nadie te avise. Un CSS que ningún módulo
importa simplemente no entra al bundle.

Fíjate en las cuatro rutas de la tienda (docs/03_diseno.md §4): `/` la
landing, `/productos` el catálogo, `/productos/:id` la ficha, y `*` la
página 404. El `<Route element={<Layout />}>` sin `path` es una **ruta
layout**: envuelve a las otras y les presta la Navbar y el Footer (lo
construimos en el paso 9).

Los componentes importados aún no existen: créalos **como stubs mínimos**
para que el proyecto compile — el mismo truco de la guía 1 con el paquete
`app/`: primero la estructura, luego el contenido. Crea estos cinco archivos
con esta forma (cambiando el nombre del componente en cada uno):

```
src/components/Layout.tsx             → export default function Layout()
src/features/landing/Landing.tsx      → export default function Landing()
src/features/catalogo/Catalogo.tsx    → export default function Catalogo()
src/features/catalogo/FichaProducto.tsx → export default function FichaProducto()
src/features/catalogo/NoEncontrado.tsx  → export default function NoEncontrado()
```

```tsx
export default function Landing() {
  return <main className="p-6">Landing — la construimos en el paso 10</main>;
}
```

Y ahora sí: **borra** `src/App.tsx`, `src/App.css` y `src/react.svg` —
demostraciones del template que ya nadie importa (fíjate que el nuevo
`main.tsx` no las menciona).

✅ **Mini-verificación:** desde `frontend/`, ejecuta:

```
npm run build
```

Termina sin errores: TypeScript compiló el proyecto completo y el router
encontró sus cinco componentes. Y mira dentro de `dist/assets/`: debe
existir un archivo `index-*.css` — es tu `index.css` (Tailwind + Nunito)
empaquetado. Si no está, el `import "./index.css"` se perdió y tu app se
vería sin estilos sin ningún error de por medio. (El build también valida
lo que el dev server perdonaría — por eso lo corremos como verificación,
no solo el `npm run dev`.)

---

## Paso 7 — `types/api.ts`: el espejo del contrato

🧠 **El desarrollador piensa:** *este archivo es el ejercicio pedagógico del
día (ADR-004). Abro `contrato_api.yaml` (fase 4 del ciclo) y traduzco sus
schemas a TypeScript **a mano**: cada campo, cada tipo, cada `required`. Sin
generación automática — a propósito: al escribir `familia: Familia` con
`Familia = "citricas" | ...` acabo de leer la regla RN-01 en dos idiomas, el
del contrato y el del compilador. Y el mapa `FAMILIA_LABELS` resuelve la
pega más fina de la RN-01: por el cable viaja el slug sin acentos
(`citricas`), la pantalla muestra la etiqueta con acento ("Cítricas") —
el traductor vive en el cliente, en un solo lugar.*

Crea **`frontend/src/types/api.ts`**:

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
```

✅ **Mini-verificación:** experimento del compilador — agrega al final del
archivo esta línea con un typo (sin la "s" final):

```typescript
const familiaMala: Familia = "citrica";
```

`npm run build` **falla** con algo como
`Type '"citrica"' is not assignable to type 'Familia'` — el compilador acaba
de impedir que un slug mal escrito llegue a la pantalla. Ahora **borra la
línea** y el build vuelve a pasar. Eso — atrapar el error en compilación y
no en la cara de la clienta — es todo lo que TypeScript aporta a este
proyecto.

---

## Paso 8 — `lib/api.ts`: el único punto de salida HTTP

🧠 **El desarrollador piensa:** *regla de la arquitectura (ADR-002): ningún
componente hace `fetch` por su cuenta — TODO el HTTP del frontend sale de
este archivo. ¿Por qué tan estricto? Porque el día que llegue el token JWT
(fase de cuentas), el header de autorización se agrega en **un** lugar;
cuando cambiemos la base URL para producción, cambia en **un** lugar; cuando
un endpoint responda 401, se decide qué hacer en **un** lugar. El helper
devuelve el JSON tipado (`apiGet<T>`) y traduce los errores del contrato: si
la respuesta no es `ok`, busca el `detail` del cuerpo — el formato de error
que el contrato define — y lo lanza como `Error`, para que TanStack Query lo
presente.*

Crea **`frontend/src/lib/api.ts`**:

```typescript
const base = import.meta.env.VITE_API_URL ?? "";

export async function apiGet<T>(ruta: string): Promise<T> {
  const res = await fetch(`${base}/${ruta}`);
  if (!res.ok) {
    let mensaje = `Error HTTP ${res.status}`;
    try {
      const cuerpo = await res.json();
      if (cuerpo?.detail) mensaje = cuerpo.detail;
    } catch {
      // El cuerpo no traía JSON: nos quedamos con el mensaje genérico
    }
    throw new Error(mensaje);
  }
  return res.json();
}
```

`VITE_API_URL` es una variable de entorno de Vite: vacía (o ausente) en
desarrollo — el proxy hace el trabajo — y la URL pública de la API en
producción (fase de despliegue).

✅ **Mini-verificación:** `npm run build` sigue pasando. Bonus de
comprensión: en `apiGet`, ¿qué pasaría si el backend respondiera 404 con
`{"detail": "Producto no encontrado"}`? Sigue la función con el dedo: `res.ok`
es falso → busca `detail` → lanza `Error("Producto no encontrado")`. Ese
camino lo verás funcionar en la guía 4.

---

## Paso 9 — El layout compartido: Navbar, Footer y Layout

Las pantallas de la tienda comparten marco (docs/03_diseno.md §4.1): una
barra de navegación pegada arriba, el contenido al medio y un pie discreto.
Crea **`frontend/src/components/Navbar.tsx`**:

```tsx
import { Link, NavLink } from "react-router";

const estiloLink = ({ isActive }: { isActive: boolean }) =>
  `text-sm min-h-11 flex items-center focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none ${
    isActive ? "text-orange-600 font-bold" : "text-neutral-600"
  }`;

export default function Navbar() {
  return (
    <header className="sticky top-0 bg-orange-50 border-b border-orange-100">
      <nav className="max-w-6xl mx-auto flex items-center justify-between gap-4 px-4 py-2">
        <Link
          to="/"
          className="text-xl font-bold text-neutral-900 truncate focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
        >
          Maura · Body Splash
        </Link>
        <div className="flex gap-4">
          <NavLink to="/" end className={estiloLink}>
            Inicio
          </NavLink>
          <NavLink to="/productos" className={estiloLink}>
            Catálogo
          </NavLink>
        </div>
      </nav>
    </header>
  );
}
```

Crea **`frontend/src/components/Footer.tsx`**:

```tsx
export default function Footer() {
  return (
    <footer className="bg-orange-50">
      <p className="max-w-6xl mx-auto px-4 py-4 text-sm text-neutral-600">
        Maura · Body Splash — proyecto educativo · 2026
      </p>
    </footer>
  );
}
```

Y reemplaza el stub de **`frontend/src/components/Layout.tsx`** — la ruta
layout de `main.tsx` renderiza `<Outlet />` (el "contenido de la página
actual") entre la Navbar y el Footer:

```tsx
import { Outlet } from "react-router";
import Navbar from "./Navbar";
import Footer from "./Footer";

export default function Layout() {
  return (
    <div className="flex min-h-screen flex-col bg-white">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
```

✅ **Mini-verificación:** `npm run dev` y abre
`http://localhost:5173/productos` (el stub): la barra naranja pálida con
**Maura · Body Splash** y los links Inicio/Catálogo aparece arriba — pegada
al borde si haces scroll — y el footer con la línea de proyecto educativo
aparece abajo, **en cualquier ruta**. Ese es el trabajo de la ruta layout.

---

## Paso 10 — La landing de Maura (STORE-01)

🧠 **El desarrollador piensa:** *la landing es la identidad de la marca hecha
pantalla (docs/01_necesidad: quién es Maura; docs/03_diseno.md §4.2: cómo se
ve). Tres decisiones de copy ya están tomadas y no se negocian en código: el
**eyebrow** presenta la marca, el título es el tagline exacto —"Frescura que
te acompaña"— y el párrafo es Maura hablando en primera persona (esa misma
voz la heredará la asistente de IA en una fase próxima). El botón principal
usa el naranja de acento — la paleta es blanco dominante, naranja pálido de
fondo, acento naranja — y la sección de familias muestra las cuatro
categorías aromáticas del catálogo (RN-01), cada una con su link hacia el
catálogo filtrado. Las cards repiten el patrón de badge + nombre +
descripción que usará el catálogo: componentes que enseñan un patrón que
vuelve.*

Reemplaza el stub de **`frontend/src/features/landing/Landing.tsx`**:

```tsx
import { Link } from "react-router";
import { FAMILIA_BADGES, FAMILIA_LABELS, type Familia } from "../../types/api";

const FAMILIAS: { slug: Familia; descripcion: string; href: string }[] = [
  {
    slug: "citricas",
    descripcion: "Frescas y chispeantes, para despertar.",
    href: "/productos?familia=citricas",
  },
  {
    slug: "florales",
    descripcion: "Suaves y románticas, de flor a flor.",
    href: "/productos?familia=florales",
  },
  {
    slug: "frutales",
    descripcion: "Dulces y jugosas, puro verano.",
    href: "/productos?familia=frutales",
  },
  {
    slug: "dulces",
    descripcion: "Cálidas y reconfortantes, con alma de repostería.",
    href: "/productos?familia=dulces",
  },
];

export default function Landing() {
  return (
    <div>
      <section className="bg-orange-50 py-16">
        <div className="max-w-xl mx-auto px-4 text-center">
          <p className="text-sm tracking-wide text-neutral-600">
            Maura · Body Splash
          </p>
          <h1 className="text-4xl font-bold tracking-tight text-neutral-900">
            Frescura que te acompaña
          </h1>
          <p className="text-base leading-normal text-neutral-600">
            Soy Maura. Hago body splash a mano, en lotes pequeños, con
            esencias frescas que elijo una por una. Esta tienda nace para que
            encuentres tu aroma desde cualquier parte de Chile, sin
            intermediarios.
          </p>
          <Link
            to="/productos"
            className="mt-6 inline-block bg-orange-600 text-white font-bold rounded-full px-6 py-2 min-h-11 hover:bg-orange-700 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
          >
            Ver catálogo
          </Link>
        </div>
      </section>

      <section className="py-12">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-xl font-bold text-neutral-900">
            Nuestras familias
          </h2>
          <div className="mt-6 grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {FAMILIAS.map((f) => (
              <div
                key={f.slug}
                className="bg-white rounded-2xl border border-orange-100 p-6"
              >
                <span
                  className={`text-sm rounded-full px-2 py-1 ${FAMILIA_BADGES[f.slug]}`}
                >
                  {FAMILIA_LABELS[f.slug]}
                </span>
                <p className="mt-2 text-xl font-bold text-neutral-900">
                  {FAMILIA_LABELS[f.slug]}
                </p>
                <p className="text-sm text-neutral-600">{f.descripcion}</p>
                <Link
                  to={f.href}
                  className="mt-2 inline-block text-sm text-orange-600 min-h-11 flex items-center focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
                >
                  Ver aromas →
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
```

Nota el patrón `FAMILIA_LABELS[f.slug]`: el badge y el título muestran la
**etiqueta** con acento, pero el `href` viaja con el **slug** sin acentos —
la RN-01 funcionando en una sola card.

✅ **Mini-verificación:** abre `http://localhost:5173/` — el hero muestra el
eyebrow "Maura · Body Splash", el tagline "Frescura que te acompaña" en
grande, el párrafo de Maura en primera persona y el botón naranja "Ver
catálogo" (clic: te lleva al catálogo). Abajo, "Nuestras familias" con las
cuatro cards y sus links "Ver aromas →" — cada uno lleva al catálogo con el
filtro de su familia ya escrito en la dirección (lo verás trabajar en la
guía 4, cuando existan productos que filtrar).

---

## Paso 11 — El catálogo mínimo (y su error honesto)

🧠 **El desarrollador piensa:** *toca la pantalla que habla con la API — pero
el endpoint de productos TODAVÍA no existe: se construye en la guía 4. ¿Y
qué hace una pantalla cuando su dato no está? No se cuelga: muestra sus
**estados**. Este es el momento en que los estados async dejan de ser
teoría: `isPending` muestra esqueletos, `isError` muestra el bloque de error
con Reintentar. Abrir `/productos` hoy y ver el error controlado —con su
mensaje y su botón, sin pantalla en blanco— es la primera lección viva de
por qué usamos TanStack Query en vez de un `useEffect` con banderas a mano.
El precio se formatea con `Intl.NumberFormat` es-CL CLP (RN-02): el peso
chileno no lleva decimales y el formateo es del navegador, no de nosotros
concatenando signos.*

Reemplaza el stub de **`frontend/src/features/catalogo/Catalogo.tsx`**:

```tsx
import { useQuery } from "@tanstack/react-query";
import { apiGet } from "../../lib/api";
import type { ProductoResumen } from "../../types/api";
import ProductCard from "./ProductCard";

export default function Catalogo() {
  const query = useQuery({
    queryKey: ["productos"],
    queryFn: () => apiGet<ProductoResumen[]>("api/productos"),
  });

  if (query.isPending) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {Array.from({ length: 8 }).map((_, i) => (
          <div
            key={i}
            className="aspect-square animate-pulse bg-neutral-200 rounded-2xl"
          />
        ))}
      </div>
    );
  }

  if (query.isError) {
    return (
      <div className="max-w-xl mx-auto px-4 py-16 text-center">
        <h1 className="text-xl font-bold text-neutral-900">
          No pudimos cargar el catálogo
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

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-xl font-bold text-neutral-900">Nuestros aromas</h1>
      <p className="mt-1 text-sm text-neutral-600">
        {query.data.length} aromas
      </p>
      <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {query.data.map((producto) => (
          <ProductCard key={producto.id} producto={producto} />
        ))}
      </div>
    </div>
  );
}
```

Crea **`frontend/src/features/catalogo/ProductCard.tsx`**:

```tsx
import { Link } from "react-router";
import { FAMILIA_BADGES, FAMILIA_LABELS, type ProductoResumen } from "../../types/api";

const clp = new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP" });

export default function ProductCard({ producto }: { producto: ProductoResumen }) {
  return (
    <Link
      to={`/productos/${producto.id}`}
      className="block bg-white rounded-2xl border border-orange-100 overflow-hidden hover:shadow-md transition-shadow focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
    >
      <img
        src={producto.imagen}
        alt={producto.nombre}
        loading="lazy"
        className="aspect-square w-full object-cover bg-neutral-200"
      />
      <div className="p-4">
        <span
          className={`text-sm rounded-full px-2 py-1 ${FAMILIA_BADGES[producto.familia]}`}
        >
          {FAMILIA_LABELS[producto.familia]}
        </span>
        <p className="mt-2 text-xl font-bold text-neutral-900 line-clamp-2">
          {producto.nombre}
        </p>
        <p className="mt-1 text-base font-bold text-neutral-900">
          {clp.format(producto.precio)}
        </p>
      </div>
    </Link>
  );
}
```

Reemplaza el stub de **`frontend/src/features/catalogo/FichaProducto.tsx`**
— versión mínima: la ficha completa (notas, stock, volver) la arma la guía 4;
hoy importa la misma estructura de estados:

```tsx
import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router";
import { apiGet } from "../../lib/api";
import { FAMILIA_LABELS, type ProductoDetalle } from "../../types/api";

const clp = new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP" });

export default function FichaProducto() {
  const { id } = useParams();

  const query = useQuery({
    queryKey: ["producto", id],
    queryFn: () => apiGet<ProductoDetalle>(`api/productos/${id}`),
  });

  if (query.isPending) {
    return (
      <div className="max-w-3xl mx-auto p-6 grid md:grid-cols-2 gap-8">
        <div className="aspect-square animate-pulse bg-neutral-200 rounded-2xl" />
        <div className="space-y-4">
          <div className="h-6 w-24 animate-pulse bg-neutral-200 rounded-full" />
          <div className="h-8 w-3/4 animate-pulse bg-neutral-200 rounded-2xl" />
          <div className="h-4 w-1/2 animate-pulse bg-neutral-200 rounded-2xl" />
        </div>
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
    <div className="max-w-3xl mx-auto p-6 grid md:grid-cols-2 gap-8">
      <img
        src={producto.imagen}
        alt={producto.nombre}
        className="rounded-2xl aspect-square object-cover bg-neutral-200 w-full"
      />
      <div>
        <p className="text-sm text-neutral-600">
          {FAMILIA_LABELS[producto.familia]}
        </p>
        <h1 className="mt-1 text-xl font-bold text-neutral-900">
          {producto.nombre}
        </h1>
        <p className="mt-2 text-xl font-bold text-neutral-900">
          {clp.format(producto.precio)}
        </p>
        <p className="mt-4 text-base text-neutral-600">
          {producto.descripcion}
        </p>
      </div>
    </div>
  );
}
```

Y reemplaza el stub de **`frontend/src/features/catalogo/NoEncontrado.tsx`**:

```tsx
import { Link } from "react-router";

export default function NoEncontrado() {
  return (
    <div className="max-w-xl mx-auto px-4 py-16 text-center">
      <h1 className="text-xl font-bold text-neutral-900">
        Página no encontrada
      </h1>
      <p className="mt-2 text-sm text-neutral-600">
        El enlace no existe o cambió.
      </p>
      <Link
        to="/"
        className="mt-6 inline-flex items-center text-sm text-orange-600 min-h-11 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
      >
        Volver al inicio
      </Link>
    </div>
  );
}
```

✅ **Mini-verificación:** abre `http://localhost:5173/productos`: verás el
bloque "No pudimos cargar el catálogo" con el botón **Reintentar** —
**comportamiento esperado**: el endpoint aún no existe. Detén el backend de
la guía 1 y vuelve a cargar: mismo error. El estado de error no distingue
"no existe el endpoint" de "el backend está apagado" — solo dice, con su
causa probable, "revisa el puerto 8000". Ese detalle lo afinaremos cuando
el endpoint exista.

---

## Paso 12 — ✅ Verificación de la guía 2 (con los dos tiers)

Enciende los dos servidores, cada uno en su terminal:

- Terminal 1, en `backend/`: `uv run fastapi dev app/main.py`
- Terminal 2, en `frontend/`: `npm run dev`

Ahora, en tu navegador:

1. **http://localhost:5173/** → la landing de Maura: eyebrow, tagline
   "Frescura que te acompaña", párrafo de Maura, botón "Ver catálogo" y las
   cuatro familias (STORE-01).
2. **http://localhost:5173/productos** → el estado de error controlado con
   "Reintentar" — correcto hasta la guía 4: el catálogo sin datos es la
   pantalla esperada, y no una página rota.
3. **http://localhost:5173/esta-ruta-no-existe** → la 404 propia: "Página no
   encontrada" con su link "Volver al inicio".

---

## ❌ El error que este archivo evita

**1. Importar del paquete de router eliminado en la versión 8.** Hasta
react-router 7 existían dos paquetes: el core y el paquete "dom". La versión
8 los fusionó: **todo** sale de `react-router`. Si copias de un tutorial
viejo una línea de import del paquete `react-router-dom`, `npm run build`
falla con algo como `Cannot find module 'react-router-dom'` — o peor,
`npm install` te instala la versión 7 antigua y el proyecto queda en un
mundo de versiones que nadie probó. La línea correcta — la única que
usamos — es:

```tsx
import { BrowserRouter, Routes, Route, Link, NavLink, useParams, Outlet } from "react-router";
```

**2. Subir TypeScript a la versión "latest".** El template lo fija en
`~6.0.2` a propósito: es la versión validada con Vite 8 y React 19. Un
`npm install typescript@latest` sube a la 7.x recién salida y desalinea el
proyecto del andamio probado — el mismo error conceptual que instalar una
versión de Python fuera del techo de la guía 1. Regla: las versiones las
fija el template y los techos del proyecto, no la ansiedad de la versión
nueva.

---

## 📝 Punto de control (respóndelas sin mirar la guía)

1. ¿Para qué sirve el proxy de `/api` en `vite.config.ts`? ¿Qué tendrías que
   cambiar si en producción la API vive en otra URL — y en cuántos archivos?
2. ¿Por qué `fetch` está prohibido en los componentes y solo vive en
   `lib/api.ts`? Nombra dos cosas que será fácil hacer cuando llegue la fase
   de cuentas JWT gracias a esa regla.
3. ¿Por qué escribimos los tipos a mano en `types/api.ts` en vez de
   generarlos automáticamente desde el contrato? ¿Qué aprende el alumno
   escribiéndolos que no aprendería generándolos?

## Lo que acabas de aprender

- Verificar y gatear tu runtime antes del primer comando (Node >= 22.22 por los engines del router)
- Scaffold react-ts de Vite: qué fija el template y qué no se toca (TypeScript incluido)
- Tailwind 4 como plugin de Vite: cero configuración, fuente self-hosted con `@theme`
- El proxy de desarrollo: same-origin en dev, `VITE_API_URL` en producción
- Providers en orden y las cuatro rutas de la tienda en library mode
- El espejo manual del contrato en TypeScript — y cómo el compilador atrapa un slug mal escrito (RN-01, ADR-004)
- `apiGet` como único punto de salida HTTP, con los errores del contrato
- La landing de marca completa (STORE-01) y los estados async como primera ciudadanía

**Siguiente:** guia-03-modelos-y-seed.md — le damos memoria al backend: la
tabla `productos`, el modelo con familia y notas, y el seed que siembra los
12 aromas demo sin duplicar nada.
