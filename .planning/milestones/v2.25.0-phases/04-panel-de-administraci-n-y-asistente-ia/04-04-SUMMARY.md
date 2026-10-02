---
phase: 04-panel-de-administraci-n-y-asistente-ia
plan: "04"
subsystem: docs
tags: [guia-educativa, asistente-ia, google-genai, gemini, structured-output, mini-rag, degradacion-503, muralla-anti-alucinacion, burbuja-chat, usemutation, productcard-reuso, grep-del-build, contrato-040, aias]

requires:
  - phase: 04-panel-de-administraci-n-y-asistente-ia (plan 01)
    provides: "contrato_api.yaml 0.4.0 (POST /api/asistente público security: [] con ChatMensaje topes 500/10 y ChatRespuesta max 3, responses 200/422/429/503 con examples locked) y ADR-017 (la decisión que los 🧠 citan, evidencia firmada contra el README @ v2.25.0)"
  - phase: 04-panel-de-administraci-n-y-asistente-ia (plan 02)
    provides: "docs/02 etapa 4 (RF-23/RF-24, RNF-08/09, RN-16, HU-13) y docs/03 pantalla 14 (burbuja) + DFD 15.0 que las guías implementan sin desviarse"
  - phase: 04-panel-de-administraci-n-y-asistente-ia (plans 03)
    provides: "guia-12/guia-13 con el panel completo (la Gran verificación final cubre la fase entera), apiPut/apiPatch sobre pedir(), la rama /admin FUERA del Layout y el Siguiente de guia-13 enlazando guia-14"
  - phase: 04-panel-de-administraci-n-y-asistente-ia (research + ui-spec)
    provides: "04-RESEARCH.md (Pattern 1 VERBATIM del README @ v2.25.0, Pattern 2 Settings str | None, Pattern 3 wrapper errors.APIError, Pattern 6 mini-RAG + validación ids, Pitfalls 1/2/4/8, A1-A5) y 04-UI-SPEC.md (pantalla 14 completa con clases Tailwind, montaje 158-169, Copywriting Contract)"
provides:
  - "docs/05_desarrollo/guia-14-asistente-backend.md: el backend de la asesora — uv add google-genai>=2.25,<3 con el pin del propio SDK, el paso del alumno D-60 (key propia en aistudio.google.com, plantilla .env.example con GEMINI_API_KEY= vacía, gate negativo sin key real), Settings gemini_api_key: str | None = None con el contraste fail-fast de secret_key (D-61), schemas/asistente.py (ChatMensaje topes RN-16, Recomendacion round-trip, ChatRespuesta max 3), services/asistente.py como ÚNICO importador del SDK (client lazy, key EXPLÍCITA desde Settings con el gotcha del auto-pickup, mini-RAG con catálogo activo por request y voz de Maura, GenerateContentConfig verbatim del pin con el drift Interactions narrado y gemini-3.8-flash como alternativa, muralla anti-alucinación doble del servidor con truncado a 3, wrapper errors.APIError → 429 sin cifras / 503 sin retry casero), routers/asistente.py público (security: [] espejo del retorno, D-59) con las CUATRO responses declaradas (Pitfall 5) y main.py solo include_router"
  - "docs/05_desarrollo/guia-15-asistente-cierre.md: la burbuja en la tienda + el cierre de la fase — BurbujaAsesora con el contrato completo de la pantalla 14 (botón fixed con aria-expanded, panel max-h-[70vh], aria-live + auto-scroll interno, las DOS excepciones declaradas de la fase), historial stateless D-58 con bienvenida local sin cuota, useMutation por request D-57, ProductCard reusada con import cruzado con razón (SEGUNDA excepción de la regla 6, D-46) hidratada por id con el queryKey de la ficha String(id), estados con copys locked + Reintentar (envio.variables), montaje en el Layout de tienda (NO en /admin) y la Gran verificación final de fase 4 (13 filas con Origen) que estrena la fila FIJA del grep del build"
  - "La pieza fija heredable: la fila 13 de la Gran verificación final (npm run build → GEMINI_API_KEY sin coincidencias en dist/, comando por shell Git Bash/PowerShell — Pitfall 8) que las fases 5+ heredan como cierre"
