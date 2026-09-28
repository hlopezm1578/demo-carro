"""Seed idempotente del catálogo demo (STORE-04).

Uso (agnóstico de terminal, D-12):

    uv run python -m app.seed

Upsert por SKU (Pitfall 6): si el producto no existe se crea ("[+]");
si ya existe se actualiza campo a campo al valor canónico ("[="). La
re-ejecución converge siempre al estado demo sin duplicar filas ni resetear
IDs. Prohibido el patrón DELETE FROM + reinsert: rompería las FK de
order_items de la fase 3 y reiniciaría los IDs.
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
# ADMN-02) y ninguno en 0 (la ficha siempre muestra disponibilidad).
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
