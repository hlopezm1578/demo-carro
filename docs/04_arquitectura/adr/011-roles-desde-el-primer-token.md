# ADR-011 — Roles desde el primer token: el admin nace del seed

- **Estado:** Aceptada
- **Fecha:** 2026-09-29
- **Resuelve:** cómo nacen las cuentas con rol admin y cómo se verifica el acceso por rol en la fase 2

## Contexto

AUTH-03 exige un rol admin verificable, pero la fase 2 no construye el panel
de administración (ese es el hito de la fase 4). Hace falta: (a) que exista
una cuenta admin sin pasos manuales, (b) que el rol viaje con la sesión, y
(c) un endpoint protegido que responda 200 al admin y 403 a la clienta para
que la dependencia de seguridad sea observable (D-33). La tentación clásica
de los tutoriales — "el primero que se registra queda admin" — es además una
puerta trasera en cualquier despliegue real.

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| **A. Claim de rol desde el primer token + cuentas demo del seed por variables de entorno** | El admin existe sin pasos manuales; el rol se verifica sin consultar la BD por request; credenciales fuera del código (`.env`) | Cambiar el rol de un usuario no afecta tokens ya emitidos (ventana de hasta 7 días) |
| **B. El primer usuario registrado queda admin** | Cero configuración; el flujo "natural" de muchos tutoriales | Puerta trasera: en un despliegue público, el primero en registrarse se queda con la tienda (descartada por D-23) |
| **C. Gestión de roles por panel de administración** | El flujo industrial completo: la dueña crea y degrada cuentas | Exige el panel (fase 4) y una sesión admin para crear al primer admin: el problema del huevo y la gallina |

## Decisión

**Opción A.** El rol viaja como claim dentro del JWT desde el primer token
que se emite, y las cuentas demo — admin y clienta — nacen del **seed
leyendo variables de entorno** (D-23, D-24, D-33):

1. **El seed hace upsert por email** (`ADMIN_EMAIL`/`ADMIN_PASSWORD` y
   `CLIENTE_EMAIL`/`CLIENTE_PASSWORD` del `.env`) y **restaura las
   credenciales al re-ejecutar**: cada alumno reinicia su admin sin miedo,
   igual que el seed de productos restaura el stock demo — es una feature
   deliberada, no un descuido.
2. **El endpoint demo `/api/admin/estado` devuelve 403 a la clienta**: con
   su token válido pero sin el rol, la respuesta observable es 403 — así
   AUTH-03 se verifica sin esperar el panel de la fase 4 (D-33).
3. **Las credenciales viven solo en el `.env`** (gitignoreado desde la guía
   1): nada de contraseñas literales en la guía ni en el código — el
   anti-patrón que se enseña a evitar es el hardcode (D-23).

## Consecuencias

**Positivas**
- Verificar los dos roles (200 vs 403) no exige ningún paso manual previo:
  las cuentas del seed son predecibles para la guía y para el UAT.
- El manejo de secretos queda bien enseñado: credenciales y `SECRET_KEY`
  por variable de entorno, jamás en el repositorio.
- El endpoint demo es minimal: enseña la dependencia `get_current_admin`
  sin inflar el contrato.

**Negativas (honestas)**
- **Cambiar el rol de un usuario no afecta tokens ya emitidos**: un admin
  degradado conserva su claim por la ventana de vida del token (hasta 7
  días, [ADR-009](009-jwt-larga-vida-localstorage.md)) — no hay revocación.
- **El endpoint demo no es el panel real**: `/api/admin/estado` devuelve
  conteos triviales del catálogo; la administración de verdad (productos,
  stock, pedidos) llega en la fase 4.

## Para conversar en clase

1. La dueña degrada hoy a una empleada de admin a clienta: ¿hasta cuándo
   sigue llegando la empleada a `/api/admin/estado`, y por qué?
2. ¿Por qué "el primer registrado queda admin" es una puerta trasera? ¿Qué
   tendría que pasar en el despliegue (fase 5) para que un extraño se
   quede con la tienda?
3. El rol viaja en el token y el token lo firma el backend: ¿qué habría que
   cambiar para consultar el rol en la BD en cada request, y qué ganaría y
   perdería esa variante?
