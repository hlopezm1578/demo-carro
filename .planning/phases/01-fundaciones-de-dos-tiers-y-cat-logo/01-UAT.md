---
status: diagnosed
phase: 01-fundaciones-de-dos-tiers-y-cat-logo
source: [01-VERIFICATION.md]
started: 2026-09-28
updated: 2026-09-29
---

## Current Test

[testing complete]

## Tests

### 1. guia-01 — proyecto backend de cero a /api/salud
expected: Siguiendo la guía en una máquina con Python 3.12 + uv: `uv init backend --vcs none` (sin repo git anidado), `uv add` de dependencias, `uv run fastapi dev` levanta sin errores, `GET /api/salud` → `{"estado": "ok"}`, `/docs` muestra Swagger.
result: issue
reported: "Ejecutada por el agente (delegado por el usuario, 2026-09-29, en D:/Repos/maura-uat): todos los resultados prometidos OK — uv init sin .git anidado, pyproject con techo >=3.12,<3.13, uv add congela uv.lock (fastapi/uvicorn/httpx), GET /api/salud → {\"estado\":\"ok\"} exacto, /docs Swagger UI titulado 'Maura API' con endpoint salud. Desviación: uv 0.9.3 con --vcs none NO genera backend/.gitignore — el Paso 1 lo lista como archivo generado y el Paso 5 manda 'revisar el .gitignore que generó uv'; el archivo no existe hasta crearlo a mano con el contenido que la propia guía entrega."
severity: minor
verified_by: agent (user-delegated)

### 2. guia-02 — proyecto frontend y landing de Maura
expected: Siguiendo la guía con Node >= 22.22: scaffold vite react-ts, Tailwind 4 + Nunito, `npm run dev` → http://localhost:5173 muestra la landing con eyebrow "Maura · Body Splash", tagline "Frescura que te acompaña", párrafo en primera persona, CTA "Ver catálogo" y las 4 mini-cards de familia; `/productos` queda en estado de error controlado con botón "Reintentar" (el endpoint aún no existe — primera lección de estados async).
result: pass
verified_by: agent (user-delegated)
notes: "Ejecutada en D:/Repos/maura-uat con Node portátil v22.23.3 (la máquina tiene 22.18 < 22.22 — la guía detecta y gatea el requisito correctamente, Paso 1 validado). Todo OK: scaffold react-ts (react 19.2.8, typescript ~6.0.2, oxlint), 3 instalaciones, proxy /api verificado vía curl (5175→8000 {"estado":"ok"}), experimento del typo falla/pasa exacto, build limpio, landing renderizada y estilizada verificada con Edge headless (hero naranja pálido, tagline, párrafo 1ª persona, CTA naranja, 4 cards con badges), /productos en error controlado con Reintentar (tras ~7s de retries default de TanStack Query), 404 propia OK. Observaciones de entorno (no bugs de guía): puerto 5173 ocupado por otro proyecto → Vite eligió 5175 (la guía asume 5173 libre); el navegador embebido de ZCode no pinta estilos inyectados por JS (verificado con Edge headless que el render real es correcto)."

### 3. guia-03 — modelos y seed idempotente
expected: Siguiendo la guía: `uv run python -m app.seed` dos veces — primera corrida imprime doce marcas `[+]`, segunda corrida imprime doce `[=]` y cero `[+]`; sin filas duplicadas (12 productos exactos).
result: pass
verified_by: agent (user-delegated)
notes: "Salida byte-a-byte igual a la prometida: corrida 1 = doce [+] + 'Seed listo: 12 creados [+], 0 actualizados [=] (12 productos en total)'; corrida 2 = doce [=] + '0 creados, 12 actualizados'. Mini-verificaciones todas exactas: engine.url=sqlite:///./maura.db, nombres del enum = slugs, tabla productos con las 10 columnas del diccionario en orden, 12 productos/4 familias, familia persistida en minúscula (gotcha del enum cerrado), count=12 filas sin duplicados, maura.db creado. Sub-check 'git status no lo lista' N/A (monorepo de prueba sin git init, opcional según la guía; .gitignore cubre *.db)."

