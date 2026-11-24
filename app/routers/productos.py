"""Adaptador: la tienda expone en REST/JSON lo que el almacén ofrece en SOAP/XML.

Quien use la API de la tienda (una app móvil, el front end) nunca ve XML.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..services.almacen import AlmacenService, ProductoNoRegistrado, get_almacen_service
from ..services.clientes import ServicioNoDisponible

router = APIRouter(prefix="/productos", tags=["Productos"])

Almacen = Annotated[AlmacenService, Depends(get_almacen_service)]


class ExistenciaOut(BaseModel):
    producto: str
    existencia: int


@router.get("/{producto}/existencia", response_model=ExistenciaOut)
def consultar_existencia(producto: str, almacen: Almacen) -> ExistenciaOut:
    try:
        existencia = almacen.consultar_existencia(producto)
    except ProductoNoRegistrado:
        raise HTTPException(status_code=404, detail="Producto no registrado") from None
    except ServicioNoDisponible:
        raise HTTPException(status_code=503, detail="Almacén no disponible") from None
    return ExistenciaOut(producto=producto, existencia=existencia)
