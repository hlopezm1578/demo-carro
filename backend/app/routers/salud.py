"""Endpoint de salud: chequeo de vida del servicio."""

from fastapi import APIRouter

router = APIRouter(tags=["Operación"])


@router.get("")
def estado_del_servicio() -> dict[str, str]:
    """GET /api/salud — responde {"estado": "ok"} si el servicio está arriba."""
    return {"estado": "ok"}
