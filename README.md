# 🧴 Maura — un proyecto para enseñar desarrollo de software

**Este repositorio es un proyecto educativo.** No es un producto comercial: es el
recorrido **completo y documentado** del ciclo de vida del software, construido
sobre una aplicación pequeña pero real. Es la **segunda guía de la serie**,
hermana de **demo-cine**, pensada para estudiantes de diseño de sistemas y
arquitectura de software que quieren ver el proceso entero — desde la necesidad
de una clienta hasta la publicación en la nube — y que además aprenden a
**integrar servicios externos reales en modo de pruebas**: un pago online
(Webpay en ambiente de integración) y un asistente de venta con IA
(Groq). Todas las decisiones a la vista.

## La aplicación

**Maura · Body Splash** es la tienda online de una PYME chilena ficticia de
perfumería artesanal — "Frescura que te acompaña". La dueña es Maura, que hace
body splash a mano en lotes pequeños. La tienda publica una landing con la
identidad de la marca, un catálogo organizado en 4 familias aromáticas (Cítricas,
Florales, Frutales y Dulces) con fichas completas de cada aroma, y —conforme
avanzan las fases de la guía— carro de compras, checkout con Webpay Plus en
ambiente de integración, cuentas de clientas (JWT), panel de administración y
una asesora de venta con IA.

Es pequeña a propósito: se lee completa en una sentada. Pero toca todo lo que
importa: dos tiers estrictamente separados (SPA + API), contrato de API
OpenAPI, autenticación, pasarela de pago real en sandbox, integración de IA y
despliegue gratuito.

## El enfoque: una fase a la vez, nada aparece de la nada

Cada fase produce documentos que la siguiente usa como insumo, con
**trazabilidad completa**: cada requerimiento nace de una petición de la
clienta; cada decisión técnica nace de un documento. Ninguna fase se escribe
sin aprobar la anterior.

| # | Fase | Documento | Estado |
|---|---|---|---|
| 1 | Necesidad del cliente | [`docs/01_necesidad_del_cliente.md`](docs/01_necesidad_del_cliente.md) | ✅ Listo |
| 2 | Análisis de requerimientos | [`docs/02_requerimientos.md`](docs/02_requerimientos.md) | ✅ Listo |
| 3 | Diseño (datos, procesos, pantallas) | [`docs/03_diseno.md`](docs/03_diseno.md) | ✅ Listo |
| 4 | Arquitectura + 18 ADRs + contrato OpenAPI | [`docs/04_arquitectura/`](docs/04_arquitectura) | ✅ Listo |
| 5 | Desarrollo (guías 1–15 paso a paso) | [`05_desarrollo/`](docs/05_desarrollo) | 🚧 Parcial (guías 1-15 listas; continúa en fases 5+) |
| 6 | Pruebas | `06_pruebas.md` | ⏳ Pendiente |
| 7 | Despliegue | `07_despliegue.md` | ⏳ Pendiente |
| 8 | Mantenimiento | `08_mantenimiento.md` | ⏳ Pendiente |

A diferencia de demo-cine, aquí los documentos se escriben **por fase de
construcción**: el estado de la tabla avanza a medida que la aplicación se
construye de verdad, fase por fase. El índice detallado del ciclo vive en
[`docs/README.md`](docs/README.md).

## Qué hace especial a este material

- **ADRs con consecuencias honestas**: las 18 decisiones de arquitectura
  (`docs/04_arquitectura/adr/`) registran contexto, opciones descartadas,
  ventajas **y desventajas**, más preguntas para discutir en clase.
- **API-first de verdad**: el contrato OpenAPI
  ([`contrato_api.yaml`](docs/04_arquitectura/contrato_api.yaml)) se diseñó y
  aprobó **antes** del código; el desarrollo debe cumplirlo y la divergencia se
  detecta comparándolo con la documentación generada (`/docs`).
- **Guías de desarrollo "senior → junior"** (`docs/05_desarrollo/`): el
  razonamiento de un desarrollador experimentado narrado paso a paso, bloques
  de código para copiar y ✅ verificaciones al final de cada paso.
- **Dos tiers estrictamente separados como decisión pedagógica**: la SPA React
  y la API FastAPI se construyen por separado y conversan únicamente por su
  contrato — la integración entre tiers ES la materia de la guía.

## Stack y cómo construir la aplicación

React 19 + TypeScript + Vite 8 + Tailwind CSS 4 (SPA) · FastAPI + SQLAlchemy
2.1 + SQLite (API en capas con cuentas JWT) · Zustand como estado de cliente
(sesión y carro persistentes) · uv como gestor del proyecto Python · Webpay
Plus en ambiente de integración: pago sandbox operativo, órdenes con snapshot
y stock transaccional · panel de administración: la dueña gestiona productos,
stock, pedidos y métricas tras su guard por rol · Groq: la asesora
de aromas recomienda del catálogo real, con la API key solo en el backend.

El código completo del proyecto vive **narrado en las guías**: este repositorio
contiene solo la guía. Siguiendo las guías de [`docs/05_desarrollo/`](docs/05_desarrollo)
en orden — copiando los bloques y pasando cada ✅ verificación en tu máquina —
la aplicación queda construida y probada de punta a punta. Ese recorrido guiado
es la experiencia diseñada para el aula.

## Uso en clases

Pensado para módulos de taller de diseño de sistemas y arquitectura de
software: los documentos de las fases 1–3 sirven como modelos de entregables,
los ADRs como base de discusión, las guías como laboratorio guiado — y las
fases de integración (pago sandbox, IA) muestran en vivo el trabajo con
credenciales, contratos y redirecciones de servicios externos reales.

> Repo mantenido con fines exclusivamente educativos. Maura, su tienda y su
> historia son ficticias; cualquier parecido con una perfumadora real es puro
> cariño por los aromas frescos.
