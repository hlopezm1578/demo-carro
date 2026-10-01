# ADR-017 — Asistente de venta con mini-RAG honesto, structured output y la API key solo en el backend

- **Estado:** Superseded por [ADR-018](018-asistente-ia-groq-structured-outputs.md) (2026-10-01)
- **Fecha:** 2026-09-30
- **Resuelve:** cómo recomienda la asesora de aromas sin alucinar productos, y dónde vive la API key de Gemini (AIAS-01, AIAS-02, AIAS-03; decisiones D-56/D-59/D-60/D-61)

## Contexto

P8 pide una asesora que recomiende aromas del catálogo a cada clienta,
como lo haría Maura en persona. Es la segunda integración con un servicio
externo real (después de Webpay) y de un tipo nuevo: request-response
JSON del backend, sin redirecciones de navegador. Dos riesgos gobiernan
la decisión: (a) todo LLM alucina — con respuesta libre puede citar
productos que no existen o que la dueña ya desactivó, y el chat mostraría
cards rotas; (b) la API key es una credencial — en el bundle del frontend
sería pública. A favor: el catálogo es chico (12 SKU activos, cabe entero
en un prompt) y el SDK oficial es `google-genai` pinneado `>=2.25,<3`.
La forma exacta de forzar JSON en esa versión NO se firmó sobre supuestos:
el research de la fase la validó contra el README del SDK en el tag
exacto del pin — la misma lección del spike de Webpay (D-41), replicada
como evidencia firmada.

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| **A. Mini-RAG honesto: el catálogo ACTIVO completo en el system prompt + respuesta JSON estructurada + validación de ids contra la BD** | Cero infraestructura nueva; el modelo solo puede citar lo que el prompt lista; el schema garantiza la forma de la respuesta; la validación server-side es la muralla final | El catálogo viaja completo en cada request (12 SKU caben; el día que el catálogo creza, esta decisión se revisa); cada mensaje consume cuota del free tier |
| **B. Embeddings + vector store (el RAG "de libro")** | Escala a catálogos grandes con búsqueda semántica | Motor ML propio: Out of Scope del proyecto; para 12 SKU es infraestructura sin lección y con costo |
| **C. Respuesta libre sin validación** (el texto del modelo directo al chat) | La más simple de escribir; el modelo "sabe" de aromas en general | Cualquier LLM alucina: citaría productos inexistentes o inactivos y el chat mostraría cards rotas — exactamente lo que AIAS-02 veta |

## Decisión

**Opción A.** La asesora recomienda SOLO del catálogo real y la key jamás
cruza al cliente (D-56/D-60/D-61):

1. **Mini-RAG honesto (D-56)**: el system prompt de CADA request lleva el
   catálogo ACTIVO completo — id, nombre, familia aromática, notas y
   precio; los 12 SKU caben enteros. Gemini responde JSON estructurado con
   `types.GenerateContentConfig(response_mime_type='application/json',
   response_json_schema=Recomendacion.model_json_schema())` — el schema
   nace del mismo Pydantic que valida la vuelta.
2. **La validación de ids es responsabilidad del SERVIDOR**: cada id que
   devuelve el modelo se valida contra el catálogo activo en la BD antes
   de responder; los alucinados se descartan en silencio. El frontend
   renderiza lo que ya llegó validado (AIAS-02) — la muralla
   anti-alucinación no se delega al navegador.
3. **La key la crea CADA alumno en Google AI Studio (D-60)** — paso del
   alumno, como las fotos de la fase 1 (D-08), gratis y sin tarjeta — y
   vive en el `.env` del backend vía pydantic-settings (`GEMINI_API_KEY`,
   opcional): jamás en código ni en el frontend. Nada de `VITE_`: toda
   variable `VITE_*` termina en el bundle.
4. **Sin key la app arranca normal y el endpoint responde 503 amable
   (D-61)** — degradación deliberada, NO fail-fast, en contraste
   EXPLÍCITO con `secret_key` de la fase 2: la firma de sesiones es
   obligatoria (sin `.env` la app no parte), el asistente es opcional
   (la tienda sigue 100% operativa y la burbuja muestra "no disponible").
   Dos secretos del mismo `.env`, dos estrategias correctas distintas.
