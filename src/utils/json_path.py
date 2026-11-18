"""Acceso a campos anidados con notación de puntos: "category.name", "tags.0.id"."""
from typing import Any

MISSING = object()


def get_by_path(data: Any, path: str) -> Any:
    current = data
    for part in path.split("."):
        if isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        elif isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return MISSING
    return current
