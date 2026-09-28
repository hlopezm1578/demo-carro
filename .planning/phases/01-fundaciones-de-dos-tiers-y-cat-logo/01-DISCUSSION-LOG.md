# Phase 1: Fundaciones de dos tiers y catálogo - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-28
**Phase:** 1-Fundaciones de dos tiers y catálogo
**Areas discussed:** Identidad de la PYME, Catálogo demo y seed, Toolchain del alumno, Convenciones de la guía

---

## Identidad de la PYME

### ¿Cómo se llama la tienda ficticia de la PYME?

| Option | Description | Selected |
|--------|-------------|----------|
| Maura (Recomendada) | Marca eponima de la dueña, estilo emprendimiento chileno real ("Maura · Body Splash"); resuelve también el nombre de la dueña | ✓ |
| Esencia Fresca | Nombre descriptivo y juvenil, tipo tienda de mall; la dueña quedaría separada | |
| Rocío Botánico | Marca natural/botánica, delicada, con líneas por notas botánicas | |

**User's choice:** Maura (Recomendada)
**Notes:** Pendiente explícito de PROJECT.md ("Nombre del cliente ficticio de la PYME") resuelto.

### ¿Cuánto desarrollo narrativo tiene la persona de Maura, la dueña?

| Option | Description | Selected |
|--------|-------------|----------|
| Persona breve (Recomendada) | 2-3 frases fijadas en la guía: quién es, qué vende, por qué necesita la tienda online | ✓ |
| Persona completa | Historia tipo caso de estudio (edad, cómo empezó, metas) | |
| Solo el nombre | La guía no desarrolla su historia; narrativa más abstracta | |

**User's choice:** Persona breve (Recomendada)

### ¿Qué dirección visual tiene la marca Maura?

| Option | Description | Selected |
|--------|-------------|----------|
| Fresco y luminoso (Rec.) | Pasteles cítricos, mucho blanco, tipografía redondeada | ✓ |
| Natural botánico | Verdes suaves, tonos tierra, estética de herbolario | |
| Elegante minimal | Base neutra con acento dorado, serif elegante | |

**User's choice:** Fresco y luminoso (Rec.)

### ¿Qué tagline lleva la landing de Maura en el hero?

| Option | Description | Selected |
|--------|-------------|----------|
| Frescura que te acompaña (Rec.) | Directo, en la línea fresco-luminosa | ✓ |
| Aromas para tu día a día | Más cercano y conversacional | |
| Lo define ui-phase | Sin tagline ahora; el copy se decide con el contrato de UI | |

**User's choice:** Frescura que te acompaña (Rec.)

---

## Catálogo demo y seed

### ¿Qué familias aromáticas componen el catálogo de Maura?

| Option | Description | Selected |
|--------|-------------|----------|
| 4 familias (Recomendada) | Cítricas, Florales, Frutales, Dulces (gourmand) | ✓ |
| 3 familias | Cítricas, Florales, Dulces | |
| 5 familias | Las 4 anteriores más Herbales/Frescas | |

**User's choice:** 4 familias (Recomendada)

### ¿Cuántos productos sembramos en el seed demo?

| Option | Description | Selected |
|--------|-------------|----------|
| 12 SKU (Recomendado) | 4 familias × 3 productos | ✓ |
| 8 SKU | 2 por familia; grilla muy vacía | |
| 16-20 SKU | 4-5 por familia; seed largo para copy-paste | |

**User's choice:** 12 SKU (Recomendado)

### ¿Qué rango de precios CLP tienen los productos del seed?

| Option | Description | Selected |
|--------|-------------|----------|
| $6.990–$12.990 (Rec.) | Realista del body splash chileno de perfumería masiva | ✓ |
| $4.990–$9.990 | Económico/entrada | |
| $9.990–$19.990 | Premium/boutique | |

**User's choice:** $6.990–$12.990 (Rec.)

### ¿De dónde salen las imágenes de los 12 productos del seed?

| Option | Description | Selected |
|--------|-------------|----------|
| Placeholders por familia (Rec.) | Degradado/tono por familia + nombre; 100% reproducible sin internet | |
| Fotos stock por URL | Fotos reales de bancos gratuitos (Unsplash/Pexels) referenciadas por URL | ✓ |
| Sin imágenes | Solo tipografía y color de familia | |

**User's choice:** Fotos stock por URL
**Notes:** El usuario prefirió fotos reales por sobre la opción recomendada (placeholders).

### Follow-up: ¿las fotos stock van descargadas al repo o hotlinkeadas por URL?

