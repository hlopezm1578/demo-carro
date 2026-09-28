# ADR-004 — TypeScript en el frontend: el espejo manual de los schemas

- **Estado:** Aceptada
- **Fecha:** 2026-09-28
- **Resuelve:** cómo se tipa la frontera entre los dos tiers en el lado cliente (D-09)

## Contexto

El cable entre la SPA y el API transporta JSON sin tipos: nada le dice a React
que `precio` es un número ni que `familia` solo admite cuatro slugs sin
acentos (RN-01). El contrato (ADR-007) define los schemas Pydantic
(`ProductoResumen`, `ProductoDetalle`); el frontend necesita esos mismos tipos
en su idioma. D-09 fijó TypeScript para el frontend; falta decidir **cómo**
llegan esos tipos al código del cliente.

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| **A. JavaScript + JSDoc** | Menos sintaxis nueva que aprender; el scaffold `react` (JS) existe | Los tipos son sugerencias: nada los verifica al compilar; el "espejo" del contrato se vuelve documentación que nadie valida |
| **B. TypeScript con espejo manual** (interfaces escritas a mano en `src/types/api.ts`) | El compilador verifica; el alumno LEE el contrato y lo traduce a tipos | El espejo puede desincronizarse del contrato; curva de aprendizaje TS el primer día |
| **C. Generación automática** (openapi-typescript desde el contrato) | Drift imposible por construcción | Tooling extra que instalar y mantener; esconde justo el ejercicio pedagógico: leer un contrato OpenAPI y entender qué dice |

## Decisión

**Opción B.** El frontend usa el template `react-ts` de Vite (TypeScript ~6.0.2
— el pin del template; no subir a ciegas a la versión 7.x recién salida) y las
interfaces TS **espejan a mano** los schemas Pydantic del contrato en
`src/types/api.ts`: `ProductoResumen`, `ProductoDetalle` y
`Familia = "citricas" | "florales" | "frutales" | "dulces"`.

El espejo manual **es** el ejercicio pedagógico: al escribir
`familia: "citricas" | ...` el alumno acaba de leer RN-01 en dos idiomas — el
del contrato y el del compilador — y el error de mandar "Cítricas" con
acento por el cable se detecta antes de la ejecución.

## Consecuencias

**Positivas**
- Los errores de tipo (un `precio` que llegó como string, una familia mal escrita) estallan en compilación y no en la pantalla de la clienta.
- El contrato se lee dos veces — en YAML y en TypeScript — y queda fijado en la cabeza del alumno.
- Cero tooling de generación: una dependencia menos que instalar y explicar.

**Negativas (honestas)**
- El espejo manual puede desincronizarse del contrato. Mitigación: el catálogo tiene 2 schemas chicos, y la verificación final de la guía compara campo a campo la respuesta real (el JSON vivo de `/docs`) contra las interfaces.
- TypeScript añade una curva de aprendizaje el primer día del frontend — la guía la introduce con los 2 tipos del catálogo, no con genéricos.

## Para conversar en clase

1. Nombren un error que TypeScript atraparía aquí y JavaScript dejaría pasar. (pista: ¿qué pasa si alguien muestra la familia con el acento que no viaja por el cable, o trata `precio` como texto para concatenar?).
2. ¿A qué escala — cuántos endpoints, cuántos equipos consumiendo la API — justificarían la generación automática de tipos?
3. La interfaz TS y el schema Pydantic discrepan: ¿quién manda — el compilador, el contrato o el JSON que llega por el cable? ¿Cómo lo averiguarían sin adivinar?
