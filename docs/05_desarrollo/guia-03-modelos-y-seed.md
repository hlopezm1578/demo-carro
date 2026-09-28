# Guía 3 — Los datos: la tabla `productos` y su siembra

> **Qué construirás hoy:** los datos de Maura — la infraestructura de base de
> datos del backend, el modelo `Producto` con su familia aromática y sus notas,
> y la siembra idempotente de los 12 aromas demo (proceso 4.0 del diseño).
> **Al terminar tendrás:** tu base de datos con los 12 body splash sembrados y
> la re-ejecución sin duplicar (STORE-04) — y el modelo exacto del diccionario
> de datos del diseño (`docs/03_diseno.md` §2.2), campo por campo.
> **Necesitas:** el backend de la guía 1 (`uv run python --version` responde
> `Python 3.12.x` desde `backend/`). No hace falta encender la API: hoy
> trabajamos con la base, no con los endpoints — llegan en la guía 4.

---

## Los términos de hoy (antes de copiar nada)

| Término | Qué es, en una frase |
|---|---|
| **ORM** | Object-Relational Mapper: traduce entre tablas de la base de datos y objetos Python — escribimos clases, el ORM escribe el SQL (ADR-005) |
| **Modelo** | Una clase Python que representa una tabla: sus atributos son las columnas. `Producto` será la tabla `productos` |
| **Sesión (`Session`)** | La conversación abierta con la base de datos: carga objetos, recuerda cambios y los confirma con `commit()` |
| **Migración** | Un paso versionado que altera el schema de una BD ya creada (Alembic). En esta fase NO se usa — ADR-005 fija cuándo entra |
| **Seed (siembra)** | Un script que pobla la BD con datos demo conocidos — el proceso interno 4.0 del diseño (§3.6) |
| **Upsert** | "Actualizar o insertar": si la fila existe se actualiza; si no, se crea. La clave de la idempotencia |
| **Idempotencia** | Ejecutar la misma operación N veces deja el sistema en el mismo estado que ejecutarla 1 vez (RF-05) |

---

## Paso 1 — `app/database.py`: el motor, la sesión y la Base

🧠 **El desarrollador piensa:** *tres objetos y una regla. El **motor** (`engine`)
es el cable a la base: lee la URL de `Settings` — la escribimos en la guía 1 —
así que cambiar de SQLite a PostgreSQL mañana es cambiar una variable de
entorno, no reescribir código (ADR-005). `SessionLocal` fabrica sesiones. Y la
**sesión vive exactamente una request**: la dependencia `get_session` la abre,
la entrega y la cierra en un `finally` — las capas superiores la reciben
inyectada por FastAPI y jamás la abren a mano (ADR-001). ¿Por qué tan estricto?
Porque el ciclo de vida de la conversación con la base tiene que vivir en UN
lugar: el día que lleguen las transacciones de las órdenes (fase 3), cada
endpoint no podrá tener su propia interpretación de "cuándo confirmar". Dos
detalles del código: `check_same_thread=False` es el requisito de SQLite para
convivir con los hilos de FastAPI, y `expire_on_commit=False` deja los objetos
legibles después de un `commit()` — las fases 2+ commitean en services y
siguen leyendo atributos.*

Crea **`backend/app/database.py`**:

```python
"""Infraestructura de base de datos: engine, sesión por request y Base.

La sesión vive exactamente una request (get_session con try/finally), y las
capas superiores la reciben inyectada por FastAPI — nunca la crean.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # SQLite + hilos de FastAPI
)

# expire_on_commit=False: los objetos siguen legibles después de un commit
# (las fases 2+ commitean en services y leen atributos después).
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base declarativa de todos los modelos SQLAlchemy."""


def get_session() -> Generator[Session, None, None]:
    """Dependencia de FastAPI: una sesión por request, cerrada siempre."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

La `Session` que importarán los routers de la guía 4 sale de aquí:
`app/database.py` es el único dueño de la conversación con la base (regla de
dependencia 1 de `docs/04_arquitectura/` §4).

✅ **Mini-verificación:** desde `backend/`, ejecuta:

```
uv run python -c "from app.database import engine; print(engine.url)"
```

Debe imprimir `sqlite:///./maura.db` — la URL que `config.py` tenía esperando
desde la guía 1, ahora conectada a un motor de verdad.

