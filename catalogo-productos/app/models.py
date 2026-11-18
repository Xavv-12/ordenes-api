"""Modelo de la tabla productos."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class ProductoModel(Base):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(7), unique=True)
    nombre: Mapped[str] = mapped_column(String(80))
    precio: Mapped[float]
    existencias: Mapped[int]
    categoria: Mapped[str] = mapped_column(String(20))
    imagen: Mapped[str | None] = mapped_column(String(255), default=None)

    @property
    def disponible(self) -> bool:
        return self.existencias > 0
