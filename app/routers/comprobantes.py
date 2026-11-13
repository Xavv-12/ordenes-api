"""Subir, listar y descargar los comprobantes de pago de una orden."""

from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from ..repository_sql import SqlOrderRepository, get_repo
from ..schemas import ComprobanteOut
from ..storage import TAMANO_MAXIMO, detectar_tipo, get_upload_dir

router = APIRouter(tags=["Comprobantes"])

Repo = Annotated[SqlOrderRepository, Depends(get_repo)]
Carpeta = Annotated[Path, Depends(get_upload_dir)]


@router.post(
    "/orders/{order_id}/comprobantes",
    response_model=ComprobanteOut,
    status_code=status.HTTP_201_CREATED,
)
def subir_comprobante(
    order_id: int, archivo: UploadFile, repo: Repo, carpeta: Carpeta
) -> ComprobanteOut:
    if repo.get(order_id) is None:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    # 1. Tamaño: leemos como máximo 1 byte más del límite para saber si se pasa
    contenido = archivo.file.read(TAMANO_MAXIMO + 1)
    if len(contenido) > TAMANO_MAXIMO:
        raise HTTPException(status_code=413, detail="El archivo supera 2 MB")

    # 2. Tipo real, según el contenido y no según el nombre
    tipo = detectar_tipo(contenido)
    if tipo is None:
        raise HTTPException(status_code=415, detail="Solo se aceptan PDF, PNG o JPEG")
    mime, extension = tipo

    # 3. Nombre nuevo y aleatorio: nunca usamos el nombre que manda el usuario como ruta
    destino = carpeta / f"{uuid4().hex}{extension}"
    destino.write_bytes(contenido)

    return repo.agregar_comprobante(
        order_id,
        nombre_original=archivo.filename or "comprobante",
        ruta=str(destino),
        tipo=mime,
        tamano=len(contenido),
    )


@router.get("/orders/{order_id}/comprobantes", response_model=list[ComprobanteOut])
def listar_comprobantes(order_id: int, repo: Repo) -> list[ComprobanteOut]:
    comprobantes = repo.listar_comprobantes(order_id)
    if comprobantes is None:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return comprobantes


@router.get("/comprobantes/{comprobante_id}/descarga")
def descargar_comprobante(comprobante_id: int, repo: Repo) -> FileResponse:
    comprobante = repo.get_comprobante(comprobante_id)
    if comprobante is None or not Path(comprobante.ruta).exists():
        raise HTTPException(status_code=404, detail="Comprobante no encontrado")
    # filename= hace que el navegador lo descargue con su nombre original
    return FileResponse(
        comprobante.ruta, media_type=comprobante.tipo, filename=comprobante.nombre_original
    )
