"""Fixtures compartidas: cada prueba usa una base SQLite nueva en memoria."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_session
from app.main import app
from app.services.clientes import ServicioNoDisponible, get_clientes_service


class ClientesFalso:
    """Sustituye al servicio externo: las pruebas no dependen de internet."""

    def __init__(self, nombres: list[str]) -> None:
        self.nombres = nombres
        self.falla = False

    def listar_nombres(self) -> list[str]:
        if self.falla:
            raise ServicioNoDisponible("sin conexión")
        return self.nombres


@pytest.fixture
def clientes():
    return ClientesFalso(["Ana López", "Luis Pérez"])


@pytest.fixture
def sesiones():
    # "sqlite://" = base en memoria; StaticPool la comparte entre hilos de la prueba
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine, expire_on_commit=False)
    engine.dispose()


@pytest.fixture
def client(clientes, sesiones):
    def get_session_de_prueba():
        with sesiones() as session:
            yield session

    app.dependency_overrides[get_session] = get_session_de_prueba
    app.dependency_overrides[get_clientes_service] = lambda: clientes
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()