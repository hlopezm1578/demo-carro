# Phase 5: Despliegue y cierre de la guía - Context

**Gathered:** 2026-10-01
**Status:** Ready for planning
**Mode:** `--auto` (discusión autónoma — decisiones auto-seleccionadas con la opción recomendada; auditables en `05-DISCUSSION-LOG.md`)

<domain>
## Phase Boundary

**El repositorio sigue guide-only (D-17, fase 1): esta fase entrega DOCUMENTOS, no código.** La fase 5 — última del roadmap — hace dos cosas:

1. **Despliegue (DEPL-01, DEPL-02):** documenta y enseña el despliegue de los dos tiers en free tier — frontend estático + API con CORS de producción — con el `return_url` de Webpay congelado a la URL pública (por eso la fase va al final). El alumno deploya SU app siguiendo las guías nuevas (`guia-16+`); el código vive como bloques dentro de las guías, como toda la serie.
2. **Cierre del ciclo de vida documentado (GUIDE-01):** escribe los tres documentos que faltan del ciclo (`docs/06_pruebas.md`, `docs/07_despliegue.md`, `docs/08_mantenimiento.md` — filas 6-8 de `docs/README.md` y del README raíz, hoy ⏳ Pendiente), con trazabilidad de extremo a extremo: un alumno que sigue la guía en orden termina con la aplicación construida, desplegada y operativa.

Como documentos, la fase:

- **Empieza con el spike de deploy runtime en `D:/Repos/maura-uat`** (D-72 — patrón D-38/D-41 de la fase 3): deployar la app del taller a los servicios reales ANTES de firmar plataforma, ADR, doc 07 y guías.
- Extiende `docs/04_arquitectura/adr/` con ADRs nuevos continuando desde ADR-019 (candidatos: decisión de despliegue free tier, persistencia efímera aceptada).
- Extiende `docs/05_desarrollo/` con las guías 16+ (deploy API, deploy frontend + fallback SPA, verificación de los 4 flujos en producción) bajo la estructura canónica 🧠/✅/📝 y la convención "Gran verificación final".
- Escribe `docs/06_pruebas.md`, `docs/07_despliegue.md`, `docs/08_mantenimiento.md` y cierra las tablas de estado de TODOS los READMEs (fila 5 a Lista, filas 6-8 a Listo — D-13/D-18, quinta corrida).
- Cierra los índices: REQUIREMENTS (GUIDE-01/DEPL-01/DEPL-02 a Complete), ROADMAP §Progress, PROJECT.md Key Decisions.

La verificación de planes es documental (greps/estructura); el UAT runtime es delegado al agente en `D:/Repos/maura-uat` (instrucción persistida en AGENTS.md) — esta vez deployando el taller a los servicios reales y corriendo los 4 flujos Webpay contra el ambiente desplegado.

Requisitos cubiertos: DEPL-01, DEPL-02, GUIDE-01.

**Nota operativa del UAT (no bloquea planning):** deployar requiere cuentas free en las plataformas elegidas. El taller maura-uat usa cuentas creadas para él (sin tarjeta, como el alumno); si algún servicio exige verificación humana/pago, el usuario participa en ese paso puntual. El spike lo detecta temprano.

**Cierre del concern de STATE.md:** "elegir plataforma de despliegue free tier" se resuelve en esta discusión (D-69); "el deploy congela `return_url`" se implementa como env var de producción en las guías (nombres a discreción del research).

</domain>

<decisions>
## Implementation Decisions

*La numeración D continúa desde la fase 4 (D-01..D-18 en `01-CONTEXT.md`, D-19..D-33 en `02-CONTEXT.md`, D-34..D-49 en `03-CONTEXT.md`, D-50..D-68 en `04-CONTEXT.md`).*

