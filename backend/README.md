# Backend — Maura API

API FastAPI en capas (routers → services → repositories) de la tienda
Maura · Body Splash. Manejado con uv (D-10).

```bash
uv add "fastapi[standard]" sqlalchemy pydantic-settings  # dependencias
uv run python -m app.seed                                 # sembrar el catálogo demo
uv run fastapi dev app/main.py                            # levantar en :8000
```
