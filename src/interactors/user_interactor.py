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

    def update_user(self, username: str, payload: dict[str, Any]) -> requests.Response:
        return self._requests.update_user(username, payload)

    def delete_user(self, username: str) -> requests.Response:
        return self._requests.delete_user(username)

    def get_user(self, username: str, attempts: int = 5, delay: float = 1.0) -> requests.Response:
        """Fetch the user, retrying while it is not available yet (404)."""
        return self._get_user_retrying_while(
            username, HTTPStatus.NOT_FOUND, "user not available yet", attempts, delay
        )

    def get_deleted_user(self, username: str, attempts: int = 5, delay: float = 1.0) -> requests.Response:
        """Fetch a deleted user, retrying while it is still found (200)."""
        return self._get_user_retrying_while(
            username, HTTPStatus.OK, "user still exists", attempts, delay
        )

    def _get_user_retrying_while(
        self, username: str, retry_status: HTTPStatus, reason: str, attempts: int, delay: float
    ) -> requests.Response:
        """GET /user/{username}, repeated while the response has `retry_status`.

        The public PetStore runs several instances behind a load balancer; a change
        (create/delete) may take a moment to be visible. Each attempt is visible in Allure.
        """
        response = self._requests.get_user(username)
        for attempt in range(2, attempts + 1):
            if response.status_code != retry_status:
                break
            with allure.step(f"Retry {attempt}/{attempts}: {reason}"):
                time.sleep(delay)
                response = self._requests.get_user(username)
        return response
