# Guía 16 — El backend en internet: Render, uv y el seed que renace en cada deploy

> **Qué construirás hoy:** la publicación de tu API en Render Free — con
> URL pública HTTPS, Python 3.12 fijado y el catálogo sembrado en cada
> deploy. La guía que cobra dos promesas que la serie dejó escritas: el
> arranque de producción de la guía 1 y el `backend_url` que la guía 9
> dejó esperando "la fase 5".
> **Al terminar tendrás:** tu API viva en
> `https://<tu-servicio>.onrender.com` con `/api/salud` y `/docs`
> respondiendo — y el `return_url` de Webpay congelado por fin.
> **Necesitas:** las guías 1 a 15 completas, TU app corriendo local y una
> cuenta de correo — nada de tarjetas
> ([ADR-019](../04_arquitectura/adr/019-despliegue-free-tier-vercel-render.md)).

---

## Los términos de hoy (antes de copiar nada)

| Término | Qué es, en una frase |
|---|---|
| **Build** | El momento en que la plataforma clona tu repo, instala tus dependencias y prepara la app — el nuestro termina sembrando la BD (seed al build) |
| **Start command** | El comando que arranca tu app en los servidores de la plataforma (nosotros: `uvicorn` con el `$PORT` que Render asigna) |
| **Variable de entorno (en producción)** | La misma de siempre, pero configurada en el dashboard de la plataforma, no en tu `.env` local |
| **Cold start / hibernación** | El plan gratis "duerme" tu API tras ~15 min sin tráfico y despierta en ~1 min — el primer visitante espera ([render.com/docs/free](https://render.com/docs/free), a la fecha) |
| **Disco efímero** | Los archivos que tu app guarda en el servidor **desaparecen** al reiniciar o re-desplegar — [ADR-020](../04_arquitectura/adr/020-persistencia-efimera-seed-idempotente.md), protagonizada hoy |
| **Deploy Git-connected** | La plataforma construye desde tu repo de GitHub: cada `git push` dispara build + deploy automáticos — el "CI/CD en chico" del [doc 07](../07_despliegue.md) |
| **Seed idempotente** | El upsert de la fase 1 que converge sin duplicar: re-ejecutarlo restaura el catálogo sin resetear IDs (D-05/D-06/D-07) |

---

## Paso 0 — Tu proyecto en Git: el requisito que las plataformas comparten

🧠 **El desarrollador piensa:** *tu taller nació sin git — y no fue un
descuido: la guía 1 creó el backend con `--vcs none` precisamente para no
arrastrar un repo vacío antes de tiempo, y por eso mismo te hizo crear el
`backend/.gitignore` A MANO (uv solo lo escribe junto al VCS). Hoy esa
decisión paga: las dos plataformas de esta fase (Render hoy, Vercel en la
guía 17) deployan desde un repo de Git — no desde tu disco. Render va a
construir desde cero: clona el repo, instala, arranca. Lo que no está
pusheado, para Render no existe. Y antes de pushear, la pregunta que
importa más que cualquier comando: **¿qué NO debe subir?** Tu `.env` con
la `SECRET_KEY` y la `GROQ_API_KEY`, y tu `maura.db` — los secretos y la
base local. La buena noticia: ya están blindados. El `.gitignore` de la
guía 1 excluye `.env` y `*.db` (la guía 3 lo celebró cuando nació
`maura.db`), y el scaffold de Vite de la guía 2 trajo el suyo para
`frontend/` (`node_modules`, `dist/` — no lo escribiste tú, venía con el
andamio). La defensa existe desde el día 1; hoy la verificas.*

En la **raíz de tu proyecto** (donde viven `backend/` y `frontend/`),
ejecuta:

```
git init
git add .
git commit -m "Tienda completa hasta la guia 15: catalogo, cuentas, Webpay, panel y asesora"
```

Ahora crea el repo remoto **vía web**: entra a
[github.com/new](https://github.com/new) (sesión con tu cuenta de correo —
gratis), dale un nombre (por ejemplo `tienda-maura`), déjalo **Private** o
Public como prefieras, **sin** README ni `.gitignore` (el commit ya trae
todo) — y con la URL que GitHub te entrega, conecta y pushea:

```
git remote add origin https://github.com/TU-USUARIO/tienda-maura.git
git branch -M main
git push -u origin main
```

✅ **Mini-verificación (la que protege tus secretos):** `git status` está
limpio (nada pendiente) y `git log --oneline` muestra tu commit. Ahora la
prueba que de verdad importa — abre el repo en el navegador
(`https://github.com/TU-USUARIO/tienda-maura`) y revisa el árbol de
archivos: **NO existe** `backend/.env`, **NO existe** `backend/maura.db` y
**NO existe** `frontend/node_modules/`. Si alguno aparece, ALTO: el
`.gitignore` correspondiente no está commiteado — arréglalo ANTES de
seguir (nadie quiere su `SECRET_KEY` en GitHub). Nota honesta de diseño:
que ambas plataformas deployen desde Git no es un requisito molesto — es
el pipeline real que las empresas llaman CI/CD, en chico y gratis
([doc 07](../07_despliegue.md)).

---

## Paso 1 — El Web Service en Render: la tabla que configura tu API

Entra a **[render.com](https://render.com)** y créate una cuenta con tu
correo (el plan **Free** no pide tarjeta — misma vara que la API key de la
asesora, D-69/[ADR-019](../04_arquitectura/adr/019-despliegue-free-tier-vercel-render.md);
si algún flujo de la plataforma te pidiera verificación extra, esa pantalla
pertenece a tu cuenta, no a la guía). Luego: **New + → Web Service**, y
conecta el repo que acabas de pushear. Configura:

| Campo | Valor |
|---|---|
| Name | `tienda-maura` (será parte de tu URL pública) |
| Root Directory | `backend` |
| Runtime | **Python 3** |
| Build Command | `uv sync --locked && uv run python -m app.seed` |
| Start Command | `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Instance Type | **Free** |

🧠 **El desarrollador piensa:** *tres decisiones viven en esta tabla, y las
tres ya estaban firmadas. **Por qué el seed VIAJA en el build**
([ADR-020](../04_arquitectura/adr/020-persistencia-efimera-seed-idempotente.md)):
el plan Free de Render no tiene shell — no puedes entrar al servidor a
ejecutar nada — y su disco es efímero. Si el seed no corriera en el build,
la tabla `usuarios` nacería vacía y el login rechazaría hasta las
credenciales correctas. La solución es el patrón que la serie hermana ya
enseñó (`&& python semilla.py`), ahora con nuestro comando canónico: cada
deploy siembra la BD desde la propia red de Render. Y como el seed es
idempotente (el upsert de SKU converge, D-05/D-06/D-07), re-deployar es
SEGURO por diseño: desde la segunda vez imprime `[=]` en vez de `[+]`, sin
duplicar filas ni resetear IDs. `git push` → redeploy es la vía de
actualización de tu tienda, atómica por plataforma. **Por qué `uvicorn`
directo y no `fastapi run`:** la `guia-01-proyecto-backend.md` prometió que "el equivalente de
producción (`fastapi run`, sin recarga) llegará en la fase de despliegue"
— la promesa se paga con una vuelta de tuerque honesta. `fastapi run` es
un envoltorio fino sobre uvicorn pensado para TU terminal; en Render el
puerto no lo eliges tú: la plataforma te lo pasa EN la variable `$PORT`, y
la forma oficial que Render documenta para FastAPI es uvicorn directo —
`uvicorn main:app --host 0.0.0.0 --port $PORT`
([render.com/docs/deploy-fastapi](https://render.com/docs/deploy-fastapi),
a la fecha) — que adaptamos a nuestro `app.main:app`. El `uv run` que lo
envuelve corre todo dentro del entorno del proyecto: Render soporta uv de
forma nativa desde que detecta tu `uv.lock`
([render.com/changelog/added-uv-to-the-python-native-runtime](https://render.com/changelog/added-uv-to-the-python-native-runtime),
a la fecha) — por eso no generas ningún `requirements.txt`: el lock que
uv ya mantenía ES la lista. **Por qué `--host 0.0.0.0`:** en tu computador
`localhost` basta porque el navegador está al lado; en el contenedor de
Render, `localhost` no es alcanzable desde internet — hay que escuchar en
todas las interfaces. Dos arranques (dev con recarga, prod con `$PORT`),
un mismo código.*

✅ **Mini-verificación:** el formulario de Render acepta los valores sin
quebrar (Root Directory `backend` encontrado, Runtime Python 3
seleccionado) — y antes de crear el servicio, el paso siguiente: las
variables de entorno. No presiones Create todavía.

---

## Paso 2 — Las variables del dashboard: el triple congelado, una por una

🧠 **El desarrollador piensa:** *la regla del día es la misma de todo el
deploy: **configura, no construyas** — ni una línea del código de las
guías 1 a 15 cambia hoy. Los nombres de estas variables no se inventaron
para la ocasión: ya viven en tu `backend/app/config.py` desde las guías 5
y 9, y pydantic-settings los lee en mayúsculas automáticamente
(`backend_url` → `BACKEND_URL`). Lo nuevo es el VALOR: la URL pública que
Render acaba de inventar para ti. Y hay una pieza que en desarrollo
jamás escribiste como variable: `CORS_ORIGINS` — en dev la cubría el
default `["http://localhost:5173"]` de `config.py`. Hoy, por primera vez,
ese campo se escribe como env var de verdad… y con un formato que nadie
adivina: pydantic-settings trata las listas como JSON. Si lo escribes
plano, la app ni parte. ¿Te suena? Es el MECANISMO del fail-fast de
`secret_key` de la guía 5 — sin valor no arranca — ahora en su versión
"valor mal parseado": la defensa es la misma, el diagnóstico vive en el
log del arranque.*

En el formulario de Render, abre **Environment** y agrega las variables
— TODAS antes del primer build:

| Clave | Valor |
|---|---|
| `PYTHON_VERSION` | `3.12.10` |
| `BACKEND_URL` | `https://<tu-servicio>.onrender.com` — **sin** slash final |
| `CORS_ORIGINS` | `["https://<tu-proyecto>.vercel.app"]` — con corchetes y comillas |
| `SECRET_KEY` | una NUEVA, larga y aleatoria — genera una con el comando de abajo |
| `ADMIN_EMAIL` | el email de la dueña en TU seed de producción |
| `ADMIN_PASSWORD` | una contraseña digna (no `admin1234`…) |
| `CLIENTE_EMAIL` | el email de la clienta demo del seed |
| `CLIENTE_PASSWORD` | una contraseña digna |
| `GROQ_API_KEY` | OPCIONAL: tu key de console.groq.com (guía 14) — sin ella la tienda degrada |

Para la `SECRET_KEY` de producción, el comando de siempre — esta vez con
propósito nuevo:

```
python -c "import secrets; print(secrets.token_hex(32))"
```

Las cuatro decisiones que esta tabla congela:

1. **`PYTHON_VERSION=3.12.10`, fully-qualified y obligatoria.** Sin ella,
   un Web Service nuevo en Render arranca con el default actual
   **3.14.3** ([render.com/docs/python-version](https://render.com/docs/python-version),
   a la fecha) — por encima del techo declarado del SDK de Transbank
   (classifiers hasta 3.12, la misma vara de ADR-006): tu `uv sync`
   reventaría contra el `requires-python = ">=3.12,<3.13"` de tu propio
   `pyproject.toml`. La versión debe ser completa (con patch), como exige
   la doc. Este es el Pitfall 1 del deploy: nadie configura Python hasta
   que revienta.

2. **`BACKEND_URL` sin slash final: el `return_url` congelado.** Esta es
   la variable que la `guia-09-ordenes-webpay.md` dejó esperando con un
   comentario que ya lo
   anunciaba — tal como lo construiste en `backend/app/config.py`:

   ```python
   # --- Etapa 3: pago Webpay (ADR-012) ---
   # La URL pública del BACKEND: a ella vuelve el navegador desde Webpay
   # (return_url). NO es cors_origins — esa es la SPA. Dev y producción
   # difieren; la fase 5 la congela junto con el origen público.
   backend_url: str = "http://localhost:8000"
   ```

   Con el valor público seteado, el `return_url` de la ida queda
   congelado a tu URL real:
   `return_url=f"{settings.backend_url}/api/pago/retorno"` (guía 9). Webpay
   exige una URL pública con SSL válido — y tu `*.onrender.com` llega con
   HTTPS incluido de plataforma ([ADR-019](../04_arquitectura/adr/019-despliegue-free-tier-vercel-render.md)).

3. **`CORS_ORIGINS` como JSON array — y con doble trabajo.** Sin
   corchetes y comillas, pydantic-settings no puede parsear la lista y la
   app NO PARTE: "Complex types like `list` … are populated from the
   environment by treating the environment variable's value as a
   JSON-encoded string", y un valor no-JSON lanza `SettingsError`
   ([pydantic.dev](https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/),
   a la fecha). `CORS_ORIGINS=https://<tu-proyecto>.vercel.app` → el log de
   Render muestra `error parsing value for field cors_origins` y santas
   gracias. Con el formato correcto, un solo valor hace DOS trabajos: es
   el origen que el CORS acepta (la regla de la serie: lista explícita,
   jamás comodín — guía 5) **y** es el destino del 302 del retorno —
   `_hacia_spa` redirige a `{settings.cors_origins[0]}/pago/resultado`
   (guía 9). Por ahora apúntalo al lugar que la SPA tendrá mañana:
   `https://<tu-proyecto>.vercel.app` — la guía 17 crea esa URL y vuelve
   a esta pantalla a cerrar el círculo.

4. **`SECRET_KEY` nueva — la de dev no viaja.** Los JWT firmados con la
   key de tu `.env` local no deben valer en internet: una key de
   producción es una key nueva (Pitfall 9 del deploy). El comando genera
   la tuya en tu propia máquina; el valor pegado en el dashboard es tuyo,
   jamás de esta guía. Las cuentas del seed (`ADMIN_*`/`CLIENTE_*`)
   también son de producción: contraseña digna — la tabla `usuarios` de
   tu tienda pública se sembrará con ellas. Y `GROQ_API_KEY` es
   OPCIONAL por diseño (D-61): sin key, la asesora degrada a su 503
   amable y TODO lo demás de la tienda sigue comprando — la tienda no se
   avergüenza de tener un servicio opcional caído.

✅ **Mini-verificación:** el panel Environment de Render lista las 8
claves obligatorias + la opcional, cada una con su valor — y `CORS_ORIGINS`
muestra corchetes y comillas en el valor. La `SECRET_KEY` del dashboard NO
es la misma de tu `.env` local (ábrelos los dos segundos y compáralas: la
única igualdad permitida entre ambos entornos es el nombre de las claves).

---

## Paso 3 — Primer deploy: el log, la salud y el login

🧠 **El desarrollador piensa:** *presionas **Create Web Service** y empieza
el espectáculo silencioso: el log del build en pantalla, en vivo. Las
marcas que importan, en orden: la línea de Python (debe decir **3.12.x** —
tu `PYTHON_VERSION` respetada), el `uv sync` resolviendo contra el lock,
y al final las marcas del seed — el mismo idioma que conoces de la guía 3:
`[+]` creado, `[=]` actualizado. Primer deploy: doce `[+]` de productos y
los `[+]` de las cuentas. Segundo deploy (habrá muchos): puro `[=]` — el
upsert convergiendo, la prueba en vivo de que re-deployar es seguro
(ADR-020). Y cuando el log pase a "live", la batería de siempre contra la
URL pública — la misma que corrías en `localhost:8000`, ahora en
internet.*

✅ **Mini-verificación (la salud pública):** abre
`https://<tu-servicio>.onrender.com/api/salud` → responde `200` con
`{"estado":"ok"}`. Tu API está en internet.

✅ **Mini-verificación (el contrato público):** abre
`https://<tu-servicio>.onrender.com/docs` → el panel Swagger con título
**Maura API** y el contrato **0.4.0** completo: catálogo, cuentas, pago,
panel y asistente. (Que `/docs` sea público es un trade-off declarado del
aula — [ADR-019](../04_arquitectura/adr/019-despliegue-free-tier-vercel-render.md) —
es TU herramienta de verificación.)

✅ **Mini-verificación (el login con las cuentas del seed):** en ese
`/docs` público, pulsa **Authorize** y entra con las credenciales
`ADMIN_*` que acabas de configurar — el login form-urlencoded de la fase 2
funciona igual contra la URL pública. ¿Rechaza credenciales que SABES
correctas? Ese es el síntoma exacto de la tabla `usuarios` vacía: faltó el
seed al build — vuelve al Build Command del Paso 1 y mira el log: las
marcas `[+]` de las cuentas tienen que estar.

> **Esta guía la vives TÚ, en tus cuentas.** El proyecto que escribe esta
> guía no deploya nada: la evidencia con la que se firmó la elección de
> plataforma es documental — las docs oficiales citadas con URL en
> [ADR-019](../04_arquitectura/adr/019-despliegue-free-tier-vercel-render.md)
> (D-73). Las mini-verificaciones de esta guía corren contra TU servicio,
> con TU `SECRET_KEY` y TU URL — como toda la serie, cada quien con la
> suya.

## El cold start: la primera visita de la mañana

El plan Free duerme el servicio tras ~15 min sin tráfico y lo despierta en
~1 min ([render.com/docs/free](https://render.com/docs/free), a la fecha).
No es un bug ni un castigo: es el tier gratis siendo honesto. La primera
visita después del sueño espera hasta un minuto — y si llega mientras la
SPA aún no existe (la construye la guía 17), la verás directamente en el
navegador. Cuando la tienda esté completa, el estado visible será el
heredado de siempre: *"No pudimos conectar con el servidor…"* con su
botón **Reintentar** — que es, accidentalmente, la UX correcta contra el
cold start: cada reintento ayuda a despertar el servicio. Sin pantalla
nueva, sin banner "despertando": la familia de errores que construiste en
dev viaja tal cual a producción.

---

## ❌ El error que este archivo evita

**1. `CORS_ORIGINS` sin JSON.**

```text
❌ CORS_ORIGINS=https://<tu-proyecto>.vercel.app
   → pydantic-settings no puede parsear la lista: SettingsError en el
   arranque — el log dice "error parsing value for field cors_origins"

✅ CORS_ORIGINS=["https://<tu-proyecto>.vercel.app"]
   → corchetes y comillas: es un JSON array, el formato que
   pydantic-settings exige para las listas
```

El mismo mecanismo del fail-fast de `secret_key` (guía 5): sin valor la
app no arrancaba; con valor mal parseado, tampoco. La defensa no cambió —
el diagnóstico vive en el log del arranque, y hoy ese log es el de Render.

**2. La `SECRET_KEY` de producción "heredada" del `.env` de dev.**

```text
❌ copiar la SECRET_KEY del .env local al dashboard
   → funciona… y enseña mal: los JWT firmados en tu computador valdrían
   en internet

✅ python -c "import secrets; print(secrets.token_hex(32))"
   → una key NUEVA por entorno; el comando viaja, el valor jamás
```

Que "funcione" es lo peligroso: nadie lo nota hasta que importa. Una key
por entorno es la higiene mínima de producción (Pitfall 9).

**3. Python sin fijar: el default de Render decide por ti.**

```text
❌ (ninguna PYTHON_VERSION seteada)
   → un Web Service nuevo arranca con 3.14.3 — por encima del techo 3.12
   del SDK de Transbank; el uv sync muere contra tu propio
   requires-python ">=3.12,<3.13"

✅ PYTHON_VERSION=3.12.10
   → fully-qualified, como exige la doc de Render: el techo del SDK
   respetado por configuración, no por suerte
```

---

## 🔧 Errores típicos del deploy (diagnóstico rápido)

| Síntoma | Causa | Remedio |
|---|---|---|
| El build muere con un error de `requires-python` (o resuelve para Python 3.14) | Sin `PYTHON_VERSION`, un servicio nuevo usa el default actual 3.14.3 — por encima del techo 3.12 del SDK de Transbank | Setear `PYTHON_VERSION` en 3.12 fully-qualified en el dashboard ([render.com/docs/python-version](https://render.com/docs/python-version), a la fecha) — Paso 2 |
| La API no parte: `error parsing value for field cors_origins` en el log de Render | `CORS_ORIGINS` escrita como string plano: pydantic-settings exige JSON array para las listas | Escribir el valor como `["https://<tu-proyecto>.vercel.app"]` con corchetes y comillas — Paso 2 |
| La app parte, pero el login rechaza tus credenciales correctas | La tabla `usuarios` está vacía: nadie corrió el seed contra la BD de producción | Build Command con `&& uv run python -m app.seed` — las marcas `[+]` de las cuentas en el log del build — Paso 1 |
| "Funciona", pero la `SECRET_KEY` del dashboard es la misma del `.env` local | La key de producción se heredó de dev: los JWT firmados en tu computador valdrían en internet | Generar una key nueva por entorno con `python -c "import secrets; print(secrets.token_hex(32))"` — jamás reutilizar la de dev — Paso 2 |

---

## ✅ Verificación de la guía 16

Con el servicio en verde en el dashboard de Render:

1. El repo en GitHub existe y el árbol NO lista `backend/.env` ni
   `backend/maura.db` ni `frontend/node_modules/` (Paso 0).
2. El log del primer build muestra Python **3.12.x**, el `uv sync`
   contra el lock y las marcas del seed (`[+]` doce productos + cuentas).
3. `https://<tu-servicio>.onrender.com/api/salud` → `200` con
   `{"estado":"ok"}`.
4. `https://<tu-servicio>.onrender.com/docs` → Maura API, contrato
   **0.4.0** completo.
5. **Authorize** en ese `/docs` público con las credenciales `ADMIN_*`
   del dashboard → el login responde; el perfil de la clienta (`CLIENTE_*`)
   también entra.
6. El panel Environment muestra `CORS_ORIGINS` con corchetes y comillas,
   y una `SECRET_KEY` distinta de la de tu `.env` local.

## 📝 Punto de control (respóndelas sin mirar la guía)

1. Tu `pyproject.toml` dice `>=3.12,<3.13` y Render acaba de crear tu
   servicio sin que toques nada: ¿qué versión de Python corría por
   defecto, contra qué techo chocaba, y con qué variable — y en qué
   formato — se fija? ([ADR-019](../04_arquitectura/adr/019-despliegue-free-tier-vercel-render.md),
   Pitfall 1.)
2. Mañana haces `git push` y Render re-deploya tu API: ¿qué le pasa al
   catálogo, qué le pasa al pedido que aprobó tu clienta hoy — y por qué
   la diferencia no es un bug sino una estrategia firmada? (D-70,
   [ADR-020](../04_arquitectura/adr/020-persistencia-efimera-seed-idempotente.md).)
3. `CORS_ORIGINS` hace DOS trabajos en tu arquitectura: ¿cuáles — y qué
   flujo completo se rompe si mañana lo apuntas a la URL equivocada?
   ¿Y quién corrió esta guía para comprobarlo: el proyecto que la escribió
   o tú? (Guía 9, ADR-012, D-73.)

## Lo que acabas de aprender

- El deploy que configura sin construir: ni una línea de las guías 1 a 15
  cambió — `Root Directory backend`, el Build con el seed adentro y el
  Start con `uvicorn` + `$PORT` son la forma oficial de Render para
  FastAPI adaptada a nuestro taller (uv nativo vía `uv.lock`)
- La promesa de la guía 1 cobrada: el arranque de producción llegó — y es
  `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`, uvicorn
  directo porque el puerto lo asigna la plataforma
- El triple congelado por env vars que ya existían en `config.py`:
  `PYTHON_VERSION=3.12.10` (el techo del SDK de Transbank), `BACKEND_URL`
  sin slash final (el `return_url` de la guía 9 congelado a tu URL
  pública) y `CORS_ORIGINS` como JSON array (el CORS de producción Y el
  destino del 302 del retorno)
- `SECRET_KEY` nueva por entorno con `secrets.token_hex(32)` — el comando
  viaja, el valor jamás; y las cuentas del seed con contraseñas dignas de
  una tienda pública
- El seed VIAJA en el build (ADR-020): el free tier no tiene shell, el
  disco es efímero — y el upsert que converge hace que re-deployar sea
  seguro; `git push` → redeploy es tu pipeline, en chico
- El cold start nombrado con cifras citadas (~15 min de sueño, ~1 min de
  despertar) y la familia de errores heredada con su Reintentar — que es
  accidentalmente la UX correcta para despertar el servicio

**Siguiente:** `guia-17-despliegue-frontend.md` — la SPA en Vercel, el
rewrite que evita el 404 y la URL que se hornea al build.
