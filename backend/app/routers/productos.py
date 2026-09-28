"""Endpoints públicos del catálogo (GET, solo JSON — dos tiers estrictos).

El router valida la frontera HTTP (query params declarativos: Enum y ge=0
producen el 422 del contrato sin código manual) y delega en CatalogService.
Nunca importa SQLAlchemy: la sesión llega inyectada desde app.database.
"""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.database import Session, get_session
from app.models.producto import FamiliaAromatica
from app.repositories.producto import ProductoRepository
from app.schemas.producto import ProductoDetalle, ProductoResumen
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


@router.get("/{producto_id}", response_model=ProductoDetalle)
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
