# Guía 6 — La sesión en la SPA: el store que recuerda a la clienta

> **Qué construirás hoy:** la sesión en la SPA — el store que recuerda a la
> clienta entre recargas, el login y el registro conectados a tu API, el
> navbar que la saluda y el interceptor que blinda toda la app contra el 401.
> **Al terminar tendrás:** login y registro funcionando contra tu API de la
> guía 5, sesión que sobrevive recargas (AUTH-02), y el patrón de ruta
> protegida con retorno que la etapa 3 y el panel de la fase 4 heredan
> (D-32).
> **Necesitas:** la guía 5 completa — backend con las cuentas sembradas
> (re-siembra imprime dos `[=]`) y la API encendida en el puerto 8000 — y el
> frontend de las guías 2 y 4 corriendo con `npm run dev`. Y las credenciales
> demo de TU `.env` a mano: son las que probarás.

---

## Los términos de hoy (antes de copiar nada)

| Término | Qué es, en una frase |
|---|---|
| **Store de cliente** | El estado que vive SOLO en el navegador (sesión, carro): no existe en el servidor, no viaja por HTTP — Zustand lo crea y lo expone con un hook |
| **`persist`** | El middleware de Zustand que guarda el store en `localStorage` y lo re-hidrata al partir: la memoria de la clienta |
| **`partialize`** | El filtro que decide QUÉ se persiste: solo datos, jamás funciones — serializar una función a JSON no existe |
| **Hidratación (síncrona)** | Leer de vuelta lo persistido al crear el store: `localStorage` es síncrono, así que la sesión está disponible en el PRIMER render, sin parpadeo |
| **Interceptor 401** | El centinela de `lib/api.ts`: cualquier llamada autenticada que responda 401 cierra la sesión y expulsa al login con aviso (D-22) |
| **Guard de ruta** | El componente que decide si una ruta se renderiza sin sesión (`RequireAuth`): pura UX — la seguridad real es el 401/403 del backend |
| **returnTo** | "Volver a donde venía": el guard guarda la ruta destino en el `state` y el login te devuelve a ella — genérico para cualquier ruta protegida futura (D-32) |

---

## Paso 1 — Zustand: el store de cliente

🧠 **El desarrollador piensa:** *la guía 2 instaló TanStack Query para el
estado del SERVIDOR (catálogo: cacheado, revalidable, con retries). Hoy
instalo Zustand para el estado del CLIENTE — y la distinción no es
tecnológica, es de dueño. La sesión (¿quién soy?) y el carro (¿qué llevo?)
no viven en ningún servidor de esta etapa: los decide el navegador, se
mutan al instante y deben SOBREVIVIR recargas. Ese es exactamente el caso
de uso de un store de cliente: persistencia local y mutaciones síncronas,
sin caché ni invalidación que administrar. Dos herramientas, dos dueños —
mezclarlas (cachear la sesión en Query, o persistir el catálogo en un
store) es pagar el costo de una para el problema de la otra.*

Desde `frontend/`, ejecuta:

```
npm install zustand
```

✅ **Mini-verificación:** tu `package.json` gana `"zustand": "^5.x"` y
`npm run build` sigue pasando — una dependencia nueva que TypeScript ya
revisa antes que tú.

---

## Paso 2 — `types/api.ts`: los schemas nuevos, espejados a mano

🧠 **El desarrollador piensa:** *el mismo ejercicio de la guía 2 (D-09
heredado): abrir `contrato_api.yaml` 0.2.0 y traducir sus schemas nuevos a
TypeScript, campo a campo, SIN generación automática. `UsuarioPublico`
(id/email/rol — fíjate que `hashed_password` no existe: no cruza la
frontera, RN-07), `Token` (access_token/token_type) y `RegistroPayload`
(espejo de `RegistroCreate`). Escribir `rol: Rol` con
`Rol = "cliente" | "admin"` es leer la regla AUTH-03 en dos idiomas — el
del contrato y el del compilador — y que el compilador la haga cumplir.
Y van ANTES del store que las usa: los tipos son el proveedor, el store
del paso siguiente el consumidor — proveedor primero, consumidor después,
el mismo orden que el backend practicó todo el proyecto.*

