# Phase 4: Panel de administración y asistente IA - Pattern Map (REWORK Gemini→Groq)

**Mapped:** 2026-10-01
**Files analyzed:** 15 (12 del producto + 2 de `.planning` discrecionales + 1 UAT de fase)
**Analogs found:** 13 / 13 del producto (todos; el corpus ES la biblioteca de patrones)

> **Nota de dominio (D-17 / ADR-008):** este repo es **guide-only** — no hay código de
> aplicación. Los "archivos a crear/modificar" son DOCUMENTOS, y los análogos son los
> documentos existentes del propio corpus. La clasificación por rol usa tipos de documento
> (guide / adr / spec / requirements / design / index) y la columna "Data Flow" describe el
> **patrón editorial** que el cambio sigue (no flujo de datos de runtime). Todo "código" en
> esta fase son bloques DENTRO de las guías que el alumno copia: su fuente primaria de
> contenido es `04-RESEARCH.md` (probe-verified 2026-10-01) y su fuente de FORMA son los
> análogos citados acá.
>
> **Gate tracked-source verificado:** los 40 archivos de `docs/` + `README.md` raíz están
> git-tracked (`git ls-files` non-empty para cada análogo citado).

## File Classification

| New/Modified File | Role | Data Flow (patrón editorial) | Closest Analog | Match Quality |
|---|---|---|---|---|
| `docs/05_desarrollo/guia-14-asistente-backend.md` | guide | reescritura honesta (mitad de integración) + blockquote de apertura | el MISMO archivo (estructura canónica) + `guia-12-panel-backend.md` paso 1 (narración de retiro) + `guia-09-ordenes-webpay.md` paso 5 (wrapper IN-06) | exact |
| `docs/05_desarrollo/guia-15-asistente-cierre.md` | guide | update de filas de la tabla de Gran verificación final | el MISMO archivo (filas 8/10/13 + nota honesta) | exact |
| `docs/04_arquitectura/adr/018-*.md` (nombre a discreción, ej. `018-asistente-ia-groq-structured-outputs.md`) | adr | NUEVO — supersede ADR-017 | `adr/017-asistente-ia-mini-rag-key-solo-backend.md` (lógica a re-narrar) + `adr/012-retorno-de-webpay.md` (formato con evidencia firmada) | exact (formato) |
| `docs/04_arquitectura/adr/017-asistente-ia-mini-rag-key-solo-backend.md` | adr | marca de superseded — cuerpo BYTE-INTACTO | principio in-repo: guia-12 paso 1 ("las guías 5 y 6 NO se re-editan — jamás") | parcial (no hay ADR superseded previo en el corpus) |
| `docs/04_arquitectura/contrato_api.yaml` | spec (OpenAPI) | agnostic-wording sweep — 8 descripciones, versión NO sube (D-66) | el MISMO archivo (ya usa "Servicio externo del asistente" en la fila 503) | exact |
| `docs/02_requerimientos.md` | requirements | rewrite in-place de filas RNF-08/RNF-09 (sin renumerar) | el MISMO archivo (RNF-08/09 actuales, líneas 146-147) | exact |
| `docs/03_diseno.md` | design | rename de entidad externa + update DFD 15.0 (sin renumerar series) | el MISMO archivo (DFDs 12.0-14.0 como molde de DFD versionado) | exact |
| `docs/04_arquitectura/README.md` | index (arquitectura) | fila de dependencias + fila nueva en índice de ADRs | el MISMO archivo (fila "SDK Webpay" l.121 como molde de fila de SDK) | exact |
| `docs/05_desarrollo/README.md` | index (guías) | fila 14 del índice + párrafo "mapa mental" | el MISMO archivo (filas 12/13 ya escritas como molde) | exact |
| `README.md` (raíz) | index (proyecto) | prosa de descripción/stack (2 pasajes) | el MISMO archivo (l.9-11 y l.74-76) | exact |
| `docs/05_desarrollo/guia-12-panel-backend.md` | guide | one-liner (l.16: "el SDK de Gemini llega con la guía 14") | el MISMO archivo | exact |
| `docs/05_desarrollo/guia-13-panel-spa.md` | guide | one-liner (l.1673: "con `google-genai`" en el "Siguiente") | el MISMO archivo | exact |
| `.planning/PROJECT.md` | planning-doc (discrecional) | constraints / Key Decisions de IA (10 menciones: l.9, 33, 38, 52-55, 59, 68-69, 80) | el MISMO archivo | exact |
| `.planning/research/STACK.md` | research-doc (discrecional) | nota groq en stack vivo (14 menciones: l.3, 30, 33, 75, 83, 102, 109, 118, 134-135, 143, 151, 155, 159) | el MISMO archivo | exact |
| `.planning/phases/04-.../04-UAT.md` | uat-log (fase) | re-verificación test 2 (registro expected/result/verified_by/evidence) | el MISMO archivo (tests 1-2 ya registrados) | exact |