5. **El wrapper del SDK traduce los errores, jamás un 500 crudo (patrón
   IN-06)**: `errors.APIError` con `.code` → 429 (cuota del free tier,
   mensaje amable SIN cifras — los límites no son públicos sin login) /
   503 (todo lo demás, incluido el caso sin key). El SDK ya reintenta los
   transitorios por su cuenta; el wrapper traduce, no re-reintenta.
6. **Endpoint público deliberado (D-59)**: `security: []` como el retorno
   de Webpay — la asesora atiende a quien navega la tienda, con o sin
   cuenta. Los topes de entrada (mensaje ≤ 500 caracteres, historial ≤ 10
   mensajes) protegen el free tier y validan en el borde del contrato
   0.4.0.

## Consecuencias

**Positivas**
- El chat solo puede mostrar cards que existen: doble muralla (prompt con
  activos + validación contra BD antes de responder).
- La lección de integración externa se completa: contrato, secreto,
  degradación y traducción de errores — el espejo completo de Webpay,
  esta vez sin redirecciones.
- Cada alumno con su propia key aísla su cuota del curso entero (D-60) y
  el happy path no depende de credenciales compartidas.

**Negativas (honestas)**
- **El catálogo completo viaja en cada request**: con 12 SKU es barato;
  con 500 habría que filtrar o paginar el prompt — esta decisión tiene
  fecha de revisión y este ADR la declara.
- **El texto del modelo no es 100% controlable**: puede prometer descuentos
  o tonos que la tienda no respalda; se renderiza como texto plano (JSX
  escapa por defecto) y la voz se entrena en el prompt, pero no hay
  garantía contractual del contenido.
- **El happy path depende de un servicio externo gratuito**: Gemini free
  tier puede degradar o cambiar términos — la tienda NO depende de él
  para operar (D-61); ese es exactamente el contrato de degradación.

## Para conversar en clase

1. ¿Por qué la validación de ids en el backend y no en el frontend, si el
   frontend igual tiene el catálogo? ¿Qué ganaría un modelo desobediente
   (o un atacante) validando del lado del cliente?
2. `secret_key` revienta el arranque sin `.env`; `GEMINI_API_KEY` no.
   ¿Por qué dos secretos del mismo archivo merecen estrategias opuestas,
   y cómo se llama cada una?
3. Las docs web de Google hoy enseñan `client.interactions.create` con
   `response_format`; el README del pin `>=2.25,<3` documenta
   `models.generate_content` con `response_json_schema`. ¿Cuál sigue el
   proyecto y por qué la diferencia ES la lección?

## Evidencia firmada

Los patrones citados en las reglas 1 y 5 están firmados con evidencia
contra el README del SDK en el tag exacto `v2.25.0`, verbatim en los
Patterns 1-3 de
[`04-RESEARCH.md`](../../../.planning/phases/04-panel-de-administraci-n-y-asistente-ia/04-RESEARCH.md):
`response_json_schema` + `model_json_schema()` (el nombre
`response_schema` NO aparece en ese README — el que sobrevive en blogs es
de otra generación del SDK), `errors.APIError` con `.code`/`.message`, y
la env var `GEMINI_API_KEY` tomada automáticamente por el `genai.Client`
(capacidad del SDK, citada como evidencia firmada; el proyecto NO confía
en ese auto-pickup: pydantic-settings lee el `.env` hacia el objeto
`Settings`, no hacia el entorno del proceso, por lo que la guía 14 pasa
`api_key=settings.gemini_api_key` explícita — ver su gotcha del `.env`).
El research también dejó registrado el drift como lección (Pitfall 1):
las docs actuales de ai.google.dev enseñan la Interactions API
(`client.interactions.create` + `response_format`), ausente del README
del pin — las docs del servicio y la versión pinneada del SDK son dos
cosas distintas, y la guía enseña el patrón del pin narrando por qué.

Relacionada: [ADR-007](007-api-first.md) (el contrato del endpoint
público con sus 422/429/503),
[ADR-009](009-jwt-larga-vida-localstorage.md) (dónde viven los secretos
de sesión y su fail-fast) y
[ADR-012](012-retorno-de-webpay.md) (el patrón de firmar contra
evidencia y el `security: []` deliberado).