affects: [04-panel-de-administraci-n-y-asistente-ia (plan 04-05 cierre de fase), docs/05_desarrollo índices (guías 14-15 al conteo), UAT delegado de fase 4 en maura-uat (degradación sin key + grep del build verificables sin el usuario; happy path tras checkpoint D-60), 05-despliegue (fase 5 hereda la fila del grep del build)]

actuals:
  tokens: 19618     # chars/4 sobre el diff real commiteado (78474 chars en 2 guías nuevas)
  tasks: 2
  commits: 2        # medido: git rev-list --count 6d67ba1..HEAD

tech-stack:
  added: []         # plan documental (repo guide-only, D-17): el único paquete nuevo de la fase (google-genai) se ENSEÑA en guia-14 como paso del alumno — el repo no lo instala
  patterns:
    - "La key EXPLÍCITA al genai.Client desde NUESTRO Settings: pydantic-settings lee el .env hacia el OBJETO, no hacia el entorno del proceso — el auto-pickup del SDK no vería el archivo; el client LAZY (módulo se importa siempre, client a la primera llamada) hace real el arranque sin key (D-61/A1)"
    - "El structured output firmado contra el README del pin exacto: models.generate_content + GenerateContentConfig(response_mime_type='application/json', response_json_schema=Recomendacion.model_json_schema()) con round-trip model_validate_json — y el drift de las docs web (Interactions API + response_format) narrado como lección, jamás copiado (Pitfalls 1/2, D-56)"
    - "La muralla anti-alucinación doble y del SERVIDOR: system prompt con catálogo ACTIVO por request (muralla 1) + filtro de ids contra la base antes de responder con truncado a 3 (muralla 2) — el frontend renderiza lo que ya llegó validado (AIAS-02)"
    - "El wrapper frontera except Exception bajo errores.APIError tipado: la regla IN-06 (nada cruza como 500) gana sobre la veta del except amplio, con la construcción del client DENTRO del try (A1) y SIN retry casero (el SDK ya reintenta transitorios 4x)"
    - "apiPostPublico: el flag sinAuth que el login estrenó, tercer uso — POST JSON público sin Bearer para el chat (D-59); el chat es useMutation por request, jamás useQuery (D-57)"

key-files:
  created:
    - docs/05_desarrollo/guia-14-asistente-backend.md
    - docs/05_desarrollo/guia-15-asistente-cierre.md
  modified: []       # cero ediciones a guías previas: el eslabón 13→14 ya lo había dejado guia-13 (plan 04-03)

key-decisions:
  - "La key se pasa EXPLÍCITA al genai.Client desde Settings en vez de confiar en el auto-pickup del SDK: pydantic-settings lee el .env hacia el objeto y NO exporta al entorno del proceso — confiar en el auto-pickup fallaría silenciosamente a la primera llamada (gotcha narrado en guia-14 paso 5)"
  - "system_instruction como string dentro del MISMO GenerateContentConfig del patrón firmado + contents como transcripto plano (Clienta:/Asesora: por línea): la superficie del SDK no firmada por el research se reduce a system_instruction (core del SDK desde 0.x) — el resto es exactamente el Pattern 1 verbatim"
  - "Recomendacion SIN tope en productos y ChatRespuesta CON max_length=3: lo que se le pide al modelo y lo que el contrato promete son cosas distintas — el truncado a 3 vive en el service, entre el round-trip y la respuesta (lección de capas en el schema)"
  - "El chat hidrata las cards por id con useQueries y el queryKey de la ficha String(id) (patrón guia-07) sobre la ProductCard reusada con import cruzado con razón: la SEGUNDA excepción de la regla 6 (D-46), la misma caché de la ficha — duplicar la card serían dos verdades del mismo producto"
  - "La fila del grep del build queda FIJA (fila 13) con comando por shell (grep -r para Git Bash, findstr /s /i para PowerShell, Select-String como alternativa) corrido DESPUÉS de npm run build: cualquier variable VITE_ termina en el bundle — la key, nunca (AIAS-03, Pitfall 8)"
  - "El 429 se enseña sin cifras en copys y GV (fila 10 del guia-15 lo nota): los límites RPM/RPD del free tier no son públicos sin login (concern abierto de STATE.md) — el happy path queda tras la key del alumno (D-60, nota honesta en la GV)"

