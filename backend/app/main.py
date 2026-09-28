"""Composición de la aplicación FastAPI.

Solo este archivo arma la app (regla de la arquitectura en capas): crea la
instancia, agrega middlewares y registra los routers con sus prefijos /api.
No contiene lógica de negocio.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import productos, salud

app = FastAPI(
    title="Maura API",
    version="0.1.0",
    description=(
        "API del catálogo de la tienda Maura · Body Splash. Tier servidor de "
        "los dos tiers: solo JSON bajo /api, jamás plantillas HTML."
    ),
)

# CORS con orígenes EXPLÍCITOS desde settings (Pitfall 7): lista dev + prod,
# nunca una lista comodín.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(salud.router, prefix="/api/salud")
app.include_router(productos.router, prefix="/api/productos")
