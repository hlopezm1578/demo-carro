# Guía 9 — Las órdenes y Webpay: el backend del pago

> **Qué construirás hoy:** el backend del pago: órdenes que nacen al pagar,
> Webpay de ida y vuelta, stock que no miente — el tier servidor completo de
> la etapa 3 (modelo con snapshot, checkout que recalcula sin confiar en el
> cliente, retorno que discrimina los 4 flujos con un 302, commit con criterio
> doble e idempotencia, y stock atómico).
> **Al terminar tendrás:** tu API cobrando de verdad en el ambiente de
> integración de Transbank y una orden PAID con stock descontado — además de
> la carrera de stock del final: dos compras disputando la última unidad y
> solo una gana (ORDR-02 observable en tu propia máquina).
> **Necesitas:** las guías 1 a 8 completas — el backend en capas con cuentas
> JWT y catálogo sembrado, la API encendida con `uv run fastapi dev
> app/main.py` y el seed corrido (14 `[=]` re-ejecutado). Abre
> `docs/04_arquitectura/contrato_api.yaml` 0.3.0 en una pestaña: como en las
> guías 4 y 5, es la vara que mide cada paso (D-15, ADR-007). Y ten a mano
> los ADRs 012-014: hoy se implementan los tres.

---

## Los términos de hoy (antes de copiar nada)

| Término | Qué es, en una frase |
|---|---|
| **Form POST auto-submit** | La salida hacia Webpay: un formulario construido en JavaScript que el navegador submitea solo — una navegación de página completa, no un `fetch` |
| **return_url** | La URL de TU backend que le entregas a Webpay al crear la transacción: a ella vuelve el navegador de la clienta cuando termina (o abandona) el formulario de pago |
| **token_ws / TBK_\*** | Los parámetros que trae el retorno: `token_ws` en el flujo normal; `TBK_TOKEN`, `TBK_ID_SESION` y `TBK_ORDEN_COMPRA` en los flujos abortados — la PRESENCIA de cada uno es la firma del flujo |
| **Commit** | La confirmación de la transacción contra Webpay: el endpoint que "cierra" el pago y devuelve `response_code` y `status` — el veredicto |
| **PRG / 302** | Post/Redirect/Get: el patrón clásico que responde una redirección que fuerza un GET del navegador — el 302 explícito, no el 307 que re-POSTearía |
| **buy_order** | El identificador de compra que exige Webpay (único, hasta 26 caracteres): será el numero legible del pedido (`MAURA-000001`) |
| **Snapshot** | La foto congelada al comprar: nombre y precio que la línea de la orden guarda para siempre, aunque el catálogo cambie después |

---

## Paso 1 — Un paquete nuevo (con las credenciales públicas dentro)

🧠 **El desarrollador piensa:** *un solo paquete, y una sorpresa agradable.
**`transbank-sdk`** es el SDK oficial de Transbank para Python (REST, sobre
`requests`) — y trae las credenciales del **ambiente de integración**
hardcodeadas como constantes públicas: el código de comercio
`597055555532` y su API key viven DENTRO del SDK. Eso significa dos cosas
que conviene decirse enteras: **no hay que registrarse en Transbank** (el
ambiente de integración es público, a propósito, para desarrollarse contra
él) y **no hay `.env` nuevo** — ninguna credencial secreta llega hoy; las
tarjetas de prueba son las documentadas por Transbank y el "pago" es de
sandbox, sin plata real. La tienda funciona en modo de prueba (RNF-07). Un
detalle técnico que ordena todo el resto del archivo: el SDK usa `requests`
(síncrono), así que las rutas que hablan con Webpay son `def` comunes —
FastAPI las corre en su threadpool; NO las escribas `async def` (el stack
lo decidió así desde la fase de investigación). Y ojo con la edad del
requisito: el README del SDK pide **Python 3.12+** — el mismo techo que tu
backend ya usa.*

Desde `backend/`, ejecuta:

```
uv add transbank-sdk
```

Tu `pyproject.toml` gana la dependencia congelada en `uv.lock` (RNF-04). El
SDK instala `requests` y `marshmallow` como dependencias suyas — no las
tocas: son internas del SDK.

✅ **Mini-verificación:** desde `backend/`, ejecuta:

```
uv run python -c "from transbank.common.integration_commerce_codes import IntegrationCommerceCodes; print(IntegrationCommerceCodes.WEBPAY_PLUS)"
```

Debe imprimir `597055555532` — la credencia pública de integración, leída
desde el propio SDK. Ese número NO va a tu `.env` ni a ningún código tuyo:
ya vive donde corresponde.

---

## Paso 2 — `models/pedido.py`: el enum por tercera vez, el snapshot y el numero legible

🧠 **El desarrollador piensa:** *el corazón del paso es un viejo conocido en
su tercera vuelta: **el gotcha del enum**. La guía 3 lo cerró con
`FamiliaAromatica`, la guía 5 con `RolUsuario` — y ahora vuelve con
`EstadoPedido`, porque `pending`/`paid`/`cancelled`/`rejected` son otra lista
cerrada. SQLAlchemy persiste los NOMBRES de los miembros: declarar
`PENDING = "pending"` guardaría `PENDING`… y el contrato 0.3.0 promete el
enum en minúsculas. La vacuna no cambia: **nombre == valor**. Alrededor del
enum, dos decisiones que estructuran todo lo demás. **La asimetría del
snapshot (D-36, RN-10):** en el carro, guardar el precio está PROHIBIDO
(RN-08) — sería un precio viejo esperando engañar; en la orden, guardarlo
es OBLIGATORIO — es el histórico de lo que se pagó. La misma columna, dos
preguntas opuestas: "lo que vale hoy" versus "lo que se pagó ese día". El
soft delete de la ficha (§2.3.5 del diseño) cierra el circuito: la FK a
productos sigue viva aunque el aroma desaparezca del catálogo, y con
snapshot el pedido viejo ni siquiera la necesita para mostrarse (ADR-014).
**El numero legible (D-37, RN-13):** la orden expone `MAURA-000001` — 11
caracteres, muy bajo el límite de 26 que exige Webpay para el `buy_order` —
y ese numero NACE del `id` autoincrement en la misma transacción: único por
construcción, jamás calculado con `max(id)+1` en Python (eso sería una
carrera con uno mismo). El `id` interno no se muestra ni viaja: identificador
público y clave primaria son cosas distintas.*

Crea **`backend/app/models/pedido.py`**:

```python
"""Modelos Pedido, LineaPedido y enum EstadoPedido (tablas `pedidos` y `pedidos_lineas`)."""

import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EstadoPedido(str, enum.Enum):
    """Estado de la orden. TERCERA vuelta del gotcha (guía 3: familias;
    guía 5: roles): SQLAlchemy persiste los NOMBRES, por eso nombre ==
    valor — la BD guarda "pending"/"paid"/"cancelled"/"rejected", los
    strings exactos del enum del contrato (RF-17)."""

    pending = "pending"      # nació al iniciar el pago; Webpay aún no responde ("en curso", RN-11)
    paid = "paid"            # commit aprobado: response_code == 0 Y status == AUTHORIZED (RF-15)
    cancelled = "cancelled"  # anulado por la clienta / timeout / error de formulario (ADR-012)
    rejected = "rejected"    # tarjeta rechazada, o stock perdido en la carrera del commit (D-35)


class Pedido(Base):
    """Una orden: nace PENDING al iniciar el pago (D-34) y su cara pública
    es el numero legible — el buy_order que viaja a Webpay (D-37, RN-13)."""

    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(primary_key=True)  # interno: jamás se muestra ni viaja (RN-13)
    numero: Mapped[str] = mapped_column(String(26), unique=True, index=True)  # "MAURA-000001"
    estado: Mapped[EstadoPedido] = mapped_column(
        Enum(EstadoPedido), default=EstadoPedido.pending
    )
    total: Mapped[int] = mapped_column(Integer)  # CLP entero, recalculado por el backend (CART-03)
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )  # el momento en que la orden nace (D-34) — viaja en OrdenLista del contrato
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))

    lineas: Mapped[list["LineaPedido"]] = relationship(cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Pedido {self.numero} ({self.estado.value})>"


class LineaPedido(Base):
    """Una línea de la orden: el snapshot congelado al comprar (D-36, RN-10)."""

    __tablename__ = "pedidos_lineas"

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"))
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))  # el soft delete la mantiene viva
    nombre_snapshot: Mapped[str] = mapped_column(String(120))  # lo que se compró, no lo que vale hoy
    precio_snapshot: Mapped[int] = mapped_column(Integer)  # lo que se PAGÓ — el histórico
    cantidad: Mapped[int] = mapped_column(Integer)
```

La tabla contra el diccionario de §2.2 del diseño, campo a campo: PEDIDO
(`id`, `numero` único de 26, `estado` de 4 valores, `total` entero,
`fecha`, `usuario_id` FK) y LÍNEA (`id`, `pedido_id` FK, `producto_id` FK,
`nombre_snapshot` 120, `precio_snapshot`, `cantidad`) — ni una más.

