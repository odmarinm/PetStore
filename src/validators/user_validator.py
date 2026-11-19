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

# ApiResponse returned by GET /user/{username} when the user does not exist (observed real behavior).
USER_NOT_FOUND_CODE = 1
USER_NOT_FOUND_MESSAGE = "User not found"


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
                    raise AssertionError(f"{failed} check(s) failed")
        except AssertionError:
            pass  # errors are already in self.errors

    def equals(self, label: str, expected: Any, actual: Any, masked: bool = False) -> None:
        """assert_equals inside an Allure sub-step; on failure, record the error and continue."""
        icon = "✔ " if actual == expected else "✘ "
        title = f"{icon}{label}: expected {show(expected, masked)} | got {show(actual, masked)}"
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
    _validate_user_saved("User creation", "POST /user", create_response, request, get_response)


def validate_user_updated(
    update_response: requests.Response,
    request: dict[str, Any],
    get_response: requests.Response,
) -> None:
    username = request.get("username")
    _validate_user_saved("User update", f"PUT /user/{username}", update_response, request, get_response)


def _validate_user_saved(
    operation: str,
    endpoint: str,
    response: requests.Response,
    request: dict[str, Any],
    get_response: requests.Response,
) -> None:
    """POST and PUT return the same ApiResponse; the saved user must then match the request."""
    checker = _Checker()
    username = request.get("username")

    # 1. ApiResponse from the POST/PUT: message is the user id
    if "id" in request:
        message = _check_api_response(checker, endpoint, response, "message (sent id)", str(request["id"]))
    else:
        message = _check_api_response(checker, endpoint, response)

    # 2. Saved user, field by field
    with checker.group(f"Validate saved user (GET /user/{username})"):
        if get_response.status_code != HTTPStatus.OK:
            checker.check(
                f"GET /user/{username} returns 200",
                f"GET /user/{username} returned {get_response.status_code}: {get_response.text}",
            )
        else:
            user = response_json(get_response)
            checker.check("Body matches the User schema", schema_error(user, "user"))
            for field in USER_FIELDS:
                if field in request:
                    checker.equals(
                        field,
                        request[field],
                        get_by_path(user, field),
                        masked=field in MASKED_FIELDS,
                    )
            if "id" not in request and str(message).isdigit():
                checker.equals(f"id (= message from {endpoint})", int(message), get_by_path(user, "id"))
            for field, expected in OMITTED_FIELD_DEFAULTS.items():
                if field not in request:
                    checker.equals(f"{field} (not sent)", expected, get_by_path(user, field))

    _raise_if_errors(checker, operation)


def validate_user_deleted(
    delete_response: requests.Response,
    username: str,
    get_response: requests.Response,
) -> None:
    """DELETE returns an ApiResponse whose message is the username; then GET must return 404."""
    checker = _Checker()
    endpoint = f"DELETE /user/{username}"

    # 1. ApiResponse from the DELETE
    _check_api_response(checker, endpoint, delete_response, "message (deleted username)", username)

    # 2. The user no longer exists
    with checker.group(f"Validate user no longer exists (GET /user/{username})"):
        checker.equals("status code", int(HTTPStatus.NOT_FOUND), get_response.status_code)
        _check_api_response_body(
            checker,
            get_response,
            code=USER_NOT_FOUND_CODE,
            response_type=ApiResponseType.ERROR,
            message_label="message",
            expected_message=USER_NOT_FOUND_MESSAGE,
        )

    _raise_if_errors(checker, "User deletion")


def _check_api_response(
    checker: _Checker,
    endpoint: str,
    response: requests.Response,
    message_label: str = "message",
    expected_message: str | None = None,
) -> Any:
    """Successful ApiResponse of POST/PUT/DELETE. Without `expected_message`, message must be a numeric id."""
    with checker.group(f"Validate {endpoint} (ApiResponse)"):
        return _check_api_response_body(
            checker,
            response,
            code=int(HTTPStatus.OK),
            response_type=ApiResponseType.UNKNOWN,
            message_label=message_label,
            expected_message=expected_message,
        )


def _check_api_response_body(
    checker: _Checker,
    response: requests.Response,
    code: int,
    response_type: ApiResponseType,
    message_label: str,
    expected_message: str | None,
) -> Any:
    """Content-Type, schema, code, type and message of an ApiResponse. Returns the message."""
    api_response = response_json(response)
    message = api_response.get("message", MISSING)
    checker.check("Content-Type is application/json", content_type_error(response, ContentType.JSON))
    checker.check("Body matches the ApiResponse schema", schema_error(api_response, "api_response"))
    checker.equals("code", code, api_response.get("code", MISSING))
    checker.equals("type", str(response_type), api_response.get("type", MISSING))
    if expected_message is not None:
        checker.equals(message_label, expected_message, message)
    else:
        checker.check(
            f"message is a numeric id: {show(message)}",
            None if str(message).isdigit() else f"message is not an id: {show(message)}",
        )
    return message


def _raise_if_errors(checker: _Checker, operation: str) -> None:
    assert not checker.errors, f"{operation} has errors:\n  - " + "\n  - ".join(checker.errors)