---

## Paso 2 — `FamiliaAromatica`: el enum con EL GOTCHA

🧠 **El desarrollador piensa:** *la familia es una lista cerrada de cuatro
valores (RN-01) — el caso de uso exacto de un `Enum`. Pero hay un detalle que
muerde a todo el mundo: **SQLAlchemy persiste los NOMBRES de los miembros, no
sus valores**. Si declaro `CITRICAS = "citricas"`, la base guarda `CITRICAS`…
y el contrato (`contrato_api.yaml`, ADR-007) promete el slug en minúsculas. La
divergencia sería invisible hasta que el frontend filtre `?familia=citricas`
y la base conteste que no conoce ese valor. La vacuna cuesta cero: declarar
cada miembro con **nombre == valor**. Y heredar de `str` hace que al
serializar a JSON el enum viaje como su string — exactamente lo que el contrato
espera por el cable.*

Crea la carpeta **`backend/app/models/`** con su **`app/models/__init__.py`**
(vacío, como el de `routers/` en la guía 1) y luego
**`backend/app/models/producto.py`**, empezando por el enum:

```python
"""Modelo Producto y enum FamiliaAromatica (tabla `productos`)."""

import enum


class FamiliaAromatica(str, enum.Enum):
    """Familia aromática del catálogo: Cítricas, Florales, Frutales, Dulces.

    SQLAlchemy persiste los NOMBRES de los miembros, no los valores, por eso
    cada miembro se declara con nombre == valor: la BD guarda "citricas" y la
    API devuelve ese mismo slug ASCII sin acentos (RN-01). La SPA mapea el
    slug a la etiqueta con acento ("Cítricas").
    """

    citricas = "citricas"
    florales = "florales"
    frutales = "frutales"
    dulces = "dulces"
```

✅ **Mini-verificación:** desde `backend/`, ejecuta:

```
uv run python -c "from app.models.producto import FamiliaAromatica; print([m.name for m in FamiliaAromatica])"
```

Debe imprimir `['citricas', 'florales', 'frutales', 'dulces']` — los cuatro
nombres EXACTOS de los slugs. Ahora abre `docs/04_arquitectura/contrato_api.yaml`
y compáralos con el `enum` del parámetro `familia`: es la misma lista, caracter
por caracter. Si algo no calza, el contrato manda (ADR-007).

---

## Paso 3 — El modelo `Producto`, campo a campo

🧠 **El desarrollador piensa:** *no estoy inventando nada: el diccionario de
datos del diseño (`docs/03_diseno.md` §2.2) ya fijó los 10 campos y sus
restricciones; mi trabajo es traducirlos a SQLAlchemy sin agregar ni quitar.
Tres traducciones merecen ojos. **`precio` es `Integer`** porque el peso
chileno no usa decimales en la práctica (RN-02): un `Float` invitaría errores
de redondeo que en plata se pagan, y el formato "$7.990" es asunto de
presentación, no del dato. **`notas` es `JSON`** (una lista de strings) porque
la ficha las muestra como fichas sueltas (§2.3.3 del diseño): si fuera texto
plano, la pantalla tendría que adivinar dónde termina una nota y dónde empieza
la siguiente. Y **`imagen` es una ruta (`String`), no un blob** (RN-03): la
foto es un archivo del proyecto del frontend — no un dato que se filtre ni se
ordene — y guardarla dentro de la base la inflaría sin necesidad. El `sku`
lleva `unique=True, index=True`: es la llave natural estable del catálogo
(§2.3.6 del diseño) y la siembra del paso 5 depende de ella para decidir
"¿creo o actualizo?".*

