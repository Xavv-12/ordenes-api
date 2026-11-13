"""Modelos de SQLAlchemy: cada clase es una tabla."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def ahora() -> datetime:
    return datetime.now(timezone.utc)


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente: Mapped[str] = mapped_column(String(80))
    producto: Mapped[str] = mapped_column(String(120))
    cantidad: Mapped[int]
    precio_unitario: Mapped[float]
    total: Mapped[float]
    status: Mapped[str] = mapped_column(String(20), default="pendiente")
    creada: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora)

    # Lado "uno" de la relación: una orden tiene muchos comprobantes.
    # cascade: si se borra la orden, se borran también sus comprobantes.
    comprobantes: Mapped[list["ComprobanteModel"]] = relationship(
        back_populates="orden", cascade="all, delete-orphan"
    )


class ComprobanteModel(Base):
    __tablename__ = "comprobantes"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Llave foránea: cada comprobante apunta a una fila de la tabla orders
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    nombre_original: Mapped[str] = mapped_column(String(255))
    ruta: Mapped[str] = mapped_column(String(255))
    tipo: Mapped[str] = mapped_column(String(50))
    tamano: Mapped[int]
    subido: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora)

    # Lado "muchos": cada comprobante pertenece a una orden
    orden: Mapped[OrderModel] = relationship(back_populates="comprobantes")
