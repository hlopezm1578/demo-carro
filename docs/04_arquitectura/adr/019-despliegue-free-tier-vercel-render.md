# ADR-019 — Despliegue en free tier: Vercel para la SPA y Render para la API

- **Estado:** Aceptada
- **Fecha:** 2026-10-01
- **Resuelve:** cómo se publican los dos tiers en internet con URL
  pública y sin costo para el alumno (DEPL-01, con el refresh sin 404 de
  DEPL-02 montado sobre el rewrite de Vercel), firmando la candidata D-69 con
  evidencia documental (D-73 — **D-72 superseded**: sin spike runtime; la
  corroboración son las docs oficiales citadas en
  [`05-RESEARCH.md`](../../../.planning/phases/05-despliegue-y-cierre-de-la-gu-a/05-RESEARCH.md),
  que no encontraron bloqueo para la candidata. El runtime del deploy lo corre
  el alumno con las guías 16-18)

## Contexto

La tienda está construida y verificada hasta la guía 15, pero vive en
`localhost`. Publicarla no es un detalle al final del recorrido: es una
condición del negocio — el `return_url` que Webpay exige debe ser una URL
pública con SSL válido, y esa URL **congela** las tres variables que las
guías ya parametrizaron (`BACKEND_URL`, `CORS_ORIGINS`, `VITE_API_URL`).
Por eso la fase de despliegue va al final del roadmap: hasta que la URL
pública existe, no hay nada que congelar.

La candidata sale del consenso ya investigado en
[`STACK.md`](../../../.planning/research/STACK.md) (estático en
Vercel/Netlify/Cloudflare Pages + Render free para la API con spin-down y
disco efímero). El criterio que la firma es pedagógico (D-69): **un solo
camino por tier** — nada de menús de opciones que dupliquen la guía — y
**tier gratuito sin tarjeta de crédito**, la misma vara que D-60/D-63
exigieron para la API key de la asesora: si el alumno tiene que pagar, la
guía está rota. D-72 había planteado un spike runtime para corroborar la
candidata antes de firmar; D-73 (corrección del usuario, 2026-10-01) lo
supersede: la fase es solo escritura y la corroboración es documental —
las docs oficiales de ambas plataformas se leyeron con URL y fecha, y no
encontraron bloqueo para Vercel Hobby (SPA) + Render Free (API).

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| **A. Vercel Hobby (SPA) + Render Free (API)** — una plataforma por tier | Ambos tiers gratis y sin tarjeta; deploy Git-connected desde GitHub (CI/CD en chico); Framework Preset Vite nativo en Vercel y runtime Python con uv nativo en Render; HTTPS incluido en los subdominios | El servicio free de Render duerme tras ~15 min sin tráfico y despierta en ~1 min; el disco de Render es efímero (ADR-020); uso no-comercial declarado en Hobby |
| **B. Netlify o Cloudflare Pages** en vez de Vercel | Las tres sirven SPA estática con fallback configurable | Duplican la guía sin ganancia pedagógica; Vercel gana por el Framework Preset Vite y el flujo Git-connected más directo para el aula (descartadas: el menú de opciones está vetado por D-69) |
| **C. Fly.io o Railway** en vez de Render | Ambas corren servicios web Python | Railway ya no tiene free real (solo crédito de prueba que se agota); Fly.io no es la que la serie hermana usó — Render es la que demo-cine ya deployó (consistencia de serie) y la que tiene docs oficiales claras para FastAPI |
| **D. Una sola plataforma para ambos tiers** | Una sola cuenta, una sola factura (cero) | Obliga a serverless o plantillas server-side para el backend: cambia la forma del código que las guías 1-15 enseñaron — [ADR-002](002-dos-tiers-spa-y-api.md) la vetaría; la SPA estática y la API Python tienen necesidades distintas y cada plataforma libre hace mejor una de las dos |

## Decisión

**Opción A.** Una plataforma por tier, gratis y sin tarjeta (D-69), con las
reglas de configuración que las guías 16/17 enseñan paso a paso:

1. **Vercel Hobby para la SPA estática** (gratis, uso no-comercial): el
   build de Vite produce archivos estáticos y Vercel los sirve con HTTPS en
   un subdominio propio. El fallback de rutas — que el refresh de
   `/pago/resultado` no dé 404 (DEPL-02) — exige un `vercel.json` con
   rewrite explícito commiteado en la raíz del frontend: Vercel NO infiere
   que el proyecto es SPA. El rewrite es configuración del host, no código
   de la app.
2. **Render Free para la API** (Web Service Python, sin tarjeta): el taller
   ya es un proyecto uv (`pyproject.toml` + `uv.lock`) y Render lo soporta
   de forma nativa. El Start Command sigue la forma oficial
   `uvicorn ... --host 0.0.0.0 --port $PORT`; el Build Command termina con
   el seed idempotente (ADR-020).
3. **`PYTHON_VERSION=3.12.x` fully-qualified obligatorio** (Pitfall 1): sin
   ella, un Web Service nuevo en Render arranca con el default actual
   3.14.3 — por encima del techo declarado del SDK de Transbank (3.12, la
   misma vara que fijó ADR-006). La doc de Render exige la versión completa
   (p. ej. `3.12.10`).
4. **El triple de env vars congelado por el código existente** (Pattern 1
   del research — los nombres NO se inventan, ya viven en `config.py` y
   `api.ts`): `BACKEND_URL` sin slash final congela el `return_url` de
   Webpay; `CORS_ORIGINS` como JSON array es el CORS de producción Y el
   destino del 302 del retorno (`cors_origins[0]`, ADR-012); `VITE_API_URL`
   se hornea al build de la SPA — cambiarla exige redeploy (Pitfall 3).
5. **`SECRET_KEY` nueva por entorno** (Pitfall 9): los JWT firmados con la
   key de dev no deben valer en producción. La guía enseña a generar una
   key digna con `python -c "import secrets; print(secrets.token_hex(32))"`
   — el comando, jamás un valor pegado.
6. **TLS incluido de plataforma, jamás hand-roll**: ambos subdominios
   llegan con HTTPS válido, que es exactamente el requisito SSL del
   `return_url` de Webpay. Emitir certificados a mano es días de trabajo y
   un riesgo sin ninguna ganancia pedagógica.

## Consecuencias

**Positivas**
- Cero costo sin tarjeta para el alumno: cada uno termina con SU tienda
  publicada en sus propias cuentas free — el mismo criterio que la API key
  de la asesora (D-63).
- `git push` → build + deploy automático en ambas plataformas: el alumno
  vive por primera vez un pipeline, en chico (CI/CD en chico).
- URLs públicas HTTPS: P1 de docs/01 — "que se abra desde cualquier
  dispositivo" — se cumple con la URL en el celular de cualquiera.

**Negativas (honestas)**
- **Hibernación:** el servicio free de Render duerme tras ~15 min sin
  tráfico y despierta en ~1 min; el primer visitante de la mañana espera
  con los skeletons heredados de la SPA. Se nombra en las guías y en el doc
  07, no se esconde — y no se contrata UI nueva para "avisar" que despierta.
- **`/docs` y `/redoc` públicos** en la URL de la API: decisión pedagógica
  deliberada (la fila contrato ↔ `/docs` de la Gran verificación final lo
  exige accesible). En un producto real se desactivaría en producción; para
  el aula es la herramienta de verificación del alumno.
- **Free tier no es producción seria:** el uso no-comercial de Hobby se
  declara honesto para una PYME ficticia con pagos sandbox — una tienda
  real con clientes reales necesitaría un tier pagado y un dominio propio.

## Para conversar en clase

1. El rewrite de `vercel.json` hace por configuración lo que un middleware
   del backend no puede: ¿por qué el fallback de rutas de una SPA ES
   responsabilidad del host estático y no del código de la app?
