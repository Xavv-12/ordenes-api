"""Pruebas del cliente HTTP con respuestas simuladas (httpx.MockTransport)."""

import httpx
import pytest

from app.services.clientes import ClientesService, ServicioNoDisponible


def servicio_con(handler) -> ClientesService:
    transporte = httpx.MockTransport(handler)
    return ClientesService(httpx.Client(base_url="https://ejemplo.test", transport=transporte))


def test_devuelve_nombres_ordenados():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/users"
        return httpx.Response(200, json=[{"name": "Zoe"}, {"name": "Ana"}])

    assert servicio_con(handler).listar_nombres() == ["Ana", "Zoe"]


def test_error_500_se_convierte_en_servicio_no_disponible():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    with pytest.raises(ServicioNoDisponible):
        servicio_con(handler).listar_nombres()


def test_timeout_se_convierte_en_servicio_no_disponible():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("el servidor tardó demasiado", request=request)

    with pytest.raises(ServicioNoDisponible):
        servicio_con(handler).listar_nombres()
