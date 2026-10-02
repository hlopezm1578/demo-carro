# Demo Carro — Guía educativa e-commerce (body splash)

## What This Is

Segunda guía educativa del ciclo de vida del software (hermana de `demo-cine`): una tienda
de body splash para una PYME ficticia, construida como aplicación de dos tiers — SPA React
en el cliente + API FastAPI en el servidor con arquitectura en capas — que integra dos
servicios externos reales en modo de pruebas: Webpay (Transbank) para el pago online y
Groq para un asistente de venta con IA. La audiencia son alumnos que aprenden a
integrar servicios externos (credenciales, contratos, redirecciones, manejo de errores)
además del recorrido completo de documentación por fases.

## Core Value

La guía documenta el ciclo de vida completo (necesidad del cliente → requerimientos →
diseño → arquitectura con ADRs → desarrollo guiado → pruebas → despliegue → mantenimiento)
y, siguiéndola en orden, la aplicación queda construida y operativa: tienda con catálogo,
carro, checkout Webpay sandbox, cuentas JWT y panel admin, más asistente IA sobre el
catálogo real.

## Requirements

### Validated

- ✓ Aplicación de dos tiers separados: SPA React que consume API FastAPI (sin renderizado de plantillas en el servidor), backend organizado en capas — Phases 01-03 (verificado runtime en maura-uat)
- ✓ Recorrido de tienda completo: landing, catálogo, carro de compras, checkout con Webpay en ambiente de integración, órdenes y cuentas de cliente (JWT) con historial — Phase 03 (UAT delegado 3/3, Gran verificación final 12/12 runtime)
- ✓ Pago operativo en ambiente de integración de Transbank con credenciales públicas sin registro, incluyendo la vuelta de la redirección de Webpay a la SPA React — Phase 03 (4 flujos runtime reales: aprobado/anulado/timeout/F5)
- ✓ Panel de administración para la dueña de la PYME: productos, stock y pedidos — Phase 04 (8/8 planes; máquina de estados de pedidos con cancelación admin, ADRs 015-017)
- ✓ Asistente de venta (burbuja de chat) que recomienda productos del catálogo real usando Groq vía el SDK oficial `groq` (ADR-018), con la API key solo en el backend — Phase 04 (UAT 5/5: happy path 200 real, 503 sin key, grep del build limpio)
- ✓ Guía educativa completa estilo demo-cine: fases documentadas con ADRs, contrato de API y guías de desarrollo paso a paso, con trazabilidad entre fases — Phase 05 (ciclo cerrado: 18 guías, 20 ADRs, docs 06/07/08, cadena Siguiente completa; GUIDE-01 Complete)
- ✓ Despliegue free tier enseñado de punta a punta: Vercel Hobby + Render Free con triple congelado de URLs/CORS y seed idempotente contra disco efímero — Phase 05 (ADRs 019/020, guías 16-18; cierre documental D-73 aceptado por el usuario)

### Active

*(none — v2.25.0 shipped 2026-10-02; los ítems v2/v2+ quedaron diferidos en el archivo del milestone y en docs/08_mantenimiento.md; el próximo milestone parte con /gsd:new-milestone)*

### Out of Scope

- Stripe como pasarela — no permite comercios registrados en Chile (verificado contra stripe.com/global)
- SDKs de Gemini (`google-generativeai`, `google-genai`) — retirados del proyecto el 2026-10-01: Google exige billing — ADR-018
- Pagos reales en producción — la guía opera solo en sandbox/integración con credenciales públicas
- Mercado Pago, Flow o Khipu como pasarelas alternativas — requisitos de sandbox no verificables contra fuente primaria en la exploración
- Renderizado de plantillas en el servidor (MVC clásico) — el objetivo pedagógico exige SPA + API separadas

## Context

**Estado tras v2.25.0 (2026-10-02):** guía completa y cerrada — 18 guías de desarrollo,
20 ADRs, contrato API 0.4.0, docs del ciclo 01-08 con las 8 filas del recorrido en ✅ Listo;
5 fases GSD ejecutadas en 5 días (284 commits, ~21.900 LOC en `docs/`). El repositorio es
guide-only (D-17/ADR-008): la aplicación vive en las guías; el taller de verificación delegada
existe en `D:/Repos/maura-uat` (hermanado a las guías, con servers y fixes espejados).
Deuda conocida: 7 findings del code review de la fase 5 con disposition deliberado
(4 warnings + 3 infos, `05-REVIEW-DISPOSITION.md`); WR-02 y WR-04 tocan bloques que el
alumno copia y merecen un fix menor en una próxima pasada de contenido.

- Proyecto hermano de `demo-cine` (primera guía del ciclo); replica su formato: fases
  documentadas con ADRs, contrato de API y guías de desarrollo paso a paso.
