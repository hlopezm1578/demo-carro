# Stack Research

**Domain:** Educational two-tier e-commerce (body splash store, fictional Chilean PYME) — React SPA + layered FastAPI + Webpay (Transbank) sandbox + Gemini AI assistant
**Researched:** 2026-09-28
**Confidence:** HIGH for version pins (verified against npm/PyPI registry APIs + GitHub + official docs the same day); MEDIUM for community-consensus opinions (state management, hosting), each tagged below.

**Runtime baselines (the two numbers that gate everything else):**

- **Python 3.12** for the backend. The Transbank SDK README states "Requisitos: Python 3.12+" and its classifiers stop at 3.12; SQLAlchemy 2.1 requires >=3.11; FastAPI 0.141 requires >=3.10. Python 3.12 is the only version declared supported by every dependency simultaneously.
- **Node.js 22 LTS (>= 22.22)** or Node 24. React Router 8 requires Node 22.22.0+ (its Vite-8 engines constraint `^20.19.0 || >=22.12.0` is looser — the router is the binding constraint).

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| React | 19.3.0 | UI (SPA) | Current stable; what `npm create vite` scaffolds (`react ^19.3.0`); satisfies React Router 8's 19.2.7+ baseline | HIGH (registry + official template) |
| Vite | 8.3.1 | Dev server + bundler | The SPA standard toolchain in 2026; Vite 8 is the current major (8.x line since Dec 2025). No Next.js server runtime needed for a pure SPA | HIGH (registry + template pin + engines on main) |
| TypeScript | ~6.0.2 | Static typing (frontend) | The official Vite react-ts template pins `typescript ~6.0.2` — follow the scaffold. npm `latest` is 7.0.2 (freshly stable native port) but the template hasn't moved yet; students get 6.x by default | HIGH (template on main inspected directly) |
| React Router | 8.4.0 | Client routing (library mode, `BrowserRouter`) | Current major (v8.0.0 released 2026-06-17, yearly cadence; v7 maintained in lockstep). v8 baselines React 19.2.7+/Vite 7+/Node 22.22+, ESM-only. Declarative/library mode is the right fit for a separate SPA | HIGH (registry + GitHub releases + changelog) |
| @tanstack/react-query | 5.104.0 | Server state (catalog, cart sync, orders) | 2026 consensus default for server state in new SPAs: caching, invalidation, retries — removes hand-rolled fetch logic | MEDIUM (registry HIGH; "default choice" is survey-backed consensus) |
| Zustand | 5.0.15 | Client state (cart, UI) | Most-downloaded dedicated state library of 2026; minimal boilerplate — ideal teaching surface vs Redux Toolkit | MEDIUM (registry HIGH; popularity claim survey-backed) |
| Tailwind CSS | 4.3.3 | Styling | v4 installs as a Vite plugin (`@tailwindcss/vite`), no `tailwind.config.js`, no PostCSS — one import line. Fast to teach, industry-standard utility CSS | HIGH (registry + official docs install guide) |
| FastAPI | 0.141.1 | REST API (layered backend) | Chosen by project constraints; current release 2026-07-29, Python >=3.10. Docs now teach uv-first workflow | HIGH (registry + official docs) |
| uvicorn | 0.54.0 | ASGI server | Ships inside `fastapi[standard]` (as `uvicorn[standard]`); nothing to decide separately | HIGH (registry) |
| SQLAlchemy | 2.1.1 | ORM (models layer) | Current 2.x line (2026-09-25), Python >=3.11. Declarative models + explicit `Session` per request is the mainstream layered-FastAPI pattern | HIGH (registry) |
| Alembic | 1.20.0 | Migrations | The SQLAlchemy migration tool; no credible alternative | HIGH (registry) |
| Pydantic | 2.13.5 | API schemas (contracts layer) | Bundled with FastAPI; Pydantic v2 schemas kept separate from ORM models keeps the layers pedagogically explicit | HIGH (registry) |
| pydantic-settings | 2.15.0 | Typed env config | Standard loader for `DATABASE_URL`, `GEMINI_API_KEY`, JWT secret — never hardcode secrets | HIGH (registry) |
| SQLite | stdlib (Python 3.12) | Default database | The official FastAPI SQL tutorial itself uses SQLite: zero setup, file-based, perfect for a classroom. SQLAlchemy makes the later switch to PostgreSQL a connection-string change | HIGH (official tutorial + multiple case studies) |
| transbank-sdk (Python) | 6.1.0 | Webpay Plus REST (integration env) | Official Transbank SDK, current (published 2025-06-24, unchanged). Integration credentials are public (commerce code 597055555532), SDK preconfigured for the integration environment. Uses sync `requests` — call it from sync `def` routes | HIGH (registry + GitHub README; matches PROJECT.md prior verification) |
| google-genai (Python) | 2.25.0 (pin `>=2.25,<3`) | Gemini AI sales assistant | Official SDK, current (2026-09-22), Python >=3.10. README advises pinning `< 3.0.0` (breaking changes planned for 3.x) | HIGH (registry + GitHub README; matches PROJECT.md) |
| PyJWT | 2.15.0 | JWT encode/decode (accounts) | What the current official FastAPI security tutorial uses; actively maintained (2.15.0 released 2026-09-23) | HIGH (official docs + PyPI) |
| pwdlib[argon2] | 0.3.1 | Password hashing | The official FastAPI tutorial's current choice (`PasswordHash.recommended()` = Argon2); replaces unmaintained passlib | HIGH (official docs + PyPI) |
| pytest | 9.1.1 | Backend tests | Current major (9.x since June 2026); FastAPI `TestClient` (httpx-based) makes API testing sync and simple | HIGH (registry) |

