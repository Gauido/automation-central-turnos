import json
from typing import Any

import allure
import httpx


class BaseClient:
    HIDDEN_HEADERS = {
        "server",
        "date",
        "connection",
        "transfer-encoding",
        "content-encoding",
        "x-correlation-id",
        "vary",
    }

    def __init__(self, base_url: str, timeout: float = 30.0, verify: bool = True) -> None:
        self.client = httpx.Client(base_url=base_url, timeout=timeout, verify=verify)

    def close(self) -> None:
        self.client.close()

    def set_bearer_token(self, token: str) -> None:
        self.client.headers["Authorization"] = f"Bearer {token}"

    def set_tenant(self, tenant_id: str) -> None:
        self.client.headers["x-tenant-id"] = tenant_id

    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        response = self.client.request(method, url, **kwargs)
        self.attach_exchange(method, url, kwargs.get("json"), response)
        return response

    def get(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("POST", url, **kwargs)

    def attach_exchange(self, method: str, url: str, payload: Any, response: httpx.Response) -> None:
        request_data = {
            "method": method,
            "url": url,
            "headers": self._safe_headers(dict(self.client.headers)),
            "json": self._mask(payload),
        }
        response_data = {
            "status_code": response.status_code,
            "headers": self._safe_headers(dict(response.headers)),
            "body": self._safe_json(response),
        }
        allure.attach(
            json.dumps(request_data, indent=2, ensure_ascii=False),
            name="request.json",
            attachment_type=allure.attachment_type.JSON,
        )
        allure.attach(
            json.dumps(response_data, indent=2, ensure_ascii=False),
            name="response.json",
            attachment_type=allure.attachment_type.JSON,
        )

    def _safe_json(self, response: httpx.Response) -> Any:
        try:
            return self._mask(response.json())
        except ValueError:
            return response.text[:1000]

    def _mask(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: self._mask_sensitive(key, val)
                for key, val in value.items()
            }
        if isinstance(value, list):
            return [self._mask(item) for item in value]
        return value

    def _mask_sensitive(self, key: str, value: Any) -> Any:
        lowered = key.lower()
        if "password" in lowered:
            return "****"
        if "token" in lowered:
            return "***"
        if lowered == "authorization":
            return "Bearer ***"
        return self._mask(value)

    def _safe_headers(self, headers: dict[str, str]) -> dict[str, str]:
        return {
            key: self._mask_sensitive(key, value)
            for key, value in headers.items()
            if key.lower() not in self.HIDDEN_HEADERS
        }
