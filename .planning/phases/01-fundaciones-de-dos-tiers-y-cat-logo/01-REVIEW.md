---
phase: 01-fundaciones-de-dos-tiers-y-cat-logo
reviewed: 2026-09-29T12:25:31Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - docs/05_desarrollo/guia-01-proyecto-backend.md
  - docs/05_desarrollo/guia-04-catalogo.md
findings:
  critical: 0
  warning: 3
  info: 1
  total: 4
status: issues_found
---

# Phase 01: Code Review Report

**Reviewed:** 2026-09-29T12:25:31Z
**Depth:** standard
**Files Reviewed:** 2
**Status:** issues_found

## Summary

Revisión del delta de cierre de gaps del UAT (commits `7d28520` y `7d8ca85`, diff desde `d85e1e7`) sobre los dos archivos guía. El repositorio es guide-only (D-17): el "código fuente" son los bloques Python/bash embebidos que el alumno copia, así que la revisión verificó la corrección factual de las afirmaciones nuevas, la consistencia contra `docs/04_arquitectura/contrato_api.yaml` y la coherencia interna entre guías.

**Verificado sin hallazgos (los dos fixes son correctos):**

- **G-01-1 (guia-01) confirmado empíricamente con uv 0.9.3**, el mismo major que usó el UAT: `uv init backend --vcs none --app` genera exactamente `pyproject.toml`, `.python-version`, `README.md` y `main.py` — ningún `.gitignore` (y sin `--vcs none` sí genera `.git` + `.gitignore`, con lo que "uv solo lo escribe junto al VCS" es correcto). La enumeración nueva del Paso 1 es exacta archivo por archivo; el contenido del `.gitignore` del Paso 5 es razonable y su mini-verificación es ejecutable.
- **G-01-4 (guia-04) correcto**: el schema `Error` (`detail: str`, requerido) coincide campo por campo con `contrato_api.yaml:51-57`; la sintaxis `responses={404: {"description": ..., "model": Error}}` es FastAPI válido y la descripción "Producto inexistente (o inactivo)" es palabra por palabra la del contrato (línea 199); la prosa docente es técnicamente exacta (FastAPI no documenta en OpenAPI los `raise HTTPException` de runtime; sin la declaración el panel lista 200+422); el `import` de `Error` en el router resuelve contra el Paso 1 de la misma guía.
- **Coherencia inter-guías preservada**: las dos menciones al `.gitignore` en guia-03 (líneas 553 y 612, "ya lo excluye") siguen siendo ciertas porque el alumno llega a la guía 3 con el archivo creado en el Paso 5 de guia-01; `FamiliaAromatica` y `get_session`/`SessionLocal` (importados por los bloques mostrados) existen tal cual en guia-03.

**Problemas:** tres warnings y un info. Los dos primeros re-verifican los desvíos contrato ↔ `/docs` que el review de fase ya había reportado y el plan 01-06 dejó conscientemente abiertos ("dirección del fix: guía -> contrato, contrato intacto") — se re-reportan porque las regiones nuevas los hacen más visibles que antes y siguen sin advertencia en la ruta del alumno. El tercero es nuevo: la fila 11, a la que el texto nuevo remite como "la comparación que cierra", no incluye el schema `Error` en la comparación de cierre.

**Nota de numeración:** este reporte reemplaza al review de fase del 2026-09-28. Los IDs `WR-01`/`WR-02` se reutilizan para los mismos defectos (re-anclados en las regiones nuevas, sin pérdida en el disposition); los hallazgos inéditos usan `WR-08`/`IN-09` para no colisionar con las filas open `WR-03`..`WR-07` y `IN-01`..`IN-08` de `01-REVIEW-DISPOSITION.md`, que siguen vigentes y fuera del alcance de este delta.

## Warnings

### WR-01: Contrato omite el 422 de `GET /api/productos/{producto_id}` — el prose nuevo lo hace visible y la fila 11 sigue sin advertirlo

