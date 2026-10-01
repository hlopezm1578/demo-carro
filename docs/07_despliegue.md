# Fase 7 — Despliegue: Maura

> **Guía:** Demo Carro — ciclo de vida del software en una tienda de body splash (segunda guía de la serie, hermana de demo-cine)
> **Fase del ciclo de vida: 7. Despliegue**
> **Qué construirás hoy:** la publicación real — tu tienda con URL pública en internet, gratis y sin tarjeta de crédito.
> **Al terminar tendrás:** la tienda de Maura abierta desde cualquier dispositivo, y una lección de arquitectura que ningún slide enseña: el disco efímero.
> **Necesitas:** las guías 1 a 18 (o al menos la app completa hasta la 15) y una cuenta de correo.
> **Decisión de fondo:** [ADR-019](04_arquitectura/adr/019-despliegue-free-tier-vercel-render.md) (Vercel + Render) **y** [ADR-020](04_arquitectura/adr/020-persistencia-efimera-seed-idempotente.md) (SQLite efímero + seed).
> **Fecha:** 2026-10-01

---

## La primera petición de Maura es la última en cumplirse

En la fase 1, Maura pidió ocho cosas. La primera de la lista: *una tienda
online propia, **que se abra desde cualquier dispositivo*** (P1 en
[01_necesidad_del_cliente.md](01_necesidad_del_cliente.md)). Construir el
catálogo, el carro, el pago y las cuentas no la cumplió: mientras la tienda
vivió en `localhost`, "cualquier dispositivo" era solo el tuyo. La URL
pública — tu tienda cargando en el celular de cualquiera — es el momento
en que P1 pasa de promesa a hecho.

¿Y por qué el despliegue va al FINAL del recorrido y no al principio?
Porque publicar no es un detalle cosmético: es el acto que **congela** las
URLs que Webpay exige. El `return_url` que le pasamos a Transbank debe ser
una URL pública con SSL válido — hasta que la tienda existe en internet,
no hay nada que congelar. Cada pieza que las guías parametrizaron con ese
fin explícito (`BACKEND_URL` en la fase 3, `VITE_API_URL` en la fase 1,
`CORS_ORIGINS` desde la primera guía del backend) cobra su promesa aquí.

## Los términos de hoy

