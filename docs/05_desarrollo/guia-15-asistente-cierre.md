# Guía 15 — La burbuja en la tienda: la cara visible de la IA y el cierre de la fase 4

> **Qué construirás hoy:** la cara visible de la IA — la burbuja de la
> asesora flotando sobre TODA la tienda, con su panel de chat, sus cards
> clicables y sus estados amables — y la **Gran verificación final** de la
> fase 4 completa: panel, asistente, contrato 0.4.0 ↔ `/docs` y el grep
> del build que prueba que la key jamás salió del backend.
> **Al terminar tendrás:** la asesora recomendando en una sola respuesta
> con 1-3 cards del catálogo real que abren la ficha — y la fase cerrada
> contra el contrato 0.4.0, fila por fila.
> **Necesitas:** las guías 1 a 14 completas — el endpoint público del
> asistente respondiendo (con TU key para el happy path, sin ella para la
> degradación), el panel de las guías 12-13 operativo y las órdenes reales
> de tu fase 3 esperando las métricas y la anulación. Abre el UI-SPEC de
> la fase 4 (pantalla 14): los copys y las clases de hoy vienen de ahí.

---

## Los términos de hoy (antes de copiar nada)

| Término | Qué es, en una frase |
|---|---|
| **Burbuja flotante** | El botón `fixed` "Pregúntale a Maura" que acompaña toda la tienda y despliega el panel de la asesora — vive en el Layout, no en una ruta |
| **`aria-live`** | El atributo que le dice al lector de pantalla "esta zona cambia sola" — la respuesta de la asesora se anuncia sin que el foco se mueva |
| **Auto-scroll** | `scrollIntoView` al llegar la respuesta: el scroll es INTERNO de la zona de mensajes — la página jamás scrollea por el chat |
| **Import cruzado con razón** | Romper la regla 6 (features sin imports cruzados) documentando POR QUÉ — hoy es la SEGUNDA excepción del proyecto: la `ProductCard` del catálogo reusada en el chat (D-46) |
| **Verificación de bundle** | Revisar lo que el build DE VERDAD embarca: `npm run build` y grep sobre `dist/` — la prueba mecánica de que la key no viajó (AIAS-03) |

---

## Paso 1 — La infraestructura chiquita: `ChatRespuesta` y el POST público

🧠 **El desarrollador piensa:** *dos piezas pequeñas, y las dos son la
misma lección de siempre: lo compartido se escribe UNA vez y el contrato
manda. **El tipo:** el espejo manual de la guía 2 (D-09) — abrir el
`contrato_api.yaml` 0.4.0 y traducir `ChatRespuesta` campo a campo. Lo
que NO trae es la mitad de la lección: no hay token, ni sesión, ni
estado — `respuesta` y `productos` nada más, porque el backend ya hizo
todo el trabajo (los ids llegan validados contra el catálogo activo,
D-56). **El verbo:** la burbuja manda un POST JSON… público. Y aquí hay
una decisión heredada que conviene mirar de nuevo: `apiPost` de la guía
6 adjunta el Bearer si hay sesión — correcto para TODO lo que exige
token, innecesario para un endpoint que no lo pide. La visitante anónima
que hojea el catálogo no tiene token que adjuntar; y una clienta con
sesión no necesita mandarlo: `/api/asistente` es `security: []` a
propósito (D-59). ¿Recuerdas el flag `sinAuth` que el login estrenó para
que su 401 no disparara el interceptor? Mismo flag, tercer uso: un POST
JSON que JAMÁS lleva Bearer, construido sobre el mismo `pedir()` — con su
interceptor 401 desactivado para esta llamada (una visita sin sesión no
puede "expirar"). Y una decisión que NO tomamos también es contenido:
el chat NO es `useQuery` — no hay nada que cachear, refrescar ni
re-fetchear: cada mensaje es un ENVÍO puntual con una respuesta única
(D-57). La respuesta única se llama mutación, y el paso 2 la escribe.*

En **`frontend/src/types/api.ts`**, agrega al final:

```typescript
// --- Etapa 4: la asesora de aromas (espejo de contrato_api.yaml 0.4.0) ---

// Quién escribió cada mensaje del historial visible (ChatMensaje.rol)
export type RolChat = "clienta" | "asesora";

export interface ChatRespuesta {
  respuesta: string; // el texto de la asesora — voz de Maura (D-02)
  productos: number[]; // ids YA validados contra el catálogo activo por el backend (D-56) — máximo 3
}
```

Y en **`frontend/src/lib/api.ts`**, agrega al final:

