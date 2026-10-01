# ADR-020 — Persistencia efímera: SQLite + seed idempotente como estrategia de producción

- **Estado:** Aceptada
- **Fecha:** 2026-10-01
- **Resuelve:** cómo persiste la BD de la tienda en un tier gratuito cuyo
  disco se borra en cada ciclo (D-70, DEPL-01/DEPL-02 en conjunto con el
  [ADR-019](019-despliegue-free-tier-vercel-render.md) que eligió la
  plataforma), con evidencia documental (D-73)

## Contexto

El Render Free del [ADR-019](019-despliegue-free-tier-vercel-render.md)
reinicia el servicio y borra el disco en cada redeploy, restart y
spin-down. No es un bug del tier: es su contrato — la doc oficial del free
tier lo dice con las palabras que hacen innecesaria cualquier paráfrasis:
los cambios al filesystem "are lost", y nombra textualmente
**"local SQLite databases"** entre lo que se pierde
([render.com/docs/free](https://render.com/docs/free), leída 2026-10-01 —
cita textual en §Pitfall 5 de
[`05-RESEARCH.md`](../../../.planning/phases/05-despliegue-y-cierre-de-la-gu-a/05-RESEARCH.md)).
La tienda guarda TODO en un SQLite local (`maura.db`, ADR-005): catálogo,
cuentas y pedidos. La pregunta no es "¿cómo evitamos que se borre?" (eso
cuesta dinero o una migración) sino **"¿qué estrategia de persistencia es
honesta para una tienda sandbox en un aula?"** — y la respuesta ya estaba
construida desde la fase 1: el seed idempotente (D-05/D-06/D-07).

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| **A. SQLite efímero + seed idempotente en el Build Command** | Cero costo y cero migración: la app queda tal cual las guías la construyeron; el upsert del seed (D-05/D-06/D-07) restaura el catálogo en cada deploy desde la propia red de Render; el trade-off se declara y se enseña — la lección ES el contenido | Los datos creados en runtime (pedidos, cuentas nuevas) se pierden en cada ciclo; la tienda "reinicia" al estado de fábrica con cada redeploy/spin-down |
| **B. PostgreSQL Neon free ahora** (cambiar el motor antes de deployar) | La BD sobrevive a los ciclos; STACK.md ya documenta la variante (`DATABASE_URL` + driver `psycopg`) | Migrar el motor a esta altura reescribe parte de las guías 3-15 contra un problema que el aula no tiene; D-70 la fija como camino de crecimiento MENCIONADO, no implementado (descartada como diferida) |
| **C. Persistencia pagada / disco persistente** | Soluciona el problema de raíz | Exige tarjeta y un plan pagado: rompe la vara del free tier sin tarjeta (D-69) para una PYME ficticia con pagos sandbox — fuera del alcance educativo (descartada) |

## Decisión

**Opción A.** SQLite efímero + seed idempotente como estrategia explícita
de producción — el trade-off se firma, no se esconde:

1. **El seed corre al BUILD, no a mano**: el Build Command de Render
   termina en `uv sync --locked && uv run python -m app.seed` — el mismo
   patrón que la serie hermana enseñó (`&& python semilla.py`), ahora con
   el comando canónico de la nuestra. Cada deploy siembra la BD desde la
   propia red de Render, sin shell y sin puertos bloqueados.
2. **El upsert converge sin duplicar** (D-05/D-06/D-07): re-ejecutar el
   seed restaura stock y precios demo sin duplicar filas ni resetear IDs —
   re-ejecutar el deploy es SEGURO por diseño; `git push` → redeploy es la
   vía de actualización de la tienda (atómica por plataforma).
3. **Las DOS capas del disco efímero, dichas por separado** (Pitfall 5 —
   la lección que este ADR firma):
   - **Capa build-time — SIEMPRE revive**: el seed corre dentro del build,
     así que la imagen que despierta en cada ciclo llega con el catálogo
     y las cuentas del seed sembradas. El catálogo NO se pierde nunca.
   - **Capa runtime — vive hasta el próximo ciclo**: lo creado DESPUÉS del
     build (pedidos nuevos, cuentas registradas, cambios de estado)
     habita un disco que el redeploy/spin-down borra. Esos datos se
     pierden en cada ciclo.
4. **El sandbox hace el trade-off aceptable**: Webpay corre en integración
   (los "pagos" son pruebas), la PYME es ficticia y el objetivo es
   pedagógico — una tienda real con clientas reales NO podría aceptar
   perder su historial; esa frontera es exactamente la conversación de
   clase.
5. **El camino de crecimiento queda MENCIONADO, no implementado**: el swap
   futuro a PostgreSQL (Neon free + driver `psycopg`) es un cambio de
   `DATABASE_URL` en el dashboard — las guías no se reescriben, se
   extienden (doc 08 lo retoma como evolución).

## Consecuencias

**Positivas**
- El catálogo siempre vuelve: cada wake/redeploy arranca desde la imagen
  del build con los 12 productos y las cuentas del seed en su estado
  canónico.
- Cero costo, cero migración: la app que las guías 1-15 construyeron
  deploya tal cual — el seed idempotente de la fase 1 paga su entrada como
  estrategia de producción.
- La lección de estado efímero + seed idempotente ES el contenido de la
  fase: el alumno VE el ciclo (crear pedido → redeploy → pedido ido,
  catálogo intacto) en lugar de leerlo en un slide.

**Negativas (honestas)**
- **El historial de pedidos de la clienta NO sobrevive un ciclo**: un
  pedido aprobado hoy desaparece tras el próximo redeploy o spin-down — se
  declara en la guía y en el doc 07, jamás se promete persistencia "porque
  el seed corre en cada deploy". Los empty states heredados ("Todavía no
  hay pedidos") son el estado honesto y correcto tras un ciclo.
- **Las cuentas nuevas también se pierden**: quien se registró después del
  build vuelve a no existir — el login rechaza credenciales que ayer
  funcionaron; el diagnóstico (no un bug) es parte de la lección.
- **La tienda "reinicia" sin aviso**: no hay banner ni UI nueva que anuncie
  el ciclo (zero UI por diseño); la prosa de la guía y del doc 07 lo
  nombran.

## Para conversar en clase

1. El catálogo revive tras un spin-down pero tu pedido de ayer no. Con
   precisión de arquitectura: ¿qué capa de la BD vive en la imagen del
   build y qué capa vive en el disco runtime — y por qué el seed solo
   puede sembrar la primera?
2. Si la tienda fuera real (clientas reales, pagos reales), ¿qué cambiaría
   primero: el seed, el motor, o el tier? ¿Qué dato merecería sobrevivir
   antes que ningún otro y por qué?
3. El swap a PostgreSQL "es solo cambiar `DATABASE_URL`". ¿Qué parte de
   esa frase es literalmente cierta y qué piezas silenciosas arrastra
   (driver, tipos, migraciones)? ¿Cuándo conviene pagar el disco?

Relacionada: [ADR-019](019-despliegue-free-tier-vercel-render.md) (la
plataforma cuyo disco efímero motiva esta estrategia), el seed idempotente
por upsert de la fase 1 (D-05/D-06/D-07, guías 01-03) y
[ADR-013](013-orden-nace-al-pagar-stock-al-aprobar.md) (las órdenes que
habitan esta BD efímera).
