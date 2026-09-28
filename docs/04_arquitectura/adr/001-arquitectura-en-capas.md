# ADR-001 — Arquitectura en capas (routers → services → repositories → models)

- **Estado:** Aceptada
- **Fecha:** 2026-09-28
- **Resuelve:** cómo organizar el código del tier servidor que implementa el diseño (fase 3)

## Contexto

La API FastAPI sirve el catálogo a la SPA (procesos 1.0–3.0 del diseño §3.3–3.5)
y un script interno siembra los datos demo (proceso 4.0, §3.6). A diferencia de
demo-cine —donde la misma lógica alimentaba dos caras, páginas HTML y JSON—
aquí el consumidor es uno: la SPA. Pero la lección se mantiene: si todo vive
mezclado en un `main.py`, cada cambio toca todo y es imposible razonar dónde
debe ir cada regla. El DFD del diseño (almacén D1, procesos 1.0–4.0) ya sugiere
la separación; este ADR la hace obligatoria en el código.

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| **A. Un solo archivo** con todo | Rápido de arrancar; se lee entero | HTTP, validaciones y SQL pegados; imposible de testear por partes; crece mal |
| **B. Capas: routers → services → repositories → models** | Una responsabilidad por capa; testeable; el endpoint y el seed comparten lógica | Más archivos y "saltos" para seguir un flujo |
| **C. Framework MVC completo** (Django) | Estructura impuesta, admin incluido | Demasiado peso para 3 endpoints; esconde justo lo que la guía quiere mostrar |

## Decisión

**Opción B**, con una regla por capa:

```
routers/       → reciben la petición, validan la forma (Pydantic), eligen la respuesta JSON
services/      → lógica de negocio: los procesos 1.0–3.0 del DFD (las reglas RN)
repositories/  → solo acceso a datos: el almacén D1 del DFD
models/        → tablas y relaciones: la entidad PRODUCTO del diseño §2
```

**Regla de dependencia:** una capa solo habla con la capa inmediatamente
inferior, y la conexión se recibe **solo por inyección** (`Depends` de
FastAPI): un router jamás importa SQLAlchemy (la `Session` inyectada llega
re-exportada desde `app.database`); un repositorio jamás decide si un producto
inactivo se muestra — eso lo decide el servicio —; un servicio jamás conoce
HTTP.

## Consecuencias

**Positivas**
- El mismo servicio alimenta el endpoint del catálogo y el script de siembra: la lógica existe una sola vez.
- La lógica se prueba sin navegador ni servidor (fase de pruebas).
- El alumno ubica cualquier regla preguntando "¿qué capa es?".

**Negativas (honestas)**
- Para 3 endpoints, el enjambre de carpetas es **overkill** y hay que decirlo en voz alta: el costo de las capas se paga cuando el sistema crece (carro, cuentas y pedidos llegan en las etapas 2 y 3) o cuando hay que testear.
- Seguir un flujo completo requiere saltar entre archivos.

## Para conversar en clase

1. ¿En qué capa validarías "la familia debe ser una de las cuatro" (RN-01)? ¿Y "el precio es un entero"? (pista: no es la misma capa).
2. ¿Qué pasaría si la regla "los productos inactivos no se muestran" viviera solo en el repositorio y llega el panel de administración (etapa 4), que SÍ debe verlos?
3. Comparen con el ADR-001 de demo-cine: allí la lógica alimentaba páginas HTML y JSON; aquí el consumidor es solo la SPA. ¿Qué cambió de aquella decisión y qué se mantuvo?
