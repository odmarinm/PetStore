"""Casos de uso de User. Los steps hablan con esta capa, nunca con src/requests."""
import time
from http import HTTPStatus
from typing import Any

import allure
import requests

from src.requests.user_requests import UserRequests


class UserInteractor:
    def __init__(self, user_requests: UserRequests | None = None) -> None:
        self._requests = user_requests or UserRequests()

    def create_user(self, payload: dict[str, Any]) -> requests.Response:
        return self._requests.create_user(payload)

    def get_user(self, username: str, attempts: int = 5, delay: float = 1.0) -> requests.Response:
        """Consulta el usuario reintentando ante 404.

        El PetStore público tiene varias instancias detrás de un balanceador; un usuario
        recién creado puede tardar en aparecer. Cada intento queda visible en Allure.
        """
        response = self._requests.get_user(username)
        for attempt in range(2, attempts + 1):
            if response.status_code != HTTPStatus.NOT_FOUND:
                break
            with allure.step(f"Reintento {attempt}/{attempts}: usuario aún no disponible"):
                time.sleep(delay)
                response = self._requests.get_user(username)
        return response