**Fuera de alcance (D-51/D-50/STAKE-04/D-57 diferidos):** upload de imágenes, refund PAID, gráficos de métricas, streaming del chat — ninguna entrada de este mapa los toca.

## Pattern Assignments

### `docs/05_desarrollo/guia-14-asistente-backend.md` (guide, reescritura de la mitad de integración)

**Analog primario: el MISMO archivo** — se mantiene la estructura canónica completa; solo cambia el CONTENIDO de los pasos que hablan del proveedor. **Analog secundario de narrativa:** `guia-12-panel-backend.md` paso 1. **Analog estructural del service:** `guia-09-ordenes-webpay.md` paso 5.

**Qué se mantiene (formas que NO cambian):** header blockquote "Qué construirás hoy / Al terminar tendrás / Necesitas" (l.3-16); tabla "Los términos de hoy" (l.20-31); la secuencia de pasos con 🧠/código/✅; la sección "❌ El error que este archivo evita" (l.690-793); "✅ Verificación de la guía" (l.797-814); "📝 Punto de control" (l.816-833); "Lo que acabas de aprender" (l.835-864); "**Siguiente:**" (l.866-869). Pasos que quedan casi intactos: **Paso 4 schemas** (solo `Recomendacion` gana `model_config = ConfigDict(extra="forbid")` — RESEARCH Pattern 1), **Paso 6 router** (responses 422/429/503 y copys locked NO cambian — D-66/Pitfall 5), **Paso 7 include_router** (l.593-632).

**Patrón de blockquote honesto de apertura (D-65) — copiar de guia-12 paso 1 (l.37-54):**

```markdown
## Paso 1 — La retirada del demo: `/api/admin/estado` se va con honors

🧠 **El desarrollador piensa:** *esta guía empieza con un funeral chico. [...]
Cumplió su lección a cabalidad [...] ¿Y las guías 5 y 6 que lo construyeron?
NO se re-editan — jamás: la historia del contrato es la historia de la tienda [...]
La evolución se narra AQUÍ [...] — el mismo criterio de las fases anteriores:
nada cambia en silencio.*
```

El blockquote de apertura de guia-14 rework (≈5 líneas, antes de "Los términos de hoy") replica exactamente este molde: narra el swap (Gemini→Groq: 402 real + billing obligatorio de Google), declara que el registro completo vive en ADR-018, y sigue "como si Groq siempre hubiera sido".

**Patrón de constante con nombre (D-64 `MODELO_ASISTENTE`) — copiar de guia-12 (l.277-285):**

```python
# Umbral de stock bajo del PANEL (RN-14, D-53): productos ACTIVOS con esta
# cantidad o menos. [...] Dos conceptos, dos constantes, dos textos [...]
STOCK_BAJO_UMBRAL = 5
```

`MODELO_ASISTENTE = "openai/gpt-oss-120b"` va con el mismo ceremonial: comentario que cita el respaldo (D-64), nombre propio, valor fijo del backend. El `.env` del alumno queda mínimo: solo `GROQ_API_KEY`.