### Plataforma de despliegue (DEPL-01 — resuelve el blocker de STATE.md)
- **D-69:** **Una plataforma por tier, free y sin tarjeta, candidata Vercel (frontend estático) + Render (API), validada por spike runtime ANTES de firmar.** El criterio es pedagógico: un solo camino por tier (nada de menús de opciones que dupliquen la guía), tier gratuito sin tarjeta de crédito (misma vara que D-60/D-63 con la API key), soporte real para SPA Vite (fallback a index.html incluido o configurable) y para FastAPI/Python. La candidata sale del consenso ya investigado en `.planning/research/STACK.md` (static en Vercel/Netlify/Cloudflare Pages + Render free API con spin-down y disco efímero); **el spike de deploy (D-72) la corrobora con evidencia runtime y puede sustituirla con evidencia si encuentra bloqueo** (p. ej. regional o de cuota) — el ADR-019 registra la elección final con esa evidencia, misma disciplina que D-41 con el retorno de Webpay. El research valida además cómo cerró su ciclo el repo hermano `demo-cine` para consistencia de la serie — **Reversibility:** costly — doc 07, ADR-019 y las guías 16+ se estructuran alrededor de la plataforma elegida; cambiarla después reescribe la etapa de despliegue completa.

### Persistencia en el free tier
- **D-70:** **SQLite + seed idempotente en producción, con el trade-off del disco efímero documentado honestamente; PostgreSQL (Neon free tier) queda como camino de crecimiento MENCIONADO, no implementado.** Render free reinicia/borra el disco en redeploys y spin-downs: la BD se pierde y el seed upsert (D-05/D-06/D-07, converge sin duplicar) la restaura — esa ES la lección: estado efímero + seed idempotente como estrategia explícita, no como bug. El sandbox de Webpay y la PYME ficticia hacen el trade-off aceptable para el aula (STACK.md ya lo declara así para la guía base). La migración futura es un cambio de `DATABASE_URL` + driver `psycopg` (STACK.md la documenta como variante) — la guía lo nombra como "cómo crecería esto" sin construirlo — **Reversibility:** reversible — el swap a PostgreSQL toca solo la URL de conexión y el driver; las guías no se reescriben, se extienden.

### Cierre documental del ciclo (GUIDE-01)
- **D-71:** **La fase 5 escribe los TRES documentos que faltan: `06_pruebas.md`, `07_despliegue.md` y `08_mantenimiento.md`.** El SC3 de GUIDE-01 exige el ciclo completo palabra por palabra ("necesidad → requerimientos → diseño → arquitectura con ADRs → desarrollo guiado → pruebas → despliegue → mantenimiento") y esta es la última fase: dejar alguno pendiente dejaría GUIDE-01 abierto. Reparto natural: **06** sintetiza la estrategia de pruebas ya vivida (mini-verificaciones por guía, Gran verificación final por fase, UAT runtime contra servicios reales — lo que el alumno ya hizo, ahora nombrado como método); **07** es la decisión de despliegue (candidata D-69, ADR-019, el porqué de free tier y del orden final de la fase); **08** cierra prospectivamente (v2 con los diferidos de REQUIREMENTS, cómo se mantiene esto vivo). El contenido exacto de cada doc es discreción del planner con `demo-cine` como referencia de formato — **Reversibility:** costly — la estructura del cierre y las tablas de estado de TODOS los READMEs (quinta corrida de D-13/D-18) se montan sobre qué docs existen y qué dicen.

### Disciplina de evidencia
- **D-72:** **El spike de deploy runtime es el PRIMER plan de la fase, antes de ADRs, doc 07 y guías** (patrón D-38/D-41 de la fase 3, replicado): en `D:/Repos/maura-uat`, deployar la app del taller (ya completa hasta guia-15) a los dos servicios reales, correr los 4 flujos Webpay contra el ambiente desplegado, cronometrar el spin-down y documentar los gotchas (return_url congelado, CORS, fallback SPA, disco efímero). Sus hallazgos alimentan ADR-019, doc 07 y las guías 16+ — la guía nace sin zonas oscuras y el UAT final no descubre nada nuevo. El código/notas del spike viven en `.planning/`, jamás en el repo (D-17) — **Reversibility:** one-way — el ADR-019 firma la elección de plataforma citando este spike como evidencia; re-hacerlo después significaría re-firmar el ADR y re-verificar docs ya cerradas.

