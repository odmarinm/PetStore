"""Validaciones de responses reutilizables. No hace HTTP: recibe el response ya obtenido."""
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
        raise AssertionError(f"El response no es JSON: {response.text!r}") from exc


def content_type_error(response: requests.Response, expected: str) -> str | None:
    actual = response.headers.get("Content-Type", "")
    if expected not in actual:
        return f"Content-Type esperado '{expected}', recibido '{actual}'"
    return None


def schema_error(body: Any, schema_name: str) -> str | None:
    schema_file = SCHEMAS_DIR / f"{schema_name.lower()}_schema.json"
    schema = json.loads(schema_file.read_text(encoding="utf-8"))
    try:
        validate(instance=body, schema=schema)
    except ValidationError as exc:
        location = ".".join(str(p) for p in exc.absolute_path) or "(raíz)"
        return f"Schema {schema_name}: '{location}' -> {exc.message}"
    return None


def field_error(request: Any, body: Any, path: str) -> str | None:
    """Compara un campo del request contra el mismo campo del response."""
    expected = get_by_path(request, path)
    actual = get_by_path(body, path)
    if expected is MISSING:
        return f"Campo '{path}': no se envió en el request"
    if actual is MISSING:
        return f"Campo '{path}': no está en el response"
    if actual != expected:
        return f"Campo '{path}': enviado {expected!r}, recibido {actual!r}"
    return None
