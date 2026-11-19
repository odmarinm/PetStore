"""Reusable response validations. No HTTP here: receives an already obtained response."""
import json
from typing import Any

import requests
from jsonschema import ValidationError, validate

from src.config.settings import ROOT_DIR
from src.utils.json_path import MISSING, get_by_path

SCHEMAS_DIR = ROOT_DIR / "src" / "schemas"


def response_json(response: requests.Response) -> Any:
    try:
        return response.json()
    except ValueError as exc:
        raise AssertionError(f"Response is not JSON: {response.text!r}") from exc


def content_type_error(response: requests.Response, expected: str) -> str | None:
    actual = response.headers.get("Content-Type", "")
    if expected not in actual:
        return f"Expected Content-Type '{expected}', got '{actual}'"
    return None


def schema_error(body: Any, schema_name: str) -> str | None:
    schema_file = SCHEMAS_DIR / f"{schema_name.lower()}_schema.json"
    schema = json.loads(schema_file.read_text(encoding="utf-8"))
    try:
        validate(instance=body, schema=schema)
    except ValidationError as exc:
        location = ".".join(str(p) for p in exc.absolute_path) or "(root)"
        return f"Schema {schema_name}: '{location}' -> {exc.message}"
    return None


def field_error(request: Any, body: Any, path: str) -> str | None:
    """Compare a request field against the same field in the response."""
    expected = get_by_path(request, path)
    actual = get_by_path(body, path)
    if expected is MISSING:
        return f"Field '{path}': not sent in the request"
    if actual is MISSING:
        return f"Field '{path}': not present in the response"
    if actual != expected:
        return f"Field '{path}': sent {expected!r}, got {actual!r}"
    return None
