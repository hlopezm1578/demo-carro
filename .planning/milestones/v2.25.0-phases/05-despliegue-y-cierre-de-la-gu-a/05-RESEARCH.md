# Phase 5: Despliegue y cierre de la guía - Research

**Researched:** 2026-10-01
**Updated:** 2026-10-01 — reconciliación con D-73 (corrección de alcance del usuario): este research se escribió PRE-D-73 y lleva anotaciones **[Actualización D-73: ...]** / **[SUPERSEDED por D-73: ...]** donde su guía original instruía el spike runtime abolido. Propiedad vigente: la fase es SOLO ESCRITURA; el runtime del deploy lo corre el ALUMNO siguiendo las guías 16-18 en SUS cuentas; la verificación del proyecto es documental (greps/estructura).
**Domain:** Despliegue free tier de dos tiers (SPA estática + API FastAPI) con `return_url` de Webpay congelado, y cierre documental del ciclo (docs 06/07/08) — repo guide-only (D-17): la fase entrega DOCUMENTOS; el runtime se verifica delegado en `D:/Repos/maura-uat` **[Actualización D-73: NO — maura-uat no aplica al deploy en esta fase; el runtime del deploy lo corre el ALUMNO siguiendo las guías 16-18 en sus cuentas free]**
**Confidence:** HIGH (integraciones del repo leídas directamente + docs oficiales de ambas plataformas y de Transbank citadas; los puntos que solo el runtime puede confirmar quedan explícitamente asignados al spike D-72) **[Actualización D-73: sin spike (D-72 superseded) — esos puntos quedan como supuestos señalados (A1-A8, § Assumptions Log) cuya confirmación runtime es del alumno]**

## Summary

La fase 5 tiene dos frentes que se alimentan mutuamente: el **spike de deploy runtime (D-72)** — que deploya el taller de maura-uat a los dos servicios reales ANTES de firmar nada — y el **cierre documental del ciclo (D-71)** — docs `06_pruebas.md`, `07_despliegue.md`, `08_mantenimiento.md` + ADRs 019/020 + guías 16+ + quinta corrida de tablas de estado. **[SUPERSEDED por D-73 (2026-10-01): el primer frente (spike runtime D-72) fue abolido — la fase es solo escritura. La corroboración de la candidata D-69 quedó DOCUMENTAL (docs oficiales citadas en § Sources, sin bloqueo encontrado); el deploy y su verificación los vive el alumno con las guías 16-18.]** El research confirma que la candidata D-69 (Vercel frontend + Render API) es viable por diseño: ambas plataformas publican exactamente lo que la app ya es (SPA estática Vite + servicio web Python), ambas tienen tier gratuito sin tarjeta, y los tres "congelamientos" que el deploy exige ya existen como env vars en el código que las guías enseñan — no hay código nuevo que inventar, solo configuración que enseñar.

El hallazgo técnico más importante para el spike: **el taller maura-uat NO es un repositorio git** (verificado: `git rev-parse` falla con "fatal: not a git repository") y ambas plataformas deployan desde un repo Git — el spike necesita un paso 0 (git init + push a GitHub, con `.env` y `*.db` ya gitignoreados por guia-01/03). **[Actualización D-73: el paso 0 vive hoy como Paso 0 de guia-16 — lo corre el ALUMNO sobre SU proyecto (misma protección `.env`/`*.db`); maura-uat no se deploya en esta fase.]** El segundo hallazgo: **Render hoy deja por defecto Python 3.14.3 en servicios nuevos** [CITED: render.com/docs/python-version], y el techo declarado del SDK de Transbank es 3.12 (STACK.md: classifiers 3.8–3.12) — la guía DEBE fijar `PYTHON_VERSION` (o `.python-version`), o el `uv sync` revienta contra un `requires-python = ">=3.12,<3.13"` que el propio taller trae. Tercero: **Render soporta uv nativamente** desde 2025-06-12 (basta incluir `uv.lock` en la raíz del servicio) [CITED: render.com/changelog/added-uv-to-the-python-native-runtime] — el taller ya tiene `backend/uv.lock`, así que no hay que generar `requirements.txt`. Y cuarto: **Vercel NO infiere que un proyecto es SPA** — el fallback a `index.html` exige un `vercel.json` con rewrite explícito, commiteado en la raíz [CITED: vercel.com/kb/guide/why-is-my-deployed-project-giving-404]; ese rewrite ES el DEPL-02 del refresh sin 404.

Para el cierre documental, `D:/Repos/demo-cine/docs/` (leído completo) entrega el formato exacto de los tres docs: cabecera con "Fase del ciclo de vida / Qué construirás hoy / Al terminar tendrás", tabla de términos, pasos con 🧠, tabla de errores típicos, ✅ verificación con columna Origen, 📝 punto de control, "Lo que acabas de aprender" y enlace de cierre. La diferencia de contenido es la lección: demo-cine deployó con Postgres persistente (Render + Neon); demo-carro deploya **con SQLite efímero + seed idempotente como estrategia explícita (D-70)** — y las docs de Render nombran textualmente "local SQLite databases" como lo que se pierde [CITED: render.com/docs/free], citación perfecta para el ADR-020.

**Primary recommendation:** Plan de la fase en este orden (D-72 manda): (0) spike en maura-uat — git init + push, deploy API a Render con `PYTHON_VERSION=3.12.x` + `uv.lock` + seed al build, deploy SPA a Vercel con `vercel.json` rewrite + `VITE_API_URL`, env triple congelada (`BACKEND_URL`/`CORS_ORIGINS` JSON/`VITE_API_URL`), 4 flujos Webpay contra el ambiente desplegado, cronómetro de spin-down; (1) ADRs 019/020 con la evidencia del spike; (2) docs 06/07/08 con formato demo-cine; (3) guías 16+ (deploy API → deploy frontend + fallback → verificación de flujos + cierre); (4) cierre de índices (REQUIREMENTS/ROADMAP/PROJECT/READMEs). El contrato 0.4.0 NO sube de versión (D-66: el deploy no cambia paths ni schemas). **[SUPERSEDED por D-73 — orden vigente: NO hay paso (0) de spike. Los planes reales son (1) 05-01: ADRs 019/020 + doc 07 con evidencia documental; (2) 05-02: docs 06/08; (3) 05-03: guías 16/17 (deploy API → deploy frontend + fallback) enseñadas al alumno; (4) 05-04: guia-18 (4 flujos + Gran verificación final DEFINIDA para el alumno); (5) 05-05: cierre de tablas de los READMEs. La confirmación runtime que el paso (0) proveería es hoy del alumno (D-73).]**

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-69:** **Una plataforma por tier, free y sin tarjeta, candidata Vercel (frontend estático) + Render (API), validada por spike runtime ANTES de firmar.** El criterio es pedagógico: un solo camino por tier (nada de menús de opciones que dupliquen la guía), tier gratuito sin tarjeta de crédito (misma vara que D-60/D-63 con la API key), soporte real para SPA Vite (fallback a index.html incluido o configurable) y para FastAPI/Python. La candidata sale del consenso ya investigado en `.planning/research/STACK.md` (static en Vercel/Netlify/Cloudflare Pages + Render free API con spin-down y disco efímero); **el spike de deploy (D-72) la corrobora con evidencia runtime y puede sustituirla con evidencia si encuentra bloqueo** (p. ej. regional o de cuota) — el ADR-019 registra la elección final con esa evidencia, misma disciplina que D-41 con el retorno de Webpay. El research valida además cómo cerró su ciclo el repo hermano `demo-cine` para consistencia de la serie — **Reversibility:** costly — doc 07, ADR-019 y las guías 16+ se estructuran alrededor de la plataforma elegida; cambiarla después reescribe la etapa de despliegue completa. **[Actualización D-73: sin spike runtime, la corroboración quedó DOCUMENTAL — este research citó las docs oficiales de ambas plataformas (SPA fallback, FastAPI deploy, free tier) y no encontró bloqueo para la candidata; sustitución solo si apareciera evidencia documental en contra antes de firmar el ADR-019.]**

- **D-70:** **SQLite + seed idempotente en producción, con el trade-off del disco efímero documentado honestamente; PostgreSQL (Neon free tier) queda como camino de crecimiento MENCIONADO, no implementado.** Render free reinicia/borra el disco en redeploys y spin-downs: la BD se pierde y el seed upsert (D-05/D-06/D-07, converge sin duplicar) la restaura — esa ES la lección: estado efímero + seed idempotente como estrategia explícita, no como bug. El sandbox de Webpay y la PYME ficticia hacen el trade-off aceptable para el aula (STACK.md ya lo declara así para la guía base). La migración futura es un cambio de `DATABASE_URL` + driver `psycopg` (STACK.md la documenta como variante) — la guía lo nombra como "cómo crecería esto" sin construirlo — **Reversibility:** reversible — el swap a PostgreSQL toca solo la URL de conexión y el driver; las guías no se reescriben, se extienden.

