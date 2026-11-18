"""Dónde y cómo se guardan las imágenes de los productos."""

from pathlib import Path

TAMANO_MAXIMO = 1024 * 1024  # 1 MB

# Firma (primeros bytes) de cada formato de imagen aceptado
FIRMAS = {
    b"\x89PNG\r\n\x1a\n": ("image/png", ".png"),
    b"\xff\xd8\xff": ("image/jpeg", ".jpg"),
}


def detectar_tipo(contenido: bytes) -> tuple[str, str] | None:
    """Devuelve (tipo MIME, extensión) si el archivo es PNG o JPEG; si no, None."""
    for firma, tipo in FIRMAS.items():
        if contenido.startswith(firma):
            return tipo
    return None


def get_upload_dir() -> Path:
    """Dependencia: carpeta donde se guardan las imágenes. Las pruebas la cambian."""
    carpeta = Path("uploads")
    carpeta.mkdir(exist_ok=True)
    return carpeta