**Reemplaza `frontend/src/types/api.ts` completo** — el archivo entero de
la guía 2, más el bloque de la etapa 2 al final:

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
```

✅ **Mini-verificación:** experimento del compilador, como en la guía 2:
agrega al final del archivo esta línea con un rol inventado:

```typescript
const rolMalo: Rol = "superadmin";
```

`npm run build` **falla** con
`Type '"superadmin"' is not assignable to type 'Rol'` — el compilador acaba
de impedir que un rol que no existe llegue a la pantalla. Borra la línea y
el build vuelve a pasar.

---

## Paso 3 — `stores/useAuthStore.ts`: la sesión que sobrevive recargas

🧠 **El desarrollador piensa:** *tres decisiones de ADR-009 hechas código.
**Primera: el store guarda `token` y `usuario`** — el par que compone la
sesión — con dos acciones: `iniciarSesion` lo instala, `cerrarSesion` lo
borra entero. **Segunda: `persist` con la clave `maura-auth`** sobre
`localStorage` (declarado explícito con `createJSONStorage`, aunque sea el
default: ver el mecanismo enseña más que heredarlo). ¿Por qué localStorage
y no una cookie httpOnly? Porque la SPA necesita LEER el token para
adjuntarlo en cada llamada, y porque debe sobrevivir los full-page loads
que Webpay impondrá en la etapa 3 — el ADR-009 deja dicha la desventaja
honesta: un XSS puede leerlo, y esa conversación ya la tuvimos. **Tercera:
`partialize` persiste SOLO token y usuario — jamás funciones** (Pitfall 7).
Una función no se puede serializar a JSON: sin el filtro, el middleware
intentaría guardar el store entero y la re-hidratación traería basura. Y la
propiedad más importante, gratis: `localStorage` hidrata SÍNCRONO — el
store nace ya con la sesión adentro. El primer render ya sabe quién eres:
sin parpadeo de "Ingresar" que se corrige solo (D-21).*

Crea la carpeta **`frontend/src/stores/`** y
**`frontend/src/stores/useAuthStore.ts`**:

```typescript
// La sesión de la clienta: token + usuario, persistidos en localStorage
// bajo la clave "maura-auth" (ADR-009, D-21). Sobrevive recargas, cierre
// del navegador y los full-page loads que trae Webpay en la etapa 3.
import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

import type { UsuarioPublico } from "../types/api";

interface EstadoAuth {
  token: string | null;
  usuario: UsuarioPublico | null;
  iniciarSesion: (token: string, usuario: UsuarioPublico | null) => void;
  cerrarSesion: () => void;
}

export const useAuthStore = create<EstadoAuth>()(
  persist(
    (set) => ({
      token: null,
      usuario: null,
      iniciarSesion: (token, usuario) => set({ token, usuario }),
      cerrarSesion: () => set({ token: null, usuario: null }),
    }),
    {
      name: "maura-auth", // la clave exacta en localStorage
      storage: createJSONStorage(() => localStorage), // explícito (didáctico)
      // SOLO datos: jamás funciones — una función no se serializa a JSON
      // (Pitfall 7: sin partialize, la re-hidratación traería basura).
      partialize: (state) => ({
        token: state.token,
        usuario: state.usuario,
      }),
    }
  )
);
```

✅ **Mini-verificación:** `npm run build` pasa. La prueba de fuego de la
persistencia (recargar y seguir vivo) llega en el paso 10 — hoy solo
comprueba que el store compila; su consumidor llega en los pasos
siguientes.

---

## Paso 4 — `lib/api.ts` crece: Bearer, `apiPostForm` y el interceptor 401

🧠 **El desarrollador piensa:** *la guía 2 prometió que este archivo
existía para HOY: "cuando llegue el token, el header se agrega en UN lugar;
cuando un endpoint responda 401, se decide qué hacer en UN lugar" (regla
5). Llegó el momento — la base (ApiError, la URL base) no se toca y lo
nuevo es una refundición, con UNA corrección honesta: la lectura del
`detail` aprende a manejar el 422 real de FastAPI (su `detail` viaja como
array, no como string). Las tres funciones pasan
por `pedir()`, que hace dos cosas transversales. **Adjunta el Bearer**
cuando hay token — leído con `useAuthStore.getState()`: la API pública de
Zustand para leer el store FUERA de React, sin hook ni contexto. **Y vigila
el 401** (interceptor, D-22): si una llamada que llevaba Bearer responde
401, la sesión está muerta — se limpia el store (el `persist` borra el
localStorage en la misma llamada) y se redirige con `window.location.assign`
a `/login?expirada=1`. ¿Por qué una carga completa y no `useNavigate`?
Porque un 401 significa "sesión inválida": recargar la app de un golpe
también deja en blanco la caché de queries — honesto y simple. ¿Y por qué
SOLO llamadas con Bearer? Porque el propio login responde 401 con
credenciales incorrectas — y ese 401 lo muestra el FORMULARIO con su banner
rojo, no el centinela (Pitfall 5). ¿Y cómo garantiza `pedir` que el login
nunca lleve Bearer? Por construcción, no por contexto: `apiPostForm` marca
la llamada como `sinAuth`, así que el login viaja SIN `Authorization`
aunque el store todavía tenga un token viejo — puede pasar: si `verificar`
falló por error de red, el formulario se muestra con el token aún guardado,
y sin la marca ese login fallido dispararía la expulsión. Su 401 nunca
entra acá. Una cosa más: `apiPostForm` manda el cuerpo como FormData
SIN tocar `Content-Type` — el navegador escribe solo el `boundary` que
separa los campos; setearlo a mano lo destruye y el backend no puede
parsear el formulario.*

Reemplaza **`frontend/src/lib/api.ts`** completo:

```typescript
// Regla 5 (ADR-002): TODO el HTTP del frontend sale de este archivo.
// La etapa 2 lo extiende sin romper la base de la guía 4: ApiError y la
// URL base siguen intactos. Lo nuevo: pedir() adjunta el Bearer, vigila
// el 401 (interceptor, D-22) y normaliza el detail del 422 (que FastAPI
// manda como array, no string).
import { useAuthStore } from "../stores/useAuthStore";

export class ApiError extends Error {
  readonly status: number;

  constructor(mensaje: string, status: number) {
    super(mensaje);
    this.status = status;
  }
}

