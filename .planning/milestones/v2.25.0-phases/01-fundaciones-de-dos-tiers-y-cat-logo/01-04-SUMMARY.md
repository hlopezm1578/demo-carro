---
phase: 01-fundaciones-de-dos-tiers-y-cat-logo
plan: 01-04
subsystem: docs
tags: [guias-desarrollo, backend, frontend, uv, vite, react, tailwind]

requires:
  - "docs/04_arquitectura/adr/001..008 y contrato_api.yaml (01-01/01-03) — los pasos citan ADR por numero"
  - "docs/01..03 del ciclo (01-02) — pantallas y copies citados por las guias"
provides:
  - "docs/05_desarrollo/README.md: indice de la serie con declaracion guide-only, 3 Reglas del alumno, tabla de 4 guias (orden D-16) y mapa mental"
  - "guia-01-proyecto-backend.md: del directorio vacio al endpoint /api/salud verificado — codigo verbatim del backend que funciono (git 364dee6)"
  - "guia-02-proyecto-frontend.md: scaffold react-ts → landing STORE-01 con copies contractuales, tipos espejo D-09, apiGet y estados async"
  - "Estructura canonica de guia Maura (blockquote / terminos / pasos con 🧠+✅ / error que evita / cierre) que heredan guia-03/04 (01-05)"
affects: [01-05, fase-2, fase-3, fase-4, fase-5]

actuals:
  tokens: 14192
  tasks: 3
  commits: 3
  plan_head_before: d145e8506cd04e3f87492a3f5544982e10e01cdd
  plan_head_after: 17a4f7f8cd6c9387296777b1ebdc853ea514f2a7

tech-stack:
  added: []
  patterns:
    - "Formato canonico de guia: blockquote Que construiras/Al terminar/Needitas + tabla terminos + pasos numerados con 🧠 (cita ADR/RN) y ✅ Mini-verificacion del alumno + ❌ error que evita + cierre (verificacion URLs / punto de control / lo aprendido / Siguiente)"
    - "Gate de runtime como paso 1 del alumno en prosa (node -v >= 22.22) — D-17: vive en la maquina del alumno, no en el pipeline"
    - "Links de familia por slug ASCII en la URL (RN-01): etiqueta con acento en pantalla, slug sin acentos en el href"
    - "Codigo verificado como fuente narrada: bloques de guia-01 verbatim del historial git (364dee6) — la guia no inventa codigo"

key-files:
  created:
    - docs/05_desarrollo/README.md
    - docs/05_desarrollo/guia-01-proyecto-backend.md
    - docs/05_desarrollo/guia-02-proyecto-frontend.md
  modified: []

key-decisions:
  - "guia-01 narra el backend verificado retirado (git 364dee6) con main.py en etapa esqueleto: solo router de salud; el router de productos se agrega como una linea de composicion en guia-04 (crecer componiendo, ADR-001)"
  - "Tabla del README de 05_desarrollo con estado honesto por fase (D-13): guia-01/02 ✅ Listo, guia-03/04 ⏳ Pendiente misma fase (las escribe 01-05) — la tabla anuncia el orden completo D-16 sin marcar listo lo que no existe"
  - "Cleanup del scaffold (App.tsx/App.css/react.svg) corrido al paso 6, despues del main.tsx nuevo: evita el estado intermedio roto (import de archivo borrado) y el ✅ npm run build del paso 6 valida la limpieza"
  - "guias con pasos 0 (monorepo) y stubs de componentes antes de main.tsx: walking skeleton que compila en cada paso verificable"

requirements-completed: [GUIDE-03, STORE-01]

