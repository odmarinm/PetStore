"""Reusable assertions with readable messages in the report."""
from typing import Any

from src.utils.json_path import MISSING


def show(value: Any, masked: bool = False) -> str:
    """Display a value in messages/report (MISSING -> '(missing)', masked -> '***')."""
    if value is MISSING:
        return "(missing)"
    return "'***'" if masked else repr(value)


def assert_equals(actual: Any, expected: Any, field: str = "value", masked: bool = False) -> None:
    """Raise AssertionError if actual != expected, showing the field and both values."""
    assert actual == expected, (
        f"{field}: expected {show(expected, masked)}, got {show(actual, masked)}"
    )