- **D-71:** **La fase 5 escribe los TRES documentos que faltan: `06_pruebas.md`, `07_despliegue.md` y `08_mantenimiento.md`.** El SC3 de GUIDE-01 exige el ciclo completo palabra por palabra ("necesidad → requerimientos → diseño → arquitectura con ADRs → desarrollo guiado → pruebas → despliegue → mantenimiento") y esta es la última fase: dejar alguno pendiente dejaría GUIDE-01 abierto. Reparto natural: **06** sintetiza la estrategia de pruebas ya vivida (mini-verificaciones por guía, Gran verificación final por fase, UAT runtime contra servicios reales — lo que el alumno ya hizo, ahora nombrado como método); **07** es la decisión de despliegue (candidata D-69, ADR-019, el porqué de free tier y del orden final de la fase); **08** cierra prospectivamente (v2 con los diferidos de REQUIREMENTS, cómo se mantiene esto vivo). El contenido exacto de cada doc es discreción del planner con `demo-cine` como referencia de formato — **Reversibility:** costly — la estructura del cierre y las tablas de estado de TODOS los READMEs (quinta corrida de D-13/D-18) se montan sobre qué docs existen y qué dicen.

- **D-72:** **El spike de deploy runtime es el PRIMER plan de la fase, antes de ADRs, doc 07 y guías** (patrón D-38/D-41 de la fase 3, replicado): en `D:/Repos/maura-uat`, deployar la app del taller (ya completa hasta guia-15) a los dos servicios reales, correr los 4 flujos Webpay contra el ambiente desplegado, cronometrar el spin-down y documentar los gotchas (return_url congelado, CORS, fallback SPA, disco efímero). Sus hallazgos alimentan ADR-019, doc 07 y las guías 16+ — la guía nace sin zonas oscuras y el UAT final no descubre nada nuevo. El código/notas del spike viven en `.planning/`, jamás en el repo (D-17) — **Reversibility:** one-way — el ADR-019 firma la elección de plataforma citando este spike como evidencia; re-hacerlo después significaría re-firmar el ADR y re-verificar docs ya cerradas. **[SUPERSEDED por D-73 (corrección del usuario, 2026-10-01): la fase es solo escritura — no se ejecuta runtime, no hay spike ni UAT de despliegue. La evidencia del ADR-019 pasa a ser documental: fuentes oficiales citadas en este research.]**

- **D-73:** **La fase 5 es SOLO ESCRITURA de las guías y documentos — el proyecto NO ejecuta ni prueba el deploy.** Decisión del usuario a mitad del pipeline ("esta fase solo es la escritura de las guías, no la probaremos"): sin spike runtime (D-72 superseded), sin deployar el taller maura-uat, sin verificación de los 4 flujos contra un ambiente desplegado por parte del proyecto. Las guías 16+ enseñan el deploy al alumno paso a paso con mini-verificaciones y una Gran verificación final QUE EL ALUMNO CORRE en sus propias cuentas free; la guía las define con exactitud (URLs de plataforma, tarjetas de prueba de la fase 3, pasos numerados), pero el proyecto no las ejecuta. La verificación de planes y de fase es documental (greps/estructura — la forma estándar de la serie guide-only). El ADR-019 firma la elección de plataforma con evidencia documental (docs oficiales de Vercel/Render citadas con URL en este research, misma vara de citación que D-68) — **Reversibility:** costly — estructura toda la fase: qué planes existen (sin plan de spike/UAT), qué verifica la Gran verificación final y cómo cierran los índices. *(Entrada añadida en la reconciliación post-D-73; el resto de esta sección se escribió pre-D-73 y lleva anotaciones donde corresponde.)*

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

**[Resoluciones del planner (2026-10-01, post-D-73) — registradas aquí porque todos los executors leen este research vía `<context>`:]**
- **Guías 16+ (tres; planes 05-03/05-04):** `guia-16-despliegue-api.md`, `guia-17-despliegue-frontend.md`, `guia-18-despliegue-cierre.md`.
- **ADRs (plan 05-01):** `019-despliegue-free-tier-vercel-render.md` + `020-persistencia-efimera-seed-idempotente.md` — con evidencia DOCUMENTAL (D-73), no de spike.
- **Nombres de env vars:** fijados por el código existente (Pattern 1, "Nota de nombres") — `BACKEND_URL`, `CORS_ORIGINS` (JSON array), `VITE_API_URL`, `PYTHON_VERSION` fully-qualified; inventar otros rompería contra lo construido.
- **Contrato:** NO sube — queda **0.4.0** (D-66: sin churn no hay bump); los planes 05-01/05-04 lo fijan con gate negativo (0.5.0 vetado) y la fila contrato ↔ `/docs` de guia-18 sigue contra 0.4.0 en la URL pública.
- **RNF de despliegue:** NO se crea — **doc 07 es el hogar del deploy** (P1 como ángulo narrativo; P1-P8 ya cubiertas; sin renumerar series).
- **Gran verificación final:** DEFINIDA en guia-18 como tabla para el alumno (refresh sin 404, 4 flujos con resultado esperado, contrato 0.4.0 ↔ `/docs` público con Authorize, grep del build en producción, ciclo efímero, paridad cero drift) — el proyecto NO la corre (D-73).
- **Copys/UI:** cero UI nueva (paridad dev ↔ producción).
- **Cuentas de plataforma / UAT delegado (último bullet de arriba): SUPERSEDED por D-73** — no hay UAT delegado de deploy; las cuentas las crea el ALUMNO en guia-16/17, y si un flujo exigiera verificación humana, la guía lo declara y remite a la doc oficial.

### Deferred Ideas (OUT OF SCOPE)

- **PostgreSQL real en producción (Neon free tier + psycopg 3)** — mencionado por D-70 como camino de crecimiento en la guía; implementarlo sería una fase/variante propia (STACK.md ya documenta el patrón).
- **CI/CD pipeline (GitHub Actions: tests + deploy automático)** — no está en los requisitos v1; el deploy por Git-connected de las plataformas es suficiente para el aula.
- **Dominio propio + HTTPS custom** — el free tier entrega subdominios de plataforma con HTTPS incluido; el dominio propio es decisión de costo, fuera del alcance educativo gratuito.
- **Monitoreo/observabilidad más allá del doc 08** (uptime alerts, logs centralizados) — el doc lo cubre documentalmente; implementar herramientas sería capacidad nueva.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DEPL-01 | Frontend estático y API quedan desplegados en free tier con URLs públicas y CORS de producción configurado | Candidata D-69 validada documentalmente (Vercel Hobby sin tarjeta + Render Free sin tarjeta; ambos con HTTPS en subdominio propio); CORS de producción = `CORS_ORIGINS` como JSON array de pydantic-settings (Pitfall 4); el triple de env vars ya existe en el código de las guías (`backend_url`, `cors_origins`, `VITE_API_URL`) — verificado in-repo |
| DEPL-02 | El refresh de rutas de la SPA no da 404 (fallback a index.html) y los 4 flujos de retorno de Webpay se verifican contra el ambiente desplegado | Fallback: `vercel.json` rewrite explícito (Vercel no infiere SPA) [CITED: vercel.com KB]; los 4 flujos: mecánica ya firmada en ADR-012 + spike fase 3, ahora contra URLs públicas — el `return_url` exige URL válida SSL ≤ 255 chars [CITED: transbankdevelopers.cl]; la cadena completa 302 API→SPA depende de `BACKEND_URL` + `cors_origins[0]` congelados (verificado in-repo guia-09) |
| GUIDE-01 | La guía documenta el ciclo de vida completo con trazabilidad entre fases | Los tres docs que faltan (06/07/08) existen en demo-cine como referencia de formato leída completa; filas 6-8 de docs/README.md y README raíz hoy ⏳ Pendiente (leído); D-71 fija el reparto; cierre de índices REQUIREMENTS/ROADMAP/PROJECT documentado en CONTEXT |
</phase_requirements>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Hosting SPA (build estático, fallback a index.html) | CDN / Static (Vercel) | — | La SPA compila a archivos estáticos; el fallback de routing es configuración del host (`vercel.json` rewrite), no código de la app |
| Hosting API (uvicorn, $PORT) | API / Backend (Render) | — | Servicio web Python con start command `uvicorn ... --port $PORT`; solo Render corre código de servidor |
| TLS / HTTPS de las URLs públicas | Plataforma (ambas) | — | Certificados incluidos en el subdominio de cada plataforma; jamás hand-roll — requisito SSL del `return_url` queda cubierto por diseño |
| Congelar `return_url` y origen del 302 | API / Backend (env vars) | Configuración de plataforma | `settings.backend_url` (ida a Webpay) y `settings.cors_origins[0]` (302 `_hacia_spa`) ya viven en el backend; producción las sobreescribe por entorno |
| CORS de producción | API / Backend (middleware) | Dashboard de plataforma | `CORSMiddleware` con `allow_origins=settings.cors_origins` ya existe (guia-05/12); el deploy solo cambia el VALOR de la lista, no el código |
| Base URL de la API en el frontend | Browser / Client (build) | Vercel env vars | `import.meta.env.VITE_API_URL` se hornrea al build (reemplazo estático de Vite); en dev la suple el proxy `/api` de Vite |
| Persistencia (SQLite + seed idempotente) | Database / Storage (efímero) | Build de Render | El seed corre en el Build Command (patrón demo-cine `&& python semilla.py`); la BD es archivo local efímero — D-70 |
| Deploy continuo (git push → redeploy) | Plataforma (Git-connected) | — | Ambas plataformas construyen desde el repo Git; es el "CI/CD en chico" que demo-cine ya enseñó — no se hand-rolea nada |
| Cierre documental del ciclo | Repositorio docs (guide-only) | — | Docs 06/07/08 + ADRs 019/020 + guías 16+ + READMEs: el producto del repo (D-17) |

