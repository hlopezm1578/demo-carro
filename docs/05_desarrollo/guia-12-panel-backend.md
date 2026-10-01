# Guía 12 — El panel (backend): CRUD con soft delete, la transición 409 y las métricas

> **Qué construirás hoy:** el backend de la trastienda: la dueña escribe el
> catálogo por primera vez (crear, editar, desactivar/reactivar), anula los
> pedidos en curso que la fase 3 dejó huérfanos y ve su negocio en números —
> todo detrás de `get_current_admin`, el guard por rol que existe desde la
> guía 5.
> **Al terminar tendrás:** el CRUD real de administración respondiendo 403 a
> una clienta con sesión válida, la huérfana PENDING anulada con su 409 a la
> segunda intención, y las métricas de tus órdenes reales de fase 3 — todo
> implementando el contrato 0.4.0 sin desviarse (D-15, ADR-007).
> **Necesitas:** las guías 1 a 11 completas — el backend en capas con el pago
> de Webpay funcionando (contrato 0.3.0 vivo en `/docs`), el seed corrido y,
> a mano, `docs/04_arquitectura/contrato_api.yaml` 0.4.0 y los ADRs 015-016:
> hoy son la vara que mide cada paso. No se instala NADA: todo el stack ya
> está — el único paquete nuevo de la fase (el SDK de Gemini) llega con la
> guía 14.

---

## Los términos de hoy (antes de copiar nada)

| Término | Qué es, en una frase |
|---|---|
| **Guard por rol** | La dependencia `get_current_admin` que valida el claim de rol EN EL SERVIDOR: token válido sin rol admin → 403 (existe desde la guía 5; hoy protege TODO un panel, ADR-015) |
| **Soft delete** | Desactivar en vez de borrar: el producto desaparece del catálogo público pero su fila vive — los pedidos viejos conservan su snapshot (D-52, §2.3.5 del diseño) |
| **Stock bajo vs últimas unidades** | DOS umbrales distintos: el del panel (≤ 5 activos, reabastecimiento, constante del backend — RN-14) y el de la tienda (1-3, urgencia de compra) — dos constantes, dos textos, dos preguntas |
| **KPI** | Key Performance Indicator: el número que resume el negocio — ingresos, pedidos por estado, top 5, stock bajo (D-54) |
| **Allow-list** | La lista CERRADA de campos que un cuerpo de entrada puede escribir: lo que el schema no tiene, el mass assignment no puede voltear |
| **Transición de estado** | Mover un pedido de un estado a otro de la máquina — cada transición tiene dueño, y la dueña posee exactamente UNA: PENDING → CANCELLED (D-50, ADR-016) |
| **Last-write-wins** | "La última escritura gana": dos admins editando el mismo producto a la vez no corrompen datos — cada escritura es un UPDATE completo por id en una transacción, y la última queda |

---

## Paso 1 — La retirada del demo: `/api/admin/estado` se va con honors

🧠 **El desarrollador piensa:** *esta guía empieza con un funeral chico. El
endpoint `/api/admin/estado` nació en la guía 5 con un solo trabajo: hacer
VERIFICABLE el 403 por rol (D-33) — un demo que reusaba el catálogo sin
escribir una línea nueva de SQL. Cumplió su lección a cabalidad: dos fases
enteras lo usaron para probar el botón Authorize de `/docs` con las cuentas
del seed. Hoy la administración de verdad toma su puesto (D-54): siete paths
que crean, editan, transicionan y agregan — y el demo se RETIRA del
contrato 0.4.0. ¿Por qué retirarlo y no dejarlo de adorno? Porque un
endpoint que nadie usa es una promesa que nadie mantiene: el contrato es
la lista de lo que la API se compromete a servir, y el demo ya no representa
nada. ¿Y las guías 5 y 6 que lo construyeron? NO se re-editan — jamás: la
historia del contrato es la historia de la tienda, y el alumno que empieza
en la guía 5 construye el demo tal como se construyó, con su lección
intacta. La evolución se narra AQUÍ y en la `description` del propio
contrato 0.4.0 — el mismo criterio de las fases anteriores: nada cambia en
silencio. Hoy no hay paso de instalación: todo el stack ya está desde la
fase 1 — ni `uv add`, ni `.env` nuevo. La primera línea de código de hoy es
de verdad: schemas.*

**Mini-verificación (el estado de partida):** abre
**http://localhost:8000/docs** con la API de la guía 11 encendida. El título
dice **0.3.0**, el tag **Administración** muestra su único habitante
(`GET /api/admin/estado`)… y ese es exactamente el punto de partida: al
final de esta guía el mismo tag mostrará las siete operaciones del panel y
el demo no estará. Guárdate esa imagen para el paso 7.

---

## Paso 2 — `schemas/admin.py`: el contrato 0.4.0 y la allow-list que no negocia

🧠 **El desarrollador piensa:** *como en las guías 4, 5 y 9: abro
`contrato_api.yaml` 0.4.0 y escribo sus schemas en Pydantic — nada más
(D-15). Y la decisión estructural de la etapa se lee por AUSENCIA, igual
que el precio ausente de `CheckoutCreate` en la guía 9: **`ProductoEditar`
no tiene `id` ni `activo`**. El `id` es del path, jamás del cuerpo (un body
que pudiera cambiar el id estaría mudando la fila que edita); y `activo` es
una escritura PROPIA — el toggle vive en su endpoint `PATCH
/api/admin/productos/{id}/activo`, no en el editor (D-52). ¿Por qué tanto
ceremonial por dos campos ausentes? Porque la tentación clásica del CRUD
apurado es recibir el body y vaciarlo sobre el ORM con un `model_dump`
ciego — y un body así, con un `"activo": false` inyectado a mano, apagaría
el producto de la vitrina sin pasar por el toggle: **mass assignment**. Lo
que el schema no puede llevar, nadie puede voltear: la allow-list ES la
seguridad de la edición (T-04-09). Fíjate también en `PedidoTransicion`:
su `estado` es un `Literal["cancelled"]` — un enum de UN valor, a propósito
(ADR-016): la dueña posee exactamente UNA transición manual, y pedir
cualquier otra cosa es 422 aquí, en la puerta, sin tocar la máquina. ¿Y el
`Metricas.top_5`? Sus items traen `nombre` desde el SNAPSHOT de la línea —
el histórico congelado al vender (D-36): un aroma desactivado sigue
apareciendo en el top con su nombre de época, porque eso fue lo que se
vendió. Y `PedidoAdmin` suma `email_clienta`: un dato que solo el rol admin
ve — la dueña es dueña del negocio entero, no de una cuenta (D-55).*

Crea **`backend/app/schemas/admin.py`**:

