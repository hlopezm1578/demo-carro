# Demo Carro — Guía educativa e-commerce (body splash)

## What This Is

Segunda guía educativa del ciclo de vida del software (hermana de `demo-cine`): una tienda
de body splash para una PYME ficticia, construida como aplicación de dos tiers — SPA React
en el cliente + API FastAPI en el servidor con arquitectura en capas — que integra dos
servicios externos reales en modo de pruebas: Webpay (Transbank) para el pago online y
Google Gemini para un asistente de venta con IA. La audiencia son alumnos que aprenden a
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

### Active

- [ ] Guía educativa completa estilo demo-cine: fases documentadas con ADRs, contrato de API y guías de desarrollo paso a paso, con trazabilidad entre fases
- [ ] Panel de administración para la dueña de la PYME: productos, stock y pedidos
- [ ] Asistente de venta (burbuja de chat) que recomienda productos del catálogo real usando Gemini vía el SDK oficial `google-genai`, con la API key solo en el backend (variable de entorno)

### Out of Scope

- Stripe como pasarela — no permite comercios registrados en Chile (verificado contra stripe.com/global)
- SDK `google-generativeai` — deprecado (soporte terminado 2025-11-30); la guía usa `google-genai`
- Pagos reales en producción — la guía opera solo en sandbox/integración con credenciales públicas
- Mercado Pago, Flow o Khipu como pasarelas alternativas — requisitos de sandbox no verificables contra fuente primaria en la exploración
- Renderizado de plantillas en el servidor (MVC clásico) — el objetivo pedagógico exige SPA + API separadas

## Context

- Proyecto hermano de `demo-cine` (primera guía del ciclo); replica su formato: fases
  documentadas con ADRs, contrato de API y guías de desarrollo paso a paso.
- Exploración previa (2026-09-28) con hallazgos verificados contra fuente primaria:
  - **Transbank**: credenciales de integración públicas sin registro (código de comercio
    597055555532, API key pública compartida) contra `webpay3gint.transbank.cl`; los SDK
    vienen preconfigurados. El valor "tbk-qa" que circula en búsquedas es falso. SDK
    oficial Python `transbank-sdk` mantenido (6.1.0, publicada 2025-06-24).
  - **Gemini**: SDK oficial vigente `google-genai` (2.25.0, publicada 2026-09-22, activo);
    API key gratis desde Google AI Studio sin tarjeta de crédito; el billing recién se
    exige para el tier pago. Patrón quickstart: `pip install -U google-genai`,
    `from google import genai`, `genai.Client(api_key=...)` o env var `GEMINI_API_KEY`.
- Pendientes que el desarrollo de la guía debe resolver (no tratar como hechos):
  - Patrón de retorno Webpay → SPA React (la redirección del navegador cae fuera del
    router de React) — resolver con un spike antes de escribir la guía de desarrollo.
  - Límites RPM/RPD del free tier de Gemini — confirmar logueado en
    aistudio.google.com/rate-limit antes de fijar el material.
  - Nombre del cliente ficticio de la PYME y plataforma de despliegue gratuita para los
    dos tiers (frontend estático + API).

## Constraints

- **Tech stack**: React (SPA) + FastAPI (Python) con backend en capas — decisión pedagógica de la exploración; dos tiers estrictamente separados
- **Pago**: Transbank Webpay Plus en ambiente de integración (sandbox) — pasarela real en modo de pruebas; Stripe descartado por no operar en Chile
- **IA**: Google Gemini vía SDK oficial `google-genai` — la API key vive solo en el backend (variable de entorno), nunca en código del frontend
- **Costo**: servicios externos en tier gratuito/sandbox (Webpay integración, Gemini free tier) — es material educativo, sin gasto

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Formato: guía educativa del ciclo de vida completo, hermana de demo-cine | Continuidad pedagógica del ciclo de guías | — Phase 01 shipped (guías 1-4, ADRs 001-008, contrato; UAT 4/4) — Phase 02 shipped (guías 5-8, ADRs 009-011, contrato 0.2.0; UAT delegado 4/4 con Gran verificación 12/12) |
| Arquitectura: en capas + dos tiers cliente-servidor separados | Objetivo pedagógico: integración real entre frontend y backend | — Phase 01 shipped (enseñada en guías 1-4 y verificada runtime) — Phase 02 shipped (capas de cuentas + stores cliente verificados runtime) |
| Frontend React (SPA), backend FastAPI (Python) | Decisión de la exploración 2026-09-28 | — Phase 01 shipped (scaffold + API verificados en maura-uat) — Phase 02 shipped (JWT/Argon2 + Zustand persist verificados runtime en maura-uat) |
| Repositorio guide-only (D-17): el código vive dentro de las guías, no en el repo | Corrección de alcance del usuario a mitad de la fase 1: el producto es la guía documental | — Phase 01 shipped (ADR-008; UAT delegado al agente en maura-uat) — Phase 02 cerró igual (UAT delegado construyó las guías 5-08 en el taller y las verificó 12/12) |
| Pago: Transbank Webpay Plus en sandbox | Pasarela real chilena con credenciales públicas sin registro; Stripe no opera en Chile | — Phase 03 shipped (spike del retorno con evidencia runtime, contrato 0.3.0, ADRs 012-014, guías 09-11; UAT delegado 3/3 con Gran verificación 12/12 runtime contra Webpay integración) |
| IA: asistente de venta en chat (recomendador sobre catálogo, mini-RAG) con Gemini | Integración de servicio externo con contratos y manejo de errores; API key solo backend | — Pending |
| Alcance funcional completo con panel admin | La PYME ficticia necesita gestionar productos, stock y pedidos | — Pending |

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
*Last updated: 2026-09-30 after Phase 03*
