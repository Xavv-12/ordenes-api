"""Especificación de la tarea: paginación, imágenes, favoritos y migraciones.

NO modifiques este archivo.
"""

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
JPG = b"\xff\xd8\xff\xe0" + b"\x00" * 64


def producto(n: int, existencias: int = 5) -> dict:
    return {
        "sku": f"PRD-{n:03d}",
        "nombre": f"Producto {n}",
        "precio": 100.0,
        "existencias": existencias,
        "categoria": "perifericos",
    }


def subir(client, producto_id, contenido, nombre="foto.png", tipo="image/png"):
    return client.post(
        f"/productos/{producto_id}/imagen", files={"archivo": (nombre, contenido, tipo)}
    )


# --- Paginación -----------------------------------------------------------


def test_t1_paginacion_de_productos(client):
    for n in range(1, 13):
        client.post("/productos", json=producto(n))
    assert len(client.get("/productos").json()) == 10
    pagina = client.get("/productos", params={"limit": 5, "offset": 10}).json()
    assert [p["sku"] for p in pagina] == ["PRD-011", "PRD-012"]


def test_t2_limit_fuera_de_rango(client):
    assert client.get("/productos", params={"limit": 0}).status_code == 422
    assert client.get("/productos", params={"offset": -1}).status_code == 422


# --- Imágenes -------------------------------------------------------------


def test_t3_subir_y_ver_imagen(client, carpeta):
    client.post("/productos", json=producto(1))
    assert client.get("/productos/1/imagen").status_code == 404  # aún no tiene
    assert subir(client, 1, PNG).status_code == 200
    r = client.get("/productos/1/imagen")
    assert r.status_code == 200
    assert r.content == PNG
    assert len(list(carpeta.iterdir())) == 1


def test_t4_acepta_jpeg(client):
    client.post("/productos", json=producto(1))
    assert subir(client, 1, JPG, "foto.jpg", "image/jpeg").status_code == 200


def test_t5_rechaza_lo_que_no_es_imagen(client):
    client.post("/productos", json=producto(1))
    pdf_disfrazado = b"%PDF-1.4 no soy una imagen"
    assert subir(client, 1, pdf_disfrazado, "foto.png", "image/png").status_code == 415


def test_t6_rechaza_imagen_grande_y_producto_inexistente(client):
    client.post("/productos", json=producto(1))
    grande = PNG + b"\x00" * (1024 * 1024)
    assert subir(client, 1, grande).status_code == 413
    assert subir(client, 99, PNG).status_code == 404


# --- Favoritos en la sesión -----------------------------------------------


def test_t7_agregar_favoritos_sin_duplicar(client):
    client.post("/productos", json=producto(1))
    client.post("/productos", json=producto(2))
    r = client.post("/web/favoritos/1", follow_redirects=False)
    assert r.status_code == 303
    client.post("/web/favoritos/2")
    client.post("/web/favoritos/1")  # repetido: no se duplica
    pagina = client.get("/web/favoritos").text
    assert pagina.count("PRD-001") == 1
    assert "PRD-002" in pagina


def test_t8_quitar_favorito_y_producto_inexistente(client):
    client.post("/productos", json=producto(1))
    client.post("/web/favoritos/1")
    client.post("/web/favoritos/1/quitar")
    assert "Todavía no tienes favoritos" in client.get("/web/favoritos").text
    assert client.post("/web/favoritos/99").status_code == 404


def test_t9_favoritos_reflejan_cambios_del_producto(client):
    client.post("/productos", json=producto(1))
    client.post("/web/favoritos/1")
    client.put("/productos/1", json={**producto(1), "nombre": "Nombre nuevo"})
    assert "Nombre nuevo" in client.get("/web/favoritos").text


# --- Migraciones ----------------------------------------------------------


def test_t10_las_migraciones_crean_la_columna_imagen(tmp_path):
    url = f"sqlite:///{tmp_path / 'prueba.db'}"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "head")
    columnas = {c["name"] for c in inspect(create_engine(url)).get_columns("productos")}
    assert "imagen" in columnas