```python
"""Schemas Pydantic del panel de administración — espejan docs/04_arquitectura/contrato_api.yaml 0.4.0.

El contrato se aprobó ANTES que este código (API-first, ADR-007): estos
schemas lo implementan, no lo inventan. La nota obligatoria de la etapa:
ProductoEditar NO tiene id ni activo — la allow-list que veta el mass
assignment se demuestra por AUSENCIA de campo (T-04-09), igual que el
precio ausente de CheckoutCreate en la guía 9 (CART-03).
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.pedido import EstadoPedido
from app.models.producto import FamiliaAromatica


class ProductoCrear(BaseModel):
    """Lo que envía el formulario "Nuevo producto" (ADMN-01).

    El producto nuevo nace SIEMPRE activo (D-52): por eso NO existe campo
    de estado comercial acá — el default del modelo (True desde la guía 3)
    hace el trabajo. Sin sku tampoco: la clave natural del seed no es del
    panel (el upsert por sku es del seed, D-05 — el panel no hace upsert).
    """

    nombre: str = Field(min_length=1)
    descripcion: str = Field(min_length=1)
    familia: FamiliaAromatica  # el enum cerrado del catálogo (RN-01)
    precio: int = Field(ge=0)  # CLP entero, jamás negativo (RN-02)
    stock: int = Field(ge=0)
    notas: list[str] = Field(min_length=1)  # el 422 nace en la firma, como siempre
    imagen: str = Field(min_length=1)  # ruta de texto, sin upload (D-51)


class ProductoEditar(ProductoCrear):
    """Lo que el panel puede escribir de un producto existente (ADMN-01).

    La MISMA allow-list de ProductoCrear — SIN id (el id es del path) y SIN
    activo (el toggle es una escritura propia, D-52). Heredar de
    ProductoCrear NO es pereza: es la promesa de que las dos listas son y
    seguirán siendo LA MISMA lista. Lo que este schema no tiene, el mass
    assignment no puede voltear.
    """


class ProductoAdmin(BaseModel):
    """Un producto tal como lo ve la dueña: TODOS, inactivos incluidos (D-52).

    Por eso suma `activo` y `stock` — el resumen público no muestra ni uno
    ni otro: el catálogo filtra activos, el panel ve la trastienda completa.
    """

    model_config = ConfigDict(from_attributes=True)  # mapear desde el ORM

    id: int
    nombre: str
    familia: FamiliaAromatica
    precio: int
    stock: int
    imagen: str
    activo: bool


class ProductoToggle(BaseModel):
    """El cuerpo del toggle: UN solo campo — la escritura propia de activo (D-52)."""

    activo: bool  # true reactiva, false esconde (soft delete)


class PedidoTransicion(BaseModel):
    """Lo que el panel envía al transicionar un pedido (ADMN-03, D-50).

    El enum acepta UN solo valor — cancelled — porque el admin posee
    exactamente UNA transición manual en la máquina: PENDING → CANCELLED
    (ADR-016). Las demás son del flujo de pago y PAID es terminal en v1
    (el refund es ADMN-05, diferido). Pedir otro destino es 422 AQUÍ, en
    la puerta; pedirlo sobre un pedido que ya no está en curso es 409 en
    el endpoint (paso 6).
    """

    estado: Literal["cancelled"]


class PedidoAdmin(BaseModel):
    """Un pedido tal como lo ve la dueña (ADMN-03).

    Lo mismo que OrdenLista MÁS el email de la clienta dueña — visible solo
    para admin (D-55). Sin vista de detalle en el panel: la fila ya lleva
    todo lo que la gestión necesita.
    """

    numero: str  # el legible, jamás el id interno (RN-13)
    fecha: datetime
    email_clienta: str
    total: int
    estado: EstadoPedido


class ConteoEstados(BaseModel):
    """Los 4 contadores de la máquina — SIEMPRE los cuatro, aunque sean 0 (D-54)."""

    pending: int
    paid: int
    cancelled: int
    rejected: int


class TopAroma(BaseModel):
    """Una fila del top 5: nombre SNAPSHOT (el congelado al vender, D-36)."""

    nombre: str
    unidades: int


class Metricas(BaseModel):
    """Los cuatro KPI del panel (ADMN-04, D-54) — tarjetas y tabla, sin gráficos."""

    ingresos_totales: int  # suma de PAID, en CLP
    pedidos_por_estado: ConteoEstados
    top_5: list[TopAroma] = Field(max_length=5)  # el maxItems: 5 del contrato (0.4.0)
    productos_stock_bajo: int  # activos con stock ≤ STOCK_BAJO_UMBRAL (RN-14)
```

✅ **Mini-verificación:** desde `backend/`, ejecuta:

```
uv run python -c "from app.schemas.admin import ProductoCrear, ProductoEditar, PedidoTransicion; print(ProductoEditar.model_json_schema()['required']); print('activo' in ProductoEditar.model_json_schema()['properties'], 'id' in ProductoEditar.model_json_schema()['properties'])"
```

Debe imprimir la lista de SIETE campos del contrato (`nombre`,
`descripcion`, `familia`, `precio`, `stock`, `notas`, `imagen`) y `False
False` — ni `activo` ni `id` existen en `ProductoEditar`: la allow-list se
demuestra por ausencia. Y el experimento de la puerta cerrada:

```
uv run python -c "from pydantic import ValidationError; from app.schemas.admin import PedidoTransicion; PedidoTransicion(estado='cancelled'); print('cancelled: pasa');
try:
    PedidoTransicion(estado='paid')
except ValidationError:
    print('paid: 422 en la puerta')"
```

Debe imprimir `cancelled: pasa` y `paid: 422 en la puerta` — la máquina
(ADR-016) ni se entera de los destinos que nadie puede pedir.

---

## Paso 3 — `repositories/producto.py`: las escrituras admin y los DOS umbrales

🧠 **El desarrollador piensa:** *el repo del catálogo hasta hoy era de solo
lectura — `listar` (solo activos) y `obtener`. Hoy gana las cuatro piezas
que el panel necesita, y cada una trae su lección. **`todos()`** es
`listar` menos una línea: SIN el `where activo` — el admin ve la trastienda
completa, activos e inactivos (D-52). El contraste con `listar` es el
punto: misma tabla, dos preguntas, dos métodos — jamás un flag
`incluir_inactivos` que ambigüe la llamada. **`crear()`** no recibe `sku`:
la clave natural del seed no es asunto del panel — se GENERA uno único por
construcción (`uuid`), porque la columna es NOT NULL y única. Consecuencia
honesta que la guía enseña completa: crear DOS veces el mismo POST crea DOS
productos — el panel NO hace upsert (el upsert por sku es del seed, D-05) —
y el idempotente por diseño es el ESTADO, no la fila: repetir una EDICIÓN o
un TOGGLE con el mismo body deja el producto en el mismo estado final (la
segunda escritura escribe lo mismo que la primera — last-write-wins contra
uno mismo). **`actualizar()`** toma cada campo como argumento EXPLÍCITO:
la allow-list se escribe dos veces a propósito — en el schema (lo que
puede ENTRAR) y en la firma del repo (lo que se ESCRIBE) — un
`model_dump()` ciego sobre el ORM sería la puerta trasera que el schema
cerró. **Y `cambiar_activo()`** es el toggle: un campo, una escritura
propia (D-52). Los métodos cierran su transacción con `commit` como el
`crear` de cuentas de la guía 5: la escritura admin es chica y propia — la
excepción de la etapa 3 (flush sin commit) era la orden que abraza a
Webpay, y acá no hay pasarela que abrazar. Arriba del archivo, la constante
de la etapa: `STOCK_BAJO_UMBRAL = 5`, con nombre propio (RN-14) — y ojo
con el Pitfall 6: NO es el umbral de "últimas unidades" de la tienda
(stock 1-3 en la ficha, urgencia de COMPRA para la clienta): este es
reabastecimiento para la dueña. Dos conceptos, dos constantes, dos textos
— usar un mismo número para ambos escondería que responden preguntas
distintas.*

En **`backend/app/repositories/producto.py`**, agrega la constante arriba
de la clase (debajo de los imports existentes):

```python
# Umbral de stock bajo del PANEL (RN-14, D-53): productos ACTIVOS con esta
# cantidad o menos. Deliberadamente DISTINTO del aviso de "últimas
# unidades" de la tienda (stock 1-3 en la ficha, urgencia de compra): este
# es reabastecimiento para la dueña. Dos conceptos, dos constantes, dos
# textos (Pitfall 6 de la fase) — y este vive en el BACKEND, no en la
# pantalla: las métricas lo usan (paso 5).
STOCK_BAJO_UMBRAL = 5
```

Y al final de la clase `ProductoRepository`, los cuatro métodos nuevos:

```python
    # --- Etapa 4: las escrituras del panel (ADMN-01, ADMN-02) ---

    def todos(self) -> list[Producto]:
        """TODOS los productos, activos e inactivos (D-52).

        El contraste con listar() es la lección: misma tabla, dos
        preguntas. El catálogo público filtra activos; el panel ve la
        trastienda completa. Sin flag "incluir_inactivos": dos métodos
        dicen más que un parámetro ambiguo.
        """
        return list(self.db.scalars(select(Producto).order_by(Producto.id)))

    def crear(
        self,
        *,
        nombre: str,
        descripcion: str,
        familia: FamiliaAromatica,
        precio: int,
        stock: int,
        notas: list[str],
        imagen: str,
    ) -> Producto:
        """Inserta un producto que NACE ACTIVO (el default del modelo, D-52).

        El sku se GENERA único (uuid): la clave natural del seed no es del
        panel — el upsert por sku es del seed (D-05) y el panel NO hace
        upsert: crear dos veces el mismo POST crea DOS productos, cada uno
        con su sku generado. La columna es NOT NULL y única; sin generación
        no habría fila.
        """
        producto = Producto(
            sku=f"panel-{uuid.uuid4().hex[:8]}",  # 14 chars < 20, único por construcción
            nombre=nombre,
            descripcion=descripcion,
            familia=familia,
            precio=precio,
            stock=stock,
            notas=notas,
            imagen=imagen,
            # activo: ni se menciona — el default True del modelo lo trae (D-52)
        )
        self.db.add(producto)
        self.db.commit()
        self.db.refresh(producto)  # recarga el id asignado por la base
        return producto

    def actualizar(
        self,
        producto_id: int,
        *,
        nombre: str,
        descripcion: str,
        familia: FamiliaAromatica,
        precio: int,
        stock: int,
        notas: list[str],
        imagen: str,
    ) -> Producto | None:
        """Escribe la allow-list campo a campo — JAMÁS un model_dump del body.

        La firma ES la allow-list (T-04-09): cada campo que el panel puede
        escribir aparece nombrado; `activo` e `id` no están porque no se
        editan acá. Dos admins a la vez no corrompen nada: cada llamada es
        un UPDATE completo por id dentro de una transacción — la última
        escritura gana (last-write-wins, sin locking optimista).
        """
        producto = self.db.get(Producto, producto_id)
        if producto is None:
            return None  # el router traduce a 404
        producto.nombre = nombre
        producto.descripcion = descripcion
        producto.familia = familia
        producto.precio = precio
        producto.stock = stock
        producto.notas = notas
        producto.imagen = imagen
        self.db.commit()
        self.db.refresh(producto)
        return producto

    def cambiar_activo(self, producto_id: int, activo: bool) -> Producto | None:
        """El toggle del soft delete (D-52): UN campo, una escritura propia.

        Desactivar saca el producto del catálogo público sin destruir su
        historial — los pedidos viejos conservan su snapshot (D-36).
        Reactivar lo devuelve. Reversible por diseño: por eso el panel ni
        pide confirmación.
        """
        producto = self.db.get(Producto, producto_id)
        if producto is None:
            return None
        producto.activo = activo
        self.db.commit()
        self.db.refresh(producto)
        return producto

    def con_stock_bajo(self) -> int:
        """Cuántos productos ACTIVOS tienen stock ≤ STOCK_BAJO_UMBRAL (RN-14).

        Solo activos: un inactivo con stock bajo no vende — no hay nada
        que reabastecer mientras esté fuera de la vitrina.
        """
        conteo = self.db.scalar(
            select(func.count()).where(
                Producto.activo.is_(True),
                Producto.stock <= STOCK_BAJO_UMBRAL,
            )
        )
        return int(conteo)
```

Y ajusta los imports del archivo (arriba), que quedan así:

```python
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.producto import FamiliaAromatica, Producto
```

✅ **Mini-verificación:** desde `backend/`, con el seed corrido:

```
uv run python -c "from app.database import SessionLocal; from app.repositories.producto import STOCK_BAJO_UMBRAL, ProductoRepository; repo = ProductoRepository(SessionLocal()); print(STOCK_BAJO_UMBRAL, len(repo.todos()), len(repo.listar()), repo.con_stock_bajo())"
```

Debe imprimir `5 12 12` y el conteo de stock bajo de TU catálogo (los 12
del seed traen stocks variados — el número es el tuyo). Fíjate en la
pareja `12 12`: HOY `todos()` y `listar()` calzan porque los 12 del seed
están activos — la diferencia nace con el primer toggle del paso 8, y esa
diferencia ES el soft delete volviéndose visible.

---

## Paso 4 — `repositories/pedido.py`: `todos()` y la transición como UPDATE condicional

🧠 **El desarrollador piensa:** *dos adiciones, y la segunda es la lección
estructural de la fase. **`todos()`** es el espejo admin de
`por_usuario()`: la dueña ve el mundo entero — TODAS las órdenes de TODAS
las clientas, sin el filtro por dueña que rige `/api/pedidos`. Y como el
panel necesita el EMAIL de cada dueña (PedidoAdmin lo expone, D-55), la
consulta lo trae en la misma ida: un `join` con `usuarios` que devuelve
parejas `(Pedido, email)` — una consulta, cero N+1. **`anular()`** es la
transición única del admin (D-50), y se escribe con la muralla de la fase
3: la MISMA técnica del guard ya-PAID de la guía 9 (UPDATE condicional
donde el check y el write son UNA sola operación) aplicada al otro dueño.
El `WHERE numero = ? AND estado = 'pending'` decide en la base: dos
pestañas del panel que anulan el mismo pedido a la vez no lo anulan dos
veces — el motor serializa la escritura y solo una encuentra la fila
pending; la otra recibe `rowcount` 0 y eso es la señal `TransicionIlegal`
que sube (T-04-08). Sin read-check-write: entre el check y el write vive
la carrera, y RN-12 ya lo había condenado para el stock. ¿Y el stock al
anular? NO se toca — ni una línea (D-35): el stock solo se descuenta al
APROBAR el pago, y una huérfana PENDING nunca aprobó nada — nunca se
descontó, no hay nada que restituir. La transición es limpia por
geometría: un UPDATE de una columna. PAID es terminal en v1 (el refund es
ADMN-05, diferido a v2 — ADR-016), y de CANCELLED no se vuelve: la
máquina no tiene flecha de regreso.*

En **`backend/app/repositories/pedido.py`**, ajusta los imports (arriba):

```python
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.pedido import EstadoPedido, LineaPedido, Pedido
from app.models.producto import Producto
from app.models.usuario import Usuario
```

Y agrega DENTRO de `PedidoRepository`, después de `por_usuario`:

```python
    # --- Etapa 4: el panel (ADMN-03) ---

    def todos(self) -> list[tuple[Pedido, str]]:
        """TODAS las órdenes de TODAS las clientas + el email de cada dueña.

        El espejo admin de por_usuario(): sin filtro de dueña — la dueña
        del NEGOCIO ve el mundo entero. El email viaja en la misma
        consulta (join con usuarios): una ida a la base, cero N+1. Orden
        por id descendente: la más reciente primero, como el historial.
        """
        filas = self.db.execute(
            select(Pedido, Usuario.email)
            .join(Usuario, Pedido.usuario_id == Usuario.id)
            .order_by(Pedido.id.desc())
        ).all()
        return [(fila[0], fila[1]) for fila in filas]

    def anular(self, numero: str) -> bool:
        """LA transición manual del admin (D-50, ADR-016): PENDING → CANCELLED.

        La MISMA muralla del guard ya-PAID de la guía 9 (UPDATE condicional:
        el check y el write en UNA sola operación), aplicada al otro dueño.
        El WHERE exige estado pending DENTRO de la sentencia — dos pestañas
        del panel que anulan a la vez no lo anulan dos veces (T-04-08): el
        motor serializa y solo una encuentra la fila.

        NO toca stock (D-35): el stock solo baja al aprobar el pago, y una
        PENDING nunca aprobó — nunca se descontó, no hay nada que restituir.

        Devuelve True si la transición aplicó (rowcount 1) y False si el
        pedido ya no estaba en curso (rowcount 0) — el service traduce ese
        False a la señal TransicionIlegal, y el router al 409 del contrato.
        """
        resultado = self.db.execute(
            update(Pedido)
            .where(
                Pedido.numero == numero,
                Pedido.estado == EstadoPedido.pending,  # la máquina, en el WHERE
            )
            .values(estado=EstadoPedido.cancelled)
            .execution_options(synchronize_session=False)  # el objeto queda stale: el service lo refresca
        )
        self.db.commit()
        return resultado.rowcount > 0
```

Y las tres agregaciones de métricas que viven en ESTE repo (los pedidos
son su materia prima — Ejemplo D del research), al final de la clase:

```python
    # --- Etapa 4: las agregaciones de métricas (ADMN-04, D-54) ---

    def ingresos_totales(self) -> int:
        """Suma de los totales de las órdenes PAID, en CLP.

        El COALESCE no es adorno: SUM sobre cero filas devuelve NULL en
        SQL, y la tienda sin ventas debe mostrar $0 (cero honesto), no
        reventar el KPI con un None.
        """
        total = self.db.scalar(
            select(func.coalesce(func.sum(Pedido.total), 0)).where(
                Pedido.estado == EstadoPedido.paid
            )
        )
        return int(total)

    def conteos_por_estado(self) -> dict[EstadoPedido, int]:
        """Contador por estado — SIEMPRE los cuatro, aunque sean 0 (D-54).

        Se empieza con los cuatro en 0 y se pisa con lo que la base
        cuente: un estado sin órdenes no desaparece del KPI, porque la
        máquina tiene cuatro estados y el panel muestra la máquina.
        """
        conteos = {estado: 0 for estado in EstadoPedido}
        filas = self.db.execute(
            select(Pedido.estado, func.count()).group_by(Pedido.estado)
        ).all()
        for estado, conteo in filas:
            conteos[estado] = conteo
        return conteos

    def top_5(self) -> list[tuple[str, int]]:
        """Los 5 aromas más vendidos por unidades, desde el SNAPSHOT (D-36/D-54).

        Join de las líneas con sus pedidos, SOLO órdenes PAID, agrupado por
        el nombre congelado al vender: un aroma desactivado sigue
        apareciendo con su nombre de época — eso fue lo que se vendió, y
        mentirlo sería falsear la historia (la honestidad del soft delete).
        """
        filas = self.db.execute(
            select(
                LineaPedido.nombre_snapshot,
                func.sum(LineaPedido.cantidad),
            )
            .join(Pedido, LineaPedido.pedido_id == Pedido.id)
            .where(Pedido.estado == EstadoPedido.paid)
            .group_by(LineaPedido.nombre_snapshot)
            .order_by(func.sum(LineaPedido.cantidad).desc())
            .limit(5)
        ).all()
        return [(nombre, int(unidades)) for nombre, unidades in filas]
```

