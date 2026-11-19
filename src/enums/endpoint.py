from enum import StrEnum


class Endpoint(StrEnum):
    """Paths relative to BASE_URL (defined in .env)."""

    USER = "/user"
    USER_BY_USERNAME = "/user/{username}"
