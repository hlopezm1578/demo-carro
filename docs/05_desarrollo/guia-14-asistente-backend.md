# Guía 14 — La asesora (backend): Groq, JSON estructurado y la key que no sale del .env

> **Nota de migración (D-65, ADR-018):** este proyecto nació con **Gemini**
> como proveedor de la asesora — hasta que Google rompió el flujo del aula:
> pasó a exigir cuenta de facturación para crear keys nuevas y la primera
> key del curso devolvió un 402 real con créditos agotados. El proyecto
> migró a **Groq** y el registro completo de esa decisión vive en el
> **ADR-018** (que supersede al ADR-017). Si vienes de la era vieja,
> desinstala el SDK muerto con `uv remove google-genai` — el resto de esta
> guía sigue como si Groq siempre hubiera estado.

> **Qué construirás hoy:** la segunda integración con un servicio externo
> real del proyecto — Groq vía el SDK oficial `groq`: un
> endpoint público que recomienda SOLO del catálogo real, responde JSON
> estructurado y degrada amable cuando no hay key. Un servicio que
> responde JSON, sin redirecciones — el contraste exacto con Webpay.
> **Al terminar tendrás:** `POST /api/asistente` respondiendo 200 con la
> recomendación y sus ids validados uno a uno contra la base, 422 en los
> topes, 429/503 amables — y la tienda arrancando y operando IGUAL sin
> `GROQ_API_KEY` (D-61).
> **Necesitas:** las guías 1 a 13 completas — el backend en capas con el
> panel encendido (0.4.0 en `/docs`), el catálogo sembrado y, a partir del
> paso 2, TU PROPIA API key de console.groq.com. Abre el
> `contrato_api.yaml` 0.4.0 y el ADR-018 en pestañas: el endpoint de hoy
> los implementa.

---

## Los términos de hoy (antes de copiar nada)

| Término | Qué es, en una frase |
|---|---|
| **System prompt** | Las instrucciones que definen a la asesora (persona, voz, reglas) y el CONTEXTO con el que responde — hoy: el catálogo activo completo, en cada request |
| **Structured output** | Forzar que el modelo responda JSON que calza un schema — `response_format` con `json_schema` en el pin del SDK, no prompt-engineering de "responde SOLO JSON" |
| **Modo strict** | *Constrained decoding*: el servicio garantiza que la respuesta calza el schema (jamás JSON inválido) — a cambio exige todos los campos en `required` y `additionalProperties: false` (Pitfall 2, paso 4) |
| **Mini-RAG** | Retrieval trivial y honesto: el catálogo activo completo viaja en el prompt (cabe: 12 SKU) — sin embeddings ni vector store (D-56, ADR-018) |
| **Alucinación** | Cuando un LLM afirma cosas que no existen — como citar productos que la dueña desactivó; se combate con DOS murallas del servidor, no con confianza |
| **Degradación** | La tienda sigue 100% operativa aunque el servicio externo no esté: sin key el endpoint responde 503 amable — lo contrario de fail-fast, y deliberado (D-61) |
| **Rate limit** | El tope de consultas por minuto/día del free tier — públicos en Groq: 30 RPM / 1.000 RPD para `openai/gpt-oss-120b` a la fecha de esta guía, citados con fuente (D-68) |
| **Free tier** | El plan gratuito (Developer) de la API de Groq — sin tarjeta; 1.000 RPD ≈ 16 consultas por minuto sostenidas todo el día: de sobra para el curso |
| **Env var** | Variable de entorno — la forma en que la key vive en el `.env` del backend y JAMÁS en el código ni en el frontend (RNF-09, D-63) |

---

## Paso 1 — La instalación: el SDK oficial, pinneado piso/techo como el corpus manda

🧠 **El desarrollador piensa:** *un solo paquete nuevo en toda la fase — y
la versión no es libre. El SDK oficial es `groq` (la organización `groq`
de GitHub, el que instalan las propias docs del servicio), y el proyecto
lo pinnea con el criterio de siempre del corpus — el mismo de
`transbank-sdk` en la guía 9: **piso `1.7`** porque es la versión exacta
que la fase validó, punta a punta contra la API real, y **techo `<2`**
porque es el próximo major. ¿Por qué el techo en el major? El README del
SDK declara que sigue SemVer "en general" pero sin prometer pureza en los
minors: el major es la única frontera que se compromete a romper, y el
techo del pin es lo que protege tu proyecto de esa ruptura. Y dos notas
antes de la primera línea. Primera, conocimiento transferible: la API de
Groq es **OpenAI-compatible** — el patrón `client.chat.completions.create`
con mensajes de roles (`system`/`user`) que usarás en el paso 5 es el
dialecto al que la industria convergió: lo volverás a encontrar en otros
proveedores. Segunda, una decisión de arquitectura: igual que `transbank`
en la guía 9, el import del SDK vivirá en UN solo archivo
(`services/asistente.py`) — hoy solo lo instalamos; el aislamiento se
cobra en el paso 5 (IN-06).*

Desde `backend/`:

```
uv add "groq>=1.7,<2"
```

✅ **Mini-verificación:** desde `backend/`, ejecuta:

```
uv run python -c "import importlib.metadata as m; print(m.version('groq'))"
```

Debe imprimir una `1.7.x` o superior DENTRO del rango del pin (el piso
lo validó la fase; el techo `<2` es lo que importa) — el SDK oficial.
(Que el pin funcione lo puedes comprobar en `pyproject.toml`: la
dependencia quedó registrada con el rango, no suelta — dentro de un año,
la 2.x no entrará
a tu proyecto sin que tú lo decidas.)

---

## Paso 2 — TU key: el paso del alumno que nada comparte por ti (D-63)

🧠 **El desarrollador piensa:** *Webpay venía con credenciales públicas de
integración DENTRO del SDK; Groq no — y está bien que así sea, porque
cada consulta consume la cuota de ALGUIEN. La decisión es la misma de las
fotos de la fase 1 (D-08): cada alumno trae la suya. Vas a
**console.groq.com**, te creas una cuenta (email, Google o GitHub —
gratis y **sin tarjeta de crédito**, RNF-08), sección **API Keys** →
**Create API Key**. Ojo con el detalle que no perdona: la key se muestra
**UNA sola vez** — cierras la página y ya no la ves — así que la copias
al `.env` DE INMEDIATO. La key que creas es TUYA: los límites del free
tier aplican por organización, así que tu cuota queda aislada de la del
curso entero, y nadie más la ve. Dos honestidades antes de pegarla.
Primera: el free tier tiene límites públicos y generosos — 30 RPM /
1.000 RPD para el modelo de esta guía a la fecha (D-68) — suficientes
para el curso, con las cifras citadas con fuente en el paso 5. Segunda:
la key es una credencial, y el material del curso JAMÁS contiene una de
verdad — la guía versiona una PLANTILLA con la línea vacía y tu key vive
solo en TU `.env` (gitignoreado desde la guía 1). Por eso este paso no
tiene ningún string que copiar con forma de key: si un día ves una key
real en un tutorial, esa persona ya tiene que cambiarla.*

