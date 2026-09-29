# Guía 4 — El catálogo: la API de productos y la pantalla que une los tiers

> **Qué construirás hoy:** el catálogo completo — la API de productos con
> filtros (schemas, repositorio, servicio y router) y la pantalla que la
> consume: fotos locales, filtros en la dirección, ficha completa y estados
> async uniformes.
> **Al terminar tendrás:** la tienda de Maura navegable de punta a punta en tu
> máquina (STORE-02, STORE-03) y la **Gran verificación final**: la comparación
> contrato ↔ `/docs` que cierra la fase (ADR-007).
> **Necesitas:** las guías 1 a 3 completas — el backend con la tabla
> `productos` sembrada (re-siembra imprime doce `[=]`) y el frontend con la
> landing, las rutas y `npm run dev` funcionando.

---

## Los términos de hoy (antes de copiar nada)

| Término | Qué es, en una frase |
|---|---|
| **Schema (Pydantic)** | El molde de los datos que cruzan la frontera HTTP: valida y serializa. Es la implementación Python del schema del contrato (ADR-007) |
| **Repositorio** | La capa que ejecuta consultas — el almacén D1 del diseño hecho clase. Única capa (con `models/`) que toca SQLAlchemy |
| **Servicio** | Los casos de uso ("listar el catálogo", "ver la ficha"): decide con entidades, no conoce HTTP |
| **Validación declarativa** | Declarar las reglas en la firma (Enum, `ge=0`) y dejar que el framework las aplique: el 422 nace sin escribir un solo `if` |
| **Search params** | La parte `?clave=valor` de la dirección: donde viven los filtros para que sean compartibles |
| **Drift (desvío)** | La divergencia silenciosa entre contrato y código — lo que la verificación final existe para detectar |

---

## Paso 1 — `app/schemas/producto.py`: el contrato, implementado

🧠 **El desarrollador piensa:** *abro `contrato_api.yaml` y escribo sus
schemas en Pydantic — nada más. El contrato define `ProductoResumen` (id, sku,
nombre, precio, familia, imagen: lo que ve la grilla) y `ProductoDetalle`
(hereda el resumen y agrega descripcion, notas, stock: la ficha). ¿Por qué una
clase aparte del modelo SQLAlchemy, si tienen casi los mismos campos? Porque
son dos contratos distintos con razones distintas para cambiar: el ORM dice
cómo se GUARDA, el schema dice cómo VIAJA. El día que la ficha necesite un
campo que la tabla no guarde — o al revés —, el acoplamiento se pagaría caro.
El `model_config = ConfigDict(from_attributes=True)` le permite a Pydantic
leer los atributos del objeto ORM directamente: el puente entre las dos capas.
Y `ProductoDetalle` HEREDA de `ProductoResumen` igual que el `allOf` del
contrato: mismo patrón, dos lenguajes.*

Crea **`backend/app/schemas/__init__.py`** (vacío) y
**`backend/app/schemas/producto.py`**:

```python
"""Schemas Pydantic del catálogo — espejan docs/04_arquitectura/contrato_api.yaml.

El contrato se aprobó ANTES que este código (API-first, ADR-007): estos
schemas lo implementan, no lo inventan. Separado de models/ para que el
contrato HTTP no quede acoplado a la BD.
"""

from pydantic import BaseModel, ConfigDict

from app.models.producto import FamiliaAromatica


class ProductoResumen(BaseModel):
    """Como aparece un producto en la grilla del catálogo (STORE-02)."""

    model_config = ConfigDict(from_attributes=True)  # mapear desde el ORM

    id: int
    sku: str
    nombre: str
    precio: int  # CLP entero
    familia: FamiliaAromatica
    imagen: str


class ProductoDetalle(ProductoResumen):
    """La ficha completa del producto (STORE-03)."""

    descripcion: str
    notas: list[str]
    stock: int


class Error(BaseModel):
    """El cuerpo de error del contrato: un detail legible para el humano."""

    detail: str
```

El schema `Error` es el tercero que trae el contrato: el cuerpo de los
errores (`{"detail": "…"}`) — el 404 de la ficha lo usa tal cual en el
paso 3.

Fíjate lo que NO hay: el campo `activo` no aparece en ningún schema. El
contrato no lo expone — un producto inactivo no existe para el mundo exterior
(§2.3.5 del diseño). El modelo lo guarda; el schema lo omite. Ese tipo de
decisiones es exactamente por lo que el contrato se escribió primero: la
interfaz se pensó fría, antes de que el código tentara a "agregar de yapa".

✅ **Mini-verificación:** desde `backend/`:

```
uv run python -c "from app.schemas.producto import ProductoResumen, ProductoDetalle; print(ProductoResumen.model_json_schema()['required']); print(ProductoDetalle.model_json_schema()['required'])"
```

Debe imprimir los 6 campos requeridos del resumen y los 9 del detalle (los 6
heredados más `descripcion`, `notas`, `stock`). Compáralos con las listas
`required` de `ProductoResumen` y `ProductoDetalle` en
`docs/04_arquitectura/contrato_api.yaml`: iguales, campo por campo.

---

## Paso 2 — `app/repositories/producto.py`: el almacén D1, sin strings SQL