const base = import.meta.env.VITE_API_URL ?? "";

async function pedir<T>(
  ruta: string,
  init: RequestInit = {},
  { sinAuth = false }: { sinAuth?: boolean } = {}
): Promise<T> {
  // getState(): leer el store FUERA de React — API pública de Zustand.
  const token = useAuthStore.getState().token;
  const headers = new Headers(init.headers); // p. ej. el Content-Type del JSON
  // sinAuth (Pitfall 5): esta llamada JAMÁS lleva Bearer — el login la usa
  // para que su 401 (credenciales incorrectas) lo muestre el formulario
  // con su banner, aunque el store todavía tenga un token viejo (pasa si
  // `verificar` falló por error de red y el formulario se muestra con la
  // sesión a medio caer).
  const llevaBearer = token !== null && !sinAuth;
  if (llevaBearer) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(`${base}/${ruta}`, { ...init, headers });

  if (!res.ok) {
    // Interceptor 401 (D-22): SOLO llamadas que llevaban Bearer. Las
    // sinAuth (como el login) muestran su 401 en el propio formulario
    // con su banner — jamás esta redirección (Pitfall 5).
    if (res.status === 401 && llevaBearer) {
      useAuthStore.getState().cerrarSesion(); // borra token+usuario (y el localStorage del persist)
      window.location.assign("/login?expirada=1"); // carga completa: caché de queries en blanco
    }
    let mensaje = `Error HTTP ${res.status}`;
    try {
      const cuerpo = await res.json();
      // El detail tiene DOS caras: string en los errores que el backend
      // lanza a mano ("Credenciales incorrectas") y ARRAY de validación
      // en el 422 de FastAPI ([{loc, msg, type}, …]). Se normaliza a UN
      // string humano: asignar el array tal cual degrada el mensaje a
      // "[object Object]" al llegar a ApiError.
      const detalle = cuerpo?.detail;
      if (typeof detalle === "string") mensaje = detalle;
      else if (Array.isArray(detalle) && detalle[0]?.msg)
        mensaje = detalle[0].msg;
    } catch {
      // El cuerpo no traía JSON: nos quedamos con el mensaje genérico
    }
    throw new ApiError(mensaje, res.status);
  }
  return res.json();
}

export async function apiGet<T>(ruta: string): Promise<T> {
  return pedir<T>(ruta);
}

// El login del contrato es un form OAuth2: el cuerpo viaja como FormData
// (username transporta el email). SIN Content-Type manual: el navegador
// agrega el boundary — setearlo a mano rompe el parseo del backend.
export async function apiPostForm<T>(ruta: string, form: FormData): Promise<T> {
  // sinAuth: el login jamás lleva Bearer (Pitfall 5) — ni siquiera con un
  // token viejo todavía en el store.
  return pedir<T>(ruta, { method: "POST", body: form }, { sinAuth: true });
}

// El registro SÍ es JSON: aquí el Content-Type se declara explícito.
export async function apiPost<T>(ruta: string, cuerpo: unknown): Promise<T> {
  return pedir<T>(ruta, {
    method: "POST",
    body: JSON.stringify(cuerpo),
    headers: { "Content-Type": "application/json" },
  });
}
```

✅ **Mini-verificación:** `npm run build` pasa — y fíjate lo que NO cambió:
`ApiError` y la URL base son los de la guía 4, así que la ficha y el
catálogo siguen funcionando idéntico. La lectura del `detail` sí creció:
normaliza el array del 422 de FastAPI a un string humano — la misma
situación del paso 7 (registro con contraseña corta) ya no degrada
`ApiError.message` a "[object Object]". El comportamiento nuevo se prueba
en los pasos 6 a 10.

---

## Paso 5 — `components/RequireAuth.tsx`: el guard que nace hoy

🧠 **El desarrollador piensa:** *catorce líneas que la etapa 3 y la fase 4
van a agradecer. La idea: una **ruta layout de guardia** — si no hay token,
no se renderiza lo de adentro: `Navigate` manda al login llevando en
`state` la ubicación ACTUAL (`from: location`) y con `replace` para que el
login no quede ensuciando el historial tras volver. Si hay token, `Outlet`
renderiza lo que envuelve. Pero la lección que importa va dicha entera:
**el guard es UX, no seguridad** (D-32). Oculta la pantalla al visitante
sin sesión — pero cualquier persona con las devtools puede falsificar el
store y "pasar" el guard: lo que de verdad protege al checkout (etapa 3) y
al panel (fase 4) es el 401/403 del BACKEND, que no se puede falsificar.
El guard existe para que la clienta normal no vea una pantalla rota: la
cortesía la da el cliente, la ley la da el servidor. Hoy el componente
nace y compila; su primer uso llega con `/checkout` en la guía 8 — y el
`from` que guarda es GENÉRICO: cualquier ruta protegida futura lo hereda
sin tocar una línea.*

Crea **`frontend/src/components/RequireAuth.tsx`**:

```tsx
// Guard de rutas protegidas: UX, no seguridad (D-32). Lo que de verdad
// protege es el 401/403 del backend — esto evita que la clienta sin
// sesión vea una pantalla rota y la devuelve a donde iba tras el login.
import { Navigate, Outlet, useLocation } from "react-router";

import { useAuthStore } from "../stores/useAuthStore";

