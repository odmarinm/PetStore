"""Full validation of user creation.

POST /user does not return the user, only an ApiResponse: {"code":200,"type":"unknown","message":"<id>"}.
So that ApiResponse is validated first and then, field by field, the user obtained with
GET /user/{username}.

Each check is an Allure sub-step showing the expected and actual values; if it fails,
that sub-step turns red and the remaining checks keep running. At the end a single
AssertionError is raised with all the errors.
"""
from collections.abc import Iterator
from contextlib import contextmanager
from http import HTTPStatus
from typing import Any

import allure
import requests

from src.enums import ApiResponseType, ContentType
from src.utils.assertions import assert_equals, show
from src.utils.json_path import MISSING, get_by_path
from src.validators.response_validator import content_type_error, response_json, schema_error

USER_FIELDS = ("id", "username", "firstName", "lastName", "email", "password", "phone", "userStatus")

# Fields whose value is hidden in the report.
MASKED_FIELDS = {"password"}

# What GET /user/{username} returns when a field was NOT sent (observed real behavior).
OMITTED_FIELD_DEFAULTS: dict[str, Any] = {
    "firstName": MISSING,
    "lastName": MISSING,
    "email": MISSING,
    "password": MISSING,
    "phone": MISSING,
    "userStatus": 0,
}


class _Checker:
    """Run each check as an Allure sub-step and collect the errors."""

    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, title: str, error: str | None) -> None:
        try:
            with allure.step(title):
                if error:
                    raise AssertionError(error)
        except AssertionError as exc:
            self.errors.append(str(exc))

    @contextmanager
    def group(self, title: str) -> Iterator[None]:
        """Group checks; the group turns red if any of its checks fails."""
        errors_before = len(self.errors)
        try:
            with allure.step(title):
                yield
                failed = len(self.errors) - errors_before
                if failed:
                    raise AssertionError(f"{failed} comprobación(es) fallida(s)")
        except AssertionError:
            pass  # errors are already in self.errors

    def equals(self, label: str, expected: Any, actual: Any, masked: bool = False) -> None:
        """assert_equals inside an Allure sub-step; on failure, record the error and continue."""
        icon = "✔ " if actual == expected else "✘ "
        title = f"{icon}{label}: esperado {show(expected, masked)} | recibido {show(actual, masked)}"
        try:
            with allure.step(title):
                assert_equals(actual, expected, label, masked)
        except AssertionError as exc:
            self.errors.append(str(exc))


def validate_user_created(
    create_response: requests.Response,
    request: dict[str, Any],
    get_response: requests.Response,
) -> None:
    checker = _Checker()
    username = request.get("username")

    # 1. ApiResponse from POST /user
    api_response = response_json(create_response)
    message = api_response.get("message", MISSING)
    with checker.group("Validar POST /user (ApiResponse)"):
        checker.check("Content-Type es application/json", content_type_error(create_response, ContentType.JSON))
        checker.check("El body cumple el schema ApiResponse", schema_error(api_response, "api_response"))
        checker.equals("code", int(HTTPStatus.OK), api_response.get("code", MISSING))
        checker.equals("type", str(ApiResponseType.UNKNOWN), api_response.get("type", MISSING))
        if "id" in request:
            checker.equals("message (id enviado)", str(request["id"]), message)
        else:
            checker.check(
                f"message es un id numérico: {show(message)}",
                None if str(message).isdigit() else f"message no es un id: {show(message)}",
            )

    # 2. Saved user, field by field
    with checker.group(f"Validar usuario guardado (GET /user/{username})"):
        if get_response.status_code != HTTPStatus.OK:
            checker.check(
                f"GET /user/{username} responde 200",
                f"GET /user/{username} respondió {get_response.status_code}: {get_response.text}",
            )
        else:
            user = response_json(get_response)
            checker.check("El body cumple el schema User", schema_error(user, "user"))
            for field in USER_FIELDS:
                if field in request:
                    checker.equals(
                        field,
                        request[field],
                        get_by_path(user, field),
                        masked=field in MASKED_FIELDS,
                    )
            if "id" not in request and str(message).isdigit():
                checker.equals("id (= message del POST)", int(message), get_by_path(user, "id"))
            for field, expected in OMITTED_FIELD_DEFAULTS.items():
                if field not in request:
                    checker.equals(f"{field} (no enviado)", expected, get_by_path(user, field))

    assert not checker.errors, "La creación del usuario tiene errores:\n  - " + "\n  - ".join(checker.errors)
