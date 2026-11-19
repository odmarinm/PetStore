import random
from typing import Any


def generate_id() -> int:
    """Explicit id: without one, the public PetStore assigns an invalid id (~9223372036854...)."""
    return random.randint(1_000_000_000, 9_999_999_999_999)


def unique_username(prefix: str = "qa_user") -> str:
    """The username is the key for GET /user/{username}: it must be unique on the shared server."""
    return f"{prefix.lower()}_{random.randint(100_000, 999_999)}"


class UserBuilder:
    def __init__(self) -> None:
        self._payload: dict[str, Any] = {}

    def with_id(self, user_id: int | None = None) -> "UserBuilder":
        self._payload["id"] = user_id if user_id is not None else generate_id()
        return self

    def with_username(self, username: str) -> "UserBuilder":
        self._payload["username"] = username
        return self

    def with_names(self, first_name: str, last_name: str) -> "UserBuilder":
        self._payload["firstName"] = first_name
        self._payload["lastName"] = last_name
        return self

    def with_email(self, email: str) -> "UserBuilder":
        self._payload["email"] = email
        return self

    def with_password(self, password: str) -> "UserBuilder":
        self._payload["password"] = password
        return self

    def with_phone(self, phone: str) -> "UserBuilder":
        self._payload["phone"] = phone
        return self

    def with_user_status(self, user_status: int) -> "UserBuilder":
        self._payload["userStatus"] = user_status
        return self

    def build(self) -> dict[str, Any]:
        return dict(self._payload)