## Standard Stack

### Plataformas (lo que esta fase "instala" — el repo no instala paquetes)

| Plataforma | Plan | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Vercel | Hobby (free) | Hosting del frontend estático (SPA Vite) | Candidata D-69; gratis sin tarjeta [CITED: vercel.com/docs/plans/hobby]; deploy nativo de Vite (Framework Preset Vite); HTTPS incluido en `*.vercel.app`; rewrite a index.html configurable vía `vercel.json` |
| Render | Free | Hosting de la API (Web Service Python) | Candidata D-69; 750 instance-hours/mes, sin tarjeta para free; soporte nativo de Python 3.12 vía `PYTHON_VERSION`; soporte nativo de uv vía `uv.lock` [CITED: render.com/changelog]; HTTPS incluido en `*.onrender.com` |

No hay stack de librerías nueva: **la fase no instala dependencias** — ni el repo (guide-only, D-17) ni el taller (la app completa hasta guia-15 ya corre). El deploy reusa lo construido: Vite 8.3.1 + react-router 8.4.0 (BrowserRouter) en el frontend; FastAPI + uvicorn (dentro de `fastapi[standard]`) + uv en el backend [VERIFIED: maura-uat/frontend/package.json scripts `dev/build/lint/preview`, dependencies `react-router ^8.4.0`; maura-uat/backend/pyproject.toml dependencies leído directo].

### Alternativas Consideradas

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Vercel (frontend) | Netlify / Cloudflare Pages | Las tres sirven SPA estática con fallback; Vercel gana por el Framework Preset Vite y el flujo Git-connected más directo para el aula — STACK.md ya declaró el consenso |
| Render (API) | Fly.io / Railway | Render es la que demo-cine ya usó (consistencia de serie), tiene free sin tarjeta y docs oficiales en español no, pero sí claras para FastAPI; Railway ya no tiene free real |
| SQLite + seed (D-70) | Neon PostgreSQL | Diferido explícitamente: se MENCIONA como camino de crecimiento (cambio de `DATABASE_URL` + `psycopg`), no se implementa |
| Deploy Git-connected | Vercel CLI / Render API | La alternativa CLI existe para el spike si Gitconnected falla, pero Git-connected ES el contenido pedagógico (CI/CD en chico, demo-cine Paso 4) — [D-73: el fallback CLI, si alguien lo necesitara, es del alumno en guia-16/17] |

### Installation

```bash
# Nada que instalar en el repo (guide-only). En el taller (spike) —
# [Actualización D-73: estos comandos son hoy el Paso 0 de guia-16, corridos por el
#  ALUMNO sobre SU proyecto; el proyecto no ejecuta spike]:
# paso 0 obligatorio — maura-uat NO es repo git hoy:
cd D:/Repos/maura-uat && git init && git add . && git commit -m "taller completo hasta guia-15"
# crear repo GitHub (web, sin gh CLI disponible) y push
```

## Package Legitimacy Audit

> Esta fase NO instala paquetes externos: el repositorio es guide-only (D-17) y el taller maura-uat ya tiene todas sus dependencias (`backend/pyproject.toml` + `uv.lock`, `frontend/package.json` — leídos directo). El "proveedor" nuevo son las plataformas Vercel y Render, verificadas contra sus docs oficiales (citas en Sources). No se requiere gate de paquetes.

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
                       AMBIENTE DESPLEGADO (free tier)
                       ================================

  [Navegador del alumno/cliente]          [Webpay Plus - integración]
        │                                          ▲
        │ 1. carga SPA (cualquier ruta,            │ form POST auto-submit
        │    vercel.json rewrite → index.html)     │ con token_ws
        ▼                                          │
  ┌─────────────────┐   2. fetch API (CORS)   ┌────┴──────────┐
  │  VERCEL Hobby   │────────────────────────▶│  RENDER Free  │
  │  SPA estática   │   VITE_API_URL horneada │  API FastAPI  │
  │  *.vercel.app   │   al build              │  *.onrender   │
  │                 │                         │  .com         │
  │  vercel.json:   │◀───────────────────────│               │
  │  rewrite /(.* ) │  3. JSON (auth, carro,  │  uvicorn      │
  │  → /index.html  │    catálogo, checkout)  │  $PORT        │
  └─────────────────┘                         │  PYTHON_      │
        ▲                                     │  VERSION=3.12 │
        │ 8. 302 Location:                    │  uv.lock      │
        │    cors_origins[0]/pago/resultado   │  + seed al    │
        │    (SPA pública)                    │    build      │
        │                                     └───────┬───────┘
        │                                             │ 4. create(buy_order,
        │                                             │    session_id, amount,
        │                                             │    return_url=
        │                                             │    BACKEND_URL+
        │                                             │    /api/pago/retorno)
        │                                             ▼
        │                                    [SQLite maura.db]
        │                                     efímero: se pierde en
        │                                     redeploy/spin-down; el seed
        │  5-7. Webpay devuelve el navegador  │ del build lo restaura
        │      al return_url (GET o POST,     └───────────────
        │      4 flujos, params distintos) ──▶ API discrimina por
        │                                      presencia de params
        │                                      (ADR-012), commit si
        │                                      token_ws, 302 → SPA
```

Flujo traza: (1) refresh de `/pago/resultado` directo → Vercel sirve `index.html` (DEPL-02); (2) SPA habla a la API por `VITE_API_URL` con CORS de lista explícita (DEPL-01); (4) el `return_url` apunta a la URL pública de la API (congelado por `BACKEND_URL`); (5-7) Webpay redirige el navegador de vuelta al return_url público con params por flujo; (8) el backend responde 302 hacia la SPA pública (`cors_origins[0]`).

### Recommended Project Structure

Lo que la fase AGREGA al repo (todo documento — D-17):

```
docs/
├── 06_pruebas.md                      # NUEVO — síntesis del método ya vivido (D-71)
├── 07_despliegue.md                   # NUEVO — decisión D-69/ADR-019 + por qué va al final
├── 08_mantenimiento.md                # NUEVO — cierre prospectivo (v2, PostgreSQL, guía viva)
├── README.md                          # EDIT — filas 5 (→ Lista) y 6-8 (→ Listo)
├── 04_arquitectura/adr/
│   ├── 019-*.md                       # NUEVO — despliegue free tier (evidencia del spike → [D-73: evidencia DOCUMENTAL, § Sources])
│   └── 020-*.md                       # NUEVO — persistencia efímera + seed como estrategia
└── 05_desarrollo/
    ├── README.md                      # EDIT — guías 16+, mapa mental completo
    ├── guia-16-*.md                   # NUEVO — deploy API (Render)
    ├── guia-17-*.md                   # NUEVO — deploy frontend + fallback SPA (Vercel)
    └── guia-18-*.md                   # NUEVO — 4 flujos en producción + Gran verificación
                                        #         final de la serie (nombres a discreción
                                        #         del planner bajo D-16)
README.md                              # EDIT — tabla del ciclo completa + stack telegráfico
.planning/...                          # hallazgos del spike (jamás en docs/, D-72) — [D-73: sin spike; esta línea no aplica]
```

### Pattern 1: El triple de env vars congeladas (la configuración ES el deploy)

**What:** El deploy no cambia código: sobreescribe tres valores que las guías ya parametrizaron. Verificado in-repo:

- Backend `Settings` [VERIFIED: D:/Repos/maura-uat/backend/app/config.py — leído directo, y guia-09:598-603]:

```python
    # --- Etapa 3: pago Webpay (ADR-012) ---
    # La URL pública del BACKEND: a ella vuelve el navegador desde Webpay
    # (return_url). NO es cors_origins — esa es la SPA. Dev y producción
    # difieren; la fase 5 la congelará junto con el origen público.
    backend_url: str = "http://localhost:8000"