### Claude's Discretion
- Estructura exacta de las guías 16+ y cuántas son (candidato natural: deploy API → deploy frontend + fallback → verificación de flujos + cierre; el planner parte bajo D-16 como siempre).
- Qué ADRs escribe la fase (candidatos: ADR-019 despliegue free tier con evidencia del spike; ADR-020 persistencia efímera + seed como estrategia) y sus títulos exactos.
- Nombres de las env vars de producción que las guías enseñan (base URL pública para `return_url`, origins del CORS, URL de la API para el build del frontend — p. ej. `VITE_API_URL`), sujetos a validación del research contra las convenciones de Vite/FastAPI ya usadas.
- Si `contrato_api.yaml` sube de versión o no: candidato a NO subir (D-66 fijó el principio de no bumpar sin churn real; el deploy no cambia paths ni schemas) — el planner lo confirma.
- Si `docs/02_requerimientos.md` gana RF/RNF de despliegue o el tema vive solo en doc 07 (P1-P8 ya están todas cubiertas; DEPL es infraestructura del ciclo, no petición de Maura — aunque P1 "que se abra desde cualquier dispositivo" es el ángulo narrativo natural).
- Contenido y estructura de `06_pruebas.md` y `08_mantenimiento.md` (con `demo-cine` como referencia de formato y tono).
- Cómo la Gran verificación final de fase 5 verifica: refresh de rutas sin 404, los 4 flujos contra el ambiente desplegado, contrato ↔ `/docs` público, y grep del build (AIAS-03) en producción — la forma exacta de la tabla es libre.
- Copys de las pantallas/estados nuevos que el deploy agregue (ninguno esperado — el deploy no cambia UI; solo si el spike descubre algo) y de los READMEs.
- Cómo el taller maneja las cuentas de plataforma del UAT delegado (nota operativa del dominio) y qué hace si un servicio exige verificación humana.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Planificación del proyecto
- `.planning/PROJECT.md` — Constraints (free tier sin gasto), pendiente explícito "plataforma de despliegue gratuita para los dos tiers", Key Decisions a cerrar (deploy + guía completa).
- `.planning/REQUIREMENTS.md` — La fase 5 cubre DEPL-01, DEPL-02, GUIDE-01 (ver Traceability); ojo con v2 diferidos que delimitan el cierre (PAY-05, ADMN-05, STAKE-*) y Out of Scope (pagos reales en producción).
- `.planning/ROADMAP.md` §Phase 5 — Goal, success criteria (SC1 free tier + CORS, SC2 refresh sin 404 + 4 flujos desplegados, SC3 ciclo completo) y el porqué del orden (congela `return_url`).
- `.planning/STATE.md` §Blockers/Concerns — "elegir plataforma de despliegue free tier (pendiente en PROJECT.md); el deploy congela return_url": ambos se resuelven aquí (D-69 + env vars).
- `.planning/phases/01-fundaciones-de-dos-tiers-y-cat-logo/01-CONTEXT.md` — Decisiones D-01..D-18 heredadas (D-17 guide-only, D-15 API-first, D-16 sub-guías, D-05/D-06/D-07 seed idempotente que D-70 reusa).
- `.planning/phases/02-cuentas-de-cliente-y-carro-persistente/02-CONTEXT.md` — Decisiones D-19..D-33 heredadas (D-23/D-24 seed de cuentas que el deploy re-sembrará).
- `.planning/phases/03-checkout-webpay-y-rdenes/03-CONTEXT.md` — Decisiones D-34..D-49 heredadas (D-38/D-41 spike con evidencia que D-72 replica; D-42 ruta de resultado; el `return_url` que esta fase congela).
- `.planning/phases/04-panel-de-administraci-n-y-asistente-ia/04-CONTEXT.md` — Decisiones D-50..D-68 heredadas (D-61 degradación sin GROQ_API_KEY; D-63 key del alumno sin tarjeta — la misma vara de D-69; CORS ya subido a [GET,POST,PUT,PATCH] en guia-12).

