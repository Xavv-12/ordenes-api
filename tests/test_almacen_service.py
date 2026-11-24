"""Pruebas del cliente SOAP con respuestas simuladas (httpx.MockTransport)."""

import httpx
import pytest

from app.services.almacen import SOAP_ACTION, AlmacenService, ProductoNoRegistrado
from app.services.clientes import ServicioNoDisponible

RESPUESTA_OK = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:alm="http://utvt.edu.mx/almacen">
  <soap:Body>
    <alm:ConsultarExistenciaResponse>
      <alm:producto>Teclado</alm:producto>
      <alm:existencia>15</alm:existencia>
    </alm:ConsultarExistenciaResponse>
  </soap:Body>
</soap:Envelope>"""


def falla(codigo: str) -> str:
    return f"""<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body><soap:Fault>
    <faultcode>soap:{codigo}</faultcode><faultstring>Producto no registrado: Silla</faultstring>
  </soap:Fault></soap:Body></soap:Envelope>"""


def servicio_que_responde(manejador) -> AlmacenService:
    return AlmacenService(client=httpx.Client(transport=httpx.MockTransport(manejador)))


def test_arma_el_sobre_soap_y_lee_la_existencia():
    recibido = {}

    def manejador(request: httpx.Request) -> httpx.Response:
        recibido["metodo"] = request.method
        recibido["accion"] = request.headers["SOAPAction"]
        recibido["tipo"] = request.headers["Content-Type"]
        recibido["cuerpo"] = request.content.decode()
        return httpx.Response(200, text=RESPUESTA_OK)

    assert servicio_que_responde(manejador).consultar_existencia("Teclado") == 15
    assert recibido["metodo"] == "POST"  # SOAP siempre viaja en POST
    assert recibido["accion"] == f'"{SOAP_ACTION}"'
    assert recibido["tipo"].startswith("text/xml")
    assert "<alm:producto>Teclado</alm:producto>" in recibido["cuerpo"]


def test_fault_client_significa_producto_no_registrado():
    servicio = servicio_que_responde(lambda r: httpx.Response(500, text=falla("Client")))
    with pytest.raises(ProductoNoRegistrado):
        servicio.consultar_existencia("Silla")


def test_fault_server_significa_servicio_no_disponible():
    servicio = servicio_que_responde(lambda r: httpx.Response(500, text=falla("Server")))
    with pytest.raises(ServicioNoDisponible):
        servicio.consultar_existencia("Teclado")


def test_timeout_significa_servicio_no_disponible():
    def manejador(request):
        raise httpx.ReadTimeout("tardó demasiado", request=request)

    with pytest.raises(ServicioNoDisponible):
        servicio_que_responde(manejador).consultar_existencia("Teclado")


def test_respuesta_que_no_es_xml_significa_servicio_no_disponible():
    servicio = servicio_que_responde(lambda r: httpx.Response(502, text="<html>Bad Gateway"))
    with pytest.raises(ServicioNoDisponible):
        servicio.consultar_existencia("Teclado")


def test_el_nombre_del_producto_se_escapa():
    recibido = {}

    def manejador(request):
        recibido["cuerpo"] = request.content.decode()
        return httpx.Response(200, text=RESPUESTA_OK)

    servicio_que_responde(manejador).consultar_existencia("<b>Teclado & Mouse</b>")
    assert "&lt;b&gt;Teclado &amp; Mouse&lt;/b&gt;" in recibido["cuerpo"]
