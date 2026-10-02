# Guía 1 — El proyecto backend: que la API viva

> **Qué construirás hoy:** el proyecto del tier servidor de Maura — un backend
> Python administrado con uv, con su configuración tipada y su primer endpoint
> de salud.
> **Al terminar tendrás:** una API FastAPI corriendo en tu máquina, con
> `http://localhost:8000/api/salud` verificado en tu navegador y el panel
> interactivo `/docs` como anticipo del contrato.
> **Necesitas:** Python 3.12 y [uv](https://docs.astral.sh/uv/) instalados
> (`uv --version` para comprobarlo). No necesitas nada de este repositorio: el
> código vive en esta guía y lo construyes en tu máquina (ADR-008).

---

## Los términos de hoy (antes de copiar nada)

| Término | Qué es, en una frase |
|---|---|
| **Monorepo** | Un solo repositorio con los dos proyectos adentro: `backend/` y `frontend/` (ADR-003) |
| **uv** | El gestor que administra el proyecto Python: dependencias, entorno y comandos, todo con `uv` (ADR-006) |
| **pyproject.toml** | El archivo que declara el proyecto: versión de Python, dependencias y metadatos. uv lo escribe por ti |
| **uv.lock** | El lockfile: congela las versiones exactas de cada dependencia para que el proyecto se reproduzca idéntico en cualquier máquina |
| **Endpoint** | Una "dirección" de la API que responde algo: `/api/salud` responderá `{"estado": "ok"}` |
| **CORS** | La política del navegador que decide qué orígenes pueden leer respuestas de otra fuente. Se configura en el servidor, con lista explícita |
| **Capas** | La forma de organizar el backend: routers → services → repositories → models, cada una con una sola responsabilidad (ADR-001) |

---

## Paso 0 — Tu monorepo, desde cero

🧠 **El desarrollador piensa:** *antes del primer comando necesito decidir dónde
vivirá el proyecto. La decisión ya está tomada (ADR-003): un monorepo con
`backend/` y `frontend/` como hermanos, porque las guías siempre parten
comandos "desde la raíz del monorepo" y así ninguna ruta se rompe después. Crear
la carpeta raíz hoy es gratis; dividir el repo en dos más adelante sería
reescribir todas las rutas.*

Crea una carpeta para tu proyecto (llámala como quieras; en las guías decimos
`maura`) y abre una terminal ahí. Todos los comandos de esta guía se ejecutan
desde esa raíz o desde `backend/`, y funcionan igual en PowerShell, cmd y
Git Bash:

```
maura/
└── (por ahora, vacío)
```

Antes del primer comando, comprueba que uv está instalado: `uv --version`.
Si la terminal no reconoce el comando, instálalo desde
[docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/).
En Windows, ejecuta el instalador oficial en PowerShell:

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

En macOS o Linux:

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Y si ya tienes Python, `pip install uv` también sirve. Tras instalar, cierra
y reabre la terminal para que el comando nuevo quede en el PATH.

✅ **Mini-verificación:** tu terminal, parada en la carpeta nueva, responde a
`uv --version` con algo como `uv 0.12.x`.

---

## Paso 1 — Crear el proyecto con `uv init`

🧠 **El desarrollador piensa:** *el comando que crea el proyecto Python trae una
sorpresa: ejecuta `git init` por dentro. Dentro de un monorepo eso crea un
repositorio git **anidado** en `backend/`, y el repositorio raíz deja de trackear
sus archivos — un problema silencioso que se descubre tarde, el día que revisas
el historial y no encuentra nada. La bandera `--vcs none` lo evita (ADR-006).
Y `--app` pide el layout de aplicación, que es el nuestro: código que se
ejecuta, no una librería que se importa. Falta una tercera bandera: las
versiones recientes de uv crean por defecto un proyecto **empaquetado** —
una carpeta `src/backend/` con su `__init__.py`, más la maquinaria para
construir e instalar el proyecto como si fuera una librería distribuible.
Nuestra API no se distribuye: se ejecuta. Con `--no-package` el template
queda plano y el código vive donde decidimos nosotros, no donde el template
decide.*

Desde la raíz de tu monorepo, ejecuta:

```
uv init backend --vcs none --app --no-package
```

El comando genera `backend/` con un `pyproject.toml`, un `.python-version`,
un `README.md` y un `main.py` de ejemplo (el clásico "Hello, world").
**Borra ese `main.py`**: es demostración del template, y nuestro código vivirá
en el paquete `app/` que creamos en el paso 4 — pegado a las capas de ADR-001,
no suelto en la raíz.

¿Y el `.gitignore`? No viene: uv solo lo genera cuando inicializa el VCS
y con `--vcs none` le pedimos no crearlo. Lo creas tú en el paso 5, con el
contenido listo.

✅ **Mini-verificación:** abre la carpeta `backend/` en tu editor: debe existir
`pyproject.toml`… y **ninguna carpeta `.git`** adentro de `backend/` (si tu
editor muestra archivos ocultos, revísalo ahí). ¿La única carpeta `.git` que
existe —si es que ya hiciste `git init` en tu monorepo— está en la raíz.

---

## Paso 2 — Fijar Python 3.12… con techo

🧠 **El desarrollador piensa:** *el `pyproject.toml` generado dice
`requires-python = ">=3.12"`: cualquier 3.12 o superior. Sobra. En la fase de
pagos integraremos el SDK de Webpay de Transbank, que declara soporte hasta
Python 3.12 — sus versiones probadas no incluyen 3.13 ni 3.14. Sin techo, uv
podría resolver 3.13 en la máquina de tu compañero y la fase 3 se rompería
lejos y tarde. El techo `,<3.13` convierte una restricción futura en una
decisión visible desde el día 1 (ADR-006) — y es exactamente el tipo de cosa
que un `>=` solo no puede expresar.*

Abre **`backend/pyproject.toml`** y deja su primera sección así (edita la línea
`requires-python`; el `description` puede decir lo que quieras):

```toml
[project]
name = "backend"
version = "0.1.0"
description = "API FastAPI en capas de la tienda Maura · Body Splash"
readme = "README.md"
requires-python = ">=3.12,<3.13"
```

Revisa también el archivo **`backend/.python-version`**: debe decir `3.12` (uv
lo crea con la versión que encontró en tu máquina; si dice otra cosa,
corrígalo a `3.12`). Ese archivo le indica a uv qué intérprete usar cada vez
que corres algo dentro del proyecto.

✅ **Mini-verificación:** dentro de `backend/`, ejecuta `uv run python --version`
— responde `Python 3.12.x` (uv descarga el intérprete si tu máquina no lo tenía).
Abre `pyproject.toml` y confirma que la línea dice `">=3.12,<3.13"` completa,
con el techo.

---

## Paso 3 — Las dependencias, congeladas

🧠 **El desarrollador piensa:** *instalo tres piezas y ninguna es casualidad.
`fastapi[standard]` trae el framework **más** lo que un servicio real necesita
de inmediato: uvicorn (el servidor), fastapi-cli (los comandos `fastapi dev`),
httpx (el cliente HTTP de pruebas) y otros. `sqlalchemy` será nuestro ORM cuando
lleguen los datos (guía 3). `pydantic-settings` lee configuración tipada desde
variables de entorno. Cada `uv add` escribe la dependencia en `pyproject.toml`
y congela la versión exacta en `uv.lock` — ese lockfile es la garantía de
reproducibilidad que `requirements.txt` suelto nunca dio (RNF-04).*

Desde `backend/` (dentro de la carpeta, no en la raíz), ejecuta:

```
uv add "fastapi[standard]" sqlalchemy pydantic-settings
```

Verás cómo uv resuelve el grafo completo de dependencias y crea el entorno
virtual del proyecto (`.venv/`, que vive dentro de `backend/` y jamás se sube
al repositorio). Al terminar, tu `pyproject.toml` queda así:

```toml
[project]
name = "backend"
version = "0.1.0"
description = "API FastAPI en capas de la tienda Maura · Body Splash"
readme = "README.md"
requires-python = ">=3.12,<3.13"
dependencies = [
    "fastapi[standard]>=0.141.1",
    "pydantic-settings>=2.15.0",
    "sqlalchemy>=2.1.1",
]
```

✅ **Mini-verificación:** dentro de `backend/` existen `uv.lock` (ábrela y mira
la lista congelada: fastapi, uvicorn, httpx…) y la carpeta `.venv/`. Y
`uv run python --version` sigue respondiendo `Python 3.12.x`.

---

## Paso 4 — `app/` y `config.py`: todo lo configurable, en un solo lugar

🧠 **El desarrollador piensa:** *el código vivirá en un paquete `app/` que
crecerá por capas — `routers/`, `models/`, `services/` — en las próximas guías,
cuando tengan contenido: una carpeta vacía no le enseña nada a nadie (ADR-001).
Hoy empiezo por `config.py`, y lo escribo con `pydantic-settings` en vez de
constantes: cada cosa que pueda variar entre mi máquina y el servidor de
producción —la base de datos, los orígenes permitidos— queda en un solo lugar,
con valores por defecto de desarrollo y sobreescribibles por variables de
entorno. Las credenciales que llegarán en las fases de pago e IA jamás irán en
el código: vivirán como variables de entorno y este archivo ya tiene el patrón
preparado para recibirlas.*

Crea dentro de `backend/` la carpeta `app/` con el archivo **`app/__init__.py`**
(puede quedar vacío; su sola existencia le dice a Python "esta carpeta se
importa como un paquete"):

```python
# app/__init__.py
# (vacío a propósito: su presencia es lo que importa)
```

Y crea **`app/config.py`**:

```python
"""Configuración tipada de la API.

TODO lo configurable vive en un solo lugar: pydantic-settings carga
valores por defecto de desarrollo y permite sobreescribirlos con
variables de entorno (p. ej. DATABASE_URL, CORS_ORIGINS). Los secretos
jamás van en el código.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Ajustes del backend. En producción se sobreescriben por entorno."""

    database_url: str = "sqlite:///./maura.db"
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
```

Dos detalles que acabas de escribir, explicados:

- `database_url` apunta a SQLite: un archivo local, cero instalación — la
  decisión de arranque de la fase de datos (ADR-005). La guía 3 lo usará tal
  cual, sin cambiar este archivo.
- `cors_origins` trae **un solo origen**: el servidor de desarrollo de Vite
  (`http://localhost:5173`), que conocerás en la guía 2. Lista explícita,
  jamás comodín — lo desarrollamos en el paso 5.

✅ **Mini-verificación:** desde `backend/`, ejecuta:

```
uv run python -c "from app.config import settings; print(settings.cors_origins)"
```

Debe imprimir `['http://localhost:5173']` — el archivo importa, la clase se
instancia y el default está vivo. Sin secretos: solo defaults de desarrollo.

---

## Paso 5 — `main.py` y `/api/salud`: composición, no lógica

🧠 **El desarrollador piensa:** *`main.py` no va a contener lógica de negocio en
su vida (ADR-001): su trabajo es **componer** —decir qué existe y en qué orden—.
Hoy compone poco: la instancia FastAPI con su nombre, el middleware de CORS y
un router de salud. El endpoint de salud lo instalo desde el día 1 porque es la
forma más barata de responder "¿está viva la API?" — y porque el contrato
(`contrato_api.yaml`, fase 4 del ciclo) ya lo promete bajo `/api/salud`.
El CORS va con orígenes EXPLÍCITOS desde settings (ADR-002): en desarrollo el
proxy de Vite ni lo usará, pero configurarlo bien desde hoy evita el error
confuso del día que el backend reciba un origen cruzado real.*

Crea **`app/routers/__init__.py`** (vacío, igual que el anterior) y
**`app/routers/salud.py`**:

```python
"""Endpoint de salud: chequeo de vida del servicio."""

from fastapi import APIRouter

router = APIRouter(tags=["Operación"])


@router.get("")
def estado_del_servicio() -> dict[str, str]:
    """GET /api/salud — responde {"estado": "ok"} si el servicio está arriba."""
    return {"estado": "ok"}
```

Y crea **`app/main.py`**:

```python
"""Composición de la aplicación FastAPI.

Solo este archivo arma la app (regla de la arquitectura en capas, ADR-001):
crea la instancia, agrega middlewares y registra los routers con sus
prefijos /api. No contiene lógica de negocio.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import salud

app = FastAPI(
    title="Maura API",
    version="0.1.0",
    description=(
        "API del catálogo de la tienda Maura · Body Splash. Tier servidor de "
        "los dos tiers: solo JSON bajo /api, jamás plantillas HTML."
    ),
)

# CORS con orígenes EXPLÍCITOS desde settings (ADR-002): lista de
# desarrollo, nunca una lista comodín.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(salud.router, prefix="/api/salud")
```

Fíjate: el router se registra con `prefix="/api/salud"` y su ruta es `""` — la
dirección completa la decide `main.py` al componer, no el router. Cuando la
guía 4 agregue el router de productos, será **una línea más** en este mismo
archivo: eso es crecer por composición.

Antes de seguir, crea el archivo **`backend/.gitignore`**: con `--vcs none`
uv no inicializó git y por eso tampoco generó este archivo (uv solo lo
escribe junto al VCS). El contenido es este (cubre el entorno, la caché, la
base de datos local y los secretos sueltos en un `.env`):

```
# Python
__pycache__/
*.pyc
*.pyo
.venv/

# Base de datos local (SQLite)
*.db

# Variables de entorno (secretos fuera del repo)
.env
```

✅ **Mini-verificación:** la estructura quedó así — `backend/app/__init__.py`,
`backend/app/config.py`, `backend/app/main.py`, `backend/app/routers/__init__.py`
y `backend/app/routers/salud.py`. El `backend/.gitignore` que acabas de crear
menciona `.env` y `*.db`.

---

## Paso 6 — Encender la API

🧠 **El desarrollador piensa:** *arranco con `fastapi dev` — el comando de
desarrollo que trae `fastapi[standard]`: levanta uvicorn con recarga automática
(cada vez que guardo un archivo, el servidor se reinicia solo) y envuelto en
`uv run` para que corra dentro del entorno del proyecto sin activar nada. El
equivalente de producción (`fastapi run`, sin recarga) llegará en la fase de
despliegue. Y la primera URL que abro no es la API: es la documentación —
porque si `/docs` ya muestra mi endpoint, el ciclo importar→componer→responder
funciona completo.*

Desde `backend/`, ejecuta:

```
uv run fastapi dev app/main.py
```

Verás el arranque de uvicorn con la dirección local. Ahora, en tu navegador:

1. Abre **http://localhost:8000/api/salud** → debes ver `{"estado":"ok"}`
2. Abre **http://localhost:8000/docs** → el panel interactivo de Swagger UI,
   mostrando tu endpoint **salud** bajo el título **Maura API** que definiste
   en `main.py`

> 🤯 **Date ese segundo:** acabas de levantar una API documentada. Ese panel
> `/docs` se arma solo desde tu código — y es el anticipo de algo más grande:
> en la fase 4 del ciclo diseñamos un **contrato OpenAPI** antes de codificar
> (ADR-007), y la verificación final de la guía 4 será comparar este panel
> contra ese contrato.

Para detener el servidor: `Ctrl+C` en la terminal.

✅ **Mini-verificación:** las dos URLs de arriba responden lo descrito, con la
API corriendo. Déjala corriendo: la guía 2 conversará con ella.

---

## ❌ El error que este archivo evita

**1. El `.git` anidado.** Si hubieras corrido `uv init backend` sin `--vcs
none`, uv habría ejecutado `git init` dentro de `backend/`. Tu monorepo habría
quedado con un repositorio **dentro** del repositorio: `git status` en la raíz
vería `backend/` como una caja sellada, sin trackear ninguno de sus archivos.
El error se descubre tarde — el día que buscas el historial de tu backend y no
existe. Si ya te pasó: borra la carpeta `backend/.git` (solo esa) antes de tu
primer commit, y el problema muere ahí. La regla que queda: **siempre** `uv
init --vcs none` dentro de un monorepo.

**2. El CORS comodín.** El error clásico no falla en desarrollo — falla al
publicar:

```python
# ❌ NUNCA: "funciona" en dev y abre la API a cualquier origen en producción
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
)

# ✅ SIEMPRE: lista explícita, leída de la configuración
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,   # ["http://localhost:5173", ...]
    allow_methods=["GET"],
    allow_headers=["*"],
)
```

La lista comodín apaga el error de hoy a costa de la seguridad de mañana: la
versión ✅ responde "¿quién puede leerme?" desde `config.py`, donde el día de
desplegar agregas el origen de producción con una variable de entorno — sin
tocar una línea de `main.py`.

---

## ✅ Verificación de la guía 1

Con la API corriendo (`uv run fastapi dev app/main.py` desde `backend/`):

1. **http://localhost:8000/api/salud** → `{"estado":"ok"}`
2. **http://localhost:8000/docs** → panel Swagger UI titulado **Maura API**,
   con el endpoint de salud operativo (puedes ejecutarlo desde el mismo panel:
   botón *Try it out* → *Execute*)

Sin la API corriendo, ninguna de las dos responde — esa es también información:
el chequeo de salud sirve exactamente para distinguir "el servicio está abajo"
de "el servicio está roto".

## 📝 Punto de control (respóndelas sin mirar la guía)

1. ¿Para qué sirven las banderas `--vcs none` y `--no-package` en `uv init`, y
   qué rompería (o sobraría) sin cada una?
2. ¿Por qué la configuración vive en `Settings` (pydantic-settings) y no en
   constantes pegadas en `main.py`? ¿Dónde terminarían los secretos de las
   fases de pago e IA si usaras constantes?
3. ¿Qué hace el middleware CORS que registramos, y por qué la lista de orígenes
   viene de `settings` en vez de ir escrita en `main.py`?

## Lo que acabas de aprender

- Crear un proyecto Python dentro de un monorepo con uv, evitando el repositorio anidado
- Fijar un techo de versión de Python por una dependencia futura (transbank-sdk, fase de pagos)
- Qué congelan `pyproject.toml` y `uv.lock`, y por qué el proyecto se reproduce en cualquier máquina (RNF-04)
- Configuración tipada con pydantic-settings: defaults de desarrollo, sobrescritura por entorno, cero secretos en código
- El patrón "punto de composición": `main.py` compone, no piensa (ADR-001)
- CORS con orígenes explícitos desde el día 1 (ADR-002)
- Tu primer endpoint y la documentación automática de FastAPI — el anticipo del contrato (ADR-007)

**Siguiente:** guia-02-proyecto-frontend.md — el otro tier: la SPA React con
TypeScript, la marca de Maura y la landing que ya conversará con esta API.