Un detalle de infraestructura: el `create_all` del seed solo crea las
tablas de los modelos que están IMPORTADOS cuando corre. En
**`backend/app/seed.py`**, agrega este import junto a los de modelos:

```python
from app.models import pedido  # noqa: F401 — registra pedidos/pedidos_lineas en el create_all
```

✅ **Mini-verificación:** desde `backend/`, ejecuta:

```
uv run python -c "from app.models.pedido import EstadoPedido, Pedido, LineaPedido; print([m.name for m in EstadoPedido]); print([c.name for c in Pedido.__table__.columns]); print([c.name for c in LineaPedido.__table__.columns])"
```

Debe imprimir `['pending', 'paid', 'cancelled', 'rejected']` y las dos
listas de columnas — compáralas con el `enum: [pending, paid, cancelled,
rejected]` de `OrdenLista` en `contrato_api.yaml` y con el diccionario de
§2.2: iguales, caracter por caracter. Después ejecuta `uv run python -m
app.seed`: los 14 `[=]` de siempre Y las dos tablas nuevas creadas —
`create_all` agrega `pedidos` y `pedidos_lineas` sin tocar las existentes
(ADR-005; sin migraciones en esta etapa).

---

## Paso 3 — `schemas/pedido.py`: el contrato 0.3.0, implementado

