"""Opcional: el mismo servicio consumido con zeep, la librería SOAP más usada en Python.

zeep lee el WSDL y crea las operaciones por ti: no escribes XML.
    pip install zeep
    python ejemplos/consumir_con_zeep.py   (con el almacén corriendo en el puerto 8001)
"""

from zeep import Client
from zeep.exceptions import Fault

cliente = Client("http://127.0.0.1:8001/almacen?wsdl")
print(cliente.service.ConsultarExistencia(producto="Mouse"))

try:
    cliente.service.ConsultarExistencia(producto="Silla")
except Fault as falla:
    print("El almacén respondió con un Fault:", falla.message)