**Patrón de wrapper de servicio externo (IN-06) — la FORMA se copia del propio guia-14 paso 5 (l.361-369) que a su vez espeja guia-09 paso 5 (l.497-547):**

```python
# guia-09 l.530-546 (el molde original — traducción de errores del SDK):
def commit(token_ws: str) -> dict | None:
    """[...] la excepción tipada del SDK (TransbankError [...]) y los errores
    de red de requests se traducen a señal de dominio AQUÍ — ninguna excepción
    de transbank ni de su transporte cruza la frontera de este archivo.
    """
    try:
        return tx.commit(token_ws)
    except (TransbankError, requests.ConnectionError, requests.Timeout):
        return None
```

```python
# guia-14 l.361-369, 433-434, 458-469 (las señales de dominio y el client lazy — SE MANTIENEN):
class CuotaAgotada(Exception): ...
class AsistenteNoDisponible(Exception): ...
_client: genai.Client | None = None   # → Groq | None (lazy, D-61)
```

**Lo que CAMBIA (contenido probe-verified, fuente: 04-RESEARCH.md Patterns 1-3 + Ejemplos A/B — NO copiar de las versiones Gemini):**
- Paso 1: `uv add "groq>=1.7,<2"` + `uv remove google-genai` (el blockquote narra el porqué del remove); mini-verificación de versión piso/techo (el fix D-4-6 ya enseñaba esa forma).
- Paso 2: console.groq.com en vez de aistudio.google.com; `.env.example` con `GROQ_API_KEY=` vacía; verificación por existencia sin imprimir el valor (mantener la forma actual l.116-125).
- Paso 3: `groq_api_key: str | None = None` (el contraste fail-fast con `secret_key` es la lección — mantener intacto el 🧠 actual l.131-145).
- Paso 5: `from groq import Groq, RateLimitError`; `response_format={"type": "json_schema", "json_schema": {"name": "Recomendacion", "strict": True, "schema": Recomendacion.model_json_schema()}}`; `Recomendacion.model_validate_json(completion.choices[0].message.content)`; except `RateLimitError` → `CuotaAgotada`, except `GroqError` → `AsistenteNoDisponible`; construcción del client DENTRO del try (RESEARCH Pattern 2: `Groq()` sin key lanza en construcción). Gotcha IN-03 a re-narrar: el SDK `groq` también auto-pickupea `GROQ_API_KEY` del entorno y NO lee `.env`.
- 🧠 del 429: cifras **30 RPM / 1.000 RPD / 8K TPM / 200K TPD** para `openai/gpt-oss-120b` CON link a console.groq.com/docs/rate-limits y "a la fecha de esta guía" (D-68 + corrección del research — JAMÁS "14.400 RPD").
- "Errores que evita" nº2 (l.710-733, drift de docs): re-escribir con el gotcha strict-mode (`extra="forbid"` — Pitfall 2 del research) como nueva lección; nº4 retry: actualizar a "el SDK groq reintenta 2x (incluye el 429)".

---

### `docs/05_desarrollo/guia-15-asistente-cierre.md` (guide, ajustes puntuales)

**Analog: el MISMO archivo.** El componente BurbujaAsesora, `apiPostPublico`, el montaje en Layout y los copys NO cambian. Solo:

**Fila 8 del happy path (l.524) y su nota honesta (l.538-540) — el patrón de fila que se ajusta:**

```markdown
| 8 | La burbuja abre con la bienvenida LOCAL [...] y la asesora recomienda con
la voz de Maura en UNA respuesta con 1-3 cards clicables [...] | RF-23, RF-24, HU-13, D-57/D-58/D-46, ADR-017 |
```

El ajuste: la nota honesta "(el happy path [...] requiere TU key: en el aula, cada quien con la suya, D-60)" pasa a nombrar console.groq.com/D-63 y citar ADR-018 junto al 017 donde aplique.