🧠 **El desarrollador piensa:** *el repositorio es el almacén D1 del DFD hecho
clase: una sola puerta de entrada a la tabla `productos`. Dos reglas lo
definen. Primera: la consulta es un `select()` de SQLAlchemy con condiciones
que se componen — `if familia is not None: consulta = consulta.where(...)`.
Cada filtro se agrega solo si vino; se combinan sin que ninguno sepa del otro.
Segunda — la de seguridad—: jamás strings SQL concatenadas. Cuando escribo
`where(Producto.familia == familia)`, SQLAlchemy envía el valor como PARÁMETRO
de la consulta, nunca incrustado en el texto: la inyección SQL es imposible
por construcción, no porque yo la haya validado caso a caso. Y nota qué hace y
qué no hace el repositorio: consulta (solo activos, filtros, orden estable por
id) pero NO decide — "un inactivo no se muestra" es una regla del diseño; el
repositorio la ejecuta mecánicamente, la decisión de negocio vive en el
servicio que lo llama (regla de dependencia 2 de `docs/04_arquitectura/` §4).*

Crea **`backend/app/repositories/__init__.py`** (vacío) y
**`backend/app/repositories/producto.py`**:

```python
"""Acceso a datos de Producto: select parameterizado con filtros componibles.

Es la ÚNICA capa (además de models/ y database.py) que toca SQLAlchemy —
regla de dependencia verificable de la arquitectura en capas. Jamás strings
SQL concatenadas: la consulta es parameterizada por construcción.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.producto import FamiliaAromatica, Producto


class ProductoRepository:
    """Repositorio del agregado Producto con la sesión inyectada."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def listar(
        self,
        familia: FamiliaAromatica | None = None,
        precio_min: int | None = None,
        precio_max: int | None = None,
    ) -> list[Producto]:
        """Productos activos que cumplen los filtros, orden estable por id."""
        consulta = select(Producto).where(Producto.activo.is_(True))
        if familia is not None:
            consulta = consulta.where(Producto.familia == familia)
        if precio_min is not None:
            consulta = consulta.where(Producto.precio >= precio_min)
        if precio_max is not None:
            consulta = consulta.where(Producto.precio <= precio_max)
        consulta = consulta.order_by(Producto.id)
        return list(self.db.scalars(consulta))

    def obtener(self, producto_id: int) -> Producto | None:
        """Un producto activo por id, o None (la ficha no muestra inactivos)."""
        consulta = select(Producto).where(
            Producto.id == producto_id, Producto.activo.is_(True)
        )
        return self.db.scalar(consulta)
```

✅ **Mini-verificación:** desde `backend/` (con la siembra de la guía 3 hecha):

```
uv run python -c "from app.database import SessionLocal; from app.models.producto import FamiliaAromatica; from app.repositories.producto import ProductoRepository; repo = ProductoRepository(SessionLocal()); print(len(repo.listar()), len(repo.listar(familia=FamiliaAromatica.dulces)))"
```

Debe imprimir `12 3` — el repositorio conversa con la base sembrada: 12
productos activos en total, 3 dulces con el filtro compuesto.

---

## Paso 3 — El servicio y el router: la validación declarativa y el 404

🧠 **El desarrollador piensa:** *el servicio (`CatalogService`) parece "que no
hace nada": lista y obtiene, delegando en el repositorio. Su valor es el
borde — es la capa que NO conoce HTTP. Cuando la fase 4 agregue el panel o la
asistente de IA, esos casos de uso hablarán con servicios, no con routers. La
regla "inexistente o inactivo es lo mismo" también vive aquí: el servicio
devuelve `None` en ambos casos; traducir ese `None` a un 404 con su `detail`
es trabajo del router, que sí conoce HTTP. ¿Y la validación de los query
params? Yo no la escribí: `familia: FamiliaAromatica | None` convierte el
parámetro al enum — un valor fuera de la lista no puede ni entrar — y
`Query(ge=0)` declara que los precios no admiten negativos. Nadie escribió un
`if`, y sin embargo un request mal formado recibe 422 con el formato del
contrato. Eso es validación declarativa: las reglas viven en la firma del
endpoint, donde el framework — y el lector — las encuentra de una vez.*

Crea **`backend/app/services/__init__.py`** (vacío) y
**`backend/app/services/catalogo.py`**:

```python
"""Casos de uso del catálogo: listado con filtros y ficha.

El service NO conoce HTTP (ni FastAPI): decide con entidades y delega el
acceso a datos en el repositorio inyectado.
"""

from app.models.producto import FamiliaAromatica, Producto
from app.repositories.producto import ProductoRepository


class CatalogService:
    """Orquesta el catálogo público de productos."""

    def __init__(self, repo: ProductoRepository) -> None:
        self.repo = repo

    def listar(
        self,
        familia: FamiliaAromatica | None = None,
        precio_min: int | None = None,
        precio_max: int | None = None,
    ) -> list[Producto]:
        """Listar productos activos con filtros opcionales (STORE-02)."""
        return self.repo.listar(
            familia=familia, precio_min=precio_min, precio_max=precio_max
        )

    def obtener(self, producto_id: int) -> Producto | None:
        """La ficha de un producto, o None si no existe (STORE-03)."""
        return self.repo.obtener(producto_id)
```

Crea **`backend/app/routers/productos.py`**:

```python
"""Endpoints públicos del catálogo (GET, solo JSON — dos tiers estrictos).

El router valida la frontera HTTP (query params declarativos: Enum y ge=0
producen el 422 del contrato sin código manual) y delega en CatalogService.
Nunca importa SQLAlchemy: la sesión llega inyectada desde app.database.
"""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.database import Session, get_session
from app.models.producto import FamiliaAromatica
from app.repositories.producto import ProductoRepository
from app.schemas.producto import Error, ProductoDetalle, ProductoResumen
from app.services.catalogo import CatalogService

router = APIRouter(tags=["Productos"])


@router.get("", response_model=list[ProductoResumen])
def listar_productos(
    familia: FamiliaAromatica | None = None,
    precio_min: int | None = Query(default=None, ge=0),
    precio_max: int | None = Query(default=None, ge=0),
    db: Session = Depends(get_session),
) -> list[ProductoResumen]:
    """GET /api/productos — grilla del catálogo con filtros (STORE-02)."""
    servicio = CatalogService(ProductoRepository(db))
    return servicio.listar(
        familia=familia, precio_min=precio_min, precio_max=precio_max
    )


@router.get(
    "/{producto_id}",
    response_model=ProductoDetalle,
    responses={
        404: {
            "description": "Producto inexistente (o inactivo)",
            "model": Error,
        }
    },
)
def obtener_producto(
    producto_id: int,
    db: Session = Depends(get_session),
) -> ProductoDetalle:
    """GET /api/productos/{producto_id} — ficha completa (STORE-03)."""
    servicio = CatalogService(ProductoRepository(db))
    producto = servicio.obtener(producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto
```

Fíjate en el `responses` del decorator de `obtener_producto`. El `raise
HTTPException(404)` funciona en runtime — lo comprobaste con el 999 —, pero
FastAPI NO documenta en OpenAPI las excepciones lanzadas a mano: sin esta
declaración, `/docs` listaría solo 200 y 422 para este endpoint… y el contrato
promete también un 404 con cuerpo `Error`. Declararlo en la firma hace tres
cosas a la vez: el panel lo muestra, muestra su esquema (`Error`, con `detail`
string) y deja la regla visible donde el framework y el lector la buscan. Es la
contracara del 422 automático: ese lo produce la validación de la firma; el 404
lo produce tu código — y por eso hay que declararlo tú también en la firma.

Y registra el router en **`backend/app/main.py`** — dos líneas, composición
no lógica (ADR-001): el import junto al de `salud`…

```python
from app.routers import productos, salud
```

…y el registro junto al existente, al final del archivo:

```python
app.include_router(salud.router, prefix="/api/salud")
app.include_router(productos.router, prefix="/api/productos")
```

Enciende la API (`uv run fastapi dev app/main.py` desde `backend/`) y
experimenta en el navegador:

✅ **Mini-verificación (la validación declarativa, en vivo):**

1. Abre **http://localhost:8000/api/productos** → el JSON completo: 12
   objetos con `id`, `sku`, `nombre`, `precio`, `familia`, `imagen` — el
   resumen del contrato, sin `descripcion`/`notas`/`stock`.
2. Abre **http://localhost:8000/api/productos?familia=citricas** → solo los
   3 cítricos; el slug viaja SIN acentos por el cable (RN-01).
3. Abre **http://localhost:8000/api/productos?familia=vinagre** → **422**
   con un JSON de error que nombra el valor rechazado — y nadie escribió ese
   `if`: lo produjo el Enum de la firma del endpoint.
4. Abre **http://localhost:8000/api/productos/1** → la ficha completa (con
   `descripcion`, `notas`, `stock`)… y **http://localhost:8000/api/productos/999**
   → 404 con `{"detail": "Producto no encontrado"}` — el `None` del servicio
   traducido a HTTP por el router.
5. Abre **http://localhost:8000/docs** y despliega `GET /api/productos/{producto_id}`:
   además de la 200 aparece la respuesta **404** con su descripción y el
   esquema `Error`. Sin el `responses` del decorator, el panel no la mostraría
   aunque el 404 funcionara — esa es exactamente la comparación que cierra la
   fila 11 de la gran verificación final.

---

## Paso 4 — Las fotos: 12 imágenes locales, cero hotlinks

🧠 **El desarrollador piensa:** *el campo `imagen` de la siembra ya apunta a
`/products/{sku}.jpg` — rutas locales (RN-03). Ahora necesito que esos
archivos EXISTAN en el proyecto del frontend: Vite sirve estático todo lo que
vive en `public/`, así que `/products/citricas-01.jpg` se sirve desde
`frontend/public/products/citricas-01.jpg`. ¿Por qué descargar y no enlazar
directo a la fuente? Porque un demo que depende de que un servicio externo no
haya cambiado la URL, no haya caído o no te haya limitado las peticiones no es
un demo confiable — y porque la decisión ya está tomada: RN-03 exige archivo
local. Esta es la única sección de toda la guía con URLs de terceros: las
fotos las eliges TÚ, las descargas a TU proyecto y de ahí en adelante la
tienda es 100 % local.*

En tu proyecto, crea la carpeta **`frontend/public/products/`** y descarga 12
fotos stock de licencia libre desde **Unsplash** (`unsplash.com`) o **Pexels**
(`pexels.com`) — una por SKU, guardadas con el nombre EXACTO del sku:

| Archivos | Familia | Criterio de búsqueda visual |
|---|---|---|
| `citricas-01.jpg` … `citricas-03.jpg` | Cítricas | Naranjas, limones, pomelo — luz brillante, tonos ámbar |
| `florales-01.jpg` … `florales-03.jpg` | Florales | Flores suaves (jazmín, peonía, rosa) sobre fondo claro |
| `frutales-01.jpg` … `frutales-03.jpg` | Frutales | Berries, durazno, frutilla — jugosidad visible |
| `dulces-01.jpg` … `dulces-03.jpg` | Dulces | Vainilla, caramelo, algodón de azúcar — tonos cálidos |

Criterios de consistencia visual (la grilla se ve profesional cuando las fotos
"conversan" entre sí):

1. **Dentro de cada familia:** las tres fotos comparten paleta y mood (las
   cítricas bien iluminadas, las dulces cálidas) — el badge de familia
   refuerza la lectura, no la corrige.
