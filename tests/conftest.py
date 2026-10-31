"""Fixtures compartidas por todas las pruebas."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repository import OrderRepository, get_repo
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
def client(clientes):
    repo = OrderRepository()
    app.dependency_overrides[get_repo] = lambda: repo
    app.dependency_overrides[get_clientes_service] = lambda: clientes
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
