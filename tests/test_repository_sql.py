"""Pruebas directas del repositorio SQL, sin pasar por HTTP."""

from app.models import OrderModel
from app.repository_sql import SqlOrderRepository
from app.schemas import OrderIn, OrderStatus

ORDEN = OrderIn(cliente="Ana López", producto="Teclado", cantidad=2, precio_unitario=350.0)


def test_los_datos_sobreviven_a_la_sesion(sesiones):
    with sesiones() as session:
        creada = SqlOrderRepository(session).add(ORDEN)

    with sesiones() as otra_session:  # una sesión nueva, como otra petición
        leida = SqlOrderRepository(otra_session).get(creada.id)

    assert leida is not None
    assert leida.total == 700.0
    assert leida.status == OrderStatus.pendiente


def test_filtra_por_estado_en_la_consulta(sesiones):
    with sesiones() as session:
        repo = SqlOrderRepository(session)
        repo.add(ORDEN)
        segunda = repo.add(ORDEN)
        session.get(OrderModel, segunda.id).status = "pagada"
        session.commit()

        pagadas = repo.list(OrderStatus.pagada)

    assert [o.id for o in pagadas] == [segunda.id]