✅ **Mini-verificación:** desde `backend/`, con las órdenes de tu fase 3 en
la base:

```
uv run python -c "from app.database import SessionLocal; from app.repositories.pedido import PedidoRepository; repo = PedidoRepository(SessionLocal()); filas = repo.todos(); print(len(filas), filas[0][0].numero, filas[0][1]); print(repo.conteos_por_estado())"
```

Debe imprimir el número de órdenes de TU base, la más reciente con SU
numero y el email de la clienta del seed (la pareja del join), y el
diccionario de los CUATRO estados con tus conteos — Pending incluido si tu
huérfana sigue viva: ella es la invitada de honor del paso 8.

---

## Paso 5 — `services/admin.py`: la señal `TransicionIlegal` y las métricas orquestadas

🧠 **El desarrollador piensa:** *el service del panel NO conoce HTTP — la
regla de la casa desde la guía 4, y hoy se paga con una traducción que ya
tiene precedente: cuando `anular()` devuelve False, el service levanta
`TransicionIlegal` EXACTAMENTE como `iniciar_checkout` levanta
`CarroNoComprable` en la guía 9 — y el router la traduce al 409 con el
copy locked del contrato ("Ese pedido ya no está en curso."). La señal
habla dominio; el código habla contrato; nadie se mezcla. Dos servicios en
un archivo, a propósito: **`AdminService`** escribe (CRUD + transición) y
**`MetricasService`** solo lee — separarlos nombra la diferencia de la
agregación: no toca una fila, jamás escribe D1 ni D3 (proceso 14.0 del
diseño). Fíjate en `anular()`: tras el UPDATE condicional el objeto
`Pedido` de la sesión quedó STALE (la guía 9 lo enseñó con
`synchronize_session=False`) — y como la respuesta necesita el estado
NUEVO, acá sí se `refresh()`: la diferencia con la guía 9 es que allá no
se releía nada y acá la respuesta ES el pedido. Y en `listar_pedidos()`
las parejas `(Pedido, email)` del join se convierten en `PedidoAdmin`
campo a campo: el email de la dueña entra al schema en el borde del
service — el único lugar donde dominio y contrato se saludan.*

Crea **`backend/app/services/admin.py`**:

```python
"""Casos de uso del panel de administración. El service NO conoce HTTP.

La señal TransicionIlegal la traduce el router al 409 del contrato (D-50)
— la misma división de CarroNoComprable → 400 en la guía 9. Métricas vive
en su propio service porque es un caso de uso de SOLO LECTURA: no escribe
ni una fila (proceso 14.0 del diseño, ADMN-04).
"""

from sqlalchemy.orm import Session

from app.models.pedido import EstadoPedido, Pedido
from app.models.producto import Producto
from app.repositories.pedido import PedidoRepository
from app.repositories.producto import ProductoRepository
from app.repositories.usuario import UsuarioRepository
from app.schemas.admin import (
    ConteoEstados,
    Metricas,
    PedidoAdmin,
    ProductoCrear,
    ProductoEditar,
    TopAroma,
)


class TransicionIlegal(Exception):
    """Señal de la máquina de estados (D-50, ADR-016).

    La lanza anular() cuando el UPDATE condicional encontró cero filas: el
    pedido ya no está en curso (otra pestaña lo anuló, o el flujo de pago
    lo decidió antes). El router la traduce al 409 con el copy locked del
    contrato — igual que CarroNoComprable → 400 en la guía 9.
    """


class AdminService:
    """Orquesta las escrituras del panel: CRUD de productos y la transición."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.productos = ProductoRepository(db)
        self.pedidos = PedidoRepository(db)
        self.usuarios = UsuarioRepository(db)  # el email de la dueña de cada pedido

    # --- Productos (ADMN-01, ADMN-02) ---

    def listar_productos(self) -> list[Producto]:
        """TODOS los productos — inactivos incluidos (D-52)."""
        return self.productos.todos()

    def crear_producto(self, datos: ProductoCrear) -> Producto:
        """Crea un aroma nuevo — nace ACTIVO por default del modelo (D-52)."""
        return self.productos.crear(
            nombre=datos.nombre,
            descripcion=datos.descripcion,
            familia=datos.familia,
            precio=datos.precio,
            stock=datos.stock,
            notas=datos.notas,
            imagen=datos.imagen,
        )

    def editar_producto(self, producto_id: int, datos: ProductoEditar) -> Producto | None:
        """Escribe la allow-list — None si el producto no existe (404 del router)."""
        return self.productos.actualizar(
            producto_id,
            nombre=datos.nombre,
            descripcion=datos.descripcion,
            familia=datos.familia,
            precio=datos.precio,
            stock=datos.stock,
            notas=datos.notas,
            imagen=datos.imagen,
        )

    def toggle_activo(self, producto_id: int, activo: bool) -> Producto | None:
        """El soft delete y su vuelta — una escritura propia (D-52)."""
        return self.productos.cambiar_activo(producto_id, activo)

    # --- Pedidos (ADMN-03) ---

    def listar_pedidos(self) -> list[PedidoAdmin]:
        """Todas las órdenes de todas las clientas, con el email de cada dueña."""
        return [
            PedidoAdmin(
                numero=pedido.numero,
                fecha=pedido.fecha,
                email_clienta=email,
                total=pedido.total,
                estado=pedido.estado,
            )
            for pedido, email in self.pedidos.todos()
        ]

    def anular(self, numero: str) -> PedidoAdmin | None:
        """LA transición manual del admin (D-50): PENDING → CANCELLED.

        None → el pedido no existe (404 del router). TransicionIlegal → ya
        no está en curso (409 del router). Cancelar NO toca stock (D-35).
        """
        pedido = self.pedidos.por_numero(numero)
        if pedido is None:
            return None
        if not self.pedidos.anular(numero):
            raise TransicionIlegal()  # rowcount 0: otra escritura decidió antes
        # El UPDATE dejó el objeto stale (synchronize_session=False): la
        # respuesta ES el pedido, así que acá sí se refresca — la diferencia
        # con la guía 9, que no releyó nada.
        self.db.refresh(pedido)
        usuario = self.usuarios.por_id(pedido.usuario_id)  # la FK garantiza que existe
        return PedidoAdmin(
            numero=pedido.numero,
            fecha=pedido.fecha,
            email_clienta=usuario.email if usuario else "",
            total=pedido.total,
            estado=pedido.estado,
        )


class MetricasService:
    """Los cuatro KPI de la dueña (ADMN-04, D-54): solo lectura y agregación."""

    def __init__(self, db: Session) -> None:
        self.pedidos = PedidoRepository(db)
        self.productos = ProductoRepository(db)

    def calcular(self) -> Metricas:
        """Orquesta las agregaciones de los repos en el schema del contrato."""
        conteos = self.pedidos.conteos_por_estado()
        return Metricas(
            ingresos_totales=self.pedidos.ingresos_totales(),
            pedidos_por_estado=ConteoEstados(
                pending=conteos[EstadoPedido.pending],
                paid=conteos[EstadoPedido.paid],
                cancelled=conteos[EstadoPedido.cancelled],
                rejected=conteos[EstadoPedido.rejected],
            ),
            top_5=[
                TopAroma(nombre=nombre, unidades=unidades)
                for nombre, unidades in self.pedidos.top_5()
            ],
            productos_stock_bajo=self.productos.con_stock_bajo(),
        )
```

✅ **Mini-verificación:** desde `backend/`, con las órdenes de fase 3:

```
uv run python -c "from app.database import SessionLocal; from app.services.admin import MetricasService; m = MetricasService(SessionLocal()).calcular(); print(m.ingresos_totales, m.pedidos_por_estado.paid, m.top_5[0] if m.top_5 else 'sin ventas', m.productos_stock_bajo)"
```

Debe imprimir TUS números: los ingresos (la suma de TUS órdenes PAID de
fase 3 — compárala con el historial de la clienta: calza), los pagados, el
aroma más vendido con su nombre snapshot, y tu conteo de stock bajo. Las
métricas ya viven — solo les falta la puerta HTTP.

---

## Paso 6 — `routers/admin.py`: el CRUD real, todo bajo `get_current_admin`

🧠 **El desarrollador piensa:** *el router del demo se reemplaza ENTERO: hoy
el archivo pasa de un endpoint de 15 líneas a las siete operaciones del
contrato 0.4.0 — y la primera decisión es no decidir: **`get_current_admin`
en CADA endpoint, sin excepción** (ADR-015). La lección D-33 hecha patrón:
el guard de la SPA que llega en la guía 13 es UX cortés, el 403 real es
ESTO — y un solo endpoint olvidado sería la puerta trasera del panel
(T-04-07). Fíjate en el dict `PROTEGIDO`: 401 y 403 declarados UNA vez y
heredados por las siete firmas con `{**PROTEGIDO, ...}` — la lección
G-01-4 de la guía 5, escalada: cada `HTTPException` manual invisible en
`/docs` cantaría un desvío falso en la comparación contrato ↔ `/docs`
(Pitfall 5), así que el 404 del PUT, el 409 de la transición y el 422
declarativo viven TODOS en las `responses`. El 409 con SU copy locked
— "Ese pedido ya no está en curso." — tal como el contrato lo examplea.
Y dos detalles finos. **El PATCH del toggle** es el primer PATCH del
proyecto, y no es casualidad: alterna exactamente UN campo (D-52) — el
verbo que dice "un cambio chico" sobre el recurso. **El PUT del editor**
manda el body completo de la allow-list: PUT es todo-o-nada, y la allow-list
es TODO lo que se puede escribir. `datos.estado` ni se consulta en la
transición — el `Literal["cancelled"]` del schema ya garantizó el destino;
lo que el router agrega es la TRADUCCIÓN de las señales: None → 404,
TransicionIlegal → 409.*

Reemplaza **`backend/app/routers/admin.py`** COMPLETO (el demo `/estado`
se despide — su lección quedó escrita en el paso 1):

```python
"""Endpoints del panel de administración — implementan contrato_api.yaml 0.4.0.

El endpoint demo /api/admin/estado de la guía 5 se retiró (D-54): cumplió
su lección de hacer verificable el 403 por rol (D-33) y la administración
de verdad toma su puesto. TODO endpoint bajo get_current_admin (ADR-015)
— la seguridad real es del servidor; el guard de la SPA (guía 13) es UX.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_session
from app.models.usuario import Usuario
from app.schemas.admin import (
    Metricas,
    PedidoAdmin,
    PedidoTransicion,
    ProductoAdmin,
    ProductoCrear,
    ProductoEditar,
    ProductoToggle,
)
from app.schemas.producto import Error  # el cuerpo de error vive en schemas/producto desde la guía 4
from app.security import get_current_admin
from app.services.admin import AdminService, MetricasService, TransicionIlegal

# SIN prefijo propio: el registro de la guía 5 ya monta este router bajo
# /api/admin — por eso CADA path trae SU segmento en el decorador
# (/productos, /pedidos, /metricas): prefijo del include + segmento del
# decorador = el path exacto del contrato.
router = APIRouter(tags=["Administración"])

# 401 y 403, los DOS códigos del guard por rol (ADR-015), declarados una
# vez y heredados por TODAS las firmas — la lección G-01-4
# de la guía 5, escalada a un panel entero: sin `responses`, el 403 no
# aparecería en /docs y la fila contrato ↔ /docs cantaría un desvío falso.
PROTEGIDO = {
    401: {"description": "Sin sesión, o token inválido/expirado", "model": Error},
    403: {
        "description": "Con sesión, pero sin rol admin",
        "model": Error,
        # el example del contrato: el mismo detail que el demo enseñó en fase 2
    },
}


@router.get("/productos", response_model=list[ProductoAdmin], responses={**PROTEGIDO})
def listar_productos(
    actual: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_session),
) -> list[ProductoAdmin]:
    """GET /api/admin/productos — TODOS los productos, inactivos incluidos (D-52)."""
    return AdminService(db).listar_productos()


@router.post(
    "/productos",
    response_model=ProductoAdmin,
    status_code=status.HTTP_201_CREATED,  # creado — y nace SIEMPRE activo (D-52)
    responses={**PROTEGIDO, 422: {"description": "Cuerpo mal formado (familia fuera del enum, precio o stock negativos, campos faltantes) — validación declarativa", "model": Error}},
)
def crear_producto(
    datos: ProductoCrear,
    actual: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_session),
) -> ProductoAdmin:
    """POST /api/admin/productos — la primera escritura del catálogo fuera del seed (ADMN-01)."""
    return AdminService(db).crear_producto(datos)


@router.put(
    "/productos/{producto_id}",
    response_model=ProductoAdmin,
    responses={
        **PROTEGIDO,
        404: {"description": "Producto inexistente", "model": Error},
        422: {"description": "Cuerpo mal formado — validación declarativa", "model": Error},
    },
)
def editar_producto(
    producto_id: int,
    datos: ProductoEditar,  # la allow-list: sin id (es del path) y sin activo (D-52)
    actual: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_session),
) -> ProductoAdmin:
    """PUT /api/admin/productos/{id} — escribe la allow-list campo a campo (ADMN-01)."""
    producto = AdminService(db).editar_producto(producto_id, datos)
    if producto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return producto


@router.patch(
    "/productos/{producto_id}/activo",
    response_model=ProductoAdmin,
    responses={
        **PROTEGIDO,
        404: {"description": "Producto inexistente", "model": Error},
        422: {"description": "Cuerpo mal formado (falta el booleano activo) — validación declarativa", "model": Error},
    },
)
def toggle_producto(
    producto_id: int,
    datos: ProductoToggle,  # un solo campo: la escritura propia del soft delete
    actual: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_session),
) -> ProductoAdmin:
    """PATCH /api/admin/productos/{id}/activo — el soft delete y su vuelta (D-52).

    El PRIMER PATCH del proyecto: alterna exactamente UN campo — el verbo
    del cambio chico. Desactivar saca el producto del catálogo público sin
    destruir su historial: los pedidos viejos conservan su snapshot (D-36).
    """
    producto = AdminService(db).toggle_activo(producto_id, datos.activo)
    if producto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return producto


@router.get("/pedidos", response_model=list[PedidoAdmin], responses={**PROTEGIDO})
def listar_pedidos(
    actual: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_session),
) -> list[PedidoAdmin]:
    """GET /api/admin/pedidos — TODAS las órdenes de TODAS las clientas (ADMN-03)."""
    return AdminService(db).listar_pedidos()


@router.patch(
    "/pedidos/{numero}/estado",
    response_model=PedidoAdmin,
    responses={
        **PROTEGIDO,
        404: {"description": "Pedido inexistente", "model": Error},
        409: {
            "description": "Transición ilegal — el pedido ya no está en curso (la máquina de estados la rechaza, D-50)",
            "model": Error,
        },
        422: {"description": "Cuerpo mal formado (estado fuera del enum de PedidoTransicion) — validación declarativa", "model": Error},
    },
)
def transicionar_pedido(
    numero: str,
    datos: PedidoTransicion,  # Literal["cancelled"]: la única meta manual (ADR-016)
    actual: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_session),
) -> PedidoAdmin:
    """PATCH /api/admin/pedidos/{numero}/estado — la ÚNICA transición manual del sistema.

    El service habla dominio (TransicionIlegal); esta frontera habla el
    contrato: 404 si no existe, 409 con el copy locked si ya no está en
    curso — la misma traducción de CarroNoComprable → 400 en la guía 9.
    """
    try:
        pedido = AdminService(db).anular(numero)
    except TransicionIlegal:
        # rowcount 0: otra escritura (otra pestaña, o el propio flujo de
        # pago) decidió antes — el copy locked del contrato 0.4.0.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ese pedido ya no está en curso.",
        )
    if pedido is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    return pedido


@router.get("/metricas", response_model=Metricas, responses={**PROTEGIDO})
def metricas(
    actual: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_session),
) -> Metricas:
    """GET /api/admin/metricas — los cuatro KPI de la dueña (ADMN-04, D-54).

    REEMPLAZA al demo /api/admin/estado (D-33): el demo cumplió su lección
    de fase 2 y la evolución se narra acá y en el contrato — nada cambió en
    silencio (Pitfall 7). Solo lectura: no escribe ni una fila.
    """
    return MetricasService(db).calcular()
```

