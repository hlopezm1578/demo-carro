# Phase 5: Despliegue y cierre de la guía - Pattern Map

**Mapped:** 2026-10-01
**Files analyzed:** 11 archivos del repo (8 nuevos + 3 editados) + 3 índices de `.planning/` (cierre de workflow)
**Analogs found:** 11 / 11 (todos con análogo tracked; 2 con match de formato cuyo contenido diverge a propósito)

> **Nota de dominio (leer antes de usar esta tabla):** este repo es **guide-only (D-17)** — no existe
> código de aplicación; el "codebase" es el corpus documental bajo `docs/`. Los *roles* de la tabla son
> roles documentales y el *data flow* es el flujo que cada documento enseña o registra. La fase es
> **SOLO escritura (D-73)**: el proyecto NO deploya ni prueba nada; las guías 16+ definen
> mini-verificaciones y una Gran verificación final **que el alumno corre en sus cuentas**. La
> verificación de planes/fase del proyecto es documental (greps/estructura).
>
> **Tracked-source gate:** todos los análogos nombrados fueron verificados con `git ls-files` en su
> repo respectivo (`demo-carro` y `demo-cine` — ambos tracked en su propio repo; `D:/Repos/demo-cine`
> es el repo hermano real, no un espejo gitignored).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `docs/05_desarrollo/guia-16-*.md` (deploy API en Render) | guía paso a paso | config/build (batch) | `docs/05_desarrollo/guia-15-asistente-cierre.md` (estructura canónica) + `D:/Repos/demo-cine/docs/07_despliegue.md` (contenido deploy) | exact (estructura) / format-match (contenido) |
| `docs/05_desarrollo/guia-17-*.md` (deploy SPA + fallback Vercel) | guía paso a paso | config/build + request-response (rewrite SPA) | `guia-15` (estructura) + demo-cine 07 Paso 2 (tabla de configuración de plataforma) | exact (estructura) / format-match (contenido) |
| `docs/05_desarrollo/guia-18-*.md` (4 flujos en producción + Gran verificación final de la serie) | guía de cierre de fase | request-response (retornos Webpay) | `guia-15` (cierre de fase: Gran verificación + Siguiente) | exact |
| `docs/04_arquitectura/adr/019-*.md` (despliegue free tier Vercel + Render) | ADR | decision-record | `docs/04_arquitectura/adr/018-asistente-ia-groq-structured-outputs.md` (evidencia documental con URLs) + `D:/Repos/demo-cine/docs/04_arquitectura/adr/007-despliegue-render-y-neon.md` (ADR de deploy) | exact |
| `docs/04_arquitectura/adr/020-*.md` (persistencia efímera + seed como estrategia) | ADR | decision-record | `docs/04_arquitectura/adr/012-retorno-de-webpay.md` (consecuencias honestas) + demo-cine ADR-007 §Negativas (disco efímero "mostrarlas, no esconderlas") | exact |
| `docs/06_pruebas.md` (NUEVO) | doc de fase del ciclo (síntesis del método) | síntesis | `D:/Repos/demo-cine/docs/06_pruebas.md` | format-match (contenido diverge: síntesis, no suite — ver No Analog) |
| `docs/07_despliegue.md` (NUEVO) | doc de fase del ciclo | procedural (deploy) | `D:/Repos/demo-cine/docs/07_despliegue.md` | exact (formato) — contenido diverge en D-70 |
| `docs/08_mantenimiento.md` (NUEVO) | doc de fase del ciclo (cierre prospectivo) | síntesis prospectiva | `D:/Repos/demo-cine/docs/08_mantenimiento.md` | exact (formato) |
| `docs/README.md` (EDIT) | índice / tabla de estado del ciclo | batch (actualización de estado) | el mismo archivo — el cierre de la fase 4 dejó filas 5-8 (docs/README.md:19-22) | exact |
| `README.md` raíz (EDIT) | portada + tabla de estado + stack telegráfico | batch | el mismo archivo — README.md:36-50 (tabla) y 70-76 (stack) | exact |
| `docs/05_desarrollo/README.md` (EDIT) | índice de guías + mapa mental | batch | el mismo archivo — líneas 24-40 (tabla), 42-46 (nota de cierre), 48-72 (mapa mental) | exact |
| `.planning/REQUIREMENTS.md`, `ROADMAP.md`, `PROJECT.md` (EDIT) | índices de planificación GSD | batch | convención de cierre del workflow (estado actual citado abajo) | exact (mechanical) |

## Pattern Assignments

### `docs/05_desarrollo/guia-16-*.md` — deploy de la API en Render (guía paso a paso, config/build)