- Exploración previa (2026-09-28) con hallazgos verificados contra fuente primaria:
  - **Transbank**: credenciales de integración públicas sin registro (código de comercio
    597055555532, API key pública compartida) contra `webpay3gint.transbank.cl`; los SDK
    vienen preconfigurados. El valor "tbk-qa" que circula en búsquedas es falso. SDK
    oficial Python `transbank-sdk` mantenido (6.1.0, publicada 2025-06-24).
  - **Groq (proveedor de IA desde el rework 2026-10-01, ADR-018 — reemplazó a Gemini
    tras el 402/billing de Google)**: SDK oficial `groq` 1.7.0 (pin `>=1.7,<2`,
    probe punta a punta 2026-10-01); API key gratis desde console.groq.com sin tarjeta
    de crédito; free tier con límites públicos (30 RPM / 1.000 RPD para
    `openai/gpt-oss-120b`, a la fecha). Patrón quickstart: `pip install groq`,
    `from groq import Groq`, `Groq(api_key=...)` con env var `GROQ_API_KEY`.
- Pendientes que el desarrollo de la guía debe resolver (no tratar como hechos):
  - Patrón de retorno Webpay → SPA React (la redirección del navegador cae fuera del
    router de React) — resolver con un spike antes de escribir la guía de desarrollo.
  - Límites RPM/RPD del free tier del proveedor de IA — CERRADO (D-68): Groq los
    publica — 30 RPM / 1.000 RPD para `openai/gpt-oss-120b`
    (console.groq.com/docs/rate-limits, a la fecha).
  - Nombre del cliente ficticio de la PYME (MAURA) y plataforma de despliegue gratuita
    para los dos tiers — CERRADO: ADR-019 fija Vercel Hobby + Render Free (D-69) con el
    triple BACKEND_URL/CORS_ORIGINS/VITE_API_URL congelado; las guías 16-18 enseñan el
    deploy y la Gran verificación final en las cuentas del alumno (D-73).

## Constraints

- **Tech stack**: React (SPA) + FastAPI (Python) con backend en capas — decisión pedagógica de la exploración; dos tiers estrictamente separados
- **Pago**: Transbank Webpay Plus en ambiente de integración (sandbox) — pasarela real en modo de pruebas; Stripe descartado por no operar en Chile
- **IA**: Groq vía SDK oficial `groq` (rework 2026-10-01, ADR-018) — la API key vive solo en el backend (variable de entorno), nunca en código del frontend
- **Costo**: servicios externos en tier gratuito/sandbox (Webpay integración, Groq free tier) — es material educativo, sin gasto

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Formato: guía educativa del ciclo de vida completo, hermana de demo-cine | Continuidad pedagógica del ciclo de guías | — Phase 01 shipped (guías 1-4, ADRs 001-008, contrato; UAT 4/4) — Phase 02 shipped (guías 5-8, ADRs 009-011, contrato 0.2.0; UAT delegado 4/4 con Gran verificación 12/12) |
| Arquitectura: en capas + dos tiers cliente-servidor separados | Objetivo pedagógico: integración real entre frontend y backend | — Phase 01 shipped (enseñada en guías 1-4 y verificada runtime) — Phase 02 shipped (capas de cuentas + stores cliente verificados runtime) |
| Frontend React (SPA), backend FastAPI (Python) | Decisión de la exploración 2026-09-28 | — Phase 01 shipped (scaffold + API verificados en maura-uat) — Phase 02 shipped (JWT/Argon2 + Zustand persist verificados runtime en maura-uat) |
| Repositorio guide-only (D-17): el código vive dentro de las guías, no en el repo | Corrección de alcance del usuario a mitad de la fase 1: el producto es la guía documental | — Phase 01 shipped (ADR-008; UAT delegado al agente en maura-uat) — Phase 02 cerró igual (UAT delegado construyó las guías 5-08 en el taller y las verificó 12/12) |
| Pago: Transbank Webpay Plus en sandbox | Pasarela real chilena con credenciales públicas sin registro; Stripe no opera en Chile | — Phase 03 shipped (spike del retorno con evidencia runtime, contrato 0.3.0, ADRs 012-014, guías 09-11; UAT delegado 3/3 con Gran verificación 12/12 runtime contra Webpay integración) |
| IA: asistente de venta en chat (recomendador sobre catálogo, mini-RAG) con Groq (rework ADR-018, 2026-10-01) | Integración de servicio externo con contratos y manejo de errores; API key solo backend | — Phase 04 shipped (guías 14-15, UAT 5/5 con 200 real y 503 degradado; contrato 0.4.0 agnóstico del proveedor D-66) |
| Alcance funcional completo con panel admin | La PYME ficticia necesita gestionar productos, stock y pedidos | — Phase 04 shipped (guías 12-13 + cierre; ADMN-01..04 Complete) |
| Despliegue: Vercel Hobby (SPA) + Render Free (API), una plataforma por tier (D-69, ADR-019) | Free sin tarjeta con URLs HTTPS públicas; PYTHON_VERSION 3.12 fijo; SQLite efímero + seed idempotente (ADR-020) como trade-off declarado | — Phase 05 shipped (guías 16-18 + Gran verificación final de la serie; D-73 writing-only: la corrida runtime es del alumno, cierre documental aceptado 2026-10-02) |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-10-02 after v2.25.0 milestone*
