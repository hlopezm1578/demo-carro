# ADR-007 — API-first: el contrato OpenAPI se diseña y aprueba antes del código

- **Estado:** Aceptada
- **Fecha:** 2026-09-28
- **Resuelve:** cómo se define la interfaz del API — la única conversación entre los dos tiers (D-15) — y su relación con el desarrollo

## Contexto

Con dos tiers estrictos (ADR-002), la interfaz del API vale más que cualquier
implementación: es lo único que los dos proyectos comparten. Con FastAPI existe
una tentación concreta: escribir el código primero y dejar que el framework
**genere** la documentación automáticamente (`/docs`). Eso es **code-first**:
el contrato llega después y hereda todas las decisiones del código, buenas y
malas. Esta guía aplica **API-first**, igual que el resto del ciclo de vida:
necesidad → requerimientos → diseño → **contrato** → código. El contrato
([`contrato_api.yaml`](../contrato_api.yaml), OpenAPI 3.0.3) ya fue diseñado y
aprobado en esta misma fase — antes de que existiera una sola línea de
backend.

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| **A. Code-first** (FastAPI genera `/docs` desde el código) | Cero pasos extra; la doc nunca se desactualiza del código | El contrato llega tarde: no se puede discutir ni aprobar antes; renombrar una ruta o cambiar un código de respuesta es "gratis" y nadie se entera |
| **B. API-first manual** (contrato OpenAPI versionado primero; el código lo implementa) | La interfaz se discute en lenguaje de contrato; sirve como mock mientras no hay backend; evaluación objetiva del desarrollo | Doble mantenimiento (contrato + código) sin herramienta que los sincronice |
| **C. API-first con generación** (del contrato se genera el esqueleto de código) | Drift imposible por construcción | Tooling pesado para el alcance de la guía; esconde justo lo que se quiere enseñar |

## Decisión

**Opción B.** El contrato vive en
[`contrato_api.yaml`](../contrato_api.yaml) (OpenAPI 3.0.3), es **la fuente de
la verdad de la interfaz** y forma parte de esta fase:

1. **Se aprueba antes de codificar** — mismo estándar de firmas que el resto de las fases.
2. **Las guías de desarrollo (`05_desarrollo/`) lo implementan sin desviarse**: nombres de rutas, parámetros, códigos de respuesta y esquemas del código deben coincidir con el contrato.
3. **Detección de desvío (drift) como mecanismo de cierre:** al terminar la fase 1, la guía 4 abre el `/docs` generado por FastAPI **al lado** del contrato y los compara. Cualquier diferencia es un hallazgo: o el código corrige, o el contrato se versiona y se aprueba de nuevo — nunca cambia en silencio.
4. Mientras no exista backend, el contrato permite **mockear** la API (importarlo en Swagger Editor o Postman) y adelantar trabajo del frontend.

## Consecuencias

**Positivas**
- La interfaz se critica en su momento: "¿por qué 422 y no 400 para una familia fuera del enum?" se discute sobre el contrato, no sobre el código ya escrito.
- La SPA (ADR-004) puede tiparse y hasta construirse contra el contrato sin esperar al backend.
- La evaluación de las guías es objetiva: ¿el endpoint cumple el contrato, sí o no?

**Negativas (honestas)**
- Sin generación automática, el contrato y el código pueden divergir; se mitiga con la comparación `/docs` ≈ contrato (y como evolución: pruebas de contrato automáticas en la fase de pruebas).
- Un documento más que mantener y versionar.

## Para conversar en clase

1. El código y el contrato discrepan: ¿quién manda y por qué? ¿Qué harían en un equipo real con clientes ya integrados?
2. Importen `contrato_api.yaml` en Swagger Editor **antes** de que exista código: ¿qué se puede hacer con una API que solo existe en papel?
3. ¿Qué código de respuesta corresponde para "familia fuera de la lista" (422) vs "producto inexistente" (404)? ¿Quién produce cada uno — la validación de esquema o la regla de negocio — y por qué se distinguen?