**Analog estructural:** `docs/05_desarrollo/guia-15-asistente-cierre.md` (la última guía de la serie — el molde vigente)
**Analog de contenido:** `D:/Repos/demo-cine/docs/07_despliegue.md` (deploy de API paso a paso con tablas de plataforma)

**Estructura canónica de guía** (guia-15 — cada sección con su línea de referencia; las guías 16+ replican el orden completo):

| Sección | Referencia en guia-15 |
|---|---|
| Título `# Guía N — ...` + blockquote de cabecera (**Qué construirás hoy / Al terminar tendrás / Necesitas**) | líneas 1-15 |
| `## Los términos de hoy (antes de copiar nada)` — tabla `\| Término \| Qué es, en una frase \|` | líneas 19-28 |
| `## Paso N — título` con bloque 🧠 **El desarrollador piensa** narrando decisiones (con D-xx y ADR citados) + bloque de código para copiar + `✅ **Mini-verificación:**` | líneas 31-93 (Paso 1 completo como muestra) |
| `## ✅ Gran verificación final` — tabla `\| # \| Verificación \| Origen \|` | líneas 509-530 |
| `**Sugerencia de commit para cerrar la fase**` (bloque git) | líneas 544-553 |
| `## ❌ El error que este archivo evita` — pares ❌/✅ en código | líneas 557-632 |
| `## ✅ Verificación de la guía N` — lista numerada | líneas 635-652 |
| `## 📝 Punto de control (respóndelas sin mirar la guía)` — preguntas con referencia (D-xx/RN-xx) | líneas 654-675 |
| `## Lo que acabas de aprender` — bullets de cierre | líneas 677-703 |
| `**Siguiente:** ...` — enlace a la guía/próxima pieza | líneas 705-709 |

**Cabecera de guía** (guia-15:1-15, abreviada — guia-16 abre igual, con "Necesitas: las guías 1 a 15 completas y TU app corriendo local"):

```markdown
# Guía 15 — La burbuja en la tienda: la cara visible de la IA y el cierre de la fase 4

> **Qué construirás hoy:** ... y la **Gran verificación final** de la
> fase 4 completa: ...
> **Al terminar tendrás:** ...
> **Necesitas:** las guías 1 a 14 completas — ...
```

**Mini-verificación** (guia-15:90-93 — el formato exacto que cada paso de guia-16/17/18 cierra; en deploy: log del build, `/api/salud` en la URL pública, etc.):

```markdown
✅ **Mini-verificación:** `npm run build` pasa — y el experimento del
compilador de siempre, ahora con la ausencia que importa: ...
```

**Contenido deploy — tabla de configuración de plataforma** (demo-cine 07:62-70 — el molde de la tabla del Web Service que guia-16 replica con los valores del research: Root Directory `backend`, Build `uv sync --locked && uv run python -m app.seed`, Start `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`, `PYTHON_VERSION=3.12.x`):

```markdown
| Campo | Valor |
|---|---|
| Runtime | **Python 3** |
| Build Command | `pip install -r requirements.txt && python semilla.py` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Instance Type | **Free** |
```

**Tabla de env vars del dashboard** (demo-cine 07:74-85 — guia-16 la replica con el triple congelado: `BACKEND_URL`, `CORS_ORIGINS` (JSON array, Pitfall 4), `SECRET_KEY` nueva + `ADMIN_*`/`CLIENTE_*`/`GROQ_API_KEY`; incluye el comando de la key digna):

```markdown
| Clave | Valor |
|---|---|
| `SECRET_KEY` | un secreto largo y aleatorio — genera uno con el comando de abajo |
| `ADMIN_PASSWORD` | una contraseña digna (no `admin1234`…) |

python -c "import secrets; print(secrets.token_hex(32))"
```

**Tabla de errores típicos con diagnóstico** (demo-cine 07:118-126 — NUEVA para esta guía: los Pitfalls 1/4/5/9 del research (`requires-python` vs 3.14.3, `CORS_ORIGINS` sin JSON, `SECRET_KEY` heredada) calzan exacto en este molde `| Síntoma | Causa | Remedio |`):

```markdown
| Síntoma | Causa | Remedio |
|---|---|---|
| El deploy muere con `ModuleNotFoundError: No module named 'psycopg2'` | `requirements.txt` sin el driver **en GitHub** | Paso 0 completo: instalar, regenerar, commit, push |
| La app parte, pero el login rechaza tus credenciales correctas | La tabla `usuarios` está vacía | Build Command con `&& python semilla.py` (Paso 3) |
```

