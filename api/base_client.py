import json
from typing import Any

import allure
import httpx


SENSITIVE_KEYS = {
    "authorization",
    "cookie",
    "cookies",
    "password",
    "token",
    "x-qa-token",
}


def sanitize_api_artifact(data: Any, depth: int = 0) -> Any:
    if depth > 4:
        return {"truncated": True}

    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            lowered = str(key).lower()
            if (
                lowered in SENSITIVE_KEYS
                or "token" in lowered
                or "password" in lowered
                or "authorization" in lowered
                or "cookie" in lowered
            ):
                sanitized[key] = "***"
            elif "email" in lowered:
                sanitized[key] = "***@***"
            elif "phone" in lowered:
                sanitized[key] = "***"
            else:
                sanitized[key] = sanitize_api_artifact(value, depth + 1)
        return sanitized

    if isinstance(data, list):
        truncated = len(data) > 5
        items = [sanitize_api_artifact(item, depth + 1) for item in data[:5]]
        if truncated:
            return {"items": items, "truncated": True, "total_items": len(data)}
        return items

    if isinstance(data, str) and len(data) > 1000:
        return {"value": data[:1000], "truncated": True}

    return data


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
        self.reporting_enabled = True

    def close(self) -> None:
        self.client.close()

    def set_bearer_token(self, token: str) -> None:
        self.client.headers["Authorization"] = f"Bearer {token}"

    def set_tenant(self, tenant_id: str) -> None:
        self.client.headers["x-tenant-id"] = tenant_id

    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        try:
            response = self.client.request(method, url, **kwargs)
        except httpx.RequestError as exc:
            if self.reporting_enabled:
                self.attach_error(method, url, kwargs.get("json"), exc)
            raise
        if self.reporting_enabled:
            self.attach_exchange(method, url, kwargs.get("json"), response)
        return response

    def request_silent(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        previous = self.reporting_enabled
        self.reporting_enabled = False
        try:
            return self.request(method, url, **kwargs)
        finally:
            self.reporting_enabled = previous

    def get_silent(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request_silent("GET", url, **kwargs)

    def post_silent(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request_silent("POST", url, **kwargs)

    def get(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("POST", url, **kwargs)

    def attach_exchange(self, method: str, url: str, payload: Any, response: httpx.Response) -> None:
        request_data = {
            "method": method,
            "body": sanitize_api_artifact(payload),
        }
        response_data = {
            "status_code": response.status_code,
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

    def attach_error(self, method: str, url: str, payload: Any, error: Exception) -> None:
        error_data = {
            "request": {
                "method": method,
                "body": sanitize_api_artifact(payload),
            },
            "error": {
                "type": error.__class__.__name__,
                "message": str(error)[:1000],
            },
        }
        allure.attach(
            json.dumps(error_data, indent=2, ensure_ascii=False),
            name="error.json",
            attachment_type=allure.attachment_type.JSON,
        )

    def _safe_json(self, response: httpx.Response) -> Any:
        try:
            return sanitize_api_artifact(response.json())
        except ValueError:
            return sanitize_api_artifact(response.text[:1000])

    def _safe_headers(self, headers: dict[str, str]) -> dict[str, str]:
        return sanitize_api_artifact(
            {key: value for key, value in headers.items() if key.lower() not in self.HIDDEN_HEADERS}
        )
