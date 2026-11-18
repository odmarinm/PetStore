from enum import StrEnum


class Endpoint(StrEnum):
    """Rutas relativas a BASE_URL (definida en .env)."""

    USER = "/user"
    USER_BY_USERNAME = "/user/{username}"
