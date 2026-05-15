from typing import Any

import httpx


class BaseApiClient:
    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers=headers or {},
        )

    def close(self) -> None:
        self.client.close()

    def set_bearer_token(self, token: str) -> None:
        self.client.headers["Authorization"] = f"Bearer {token}"

    def get(self, url: str, **kwargs: Any) -> httpx.Response:
        response = self.client.get(url, **kwargs)
        response.raise_for_status()
        return response

    def post(self, url: str, **kwargs: Any) -> httpx.Response:
        response = self.client.post(url, **kwargs)
        response.raise_for_status()
        return response

    def put(self, url: str, **kwargs: Any) -> httpx.Response:
        response = self.client.put(url, **kwargs)
        response.raise_for_status()
        return response

    def delete(self, url: str, **kwargs: Any) -> httpx.Response:
        response = self.client.delete(url, **kwargs)
        response.raise_for_status()
        return response

