from enum import StrEnum


class ApiResponseType(StrEnum):
    """Values of the "type" field in the PetStore ApiResponse (observed on the real API)."""

    UNKNOWN = "unknown"  # successful operation (e.g. POST /user)
    ERROR = "error"  # e.g. GET /user/{username} for a non-existent user
