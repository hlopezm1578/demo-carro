---
phase: 05-despliegue-y-cierre-de-la-gu-a
plan: 03
subsystem: docs
tags: [deploy, render, vercel, spa-rewrite, vite, uv, seed-idempotente, cors, env-vars, guia]

requires:
  - phase: 05-despliegue-y-cierre-de-la-gu-a
    provides: ADR-019/ADR-020 y docs/07_despliegue.md (plan 05-01 — lo que las guías citan) y guia-15 como molde vigente de estructura canónica
provides:
  - docs/05_desarrollo/guia-16-despliegue-api.md: la guía del deploy del backend en Render Free (git → Web Service → env vars del triple congelado → verificación), citando ADR-019/020 y cobrando las promesas de guia-01/guia-09
  - docs/05_desarrollo/guia-17-despliegue-frontend.md: la guía del deploy de la SPA en Vercel Hobby (vercel.json commiteado, VITE_API_URL horneada, círculo del CORS, mini-verificación DEPL-02, grep del build extendido a producción)
  - El eslabón Siguiente 15 → 16 → 17 verificado por grep: guia-15 enlaza guia-16 por nombre de archivo con el conteo de ADRs al día (20)
affects: [05-04 (guia-18 asume las guías 16/17 hechas y su Siguiente ya enlazado), 05-05 (las tablas de estado cuentan guías 1-18)]

actuals:
  tokens: 11283         # chars/4 sobre el diff realizado (45.135 chars / 4)
  tasks: 2
  commits: 2            # MEDIDO: git rev-list --count 6322a00..HEAD
  plan_head_before: 6322a00f0187b37782cad4f4261aee5df15fb274
  plan_head_after: 65ad0475c0f3abe6b69e6c1802362ac79c55062d

tech-stack:
  added: []             # fase documental (D-17/D-73): cero paquetes; Vercel/Render ya firmados por ADR-019
  patterns: [Guía de deploy con tabla | Campo | Valor | y | Clave | Valor | (molde demo-cine 07 adaptado al taller uv), prohibición de placeholders con subdominio real — siempre <tu-servicio>/<tu-proyecto>]

key-files:
  created:
    - docs/05_desarrollo/guia-16-despliegue-api.md
    - docs/05_desarrollo/guia-17-despliegue-frontend.md
  modified:
    - docs/05_desarrollo/guia-15-asistente-cierre.md   # SOLO el bloque Siguiente (diff de precisión verificado pre y post commit)

key-decisions:
  - "Paso 0 de guia-16 enseña el estado REAL de los .gitignore del taller: el de backend lo creó guia-01 a mano (--vcs none) y el de frontend vino con el scaffold de Vite de guia-02 — la mini-verificación lista .env, *.db y node_modules como los tres que NO deben aparecer en GitHub"
  - "El grep del build en producción (guia-17 Paso 5) se enseña como rebuild local con la MISMA env var de Vercel (Vite hace el mismo reemplazo estático) — con control positivo (URL pública en dist/) y negativo (GROQ_API_KEY → cero), comando por shell Git Bash/PowerShell como guia-15:530"
  - "La promesa de guia-01 se cobra con la vuelta de tuerca honesta: el arranque de producción es uv run uvicorn con $PORT (la forma oficial de Render para FastAPI, citada), no fastapi run — narrado explícitamente en el 🧠 del Paso 1"
  - "guia-17 cita los bloques verbatim de guia-04:760-763 (${base}/${ruta}) y guia-09 (_hacia_spa con cors_origins[0]) como anclas — las cita, no las reescribe (cero delta UI)"

patterns-established:
  - "Las guías de deploy cierran cada paso con mini-verificación observable en el dashboard/URL pública (log del build con marcas [+]/[=], git status limpio de secretos, refresh de rutas profundas) — la verificación la define la guía, el alumno la corre (D-73)"