```typescript
// --- Etapa 4: el chat de la asesora (guía 15) ---
// POST JSON PÚBLICO: el molde de apiPost con el sinAuth que el login
// estrenó — /api/asistente no pide sesión (D-59) y la burbuja la usa una
// visitante anónima: sin Bearer aunque el store tenga un token, y sin
// interceptor 401 para esta llamada (no hay sesión que expirar).
export async function apiPostPublico<T>(ruta: string, cuerpo: unknown): Promise<T> {
  return pedir<T>(
    ruta,
    {
      method: "POST",
      body: JSON.stringify(cuerpo),
      headers: { "Content-Type": "application/json" },
    },
    { sinAuth: true },
  );
}
```

✅ **Mini-verificación:** `npm run build` pasa — y el experimento del
compilador de siempre, ahora con la ausencia que importa: el tipo
`ChatRespuesta` no tiene campo para token, sesión ni estado. El
frontend no puede ni nombrar lo que el backend no le manda.

---

## Paso 2 — `BurbujaAsesora.tsx`: el contrato completo de la pantalla 14

🧠 **El desarrollador piensa:** *el componente más nuevo del proyecto — y
el primero que FLOTA. La pantalla 14 del UI-SPEC es el contrato, y trae
las DOS excepciones declaradas de la fase, que no son decoration:
**`shadow-lg`** — el contrato de fase 1 limitaba la sombra al hover de la
ProductCard, pero un elemento `fixed` necesita elevación para leerse como
flotante SOBRE la página: la excepción cubre exactamente los dos elementos
flotantes (el botón y el panel desplegado) y nada más; **`max-h-[70vh]`**
— una altura que depende del viewport no puede ser múltiplo fijo de la
escala de spacing: es la excepción documentada, y la razón de que el chat
nunca tape la tienda en un notebook chico. Con esas dos firmadas, el
resto es tokens de siempre. **El botón** lleva `aria-expanded` y
`aria-controls` apuntando al panel: un lector de pantalla anuncia "se
despliega" antes de que exista. **La zona de mensajes** es la parte con
más detalles por centímetro cuadrado del proyecto: `aria-live="polite"`
(la respuesta se anuncia sola), `overflow-y-auto` (el scroll es interno —
header e input fijos, la página jamás scrollea por el chat) y el
auto-scroll con `scrollIntoView` al llegar cada respuesta. **El
historial es stateless POR DECISIÓN (D-58):** un arreglo en estado del
componente — sobrevive la navegación interna de la SPA (el Layout no se
desmonta al cambiar de ruta) y parte de cero tras un full-page load; el
backend no guarda conversaciones ni existe tabla de mensajes. La primera
entrada es la bienvenida LOCAL: se renderiza sin llamar al servicio
de IA, cero cuota — el panel jamás abre con la zona de mensajes en
blanco. **La
mutación (D-57):** `useMutation` por request, NO `useQuery` — respuesta
única, sin caché ni refetch; en vuelo, el mensaje de la clienta aparece
inmediato, una burbuja `animate-pulse` de la asesora hace la espera
honesta (sin streaming que la disimule) y Enviar queda `disabled` — el
anti doble envío de los submits de siempre. El historial que viaja se
arma ANTES de agregar el mensaje nuevo: lo ya dicho va en `historial`,
lo nuevo en `mensaje` — el contrato separa las dos cosas y el payload lo
respeta, con el tope de 10 (RN-16) aplicado con `slice`. **Las cards:
el reuso LITERAL de `ProductCard`** del catálogo, con import cruzado con
razón — la SEGUNDA excepción de la regla 6, el mismo patrón de
`VoucherPedido` en la guía 11 (D-46): duplicar la card serían dos
verdades del mismo producto. Y como el chat recibe IDS (no productos),
la hidratación es la de la guía 7: `useQueries` con el MISMO queryKey de
la ficha — con `String(id)`, el gotcha: `("producto", "1")` y
`("producto", 1)` son cachés distintas. ¿Y si el modelo citara algo
raro? No puede llegarte: los ids que el endpoint devuelve ya pasaron la
muralla del backend (D-56) — si la respuesta trae `productos: []`, solo
texto, sin cards rotas. **Los estados del error** con sus copys locked
del contrato: 503 → "no disponible… más tarde", 429 → "muchas
consultas… unos segundos" (SIN cifras — no son públicas), y la familia
de red de todo el sistema (puerto 8000); cada uno con su
**Reintentar**, que reenvía el último mensaje con `envio.variables` —
el payload ya armado, exactamente igual. Y la regla de render más
importante del día: el texto de la asesora se renderiza como
**TEXTO** — `{m.texto}` entre llaves, el escape por defecto de React.
El atributo que inyecta HTML crudo (el que arranca con `dangerously`)
no existe en este proyecto y no se escribe: el modelo podría devolver
markup y el chat sería un XSS andante (T-04-11).*

Crea la carpeta **`frontend/src/features/asistente/`** y
**`frontend/src/features/asistente/BurbujaAsesora.tsx`**:

```tsx
// La burbuja de la asesora (pantalla 14 del diseño, AIAS-01/02): chat
// público request-response (D-57) con historial stateless en el
// componente (D-58). Los ids de las cards llegan YA validados contra el
// catálogo activo por el backend (D-56): este archivo renderiza, no
// verifica — la muralla anti-alucinación es del servidor (guía 14).
import { useMutation, useQueries } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";

import { ApiError, apiGet, apiPostPublico } from "../../lib/api";
import type { ChatRespuesta, ProductoDetalle, RolChat } from "../../types/api";
import ProductCard from "../catalogo/ProductCard"; // regla 6 CON razón: la SEGUNDA excepción (D-46)

const BIENVENIDA =
  "¡Hola! Soy la asesora de Maura. Cuéntame qué aromas te gustan y te recomiendo del catálogo.";
const MAX_HISTORIAL = 10; // RN-16: lo máximo que viaja en cada request

// Un mensaje del historial visible. productos solo existe en las
// respuestas de la asesora — ids que el backend ya validó (D-56).
interface MensajeChat {
  rol: RolChat;
  texto: string;
  productos?: number[];
}

// Lo que viaja en cada POST: el mensaje nuevo + el historial visible —
// el backend no guarda nada (D-58, ChatMensaje del contrato).
interface EnvioChat {
  mensaje: string;
  historial: { rol: RolChat; texto: string }[];
}

// Las cards de una respuesta (AIAS-02): hidratación por id con el MISMO
// queryKey de la ficha — String(id), el gotcha de la guía 7. Los ids
// llegan validados contra el catálogo ACTIVO: cada ficha responde 200.
function CardsRecomendacion({ ids }: { ids: number[] }) {
  const resultados = useQueries({
    queries: ids.map((id) => ({
      queryKey: ["producto", String(id)],
      queryFn: () => apiGet<ProductoDetalle>(`api/productos/${id}`),
    })),
  });
  return (
    <div className="flex flex-col gap-2">
      {resultados.map((r, i) =>
        r.data ? <ProductCard key={ids[i]} producto={r.data} /> : null,
      )}
    </div>
  );
}

export default function BurbujaAsesora() {
  const [abierto, setAbierto] = useState(false);

  // El historial vive en estado del COMPONENTE (D-58): sobrevive la
  // navegación interna (el Layout no se desmonta) y parte de cero tras
  // un full-page load. La bienvenida es LOCAL: render sin llamada al
  // servicio de IA — cero cuota, y el panel jamás abre en blanco.
  const [mensajes, setMensajes] = useState<MensajeChat[]>([
    { rol: "asesora", texto: BIENVENIDA },
  ]);
  const [entrada, setEntrada] = useState("");

  // Respuesta ÚNICA por request (D-57): useMutation, NO useQuery — no
  // hay nada que cachear ni refrescar; cada mensaje es un envío puntual.
  const envio = useMutation({
    mutationFn: (datos: EnvioChat) =>
      apiPostPublico<ChatRespuesta>("api/asistente", datos),
    onSuccess: (respuesta) => {
      setMensajes((actuales) => [
        ...actuales,
        {
          rol: "asesora",
          texto: respuesta.respuesta,
          productos: respuesta.productos,
        },
      ]);
    },
  });

  // Auto-scroll al último mensaje (pantalla 14): scrollIntoView dentro
  // de la zona con overflow-y-auto — la página no se entera.
  const finRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    finRef.current?.scrollIntoView({ block: "end" });
  }, [mensajes, envio.isPending]);

  function enviar() {
    const texto = entrada.trim();
    if (!texto || envio.isPending) return; // segundo candado del anti doble envío
    // El historial se arma ANTES de agregar el mensaje nuevo: lo ya
    // dicho viaja en historial; lo nuevo, en mensaje — como el contrato
    // separa las dos cosas. slice(-10): el tope de RN-16 en el borde.
    const historial = mensajes
      .slice(-MAX_HISTORIAL)
      .map(({ rol, texto: t }) => ({ rol, texto: t }));
    setMensajes((actuales) => [...actuales, { rol: "clienta", texto }]);
    setEntrada("");
    envio.mutate({ mensaje: texto, historial });
  }

  // El copy del error por causa (los example del contrato 0.4.0): 503
  // degradación (D-61), 429 cuota SIN cifras (no son públicas sin login)
  // — y si ni siquiera hubo HTTP (red caída), la familia de siempre.
  const errorChat =
    envio.error instanceof ApiError && envio.error.status === 503
      ? "La asesora no está disponible en este momento. Inténtalo más tarde."
      : envio.error instanceof ApiError && envio.error.status === 429
        ? "La asesora está recibiendo muchas consultas. Espera unos segundos y reintenta."
        : "No pudimos conectar con el servidor. Revisa que el backend esté corriendo en el puerto 8000 e inténtalo de nuevo.";

  return (
    <>
      {/* La burbuja cerrada: fixed bottom-6 right-6 — una de las DOS
          excepciones de sombra de la fase (elemento flotante). */}
      <button
        type="button"
        onClick={() => setAbierto((a) => !a)}
        aria-expanded={abierto}
        aria-controls="panel-asesora"
        className="fixed bottom-6 right-6 rounded-full bg-orange-600 text-white font-bold text-sm px-4 py-2 min-h-11 hover:bg-orange-700 shadow-lg focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
      >
        Pregúntale a Maura
      </button>

      {abierto && (
        <section
          id="panel-asesora"
          className="fixed bottom-20 right-6 w-80 sm:w-96 max-h-[70vh] bg-white rounded-2xl border border-orange-100 shadow-lg flex flex-col"
        >
          <header className="bg-orange-50 rounded-t-2xl p-4">
            <div className="flex items-start justify-between gap-2">
              <div>
                <h2 className="text-xl font-bold text-neutral-900">
                  Asesora de aromas
                </h2>
                <p className="text-sm text-neutral-600">
                  Recomendaciones del catálogo de Maura
                </p>
              </div>
              <button
                type="button"
                onClick={() => setAbierto(false)}
                className="text-sm text-neutral-600 font-bold min-h-11 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
              >
                Cerrar
              </button>
            </div>
          </header>

          {/* La zona de mensajes: aria-live anuncia las respuestas; el
              scroll es INTERNO (overflow-y-auto) — header e input fijos. */}
          <div
            className="p-4 overflow-y-auto flex flex-col gap-2"
            aria-live="polite"
          >
            {mensajes.map((m, i) =>
              m.rol === "asesora" ? (
                <div key={i} className="self-start max-w-full flex flex-col gap-2">
                  {/* El texto del modelo se renderiza como TEXTO ({m.texto}
                      entre llaves): React escapa por defecto — jamás HTML. */}
                  <div className="bg-orange-50 rounded-2xl p-2 text-sm leading-relaxed">
                    {m.texto}
                  </div>
                  {m.productos && m.productos.length > 0 && (
                    <CardsRecomendacion ids={m.productos} />
                  )}
                </div>
              ) : (
                <div
                  key={i}
                  className="self-end bg-orange-600 text-white rounded-2xl p-2 text-sm leading-relaxed"
                >
                  {m.texto}
                </div>
              ),
            )}

            {/* En vuelo (D-57): la espera honesta — una burbuja que late,
                sin streaming que la disimule. */}
            {envio.isPending && (
              <div
                aria-hidden="true"
                className="self-start w-28 h-9 animate-pulse bg-orange-50 rounded-2xl p-2"
              />
            )}

            {/* El error con su copy por causa + Reintentar que reenvía el
                último mensaje (el payload YA armado vive en variables). */}
            {envio.isError && (
              <div className="self-start max-w-full bg-red-50 text-red-600 rounded-2xl p-2 text-sm leading-relaxed flex flex-col gap-2">
                <p>{errorChat}</p>
                {envio.variables && (
                  <button
                    type="button"
                    onClick={() => envio.mutate(envio.variables)}
                    className="text-left text-orange-600 font-bold min-h-11 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
                  >
                    Reintentar
                  </button>
                )}
              </div>
            )}

            <div ref={finRef} />
          </div>

          <form
            className="p-4 border-t border-orange-100 flex gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              enviar();
            }}
          >
            <input
              type="text"
              value={entrada}
              onChange={(e) => setEntrada(e.target.value)}
              aria-label="Escribe tu mensaje"
              placeholder="¿Qué aroma buscas?"
              maxLength={500}
              className="flex-1 rounded-lg border border-orange-200 bg-white px-4 py-2 min-h-11 text-base focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
            />
            <button
              type="submit"
              disabled={envio.isPending}
              className="rounded-full bg-orange-600 text-white font-bold text-sm px-4 py-2 min-h-11 hover:bg-orange-700 disabled:opacity-60 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
            >
              Enviar
            </button>
          </form>
        </section>
      )}
    </>
  );
}
```