2. **Entre familias:** mismo estilo fotográfico (todas de producto o todas de
   "ambiente", sin mezclas) — y clima de tienda de belleza: frascos, sprays,
   ingredientes en primer plano y fondos claros; evita fotos de comida
   servida o platos armados, que se leen como restaurante y no como marca
   de cuidado personal.
3. **Formato:** cualquier proporción sirve — la card recorta con
   `object-cover` — pero prefiere sujetos centrados. Si la descarga viene en
   `.png` o `.webp`, conviértela o descarga otra: el nombre debe terminar en
   `.jpg` exacto, porque esa ruta ya está sembrada en la base con esa
   extensión.

(La licencia de ambos sitios permite este uso educativo sin atribución
obligatoria; igual, anotar la URL de origen de cada foto en un comentario de
tu proyecto es buena práctica profesional.)

✅ **Mini-verificación:** tu explorador de archivos muestra **12 archivos
`.jpg`** en `frontend/public/products/` con los nombres exactos de los sku
(`citricas-01.jpg` … `dulces-03.jpg`). Con `npm run dev` corriendo, abre
**http://localhost:5173/products/citricas-01.jpg**: la foto se sirve desde tu
propio proyecto — local, sin salir a internet.

### Las fotos también visten la landing

La landing de la guía 2 vistió su hero con anillos concéntricos en CSS — era
lo honesto: cuando la construiste, no existían fotos. Ahora existen, y el
círculo se convierte en la foto de tu producto. En
**`frontend/src/features/landing/Landing.tsx`**, dentro del hero, reemplaza
los tres `div` de los anillos (los que llevan `rounded-full` con `inset-0`,
`inset-6` e `inset-14`) por tu primera foto cítrica:

```tsx
<img
  src="/products/citricas-01.jpg"
  alt="Body splash artesanal de Maura"
  className="absolute inset-0 aspect-square w-full rounded-full object-cover shadow-xl ring-8 ring-white"
/>
```