requirements-completed: [DEPL-01, DEPL-02]  # DEPL-01 queda Complete (05-01+05-03 con SUMMARY); DEPL-02 espera a 05-04 por el shared-ID gate — ready-ids devolvió solo DEPL-01

coverage:
  - id: D1
    description: "guia-16-despliegue-api.md: el backend en Render Free enseñado paso a paso (Paso 0 git con defensa .env/*.db/node_modules, tabla del Web Service con seed al build, triple congelado de env vars con PYTHON_VERSION 3.12.10 / CORS_ORIGINS JSON array / SECRET_KEY nueva, primer deploy con verificaciones) + eslabón del Siguiente de guia-15 (guia-16 por nombre de archivo, 20 ADRs)"
    requirement: DEPL-01
    verification:
      - kind: other
        ref: "grep gate del plan (g16-ok, GNU grep): título/Render/PYTHON_VERSION 3.12/BACKEND_URL/CORS_ORIGINS/comandos exactos de build y start/secrets.token_hex(32)/GROQ_API_KEY opcional/citas ADR-019+020+return_url+guia-01+guia-09/git init/render.com/docs/free con 'a la fecha'/tarjeta/6 mini-verificaciones/4 piensa/Siguiente a guia-17; negativos sin gsk_ y sin CORS comodín; guia-15 con guia-16-despliegue-api + 20 ADRs y sin 'los 18 ADRs'"
        status: pass
      - kind: other
        ref: "diff de precisión sobre guia-15 pre-commit (solo el bloque Siguiente cambia) + git show --stat post-commit (guia-15: 8 líneas; guia-16: 421 nuevas)"
        status: pass
    human_judgment: false
  - id: D2
    description: "guia-17-despliegue-frontend.md: la SPA en Vercel Hobby enseñada paso a paso (vercel.json rewrite commiteado ANTES del import, preset Vite + Root frontend + VITE_API_URL sin slash final, CORS cerrando el círculo del 302, mini-verificación DEPL-02 de rutas profundas, grep del build positivo+negativo en producción, notas heredadas con cero UI nueva)"
    requirement: DEPL-02
    verification:
      - kind: other
        ref: "grep gate del plan (g17-ok, GNU grep): título/vercel.json+index.html/VITE_API_URL con slash final y horneada/redeploy/CORS_ORIGINS como destino del 302 (cors_origins[0])/rutas /pago/resultado y /admin/pedidos/404/GROQ_API_KEY/anclas guia-04 e import.meta.env + guia-09/vercel.com + 'a la fecha'/tarjeta/6 mini-verificaciones/5 piensa/Siguiente a guia-18; negativo sin gsk_"
        status: pass
      - kind: other
        ref: "chequeo de prohibiciones y AC: rewrite exacto del Pattern 2 antes del import, URLs siempre placeholder (<tu-servicio>/<tu-proyecto>, verificado por grep — solo el patrón 'onrender.com' del grep aparece sin placeholder), links relativos resueltos (4/4 OK)"
        status: pass
    human_judgment: false

duration: 11 min
completed: 2026-10-01
status: complete
---

# Phase 5 Plan 3: guías 16/17 — deploy de la API (Render) y de la SPA (Vercel) Summary

**guia-16 publica la API en Render Free (git del taller, Web Service con seed al build, triple congelado PYTHON_VERSION/BACKEND_URL/CORS_ORIGINS, SECRET_KEY nueva) y guia-17 publica la SPA en Vercel Hobby (vercel.json commiteado, VITE_API_URL horneada sin slash final, mini-verificación DEPL-02 del refresh sin 404 y grep del build con control positivo) — el eslabón Siguiente 15 → 16 → 17 queda grep-verificable**

## Performance

- **Duration:** 11 min
- **Started:** 2026-10-01T18:17:23Z
- **Completed:** 2026-10-01T18:28:27Z
- **Tasks:** 2/2
- **Files modified:** 3 (2 creados, 1 editado en un solo bloque)

## Accomplishments

