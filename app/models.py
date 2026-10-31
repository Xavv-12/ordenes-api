"""Modelos de SQLAlchemy: cada clase es una tabla."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente: Mapped[str] = mapped_column(String(80))
    producto: Mapped[str] = mapped_column(String(120))
    cantidad: Mapped[int]
    precio_unitario: Mapped[float]
    total: Mapped[float]
    status: Mapped[str] = mapped_column(String(20), default="pendiente")
    creada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