Continúa **`app/models/producto.py`** (agrega los imports de SQLAlchemy y la
clase, después del enum):

```python
from sqlalchemy import JSON, Boolean, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Producto(Base):
    """Un body splash del catálogo. Precio en CLP entero, notas como lista JSON."""

    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120))
    descripcion: Mapped[str] = mapped_column(Text)
    precio: Mapped[int] = mapped_column(Integer)  # CLP entero, sin decimales (RN-02)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    familia: Mapped[FamiliaAromatica] = mapped_column(Enum(FamiliaAromatica))
    notas: Mapped[list[str]] = mapped_column(JSON, default=list)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    imagen: Mapped[str] = mapped_column(String(200))  # "/products/{sku}.jpg" (RN-03)

    def __repr__(self) -> str:
        return f"<Producto {self.sku} {self.nombre!r}>"
```

La tabla contra el diccionario de §2.2, campo a campo: `id` (clave primaria) ·
`sku` (único, 20) · `nombre` (120) · `descripcion` (texto largo) · `precio`
(entero CLP) · `stock` · `familia` (lista cerrada de 4) · `notas` (lista) ·
`activo` · `imagen` (ruta local, 200). Diez campos, diez columnas — ni uno más.

✅ **Mini-verificación:** desde `backend/`:

```
uv run python -c "from app.models.producto import Producto; print(Producto.__tablename__); print([c.name for c in Producto.__table__.columns])"
```

Debe imprimir `productos` y la lista de los 10 nombres de columna, en el mismo
orden del diccionario. Cuenta: son diez.

---

## Paso 4 — ¿Dónde nacen las tablas? `create_all` sí, Alembic todavía no

🧠 **El desarrollador piensa:** *falta decidir quién crea la tabla `productos`
la primera vez. La respuesta corta: `Base.metadata.create_all` — le ordena a la
Base "crea las tablas que falten" contra el motor. La respuesta honesta
(ADR-005): `create_all` **no altera tablas ya creadas** — si mañana agrego una
columna al modelo, la tabla existente no la adquiere por arte de magia. La
herramienta para eso es **Alembic** (migraciones versionadas), y tiene fecha de
entrada definida: recién cuando un cambio de schema toque datos existentes —
las cuentas de la fase 2 o los pedidos de la fase 3. Mientras la BD sea
desechable (12 filas demo que la siembra restaura), borrar el archivo y
resembrar es aceptable. Decidirlo explícito hoy evita "aprenderlo mal" mañana.
¿Y dónde vive el `create_all`? En el seed, **no** en `main.py`: la API no debe
mutar el schema al arrancar — una API de solo lectura (RN-04) no tiene nada que
crear; crear tablas es parte de sembrar el estado demo, no de servirlo.*

Este paso no escribe código: la llamada a `create_all` vive dentro del seed que
escribimos a continuación. La decisión queda registrada en ADR-005 con su
advertencia honesta — reléela: las consecuencias negativas existen para no
olvidarlas, no para adornar el documento.

---

## Paso 5 — `app/seed.py`: los 12 aromas canónicos y el upsert

🧠 **El desarrollador piensa:** *dos piezas: los DATOS y el MECANISMO. Los
datos son los 12 SKU canónicos que el diseño ya fijó: 4 familias × 3 productos,
precios CLP enteros entre $6.990 y $12.990 (D-07), stocks variados con
exactamente dos valores bajos (`citricas-03` con 3 y `florales-03` con 2 —
preparan la alerta de stock del panel de la fase 4) y ninguno en 0 (la ficha
siempre debe mostrar disponibilidad). El mecanismo es **upsert por SKU**:
consultar por sku; si no existe, insertar e imprimir `[+]`; si existe,
actualizar TODOS los campos al valor canónico e imprimir `[=]`. Difiere
deliberadamente del "insertar solo si la tabla está vacía" del proyecto
hermano demo-cine: aquel patrón no restaura un stock movido por pruebas. El
upsert converge SIEMPRE al estado canónico — re-ejecutarlo tras una prueba que
movió stock o precios los RESTAURA: eso es una feature (reproducibilidad,
CS3), no un bug. Y jamás borra filas: cuando lleguen los pedidos (fase 3) con
sus llaves foráneas apuntando a productos, borrar y reinsertar rompería
referencias y resetearía los ids. Upsert por sku, desde el día 1.*