### Supporting Libraries

| Library | Version | Purpose | When to Use | Confidence |
|---------|---------|---------|-------------|------------|
| httpx | 0.28.1 | FastAPI `TestClient` transport | Comes with `fastapi[standard]` — no separate install needed for testing | HIGH |
| python-multipart | 0.0.32 | Form parsing | Needed for `OAuth2PasswordRequestForm` (login) and any admin image upload; included in `[standard]` | HIGH |
| email-validator | 2.3.0 | `EmailStr` validation | Included in `[standard]`; use for customer account emails | HIGH |
| @tailwindcss/vite | 4.3.3 | Tailwind Vite plugin | Always (same version line as tailwindcss) | HIGH |
| @vitejs/plugin-react | 6.1.1 | React fast refresh in Vite | Always (scaffold default) | HIGH |
| oxlint | ^1.85 | Frontend linter | Now the official Vite template default (replaces ESLint in the scaffold); use what `npm create vite` gives | MEDIUM (template on main; ecosystem transition still settling) |
| pytest-asyncio | 1.4.0 | Async test support | Only if the guide adopts async endpoints/tests — not needed with the sync-by-default recommendation below | MEDIUM |
| psycopg (binary: psycopg-binary) | 3.3.6 | PostgreSQL driver | Only in the PostgreSQL variant (see Stack Patterns) | HIGH (registry) |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| uv | Python project + dependency manager | The FastAPI official docs now teach `uv add ...` / `uv run fastapi dev`; fastest and most current convention. pip + venv works as the classroom fallback (`pip install "fastapi[standard]"` inside an activated venv) |
| `fastapi dev` / `fastapi run` (fastapi-cli) | Dev/prod server commands | Included via `fastapi[standard]`; `fastapi dev` for development, `fastapi run` for production |
| ruff | Python lint + format | Mainstream 2026 Python tooling; single tool replaces flake8+black+isort |
| Node 22 LTS / 24 | Frontend runtime | React Router 8 requires >= 22.22; check with `node -v` |
| Python 3.12 | Backend runtime | See runtime baselines above — the Transbank SDK compatibility ceiling |

## Installation

```bash
# Frontend (React SPA + TS + Tailwind)
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install react-router @tanstack/react-query zustand
npm install tailwindcss @tailwindcss/vite
# then: add tailwindcss() to vite.config.ts plugins and
#       `@import "tailwindcss";` at the top of src/index.css

# Backend (FastAPI layered API)
uv init backend && cd backend
uv add "fastapi[standard]" "google-genai>=2.25,<3" "transbank-sdk==6.1.0"
uv add "sqlalchemy>=2.1" "alembic>=1.20" "pydantic-settings"
uv add "pyjwt" "pwdlib[argon2]"

# Dev / test (backend)
uv add --dev pytest ruff
```

