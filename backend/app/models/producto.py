"""Modelo Producto y enum FamiliaAromatica (tabla `productos`)."""

import enum

from sqlalchemy import JSON, Boolean, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FamiliaAromatica(str, enum.Enum):
    """Familia aromática del catálogo (D-05: Cítricas, Florales, Frutales, Dulces).

    SQLAlchemy persiste los NOMBRES de los miembros (Pitfall 4), por eso cada
    miembro se declara con nombre == valor: la BD guarda "citricas" y la API
    devuelve ese mismo slug ASCII sin acentos (Pitfall 5). La SPA mapea el
    slug a la etiqueta con tilde ("Cítricas").
    """

    citricas = "citricas"
    florales = "florales"
    frutales = "frutales"
    dulces = "dulces"


class Producto(Base):
    """Un body splash del catálogo. Precio en CLP entero, notas como lista JSON."""

    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120))
    descripcion: Mapped[str] = mapped_column(Text)
    precio: Mapped[int] = mapped_column(Integer)  # CLP entero, sin decimales
    stock: Mapped[int] = mapped_column(Integer, default=0)
    familia: Mapped[FamiliaAromatica] = mapped_column(Enum(FamiliaAromatica))
    notas: Mapped[list[str]] = mapped_column(JSON, default=list)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    imagen: Mapped[str] = mapped_column(String(200))  # "/products/{sku}.jpg" (D-08)

    def __repr__(self) -> str:
        return f"<Producto {self.sku} {self.nombre!r}>"
