# ADR-002 — Dos tiers estrictos: SPA React + API FastAPI (nada de plantillas en el servidor)

- **Estado:** Aceptada
- **Fecha:** 2026-09-28
- **Resuelve:** cómo se sirven las pantallas del diseño (§4) — la decisión central del proyecto

## Contexto

El diseño definió 3 pantallas responsivas con estados de carga/error/vacío
(§4.1) y filtros que viven en la dirección de la página (§4.1). Pero el
objetivo de ESTA guía no es solo publicar una tienda: es que el alumno aprenda
a **integrar tiers y servicios externos reales** — una SPA que consume un API
por contrato y, en las fases 3 y 4, un pago Webpay y un asistente de IA (Groq) cuyas
credenciales y SDK solo pueden vivir en el servidor.

El proyecto hermano demo-cine enfrentó esta misma decisión y eligió lo
contrario (su ADR-006: SSR con Jinja2 desde el propio FastAPI — un solo
proyecto y despliegue, sin CORS) porque SU objetivo era el camino más corto a
una URL pública. Mismo formato de decisión, contextos distintos: aquí la
complejidad de la separación **es** la materia. Contraste pedagógico
deliberado: dos guías hermanas, la misma mesa de análisis, decisiones opuestas
por objetivos distintos.

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| **A. Monolito con plantillas en el servidor** (FastAPI + Jinja2) | Un solo proyecto y despliegue; el HTML llega renderizado; sin CORS (la elección de demo-cine) | La integración frontend/backend desaparece del ejercicio; las redirecciones de Webpay y el asistente IA se pelean con las plantillas |
| **B. SPA React + API FastAPI estrictamente separadas** | Frontera explícita por contrato (ADR-007); separación de frontend/backend como en la industria; cada tier evoluciona y se despliega solo | Dos proyectos que coordinar; CORS; SEO client-side |
| **C. Híbrido / BFF** (el backend sirve la SPA y el JSON, o SSR tipo Next.js) | Un despliegue con algo de las dos anteriores | Los dos mundos a la vez: tooling fuera del stack y la mitad del curso sin entender ninguno |

## Decisión

**Opción B**, con la regla explícita: **el backend expone JSON y nada más; la
SPA renderiza todo; jamás hay plantillas en el servidor.** Los dos tiers
conversan únicamente a través del contrato (ADR-007). En desarrollo, el proxy
`/api` de Vite hace que la SPA llame a su mismo origen (sin CORS que
configurar); en producción cada tier se publica por separado (fase 5) con CORS
explícito desde `Settings`.

## Consecuencias

**Positivas**
- La frontera entre tiers es un contrato legible, discutible y versionado — el punto pedagógico central de la guía.
- La SPA es un sitio estático publicable gratis; el API se apaga, escala o reescribe sin tocar la interfaz.
- Webpay (fase 3) y el servicio de IA (fase 4) encajan naturalmente: credenciales, SDK y llamadas viven solo en el backend.

**Negativas (honestas)**
- **SEO client-side**: el HTML llega sin contenido y el buscador debe ejecutar JavaScript. Para una PYME real esto duele; para Maura se acepta porque el foco es pedagógico — y es discusión obligada de clase.
- Dos proyectos que coordinar: versiones de Node y Python, dos servidores corriendo en desarrollo, un contrato que mantener alineado.
- CORS hay que configurarlo bien desde el día 1, o los errores de origen cruzado son confusos de diagnosticar.

## Para conversar en clase

1. Maura (la clienta ficticia) pregunta: "¿saldré en Google?" — ¿qué le responden y qué opción técnica lo resolvería?
2. Contrasten con el ADR-006 de demo-cine: la misma decisión en el mismo formato eligió lo contrario. ¿Qué cambió en el contexto que justifica cambiar la respuesta? (pista: el objetivo pedagógico de cada guía).
3. ¿Qué pantalla de Maura justificaría render en el servidor y por qué? (pista: la que querría indexar un buscador).