pip/venv alternative for the backend: `pip install "fastapi[standard]" "google-genai>=2.25,<3" transbank-sdk==6.1.0 sqlalchemy alembic pydantic-settings pyjwt "pwdlib[argon2]"` and `pip install pytest ruff`.

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Vite 8 | Next.js in SPA mode | Only if the course later needs SSR/SSG, server components, or a mixed app. For a strictly separated SPA it drags in a Node server runtime the pedagogy explicitly avoids — MEDIUM confidence the exclusion holds for this project |
| Zustand + TanStack Query | Redux Toolkit (+ RTK Query) | Large teams needing strict conventions, DevTools tracing, or existing Redux code. Overkill for a classroom shop: more boilerplate, no benefit at this scale |
| SQLAlchemy 2.1 + separate Pydantic schemas | SQLModel | The official FastAPI SQL tutorial uses SQLModel (one class = model + schema). We keep them separate because layer separation IS the learning objective; SQLModel merges the layers conceptually |
| SQLite (default) | PostgreSQL | When you want production-realistic concurrency/types in the guide itself — switch the SQLAlchemy URL and use psycopg 3 (see Patterns) |
| Sync routes + sync SQLAlchemy sessions | Fully async (async def + AsyncSession + aiosqlite/asyncpg) | Only for an advanced performance module. The Transbank SDK is sync (`requests`), so full async forces `run_in_threadpool` around payments anyway — sync keeps one mental model for students |
| Native fetch + TanStack Query | axios | axios adds a dependency for zero benefit here; `fetch` covers all calls and the guide teaches less API surface |
| oxlint (scaffold default) | ESLint 9 (flat config) | If the course needs a specific ESLint plugin ecosystem; otherwise keep what the template ships |
| uv | pip + venv | Classroom constraint (no uv allowed) — fully supported by FastAPI docs |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| google-generativeai (old Gemini SDK) | Deprecated; support ended 2025-11-30 (verified in prior exploration, recorded in PROJECT.md) | `google-genai` pinned `>=2.25,<3` |
| python-jose | Effectively unmaintained (last release 3.3.0) with open CVEs: CVE-2024-33663 (algorithm confusion with OpenSSH ECDSA keys) and CVE-2024-33664. Removed from the official FastAPI tutorial | PyJWT 2.15.0 (`import jwt`, explicit `algorithms=["HS256"]`) |
| passlib | Unmaintained since 2020 (1.7.4); brittle against bcrypt 5.x. Official docs now mention it only for verifying legacy hashes | pwdlib[argon2] |
| Server-side templating (Jinja2/MVC) | Explicitly out of scope — the pedagogy requires SPA + separate API (PROJECT.md). Note jinja2 arrives inside `fastapi[standard]` but stays unused | React SPA + JSON API |
| Stripe | Does not operate for Chile-registered merchants (verified against stripe.com/global, recorded in PROJECT.md) | Webpay Plus integration environment |
| "tbk-qa" commerce code circulating in search results | False rumor — verified in prior exploration | Public integration credentials: commerce code 597055555532 against `webpay3gint.transbank.cl` |
| MySQL | No advantage for this scope; adds a server to manage and is not the documented FastAPI upgrade path | SQLite default; PostgreSQL as the growth path |
| pinning `google-genai >=3` when it ships | README warns 3.x removes/moves several APIs | Pin `>=2.25,<3` |

## Stack Patterns by Variant

**If deployed data must persist across redeploys:**
- Use free PostgreSQL (e.g. Neon free tier) + `psycopg` 3 driver, changing only the SQLAlchemy `DATABASE_URL`
- Because Render free instances have ephemeral disk — SQLite files there are wiped on redeploys/spin-downs. For the base guide, an idempotent seed script + SQLite is acceptable (sandbox payments, fictional PYME); document this trade-off explicitly to students

**If the guide adds an async module:**
- `async def` routes + `AsyncSession` + aiosqlite (or asyncpg with Postgres) + `client.aio.models.generate_content` for Gemini
- Keep Webpay calls behind `run_in_threadpool` regardless — the SDK is synchronous `requests`

**If TypeScript friction hurts the timeline:**
- Scaffold with `--template react` (plain JS) — every other recommendation is unchanged

**Local development CORS:**
- Simplest: Vite dev-server `proxy` for `/api` in dev, plus FastAPI `CORSMiddleware` with the deployed frontend origin(s) in production settings

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| react-router@8.4.0 | react >= 19.2.7, vite >= 7, node >= 22.22.0 | v8 is ESM-only; the router's Node floor (22.22) is stricter than Vite 8's engines (`^20.19.0 \|\| >=22.12.0`) |
| vite@8.3.1 + @vitejs/plugin-react@6.1.1 | node `^20.19.0 \|\| >=22.12.0` | Template pins plugin ^6.1.1 alongside vite ^8.3.1 |
| typescript ~6.0.2 (template pin) | Vite react-ts scaffold | npm `latest` tag is 7.0.2 — do NOT bump blindly; the official template still validates 6.x |
| Python 3.12 runtime | fastapi >= 3.10, sqlalchemy 2.1 >= 3.11, transbank-sdk (README "3.12+", classifiers 3.8–3.12), google-genai >= 3.10, alembic >= 3.10, pwdlib >= 3.10 | 3.13/3.14 exceed the Transbank SDK's declared classifiers — do not use for the backend |
| google-genai 2.25.0 | Pin `< 3.0.0` | README: breaking changes land in 3.x |
| tailwindcss@4.3.3 | @tailwindcss/vite@4.3.3 | Keep both on the same version line; v4 = no config file, no PostCSS |
| pytest@9.1.1 | pytest-asyncio@1.4.0 | Only relevant if async tests are adopted |
| transbank-sdk 6.1.0 | marshmallow <= 3.26.1, requests >= 2.20 (auto-resolved) | Deps are sync — keep Webpay calls in sync routes |

