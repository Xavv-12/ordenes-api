"""Carrito de compras guardado en la sesión del usuario (cookie firmada)."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, ValidationError

from ..repository_sql import SqlOrderRepository, get_repo
from ..schemas import OrderIn

router = APIRouter(prefix="/web/carrito", include_in_schema=False)
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

Repo = Annotated[SqlOrderRepository, Depends(get_repo)]


class ItemCarrito(BaseModel):
    producto: str = Field(min_length=1, max_length=120)
    cantidad: int = Field(gt=0, le=100)
    precio_unitario: float = Field(gt=0)


def leer_carrito(request: Request) -> list[dict]:
    # request.session funciona como un diccionario; vive en una cookie del navegador
    return request.session.get("carrito", [])


def _pagina(request: Request, errores: dict, status_code: int = 200):
    carrito = leer_carrito(request)
    total = sum(item["cantidad"] * item["precio_unitario"] for item in carrito)
    contexto = {"carrito": carrito, "total": total, "errores": errores}
    return templates.TemplateResponse(request, "carrito.html", contexto, status_code=status_code)


@router.get("", response_class=HTMLResponse)
def ver_carrito(request: Request):
    return _pagina(request, errores={})


@router.post("/agregar", response_class=HTMLResponse)
def agregar_al_carrito(
    request: Request,
    producto: Annotated[str, Form()] = "",
    cantidad: Annotated[str, Form()] = "",
    precio_unitario: Annotated[str, Form()] = "",
):
    try:
        item = ItemCarrito(producto=producto, cantidad=cantidad, precio_unitario=precio_unitario)
    except ValidationError as error:
        errores = {e["loc"][0]: e["msg"] for e in error.errors()}
        return _pagina(request, errores, status_code=422)
    carrito = leer_carrito(request)
    carrito.append(item.model_dump())
    request.session["carrito"] = carrito  # se reescribe la cookie en la respuesta
    return RedirectResponse("/web/carrito", status_code=303)


@router.post("/vaciar")
def vaciar_carrito(request: Request):
    request.session.pop("carrito", None)
    return RedirectResponse("/web/carrito", status_code=303)


@router.post("/confirmar", response_class=HTMLResponse)
def confirmar_compra(request: Request, repo: Repo, cliente: Annotated[str, Form()] = ""):
    carrito = leer_carrito(request)
    if not carrito:
        return _pagina(request, {"general": "El carrito está vacío"}, status_code=422)
    try:
        ordenes = [OrderIn(cliente=cliente, **item) for item in carrito]
    except ValidationError as error:
        errores = {e["loc"][0]: e["msg"] for e in error.errors()}
        return _pagina(request, errores, status_code=422)
    for orden in ordenes:  # una orden por cada producto del carrito
        repo.add(orden)
    request.session.pop("carrito", None)
    return RedirectResponse("/web/ordenes", status_code=303)