**File:** `docs/05_desarrollo/guia-04-catalogo.md:294-302` (prose nuevo del Paso 3; ver también la fila 11 en `guia-04:945` y `docs/04_arquitectura/contrato_api.yaml:191-203`)
**Issue:** El párrafo nuevo enseña que sin el `responses` el panel "listaría solo 200 y 422" para la ficha — y con la declaración quedan 200, 404 y 422. Pero el contrato declara solo `'200'` y `'404'` para ese path: el 422 automático (validación del path param `producto_id: int`) no existe en `contrato_api.yaml`. El propio texto nuevo remite a la fila 11 ("esa es exactamente la comparación que cierra la fila 11"), que ordena comparar "los códigos de respuesta (200, 404, 422)" UNO A UNO bajo el protocolo "cualquier diferencia entre el panel y el contrato es un desvío" (`guia-04:947-949`): el alumno encuentra un 422 en `/docs` que el contrato no declara, sin que la guía le diga que es un desvío del contrato (no de su código) ni cómo resolverlo. Re-verificación del WR-01 del review de fase (disposition: open); el UAT test 4 confirmó que el alumno topa con desvíos no advertidos en esa fila. El delta cerró el eje 404 pero dejó este eje más expuesto que antes: ahora el prose lo nombra explícitamente sin resolverlo.
**Fix:** Elegir un lado (la regla de la propia guía no admite el silencio): (a) versionar `contrato_api.yaml` añadiendo el 422 al path de la ficha —
```yaml
# en paths./api/productos/{producto_id}.get.responses, junto a '200' y '404':
        '422':
          description: Path parameter mal formado (producto_id no entero)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
```
— o (b) una oración en el Paso 3 (región ya tocada por este delta) que nombre el desvío: "el 422 que verás junto al 404 es la validación del path param; el contrato aún no lo declara — desvío conocido del contrato, no un error de tu código".

### WR-02: `Error` presentado como "el cuerpo de los errores" — el 422 real de FastAPI trae `detail` como array, no string

**File:** `docs/05_desarrollo/guia-04-catalogo.md:87-89` (prose nuevo del Paso 1; ver `contrato_api.yaml:51-57` y `171-176`)
**Issue:** La oración nueva presenta `Error` como "el cuerpo de los errores (`{"detail": "…"}`)". Es exacta para el 404 (string), pero el contrato referencia el mismo schema `Error` para el 422 de `GET /api/productos` (contrato:171-176), y el 422 real que FastAPI produce y documenta en `/docs` usa `detail` como ARRAY de objetos (`HTTPValidationError`: `loc`, `msg`, `type`). El alumno que compara el 422 del panel contra el contrato en la fila 11 encuentra que ni la forma del cuerpo ni el schema coinciden — otro desvío no advertido, ahora reforzado por una generalización ("los errores") que solo el 404 cumple. Re-verificación del WR-02 del review de fase (disposition: open).
**Fix:** (a) Acotar la frase en la región nueva: "el cuerpo del 404 de la ficha — y, según el contrato, también del 422; ojo: el 422 real de FastAPI trae `detail` como array, desvío conocido del contrato" — o (b) versionar el contrato con un schema separado `ValidationError` (`detail`: array de `{loc, msg, type}`) referenciado en las respuestas 422, dejando `Error` con `detail: string` exclusivamente para el 404.

### WR-08: La fila 11 — invocada por el texto nuevo como "la comparación que cierra" — no incluye el schema `Error` en la comparación de schemas

**File:** `docs/05_desarrollo/guia-04-catalogo.md:945` (fila 11; remitida desde la mini-verificación 5 nueva en `guia-04:335-339`)
**Issue:** La celda de schemas de la fila 11 dice "los schemas (`ProductoResumen` con 6 campos, `ProductoDetalle` con 9)" — omite `Error`, el tercer schema del contrato y justamente el que este delta añadió (Paso 1) para cerrar G-01-4. El texto nuevo llama a la fila 11 "exactamente la comparación que cierra" la fase, pero la evidencia formal de cierre no verifica `Error` contra el contrato: la mini-verificación 5 solo hace ver el esquema en el panel, sin comparar sus campos con `contrato_api.yaml:51-57`. Si el schema enseñado divergiera del contrato (p. ej. `detail` con otro tipo), la tabla de cierre no lo detectaría.
**Fix:** Extender la celda de la fila 11: "los schemas (`ProductoResumen` con 6 campos, `ProductoDetalle` con 9, `Error` con `detail` string)".

## Info

### IN-09: El `.gitignore` se crea en el Paso 5, pero `.venv/` existe desde el Paso 3 — ventana sin cobertura para quien commitea temprano

**File:** `docs/05_desarrollo/guia-01-proyecto-backend.md:300-303` (creación del `.gitignore`; `.venv/` nace con `uv add` en `guia-01:133-141`)
**Issue:** El `.gitignore` se crea recién en el Paso 5, mientras que `.venv/` existe desde el Paso 3 y `maura.db` existirá desde la guía 3. Un alumno que haya hecho `git init` en la raíz (caso que la propia mini-verificación del Paso 1 contempla: "si es que ya hiciste `git init` en tu monorepo") y commitee sus avances antes del Paso 5 trackea el entorno virtual completo. El flujo instruido está a salvo (la guía no pide commitear antes de guia-04), así que la ventana es solo para el alumno que commitea por su cuenta — pero cerrarla es gratis.
**Fix:** Mover la creación del archivo al Paso 1 (la nota nueva "Lo creas tú en el paso 5" pasaría a ser "lo creas ahora mismo, aquí abajo"), o añadir al Paso 5 "— antes de tu primer commit".

---

_Reviewed: 2026-09-29T12:25:31Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
