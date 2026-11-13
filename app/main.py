"""Práctica 2 · API de Órdenes con FastAPI y Pydantic."""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from .routers import carrito, comprobantes, orders, web

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("API de Órdenes iniciada")
    yield
    logger.info("API de Órdenes detenida")


app = FastAPI(title="API de Órdenes", version="0.2.0", lifespan=lifespan)
app.include_router(orders.router)
app.include_router(web.router)
app.include_router(comprobantes.router)
app.include_router(carrito.router)

# La sesión se guarda en una cookie firmada con esta clave: si alguien la modifica,
# la firma no coincide y se descarta. En producción la clave viene de una variable de entorno.
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SECRET_KEY", "solo-para-desarrollo-cambiar"),
    session_cookie="sesion_tienda",
    max_age=60 * 60 * 2,  # la sesión dura 2 horas
    same_site="lax",
    https_only=False,  # en producción, True (solo por HTTPS)
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
