"""Pruebas de contrato: el cliente habla con el servicio SOAP real (sin abrir puertos).

TestClient también es un cliente de httpx, así que se lo pasamos al AlmacenService:
las peticiones llegan directo a la aplicación del almacén.
"""

import pytest
from fastapi.testclient import TestClient

from almacen_soap.main import app as almacen_app
from app.services.almacen import SOAP_ACTION, AlmacenService, ProductoNoRegistrado


@pytest.fixture
def almacen_real():
    with TestClient(almacen_app) as cliente:
        yield AlmacenService(client=cliente)


def test_consulta_un_producto_del_inventario(almacen_real):
    assert almacen_real.consultar_existencia("Teclado") == 15


def test_producto_desconocido_lanza_producto_no_registrado(almacen_real):
    with pytest.raises(ProductoNoRegistrado):
        almacen_real.consultar_existencia("Silla gamer")


def test_el_wsdl_describe_la_operacion_que_usamos():
    with TestClient(almacen_app) as cliente:
        wsdl = cliente.get("/almacen", params={"wsdl": ""}).text
    assert '<operation name="ConsultarExistencia">' in wsdl
    assert f'soapAction="{SOAP_ACTION}"' in wsdl
