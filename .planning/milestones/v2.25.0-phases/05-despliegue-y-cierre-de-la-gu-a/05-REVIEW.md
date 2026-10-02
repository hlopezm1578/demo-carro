---
phase: 05-despliegue-y-cierre-de-la-gu-a
reviewed: 2026-10-01T12:00:00Z
depth: standard
files_reviewed: 13
files_reviewed_list:
  - docs/04_arquitectura/adr/019-despliegue-free-tier-vercel-render.md
  - docs/04_arquitectura/adr/020-persistencia-efimera-seed-idempotente.md
  - docs/07_despliegue.md
  - docs/06_pruebas.md
  - docs/08_mantenimiento.md
  - docs/05_desarrollo/guia-16-despliegue-api.md
  - docs/05_desarrollo/guia-17-despliegue-frontend.md
  - docs/05_desarrollo/guia-18-despliegue-cierre.md
  - docs/04_arquitectura/README.md
  - docs/05_desarrollo/guia-15-asistente-cierre.md
  - docs/05_desarrollo/README.md
  - docs/README.md
  - README.md
findings:
  critical: 1
  warning: 4
  info: 3
  total: 8
status: issues_found
---

# Phase 5: Code Review Report

**Reviewed:** 2026-10-01T12:00:00Z
**Depth:** standard
**Files Reviewed:** 13
**Status:** issues_found

## Summary

Revisión adversarial del corpus de la fase 5 (8 documentos nuevos + 5 modificados), tratados como lo que son: guías educativas cuyos bloques de código el alumno copia, y documentos de registro. Cada afirmación factual se verificó contra el corpus bloqueado (guias 01-15, ADRs 001-018, REQUIREMENTS, `05-RESEARCH.md` como verdad de referencia) y contra los archivos citados byte a byte.

Verificado y CORRECTO (muestra del cruce completo): el triple congelado (`BACKEND_URL`/`CORS_ORIGINS` JSON/`VITE_API_URL`) calza con `config.py` de guia-01/05/09 y `api.ts` de guia-04 (citas byte-exactas confirmadas en guia-02:414-417 y guia-04:760-763); `PYTHON_VERSION=3.12.10` vs techo Transbank vs default 3.14.3 de Render; `vercel.json` rewrite `/(.*)` → `/index.html`; build/start commands de Render; conteos 18 guías / 20 ADRs / contrato quieto en 0.4.0 (D-66); tarjetas y cronometrajes de la fase 3 (603 s, 22-78 s, 9 veces, `error.cgi` — todos en `03-SPIKE-RETORNO.md`); rutas (`/checkout`, `/pedidos`, `/admin/pedidos`, `/pago/resultado` pública fuera de `RequireAuth`); copys heredados ("¡Gracias por tu compra!", "No tenemos un resultado que mostrarte", "puerto 8000", "¡Últimas 2 unidades!", `?familia=vinagre`→422); IDs de requerimientos (PAY-02..05, RN-11, RN-15, AUTH-04, CART-02/03, ADMN-04/05, STORE-05, ORDR-03, STAKE-01..04, AIAS-03, RNF-09, DEPL-01/02, GUIDE-01); cifras Groq 30 RPM / 1.000 RPD (D-68 corregido); decisiones citadas (D-44, D-48, D-27, D-70, D-73); 12 SKU del seed; `--vcs none` y `.gitignore` de guia-01/03; conteos de filas de las Gran verificaciones (11/12/12/13); todos los links relativos de los 8 archivos nuevos resuelven; invariante honest-doc D-73 respetado (ningún documento claims runtime propio del proyecto; guia-16 lleva el blockquote explícito y ADR-019 declara "NO reporta runtime propio"); seguridad enseñada correcta (secretos solo en env vars, `SECRET_KEY` nueva por entorno, CORS lista explícita JSON, grep del build como control AIAS-03, sin keys/URLs reales — todo placeholder).

Se encontró 1 defecto CRÍTICO en un bloque de código que la guía enseña (la variante PowerShell del grep del build no escanea el bundle real, rompiendo el control positivo y dando falso verde al control de seguridad), 4 WARNINGS (marcador de seed inventado en doc 06; cita de empty state del historial con el copy del panel admin; afirmación de "revivencia" de la capa build que excede la evidencia citada; comando de `SECRET_KEY` sin `uv run`) y 3 INFOS.

## Critical Issues

### CR-01: La variante PowerShell del grep del build no escanea `dist/assets/` — el control positivo siempre falla y el control de seguridad da falso verde