**Anclas de integración que guia-16 parameteriza** (verificado byte-exacto; las guías las citan, NO las reescriben — D-73: el deploy no cambia código):
- `guia-09:597-603` — el bloque `backend_url` en `config.py` cuyo comentario YA promete esta fase:
  ```python
  # --- Etapa 3: pago Webpay (ADR-012) ---
  # La URL pública del BACKEND: a ella vuelve el navegador desde Webpay
  # (return_url). NO es cors_origins — esa es la SPA. Dev y producción
  # difieren; la fase 5 la congela junto con el origen público.
  backend_url: str = "http://localhost:8000"
  ```
- `guia-09:685` — `return_url=f"{settings.backend_url}/api/pago/retorno",`
- `guia-09:1042-1054` — `_hacia_spa`: `url = f"{settings.cors_origins[0]}/pago/resultado?{urlencode(params)}"` + `RedirectResponse(url, status_code=302)`
- `guia-01:331-333` — la promesa del arranque de producción: "El equivalente de producción (`fastapi run`, sin recarga) **llegará en la fase de despliegue**"

---

### `docs/05_desarrollo/guia-17-*.md` — deploy del frontend + fallback SPA en Vercel (guía paso a paso)

**Analog estructural:** `guia-15` (misma tabla de secciones que guia-16)
**Analog de contenido:** demo-cine 07 Pasos 0-2 (requisitos en el repo + tabla de plataforma) — adaptado al tier estático

**Piezas específicas de esta guía:**
- El `vercel.json` con rewrite (RESEARCH Pattern 2, citado de vercel.com KB) va como bloque de código para copiar, con la advertencia de que debe quedar **commiteado junto al `package.json` del frontend** (Pitfall 7) — misma forma que cualquier bloque de código de guia-15 (bloque + 🧠 narrando el porqué + ✅ mini-verificación).
- La mini-verificación ES el caso de uso DEPL-02: refresh/deep-link de `/carro` o `/pago/resultado` → 200 con la SPA, no 404 (demo-cine 07 usa el mismo estilo de verificación observable en la URL pública, líneas 129-138).
- `VITE_API_URL` SIN slash final + "todo cambio exige redeploy" (Pitfall 3): anclar narrativamente en `guia-02:416-418` (verbatim abajo), la promesa que esta guía cobra:
  ```markdown
  `VITE_API_URL` es una variable de entorno de Vite: vacía (o ausente) en
  desarrollo — el proxy hace el trabajo — y la URL pública de la API en
  producción (fase de despliegue).
  ```
- El grep del build (AIAS-03, guia-15 fila 13) se EXTIENDE aquí al bundle de producción: grep de la URL pública (control positivo) además de `GROQ_API_KEY` → cero (guia-15:530 tiene el comando por shell — Git Bash vs PowerShell — que se copia tal cual).

---

### `docs/05_desarrollo/guia-18-*.md` — los 4 flujos en producción + Gran verificación final de la serie (guía de cierre)

**Analog:** `guia-15` — es la guía de cierre de la fase 4; guia-18 cierra la fase 5 Y la serie completa.

**Gran verificación final — forma exacta de la tabla** (guia-15:509-530; guia-18 replica el molde con las filas de deploy: refresh sin 404, 4 flujos contra el ambiente desplegado, contrato 0.4.0 ↔ `/docs` público, grep del build en producción — D-73: la tabla la DEFINE para el alumno, el proyecto no la ejecuta):

```markdown
## ✅ Gran verificación final de la fase 4

La tabla de cierre del ciclo — como en las fases 1, 2 y 3, cada fila
cita su origen y se marca solo si TÚ la comprobaste. ...

| # | Verificación | Origen |
|---|---|---|
| 1 | Roles en `/docs` con las cuentas del seed: ... | RF-19..RF-22, D-55, ADR-015 |
| 12 | **Contrato ↔ `/docs`**: abre `http://localhost:8000/docs` y compara UNO A UNO contra `docs/04_arquitectura/contrato_api.yaml` **0.4.0**: ... | ADR-007, GUIDE-02, ... |
| 13 | **El grep del build** (AIAS-03): `npm run build` y, DESPUÉS de que termine, busca `GROQ_API_KEY` en el `dist/` regenerado — **CERO coincidencias** ... | RNF-09, AIAS-03, D-60 |
```

Nota: la fila contrato ↔ `/docs` y la fila grep del build (guia-15:529-530) son FIJAS por convención de serie — guia-18 las hereda cambiando `localhost:8000` por la URL pública y el contrato se queda en **0.4.0** (D-66: no bump sin churn).

**Sugerencia de commit de cierre** (guia-15:544-553 — mismo bloque, texto de la fase 5).

**Cierre de la serie** — el "**Siguiente:**" de guia-15 (líneas 705-709) es el eslabón que guia-16 retoma; el de guia-18 no apunta a otra guía sino al cierre del ciclo (docs 06/07/08) — el molde de ese cierre narrativo está en demo-cine 08:130-135 ("El ciclo se cierra (y se reabre)", citado abajo en el bloque de doc 08).

---

### `docs/04_arquitectura/adr/019-*.md` — despliegue free tier: Vercel + Render (ADR)

**Analog de forma + evidencia:** `docs/04_arquitectura/adr/018-asistente-ia-groq-structured-outputs.md`
**Analog de contenido:** `D:/Repos/demo-cine/docs/04_arquitectura/adr/007-despliegue-render-y-neon.md`

**Cabecera ADR** (ADR-012:1-5 — molde de las 18 existentes; ADR-019/020 continúan la numeración y el formato exacto):

```markdown
# ADR-012 — El retorno de Webpay: 302 hacia la ruta única de la SPA, discriminando por presencia de params

