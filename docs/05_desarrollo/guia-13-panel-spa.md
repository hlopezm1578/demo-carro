# Guía 13 — El panel (SPA): RequireAdmin, el layout de la trastienda y las tres pantallas

> **Qué construirás hoy:** la trastienda en pantalla: el guard por rol
> `RequireAdmin` con su página de no autorizado, el layout propio del panel
> con subnav, y las tres pantallas — Productos con su editor inline y el
> toggle reversible, Pedidos con la anulación en dos pasos, y Métricas con
> sus KPI. De paso, la tabla BADGES baja a su módulo propio, como la guía
> 11 lo prometió.
> **Al terminar tendrás:** la dueña administrando productos, pedidos y
> métricas de punta a punta — y una clienta que fuerza `/admin` viendo la
> pantalla de no autorizado, sin expulsión y sin pantalla rota.
> **Necesitas:** las guías 1 a 12 completas — el backend del panel
> encendido (los 7 paths admin respondiendo en `/docs` 0.4.0), las cuentas
> del seed, y la huérfana PENDING de tu fase 3 esperando su anulación.
> Abre el UI-SPEC de la fase 4 y el contrato 0.4.0 en pestañas: los copys
> y los tokens de hoy vienen de ahí.

---

## Los términos de hoy (antes de copiar nada)

| Término | Qué es, en una frase |
|---|---|
| **Guard por rol** | `RequireAdmin`: la puerta de la rama `/admin` — sin sesión delega en `RequireAuth` (login con vuelta); con sesión sin rol muestra la página de no autorizado (D-55, ADR-015) |
| **Layout con Outlet** | Un componente de ruta que dibuja el chrome (navbar, subnav) y renderea las sub-rutas donde va su `<Outlet />` — la tienda tiene uno, el panel otro |
| **Subnav** | La navegación de segundo nivel del panel (Productos · Pedidos · Métricas), blanca bajo la navbar crema — dos niveles, dos superficies |
| **Editor inline** | El formulario de producto como ESTADO de la pantalla (`editando`), no como ruta propia: no hay URL `/admin/productos/nuevo` — se abre sobre la tabla y se cierra en el lugar |
| **Badge de estado** | El tag redondo que dice la verdad del dato: BADGES para el pedido (una sola tabla desde hoy), Activo/Inactivo para el producto, Stock bajo para el umbral admin |
| **Degradación de permisos** | La diferencia entre "no te conozco" (401 → login) y "te conozco y no puedes" (403 → NoAutorizado): identidad y permiso son cosas distintas |

---

## Paso 1 — `RequireAdmin` y `NoAutorizado`: el guard que no expulsa

🧠 **El desarrollador piensa:** *el guard de sesión existe desde la guía 6 y
su lección sigue intacta: es UX, no seguridad — lo que de verdad protege al
panel es el `get_current_admin` de CADA endpoint que la guía 12 puso en el
server (ADR-015). Hoy ese patrón gana su segundo piso. **Sin sesión**,
`RequireAdmin` simplemente delega en `<RequireAuth />`: el guard viejo hace
su número completo — login con la ubicación a cuestas (returnTo genérico,
D-32) y vuelta AL PANEL tras entrar, no a la portada. Renderizar un
componente de guard DENTRO de otro no es trampa: el `<Outlet />` de
`RequireAuth` lee el contexto de rutas — que sigue siendo el de las hijas
de `RequireAdmin` — y su `<Navigate>` expulsa igual. **Con sesión pero sin
rol admin**, la decisión nueva: NO se expulsa al login — se renderiza
`NoAutorizado`. ¿Por qué? Porque a una clienta con sesión VÁLIDA no le
falta identidad, le falta permiso: mandarla al login la haría intentar
entrar con OTRA cuenta para ver la misma pantalla de rechazo. El 403 del
backend dice "te conozco y no puedes pasar"; el espejo UX dice lo mismo en
chileno: "el panel es solo para la dueña" (D-55, Pattern 4 del research).
Y ojo de dónde sale el rol: del MISMO store que lee `RequireAuth` — el
claim viaja en el token desde el primer login de la fase 2 (ADR-011), sin
segunda fuente, sin consultar la base. La importación cruzada
`components → features` (RequireAdmin importa NoAutorizado de
`features/admin`) es la excepción narrada de hoy, con la misma honestidad
del `VoucherPedido` de la guía 11 (D-46): NoAutorizado es una PANTALLA del
panel, no una pieza compartida — subirla a `components/` sería poner
territorio de un feature en el espacio de todos.*

Crea la carpeta **`frontend/src/features/admin/`** y
**`frontend/src/features/admin/NoAutorizado.tsx`**:

```tsx
// Pantalla 13 del diseño: lo que ve una clienta con sesión que fuerza
// /admin — el espejo UX del 403 backend (D-55). Contenido estático, sin
// datos que cargar: no hay nada que fetchear para decir "no puedes".
import { Link } from "react-router";

export default function NoAutorizado() {
  return (
    <main className="max-w-md mx-auto px-4 py-16 text-center">
      <h1 className="text-2xl md:text-3xl font-extrabold text-neutral-900">
        No tienes acceso al panel
      </h1>
      <p className="mt-2 text-base text-neutral-600">
        El panel de administración es solo para la dueña de la tienda.
      </p>
      <Link
        to="/"
        className="mt-6 inline-flex items-center text-sm text-orange-600 font-bold min-h-11 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
      >
        Volver a la tienda
      </Link>
    </main>
  );
}
```

Y crea **`frontend/src/components/RequireAdmin.tsx`**:

```tsx
// Guard por rol de la rama /admin (D-55, ADR-015): UX cortés, NO
// seguridad — el 403 real lo produce get_current_admin en CADA endpoint
// (guía 12). Sin sesión delega en RequireAuth (returnTo genérico D-32:
// tras el login vuelve AL PANEL); con sesión sin rol muestra
// NoAutorizado SIN expulsar: le falta permiso, no identidad.
import { Outlet } from "react-router";

import NoAutorizado from "../features/admin/NoAutorizado"; // regla 6 con razón: pantalla del panel
import { useAuthStore } from "../stores/useAuthStore";
import RequireAuth from "./RequireAuth";

export default function RequireAdmin() {
  // Se pregunta por el USUARIO, no por el token: el rol vive en el
  // usuario, y el par token+usuario se instala junto (guía 6).
  const usuario = useAuthStore((s) => s.usuario);

  if (!usuario) {
    // Sin sesión: el guard de la guía 6, entero — login con la ubicación
    // a cuestas y vuelta acá. Su <Outlet /> renderea las hijas de ESTE
    // guard porque el contexto de rutas no cambió.
    return <RequireAuth />;
  }

  if (usuario.rol !== "admin") {
    // Con sesión válida sin rol admin: la pantalla que explica, no la
    // expulsión. El claim viaja desde el primer token (ADR-011) — el
    // guard lo lee del mismo store que RequireAuth.
    return <NoAutorizado />;
  }

  return <Outlet />;
}
```

✅ **Mini-verificación:** `npm run build` pasa. Nada usa el guard todavía
— su rama llega en el paso 4, y su comportamiento se prueba de verdad en
el paso 9.

---

## Paso 2 — `src/lib/badges.ts`: la tercera consumidora cobra la nota de la guía 11

🧠 **El desarrollador piensa:** *la guía 11 dejó la promesa ESCRITA en un
comentario: "si un día nace una tercera consumidora, baja a un módulo
propio — hoy son dos y copiarla una vez más es más honesto que
adelantarse". Hoy nació: el panel de pedidos. Y la regla de la casa se
cumple igual que con `VoucherPedido` (D-46): se construye UNA vez y las
demás lo heredan — una sola verdad del estado en toda la tienda (D-45).
El refactor toca el CÓDIGO del alumno, jamás las guías viejas: las guías
10 y 11 quedan byte-intactas, porque re-editarlas rompería la trazabilidad
del corpus (la guía 11 enseñó a copiar la tabla cuando eran dos — eso fue
lo correcto ENTONCES). A los módulos nuevos: la tabla BADGES exacta, más
los badges de producto de esta etapa — Activo/Inactivo (los tonos de
"Pagado"/"Anulado": en circulación vs fuera de ella) y el de Stock bajo.
Y este último viene con SU lección de contraste: el umbral admin es ≤ 5
sobre activos (reabastecimiento, RN-14 — la constante del backend de la
guía 12), DELIBERADAMENTE distinto del "¡Últimas N unidades!" de la ficha
de tienda (stock 1-3, urgencia de compra): dos conceptos, dos constantes,
dos textos (Pitfall 6). El espejo frontend del umbral se llama
`STOCK_BAJO` y vive aquí para que badge y cuenta digan lo mismo que el
backend — si un día cambia, cambia en los dos lugares y solo en ellos.*

Crea **`frontend/src/lib/badges.ts`**:

