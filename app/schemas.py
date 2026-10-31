"""Esquemas Pydantic: definen qué entra (OrderIn) y qué sale (OrderOut)."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class OrderStatus(str, Enum):
    pendiente = "pendiente"
    pagada = "pagada"
    cancelada = "cancelada"


class OrderIn(BaseModel):
    cliente: str = Field(min_length=3, max_length=80, examples=["Ana López"])
    producto: str = Field(min_length=1, max_length=120, examples=["Teclado"])
    cantidad: int = Field(gt=0, le=100, examples=[2])
    precio_unitario: float = Field(gt=0, examples=[350.0])


class OrderOut(OrderIn):
    model_config = ConfigDict(from_attributes=True)  # permite leer objetos del ORM

    id: int
    total: float
    status: OrderStatus
    creada: datetime
