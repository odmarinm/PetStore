"""Base HTTP client. Attaches every request/response to the Allure report."""
import json
from typing import Any

import allure
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.config.settings import Settings, get_settings
from src.enums import ContentType

# Retry only when the connection could not be established (e.g. a transient DNS failure).
# The request never reached the server, so retrying is safe even for POST/PUT.
# Read errors and HTTP status codes are NOT retried. Waits between attempts: 0, 2, 4, 8, 16 s.
CONNECTION_RETRY = Retry(total=5, connect=5, read=0, status=0, other=0, backoff_factor=1)


class BaseClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=CONNECTION_RETRY))
        self.session.mount("http://", HTTPAdapter(max_retries=CONNECTION_RETRY))
        self.session.headers.update(
            {"Accept": ContentType.JSON, "Content-Type": ContentType.JSON}
        )
        if self.settings.api_key:
            self.session.headers["api_key"] = self.settings.api_key

    def get(self, endpoint: str) -> requests.Response:
        return self._send("GET", endpoint)

    def post(self, endpoint: str, payload: dict[str, Any]) -> requests.Response:
        return self._send("POST", endpoint, json=payload)

    def put(self, endpoint: str, payload: dict[str, Any]) -> requests.Response:
        return self._send("PUT", endpoint, json=payload)

    def delete(self, endpoint: str) -> requests.Response:
        return self._send("DELETE", endpoint)

    def _send(self, method: str, endpoint: str, **kwargs: Any) -> requests.Response:
        url = f"{self.settings.base_url}{endpoint}"
        with allure.step(f"{method} {url}"):
            body = kwargs.get("json")
            if body is not None:
                allure.attach(
                    json.dumps(body, indent=2, ensure_ascii=False),
                    name="Request body",
                    attachment_type=allure.attachment_type.JSON,
                )
            response = self.session.request(
                method, url, timeout=self.settings.timeout, **kwargs
            )
            allure.attach(
                self._pretty(response),
                name=f"Response {response.status_code}",
                attachment_type=allure.attachment_type.JSON,
            )
        return response

    @staticmethod
    def _pretty(response: requests.Response) -> str:
        try:
            return json.dumps(response.json(), indent=2, ensure_ascii=False)
        except ValueError:
            return response.text
