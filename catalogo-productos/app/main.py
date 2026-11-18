"""Catálogo de Productos: imágenes, favoritos y paginación."""

import os

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from .routers import favoritos, imagenes, productos, web

# Las tablas ya no se crean aquí: las crea Alembic con "alembic upgrade head".
app = FastAPI(title="Catálogo de Productos", version="0.5.0")
app.include_router(productos.router)
app.include_router(imagenes.router)
app.include_router(web.router)
app.include_router(favoritos.router)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SECRET_KEY", "solo-para-desarrollo-cambiar"),
    session_cookie="sesion_catalogo",
    same_site="lax",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
