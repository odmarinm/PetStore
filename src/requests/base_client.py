"""Cliente HTTP base. Adjunta cada request/response al reporte de Allure."""
import json
from typing import Any

import allure
import requests

from src.config.settings import Settings, get_settings
from src.enums import ContentType


class BaseClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.session = requests.Session()
        self.session.headers.update(
            {"Accept": ContentType.JSON, "Content-Type": ContentType.JSON}
        )
        if self.settings.api_key:
            self.session.headers["api_key"] = self.settings.api_key

    def get(self, endpoint: str) -> requests.Response:
        return self._send("GET", endpoint)

    def post(self, endpoint: str, payload: dict[str, Any]) -> requests.Response:
        return self._send("POST", endpoint, json=payload)

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