```typescript
// La verdad del estado de un pedido, UNA vez para toda la tienda (D-45).
// Nació copiada en el voucher (guía 10), se copió al historial (guía 11)
// como segunda consumidora — y la guía 11 dejó escrito el día de hoy: la
// tercera consumidora (el panel) la baja a módulo propio. Las TRES
// consumidoras (voucher, historial, panel) importan de aquí desde hoy.
import type { EstadoPedido } from "../types/api";

export const BADGES: Record<EstadoPedido, { texto: string; clases: string }> = {
  paid: { texto: "Pagado", clases: "bg-emerald-100 text-emerald-800" },
  pending: { texto: "En curso", clases: "bg-amber-100 text-amber-800" }, // RN-11
  rejected: { texto: "Rechazado", clases: "bg-red-50 text-red-600" },
  cancelled: { texto: "Anulado", clases: "bg-neutral-200 text-neutral-700" },
};

// --- Etapa 4: los badges del panel (tokens del UI-SPEC de la fase) ---

// El estado comercial del producto (D-52): el mismo tono de "Pagado" para
// el que está en circulación y el de "Anulado" para el que salió.
export const BADGES_PRODUCTO: Record<"activo" | "inactivo", { texto: string; clases: string }> = {
  activo: { texto: "Activo", clases: "bg-emerald-100 text-emerald-800" },
  inactivo: { texto: "Inactivo", clases: "bg-neutral-200 text-neutral-700" },
};

// La alerta de reabastecimiento (RN-14): ámbar como "En curso", y
// DELIBERADAMENTE distinta del "¡Últimas N unidades!" de la ficha de
// tienda (stock 1-3, urgencia de compra — Pitfall 6). Dos conceptos, dos
// textos, misma familia semántica.
export const BADGE_STOCK_BAJO = {
  texto: "Stock bajo",
  clases: "bg-amber-100 text-amber-800",
};

// El espejo frontend del STOCK_BAJO_UMBRAL = 5 del backend (guía 12,
// RN-14): dos constantes con nombre en dos tiers que dicen lo mismo.
export const STOCK_BAJO = 5;
```

Ahora el refactor en las DOS consumidoras viejas — tu código, no las
guías:

En **`frontend/src/features/pago/VoucherPedido.tsx`** y en
**`frontend/src/features/pedidos/Pedidos.tsx`**: BORRA la constante
`BADGES` local (la tabla completa con su comentario) y agrega el import
junto a los existentes:

```tsx
import { BADGES } from "../../lib/badges"; // la tercera consumidora nació: bajó a módulo (D-45)
```

Y un detalle que el compilador no te deja pasar: si en `Pedidos.tsx` el
`import type` queda con `EstadoPedido` huérfano (solo la tabla borrada lo
usaba — `VoucherPedido.tsx` no lo tiene), quítalo del import: el scaffold
corre con `noUnusedLocals` y un import sin uso rompe el build.

✅ **Mini-verificación:** `npm run build` pasa — con los DOS archivos
viejos importando del módulo y sin la tabla duplicada en ninguno. Si
algún `BADGES[...]` dejó de compilar, es que el import quedó en el archivo
equivocado: el compilador te dice cuál.

---

## Paso 3 — La infraestructura chiquita: `apiPut`/`apiPatch` y los tipos admin

🧠 **El desarrollador piensa:** *dos piezas pequeñas antes de las pantallas,
y las dos son la misma idea: lo compartido se escribe UNA vez. **Los
verbos:** el proyecto nunca ha hecho un PUT ni un PATCH — el editor de hoy
manda el body completo de la allow-list (PUT, todo-o-nada) y el toggle y
la transición mandan un campo (PATCH, el cambio chico — el mismo par que
la guía 12 justificó en el backend). La buena noticia es el diseño de la
guía 6: `pedir()` ya adjunta el Bearer, ya vigila el 401 con el
interceptor (una sesión que expira DENTRO del panel expulsa con aviso y
vuelve acá por el returnTo — D-22 sin tocar nada) y ya normaliza el
`detail`. `apiPut` y `apiPatch` son el mismo molde de `apiPost` con otro
verbo: tres líneas cada uno, cero decisiones nuevas. **Los tipos:** el
espejo manual de siempre (D-09) — abrir el contrato 0.4.0 y traducir
`ProductoAdmin`, `PedidoAdmin` y `Metricas` campo a campo. Fíjate qué NO
trae `ProductoAdmin`: `descripcion` y `notas` — el listado admin es
liviano a propósito, y esa ausencia tiene consecuencias en el editor del
paso 6 (hidratación desde la ficha pública). Y `ProductoPayload` es el
espejo de la allow-list `ProductoCrear`/`ProductoEditar` — un solo tipo
porque el contrato dice que son LA MISMA lista de campos.*

En **`frontend/src/lib/api.ts`**, agrega al final:

```typescript
// --- Etapa 4: las escrituras del panel (guía 13) ---
// El PRIMER PUT y el PRIMER PATCH del proyecto: pedir() ya trae el
// Bearer, el interceptor 401 y la normalización del detail — solo cambian
// los verbos. PUT manda el body COMPLETO (allow-list todo-o-nada);
// PATCH, un campo (toggle, transición).
export async function apiPut<T>(ruta: string, cuerpo: unknown): Promise<T> {
  return pedir<T>(ruta, {
    method: "PUT",
    body: JSON.stringify(cuerpo),
    headers: { "Content-Type": "application/json" },
  });
}

export async function apiPatch<T>(ruta: string, cuerpo: unknown): Promise<T> {
  return pedir<T>(ruta, {
    method: "PATCH",
    body: JSON.stringify(cuerpo),
    headers: { "Content-Type": "application/json" },
  });
}
```

Y en **`frontend/src/types/api.ts`**, agrega al final:

```typescript
// --- Etapa 4: panel de administración (espejo de contrato_api.yaml 0.4.0) ---

export interface ProductoAdmin {
  id: number;
  nombre: string;
  familia: Familia;
  precio: number;
  stock: number;
  imagen: string;
  activo: boolean; // el soft delete visible (D-52) — el catálogo público no lo muestra
}

// Espejo de ProductoCrear/ProductoEditar: la MISMA allow-list para crear
// y para guardar (sin id ni activo — T-04-09, el mass assignment vetado).
export interface ProductoPayload {
  nombre: string;
  descripcion: string;
  familia: Familia;
  precio: number;
  stock: number;
  notas: string[];
  imagen: string;
}

export interface PedidoAdmin {
  numero: string; // el legible, jamás el id interno (RN-13)
  fecha: string;
  email_clienta: string; // visible solo para admin (D-55)
  total: number;
  estado: EstadoPedido;
}

export interface ConteoEstados {
  pending: number;
  paid: number;
  cancelled: number;
  rejected: number;
}

export interface TopAroma {
  nombre: string; // snapshot congelado al vender (D-36) — histórico
  unidades: number;
}

export interface Metricas {
  ingresos_totales: number;
  pedidos_por_estado: ConteoEstados;
  top_5: TopAroma[];
  productos_stock_bajo: number;
}
```

✅ **Mini-verificación:** `npm run build` pasa. El experimento del
compilador de siempre, ahora con la ausencia que importa: agrega al final
del archivo esta línea con el campo vetado:

```typescript
const imposible: ProductoPayload = {
  nombre: "x", descripcion: "x", familia: "citricas", precio: 1,
  stock: 1, notas: ["x"], imagen: "/x.jpg", activo: false,
};
```

`npm run build` FALLA con
`Object literal may only specify known properties, and 'activo' does not
exist in type 'ProductoPayload'` — el compilador acaba de impedir que el
frontend mande el campo que el backend no tiene dónde recibir. Borra la
línea y el build vuelve a pasar.

---

## Paso 4 — `main.tsx`: la rama paralela del panel, FUERA del Layout de tienda

🧠 **El desarrollador piensa:** *la decisión de rutas más importante del
día, y es de LAYOUT, no de guard: la rama `/admin` vive FUERA del
`<Route element={<Layout />}>` de la tienda — una segunda rama de primer
nivel, paralela. ¿Por qué? Porque el Layout de tienda arrastra el Footer
y (en la guía 15) la burbuja de la asesora: piezas que le hablan a la
CLIENTA. El panel es la trastienda de la dueña: otra navbar de segundo
nivel (la subnav), otro ritmo (`py-12` de densidad de trabajo contra el
`py-16` de marketing), y ni Footer ni burbuja — la dueña no necesita que
su propia asesora le venda stock. Dos ramas, dos layouts, un solo router:
el patrón de rutas anidadas con `<Outlet />` que el proyecto usa desde la
guía 2, ahora con dos raíces. Y fíjate el ORDEN de los envoltorios:
`RequireAdmin` por fuera de `LayoutAdmin` — el guard decide ANTES de que
exista chrome de panel (una clienta que fuerza `/admin` ni siquiera debe
ver la subnav: ve NoAutorizado a secas), y `LayoutAdmin` por fuera de las
tres sub-rutas con `index` para `/admin` exacto (Productos) y paths
relativos `pedidos`/`metricas`.*

