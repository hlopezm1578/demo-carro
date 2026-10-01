# Phase 5: Despliegue y cierre de la guía - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-01
**Phase:** 5-Despliegue y cierre de la guía
**Mode:** `--auto` — fully autonomous discuss (per user invocation `/gsd-discuss-phase 5 --auto`). No interactive AskUserQuestion was used; each area auto-selected the recommended option, logged inline below.
**Areas discussed:** Plataforma de despliegue, Persistencia en free tier, Cierre documental (docs 06/07/08), Spike de deploy antes de las guías

---

## Plataforma de despliegue

| Option | Description | Selected |
|--------|-------------|----------|
| Una plataforma por tier, validada por spike (candidata Vercel + Render) | Free y sin tarjeta, un solo camino por tier; el spike runtime corrobora con evidencia antes de firmar ADR/docs y puede sustituir con evidencia si hay bloqueo | ✓ |
| Fijar Vercel + Render sin spike | Firmar la plataforma en la discusión y redactar directo sobre la documentación oficial | |
| Enseñar dos opciones por tier | Menú de plataformas en la guía (p. ej. Vercel o Netlify; Render o Railway) | |

**[auto] Q: "¿Qué par de servicios free tier se enseña (frontend estático + API)?" → Selected: "Una plataforma por tier, free y sin tarjeta (candidata: Vercel + Render), validada por spike runtime antes de firmar docs" (recommended default)**
**Notes:** Resuelve el blocker heredado de STATE.md ("elegir plataforma de despliegue free tier"). El consenso de `.planning/research/STACK.md` ya apunta a static + Render free API. La disciplina del proyecto (D-38/D-41 desde el spike de Webpay) exige evidencia runtime antes de firmar — y el deploy congela `return_url`, riesgo real de plataforma. Registrada como **D-69**.

---

## Persistencia en free tier

| Option | Description | Selected |
|--------|-------------|----------|
| SQLite + seed idempotente, trade-off documentado | El disco efímero de Render free borra la BD en redeploys/spin-downs; el seed upsert (D-05/D-06/D-07) la restaura — lección explícita de estado efímero | ✓ |
| Migrar a PostgreSQL (Neon free tier) | Cambiar `DATABASE_URL` + psycopg 3; disco persistente real pero suma cuenta/servicio al alumno | |
| Ambos como variantes de la guía | Camino base SQLite + variante PostgreSQL documentada paso a paso | |

**[auto] Q: "¿SQLite con disco efímero o migración a PostgreSQL (Neon)?" → Selected: "SQLite + seed idempotente con el trade-off documentado; PostgreSQL como camino de crecimiento mencionado" (recommended default)**
**Notes:** STACK.md ya declara la opción aceptable para la guía base. Minimiza cuentas/servicios del alumno (misma vara de fricción cero que D-60/D-63 con la API key). Reversible: el swap futuro toca solo URL de conexión + driver. Registrada como **D-70**.

---

## Cierre documental (docs 06/07/08)

| Option | Description | Selected |
|--------|-------------|----------|
| Los tres documentos (06 + 07 + 08) | Cierran GUIDE-01 con el ciclo completo; filas 6-8 de docs/README y README raíz pasan a Listo | ✓ |
| Solo 07 (despliegue) | Escribir únicamente el doc de la fase; diferir 06 y 08 | |
| 07 + 08, diferir 06 | Cerrar despliegue y mantenimiento; dejar pruebas para otra instancia | |

**[auto] Q: "¿La fase 5 escribe 06_pruebas, 07_despliegue y 08_mantenimiento?" → Selected: "Los tres documentos — cierran GUIDE-01 con el ciclo completo" (recommended default)**
**Notes:** El SC3 de GUIDE-01 exige el ciclo completo palabra por palabra ("…pruebas → despliegue → mantenimiento") y esta es la última fase del roadmap — dejar alguno pendiente dejaría GUIDE-01 abierto. 06 sintetiza la estrategia de pruebas ya vivida; 07 es la decisión de despliegue; 08 cierra prospectivamente (v2, upgrade paths). Registrada como **D-71**.

---

## Spike de deploy antes de las guías

| Option | Description | Selected |
|--------|-------------|----------|
| Spike de deploy como primer plan | Deployar el taller maura-uat a los servicios reales, correr los 4 flujos, cronometrar spin-down, documentar gotchas — antes de ADR/doc 07/guías | ✓ |
| Redactar directo con research | Investigar la documentación oficial de las plataformas y escribir sin corroboración runtime previa | |
| Deployar como parte del UAT final | Correr el deploy recién en la verificación de fase, aceptando retrabajos si algo falla | |

**[auto] Q: "¿Se corrobora el deploy runtime en maura-uat antes de redactar?" → Selected: "Sí — spike de deploy como primer plan de la fase, patrón D-38/D-41" (recommended default)**
**Notes:** Réplica directa del patrón de la fase 3 (03-01-PLAN): la mecánica de retorno se firmó con evidencia runtime, no contra la doc sola. El deploy tiene riesgo real (plataforma, `return_url` congelado, CORS, fallback SPA, disco efímero) y el UAT final no debería descubrir nada nuevo. Registrada como **D-72**.

---

## Claude's Discretion

- Estructura y cantidad de guías 16+ (candidato: deploy API → deploy frontend + fallback → verificación de flujos + cierre), bajo D-16.
- Qué ADRs escribe la fase (candidatos: ADR-019 despliegue free tier, ADR-020 persistencia efímera) y sus títulos.
- Nombres de las env vars de producción (`return_url` base, CORS origins, `VITE_API_URL` o equivalente), validados por research.
- Si el contrato sube de versión (candidato: NO — D-66 fijó no bumpar sin churn real).
- Si docs/02 gana RF/RNF de despliegue o el tema vive en doc 07 (P1-P8 ya completas).
- Contenido exacto de 06_pruebas.md y 08_mantenimiento.md (con demo-cine como referencia de formato).
- Forma de la Gran verificación final de fase 5 (4 flujos desplegados, refresh sin 404, contrato ↔ /docs público, grep del build).
- Manejo operativo de las cuentas de plataforma del UAT delegado en maura-uat.

## Deferred Ideas

- PostgreSQL real en producción (Neon + psycopg) — camino de crecimiento mencionado, no implementado (D-70).
- CI/CD pipeline (GitHub Actions) — fuera de requisitos v1.
- Dominio propio + HTTPS custom — decisión de costo, fuera del alcance gratuito educativo.
- Monitoreo/observabilidad implementado — 08_mantenimiento.md lo cubre documentalmente.