✅ **Mini-verificación:** `npm run build` pasa — y con el servidor de
desarrollo puesto, el experimento rápido: importa el componente en
cualquier página temporalmente… no hace falta: el paso siguiente lo
monta donde vive de verdad. Lo que el build ya probó: el import cruzado
resuelve, `String(id)` compila y los tipos calzan con el contrato.

---

## Paso 3 — El montaje: la burbuja vive en el Layout de la TIENDA (y solo ahí)

🧠 **El desarrollador piensa:** *¿dónde se monta un componente que debe
"acompañar toda la tienda"? La respuesta de la guía 13 sigue en pie: en
el ROUTER, la estructura decide — y hoy la estructura ya tiene DOS ramas
de layout paralelas. La burbuja va DENTRO del `Layout` de tienda
(`components/Layout.tsx`): por eso la ven las rutas públicas Y las de
clienta (todas atienden a la shopper, con o sin cuenta — D-59), y por
eso NO la ve `/admin`: esa ruta vive en la OTRA rama, bajo
`LayoutAdmin`, FUERA del Layout de tienda — la dueña no necesita que su
propia asesora le venda stock (guía 13, paso 4). Cero condicionales de
ruta, cero lógica: la ubicación en el árbol ES la regla. Y el import
que esto exige — `components/Layout` importando de
`features/asistente` — es la MISMA dirección de excepción que la guía
13 narró para `RequireAdmin → NoAutorizado`: components importando una
pieza de un feature, con la razón dicha en voz alta (la burbuja es una
pieza de la asesora; su hogar natural es su feature). La regla 6 veta
features importando features SIN razón — y su segunda excepción (la
ProductCard) ya quedó firmada en el paso 2 con el patrón D-46.*