| Término | Qué es, en una frase |
|---|---|
| **Build** | El momento en que la plataforma clona tu repo, instala tus dependencias y prepara la app — el nuestro termina sembrando la BD (seed al build) |
| **Start command** | El comando que arranca tu app en los servidores de la plataforma (nosotros: `uvicorn` con el `$PORT` que Render asigna) |
| **Variable de entorno (en producción)** | La misma de siempre, pero configurada en el dashboard de la plataforma, no en tu `.env` local |
| **Cold start / hibernación** | El plan gratis "duerme" tu API tras ~15 min sin tráfico y despierta en ~1 min — el primer visitante espera ([render.com/docs/free](https://render.com/docs/free), a la fecha) |
| **Disco efímero** | Los archivos que tu app guarda en el servidor **desaparecen** al reiniciar o re-desplegar — las docs de Render nombran textualmente "local SQLite databases" entre lo que se pierde ([render.com/docs/free](https://render.com/docs/free), a la fecha). [ADR-020](04_arquitectura/adr/020-persistencia-efimera-seed-idempotente.md), protagonizada hoy |
| **Fallback SPA / rewrite** | La regla del host estático que sirve `index.html` para CUALQUIER ruta — sin ella, el refresh de `/pago/resultado` da 404 (DEPL-02) |
| **Env var horneada (`VITE_*`) | Las variables de Vite que empiezan con `VITE_` se reemplazan estáticamente **al build** — cambiarlas en el dashboard no hace nada hasta el redeploy |
| **Seed idempotente** | El upsert de la fase 1 que converge sin duplicar: re-ejecutarlo restaura el catálogo sin resetear IDs (D-05/D-06/D-07) |

---

## La decisión: qué plataforma, y por qué gratis

🧠 **El desarrollador piensa:** *la regla del curso es una sola: si el alumno
tiene que pagar, la guía está rota. La API key de la asesora fue gratis y
sin tarjeta (D-63); el despliegue no puede ser la excepción (D-69). Por eso
la vara fue free tier real — el plan Hobby de Vercel para la SPA (gratis,
uso no-comercial, [vercel.com/docs/plans/hobby](https://vercel.com/docs/plans/hobby),
a la fecha) y el plan Free de Render para la API (750 instance-hours al
mes y sin tarjeta, [render.com/docs/free](https://render.com/docs/free), a
la fecha). Y una sola plataforma por tier, sin menú de alternativas: el
alumno necesita UN camino que funcione, no tres que quizás — las
alternativas (Netlify, Cloudflare Pages, Fly.io, Railway) viven discutidas
y descartadas dentro del
[ADR-019](04_arquitectura/adr/019-despliegue-free-tier-vercel-render.md),
que es su lugar.*

La forma de la decisión respeta la arquitectura que ya construimos
(ADR-002): la SPA es un puñado de archivos estáticos — su hogar natural es
un host estático con CDN; la API es un proceso Python de verdad — su hogar
natural es un web service. El deploy no cambia NI UNA línea del código de
las guías 1 a 15: **configura, no construye**. Lo único que "nueva" es un
`vercel.json` con el rewrite del fallback (porque Vercel NO adivina que tu
proyecto es SPA) — y eso es configuración del host, no código de la app.

El orden de la fase también es parte de la decisión: primero la API en
Render (`guia-16-despliegue-api.md`), porque su URL pública congela el
`return_url`; después la SPA en Vercel (`guia-17-despliegue-frontend.md`),
que hornea esa URL en su build y commitea el rewrite; y al final la
verificación completa (`guia-18-despliegue-cierre.md`): los 4 flujos de
Webpay contra tu ambiente desplegado, con la Gran verificación final de la
serie. El triple de variables que la fase congela — `BACKEND_URL` (sin
slash final: el `return_url`), `CORS_ORIGINS` (JSON array: el CORS de
producción Y el destino del 302 del retorno) y `VITE_API_URL` (la base URL
horneada al build de la SPA) — ya estaba parametrizado por las guías; esta
fase solo les da su valor de producción.

## La lección del disco efímero — en DOS capas (D-70)

La doc oficial del free tier de Render lo dice con palabras que no necesitan
paráfrasis: los cambios al filesystem "are lost" en cada redeploy,
restart o spin-down, y nombra textualmente **"local SQLite databases"**
entre lo que se pierde ([render.com/docs/free](https://render.com/docs/free),
leída 2026-10-01, a la fecha). Nuestra BD entera (`maura.db`) es un SQLite
local: el catálogo, las cuentas, los pedidos. ¿Entonces la tienda se borra
cada vez que duerme? **No exactamente — y la diferencia ES la lección:**

1. **La capa del build SIEMPRE revive.** El Build Command termina con el
   seed idempotente: cada deploy siembra la BD desde la propia red de
   Render, y la imagen que despierta en cada ciclo llega con el catálogo y
   las cuentas del seed en su estado canónico. El catálogo NO se pierde
   nunca — re-ejecutar el deploy es seguro por diseño del upsert (D-05,
   D-06, D-07), y `git push` → redeploy es la vía de actualización de la
   tienda: atómica por plataforma, el "CI/CD en chico".
2. **La capa runtime vive hasta el próximo ciclo.** Lo creado DESPUÉS del
   build — pedidos nuevos, cuentas registradas, cambios de estado — habita
   un disco que el redeploy o el spin-down borra. El historial de pedidos
   de tu clienta de ayer NO sobrevive el ciclo: tras un reinicio, los
   empty states heredados ("Todavía no hay pedidos") son el estado honesto
   y correcto, no un bug.

[ADR-020](04_arquitectura/adr/020-persistencia-efimera-seed-idempotente.md)
firma este trade-off como estrategia explícita: aceptable porque Webpay
corre en sandbox y la PYME es ficticia; impensable en una tienda real — y
el camino de crecimiento (PostgreSQL free con cambio de `DATABASE_URL`)
queda mencionado, no implementado.

**El arranque frío, nombrado y no escondido:** el servicio free de Render
duerme tras ~15 min sin tráfico y despierta en ~1 min
([render.com/docs/free](https://render.com/docs/free), a la fecha). Tu SPA
estática carga al instante (Vercel no duerme); las llamadas a la API quedan
en sus skeletons heredados hasta por un minuto. No hay pantalla ni banner
"despertando": es el tier gratis siendo honesto, y el botón "Reintentar"
heredado es accidentalmente la UX correcta — cada reintento ayuda a
despertar el servicio.

> ⚠️ **Caveat del copy heredado:** si la API duerme, la tienda muestra el
> mensaje de error de la familia *"Revisa que el backend esté corriendo en
> el **puerto 8000** e inténtalo de nuevo."* — wording pensado para tu
> computador de desarrollo, visto ahora por una clienta en internet. Es
> **aceptado para esta fase** (la serie no re-edita guías construidas).
> Regla de decisión: pasa a defecto real solo si la evidencia viva del
> alumno en producción lo declara — y entonces se corrige en AMBOS lugares
> (guía + taller) junto con un amendment al UI-SPEC, nunca en silencio.

## Dónde están los pasos

Este documento firma la DECISIÓN; los pasos viven en las guías, como toda
la serie:

- [**Guía 16** — `guia-16-despliegue-api.md`](05_desarrollo/guia-16-despliegue-api.md):
  la API a Render — la cuenta free, `PYTHON_VERSION` en 3.12 (el techo del
  SDK de Transbank vs. el default 3.14.3 de Render,
  [render.com/docs/python-version](https://render.com/docs/python-version),
  a la fecha), el seed al build y las variables de entorno del dashboard.
- [**Guía 17** — `guia-17-despliegue-frontend.md`](05_desarrollo/guia-17-despliegue-frontend.md):
  la SPA a Vercel — el `vercel.json` con el rewrite commiteado,
  `VITE_API_URL` horneada al build y la mini-verificación del refresh sin
  404 (DEPL-02).
- [**Guía 18** — `guia-18-despliegue-cierre.md`](05_desarrollo/guia-18-despliegue-cierre.md):
  los 4 flujos de Webpay contra tu ambiente desplegado y la **Gran
  verificación final** de la serie — tú la corres, en tus cuentas.

El método para verificar todo eso no se inventa aquí: es el que la fase 6
nombra ([06_pruebas.md](06_pruebas.md)) — mini-verificación por paso, tabla
de cierre con Origen por fila, y la evidencia en tus propias cuentas.

## 🔧 Errores típicos del deploy (diagnóstico rápido)

| Síntoma | Causa | Remedio |
|---|---|---|
| El build de Render muere con un error de `requires-python` (o resuelve para Python 3.14) | Sin `PYTHON_VERSION`, un servicio nuevo usa el default actual 3.14.3 — por encima del techo 3.12 del SDK de Transbank (Pitfall 1) | Setear `PYTHON_VERSION` en 3.12 fully-qualified en el dashboard ([render.com/docs/python-version](https://render.com/docs/python-version), a la fecha) — guía 16 |
| La SPA en producción pide a `localhost` o aparece `//api` en la pestaña Network | `VITE_API_URL` cambiada SIN redeploy (se hornea al build) o escrita con slash final (Pitfall 3) | Valor SIN slash final + redeploy después de cualquier cambio — guía 17 |
| La API no parte: `error parsing value for field cors_origins` en el log de Render | `CORS_ORIGINS` escrita como string plano: pydantic-settings exige JSON array para las listas (Pitfall 4) | Escribir el valor como `["https://tu-proyecto.vercel.app"]` con corchetes y comillas — guía 16 |
| Navegar desde `/` funciona, pero el refresh o un link directo a `/pago/resultado` da 404 | El `vercel.json` con el rewrite no está commiteado (o el Framework Preset quedó "Other"): el rewrite silenciosamente no aplica (Pitfall 7) | Commitear el `vercel.json` en la raíz del frontend y pushear — el refresh de una ruta profunda ES la mini-verificación — guía 17 |
| "Funciona", pero la `SECRET_KEY` del dashboard es la misma del `.env` local | La key de producción se heredó de dev: los JWT firmados en tu computador valdrían en internet (Pitfall 9) | Generar una key nueva por entorno con `python -c "import secrets; print(secrets.token_hex(32))"` — jamás reutilizar la de dev — guía 16 |

---

## ✅ Verificación de la fase (en tu URL pública)

Lo que debe ser cierto al terminar las guías 16-18 — la tabla de cierre
completa, fila por fila con su Origen, vive en la Gran verificación final
de la guía 18:

| # | Verificación | Origen |
|---|---|---|
| 1 | `https://TU-API.onrender.com/api/salud` responde `200` con `{"estado":"ok"}` | DEPL-01, ADR-019 |
| 2 | El refresh (o un link directo) a `/pago/resultado` desde la URL pública carga la SPA — sin 404 | DEPL-02, ADR-019 |
| 3 | Los 4 flujos de retorno de Webpay (aprobado, anulado, timeout, error) llegan a tu `return_url` público y terminan en el voucher/pantalla correcta | DEPL-02, ADR-012, ADR-019 |

---

## 📝 Punto de control

1. El `return_url` de Webpay explica por qué esta fase va al final y no al
   principio: ¿qué URLs quedaron **congeladas** el día que deployaste, y
   qué flujo completo se rompe si mañana cambia tu subdominio de Render?
   (D-69, ADR-019)
2. Tras un redeploy tu pedido de ayer desapareció pero el catálogo está
   intacto. Explica la diferencia con precisión de arquitectura: ¿qué capa
   revivió con la imagen del build y qué capa murió con el disco? (D-70,
   ADR-020)
3. Cambiaste `VITE_API_URL` en el dashboard de Vercel y la SPA siguió
   pidiendo a la URL vieja: ¿por qué no bastó con guardar el valor, y qué
   tuvo que pasar después? (ADR-019, env var horneada)

## Lo que acabas de aprender

- Publicar dos tiers en free tier real sin tarjeta: cada plataforma en su
  rol natural (estática con CDN / web service Python)
- El deploy que congela: `BACKEND_URL`, `CORS_ORIGINS` y `VITE_API_URL`
  pasaron de parámetros de dev a contratos de producción
- El fallback SPA como configuración del host (el rewrite de `vercel.json`
  ES el DEPL-02), no como código de la app
- El disco efímero en dos capas: el seed del build revive el catálogo; lo
  runtime se pierde — estrategia firmada, no bug escondido
- El arranque frío del free tier nombrado con cifras citadas — honestidad
  como decisión pedagógica

**Siguiente:** [08_mantenimiento.md](08_mantenimiento.md) — el ciclo se
cierra (y se reabre).