✅ **Mini-verificación:** enciende la API (`uv run fastapi dev app/main.py`
desde `backend/`) y abre **http://localhost:8000/docs**:

1. El tag **Administración** lista las SIETE operaciones: `GET`+`POST
   /api/admin/productos`, `PUT /api/admin/productos/{producto_id}`, `PATCH
   /api/admin/productos/{producto_id}/activo`, `GET /api/admin/pedidos`,
   `PATCH /api/admin/pedidos/{numero}/estado` y `GET /api/admin/metricas`.
2. `GET /api/admin/estado` YA NO ESTÁ — la retirada del paso 1, visible.
   (Las guías 5 y 6 que lo construyeron siguen tal cual: la historia no
   se re-edita.)
3. Despliega `PATCH /api/admin/pedidos/{numero}/estado`: lista **200**,
   **401**, **403**, **404**, **409** y **422** — el 409 con su
   descripción. Sin el `responses` de la firma no aparecería: la lección
   G-01-4, ahora con el código más interesante del panel.
4. TODAS las operaciones muestran el candado 🔒 `bearerAuth (JWT)`: el
   guard por rol les pega a todas — no hay puerta sin candado.

---

## Paso 7 — `main.py`: la versión 0.4.0 y el CORS que crece con la API

🧠 **El desarrollador piensa:** *dos líneas, dos decisiones. **La versión**:
el título de `/docs` muestra la versión que la app declara de sí misma — y
hoy implementas el contrato 0.4.0: una app que implementa 0.4.0
presentándose como 0.3.0 es un desvío que la fila contrato ↔ `/docs` del
cierre detectaría (la misma coherencia que la guía 5 exigió con 0.2.0 y la
9 con 0.3.0, ADR-007). ¿Y el `include_router` del admin? NADA que hacer:
existe desde la guía 5 — hoy cambió el CONTENIDO del router, no su
registro; el `include` sigue apuntando al mismo archivo. **El CORS**: la
guía 5 lo dejó en `["GET", "POST"]` y enseñó la regla — "el CORS crece con
la API: cada verbo nuevo que la SPA necesite cruzar origen, se declara".
Hoy llegan los primeros PUT y PATCH del proyecto (el editor y el toggle de
la guía 13), y en desarrollo el proxy de Vite disimula la omisión
(same-origin: el CORS ni actúa)… hasta el despliegue de la fase 5, cuando
la SPA estática viva en otro origen y el preflight rechace el PUT con un
error CORS que no tiene nada que ver con tu código. La cura es la misma
línea de la guía 5: los verbos nuevos entran a la lista EXPLÍCITA — jamás
el comodín `["*"]` de métodos.*

En **`backend/app/main.py`**, sube la versión en el `FastAPI(...)`:

```python
version="0.4.0"  # la del contrato que implementas (ADR-007: panel y contrato dicen lo mismo)
```

Y en el middleware CORS, agrega los dos verbos nuevos a la lista explícita:

```python
# CORS con orígenes y métodos EXPLÍCITOS (ADR-002). Crece con la API: la
# etapa 4 trae los primeros PUT (editor) y PATCH (toggle, transición) —
# siempre lista explícita, jamás comodín.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "PUT", "PATCH"],
    allow_headers=["*"],  # incluye Authorization: Bearer ...
)
```

✅ **Mini-verificación:** con la API re-encendida, el título de
**http://localhost:8000/docs** dice **Maura API 0.4.0** — la versión del
contrato que acabas de implementar. Y el preflight de los verbos nuevos
responde `200`:

```
uv run python -c "import httpx; r = httpx.request('OPTIONS', 'http://localhost:8000/api/admin/productos', headers={'Origin': 'http://localhost:5173', 'Access-Control-Request-Method': 'PATCH'}); print(r.status_code)"
```

Debe imprimir `200` — el preflight que el panel de la guía 13 mandará
antes de cada PATCH ya tiene luz verde. Pero ojo con lo que este golpe
NO prueba: el middleware CORS responde el preflight ANTES del routing —
da `200` para CUALQUIER path, exista o no la ruta (si al decorador se le
olvidara su segmento `/productos`, este mismo comando daría `200`
igual). El golpe que SÍ prueba que la ruta quedó montada es un GET sin
token:

```
uv run python -c "import httpx; r = httpx.get('http://localhost:8000/api/admin/productos'); print(r.status_code)"
```

Debe imprimir `401` — sin token no pasas ni el guard (ADR-015). Un
`404` en su lugar delataría un path no montado: el prefijo del
`include_router` de la guía 5 (`/api/admin`) más el segmento del
decorador (`/productos`) tienen que sumar EXACTAMENTE el path del
contrato.

---

## Paso 8 — La prueba de fuego: 403 a la clienta, la huérfana anulada y el snapshot intacto

🧠 **El desarrollador piensa:** *la batería completa, y cada golpe verifica
una promesa del contrato. El 403 con la clienta del seed (la clienta
autenticada NO pasa aunque quiera — la seguridad es del servidor). El
nacimiento activo del producto creado. La idempotencia de estado del
editor: dos PUT con el MISMO body dejan el producto en el MISMO estado
final — la segunda escritura escribe lo mismo (ADMN-01). El soft delete
con sus DOS caras: el producto desaparece del catálogo público PERO el
pedido viejo de fase 3 conserva su snapshot — la asimetría de la guía 9
cobrada en pantalla (D-52/D-36). La transición: 200 a la primera, 409 con
SU copy a la segunda, 422 a la meta imposible. Y las métricas contra las
órdenes REALES que la fase 3 dejó — la suma de PAID calza con el historial
porque ambas salen de la misma base. Para el aroma de prueba: créalo con
stock 4 — así también sirve de demostración del badge de stock bajo (≤ 5,
RN-14) que la guía 13 pintará. Y al final, honestidad del sistema: el
aroma de prueba NO se borra — no existe DELETE — se DESACTIVA: el soft
delete ES la forma de borrar de esta tienda.*

Con la API encendida y el seed corrido. Los golpes, en orden:

✅ **Mini-verificación (200 vs 403 — el guard es del servidor):** desde
`backend/`, ejecuta (todo en una línea — las credenciales salen del propio
`Settings`):

```
uv run python -c "import httpx; from app.config import settings; t = httpx.post('http://localhost:8000/api/auth/login', data={'username': settings.admin_email, 'password': settings.admin_password}).json()['access_token']; r = httpx.get('http://localhost:8000/api/admin/productos', headers={'Authorization': f'Bearer {t}'}); print(r.status_code, len(r.json()), r.json()[0]['activo'])"
```

Debe imprimir `200 12 True` (los 12 del seed, TODOS activos, con su
`activo` a la vista — dato que el catálogo público no muestra). Ahora
cambia las cuatro variables por las de la clienta
(`cliente_email`/`cliente_password`) y a `GET /api/admin/pedidos`: `403
{'detail': 'Requiere rol admin'}` — el token de la clienta es
PERFECTAMENTE válido (pasa `get_current_user`), pero su claim no alcanza
en `get_current_admin`. Prueba también `/api/admin/metricas` con ella:
mismo 403. Tres endpoints, un solo guard, cero excepciones.

✅ **Mini-verificación (el aroma de prueba nace activo — y con stock
bajo):**

```
uv run python -c "import httpx; from app.config import settings; t = httpx.post('http://localhost:8000/api/auth/login', data={'username': settings.admin_email, 'password': settings.admin_password}).json()['access_token']; r = httpx.post('http://localhost:8000/api/admin/productos', headers={'Authorization': f'Bearer {t}'}, json={'nombre': 'Brisa de Prueba', 'descripcion': 'Un aroma de prueba para el panel.', 'familia': 'citricas', 'precio': 6990, 'stock': 4, 'notas': ['naranja', 'azahar'], 'imagen': '/products/citricas-01.jpg'}); print(r.status_code, r.json()['id'], r.json()['activo'])"
```

