# ADR-009 — Sesión con un JWT de larga vida guardado en localStorage

- **Estado:** Aceptada
- **Fecha:** 2026-09-29
- **Resuelve:** cómo mantiene la SPA la sesión de la clienta entre recargas, cierres de pestaña y los full-page loads que trae Webpay en la fase 3

## Contexto

La tienda necesita que la clienta llegue al checkout con su identidad viva:
el token debe sobrevivir la recarga (F5), el cierre de la pestaña y, en la
fase 3, la vuelta de la redirección de Webpay — un full-page load donde la
SPA entera parte de cero. El tutorial oficial de FastAPI emite un token de
30 minutos pensado para renovarse; una tienda no puede cerrarle la sesión a
una clienta que dejó el carro armado y volvió al día siguiente. Dónde
guardar ese token en el navegador es una decisión de seguridad con trade-offs
reales, y acá se elige con la desventaja dicha en voz alta (D-21).

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| **A. Token único JWT de 7 días en `localStorage`** (store de Zustand con `persist`) | Sobrevive recargas y full-page loads sin pedir nada al servidor; cero superficie de renovación; el claim `exp` se lee claro en la mini-verificación | Un script inyectado (XSS) lo puede leer; sin revocación server-side durante los 7 días |
| **B. Access token corto + token de renovación** | Ventana de robo mínima; revocación posible al rotar el refresh | Doble endpoint, expiración silenciosa en plena pantalla, complejidad que una tienda demo no necesita (descartada por D-19) |
| **C. Cookie httpOnly con sesión en el servidor** | El JavaScript no puede leer la cookie: el XSS pierde su presa | Exige backend en el mismo origen o CORS con `credentials`; la vuelta de Webpay (fase 3) cruza orígenes y complica el flujo completo |

## Decisión

**Opción A.** La sesión es un único access token JWT de **7 días** (claim
`exp`, D-20) que la SPA guarda en `localStorage` a través del store de
autenticación de Zustand con el middleware `persist` (D-21):

1. **El claim de rol viaja dentro del token desde que se emite** (junto a
   `sub`, `exp` e `iat`): el backend firma la identidad una sola vez y no
   consulta la BD en cada request para saber quién entra (D-19, D-20, D-21;
   el rol se formaliza en el [ADR-011](011-roles-desde-el-primer-token.md)).
2. **El interceptor 401 de `lib/api.ts` cierra la sesión**: cualquier llamada
   autenticada que responda 401 limpia el store y redirige a `/login` con el
   aviso "Tu sesión expiró, ingresa de nuevo" — se enseña una vez y las fases
   3 y 4 lo heredan gratis (D-22).
3. **No existe endpoint de renovación**: la complejidad del refresh token
   queda fuera de la guía como comentario para el alumno curioso, no como
   código (D-19).

## Consecuencias

**Positivas**
- La clienta vuelve al día siguiente y su sesión sigue viva: el carro y el
  checkout la esperan tal cual.
- El flujo de la fase 3 (vuelta de Webpay como full-page load) funciona sin
  código extra: el token ya está en el `localStorage` antes de que React
  arranque.
- Cero piezas de renovación: un endpoint menos que mantener, enseñar y
  depurar.

**Negativas (honestas)**
- **Robo de token por XSS**: cualquier script inyectado puede leer el
  `localStorage` y usar el token por hasta 7 días. React escapa por defecto y
  `dangerouslySetInnerHTML` queda prohibido en la guía, pero la mitigación
  real (cookie httpOnly) se descartó arriba — este es **el costo enseñado del
  patrón** y D-21 exige tenerlo dicho, no escondido.
- **Sin revocación server-side**: si un token se filtra, nadie puede
  invalidarlo antes de los 7 días; no hay lista negra ni logout en el
  servidor — cerrar sesión solo borra el `localStorage`.
- **La opción más segura existía y no se tomó**: es la conversación honesta
  de la clase — se eligió simplicidad y desacople de cookies/CORS de cara a
  la fase 3, sabiendo el precio.

## Para conversar en clase

1. Un atacante logra un XSS en la SPA: ¿qué puede hacer con el token del
   `localStorage` que no podría con una cookie httpOnly, y por cuánto
   tiempo?
2. La dueña despide a una empleada que tenía rol admin: ¿cómo le cierran el
   acceso si el token vive 7 días y no existe revocación?
3. ¿Qué cambiaría en el contrato y en `lib/api.ts` si mañana la tienda
   agregara refresh tokens? (Pista: D-19 lo dejó reversible a propósito.)
