# Fase 5 del ciclo — Desarrollo guiado paso a paso

> **Cómo funcionan estas guías:** cada una está escrita como un **desarrolladora
> o desarrollador experimentado pensando en voz alta** mientras construye la
> tienda de Maura. Leerás las decisiones (con su porqué, referenciando los ADRs
> de `04_arquitectura/` y las reglas RN de `02_requerimientos.md`), copiarás y
> pegarás los bloques de código, y verificarás al final de cada paso que todo
> funciona antes de seguir.
>
> **Este repositorio contiene solo la guía.** Aquí no hay aplicación que correr:
> el código completo de la tienda vive **narrado** dentro de estas guías (ADR-008).
> Cada bloque de código se copia y se ejecuta **en tu máquina**, en el proyecto
> que tú construyes, y cada ✅ mini-verificación la corres tú en tu terminal y en
> tu navegador. Si algo falla, falla en tu proyecto — y se arregla en tu proyecto.
>
> **Reglas del alumno:**
> 1. No te saltes ninguna ✅ mini-verificación: es tu única prueba de que el paso
>    quedó bien antes de seguir avanzando.
> 2. Lee el bloque 🧠 "El desarrollador piensa" **antes** de copiar el código:
>    el porqué de cada decisión es el contenido del curso; el código es su consecuencia.
> 3. El error es información: léelo completo antes de borrarlo. Un error entendido
>    enseña más que un copy-paste que salió a la primera.

| # | Guía | Construye | Estado |
|---|---|---|---|
| 1 | `guia-01-proyecto-backend.md` | El tier servidor: proyecto Python con uv, configuración tipada y el primer endpoint (`/api/salud`) | ✅ Listo |
| 2 | `guia-02-proyecto-frontend.md` | El tier cliente: SPA React con TypeScript, la marca y la landing de Maura | ✅ Listo |
| 3 | `guia-03-modelos-y-seed.md` | Los datos: la tabla `productos`, el modelo con familia y notas, y el seed de 12 SKU | ✅ Listo |
| 4 | `guia-04-catalogo.md` | La pantalla que une los tiers: API de productos con filtros, grilla del catálogo, ficha y fotos | ✅ Listo |
| 5 | `guia-05-cuentas-backend.md` | Las cuentas en el backend: registro y login con JWT, roles desde el primer token y el seed de admin/clienta | ✅ Listo |
| 6 | `guia-06-sesion-frontend.md` | La sesión en la SPA: store persistente, interceptor 401 y rutas protegidas con retorno | ✅ Listo |
| 7 | `guia-07-carro.md` | El carro persistente: página `/carro` con precios vigentes, badge en el navbar y store que lo recuerda | ✅ Listo |
| 8 | `guia-08-checkout.md` | El checkout protegido y la Gran verificación final de la fase 2 | ✅ Listo |

> La fase 2 del proyecto completa sus cuatro guías (5-8: cuentas, sesión,
> carro y checkout). Las guías 9+ llegan con las fases siguientes (pago Webpay,
> panel admin, IA) — cada una asumiendo que estas están construidas y
> verificadas en tu máquina, igual que el índice de `docs/README.md` avanza
> por fase.

**Mapa mental de la serie:** el orden es **de adentro hacia afuera**. Primero
construimos cada tier por separado (guías 1 y 2: el backend que responde JSON y
el frontend que renderiza), sin que todavía conversen. Luego los datos (guía 3:
la tabla y el seed que le dan memoria al servidor). Al final de la fase 1, la
pantalla que une los dos tiers (guía 4: el catálogo que la SPA llena con la
API). La fase 2 agrega sobre esa base la **capa de estado de cliente** (guías
5-8): las cuentas con JWT que reconocen a la clienta (guía 5), la sesión y el
carro que sobreviven recargas en su máquina (guías 6 y 7) y el checkout
protegido que los junta (guía 8) — dejando el terreno listo para el pago de la
fase 3. Las fases siguientes del proyecto (pago, panel, asistente) agregan las
guías 9+ sobre esta base — cada una asumiendo que las anteriores están
construidas y verificadas en tu máquina.
