# ADR-006 — uv como gestor del proyecto Python (con techo 3.12 fijo)

- **Estado:** Aceptada
- **Fecha:** 2026-09-28
- **Resuelve:** cómo se administran dependencias y entorno del tier servidor (D-10) — y qué versión de Python fija el proyecto

## Contexto

El backend necesita un entorno reproducible en la máquina de cada alumno
(C1, RNF-04): las guías deben correr igual en cualquier computador. La
documentación oficial de FastAPI enseña hoy el flujo **uv-first** (`uv add` /
`uv run fastapi dev`, `pyproject.toml` + `uv.lock`), y D-10 lo adoptó. Dos
restricciones duras del proyecto mandan en este ADR:

1. **Techo de Python 3.12**: el SDK `transbank-sdk` de la fase 3 declara
   soporte hasta Python 3.12 (sus classifiers no incluyen 3.13/3.14). Un
   `requires-python = ">=3.12"` sin techo dejaría que uv resolviera 3.13 o
   3.14 en otra máquina — y la fase 3 se rompería tarde y lejos.
2. **`uv init` ejecuta `git init` interno**: dentro del monorepo del alumno
   (ADR-003) crearía un repositorio git anidado en `backend/` y el repositorio
   raíz dejaría de trackear sus archivos.

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| **A. pip + venv + requirements.txt** | Está en todas las máquinas; lo conocen todos los cursos | Sin lockfile real: "funciona en mi máquina"; instalar dependencias a mano en cada guía; resolver versiones es tarea del alumno |
| **B. uv (pyproject.toml + uv.lock)** | Lock reproducible; los comandos de la guía son cortos (`uv add`, `uv run`); es lo que enseña la doc oficial de FastAPI hoy | Una herramienta más que instalar el primer día; `uv.lock` es ruido para quien nunca vio un lockfile |
| **C. Poetry** | Gestor maduro y difundido | Otro formato de proyecto (poetry.lock, secciones propias) que se aleja del flujo que documenta FastAPI; instala más lento en aula |

## Decisión

**Opción B.** El proyecto backend se administra con **uv**:

- **Dependencias:** `uv add "fastapi[standard]" sqlalchemy pydantic-settings` — el `pyproject.toml` declara, el `uv.lock` congela.
- **Ejecución:** siempre `uv run` (`uv run fastapi dev app/main.py`, `uv run python -m app.seed`) — comandos agnósticos de terminal (D-12): funcionan igual en PowerShell, cmd y Git Bash, sin "activar venv".
- **Versión de Python:** `requires-python = ">=3.12,<3.13"` — el techo `,<3.13` es obligatorio por `transbank-sdk` (fase 3) — más el archivo `.python-version` fijado en 3.12.
- **Dentro del monorepo:** `uv init backend --vcs none` — la opción `--vcs none` evita el repositorio git anidado que `uv init` crea por defecto (ver Contexto).

## Consecuencias

**Positivas**
- `uv.lock` garantiza que el entorno de cada alumno resuelva las mismas versiones exactas — la guía no depende de la suerte.
- Los comandos que la guía enseña son los mismos que la documentación oficial de FastAPI: el alumno puede salir del aula y seguir documentado.
- El techo `<3.13` convierte una restricción futura (fase 3) en una decisión temprana visible, no en un bug tardío.

**Negativas (honestas)**
- Hay que instalar uv antes de la primera guía: el prerrequisito está documentado, y pip + venv sigue siendo el fallback de aula soportado (la doc oficial de FastAPI también lo enseña).
- Un lockfile más que leer: las guías dedican un párrafo a explicar qué es `uv.lock` y por qué no se edita a mano.
- El techo 3.12 se quedará viejo cuando `transbank-sdk` amplíe soporte — tocará revisar este ADR, y esa conversación también es material de clase.

## Para conversar en clase

1. ¿Qué garantiza `uv.lock` que `requirements.txt` no? ¿Qué pasa cuando dos alumnos instalan con meses de diferencia?
2. Python 3.14 ya existe: ¿por qué el proyecto se prohíbe pasar de 3.12? (pista: quién fija los techos de versión en un proyecto real — el lenguaje o sus dependencias).
3. ¿Qué habría pasado el día que el alumno hiciera su primer commit del monorepo si `uv init` hubiera creado el `.git` anidado en `backend/`? ¿Cómo lo habría descubierto?