patterns-established:
  - "La degradación como promesa de usuario: sin key la burbuja SIGUE visible avisando amable con Reintentar (jamás se esconde) y la tienda 100% operativa — el contraste D-61 (fail-fast de secret_key vs str | None de gemini_api_key) demostrado con model_fields en una mini-verificación"
  - "El texto del modelo se renderiza como TEXTO ({m.texto} entre llaves, escape por defecto de React): el atributo que inyecta HTML crudo ni se nombra en la guía — la muralla del render contra prompt injection (T-04-11)"
  - "Reintentar con envio.variables: el payload YA armado del último envío se re-envía tal cual — TanStack v5 guarda las variables de la última mutación y el patrón cabe en un botón"
  - "La ubicación en el árbol de rutas ES la regla: la burbuja vive en el Layout de tienda (la ven públicas y clienta) y NO en /admin porque esa ruta vive en la OTRA rama de layout — cero condicionales (D-55/D-59)"

requirements-completed: [AIAS-01, AIAS-02, AIAS-03]  # copiado verbatim del PLAN; flip en REQUIREMENTS.md vía requirements.ready-ids (sin shared-ID: 04-05 no declara AIAS-*)

coverage:
  - id: D1
    description: "guia-14-asistente-backend.md enseña la segunda integración con servicio externo real implementando el contrato 0.4.0: instalación con pin >=2.25,<3 (🧠 del pin del propio SDK y google-generativeai vetado EOL), el paso del alumno D-60 (key propia en aistudio.google.com, plantilla .env.example con GEMINI_API_KEY= vacía, verificación por existencia sin imprimir el valor, gate negativo sin key real), Settings gemini_api_key: str | None con el contraste fail-fast demostrado con model_fields, schemas/asistente.py con los tres modelos y sus tres trabajos (topes RN-16 500/10 declarativos, Recomendacion round-trip sin tope, ChatRespuesta max 3), services/asistente.py ÚNICO importador del SDK (client lazy con guard None, key explícita con el gotcha del auto-pickup, mini-RAG con catálogo activo por request y voz de Maura en primera persona, llamada verbatim del README @ v2.25.0 con gemini-flash-latest y gemini-3.8-flash como alternativa con el drift Interactions narrado, advertencia de no duplicar el schema en el prompt, validación de ids contra BD + truncado a 3, wrapper errors.APIError e.code==429 sin cifras / resto 503 con except Exception de frontera IN-06 y sin retry casero), routers/asistente.py público con 200/422/429/503 declaradas, main.py solo include_router, y las mini-verificaciones SIN depender del usuario (422 en 501 chars y en historial 11; degradación sin key con 503 amable + tienda operativa) con estructura canónica (8 🧠, 8 mini-verificaciones, ❌ con 5 errores evitados incluida la key en VITE_, Punto de control, Siguiente→guia-15)"
    requirement: AIAS-01
    verification:
      - kind: other
        ref: "grep chain del Task 1 (g14-ok) re-ejecutada: google-genai, >=2.25,<3, aistudio.google.com, GEMINI_API_KEY, 'str | None', fail-fast, from google import genai, response_mime_type, response_json_schema, model_json_schema, GenerateContentConfig, gemini-flash-latest, errors.APIError, 429, 503, model_validate_json, catálogo activo, voz de Maura, security: []/público, Interactions, ADR-017, contrato_api.yaml, v2.25.0, 8×'El desarrollador piensa' (≥5), 8×'Mini-verificación' (≥4), Punto de control, Siguiente→guia-15-asistente-cierre, gate negativo sin prefijo de key real — pass"
        status: pass
    human_judgment: false
  - id: D2
    description: "guia-15-asistente-cierre.md enseña la burbuja en la tienda y cierra la fase 4: tipos ChatRespuesta/RolChat espejo del contrato + apiPostPublico (sinAuth del login, tercer uso — POST sin Bearer porque el endpoint es público D-59), BurbujaAsesora con el contrato completo de la pantalla 14 (botón fixed bottom-6 right-6 con aria-expanded/aria-controls y label Pregúntale a Maura, panel fixed bottom-20 right-6 w-80 sm:w-96 max-h-[70vh] con header Asesora de aromas + subtítulo + Cerrar, zona de mensajes p-4 overflow-y-auto con aria-live=polite y auto-scroll scrollIntoView, burbujas asesora bg-orange-50/clienta bg-orange-600 self-end, input con aria-label/placeholder ¿Qué aroma buscas?/maxLength 500 y Enviar disabled en vuelo, las DOS excepciones declaradas shadow-lg/max-h-[70vh]), historial stateless D-58 con bienvenida local ¡Hola! Soy la asesora de Maura… sin cuota, useMutation por request D-57 con burbuja animate-pulse, ProductCard reusada con import cruzado con razón (SEGUNDA excepción de la regla 6, D-46) hidratada con useQueries queryKey ['producto', String(id)], estados 503/429/red con copys locked + Reintentar con envio.variables, texto del modelo como TEXTO, montaje en el Layout de tienda (NO en /admin), y la Gran verificación final de fase 4: 13 filas con Origen (roles/CRUD/soft delete/huérfana 409/métricas/asistente/topes/degradación/burbuja sin admin), fila 12 contrato 0.4.0 ↔ /docs con Authorize admin contra el CRUD real, fila 13 FIJA del grep del build (GEMINI_API_KEY sin coincidencias en dist/, grep -r Git Bash y findstr/Select-String PowerShell, tras npm run build), párrafo 'cualquier diferencia… jamás cambia en silencio', commit de cierre con los 17 ADRs, Siguiente→fase 5 y nota honesta D-60"
    requirement: AIAS-02
    verification:
      - kind: other
        ref: "grep chain del Task 2 (g15-ok): BurbujaAsesora, Pregúntale a Maura, Asesora de aromas, ¡Hola! Soy la asesora de Maura, ¿Qué aroma buscas?, aria-live, scrollIntoView, ProductCard, useMutation, 'La asesora no está disponible en este momento', 'recibiendo muchas consultas', Reintentar, Gran verificación final, 0.4.0, Authorize, GEMINI_API_KEY, dist/, 'grep -r', PowerShell/findstr/Select-String, npm run build, 17 ADRs, fase 5, NoAutorizado, 4×'El desarrollador piensa' (≥4), 6×'Mini-verificación' (≥3), Punto de control, Siguiente, gate negativo sin el atributo que inyecta HTML — pass"
        status: pass
    human_judgment: false