```
  junto a `cors_origins: list[str] = ["http://localhost:5173"]`, `secret_key: str` (fail-fast sin default), `admin_email/admin_password/cliente_email/cliente_password`, `groq_api_key: str | None = None`, `model_config = SettingsConfigDict(env_file=".env")` — el campo completo está en config.py del taller.

- El uso en el retorno [VERIFIED: docs/05_desarrollo/guia-09-ordenes-webpay.md:685]: `return_url=f"{settings.backend_url}/api/pago/retorno"` y [VERIFIED: guia-09:1053-1054]:
```python
    url = f"{settings.cors_origins[0]}/pago/resultado?{urlencode(params)}"
    return RedirectResponse(url, status_code=302)  # 302 EXPLÍCITO — jamás el 307 default
```

- Frontend [VERIFIED: docs/05_desarrollo/guia-04-catalogo.md:760]: `const base = import.meta.env.VITE_API_URL ?? "";` — vacío en dev (el proxy `/api` de Vite hace el trabajo [VERIFIED: guia-02:142-147 `server: { proxy: { "/api": "http://localhost:8000" } }`]), URL pública en producción [VERIFIED: guia-02:416-418].

**When to use:** tablas de env vars de los dashboards (Render: `BACKEND_URL`, `CORS_ORIGINS`, `SECRET_KEY`, `ADMIN_*`, `CLIENTE_*`, `GROQ_API_KEY`, `DATABASE_URL` opcional, `PYTHON_VERSION`; Vercel: `VITE_API_URL`).

| Env var | Plataforma | Valor de producción (ejemplo taller) | Efecto |
|---------|-----------|--------------------------------------|--------|
| `PYTHON_VERSION` | Render | `3.12.10` (fully-qualified) | Fija Python 3.12 — el techo del SDK Transbank; sin ella Render usa 3.14.3 [CITED: render.com/docs/python-version] |
| `BACKEND_URL` | Render | `https://<servicio>.onrender.com` (sin slash final) | Congela el `return_url` de Webpay |
| `CORS_ORIGINS` | Render | `["https://<proyecto>.vercel.app"]` — JSON array | CORS de producción Y el destino del 302 (`cors_origins[0]`) |
| `VITE_API_URL` | Vercel (Production) | `https://<servicio>.onrender.com` (sin slash final) | Base URL horneada al build — `fetch(\`${base}/${ruta}\`)` |
| `SECRET_KEY`, `ADMIN_*`, `CLIENTE_*`, `GROQ_API_KEY` | Render | los mismos del `.env` local (nuevo `SECRET_KEY` digno de producción) | Los settings sin default siguen fail-fast |

**Nota de nombres:** pydantic-settings mapea `backend_url`→`BACKEND_URL` y `cors_origins`→`CORS_ORIGINS` automáticamente (mayúsculas). La discreción del CONTEXT sobre nombres queda así resuelta: **los nombres ya están fijados por el código existente** — inventar otros rompería contra lo construido.

### Pattern 2: Fallback SPA en Vercel (DEPL-02)

**What:** Vercel no adivina que el proyecto es SPA — hay que decírselo con un `vercel.json` commiteado en la raíz del proyecto [CITED: vercel.com/kb/guide/why-is-my-deployed-project-giving-404]:

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

**When to use:** guía de deploy del frontend. El router de la SPA es `BrowserRouter` de react-router v8 [VERIFIED: guia-02:234 `import { BrowserRouter, Routes, Route } from "react-router";` — v8 eliminó `react-router-dom`], así que TODAS las rutas (`/carro`, `/pago/resultado`, `/admin`, `/historial`) viven solo en el cliente: el refresh pide el path al servidor y sin rewrite da 404. Gotchas citados por la KB: el archivo debe estar commiteado en Git (si no, el rewrite silenciosamente no aplica) y el Framework Preset no debe quedar en "Other".

### Pattern 3: API en Render con uv + seed al build

**What:** El taller ya es un proyecto uv (`backend/pyproject.toml` con `requires-python = ">=3.12,<3.13"` + `backend/uv.lock` [VERIFIED: leídos directo]). Render lo soporta nativo: incluir `uv.lock` habilita uv "in place of pip for your service's build command and other scripts" [CITED: render.com/changelog/added-uv-to-the-python-native-runtime]. Configuración del Web Service:

| Campo | Valor (candidato — el spike lo firma → [D-73: firmado documentalmente en ADR-019/guia-16]) |
|---|---|
| Root Directory | `backend` (el taller es monorepo) |
| Environment | Python 3 (`PYTHON_VERSION=3.12.x` fully-qualified) |
| Build Command | `uv sync --locked && uv run python -m app.seed` — seed idempotente (D-05) restaurando el catálogo en cada deploy, patrón del Paso 3 de demo-cine (`&& python semilla.py`) |
| Start Command | `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT` — la forma oficial Render es `uvicorn main:app --host 0.0.0.0 --port $PORT` [CITED: render.com/docs/deploy-fastapi] adaptada al `app/` y uv del taller |

El comando del seed es el canónico de la serie [VERIFIED: guia-03:263/509 `uv run python -m app.seed`]. guia-01:332 ya prometió esta pieza: el equivalente de producción "`fastapi run`, sin recarga) llegará en la fase de..." — la guía de deploy la cumple (con uvicorn directo, que es lo que Render necesita por `$PORT`).

**When to use:** guía de deploy del API + doc 07. El exacto comportamiento del build uv (si `uv sync` solo basta, si exige `--locked`) es pregunta del spike — el changelog no literaliza el comando. **[Actualización D-73: sin spike — la variante candidata de la tabla (Build `uv sync --locked && uv run python -m app.seed` / Start `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`) se enseña como CANÓNICA en guia-16 citando las fuentes oficiales; A3 queda supuesto señalado y la confirmación runtime es del alumno.]**

### Pattern 4: Spike-first con evidencia (D-72 replica D-38/D-41) — **[SUPERSEDED por D-73: ver nota en "When to use"]**

**What:** El spike de la fase 3 (`03-SPIKE-RETORNO.md`, leído) fijó el molde: frontmatter con `status/phase/verified_by`, sección "Cómo se corrió (para reproducir)", tests con `expected` (según docs) / `result` (pass con correcciones materiales si las hay) / `evidence` (evidencia textual), hallazgos que las docs no dicen. El spike de deploy replica esa disciplina con: deploy de ambos tiers, 4 flujos contra el ambiente desplegado, cronómetro de spin-down (15 min según doc [CITED: render.com/docs/free]; wake ~1 min), qué queda en `maura.db` tras un wake, y gotchas de cuentas/verificación humana.

**When to use:** PRIMER plan de la fase (D-72); sus hallazgos citan ADR-019 y doc 07. **[SUPERSEDED por D-73: NO existe plan de spike — la fase abre con los ADRs 019/020 + doc 07 a evidencia documental (plan 05-01). El molde de `03-SPIKE-RETORNO.md` se conserva solo como referencia de formato de hallazgos; el cronometraje y los 4 flujos contra el ambiente desplegado los corre el alumno (guia-18).]**

### Pattern 5: Cierre documental con formato demo-cine (D-71)

**What:** Los tres docs de cierre de demo-cine (leídos completos) comparten molde: cabecera blockquote (Fase del ciclo / Qué construirás hoy / Al terminar tendrás / Necesitas / Decisión de fondo=ADR / Fecha), "Los términos de hoy" en tabla, pasos numerados con 🧠 narrando decisiones, tabla de "Errores típicos" (demo-cine 07 la tiene — PERFECTA para el deploy), ✅ verificación con columna Origen, 📝 punto de control, "Lo que acabas de aprender", enlace final. La diferencia de fondo (y la lección de la serie): demo-cine 07 deployó sobre **Postgres persistente de Neon** con "la lección del disco efímero" como gotcha de carátulas; demo-carro deploya sobre **SQLite efímero por diseño (D-70)** — el doc 07 debe enseñar el trade-off como decisión (ADR-020), citando que las docs de Render nombran textualmente "local SQLite databases" entre lo que se pierde [CITED: render.com/docs/free].

**When to use:** docs 06/07/08. 06 NO es una suite pytest nueva (esa es la de demo-cine): es la síntesis del método ya vivido (mini-verificación por paso, Gran verificación final por fase, verificación runtime contra servicios reales — D-71 literal).

