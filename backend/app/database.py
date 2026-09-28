"""Infraestructura de base de datos: engine, sesión por request y Base.

La sesión vive exactamente una request (get_session con try/finally), y las
capas superiores la reciben inyectada por FastAPI — nunca la crean.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # SQLite + hilos de FastAPI
)

# expire_on_commit=False: los objetos siguen legibles después de un commit
# (las fases 2+ commitean en services y leen atributos después).
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base declarativa de todos los modelos SQLAlchemy."""


def get_session() -> Generator[Session, None, None]:
    """Dependencia de FastAPI: una sesión por request, cerrada siempre."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
