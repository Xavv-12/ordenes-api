"""Pruebas de las páginas HTML y del formulario."""

FORMULARIO = {
    "cliente": "Ana López",
    "producto": "Teclado",
    "cantidad": "2",
    "precio_unitario": "350",
}


def test_formulario_muestra_clientes_del_servicio(client):
    r = client.get("/web/ordenes/nueva")
    assert r.status_code == 200
    assert "<select" in r.text
    assert "Luis Pérez" in r.text


def test_formulario_funciona_aunque_el_servicio_falle(client, clientes):
    clientes.falla = True
    r = client.get("/web/ordenes/nueva")
    assert r.status_code == 200
    assert "no responde" in r.text
    assert "<select" not in r.text


def test_post_valido_guarda_y_redirige(client):
    r = client.post("/web/ordenes/nueva", data=FORMULARIO, follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/web/ordenes"
    ordenes = client.get("/orders").json()
    assert len(ordenes) == 1
    assert ordenes[0]["total"] == 700.0


def test_post_invalido_muestra_errores_y_no_guarda(client):
    r = client.post("/web/ordenes/nueva", data={**FORMULARIO, "cantidad": "0"})
    assert r.status_code == 422
    assert "greater than 0" in r.text
    assert client.get("/orders").json() == []


def test_lista_muestra_las_ordenes(client):
    client.post("/web/ordenes/nueva", data=FORMULARIO)
    r = client.get("/web/ordenes")
    assert r.status_code == 200
    assert "Teclado" in r.text
    assert "$700.00" in r.text