### Anti-Patterns to Avoid

- **Hardcodear URLs de producción en el código de las guías:** las URLs públicas son por-alumno (subdominios generados por plataforma); siempre env vars (`backend_url`, `cors_origins`, `VITE_API_URL`), nunca literales en `config.py` ni `api.ts`.
- **Comodín de CORS "para que funcione en producción":** la serie ya lo vetó ("siempre lista explícita — jamás comodín" [VERIFIED: guia-05:813]); el deploy cambia el VALOR de la lista, no la regla.
- **Enseñar las dos plataformas por tier (menú de opciones):** D-69 lo veta pedagógicamente — un solo camino por tier; las alternativas viven en el ADR-019 como opciones descartadas.
- **Bumpar el contrato 0.4.0 "por la fase nueva":** el deploy no cambia paths, schemas ni copys (D-66: no bump sin churn real) — el planner confirma.
- **Poner `maura.db` en git para "pre-poblar" producción:** el seed del build lo crea; el `.gitignore` del taller ya lo excluye (`*.db` [VERIFIED: maura-uat/backend/.gitignore]).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Fallback de rutas SPA | Middleware/404 custom, `try_files` casero | `vercel.json` rewrites | Configuración declarativa de la plataforma; cubre TODAS las rutas de una vez [CITED: vercel.com KB] |
| Certificados HTTPS | Certbot/proxy propio | TLS incluido de Vercel/Render | Requisito SSL del `return_url` cubierto por diseño; hand-roll es días de trabajo y un riesgo |
| CI/CD | Scripts de deploy propios | Git-connected de las plataformas | `git push` → build+deploy automático; demo-cine ya lo enseñó como "CI/CD en chico" |
| Restaurar la BD tras spin-down | Cron de re-seed, endpoint admin de seed | Seed idempotente en el Build Command | El upsert ya converge (D-05/06/07); re-seedear en cada deploy es gratis — patrón demo-cine Paso 3 |
| Monitoreo/health checks custom | Endpoint de estado ad-hoc | `/api/salud` ya existe + logs del dashboard | doc 08 lo cubre documentalmente (deferred: uptime alerts) |

**Key insight:** Todo lo que el deploy parece "requerir nuevo" ya fue parametrizado por las guías anteriores con ese fin explícito — `backend_url` ("la fase 5 la congelará junto con el origen público" [VERIFIED: guia-09:600-601 y config.py del taller]), `VITE_API_URL` ("la URL pública de la API en producción (fase de despliegue)" [VERIFIED: guia-02:417-418]) y `cors_origins`. La fase 5 es la que COBRA esas promesas: configura, no construye.

## Common Pitfalls

### Pitfall 1: Python default de Render (3.14.3) vs techo del SDK Transbank (3.12)
**What goes wrong:** Sin `PYTHON_VERSION`, un Web Service nuevo en Render arranca con el default actual 3.14.3 [CITED: render.com/docs/python-version]; el `uv sync` falla contra `requires-python = ">=3.12,<3.13"` del taller, o peor: con pip y requirements sin pin, instalaría deps fuera del techo declarado del SDK de Transbank (classifiers 3.8–3.12, STACK.md).
**Why it happens:** El default de Render cambia por fecha de creación del servicio; nadie lo configura hasta que revienta.
**How to avoid:** `PYTHON_VERSION=3.12.x` fully-qualified (la doc exige versión completa, ej. `3.12.10`) o `.python-version` en la raíz del repo (admite sin patch). El build del guía lo enseña como paso con mini-verificación (el log del build muestra la versión).
**Warning signs:** Build muere en `uv sync` con "requires-python" o resuelve para Python 3.14.

### Pitfall 2: maura-uat no es repositorio git (bloqueador del spike)
**What goes wrong:** Ambas plataformas deployan desde un repo Git (GitHub/GitLab/Bitbucket); `D:/Repos/maura-uat` hoy NO es repo (verificado: "fatal: not a git repository") y `gh` CLI no está instalado (verificado).
**Why it happens:** El taller se construyó copiando bloques de las guías, sin git init.
**How to avoid:** Paso 0 del spike: `git init` + commit + crear repo GitHub (vía web — sin gh) + push. Los `.gitignore` del taller ya protegen `.env` y `*.db` [VERIFIED: maura-uat/backend/.gitignore]. La nota operativa del CONTEXT aplica: si crear el repo/pushear exige credenciales, el usuario participa en ese paso. **[Actualización D-73: el "paso 0 del spike" es hoy el Paso 0 de guia-16 — lo corre el ALUMNO sobre su propio proyecto; maura-uat no se deploya en esta fase.]**
**Warning signs:** El import de repo en Vercel/Render no encuentra el proyecto.

### Pitfall 3: `VITE_API_URL` se hornea al build (y el doble slash)
**What goes wrong:** (a) Cambiar `VITE_API_URL` en Vercel SIN redeploy no hace nada — el valor se sustituye estáticamente al build [CITED: vite.dev/guide/env-and-mode: "statically replaced at build time"]. (b) `api.ts` concatena `` `${base}/${ruta}` `` [VERIFIED: guia-04:762-763], así que un valor CON slash final produce `https://api...com//api/...`.
**Why it happens:** Es la naturaleza del reemplazo estático de Vite; el trailing slash es un descuido clásico de dashboards.
**How to avoid:** Enseñar el valor SIN slash final y que todo cambio de env en Vercel exige redeploy (mini-verificación: grepear el bundle `dist/` por la URL pública — natural extensión del grep AIAS-03 que guia-15 ya instauró).
**Warning signs:** La SPA en producción pide a localhost:5173/8000 o aparece `//api` en Network.

### Pitfall 4: `CORS_ORIGINS` debe ser JSON array (o `Settings()` revienta)
**What goes wrong:** pydantic-settings trata los valores de tipos complejos (list/dict/submodelos) como strings JSON: "Complex types like `list`, `set`, `dict`, and sub-models are populated from the environment by treating the environment variable's value as a JSON-encoded string" y un valor no-JSON "raises a `SettingsError`" [CITED: pydantic.dev/docs/validation/latest/concepts/pydantic_settings]. Si el alumno pone `CORS_ORIGINS=https://tienda.vercel.app` (sin corchetes), la app NO PARTE.
**Why it happens:** En dev nunca se seteó (default `["http://localhost:5173"]`); la primera vez que se escribe como env var es en el dashboard de Render.
**How to avoid:** La guía enseña el valor exacto `["https://<proyecto>.vercel.app"]` con corchetes y comillas, y lo conecta con el fail-fast de `secret_key` ya aprendido (mismo mecanismo, mismo diagnóstico: el log del arranque). Mini-verificación: el log de Render muestra el arranque limpio y el preflight de guia-05 contra el origen público.
**Warning signs:** "error parsing value for field cors_origins from source EnvSettingsSource" en el log de Render.

### Pitfall 5: El disco efímero borra lo runtime, no lo del build (la lección D-70 — hay que contarla bien)
**What goes wrong:** Malentender QUÉ se pierde: los cambios al filesystem (datos creados en runtime — pedidos, cuentas nuevas) "are lost" en redeploy/restart/spin-down, y las docs nombran textualmente "local SQLite databases" [CITED: render.com/docs/free]. La imagen del build (con el seed ya corrido) es la que revive en cada wake — el catálogo SEMPRE vuelve; el historial de pedidos de la clienta NO.
**Why it happens:** La tentación es decir "la BD se pierde" sin distinguir build-time vs runtime — y el alumno no entiende por qué el catálogo sigue ahí tras un spin-down pero su pedido desapareció.
**How to avoid:** Doc 07/ADR-020 y la guía lo explican en dos capas (build-time siembrebra → runtime vive hasta el próximo ciclo). El spike lo CORROBORA con evidencia: crear un pedido, forzar spin-down (esperar 15 min o redeploy), despertar, observar catálogo restaurado + pedido ido. Es la "lección del disco efímero" de demo-cine, ahora en el dato y no en la carátula. **[Actualización D-73: esa corroboración la corre el ALUMNO (Paso 6 de guia-18, fila "ciclo efímero" de la Gran verificación final); A5 queda supuesto señalado — ADR-020/doc 07 firman la lección con la cita documental de render.com/docs/free.]**
**Warning signs:** Alguien promete persistencia "porque el seed corre en cada deploy".

