"""Pruebas de la paginación de GET /orders."""

ORDEN = {"cliente": "Ana López", "producto": "Teclado", "cantidad": 1, "precio_unitario": 100.0}


def crear_ordenes(client, cuantas: int) -> None:
    for _ in range(cuantas):
        client.post("/orders", json=ORDEN)


def test_por_defecto_devuelve_10(client):
    crear_ordenes(client, 12)
    assert len(client.get("/orders").json()) == 10


def test_limit_y_offset_recorren_las_paginas(client):
    crear_ordenes(client, 12)
    pagina_2 = client.get("/orders", params={"limit": 5, "offset": 5}).json()
    assert [o["id"] for o in pagina_2] == [6, 7, 8, 9, 10]
    ultima = client.get("/orders", params={"limit": 5, "offset": 10}).json()
    assert [o["id"] for o in ultima] == [11, 12]


def test_limit_fuera_de_rango_devuelve_422(client):
    assert client.get("/orders", params={"limit": 0}).status_code == 422
    assert client.get("/orders", params={"limit": 51}).status_code == 422