En **`frontend/src/main.tsx`**, agrega los imports junto a los de las
features:

```tsx
import RequireAdmin from "./components/RequireAdmin";
import AdminMetricas from "./features/admin/AdminMetricas";
import AdminPedidos from "./features/admin/AdminPedidos";
import AdminProductos from "./features/admin/AdminProductos";
import LayoutAdmin from "./features/admin/LayoutAdmin";
```

Y la rama nueva DESPUÉS del bloque `<Route element={<Layout />}>` de la
tienda — paralela, FUERA de él:

```tsx
{/* La rama del panel (etapa 4, D-55): FUERA del Layout de tienda — sin
    Footer ni burbuja, con su propio layout de subnav. El guard por
    fuera del layout: una clienta que fuerza /admin ni ve la subnav. */}
<Route element={<RequireAdmin />}>
  <Route path="/admin" element={<LayoutAdmin />}>
    <Route index element={<AdminProductos />} />
    <Route path="pedidos" element={<AdminPedidos />} />
    <Route path="metricas" element={<AdminMetricas />} />
  </Route>
</Route>
```

✅ **Mini-verificación:** el build todavía no pasa — faltan los cuatro
componentes del panel (LayoutAdmin y las tres pantallas, pasos 6 a 8). Si
prefieres ver verde entre pasos, comenta la rama hasta el paso 8; el
orden de esta guía la monta completa al final del paso 8 y la prueba en
el 9.

---

## Paso 5 — `LayoutAdmin` y el navbar que solo la dueña ve completo

🧠 **El desarrollador piensa:** *dos piezas de chrome, dos decisiones. **El
layout**: la MISMA Navbar compartida de la tienda — marca, catálogo, carro,
sesión con "Cerrar sesión": la dueña sigue siendo una usuaria navegando su
propio sitio, y una navbar conocida cuesta cero aprendizaje. Debajo, la
subnav propia: BLANCA deliberada, porque la navbar ya es crema — la capa
inmediatamente inferior en blanco separa los dos niveles de navegación sin
inventar un token (el UI-SPEC lo fija así). Tres links con el
`estiloLink` de siempre y el activo en naranja bold; y el "Productos"
lleva `end` — sin él, `/admin` estaría "activo" también en
`/admin/pedidos` (prefix matching de NavLink) y la subnav encendería dos
secciones a la vez. **El navbar**: el link "Panel" renderizado solo cuando
`usuario.rol === "admin"` — el mismo condicionado por estado que instaló
"Mis pedidos" (D-47), ahora por ROL: una clienta ni siquiera sabe que la
ruta existe. Es teatro de UX montado sobre la seguridad del servidor, y
está bien que lo sea: el 403 de `get_current_admin` es la muralla, el link
escondido es cortesía (ADR-015).*

Crea **`frontend/src/features/admin/LayoutAdmin.tsx`**:

```tsx
// El layout del panel (D-55): la MISMA Navbar de la tienda + una subnav
// propia con las tres secciones. SIN Footer y SIN burbuja de asesora
// (esa vive en el Layout de TIENDA, guía 15): el panel es la trastienda.
import { NavLink, Outlet } from "react-router";

import Navbar from "../../components/Navbar";

// La subnav: blanca deliberada — la navbar ya es crema; la capa inferior
// en blanco separa los dos niveles de navegación sin un token nuevo.
const estiloSubnav = ({ isActive }: { isActive: boolean }) =>
  `text-sm min-h-11 flex items-center focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none ${
    isActive ? "text-orange-600 font-bold" : "text-neutral-600"
  }`;

export default function LayoutAdmin() {
  return (
    <div className="flex min-h-screen flex-col bg-white">
      <Navbar />
      <nav className="bg-white border-b border-orange-100">
        <div className="max-w-6xl mx-auto px-4 py-2 flex flex-wrap gap-4">
          {/* end: /admin exacto — sin él, /admin/pedidos dejaría
              "Productos" activo también (prefix matching de NavLink). */}
          <NavLink to="/admin" end className={estiloSubnav}>
            Productos
          </NavLink>
          <NavLink to="/admin/pedidos" className={estiloSubnav}>
            Pedidos
          </NavLink>
          <NavLink to="/admin/metricas" className={estiloSubnav}>
            Métricas
          </NavLink>
        </div>
      </nav>
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}
```

Y en **`frontend/src/components/Navbar.tsx`**, dentro del bloque con
sesión (`{usuario ? ( ... )}`), agrega el link ANTES del de "Mis
pedidos":

```tsx
              {/* Panel: solo el rol admin lo ve (D-55) — el mismo
                  condicionado de "Mis pedidos" (D-47), ahora por rol.
                  Cortesía de UX: el 403 real es del backend (ADR-015). */}
              {usuario.rol === "admin" && (
                <NavLink to="/admin" className={estiloLink}>
                  Panel
                </NavLink>
              )}
              <NavLink to="/pedidos" className={estiloLink}>
                Mis pedidos
              </NavLink>
```

✅ **Mini-verificación:** `npm run build` sigue esperando a las pantallas
(paso 8) — pero el Navbar y el layout ya compilan solos si quieres
adelantarlos: comenta la rama del paso 4 un momento y `npm run build`
pasa con las dos piezas nuevas.

---

## Paso 6 — `AdminProductos`: la tabla de TODOS, el editor inline y el toggle sin confirmación

🧠 **El desarrollador piensa:** *la pantalla más cargada del panel, con
cuatro decisiones que se sostienen juntas. **La tabla lista TODOS**: el
queryKey `["productos", "admin"]` — y ese prefijo compartido es la pieza
fina del día: TanStack invalida por PREFIJO, así que invalidar
`["productos"]` refresca a la vez el catálogo público
(`["productos", params]`, guía 4) y este listado — desactivar un aroma
aquí hace que la vitrina reaccione SOLA, sin saber el panel que existe.
**El editor es estado, no ruta**: `editando: producto | "nuevo" | null`
— no hay URL para "nuevo producto" porque no hay nada que compartir ni
bookmarkear: es un estado transitorio de la pantalla que se abre sobre la
tabla y se cierra en el lugar. La validación cliente es el espejo HONESTO
del 422: los CINCO copys locked bajo el campo que los causó, inmediatos
— y la API sigue siendo la autoridad (el banner rojo del servidor cubre
lo que el espejo no alcanzó a prever). **La hidratación del editor** tiene
su truco honesto: `ProductoAdmin` es liviano a propósito (contrato 0.4.0)
— sin `descripcion` ni `notas` — y esas DOS las trae la FICHA pública
(`ProductoDetalle` las tiene). Al abrir "Editar" se consulta
`api/productos/{id}` con un fetch fresco (`apiGet` directo, NO la caché
`["producto", id]` de la ficha: la dueña que abre el editor merece la
verdad del momento, no una foto que pudo quedar vieja — y el editor ni
sabe si esa key estuvo en pantalla). ¿Y un producto INACTIVO? La
ficha pública no lo muestra (se oculta entero, D-52): su editor parte
con descripción y notas VACÍAS y la dueña las re-escribe — la alternativa
sería un endpoint admin de detalle, que el contrato 0.4.0 no declara: se
anota el deseo, no se improvisa el desvío. **El toggle no pide
confirmación**: "Desactivar"/"Reactivar" escribe directo porque es
reversible POR DISEÑO — el botón de vuelta está en la misma fila — y el
feedback es el badge cambiando en el lugar, sin toast. El contraste con
"Anular" (paso 7), que SÍ confirma en dos pasos, es la lección de
asimetría de la fase 2 hecha regla: la confirmación se cobra donde no
hay vuelta. Y las notas cruzan la frontera como en todo el sistema: texto
con comas en pantalla, `string[]` por el cable — el split/join vive en
el borde del form.*

Crea **`frontend/src/features/admin/AdminProductos.tsx`**:

```tsx
// Pantalla 10 del diseño: TODOS los productos (activos e inactivos, D-52)
// con el editor inline como estado de la pantalla y el toggle reversible
// sin confirmación. El queryKey ["productos", "admin"] comparte PREFIJO
// con el catálogo público: invalidar ["productos"] reacciona ambos.
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";

import { apiGet, apiPatch, apiPost, apiPut } from "../../lib/api";
import { BADGES_PRODUCTO, BADGE_STOCK_BAJO, STOCK_BAJO } from "../../lib/badges";
import {
  FAMILIA_BADGES,
  FAMILIA_LABELS,
  type Familia,
  type ProductoAdmin,
  type ProductoDetalle,
  type ProductoPayload,
} from "../../types/api";

const clp = new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP" });

// El form vive en strings (inputs controlados); el parseo al payload se
// hace al submit, con la validación espejo del 422 debajo de cada campo.
interface Formulario {
  nombre: string;
  descripcion: string;
  familia: Familia | ""; // "" = sin elegir (el select arranca así)
  precio: string;
  stock: string;
  notas: string; // texto con comas en pantalla, string[] por el cable
  imagen: string;
}

const VACIO: Formulario = {
  nombre: "",
  descripcion: "",
  familia: "",
  precio: "",
  stock: "",
  notas: "",
  imagen: "",
};

const aNotas = (texto: string): string[] =>
  texto.split(",").map((nota) => nota.trim()).filter(Boolean);

// El espejo HONESTO del 422: los cinco copys locked, bajo su campo.
function validar(form: Formulario) {
  const errores: Partial<Record<keyof Formulario, string>> = {};
  if (!form.nombre.trim()) errores.nombre = "Escribe un nombre.";
  const precio = Number(form.precio);
  if (form.precio === "" || !Number.isInteger(precio) || precio < 0)
    errores.precio = "El precio debe ser un número mayor o igual a 0.";
  const stock = Number(form.stock);
  if (form.stock === "" || !Number.isInteger(stock) || stock < 0)
    errores.stock = "El stock debe ser un número mayor o igual a 0.";
  if (form.familia === "") errores.familia = "Elige una familia.";
  if (aNotas(form.notas).length === 0) errores.notas = "Escribe al menos una nota.";
  return errores;
}

export default function AdminProductos() {
  const queryClient = useQueryClient();
  // editando: producto | "nuevo" | null — el editor es ESTADO de la
  // pantalla, no una ruta propia.
  const [editando, setEditando] = useState<ProductoAdmin | "nuevo" | null>(null);
  const [form, setForm] = useState<Formulario>(VACIO);
  const [errores, setErrores] = useState<Partial<Record<keyof Formulario, string>>>({});

  const productos = useQuery({
    queryKey: ["productos", "admin"],
    queryFn: () => apiGet<ProductoAdmin[]>("api/admin/productos"),
  });

  const guardar = useMutation({
    mutationFn: ({ body }: { body: ProductoPayload }) =>
      editando !== null && editando !== "nuevo"
        ? apiPut<ProductoAdmin>(`api/admin/productos/${editando.id}`, body)
        : apiPost<ProductoAdmin>("api/admin/productos", body),
    onSuccess: () => {
      // Invalida el PREFIJO: el catálogo público (["productos", params])
      // y este listado reaccionan juntos — desactivar aquí mueve la
      // vitrina sola.
      queryClient.invalidateQueries({ queryKey: ["productos"] });
      setEditando(null);
    },
  });

  const toggle = useMutation({
    mutationFn: (producto: ProductoAdmin) =>
      apiPatch<ProductoAdmin>(`api/admin/productos/${producto.id}/activo`, {
        activo: !producto.activo,
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["productos"] }),
  });

  function abrirNuevo() {
    setEditando("nuevo");
    setForm(VACIO);
    setErrores({});
  }

  function abrirEditor(producto: ProductoAdmin) {
    setEditando(producto);
    setErrores({});
    // ProductoAdmin es liviano a propósito (contrato 0.4.0): descripcion
    // y notas NO viajan en el listado — las trae la FICHA pública. Un
    // producto INACTIVO no tiene ficha (se oculta entero, D-52): su
    // editor parte con esas dos vacías y se re-escriben.
    apiGet<ProductoDetalle>(`api/productos/${producto.id}`)
      .then((detalle) => {
        setForm({
          nombre: detalle.nombre,
          descripcion: detalle.descripcion,
          familia: detalle.familia,
          precio: String(detalle.precio),
          stock: String(detalle.stock),
          notas: detalle.notas.join(", "),
          imagen: detalle.imagen,
        });
      })
      .catch(() => {
        setForm({
          nombre: producto.nombre,
          descripcion: "",
          familia: producto.familia,
          precio: String(producto.precio),
          stock: String(producto.stock),
          notas: "",
          imagen: producto.imagen,
        });
      });
  }

  function submit(evento: FormEvent) {
    evento.preventDefault();
    const erroresNuevos = validar(form);
    setErrores(erroresNuevos);
    if (Object.keys(erroresNuevos).length > 0) return;
    guardar.mutate({
      body: {
        nombre: form.nombre.trim(),
        descripcion: form.descripcion.trim(),
        familia: form.familia as Familia,
        precio: Number(form.precio),
        stock: Number(form.stock),
        notas: aNotas(form.notas),
        imagen: form.imagen.trim(),
      },
    });
  }

  if (productos.isPending) {
    return (
      <main className="max-w-6xl mx-auto px-4 py-12">
        <h1 className="text-2xl md:text-3xl font-extrabold text-neutral-900">
          Productos
        </h1>
        <div className="mt-6 bg-white rounded-2xl border border-orange-100 p-6 divide-y divide-orange-100">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="py-4 flex items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 animate-pulse bg-neutral-200 rounded-lg" />
                <div className="h-4 w-44 animate-pulse bg-neutral-200 rounded-2xl" />
              </div>
              <div className="h-6 w-24 animate-pulse bg-neutral-200 rounded-2xl" />
            </div>
          ))}
        </div>
      </main>
    );
  }

  if (productos.isError) {
    return (
      <main className="max-w-xl mx-auto px-4 py-16 text-center">
        <h1 className="text-xl font-bold text-neutral-900">
          No pudimos cargar los productos
        </h1>
        <p className="mt-2 text-sm text-neutral-600">
          Revisa que el backend esté corriendo en el puerto 8000 e inténtalo
          de nuevo.
        </p>
        <button
          onClick={() => productos.refetch()}
          className="mt-6 bg-orange-600 text-white font-bold rounded-full px-6 py-2 min-h-11 hover:bg-orange-700 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
        >
          Reintentar
        </button>
      </main>
    );
  }

  return (
    <main className="max-w-6xl mx-auto px-4 py-12">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl md:text-3xl font-extrabold text-neutral-900">
          Productos
        </h1>
        <button
          onClick={abrirNuevo}
          className="bg-orange-600 text-white font-bold rounded-full px-4 py-2 min-h-11 text-sm hover:bg-orange-700 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
        >
          Nuevo producto
        </button>
      </div>

      {/* El toggle es reversible por diseño: SIN confirmación. Si falla,
          la familia genérica de escritura — el badge es el feedback. */}
      {toggle.isError && (
        <p className="mt-4 rounded-2xl bg-red-50 text-red-600 p-4 text-sm">
          No pudimos guardar el cambio. Inténtalo de nuevo.
        </p>
      )}

      {editando !== null && (
        <form
          onSubmit={submit}
          className="mt-6 bg-white rounded-2xl border border-orange-100 p-6"
        >
          <div className="flex flex-wrap items-center justify-between gap-4">
            <h2 className="text-xl font-bold text-neutral-900">
              {editando === "nuevo"
                ? "Nuevo producto"
                : `Editar ${editando.nombre}`}
            </h2>
            <button
              type="button"
              onClick={() => setEditando(null)}
              className="text-sm text-neutral-600 min-h-11 hover:text-neutral-900 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
            >
              Cancelar
            </button>
          </div>

          {/* El form NO edita activo: un producto nuevo nace activo y el
              toggle de la fila es el único dueño del estado comercial
              (D-52). */}
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <div>
              <label htmlFor="nombre" className="text-sm font-bold text-neutral-900">
                Nombre
              </label>
              <input
                id="nombre"
                type="text"
                value={form.nombre}
                onChange={(e) => setForm({ ...form, nombre: e.target.value })}
                className="mt-1 w-full rounded-lg border border-orange-200 bg-white px-4 py-2 min-h-11 text-base focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
              />
              {errores.nombre && (
                <p className="mt-1 text-sm text-red-600">{errores.nombre}</p>
              )}
            </div>
            <div>
              <label htmlFor="familia" className="text-sm font-bold text-neutral-900">
                Familia
              </label>
              <select
                id="familia"
                value={form.familia}
                onChange={(e) =>
                  setForm({ ...form, familia: e.target.value as Familia | "" })
                }
                className="mt-1 w-full rounded-lg border border-orange-200 bg-white px-4 py-2 min-h-11 text-base focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
              >
                <option value="">Elige una familia</option>
                {(Object.keys(FAMILIA_LABELS) as Familia[]).map((familia) => (
                  <option key={familia} value={familia}>
                    {FAMILIA_LABELS[familia]}
                  </option>
                ))}
              </select>
              {errores.familia && (
                <p className="mt-1 text-sm text-red-600">{errores.familia}</p>
              )}
            </div>
            <div>
              <label htmlFor="precio" className="text-sm font-bold text-neutral-900">
                Precio
              </label>
              <input
                id="precio"
                type="number"
                min="0"
                value={form.precio}
                onChange={(e) => setForm({ ...form, precio: e.target.value })}
                className="mt-1 w-full rounded-lg border border-orange-200 bg-white px-4 py-2 min-h-11 text-base focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
              />
              {errores.precio && (
                <p className="mt-1 text-sm text-red-600">{errores.precio}</p>
              )}
            </div>
            <div>
              <label htmlFor="stock" className="text-sm font-bold text-neutral-900">
                Stock
              </label>
              <input
                id="stock"
                type="number"
                min="0"
                value={form.stock}
                onChange={(e) => setForm({ ...form, stock: e.target.value })}
                className="mt-1 w-full rounded-lg border border-orange-200 bg-white px-4 py-2 min-h-11 text-base focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
              />
              {errores.stock && (
                <p className="mt-1 text-sm text-red-600">{errores.stock}</p>
              )}
            </div>
            <div className="sm:col-span-2">
              <label htmlFor="descripcion" className="text-sm font-bold text-neutral-900">
                Descripción
              </label>
              <textarea
                id="descripcion"
                rows={3}
                value={form.descripcion}
                onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
                className="mt-1 w-full rounded-lg border border-orange-200 bg-white px-4 py-2 min-h-11 text-base focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
              />
            </div>
            <div className="sm:col-span-2">
              <label htmlFor="notas" className="text-sm font-bold text-neutral-900">
                Notas aromáticas
              </label>
              <input
                id="notas"
                type="text"
                value={form.notas}
                onChange={(e) => setForm({ ...form, notas: e.target.value })}
                className="mt-1 w-full rounded-lg border border-orange-200 bg-white px-4 py-2 min-h-11 text-base focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
              />
              <p className="mt-1 text-sm text-neutral-600">
                Separa las notas con comas, ej: naranja, bergamota.
              </p>
              {errores.notas && (
                <p className="mt-1 text-sm text-red-600">{errores.notas}</p>
              )}
            </div>
            <div className="sm:col-span-2">
              <label htmlFor="imagen" className="text-sm font-bold text-neutral-900">
                Foto (ruta)
              </label>
              <input
                id="imagen"
                type="text"
                value={form.imagen}
                onChange={(e) => setForm({ ...form, imagen: e.target.value })}
                className="mt-1 w-full rounded-lg border border-orange-200 bg-white px-4 py-2 min-h-11 text-base focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
              />
              {/* D-51: la foto es una RUTA de texto — sin upload de
                  archivos; el seed baja las fotos (D-08). */}
              <p className="mt-1 text-sm text-neutral-600">
                Ruta dentro del sitio, ej: /products/citricas-01.jpg.
              </p>
            </div>
          </div>

          {guardar.isError && (
            <p className="mt-4 rounded-2xl bg-red-50 text-red-600 p-4 text-sm">
              No pudimos guardar el producto. Revisa los datos e inténtalo
              de nuevo.
            </p>
          )}

          <button
            type="submit"
            disabled={guardar.isPending}
            className="mt-6 bg-orange-600 text-white font-bold rounded-full px-6 py-2 min-h-11 hover:bg-orange-700 disabled:opacity-60 disabled:cursor-not-allowed focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
          >
            {guardar.isPending
              ? "Guardando…"
              : editando === "nuevo"
                ? "Crear producto"
                : "Guardar cambios"}
          </button>
        </form>
      )}

      {productos.data.length === 0 ? (
        <div className="mt-6 text-center bg-white rounded-2xl border border-orange-100 p-6">
          <h2 className="text-xl font-bold text-neutral-900">
            Aún no hay productos
          </h2>
          <p className="mt-2 text-base text-neutral-600">
            Crea el primero con el botón «Nuevo producto».
          </p>
        </div>
      ) : (
        <div className="mt-6 bg-white rounded-2xl border border-orange-100 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-neutral-600">
                <th className="px-4 py-3 font-bold">Producto</th>
                <th className="px-4 py-3 font-bold">Precio</th>
                <th className="px-4 py-3 font-bold">Stock</th>
                <th className="px-4 py-3 font-bold">Estado</th>
                <th className="px-4 py-3 font-bold">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {productos.data.map((producto) => {
                const estado = BADGES_PRODUCTO[producto.activo ? "activo" : "inactivo"];
                return (
                  <tr key={producto.id} className="border-t border-orange-100">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-4">
                        <img
                          src={producto.imagen}
                          alt={producto.nombre}
                          className="w-12 h-12 rounded-lg object-cover"
                        />
                        <div>
                          <p className="font-bold text-neutral-900">
                            {producto.nombre}
                          </p>
                          <span
                            className={`rounded-full px-2 py-1 ${FAMILIA_BADGES[producto.familia]}`}
                          >
                            {FAMILIA_LABELS[producto.familia]}
                          </span>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-base font-extrabold text-orange-700">
                      {clp.format(producto.precio)}
                    </td>
                    <td className="px-4 py-3">
                      <span className="flex flex-wrap items-center gap-2">
                        <span className="text-neutral-900">{producto.stock} u.</span>
                        {/* Solo activos (RN-14): un inactivo con stock bajo
                            no vende — nada que reabastecer. */}
                        {producto.activo && producto.stock <= STOCK_BAJO && (
                          <span
                            className={`rounded-full px-2 py-1 ${BADGE_STOCK_BAJO.clases}`}
                          >
                            {BADGE_STOCK_BAJO.texto}
                          </span>
                        )}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`rounded-full px-2 py-1 ${estado.clases}`}>
                        {estado.texto}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="flex flex-wrap items-center gap-4">
                        <button
                          onClick={() => abrirEditor(producto)}
                          className="text-orange-600 font-bold min-h-11 hover:bg-orange-50 rounded-full px-2 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
                        >
                          Editar
                        </button>
                        {/* Sin confirmación: reversible por diseño (D-52) —
                            el feedback es el badge cambiando en el lugar. */}
                        <button
                          onClick={() => toggle.mutate(producto)}
                          disabled={toggle.isPending}
                          className="text-orange-600 font-bold min-h-11 hover:bg-orange-50 rounded-full px-2 disabled:opacity-60 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
                        >
                          {producto.activo ? "Desactivar" : "Reactivar"}
                        </button>
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
```

