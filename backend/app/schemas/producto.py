"""Schemas Pydantic del catálogo — espejan docs/04_arquitectura/contrato_api.yaml.

El contrato se aprobó ANTES que este código (D-15, API-first): estos schemas
lo implementan, no lo inventan. Mantener separado de models/ para que el
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