export default function RequireAuth() {
  const token = useAuthStore((s) => s.token);
  const location = useLocation();

  if (!token) {
    // returnTo (D-32): la ubicación actual viaja en el state; el login
    // la lee y devuelve a la clienta a donde venía. replace: sin el
    // login en el historial tras volver.
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return <Outlet />;
}
```

✅ **Mini-verificación:** `npm run build` pasa. Nada lo usa todavía — su
primera ruta protegida (`/checkout`) llega en la guía 8, y hoy ya está
escrito exactamente como esa guía lo necesitará.

---

## Paso 6 — `features/cuentas/Login.tsx`: el formulario que pregunta

🧠 **El desarrollador piensa:** *la pantalla con más decisiones por
centímetro cuadrado de la etapa. **Los avisos de arriba:** el login lee dos
contextos — `?expirada=1` (lo puso el interceptor: sesión muerta, banner
ámbar con el copy locked de D-22) y `location.state.cuentaCreada` (lo puso
el registro: banner esmeralda). **La mutación:** un `useMutation` de
TanStack Query como en toda la serie — submit `disabled` con label en
gerundio mientras vuela. Dentro, dos llamadas en secuencia: el login
(`apiPostForm` con el FormData cuyo campo `username` transporta el email)
entrega el token; el token entra al store PRIMERO (para que `authHeaders()`
ya pueda adjuntarlo); y el `usuario` lo trae `/api/auth/perfil` — la
primera llamada autenticada de la app. ¿Por qué pedir el perfil si el
formulario ya sabe el email? Porque quién eres lo dice el SERVIDOR, no lo
que un formulario escribió — el día que la cuenta tenga más campos, la
pantalla no se enterará por el login. **Y la entrada con sesión:** si
llegas al login con token guardado, no se muestra el formulario directo:
se COMPRUEBA el token contra el perfil — vivo → `/`; muerto → el
interceptor hace su número (expulsión con aviso). Esa comprobación es
justamente lo que hace observable al interceptor sin esperar al checkout
de la guía 8. La validación cliente es un espejo HONESTO: el backend del
login no valida forma de contraseña (una clave corta ahí es solo una
credencial incorrecta → 401 genérico, guía 5), así que el formulario
revisa el formato del email y nada más — no inventa reglas que el endpoint
no tiene.*

Crea la carpeta **`frontend/src/features/cuentas/`** y
**`frontend/src/features/cuentas/Login.tsx`**:

```tsx
// Login: el form OAuth2 (username = email), los avisos de expirada/cuenta
// creada, y el returnTo genérico (D-32). El error 401 se muestra AQUÍ en
// banner — el interceptor no interfiere en el propio login (Pitfall 5).
import { useMutation, useQuery } from "@tanstack/react-query";
import { Link, Navigate, useLocation, useNavigate } from "react-router";
import { useState, type FormEvent } from "react";

import { ApiError, apiGet, apiPostForm } from "../../lib/api";
import { useAuthStore } from "../../stores/useAuthStore";
import { type Token, type UsuarioPublico } from "../../types/api";

const inputClase =
  "w-full rounded-lg border border-orange-200 bg-white px-4 py-2 min-h-11 text-base focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none";

export default function Login() {
  const navegar = useNavigate();
  const ubicacion = useLocation();
  const token = useAuthStore((s) => s.token);
  const iniciarSesion = useAuthStore((s) => s.iniciarSesion);

  // ¿Hay sesión guardada? Se COMPRUEBA contra el servidor antes de
  // redirigir: un token vencido no debe ver este formulario — debe ver
  // el aviso ámbar del interceptor (401 → expulsión).
  const verificar = useQuery({
    queryKey: ["perfil"],
    queryFn: () => apiGet<UsuarioPublico>("api/auth/perfil"),
    enabled: token !== null,
    retry: false, // un 401 no se reintenta: el interceptor ya expulsó
  });

  const mutation = useMutation({
    mutationFn: async (datos: { email: string; password: string }) => {
      // El form OAuth2 del contrato: el campo username transporta el email.
      const form = new FormData();
      form.append("username", datos.email);
      form.append("password", datos.password);
      const sesion = await apiPostForm<Token>("api/auth/login", form);
      // Token primero: desde esta línea authHeaders() ya lo adjunta. El
      // usuario lo dice el SERVIDOR (perfil), no el formulario.
      iniciarSesion(sesion.access_token, null);
      const usuario = await apiGet<UsuarioPublico>("api/auth/perfil");
      iniciarSesion(sesion.access_token, usuario);
      return usuario;
    },
    onSuccess: () => {
      // returnTo genérico (D-32): a donde venía la clienta — o al inicio.
      navegar(ubicacion.state?.from?.pathname ?? "/", { replace: true });
    },
  });

  const [errorEmail, setErrorEmail] = useState("");

  function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    const datos = new FormData(evento.currentTarget);
    const email = String(datos.get("email") ?? "").trim();
    const password = String(datos.get("password") ?? "");
    // Espejo honesto: el backend del login NO valida forma de contraseña
    // (clave corta = credencial incorrecta → 401); el email sí es un email.
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setErrorEmail("Escribe un email válido.");
      return;
    }
    setErrorEmail("");
    mutation.mutate({ email, password });
  }

  if (token && verificar.isPending) {
    return (
      <main className="max-w-md mx-auto px-4 py-16 text-sm text-neutral-600">
        Comprobando tu sesión…
      </main>
    );
  }
  if (token && verificar.isSuccess) {
    return <Navigate to="/" replace />;
  }
  // (401: el interceptor ya redirigió a /login?expirada=1 con aviso ámbar.
  // Error de red — backend caído: mostramos el formulario, sin pérdida.)

  const expirada =
    new URLSearchParams(ubicacion.search).get("expirada") === "1";
  const cuentaCreada = Boolean(ubicacion.state?.cuentaCreada);

  return (
    <main className="max-w-md mx-auto px-4 py-16">
      <h1 className="text-2xl md:text-3xl font-extrabold text-neutral-900">
        Iniciar sesión
      </h1>

      {expirada && (
        <p className="mt-6 bg-amber-100 text-amber-800 rounded-2xl p-4 text-sm">
          Tu sesión expiró, ingresa de nuevo
        </p>
      )}
      {cuentaCreada && (
        <p className="mt-6 bg-emerald-100 text-emerald-800 rounded-2xl p-4 text-sm">
          Cuenta creada. Ingresa con tu email y contraseña.
        </p>
      )}

      <form
        onSubmit={enviar}
        className="mt-6 bg-white rounded-2xl border border-orange-100 p-6 md:p-8"
      >
        <label htmlFor="email" className="text-sm font-bold text-neutral-900">
          Email
        </label>
        <input id="email" name="email" type="email" className={`mt-2 ${inputClase}`} />
        {errorEmail && <p className="mt-2 text-sm text-red-600">{errorEmail}</p>}

        <label
          htmlFor="password"
          className="mt-4 block text-sm font-bold text-neutral-900"
        >
          Contraseña
        </label>
        <input
          id="password"
          name="password"
          type="password"
          className={`mt-2 ${inputClase}`}
        />

        {mutation.isError && (
          <p className="mt-4 bg-red-50 text-red-600 rounded-2xl p-4 text-sm">
            {mutation.error instanceof ApiError && mutation.error.status === 401
              ? "Credenciales incorrectas" // copy locked (D-26), genérico deliberado
              : "No pudimos conectar con el servidor. Revisa que el backend esté corriendo en el puerto 8000 e inténtalo de nuevo."}
          </p>
        )}

        <button
          type="submit"
          disabled={mutation.isPending}
          className="mt-6 w-full bg-orange-600 text-white font-bold rounded-full px-6 py-2 min-h-11 hover:bg-orange-700 disabled:opacity-60 disabled:cursor-not-allowed focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
        >
          {mutation.isPending ? "Ingresando…" : "Iniciar sesión"}
        </button>

        <p className="mt-6 text-sm text-neutral-600">
          ¿No tienes cuenta?{" "}
          <Link
            to="/registro"
            className="text-orange-600 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
          >
            Crear cuenta
          </Link>
        </p>
      </form>
    </main>
  );
}
```

✅ **Mini-verificación (el 401 en su casa, sin redirección):** con ambos
servidores corriendo, abre **http://localhost:5173/login** — la card con
labels persistentes (sin placeholders), el aviso NO aparece. Envía
credenciales malas (email de la clienta seed + clave equivocada): banner
ROJO con "Credenciales incorrectas" DENTRO de la card, la página NO se
redirige — ese es el Pitfall 5 en vivo: el 401 del login lo maneja el
formulario, no el interceptor. (El botón muestra "Ingresando…" mientras
vuela.)

---

## Paso 7 — `features/cuentas/Registro.tsx`: crear cuenta NO inicia sesión

🧠 **El desarrollador piensa:** *el gemelo del login con dos decisiones
propias. **La validación SÍ es un espejo completo:** `RegistroCreate`
exige email con formato y mínimo 8 (RN-05) — el cliente repite exactamente
esas dos reglas al submit, para que el 422 del backend casi nunca ocurra;
el helper "Mínimo 8 caracteres." bajo el campo hace la regla VISIBLE antes
de equivocarse, y no hay composición obligatoria: longitud sobre
complejidad, igual que el backend. **Y la decisión de flujo:** el registro
exitoso NO inicia sesión — navega al login con el aviso esmeralda en el
`state`. ¿No sería "más cómodo" entrar directo? Sí — y menos seguro: la
clienta confirma su clave ENTRANDO (si se equivocó al tipearla dos veces,
lo descubre ahora y no con su pedido en la balanza), y el flujo queda
honesto con lo que existe: el registro devuelve una cuenta (201), no un
token — el token lo emite el login. El 409 del email duplicado se muestra
en banner con el copy locked: la asimetría con el 401 genérico del login
es deliberada y ya la discutimos en la guía 5 (D-26).*

Crea **`frontend/src/features/cuentas/Registro.tsx`**:

```tsx
// Registro: espejo cliente de RegistroCreate (email + mínimo 8, RN-05).
// El éxito NO inicia sesión: navega al login con aviso de cuenta creada
// (no hay token todavía — el token lo emite el login).
import { useMutation } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router";
import { useState, type FormEvent } from "react";