✅ **Mini-verificación:** el build sigue esperando a las pantallas 11 y 12
— esta es la primera de tres. Su momento de verde llega al final del paso
8; su momento de verdad, en el 9.

---

## Paso 7 — `AdminPedidos`: todas las órdenes, la anulación en dos pasos y el 409 con su copy

🧠 **El desarrollador piensa:** *la pantalla de la acción destructiva de la
fase, y cada decisión gira alrededor de eso. **"Anular" solo aparece en
filas pending** — no se oculta por estética: es que la máquina NO TIENE
flecha de salida desde PAID/REJECTED/CANCELLED (D-50), y pintar un botón
que siempre fallaría sería prometer una transición que no existe. Pero
ojo: el `if` de la pantalla es UX que ahorra un clic, NO la muralla — la
muralla es el `WHERE estado = 'pending'` del backend (guía 12), y por eso
el 409 existe: dos pestañas del panel que anulan a la vez, una gana y la
otra recibe el copy locked. **La confirmación en dos pasos inline** es el
patrón "Vaciar carro" de la fase 2 (primera acción destructiva de
entonces, primera IRREVERSIBLE de ahora): el primer clic transforma la
celda en "¿Anular el pedido {numero}?" con "Sí, anular"/"Cancelar" — sin
modal ni `window.confirm`, texto que reemplaza texto en el mismo lugar.
El contraste con el toggle del paso 6 es la lección completa: la
confirmación se cobra donde no hay vuelta, y solo ahí. **El 409 se
muestra con SU copy** — "Ese pedido ya no está en curso." — y tras
mostrarlo se invalida el prefijo `["pedidos"]`: la fila refresca con la
verdad del servidor, que otro decidió. Ese prefijo también alcanza al
historial de la clienta (`["pedidos"]`, guía 11): su pantalla reaccionará
sola la próxima vez que la monte — D-48/D-49 cobrados sin editar la guía
11. **Y sin vista de detalle**: la fila no enlaza al voucher. El endpoint
de detalle es del DUEÑO del pedido (404 uniforme de ownership, RN-08) —
un link del panel al `/pedidos/{numero}` de la clienta sería un link a un
404 garantizado. La fila ya trae todo lo que la gestión necesita: numero,
fecha, email, total y estado.*

Crea **`frontend/src/features/admin/AdminPedidos.tsx`**:

```tsx
// Pantalla 11 del diseño: TODAS las órdenes de TODAS las clientas, la
// más reciente primero, con "Anular" SOLO en las pending (D-50) — la
// confirmación en dos pasos inline (patrón "Vaciar carro") porque es la
// acción destructiva IRREVERSIBLE de la fase. Sin vista de detalle: el
// endpoint de detalle es del dueño del pedido (404 uniforme, RN-08).
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { ApiError, apiGet, apiPatch } from "../../lib/api";
import { BADGES } from "../../lib/badges"; // la tercera consumidora (D-45)
import type { PedidoAdmin } from "../../types/api";

const clp = new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP" });

export default function AdminPedidos() {
  const queryClient = useQueryClient();
  // El numero en confirmación inline (la celda en su segundo paso).
  const [anulando, setAnulando] = useState<string | null>(null);
  const [aviso, setAviso] = useState<string | null>(null);

  const pedidos = useQuery({
    queryKey: ["pedidos", "admin"], // prefijo ["pedidos"]: invalidación compartida con el historial
    queryFn: () => apiGet<PedidoAdmin[]>("api/admin/pedidos"),
  });

  const anular = useMutation({
    mutationFn: (numero: string) =>
      apiPatch<PedidoAdmin>(`api/admin/pedidos/${numero}/estado`, {
        estado: "cancelled", // el único destino manual (ADR-016)
      }),
    onSuccess: () => {
      setAnulando(null);
      setAviso(null);
      // Prefijo ["pedidos"]: esta lista Y el historial de la clienta
      // (guía 11) reaccionan — ella verá "Anulado" sin que nadie edite
      // su pantalla (D-48/D-49).
      queryClient.invalidateQueries({ queryKey: ["pedidos"] });
    },
    onError: (error) => {
      setAnulando(null);
      setAviso(
        error instanceof ApiError && error.status === 409
          ? // El copy locked del contrato (D-50): otra pestaña anuló
            // antes — la máquina de estados del backend lo decidió.
            "Ese pedido ya no está en curso."
          : // La familia genérica de escritura, para cualquier otro fallo.
            "No pudimos guardar el cambio. Inténtalo de nuevo."
      );
      // La fila puede quedar vieja: refresca con la verdad del servidor.
      queryClient.invalidateQueries({ queryKey: ["pedidos"] });
    },
  });

  if (pedidos.isPending) {
    return (
      <main className="max-w-6xl mx-auto px-4 py-12">
        <h1 className="text-2xl md:text-3xl font-extrabold text-neutral-900">
          Pedidos
        </h1>
        <div className="mt-6 bg-white rounded-2xl border border-orange-100 p-6 divide-y divide-orange-100">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="py-4 flex items-center justify-between gap-4">
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
          No pudimos cargar los pedidos
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

  return (
    <main className="max-w-6xl mx-auto px-4 py-12">
      <h1 className="text-2xl md:text-3xl font-extrabold text-neutral-900">
        Pedidos
      </h1>

      {aviso && (
        <p className="mt-4 rounded-2xl bg-red-50 text-red-600 p-4 text-sm" role="alert">
          {aviso}
        </p>
      )}

      {pedidos.data.length === 0 ? (
        <div className="mt-6 text-center bg-white rounded-2xl border border-orange-100 p-6">
          <h2 className="text-xl font-bold text-neutral-900">
            Todavía no hay pedidos
          </h2>
          <p className="mt-2 text-base text-neutral-600">
            Cuando tus clientas compren, los pedidos aparecerán aquí.
          </p>
        </div>
      ) : (
        <div className="mt-6 bg-white rounded-2xl border border-orange-100 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-neutral-600">
                <th className="px-4 py-3 font-bold">Pedido</th>
                <th className="px-4 py-3 font-bold">Fecha</th>
                <th className="px-4 py-3 font-bold">Clienta</th>
                <th className="px-4 py-3 font-bold">Total</th>
                <th className="px-4 py-3 font-bold">Estado</th>
                <th className="px-4 py-3 font-bold">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {pedidos.data.map((pedido) => {
                const badge = BADGES[pedido.estado] ?? BADGES.pending;
                return (
                  <tr key={pedido.numero} className="border-t border-orange-100">
                    <td className="px-4 py-3 font-bold text-neutral-900">
                      {pedido.numero}
                    </td>
                    <td className="px-4 py-3 text-neutral-600">
                      {new Date(pedido.fecha).toLocaleDateString("es-CL")}
                    </td>
                    <td className="px-4 py-3">
                      {/* email truncado con title: el dato completo al
                          hover, la tabla respira en mobile. */}
                      <span
                        className="text-neutral-600 truncate max-w-32 block"
                        title={pedido.email_clienta}
                      >
                        {pedido.email_clienta}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-lg font-extrabold text-orange-700">
                      {clp.format(pedido.total)}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`rounded-full px-2 py-1 ${badge.clases}`}>
                        {badge.texto}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {pedido.estado === "pending" ? (
                        anulando === pedido.numero ? (
                          // Segundo paso: texto que reemplaza texto en la
                          // celda — sin modal (patrón "Vaciar carro").
                          <span className="flex flex-wrap items-center gap-2">
                            <span className="text-neutral-900">
                              ¿Anular el pedido {pedido.numero}?
                            </span>
                            <button
                              onClick={() => anular.mutate(pedido.numero)}
                              disabled={anular.isPending}
                              className="text-red-600 font-bold min-h-11 hover:bg-red-50 rounded-full px-2 disabled:opacity-60 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
                            >
                              Sí, anular
                            </button>
                            <button
                              onClick={() => setAnulando(null)}
                              className="text-neutral-600 min-h-11 hover:bg-neutral-100 rounded-full px-2 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
                            >
                              Cancelar
                            </button>
                          </span>
                        ) : (
                          // Primer paso: solo las pending muestran la
                          // acción — la máquina no tiene flecha desde los
                          // otros estados (D-50).
                          <button
                            onClick={() => setAnulando(pedido.numero)}
                            className="text-red-600 font-bold min-h-11 hover:bg-red-50 rounded-full px-2 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
                          >
                            Anular
                          </button>
                        )
                      ) : null}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
```

✅ **Mini-verificación:** build aún en espera — una pantalla más y el
montaje del paso 4 despierta.

---

## Paso 8 — `AdminMetricas`: tres tarjetas, una tabla y el cero honesto

🧠 **El desarrollador piensa:** *la pantalla más tranquila del panel y la
que más tentación genera de decorar. El requisito veta los gráficos
(RF-22/ADMN-04, STAKE-04 diferido): la dueña necesita números CONFIABLES,
no decoración — tarjetas y tabla HTML, nada más. **Tres KPI cards**: los
ingresos con el token de precio (`text-2xl font-extrabold
text-orange-700` — dinero), los pedidos por estado como CUATRO filas
badge+conteo (la máquina completa, siempre), y el stock bajo con el valor
en neutral (NO es dinero) y su link "Ver productos →" hacia `/admin`. **El
cero honesto**: sin ventas, los KPI muestran `$0` y `0` explícitos — los
números no se esconden ni se disimulan con guiones; y la tabla top 5 tiene
su propio empty ("Aún no hay ventas registradas."). **Y la fila del top 5
no enlaza a nada**: el nombre es el SNAPSHOT congelado al vender (D-36) —
histórico que puede ya no existir en el catálogo; un link sería prometer
una ficha que quizá no está. Texto plano, a diferencia de las cards del
chat que vienen en la guía 15 (esas SÍ existen: el backend las valida
contra el catálogo activo).*

Crea **`frontend/src/features/admin/AdminMetricas.tsx`**:

```tsx
// Pantalla 12 del diseño: los cuatro KPI en 3 tarjetas + la tabla top 5,
// SIN gráficos (RF-22/ADMN-04). Cero honesto: $0 y 0 explícitos — los
// números no se esconden. El top 5 usa el nombre SNAPSHOT: filas de texto
// plano sin link (histórico, puede no existir en el catálogo — D-36).
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router";

import { apiGet } from "../../lib/api";
import { BADGES } from "../../lib/badges";
import type { EstadoPedido, Metricas } from "../../types/api";

const clp = new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP" });

// La máquina completa, siempre — el orden de la pantalla 12 del diseño.
const ESTADOS: EstadoPedido[] = ["paid", "pending", "cancelled", "rejected"];

export default function AdminMetricas() {
  const metricas = useQuery({
    queryKey: ["metricas"],
    queryFn: () => apiGet<Metricas>("api/admin/metricas"),
  });

  if (metricas.isPending) {
    return (
      <main className="max-w-6xl mx-auto px-4 py-12">
        <h1 className="text-2xl md:text-3xl font-extrabold text-neutral-900">
          Métricas
        </h1>
        <div className="mt-6 grid gap-6 sm:grid-cols-3">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="h-40 animate-pulse bg-neutral-200 rounded-2xl"
            />
          ))}
        </div>
        <div className="mt-6 h-40 animate-pulse bg-neutral-200 rounded-2xl" />
      </main>
    );
  }

  if (metricas.isError) {
    return (
      <main className="max-w-xl mx-auto px-4 py-16 text-center">
        <h1 className="text-xl font-bold text-neutral-900">
          No pudimos cargar las métricas
        </h1>
        <p className="mt-2 text-sm text-neutral-600">
          Revisa que el backend esté corriendo en el puerto 8000 e inténtalo
          de nuevo.
        </p>
        <button
          onClick={() => metricas.refetch()}
          className="mt-6 bg-orange-600 text-white font-bold rounded-full px-6 py-2 min-h-11 hover:bg-orange-700 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
        >
          Reintentar
        </button>
      </main>
    );
  }

  const m = metricas.data;

  return (
    <main className="max-w-6xl mx-auto px-4 py-12">
      <h1 className="text-2xl md:text-3xl font-extrabold text-neutral-900">
        Métricas
      </h1>

      <div className="mt-6 grid gap-6 sm:grid-cols-3">
        <div className="bg-white rounded-2xl border border-orange-100 p-6">
          <p className="text-sm text-neutral-600">Ingresos totales</p>
          {/* Token de precio: dinero — el mismo del total de los pedidos. */}
          <p className="mt-2 text-2xl font-extrabold text-orange-700">
            {clp.format(m.ingresos_totales)}
          </p>
          <p className="mt-2 text-sm text-neutral-600">
            Suma de los pedidos pagados.
          </p>
        </div>

        <div className="bg-white rounded-2xl border border-orange-100 p-6">
          <p className="text-sm text-neutral-600">Pedidos por estado</p>
          <ul className="mt-2 flex flex-col gap-2">
            {ESTADOS.map((estado) => {
              const badge = BADGES[estado];
              return (
                <li key={estado} className="flex justify-between items-center gap-2">
                  <span className={`rounded-full px-2 py-1 ${badge.clases}`}>
                    {badge.texto}
                  </span>
                  {/* Cero honesto: el 0 se muestra, no se esconde. */}
                  <span className="text-lg font-extrabold text-neutral-900">
                    {m.pedidos_por_estado[estado]}
                  </span>
                </li>
              );
            })}
          </ul>
        </div>

        <div className="bg-white rounded-2xl border border-orange-100 p-6">
          <p className="text-sm text-neutral-600">Stock bajo</p>
          {/* NO es dinero: neutral-900, no el token de precio. */}
          <p className="mt-2 text-2xl font-extrabold text-neutral-900">
            {m.productos_stock_bajo}
          </p>
          <p className="mt-2 text-sm text-neutral-600">
            Productos activos con 5 unidades o menos.
          </p>
          <Link
            to="/admin"
            className="mt-2 inline-flex items-center text-sm text-orange-600 font-bold min-h-11 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
          >
            Ver productos →
          </Link>
        </div>
      </div>

      <h2 className="mt-8 text-xl font-bold text-neutral-900">
        Top 5 aromas vendidos
      </h2>
      {m.top_5.length === 0 ? (
        <div className="mt-4 text-center bg-white rounded-2xl border border-orange-100 p-6">
          <p className="text-base text-neutral-600">
            Aún no hay ventas registradas.
          </p>
        </div>
      ) : (
        <div className="mt-4 bg-white rounded-2xl border border-orange-100 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-neutral-600">
                <th className="px-4 py-3 font-bold">#</th>
                <th className="px-4 py-3 font-bold">Aroma</th>
                <th className="px-4 py-3 font-bold">Unidades</th>
              </tr>
            </thead>
            <tbody>
              {m.top_5.map((aroma, indice) => (
                <tr key={aroma.nombre} className="border-t border-orange-100">
                  <td className="px-4 py-3 text-neutral-600">{indice + 1}</td>
                  {/* Texto plano SIN link: el nombre es el snapshot
                      congelado al vender (D-36) — puede ya no existir en
                      el catálogo. */}
                  <td className="px-4 py-3 font-bold text-neutral-900">
                    {aroma.nombre}
                  </td>
                  <td className="px-4 py-3 text-lg font-extrabold text-neutral-900">
                    {aroma.unidades}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
```

✅ **Mini-verificación:** descomenta (o confirma) la rama del paso 4 y
`npm run build` pasa completo: guard, layout, navbar, módulo de badges,
los dos verbos nuevos, los tipos y las tres pantallas — el panel entero
compila. Su momento de verdad es el siguiente paso, en el navegador.

---

## Paso 9 — La prueba de fuego: la clienta rechazada, la dueña adentro y la huérfana anulada

🧠 **El desarrollador piensa:** *la batería del navegador, y cada golpe
verifica una promesa del UI-SPEC. La clienta que fuerza `/admin` ve
NoAutorizado SIN expulsión — y el detalle fino: lo ve A SECAS, sin navbar
de tienda ni subnav de panel — el guard vetó la RAMA entera y
`LayoutAdmin` ni se montó (el orden de los envoltorios del paso 4
haciendo su trabajo). Su sesión SIGUE viva: es permiso, no identidad. El
returnTo del admin: cerrar sesión, forzar `/admin`, entrar como admin — y
volver AL PANEL, no a la portada (D-32 por tercera vez). El link Panel
que solo la dueña ve. El catálogo que reacciona solo al desactivar (la
invalidación por prefijo — el alumno lo VEE: misma sesión, otra pestaña,
el aroma desapareció de la vitrina). La anulación en dos pasos con su
badge cambiando en el lugar. El 409 con su banner, provocado a propósito
con dos pestañas. Y el cierre del ciclo de la fase 3: la clienta ve su
huérfana ANULADA en el historial — la guía 11 mostró la verdad pendiente,
la 12 la hizo transicionable, la 13 la transiciona. Nadie editó la guía
11: el historial siempre mostró el estado REAL, y hoy el estado real
cambió.*

Con ambos servidores corriendo (`uv run fastapi dev app/main` en
`backend/`, `npm run dev` en `frontend/`):

✅ **Mini-verificación (la clienta rechazada, sin expulsión):** entra con
tu `CLIENTE_EMAIL` y escribe **http://localhost:5173/admin** en la barra:
ves **"No tienes acceso al panel"** con "El panel de administración es
solo para la dueña de la tienda." y el link "Volver a la tienda" — NO el
login, y A SECAS: sin navbar de tienda y sin subnav de panel, porque el
guard vetó la rama entera y `LayoutAdmin` nunca se montó. Tu sesión
sigue viva: "Volver a la tienda" te deja en el inicio CON tu navbar
saludándote de nuevo, lista para seguir comprando — te falta permiso, no
identidad (D-55). Y fíjate: tu navbar NO tiene link "Panel" —
una clienta ni sabe que la ruta existe.

✅ **Mini-verificación (el returnTo del panel):** cierra sesión y fuerza
`/admin` de nuevo: ahora SÍ al login (sin sesión, `RequireAdmin`
delegó en `RequireAuth` — D-32). Entra con tu `ADMIN_EMAIL`… y aterrizas
EN EL PANEL, no en la portada: el guard guardó el destino y el login lo
leyó, igual que la guía 8 hizo con el checkout. Tu navbar ahora muestra
**"Panel"** entre "Carro" y "Mis pedidos" (solo visible con rol admin) y
la subnav blanca con Productos · Pedidos · Métricas.

✅ **Mini-verificación (el soft delete reacciona en la vitrina, solo):**
en **/admin**, desactiva un aroma con **Desactivar** — sin confirmación:
el badge cambia de "Activo" a "Inactivo" en el lugar (ese es el
feedback). En OTRA pestaña de la MISMA sesión, abre el catálogo público:
el aroma DESAPARECIÓ de la vitrina — la invalidación del prefijo
`["productos"]` refrescó la key del catálogo sin que el panel supiera de
ella. Reactívalo y la vitrina lo recupera igual de sola.

✅ **Mini-verificación (la huérfana, por fin anulada):** en
**/admin/pedidos**, encuentra tu PENDING de fase 3 (badge "En curso") y
presiona **Anular**: la celda se transforma en "¿Anular el pedido
{numero}?" con "Sí, anular"/"Cancelar" — el dos pasos inline, sin modal.
"Sí, anular": el badge pasa a **"Anulado"** y el botón desaparece (ya no
es pending — la máquina no tiene flecha de vuelta). Ahora cierra sesión
de admin, entra como clienta y abre **"Mis pedidos"**: esa orden muestra
**"Anulado"** — la guía 11 intacta mostrando una verdad que otra pantalla
cambió (D-48/D-49).

✅ **Mini-verificación (el 409 con su copy, provocado):** abre
`/admin/pedidos` en DOS pestañas del navegador (la misma sesión admin) y
anula la MISMA PENDING en ambas — primero en una, luego en la otra: la
segunda recibe el banner rojo **"Ese pedido ya no está en curso."** — el
409 del backend con su copy locked, porque el `WHERE estado = 'pending'`
ya no encontró la fila (D-50). La máquina de estados decidió; el panel
solo lo cuenta.

✅ **Mini-verificación (métricas contra tu fase 3):** abre
**/admin/metricas**: los ingresos suman TUS órdenes pagadas, los cuatro
estados con sus conteos (tu huérfana ya suma en "Anulado"), el stock bajo
con tu conteo — y el top 5 con los nombres de época de lo que vendiste.
Si desactivaste un aroma vendido en la prueba anterior, sigue en el top:
SNAPSHOT, no catálogo (D-36).