En **`frontend/src/components/Layout.tsx`**, agrega el import y la
pieza:

```tsx
import { Outlet } from "react-router";

import BurbujaAsesora from "../features/asistente/BurbujaAsesora"; // components → feature: la burbuja acompaña TODA la tienda (D-59)
import Footer from "./Footer";
import Navbar from "./Navbar";

export default function Layout() {
  return (
    <div className="flex min-h-screen flex-col bg-white">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
      {/* La asesora flotando sobre la tienda (pantalla 14): rutas
          públicas y de clienta — /admin vive en la OTRA rama de layout y
          no la ve (guía 13). */}
      <BurbujaAsesora />
    </div>
  );
}
```

✅ **Mini-verificación:** con ambos servidores corriendo (`uv run
fastapi dev app/main.py` en `backend/`, `npm run dev` en `frontend/`),
abre **http://localhost:5173**: el botón **"Pregúntale a Maura"** flota
abajo a la derecha en la portada, en el catálogo y en la ficha.
Navega entre ellas: la burbuja NO parpadea — el Layout no se desmonta.
Y ahora fuerza **/admin** (con tu sesión de admin): la burbuja NO está
— la trastienda es otra rama.

---

## Paso 4 — La prueba de fuego: bienvenida sin cuota, cards clicables y la degradación amable

🧠 **El desarrollador piensa:** *la batería del navegador, y cada golpe
una promesa. La bienvenida que no gasta cuota — el panel abre con
mensaje sin que exista request (mira la pestaña Network: CERO llamadas
al abrir). La recomendación con la voz de Maura y sus cards — que son LA
MISMA card del catálogo (clic y a la ficha: la excepción de la regla 6
funcionando). La degradación: comentar la key y reiniciar — la burbuja
SIGUE ahí (no se esconde: la tienda no se avergüenza de tener un
servicio opcional caído), avisa amable y ofrece Reintentar; y la tienda
entera sigue comprando. Y el detalle fino del historial: recarga la
página completa (F5) — el chat parte de cero con la bienvenida:
stateless por diseño (D-58), nadie guarda tu conversación. ¿El 429? Ese
no lo puedes provocar a voluntad sin quemar tu cuota a propósito — su
copy está listo y su copy no promete cifras que nadie puede verificar
(concern abierto): confía en el wrapper de la guía 14, que ya probiste
con los topes del 422.*

Con ambos servidores corriendo y TU key en el `.env` del backend:

✅ **Mini-verificación (la bienvenida sin cuota):** abre la burbuja con
el panel de Network a la vista: aparece "¡Hola! Soy la asesora de
Maura…" **sin ninguna llamada a `/api/asistente`** — la bienvenida es
local (D-58): cero cuota, cero red, y el panel jamás abre en blanco.

✅ **Mini-verificación (la recomendación con cards clicables):** escribe
"algo cítrico para el día" y presiona Enviar: tu mensaje aparece al instante
(burbuja terracota a la derecha), la burbuja de la asesora LATE mientras
espera (`animate-pulse`, Enviar deshabilitado), y llega UNA respuesta
con la voz de Maura — con 0 a 3 cards debajo del texto. Clic una card:
abre la FICHA de ese aroma — la misma ProductCard del catálogo, la
misma caché de la guía 7 (import cruzado con razón, D-46). Vuelve y
sigue la conversación: el historial sigue en pantalla (el Layout no se
desmontó) y viaja entero en cada envío.

✅ **Mini-verificación (la degradación amable, sin key):** comenta la
línea `GROQ_API_KEY` del `.env` del backend, reinicia la API y manda
un mensaje: la burbuja de error roja con **"La asesora no está
disponible en este momento. Inténtalo más tarde."** y el link
**Reintentar** — la burbuja flotante SIGUE en su lugar (D-61: no se
esconde). Ahora navega: catálogo, login, tu carro — TODO funciona. Y F5:
el chat parte de cero (stateless). Descomenta la key, reinicia, y
**Reintentar**: la respuesta llega — el último mensaje reenviado tal
cual (el payload vivía en `envio.variables`).