Crea **`backend/app/seed.py`**:

```python
"""Seed idempotente del catálogo demo (STORE-04).

Uso (agnóstico de terminal, D-12):

    uv run python -m app.seed

Upsert por SKU: si el producto no existe se crea ("[+]"); si ya existe se
actualiza campo a campo al valor canónico ("[="). La re-ejecución converge
siempre al estado demo sin duplicar filas ni resetear IDs. Prohibido el
patrón DELETE FROM + reinsert: rompería las FK de los pedidos de la fase 3
y reiniciaría los IDs.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.models.producto import FamiliaAromatica, Producto


def upsert_producto(sesion: Session, datos: dict) -> str:
    """Crea el producto ("[+]") o lo actualiza al valor canónico ("[=]")."""
    existente = sesion.scalar(select(Producto).where(Producto.sku == datos["sku"]))
    if existente is None:
        sesion.add(Producto(**datos))
        return "[+]"
    for campo, valor in datos.items():
        setattr(existente, campo, valor)  # restaura precios/stock del demo
    return "[=]"


# Datos demo canónicos: 4 familias x 3 productos (D-05/D-06). Precios CLP
# enteros dentro de $6.990–$12.990 (D-07); imágenes locales (D-08); stock con
# exactamente dos valores bajos (citricas-03 y florales-03, para la alerta de
# la fase 4) y ninguno en 0 (la ficha siempre muestra disponibilidad).
PRODUCTOS_DEMO: list[dict] = [
    # -- Cítricas ----------------------------------------------------------
    {
        "sku": "citricas-01",
        "nombre": "Brisa de Naranja",
        "descripcion": (
            "Naranja recién pelada con un fondo de bergamota. "
            "Frescura luminosa para el día."
        ),
        "precio": 7990,
        "stock": 14,
        "familia": FamiliaAromatica.citricas,
        "notas": ["naranja", "bergamota", "mandarina"],
        "activo": True,
        "imagen": "/products/citricas-01.jpg",
    },
    {
        "sku": "citricas-02",
        "nombre": "Limón y Albahaca",
        "descripcion": (
            "Limón chispeante con albahaca fresca y un toque de cidrón. "
            "Energía cítrica para arrancar bien el día."
        ),
        "precio": 6990,
        "stock": 9,
        "familia": FamiliaAromatica.citricas,
        "notas": ["limón", "albahaca", "cidrón"],
        "activo": True,
        "imagen": "/products/citricas-02.jpg",
    },
    {
        "sku": "citricas-03",
        "nombre": "Gajo de Pomelo",
        "descripcion": (
            "Pomelo rosado con cardamomo y un cierre de lima. "
            "Jugoso, con personalidad y ganas de sol."
        ),
        "precio": 8990,
        "stock": 3,
        "familia": FamiliaAromatica.citricas,
        "notas": ["pomelo rosado", "cardamomo", "lima"],
        "activo": True,
        "imagen": "/products/citricas-03.jpg",
    },
    # -- Florales ----------------------------------------------------------
    {
        "sku": "florales-01",
        "nombre": "Jazmín de Tarde",
        "descripcion": (
            "Jazmín que abre con azahar y cierra en neroli. "
            "Un ramo sereno para la tarde."
        ),
        "precio": 9990,
        "stock": 11,
        "familia": FamiliaAromatica.florales,
        "notas": ["jazmín", "azahar", "neroli"],
        "activo": True,
        "imagen": "/products/florales-01.jpg",
    },
    {
        "sku": "florales-02",
        "nombre": "Peonía Blanca",
        "descripcion": (
            "Peonía blanca con freesia y un velo de almizcle floral. "
            "Suave, limpio y romántico."
        ),
        "precio": 8990,
        "stock": 7,
        "familia": FamiliaAromatica.florales,
        "notas": ["peonía", "freesia", "almizcle floral"],
        "activo": True,
        "imagen": "/products/florales-02.jpg",
    },
    {
        "sku": "florales-03",
        "nombre": "Rosa de Río",
        "descripcion": (
            "Rosa con geranio y un guiño de litchi. "
            "Floral con cuerpo, para no pasar inadvertida."
        ),
        "precio": 10990,
        "stock": 2,
        "familia": FamiliaAromatica.florales,
        "notas": ["rosa", "geranio", "litchi"],
        "activo": True,
        "imagen": "/products/florales-03.jpg",
    },
    # -- Frutales ----------------------------------------------------------
    {
        "sku": "frutales-01",
        "nombre": "Mora Silvestre",
        "descripcion": (
            "Mora con frambuesa y cassis. "
            "Un canasto de berries recién cosechados."
        ),
        "precio": 8490,
        "stock": 16,
        "familia": FamiliaAromatica.frutales,
        "notas": ["mora", "frambuesa", "cassis"],
        "activo": True,
        "imagen": "/products/frutales-01.jpg",
    },
    {
        "sku": "frutales-02",
        "nombre": "Durazno Crema",
        "descripcion": (
            "Durazno maduro sobre vainilla cremosa y almendra. "
            "Dulzor frutal con el confort de un postre."
        ),
        "precio": 9490,
        "stock": 8,
        "familia": FamiliaAromatica.frutales,
        "notas": ["durazno", "vainilla cremosa", "almendra"],
        "activo": True,
        "imagen": "/products/frutales-02.jpg",
    },
    {
        "sku": "frutales-03",
        "nombre": "Frutilla Fresca",
        "descripcion": (
            "Frutilla fresca con flor de azahar y un fondo de almíbar. "
            "Dulce, jugosa y sin empalagar."
        ),
        "precio": 7490,
        "stock": 5,
        "familia": FamiliaAromatica.frutales,
        "notas": ["frutilla", "flor de azahar", "almíbar"],
        "activo": True,
        "imagen": "/products/frutales-03.jpg",
    },
    # -- Dulces ------------------------------------------------------------
    {
        "sku": "dulces-01",
        "nombre": "Vainilla y Sándalo",
        "descripcion": (
            "Vainilla cremosa sobre un fondo cálido de sándalo. "
            "El abrazo dulce de la casa."
        ),
        "precio": 12990,
        "stock": 6,
        "familia": FamiliaAromatica.dulces,
        "notas": ["vainilla", "sándalo", "ámbar"],
        "activo": True,
        "imagen": "/products/dulces-01.jpg",
    },
    {
        "sku": "dulces-02",
        "nombre": "Caramelo Salado",
        "descripcion": (
            "Caramelo con un punto de sal marina y praliné. "
            "Golosura con un giro adulto."
        ),
        "precio": 11490,
        "stock": 12,
        "familia": FamiliaAromatica.dulces,
        "notas": ["caramelo", "sal marina", "praliné"],
        "activo": True,
        "imagen": "/products/dulces-02.jpg",
    },
    {
        "sku": "dulces-03",
        "nombre": "Algodón de Azúcar",
        "descripcion": (
            "Nube de algodón de azúcar con frambuesa blanca y almizcle dulce. "
            "Pura nostalgia dulce."
        ),
        "precio": 10490,
        "stock": 10,
        "familia": FamiliaAromatica.dulces,
        "notas": ["algodón de azúcar", "frambuesa blanca", "almizcle dulce"],
        "activo": True,
        "imagen": "/products/dulces-03.jpg",
    },
]


def main() -> None:
    # El schema y el seed existen ANTES de cualquier verificación de
    # endpoints: la creación de tablas vive aquí, no en main.py.
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as sesion:
        marcas = []
        for datos in PRODUCTOS_DEMO:
            marca = upsert_producto(sesion, datos)
            marcas.append(marca)
            print(f"{marca} {datos['sku']} — {datos['nombre']}")
        sesion.commit()
    print(
        f"Seed listo: {marcas.count('[+]')} creados [+], "
        f"{marcas.count('[=]')} actualizados [=] "
        f"({len(marcas)} productos en total)"
    )


if __name__ == "__main__":
    main()
```