**Fila 10 (l.526) y fila 13 (l.529) — sustitución literal de la key en el patrón del grep:**

```markdown
| 13 | **El grep del build** (AIAS-03): `npm run build` y, DESPUÉS [...] busca
`GEMINI_API_KEY` en el `dist/` regenerado — **CERO coincidencias**. Git Bash:
`grep -r "GEMINI_API_KEY" dist/` [...] PowerShell: `findstr /s /i "GEMINI_API_KEY" dist\*`
(o `Select-String -Path dist\* -Pattern "GEMINI_API_KEY"`) [...] | RNF-09, AIAS-03, D-60 |
```

Cambiar `GEMINI_API_KEY` → `GROQ_API_KEY` en fila 10, fila 13, paso 4 (l.492-499), punto de control 5 (l.670-673) y aprendizajes (l.699-701), manteniendo el control positivo y la variante Select-String (Pitfall 8 del research: findstr desde Git Bash corrompe switches MSYS).

---

### `docs/04_arquitectura/adr/018-*.md` (adr, NUEVO — supersede ADR-017)

**Analog de contenido: ADR-017 completo (130 líneas). Analog de formato con evidencia: ADR-012.**

**Frontmatter y secciones — copiar el molde de ADR-017 (l.1-5):**

```markdown
# ADR-017 — Asistente de venta con mini-RAG honesto, structured output y la API key solo en el backend

- **Estado:** Aceptada
- **Fecha:** 2026-09-30
- **Resuelve:** cómo recomienda la asesora de aromas sin alucinar productos, y dónde
  vive la API key de Gemini (AIAS-01..03; decisiones D-56/D-59/D-60/D-61)
```

ADR-018 replica: `- **Estado:** Aceptada` + `- **Fecha:** 2026-10-01` + `- **Resuelve:**` (nombrando que reemplaza el proveedor de ADR-017, decisiones D-63..D-68) — y sus secciones `## Contexto` / `## Opciones consideradas` (tabla A/B/C) / `## Decisión` (numerada 1..n) / `## Consecuencias` (Positivas + **Negativas (honestas)**) / `## Para conversar en clase` / `## Evidencia firmada` / `Relacionada:` (l.125-130). La tabla de opciones de ADR-017 (l.23-29, mini-RAG vs embeddings vs respuesta libre) es el molde; las opciones de ADR-018 son proveedor/SDK (Groq vs quedarse en Gemini roto vs REST directo — ver RESEARCH "Alternatives Considered").

**Patrón de "Evidencia firmada" — copiar de ADR-017 (l.105-123) y ADR-012 (l.16-18, spike como evidencia):**

```markdown
## Evidencia firmada

Los patrones citados en las reglas 1 y 5 están firmados con evidencia
contra el README del SDK en el tag exacto `v2.25.0`, verbatim en los
Patterns 1-3 de [`04-RESEARCH.md`](../../../.planning/phases/04-panel-.../04-RESEARCH.md): [...]
```

ADR-018 firma igual contra: docs oficiales de Groq (rate-limits/structured-outputs/deprecations, URLs en RESEARCH §Sources) + probe punta a punta SDK 1.7.0 del 2026-10-01 + la evidencia del 402/billing de Google (04-UAT.md test 2). El gotcha IN-03 (auto-pickup de `GROQ_API_KEY`) se registra acá (re-narrando la regla 5 de ADR-017, l.58-62).

**Contenido que se PRESERVA de ADR-017 (la muralla no cambia — D-56 intacto):** mini-RAG con catálogo activo en el prompt, validación de ids server-side, endpoint público `security: []`, degradación D-61, wrapper jamás-500. Solo cambian: proveedor/SDK, mecanismo de JSON (`response_format` json_schema strict vs `response_json_schema`), key en console.groq.com, y cifras públicas de límites (D-68).

---