✅ **Mini-verificación (la burbuja NO está en el panel):** entra como
admin a **/admin**: sin burbuja — la rama del panel tiene su propio
layout (guía 13) y la asesora acompaña a la clienta, no a la dueña.

---

## ✅ Gran verificación final de la fase 4

La tabla de cierre del ciclo — como en las fases 1, 2 y 3, cada fila
cita su origen y se marca solo si TÚ la comprobaste. Las credenciales
son las de TU `.env` (las sembró la guía 5); para la fila 8 necesitas TU
key de console.groq.com (guía 14); las filas 9 y 10 no necesitan key:

| # | Verificación | Origen |
|---|---|---|
| 1 | Roles en `/docs` con las cuentas del seed: el admin ejecuta los 7 paths de administración → 200; la clienta (token PERFECTAMENTE válido) → 403 "Requiere rol admin" en cada uno — la seguridad es del servidor, el guard de la SPA es UX | RF-19..RF-22, D-55, ADR-015 |
| 2 | La clienta con sesión fuerza **/admin** → "No tienes acceso al panel" SIN expulsión al login y A SECAS (sin navbar ni subnav: el guard vetó la rama entera) — "Volver a la tienda" la recibe con su sesión viva: le falta permiso, no identidad — y sin sesión, login → vuelta AL panel (returnTo) | D-55, HU-12, ADR-015 |
| 3 | CRUD del catálogo: "Nuevo producto" nace activo con sku generado; el editor escribe la allow-list (un `"activo": false` inyectado a mano no tiene dónde entrar) y dos guardados con el mismo body dejan el mismo estado | RF-19, HU-12, D-52 |
| 4 | Stock bajo del panel: badge "Stock bajo" SOLO en activos con ≤ 5 — y la ficha de la tienda sigue con SU umbral 1-3 ("últimas unidades"): dos umbrales, dos públicos, dos textos | RF-20, RN-14 |
| 5 | Soft delete con sus DOS caras: desactivar un aroma → DESAPARECE del catálogo público en la misma sesión (invalidación por prefijo) y tu pedido viejo de fase 3 conserva el snapshot de nombre y precio | RF-19, D-52, D-36, HU-12 |
| 6 | La huérfana PENDING de fase 3: "Anular" en dos pasos → badge "Anulado" sin tocar stock; repetir la anulación en otra pestaña → 409 "Ese pedido ya no está en curso."; y la clienta la ve "Anulado" en SU historial — la guía 11 intacta mostrando una verdad que otra pantalla cambió | RF-21, RN-15, ADR-016, D-48/D-49 |
| 7 | Métricas contra las órdenes REALES de tu fase 3: ingresos = la suma exacta de tus PAID, los 4 estados con sus conteos (la anulada ya suma), top 5 con los nombres DE ÉPOCA (snapshot) y el conteo de stock bajo | RF-22, D-54, D-36 |
| 8 | La burbuja abre con la bienvenida LOCAL (cero requests en Network, cero cuota) y la asesora recomienda con la voz de Maura en UNA respuesta con 1-3 cards clicables que abren la ficha — la misma ProductCard del catálogo | RF-23, RF-24, HU-13, D-57/D-58/D-46, ADR-017/ADR-018 |
| 9 | Los topes del chat validan en el borde: mensaje de 501 caracteres → 422; historial de 11 entradas → 422 — ANTES de tocar el servicio de IA, sin gastar cuota | RN-16, D-59 |
| 10 | Degradación sin key: comentar `GROQ_API_KEY` del `.env`, reiniciar → POST 503 con "La asesora no está disponible…" y la burbuja avisando con Reintentar — mientras login, catálogo, carro, checkout y panel siguen 100% operativos | RNF-08, D-61, ADR-017 |
| 11 | La burbuja acompaña TODA la tienda — portada, catálogo, ficha, carro, checkout, pedidos, con y sin sesión (pública, D-59) — y NO existe dentro de /admin: dos ramas de layout, cero condicionales | RF-23, D-55, D-59 |
| 12 | **Contrato ↔ `/docs`**: abre `http://localhost:8000/docs` y compara UNO A UNO contra `docs/04_arquitectura/contrato_api.yaml` **0.4.0**: los paths NUEVOS (los 7 de administración + `/api/asistente`), el **409/429/503 declarados** en las firmas (las HTTPException manuales, visibles — lección G-01-4), el endpoint público del asistente SIN candado (`security: []` a propósito, como el retorno de Webpay) — y el botón **Authorize** probado con la cuenta admin del seed AHORA contra el CRUD real: 200 en los paths donde la clienta vio el 403 | ADR-007, GUIDE-02, ADR-015, ADR-017 |
| 13 | **El grep del build** (AIAS-03): `npm run build` y, DESPUÉS de que termine, busca `GROQ_API_KEY` en el `dist/` regenerado — **CERO coincidencias** (control positivo: `grep -r "Pregúntale a Maura" dist/` SÍ encuentra — el grep funciona; lo ausente es la key). Git Bash: `grep -r "GROQ_API_KEY" dist/` (sin output es el éxito); PowerShell: `Select-String -Path dist\* -Pattern "GROQ_API_KEY"` (findstr invocado desde Git Bash corrompe sus switches — Pitfall 8). La prueba mecánica de que la key vive solo en el backend: cualquier variable `VITE_*` termina en el bundle — la key, nunca | RNF-09, AIAS-03, D-60 |