✅ **Mini-verificación:** desde `backend/`:

```
uv run python -c "from app.seed import PRODUCTOS_DEMO; print(len(PRODUCTOS_DEMO)); print(sorted({p['familia'].value for p in PRODUCTOS_DEMO}))"
```

Debe imprimir `12` y `['citricas', 'dulces', 'florales', 'frutales']` — doce
aromas, las cuatro familias, y cada `sku` aparece una sola vez en la constante
(el `unique=True` del modelo no perdonaría un duplicado).

---

## Paso 6 — Sembrar… y volver a sembrar

Desde `backend/`, ejecuta:

```
uv run python -m app.seed
```

La primera corrida imprime una línea por aroma creado y el resumen — doce
`[+]`:

```
[+] citricas-01 — Brisa de Naranja
[+] citricas-02 — Limón y Albahaca
[+] citricas-03 — Gajo de Pomelo
[+] florales-01 — Jazmín de Tarde
[+] florales-02 — Peonía Blanca
[+] florales-03 — Rosa de Río
[+] frutales-01 — Mora Silvestre
[+] frutales-02 — Durazno Crema
[+] frutales-03 — Frutilla Fresca
[+] dulces-01 — Vainilla y Sándalo
[+] dulces-02 — Caramelo Salado
[+] dulces-03 — Algodón de Azúcar
Seed listo: 12 creados [+], 0 actualizados [=] (12 productos en total)
```

