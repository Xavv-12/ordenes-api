"""Fixtures compartidas: cada prueba usa una base SQLite nueva en memoria."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_session
from app.main import app
from app.services.almacen import ProductoNoRegistrado, get_almacen_service
from app.services.clientes import ServicioNoDisponible, get_clientes_service
from app.storage import get_upload_dir


class ClientesFalso:
    """Sustituye al servicio externo: las pruebas no dependen de internet."""

    def __init__(self, nombres: list[str]) -> None:
        self.nombres = nombres
        self.falla = False

    def listar_nombres(self) -> list[str]:
        if self.falla:
            raise ServicioNoDisponible("sin conexión")
        return self.nombres


class AlmacenFalso:
    """Sustituye al almacén SOAP: las pruebas no necesitan el servicio en el puerto 8001."""

    def __init__(self, existencias: dict[str, int]) -> None:
        self.existencias = existencias
        self.falla = False

    def consultar_existencia(self, producto: str) -> int:
        if self.falla:
            raise ServicioNoDisponible("sin conexión")
        if producto not in self.existencias:
            raise ProductoNoRegistrado(producto)
        return self.existencias[producto]


@pytest.fixture
def almacen():
    return AlmacenFalso({"Teclado": 50, "Mouse": 50, "Monitor": 3})


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
def carpeta(tmp_path):
    """Carpeta temporal para los archivos subidos; pytest la borra al terminar."""
    return tmp_path


@pytest.fixture
def client(clientes, almacen, sesiones, carpeta):
    def get_session_de_prueba():
        with sesiones() as session:
            yield session

    app.dependency_overrides[get_session] = get_session_de_prueba
    app.dependency_overrides[get_clientes_service] = lambda: clientes
    app.dependency_overrides[get_upload_dir] = lambda: carpeta
    app.dependency_overrides[get_almacen_service] = lambda: almacen
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