---

## ❌ El error que este archivo evita

**1. Un solo umbral de stock en la cabeza del que escribe.**

```tsx
// ❌ el mismo número y el mismo texto para la dueña y la clienta:
// "¡Stock bajo!" en la ficha asusta a la clienta con 4 unidades
const UMBRAL = 5;
{stock <= UMBRAL && <span>¡Stock bajo!</span>}

// ✅ dos constantes con nombre, dos textos, dos públicos (Pitfall 6, RN-14)
// lib/badges.ts: STOCK_BAJO = 5 — el umbral ADMIN (reabastecimiento)
{producto.activo && producto.stock <= STOCK_BAJO && <span>Stock bajo</span>}
// la ficha de tienda sigue con SU umbral 1-3 ("últimas unidades") — su lugar, su copy
```

La dueña que ve "Stock bajo" con 4 unidades reabastece a tiempo; la
clienta que lo viera desconfiaría de un producto con stock sano. El mismo
número para los dos sería un bug de MENSAJE que ningún test atrapa — solo
la dueña confundida.

**2. Confirmación para el toggle reversible.**

```tsx
// ❌ window.confirm para DESACTIVAR: interrumpe una acción que tiene
// botón de vuelta en la misma fila
if (!window.confirm("¿Desactivar el producto?")) return;

// ✅ sin confirmación: reversible por diseño — el feedback es el badge
// cambiando "Activo" ↔ "Inactivo" en el lugar
<button onClick={() => toggle.mutate(producto)}>Desactivar</button>
```

La confirmación se cobra donde no hay vuelta (el "Anular" de pedidos la
tiene, en dos pasos inline): gastarla en lo reversible entrena a la dueña
a clicar "sí" por reflejo — y entonces ya no protege nada.

**3. Enlazar la fila del panel al voucher de la clienta.**

```tsx
// ❌ el admin navega "a ver el pedido"… a un 404 garantizado
<Link to={`/pedidos/${pedido.numero}`}>Ver detalle →</Link>

// ✅ la fila ya trae TODO lo que la gestión necesita — sin link
<td>{pedido.numero} · {pedido.email_clienta} · {clp.format(pedido.total)} …</td>
```

El endpoint de detalle responde SOLO al dueño del pedido (404 uniforme de
ownership, RN-08): el historial es de la clienta, la fila es de la dueña.
Un link que siempre revienta es peor que ningún link — y la pantalla
honesta es la que no promete lo que el backend no da.

**4. Duplicar BADGES una tercera vez.**

```tsx
// ❌ copiar la tabla de estados OTRA vez en la pantalla del panel:
// tres verdades del mismo estado, tres lugares que corregir
const BADGES = { paid: {...}, pending: {...}, ... };

// ✅ la tercera consumidora baja a módulo — la nota que la guía 11 dejó
import { BADGES } from "../../lib/badges"; // una sola verdad (D-45)
```

La guía 10 copió (una consumidora), la 11 copió (dos — y dejó escrito el
día de hoy): a la tercera, módulo. El refactor toca el código del alumno,
jamás las guías viejas — la promesa se cobra sin re-escribir la historia.

---

## ✅ Verificación de la guía 13

Con ambos servidores corriendo y el seed corrido:

1. `npm run build` pasa — guard, layout, módulo badges, `apiPut`/
   `apiPatch`, tipos y las tres pantallas.
2. Clienta con sesión que fuerza `/admin` → "No tienes acceso al panel"
   con "Volver a la tienda" — SIN expulsión al login y A SECAS (sin
   navbar ni subnav: el guard vetó la rama entera); su sesión vive y la
   tienda la recibe de vuelta (D-55).
3. Sin sesión, `/admin` → login → entrar como admin → vuelta AL PANEL
   (returnTo, D-32) — y "Panel" en el navbar solo con rol admin (D-47 por
   rol).
4. `/admin` lista TODOS los productos con badges Activo/Inactivo y Stock
   bajo (solo activos, RN-14); "Nuevo producto" abre el editor inline
   (estado de la pantalla, sin ruta) y "Crear producto" nace el aroma
   activo; "Editar" hidrata desde la ficha pública (descripción y notas),
   con los 5 copys de validación espejo del 422.
5. "Desactivar" sin confirmación: badge cambiando en el lugar — y el
   catálogo público reacciona SOLO en la misma sesión (invalidación por
   prefijo de `["productos"]`).
6. `/admin/pedidos`: TODAS las órdenes con email de clienta, "Anular"
   solo en pending, confirmación en dos pasos inline — y el 409 de la
   doble anulación con su banner "Ese pedido ya no está en curso."
7. La clienta ve la huérfana "Anulado" en SU historial — guía 11
   byte-intacta (D-48/D-49).
8. `/admin/metricas`: los 3 KPI + top 5 contra tus órdenes de fase 3,
   cero honesto y filas del top sin link (snapshot, D-36).

(La comparación contrato 0.4.0 ↔ `/docs` con Authorize y el grep del
build del asistente — fase completa — son la Gran verificación final de
la guía 15.)

## 📝 Punto de control (respóndelas sin mirar la guía)

1. `RequireAdmin` con una clienta autenticada NO la manda al login:
   ¿qué diferencia hay entre identidad y permiso, qué pantalla lo dice
   — y quién es la muralla de verdad si el guard se salta con las
   devtools? (D-55, ADR-015.)
2. Desactivar un producto en `/admin` hace que el catálogo público
   reaccione sin que el panel lo llame: ¿qué pieza de TanStack Query lo
   hace posible, qué comparten exactamente las dos pantallas — y qué
   pasaría si el panel usara la key `["admin-productos"]`?
3. "Desactivar" no pide confirmación y "Anular" sí, en dos pasos inline:
   ¿qué propiedad de cada acción justifica la asimetría — y por qué el
   409 del backend sigue siendo necesario aunque la pantalla ya solo
   muestra "Anular" en las pending? (D-50, T-04-08.)
4. La fila del top 5 no enlaza a la ficha, pero las cards del chat de la
   guía 15 sí enlazarán: ¿qué hay detrás de cada nombre — snapshot o
   catálogo vivo — y por qué esa diferencia decide el link? (D-36,
   D-56.)

## Lo que acabas de aprender

- `RequireAdmin` que extiende `RequireAuth` sin sesión (returnTo al
  panel, D-32) y muestra `NoAutorizado` con sesión sin rol — SIN
  expulsar: le falta permiso, no identidad; el espejo UX del 403 (D-55,
  ADR-015/ADR-011 — el claim desde el primer token)
- La rama `/admin` FUERA del Layout de tienda: dos layouts paralelos,
  subnav blanca bajo la navbar crema, sin Footer ni burbuja — la
  trastienda — y el "Panel" del navbar condicionado por rol (D-47 por
  rol)
- BADGES bajada a `src/lib/badges.ts` con la tercera consumidora: una
  sola verdad del estado (D-45), el refactor en el código del alumno con
  las guías 10/11 byte-intactas — y los badges nuevos (Activo/Inactivo,
  Stock bajo) con los tokens del UI-SPEC y el contraste de los DOS
  umbrales (RN-14, Pitfall 6)
- El PRIMER PUT y PATCH del frontend (`apiPut`/`apiPatch` sobre el
  `pedir()` de la guía 6: Bearer, interceptor 401 y detail normalizados
  de herencia) y los tipos admin espejados del contrato 0.4.0
- El editor inline como estado de la pantalla (`editando: producto |
  "nuevo" | null`, sin ruta propia), el form SIN campo activo (nace
  activo, D-52), la validación espejo del 422 con sus 5 copys — y la
  hidratación de descripción/notas desde la ficha pública, con su hueco
  honesto para inactivos
- El toggle sin confirmación (reversible por diseño, feedback = badge en
  el lugar) contra el "Anular" en dos pasos inline (irreversible, patrón
  "Vaciar carro") — la asimetría por reversibilidad hecha regla
- La invalidación por PREFIJO de queryKey: `["productos"]` reacciona
  vitrina y panel juntos, `["pedidos"]` historial y panel — la clienta
  ve "Anulado" sin editar la guía 11 (D-48/D-49)
- El 409 con su copy locked en banner y la fila refrescada con la
  verdad del servidor — y la fila de pedidos SIN link al voucher: el
  detalle es del dueño (404 uniforme, RN-08)
- Las métricas sin gráficos: 3 KPI cards + tabla, cero honesto ($0/0
  explícitos) y el top 5 desde el nombre SNAPSHOT en texto plano (D-36,
  RF-22)

**Siguiente:** guia-14-asistente-backend.md — la asesora de aromas
(backend): el primer endpoint de IA del proyecto con `google-genai`, el
mini-RAG honesto con el catálogo en el prompt, el JSON estructurado que
el backend valida id por id — y la degradación amable cuando no hay key.
