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
        return self.get(Endpoint.USER_BY_USERNAME.format(username=quote(username, safe="")))
