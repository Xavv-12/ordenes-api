"""Pruebas de subida y descarga de comprobantes."""

PDF = b"%PDF-1.4\n% comprobante de prueba\n"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
ORDEN = {"cliente": "Ana López", "producto": "Teclado", "cantidad": 2, "precio_unitario": 350.0}


def crear_orden(client) -> int:
    return client.post("/orders", json=ORDEN).json()["id"]


def subir(client, order_id, nombre, contenido, tipo="application/pdf"):
    return client.post(
        f"/orders/{order_id}/comprobantes", files={"archivo": (nombre, contenido, tipo)}
    )


def test_subir_pdf_lo_guarda_con_nombre_nuevo(client, carpeta):
    order_id = crear_orden(client)
    r = subir(client, order_id, "pago.pdf", PDF)
    assert r.status_code == 201
    body = r.json()
    assert body["nombre_original"] == "pago.pdf"
    assert body["tipo"] == "application/pdf"
    assert "ruta" not in body  # la ruta interna nunca se expone
    guardados = list(carpeta.iterdir())
    assert len(guardados) == 1
    assert guardados[0].name != "pago.pdf"  # se renombró
    assert guardados[0].read_bytes() == PDF


def test_el_tipo_se_revisa_por_contenido_no_por_nombre(client):
    order_id = crear_orden(client)
    disfrazado = b"MZ esto es un programa, no un PDF"
    r = subir(client, order_id, "factura.pdf", disfrazado, "application/pdf")
    assert r.status_code == 415


def test_archivo_mayor_a_2_mb_devuelve_413(client):
    order_id = crear_orden(client)
    grande = PDF + b"0" * (2 * 1024 * 1024)
    assert subir(client, order_id, "grande.pdf", grande).status_code == 413


def test_orden_inexistente_devuelve_404(client):
    assert subir(client, 99, "pago.pdf", PDF).status_code == 404
    assert client.get("/orders/99/comprobantes").status_code == 404


def test_listar_y_descargar(client):
    order_id = crear_orden(client)
    subir(client, order_id, "pago.pdf", PDF)
    subir(client, order_id, "ticket.png", PNG, "image/png")

    lista = client.get(f"/orders/{order_id}/comprobantes").json()
    assert [c["tipo"] for c in lista] == ["application/pdf", "image/png"]

    r = client.get(f"/comprobantes/{lista[1]['id']}/descarga")
    assert r.status_code == 200
    assert r.content == PNG
    assert r.headers["content-type"] == "image/png"
    assert 'filename="ticket.png"' in r.headers["content-disposition"]