Debe imprimir `201`, un `id` nuevo y `True`: nació activo sin que nadie
lo pidiera (el default del modelo, D-52) — y ni el `id` ni el sku vienen
del body. El sku `panel-XXXXXXXX` se GENERA solo en la fila de la BD (el
panel no hace upsert, D-05) y ahí se queda: el contrato NO lo expone —
`ProductoAdmin` no lo declara, así que jamás cruza el cable; es de la
trastienda, como el `id` en las pantallas de tienda. Y con stock 4 ≤ 5,
ya es un producto "stock bajo" (RN-14) — lo verás en las métricas al
final. (Guarda el `id` que devuelve: los dos golpes siguientes lo usan —
si perdiste el output, re-ejecuta este y usa
el id nuevo.)

✅ **Mini-verificación (la edición es idempotente por estado — ADMN-01):**
con el id del aroma de prueba en la variable (reemplaza `{ID}`):

```
uv run python -c "import httpx; from app.config import settings; s = httpx.Client(); t = s.post('http://localhost:8000/api/auth/login', data={'username': settings.admin_email, 'password': settings.admin_password}).json()['access_token']; h = {'Authorization': f'Bearer {t}'}; body = {'nombre': 'Brisa de Prueba', 'descripcion': 'Un aroma de prueba para el panel, ya editado.', 'familia': 'citricas', 'precio': 7490, 'stock': 4, 'notas': ['naranja', 'azahar'], 'imagen': '/products/citricas-01.jpg'}; r1 = s.put(f'http://localhost:8000/api/admin/productos/{ID}', headers=h, json=body); r2 = s.put(f'http://localhost:8000/api/admin/productos/{ID}', headers=h, json=body); print(r1.status_code, r2.status_code, r1.json()['precio'], r2.json()['precio'])"
```

Debe imprimir `200 200 7490 7490` — DOS escrituras con el MISMO body y el
producto queda en el MISMO estado final: repetir una edición no duplica ni
corrompe nada (la segunda escribe lo mismo — last-write-wins contra uno
mismo). Ese es el idempotente de ESTADO por diseño que el panel promete:
crear dos veces SÍ crea dos productos (cada uno con su sku generado), pero
editar y toggle son idempotentes por construcción. Y la allow-list en
acción: prueba inyectar `'activo': False` dentro del `body` — el PUT
responde `200` y el `activo` del producto SIGUE `True`: el campo no
existe en `ProductoEditar`, y lo que el schema no tiene, el body no
voltea (T-04-09).

✅ **Mini-verificación (la huérfana anulada — 200, 409 y 422):** la
PENDING que tu fase 3 dejó colgando (la `MAURA-000001` de la guía 9 si
nunca pagaste su retorno; si ya no tienes huérfanas, inicia un checkout
nuevo y no lo completes — reemplaza `{NUMERO}` con ella):

```
uv run python -c "import httpx; from app.config import settings; s = httpx.Client(); t = s.post('http://localhost:8000/api/auth/login', data={'username': settings.admin_email, 'password': settings.admin_password}).json()['access_token']; h = {'Authorization': f'Bearer {t}'}; r1 = s.patch(f'http://localhost:8000/api/admin/pedidos/{NUMERO}/estado', headers=h, json={'estado': 'cancelled'}); r2 = s.patch(f'http://localhost:8000/api/admin/pedidos/{NUMERO}/estado', headers=h, json={'estado': 'cancelled'}); r3 = s.patch(f'http://localhost:8000/api/admin/pedidos/{NUMERO}/estado', headers=h, json={'estado': 'paid'}); print(r1.status_code, r1.json()['estado'], r1.json()['email_clienta']); print(r2.status_code, r2.json()['detail']); print(r3.status_code)"
```

Debe imprimir tres líneas: `200 cancelled` con el email de la clienta del
seed (la dueña del pedido — dato que solo el admin ve); `409 Ese pedido ya
no está en curso.` — la segunda intención encuentra el `WHERE estado =
'pending'` vacío y la máquina la rechaza con el copy locked (D-50, la
misma muralla del guard ya-PAID); y `422` — pedir `paid` ni siquiera pasa
la puerta del `Literal`. Ahora el cobro de la promesa: con el token de la
CLIENTA, `GET /api/pedidos` muestra esa orden con estado `cancelled` — la
clienta ve "Anulado" en su historial SIN que la guía 11 se haya editado:
el historial siempre mostró el estado REAL, y hoy el estado real cambió
por fin (D-48/D-49).

✅ **Mini-verificación (el soft delete y el snapshot — las dos caras):**
desactiva un aroma que YA se vendió en fase 3 (el de tu primera orden
APROBADA — reemplaza `{ID-VENDIDO}` con su id, típicamente 1 si compraste
"Brisa de Naranja"):

```
uv run python -c "import httpx; from app.config import settings; s = httpx.Client(); t = s.post('http://localhost:8000/api/auth/login', data={'username': settings.admin_email, 'password': settings.admin_password}).json()['access_token']; h = {'Authorization': f'Bearer {t}'}; r = s.patch(f'http://localhost:8000/api/admin/productos/{ID-VENDIDO}/activo', headers=h, json={'activo': False}); publico = s.get('http://localhost:8000/api/productos'); print(r.status_code, r.json()['activo'], len(publico.json()))"
```

Debe imprimir `200 False` y UN número MENOS que antes en el catálogo
público (12 si desactivaste un aroma del seed con la "Brisa de Prueba"
aún activa): el producto desapareció de la vitrina. PERO — y esta es la
cara que hace al soft delete un DECISIÓN y no un borrado — el pedido viejo
sigue contando la verdad. Con el token de la CLIENTA, pide el detalle de
esa orden aprobada (`GET /api/pedidos/{NUMERO-APROBADA}`): sus `lineas`
muestran el `nombre_snapshot` y `precio_snapshot` del aroma desactivado,
INTACTOS (D-36) — lo que se pagó no cambia porque la vitrina cambió.
Reactívalo ahora (el mismo PATCH con `json={'activo': True}`) y el
catálogo público vuelve al número de antes: reversible por diseño (D-52).
Para cerrar, desactiva la "Brisa de Prueba" con su toggle — y ahí la
dejamos: no existe DELETE en esta tienda, y el aroma inactivo del listado
ES la forma honesta de "borrarlo" (el seed de la guía 3 sigue convergiendo
por sku: tus 12 canónicos se restauran solos; el aroma de prueba queda
inactivo, visible solo para ti).

✅ **Mini-verificación (las métricas contra las órdenes reales):**

```
uv run python -c "import httpx; from app.config import settings; t = httpx.post('http://localhost:8000/api/auth/login', data={'username': settings.admin_email, 'password': settings.admin_password}).json()['access_token']; r = httpx.get('http://localhost:8000/api/admin/metricas', headers={'Authorization': f'Bearer {t}'}); m = r.json(); print(r.status_code, m['ingresos_totales'], m['pedidos_por_estado'], m['productos_stock_bajo'], [f['nombre'] for f in m['top_5']])"
```

Debe imprimir `200` con TUS números de fase 3: los ingresos (compáralos a
ojo con la suma de las PAID del historial de la clienta — calzan, porque
ambos salen de la misma base), los CUATRO contadores (con tu huérfana
recién anulada sumando en `cancelled`), el conteo de stock bajo (la
"Brisa de Prueba" desactivada NO cuenta — solo activos, RN-14) y el top 5
con los nombres SNAPSHOT de lo que vendiste. Si tu fase 3 dejó una orden
APROBADA con "Brisa de Naranja", ella encabeza el top — congelada al
vender, aunque hoy el aroma esté como esté (D-36).

---

## ❌ El error que este archivo evita

**1. Validar la transición en el frontend.**

```tsx
// ❌ el panel decide si "puede" anular y el backend confía
if (pedido.estado === "pending") anular();  // y en el backend: aceptar cualquier PATCH

// ✅ el backend decide SOLO: UPDATE condicional, rowcount 0 → 409
update(Pedido).where(Pedido.numero == numero, Pedido.estado == EstadoPedido.pending)
```

La máquina de estados vive en el servidor (D-50, ADR-016): el `if` de la
pantalla es UX que evita un clic inútil, no la muralla — la muralla es el
`WHERE` dentro del UPDATE. Dos pestañas de admin que anulan a la vez lo
demuestran: una gana, la otra recibe el 409 con SU copy, y la fila se
refresca con la verdad (T-04-08).

**2. Un solo umbral de stock para dos preguntas.**

```python
# ❌ el mismo 3 para "¡Últimas unidades!" de la tienda y para el panel:
# la dueña reabastece con urgencia de clienta, la clienta siente urgencia
# de reabastecimiento — los dos mensajes cruzados
UMBRAL = 3

# ✅ dos constantes con nombre, dos reglas, dos textos (Pitfall 6, RN-14)
STOCK_BAJO_UMBRAL = 5   # panel: reabastecimiento (backend, métricas)
# la tienda: 1-3 en la ficha, urgencia de compra (fase 2, su propio lugar)
```

