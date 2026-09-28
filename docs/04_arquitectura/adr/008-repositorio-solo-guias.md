# ADR-008 — Repositorio solo guías (guide-only): el código vive narrado, no commiteado

- **Estado:** Aceptada
- **Fecha:** 2026-09-28
- **Resuelve:** qué contiene este repositorio y qué construye el alumno (corrección de alcance D-17, portada D-18)

## Contexto

A mitad de la fase 1, el plan original construía la aplicación **dentro de
este repositorio**: el backend se commiteaba acá y los planes verificaban su
trabajo ejecutando código. El usuario corrigió el producto: **este
repositorio es únicamente la guía** (D-17) — el modelo es exactamente
demo-cine, un repo docs-only donde el ciclo de vida se documenta y el código
vive **dentro de las guías de desarrollo** como bloques que el alumno copia en
su máquina. El código construido se retiró del repositorio en el commit
`fc93522`. Con esa corrección, el recorrido documental —no la app corriendo
en un server— es el producto: la experiencia diseñada es que el alumno
construya la tienda siguiendo las guías, y las ✅ verificaciones de cada paso
las corre él en su máquina.

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| **A. Repositorio con código de aplicación + docs juntos** (lo que se hizo primero) | La verificación de los planes es real: se ejecuta la app y se prueba; el docente puede clonar y correr | El repo deja de ser material de aula portátil; el foco se desvía a mantener la app (estado, entornos, dependencias) en vez de la guía; los bloques de las guías se desincronizan del código "de verdad" |
| **B. Repositorio solo guía, con el código narrado dentro de las guías** | El repo es 100% material de clases, liviano y legible; el recorrido del alumno ES el producto; sin estado de aplicación que ensucie los ejemplos | Nada de CI ejecutando la app; el docente no puede "correr el proyecto del repo" — debe construirlo como un alumno más |
| **C. Dos repositorios separados** (guía + código de referencia) | La guía queda limpia Y existe un código ejecutable de referencia | Duplica el mantenimiento: cada cambio se hace dos veces y los dos repos se desincronizan justo donde más importa |

## Decisión

**Opción B**, con la regla explícita: **jamás se commitea código de
aplicación en este repositorio** — ni `backend/`, ni `frontend/`, ni `.venv`,
ni `node_modules`. El código de la tienda existe exclusivamente como bloques
dentro de las guías de `docs/05_desarrollo/`.

Consecuencias operativas de la regla:

- **La verificación de los planes de la guía es documental** (greps, estructura y conteos sobre `docs/` y `README.md`): nada se ejecuta ni instala en el pipeline.
- **Las ✅ verificaciones de cada guía las corre el alumno en su máquina** — la guía es responsable de que cada paso tenga su verificación ejecutable.
- **El README raíz es la portada del producto** (D-18): presenta el recorrido, declara el invariant ("el código completo del proyecto vive narrado en las guías") y mantiene la tabla de estado de las 8 fases conforme avanza el ciclo.

## Consecuencias

**Positivas**
- El repositorio es liviano y 100 % material de clases: se lee, se comparte, se proyecta en aula — sin dependencias que instalar para "ver el proyecto".
- El recorrido del alumno es el producto: cada guía parte de un estado conocido y termina verificada — sin un estado de app que arrastre historia invisible.
- Los bloques de código de las guías no compiten con un código "real" paralelo: la guía es la única fuente.

**Negativas (honestas)**
- **No hay CI que ejecute la aplicación**: el riesgo de guías desactualizadas (una versión del stack que cambia y rompe un paso) no lo detecta ningún pipeline. Mitigación: el stack está versionado y verificado contra registros y docs oficiales (`.planning/research/STACK.md`), y cada guía cierra con una gran verificación final en la máquina del alumno.
- **El docente no puede "correr el proyecto del repositorio"**: para tener la app corriendo debe seguir las guías como cualquier alumno — que es exactamente la experiencia que la guía quiere provocar, pero hay que decirlo.

## Para conversar en clase

1. ¿Qué se pierde al no tener CI ejecutando el código de un proyecto? ¿Qué clase de errores deja de detectar el equipo y cuándo aparecerían?
2. ¿Cómo garantizarían que una guía sigue funcionando tras un cambio de versión (por ejemplo, React 20 o FastAPI 1.0)? Diseñen su mecanismo mínimo.
3. ¿Cuándo convendría el repositorio con código incluido? (pista: ¿qué cambia si el curso no tiene laboratorio, o si el material es de referencia y no de recorrido?).
