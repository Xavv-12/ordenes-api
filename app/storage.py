"""Dónde y cómo se guardan los archivos subidos."""

from pathlib import Path

TAMANO_MAXIMO = 2 * 1024 * 1024  # 2 MB

# Los primeros bytes de un archivo ("firma" o "número mágico") dicen qué es en realidad.
# No confiamos en la extensión ni en el Content-Type que manda el cliente: se pueden falsificar.
FIRMAS = {
    b"%PDF-": ("application/pdf", ".pdf"),
    b"\x89PNG\r\n\x1a\n": ("image/png", ".png"),
    b"\xff\xd8\xff": ("image/jpeg", ".jpg"),
}


def detectar_tipo(contenido: bytes) -> tuple[str, str] | None:
    """Devuelve (tipo MIME, extensión) si el archivo es PDF, PNG o JPEG; si no, None."""
    for firma, tipo in FIRMAS.items():
        if contenido.startswith(firma):
            return tipo
    return None


def get_upload_dir() -> Path:
    """Dependencia: carpeta donde se guardan los archivos. Las pruebas la cambian."""
    carpeta = Path("uploads")
    carpeta.mkdir(exist_ok=True)
    return carpeta