🧠 **El desarrollador piensa:** *igual que en las guías 4 y 5: abro
`contrato_api.yaml` 0.3.0 y escribo sus schemas en Pydantic — nada más
(D-15). Y fíjate lo que NO hay, porque es la decisión estructural de la
etapa entera: **NINGÚN schema de entrada tiene campo precio**. La nota
obligatoria que la guía 4 escribió para `hashed_password` ("no aparece:
no cruza la frontera") hoy la escribe el ausente: `CheckoutCreate` recibe
SOLO `items [{producto_id, cantidad}]` — el carro tal como vive en el
navegador (D-27, RN-08) — y el total lo calcula el servidor consultando el
catálogo (CART-03). Es la misma lección del hash, al revés: allá el
servidor tenía algo que jamás entrega; acá jamás RECIBE lo que no debe
confiarle a nadie. Aunque un cliente malicioso mande `"precio": 1` en el
JSON, Pydantic lo ignora: no hay campo que lo reciba — la regla es
estructural, no un `if`. La validación declarativa hace el resto:
`cantidad` con `ge=1` y `items` con `min_length=1` producen el 422 del
contrato sin escribir un solo `if` — como el `min_length=8` de la clave
(RN-05) en la guía 5.*

Crea **`backend/app/schemas/pedido.py`**:

```python
"""Schemas Pydantic de pedidos — espejan docs/04_arquitectura/contrato_api.yaml 0.3.0.

El contrato se aprobó ANTES que este código (API-first, ADR-007): estos
schemas lo implementan, no lo inventan. Y la nota obligatoria de la etapa:
NINGÚN schema de entrada tiene campo precio ni total — el monto lo calcula
el servidor con el precio vigente del catálogo (CART-03, D-27, RN-08).
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.pedido import EstadoPedido


class CheckoutItem(BaseModel):
    """Un par del carro tal como vive en el navegador (D-27, RN-08)."""

    producto_id: int
    cantidad: int = Field(ge=1)  # el 422 nace en la firma, como el min_length de la clave (RN-05)


class CheckoutCreate(BaseModel):
    """Lo que la SPA envía al iniciar el pago (CART-03) — sin precios, jamás."""

    items: list[CheckoutItem] = Field(min_length=1)  # un checkout sin ítems no existe


class CheckoutRespuesta(BaseModel):
    """Los tres datos del form POST hacia Webpay (PAY-01) — el numero es el
    de la orden recién nacida en pending (D-34, D-37)."""

    url: str
    token_ws: str  # el nombre EXACTO que exige Webpay en el wire
    numero: str  # "MAURA-000001" — a la vez el buy_order que viajó a la pasarela


class OrdenLinea(BaseModel):
    """Una línea congelada del pedido (D-36, RN-10)."""

    model_config = ConfigDict(from_attributes=True)  # mapear desde el ORM

    nombre_snapshot: str
    precio_snapshot: int
    cantidad: int


class OrdenLista(BaseModel):
    """Una orden tal como aparece en el historial (ORDR-01) — liviana, sin líneas."""

    model_config = ConfigDict(from_attributes=True)

    numero: str
    fecha: datetime
    total: int
    estado: EstadoPedido


class OrdenDetalle(OrdenLista):
    """La orden completa que renderizan el voucher y el detalle (D-43)."""

    lineas: list[OrdenLinea]
```

✅ **Mini-verificación:** desde `backend/`, ejecuta:

```
uv run python -c "from app.schemas.pedido import CheckoutCreate, CheckoutRespuesta, OrdenLista; print(CheckoutCreate.model_json_schema()['required'], CheckoutRespuesta.model_json_schema()['required'], OrdenLista.model_json_schema()['required'])"
```

Debe imprimir `['items']` `['url', 'token_ws', 'numero']` y
`['numero', 'fecha', 'total', 'estado']` — compáralas con las listas
`required` de `CheckoutCreate`, `CheckoutRespuesta` y `OrdenLista` en el
contrato: campo por campo. Y el experimento del precio inyectado:

```
uv run python -c "from app.schemas.pedido import CheckoutCreate; print(CheckoutCreate(items=[{'producto_id': 1, 'cantidad': 2, 'precio': 1}]).items[0])"
```

Imprime `producto_id=1 cantidad=2` — el `precio` mandado a mano
desapareció sin error: no había dónde recibirlo. CART-03 no es un chequeo:
es la forma de la entrada.

---

## Paso 4 — `repositories/pedido.py`: la muralla del stock

🧠 **El desarrollador piensa:** *dos diferencias con `UsuarioRepository`,
y las dos son la etapa. **Primera: este repositorio NO cierra sus
transacciones** — ni `crear` ni `descontar_stock_atomico` llaman a
`commit()`. ¿Por qué rompen la costumbre de la guía 5? Porque las
transacciones de la orden abarcan cosas más grandes que ella misma: la
orden nace DENTRO de una transacción que también abraza la llamada a
Webpay (si la pasarela falla, la orden se revierte sola — Pitfall 11), y el
descuento comparte transacción con la transición de estado (ADR-013: o
queda todo, o no queda nada). Quien decide cuándo cerrar es el service;
el repo ejecuta. `crear` hace `flush()` — el INSERT baja a la base, el
`id` nace, el numero se calcula — pero la transacción sigue abierta.
**Segunda: `descontar_stock_atomico` lleva la condición DENTRO del SQL.**
La tentación clásica es leer el stock, compararlo en Python y escribir
después — pero eso es `read-check-write`, y entre el check y el write vive
la carrera: dos requests leen stock=1, ambos "alcanzan", ambos escriben, y
se vendieron dos unidades de una (RN-12 lo prometía: la condición vive
dentro de la propia sentencia). El UPDATE condicional
`WHERE stock >= cantidad` con `values(stock=stock-cantidad)` es la
muralla: el motor serializa la escritura y evalúa la condición ATÓMICAMENTE
— dos threads no pueden ambos pasarla. El veredicto es el `rowcount`: 0
filas tocadas significa que el WHERE no encontró stock suficiente, y la
excepción `StockInsuficiente` sube para que el service revierta todo y
marque la orden REJECTED (D-35). Y un costo honesto que hay que saber:
`execution_options(synchronize_session=False)` deja los objetos `Producto`
de la sesión STALE (Python no puede evaluar `stock >= n` contra el identity
map) — por eso este request NO relee productos después de descontar; la
pantalla fresca llega en el siguiente (la guía 10 invalida la caché justo
para eso).*

Crea **`backend/app/repositories/pedido.py`**:

```python
"""Acceso a datos de Pedido y LineaPedido: sesión inyectada, UPDATE condicional.

Regla de la etapa: los métodos de este repositorio NO cierran la
transacción — la orden nace dentro de una transacción que también abarca
la llamada a Webpay (Pitfall 11), y el descuento comparte transacción con
la transición de estado (ADR-013). Quien decide cuándo commit/rollback es
el service.
"""

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.pedido import LineaPedido, Pedido
from app.models.producto import Producto


class StockInsuficiente(Exception):
    """Veredicto del UPDATE condicional: una línea perdió el stock (D-35).

    La lanza descontar_stock_atomico DENTRO de la transacción del commit
    aprobado — el service la traduce en orden REJECTED (la carrera de
    ORDR-02 que la mini-verificación del final provoca a propósito).
    """

    def __init__(self, producto_id: int) -> None:
        super().__init__(f"stock insuficiente para el producto {producto_id}")
        self.producto_id = producto_id


class PedidoRepository:
    """Repositorio del agregado Pedido con la sesión inyectada."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def crear(self, usuario_id: int, total: int, lineas: list[LineaPedido]) -> Pedido:
        """Inserta la orden PENDING y calcula su numero — SIN commit.

        El flush fuerza el INSERT (el id nace AHÍ) sin cerrar la
        transacción: si la llamada a Webpay que viene después falla, la
        orden se revierte sola (Pitfall 11). El numero nace del id en la
        MISMA transacción: único por construcción (D-37) — jamás
        max(id)+1 en Python, que sería una carrera con uno mismo.
        """
        pedido = Pedido(usuario_id=usuario_id, total=total)  # estado: default pending (D-34)
        pedido.lineas = lineas
        self.db.add(pedido)
        self.db.flush()  # el id nace; la transacción sigue ABIERTA
        pedido.numero = f"MAURA-{pedido.id:06d}"  # 11 chars << límite 26 de Webpay
        return pedido

    def por_numero(self, numero: str) -> Pedido | None:
        """Una orden por su numero legible — la llave pública (D-37)."""
        return self.db.scalar(select(Pedido).where(Pedido.numero == numero))

    def por_usuario(self, usuario_id: int) -> list[Pedido]:
        """TODAS las órdenes de una clienta, la más reciente primero (RN-11)."""
        return list(
            self.db.scalars(
                select(Pedido)
                .where(Pedido.usuario_id == usuario_id)
                .order_by(Pedido.id.desc())
            )
        )

    def descontar_stock_atomico(self, lineas: list[LineaPedido]) -> None:
        """El descuento del commit aprobado: la condición vive DENTRO del SQL.

        UPDATE productos SET stock = stock - cantidad
        WHERE id = ? AND stock >= cantidad

        Dos threads que leen el mismo stock NO pueden ambos "alcanzar": el
        motor serializa el UPDATE y el rowcount es el veredicto. rowcount
        0 en CUALQUIER línea → StockInsuficiente → el service revierte
        TODO y la orden queda REJECTED (D-35, ORDR-02, RN-12). SIN commit:
        la transición de estado vive en el mismo bloque (ADR-013).
        """
        for linea in lineas:
            resultado = self.db.execute(
                update(Producto)
                .where(
                    Producto.id == linea.producto_id,
                    Producto.stock >= linea.cantidad,  # la muralla anti-oversell
                )
                .values(stock=Producto.stock - linea.cantidad)
                .execution_options(synchronize_session=False)  # objetos stale: no releer
            )
            if resultado.rowcount == 0:
                # 0 filas: el WHERE no encontró stock suficiente — perdimos
                # la carrera. La excepción sube y el service revierte todo.
                raise StockInsuficiente(linea.producto_id)
```

✅ **Mini-verificación:** desde `backend/`, ejecuta:

```
uv run python -c "from app.database import SessionLocal; from app.repositories.pedido import PedidoRepository, StockInsuficiente; print(type(PedidoRepository(SessionLocal())).__name__)"
```

Debe imprimir `PedidoRepository` — la capa importa y se construye con la
sesión inyectada. La muralla del stock se prueba de verdad en la carrera
del paso 10: con datos, con threads y con un perdedor.

---

## Paso 5 — `services/webpay.py`: el único archivo que importa transbank

🧠 **El desarrollador piensa:** *un wrapper chico con una regla grande:
ESTE es el único archivo del proyecto que escribe `import transbank`.
¿Por qué aislarlo? Porque el SDK es una dependencia externa con sus
propios ritmos (versiones, errores tipados, `requests` síncrono) — y
queremos que ese ritmo se note en UN lugar, no regado por services y
routers. El wrapper habla el vocabulario del negocio (`crear` con
`buy_order`/`session_id`/`amount`/`return_url`, `commit` con el token) y
esconde los detalles del SDK. Dos de esos detalles importan hoy. **La
instancia:** en el SDK 6.x no existe el estilo clase-estática de los
ejemplos viejos de internet — se construye con
`Transaction.build_for_integration(IntegrationCommerceCodes.WEBPAY_PLUS,
IntegrationApiKeys.WEBPAY)` (las credenciales públicas del paso 1) y ESA
instancia tiene `.create` y `.commit`. **El nombre del token:** el
`create` devuelve un dict cuya clave es `"token"` — NO `"token_ws"` —
pero el `input` del formulario hacia Webpay SÍ se llama `token_ws` (es el
nombre que exige el wire). El wrapper normaliza esa rareza a la entrada:
devuelve `{"url": …, "token_ws": …}` y el resto del proyecto vive feliz
sin saberla. Y las firmas, con sus límites validados por el SDK ANTES de
llamar a la API: `buy_order` máximo 26 caracteres (tu `MAURA-000001` de
11 va sobrado), `session_id` 61, `return_url` 255, `amount` como float
(tu total CLP entero viaja como `float(total)`, sin decimales). El
`return_url` apunta al endpoint público del paso 8 — y su origen se
reutiliza de `settings.cors_origins[0]`: la misma URL de la SPA que el
CORS ya declara (la fase 5 la congelará al desplegar).*

Crea **`backend/app/services/webpay.py`**:

```python
"""El wrapper de Webpay Plus (ambiente de integración) — ÚNICO archivo que
importa transbank.

Las credenciales de integración son PÚBLICAS y viven dentro del SDK
(597055555532): sin registro en Transbank y sin .env nuevo (RNF-07). El
SDK usa requests (sync): las rutas que hablan con Webpay son `def`.
"""

from transbank.common.integration_api_keys import IntegrationApiKeys
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.webpay.webpay_plus.transaction import Transaction

tx = Transaction.build_for_integration(
    IntegrationCommerceCodes.WEBPAY_PLUS,  # "597055555532" — público, va DENTRO del SDK
    IntegrationApiKeys.WEBPAY,
)


def crear(buy_order: str, session_id: str, amount: float, return_url: str) -> dict:
    """Crea la transacción y devuelve {"url", "token_ws"} (PAY-01).

    Gotcha del SDK 6.1.0: el token del create viaja bajo la clave "token"
    — el input del formulario SÍ se llama token_ws (nombre del wire). El
    wrapper normaliza: afuera de este archivo, siempre "token_ws".
    """
    resp = tx.create(buy_order, session_id, amount, return_url)
    return {"url": resp["url"], "token_ws": resp["token"]}


def commit(token_ws: str) -> dict:
    """Confirma la transacción — el veredicto (PAY-03).

    Devuelve el dict de Webpay: response_code, status, buy_order, amount,
    authorization_code, transaction_date… Con response_code == 0 Y
    status == "AUTHORIZED" (ambos) el pago aprobó.
    """
    return tx.commit(token_ws)
```

✅ **Mini-verificación:** desde `backend/`, ejecuta:

```
uv run python -c "from app.services import webpay; print(type(webpay.tx).__name__)"
```

Debe imprimir `Transaction` — la instancia de integración construida (sin
tocar la red: construir no llama a Webpay). Y comprueba el aislamiento:
`grep -r transbank backend/app` debe listar SOLO `services/webpay.py`.

## Paso 6 — `services/pedidos.py` (ida): `iniciar_checkout` recalcula y crea la orden

🧠 **El desarrollador piensa:** *el caso de uso de la ida, y la promesa de
CART-03 hecha código. La entrada trae SOLO ids y cantidades; el servicio
hidrata cada par contra el catálogo (el mismo `ProductoRepository.obtener`
de la guía 4), recalcula cada línea con el precio VIGENTE y valida que el
stock alcance — **sin tocarlo**: la primera barrera contra la sobreventa
fue RN-09 en pantalla, esta es la segunda en backend, y la definitiva
recién llega con el commit (RN-12, ADR-013). ¿Qué pasa si no alcanza? El
servicio NO conoce HTTP: lanza `CarroNoComprable` con el mensaje — y el
router del paso 8 la traduce al 400 del contrato. Es la misma división de
la señal `None` del registro en la guía 5, ahora con excepción porque el
mensaje importa. Después, la ceremonia de D-34 EN ORDEN: primero nace la
orden PENDING con sus líneas congeladas (el repo hace flush, la
transacción sigue abierta), y SOLO DESPUÉS se llama a Webpay — si `create`
falla, la transacción de la base revierte la orden sola (Pitfall 11: jamás
un token huérfano sin orden, jamás una orden sin token). Cuando Webpay
responde, recién ahí `commit()`: la orden PENDING queda persistida con su
transacción viva esperando el retorno. ¿Y el `session_id` que viaja a
Webpay? `str(usuario.id)` — un espejo informativo: el mapeo real
token→orden lo hace el `buy_order` que el commit devuelve. Y una
honradez: si Webpay no responde (la red se cayó), la excepción del SDK
sube tal cual y el navegador verá un error genérico — la orden muere con
la transacción, que es lo que Pitfall 11 garantiza; endurecer ese camino
con reintentos no está en el contrato de esta etapa.*

Crea **`backend/app/services/pedidos.py`** — primera parte (la ida y el
historial; la vuelta llega en el paso 7):

```python
"""Casos de uso de pedidos: checkout, retorno e historial. El service NO
conoce HTTP — las señales (CarroNoComprable, None del detalle) las
traduce el router (CART-03, PAY-02, ORDR-01).
"""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.config import settings
from app.models.pedido import EstadoPedido, LineaPedido, Pedido
from app.models.usuario import Usuario
from app.repositories.pedido import PedidoRepository, StockInsuficiente
from app.repositories.producto import ProductoRepository
from app.schemas.pedido import CheckoutCreate, CheckoutRespuesta
from app.services import webpay
from transbank.error.transaction_commit_error import TransactionCommitError


class CarroNoComprable(Exception):
    """Señal de regla de negocio: el carro no puede convertirse en orden.

    La lanza iniciar_checkout (stock insuficiente o aroma desaparecido) y
    el router la traduce al 400 del contrato (CART-03) con SU mensaje.
    """

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje


class PedidosService:
    """Orquesta el ciclo de vida de la orden (D-34..D-37)."""

    def __init__(self, db: Session) -> None:
        # Recibe la SESIÓN (no un solo repo): necesita el catálogo para
        # recalcular, el repo de pedidos para persistir… y decide cuándo
        # cerrar la transacción — las fronteras son de la etapa (Pitfall 11).
        self.db = db
        self.pedidos = PedidoRepository(db)
        self.productos = ProductoRepository(db)

    # --- La ida: el checkout (CART-03, D-34, Pitfall 11) ---

    def iniciar_checkout(self, usuario: Usuario, datos: CheckoutCreate) -> CheckoutRespuesta:
        """Valida recalculando, crea la orden PENDING y la transacción — en ese orden."""
        lineas: list[LineaPedido] = []
        total = 0
        for item in datos.items:
            producto = self.productos.obtener(item.producto_id)
            if producto is None or not producto.activo:
                raise CarroNoComprable("Un aroma de tu carro ya no está disponible")
            if producto.stock < item.cantidad:  # valida SIN tocar (RN-12, D-35)
                raise CarroNoComprable(
                    f"Stock insuficiente en {producto.nombre} (quedan {producto.stock})"
                )
            total += producto.precio * item.cantidad  # precio VIGENTE (CART-03)
            lineas.append(
                LineaPedido(
                    producto_id=producto.id,
                    nombre_snapshot=producto.nombre,  # congelado (D-36, RN-10)
                    precio_snapshot=producto.precio,
                    cantidad=item.cantidad,
                )
            )

        # La orden nace PENDING (D-34) — flush SIN commit: la transacción
        # sigue abierta para abrazar la llamada a Webpay (Pitfall 11).
        pedido = self.pedidos.crear(usuario.id, total, lineas)

        # Recién AHORA la pasarela: si create falla, la orden se revierte
        # sola al cerrar la sesión sin commit.
        respuesta = webpay.crear(
            buy_order=pedido.numero,  # el numero ES el buy_order (D-37)
            session_id=str(usuario.id),  # espejo informativo — el mapeo real va por buy_order
            amount=float(total),  # CLP entero como float (RN-02)
            return_url=f"{settings.cors_origins[0]}/api/pago/retorno",
        )
        self.db.commit()  # Webpay respondió: la orden PENDING queda persistida
        return CheckoutRespuesta(
            url=respuesta["url"], token_ws=respuesta["token_ws"], numero=pedido.numero
        )

    # --- El historial (ORDR-01, D-46..D-49) ---

    def listar(self, usuario_id: int) -> list[Pedido]:
        """TODAS las órdenes de la clienta — las "en curso" incluidas (RN-11)."""
        return self.pedidos.por_usuario(usuario_id)

    def detalle(self, usuario_id: int, numero: str) -> Pedido | None:
        """La orden si existe Y es de la dueña del token — None si no (404 uniforme)."""
        pedido = self.pedidos.por_numero(numero)
        if pedido is None or pedido.usuario_id != usuario_id:
            return None  # "no existe" y "no es tuya" responden IGUAL (ORDR-01)
        return pedido
```

✅ **Mini-verificación:** desde `backend/`, ejecuta:

```
uv run python -c "from app.database import SessionLocal; from app.services.pedidos import PedidosService; print(type(PedidosService(SessionLocal())).__name__)"
```

Debe imprimir `PedidosService` — el servicio se construye sobre la sesión
inyectada. Su comportamiento completo (el recalculo, el 400, la orden
PENDING) se prueba con datos de verdad en el paso 10.

---

## Paso 7 — `services/pedidos.py` (vuelta): `procesar_retorno` discrimina los 4 flujos

🧠 **El desarrollador piensa:** *la vuelta, y el paso más cargado de
evidencia de la fase. **El discriminador va por PRESENCIA de params, jamás
por método HTTP** — y no es una opinión: el spike de retorno de la fase
corrió los flujos reales contra el ambiente de integración y el anulado
llegó por GET cuando las docs oficiales decían POST, mientras que la
presencia de parámetros fue 100% estable en los 25+ retornos observados.
La presencia es la firma; el método, un rumor. `clasificar_flujo` traduce
el orden de ramas del plugin oficial de Transbank: los 4 params juntos es
error de formulario (el form se submiteó dos veces); `TBK_ID_SESION` +
`TBK_TOKEN` sin `token_ws` es anulado; `TBK_ID_SESION` solo es timeout
(sin ningún token — por eso la orden se busca por `TBK_ORDEN_COMPRA`); y
`token_ws` solo es el flujo normal, donde aprobado y rechazado por la
tarjeta viajan IGUAL y los decide el commit. **Los flujos no-normales NO
llaman a la API** (Pitfall 3): commitear una transacción anulada revienta
con `TransactionCommitError` y un 500 al navegador — las docs oficiales
lo dicen con todas las letras: "no es necesario confirmar la
transacción". Se marca la orden CANCELLED localmente y listo, con un
guard: solo si sigue `pending` — el navegador puede REPETIR retornos (se
observaron 7 repeticiones de un mismo timeout) y un retorno tardío jamás
pisa un estado ya decidido. **En el flujo normal, tres defensas en
orden.** El `commit` envuelto en `try/except TransactionCommitError`: un
token que Webpay no puede confirmar produce una 302 con estado de error,
jamás un 500. El mapeo token→orden lo hace el `buy_order` que el commit
devuelve (por eso la orden nació ANTES del pago, D-34). Y el **guard
ya-PAID** (Pitfall 4, PAY-03): si la orden ya está pagada, se re-muestra
SIN ningún side effect — refrescar no paga dos veces; el descuento y la
transición viven en UNA sola transacción SQLAlchemy, el patrón
`checkIsAlreadyProcessed` del plugin oficial. El **criterio doble** es
literal del requisito: `response_code == 0` Y `status == "AUTHORIZED"` —
ambos, jamás solo uno (RF-15): un commit puede traer `status` con
`response_code != 0`, y ese pago NO aprobó. Si el criterio pasa, el
descuento atómico del paso 4 corre en la misma transacción que la
transición a `paid`; si pierde la carrera (`StockInsuficiente`), el
`rollback` revierte el descuento parcial y la orden queda REJECTED — la
verdad, no un voucher falso (ADR-013).*

Continúa **`backend/app/services/pedidos.py`**: agrega `RetornoResultado`
y `clasificar_flujo` entre `CarroNoComprable` y la clase…

```python
@dataclass
class RetornoResultado:
    """Lo que el retorno decidió — el router lo convierte en la 302.

    estado: "pagado" | "rechazado" | "anulado" | "timeout" | "error".
    """

    estado: str
    numero: str | None


def clasificar_flujo(
    token_ws: str | None, tbk_token: str | None, tbk_id_sesion: str | None
) -> str:
    """El discriminador de los 4 flujos por PRESENCIA de params (PAY-02, ADR-012).

    Orden verbatim del plugin oficial de Transbank — y JAMÁS por método
    HTTP: el spike de la fase corrió los flujos reales contra el ambiente
    de integración y el anulado llegó por GET cuando las docs oficiales
    decían POST; la presencia de params fue 100% estable en los 25+
    retornos observados. La presencia es la firma; el método, un rumor.
    """
    if token_ws and tbk_token:
        return "error_formulario"  # los 4 juntos: el form se submiteó dos veces
    if tbk_id_sesion and tbk_token and not token_ws:
        return "anulado"  # la clienta anuló en el formulario
    if tbk_id_sesion and not tbk_token and not token_ws:
        return "timeout"  # el formulario expiró — sin token: la orden va por TBK_ORDEN_COMPRA
    if token_ws and not tbk_token and not tbk_id_sesion:
        return "normal"  # aprobado o rechazado por la tarjeta: lo decide el commit
    return "desconocido"  # defensivo: el router responde el 400 del contrato
```

…y los tres métodos de la vuelta DENTRO de `PedidosService` (después de
`iniciar_checkout`):

```python
    # --- La vuelta: el retorno (PAY-02/PAY-03, ADR-012/013) ---

    def procesar_retorno(
        self,
        token_ws: str | None,
        tbk_token: str | None,
        tbk_id_sesion: str | None,
        tbk_orden_compra: str | None,
    ) -> RetornoResultado | None:
        """Discrimina el flujo y ejecuta su efecto — o None si es irreconocible."""
        flujo = clasificar_flujo(token_ws, tbk_token, tbk_id_sesion)
        if flujo == "error_formulario":
            return self._cancelar(tbk_orden_compra, "error")
        if flujo == "anulado":
            return self._cancelar(tbk_orden_compra, "anulado")
        if flujo == "timeout":
            # Sin ningún token: la orden se encuentra por TBK_ORDEN_COMPRA.
            return self._cancelar(tbk_orden_compra, "timeout")
        if flujo == "normal":
            return self._confirmar(token_ws)
        return None  # desconocido: el router responde el 400 defensivo

    def _cancelar(self, numero: str | None, estado: str) -> RetornoResultado:
        """Flujos no-normales: CANCELLED local, SIN llamar a la API (Pitfall 3).

        Commitear una transacción anulada revienta con
        TransactionCommitError y un 500 al navegador; las docs oficiales
        lo dicen explícito: "no es necesario confirmar la transacción".
        """
        if numero:
            pedido = self.pedidos.por_numero(numero)
            if pedido is not None and pedido.estado == EstadoPedido.pending:
                # El guard de los flujos locales: el navegador PUEDE repetir
                # retornos (se observaron 7 repeticiones de un mismo timeout)
                # y un retorno tardío jamás pisa un estado ya decidido.
                pedido.estado = EstadoPedido.cancelled
                self.db.commit()
        return RetornoResultado(estado=estado, numero=numero)

    def _confirmar(self, token_ws: str) -> RetornoResultado:
        """Flujo normal: commit, criterio doble, guard ya-PAID y stock atómico."""
        try:
            commit = webpay.commit(token_ws)
        except TransactionCommitError:
            # Un token que Webpay no puede confirmar (inventado, de una
            # transacción anulada…): 302 con estado de error, JAMÁS un 500.
            return RetornoResultado(estado="error", numero=None)
        # El commit devuelve el buy_order — así se mapea token → orden
        # (D-34): por eso la orden tuvo que nacer ANTES del pago.
        pedido = self.pedidos.por_numero(commit["buy_order"])
        if pedido is None:
            return RetornoResultado(estado="error", numero=None)

        # Guard ya-PAID (Pitfall 4, PAY-03): refrescar no paga dos veces —
        # la orden se re-muestra SIN ningún side effect (el patrón
        # checkIsAlreadyProcessed del plugin oficial).
        if pedido.estado == EstadoPedido.paid:
            return RetornoResultado(estado="pagado", numero=pedido.numero)

        # Criterio doble de PAY-03 — AMBOS, jamás solo uno: un commit puede
        # traer status con response_code != 0, y ese pago NO aprobó.
        aprobado = commit["response_code"] == 0 and commit["status"] == "AUTHORIZED"
        if not aprobado:
            pedido.estado = EstadoPedido.rejected
            self.db.commit()
            return RetornoResultado(estado="rechazado", numero=pedido.numero)

        try:
            # Descuento + transición en UNA sola transacción (ADR-013):
            # o queda todo, o no queda nada.
            self.pedidos.descontar_stock_atomico(pedido.lineas)
        except StockInsuficiente:
            self.db.rollback()  # revierte el descuento parcial de las líneas que sí alcanzaron
            pedido.estado = EstadoPedido.rejected
            self.db.commit()
            return RetornoResultado(estado="rechazado", numero=pedido.numero)
        pedido.estado = EstadoPedido.paid
        self.db.commit()
        return RetornoResultado(estado="pagado", numero=pedido.numero)
```

✅ **Mini-verificación (el discriminador, en tu máquina):** desde
`backend/`, ejecuta:

```
uv run python -c "from app.services.pedidos import clasificar_flujo as f; print(f('t', None, None), f(None, 't', 's'), f(None, None, 's'), f('t', 't', 's'), f('t', None, 's'))"
```

Debe imprimir `normal anulado timeout error_formulario desconocido` — las
cinco combinaciones de la tabla de flujos de ADR-012, decididas SOLO por
la presencia de los params. La última (`token_ws` + `TBK_ID_SESION` sin
`TBK_TOKEN`) no es flujo de nadie: por eso existe el 400 defensivo del
contrato.

---

## Paso 8 — Los routers: checkout con Bearer, retorno GET+POST con 302, pedidos con 404 uniforme

🧠 **El desarrollador piensa:** *la frontera HTTP, y hoy con DOS novedades
que ninguna guía anterior tenía. **La primera: un endpoint que responde a
una navegación, no a un fetch.** `/api/pago/retorno` es PÚBLICO por diseño
(ADR-012): quien llega es el navegador de la clienta recién salido del
formulario de Webpay, SIN Bearer — ponerle candado sería exigirle una
sesión a un navegador que viene de otra parte; la sesión se retoma
DESPUÉS en la SPA. Por eso el contrato lo declara `security: []`, en
contraste deliberado con sus vecinos. El endpoint se declara **GET y
POST** leyendo query Y body form-encoded (`Form(default=None)` — la misma
pieza `python-multipart` que parsea el form del login de la guía 5), y su
respuesta es una **redirección con 302 EXPLÍCITO**: `RedirectResponse(url)`
sin `status_code` responde 307, que preserva método+body — si el retorno
llegó por POST, la "redirección" re-POSTearía el form de Webpay contra la
ruta de la SPA, que no tiene handler POST, y la pantalla revienta. El 302
fuerza el GET del navegador: la primera lección PRG
(Post/Redirect/Get) del proyecto (Pitfall 1). **La segunda novedad: el
302 en las `responses` de la firma.** La lección G-01-4 (declarar el 404
en la guía 4, el 409 en la guía 5) ahora aplica a un código que no es
JSON: sin `responses={302: …}`, `/docs` no lo lista y la fila contrato ↔
`/docs` del cierre acusaría un desvío que no existe (Pitfall 13). Todos
los routers nuevos declaran SUS códigos: el checkout 400/401/422, el
retorno 302/400 en AMBOS métodos, pedidos 401 y el 404 uniforme — el que
responde IGUAL para "no existe" y "no es tuya", porque un numero
secuencial legible sería enumerable de otra forma. Y las rutas son `def`
(sync): el SDK de Webpay usa `requests`.*

Crea **`backend/app/routers/checkout.py`**:

```python
"""POST /api/checkout — iniciar el pago (implementa contrato_api.yaml 0.3.0).

La señal de regla de negocio del service (CarroNoComprable) se traduce al
400 del contrato EN ESTA frontera: el service no conoce HTTP.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_session
from app.models.usuario import Usuario
from app.schemas.pedido import CheckoutCreate, CheckoutRespuesta
from app.schemas.producto import Error  # el cuerpo de error vive en schemas/producto desde la guía 4
from app.security import get_current_user
from app.services.pedidos import CarroNoComprable, PedidosService

router = APIRouter(tags=["Pago"])


@router.post(
    "",
    response_model=CheckoutRespuesta,
    status_code=status.HTTP_201_CREATED,  # creado: la orden PENDING nace aquí (D-34)
    responses={
        400: {
            "description": "Stock insuficiente o aroma no disponible — regla de negocio (CART-03); la orden no se crea",
            "model": Error,
        },
        401: {"description": "Sin sesión, o token inválido/expirado", "model": Error},
        422: {
            "description": "Cuerpo mal formado (items vacío, cantidad menor a 1) — validación declarativa",
            "model": Error,
        },
    },
)
def checkout(
    datos: CheckoutCreate,
    actual: Usuario = Depends(get_current_user),  # la dueña sale del token, jamás del cuerpo
    db: Session = Depends(get_session),
) -> CheckoutRespuesta:
    """POST /api/checkout — valida el carro, crea la orden PENDING y el form de Webpay (PAY-01)."""
    try:
        return PedidosService(db).iniciar_checkout(actual, datos)
    except CarroNoComprable as exc:
        # El service habla dominio; el 400 con SU mensaje habla contrato.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.mensaje)
```

Crea **`backend/app/routers/retorno.py`**:

```python
"""GET+POST /api/pago/retorno — la vuelta del navegador desde Webpay (PAY-02).

Endpoint PÚBLICO por diseño (ADR-012): quien llega es el navegador de la
clienta recién salido del formulario de Webpay, SIN Bearer. Responde
SIEMPRE un 302 explícito (no el 307 default) hacia la ruta única de
resultado de la SPA: el 307 preservaría método+body y re-POSTearía el
form de Webpay contra la SPA (Pitfall 1).
"""

from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_session
from app.schemas.producto import Error  # el cuerpo de error vive en schemas/producto desde la guía 4
from app.services.pedidos import PedidosService, RetornoResultado

router = APIRouter(tags=["Pago"])

RESPUESTAS_RETORNO = {
    302: {
        "description": "Redirección del navegador a /pago/resultado con el resultado como query params (D-42) — el primer response no-JSON de la API",
    },
    400: {
        "description": "Retorno de Webpay irreconocible (params que no calzan con ningún flujo) — defensivo",
        "model": Error,
    },
}


def _hacia_spa(resultado: RetornoResultado) -> RedirectResponse:
    """El 302 explícito hacia la ruta única de la SPA (D-41/D-42).

    El origen de la SPA se reutiliza de cors_origins[0]: la misma URL que
    el CORS ya declara (la fase 5 la congelará al desplegar).
    """
    params = {"estado": resultado.estado}
    if resultado.numero:
        params["orden"] = resultado.numero
    url = f"{settings.cors_origins[0]}/pago/resultado?{urlencode(params)}"
    return RedirectResponse(url, status_code=302)  # 302 EXPLÍCITO — jamás el 307 default


def _procesar(
    token_ws: str | None,
    tbk_token: str | None,
    tbk_id_sesion: str | None,
    tbk_orden_compra: str | None,
    db: Session,
) -> RedirectResponse:
    resultado = PedidosService(db).procesar_retorno(
        token_ws, tbk_token, tbk_id_sesion, tbk_orden_compra
    )
    if resultado is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Retorno de Webpay irreconocible",
        )
    return _hacia_spa(resultado)


@router.get("/retorno", responses=RESPUESTAS_RETORNO)
def retorno_get(
    request: Request, db: Session = Depends(get_session)
) -> RedirectResponse:
    """GET /api/pago/retorno — el retorno que llega por query (flujo normal)."""
    q = request.query_params
    return _procesar(
        q.get("token_ws"),
        q.get("TBK_TOKEN"),
        q.get("TBK_ID_SESION"),
        q.get("TBK_ORDEN_COMPRA"),
        db,
    )


@router.post("/retorno", responses=RESPUESTAS_RETORNO)
def retorno_post(
    token_ws: str | None = Form(default=None),
    TBK_TOKEN: str | None = Form(default=None),  # nombre LITERAL de Transbank
    TBK_ID_SESION: str | None = Form(default=None),
    TBK_ORDEN_COMPRA: str | None = Form(default=None),
    db: Session = Depends(get_session),
) -> RedirectResponse:
    """POST /api/pago/retorno — el retorno que llega form-encoded (python-multipart)."""
    return _procesar(token_ws, TBK_TOKEN, TBK_ID_SESION, TBK_ORDEN_COMPRA, db)
```

Y crea **`backend/app/routers/pedidos.py`**:

```python
"""GET /api/pedidos y /api/pedidos/{numero} — el historial (ORDR-01).

El 404 es uniforme a propósito: cubre el pedido que NO existe y el que
existe pero NO es de la clienta — ownership sin revelar existencia.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_session
from app.models.usuario import Usuario
from app.schemas.pedido import OrdenDetalle, OrdenLista
from app.schemas.producto import Error
from app.security import get_current_user
from app.services.pedidos import PedidosService

router = APIRouter(tags=["Pedidos"])


@router.get(
    "",
    response_model=list[OrdenLista],
    responses={401: {"description": "Sin sesión, o token inválido/expirado", "model": Error}},
)
def listar(
    actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> list[OrdenLista]:
    """GET /api/pedidos — TODAS las órdenes de la dueña del token, pendientes incluidas (RN-11)."""
    return PedidosService(db).listar(actual.id)


@router.get(
    "/{numero}",
    response_model=OrdenDetalle,
    responses={
        401: {"description": "Sin sesión, o token inválido/expirado", "model": Error},
        404: {
            "description": "Pedido inexistente — o existente pero de otra clienta (uniforme a propósito)",
            "model": Error,
        },
    },
)
def detalle(
    numero: str,
    actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> OrdenDetalle:
    """GET /api/pedidos/{numero} — el detalle que renderiza el voucher (D-43)."""
    pedido = PedidosService(db).detalle(actual.id, numero)
    if pedido is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado"
        )
    return pedido
```

✅ **Mini-verificación:** los tres archivos importan limpios — desde
`backend/`, ejecuta:

```
uv run python -c "from app.routers import checkout, pedidos, retorno; print([r.tags[0] for r in (checkout.router, retorno.router, pedidos.router)])"
```

Debe imprimir `['Pago', 'Pago', 'Pedidos']` — los tags nuevos del contrato
0.3.0. (La comparación completa contra `/docs` llega en el paso
siguiente, cuando los registres en `main.py`.)

---

## Paso 9 — `main.py`: tres routers nuevos, la versión 0.3.0… y el CORS que NO cambia

🧠 **El desarrollador piensa:** *la composición de siempre — solo
`include_router` — más dos detalles que son decisiones, no omisiones.
**La versión sube a 0.3.0**: el título de `/docs` muestra la versión que
la app declara de sí misma, y hoy implementas el contrato 0.3.0 — una app
que implementa 0.3.0 presentándose como 0.2.0 es un desvío que la fila
contrato ↔ `/docs` del cierre detectaría (la misma coherencia que la
guía 5 exigió con 0.2.0, ADR-007). **Y el CORS NO cambia** — ninguna
línea. La tentación de "agregar Webpay al CORS" confunde dos mundos: el
CORS gobierna las lecturas de script cross-origin (los `fetch` de tu
SPA), y el retorno de Webpay es una NAVEGACIÓN de formulario del
navegador, no un fetch — CORS jamás aplicó a navegaciones clásicas
(Pitfall 10). Ni `webpay3gint.transbank.cl` en `allow_origins` ni
comodines nuevos: la lista queda `["GET", "POST"]` para los orígenes de
siempre. La regla 5 de las dependencias gana su primera excepción
narrada: todo el HTTP del frontend sale de `lib/api.ts`… excepto esta
navegación, que no es HTTP de la SPA sino del navegador mismo.*

En **`backend/app/main.py`**, extiende el import de routers:

```python
from app.routers import admin, auth, checkout, pedidos, productos, retorno, salud
```

…los registros junto a los existentes, al final del archivo:

```python
app.include_router(salud.router, prefix="/api/salud")
app.include_router(productos.router, prefix="/api/productos")
app.include_router(auth.router, prefix="/api/auth")
app.include_router(admin.router, prefix="/api/admin")
app.include_router(checkout.router, prefix="/api/checkout")
app.include_router(retorno.router, prefix="/api/pago")
app.include_router(pedidos.router, prefix="/api/pedidos")
```

…y en el `FastAPI(...)`, sube la versión que la app declara de sí misma:

```python
version="0.3.0"  # la del contrato que implementas (ADR-007: panel y contrato dicen lo mismo)
```

✅ **Mini-verificación:** enciende la API (`uv run fastapi dev app/main.py`
desde `backend/`) y abre **http://localhost:8000/docs**:

1. El título dice **Maura API 0.3.0** — la versión del contrato nueva.
2. Aparecen los tags **Pago** y **Pedidos**: `POST /api/checkout`,
   `GET+POST /api/pago/retorno`, `GET /api/pedidos` y
   `GET /api/pedidos/{numero}` — los 4 paths nuevos del contrato 0.3.0.
3. Despliega `GET /api/pago/retorno`: lista **302** y **400** con sus
   descripciones — y el POST lista LOS MISMOS (la lección G-01-4, ahora
   con el response no-JSON).
4. `POST /api/checkout` lista **201**, **400**, **401** y **422**;
   `GET /api/pedidos/{numero}` lista **200**, **401** y **404**. Los
   candados 🔒 van donde corresponde: checkout y pedidos con bearerAuth —
   el retorno SIN candado, público por diseño.

---

## Paso 10 — La prueba de fuego: PENDING de verdad, 302 que nunca revienta, la carrera y el 404

🧠 **El desarrollador piensa:** *cuatro verificaciones que entre ambas
recorren el contrato entero. La primera crea una orden PENDING REAL — con
transacción REAL en Webpay integración (el `create` sí llama a la
pasarela; nadie paga nada todavía). La segunda golpea el retorno con un
token INVENTADO: el commit de Webpay lo rechazará, el `try/except` tipado
lo atrapará y la respuesta será una 302 con `estado=error` — jamás un
500. La tercera es la carrera de stock: dos `POST /api/checkout`
concurrentes contra la última unidad crean DOS órdenes PENDING (validar
no reserva — la primera mitad de la lección), y dos threads ejecutando el
bloque del retorno aprobado — el MISMO `descontar_stock_atomico` de la
paso 4, sin Webpay en el medio porque el commit "ya aprobó" cuando ese
código corre en la app real — terminan en exactamente un PAID y un
REJECTED con stock 0 (la segunda mitad). Y la cuarta prueba el 404
uniforme: el admin pregunta por el pedido de la clienta y el sistema le
dice "no encontrado" — porque para él, no lo es.*

Con la API encendida y el seed corrido. Los cuatro golpes, en orden:

✅ **Mini-verificación (la orden nace PENDING con transacción real):**
desde `backend/`, ejecuta (una línea — las credenciales salen del propio
`Settings`):

```
uv run python -c "import httpx; from app.config import settings; token = httpx.post('http://localhost:8000/api/auth/login', data={'username': settings.cliente_email, 'password': settings.cliente_password}).json()['access_token']; r = httpx.post('http://localhost:8000/api/checkout', headers={'Authorization': f'Bearer {token}'}, json={'items': [{'producto_id': 1, 'cantidad': 1}]}); print(r.status_code, r.json())"
```

Debe imprimir `201` con un dict de tres campos: `url` apuntando a
`https://webpay3gint.transbank.cl/...` (el formulario hosted REAL, recién
creado para ti), `token_ws` de 64 caracteres y `numero` =
**`MAURA-000001`**. Y en la base, la orden nació pending:

```
uv run python -c "from sqlalchemy import select; from app.database import SessionLocal; from app.models.pedido import Pedido; print(SessionLocal().scalars(select(Pedido)).all())"
```

Debe imprimir `[<Pedido MAURA-000001 (pending)>]` — la orden existe,
espera el retorno, y el historial la mostrará "en curso" (RN-11). Un
segundo checkout respondería `201` con `MAURA-000002`: el numero nace del
autoincrement, único por construcción.

✅ **Mini-verificación (el retorno que JAMÁS revienta):** simula el
retorno del navegador con un token inventado:

```
uv run python -c "import httpx; r = httpx.get('http://localhost:8000/api/pago/retorno', params={'token_ws': 'token-inventado-que-webpay-no-conoce'}, follow_redirects=False); print(r.status_code, r.headers.get('location'))"
```

Debe imprimir `302` y
`http://localhost:5173/pago/resultado?estado=error` — Webpay rechazó el
commit, el `except TransactionCommitError` lo convirtió en la redirección
de error, y el navegador jamás vio un 500 (Pitfall 3). Fíjate en el
`follow_redirects=False`: httpx sigue redirecciones solo si se lo pides —
acá quieres VER la 302, no seguirla.

✅ **Mini-verificación (la carrera de stock — ORDR-02 en tu máquina):**
crea **`backend/carrera.py`** (script desechable de verificación, no parte
de la app):

```python
"""La carrera de stock de ORDR-02, provocada a propósito (guía 9).

Dos checkouts concurrentes crean DOS órdenes PENDING para la última
unidad — validar no reserva el stock (D-35). Luego dos threads ejecutan
el bloque del retorno aprobado (el MISMO descuento atómico de
PedidoRepository que corre cuando el criterio doble de Webpay aprueba):
solo una gana.

Uso (con la API encendida en el puerto 8000):  uv run python carrera.py
"""

from concurrent.futures import ThreadPoolExecutor

import httpx
from sqlalchemy import select

from app.config import settings
from app.database import SessionLocal
from app.models.pedido import EstadoPedido, Pedido
from app.models.producto import Producto
from app.repositories.pedido import PedidoRepository, StockInsuficiente

API = "http://localhost:8000"
PRODUCTO_ID = 1


def login() -> str:
    r = httpx.post(
        f"{API}/api/auth/login",
        data={"username": settings.cliente_email, "password": settings.cliente_password},
    )
    return r.json()["access_token"]


def checkout(token: str) -> str:
    """POST /api/checkout con la última unidad → el numero de la orden PENDING."""
    r = httpx.post(
        f"{API}/api/checkout",
        headers={"Authorization": f"Bearer {token}"},
        json={"items": [{"producto_id": PRODUCTO_ID, "cantidad": 1}]},
    )
    return r.json()["numero"]


def aprobar(numero: str) -> str:
    """El bloque del retorno aprobado (services/pedidos.py), sin Webpay.

    En la app real este código corre DESPUÉS de que el commit de la
    pasarela aprobó; acá lo ejercemos directo para ver la carrera con dos
    threads — la muralla es la misma: el UPDATE condicional.
    """
    with SessionLocal() as sesion:
        repo = PedidoRepository(sesion)
        pedido = repo.por_numero(numero)
        if pedido.estado != EstadoPedido.pending:
            return f"{numero}: ya {pedido.estado.value} (guard, sin side effects)"
        try:
            repo.descontar_stock_atomico(pedido.lineas)
        except StockInsuficiente:
            sesion.rollback()  # revierte el descuento parcial
            pedido.estado = EstadoPedido.rejected
            sesion.commit()
            return f"{numero}: REJECTED (perdió la carrera)"
        pedido.estado = EstadoPedido.paid
        sesion.commit()
        return f"{numero}: PAID (stock descontado)"


def main() -> None:
    # 1) La última unidad: stock=1 en el producto de prueba.
    with SessionLocal() as sesion:
        producto = sesion.get(Producto, PRODUCTO_ID)
        producto.stock = 1
        sesion.commit()
        print(f"stock inicial de {producto.nombre!r}: 1")

    token = login()

    # 2) DOS checkouts concurrentes → dos órdenes PENDING (validar no reserva).
    with ThreadPoolExecutor(max_workers=2) as pool:
        numeros = list(pool.map(checkout, [token, token]))
    print("checkouts:", numeros)

    # 3) La carrera: dos threads ejecutan el descuento atómico a la vez.
    with ThreadPoolExecutor(max_workers=2) as pool:
        for linea in pool.map(aprobar, numeros):
            print(linea)

    # 4) El veredicto: exactamente un PAID, un REJECTED y stock 0.
    with SessionLocal() as sesion:
        stock = sesion.get(Producto, PRODUCTO_ID).stock
        ordenes = [repr(p) for p in sesion.scalars(select(Pedido)).all()]
    print("stock final:", stock)
    print("ordenes:", ordenes)


if __name__ == "__main__":
    main()
```

Ejecuta `uv run python carrera.py`. La salida debe contar la historia
completa:

```
stock inicial de 'Brisa de Naranja': 1
checkouts: ['MAURA-000002', 'MAURA-000003']
MAURA-000002: PAID (stock descontado)
MAURA-000003: REJECTED (perdió la carrera)
stock final: 0
ordenes: ['<Pedido MAURA-000001 (pending)>', '<Pedido MAURA-000002 (paid)>', '<Pedido MAURA-000003 (rejected)>']
```

(qué orden gana varía entre corridas — LO QUE NO VARÍA es la cuenta:
exactamente un PAID, un REJECTED y stock 0. Con el read-check-write de
Python, ambos habrían "alcanzado" y el stock quedaría en -1: el oversell
que RN-12 prohíbe). Re-ejecuta el seed para restaurar el stock del
catálogo antes de seguir.

✅ **Mini-verificación (el 404 uniforme de ownership):** el admin pregunta
por el pedido de la clienta:

```
uv run python -c "import httpx; from app.config import settings; t = httpx.post('http://localhost:8000/api/auth/login', data={'username': settings.admin_email, 'password': settings.admin_password}).json()['access_token']; r = httpx.get('http://localhost:8000/api/pedidos/MAURA-000001', headers={'Authorization': f'Bearer {t}'}); print(r.status_code, r.json()); r2 = httpx.get('http://localhost:8000/api/pedidos', headers={'Authorization': f'Bearer {t}'}); print(r2.status_code, r2.json())"
```

Debe imprimir `404 {'detail': 'Pedido no encontrado'}` — el pedido EXISTE,
pero no es del admin, y la respuesta es idéntica a la de un numero
inventado: ownership sin revelar existencia (ORDR-01). Y `200 []` — la
lista del admin está vacía porque el filtro por dueña lo hace el
servidor. Ahora con el token de la CLIENTA (cambia las cuatro variables
por las de `cliente`): `200` con el detalle completo de `MAURA-000001`
incluyendo sus `lineas` con `nombre_snapshot` y `precio_snapshot` (D-43)
— y la lista con TODAS sus órdenes, la pending "en curso" primero.

**Las llaves del sandbox (para cuando pagues de verdad, en la guía 10):**

```text
Tarjeta de éxito (integración):  VISA 4051 8856 0044 6623 — CVV 123 —
  vencimiento: cualquiera superior a la fecha actual.
  Autenticación bancaria (3DS): RUT 11.111.111-1 (CON puntos) — clave 123.

Compra anulada: con cualquier pago iniciado, el botón "Anular compra y
  volver" del propio formulario de Webpay produce el flujo anulado.
Pago rechazado: en la segunda página del 3DS, cambiar el select de
  Aceptar (TSY) a Rechazar (TSN) — el pago SIGUE el flujo normal y el
  commit devuelve response_code -1: el camino reproducible a REJECTED.
Timeout del formulario: ~10 minutos (cronometrado: 603 s) con la pestaña
  ACTIVA — si el tab duerme en background, el retorno puede no llegar
  nunca y la orden queda "en curso" (RN-11).
```

---

## ❌ El error que este archivo evita

**1. Commitear un flujo anulado (o timeout, o error de formulario).**

```python
# ❌ La API rechaza el commit de una transacción sin autorización:
# TransactionCommitError → la 302 nunca sale → el navegador ve un 500
commit = webpay.commit(tbk_token)  # el token del flujo anulado

# ✅ El commit va SOLO en la rama token_ws-solo; los demás flujos
# marcan la orden CANCELLED localmente y redirigen (Pitfall 3)
if flujo == "normal":
    commit = webpay.commit(token_ws)
else:
    self._cancelar(tbk_orden_compra, ...)
```

Las docs oficiales lo dicen explícito: "no es necesario confirmar la
transacción" anulada. El síntoma es inconfundible: un 500 crudo al volver
de anular, con la clienta mirando una pantalla rota.

**2. El stock leído en Python (el falso atómico).**

```python
# ❌ read-check-write: dos threads leen stock=1, ambos pasan el if,
# ambos escriben — se vendieron dos unidades de una
producto = repo.obtener(linea.producto_id)
if producto.stock >= linea.cantidad:
    producto.stock -= linea.cantidad

# ✅ la condición vive DENTRO del UPDATE y el rowcount es el veredicto
resultado = sesion.execute(
    update(Producto)
    .where(Producto.id == linea.producto_id, Producto.stock >= linea.cantidad)
    .values(stock=Producto.stock - linea.cantidad)
)
if resultado.rowcount == 0:
    raise StockInsuficiente(linea.producto_id)
```

Entre el check y el write vive la carrera (RN-12). La mini-verificación
del paso 10 lo demuestra: con la versión ❌, la carrera termina con stock
-1 y DOS pagadas.

**3. `RedirectResponse(url)` sin `status_code` (el 307 que re-POSTea).**

```python
# ❌ 307 por defecto: preserva método+body — si el retorno llegó por
# POST, el navegador re-POSTea el form de Webpay contra la SPA
return RedirectResponse(url)

# ✅ 302 explícito: fuerza el GET del navegador (PRG, Pitfall 1)
return RedirectResponse(url, status_code=302)
```

El síntoma aparece justo donde no lo buscas: el flujo aprobado (GET)
funciona perfecto… y el anulado revienta la pantalla de resultado.

**4. El enum del estado en mayúsculas (tercera vuelta del gotcha).**

```python
# ❌ La BD guardaría "PENDING": SQLAlchemy persiste los NOMBRES
class EstadoPedido(str, enum.Enum):
    PENDING = "pending"

# ✅ nombre == valor: la BD guarda el slug del contrato
class EstadoPedido(str, enum.Enum):
    pending = "pending"
```

La versión ❌ compila, siembra y parece funcionar — hasta que el badge del
historial muestra "PENDING" y el enum `[pending, paid, cancelled,
rejected]` del contrato diverge. Ya pasó con las familias (guía 3) y los
roles (guía 5): tercera vuelta, misma cura.

**5. El id interno como buy_order.**

```python
# ❌ el id de la BD viajando a Webpay: enumerable, sin formato y sin
# la unicidad garantizada que el buy_order exige
buy_order=str(pedido.id)

# ✅ el numero legible nace del id en la misma transacción (D-37)
pedido.numero = f"MAURA-{pedido.id:06d}"
```

El numero legible sirve de llave única en los tres mundos a la vez —
base de datos, Webpay y pantalla — y el `id` interno jamás se muestra ni
viaja (RN-13).

---

## ✅ Verificación de la guía 9

Desde `backend/`, con la API encendida y el seed corrido:

1. `uv run python -m app.seed` → los 14 `[=]` de siempre; las tablas
   `pedidos` y `pedidos_lineas` nacieron con el `create_all` (ADR-005).
2. **http://localhost:8000/docs** dice **0.3.0** y lista los 4 paths
   nuevos con SUS códigos: checkout 201/400/401/422, retorno GET y POST
   con 302/400, pedidos 200/401 y 200/401/404 — el retorno SIN candado,
   público por diseño (ADR-012).
3. El experimento del precio inyectado del paso 3: `"precio": 1` en el
   JSON desaparece sin error — CART-03 es la forma de la entrada.
4. El discriminador del paso 7 imprime las cinco combinaciones —
   `normal anulado timeout error_formulario desconocido`.
5. El checkout de la clienta → `201` con `{url, token_ws, numero}` y la
   orden `<Pedido MAURA-000001 (pending)>` en la base (D-34).
6. El retorno con token inventado → `302` a
   `/pago/resultado?estado=error` — jamás un 500 (Pitfall 3).
7. `uv run python carrera.py` → exactamente un PAID, un REJECTED y stock
   0 — el oversell evitado en tu propia máquina (ORDR-02, RN-12).
8. El detalle del pedido de la clienta con el token del admin → `404`
   uniforme; con el de la clienta → `200` con las líneas snapshot (D-43).

(La comparación completa contrato 0.3.0 ↔ `/docs` — los 11 paths, tags y
schemas — es la Gran verificación final de la guía 11, como en cada fase.)

## 📝 Punto de control (respóndelas sin mirar la guía)

1. ¿Por qué la orden nace ANTES de llamar a Webpay, y qué le pasaría al
   retorno si naciera después? Nombra la pieza exacta del commit que
   necesita ese orden (Pitfall 11, D-34).
2. Dos clientas pagan a la vez la última unidad: recorre la carrera paso
   a paso — ¿qué ve cada una, quién decide, y por qué el `WHERE stock >=
   cantidad` del UPDATE es la muralla y no el `if` de Python?
3. La clienta refresca la pantalla de resultado tres veces después de
   pagar: ¿qué guarda evita el segundo descuento, en qué rama vive, y por
   qué el commit de Webpay ser idempotente NO le quita el trabajo a ese
   guard? (Pitfall 4, PAY-03.)
4. ¿Por qué el endpoint del retorno no lleva candado de sesión si el
   checkout y los pedidos sí? ¿Y por qué su respuesta es un 302 explícito
   y no la redirección por defecto de `RedirectResponse`?

## Lo que acabas de aprender

- `transbank-sdk` con `Transaction.build_for_integration(...)`: credenciales PÚBLICAS de integración dentro del SDK (597055555532 — sin registro, sin `.env` nuevo, RNF-07), rutas `def` porque el SDK usa `requests`
- `services/webpay.py` como ÚNICO importador de transbank — y el gotcha del SDK: el token del `create` viaja como `"token"`, el input del form como `token_ws`
- `EstadoPedido` con nombre == valor (tercera vuelta del gotcha: familias → roles → estados) y el modelo con snapshot `nombre_snapshot`/`precio_snapshot` — la asimetría con RN-08 hecha columnas (D-36, ADR-014)
- El numero legible `MAURA-{id:06d}` nacido del autoincrement en la misma transacción: único por construcción, 11 chars bajo el límite 26, a la vez buy_order e identificador público (D-37, RN-13)
- `iniciar_checkout` que recalcula con precio vigente desde ids+cantidades (la entrada no tiene precio — CART-03 estructural), valida stock sin tocarlo (400) y SOLO DESPUÉS llama a Webpay (D-34, Pitfall 11)
- El discriminador de los 4 flujos por PRESENCIA de params en el orden del plugin oficial — jamás por método HTTP (ADR-012); commit solo en la rama `token_ws`-solo, `TransactionCommitError` atrapado → 302, nunca 500 (Pitfall 3)
- El guard ya-PAID sin side effects + el criterio doble `response_code == 0` Y `status == AUTHORIZED` + descuento y transición en UNA transacción (PAY-03, Pitfall 4, ADR-013)
- El UPDATE condicional `WHERE stock >= cantidad` con `rowcount` como veredicto — y la carrera de la mini-verificación: un PAID, un REJECTED, stock 0 (ORDR-02, RN-12)
- El retorno GET+POST con `Form(default=None)` (la pieza del login, fase 2) y `RedirectResponse(url, status_code=302)` — la primera lección PRG del proyecto (Pitfall 1)
- Las `responses` con el 302 declarado en ambos métodos: la lección G-01-4 con el primer response no-JSON (Pitfall 13)
- El 404 uniforme de ownership en pedidos y el CORS que NO cambia: el retorno es navegación, no fetch (Pitfall 10)

**Siguiente:** guia-10-retorno-voucher.md — la vuelta a la SPA: encender
el CTA "Pagar con Webpay" con el form POST auto-submit, la ruta pública
`/pago/resultado` que recibe el 302… y tu primer pago real de ida y
vuelta con la tarjeta de prueba.