### `docs/04_arquitectura/adr/017-*.md` (adr, marca de superseded)

**Analog del principio: guia-12 paso 1 (l.47-51)** — "¿Y las guías 5 y 6 que lo construyeron? NO se re-editan — jamás [...] la evolución se narra AQUÍ". ADR-017 recibe SOLO el cambio de estado en el frontmatter (l.3):

```markdown
- **Estado:** Aceptada
```

→ `- **Estado:** Superseded por [ADR-018](018-....md) (2026-10-01)` — cuerpo byte-intacto (Pitfall 7 del research). CERO ediciones al resto del archivo.

---

### `docs/04_arquitectura/contrato_api.yaml` (spec, 8 descripciones agnósticas — versión queda 0.4.0)

**Analog: el MISMO archivo.** El yaml YA usa registro mayormente agnóstico; el wording objetivo ya existe en la propia fila 503 (l.54): `"Servicio externo del asistente no disponible (sin API key o Gemini caído — degradación D-61)"` → basta eliminar "o Gemini caído" / "Gemini" de cada fila. Las 8 menciones exactas:

| Línea | Contexto | Dirección D-66 |
|---|---|---|
| l.53 | Convención de errores, fila 429: "Cuota del free tier de Gemini consumida — [...] sin cifras de límites" | "Cuota del free tier del servicio de IA consumida [...] " — y el paréntesis "no son públicos sin login" MUERE (D-68: son públicos) |
| l.54 | Convención de errores, fila 503: "[...] (sin API key o Gemini caído — degradación D-61)" | "sin API key o servicio caído" |
| l.74 | Tag Asistente description: "recomienda aromas del catálogo real vía Gemini" | "vía el servicio de IA" |
| l.546 | ChatMensaje.historial description: "el free tier de Gemini y validan aquí" | "el free tier del servicio de IA" |
| l.1436-1437 | description de `POST /api/asistente`: "Gemini responde JSON estructurado [...] Sin `GEMINI_API_KEY` en el .env" | "el servicio de IA responde JSON estructurado [...] Sin la API key del asistente en el .env" + eliminar "(no hay fuente pública sin login)" (l.1440-1441) |
| l.1464 | response 429: "Cuota del free tier de Gemini consumida — [...] (no son públicos sin login)" | agnóstico, sin el paréntesis |
| l.1472 | response 503: "(sin API key en el .env del backend o Gemini caído)" | "(sin API key del asistente en el .env o servicio caído)" |

La versión NO sube (0.4.0 nunca salió por separado) y cero churn en guia-12/fila contrato↔`/docs` (D-66). El molde de cómo se escribe una description del asistente ya está en l.1430-1442 — mantener la estructura del bloque `description: |` con bullets de decisiones.

---

### `docs/02_requerimientos.md` (requirements, RNF-08/09 in-place)

**Analog: el MISMO archivo.** Filas actuales (l.146-147):

```markdown
| RNF-08 | Dependencia externa | La asesora de venta depende del servicio externo Google Gemini
operado en su **tier gratuito**: cada alumno crea su propia API key gratis, sin tarjeta
de crédito; [...] degrada a un mensaje amable (503/429), sin cifras de límites que no
tienen fuente pública | P8 |
| RNF-09 | Seguridad | La API key de Gemini vive **solo en el backend**, como variable de
entorno del servidor [...] | AIAS-03, D-60/D-61 |
```

Rewrite manteniendo código/categoría/columnas: RNF-08 queda agnóstica y SIN números pero con "los límites exactos son los documentados públicamente por proveedor" (D-68); "Google Gemini" → "el servicio de IA" (quien nombra cifras y proveedor es la guía y ADR-018, no la RN). RNF-09: "La API key del asistente vive...". **Patrón de serie sin renumerar (análogo in-repo):** RN-04 (l.156, "el catálogo de esta etapa es de solo lectura [...] llegan con el panel de la etapa 4") quedó byte-intacta cuando RN-15 (l.167) la referencia y la cumple — la regla del corpus es que las series continúan sin tocar lo anterior; aquí la EXCEPCIÓN documentada es que RNF-08/09 describen el sistema VIGENTE y se reescriben (D-67), igual que ADR-002 cambia 2 líneas por la misma razón.