- **Estado:** Aceptada
- **Fecha:** 2026-09-30
- **Resuelve:** cómo vuelve el navegador de la clienta desde el formulario de Webpay a la tienda, y cómo el backend distingue los 4 flujos oficiales del retorno (PAY-02)
```

**Evidencia DOCUMENTAL (D-73 — la clave de este ADR):** ADR-019 firma con fuentes oficiales citadas con URL y "a la fecha", NO con spike runtime (D-72 superseded). El molde es la sección **"Evidencia firmada"** de ADR-018 (líneas 144-185), que citó docs oficiales con URL bajo la disciplina D-68. Ejemplo del formato de cita (ADR-018:152-157):

```markdown
- **Doc oficial de límites**
  ([console.groq.com/docs/rate-limits](https://console.groq.com/docs/rate-limits),
  leída 2026-10-01): tabla verbatim `openai/gpt-oss-120b | 30 | 1K | 8K |
  200K` (RPM/RPD/TPM/TPD); ...
```

ADR-019 replica esto con las fuentes de `05-RESEARCH.md` §Sources (render.com/docs/free, render.com/docs/deploy-fastapi, render.com/docs/python-version, render.com/changelog uv, vercel.com KB del rewrite, vercel.com/docs/plans/hobby — todas ya con URL en el research, mismas que las guías citan). El vínculo al documento de fase también sigue el molde: ADR-018:148-150 enlaza `04-RESEARCH.md` con ruta relativa `../../../.planning/...`.

**Tabla de opciones consideradas** (demo-cine ADR-007:11-19 — molde exacto: plataformas alternativas como filas con "A favor/En contra"; ADR-019 lista Vercel+Render como elegida y Netlify/Cloudflare/Fly/Railway como descartadas):

```markdown
| Opción | A favor | En contra |
|---|---|---|
| **C. Render (web service free) + Neon (Postgres free)** | Deploy automático desde GitHub; capas gratis permanentes; sin tarjeta | El servicio **duerme** tras inactividad; el disco es efímero |
| **D. Vercel serverless** | Gama alta de DX | El modelo serverless cambia la forma del código |
```

**Consecuencias negativas "mostrarlas, no esconderlas"** (demo-cine ADR-007:35-39 — ADR-019 las hereda casi por título: hibernación 15 min/wake ~1 min, disco efímero, free tier no es producción seria):

```markdown
**Negativas (mostrarlas, no esconderlas)**

- **Hibernación:** tras ~15 min sin tráfico el servicio se duerme; el primer visitante espera 30–60 s. ...
- **Disco efímero:** las carátulas subidas desaparecen en cada despliegue (ADR-004). ...
```

**Cierre de ADR** (ADR-012:87-97 — "## Para conversar en clase" con 3 preguntas socráticas; ADR-018:186-191 cierra con "Relacionada:" enlazando ADRs hermanos — ADR-019 enlaza ADR-012 (el retorno que ejercita) y ADR-002/008).

---

### `docs/04_arquitectura/adr/020-*.md` — persistencia efímera + seed idempotente como estrategia (ADR)

**Analog:** `docs/04_arquitectura/adr/012-retorno-de-webpay.md` (ADR de lección con consecuencias honestas) + demo-cine ADR-007 §Negativas

**Estructura completa del ADR-012** (98 líneas — ADR-020 sigue el mismo esqueleto):
1. Cabecera Estado/Fecha/Resuelve (líneas 1-5)
2. `## Contexto` — el problema con la evidencia citada en línea (líneas 7-20; ADR-012 enlaza el spike relativo `../../../.planning/phases/03-.../03-SPIKE-RETORNO.md` en la línea 18 — ADR-020 enlaza `05-RESEARCH.md` §Pitfall 5 y render.com/docs/free, que nombra textualmente "local SQLite databases")
3. `## Opciones consideradas` — tabla A/B/C (líneas 22-28; ADR-020: SQLite efímero + seed vs PostgreSQL Neon ahora vs dominio propio/persistencia pagada)
4. `## Decisión` — "**Opción X.**" + puntos numerados (líneas 30-63)
5. `## Consecuencias` — **Positivas** y **Negativas (honestas)** (líneas 65-85; el formato de negativa honesta con negrita + explicación es la firma de la serie):
   ```markdown
   **Negativas (honestas)**
   - **El resultado viaja en la URL**: `estado` y `orden` quedan visibles en la
     barra de direcciones y el historial del navegador — aceptable para
     una tienda sandbox; el detalle sensible exige sesión.
   ```
   Para ADR-020 la negativa honesta central: los datos RUNTIME (pedidos, cuentas nuevas) se pierden en redeploy/spin-down — solo el catálogo del build revive (Pitfall 5: build-time vs runtime).
6. `## Para conversar en clase` — 3 preguntas (líneas 87-97)

---

### `docs/06_pruebas.md` (NUEVO — síntesis del método de pruebas ya vivido)

**Analog de formato:** `D:/Repos/demo-cine/docs/06_pruebas.md`
**ADVERTENCIA de contenido (D-71):** demo-cine 06 enseña a CONSTRUIR una suite pytest; demo-carro 06 NO — nombra como método lo que el alumno ya vivió (mini-verificación por paso, Gran verificación final por fase, verificación runtime contra Webpay/Groq reales). El molde externo sirve para CABECERA/términos/pasos/verificación/punto de control/aprendizajes/Siguiente; la suite pytest NO se copia.

**Cabecera del doc de fase del ciclo** (demo-cine 06:1-7 — el molde de los tres docs 06/07/08; demo-carro reemplaza "Módulos: ISI601/ISI602" por la línea que use la serie — los docs 01-05 de demo-carro ya tienen su propia cabecera, mantener la de la serie):

```markdown
# Fase 6 — Guía de Pruebas: automatizar lo que verificábamos a mano

> **Módulos:** ISI601 / ISI602 · **Fase del ciclo de vida:** 6. Pruebas
> **Qué construirás hoy:** una suite de pruebas automáticas que ...
> **Al terminar tendrás:** ...
> **Necesitas:** las guías 1 a 8 terminadas (la aplicación funcionando).
> **Fecha:** 2026-08-23
```

**Tabla método ↔ defensa** (demo-cine 06:27-36 — el molde `| Regla / flujo | Origen | La defensa |` que demo-carro 06 adapta a `| Verificación de la serie | Origen | Qué defiende |`: mini-verificación → el paso quedó bien; Gran verificación → el contrato/fase; UAT runtime → la integración real):

```markdown
| Regla / flujo | Origen | La defensa |
|---|---|---|
| Tráiler solo YouTube, 3 formatos | RN-03 | Pruebas de `normalizar_trailer` |
| Una calificación por socio | RN-01 | Calificar + recalificar: el total NO sube |
```

**Secciones de cierre** (demo-cine 06:302-327): `## ✅ Verificación de la guía` (numerada), `## 📝 Punto de control`, `## Lo que acabas de aprender` (bullets) y `**Siguiente:** 07_despliegue.md — ...` (en demo-carro, el Siguiente de 06 apunta a `07_despliegue.md` igual — los tres docs se encadenan entre sí).

---

### `docs/07_despliegue.md` (NUEVO — la decisión de despliegue como fase del ciclo)

**Analog:** `D:/Repos/demo-cine/docs/07_despliegue.md` (160 líneas, leído completo)

**Cabecera con "Decisión de fondo"** (demo-cine 07:1-8 — línea 7 es la clave: ancla el doc a su ADR; demo-carro: "**Decisión de fondo:** ADR-019 (Vercel + Render) **y** ADR-020 (SQLite efímero + seed)"):

```markdown
# Fase 7 — Guía de Despliegue: el gran final (gratis)

> **Módulos:** ISI601 / ISI602 · **Fase del ciclo de vida:** 7. Despliegue
> **Qué construirás hoy:** la publicación real: tu aplicación con URL pública en internet, ...
> **Al terminar tendrás:** ... una lección de arquitectura que ningún slide enseña: el disco efímero.
> **Necesitas:** las guías 1 a 8 terminadas, el proyecto en un repo de GitHub, y una cuenta de correo.
> **Decisión de fondo:** ADR-007 (Render + Neon).
> **Fecha:** 2026-08-23
```

**Tabla de términos de deploy** (demo-cine 07:12-21 — demo-carro reusa Build, Start command, Variable de entorno (en producción), Cold start/hibernación, Disco efímero y agrega los propios: fallback SPA/rewrite, env var horneada `VITE_*`, seed idempotente — listado candidato ya en `05-RESEARCH.md` §Code Examples):

```markdown
| Término | Qué es, en una frase |
|---|---|
| **Build** | El momento en que la plataforma instala tus dependencias ... |
| **Cold start / hibernación** | El plan gratis "duerme" tu app tras ~15 min sin visitas; el próximo visitante espera 30–60 s mientras despierta |
| **Disco efímero** | Los archivos que tu app guarda en el servidor **desaparecen** al reiniciar o re-desplegar. ADR-004, protagonizada hoy |
```

**Estructura de pasos** (demo-cine 07: Paso 0 requisitos en el repo → Paso 1 BD → Paso 2 plataforma → Paso 3 seed → Paso 4 deploy continuo → `## 🔧 Errores típicos` → `## ✅ Verificación` → `## 📝 Punto de control` → `## Lo que acabas de aprender` → enlace final "**Última parada:** `08_mantenimiento.md`" línea 160). demo-carro 07 es un DOC de decisión (no re-pasa los pasos de las guías 16-18: referencia y narra el porqué — D-71: candidata D-69, ADR-019, por qué free tier y por qué la fase va al final/return_url congelado).

**La gran diferencia de contenido (la lección de la serie):** demo-cine 07:140 enseña la lección del disco efímero como EXCEPCIÓN (carátulas perdidas, BD Neon persistente); demo-carro la enseña como DECISIÓN (D-70: SQLite efímero POR DISEÑO + seed idempotente restaurando, PostgreSQL como camino de crecimiento mencionado) — citando render.com/docs/free ("local SQLite databases" entre lo que se pierde) con URL, "a la fecha".

---

### `docs/08_mantenimiento.md` (NUEVO — cierre prospectivo)

**Analog:** `D:/Repos/demo-cine/docs/08_mantenimiento.md` (135 líneas, leído completo)

**Cabecera "nada de código nuevo — construirás la disciplina"** (demo-cine 08:1-8 — el tono prospectivo que demo-carro 08 replica: v2 con los diferidos reales de REQUIREMENTS (PAY-05, ADMN-05, STAKE-*), upgrade a PostgreSQL (D-70), guía viva).

**Tabla de hilo hacia atrás** (demo-cine 08:74-84 — el molde `| Fase | Documento a tocar | El cambio |` que demo-carro 08 usa para los diferidos de v2: cada diferido recorre el ciclo hacia atrás):

```markdown
| Fase | Documento a tocar | El cambio |
|---|---|---|
| 1 | Necesidad | nueva petición P6 con cita de Macarena |
| 2 | Requerimientos | RN-02 v2: estrellas de 0,5 a 5,0 ... |
| 4 | Arquitectura | ... **versión 1.1.0 del contrato, aprobada antes de codificar** (ADR-008) |
```

**Cierre del ciclo** (demo-cine 08:130-135 — la sección final que demo-carro replica como cierre de la SERIE: mapa de lo que queda abierto (sus diferidos) + la pregunta de cierre para llevar a casa):

```markdown
## El ciclo se cierra (y se reabre)

Con las 8 fases recorridas, el proyecto queda **vivo y documentado**: cada decisión con su
porqué, cada regla con su defensa, cada evolución futura con su puerta abierta. Lo que queda
en el mapa son las escaleras que conversamos: ...

> La pregunta de cierre del curso, para llevar a casa: *¿qué tendría que pasarle a ...?*
```

---

### `docs/README.md` (EDIT — filas 5→Lista, 6-8→Listo)

**Analog:** el propio archivo — la corrida de la fase 4 (quinta corrida de D-13/D-18).

**Filas a tocar** (docs/README.md:19-22, estado actual):

```markdown
| 5 | Desarrollo | `05_desarrollo/` (guías paso a paso con razonamiento y código) | 🚧 Parcial (guías 1-15 listas; continúa en fases 5+) |
| 6 | Pruebas | `06_pruebas.md` | ⏳ Pendiente |
| 7 | Despliegue | `07_despliegue.md` | ⏳ Pendiente |
| 8 | Mantenimiento | `08_mantenimiento.md` | ⏳ Pendiente |
```

Después de la fase: fila 5 → `✅ Listo` (guías 1-18), filas 6-8 → `✅ Listo` con link al archivo (como las filas 1-4 ya lo tienen, líneas 15-18). La fila 4 dice "18 ADRs" — actualizar a "20 ADRs" (línea 18). Los emojis de estado (`✅ Listo` / `🚧 Parcial` / `⏳ Pendiente`) son el vocabulario fijo de la tabla. La "Regla del proyecto" (líneas 24-26) no cambia.

---

### `README.md` raíz (EDIT — tabla del ciclo completa + stack telegráfico)

**Analog:** el propio archivo — líneas 36-50 (tabla) y 68-76 (stack).

**Tabla del ciclo** (README.md:42-45 — mismas cuatro filas a cerrar, con links estilo `[\`docs/...\`](docs/...)`; la fila 4 "Arquitectura + 18 ADRs" (línea 41) pasa a "20 ADRs"):

```markdown
| 5 | Desarrollo (guías 1–15 paso a paso) | [`05_desarrollo/`](docs/05_desarrollo) | 🚧 Parcial (guías 1-15 listas; continúa en fases 5+) |
| 6 | Pruebas | `06_pruebas.md` | ⏳ Pendiente |
| 7 | Despliegue | `07_despliegue.md` | ⏳ Pendiente |
| 8 | Mantenimiento | `08_mantenimiento.md` | ⏳ Pendiente |
```

**Otros puntos a sincronizar:** línea 27 ya promete "despliegue gratuito" (se mantiene); línea 42 "guías 1–15" → "1–18"; §"Qué hace especial" línea 54 "las 18 decisiones" → "las 20 decisiones"; el stack telegráfico (líneas 70-76) gana su línea de despliegue (Vercel + Render free tier, SQLite efímero + seed) en el mismo estilo de frase con "·" separador.

---

### `docs/05_desarrollo/README.md` (EDIT — guías 16+, mapa mental completo)

**Analog:** el propio archivo — cómo la fase 4 cerró su corrida.

**Tabla de índice** (docs/05_desarrollo/README.md:24-40 — agregar filas 16-18 al mismo molde `| # | Guía | Construye | Estado |`; las filas existentes terminan todas en `✅ Listo`):

```markdown
| 15 | `guia-15-asistente-cierre.md` | La burbuja de la asesora en la tienda y la Gran verificación final de la fase 4 | ✅ Listo |
```

**Nota de cierre de fase** (líneas 42-46 — el bloque que cada fase reescribe; la fase 5 lo reemplaza por el cierre de la SERIE):

```markdown
> La fase 4 del proyecto completa sus cuatro guías (12-15: panel de
> administración y asistente IA). La guía siguiente llega con la fase 5
> (despliegue) — cada una asumiendo que estas están construidas y
> verificadas en tu máquina, igual que el índice de `docs/README.md`
> avanza por fase.
```

**Mapa mental** (líneas 48-72 — el párrafo "de adentro hacia afuera" que crece por fase; la fase 5 agrega la capa de despliegue: URLs públicas, return_url congelado, disco efímero + seed como estrategia, cierre del ciclo).

---

### `.planning/REQUIREMENTS.md` / `ROADMAP.md` / `PROJECT.md` (EDIT — cierre de índices)

Convención mecánica (estado actual verificado):
- `REQUIREMENTS.md`: checkboxes `- [ ] **GUIDE-01**` (línea 12), `**DEPL-01**` (63), `**DEPL-02**` (64) → `- [x]`; Traceability (líneas 108/135/136) `Pending` → `Complete`.
- `ROADMAP.md` §Progress: línea 31 `- [ ] **Phase 5: ...**` → `- [x] ... (completed <fecha>)` — copia el formato exacto de la línea 30 (Phase 4).
- `PROJECT.md` §Key Decisions (línea 74): agregar la entrada de deploy (D-69/D-70) en el formato de las existentes.

Estas tres ediciones suelen quedar en manos del cierre del workflow `execute-phase`; si el planner las incluye en un plan, son acciones mecánicas contra las líneas citadas.

## Shared Patterns

### 1. Estructura canónica de guía (🧠/✅/📝)
**Source:** `docs/05_desarrollo/guia-15-asistente-cierre.md` (secciones y líneas en la tabla de guia-16 arriba)
**Apply to:** guia-16, guia-17, guia-18. La cadena de secciones es fija en las 15 guías existentes: cabecera blockquote → términos → pasos numerados con 🧠 + código + ✅ mini-verificación → (guía de cierre) Gran verificación final → ❌ errores → ✅ verificación de la guía → 📝 punto de control → aprendizajes → **Siguiente**.

### 2. Tabla "Gran verificación final" (`| # | Verificación | Origen |`)
**Source:** guia-15:509-530; verificación con columna Origen también en demo-cine 07:129-138
**Apply to:** guia-18 (y solo si el planner parte la verificación, en 16/17 como mini-verificaciones). Cada fila cita su origen (RF/RN/D-xx/ADR-xx). Filas FIJAS heredadas: contrato ↔ `/docs` (contra 0.4.0 en URL pública) y grep del build (AIAS-03, comando por shell Git Bash/PowerShell — guia-15:530).

### 3. Disciplina de evidencia documental (D-73/D-68: fuente oficial + URL + "a la fecha")
**Source:** `docs/04_arquitectura/adr/018-*.md` §Evidencia firmada (líneas 144-185)
**Apply to:** ADR-019, ADR-020, doc 07, guías 16-18. Toda cifra de free tier (spin-down 15 min, wake ~1 min, 750 h/mes, límites Hobby) y todo comando de plataforma se cita con URL de la doc oficial y "a la fecha" — jamás cifras desnudas. Las fuentes ya están recolectadas con URL en `05-RESEARCH.md` §Sources.

### 4. Corrida de tablas de estado (quinta corrida D-13/D-18)
**Source:** `docs/README.md:13-22`, `README.md:36-50`, `docs/05_desarrollo/README.md:24-46`
**Apply to:** los tres READMEs. Vocabulario fijo de estados (`✅ Listo` / `🚧 Parcial` / `⏳ Pendiente`), links relativos al estilo de las filas 1-4, conteos sincronizados ("18 ADRs"→"20", "guías 1-15"→"1-18").

### 5. Anclas de integración ya construidas (la fase COBRA promesas, no construye)
**Source:** `guia-09:597-603` (`backend_url` + comentario que nombra "la fase 5"), `guia-09:685` (`return_url`), `guia-09:1042-1054` (`_hacia_spa` 302 con `cors_origins[0]`), `guia-02:416-418` (`VITE_API_URL` "fase de despliegue"), `guia-01:331-333` (`fastapi run` "llegará en la fase de despliegue")
**Apply to:** guías 16-18 y doc 07. Los nombres de env vars ya están fijados por el código (`BACKEND_URL`, `CORS_ORIGINS`, `VITE_API_URL`) — las guías los enseñan como overriding de entorno, jamás hardcodean URLs (anti-pattern del research).

### 6. Enlazado "Siguiente" en cadena
**Source:** guia-15:705-709 (apunta a fase 5); demo-cine 06:327 → 07 → 08 (los docs del ciclo también se encadenan)
**Apply to:** guia-16 → guia-17 → guia-18 → docs 06/07/08. La cadena continua es un criterio de la verificación documental de la fase (specifics de CONTEXT).

### 7. Honestidad como decisión pedagógica
**Source:** ADR-012 §"Negativas (honestas)" (76-85), demo-cine ADR-007 §"Negativas (mostrarlas, no esconderlas)" (35-39), guia-15 nota honesta de la fila 8 (538-542)
**Apply to:** ADR-019/020 y guías: el spin-down/cold start se nombra (Pitfall 6), el disco efímero se explica en dos capas build-time/runtime (Pitfall 5), `/docs` público como trade-off declarado.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `docs/06_pruebas.md` (contenido) | doc de fase | síntesis | El análogo (demo-cine 06) construye una suite pytest — en demo-carro NO hay suite: el doc sintetiza el método ya vivido (D-71). El FORMATO se copia (demo-cine 06); el CONTENIDO no tiene análogo y sale de `05-RESEARCH.md` Pattern 5 + `05-CONTEXT.md` specifics (mini-verificación / Gran verificación / UAT runtime como método). |
| Gran verificación final "definida, no ejecutada" | verificación | request-response | Sin precedente en la serie: las fases 1-4 siempre la CORRIERON (UAT delegado). D-73 cambia el contrato: la tabla se escribe PARA el alumno. Molde de tabla = guia-15; la nota que declara "esta verificación la corres TÚ en tus cuentas" es nueva (tono: la nota honesta de guia-15:538-542 es el pariente más cercano). |
| Cierre de la SERIE (guía 18 / doc 08 finales) | cierre narrativo | síntesis | Ninguna guía de demo-carro cierra serie (guia-15 cierra fase). Parcial: demo-cine 08:130-135 "El ciclo se cierra (y se reabre)". |

## Metadata

**Analog search scope:** `docs/` completo de demo-carro (05_desarrollo/, 04_arquitectura/adr/, READMEs) + `D:/Repos/demo-cine/docs/` (06/07/08 + adr/007) + `.planning/` (REQUIREMENTS/ROADMAP/PROJECT, solo convención de cierre)
**Files scanned:** 11 análogos leídos (6 demo-carro, 5 demo-cine) + 3 índices `.planning` (grep)
**Tracked-source check:** `git ls-files` ejecutado en ambos repos — todos los análogos listados son tracked en su repo de origen
**Pattern extraction date:** 2026-10-01