coverage:
  - id: D1
    description: "README de 05_desarrollo con Reglas del alumno, tabla de 4 guias en orden D-16, mapa mental y declaracion guide-only (el codigo se construye en la maquina del alumno)"
    requirement: "GUIDE-03"
    verification: [{kind: other, ref: "grep 'Reglas del alumno' + guia-01 + guia-04 + 'mapa mental' + 'tu máquina' → dev-readme-ok", status: pass}]
    human_judgment: false
  - id: D2
    description: "guia-01 backend: uv init --vcs none, techo >=3.12,<3.13, Settings, CORS explicito, /api/salud y fastapi dev; 7 bloques piensa + 7 mini-verificaciones; codigo verbatim de git 364dee6"
    requirement: "GUIDE-03"
    verification: [{kind: other, ref: "grep uv init/vcs none/3.12/api/salud/fastapi dev/CORSMiddleware + conteos -ge 4 + ADR-006 → g1-ok", status: pass}]
    human_judgment: false
  - id: D3
    description: "guia-02 frontend: gate node -v >= 22.22, scaffold, Tailwind 4 + Nunito, providers v8, tipos espejo (ProductoResumen), apiGet, landing STORE-01 con copies textuales y exactamente 4 links por familia"
    requirement: "STORE-01"
    verification: [{kind: other, ref: "grep node -v/22.22/create vite/tailwindcss/Nunito/tagline/Ver catálogo/Nuestras familias/ProductoResumen/es-CL + conteo productos?familia= -eq 4 + conteos -ge 5 + gate negativo sin import del paquete eliminado → g2-ok", status: pass}]
    human_judgment: false
  - id: D4
    description: "Cobertura STORE-01 en terminos D-17: la guia ensena a construir la landing (hero eyebrow/tagline D-04/persona/CTA/familias) y hace que el ALUMNO la verifique en localhost:5173 — el UAT visual vive en la maquina del alumno, no en este repo"
    requirement: "STORE-01"
    verification: [{kind: other, ref: "greps de copies contractuales + paso 12 de guia-02 con URLs concretas del alumno", status: pass}]
    human_judgment: true

duration: 11min
completed: 2026-09-28
status: complete
---

# Phase 01 Plan 01-04: Guías de desarrollo 01-02 (backend y frontend) Summary

**Serie de desarrollo bajo el modelo guide-only (D-17): README de 05_desarrollo con las reglas del alumno + guia-01 (backend uv → /api/salud con código verificado del historial git) + guia-02 (scaffold react-ts → landing STORE-01 con copies contractuales, tipos espejo del contrato y estados async honestos).**

## Performance

- 3 tareas / 3 commits / 3 archivos creados (solo docs/05_desarrollo — cero código de aplicación en el repo)
- Estimate 34000 tokens → actual ~14192 tokens (chars/4 del diff docs/) — el plan sobreestimó; la guía resultó más compacta que el presupuesto
- Verificaciones automatizadas de las 3 tareas: dev-readme-ok, g1-ok, g2-ok — a la primera, sin reintentos

## Accomplishments

- **docs/05_desarrollo/README.md**: blockquote de funcionamiento con la declaración guide-only (ADR-008: el código vive narrado en las guías y se construye en la máquina del alumno), 3 Reglas del alumno numeradas, tabla de las 4 guías de fase 1 en orden D-16 (proyecto backend / proyecto frontend / modelos y seed / catálogo) y mapa mental "de adentro hacia afuera" (tiers → datos → pantalla que une).
- **guia-01-proyecto-backend.md** (429 líneas): 7 pasos (0-6) cada uno con 🧠 citando ADR-001/002/003/005/006/007/008 y RNF-04 + ✅ Mini-verificación que corre el alumno. Código verbatim del backend verificado que fue retirado del árbol (git 364dee6): pyproject con techo, config.py con Settings, routers/salud.py, main.py composición + CORS explícito, .gitignore. Sección "el error que este archivo evita": .git anidado y CORS comodín (contraste ❌/✅). Cierre completo: verificación con URLs concretas (localhost:8000/api/salud y /docs), punto de control (3 preguntas), lo aprendido, Siguiente → guia-02.
- **guia-02-proyecto-frontend.md** (904 líneas): 12 pasos con 9 bloques 🧠 + 10 ✅. Gate node -v >= 22.22 como PREREQUISITO en prosa del alumno (D-17: gate de guía, no del pipeline; con guía de upgrade MSI/nvm-windows). Scaffold react-ts + installs (router v8, TanStack Query, Tailwind 4 plugin, Nunito self-hosted vía npm). Bloques anclados en Patterns 3/4 verificados de 01-RESEARCH y copies textuales del UI-SPEC: hero con eyebrow "Maura · Body Splash", tagline D-04 "Frescura que te acompaña", persona en primera persona, CTA "Ver catálogo", "Nuestras familias" con exactamente 4 links por slug ASCII (RN-01). Tipos TS espejo del contrato (ProductoResumen/ProductoDetalle, ADR-004), apiGet único punto HTTP, catálogo mínimo con estados async (isPending skeletons / isError "No pudimos cargar el catálogo" + Reintentar) y la lección honesta: /productos muestra error controlado hasta guia-04.
- **Prohibiciones verificadas**: cero código de aplicación commiteado (solo 3 .md en docs/); cero líneas de import del paquete de router eliminado en v8 (el nombre aparece solo en prosa de advertencia — gate negativo del verify en 0); cero comandos bash-only ni formas alternativas (D-12); cero hotlinks externos en bloques de código (Nunito es paquete npm; nodejs.org solo en prosa).