Los tres chips flotantes ("Hecho a mano", "Lotes pequeños", "Sin
intermediarios") se quedan: ahora flotan sobre la foto — mismo círculo,
mismo anillo blanco, pero con contenido real adentro.

Y en la sección de familias, agrega la foto de cada familia como primera
hija de la card (justo antes del kicker "Familia 0X"):

```tsx
<img
  src={`/products/${f.slug}-01.jpg`}
  alt={`Aroma de la familia ${FAMILIA_LABELS[f.slug]}`}
  className="aspect-[4/3] w-full rounded-xl object-cover"
/>
```

✅ **Mini-verificación:** recarga `http://localhost:5173/`: el hero muestra
la foto dentro del círculo con su anillo blanco, los chips flotan sobre la
imagen, y cada card de familia abre con su foto. La ruta sigue siendo 100 %
local — el hero no volvió a los hotlinks: usa las imágenes que ya
descargaste a TU proyecto.

---

## Paso 5 — La barra de filtros: el estado en la dirección

🧠 **El desarrollador piensa:** *la decisión de UX más importante de la
pantalla ya la tomó el diseño (§4.1): los filtros viven en la DIRECCIÓN
(`?familia=citricas&precio_min=6990`), no en un `useState`. Tres regalos
salen de eso: la vista filtrada se puede COMPARTIR (pegar el link en WhatsApp
abre la tienda ya filtrada), el botón atrás/adelante del navegador FUNCIONA
(cada filtro aplicado es una entrada del historial), y RECARGAR no pierde
nada. El mecanismo es `useSearchParams`: leo los parámetros para saber el
estado y escribo con `setParams` para cambiarlo — y como el `queryKey` de
TanStack Query incluye los parámetros, cada combinación de filtros tiene su
propia caché: volver a un filtro ya visto es instantáneo. Los chips muestran
la etiqueta con acento ("Cítricas") pero escriben el slug ASCII (`citricas`):
la RN-01 completa — por el cable sin acentos, en pantalla con acentos. El
formulario de precio hace submit con botón, no tecla a tecla: escribir "8000"
serían cuatro consultas que nadie pidió; el botón "Filtrar precio" escribe
`precio_min` y `precio_max` JUNTOS — una consulta, una entrada de historial. Y
el `key={params.toString()}` del `<form>` es el truco React para resetear
inputs desde afuera: cuando la URL cambia (por "Limpiar filtros" o el botón
atrás), el formulario se remonta con los valores frescos de la dirección.
`ProductCard` no se toca: la card que construiste en la guía 2 ya cumple todo
el contrato visual (imagen `aspect-square object-cover` con `loading="lazy"`
y `alt` = nombre, badge de familia, nombre `line-clamp-2`, precio con
`Intl.NumberFormat` es-CL CLP) — hoy solo le llegan datos de verdad.*

Reemplaza **`frontend/src/features/catalogo/Catalogo.tsx`** completo:

```tsx
import { useQuery } from "@tanstack/react-query";
import type { FormEvent } from "react";
import { useSearchParams } from "react-router";
import { apiGet } from "../../lib/api";
import { FAMILIA_LABELS, type ProductoResumen } from "../../types/api";
import ProductCard from "./ProductCard";

const chips = [
  { slug: "", label: "Todas" },
  ...Object.entries(FAMILIA_LABELS).map(([slug, label]) => ({ slug, label })),
];

export default function Catalogo() {
  const [params, setParams] = useSearchParams();
  const familia = params.get("familia") ?? "";

  const query = useQuery({
    queryKey: ["productos", params.toString()],
    queryFn: () => {
      const filtros = new URLSearchParams();
      params.forEach((valor, clave) => {
        if (valor !== "") filtros.set(clave, valor);
      });
      const sufijo = filtros.toString() ? `?${filtros}` : "";
      return apiGet<ProductoResumen[]>(`api/productos${sufijo}`);
    },
  });

  function elegirFamilia(slug: string) {
    const siguientes = new URLSearchParams(params);
    if (slug === "") siguientes.delete("familia");
    else siguientes.set("familia", slug);
    setParams(siguientes, { replace: true });
  }

  function filtrarPrecio(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    const datos = new FormData(evento.currentTarget);
    const siguientes = new URLSearchParams(params);
    for (const clave of ["precio_min", "precio_max"]) {
      const valor = String(datos.get(clave) ?? "");
      if (valor === "") siguientes.delete(clave);
      else siguientes.set(clave, valor);
    }
    setParams(siguientes);
  }

  function limpiarFiltros() {
    setParams(new URLSearchParams());
  }

  if (query.isPending) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {Array.from({ length: 8 }).map((_, i) => (
          <div
            key={i}
            className="aspect-square animate-pulse bg-neutral-200 rounded-2xl"
          />
        ))}
      </div>
    );
  }

  if (query.isError) {
    return (
      <div className="max-w-xl mx-auto px-4 py-16 text-center">
        <h1 className="text-xl font-bold text-neutral-900">
          No pudimos cargar el catálogo
        </h1>
        <p className="mt-2 text-sm text-neutral-600">
          Revisa que el backend esté corriendo en el puerto 8000 e inténtalo
          de nuevo.
        </p>
        <button
          onClick={() => query.refetch()}
          className="mt-6 bg-orange-600 text-white font-bold rounded-full px-6 py-2 min-h-11 hover:bg-orange-700 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
        >
          Reintentar
        </button>
      </div>
    );
  }

  const productos = query.data;
  const total = productos.length;
  const hayFiltros = [...params.keys()].length > 0;

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl md:text-3xl font-extrabold text-neutral-900">
        Nuestros aromas
      </h1>

      <div className="mt-5 bg-orange-50 rounded-2xl p-4 flex flex-wrap gap-4 items-center">
        <div className="flex flex-wrap gap-2">
          {chips.map((chip) => (
            <button
              key={chip.slug}
              onClick={() => elegirFamilia(chip.slug)}
              className={`rounded-full px-4 py-2 min-h-11 text-sm border focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none ${
                familia === chip.slug
                  ? "bg-orange-600 border-orange-600 text-white font-bold"
                  : "bg-white border-orange-200 text-neutral-700"
              }`}
            >
              {chip.label}
            </button>
          ))}
        </div>

        <form
          key={params.toString()}
          onSubmit={filtrarPrecio}
          className="flex flex-wrap gap-2 items-center"
        >
          <input
            type="number"
            min="0"
            name="precio_min"
            defaultValue={params.get("precio_min") ?? ""}
            placeholder="$ mínimo"
            aria-label="Precio mínimo"
            className="w-32 rounded-lg border border-orange-200 px-4 py-2 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
          />
          <input
            type="number"
            min="0"
            name="precio_max"
            defaultValue={params.get("precio_max") ?? ""}
            placeholder="$ máximo"
            aria-label="Precio máximo"
            className="w-32 rounded-lg border border-orange-200 px-4 py-2 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
          />
          <button
            type="submit"
            className="bg-white border border-orange-300 font-bold rounded-full px-4 py-2 min-h-11 text-sm focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
          >
            Filtrar precio
          </button>
        </form>

        {hayFiltros && (
          <button
            onClick={limpiarFiltros}
            className="text-sm text-orange-600 min-h-11 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
          >
            Limpiar filtros
          </button>
        )}
      </div>

      <p className="mt-4 text-sm font-semibold text-neutral-500">
        {total} {total === 1 ? "aroma" : "aromas"}
      </p>

      {total === 0 && hayFiltros && (
        <div className="mt-6 max-w-xl mx-auto py-8 text-center">
          <h2 className="text-xl font-bold text-neutral-900">
            No encontramos aromas con esos filtros
          </h2>
          <p className="mt-2 text-sm text-neutral-600">
            Prueba con otra familia o amplía el rango de precio.
          </p>
          <button
            onClick={limpiarFiltros}
            className="mt-6 inline-flex items-center text-sm text-orange-600 min-h-11 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
          >
            Limpiar filtros
          </button>
        </div>
      )}

      {total === 0 && !hayFiltros && (
        <div className="mt-6 max-w-xl mx-auto py-8 text-center">
          <h2 className="text-xl font-bold text-neutral-900">
            Aún no hay aromas por aquí
          </h2>
          <p className="mt-2 text-sm text-neutral-600">
            Siembra los datos demo con{" "}
            <code>uv run python -m app.seed</code> y vuelve a intentar.
          </p>
          <button
            onClick={() => query.refetch()}
            className="mt-6 bg-orange-600 text-white font-bold rounded-full px-6 py-2 min-h-11 hover:bg-orange-700 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
          >
            Reintentar
          </button>
        </div>
      )}

      {total > 0 && (
        <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {productos.map((producto) => (
            <ProductCard key={producto.id} producto={producto} />
          ))}
        </div>
      )}
    </div>
  );
}
```

Tres notas del bloque, antes de que pregunten:

- Los chips se derivan de `FAMILIA_LABELS` (`types/api.ts`): "Todas" más las
  cuatro familias — una sola fuente de verdad para las etiquetas.
- `elegirFamilia` usa `replace: true`: cambiar de chip no llena el historial
  de basura (el atrás te lleva a la página anterior, no a través de cada chip
  que tocaste). El formulario de precio SÍ agrega historial: aplicar un rango
  es una acción deliberada que merece su atrás.
- El filtro viaja al backend: la SPA pide `api/productos?familia=...` y el
  SERVIDOR filtra — la SPA nunca filtra datos que no recibió (el diseño del
  proceso 2.0, §3.4).

✅ **Mini-verificación (la dirección ES el estado):** con los dos servidores
corriendo, abre **http://localhost:5173/productos**: 12 aromas en la grilla
con sus fotos. Filtra por "Cítricas": la dirección cambia a
`/productos?familia=citricas` y quedan 3. COPIA la dirección completa, abre
una pestaña nueva y pégala: llega YA filtrada. Aplica el rango 8000–9500 con
el botón: la dirección gana `precio_min=8000&precio_max=9500` y la grilla se
acota. El botón atrás del navegador deshace el último filtro aplicado.

---

## Paso 6 — El contador y los cuatro estados de la pantalla

🧠 **El desarrollador piensa:** *recuerda la guía 2: `/productos` mostraba
honestamente "No pudimos cargar el catálogo" porque el endpoint no existía.
Hoy ese error pasó de ser la pantalla permanente a ser una de las cuatro
formas de la MISMA pantalla — y por eso los estados se diseñaron antes de que
existieran datos: la pantalla que ya sabe estar cargando, fallar, estar vacía
y estar llena no se rompe cuando la realidad cambia. Los cuatro estados, en
el orden en que el bloque los pregunta: `isPending` → 8 esqueletos del MISMO
tamaño que las cards reales (la página no salta cuando llegan los datos);
`isError` → el bloque centrado con su causa probable y "Reintentar"
(`refetch()` de TanStack Query); vacío CON filtros → "No encontramos aromas
con esos filtros" + "Limpiar filtros" (la causa es tuya: la pantalla te
ayuda a deshacerla); vacío SIN filtros → "Aún no hay aromas por aquí" + la
pista de la siembra (la causa es del entorno: la BD está vacía). Y el
contador con plural correcto ("12 aromas" / "1 aroma" / "0 aromas"): filtrar
a cero tiene que ser EVIDENTE, nunca un misterio (§4.3 del diseño).*