duration: 15 min
completed: 2026-09-30
status: complete
plan_head_before: 6d67ba1a21fe7b4722d2f3d7491e31fefc579285
plan_head_after: 7c0de8a6d6fd935f9dccfe475af748a3017c1c67
---

# Phase 4 Plan 04: Asistente IA (guías 14-15) Summary

**La mitad de desarrollo del asistente (AIAS-01..03): guia-14 enseña google-genai con structured output firmado contra el README del pin, key opcional con degradación y muralla anti-alucinación del servidor; guia-15 la burbuja SPA con la ProductCard reusada y la Gran verificación final de fase 4 que estrena la fila FIJA del grep del build**

## Performance

- **Duration:** 15 min
- **Started:** 2026-09-30T22:02:20Z
- **Completed:** 2026-09-30T22:17:06Z
- **Tasks:** 2
- **Files modified:** 2 (creadas)

## Accomplishments
- guia-14: la segunda integración con servicio externo real — pin `>=2.25,<3` con la razón del propio SDK, key como paso del alumno (D-60) con plantilla vacía y gate negativo, `str | None` con el contraste fail-fast demostrado, el trío `response_mime_type`/`response_json_schema`/`model_json_schema()` VERBATIM del README @ v2.25.0 con el drift Interactions narrado, doble muralla anti-alucinación y wrapper 429/503 sin retry casero
- guia-15: la burbuja con el contrato completo de la pantalla 14 (aria-live, auto-scroll interno, las dos excepciones declaradas), historial stateless con bienvenida local, useMutation por request, ProductCard reusada (segunda excepción de la regla 6, D-46) y los tres estados con copys locked
- La Gran verificación final de fase 4 completa: 13 filas con Origen, la fila contrato 0.4.0 ↔ `/docs` con Authorize admin contra el CRUD real, y la fila 13 FIJA del grep del build por shell que las fases futuras heredan (AIAS-03)

