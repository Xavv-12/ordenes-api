"""Sistema de almacén "heredado": un servicio SOAP 1.1 que la tienda debe consumir.

No lo modifiques. Hace el papel del sistema de otra área de la empresa, escrito hace
años, que solo habla SOAP. Se ejecuta aparte de la tienda, en el puerto 8001:

    fastapi dev almacen_soap/main.py --port 8001

Contrato (ver almacen.wsdl):
    POST /almacen       operación ConsultarExistencia(producto) -> existencia
    GET  /almacen?wsdl  devuelve el WSDL que describe el servicio
"""

from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

from fastapi import FastAPI, Request, Response

NS_SOAP = "http://schemas.xmlsoap.org/soap/envelope/"
NS_ALM = "http://utvt.edu.mx/almacen"
WSDL = Path(__file__).with_name("almacen.wsdl")

# Inventario de ejemplo. La búsqueda no distingue mayúsculas: "teclado" = "Teclado".
EXISTENCIAS = {"teclado": 15, "mouse": 30, "monitor": 4, "laptop": 2, "audífonos": 0}

app = FastAPI(title="Almacén (SOAP)", docs_url=None, redoc_url=None, openapi_url=None)


def _sobre(cuerpo: str) -> str:
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        f'<soap:Envelope xmlns:soap="{NS_SOAP}" xmlns:alm="{NS_ALM}">'
        f"<soap:Body>{cuerpo}</soap:Body></soap:Envelope>"
    )


def _xml(contenido: str, status_code: int = 200) -> Response:
    return Response(contenido, status_code=status_code, media_type="text/xml; charset=utf-8")


def _falla(codigo: str, mensaje: str) -> Response:
    # En SOAP 1.1 los errores viajan como un <soap:Fault> con estado HTTP 500.
    # faultcode Client = el error es de quien llama; Server = el error es del servicio.
    cuerpo = (
        f"<soap:Fault><faultcode>soap:{codigo}</faultcode>"
        f"<faultstring>{escape(mensaje)}</faultstring></soap:Fault>"
    )
    return _xml(_sobre(cuerpo), status_code=500)


@app.get("/almacen")
def descargar_wsdl(request: Request) -> Response:
    if "wsdl" in request.query_params:
        return _xml(WSDL.read_text(encoding="utf-8"))
    return Response("Servicio SOAP de almacén. El contrato está en /almacen?wsdl")


@app.post("/almacen")
async def atender_operacion(request: Request) -> Response:
    try:
        raiz = ET.fromstring(await request.body())
    except ET.ParseError:
        return _falla("Client", "El mensaje no es XML válido")

    pedido = raiz.find(f"{{{NS_SOAP}}}Body/{{{NS_ALM}}}ConsultarExistencia")
    if pedido is None:
        return _falla("Client", "Operación no soportada")

    producto = (pedido.findtext(f"{{{NS_ALM}}}producto") or "").strip()
    existencia = EXISTENCIAS.get(producto.lower())
    if existencia is None:
        return _falla("Client", f"Producto no registrado: {producto}")

    respuesta = (
        "<alm:ConsultarExistenciaResponse>"
        f"<alm:producto>{escape(producto)}</alm:producto>"
        f"<alm:existencia>{existencia}</alm:existencia>"
        "</alm:ConsultarExistenciaResponse>"
    )
    return _xml(_sobre(respuesta))