---

### `docs/03_diseno.md` (design, entidad GEM + DFD 15.0)

**Analog: el MISMO archivo; molde de DFD versionado: DFDs 12.0-14.0 (l.555-613).** Los 4 puntos de toque:

1. **Decisión 18** (l.244-249): "sin `GEMINI_API_KEY` el endpoint del asistente responde 503" → "sin la API key del asistente" (la decisión es del QUÉ; agnóstica como el contrato).
2. **Diagrama de contexto** (l.297-329): el párrafo "la etapa 4 suma a **Gemini**, el segundo servicio externo — y de un tipo nuevo [...]" y el nodo `GEM["Gemini (asesora IA)"]` (l.314) con sus dos flechas (l.327-328). Rename a discreción del planner: `GEM["Servicio de IA (asesora)"]` o nombra Groq como entidad externa concreta (el análogo Webpay en el MISMO diagrama nombra la pasarela real — l.313 `WP["Webpay (pasarela de pago)"]`); ambas calzan con D-67 mientras "asesora Gemini" no quede.
3. **DFD 15.0** (l.614-636): el nodo `GEM["Gemini (asesora IA)"]` (l.621) y las "Reglas del proceso" (l.628-636: "429 sin cifras de límites (RNF-08)" → ajustar a la nueva RNF-08). El molde mermaid de los DFDs previos (ej. 13.0, l.576-584: entidades `[("D# ...")]`, proceso `(["N.0 ..."])`, aristas con etiquetas `<br/>`) se mantiene exacto.
4. **Trazabilidad §** (l.1393-1401): "RNF-08 (dependencia del servicio Gemini free tier)", "RNF-09 [...] solo el backend habla con Gemini", "RN-16 [...] topes antes de Gemini" — actualizar el texto entre paréntesis sin tocar los números de fila.

---

### `docs/04_arquitectura/README.md` (index arquitectura)

**Analog: el MISMO archivo.** Cuatro toques con sus moldes:

1. **Contexto** (l.18-19): "(Webpay en la fase 3, Gemini en la fase 4)" → proveedor nuevo o "el servicio de IA".
2. **Fila de dependencias** (l.122) — molde: la fila Webpay (l.121) con "versión + pin + para qué + link a ADR":

```markdown
| IA (fase 4) | **google-genai 2.25.0** (pin `>=2.25,<3`) | SDK oficial de Gemini para la
asesora de venta: JSON estructurado + validación de ids contra la BD (mini-RAG, D-56); la
API key vive solo en el `.env` del backend y sin key el asistente degrada a 503 amable
([ADR-017](adr/017-asistente-ia-mini-rag-key-solo-backend.md)) |
```

→ fila IA pasa a `groq 1.7.0 (pin >=1.7,<2)` citando ADR-018 (y ADR-017 como superseded).
3. **Regla 3 de capas** (l.196-199): "traduce los errores del SDK de Gemini a señales de dominio" → "del SDK de IA" (la técnica nombrada — `services/webpay.py` — no cambia).
4. **Índice de ADRs** (l.217-235): fila 017 se mantiene (su "Resuelto por" puede anotar superseded) y se AGREGA la fila 018 siguiendo el formato `| [018](adr/018-....md) | Título | Resuelto por (AIAS-01..03, D-63..D-68) |`.

---

### `docs/05_desarrollo/README.md` (index guías)

**Analog: el MISMO archivo.** Fila 14 del índice (l.39): "El backend de la asesora de aromas: Gemini con respuesta JSON validada contra el catálogo" → proveedor nuevo/agnóstico. Párrafo mapa mental (l.64-69): "Gemini es el **segundo servicio externo** del proyecto — y de un tipo nuevo: Webpay era una redirección [...] la asesora es un request-response JSON **desde el backend**" — mantener la lección de contraste, cambiar el nombre.

