from enum import StrEnum


class ApiResponseType(StrEnum):
    """Valores del campo "type" del ApiResponse de PetStore (observados en la API real)."""

    UNKNOWN = "unknown"  # operación exitosa (p. ej. POST /user)
    ERROR = "error"  # p. ej. GET /user/{username} inexistente
