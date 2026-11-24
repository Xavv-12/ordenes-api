"""El adaptador REST y el carrito usan el almacén (aquí, el AlmacenFalso de conftest.py)."""


def test_existencia_se_entrega_en_json(client):
    r = client.get("/productos/Monitor/existencia")
    assert r.status_code == 200
    assert r.json() == {"producto": "Monitor", "existencia": 3}


def test_producto_no_registrado_devuelve_404(client):
    assert client.get("/productos/Silla/existencia").status_code == 404


def test_almacen_caido_devuelve_503(client, almacen):
    almacen.falla = True
    assert client.get("/productos/Monitor/existencia").status_code == 503


def test_carrito_no_acepta_mas_de_lo_que_hay(client):
    datos = {"producto": "Monitor", "cantidad": "5", "precio_unitario": "3000"}
    r = client.post("/web/carrito/agregar", data=datos)
    assert r.status_code == 422
    assert "Solo hay 3 en existencia" in r.text


def test_carrito_no_acepta_productos_que_no_existen(client):
    datos = {"producto": "Silla", "cantidad": "1", "precio_unitario": "900"}
    r = client.post("/web/carrito/agregar", data=datos)
    assert r.status_code == 422
    assert "No existe en el almacén" in r.text


def test_carrito_avisa_si_el_almacen_no_responde(client, almacen):
    almacen.falla = True
    datos = {"producto": "Monitor", "cantidad": "1", "precio_unitario": "3000"}
    r = client.post("/web/carrito/agregar", data=datos)
    assert r.status_code == 503
    assert "intenta más tarde" in r.text
    assert "Tu carrito está vacío" in r.text