### `README.md` raíz (index proyecto)

**Analog: el MISMO archivo.** l.9-11: "un asistente de venta con IA (Google Gemini)" → "(Groq)". l.74-76 (stack en prosa): "Google Gemini: la asesora de aromas recomienda del catálogo real, con la API key solo en el backend" → mismo formato con Groq. Ambos son prosa de una línea; sin tabla.

### `guia-12-panel-backend.md` / `guia-13-panel-spa.md` (one-liners)

- guia-12 l.16 (header "Necesitas"): "el único paquete nuevo de la fase (el SDK de Gemini) llega con la guía 14" → "(el SDK de Groq)". Es la ÚNICA mención; nada más se toca (D-66: cero churn en guia-12).
- guia-13 l.1672-1675 ("**Siguiente:**"): "el primer endpoint de IA del proyecto con `google-genai`, el mini-RAG honesto [...]" → "con el SDK `groq`". Única mención.

### `.planning/PROJECT.md` y `.planning/research/STACK.md` (discrecionales — rework o cierre de fase)

CONTEXT "Claude's Discretion (rework Groq)" permite ambos; la condición es que NO queden diciendo Gemini al partir la fase 5. Líneas exactas (verif. 2026-10-01): PROJECT.md l.9, 33, 38, 52-55, 59, 68-69, 80; STACK.md l.3, 30, 33, 75, 83, 102, 109, 118, 134-135, 143, 151, 155, 159. Si van en el rework: el molde de PROJECT.md es su propia sección "Constraints" (bullets con backticks) y el de STACK.md su tabla Core (fila `google-genai` l.33 → fila `groq` con misma estructura Version/Purpose/Why/Confidence/Provenance).

### `04-UAT.md` (re-verificación test 2)

**Analog: el MISMO archivo.** Formato de registro por test (copiar de los ya existentes):

```markdown
### N. Título
expected: ...
result: pass|fail
verified_by: agent (user-delegated)
evidence: |
  ...notas de corrida en D:/Repos/maura-uat...
```

El test 2 se re-verifica tras el rework con la receta del probe del research (SDK `groq` 1.7.0 en el taller, `GROQ_API_KEY` ya presente en el `.env`, truststore como nota de entorno del taller — Pitfall 9).

## Shared Patterns

### 1. Estructura canónica de guía (🧠/✅/📝)
**Source:** `docs/05_desarrollo/guia-14-asistente-backend.md` (estructura completa) — header blockquote Qué/Al terminar/Necesitas → tabla de términos → pasos numerados con 🧠 "El desarrollador piensa" + bloque de código + ✅ mini-verificación → "❌ El error que este archivo evita" → "✅ Verificación de la guía" numerada → "📝 Punto de control" → "Lo que acabas de aprender" (bullets con D-references) → "**Siguiente:**".
**Apply to:** reescritura de guia-14 (toda su forma), ajustes de guia-15.

### 2. Nada cambia en silencio (narración honesta)
**Source:** `guia-12-panel-backend.md` l.37-54 (retirada del demo narrada in situ; guías previas jamás re-editadas) + `docs/02` RN-04↔RN-15.
**Apply to:** blockquote de apertura de guia-14 (D-65), ADR-018, marca en ADR-017, nota de la fila 8 en guia-15.

### 3. Wrapper de servicio externo IN-06 (un solo archivo importa el SDK)
**Source:** `guia-09-ordenes-webpay.md` l.460-557 (`services/webpay.py`: excepciones tipadas → señal de dominio, `grep -r <sdk> backend/app` lista SOLO el wrapper) ↔ `guia-14` l.282-486.
**Apply to:** guia-14 paso 5 reescrito: `from groq import Groq, RateLimitError` vive SOLO en `services/asistente.py`; `RateLimitError`→CuotaAgotada, `GroqError`→AsistenteNoDisponible; sin retry casero (el SDK reintenta 2x, incl. 429).

