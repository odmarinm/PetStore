"""User use cases. Steps talk to this layer, never to src/requests."""
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
        """Fetch the user, retrying on 404.

        The public PetStore runs several instances behind a load balancer; a newly
        created user may take a moment to appear. Each attempt is visible in Allure.
        """
        response = self._requests.get_user(username)
        for attempt in range(2, attempts + 1):
            if response.status_code != HTTPStatus.NOT_FOUND:
                break
            with allure.step(f"Reintento {attempt}/{attempts}: usuario aún no disponible"):
                time.sleep(delay)
                response = self._requests.get_user(username)
        return response
