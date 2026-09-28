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