### Pitfall 6: El flujo timeout (10 min) contra el spin-down (15 min) y el cold start
**What goes wrong:** Dos relojes de Webpay: el token vive 5 minutos desde el create [CITED: transbankdevelopers.cl/documentacion/webpay-plus] y el timeout del form es "de 10 minutos en integración" (4 en producción). El spin-down de Render llega a los 15 min sin tráfico — el create "resetea" la ventana, así que el retorno del timeout (t+10) llega dentro de la ventana despierta. PERO la primera visita de la mañana (SPA fría) espera el wake de ~1 min con página de carga [CITED: render.com/docs/free], y si algo duerme en el camino, el retorno puede pegar contra un servicio despertando (~1 min de latencia extra).
**Why it happens:** Interacción de tres relojes que ninguna doc única describe.
**How to avoid:** La guía lo nombra honestamente (el specifics del CONTEXT ya lo pide: "la primera request tras el sueño arranca fría"). El spike mide: primera request tras spin-down (cuánto), y un retorno contra servicio despierto. **[Actualización D-73: sin cronometraje del proyecto — las cifras se citan "a la fecha" de render.com/docs/free (A8 supuesto señalado); el alumno puede cronometrarlo al correr guia-18.]**
**Warning signs:** Retorno de Webpay "lento" pero funcional — no es bug, es el tier gratis.

### Pitfall 7: `vercel.json` que no aplica (ubicación y preset)
**What goes wrong:** El rewrite silenciosamente no aplica si el archivo no está commiteado en la raíz que Vercel usa (o con Root Directory configurado, en la raíz del proyecto importado), o si el Framework Preset quedó "Other" [CITED: vercel.com/kb/guide/why-is-my-deployed-project-giving-404].
**Why it happens:** Vercel sirve lo que el deploy construyó; un archivo local no pusheado no existe para la plataforma.
**How to avoid:** La guía coloca `vercel.json` junto a `package.json` del frontend (raíz del proyecto Vercel), lo commitea, y la mini-verificación ES el refresh de una ruta profunda (`/carro` → 200 con la SPA, no 404).
**Warning signs:** Funciona navegando desde `/` pero 404 al refresh/deep-link — el síntoma exacto de DEPL-02 sin configurar.

### Pitfall 8: Las docs de Transbank dicen POST (integración) pero el runtime habló GET
**What goes wrong:** La doc oficial dice que el flujo abortado en integración llega por POST — el spike de la fase 3 lo observó por GET (corrección material ya canónica en ADR-012, endpoint GET+POST inmune por diseño).
**Why it happens:** Divergencia doc/comportamiento ya documentada en la serie; en el ambiente desplegado puede repetirse en cualquier flujo.
**How to avoid:** El endpoint GET+POST con discriminador por presencia de params ya está construido (ADR-012); el spike de deploy solo re-verifica los 4 flujos contra las URLs públicas SIN cambiar el código. **[Actualización D-73: esa re-verificación la define guia-18 y la corre el alumno contra SU ambiente desplegado; cualquier sorpresa se registra como hallazgo con la regla de fix en ambos lugares.]**
**Warning signs:** Cualquier sorpresa de método/params en el retorno desplegado → se registra como hallazgo, no se improvisa fix.

### Pitfall 9: `SECRET_KEY` de producción "heredada" del `.env` de dev
**What goes wrong:** Copiar la misma `SECRET_KEY` del taller al dashboard: funciona, pero enseña mal — los tokens firmados con la key local valen en producción.
**Why it happens:** Prisa del primer deploy.
**How to avoid:** La guía genera una key nueva para producción (`python -c "import secrets; print(secrets.token_hex(32))"` — el mismo comando que demo-cine 07 enseña) y narra por qué (los JWT de dev no deben valer afuera).
**Warning signs:** La única diferencia entre `.env` local y dashboard es la URL.

## Code Examples

### vercel.json (fallback SPA — DEPL-02)
```json
// Fuente: vercel.com/kb/guide/why-is-my-deployed-project-giving-404 (cita textual del rewrite)
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

### Configuración del Web Service en Render (candidato — el spike la firma → [D-73: canónica documental, enseñada en guia-16])
```text
Fuente: render.com/docs/deploy-fastapi (build/start oficiales) + render.com/changelog/added-uv-to-the-python-native-runtime (uv nativo)
+ taller maura-uat (estructura real, leída)

Root Directory:  backend
Runtime:         Python 3 (PYTHON_VERSION=3.12.x fully-qualified)
Build Command:   uv sync --locked && uv run python -m app.seed
Start Command:   uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT
Instance Type:   Free
Env vars:        PYTHON_VERSION, BACKEND_URL, CORS_ORIGINS, SECRET_KEY,
                 ADMIN_EMAIL, ADMIN_PASSWORD, CLIENTE_EMAIL, CLIENTE_PASSWORD,
                 GROQ_API_KEY (opcional — la tienda degrada sin ella, D-61)
