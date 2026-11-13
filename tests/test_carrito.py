"""Pruebas del carrito guardado en la sesión."""

from fastapi.testclient import TestClient

from app.main import app

TECLADO = {"producto": "Teclado", "cantidad": "2", "precio_unitario": "350"}
MOUSE = {"producto": "Mouse", "cantidad": "1", "precio_unitario": "150"}


def test_agregar_productos_y_ver_el_total(client):
    client.post("/web/carrito/agregar", data=TECLADO)
    client.post("/web/carrito/agregar", data=MOUSE)
    r = client.get("/web/carrito")
    assert "Teclado" in r.text and "Mouse" in r.text
    assert "$850.00" in r.text
    assert "sesion_tienda" in client.cookies  # el carrito viaja en esta cookie


def test_producto_invalido_no_entra_al_carrito(client):
    r = client.post("/web/carrito/agregar", data={**TECLADO, "cantidad": "0"})
    assert r.status_code == 422
    assert "Tu carrito está vacío" in r.text


def test_confirmar_crea_una_orden_por_producto_y_vacia_el_carrito(client):
    client.post("/web/carrito/agregar", data=TECLADO)
    client.post("/web/carrito/agregar", data=MOUSE)
    r = client.post("/web/carrito/confirmar", data={"cliente": "Ana López"}, follow_redirects=False)
    assert r.status_code == 303
    ordenes = client.get("/orders").json()
    assert [(o["producto"], o["total"]) for o in ordenes] == [("Teclado", 700.0), ("Mouse", 150.0)]
    assert "Tu carrito está vacío" in client.get("/web/carrito").text


def test_cada_navegador_tiene_su_propio_carrito(client):
    client.post("/web/carrito/agregar", data=TECLADO)
    with TestClient(app) as otro_navegador:  # sin la cookie del primero
        assert "Tu carrito está vacío" in otro_navegador.get("/web/carrito").text
    assert "Teclado" in client.get("/web/carrito").text


def test_una_cookie_alterada_se_ignora(client):
    client.post("/web/carrito/agregar", data=TECLADO)
    client.cookies.set("sesion_tienda", "datos-inventados-por-un-atacante")
    assert "Tu carrito está vacío" in client.get("/web/carrito").text
