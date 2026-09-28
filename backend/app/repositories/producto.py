"""Acceso a datos de Producto: select parameterizado con filtros componibles.

Es la ÚNICA capa (además de models/ y database.py) que importa select de
sqlalchemy — regla de dependencia verificable de la arquitectura en capas.
Jamás strings SQL concatenadas: la consulta es parameterizada por
construcción (SQLi imposible).
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
