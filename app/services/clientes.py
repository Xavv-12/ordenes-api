"""Cliente HTTP para un servicio externo de clientes (JSONPlaceholder)."""

import httpx

URL_BASE = "https://jsonplaceholder.typicode.com"


class ServicioNoDisponible(Exception):
    """El servicio externo no respondió o respondió con error."""


class ClientesService:
    def __init__(self, client: httpx.Client | None = None) -> None:
        # timeout: máximo 3 s por petición; retries: reintenta si falla la conexión
        self._client = client or httpx.Client(
            base_url=URL_BASE,
            timeout=3.0,
            transport=httpx.HTTPTransport(retries=2),
        )

    def listar_nombres(self) -> list[str]:
        try:
            respuesta = self._client.get("/users")
            respuesta.raise_for_status()  # 4xx o 5xx se convierten en excepción
        except httpx.HTTPError as error:
            raise ServicioNoDisponible(str(error)) from error
        return sorted(usuario["name"] for usuario in respuesta.json())


servicio = ClientesService()


def get_clientes_service() -> ClientesService:
    return servicio