✅ **Mini-verificación (idempotencia, STORE-04):** ejecuta el MISMO comando
otra vez. Ahora imprime doce `[=]` — ninguno nuevo, todos actualizados al
canónico — y `Seed listo: 0 creados [+], 12 actualizados [=] (12 productos en
total)`. El total sigue siendo 12: nada se duplicó y ningún id se reseteó
(HU-04). Y si durante una prueba movieras un stock a mano, re-ejecutar el seed
lo RESTAURA al valor canónico — reproducibilidad total (CS3, RNF-04): una
feature deliberada del demo, no un descuido.

✅ **Mini-verificación (el gotcha del enum, cerrado):** consulta lo que la base
realmente guardó en la columna `familia`:

```
uv run python -c "from sqlalchemy import select; from app.database import SessionLocal; from app.models.producto import Producto; s = SessionLocal(); print(sorted({f.value for f in s.scalars(select(Producto.familia))}))"
```

Debe imprimir `['citricas', 'dulces', 'florales', 'frutales']` — los slugs en
minúscula, exactamente los strings que el contrato envía por el cable (RN-01).
Si hubieras declarado los miembros en MAYÚSCULAS, aquí estarías viendo
`CITRICAS`… y la cura sería borrar la BD y resembrar: barato hoy, carísimo en
la fase 3.

Nota también el archivo nuevo en `backend/`: `maura.db`. La base SQLite
completa es ese archivo (ADR-005) — y tu `.gitignore` ya lo excluye (`*.db`):
la base es local y desechable; lo reproducible es el seed, no el archivo.

---

## ❌ El error que este archivo evita

