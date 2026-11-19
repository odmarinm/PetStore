"""Loads the configuration from the .env file at the project root."""
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    base_url: str
    api_key: str | None
    timeout: float


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Falta la variable '{name}' en el archivo .env")
    return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        base_url=_required("BASE_URL").rstrip("/"),
        api_key=os.getenv("API_KEY") or None,
        timeout=float(os.getenv("REQUEST_TIMEOUT", "30")),
    )
