"""Páginas HTML: lista de órdenes y formulario para crear una."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from ..repository_sql import SqlOrderRepository, get_repo
from ..schemas import OrderIn, OrderStatus
from ..services.clientes import ClientesService, ServicioNoDisponible, get_clientes_service

router = APIRouter(prefix="/web", tags=["Páginas web"], include_in_schema=False)
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

Repo = Annotated[SqlOrderRepository, Depends(get_repo)]
Clientes = Annotated[ClientesService, Depends(get_clientes_service)]


def _formulario(request: Request, clientes: ClientesService, datos, errores, status_code=200):
    """Muestra el formulario. Si el servicio externo falla, usa un campo de texto."""
    try:
        nombres = clientes.listar_nombres()
        aviso = None
    except ServicioNoDisponible:
        nombres = []
        aviso = "El servicio de clientes no responde: escribe el nombre a mano."
    contexto = {"clientes": nombres, "aviso": aviso, "datos": datos, "errores": errores}
    return templates.TemplateResponse(
        request, "nueva_orden.html", contexto, status_code=status_code
    )


@router.get("/ordenes", response_class=HTMLResponse)
def lista_ordenes(request: Request, repo: Repo, estado: str = ""):
    # Reto: filtro por estado. "" (Todas) no filtra; un valor inválido también muestra todas.
    filtro = OrderStatus(estado) if estado in [e.value for e in OrderStatus] else None
    contexto = {"ordenes": repo.list(filtro), "estados": list(OrderStatus), "estado": estado}
    return templates.TemplateResponse(request, "ordenes.html", contexto)


@router.get("/ordenes/nueva", response_class=HTMLResponse)
def formulario_orden(request: Request, clientes: Clientes):
    return _formulario(request, clientes, datos={}, errores={})


@router.post("/ordenes/nueva", response_class=HTMLResponse)
def crear_orden_desde_formulario(
    request: Request,
    repo: Repo,
    clientes: Clientes,
    cliente: Annotated[str, Form()] = "",
    producto: Annotated[str, Form()] = "",
    cantidad: Annotated[str, Form()] = "",
    precio_unitario: Annotated[str, Form()] = "",
):
    datos = {
        "cliente": cliente,
        "producto": producto,
        "cantidad": cantidad,
        "precio_unitario": precio_unitario,
    }
    try:
        orden = OrderIn(**datos)  # el mismo esquema que valida la API
    except ValidationError as error:
        errores = {e["loc"][0]: e["msg"] for e in error.errors()}
        return _formulario(request, clientes, datos, errores, status_code=422)
    repo.add(orden)
    # Patrón PRG (Post/Redirect/Get): tras guardar, redirige para no duplicar al recargar
    return RedirectResponse("/web/ordenes", status_code=303)
