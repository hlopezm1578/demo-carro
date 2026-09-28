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


# Datos demo canónicos (Task 3 completa las 4 familias x 3 productos, D-06).
PRODUCTOS_DEMO: list[dict] = [
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