| Option | Description | Selected |
|--------|-------------|----------|
| Descargar al repo (Rec.) | Guía incluye descarga de las 12 fotos a frontend/public/products/; seed apunta a rutas locales | ✓ |
| Hotlink directo | Seed con URLs directas; riesgo de imágenes quebradas con el tiempo | |

**User's choice:** Descargar al repo (Rec.)

---

## Toolchain del alumno

### ¿El frontend de la guía va en TypeScript o JavaScript?

| Option | Description | Selected |
|--------|-------------|----------|
| TypeScript (Recomendado) | Default del template react-ts de Vite; contrato API tipado que espeja los schemas Pydantic | ✓ |
| JavaScript | Template react plano; menos fricción cognitiva, sin red de tipos | |

**User's choice:** TypeScript (Recomendado)

### ¿La guía maneja las dependencias de Python con uv o pip+venv?

| Option | Description | Selected |
|--------|-------------|----------|
| uv (Recomendado) | Lo que enseña la doc oficial de FastAPI; rápido, con lockfile | ✓ |
| pip + venv | El clásico; cero herramientas nuevas, pasos manuales de activación | |

**User's choice:** uv (Recomendado)

### ¿El proyecto vive en un monorepo (backend/ + frontend/) o en dos repos separados?

| Option | Description | Selected |
|--------|-------------|----------|
| Monorepo (Recomendado) | Un repo con backend/ y frontend/, como propone la investigación | ✓ |
| Dos repos | maura-api + maura-web; duplica setup para el alumno | |

**User's choice:** Monorepo (Recomendado)

### ¿Qué terminal asume la guía para los comandos del alumno?

| Option | Description | Selected |
|--------|-------------|----------|
| Agnósticos (Recomendado) | Todo vía npm scripts / uv run; funciona en PowerShell, cmd y Git Bash | ✓ |
| Git Bash estándar | Guía asume Git Bash/WSL e incluye su instalación | |
| PowerShell | Terminal de referencia para Windows; rompe en macOS/Linux | |

**User's choice:** Agnósticos (Recomendado)

---

## Convenciones de la guía

### ¿La estructura de docs/ replica a demo-cine o se organiza por fase?

| Option | Description | Selected |
|--------|-------------|----------|
| Réplica demo-cine (Rec.) | Mismo layout 01-08 con 04_arquitectura/adr + contrato y 05_desarrollo/guia-NN; docs crecen por fase GSD | ✓ |
| Carpetas por fase | docs/fase-01/… refleja el roadmap pero rompe la numeración del ciclo | |
| Estructura nueva | Definir layout propio sin atarse a demo-cine | |

**User's choice:** Réplica demo-cine (Rec.)

### ¿Qué documentos del ciclo de vida escribe la fase 1?

| Option | Description | Selected |
|--------|-------------|----------|
| Todo lo fundacional (Rec.) | Fase 1 escribe 01_necesidad, 02_requerimientos, 03_diseno, 04_arquitectura (ADRs + contrato) y primeras guías de 05_desarrollo | ✓ |
| Solo técnico ahora | ADRs, contrato y guías; docs 01-03 al final (fase 5) como cierre retrospectivo | |

**User's choice:** Todo lo fundacional (Rec.)

### ¿Cómo se mantiene el contrato de API de la aplicación?

| Option | Description | Selected |
|--------|-------------|----------|
| YAML API-first (Rec.) | contrato_api.yaml se escribe ANTES del código (metodología demo-cine) | ✓ |
| Autogenerado | FastAPI genera OpenAPI vivo; snapshot exportado cada fase | |
| Híbrido con chequeo | YAML manual + test que compara contra /openapi.json | |

**User's choice:** YAML API-first (Rec.)

### ¿Las guías de desarrollo (05_desarrollo) se parten en sub-guías por hito o una por fase?

| Option | Description | Selected |
|--------|-------------|----------|
| Sub-guías por hito (Rec.) | Guías cortas por hito (backend, frontend, modelos+seed, catálogo); formato demo-cine | ✓ |
| Una guía por fase | Un documento largo por fase; difícil de retomar | |

**User's choice:** Sub-guías por hito (Rec.)

---

## Claude's Discretion

- Nombres, notas y descripciones de los 12 productos (dentro de las 4 familias).
- Selección concreta de fotos stock.
- Numeración y redacción de los ADRs fundacionales.
- Stock inicial y precios exactos dentro del rango fijado.
- Paleta Tailwind concreta bajo la dirección fresco-luminosa (la formaliza ui-phase).
- Rutas SPA, prefijos de API y detalles de carpetas (seguir investigación de arquitectura).

## Deferred Ideas

Ninguna — la discusión se mantuvo dentro del alcance de la fase.
