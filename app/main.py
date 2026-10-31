"""Práctica 2 · API de Órdenes con FastAPI y Pydantic."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import models  # noqa: F401  (registra las tablas en Base.metadata)
from .db import Base, engine
from .routers import orders, web

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)  # crea las tablas que no existan
    logger.info("API de Órdenes iniciada")
    yield
    logger.info("API de Órdenes detenida")


app = FastAPI(title="API de Órdenes", version="0.2.0", lifespan=lifespan)
app.include_router(orders.router)
app.include_router(web.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
