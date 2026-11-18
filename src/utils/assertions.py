"""Aserciones reutilizables con mensajes legibles en el reporte."""
from typing import Any

from src.utils.json_path import MISSING


def show(value: Any, masked: bool = False) -> str:
    """Representación de un valor para mensajes/reporte (MISSING -> '(ausente)', enmascarado -> '***')."""
    if value is MISSING:
        return "(ausente)"
    return "'***'" if masked else repr(value)


def assert_equals(actual: Any, expected: Any, field: str = "valor", masked: bool = False) -> None:
    """Falla con AssertionError si actual != expected, indicando el campo y ambos valores."""
    assert actual == expected, (
        f"{field}: esperado {show(expected, masked)}, recibido {show(actual, masked)}"
    )