El síntoma es silencioso: nada se rompe — solo la dueña deja de entender
qué le dice su propio panel. Si un día no sabes cuál usar, pregúntale a la
pantalla: ¿quién lee este número y qué hace con él?

**3. Tocar el stock al anular una PENDING.**

```python
# ❌ "anular = devolver el stock" — pero NUNCA se descontó
self.productos.reponer_stock(pedido.lineas)  # stock fantasma: +1 que jamás fue -1

# ✅ la transición es limpia POR GEOMETRÍA: un UPDATE de una columna
update(Pedido).where(..., Pedido.estado == EstadoPedido.pending).values(estado=EstadoPedido.cancelled)
```

El stock solo se descuenta al APROBAR el pago (D-35, ADR-013): una huérfana
PENDING nunca aprobó — no hay nada que restituir. "Devolver" un stock que
no se descontó es regalar unidades: el inventario mentiría hacia arriba y
la carrera de la guía 9 habría sido en vano.

**4. El `model_dump` ciego del body al ORM.**

```python
# ❌ el body entero sobre la fila: un {"activo": false} inyectado apaga la
# vitrina sin pasar por el toggle — mass assignment (T-04-09)
for campo, valor in datos.model_dump().items():
    setattr(producto, campo, valor)

# ✅ la allow-list se escribe campo a campo: lo que la firma no nombra, no se escribe
producto.nombre = nombre
producto.precio = precio
# ... activo NO está — su escritura vive en cambiar_activo (D-52)
```

La versión ❌ compila y funciona… hasta que alguien descubre que el editor
también "sabe" apagar productos. La allow-list del schema (paso 2) y la
firma explícita del repo (paso 3) son la MISMA regla escrita dos veces a
propósito.

**5. El 409 sin declarar en `responses`.**

```python
# ❌ funciona perfecto — y /docs ni se entera: la fila contrato ↔ /docs
# del cierre canta un desvío que no existe (lección G-01-4, Pitfall 5)
raise HTTPException(status_code=409, detail="Ese pedido ya no está en curso.")

# ✅ declarado en la firma: /docs lista el 409 con su descripción
@router.patch(..., responses={**PROTEGIDO, 409: {"description": ..., "model": Error}})
```

El contrato 0.4.0 declara el 409 con SU example — la comparación de
cierre compara el panel contra el contrato, y un código invisible en
`/docs` es un desvío falso esperando gritar.

---

## ✅ Verificación de la guía 12

Desde `backend/`, con la API encendida y el seed corrido:

1. **/docs** dice **0.4.0** y el tag Administración lista las SIETE
   operaciones con SUS códigos — y `GET /api/admin/estado` ya no está
   (D-54): la retirada narrada, no silenciosa.
2. Cada path admin responde **200** con el token del admin y **403
   "Requiere rol admin"** con el de la clienta — el guard en CADA
   endpoint, sin excepciones (ADR-015).
3. `POST /api/admin/productos` → **201** con un `id` nuevo y `activo:
   true` (nace activo, D-52); ni el `id` ni el `sku` vienen del body — y
   el sku generado (`panel-…`) vive solo en la BD: el contrato no lo
   expone en `ProductoAdmin`, jamás cruza el cable.
4. Dos PUT con el mismo body → `200` ambos y el MISMO estado final
   (idempotencia de estado, ADMN-01); un `"activo": false` inyectado en el
   body se ignora — la allow-list no lo tiene.
5. `PATCH …/activo` `false` → el producto desaparece de
   `GET /api/productos` PERO el pedido viejo conserva su
   `nombre_snapshot`/`precio_snapshot` en `/api/pedidos/{numero}`
   (D-52/D-36) — y `true` lo devuelve.
6. `PATCH /api/admin/pedidos/{numero}/estado` sobre una PENDING → `200`
   con `email_clienta`; repetido → `409 "Ese pedido ya no está en
   curso."`; pidiendo `paid` → `422` (D-50, ADR-016). La clienta ve la
   orden `cancelled` en su historial sin editar la guía 11.
7. `GET /api/admin/metricas` → los CUATRO KPI contra tus órdenes reales de
   fase 3, con el top 5 desde nombres snapshot y el stock bajo contando
   solo activos (D-53/D-54).
8. El preflight `OPTIONS` de PUT y PATCH responde `200` — el CORS creció
   con la API antes de necesitarlo.

(La comparación completa contrato 0.4.0 ↔ `/docs` — las SIETE operaciones
del panel con sus códigos, el ejemplo del 409 y el Authorize probado con
ambas cuentas — es la Gran verificación final de la guía 15, como en cada
fase.)

## 📝 Punto de control (respóndelas sin mirar la guía)

1. ¿Por qué el 409 de la transición ilegal lo decide un `WHERE` dentro del
   UPDATE y no un `if` en Python — y qué le pasaría a la segunda pestaña
   de admin que anula a la vez si la validación fuera read-check-write?
   (D-50, T-04-08.)
2. `ProductoEditar` hereda de `ProductoCrear` y NO agrega nada: ¿qué dos
   campos ausentes son la decisión estructural, por qué cada uno vive
   donde vive (path/toggle), y qué ataque cierran por ausencia?
3. Cancelar una PENDING no toca stock "por geometría": ¿qué quiere decir
   eso con la línea de tiempo de una orden — cuándo se descuenta el
   stock, qué aprobó la huérfana que se anula, y qué pasaría con el
   inventario si "devolviéramos" ese stock?
4. Nombra los DOS umbrales de stock del sistema, quién lee cada uno, qué
   hace con él — y por qué compartir un número sería un bug de MENSAJE
   aunque el código compilara perfecto. (RN-14, Pitfall 6.)

## Lo que acabas de aprender

- La retirada narrada del demo `/api/admin/estado`: los endpoints
  cumplen lecciones y se van con honors — las guías viejas jamás se
  re-editan, el contrato cuenta su propia historia (D-54, Pitfall 7)
- La allow-list como seguridad estructural: `ProductoEditar` SIN `id` y
  SIN `activo`, la firma explícita del repo, y el mass assignment vetado
  por ausencia de campo (T-04-09) — la misma lección del precio ausente
  de `CheckoutCreate`, ahora para la escritura
- El soft delete como decisión: `todos()` vs `listar()`, el toggle como
  escritura propia (D-52), el producto que desaparece de la vitrina
  mientras el pedido viejo conserva su snapshot (D-36)
- `STOCK_BAJO_UMBRAL = 5` con nombre propio, distinto del "últimas
  unidades" de la tienda: dos constantes, dos reglas, dos textos (RN-14,
  Pitfall 6) — y el conteo de métricas SOLO sobre activos
- La transición manual única PENDING → CANCELLED como UPDATE condicional
  con `rowcount` — la MISMA muralla del guard ya-PAID de la guía 9
  aplicada al dueño nuevo — y la señal `TransicionIlegal` → 409 con copy
  locked, la traducción de `CarroNoComprable` → 400 hecha patrón (D-50,
  ADR-016)
- Las métricas como agregaciones SQL en el repositorio: `sum` con
  `COALESCE` para el cero honesto, `group_by` con los CUATRO estados
  siempre, el top 5 desde el nombre SNAPSHOT (honesto con el soft
  delete), y el `join` de `todos()` que trae el email de la dueña sin
  N+1 (D-54, Ejemplo D)
- `get_current_admin` en CADA endpoint con las `responses` heredadas del
  dict `PROTEGIDO` — 401/403/404/409/422 declarados, la lección G-01-4
  escalada a un panel entero (ADR-015, Pitfall 5)
- La versión 0.4.0 en `main.py` (ADR-007) y el CORS que crece con la API:
  PUT y PATCH a la lista explícita ANTES del despliegue que los necesite
- El PRIMER PUT y el PRIMER PATCH del proyecto: todo-o-nada para la
  allow-list, un solo campo para el toggle — el verbo que dice cuánto
  cambia

**Siguiente:** guia-13-panel-spa.md — la trastienda en pantalla: el guard
`RequireAdmin` con su pantalla de no autorizado, el layout propio del
panel con subnav, las tres pantallas (productos con editor inline, pedidos
con la anulación en dos pasos, métricas)… y la tabla BADGES bajando a su
módulo propio, como la guía 11 lo prometió.