- guia-16-despliegue-api.md (421 líneas) con la estructura canónica completa de guia-15: cabecera blockquote con "nada de tarjetas (ADR-019)", 7 términos de deploy, Paso 0 git (el taller nació sin git por `--vcs none` — mini-verificación de que `.env`, `maura.db` y `node_modules` NO aparecen en GitHub), Paso 1 tabla del Web Service (Root `backend`, Build `uv sync --locked && uv run python -m app.seed`, Start `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`, Free) con el 🧠 que narra por qué el seed viaja en el build (ADR-020, upsert que converge), por qué uvicorn directo y no `fastapi run` (la promesa de guia-01 cobrada) y por qué `$PORT`; Paso 2 tabla de env vars con las cuatro decisiones congeladas (PYTHON_VERSION 3.12.10 vs default 3.14.3 de Render, BACKEND_URL sin slash congelando el return_url de guia-09 citado verbatim, CORS_ORIGINS como JSON array con la SettingsError de pydantic-settings conectada al fail-fast de secret_key, SECRET_KEY nueva con el comando); Paso 3 con el log del build (marcas `[+]`/`[=]`), /api/salud, /docs 0.4.0 y Authorize con las cuentas del seed; cold start con cifras citadas; nota D-73; 3 pares ❌/✅; tabla de errores típicos (Pitfalls 1/4/9 + login con tabla vacía); Punto de control (3 preguntas ADR-019/020/D-70/D-73) y Siguiente → guia-17
- guia-17-despliegue-frontend.md (380 líneas) con la misma estructura: Paso 1 vercel.json con el rewrite exacto `/(.*)` → `/index.html` commiteado ANTES del import (Pitfall 7, KB oficial citada); Paso 2 import con preset Vite, Root `frontend` y VITE_API_URL scope Production SIN slash final (Pitfall 3 con la cita de vite.dev y el bloque verbatim de guia-04:760-763 como ancla del doble slash, más la promesa de guia-02:416-418 cobrada); Paso 3 cierra el círculo del CORS (CORS_ORIGINS → URL real de Vercel, cita `_hacia_spa` de guia-09, carro/sesión cruzan el full-page load); Paso 4 mini-verificación DEPL-02 (refresh F5 en /carro + deep-links fríos a /pago/resultado, /admin/pedidos, /productos/1 → 200 con la SPA, jamás 404) con la cadena crítica del retorno de Webpay en prosa; Paso 5 grep del build extendido a producción (control positivo URL pública + negativo GROQ_API_KEY → cero, por shell como guia-15:530); notas heredadas (401 con returnTo D-22, familia de errores + Reintentar como UX del cold start, síntomas //api y localhost) con cero UI nueva; 3 pares ❌/✅; tabla de errores típicos (Pitfalls 3/7 + CORS a localhost); Siguiente → guia-18
- El eslabón de la cadena: guia-15 editado SOLO en su bloque Siguiente (diff de precisión verificado pre-commit y confirmado con `git show --stat` post-commit) — ahora nombra `guia-16-despliegue-api.md` por nombre de archivo y dice "los 20 ADRs"; la cadena 15 → 16 → 17 → (18, la escribe 05-04) queda continua

## Task Commits

Each task was committed atomically:

1. **Task 1: guia-16-despliegue-api.md — el backend en Render free + eslabón del Siguiente de guia-15** - `59c9a24` (docs)
2. **Task 2: guia-17-despliegue-frontend.md — la SPA en Vercel: rewrite, VITE_API_URL horneada y la mini-verificación DEPL-02** - `65ad047` (docs)

**Plan metadata:** (commit final de este plan, ver abajo)

## Files Created/Modified

- `docs/05_desarrollo/guia-16-despliegue-api.md` - Guía 16: deploy del backend en Render Free con el triple congelado y el seed al build (D-69/D-70/D-73 enseñados al alumno)
- `docs/05_desarrollo/guia-17-despliegue-frontend.md` - Guía 17: deploy de la SPA en Vercel con el rewrite DEPL-02, VITE_API_URL horneada y el grep del build en producción
- `docs/05_desarrollo/guia-15-asistente-cierre.md` - Solo el bloque Siguiente: enlace a guia-16 por nombre de archivo + conteo de ADRs 18 → 20

## Decisions Made

- Paso 0 de guia-16 relata el estado real de los `.gitignore` del taller: backend (creado a mano en guia-01 por `--vcs none`) y frontend (vino con el scaffold de Vite de guia-02) — la defensa existe desde la fase 1 y hoy se verifica; la mini-verificación nombra los TRES artefactos que no deben subir (.env, maura.db, node_modules)
- El grep "contra producción" de guia-17 se resolvió como rebuild local con la misma env var de Vercel (Vite hace el mismo reemplazo estático al build — el dist/ local es copia del bundle de producción), con la confirmación viva del paso 3 (Network contra la URL pública); ambas caras del grep (positiva y negativa) quedaron como pasos numerados
- Las citas de guías previas van por nombre de archivo donde la serie lo pide (`guia-01-proyecto-backend.md`, `guia-09-ordenes-webpay.md`) y por bloque verbatim donde son ancla de código (config.py de guia-09, `${base}/${ruta}` de guia-04, `_hacia_spa`) — las guías 16/17 cobran promesas, no reescriben
- La nota D-73 vive como blockquote dentro del Paso 3 de guia-16 ("esta guía la vives TÚ, en tus cuentas — el proyecto que escribe esta guía no deploya") y el registro de flujo Vercel/Render "sin tarjeta" cita vercel.com/docs/plans/hobby y ADR-019 con "a la fecha"

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- El gate de Task 1 falló en la primera corrida por dos literales ausentes (`guia-01`, `guia-09`): la redacción inicial citaba "guía 1"/"guía 9" en prosa. Corregido referenciando por nombre de archivo (`guia-01-proyecto-backend.md` en el 🧠 del Paso 1, `guia-09-ordenes-webpay.md` en la decisión 2 del Paso 2) — sin cambios de contenido. Los gates pasaron (g16-ok, g17-ok) ejecutados con `/usr/bin/grep` (GNU grep) por el tema ugrep documentado en 05-02-SUMMARY.
- Ajuste de higiene propio de las prohibiciones del plan: los primeros borradores de guia-16 usaban `tienda.vercel.app` como valor de ejemplo en el par ❌/✅ y la tabla de errores; se normalizó todo al placeholder `<tu-proyecto>` (verificado por grep: cero subdominios reales, cero localhost enseñado como valor).

## User Setup Required

None - no external service configuration required. (D-73: las cuentas de Vercel/Render las crea el ALUMNO siguiendo las guías 16/17 — este plan no ejecuta runtime.)

## Next Phase Readiness

- guia-16 y guia-17 existen con la estructura canónica completa y la cadena Siguiente 15 → 16 → 17 → guia-18 (nombre ya reservado) — el plan 05-04 escribe guia-18 con los 4 flujos y la Gran verificación final de la serie
- DEPL-01 queda marcado Complete en REQUIREMENTS.md (todos sus planes declarantes con SUMMARY); DEPL-02 espera a 05-04 por el shared-ID gate
- Los links de guia-16/17 a ADR-019/020, doc 07 y entre guías resuelven (verificado); el contrato_api.yaml no se tocó (sigue 0.4.0, D-66)
- Sin blockers ni concerns nuevos

## Self-Check: PASSED

Archivos creados existen en disco (guia-16: 421 líneas; guia-17: 380 líneas); commits 59c9a24 y 65ad047 en el log; commits medidos contra el ledger (6322a00..HEAD = 2); gates del plan re-ejecutados en verde (g16-ok, g17-ok); diff de precisión de guia-15 verificado pre y post commit; sin deletions ni untracked.

---
*Phase: 05-despliegue-y-cierre-de-la-gu-a*
*Completed: 2026-10-01*