import { ApiError, apiPost } from "../../lib/api";
import { type RegistroPayload, type UsuarioPublico } from "../../types/api";

const inputClase =
  "w-full rounded-lg border border-orange-200 bg-white px-4 py-2 min-h-11 text-base focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none";

export default function Registro() {
  const navegar = useNavigate();
  const [errores, setErrores] = useState<{ email?: string; password?: string }>(
    {}
  );

  const mutation = useMutation({
    mutationFn: (datos: RegistroPayload) =>
      apiPost<UsuarioPublico>("api/auth/registro", datos),
    onSuccess: () => {
      // Sin iniciar sesión: la clienta confirma su clave entrando.
      navegar("/login", { state: { cuentaCreada: true } });
    },
  });

  function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    const datos = new FormData(evento.currentTarget);
    const email = String(datos.get("email") ?? "").trim();
    const password = String(datos.get("password") ?? "");
    // Espejo de RegistroCreate: las mismas dos reglas del 422 — ni una más.
    const siguientes: { email?: string; password?: string } = {};
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      siguientes.email = "Escribe un email válido.";
    }
    if (password.length < 8) {
      siguientes.password = "La contraseña debe tener al menos 8 caracteres.";
    }
    setErrores(siguientes);
    if (!siguientes.email && !siguientes.password) {
      mutation.mutate({ email, password });
    }
  }

  return (
    <main className="max-w-md mx-auto px-4 py-16">
      <h1 className="text-2xl md:text-3xl font-extrabold text-neutral-900">
        Crear cuenta
      </h1>

      <form
        onSubmit={enviar}
        className="mt-6 bg-white rounded-2xl border border-orange-100 p-6 md:p-8"
      >
        <label htmlFor="email" className="text-sm font-bold text-neutral-900">
          Email
        </label>
        <input id="email" name="email" type="email" className={`mt-2 ${inputClase}`} />
        {errores.email && (
          <p className="mt-2 text-sm text-red-600">{errores.email}</p>
        )}

        <label
          htmlFor="password"
          className="mt-4 block text-sm font-bold text-neutral-900"
        >
          Contraseña
        </label>
        <input
          id="password"
          name="password"
          type="password"
          className={`mt-2 ${inputClase}`}
        />
        <p className="mt-2 text-sm text-neutral-600">Mínimo 8 caracteres.</p>
        {errores.password && (
          <p className="mt-2 text-sm text-red-600">{errores.password}</p>
        )}

        {mutation.isError && (
          <p className="mt-4 bg-red-50 text-red-600 rounded-2xl p-4 text-sm">
            {mutation.error instanceof ApiError && mutation.error.status === 409
              ? "Ese email ya tiene cuenta, inicia sesión" // copy locked (D-26)
              : "No pudimos conectar con el servidor. Revisa que el backend esté corriendo en el puerto 8000 e inténtalo de nuevo."}
          </p>
        )}

        <button
          type="submit"
          disabled={mutation.isPending}
          className="mt-6 w-full bg-orange-600 text-white font-bold rounded-full px-6 py-2 min-h-11 hover:bg-orange-700 disabled:opacity-60 disabled:cursor-not-allowed focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
        >
          {mutation.isPending ? "Creando cuenta…" : "Crear cuenta"}
        </button>

        <p className="mt-6 text-sm text-neutral-600">
          ¿Ya tienes cuenta?{" "}
          <Link
            to="/login"
            className="text-orange-600 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
          >
            Iniciar sesión
          </Link>
        </p>
      </form>
    </main>
  );
}
```

✅ **Mini-verificación (el 409 y el aviso esmeralda):** en
**http://localhost:5173/registro**:

1. Envía el formulario VACÍO: los dos espejos bajo sus campos ("Escribe un
   email válido." / "La contraseña debe tener al menos 8 caracteres.") —
   sin llamar al backend: la validación corrió al submit, en el cliente.
2. Regístrate con el EMAIL DE LA CLIENTA SEED (el de tu `.env`): banner
   rojo "Ese email ya tiene cuenta, inicia sesión" — el 409 claro dentro
   de la card.
3. Regístrate con un email NUEVO y clave de 8+: llegas al login con el
   aviso esmeralda "Cuenta creada. Ingresa con tu email y contraseña." —
   y entras con la clave que acabas de crear. El registro no inició
   sesión: te hizo confirmarla entrando.

---

## Paso 8 — La Navbar que saluda (y despide)

🧠 **El desarrollador piensa:** *el chrome compartido gana su primer
estado. Sin sesión: un link "Ingresar" con el mismo `estiloLink` de siempre.
Con sesión: el email de la clienta — truncado con `truncate max-w-32` y su
`title` para leerlo completo en hover, porque los emails son largos y la
barra es de todos — más el botón "Cerrar sesión", sin confirmación: borra
token y usuario del store (el `persist` limpia el localStorage en el mismo
llamado) y navega a `/`. ¿Por qué sin confirmación? Porque cerrar sesión es
reversible por diseño: entrar de nuevo son dos campos — no hay daño que
confirmar. Y el grupo de links pasa a `flex flex-wrap`: la barra creció y
en pantallas angostas debe envolver en vez de estirar — NADA de scroll
horizontal. El badge del carro con su contador llega en la guía 7 (D-28):
hoy no existe, y la barra ya quedó lista para recibirlo.*

Reemplaza **`frontend/src/components/Navbar.tsx`** completo:

```tsx
// Navbar con estado de sesión (A9): sin sesión → "Ingresar"; con sesión →
// email truncado + "Cerrar sesión". El badge del carro llega en la guía 7.
import { Link, NavLink, useNavigate } from "react-router";