### Research ya hecho (insumo directo, no repetir de cero)
- `.planning/research/STACK.md` — Free-hosting consensus (static Vercel/Netlify/Cloudflare Pages + Render free API con spin-down y disco efímero), variante PostgreSQL (Neon + psycopg, solo cambiar `DATABASE_URL`), y la declaración explícita de que SQLite + seed idempotente es aceptable para la guía base documentando el trade-off (D-70 la cita).
- `.planning/phases/03-checkout-webpay-y-rdenes/03-SPIKE-RETORNO.md` — El patrón de spike runtime que D-72 replica (estructura de hallazgos, evidencia por flujo).

### Docs del ciclo que esta fase cierra o extiende
- `docs/README.md` — Tabla del ciclo: filas 6-8 (`06_pruebas.md`, `07_despliegue.md`, `08_mantenimiento.md`) hoy ⏳ Pendiente (D-71 las escribe); fila 5 pasa a Lista.
- `README.md` (raíz) — Portada del producto (D-18): ya promete "despliegue gratuito" (línea 27); su tabla del ciclo y su stack telegráfico se completan aquí.
- `docs/01_necesidad_del_cliente.md` — P1 "que se abra desde cualquier dispositivo" es el ángulo narrativo del deploy (la URL pública materializa la primera petición de Maura); CS5 firma por etapa.
- `docs/02_requerimientos.md` — Series completas hasta RF-24/RNF-09/RN-16/HU-13; el planner decide si DEPL entra como RNF nueva o vive en doc 07 (discreción anotada).
- `docs/03_diseno.md` — Sin pantallas nuevas esperadas (el deploy no cambia UI); DFDs/pantallas solo si el spike descubre algo.
- `docs/04_arquitectura/contrato_api.yaml` — 0.4.0 agnóstico (D-66): el deploy no debería cambiarlo (discreción del planner confirma).
- `docs/04_arquitectura/adr/` — ADRs 001-018 existentes; la fase continúa desde ADR-019 (formato demo-cine). ADR-012 (retorno) y ADR-018 (Groq) son los que el deploy ejercita en producción.
- `docs/05_desarrollo/README.md` — Índice de guías: la fase agrega guia-16+ y completa el mapa mental.
- `docs/05_desarrollo/guia-15-asistente-cierre.md` — Último eslabón actual: su "Siguiente" y su Gran verificación final son los que la fase 5 enlaza y replica (con el grep del build ya probado).
- `D:/Repos/demo-cine/docs/` — Referencia externa de formato (repo hermano): cómo cerró su ciclo de vida documental, tono de los docs de cierre.

### Fuentes externas (para research/spike, no archivos del repo)
- Documentación oficial de las plataformas candidatas (vercel.com/docs, render.com/docs): deploy de SPA Vite con fallback a index.html, deploy de FastAPI (build/start commands, env vars), límites del free tier (spin-down, disco efímero) — validar contra la fuente antes de fijar cifras en la guía (misma vara que D-68).
- transbankdevelopers.cl — `return_url` en ambiente de integración: requisitos de URL pública/HTTPS para el retorno (el spike lo corrobora runtime, no contra la doc sola).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Ninguno de código — **el repo es guide-only (D-17)**. Los assets reutilizables son patrones documentados:
- Estructura canónica de guías (guia-01..15) y convención "Gran verificación final" (tabla CS/RF + fila contrato ↔ `/docs`) que esta fase replica por última vez.
- Workspace `D:/Repos/maura-uat` con la app COMPLETA (hasta guia-15, `.env` con `GROQ_API_KEY`, órdenes reales de los 4 flujos, cuentas seed admin/clienta) — el insumo directo del spike de deploy y del UAT de fase 5.
- Seed idempotente por upsert (D-05/D-06/D-07 productos, D-23/D-24 cuentas) — la pieza que D-70 convierte en estrategia de persistencia ante el disco efímero.

