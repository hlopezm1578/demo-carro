# ADR-015 — El panel protegido por rol en los dos tiers: RequireAdmin como espejo UX del 403

- **Estado:** Aceptada
- **Fecha:** 2026-09-30
- **Resuelve:** cómo se protege el panel de administración de la dueña en la SPA y en la API — quién puede entrar a `/admin` y quién responde cada endpoint (ADMN-01, ADMN-02, ADMN-03, ADMN-04; decisión D-55)

## Contexto

ADMN-01..04 piden un panel donde la dueña gestiona productos, stock, pedidos
y métricas. El rol existe desde la fase 2: viaja como claim dentro del JWT
desde el primer token que se emite
([ADR-011](011-roles-desde-el-primer-token.md)) y `get_current_admin` ya
responde 403 a la clienta — el endpoint demo `/api/admin/estado` existía
justo para que ese 403 fuera verificable (D-33). La pregunta nueva es del
tier cliente: la clienta autenticada que escribe `/admin` en la barra del
navegador, ¿qué ve? Dejar que cada fetch reviente en 403 sería honesto pero
cruel; y duplicar la lógica de sesión dentro del panel sería una segunda
verdad de "quién puede". Falta decidir dónde vive el guard del panel y qué
tan lejos llega su autoridad.

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| **A. `RequireAdmin` que extiende `RequireAuth` + returnTo sumando el claim de rol** | Reusa el guard existente (D-32) y el claim que ya viaja en el token (ADR-011); sin sesión manda al login con returnTo y vuelve al panel; con sesión sin rol muestra `NoAutorizado` SIN expulsar al login — le falta permiso, no identidad | Son dos niveles de "quién puede" (guard SPA y dependencias backend) que deben mantenerse en sync |
| **B. Solo backend: el panel sin guard, cada fetch resuelve su 403/401** | Una sola línea de defensa; cero duplicación | La clienta que fuerza `/admin` ve una pantalla rota llena de errores de red — UX cruel y ruidosa en consola |
| **C. Duplicar la lógica de sesión dentro del panel** (leer el token a mano en cada pantalla admin) | El panel se vuelve autónomo | Una segunda verdad del token y del rol: el día que cambie algo de la sesión ([ADR-009](009-jwt-larga-vida-localstorage.md)), hay dos lugares que corregir |

## Decisión

**Opción A.** El panel se protege en los DOS tiers, cada uno con su propio
trabajo (D-55):

1. **La Navbar muestra "Panel" solo con rol admin**: el link
   (`usuario.rol === "admin"`) vive junto al estado de sesión — una
   clienta ni siquiera sabe que la ruta existe (el mismo criterio del
   "Mis pedidos" condicionado de la fase 3).
2. **`RequireAdmin` es UX cortés, NO la seguridad**: sin sesión delega en
   `<RequireAuth />` (el returnTo genérico de D-32 — tras el login vuelve
   al panel, no a la portada); con sesión válida pero sin rol renderiza
   `NoAutorizado` SIN expulsar al login: una clienta con sesión válida no
   necesita autenticarse de nuevo — le falta permiso, no identidad. Es el
   espejo frontend del 403 que D-33 enseñó en backend.
3. **`get_current_admin` en CADA endpoint `/api/admin/*` es la seguridad
   real** (la lección D-33 hecha patrón): el guard SPA se salta limpiando
   el localStorage o forzando la URL; el 403 del backend no. El contrato
   0.4.0 declara el 403 con su example `detail: Requiere rol admin` en
   TODOS los paths de administración, como el demo lo hizo en la fase 2.
4. **La base es ADR-011**: el claim de rol viaja en el token desde que se
   emite — el guard no consulta la BD ni inventa una segunda fuente del
   rol; lee el mismo store que lee `RequireAuth`.

## Consecuencias

**Positivas**
- La clienta que fuerza `/admin` recibe una pantalla que se explica ("No
  tienes acceso al panel") en vez de una rota — cortesía sin costar
  seguridad.
- La dueña entra directo: el returnTo la devuelve al panel tras un login,
  no a la portada.
- Cero lógica nueva de sesión: `RequireAdmin` lee el mismo store y el
  mismo claim que ya existían — el guard completo son unas líneas.

**Negativas (honestas)**
- **Dos niveles de "quién puede" que deben mantenerse en sync**: el guard
  conoce el claim, el backend la verdad; si mañana el panel filtra por un
  permiso más fino (por ejemplo, una empleada que ve métricas pero no
  edita productos), hay dos listas que actualizar — y el 403 del backend
  siempre manda.
- **El guard por rol se salta con las devtools**: es teatro de UX montado
  sobre la seguridad del servidor — y está bien que lo sea, mientras
  nadie lo confunda con la muralla.

## Para conversar en clase

1. Una clienta abre las devtools, borra el claim del store y recarga
   `/admin`: ¿qué ve en pantalla, qué responde el primer fetch del panel
   y por qué la tienda NO quedó comprometida?
2. ¿Por qué `NoAutorizado` NO expulsa al login, si "no tienes permiso"
   también suena a problema de sesión? ¿Qué diferencia hay entre
   identidad y permiso?
3. Si mañana existiera un rol "empleada" (ve pedidos, no toca productos),
   ¿qué cambian el guard, el navbar y `get_current_admin` — y por qué el
   backend no puede limitarse a confiar en el guard?

Relacionada: [ADR-011](011-roles-desde-el-primer-token.md) (el claim desde
el primer token) y [ADR-007](007-api-first.md) (el contrato 0.4.0 que
declara el 403 en cada path admin).
