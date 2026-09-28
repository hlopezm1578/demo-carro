# API Coverage — Phase 1

**Scan date:** 2026-09-28
**Scan result:** `detected: true` — both signals are the project's own two-tier API, not an external service.

No external API integration: la fase 1 levanta la tienda de dos tiers propia (SPA React que consume SU
propia API FastAPI en capas y su contrato OpenAPI interno `contrato_api.yaml`); el único "servicio" del
ciclo que vive fuera del repo es SQLite (stdlib local). Webpay (Transbank sandbox) llega en la fase 3 y
Google Gemini en la fase 4 — ninguna credencial, SDK externo ni endpoint de terceros se integra en esta
fase, por lo que no se requiere COVERAGE de APIs externas.