## Task Commits

| Task | Commit | Archivo |
|---|---|---|
| 1. README índice y reglas | `0300025` | docs/05_desarrollo/README.md |
| 2. guia-01 proyecto backend | `83e3487` | docs/05_desarrollo/guia-01-proyecto-backend.md |
| 3. guia-02 proyecto frontend | `17a4f7f` | docs/05_desarrollo/guia-02-proyecto-frontend.md |

## Files Created-Modified

**Created:** docs/05_desarrollo/README.md · docs/05_desarrollo/guia-01-proyecto-backend.md · docs/05_desarrollo/guia-02-proyecto-frontend.md

**Modified:** ninguno (el plan es greenfield documental)

## Decisions Made

Ver `key-decisions` en el frontmatter. La principal: **la tabla del README marca guia-03/04 como pendientes de la misma fase** en vez de ✅ Listo anticipado — el plan anticipaba el ✅ "al cierre de la fase", pero marcar listo lo que 01-05 todavía no escribió contradiría la honestidad documental que el propio producto enseña (regla del proyecto: ninguna fase se escribe sin aprobar la anterior).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Secuencia] Cleanup del scaffold movido del paso 5 al paso 6 de guia-02**
- **Found during:** Task 3
- **Issue:** la acción del plan ponía "borrar los sobrantes App.tsx/App.css/react.svg" en el paso 5, pero main.tsx (que deja de importarlos) se escribe recién en el paso 6 — borrando en el paso 5 el proyecto queda con un import roto y ninguna verificación puede pasar.
- **Fix:** el borrado vive al final del paso 6, inmediatamente después del main.tsx nuevo; el ✅ "npm run build sin errores" del paso 6 valida la limpieza completa.
- **Files modified:** docs/05_desarrollo/guia-02-proyecto-frontend.md
- **Commit:** 17a4f7f

**2. [Rule 1 - Honestidad documental] Estado de guia-03/04 en la tabla del README**
- **Found during:** Task 1
- **Issue:** la acción del plan pedía Estado "✅ Listo al cierre de la fase" para las 4 filas; guia-03/04 no existen aún (las escribe 01-05) y marcarlas listas sería documentación falsa en el repo cuyo producto ES la documentación.
- **Fix:** guia-01/02 "✅ Listo", guia-03/04 "⏳ Pendiente (misma fase)" con nota de que la tabla declara el orden completo — D-13 (estado avanza por fase) aplicado también dentro de 05_desarrollo.
- **Files modified:** docs/05_desarrollo/README.md
- **Commit:** 0300025

## Issues Encountered

Ninguno bloqueante. Las tres verificaciones automatizadas pasaron a la primera. Nota menor de forma (sin impacto en gates): ajuste de un salto de línea accidental en la prosa de FichaProducto antes de commitear Task 3.

## User Setup Required

None — el plan es documental (D-17): nada que instalar ni configurar en este repo. El gate node -v >= 22.22 es un paso del alumno dentro de guia-02, no un requisito del repo.

## Next Phase Readiness

- **01-05** (guia-03 modelos y seed + guia-04 catálogo): hereda la estructura canónica de guía fijada aquí (blockquote/términos/🧠+✅/error evitado/cierre), el "Siguiente: guia-03" que encadena guia-02, y las dos filas ⏳ del README que debe voltear a ✅.
- **GUIDE-03 queda a la mitad** (cobertura documental de guias 1-2 de 4): completa cuando 01-05 entregue guia-03/04 — el gate `requirements.ready-ids` lo reporta blocked por dependencia.
- STORE-01 cubierto documentalmente: la guía enseña y hace verificar la landing con identidad de marca; el UAT visual vive en la máquina del alumno (D-17).

## Self-Check: PASSED

Archivos verificados en disco: README.md, guia-01-proyecto-backend.md, guia-02-proyecto-frontend.md (los 3 FOUND). Commits verificados en `git log --all`: 0300025, 83e3487, 17a4f7f (los 3 FOUND). Sin pendientes.
