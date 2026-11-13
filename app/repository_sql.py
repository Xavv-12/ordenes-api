"""Repositorio de Órdenes sobre SQLite. Misma interfaz que el repositorio en memoria."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import get_session
from .models import ComprobanteModel, OrderModel
from .schemas import ComprobanteGuardado, ComprobanteOut, OrderIn, OrderOut, OrderStatus


class SqlOrderRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, data: OrderIn) -> OrderOut:
        orden = OrderModel(
            **data.model_dump(),
            total=round(data.cantidad * data.precio_unitario, 2),
        )
        self.session.add(orden)  # INSERT pendiente
        self.session.commit()  # se confirma la transacción
        self.session.refresh(orden)  # trae id, status y creada desde la BD
        return OrderOut.model_validate(orden)

    def list(
        self, estado: OrderStatus | None = None, limit: int = 10, offset: int = 0
    ) -> list[OrderOut]:
        # TODO A: SELECT * FROM orders [WHERE status = ...] ORDER BY id
        consulta = select(OrderModel).order_by(OrderModel.id)
        if estado is not None:
            consulta = consulta.where(OrderModel.status == estado.value)
        consulta = consulta.limit(limit).offset(offset)  # paginación
        return [OrderOut.model_validate(o) for o in self.session.scalars(consulta)]

    def get(self, order_id: int) -> OrderOut | None:
        orden = self.session.get(OrderModel, order_id)
        return OrderOut.model_validate(orden) if orden else None

    def update(self, order_id: int, data: OrderIn) -> OrderOut | None:
        # TODO B: UPDATE orders SET ... WHERE id = ...
        orden = self.session.get(OrderModel, order_id)
        if orden is None:
            return None
        for campo, valor in data.model_dump().items():
            setattr(orden, campo, valor)
        orden.total = round(data.cantidad * data.precio_unitario, 2)
        self.session.commit()
        self.session.refresh(orden)
        return OrderOut.model_validate(orden)

    def delete(self, order_id: int) -> bool:
        # TODO C: DELETE FROM orders WHERE id = ...
        orden = self.session.get(OrderModel, order_id)
        if orden is None:
            return False
        self.session.delete(orden)
        self.session.commit()
        return True

    # --- Relación orden -> comprobantes ------------------------------------
    def agregar_comprobante(
        self, order_id: int, nombre_original: str, ruta: str, tipo: str, tamano: int
    ) -> ComprobanteOut | None:
        orden = self.session.get(OrderModel, order_id)
        if orden is None:
            return None
        comprobante = ComprobanteModel(
            nombre_original=nombre_original, ruta=ruta, tipo=tipo, tamano=tamano
        )
        orden.comprobantes.append(comprobante)  # SQLAlchemy llena order_id por nosotros
        self.session.commit()
        self.session.refresh(comprobante)
        return ComprobanteOut.model_validate(comprobante)

    def listar_comprobantes(self, order_id: int) -> list[ComprobanteOut] | None:
        orden = self.session.get(OrderModel, order_id)
        if orden is None:
            return None
        return [ComprobanteOut.model_validate(c) for c in orden.comprobantes]

    def get_comprobante(self, comprobante_id: int) -> ComprobanteGuardado | None:
        comprobante = self.session.get(ComprobanteModel, comprobante_id)
        return ComprobanteGuardado.model_validate(comprobante) if comprobante else None


def get_repo(session: Annotated[Session, Depends(get_session)]) -> SqlOrderRepository:
    """Dependencia: FastAPI primero obtiene la sesión y luego crea el repositorio."""
    return SqlOrderRepository(session)