2. Si Render regenerara tu subdominio (`mi-tienda.onrender.com` → otro),
   ¿qué variables de entorno dejarían de calzar y qué flujo completo se
   rompería primero? (pista: empieza en `return_url`).
3. El disco efímero de Render borra la BD en cada redeploy. ¿Por qué es
   aceptable AQUÍ (sandbox, PYME ficticia, seed idempotente) y sería
   inaceptable en una tienda real con clientas reales? ¿Qué cambiaría
   primero? ([ADR-020](020-persistencia-efimera-seed-idempotente.md))

## Evidencia firmada

Todo lo firmado acá descansa en las docs oficiales de ambas plataformas
(disciplina D-73/D-68: evidencia documental citada con URL y "a la fecha";
este ADR NO reporta runtime propio — el runtime del deploy lo corre el
alumno con las guías 16-18). Las citas verbatim están en los Patterns 1-3,
los Pitfalls y §Sources de
[`05-RESEARCH.md`](../../../.planning/phases/05-despliegue-y-cierre-de-la-gu-a/05-RESEARCH.md)
(research 2026-10-01):

- **Doc oficial del plan Hobby de Vercel**
  ([vercel.com/docs/plans/hobby](https://vercel.com/docs/plans/hobby),
  leída 2026-10-01): Hobby es free para uso personal y **no-comercial**,
  sin tarjeta — la declaración que hace honesto el trade-off del aula; los
  límites mensuales del plan viven en esa página.
- **KB oficial del rewrite SPA de Vercel**
  ([vercel.com/kb/guide/why-is-my-deployed-project-giving-404](https://vercel.com/kb/guide/why-is-my-deployed-project-giving-404),
  leída 2026-10-01): Vercel NO infiere que un proyecto es SPA — el fallback
  a `index.html` exige `vercel.json` con rewrite explícito, commiteado en
  la raíz del proyecto (si no está pusheado, el rewrite silenciosamente no
  aplica).
- **Doc oficial del free tier de Render**
  ([render.com/docs/free](https://render.com/docs/free), leída 2026-10-01):
  750 instance-hours/mes, spin-down tras 15 min sin tráfico, wake en ~1
  min, y el disco efímero nombrando textualmente "local SQLite databases"
  entre lo que se pierde — la cita que funda el [ADR-020](020-persistencia-efimera-seed-idempotente.md).
- **Doc oficial de versión de Python en Render**
  ([render.com/docs/python-version](https://render.com/docs/python-version),
  leída 2026-10-01): `PYTHON_VERSION` exige versión fully-qualified y el
  default actual para servicios nuevos es 3.14.3 — por encima del techo
  3.12 del SDK de Transbank (Pitfall 1).
- **Doc oficial de deploy de FastAPI en Render**
  ([render.com/docs/deploy-fastapi](https://render.com/docs/deploy-fastapi),
  leída 2026-10-01): la forma oficial del arranque es
  `uvicorn main:app --host 0.0.0.0 --port $PORT` — la guía la adapta al
  `app.main:app` y al `uv run` del taller.
- **Changelog oficial de uv nativo en Render**
  ([render.com/changelog/added-uv-to-the-python-native-runtime](https://render.com/changelog/added-uv-to-the-python-native-runtime),
  2025-06-12): incluir `uv.lock` en la raíz del servicio habilita uv "in
  place of pip for your service's build command and other scripts" — el
  taller deploya sin generar requirements.txt (a la fecha).

Relacionada: [ADR-012](012-retorno-de-webpay.md) (el retorno de Webpay que
el deploy ejercita en producción sobre URLs públicas),
[ADR-002](002-dos-tiers-spa-y-api.md) (dos tiers estrictos — cada tier en
su plataforma natural),
[ADR-008](008-repositorio-solo-guias.md) (guide-only: las guías enseñan el
deploy, el repo no lo ejecuta — D-17/D-73) y
[ADR-020](020-persistencia-efimera-seed-idempotente.md) (la persistencia
efímera que hace posible este deploy).
