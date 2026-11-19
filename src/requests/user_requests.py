from typing import Any
from urllib.parse import quote

import requests

from src.enums import Endpoint
from src.requests.base_client import BaseClient


class UserRequests(BaseClient):
    def create_user(self, payload: dict[str, Any]) -> requests.Response:
        """POST /user - Create user."""
        return self.post(Endpoint.USER, payload)

    def get_user(self, username: str) -> requests.Response:
        """GET /user/{username} - Get user by user name."""
        return self.get(self._user_path(username))

    def update_user(self, username: str, payload: dict[str, Any]) -> requests.Response:
        """PUT /user/{username} - Update user (the API requires the full User object)."""
        return self.put(self._user_path(username), payload)

    def delete_user(self, username: str) -> requests.Response:
        """DELETE /user/{username} - Delete user."""
        return self.delete(self._user_path(username))

    @staticmethod
    def _user_path(username: str) -> str:
        return Endpoint.USER_BY_USERNAME.format(username=quote(username, safe=""))