## Sources

- registry.npmjs.org (dist-tags + tarball metadata, fetched 2026-09-28): vite 8.3.1, react/react-dom 19.3.0, react-router 8.4.0, @tanstack/react-query 5.104.0, zustand 5.0.15, tailwindcss + @tailwindcss/vite 4.3.3, typescript 7.0.2 (latest tag), create-vite 9.2.1 — HIGH
- pypi.org/pypi/*/json (fetched 2026-09-28): fastapi 0.141.1, uvicorn 0.54.0, sqlalchemy 2.1.1, alembic 1.20.0, pydantic 2.13.5, pydantic-settings 2.15.0, transbank-sdk 6.1.0, google-genai 2.25.0, pytest 9.1.1, httpx 0.28.1, pyjwt 2.15.0, pwdlib 0.3.1, pytest-asyncio 1.4.0, python-multipart 0.0.32, email-validator 2.3.0, psycopg-binary 3.3.6 (includes upload_time + requires_python) — HIGH
- github.com/vitejs/vite (main): react/react-ts templates pin react ^19.3.0, vite ^8.3.1, typescript ~6.0.2, oxlint ^1.85, @vitejs/plugin-react ^6.1.1; vite engines `^20.19.0 || >=22.12.0` — HIGH
- github.com/remix-run/react-router: releases + CHANGELOG v8.0.0 (2026-06-17; baselines Node 22.22+/React 19.2.7+/Vite 7+; ESM-only; future-flag strategy; v7/v8 lockstep) — HIGH
- github.com/TransbankDevelopers/transbank-sdk-python (README, master): "Requisitos: Python 3.12+", pip install, docs at transbankdevelopers.cl — HIGH
- github.com/googleapis/python-genai (README, main): client/generate_content/config patterns, env vars, pin `< 3.0.0` advice — HIGH
- fastapi.tiangolo.com (official docs, current): security tutorial uses pwdlib + PyJWT (passlib legacy-only, python-jose absent); home page install `uv add "fastapi[standard]"` + `[standard]` contents; first-steps uses `uv run fastapi dev`/`fastapi run` — HIGH
- tailwindcss.com/docs (official): v4 + Vite plugin install (no config, no PostCSS) — HIGH
- Community/survey sources on 2026 state management (TanStack Query + Zustand as greenfield default; Redux Toolkit legacy/large-team), SQLite-vs-PostgreSQL for learning projects, python-jose CVE trackers (CVE-2024-33663/33664), and free-hosting consensus (static on Vercel/Netlify/Cloudflare Pages + Render free API tier with spin-down and ephemeral disk) — MEDIUM (multi-source web consensus, cross-checked where possible)
- D:/Repos/demo-carro/.planning/PROJECT.md — prior verified exploration (transbank 6.1.0 / google-genai 2.25.0 / google-generativeai EOL 2025-11-30 / Stripe-not-Chile / public integration credentials); this research re-verified the version claims against the registries independently — HIGH

**Honest gaps (for phase-level research):**
- Exact Webpay Plus REST code snippets (create/commit + return-URL handling into the SPA) were not re-inspected against transbankdevelopers.cl today — the architecture researcher owns the Webpay-return spike already flagged in PROJECT.md
- Gemini free-tier RPM/RPD limits remain unconfirmed (needs a logged-in check at aistudio.google.com/rate-limit, as PROJECT.md notes)
- The gsd `classify-confidence` seam caps generic webfetch at LOW even when verified; the version pins above are registry-API primary sources triple-checked (registry + GitHub + official docs), which is why they are tagged HIGH despite the generic-provider cap. A `package-legitimacy` probe returned a false "SUS" verdict for `fastapi` (environment artifact — the same PyPI metadata identifies tiangolo as author and the official docs cross-reference)

---
*Stack research for: educational two-tier e-commerce (React SPA + FastAPI + Webpay sandbox + Gemini)*
*Researched: 2026-09-28*
