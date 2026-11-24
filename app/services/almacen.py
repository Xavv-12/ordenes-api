"""Cliente SOAP del sistema de almacén.

SOAP no es más que XML enviado por HTTP POST: armamos el sobre (Envelope) a mano,
lo enviamos con httpx y leemos la respuesta con ElementTree.
"""

import os
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

import httpx

from .clientes import ServicioNoDisponible

URL_ALMACEN = os.environ.get("ALMACEN_URL", "http://127.0.0.1:8001/almacen")
NS_SOAP = "http://schemas.xmlsoap.org/soap/envelope/"
NS_ALM = "http://utvt.edu.mx/almacen"
SOAP_ACTION = "http://utvt.edu.mx/almacen/ConsultarExistencia"

SOBRE = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="{ns_soap}" xmlns:alm="{ns_alm}">
  <soap:Body>
    <alm:ConsultarExistencia>
      <alm:producto>{producto}</alm:producto>
    </alm:ConsultarExistencia>
  </soap:Body>
</soap:Envelope>"""


class ProductoNoRegistrado(Exception):
    """El almacén respondió con un Fault de tipo Client: el producto no existe."""


class AlmacenService:
    def __init__(self, client: httpx.Client | None = None) -> None:
        self._client = client or httpx.Client(timeout=3.0, transport=httpx.HTTPTransport(retries=2))

    def consultar_existencia(self, producto: str) -> int:
        # escape() convierte < > & en texto: así nadie puede inyectar XML en el sobre
        sobre = SOBRE.format(ns_soap=NS_SOAP, ns_alm=NS_ALM, producto=escape(producto))
        encabezados = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": f'"{SOAP_ACTION}"',  # SOAP 1.1 lo pide entre comillas
        }
        try:
            respuesta = self._client.post(URL_ALMACEN, content=sobre, headers=encabezados)
            raiz = ET.fromstring(respuesta.content)
        except (httpx.HTTPError, ET.ParseError) as error:
            raise ServicioNoDisponible(str(error)) from error

        falla = raiz.find(f".//{{{NS_SOAP}}}Fault")
        if falla is not None:
            codigo = falla.findtext("faultcode", default="")
            mensaje = falla.findtext("faultstring", default="Error del almacén")
            if codigo.endswith("Client"):
                raise ProductoNoRegistrado(mensaje)
            raise ServicioNoDisponible(mensaje)

        existencia = raiz.findtext(f".//{{{NS_ALM}}}existencia")
        if respuesta.status_code != 200 or existencia is None:
            raise ServicioNoDisponible(f"Respuesta inesperada ({respuesta.status_code})")
        return int(existencia)


servicio = AlmacenService()


def get_almacen_service() -> AlmacenService:
    return servicio
