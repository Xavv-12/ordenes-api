"""Pruebas de la relación uno a muchos: una orden tiene muchos comprobantes."""

from sqlalchemy import select

from app.models import ComprobanteModel, OrderModel
from app.repository_sql import SqlOrderRepository
from app.schemas import OrderIn

ORDEN = OrderIn(cliente="Ana López", producto="Teclado", cantidad=2, precio_unitario=350.0)


def test_una_orden_tiene_varios_comprobantes(sesiones):
    with sesiones() as session:
        repo = SqlOrderRepository(session)
        orden = repo.add(ORDEN)
        repo.agregar_comprobante(orden.id, "pago.pdf", "uploads/a.pdf", "application/pdf", 1200)
        repo.agregar_comprobante(orden.id, "ticket.png", "uploads/b.png", "image/png", 800)

        comprobantes = repo.listar_comprobantes(orden.id)

    assert [c.nombre_original for c in comprobantes] == ["pago.pdf", "ticket.png"]
    assert all(c.order_id == orden.id for c in comprobantes)


def test_comprobante_de_orden_inexistente_devuelve_none(sesiones):
    with sesiones() as session:
        repo = SqlOrderRepository(session)
        assert repo.agregar_comprobante(99, "x.pdf", "x", "application/pdf", 1) is None
        assert repo.listar_comprobantes(99) is None


def test_borrar_la_orden_borra_sus_comprobantes(sesiones):
    with sesiones() as session:
        repo = SqlOrderRepository(session)
        orden = repo.add(ORDEN)
        repo.agregar_comprobante(orden.id, "pago.pdf", "uploads/a.pdf", "application/pdf", 1200)
        assert repo.delete(orden.id)

        assert session.get(OrderModel, orden.id) is None
        assert session.scalars(select(ComprobanteModel)).all() == []