**File:** `docs/05_desarrollo/guia-17-despliegue-frontend.md:226-231` (y replicado en `docs/05_desarrollo/guia-18-despliegue-cierre.md:297`, fila 7 de la Gran verificación final)
**Issue:** `Select-String -Path dist\* -Pattern "onrender.com"` NO es recursivo: `dist\*` solo alcanza los archivos del primer nivel de `dist/` (`index.html`, favicon). La URL pública horneada vive en los chunks de JS de `dist/assets/*.js`, que quedan fuera del escaneo. Consecuencias, ambas graves:
1. **Control positivo roto:** el alumno que sigue la rama PowerShell ve cero coincidencias para `onrender.com` y concluye que el reemplazo estático de `VITE_API_URL` falló — cuando funcionó. La guía lo dice explícitamente al revés: "el primer grep ENCUENTRA la URL pública".
2. **Control de seguridad (AIAS-03) inválido:** `Select-String -Path dist\* -Pattern "GROQ_API_KEY"` da "cero resultados" sin haber mirado un solo archivo `.js` — exactamente el falso negativo que el grep del build existe para impedir. La fila 7 de la Gran verificación final de la serie (guia-18) canónica este comando como la verificación de seguridad en producción, y doc 06 (`docs/06_pruebas.md:109`) enseña "Control positivo SIEMPRE antes de celebrar el cero" — el comando enseñado derrota su propio método.

Nota de alcance: el patrón se hereda de guia-15:530 (fase 4, fuera de este diff), pero esta fase lo REPLICÓ y lo EXTENDIÓ al control positivo (guia-17 Paso 5 usa la variante PowerShell para ambos greps) y lo elevó a fila de cierre de la serie.
**Fix:**
```powershell
# PowerShell — recursivo sobre TODO el bundle (equivalente a grep -r)
Get-ChildItem -Recurse -File dist | Select-String -Pattern "onrender.com"   # control positivo: SÍ encuentra
Get-ChildItem -Recurse -File dist | Select-String -Pattern "GROQ_API_KEY"   # cero resultados = éxito real
```
Aplicar el reemplazo en guia-17 Paso 5, en la fila 7 de guia-18 y (por la regla de fix en ambos lugares que aplica a bugs de guía) en la fila 13 de guia-15, más la mención espejo en `docs/06_pruebas.md:109` si cita el comando.

## Warnings

### WR-01: doc 06 inventa un marcador de seed que no existe (`[-]`) y arma un escenario confuso

**File:** `docs/06_pruebas.md:70-71`
**Issue:** "Cuando en la guía 3 el seed imprimió once `[+]` y un `[-]` donde esperabas doce `[=]`…". El seed real solo imprime `[+]` (creado) y `[=]` (actualizado) — verificado en guia-03:246-247, 280-287 y 482-483; el marcador `[-]` no existe en el vocabulario del seed. Además el escenario mezcla corridas: los `[=]` son el comportamiento de la SEGUNDA corrida, no algo que se "espere" en la misma pasada donde algo se crea. Un doc de registro que nombra el método de pruebas no puede citar marcadores inventados.
**Fix:** Reescribir con marcadores reales, p. ej.: "Cuando en la guía 3 la segunda corrida del seed imprimió un `[+]` donde esperabas doce `[=]`, no necesitaste debugger: algo borró la BD entre corridas y el paso anterior era el culpable, a una pantalla de distancia."

### WR-02: El empty state del historial de la clienta se cita con el copy del panel admin

**File:** `docs/05_desarrollo/guia-18-despliegue-cierre.md:268-269`, `docs/04_arquitectura/adr/020-persistencia-efimera-seed-idempotente.md:85-86`, `docs/07_despliegue.md:103-104`
**Issue:** Los tres citan "Todavía no hay pedidos" como el empty state del historial de la clienta. Verificado: el copy del historial de la clienta es **"Todavía no tienes pedidos"** (guia-11:143); "Todavía no hay pedidos" es el empty state del PANEL ADMIN (guia-13:1146). En una serie que exige citas byte-exactas y whose fila 9 de la Gran verificación final exige "paridad cero drift", un copy atribuido a la pantalla equivocada es un defecto que el alumno detectará al comparar (guia-18 Paso 6 le pide observar exactamente esa pantalla).
**Fix:** Reemplazar por "Todavía no tienes pedidos" en los tres lugares (o, si se quiere citar ambos, distinguir: historial clienta vs panel admin).

### WR-03: La capa build-time "SIEMPRE revive" se afirma como hecho, pero la evidencia citada no cubre la revivencia (supuesto A5 no señalado)

**File:** `docs/04_arquitectura/adr/020-persistencia-efimera-seed-idempotente.md:51-57,71-73`, `docs/07_despliegue.md:92-98`, `docs/05_desarrollo/guia-16-despliegue-api.md:106-113`
**Issue:** ADR-020 (decisión 3 y Consecuencias), doc 07 y guia-16 afirman incondicionalmente que la imagen del build revive con la BD sembrada ("SIEMPRE revive", "El catálogo NO se pierde nunca", "El catálogo siempre vuelve"). La cita documental que los funda (render.com/docs/free) solo cubre que los cambios al filesystem **se pierden**; que los archivos escritos durante el BUILD sobreviven a la imagen que arranca en runtime es el supuesto A5 de `05-RESEARCH.md`, registrado ahí explícitamente como **interpretación** ("las docs dicen que los cambios al filesystem se pierden, pero el detalle de qué revive es interpretación — Risk if wrong: la lección D-70 cambia de matiz"). El propio research resolvió que ese supuesto quedaría "señalado" y que su confirmación es del alumno (guia-18 Paso 6), pero los tres documentos públicos lo presentan como certeza sin señal alguna — por debajo de la vara de honestidad documental que la serie aplica a toda cifra de terceros ("a la fecha") y que D-73 fijó para este ADR.
**Fix:** Añadir una cláusula honesta en ADR-020 (decisión 3) y/o doc 07: p. ej. "La revivencia de la capa del build es el modelo de imagen de Render que las docs describen indirectamente (lo perdido son los cambios al filesystem, no el build); guia-18 Paso 6 la confirma en TU dato — si tu observación difiere, es un hallazgo y se registra". La afirmación de "siempre" queda así respaldada por la verificación que la guía ya define.