✅ **Mini-verificación (los estados, provocados a propósito):**

1. **Vacío con filtros:** aplica el rango 0–1000 (o "Cítricas" + máximo
   1000). La grilla se reemplaza por "No encontramos aromas con esos
   filtros", "Prueba con otra familia o amplía el rango de precio." y la
   acción "Limpiar filtros"; el contador dice "0 aromas". Clic en "Limpiar
   filtros": vuelven los 12.
2. **Error controlado:** DETÉN el backend (`Ctrl+C` en su terminal) y recarga
   `/productos`: "No pudimos cargar el catálogo" con "Revisa que el backend
   esté corriendo en el puerto 8000 e inténtalo de nuevo." y el botón
   "Reintentar". Vuelve a encender el backend y clic en "Reintentar" (sin
   recargar la página): el catálogo regresa — eso es `refetch()` trabajando.

(El estado "vacío sin filtros" hoy no debería aparecer con la siembra hecha —
salvo que borres `maura.db` y no re-siembres: pruébalo si quieres, es
inofensivo y es justamente su razón de existir.)

---

## Paso 7 — La ficha completa (y el volver que preserva filtros)

🧠 **El desarrollador piensa:** *la ficha de la guía 2 era mínima a propósito;
hoy completa el diseño §4.4. Tres decisiones. **La regla de stock como
componente:** el diseño fija tres formas de disponibilidad (más de 3 → verde;
1 a 3 → ámbar "¡Últimas N unidades!"; 0 → "Agotado") — la traduzco a un
`BadgeDisponibilidad` que recibe el número y decide solo: la regla vive en UN
lugar y el panel de la fase 4 la reutilizará. **Las notas como chips**
(§2.3.3): la lista JSON que guardamos en la guía 3, renderizada como fichas
sueltas — y si llegara vacía, la sección completa se omite
(`notas.length > 0 && ...`): rama defensiva barata. **Volver con
`navigate(-1)`:** la tentación es `<Link to="/productos">` — pero eso abre el
catálogo VIRGEN: quien entró desde "Florales + rango 8000–10000" y vuelve por
Link pierde sus filtros. `navigate(-1)` pisa el botón atrás del navegador — y
como cada filtro era una entrada del historial (paso 5), volver restaura
exactamente lo que había. El estado vivía en la dirección; por eso volver
funciona. Y para el 404 necesito DISTINGUIRLO de un error de red: extiendo
`lib/api.ts` con un `ApiError` que carga el `status` — la ficha pregunta
`instanceof ApiError && status === 404` y muestra "Producto no encontrado" en
vez del error genérico. Dos errores distintos, dos pantallas distintas
(HU-03).*

Primero, reemplaza **`frontend/src/lib/api.ts`** completo — es el de la guía
2 con dos cambios: la clase arriba y el `throw` ahora lanza `ApiError`:

```typescript
export class ApiError extends Error {
  readonly status: number;

  constructor(mensaje: string, status: number) {
    super(mensaje);
    this.status = status;
  }
}

const base = import.meta.env.VITE_API_URL ?? "";

export async function apiGet<T>(ruta: string): Promise<T> {
  const res = await fetch(`${base}/${ruta}`);
  if (!res.ok) {
    let mensaje = `Error HTTP ${res.status}`;
    try {
      const cuerpo = await res.json();
      if (cuerpo?.detail) mensaje = cuerpo.detail;
    } catch {
      // El cuerpo no traía JSON: nos quedamos con el mensaje genérico
    }
    throw new ApiError(mensaje, res.status);
  }
  return res.json();
}
```

Y reemplaza **`frontend/src/features/catalogo/FichaProducto.tsx`** completo:

```tsx
import { useQuery } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router";
import { ApiError, apiGet } from "../../lib/api";
import {
  FAMILIA_BADGES,
  FAMILIA_LABELS,
  type ProductoDetalle,
} from "../../types/api";

const clp = new Intl.NumberFormat("es-CL", { style: "currency", currency: "CLP" });

function BadgeDisponibilidad({ stock }: { stock: number }) {
  if (stock === 0) {
    return (
      <span className="text-sm rounded-full px-2 py-1 bg-neutral-200 text-neutral-700">
        Agotado
      </span>
    );
  }
  if (stock <= 3) {
    return (
      <span className="text-sm rounded-full px-2 py-1 bg-amber-100 text-amber-800">
        ¡Últimas {stock} unidades!
      </span>
    );
  }
  return (
    <span className="text-sm rounded-full px-2 py-1 bg-emerald-100 text-emerald-800">
      Disponible
    </span>
  );
}

export default function FichaProducto() {
  const { id } = useParams();
  const navigate = useNavigate();

  const query = useQuery({
    queryKey: ["producto", id],
    queryFn: () => apiGet<ProductoDetalle>(`api/productos/${id}`),
  });

  if (query.isPending) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-10 grid md:grid-cols-2 gap-10">
        <div className="aspect-square animate-pulse bg-neutral-200 rounded-3xl" />
        <div className="space-y-4">
          <div className="h-6 w-24 animate-pulse bg-neutral-200 rounded-full" />
          <div className="h-8 w-3/4 animate-pulse bg-neutral-200 rounded-2xl" />
          <div className="h-4 w-1/2 animate-pulse bg-neutral-200 rounded-2xl" />
        </div>
      </div>
    );
  }

  if (
    query.isError &&
    query.error instanceof ApiError &&
    query.error.status === 404
  ) {
    return (
      <div className="max-w-xl mx-auto px-4 py-16 text-center">
        <h1 className="text-xl font-bold text-neutral-900">
          Producto no encontrado
        </h1>
        <p className="mt-2 text-sm text-neutral-600">
          Puede que el enlace esté viejo.
        </p>
        <Link
          to="/productos"
          className="mt-6 inline-flex items-center text-sm text-orange-600 min-h-11 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
        >
          Volver al catálogo
        </Link>
      </div>
    );
  }

  if (query.isError) {
    return (
      <div className="max-w-xl mx-auto px-4 py-16 text-center">
        <h1 className="text-xl font-bold text-neutral-900">
          No pudimos cargar este producto
        </h1>
        <p className="mt-2 text-sm text-neutral-600">
          Revisa que el backend esté corriendo en el puerto 8000 e inténtalo
          de nuevo.
        </p>
        <button
          onClick={() => query.refetch()}
          className="mt-6 bg-orange-600 text-white font-bold rounded-full px-6 py-2 min-h-11 hover:bg-orange-700 focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
        >
          Reintentar
        </button>
      </div>
    );
  }

  const producto = query.data;

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <button
        onClick={() => navigate(-1)}
        className="text-sm text-orange-600 min-h-11 flex items-center focus-visible:ring-2 focus-visible:ring-orange-600 focus:outline-none"
      >
        ← Volver al catálogo
      </button>

      <div className="mt-4 grid md:grid-cols-2 gap-10">
        <img
          src={producto.imagen}
          alt={producto.nombre}
          className="rounded-3xl aspect-square object-cover bg-neutral-200 w-full shadow-md"
        />
        <div>
          <div className="flex flex-wrap gap-2">
            <span
              className={`text-sm rounded-full px-2 py-1 ${FAMILIA_BADGES[producto.familia]}`}
            >
              {FAMILIA_LABELS[producto.familia]}
            </span>
            <BadgeDisponibilidad stock={producto.stock} />
          </div>
          <h1 className="mt-3 text-2xl md:text-3xl font-extrabold text-neutral-900">
            {producto.nombre}
          </h1>
          <p className="mt-1 text-2xl font-extrabold text-orange-700">
            {clp.format(producto.precio)}
          </p>
          <p className="mt-5 text-base leading-relaxed text-neutral-600">
            {producto.descripcion}
          </p>
          {producto.notas.length > 0 && (
            <div className="mt-6">
              <p className="text-sm font-bold text-neutral-900">
                Notas aromáticas
              </p>
              <div className="mt-2 flex flex-wrap gap-2">
                {producto.notas.map((nota) => (
                  <span
                    key={nota}
                    className="text-sm rounded-full px-2 py-1 bg-orange-50 text-neutral-700"
                  >
                    {nota}
                  </span>
                ))}
              </div>
            </div>
          )}
          <p className="mt-6 text-sm font-semibold text-neutral-600">
            {producto.stock === 0
              ? "Agotado"
              : `${producto.stock} ${producto.stock === 1 ? "unidad" : "unidades"} disponibles`}
          </p>
        </div>
      </div>
    </div>
  );
}
```

✅ **Mini-verificación (la regla de stock, en vivo):** en el catálogo, abre la
ficha de **Rosa de Río** (`florales-03`, stock 2): junto al badge de familia
aparece el ámbar **"¡Últimas 2 unidades!"** y abajo "2 unidades disponibles".
Compara con **Brisa de Naranja** (stock 14): badge verde "Disponible".
Verifica también el volver: filtra el catálogo por "Florales", entra a una
ficha y clic en "← Volver al catálogo" — regresas AL CATÁLOGO FILTRADO. Y el
404 propio: abre **http://localhost:5173/productos/999** → "Producto no
encontrado", "Puede que el enlace esté viejo." y el link al catálogo (distinto
del error de red: apaga el backend y verás el otro).