La fila 12 es la evidencia formal del cierre, y esta fase le suma una
pieza que se queda para siempre: la fila 13. **Cualquier diferencia entre
el panel y el contrato es un desvío — o el código corrige, o el contrato
se versiona y se aprueba de nuevo; jamás cambia en silencio.** El
contrato vive en el repositorio de la guía; el `/docs` y el `dist/` viven
en tu máquina — compararlos y grepearlos es tu trabajo de cierre, y este
mismo mecanismo se repite al final de cada fase del proyecto. (Nota
honesta para la fila 8: el happy path del asistente — la llamada REAL al
servicio de IA — requiere TU key: en el aula, cada quien con la suya
(console.groq.com, D-63). Las filas 9, 10 y 13 no dependen de ninguna
key.)

**Sugerencia de commit para cerrar la fase** (en TU proyecto):

```
git add -A
git commit -m "Fase 4 completa: panel de administración y asesora IA según guías 12-15

Cumple el contrato OpenAPI 0.4.0 (verificación /docs con Authorize, sin
desvíos; el grep del build sin rastro de la API key) y respeta los 18
ADRs del proyecto."
```

---

## ❌ El error que este archivo evita

**1. Renderizar el texto del modelo como HTML.**

```tsx
// ❌ "para que la asesora pueda usar negritas y emojis bonitos" — el
// atributo de React que inyecta HTML crudo (el que arranca con
// `dangerously`): el modelo devolvería markup y el chat, un XSS andante
<div dangerously-... />  // VETADO: ni se escribe en este proyecto

// ✅ {m.texto} entre llaves: React escapa por defecto — el texto es
// texto, con text-sm leading-relaxed y wrap natural
<div className="bg-orange-50 rounded-2xl p-2 text-sm leading-relaxed">
  {m.texto}
</div>
```

El modelo NO es de confianza: un visitante puede pedirle que devuelva
HTML (prompt injection, T-04-11) y el chat es un panel público. El
escape por defecto de React es la muralla del render — y cuesta cero:
es lo que pasa cuando NO haces nada especial.

**2. `useQuery` para el chat (o un streaming casero que disimule la espera).**

```tsx
// ❌ una query cacheable con refetch — como si la respuesta fuera un
// dato que "cargar"; y peor: un loop de polling o un falso streaming
const chat = useQuery({ queryFn: () => apiPostPublico(...) })

// ✅ useMutation por request: cada mensaje es un ENVÍO puntual con una
// respuesta única (D-57) — y en vuelo, la burbuja animate-pulse honra la
// espera en vez de esconderla
const envio = useMutation({ mutationFn: (datos) => apiPostPublico(...) });
```

TanStack Query separa dos mundos: datos que se CARGAN (queries, con
caché e invalidación) y acciones que se EJECUTAN (mutaciones). El chat
es una acción — cachear una conversación sería reírse de la persona que
acaba de preguntar.

**3. Persistir la conversación (tabla de mensajes, sesión de chat en el backend).**

```python
# ❌ "para que la clienta retome su conversación" — una tabla mensajes
# con FK al chat… y el asistente deja de ser stateless (D-58)
class MensajeChat(BaseModel): ...

# ✅ el historial visible vive en el NAVEGADOR y viaja en cada request
# (máx 10): cero tablas nuevas, cero estado del servidor — tras un F5
# parte de cero, y eso es una decisión, no un bug
historial: list[MensajeHistorial] = Field(max_length=10)
```

La conversación es UI, no dato de negocio: nadie la consulta mañana.
Guardarla agregaría una tabla, una limpieza y una superficie de privacidad
— para que el historial sobreviva un F5, que el diseño decidió que no
sobreviva (D-58).

**4. Esconder la burbuja cuando el servicio está caído (o montarla en /admin).**

```tsx
// ❌ "si no hay key, mejor ni mostramos el chat" — el componente decide
// por el negocio qué piezas existen
{hayKey && <BurbujaAsesora />}

// ✅ la burbuja SIEMPRE está (D-61): sin key avisa amable y ofrece
// Reintentar — la tienda no esconde que tiene un servicio opcional
// caído; y su hogar es el Layout de TIENDA: /admin es otra rama
<BurbujaAsesora />
```