## Task Commits

Each task was committed atomically:

1. **Task 1: guia-14-asistente-backend.md** - `7813c49` (docs)
2. **Task 2: guia-15-asistente-cierre.md** - `7c0de8a` (docs)

**Plan metadata:** (commit al cierre de este plan)

## Files Created/Modified
- `docs/05_desarrollo/guia-14-asistente-backend.md` - El backend de la asesora: instalación pinneada, key del alumno, Settings opcional, schemas, service ÚNICO importador del SDK (client lazy, mini-RAG, structured output del pin, muralla de ids, wrapper de errores), router público con las cuatro responses y mini-verificaciones sin depender del usuario
- `docs/05_desarrollo/guia-15-asistente-cierre.md` - La burbuja en la tienda (pantalla 14 completa), el montaje en el Layout, la prueba de fuego y la Gran verificación final de fase 4 con la fila del grep del build

## Decisions Made
- La key pasa EXPLÍCITA al `genai.Client` desde Settings (el auto-pickup del SDK no ve el `.env` que pydantic-settings lee hacia el objeto, no hacia el entorno del proceso); client LAZY para que la app arranque sin key
- `Recomendacion` sin tope de ids y `ChatRespuesta` con `max_length=3`: pedirle al modelo y prometer en el contrato son cosas distintas — el truncado vive en el service
- Las cards del chat se hidratan por id con el queryKey de la ficha (`String(id)`, patrón guia-07) sobre la ProductCard reusada — la misma caché, una sola verdad del producto
- La fila del grep del build queda FIJA en la posición 13 de la GV con comando por shell (Pitfall 8), y el happy path del asistente queda honestamente anotado como dependiente de la key del alumno (D-60)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required. (La GEMINI_API_KEY es paso del ALUMNO dentro de la guía, D-60 — no del repo ni del pipeline.)

## Next Phase Readiness
- Listo para 04-05 (cierre de fase 4): índices de docs/05_desarrollo y READMEs, gate documental de fase y conteo de guías 1-15
- El UAT delegado de fase 4 tiene la ruta marcada: degradación sin key (503 + burbuja) y grep del build verificables SIN el usuario; el happy path (llamada real a Gemini) queda tras checkpoint:human-verify con la key del usuario (Open Question 1 resuelta en 04-RESEARCH)
- La fila 13 del grep del build es herencia directa de la fase 5 (despliegue): el build que se publicará es el mismo que se grep-ea

## Self-Check: PASSED

- [x] docs/05_desarrollo/guia-14-asistente-backend.md existe (850 líneas)
- [x] docs/05_desarrollo/guia-15-asistente-cierre.md existe (707 líneas)
- [x] Commit 7813c49 en la historia (Task 1)
- [x] Commit 7c0de8a en la historia (Task 2)
- [x] grep chain Task 1 (g14-ok) — pass
- [x] grep chain Task 2 (g15-ok) — pass
- [x] Cadena de Siguiente: guia-13→14 (preexistente), 14→15, 15→fase 5
- [x] Sin ediciones a guías previas (guia-13 ya enlazaba guia-14)
- [x] Sin key real en el material (gate negativo de prefijo de key: 0 coincidencias en ambas guías)

---
*Phase: 04-panel-de-administraci-n-y-asistente-ia*
*Completed: 2026-09-30*