En **console.groq.com**, crea tu key y cópiala en el MISMO instante (la
página no la volverá a mostrar; no la pegues en ningún chat ni commit).
Ahora, en **`backend/.env.example`** — la plantilla que SÍ se versiona —
agrega la línea nueva AL FINAL, con el valor VACÍO:

```
# Copia este archivo como .env y reemplaza cada valor por el TUYO.
# El .env ya está gitignoreado desde la guía 1: lo que se versiona es
# este ejemplo, jamás el secreto real.
SECRET_KEY=pega-aqui-el-resultado-del-comando-token-hex
ADMIN_EMAIL=admin@maura.cl
ADMIN_PASSWORD=elige-una-clave-para-tu-admin-demo
CLIENTE_EMAIL=clienta@maura.cl
CLIENTE_PASSWORD=elige-una-clave-para-tu-clienta-demo
# La asesora de aromas (guía 14): OPCIONAL — sin esta línea la tienda
# sigue 100% operativa y el asistente degrada a 503 amable (D-61).
GROQ_API_KEY=
```

Y en TU **`backend/.env`** (el que no se sube), agrega al final tu key
real:

```
GROQ_API_KEY=aqui-tu-key-real-que-nunca-sale-de-este-archivo
```

✅ **Mini-verificación:** desde `backend/`, ejecuta (nota: el VALOR jamás
se imprime — verificar que existe no es leerlo en pantalla):

```
uv run python -c "from pathlib import Path; lineas = Path('.env').read_text().splitlines(); hay = any(l.startswith('GROQ_API_KEY=') and l.strip() != 'GROQ_API_KEY=' for l in lineas); print('key presente:', hay)"
```

Debe imprimir `key presente: True` — y ninguna parte del comando mostró
tu key. La costumbre importa: los secretos se verifican por existencia,
nunca por impresión.

---

## Paso 3 — `Settings` gana la key: OPCIONAL, y el contraste es la lección (D-61)

🧠 **El desarrollador piensa:** *una línea de código… que es la decisión
de arquitectura del día, por contraste. `secret_key` en la guía 5 se
declaró **sin default**: si el `.env` no existe, pydantic revienta al
importar y la app NO PARTE — fail-fast, porque una tienda que firma
tokens con un secreto inventado por omisión es una tienda insegura y ni
siquiera se entera. Hoy llega el segundo secreto del mismo `.env` y
merece la estrategia OPUESTA: `groq_api_key: str | None = None`. ¿Por
qué? Porque el asistente es un servicio OPCIONAL (D-61): sin key, la
tienda entera — login, catálogo, carro, checkout, panel — debe seguir
100% operativa y solo la asesora degrada a "no disponible". Fail-fast
acá apagaría la tienda por un servicio que nadie necesita para comprar.
Dos secretos del mismo archivo, dos estrategias correctas distintas — y
la diferencia no es gusto: es qué pasa con el negocio si falta. Este
contraste explícito es exactamente lo que ADR-018 registra como decisión
(heredada íntegra del ADR-017 que supersede).*

En **`backend/app/config.py`**, agrega el campo dentro de `Settings`
(como un bloque Etapa 4 al final, tras el bloque de la etapa 3 — cada
etapa suma su bloque, en orden):

```python
    # --- Etapa 4: la asesora de aromas (ADR-018) ---
    # OPCIONAL por diseño (D-61): el asistente es un servicio que DEGRADA,
    # no un requisito de arranque. El contraste con secret_key es la
    # lección: la firma de sesiones es obligatoria (fail-fast sin .env);
    # la asesora, opcional (la tienda sigue 100% operativa sin key).
    groq_api_key: str | None = None
```

✅ **Mini-verificación:** desde `backend/`, ejecuta:

```
uv run python -c "from app.config import Settings; print(Settings.model_fields['groq_api_key'].default, '|', Settings.model_fields['secret_key'].default)"
```

Debe imprimir `None | PydanticUndefined` — las DOS estrategias en una
línea: la key de Groq tiene default `None` (arranca sin ella), y
`secret_key` sigue `PydanticUndefined` (sin `.env` la app no parte).
Nadie escribió un `if` para lograrlo: el default ES la estrategia.

---

## Paso 4 — `schemas/asistente.py`: los topes del contrato y el modelo del round-trip

🧠 **El desarrollador piensa:** *tres modelos, tres trabajos distintos —
y confundirlos es confundir el contrato. **`ChatMensaje`** es lo que
ENTRA: espejo del contrato 0.4.0 con los topes de RN-16 (`mensaje` máximo
500 caracteres, `historial` máximo 10 entradas — y cada `texto` del
historial con el MISMO tope de 500: en un endpoint público, TODO el texto
que viaja al modelo lo controla el cliente) — Pydantic los valida en
el borde, y un payload pasado de la raya recibe 422 sin que nadie escriba
un `if`: la validación declarativa de siempre, ahora protegiendo el free
tier de TU key (D-59). El historial es stateless por diseño (D-58): el
backend no guarda conversaciones — cero tablas nuevas —, solo acota lo
que le mandan. **`Recomendacion`** es el round-trip con el servicio de
IA: el MISMO modelo Pydantic genera el schema del pedido
(`.model_json_schema()` viaja en el `response_format` del paso 5) Y
valida la vuelta (`model_validate_json`) — un solo lugar de verdad para
la forma de la respuesta (Don't Hand-Roll: ni prompt-engineering de
"responde solo JSON", ni validador a mano campo por campo). Y hoy gana
UNA línea nueva con historia: `model_config = ConfigDict(extra="forbid")`.
El modo strict del paso 5 exige DOS cosas que un schema Pydantic pelado
NO cumple solo: todos los campos en `required` (eso Pydantic sí lo emite)
y `additionalProperties: false` (eso NO — lo comprobó el probe de la fase
contra pydantic 2.13.5). `extra="forbid"` hace que el schema emitido lo
declare — y de paso la validación de la VUELTA queda más estricta: un
JSON con una clave de más que se colara, revienta acá. Una línea, doble
duty: requisito del servicio Y muralla adicional de nuestra frontera.
Fíjate que NO le pongo tope
a `productos`: lo que se le PIDE al modelo y lo que el contrato PROMETE
son cosas distintas — el tope de 3 lo aplica el service, después de
filtrar contra la base. **`ChatRespuesta`** es lo que SALE: la forma del
contrato, con el `max_length=3` explícito — el endpoint responde lo que
el contrato dice, ni un id más.*

Crea **`backend/app/schemas/asistente.py`**:

```python
"""Schemas del asistente de venta — contrato_api.yaml 0.4.0 (tag Asistente).

ChatMensaje es lo que entra (con los topes de RN-16 que protegen el free
tier); Recomendacion es el round-trip con el servicio de IA (el modelo que
genera el schema del pedido Y valida la vuelta — y habilita el modo
strict); ChatRespuesta es lo que sale (los ids, ya validados contra la
base y truncados a 3 por el service).
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MensajeHistorial(BaseModel):
    """Una entrada del historial visible que mantiene el navegador (D-58)."""

    rol: Literal["clienta", "asesora"]
    # El MISMO tope del mensaje nuevo (RN-16): el texto del historial
    # también lo controla el cliente — y también viaja entero al modelo.
    texto: str = Field(max_length=500)


class ChatMensaje(BaseModel):
    """POST /api/asistente — lo que la burbuja envía (AIAS-01, RN-16).

    Multi-turno stateless: el historial viaja en cada request porque el
    backend NO guarda conversaciones (cero tablas para el asistente).
    """

    mensaje: str = Field(
        max_length=500,
        description="El mensaje nuevo de la visitante — máximo 500 caracteres",
    )
    historial: list[MensajeHistorial] = Field(
        default_factory=list,
        max_length=10,
        description="Los últimos mensajes de la conversación, tal como los mantiene el navegador",
    )


class Recomendacion(BaseModel):
    """El JSON que el servicio de IA debe devolver (D-56): el texto + los ids citados.

    Este MISMO modelo genera el schema del pedido (.model_json_schema() va
    en el response_format del paso 5) y valida la vuelta
    (model_validate_json): round-trip Pydantic → schema → respuesta del
    modelo → Pydantic, un solo lugar de verdad. extra="forbid" habilita
    el modo strict (exige additionalProperties: false — pydantic NO lo
    emite solo) y de paso endurece la validación de la vuelta: doble
    duty. Sin tope en productos: el máximo de 3 lo aplica el SERVICE tras
    filtrar contra la base — pedirle al modelo y prometer en el contrato
    son cosas distintas.
    """

    model_config = ConfigDict(extra="forbid")

    respuesta: str
    productos: list[int]


class ChatRespuesta(BaseModel):
    """La respuesta del endpoint (AIAS-02): ids ya validados y truncados."""

    respuesta: str
    productos: list[int] = Field(max_length=3)
```

✅ **Mini-verificación:** desde `backend/`, ejecuta:

```
uv run python -c "from app.schemas.asistente import ChatMensaje, ChatRespuesta, Recomendacion; s = ChatMensaje.model_json_schema(); r = Recomendacion.model_json_schema(); print(s['properties']['mensaje'].get('maxLength'), s['$defs']['MensajeHistorial']['properties']['texto'].get('maxLength'), s['properties']['historial'].get('maxItems'), ChatRespuesta.model_json_schema()['properties']['productos'].get('maxItems'), '|', r.get('additionalProperties'), sorted(r.get('required', [])))"
```

Debe imprimir `500 500 10 3 | False ['productos', 'respuesta']` — dos
lecciones en un output. La primera mitad son los topes de RN-16 nacidos
declarativos en el schema: el del mensaje, el del `texto` de cada
entrada del historial (el MISMO 500 — el contenido que el cliente
controla también viaja al modelo), el del historial y el de las cards;
fíjate por dónde se llega al segundo: Pydantic v2 NO inlinea el modelo
anidado — `historial` apunta por `$ref` a `$defs/MensajeHistorial`, y el
tope del `texto` vive adentro de ese `$defs` (imprime `s` entero si
quieres verlo: es un mini-`contrato_api.yaml` generado). La segunda
mitad es la nueva: el schema EMITIDO de `Recomendacion` trae
`"additionalProperties": false` (gracias a `extra="forbid"`) y
`required` con los DOS campos — exactamente lo que el modo strict del
paso 5 va a exigir. El 422
que los hace cumplir lo verás golpear en el paso 8; lo que generan ya
está en el contrato (`ChatMensaje`/`ChatRespuesta` en
`contrato_api.yaml` — ábrelo y compara: deben calzar campo a campo).

---

## Paso 5 — `services/asistente.py`: el único archivo que importa groq