### Established Patterns
- Backend en capas routers → services → repositories; solo `main.py` arma la app (con CORS ya en [GET,POST,PUT,PATCH] desde guia-12); secretos por env var vía pydantic-settings (`.env` + `SettingsConfigDict`).
- Firmar con evidencia antes de escribir: spike runtime → ADR → contrato → docs → guías (D-38/D-41/D-56/D-68) — D-72 lo aplica al deploy.
- UAT delegado al agente en maura-uat (instrucción persistida en AGENTS.md) — fase 5 lo extiende a deployar el taller.
- Bugs de guía: fix en AMBOS lugares (guía en demo-carro + taller en maura-uat) — regla persistida.

### Integration Points
- `return_url` de Webpay (guias 09/10): hoy armado contra localhost — la guía de fase 5 lo parametriza por env var de producción y lo congela a la URL pública.
- CORS del backend (guia-05, ampliado en guia-12): origins por env var para el frontend desplegado.
- `lib/api.ts` del frontend: base URL de la API — el build de producción la recibe por env var (convención `VITE_*` de Vite a validar).
- Router de la SPA: fallback a index.html para que el refresh de rutas no dé 404 (SC2/DEPL-02) — configuración del host estático, no código nuevo esperado.
- `guia-15-asistente-cierre.md`: el "Siguiente" que la fase 16+ enlaza; los READMEs (docs/, raíz, 05_desarrollo/) reciben la quinta corrida de estado (D-13/D-18).
- REQUIREMENTS.md Traceability + ROADMAP §Progress + PROJECT.md Key Decisions: cierran con GUIDE-01/DEPL-01/DEPL-02 Complete y la fase 5 marcada.

</code_context>

<specifics>
## Specific Ideas

- La Gran verificación final de fase 5 (la última de la serie): tabla numerada CS/RF con los 4 flujos Webpay corridos contra el AMBIENTE DESPLEGADO (no localhost), refresh de rutas sin 404, contrato ↔ `/docs` público en la URL de la API, y el grep del build (AIAS-03) re-verificado en producción.
- El spin-down del free tier como momento pedagógico: la primera request tras el sueño arranca fría (decenas de segundos) — la guía lo nombra honestamente en vez de esconderlo (misma honestidad que PENDING "en curso" de D-48).
- Narrativa del cierre: el deploy materializa P1 de docs/01 ("que se abra desde cualquier dispositivo") — la primera petición de Maura es la última en cumplirse; buen arco para el doc 07 y la guía de cierre.
- `08_mantenimiento.md` mira hacia adelante: v2 con los diferidos reales de REQUIREMENTS (PAY-05 guest checkout, ADMN-05 refund, STAKE-*), upgrade path a PostgreSQL (D-70), y cómo se mantiene la guía viva.
- `06_pruebas.md` nombra como método lo que el alumno ya vivió: mini-verificación por paso, Gran verificación final por fase, verificación runtime contra servicios reales (Webpay integración, Groq) — el porqué de cada una.
- Nota operativa del UAT: el taller deploya con cuentas free creadas para maura-uat (sin tarjeta); si un servicio exige verificación humana, el usuario participa en ese paso puntual.

</specifics>

<deferred>
## Deferred Ideas

- **PostgreSQL real en producción (Neon free tier + psycopg 3)** — mencionado por D-70 como camino de crecimiento en la guía; implementarlo sería una fase/variante propia (STACK.md ya documenta el patrón).
- **CI/CD pipeline (GitHub Actions: tests + deploy automático)** — no está en los requisitos v1; el deploy por Git-connected de las plataformas es suficiente para el aula.
- **Dominio propio + HTTPS custom** — el free tier entrega subdominios de plataforma con HTTPS incluido; el dominio propio es decisión de costo, fuera del alcance educativo gratuito.
- **Monitoreo/observabilidad más allá del doc 08** (uptime alerts, logs centralizados) — el doc lo cubre documentalmente; implementar herramientas sería capacidad nueva.

</deferred>

---

*Phase: 5-Despliegue y cierre de la guía*
*Context gathered: 2026-10-01 (modo `--auto`)*