---

## Paso 8 — ✅ Verificación de la guía 4 (la tienda, de punta a punta)

Con los dos servidores corriendo (backend en `backend/`, frontend en
`frontend/`):

1. **http://localhost:5173/** → la landing de Maura — y sus links
   "Ver aromas →" ahora SÍ filtran al llegar al catálogo.
2. **http://localhost:5173/productos** → los 12 aromas con sus fotos,
   filtrables por familia y rango de precio, con contador y estados completos
   (STORE-02).
3. **http://localhost:5173/productos/1** → la ficha completa: badges, precio
   CLP, descripción, "Notas aromáticas" como chips y disponibilidad
   (STORE-03).

---

## ✅ Gran verificación final de la fase 1

La tabla de cierre del ciclo — como en el proyecto hermano, cada fila cita su
origen y se marca solo si TÚ la comprobaste:

| # | Verificación | Origen |
|---|---|---|
| 1 | Landing de marca: eyebrow, tagline "Frescura que te acompaña", párrafo de Maura, CTA "Ver catálogo", cuatro familias con links que filtran | RF-01, D-04 |
| 2 | Grilla con 12 aromas: foto, badge de familia, nombre, precio CLP `$6.990`–`$12.990`; contador "12 aromas" | RF-02, RN-02, HU-01 |
| 3 | Filtro por familia: "Cítricas" → 3 aromas, URL `?familia=citricas`, contador actualizado; la URL copiada a otra pestaña llega filtrada | RF-03, CS1, HU-02 |
| 4 | Filtros combinados: familia "Dulces" + rango 10000–11000 → solo los dulces del rango | RF-03, CS1 |
| 5 | Ficha completa: imagen, badges, descripción, "Notas aromáticas" como chips, "N unidades disponibles" | RF-04, CS2, HU-03 |
| 6 | Ficha con stock bajo (Rosa de Río): badge ámbar "¡Últimas 2 unidades!" | RF-04, CS2 |
| 7 | Ficha inexistente (`/productos/999`): "Producto no encontrado" + volver al catálogo | RF-04, HU-03 |
| 8 | API: `?familia=vinagre` → 422 (validación declarativa: nadie escribió el if) | RN-01, ADR-007 |
| 9 | Siembra re-ejecutada: doce `[=]`, el total sigue en 12 (restauración canónica) | RF-05, CS3, HU-04 |
| 10 | Con el backend detenido: catálogo en error controlado con "Reintentar" — y revive al reintentar | §4.1 del diseño (estados) |
| 11 | **Contrato ↔ `/docs`**: abre `http://localhost:8000/docs` y compara UNO A UNO contra `docs/04_arquitectura/contrato_api.yaml`: los 3 paths (`/api/salud`, `/api/productos`, `/api/productos/{producto_id}`), sus parámetros (`familia` con sus 4 valores, `precio_min`/`precio_max` ≥ 0, `producto_id`), los códigos de respuesta (200, 404, 422) y los schemas (`ProductoResumen` con 6 campos, `ProductoDetalle` con 9) | ADR-007, GUIDE-02 |

La fila 11 es la evidencia formal del cierre: **cualquier diferencia entre el
panel y el contrato es un desvío** — o el código corrige, o el contrato se
versiona y se aprueba de nuevo; jamás cambia en silencio. El contrato vive en
el repositorio de la guía; el `/docs` vive en tu máquina — compararlos es tu
trabajo de cierre, y este mismo mecanismo se repite al final de cada fase del
proyecto.

**Sugerencia de commit para cerrar la fase** (en TU proyecto):

```
git add -A
git commit -m "Fase 1 completa: catálogo de punta a punta según guías 1-4

Cumple el contrato OpenAPI (verificación /docs contra contrato_api.yaml sin
desvíos) y respeta los 8 ADRs de la fase 4."
```

---

## 📝 Punto de control (respóndelas sin mirar la guía)

1. ¿Quién produce el 422 y quién el 404 — y por qué viven en capas distintas?
   ¿Qué parte de la firma del endpoint declara cada regla?
2. Nombra tres comportamientos que funcionan porque los filtros viven en la
   dirección y no en un `useState`.
3. Si mañana el contrato renombra `precio_min` a `precio_desde`: ¿qué archivos
   cambian, en qué orden — y quién te avisa del desvío si te olvidas de
   alguno?

## Lo que acabas de aprender

- Schemas Pydantic como implementación del contrato (ADR-007), separados del ORM por una razón concreta
- Repositorio con `select` parameterizado y filtros componibles — inyección SQL imposible por construcción
- Servicio (casos de uso, sin HTTP) + router (frontera declarativa: Enum y `ge=0` → 422 automático; `responses` del decorator para que `/docs` documente el 404 del contrato)
- Fotos locales en `public/products/` nombradas por sku (RN-03) — cero hotlinks, demo autónomo
- Filtros en URL search params: compartibles, back/forward, recargables — y caché por combinación en TanStack Query
- Los cuatro estados async uniformes y el contador con plural correcto
- La ficha completa: regla de stock como componente, notas como chips, `navigate(-1)` que preserva filtros y el 404 distinguido con `ApiError`
- La verificación de cierre de fase: contrato ↔ `/docs`, el mecanismo que detecta el drift (GUIDE-02)

**Siguiente:** guia-05-cuentas-backend.md — las cuentas: el registro, el login
que emite un JWT de larga vida y el primer rol admin. El catálogo que acabas
de terminar es el cimiento que la fase 2 extiende: clientas con JWT, el carro
que guarda tus aromas y las órdenes que un día descontarán stock.