🧠 **El desarrollador piensa:** *el corazón de la fase, y es el espejo
estructural EXACTO de `services/webpay.py` de la guía 9 (Paso 5): un
wrapper chico con una regla grande — ESTE es el único archivo del
proyecto que escribe `from groq import`, y ni imports, ni
errores, ni vocabulario del SDK cruzan su frontera (IN-06). Las piezas,
una a una. **El modelo vive en una constante (D-64):**
`MODELO_ASISTENTE = "openai/gpt-oss-120b"`, el mismo ceremonial de
`STOCK_BAJO_UMBRAL` en la guía 12 — nombre propio, valor fijo, respaldo
de decisión. ¿Por qué constante y no el string inline? Porque el nombre
del modelo es la pieza más frágil del stack: Groq depreca modelos
periódicamente (aviso típico de 30 días por documentación, email y
banners de la consola) — con un matiz que juega a favor: los
*production models* como gpt-oss-120b no se decomisionan como los labs.
Si un día tu modelo deja de responder, `client.models.list()` lista los
vigentes — el paso 8 te lo corre como mini-exploración. **El client es
LAZY** (`_client` arranca en `None` y se construye a la primera llamada):
la app debe importar y encender SIN key — y fíjate DÓNDE vive la
construcción: DENTRO del `try`, porque `Groq()` sin key lanza
`GroqError` EN LA CONSTRUCCIÓN (lo verificó el probe de la fase con el
SDK 1.7.0), no a la primera llamada. Y la key se pasa EXPLÍCITA desde
NUESTRO `Settings` — ojo con este gotcha, porque el README del SDK
promete que el client "levanta `GROQ_API_KEY` del entorno
automáticamente" ("this is the default and can be omitted"): cierto, del
ENTORNO DEL PROCESO — pero pydantic-settings lee el `.env` hacia el
OBJETO Settings, no exporta nada a las variables de entorno del proceso,
y el SDK no lee archivos. Si confías en el auto-pickup, tu `.env`
existe, el SDK no lo ve, y el error llega recién a la primera llamada,
con un mensaje que no menciona tu `.env`. Explícito es determinista.
**El system prompt se arma POR REQUEST** con el catálogo
ACTIVO consultando el repositorio (mini-RAG honesto, D-56): id, nombre,
familia, notas y precio de los 12 SKU — cabe entero, y si mañana la dueña
desactiva un aroma en el panel de la guía 12, el PRÓSIGUIENTE prompt ya
no lo lista: el prompt no se cachea nunca. La voz es la de Maura en
primera persona (D-02): tuteo chileno, cálida, breve — "si te gusta lo
cítrico…". **La llamada** es `client.chat.completions.create` — el
dialecto OpenAI-compatible de la API de Groq — con `response_format`
`json_schema` y `strict: true`: *constrained decoding*, el servicio
garantiza que la respuesta calza el schema. El patrón está firmado DOS
veces (la disciplina de siempre: doc oficial de Structured Outputs + el
probe del research contra el SDK 1.7.0 el 2026-10-01) y el schema viaja
en la llamada — el prompt lleva catálogo y voz, no instrucciones de
formato. **La muralla anti-alucinación es doble y
del SERVIDOR** (D-56): el prompt solo lista activos (muralla 1) y cada id
que devuelve el modelo se filtra contra el catálogo activo en la BASE
antes de responder, con truncado a 3 (muralla 2) — un modelo que
desobedece o alucina solo puede producir texto; las cards que el chat
mostrará existen o no existen, y eso no lo decide el modelo. **Y el
ALCANCE temático también vive en el prompt** — porque la muralla NO lo
cubre: una respuesta fuera de tema con la lista de productos VACÍA es
una respuesta perfectamente válida para el contrato, así que "La
capital de Francia es París" cruzaría la muralla sin rozarla (lo
reproducimos en el paso 8). El prompt lo cierra con una cláusula de
alcance: Maura solo conversa sobre aromas, notas y su tienda —
cualquier otra pregunta se deflecta breve y en su voz, invitando a
volver a los aromas. La muralla valida PRODUCTOS con código; de qué se
puede hablar lo escribe el prompt (AIAS-01: Maura en persona tampoco
da clases de geografía en su tienda). **El
wrapper** atrapa los errores tipados del SDK: `RateLimitError` → señal
de cuota — con las cifras públicas a la vista, porque Groq SÍ las
publica: 30 RPM / 1.000 RPD / 8K TPM / 200K TPD para
`openai/gpt-oss-120b` a la fecha de esta guía, en
[console.groq.com/docs/rate-limits](https://console.groq.com/docs/rate-limits)
— y los límites exactos de TU organización viven en la página Limits de
la propia consola (D-68). Para el aula: 1.000 RPD son ~16 consultas por
minuto sostenidas TODO el día — de sobra. TODO lo demás — la jerarquía
`GroqError` completa: `APIStatusError` de los 4xx/5xx HTTP,
`APIConnectionError` y su hija `APITimeoutError`, y la construcción sin
key — es señal de no disponible. ¿`except Exception` en un wrapper? Sí:
acá la regla es que NADA de esta integración cruce como 500 crudo
(IN-06) — las dos señales de dominio son lo único que sale. Y **SIN
retry casero**: el SDK ya reintentó 2 veces por defecto (errores de
conexión, 408, 409, 429 y 5xx, backoff corto exponencial) ANTES de
entregarte el error — y ojo con el reloj: TAMBIÉN reintenta el 429, así
que el `RateLimitError` te llega ~2-4 s después de la primera negativa,
no de inmediato. El wrapper TRADUCE, no re-intenta.*

Crea **`backend/app/services/asistente.py`**:

```python
"""El service de la asesora de aromas — ÚNICO archivo que importa groq.

Espejo estructural de services/webpay.py (guía 9, IN-06): ni imports, ni
errores, ni vocabulario del SDK cruzan esta frontera. Lo que sale son DOS
señales de dominio — CuotaAgotada (429) y AsistenteNoDisponible (503) —
que el router traduce a HTTPException con los copys amables del contrato.
Sin GROQ_API_KEY la señal sale TEMPRANO, sin tocar la red (D-61): el
asistente es opcional, la tienda no.
"""

from groq import Groq, GroqError, RateLimitError
from sqlalchemy.orm import Session

from app.config import settings
from app.repositories.producto import ProductoRepository
from app.schemas.asistente import ChatMensaje, ChatRespuesta, Recomendacion

# RN-16: máximo de product cards por respuesta — el tope lo aplica ESTA
# capa, después de filtrar los ids contra la base.
MAX_CARDS = 3

# El modelo de la asesora (D-64): constante con nombre propio, mismo
# ceremonial que STOCK_BAJO_UMBRAL de la guía 12 — si Groq depreca el
# modelo, ESTA línea es la única que cambia. production model: no se
# decomisiona como los labs, pero Groq avisa deprecaciones con típicamente
# 30 días — models.list() (paso 8) es el diagnóstico el día que el nombre
# deje de responder.
MODELO_ASISTENTE = "openai/gpt-oss-120b"


class CuotaAgotada(Exception):
    """429 — el free tier dijo basta: 30 RPM / 1.000 RPD por organización (D-68)."""


class AsistenteNoDisponible(Exception):
    """503 — sin key, servicio caído, timeout, red o JSON que no calza."""


# LAZY (D-61): arranca en None y se construye a la primera llamada — la
# app debe encender SIN key. El módulo se importa siempre; el client, no.
_client: Groq | None = None


def _obtener_client() -> Groq:
    global _client
    if _client is None:
        # La key va EXPLÍCITA desde NUESTRO Settings (IN-03): el SDK
        # auto-pickupea GROQ_API_KEY del entorno ("this is the default
        # and can be omitted", su README) PERO no lee el archivo .env —
        # pydantic-settings lee el .env hacia el OBJETO, no hacia el
        # entorno del proceso: el loader de la key es Settings.
        _client = Groq(api_key=settings.groq_api_key)
    return _client


def _prompt_sistema(catalogo: list) -> str:
    """El mini-RAG honesto (D-56): persona de Maura + catálogo ACTIVO completo.

    Se arma POR REQUEST (jamás cacheado): si la dueña desactivó un aroma en
    el panel, el siguiente prompt ya no lo lista. Sin el schema acá: viaja
    en el response_format de la llamada — el prompt lleva catálogo y voz,
    no formato.
    """
    lineas = [
        "Eres Maura, la dueña de una tienda chilena de body splash, atendiendo",
        "tu tienda online. Solo conversas sobre aromas, notas, tu tienda y",
        "tu catálogo: cualquier otra pregunta (geografía, historia, ciencia,",
        "cualquier tema) NO la contestas — respondes solo con una frase breve",
        "y cálida, en tu voz, invitando a la clienta a contarte qué aroma",
        "busca. Ejemplo: si preguntan la capital de Francia, NO la dices:",
        "respondes que de eso no sabes nada y que te cuenten qué frescura",
        "andan buscando.",
        "Cuando la clienta habla de aromas, recomiendas en primera persona,",
        "con tuteo chileno, cálida y breve (dos o tres frases). Recomiendas",
        "SOLO productos de este catálogo, priorizando los que calzan con lo",
        "que la clienta cuenta que le gusta, y citando sus id en el campo",
        "productos (máximo 3). Si nada del catálogo calza, responde sin",
        "productos. El campo respuesta jamás contiene información ajena a",
        "aromas, notas, tu tienda o tu catálogo.",
        "",
        "Catálogo (productos activos de la tienda):",
    ]
    for p in catalogo:
        lineas.append(
            f"id={p.id} nombre={p.nombre} familia={p.familia.value}"
            f" notas={', '.join(p.notas)} precio={p.precio}"
        )
    return "\n".join(lineas)


def _conversacion(datos: ChatMensaje) -> str:
    """El historial visible (D-58) + el mensaje nuevo, como transcripto."""
    partes = [
        f"{'Clienta' if m.rol == 'clienta' else 'Asesora'}: {m.texto}"
        for m in datos.historial
    ]
    partes.append(f"Clienta: {datos.mensaje}")
    return "\n".join(partes)


class AsistenteService:
    """El caso de uso de la asesora (AIAS-01/AIAS-02, ADR-018)."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def conversar(self, datos: ChatMensaje) -> ChatRespuesta:
        # El mini-RAG consulta la MISMA base que el catálogo: listar() trae
        # SOLO activos — muralla 1: lo que el prompt no lista, el modelo
        # no lo puede citar (D-56).
        catalogo = ProductoRepository(self.db).listar()
        ids_validos = {p.id for p in catalogo}

        if not settings.groq_api_key:
            # D-61: degradación TEMPRANA — ni client ni red. `not` cubre
            # los DOS estados sin key: ausente (None) y la línea VACÍA
            # que la plantilla modela (`GROQ_API_KEY=` en el
            # .env.example). La tienda sigue operativa; solo la asesora
            # no está.
            raise AsistenteNoDisponible()

        try:
            # La construcción del client vive DENTRO del try: `Groq()` sin
            # key lanza GroqError EN LA CONSTRUCCIÓN (probe de la fase) —
            # cubierta por el mismo traductor que la red y el timeout.
            client = _obtener_client()
            completion = client.chat.completions.create(
                model=MODELO_ASISTENTE,
                messages=[
                    {"role": "system", "content": _prompt_sistema(catalogo)},
                    {"role": "user", "content": _conversacion(datos)},
                ],
                # Structured output (doc oficial + probe del research,
                # SDK 1.7.0): json_schema strict — el MISMO Recomendacion
                # del paso 4 genera el schema y valida la vuelta.
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "Recomendacion",
                        "strict": True,
                        "schema": Recomendacion.model_json_schema(),
                    },
                },
            )
            # Round-trip Pydantic: el MISMO modelo que generó el schema
            # valida la vuelta — un JSON que no calza no pasa (Don't
            # Hand-Roll).
            recomendacion = Recomendacion.model_validate_json(
                completion.choices[0].message.content
            )
        except RateLimitError as e:
            # 429 es cuota (con cifras públicas — 🧠 de arriba, D-68);
            # OJO: va ANTES que GroqError porque hereda de ella.
            raise CuotaAgotada() from e
        except GroqError as e:
            # La jerarquía completa del SDK (APIStatusError de los
            # 4xx/5xx, APIConnectionError, APITimeoutError⊂connection) y
            # la construcción sin key: todo es "no disponible".
            raise AsistenteNoDisponible() from e
        except Exception as e:
            # La frontera IN-06: un JSON que no calza o cualquier otra
            # sorpresa de la integración — NADA cruza como 500 crudo. Y
            # SIN retry casero: el SDK ya reintentó 2 veces (incluido el
            # 429) antes de entregar el error; el wrapper traduce, no
            # re-intenta.
            raise AsistenteNoDisponible() from e

        # Muralla 2 (D-56): cada id contra el catálogo ACTIVO en la base —
        # los alucinados o desactivados se descartan en silencio; 3 cards
        # máximo (RN-16). El chat solo puede mostrar lo que existe.
        productos = [i for i in recomendacion.productos if i in ids_validos][:MAX_CARDS]
        return ChatRespuesta(respuesta=recomendacion.respuesta, productos=productos)
```

✅ **Mini-verificación:** desde `backend/`, ejecuta:

```
uv run python -c "from app.services import asistente; print(asistente._client)"
```

Debe imprimir `None` — el client LAZY sin construir: el módulo importó,
la app puede encender, y nadie tocó la red ni pidió key. Y comprueba el
aislamiento (la regla de la guía 9, ahora para Groq):
`grep -r "from groq" backend/app` debe listar SOLO `services/asistente.py`
— ni un import del SDK fuera del wrapper.

---

## Paso 6 — `routers/asistente.py`: público por diseño, con las CUATRO responses declaradas

🧠 **El desarrollador piensa:** *el router más corto de la etapa 4, con
las dos decisiones que importan. **Público por diseño (D-59)**: el
`security: []` del contrato — la segunda aparición del patrón después
del retorno de Webpay — en FastAPI se implementa como la AUSENCIA de
dependencias de auth: nada de `Depends(get_current_user)`, nada de
`get_current_admin`. ¿Por qué? Porque la asesora atiende a quien navega
la tienda, CON o SIN cuenta (P8): exigir sesión para que te recomienden
un aroma sería ponerle llave al vendedor. La burbuja de la guía 15 vive
en las páginas públicas — este endpoint tiene que responderle a una
visitante anónima. ¿Y el abuso? Los topes de RN-16 ya validaron en el
borde (422) y el 429 traduce la cuota — el endpoint público deliberado
es la decisión, sus salvaguardas ya están (T-04-13). **Las responses
TODAS declaradas** (lección G-01-4 de la guía 5, Pitfall 5 de la fase):
el 422 de los topes, el 429 de la cuota y el 503 de la degradación se
lanzan con `HTTPException` a mano en la traducción de señales — y una
`HTTPException` manual NO aparece en `/docs` si no se declara en
`responses`. La fila contrato ↔ `/docs` de la guía 15 compara el panel
contra el `contrato_api.yaml` uno a uno: sin la declaración, cantaría un
desvío falso. El router no valida nada ni conoce el SDK: Pydantic ya
validó (422), el service ya tradujo (dos señales) — este archivo solo
mapea señal → código HTTP con el copy EXACTO que el contrato examplea,
incluido el 429 SIN cifras de límites.*

Crea **`backend/app/routers/asistente.py`**:

```python
"""POST /api/asistente — la asesora de aromas (contrato_api.yaml 0.4.0).

PÚBLICO por diseño (D-59): el `security: []` del contrato — segunda
aparición del patrón después del retorno de Webpay (guía 9) — se
implementa como la AUSENCIA de dependencias de auth: la asesora atiende
a quien navega la tienda, con o sin cuenta. Pydantic ya validó los topes
(422, RN-16); este router solo traduce las DOS señales del service a
HTTPException con los copys amables del contrato. Jamás un 500 crudo
(IN-06) — y las CUATRO responses declaradas (lección G-01-4, Pitfall 5).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_session
from app.schemas.asistente import ChatMensaje, ChatRespuesta
from app.schemas.producto import Error  # el cuerpo de error vive acá desde la guía 4
from app.services.asistente import AsistenteNoDisponible, AsistenteService, CuotaAgotada

router = APIRouter(tags=["Asistente"])


@router.post(
    "",
    response_model=ChatRespuesta,
    responses={
        422: {
            "description": "Topes violados (mensaje o texto del historial sobre 500 caracteres, historial sobre 10 mensajes) — validación declarativa (RN-16)",
            "model": Error,
        },
        429: {
            "description": "Cuota del free tier del servicio de IA consumida — mensaje amable, sin cifras de límites",
            "model": Error,
        },
        503: {
            "description": "Servicio externo no disponible (sin key en el .env o servicio caído) — degradación deliberada (D-61)",
            "model": Error,
        },
    },
)
def conversar(
    datos: ChatMensaje,
    db: Session = Depends(get_session),
) -> ChatRespuesta:
    """POST /api/asistente — recomienda SOLO del catálogo real, ids ya validados (máximo 3)."""
    try:
        return AsistenteService(db).conversar(datos)
    except CuotaAgotada:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="La asesora está recibiendo muchas consultas. Espera unos segundos y reintenta.",
        )
    except AsistenteNoDisponible:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La asesora no está disponible en este momento. Inténtalo más tarde.",
        )
```

✅ **Mini-verificación:** el router importa limpio y sus señales están
mapeadas:

```
uv run python -c "from app.routers.asistente import router; print(len(router.routes), router.routes[0].responses.keys())"
```

Debe imprimir `1 dict_keys([422, 429, 503])` — una sola operación y las
TRES responses que se lanzan a mano (sin `responses`, ni siquiera
aparecerían en `/docs`). ¿Y el 200? No vive en el atributo: FastAPI
guarda `route.responses` tal cual se lo pasaste y agrega el 200 recién
al GENERAR el OpenAPI — el paso 7 lo cobra en `/docs`, donde la
operación desplegada lista las CUATRO del contrato, 200 incluido.

---

## Paso 7 — `main.py`: solo el `include_router` de siempre

🧠 **El desarrollador piensa:** *el paso más chico del backend de la
etapa, y esa es exactamente la noticia. Nada de versión nueva (0.4.0 se
subió con el panel en la guía 12 — el asistente ya estaba DECLARADO en
ese contrato, D-15: el contrato fue aprobado completo antes de que
existiera una sola línea de esta guía), nada de CORS (el endpoint es un
POST JSON más entre los que ya cruzan; en desarrollo el proxy de Vite
los hace same-origin, como todos desde la guía 2), nada de dependencias
globales (el endpoint es público: no hay candado que declarar). Solo el
`include_router` con su prefijo — el mismo molde de las nueve inclusiones
que ya viven en `main.py`. Cuando el paso final de una integración es
una línea, las capas hicieron su trabajo.*

En **`backend/app/main.py`**, agrega el import junto a los de los demás
routers:

```python
from app.routers import asistente
```

Y al final de la lista de inclusiones:

```python
app.include_router(asistente.router, prefix="/api/asistente")
```

✅ **Mini-verificación:** enciende la API (`uv run fastapi dev app/main`
desde `backend/`) y abre **http://localhost:8000/docs**:

1. El título sigue diciendo **Maura API 0.4.0** — la versión no se toca:
   el asistente ya vivía en este contrato.
2. Aparece el tag **Asistente** con `POST /api/asistente` — y desplegado
   lista **200, 422, 429 y 503**: las cuatro responses del paso 6
   visibles en el panel (la lección G-01-4 cobrada).
3. La operación está **SIN candado** 🔒 — pública como el retorno de
   Webpay, la segunda aparición deliberada del patrón (D-59). Compara
   contra `contrato_api.yaml`: el `security: []` del path y el candado
   ausente dicen lo mismo.

---

## Paso 8 — La prueba de fuego: recomendación real, topes 422, la degradación SIN key y el diagnóstico de modelos

🧠 **El desarrollador piensa:** *la batería de cierre, ordenada para no
depender de nada que no controles. Primero el happy path CON tu key: un
mensaje de prueba y la verificación de que los ids que devuelve EXISTEN
en el catálogo — porque la muralla del servidor no se demuestra
confiando, se demuestra comprobando (la prueba consulta la MISMA base
que el service). Sigue una pregunta trampa fuera de tema: el alcance de
la asesora lo fija el prompt del paso 5, y esta es la prueba de que la
cláusula deflector a funciona — la muralla sola no la cubriría. Luego
los topes: 501 caracteres y
un historial de 11 — el 422 declarativo de RN-16, sin que nadie escribiera
un `if`. Después la verificación que NO necesita key (la que el
material puede prometer sin depender de nadie): comentar la línea del
`.env`, reiniciar, y el endpoint responde 503 con el copy amable —
mientras la tienda entera sigue operativa. Esa es D-61 hecha runtime: la
asesora es un huésped opcional de la tienda, no un pilar. Y de postre la
mini-exploración `models.list()` — el diagnóstico del paso 5 corriendo
en TU máquina, con TU key. Si tu key no está o no quieres gastar cuota:
corre igual los golpes 2 y 3 — la degradación y los topes no tocan el
servicio de IA para nada.*

Con la API encendida y el seed corrido. Los golpes, en orden:

✅ **Mini-verificación (la recomendación con ids que EXISTEN):** desde
`backend/`, ejecuta:

```
uv run python -c "import httpx; r = httpx.post('http://localhost:8000/api/asistente', json={'mensaje': 'algo cítrico para el día'}); catalogo = {p['id'] for p in httpx.get('http://localhost:8000/api/productos').json()}; d = r.json(); print(r.status_code, d['respuesta'][:60], 'ids validos:', [i for i in d['productos'] if i in catalogo] == d['productos'], '| cards:', len(d['productos']))"
```

Debe imprimir `200`, el comienzo de una recomendación CON LA VOZ de Maura
(primera persona, tuteo — D-02), `ids validos: True` y `cards:` entre 0 y
3 — cada id que el endpoint devolvió existe en el catálogo activo (la
consulta a `/api/productos` es la misma tabla de activos contra la que
el service filtró): la
muralla del servidor funcionó (puede que el modelo cite ids y el filtro
los pase todos; puede que cite basura y devuelva `[]` — ambas son
respuestas CORRECTAS del contrato, AIAS-02).

✅ **Mini-verificación (la pregunta trampa — el alcance de la asesora):**
con tu key activa, desde `backend/`, ejecuta:

```
uv run python -c "import httpx; r = httpx.post('http://localhost:8000/api/asistente', json={'mensaje': 'cuál es la capital de Francia?'}); d = r.json(); print(r.status_code, d['respuesta'][:80], '| cards:', len(d['productos']))"
```

Debe imprimir `200` con una respuesta en la voz de Maura que NO contesta
la pregunta — ninguna capital, solo un amable regreso a los aromas — y
`cards: 0`. Esa es la cláusula de alcance del paso 5 funcionando: la
muralla del servidor valida PRODUCTOS, pero una respuesta off-topic con
lista vacía también calza el contrato — de qué se puede hablar lo decide
el prompt (AIAS-01: "como lo haría Maura en persona"). Y si tu modelo
igual suelta la capital, estás viendo la diferencia entre la muralla
DURA (validación por código, imposible de saltar) y el contrato BLANDO
del prompt (una instrucción que un modelo puede desobedecer):
endurece la cláusula y vuelve a probar — el prompt es la única capa
que gobierna el alcance.

✅ **Mini-verificación (los topes del free tier, 422):**

```
uv run python -c "import httpx; r1 = httpx.post('http://localhost:8000/api/asistente', json={'mensaje': 'a' * 501}); r2 = httpx.post('http://localhost:8000/api/asistente', json={'mensaje': 'hola', 'historial': [{'rol': 'clienta', 'texto': 'x'}] * 11}); print(r1.status_code, r2.status_code)"
```

Debe imprimir `422 422` — los dos topes de RN-16 golpearon ANTES de
tocar el servicio de IA: 501 caracteres en el mensaje, 11 entradas en el historial.
Ninguno gastó un token de tu cuota (esa es la razón de ser de los topes:
validar en el borde, D-59).

✅ **Mini-verificación (la degradación SIN key — y la tienda en pie):**
en `backend/.env`, COMENTA la línea de la key (anteponle `#`), reinicia
la API y ejecuta:

```
uv run python -c "import httpx; a = httpx.post('http://localhost:8000/api/asistente', json={'mensaje': 'hola'}); s = httpx.get('http://localhost:8000/api/salud'); c = {p['id'] for p in httpx.get('http://localhost:8000/api/productos').json()}; print(a.status_code, a.json()['detail'], '| salud:', s.status_code, '| catalogo:', len(c))"
```

Debe imprimir `503 La asesora no está disponible en este momento. Inténtalo más tarde. | salud: 200 | catalogo: 12` — el copy amable del contrato, la app ARRANCÓ sin key (client lazy + `str | None`, pasos 3 y 5) y la tienda sigue 100% operativa: re-prueba en el navegador login, catálogo, carro, checkout y panel — todo intacto (D-61). En el navegador se ve igual: la tienda completa, con la burbuja de la guía 15 avisando "no disponible" en vez de romperse. Descomenta la key y reinicia para volver al happy path.

✅ **Mini-verificación (models.list, el diagnóstico de la deprecación):**
con tu key activa, desde `backend/`, ejecuta:

```
uv run python -c "from app.config import settings; from groq import Groq; print([m.id for m in Groq(api_key=settings.groq_api_key).models.list().data])"
```

Debe imprimir una lista de ids de modelo que INCLUYE
`openai/gpt-oss-120b` — tu `MODELO_ASISTENTE` existe hoy. Guárdate este
comando: es la primera herramienta el día que el modelo de la constante
deje de responder (Groq avisa deprecaciones con típicamente 30 días, y
los production models no se decomisionan como los labs — pero la lista
de vigentes siempre manda, D-64).

---

## ❌ El error que este archivo evita

**1. La key en una variable `VITE_` "para que el frontend también pueda".**

```python
# ❌ CUALQUIER variable VITE_* termina dentro del bundle que baja el
# navegador: la key sería pública al primer visitante
VITE_GROQ_API_KEY=aqui-la-key   # en el .env del FRONTEND — jamás

# ✅ la key vive SOLO en el .env del BACKEND y sale por ningún cable:
# el navegador habla con TU endpoint; TU backend habla con Groq
# groq_api_key: str | None = None   # settings del BACKEND (D-63/RNF-09)
```

El frontend no necesita la key para nada: la burbuja de la guía 15
pregunta a TU API, y tu API es la única que conoce a Groq. La prueba
mecánica de que nada se filtró es la fila del grep del build en la Gran
verificación final — `grep -r "GROQ_API_KEY" dist/` con CERO
coincidencias tras `npm run build` — y esa fila existe porque este error
es el más tentador del proyecto (T-04-10).

**2. `model_json_schema()` pelado con `strict: true` (la línea que falta).**

```python
# ❌ el schema de Pydantic tal cual: sale con los campos en "required"
# PERO SIN "additionalProperties": false — y el modo strict lo EXIGE:
# la llamada falla o la garantía se pierde
response_format={"type": "json_schema", "json_schema": {
    "name": "Recomendacion", "strict": True,
    "schema": Recomendacion.model_json_schema(),   # pelado
}}

# ✅ UNA línea en el modelo habilita el modo strict Y endurece la vuelta
# (doble duty): Pydantic pasa a EMITIR "additionalProperties": false
class Recomendacion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    respuesta: str
    productos: list[int]
```

El modo strict es *constrained decoding*: el servicio garantiza que la
respuesta calza el schema — pero a cambio exige que TODOS los campos
estén en `required` y que cada objeto declare `additionalProperties:
false`. Pydantic v2 NO emite esa clave por defecto (probe de la fase
contra pydantic 2.13.5: el schema sale con `required` completo pero SIN
`additionalProperties`) — la línea que falta es
`ConfigDict(extra="forbid")`, y de paso la validación de la vuelta en TU
backend queda más estricta: el doble duty de una sola línea (Pitfall 2).

**3. Filtrar los ids alucinados en el frontend.**

```tsx
// ❌ "el chat revisa que el producto exista antes de mostrar la card" —
// la muralla en el navegador, donde un atacante la apaga con devtools
{respuesta.productos.filter((id) => catalogo.includes(id))}

// ✅ el chat renderiza lo que el backend YA validó: los ids que llegan
// existen y están activos, garantizado por el servidor (D-56, T-04-12)
{respuesta.productos.map((id) => <Card key={id} id={id} />)}
```

La validación de ids es responsabilidad del SERVIDOR (ADR-018): un
modelo desobediente — o un atacante que inyecta ids a mano en la
respuesta — solo puede producir texto si la muralla vive del lado de la
base. El frontend confía porque el backend ya verificó.

**4. Fail-fast sin key (y su primo, el 500 crudo).**

```python
# ❌ "sin .env no se parte" — mataría la TIENDA por un servicio OPCIONAL
groq_api_key: str  # sin default: pydantic revienta al importar

# ❌ el error del SDK cruzando hasta el navegador como 500 Internal Server
# Error, con el traceback de Groq en el log
return client.chat.completions.create(...)  # sin wrapper

# ✅ degradación (D-61): key opcional, client lazy, y TODA falla del
# servicio traducida a 503/429 amables — la tienda nunca depende de la IA
groq_api_key: str | None = None
```

`secret_key` y `GROQ_API_KEY` viven en el mismo `.env` con estrategias
opuestas a propósito: la firma de sesiones es obligatoria, la asesora no
(D-61, ADR-018). Y un 500 crudo del servicio externo jamás cruza la
frontera del wrapper — es la misma regla IN-06 que la guía 9 firmó para
`TransbankError`.

**5. El retry casero sobre el SDK que ya reintenta.**

```python
# ❌ "si falla, reintento yo" — un loop con sleep ENCIMA del SDK
for intento in range(3):
    try:
        return client.chat.completions.create(...)
    except GroqError:
        time.sleep(2 ** intento)  # doble-retry

# ✅ el SDK ya reintentó 2 veces (conexión, 408, 409, 429 y 5xx, backoff
# corto exponencial) ANTES de entregarte el error — el wrapper traduce,
# no re-intenta
except RateLimitError as e:
    raise CuotaAgotada() from e
except GroqError as e:
    raise AsistenteNoDisponible() from e
```

Duplicar el backoff del SDK presiona el free tier exactamente cuando ya
está agotado — cada reintento tuyo suma a la cuota que no te queda. Y ojo
con el reloj: el SDK TAMBIÉN reintenta el 429, así que el
`RateLimitError` te llega ~2-4 s después de la primera negativa
(Pitfall 4, anti-patrón del research).

**6. Confiar en el auto-pickup del entorno.**

```python
# ❌ "el SDK la levanta solo" — cierto del ENTORNO DEL PROCESO, falso del
# .env: tu archivo existe y el SDK no lo ve (no lee archivos)
_client = Groq()   # "this is the default and can be omitted"… del entorno

# ✅ explícita desde NUESTRO Settings (IN-03): pydantic-settings lee el
# .env hacia el OBJETO — el loader de la key es Settings, no el entorno
_client = Groq(api_key=settings.groq_api_key)
```

El README del SDK promete que el client levanta `GROQ_API_KEY` del
entorno automáticamente — y es cierto… del entorno del proceso, no de tu
`.env`. Con `api_key` explícita la fuente de la verdad es una sola
(Settings) y el modo strict de tu bóveda es el mismo de siempre:
explícito es determinista (gotcha IN-03, ADR-018).

---

## ✅ Verificación de la guía 14

Con la API encendida y el seed corrido:

1. `groq` instalado con el pin `>=1.7,<2` (el `pyproject.toml`
   registra el rango, no la versión suelta).
2. TU key creada en console.groq.com, en TU `.env` — y la plantilla
   `.env.example` versionada con la línea `GROQ_API_KEY=` VACÍA, sin
   key real en ningún archivo que se suba (D-63).
3. `Settings` con `groq_api_key: str | None = None`: la app arranca
   SIN key; el contraste con `secret_key` fail-fast es la lección (D-61).
4. `grep -r "from groq" backend/app` lista SOLO `services/asistente.py`
   — el aislamiento del SDK (espejo de la guía 9, IN-06).
5. `POST /api/asistente` en `/docs` con 200/422/429/503 declaradas y SIN
   candado — público como el retorno de Webpay (D-59).
6. La batería del paso 8: recomendación con voz de Maura e ids que
   EXISTEN en el catálogo, 422 en 501 chars y en historial de 11, la
   degradación SIN key (503 amable con la tienda en pie) — y
   `models.list()` listando el modelo vigente.

## 📝 Punto de control (respóndelas sin mirar la guía)

1. `secret_key` revienta el arranque sin `.env`; `groq_api_key` no.
   ¿Por qué dos secretos del mismo archivo merecen estrategias opuestas
   — y cómo se llama cada una? (D-61, ADR-018.)
2. El modo strict garantiza JSON que calza el schema — pero tu
   `Recomendacion` necesita una línea extra para habilitarlo. ¿Cuál es,
   qué exige el modo strict que Pydantic NO emite solo — y qué gana TU
   validación de vuelta con esa misma línea? (Pitfall 2, D-56.)
3. La muralla anti-alucinación tiene DOS muros y ambos son del servidor.
   ¿Qué hace cada uno — y qué ganaría un modelo desobediente (o un
   atacante) si el segundo muro se mudara al frontend? (D-56, ADR-018,
   T-04-11/T-04-12.)
4. El 429 de la asesora se traduce amable, y el SDK ya reintentó 2 veces
   antes de que lo veas. ¿Cuáles son las cifras del free tier para
   `openai/gpt-oss-120b` a la fecha de esta guía, contra qué fuente se
   firmaron — y qué DOS mecanismos del sistema de hoy protegen tu cuota
   ANTES de que el 429 pueda ocurrir? (RN-16, D-59/D-68.)

## Lo que acabas de aprender

- La segunda integración con servicio externo real — y el contraste
  completo con Webpay: request-response JSON sin redirecciones, con el
  MISMO patrón de aislamiento (un único archivo importa el SDK, el
  wrapper traduce TODOS los errores a señales de dominio, IN-06)
- El SDK oficial `groq` pinneado `>=1.7,<2` (piso probe-verified, techo
  próximo major — el criterio del corpus) y la API OpenAI-compatible
  como conocimiento transferible (`chat.completions.create` con mensajes
  de roles system/user)
- La key como paso del ALUMNO (D-63): tuya, gratis, sin tarjeta en
  console.groq.com, mostrada UNA sola vez y copiada al `.env` de
  inmediato — con plantilla versionada vacía y jamás una key real en el
  material (patrón D-08)
- `groq_api_key: str | None = None` con el contraste explícito del
  fail-fast de `secret_key` (D-61): degradación, client lazy, tienda
  100% operativa sin key
- Structured output con `response_format` `json_schema` `strict: true` —
  firmado DOS veces (doc oficial de Structured Outputs + probe del
  research contra el SDK 1.7.0) y habilitado por
  `ConfigDict(extra="forbid")`: el modo strict exige
  `additionalProperties: false` + todos los campos required, y esa misma
  línea endurece la validación backend (doble duty, Pitfall 2)
- `MODELO_ASISTENTE = "openai/gpt-oss-120b"` como constante con
  ceremonial (D-64, patrón STOCK_BAJO_UMBRAL) — con la lección de
  deprecación (aviso típico de 30 días; production models no se
  decomisionan como los labs) y `models.list()` como diagnóstico
- El mini-RAG honesto: catálogo ACTIVO completo en el system prompt de
  CADA request (12 SKU, voz de Maura en primera persona — D-02/D-56) y
  la doble muralla del servidor contra ids alucinados (prompt con
  activos + filtro contra base + truncado a 3, RN-16)
- El wrapper `RateLimitError` → 429 / `GroqError` → 503, sin retry
  casero (el SDK reintenta 2x — INCLUYENDO el 429, ~2-4 s) — jamás un
  500 crudo (T-04-13, IN-06)
- Las cifras del free tier citadas con fuente y "a la fecha" (30 RPM /
  1.000 RPD / 8K TPM / 200K TPD para `openai/gpt-oss-120b`,
  console.groq.com/docs/rate-limits — D-68)
- El endpoint público `POST /api/asistente` con `security: []` espejo
  del retorno de Webpay (D-59) y las CUATRO responses declaradas para
  que la fila contrato ↔ `/docs` no cante desvíos falsos (Pitfall 5)

**Siguiente:** guia-15-asistente-cierre.md — la burbuja en la tienda (la
cara visible de la IA, con sus cards clicables) y la Gran verificación
final de la fase 4 completa: panel, asistente, contrato 0.4.0 ↔ `/docs`
y el grep del build que prueba que la key jamás salió del backend.