**1. Borrar la tabla para re-sembrar.** La tentación clásica: `DELETE FROM
productos` (o eliminar `maura.db`) cada vez que se quieren "resetear" los
datos. Hoy funciona. En la fase 3, cuando los pedidos apunten a productos con
llaves foráneas, borrar productos rompe referencias — y reinsertarlos les da
ids NUEVOS: un pedido histórico quedaría apuntando a un id que ya no existe.
El patrón correcto desde hoy:

```python
# ❌ NUNCA: borrar y reinsertar "para resetear"
sesion.execute(text("DELETE FROM productos"))  # rompe las FK de la fase 3 y resetea los ids

# ✅ SIEMPRE: upsert por sku — crea lo que falta, actualiza lo que hay
existente = sesion.scalar(select(Producto).where(Producto.sku == datos["sku"]))
if existente is None:
    sesion.add(Producto(**datos))
else:
    for campo, valor in datos.items():
        setattr(existente, campo, valor)
```

(Borrar `maura.db` para empezar de cero durante el aprendizaje sí está bien:
eso es desechar una BD desechable. Otra cosa es convertirlo en rutina de
"reset" el día que haya datos vivos.)

**2. El enum con nombres que no son slugs.**

```python
# ❌ La BD guardaría "CITRICAS": los NOMBRES son lo que se persiste
class FamiliaAromatica(str, enum.Enum):
    CITRICAS = "citricas"

# ✅ nombre == valor: la BD guarda el slug del contrato
class FamiliaAromatica(str, enum.Enum):
    citricas = "citricas"
```

La versión ❌ compila, siembra y parece funcionar — hasta que el frontend
filtre `?familia=citricas` y la base conteste que no conoce ese valor. La
divergencia contrato ↔ código es exactamente el pecado que esta guía existe
para evitar (ADR-007), y este enum es su primera oportunidad de aparecer.

---

## ✅ Verificación de la guía 3

Desde `backend/` (la API encendida o apagada: el seed es independiente):

1. `uv run python -m app.seed` → doce `[+]` y `Seed listo: 12 creados [+], 0
   actualizados [=] (12 productos en total)`.
2. Re-ejecutar el mismo comando → doce `[=]` y `0 creados, 12 actualizados
   (12 en total)`.
3. En tu explorador de archivos existe `backend/maura.db` — y `git status` no
   lo lista (el `.gitignore` de la guía 1 ya lo excluye).
4. La consulta de `familia` del paso 6 imprime los cuatro slugs en minúscula,
   sin acentos (RN-01).

## 📝 Punto de control (respóndelas sin mirar la guía)

1. ¿Qué persiste SQLAlchemy de un enum — los nombres de los miembros o sus
   valores — y cómo lo declaraste para que la BD guardara el slug del contrato?
2. ¿Por qué el seed hace upsert por sku en vez de borrar la tabla y
   reinsertar? Nombra las dos cosas que se romperían en la fase 3.
3. ¿Por qué `create_all` basta en esta fase y cuál es la fecha de entrada de
   Alembic según ADR-005? ¿Qué NO hace `create_all` con tablas ya creadas?

## Lo que acabas de aprender

- El ORM como traductor: modelo SQLAlchemy = tabla, atributos = columnas (ADR-001)
- La sesión por request: quién la abre, quién la cierra y por qué el router jamás la crea a mano
- EL GOTCHA del enum: los NOMBRES se persisten — nombre == valor o el contrato diverge (RN-01)
- El diccionario de datos traducido campo a campo: precio `Integer` CLP (RN-02), notas `JSON`, imagen como ruta (RN-03)
- `create_all` con su advertencia honesta y Alembic diferido con fecha de entrada (ADR-005)
- Upsert por sku: idempotencia observable (`[+]` → `[=]`), restauración canónica tras pruebas y compatibilidad con las FK futuras (STORE-04, RF-05)

**Siguiente:** guia-04-catalogo.md — la pantalla que une los tiers: la API de
productos con filtros, las fotos del catálogo, los filtros en la dirección y
la ficha completa… más la gran verificación final contra el contrato.