### 4. Formato ADR demo-cine
**Source:** `adr/017` (l.1-5, 23-29, 31-67, 69-90, 92-103, 105-130) y `adr/012` (l.1-5, 16-18).
**Apply to:** ADR-018 completo; sección "Evidencia firmada" obligatoria (disciplina D-56: firmar contra doc oficial + probe, jamás supuestos).

### 5. Fila de tabla de dependencias / índice con link a ADR
**Source:** `docs/04_arquitectura/README.md` l.115-122 (filas pyjwt/transbank/google-genai) e índice l.217-235.
**Apply to:** fila IA → groq 1.7.0 pin `>=1.7,<2`; fila nueva de ADR-018 en el índice.

### 6. Convención de errores del contrato + responses declaradas
**Source:** `contrato_api.yaml` l.42-54 (tabla de códigos) y l.1450-1478 (422/429/503 con example `detail` locked).
**Apply to:** wording agnóstico D-66 — los copys `detail` ("La asesora está recibiendo muchas consultas..." / "La asesora no está disponible...") NO cambian; solo las descriptions que nombran Gemini.

### 7. Firmar cifras con fuente + "a la fecha" (D-68)
**Source:** patrón nuevo establecido por el research (04-RESEARCH.md Pitfall 1); el contraejemplo in-repo es la promesa actual "sin cifras de límites (no son públicos sin login)" que muere.
**Apply to:** 🧠 del 429 en guia-14: 30 RPM / 1.000 RPD / 8K TPM / 200K TPD + URL + "a la fecha de esta guía"; RNF-08 sin números.

## No Analog Found

| File | Role | Razón |
|---|---|---|
| Marca de "Superseded" en frontmatter de ADR | adr | Ningún ADR del corpus está superseded aún (001-017 todos "Aceptada"). El PRINCIPIO byte-intacto sí tiene análogo (guia-12 paso 1 l.47-51: no re-editar historia) y el formato textual de la marca existe en `.planning` (CONTEXT D-60: "**[ROTO 2026-10-01...] SUPERSEDED por D-63...**", cuerpo intacto). El planner define la redacción exacta de la línea de Estado. |
| Contenido técnico Groq (bloques de código) | guide-code | No existe código groq en el corpus — fuente primaria: `04-RESEARCH.md` Patterns 1-3 + Ejemplos A/B (probe-verified 2026-10-01, SDK 1.7.0). La FORMA sí tiene análogo (assignments de guia-14 arriba). |

## Metadata

**Analog search scope:** `docs/` completo (41 archivos), `README.md` raíz, `.planning/PROJECT.md`, `.planning/research/STACK.md`, `.planning/phases/04-*/04-UAT.md`; conteo de menciones Gemini/google-genai con grep case-insensitive sobre todo el repo (96 menciones en 12 archivos del producto + 24 en 2 archivos de `.planning`).
**Tracked-source gate:** los 40 archivos de docs + README raíz verificados con `git ls-files` (todos tracked; cero rutas mirror).
**Files scanned:** 15 archivos leídos o grepped con lectura dirigida; lecturas completas: guia-14 (869), guia-15 (707), ADR-017 (130), ADR-012 (97), ADR-002 (57), docs/02 (456), docs/05 README (71), README raíz (94); lecturas dirigidas: guia-12 (2 rangos), guia-09 (1 rango), contrato (2 rangos), docs/03 (3 rangos), docs/04 README (3 rangos), guia-13 (1 rango).
**Early stop:** aplicado — 5 análogos fuertes (guia-14 sí-misma, guia-12, guia-09, ADR-017/012, contrato) cubren todos los archivos del rework; no se exploró demo-cine (referencia externa de formato, no necesaria: el corpus propio cubre todo).
**Pattern extraction date:** 2026-10-01
