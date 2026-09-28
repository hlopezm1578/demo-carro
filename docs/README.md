# Proyecto Maura — Documentos del ciclo de vida

> **Guía:** Demo Carro — ciclo de vida del software en una tienda de body splash
> (segunda guía de la serie, hermana de **demo-cine**)
> **Producto:** Maura · Body Splash — tienda online de una PYME chilena de
> perfumería artesanal
> **Método:** el proyecto avanza **paso a paso por el ciclo de vida del software**,
> un documento por fase. Cada fase usa la anterior como insumo y la referencia
> de forma trazable. A diferencia de demo-cine, aquí los documentos se escriben
> **por fase de construcción**: el estado de la tabla avanza a medida que la
> aplicación se construye de verdad.

| # | Fase del ciclo de vida | Documento | Estado |
|---|---|---|---|
| 1 | Necesidad del cliente | `01_necesidad_del_cliente.md` | ✅ Listo |
| 2 | Análisis de requerimientos | `02_requerimientos.md` | ✅ Listo |
| 3 | Diseño (modelo de datos, procesos, pantallas) | `03_diseno.md` | ✅ Listo |
| 4 | Arquitectura y decisiones (ADRs) + contrato API-first | `04_arquitectura/` (documento + 7 ADRs + `contrato_api.yaml`) | ✅ Listo |
| 5 | Desarrollo | `05_desarrollo/` (guías paso a paso con razonamiento y código) | 🚧 Parcial (guías 1–4) |
| 6 | Pruebas | `06_pruebas.md` | ⏳ Pendiente |
| 7 | Despliegue | `07_despliegue.md` | ⏳ Pendiente |
| 8 | Mantenimiento | `08_mantenimiento.md` | ⏳ Pendiente |

**Regla del proyecto:** ninguna fase se escribe sin aprobar la anterior. Así se
vive el ciclo: la necesidad aprueba la clienta, los requerimientos los firma el
analista, el diseño se valida contra los requerimientos, y así hasta producción.