### 4. guia-04 — catálogo completo y cierre contrato ↔ /docs
expected: Siguiendo la guía: grilla con 12 productos, filtros por familia y rango de precio reflejados en la URL (compartibles con back/forward), ficha de producto con badge ámbar "¡Últimas N unidades!" cuando stock <= 3, familia inválida por URL editada → 422 con mensaje claro, descarga de las 12 fotos a frontend/public/products/, y la fila 11 de la Gran Verificación Final compara /docs contra contrato_api.yaml. NOTA: WR-01/WR-02 del review (abiertos) harán aparecer un desvío falso en esa fila (422 faltante en el contrato para /api/productos/{id} y schema Error detail string vs array) — revisar con esa lectura.
result: issue
reported: "Ejecutada por el agente (delegado por el usuario, 2026-09-29): TODO el funcional pasa — 12 productos con fotos reales en public/products/ servidas localmente, filtros familia+rango en la URL (compartible por navegación directa, back/forward funcionando, 'Limpiar filtros'), 422 por familia=vinagre con JSON que nombra el valor, 404 runtime con detail exacto, ficha completa con badge ámbar '¡Últimas 2 unidades!' (stock 2) y verde 'Disponible' (stock 14), notas como chips, navigate(-1) preserva filtros, 404 propio en /productos/999 vía ApiError, error controlado con backend apagado y Reintentar revive sin recargar, re-siembra doce [=]. Fila 11 (contrato ↔ /docs): paths, parámetros (enum 4 slugs, minimum 0, path id) y schemas ProductoResumen(6)/ProductoDetalle(9) coinciden; se confirman los 2 desvíos YA CONOCIDOS (WR-01: 422 de {id} no declarado en contrato; WR-02: Error.detail string vs array real) — pero aparece un TERCER desvío NO previsto por la nota del review: el contrato declara respuesta 404 para /api/productos/{producto_id} y /docs NO la documenta, porque el router de la guía (Paso 3) hace raise HTTPException(404) sin declarar responses={404} y FastAPI no documenta las excepciones lanzadas a runtime. El alumno que hace la fila 11 con la 'lectura WR' igual topa con este desvío sin estar advertido."
severity: minor
verified_by: agent (user-delegated)

## Summary

total: 4
passed: 2
issues: 2
pending: 0
skipped: 0
blocked: 0

## Gaps

- gap_id: G-01-1
  truth: "guia-01 Paso 1 afirma que `uv init backend --vcs none --app` genera un `.gitignore` en `backend/`, y el Paso 5 pide 'revisar el .gitignore que generó uv'"
  status: failed
  reason: "Agent-executed run (user-delegated, uv 0.9.3): `--vcs none` NO genera `.gitignore` — el archivo no existe tras el Paso 1 y el Paso 5 presuponía encontrarlo ya generado; hubo que crearlo manualmente con el contenido que la propia guía muestra"
  severity: minor
  test: 1
  artifacts:
    - path: "docs/05_desarrollo/guia-01-proyecto-backend.md"
      issue: "Paso 1 lista '.gitignore' entre los archivos que genera uv init; Paso 5 pide 'revisar el backend/.gitignore que generó uv. Déjalo así'"
  missing:
    - "Corregir Paso 1: quitar .gitignore de la lista de archivos generados por 'uv init --vcs none'"
    - "Corregir Paso 5: cambiar 'revisa el .gitignore que generó uv' por 'crea backend/.gitignore con este contenido' (el contenido ya está en la guía)"
  root_cause: "uv init solo genera .gitignore cuando crea el VCS: con --vcs none el archivo no existe (verificado empíricamente con uv 0.9.3 en dos puntos de la ejecución)"
  debug_session: ""
- gap_id: G-01-4
  truth: "La fila 11 de la Gran Verificación Final de guia-04 (contrato ↔ /docs) debería mostrar solo los desvíos ya conocidos (WR-01/WR-02), pero el contrato declara respuesta 404 para /api/productos/{producto_id} y el panel /docs generado siguiendo la guía no la documenta"
  status: failed
  reason: "Agent-executed run (user-delegated): el router del Paso 3 de guia-04 hace raise HTTPException(404) sin declarar responses={404}; FastAPI no documenta en OpenAPI las excepciones lanzadas a runtime, por lo que /docs lista solo 200+422 para {producto_id}. El 404 funciona en runtime (verificado por curl), pero el alumno que compara fila 11 encuentra un tercer desvío no advertido por la guía ni por la nota WR del review"
  severity: minor
  test: 4
  artifacts:
    - path: "docs/05_desarrollo/guia-04-catalogo.md"
      issue: "Paso 3: obtener_producto hace raise HTTPException(status_code=404) sin declarar responses={404} en el decorator; la fila 11 de la Gran Verificación compara contra contrato_api.yaml que sí declara la respuesta 404 para ese path"
  missing:
    - "Opción A (recomendada, pedagógica): enseñar en el Paso 3 a declarar la respuesta 404 en el decorator (responses={404: {'description': 'Producto inexistente', 'model': Error}}) para que /docs la documente y la fila 11 cierre sin este desvío"
    - "Opción B (mínima): agregar a la nota de la fila 11 (junto a la advertencia WR-01/WR-02 del review) que el 404 declarado en el contrato no aparece en /docs y por qué"
  root_cause: "FastAPI no documenta en OpenAPI las HTTPException lanzadas a runtime si el endpoint no declara la respuesta vía el parámetro responses del decorator (verificado contra openapi.json vivo: responses de {id} = ['200','422'])"
  debug_session: ""