import { useAuthStore } from "../stores/useAuthStore";

const estiloLink = ({ isActive }: { isActive: boolean }) =>
  `text-sm min-h-11 flex items-center focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none ${
    isActive ? "text-orange-600 font-bold" : "text-neutral-600"
  }`;

export default function Navbar() {
  const navegar = useNavigate();
  const usuario = useAuthStore((s) => s.usuario);
  const cerrarSesion = useAuthStore((s) => s.cerrarSesion);

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

✅ **Mini-verificación (la barra en sus dos estados):** sin sesión, la
barra muestra "Ingresar" al lado de Catálogo. Entra con la clienta seed
(paso 6): el link cambia por su email (pásale el mouse: el `title` lo
muestra completo) y el botón "Cerrar sesión". Clic en el botón: vuelve el
"Ingresar" y estás en `/` — sesión borrada, sin confirmación, sin scroll
horizontal en ninguna de las dos formas.

---

## Paso 9 — `main.tsx`: las rutas nuevas dentro del Layout vigente

🧠 **El desarrollador piensa:** *dos líneas de rutas, cero decisiones
nuevas — y eso ES la decisión. Las rutas `/login` y `/registro` viven
DENTRO de la ruta layout vigente: heredan Navbar y Footer, porque son
páginas de la tienda, no islas. Los imports siguen saliendo de
`"react-router"` (la regla de la v8 que la guía 2 fijó) y el orden de los
providers es intocable: StrictMode → QueryClientProvider → BrowserRouter.
¿Y `/checkout`? No existe todavía — la construye la guía 8, y ese día se
agrega envuelta en el `RequireAuth` que ya escribimos en el paso 5. Hoy el
mapa de rutas crece por composición, como la API en su momento.*

En **`frontend/src/main.tsx`**, agrega los imports junto a los de las
features:

```tsx
import Login from "./features/cuentas/Login";
import Registro from "./features/cuentas/Registro";
```

Y las rutas dentro de `<Route element={<Layout />}>`, junto a las
existentes:

```tsx
<Route element={<Layout />}>
  <Route path="/" element={<Landing />} />
  <Route path="/productos" element={<Catalogo />} />
  <Route path="/productos/:id" element={<FichaProducto />} />
  <Route path="/login" element={<Login />} />
  <Route path="/registro" element={<Registro />} />
  <Route path="*" element={<NoEncontrado />} />
</Route>
```

✅ **Mini-verificación:** `npm run build` pasa, y con `npm run dev` las
direcciones responden: **http://localhost:5173/login** y
**http://localhost:5173/registro** muestran sus pantallas con la Navbar y
el Footer alrededor — dentro del Layout, no islas.

---

## Paso 10 — La prueba de fuego: la sesión que sobrevive (y la que muere)

Con ambos servidores corriendo y el seed de la guía 5 hecho. Los tres
momentos de AUTH-02:

✅ **Mini-verificación (login con la clienta seed):** en
**http://localhost:5173/login**, entra con TU `CLIENTE_EMAIL` y
`CLIENTE_PASSWORD`. El navbar muestra su email truncado y "Cerrar sesión"
— la tienda ya sabe quién eres. Abre las DevTools → Application →
Local Storage → `maura-auth`: el JSON tiene exactamente `token` y
`usuario` — sin rastro de funciones (el `partialize` trabajando). Ahí
vive la sesión (D-21).

✅ **Mini-verificación (AUTH-02: F5 y sigue viva):** con la sesión puesta,
presiona **F5** en cualquier página. El navbar muestra el email DESDE EL
PRIMER render — sin un parpadeo de "Ingresar" que se corrija solo:
`localStorage` hidrata síncrono y el store nace con la sesión adentro.
Cierra la pestaña, ábrela de nuevo: sigue viva. Esa es la sesión que la
redirección de Webpay encontrará esperándola en la etapa 3.

✅ **Mini-verificación (el interceptor: matar el token a mano):** en
DevTools → Local Storage → `maura-auth`, EDITA el valor: cambia los
últimos caracteres del token (rompe la firma) y guarda. Navega a
**/login**: la comprobación de sesión dispara el perfil con el token
corrupto → la API responde **401** → el interceptor limpia la sesión y te
expulsa a **/login?expirada=1** con el aviso ámbar "Tu sesión expiró,
ingresa de nuevo" (D-22). Ese es el centinela en acción — el mismo
mecanismo que en la etapa 3 expulsará de cualquier pantalla cuando el
token venza a los 7 días, sin que ninguna pantalla sepa que existe.

---

## ❌ El error que este archivo evita

**1. Persistir funciones en el store.**

```typescript
// ❌ Sin partialize: el middleware intenta serializar TODO el estado —
// y las acciones no existen en JSON. La re-hidratacción trae basura.
persist((set) => ({ ... }), { name: "maura-auth" })

// ✅ partialize SIEMPRE: solo datos, jamás funciones
partialize: (state) => ({ token: state.token, usuario: state.usuario })
```

El síntoma clásico es sutil: la app "funciona"… hasta que recargas y el
store despierta con campos que no eran — o el `JSON.stringify` del
middleware revienta en consola. Regla: si vive en el store y es función,
no se persiste.

**2. Setear `Content-Type` en un FormData.**

```typescript
// ❌ El boundary del form se pierde: el backend no puede separar los campos
fetch(ruta, { method: "POST", body: form, headers: { "Content-Type": "multipart/form-data" } })

// ✅ Sin Content-Type: el navegador escribe el boundary correcto solo
fetch(ruta, { method: "POST", body: form })
```

El `Content-Type` de un form lleva un `boundary` único por envío: pegarlo
a mano con un valor fijo garantiza que el servidor no encuentre los
campos — y el login falle con un 422 que nadie espera. El navegador lo
hace mejor solo.

**3. El interceptor dispara en el propio login.**

```typescript
// ❌ Cualquier 401 redirige: credenciales incorrectas te expulsan a
// /login?expirada=1 — el banner rojo del formulario nunca se ve
if (res.status === 401) { cerrarSesion(); window.location.assign("/login?expirada=1"); }

// ✅ SOLO llamadas que llevaban Bearer: el login viaja marcado sinAuth
// (sin Authorization adjunta), así su 401 lo maneja el formulario con
// su banner (Pitfall 5)
if (res.status === 401 && llevaBearer) { ... }
```

Sin la marca `sinAuth`, la condición `&& token` no basta: el formulario del
login puede estar visible CON un token viejo aún en el store (si `verificar`
falló por error de red) — y ese login con credenciales incorrectas
dispararía la expulsión: escribes mal la clave y en vez del banner rojo te
recibe el aviso ámbar de "sesión expirada" — que además miente: nunca hubo
sesión.

---

## ✅ Verificación de la guía 6

Con ambos servidores corriendo y el seed hecho:

1. **/login** con la clienta seed → 200, el navbar muestra su email, y en
   Local Storage `maura-auth` guarda solo `token` y `usuario`.
2. **F5** en cualquier página → la sesión sigue viva al primer render,
   sin parpadeo (AUTH-02, D-21).
3. Credenciales incorrectas → banner rojo "Credenciales incorrectas"
   dentro de la card, SIN redirección (Pitfall 5, D-26).
4. **/registro** vacío → espejos cliente al submit; email duplicado →
   banner "Ese email ya tiene cuenta, inicia sesión"; cuenta nueva →
   aviso esmeralda en el login y entrada con la nueva clave.
5. "Cerrar sesión" borra la sesión y navega a `/` — el navbar vuelve a
   "Ingresar"; sin scroll horizontal en ninguna resolución angosta.
6. Token corrompido a mano + navegar a **/login** → expulsión a
   `/login?expirada=1` con el aviso ámbar "Tu sesión expiró, ingresa de
   nuevo" (interceptor, D-22).
7. `npm run build` pasa — `RequireAuth` compilado y esperando a la
   guía 8.

## 📝 Punto de control (respóndelas sin mirar la guía)

1. ¿Qué se persiste en `maura-auth` y qué jamás debería persistirse — y
   por qué la hidratación de la sesión no produce un parpadeo de
   "Ingresar" al recargar?
2. ¿Por qué el interceptor actúa SOLO en llamadas con Bearer adjunto y
   qué gana la app recargándose completa (`window.location.assign`) en
   vez de navegar con `useNavigate`?
3. `RequireAuth` es seguridad o UX — y quién protege de verdad una ruta
   protegida? ¿Cómo vuelve la clienta a la página donde estaba después
   de iniciar sesión, y por qué el mecanismo es genérico (D-32)?

## Lo que acabas de aprender

- Zustand para el estado del CLIENTE vs TanStack Query para el estado del SERVIDOR: dos dueños, dos herramientas
- El store de sesión con `persist` + `createJSONStorage` + `partialize` (solo datos, jamás funciones) y la hidratación síncrona de localStorage: sesión al primer render, sin parpadeo (D-21, ADR-009)
- `getState()` fuera de React: cómo lee el token el único punto de salida HTTP de la app (regla 5)
- `apiPostForm` con FormData sin `Content-Type` manual (el boundary lo pone el navegador) y `apiPost` JSON para el registro
- El interceptor 401 (D-22): limpia sesión, redirige a `/login?expirada=1` con el copy locked — y el propio login eximido (Pitfall 5); las fases 3 y 4 lo heredan gratis
- `RequireAuth` con `Navigate state={{ from: location }} replace` y el login que vuelve con `location.state?.from?.pathname ?? "/"`: el returnTo genérico (D-32)
- El guard como UX y el 401/403 del backend como seguridad real — dicha explícita, no asumida
- Login y registro según el UI-SPEC: labels persistentes sin placeholders, banners de servidor dentro de la card con los copies locked, validación espejo al submit, submits en gerundio y cross-links
- El registro que NO inicia sesión: la clienta confirma su clave entrando — y el 201 sin token, honesto con el contrato

**Siguiente:** guia-07-carro.md — el carro: el store que guarda tus aromas
(en localStorage, como la sesión), la ficha que agrega, la página `/carro`
que hidrata precios vigentes y el badge del navbar que cuenta unidades.
