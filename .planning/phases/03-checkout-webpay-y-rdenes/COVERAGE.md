# API Coverage — Webpay Plus REST (Transbank SDK Python 6.1.0)

> Full coverage by default. Opt-outs are explicit, reasoned decisions.
>
> **Scan date:** 2026-09-30 (planner, plan-time)
> **Scan result:** `detected: true` — la fase 3 integra Webpay Plus REST en ambiente de
> integración vía el SDK oficial `transbank-sdk` 6.1.0 (superficie verificada en fuente:
> `transaction.py` con create/commit/status/refund — ver 03-RESEARCH.md Pattern 1 y Sources).
> El detector fires sobre "Webpay Plus REST" + "SDK Python" en el scope de la fase.

| capability | decision | reason |
|---|---|---|
| create (iniciar transacción) | INTEGRATE | |
| commit (confirmar transacción) | INTEGRATE | |
| status (consultar sin confirmar) | OPT-OUT | not needed yet — la fase 3 discrimina los flujos del retorno por presencia de params y el plugin oficial NO llama status en los flujos de retorno (03-RESEARCH Pattern 3); la consulta sin confirmar llega con la gestión de órdenes huérfanas del panel admin (fase 4, ADMN-03). La guía puede mencionarla como nota educativa (ventana de 7 días) |
| refund (anular/reembolsar) | OPT-OUT | explicitly out of scope — ADMN-05 (refund desde el panel admin) está diferido a v1.x (REQUIREMENTS v2) |
| capture (captura diferida) | OPT-OUT | explicitly out of scope — "Webpay Mall / captura diferida" figura en Out of Scope de REQUIREMENTS.md (modalidades fuera del caso de la PYME) |

Notas de cobertura:

- **create + commit son el corazón de la fase** (PAY-01/PAY-03): create se enseña en guia-09
  (`iniciar_checkout`, D-34) y commit en `procesar_retorno` con el criterio oficial
  `response_code == 0 && status == AUTHORIZED` — ambos verificados runtime por el spike
  (plan 03-01) antes de documentarse.
- El 4° flujo del retorno (error de formulario) se maneja por la rama `token_ws`+`TBK_TOKEN`
  del discriminador (Pattern 3 del research, patrón del plugin oficial) sin llamada a la API —
  cubierto por diseño, no por capability adicional.
- Instalments / Mall / Oneclick no figuran: son productos distintos de Webpay Plus REST normal,
  fuera del alcance de la PYME (Out of Scope de REQUIREMENTS.md).