```
Referencia oficial del start: "uvicorn main:app --host 0.0.0.0 --port $PORT" [CITED: render.com/docs/deploy-fastapi]; el `uv run` envuelve según el soporte uv nativo ("use uv in place of pip for your service's build command and other scripts" [CITED: render.com/changelog]).

### La cadena congelada (lo que la Gran verificación final de fase 5 traza)
```python
# Fuente: docs/05_desarrollo/guia-09-ordenes-webpay.md:685, 1053-1054 (VERIFICADO — byte-exacto)
return_url=f"{settings.backend_url}/api/pago/retorno",          # ida: API pública
url = f"{settings.cors_origins[0]}/pago/resultado?{urlencode(params)}"
return RedirectResponse(url, status_code=302)                    # vuelta: SPA pública
```
```ts
// Fuente: docs/05_desarrollo/guia-04-catalogo.md:760-763 (VERIFICADO — byte-exacto)
const base = import.meta.env.VITE_API_URL ?? "";
export async function apiGet<T>(ruta: string): Promise<T> {
  const res = await fetch(`${base}/${ruta}`);
```

### Env vars de producción (tablas que las guías 16+ enseñan)
```bash
# Render (API) — CORS_ORIGINS es JSON array o Settings() revienta (Pitfall 4)
BACKEND_URL=https://<servicio>.onrender.com
CORS_ORIGINS=["https://<proyecto>.vercel.app"]
PYTHON_VERSION=3.12.10            # fully-qualified (render.com/docs/python-version)
SECRET_KEY=<nueva, python -c "import secrets; print(secrets.token_hex(32))">
# ... ADMIN_EMAIL/ADMIN_PASSWORD/CLIENTE_EMAIL/CLIENTE_PASSWORD/GROQ_API_KEY

# Vercel (SPA) — scope Production; todo cambio exige redeploy (Pitfall 3)
VITE_API_URL=https://<servicio>.onrender.com   # SIN slash final
```

### Molde de cabecera de los docs de cierre (formato demo-cine, leído)
```markdown
# Fase 7 — Guía de Despliegue: el gran final (gratis)     ← demo-cine 07:1
> **Módulos:** ISI601 / ISI602 · **Fase del ciclo de vida:** 7. Despliegue
> **Qué construirás hoy:** la publicación real...
> **Decisión de fondo:** ADR-007 (Render + Neon).
```
demo-carro 07 ancla "Decisión de fondo: ADR-019 (Vercel + Render)" y su tabla de términos ya tiene candidatos leídos de demo-cine: Build, Start command, Variable de entorno (en producción), Cold start / hibernación, Disco efímero — más los propios: fallback SPA/rewrite, env var horneada (VITE_*), seed idempotente.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Render solo pip + requirements.txt | Runtime nativo de Python con uv (habilitado por `uv.lock` en la raíz) | 2025-06-12 [CITED: render.com/changelog] | El taller deploya SIN generar requirements.txt; pero uv NO fija la versión de Python — `PYTHON_VERSION` sigue siendo obligatorio |
| Default de Python en Render 3.11/3.13 | 3.14.3 para servicios nuevos (historial: 3.13.4 jun2025–feb2026) | feb 2026 [CITED: render.com/docs/python-version] | Sin `PYTHON_VERSION=3.12.x` el deploy choca con el techo del SDK Transbank (Pitfall 1) |
| "Free tier sin límites visibles" | Hobby: 100 GB transfer/mes, 100 deploys/día, uso no-comercial explícito; Render Free: 750 h/mes, spin-down 15 min, wake ~1 min | docs vigentes oct-2026 | Las cifras del doc 07/guías se citan con URL y "a la fecha" (misma vara que D-68 con Groq) |
| Heroku free (el clásico docente) | Cerrado en 2022; el consenso actual es static (Vercel/Netlify/CF Pages) + Render free | 2022→ | STACK.md ya documentó el consenso; demo-cine ya migró a Render |

**Deprecated/outdated:**
- Heroku free tier: desaparecido — no citar como opción.
- `react-router-dom` como paquete separado: eliminado en v8 [VERIFIED: guia-02:223-224] — el import es `from "react-router"`; guías de deploy no deben introducirlo de vuelta.

## Assumptions Log

> **[Actualización D-73:** el spike D-72 — mecanismo de confirmación citado en las filas A1/A2/A3/A5/A7/A8 — fue superseded: la confirmación runtime de estos supuestos es del ALUMNO al seguir las guías 16-18. Los supuestos quedan señalados (flagged) en los planes donde corresponde (05-04/05-05).**]

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Vercel Hobby se registra y deploya sin tarjeta (docs: free, tarjeta solo al subir a Pro; flujo de signup no corrido) | Standard Stack | El spike lo detecta en minutos; nota operativa del CONTEXT cubre la participación del usuario |
| A2 | Render Free crea servicios sin tarjeta (docs: sin payment method el exceso SUSPENDE en vez de cobrar — implica que operar sin tarjeta es posible; no es una declaración afirmativa de registro sin tarjeta) | Standard Stack | Igual que A1 — el spike responde con evidencia |
| A3 | El Build Command exacto con uv es `uv sync --locked && uv run python -m app.seed` y el Start `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT` — el changelog confirma uv nativo pero NO literaliza los comandos | Pattern 3 | Variante menor (flags de uv sync, `.venv/bin/uvicorn` directo); el spike la fija antes de las guías |
| A4 | Webpay integración acepta `*.onrender.com` como `return_url` (URL pública con SSL válido ≤ 255 chars cumple el requisito documentado; subdominios de plataforma no probados runtime contra Transbank) | DEPL-02 | Riesgo bajo (el requisito documentado es SSL+público); el spike lo corrobora con el flujo aprobado real |
| A5 | Tras un spin-down, el servicio revive desde la IMAGEN del build (catálogo sembrado presente, datos runtime ausentes) — las docs dicen que los cambios al filesystem se pierden, pero el detalle de qué revive es interpretación | Pitfall 5 | Si el wake re-corriera el build o vaciara la BD, la lección D-70 cambia de matiz; el spike lo observa directamente |
| A6 | "Uso no-comercial" de Vercel Hobby admite una tienda ficticia educativa sin transacciones reales (sandbox) — interpretación de fair use, no un dictamen | Standard Stack | Riesgo bajo para el aula; el doc 07 lo declara honestamente (PYME ficticia, pagos sandbox) |
| A7 | El repo GitHub del taller se crea vía web (gh CLI ausente, verificado) y el push funciona con las credenciales git del usuario; el usuario participa si hay fricción de cuentas | Pitfall 2 / Environment | Paso bloqueante del spike — detectado temprano por diseño (D-72) |
| A8 | Los 15 min de spin-down y ~1 min de wake aplican al taller tal cual (cifras de docs oficiales, no cronometradas en este entorno) | Pitfall 6 | El spike cronometra y firma las cifras que las guías citan (misma vara que D-68) |

## Open Questions (RESOLVED)

> **[Nota de resolución (2026-10-01):** las cinco preguntas quedan RESUELTAS bajo D-73 (la fase es solo escritura — sin spike runtime) y las decisiones del planner ya tomadas en los planes 05-01..05-05. La disposición de cada una sigue a su "Recommendation" original. Ninguna queda abierta.]**

1. **¿Cuál es el build/start command uv exacto que Render ejecuta bien para ESTE taller?**
   - What we know: uv nativo habilitado por `uv.lock` [CITED: changelog]; start oficial `uvicorn ... --port $PORT` [CITED: deploy-fastapi]; el taller es `app.main:app` con uv.
   - What's unclear: si `uv sync` solo basta, si `--locked`/`--frozen` van mejor, y si `uv run uvicorn` hereda bien `$PORT`.
   - Recommendation: el spike prueba la variante candidata (Pattern 3) y documenta el delta; las guías citan LO QUE CORRIÓ.
   - **[RESOLVED (D-73): esa recomendación quedó inejecutable y NO se aplicó — sin spike, las guías NO citan "lo que corrió". Disposición: la variante candidata del Pattern 3 (Build `uv sync --locked && uv run python -m app.seed` / Start `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`) se enseña como CANÓNICA en guia-16 (plan 05-03) citando las fuentes oficiales (render.com/docs/deploy-fastapi + changelog uv); la confirmación runtime es del alumno (A3 queda supuesto señalado).]**
2. **¿Qué contiene exactamente `maura.db` tras un spin-down + wake?**
   - What we know: filesystem changes lost en redeploy/restart/spin-down [CITED: render.com/docs/free]; el seed corre al build.
   - What's unclear: si el wake monta la imagen del build tal cual (A5).
   - Recommendation: test explícito del spike (crear pedido → forzar ciclo → observar); alimenta ADR-020 y la "lección del disco efímero" de la guía.
   - **[RESOLVED (D-73): el test lo corre el ALUMNO como Paso 6 de guia-18 (fila "ciclo efímero" de la Gran verificación final); mientras tanto queda como supuesto A5 señalado — ADR-020 y doc 07 firman la lección con la cita documental de render.com/docs/free.]**
3. **¿Exige alguna plataforma verificación humana/tarjeta en el flujo de registro 2026?**
   - What we know: docs dicen free sin tarjeta (con los matices A1/A2).
   - What's unclear: el flujo de signup real para cuentas nuevas del taller.
   - Recommendation: nota operativa del CONTEXT ya lo contempla — el usuario participa en ese paso puntual si aparece.
   - **[RESOLVED (D-73): sin runtime del proyecto — queda en los supuestos A1/A2 señalados; guia-16/17 enseñan el registro sin tarjeta citando las docs oficiales, y si el flujo del ALUMNO exigiera verificación humana, la guía lo declara y remite a la doc oficial.]**
4. **¿Fila RNF de despliegue en docs/02 o solo doc 07?**
   - What we know: discreción anotada del CONTEXT; P1 "que se abra desde cualquier dispositivo" es el ángulo narrativo; P1-P8 cubiertas.
   - Recommendation: doc 07 como hogar natural (DEPL es infraestructura del ciclo); si el planner añade RNF, que sea UNA (URL pública HTTPS) trazada a P1 — no renumerar series.
   - **[RESOLVED (planner): doc 07 como hogar del deploy — SIN RNF nueva en docs/02 (P1-P8 ya cubiertas; P1 queda como ángulo narrativo del doc 07); ninguna serie se renumera.]**
5. **¿Sube el contrato a 0.5.0?**
   - Recommendation del research: NO (D-66 — el deploy no toca paths/schemas/copys; la fila contrato ↔ `/docs` de la Gran verificación final sigue contra 0.4.0 en la URL pública). El planner confirma.
   - **[RESOLVED (planner, confirmado): NO sube — el contrato queda 0.4.0 (D-66); los planes 05-01/05-04 lo fijan con gate negativo (0.5.0 vetado) y la fila contrato ↔ `/docs` de guia-18 sigue contra 0.4.0 en la URL pública.]**

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js (taller frontend) | build de la SPA en Vercel | ✓ (remoto) / ✓ local | v24.21.0 en taller [VERIFIED: vite --version local]; Vercel build usa su runtime | — |
| uv | backend del taller + build Render | ✓ local / ✓ Render nativo | 0.9.3 (spike fase 3) / nativo vía uv.lock [CITED] | pip + requirements.txt exportado (`uv export`) |
| Python 3.12 | API | ✓ (Render pinneable) | `PYTHON_VERSION=3.12.x` [CITED] | — (3.13/3.14 vetados por Transbank) |
| Git repo del taller + remote GitHub | deploy Git-connected de AMBAS plataformas | ✗ — maura-uat NO es repo git (verificado); gh CLI ausente | — | `git init` + repo vía web + push (paso 0 del spike → [D-73: hoy Paso 0 de guia-16, corrido por el ALUMNO sobre su proyecto]); alternativa CLI (vercel) solo como plan B |
| Cuenta Vercel (Hobby) | hosting frontend | ✗ (se crea en el spike → [D-73: la crea el ALUMNO en guia-17]) | — | Netlify/CF Pages si apareciera evidencia documental en contra (D-69/D-73) |
| Cuenta Render (Free) | hosting API | ✗ (se crea en el spike → [D-73: la crea el ALUMNO en guia-16]) | — | Fly.io/Railway ídem |
| Webpay integración | 4 flujos en producción | ✓ (público, sin registro) | comercio 597055555532 (STACK.md/spike fase 3) | — |
| Groq API key | asistente en producción | ✓ (.env del taller) | key existente | Opcional por diseño (D-61: tienda degrada sin key) |

**Missing dependencies with no fallback:** ninguna bloqueante — el gap git/GitHub del taller es un paso 0 conocido del spike (Pitfall 2), no un bloqueador de planning. **[Actualización D-73: hoy es el Paso 0 de guia-16, corrido por el alumno sobre su proyecto.]**
**Missing dependencies with fallback:** cuentas de plataforma (se crean — por el ALUMNO, guia-16/17; sustituibles con evidencia según D-69/D-73).

## Security Domain

`security_enforcement: true`, `security_asvs_level: 1` (config.json leído). Fase documental + spike runtime; no hay código de aplicación nuevo. **[Actualización D-73: sin spike runtime — fase solo documental; el runtime del deploy es del alumno.]**

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes (heredado) | JWT login existente (guia-05/06); el deploy no cambia auth — reuso tal cual |
| V3 Session Management | yes (heredado) | Bearer token, `token_dias = 7`; sin cookies → sin CSRF de cookies; localStorage documentado en ADR-009 |
| V4 Access Control | yes (heredado) | `get_current_admin` en cada endpoint admin (ADR-015); `/docs` público con Authorize — igual que en dev, ahora en URL pública |
| V5 Input Validation | yes (heredado) | Pydantic en el contrato 0.4.0; el retorno Webpay discrimina por presencia de params (ADR-012) |
| V6 Cryptography | yes (heredado) | pwdlib[argon2] + PyJWT HS256; TLS lo aportan las plataformas (jamás hand-roll) |
| V14 Config Management | yes (NUEVO en esta fase) | Todos los secretos por env vars de plataforma (jamás en código/bundle); `SECRET_KEY` nueva por entorno (Pitfall 9); `VITE_*` solo lleva URLs públicas |

### Known Threat Patterns for deploy de dos tiers free

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Secretos en el bundle del frontend | Information Disclosure | Solo `VITE_API_URL` (pública) cruza al build; grep del build `GROQ_API_KEY` → CERO (guia-15 lo instaura; la Gran verificación final lo re-corre contra el build de producción) |
| `/docs` y `/redoc` públicos en la URL de la API | Information Disclosure | Decisión pedagógica deliberada (fila contrato ↔ `/docs` de la serie); doc 07 lo declara como trade-off del aula — en un producto real se desactivaría |
| Credenciales seed débiles en producción | Spoofing | Guía enseña `ADMIN_PASSWORD` digna + `SECRET_KEY` nueva por entorno (Pitfall 9); fail-fast ya existe |
| CORS comodín para "arreglar" producción | Elevation of Privilege | Lista explícita JSON (`CORS_ORIGINS`) — regla de la serie (guia-05), el deploy solo cambia el valor |
| `return_url` manipulado / retorno forjado | Tampering | Endpoint público GET+POST que JAMÁS confía en el navegador: el estado real lo decide el `commit` del token (PAY-03, ADR-012); idempotencia OUR-side ya construida |
| Cold start como vector de confusión (¿caída?) | Denial of Service (percebido) | Doc 07/guía lo nombran honestamente (~1 min, página de carga) — diagnóstico, no bug (Pitfall 6) |

## Sources

### Primary (HIGH confidence — in-repo, leído directo esta sesión)
- `D:/Repos/maura-uat/backend/app/config.py` — Settings completo (10 campos verbatim, `SettingsConfigDict(env_file=".env")`)
- `D:/Repos/maura-uat/backend/pyproject.toml` + `uv.lock` — `requires-python = ">=3.12,<3.13"`, deps con pins de la serie
- `D:/Repos/maura-uat/frontend/package.json` + `vite.config.ts` — scripts (`tsc -b && vite build`), proxy `/api`, react-router ^8.4.0
- `D:/Repos/maura-uat/backend/.gitignore` — `.env` y `*.db` excluidos; taller NO es repo git (verificado)
- `docs/05_desarrollo/guia-09-ordenes-webpay.md:580-603, 685, 1042-1054` — `backend_url`, `return_url`, `_hacia_spa` 302
- `docs/05_desarrollo/guia-04-catalogo.md:760-763` — `import.meta.env.VITE_API_URL ?? ""`
- `docs/05_desarrollo/guia-02-proyecto-frontend.md:142-147, 234, 416-418` — proxy Vite, BrowserRouter v8, VITE_API_URL dev/prod
- `docs/05_desarrollo/guia-05-cuentas-backend.md:813-819` + `guia-12-panel-backend.md:1028-1033` — CORS lista explícita, methods [GET,POST,PUT,PATCH]
- `docs/05_desarrollo/guia-03-modelos-y-seed.md:263, 509` — `uv run python -m app.seed`
- `docs/05_desarrollo/guia-01-proyecto-backend.md:328-340` — `fastapi dev` y la promesa de `fastapi run`/producción para fase 5
- `D:/Repos/demo-cine/docs/06_pruebas.md`, `07_despliegue.md`, `08_mantenimiento.md` — formato de cierre (leídos completos)
- `.planning/phases/03-checkout-webpay-y-rdenes/03-SPIKE-RETORNO.md` — molde del spike D-72 (leído)
- `docs/README.md` + `README.md` (raíz) — filas 6-8 ⏳ Pendiente, fila 5 Parcial (leídos)

### Secondary (MEDIUM — docs oficiales citadas)
- [vercel.com/kb/guide/why-is-my-deployed-project-giving-404](https://vercel.com/kb/guide/why-is-my-deployed-project-giving-404) — rewrite SPA explícito, vercel.json commiteado, preset "Other"
- [vercel.com/docs/plans/hobby](https://vercel.com/docs/plans/hobby) — Hobby free, no-comercial personal (fair use), límites mensuales
- [vercel.com/docs/frameworks/frontend/vite](https://vercel.com/docs/frameworks/frontend/vite) — env vars con prefijo VITE_ durante el build
- [vite.dev/guide/env-and-mode](https://vite.dev/guide/env-and-mode) — VITE_ prefix, `import.meta.env`, .env.production, "statically replaced at build time"
- [render.com/docs/free](https://render.com/docs/free) — 15 min spin-down, wake ~1 min, 750 h/mes, filesystem efímero citando "local SQLite databases"
- [render.com/docs/deploy-fastapi](https://render.com/docs/deploy-fastapi) — build/start commands uvicorn/$PORT oficiales
- [render.com/docs/python-version](https://render.com/docs/python-version) — PYTHON_VERSION fully-qualified, default actual 3.14.3
- [render.com/changelog/added-uv-to-the-python-native-runtime](https://render.com/changelog/added-uv-to-the-python-native-runtime) — uv nativo vía uv.lock (2025-06-12)
- [transbankdevelopers.cl/documentacion/webpay-plus](https://www.transbankdevelopers.cl/documentacion/webpay-plus) — 4 flujos con params, token 5 min de vida, response_code 0 + AUTHORIZED, timeout 4/10 min; requisito return_url SSL ≤ 255 chars (corroborado por búsqueda del mismo sitio + ya verificado en guia-09:488)
- [pydantic.dev/docs/validation/latest/concepts/pydantic_settings](https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/) — tipos complejos desde env como JSON; no-JSON → SettingsError

### Tertiary (LOW — search-only, para validación del spike) — [D-73: la validación runtime es del alumno; estas fuentes quedan como señal complementaria]
- Vercel "no credit card required" (vía vercel.com/pricing resumido por search, no leído directo)
- Medium/Reddit sobre uv+Render (solo como señal de que el patrón es común; el spike manda → [D-73: manda la confirmación del alumno])

## Metadata

**Validation Architecture:** OMITIDA — `workflow.nyquist_validation: false` explícito en `.planning/config.json` (leído). La verificación de planes es documental (greps/estructura) y el UAT runtime es delegado en maura-uat (AGENTS.md). **[Actualización D-73: el UAT runtime delegado en maura-uat NO aplica al deploy en esta fase — no hay UAT de despliegue; la verificación de la fase es documental y el runtime del deploy es del alumno (las reglas de fix en ambos lugares siguen vigentes solo ante bugs de guía).]**

**Runtime State Inventory:** OMITIDA — fase greenfield documental + spike; no es rename/refactor/migración. **[D-73: solo documental — sin spike]**

**Confidence breakdown:**
- Integraciones del repo (env vars, cadenas, comandos): HIGH — archivos fuente leídos directo con citas byte-exactas
- Plataformas (Vercel/Render): MEDIUM-HIGH — docs oficiales citadas; los comandos exactos uv quedan para el spike (A3) **[D-73: enseñados como canónicos en guia-16; confirmación runtime del alumno]**
- Cierre documental (formato demo-cine): HIGH — docs hermano leídos completos + tablas de estado actuales leídas
- Cifras free tier / comportamiento runtime (spin-down, wake, A5/A8): MEDIUM — docs citadas, cronometraje es del spike **[D-73: cronometraje opcional del alumno en guia-18]**

**Research date:** 2026-10-01
**Valid until:** 2026-10-15 (cifras de free tier y defaults de plataforma se mueven; ADR-019 debe citar "a la fecha" con URL — misma vara que D-68)
