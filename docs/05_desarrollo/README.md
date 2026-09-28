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
| 3 | `guia-03-modelos-y-seed.md` | Los datos: la tabla `productos`, el modelo con familia y notas, y el seed de 12 SKU | ⏳ Pendiente (misma fase) |
| 4 | `guia-04-catalogo.md` | La pantalla que une los tiers: API de productos con filtros, grilla del catálogo, ficha y fotos | ⏳ Pendiente (misma fase) |

> Las guías 3 y 4 se escriben dentro de esta misma fase del proyecto: la tabla
> declara el orden completo desde ya, igual que el índice de `docs/README.md`
> avanza por fase.

**Mapa mental de la serie:** el orden es **de adentro hacia afuera**. Primero
construimos cada tier por separado (guías 1 y 2: el backend que responde JSON y
el frontend que renderiza), sin que todavía conversen. Luego los datos (guía 3:
la tabla y el seed que le dan memoria al servidor). Al final, la pantalla que
une los dos tiers (guía 4: el catálogo que la SPA llena con la API). Las fases
siguientes del proyecto (carro, pago, panel, asistente) agregan las guías 5+
sobre esta base — cada una asumiendo que las anteriores están construidas y
verificadas en tu máquina.
