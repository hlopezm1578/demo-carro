# ADR-003 — Monorepo del alumno: backend/ + frontend/ en una sola raíz

- **Estado:** Aceptada
- **Fecha:** 2026-09-28
- **Resuelve:** cómo se organiza el proyecto que el alumno construye (D-11) — dónde viven el tier cliente y el tier servidor

## Contexto

La decisión de dos tiers (ADR-002) produce dos proyectos: una API Python y una
SPA npm. El alumno los construye **juntos, guía por guía** (`05_desarrollo/`):
abre el mismo editor, arranca los dos servidores de desarrollo, y una misma
guía puede tocar ambos lados (la guía del catálogo agrega el endpoint Y la
grilla que lo consume).

Nota de alcance (D-17): este monorepo es el proyecto **en la máquina del
alumno**. Este repositorio contiene solo la guía — el árbol que aquí se decide
es exactamente el que las guías de desarrollo construyen pieza por pieza.

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| **A. Dos repositorios separados** (`maura-api`, `maura-web`) | Frontera física innegable; releases independientes | Duplica la ceremonia para un alumno; la guía tendría que decir "clona el OTRO repositorio" en cada paso; el contrato viviría en un tercero |
| **B. Monorepo simple: una raíz con `backend/` + `frontend/`** | Una carpeta que abrir; cada proyecto conserva su propio tooling (uv / npm); comandos de guía cortos | La raíz no tiene un build único; dos `.gitignore` que cuidar |
| **C. Monorepo con tooling pesado** (npm workspaces + turborepo/nx) | Una sola instalación de dependencias; pipelines compartidos | Complejidad desproporcionada para 1 SPA + 1 API; esconde cómo funciona cada proyecto por dentro |

## Decisión

**Opción B.** Una sola raíz, **dos proyectos independientes** (D-11):
`backend/` se administra con uv (`pyproject.toml` + `uv.lock`, ADR-006) y
`frontend/` con npm. Ninguno importa al otro; la única conexión entre ellos es
el contrato (ADR-007) y, en desarrollo, el proxy `/api` de Vite. Detalle
operativo: `uv init backend --vcs none` evita el repositorio git anidado que
`uv init` crearía dentro del monorepo (ver ADR-006).

## Consecuencias

**Positivas**
- Abrir una carpeta y tener todo el proyecto: las guías se leen sin saltar entre repositorios.
- Cada tier mantiene su ciclo de vida (`uv.lock` por un lado, `package-lock.json` por el otro) sin tooling compartido que aprender.
- El diff de cada guía toca un solo lado, casi siempre — se ve en el historial qué aprendió cada etapa.

**Negativas (honestas)**
- La raíz no es "un proyecto" en ningún sentido que un IDE entienda: no existe un comando que construya o pruebe todo.
- Hay que saber en qué carpeta está parado uno antes de ejecutar un comando, y mantener dos listas de ignorados (`.venv` en backend, `node_modules` en frontend).

## Para conversar en clase

1. ¿Qué tendría que cambiar (tamaño de equipo, ritmo de releases, propiedad del código) para justificar separar esto en dos repositorios?
2. ¿Qué problema resuelven npm workspaces y por qué no lo necesitamos con una sola SPA?
3. ¿Dónde debería vivir el contrato de la API (`contrato_api.yaml`) en un monorepo? ¿Y si fueran dos repos separados? ¿Qué implica cada respuesta para el equipo que lo cambia?