### WR-04: El comando de la `SECRET_KEY` perdió el prefijo `uv run` y el contexto de directorio que la serie estableció

**File:** `docs/05_desarrollo/guia-16-despliegue-api.md:174-179` (también 329 y 358; espejado en `docs/07_despliegue.md:160`)
**Issue:** guia-16 presenta "el comando de siempre" como `python -c "import secrets; print(secrets.token_hex(32))"`. El comando de siempre NO es ese: guia-05:86 enseña `uv run python -c "import secrets; print(secrets.token_hex(32))"` ejecutado desde `backend/`. El taller del alumno puede tener Python solo vía uv (los runtimes de uv no viven en el PATH por defecto), en cuyo caso `python` no resuelve y el alumno queda clavado en mitad del deploy con "python: command not found" — o peor, genera la key con otro Python inexistente. Además guia-16 no dice desde qué directorio correrlo (en guia-16 el alumno está en la raíz del proyecto, donde `uv run` sin `--directory` tampoco calzaría).
**Fix:** `cd backend && uv run python -c "import secrets; print(secrets.token_hex(32))"` (o `uv run --directory backend python -c ...` desde la raíz), y propagar el comando completo a las dos repeticiones internas de guia-16 y a la fila de doc 07.

## Info

### IN-01: guia-16 atribuye `cors_origins` a "las guías 5 y 9" cuando nació en la guía 1 (doc 07 lo dice bien)

**File:** `docs/05_desarrollo/guia-16-despliegue-api.md:146-148`
**Issue:** "ya viven en tu `backend/app/config.py` desde las guías 5 y 9" — correcto para `SECRET_KEY`/`ADMIN_*`/`CLIENTE_*` (guía 5) y `backend_url` (guía 9), pero `cors_origins` está en `config.py` desde la guía 1 (guia-01:203, con el CORS ya compuesto en `main.py`). doc 07:28-29 lo afirma correctamente ("`CORS_ORIGINS` desde la primera guía del backend") — los dos documentos nuevos se contradicen entre sí en la procedencia de la misma variable.
**Fix:** "…ya viven en tu `backend/app/config.py` desde la guía 1 (`cors_origins`), la 5 (`SECRET_KEY`, cuentas) y la 9 (`backend_url`)".

### IN-02: Gramática rota en la tabla de errores típicos de doc 06

**File:** `docs/06_pruebas.md:107`
**Issue:** "La fila de la Gran verificación quedó marcada… y no la corrido" — elipsis gramatical inválida en español (falta el verbo conjugado: "y no la corriste" / "sin haberla corrido"). Es un documento de registro del ciclo; el resto del corpus cuida la prosa.
**Fix:** "quedó marcada… y no fue corrida" o "…y no la corriste tú".

### IN-03: guia-18 suma "guard de sesión" a la ruta que la fase 3 dejó deliberadamente pública

**File:** `docs/05_desarrollo/guia-18-despliegue-cierre.md:81-82`
**Issue:** La mini-verificación del deep-link frío a `/pago/resultado` dice "rewrite + ruta pública + guard de sesión, todo el eslabón 6 y 7 vivo". `/pago/resultado` es pública POR DISEÑO y vive FUERA de `RequireAuth` (guia-10:212-225 — la lección explícita de la fase 3: el 302 llega sin sesión y la pantalla degrada con honestidad, con login+`returnTo` como CTA, no como guard). La expectativa descrita (cara honesta "No tenemos un resultado que mostrarte") es correcta; el rótulo "guard de sesión" confunde la lección que la propia guía 18 está cerrando.
**Fix:** "rewrite + ruta pública (fuera del guard, por diseño de la fase 3) + degradación honesta sin sesión — todo el eslabón 6 y 7 vivo".

---

## Nota de verificación (positiva)

Se verificó además, sin hallazgos: la quinta corrida de tablas (docs/README.md, README.md, 04_arquitectura/README.md con filas 019/020 e índice a 20), el "Siguiente" de guia-15 ahora apuntando a guia-16 con el conteo 20 ADRs corregido, la cadena Siguiente continua 16→17→18→docs 06/07/08, el mapa mental de 05_desarrollo/README.md (fases y rangos de guías correctos), el gate negativo del contrato (0.4.0 quieto, sin bump — verificado en `contrato_api.yaml:13`), y la ausencia de secretos/URLs reales en los nuevos documentos (solo placeholders `<tu-servicio>`/`<tu-proyecto>`, docs oficiales y datos públicos de integración Webpay).

_Reviewed: 2026-10-01T12:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
