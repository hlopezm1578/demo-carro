"""Configuración tipada de la API.

TODO lo configurable vive en un solo lugar (D-10): pydantic-settings carga
valores por defecto de desarrollo y permite sobreescribirlos con variables
de entorno (p. ej. DATABASE_URL, CORS_ORIGINS). Los secretos jamás van en
el código.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Ajustes del backend. En producción se sobreescriben por entorno."""

    database_url: str = "sqlite:///./maura.db"
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