La degradación es una PROMESA de usuario, no una mancha: "la asesora no
está disponible ahora" es información honesta — quitar la burbuja sería
la tienda fingiendo que la asesora nunca existió. Y montarla en el panel
le vendería stock a su propia dueña.

---

## ✅ Verificación de la guía 15

Con ambos servidores corriendo, el seed corrido y TU key en el `.env`:

1. `npm run build` pasa — tipos espejados, `apiPostPublico`, la burbuja
   completa y el montaje en el Layout.
2. La burbuja en TODA la tienda (públicas y de clienta) y NO en `/admin`
   — dos ramas de layout, cero condicionales (D-55/D-59).
3. La bienvenida local sin requests en Network (cero cuota) — y tras F5,
   el chat parte de cero (D-58).
4. "Algo cítrico para el día" → UNA respuesta con voz de Maura, 0-3
   cards clicables (la ProductCard del catálogo reusada, D-46) y el
   historial que sobrevive la navegación interna.
5. Sin key: 503 con su copy y Reintentar que reenvía el último mensaje
   — la tienda 100% operativa (D-61).
6. La tabla de la Gran verificación final, fila por fila — con la 12
   comparando el contrato 0.4.0 contra `/docs` (Authorize admin contra
   el CRUD real) y la 13 grepando el build SIN rastro de la key.

## 📝 Punto de control (respóndelas sin mirar la guía)

1. El chat NO usa `useQuery` ni caché: ¿qué propiedad de la respuesta
   lo hace una MUTACIÓN y no una carga de datos — y qué gana la
   experiencia al mostrar la burbuja `animate-pulse` en vez de
   disimular la espera? (D-57.)
2. Tras un F5 la conversación desaparece; tras navegar dentro de la SPA,
   sobrevive. ¿Qué pieza de la arquitectura explica la diferencia — y
   por qué el backend ni se entera de cuál de las dos acaba de pasar?
   (D-58.)
3. Las cards del chat son la ProductCard del catálogo con un import
   cruzado entre features: ¿qué regla se rompe, con qué razón se
   justifica — y qué pasaría con la ficha del producto si el chat
   tuviera SU PROPIA card? (Regla 6, D-46, segunda excepción.)
4. Dos requests al asistente disparados en paralelo (o uno abortado a
   mitad) no corrompen nada: ¿qué propiedad de la llamada del service
   lo garantiza — y a qué señal se traduce la interrupción para el
   cliente? (D-57, guía 14: stateless por request, IN-06.)
5. El grep del build busca `GROQ_API_KEY` en `dist/` y espera CERO
   coincidencias: ¿por qué una variable `VITE_` SÍ aparecería — y por
   qué ese grep corre DESPUÉS de `npm run build` y no antes? (RNF-09,
   AIAS-03, Pitfall 8.)

## Lo que acabas de aprender

- La burbuja flotante con el contrato completo de la pantalla 14: botón
  `fixed` con `aria-expanded`/`aria-controls`, panel `max-h-[70vh]` con
  header fijo, zona de mensajes con `aria-live="polite"`, scroll INTERNO
  + `scrollIntoView` (la página jamás scrollea por el chat) y las DOS
  excepciones declaradas de la fase (`shadow-lg` flotante,
  `max-h-[70vh]` viewport-relativa)
- El historial stateless (D-58): estado del componente, sobrevive la
  navegación interna, parte de cero tras F5 — con la bienvenida LOCAL
  que calienta el contexto sin gastar cuota
- `useMutation` por request (D-57): respuesta única, en vuelo el
  mensaje inmediato + burbuja `animate-pulse` + Enviar disabled — y
  `envio.variables` como el payload del Reintentar
- La SEGUNDA excepción de la regla 6 (D-46): la ProductCard del
  catálogo reusada en el chat con import cruzado con razón — e hidratada
  por id con el MISMO queryKey de la ficha (`String(id)`, el gotcha de
  la guía 7); `productos: []` → solo texto, sin cards rotas
- Los tres estados del chat con sus copys locked (503 degradación D-61,
  429 sin cifras, red puerto 8000) y el texto del modelo renderizado
  como TEXTO — el escape por defecto de React como muralla del render
- La Gran verificación final de la fase 4: 13 filas con Origen — panel
  (roles, CRUD, soft delete, la huérfana anulada, métricas contra tus
  órdenes reales), asistente completo, la fila contrato 0.4.0 ↔ `/docs`
  con Authorize admin contra el CRUD real — y la fila nueva FIJA que las
  fases futuras heredan: el grep del build (`GROQ_API_KEY` sin
  coincidencias en `dist/`, comando por shell, Pitfall 8)

**Siguiente:** la fase 5 — el despliegue: la tienda y su API en internet
con tier gratuito… y la que congela el `return_url` que Webpay exige
(la URL pública de TU backend, definida al fin). La clave: TODO lo
construido hasta hoy corriendo en vivo — con el contrato, los 18 ADRs y
el grep del build como red de seguridad.
